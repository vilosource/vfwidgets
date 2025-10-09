# ViloCodeWindow

A VS Code-style application window widget for PySide6 with activity bar, sidebar, main pane, and auxiliary bar. Build professional IDE-style applications with ease.

## Features

- **Dual-Mode Operation**: Works as a frameless top-level window or embedded widget
- **VS Code Layout**: Activity bar, collapsible sidebar, main content area, and auxiliary bar
- **Keyboard Shortcuts**: VS Code-compatible shortcuts (Ctrl+B, F11, etc.) - fully customizable
- **Theme Integration**: Automatic integration with [vfwidgets-theme](../theme_system/)
- **Platform Support**: Windows, macOS, Linux (X11/Wayland), WSL
- **Flexible Content**: Use any Qt widget in the main pane (ChromeTabbedWindow, MultisplitWidget, etc.)
- **Easy to Use**: 4-tier API from simple (Tier 1) to advanced (Tier 4)

## Installation

```bash
# Basic installation
pip install vfwidgets-vilocode-window

# With theme support
pip install vfwidgets-vilocode-window[theme]

# Development installation
pip install -e ".[dev]"
```

## Quick Start

### Tier 1: Simplest Usage

```python
from PySide6.QtWidgets import QApplication, QTextEdit
from vfwidgets_vilocode_window import ViloCodeWindow

app = QApplication([])

# Create window
window = ViloCodeWindow()

# Set main content
window.set_main_content(QTextEdit("Hello, World!"))

window.show()
app.exec()
```

### Tier 2: With Sidebar

```python
from PySide6.QtWidgets import QApplication, QTextEdit, QTreeView
from PySide6.QtGui import QIcon
from vfwidgets_vilocode_window import ViloCodeWindow

app = QApplication([])
window = ViloCodeWindow()

# Add activity items
files_action = window.add_activity_item(
    "files",
    QIcon("icons/files.png"),
    "Explorer"
)

# Add sidebar panel
window.add_sidebar_panel(
    "explorer",
    QTreeView(),
    "EXPLORER"
)

# Connect activity item to show panel
files_action.triggered.connect(
    lambda: window.show_sidebar_panel("explorer")
)

# Set main content
window.set_main_content(QTextEdit())

window.show()
app.exec()
```

### Tier 3: Declarative Configuration

```python
from vfwidgets_vilocode_window import ViloCodeWindow

window = ViloCodeWindow()

# Configure everything at once
window.configure({
    "activity_items": [
        {"id": "files", "icon": files_icon, "tooltip": "Explorer"},
        {"id": "search", "icon": search_icon, "tooltip": "Search"},
    ],
    "sidebar_panels": [
        {"id": "explorer", "widget": QTreeView(), "title": "EXPLORER"},
        {"id": "search", "widget": QWidget(), "title": "SEARCH"},
    ],
    "main_content": ChromeTabbedWindow(),
    "auto_connect": True,  # Automatically connect activity items to panels
})
```

## API Overview

### Constructor

```python
ViloCodeWindow(
    parent: Optional[QWidget] = None,
    enable_default_shortcuts: bool = True
)
```

### Activity Bar (10 methods)

```python
# Basic
add_activity_item(id, icon, tooltip) → QAction
remove_activity_item(id)
set_active_activity_item(id)
get_active_activity_item() → str

# Enhanced
set_activity_item_icon(id, icon)
set_activity_item_enabled(id, enabled)
is_activity_item_enabled(id) → bool
get_activity_items() → List[str]
```

### Sidebar (13 methods)

```python
# Panel Management
add_sidebar_panel(id, widget, title)
remove_sidebar_panel(id)
show_sidebar_panel(id)
get_sidebar_panel(id) → QWidget
get_current_sidebar_panel() → str

# Visibility
toggle_sidebar()
set_sidebar_visible(visible)
is_sidebar_visible() → bool

# Sizing
set_sidebar_width(width)
get_sidebar_width() → int

# Enhanced
set_sidebar_panel_widget(id, widget)
set_sidebar_panel_title(id, title)
get_sidebar_panels() → List[str]
set_sidebar_width_constraints(min, max)
```

### Main Pane (2 methods)

```python
set_main_content(widget)
get_main_content() → QWidget
```

### Auxiliary Bar (7 methods)

