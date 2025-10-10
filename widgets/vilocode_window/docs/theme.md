# ViloCodeWindow Theme Integration Guide

Complete guide to theming ViloCodeWindow and its child widgets using the vfwidgets-theme system.

---

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Theme Integration Architecture](#theme-integration-architecture)
- [VS Code Color Tokens](#vs-code-color-tokens)
- [Theming Child Widgets](#theming-child-widgets)
- [Custom Themes](#custom-themes)
- [Fallback Without Theme System](#fallback-without-theme-system)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

ViloCodeWindow integrates with the **vfwidgets-theme** system to provide automatic, VS Code-compatible theming. The theme system is **optional** — the widget works standalone with sensible fallback colors.

**Key Features**:
- **Optional dependency**: Works with or without vfwidgets-theme
- **Automatic theming**: Colors applied automatically when theme changes
- **VS Code tokens**: Uses standard VS Code theme token names
- **Fallback colors**: Sensible defaults when theme unavailable
- **Child widget theming**: Automatically applies themes to main pane content

---

## Quick Start

### With Theme System

```python
from PySide6.QtWidgets import QApplication, QTextEdit
from vfwidgets_vilocode_window import ViloCodeWindow

# Install: pip install vfwidgets-theme
from vfwidgets_theme import get_theme_manager

app = QApplication([])

# Create window (automatically integrates with theme)
window = ViloCodeWindow()
window.setWindowTitle("Themed IDE")
window.set_main_content(QTextEdit())

# Apply a theme
theme_manager = get_theme_manager()
theme_manager.apply_theme("Dark Default")

window.show()
app.exec()
```

### Without Theme System

```python
from PySide6.QtWidgets import QApplication, QTextEdit
from vfwidgets_vilocode_window import ViloCodeWindow

app = QApplication([])

# Create window (uses fallback colors)
window = ViloCodeWindow()
window.setWindowTitle("Fallback Colors IDE")
window.set_main_content(QTextEdit())

window.show()
app.exec()
```

The window **automatically detects** if vfwidgets-theme is available and adapts accordingly.

---

## Theme Integration Architecture

### Dynamic Base Class Pattern

ViloCodeWindow uses **dynamic base class composition** to support optional theming:

```python
# In src/vfwidgets_vilocode_window/vilocode_window.py

try:
    from vfwidgets_theme import ThemedWidget
    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False
    ThemedWidget = object

# Dynamically create base class
if THEME_AVAILABLE:
    # Inherit from ThemedWidget + QWidget
    _BaseClass = type("_BaseClass", (ThemedWidget, QWidget), {})
else:
    # Just QWidget
    _BaseClass = QWidget

class ViloCodeWindow(_BaseClass):
    """Works with or without theme system."""
```

**Benefits**:
- No hard dependency on vfwidgets-theme
- Automatic theme integration when available
- Zero performance overhead when theme system not installed

### Theme Config Mapping

ViloCodeWindow defines theme mappings via `theme_config` dictionary:

```python
class ViloCodeWindow(_BaseClass):
    theme_config = {
        # Window
        "window_background": "editor.background",

        # Activity Bar
        "activity_bar_background": "activityBar.background",
        "activity_bar_foreground": "activityBar.foreground",
        "activity_bar_border": "activityBar.border",
        "activity_bar_active_border": "activityBar.activeBorder",
        "activity_bar_inactive_foreground": "activityBar.inactiveForeground",

        # Sidebar
        "sidebar_background": "sideBar.background",
        "sidebar_foreground": "sideBar.foreground",
        "sidebar_border": "sideBar.border",
        "sidebar_title_foreground": "sideBarTitle.foreground",

        # Editor/Main Pane
        "editor_background": "editor.background",
        "editor_foreground": "editor.foreground",

        # Status Bar
        "statusbar_background": "statusBar.background",
        "statusbar_foreground": "statusBar.foreground",
        "statusbar_border": "statusBar.border",

        # Menu
        "menu_background": "menu.background",
        "menu_foreground": "menu.foreground",

        # Title Bar
        "titlebar_background": "titleBar.activeBackground",
        "titlebar_foreground": "titleBar.activeForeground",
        "titlebar_border": "titleBar.border",
    }
```

**How it Works**:
1. ThemedWidget reads `theme_config` on initialization
2. Maps internal color roles (left side) to VS Code tokens (right side)
3. Applies colors automatically when theme changes
4. Calls `on_theme_changed()` when theme switches

### Theme Change Flow

```
User calls: theme_manager.apply_theme("Dark Default")
  ↓
ThemeManager loads theme colors from JSON
  ↓
ThemeManager.theme_changed signal emitted
  ↓
ThemedWidget.on_theme_changed(theme_name) called
  ↓
ViloCodeWindow.on_theme_changed(theme_name) called
  ↓
ViloCodeWindow._apply_theme_colors() called
  ↓
Components update their colors
  ↓
window.update() - repaint with new colors
```

---

## VS Code Color Tokens

ViloCodeWindow uses standard VS Code color tokens. Full reference:

### Activity Bar Tokens

| Token | Description | Example |
|-------|-------------|---------|
| `activityBar.background` | Activity bar background | #333333 |
| `activityBar.foreground` | Icon color | #FFFFFF |
| `activityBar.border` | Right border | #444444 |
| `activityBar.activeBorder` | Active item border | #007ACC |
| `activityBar.inactiveForeground` | Inactive icon color | #CCCCCC80 |

### Sidebar Tokens

| Token | Description | Example |
|-------|-------------|---------|
| `sideBar.background` | Sidebar background | #252526 |
| `sideBar.foreground` | Sidebar text | #CCCCCC |
| `sideBar.border` | Right border | #444444 |
| `sideBarTitle.foreground` | Panel title color | #FFFFFF |

### Editor Tokens

| Token | Description | Example |
|-------|-------------|---------|
| `editor.background` | Main pane background | #1E1E1E |
| `editor.foreground` | Main pane text | #D4D4D4 |

### Status Bar Tokens

| Token | Description | Example |
|-------|-------------|---------|
| `statusBar.background` | Status bar background | #007ACC |
| `statusBar.foreground` | Status bar text | #FFFFFF |
| `statusBar.border` | Top border | #00000000 |

### Title Bar Tokens (Frameless Mode)

| Token | Description | Example |
|-------|-------------|---------|
| `titleBar.activeBackground` | Title bar background | #3C3C3C |
| `titleBar.activeForeground` | Title bar text | #CCCCCC |
| `titleBar.border` | Bottom border | #444444 |

### Menu Tokens

| Token | Description | Example |
|-------|-------------|---------|
| `menu.background` | Menu background | #252526 |
| `menu.foreground` | Menu text | #CCCCCC |

**Full VS Code Token Reference**: https://code.visualstudio.com/api/references/theme-color

---

## Theming Child Widgets

When you place widgets in the main pane, you should theme them too!

### Pattern 1: ThemedWidget for Main Content

```python
from PySide6.QtWidgets import QTextEdit
from vfwidgets_theme import ThemedWidget

class ThemedTextEdit(ThemedWidget, QTextEdit):
    """Text editor with theme integration."""

    theme_config = {
        "background": "editor.background",
        "foreground": "editor.foreground",
        "selection_bg": "editor.selectionBackground",
        "selection_fg": "editor.selectionForeground",
    }

    def __init__(self):
        super().__init__()
        # ThemedWidget handles theme application

# Use in ViloCodeWindow
window = ViloCodeWindow()
editor = ThemedTextEdit()
window.set_main_content(editor)
```

### Pattern 2: Manual Theme Colors

```python
from vfwidgets_theme import get_theme_manager

# Get current theme colors
theme = get_theme_manager().get_current_theme()
bg_color = theme.get_color("editor.background", "#1E1E1E")
fg_color = theme.get_color("editor.foreground", "#D4D4D4")

# Apply to widget
widget = QTextEdit()
widget.setStyleSheet(f"""
    QTextEdit {{
        background-color: {bg_color.name()};
        color: {fg_color.name()};
    }}
""")

window.set_main_content(widget)
```

### Pattern 3: Auto-detect Theme (example in 05_advanced_ide.py)

```python
def get_theme_colors():
    """Get theme colors if available, else fallback."""
    try:
        from vfwidgets_theme import get_theme_manager
        theme = get_theme_manager().get_current_theme()
        return {
            "bg": theme.get_color("editor.background", "#1E1E1E"),
            "fg": theme.get_color("editor.foreground", "#D4D4D4"),
            "border": theme.get_color("editor.lineHighlightBorder", "#444444"),
        }
    except ImportError:
        # Fallback colors
        return {
            "bg": QColor("#1E1E1E"),
            "fg": QColor("#D4D4D4"),
            "border": QColor("#444444"),
        }

# Use theme colors
colors = get_theme_colors()
widget.setStyleSheet(f"""
    QWidget {{
        background-color: {colors["bg"].name()};
        color: {colors["fg"].name()};
        border: 1px solid {colors["border"].name()};
    }}
""")
```

---

## Custom Themes

### Creating a Custom Theme

1. **Create theme JSON file**:

```json
{
  "name": "My Dark Theme",
  "type": "dark",
  "colors": {
    "activityBar.background": "#1a1a1a",
    "activityBar.foreground": "#ffffff",
    "activityBar.activeBorder": "#00ff00",
    "sideBar.background": "#202020",
    "sideBar.foreground": "#e0e0e0",
    "editor.background": "#181818",
    "editor.foreground": "#ffffff",
    "statusBar.background": "#00aa00",
    "statusBar.foreground": "#ffffff",
    "titleBar.activeBackground": "#2a2a2a",
    "titleBar.activeForeground": "#ffffff"
  }
}
```

2. **Register and apply the theme**:

```python
from vfwidgets_theme import get_theme_manager

theme_manager = get_theme_manager()

# Register custom theme
theme_manager.register_theme_file("path/to/my_theme.json")

# Apply custom theme
theme_manager.apply_theme("My Dark Theme")
```

### Extending ViloCodeWindow Theme Config

You can add custom theme mappings by subclassing:

```python
class MyViloCodeWindow(ViloCodeWindow):
    theme_config = {
        **ViloCodeWindow.theme_config,  # Inherit defaults
        "custom_accent": "my.custom.accent",
        "custom_highlight": "my.custom.highlight",
    }

    def _apply_theme_colors(self):
        """Override to apply custom colors."""
        super()._apply_theme_colors()

        # Apply custom colors
        if THEME_AVAILABLE:
            accent = self.get_theme_color("custom_accent", "#FF0000")
            # Use accent color...
```

---

## Fallback Without Theme System

When vfwidgets-theme is **not installed**, ViloCodeWindow uses sensible fallback colors:

```python
# Default fallback colors (dark theme)
FALLBACK_COLORS = {
    "activity_bar_background": QColor(51, 51, 51),      # #333333
    "activity_bar_foreground": QColor(255, 255, 255),   # #FFFFFF
    "sidebar_background": QColor(37, 37, 38),           # #252526
    "sidebar_foreground": QColor(204, 204, 204),        # #CCCCCC
    "editor_background": QColor(30, 30, 30),            # #1E1E1E
    "editor_foreground": QColor(212, 212, 212),         # #D4D4D4
    "statusbar_background": QColor(0, 122, 204),        # #007ACC
    "statusbar_foreground": QColor(255, 255, 255),      # #FFFFFF
    "titlebar_background": QColor(60, 60, 60),          # #3C3C3C
    "titlebar_foreground": QColor(204, 204, 204),       # #CCCCCC
}
```

These colors match VS Code's "Dark Default" theme.

---

## Best Practices

### 1. Always Provide Fallback Colors

When getting theme colors, **always** provide fallback:

```python
# ✅ Good
bg = theme.get_color("editor.background", "#1E1E1E")

# ❌ Bad
bg = theme.get_color("editor.background")  # May return None!
```

### 2. Use Correct Token Names

Use **standard VS Code token names** for best compatibility:

```python
# ✅ Good - standard token
"background": "editor.background"

# ❌ Bad - non-standard token
"background": "myCustomBackground"  # Won't work with most themes!
```

### 3. Theme Main Pane Content

**Always theme your main pane widgets** to match the IDE aesthetic:

```python
# ✅ Good - themed main content
class ThemedEditor(ThemedWidget, QTextEdit):
    theme_config = {"bg": "editor.background", "fg": "editor.foreground"}

# ❌ Bad - unthemed main content
editor = QTextEdit()  # Uses default Qt styling (won't match!)
```

### 4. Check Theme Availability

When widgets in main pane need theming, check if theme is available:

```python
try:
    from vfwidgets_theme import ThemedWidget, get_theme_manager
    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False

if THEME_AVAILABLE:
    # Use ThemedWidget
    class MyWidget(ThemedWidget, QWidget):
        theme_config = {...}
else:
    # Use regular QWidget with fallback colors
    class MyWidget(QWidget):
        def __init__(self):
            super().__init__()
            self.setStyleSheet("background: #1E1E1E; color: #D4D4D4;")
```

### 5. Test Both Modes

Always test your widget with **and without** vfwidgets-theme:

```bash
# Test without theme (fallback mode)
pip uninstall vfwidgets-theme
python my_app.py

# Test with theme
pip install vfwidgets-theme
python my_app.py
```

---

## Troubleshooting

### Problem: Widget Not Themed

**Symptoms**: Widget displays with default Qt colors instead of theme colors.

**Causes & Solutions**:

1. **Widget not inheriting ThemedWidget**:
   ```python
   # ❌ Problem
   class MyWidget(QWidget):
       pass

   # ✅ Solution
   class MyWidget(ThemedWidget, QWidget):
       theme_config = {"bg": "editor.background"}
   ```

2. **Missing theme_config**:
   ```python
   # ❌ Problem
   class MyWidget(ThemedWidget, QWidget):
       pass  # No theme_config!

   # ✅ Solution
   class MyWidget(ThemedWidget, QWidget):
       theme_config = {"bg": "editor.background", "fg": "editor.foreground"}
   ```

3. **Invalid token name**:
   ```python
   # ❌ Problem
   theme_config = {"bg": "editor.bg"}  # Wrong token name!

   # ✅ Solution
   theme_config = {"bg": "editor.background"}  # Correct token name
   ```

---

### Problem: Colors Not Updating on Theme Change

**Symptoms**: Colors stay the same when switching themes.

**Causes & Solutions**:

1. **Not calling super().on_theme_changed()**:
   ```python
   # ❌ Problem
   def on_theme_changed(self, theme_name: str):
       self.update()  # Forgot to call super!

   # ✅ Solution
   def on_theme_changed(self, theme_name: str):
       super().on_theme_changed(theme_name)  # Call super first!
       self.update()
   ```

2. **QSS overriding theme colors**:
   ```python
   # ❌ Problem
   widget.setStyleSheet("background: #FF0000;")  # Hardcoded color!

   # ✅ Solution
   # Use theme colors in stylesheet
   bg = theme.get_color("editor.background", "#1E1E1E")
   widget.setStyleSheet(f"background: {bg.name()};")
   ```

---

### Problem: Theme Not Found

**Symptoms**: `ThemeNotFoundError` when applying theme.

**Solution**:

1. Check theme name spelling:
   ```python
   # ❌ Problem
   theme_manager.apply_theme("dark default")  # Wrong case!

   # ✅ Solution
   theme_manager.apply_theme("Dark Default")  # Correct case
   ```

2. List available themes:
   ```python
   theme_manager = get_theme_manager()
   themes = theme_manager.get_available_themes()
   print(themes)  # ['Dark Default', 'Light Default', ...]
   ```

---

### Problem: Fallback Colors Not Applied

**Symptoms**: Widget is black/white instead of fallback colors.

**Solution**:

Check that `_apply_theme_colors()` is being called:

```python
def __init__(self):
    super().__init__()
    # ... other init code ...

    # Apply theme colors (or fallback)
    self._apply_theme_colors()  # Don't forget this!
```

---

## See Also

- [api.md](api.md) - Complete API reference
- [architecture.md](architecture.md) - Internal architecture
- [vfwidgets-theme README](../../theme_system/README.md) - Theme system documentation
- [VS Code Theme Color Reference](https://code.visualstudio.com/api/references/theme-color) - Official VS Code token list
- [examples/05_advanced_ide.py](../examples/05_advanced_ide.py) - Advanced example with theming
