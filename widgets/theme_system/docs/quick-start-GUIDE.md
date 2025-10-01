# VFWidgets Theme System 2.0 - Quick Start Guide

**Get your PySide6 application fully themed in under 5 minutes!**

---

## Table of Contents

1. [Installation](#installation)
2. [Your First Themed Application](#your-first-themed-application)
3. [Understanding What Just Happened](#understanding-what-just-happened)
4. [Adding More Widgets](#adding-more-widgets)
5. [Switching Themes](#switching-themes)
6. [Using Role Markers](#using-role-markers)
7. [Next Steps](#next-steps)

---

## Installation

```bash
cd /path/to/vfwidgets/widgets/theme_system
pip install -e .
```

---

## Your First Themed Application

**Create a file called `hello_themed.py`:**

```python
#!/usr/bin/env python3
import sys
from PySide6.QtWidgets import QPushButton, QVBoxLayout
from vfwidgets_theme import ThemedApplication, ThemedMainWindow, ThemedQWidget

# 1. Use ThemedApplication instead of QApplication
app = ThemedApplication(sys.argv)

# 2. Use ThemedMainWindow instead of QMainWindow
window = ThemedMainWindow()
window.setWindowTitle("My First Themed App")

# 3. Create central widget
central = ThemedQWidget()
window.setCentralWidget(central)
layout = QVBoxLayout(central)

# 4. Add a button - it's automatically themed!
button = QPushButton("Click Me!", central)
button.clicked.connect(lambda: print("Button clicked!"))
layout.addWidget(button)

window.show()
sys.exit(app.exec())
```

**Run it:**
```bash
python hello_themed.py
```

**You just created a fully themed application!** ✨

---

## Understanding What Just Happened

### 1. ThemedApplication

```python
app = ThemedApplication(sys.argv)
```

- Replaces `QApplication`
- Loads and manages themes
- Default theme: **vscode** (VS Code Dark+)
- Coordinates theme changes across all widgets

### 2. ThemedMainWindow

```python
window = ThemedMainWindow()
```

- Replaces `QMainWindow`
- Automatically applies theme stylesheet
- All child widgets (buttons, inputs, etc.) get themed
- Updates when theme changes

### 3. Automatic Child Widget Theming

```python
button = QPushButton("Click Me!", central)
```

- **No special code needed!**
- Button automatically gets:
  - Theme colors (background, foreground, borders)
  - Hover effects
  - Focus states
  - Pressed states
  - Disabled states

**This is the magic of Theme System 2.0**: All standard Qt widgets inside themed parents get comprehensive styling automatically!

---

## Adding More Widgets

Let's expand our application:

```python
#!/usr/bin/env python3
import sys
from PySide6.QtWidgets import (
    QPushButton, QLabel, QLineEdit, QVBoxLayout
)
from vfwidgets_theme import ThemedApplication, ThemedMainWindow, ThemedQWidget

app = ThemedApplication(sys.argv)

window = ThemedMainWindow()
window.setWindowTitle("More Widgets")
window.setMinimumSize(400, 300)

central = ThemedQWidget()
window.setCentralWidget(central)
layout = QVBoxLayout(central)

# Label - automatically themed
label = QLabel("Enter your name:")
layout.addWidget(label)

# Input field - automatically themed
name_input = QLineEdit()
name_input.setPlaceholderText("Type here...")
layout.addWidget(name_input)

# Button - automatically themed
submit_btn = QPushButton("Submit")
submit_btn.clicked.connect(
    lambda: label.setText(f"Hello, {name_input.text()}!")
)
layout.addWidget(submit_btn)

window.show()
sys.exit(app.exec())
```

**All widgets are themed!** No inline styles, no custom CSS, zero configuration.

---

## Switching Themes

Theme System 2.0 comes with 5 built-in themes:

### Available Themes

1. **vscode** (default) - VS Code Dark+ theme
2. **dark** - GitHub-inspired dark theme
3. **light** - High contrast light theme
4. **default** - Microsoft-inspired light theme
5. **minimal** - Monochrome fallback theme

### Switch Theme at Startup

```python
app = ThemedApplication(sys.argv)

# Switch to light theme
app.set_theme("light")

window = ThemedMainWindow()
# ...
```

### Switch Theme Dynamically

```python
from PySide6.QtWidgets import QComboBox

# Create theme selector
theme_selector = QComboBox()
theme_selector.addItems(app.available_themes)
theme_selector.setCurrentText(app.get_current_theme().name)

# Connect to theme switching
theme_selector.currentTextChanged.connect(app.set_theme)

layout.addWidget(theme_selector)
```

**All widgets automatically update when theme changes!**

### Complete Theme Switching Example

```python
#!/usr/bin/env python3
import sys
from PySide6.QtWidgets import (
    QPushButton, QLabel, QComboBox, QVBoxLayout
)
from vfwidgets_theme import ThemedApplication, ThemedMainWindow, ThemedQWidget

app = ThemedApplication(sys.argv)

window = ThemedMainWindow()
window.setWindowTitle("Theme Switcher")
window.setMinimumSize(400, 200)

central = ThemedQWidget()
window.setCentralWidget(central)
layout = QVBoxLayout(central)

# Theme selector
label = QLabel("Choose a theme:")
layout.addWidget(label)

theme_combo = QComboBox()
theme_combo.addItems(app.available_themes)
theme_combo.setCurrentText(app.get_current_theme().name)
theme_combo.currentTextChanged.connect(app.set_theme)
layout.addWidget(theme_combo)

# Sample widgets to see theme changes
button = QPushButton("Sample Button")
layout.addWidget(button)

window.show()
sys.exit(app.exec())
```

---

## Using Role Markers

Role markers provide **semantic styling** without custom CSS:

### Available Roles

- **danger** - Red styling for destructive actions
- **success** - Green styling for positive actions
- **warning** - Yellow styling for warnings
- **secondary** - Muted styling for secondary actions
- **editor** - Monospace font for code/text editors

### Button Roles Example

```python
from PySide6.QtWidgets import QPushButton, QHBoxLayout

layout = QHBoxLayout()

# Default button (no role)
default_btn = QPushButton("Default")
layout.addWidget(default_btn)

# Danger button (red)
delete_btn = QPushButton("Delete")
delete_btn.setProperty("role", "danger")
layout.addWidget(delete_btn)

# Success button (green)
save_btn = QPushButton("Save")
save_btn.setProperty("role", "success")
layout.addWidget(save_btn)

# Warning button (yellow)
warning_btn = QPushButton("Proceed with Caution")
warning_btn.setProperty("role", "warning")
layout.addWidget(warning_btn)

# Secondary button (muted)
cancel_btn = QPushButton("Cancel")
cancel_btn.setProperty("role", "secondary")
layout.addWidget(cancel_btn)
```

### Editor Role Example

```python
from PySide6.QtWidgets import QTextEdit

# Regular text edit (UI font)
regular_edit = QTextEdit()
regular_edit.setPlainText("This uses the default UI font")

# Code editor (monospace font)
code_editor = QTextEdit()
code_editor.setProperty("role", "editor")
code_editor.setPlainText("def hello():\n    print('Hello!')")
```

**The editor role automatically applies:**
- Monospace font (Courier New, 11pt)
- Editor-specific colors
- Proper selection colors

---

## Next Steps

### 1. Run the Examples

```bash
cd examples/

# Basic examples
python 01_hello_world.py          # Simplest possible
python 02_buttons_and_layout.py   # Multiple widgets
python 03_theme_switching.py      # Dynamic themes

# Advanced examples
python 04_input_forms.py          # Forms and dialogs
python 05_vscode_editor.py        # Production-quality app
python 06_role_markers.py         # Role marker demo
```

### 2. Read the Documentation

- **[API Reference](api-REFERENCE.md)** - Complete API documentation
- **[Theme Customization](theme-customization-GUIDE.md)** - Create custom themes
- **[Architecture](ARCHITECTURE.md)** - System internals for contributors
- **[Roadmap](ROADMAP.md)** - Design rationale and future plans

### 3. Explore Advanced Features

**Custom Themed Widgets:**
```python
from vfwidgets_theme import ThemedQWidget

class MyCustomWidget(ThemedQWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Your widgets are automatically themed!
        self.button = QPushButton("Themed!", self)
```

**Access Theme Values:**
```python
window = ThemedMainWindow()

# Get current theme
theme = window.theme

# Access color tokens
bg_color = theme.get("colors.background")
btn_color = theme.get("button.background")

# Use in custom code
custom_color = theme.get("button.hoverBackground", "#default")
```

**Custom Styling (when needed):**
```python
class MyWidget(ThemedQWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Widget already has base theme applied
        # Add custom styling on top
        self.custom_label = QLabel("Custom", self)
        self.custom_label.setStyleSheet(
            f"color: {self.theme.get('colors.primary')};"
        )
```

---

## Common Patterns

### Pattern 1: Main Application Window

```python
from vfwidgets_theme import ThemedApplication, ThemedMainWindow, ThemedQWidget
from PySide6.QtWidgets import QVBoxLayout

app = ThemedApplication(sys.argv)
window = ThemedMainWindow()

# Create your UI
central = ThemedQWidget()
window.setCentralWidget(central)
layout = QVBoxLayout(central)
# Add widgets to layout...

window.show()
sys.exit(app.exec())
```

### Pattern 2: Custom Widget

```python
from vfwidgets_theme import ThemedQWidget
from PySide6.QtWidgets import QPushButton, QVBoxLayout

class MyWidget(ThemedQWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # All these widgets are automatically themed!
        button = QPushButton("Click me", self)
        layout.addWidget(button)
```

### Pattern 3: Dialog

```python
from vfwidgets_theme import ThemedDialog

class MyDialog(ThemedDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("My Dialog")

        # Widgets inside dialog are automatically themed
        # ...
```

---

## Key Concepts

### 1. Zero Configuration

**You don't need to:**
- Write custom stylesheets
- Set colors manually
- Handle theme changes
- Update child widgets

**The system handles it all automatically!**

### 2. Automatic Cascade

When you use `ThemedMainWindow` or `ThemedQWidget`, **all child widgets** get themed:
- QPushButton
- QLineEdit, QTextEdit
- QLabel
- QComboBox
- QListWidget, QTreeWidget
- QTableWidget
- QTabWidget
- QMenuBar, QMenu
- QScrollBar
- And more!

### 3. Theme Propagation

When you call `app.set_theme("dark")`, **all themed widgets** in your application automatically update. No manual refresh needed!

### 4. Smart Defaults

Every theme includes **197 tokens** covering:
- 192 color tokens
- 14 font tokens
- All UI elements
- All widget states (hover, pressed, disabled, focus)

**If a theme is missing a token, it falls back to sensible defaults.**

---

## Troubleshooting

### Q: My widget isn't themed!

**A:** Make sure you're using:
- `ThemedApplication` instead of `QApplication`
- `ThemedMainWindow`, `ThemedQWidget`, or `ThemedDialog`
- Standard Qt widgets (QPushButton, QLineEdit, etc.)

### Q: Can I use custom stylesheets?

**A:** Yes! Themed widgets apply base styling first, then your custom styles:

```python
widget = ThemedQWidget()
# Base theme applied automatically

# Add custom styles on top
widget.setStyleSheet("border: 2px solid red;")
```

### Q: How do I access theme colors?

**A:**
```python
window = ThemedMainWindow()
color = window.theme.get("button.background")
```

### Q: My custom widget isn't updating on theme change

**A:** Make sure to inherit from a themed base class:
```python
# Wrong
class MyWidget(QWidget):
    pass

# Right
class MyWidget(ThemedQWidget):
    pass
```

---

## Summary

🎯 **3 Steps to Themed Application:**
1. Use `ThemedApplication` instead of `QApplication`
2. Use `ThemedMainWindow` instead of `QMainWindow`
3. That's it! All widgets are now themed!

🎨 **5 Built-in Themes:**
- vscode (default)
- dark
- light
- default
- minimal

🚀 **Zero Configuration:**
- No stylesheets to write
- No colors to manage
- Automatic theme switching
- All child widgets themed

---

**You're ready to build beautifully themed applications!** 🎉

Check out the [examples](../examples/) directory for complete working applications.
