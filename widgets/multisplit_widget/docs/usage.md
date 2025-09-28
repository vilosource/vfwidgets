# MultiSplit Widget Usage Guide

Practical guide for integrating MultiSplit - a runtime-splittable pane widget for PySide6/Qt6.

## Quick Start (2 minutes)

```python
from vfwidgets_multisplit import MultisplitWidget
from vfwidgets_multisplit.core.types import WherePosition

# Minimal working example
app = QApplication([])
window = QMainWindow()

# Create and use MultiSplit
multisplit = MultisplitWidget()
window.setCentralWidget(multisplit)

# Split at runtime - the key feature!
multisplit.initialize_empty("content-1")
pane = multisplit.get_focused_pane()
multisplit.split_pane(pane, "content-2", WherePosition.RIGHT)

window.show()
app.exec()
```

## Core Concept

**MultiSplit = Runtime Pane Splitting**: Any pane can be split into two at any time during program execution. Users can create their ideal layout on-the-fly.

### Architecture

- **MultisplitWidget**: Manages the split-pane tree
- **WidgetProvider**: Your code that creates content for panes
- **Panes**: Splittable content areas identified by unique IDs
- **Widget IDs**: Tell provider what type of content to create

## Essential Patterns

### 1. Implement WidgetProvider

```python
from vfwidgets_multisplit.view.container import WidgetProvider

class MyProvider(WidgetProvider):
    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        # widget_id tells you WHAT to create
        # pane_id tells you WHERE it's going
        return QLabel(f"Content: {widget_id}")

multisplit = MultisplitWidget(provider=MyProvider())
```

### 2. Split Operations

```python
# Four split directions
WherePosition.RIGHT   # →  New pane on right
WherePosition.LEFT    # ←  New pane on left
WherePosition.BOTTOM  # ↓  New pane below
WherePosition.TOP     # ↑  New pane above

# Split with ratio (0.0-1.0)
multisplit.split_pane(pane_id, "new-content", WherePosition.RIGHT, 0.3)
# Result: 30% left (original), 70% right (new)
```

### 3. Focus Control

```python
# Navigate focus
multisplit.navigate_focus(Direction.RIGHT)  # Move focus right
focused = multisplit.get_focused_pane()      # Get focused pane ID
multisplit.focus_pane(pane_id)              # Set focus directly

# React to focus
multisplit.pane_focused.connect(lambda pane_id: print(f"Focus: {pane_id}"))
```

## Advanced Usage

### Multi-Type Provider

```python
class SmartProvider(WidgetProvider):
    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        # Use prefixes for type routing
        widget_type, config = widget_id.split(":", 1) if ":" in widget_id else (widget_id, "")

        if widget_type == "editor":
            editor = QPlainTextEdit()
            if config:  # config is filepath
                editor.setPlainText(Path(config).read_text())
            return editor
        elif widget_type == "terminal":
            return self.create_terminal()
        else:
            return QLabel(widget_id)

# Usage: multisplit.split_pane(pane, "editor:/path/to/file.py", ...)
```

### Persistence

```python
# Save/Load layouts
multisplit.save_layout(Path("workspace.json"))     # To file
multisplit.load_layout(Path("workspace.json"))     # From file

layout = multisplit.get_layout_json()              # To string
multisplit.set_layout_json(layout)                 # From string

# Undo/Redo
if multisplit.can_undo(): multisplit.undo()
if multisplit.can_redo(): multisplit.redo()

# Size constraints
multisplit.set_constraints(pane_id, min_width=200, max_width=800)
```

## Examples

Run interactive launcher: `python examples/run_examples.py`

1. **01_basic_text_editor.py** - Core splitting, basic provider
2. **02_tabbed_split_panes.py** - Tabs + splitting, complex widgets
3. **03_keyboard_driven_splitting.py** - Vim navigation, power-user features
4. **04_advanced_dynamic_workspace.py** - Full application, multiple types

## Common Patterns

### IDE Layout
```python
# Editor with sidebar and terminal
multisplit.initialize_empty("editor:main.py")
main = multisplit.get_focused_pane()
multisplit.split_pane(main, "sidebar", WherePosition.LEFT, 0.2)
multisplit.split_pane(main, "terminal", WherePosition.BOTTOM, 0.7)
```

### Dashboard Grid
```python
# 2x2 grid
multisplit.initialize_empty("chart:1")
p = multisplit.get_focused_pane()
multisplit.split_pane(p, "chart:2", WherePosition.RIGHT, 0.5)
multisplit.split_pane(p, "chart:3", WherePosition.BOTTOM, 0.5)
panes = multisplit.get_pane_ids()
multisplit.split_pane(panes[1], "chart:4", WherePosition.BOTTOM, 0.5)
```

## Best Practices

### Widget ID Convention
```python
"type:config"  # Recommended format
"editor:/path/to/file.py"
"terminal:bash"
"chart:sales-2024"
```

### Memory Management
```python
class CleanProvider(WidgetProvider):
    def widget_closing(self, widget_id: str, widget: QWidget):
        # Cleanup on pane removal
        widget.save() if hasattr(widget, 'save') else None
        self.cache.pop(widget_id, None)
```

### Error Handling
```python
# Check operations
if not multisplit.split_pane(pane_id, widget_id, pos):
    handle_error()

# React to errors
multisplit.validation_failed.connect(
    lambda errors: [print(e) for e in errors]
)

```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Widgets not appearing | `provide_widget()` must return QWidget, never None |
| Focus not updating | Set `widget.setFocusPolicy(Qt.StrongFocus)` |
| Session restore fails | Keep widget IDs consistent between save/load |
| Constraints ignored | Apply constraints after pane exists |

## Quick Reference

**Signals:**
- `pane_added(str)` - New pane created
- `pane_removed(str)` - Pane removed
- `pane_focused(str)` - Focus changed
- `layout_changed()` - Structure modified
- `validation_failed(list)` - Operation failed

**Key Methods:**
- `split_pane(pane_id, widget_id, position, ratio)`
- `remove_pane(pane_id)`
- `focus_pane(pane_id)` / `navigate_focus(direction)`
- `save_layout(path)` / `load_layout(path)`
- `undo()` / `redo()`

## See Also

- [API Reference](api.md) - Complete method documentation
- [Examples](../examples/) - Working demonstrations
- Run `python examples/run_examples.py` for interactive guide