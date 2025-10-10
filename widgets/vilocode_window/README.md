# ViloCodeWindow

> **A VS Code-style application window widget for PySide6**

Build professional IDE-style applications with activity bar, collapsible sidebar, main content area, and auxiliary bar. Works as a frameless window or embedded widget.

---

## Features

- ✨ **Dual-Mode Operation**: Frameless top-level window or embedded widget
- 🎨 **VS Code Layout**: Activity bar, sidebar, main pane, auxiliary bar, status bar
- 🎬 **Smooth Animations**: 200ms collapse/expand with configurable animation
- ⌨️ **Keyboard Shortcuts**: VS Code-compatible (Ctrl+B, Ctrl+0, Ctrl+1, F11)
- 🎯 **Focus Management**: Keyboard navigation between components
- 🌈 **Theme Integration**: Automatic integration with [vfwidgets-theme](../theme_system/)
- ♿ **Accessibility**: Screen reader support, keyboard navigation
- 🖥️ **Cross-Platform**: Windows, macOS, Linux (X11/Wayland), WSL
- 🔧 **Flexible**: Use any Qt widget in main pane (ChromeTabbedWindow, MultisplitWidget, etc.)
- 📦 **Clean API**: Simple to advanced usage patterns

---

## Installation

```bash
# Basic installation
pip install vfwidgets-vilocode-window

# With theme support
pip install vfwidgets-vilocode-window[theme]

# Development installation
pip install -e ".[dev]"
```

---

## Quick Start

### Minimal Example (Tier 1)

```python
from PySide6.QtWidgets import QApplication, QTextEdit
from vfwidgets_vilocode_window import ViloCodeWindow

app = QApplication([])

# Create window and set content
window = ViloCodeWindow()
window.set_main_content(QTextEdit("Hello, World!"))
window.show()

app.exec()
```

### With Sidebar (Tier 2)

```python
from PySide6.QtWidgets import QApplication, QTextEdit, QTreeView
from PySide6.QtGui import QIcon
from vfwidgets_vilocode_window import ViloCodeWindow

app = QApplication([])
window = ViloCodeWindow()

# Add activity item and sidebar panel
files_action = window.add_activity_item("files", QIcon("icons/files.png"), "Explorer")
window.add_sidebar_panel("explorer", QTreeView(), "EXPLORER")

# Connect activity to panel
files_action.triggered.connect(lambda: window.show_sidebar_panel("explorer"))

# Set main content
window.set_main_content(QTextEdit())
window.show()

app.exec()
```

### Declarative Configuration (Tier 3)

```python
window = ViloCodeWindow()

window.configure({
    "activity_items": [
        {"id": "files", "icon": files_icon, "tooltip": "Explorer"},
        {"id": "search", "icon": search_icon, "tooltip": "Search"},
    ],
    "sidebar_panels": [
        {"id": "files", "widget": file_tree, "title": "EXPLORER"},
        {"id": "search", "widget": search_widget, "title": "SEARCH"},
    ],
    "main_content": ChromeTabbedWindow(),
    "auto_connect": True,  # Auto-connect activity items to panels
})
```

**See [examples/](examples/)** for 5 progressively complex examples from minimal to advanced IDE.

---

## Documentation

### For Users

- **[API Reference](docs/api.md)** — Complete API documentation with examples
- **[Theme Integration Guide](docs/theme.md)** — How to theme your window and child widgets
- **[Examples](examples/)** — 5 progressive examples from simple to advanced:
  - `01_minimal.py` — Absolute minimum code
  - `02_basic_layout.py` — Activity bar + sidebar + main pane
  - `03_full_layout.py` — All components (auxiliary bar, status bar)
  - `04_customization.py` — Custom shortcuts, menu bar, themes
  - `05_advanced_ide.py` — Production-ready IDE with tabs and file operations

### For Developers

- **[Architecture Guide](docs/architecture.md)** — Internal architecture and design patterns
- **[Full Specification](docs/vilocode-window-SPECIFICATION.md)** — Complete v1.0 specification

---

## API Summary

### Constructor

