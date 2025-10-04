# MultisplitWidget API Best Practices

This guide provides best practices for using the MultisplitWidget API effectively.

## Core Principles

### 1. Use Only Public API

**✅ DO**: Use documented public methods and signals
```python
from vfwidgets_multisplit import MultisplitWidget, WherePosition

widget = multisplit.get_widget(pane_id)
multisplit.split_pane(pane_id, "new-widget", WherePosition.RIGHT)
multisplit.focus_changed.connect(on_focus_changed)
```

**❌ DON'T**: Access internal attributes (prefixed with `_`)
```python
# BAD - internal implementation details
widget = multisplit._container._widget_pool.get_widget(pane_id)
multisplit._model.signals.focus_changed.connect(handler)
```

### 2. Implement Widget Lifecycle Hooks

**✅ DO**: Implement `widget_closing()` for cleanup
```python
from vfwidgets_multisplit import WidgetProvider

class MyProvider(WidgetProvider):
    def __init__(self):
        self.widgets = {}

    def provide_widget(self, widget_id, pane_id):
        widget = QTextEdit()
        self.widgets[pane_id] = widget
        return widget

    def widget_closing(self, widget_id, pane_id, widget):
        """Called BEFORE widget removal - perfect for cleanup"""
        # Save state
        if hasattr(widget, 'save_content'):
            widget.save_content()

        # Clean up tracking
        if pane_id in self.widgets:
            del self.widgets[pane_id]
```

**❌ DON'T**: Manually track deleted panes
```python
# BAD - manual cleanup is error-prone
def on_focus_changed(old_id, new_id):
    # This is fragile and can miss deletions
    current_panes = set(multisplit.get_pane_ids())
    deleted = set(self.widgets.keys()) - current_panes
    for pane_id in deleted:
        del self.widgets[pane_id]
```

### 3. Use Widget Lookup APIs

**✅ DO**: Use built-in lookup methods
```python
# Get specific widget
widget = multisplit.get_widget(pane_id)
if widget:
    widget.setText("New content")

# Get all widgets
for pane_id, widget in multisplit.get_all_widgets().items():
    widget.update_theme()

# Find pane by widget
pane_id = multisplit.find_pane_by_widget(some_text_edit)
```

**❌ DON'T**: Maintain parallel widget tracking
```python
# BAD - unnecessary complexity
class MyProvider:
    def __init__(self):
        self.pane_to_widget = {}  # Don't do this!

    def provide_widget(self, widget_id, pane_id):
        widget = QTextEdit()
        self.pane_to_widget[pane_id] = widget  # Redundant
        return widget
```

### 4. Use Improved Focus Signal

**✅ DO**: Use `focus_changed` signal with both old and new IDs
```python
def on_focus_changed(old_pane_id: str, new_pane_id: str):
    """Handle focus transitions with complete information"""
    if old_pane_id:
        old_widget = multisplit.get_widget(old_pane_id)
        if old_widget:
            old_widget.setStyleSheet("border: 1px solid gray")

    if new_pane_id:
        new_widget = multisplit.get_widget(new_pane_id)
        if new_widget:
            new_widget.setStyleSheet("border: 2px solid blue")

multisplit.focus_changed.connect(on_focus_changed)
```

### 5. Use Clean Imports

**✅ DO**: Import from main package
```python
from vfwidgets_multisplit import (
    MultisplitWidget,
    WidgetProvider,
    WherePosition,
    Direction,
    SplitterStyle,
)
```

**❌ DON'T**: Use deep imports
```python
# BAD - internal module structure may change
from vfwidgets_multisplit.core.types import WherePosition
from vfwidgets_multisplit.view.container import WidgetProvider
```

## Common Patterns

### Pattern 1: Document Management

