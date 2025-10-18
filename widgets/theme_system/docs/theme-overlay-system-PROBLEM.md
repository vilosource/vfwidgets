# Theme Overlay System - Problem Description & Analysis

**Document Status**: Problem Report & Requirements Analysis
**Date**: 2025-10-18
**Author**: VFWidgets Architecture Team
**Stakeholders**: ViloxTerm, ViloWeb, Reamde, Future Applications

**Related Documents**:
- **Vision**: [theme-customization-system-VISION.md](./theme-customization-system-VISION.md) - Architectural vision and solution
- **Specification**: [theme-overlay-system-SPECIFICATION.md](./theme-overlay-system-SPECIFICATION.md) - Technical implementation spec
- **Breaking Changes**: [BREAKING-CHANGES.md](./BREAKING-CHANGES.md) - Breaking changes tracking
- **Documentation Index**: [README-OVERLAY-SYSTEM.md](./README-OVERLAY-SYSTEM.md) - Navigation guide

---

## Executive Summary

### The Problem

The VFWidgets theme system currently **lacks a runtime color overlay/customization API**, forcing applications to choose between:

1. **No user customization** (accept theme as-is)
2. **Create ephemeral themes** (violates separation of concerns, persistence issues)
3. **Manage theme files** (violates theme system responsibility boundary)

This gap was discovered while implementing **tab bar background color customization** for ViloxTerm, where we found:
- ❌ No API to override specific theme tokens at runtime
- ❌ Creating customized themes works but **doesn't persist across restarts**
- ❌ Applications forced to manage theme lifecycle (violates architecture)
- ❌ No clean separation between "base theme" and "user customizations"

### Impact

**Current Workarounds**:
- Applications create new `Theme` objects with modified colors
- Theme names like "Dark (Custom)" pollute theme repository
- Customizations lost on restart (transient themes)
- Applications must implement their own persistence
- Violates **separation of concerns** principle

**Affected Applications**:
- 🔴 **ViloxTerm**: Needs color overrides for UI customization
- 🟡 **ViloWeb**: May need per-site color schemes (future)
- 🟢 **Reamde**: Currently unaffected (no customization needs)
- 🟢 **Theme Studio**: Intentionally unthemed (preview only)

### Proposed Solution

**Theme Overlay System**: Add runtime color/font override API to theme system.

```python
# Application code
theme_mgr = ThemeManager.get_instance()
theme_mgr.set_color_override("editorGroupHeader.tabsBackground", "#ff0000")

# Persist overrides (application's responsibility)
save_to_prefs({"color_overrides": theme_mgr.get_overrides()})

# On restart
for token, value in load_from_prefs()["color_overrides"].items():
    theme_mgr.set_color_override(token, value)
```

**Benefits**:
- ✅ Clean separation: Apps own UI & persistence, theme system owns theming
- ✅ Overrides apply to ANY base theme
- ✅ No ephemeral theme objects
- ✅ No theme repository pollution
- ✅ Reusable across all applications

---

## Current State: How Applications Use Themes

### Overview

**Theme System Architecture**:
```
┌─────────────────────────────────────────────┐
│ ThemedApplication                            │
│  ├─ set_theme(name_or_theme)                │
│  ├─ get_current_theme() → Theme            │
│  └─ theme_changed signal                    │
└─────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────┐
│ ThemeManager (singleton)                     │
│  ├─ Repository: Built-in & loaded themes    │
│  ├─ Applicator: Apply to widgets            │
│  ├─ Notifier: Signal widgets                │
│  └─ Provider: Theme data access              │
└─────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────┐
│ ThemedWidget instances                       │
│  ├─ Automatically registered                 │
│  ├─ _on_theme_changed() callback            │
│  └─ Auto-update on theme switch             │
└─────────────────────────────────────────────┘
```

### Application 1: ViloxTerm

**Type**: Feature-rich terminal emulator
**Theme Usage**: Advanced (theme selection + wants customization)

**Current Implementation**:

