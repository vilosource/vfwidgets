# Theme System Integration Guide

## Overview

ChromeTabbedWindow integrates with the VFWidgets theme system to provide automatic color adaptation and dynamic theme switching. This guide explains how the integration works and how to use it effectively.

## Architecture

### ThemedWidget Inheritance

ChromeTabbedWindow inherits from `ThemedWidget` mixin when the theme system is available:

```python
from vfwidgets_theme.widgets.base import ThemedWidget

class ChromeTabbedWindow(ThemedWidget, QWidget):
    """Chrome-style tabbed window with theme support.

    IMPORTANT: ThemedWidget MUST come first for theming to work!
    """
    pass
```

This provides:
- Automatic theme detection
- Theme change notifications via `_on_theme_changed()`
- Access to theme colors via `get_current_theme()`

### Graceful Fallback

When the theme system is not available, ChromeTabbedWindow automatically falls back to hardcoded Chrome colors:

```python
try:
    from vfwidgets_theme.widgets.base import ThemedWidget
    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False
    ThemedWidget = object
```

This ensures backward compatibility with applications that don't use the theme system.

## Color Mapping

Chrome tab colors are mapped to theme tokens:

| Tab Element | Theme Token | Fallback Color |
|-------------|-------------|----------------|
| Active tab background | `tab.activeBackground` | `#FFFFFF` |
| Inactive tab background | `tab.inactiveBackground` | `#F2F3F5` |
| Hover tab background | `tab.hoverBackground` | `#F8F9FA` |
| Active tab text | `tab.activeForeground` | `#3C4043` |
| Inactive tab text | `tab.inactiveForeground` | `#5F6368` |
| Tab border | `tab.border` | `#C1C3C7` |
| Tab bar background | `editorGroupHeader.tabsBackground` | `#DEE1E6` |

### ChromeTabRenderer Theme Colors

The `ChromeTabRenderer.get_tab_colors()` method extracts colors from theme:

```python
@classmethod
def get_tab_colors(cls, theme: Optional[Any] = None) -> Dict[str, QColor]:
    """Get tab colors from theme or fallback to Chrome defaults."""
    if theme is None or not hasattr(theme, 'colors'):
        # Fallback to hardcoded Chrome colors
        return {...}

    # Extract colors from theme
    colors = theme.colors
    return {
        'background': QColor(colors.get('tab.inactiveBackground', '#DEE1E6')),
        'tab_normal': QColor(colors.get('tab.inactiveBackground', '#F2F3F5')),
        'tab_hover': QColor(colors.get('tab.hoverBackground', '#F8F9FA')),
        'tab_active': QColor(colors.get('tab.activeBackground', '#FFFFFF')),
        'text': QColor(colors.get('tab.activeForeground', '#3C4043')),
        'text_inactive': QColor(colors.get('tab.inactiveForeground', '#5F6368')),
        'border': QColor(colors.get('tab.border', '#C1C3C7')),
        # ...
    }
```

## Usage Examples

### Basic Theme Support

```python
from vfwidgets_theme import ThemedApplication
from chrome_tabbed_window import ChromeTabbedWindow

app = ThemedApplication(sys.argv)
app.set_theme("dark")

window = ChromeTabbedWindow()
window.addTab(QTextEdit(), "Tab 1")
# Tabs automatically use theme colors!
```

### Theme Switching

```python
from vfwidgets_theme.widgets import add_theme_menu

# Add theme menu to window
add_theme_menu(window)

# Or programmatically
app.set_theme("dark")    # Switch to dark theme
app.set_theme("light")   # Switch to light theme
app.set_theme("default") # Switch to default theme
app.set_theme("minimal") # Switch to minimal theme
```

### Embedded Mode with Themed Parent

```python
from vfwidgets_theme.widgets import ThemedMainWindow, ThemedQWidget

class MainWindow(ThemedMainWindow):
    def __init__(self):
        super().__init__()

        central = ThemedQWidget()
        layout = QVBoxLayout(central)

        # Embedded tabs inherit theme from parent
        tabs = ChromeTabbedWindow(parent=central)
        tabs.addTab(QTextEdit(), "Tab 1")
        layout.addWidget(tabs)

        self.setCentralWidget(central)

# Both main window and tabs use same theme
app = ThemedApplication(sys.argv)
app.set_theme("dark")
window = MainWindow()
```

### Custom Themes

Create custom themes and ChromeTabbedWindow will use them:

```python
custom_theme = {
    "name": "custom",
    "colors": {
        "tab.activeBackground": "#1E1E1E",
        "tab.inactiveBackground": "#2D2D2D",
        "tab.hoverBackground": "#3E3E3E",
        "tab.activeForeground": "#FFFFFF",
        "tab.inactiveForeground": "#CCCCCC",
        "tab.border": "#454545",
        "editorGroupHeader.tabsBackground": "#252525",
        # ... other colors
    }
}

app.add_custom_theme(custom_theme)
app.set_theme("custom")
```

## Implementation Details

### Theme Change Handling

ChromeTabbedWindow implements `_on_theme_changed()` to handle theme updates:

```python
def _on_theme_changed(self) -> None:
    """Called automatically when the application theme changes.

    Updates the tab bar and window controls with new theme colors.
    """
    if not THEME_AVAILABLE:
        return

    # Trigger tab bar repaint with new theme colors
    if hasattr(self, '_tab_bar') and self._tab_bar:
        self._tab_bar.update()

    # Update window controls if in frameless mode
    if hasattr(self, '_window_controls') and self._window_controls:
        self._window_controls.update()

    # Force full repaint
    self.update()
```

