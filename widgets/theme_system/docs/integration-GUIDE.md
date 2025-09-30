# Widget Integration Guide - VFWidgets Theme System

## The Right Way: Use ThemedWidget

```python
from vfwidgets_theme import ThemedWidget

class YourWidget(ThemedWidget):
    pass  # ✅ Done! Everything handled correctly!
```

That's it. Your widget now has:
- ✅ **Proper theming** with automatic updates
- ✅ **Memory safety** with automatic cleanup
- ✅ **Thread safety** built in
- ✅ **Clean architecture** hidden inside
- ✅ **Testability** through dependency injection

## 🎯 Quick Decision Guide - What Do You Need?

```
START HERE → What does your widget need?
│
├─ Just standard Qt widgets?
│  └─ ✅ You're done! ThemedWidget handles everything
│
├─ Custom theme colors?
│  └─ ✅ Add theme_config dictionary
│
├─ React to theme changes?
│  └─ ✅ Override on_theme_changed()
│
└─ Full control?
   └─ ✅ Access the clean architecture underneath
```

## The ThemedWidget Approach

```python
# Step 1: Basic Widget (90% of cases)
class MyLabel(ThemedWidget):
    pass  # Automatically themed!

# Step 2: Custom Colors (when needed)
class MyButton(ThemedWidget):
    theme_config = {
        'accent': 'button.accent',
        'glow': 'button.glow'
    }

    def paintEvent(self, event):
        color = self.theme.accent  # Type-safe access!

# Step 3: Dynamic Behavior (when needed)
class MyEditor(ThemedWidget):
    def on_theme_changed(self):
        """Called when theme changes"""
        self.update_syntax_colors()
```

**That's it!** Your widget now:
- ✅ Automatically applies current theme
- ✅ Updates when theme changes
- ✅ Inherits appropriate colors based on widget type
- ✅ Supports all theme features

## 🎨 What Happens Automatically?

When you inherit from `VFWidget`, the theme system automatically:

### Automatic Widget Recognition

| Your Widget Class Name | Automatically Gets These Theme Properties | Example |
|------------------------|-------------------------------------------|---------|
| `*Button`, `*Btn` | `button.background`, `button.foreground`, `button.hoverBackground`, `button.activeBackground`, `button.disabledBackground` | `MyButton`, `SubmitBtn` |
| `*Editor` | `editor.background`, `editor.foreground`, `editor.selectionBackground`, `editor.lineHighlightBackground` | `CodeEditor`, `TextEditor` |
| `*Terminal` | `terminal.background`, `terminal.foreground`, all 16 ANSI colors | `Terminal`, `ConsoleTerminal` |
| `*StatusBar` | `statusBar.background`, `statusBar.foreground`, `statusBar.border` | `StatusBar`, `MyStatusBar` |
| `*TabWidget`, `*Tabs` | `tabs.background`, `tabs.activeBackground`, `tabs.border` | `TabWidget`, `ChromeTabs` |
| `*List`, `*Tree` | `list.background`, `list.selectedBackground`, `list.hoverBackground` | `FileList`, `TreeView` |
| `*Input`, `*Field` | `input.background`, `input.foreground`, `input.border`, `input.focusBorder` | `SearchInput`, `TextField` |
| `*Menu` | `menu.background`, `menu.foreground`, `menu.selectedBackground` | `ContextMenu`, `MainMenu` |
| `*Bar` (not StatusBar) | `widget.background`, `widget.foreground` | `ToolBar`, `NavBar` |
| Any other name | `window.background`, `window.foreground` (fallback) | `MyWidget`, `CustomView` |

### Child Widget Behavior

**IMPORTANT:** Child Qt widgets inside your VFWidget are automatically themed!

```python
class MyPanel(VFWidget):  # Inherits from VFWidget
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # These child widgets are AUTOMATICALLY themed:
        self.button = QPushButton("Click")      # Gets button.* colors
        self.editor = QTextEdit()               # Gets editor.* colors
        self.input = QLineEdit()                # Gets input.* colors
        self.list = QListWidget()               # Gets list.* colors

        layout.addWidget(self.button)
        layout.addWidget(self.editor)
        # No theme code needed - it just works!
```

## Do I Need to Do Anything Else?