```python
# File: apps/viloxterm/src/viloxterm/__main__.py
def main():
    app = ThemedApplication(sys.argv)

    # Load saved theme preference
    settings = QSettings("ViloxTerm", "ViloxTerm")
    saved_theme = settings.value("theme/current")  # e.g., "dark"

    if saved_theme:
        app.set_theme(saved_theme)  # ← Uses theme system API
    else:
        app.set_theme("dark")  # Default
```

**Preferences System**:

```python
# File: apps/viloxterm/src/viloxterm/models/preferences_model.py
@dataclass
class AppearancePreferences:
    # Theme selection
    application_theme: str = "dark"  # User-selected base theme
    sync_with_system: bool = False
    custom_theme_path: str = ""  # Path to custom .json theme

    # UI customization (NO THEME API FOR THIS!)
    focus_border_color: str = ""  # Color override (currently unused)
    # ... wants to add: tab_bar_background_color
```

**Theme Dialog** (apps/viloxterm/src/viloxterm/components/theme_dialog.py):

```python
def select_theme(self, theme_name: str):
    app = QApplication.instance()
    app.set_theme(theme_name)  # ← Uses theme system

    # Persist to ViloxTerm config
    settings = QSettings("ViloxTerm", "ViloxTerm")
    settings.setValue("theme/current", theme_name)
```

**Desired Feature** (not yet implemented):

```python
# User wants to customize tab bar background color
# Current problem: NO API to do this!

# What we WANT to do:
preferences.tab_bar_background_color = "#ff0000"

# How do we apply this?
# Option 1: Create ephemeral theme (CURRENT PLAN, PROBLEMATIC)
# Option 2: Theme overlay system (PROPOSED SOLUTION)
```

**Issues**:
1. ❌ No way to override specific colors without creating new theme
2. ❌ `focus_border_color` preference exists but has no theme API
3. ❌ Would need to create "Dark (Custom)" theme → persistence problem

---

### Application 2: ViloWeb

**Type**: Educational web browser
**Theme Usage**: Basic (hardcoded dark theme)

**Current Implementation**:

```python
# File: apps/viloweb/src/viloweb/application.py
class ViloWebApplication:
    def __init__(self):
        if THEME_AVAILABLE:
            self._qapp = ThemedApplication(sys.argv)
            self._setup_theme()
        else:
            self._qapp = QApplication(sys.argv)

    def _setup_theme(self):
        # Defensive multi-method theme loading
        try:
            # Method 1: Built-in themes (newer API)
            from vfwidgets_theme.importers import load_builtin_theme
            theme = load_builtin_theme("dark")
            self._qapp.set_theme(theme)
            return
        except (ImportError, AttributeError):
            pass

        try:
            # Method 2: Theme repository (older API)
            self._qapp.set_theme("dark")
            return
        except:
            pass

        # Fallback: No theme (use OS)
```

**Characteristics**:
- ✅ Uses ThemedApplication correctly
- ✅ Defensive API usage (supports multiple versions)
- ❌ NO user theme selection (hardcoded dark)
- ❌ NO preferences for customization

**Future Needs**:
- User theme selection (dark/light toggle)
- Potential: Per-website color schemes (advanced)
- Potential: Reader mode custom colors

**Current Blocker**:
- No preferences system yet (educational app, simple by design)
- If adding prefs → would hit same overlay problem as ViloxTerm

---

### Application 3: Reamde

**Type**: Markdown viewer/editor
**Theme Usage**: Basic (prefer dark, no persistence)

**Current Implementation**:

```python
# File: apps/reamde/src/reamde/app.py
class ReamdeApp(SingleInstanceApplication):
    def __init__(self, argv: list[str]):
        setup_logging()

        # SingleInstanceApplication extends ThemedApplication if available
        super().__init__(
            argv,
            app_id="reamde",
            prefer_dark=True  # ← Simple theme preference
        )
```

**SingleInstanceApplication Integration**:

```python
# File: shared/vfwidgets_common/src/vfwidgets_common/single_instance.py
class SingleInstanceApplication(_BaseApp):  # _BaseApp = ThemedApplication if available
    def __init__(self, argv, app_id, prefer_dark=False, theme_config=None):
        # Build theme config from prefer_dark flag
        if prefer_dark and theme_config is None:
            theme_config = {
                "default_theme": "dark",
                "auto_detect_system": False,  # Don't override
                "persist_theme": False,  # Don't persist
            }

        if THEME_AVAILABLE:
            super().__init__(argv, theme_config=theme_config)
        else:
            super().__init__(argv)
```

