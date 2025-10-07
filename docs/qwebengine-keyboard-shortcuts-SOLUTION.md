# QWebEngine Keyboard Shortcuts Solution

## Problem

Qt keyboard shortcuts (QAction shortcuts) do NOT work when QWebEngineView has focus. The WebEngine's Chromium process intercepts keyboard events before Qt's shortcut system can process them.

**Symptom**: Shortcuts registered with `QAction.setShortcut()` work everywhere EXCEPT when a QWebEngineView widget has focus.

## Failed Approaches

### ❌ Event Filters on QWebEngineView
```python
# This DOES NOT work
web_view.installEventFilter(event_filter)
```
- WebEngine runs in a separate process
- Keyboard events are processed in Chromium before Qt sees them
- Event filter receives events too late

### ❌ ShortcutContext.ApplicationShortcut
```python
# This DOES NOT work
action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
```
- Still doesn't reach WebEngine's embedded content
- Chromium process captures keys first

### ❌ JavaScript `return false` from event handlers
```javascript
// This blocks xterm.js but ALSO blocks Qt
term.attachCustomKeyEventHandler((event) => {
    if (shouldBlock) return false;
});
```
- Blocks JavaScript library from processing
- But event is consumed in browser - Qt never sees it

### ❌ JavaScript `event.preventDefault()` alone
```javascript
// This prevents browser default but Qt still doesn't see it
event.preventDefault();
```
- Prevents browser navigation/actions
- But Qt shortcuts still don't trigger

## ✅ Working Solution: QWebChannel Bridge

Use QWebChannel to call Python directly from JavaScript, bypassing Qt's shortcut system entirely.

### Architecture

```
Keyboard Event Flow:
1. User presses Ctrl+Shift+Arrow in terminal
2. DOM keydown event (capture phase)
3. JavaScript intercepts BEFORE xterm.js
4. JavaScript calls: terminalBridge.on_shortcut_pressed(action_id)
5. QWebChannel → Python signal: bridge.shortcut_pressed.emit(action_id)
6. TerminalWidget signal: widget.shortcutPressed.emit(action_id)
7. ViloxTerm handler: _on_terminal_shortcut(action_id)
8. Trigger QAction: self.actions[action_id].trigger()
9. Action callback executes
```

### Implementation

#### 1. JavaScript: Intercept Keys at DOM Level

```javascript
// In terminal.html - BEFORE xterm.js initialization
document.getElementById('terminal').addEventListener('keydown', function(e) {
    // Intercept shortcuts we want Qt to handle
    if (e.ctrlKey && e.shiftKey && (e.key === 'ArrowLeft' || e.key === 'ArrowRight' ||
                                     e.key === 'ArrowUp' || e.key === 'ArrowDown')) {
        e.preventDefault();    // Prevent browser default (back/forward navigation)
        e.stopPropagation();   // Prevent xterm.js from seeing it

        // Call Qt via bridge
        if (terminalBridge) {
            const directionMap = {
                'ArrowLeft': 'LEFT',
                'ArrowRight': 'RIGHT',
                'ArrowUp': 'UP',
                'ArrowDown': 'DOWN'
            };
            terminalBridge.on_shortcut_pressed('pane.navigate_' + directionMap[e.key].toLowerCase());
        }
        return;
    }
}, true);  // Use capture phase to intercept BEFORE child elements
```

**Key points**:
- Use **capture phase** (`true` parameter) to intercept before xterm.js
- Call `preventDefault()` to prevent browser shortcuts (Ctrl+Shift+Left = navigate back)
- Call `stopPropagation()` to prevent xterm.js from processing
- Call bridge method with action ID string

#### 2. Python: Bridge with Signal

```python
# In TerminalBridge class
class TerminalBridge(QObject):
    shortcut_pressed = Signal(str)  # action_id

    @Slot(str)
    def on_shortcut_pressed(self, action_id: str) -> None:
        """Handle shortcut from JavaScript."""
        logger.info(f"Shortcut pressed from JS: {action_id}")
        self.shortcut_pressed.emit(action_id)
```

#### 3. Python: Widget Forwards Signal

```python
# In TerminalWidget class
class TerminalWidget(QWidget):
    shortcutPressed = Signal(str)

    def _connect_bridge_signals(self):
        # Forward bridge signal to widget signal
        self.bridge.shortcut_pressed.connect(
            lambda action_id: self.shortcutPressed.emit(action_id)
        )
```

#### 4. Python: Application Triggers Action

