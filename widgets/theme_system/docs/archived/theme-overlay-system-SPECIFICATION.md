# Theme Overlay System - Technical Specification

**Status**: Draft
**Version**: 1.0.0
**Date**: 2025-10-18

**Related Documents**:
- **Problem Analysis**: [theme-overlay-system-PROBLEM.md](./theme-overlay-system-PROBLEM.md) - What problem this solves
- **Vision Document**: [theme-customization-system-VISION.md](./theme-customization-system-VISION.md) - Architectural vision
- **Breaking Changes**: [BREAKING-CHANGES.md](./BREAKING-CHANGES.md) - Breaking changes tracking
- **Documentation Index**: [README-OVERLAY-SYSTEM.md](./README-OVERLAY-SYSTEM.md) - Navigation guide

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [API Specification](#api-specification)
4. [Data Model](#data-model)
5. [Implementation Plan](#implementation-plan)
6. [Migration Guide](#migration-guide)
7. [Testing Strategy](#testing-strategy)
8. [Performance Requirements](#performance-requirements)
9. [Security Considerations](#security-considerations)
10. [Appendix](#appendix)

---

## 1. Executive Summary

### 1.1 Purpose

This specification defines the technical implementation of the **Theme Overlay System** for VFWidgets. The overlay system enables runtime theme customization through a three-tier architecture while maintaining separation of concerns between the theme system and applications.

### 1.2 Goals

1. **Runtime Customization**: Enable color token overrides without creating ephemeral themes
2. **Persistence**: Provide clear API for apps to save/load user customizations
3. **Separation of Concerns**: Theme business logic in theme_system, persistence in apps
4. **Developer Experience**: Simple declarative API for common use cases
5. **API Improvements**: Fix design issues even if it requires breaking changes

### 1.3 Success Criteria

- ✅ Apps can override theme colors at runtime
- ✅ Overrides persist across application restarts
- ✅ Theme changes notify all widgets (<100ms)
- ✅ All breaking changes documented with migration paths
- ✅ Migration plan for ViloxTerm, ViloWeb, Reamde
- ✅ Comprehensive test coverage (>90%)

### 1.4 Breaking Changes Policy

**Philosophy**: We prioritize correctness and long-term maintainability over backward compatibility. If the current API has design flaws, we fix them now even if it requires breaking changes.

**Requirements**:
1. **Document All Breaks**: Every breaking change must be documented in `BREAKING-CHANGES.md`
2. **Provide Migration Paths**: Each breaking change must include:
   - What breaks and why
   - How to migrate (code examples)
   - Automated migration tools where possible
3. **Track Affected Apps**: Identify which VFWidgets apps are affected
4. **Fix Internal Apps**: All apps in the monorepo must be updated as part of implementation

**Breaking Changes Tracking**:
- Document: `widgets/theme_system/docs/BREAKING-CHANGES.md`
- Updated continuously during implementation
- Reviewed before each phase gate

---

## 2. System Architecture

### 2.1 Three-Tier Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Effective Theme                          │
│  (Runtime composition of base theme + app + user overrides) │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
         ┌────────────────────┴────────────────────┐
         │                                         │
┌────────┴──────────┐  ┌──────────────┐  ┌────────┴─────────┐
│   Base Theme      │  │ App Overrides│  │  User Overrides  │
│  (Theme Studio)   │  │  (Developer) │  │   (End User)     │
├───────────────────┤  ├──────────────┤  ├──────────────────┤
│ dark.json         │  │ Primary color│  │ Tab bar color    │
│ light.json        │  │ Brand colors │  │ Focus border     │
│ high-contrast.json│  │ Font sizes   │  │ Terminal bg      │
└───────────────────┘  └──────────────┘  └──────────────────┘
     Priority: 1            Priority: 2        Priority: 3
                                                (Highest)
```

### 2.2 Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│  ┌──────────────────┐         ┌─────────────────────┐      │
│  │ VFThemedApp      │────────▶│  QSettings          │      │
│  │ (New Base Class) │         │  (Persistence)      │      │
│  └────────┬─────────┘         └─────────────────────┘      │
└───────────┼──────────────────────────────────────────────────┘
            │ Uses
            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Theme System Layer                         │
│  ┌──────────────────┐         ┌─────────────────────┐      │
│  │ ThemeManager     │────────▶│ OverrideRegistry    │      │
│  │ (Enhanced)       │         │ (New Component)     │      │
│  └────────┬─────────┘         └─────────────────────┘      │
│           │                                                  │
│           │ Notifies                                         │
│           ▼                                                  │
│  ┌──────────────────┐                                       │
│  │ ThemedWidget     │ (May have breaking changes if needed) │
│  └──────────────────┘                                       │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 Core Components

#### ThemeManager (Enhanced)
**Location**: `widgets/theme_system/src/vfwidgets_theme/core/theme_manager.py`

**Responsibilities**:
- Manage base theme selection
- Store app-level and user-level overrides
- Compute effective theme values
- Notify widgets of theme changes

**New Attributes**:
```python
_override_registry: OverrideRegistry  # NEW: Manages layered overrides
```

#### OverrideRegistry (New)
**Location**: `widgets/theme_system/src/vfwidgets_theme/core/override_registry.py`

**Responsibilities**:
- Store layered overrides (app + user)
- Resolve override priority
- Validate override values
- Serialize/deserialize for persistence

#### VFThemedApplication (New)
**Location**: `widgets/theme_system/src/vfwidgets_theme/widgets/vf_themed_application.py`

**Responsibilities**:
- Declarative theme configuration
- Load/save user overrides to QSettings
- Template method for app initialization
- Convenience methods for common operations

---

## 3. API Specification

### 3.1 ThemeManager API Extensions

#### 3.1.1 Override Management

```python
from vfwidgets_theme.core.theme_manager import ThemeManager

class ThemeManager:
    """Enhanced theme manager with overlay support."""

    # ─── Override Management ───

    def set_app_override(
        self,
        token: str,
        value: str,
        validate: bool = True
    ) -> bool:
        """Set application-level color override.

        App overrides have lower priority than user overrides but higher
        than base theme values. These are typically set by developers to
        provide brand colors or application-specific defaults.

        Args:
            token: Color token name (e.g., "editorGroupHeader.tabsBackground")
            value: Color value in hex format (e.g., "#1e1e1e")
            validate: Whether to validate color format (default: True)

        Returns:
            True if override was set successfully, False otherwise

        Raises:
            ValueError: If color format is invalid and validate=True
            KeyError: If token name is not recognized

        Example:
            >>> manager = ThemeManager.instance()
            >>> manager.set_app_override("colors.primary", "#007bff")
            True

        Thread Safety:
            This method is thread-safe and can be called from any thread.
            Widget notifications are dispatched on the main thread.
        """
        pass

    def set_user_override(
        self,
        token: str,
        value: str,
        validate: bool = True,
        persist: bool = False
    ) -> bool:
        """Set user-level color override.

        User overrides have the highest priority and override both app
        overrides and base theme values. These are typically set by end
        users through application settings UI.

        Args:
            token: Color token name
            value: Color value in hex format
            validate: Whether to validate color format
            persist: Whether to emit signal for app to persist (default: False)

        Returns:
            True if override was set successfully

        Raises:
            ValueError: If color format is invalid and validate=True
            KeyError: If token name is not recognized

        Signals:
            If persist=True, emits override_changed signal for apps to save

        Example:
            >>> manager = ThemeManager.instance()
            >>> manager.set_user_override(
            ...     "editorGroupHeader.tabsBackground",
            ...     "#2d2d30",
            ...     persist=True
            ... )
            True
        """
        pass

    def clear_app_override(self, token: str) -> bool:
        """Clear application-level override for a token.

        Args:
            token: Token to clear override for

        Returns:
            True if override was cleared, False if no override existed
        """
        pass

    def clear_user_override(self, token: str, persist: bool = False) -> bool:
        """Clear user-level override for a token.

        Args:
            token: Token to clear override for
            persist: Whether to emit signal for app to persist

        Returns:
            True if override was cleared, False if no override existed
        """
        pass

    def clear_all_user_overrides(self, persist: bool = False) -> int:
        """Clear all user overrides.

        Args:
            persist: Whether to emit signal for app to persist

        Returns:
            Number of overrides cleared
        """
        pass

    def get_app_overrides(self) -> dict[str, str]:
        """Get all application-level overrides.

        Returns:
            Dictionary mapping token names to color values

        Example:
            >>> manager.get_app_overrides()
            {
                "colors.primary": "#007bff",
                "button.background": "#007bff"
            }
        """
        pass

    def get_user_overrides(self) -> dict[str, str]:
        """Get all user-level overrides.

        This method is used by applications to persist user customizations.

        Returns:
            Dictionary mapping token names to color values

        Example:
            >>> overrides = manager.get_user_overrides()
            >>> settings.setValue("theme/user_overrides", overrides)
        """
        pass

    def set_user_overrides_bulk(
        self,
        overrides: dict[str, str],
        validate: bool = True
    ) -> tuple[int, list[str]]:
        """Set multiple user overrides at once.

        This is more efficient than calling set_user_override() repeatedly
        as it only triggers one widget notification at the end.

        Args:
            overrides: Dictionary mapping token names to color values
            validate: Whether to validate color formats

        Returns:
            Tuple of (success_count, failed_tokens)

        Example:
            >>> overrides = {
            ...     "editorGroupHeader.tabsBackground": "#2d2d30",
            ...     "terminal.background": "#1e1e1e"
            ... }
            >>> success, failed = manager.set_user_overrides_bulk(overrides)
            >>> print(f"Applied {success} overrides, {len(failed)} failed")
        """
        pass

    # ─── Effective Value Resolution ───

    def get_effective_color(self, token: str) -> str:
        """Get effective color value with override resolution.

        Resolution priority (highest to lowest):
        1. User override
        2. App override
        3. Base theme value
        4. Fallback value

        Args:
            token: Color token name

        Returns:
            Color value in hex format

        Example:
            >>> # Base theme has "#1e1e1e"
            >>> # App override sets "#2d2d30"
            >>> # User override sets "#3e3e42"
            >>> manager.get_effective_color("editor.background")
            "#3e3e42"  # User override wins
        """
        pass

    def get_all_effective_colors(self) -> dict[str, str]:
        """Get all effective color values.

        Returns complete color dictionary with all overrides applied.
        Useful for debugging or exporting effective theme.

        Returns:
            Dictionary mapping all token names to effective color values
        """
        pass
```

#### 3.1.2 New Signals

```python
from PySide6.QtCore import Signal

class ThemeManager(QObject):
    # ─── New Signals ───

    override_changed = Signal(str, str)  # (token, value)
    """Emitted when an override is set/cleared.

    Args:
        token: The token that changed
        value: New effective value (after override resolution)
    """

    overrides_cleared = Signal()
    """Emitted when all overrides are cleared."""
```

### 3.2 OverrideRegistry API

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class OverrideLayer:
    """Represents a single override layer."""
    name: str  # "app" or "user"
    overrides: dict[str, str]  # token -> color value
    priority: int  # Higher = higher priority


class OverrideRegistry:
    """Manages layered color overrides with priority resolution.

    This class is the core of the overlay system. It maintains separate
    override layers and resolves them according to priority.

    Thread Safety:
        All public methods are thread-safe.
    """

    def __init__(self):
        """Initialize registry with empty override layers."""
        pass

    # ─── Layer Management ───

    def set_override(
        self,
        layer: str,  # "app" or "user"
        token: str,
        value: str
    ) -> None:
        """Set override in specific layer.

        Args:
            layer: Layer name ("app" or "user")
            token: Color token name
            value: Color value in hex format

        Raises:
            ValueError: If layer name is invalid
        """
        pass

    def clear_override(self, layer: str, token: str) -> bool:
        """Clear override from specific layer.

        Args:
            layer: Layer name
            token: Token to clear

        Returns:
            True if override existed and was cleared
        """
        pass

    def clear_layer(self, layer: str) -> int:
        """Clear all overrides in a layer.

        Args:
            layer: Layer name

        Returns:
            Number of overrides cleared
        """
        pass

    def get_layer_overrides(self, layer: str) -> dict[str, str]:
        """Get all overrides in a specific layer.

        Args:
            layer: Layer name

        Returns:
            Copy of override dictionary for the layer
        """
        pass

    # ─── Resolution ───

    def resolve(
        self,
        token: str,
        base_value: Optional[str] = None
    ) -> Optional[str]:
        """Resolve effective value for a token.

        Resolution order (highest to lowest priority):
        1. User layer override
        2. App layer override
        3. Base value (if provided)
        4. None

        Args:
            token: Token to resolve
            base_value: Base theme value (optional)

        Returns:
            Effective color value or None if not found
        """
        pass

    def resolve_all(
        self,
        base_colors: dict[str, str]
    ) -> dict[str, str]:
        """Resolve all tokens with overrides applied.

        Args:
            base_colors: Base theme color dictionary

        Returns:
            Complete color dictionary with all overrides applied
        """
        pass

    # ─── Serialization ───

    def to_dict(self) -> dict[str, dict[str, str]]:
        """Serialize registry to dictionary.

        Returns:
            Dictionary with layer names as keys, override dicts as values

        Example:
            {
                "app": {"colors.primary": "#007bff"},
                "user": {"editor.background": "#1e1e1e"}
            }
        """
        pass

    @classmethod
    def from_dict(cls, data: dict[str, dict[str, str]]) -> "OverrideRegistry":
        """Deserialize registry from dictionary.

        Args:
            data: Dictionary from to_dict()

        Returns:
            New OverrideRegistry instance
        """
        pass
```

### 3.3 VFThemedApplication API

```python
from typing import Optional
from PySide6.QtWidgets import QApplication
from vfwidgets_theme import ThemedApplication

class VFThemedApplication(ThemedApplication):
    """Base application class with declarative theme configuration.

    This class provides a template method pattern for applications that
    want to use the theme overlay system. It handles common initialization,
    loading user preferences, and saving overrides.

    Example:
        >>> class MyApp(VFThemedApplication):
        ...     theme_config = {
        ...         "base_theme": "dark",
        ...         "app_overrides": {
        ...             "colors.primary": "#007bff"
        ...         },
        ...         "allow_user_customization": True,
        ...         "customizable_tokens": [
        ...             "editorGroupHeader.tabsBackground",
        ...             "terminal.background"
        ...         ]
        ...     }
        ...
        >>> app = MyApp(sys.argv)
        >>> sys.exit(app.exec())
    """

    # ─── Class-level Configuration ───

    theme_config: dict = {
        "base_theme": "dark",  # Default base theme name
        "app_overrides": {},   # App-level color overrides
        "allow_user_customization": True,  # Allow runtime customization
        "customizable_tokens": [],  # List of tokens users can customize
        "persist_base_theme": True,  # Save base theme selection
        "persist_user_overrides": True,  # Save user overrides
        "settings_key_prefix": "theme/",  # QSettings key prefix
    }

    def __init__(
        self,
        argv: list[str],
        app_id: Optional[str] = None
    ):
        """Initialize application with theme configuration.

        This follows the template method pattern:
        1. Initialize ThemedApplication
        2. Apply app-level overrides
        3. Load user preferences
        4. Apply user overrides

        Args:
            argv: Command-line arguments
            app_id: Application ID for settings (default: app name)
        """
        pass

    # ─── Template Methods (Override in Subclass) ───

    def get_settings_organization(self) -> str:
        """Get organization name for QSettings.

        Default: Returns application organization domain or name.
        Override to customize.
        """
        return self.organizationName() or "VFWidgets"

    def get_settings_application(self) -> str:
        """Get application name for QSettings.

        Default: Returns application name.
        Override to customize.
        """
        return self.applicationName() or "VFApp"

    def load_user_preferences(self) -> dict[str, str]:
        """Load user override preferences from storage.

        Default: Loads from QSettings at "theme/user_overrides".
        Override to use custom persistence (e.g., JSON file, database).

        Returns:
            Dictionary of user overrides (token -> color)
        """
        pass

    def save_user_preferences(self, overrides: dict[str, str]) -> None:
        """Save user override preferences to storage.

        Default: Saves to QSettings at "theme/user_overrides".
        Override to use custom persistence.

        Args:
            overrides: Dictionary of user overrides to save
        """
        pass

    # ─── Convenience Methods ───

    def customize_color(
        self,
        token: str,
        color: str,
        persist: bool = True
    ) -> bool:
        """Customize a color token (user override).

        This is a convenience method that:
        1. Validates the token is customizable
        2. Sets the user override
        3. Optionally persists the change

        Args:
            token: Token to customize
            color: New color value
            persist: Whether to save immediately

        Returns:
            True if successful

        Raises:
            ValueError: If token is not customizable or color is invalid
        """
        pass

    def reset_color(self, token: str, persist: bool = True) -> bool:
        """Reset a color token to default (clear user override).

        Args:
            token: Token to reset
            persist: Whether to save immediately

        Returns:
            True if override was cleared
        """
        pass

    def reset_all_colors(self, persist: bool = True) -> int:
        """Reset all color customizations.

        Args:
            persist: Whether to save immediately

        Returns:
            Number of overrides cleared
        """
        pass

    def get_customizable_tokens(self) -> list[str]:
        """Get list of tokens that users can customize.

        Returns:
            List from theme_config["customizable_tokens"]
        """
        return self.theme_config.get("customizable_tokens", [])

    def is_customizable(self, token: str) -> bool:
        """Check if a token can be customized by users.

        Args:
            token: Token to check

        Returns:
            True if token is in customizable list (or list is empty)
        """
        pass
```

### 3.4 Usage Examples

#### 3.4.1 Simple Application (No User Customization)

```python
from vfwidgets_theme.widgets import VFThemedApplication

class SimpleApp(VFThemedApplication):
    theme_config = {
        "base_theme": "dark",
        "allow_user_customization": False,  # No runtime customization
    }

app = SimpleApp(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
```

#### 3.4.2 Branded Application (App Overrides)

```python
class BrandedApp(VFThemedApplication):
    theme_config = {
        "base_theme": "dark",
        "app_overrides": {
            # Brand colors
            "colors.primary": "#007bff",
            "colors.secondary": "#6c757d",
            "button.background": "#007bff",
            "button.hoverBackground": "#0056b3",
        },
        "allow_user_customization": False,
    }

app = BrandedApp(sys.argv)
# App colors are automatically applied
```

#### 3.4.3 Customizable Application (User Overrides)

```python
from PySide6.QtCore import QSettings

class CustomizableApp(VFThemedApplication):
    theme_config = {
        "base_theme": "dark",
        "app_overrides": {
            "colors.primary": "#007bff",
        },
        "allow_user_customization": True,
        "customizable_tokens": [
            "editorGroupHeader.tabsBackground",
            "terminal.background",
            "terminal.foreground",
        ],
        "persist_user_overrides": True,
    }

app = CustomizableApp(sys.argv)

# User customizes color via UI
def on_color_changed(token: str, color: str):
    app.customize_color(token, color, persist=True)

# Reset to defaults
def on_reset_clicked():
    app.reset_all_colors(persist=True)
```

#### 3.4.4 Advanced: Manual Override Management

```python
from vfwidgets_theme.core.theme_manager import ThemeManager

# Get theme manager instance
manager = ThemeManager.instance()

# Set app-level override (developer defaults)
manager.set_app_override("colors.primary", "#ff6b6b")

# Set user-level override (runtime customization)
manager.set_user_override(
    "editorGroupHeader.tabsBackground",
    "#2d2d30",
    persist=True  # Triggers signal for app to save
)

# Get effective value (with all overrides applied)
effective = manager.get_effective_color("editorGroupHeader.tabsBackground")
print(f"Effective color: {effective}")

# Get all user overrides for persistence
overrides = manager.get_user_overrides()
settings = QSettings("MyOrg", "MyApp")
settings.setValue("theme/user_overrides", overrides)

# Load on startup
saved_overrides = settings.value("theme/user_overrides", {})
if saved_overrides:
    manager.set_user_overrides_bulk(saved_overrides)
```

---

## 4. Data Model

### 4.1 Override Storage Format

#### 4.1.1 In-Memory (OverrideRegistry)

```python
{
    "app": {
        "colors.primary": "#007bff",
        "button.background": "#007bff",
        "button.hoverBackground": "#0056b3"
    },
    "user": {
        "editorGroupHeader.tabsBackground": "#2d2d30",
        "terminal.background": "#1e1e1e"
    }
}
```

#### 4.1.2 QSettings Persistence

**Key**: `theme/user_overrides`
**Type**: `QVariant<QMap<QString, QString>>`

```python
from PySide6.QtCore import QSettings

settings = QSettings("ViloxTerm", "ViloxTerm")

# Save
overrides = {
    "editorGroupHeader.tabsBackground": "#2d2d30",
    "terminal.background": "#1e1e1e"
}
settings.setValue("theme/user_overrides", overrides)

# Load
saved = settings.value("theme/user_overrides", {})
# Returns: dict[str, str] or empty dict
```

**Storage Location**:
- Linux: `~/.config/ViloxTerm/ViloxTerm.conf`
- Windows: `HKEY_CURRENT_USER\Software\ViloxTerm\ViloxTerm`
- macOS: `~/Library/Preferences/com.viloforge.ViloxTerm.plist`

### 4.2 Color Value Validation

#### 4.2.1 Supported Formats

```python
# Hex formats (case-insensitive)
"#1e1e1e"      # ✅ 6-digit hex
"#1E1E1E"      # ✅ Uppercase
"#fff"         # ✅ 3-digit hex (expanded to #ffffff)
"1e1e1e"       # ❌ Missing #

# Named colors (Qt standard)
"red"          # ✅ Qt named color
"transparent"  # ✅ Special value

# RGB/RGBA formats
"rgb(30,30,30)"        # ✅ RGB
"rgba(30,30,30,0.5)"   # ✅ RGBA with alpha

# Invalid
""             # ❌ Empty string
"#gggggg"      # ❌ Invalid hex
"notacolor"    # ❌ Unknown name
```

#### 4.2.2 Validation Function

```python
from PySide6.QtGui import QColor

def validate_color(value: str) -> tuple[bool, str]:
    """Validate color value format.

    Args:
        value: Color value to validate

    Returns:
        Tuple of (is_valid, normalized_value)

    Examples:
        >>> validate_color("#1e1e1e")
        (True, "#1e1e1e")

        >>> validate_color("#fff")
        (True, "#ffffff")

        >>> validate_color("notacolor")
        (False, "")
    """
    if not value:
        return False, ""

    color = QColor(value)
    if not color.isValid():
        return False, ""

    # Normalize to #RRGGBB format
    normalized = color.name()  # Always returns #rrggbb
    return True, normalized
```

### 4.3 Token Name Validation

```python
def validate_token(token: str) -> bool:
    """Validate color token name.

    Valid token names must:
    - Be non-empty
    - Contain only alphanumeric, dots, and underscores
    - Start with a letter

    Args:
        token: Token name to validate

    Returns:
        True if valid

    Examples:
        >>> validate_token("editor.background")
        True

        >>> validate_token("colors.primary")
        True

        >>> validate_token("123invalid")
        False

        >>> validate_token("has spaces")
        False
    """
    import re

    if not token:
        return False

    # Pattern: starts with letter, contains alphanumeric/dots/underscores
    pattern = r'^[a-zA-Z][a-zA-Z0-9._]*$'
    return bool(re.match(pattern, token))
```

---

## 5. Implementation Plan

### 5.1 Phase 0: Preparation (Week 1)

**Goal**: Set up development environment and write comprehensive tests

#### Tasks:

1. **Create test infrastructure**
   - [ ] Create `tests/test_override_registry.py`
   - [ ] Create `tests/test_theme_manager_overlays.py`
   - [ ] Create `tests/test_vf_themed_application.py`
   - [ ] Set up pytest fixtures for common scenarios

2. **Write failing tests (TDD approach)**
   - [ ] Test override priority resolution
   - [ ] Test bulk operations
   - [ ] Test persistence round-trip
   - [ ] Test validation errors
   - [ ] Test thread safety
   - [ ] Test signal emissions

3. **Document test scenarios**
   - [ ] Create `docs/test-scenarios-overlay-system.md`
   - [ ] Define edge cases
   - [ ] Define performance benchmarks

4. **Create breaking changes tracking document**
   - [ ] Create `docs/BREAKING-CHANGES.md`
   - [ ] Set up template with sections: What Breaks, Why, Migration Path, Affected Apps
   - [ ] Document policy for tracking changes during implementation

**Exit Criteria**:
- ✅ Comprehensive test suite written (all failing)
- ✅ Test coverage plan documented
- ✅ Performance benchmarks defined
- ✅ Breaking changes tracking document ready

### 5.2 Phase 1: Core Implementation (Week 2-3)

**Goal**: Implement OverrideRegistry and enhance ThemeManager

#### Tasks:

1. **Implement OverrideRegistry**
   - [ ] Create `core/override_registry.py`
   - [ ] Implement layer management (app/user)
   - [ ] Implement priority resolution
   - [ ] Implement serialization (to_dict/from_dict)
   - [ ] Add thread safety (locks)
   - [ ] Write unit tests

2. **Enhance ThemeManager**
   - [ ] Add `_override_registry` attribute
   - [ ] Implement `set_app_override()`
   - [ ] Implement `set_user_override()`
   - [ ] Implement `get_effective_color()`
   - [ ] Implement bulk operations
   - [ ] Add new signals (override_changed, overrides_cleared)
   - [ ] Update `get_color()` to use overrides
   - [ ] Write integration tests

3. **Update ColorTokenRegistry**
   - [ ] Modify `get()` to check overrides via ThemeManager
   - [ ] Ensure fallback chain still works
   - [ ] Write integration tests

**Exit Criteria**:
- ✅ OverrideRegistry fully implemented with tests
- ✅ ThemeManager enhancements complete with tests
- ✅ All Phase 0 tests passing
- ✅ All breaking changes documented in BREAKING-CHANGES.md

### 5.3 Phase 2: Application Support (Week 4)

**Goal**: Implement VFThemedApplication base class

#### Tasks:

1. **Implement VFThemedApplication**
   - [ ] Create `widgets/vf_themed_application.py`
   - [ ] Implement template method pattern
   - [ ] Implement `load_user_preferences()`
   - [ ] Implement `save_user_preferences()`
   - [ ] Implement convenience methods
   - [ ] Add declarative theme_config support
   - [ ] Write tests

2. **Create example applications**
   - [ ] Simple app (no customization)
   - [ ] Branded app (app overrides)
   - [ ] Customizable app (user overrides)
   - [ ] Advanced app (manual management)

3. **Update breaking changes tracking**
   - [ ] Document any API changes in VFThemedApplication
   - [ ] Update BREAKING-CHANGES.md with migration examples

**Exit Criteria**:
- ✅ VFThemedApplication implemented with tests
- ✅ Example apps run successfully
- ✅ Documentation complete
- ✅ Breaking changes documented and reviewed

### 5.4 Phase 3: Migration - ViloxTerm (Week 5-6)

**Goal**: Migrate ViloxTerm to use overlay system

#### Tasks:

1. **Audit current ViloxTerm theme usage**
   - [ ] Document all theme-related code
   - [ ] Identify customization points
   - [ ] Plan migration strategy

2. **Implement ViloxTerm migration**
   - [ ] Extend VFThemedApplication
   - [ ] Define theme_config with app overrides
   - [ ] Migrate preferences model
   - [ ] Update theme dialog UI
   - [ ] Add tab bar customization UI
   - [ ] Add focus border customization UI
   - [ ] Update startup code to load overrides
   - [ ] Write migration guide for users

3. **Fix ChromeTabRenderer color fallback**
   - [ ] Fix fallback order for tab bar background
   - [ ] Test with various themes
   - [ ] Document change

4. **Verify migration and update tracking**
   - [ ] Test ViloxTerm migration thoroughly
   - [ ] Document any unexpected breaking changes in BREAKING-CHANGES.md
   - [ ] Update migration guide based on real migration experience

**Exit Criteria**:
- ✅ ViloxTerm uses overlay system
- ✅ User preferences migrate automatically
- ✅ Tab bar customization works
- ✅ No regressions in existing functionality
- ✅ Migration experience documented for other apps

### 5.5 Phase 4: Migration - Other Apps (Week 7)

**Goal**: Standardize theme usage across all apps

#### Tasks:

1. **Migrate ViloWeb**
   - [ ] Switch to VFThemedApplication
   - [ ] Define app overrides (if needed)
   - [ ] Test theme loading

2. **Migrate Reamde**
   - [ ] Switch to VFThemedApplication
   - [ ] Simplify with theme_config
   - [ ] Remove manual theme setup

3. **Update Theme Studio**
   - [ ] Keep as plain QApplication (correct pattern)
   - [ ] Update preview to test overlay system

4. **Finalize breaking changes documentation**
   - [ ] Review all app migrations
   - [ ] Ensure BREAKING-CHANGES.md is complete
   - [ ] Create migration checklist for external users

**Exit Criteria**:
- ✅ All apps use consistent theme pattern
- ✅ Documentation updated
- ✅ Examples updated
- ✅ All internal apps migrated successfully
- ✅ BREAKING-CHANGES.md complete and reviewed

### 5.6 Phase 5: Documentation & Polish (Week 8)

**Goal**: Comprehensive documentation and developer experience

#### Tasks:

1. **API Documentation**
   - [ ] Document all new public APIs
   - [ ] Add docstring examples
   - [ ] Generate API reference

2. **User Documentation**
   - [ ] Migration guide (existing apps)
   - [ ] Developer tutorial (new apps)
   - [ ] Best practices guide
   - [ ] FAQ

3. **Polish**
   - [ ] Performance profiling
   - [ ] Memory leak checks
   - [ ] Error message improvements
   - [ ] Logging improvements

**Exit Criteria**:
- ✅ Complete documentation
- ✅ Performance meets requirements
- ✅ No memory leaks

---

## 5.7 Breaking Changes Tracking Document Structure

**File**: `widgets/theme_system/docs/BREAKING-CHANGES.md`

**Purpose**: Continuously updated document tracking all breaking changes introduced during implementation.

**Template**:

```markdown
# Breaking Changes - Theme Overlay System

**Version**: 2.0.0
**Date**: 2025-10-18 - Ongoing

This document tracks all breaking changes introduced by the Theme Overlay System implementation.

---

## Summary

Total breaking changes: [N]
Affected apps in monorepo: ViloxTerm, ViloWeb, Reamde
Affected external users: [Estimated count]

---

## Breaking Change #1: [Title]

**Component**: [ThemeManager / ThemedWidget / ThemedApplication / etc.]
**Severity**: [High / Medium / Low]
**Date Introduced**: [Date]
**Phase**: [Phase number]

### What Breaks

[Detailed description of what code will break]

Example:
```python
# This code will no longer work:
manager.get_color("editor.background")

# Error: AttributeError: 'ThemeManager' object has no attribute 'get_color'
```

### Why This Change

[Rationale for the breaking change - what design problem does it fix?]

### Migration Path

**Automatic Migration**: [Yes/No - describe if tool available]

**Manual Migration**:

```python
# Old code:
manager.get_color("editor.background")

# New code:
manager.get_effective_color("editor.background")
```

### Affected Apps

- [ ] ViloxTerm: [Status - Not started / In progress / Migrated]
  - Files affected: [List files]
  - Migration complexity: [Simple / Moderate / Complex]

- [ ] ViloWeb: [Status]
  - Files affected: [List files]
  - Migration complexity: [Simple / Moderate / Complex]

- [ ] Reamde: [Status]
  - Files affected: [List files]
  - Migration complexity: [Simple / Moderate / Complex]

- [ ] Theme Studio: [Status]
  - Files affected: [List files]
  - Migration complexity: [Simple / Moderate / Complex]

### External User Impact

[Estimated number of external projects affected]
[Mitigation strategy]

---

## Breaking Change #2: [Title]

[Repeat template...]

---

## Appendix: Migration Checklist for External Users

- [ ] Read BREAKING-CHANGES.md completely
- [ ] Identify which changes affect your code
- [ ] Follow migration paths for each breaking change
- [ ] Run tests to verify migration
- [ ] Update dependencies to vfwidgets-theme >= 2.0.0
```

**Update Process**:
1. Developer discovers/introduces breaking change during implementation
2. Immediately document in BREAKING-CHANGES.md using template
3. Add migration path with code examples
4. Mark affected apps
5. Review at each phase gate
6. Update as migration proceeds

---

## 6. Migration Guide

**Important**: This migration guide shows the expected migration paths. As implementation proceeds, some API details may change if breaking changes are needed to fix design issues. All breaking changes will be documented in `BREAKING-CHANGES.md` with updated migration paths.

### 6.1 For Application Developers

#### 6.1.1 Migrating from ThemedApplication

**Before (Old Pattern)**:
```python
from vfwidgets_theme import ThemedApplication

class MyApp(ThemedApplication):
    def __init__(self, argv):
        super().__init__(argv)

        # Manual theme setup
        self.set_theme("dark")

app = MyApp(sys.argv)
```

**After (New Pattern)**:
```python
from vfwidgets_theme.widgets import VFThemedApplication

class MyApp(VFThemedApplication):
    theme_config = {
        "base_theme": "dark",
        "app_overrides": {},
        "allow_user_customization": False,
    }

app = MyApp(sys.argv)
# Theme automatically loaded and configured
```

#### 6.1.2 Adding User Customization

**Step 1**: Define customizable tokens in theme_config
```python
class MyApp(VFThemedApplication):
    theme_config = {
        "base_theme": "dark",
        "allow_user_customization": True,
        "customizable_tokens": [
            "editorGroupHeader.tabsBackground",
            "terminal.background",
        ],
    }
```

**Step 2**: Build UI for customization
```python
from PySide6.QtWidgets import QColorDialog

def on_customize_tab_bar():
    current = app.theme_manager.get_effective_color(
        "editorGroupHeader.tabsBackground"
    )
    color = QColorDialog.getColor(QColor(current))

    if color.isValid():
        app.customize_color(
            "editorGroupHeader.tabsBackground",
            color.name(),
            persist=True
        )
```

**Step 3**: Add reset functionality
```python
def on_reset():
    count = app.reset_all_colors(persist=True)
    QMessageBox.information(
        None,
        "Reset",
        f"Reset {count} customizations"
    )
```

### 6.2 For Widget Developers

**Expected**: No changes required for most widgets.

The overlay system is designed to be transparent to widgets - they receive updated colors via the existing notification mechanism. However, if API improvements are needed in ThemedWidget during implementation, those changes will be documented in `BREAKING-CHANGES.md` with migration paths.

**Current expected pattern (may evolve)**:
```python
from vfwidgets_theme import ThemedWidget

class MyWidget(ThemedWidget):
    theme_config = {
        "background": "editor.background",
        "foreground": "editor.foreground",
    }

    # Widget automatically gets updated colors
    # whether from base theme or overrides
```

**Action for widget developers**: Monitor `BREAKING-CHANGES.md` during the v2.0.0 implementation period.

---

## 7. Testing Strategy

### 7.1 Unit Tests

#### 7.1.1 OverrideRegistry Tests

**File**: `tests/test_override_registry.py`

```python
import pytest
from vfwidgets_theme.core.override_registry import OverrideRegistry

class TestOverrideRegistry:
    """Unit tests for OverrideRegistry."""

    def test_set_app_override(self):
        """Test setting app-level override."""
        registry = OverrideRegistry()
        registry.set_override("app", "colors.primary", "#007bff")

        overrides = registry.get_layer_overrides("app")
        assert overrides["colors.primary"] == "#007bff"

    def test_set_user_override(self):
        """Test setting user-level override."""
        registry = OverrideRegistry()
        registry.set_override("user", "editor.background", "#1e1e1e")

        overrides = registry.get_layer_overrides("user")
        assert overrides["editor.background"] == "#1e1e1e"

    def test_priority_resolution(self):
        """Test that user override takes priority over app override."""
        registry = OverrideRegistry()

        # Set app override
        registry.set_override("app", "colors.primary", "#007bff")

        # Set user override for same token
        registry.set_override("user", "colors.primary", "#ff6b6b")

        # User override should win
        result = registry.resolve("colors.primary")
        assert result == "#ff6b6b"

    def test_resolve_with_base_value(self):
        """Test resolution falls back to base value."""
        registry = OverrideRegistry()

        # No overrides set
        result = registry.resolve("editor.background", base_value="#1e1e1e")
        assert result == "#1e1e1e"

    def test_resolve_all(self):
        """Test resolving all tokens."""
        registry = OverrideRegistry()
        registry.set_override("app", "colors.primary", "#007bff")
        registry.set_override("user", "colors.secondary", "#ff6b6b")

        base_colors = {
            "colors.primary": "#ffffff",
            "colors.secondary": "#000000",
            "colors.tertiary": "#cccccc",
        }

        result = registry.resolve_all(base_colors)

        assert result["colors.primary"] == "#007bff"  # App override
        assert result["colors.secondary"] == "#ff6b6b"  # User override
        assert result["colors.tertiary"] == "#cccccc"  # Base value

    def test_clear_override(self):
        """Test clearing single override."""
        registry = OverrideRegistry()
        registry.set_override("user", "colors.primary", "#007bff")

        cleared = registry.clear_override("user", "colors.primary")
        assert cleared is True

        overrides = registry.get_layer_overrides("user")
        assert "colors.primary" not in overrides

    def test_clear_layer(self):
        """Test clearing entire layer."""
        registry = OverrideRegistry()
        registry.set_override("user", "colors.primary", "#007bff")
        registry.set_override("user", "colors.secondary", "#ff6b6b")

        count = registry.clear_layer("user")
        assert count == 2

        overrides = registry.get_layer_overrides("user")
        assert len(overrides) == 0

    def test_serialization(self):
        """Test to_dict and from_dict round-trip."""
        registry = OverrideRegistry()
        registry.set_override("app", "colors.primary", "#007bff")
        registry.set_override("user", "editor.background", "#1e1e1e")

        # Serialize
        data = registry.to_dict()

        # Deserialize
        restored = OverrideRegistry.from_dict(data)

        # Verify
        assert restored.get_layer_overrides("app") == {"colors.primary": "#007bff"}
        assert restored.get_layer_overrides("user") == {"editor.background": "#1e1e1e"}
```

#### 7.1.2 ThemeManager Tests

**File**: `tests/test_theme_manager_overlays.py`

```python
import pytest
from PySide6.QtCore import QSignalSpy
from vfwidgets_theme.core.theme_manager import ThemeManager
from vfwidgets_theme.core.theme import Theme

class TestThemeManagerOverlays:
    """Tests for ThemeManager overlay functionality."""

    @pytest.fixture
    def manager(self, qapp):
        """Create fresh ThemeManager instance."""
        # Reset singleton
        ThemeManager._instance = None
        manager = ThemeManager.instance()

        # Load a base theme
        from vfwidgets_theme.importers import load_builtin_theme
        theme = load_builtin_theme("dark")
        manager.set_theme(theme)

        return manager

    def test_set_app_override(self, manager):
        """Test setting app-level override."""
        success = manager.set_app_override("colors.primary", "#007bff")
        assert success is True

        overrides = manager.get_app_overrides()
        assert overrides["colors.primary"] == "#007bff"

    def test_set_user_override(self, manager):
        """Test setting user-level override."""
        success = manager.set_user_override("editor.background", "#1e1e1e")
        assert success is True

        overrides = manager.get_user_overrides()
        assert overrides["editor.background"] == "#1e1e1e"

    def test_get_effective_color(self, manager):
        """Test effective color resolution."""
        # Set app override
        manager.set_app_override("colors.primary", "#007bff")

        # Set user override for same token
        manager.set_user_override("colors.primary", "#ff6b6b")

        # User override should win
        effective = manager.get_effective_color("colors.primary")
        assert effective == "#ff6b6b"

    def test_override_changed_signal(self, manager, qtbot):
        """Test override_changed signal emission."""
        spy = QSignalSpy(manager.override_changed)

        manager.set_user_override("editor.background", "#1e1e1e")

        assert len(spy) == 1
        token, value = spy[0]
        assert token == "editor.background"
        assert value == "#1e1e1e"

    def test_bulk_set_overrides(self, manager):
        """Test setting multiple overrides at once."""
        overrides = {
            "colors.primary": "#007bff",
            "colors.secondary": "#ff6b6b",
            "editor.background": "#1e1e1e",
        }

        success, failed = manager.set_user_overrides_bulk(overrides)

        assert success == 3
        assert len(failed) == 0

        saved = manager.get_user_overrides()
        assert saved == overrides

    def test_validation_invalid_color(self, manager):
        """Test that invalid colors are rejected."""
        with pytest.raises(ValueError, match="Invalid color format"):
            manager.set_user_override("colors.primary", "notacolor")

    def test_clear_user_override(self, manager):
        """Test clearing user override."""
        manager.set_user_override("colors.primary", "#007bff")

        cleared = manager.clear_user_override("colors.primary")
        assert cleared is True

        overrides = manager.get_user_overrides()
        assert "colors.primary" not in overrides

    def test_clear_all_user_overrides(self, manager):
        """Test clearing all user overrides."""
        manager.set_user_override("colors.primary", "#007bff")
        manager.set_user_override("colors.secondary", "#ff6b6b")

        count = manager.clear_all_user_overrides()
        assert count == 2

        overrides = manager.get_user_overrides()
        assert len(overrides) == 0
```

### 7.2 Integration Tests

#### 7.2.1 End-to-End Widget Notification

**File**: `tests/test_overlay_integration.py`

```python
import pytest
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QColor
from vfwidgets_theme import ThemedWidget
from vfwidgets_theme.core.theme_manager import ThemeManager

class TestWidget(ThemedWidget, QWidget):
    """Test widget for integration tests."""
    theme_config = {
        "background": "editor.background",
        "foreground": "editor.foreground",
    }

    def __init__(self):
        super().__init__()
        self.update_count = 0

    def apply_theme(self):
        """Track theme applications."""
        super().apply_theme()
        self.update_count += 1

class TestOverlayIntegration:
    """Integration tests for overlay system."""

    def test_widget_receives_override(self, qapp):
        """Test that widget receives color from override."""
        manager = ThemeManager.instance()

        # Create widget
        widget = TestWidget()
        initial_count = widget.update_count

        # Set override
        manager.set_user_override("editor.background", "#ff0000")

        # Widget should be notified
        assert widget.update_count > initial_count

        # Widget should use override color
        bg = widget._theme_colors.get("background")
        assert QColor(bg) == QColor("#ff0000")

    def test_multiple_widgets_notified(self, qapp):
        """Test that all widgets receive override notification."""
        manager = ThemeManager.instance()

        # Create multiple widgets
        widgets = [TestWidget() for _ in range(5)]
        initial_counts = [w.update_count for w in widgets]

        # Set override
        manager.set_user_override("editor.background", "#00ff00")

        # All widgets should be notified
        for i, widget in enumerate(widgets):
            assert widget.update_count > initial_counts[i]
            bg = widget._theme_colors.get("background")
            assert QColor(bg) == QColor("#00ff00")
```

### 7.3 Performance Tests

**File**: `tests/test_overlay_performance.py`

```python
import pytest
import time
from vfwidgets_theme.core.theme_manager import ThemeManager

class TestOverlayPerformance:
    """Performance tests for overlay system."""

    def test_resolution_speed(self, manager):
        """Test that override resolution is fast."""
        # Set up overrides
        for i in range(100):
            manager.set_app_override(f"test.token{i}", f"#{i:06x}")

        # Measure resolution time
        start = time.perf_counter()
        for i in range(1000):
            manager.get_effective_color("test.token50")
        elapsed = time.perf_counter() - start

        # Should be < 10ms for 1000 resolutions
        assert elapsed < 0.01

    def test_bulk_set_performance(self, manager):
        """Test bulk override setting is efficient."""
        overrides = {f"test.token{i}": f"#{i:06x}" for i in range(500)}

        start = time.perf_counter()
        manager.set_user_overrides_bulk(overrides)
        elapsed = time.perf_counter() - start

        # Should be < 50ms for 500 overrides
        assert elapsed < 0.05

    def test_widget_notification_performance(self, qapp):
        """Test that widget notification is fast."""
        manager = ThemeManager.instance()

        # Create many widgets
        from vfwidgets_theme import ThemedWidget
        from PySide6.QtWidgets import QWidget

        class TestWidget(ThemedWidget, QWidget):
            theme_config = {"bg": "editor.background"}

        widgets = [TestWidget() for _ in range(100)]

        # Measure notification time
        start = time.perf_counter()
        manager.set_user_override("editor.background", "#123456")
        elapsed = time.perf_counter() - start

        # Should be < 100ms for 100 widgets
        assert elapsed < 0.1
```

---

## 8. Performance Requirements

### 8.1 Benchmarks

| Operation | Target | Maximum |
|-----------|--------|---------|
| Single override resolution | <0.01ms | 0.1ms |
| Bulk override set (100 tokens) | <10ms | 50ms |
| Widget notification (100 widgets) | <50ms | 100ms |
| Persistence save | <20ms | 100ms |
| Persistence load | <20ms | 100ms |
| Memory overhead per widget | <100 bytes | 500 bytes |

### 8.2 Scalability

- **Overrides**: Support 1000+ concurrent overrides without degradation
- **Widgets**: Support 1000+ widgets per application
- **Apps**: Support multiple instances with separate override state

### 8.3 Memory

- OverrideRegistry: O(n) where n = number of overrides
- Per-widget overhead: Minimal (theme colors cached)
- No memory leaks on theme changes or widget destruction

---

## 9. Security Considerations

### 9.1 Input Validation

**Color Values**:
- Validate all color values via `QColor.isValid()`
- Reject empty strings, invalid hex, unknown names
- Sanitize before persistence

**Token Names**:
- Validate token name format (alphanumeric, dots, underscores)
- Reject empty strings, special characters
- Maximum length: 255 characters

### 9.2 Persistence Security

**QSettings**:
- Uses platform-native secure storage (registry, plist, config files)
- No encryption needed (colors are not sensitive data)
- Validate on load (reject malformed data)

**File Permissions**:
- Config files should have user-only permissions (0600)
- Check on startup, warn if world-readable

### 9.3 Resource Limits

**Prevent DoS**:
- Maximum overrides per layer: 10,000
- Maximum token name length: 255 chars
- Maximum color value length: 50 chars

---

## 10. Appendix

### 10.1 Complete Example: ViloxTerm Migration

**File**: `apps/viloxterm/src/viloxterm/app.py`

```python
"""ViloxTerm application with theme overlay system."""

import sys
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QSettings
from vfwidgets_theme.widgets import VFThemedApplication

from .window import ViloxTermWindow
from .utils.logging_setup import setup_logging, get_logger


class ViloxTermApp(VFThemedApplication):
    """ViloxTerm application with theme customization support.

    This app demonstrates the full overlay system:
    - Base theme selection (dark, light, high-contrast)
    - App-level branding (ViloxTerm purple)
    - User customization (tab bar, focus borders, terminal colors)
    """

    theme_config = {
        # Base theme
        "base_theme": "dark",

        # App-level branding
        "app_overrides": {
            "colors.primary": "#9b59b6",  # ViloxTerm purple
            "activityBar.background": "#2c2c2c",
        },

        # User customization
        "allow_user_customization": True,
        "customizable_tokens": [
            # Chrome window
            "editorGroupHeader.tabsBackground",
            "tab.activeBackground",
            "tab.inactiveBackground",

            # Focus indicators
            "focusBorder",

            # Terminal
            "terminal.background",
            "terminal.foreground",
            "terminal.ansiBlack",
            "terminal.ansiRed",
            "terminal.ansiGreen",
            "terminal.ansiYellow",
            "terminal.ansiBlue",
            "terminal.ansiMagenta",
            "terminal.ansiCyan",
            "terminal.ansiWhite",
        ],

        # Persistence
        "persist_base_theme": True,
        "persist_user_overrides": True,
    }

    def __init__(self, argv: list[str]):
        """Initialize ViloxTerm application."""
        # Set up logging FIRST
        setup_logging()
        self.logger = get_logger(__name__)
        self.logger.info("ViloxTerm starting")

        # Initialize themed application
        super().__init__(argv, app_id="viloxterm")

        # Set app metadata
        self.setApplicationName("ViloxTerm")
        self.setApplicationVersion("2.0.0")
        self.setOrganizationName("Viloforge")
        self.setOrganizationDomain("viloforge.com")

        self.window: Optional[ViloxTermWindow] = None

    def run(self) -> int:
        """Run the application.

        Returns:
            Exit code
        """
        self.logger.info("Creating main window")

        # Create and show window
        self.window = ViloxTermWindow()
        self.window.show()

        self.logger.info("Entering event loop")

        # Run event loop
        return self.exec()


def main(argv: Optional[list[str]] = None) -> int:
    """Main entry point.

    Args:
        argv: Command-line arguments

    Returns:
        Exit code
    """
    app = ViloxTermApp(argv or sys.argv)
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
```

**File**: `apps/viloxterm/src/viloxterm/components/preferences_dialog.py`

```python
"""Preferences dialog with theme customization UI."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QWidget, QLabel, QPushButton, QColorDialog, QMessageBox
)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QColor
from vfwidgets_theme.core.theme_manager import ThemeManager


class AppearanceTab(QWidget):
    """Appearance preferences tab with theme customization."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._load_current_values()

    def _setup_ui(self):
        """Set up UI."""
        layout = QVBoxLayout(self)

        # Tab bar customization
        layout.addWidget(QLabel("<b>Chrome Window</b>"))

        # Tab bar background
        tab_bar_layout = QHBoxLayout()
        tab_bar_layout.addWidget(QLabel("Tab Bar Background:"))

        self.tab_bar_color_btn = QPushButton()
        self.tab_bar_color_btn.setFixedSize(50, 25)
        self.tab_bar_color_btn.clicked.connect(
            lambda: self._customize_color("editorGroupHeader.tabsBackground")
        )
        tab_bar_layout.addWidget(self.tab_bar_color_btn)

        reset_tab_bar_btn = QPushButton("Reset")
        reset_tab_bar_btn.clicked.connect(
            lambda: self._reset_color("editorGroupHeader.tabsBackground")
        )
        tab_bar_layout.addWidget(reset_tab_bar_btn)

        tab_bar_layout.addStretch()
        layout.addLayout(tab_bar_layout)

        # Focus border
        layout.addWidget(QLabel("<b>Focus Indicators</b>"))

        focus_layout = QHBoxLayout()
        focus_layout.addWidget(QLabel("Focus Border:"))

        self.focus_color_btn = QPushButton()
        self.focus_color_btn.setFixedSize(50, 25)
        self.focus_color_btn.clicked.connect(
            lambda: self._customize_color("focusBorder")
        )
        focus_layout.addWidget(self.focus_color_btn)

        reset_focus_btn = QPushButton("Reset")
        reset_focus_btn.clicked.connect(
            lambda: self._reset_color("focusBorder")
        )
        focus_layout.addWidget(reset_focus_btn)

        focus_layout.addStretch()
        layout.addLayout(focus_layout)

        # Terminal colors
        layout.addWidget(QLabel("<b>Terminal</b>"))

        terminal_bg_layout = QHBoxLayout()
        terminal_bg_layout.addWidget(QLabel("Background:"))

        self.terminal_bg_btn = QPushButton()
        self.terminal_bg_btn.setFixedSize(50, 25)
        self.terminal_bg_btn.clicked.connect(
            lambda: self._customize_color("terminal.background")
        )
        terminal_bg_layout.addWidget(self.terminal_bg_btn)

        reset_terminal_bg_btn = QPushButton("Reset")
        reset_terminal_bg_btn.clicked.connect(
            lambda: self._reset_color("terminal.background")
        )
        terminal_bg_layout.addWidget(reset_terminal_bg_btn)

        terminal_bg_layout.addStretch()
        layout.addLayout(terminal_bg_layout)

        # Reset all button
        layout.addStretch()

        reset_all_btn = QPushButton("Reset All Customizations")
        reset_all_btn.clicked.connect(self._reset_all)
        layout.addWidget(reset_all_btn)

    def _load_current_values(self):
        """Load current color values and update button colors."""
        manager = ThemeManager.instance()

        # Tab bar background
        tab_bar_color = manager.get_effective_color("editorGroupHeader.tabsBackground")
        self._set_button_color(self.tab_bar_color_btn, tab_bar_color)

        # Focus border
        focus_color = manager.get_effective_color("focusBorder")
        self._set_button_color(self.focus_color_btn, focus_color)

        # Terminal background
        terminal_bg = manager.get_effective_color("terminal.background")
        self._set_button_color(self.terminal_bg_btn, terminal_bg)

    def _set_button_color(self, button: QPushButton, color: str):
        """Set button background color."""
        button.setStyleSheet(f"background-color: {color};")

    def _customize_color(self, token: str):
        """Show color picker for token customization."""
        from PySide6.QtWidgets import QApplication

        manager = ThemeManager.instance()
        current = manager.get_effective_color(token)

        color = QColorDialog.getColor(
            QColor(current),
            self,
            f"Customize {token}"
        )

        if color.isValid():
            # Get app instance
            app = QApplication.instance()

            # Use convenience method
            success = app.customize_color(token, color.name(), persist=True)

            if success:
                # Update button
                button_map = {
                    "editorGroupHeader.tabsBackground": self.tab_bar_color_btn,
                    "focusBorder": self.focus_color_btn,
                    "terminal.background": self.terminal_bg_btn,
                }

                if token in button_map:
                    self._set_button_color(button_map[token], color.name())

    def _reset_color(self, token: str):
        """Reset token to default."""
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance()
        success = app.reset_color(token, persist=True)

        if success:
            # Reload current values
            self._load_current_values()

    def _reset_all(self):
        """Reset all customizations."""
        from PySide6.QtWidgets import QApplication

        reply = QMessageBox.question(
            self,
            "Reset All",
            "Reset all color customizations to defaults?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            app = QApplication.instance()
            count = app.reset_all_colors(persist=True)

            QMessageBox.information(
                self,
                "Reset Complete",
                f"Reset {count} customizations"
            )

            # Reload current values
            self._load_current_values()
```

### 10.2 Token Reference

**Customizable Tokens for ViloxTerm**:

| Category | Token | Description | Default (Dark) |
|----------|-------|-------------|----------------|
| **Chrome Window** | | | |
| | `editorGroupHeader.tabsBackground` | Tab bar background | `#2d2d30` |
| | `tab.activeBackground` | Active tab background | `#1e1e1e` |
| | `tab.inactiveBackground` | Inactive tab background | `#2d2d30` |
| | `tab.border` | Tab border | `#252526` |
| **Focus** | | | |
| | `focusBorder` | Focus border color | `#007fd4` |
| **Terminal** | | | |
| | `terminal.background` | Terminal background | `#1e1e1e` |
| | `terminal.foreground` | Terminal foreground | `#cccccc` |
| | `terminal.ansiBlack` | ANSI black | `#000000` |
| | `terminal.ansiRed` | ANSI red | `#cd3131` |
| | `terminal.ansiGreen` | ANSI green | `#0dbc79` |
| | `terminal.ansiYellow` | ANSI yellow | `#e5e510` |
| | `terminal.ansiBlue` | ANSI blue | `#2472c8` |
| | `terminal.ansiMagenta` | ANSI magenta | `#bc3fbc` |
| | `terminal.ansiCyan` | ANSI cyan | `#11a8cd` |
| | `terminal.ansiWhite` | ANSI white | `#e5e5e5` |

### 10.3 Glossary

**Base Theme**: A complete theme created in Theme Studio (e.g., dark.json, light.json)

**App Override**: Developer-defined color override in theme_config (e.g., brand colors)

**User Override**: End-user customization via application settings UI

**Effective Color**: Final resolved color value after applying all overrides

**Override Layer**: A set of overrides with a specific priority (app or user)

**Token**: A named color variable (e.g., `editor.background`, `terminal.foreground`)

**Theme Overlay**: Runtime color customization without modifying base theme

**Persistence**: Saving user overrides to QSettings for restoration on restart

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-10-18 | Claude Code | Initial specification |

---

**End of Specification**
