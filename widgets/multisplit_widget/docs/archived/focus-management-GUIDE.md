# MultisplitWidget Focus Management Guide

**Widget**: vfwidgets-multisplit
**Purpose**: Comprehensive guide to focus management in MultisplitWidget applications
**Audience**: Developers integrating MultisplitWidget into applications

## Overview

MultisplitWidget provides a rich signal system for managing focus across dynamically created panes. This guide covers:

- Using signals for automatic focus management
- Implementing smart focus policies
- Special handling for web-based widgets (QWebEngineView)
- Production patterns from ViloxTerm reference implementation

## Quick Start: Automatic Focus After Split

The most common use case is automatically focusing newly created panes after a split operation:

```python
from PySide6.QtWidgets import QApplication
from vfwidgets_multisplit import MultisplitWidget
from vfwidgets_multisplit.core.types import WherePosition

# Create widget with provider
multisplit = MultisplitWidget(provider=my_provider)

# Connect to pane_added signal
multisplit.pane_added.connect(lambda pane_id: multisplit.focus_pane(pane_id))

# Now when you split, focus moves automatically
focused = multisplit.get_focused_pane()
multisplit.split_pane(focused, "new-widget", WherePosition.RIGHT)
# Focus is now on the newly created pane!
```

## Focus Signals

MultisplitWidget emits three key focus-related signals:

### pane_added

**Signal**: `pane_added(str)`
**When**: Emitted immediately after a new pane is created and added to the layout
**Use**: Auto-focus new panes, update UI, track pane lifecycle

```python
def on_pane_added(pane_id: str):
    print(f"New pane created: {pane_id}")
    multisplit.focus_pane(pane_id)

multisplit.pane_added.connect(on_pane_added)
```

### pane_focused

**Signal**: `pane_focused(str)`
**When**: Emitted when a pane gains focus (user click or programmatic)
**Use**: Update UI indicators, sync state, track focus changes

```python
def on_pane_focused(pane_id: str):
    print(f"Pane focused: {pane_id}")
    # Update title bar, status bar, etc.

multisplit.pane_focused.connect(on_pane_focused)
```

### pane_removed

**Signal**: `pane_removed(str)`
**When**: Emitted after a pane is removed from the layout
**Use**: Cleanup, focus management for remaining panes

```python
def on_pane_removed(pane_id: str):
    print(f"Pane removed: {pane_id}")
    # MultisplitWidget automatically moves focus to sibling pane

multisplit.pane_removed.connect(on_pane_removed)
```

## Programmatic Focus Control

### focus_pane()

Set focus on a specific pane programmatically:

```python
# Get all pane IDs
pane_ids = multisplit.get_pane_ids()

# Focus a specific pane
success = multisplit.focus_pane(pane_ids[0])
if success:
    print(f"Focused pane: {pane_ids[0]}")
else:
    print("Focus failed - pane doesn't exist")
```

### get_focused_pane()

Get the currently focused pane ID:

```python
focused = multisplit.get_focused_pane()
if focused:
    print(f"Current focus: {focused}")
else:
    print("No pane has focus")
```

## Smart Focus Policies

### Conditional Auto-Focus

Only auto-focus under specific conditions:

```python
class SmartFocusHandler:
    def __init__(self, multisplit: MultisplitWidget):
        self.multisplit = multisplit
        self.splitting_in_progress = False

        # Connect signals
        multisplit.pane_added.connect(self.on_pane_added)

    def on_split_requested(self):
        """Called before splitting"""
        self.splitting_in_progress = True

    def on_pane_added(self, pane_id: str):
        """Only auto-focus panes created from splits"""
        if self.splitting_in_progress:
            self.multisplit.focus_pane(pane_id)
            self.splitting_in_progress = False

# Usage
handler = SmartFocusHandler(multisplit)

# When user initiates split
handler.on_split_requested()
multisplit.split_pane(focused_pane, "new-widget", WherePosition.RIGHT)
# Focus moves to new pane automatically
```

