# API Reference - VFWidgets Theme System

## Primary Classes (What You Use)

### `ThemedWidget`

The main base class for creating themed widgets. Handles all complexity internally.

```python
class ThemedWidget(metaclass=ThemedWidgetMeta):
    """
    Mixin for themed widgets - use with multiple inheritance.

    What you see: Simple mixin class
    What it does: Clean architecture with dependency injection,
                  memory management, and thread safety
    """
```

#### Simple Usage

```python
from vfwidgets_theme import ThemedWidget
from PySide6.QtWidgets import QWidget

class YourWidget(ThemedWidget, QWidget):
    pass  # ✅ Fully themed with clean architecture
```

**Note**: For single inheritance, use `ThemedQWidget` instead (recommended).

#### Configuration

```python
class YourWidget(ThemedWidget):
    # Declare theme properties you need
    theme_config = {
        'background': 'editor.background',
        'accent': 'button.accent',
        'border': 'panel.border'
    }

    def paintEvent(self, event):
        # Access theme properties
        bg_color = self.theme.background
        accent = self.theme.accent
```

#### Methods

##### `on_theme_changed()`
Override to react to theme changes.

```python
class YourWidget(ThemedWidget, QWidget):
    def on_theme_changed(self):
        """Called when theme changes - override to update your widget"""
        self.update()  # Trigger repaint
        self.update_syntax_colors()  # Custom updates
```

#### Properties

- `theme` - Dynamic property accessor for configured theme properties (returns ThemePropertyProxy with smart defaults)

---

### `ThemedQWidget` (New - Recommended)

Convenience class that combines ThemedWidget with QWidget inheritance.

```python
from vfwidgets_theme import ThemedQWidget

class MyWidget(ThemedQWidget):  # Single inheritance - simpler!
    theme_config = {
        'bg': 'colors.background',
        'fg': 'colors.foreground'
    }

    def __init__(self):
        super().__init__()
        # Widget has full theming + QWidget functionality
```

**Benefits over ThemedWidget:**
- Single inheritance (simpler to understand)
- No inheritance order concerns
- Clearer intent

---

### `ThemedMainWindow` (New - Recommended)

Convenience class for themed main windows.

```python
from vfwidgets_theme import ThemedMainWindow

class MyWindow(ThemedMainWindow):  # Single inheritance!
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")
        # Full QMainWindow + theming functionality
```

---

### `ThemedDialog` (New - Recommended)

Convenience class for themed dialogs.

```python
from vfwidgets_theme import ThemedDialog

class MyDialog(ThemedDialog):  # Single inheritance!
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
        # Full QDialog + theming functionality
```

---

### Property Access with Smart Defaults

Theme properties now have intelligent defaults:

```python
# Old way (still works)
bg = getattr(self.theme, 'background', '#ffffff')

# New way (recommended)
bg = self.theme.background  # Automatic smart default if not in theme
```

**Smart defaults provided for:**
- Colors (background, foreground, accent, error, warning, success, info)
- Fonts (font, font_family, font_size)
- Dimensions (padding, margin, border, spacing)
- Opacity (opacity, alpha)

---

### `ThemedApplication`

Application wrapper that sets up theming for your entire app.

```python
class ThemedApplication(QApplication):
    """
    Qt Application with built-in theme support.

    Automatically initializes theme system with clean architecture.
    """
```

#### Usage

```python
from vfwidgets_theme import ThemedApplication
import sys

app = ThemedApplication(sys.argv)
app.set_theme("dark-modern")  # or "light-default"

window = YourWidget()
window.show()

app.exec()
```

#### Methods

##### `set_theme(name: str)`
Set the application theme.

```python
app.set_theme("dark-modern")
# Built-in themes: "dark-modern", "light-default", "high-contrast"
```

##### `load_theme_file(path: str | Path)`
Load a custom theme from file.

```python
app.load_theme_file("my-custom-theme.json")
```

##### `import_vscode_theme(path: str | Path) -> bool`
Import a VSCode theme.

