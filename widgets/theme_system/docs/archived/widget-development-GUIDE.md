# Widget Development Guide - Custom Themed Widgets

**When you need more than QWidget, QMainWindow, or QDialog.**

---

## Who This Guide Is For

You've been using `ThemedMainWindow` and `ThemedQWidget` successfully. Now you need to create custom widgets that inherit from:

- `QTextEdit` - For code editors or rich text
- `QFrame` - For custom panels or containers
- `QPushButton` - For specialized buttons
- `QLineEdit` - For custom input fields
- `QListWidget`, `QTreeWidget`, `QTableWidget` - For custom data views
- Any other Qt widget type

**This guide shows you how to use the advanced API: `ThemedWidget`.**

**For comprehensive theming patterns (80% simple case, 20% complex case):** See [Official Theming Guide](THEMING-GUIDE-OFFICIAL.md)

---

## Table of Contents

1. [Quick Start - Your First Custom Widget](#quick-start---your-first-custom-widget)
2. [Understanding ThemedWidget](#understanding-themedwidget)
3. [The Pattern - Inheritance Order](#the-pattern---inheritance-order)
4. [Common Use Cases](#common-use-cases)
5. [Theme Configuration](#theme-configuration)
6. [Responding to Theme Changes](#responding-to-theme-changes)
7. [Advanced Features](#advanced-features)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start - Your First Custom Widget

Let's build a custom code editor that inherits from `QTextEdit`:

```python
from vfwidgets_theme import ThemedWidget
from PySide6.QtWidgets import QTextEdit

class CodeEditor(ThemedWidget, QTextEdit):
    """A themed code editor widget.

    IMPORTANT: ThemedWidget must come FIRST in the inheritance list.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Widget is now themed! All editor colors follow the active theme
        self.setPlaceholderText("Type your code here...")
```

**That's it!** Your `CodeEditor` now:
- ✅ Automatically applies theme colors
- ✅ Updates when theme changes
- ✅ Inherits all QTextEdit functionality
- ✅ Works with any theme

### Using Your Custom Widget

```python
from vfwidgets_theme import ThemedApplication, ThemedMainWindow

app = ThemedApplication(sys.argv)
window = ThemedMainWindow()

# Use your custom widget
editor = CodeEditor()
window.setCentralWidget(editor)

window.show()
sys.exit(app.exec())
```

---

## Understanding ThemedWidget

### What You've Been Using

In the Quick Start Guide, you learned:

```python
from vfwidgets_theme import ThemedQWidget

class MyWidget(ThemedQWidget):  # Simple - one base class
    pass
```

**This worked because `ThemedQWidget` is actually:**

```python
class ThemedQWidget(ThemedWidget, QWidget):
    """Pre-combined for convenience."""
    pass
```

### The Real Pattern

`ThemedWidget` is a **mixin** that adds theming to any Qt widget:

```python
from vfwidgets_theme import ThemedWidget

class MyCustomWidget(ThemedWidget, AnyQtWidget):
    """ThemedWidget + any Qt base class = themed custom widget."""
    pass
```

**This is the full power of the theme system:**
- Works with **any** Qt widget as the base
- Not limited to QWidget, QMainWindow, QDialog
- Maximum flexibility

### Why ThemedQWidget Isn't Enough

```python
# This doesn't work:
class CodeEditor(ThemedQWidget, QTextEdit):  # ❌ Error!
    pass

# Because ThemedQWidget is already (ThemedWidget + QWidget)
# You can't combine it with QTextEdit (multiple inheritance conflict)
```

**Solution:** Use `ThemedWidget` directly:

```python
# This works:
class CodeEditor(ThemedWidget, QTextEdit):  # ✅ Correct!
    pass
```

---

## The Pattern - Inheritance Order

### The Golden Rule

**ThemedWidget MUST come FIRST in the inheritance list.**

```python
# ✅ CORRECT
class MyWidget(ThemedWidget, QTextEdit):
    pass

# ❌ WRONG
class MyWidget(QTextEdit, ThemedWidget):  # Will raise TypeError!
    pass
```

### Why Order Matters

Python's Method Resolution Order (MRO) requires `ThemedWidget` to come first so that:
1. `ThemedWidget.__init__()` runs first
2. Theme registration happens before widget initialization
3. Theme is available when Qt widget sets up

### Runtime Validation

The system validates inheritance order automatically:

```python
class BadWidget(QTextEdit, ThemedWidget):  # Wrong order
    pass

widget = BadWidget()  # TypeError with helpful message!

# TypeError: BadWidget: ThemedWidget must come BEFORE QTextEdit.
#   ❌ Wrong: class BadWidget(QTextEdit, ThemedWidget)
#   ✅ Right: class BadWidget(ThemedWidget, QTextEdit)
#
# 📖 See: docs/widget-development-GUIDE.md
```

---

## Common Use Cases

### 1. Custom Text Editor

```python
from vfwidgets_theme import ThemedWidget
from PySide6.QtWidgets import QTextEdit
from PySide6.QtGui import QFont

class CodeEditor(ThemedWidget, QTextEdit):
    """Code editor with monospace font."""

    theme_config = {
        'bg': 'editor.background',
        'fg': 'editor.foreground',
        'selection_bg': 'editor.selectionBackground',
        'selection_fg': 'editor.selectionForeground',
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        # Set monospace font
        font = QFont("Courier New", 11)
        self.setFont(font)

        # Or use editor role marker
        self.setProperty("role", "editor")
```

### 2. Custom Frame Panel

```python
from vfwidgets_theme import ThemedWidget
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel

class StatusPanel(ThemedWidget, QFrame):
    """Themed status panel with border."""

    theme_config = {
        'bg': 'panel.background',
        'fg': 'panel.foreground',
        'border': 'panel.border',
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        # Set frame style
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)

        # Add content
        layout = QVBoxLayout(self)
        self.status_label = QLabel("Status: Ready")
        layout.addWidget(self.status_label)
```

### 3. Custom Button

```python
from vfwidgets_theme import ThemedWidget
from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QIcon

class IconButton(ThemedWidget, QPushButton):
    """Button with icon and custom styling."""

    theme_config = {
        'bg': 'button.background',
        'fg': 'button.foreground',
        'hover_bg': 'button.hoverBackground',
    }

    def __init__(self, text="", icon_path=None, parent=None):
        super().__init__(parent)

        self.setText(text)

        if icon_path:
            self.setIcon(QIcon(icon_path))
```

### 4. Custom Input Field

```python
from vfwidgets_theme import ThemedWidget
from PySide6.QtWidgets import QLineEdit
from PySide6.QtCore import Signal

class ValidatedInput(ThemedWidget, QLineEdit):
    """Input field with validation."""

    validationChanged = Signal(bool)

    theme_config = {
        'bg': 'input.background',
        'fg': 'input.foreground',
        'border': 'input.border',
        'error': 'errorForeground',
    }

    def __init__(self, validator=None, parent=None):
        super().__init__(parent)

        if validator:
            self.setValidator(validator)

        self.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self, text):
        is_valid = self.hasAcceptableInput()
        self.validationChanged.emit(is_valid)
```

### 5. Custom List Widget

```python
from vfwidgets_theme import ThemedWidget
from PySide6.QtWidgets import QListWidget, QListWidgetItem

class ThemedListWidget(ThemedWidget, QListWidget):
    """List widget with custom item styling."""

    theme_config = {
        'bg': 'list.background',
        'fg': 'list.foreground',
        'selection_bg': 'list.activeSelectionBackground',
        'selection_fg': 'list.activeSelectionForeground',
    }

    def add_item(self, text, icon=None):
        """Add themed item to list."""
        item = QListWidgetItem(text)
        if icon:
            item.setIcon(icon)
        self.addItem(item)
```

---

## Theme Configuration

### Basic Configuration

Use `theme_config` to map theme tokens to semantic names:

```python
class MyWidget(ThemedWidget, QTextEdit):
    theme_config = {
        'bg': 'editor.background',          # Background color
        'fg': 'editor.foreground',          # Text color
        'selection_bg': 'editor.selectionBackground',
    }
```

### Accessing Theme Values

```python
class MyWidget(ThemedWidget, QWidget):
    theme_config = {
        'bg': 'window.background',
        'accent': 'colors.primary',
    }

    def paintEvent(self, event):
        painter = QPainter(self)

        # Access configured theme values
        bg_color = self.theme.bg
        accent_color = self.theme.accent

        painter.fillRect(self.rect(), QColor(bg_color))
```

### Available Theme Tokens

Common theme tokens (see [theme-customization-GUIDE.md](theme-customization-GUIDE.md) for complete list):

**Colors:**
- `colors.foreground`, `colors.background`
- `colors.primary`, `colors.secondary`

**Window:**
- `window.background`, `window.foreground`
- `window.border`

**Buttons:**
- `button.background`, `button.foreground`
- `button.hoverBackground`, `button.hoverForeground`
- `button.pressedBackground`

**Inputs:**
- `input.background`, `input.foreground`
- `input.border`, `input.placeholderForeground`

**Editor:**
- `editor.background`, `editor.foreground`
- `editor.selectionBackground`, `editor.selectionForeground`
- `editor.lineHighlightBackground`

**Lists:**
- `list.background`, `list.foreground`
- `list.activeSelectionBackground`
- `list.hoverBackground`

---

## Responding to Theme Changes

### Automatic Updates

Most widgets don't need special handling - Qt stylesheets update automatically:

```python
class MyWidget(ThemedWidget, QPushButton):
    """Button updates automatically when theme changes."""

    theme_config = {
        'bg': 'button.background',
        'fg': 'button.foreground',
    }

    # No special code needed - Qt stylesheet handles it!
```

### Custom Theme Change Handling

For custom painting or dynamic updates:

```python
class MyWidget(ThemedWidget, QWidget):
    theme_config = {
        'bg': 'window.background',
        'accent': 'colors.primary',
    }

    def on_theme_changed(self):
        """Called automatically when theme changes."""
        # Trigger repaint
        self.update()

        # Update cached values
        self._cached_color = QColor(self.theme.accent)

        # Custom logic
        self.recalculate_layout()
```

### Lifecycle Hooks (Advanced)

```python
class AdvancedWidget(ThemedWidget, QWidget):
    def before_theme_change(self, old_theme, new_theme):
        """Called before theme changes. Return False to prevent change."""
        if self.is_busy():
            return False  # Defer theme change
        return True

    def on_theme_changed(self):
        """Called during theme change."""
        self.update()  # Automatically called for you

    def after_theme_applied(self):
        """Called after theme fully applied."""
        # Expensive operations here
        self.rebuild_syntax_highlighter()
```

---

## Advanced Features

### Using Token Constants

Instead of string literals, use `Tokens` constants for IDE autocomplete:

```python
from vfwidgets_theme import ThemedWidget, Tokens

class MyWidget(ThemedWidget, QTextEdit):
    theme_config = {
        'bg': Tokens.EDITOR_BACKGROUND,      # IDE autocomplete! ✅
        'fg': Tokens.EDITOR_FOREGROUND,
        'selection': Tokens.EDITOR_SELECTION_BACKGROUND,
    }
```

### Using Property Descriptors (NEW in 2.0.0-rc4)

For cleaner code, use `ThemeProperty` descriptors instead of `theme_config`:

```python
from vfwidgets_theme import ThemedWidget, Tokens
from vfwidgets_theme.widgets.properties import ThemeProperty

class MyWidget(ThemedWidget, QWidget):
    # Property descriptors - clean, type-safe access
    bg = ThemeProperty(Tokens.COLORS_BACKGROUND, default='#ffffff')
    fg = ThemeProperty(Tokens.COLORS_FOREGROUND, default='#000000')
    accent = ThemeProperty(Tokens.COLORS_PRIMARY, default='#0078d4')

    def paintEvent(self, event):
        painter = QPainter(self)

        # Clean property access - no getattr or dict lookups!
        painter.fillRect(self.rect(), QColor(self.bg))
        painter.setPen(QColor(self.fg))
```

**Benefits:**
- ✅ IDE autocomplete on property access
- ✅ Type-safe (can't typo property names)
- ✅ Clean syntax (no `self.theme.get()` needed)
- ✅ Read-only (prevents accidental modification)

#### ColorProperty - Automatic QColor Conversion

For color properties, use `ColorProperty` to get `QColor` instances directly:

```python
from vfwidgets_theme import ThemedWidget, Tokens
from vfwidgets_theme.widgets.properties import ColorProperty

class MyWidget(ThemedWidget, QWidget):
    # ColorProperty returns QColor instances automatically
    bg_color = ColorProperty(Tokens.COLORS_BACKGROUND, default='#ffffff')
    fg_color = ColorProperty(Tokens.COLORS_FOREGROUND, default='#000000')
    border_color = ColorProperty(Tokens.COLORS_FOCUS_BORDER, default='#0078d4')

    def paintEvent(self, event):
        painter = QPainter(self)

        # No QColor() conversion needed - already a QColor!
        painter.fillRect(self.rect(), self.bg_color)  # Direct QColor
        painter.setPen(self.fg_color)  # Direct QColor

        # Draw border
        painter.setPen(QPen(self.border_color, 2))
        painter.drawRect(self.rect())
```

#### FontProperty - Automatic QFont Conversion

For font properties, use `FontProperty` to get `QFont` instances directly:

```python
from vfwidgets_theme import ThemedWidget, Tokens
from vfwidgets_theme.widgets.properties import FontProperty, ColorProperty
from PySide6.QtWidgets import QTextEdit

class CodeEditor(ThemedWidget, QTextEdit):
    # FontProperty returns QFont instances automatically
    editor_font = FontProperty('text.font', default='Consolas, 10px')

    # Combine with ColorProperty for complete theming
    bg_color = ColorProperty(Tokens.EDITOR_BACKGROUND, default='#1e1e1e')
    fg_color = ColorProperty(Tokens.EDITOR_FOREGROUND, default='#d4d4d4')

    def __init__(self, parent=None):
        super().__init__(parent)

        # Use properties directly - already converted to Qt types!
        self.setFont(self.editor_font)  # QFont ready to use

        # Apply colors via stylesheet (automatic)
        # or manually in paintEvent

    def paintEvent(self, event):
        # Properties are already the correct Qt types
        painter = QPainter(self.viewport())
        painter.fillRect(self.viewport().rect(), self.bg_color)  # QColor
        painter.setFont(self.editor_font)  # QFont
        painter.setPen(self.fg_color)  # QColor
```

#### Property Descriptors vs theme_config

**Old way (theme_config):**
```python
class MyWidget(ThemedWidget, QWidget):
    theme_config = {
        'bg': Tokens.COLORS_BACKGROUND,
        'fg': Tokens.COLORS_FOREGROUND,
    }

    def paintEvent(self, event):
        # String lookup, manual QColor conversion
        bg = self.theme.bg
        painter.fillRect(self.rect(), QColor(bg))  # Manual conversion
```

**New way (ThemeProperty):**
```python
class MyWidget(ThemedWidget, QWidget):
    bg_color = ColorProperty(Tokens.COLORS_BACKGROUND, default='#ffffff')
    fg_color = ColorProperty(Tokens.COLORS_FOREGROUND, default='#000000')

    def paintEvent(self, event):
        # Direct property access, automatic QColor conversion
        painter.fillRect(self.rect(), self.bg_color)  # Already QColor!
```

**Both work!** Use `theme_config` for simplicity, use property descriptors for cleaner code and type safety.

### Using Widget Roles

For semantic styling:

```python
from vfwidgets_theme import ThemedWidget, WidgetRole, set_widget_role
from PySide6.QtWidgets import QPushButton

class DangerButton(ThemedWidget, QPushButton):
    """Button with danger styling (red)."""

    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.setText(text)

        # Set role for automatic red styling
        set_widget_role(self, WidgetRole.DANGER)
```

**Available roles:**
- `WidgetRole.DANGER` - Red styling
- `WidgetRole.SUCCESS` - Green styling
- `WidgetRole.WARNING` - Yellow styling
- `WidgetRole.SECONDARY` - Muted styling
- `WidgetRole.EDITOR` - Monospace font
- `WidgetRole.PRIMARY` - Primary accent color

---

## Troubleshooting

### Error: "ThemedWidget must come BEFORE ..."

**Problem:**
```python
class MyWidget(QTextEdit, ThemedWidget):  # Wrong order
    pass

# TypeError: MyWidget: ThemedWidget must come BEFORE QTextEdit.
```

**Solution:**
```python
class MyWidget(ThemedWidget, QTextEdit):  # Correct order
    pass
```

---

### Widget Not Updating on Theme Change

**Problem:** Widget doesn't repaint when theme changes.

**Solution:** Override `on_theme_changed()`:

```python
class MyWidget(ThemedWidget, QWidget):
    def on_theme_changed(self):
        """Force repaint."""
        self.update()
```

---

### Theme Values Not Accessible

**Problem:**
```python
color = self.theme.my_color  # AttributeError
```

**Solution:** Check `theme_config` mapping:

```python
class MyWidget(ThemedWidget, QWidget):
    theme_config = {
        'my_color': 'window.background',  # Map it first
    }

    def paintEvent(self, event):
        color = self.theme.my_color  # Now works
```

---

### Can't Access Theme in `__init__`

**Problem:**
```python
class MyWidget(ThemedWidget, QWidget):
    def __init__(self):
        super().__init__()
        color = self.theme.bg  # May not be ready yet
```

**Solution:** Access theme after construction or in `on_theme_changed()`:

```python
class MyWidget(ThemedWidget, QWidget):
    def __init__(self):
        super().__init__()
        # Don't access theme here

    def showEvent(self, event):
        # Safe to access theme now
        color = self.theme.bg
```

---

### Child Widgets Need Theme Access

**Problem:** You have a child widget (non-ThemedWidget) that needs theme colors.

```python
class TabBar(QWidget):  # Not ThemedWidget
    def paintEvent(self, event):
        # How to get theme from parent???
        theme = ???  # No access to theme!
        self.renderer.draw(painter, theme)
```

**Solution:** Use `get_current_theme()` pattern to expose theme from parent:

```python
# Parent widget (ThemedWidget)
class ChromeTabbedWindow(ThemedWidget, QWidget):
    def __init__(self):
        super().__init__()
        self.tab_bar = TabBar(self)  # Child widget

    def get_current_theme(self):
        """Expose theme to children."""
        # Method inherited from ThemedWidget
        return super().get_current_theme()

# Child widget (non-ThemedWidget)
class TabBar(QWidget):
    def _get_theme_from_parent(self):
        """Traverse parent chain to find theme."""
        parent = self.parent()
        while parent:
            if hasattr(parent, 'get_current_theme'):
                return parent.get_current_theme()
            parent = parent.parent()
        return None

    def paintEvent(self, event):
        theme = self._get_theme_from_parent()
        if theme:
            colors = theme.colors
            bg_color = colors.get('tab.activeBackground', '#fff')
            self.renderer.draw(painter, theme)
```

**Alternative:** Pass theme directly to child components:

```python
class ParentWidget(ThemedWidget, QWidget):
    def __init__(self):
        super().__init__()
        self.renderer = CustomRenderer()

    def paintEvent(self, event):
        theme = self.get_current_theme()
        if theme:
            self.renderer.draw(painter, theme)
```

**Key Points:**
- ✅ `get_current_theme()` returns actual Theme object with `.colors` dict
- ✅ Works for passing theme to renderers, painters, child widgets
- ✅ Graceful fallback when theme unavailable (returns None)
- ✅ Standard pattern for complex widgets

---

## Complete Example - Professional Widget

Here's a complete example combining all concepts:

```python
"""
professional_widget.py - Complete themed custom widget example
"""

import sys
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from vfwidgets_theme import (
    ThemedApplication,
    ThemedMainWindow,
    ThemedWidget,
    Tokens,
    WidgetRole,
    set_widget_role,
)
from vfwidgets_theme.widgets.properties import ThemeProperty


class StatusPanel(ThemedWidget, QFrame):
    """Professional status panel with theming."""

    # Using property descriptors for clean access
    bg = ThemeProperty(Tokens.PANEL_BACKGROUND)
    fg = ThemeProperty(Tokens.PANEL_FOREGROUND)
    border = ThemeProperty(Tokens.PANEL_BORDER)

    # Or traditional theme_config
    theme_config = {
        'title_color': Tokens.COLORS_PRIMARY,
        'status_color': Tokens.COLORS_SECONDARY,
    }

    def __init__(self, title="Status", parent=None):
        super().__init__(parent)

        # Set frame style
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setMinimumWidth(200)

        # Create UI
        layout = QVBoxLayout(self)

        # Title label
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Action buttons
        self.start_btn = QPushButton("Start")
        set_widget_role(self.start_btn, WidgetRole.SUCCESS)
        layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("Stop")
        set_widget_role(self.stop_btn, WidgetRole.DANGER)
        layout.addWidget(self.stop_btn)

    def on_theme_changed(self):
        """Update custom styling when theme changes."""
        # Update title color
        self.title_label.setStyleSheet(
            f"color: {self.theme.title_color}; font-weight: bold;"
        )

        # Update status color
        self.status_label.setStyleSheet(
            f"color: {self.theme.status_color};"
        )

    def set_status(self, status_text):
        """Update status text."""
        self.status_label.setText(status_text)


def main():
    """Demo application."""
    app = ThemedApplication(sys.argv)

    window = ThemedMainWindow()
    window.setWindowTitle("Professional Themed Widget")
    window.setMinimumSize(400, 300)

    # Use our custom widget
    panel = StatusPanel("Application Status")
    window.setCentralWidget(panel)

    # Connect buttons
    panel.start_btn.clicked.connect(
        lambda: panel.set_status("Running...")
    )
    panel.stop_btn.clicked.connect(
        lambda: panel.set_status("Stopped")
    )

    window.show()
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
```

---

### Theme Properties May Return Stale Values in `on_theme_changed()`

**Problem:** Theme switches work in one direction but not the other (e.g., dark→light works, but light→dark doesn't).

```python
class MyWidget(ThemedWidget, QWidget):
    theme_config = {
        'bg': 'editor.background',
    }

    def on_theme_changed(self):
        # ❌ May return OLD theme's value!
        bg = self.theme.bg or '#1e1e1e'
        self.setStyleSheet(f"background: {bg};")
```

**Why This Happens:**
- `on_theme_changed()` is called DURING theme transition
- Property cache may still contain values from the previous theme
- Using `or` operator doesn't help if cached value is truthy but wrong

**Solution 1: Query Theme Manager by Name (Most Reliable)**

```python
def _get_current_theme_type(self) -> str:
    """Get current theme type reliably."""
    try:
        if hasattr(self, '_current_theme_name') and self._current_theme_name:
            from vfwidgets_theme import ThemedApplication
            app = ThemedApplication.instance()
            if app and hasattr(app, '_theme_manager') and app._theme_manager:
                # Query by name to get CURRENT theme
                theme = app._theme_manager.get_theme(self._current_theme_name)
                if theme and hasattr(theme, 'type'):
                    return theme.type
    except Exception:
        pass
    return 'dark'

def on_theme_changed(self):
    theme_type = self._get_current_theme_type()

    # Select appropriate fallbacks based on theme type
    if theme_type == 'light':
        fallbacks = {'bg': '#ffffff', 'fg': '#000000'}
    else:
        fallbacks = {'bg': '#1e1e1e', 'fg': '#d4d4d4'}

    # Use fallbacks directly - don't trust self.theme properties
    self.setStyleSheet(f"background: {fallbacks['bg']};")
```

**Solution 2: Use ThemeProperty Descriptors (Cleaner)**

```python
from vfwidgets_theme.widgets.properties import ThemeProperty

class MyWidget(ThemedWidget, QWidget):
    bg = ThemeProperty('colors.background', default='#ffffff')

    def on_theme_changed(self):
        # ThemeProperty handles caching correctly
        self.setStyleSheet(f"background: {self.bg};")
```

**When This Matters Most:**
- WebView-based widgets (xterm.js, Monaco Editor, etc.)
- Custom painting code that caches colors
- Bidirectional theme switching (light↔dark multiple times)

**📖 For detailed guidance on WebView integration, see:**
[Terminal Widget Theme Integration Lessons](../../terminal_widget/docs/theme-integration-lessons-GUIDE.md)

---

## Next Steps

### Further Reading

- **[API Reference](api-REFERENCE.md)** - Complete ThemedWidget API
- **[Theme Customization](theme-customization-GUIDE.md)** - Create custom themes
- **[API Strategy](API-STRATEGY.md)** - Understand the progressive API design
- **[WebView Theme Integration](../../terminal_widget/docs/theme-integration-lessons-GUIDE.md)** - xterm.js, Monaco, WebView widgets

### Advanced Topics

- Building widget libraries with theming support
- Custom theme applicators
- Theme inheritance and composition
- Performance optimization for large widget trees

---

## Summary

🎯 **Key Takeaways:**

1. **Use `ThemedWidget` for any Qt base class** - QTextEdit, QFrame, QPushButton, etc.
2. **Inheritance order matters** - ThemedWidget must come FIRST
3. **theme_config maps tokens** - Connect theme values to your widget
4. **Automatic updates** - Most widgets work without custom code
5. **Advanced features available** - Tokens, ThemeProperty, WidgetRole for cleaner code

**You now have the full power of the theme system!** 🚀

Build amazing custom widgets that seamlessly integrate with your application's theme.