**Real-world example**: See ViloxTerm's `_splitting_in_progress` flag pattern:
- [`apps/viloxterm/src/viloxterm/app.py:52`](../../../apps/viloxterm/src/viloxterm/app.py#L52)

### User Preference Control

Respect user preferences for focus behavior:

```python
class ConfigurableFocusManager:
    def __init__(self, multisplit: MultisplitWidget, config: dict):
        self.multisplit = multisplit
        self.auto_focus_on_split = config.get("auto_focus_on_split", True)
        self.auto_focus_on_remove = config.get("auto_focus_on_remove", True)

        multisplit.pane_added.connect(self.on_pane_added)
        multisplit.pane_removed.connect(self.on_pane_removed)

    def on_pane_added(self, pane_id: str):
        if self.auto_focus_on_split:
            self.multisplit.focus_pane(pane_id)

    def on_pane_removed(self, pane_id: str):
        if self.auto_focus_on_remove:
            # MultisplitWidget handles focus automatically,
            # but you could implement custom logic here
            pass
```

## Special Case: QWebEngineView Widgets

### The Problem

If your widgets use `QWebEngineView` (terminals, browsers, HTML previews), standard Qt focus handling is **not sufficient**:

```python
# This sets Qt focus on the widget
multisplit.focus_pane(pane_id)

# But QWebEngineView needs explicit focus on its internal focus proxy
# Without this, keyboard input won't work!
```

### The Solution

Override `setFocus()` in your widget to propagate focus to the web view:

```python
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget

class MyWebWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.web_view = QWebEngineView()
        # ... setup layout

    def setFocus(self) -> None:
        """Override to focus web view's focus proxy."""
        super().setFocus()

        # Focus the web view's focus proxy (actual input receiver)
        focus_proxy = self.web_view.focusProxy()
        if focus_proxy:
            focus_proxy.setFocus()
        else:
            # Fallback: focus web view directly
            self.web_view.setFocus()
```

### Why This Is Necessary

`QWebEngineView` uses a **focus proxy** architecture:

```
MyWebWidget
└── QWebEngineView
    └── Focus Proxy (hidden internal widget)
        └── This is what actually receives keyboard input!
```

When you call `multisplit.focus_pane()`:
1. Qt sets focus on `MyWebWidget` ✓
2. But the focus proxy remains unfocused ✗
3. Result: Widget looks focused but doesn't receive keyboard input

By overriding `setFocus()`, you ensure the focus proxy is explicitly focused.

### Complete Example

See **TerminalWidget** as a reference implementation:
- **setFocus() override**: [`widgets/terminal_widget/src/vfwidgets_terminal/terminal.py:653`](../../terminal_widget/src/vfwidgets_terminal/terminal.py#L653)
- **ViloxTerm integration**: [`apps/viloxterm/docs/focus-handling-GUIDE.md`](../../../apps/viloxterm/docs/focus-handling-GUIDE.md)

## Production Patterns

### Pattern 1: Track Focus History

```python
from collections import deque

class FocusHistoryManager:
    def __init__(self, multisplit: MultisplitWidget, max_history: int = 10):
        self.multisplit = multisplit
        self.focus_history = deque(maxlen=max_history)

        multisplit.pane_focused.connect(self.on_pane_focused)

    def on_pane_focused(self, pane_id: str):
        self.focus_history.append(pane_id)

    def focus_previous(self) -> bool:
        """Focus the previously focused pane"""
        if len(self.focus_history) > 1:
            self.focus_history.pop()  # Remove current
            previous = self.focus_history[-1]
            return self.multisplit.focus_pane(previous)
        return False
```

### Pattern 2: Focus Guards

Prevent focus changes during critical operations:

```python
class FocusGuard:
    def __init__(self, multisplit: MultisplitWidget):
        self.multisplit = multisplit
        self.locked = False
        self._pending_focus = None

        multisplit.pane_added.connect(self.on_pane_added)

    def __enter__(self):
        self.locked = True
        return self

    def __exit__(self, *args):
        self.locked = False
        if self._pending_focus:
            self.multisplit.focus_pane(self._pending_focus)
            self._pending_focus = None

    def on_pane_added(self, pane_id: str):
        if self.locked:
            self._pending_focus = pane_id
        else:
            self.multisplit.focus_pane(pane_id)

# Usage
with FocusGuard(multisplit):
    # Multiple operations - focus changes queued
    multisplit.split_pane(pane1, "w1", WherePosition.RIGHT)
    multisplit.split_pane(pane2, "w2", WherePosition.BOTTOM)
# Focus change happens here
```

### Pattern 3: Focus Indicators

Update UI to show focused pane:

```python
class FocusIndicator:
    def __init__(self, multisplit: MultisplitWidget, status_bar):
        self.multisplit = multisplit
        self.status_bar = status_bar

        multisplit.pane_focused.connect(self.update_indicator)

    def update_indicator(self, pane_id: str):
        total_panes = len(self.multisplit.get_pane_ids())
        self.status_bar.showMessage(
            f"Focus: {pane_id} ({total_panes} panes)"
        )
```

## Timing Considerations

### Signal Emission Order

When a pane is created:

1. Pane is added to model
2. Widget is created by provider
3. Layout is updated
4. **`pane_added` signal is emitted**
5. Your handler can now safely call `focus_pane()`

### Widget Initialization

**Important**: The widget may not be fully initialized when `pane_added` fires:

```python
def on_pane_added(self, pane_id: str):
    # Qt focus can be set immediately
    self.multisplit.focus_pane(pane_id)

    # But widget content might still be loading
    # For web views, wait for loadFinished signal:
    widget = self.get_widget_for_pane(pane_id)
    if isinstance(widget, QWebEngineView):
        widget.loadFinished.connect(
            lambda: self.on_web_view_ready(pane_id)
        )
```

## Debugging Focus Issues

### Enable Focus Logging

```python
import logging

logger = logging.getLogger("focus_debug")
logger.setLevel(logging.DEBUG)

def log_pane_added(pane_id: str):
    logger.debug(f"Pane added: {pane_id}")

def log_pane_focused(pane_id: str):
    logger.debug(f"Pane focused: {pane_id}")

multisplit.pane_added.connect(log_pane_added)
multisplit.pane_focused.connect(log_pane_focused)
```

### Check Signal Connections

```python
# Verify signal is connected
if multisplit.pane_added.receivers() > 0:
    print("pane_added has receivers")
else:
    print("WARNING: pane_added has NO receivers")
```

### Verify Focus Flow

```python
def debug_focus_chain(multisplit: MultisplitWidget):
    """Debug focus management"""

    def on_pane_added(pane_id: str):
        print(f"1. Pane added: {pane_id}")
        multisplit.focus_pane(pane_id)
        print(f"2. Called focus_pane({pane_id})")

    def on_pane_focused(pane_id: str):
        print(f"3. Pane focused: {pane_id}")
        current = multisplit.get_focused_pane()
        print(f"4. Current focus: {current}")

    multisplit.pane_added.connect(on_pane_added)
    multisplit.pane_focused.connect(on_pane_focused)
```

## Best Practices

### ✅ Do

1. **Connect to `pane_added`** for automatic focus after splits
2. **Use conditional logic** to control when auto-focus happens
3. **Override `setFocus()`** for QWebEngineView-based widgets
4. **Handle focus timing** for asynchronously initialized widgets
5. **Respect user preferences** for focus behavior

### ❌ Don't

1. **Don't call `focus_pane()` in tight loops** - it can cause performance issues
2. **Don't assume widget is fully initialized** when `pane_added` fires
3. **Don't forget to disconnect signals** when cleaning up
4. **Don't ignore return value** of `focus_pane()` - it returns False if pane doesn't exist
5. **Don't fight Qt's focus system** - work with it by overriding `setFocus()`

## Reference Implementations

### ViloxTerm Terminal Emulator

Complete production example with QWebEngineView focus handling:

- **Application-level handler**: [`apps/viloxterm/src/viloxterm/app.py:226`](../../../apps/viloxterm/src/viloxterm/app.py#L226)
- **TerminalWidget setFocus()**: [`widgets/terminal_widget/src/vfwidgets_terminal/terminal.py:653`](../../terminal_widget/src/vfwidgets_terminal/terminal.py#L653)
- **Comprehensive lessons learned**: [`apps/viloxterm/docs/focus-handling-GUIDE.md`](../../../apps/viloxterm/docs/focus-handling-GUIDE.md)

### Key Patterns Used

1. **Conditional auto-focus**: Only focus panes created from user-initiated splits
2. **Signal-based architecture**: Connect to `pane_added` in tab creation
3. **QWebEngineView handling**: Override `setFocus()` to focus web view's focus proxy
4. **Clean logging**: DEBUG-level logs for troubleshooting, not production noise

## Further Reading

- **MultisplitWidget API**: [../README.md](../README.md)
- **Integration Guide**: [06-guides/integration-guide.md](06-guides/integration-guide.md)
- **ViloxTerm Focus Guide**: [../../../apps/viloxterm/docs/focus-handling-GUIDE.md](../../../apps/viloxterm/docs/focus-handling-GUIDE.md)
- **TerminalWidget Docs**: [../../terminal_widget/README.md](../../terminal_widget/README.md)

---

**Last Updated**: 2025-10-03
**Version**: 1.0
