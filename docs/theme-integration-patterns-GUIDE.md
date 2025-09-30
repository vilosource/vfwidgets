# Theme Integration Patterns for Widget Developers

## Philosophy: "It Just Works"

Our theme system follows a **progressive enhancement** model:
1. **Zero effort** = automatic basic theming
2. **Minimal effort** = customized theming
3. **Full control** = advanced theming

## Integration Levels

### Level 0: Automatic Theming (Zero Code)
**Just inherit from VFWidget base class - theming happens automatically!**

```python
from vfwidgets.core import VFWidget

class MyButton(VFWidget):
    def __init__(self):
        super().__init__()
        # That's it! Your widget is now themed
        # The theme system automatically detects widget type and applies appropriate styles
```

**How it works:**
- VFWidget base class handles all theme integration
- Automatic property detection based on Qt widget type
- Intelligent defaults based on widget hierarchy
- Theme changes automatically propagate

### Level 1: Declarative Theme Properties (1-5 lines)

**Declare what theme properties you need using simple decorators:**

```python
from vfwidgets.core import VFWidget, theme_property

class MyCustomButton(VFWidget):
    # Declare theme properties with semantic names
    background = theme_property("button.background")
    hover_background = theme_property("button.hoverBackground")
    text_color = theme_property("button.foreground")

    def __init__(self):
        super().__init__()
        # Properties are automatically applied and updated on theme change
```

**Or use class-level declaration:**

```python
class MyTerminal(VFWidget):
    class Theme:
        background = "terminal.background"
        foreground = "terminal.foreground"
        cursor = "terminal.cursor"
        selection = "terminal.selection"

    def __init__(self):
        super().__init__()
        # Access: self.theme.background, self.theme.foreground, etc.
```

### Level 2: Smart Theme Mapping (For Complex Widgets)

**Use theme mapping for widgets with multiple styled components:**

```python
from vfwidgets.core import VFWidget, ThemeMapping

class ChromeTabbedWindow(VFWidget):
    theme_map = ThemeMapping({
        # Map semantic names to widget selectors
        "tabs.background": "QTabBar",
        "tabs.activeBackground": "QTabBar::tab:selected",
        "tabs.hoverBackground": "QTabBar::tab:hover",
        "tabs.border": "QTabBar::tab { border }",

        # Nested components
        "editor.background": ".editor-widget",
        "statusBar.background": "QStatusBar",
    })

    def __init__(self):
        super().__init__()
        # Theme automatically generates and applies QSS
```

### Level 3: Dynamic Theme Responses

**For widgets that need to respond to theme changes programmatically:**

```python
from vfwidgets.core import VFWidget, on_theme_change

class SyntaxHighlighter(VFWidget):

    @on_theme_change
    def update_syntax_colors(self, theme):
        """Called automatically when theme changes"""
        # Access the full theme object
        self.keyword_color = theme.get_token_color("keyword")
        self.comment_color = theme.get_token_color("comment")
        self.refresh_highlighting()

    @on_theme_change("editor.fontSize")
    def update_font_size(self, new_size):
        """Called only when specific property changes"""
        self.set_font_size(new_size)
```

## Best Patterns for Widget Implementers

### 1. Use Semantic Property Names

```python
# GOOD - Semantic, reusable across themes
class MyWidget(VFWidget):
    bg = theme_property("editor.background")
    fg = theme_property("editor.foreground")
    accent = theme_property("accent.primary")

# BAD - Hardcoded colors
class MyWidget(VFWidget):
    def __init__(self):
        self.setStyleSheet("background: #1e1e1e")
```

### 2. Leverage Property Inheritance

```python
class CodeEditor(VFWidget):
    class Theme:
        # Inherits all editor.* properties automatically
        inherit = "editor"
        # Add custom properties
        line_numbers = "editorLineNumber.foreground"
```

### 3. Use Context-Aware Properties

```python
class SmartButton(VFWidget):
    # Automatically adjusts based on context
    background = theme_property("button.background",
                               context_aware=True)

    def set_danger(self):
        self.theme_context = "danger"  # Now uses danger.background

    def set_success(self):
        self.theme_context = "success"  # Now uses success.background
```

### 4. Computed Properties for Complex Styling

```python
from vfwidgets.core import VFWidget, computed_theme_property

class FancyWidget(VFWidget):

    @computed_theme_property
    def gradient_background(self, theme):
        """Generate gradient from theme colors"""
        start = theme.get("widget.gradientStart")
        end = theme.get("widget.gradientEnd")
        return f"linear-gradient({start}, {end})"
```

## Type-Safe Theme Integration

**Use TypedDict for IDE support and validation:**

```python
from typing import TypedDict
from vfwidgets.core import VFWidget, typed_theme

class TerminalTheme(TypedDict):
    background: str
    foreground: str
    cursor: str
    selection: str
    ansi_black: str
    ansi_red: str
    # ... etc

@typed_theme(TerminalTheme)
class Terminal(VFWidget):
    def __init__(self):
        super().__init__()
        # IDE knows all available theme properties
        # Type checker validates theme usage
```

## Convention-Based Automatic Theming

**Follow naming conventions for automatic theme detection:**

```python
# Widget names are automatically mapped to theme properties
class EditorWidget(VFWidget):  # Gets editor.* properties
    pass

class ButtonWidget(VFWidget):  # Gets button.* properties
    pass

class StatusBarWidget(VFWidget):  # Gets statusBar.* properties
    pass

# Custom prefix override
class MyEditor(VFWidget):
    theme_prefix = "codeEditor"  # Uses codeEditor.* properties
```

