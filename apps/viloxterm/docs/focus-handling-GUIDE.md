# Focus Handling with QWebEngineView Widgets - Lessons Learned

**Date**: 2025-10-03
**Context**: ViloxTerm automatic focus after split pane creation
**Issue**: Terminals required double-click to receive keyboard input after programmatic focus

## The Problem

When implementing automatic focus transfer to newly created split panes in ViloxTerm, we encountered an issue where terminals would receive Qt focus programmatically, but keyboard input would not work until the user clicked on the terminal **twice**.

### Symptoms

1. After splitting a pane with Ctrl+Shift+H/V, Qt focus indicators showed the terminal was focused
2. However, typing on the keyboard had no effect
3. First click: Terminal gained visual focus highlight
4. Second click: Terminal finally received keyboard input

### Expected Behavior

After a split operation, the new terminal pane should immediately accept keyboard input without requiring any mouse clicks.

## Root Cause Analysis

### Qt Focus Architecture

The issue stems from how Qt's focus system interacts with `QWebEngineView` (the widget used by TerminalWidget):

```
TerminalWidget (QWidget)
└── QWebEngineView (embedded web content)
    └── Focus Proxy (internal widget that actually receives keyboard events)
```

**Key Discovery**: When you call `setFocus()` on a `QWidget` that contains a `QWebEngineView`, Qt sets focus on the widget itself, but **does not automatically propagate focus** to the web view's internal focus proxy.

### Signal Chain Investigation

During debugging, we discovered that the pane_added signal chain had a break:

1. **Model emits signal**: `model.signals.pane_added.emit(pane_id)` ✓
2. **MultisplitWidget forwards**: Signal was NOT being forwarded ✗
3. **ViloxTerm receives**: Never received the signal ✗

The signal forwarding lambda function had incorrect scope:

```python
# BROKEN: Lambda doesn't capture self correctly
def _forward_pane_added(pane_id):
    logger.info(f"📤 Forwarding pane_added signal: {pane_id}")
    self.pane_added.emit(str(pane_id))  # self is undefined!

self.model.signals.pane_added.connect(_forward_pane_added)
```

**Fix**: Make it a proper instance method:

```python
def _forward_pane_added(self, pane_id):
    """Forward pane_added signal from model to public signal."""
    from .core.logger import logger
    logger.info(f"📤 Forwarding pane_added signal: {pane_id}")
    self.pane_added.emit(str(pane_id))
```

## The Solution

### Two-Part Fix

#### Part 1: Fix Signal Forwarding Chain

**File**: `widgets/multisplit_widget/src/vfwidgets_multisplit/multisplit.py`

Make the signal forwarder a proper instance method:

```python
def _forward_pane_added(self, pane_id):
    """Forward pane_added signal from model to public signal."""
    self.pane_added.emit(str(pane_id))

def _connect_signals(self):
    # Forward model signals
    self.model.signals.pane_added.connect(self._forward_pane_added)
```

#### Part 2: Override setFocus() in TerminalWidget

**File**: `widgets/terminal_widget/src/vfwidgets_terminal/terminal.py`

```python
def setFocus(self) -> None:
    """Override setFocus to properly focus the web view.

    When Qt focus is set on TerminalWidget programmatically,
    we need to explicitly set focus on the QWebEngineView to
    ensure the terminal can receive keyboard input immediately.
    """
    super().setFocus()
    # Focus the web view's focus proxy (the actual input receiver)
    focus_proxy = self.web_view.focusProxy()
    if focus_proxy:
        focus_proxy.setFocus()
        logger.debug("🎯 setFocus(): Focused web view's focus proxy")
    else:
        # Fallback: focus the web view itself
        self.web_view.setFocus()
        logger.debug("🎯 setFocus(): Focused web view directly")
```

### Why This Works

1. **Signal Chain**: Ensures that when a new pane is created, the application receives notification
2. **Explicit Focus Proxy**: When `setFocus()` is called on TerminalWidget, it explicitly sets focus on the QWebEngineView's focus proxy
3. **Immediate Input**: The web view's focus proxy is what actually receives keyboard events, so focusing it directly makes the terminal immediately responsive

## Debugging Techniques Used

### 1. Signal Flow Logging

