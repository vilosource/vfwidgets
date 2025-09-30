# Developer Getting Started Guide - VFWidgets Theme System

## Installation

```bash
# Install from the monorepo
cd widgets/theme_system
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

## Quick Start - 30 Seconds to Themed App

### The Complete App

```python
from vfwidgets_theme import ThemedApplication, ThemedWidget
from PySide6.QtWidgets import QVBoxLayout, QPushButton, QTextEdit
import sys

# Create themed application
app = ThemedApplication(sys.argv)
app.set_theme("dark-modern")  # Built-in theme

# Create your widget - just inherit ThemedWidget!
class MyWindow(ThemedWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QTextEdit())     # Automatically themed!
        layout.addWidget(QPushButton("Click Me"))  # Also themed!

# Show and run
window = MyWindow()
window.show()
app.exec()
```

**That's it!** You have a fully themed application with:
- ✅ Automatic theming of all widgets
- ✅ Clean architecture underneath
- ✅ Memory safety and thread safety
- ✅ Theme switching support
- ✅ VSCode theme compatibility

## The Two Classes You Need

### 1. `ThemedApplication`

Your application wrapper that handles all theme initialization:

```python
from vfwidgets_theme import ThemedApplication
import sys

app = ThemedApplication(sys.argv)
app.set_theme("dark-modern")  # or "light-default" or custom theme
```

### 2. `ThemedWidget`

Your widget base class that makes everything work automatically:

```python
from vfwidgets_theme import ThemedWidget

class YourWidget(ThemedWidget):
    pass  # That's all! Fully themed with clean architecture
```

## Common Use Cases

### Basic Window

```python
from vfwidgets_theme import ThemedApplication, ThemedWidget
import sys

class MainWindow(ThemedWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")
        # Add your UI here

app = ThemedApplication(sys.argv)
app.set_theme("dark-modern")

window = MainWindow()
window.show()
app.exec()
```

### Widget with Custom Colors

```python
class CustomButton(ThemedWidget):
    # Declare what theme properties you need
    theme_config = {
        'bg': 'button.background',
        'hover': 'button.hoverBackground'
    }

    def paintEvent(self, event):
        # Use your theme colors
        color = self.theme.bg  # Automatic property access!
```

### Reacting to Theme Changes

```python
class DynamicWidget(ThemedWidget):
    def on_theme_changed(self):
        """Called automatically when theme changes"""
        print(f"Theme is now: {'dark' if self.is_dark_theme else 'light'}")
        self.update_my_colors()
```

### Complete Application Example

```python
from vfwidgets_theme import ThemedApplication, ThemedWidget
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton,
                               QTextEdit, QListWidget, QComboBox)
import sys