## Helper Utilities for Common Patterns

### Quick Theme Access

```python
class MyWidget(VFWidget):
    def paintEvent(self, event):
        # Quick access to theme colors
        painter.setPen(self.theme_color("text"))
        painter.setBrush(self.theme_color("background"))

        # With defaults
        border = self.theme_color("border", default="#333333")
```

### State-Based Theming

```python
class InteractiveWidget(VFWidget):
    def enterEvent(self, event):
        self.apply_theme_state("hover")

    def leaveEvent(self, event):
        self.apply_theme_state("normal")

    def mousePressEvent(self, event):
        self.apply_theme_state("pressed")
```

### Batch Property Updates

```python
class ComplexWidget(VFWidget):
    def setup_theme(self):
        # Apply multiple properties at once
        self.apply_theme_properties({
            "background-color": "window.background",
            "color": "window.foreground",
            "border": "window.border",
            "border-radius": "window.borderRadius"
        })
```

## Testing Your Themed Widget

```python
from vfwidgets.theme.testing import ThemeTestCase

class TestMyWidget(ThemeTestCase):
    def test_theme_application(self):
        widget = MyWidget()

        # Test with different themes
        self.apply_test_theme("dark")
        self.assert_has_style(widget, "background-color", "#1e1e1e")

        self.apply_test_theme("light")
        self.assert_has_style(widget, "background-color", "#ffffff")

    def test_theme_switching(self):
        widget = MyWidget()

        # Verify theme switches properly
        self.switch_theme("dark", "light")
        self.assert_theme_updated(widget)
```

## Migration Guide: Making Existing Widgets Themeable

### Step 1: Change Base Class
```python
# Before
class MyWidget(QWidget):
    pass

# After
from vfwidgets.core import VFWidget
class MyWidget(VFWidget):  # Just change the base class!
    pass
```

### Step 2: Replace Hardcoded Colors (Optional)
```python
# Before
self.setStyleSheet("background: #1e1e1e; color: #ffffff;")

# After
self.apply_theme_properties({
    "background-color": "window.background",
    "color": "window.foreground"
})
```

### Step 3: Add Theme Properties (If Needed)
```python
# Add semantic properties for custom styling
class MyWidget(VFWidget):
    highlight_color = theme_property("accent.primary")
```

## Common Patterns Cookbook

### Pattern 1: Toolbar with Dynamic Icons
```python
class Toolbar(VFWidget):
    @on_theme_change("type")  # React to dark/light change
    def update_icons(self, theme_type):
        icon_set = "dark" if theme_type == "light" else "light"
        self.load_icons(icon_set)
```

### Pattern 2: Syntax Highlighted Editor
```python
class CodeEditor(VFWidget):
    def __init__(self):
        super().__init__()
        # Automatically get token colors from theme
        self.highlighter = ThemeSyntaxHighlighter(self)
```

### Pattern 3: Custom Drawing Widget
```python
class CustomCanvas(VFWidget):
    def paintEvent(self, event):
        painter = ThemePainter(self)  # Theme-aware painter
        painter.draw_background()      # Uses theme colors
        painter.draw_grid("grid.color")
        painter.draw_text("Hello", "text.primary")
```

## DO's and DON'Ts

### DO's ✅
- **DO** inherit from VFWidget for automatic theming
- **DO** use semantic property names (button.background not #0066cc)
- **DO** provide sensible defaults for custom properties
- **DO** test with multiple themes (dark, light, high-contrast)
- **DO** document any custom theme properties

### DON'Ts ❌
- **DON'T** hardcode colors in stylesheets
- **DON'T** assume theme type (dark/light) in logic
- **DON'T** override theme colors without user action
- **DON'T** mix themed and non-themed styling
- **DON'T** ignore theme change events for dynamic content

## Performance Tips

1. **Use property caching:** Theme properties are cached automatically
2. **Batch updates:** Group style changes in theme callbacks
3. **Lazy loading:** Don't compute theme properties until needed
4. **Selective updates:** Use specific property listeners vs global

## IDE Support

### VS Code / PyCharm Integration
```python
# Type hints for autocomplete
from vfwidgets.theme import ThemeProperties

class MyWidget(VFWidget):
    theme: ThemeProperties  # Full autocomplete for theme.editor.background etc.
```

### Theme Property Discovery
```python
# Use the theme explorer
from vfwidgets.theme import explore_theme

# In development, see all available properties
explore_theme()  # Opens interactive theme browser
```

## Examples by Widget Complexity

### Simple Label (Zero Config)
```python
class StatusLabel(VFWidget):
    pass  # Fully themed!
```

### Button with States (Minimal Config)
```python
class ModernButton(VFWidget):
    class Theme:
        normal = "button.background"
        hover = "button.hoverBackground"
        pressed = "button.activeBackground"
```

### Complex Multi-Component Widget
```python
class IDEWidget(VFWidget):
    theme_map = ThemeMapping({
        "editor": "editor.*",
        "terminal": "terminal.*",
        "sidebar": "sideBar.*",
        "statusbar": "statusBar.*"
    })

    @on_theme_change
    def update_layout_colors(self, theme):
        # Custom logic for complex updates
        self.splitter.setStyleSheet(theme.generate_qss("splitter"))
```

## Summary

The key to our theme system's success is **progressive enhancement**:
1. Developers get theming for free by using VFWidget
2. Simple decorators/properties for customization
3. Full control when needed
4. Type safety and IDE support throughout
5. Convention over configuration

Most widgets will only need Level 0 or Level 1 integration, making theme support essentially automatic!