```python
class DocumentProvider(WidgetProvider):
    def __init__(self):
        self.documents = {}

    def provide_widget(self, widget_id, pane_id):
        # Create or retrieve document
        if widget_id not in self.documents:
            self.documents[widget_id] = self._create_document(widget_id)

        # Create editor view
        editor = QTextEdit()
        editor.setPlainText(self.documents[widget_id])
        return editor

    def widget_closing(self, widget_id, pane_id, widget):
        # Save document content
        if isinstance(widget, QTextEdit):
            self.documents[widget_id] = widget.toPlainText()
```

### Pattern 2: Focus Border Highlighting

```python
class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.multisplit = MultisplitWidget(provider=MyProvider())
        self.multisplit.focus_changed.connect(self.update_focus_borders)

    def update_focus_borders(self, old_pane_id: str, new_pane_id: str):
        # Update all widgets
        for pane_id, widget in self.multisplit.get_all_widgets().items():
            is_focused = (pane_id == new_pane_id)
            border = "2px solid blue" if is_focused else "1px solid gray"
            widget.setStyleSheet(f"border: {border}")
```

### Pattern 3: Custom Navigation

```python
class App(QMainWindow):
    def setup_navigation(self):
        # Use Direction enum for clarity
        QShortcut(QKeySequence("Alt+H"), self,
                  lambda: self.multisplit.navigate_focus(Direction.LEFT))
        QShortcut(QKeySequence("Alt+L"), self,
                  lambda: self.multisplit.navigate_focus(Direction.RIGHT))
        QShortcut(QKeySequence("Alt+K"), self,
                  lambda: self.multisplit.navigate_focus(Direction.UP))
        QShortcut(QKeySequence("Alt+J"), self,
                  lambda: self.multisplit.navigate_focus(Direction.DOWN))
```

## Anti-Patterns to Avoid

### ❌ Anti-Pattern 1: Accessing Internal State

```python
# BAD - fragile and breaks encapsulation
root = multisplit._model.root
panes = multisplit._model.get_all_pane_ids()
```

**Fix**: Use public API
```python
# GOOD - stable public API
pane_ids = multisplit.get_pane_ids()
```

### ❌ Anti-Pattern 2: Ignoring Lifecycle Hooks

```python
# BAD - resource leaks
class MyProvider(WidgetProvider):
    def provide_widget(self, widget_id, pane_id):
        widget = ExpensiveWidget()
        widget.allocate_resources()  # Never cleaned up!
        return widget
```

**Fix**: Use lifecycle hook
```python
# GOOD - proper cleanup
class MyProvider(WidgetProvider):
    def provide_widget(self, widget_id, pane_id):
        widget = ExpensiveWidget()
        widget.allocate_resources()
        return widget

    def widget_closing(self, widget_id, pane_id, widget):
        widget.cleanup_resources()  # Proper cleanup
```

### ❌ Anti-Pattern 3: Manual Widget Tracking

```python
# BAD - reinventing the wheel
class MyProvider(WidgetProvider):
    def __init__(self):
        self.widget_map = {}  # Unnecessary!
```

**Fix**: Use widget lookup API
```python
# GOOD - use built-in lookup
widget = multisplit.get_widget(pane_id)
all_widgets = multisplit.get_all_widgets()
```

## Performance Tips

1. **Batch Operations**: When making multiple changes, batch them to avoid multiple redraws
2. **Use Signals Wisely**: Connect to signals only when needed, disconnect when done
3. **Lazy Loading**: Create widgets only when needed via `provide_widget()`
4. **Proper Cleanup**: Always implement `widget_closing()` to prevent memory leaks

## Version Compatibility

This guide is for MultisplitWidget **v0.2.0+** which includes:
- Widget lifecycle hooks (`widget_closing()`)
- Widget lookup APIs (`get_widget()`, `get_all_widgets()`, `find_pane_by_widget()`)
- Improved focus signal (`focus_changed` with old and new IDs)
- Clean package exports

For migration from older versions, see [Migration Guide](migration-guide-GUIDE.md).
