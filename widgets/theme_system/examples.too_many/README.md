# VFWidgets Theme System - Examples

This directory contains comprehensive examples demonstrating all the capabilities of the VFWidgets theme system. The examples are organized by complexity and functionality, making it easy to learn and understand the system progressively.

## 🚀 Quick Start

To get started with the VFWidgets theme system, run the main showcase:

```bash
python phase_5_living_example.py
```

This will open a comprehensive demo showing all the examples and features.

## 📚 Tutorial Series (Recommended Starting Point)

The tutorial series provides a progressive learning experience, starting from the basics and building up to complete applications. **Start here if you're new to the theme system.**

### [`tutorials/`](tutorials/)

| Tutorial | Description | Key Concepts |
|----------|-------------|--------------|
| **[01_hello_theme.py](tutorials/01_hello_theme.py)** | Your first themed application | ThemedWidget basics, theme switching |
| **[02_custom_theme.py](tutorials/02_custom_theme.py)** | Creating custom themes | Theme structure, custom colors |
| **[03_theme_switching.py](tutorials/03_theme_switching.py)** | Advanced theme management | Dynamic switching, global sync |
| **[04_vscode_import.py](tutorials/04_vscode_import.py)** | Importing VSCode themes | Theme conversion, external themes |
| **[05_custom_widget.py](tutorials/05_custom_widget.py)** | Building custom themed widgets | Custom painting, theme-aware widgets |
| **[06_complete_app.py](tutorials/06_complete_app.py)** | Complete themed application | Full app architecture, best practices |

**Learning Path**: Follow the tutorials in order (01 → 06) for the best learning experience.

## 🧱 Basic Widget Examples

Fundamental themed widgets that form the building blocks of any application.

### [`basic/`](basic/)

| Example | Description | Demonstrates |
|---------|-------------|-------------|
| **[themed_button.py](basic/themed_button.py)** | Themed buttons with states | Button theming, hover/press states |
| **[themed_label.py](basic/themed_label.py)** | Dynamic text labels | Text styling, different label types |
| **[themed_input.py](basic/themed_input.py)** | Input fields with validation | Input theming, validation states |
| **[themed_list.py](basic/themed_list.py)** | List widgets with alternating rows | List theming, selection states |
| **[themed_dialog.py](basic/themed_dialog.py)** | Modal and modeless dialogs | Dialog theming, consistent styling |

## 📐 Layout Examples

Advanced layout management with theme-aware containers and organizers.

### [`layouts/`](layouts/)

| Example | Description | Demonstrates |
|---------|-------------|-------------|
| **[grid_layout.py](layouts/grid_layout.py)** | Grid layouts with themed cells | Grid theming, cell styling |
| **[tab_widget.py](layouts/tab_widget.py)** | Tabbed interfaces | Tab styling, content theming |
| **[splitter.py](layouts/splitter.py)** | Resizable split layouts | Splitter theming, handle styling |
| **[dock_widget.py](layouts/dock_widget.py)** | Dockable panels | Dock theming, title bars |
| **[stacked_widget.py](layouts/stacked_widget.py)** | Stacked page navigation | Page transitions, navigation |

## 🎨 Theme Features

| Feature | Description | Examples |
|---------|-------------|----------|
| **Automatic Updates** | Widgets automatically update when themes change | All examples |
| **Custom Properties** | Define your own theme properties | `tutorials/02_custom_theme.py` |
| **Nested Themes** | Hierarchical theme property organization | `tutorials/02_custom_theme.py` |
| **Theme Inheritance** | Widgets inherit parent theme properties | `layouts/tab_widget.py` |
| **Performance Optimized** | Efficient theme switching with caching | All examples |
| **Memory Safe** | Automatic cleanup prevents memory leaks | All examples |

## 🏃‍♂️ Running Examples

### Prerequisites

```bash
# Ensure PySide6 is installed
pip install PySide6

# Navigate to the theme system directory
cd widgets/theme_system
```

### Running Individual Examples

```bash
# Basic widgets
python examples/basic/themed_button.py
python examples/basic/themed_label.py
python examples/basic/themed_input.py

# Layouts
python examples/layouts/grid_layout.py
python examples/layouts/tab_widget.py

# Tutorials (start here!)
python examples/tutorials/01_hello_theme.py
python examples/tutorials/02_custom_theme.py
```

### Running the Main Showcase

```bash
# Comprehensive demo of all features
python examples/phase_5_living_example.py
```

## 🎯 Example Categories

### By Complexity Level

- **🟢 Beginner**: `tutorials/01_hello_theme.py`, `basic/themed_button.py`
- **🟡 Intermediate**: `tutorials/02_custom_theme.py`, `layouts/grid_layout.py`
- **🔴 Advanced**: `tutorials/06_complete_app.py`, `layouts/dock_widget.py`

### By Use Case

