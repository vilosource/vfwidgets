# Theme Overlay System - Migration Guide

**Version**: 2.0.0
**Audience**: Application developers upgrading to vfwidgets-theme v2.0.0
**Difficulty**: Easy (backward compatible)

## Overview

The Theme Overlay System (v2.0.0) adds runtime color customization to vfwidgets-theme. This guide shows how to adopt the new features in existing applications.

**Good News**: v2.0.0 is fully backward compatible - no migration required!

## Should You Migrate?

### Keep Using ThemedApplication If:
- ✅ Your app doesn't need runtime color customization
- ✅ Your app doesn't need persistent user preferences for colors
- ✅ You're happy with theme files for all customization

### Migrate to Overlay System If:
- ✅ You want to override specific colors without modifying theme files
- ✅ You want to provide branding that works across all themes
- ✅ You want users to customize colors (with or without restrictions)
- ✅ You want automatic persistence of color preferences

## Migration Paths

### Path 1: No Migration (Continue Using ThemedApplication)

**Best for**: Applications that don't need color customization

**Action Required**: None!

**Your current code continues to work**:
```python
from vfwidgets_theme import ThemedApplication

app = ThemedApplication(sys.argv)
app.set_theme("dark")
```

---

### Path 2: Add Runtime Overrides (Keep ThemedApplication)

**Best for**: Applications that need occasional color tweaks

**Action Required**: Use ThemeManager overlay methods directly

**Before** (v1.x):
```python
from vfwidgets_theme import ThemedApplication

app = ThemedApplication(sys.argv)
app.set_theme("dark")
# No way to override individual colors
```

**After** (v2.0.0):
```python
from vfwidgets_theme import ThemedApplication
from vfwidgets_theme.core.manager import ThemeManager

app = ThemedApplication(sys.argv)
app.set_theme("dark")

# NEW: Override specific colors at runtime
manager = ThemeManager.get_instance()
manager.set_app_override("editor.background", "#1e1e2e")
manager.set_app_override("tab.activeBackground", "#89b4fa")
```

**Benefits**:
- Minimal code changes
- Runtime color customization
- Works with existing ThemedApplication

**Limitations**:
- No automatic persistence
- No declarative configuration
- Must manually call ThemeManager methods

---

### Path 3: Migrate to VFThemedApplication (Recommended for New Features)

**Best for**: Applications that want branding or user customization with persistence

#### Step 1: Import VFThemedApplication

**Before**:
```python
from vfwidgets_theme import ThemedApplication
```

**After**:
```python
from vfwidgets_theme.widgets import VFThemedApplication
```

#### Step 2: Create Subclass with theme_config

**Before**:
```python
app = ThemedApplication(sys.argv)
app.set_theme("dark")

# Manual theme persistence
settings = QSettings("MyOrg", "MyApp")
saved_theme = settings.value("theme/current")
if saved_theme:
    app.set_theme(saved_theme)
```

**After**:
```python
class MyApp(VFThemedApplication):
    theme_config = {
        "base_theme": "dark",
        "app_overrides": {
            # Your brand colors (optional)
            "tab.activeBackground": "#7c3aed",  # Purple brand
            "statusBar.background": "#14b8a6",  # Teal brand
        },
        "persist_base_theme": True,  # Auto-save theme selection
        "persist_user_overrides": True,  # Auto-save user customizations
    }

app = MyApp(sys.argv)
# Theme automatically loads from saved preferences!
# No manual QSettings code needed
```

**Benefits**:
- ✅ Declarative configuration
- ✅ Automatic persistence (no manual QSettings)
- ✅ Clean, class-based API
- ✅ Branding support
- ✅ User customization support

#### Step 3: Migrate Manual Persistence (If Applicable)

**Before** (manual theme persistence):
```python
# Load theme
settings = QSettings("MyOrg", "MyApp")
saved_theme = settings.value("theme/current")
if saved_theme:
    app.set_theme(saved_theme)

# Save theme (in preferences dialog)
def on_theme_changed(theme_name):
    settings = QSettings("MyOrg", "MyApp")
    settings.setValue("theme/current", theme_name)
    app.set_theme(theme_name)
```

**After** (automatic with VFThemedApplication):
```python
class MyApp(VFThemedApplication):
    theme_config = {
        "base_theme": "dark",
        "persist_base_theme": True,  # Automatic!
        "settings_key_prefix": "theme/",  # Customize if needed
    }

app = MyApp(sys.argv, app_id="MyApp")  # Provide app_id for QSettings
# Theme loads automatically from QSettings

# Save theme (in preferences dialog)
def on_theme_changed(theme_name):
    app.set_theme(theme_name)  # Automatically persists!
```

**QSettings Key Migration**:

VFThemedApplication uses these QSettings keys by default:
- `theme/base_theme` - Current theme name
- `theme/user_overrides` - User color customizations

If your app uses different keys (e.g., `theme/current`), you have two options:

**Option A: Use New Keys** (recommended)
```python
# Let VFThemedApplication use new keys
# Old preferences will be ignored (users reset their theme once)
class MyApp(VFThemedApplication):
    theme_config = {
        "base_theme": "dark",  # Default for new users
        "persist_base_theme": True,
    }
```

**Option B: Migrate Old Keys** (preserve user preferences)
```python
# One-time migration in __init__
class MyApp(VFThemedApplication):
    def __init__(self, argv):
        # Migrate old settings before super().__init__
        from PySide6.QtCore import QSettings
        settings = QSettings("MyOrg", "MyApp")

        old_theme = settings.value("theme/current")
        if old_theme and not settings.value("theme/base_theme"):
            # Migrate old key to new key
            settings.setValue("theme/base_theme", old_theme)
            settings.remove("theme/current")  # Optional: remove old key

        super().__init__(argv, app_id="MyApp")
```

---

### Path 4: Add User Customization

**Best for**: Applications that want to let users customize colors

**Add customization support**:

```python
class CustomizableApp(VFThemedApplication):
    theme_config = {
        "base_theme": "dark",
        "allow_user_customization": True,

        # Define which tokens users can customize (optional)
        "customizable_tokens": [
            "editor.background",
            "editor.foreground",
            "editor.selectionBackground",
        ],
        # Empty list = all tokens customizable

        "persist_user_overrides": True,  # Save user choices
    }

app = CustomizableApp(sys.argv, app_id="MyApp")

# In your preferences dialog
def on_customize_color(token, color):
    """User clicks "Customize Color" button"""
    if app.is_token_customizable(token):
        app.customize_color(token, color, persist=True)

def on_reset_color(token):
    """User clicks "Reset to Default" button"""
    app.reset_color(token, persist=True)

def on_reset_all():
    """User clicks "Reset All" button"""
    app.clear_user_preferences()
```

---

### Path 5: Use with configure_desktop()

**Best for**: Applications using vfwidgets_common.desktop integration

**Before**:
```python
from vfwidgets_common.desktop import configure_desktop
from vfwidgets_theme import ThemedApplication

app = configure_desktop(
    app_name="myapp",
    app_display_name="My App",
    icon_name="myapp",
    application_class=ThemedApplication,
)
```

**After**:
```python
from vfwidgets_common.desktop import configure_desktop
from vfwidgets_theme.widgets import VFThemedApplication

# Define your app class first
class MyApp(VFThemedApplication):
    theme_config = {
        "base_theme": "dark",
        "app_overrides": {
            "tab.activeBackground": "#7c3aed",
        },
    }

# Pass to configure_desktop
app = configure_desktop(
    app_name="myapp",
    app_display_name="My App",
    icon_name="myapp",
    application_class=MyApp,  # Use your subclass
)
```

---

## Common Migration Scenarios

### Scenario 1: Adding Brand Colors

**Goal**: Override specific colors across all themes for branding

**Solution**: Use VFThemedApplication with app_overrides

```python
class BrandedApp(VFThemedApplication):
    theme_config = {
        "base_theme": "dark",
        "app_overrides": {
            # Brand colors that work on all themes
            "tab.activeBackground": "#7c3aed",  # Purple accent
            "statusBar.background": "#14b8a6",  # Teal status bar
            "button.hoverBackground": "#7c3aed",  # Purple hover
        },
    }

app = BrandedApp(sys.argv, app_id="MyBrandedApp")
```

Users can still switch between dark/light themes - your brand colors persist!

### Scenario 2: Adding a Color Picker Dialog

**Goal**: Let users customize specific colors

**Solution**: Use VFThemedApplication.customize_color()

```python
from PySide6.QtWidgets import QColorDialog
from PySide6.QtGui import QColor

class MyPreferencesDialog(QDialog):
    def on_customize_editor_background(self):
        """User clicks "Customize Background" button"""
        app = VFThemedApplication.instance()

        # Get current color
        manager = ThemeManager.get_instance()
        current = manager.get_effective_color("editor.background", "#1e1e2e")

        # Show color picker
        color = QColorDialog.getColor(QColor(current), self, "Choose Background Color")

        if color.isValid():
            # Apply and save
            app.customize_color("editor.background", color.name(), persist=True)
            QMessageBox.information(self, "Success", "Color saved!")
```

### Scenario 3: Migrating Existing Theme Persistence

**Goal**: Preserve user's existing theme selection

**Solution**: One-time migration in __init__

```python
class MyApp(VFThemedApplication):
    def __init__(self, argv):
        # Migrate old QSettings keys before initialization
        from PySide6.QtCore import QSettings
        settings = QSettings("MyOrg", "MyApp")

        # Check for old theme setting
        old_theme_key = "appearance/theme"  # Your old key
        new_theme_key = "theme/base_theme"  # VFThemedApplication key

        old_theme = settings.value(old_theme_key)
        new_theme = settings.value(new_theme_key)

        if old_theme and not new_theme:
            # Migrate: copy old to new
            settings.setValue(new_theme_key, old_theme)
            print(f"Migrated theme preference: {old_theme}")

        # Initialize with automatic persistence
        super().__init__(argv, app_id="MyApp")
```

