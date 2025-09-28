# MultiSplit Widget API Reference

Complete API documentation for the MultiSplit widget - a runtime-splittable pane system for PySide6/Qt6.

## Quick Reference Table

| Method | Returns | Description |
|--------|---------|-------------|
| `split_pane(pane_id, widget_id, position, ratio=0.5)` | `bool` | Split a pane |
| `remove_pane(pane_id)` | `bool` | Remove a pane |
| `focus_pane(pane_id)` | `bool` | Set focus |
| `navigate_focus(direction)` | `bool` | Move focus |
| `get_focused_pane()` | `str\|None` | Get focused ID |
| `get_pane_ids()` | `List[str]` | All pane IDs |
| `undo()` / `redo()` | `bool` | Undo/redo ops |
| `save_layout(path)` | `bool` | Save to file |
| `get_layout_json()` | `str` | Get as JSON |

---

## MultisplitWidget

```python
class MultisplitWidget(QWidget)
```

Main widget providing runtime pane splitting.

### Constructor

```python
MultisplitWidget(provider: Optional[WidgetProvider] = None,
                parent: Optional[QWidget] = None)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `provider` | `WidgetProvider\|None` | Creates widgets for panes |
| `parent` | `QWidget\|None` | Parent Qt widget |

### Core Methods

#### initialize_empty
```python
initialize_empty(widget_id: str = "default") -> None
```
Start with a single pane containing the specified widget.

#### split_pane
```python
split_pane(pane_id: str, widget_id: str,
          position: WherePosition, ratio: float = 0.5) -> bool
```
Split existing pane into two.

| Parameter | Type | Description |
|-----------|------|-------------|
| `pane_id` | `str` | Pane to split |
| `widget_id` | `str` | Widget for new pane |
| `position` | `WherePosition` | Where to place new pane |
| `ratio` | `float` | Split ratio (0.0-1.0) |

**Returns:** `True` if successful

#### remove_pane
```python
remove_pane(pane_id: str) -> bool
```
Remove pane from layout. Cannot remove last pane.

#### focus_pane
```python
focus_pane(pane_id: str) -> bool
```
Set keyboard focus to specific pane.

#### navigate_focus
```python
navigate_focus(direction: Direction) -> bool
```
Move focus to adjacent pane in direction (LEFT/RIGHT/UP/DOWN).

### Query Methods

#### get_pane_ids
```python
get_pane_ids() -> List[str]
```
Get all current pane IDs.

#### get_focused_pane
```python
get_focused_pane() -> Optional[str]
```
Get currently focused pane ID or None.

### Persistence Methods

#### save_layout / load_layout
```python
save_layout(filepath: Path) -> bool
load_layout(filepath: Path) -> bool
```
Save/load layout to/from file.

#### get_layout_json / set_layout_json
```python
get_layout_json() -> str
set_layout_json(json_str: str) -> bool
```
Get/set layout as JSON string.

### History Methods

#### undo / redo
```python
undo() -> bool
redo() -> bool
can_undo() -> bool
can_redo() -> bool
```
Undo/redo support for operations.

### Configuration Methods

#### set_constraints
```python
set_constraints(pane_id: str, min_width: int = 50, min_height: int = 50,
               max_width: Optional[int] = None,
               max_height: Optional[int] = None) -> bool
```
Set size constraints for a pane (in pixels).

#### set_widget_provider
```python
set_widget_provider(provider: WidgetProvider) -> None
```
Change widget provider at runtime.

---

## WidgetProvider Protocol

```python
class WidgetProvider(Protocol):
    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Create widget for pane."""
        ...

    def widget_closing(self, widget_id: str, widget: QWidget) -> None:
        """Optional: Handle cleanup."""
        ...
```

### Implementation Example

```python
class MyProvider:
    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        if widget_id.startswith("editor:"):
            return QTextEdit()
        return QLabel(widget_id)

    def widget_closing(self, widget_id: str, widget: QWidget):
        # Optional cleanup
        pass
```

---

## Enums

### WherePosition
```python
class WherePosition(str, Enum):
    LEFT = "left"      # Split horizontally, new on left
    RIGHT = "right"    # Split horizontally, new on right
    TOP = "top"        # Split vertically, new on top
    BOTTOM = "bottom"  # Split vertically, new on bottom
```

### Direction
```python
class Direction(str, Enum):
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"
```

### Orientation
```python
class Orientation(str, Enum):
    HORIZONTAL = "horizontal"  # Left-right split
    VERTICAL = "vertical"      # Top-bottom split
```

---

## Signals

| Signal | Parameters | Description |
|--------|------------|-------------|
| `pane_added` | `str` | New pane created |
| `pane_removed` | `str` | Pane removed |
| `pane_focused` | `str` | Focus changed |
| `layout_changed` | - | Structure modified |
| `widget_needed` | `str, str` | Widget requested |
| `validation_failed` | `list` | Operation failed |

### Connection Example

```python
multisplit.pane_focused.connect(lambda pane_id: print(f"Focus: {pane_id}"))
multisplit.pane_added.connect(on_pane_added)
multisplit.validation_failed.connect(lambda errors: handle_errors(errors))
```

---

## Exceptions

```
PaneError                  # Base exception
├── PaneNotFoundError     # Invalid pane ID
├── InvalidStructureError # Tree corrupted
├── InvalidRatioError     # Bad split ratio
├── WidgetProviderError   # Provider failed
└── CommandExecutionError # Command failed
```

### Usage

```python
from vfwidgets_multisplit.core.types import PaneNotFoundError

try:
    multisplit.remove_pane("invalid-id")
except PaneNotFoundError as e:
    print(f"Pane not found: {e.pane_id}")
```

---

## Data Classes

### SizeConstraints

```python
@dataclass
class SizeConstraints:
    min_width: int = 50
    min_height: int = 50
    max_width: Optional[int] = None
    max_height: Optional[int] = None
```

---

## Complete Example

```python
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit
from vfwidgets_multisplit import MultisplitWidget
from vfwidgets_multisplit.core.types import WherePosition, Direction

# 1. Define provider
class MyProvider:
    def provide_widget(self, widget_id: str, pane_id: str):
        return QTextEdit(f"Content: {widget_id}")

# 2. Create application
app = QApplication([])
window = QMainWindow()

# 3. Setup MultiSplit
provider = MyProvider()
multisplit = MultisplitWidget(provider=provider)
window.setCentralWidget(multisplit)

# 4. Connect signals
multisplit.pane_focused.connect(
    lambda p: window.setWindowTitle(f"Focus: {p[:8]}")
)

# 5. Build layout
multisplit.initialize_empty("editor:main.py")
pane = multisplit.get_focused_pane()

# Add sidebar
multisplit.split_pane(pane, "sidebar", WherePosition.LEFT, 0.2)

# Add terminal
multisplit.split_pane(pane, "terminal", WherePosition.BOTTOM, 0.7)

# 6. Run
window.show()
app.exec()
```

---

## Type Aliases

```python
PaneId = NewType('PaneId', str)      # Pane identifier
NodeId = NewType('NodeId', str)      # Internal node ID
WidgetId = NewType('WidgetId', str)  # Widget type ID
```

*In practice, these are strings but provide semantic meaning for type checkers.*

---

## Version

- **Version:** 1.0.0
- **Python:** 3.8+
- **Qt:** PySide6/PyQt6
- **Status:** Stable API

## See Also

- [Usage Guide](usage.md) - Practical patterns
- [Examples](../examples/) - Working code
- Run: `python examples/run_examples.py`