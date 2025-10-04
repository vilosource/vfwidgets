# MultisplitWidget API Reference (v0.2.0)

Complete API documentation for MultisplitWidget - a runtime-splittable pane widget for PySide6/PyQt6.

## Quick Import

```python
from vfwidgets_multisplit import (
    MultisplitWidget,
    WidgetProvider,
    WherePosition,
    Direction,
    SplitterStyle,
)
```

---

## MultisplitWidget

The main widget that manages split panes.

### Constructor

```python
MultisplitWidget(provider: WidgetProvider = None, parent: QWidget = None)
```

**Parameters:**
- `provider` - WidgetProvider instance for creating widgets
- `parent` - Optional parent QWidget

**Example:**
```python
multisplit = MultisplitWidget(provider=MyProvider())
```

---

### Pane Management

#### `initialize_empty(widget_id: str = "default") -> bool`

Initialize with a single root pane.

**Parameters:**
- `widget_id` - ID passed to provider's `provide_widget()`

**Returns:** `True` if successful

**Example:**
```python
multisplit.initialize_empty("editor-1")
```

---

#### `split_pane(pane_id: str, widget_id: str, position: WherePosition, ratio: float = 0.5) -> bool`

Split an existing pane, adding a new pane beside it.

**Parameters:**
- `pane_id` - ID of pane to split
- `widget_id` - ID for new widget (passed to provider)
- `position` - Where to place new pane (`WherePosition.LEFT/RIGHT/TOP/BOTTOM`)
- `ratio` - Split ratio (0.0 to 1.0, default 0.5)

**Returns:** `True` if successful, `False` if pane not found or invalid ratio

**Example:**
```python
focused = multisplit.get_focused_pane()
multisplit.split_pane(focused, "editor-2", WherePosition.RIGHT, 0.5)
```

**Visual:**
```
BEFORE:                    AFTER (RIGHT, 0.5):
┌─────────────┐           ┌──────┬──────┐
│   pane_id   │    -->    │ old  │ NEW  │
│             │           │ 50%  │ 50%  │
└─────────────┘           └──────┴──────┘
```

---

#### `remove_pane(pane_id: str) -> bool`

Remove a pane and its widget.

**Parameters:**
- `pane_id` - ID of pane to remove

**Returns:** `True` if successful, `False` if pane not found or is last pane

**Note:** Cannot remove the last pane. Calls `widget_closing()` hook before removal.

**Example:**
```python
multisplit.remove_pane(pane_id)
```

---

#### `get_pane_ids() -> list[str]`

Get list of all pane IDs.

**Returns:** List of pane ID strings

**Example:**
```python
all_panes = multisplit.get_pane_ids()
print(f"Total panes: {len(all_panes)}")
```

---

#### `get_focused_pane() -> Optional[str]`

Get the currently focused pane ID.

**Returns:** Pane ID string or `None` if no pane is focused

**Example:**
```python
focused = multisplit.get_focused_pane()
if focused:
    print(f"Focused: {focused}")
```

---

#### `focus_pane(pane_id: str) -> bool`

Programmatically set focus to a pane.

**Parameters:**
- `pane_id` - ID of pane to focus

**Returns:** `True` if successful

**Example:**
```python
multisplit.focus_pane(first_pane_id)
```

---

### Widget Lookup (v0.2.0+)

#### `get_widget(pane_id: str) -> Optional[QWidget]`

Get the widget in a specific pane.

**Parameters:**
- `pane_id` - ID of pane

**Returns:** QWidget instance or `None` if pane not found

**Example:**
```python
focused = multisplit.get_focused_pane()
if focused:
    widget = multisplit.get_widget(focused)
    if widget:
        widget.setText("Hello!")
```

---

#### `get_all_widgets() -> dict[str, QWidget]`

Get all widgets mapped by pane ID.

**Returns:** Dictionary mapping pane IDs to widgets

**Example:**
```python
for pane_id, widget in multisplit.get_all_widgets().items():
    widget.update_theme()
```

---

#### `find_pane_by_widget(widget: QWidget) -> Optional[str]`

Find which pane contains a widget.

**Parameters:**
- `widget` - QWidget instance to search for

**Returns:** Pane ID string or `None` if not found

**Example:**
```python
pane_id = multisplit.find_pane_by_widget(my_text_edit)
if pane_id:
    multisplit.focus_pane(pane_id)
```

---

### Navigation

#### `navigate_focus(direction: Direction) -> bool`

Move focus to adjacent pane in a direction.

**Parameters:**
- `direction` - `Direction.UP/DOWN/LEFT/RIGHT`

**Returns:** `True` if focus moved, `False` if no adjacent pane

**Example:**
```python
# Vim-like navigation
multisplit.navigate_focus(Direction.LEFT)  # h
multisplit.navigate_focus(Direction.DOWN)  # j
multisplit.navigate_focus(Direction.UP)    # k
multisplit.navigate_focus(Direction.RIGHT) # l
```

---

### Session Management

#### `save_session() -> str`

Save current layout as JSON.

**Returns:** JSON string representing layout structure

**Example:**
```python
json_data = multisplit.save_session()
with open("session.json", "w") as f:
    f.write(json_data)
```

---

#### `load_session(json_str: str) -> bool`

Restore layout from JSON.

**Parameters:**
- `json_str` - JSON string from `save_session()`

**Returns:** `True` if successful

**Note:** Calls `provide_widget()` for each pane in saved layout.

**Example:**
```python
with open("session.json") as f:
    json_data = f.read()
multisplit.load_session(json_data)
```

---

### Styling

#### `set_splitter_style(style: SplitterStyle) -> None`

Set visual style for split handles.

