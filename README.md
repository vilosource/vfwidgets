# VFWidgets - PySide6 Qt Widgets Collection

A monorepo collection of reusable PySide6 Qt widgets, each independently installable and maintainable.

## Repository Structure

```
vfwidgets/
├── widgets/           # Individual widget packages
├── shared/           # Shared utilities and base classes
├── tools/            # Development tools and scripts
├── docs/             # Documentation and guidelines
└── .github/          # CI/CD workflows
```

## Quick Start

### Installing a Widget

Each widget can be installed independently:

```bash
# Install from local path
pip install ./widgets/button_widget

# Install in editable mode for development
pip install -e ./widgets/button_widget

# Install with development dependencies
pip install -e "./widgets/button_widget[dev]"
```

### Creating a New Widget

Use the widget generator script to create a new widget from the template:

```bash
python tools/create_widget.py my_new_widget
```

This will create a new widget package in `widgets/my_new_widget/` with the standard structure.

## Shared Libraries

### vfwidgets_common - Cross-Platform Application Utilities

**Essential for building VFWidgets applications.** Provides cross-platform desktop integration and application bootstrap functionality.

**Installation:**
```bash
pip install -e ./shared/vfwidgets_common
```

**Key Feature: Unified Desktop Integration**

The `configure_desktop()` API handles all cross-platform concerns for Qt applications:

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

**What It Does:**
- ✅ **Platform Detection** - Detects OS, desktop environment, display server, WSL, containers
- ✅ **Automatic Quirks** - Applies platform-specific fixes automatically
  - WSL: Software rendering for Qt WebEngine
  - Wayland: HiDPI scaling and window matching
  - Remote Desktop: Rendering optimizations
- ✅ **Desktop Integration** - Checks/installs desktop files and icons (Linux)
- ✅ **QApplication Setup** - Proper metadata and theme integration

**Platform Support:**
- Linux (GNOME, KDE, XFCE) - XDG desktop integration
- WSL (WSL1, WSL2) - Automatic software rendering
- Wayland - HiDPI scaling and XDG Portal
- X11 - Full compatibility
- Windows/macOS - Extensible backend (coming soon)

**Documentation:**
- [Desktop Integration Design](shared/vfwidgets_common/wip/unified-desktop-integration-DESIGN.md)
- See [ViloxTerm](apps/viloxterm/README.md) for production usage example

## Available Widgets

| Widget | Description | Status | Documentation |
|--------|-------------|--------|---------------|
| button_widget | Enhanced button with animations and styles | 🟢 Ready | [Docs](widgets/button_widget/README.md) |
| theme_system | VSCode-compatible theme management | 🟢 Ready | [Docs](widgets/theme_system/README.md) |
| multisplit_widget | Dynamic split pane widget | 🟢 Ready | [Docs](widgets/multisplit_widget/README.md) |
| terminal_widget | xterm.js-based terminal emulator | 🟢 Ready | [Docs](widgets/terminal_widget/README.md) |
| markdown_widget | Professional markdown editor/viewer with theme support | 🟢 Ready | [Docs](widgets/markdown_widget/README.md) |
| chrome-tabbed-window | Chrome-style tabbed window | 🟢 Ready | [Docs](widgets/chrome-tabbed-window/README.md) |
| vilocode_window | VS Code-style frameless window | 🟢 Ready | [Docs](widgets/vilocode_window/README.md) |
| keybinding_manager | User-customizable keyboard shortcuts | 🟢 Ready | [Docs](widgets/keybinding_manager/README.md) |

## Applications

### ViloxTerm - Modern Terminal Emulator

Full-featured terminal application demonstrating integration of multiple VFWidgets components.

**Installation:**
```bash
cd apps/viloxterm
make local-release  # Builds and installs with GNOME/KDE integration
```

**Features:**
- Chrome-style tabs with split panes
- Multi-session terminal server (xterm.js)
- VSCode-compatible themes with live switching
- Comprehensive preferences system (58 settings across 4 tabs)
  - Terminal font customization (family, size, line height, spacing)
  - Window opacity and appearance controls
  - Performance and behavior settings
