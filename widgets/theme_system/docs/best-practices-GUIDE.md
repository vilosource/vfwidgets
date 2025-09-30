# Best Practices Guide - VFWidgets Theme System

## The Golden Rule

**Use ThemedWidget. It provides clean architecture as THE way.**

```python
# This is the correct approach - always!
from vfwidgets_theme import ThemedWidget

class YourWidget(ThemedWidget):
    pass  # Clean architecture built-in!
```

## Core Principles

### 1. Clean Architecture as THE Way
ThemedWidget provides the simple API that's architecturally correct. No compromises.

### 2. Progressive Enhancement
Start with ThemedWidget, add complexity only when needed.

### 3. Convention Over Configuration
ThemedWidget handles everything by default, configure only what's special.

### 4. Built-in Best Practices
Memory safety, thread safety, and proper cleanup are automatic with ThemedWidget.

## Widget Development Best Practices

### ✅ DO: Always Use ThemedWidget

```python
# ✅ CORRECT - ThemedWidget is THE way
class GoodWidget(ThemedWidget):
    pass

# ❌ WRONG - Direct QWidget loses all benefits
class BadWidget(QWidget):
    pass

# ❌ WRONG - Direct ThemeManager access breaks architecture
class BadWidget(QWidget):
    def __init__(self):
        self.tm = ThemeManager.instance()  # Don't do this!
```

### ✅ DO: Use theme_config for Properties

```python
# ✅ CORRECT - Declarative configuration
class GoodWidget(ThemedWidget):
    theme_config = {
        'bg': 'window.background',
        'fg': 'window.foreground',
        'accent': 'accent.primary'
    }

    def paintEvent(self, event):
        color = self.theme.bg  # Direct access!

# ❌ WRONG - Hardcoded colors
class BadWidget(ThemedWidget):
    def __init__(self):
        self.bg_color = "#1e1e1e"  # Hardcoded!
```

### ✅ DO: Override on_theme_changed() for Updates

```python
# ✅ CORRECT - Proper theme reaction
class GoodWidget(ThemedWidget):
    def on_theme_changed(self):
        if self.is_dark_theme:
            self.load_dark_icons()
        self.update()  # Trigger repaint

# ❌ WRONG - Manual theme tracking
class BadWidget(ThemedWidget):
    def __init__(self):
        self.current_theme = "dark"  # Manual tracking
```

### ✅ DO: Provide Defaults

```python
# ✅ CORRECT - Graceful fallback
class GoodWidget(ThemedWidget):
    def paintEvent(self, event):
        color = self.get_theme_color("custom.color", default="#0066cc")

# ❌ WRONG - No fallback
class BadWidget(ThemedWidget):
    def paintEvent(self, event):
        color = self.get_theme_color("custom.color")  # May fail!
```

### ✅ DO: Let ThemedWidget Handle Lifecycle

```python
# ✅ CORRECT - ThemedWidget manages everything
class GoodWidget(ThemedWidget):
    def __init__(self):
        super().__init__()  # ThemedWidget handles cleanup!

# ❌ WRONG - Manual lifecycle management
class BadWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.register_for_themes()  # Manual!

    def __del__(self):
        self.unregister_from_themes()  # Manual!
```

## Performance Best Practices

### Use theme_config for Efficiency

```python
# ✅ CORRECT - Properties cached automatically
class FastWidget(ThemedWidget):
    theme_config = {
        'bg': 'window.background',
        'fg': 'window.foreground'
    }

    def paintEvent(self, event):
        # Direct access, cached internally
        bg = self.theme.bg
        fg = self.theme.fg

# ❌ WRONG - Repeated lookups
class SlowWidget(ThemedWidget):
    def paintEvent(self, event):
        # Lookup every time
        bg = self.get_theme_color("window.background")
        fg = self.get_theme_color("window.foreground")
```

### Batch Updates in on_theme_changed()

```python
# ✅ CORRECT - Single update method
class GoodWidget(ThemedWidget):
    def on_theme_changed(self):
        # Batch all updates
        self.setUpdatesEnabled(False)
        self.update_colors()
        self.update_icons()
        self.update_layout()
        self.setUpdatesEnabled(True)

# ❌ WRONG - Multiple callbacks
class BadWidget(ThemedWidget):
    def __init__(self):
        # Don't add multiple listeners!
        theme_manager.theme_changed.connect(self.update_colors)
        theme_manager.theme_changed.connect(self.update_icons)
        theme_manager.theme_changed.connect(self.update_layout)
```

## Application Architecture Best Practices

### ✅ DO: Use ThemedApplication

```python
# ✅ CORRECT - ThemedApplication handles everything
from vfwidgets_theme import ThemedApplication, ThemedWidget

app = ThemedApplication(sys.argv)
app.set_theme("dark-modern")

class MainWindow(ThemedWidget):
    pass

window = MainWindow()
window.show()
app.exec()

# ❌ WRONG - Manual application setup
app = QApplication(sys.argv)
tm = ThemeManager()
tm.load_theme("dark-modern")
# Complex manual setup...
```

### ✅ DO: Let ThemedApplication Manage Themes

```python
# ✅ CORRECT - Use ThemedApplication methods
app = ThemedApplication(sys.argv)
app.set_theme("dark-modern")
app.import_vscode_theme("monokai.json")
app.toggle_dark_mode()

# ❌ WRONG - Direct ThemeManager manipulation
tm = ThemeManager.instance()
tm.load_builtin_theme("dark-modern")
```

## Testing Best Practices

### Use Built-in Testing Support