```python
# In ViloxTermApp
def _on_pane_added(self, pane_id: str):
    terminal = multisplit.get_widget(pane_id)
    if isinstance(terminal, TerminalWidget):
        # Connect ALL terminals to shortcut handler
        terminal.shortcutPressed.connect(self._on_terminal_shortcut)

def _on_terminal_shortcut(self, action_id: str):
    """Handle shortcut pressed from terminal JavaScript."""
    if action_id in self.actions:
        self.actions[action_id].trigger()  # Trigger the registered QAction
```

## Why This Works

1. **JavaScript has full control** over keyboard events in WebEngine
2. **QWebChannel** provides bidirectional Python ↔ JavaScript communication
3. **Bridge pattern** allows JavaScript to call Python methods
4. **Qt Signals** maintain clean architecture and decoupling
5. **QAction.trigger()** executes the same callback as if shortcut matched

## When to Use This Pattern

Use QWebChannel bridge for shortcuts when:
- ✅ Embedding QWebEngineView widgets
- ✅ Need shortcuts to work when WebEngine has focus
- ✅ JavaScript library (like xterm.js) would otherwise consume the keys
- ✅ Browser shortcuts (Ctrl+Shift+Arrow = navigate) conflict with app shortcuts

## Example: ViloxTerm Pane Navigation

**Problem**: Ctrl+Shift+Arrow keys for pane navigation didn't work when terminal had focus.

**Solution**:
- JavaScript intercepts arrow keys
- Calls `terminalBridge.on_shortcut_pressed('pane.navigate_left')`
- Python receives signal and triggers `navigate_focus(Direction.LEFT)`
- Panes switch correctly

**Files**:
- `terminal.html`: DOM event listener with bridge call
- `terminal.py`: TerminalBridge with shortcut_pressed signal
- `app.py`: ViloxTerm connects terminal.shortcutPressed → _on_terminal_shortcut()

## Browser Shortcuts to Watch For

Common browser shortcuts that conflict with app shortcuts:

- **Ctrl+Shift+Left/Right**: Navigate backward/forward in history
- **Ctrl+Shift+T**: Reopen closed tab
- **Ctrl+Shift+N**: New incognito window
- **Ctrl+PgUp/PgDn**: Switch tabs (in browser)
- **Alt+Left/Right**: Navigate backward/forward

All of these need `event.preventDefault()` in JavaScript when overriding.

## Performance Considerations

- ✅ **Minimal overhead**: QWebChannel uses efficient binary protocol
- ✅ **Signal-based**: No polling or timers needed
- ✅ **Direct**: JavaScript → Python signal is ~1-2ms latency
- ✅ **Scalable**: Works with multiple WebEngine widgets simultaneously

## Testing Checklist

When implementing this pattern:

1. ✅ JavaScript receives keydown events (add console.log)
2. ✅ Bridge method is called (check Python logs)
3. ✅ Signal is emitted from bridge
4. ✅ Widget receives and forwards signal
5. ✅ Application handler is connected to ALL widget instances
6. ✅ QAction is triggered and callback executes
7. ✅ No duplicate connections (use lambda or careful connect/disconnect)

## Common Pitfalls

### ❌ Forgetting to connect shortcuts for ALL widgets

```python
# WRONG - only connects first terminal
def add_new_tab(self):
    terminal = TerminalWidget()
    terminal.shortcutPressed.connect(handler)  # Only this one terminal

# CORRECT - connect ALL terminals including from splits
def _on_pane_added(self, pane_id):
    terminal = multisplit.get_widget(pane_id)
    terminal.shortcutPressed.connect(handler)  # Every terminal
```

### ❌ Using event.stopPropagation() without capture phase

```javascript
// WRONG - xterm.js already received the event
element.addEventListener('keydown', handler, false);  // Bubble phase

// CORRECT - intercept before xterm.js
element.addEventListener('keydown', handler, true);   // Capture phase
```

### ❌ Blocking in JavaScript without calling bridge

```javascript
// WRONG - key is blocked but Qt never sees it
if (shouldBlock) {
    e.preventDefault();
    return;  // Qt doesn't know about this key!
}

// CORRECT - explicitly call Qt
if (shouldBlock) {
    e.preventDefault();
    terminalBridge.on_shortcut_pressed(action_id);  // Tell Qt!
    return;
}
```

## Related Documentation

- Qt QWebChannel: https://doc.qt.io/qt-6/qwebchannel.html
- QWebEngineView keyboard: https://doc.qt.io/qt-6/qwebengineview.html
- VFWidgets terminal_widget: `widgets/terminal_widget/`
- ViloxTerm implementation: `apps/viloxterm/`

## Credits

Solution developed while implementing pane navigation in ViloxTerm (2025-10-06).
After multiple failed attempts with event filters and shortcut contexts, discovered
that QWebChannel bridge is the only reliable way to handle shortcuts in QWebEngineView.