### ✅ No Additional Code Needed If:
- You only use standard Qt widgets (QLabel, QPushButton, QTextEdit, etc.)
- You don't use hardcoded colors in stylesheets
- You don't have custom `paintEvent` drawing
- Your widget name follows the patterns above

### ⚠️ You Need Custom Code If:
- You hardcode colors → Replace with theme properties (Level 1)
- You have custom painting → Use `theme_color()` in paintEvent (Level 1)
- You need specific theme properties → Declare with `theme_property` (Level 1)
- You have complex multi-component layouts → Use ThemeMapping (Level 2)
- You need to update when theme changes → Use `@on_theme_change` (Level 3)

## Integration Levels

### Level 0: Zero-Configuration (Automatic)

Just inherit from `VFWidget` and theming happens automatically:

```python
from vfwidgets_theme import VFWidget

class StatusBar(VFWidget):
    def __init__(self):
        super().__init__()
        # Widget automatically themed based on class name
        # "StatusBar" → uses statusBar.* theme properties
```

**Automatic Property Detection:**
- `*Button` classes get button theme properties
- `*Editor` classes get editor theme properties
- `*Terminal` classes get terminal theme properties
- Standard Qt widgets get appropriate defaults

### Level 1: Declarative Properties (Simple)

Declare specific theme properties your widget needs:

```python
from vfwidgets_theme import VFWidget, theme_property

class CustomButton(VFWidget):
    # Declare theme properties as class attributes
    background = theme_property("button.background")
    hover_bg = theme_property("button.hoverBackground")
    text_color = theme_property("button.foreground")

    def paintEvent(self, event):
        painter = QPainter(self)
        # Properties are automatically available
        painter.fillRect(self.rect(), QColor(self.background))
        painter.setPen(QColor(self.text_color))
```

**Alternative syntax with Theme inner class:**

```python
class Terminal(VFWidget):
    class Theme:
        """Group all theme properties together"""
        background = "terminal.background"
        foreground = "terminal.foreground"
        cursor = "terminal.cursorColor"
        selection = "terminal.selectionBackground"

    def __init__(self):
        super().__init__()
        # Access: self.theme.background, self.theme.foreground
        self.setStyleSheet(f"""
            Terminal {{
                background-color: {self.theme.background};
                color: {self.theme.foreground};
            }}
        """)
```

### Level 2: Smart Mapping (Complex Widgets)

For widgets with multiple components, use theme mapping:

```python
from vfwidgets_theme import VFWidget, ThemeMapping

class IDEWidget(VFWidget):
    # Map theme properties to Qt selectors
    theme_map = ThemeMapping({
        # Widget parts
        "editor.background": "QTextEdit#editor",
        "sidebar.background": "QListWidget#sidebar",
        "statusBar.background": "QStatusBar",

        # States
        "list.hoverBackground": "QListWidget::item:hover",
        "list.activeSelectionBackground": "QListWidget::item:selected",

        # Nested components
        "button.background": "QPushButton",
        "button.hoverBackground": "QPushButton:hover",
    })

    def __init__(self):
        super().__init__()
        # QSS automatically generated from theme_map
        # Updates when theme changes
```

### Level 3: Dynamic Responses (Advanced)

React to theme changes programmatically:

```python
from vfwidgets_theme import VFWidget, on_theme_change

class SyntaxHighlighter(VFWidget):

    @on_theme_change
    def update_all_colors(self, theme):
        """Called when theme changes"""
        self.keyword_color = theme.get_token_color("keyword")
        self.string_color = theme.get_token_color("string")
        self.comment_color = theme.get_token_color("comment")
        self.rehighlight_document()

    @on_theme_change("editor.fontSize")
    def update_font_size(self, new_size):
        """Called only when specific property changes"""
        font = self.font()
        font.setPointSize(new_size)
        self.setFont(font)

    @on_theme_change.debounce(100)  # Debounce rapid changes
    def expensive_update(self, theme):
        """Called max once per 100ms during rapid theme changes"""
        self.rebuild_entire_view()
```

## 📚 Common Widget Recipes

### Recipe: "I'm Making a Custom Button"
```python
class MyCustomButton(VFWidget):  # Just inherit VFWidget
    # That's it for basic theming!

    # Only if you need hover effects:
    hover_bg = theme_property("button.hoverBackground")

    def enterEvent(self, event):
        self.setStyleSheet(f"background: {self.hover_bg}")
```

