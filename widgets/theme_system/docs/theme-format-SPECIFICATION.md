# Theme Format Specification - VFWidgets Theme System

## Version 1.0

This specification defines the JSON format for VFWidgets themes, including structure, properties, validation rules, and extension mechanisms.

## Basic Structure

```json
{
  "$schema": "https://vfwidgets.org/schemas/theme-v1.json",
  "name": "Theme Name",
  "type": "dark" | "light",
  "version": "1.0.0",
  "colors": {
    // Color definitions
  },
  "tokenColors": [
    // Syntax highlighting rules
  ],
  "metadata": {
    // Theme metadata
  },
  "extends": "parent-theme-name",
  "qt": {
    // Qt-specific overrides
  }
}
```

## Root Properties

### Required Properties

#### `name` (string, required)
Display name of the theme.
- Must be 1-100 characters
- Unicode allowed
- Example: `"Dark Modern"`

#### `type` (enum, required)
Theme type for system integration.
- Values: `"dark"` | `"light"`
- Used for system theme matching

#### `colors` (object, required)
Color definitions using property paths as keys.
- At minimum must include base colors
- Values must be valid color strings

### Optional Properties

#### `version` (string)
Theme version following semantic versioning.
- Format: `"MAJOR.MINOR.PATCH"`
- Example: `"1.2.3"`

#### `extends` (string)
Parent theme to inherit from.
- Must reference an available theme
- Child properties override parent

#### `tokenColors` (array)
Syntax highlighting rules for code editors.
- Array of TokenColor objects
- Used by syntax highlighters

#### `metadata` (object)
Additional theme information.
- Author, description, license, etc.

#### `qt` (object)
Qt-specific style overrides.
- Raw QSS properties
- Widget-specific customizations

## Color Properties

### Color Format

Colors can be specified in these formats:

```json
{
  "colors": {
    // Hex formats
    "color1": "#RGB",          // 3-digit hex
    "color2": "#RRGGBB",       // 6-digit hex
    "color3": "#RRGGBBAA",     // 8-digit hex with alpha

    // RGB/RGBA functions
    "color4": "rgb(255, 0, 0)",
    "color5": "rgba(255, 0, 0, 0.5)",

    // HSL/HSLA functions
    "color6": "hsl(0, 100%, 50%)",
    "color7": "hsla(0, 100%, 50%, 0.5)",

    // Named colors
    "color8": "transparent",
    "color9": "currentColor",

    // References
    "color10": "@window.background",  // Reference another property
    "color11": "lighten(@window.background, 10%)",  // Color function
  }
}
```

### Core Color Properties

#### Window Colors
```json
{
  "window.background": "#1e1e1e",
  "window.foreground": "#d4d4d4",
  "window.border": "#333333",
  "window.activeBorder": "#0066cc",
  "window.inactiveBorder": "#555555"
}
```

#### Widget Colors
```json
{
  "widget.background": "#252526",
  "widget.foreground": "#cccccc",
  "widget.border": "#3c3c3c",
  "widget.shadow": "rgba(0, 0, 0, 0.25)"
}
```

#### Button Colors
```json
{
  "button.background": "#0e639c",
  "button.foreground": "#ffffff",
  "button.hoverBackground": "#1177bb",
  "button.activeBackground": "#005a9e",
  "button.disabledBackground": "#555555",
  "button.border": "transparent"
}
```

#### Input Colors
```json
{
  "input.background": "#3c3c3c",
  "input.foreground": "#cccccc",
  "input.border": "#555555",
  "input.focusBorder": "#0066cc",
  "input.placeholderForeground": "#999999",
  "input.selectionBackground": "#264f78"
}
```

#### List/Tree Colors
```json
{
  "list.background": "#1e1e1e",
  "list.foreground": "#d4d4d4",
  "list.hoverBackground": "#2a2d2e",
  "list.selectedBackground": "#094771",
  "list.selectedForeground": "#ffffff",
  "list.inactiveSelectedBackground": "#37373d",
  "list.focusOutline": "#0066cc"
}
```

