# Theme System Troubleshooting Guide

**Common issues and their solutions**

This guide covers the most common problems developers encounter when using the VFWidgets theme system, organized by category.

---

## Table of Contents

1. [Override System Issues](#override-system-issues)
2. [ThemedWidget Issues](#themedwidget-issues)
3. [Token Resolution Issues](#token-resolution-issues)
4. [Performance Issues](#performance-issues)
5. [Integration Issues](#integration-issues)
6. [Theme File Issues](#theme-file-issues)

---

## Override System Issues

### ❌ Override Not Showing Up

**Problem**: You set a user override but the color doesn't change.

```python
app.customize_color("editor.background", "#ff0000", persist=True)
# But widget still shows default color
```

**Diagnosis**:

1. **Check if override is actually set**:
```python
from vfwidgets_theme.core.manager import ThemeManager

manager = ThemeManager.get_instance()
overrides = manager.get_user_overrides()
print(f"User overrides: {overrides}")

# Should show: {'editor.background': '#ff0000'}
```

2. **Check if you're bypassing the override system**:
```python
# ❌ WRONG - Bypasses overrides
theme = widget.get_current_theme()
bg = theme.colors.get('editor.background')  # Ignores overrides!

# ✅ CORRECT - Checks overrides
bg = widget.theme.bg  # From theme_config
# OR
manager = ThemeManager.get_instance()
bg = manager.resolve_color('editor.background')
```

3. **Check if widget is using ThemedWidget**:
```python
from vfwidgets_theme import ThemedWidget

# Must inherit from ThemedWidget
class MyWidget(ThemedWidget, QWidget):  # ✅ Correct
    theme_config = {'bg': 'editor.background'}

class MyWidget(QWidget):  # ❌ Won't see overrides
    pass
```

**Solution**: Use `theme_config` or `ThemeManager.resolve_color()`, never `theme.colors.get()`.

**📖 Reference**: [THEMED-WIDGET-INTEGRATION.md](THEMED-WIDGET-INTEGRATION.md) - Common Mistakes section

---

### ❌ Wrong Token for Top Bar Background

**Problem**: You're trying to customize the top bar (where tabs and window controls are) but the wrong widget is changing color.

```python
# User sets this:
app.customize_color("tab.inactiveBackground", "#ff0000")

# But it changes the wrong thing:
# - Preferences dialog tabs change color (wrong widget!)
# - Top bar stays the same (what we wanted to change)
```

**Why This Happens**:
- `tab.inactiveBackground` = Individual tab backgrounds (QTabWidget tabs)
- `editorGroupHeader.tabsBackground` = Top bar background (where tabs sit)

**Solution**: Use the correct token

```python
# ❌ WRONG - Changes individual tabs
app.customize_color("tab.inactiveBackground", "#ff0000")
app.customize_color("tab.activeBackground", "#ff0000")

# ✅ CORRECT - Changes top bar (draggable area)
app.customize_color("editorGroupHeader.tabsBackground", "#ff0000")
```

**Token Guide**:
```
editorGroupHeader.tabsBackground  → Top bar background (draggable area with tabs + controls)
editorGroupHeader.tabsBorder      → Top bar border
tab.activeBackground              → Individual active tab background
tab.inactiveBackground            → Individual inactive tab backgrounds
tab.hoverBackground               → Individual tab on hover
```

**📖 Reference**: [tokens-GUIDE.md](tokens-GUIDE.md) - Token Hierarchy section

---

### ❌ Override Persists After Clearing

**Problem**: You cleared an override but the color didn't change back to default.

```python
app.reset_color("editor.background", persist=True)
# But widget still shows custom color
```

**Diagnosis**:

1. **Check if override was actually removed**:
```python
manager = ThemeManager.get_instance()
overrides = manager.get_user_overrides()
print(f"User overrides: {overrides}")
# Should NOT contain 'editor.background'
```

2. **Check if app override is still set**:
```python
app_overrides = manager.get_app_overrides()
print(f"App overrides: {app_overrides}")
# Might still have app-level override (not cleared by reset_color)
```

3. **Check if widget cache is stale**:
```python
# Force widget update
widget.on_theme_changed()
widget.update()
```

**Solution**: Clear both user and app overrides if needed

```python
# Clear user override only
app.reset_color("editor.background", persist=True)

# Clear app override (if set programmatically)
manager = ThemeManager.get_instance()
manager.remove_app_override("editor.background")

# Nuclear option: Clear all user overrides
app.clear_user_preferences()
```

---

## ThemedWidget Issues

### ❌ TypeError: ThemedWidget Must Come First

**Problem**: You get a TypeError about inheritance order.

```python
class MyWidget(QTextEdit, ThemedWidget):  # ❌ Wrong order
    pass

# TypeError: MyWidget: ThemedWidget must come BEFORE QTextEdit.
```

**Why**: Python's Method Resolution Order (MRO) requires `ThemedWidget` first.

**Solution**: Put `ThemedWidget` first in inheritance list

```python
# ✅ CORRECT
class MyWidget(ThemedWidget, QTextEdit):
    pass

# ✅ CORRECT
class MyDialog(ThemedWidget, QDialog):
    pass

# ✅ CORRECT
class MyFrame(ThemedWidget, QFrame):
    pass
```

**📖 Reference**: [widget-development-GUIDE.md](widget-development-GUIDE.md) - Inheritance Order section

---

### ❌ Theme Properties Return None

**Problem**: `widget.theme.property` returns None.

```python
class MyWidget(ThemedWidget, QWidget):
    theme_config = {
        'bg': 'window.background',
    }

    def paintEvent(self, event):
        bg = self.theme.bg  # Returns None!
```

**Diagnosis**:

1. **Check theme_config mapping**:
```python
# Is property actually in theme_config?
print(self._theme_config)
# Should show: {'bg': 'window.background'}
```

2. **Check if token exists in theme**:
```python
theme = self.get_current_theme()
print(f"Theme colors: {list(theme.colors.keys())}")
# Does 'window.background' exist?
```

3. **Check if theme is loaded**:
```python
manager = ThemeManager.get_instance()
print(f"Current theme: {manager.current_theme.name if manager.current_theme else 'None'}")
```

**Solutions**:

```python
# Solution 1: Use fallback value
bg = getattr(self.theme, 'bg', '#ffffff')  # Fallback to white

# Solution 2: Use correct token name
theme_config = {
    'bg': 'colors.background',  # ✅ Correct - exists in all themes
}

# Solution 3: Check theme before accessing
def paintEvent(self, event):
    if not hasattr(self, 'theme') or self.theme is None:
        return  # Theme not ready yet

    bg = self.theme.bg or '#ffffff'  # Safe access
```

---

### ❌ Theme Properties Stale in on_theme_changed()

**Problem**: Theme switches work in one direction but not the other (e.g., dark→light works, light→dark doesn't).

```python
class MyWidget(ThemedWidget, QWidget):
    theme_config = {'bg': 'colors.background'}

    def on_theme_changed(self):
        # ❌ May return OLD theme's value during transition!
        bg = self.theme.bg or '#ffffff'
        self.setStyleSheet(f"background: {bg};")
```

**Why**: `on_theme_changed()` is called DURING theme transition, property cache may still contain old values.

**Solution 1: Query ThemeManager directly (Most Reliable)**

```python
def on_theme_changed(self):
    # ✅ Query manager for current theme type
    from vfwidgets_theme import ThemedApplication

    app = ThemedApplication.instance()
    if app and hasattr(app, '_theme_manager'):
        theme = app._theme_manager.current_theme
        theme_type = theme.type if theme else 'dark'

        # Select appropriate fallback based on current theme type
        if theme_type == 'light':
            fallback_bg = '#ffffff'
        else:
            fallback_bg = '#1e1e1e'

        # Use manager directly (bypasses cache)
        manager = ThemeManager.get_instance()
        bg = manager.resolve_color('colors.background', fallback=fallback_bg)

        self.setStyleSheet(f"background: {bg};")
```

**Solution 2: Use ThemeProperty Descriptors (Cleaner)**

```python
from vfwidgets_theme.widgets.properties import ColorProperty

class MyWidget(ThemedWidget, QWidget):
    bg_color = ColorProperty('colors.background', default='#ffffff')

    def on_theme_changed(self):
        # ✅ ColorProperty handles caching correctly
        self.setStyleSheet(f"background: {self.bg_color};")
```

**📖 Reference**: [THEMED-WIDGET-INTEGRATION.md](THEMED-WIDGET-INTEGRATION.md) - Advanced section

---

### ❌ Child Widgets Can't Access Theme

**Problem**: Child widget (non-ThemedWidget) needs theme colors but doesn't have access.

```python
class TabBar(QWidget):  # Not ThemedWidget
    def paintEvent(self, event):
        # How to get theme???
        theme = ???  # No access!
```

**Solution**: Traverse parent chain to find themed parent

```python
class TabBar(QWidget):
    def _get_theme_from_parent(self):
        """Find ThemedWidget parent in hierarchy."""
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

**📖 Reference**: [THEMED-WIDGET-INTEGRATION.md](THEMED-WIDGET-INTEGRATION.md) - Advanced: Accessing Theme in Non-ThemedWidget Components

---

## Token Resolution Issues

### ❌ Token Not Found Warning

**Problem**: Logs show "Token not found" warnings.

```
WARNING: Token 'myWidget.specialColor' not found in theme
```

**Diagnosis**:

1. **Check token exists in theme file**:
```bash
grep "myWidget.specialColor" ~/.vfwidgets/themes/dark-default.json
# Should find the token
```

2. **Check token name spelling**:
```python
# Common typos:
"editorGroupHeader.tabsBackground"  # ✅ Correct
"editorGroupHeader.tabsBackgroud"   # ❌ Typo: "backgroud"
"editorGroupHeader.tabsbackground"  # ❌ Wrong case
```

3. **Check if using custom token**:
```python
# Custom tokens need to be defined in theme
theme_config = {
    'special': 'myWidget.specialColor',  # Custom token
}

# If not in theme, provide fallback
special = getattr(self.theme, 'special', '#ff00ff')
```

**Solutions**:

```python
# Solution 1: Use existing token
theme_config = {
    'bg': 'colors.background',  # ✅ Standard token (always exists)
}

# Solution 2: Provide fallback for custom tokens
theme_config = {
    'special': 'myWidget.specialColor',  # Custom token
}

def paintEvent(self, event):
    special = getattr(self.theme, 'special', '#ff00ff')  # With fallback

# Solution 3: Add token to theme file
{
  "myWidget.specialColor": "#ff00ff"
}
```

---

### ❌ Wrong Token Type Inferred

**Problem**: Token type detection is wrong (e.g., color detected as font).

```python
theme_config = {
    'line_height': 'editor.lineHeight',  # Should be SIZE, detected as ???
}
```

**Solution**: Use explicit token type

```python
from vfwidgets_theme.core.manager import ThemeManager
from vfwidgets_theme.core.token_types import TokenType

# Automatic type inference (usually works)
manager = ThemeManager.get_instance()
value = manager.resolve_token('editor.lineHeight')  # Infers from keywords

# Explicit type (when inference fails)
value = manager.resolve_token('editor.lineHeight', TokenType.SIZE)  # Explicit
```

**📖 Reference**: [TOKEN-RESOLUTION.md](TOKEN-RESOLUTION.md) - Token Type Inference section

---

## Performance Issues

### ❌ Slow Theme Switching

**Problem**: Theme changes take several seconds with many widgets.

**Diagnosis**:

1. **Check widget count**:
```python
manager = ThemeManager.get_instance()
widget_count = len(manager._widget_registry.get_all_widgets())
print(f"Registered widgets: {widget_count}")
# >1000 widgets is slow
```

2. **Check for expensive on_theme_changed() handlers**:
```python
class MyWidget(ThemedWidget, QWidget):
    def on_theme_changed(self):
        # ❌ Expensive operation on every theme change
        self.rebuild_entire_ui()  # BAD!
        self.recalculate_complex_layout()  # BAD!
```

**Solutions**:

```python
# Solution 1: Lightweight on_theme_changed()
def on_theme_changed(self):
    # ✅ Just trigger repaint
    self.update()  # Fast!

# Solution 2: Defer expensive work
def on_theme_changed(self):
    # Schedule expensive work for later
    QTimer.singleShot(0, self._rebuild_ui_async)

def _rebuild_ui_async(self):
    # Expensive work here
    self.rebuild_ui()

# Solution 3: Batch widget creation
# Create widgets in groups, not one at a time
widgets = []
for i in range(100):
    widget = MyWidget()  # Don't show yet
    widgets.append(widget)

# Show all at once (single theme application)
for widget in widgets:
    layout.addWidget(widget)
```

---

### ❌ High CPU Usage During Painting

**Problem**: Painting uses too much CPU.

**Diagnosis**:

```python
def paintEvent(self, event):
    # ❌ Resolving on every paint (expensive!)
    manager = ThemeManager.get_instance()
    for i in range(100):
        bg = manager.resolve_color('editor.background')  # Resolved 100x per paint!
```

**Solution**: Use cached properties

```python
# ✅ Solution 1: Use theme_config (automatic caching)
class MyWidget(ThemedWidget, QWidget):
    theme_config = {'bg': 'editor.background'}

    def paintEvent(self, event):
        bg = self.theme.bg  # Cached! Fast! ✅

# ✅ Solution 2: Cache in on_theme_changed()
class MyWidget(ThemedWidget, QWidget):
    def __init__(self):
        super().__init__()
        self._cached_bg = None

    def on_theme_changed(self):
        manager = ThemeManager.get_instance()
        self._cached_bg = QColor(manager.resolve_color('editor.background'))
        self.update()

    def paintEvent(self, event):
        if self._cached_bg:
            painter.fillRect(self.rect(), self._cached_bg)  # Fast!
```

---

## Integration Issues

### ❌ Stylesheet Not Updating

**Problem**: Widget stylesheet doesn't reflect theme changes.

**Diagnosis**:

```python
# Check if stylesheet is being set manually
widget.setStyleSheet("background: #ffffff;")  # ❌ Overrides theme!
```

**Solution**: Use theme-based stylesheets or remove manual styling

```python
# ✅ Solution 1: Remove manual stylesheet (let theme handle it)
# widget.setStyleSheet("")  # Clear manual stylesheet

# ✅ Solution 2: Use theme colors in stylesheet
def on_theme_changed(self):
    manager = ThemeManager.get_instance()
    bg = manager.resolve_color('window.background', fallback='#1e1e1e')
    fg = manager.resolve_color('window.foreground', fallback='#d4d4d4')

    self.setStyleSheet(f"""
        QWidget {{
            background: {bg};
            color: {fg};
        }}
    """)
```

---

### ❌ Qt Designer Forms Not Themed

**Problem**: Widgets created in Qt Designer don't get themed.

**Solution**: Promote widgets to themed versions

```
1. In Qt Designer:
   - Right-click widget → Promote to...
   - Base class: QWidget
   - Promoted class: ThemedQWidget
   - Header file: vfwidgets_theme
   - Click "Add" then "Promote"

2. In code:
   from vfwidgets_theme import ThemedQWidget
   # Designer-created widget now themed!
```

---

## Theme File Issues

### ❌ Theme Not Loading

**Problem**: Custom theme file doesn't load.

**Diagnosis**:

1. **Check JSON syntax**:
```bash
python -m json.tool mytheme.json
# Should pretty-print JSON without errors
```

2. **Check required fields**:
```json
{
  "name": "My Theme",     // ✅ Required
  "type": "dark",         // ✅ Required
  "colors": {             // ✅ Required
    "colors.foreground": "#ffffff"
  }
}
```

3. **Check file location**:
```bash
# User themes go in:
~/.vfwidgets/themes/mytheme.json
# OR
~/.config/ViloxTerm/themes/mytheme.json
```

**Solution**: Fix JSON and ensure correct location

```bash
# Validate JSON
python -c "import json; print(json.load(open('mytheme.json')))"

# Copy to correct location
cp mytheme.json ~/.vfwidgets/themes/
```

---

### ❌ Colors Look Wrong

**Problem**: Theme colors don't look like expected.

**Common Issues**:

1. **Wrong color format**:
```json
{
  "colors.background": "#1e1e1e",    // ✅ Hex format
  "colors.foreground": "rgb(255,255,255)",  // ✅ RGB format
  "colors.accent": "blue"            // ❌ Named colors not supported!
}
```

2. **Typo in token name**:
```json
{
  "editorGroupHeader.tabsBackgroud": "#ff0000"  // ❌ Typo: "backgroud"
  "editorGroupHeader.tabsBackground": "#ff0000" // ✅ Correct
}
```

3. **Missing alpha channel**:
```json
{
  "scrollbar.background": "#79797940"  // ✅ RRGGBBAA format (40 = 25% opacity)
}
```

---

## Getting More Help

### Enable Debug Logging

```python
import logging

# Enable theme system debug logs
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('vfwidgets_theme')
logger.setLevel(logging.DEBUG)
```

### Inspect Widget State

```python
# Check widget's theme status
print(f"Widget ID: {widget._widget_id}")
print(f"Theme config: {widget._theme_config}")
print(f"Current theme: {widget.get_current_theme().name}")

# Check registered widgets
manager = ThemeManager.get_instance()
widgets = manager._widget_registry.get_all_widgets()
print(f"Registered widgets: {len(widgets)}")
```

### Check Override State

```python
manager = ThemeManager.get_instance()

# Dump all overrides
print(f"App overrides: {manager.get_app_overrides()}")
print(f"User overrides: {manager.get_user_overrides()}")
print(f"All effective: {manager.get_all_effective_overrides()}")

# Test specific token
token = "editor.background"
effective = manager.get_effective_color(token)
print(f"Effective color for {token}: {effective}")
```

---

## Summary of Common Pitfalls

**Top 5 Issues**:

1. ❌ **Bypassing override system** → Use `theme_config` or `resolve_color()`, never `theme.colors.get()`
2. ❌ **Wrong token name** → Use `editorGroupHeader.tabsBackground` for top bar, not `tab.*`
3. ❌ **Wrong inheritance order** → `ThemedWidget` must come FIRST
4. ❌ **Stale cache in on_theme_changed()** → Query ThemeManager directly or use ColorProperty
5. ❌ **Manual stylesheet overrides theme** → Remove `setStyleSheet()` or use theme colors

**Key Documentation**:
- [TOKEN-RESOLUTION.md](TOKEN-RESOLUTION.md) - How resolution works
- [THEMED-WIDGET-INTEGRATION.md](THEMED-WIDGET-INTEGRATION.md) - ThemedWidget + Overrides
- [tokens-GUIDE.md](tokens-GUIDE.md) - Available tokens
- [widget-development-GUIDE.md](widget-development-GUIDE.md) - ThemedWidget usage

---

**Last Updated**: 2025-10-18
**Version**: 2.1.0
