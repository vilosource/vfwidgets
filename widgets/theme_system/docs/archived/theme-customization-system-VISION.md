# VFWidgets Theme Customization System - Vision & Design

**Status**: Vision Document & Design Specification
**Version**: 1.0.0-draft
**Date**: 2025-10-18
**Author**: VFWidgets Architecture Team

**Related Documents**:
- **Problem Analysis**: [theme-overlay-system-PROBLEM.md](./theme-overlay-system-PROBLEM.md) - The problem this solves
- **Technical Specification**: [theme-overlay-system-SPECIFICATION.md](./theme-overlay-system-SPECIFICATION.md) - Implementation details
- **Breaking Changes**: [BREAKING-CHANGES.md](./BREAKING-CHANGES.md) - Breaking changes tracking
- **Documentation Index**: [README-OVERLAY-SYSTEM.md](./README-OVERLAY-SYSTEM.md) - Navigation guide

**Additional Resources**:
- [Theme System Architecture](./ARCHITECTURE.md) - Current implementation (if exists)
- [API Reference](./api-REFERENCE.md) - Current API documentation (if exists)

---

## Executive Summary

This document defines the **unified theme customization system** for the VFWidgets ecosystem, providing a comprehensive solution for theme management across three tiers:

1. **Base Themes** - Created by theme developers in Theme Studio
2. **Application Themes** - App-specific defaults and curated experiences
3. **User Themes** - End-user runtime customizations

### The Vision

**Every VFWidgets application should have a consistent, simple pattern for theme customization that respects separation of concerns, provides excellent developer experience, and empowers end users to personalize their applications.**

### Core Principles

1. **Separation of Responsibilities**
   - Theme System: Manages themes, overlays, widget notification
   - Applications: Provide UI, persist preferences
   - Widgets: Consume themes, no theme logic

2. **Developer Experience First**
   - Simple API for common cases
   - Progressive enhancement for advanced features
   - Convention over configuration
   - Common patterns work automatically

3. **End-User Empowerment**
   - Easy personalization without breaking design
   - Consistent UI across apps
   - Changes persist across sessions
   - Safe experimentation (reset to defaults)

4. **Ecosystem Thinking**
   - Base themes are reusable across apps
   - Apps can provide curated theme experiences
   - Users can share customizations
   - Widgets automatically integrate

---

## Problem Statement

**Link**: See [Theme Overlay System - Problem Analysis](./theme-overlay-system-PROBLEM.md)

### Current Gap

Applications need to provide theme customization to users, but the theme system lacks:
- ❌ Runtime overlay/override API
- ❌ Standard pattern for app integration
- ❌ Clear separation between base themes and customizations
- ❌ Common persistence pattern
- ❌ Developer-friendly abstraction

### Impact

- Apps forced to create ephemeral themes (architectural violation)
- Each app implements customization differently (inconsistency)
- Themes don't persist across restarts (poor UX)
- Tight coupling to theme internals (fragile)
- No reusable patterns (duplicated code)

---

## Stakeholder Use Cases

### Use Case 1: Theme Studio Developer

**Role**: Creates high-quality base themes for the ecosystem

**Current Workflow**:
```python
# In Theme Studio
1. Create new theme → dark-professional.json
2. Define color tokens (179 tokens)
3. Test with preview widgets
4. Export theme file
5. Share theme in ecosystem
```

**Needs**:
- ✅ Theme Studio provides professional editing environment
- ✅ Themes follow VSCode token standards
- ✅ Preview system shows widgets with theme
- ✅ Export produces valid theme files

**Future Enhancement**:
- Theme versioning and updates
- Theme marketplace/repository
- Automatic compatibility checking

**Current Status**: ✅ Well supported, no changes needed

---

### Use Case 2: App Developer

**Role**: Builds applications using VFWidgets, integrates theme system

**Scenario A: Simple App (No Customization)**

```python
# Example: Simple utility app
from vfwidgets_theme import ThemedApplication

app = ThemedApplication(sys.argv)
app.set_theme("dark")  # Use base theme as-is
window = MyWindow()
window.show()
sys.exit(app.exec())
```

**Needs**:
- ✅ Minimal code (2 lines for theming)
- ✅ Works with any base theme
- ✅ No configuration required

**Current Status**: ✅ Fully supported

---

**Scenario B: App with Default Customizations**

```python
# Example: Branded app with specific colors
from vfwidgets_theme import VFThemedApplication  # NEW: Enhanced base class

class MyApp(VFThemedApplication):
    # Declarative theme configuration
    theme_config = {
        "base_theme": "dark",
        "app_overrides": {
            # App branding colors
            "colors.primary": "#007bff",
            "button.background": "#007bff",
            "button.hoverBackground": "#0056b3",
        },
        "allow_user_customization": False,  # Lock to app theme
    }

app = MyApp(sys.argv)
# App theme (dark + overrides) automatically applied!
```

