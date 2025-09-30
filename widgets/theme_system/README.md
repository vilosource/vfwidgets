# VFWidgets Theme System

A comprehensive, VSCode-compatible theme management system for PySide6/Qt applications. Make any widget theme-aware with a single line change!

## Features

✨ **Zero-Configuration Theming** - Just inherit from `ThemedWidget` for automatic theming
🎨 **VSCode Theme Compatibility** - Import and use thousands of existing VSCode themes
🔄 **Dynamic Theme Switching** - Change themes at runtime without restart
🎯 **Progressive Enhancement** - From simple to advanced with minimal code
📦 **Built-in Themes** - Dark, light, and high-contrast themes included
🔧 **Theme Editor** - Visual editor for creating and customizing themes
🚀 **High Performance** - Optimized with caching and batch updates
♿ **Accessibility** - High contrast support and WCAG compliance

## Quick Start

### Installation

```bash
# Install from the monorepo
cd widgets/theme_system
pip install -e .
```

### Make Your App Themed in 30 Seconds

```python
from PySide6.QtWidgets import QApplication
from vfwidgets_theme import ThemeManager, ThemedWidget

# Create app
app = QApplication([])

# Initialize themes
tm = ThemeManager()
tm.load_builtin_theme("dark-modern")
tm.apply_to_application()

# Any widget inheriting from ThemedWidget is automatically themed!
class MyWindow(ThemedWidget):
    pass

window = MyWindow()
window.show()
app.exec()
```

## 🎯 For Widget Developers - Start Here!

### The 30-Second Integration

**Want to make your widget themeable? Just change the base class:**

```python
# Before: Regular widget
from PySide6.QtWidgets import QWidget
class MyWidget(QWidget):
    pass

# After: Themed widget (that's it!)
from vfwidgets_theme import ThemedWidget
class MyWidget(ThemedWidget):  # ✅ Done! Your widget is now themeable!
    pass
```

### What You Get Automatically (Zero Code!)

When you inherit from `ThemedWidget`:
- ✅ **Automatic theme colors** based on your widget's class name
- ✅ **Child widgets themed** - QPushButton, QTextEdit, etc. inside your widget are themed
- ✅ **Theme switching** - Updates automatically when user changes theme
- ✅ **Dark/light mode** - Works with both without any code
- ✅ **VSCode themes** - Compatible with thousands of themes

### Quick Decision: Do I Need More Code?

```
My widget has...
├─ Only standard Qt widgets? → You're DONE! No more code needed! ✅
├─ Custom colors? → Add one line: color = theme_property("widget.color")
├─ Custom painting? → Use theme_color() in your paintEvent
└─ Multiple parts? → Use ThemeMapping (5 lines of code)
```