**Characteristics**:
- ✅ Clean integration via `prefer_dark` flag
- ✅ No persistence (simple app, temporary)
- ✅ No customization UI (intentionally simple)
- ✅ SingleInstanceApplication handles theme config

**Current Needs**: None (satisfied with basic dark theme)

**Future Potential**:
- Preferences dialog → theme selection
- Per-document color schemes (syntax highlighting)
- Would hit overlay problem if adding customization

---

### Application 4: Theme Studio

**Type**: Theme editor/creator
**Theme Usage**: NONE (intentionally unthemed)

**Current Implementation**:

```python
# File: apps/theme-studio/src/theme_studio/app.py
class ThemeStudioApp(QApplication):  # Plain QApplication, NOT ThemedApplication
    """Uses OS/system theme - no custom theming.

    Theme Studio does not apply custom themes to itself - only to preview widgets.
    """

    def __init__(self, argv):
        super().__init__(argv)
        # No theme setup - use OS theme
```

**Rationale**:
- Theme Studio CREATES themes for other apps
- Using custom theme would be confusing (is this the theme I'm editing?)
- OS theme provides neutral, professional look
- Preview widgets show the theme being edited

**Characteristics**:
- ✅ Intentionally does NOT use theme system
- ✅ Correct architecture (meta-tool uses neutral theme)
- ✅ No overlay needs (not a theme consumer)

---

## The Problem: Missing Overlay System

### What We Discovered

While implementing **ViloxTerm tab bar background customization**, we found a fundamental gap:

**User Story**:
> As a ViloxTerm user, I want to customize the tab bar background color while keeping the rest of the "Dark" theme, and have my customization persist across restarts.

**What We Need**:
```python
# In ViloxTerm preferences
preferences.application_theme = "dark"  # Base theme
preferences.tab_bar_background_color = "#ff0000"  # Override one token

# On startup
app.set_theme("dark")  # Load base theme
# ... somehow apply color override ...

# On restart
app.set_theme("dark")  # ← How do we reapply the override?
```

**Problem**: No theme system API for this!

### Current Workarounds (All Problematic)

#### Workaround 1: Create Ephemeral Theme (Current Plan)

```python
def apply_theme_with_overrides(app, theme_name, overrides):
    # Load base theme
    app.set_theme(theme_name)

    # Create modified theme
    current_theme = theme_mgr.current_theme
    builder = ThemeBuilder.from_theme(current_theme)
    builder.add_color("editorGroupHeader.tabsBackground", "#ff0000")
    customized = builder.build()

    # Apply customized theme
    app.set_theme(customized)  # ← Theme name is "Dark (Custom)"
```

**Issues**:
- ❌ Customized theme only exists in memory
- ❌ Theme name "Dark (Custom)" gets persisted by ThemedApplication
- ❌ On restart: "Dark (Custom)" theme not found → crash/fallback
- ❌ Must disable auto-persist and manage manually
- ❌ App manages theme lifecycle (violates SoC)

**Lifecycle Problem**:
```
Session 1:
1. User sets color → Create "Dark (Custom)" theme
2. set_theme("Dark (Custom)") → Theme system saves name
3. App exits → "Dark (Custom)" theme lost (in-memory only)

Session 2:
1. Theme system loads saved preference → "Dark (Custom)"
2. ThemeManager.get_theme("Dark (Custom)") → NOT FOUND!
3. Crash or fallback to default
```

#### Workaround 2: Persist Custom Theme to Disk

```python
def apply_theme_with_overrides(app, theme_name, overrides):
    # Create customized theme
    customized = create_customized_theme(...)

    # Save as file
    theme_file = Path.home() / ".config/viloxterm/themes/customized.json"
    save_theme_to_file(customized, theme_file)

    # Load into theme system
    theme_mgr.load_theme_from_file(theme_file)

    # Apply
    app.set_theme("customized")
```

**Issues**:
- ❌ Application manages theme files (violates SoC)
- ❌ File sync issues (what if user changes base theme preference?)
- ❌ Must regenerate file when base theme changes
- ❌ File management complexity (create, update, delete)
- ❌ Not scalable (what if 10 color overrides?)

#### Workaround 3: Always Recreate on Startup

```python
# On startup
def main():
    prefs = load_preferences()

    # Load base theme
    app.set_theme(prefs.application_theme, persist=False)

    # Apply overrides (recreate customized theme)
    if prefs.tab_bar_background_color:
        builder = ThemeBuilder.from_theme(theme_mgr.current_theme)
        builder.add_color("...", prefs.tab_bar_background_color)
        customized = builder.build()
        app.set_theme(customized, persist=False)

    # Manually persist base theme name (not customized name)
    save_theme_preference(prefs.application_theme)
```

**Issues**:
- ⚠️ Must disable auto-persist (`persist=False`)
- ⚠️ Must manually persist base theme name
- ⚠️ Recreates theme object every startup (wasteful)
- ⚠️ Couples app to theme internals (ThemeBuilder, color tokens)
- ⚠️ Fragile (breaks if theme system changes)
- ✅ BUT: Works and doesn't persist ephemeral themes

**This is the least-bad workaround, but still problematic.**

---

## Requirements for Theme Overlay System

### Functional Requirements

**FR1: Runtime Color Overrides**
- API to override specific theme tokens at runtime
- Overrides apply on top of current theme
- Overrides persist across theme switches (follow the theme)

**FR2: Override Persistence** (Application Responsibility)
- Application saves overrides to its own config
- Application reapplies overrides on startup
- Theme system provides get/set API, NOT persistence

**FR3: Theme Independence**
- Overrides work with ANY base theme
- Changing base theme keeps overrides (if tokens exist)
- Tokens that don't exist in new theme are ignored

**FR4: Override Inspection**
- API to get current overrides
- API to check if specific token is overridden
- API to clear overrides (individual or all)

**FR5: Widget Notification**
- Widgets notified when override changes
- Same notification mechanism as theme changes
- No widget code changes needed

### Non-Functional Requirements

**NFR1: Separation of Concerns**
- Theme system: Manages overrides (runtime state)
- Application: Persists overrides (config/preferences)
- Clear API boundary

**NFR2: Performance**
- Override application: < 10ms
- Same as current theme switching performance
- No overhead for apps not using overrides

**NFR3: Backward Compatibility**
- Existing apps continue to work
- Optional feature (apps opt-in)
- No breaking changes to Theme/ThemeManager

**NFR4: Type Safety**
- Token names validated
- Color format validated
- Helpful error messages

### API Design Requirements

**REQ1: Simple API**
```python
# Set override
theme_mgr.set_color_override("token.name", "#ff0000")

# Get override
color = theme_mgr.get_color_override("token.name")

# Clear override
theme_mgr.clear_color_override("token.name")

# Get all overrides
overrides = theme_mgr.get_overrides()  # dict

# Clear all overrides
theme_mgr.clear_all_overrides()
```

**REQ2: Application Persistence Pattern**
```python
# Save to app config (application responsibility)
prefs.color_overrides = theme_mgr.get_overrides()
save_preferences(prefs)

# Load from app config (application responsibility)
prefs = load_preferences()
for token, value in prefs.color_overrides.items():
    theme_mgr.set_color_override(token, value)
```

**REQ3: Theme Switch Behavior**
```python
# Set some overrides
theme_mgr.set_color_override("tab.activeBackground", "#ff0000")

# Switch theme
app.set_theme("light")  # ← Override still active!

# Override applies to new theme (if token exists)
# Widgets auto-update
```

---

## Proposed Solution Architecture

### Core Concept: Overlay Layer

```
┌───────────────────────────────────────────┐
│ Widget Rendering                           │
└───────────────────────────────────────────┘
                ↓
┌───────────────────────────────────────────┐
│ Effective Colors (Base + Overrides)       │  ← NEW: Merge layer
└───────────────────────────────────────────┘
                ↓
        ┌───────┴───────┐
        ↓               ↓
┌──────────────┐ ┌──────────────┐
│ Base Theme   │ │  Overrides   │  ← NEW: Override storage
│ (immutable)  │ │  (mutable)   │
└──────────────┘ └──────────────┘
```

### Implementation Layers

#### Layer 1: ThemeManager Extension

```python
# File: widgets/theme_system/src/vfwidgets_theme/core/manager.py

class ThemeManager:
    def __init__(self):
        # ... existing code ...

        # NEW: Override storage (mutable runtime state)
        self._color_overrides: dict[str, str] = {}
        self._font_overrides: dict[str, Any] = {}

    def set_color_override(self, token: str, color: str) -> bool:
        """Set runtime color override.

        Args:
            token: Theme token name (e.g., "tab.activeBackground")
            color: Color value (hex, rgb, rgba)

        Returns:
            True if override applied successfully

        Raises:
            ValueError: If color format invalid
        """
        # Validate color format
        from PySide6.QtGui import QColor
        if not QColor.isValidColor(color):
            raise ValueError(f"Invalid color format: {color}")

        # Store override
        self._color_overrides[token] = color

        # Notify all widgets (same as theme change)
        self._notifier.notify_theme_changed(self.current_theme)

        return True

    def get_color_override(self, token: str) -> Optional[str]:
        """Get color override for token."""
        return self._color_overrides.get(token)

    def clear_color_override(self, token: str) -> bool:
        """Clear color override."""
        if token in self._color_overrides:
            del self._color_overrides[token]
            self._notifier.notify_theme_changed(self.current_theme)
            return True
        return False

    def get_overrides(self) -> dict[str, str]:
        """Get all color overrides.

        Returns:
            Dictionary of token → color mappings

        Note:
            This is intended for application persistence.
            Apps should save this to their config and restore on startup.
        """
        return self._color_overrides.copy()

    def clear_all_overrides(self):
        """Clear all overrides."""
        self._color_overrides.clear()
        self._font_overrides.clear()
        self._notifier.notify_theme_changed(self.current_theme)
```

#### Layer 2: ColorTokenRegistry Extension

```python
# File: widgets/theme_system/src/vfwidgets_theme/core/tokens.py

class ColorTokenRegistry:
    @staticmethod
    def get(token: str, theme: Theme, overrides: Optional[dict] = None) -> str:
        """Get color value with override support.

        Args:
            token: Token name
            theme: Base theme
            overrides: Optional override dictionary

        Returns:
            Color value (override if set, otherwise theme value)
        """
        # Check override first
        if overrides and token in overrides:
            return overrides[token]

        # Fallback to theme
        return theme.colors.get(token, "#000000")  # Black fallback
```

#### Layer 3: ThemedWidget Integration (Transparent)

```python
# No changes needed! ThemedWidget already calls:
# - theme_manager.current_theme
# - ColorTokenRegistry.get()

# Internal change: get() now checks overrides
# Widgets automatically get override values
```

### Usage Example: ViloxTerm

```python
# File: apps/viloxterm/src/viloxterm/theme_customizer.py

def apply_theme_with_overrides(app, theme_name, overrides):
    """Apply theme with color overrides.

    Uses theme overlay system (NEW API).
    """
    # 1. Load base theme
    if not app.set_theme(theme_name):
        return False

    # 2. Get theme manager
    theme_mgr = ThemeManager.get_instance()

    # 3. Clear old overrides
    theme_mgr.clear_all_overrides()

    # 4. Apply new overrides
    if overrides.tab_bar_background_color:
        try:
            theme_mgr.set_color_override(
                "editorGroupHeader.tabsBackground",
                overrides.tab_bar_background_color
            )
        except ValueError as e:
            logger.error(f"Invalid color: {e}")
            return False

    # 5. Widgets auto-update (via theme system notification)
    return True


# File: apps/viloxterm/src/viloxterm/__main__.py

def main():
    app = ThemedApplication(sys.argv)

    # Load preferences
    prefs = load_preferences()

    # Apply theme + overrides
    apply_theme_with_overrides(app, prefs.application_theme, prefs.appearance)

    # ... create window, run ...


# File: apps/viloxterm/src/viloxterm/components/appearance_prefs_tab.py

def save_preferences(self):
    # Get current overrides from theme system
    theme_mgr = ThemeManager.get_instance()
    current_overrides = theme_mgr.get_overrides()

    # Save to preferences
    # (Application persistence, not theme system!)
    self._preferences.color_overrides = current_overrides

    return self._preferences
```

---

## Benefits of Overlay System

### Benefit 1: Separation of Concerns ✅

**Before** (Ephemeral Theme):
```
Application:
- Creates Theme objects
- Manages ThemeBuilder
- Couples to theme internals
- Manages theme lifecycle

Theme System:
- Provides Theme, ThemeBuilder
- Confused: who owns custom themes?
```

**After** (Overlay System):
```
Application:
- Provides UI for customization
- Persists overrides to config
- Calls simple overlay API
- No theme object creation

Theme System:
- Manages runtime overlays
- Notifies widgets
- Provides get/set API
- Clear ownership
```

### Benefit 2: Persistence Made Simple ✅

**Before**:
```python
# Must recreate theme every startup
builder = ThemeBuilder.from_theme(current_theme)
builder.add_color(...)
customized = builder.build()
app.set_theme(customized, persist=False)
save_theme_preference(base_theme_name)  # Manual
```

**After**:
```python
# Just restore overrides
for token, color in prefs.color_overrides.items():
    theme_mgr.set_color_override(token, color)
# Done!
```

### Benefit 3: Theme Independence ✅

**Before**:
```
User sets tab bar color to red in Dark theme.
User switches to Light theme.
→ Lost! Must recreate customized Light theme.
```

**After**:
```
User sets tab bar color to red.
User switches themes.
→ Override follows! Applies to all themes.
```

### Benefit 4: Reusability ✅

**Any application can use this**:
- ViloxTerm: Tab bar colors
- ViloWeb: Per-site color schemes
- Reamde: Syntax highlighting overrides
- Custom apps: Any color customization

**No app needs to**:
- Create Theme objects
- Use ThemeBuilder
- Manage theme files
- Worry about persistence to theme system

---

## Migration Path

### Phase 1: Add Overlay API to ThemeManager

**Changes**:
- Add `_color_overrides` dict to ThemeManager
- Implement `set/get/clear_color_override()` methods
- Update `ColorTokenRegistry.get()` to check overrides
- Add tests

**Impact**: Zero (new API, optional)

### Phase 2: Update Documentation

**Add**:
- API reference for overlay methods
- Usage guide with examples
- Migration guide for apps using workarounds

**Update**:
- Best practices doc
- Architecture doc

### Phase 3: Migrate ViloxTerm (Pilot)

**Before**: Uses ephemeral theme workaround
**After**: Uses overlay API

**Steps**:
1. Update `theme_customizer.py` to use overlay API
2. Update preferences model to store `color_overrides: dict`
3. Update startup to restore overrides
4. Remove ThemeBuilder usage
5. Test persistence

### Phase 4: (Optional) Extend to Fonts

**If needed**:
- Add `set_font_override()` API
- Same pattern as colors
- ViloxTerm could customize terminal font independently

---

## Implementation Checklist

### Core System
- [ ] Add `_color_overrides` to ThemeManager
- [ ] Implement `set_color_override(token, color)`
- [ ] Implement `get_color_override(token)`
- [ ] Implement `clear_color_override(token)`
- [ ] Implement `get_overrides()` → dict
- [ ] Implement `clear_all_overrides()`
- [ ] Update `ColorTokenRegistry.get()` to check overrides
- [ ] Add color validation (QColor.isValidColor)
- [ ] Ensure widget notification on override change

### Testing
- [ ] Unit tests for override API
- [ ] Test override + theme switch
- [ ] Test persistence pattern (save/restore)
- [ ] Test invalid color handling
- [ ] Performance test (override application speed)

### Documentation
- [ ] API reference for overlay methods
- [ ] Usage guide with examples
- [ ] Update architecture doc
- [ ] Migration guide for existing apps

### ViloxTerm Migration (Pilot)
- [ ] Update preferences model
- [ ] Update theme_customizer.py
- [ ] Update __main__.py startup
- [ ] Update appearance preferences tab
- [ ] Remove ThemeBuilder usage
- [ ] Test full lifecycle

---

## Risks & Mitigations

### Risk 1: Performance Impact

**Risk**: Checking overrides on every color access slows widgets.

**Mitigation**:
- Overrides stored in dict (O(1) lookup)
- Only check if overrides non-empty
- Benchmark: Ensure <1ms overhead
- Cache effective colors if needed

### Risk 2: Token Name Validation

**Risk**: Apps use invalid token names, silent failures.

**Mitigation**:
- Validate token exists in at least one theme
- Log warnings for unknown tokens
- Provide token autocomplete helper
- Document standard tokens

### Risk 3: Backward Compatibility

**Risk**: Existing apps break with new API.

**Mitigation**:
- New API is additive (no removals)
- Existing code continues to work
- Optional feature (apps opt-in)
- Version guard for safety

---

## Comparison: Current vs. Proposed

### Creating Custom Theme

**Current** (Ephemeral Theme):
```python
# Application code
from vfwidgets_theme.core.theme import ThemeBuilder
theme_mgr = ThemeManager.get_instance()
current = theme_mgr.current_theme

builder = ThemeBuilder.from_theme(current)
builder.add_color("tab.activeBackground", "#ff0000")
customized = builder.build()

app.set_theme(customized, persist=False)
save_theme_preference("dark")  # Manual persistence
```

**Proposed** (Overlay System):
```python
# Application code
from vfwidgets_theme.core.manager import ThemeManager
theme_mgr = ThemeManager.get_instance()

theme_mgr.set_color_override("tab.activeBackground", "#ff0000")
# Done! No theme object creation.
```

### Persistence

**Current**:
```python
# On startup
prefs = load_preferences()
app.set_theme(prefs.application_theme, persist=False)

# Recreate customizations
if prefs.tab_bar_background_color:
    builder = ThemeBuilder.from_theme(theme_mgr.current_theme)
    builder.add_color("...", prefs.tab_bar_background_color)
    customized = builder.build()
    app.set_theme(customized, persist=False)

save_theme_preference(prefs.application_theme)
```

**Proposed**:
```python
# On startup
prefs = load_preferences()
app.set_theme(prefs.application_theme)

# Restore overrides (simple!)
for token, color in prefs.color_overrides.items():
    theme_mgr.set_color_override(token, color)
```

### Application Preferences Model

**Current**:
```python
@dataclass
class AppearancePreferences:
    application_theme: str = "dark"
    tab_bar_background_color: str = ""  # How to apply this?
```

**Proposed**:
```python
@dataclass
class AppearancePreferences:
    application_theme: str = "dark"
    color_overrides: dict[str, str] = field(default_factory=dict)

    # Helper methods
    def set_color_override(self, token: str, color: str):
        self.color_overrides[token] = color

    def get_color_override(self, token: str) -> Optional[str]:
        return self.color_overrides.get(token)
```

---

## Next Steps

### Immediate Actions

1. **Review this document** with stakeholders
2. **Refine requirements** based on feedback
3. **Create implementation plan** (phased approach)
4. **Prototype** core overlay API
5. **Pilot with ViloxTerm** tab bar customization

### Future Enhancements

1. **Font Overrides**: Extend to fonts (terminal font customization)
2. **Preset System**: Save/load override presets
3. **UI Builder**: Visual override editor (drag-drop color picker)
4. **Import/Export**: Share override sets between users

---

## Conclusion

The theme overlay system fills a critical gap in VFWidgets' theme architecture:

**Problem**: Applications need runtime color customization without managing theme lifecycle.

**Solution**: Add overlay API to theme system for runtime token overrides.

**Benefits**:
- ✅ Clean separation of concerns
- ✅ Simple persistence pattern
- ✅ Reusable across all apps
- ✅ No theme repository pollution
- ✅ Theme-independent overrides

**Impact**:
- Enables ViloxTerm tab bar customization (current blocker)
- Opens door for advanced customization features
- Maintains architectural integrity
- Minimal implementation cost

**Recommendation**: **PROCEED** with overlay system implementation.

This architectural improvement will benefit all current and future VFWidgets applications while maintaining clean separation between application UI and theme system business logic.
