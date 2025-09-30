# Migration Guide - Adopting VFWidgets Theme System

## The 10-Second Migration

```python
# Before: Your existing widget
class MyWidget(QWidget):
    pass

# After: Just change the base class!
from vfwidgets_theme import ThemedWidget
class MyWidget(ThemedWidget):
    pass  # ✅ Done! Clean architecture built-in!
```

**That's it!** You now have:
- ✅ Automatic theming
- ✅ Memory safety (WeakRefs)
- ✅ Thread safety (Qt signals)
- ✅ Clean architecture (dependency injection)
- ✅ Proper cleanup on deletion

## Migration Levels

### Level 1: Just Make It Work (10 seconds)
Change base class to `ThemedWidget`. Done.

### Level 2: Fix Hardcoded Colors (5 minutes)
Replace hardcoded colors with theme properties.

### Level 3: Full Integration (30 minutes)
Add custom theme properties and reactions.

## Quick Migration Checklist

- [ ] Change base class from `QWidget` to `ThemedWidget`
- [ ] Replace hardcoded colors with `theme_config`
- [ ] Override `on_theme_changed()` if needed
- [ ] Test with dark and light themes
- [ ] Remove direct ThemeManager access (if any)

## Common Migration Patterns

### Pattern 1: Basic Widget

**Before:**
```python
from PySide6.QtWidgets import QWidget

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        # Your widget code
```

**After:**
```python
from vfwidgets_theme import ThemedWidget

class MyWidget(ThemedWidget):
    def __init__(self):
        super().__init__()
        # Same widget code - now themed!
```

### Pattern 2: Widget with Hardcoded Colors

**Before:**
```python
class MyButton(QPushButton):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            background-color: #0066cc;
            color: white;
            border-radius: 4px;
        """)
```

**After:**
```python
from vfwidgets_theme import ThemedWidget

class MyButton(ThemedWidget, QPushButton):
    theme_config = {
        'bg': 'button.background',
        'fg': 'button.foreground'
    }

    def on_theme_changed(self):
        self.setStyleSheet(f"""
            background-color: {self.theme.bg};
            color: {self.theme.fg};
            border-radius: 4px;
        """)
```

### Pattern 3: Custom Painted Widget

**Before:**
```python
class CustomWidget(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#1e1e1e"))
        painter.setPen(QColor("#ffffff"))
        painter.drawText(self.rect(), Qt.AlignCenter, "Hello")
```

**After:**
```python
class CustomWidget(ThemedWidget):
    theme_config = {
        'bg': 'window.background',
        'fg': 'window.foreground'
    }

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(self.theme.bg))
        painter.setPen(QColor(self.theme.fg))
        painter.drawText(self.rect(), Qt.AlignCenter, "Hello")

    def on_theme_changed(self):
        self.update()  # Trigger repaint
```

### Pattern 4: Widget with Dark/Light Mode

**Before:**
```python
class DualModeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.dark_mode = False
        self.apply_theme()

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_theme(self):
        if self.dark_mode:
            self.setStyleSheet("background: #1e1e1e; color: #fff;")
            self.icon = QIcon("icons/dark/icon.svg")
        else:
            self.setStyleSheet("background: #fff; color: #000;")
            self.icon = QIcon("icons/light/icon.svg")
```

**After:**
```python
class DualModeWidget(ThemedWidget):
    def on_theme_changed(self):
        # Automatically called when theme changes!
        if self.is_dark_theme:
            self.icon = QIcon("icons/dark/icon.svg")
        else:
            self.icon = QIcon("icons/light/icon.svg")
        # Styling handled automatically by ThemedWidget!
```

## Application-Level Migration

### Before: Manual Application Theming

```python
class MyApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.load_stylesheet()

    def load_stylesheet(self):
        with open("dark_theme.qss", "r") as f:
            self.setStyleSheet(f.read())

app = MyApp(sys.argv)
window = MainWindow()  # Your main window
window.show()
app.exec()
```

### After: Automatic Application Theming

```python
from vfwidgets_theme import ThemedApplication, ThemedWidget

app = ThemedApplication(sys.argv)
app.set_theme("dark-modern")  # or "light-default"

class MainWindow(ThemedWidget):  # Just inherit ThemedWidget!
    pass

window = MainWindow()
window.show()
app.exec()
```

## Migrating from Direct ThemeManager Usage

If you have old code that directly uses ThemeManager (not recommended), here's how to migrate:

### Before: Direct ThemeManager Access

```python
from vfwidgets_theme import ThemeManager

class OldWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.tm = ThemeManager.instance()
        self.tm.register_widget(self)

    def get_color(self):
        return self.tm.get_property("button.background")

    def on_theme_change(self):
        self.apply_colors()
```

### After: Clean ThemedWidget Approach

```python
from vfwidgets_theme import ThemedWidget

class NewWidget(ThemedWidget):
    theme_config = {
        'bg': 'button.background'
    }

    def get_color(self):
        return self.theme.bg  # So much simpler!

    def on_theme_changed(self):
        # Automatically called - no registration needed!
        pass
```

## Complex Migration Example: Code Editor

### Before: Complex Manual Theming

```python
class CodeEditor(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setup_colors()
        self.setup_highlighting()

    def setup_colors(self):
        palette = self.palette()
        palette.setColor(QPalette.Base, QColor("#1e1e1e"))
        palette.setColor(QPalette.Text, QColor("#d4d4d4"))
        palette.setColor(QPalette.Highlight, QColor("#264f78"))
        self.setPalette(palette)

    def setup_highlighting(self):
        self.highlighter = Highlighter(self.document())
        self.highlighter.keyword_format.setForeground(QColor("#569cd6"))
        self.highlighter.string_format.setForeground(QColor("#ce9178"))
        self.highlighter.comment_format.setForeground(QColor("#6a9955"))

    def toggle_dark_mode(self):
        # Complex theme switching logic...
        pass
```