### Recipe: "I'm Making a Code Editor"
```python
class CodeEditor(VFWidget):  # Name ends with "Editor" = auto editor colors!
    # Automatically gets editor.background, editor.foreground, etc.

    # Only if you need syntax colors:
    @on_theme_change
    def update_syntax(self, theme):
        self.keyword_color = theme.get_token_color("keyword")
```

### Recipe: "I'm Making a Custom-Painted Widget"
```python
class MyCanvas(VFWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        # Use theme colors for painting:
        bg = self.theme_color("widget.background")
        fg = self.theme_color("widget.foreground")
        painter.fillRect(self.rect(), QColor(bg))
        painter.setPen(QColor(fg))
```

### Recipe: "I Have a Widget with Multiple Parts"
```python
class MyComplexWidget(VFWidget):
    theme_map = ThemeMapping({
        "editor.background": "QTextEdit",
        "sidebar.background": "#sidebar",
        "button.background": "QPushButton"
    })
    # Each part gets its own theme colors!
```

## Common Widget Patterns

### Pattern 1: Simple Label/Display Widget

```python
class InfoLabel(VFWidget):
    """Minimal theme integration"""
    pass  # Automatically themed!
```

### Pattern 2: Button with States

```python
class ModernButton(VFWidget):
    # Declare state-based properties
    normal = theme_property("button.background")
    hover = theme_property("button.hoverBackground")
    pressed = theme_property("button.activeBackground")
    disabled = theme_property("button.disabledBackground")

    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self._state = "normal"

    def enterEvent(self, event):
        self._state = "hover"
        self.update_style()

    def leaveEvent(self, event):
        self._state = "normal"
        self.update_style()

    def update_style(self):
        color = getattr(self, self._state)
        self.setStyleSheet(f"background-color: {color};")
```

### Pattern 3: Context-Aware Widget

```python
class SmartButton(VFWidget):
    # Context-aware property resolution
    background = theme_property("button.background", context_aware=True)

    def __init__(self):
        super().__init__()
        self.theme_context = "normal"  # normal, danger, success, warning

    def set_danger(self):
        self.theme_context = "danger"
        # Now uses danger.button.background if available
        # Falls back to danger.background then button.background
```

### Pattern 4: Custom Drawing Widget

```python
class Canvas(VFWidget):
    # Theme colors for custom painting
    grid_color = theme_property("canvas.gridColor", default="#333333")
    background = theme_property("canvas.background", default="#1e1e1e")

    def paintEvent(self, event):
        painter = QPainter(self)

        # Use theme colors in painting
        painter.fillRect(self.rect(), QColor(self.background))

        # Draw grid
        painter.setPen(QColor(self.grid_color))
        for x in range(0, self.width(), 20):
            painter.drawLine(x, 0, x, self.height())
```

### Pattern 5: Composite Widget

```python
class SearchBar(VFWidget):
    # Different theme properties for sub-components
    class Theme:
        input_bg = "input.background"
        input_fg = "input.foreground"
        button_bg = "button.background"
        icon_color = "icon.foreground"

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.apply_component_themes()

    def apply_component_themes(self):
        self.search_input.setStyleSheet(f"""
            background: {self.theme.input_bg};
            color: {self.theme.input_fg};
        """)
        self.search_button.setStyleSheet(f"""
            background: {self.theme.button_bg};
        """)
```

## Computed Properties

For dynamic theme values based on other properties:

```python
from vfwidgets_theme import VFWidget, computed_property

class FancyWidget(VFWidget):

    @computed_property
    def gradient_background(self):
        """Generate gradient from theme colors"""
        start = self.get_theme_color("gradient.start")
        end = self.get_theme_color("gradient.end")
        return f"qlineargradient(x1:0, y1:0, x2:1, y2:1, " \
               f"stop:0 {start}, stop:1 {end})"

    @computed_property
    def adjusted_border(self):
        """Compute border based on background luminance"""
        bg = self.get_theme_color("window.background")
        if is_dark_color(bg):
            return lighten(bg, 20)
        else:
            return darken(bg, 20)
```

## Helper Methods

Every `VFWidget` has these helper methods:

```python
class MyWidget(VFWidget):
    def example_usage(self):
        # Get any theme color
        color = self.theme_color("editor.background")

        # Get with default fallback
        border = self.theme_color("border", default="#333")

        # Check theme type
        if self.theme_type == "dark":
            # Do something for dark themes
            pass

        # Get current theme object
        theme = self.current_theme

        # Force theme refresh
        self.refresh_theme()

        # Temporarily override theme
        with self.theme_override({"button.background": "#ff0000"}):
            # Temporary red background
            pass
```

