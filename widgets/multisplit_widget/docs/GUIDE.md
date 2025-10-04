# MultisplitWidget Developer Guide

Comprehensive guide to building applications with MultisplitWidget, including best practices, common patterns, and advanced techniques.

## Table of Contents

- [Core Principles](#core-principles)
- [WidgetProvider Patterns](#widgetprovider-patterns)
- [Focus Management](#focus-management)
- [Session Persistence](#session-persistence)
- [Common Patterns](#common-patterns)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Core Principles

### Use Only Public API

**✅ DO**: Use documented public methods and signals

```python
from vfwidgets_multisplit import MultisplitWidget, WherePosition

# Public API - stable and supported
widget = multisplit.get_widget(pane_id)
multisplit.split_pane(pane_id, "new-widget", WherePosition.RIGHT)
multisplit.focus_changed.connect(on_focus_changed)
```

**❌ DON'T**: Access internal attributes

```python
# BAD - internal implementation, will break
widget = multisplit._container._widget_pool.get_widget(pane_id)
multisplit._model.signals.focus_changed.connect(handler)
```

### Clean Imports (v0.2.0+)

**✅ DO**: Import from main package

```python
from vfwidgets_multisplit import (
    MultisplitWidget,
    WidgetProvider,
    WherePosition,
    Direction,
)
```

**❌ DON'T**: Use deep imports

```python
# BAD - internal module structure may change
from vfwidgets_multisplit.core.types import WherePosition
from vfwidgets_multisplit.view.container import WidgetProvider
```

---

## WidgetProvider Patterns

### Basic Provider

```python
from vfwidgets_multisplit import WidgetProvider

class SimpleProvider(WidgetProvider):
    def provide_widget(self, widget_id: str, pane_id: str):
        """Create widget based on widget_id"""
        editor = QTextEdit()
        editor.setPlainText(f"Content: {widget_id}")
        return editor

    def widget_closing(self, widget_id: str, pane_id: str, widget: QWidget):
        """Optional: cleanup before removal"""
        print(f"Closing {widget_id}")
```

### Multi-Type Provider

```python
class MultiTypeProvider(WidgetProvider):
    def provide_widget(self, widget_id: str, pane_id: str):
        # Parse widget_id to determine type
        if widget_id.startswith("editor:"):
            return self.create_editor(widget_id[7:])
        elif widget_id.startswith("terminal:"):
            return self.create_terminal(widget_id[9:])
        elif widget_id.startswith("browser:"):
            return self.create_browser(widget_id[8:])
        else:
            return QLabel(f"Unknown: {widget_id}")

    def create_editor(self, config: str):
        editor = QTextEdit()
        # Configure based on config string
        return editor

    def create_terminal(self, config: str):
        terminal = TerminalWidget()
        # Configure terminal
        return terminal

    def create_browser(self, url: str):
        browser = QWebView()
        browser.load(QUrl(url))
        return browser
```

### File-Based Provider

```python
class FileProvider(WidgetProvider):
    def __init__(self):
        self.file_contents = {}  # Cache for unsaved changes

    def provide_widget(self, widget_id: str, pane_id: str):
        if widget_id.startswith("file:"):
            file_path = widget_id[5:]
            editor = QTextEdit()

            # Load file
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                editor.setPlainText(content)
            except Exception as e:
                editor.setPlainText(f"Error loading {file_path}: {e}")

            # Track changes
            editor.textChanged.connect(
                lambda: self.on_content_changed(widget_id, editor)
            )

            return editor
        else:
            return QLabel(f"Unknown: {widget_id}")

    def on_content_changed(self, widget_id: str, editor: QTextEdit):
        """Track unsaved changes"""
        self.file_contents[widget_id] = editor.toPlainText()

    def widget_closing(self, widget_id: str, pane_id: str, widget: QWidget):
        """Save before closing"""
        if widget_id in self.file_contents:
            if self.has_unsaved_changes(widget_id):
                # Prompt to save
                self.save_file(widget_id)

            del self.file_contents[widget_id]
```

### Provider with State Management

```python
class StatefulProvider(WidgetProvider):
    def __init__(self):
        self.widget_states = {}  # widget_id -> state dict

    def provide_widget(self, widget_id: str, pane_id: str):
        editor = QTextEdit()

        # Restore state if exists
        if widget_id in self.widget_states:
            state = self.widget_states[widget_id]
            editor.setPlainText(state.get('content', ''))
            cursor = editor.textCursor()
            cursor.setPosition(state.get('cursor_pos', 0))
            editor.setTextCursor(cursor)
        else:
            editor.setPlainText(f"New: {widget_id}")

        # Track state changes
        editor.textChanged.connect(
            lambda: self.save_state(widget_id, editor)
        )

        return editor

    def save_state(self, widget_id: str, editor: QTextEdit):
        """Save current state"""
        self.widget_states[widget_id] = {
            'content': editor.toPlainText(),
            'cursor_pos': editor.textCursor().position(),
        }

    def widget_closing(self, widget_id: str, pane_id: str, widget: QWidget):
        """State is preserved - widget_id can be recreated later"""
        print(f"Widget {widget_id} closing - state preserved")
```

---

## Focus Management

### Using focus_changed Signal (v0.2.0+)

The `focus_changed` signal provides complete focus transition information:

```python
def setup_focus_handling(self):
    self.multisplit.focus_changed.connect(self.on_focus_changed)

def on_focus_changed(self, old_pane_id: str, new_pane_id: str):
    """
    Args:
        old_pane_id: Pane that lost focus (empty string if none)
        new_pane_id: Pane that gained focus (empty string if none)
    """
    # Clear old focus indicator
    if old_pane_id:
        old_widget = self.multisplit.get_widget(old_pane_id)
        if old_widget:
            old_widget.setStyleSheet("")

    # Add new focus indicator
    if new_pane_id:
        new_widget = self.multisplit.get_widget(new_pane_id)
        if new_widget:
            new_widget.setStyleSheet("border: 2px solid blue")

        # Update UI for focused pane
        self.update_toolbar_for_pane(new_pane_id)
        self.statusbar.showMessage(f"Focused: {new_pane_id[:8]}")
```

### Focus-Aware Operations

```python
def split_current_pane(self, position: WherePosition):
    """Split the currently focused pane"""
    focused = self.multisplit.get_focused_pane()

    if not focused:
        QMessageBox.warning(self, "No Focus", "No pane is focused")
        return

    # Create new widget
    widget_id = self.create_new_widget_id()

    # Split focused pane
    success = self.multisplit.split_pane(focused, widget_id, position, 0.5)

    if not success:
        QMessageBox.warning(self, "Split Failed", "Could not split pane")

def close_current_pane(self):
    """Close the currently focused pane"""
    focused = self.multisplit.get_focused_pane()

    if not focused:
        return

    # Confirm if needed
    widget = self.multisplit.get_widget(focused)
    if self.has_unsaved_changes(widget):
        reply = QMessageBox.question(
            self, "Unsaved Changes",
            "Save before closing?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
        )

        if reply == QMessageBox.Save:
            self.save_widget(widget)
        elif reply == QMessageBox.Cancel:
            return

    self.multisplit.remove_pane(focused)
```

### Keyboard Navigation

```python
def setup_navigation(self):
    """Setup vim-like navigation"""
    QShortcut(QKeySequence("Ctrl+H"), self,
              lambda: self.multisplit.navigate_focus(Direction.LEFT))
    QShortcut(QKeySequence("Ctrl+J"), self,
              lambda: self.multisplit.navigate_focus(Direction.DOWN))
    QShortcut(QKeySequence("Ctrl+K"), self,
              lambda: self.multisplit.navigate_focus(Direction.UP))
    QShortcut(QKeySequence("Ctrl+L"), self,
              lambda: self.multisplit.navigate_focus(Direction.RIGHT))
```

---

## Session Persistence

### Save/Load Pattern

```python
class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.session_file = "workspace.json"
        self.multisplit = MultisplitWidget(provider=MyProvider())

        # Load previous session
        self.load_session()

    def load_session(self):
        """Load saved session on startup"""
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, 'r') as f:
                    json_data = f.read()
                self.multisplit.load_session(json_data)
                print("Session loaded")
            except Exception as e:
                print(f"Error loading session: {e}")
                # Fall back to default
                self.multisplit.initialize_empty("default")
        else:
            # First run - initialize with default
            self.multisplit.initialize_empty("default")

    def save_session(self):
        """Save current session"""
        try:
            json_data = self.multisplit.save_session()
            with open(self.session_file, 'w') as f:
                f.write(json_data)
            print("Session saved")
        except Exception as e:
            print(f"Error saving session: {e}")

    def closeEvent(self, event):
        """Save session on exit"""
        self.save_session()
        event.accept()
```

### Auto-Save Pattern

```python
def setup_autosave(self):
    """Auto-save session every 30 seconds"""
    self.autosave_timer = QTimer()
    self.autosave_timer.timeout.connect(self.save_session)
    self.autosave_timer.start(30000)  # 30 seconds

    # Also save on layout changes
    self.multisplit.layout_changed.connect(self.on_layout_changed)

def on_layout_changed(self):
    """Debounced save on layout change"""
    # Restart timer - only save if no changes for 5 seconds
    self.save_debounce_timer.stop()
    self.save_debounce_timer.start(5000)
```

### Multiple Named Sessions

```python
class SessionManager:
    def __init__(self, multisplit: MultisplitWidget):
        self.multisplit = multisplit
        self.sessions_dir = Path.home() / ".myapp" / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def list_sessions(self) -> list[str]:
        """Get list of saved session names"""
        return [f.stem for f in self.sessions_dir.glob("*.json")]

    def save_session(self, name: str):
        """Save session with a name"""
        json_data = self.multisplit.save_session()
        session_file = self.sessions_dir / f"{name}.json"
        with open(session_file, 'w') as f:
            f.write(json_data)

    def load_session(self, name: str) -> bool:
        """Load named session"""
        session_file = self.sessions_dir / f"{name}.json"
        if session_file.exists():
            with open(session_file, 'r') as f:
                json_data = f.read()
            return self.multisplit.load_session(json_data)
        return False

    def delete_session(self, name: str):
        """Delete a saved session"""
        session_file = self.sessions_dir / f"{name}.json"
        if session_file.exists():
            session_file.unlink()
```

---

## Common Patterns

### Pattern 1: IDE-Style Layout

```python
def create_ide_layout(self):
    """Create typical IDE layout: editor | terminal"""
    # Start with editor
    self.multisplit.initialize_empty("editor:main.py")

    # Split to add terminal on bottom
    panes = self.multisplit.get_pane_ids()
    if panes:
        self.multisplit.split_pane(
            panes[0],
            "terminal:bash",
            WherePosition.BOTTOM,
            0.7  # Editor gets 70%, terminal gets 30%
        )
```

### Pattern 2: Dashboard Layout

```python
def create_dashboard_layout(self):
    """Create dashboard: chart | stats
                           logs  | logs"""
    # Main chart
    self.multisplit.initialize_empty("chart:main")

    # Add stats on right
    panes = self.multisplit.get_pane_ids()
    self.multisplit.split_pane(panes[0], "stats:overview", WherePosition.RIGHT, 0.7)

    # Add logs on bottom (split the chart pane)
    self.multisplit.split_pane(panes[0], "logs:system", WherePosition.BOTTOM, 0.7)
```

### Pattern 3: Dynamic Widget Creation

```python
def open_file(self, file_path: str):
    """Open file in new pane, splitting current"""
    focused = self.multisplit.get_focused_pane()

    if focused:
        widget_id = f"file:{file_path}"
        self.multisplit.split_pane(
            focused,
            widget_id,
            WherePosition.RIGHT,
            0.5
        )
    else:
        # No panes yet - initialize
        self.multisplit.initialize_empty(f"file:{file_path}")
```

### Pattern 4: Widget Lookup for Operations

```python
def save_all_files(self):
    """Save all editor widgets"""
    for pane_id, widget in self.multisplit.get_all_widgets().items():
        if isinstance(widget, QTextEdit):
            self.save_editor_content(widget)

def update_all_themes(self, theme: str):
    """Apply theme to all widgets"""
    for pane_id, widget in self.multisplit.get_all_widgets().items():
        if hasattr(widget, 'set_theme'):
            widget.set_theme(theme)

def find_editor_by_file(self, file_path: str) -> Optional[QTextEdit]:
    """Find editor widget displaying a file"""
    for pane_id, widget in self.multisplit.get_all_widgets().items():
        if isinstance(widget, QTextEdit):
            if hasattr(widget, 'file_path') and widget.file_path == file_path:
                return widget
    return None
```

---

## Best Practices

### 1. Implement widget_closing() Hook

**✅ DO**:
```python
class MyProvider(WidgetProvider):
    def widget_closing(self, widget_id: str, pane_id: str, widget: QWidget):
        # Save state
        if hasattr(widget, 'save_content'):
            widget.save_content()

        # Cleanup resources
        widget.cleanup()
```

**❌ DON'T**:
```python
# BAD - manual tracking is error-prone
def on_pane_removed(self, pane_id: str):
    # This misses edge cases and is fragile
    if pane_id in self.widgets:
        del self.widgets[pane_id]
```

### 2. Use Widget Lookup APIs

**✅ DO**:
```python
# Get widget directly
widget = multisplit.get_widget(pane_id)

# Iterate all widgets
for pane_id, widget in multisplit.get_all_widgets().items():
    widget.update()
```

**❌ DON'T**:
```python
# BAD - unnecessary parallel tracking
self.pane_to_widget = {}  # Don't maintain this yourself
```

### 3. Check Return Values

**✅ DO**:
```python
if not multisplit.split_pane(pane_id, "widget", WherePosition.RIGHT):
    QMessageBox.warning(self, "Error", "Split failed")

if not multisplit.remove_pane(pane_id):
    print("Remove failed - may be last pane")
```

### 4. Handle Empty String in Signals

```python
def on_focus_changed(self, old_pane_id: str, new_pane_id: str):
    # Empty string means no pane (not None)
    if old_pane_id:  # Will be False for empty string
        print(f"Lost focus: {old_pane_id}")

    if new_pane_id:  # Will be False for empty string
        print(f"Gained focus: {new_pane_id}")
```

### 5. Validate Ratios

```python
def split_with_ratio(self, pane_id: str, ratio: float):
    # Clamp ratio to valid range
    ratio = max(0.1, min(0.9, ratio))

    self.multisplit.split_pane(
        pane_id,
        "widget-id",
        WherePosition.RIGHT,
        ratio
    )
```

---

## Troubleshooting

### Problem: Focus not updating

**Cause**: Widgets not participating in Qt focus chain

**Solution**:
```python
# Ensure widgets can receive focus
widget.setFocusPolicy(Qt.StrongFocus)

# Install event filter if needed
widget.installEventFilter(self.multisplit)
```

### Problem: widget_closing() not called

**Cause**: Using old signature (missing `pane_id` parameter)

**Solution**:
```python
# WRONG (v0.1.x):
def widget_closing(self, widget_id: str, widget: QWidget):
    pass

# CORRECT (v0.2.0+):
def widget_closing(self, widget_id: str, pane_id: str, widget: QWidget):
    pass
```

### Problem: Session restore failing

**Cause**: WidgetProvider can't recreate widgets from saved IDs

**Solution**:
```python
def provide_widget(self, widget_id: str, pane_id: str):
    # Ensure you can recreate ANY widget_id used in your app
    if widget_id.startswith("editor:"):
        return self.create_editor(widget_id[7:])
    elif widget_id.startswith("terminal:"):
        return self.create_terminal(widget_id[9:])
    else:
        # Fallback for unknown IDs
        return QLabel(f"Could not restore: {widget_id}")
```

### Problem: Can't remove last pane

**Cause**: `remove_pane()` prevents removing the last pane

**Solution**:
```python
# Check pane count before removing
panes = multisplit.get_pane_ids()
if len(panes) > 1:
    multisplit.remove_pane(pane_id)
else:
    # Replace content instead of removing
    # (implementation depends on your needs)
    pass
```

---

## Performance Tips

1. **Lazy widget creation** - Create complex widgets only when needed:
   ```python
   def provide_widget(self, widget_id: str, pane_id: str):
       # Don't load heavy content until widget is visible
       widget = MyWidget()
       QTimer.singleShot(0, lambda: widget.load_content(widget_id))
       return widget
   ```

2. **Debounce frequent operations**:
   ```python
   # Debounce auto-save
   self.save_timer = QTimer()
   self.save_timer.setSingleShot(True)
   self.save_timer.timeout.connect(self.save_session)

   def on_layout_changed(self):
       self.save_timer.start(5000)  # Save 5s after last change
   ```

3. **Cleanup in widget_closing()**:
   ```python
   def widget_closing(self, widget_id: str, pane_id: str, widget: QWidget):
       # Release heavy resources
       if hasattr(widget, 'cleanup'):
           widget.cleanup()
   ```

---

## Next Steps

- **API Reference**: See [API.md](API.md) for complete API documentation
- **Examples**: Check `examples/` for complete working applications
- **Migration**: Upgrading from v0.1.x? See [MIGRATION.md](MIGRATION.md)

For questions or issues, please open an issue on GitHub.
