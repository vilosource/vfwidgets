# VFWidgets Theme System Guide

**Complete guide to theme management, customization, and architecture**

---

## Table of Contents

- [Overview](#overview)
- [Theme Discovery](#theme-discovery)
- [Theme Priority](#theme-priority)
- [Creating Custom Themes](#creating-custom-themes)
- [Theme Persistence](#theme-persistence)
- [Theme Aliasing](#theme-aliasing)
- [Architecture](#architecture)
- [Troubleshooting](#troubleshooting)

---

## Overview

The VFWidgets Theme System provides professional theme management for PySide6/Qt applications with:

- **Automatic theme discovery** - No manual theme loading required
- **Three-tier priority system** - User > Package > Built-in themes
- **Theme aliasing** - Multiple names can reference the same theme
- **Automatic persistence** - Theme preferences saved and restored
- **200+ color tokens** - Comprehensive UI coverage
- **Hot reloading** - Changes reflected immediately (optional)

---

## Theme Discovery

### Automatic Discovery

The theme system automatically discovers themes from three locations on startup:

#### 1. Built-in Themes (Lowest Priority)

Hardcoded Python themes in `vfwidgets_theme.core.repository`:

```python
{
    "minimal": "Safe fallback theme",
    "default": "Microsoft-inspired light theme",
    "dark": "GitHub-inspired dark theme",
    "light": "High contrast light theme"
}
```

**Location:** `vfwidgets_theme/core/repository.py` (BuiltinThemeManager)
**Format:** Python dictionaries
**Token style:** Namespaced (`colors.foreground`, `colors.background`)

#### 2. Package Themes (Medium Priority)

JSON themes shipped with the package:

```
widgets/theme_system/themes/
├── dark-default.json      # Comprehensive dark theme (116 tokens)
├── light-default.json     # Comprehensive light theme (116 tokens)
└── high-contrast.json     # Accessibility theme
```

**Discovery:** Automatic on `ThemeRepository.__init__()`
**Format:** JSON files (`.json`, `.yaml`, `.yml`)
**Token style:** Non-namespaced (`icon.foreground`, `focusBorder`)

#### 3. User Custom Themes (Highest Priority)

User-created themes in standard config directories:

```
~/.config/ViloxTerm/themes/
├── vscode-dark.json
├── my-custom-theme.json
└── solarized-dark.json

~/.vfwidgets/themes/
├── custom-light.json
└── another-theme.json
```

**Discovery:** Automatic on `ThemeRepository.__init__()`
**Format:** JSON files (`.json`, `.yaml`, `.yml`)
**Token style:** Any (system handles both)

### Discovery Process

```python
# On ThemeRepository initialization:
1. _load_builtin_themes()      # Load built-in Python themes
2. _discover_package_themes()  # Auto-discover package JSON themes
3. _discover_user_themes()     # Auto-discover user custom themes
```

**Key Code:** `repository.py:548-553`

---

## Theme Priority

When multiple themes exist with the same name, the system uses this priority:

```
User Themes (Highest)
    ↓
Package Themes
    ↓
Built-in Themes (Lowest)
```

### Example

If you have:
- Built-in theme: `dark` (Python)
- Package theme: `dark-default.json`
- User theme: `dark.json` in `~/.config/ViloxTerm/themes/`

```python
app.set_theme("dark")
# Loads: User's dark.json (if exists)
# Falls back to: Built-in dark theme
```

**Implementation:** Themes loaded in order, later ones override earlier ones with same name.

---

## Creating Custom Themes

### Theme File Structure

```json
{
  "name": "My Custom Theme",
  "type": "dark",
  "version": "1.0.0",
  "metadata": {
    "author": "Your Name",
    "description": "My custom theme description"
  },
  "colors": {
    "window.background": "#1e1e1e",
    "window.foreground": "#cccccc",
    "window.border": "#333333",

    "focusBorder": "#007acc",
    "icon.foreground": "#d4d4d4",

    "toolbar.hoverBackground": "rgba(255, 255, 255, 0.1)",
    "toolbar.hoverForeground": "#ffffff",
    "toolbar.activeBackground": "rgba(255, 255, 255, 0.15)",

    "tab.activeBackground": "#1e1e1e",
    "tab.inactiveBackground": "#2d2d30",
    "tab.activeForeground": "#ffffff",
    "tab.inactiveForeground": "#969696",

    "button.background": "#0e639c",
    "button.foreground": "#ffffff",
    "button.hoverBackground": "#1177bb",

    "input.background": "#3c3c3c",
    "input.foreground": "#cccccc",
    "input.border": "#3c3c3c",
    "input.focusBorder": "#007acc",

    "editor.background": "#1e1e1e",
    "editor.foreground": "#d4d4d4"
  }
}
```

### Required Tokens

Minimum tokens for a functional theme:

```json
{
  "colors": {
    "window.background": "#1e1e1e",
    "window.foreground": "#cccccc",
    "focusBorder": "#007acc",
    "icon.foreground": "#d4d4d4"
  }
}
```

**Note:** Missing tokens automatically fall back to defaults.

### Where to Save Custom Themes

**Option 1: Application-specific (Recommended for ViloxTerm)**
```bash
~/.config/ViloxTerm/themes/my-theme.json
```

**Option 2: Global (Shared across all VFWidgets apps)**
```bash
~/.vfwidgets/themes/my-theme.json
```

### Using Your Custom Theme

```python
# Theme is auto-discovered, just use it:
app.set_theme("my-theme")  # Matches filename: my-theme.json

# Or use the full name from JSON:
app.set_theme("My Custom Theme")
```

---

## Theme Persistence

### Automatic Persistence

Enable theme persistence in your application:

```python
from vfwidgets_theme import ThemedApplication

# Enable theme persistence
theme_config = {"persist_theme": True}
app = ThemedApplication(sys.argv, theme_config=theme_config)

# Now theme changes are automatically saved
app.set_theme("dark")  # Saved to ~/.vfwidgets/theme_preference.json
```

### Application-Specific Persistence

For application-specific theme preferences (like ViloxTerm):

```python
from PySide6.QtCore import QSettings
from vfwidgets_theme import ThemedApplication

app = ThemedApplication(sys.argv)

# Load saved theme
settings = QSettings("ViloxTerm", "ViloxTerm")
saved_theme = settings.value("theme/current")

if saved_theme:
    app.set_theme(saved_theme)

# Later, when user changes theme:
def save_theme_preference(theme_name: str):
    settings = QSettings("ViloxTerm", "ViloxTerm")
    settings.setValue("theme/current", theme_name)
    settings.sync()
```

**ViloxTerm Implementation:** `apps/viloxterm/src/viloxterm/__main__.py:52-69`

### Where Preferences are Saved

**VFWidgets Default:**
```
~/.vfwidgets/theme_preference.json
```

**ViloxTerm Specific:**
```
~/.config/ViloxTerm/ViloxTerm.conf
[theme]
current=vscode-dark
```

---

## Theme Aliasing

Multiple names can reference the same theme:

### Automatic Aliases

The system automatically creates aliases for package themes:

```python
# File: dark-default.json
# Auto-creates alias: "dark-default" → "Dark Default" (from name field)

app.set_theme("dark-default")     # Works
app.set_theme("Dark Default")      # Also works (actual theme name)
```

### Manual Aliases

```python
from vfwidgets_theme.core.repository import ThemeRepository

repo = ThemeRepository()

# Add custom alias
repo.add_alias("my-dark", "dark-default")

# Now both work:
app.set_theme("dark-default")  # Original
app.set_theme("my-dark")       # Alias
```

### Use Cases

- **Backwards compatibility:** Keep old theme names working
- **Convenience:** Short aliases for long theme names
- **Migration:** Gradual theme name changes

---

## Architecture

### Component Overview

```
ThemeRepository (core/repository.py)
├── BuiltinThemeManager      # Built-in Python themes
├── ThemeDiscovery           # Auto-discovery service
├── FileThemeLoader          # Load JSON/YAML themes
├── ThemeCache               # Performance optimization
└── Alias System             # Theme name aliasing
```

### Data Flow

```
Application Startup
        ↓
ThemeRepository.__init__()
        ↓
    ┌───┴───┐
    │       │
Load      Discover
Built-in   Themes
Themes        ↓
    │    ┌───┴───┐
    │    │       │
    │  Package  User
    │  Themes   Themes
    │    │       │
    └────┴───┬───┘
             ↓
      Theme Registry
             ↓
    app.set_theme()
             ↓
      Apply to Widgets
```

### Key Classes

**ThemeRepository** (`repository.py:510-848`)
- Central theme storage and retrieval
- Handles discovery, caching, and aliases
- Thread-safe operations

**ThemeDiscovery** (`repository.py:449-508`)
- Scans directories for theme files
- Supports recursive scanning
- Handles multiple file formats

**FileThemeLoader** (`repository.py:155-251`)
- Loads JSON/YAML theme files
- Validates theme data
- Error handling and recovery

**BuiltinThemeManager** (`repository.py:253-447`)
- Manages hardcoded Python themes
- Provides fallback themes
- Namespaced token support

### Discovery Implementation

```python
def _discover_package_themes(self) -> None:
    """Auto-discover and load themes from package themes directory."""
    # Find: widgets/theme_system/themes/
    package_dir = Path(__file__).parent.parent.parent.parent / "themes"

    if package_dir.exists():
        themes = self._discovery.discover_in_directory(package_dir)
        for theme in themes:
            self._themes[theme.name] = theme  # Package themes override built-in

def _discover_user_themes(self) -> None:
    """Auto-discover and load themes from user theme directories."""
    user_theme_dirs = [
        Path.home() / ".config" / "ViloxTerm" / "themes",
        Path.home() / ".vfwidgets" / "themes",
    ]

    for theme_dir in user_theme_dirs:
        if theme_dir.exists():
            themes = self._discovery.discover_in_directory(theme_dir)
            for theme in themes:
                self._themes[theme.name] = theme  # User themes override all
```

**Code Reference:** `repository.py:575-641`

---

## Troubleshooting

### Theme Not Found

**Problem:** `ThemeNotFoundError: Theme 'my-theme' not found in repository`

**Solutions:**

1. **Check filename matches:**
   ```bash
   ls ~/.config/ViloxTerm/themes/
   # Should see: my-theme.json
   ```

2. **Verify JSON syntax:**
   ```bash
   python -m json.tool ~/.config/ViloxTerm/themes/my-theme.json
   ```

3. **Check theme name field:**
   ```json
   {
     "name": "my-theme"  // Must match or use as alias
   }
   ```

4. **Enable debug logging:**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

### Theme Not Loading

**Problem:** Custom theme exists but defaults to built-in theme

**Solutions:**

1. **Check directory permissions:**
   ```bash
   ls -la ~/.config/ViloxTerm/themes/
   # Should be readable by user
   ```

2. **Verify discovery order:**
   ```python
   from vfwidgets_theme.core.manager import ThemeManager

   mgr = ThemeManager.get_instance()
   print(mgr.list_themes())  # Should include your theme
   ```

3. **Check for JSON errors:**
   - Trailing commas
   - Missing quotes
   - Invalid color formats

### Icons Wrong Color

**Problem:** Window control icons are wrong color (e.g., dark on dark)

**Solution:** Ensure theme includes icon tokens:

```json
{
  "colors": {
    "icon.foreground": "#d4d4d4",       // Required
    "toolbar.hoverBackground": "rgba(255, 255, 255, 0.1)",
    "toolbar.hoverForeground": "#ffffff",
    "toolbar.activeBackground": "rgba(255, 255, 255, 0.15)"
  }
}
```

**Fallback chain:**
```
icon.foreground → colors.foreground → window.foreground → theme-based default
```

### Theme Preference Not Persisting

**Problem:** Theme resets to default on restart

**Solutions:**

1. **Enable persistence:**
   ```python
   theme_config = {"persist_theme": True}
   app = ThemedApplication(sys.argv, theme_config=theme_config)
   ```

2. **Check QSettings save:**
   ```python
   from PySide6.QtCore import QSettings
   settings = QSettings("ViloxTerm", "ViloxTerm")
   print(settings.value("theme/current"))  # Should show saved theme
   ```

3. **Verify ThemeDialog saves:**
   - Check `components/theme_dialog.py:54-63`
   - Ensure `settings.setValue()` is called

### Theme Changes Not Visible

**Problem:** Changed theme but UI doesn't update

**Solutions:**

1. **Complete restart required:**
   - Some changes need full application restart
   - Not just new tab/window

2. **Check cache:**
   ```python
   # Clear theme cache
   from vfwidgets_theme.core.manager import ThemeManager
   mgr = ThemeManager.get_instance()
   mgr._repository._cache.clear()
   ```

3. **Force stylesheet reload:**
   ```python
   widget.setStyleSheet("")
   widget.style().unpolish(widget)
   widget.style().polish(widget)
   ```

---

## Advanced Topics

### Hot Reloading

Enable live theme updates during development:

```python
app = ThemedApplication(sys.argv)

# Enable hot reload with 500ms debounce
app.enable_hot_reload(debounce_ms=500)

# Watch specific theme file
app.watch_theme_file("~/.config/ViloxTerm/themes/my-theme.json")
```

### Theme Validation

Validate theme before using:

```python
from vfwidgets_theme.core.theme import ThemeValidator

validator = ThemeValidator()
result = validator.validate_theme_data(theme_dict)

if not result.is_valid:
    print("Validation errors:", result.errors)
```

### Programmatic Theme Creation

```python
from vfwidgets_theme.core.theme import ThemeBuilder

theme = (ThemeBuilder("my-theme")
    .set_type("dark")
    .add_color("window.background", "#1e1e1e")
    .add_color("window.foreground", "#cccccc")
    .add_color("icon.foreground", "#d4d4d4")
    .build())

# Add to repository
from vfwidgets_theme.core.manager import ThemeManager
mgr = ThemeManager.get_instance()
mgr._repository.add_theme(theme)
```

---

## References

### Code Locations

- **Theme Repository:** `widgets/theme_system/src/vfwidgets_theme/core/repository.py`
- **Theme Manager:** `widgets/theme_system/src/vfwidgets_theme/core/manager.py`
- **Theme Discovery:** `repository.py:449-508`
- **Built-in Themes:** `repository.py:253-447`
- **ViloxTerm Integration:** `apps/viloxterm/src/viloxterm/__main__.py`

### Related Documentation

- [Quick Start Guide](quick-start-GUIDE.md)
- [Theme Customization](theme-customization-GUIDE.md)
- [API Reference](api-REFERENCE.md)
- [Architecture Design](architecture-DESIGN.md)

---

**Last Updated:** 2025-10-07
**Version:** 2.0.0-rc5