## Testing Your Integration

```python
from vfwidgets_theme.testing import ThemeTestCase

class TestMyWidget(ThemeTestCase):
    def test_theme_integration(self):
        widget = MyWidget()

        # Test with different themes
        self.apply_test_theme("dark")
        assert widget.theme_color("background") == "#1e1e1e"

        self.apply_test_theme("light")
        assert widget.theme_color("background") == "#ffffff"

    def test_theme_switching(self):
        widget = MyWidget()

        # Ensure theme switches properly
        self.assert_theme_switches_cleanly(widget, "dark", "light")

    def test_custom_properties(self):
        widget = MyCustomWidget()

        # Verify custom properties work
        self.assert_has_property(widget, "myCustomColor")
        self.assert_property_updates(widget, "myCustomColor", "#ff0000")
```

## TypeScript-Style Type Safety

```python
from typing import TypedDict
from vfwidgets_theme import VFWidget, typed_theme

class TerminalColors(TypedDict):
    background: str
    foreground: str
    black: str
    red: str
    green: str
    yellow: str
    blue: str
    magenta: str
    cyan: str
    white: str

@typed_theme(TerminalColors)
class Terminal(VFWidget):
    def __init__(self):
        super().__init__()
        # IDE knows all available colors
        # Type checker validates usage
```

## Migration Checklist

Migrating existing widgets to use themes:

- [ ] Change base class from `QWidget` to `VFWidget`
- [ ] Replace hardcoded colors with theme properties
- [ ] Remove inline style sheets with colors
- [ ] Add theme property declarations
- [ ] Test with light and dark themes
- [ ] Document custom theme properties

## Performance Tips

### 1. Cache Computed Values

```python
class MyWidget(VFWidget):
    def __init__(self):
        super().__init__()
        self._gradient_cache = None

    @on_theme_change
    def invalidate_cache(self, theme):
        self._gradient_cache = None

    @property
    def gradient(self):
        if self._gradient_cache is None:
            self._gradient_cache = self.compute_gradient()
        return self._gradient_cache
```

### 2. Batch Updates

```python
class MultiComponentWidget(VFWidget):
    @on_theme_change
    def update_all_components(self, theme):
        # Batch updates to avoid multiple repaints
        self.setUpdatesEnabled(False)
        try:
            self.update_component_a()
            self.update_component_b()
            self.update_component_c()
        finally:
            self.setUpdatesEnabled(True)
```

### 3. Use Selective Updates

```python
class OptimizedWidget(VFWidget):
    @on_theme_change("editor.background")
    def update_background_only(self, color):
        # Only update when specific property changes
        self.setStyleSheet(f"background: {color};")

    @on_theme_change(["editor.foreground", "editor.fontSize"])
    def update_text_properties(self, theme):
        # Update only when text-related properties change
        pass
```

## Troubleshooting

### Widget Not Themed?

1. Ensure inheriting from `VFWidget` not `QWidget`
2. Check theme manager is initialized
3. Verify theme has required properties
4. Look for hardcoded styles overriding theme

### Theme Not Updating?

1. Check widget is registered with theme manager
2. Ensure not blocking theme change events
3. Verify no cached styles preventing updates
4. Check for style sheet conflicts

### Performance Issues?

1. Use property-specific listeners vs global
2. Cache computed properties
3. Batch multiple updates
4. Profile theme application with `ThemeProfiler`

## Best Practices Summary

### DO ✅
- Inherit from `VFWidget` for automatic theming
- Use semantic property names
- Cache expensive computations
- Test with multiple themes
- Document custom properties

### DON'T ❌
- Hardcode colors
- Mix themed and non-themed styles
- Ignore theme change events
- Assume theme type (dark/light)
- Override user theme preferences

## Next Steps

1. Review [API Reference](api-REFERENCE.md) for all available methods
2. See [Best Practices Guide](best-practices-GUIDE.md) for advanced patterns
3. Check [Example Themes](examples/) for real-world usage
4. Read [Migration Guide](migration-GUIDE.md) for existing projects

---

*Remember: The theme system is designed to be progressive. Start simple and add complexity only when needed!*