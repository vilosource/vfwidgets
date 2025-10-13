# ViloxTerm Theme Integration

**Status**: Implemented
**Version**: 1.2.0+
**Last Updated**: 2025-10-13

## Overview

ViloxTerm terminals automatically follow the application theme via ThemedWidget inheritance. This provides seamless, automatic theme propagation without any manual theme management code.

### Key Benefits

- **Automatic**: Terminals inherit theme from ThemedApplication
- **Simple**: No theme management code needed
- **Consistent**: All widgets use same theme system
- **Fast**: Theme changes propagate instantly (<100ms)
- **Reliable**: No theme synchronization bugs

### Architecture Change

**Old Approach** (v1.0-1.1):
```
TerminalThemeManager → set_terminal_theme() → Terminal updates
```

**New Approach** (v1.2+):
```
ThemedApplication.set_theme() → ThemedWidget.on_theme_changed() → Terminal updates
```

## Hierarchical Token System

Terminals use a hierarchical token resolution system for colors:

### Token Resolution Order

1. **Widget-specific** (optional): `terminal.colors.<token>`
2. **Base** (required): `colors.<token>`

### Example

```json
{
  "colors": {
    "colors.background": "#1e1e1e",
    "colors.foreground": "#d4d4d4",
    "colors.border": "#333333",

    "terminal.colors.background": "#1a1a1a",
    "terminal.colors.foreground": "#cccccc"
  }
}
```

If `terminal.colors.background` is missing, falls back to `colors.background`.

### Required Tokens

These base tokens **MUST** exist in every theme (application exits if missing):

- `colors.background` - Base background color
- `colors.foreground` - Base foreground/text color
- `colors.border` - Base border color

### Terminal-Specific Tokens

These tokens customize terminal appearance (all optional):

**Core Colors**:
- `terminal.colors.background` - Terminal background
- `terminal.colors.foreground` - Terminal text
- `terminal.colors.cursor` - Cursor color
- `terminal.colors.cursorAccent` - Cursor background
- `terminal.colors.selectionBackground` - Selection highlight

**ANSI Colors**:
- `terminal.colors.ansiBlack` through `terminal.colors.ansiWhite`
- `terminal.colors.ansiBrightBlack` through `terminal.colors.ansiBrightWhite`

### Built-in Theme Support

All VFWidgets themes include complete terminal color definitions:

- `widgets/theme_system/themes/dark-default.json`
- `widgets/theme_system/themes/light-default.json`
- `widgets/theme_system/themes/high-contrast.json`

## How It Works

### Application Startup

```python
# __main__.py
from vfwidgets_theme import ThemedApplication

app = configure_desktop(
    app_name="viloxterm",
    application_class=ThemedApplication,
    theme_config={"persist_theme": True}
)

# Load theme (either saved or default)
app.set_theme("dark")

# All terminals created after this point inherit the theme
```

### Theme Propagation Flow

```
1. User changes theme (via menu/settings)
   ↓
2. ThemedApplication.set_theme("light")
   ↓
3. Theme system calls on_theme_changed() on all ThemedWidget instances
   ↓
4. TerminalWidget.on_theme_changed()
   - Gets current theme via self.get_current_theme()
   - Resolves colors using hierarchical tokens
   - Builds xterm.js theme dictionary
   - Applies via JavaScript injection
   ↓
5. All terminals update instantly
```

### Terminal Creation

```python
# provider/terminal_provider.py
def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
    # Create terminal - ThemedWidget handles everything
    terminal = TerminalWidget(server_url=session_url)

    # Terminal automatically:
    # - Registers with theme system
    # - Gets current theme
    # - Applies theme on creation
    # - Updates when theme changes

    return terminal
```

No manual theme application needed!

## Customizing Terminal Colors

### Option 1: Modify Built-in Themes

Edit theme files in `widgets/theme_system/themes/`:

```json
{
  "colors": {
    "terminal.colors.background": "#1a1a1a",
    "terminal.colors.ansiRed": "#ff5555",
    "terminal.colors.ansiGreen": "#50fa7b"
  }
}
```

### Option 2: Create Custom Theme

```python
from vfwidgets_theme import Theme

custom_theme = Theme(
    name="My Terminal Theme",
    type="dark",
    colors={
        "colors.background": "#1e1e1e",
        "colors.foreground": "#d4d4d4",
        "colors.border": "#333333",
        "terminal.colors.background": "#0a0a0a",
        "terminal.colors.foreground": "#ffffff",
        # ... more colors
    }
)

# Add to application
app = QApplication.instance()
app._theme_manager.add_theme(custom_theme)
app.set_theme("My Terminal Theme")
```

### Option 3: Runtime Override

```python
# In ViloxTermApp or plugin
def customize_terminal_colors(self):
    # Get current theme
    app = QApplication.instance()
    theme = app.get_current_theme()

    # Modify terminal colors
    new_colors = theme.colors.copy()
    new_colors["terminal.colors.background"] = "#000000"

    # Create modified theme
    custom_theme = Theme(
        name=f"{theme.name} (Custom)",
        type=theme.type,
        colors=new_colors
    )

    # Apply it
    app._theme_manager.add_theme(custom_theme)
    app.set_theme(custom_theme.name)
```

## Migration Guide

### From TerminalThemeManager (v1.0-1.1)