```python
success = app.import_vscode_theme("monokai.json")
if success:
    app.set_theme("Monokai")
```

#### Properties

- `current_theme_name: str` - Name of current theme
- `available_themes: List[str]` - List of available theme names
- `theme_type: str` - Current theme type ("dark" or "light")

#### Signals

- `theme_changed` - Emitted when theme changes

```python
app.theme_changed.connect(lambda: print("Theme changed!"))
```

---

## Advanced Classes (Internal Architecture)

> **Note**: These classes are part of the internal clean architecture. You typically don't need to use them directly - ThemedWidget and ThemedApplication handle everything.

### `Theme`

Theme data structure (you receive this in callbacks).

```python
@dataclass
class Theme:
    """Immutable theme data."""
    name: str
    type: Literal["dark", "light"]
    colors: Dict[str, str]
    # ... other properties
```

### `ThemeProvider` (Protocol)

Interface for theme provision - enables testing and dependency injection.

```python
class ThemeProvider(Protocol):
    """Interface that ThemedWidget uses internally."""
    def get_current_theme(self) -> Theme: ...
    def get_property(self, key: str) -> Any: ...
```

---

---

## Common Patterns

### Basic Themed Widget

```python
from vfwidgets_theme import ThemedQWidget

class MyLabel(ThemedQWidget):
    """Automatically themed label - no config needed!"""
    pass
```

### Widget with Custom Colors

```python
from vfwidgets_theme import ThemedWidget
from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QPainter, QColor
from PySide6.QtCore import Qt

class MyButton(ThemedWidget, QPushButton):
    theme_config = {
        'bg': 'button.background',
        'hover': 'button.hoverBackground',
        'text': 'button.foreground'
    }

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(self.theme.bg))
        painter.setPen(QColor(self.theme.text))
        painter.drawText(self.rect(), Qt.AlignCenter, self.text())
```

### Widget with Theme Reaction

```python
from vfwidgets_theme import ThemedWidget
from PySide6.QtWidgets import QTextEdit

class CodeEditor(ThemedWidget, QTextEdit):
    theme_config = {
        'bg': 'editor.background',
        'fg': 'editor.foreground',
        'selection': 'editor.selectionBackground'
    }

    def on_theme_changed(self):
        # Update syntax highlighter with new colors
        if hasattr(self, 'highlighter'):
            self.highlighter.update_colors()
        # Refresh display
        self.update()
```

### Complex Widget with Progressive Enhancement

```python
from vfwidgets_theme import ThemedQWidget
from PySide6.QtWidgets import QLabel, QVBoxLayout

class AdvancedPanel(ThemedQWidget):
    theme_config = {
        'panel_bg': 'panel.background',
        'panel_border': 'panel.border',
        'title_bg': 'titleBar.background',
        'title_fg': 'titleBar.foreground'
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.title_label = QLabel("Title")
        self.content_area = QLabel("Content")
        layout.addWidget(self.title_label)
        layout.addWidget(self.content_area)

    def on_theme_changed(self):
        # Apply theme to child widgets
        self.title_label.setStyleSheet(f"""
            background-color: {self.theme.title_bg};
            color: {self.theme.title_fg};
        """)
        self.content_area.setStyleSheet(f"""
            background-color: {self.theme.panel_bg};
            border: 1px solid {self.theme.panel_border};
        """)
```

---

## Testing Support

### Testing Themed Widgets

```python
from vfwidgets_theme.testing import ThemedTestCase

class TestMyWidget(ThemedTestCase):
    def test_dark_theme(self):
        widget = MyWidget()
        self.apply_test_theme("dark")

        # Widget automatically updates
        self.assertEqual(widget.theme_type, "dark")
        self.assertTrue(widget.is_dark_theme)

    def test_theme_switching(self):
        widget = MyWidget()

        self.apply_test_theme("light")
        light_bg = widget.theme.background

        self.apply_test_theme("dark")
        dark_bg = widget.theme.background

        self.assertNotEqual(light_bg, dark_bg)
```

### Mock Theme Provider

