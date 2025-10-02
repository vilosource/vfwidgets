# API Reference - VFWidgets Theme System 2.0

**Complete API documentation organized by skill level.**

---

## Navigation

- [Simple API](#simple-api-start-here) - For building themed applications (90% of users)
- [Advanced API](#advanced-api-custom-widgets) - For custom widget development
- [Developer Experience Features](#developer-experience-features) - Tokens, descriptors, enums
- [Theme Creation](#theme-creation) - Building custom themes

**New to the theme system?** Start with the [Quick Start Guide](quick-start-GUIDE.md).

**Building custom widgets?** See the [Widget Development Guide](widget-development-GUIDE.md).

---

## Simple API (Start Here)

**For building themed applications quickly with minimal code.**

### ThemedApplication

Application class that sets up the theme system.

**Usage:**
```python
from vfwidgets_theme import ThemedApplication
import sys

app = ThemedApplication(sys.argv)

# Optional: Set theme at startup
app.set_theme("dark")  # or "light", "default", etc.

window = YourMainWindow()
window.show()

sys.exit(app.exec())
```

**Methods:**

#### `set_theme(name: str) -> None`

Set the active theme for the entire application.

```python
app.set_theme("dark")    # Built-in dark theme
app.set_theme("light")   # Built-in light theme
app.set_theme("default") # Default light theme
```

**Available built-in themes:**
- `"dark"` - Professional dark theme with good contrast
- `"light"` - High contrast light theme
- `"default"` - Default light theme (used at startup)
- `"minimal"` - Monochrome fallback theme

#### `get_current_theme() -> Theme`

Get the currently active theme object.

```python
theme = app.get_current_theme()
print(f"Current theme: {theme.name}")
```

#### `available_themes: list[str]`

List of all available theme names.

```python
for theme_name in app.available_themes:
    print(theme_name)
```

#### `load_theme_file(path: str | Path) -> None`

Load a custom theme from a JSON file.

```python
app.load_theme_file("mytheme.json")
app.set_theme("mytheme")
```

#### `import_vscode_theme(path: str | Path) -> bool`

Import a VS Code theme file.

```python
if app.import_vscode_theme("monokai.json"):
    app.set_theme("Monokai")
```

---

### ThemedMainWindow

Themed main window for applications.

**When to use:** Building a main application window.

**Usage:**
```python
from vfwidgets_theme import ThemedMainWindow

class MyApp(ThemedMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Application")

        # Add your UI elements
        # All widgets are automatically themed!
```

**Features:**
- ✅ Automatic theming of all child widgets
- ✅ Updates when theme changes
- ✅ Full `QMainWindow` functionality
- ✅ Single inheritance (simple)

**Complete example:**
```python
from vfwidgets_theme import ThemedApplication, ThemedMainWindow
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget

class MyApp(ThemedMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hello World")

        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Add button - automatically themed!
        button = QPushButton("Click Me")
        layout.addWidget(button)

app = ThemedApplication(sys.argv)
window = MyApp()
window.show()
sys.exit(app.exec())
```

---

### ThemedDialog

Themed dialog window.

**When to use:** Building dialog windows (settings, prompts, etc.).

**Usage:**
```python
from vfwidgets_theme import ThemedDialog
from PySide6.QtWidgets import QVBoxLayout, QPushButton

class SettingsDialog(ThemedDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout(self)

        # Add dialog content
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)
```

**Features:**
- ✅ Automatic theming
- ✅ Full `QDialog` functionality
- ✅ Modal and non-modal support
- ✅ Single inheritance

---

### ThemedQWidget

Themed container widget.

**When to use:** Building simple custom container widgets.

**Usage:**
```python
from vfwidgets_theme import ThemedQWidget
from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton

class StatusWidget(ThemedQWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        self.label = QLabel("Status: Ready")
        layout.addWidget(self.label)

        self.button = QPushButton("Update")
        layout.addWidget(self.button)
```

**Features:**
- ✅ Automatic theming
- ✅ Full `QWidget` functionality
- ✅ Single inheritance
- ✅ Perfect for container widgets

**When NOT to use:**

If you need to inherit from other Qt widgets (QTextEdit, QFrame, QPushButton, etc.), use [ThemedWidget](#themedwidget) instead. See the [Widget Development Guide](widget-development-GUIDE.md).

---

### Widget Roles

Semantic roles provide automatic styling without custom CSS.

**Usage:**
```python
from PySide6.QtWidgets import QPushButton

# Danger button (red)
delete_btn = QPushButton("Delete")
delete_btn.setProperty("role", "danger")

# Success button (green)
save_btn = QPushButton("Save")
save_btn.setProperty("role", "success")

# Warning button (yellow)
warning_btn = QPushButton("Proceed")
warning_btn.setProperty("role", "warning")

# Secondary button (muted)
cancel_btn = QPushButton("Cancel")
cancel_btn.setProperty("role", "secondary")

# Editor (monospace font)
code_editor = QTextEdit()
code_editor.setProperty("role", "editor")
```

**Available roles:**
- `"danger"` - Red styling for destructive actions
- `"success"` - Green styling for positive actions
- `"warning"` - Yellow styling for warnings
- `"secondary"` - Muted styling for secondary actions
- `"primary"` - Primary accent color
- `"info"` - Blue informational styling
- `"editor"` - Monospace font for code/text editors

**Type-safe alternative:** See [WidgetRole enum](#widgetrole) in Advanced API.

---

## Advanced API (Custom Widgets)

**For creating custom widget classes that inherit from Qt widgets.**

**📖 Full guide:** [Widget Development Guide](widget-development-GUIDE.md)

### ThemedWidget

The core mixin for creating themed custom widgets.

**When to use:** Building custom widgets that inherit from QTextEdit, QFrame, QPushButton, or any Qt widget besides QWidget/QMainWindow/QDialog.

**Understanding the 80/20 Use Cases:**

ThemedWidget supports two primary use cases:

1. **80% Case (Simple):** Access theme properties for custom painting/styling
   - Use `self.theme.property` to get themed colors
   - Automatic Qt stylesheet styling
   - Perfect for widgets with custom `paintEvent()` or styling

2. **20% Case (Complex):** Pass theme to children or external components
   - Use `get_current_theme()` to get Theme object
   - Pass theme to child widgets or renderers
   - For multi-component widgets

**See:** [Official Theming Guide](THEMING-GUIDE-OFFICIAL.md) for complete patterns and examples.

**Pattern:**
```python
from vfwidgets_theme import ThemedWidget
from PySide6.QtWidgets import QTextEdit

class CodeEditor(ThemedWidget, QTextEdit):
    """IMPORTANT: ThemedWidget must come FIRST."""

    theme_config = {
        'bg': 'editor.background',
        'fg': 'editor.foreground',
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        # Widget is now fully themed!
```

**Key Rules:**

1. **Inheritance Order:** ThemedWidget MUST come before Qt base class
   ```python
   # ✅ Correct
   class MyWidget(ThemedWidget, QTextEdit):
       pass

   # ❌ Wrong - Will raise TypeError!
   class MyWidget(QTextEdit, ThemedWidget):
       pass
   ```

2. **Runtime Validation:** The system validates inheritance order automatically:
   ```python
   # This will fail with helpful error message:
   class BadWidget(QTextEdit, ThemedWidget):
       pass

   widget = BadWidget()
   # TypeError: BadWidget: ThemedWidget must come BEFORE QTextEdit.
   #   ❌ Wrong: class BadWidget(QTextEdit, ThemedWidget)
   #   ✅ Right: class BadWidget(ThemedWidget, QTextEdit)
   ```

**Configuration:**

#### `theme_config` dict

Maps theme tokens to semantic property names:

```python
class MyWidget(ThemedWidget, QWidget):
    theme_config = {
        'bg': 'window.background',        # Background color
        'fg': 'window.foreground',        # Foreground/text color
        'accent': 'colors.primary',       # Accent color
        'border': 'panel.border',         # Border color
    }
```

**Accessing theme values:**

```python
def paintEvent(self, event):
    # Access configured theme values
    bg_color = self.theme.bg
    fg_color = self.theme.fg
    accent = self.theme.accent

    painter = QPainter(self)
    painter.fillRect(self.rect(), QColor(bg_color))
```

**Methods:**

#### `on_theme_changed()`

Override to respond to theme changes.

```python
class MyWidget(ThemedWidget, QWidget):
    def on_theme_changed(self):
        """Called automatically when theme changes."""
        # Note: self.update() is already called by the framework
        # Use this for additional logic only
        self.recalculate_layout()  # Custom logic
        self.update_children()     # Update child widgets
```

#### `get_current_theme() -> Theme`

Get the actual Theme object (for 20% case - passing theme to children/renderers).

```python
class ComplexWidget(ThemedWidget, QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Get Theme object to pass to children or renderers
        theme = self.get_current_theme()

        # Pass to child component
        self.renderer = CustomRenderer(theme=theme)

        # Pass to non-ThemedWidget child
        self.child = PlainQWidget(self)
        self.child.theme = theme
```

**See:** [Official Theming Guide](THEMING-GUIDE-OFFICIAL.md) for complete 80/20 use case patterns

#### `before_theme_change(old_theme: Theme, new_theme: Theme) -> bool`

(Advanced) Called before theme changes. Return False to prevent change.

```python
def before_theme_change(self, old_theme, new_theme):
    """Return False to defer theme change."""
    if self.is_busy():
        return False  # Don't change theme now
    return True
```

#### `after_theme_applied()`

(Advanced) Called after theme is fully applied.

```python
def after_theme_applied(self):
    """Do expensive operations here."""
    self.rebuild_syntax_highlighter()
```

**Properties:**

#### `theme`

Dynamic property accessor for configured theme properties.

```python
class MyWidget(ThemedWidget, QWidget):
    theme_config = {'bg': 'window.background'}

    def paintEvent(self, event):
        color = self.theme.bg  # Accesses 'window.background' from theme
```

---

### Common Patterns

#### Custom Text Editor

```python
from vfwidgets_theme import ThemedWidget
from PySide6.QtWidgets import QTextEdit

class CodeEditor(ThemedWidget, QTextEdit):
    theme_config = {
        'bg': 'editor.background',
        'fg': 'editor.foreground',
        'selection_bg': 'editor.selectionBackground',
    }

    def __init__(self, parent=None):
        super().__init__()
        self.setProperty("role", "editor")  # Monospace font
```

#### Custom Button

```python
from vfwidgets_theme import ThemedWidget
from PySide6.QtWidgets import QPushButton

class IconButton(ThemedWidget, QPushButton):
    theme_config = {
        'bg': 'button.background',
        'hover_bg': 'button.hoverBackground',
    }
```

#### Custom Frame

```python
from vfwidgets_theme import ThemedWidget
from PySide6.QtWidgets import QFrame

class Panel(ThemedWidget, QFrame):
    theme_config = {
        'bg': 'panel.background',
        'border': 'panel.border',
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel)
```

---

## Developer Experience Features

**Tools to make theme development cleaner and easier.**

### Tokens

Token constants for IDE autocomplete.

**Problem:** String literals don't have autocomplete:
```python
theme_config = {'bg': 'window.background'}  # What tokens exist? 🤷
```

**Solution:** Use Tokens constants:
```python
from vfwidgets_theme import Tokens

theme_config = {
    'bg': Tokens.WINDOW_BACKGROUND,      # IDE autocomplete! ✅
    'fg': Tokens.WINDOW_FOREGROUND,
    'accent': Tokens.COLORS_PRIMARY,
}
```

**Usage:**
```python
from vfwidgets_theme import ThemedWidget, Tokens

class MyWidget(ThemedWidget, QWidget):
    theme_config = {
        'bg': Tokens.EDITOR_BACKGROUND,
        'fg': Tokens.EDITOR_FOREGROUND,
        'selection': Tokens.EDITOR_SELECTION_BACKGROUND,
        'border': Tokens.PANEL_BORDER,
    }
```

**Common token categories:**

```python
# Colors
Tokens.COLORS_FOREGROUND
Tokens.COLORS_BACKGROUND
Tokens.COLORS_PRIMARY
Tokens.COLORS_SECONDARY

# Window
Tokens.WINDOW_BACKGROUND
Tokens.WINDOW_FOREGROUND
Tokens.WINDOW_BORDER

# Buttons
Tokens.BUTTON_BACKGROUND
Tokens.BUTTON_FOREGROUND
Tokens.BUTTON_HOVER_BACKGROUND
Tokens.BUTTON_PRESSED_BACKGROUND

# Editor
Tokens.EDITOR_BACKGROUND
Tokens.EDITOR_FOREGROUND
Tokens.EDITOR_SELECTION_BACKGROUND
Tokens.EDITOR_LINE_HIGHLIGHT_BACKGROUND

# Input fields
Tokens.INPUT_BACKGROUND
Tokens.INPUT_FOREGROUND
Tokens.INPUT_BORDER
Tokens.INPUT_PLACEHOLDER_FOREGROUND

# Lists
Tokens.LIST_BACKGROUND
Tokens.LIST_ACTIVE_SELECTION_BACKGROUND
Tokens.LIST_HOVER_BACKGROUND
```

**Methods:**

#### `Tokens.all_tokens() -> list[str]`

Get all available token strings:

```python
all_tokens = Tokens.all_tokens()
# ['colors.foreground', 'colors.background', ...]
```

#### `Tokens.validate(token: str) -> bool`

Check if a token exists:

```python
if Tokens.validate('window.background'):
    print("Valid token!")
```

---

### ThemeProperty

Property descriptor for clean theme access.

**Problem:** `getattr(self.theme, 'bg', '#fff')` is verbose.

**Solution:** Use ThemeProperty descriptors:

```python
from vfwidgets_theme import ThemedWidget, Tokens
from vfwidgets_theme.widgets.properties import ThemeProperty

class MyWidget(ThemedWidget, QWidget):
    # Property descriptors
    bg = ThemeProperty(Tokens.WINDOW_BACKGROUND)
    fg = ThemeProperty(Tokens.WINDOW_FOREGROUND)
    accent = ThemeProperty(Tokens.COLORS_PRIMARY)

    def paintEvent(self, event):
        painter = QPainter(self)

        # Clean property access - no getattr!
        painter.fillRect(self.rect(), QColor(self.bg))
        painter.setPen(QColor(self.fg))
```

**Constructor:**

```python
ThemeProperty(token: str, default: Optional[str] = None)
```

- `token` - Theme token name (use Tokens constants)
- `default` - Optional fallback value if token not found

**Example with defaults:**

```python
class MyWidget(ThemedWidget, QWidget):
    bg = ThemeProperty(Tokens.WINDOW_BACKGROUND, default='#ffffff')
    accent = ThemeProperty(Tokens.COLORS_PRIMARY, default='#007acc')
```

**Features:**
- ✅ Read-only (theme properties can't be set)
- ✅ Smart defaults from ColorTokenRegistry
- ✅ IDE autocomplete
- ✅ Type-safe

---

### ColorProperty

Specialized ThemeProperty that returns QColor instances.

```python
from vfwidgets_theme.widgets.properties import ColorProperty

class MyWidget(ThemedWidget, QWidget):
    bg = ColorProperty(Tokens.WINDOW_BACKGROUND)

    def paintEvent(self, event):
        painter = QPainter(self)
        # Returns QColor directly!
        painter.fillRect(self.rect(), self.bg)
```

---

### FontProperty

Specialized ThemeProperty that returns QFont instances.

```python
from vfwidgets_theme.widgets.properties import FontProperty

class MyWidget(ThemedWidget, QWidget):
    editor_font = FontProperty(Tokens.EDITOR_FONT_FAMILY)

    def __init__(self):
        super().__init__()
        # Returns QFont directly!
        self.setFont(self.editor_font)
```

---

### WidgetRole

Type-safe enum for widget roles.

**Problem:** String-based roles have no IDE support:
```python
button.setProperty("role", "dange")  # Typo - runtime error!
```

**Solution:** Use WidgetRole enum:

```python
from vfwidgets_theme import WidgetRole, set_widget_role

button = QPushButton("Delete")
set_widget_role(button, WidgetRole.DANGER)  # IDE autocomplete! ✅
```

**Available roles:**

```python
class WidgetRole(Enum):
    DANGER = "danger"      # Red styling
    SUCCESS = "success"    # Green styling
    WARNING = "warning"    # Yellow styling
    SECONDARY = "secondary"  # Muted styling
    EDITOR = "editor"      # Monospace font
    PRIMARY = "primary"    # Primary accent
    INFO = "info"          # Blue informational
```

**Functions:**

#### `set_widget_role(widget, role: WidgetRole)`

Set widget role with automatic style refresh:

```python
from vfwidgets_theme import WidgetRole, set_widget_role

delete_btn = QPushButton("Delete")
set_widget_role(delete_btn, WidgetRole.DANGER)

save_btn = QPushButton("Save")
set_widget_role(save_btn, WidgetRole.SUCCESS)
```

#### `get_widget_role(widget) -> WidgetRole | None`

Get widget role if set:

```python
from vfwidgets_theme.widgets.roles import get_widget_role

role = get_widget_role(button)
if role == WidgetRole.DANGER:
    print("Danger button!")
```

---

## Theme Creation

**For creating custom themes.**

**📖 Full guide:** [Theme Customization Guide](theme-customization-GUIDE.md)

### Theme

Immutable theme data class.

```python
@dataclass(frozen=True)
class Theme:
    name: str
    version: str = "1.0.0"
    colors: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
```

**Properties:**
- `name` - Theme name
- `version` - Theme version
- `colors` - Dictionary of token → color mappings
- `metadata` - Additional theme metadata

**Methods:**

#### `get(token: str, default: Any = None) -> Any`

Get theme token value with optional default:

```python
theme = app.get_current_theme()
bg_color = theme.get('window.background', '#ffffff')
```

---

### ThemeBuilder

Builder for creating themes.

```python
from vfwidgets_theme import ThemeBuilder, Tokens

theme = (ThemeBuilder("my_theme")
    .set_type("dark")
    .add_color(Tokens.COLORS_FOREGROUND, "#e0e0e0")
    .add_color(Tokens.COLORS_BACKGROUND, "#1e1e1e")
    .add_color(Tokens.BUTTON_BACKGROUND, "#0e639c")
    .add_metadata("description", "My custom theme")
    .build())
```

**Methods:**

#### `set_type(theme_type: str) -> ThemeBuilder`

Set theme type ("dark" or "light"):

```python
builder.set_type("dark")
```

#### `add_color(token: str, color: str) -> ThemeBuilder`

Add a color token:

```python
builder.add_color(Tokens.WINDOW_BACKGROUND, "#1e1e1e")
```

#### `add_metadata(key: str, value: Any) -> ThemeBuilder`

Add metadata:

```python
builder.add_metadata("author", "John Doe")
builder.add_metadata("description", "A dark theme")
```

#### `extend(parent_theme: Union[str, Theme]) -> ThemeBuilder`

**Phase 2 Feature** - Inherit from a parent theme:

```python
# Extend built-in theme
custom = (ThemeBuilder("custom")
    .extend("dark")  # Inherit all dark theme properties
    .add_color("button.background", "#ff0000")  # Override specific properties
    .build())

# Extend another Theme instance
parent = ThemeBuilder("parent").build()
child = ThemeBuilder("child").extend(parent).build()
```

**Behavior:**
- Inherits all colors, styles, and metadata from parent
- Properties set BEFORE `.extend()` are preserved (not overridden)
- Properties set AFTER `.extend()` override parent values
- Parent reference stored in `metadata["parent_theme"]`

#### `build() -> Theme`

Build the immutable Theme object:

```python
theme = builder.build()
```

---

### ThemeComposer

**Phase 2 Feature** - Merge multiple themes together.

```python
from vfwidgets_theme.core.theme import ThemeComposer

composer = ThemeComposer()

# Compose two themes (later overrides earlier)
base = app.get_theme("dark")
custom_buttons = ThemeBuilder("custom-buttons").add_color("button.background", "#ff0000").build()
merged = composer.compose(base, custom_buttons, name="dark-with-custom-buttons")

# Compose chain of themes
result = composer.compose_chain([theme1, theme2, theme3])

# Caching - same composition returns cached result
result1 = composer.compose(theme1, theme2)
result2 = composer.compose(theme1, theme2)  # Same instance (cached)

# Clear cache
composer.clear_cache()
```

**Methods:**

#### `compose(*themes: Theme, name: Optional[str] = None) -> Theme`

Merge themes with priority (later themes override earlier):

```python
merged = composer.compose(base_theme, override_theme, name="merged")
```

#### `compose_chain(themes: List[Theme]) -> Theme`

Compose a list of themes:

```python
result = composer.compose_chain([theme1, theme2, theme3])
```

#### `clear_cache() -> None`

Clear composition cache:

```python
composer.clear_cache()
```

---

### ThemeValidator

**Phase 2 Feature** - Validate themes for accessibility and correctness.

```python
from vfwidgets_theme.core.theme import ThemeValidator

validator = ThemeValidator()

# Validate accessibility (WCAG contrast ratios)
result = validator.validate_accessibility(theme)
if result.is_valid:
    print("Theme passes accessibility checks!")
else:
    for error in result.errors:
        print(f"Error: {error}")
    for warning in result.warnings:
        print(f"Warning: {warning}")

# Get enhanced error messages
error_msg = validator.format_error("button.backgroud", "not_found")
# Output includes:
#   - Typo suggestions
#   - Available properties list
#   - Documentation links
```

**Methods:**

#### `validate_accessibility(theme: Theme) -> ValidationResult`

Validate WCAG contrast ratios:

```python
result = validator.validate_accessibility(theme)
# result.is_valid: bool
# result.errors: List[str]
# result.warnings: List[str]
```

**Checks:**
- Text contrast ratio ≥ 4.5:1 (WCAG AA)
- Large text contrast ratio ≥ 3:1
- Button contrast ratios
- Input field contrast ratios

#### `format_error(property_name: str, error_type: str = "not_found") -> str`

Generate enhanced error message with suggestions and docs links:

```python
error_msg = validator.format_error("button.backgroud", "not_found")
# Suggests: "button.background"
# Lists: Available button.* properties
# Links: https://vfwidgets.readthedocs.io/themes/tokens#button
```

#### `suggest_correction(property_name: str) -> Optional[str]`

Get typo correction suggestion:

```python
suggestion = validator.suggest_correction("buton.background")
# Returns: "button.background"
```

#### `get_available_properties(prefix: str = "") -> List[str]`

Get list of available properties with given prefix:

```python
button_props = validator.get_available_properties("button")
# Returns: ["button.background", "button.foreground", "button.border", ...]
```

---

## Common Theme Tokens

**Complete token reference:** See [Theme Customization Guide](theme-customization-GUIDE.md)

### Base Colors (11 tokens)

- `colors.foreground` - Primary text color
- `colors.background` - Primary background color
- `colors.primary` - Primary accent color
- `colors.secondary` - Secondary accent color
- `errorForeground` - Error text color
- `warningForeground` - Warning text color
- `successForeground` - Success text color

### Window (8 tokens)

- `window.background`
- `window.foreground`
- `window.border`
- `window.activeBorder`
- `window.inactiveBorder`

### Buttons (12 tokens)

- `button.background`
- `button.foreground`
- `button.hoverBackground`
- `button.hoverForeground`
- `button.pressedBackground`
- `button.disabledBackground`
- `button.disabledForeground`
- `button.border`

### Input Fields (10 tokens)

- `input.background`
- `input.foreground`
- `input.border`
- `input.placeholderForeground`
- `input.focusBorder`
- `input.errorBorder`

### Editor (45+ tokens)

- `editor.background`
- `editor.foreground`
- `editor.selectionBackground`
- `editor.selectionForeground`
- `editor.lineHighlightBackground`
- `editor.findMatchBackground`
- `editor.findMatchHighlightBackground`
- ... (see theme customization guide for complete list)

### Lists (12 tokens)

- `list.background`
- `list.foreground`
- `list.activeSelectionBackground`
- `list.activeSelectionForeground`
- `list.inactiveSelectionBackground`
- `list.hoverBackground`
- `list.focusBackground`

---

## Migration from Theme System 1.0

**For users upgrading from the old API.**

### Key Changes

1. **Convenience classes added** - ThemedQWidget, ThemedMainWindow, ThemedDialog
2. **Smart defaults** - No more `getattr(self.theme, 'bg', '#fff')` needed
3. **Tokens constants** - IDE autocomplete for theme tokens
4. **ThemeProperty descriptors** - Cleaner property access
5. **WidgetRole enum** - Type-safe roles

### Old API Still Works

All existing code continues to work:

```python
# This still works perfectly
class MyWidget(ThemedWidget, QWidget):
    theme_config = {
        'bg': 'window.background'  # String literals still work
    }

    def paintEvent(self, event):
        bg = getattr(self.theme, 'bg', '#fff')  # Still works
```

### Recommended Migration Path

1. **Use convenience classes where possible:**
   ```python
   # Old
   class MyWindow(ThemedWidget, QMainWindow):
       pass

   # New (simpler)
   class MyWindow(ThemedMainWindow):
       pass
   ```

2. **Use Tokens for discoverability:**
   ```python
   # Old
   theme_config = {'bg': 'window.background'}

   # New (with autocomplete)
   theme_config = {'bg': Tokens.WINDOW_BACKGROUND}
   ```

3. **Use ThemeProperty for clean access:**
   ```python
   # Old
   bg = getattr(self.theme, 'bg', '#fff')

   # New (cleaner)
   bg = ThemeProperty(Tokens.WINDOW_BACKGROUND)
   # Access: self.bg
   ```

---

## See Also

- **[Quick Start Guide](quick-start-GUIDE.md)** - Get started in 5 minutes
- **[Widget Development Guide](widget-development-GUIDE.md)** - Build custom themed widgets
- **[Theme Customization Guide](theme-customization-GUIDE.md)** - Create custom themes
- **[API Strategy](API-STRATEGY.md)** - Understand the progressive API design
- **[Architecture](ARCHITECTURE.md)** - System internals
- **[Roadmap](ROADMAP.md)** - Design decisions and future plans