### Scenario 4: Advanced - Custom Persistence Backend

**Goal**: Use custom storage instead of QSettings

**Solution**: Override persistence methods

```python
import json
from pathlib import Path

class CustomPersistenceApp(VFThemedApplication):
    theme_config = {
        "base_theme": "dark",
        "persist_user_overrides": False,  # Disable QSettings
    }

    def __init__(self, argv):
        super().__init__(argv)
        # Load from custom backend
        self._load_custom_preferences()

    def _load_custom_preferences(self):
        """Load from JSON file instead of QSettings"""
        config_file = Path.home() / ".myapp" / "preferences.json"
        if config_file.exists():
            with open(config_file) as f:
                data = json.load(f)

            # Apply user overrides
            user_overrides = data.get("color_overrides", {})
            if user_overrides:
                manager = ThemeManager.get_instance()
                manager.set_user_overrides_bulk(user_overrides)

    def save_user_preferences(self, overrides=None):
        """Save to JSON file instead of QSettings"""
        if overrides is None:
            manager = ThemeManager.get_instance()
            overrides = manager.get_user_overrides()

        config_file = Path.home() / ".myapp" / "preferences.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing, update, save
        data = {}
        if config_file.exists():
            with open(config_file) as f:
                data = json.load(f)

        data["color_overrides"] = overrides

        with open(config_file, 'w') as f:
            json.dump(data, f, indent=2)
```

---

## Testing Your Migration

### Checklist

After migration, verify:

- [ ] Application starts successfully
- [ ] Theme loads correctly (check saved preferences)
- [ ] Theme switching still works
- [ ] Color overrides appear correctly
- [ ] Preferences persist across restarts
- [ ] User customization works (if applicable)
- [ ] No regressions in existing functionality

### Manual Testing

1. **Start fresh**: Delete QSettings, start app, verify defaults
2. **Change theme**: Switch theme, restart, verify persistence
3. **Customize colors**: Change colors, restart, verify persistence
4. **Reset**: Clear customizations, verify return to defaults

### Automated Testing

```python
import pytest
from PySide6.QtCore import QSettings

def test_theme_persistence(qapp, tmp_path, monkeypatch):
    """Test theme persistence with VFThemedApplication"""
    # Mock QSettings to use temp file
    settings_file = tmp_path / "settings.ini"

    original_init = QSettings.__init__
    def mock_init(self, *args, **kwargs):
        original_init(self, str(settings_file), QSettings.Format.IniFormat)
    monkeypatch.setattr(QSettings, "__init__", mock_init)

    # Create app with default theme
    class TestApp(VFThemedApplication):
        theme_config = {"base_theme": "dark", "persist_base_theme": True}

    # First run: app uses default
    # Second run: app loads saved preference
    # Verify QSettings contains expected data
    ...
```

---

## Examples

See the `examples/` directory for complete working examples:

- **examples/16_simple_overlay.py** - Basic runtime overrides
- **examples/17_branded_app.py** - VFThemedApplication with branding
- **examples/18_customizable_app.py** - User customization with restrictions
- **examples/19_advanced_manual.py** - Advanced ThemeManager API

---

## FAQ

### Q: Do I need to migrate immediately?
**A**: No! v2.0.0 is backward compatible. Migrate when you need the new features.

### Q: Will my existing themes still work?
**A**: Yes! Theme files are unchanged. Overlays work on top of existing themes.

### Q: Can I use both ThemedApplication and overlays?
**A**: Yes! Use ThemeManager methods directly with ThemedApplication.

### Q: What if I'm using a custom QApplication subclass?
**A**: VFThemedApplication extends ThemedApplication which extends QApplication. You may need to refactor to use composition or multiple inheritance carefully.

### Q: How do I test the overlay system?
**A**: Run the examples: `python examples/17_branded_app.py`

### Q: Where are user preferences stored?
**A**: QSettings, typically in:
- Linux: `~/.config/YourOrg/YourApp.conf`
- macOS: `~/Library/Preferences/com.YourOrg.YourApp.plist`
- Windows: Registry under `HKEY_CURRENT_USER\Software\YourOrg\YourApp`

---

## Getting Help

- **Documentation**: `docs/overlay-system-specification.md`
- **Examples**: `examples/16-19_*.py`
- **Tests**: `tests/test_overlay_system/`
- **Issues**: GitHub issues for vfwidgets

---

## Summary

**Easiest Migration**: No changes required - existing code works!

**Recommended Migration for New Features**:
1. Change `ThemedApplication` → `VFThemedApplication`
2. Add `theme_config` class attribute
3. Remove manual QSettings persistence code
4. Test and enjoy automatic features!

**v2.0.0 is fully backward compatible - migrate at your own pace!**
