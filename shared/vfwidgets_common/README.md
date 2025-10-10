# VFWidgets Common

Shared utilities and base classes for VFWidgets, including cross-platform desktop integration.

## Installation

This package is typically installed as a dependency when installing individual widgets:

```bash
# Install from local path (for development)
pip install -e ../../shared/vfwidgets_common
```

## Components

### Desktop Integration (NEW)

**Unified cross-platform desktop integration for Qt applications.** This is the recommended way to bootstrap all VFWidgets applications.

#### Quick Start

```python
from vfwidgets_common.desktop import configure_desktop

# Single call handles everything
app = configure_desktop(
    app_name="myapp",
    app_display_name="My Application",
    icon_name="myapp",
    desktop_categories="Utility;",
)

window = MyMainWindow()
window.show()
sys.exit(app.exec())
```

#### What It Does

The `configure_desktop()` API automatically:

1. **Detects Platform** - OS, desktop environment, display server, WSL, containers
2. **Applies Platform Quirks** - Fixes platform-specific issues automatically
3. **Checks Desktop Integration** - Verifies icons and .desktop files are installed (Linux)
4. **Creates QApplication** - With proper metadata and theme integration
5. **Returns Configured App** - Ready to use

#### Platform Quirks Applied Automatically

- **WSL** - Forces software rendering for Qt WebEngine (fixes OpenGL crashes)
- **Wayland** - HiDPI scaling, window matching, XDG Portal integration
- **Remote Desktop** - Optimized rendering for RDP/VNC
- **Containers** - Appropriate graphics configuration

#### Platform Support

| Platform | Status | Features |
|----------|--------|----------|
| Linux (GNOME/KDE/XFCE) | ✅ Ready | XDG desktop integration, icons, .desktop files |
| WSL (WSL1/WSL2) | ✅ Ready | Automatic software rendering |
| Wayland | ✅ Ready | HiDPI scaling, window matching |
| X11 | ✅ Ready | Full compatibility |
| Windows/macOS | 🔜 Future | Extensible backend architecture |

#### Advanced Usage with ThemedApplication

```python
from vfwidgets_common.desktop import configure_desktop
from vfwidgets_theme import ThemedApplication

app = configure_desktop(
    app_name="viloxterm",
    app_display_name="ViloxTerm",
    icon_name="viloxterm",
    desktop_categories="System;TerminalEmulator;",
    application_class=ThemedApplication,  # Custom QApplication class
    theme_config={"persist_theme": True}, # Passed to ThemedApplication
)
```

#### Documentation

- [Complete Design Document](wip/unified-desktop-integration-DESIGN.md)
- [ViloxTerm Usage Example](../../apps/viloxterm/README.md)



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