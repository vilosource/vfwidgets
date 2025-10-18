# ThemedWidget + Override System Integration

**How ThemedWidget automatically integrates with the Theme Overlay System**

This document explains how `ThemedWidget` integrates with the override system to ensure user and app-level color customizations work automatically. Understanding this is critical to avoid bypassing the override system.

---

## Table of Contents

1. [The Integration in 30 Seconds](#the-integration-in-30-seconds)
2. [Why This Integration Matters](#why-this-integration-matters)
3. [How It Works](#how-it-works)
4. [Using theme_config](#using-theme_config)
5. [Common Mistakes](#common-mistakes)
6. [Best Practices](#best-practices)
7. [Advanced: Accessing Theme in Non-ThemedWidget Components](#advanced-accessing-theme-in-non-themedwidget-components)
8. [Migration from v2.0.0 to v2.1.0](#migration-from-v200-to-v210)

---

## The Integration in 30 Seconds

**v2.1.0 Fix**: `ThemedWidget` now automatically uses `ThemeManager.resolve_token()` for all `theme_config` properties, which means **user and app overrides work automatically**.

**What this means for you**:

```python
from vfwidgets_theme import ThemedWidget
from PySide6.QtWidgets import QWidget

class MyWidget(ThemedWidget, QWidget):
    theme_config = {
        'bg': 'editor.background',  # Maps property to token
    }

    def paintEvent(self, event):
        bg = self.theme.bg  # ✅ Automatically checks overrides!
```

**No code changes required** - existing widgets automatically benefit from this integration!

---

## Why This Integration Matters

### The Problem (v2.0.0)

Before v2.1.0, ThemedWidget had an architectural issue:

```python
# v2.0.0: ThemedWidget._resolve_property_path()

def _resolve_property_path(self, theme, property_path):
    """OLD CODE - Bypassed overrides!"""
    # Split "editor.background" → ["editor", "background"]
    parts = property_path.split('.')
    current = theme.colors  # ❌ Directly accesses theme.colors dictionary

    for part in parts:
        if part in current:
            current = current[part]  # ❌ Navigates dictionary manually

    return current  # ❌ Returns base theme value, IGNORES overrides!
```

**Problem**: This code NEVER checked the OverrideRegistry!

**Impact**:
- ✅ `app.customize_color()` stored overrides correctly
- ✅ `ThemeManager.get_effective_color()` returned overrides correctly
- ❌ ThemedWidget.theme.property IGNORED overrides!

### Real-World Failure Case

**User Story**: ViloxTerm top bar customization

```python
# User sets custom color in preferences
app.customize_color("editorGroupHeader.tabsBackground", "#ff0000", persist=True)

# Override saved correctly ✅
QSettings["theme/user_overrides"]["editorGroupHeader.tabsBackground"] = "#ff0000"

# OverrideRegistry has the override ✅
manager.get_user_overrides()["editorGroupHeader.tabsBackground"] == "#ff0000"

# But ChromeTabbedWindow (ThemedWidget) still shows default color ❌
class ChromeTabbedWindow(ThemedWidget, QWidget):
    theme_config = {
        "background": "editorGroupHeader.tabsBackground",
    }

    def paintEvent(self, event):
        bg = self.theme.background
        # bg == "#2d2d30" (base theme)  ❌ WRONG!
        # bg should be "#ff0000" (user override) ✅
```

**Root Cause**: `_resolve_property_path()` didn't call `ThemeManager.resolve_token()`.

### The Fix (v2.1.0)

```python
# v2.1.0: ThemedWidget.get_property()

def get_property(self, property_name: str, default_value: Any = None) -> Any:
    """NEW CODE - Uses unified resolution API!"""

    # Look up token from theme_config
    property_path = widget._theme_config[property_name]  # "editor.background"

    # Infer token type (automatic)
    token_type = self._infer_token_type(property_name, property_path)  # TokenType.COLOR

    # ✅ NEW: Use ThemeManager.resolve_token() which checks overrides!
    theme_manager = ThemeManager.get_instance()
    value = theme_manager.resolve_token(
        property_path,      # "editor.background"
        token_type,         # TokenType.COLOR
        fallback=default_value
    )

    return value  # ✅ Returns override if set, otherwise theme value
```

**Now**: ThemedWidget properties automatically see overrides!

---

## How It Works

### The Flow

```
User accesses:
  widget.theme.bg

        ↓

ThemeAccess.__getattr__("bg")
  → Calls ThemePropertiesManager.get_property("bg")

        ↓

ThemePropertiesManager.get_property("bg")
  1. Look up token from theme_config: "bg" → "editor.background"
  2. Infer token type: "background" keyword → TokenType.COLOR
  3. Call ThemeManager.resolve_token("editor.background", TokenType.COLOR)

        ↓

ThemeManager.resolve_token("editor.background", TokenType.COLOR)
  1. Get ColorTokenResolver
  2. Check if type supports overrides: True ✅
  3. Check OverrideRegistry:
     - Check user overrides → FOUND: "#ff0000" ✅
     - RETURN "#ff0000"

        ↓

widget.theme.bg == "#ff0000"  ✅ User override!
```

### Token Type Inference

ThemedWidget automatically detects token types:

```python
def _infer_token_type(self, property_name: str, property_path: str) -> TokenType:
    """Infer token type from property name or path."""

    name_lower = property_name.lower()
    path_lower = property_path.lower()

    # Color detection (most common)
    if any(keyword in name_lower or keyword in path_lower for keyword in [
        "color", "background", "foreground", "bg", "fg", "border"
    ]):
        return TokenType.COLOR

    # Font detection
    if "font" in name_lower or "font" in path_lower:
        if "size" in name_lower or "size" in path_lower:
            return TokenType.FONT_SIZE
        return TokenType.FONT

    # Size detection
    if any(keyword in name_lower or keyword in path_lower for keyword in [
        "size", "width", "height", "spacing", "padding", "margin"
    ]):
        return TokenType.SIZE

    # Default to OTHER
    return TokenType.OTHER
```

**Example**:
```python
theme_config = {
    'bg': 'editor.background',           # Detected as COLOR (has "background")
    'fg': 'editor.foreground',           # Detected as COLOR (has "foreground")
    'border': 'colors.border',           # Detected as COLOR (has "border")
    'font': 'font.editor.family',        # Detected as FONT (has "font")
    'font_size': 'font.editor.size',     # Detected as FONT_SIZE (has "font" + "size")
    'spacing': 'editor.lineHeight',      # Detected as SIZE (has "spacing")
}
```

---

## Using theme_config

### Basic Usage

```python
from vfwidgets_theme import ThemedWidget
from PySide6.QtWidgets import QWidget

class MyWidget(ThemedWidget, QWidget):
    """Custom widget with automatic override support."""

    theme_config = {
        'bg': 'window.background',      # Background color
        'fg': 'window.foreground',      # Text color
        'accent': 'colors.primary',     # Accent color
    }

    def paintEvent(self, event):
        painter = QPainter(self)

        # ✅ Automatically checks overrides!
        bg_color = self.theme.bg
        fg_color = self.theme.fg
        accent_color = self.theme.accent

        painter.fillRect(self.rect(), QColor(bg_color))
        painter.setPen(QColor(fg_color))
        # ... painting code ...
```

### Widget-Specific Tokens

```python
class ChromeTabbedWindow(ThemedWidget, QWidget):
    """Chrome-style tabbed window."""

    theme_config = {
        # Generic tokens (work for all apps)
        "background": "editorGroupHeader.tabsBackground",  # Top bar background
        "border": "editorGroupHeader.tabsBorder",          # Top bar border

        # Tab-specific tokens
        "tab_active_bg": "tab.activeBackground",
        "tab_inactive_bg": "tab.inactiveBackground",
        "tab_hover_bg": "tab.hoverBackground",
    }

    def paintEvent(self, event):
        painter = QPainter(self)

        # All properties automatically see overrides!
        top_bar_bg = self.theme.background  # User can customize this!
        border_color = self.theme.border

        # Paint top bar
        painter.fillRect(self.top_bar_rect, QColor(top_bar_bg))
```

### Advanced: Fallback Values

```python
class MyWidget(ThemedWidget, QWidget):
    theme_config = {
        'bg': 'window.background',
        'special': 'myWidget.specialColor',  # Custom token
    }

    def paintEvent(self, event):
        # Standard token - always exists
        bg = self.theme.bg

        # Custom token - may not exist in theme
        # Use getattr() with fallback
        special = getattr(self.theme, 'special', '#ff00ff')
        # If token not in theme, returns '#ff00ff'
```

---

## Common Mistakes

### Mistake 1: Directly Accessing theme.colors

**❌ WRONG - Bypasses override system**:
```python
class MyWidget(ThemedWidget, QWidget):
    def paintEvent(self, event):
        # ❌ BAD: Directly accessing theme object
        theme = self.get_current_theme()
        bg = theme.colors.get('editor.background')  # IGNORES overrides!
```

**✅ CORRECT - Uses override system**:
```python
class MyWidget(ThemedWidget, QWidget):
    theme_config = {
        'bg': 'editor.background',
    }

    def paintEvent(self, event):
        # ✅ GOOD: Uses theme_config (automatic override checking)
        bg = self.theme.bg  # Checks overrides ✅
```

### Mistake 2: Passing Theme to Helper Functions

**❌ WRONG - Helper can't check overrides**:
```python
class ChromeTabbedWindow(ThemedWidget, QWidget):
    def paintEvent(self, event):
        theme = self.get_current_theme()  # Raw Theme object

        # Helper gets Theme object (can't check overrides!)
        ChromeTabRenderer.draw_tab(painter, rect, text, theme)  # ❌

class ChromeTabRenderer:
    @staticmethod
    def draw_tab(painter, rect, text, theme):
        # ❌ Can only access theme.colors directly
        bg = theme.colors.get('tab.activeBackground')  # IGNORES overrides!
```

**✅ CORRECT - Helper uses ThemeManager**:
```python
class ChromeTabbedWindow(ThemedWidget, QWidget):
    def paintEvent(self, event):
        # Pass theme object (needed for other data like metadata)
        theme = self.get_current_theme()
        ChromeTabRenderer.draw_tab(painter, rect, text, theme)  # ✅

class ChromeTabRenderer:
    @staticmethod
    def draw_tab(painter, rect, text, theme):
        # ✅ Helper uses ThemeManager.resolve_color()
        from vfwidgets_theme.core.manager import ThemeManager

        manager = ThemeManager.get_instance()
        bg = manager.resolve_color('tab.activeBackground', fallback='#2d2d30')  # ✅ Checks overrides!
```

### Mistake 3: Caching Theme Values Incorrectly

**❌ WRONG - Cached value becomes stale**:
```python
class MyWidget(ThemedWidget, QWidget):
    def __init__(self):
        super().__init__()

        # ❌ Cache theme value in __init__
        self._cached_bg = self.theme.bg  # Cached once!

    def paintEvent(self, event):
        # ❌ Uses stale cached value (doesn't update when override changes)
        painter.fillRect(self.rect(), QColor(self._cached_bg))
```

**✅ CORRECT - Let ThemedWidget handle caching**:
```python
class MyWidget(ThemedWidget, QWidget):
    theme_config = {
        'bg': 'window.background',
    }

    def paintEvent(self, event):
        # ✅ ThemedWidget caches this internally and invalidates on theme change
        bg = self.theme.bg  # Always up-to-date! ✅
        painter.fillRect(self.rect(), QColor(bg))
```

---

## Best Practices

### Practice 1: Always Use theme_config

```python
# ✅ RECOMMENDED
class MyWidget(ThemedWidget, QWidget):
    theme_config = {
        'bg': 'window.background',
        'fg': 'window.foreground',
    }

    def paintEvent(self, event):
        bg = self.theme.bg  # Automatic override checking ✅
```

### Practice 2: Use ThemeManager for Helpers

```python
# For renderer classes, painters, or non-ThemedWidget components
class MyRenderer:
    @staticmethod
    def draw(painter, rect, theme):
        from vfwidgets_theme.core.manager import ThemeManager

        manager = ThemeManager.get_instance()
        bg = manager.resolve_color('window.background', fallback='#1e1e1e')  # ✅
```

### Practice 3: Don't Cache Manually

```python
# ❌ DON'T DO THIS
def __init__(self):
    self._bg_color = self.theme.bg  # Cached manually

# ✅ DO THIS
def paintEvent(self, event):
    bg = self.theme.bg  # ThemedWidget handles caching ✅
```

### Practice 4: Use Generic Tokens

```python
# ✅ GOOD: Generic tokens work for all apps
theme_config = {
    "background": "editorGroupHeader.tabsBackground",  # Generic top bar
}

# ❌ BAD: App-specific tokens limit reusability
theme_config = {
    "background": "viloxterm.topBarBackground",  # ViloxTerm-specific (doesn't exist!)
}
```

---

## Advanced: Accessing Theme in Non-ThemedWidget Components

Sometimes you have helper classes, renderers, or child widgets that need theme access but aren't `ThemedWidget` themselves.

### Pattern: Parent Exposes Theme

```python
# Parent widget (ThemedWidget)
class ChromeTabbedWindow(ThemedWidget, QWidget):
    def __init__(self):
        super().__init__()
        self.tab_bar = TabBar(self)  # Child widget (not ThemedWidget)

    def get_current_theme(self):
        """Expose theme to children."""
        # Inherited from ThemedWidget
        return super().get_current_theme()

    def paintEvent(self, event):
        # Pass theme to renderer
        theme = self.get_current_theme()
        self.tab_bar.render(painter, theme)
```

### Pattern: Traverse Parent Chain

```python
# Child widget (non-ThemedWidget)
class TabBar(QWidget):
    def _get_theme_from_parent(self):
        """Find themed parent in widget hierarchy."""
        parent = self.parent()
        while parent:
            if hasattr(parent, 'get_current_theme'):
                return parent.get_current_theme()
            parent = parent.parent()
        return None

    def paintEvent(self, event):
        theme = self._get_theme_from_parent()
        if theme:
            # ✅ Use ThemeManager to check overrides!
            from vfwidgets_theme.core.manager import ThemeManager
            manager = ThemeManager.get_instance()
            bg = manager.resolve_color('tab.activeBackground', fallback='#2d2d30')
        else:
            # Fallback
            bg = '#2d2d30'
```

### Pattern: Pass ThemeManager Directly

```python
# Renderer class
class ChromeTabRenderer:
    @staticmethod
    def draw_tab(painter, rect, text, theme):
        """Draw a Chrome-style tab.

        Args:
            theme: Theme object (for metadata, fonts, etc.)
        """
        # ✅ Use ThemeManager for colors (checks overrides)
        from vfwidgets_theme.core.manager import ThemeManager
        manager = ThemeManager.get_instance()

        bg = manager.resolve_color('tab.activeBackground', fallback='#1e1e1e')
        fg = manager.resolve_color('tab.activeForeground', fallback='#ffffff')

        # Use resolved colors
        painter.fillRect(rect, QColor(bg))
        painter.setPen(QColor(fg))
```

**Key Point**: Non-ThemedWidget components should use `ThemeManager.resolve_color()` directly, not `theme.colors.get()`.

---

## Migration from v2.0.0 to v2.1.0

### Good News: Zero Code Changes Required!

If you're using `theme_config` pattern, **no migration needed**:

```python
# v2.0.0 code
class MyWidget(ThemedWidget, QWidget):
    theme_config = {
        'bg': 'editor.background',
    }

    def paintEvent(self, event):
        bg = self.theme.bg

# ✅ v2.1.0: Same code, but now sees overrides automatically!
# NO CHANGES NEEDED!
```

### If You Were Bypassing theme_config

If you were directly accessing `theme.colors`, you should migrate:

**Before (v2.0.0)**:
```python
def paintEvent(self, event):
    theme = self.get_current_theme()
    bg = theme.colors.get('editor.background')  # Bypassed overrides
```

**After (v2.1.0)**:
```python
# Option 1: Use theme_config (recommended)
class MyWidget(ThemedWidget, QWidget):
    theme_config = {
        'bg': 'editor.background',
    }

    def paintEvent(self, event):
        bg = self.theme.bg  # ✅ Checks overrides

# Option 2: Use ThemeManager directly
def paintEvent(self, event):
    from vfwidgets_theme.core.manager import ThemeManager
    manager = ThemeManager.get_instance()
    bg = manager.resolve_color('editor.background')  # ✅ Checks overrides
```

### Deprecation Notice

**Deprecated pattern** (still works, but discouraged):
```python
theme = widget.get_current_theme()
color = theme.colors.get('editor.background')  # ⚠️ Bypasses overrides
```

**Recommended pattern**:
```python
color = widget.theme.bg  # From theme_config ✅
# OR
color = ThemeManager.get_instance().resolve_color('editor.background')  # ✅
```

---

## Summary

**Key Takeaways**:

1. **✅ ThemedWidget integration is automatic** - No code changes needed
2. **✅ theme_config properties check overrides** - Via `resolve_token()`
3. **✅ Type inference is automatic** - Detects colors, fonts, sizes
4. **❌ Don't bypass with theme.colors.get()** - Always use theme_config or ThemeManager
5. **✅ Helpers should use ThemeManager** - Not direct theme.colors access

**Best Practices**:
- Always use `theme_config` for widget properties
- Use `ThemeManager.resolve_color()` for helpers/renderers
- Never cache theme values manually (ThemedWidget handles it)
- Use generic tokens, not app-specific ones

**Next Steps**:
- **[TOKEN-RESOLUTION.md](TOKEN-RESOLUTION.md)** - How resolution works internally
- **[widget-development-GUIDE.md](widget-development-GUIDE.md)** - Complete ThemedWidget guide
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions

---

**Last Updated**: 2025-10-18
**Version**: 2.1.0