```python
# ✅ CORRECT - Use ThemedTestCase
from vfwidgets_theme.testing import ThemedTestCase

class TestMyWidget(ThemedTestCase):
    def test_theming(self):
        widget = MyWidget()  # Must inherit ThemedWidget!

        self.apply_test_theme("dark")
        self.assertTrue(widget.is_dark_theme)

        self.apply_test_theme("light")
        self.assertFalse(widget.is_dark_theme)

# ❌ WRONG - Manual theme testing
class BadTest(unittest.TestCase):
    def test_theming(self):
        tm = ThemeManager()
        widget = MyWidget()
        # Complex manual setup...
```

### Mock Themes Properly

```python
# ✅ CORRECT - Use MockThemeProvider
from vfwidgets_theme.testing import MockThemeProvider

def test_widget():
    mock = MockThemeProvider({
        "button.background": "#ff0000"
    })

    widget = MyButton()  # Must inherit ThemedWidget!
    widget._theme_provider = mock  # Dependency injection

    assert widget.theme.bg == "#ff0000"
```

## Common Anti-Patterns to Avoid

### ❌ Anti-Pattern: Bypassing ThemedWidget

```python
# ❌ NEVER DO THIS
class BadWidget(QWidget):
    def __init__(self):
        super().__init__()
        # Trying to add theming manually
        self.tm = ThemeManager.instance()
        self.tm.register_widget(self)

# ✅ ALWAYS DO THIS
class GoodWidget(ThemedWidget):
    pass  # Everything handled!
```

### ❌ Anti-Pattern: Hardcoded Colors

```python
# ❌ NEVER DO THIS
class BadWidget(ThemedWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: #1e1e1e")  # Hardcoded!

# ✅ ALWAYS DO THIS
class GoodWidget(ThemedWidget):
    theme_config = {'bg': 'window.background'}

    def on_theme_changed(self):
        self.setStyleSheet(f"background: {self.theme.bg}")
```

### ❌ Anti-Pattern: Manual Memory Management

```python
# ❌ NEVER DO THIS
class BadWidget(QWidget):
    def __init__(self):
        self.theme_refs = []  # Manual reference tracking

    def __del__(self):
        self.cleanup_themes()  # Manual cleanup

# ✅ ALWAYS DO THIS
class GoodWidget(ThemedWidget):
    pass  # WeakRefs and cleanup handled automatically!
```

### ❌ Anti-Pattern: Theme-Specific Logic

```python
# ❌ NEVER DO THIS
class BadWidget(ThemedWidget):
    def update(self):
        if self.current_theme.name == "Dark Modern":
            # Specific to one theme

# ✅ ALWAYS DO THIS
class GoodWidget(ThemedWidget):
    def on_theme_changed(self):
        if self.is_dark_theme:
            # Works with any dark theme
```

## Migration Best Practice

### The One Rule for Migration

```python
# Before: Any existing widget
class OldWidget(QWidget):
    def __init__(self):
        super().__init__()
        # Complex manual theming...

# After: Just change the base class!
class NewWidget(ThemedWidget):
    def __init__(self):
        super().__init__()
        # Same code, now with clean architecture!
```

## Documentation Best Practices

### Document Your theme_config

```python
class CustomWidget(ThemedWidget):
    """
    Custom widget with automatic theming.

    Uses ThemedWidget for clean architecture with:
    - Memory safety (WeakRefs)
    - Thread safety (Qt signals)
    - Automatic cleanup

    Theme Properties:
        bg: Uses 'panel.background'
        accent: Uses 'accent.primary'
        border: Uses 'panel.border' (default: #333)
    """
    theme_config = {
        'bg': 'panel.background',
        'accent': 'accent.primary',
        'border': 'panel.border'
    }
```

## Debugging Best Practices

### Use Built-in Debugging

```python
# ✅ CORRECT - Use ThemedApplication debug mode
app = ThemedApplication(sys.argv, debug=True)
# Shows theme resolution and performance

# Check widget state
widget = MyWidget()
print(f"Theme type: {widget.theme_type}")
print(f"Is dark: {widget.is_dark_theme}")
```

## The Architecture You Get for Free

When you use ThemedWidget, you automatically get:

1. **Memory Safety** - WeakRef registry prevents leaks
2. **Thread Safety** - Qt signals handle updates correctly
3. **Dependency Injection** - ThemeProvider pattern built-in
4. **Lifecycle Management** - Automatic cleanup on deletion
5. **Error Recovery** - Fallback to minimal theme
6. **Performance Optimization** - Caching and lazy loading
7. **Testing Support** - MockThemeProvider for isolation
8. **Child Widget Theming** - Children automatically themed

## Summary Checklist

### For Every Widget
- [ ] Inherits from `ThemedWidget` (not QWidget)
- [ ] Uses `theme_config` for custom properties
- [ ] Overrides `on_theme_changed()` if needed
- [ ] No hardcoded colors
- [ ] Calls `super().__init__()`

### For Every Application
- [ ] Uses `ThemedApplication` (not QApplication)
- [ ] Calls `app.set_theme()` to set theme
- [ ] No direct ThemeManager access
- [ ] Theme set before creating widgets

### For Testing
- [ ] Uses `ThemedTestCase` for widget tests
- [ ] Uses `MockThemeProvider` for unit tests
- [ ] Tests both dark and light themes

## The Most Important Rule

**Always use ThemedWidget. It's not just the easy way - it's the correct way.**

```python
# This is all you need to remember:
class YourWidget(ThemedWidget):
    pass  # Clean architecture, no compromises!
```

---

*ThemedWidget provides clean architecture as THE way. Simple API, correct implementation, no compromises.*