### After: Simple ThemedWidget Approach

```python
from vfwidgets_theme import ThemedWidget

class CodeEditor(ThemedWidget, QTextEdit):
    theme_config = {
        'bg': 'editor.background',
        'fg': 'editor.foreground',
        'selection': 'editor.selectionBackground',
        'keyword': 'tokenColor.keyword',
        'string': 'tokenColor.string',
        'comment': 'tokenColor.comment'
    }

    def __init__(self):
        super().__init__()
        self.setup_highlighting()

    def on_theme_changed(self):
        # Update palette
        palette = self.palette()
        palette.setColor(QPalette.Base, QColor(self.theme.bg))
        palette.setColor(QPalette.Text, QColor(self.theme.fg))
        palette.setColor(QPalette.Highlight, QColor(self.theme.selection))
        self.setPalette(palette)

        # Update highlighter
        if hasattr(self, 'highlighter'):
            self.highlighter.keyword_format.setForeground(QColor(self.theme.keyword))
            self.highlighter.string_format.setForeground(QColor(self.theme.string))
            self.highlighter.comment_format.setForeground(QColor(self.theme.comment))

    def setup_highlighting(self):
        self.highlighter = Highlighter(self.document())
        self.on_theme_changed()  # Apply initial theme
```

## Testing Your Migration

### Simple Test

```python
from vfwidgets_theme import ThemedApplication, ThemedWidget

# Create test app
app = ThemedApplication([])

# Test your migrated widget
widget = YourMigratedWidget()
widget.show()

# Test theme switching
app.set_theme("dark-modern")
assert widget.is_dark_theme

app.set_theme("light-default")
assert not widget.is_dark_theme
```

### Unit Testing

```python
from vfwidgets_theme.testing import ThemedTestCase

class TestMigration(ThemedTestCase):
    def test_widget_theming(self):
        widget = YourMigratedWidget()

        # Test dark theme
        self.apply_test_theme("dark")
        self.assertTrue(widget.is_dark_theme)

        # Test light theme
        self.apply_test_theme("light")
        self.assertFalse(widget.is_dark_theme)

        # Test that widget updates
        # Add your specific assertions here
```

## Troubleshooting Common Issues

### Issue: Widget Doesn't Update with Theme

**Problem:** Widget appearance doesn't change when switching themes.

**Solution:**
```python
class MyWidget(ThemedWidget):  # ✅ Must inherit ThemedWidget
    def on_theme_changed(self):
        # ✅ Must override this if doing custom painting
        self.update()  # Trigger repaint
```

### Issue: Hardcoded Colors Still Showing

**Problem:** Some colors don't change with theme.

**Solution:**
```python
# ❌ WRONG - Hardcoded color
self.setStyleSheet("background: #ffffff")

# ✅ RIGHT - Use theme config
class MyWidget(ThemedWidget):
    theme_config = {'bg': 'window.background'}

    def on_theme_changed(self):
        self.setStyleSheet(f"background: {self.theme.bg}")
```

### Issue: Child Widgets Not Themed

**Problem:** Child widgets don't get themed.

**Solution:**
```python
class ParentWidget(ThemedWidget):
    def __init__(self):
        super().__init__()  # ✅ MUST call super().__init__()

        # Now child widgets are automatically themed
        self.button = QPushButton("Click", self)
        self.editor = QTextEdit(self)
```

## Migration Benefits

After migrating to ThemedWidget, you automatically get:

1. **Memory Safety** - WeakRef registry prevents memory leaks
2. **Thread Safety** - Qt signals handle cross-thread updates
3. **Error Recovery** - Graceful fallback to minimal theme
4. **Clean Architecture** - Dependency injection built-in
5. **Automatic Cleanup** - Proper lifecycle management
6. **Child Widget Theming** - Children automatically themed
7. **VSCode Theme Support** - Import any VSCode theme
8. **Theme Switching** - Runtime theme changes
9. **Testing Support** - MockThemeProvider for unit tests
10. **Future Proof** - Clean architecture ensures maintainability

## Performance Tips

1. **Use theme_config** - Declare properties once, access many times
2. **Batch Updates** - Update multiple properties in `on_theme_changed()`
3. **Avoid Frequent Lookups** - Cache theme properties locally if needed
4. **Lazy Loading** - ThemedWidget uses lazy loading automatically

## Next Steps After Migration

1. **Add Theme Switching**
   ```python
   combo = QComboBox()
   combo.addItems(["dark-modern", "light-default"])
   combo.currentTextChanged.connect(app.set_theme)
   ```

2. **Import VSCode Themes**
   ```python
   app.import_vscode_theme("monokai.json")
   app.set_theme("Monokai")
   ```

3. **Create Custom Themes**
   ```json
   {
     "name": "My Theme",
     "type": "dark",
     "colors": {
       "window.background": "#1a1a1a",
       "window.foreground": "#ffffff"
     }
   }
   ```

## Summary

Migration is simple:
1. **Inherit from ThemedWidget** instead of QWidget
2. **Add theme_config** for custom colors
3. **Override on_theme_changed()** if needed

ThemedWidget handles all the complexity - you just focus on your widget logic!

---

*For more patterns, see the [Patterns Cookbook](patterns-cookbook.md) and [API Reference](api-REFERENCE.md).*