#### Editor Colors
```json
{
  "editor.background": "#1e1e1e",
  "editor.foreground": "#d4d4d4",
  "editor.lineHighlightBackground": "#282828",
  "editor.selectionBackground": "#264f78",
  "editor.cursorForeground": "#aeafad",
  "editor.findMatchBackground": "#515c6a",
  "editor.findMatchHighlightBackground": "#ea5c0055"
}
```

#### Status Colors
```json
{
  "error.foreground": "#f48771",
  "error.background": "#f4877133",
  "warning.foreground": "#cca700",
  "warning.background": "#cca70033",
  "success.foreground": "#89d185",
  "success.background": "#89d18533",
  "info.foreground": "#75beff",
  "info.background": "#75beff33"
}
```

### Component-Specific Colors

#### Terminal Colors
```json
{
  "terminal.background": "#1e1e1e",
  "terminal.foreground": "#cccccc",
  "terminal.ansiBlack": "#000000",
  "terminal.ansiRed": "#cd3131",
  "terminal.ansiGreen": "#0dbc79",
  "terminal.ansiYellow": "#e5e510",
  "terminal.ansiBlue": "#2472c8",
  "terminal.ansiMagenta": "#bc3fbc",
  "terminal.ansiCyan": "#11a8cd",
  "terminal.ansiWhite": "#e5e5e5",
  "terminal.ansiBrightBlack": "#666666",
  "terminal.ansiBrightRed": "#f14c4c",
  "terminal.ansiBrightGreen": "#23d18b",
  "terminal.ansiBrightYellow": "#f5f543",
  "terminal.ansiBrightBlue": "#3b8eea",
  "terminal.ansiBrightMagenta": "#d670d6",
  "terminal.ansiBrightCyan": "#29b8db",
  "terminal.ansiBrightWhite": "#ffffff"
}
```

#### Tab Colors
```json
{
  "tabs.background": "#2d2d30",
  "tabs.activeBackground": "#1e1e1e",
  "tabs.inactiveBackground": "#2d2d30",
  "tabs.activeForeground": "#ffffff",
  "tabs.inactiveForeground": "#969696",
  "tabs.border": "#252526",
  "tabs.activeBorder": "#0066cc"
}
```

## Token Colors (Syntax Highlighting)

```json
{
  "tokenColors": [
    {
      "name": "Comment",
      "scope": ["comment", "punctuation.definition.comment"],
      "settings": {
        "foreground": "#6A9955",
        "fontStyle": "italic"
      }
    },
    {
      "name": "Keyword",
      "scope": ["keyword", "storage.type", "storage.modifier"],
      "settings": {
        "foreground": "#569CD6",
        "fontStyle": "bold"
      }
    },
    {
      "name": "String",
      "scope": ["string", "string.quoted"],
      "settings": {
        "foreground": "#CE9178"
      }
    }
  ]
}
```

### Token Color Properties

- `name`: Display name for the rule
- `scope`: Array of TextMate scope selectors
- `settings`: Style settings
  - `foreground`: Text color
  - `background`: Background color (rarely used)
  - `fontStyle`: `"italic"`, `"bold"`, `"underline"`, `"strikethrough"`

## Metadata

```json
{
  "metadata": {
    "author": "Author Name",
    "description": "A modern dark theme",
    "homepage": "https://example.com",
    "repository": "https://github.com/user/theme",
    "license": "MIT",
    "keywords": ["dark", "modern", "minimal"],
    "compatibleWith": ["vfwidgets>=1.0.0"],
    "screenshots": [
      "https://example.com/screenshot1.png"
    ]
  }
}
```

## Qt-Specific Properties

```json
{
  "qt": {
    // Global QSS overrides
    "global": {
      "QWidget": {
        "font-family": "Segoe UI",
        "font-size": "12px"
      }
    },

    // Widget-specific styles
    "widgets": {
      "QPushButton": {
        "border-radius": "4px",
        "padding": "6px 12px",
        "min-width": "80px"
      },
      "QLineEdit": {
        "border-radius": "2px",
        "padding": "4px 8px"
      }
    },

    // Custom properties
    "custom": {
      "borderRadius.small": "2px",
      "borderRadius.medium": "4px",
      "borderRadius.large": "8px",
      "spacing.small": "4px",
      "spacing.medium": "8px",
      "spacing.large": "16px"
    }
  }
}
```

