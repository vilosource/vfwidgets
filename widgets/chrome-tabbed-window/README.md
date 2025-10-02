# ChromeTabbedWindow

A professional Chrome-style tabbed window widget for PySide6/PyQt6 with full QTabWidget API compatibility.

## Features

- 🎯 **100% QTabWidget API Compatible** - Drop-in replacement for QTabWidget
- 🎨 **Theme System Integration** - Automatic color adaptation with VFWidgets theme system
- 🪟 **Dual Mode Operation**:
  - **Top-level mode**: Frameless window with custom title bar and native move/resize
  - **Embedded mode**: Regular tab widget for use in layouts
- 🌍 **Cross-Platform**: Windows, macOS, Linux (X11/Wayland), WSL/WSLg
- 🎭 **Chrome-Style UI**: Modern tab design with smooth animations
- ⚡ **High Performance**: < 50ms tab operations, 60 FPS animations
- 🔧 **Platform-Aware**: Automatic detection and graceful degradation
- ♿ **Accessible**: Full keyboard navigation and screen reader support

## Quick Start

### Installation

```bash
pip install chrome-tabbed-window
```

### Basic Usage

```python
from chrome_tabbed_window import ChromeTabbedWindow
from PySide6.QtWidgets import QApplication, QTextEdit

app = QApplication([])

# Create as top-level window (frameless with chrome)
window = ChromeTabbedWindow()

# Add tabs (same as QTabWidget)
window.addTab(QTextEdit("Content 1"), "Tab 1")
window.addTab(QTextEdit("Content 2"), "Tab 2")

# Connect signals (same as QTabWidget)
window.currentChanged.connect(lambda i: print(f"Tab {i} selected"))
window.tabCloseRequested.connect(lambda i: window.removeTab(i))

window.show()
app.exec()
```

### Embedded Mode

```python
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

main_window = QMainWindow()
central = QWidget()
layout = QVBoxLayout(central)

# Use as embedded widget (no window controls)
tabs = ChromeTabbedWindow(parent=central)
tabs.addTab(QTextEdit("Editor 1"), "File 1")
tabs.addTab(QTextEdit("Editor 2"), "File 2")

layout.addWidget(tabs)
main_window.setCentralWidget(central)
main_window.show()
```

## Theme System Integration

ChromeTabbedWindow integrates seamlessly with the VFWidgets theme system:

```python
from chrome_tabbed_window import ChromeTabbedWindow
from vfwidgets_theme import ThemedApplication
from vfwidgets_theme.widgets import add_theme_menu

# Create themed application
app = ThemedApplication(sys.argv)
app.set_theme("dark")

# ChromeTabbedWindow automatically uses theme colors!
window = ChromeTabbedWindow()
window.addTab(QTextEdit(), "Tab 1")

# Add theme switching menu
add_theme_menu(window)

window.show()
app.exec()
```

**Theme Features:**
- ✅ Automatic color adaptation from theme
- ✅ Dynamic theme switching support
- ✅ Works with all built-in themes (dark, light, default, minimal)
- ✅ Custom theme support
- ✅ Embedded mode respects parent theme
- ✅ Graceful fallback to Chrome colors when theme system unavailable

See [examples/04_themed_chrome_tabs.py](examples/04_themed_chrome_tabs.py) for complete example.

## QTabWidget API Compatibility

ChromeTabbedWindow provides 100% compatibility with QTabWidget's public API:

### Core Methods
- `addTab()`, `insertTab()`, `removeTab()`, `clear()`
- `currentIndex()`, `setCurrentIndex()`, `count()`
- `widget()`, `indexOf()`

### Tab Attributes
- `setTabText()`, `tabText()`, `setTabIcon()`, `tabIcon()`
- `setTabToolTip()`, `tabToolTip()`, `setTabEnabled()`, `isTabEnabled()`

### Signals
- `currentChanged`, `tabCloseRequested`, `tabBarClicked`, `tabBarDoubleClicked`

See [API Documentation](docs/api.md) for complete reference.

## Platform Support

| Platform | Frameless | System Move | System Resize | Notes |
|----------|-----------|-------------|---------------|-------|
| Windows 10/11 | ✅ | ✅ | ✅ | Full Aero snap support |
| macOS | ✅ | ✅ | ✅ | Native fullscreen |
| Linux X11 | ✅ | ✅ | ✅ | Full support |
| Linux Wayland | ✅ | ✅* | ✅* | Compositor-dependent |
| WSL/WSLg | ⚠️ | ⚠️ | ⚠️ | Falls back to native |

*Requires Qt 6.5+ and compositor support

## Documentation

- [Full Specification](docs/chrome-tabbed-window-SPECIFICATION.md) - Complete requirements
- [API Reference](docs/api.md) - Detailed API documentation
- [Usage Guide](docs/usage.md) - Patterns and best practices
- [Platform Notes](docs/platform-notes.md) - Platform-specific details
- [Examples](examples/) - Working example applications

## Examples

Run the interactive example launcher:

```bash
python examples/run_examples.py
```

Available examples:
1. **Basic Usage** - Simple tabbed window
2. **Frameless Chrome** - Top-level frameless window
3. **Tab Compression** - Chrome-style tab sizing
4. **Themed Chrome Tabs** - Integration with theme system
5. **Themed Embedded** - Embedded tabs with theming

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/vilosource/vfwidgets
cd vfwidgets/widgets/chrome-tabbed-window

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run benchmarks
pytest benchmarks/
```

### Project Structure

```
chrome-tabbed-window/
├── src/chrome_tabbed_window/  # Source code
│   ├── platform/              # Platform-specific code
│   ├── components/            # UI components
│   ├── api/                   # QTabWidget compatibility
│   └── utils/                 # Utilities
├── tests/                     # Test suite
├── examples/                  # Example applications
├── docs/                      # Documentation
└── benchmarks/                # Performance tests
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- Inspired by Chrome's tab interface
- Built on Qt/PySide6 framework
- Part of the VFWidgets collection

## Support

- [GitHub Issues](https://github.com/vilosource/vfwidgets/issues)
- [Discussions](https://github.com/vilosource/vfwidgets/discussions)

---

*ChromeTabbedWindow is part of the [VFWidgets](https://github.com/vilosource/vfwidgets) collection of professional Qt widgets.*