Add logging at each step of the signal chain to identify where it breaks:

```python
# At emission point
logger.info(f"⚡ Emitting pane_added signal for: {pane_id}")
self.model.signals.pane_added.emit(pane_id)

# At forwarding point
logger.info(f"📤 Forwarding pane_added signal: {pane_id}")
self.pane_added.emit(str(pane_id))

# At receiving point
logger.info(f"🔔 Pane added signal received: {pane_id}")
```

### 2. Focus Event Tracking

Monitor Qt focus events to understand focus flow:

```python
def eventFilter(self, obj: QObject, event: QEvent) -> bool:
    if event.type() == QEvent.Type.FocusIn:
        logger.info(f"🎯 FOCUS: Terminal received focus")
    elif event.type() == QEvent.Type.FocusOut:
        logger.info(f"❌ FOCUS: Terminal lost focus")
    return super().eventFilter(obj, event)
```

### 3. Focus Proxy Investigation

Check if the focus proxy exists and is correctly set up:

```python
focus_proxy = self.web_view.focusProxy()
if focus_proxy:
    logger.info(f"✅ Focus proxy available: {type(focus_proxy).__name__}")
    focus_proxy.installEventFilter(self)
else:
    logger.warning("❌ Focus proxy not available")
```

## Key Takeaways

### For QWebEngineView-Based Widgets

1. **Always override `setFocus()`**: When creating widgets that contain `QWebEngineView`, always override `setFocus()` to explicitly focus the web view's focus proxy

2. **Focus Proxy Pattern**:
   ```python
   def setFocus(self) -> None:
       super().setFocus()
       focus_proxy = self.web_view.focusProxy()
       if focus_proxy:
           focus_proxy.setFocus()
   ```

3. **Event Filters**: Install event filters on the focus proxy, not just the web view, to catch actual focus events

### For Signal Chains

1. **Local Functions Need Careful Scope**: Lambda functions and local functions in signal connections need proper scope. Use instance methods when possible.

2. **Debug Signal Flow**: Add logging at emit, forward, and receive points to verify signal chains work end-to-end

3. **Test Signal Connections**: After connecting signals, test that they actually fire by checking logs

### General Focus Management

1. **Qt Focus != Input Focus**: For embedded widgets (web views, native windows), Qt widget focus and actual input focus are separate concerns

2. **Programmatic vs Manual Focus**: Focus behavior can differ between:
   - User clicking (works automatically)
   - Programmatic `setFocus()` (may need special handling)

3. **Focus Timing**: Be aware that web content may not be fully initialized when widget is created. Handle focus setup in `loadFinished` signal.

## Related Files

- **ViloxTerm app**: `apps/viloxterm/src/viloxterm/app.py`
  - Auto-focus logic in `_on_pane_added()` (line 226)
  - Split handlers set `_splitting_in_progress` flag (lines 242, 275)

- **TerminalWidget**: `widgets/terminal_widget/src/vfwidgets_terminal/terminal.py`
  - `setFocus()` override (line 653)
  - Focus proxy setup (line 605)

- **MultisplitWidget**: `widgets/multisplit_widget/src/vfwidgets_multisplit/multisplit.py`
  - Signal forwarding in `_forward_pane_added()` (line 130)
  - Signal connection in `_connect_signals()` (line 113)

## Testing Verification

To verify the fix works:

1. Launch ViloxTerm
2. Press Ctrl+Shift+H (horizontal split) or Ctrl+Shift+V (vertical split)
3. Immediately start typing without clicking
4. **Expected**: Text appears in the newly created terminal pane
5. **Logs should show**:
   ```
   ⚡ Emitting pane_added signal for: pane_XXXXX
   📤 Forwarding pane_added signal: pane_XXXXX
   🔔 Pane added signal received: pane_XXXXX, splitting=True
   ✅ Auto-focused new pane: pane_XXXXX
   ```

## Prevention

To prevent similar issues in the future:

1. **Documentation**: Document focus handling requirements for any widget using QWebEngineView
2. **Code Review**: Check for proper `setFocus()` overrides in web-based widgets
3. **Testing**: Include programmatic focus scenarios in widget tests
4. **Patterns**: Establish patterns for signal forwarding that avoid scope issues
