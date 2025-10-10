# MarkdownViewer Usage Guide

## Installation

```bash
pip install vfwidgets-markdown_viewer
```

## Basic Usage

### Simple Example

```python
from PySide6.QtWidgets import QApplication
from vfwidgets_markdown import MarkdownViewer

app = QApplication([])

widget = MarkdownViewer()
widget.show()

app.exec()
```

### Integration with Existing UI

```python
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from vfwidgets_markdown import MarkdownViewer

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Add our custom widget
        custom_widget = MarkdownViewer()
        layout.addWidget(custom_widget)
```

## Advanced Usage

### Customizing Appearance

```python
widget = MarkdownViewer()
widget.setStyleSheet("""
    /* Custom styles here */
""")
```

### Handling Signals

```python
def on_value_changed(value):
    print(f"New value: {value}")

widget = MarkdownViewer()
widget.value_changed.connect(on_value_changed)
```

## Common Patterns

### Pattern 1: Data Binding

```python
# Bind widget to data model
widget.value_changed.connect(model.update_data)
model.data_changed.connect(widget.set_value)
```

### Pattern 2: Validation

```python
def validate_and_set(value):
    if is_valid(value):
        widget.set_value(value)
    else:
        show_error("Invalid value")
```

## Troubleshooting

### Issue: Widget not displaying
- Ensure QApplication is created before widget
- Check parent widget and layout

### Issue: Signals not connecting
- Verify signal signature matches slot
- Check for typos in signal names

## Best Practices

1. Always handle widget cleanup in parent destructors
2. Use type hints for better IDE support
3. Connect to signals before setting initial values
4. Test widget in isolation before integration
