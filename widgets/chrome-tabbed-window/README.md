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

> ⚠️ **Theme Token Requirements**: For proper Chrome-style tab appearance, use themes with VS Code tab tokens:
> - ✅ **Recommended**: `"Dark Default"` or `"Light Default"` (full VS Code tab styling)
> - ⚠️ **Generic**: `"default"` or `"dark"` (fallback to generic colors)
>
> See [Theme Selection Guide](#theme-selection-guide) below for details.

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

## Theme Selection Guide

### Choosing the Right Theme

ChromeTabbedWindow looks best with themes that include **VS Code tab color tokens**. Different themes provide different levels of styling:

| Theme | Tab Tokens | Tab Appearance | Best For |
|-------|-----------|----------------|----------|
| **Dark Default** | ✅ Full VS Code | Chrome-like tabs with proper active/inactive/hover states | VS Code-style dark IDEs |
| **Light Default** | ✅ Full VS Code | Chrome-like tabs with proper active/inactive/hover states | VS Code-style light IDEs |
| default | ⚠️ Fallback only | Generic styled tabs using `colors.*` tokens | Simple applications |
| dark | ⚠️ Fallback only | Generic styled tabs using `colors.*` tokens | Simple dark applications |
| minimal | ⚠️ Fallback only | Generic styled tabs using `colors.*` tokens | Minimal UI applications |

### Required Tab Tokens

For optimal Chrome-style tab appearance, your theme should include these VS Code tokens:

**Essential tokens:**
- `tab.activeBackground` - Background color of the active tab
- `tab.inactiveBackground` - Background color of inactive tabs
- `tab.activeForeground` - Text color of the active tab
- `tab.inactiveForeground` - Text color of inactive tabs

**Recommended tokens:**
- `tab.hoverBackground` - Background color when hovering over tabs
- `tab.hoverForeground` - Text color when hovering over tabs
- `tab.border` - Border color between tabs
- `tab.activeBorder` - Bottom border of active tab
- `editorGroupHeader.tabsBackground` - Tab bar background

**Without these tokens**, ChromeTabbedWindow falls back to generic `colors.*` tokens (primary, hover, foreground), which results in less refined tab styling.

### Quick Fix for Generic-Looking Tabs

If your tabs look unstyled or generic, explicitly set a theme with VS Code tab tokens:

```python
from vfwidgets_theme.core.manager import ThemeManager

# Get theme manager instance
theme_manager = ThemeManager.get_instance()

# Set a theme with full tab token support
theme_manager.set_theme("Dark Default")   # For dark themes
# OR
theme_manager.set_theme("Light Default")  # For light themes
```

### Example: Proper Theme Setup

```python
from chrome_tabbed_window import ChromeTabbedWindow
from vfwidgets_theme import ThemedApplication

app = ThemedApplication(sys.argv)

# ✅ RECOMMENDED: Use theme with VS Code tab tokens
app.set_theme("Dark Default")  # Full Chrome-style tab appearance

# ⚠️ WORKS BUT GENERIC: Uses fallback colors
# app.set_theme("dark")  # Generic tab styling

window = ChromeTabbedWindow()
window.addTab(QTextEdit(), "Tab 1")
window.show()
```

### Custom Themes

To create custom themes with proper tab styling, include all VS Code tab tokens:

```json
{
  "name": "my-custom-theme",
  "version": "1.0.0",
  "colors": {
    "tab.activeBackground": "#1e1e1e",
    "tab.inactiveBackground": "#2d2d30",
    "tab.activeForeground": "#ffffff",
    "tab.inactiveForeground": "#969696",
    "tab.hoverBackground": "#2e2e32",
    "tab.hoverForeground": "#ffffff",
    "tab.border": "#252526",
    "tab.activeBorder": "#0066cc",
    "editorGroupHeader.tabsBackground": "#252526"
  }
}
```

See [Theme Integration Guide](docs/theme-integration-GUIDE.md) for complete details.

## Customizing New Tab Behavior

ChromeTabbedWindow includes a built-in "+" button rendered on the tab bar (not a QWidget). By default, clicking it creates a placeholder widget with "New Tab" text.

### ❌ Wrong Approach

**Do NOT create a separate "+" button:**
```python
# ❌ WRONG - This button will be ignored!
class MyWindow(ChromeTabbedWindow):
    def __init__(self):
        super().__init__()

        # This creates a second button that conflicts with the built-in one
        new_tab_button = QPushButton("+")
        new_tab_button.clicked.connect(self._on_new_tab)
        self.setCornerWidget(new_tab_button, Qt.Corner.TopRightCorner)
```

### ✅ Correct Approach

**Override `_on_new_tab_requested()` instead:**
```python
# ✅ CORRECT - Override the built-in handler
class MyWindow(ChromeTabbedWindow):
    def __init__(self):
        super().__init__()
        self.add_custom_tab("Tab 1")

    def _on_new_tab_requested(self):
        """Called when the built-in + button is clicked."""
        tab_count = self.count()
        self.add_custom_tab(f"Tab {tab_count + 1}")

    def add_custom_tab(self, title: str):
        widget = MyCustomWidget()
        self.addTab(widget, title)
```

**Why this matters:**
- The "+" button is **painted on the tab bar**, not a separate QWidget
- It's positioned dynamically after the last tab
- Clicking it calls `_on_new_tab_requested()`
- The method is designed to be overridden for custom behavior

See [examples/02_frameless_chrome.py](examples/02_frameless_chrome.py) for the default behavior.

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

## Known Limitations

### Frameless Mode Features

| Feature | Status | Notes |
|---------|--------|-------|
| Window dragging | ✅ Implemented | Click and drag empty tab bar area |
| Minimize/Maximize/Close buttons | ✅ Implemented | Native-style window controls |
| Double-click to maximize | ✅ Implemented | Double-click empty tab bar area |
| System context menu | ⚠️ Platform-dependent | Right-click title bar (Windows/Linux) |
| Native window animations | ⚠️ Platform-dependent | Maximize/minimize animations vary by OS |

**Double-Click to Maximize:**
- Double-click any empty area of the tab bar to toggle maximize/restore
- Works in frameless (top-level) mode only
- Does not interfere with tab double-click events

## Troubleshooting

### My tabs look generic/unstyled

**Cause**: You're using a theme without VS Code tab tokens (e.g., `default`, `dark`, `minimal`)

**Solution**: Switch to a theme with full tab styling tokens:

```python
from vfwidgets_theme.core.manager import ThemeManager

theme_manager = ThemeManager.get_instance()
theme_manager.set_theme("Dark Default")   # For dark theme
# OR
theme_manager.set_theme("Light Default")  # For light theme
```

See [Theme Selection Guide](#theme-selection-guide) for details.

### My tabs don't match VS Code appearance

**Cause**: Theme doesn't have all `tab.*` tokens defined, or is using generic token fallbacks

**Solution**: Use built-in `Dark Default` or `Light Default` themes, or add missing tokens to your custom theme:

```json
{
  "colors": {
    "tab.activeBackground": "#1e1e1e",
    "tab.inactiveBackground": "#2d2d30",
    "tab.activeForeground": "#ffffff",
    "tab.inactiveForeground": "#969696",
    "tab.hoverBackground": "#2e2e32",
    "tab.hoverForeground": "#ffffff",
    "tab.border": "#252526",
    "tab.activeBorder": "#0066cc"
  }
}
```

### Tabs show window controls (minimize/maximize/close) when embedded

**Cause**: ChromeTabbedWindow was created without a parent widget

**Solution**: Pass `parent` argument when creating embedded tabs:

```python
# ✅ Correct - Embedded mode (no window controls)
tabs = ChromeTabbedWindow(parent=parent_widget)

# ❌ Wrong - Frameless mode (includes window controls)
tabs = ChromeTabbedWindow()
```

### Theme changes don't update tab colors

**Cause**: ChromeTabbedWindow not inheriting from ThemedWidget (should never happen with official builds)

**Solution**: Verify you're using the official chrome-tabbed-window package:

```bash
pip install --upgrade chrome-tabbed-window
```

If problem persists, check that `vfwidgets-theme` is installed:

```bash
pip install vfwidgets-theme
```

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