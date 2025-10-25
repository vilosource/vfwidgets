---
name: theme-integration
description: Guide for integrating vfwidgets-theme into widgets using ThemedWidget mixin pattern. Use when adding theme support, dark mode, or styling to widgets.
allowed-tools:
  - Read
  - Edit
  - Grep
---

# Theme Integration Skill

When the user asks to add theme system support to a widget, follow these patterns to ensure proper integration with the VFWidgets theme system.

## Overview

The VFWidgets theme system uses the **ThemedWidget mixin pattern** to provide:
- Automatic theme color application
- Live theme switching support
- Theme token resolution with fallbacks
- Optional dependency (widgets work without theme system)

## 1. Understanding Theme System Architecture

The theme system provides:

- **ThemedWidget**: Mixin class that adds theming capabilities
- **ThemedApplication**: Application-level theme management
- **ThemeManager**: Singleton for theme token resolution
- **Theme tokens**: Hierarchical color tokens (e.g., `editor.background`, `input.foreground`)

**Key principle**: Theme integration is **optional** - widgets should work with or without the theme system installed.

## 2. Optional Dependency Pattern

Always implement theme integration as an optional dependency:

```python
# Check if theme system is available
try:
    from vfwidgets_theme import ThemedWidget
    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False
    ThemedWidget = object  # Fallback to object

# Use conditional base class
if THEME_AVAILABLE:
    _BaseClass = type("_BaseClass", (ThemedWidget, QWidget), {})
else:
    _BaseClass = QWidget

class MyWidget(_BaseClass):
    """Widget with optional theme support."""

    # Only define theme_config if theme system available
    if THEME_AVAILABLE:
        theme_config = {
            "bg": "editor.background",
            "fg": "editor.foreground",
        }
```

## 3. Theme Token Mapping

Use the `theme_config` dictionary to map widget properties to theme tokens:

```python
from vfwidgets_theme import ThemedWidget

class MyThemedWidget(ThemedWidget):
    """Widget with theme integration."""

    theme_config = {
        # Map property names to theme tokens
        "background": "editor.background",
        "foreground": "editor.foreground",
        "border": "widget.border",
        "hover_bg": "list.hoverBackground",
        "selection_bg": "editor.selectionBackground",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        # Theme is automatically applied during initialization
```

## 4. Common Theme Tokens

Use these standard tokens for consistency:

### Editor/Content Areas
- `editor.background` - Main content background
- `editor.foreground` - Main content text
- `editor.selectionBackground` - Selected text background
- `editor.selectionForeground` - Selected text foreground

### Input Fields
- `input.background` - Input field background
- `input.foreground` - Input field text
- `input.border` - Input field border (normal state)
- `input.focusBorder` - Input field border (focused)
- `input.placeholderForeground` - Placeholder text

### Widgets/UI Elements
- `widget.border` - Widget borders
- `widget.shadow` - Widget shadows
- `list.hoverBackground` - Hover state background
- `list.activeSelectionBackground` - Active selection
- `list.inactiveSelectionBackground` - Inactive selection

### Code Blocks (Markdown widgets)
- `markdown.colors.code.background` - Code block background
- `markdown.colors.code.foreground` - Code block text
- `markdown.colors.link` - Hyperlink color

### Scrollbars
- `markdown.colors.scrollbar.background` - Scrollbar track
- `markdown.colors.scrollbar.thumb` - Scrollbar thumb
- `markdown.colors.scrollbar.thumbHover` - Scrollbar thumb hover

## 5. Manual Theme Resolution (Advanced)

For complex styling scenarios, use ThemeManager directly:

```python
from PySide6.QtWidgets import QWidget
from vfwidgets_theme.core.manager import ThemeManager

class ComplexWidget(QWidget):
    """Widget with manual theme resolution."""

    def _build_stylesheet(self) -> str:
        """Build theme-aware stylesheet."""
        theme_mgr = ThemeManager.get_instance()

        # Resolve colors with fallbacks
        bg = theme_mgr.resolve_color("editor.background", "#1e1e1e")
        fg = theme_mgr.resolve_color("editor.foreground", "#d4d4d4")
        border = theme_mgr.resolve_color("input.focusBorder", "#007acc")

        return f"""
            QWidget {{
                background-color: {bg};
                color: {fg};
                border: 1px solid {border};
            }}
        """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(self._build_stylesheet())
```

## 6. Live Theme Switching Support

For widgets that need to update during theme changes:

### Method 1: Using ThemedWidget (Automatic)

```python
from vfwidgets_theme import ThemedWidget

class AutoUpdateWidget(ThemedWidget):
    """Widget with automatic theme updates."""

    theme_config = {
        "bg": "editor.background",
        "fg": "editor.foreground",
    }

    # ThemedWidget automatically handles theme changes
```