## Color Functions

Themes support color manipulation functions:

```json
{
  "colors": {
    "hover.background": "lighten(@window.background, 10%)",
    "active.background": "darken(@window.background, 10%)",
    "disabled.foreground": "opacity(@window.foreground, 0.5)",
    "accent.light": "saturate(@accent.primary, 20%)",
    "accent.dark": "desaturate(@accent.primary, 20%)",
    "border": "mix(@window.background, @window.foreground, 20%)"
  }
}
```

### Available Functions

- `lighten(color, amount)`: Lighten by percentage
- `darken(color, amount)`: Darken by percentage
- `opacity(color, alpha)`: Set opacity (0.0 - 1.0)
- `saturate(color, amount)`: Increase saturation
- `desaturate(color, amount)`: Decrease saturation
- `mix(color1, color2, weight)`: Mix two colors
- `complement(color)`: Get complementary color
- `invert(color)`: Invert color
- `grayscale(color)`: Convert to grayscale

## Theme Inheritance

```json
{
  "name": "My Custom Dark",
  "extends": "dark-modern",
  "type": "dark",
  "colors": {
    // Only specify overrides
    "accent.primary": "#00ff00",
    "button.background": "#00aa00"
  }
}
```

### Inheritance Rules

1. Child inherits all parent properties
2. Child properties override parent properties
3. Deep merge for nested objects
4. Arrays are replaced, not merged
5. Maximum inheritance depth: 5 levels

## Validation Rules

### Required Minimum Properties

```json
{
  "name": "Minimum Valid Theme",
  "type": "dark",
  "colors": {
    "window.background": "#1e1e1e",
    "window.foreground": "#d4d4d4",
    "widget.background": "#252526",
    "widget.foreground": "#cccccc",
    "button.background": "#0066cc",
    "button.foreground": "#ffffff"
  }
}
```

### Validation Checks

1. **Structure**: Valid JSON format
2. **Required Fields**: name, type, colors
3. **Color Format**: Valid color strings
4. **Contrast**: Readable text/background combinations
5. **Completeness**: Core properties present
6. **References**: Valid property references
7. **Inheritance**: Parent theme exists

## Schema Definition

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["name", "type", "colors"],
  "properties": {
    "name": {
      "type": "string",
      "minLength": 1,
      "maxLength": 100
    },
    "type": {
      "type": "string",
      "enum": ["dark", "light"]
    },
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$"
    },
    "colors": {
      "type": "object",
      "additionalProperties": {
        "type": "string"
      }
    },
    "tokenColors": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["scope", "settings"],
        "properties": {
          "name": {"type": "string"},
          "scope": {
            "oneOf": [
              {"type": "string"},
              {"type": "array", "items": {"type": "string"}}
            ]
          },
          "settings": {
            "type": "object",
            "properties": {
              "foreground": {"type": "string"},
              "background": {"type": "string"},
              "fontStyle": {"type": "string"}
            }
          }
        }
      }
    },
    "extends": {
      "type": "string"
    },
    "metadata": {
      "type": "object"
    },
    "qt": {
      "type": "object"
    }
  }
}
```

## File Naming Convention

- Theme files should use `.json` extension
- Naming pattern: `[type]-[name]-theme.json`
- Examples:
  - `dark-modern-theme.json`
  - `light-default-theme.json`
  - `high-contrast-dark-theme.json`

## Versioning

Themes follow semantic versioning:
- **MAJOR**: Breaking changes to property structure
- **MINOR**: New properties added (backward compatible)
- **PATCH**: Color adjustments, bug fixes

## Future Extensions

### Planned Features (v2.0)

1. **Conditional Properties**: Time-based, OS-based conditions
2. **Animation Properties**: Transition timings and effects
3. **Gradient Definitions**: Complex gradient support
4. **Variable Definitions**: CSS-style custom properties
5. **Media Queries**: Responsive theme properties
6. **Theme Variants**: Multiple variants in single file

---

*For implementation details, see the [Developer Guide](developer-GUIDE.md) and [API Reference](api-REFERENCE.md).*