# VFWidgets Theming System - Official Developer Guide

**Version:** 2.0
**Last Updated:** 2025-10-02
**Target Audience:** Developers building themed applications and custom widgets

---

## Table of Contents

1. [Quick Start (5 minutes)](#quick-start)
2. [The Two Use Cases](#the-two-use-cases)
3. [Simple Widgets (80% Case)](#simple-widgets)
4. [Complex Widgets (20% Case)](#complex-widgets)
5. [Theme Access Patterns](#theme-access-patterns)
6. [Common Recipes](#common-recipes)
7. [Tips & Tricks](#tips-and-tricks)
8. [Troubleshooting](#troubleshooting)
9. [API Reference](#api-reference)

---

## Quick Start

### Install and Run

```bash
pip install vfwidgets-theme
```

```python
from vfwidgets_theme import ThemedApplication, ThemedWidget
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

class MyWindow(ThemedWidget, QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Hello, themed world!"))

app = ThemedApplication(theme_name='dark')
window = MyWindow()
window.show()
app.exec()
```

**That's it!** Your application is now themed.

---

## The Two Use Cases

### 🎨 Simple Widgets (80% of cases)
**You use Qt stylesheets and standard widgets.**
- Just inherit `ThemedWidget`
- Everything styles automatically
- Minimal code needed

### 🎨 Complex Widgets (20% of cases)
**You have custom painting, renderers, or child components.**
- Custom `paintEvent()` that needs theme colors
- External renderers that need theme data
- Child widgets (non-ThemedWidget) that need theme
- Multi-component widgets with shared theme

**This guide covers BOTH cases clearly.**

---

## Simple Widgets

### Pattern: Just Inherit ThemedWidget

```python
from vfwidgets_theme import ThemedWidget
from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout

class MyWidget(ThemedWidget, QWidget):
    """Simple widget - stylesheet handles everything"""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # These get styled automatically
        layout.addWidget(QPushButton("Primary"))
        layout.addWidget(QPushButton("Secondary"))
```

**How it works:**
1. ThemedWidget sets up theme system
2. Qt stylesheet applied to entire widget tree
3. All child widgets styled automatically
4. Theme changes update everything

**When to use:**
- ✅ Using standard Qt widgets
- ✅ Rely on Qt stylesheets
- ✅ No custom painting needed
- ✅ No external components

---

### Pattern: Custom Painting with theme_config

```python
from vfwidgets_theme import ThemedWidget
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor
from PySide6.QtCore import Qt

class CustomButton(ThemedWidget, QWidget):
    """Custom painting using theme colors"""

    # Map friendly names to theme tokens
    theme_config = {
        'bg': 'button.background',
        'fg': 'button.foreground',
        'hover_bg': 'button.hoverBackground',
    }

    def paintEvent(self, event):
        painter = QPainter(self)

        # Access theme via friendly names
        bg = QColor(self.theme.bg)
        fg = QColor(self.theme.fg)

        painter.fillRect(self.rect(), bg)
        painter.setPen(fg)
        painter.drawText(self.rect(), Qt.AlignCenter, "Button")
```

**How theme_config works:**
- Maps friendly names → theme token paths
- `self.theme.bg` resolves via theme_config
- Automatic fallback to smart defaults
- Changes with theme automatically

**When to use:**
- ✅ Custom paintEvent()
- ✅ Need theme colors
- ✅ Want simple property access
- ✅ Single widget (no children needing theme)

---

## Complex Widgets

### Pattern: Passing Theme to Renderers

**Problem:** You have a custom renderer that needs theme colors.

```python
from vfwidgets_theme import ThemedWidget
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter

class ChromeTabRenderer:
    """External renderer that draws tabs"""

    @staticmethod
    def draw(painter, rect, theme):
        """Draw tab using theme colors"""
        bg = theme.colors.get('tab.activeBackground', '#2d2d2d')
        fg = theme.colors.get('tab.activeForeground', '#ffffff')

        painter.fillRect(rect, QColor(bg))
        painter.setPen(QColor(fg))
        painter.drawText(rect, Qt.AlignCenter, "Tab")

class ChromeTabbedWindow(ThemedWidget, QWidget):
    """Widget with external renderer"""

    def __init__(self):
        super().__init__()
        self.renderer = ChromeTabRenderer()

    def paintEvent(self, event):
        painter = QPainter(self)

        # Get Theme object to pass to renderer
        theme = self.get_current_theme()
        if theme:
            self.renderer.draw(painter, self.rect(), theme)
```

**Key points:**
- Use `self.get_current_theme()` to get actual Theme object
- Pass Theme object to external components
- Theme object has `.colors` dict with all colors
- Use `.get()` with defaults for safety

**When to use:**
- ✅ External renderers/painters
- ✅ Need to pass theme elsewhere
- ✅ Custom rendering logic
- ✅ Helper classes need theme data

---

### Pattern: Child Widgets Need Theme

**Problem:** You have child widgets (non-ThemedWidget) that need theme.

```python
from vfwidgets_theme import ThemedWidget
from PySide6.QtWidgets import QWidget, QTabBar

class ChromeTabBar(QTabBar):
    """Child widget - NOT inheriting ThemedWidget"""

    def __init__(self, parent, theme):
        super().__init__(parent)
        self._theme = theme  # Store theme

    def paintEvent(self, event):
        painter = QPainter(self)

        # Use stored theme
        bg = self._theme.colors.get('tab.activeBackground', '#2d2d2d')
        painter.fillRect(self.rect(), QColor(bg))

class ChromeTabbedWindow(ThemedWidget, QWidget):
    """Parent widget provides theme to children"""

    def __init__(self):
        super().__init__()

        # Get theme and pass to child
        theme = self.get_current_theme()
        self.tab_bar = ChromeTabBar(self, theme=theme)

    def on_theme_changed(self):
        """Theme changed - update children"""
        theme = self.get_current_theme()
        if hasattr(self.tab_bar, '_theme'):
            self.tab_bar._theme = theme
            self.tab_bar.update()
```

**Key points:**
- Parent calls `get_current_theme()` to get Theme object
- Pass theme explicitly to child constructor
- Store theme in child's `_theme` attribute
- Override `on_theme_changed()` to update children

**When to use:**
- ✅ Child widgets don't inherit ThemedWidget
- ✅ Third-party widgets need theme
- ✅ Performance-critical children
- ✅ Multiple components share theme

---

### Pattern: Helper for Theme Propagation

**Problem:** Lots of children need theme - tedious to pass manually.

```python
from vfwidgets_theme import ThemedWidget
from PySide6.QtWidgets import QWidget

class ComplexWidget(ThemedWidget, QWidget):
    """Widget with many themed children"""

    def __init__(self):
        super().__init__()

        # Create multiple children with theme
        self.child1 = self._create_themed_child(ChildWidget)
        self.child2 = self._create_themed_child(AnotherChild)
        self.child3 = self._create_themed_child(ThirdChild)

    def _create_themed_child(self, widget_class, *args, **kwargs):
        """Helper: create child widget with theme"""
        theme = self.get_current_theme()
        return widget_class(*args, parent=self, theme=theme, **kwargs)

    def on_theme_changed(self):
        """Update all themed children"""
        theme = self.get_current_theme()
        for child in [self.child1, self.child2, self.child3]:
            if hasattr(child, '_theme'):
                child._theme = theme
                child.update()
```

**Key points:**
- Create helper method `_create_themed_child()`
- Centralizes theme passing logic
- Easier to update all children on theme change
- Reduces boilerplate

**When to use:**
- ✅ Many children need theme
- ✅ Want cleaner code
- ✅ Standard pattern across widget
- ✅ Easy maintenance

---

## Theme Access Patterns

### The Official API

```python
class ThemedWidget:
    """Official theme access methods"""

    @property
    def theme(self) -> ThemeAccess:
        """Smart property access (80% case)

        Use this for: self.theme.bg, self.theme.fg, etc.
        Works with theme_config mappings.
        Provides smart defaults automatically.
        """

    def get_current_theme(self) -> Theme:
        """Get Theme object (20% case)

        Use this when you need to:
        - Pass theme to renderers
        - Pass theme to child widgets
        - Access theme.colors dict directly
        - Store theme for later use
        """

    def on_theme_changed(self):
        """Override to respond to theme changes

        Called automatically when app theme changes.
        Default behavior: calls self.update()
        Override to update children, cache, etc.
        """
```

### When to Use Which

**Use `self.theme.property`:**
```python
def paintEvent(self, event):
    bg = self.theme.bg  # ✅ Simple property access
    fg = self.theme.fg
```

**Use `get_current_theme()`:**
```python
def __init__(self):
    theme = self.get_current_theme()  # ✅ Get Theme object
    self.child = Child(theme=theme)    # Pass to others
    self.renderer = Renderer(theme)
```

**Use `on_theme_changed()`:**
```python
def on_theme_changed(self):
    # ✅ Update children when theme changes
    theme = self.get_current_theme()
    self.child._theme = theme
    self.child.update()
```

---

## Common Recipes

### Recipe 1: Themed Button with Hover

```python
class ThemedButton(ThemedWidget, QPushButton):
    theme_config = {
        'normal_bg': 'button.background',
        'hover_bg': 'button.hoverBackground',
        'active_bg': 'button.activeBackground',
        'fg': 'button.foreground',
    }

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setText(text)
        self._hovered = False

    def enterEvent(self, event):
        self._hovered = True
        self.update()

    def leaveEvent(self, event):
        self._hovered = False
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        # Choose color based on state
        if self.isDown():
            bg = self.theme.active_bg
        elif self._hovered:
            bg = self.theme.hover_bg
        else:
            bg = self.theme.normal_bg

        painter.fillRect(self.rect(), QColor(bg))
        painter.setPen(QColor(self.theme.fg))
        painter.drawText(self.rect(), Qt.AlignCenter, self.text())
```

---

### Recipe 2: Multi-Component Widget

```python
class IDEWidget(ThemedWidget, QWidget):
    """IDE with editor, sidebar, statusbar"""

    def __init__(self):
        super().__init__()

        # Get theme once
        theme = self.get_current_theme()

        # Pass to all components
        self.editor = EditorWidget(theme=theme)
        self.sidebar = SidebarWidget(theme=theme)
        self.statusbar = StatusBarWidget(theme=theme)

        # Layout
        layout = QHBoxLayout(self)
        layout.addWidget(self.sidebar)
        layout.addWidget(self.editor)

        statusbar_layout = QVBoxLayout()
        statusbar_layout.addLayout(layout)
        statusbar_layout.addWidget(self.statusbar)
        self.setLayout(statusbar_layout)

    def on_theme_changed(self):
        """Propagate theme changes to all components"""
        theme = self.get_current_theme()

        for component in [self.editor, self.sidebar, self.statusbar]:
            if hasattr(component, 'set_theme'):
                component.set_theme(theme)

class EditorWidget(QWidget):
    """Non-ThemedWidget that receives theme"""

    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self._theme = theme

    def set_theme(self, theme):
        """Update theme"""
        self._theme = theme
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        bg = self._theme.colors.get('editor.background', '#1e1e1e')
        painter.fillRect(self.rect(), QColor(bg))
```

---

### Recipe 3: Frameless Window with Custom Chrome

```python
class FramelessWindow(ThemedWidget, QWidget):
    """Custom window chrome with theme support"""

    def __init__(self):
        super().__init__()

        # Frameless
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Get theme for chrome components
        theme = self.get_current_theme()

        # Custom title bar
        self.title_bar = TitleBar(theme=theme, parent=self)

        # Content area
        self.content = QWidget(self)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.title_bar)
        layout.addWidget(self.content)

    def on_theme_changed(self):
        """Update custom chrome"""
        theme = self.get_current_theme()
        self.title_bar.set_theme(theme)

class TitleBar(QWidget):
    """Custom title bar that uses theme"""

    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self._theme = theme
        self.setFixedHeight(32)

    def set_theme(self, theme):
        self._theme = theme
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        # Use theme colors for chrome
        bg = self._theme.colors.get('titleBar.activeBackground', '#2d2d2d')
        fg = self._theme.colors.get('titleBar.activeForeground', '#ffffff')

        painter.fillRect(self.rect(), QColor(bg))
        painter.setPen(QColor(fg))
        painter.drawText(self.rect(), Qt.AlignCenter, "My App")
```

---

## Tips and Tricks

### Tip 1: Cache Theme Colors in Constructor

**Don't:**
```python
def paintEvent(self, event):
    # Resolves theme color every paint!
    bg = self.theme.bg
    painter.fillRect(self.rect(), QColor(bg))
```

**Do:**
```python
def __init__(self):
    super().__init__()
    self._update_colors()

def _update_colors(self):
    """Cache theme colors"""
    self._bg = QColor(self.theme.bg)
    self._fg = QColor(self.theme.fg)

def on_theme_changed(self):
    """Update cache when theme changes"""
    self._update_colors()
    self.update()

def paintEvent(self, event):
    # Use cached color - much faster!
    painter.fillRect(self.rect(), self._bg)
```

---

### Tip 2: Always Provide Defaults

**Don't:**
```python
theme = self.get_current_theme()
bg = theme.colors['button.background']  # KeyError if missing!
```

**Do:**
```python
theme = self.get_current_theme()
bg = theme.colors.get('button.background', '#0078d4')  # Safe default
```

---

### Tip 3: Test Without ThemedApplication

**Your widgets should work even without themed app:**

```python
class MyWidget(ThemedWidget, QWidget):
    def paintEvent(self, event):
        theme = self.get_current_theme()

        # Graceful fallback if no theme
        if theme:
            bg = theme.colors.get('button.background', '#0078d4')
        else:
            bg = '#0078d4'  # Fallback

        painter.fillRect(self.rect(), QColor(bg))
```

---

### Tip 4: Use theme_config for Simple Cases

**If you only need a few colors, theme_config is cleaner:**

```python
# Instead of:
def paintEvent(self, event):
    theme = self.get_current_theme()
    bg = theme.colors.get('button.background', '#default')

# Do this:
theme_config = {'bg': 'button.background'}

def paintEvent(self, event):
    bg = self.theme.bg  # Cleaner!
```

---

### Tip 5: Document Theme Tokens Used

**Help future maintainers:**

```python
class MyWidget(ThemedWidget, QWidget):
    """Custom widget with themed appearance.

    Theme tokens used:
    - button.background: Main background color
    - button.foreground: Text color
    - button.hoverBackground: Hover state color
    - button.border: Border color
    """

    theme_config = {
        'bg': 'button.background',
        'fg': 'button.foreground',
        'hover_bg': 'button.hoverBackground',
        'border': 'button.border',
    }
```

---

## Troubleshooting

### Issue: `get_current_theme()` returns None

**Cause:** Theme system not initialized or no ThemedApplication.

**Solution:**
```python
theme = self.get_current_theme()
if not theme:
    # Fallback or error handling
    logger.warning("Theme not available, using defaults")
    return
```

---

### Issue: Children don't update when theme changes

**Cause:** Not overriding `on_theme_changed()` to update children.

**Solution:**
```python
def on_theme_changed(self):
    """Propagate theme change to children"""
    theme = self.get_current_theme()

    for child in self.findChildren(QWidget):
        if hasattr(child, 'set_theme'):
            child.set_theme(theme)

    self.update()
```

---

### Issue: Colors don't match theme

**Cause:** Using wrong token names or tokens don't exist in theme.

**Solution:**
```python
# Check what tokens exist in theme
theme = self.get_current_theme()
if theme:
    print("Available tokens:", list(theme.colors.keys())[:20])

# Use .get() with defaults
bg = theme.colors.get('button.background', '#0078d4')
```

---

### Issue: Performance issues with theme access

**Cause:** Resolving theme colors in paint loop.

**Solution:** Cache colors, update in `on_theme_changed()`:
```python
def __init__(self):
    super().__init__()
    self._cached_colors = {}
    self._update_color_cache()

def _update_color_cache(self):
    theme = self.get_current_theme()
    if theme:
        self._cached_colors = {
            'bg': QColor(theme.colors.get('button.background', '#0078d4')),
            'fg': QColor(theme.colors.get('button.foreground', '#ffffff')),
        }

def on_theme_changed(self):
    self._update_color_cache()
    self.update()

def paintEvent(self, event):
    painter.fillRect(self.rect(), self._cached_colors['bg'])
```

---

## API Reference

### ThemedWidget

```python
class ThemedWidget:
    """Base class for themed widgets"""

    # Class attribute
    theme_config: dict = {}
        """Maps friendly names to theme token paths

        Example:
            theme_config = {
                'bg': 'button.background',
                'fg': 'button.foreground',
            }
        """

    # Instance property
    @property
    def theme(self) -> ThemeAccess:
        """Smart theme property access

        Returns ThemeAccess object that resolves properties
        via theme_config with automatic fallbacks.

        Example:
            bg = self.theme.bg  # Resolves via theme_config
        """

    # Instance method
    def get_current_theme(self) -> Optional[Theme]:
        """Get actual Theme object

        Returns the Theme object with .colors dict and .name.
        Returns None if theme system not initialized.

        Use this when you need to:
        - Pass theme to other components
        - Access theme.colors dict directly
        - Store theme reference

        Example:
            theme = self.get_current_theme()
            if theme:
                self.child = Child(theme=theme)
        """

    # Override method
    def on_theme_changed(self):
        """Called when application theme changes

        Override this to respond to theme changes.
        Note: self.update() is already called automatically
        by the framework BEFORE on_theme_changed().

        Use this only if you need additional logic like
        updating children or invalidating caches.

        Example:
            def on_theme_changed(self):
                # self.update() already called automatically
                # Just update children
                theme = self.get_current_theme()
                self.child._theme = theme
                self.child.update()
        """
```

### Theme Object

```python
@dataclass(frozen=True)
class Theme:
    """Immutable theme data"""

    name: str              # Theme name (e.g., 'dark', 'light')
    version: str           # Semantic version
    colors: Dict[str, str] # Color token dictionary
    styles: Dict[str, Any] # Style properties
    metadata: Dict         # Additional metadata
    type: str             # 'light', 'dark', or 'high-contrast'
```

### ThemedApplication

```python
class ThemedApplication(QApplication):
    """Application with theme support"""

    def __init__(self, theme_name: str = 'dark', *args, **kwargs):
        """Create themed application

        Args:
            theme_name: Initial theme ('dark', 'light', 'default')
        """

    def set_theme(self, theme_name: str) -> bool:
        """Change application theme

        Args:
            theme_name: Theme to switch to

        Returns:
            True if successful, False otherwise
        """

    def get_available_themes(self) -> List[str]:
        """Get list of available theme names"""

    # Signal
    theme_changed: Signal(str)
        """Emitted when theme changes (theme_name)"""
```

---

## Summary: The One Pattern

### Remember This:

**For 80% of widgets:**
```python
class SimpleWidget(ThemedWidget, QWidget):
    theme_config = {'bg': 'window.background'}

    def paintEvent(self, event):
        bg = self.theme.bg  # Simple!
```

**For 20% of widgets:**
```python
class ComplexWidget(ThemedWidget, QWidget):
    def __init__(self):
        super().__init__()
        theme = self.get_current_theme()  # Get Theme object
        self.child = Child(theme=theme)    # Pass to children

    def on_theme_changed(self):
        theme = self.get_current_theme()   # Update children
        self.child._theme = theme
        self.child.update()
```

**That's the entire API. Everything else is variations on these two patterns.**

---

**Questions? Check:**
- `examples/` - Working examples of all patterns
- `docs/widget-development-GUIDE.md` - Additional widget development tips
- `docs/theme-api-issues-ANALYSIS.md` - Deep architectural details

**Happy theming! 🎨**