**Needs**:
- ✅ Declarative configuration (no imperative code)
- ✅ Base theme + app overrides composition
- ✅ Option to lock theme (no user customization)
- ❌ **NOT CURRENTLY SUPPORTED** - requires new API

**Desired Benefits**:
- Consistent app branding across theme switches
- No theme lifecycle management
- Works with theme system's strengths

---

**Scenario C: App with User Customization**

```python
# Example: ViloxTerm - user customizes tab bar color
from vfwidgets_theme import VFThemedApplication

class ViloxTermApp(VFThemedApplication):
    theme_config = {
        "base_theme": "dark",
        "app_overrides": {
            # App defaults (terminal-specific)
            "terminal.background": "#1a1a1a",
            "terminal.foreground": "#d4d4d4",
        },
        "allow_user_customization": True,  # User can override
        "customizable_tokens": [
            # Expose specific tokens to user
            "editorGroupHeader.tabsBackground",
            "terminal.background",
            "terminal.foreground",
        ],
    }

app = ViloxTermApp(sys.argv)

# Load user overrides from app preferences
user_overrides = load_user_preferences().color_overrides
app.apply_user_overrides(user_overrides)  # NEW: Apply user customizations
```

**Needs**:
- ✅ Declarative app defaults
- ✅ User override support
- ✅ Selective customization (only expose specific tokens)
- ✅ Simple persistence pattern
- ❌ **NOT CURRENTLY SUPPORTED** - requires overlay system

**Desired Benefits**:
- User empowerment (customization)
- App maintains design coherence (limited token exposure)
- Simple integration (no theme object management)

---

**Scenario D: Advanced App (Theme Presets)**

```python
# Example: ViloWeb - per-site color schemes
from vfwidgets_theme import VFThemedApplication

class ViloWebApp(VFThemedApplication):
    theme_config = {
        "base_theme": "dark",
        "allow_user_customization": True,
        "presets": {
            # Pre-built override sets
            "reader_mode": {
                "editor.background": "#f9f9f9",
                "editor.foreground": "#2e2e2e",
            },
            "high_contrast": {
                "colors.foreground": "#ffffff",
                "colors.background": "#000000",
            },
        },
    }

app = ViloWebApp(sys.argv)

# User can switch between presets
app.apply_preset("reader_mode")  # NEW: Apply preset overrides

# Or create custom preset from current state
app.save_preset("my_custom", app.get_effective_overrides())
```

**Needs**:
- ✅ Preset system (named override sets)
- ✅ Preset switching (atomic change)
- ✅ User-created presets
- ❌ **NOT CURRENTLY SUPPORTED** - future enhancement

**Desired Benefits**:
- Quick theme switching (presets)
- Shareable configurations
- Power user features

---

### Use Case 3: End User

**Role**: Uses VFWidgets applications, wants to personalize appearance

**Scenario A: Theme Selection**

```
User:
1. Opens ViloxTerm → Preferences → Appearance
2. Sees dropdown: [Dark, Light, High Contrast, Custom...]
3. Selects "Light"
4. App immediately switches to light theme
5. Closes app, reopens → Still light theme ✓
```

**Needs**:
- ✅ Simple theme selection UI
- ✅ Immediate feedback (live preview)
- ✅ Persistence across sessions
- ✅ Currently supported (each app implements independently)

**Future Enhancement**:
- Reusable theme selection widget
- Live preview before applying
- Standard UI patterns

---

**Scenario B: Color Customization**

```
User:
1. Opens ViloxTerm → Preferences → Appearance → Customize
2. Sees: "Tab Bar Background: [#2d2d30] [Pick Color...]"
3. Clicks "Pick Color" → Color picker dialog
4. Selects red (#ff0000) → Tab bar turns red immediately
5. Clicks Apply → Change saved
6. Closes app, reopens → Tab bar still red ✓
7. Switches to Light theme → Red override applies to light theme too ✓
8. Clicks "Reset to Default" → Returns to theme's default color
```

**Needs**:
- ✅ Visual color picker
- ✅ Live preview
- ✅ Persistence
- ✅ Theme independence (overrides follow theme switches)
- ✅ Easy reset
- ❌ **NOT CURRENTLY SUPPORTED** - requires overlay system

