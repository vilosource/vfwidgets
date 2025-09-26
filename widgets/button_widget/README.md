# VFWidgets ButtonWidget

A custom PySide6 button widget for the VFWidgets collection.

## Installation

```bash
# Install from local path
pip install ./widgets/button_widget

# Install in editable mode for development
pip install -e ./widgets/button_widget

# Install with development dependencies
pip install -e "./widgets/button_widget[dev]"
```

## Usage

```python
from PySide6.QtWidgets import QApplication
from vfwidgets_button import ButtonWidget

app = QApplication([])

widget = ButtonWidget()
widget.show()

app.exec()
```

## Features

- Feature 1
- Feature 2
- Feature 3

## Development

```bash
# Run tests
cd widgets/button_widget
pytest

# Format code
black src/

# Lint
ruff check src/

# Type check
mypy src/
```

## API Documentation

See [API documentation](docs/api.md) for detailed usage.

## Examples

Check the `examples/` directory for usage examples:
- `basic_usage.py` - Simple usage example
- `advanced_features.py` - Advanced features demonstration

## License

MIT License - See LICENSE file for details.
