# MarkdownViewerWidget API Documentation

## Class: `MarkdownViewerWidget`

### Description
Custom PySide6 widget for [describe purpose].

### Inheritance
- `QWidget` (or `VFBaseWidget` if using common utilities)

### Signals

#### `value_changed(value: object)`
Emitted when the widget value changes.

**Parameters:**
- `value`: The new value of the widget

### Methods

#### `__init__(parent: Optional[QWidget] = None)`
Initialize the widget.

**Parameters:**
- `parent`: Parent widget (optional)

#### `set_value(value: object) -> None`
Set the widget value.

**Parameters:**
- `value`: The value to set

#### `get_value() -> object`
Get the current widget value.

**Returns:**
- The current value of the widget

### Usage Example

```python
from vfwidgets_markdown_viewer import MarkdownViewerWidget

widget = MarkdownViewerWidget()
widget.set_value("Hello")
current_value = widget.get_value()

# Connect to signal
widget.value_changed.connect(on_value_changed)
```

### Styling

The widget can be styled using Qt stylesheets:

```python
widget.setStyleSheet("""
    MarkdownViewerWidget {
        background-color: #f0f0f0;
        border: 1px solid #ccc;
    }
""")
```

### Properties

| Property | Type | Description | Default |
|----------|------|-------------|---------|
| value | object | The widget value | None |

### Events

The widget responds to standard Qt events and can be subclassed to handle custom events.
