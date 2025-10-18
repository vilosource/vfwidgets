# Breaking Changes

This document tracks breaking changes across versions of vfwidgets-theme-system.

## v2.0.0 - Theme Overlay System (2025-10-18)

### ✅ NO BREAKING CHANGES

**v2.0.0 is fully backward compatible!**

The Theme Overlay System is a purely additive feature. All existing code continues to work without modification.

### New Features (Non-Breaking)

#### 1. OverrideRegistry (Internal)
New internal class for managing layered color overrides. Not typically used directly.

**File**: `src/vfwidgets_theme/core/override_registry.py`

#### 2. ThemeManager - New Overlay Methods
Added 11 new methods to ThemeManager for runtime color customization:

```python
# Single override operations
manager.set_app_override(token: str, color: str)
manager.set_user_override(token: str, color: str)
manager.remove_app_override(token: str) -> bool
manager.remove_user_override(token: str) -> bool

# Bulk operations
manager.set_app_overrides_bulk(overrides: Dict[str, str])
manager.set_user_overrides_bulk(overrides: Dict[str, str])
manager.clear_app_overrides() -> int
manager.clear_user_overrides() -> int

# Introspection
manager.get_app_overrides() -> Dict[str, str]
manager.get_user_overrides() -> Dict[str, str]
manager.get_all_effective_overrides() -> Dict[str, str]
manager.get_effective_color(token: str, fallback: Optional[str] = None) -> Optional[str]
```

**Existing Methods**: All existing ThemeManager methods continue to work unchanged.

#### 3. VFThemedApplication - New Class
New application class extending ThemedApplication with declarative theme configuration:

```python
from vfwidgets_theme.widgets import VFThemedApplication

class MyApp(VFThemedApplication):
    theme_config = {
        "base_theme": "dark",
        "app_overrides": {...},
        "allow_user_customization": True,
        "customizable_tokens": [...],
        "persist_user_overrides": True,
    }
```

**Existing Code**: Applications using ThemedApplication continue to work unchanged.

#### 4. Color Token Resolution - Enhanced Behavior
`ColorTokenRegistry.get()` now checks ThemeManager overrides before theme defaults:

**Resolution Order** (v2.0.0):
1. ThemeManager user overrides (NEW)
2. ThemeManager app overrides (NEW)
3. Theme-defined color
4. Registry default for dark/light
5. Smart heuristic fallback

**Impact**: Widgets automatically see color overrides without code changes.

**Backward Compatibility**: If no overrides are set, behavior is identical to v1.x.

### Migration Guide

**No migration required!** Existing applications work as-is.

#### To Add Runtime Color Customization

**Option 1: Use ThemeManager directly (existing apps)**
```python
from vfwidgets_theme.core.manager import ThemeManager

manager = ThemeManager.get_instance()
manager.set_app_override("editor.background", "#1e1e2e")
```

**Option 2: Use VFThemedApplication (new apps)**
```python
from vfwidgets_theme.widgets import VFThemedApplication

class BrandedApp(VFThemedApplication):
    theme_config = {
        "base_theme": "dark",
        "app_overrides": {
            "editor.background": "#1e1e2e",
        },
    }

app = BrandedApp(sys.argv)
```

**Option 3: Use configure_desktop with VFThemedApplication**
```python
from vfwidgets_common.desktop import configure_desktop
from vfwidgets_theme.widgets import VFThemedApplication

app = configure_desktop(
    app_name="myapp",
    app_display_name="My App",
    icon_name="myapp",
    application_class=VFThemedApplication,
)
```

### Examples

Four comprehensive examples demonstrate the overlay system:
- `examples/16_simple_overlay.py` - Basic runtime overrides
- `examples/17_branded_app.py` - Declarative branding
- `examples/18_customizable_app.py` - User customization
- `examples/19_advanced_manual.py` - Advanced API usage

### Testing

**Test Coverage**: 53/53 tests passing
- OverrideRegistry: 32 tests
- VFThemedApplication: 21 tests

### Known Limitations

1. **QColor Validation**: Uses deprecated `QColor.isValidColor()`
   - Limitation: Doesn't support `rgb()` color format
   - Workaround: Use hex colors (`#rrggbb`) or named colors (`red`, `blue`)

2. **QSettings Key Naming**: VFThemedApplication uses `"theme/"` prefix by default
   - Can be customized via `theme_config["settings_key_prefix"]`
   - May differ from existing manual persistence implementations

### Deprecations

**None**. No APIs were deprecated in v2.0.0.

---

## v1.x - Previous Versions

### v1.0.0 (Initial Release)
- Initial theme system implementation
- ThemedWidget, ThemedApplication
- Basic theme loading and switching
- VSCode theme import

No breaking changes documented for v1.x series.

---

## Future Versions

### Planned for v2.1.0
- Performance benchmarks and optimizations
- Enhanced color validation (replace deprecated QColor)
- Additional persistence backends

### Planned for v3.0.0 (Breaking)
TBD - No breaking changes currently planned