- **Learning**: All files in `tutorials/`
- **UI Components**: All files in `basic/`
- **Layout Management**: All files in `layouts/`
- **Complete Applications**: `tutorials/06_complete_app.py`, `phase_5_living_example.py`

## 🔧 Customization Guide

### Creating Your Own Themes

1. **Start with the tutorial**: `tutorials/02_custom_theme.py`
2. **Define theme structure**:
   ```python
   my_theme = {
       'name': 'my_theme',
       'window': {
           'background': '#your_bg_color',
           'foreground': '#your_text_color'
       },
       'button': {
           'background': '#button_bg',
           'foreground': '#button_text',
           'hover': {'background': '#button_hover'}
       }
   }
   ```
3. **Register with application**:
   ```python
   app.register_theme('my_theme', my_theme)
   app.set_theme('my_theme')
   ```

### Creating Custom Widgets

1. **Inherit from ThemedWidget**:
   ```python
   class MyWidget(ThemedWidget):
       theme_config = {
           'bg': 'my_widget.background',
           'fg': 'my_widget.foreground'
       }
   ```
2. **Implement theme response**:
   ```python
   def on_theme_changed(self):
       # Update widget appearance
       self.update_styling()
   ```
3. **See**: `tutorials/05_custom_widget.py` for complete examples

## 📋 Best Practices

### 1. Theme Property Naming
- Use descriptive, hierarchical names: `button.hover.background`
- Group related properties: `window.*`, `button.*`, `input.*`
- Provide fallback values: `self.theme.get('color', '#000000')`

### 2. Widget Design
- Always inherit from `ThemedWidget`
- Define `theme_config` for property mapping
- Implement `on_theme_changed()` for updates
- Use semantic property names

### 3. Performance
- Use theme property caching (automatic)
- Minimize unnecessary theme updates
- Batch theme changes when possible

### 4. Accessibility
- Ensure sufficient color contrast
- Test with different themes
- Support high-contrast themes

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure you're in the correct directory
   cd widgets/theme_system
   python examples/tutorials/01_hello_theme.py
   ```

2. **Theme Not Updating**
   ```python
   # Ensure on_theme_changed() is implemented
   def on_theme_changed(self):
       self.update_styling()
   ```

3. **Property Not Found**
   ```python
   # Always provide fallback values
   color = self.theme.get('my_property', '#default_color')
   ```

### Getting Help

- 📖 **Start with tutorials**: Follow the 6-part tutorial series
- 🔍 **Check examples**: Find similar use cases in the examples
- 🎨 **Use the showcase**: Run `phase_5_living_example.py` for inspiration

## 📈 Example Statistics

| Category | Count | Lines of Code | Features Demonstrated |
|----------|-------|---------------|----------------------|
| Tutorials | 6 | ~1,800 | Complete learning path |
| Basic Widgets | 5 | ~1,500 | Core widget theming |
| Layouts | 5 | ~1,200 | Advanced layouts |
| **Total** | **16** | **~4,500** | **Complete theme system** |

## 🎉 Next Steps

After exploring these examples:

1. **Build your own themed application** using the patterns shown
2. **Create custom themes** for your brand or preferences
3. **Develop custom widgets** that integrate seamlessly
4. **Contribute back** with new examples or improvements

## 📝 Example Template

Use this template to create new themed widgets:

```python
#!/usr/bin/env python3
"""
my_widget.py - Description of your widget

Shows how to create [specific functionality].

Key Concepts:
- [Concept 1]
- [Concept 2]
- [Concept 3]
"""

import sys
from PySide6.QtWidgets import QWidget, QVBoxLayout
from vfwidgets_theme import ThemedWidget, ThemedApplication

class MyThemedWidget(ThemedWidget):
    """Your custom themed widget."""

    theme_config = {
        'bg': 'my_widget.background',
        'fg': 'my_widget.foreground',
        # Add more properties as needed
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Set up the widget UI."""
        layout = QVBoxLayout(self)
        # Add your UI elements

    def on_theme_changed(self):
        """Called when theme changes."""
        self.update_styling()

    def update_styling(self):
        """Update widget styling based on current theme."""
        bg = self.theme.get('bg', '#ffffff')
        fg = self.theme.get('fg', '#000000')

        self.setStyleSheet(f"""
        MyThemedWidget {{
            background-color: {bg};
            color: {fg};
        }}
        """)

def main():
    app = ThemedApplication(sys.argv)

    # Define your theme
    theme = {
        'name': 'my_theme',
        'my_widget': {
            'background': '#ffffff',
            'foreground': '#000000'
        }
    }

    app.register_theme('my_theme', theme)
    app.set_theme('my_theme')

    widget = MyThemedWidget()
    widget.show()

    return app.exec()

if __name__ == '__main__':
    sys.exit(main())
```

---

**Happy theming!** 🎨✨

*The VFWidgets theme system makes it easy to create beautiful, consistent, and accessible user interfaces. Start with the tutorials and work your way up to building complete themed applications.*