```python
from vfwidgets_theme.testing import MockThemeProvider

def test_widget_isolation():
    # Create widget with mock theme provider
    mock_provider = MockThemeProvider({
        "button.background": "#ff0000",
        "button.foreground": "#ffffff"
    })

    widget = MyButton()
    widget._theme_provider = mock_provider  # Inject mock

    assert widget.theme.bg == "#ff0000"
```

---

## Configuration

### Application-Level Configuration

```python
from vfwidgets_theme import ThemedApplication

app = ThemedApplication(sys.argv, config={
    'auto_detect_system': True,      # Follow system dark/light mode
    'fallback_theme': 'light-default',  # Fallback if theme fails
    'validate_themes': True,         # Validate theme files on load
    'cache_themes': True,            # Cache processed themes
    'theme_directory': '~/.themes'   # Custom theme directory
})
```

### Per-Widget Configuration

```python
class CustomWidget(ThemedWidget):
    theme_config = {
        # Property mappings
        'bg': 'editor.background',

        # Configuration options
        '_options': {
            'inherit_parent_theme': True,  # Inherit from parent widget
            'cache_properties': True,       # Cache property lookups
            'auto_refresh': True           # Auto-refresh on theme change
        }
    }
```

---

## Error Handling

The theme system uses graceful degradation - your app never crashes due to theme issues.

```python
class RobustWidget(ThemedWidget):
    theme_config = {
        'primary': 'custom.primary',
        'secondary': 'custom.secondary'
    }

    def paintEvent(self, event):
        # Always returns a valid color, even if theme property missing
        primary = self.get_theme_color('custom.primary',
                                       default='#0066cc')

        # Graceful fallback chain:
        # 1. Try custom.primary from current theme
        # 2. Try parent theme if current extends another
        # 3. Use default color
        # 4. Use system fallback (never fails)
```

---

## Migration Guide

### From Direct ThemeManager Usage

```python
# Old way (direct singleton access)
from vfwidgets_theme import ThemeManager

class OldWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.tm = ThemeManager.instance()
        self.tm.register_widget(self)

    def get_color(self):
        return self.tm.get_property("button.background")

# New way (clean architecture)
from vfwidgets_theme import ThemedWidget

class NewWidget(ThemedWidget):
    theme_config = {
        'bg': 'button.background'
    }

    def get_color(self):
        return self.theme.bg  # So much simpler!
```

### From Manual Theme Management

```python
# Old way (manual everything)
class OldButton(QPushButton):
    def __init__(self):
        super().__init__()
        self.apply_theme()
        theme_manager.theme_changed.connect(self.apply_theme)

    def apply_theme(self):
        theme = theme_manager.current_theme
        self.setStyleSheet(f"""
            background: {theme.colors.get('button.background')};
            color: {theme.colors.get('button.foreground')};
        """)

# New way (automatic)
class NewButton(ThemedWidget, QPushButton):
    theme_config = {
        'bg': 'button.background',
        'fg': 'button.foreground'
    }

    def on_theme_changed(self):
        self.setStyleSheet(f"""
            background: {self.theme.bg};
            color: {self.theme.fg};
        """)
```

---

## FAQ

### Q: Do I need to understand the internal architecture?
**A**: No! Just inherit from `ThemedWidget` and optionally add `theme_config`. The clean architecture is there but hidden.

### Q: Will this slow down my app?
**A**: No. The theme system uses:
- Lazy loading
- Multi-level caching
- Batch updates
- WeakRef for memory efficiency

### Q: What if a theme file is corrupted?
**A**: The system automatically falls back to a minimal built-in theme. Your app keeps running.

### Q: Can I test widgets in isolation?
**A**: Yes! The clean architecture with dependency injection makes testing easy. Use `MockThemeProvider` for unit tests.

### Q: Is it thread-safe?
**A**: Yes! The system uses Qt signals/slots for thread-safe theme updates.

---

*For more examples, see the [Quick Start Guide](quick-start-GUIDE.md) and the examples directory.*