### 📚 Widget Developer Resources
- **[🎯 Quick Reference Card](docs/quick-reference-CARD.md)** - One-page cheat sheet
- **[🔧 Integration Guide](docs/integration-GUIDE.md)** - Detailed integration patterns
- **[📖 Common Recipes](docs/integration-GUIDE.md#-common-widget-recipes)** - Copy-paste solutions

## Make Existing Widgets Themeable

### Before
```python
from PySide6.QtWidgets import QWidget

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: #1e1e1e; color: #ffffff;")
```

### After
```python
from vfwidgets_theme import ThemedWidget

class MyWidget(ThemedWidget):  # Just change the base class!
    def __init__(self):
        super().__init__()
        # Theming happens automatically!
```

## Using Theme Properties

```python
from vfwidgets_theme import ThemedWidget, theme_property

class CustomButton(ThemedWidget):
    # Declare theme properties
    background = theme_property("button.background")
    hover_bg = theme_property("button.hoverBackground")
    text_color = theme_property("button.foreground")

    def use_colors(self):
        print(f"Background: {self.background}")
        # Colors automatically update when theme changes!
```

## Import VSCode Themes

```python
from vfwidgets_theme import ThemeManager

tm = ThemeManager()

# Import any VSCode theme
tm.import_vscode_theme("path/to/monokai.json")
tm.switch_theme("Monokai")

# Your entire app now uses the VSCode theme!
```

## Dynamic Theme Switching

```python
from PySide6.QtWidgets import QComboBox
from vfwidgets_theme import ThemeManager, ThemedWidget

class ThemeSwitcher(ThemedWidget):
    def __init__(self):
        super().__init__()
        self.tm = ThemeManager.instance()

        self.combo = QComboBox()
        self.combo.addItems(self.tm.available_themes())
        self.combo.currentTextChanged.connect(self.tm.switch_theme)
        # Theme changes instantly!
```

## React to Theme Changes

```python
from vfwidgets_theme import ThemedWidget, on_theme_change

class ReactiveWidget(ThemedWidget):
    @on_theme_change
    def theme_changed(self, theme):
        print(f"Theme changed to: {theme.name}")
        # Update widget-specific elements

    @on_theme_change("type")
    def theme_type_changed(self, theme_type):
        if theme_type == "dark":
            self.load_dark_icons()
        else:
            self.load_light_icons()
```

## Create Custom Themes

```python
from vfwidgets_theme import Theme

# Create programmatically
theme = Theme(
    name="My Custom Theme",
    type="dark",
    colors={
        "window.background": "#1a1a1a",
        "window.foreground": "#e0e0e0",
        "button.background": "#4a90e2",
        "accent.primary": "#ff6b6b"
    }
)

# Or use the visual editor
from vfwidgets_theme import ThemeEditor
editor = ThemeEditor()
editor.show()
```

## Available Themes

### Built-in Themes
- **Dark Default** - Professional dark theme
- **Light Default** - Clean light theme
- **High Contrast** - Accessibility-focused theme

### Import VSCode Themes
- Any `.json` VSCode theme file
- Automatic property mapping
- Syntax highlighting support

## Documentation

📚 **Complete documentation in [`docs/`](docs/)**

- [🚀 Developer Guide](docs/developer-GUIDE.md) - Get started quickly
- [🔧 Integration Guide](docs/integration-GUIDE.md) - Make widgets themeable
- [📖 API Reference](docs/api-REFERENCE.md) - Complete API documentation
- [🏗️ Architecture](docs/architecture-DESIGN.md) - System design
- [🔄 Migration Guide](docs/migration-GUIDE.md) - Migrate existing code
- [⭐ Best Practices](docs/best-practices-GUIDE.md) - Tips and patterns

## Examples

### Minimal Example
```python
from vfwidgets_theme import ThemedWidget

class ThemedLabel(ThemedWidget):
    pass  # Automatically themed!
```

### Advanced Example
```python
from vfwidgets_theme import ThemedWidget, ThemeMapping

class ComplexWidget(ThemedWidget):
    theme_map = ThemeMapping({
        "editor.background": "QTextEdit",
        "sidebar.background": "QListWidget",
        "tabs.activeBackground": "QTabBar::tab:selected"
    })
```

## Performance

- ⚡ Lazy theme loading
- 💾 Intelligent caching
- 🎯 Selective updates
- 📦 Batch operations
- 🔍 Property inheritance

## Testing

```python
from vfwidgets_theme.testing import ThemeTestCase

class TestMyWidget(ThemeTestCase):
    def test_theming(self):
        widget = MyWidget()

        self.apply_test_theme("dark")
        assert widget.theme_type == "dark"

        self.apply_test_theme("light")
        assert widget.theme_type == "light"
```

## Contributing

We welcome contributions! See our [Contributing Guide](../../CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the monorepo
git clone https://github.com/vfwidgets/vfwidgets.git
cd vfwidgets/widgets/theme_system

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run linting
ruff check src/
mypy src/
```

## Architecture

The theme system uses a layered architecture:

```
Application Layer
    ↓
Theme Manager (singleton)
    ↓
Theme Engine (processing)
    ↓
Widget Integration (ThemedWidget)
    ↓
Your Widgets
```

## Compatibility

- **Python**: 3.9+
- **PySide6**: 6.5.0+
- **Qt**: 6.5+
- **Platforms**: Windows, macOS, Linux

## License

MIT License - See [LICENSE](LICENSE) for details.

## Support

- 📧 Email: support@vfwidgets.org
- 💬 Discord: [Join our server](https://discord.gg/vfwidgets)
- 🐛 Issues: [GitHub Issues](https://github.com/vfwidgets/theme-system/issues)

## Roadmap

- [ ] Theme marketplace integration
- [ ] AI-powered theme generation
- [ ] Animation support
- [ ] Theme inheritance chains
- [ ] Remote theme loading
- [ ] Theme version management

## Credits

Created by the VFWidgets Team with inspiration from:
- Visual Studio Code's excellent theming system
- Qt's powerful styling capabilities
- The open-source community

---

**Make your Qt applications beautiful with zero effort!** 🎨✨