```python
set_auxiliary_content(widget)
get_auxiliary_content() → QWidget
toggle_auxiliary_bar()
set_auxiliary_bar_visible(visible)
is_auxiliary_bar_visible() → bool
set_auxiliary_bar_width(width)
get_auxiliary_bar_width() → int
set_auxiliary_bar_width_constraints(min, max)
```

### Keyboard Shortcuts (5 methods)

```python
register_shortcut(key, callback, desc) → QShortcut
unregister_shortcut(key)
get_shortcuts() → Dict[str, QShortcut]
get_default_shortcuts() → Dict[str, str]
set_shortcut(action, key)  # Override default
```

**Default Shortcuts** (VS Code compatible):
- `Ctrl+B` - Toggle sidebar
- `Ctrl+Alt+B` - Toggle auxiliary bar
- `Ctrl+0` - Focus sidebar
- `Ctrl+1` - Focus main pane
- `Ctrl+Shift+E/F/G/D/X` - Activity items 1-5
- `F11` - Toggle fullscreen

### Status Bar (4 methods)

```python
get_status_bar() → QStatusBar
set_status_bar_visible(visible)
is_status_bar_visible() → bool
set_status_message(message, timeout)
```

### Menu Bar (2 methods)

```python
set_menu_bar(menubar)
get_menu_bar() → QMenuBar
```

### Utilities (2 methods)

```python
@contextmanager
batch_updates()  # Defer layout updates

configure(config: dict)  # Declarative setup
```

### Signals (4)

```python
activity_item_clicked = Signal(str)
sidebar_panel_changed = Signal(str)
sidebar_visibility_changed = Signal(bool)
auxiliary_bar_visibility_changed = Signal(bool)
```

## Examples

See the [examples/](examples/) directory for more:

- `01_basic_usage.py` - Simplest possible usage
- `02_with_sidebar.py` - Activity bar and sidebar
- `03_declarative.py` - Using `configure()`
- `04_keyboard_shortcuts.py` - Custom shortcuts
- `05_theme_integration.py` - Theme system
- `06_full_ide.py` - Complete IDE with all features
- `07_embedded_mode.py` - Using as embedded widget
- `08_custom_shortcuts.py` - Advanced shortcut customization

## Documentation

- [Full Specification](docs/vilocode-window-SPECIFICATION.md) - Complete API reference
- [Architecture](docs/architecture.md) - Internal design (coming soon)
- [Keyboard Shortcuts Guide](docs/keyboard-shortcuts-GUIDE.md) - Shortcut customization (coming soon)
- [API Patterns Guide](docs/api-patterns-GUIDE.md) - Best practices (coming soon)

## Requirements

- Python 3.9+
- PySide6 >= 6.5.0
- Optional: vfwidgets-theme >= 2.0.0 (for theming)

## Platform Support

| Platform | Frameless Mode | Notes |
|----------|---------------|-------|
| Windows 10/11 | ✅ Full | Native window controls |
| macOS | ✅ Full | Native window controls |
| Linux X11 | ✅ Full | Native window controls |
| Linux Wayland | ✅ Qt 6.5+ | Requires Qt 6.5+ |
| WSL | ⚠️ Fallback | Native decorations |

## Development Status

**Current Version**: 0.1.0 (Alpha)

- ✅ Specification complete
- 🚧 Phase 1: Foundation (In Progress)
- ⏳ Phase 2: Components (Not Started)
- ⏳ Phase 3: Polish & Examples (Not Started)

See [wip/README.md](wip/README.md) for detailed implementation status.

## Contributing

This widget is part of the [VFWidgets](https://github.com/vilosource/vfwidgets) monorepo. Please see the main repository for contribution guidelines.

## License

MIT License - see LICENSE file for details.

## Related Widgets

- [chrome-tabbed-window](../chrome-tabbed-window/) - Chrome-style tabs (great for main pane!)
- [vfwidgets-theme](../theme_system/) - Theme management system
- [multisplit-widget](../multisplit_widget/) - Advanced split panes
- [terminal-widget](../terminal_widget/) - Terminal emulator
- [keybinding-manager](../keybinding_manager/) - Advanced shortcut management

## Credits

Developed by the VFWidgets team. Inspired by Visual Studio Code's layout.
