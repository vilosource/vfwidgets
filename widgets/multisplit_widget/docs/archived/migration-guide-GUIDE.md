# Migration Guide: v0.1.x → v0.2.0

This guide helps you upgrade from MultisplitWidget v0.1.x to v0.2.0.

## Overview of Changes

v0.2.0 focuses on **API cleanup and developer experience improvements**:

- ✅ Better lifecycle management
- ✅ Cleaner widget access
- ✅ Improved focus tracking
- ✅ Simpler imports
- ❌ Breaking changes (see below)

## Breaking Changes

### 1. Focus Signal Changed

**OLD (v0.1.x):**
```python
multisplit.pane_focused.connect(on_pane_focused)

def on_pane_focused(pane_id: str):
    print(f"Focused: {pane_id}")
```

**NEW (v0.2.0):**
```python
multisplit.focus_changed.connect(on_focus_changed)

def on_focus_changed(old_pane_id: str, new_pane_id: str):
    print(f"Focus: {old_pane_id} -> {new_pane_id}")
```

**Why**: The new signal provides complete focus transition information, enabling better UX patterns.

**Migration**:
- Replace `pane_focused` with `focus_changed`
- Update handler signature to accept two parameters
- Use empty string `""` for None values

### 2. Internal Attributes Now Private

**OLD (v0.1.x):**
```python
# These were accidentally public
model = multisplit.model
controller = multisplit.controller
container = multisplit.container
```

**NEW (v0.2.0):**
```python
# Internal attributes are now private
# DON'T: multisplit._model  # Will work but don't use!

# DO: Use public APIs instead
pane_ids = multisplit.get_pane_ids()
widget = multisplit.get_widget(pane_id)
```

**Why**: Enforces API boundaries and prevents fragile code that depends on internal implementation.

**Migration**:
- Remove any code accessing `multisplit.model`, `multisplit.controller`, etc.
- Use public APIs like `get_widget()`, `get_pane_ids()`, etc.
- File an issue if you need functionality not available via public API

### 3. Model Signal Access Removed

**OLD (v0.1.x):**
```python
# Direct access to internal model signals
multisplit.model.signals.focus_changed.connect(handler)
multisplit.model.signals.pane_added.connect(handler)
```

**NEW (v0.2.0):**
```python
# Use public signals only
multisplit.focus_changed.connect(handler)
multisplit.pane_added.connect(handler)
```

**Why**: Internal model signals were never meant to be public API.

**Migration**:
- Replace `multisplit.model.signals.focus_changed` with `multisplit.focus_changed`
- All model signals have public equivalents

### 4. Import Path Cleanup

**OLD (v0.1.x):**
```python
from vfwidgets_multisplit import MultisplitWidget
from vfwidgets_multisplit.core.types import WherePosition, Direction
from vfwidgets_multisplit.view.container import WidgetProvider
```

**NEW (v0.2.0):**
```python
# Much cleaner!
from vfwidgets_multisplit import (
    MultisplitWidget,
    WherePosition,
    Direction,
    WidgetProvider,
)
```

**Why**: Common types exported from main package for convenience.

**Migration**:
- Update imports to use main package
- Old imports still work but are not recommended

## New Features

### 1. Widget Lifecycle Hook

**NEW in v0.2.0:**
```python
from vfwidgets_multisplit import WidgetProvider

class MyProvider(WidgetProvider):
    def provide_widget(self, widget_id, pane_id):
        widget = QTextEdit()
        widget.load_content(widget_id)
        return widget

    def widget_closing(self, widget_id, pane_id, widget):
        """NEW: Called before widget removal"""
        widget.save_content()  # Save state
        print(f"Closing {widget_id}")
```

**Benefits**:
- Automatic cleanup notification
- Save state before destruction
- No manual tracking needed

**Recommendation**: Add `widget_closing()` to all providers for proper resource cleanup.

### 2. Widget Lookup APIs

**NEW in v0.2.0:**
```python
# Get specific widget
widget = multisplit.get_widget(pane_id)
if widget:
    widget.setText("Hello")

# Get all widgets
for pane_id, widget in multisplit.get_all_widgets().items():
    widget.update_theme()

# Find pane by widget
pane_id = multisplit.find_pane_by_widget(text_edit)
```

**Benefits**:
- No manual widget tracking needed
- Query widgets on demand
- Reverse lookup (widget → pane_id)

**Recommendation**: Remove manual widget dictionaries, use lookup APIs instead.

### 3. Complete Focus Information