**Parameters:**
- `style` - `SplitterStyle` instance

**Example:**
```python
# Minimal style (thin handles)
multisplit.set_splitter_style(SplitterStyle.minimal())

# Compact style (thicker, visible handles)
multisplit.set_splitter_style(SplitterStyle.compact())

# Custom style
custom = SplitterStyle(
    handle_width=8,
    handle_color="#333",
    hover_color="#555"
)
multisplit.set_splitter_style(custom)
```

---

### Signals

All signals are Qt signals - connect with `.connect()`:

#### `pane_added(str)`

Emitted when a pane is added.

**Parameters:** `pane_id` - ID of added pane

**Example:**
```python
multisplit.pane_added.connect(on_pane_added)

def on_pane_added(pane_id: str):
    print(f"Pane added: {pane_id}")
```

---

#### `pane_removed(str)`

Emitted when a pane is removed.

**Parameters:** `pane_id` - ID of removed pane

**Example:**
```python
multisplit.pane_removed.connect(on_pane_removed)

def on_pane_removed(pane_id: str):
    print(f"Pane removed: {pane_id}")
```

---

#### `focus_changed(str, str)` *(v0.2.0+)*

Emitted when focus changes between panes.

**Parameters:**
- `old_pane_id` - Previous focused pane (empty string if none)
- `new_pane_id` - New focused pane (empty string if none)

**Example:**
```python
multisplit.focus_changed.connect(on_focus_changed)

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

---

#### `layout_changed()`

Emitted when layout structure changes (split, remove, load).

**Example:**
```python
multisplit.layout_changed.connect(on_layout_changed)

def on_layout_changed():
    print("Layout changed - save session?")
```

---

## WidgetProvider Protocol

Protocol for providing widgets to panes.

### Required Methods

#### `provide_widget(widget_id: str, pane_id: str) -> QWidget`

Create a widget for a pane.

**Parameters:**
- `widget_id` - Identifies WHAT to create (passed to `initialize_empty()` or `split_pane()`)
- `pane_id` - Identifies WHERE it goes (unique pane ID)

**Returns:** QWidget instance

**Example:**
```python
class MyProvider(WidgetProvider):
    def provide_widget(self, widget_id: str, pane_id: str):
        if widget_id.startswith("editor:"):
            return QTextEdit()
        elif widget_id.startswith("terminal:"):
            return TerminalWidget()
        else:
            return QLabel(f"Unknown: {widget_id}")
```

---

### Optional Methods

#### `widget_closing(widget_id: str, pane_id: str, widget: QWidget) -> None` *(v0.2.0+)*

Called before a widget is removed from a pane.

**Parameters:**
- `widget_id` - The widget ID
- `pane_id` - The pane ID
- `widget` - The actual QWidget instance

**Use cases:**
- Save unsaved changes
- Release resources
- Update internal tracking

**Example:**
```python
class MyProvider(WidgetProvider):
    def widget_closing(self, widget_id: str, pane_id: str, widget: QWidget):
        # Save state
        if isinstance(widget, QTextEdit):
            self.save_content(widget_id, widget.toPlainText())

        # Cleanup
        widget.cleanup()
        print(f"Widget {widget_id} closing")
```

---

## Enums

### WherePosition

Position for new pane when splitting.

```python
class WherePosition(Enum):
    LEFT = "left"      # New pane on left, existing on right
    RIGHT = "right"    # New pane on right, existing on left
    TOP = "top"        # New pane on top, existing on bottom
    BOTTOM = "bottom"  # New pane on bottom, existing on top
```

**Visual:**
```
LEFT:               RIGHT:              TOP:                BOTTOM:
┌────┬────┐        ┌────┬────┐        ┌─────────┐         ┌─────────┐
│NEW │old │        │old │NEW │        │   NEW   │         │   old   │
└────┴────┘        └────┴────┘        ├─────────┤         ├─────────┤
                                      │   old   │         │   NEW   │
                                      └─────────┘         └─────────┘
```

---

### Direction

Direction for focus navigation.

```python
class Direction(Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
```

---

### SplitterStyle

Visual style for split handles.

#### Factory Methods

```python
SplitterStyle.minimal()   # Thin, subtle handles
SplitterStyle.compact()   # Thicker, visible handles
```

#### Custom Style

```python
SplitterStyle(
    handle_width: int = 4,
    handle_color: str = "#ccc",
    hover_color: str = "#999"
)
```

---

## Type Aliases

```python
PaneId = str      # Unique identifier for a pane
WidgetId = str    # Identifier for widget content
```

---

## Error Handling

Most methods return `bool` to indicate success/failure. Failed operations return `False` and log warnings.

**Example:**
```python
if not multisplit.split_pane(pane_id, "widget-1", WherePosition.RIGHT):
    print("Split failed - pane may not exist")

if not multisplit.remove_pane(pane_id):
    print("Remove failed - may be last pane")
```

---

## Best Practices

1. **Check return values** - Most operations can fail
2. **Use widget lookup APIs** - Don't manually track widgets (v0.2.0+)
3. **Implement widget_closing()** - For proper cleanup (v0.2.0+)
4. **Use clean imports** - Import from main package (v0.2.0+)
5. **Handle focus changes** - Use `focus_changed` signal for UI updates

See [GUIDE.md](GUIDE.md) for detailed best practices and patterns.

---

## Version Notes

- **v0.2.0** - Added widget lookup APIs, `focus_changed` signal, `widget_closing()` hook
- **v0.1.x** - Initial release (see [MIGRATION.md](MIGRATION.md) for upgrade guide)

For breaking changes and migration, see [MIGRATION.md](MIGRATION.md).
