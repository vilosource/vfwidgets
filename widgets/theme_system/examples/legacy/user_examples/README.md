# VFWidgets Theme System - User Examples

This directory contains practical examples showing how to use the VFWidgets theme system in real applications. The examples progress from simple to sophisticated, demonstrating all major features.

## Quick Start

All examples use only the public API: `ThemedWidget` and `ThemedApplication`.

```python
from vfwidgets_theme import ThemedWidget, ThemedApplication

# Create a themed application
app = ThemedApplication(sys.argv)

# Create a themed widget
widget = ThemedWidget()

# Switch themes
app.set_theme('dark')
```

## Examples Overview

### 1. [01_minimal_hello_world.py](01_minimal_hello_world.py) - Minimal Hello World
**Difficulty:** ⭐ Beginner
**Lines of Code:** ~40
**Key Concepts:** Basic themed application setup

The simplest possible themed application. Shows how to:
- Create a `ThemedApplication`
- Create a basic `ThemedWidget`
- Automatic theme application

```bash
python 01_minimal_hello_world.py
```

### 2. [02_theme_switching.py](02_theme_switching.py) - Dynamic Theme Switching
**Difficulty:** ⭐⭐ Easy
**Lines of Code:** ~120
**Key Concepts:** Runtime theme changes, theme property mapping

Interactive theme switcher demonstrating:
- Listing available themes
- Switching themes at runtime
- Responding to theme changes in widgets
- Mapping theme properties to widget styling

```bash
python 02_theme_switching.py
```

### 3. [03_custom_themed_widgets.py](03_custom_themed_widgets.py) - Custom Themed Widgets
**Difficulty:** ⭐⭐⭐ Intermediate
**Lines of Code:** ~250
**Key Concepts:** Custom widgets, painting, animations

Creating sophisticated custom widgets:
- Custom painting with theme colors
- Progress bars with animations
- Card widgets with hover effects
- Theme-aware property animations

```bash
python 03_custom_themed_widgets.py
```

### 4. [04_multi_window_application.py](04_multi_window_application.py) - Multi-Window Application
**Difficulty:** ⭐⭐⭐⭐ Advanced
**Lines of Code:** ~350
**Key Concepts:** Complex application architecture

Real application with multiple windows:
- Multiple synchronized windows
- Menu bar theming
- Dialogs and settings
- File tree and editor panels
- Status bar with theme info

```bash
python 04_multi_window_application.py
```

### 5. [05_complete_application.py](05_complete_application.py) - Complete Production Application
**Difficulty:** ⭐⭐⭐⭐⭐ Expert
**Lines of Code:** ~500
**Key Concepts:** All features combined

Production-ready application demonstrating:
- Custom theme creation and editing
- Theme persistence (save/load)
- Live theme preview
- Animated theme transitions
- Complex widget hierarchies
- Data tables and dashboards

```bash
python 05_complete_application.py
```

## Key Concepts

### ThemedWidget

Base class for all themed widgets. Inherit from it to get automatic theming:

```python
class MyWidget(ThemedWidget):
    # Map semantic names to theme properties
    theme_config = {
        'background': 'colors.background',
        'text': 'colors.foreground'
    }

    def on_theme_changed(self):
        """Called when theme changes"""
        bg = self.theme.background  # Access mapped properties
        self.setStyleSheet(f"background-color: {bg};")
```

### ThemedApplication

Manages themes for the entire application:

```python
app = ThemedApplication(sys.argv)

# Available themes
print(app.available_themes)  # ['default', 'dark', 'light', 'minimal']

# Switch theme
app.set_theme('dark')

# Get current theme
current = app.current_theme_name
theme_type = app.theme_type  # 'light' or 'dark'
```

### Theme Configuration

Map theme properties to widget attributes:

```python
theme_config = {
    'bg': 'colors.background',      # Maps self.theme.bg to colors.background
    'fg': 'colors.foreground',      # Maps self.theme.fg to colors.foreground
    'accent': 'colors.accent'       # Maps self.theme.accent to colors.accent
}
```

### Theme Properties

Access theme properties through the mapping:

```python
def on_theme_changed(self):
    # Access through mapped names
    bg_color = self.theme.bg
    fg_color = self.theme.fg

    # Or use getattr with defaults
    accent = getattr(self.theme, 'accent', '#0066cc')
```

## Running the Examples

1. **Requirements:**
   - Python 3.8+
   - PySide6
   - VFWidgets theme system installed

2. **Basic Usage:**
   ```bash
   cd examples/user_examples
   python 01_minimal_hello_world.py
   ```

3. **Testing All Examples:**
   ```bash
   python test_examples.py
   ```

## Creating Your Own Themed Application

1. **Start Simple:** Begin with example 1 and modify it
2. **Add Complexity:** Look at example 2 for theme switching
3. **Custom Widgets:** Example 3 shows how to create custom widgets
4. **Scale Up:** Examples 4 and 5 show production patterns

## Best Practices

1. **Always inherit from ThemedWidget** for automatic theming
2. **Define theme_config** to map properties
3. **Implement on_theme_changed()** to update styling
4. **Use getattr() with defaults** for safe property access
5. **Let ThemedApplication manage themes** - don't create ThemeManager directly

## Common Patterns

### Simple Widget
```python
class SimpleWidget(ThemedWidget, QLabel):
    def __init__(self):
        super().__init__()
        self.setText("Hello")
```

### Widget with Theme Config
```python
class ConfiguredWidget(ThemedWidget):
    theme_config = {
        'bg': 'colors.background',
        'fg': 'colors.foreground'
    }

    def on_theme_changed(self):
        self.update_colors()
```

### Multiple Inheritance
```python
# IMPORTANT: ThemedWidget must come FIRST in inheritance
class CustomButton(ThemedWidget, QPushButton):
    """Combine ThemedWidget with Qt widgets"""
    pass

# For QMainWindow and QDialog too:
class MyWindow(ThemedWidget, QMainWindow):  # ✓ Correct
class MyDialog(ThemedWidget, QDialog):      # ✓ Correct

# NOT: class MyWindow(QMainWindow, ThemedWidget)  # ✗ Wrong - causes RuntimeError
```

## Troubleshooting

**Theme not applying?**
- Ensure `ThemedApplication` is created before any `ThemedWidget`
- Check that `on_theme_changed()` is implemented
- Verify theme_config mapping is correct

**Property not found?**
- Check theme structure with `print(app.current_theme_name)`
- Use getattr() with defaults: `getattr(self.theme, 'prop', default)`

**Multiple inheritance issues?**
- Put `ThemedWidget` first in inheritance: `class MyWidget(ThemedWidget, QWidget)`

## Further Resources

- [Development Examples](../development_examples/) - Internal implementation examples
- [Theme System Documentation](../../docs/) - Full documentation
- [API Reference](../../src/vfwidgets_theme/) - Source code

## License

These examples are part of the VFWidgets project and follow the project license.