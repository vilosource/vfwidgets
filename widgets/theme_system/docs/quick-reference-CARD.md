# 🎯 VFWidgets Theme System - Quick Reference Card

## The 30-Second Solution

```python
# Your entire themed app:
from vfwidgets_theme import ThemedApplication, ThemedWidget
import sys

app = ThemedApplication(sys.argv)
app.set_theme("dark-modern")

class MyWidget(ThemedWidget):  # ✅ That's it! Clean architecture built-in!
    pass

widget = MyWidget()
widget.show()
app.exec()
```

## Do I Need More? (Decision Tree)

```
My widget needs...
├─ Basic theming? → Just inherit ThemedWidget → DONE! ✅
├─ Custom colors? → Add theme_config dictionary
├─ React to theme changes? → Override on_theme_changed()
├─ Custom painting? → Use self.theme.property in paintEvent
└─ Nothing special? → ThemedWidget handles everything!
```

## The Two Classes You Use

### 1. ThemedApplication - Your App
```python
app = ThemedApplication(sys.argv)
app.set_theme("dark-modern")  # or "light-default" or custom
```

### 2. ThemedWidget - Your Widgets
```python
class YourWidget(ThemedWidget):
    pass  # Fully themed with clean architecture!
```

## Common Patterns - Copy & Paste

### Pattern 1: Widget with Custom Colors
```python
class ColoredWidget(ThemedWidget):
    theme_config = {
        'bg': 'window.background',
        'fg': 'window.foreground',
        'accent': 'accent.primary'
    }

    def paintEvent(self, event):
        # Use theme colors
        color = self.theme.bg  # Direct property access!
```

### Pattern 2: React to Theme Changes
```python
class ReactiveWidget(ThemedWidget):
    def on_theme_changed(self):
        """Called automatically when theme changes"""
        if self.is_dark_theme:
            self.load_dark_icons()
        else:
            self.load_light_icons()
        self.update()  # Trigger repaint
```

### Pattern 3: Button with Theme Colors
```python
class ThemedButton(ThemedWidget, QPushButton):
    theme_config = {
        'bg': 'button.background',
        'hover': 'button.hoverBackground'
    }

    def on_theme_changed(self):
        self.setStyleSheet(f"""
            QPushButton {{ background: {self.theme.bg}; }}
            QPushButton:hover {{ background: {self.theme.hover}; }}
        """)
```

### Pattern 4: Editor with Theme
```python
class ThemedEditor(ThemedWidget, QTextEdit):
    theme_config = {
        'bg': 'editor.background',
        'fg': 'editor.foreground',
        'selection': 'editor.selectionBackground'
    }

    def on_theme_changed(self):
        palette = self.palette()
        palette.setColor(QPalette.Base, QColor(self.theme.bg))
        palette.setColor(QPalette.Text, QColor(self.theme.fg))
        self.setPalette(palette)
```

## What ThemedWidget Does For You

**Automatically Handles:**
- ✅ Theme application and updates
- ✅ Memory management (WeakRefs)
- ✅ Thread safety (Qt signals)
- ✅ Dependency injection
- ✅ Cleanup on widget deletion
- ✅ Child widget theming
- ✅ Error recovery

**You Just:**
- Inherit from `ThemedWidget`
- Optionally add `theme_config`
- Optionally override `on_theme_changed()`

## Helper Properties & Methods

```python
class YourWidget(ThemedWidget):
    def example(self):
        # Properties available in every ThemedWidget:
        self.theme.bg           # Access configured properties
        self.is_dark_theme      # True if dark theme
        self.theme_type         # "dark" or "light"

        # Methods available:
        self.get_theme_color("button.background", default="#333")
        self.get_theme_property("editor.fontSize", default=12)
```

## Complete Example Apps

### Minimal App
```python
from vfwidgets_theme import ThemedApplication, ThemedWidget
from PySide6.QtWidgets import QVBoxLayout, QPushButton, QTextEdit
import sys

app = ThemedApplication(sys.argv)
app.set_theme("dark-modern")

class MainWindow(ThemedWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QTextEdit())      # Auto-themed!
        layout.addWidget(QPushButton("Click"))  # Auto-themed!

window = MainWindow()
window.show()
app.exec()
```

### App with Theme Switching
```python
class AppWithSwitcher(ThemedWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # Theme switcher
        self.combo = QComboBox()
        self.combo.addItems(["dark-modern", "light-default"])
        self.combo.currentTextChanged.connect(app.set_theme)
        layout.addWidget(self.combo)

        # Your content
        layout.addWidget(QTextEdit())
```

## ✅ Checklist: Is My Widget Correct?

- [ ] Inherits from `ThemedWidget` not `QWidget`
- [ ] Calls `super().__init__()` in constructor
- [ ] No hardcoded colors (use theme properties)
- [ ] Custom painting calls `self.update()` in `on_theme_changed()`

## ⚠️ Common Mistakes to Avoid

```python
# ❌ WRONG - Direct QWidget
class Bad(QWidget):
    pass

# ✅ RIGHT - ThemedWidget
class Good(ThemedWidget):
    pass

# ❌ WRONG - Hardcoded color
self.setStyleSheet("background: #1e1e1e")

# ✅ RIGHT - Theme color
class Good(ThemedWidget):
    theme_config = {'bg': 'window.background'}
    def on_theme_changed(self):
        self.setStyleSheet(f"background: {self.theme.bg}")

# ❌ WRONG - Accessing ThemeManager directly
tm = ThemeManager.instance()

# ✅ RIGHT - ThemedWidget handles it
class Good(ThemedWidget):
    pass  # Everything handled internally!
```

## Migration in 10 Seconds

```python
# Old code:
class OldWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: white")

# New code:
class NewWidget(ThemedWidget):  # Just change base class!
    theme_config = {'bg': 'window.background'}
    def on_theme_changed(self):
        self.setStyleSheet(f"background: {self.theme.bg}")
```

## VSCode Theme Support

```python
# Use any VSCode theme!
app = ThemedApplication(sys.argv)
app.import_vscode_theme("monokai.json")
app.set_theme("Monokai")
```

## Testing Your Widgets

```python
from vfwidgets_theme.testing import ThemedTestCase

class TestMyWidget(ThemedTestCase):
    def test_theming(self):
        widget = MyWidget()
        self.apply_test_theme("dark")
        self.assertTrue(widget.is_dark_theme)
```

## 📖 Need More?

- **Detailed Examples**: [patterns-cookbook.md](patterns-cookbook.md)
- **Full API**: [api-REFERENCE.md](api-REFERENCE.md)
- **Architecture** (if curious): [architecture-DESIGN.md](architecture-DESIGN.md)

---

**Remember: ThemedWidget = Simple API + Clean Architecture. No compromises!** 🎉