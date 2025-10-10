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

### FramelessWindowBehavior

Encapsulates frameless window dragging and resizing behavior using Qt's native window management APIs. This class eliminates code duplication across widgets that implement custom window frames.

**Features:**
- Native window dragging via `startSystemMove()` with fallback
- Edge-based window resizing via `startSystemResize()` with fallback
- Automatic cursor updates for resize edges
- Configurable draggable areas (via widget or callback)
- Configurable resize margins
- Double-click to maximize support

**Basic Usage:**

```python
from PySide6.QtWidgets import QWidget
from vfwidgets_common import FramelessWindowBehavior

class MyFramelessWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Initialize behavior with draggable widget (e.g., title bar)
        self._frameless_behavior = FramelessWindowBehavior(
            draggable_widget=self.title_bar,
            resize_margin=5,
            enable_resize=True,
            enable_drag=True,
            enable_double_click_maximize=True,
        )

    def mousePressEvent(self, event):
        if self._frameless_behavior.handle_press(self, event):
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._frameless_behavior.handle_move(self, event):
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._frameless_behavior.handle_release(self, event):
            return
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if self._frameless_behavior.handle_double_click(self, event):
            return
        super().mouseDoubleClickEvent(event)
```

**Advanced Usage with Custom Draggable Area Callback:**

```python
def is_draggable_area(widget: QWidget, pos: QPoint) -> bool:
    """Check if position is in custom draggable area."""
    # Custom logic to determine if position should trigger dragging
    # For example, check if click is on empty tab bar area
    return pos.y() < 30 and not is_on_button(pos)

self._frameless_behavior = FramelessWindowBehavior(
    draggable_widget=None,  # Use callback instead
    is_draggable_area=is_draggable_area,
    resize_margin=4,
)
```

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