**NEW in v0.2.0:**
```python
def on_focus_changed(old_pane_id: str, new_pane_id: str):
    # Clear old focus border
    if old_pane_id:
        old_widget = multisplit.get_widget(old_pane_id)
        if old_widget:
            old_widget.setStyleSheet("")

    # Add new focus border
    if new_pane_id:
        new_widget = multisplit.get_widget(new_pane_id)
        if new_widget:
            new_widget.setStyleSheet("border: 2px solid blue")
```

**Benefits**:
- Complete transition information
- Cleaner focus border implementation
- No need to iterate all widgets

## Migration Checklist

- [ ] Update `pane_focused` → `focus_changed` signal
- [ ] Update focus handler signature to accept `(old_id, new_id)`
- [ ] Remove access to `multisplit.model`, `multisplit.controller`, etc.
- [ ] Remove access to `multisplit.model.signals.*`
- [ ] Update imports to use main package
- [ ] Add `widget_closing()` to WidgetProvider implementations
- [ ] Replace manual widget tracking with `get_widget()` API
- [ ] Test thoroughly!

## Step-by-Step Example

### Before (v0.1.x)

```python
from vfwidgets_multisplit import MultisplitWidget
from vfwidgets_multisplit.core.types import WherePosition
from vfwidgets_multisplit.view.container import WidgetProvider

class MyProvider(WidgetProvider):
    def __init__(self):
        self.widgets = {}  # Manual tracking

    def provide_widget(self, widget_id, pane_id):
        widget = QTextEdit()
        self.widgets[pane_id] = widget  # Manual tracking
        return widget

class MyApp(QMainWindow):
    def __init__(self):
        self.multisplit = MultisplitWidget(provider=MyProvider())

        # Old signal
        self.multisplit.pane_focused.connect(self.on_focus)

        # Accessing internal model
        self.multisplit.model.signals.pane_added.connect(self.on_added)

    def on_focus(self, pane_id):
        # Only new pane ID
        print(f"Focused: {pane_id}")

        # Manual cleanup of deleted panes
        current = set(self.multisplit.get_pane_ids())
        deleted = set(self.provider.widgets.keys()) - current
        for pid in deleted:
            del self.provider.widgets[pid]
```

### After (v0.2.0)

```python
from vfwidgets_multisplit import (
    MultisplitWidget,
    WherePosition,
    WidgetProvider,
)

class MyProvider(WidgetProvider):
    def provide_widget(self, widget_id, pane_id):
        widget = QTextEdit()
        return widget

    def widget_closing(self, widget_id, pane_id, widget):
        """NEW: Automatic cleanup notification"""
        print(f"Widget {widget_id} closing")
        # Save state, cleanup resources, etc.

class MyApp(QMainWindow):
    def __init__(self):
        self.multisplit = MultisplitWidget(provider=MyProvider())

        # New signal
        self.multisplit.focus_changed.connect(self.on_focus_changed)

        # Public signal
        self.multisplit.pane_added.connect(self.on_added)

    def on_focus_changed(self, old_pane_id, new_pane_id):
        # Complete transition info
        print(f"Focus: {old_pane_id} -> {new_pane_id}")

        # No manual cleanup needed - handled by widget_closing()
```

## Common Issues

### Issue: "AttributeError: 'MultisplitWidget' object has no attribute 'pane_focused'"

**Cause**: Using old `pane_focused` signal

**Fix**: Replace with `focus_changed`
```python
# OLD
multisplit.pane_focused.connect(handler)

# NEW
multisplit.focus_changed.connect(handler)
```

### Issue: "TypeError: handler() missing 1 required positional argument"

**Cause**: Focus handler has old signature

**Fix**: Update to accept two parameters
```python
# OLD
def handler(pane_id):
    ...

# NEW
def handler(old_pane_id, new_pane_id):
    ...
```

### Issue: "AttributeError: 'MultisplitWidget' object has no attribute 'model'"

**Cause**: Accessing internal attributes

**Fix**: Use public APIs
```python
# OLD
panes = multisplit.model.get_all_pane_ids()

# NEW
panes = multisplit.get_pane_ids()
```

## Getting Help

If you encounter issues during migration:

1. Check this guide thoroughly
2. Review [API Best Practices](api-best-practices-GUIDE.md)
3. Check examples in `examples/` directory
4. Open an issue on GitHub

## Timeline

- **v0.2.0 Release**: [Date]
- **v0.1.x Support**: Ended (use for reference only)
- **v1.0.0 Target**: [Future date] - Will include stability guarantees