**Desired UX**:
- Discoverable (obvious what's customizable)
- Safe (can always reset)
- Responsive (immediate visual feedback)
- Consistent (same UI pattern across apps)

---

**Scenario C: Preset Switching (Advanced)**

```
User:
1. Creates custom color scheme for coding
2. Saves as preset: "Coding Dark"
3. Creates another preset for presentations: "High Contrast"
4. Quick-switches between presets from toolbar
5. Exports preset to share with colleagues
6. Imports colleague's preset
```

**Needs**:
- ✅ Preset creation from current state
- ✅ Preset management UI
- ✅ Quick switching
- ✅ Import/export
- ❌ **NOT CURRENTLY SUPPORTED** - future enhancement

---

## Architecture Design

### Three-Tier Theme Resolution

```
┌─────────────────────────────────────────────────────┐
│ Effective Theme (What widgets see)                  │
│ = Base Theme + App Overrides + User Overrides       │
└─────────────────────────────────────────────────────┘
                        ↑
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓
┌──────────────┐ ┌─────────────┐ ┌─────────────┐
│  Base Theme  │ │App Overrides│ │User Overrides│
│              │ │             │ │             │
│ Created in   │ │ Defined by  │ │ Set at      │
│ Theme Studio │ │ app dev     │ │ runtime by  │
│              │ │             │ │ end user    │
│ dark.json    │ │ theme_config│ │ preferences │
│ light.json   │ │ in app.py   │ │ UI          │
└──────────────┘ └─────────────┘ └─────────────┘
```

**Resolution Strategy**:
1. Load base theme (e.g., "dark")
2. Apply app overrides (from `theme_config`)
3. Apply user overrides (from app preferences)
4. Notify widgets of effective theme

**Priority**: User Overrides > App Overrides > Base Theme

---

### MVC Architecture Alignment

```
┌────────────────────────────────────────────────────┐
│ MODEL (Theme Data)                                  │
│  ├─ Base Theme (immutable)                          │
│  ├─ App Overrides (immutable, defined in code)      │
│  └─ User Overrides (mutable, runtime)               │
└────────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────────┐
│ CONTROLLER (Theme Manager)                          │
│  ├─ Loads base theme                                │
│  ├─ Applies overrides (app + user)                  │
│  ├─ Manages runtime state                           │
│  ├─ Validates changes                               │
│  └─ Notifies views                                  │
└────────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────────┐
│ VIEW (Widgets)                                      │
│  ├─ ThemedWidget mixin                              │
│  ├─ Receives theme change notifications             │
│  ├─ Renders with effective theme                    │
│  └─ No theme logic (pure view)                      │
└────────────────────────────────────────────────────┘
```

**Separation of Concerns**:

| Layer | Responsibility | Does NOT Do |
|-------|---------------|-------------|
| **Theme System (Model + Controller)** | Theme lifecycle, overlay management, validation, widget notification | Provide UI, persist app preferences, know about specific apps |
| **Application (Controller)** | Provide preferences UI, persist user overrides, declare app defaults | Create Theme objects, manage theme files, notify widgets |
| **Widgets (View)** | Render with theme, react to changes | Know about overrides, persistence, or theme sources |

---

### Design Patterns Applied

#### 1. **Strategy Pattern** - Theme Resolution

```python
class ThemeResolutionStrategy(Protocol):
    """Strategy for resolving effective theme from layers."""

    def resolve(
        self,
        base_theme: Theme,
        app_overrides: dict[str, str],
        user_overrides: dict[str, str]
    ) -> Theme:
        """Resolve effective theme."""
        ...

class MergeStrategy(ThemeResolutionStrategy):
    """Merge all layers (default strategy)."""

    def resolve(self, base_theme, app_overrides, user_overrides):
        # Priority: user > app > base
        effective_colors = {
            **base_theme.colors,
            **app_overrides,
            **user_overrides,
        }
        return Theme(name=f"{base_theme.name} (customized)", colors=effective_colors, ...)
```

**Benefit**: Different resolution strategies for different needs (merge, replace, filter).

---

#### 2. **Observer Pattern** - Widget Notification

```python
# Already implemented in theme system!
class ThemeManager:
    def set_color_override(self, token, color):
        self._color_overrides[token] = color
        self._notifier.notify_theme_changed(self.current_theme)  # ← Observer pattern
        # All registered widgets receive notification automatically

class ThemedWidget:
    def _on_theme_changed(self, theme):
        # Widget updates automatically (Observer)
        self.update()
```

**Benefit**: Widgets automatically stay in sync, no manual update calls.

---

#### 3. **Builder Pattern** - Theme Composition

```python
# Already exists (ThemeBuilder), extend for overlays
builder = ThemeBuilder.from_theme(base_theme)
builder.apply_overrides(app_overrides)  # NEW: Batch apply
builder.apply_overrides(user_overrides)  # NEW: Second layer
effective_theme = builder.build()
```

**Benefit**: Immutable theme construction with validation.

---

#### 4. **Facade Pattern** - Simple API for Apps

```python
class VFThemedApplication(ThemedApplication):
    """Facade hiding theme customization complexity."""

    def __init__(self, argv, theme_config=None):
        super().__init__(argv)
        self._theme_config = theme_config or {}
        self._setup_theme_customization()

    def _setup_theme_customization(self):
        # Internal: Complex theme resolution
        # External: Simple API
        base = self._theme_config.get("base_theme", "dark")
        app_overrides = self._theme_config.get("app_overrides", {})

        self.set_theme(base)
        self.apply_app_overrides(app_overrides)  # NEW: Facade method

    def apply_user_overrides(self, overrides: dict):
        """Simple API for apps to apply user customizations."""
        # Facade: Hides ThemeManager complexity
        theme_mgr = ThemeManager.get_instance()
        for token, value in overrides.items():
            theme_mgr.set_color_override(token, value)
```

**Benefit**: Apps use simple facade, don't touch ThemeManager internals.

---

#### 5. **Template Method Pattern** - Common App Initialization

```python
class VFThemedApplication(ThemedApplication):
    """Base class for VFWidgets apps with theme customization."""

    # Template method pattern
    def _setup_theme_customization(self):
        """Template method with hooks for subclasses."""
        self._load_base_theme()       # Step 1: Load base
        self._apply_app_defaults()    # Step 2: App overrides (hook)
        self._restore_user_prefs()    # Step 3: User overrides (hook)

    def _load_base_theme(self):
        """Implemented in base class."""
        base = self.theme_config.get("base_theme", "dark")
        self.set_theme(base)

    def _apply_app_defaults(self):
        """Hook: Subclasses can override."""
        app_overrides = self.theme_config.get("app_overrides", {})
        if app_overrides:
            self.apply_app_overrides(app_overrides)

    def _restore_user_prefs(self):
        """Hook: Subclasses override to load user prefs."""
        pass  # Default: no user customization
```

**Benefit**: Consistent initialization pattern, extensible via hooks.

---

## Proposed API Design

### Level 1: Simple Apps (No Customization)

**Current API** (Keep as-is):

```python
from vfwidgets_theme import ThemedApplication

app = ThemedApplication(sys.argv)
app.set_theme("dark")
# Done! No customization support needed.
```

**Status**: ✅ Already works, no changes

---

### Level 2: Apps with Declarative Defaults

**New API**:

```python
from vfwidgets_theme import VFThemedApplication  # NEW

class MyApp(VFThemedApplication):
    theme_config = {
        "base_theme": "dark",
        "app_overrides": {
            "colors.primary": "#007bff",
            "button.background": "#007bff",
        },
    }

app = MyApp(sys.argv)
# Base theme + app overrides automatically applied!
```

**Implementation**:

```python
class VFThemedApplication(ThemedApplication):
    theme_config: dict = {}  # Subclasses override

    def __init__(self, argv, theme_config=None):
        super().__init__(argv)

        # Use instance config or class attribute
        self._config = theme_config or self.theme_config

        # Setup theme with overrides
        self._setup_theme_customization()

    def _setup_theme_customization(self):
        base_theme = self._config.get("base_theme", "dark")
        app_overrides = self._config.get("app_overrides", {})

        # Load base theme
        if not self.set_theme(base_theme):
            self.set_theme("dark")  # Fallback

        # Apply app overrides
        if app_overrides:
            self.apply_app_overrides(app_overrides)

    def apply_app_overrides(self, overrides: dict[str, str]):
        """Apply app-level theme overrides.

        Args:
            overrides: Dictionary of token → value mappings
        """
        theme_mgr = ThemeManager.get_instance()
        for token, value in overrides.items():
            try:
                theme_mgr.set_color_override(token, value)
            except ValueError as e:
                logger.warning(f"Invalid override {token}={value}: {e}")
```

**Status**: ❌ Requires overlay system implementation

---

### Level 3: Apps with User Customization

**New API**:

```python
from vfwidgets_theme import VFThemedApplication

class ViloxTermApp(VFThemedApplication):
    theme_config = {
        "base_theme": "dark",
        "app_overrides": {...},
        "allow_user_customization": True,
        "customizable_tokens": [
            "editorGroupHeader.tabsBackground",
            "terminal.background",
        ],
    }

    def _restore_user_prefs(self):
        """Hook: Load user overrides from app preferences."""
        prefs = self.load_preferences()  # App-specific method
        if prefs.theme_customization:
            self.apply_user_overrides(prefs.theme_customization.overrides)

app = ViloxTermApp(sys.argv)
# Loads: base theme + app defaults + user customizations
```

**New Methods**:

```python
class VFThemedApplication(ThemedApplication):
    def apply_user_overrides(self, overrides: dict[str, str]):
        """Apply user customizations.

        Args:
            overrides: Dictionary of token → value mappings from user prefs
        """
        theme_mgr = ThemeManager.get_instance()

        # Clear previous user overrides
        # (app overrides remain, only clear user layer)
        theme_mgr.clear_user_overrides()

        # Apply new user overrides
        for token, value in overrides.items():
            # Validate against customizable_tokens if configured
            if self._is_token_customizable(token):
                try:
                    theme_mgr.set_user_override(token, value)
                except ValueError as e:
                    logger.warning(f"Invalid user override: {e}")

    def _is_token_customizable(self, token: str) -> bool:
        """Check if token is exposed for user customization."""
        customizable = self._config.get("customizable_tokens")
        if customizable is None:
            return True  # All tokens customizable (no filter)
        return token in customizable

    def get_effective_overrides(self) -> dict[str, str]:
        """Get all effective overrides (app + user).

        Returns:
            Dictionary with current override state
        """
        theme_mgr = ThemeManager.get_instance()
        return {
            "app": theme_mgr.get_app_overrides(),
            "user": theme_mgr.get_user_overrides(),
        }
```

**Status**: ❌ Requires overlay system with layer separation

---

### Overlay System API (Theme System Extension)

**New ThemeManager Methods**:

```python
class ThemeManager:
    def __init__(self):
        # ... existing ...

        # NEW: Layered override storage
        self._app_overrides: dict[str, str] = {}   # App-level defaults
        self._user_overrides: dict[str, str] = {}  # User customizations

    # App Override Methods (for VFThemedApplication)
    def set_app_override(self, token: str, value: str):
        """Set app-level override (lower priority than user)."""
        self._validate_color(value)
        self._app_overrides[token] = value
        self._notify_change()

    def get_app_overrides(self) -> dict[str, str]:
        """Get all app overrides."""
        return self._app_overrides.copy()

    def clear_app_overrides(self):
        """Clear all app overrides."""
        self._app_overrides.clear()
        self._notify_change()

    # User Override Methods (for end users)
    def set_user_override(self, token: str, value: str):
        """Set user-level override (highest priority)."""
        self._validate_color(value)
        self._user_overrides[token] = value
        self._notify_change()

    def get_user_overrides(self) -> dict[str, str]:
        """Get all user overrides."""
        return self._user_overrides.copy()

    def clear_user_overrides(self):
        """Clear all user overrides (keep app overrides)."""
        self._user_overrides.clear()
        self._notify_change()

    def clear_all_overrides(self):
        """Clear both app and user overrides."""
        self._app_overrides.clear()
        self._user_overrides.clear()
        self._notify_change()

    # Token Resolution (updated to support layers)
    def get_effective_color(self, token: str) -> str:
        """Get effective color value with layered override support.

        Priority: User Override > App Override > Base Theme
        """
        # Check user override first
        if token in self._user_overrides:
            return self._user_overrides[token]

        # Check app override
        if token in self._app_overrides:
            return self._app_overrides[token]

        # Fallback to base theme
        theme = self.current_theme
        return theme.colors.get(token, "#000000")
```

**Status**: ❌ To be implemented

---

## Common Patterns for Apps

### Pattern 1: Standard App Initialization

**Template** (Copy this for new apps):

```python
# app.py
from vfwidgets_theme import VFThemedApplication

class MyApp(VFThemedApplication):
    # Declarative theme configuration
    theme_config = {
        "base_theme": "dark",                    # Base theme name
        "app_overrides": {},                     # App defaults (optional)
        "allow_user_customization": False,       # Enable/disable user prefs
        "customizable_tokens": None,             # None = all, or list of tokens
    }

    def __init__(self, argv):
        super().__init__(argv)
        # App-specific initialization
        self.main_window = None

    def run(self):
        """Run the application."""
        self.main_window = MainWindow()
        self.main_window.show()
        return self.exec()

# __main__.py
def main():
    app = MyApp(sys.argv)
    sys.exit(app.run())
```

**Benefits**:
- ✅ Consistent pattern across all apps
- ✅ Minimal boilerplate
- ✅ Declarative configuration
- ✅ Easy to understand

---

### Pattern 2: App with User Preferences

**Template**:

```python
# models/preferences_model.py
from dataclasses import dataclass, field

@dataclass
class ThemeCustomization:
    """Theme customization preferences."""
    base_theme: str = "dark"
    user_overrides: dict[str, str] = field(default_factory=dict)

@dataclass
class AppPreferences:
    """Application preferences."""
    theme: ThemeCustomization = field(default_factory=ThemeCustomization)
    # ... other preferences ...

# app.py
class MyApp(VFThemedApplication):
    theme_config = {
        "base_theme": "dark",  # Default, can be overridden by prefs
        "allow_user_customization": True,
    }

    def _restore_user_prefs(self):
        """Hook: Restore user theme customizations."""
        prefs = self.load_preferences()

        # Apply base theme choice
        if prefs.theme.base_theme != "dark":
            self.set_theme(prefs.theme.base_theme)

        # Apply user overrides
        if prefs.theme.user_overrides:
            self.apply_user_overrides(prefs.theme.user_overrides)

    def load_preferences(self) -> AppPreferences:
        """App-specific preference loading."""
        # Load from ~/.config/myapp/preferences.json
        ...

    def save_preferences(self, prefs: AppPreferences):
        """App-specific preference saving."""
        # Save to ~/.config/myapp/preferences.json
        ...
```

**Benefits**:
- ✅ Clear hook points (`_restore_user_prefs`)
- ✅ App owns persistence (separation of concerns)
- ✅ Standard preference model structure

---

### Pattern 3: Preferences UI Integration

**Template**:

```python
# components/appearance_prefs_tab.py
from vfwidgets_theme import ThemeManager  # NEW: Access overlay system

class AppearancePreferencesTab(QWidget):
    def _create_theme_group(self):
        """Create theme customization UI."""
        group = QGroupBox("Theme")
        layout = QFormLayout()

        # Base theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light", "High Contrast"])
        layout.addRow("Base theme:", self.theme_combo)

        # User customization section (if enabled)
        if app.theme_config.get("allow_user_customization"):
            self._add_customization_controls(layout)

        return group

    def _add_customization_controls(self, layout):
        """Add color override controls."""
        customizable = app.theme_config.get("customizable_tokens", [])

        for token in customizable:
            # Create color picker for each customizable token
            color_layout = QHBoxLayout()
            color_edit = QLineEdit()
            color_edit.setPlaceholderText("Theme default")

            pick_btn = QPushButton("Pick...")
            pick_btn.clicked.connect(lambda t=token: self._pick_color(t))

            color_layout.addWidget(color_edit)
            color_layout.addWidget(pick_btn)

            # User-friendly label
            label = self._token_to_label(token)
            layout.addRow(label, color_layout)

    def _pick_color(self, token: str):
        """Open color picker for token."""
        from PySide6.QtWidgets import QColorDialog

        color = QColorDialog.getColor()
        if color.isValid():
            # Apply immediately (live preview)
            theme_mgr = ThemeManager.get_instance()
            theme_mgr.set_user_override(token, color.name())

    def save_preferences(self):
        """Save user customizations."""
        theme_mgr = ThemeManager.get_instance()

        # Get current theme and overrides
        prefs = AppPreferences()
        prefs.theme.base_theme = self.theme_combo.currentText().lower()
        prefs.theme.user_overrides = theme_mgr.get_user_overrides()

        # Save to app config
        self.app.save_preferences(prefs)
```

**Benefits**:
- ✅ Standard UI pattern
- ✅ Live preview (immediate feedback)
- ✅ Declarative (driven by `customizable_tokens`)
- ✅ Reusable across apps

---

## Developer Experience Goals

### Goal 1: "It Just Works" (Zero Config)

**Example**: Simple app

```python
from vfwidgets_theme import ThemedApplication

app = ThemedApplication(sys.argv)
app.set_theme("dark")  # One line!
```

**Outcome**: ✅ Automatic widget theming, no boilerplate

---

### Goal 2: "Convention Over Configuration"

**Example**: App with defaults

```python
class MyApp(VFThemedApplication):
    theme_config = {
        "base_theme": "dark",  # Convention: Use "dark" if not specified
        "app_overrides": {...},  # Convention: Apply after base theme
    }
```

**Outcome**: ✅ Predictable behavior, minimal configuration

---

### Goal 3: "Progressive Enhancement"

**Levels**:
1. Basic: Use base theme (ThemedApplication)
2. Intermediate: Add app defaults (VFThemedApplication + theme_config)
3. Advanced: Enable user customization (+ override hooks)
4. Expert: Preset system, import/export (future)

**Outcome**: ✅ Developers only learn what they need

---

### Goal 4: "Declarative > Imperative"

**Before** (Imperative):
```python
theme = load_theme("dark")
builder = ThemeBuilder.from_theme(theme)
builder.add_color("tab.activeBackground", "#ff0000")
customized = builder.build()
app.set_theme(customized)
```

**After** (Declarative):
```python
class MyApp(VFThemedApplication):
    theme_config = {
        "base_theme": "dark",
        "app_overrides": {"tab.activeBackground": "#ff0000"}
    }
```

**Outcome**: ✅ Less code, clearer intent

---

### Goal 5: "Fail Fast with Helpful Errors"

**Example**:
```python
# Invalid color format
theme_mgr.set_user_override("tab.activeBackground", "invalid-color")

# Error raised:
# ValueError: Invalid color format 'invalid-color'.
#   Expected formats: #RRGGBB, #RGB, rgb(r,g,b), rgba(r,g,b,a)
#   Example: '#ff0000' or 'rgb(255, 0, 0)'
```

**Outcome**: ✅ Clear error messages, fast debugging

---

### Goal 6: "Discoverability via IDE"

**Example**: IDE autocomplete

```python
app = VFThemedApplication(sys.argv)
app.  # IDE shows:
      # - apply_user_overrides()
      # - apply_app_overrides()
      # - get_effective_overrides()
      # - set_theme()
      # ... with docstrings!
```

**Outcome**: ✅ Self-documenting API, IDE-friendly

---

## End-User Experience Goals

### Goal 1: "Discoverable Customization"

**UI Pattern**:
```
Preferences → Appearance Tab
  ├─ Theme: [Dropdown: Dark, Light, ...]
  └─ Customize:
      ├─ Tab Bar Background: [#2d2d30] [Pick Color...] [Reset]
      ├─ Terminal Background: [#1a1a1a] [Pick Color...] [Reset]
      └─ ... (only customizable tokens shown)
```

**Outcome**: ✅ Obvious what's customizable, clear UI

---

### Goal 2: "Safe Experimentation"

**Features**:
- Live preview (see changes immediately)
- Reset button (revert to default)
- Cancel button (discard all changes)
- Undo/Redo (future)

**Outcome**: ✅ Users comfortable trying things

---

### Goal 3: "Consistent UI Across Apps"

**Standard Widgets** (to be developed):
- `ThemeSelectionWidget` - Dropdown for base theme
- `ColorCustomizationWidget` - Color picker with preview
- `ThemePresetWidget` - Preset management (future)

**Outcome**: ✅ Familiar UI across all VFWidgets apps

---

### Goal 4: "Persistence That Works"

**User Expectation**:
```
1. Customize color → Looks good
2. Close app
3. Reopen app → Color still there ✓
4. Switch themes → Color follows ✓
5. Reset → Returns to default ✓
```

**Outcome**: ✅ No surprises, predictable behavior

---

## Ecosystem Vision

### Tier 1: Base Themes (Theme Studio)

**Purpose**: Professional, high-quality themes for the ecosystem

**Created By**: Theme developers, design-focused developers

**Examples**:
- `dark-default` - VFWidgets default dark theme
- `light-default` - VFWidgets default light theme
- `high-contrast` - Accessibility-focused theme
- `solarized-dark` - Community theme
- `dracula` - Community theme

**Characteristics**:
- ✅ Complete token coverage (all 179 tokens)
- ✅ Professionally designed
- ✅ Tested with preview widgets
- ✅ Distributed as .json files
- ✅ Versioned

**Distribution**:
- Built-in themes (shipped with vfwidgets-theme)
- Theme marketplace (future)
- GitHub repos
- User themes directory (`~/.vfwidgets/themes/`)

---

### Tier 2: App Themes (App Developers)

**Purpose**: App-specific branding and UX polish

**Created By**: App developers

**Examples**:
- ViloxTerm: Terminal-optimized colors, distinct tab bar
- ViloWeb: Reader-friendly browser colors
- Reamde: Document-focused editor colors

**Characteristics**:
- ✅ Base theme + selective overrides
- ✅ Coded in app (declarative `theme_config`)
- ✅ Locked (users can't change app branding)
- ✅ Consistent across installations

**Benefits**:
- Branded app experience
- Optimized for app's domain (terminal vs. web vs. document)
- Maintains design coherence

---

### Tier 3: User Themes (End Users)

**Purpose**: Personal customization and accessibility

**Created By**: End users via app preferences

**Examples**:
- User sets red tab bar in ViloxTerm
- User creates high-contrast preset for presentations
- User imports colleague's color scheme

**Characteristics**:
- ✅ Selective token overrides
- ✅ Persisted in app config (`~/.config/app/preferences.json`)
- ✅ Portable (can export/import)
- ✅ Reversible (reset to defaults)

**Benefits**:
- Personalization
- Accessibility (vision needs)
- Workflow optimization (different presets for different tasks)

---

### Theme Flow

```
Theme Studio
     ↓
 Base Theme (dark.json)
     ↓
App Developer uses base theme
     ↓
App Theme = dark.json + app_overrides
     ↓
End User customizes
     ↓
User Theme = App Theme + user_overrides
     ↓
Widgets render with User Theme
```

---

## Implementation Roadmap

### Phase 1: Foundation (Overlay System)

**Goal**: Add runtime overlay API to theme system

**Tasks**:
- [ ] Add layered override storage to ThemeManager
- [ ] Implement set/get/clear methods
- [ ] Update ColorTokenRegistry.get() to check overrides
- [ ] Add validation (color format, token existence)
- [ ] Widget notification on override change
- [ ] Unit tests

**Deliverable**: Overlay system API ready for apps to use

**Duration**: ~2 weeks

---

### Phase 2: Application Base Class

**Goal**: Create VFThemedApplication with declarative config

**Tasks**:
- [ ] Implement VFThemedApplication class
- [ ] Declarative `theme_config` support
- [ ] Template method pattern for initialization
- [ ] Hook methods for customization
- [ ] Documentation and examples
- [ ] Migration guide

**Deliverable**: VFThemedApplication ready for app adoption

**Duration**: ~1 week

---

### Phase 3: Pilot Integration (ViloxTerm)

**Goal**: Migrate ViloxTerm to new system

**Tasks**:
- [ ] Update ViloxTermApp to extend VFThemedApplication
- [ ] Define `theme_config` with app defaults
- [ ] Update preferences model (ThemeCustomization dataclass)
- [ ] Update appearance preferences tab UI
- [ ] Implement preference persistence
- [ ] Remove old workarounds (ephemeral themes)
- [ ] End-to-end testing

**Deliverable**: ViloxTerm uses overlay system, tab bar customization works

**Duration**: ~1 week

---

### Phase 4: Standard UI Components

**Goal**: Reusable preference widgets for all apps

**Tasks**:
- [ ] ThemeSelectionWidget (base theme dropdown)
- [ ] ColorCustomizationWidget (color picker + preview)
- [ ] ThemePresetWidget (preset management, future)
- [ ] Documentation and examples
- [ ] Integrate into ViloxTerm (validate)

**Deliverable**: UI widget library for theme preferences

**Duration**: ~2 weeks

---

### Phase 5: Ecosystem Expansion

**Goal**: Adopt system in other apps

**Tasks**:
- [ ] ViloWeb: Add theme selection + optional customization
- [ ] Reamde: Add theme selection (no customization yet)
- [ ] Update all app templates
- [ ] Write developer guide
- [ ] Create video tutorial

**Deliverable**: All apps use consistent theme pattern

**Duration**: ~1 week

---

### Phase 6: Advanced Features (Future)

**Optional enhancements**:
- [ ] Preset system (named override sets)
- [ ] Import/export presets
- [ ] Theme marketplace
- [ ] Automatic theme updates
- [ ] Undo/redo for customizations

**Deliverable**: Power user features

**Duration**: TBD

---

## Success Metrics

### Developer Success

**Metric 1: Time to Add Theming**
- Target: < 5 minutes to add basic theming to new app
- Current: 2 lines of code (ThemedApplication)
- Future: 2 lines + declarative config (VFThemedApplication)

**Metric 2: Time to Add Customization**
- Target: < 30 minutes to add user customization
- Current: Not feasible (no API)
- Future: Add to `theme_config`, use standard UI widgets

**Metric 3: API Learnability**
- Target: 90% of developers understand API from examples alone
- Measure: Survey, documentation analytics

**Metric 4: Code Reduction**
- Target: 50% less code for theme customization vs. current workarounds
- Current: ~150 lines (ephemeral theme creation)
- Future: ~50 lines (declarative config + hooks)

---

### End-User Success

**Metric 1: Customization Adoption**
- Target: 20% of users customize at least one color
- Measure: Telemetry (optional, privacy-respecting)

**Metric 2: Theme Persistence**
- Target: 100% of customizations persist across restarts
- Measure: QA testing, user feedback

**Metric 3: User Satisfaction**
- Target: 4.5/5 stars for customization UX
- Measure: User survey

**Metric 4: Support Requests**
- Target: < 5% of users need help with customization
- Measure: Support ticket analysis

---

## Risks & Mitigations

### Risk 1: Complexity Creep

**Risk**: System becomes too complex, hurting developer experience

**Mitigation**:
- Follow "progressive enhancement" principle
- Keep basic cases simple (ThemedApplication unchanged)
- Extensive documentation and examples
- Usability testing with real developers

---

### Risk 2: Performance Impact

**Risk**: Overlay system slows widget rendering

**Mitigation**:
- Benchmark: Ensure < 1ms overhead per color lookup
- Cache effective theme (invalidate on override change)
- Optimize hot paths (token resolution)
- Performance tests in CI

---

### Risk 3: Breaking Changes

**Risk**: New API breaks existing apps

**Mitigation**:
- New API is additive (no removals)
- ThemedApplication unchanged (backward compatible)
- Migration guide for apps using workarounds
- Deprecation cycle for any future breaking changes

---

### Risk 4: Adoption Resistance

**Risk**: Developers prefer existing workarounds

**Mitigation**:
- Pilot with ViloxTerm (prove value)
- Provide migration guide
- Show code reduction and benefits
- Evangelize in documentation

---

## Conclusion

This vision defines a **unified, developer-friendly theme customization system** for the VFWidgets ecosystem that:

1. **Respects Architecture**
   - Clean separation of concerns (theme system / apps / widgets)
   - Proper MVC alignment
   - Design patterns applied correctly
   - Maintainable and extensible

2. **Empowers Developers**
   - Simple API for common cases
   - Progressive enhancement for advanced features
   - Declarative > imperative
   - Excellent documentation and examples

3. **Delights Users**
   - Discoverable customization
   - Safe experimentation
   - Persistent preferences
   - Consistent UI across apps

4. **Enables Ecosystem**
   - Base themes (Theme Studio)
   - App themes (developer branding)
   - User themes (personalization)
   - Reusable patterns and widgets

### Next Steps

1. ✅ **This Document**: Vision approved by stakeholders
2. → **Implementation Plan**: Detailed technical specification
3. → **Phase 1**: Implement overlay system
4. → **Pilot**: ViloxTerm migration
5. → **Rollout**: Expand to all apps

This system will become the **foundation for theme customization across all VFWidgets applications**, providing a consistent, powerful, and delightful experience for both developers and end users.

---

**Document Version**: 1.0.0-draft
**Status**: Awaiting stakeholder review
**Next Review**: After overlay system prototype
**Contacts**: VFWidgets Architecture Team