### ChromeTabBar Theme Integration

The tab bar gets theme from parent and passes it to renderer:

```python
def paintEvent(self, event: QPaintEvent) -> None:
    """Custom paint event for Chrome-style tabs."""
    painter = QPainter(self)

    # Get theme from parent ChromeTabbedWindow
    theme = self._get_theme_from_parent()

    # Use theme for background
    ChromeTabRenderer.draw_tab_bar_background(painter, self.rect(), theme)

    # Paint tabs with theme
    for i in range(self.count()):
        self._paint_chrome_tab_with_renderer(painter, i, is_active, theme)

def _get_theme_from_parent(self):
    """Get theme from parent ChromeTabbedWindow if available."""
    parent_window = self.parent()
    while parent_window:
        if hasattr(parent_window, 'get_current_theme'):
            return parent_window.get_current_theme()
        parent_window = parent_window.parent()
    return None
```

### WindowControls Theme Integration

Window control buttons also support theming:

```python
class WindowControlButton(QPushButton):
    def _get_theme_colors(self):
        """Get colors from theme or fallback to defaults."""
        parent_widget = self.parent()
        while parent_widget:
            if hasattr(parent_widget, 'get_current_theme'):
                theme = parent_widget.get_current_theme()
                if theme and hasattr(theme, 'colors'):
                    colors = theme.colors
                    return {
                        'normal': QColor(0, 0, 0, 0),
                        'hover': QColor(colors.get('toolbar.hoverBackground', 'rgba(0, 0, 0, 0.1)')),
                        'icon': QColor(colors.get('icon.foreground', '#000000')),
                    }
            parent_widget = parent_widget.parent()
        return {...}  # Fallback
```

## Testing

Test theme integration:

```python
def test_theme_integration():
    app = ThemedApplication([])
    window = ChromeTabbedWindow()

    # Verify themed widget
    from vfwidgets_theme import ThemedWidget
    assert isinstance(window, ThemedWidget)

    # Test theme switching
    app.set_theme("dark")
    assert window.get_current_theme().name == "dark"

    app.set_theme("light")
    assert window.get_current_theme().name == "light"
```

Run the full test suite:

```bash
pytest tests/test_theme_integration.py -v
```

## Troubleshooting

### Problem: Tabs don't update when theme changes

**Solution:** Ensure ChromeTabbedWindow inherits from ThemedWidget FIRST:

```python
# ✅ Correct order
class ChromeTabbedWindow(ThemedWidget, QWidget):
    pass

# ❌ Wrong - theming won't work!
class ChromeTabbedWindow(QWidget, ThemedWidget):
    pass
```

### Problem: Custom colors not showing

**Solution:** Check theme token names match exactly:

```python
# Correct - with proper token names
theme.colors["tab.activeBackground"] = "#FFFFFF"
theme.colors["tab.inactiveBackground"] = "#F2F3F5"

# Wrong - incorrect token names
theme.colors["activeBackground"] = "#FFFFFF"  # Missing "tab." prefix
```

### Problem: Embedded tabs don't match parent theme

**Solution:** Ensure parent window uses ThemedMainWindow:

```python
# ✅ Correct
from vfwidgets_theme.widgets import ThemedMainWindow
main_window = ThemedMainWindow()

# ❌ Wrong - won't receive theme updates
from PySide6.QtWidgets import QMainWindow
main_window = QMainWindow()
```

### Problem: Theme colors look wrong

**Solution:** Verify theme has all required tokens defined. Missing tokens fall back to Chrome defaults. Check theme file for completeness.

## Performance Considerations

- **Theme color lookup**: Fast (< 1ms), colors are cached in dictionaries
- **Theme changes**: Only repaint on actual theme change, not on every access
- **Memory**: Theme colors are references, not copies
- **Startup**: No performance impact, theme integration is lazy

## Best Practices

1. **Always use ThemedApplication** when you want theme support
2. **Use ThemedMainWindow/ThemedQWidget** for parent containers
3. **Let the theme system handle colors** - don't override with custom stylesheets
4. **Test with all built-in themes** to ensure consistent appearance
5. **Provide meaningful theme token fallbacks** for custom themes

## VS Code Theme Compatibility

ChromeTabbedWindow uses VS Code theme tokens, making it compatible with imported VS Code themes:

```python
from vfwidgets_theme.vscode import import_vscode_theme

# Import a VS Code theme
theme = import_vscode_theme("path/to/theme.json")
app.add_custom_theme(theme)
app.set_theme(theme.name)

# ChromeTabbedWindow automatically adapts!
```

## Summary

- ✅ ChromeTabbedWindow integrates seamlessly with VFWidgets theme system
- ✅ Automatic color adaptation from theme
- ✅ Dynamic theme switching support
- ✅ Graceful fallback to Chrome colors when theme unavailable
- ✅ Works in both top-level and embedded modes
- ✅ VS Code theme compatibility
- ✅ Comprehensive test coverage

For complete examples, see:
- `examples/04_themed_chrome_tabs.py` - Basic theme integration
- `examples/05_themed_chrome_embedded.py` - Embedded mode with theming
- `tests/test_theme_integration.py` - Theme integration tests
