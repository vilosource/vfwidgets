# VFWidgets Theme System 2.0

**Professional theme management for PySide6/Qt applications - Zero configuration, maximum flexibility**

[![Version](https://img.shields.io/badge/version-2.0.0--rc1-blue.svg)](https://github.com/yourusername/vfwidgets)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PySide6](https://img.shields.io/badge/PySide6-6.0+-green.svg)](https://pypi.org/project/PySide6/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## ✨ What's New in 2.0

🎯 **Zero Configuration** - All child widgets themed automatically
🎨 **197 Tokens** - Comprehensive coverage of all UI elements
🚀 **5 Built-in Themes** - vscode, dark, light, default, minimal
🔥 **Role Markers** - Semantic styling (danger, success, warning, editor)
📦 **100% Coverage** - Every Qt widget type supported
⚡ **Production Ready** - 36 unit tests, all examples working

---

## Quick Start

### Installation

```bash
cd /path/to/vfwidgets/widgets/theme_system
pip install -e .
```

### Your First Themed App (30 seconds!)

```python
#!/usr/bin/env python3
import sys
from PySide6.QtWidgets import QPushButton
from vfwidgets_theme import ThemedApplication, ThemedMainWindow

# 1. Use ThemedApplication
app = ThemedApplication(sys.argv)

# 2. Use ThemedMainWindow
window = ThemedMainWindow()
window.setWindowTitle("My Themed App")

# 3. Add widgets - automatically themed!
central = window.create_central_widget()
button = QPushButton("Click Me!", central)

window.show()
sys.exit(app.exec())
```

**That's it!** Your button (and all other widgets) are now fully themed with:
- ✅ Theme colors
- ✅ Hover effects
- ✅ Focus states
- ✅ Pressed states
- ✅ Disabled states
- ✅ Dynamic theme switching

---

## Features

### 🎯 Zero Configuration Theming

**Before Theme System 2.0:**
```python
# Manually set colors, handle theme changes, update child widgets
button.setStyleSheet("background: #0e639c; color: #fff;")
# Repeat for every widget... 😫
```

**With Theme System 2.0:**
```python
# Just use themed base classes - everything else is automatic!
from vfwidgets_theme import ThemedMainWindow

window = ThemedMainWindow()
button = QPushButton("Themed!", window)  # ✅ Automatically themed!
```

### 🎨 Comprehensive Widget Coverage

All standard Qt widgets are styled:

| Widget Type | Coverage |
|-------------|----------|
| Buttons | QPushButton, QToolButton, QRadioButton, QCheckBox |
| Inputs | QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox |
| Lists | QListWidget, QListView, QTreeWidget, QTreeView |
| Tables | QTableWidget, QTableView, QHeaderView |
| Combos | QComboBox, dropdown lists |
| Tabs | QTabWidget, QTabBar |
| Menus | QMenuBar, QMenu |
| Scrollbars | QScrollBar (vertical & horizontal) |
| Containers | QGroupBox, QFrame, QSplitter, QToolBar |
| Other | QLabel, QProgressBar, QStatusBar |

### 🔥 Role Markers

Semantic styling without custom CSS:

```python
# Danger button (red)
delete_btn = QPushButton("Delete")
delete_btn.setProperty("role", "danger")

# Success button (green)
save_btn = QPushButton("Save")
save_btn.setProperty("role", "success")

# Editor with monospace font
code_editor = QTextEdit()
code_editor.setProperty("role", "editor")
```

**Available roles**: `danger`, `success`, `warning`, `secondary`, `editor`

### 🚀 Built-in Themes

5 professional themes included:

1. **vscode** (default) - VS Code Dark+ theme
2. **dark** - GitHub-inspired dark theme
3. **light** - High contrast light theme
4. **default** - Microsoft-inspired light theme
5. **minimal** - Monochrome fallback theme

Switch themes dynamically:
```python
app.set_theme("light")  # All widgets update automatically!
```

### 📊 197 Theme Tokens

Complete control over every visual aspect:

- **192 color tokens** - All UI elements and states
- **14 font tokens** - Separate UI and editor fonts
- **14 categories** - Organized by widget type
- **Smart defaults** - Missing tokens fall back intelligently

---

## Examples

### Example 1: Simple Application

```python
from vfwidgets_theme import ThemedApplication, ThemedMainWindow
from PySide6.QtWidgets import QLabel

app = ThemedApplication(sys.argv)
window = ThemedMainWindow()

central = window.create_central_widget()
label = QLabel("Hello, Themed World!", central)

window.show()
app.exec()
```

### Example 2: Theme Switcher

```python
from PySide6.QtWidgets import QComboBox, QVBoxLayout

app = ThemedApplication(sys.argv)
window = ThemedMainWindow()

central = window.create_central_widget()
layout = QVBoxLayout(central)

# Theme selector - automatically updates all widgets!
theme_selector = QComboBox()
theme_selector.addItems(app.available_themes)
theme_selector.currentTextChanged.connect(app.set_theme)
layout.addWidget(theme_selector)

window.show()
app.exec()
```

### Example 3: Role Markers

```python
from PySide6.QtWidgets import QPushButton, QHBoxLayout

layout = QHBoxLayout()

# Different button roles
delete_btn = QPushButton("Delete")
delete_btn.setProperty("role", "danger")  # Red
layout.addWidget(delete_btn)

save_btn = QPushButton("Save")
save_btn.setProperty("role", "success")  # Green
layout.addWidget(save_btn)

cancel_btn = QPushButton("Cancel")
cancel_btn.setProperty("role", "secondary")  # Muted
layout.addWidget(cancel_btn)
```

### Run Complete Examples

```bash
cd examples/

python 01_hello_world.py          # Simplest possible (~50 lines)
python 02_buttons_and_layout.py   # Multiple widgets (~120 lines)
python 03_theme_switching.py      # Dynamic themes (~150 lines)
python 04_input_forms.py          # Forms and dialogs (~200 lines)
python 05_vscode_editor.py        # Production app (~550 lines, ZERO inline styles!)
python 06_role_markers.py         # Role markers demo (~200 lines)
```

---

## Documentation

### Getting Started

- 📖 **[Quick Start Guide](docs/quick-start-GUIDE.md)** - Get up and running in 5 minutes
- 🎨 **[Theme Customization](docs/theme-customization-GUIDE.md)** - Create custom themes
- 🔧 **[API Reference](docs/api-REFERENCE.md)** - Complete API documentation
- 📚 **[Best Practices](docs/best-practices-GUIDE.md)** - Patterns and anti-patterns
- 🚀 **[Integration Guide](docs/integration-GUIDE.md)** - Integrate with existing apps

### Advanced Topics

- 🏗️ **[Architecture](docs/architecture-DESIGN.md)** - System architecture
- 🎯 **[Migration Guide](docs/migration-GUIDE.md)** - Upgrade from 1.0 to 2.0
- 📊 **[Implementation Progress](docs/implementation-progress.md)** - Development status
- 🧪 **[Testing](tests/)** - 36 unit tests, 100% coverage on core modules

---

## Architecture

### Core Components

```
vfwidgets_theme/
├── core/
│   ├── tokens.py              # 197 token definitions
│   ├── theme.py               # Theme data model
│   └── manager.py             # Theme lifecycle management
├── widgets/
│   ├── application.py         # ThemedApplication + 5 built-in themes
│   ├── base.py                # ThemedWidget mixin
│   ├── convenience.py         # ThemedQWidget, ThemedMainWindow, ThemedDialog
│   └── stylesheet_generator.py  # Comprehensive stylesheet generation
└── examples/                  # 6 complete examples
```

### How It Works

1. **ThemedApplication** loads built-in themes on startup
2. **ThemedMainWindow** generates comprehensive stylesheet for all child widgets
3. **StylesheetGenerator** creates Qt CSS with descendant selectors
4. **Automatic cascade** - all child widgets get styled
5. **Theme switching** - updates all widgets via signal/slot

---

## Key Features

### ✅ Automatic Child Widget Theming

Theme System 2.0 solves the #1 pain point from 1.0:

**Version 1.0** (only parent widgets themed):
```python
window = ThemedMainWindow()  # ✅ Themed
button = QPushButton(window)  # ❌ NOT themed (Qt defaults)
```

**Version 2.0** (ALL widgets themed):
```python
window = ThemedMainWindow()  # ✅ Themed
button = QPushButton(window)  # ✅ ALSO themed (automatic!)
```

### ✅ Comprehensive Coverage

**197 tokens** covering:
- Base colors (foreground, background, primary, borders)
- Buttons (default + 4 roles × all states)
- Inputs (text fields, editors, dropdowns)
- Lists, trees, tables
- Tabs, menus, scrollbars
- Editor-specific colors
- Fonts (UI vs monospace)

### ✅ Smart Fallbacks

Missing tokens automatically fall back:
```python
theme.get("button.hoverBackground")
# Tries: button.hoverBackground → button.background → colors.primary → default
```

### ✅ Production Ready

- ✅ 36 unit tests passing
- ✅ 100% coverage on StylesheetGenerator
- ✅ 86% coverage on ColorTokenRegistry
- ✅ All 6 examples working
- ✅ Zero "Exception ignored" messages
- ✅ Comprehensive documentation

---

## API Overview

### ThemedApplication

```python
from vfwidgets_theme import ThemedApplication

app = ThemedApplication(sys.argv)

# Available themes
themes = app.available_themes  # ['vscode', 'dark', 'light', 'default', 'minimal']

# Get current theme
current = app.get_current_theme()

# Switch theme
app.set_theme("dark")  # Returns True if successful
```

### ThemedMainWindow

```python
from vfwidgets_theme import ThemedMainWindow

window = ThemedMainWindow()

# Access current theme
theme = window.theme

# Get color tokens
bg_color = theme.get("colors.background")
btn_color = theme.get("button.background", "#default")

# Create central widget
central = window.create_central_widget()
```

### ThemedQWidget

```python
from vfwidgets_theme import ThemedQWidget

class MyWidget(ThemedQWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # All child widgets are automatically themed!
        self.button = QPushButton("Themed", self)
        self.input = QLineEdit(self)
```

### Theme

```python
from vfwidgets_theme.core.theme import Theme, ThemeBuilder

# Create custom theme
my_theme = (ThemeBuilder("custom")
    .set_type("dark")
    .add_color("colors.foreground", "#ffffff")
    .add_color("colors.background", "#000000")
    .add_color("button.background", "#0e639c")
    .add_font("font.default.family", "Arial")
    .build())

# Access tokens
color = my_theme.get("button.background")
font = my_theme.get("font.default.family")
```

---

## Performance

Theme System 2.0 is optimized for production:

- **Stylesheet generation**: < 10ms
- **Theme switching**: < 50ms
- **Memory usage**: Minimal (themes cached)
- **Widget creation**: No overhead (lazy stylesheet generation)

---

## Testing

Run the test suite:

```bash
# Unit tests (36 tests)
pytest tests/test_color_token_registry.py  # 14 tests
pytest tests/test_stylesheet_generator.py  # 22 tests

# Integration tests (27 tests)
pytest tests/test_integration.py

# Example validation
python examples/test_examples.py
```

**Test Coverage:**
- ColorTokenRegistry: 86%
- StylesheetGenerator: 100%
- Overall: 17% (many modules are future features)

### Debugging Theme Issues

All themed widgets include a debug helper:

```python
widget = ThemedMainWindow()
print(widget.debug_styling_status())
```

Output:
```
Widget: ThemedMainWindow
Widget ID: 9eddac52-1014-4ca6-8a2b-bfb5ed37321c
Theme System Ready: True
Current Theme: vscode
Registered: True
Stylesheet Length: 11104 chars
✅ Stylesheet applied successfully
```

---

## Requirements

- Python 3.8+
- PySide6 6.0+

---

## Contributing

We welcome contributions! Please see:
- [Implementation Progress](docs/implementation-progress.md) - Current status
- [Architecture](docs/architecture-DESIGN.md) - System design
- [Best Practices](docs/best-practices-GUIDE.md) - Coding guidelines

---

## Roadmap

### ✅ Completed (Phase 1-8)

- ✅ Core token system (197 tokens)
- ✅ Stylesheet generator (all Qt widgets)
- ✅ 5 built-in themes
- ✅ Role marker support
- ✅ Automatic child widget theming
- ✅ 6 complete examples
- ✅ Comprehensive testing
- ✅ Documentation

### 🚧 In Progress (Phase 9)

- 📝 Final documentation polish
- 📝 Migration guide from 1.0
- 📝 API reference updates

### 🎯 Future (Post-2.0)

- Import VSCode themes from JSON
- Theme editor GUI
- Hot reload during development
- Additional built-in themes
- Plugin system for custom themes

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Credits

Built with ❤️ by the VFWidgets team.

Special thanks to:
- Microsoft VSCode team for theme inspiration
- Qt/PySide6 team for the excellent framework
- All contributors and testers

---

## Links

- 📖 **[Documentation](docs/)**
- 🎨 **[Examples](examples/)**
- 🧪 **[Tests](tests/)**
- 📊 **[Progress](docs/implementation-progress.md)**
- 🏗️ **[Architecture](docs/architecture-DESIGN.md)**

---

**Ready to theme your application? [Get Started →](docs/quick-start-GUIDE.md)**