**Old code**:
```python
# app.py
self.terminal_theme_manager = TerminalThemeManager()
default_theme = self.terminal_theme_manager.get_default_theme()
self.terminal_provider.set_default_theme(default_theme)

# terminal_provider.py
if self._default_theme:
    terminal.set_terminal_theme(self._default_theme)
```

**New code**:
```python
# Nothing! ThemedWidget handles everything automatically
```

### Custom Terminal Themes

If you have custom `~/.config/viloxterm/terminal_themes/*.json` files:

1. **Convert to VFWidgets theme format**:
   ```json
   {
     "$schema": "https://vfwidgets.org/schemas/theme-v1.json",
     "name": "My Custom Theme",
     "type": "dark",
     "colors": {
       "colors.background": "#1e1e1e",
       "colors.foreground": "#d4d4d4",
       "colors.border": "#333333",
       "terminal.colors.background": "<your color>",
       "terminal.colors.foreground": "<your color>",
       ...
     }
   }
   ```

2. **Install in VFWidgets theme directory**:
   ```bash
   cp my-theme.json ~/.config/vfwidgets/themes/
   ```

3. **Select via ViloxTerm menu**: Settings → Theme → My Custom Theme

## Troubleshooting

### Terminals not updating when theme changes

**Cause**: Terminal widget not inheriting from ThemedWidget

**Solution**: Verify terminal_widget installation:
```bash
pip install -e ./widgets/terminal_widget
python -c "from vfwidgets_terminal import TerminalWidget; print(TerminalWidget.__bases__)"
# Should include ThemedWidget
```

### White flash on startup

**Cause**: Old terminal widget version without transparent web view

**Solution**: Install latest terminal widget:
```bash
pip install -e ./widgets/terminal_widget --force-reinstall
```

Verify transparent web view in `terminal.py:733-737`:
```python
self.web_view.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
self.web_view.setStyleSheet("background: transparent")
self.web_view.page().setBackgroundColor(Qt.GlobalColor.transparent)
```

### Missing colors / validation errors

**Error**: `CRITICAL: Required token 'colors.background' not found!`

**Cause**: Theme missing required base tokens

**Solution**: Ensure theme has all required tokens:
```json
{
  "colors": {
    "colors.background": "#1e1e1e",
    "colors.foreground": "#d4d4d4",
    "colors.border": "#333333"
  }
}
```

### Terminals using wrong colors

**Debug**:
```bash
# Check terminal logs
viloxterm 2>&1 | grep "Terminal using base"

# Should see:
# [INFO] Terminal using base colors.* for 21 tokens
# [INFO] Terminal page background: #1e1e1e
```

**Solution**: Verify theme tokens are correctly defined in theme JSON

## API Reference

### TerminalWidget

```python
class TerminalWidget(ThemedWidget, QWidget):
    """Terminal widget with automatic theme integration.

    Automatically inherits theme from ThemedApplication.
    No manual theme management needed.
    """

    def on_theme_changed(self, theme=None) -> None:
        """Called automatically when theme changes.

        Builds xterm.js theme using hierarchical token resolution:
        1. Try terminal.colors.<token> (widget-specific)
        2. Fall back to colors.<token> (base)
        3. Exit if required base token missing
        """
```

### Token Resolution

```python
def _get_color_with_fallback(token_name: str, theme=None) -> str:
    """Get color with hierarchical fallback.

    Args:
        token_name: Token without namespace (e.g., "background")
        theme: Optional theme object

    Returns:
        Color hex value (e.g., "#1e1e1e")

    Resolution order:
        1. terminal.colors.{token_name}
        2. colors.{token_name}
        3. SystemExit if required token missing
    """
```

## Performance

- **Theme switch time**: <100ms for 100 terminals
- **Memory overhead**: ~1KB per terminal for theme data
- **Startup impact**: Negligible (theme cached)

## Architecture Diagram

```
┌─────────────────────────────────────┐
│     ThemedApplication              │
│  (Manages app-wide theme)          │
└──────────────┬──────────────────────┘
               │ theme_changed signal
               ↓
┌─────────────────────────────────────┐
│     LifecycleManager                │
│  (Propagates to all widgets)        │
└──────────────┬──────────────────────┘
               │ calls on_theme_changed()
               ↓
┌─────────────────────────────────────┐
│     ThemedWidget (base class)       │
│  - Auto-registers with theme system │
│  - Provides get_current_theme()     │
│  - Calls on_theme_changed()         │
└──────────────┬──────────────────────┘
               │ inherits
               ↓
┌─────────────────────────────────────┐
│     TerminalWidget                  │
│  - Implements on_theme_changed()    │
│  - Resolves hierarchical tokens     │
│  - Applies to xterm.js              │
└─────────────────────────────────────┘
```

## See Also

- [Terminal Widget Documentation](../../../widgets/terminal_widget/README.md)
- [Theme System Documentation](../../../widgets/theme_system/README.md)
- [VFWidgets Theme Specification](../../../widgets/theme_system/docs/theme-specification.md)

## Changelog

### v1.2.0 (2025-10-13)
- ✅ Migrated to ThemedWidget-based theme integration
- ✅ Removed TerminalThemeManager (deprecated)
- ✅ Implemented hierarchical token system
- ✅ Added transparent web view (no white flash)
- ✅ Automatic theme propagation

### v1.1.x
- Legacy TerminalThemeManager approach

### v1.0.x
- Initial terminal theming
