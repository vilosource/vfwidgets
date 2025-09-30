# API Reference - VFWidgets Theme System

## Primary Classes (What You Use)

### `ThemedWidget`

The main base class for creating themed widgets. Handles all complexity internally.

```python
class ThemedWidget(QWidget):
    """
    Simple inheritance for themed widgets.

    What you see: Simple base class
    What it does: Clean architecture with dependency injection,
                  memory management, and thread safety
    """
```

#### Simple Usage

```python
from vfwidgets_theme import ThemedWidget

class YourWidget(ThemedWidget):
    pass  # ✅ That's it! Fully themed with clean architecture
```

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
class YourWidget(ThemedWidget):
    def on_theme_changed(self):
        """Called when theme changes - override to update your widget"""
        self.update()  # Trigger repaint
        self.update_syntax_colors()  # Custom updates
```

##### `get_theme_color(key: str, default: str = None) -> str`
Get a color from the current theme.

```python
color = self.get_theme_color("button.background", default="#0066cc")
```

##### `get_theme_property(key: str, default: Any = None) -> Any`
Get any theme property.

```python
font_size = self.get_theme_property("editor.fontSize", default=12)
```

#### Properties

- `theme` - Dynamic property accessor for configured theme properties
- `theme_type: str` - Current theme type ("dark" or "light")
- `is_dark_theme: bool` - Convenience property for dark theme detection

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

##### `import_vscode_theme(path: str | Path)`
Import a VSCode theme.

```python
app.import_vscode_theme("monokai.json")
```

##### `toggle_dark_mode()`
Toggle between dark and light themes.

```python
app.toggle_dark_mode()
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

## Decorators

### `@theme_property`

Create computed theme properties.

```python
class MyWidget(ThemedWidget):
    theme_config = {
        'start': 'gradient.start',
        'end': 'gradient.end'
    }

    @theme_property
    def gradient_background(self) -> str:
        return f"linear-gradient({self.theme.start}, {self.theme.end})"
```

---

## Utility Functions

### Color Utilities

```python
from vfwidgets_theme.utils import lighten, darken, ensure_contrast

# Lighten/darken colors
lighter = lighten("#000000", 20)  # Returns "#333333"
darker = darken("#ffffff", 20)    # Returns "#cccccc"

# Ensure readable text
text_color = ensure_contrast(text_color, bg_color, min_ratio=4.5)
```

### Theme Detection

```python
from vfwidgets_theme.utils import is_dark_color, detect_system_theme

# Check if color is dark
if is_dark_color(bg_color):
    use_light_text()

# Detect system theme
if detect_system_theme() == "dark":
    app.set_theme("dark-modern")
```

---

## Common Patterns

### Basic Themed Widget

```python
class MyLabel(ThemedWidget):
    """Automatically themed label - no config needed!"""
    pass
```

### Widget with Custom Colors

```python
class MyButton(ThemedWidget):
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
class CodeEditor(ThemedWidget):
    theme_config = {
        'bg': 'editor.background',
        'fg': 'editor.foreground',
        'selection': 'editor.selectionBackground'
    }

    def on_theme_changed(self):
        # Update syntax highlighter
        self.highlighter.set_theme_colors(self.get_current_theme())
        # Update editor palette
        self.update_palette()
        # Refresh display
        self.update()
```

### Complex Widget with Progressive Enhancement

```python
class AdvancedPanel(ThemedWidget):
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
        # UI setup code
        pass

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

*For more examples, see the [Integration Guide](integration-GUIDE.md) and [Patterns Cookbook](patterns-cookbook.md).*