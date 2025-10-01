# Theme Customization Guide

Learn how to create and customize themes for your PySide6 applications.

---

## Table of Contents

1. [Creating a Simple Theme](#creating-a-simple-theme)
2. [Understanding Theme Tokens](#understanding-theme-tokens)
3. [Using ThemeBuilder](#using-themebuilder)
4. [Complete Theme Example](#complete-theme-example)
5. [Loading Custom Themes](#loading-custom-themes)
6. [Modifying Built-in Themes](#modifying-built-in-themes)
7. [Theme Token Reference](#theme-token-reference)

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
    .add_font("font.default.family", "Arial, sans-serif")
    .add_font("font.default.size", "9pt")
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

## Using ThemeBuilder

`ThemeBuilder` provides a fluent API for creating themes:

### Basic Theme

```python
from vfwidgets_theme.core.theme import ThemeBuilder

theme = (ThemeBuilder("my_simple_theme")
    .set_type("dark")
    .set_description("My first custom theme")
    .add_color("colors.foreground", "#ffffff")
    .add_color("colors.background", "#1e1e1e")
    .build())
```

### Comprehensive Theme

```python
theme = (ThemeBuilder("my_comprehensive_theme")
    .set_type("dark")
    .set_description("A complete custom theme")

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
    .add_font("font.default.family", "Segoe UI, Arial, sans-serif")
    .add_font("font.default.size", "9pt")
    .add_font("font.editor.family", "Courier New, Consolas, monospace")
    .add_font("font.editor.size", "11pt")

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
    .set_description("A beautiful purple theme")

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
    .add_font("font.default.family", "Segoe UI, Arial, sans-serif")
    .add_font("font.default.size", "9pt")
    .add_font("font.editor.family", "Courier New, Consolas, monospace")
    .add_font("font.editor.size", "11pt")
    .add_font("font.button.family", "Segoe UI, Arial, sans-serif")
    .add_font("font.button.size", "9pt")

    .build())


def main():
    """Run the purple-themed application."""
    app = ThemedApplication(sys.argv)

    # Add custom theme to application
    app._available_themes["purple_dream"] = purple_theme
    app._theme_manager.add_theme(purple_theme)

    # Set the purple theme
    app.set_theme("purple_dream")

    # Create window
    window = ThemedMainWindow()
    window.setWindowTitle("Purple Dream Theme")
    window.setMinimumSize(500, 400)

    # Create UI
    central = window.create_central_widget()
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

### Method 1: Add to ThemedApplication

```python
from vfwidgets_theme import ThemedApplication
from vfwidgets_theme.core.theme import ThemeBuilder

app = ThemedApplication(sys.argv)

# Create custom theme
my_theme = (ThemeBuilder("custom")
    # ... theme definition ...
    .build())

# Add to application
app._available_themes["custom"] = my_theme
app._theme_manager.add_theme(my_theme)

# Use it
app.set_theme("custom")
```

### Method 2: Save to JSON and Load

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

# Load from JSON (later)
theme_data = json.loads(Path("my_theme.json").read_text())

loaded_theme = (ThemeBuilder(theme_data["name"])
    .set_type(theme_data["type"])
    .add_colors(theme_data["colors"])
    .build())
```

---

## Modifying Built-in Themes

### Override Specific Colors

```python
from vfwidgets_theme import ThemedApplication
from vfwidgets_theme.core.theme import ThemeBuilder

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

# Use it
app._available_themes["vscode_custom"] = custom_theme
app._theme_manager.add_theme(custom_theme)
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
    .add_font("font.default.family", "Arial, sans-serif")
    .add_font("font.default.size", "9pt")

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
    .set_description(
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
