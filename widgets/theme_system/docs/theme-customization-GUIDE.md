# Theme Customization Guide

Learn how to create and customize themes for your PySide6 applications.

---

## Table of Contents

1. [Creating a Simple Theme](#creating-a-simple-theme)
2. [Understanding Theme Tokens](#understanding-theme-tokens)
3. [Using Token Constants](#using-token-constants-new-in-v200-rc4) (NEW in v2.0.0-rc4)
4. [Using ThemeBuilder](#using-themebuilder)
5. [Theme Inheritance](#theme-inheritance) (NEW - Phase 2)
6. [Theme Composition](#theme-composition) (NEW - Phase 2)
7. [Accessibility Validation](#accessibility-validation) (NEW - Phase 2)
8. [Complete Theme Example](#complete-theme-example)
9. [Loading Custom Themes](#loading-custom-themes)
10. [Modifying Built-in Themes](#modifying-built-in-themes)
11. [Theme Token Reference](#theme-token-reference)

---

## Creating a Simple Theme

The easiest way to create a theme is using `ThemeBuilder`:

```python
from vfwidgets_theme.core.theme import Theme, ThemeBuilder

# Create a simple theme
my_theme = (ThemeBuilder("my_theme")
    .set_type("dark")  # "dark" or "light"
    .add_color("colors.background", "#1e1e1e")
    .add_color("colors.foreground", "#d4d4d4")
    .add_color("button.background", "#0e639c")
    .add_color("button.foreground", "#ffffff")
    .add_color("font.default.family", "Arial, sans-serif")
    .add_color("font.default.size", "9pt")
    .build())
```

---

## Understanding Theme Tokens

Theme System 2.0 uses **197 tokens** organized into categories:

### Token Categories

1. **Base Colors** (11 tokens) - Fundamental colors
   - `colors.foreground`, `colors.background`
   - `colors.primary`, `colors.secondary`
   - `colors.focusBorder`, `colors.contrastBorder`

2. **Button Colors** (18 tokens) - All button states
   - `button.background`, `button.foreground`
   - `button.hoverBackground`, `button.pressedBackground`
   - `button.danger.background`, `button.success.background`

3. **Input Colors** (18 tokens) - Text fields, text areas
   - `input.background`, `input.foreground`
   - `input.border`, `input.focusBorder`
   - `input.placeholderForeground`

4. **Editor Colors** (35 tokens) - Code/text editors
   - `editor.background`, `editor.foreground`
   - `editor.selectionBackground`
   - `editorLineNumber.foreground`

5. **List/Tree Colors** (22 tokens) - Lists, trees, tables
   - `list.background`, `list.foreground`
   - `list.activeSelectionBackground`
   - `list.hoverBackground`

6. **Tab Colors** (17 tokens) - Tab widgets
   - `tab.activeBackground`, `tab.inactiveBackground`
   - `tab.border`, `tab.hoverBackground`

7. **Menu Colors** (11 tokens) - Menus and menu bars
   - `menu.background`, `menu.foreground`
   - `menu.selectionBackground`

8. **Font Tokens** (14 tokens) - Typography
   - `font.default.family`, `font.default.size`
   - `font.editor.family`, `font.editor.size`

### Token Naming Convention

Tokens follow a hierarchical dot notation:

```
<component>.<property>
<component>.<state>.<property>
<component>.<variant>.<property>
```

**Examples:**
```
button.background              # Button background color
button.hoverBackground         # Button background when hovered
button.danger.background       # Danger button background
editor.selectionBackground     # Editor selection background
font.editor.family             # Editor font family
```

---

## Using Token Constants (NEW in v2.0.0-rc4)

Instead of typing token strings manually (which is error-prone), use the `Tokens` class for **IDE autocomplete** and **typo prevention**:

### Before (Magic Strings)

```python
from vfwidgets_theme.core.theme import ThemeBuilder

theme = (ThemeBuilder("my_theme")
    .set_type("dark")
    .add_color("colors.foreground", "#ffffff")  # Typo risk!
    .add_color("colors.background", "#1e1e1e")  # No autocomplete
    .add_color("buttn.background", "#0e639c")   # Typo! Won't catch until runtime
    .build())
```

### After (Token Constants)

```python
from vfwidgets_theme.core.theme import ThemeBuilder
from vfwidgets_theme import Tokens  # NEW!

theme = (ThemeBuilder("my_theme")
    .set_type("dark")
    .add_color(Tokens.COLORS_FOREGROUND, "#ffffff")  # IDE autocomplete!
    .add_color(Tokens.COLORS_BACKGROUND, "#1e1e1e")  # Typo-safe!
    .add_color(Tokens.BUTTON_BACKGROUND, "#0e639c")  # IDE catches typos!
    .build())
```

### Benefits of Token Constants

1. **IDE Autocomplete**: Type `Tokens.` and see all 179 available tokens
2. **Typo Prevention**: IDE catches invalid token names at write-time
3. **Refactoring Safe**: Rename refactoring works correctly
4. **Documentation**: Hover over constant to see token description

### Available Token Categories

```python
from vfwidgets_theme import Tokens

# Base Colors (11 tokens)
Tokens.COLORS_FOREGROUND
Tokens.COLORS_BACKGROUND
Tokens.COLORS_PRIMARY
Tokens.COLORS_FOCUS_BORDER

# Button Colors (18 tokens)
Tokens.BUTTON_BACKGROUND
Tokens.BUTTON_FOREGROUND
Tokens.BUTTON_HOVER_BACKGROUND
Tokens.BUTTON_DANGER_BACKGROUND

# Input Colors (18 tokens)
Tokens.INPUT_BACKGROUND
Tokens.INPUT_FOREGROUND
Tokens.INPUT_BORDER
Tokens.INPUT_FOCUS_BORDER

# Editor Colors (35 tokens)
Tokens.EDITOR_BACKGROUND
Tokens.EDITOR_FOREGROUND
Tokens.EDITOR_SELECTION_BACKGROUND
Tokens.EDITOR_LINE_NUMBER_FOREGROUND

# List/Tree Colors (20 tokens)
Tokens.LIST_BACKGROUND
Tokens.LIST_ACTIVE_SELECTION_BACKGROUND
Tokens.LIST_HOVER_BACKGROUND

# Tabs, Panels, Menus, etc. (77+ more tokens)
Tokens.TAB_ACTIVE_BACKGROUND
Tokens.PANEL_BACKGROUND
Tokens.MENU_BACKGROUND
Tokens.STATUSBAR_BACKGROUND
```

### Using with Widget theme_config

```python
from vfwidgets_theme import ThemedWidget, Tokens
from PySide6.QtWidgets import QWidget

class MyWidget(ThemedWidget, QWidget):
    """Custom widget with type-safe token usage."""

    theme_config = {
        'bg': Tokens.EDITOR_BACKGROUND,      # IDE autocomplete!
        'fg': Tokens.EDITOR_FOREGROUND,
        'selection': Tokens.EDITOR_SELECTION_BACKGROUND,
        'border': Tokens.COLORS_FOCUS_BORDER
    }

    def __init__(self):
        super().__init__()
        # Widget automatically themed with correct tokens
```

### Utility Methods

```python
from vfwidgets_theme import Tokens

# Get all token strings as a list
all_tokens = Tokens.all_tokens()  # Returns list of 179 token strings
print(f"Total tokens: {len(all_tokens)}")

# Validate a token string
is_valid = Tokens.validate("colors.foreground")  # True
is_valid = Tokens.validate("invalid.token")      # False
```

### Backward Compatibility

**Token constants are just strings!** You can still use strings directly:

```python
# Both are equivalent:
theme_config = {'bg': Tokens.EDITOR_BACKGROUND}  # New way
theme_config = {'bg': 'editor.background'}       # Old way still works
```

---

## Using ThemeBuilder

`ThemeBuilder` provides a fluent API for creating themes:

### Basic Theme

```python
from vfwidgets_theme.core.theme import ThemeBuilder

theme = (ThemeBuilder("my_simple_theme")
    .set_type("dark")
    .add_metadata("description", "My first custom theme")
    .add_color("colors.foreground", "#ffffff")
    .add_color("colors.background", "#1e1e1e")
    .build())
```

### Comprehensive Theme

```python
theme = (ThemeBuilder("my_comprehensive_theme")
    .set_type("dark")
    .add_metadata("description", "A complete custom theme")

    # Base colors
    .add_color("colors.foreground", "#e0e0e0")
    .add_color("colors.background", "#181818")
    .add_color("colors.primary", "#007acc")
    .add_color("colors.focusBorder", "#007acc")

    # Button colors
    .add_color("button.background", "#0e639c")
    .add_color("button.foreground", "#ffffff")
    .add_color("button.hoverBackground", "#1177bb")
    .add_color("button.pressedBackground", "#094771")

    # Button roles
    .add_color("button.danger.background", "#dc3545")
    .add_color("button.success.background", "#28a745")
    .add_color("button.warning.background", "#ffc107")
    .add_color("button.secondary.background", "#313131")

    # Input colors
    .add_color("input.background", "#2d2d2d")
    .add_color("input.foreground", "#e0e0e0")
    .add_color("input.border", "#3c3c3c")
    .add_color("input.focusBorder", "#007acc")

    # Editor colors
    .add_color("editor.background", "#1e1e1e")
    .add_color("editor.foreground", "#d4d4d4")
    .add_color("editor.selectionBackground", "#264f78")

    # List colors
    .add_color("list.background", "#252526")
    .add_color("list.foreground", "#cccccc")
    .add_color("list.activeSelectionBackground", "#094771")
    .add_color("list.hoverBackground", "#2a2d2e")

    # Fonts
    .add_color("font.default.family", "Segoe UI, Arial, sans-serif")
    .add_color("font.default.size", "9pt")
    .add_color("font.editor.family", "Courier New, Consolas, monospace")
    .add_color("font.editor.size", "11pt")

    .build())
```

### Copy and Modify

Start with a built-in theme and modify it:

```python
from vfwidgets_theme import ThemedApplication

app = ThemedApplication([])

# Get the vscode theme
vscode_theme = app.get_current_theme()

# Create a modified version
my_theme = (ThemeBuilder("my_vscode_variant")
    .set_type(vscode_theme.type)
    .add_colors(vscode_theme.colors)  # Copy all colors

    # Override specific colors
    .add_color("colors.primary", "#ff0000")  # Custom primary color
    .add_color("button.background", "#cc0000")  # Custom button color

    .build())
```

---

## Theme Inheritance

**NEW in Phase 2** - Inherit from existing themes using `.extend()`.

### Why Use Inheritance?

Instead of copying all properties manually, inherit from a built-in theme and override only what you need:

```python
from vfwidgets_theme.core.theme import ThemeBuilder

# OLD WAY (manual copying):
base_theme = app.get_theme("dark")
custom = (ThemeBuilder("custom")
    .add_colors(base_theme.colors)  # Copy everything
    .add_color("button.background", "#ff0000")  # Change one thing
    .build())

# NEW WAY (inheritance):
custom = (ThemeBuilder("custom")
    .extend("dark")  # Inherit everything from dark theme
    .add_color("button.background", "#ff0000")  # Override one property
    .build())
```

### Basic Inheritance

```python
# Extend a built-in theme
my_dark_variant = (ThemeBuilder("my_dark_variant")
    .extend("dark")  # Inherit from built-in "dark" theme
    .add_color("colors.primary", "#ff6b6b")  # Override primary color
    .add_color("button.background", "#ff6b6b")  # Override button color
    .build())
```

### Extend from Theme Instance

```python
# Create parent theme
parent = (ThemeBuilder("parent")
    .set_type("dark")
    .add_color("colors.background", "#1e1e1e")
    .add_color("colors.foreground", "#d4d4d4")
    .add_color("button.background", "#0e639c")
    .build())

# Child theme inherits from parent
child = (ThemeBuilder("child")
    .extend(parent)  # Pass Theme instance
    .add_color("button.background", "#ff0000")  # Override button
    .build())

# child.colors["colors.background"] == "#1e1e1e"  (inherited)
# child.colors["button.background"] == "#ff0000"  (overridden)
```

### Inheritance Chain

Themes can extend themes that extend other themes:

```python
# Grandparent
base = (ThemeBuilder("base")
    .set_type("dark")
    .add_color("colors.background", "#000000")
    .add_color("colors.foreground", "#ffffff")
    .build())

# Parent extends grandparent
specialized = (ThemeBuilder("specialized")
    .extend(base)
    .add_color("button.background", "#0e639c")
    .build())

# Child extends parent (inherits from entire chain)
final = (ThemeBuilder("final")
    .extend(specialized)
    .add_color("button.foreground", "#ffffff")
    .build())

# final inherits:
# - colors.background from base
# - colors.foreground from base
# - button.background from specialized
# - button.foreground from final (own property)
```

### Property Override Priority

**IMPORTANT**: Properties set BEFORE `.extend()` are preserved:

```python
# Properties set BEFORE extend are NOT overridden
theme1 = (ThemeBuilder("theme1")
    .add_color("colors.primary", "#ff0000")  # Set FIRST
    .extend("dark")  # dark theme won't override primary
    .build())
# Result: colors.primary = "#ff0000" (preserved)

# Properties set AFTER extend override parent
theme2 = (ThemeBuilder("theme2")
    .extend("dark")  # Inherit dark.primary
    .add_color("colors.primary", "#ff0000")  # Override
    .build())
# Result: colors.primary = "#ff0000" (overridden)
```

---

## Theme Composition

**NEW in Phase 2** - Merge multiple themes together.

### Why Use Composition?

Composition lets you combine themes like layers, with later themes overriding earlier ones:

```python
from vfwidgets_theme.core.theme import ThemeComposer

composer = ThemeComposer()

# Base theme with general colors
base = ThemeBuilder("base").add_color("colors.background", "#1e1e1e").build()

# Button theme with button-specific colors
buttons = ThemeBuilder("buttons").add_color("button.background", "#ff0000").build()

# Input theme with input-specific colors
inputs = ThemeBuilder("inputs").add_color("input.background", "#2d2d2d").build()

# Compose them together
app_theme = composer.compose(base, buttons, inputs, name="app")
# Result has colors from all three themes
```

### Basic Composition

```python
from vfwidgets_theme.core.theme import ThemeComposer

composer = ThemeComposer()

# Two themes with overlapping properties
theme1 = (ThemeBuilder("theme1")
    .add_color("colors.background", "#111111")
    .add_color("colors.foreground", "#ffffff")
    .build())

theme2 = (ThemeBuilder("theme2")
    .add_color("colors.background", "#222222")  # Will override theme1
    .add_color("button.background", "#ff0000")  # New property
    .build())

# Later themes override earlier ones
merged = composer.compose(theme1, theme2, name="merged")

# Result:
# colors.background = "#222222"  (from theme2, overrode theme1)
# colors.foreground = "#ffffff"  (from theme1)
# button.background = "#ff0000"  (from theme2)
```

### Component Library Pattern

Use composition to organize component-specific theming:

```python
# Separate themes for each component
editor_theme = (ThemeBuilder("editor-colors")
    .add_color("editor.background", "#1e1e1e")
    .add_color("editor.foreground", "#d4d4d4")
    .add_color("editor.selectionBackground", "#264f78")
    .build())

toolbar_theme = (ThemeBuilder("toolbar-colors")
    .add_color("toolbar.background", "#2d2d2d")
    .add_color("toolbar.foreground", "#cccccc")
    .build())

sidebar_theme = (ThemeBuilder("sidebar-colors")
    .add_color("sideBar.background", "#252526")
    .add_color("sideBar.foreground", "#cccccc")
    .build())

# Compose into complete application theme
app_theme = composer.compose(
    base_dark_theme,
    editor_theme,
    toolbar_theme,
    sidebar_theme,
    name="my-ide-theme"
)
```

### Compose Chain

For longer lists of themes:

```python
theme_layers = [
    base_theme,
    component_theme1,
    component_theme2,
    component_theme3,
    overrides_theme
]

final_theme = composer.compose_chain(theme_layers)
```

### Caching

Composition results are cached for performance:

```python
composer = ThemeComposer()

# First call - does the work
result1 = composer.compose(theme1, theme2)

# Second call with same themes - returns cached result
result2 = composer.compose(theme1, theme2)
assert result1 is result2  # Same instance (cached)

# Clear cache if needed
composer.clear_cache()
```

---

## Accessibility Validation

**NEW in Phase 2** - Validate themes for WCAG compliance.

### Why Validate?

Ensure your themes meet accessibility standards (WCAG contrast ratios):

```python
from vfwidgets_theme.core.theme import ThemeValidator

validator = ThemeValidator()

# Validate a theme
result = validator.validate_accessibility(my_theme)

if result.is_valid:
    print("✓ Theme passes accessibility checks")
else:
    print("✗ Theme has accessibility issues:")
    for error in result.errors:
        print(f"  ERROR: {error}")
    for warning in result.warnings:
        print(f"  WARNING: {warning}")
```

### WCAG Standards Checked

The validator checks these contrast ratios:
- **Text** (normal): ≥ 4.5:1 (WCAG AA)
- **Text** (large): ≥ 3:1 (WCAG AA)
- **Buttons**: ≥ 4.5:1 foreground/background
- **Input fields**: ≥ 4.5:1 foreground/background

### Example Validation

```python
# Create theme with poor contrast
bad_theme = (ThemeBuilder("bad")
    .add_color("colors.background", "#ffffff")
    .add_color("colors.foreground", "#eeeeee")  # Very low contrast!
    .build())

validator = ThemeValidator()
result = validator.validate_accessibility(bad_theme)

print(result.warnings)
# Output: ["Text contrast ratio 1.2:1 is below WCAG AA (4.5:1)"]
```

### Good Contrast Example

```python
# Create theme with good contrast
good_theme = (ThemeBuilder("good")
    .add_color("colors.background", "#ffffff")
    .add_color("colors.foreground", "#000000")  # Maximum contrast
    .add_color("button.background", "#0066cc")
    .add_color("button.foreground", "#ffffff")
    .build())

result = validator.validate_accessibility(good_theme)
print(result.is_valid)  # True
```

### Enhanced Error Messages

The validator also provides enhanced error messages with suggestions:

```python
# Typo in property name
error_msg = validator.format_error("button.backgroud", "not_found")

print(error_msg)
# Output:
#   Property 'button.backgroud' not found
#
#   Did you mean: 'button.background'?
#
#   Available button properties:
#     - button.background
#     - button.foreground
#     - button.border
#     ... (more)
#
#   See: https://vfwidgets.readthedocs.io/themes/tokens#button

# Get property suggestions
suggestion = validator.suggest_correction("buton.background")
print(suggestion)  # "button.background"

# List available properties
button_props = validator.get_available_properties("button")
print(button_props)
# ["button.background", "button.foreground", "button.border", ...]
```

---

## Complete Theme Example

Here's a complete purple-themed example:

```python
#!/usr/bin/env python3
"""Purple Dream Theme - A custom purple-themed application."""

import sys
from PySide6.QtWidgets import QPushButton, QVBoxLayout
from vfwidgets_theme import ThemedApplication, ThemedMainWindow
from vfwidgets_theme.core.theme import ThemeBuilder

# Create custom purple theme
purple_theme = (ThemeBuilder("purple_dream")
    .set_type("dark")
    .add_metadata("description", "A beautiful purple theme")

    # Base colors - Purple palette
    .add_color("colors.foreground", "#e8d5f0")
    .add_color("colors.background", "#1a0d24")
    .add_color("colors.primary", "#9d4edd")
    .add_color("colors.secondary", "#7b2cbf")
    .add_color("colors.focusBorder", "#9d4edd")
    .add_color("colors.contrastBorder", "#3c1f4d")
    .add_color("colors.disabledForeground", "#6c5279")

    # Button colors - Purple shades
    .add_color("button.background", "#7b2cbf")
    .add_color("button.foreground", "#ffffff")
    .add_color("button.border", "none")
    .add_color("button.hoverBackground", "#9d4edd")
    .add_color("button.pressedBackground", "#5a1d99")
    .add_color("button.disabledBackground", "#3c1f4d")
    .add_color("button.disabledForeground", "#6c5279")

    # Button roles
    .add_color("button.danger.background", "#e63946")
    .add_color("button.danger.hoverBackground", "#d62828")
    .add_color("button.success.background", "#06ffa5")
    .add_color("button.success.hoverBackground", "#00e68a")
    .add_color("button.warning.background", "#ffbe0b")
    .add_color("button.warning.foreground", "#000000")
    .add_color("button.warning.hoverBackground", "#fb8500")
    .add_color("button.secondary.background", "#3c1f4d")
    .add_color("button.secondary.foreground", "#c8b3d6")
    .add_color("button.secondary.hoverBackground", "#5a2d75")

    # Input colors
    .add_color("input.background", "#2a1438")
    .add_color("input.foreground", "#e8d5f0")
    .add_color("input.border", "#3c1f4d")
    .add_color("input.placeholderForeground", "#8a75a3")
    .add_color("input.focusBorder", "#9d4edd")
    .add_color("input.disabledBackground", "#1f0f2e")
    .add_color("input.disabledForeground", "#6c5279")

    # Editor colors
    .add_color("editor.background", "#1a0d24")
    .add_color("editor.foreground", "#e8d5f0")
    .add_color("editor.selectionBackground", "#5a2d75")
    .add_color("editorLineNumber.foreground", "#6c5279")

    # List colors
    .add_color("list.background", "#1f0f2e")
    .add_color("list.foreground", "#e8d5f0")
    .add_color("list.activeSelectionBackground", "#7b2cbf")
    .add_color("list.activeSelectionForeground", "#ffffff")
    .add_color("list.inactiveSelectionBackground", "#3c1f4d")
    .add_color("list.hoverBackground", "#2a1438")

    # Tab colors
    .add_color("tab.activeBackground", "#1a0d24")
    .add_color("tab.activeForeground", "#e8d5f0")
    .add_color("tab.inactiveBackground", "#2a1438")
    .add_color("tab.inactiveForeground", "#8a75a3")
    .add_color("tab.hoverBackground", "#3c1f4d")
    .add_color("tab.border", "#3c1f4d")

    # Menu colors
    .add_color("menu.background", "#1f0f2e")
    .add_color("menu.foreground", "#e8d5f0")
    .add_color("menu.border", "#3c1f4d")
    .add_color("menu.selectionBackground", "#7b2cbf")
    .add_color("menu.selectionForeground", "#ffffff")
    .add_color("menubar.background", "#1a0d24")

    # Scrollbar colors
    .add_color("scrollbarSlider.background", "#5a2d7566")
    .add_color("scrollbarSlider.hoverBackground", "#7b2cbfcc")
    .add_color("scrollbarSlider.activeBackground", "#9d4eddcc")

    # Status bar
    .add_color("statusBar.background", "#7b2cbf")
    .add_color("statusBar.foreground", "#ffffff")

    # Fonts
    .add_color("font.default.family", "Segoe UI, Arial, sans-serif")
    .add_color("font.default.size", "9pt")
    .add_color("font.editor.family", "Courier New, Consolas, monospace")
    .add_color("font.editor.size", "11pt")
    .add_color("font.button.family", "Segoe UI, Arial, sans-serif")
    .add_color("font.button.size", "9pt")

    .build())


def main():
    """Run the purple-themed application."""
    app = ThemedApplication(sys.argv)

    # Save theme to file
    import json
    from pathlib import Path
    theme_file = Path("purple_dream.json")
    theme_file.write_text(json.dumps({
        "name": purple_theme.name,
        "type": purple_theme.type,
        "colors": purple_theme.colors,
        "version": purple_theme.version
    }, indent=2))

    # Load custom theme
    app.load_theme_file(theme_file)

    # Set the purple theme
    app.set_theme("purple_dream")

    # Create window
    window = ThemedMainWindow()
    window.setWindowTitle("Purple Dream Theme")
    window.setMinimumSize(500, 400)

    # Create UI
    from vfwidgets_theme import ThemedQWidget
    central = ThemedQWidget()
    window.setCentralWidget(central)
    layout = QVBoxLayout(central)

    # Add some widgets to see the theme
    buttons = [
        ("Default Button", None),
        ("Danger Button", "danger"),
        ("Success Button", "success"),
        ("Warning Button", "warning"),
        ("Secondary Button", "secondary"),
    ]

    for text, role in buttons:
        btn = QPushButton(text)
        if role:
            btn.setProperty("role", role)
        layout.addWidget(btn)

    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
```

Save this as `purple_theme_example.py` and run it!

---

## Loading Custom Themes

### Method 1: Save to JSON and Load

```python
import json
from pathlib import Path

# Create theme
theme = (ThemeBuilder("my_theme")
    # ... theme definition ...
    .build())

# Save to JSON
theme_data = {
    "name": theme.name,
    "type": theme.type,
    "colors": theme.colors,
    "version": theme.version
}

Path("my_theme.json").write_text(json.dumps(theme_data, indent=2))

# Load from JSON in your application
from vfwidgets_theme import ThemedApplication

app = ThemedApplication(sys.argv)
app.load_theme_file("my_theme.json")
app.set_theme("my_theme")
```

---

## Modifying Built-in Themes

### Override Specific Colors

```python
from vfwidgets_theme import ThemedApplication
from vfwidgets_theme.core.theme import ThemeBuilder
import json
from pathlib import Path

app = ThemedApplication(sys.argv)

# Start with vscode theme
base_theme = app.get_current_theme()

# Create variant with custom primary color
custom_theme = (ThemeBuilder("vscode_custom")
    .set_type(base_theme.type)
    .add_colors(base_theme.colors)  # Copy all colors
    .add_color("colors.primary", "#ff0000")  # Custom primary
    .add_color("button.background", "#cc0000")  # Custom button
    .build())

# Save and load the custom theme
theme_file = Path("vscode_custom.json")
theme_file.write_text(json.dumps({
    "name": custom_theme.name,
    "type": custom_theme.type,
    "colors": custom_theme.colors,
    "version": custom_theme.version
}, indent=2))

app.load_theme_file(theme_file)
app.set_theme("vscode_custom")
```

### Create Light Version of Dark Theme

```python
dark_theme = app.get_current_theme()

light_version = (ThemeBuilder(f"{dark_theme.name}_light")
    .set_type("light")
    .add_colors(dark_theme.colors)

    # Invert key colors
    .add_color("colors.foreground", dark_theme.get("colors.background"))
    .add_color("colors.background", dark_theme.get("colors.foreground"))

    # Adjust other colors as needed
    .add_color("button.background", "#0e639c")
    .add_color("input.background", "#ffffff")

    .build())
```

---

## Theme Token Reference

### Essential Tokens (Minimum for a Theme)

These are the absolute minimum tokens you should define:

```python
theme = (ThemeBuilder("minimal")
    .set_type("dark")

    # Base (required)
    .add_color("colors.foreground", "#ffffff")
    .add_color("colors.background", "#000000")

    # Buttons (required)
    .add_color("button.background", "#0e639c")
    .add_color("button.foreground", "#ffffff")

    # Inputs (required)
    .add_color("input.background", "#1e1e1e")
    .add_color("input.foreground", "#ffffff")

    # Editor (required)
    .add_color("editor.background", "#1e1e1e")
    .add_color("editor.foreground", "#ffffff")

    # Fonts (required)
    .add_color("font.default.family", "Arial, sans-serif")
    .add_color("font.default.size", "9pt")

    .build())
```

**Missing tokens automatically fall back to defaults!**

### Complete Token List

For a comprehensive list of all 197 tokens, see:
- `src/vfwidgets_theme/core/tokens.py` - Complete token registry
- Examples directory - See built-in themes for reference

### Token Categories Summary

| Category | Token Count | Example Tokens |
|----------|-------------|----------------|
| Base | 11 | `colors.foreground`, `colors.primary` |
| Button | 18 | `button.background`, `button.danger.background` |
| Input | 18 | `input.background`, `input.focusBorder` |
| Editor | 35 | `editor.background`, `editor.selectionBackground` |
| List/Tree | 22 | `list.activeSelectionBackground`, `list.hoverBackground` |
| Tab | 17 | `tab.activeBackground`, `tab.border` |
| Sidebar | 7 | `sideBar.background` |
| Panel | 8 | `panel.background`, `panel.border` |
| Activity Bar | 8 | `activityBar.background` |
| Status Bar | 11 | `statusBar.background` |
| Title Bar | 5 | `titleBar.activeBackground` |
| Menu | 11 | `menu.background`, `menu.selectionBackground` |
| Scrollbar | 4 | `scrollbarSlider.background` |
| Misc | 8 | `progressBar.background` |
| Fonts | 14 | `font.default.family`, `font.editor.size` |

---

## Best Practices

### 1. Start with Built-in Themes

Always start by modifying a built-in theme rather than creating from scratch:

```python
# Good
base = app.get_current_theme()
custom = ThemeBuilder("custom").add_colors(base.colors)

# Less Good (more work)
custom = ThemeBuilder("custom")  # Start from scratch
```

### 2. Use Semantic Color Names

Define base colors first, then reference them:

```python
theme = (ThemeBuilder("semantic")
    # Define base colors
    .add_color("colors.primary", "#007acc")
    .add_color("colors.danger", "#dc3545")

    # Use semantic colors
    .add_color("button.background", "#007acc")  # Same as primary
    .add_color("button.danger.background", "#dc3545")  # Same as danger

    .build())
```

### 3. Test with All Widget Types

Make sure to test your theme with:
- Buttons (all roles)
- Text inputs
- Lists and trees
- Tables
- Tabs
- Menus
- Scrollbars

### 4. Consider Accessibility

- Ensure sufficient contrast (4.5:1 minimum for text)
- Test with colorblind simulators
- Provide high-contrast variant

### 5. Document Your Theme

```python
theme = (ThemeBuilder("my_theme")
    .add_metadata("description",
        "A custom theme inspired by X. "
        "Features high contrast and accessibility support."
    )
    # ... colors ...
    .build())
```

---

## Next Steps

- Check out [built-in themes](../src/vfwidgets_theme/widgets/application.py) for complete examples
- Read the [API Reference](api-REFERENCE.md) for detailed documentation
- Explore [examples](../examples/) to see themes in action
- Join the community to share your custom themes!

---

**Happy Theming!** 🎨