- User-customizable keyboard shortcuts
- Cross-platform desktop integration

**Documentation:** [apps/viloxterm/README.md](apps/viloxterm/README.md)

### Theme Studio - Visual Theme Editor

Interactive theme editor for creating and editing VSCode-compatible themes.

**Installation:**
```bash
cd apps/theme-studio
pip install -e .
python -m theme_studio
```

**Features:**
- Visual editing of all theme tokens
- Font property editing with live preview
- Color token browser with hierarchical organization
- Font token browser with system font detection
- Real-time preview of changes
- Export to VSCode-compatible JSON themes
- Undo/redo support

**Documentation:** [apps/theme-studio/README.md](apps/theme-studio/README.md)

## Development

### Prerequisites

- Python 3.9+
- PySide6 6.9.0+
- Git

### Setting Up Development Environment

1. Clone the repository:
```bash
git clone https://github.com/yourusername/vfwidgets.git
cd vfwidgets
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development tools:
```bash
pip install -U pip setuptools wheel
pip install pytest pytest-qt black ruff mypy
```

4. Install a widget in development mode:
```bash
pip install -e "./widgets/button_widget[dev]"
```

### Running Tests

```bash
# Test a specific widget
cd widgets/button_widget
pytest

# Test all widgets
./tools/test_all.sh
```

### Code Quality

All widgets should follow these standards:

- **Formatting**: Black (line length 100)
- **Linting**: Ruff
- **Type Checking**: MyPy
- **Testing**: Pytest with pytest-qt

Run checks:
```bash
black --check src/
ruff check src/
mypy src/
```

## Documentation

### For Widget Developers

- **[Widget DX Principles](docs/widget-dx-principles-GUIDE.md)** - Developer experience best practices for creating VFWidgets
- **[Widget Development Guide](docs/widget-development-GUIDE.md)** - Step-by-step guide for creating new widgets
- **[New Widget Checklist](docs/new-widget-checklist.md)** - Ensure you don't miss critical steps

### For Application Developers

- **[Building Apps Checklist](docs/building-apps-CHECKLIST.md)** - Complete checklist for building VFWidgets applications
- **[Theme Integration Guide](docs/theme-integration-GUIDE.md)** - How to properly integrate the theme system
- **[Task-Driven Development](docs/task-driven-development-GUIDE.md)** - Development methodology guide

### Architecture & Design Docs

- **[Single Instance Design](docs/single-instance-DESIGN.md)** - Single-instance application pattern
- **[Multi-Window Architecture](docs/multi-window-architecture-DESIGN.md)** - Multi-window application design
- **[Context Menu Architecture](docs/context-menu-architecture-SPEC.md)** - Context menu system specification

## Widget Development Guidelines

Each widget should:

1. **Be Self-Contained**: Minimal external dependencies beyond PySide6
2. **Follow Naming Convention**: `vfwidgets_<name>` for package namespace
3. **Include Documentation**: README, docstrings, and usage examples
4. **Have Tests**: Unit tests using pytest-qt
5. **Provide Examples**: Runnable example scripts in `examples/`

### Standard Widget Structure

```
widgets/my_widget/
├── pyproject.toml          # Package configuration
├── README.md              # Widget documentation
├── src/
│   └── vfwidgets_my_widget/
│       ├── __init__.py
│       ├── widget.py      # Main widget implementation
│       └── resources/     # Icons, styles, etc.
├── tests/
│   └── test_widget.py
└── examples/
    └── basic_usage.py
```

## Publishing Widgets

Widgets can be published to PyPI independently:

```bash
cd widgets/button_widget
python -m build
python -m twine upload dist/*
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run quality checks
6. Submit a pull request

## License

Each widget may have its own license. Check the individual widget directories for specific licensing information.

## Support

For issues, questions, or contributions, please open an issue on GitHub.