### Method 2: Manual Update in paintEvent

```python
class ManualUpdateWidget(QWidget):
    """Widget with manual theme update."""

    def paintEvent(self, event):
        """Paint event with theme update check."""
        # Update stylesheet if theme changed
        current_theme = self._get_current_theme()
        if current_theme != self._last_theme:
            self.setStyleSheet(self._build_stylesheet())
            self._last_theme = current_theme

        super().paintEvent(event)
```

## 7. Real-World Example: ChromeTabBar Editor

Reference implementation from `widgets/chrome-tabbed-window/src/chrome_tabbed_window/view/chrome_tab_bar.py:909-980`:

```python
def _build_editor_stylesheet(self) -> str:
    """Build theme-aware stylesheet for QLineEdit tab editor."""
    # Default fallback colors
    default_bg = "#3c3c3c"
    default_fg = "#cccccc"
    default_border = "#0078d4"

    try:
        from vfwidgets_theme.core.manager import ThemeManager
        theme_mgr = ThemeManager.get_instance()

        # Resolve colors from theme tokens
        bg = theme_mgr.resolve_color("input.background", default_bg)
        fg = theme_mgr.resolve_color("input.foreground", default_fg)
        border = theme_mgr.resolve_color("input.focusBorder", default_border)

    except (ImportError, AttributeError, Exception):
        # Fallback if theme system unavailable
        bg = default_bg
        fg = default_fg
        border = default_border

    return f"""
        QLineEdit {{
            background: {bg};
            color: {fg};
            border: 2px solid {border};
        }}
    """
```

## 8. Testing Theme Integration

Verify theme integration works correctly:

```python
def test_widget_with_theme():
    """Test widget with theme system available."""
    from vfwidgets_theme import ThemedApplication

    app = ThemedApplication([])
    widget = MyThemedWidget()

    # Widget should apply theme
    assert widget.styleSheet()  # Should have themed stylesheet

def test_widget_without_theme():
    """Test widget works without theme system."""
    # Create widget without ThemedApplication
    app = QApplication([])
    widget = MyThemedWidget()

    # Widget should still work (using fallback styles)
    assert widget is not None
```

## 9. Adding Theme Support to Existing Widget

Steps to add theme support to an existing widget:

1. **Add optional dependency** to `pyproject.toml`:
   ```toml
   [project.optional-dependencies]
   theme = ["vfwidgets-theme>=2.0.0"]
   ```

2. **Import with fallback**:
   ```python
   try:
       from vfwidgets_theme import ThemedWidget
       THEME_AVAILABLE = True
   except ImportError:
       THEME_AVAILABLE = False
       ThemedWidget = object
   ```

3. **Update base class**:
   ```python
   class MyWidget(ThemedWidget, QWidget):  # Add ThemedWidget mixin
       theme_config = {
           "bg": "editor.background",
           "fg": "editor.foreground",
       }
   ```

4. **Update examples** to show theme usage:
   ```python
   from vfwidgets_theme import ThemedApplication

   app = ThemedApplication([])
   app.set_theme("dark")  # or "light"
   ```

## 10. Performance Considerations

Theme system is designed for performance:
- **< 100ms** theme switching time
- **< 1KB** per widget memory overhead
- Lazy theme token resolution
- Cached color lookups

Avoid:
- ❌ Creating new ThemeManager instances (use singleton)
- ❌ Resolving theme tokens in tight loops
- ❌ Rebuilding stylesheets every frame

Prefer:
- ✅ Using ThemedWidget mixin (automatic optimization)
- ✅ Caching resolved colors
- ✅ Only updating on theme change events

## 11. Documentation References

For more details, see:

- **Theme integration guide**: `docs/theme-integration-GUIDE.md` - Complete quick reference for theme integration
- **Theme system source**: `widgets/theme_system/src/vfwidgets_theme/` - Implementation details
- **Example integrations**:
  - `widgets/chrome-tabbed-window/` - Tab editor (lines 909-980)
  - `widgets/workspace_widget/` - WorkspaceWidget with optional theme support
  - `widgets/markdown_widget/` - MarkdownViewer with theme integration

## Checklist for Theme Integration

Before marking theme integration as complete:

- [ ] Widget works WITH theme system installed
- [ ] Widget works WITHOUT theme system installed (fallback)
- [ ] Used appropriate theme tokens (not hardcoded colors)
- [ ] Live theme switching works (if applicable)
- [ ] Added theme example to examples/
- [ ] Updated README with theme usage
- [ ] Tests pass with and without theme system
- [ ] Performance acceptable (< 100ms theme switch)