class MyEditor(ThemedWidget):
    """A complete editor application - no theme code needed!"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Themed Editor")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.addWidget(QPushButton("New"))
        toolbar.addWidget(QPushButton("Open"))
        toolbar.addWidget(QPushButton("Save"))

        # Theme switcher
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark-modern", "light-default"])
        self.theme_combo.currentTextChanged.connect(app.set_theme)
        toolbar.addWidget(self.theme_combo)

        layout.addLayout(toolbar)

        # Main content
        content = QHBoxLayout()
        content.addWidget(QListWidget(), 1)  # File browser
        content.addWidget(QTextEdit(), 3)    # Editor

        layout.addLayout(content)

# Run the app
app = ThemedApplication(sys.argv)
app.set_theme("dark-modern")

editor = MyEditor()
editor.show()

app.exec()
```

## Working with Themes

### Available Built-in Themes

```python
app.set_theme("dark-modern")    # Modern dark theme
app.set_theme("light-default")  # Clean light theme
app.set_theme("high-contrast")  # Accessibility theme
```

### Loading Custom Themes

```python
# From file
app.load_theme_file("my-theme.json")
app.set_theme("My Theme")

# From VSCode theme
app.import_vscode_theme("monokai.json")
app.set_theme("Monokai")
```

### Creating Custom Themes

Create a JSON file:

```json
{
  "name": "My Custom Theme",
  "type": "dark",
  "colors": {
    "window.background": "#1e1e1e",
    "window.foreground": "#d4d4d4",
    "button.background": "#0e639c",
    "button.hoverBackground": "#1177bb",
    "editor.background": "#1e1e1e",
    "editor.foreground": "#d4d4d4"
  }
}
```

### Theme Switching

```python
class AppWithThemeSwitcher(ThemedWidget):
    def __init__(self):
        super().__init__()

        # Add theme switcher button
        self.dark_button = QPushButton("Dark Mode")
        self.dark_button.clicked.connect(lambda: app.set_theme("dark-modern"))

        self.light_button = QPushButton("Light Mode")
        self.light_button.clicked.connect(lambda: app.set_theme("light-default"))
```

## Advanced Features

### Custom Theme Properties

```python
class AdvancedWidget(ThemedWidget):
    theme_config = {
        'primary': 'accent.primary',
        'secondary': 'accent.secondary',
        'danger': 'status.danger',
        'success': 'status.success'
    }

    def show_status(self, is_error):
        color = self.theme.danger if is_error else self.theme.success
        self.status_label.setStyleSheet(f"color: {color}")
```

### System Theme Detection

```python
app = ThemedApplication(sys.argv, config={
    'auto_detect_system': True  # Follow system dark/light mode
})

# Or manually:
from vfwidgets_theme.utils import detect_system_theme
theme = "dark-modern" if detect_system_theme() == "dark" else "light-default"
app.set_theme(theme)
```

### Theme Persistence

```python
# App remembers last theme
app = ThemedApplication(sys.argv, config={
    'persistent': True  # Saves theme choice
})

# Or manually save preference
app.save_theme_preference("dark-modern")

# Load on next startup
saved_theme = app.load_theme_preference()
if saved_theme:
    app.set_theme(saved_theme)
```

## VSCode Theme Support

### Using VSCode Themes

```python
# Import any VSCode theme
app.import_vscode_theme("path/to/vscode-theme.json")

# The theme is now available
app.set_theme("Theme Name from JSON")
```

### Where to Find VSCode Themes

1. From VSCode extensions: `~/.vscode/extensions/*/themes/*.json`
2. From theme repositories on GitHub
3. From the VSCode marketplace

## Testing Your Themed Widgets

```python
from vfwidgets_theme.testing import ThemedTestCase

class TestMyWidget(ThemedTestCase):
    def test_theming(self):
        widget = MyWidget()

        # Apply test theme
        self.apply_test_theme("dark")

        # Widget automatically updates
        self.assertTrue(widget.is_dark_theme)

        # Switch theme
        self.apply_test_theme("light")
        self.assertFalse(widget.is_dark_theme)
```

## Performance & Best Practices

### Do's ✅

```python
# DO: Use ThemedWidget as base class
class Good(ThemedWidget):
    pass

# DO: Use theme_config for properties
class Good(ThemedWidget):
    theme_config = {'bg': 'window.background'}

# DO: Override on_theme_changed for updates
class Good(ThemedWidget):
    def on_theme_changed(self):
        self.update()
```

### Don'ts ❌

```python
# DON'T: Access ThemeManager directly
class Bad(QWidget):
    def __init__(self):
        self.tm = ThemeManager.instance()  # ❌ Don't do this!

# DON'T: Hardcode colors
class Bad(ThemedWidget):
    def __init__(self):
        self.setStyleSheet("background: #ffffff")  # ❌ Use theme colors!

# DON'T: Forget to call super().__init__()
class Bad(ThemedWidget):
    def __init__(self):
        # super().__init__()  # ❌ Forgetting this breaks theming!
        pass
```

## Configuration Options

### Application Configuration

```python
app = ThemedApplication(sys.argv, config={
    'auto_detect_system': True,      # Follow system theme
    'fallback_theme': 'light-default',  # If theme fails to load
    'validate_themes': True,         # Validate theme files
    'cache_themes': True,            # Better performance
    'theme_directory': '~/.themes'   # Where to look for themes
})
```

### Widget Configuration

```python
class ConfiguredWidget(ThemedWidget):
    theme_config = {
        # Property mappings
        'bg': 'editor.background',

        # Widget options
        '_options': {
            'cache_properties': True,  # Cache lookups
            'auto_refresh': True       # Auto-update on theme change
        }
    }
```

## Debugging

### Enable Debug Mode

```python
app = ThemedApplication(sys.argv, debug=True)
# Shows theme property resolution and performance info
```

### Check Current Theme

```python
print(f"Current theme: {app.current_theme_name}")
print(f"Theme type: {app.theme_type}")
print(f"Available themes: {app.available_themes}")
```

## Common Issues & Solutions

### Theme Not Applying?

```python
# ✅ Correct: Inherit from ThemedWidget
class MyWidget(ThemedWidget):
    pass

# ❌ Wrong: Inheriting from QWidget
class MyWidget(QWidget):  # Won't get themed!
    pass
```

### Custom Paint Not Updating?

```python
class CustomPaintWidget(ThemedWidget):
    def on_theme_changed(self):
        """Must call update() to repaint"""
        self.update()  # ✅ Triggers paintEvent
```

### Child Widgets Not Themed?

```python
# Child Qt widgets are automatically themed if parent is ThemedWidget
class ParentWidget(ThemedWidget):
    def __init__(self):
        super().__init__()  # ✅ Must call super().__init__()

        # These get themed automatically
        self.button = QPushButton("Auto-themed!", self)
        self.editor = QTextEdit(self)
```

## Migration from Old Code

### From Manual Theme Management

```python
# Old way 😢
class OldWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.apply_theme()
        theme_manager.theme_changed.connect(self.apply_theme)

    def apply_theme(self):
        theme = theme_manager.get_current_theme()
        self.setStyleSheet(f"background: {theme['background']}")

# New way 😊
class NewWidget(ThemedWidget):
    theme_config = {'bg': 'window.background'}

    def on_theme_changed(self):
        self.setStyleSheet(f"background: {self.theme.bg}")
```

### From Hardcoded Colors

```python
# Old way 😢
class OldButton(QPushButton):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: #0066cc; color: white;")

# New way 😊
class NewButton(ThemedWidget, QPushButton):
    theme_config = {
        'bg': 'button.background',
        'fg': 'button.foreground'
    }

    def on_theme_changed(self):
        self.setStyleSheet(f"""
            background: {self.theme.bg};
            color: {self.theme.fg};
        """)
```

## Quick Reference

```python
# 1. Create app
from vfwidgets_theme import ThemedApplication, ThemedWidget
app = ThemedApplication(sys.argv)
app.set_theme("dark-modern")

# 2. Create widget
class MyWidget(ThemedWidget):
    # Optional: declare theme properties
    theme_config = {'bg': 'window.background'}

    # Optional: react to theme changes
    def on_theme_changed(self):
        print(f"Theme changed! Dark: {self.is_dark_theme}")

# 3. Run
widget = MyWidget()
widget.show()
app.exec()
```

## Next Steps

1. Try the [Patterns Cookbook](patterns-cookbook.md) for common widget patterns
2. See [API Reference](api-REFERENCE.md) for detailed documentation
3. Check [Example Themes](examples/) for theme creation
4. Read [Best Practices](best-practices-GUIDE.md) for optimization

---

*Remember: ThemedWidget handles all the complexity. You just build your app!*