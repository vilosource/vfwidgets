# VFWidgets Common

Shared utilities and base classes for VFWidgets.

## Installation

This package is typically installed as a dependency when installing individual widgets:

```bash
# Install from local path (for development)
pip install -e ../../shared/vfwidgets_common
```

## Components

### VFBaseWidget

Base class for all VFWidgets providing:
- Configuration management
- Common signals (widget_initialized, widget_error)
- Style change handling for theme support
- Initialization lifecycle

### Utility Functions

- `setup_widget_style()` - Apply QSS stylesheets to widgets
- `load_widget_icon()` - Load icons with fallback support
- `get_widget_resource_path()` - Access widget resources
- `ensure_widget_size()` - Set size constraints

## Usage Example

```python
from vfwidgets_common import VFBaseWidget, setup_widget_style

class MyWidget(VFBaseWidget):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

    def _setup_widget(self):
        super()._setup_widget()
        # Your initialization code here
        setup_widget_style(self, style_string="QPushButton { color: blue; }")
```

## Development

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/

# Lint
ruff check src/

# Type check
mypy src/
```