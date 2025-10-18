# Token Resolution System - Complete Guide

**Understanding how theme tokens are resolved in vfwidgets-theme v2.1.0+**

This document explains the **unified token resolution system** that integrates the Theme Overlay System with ThemedWidget. Understanding this is critical for widget developers and anyone implementing runtime color customization.

---

## Table of Contents

1. [Why This Matters](#why-this-matters)
2. [The Problem We Solved](#the-problem-we-solved)
3. [Resolution Priority](#resolution-priority)
4. [The Unified Resolution API](#the-unified-resolution-api)
5. [Token Types and Resolvers](#token-types-and-resolvers)
6. [Resolution Flow Diagram](#resolution-flow-diagram)
7. [Code Examples](#code-examples)
8. [Integration with ThemedWidget](#integration-with-themedwidget)
9. [Performance and Caching](#performance-and-caching)
10. [Troubleshooting](#troubleshooting)

---

## Why This Matters

**Before v2.1.0**, there were TWO separate color resolution paths:

```
Path 1 (CORRECT):
  ThemeManager.get_effective_color()
    → Checks user overrides ✅
    → Checks app overrides ✅
    → Falls back to theme

Path 2 (BROKEN):
  ThemedWidget.theme.property
    → Directly reads theme.colors dictionary ❌
    → IGNORES overrides completely ❌
```

**Problem**: User color customizations worked in some places but not others. Specifically:
- ✅ Qt stylesheets saw overrides
- ❌ ThemedWidget `theme_config` properties ignored overrides
- ❌ Custom painting code had to manually call `get_effective_color()`

**Solution (v2.1.0)**: Unified token resolution API that ALL code paths use.

---

## The Problem We Solved

### Real-World Example: ViloxTerm Top Bar Customization

**User Request**: "I want to customize the top bar background color in ViloxTerm"

**What Happened (v2.0.0)**:

```python
# User sets customization in preferences
app.customize_color("editorGroupHeader.tabsBackground", "#ff0000", persist=True)

# Override stored correctly ✅
OverrideRegistry["user"]["editorGroupHeader.tabsBackground"] = "#ff0000"

# But ChromeTabbedWindow still showed default color ❌
# Because ThemedWidget._resolve_property_path() didn't check overrides!
```

**What We Fixed (v2.1.0)**:

```python
# ThemedWidget now uses unified resolution API
class ChromeTabbedWindow(ThemedWidget, QWidget):
    theme_config = {
        "background": "editorGroupHeader.tabsBackground",  # Token
    }

# Internally:
def _resolve_property_path(self, theme, property_path):
    # OLD (v2.0.0): theme.colors[property_path]  ❌ Bypassed overrides
    # NEW (v2.1.0): theme_manager.resolve_token(property_path)  ✅ Checks overrides!
```

**Result**: User customizations now work everywhere!

---

## Resolution Priority

The unified resolution API follows this priority (from highest to lowest):

```
1. User Override
   ↓ (if not found)
2. App Override
   ↓ (if not found)
3. Base Theme Value
   ↓ (if not found)
4. Token Registry Default (dark/light)
   ↓ (if not found)
5. Smart Heuristic Fallback
   ↓ (if not found)
6. Provided Fallback Value
```

### Example Resolution

```python
# Scenario: Resolving "editor.background"

# Base theme (dark-default.json)
theme.colors["editor.background"] = "#1a1a1a"

# App override (branding)
app_overrides["editor.background"] = "#1e1e2e"

# User override (customization)
user_overrides["editor.background"] = "#2d1b42"

# Resolution:
ThemeManager.resolve_color("editor.background")
  → Checks user_overrides first → FOUND: "#2d1b42" ✅
  → Returns "#2d1b42" (user override wins)
```

### No Override Set

```python
# Scenario: No overrides, use base theme

# Base theme
theme.colors["editor.background"] = "#1a1a1a"

# No overrides set
app_overrides["editor.background"] = None
user_overrides["editor.background"] = None

# Resolution:
ThemeManager.resolve_color("editor.background")
  → Checks user_overrides → NOT FOUND
  → Checks app_overrides → NOT FOUND
  → Checks base theme → FOUND: "#1a1a1a" ✅
  → Returns "#1a1a1a"
```

### Token Not in Theme

```python
# Scenario: Token not defined anywhere

# Base theme doesn't have this token
theme.colors["customWidget.specialColor"] = None

# No overrides
app_overrides["customWidget.specialColor"] = None
user_overrides["customWidget.specialColor"] = None

# Resolution:
ThemeManager.resolve_color("customWidget.specialColor", fallback="#ff00ff")
  → Checks user_overrides → NOT FOUND
  → Checks app_overrides → NOT FOUND
  → Checks base theme → NOT FOUND
  → Checks TokenRegistry defaults → NOT FOUND
  → Smart heuristic (keyword "Color") → NOT FOUND
  → Returns fallback: "#ff00ff" ✅
```

---

## The Unified Resolution API

### Core Method: `resolve_token()`

**Location**: `src/vfwidgets_theme/core/manager.py:1101-1155`

```python
def resolve_token(
    self,
    token: str,
    token_type: TokenType = TokenType.COLOR,
    fallback: Optional[Any] = None,
    check_overrides: bool = True
) -> Optional[Any]:
    """Resolve a theme token with override support.

    Args:
        token: Token path (e.g., "editor.background")
        token_type: Type of token (COLOR, FONT, SIZE, etc.)
        fallback: Fallback value if token not found
        check_overrides: Whether to check override registry (default: True)

    Returns:
        Resolved value or fallback

    Resolution priority:
        1. User override (if check_overrides=True and type supports it)
        2. App override (if check_overrides=True and type supports it)
        3. Base theme value
        4. Fallback value
    """
```

### Convenience Methods

**For colors**:
```python
def resolve_color(
    self,
    token: str,
    fallback: Optional[str] = None
) -> Optional[str]:
    """Convenience method for resolving color tokens."""
    return self.resolve_token(token, TokenType.COLOR, fallback)
```

**For fonts**:
```python
def resolve_font(
    self,
    token: str,
    fallback: Optional[str] = None
) -> Optional[str]:
    """Convenience method for resolving font tokens."""
    return self.resolve_token(token, TokenType.FONT, fallback)
```

**For sizes**:
```python
def resolve_size(
    self,
    token: str,
    fallback: Optional[Any] = None
) -> Optional[Any]:
    """Convenience method for resolving size tokens."""
    return self.resolve_token(token, TokenType.SIZE, fallback)
```

---

## Token Types and Resolvers

### TokenType Enum

**Location**: `src/vfwidgets_theme/core/token_types.py:12-23`

```python
class TokenType(Enum):
    """Types of theme tokens that can be resolved."""
    COLOR = auto()      # Color values (#hex, rgb(), rgba())
    FONT = auto()       # Font family names
    FONT_SIZE = auto()  # Font sizes (pt, px)
    SIZE = auto()       # Widget sizes, spacing
    SPACING = auto()    # Padding, margins
    BORDER = auto()     # Border widths, styles
    OPACITY = auto()    # Transparency values
    DURATION = auto()   # Animation durations
    OTHER = auto()      # Generic/unknown types
```

### Token Resolvers

Each token type has a dedicated resolver:

```python
class TokenResolver(Protocol):
    """Protocol for token-specific resolution logic."""

    def can_override(self) -> bool:
        """Whether this token type supports the override system."""
        ...

    def validate_value(self, value: Any) -> bool:
        """Validate that a value is appropriate for this token type."""
        ...

    def resolve_from_theme(self, theme: Theme, token: str, fallback: Any) -> Any:
        """Resolve token value from theme data."""
        ...
```

### ColorTokenResolver

**Location**: `src/vfwidgets_theme/core/token_types.py:52-107`

```python
class ColorTokenResolver(TokenResolver):
    """Resolver for color tokens with override support."""

    def can_override(self) -> bool:
        return True  # ✅ Colors support overrides

    def validate_value(self, value: Any) -> bool:
        """Validate color format (#hex, rgb(), rgba())."""
        if not isinstance(value, str):
            return False
        # Check hex format
        if value.startswith('#'):
            return len(value) in (4, 7, 9)  # #RGB, #RRGGBB, #RRGGBBAA
        # Check rgb/rgba format
        if value.startswith('rgb(') or value.startswith('rgba('):
            return True
        return False

    def resolve_from_theme(self, theme: Theme, token: str, fallback: Any) -> Any:
        """Navigate theme.colors dictionary to find token value."""
        colors = theme.colors

        # Try direct key access with dots (e.g., "editor.background")
        if token in colors:
            color = colors[token]
            if isinstance(color, str):
                return color

        # Try nested dictionary navigation
        parts = token.split('.')
        if len(parts) > 1:
            current = colors
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    break
            else:
                if isinstance(current, str):
                    return current

        return fallback
```

---

## Resolution Flow Diagram

```
User code calls:
  theme_manager.resolve_color("editor.background", fallback="#1e1e1e")
        ↓
  resolve_token(token="editor.background", token_type=TokenType.COLOR)
        ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Get Token Resolver                                  │
│   resolver = get_resolver(TokenType.COLOR)                  │
│   → Returns ColorTokenResolver instance                     │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Check if Token Type Supports Overrides             │
│   if check_overrides and resolver.can_override():           │
│     → ColorTokenResolver.can_override() returns True ✅     │
└─────────────────────────────────────────────────────────────┘
        ↓ YES
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Check Override Registry                            │
│   override_value = self._override_registry.resolve(token)   │
│                                                              │
│   Priority:                                                  │
│   1. Check user overrides (highest priority)                │
│   2. Check app overrides                                     │
│                                                              │
│   If found: RETURN override_value ✅ DONE!                  │
└─────────────────────────────────────────────────────────────┘
        ↓ NOT FOUND
┌─────────────────────────────────────────────────────────────┐
│ Step 4: Resolve from Base Theme                            │
│   if self._current_theme:                                   │
│     theme_value = resolver.resolve_from_theme(              │
│       self._current_theme,                                   │
│       token,                                                 │
│       fallback                                               │
│     )                                                        │
│                                                              │
│   ColorTokenResolver.resolve_from_theme():                  │
│   - Check theme.colors["editor.background"]                 │
│   - Check theme.colors["editor"]["background"]              │
│                                                              │
│   If found: RETURN theme_value ✅ DONE!                     │
└─────────────────────────────────────────────────────────────┘
        ↓ NOT FOUND
┌─────────────────────────────────────────────────────────────┐
│ Step 5: Return Fallback                                    │
│   return fallback  ("#1e1e1e")                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Code Examples

### Example 1: Application-Level Usage

```python
from vfwidgets_theme.core.manager import ThemeManager

# Get singleton instance
manager = ThemeManager.get_instance()

# Resolve colors
bg_color = manager.resolve_color("editor.background", fallback="#1e1e1e")
fg_color = manager.resolve_color("editor.foreground", fallback="#d4d4d4")

# Resolve fonts
editor_font = manager.resolve_font("font.editor.family", fallback="Consolas")

# Resolve sizes
font_size = manager.resolve_size("font.editor.size", fallback="12")
```

### Example 2: Widget Custom Painting

```python
from vfwidgets_theme import ThemedWidget
from vfwidgets_theme.core.manager import ThemeManager
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor

class MyCustomWidget(ThemedWidget, QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)

        # ✅ CORRECT: Use ThemeManager.resolve_color()
        manager = ThemeManager.get_instance()
        bg = manager.resolve_color("window.background", fallback="#1e1e1e")
        fg = manager.resolve_color("window.foreground", fallback="#d4d4d4")

        # Paint with resolved colors (includes overrides!)
        painter.fillRect(self.rect(), QColor(bg))
        painter.setPen(QColor(fg))
        painter.drawText(self.rect(), Qt.AlignCenter, "Hello!")
```

### Example 3: ThemedWidget Integration (Automatic!)

```python
from vfwidgets_theme import ThemedWidget
from PySide6.QtWidgets import QWidget

class MyWidget(ThemedWidget, QWidget):
    # Define theme_config as usual
    theme_config = {
        'bg': 'window.background',
        'fg': 'window.foreground',
        'accent': 'colors.primary',
    }

    def paintEvent(self, event):
        painter = QPainter(self)

        # ✅ Automatically uses resolve_color() internally!
        # ThemedWidget._resolve_property_path() calls ThemeManager.resolve_token()
        bg = self.theme.bg  # Checks overrides ✅
        fg = self.theme.fg  # Checks overrides ✅

        painter.fillRect(self.rect(), QColor(bg))
        painter.setPen(QColor(fg))
```

**Key Point**: When you access `self.theme.property`, ThemedWidget automatically calls `ThemeManager.resolve_token()` under the hood!

---

## Integration with ThemedWidget

### How ThemedWidget Uses the Resolution API

**Location**: `src/vfwidgets_theme/widgets/base.py:266-306`

```python
def get_property(self, property_name: str, default_value: Any = None) -> Any:
    """Get theme property with caching.

    This method now uses ThemeManager.resolve_token() to ensure
    user and app overrides are respected.
    """
    # ... cache checking ...

    # Look up the property path from theme_config
    property_path = property_name
    if hasattr(widget, "_theme_config") and property_name in widget._theme_config:
        property_path = widget._theme_config[property_name]

    # ✅ NEW (v2.1.0): Infer token type and use unified resolution API
    token_type = self._infer_token_type(property_name, property_path)

    # Get ThemeManager
    theme_manager = ThemeManager.get_instance()

    # ✅ NEW (v2.1.0): Use resolve_token() which checks overrides!
    value = theme_manager.resolve_token(
        property_path,
        token_type,
        fallback=default_value
    )

    if value is not None:
        self._cache[property_name] = value
        return value

    return default_value
```

### Token Type Inference

```python
def _infer_token_type(self, property_name: str, property_path: str) -> TokenType:
    """Infer token type from property name or path.

    Heuristic-based type detection for automatic handling.
    """
    name_lower = property_name.lower()
    path_lower = property_path.lower()

    # Check for color indicators
    if any(word in name_lower or word in path_lower for word in [
        "color", "background", "foreground", "bg", "fg", "border"
    ]):
        return TokenType.COLOR

    # Check for font indicators
    if "font" in name_lower or "font" in path_lower:
        if "size" in name_lower or "size" in path_lower:
            return TokenType.FONT_SIZE
        return TokenType.FONT

    # Check for size indicators
    if any(word in name_lower or word in path_lower for word in [
        "size", "width", "height", "spacing", "padding", "margin"
    ]):
        return TokenType.SIZE

    # Default to OTHER for unknown types
    return TokenType.OTHER
```

**Key Point**: Type inference is automatic! You don't need to specify token types in `theme_config`.

---

## Performance and Caching

### Resolution Performance

**Target**: < 0.5ms per resolution (< 500 microseconds)

**Actual** (from tests):
- First resolution: ~0.3ms (includes override checking)
- Cached resolution: < 0.001ms (< 1 microsecond)

### Caching Strategy

**Three levels of caching**:

1. **ThemePropertiesManager Cache** (Widget-level)
   - Caches resolved values per widget
   - Invalidated on theme change
   - Lifetime: Widget lifetime

2. **ThemeManager Override Registry** (Manager-level)
   - Cached override resolution
   - Invalidated when overrides change
   - Lifetime: Application lifetime

3. **TokenResolver Cache** (Future enhancement)
   - Could cache theme value lookups
   - Not yet implemented

### Cache Invalidation

```python
# When theme changes:
ThemeManager.set_theme("new_theme")
  → Clears all widget property caches
  → Calls widget.on_theme_changed()
  → Widget repaints with new colors

# When override changes:
ThemeManager.set_user_override("editor.background", "#ff0000")
  → Override registry updated
  → Next resolution sees new override
  → Widget property cache invalidated on next theme_changed signal
```

---

## Troubleshooting

### Issue: "My override isn't showing up!"

**Check 1**: Are you using the unified resolution API?

```python
# ❌ WRONG - Bypasses overrides
theme = widget.get_current_theme()
bg = theme.colors.get("editor.background")

# ✅ CORRECT - Checks overrides
from vfwidgets_theme.core.manager import ThemeManager
manager = ThemeManager.get_instance()
bg = manager.resolve_color("editor.background")

# ✅ OR use theme_config (automatic)
bg = widget.theme.bg  # From theme_config
```

**Check 2**: Is the override actually set?

```python
manager = ThemeManager.get_instance()

# Check user overrides
user_overrides = manager.get_user_overrides()
print(f"User overrides: {user_overrides}")

# Check app overrides
app_overrides = manager.get_app_overrides()
print(f"App overrides: {app_overrides}")

# Check effective color
effective = manager.get_effective_color("editor.background")
print(f"Effective color: {effective}")
```

**Check 3**: Is caching causing stale values?

```python
# In widget.on_theme_changed():
def on_theme_changed(self):
    # ❌ May return stale cached value
    bg = self.theme.bg

    # ✅ Query manager directly for current value
    manager = ThemeManager.get_instance()
    bg = manager.resolve_color("editor.background", fallback="#1e1e1e")
```

### Issue: "Token type detection is wrong!"

**Explicit token type**:

```python
# Let system infer type (automatic)
manager.resolve_token("editor.background")  # Infers COLOR

# Or specify explicitly
from vfwidgets_theme.core.token_types import TokenType
manager.resolve_token("editor.background", TokenType.COLOR)
```

### Issue: "Performance seems slow!"

**Check**: Are you bypassing the cache?

```python
# ❌ Slow - resolves every time
def paintEvent(self, event):
    manager = ThemeManager.get_instance()
    bg = manager.resolve_color("editor.background")  # Resolves on every paint!

# ✅ Fast - cached in widget
class MyWidget(ThemedWidget, QWidget):
    theme_config = {'bg': 'editor.background'}

    def paintEvent(self, event):
        bg = self.theme.bg  # Cached! ✅
```

---

## Summary

**Key Takeaways**:

1. **Single Source of Truth**: `ThemeManager.resolve_token()` is THE resolution API
2. **Override Integration**: Overrides checked FIRST, before theme values
3. **Type-Specific Resolvers**: Each token type has dedicated resolution logic
4. **Automatic for ThemedWidget**: `theme_config` properties automatically use resolve_token()
5. **Performance**: Cached resolution is < 1 microsecond
6. **Extensible**: Easy to add new token types

**Best Practices**:

- ✅ Use `theme_config` for widget properties (automatic resolution)
- ✅ Use `resolve_color()` for custom painting code
- ✅ Never directly access `theme.colors` dictionary
- ✅ Trust the cache (don't resolve in tight loops)
- ✅ Query manager in `on_theme_changed()` for current values

**Next Steps**:

- **[THEMED-WIDGET-INTEGRATION.md](THEMED-WIDGET-INTEGRATION.md)** - How ThemedWidget uses this system
- **[tokens-GUIDE.md](tokens-GUIDE.md)** - Available tokens
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues

---

**Last Updated**: 2025-10-18
**Version**: 2.1.0