```python
ViloCodeWindow(parent=None, enable_default_shortcuts=True)
```

### Core APIs

- **Activity Bar**: `add_activity_item()`, `remove_activity_item()`, `set_active_activity_item()` (10 methods)
- **Sidebar**: `add_sidebar_panel()`, `toggle_sidebar()`, `set_sidebar_visible()` (13 methods)
- **Main Pane**: `set_main_content()`, `get_main_content()` (2 methods)
- **Auxiliary Bar**: `set_auxiliary_content()`, `toggle_auxiliary_bar()` (7 methods)
- **Menu Bar**: `set_menu_bar()`, `get_menu_bar()` (2 methods)
- **Status Bar**: `get_status_bar()`, `set_status_message()` (4 methods)
- **Keyboard Shortcuts**: `register_shortcut()`, `set_shortcut()` (5 methods)
- **Configuration**: `configure()`, `batch_updates()` (2 methods)

**Total**: 52 public methods + 4 signals

### Default Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+B` | Toggle sidebar |
| `Ctrl+Alt+B` | Toggle auxiliary bar |
| `Ctrl+0` | Focus sidebar |
| `Ctrl+1` | Focus main pane |
| `Ctrl+Shift+E/F/G/D/X` | Show activity items 1-5 |
| `F11` | Toggle fullscreen |

**See [API Reference](docs/api.md)** for complete documentation.

---

## Requirements

- **Python**: 3.9+
- **PySide6**: >= 6.5.0
- **Optional**: vfwidgets-theme >= 2.0.0 (for theming)

---

## Platform Support

| Platform | Frameless Mode | Notes |
|----------|---------------|-------|
| **Windows 10/11** | ✅ Full | Native window controls, Aero snap |
| **macOS** | ✅ Full | Native window controls, fullscreen |
| **Linux X11** | ✅ Full | Native window controls |
| **Linux Wayland** | ✅ Qt 6.5+ | Requires Qt 6.5+, compositor-dependent |
| **WSL/WSLg** | ⚠️ Fallback | Uses native decorations |

---

## Development Status

**Current Version**: 1.0.0 (Production Ready)

- ✅ **Phase 1**: Foundation complete
- ✅ **Phase 2**: Components complete
- ✅ **Phase 3**: Polish & examples complete
- ✅ **79/79 tests passing**
- ✅ **Production-ready**

### What's Implemented (v1.0)

- ✅ Complete VS Code-style layout
- ✅ Dual-mode operation (frameless/embedded)
- ✅ 52 public API methods
- ✅ VS Code-compatible keyboard shortcuts
- ✅ Smooth animations (200ms collapse/expand)
- ✅ Focus management
- ✅ Theme system integration
- ✅ Full accessibility support
- ✅ Cross-platform support

### Future (v2.0+)

- ⏳ Persistence (save/restore layout state)
- ⏳ Dockable panels (drag to reposition)
- ⏳ Floating panels (detach to separate windows)
- ⏳ Plugin system

---

## Contributing

This widget is part of the [VFWidgets](https://github.com/vilosource/vfwidgets) monorepo. See the main repository for contribution guidelines.

**For developers**:
- See [Architecture Guide](docs/architecture.md) for internal design
- All PRs must pass 79/79 tests: `pytest`
- Code quality: `black src/ && ruff check src/ && mypy src/`

---

## License

MIT License — see LICENSE file for details.

---

## Related Widgets

Part of the VFWidgets family:

- **[chrome-tabbed-window](../chrome-tabbed-window/)** — Chrome-style tabs (perfect for main pane!)
- **[vfwidgets-theme](../theme_system/)** — Theme management system
- **[multisplit-widget](../multisplit_widget/)** — Advanced split panes
- **[terminal-widget](../terminal_widget/)** — Terminal emulator widget
- **[keybinding-manager](../keybinding_manager/)** — Advanced shortcut management

---

## Credits

Developed by the VFWidgets team. Inspired by Visual Studio Code's layout.

**Have questions?** See the [API Reference](docs/api.md) or [examples/](examples/).
