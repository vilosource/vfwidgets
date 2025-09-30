# VSCode Theme Compatibility Specification

## Overview

The VFWidgets Theme System provides comprehensive compatibility with VSCode themes, allowing users to leverage the vast ecosystem of thousands of existing VSCode themes. This document specifies how VSCode themes are imported, mapped, and adapted for Qt/PySide6 applications.

## VSCode Theme Structure

### Standard VSCode Theme Format

```json
{
  "name": "Theme Name",
  "type": "dark" | "light",
  "colors": {
    // UI Colors - Application chrome
    "editor.background": "#1e1e1e",
    "editor.foreground": "#d4d4d4",
    "activityBar.background": "#333333",
    "sideBar.background": "#252526",
    "statusBar.background": "#007acc",
    // ... hundreds more
  },
  "tokenColors": [
    // Syntax highlighting rules
    {
      "name": "Comment",
      "scope": ["comment", "punctuation.definition.comment"],
      "settings": {
        "foreground": "#6A9955",
        "fontStyle": "italic"
      }
    }
    // ... many more
  ]
}
```

## Property Mapping

### Core UI Mappings

| VSCode Property | Qt/VFWidgets Property | Description |
|----------------|----------------------|-------------|
| `editor.background` | `window.background` | Main window background |
| `editor.foreground` | `window.foreground` | Default text color |
| `activityBar.background` | `sidebar.background` | Sidebar background |
| `activityBar.foreground` | `sidebar.foreground` | Sidebar text |
| `statusBar.background` | `statusBar.background` | Status bar background |
| `statusBar.foreground` | `statusBar.foreground` | Status bar text |
| `button.background` | `button.background` | Button background |
| `button.foreground` | `button.foreground` | Button text |
| `button.hoverBackground` | `button.hoverBackground` | Button hover state |
| `input.background` | `input.background` | Input field background |
| `input.foreground` | `input.foreground` | Input field text |
| `input.border` | `input.border` | Input field border |
| `list.activeSelectionBackground` | `list.selectedBackground` | Selected item background |
| `list.activeSelectionForeground` | `list.selectedForeground` | Selected item text |
| `list.hoverBackground` | `list.hoverBackground` | Hover item background |

### Extended Mappings

```python
VSCODE_TO_QT_MAP = {
    # Editor
    "editor.lineHighlightBackground": "editor.currentLineBackground",
    "editorLineNumber.foreground": "editor.lineNumberForeground",
    "editorCursor.foreground": "editor.cursorColor",
    "editor.selectionBackground": "editor.selectionBackground",

    # Terminal
    "terminal.background": "terminal.background",
    "terminal.foreground": "terminal.foreground",
    "terminal.ansiBlack": "terminal.black",
    "terminal.ansiRed": "terminal.red",
    "terminal.ansiGreen": "terminal.green",
    "terminal.ansiYellow": "terminal.yellow",
    "terminal.ansiBlue": "terminal.blue",
    "terminal.ansiMagenta": "terminal.magenta",
    "terminal.ansiCyan": "terminal.cyan",
    "terminal.ansiWhite": "terminal.white",

    # Tabs
    "tab.activeBackground": "tabs.activeBackground",
    "tab.inactiveBackground": "tabs.inactiveBackground",
    "tab.activeForeground": "tabs.activeForeground",
    "tab.border": "tabs.border",

    # Scrollbar
    "scrollbarSlider.background": "scrollbar.background",
    "scrollbarSlider.hoverBackground": "scrollbar.hoverBackground",
    "scrollbarSlider.activeBackground": "scrollbar.activeBackground",

    # Dropdown
    "dropdown.background": "comboBox.background",
    "dropdown.foreground": "comboBox.foreground",
    "dropdown.border": "comboBox.border",

    # Notifications
    "notificationCenter.background": "notification.background",
    "notificationCenter.foreground": "notification.foreground",
    "notificationCenter.border": "notification.border",

    # Errors/Warnings
    "editorError.foreground": "error.foreground",
    "editorWarning.foreground": "warning.foreground",
    "editorInfo.foreground": "info.foreground",

    # Git colors
    "gitDecoration.addedResourceForeground": "git.added",
    "gitDecoration.modifiedResourceForeground": "git.modified",
    "gitDecoration.deletedResourceForeground": "git.deleted",
    "gitDecoration.untrackedResourceForeground": "git.untracked",

    # Diff colors
    "diffEditor.insertedTextBackground": "diff.insertedBackground",
    "diffEditor.removedTextBackground": "diff.removedBackground",

    # Find/Search
    "editor.findMatchBackground": "search.matchBackground",
    "editor.findMatchHighlightBackground": "search.matchHighlightBackground",

    # Panels
    "panel.background": "panel.background",
    "panel.border": "panel.border",
    "panelTitle.activeForeground": "panel.titleForeground",

    # Peek View
    "peekView.border": "preview.border",
    "peekViewResult.background": "preview.background",
    "peekViewEditor.background": "preview.editorBackground",

    # Widgets
    "widget.shadow": "widget.shadow",
    "badge.background": "badge.background",
    "badge.foreground": "badge.foreground",
    "progressBar.background": "progressBar.background",

    # Menus
    "menu.background": "menu.background",
    "menu.foreground": "menu.foreground",
    "menu.selectionBackground": "menu.selectedBackground",
    "menubar.selectionBackground": "menuBar.selectedBackground"
}
```

## Color Format Conversion

### Supported Formats

VSCode themes may use various color formats that need conversion:

```python
# Input formats (VSCode)
"#RGB"          -> "#RRGGBB"      # 3-digit hex to 6-digit
"#RGBA"         -> "#RRGGBBAA"    # 4-digit hex to 8-digit
"#RRGGBB"       -> "#RRGGBB"      # 6-digit hex (no change)
"#RRGGBBAA"     -> "#RRGGBBAA"    # 8-digit hex with alpha
"rgb(r,g,b)"    -> "#RRGGBB"      # RGB function to hex
"rgba(r,g,b,a)" -> "#RRGGBBAA"    # RGBA function to hex
"transparent"   -> "#00000000"    # Named colors
```

### Alpha Channel Handling

Qt requires alpha channel in ARGB format while VSCode uses RGBA:

```python
def convert_vscode_to_qt_alpha(color: str) -> str:
    if len(color) == 9 and color.startswith("#"):
        # Convert #RRGGBBAA to Qt's #AARRGGBB
        return f"#{color[7:9]}{color[1:7]}"
    return color
```

## Token Colors (Syntax Highlighting)

### Scope Mapping

VSCode TextMate scopes map to Qt syntax highlighter categories:

| VSCode Scope | Qt Highlighter Category |
|-------------|------------------------|
| `comment` | `Comment` |
| `keyword` | `Keyword` |
| `string` | `String` |
| `constant.numeric` | `Number` |
| `entity.name.function` | `Function` |
| `entity.name.class` | `Class` |
| `variable` | `Variable` |
| `support.type` | `Type` |
| `constant.language` | `Constant` |
| `markup.heading` | `Heading` |

### Font Style Mapping

```python
FONT_STYLE_MAP = {
    "italic": QFont.StyleItalic,
    "bold": QFont.Bold,
    "underline": QFont.UnderlineStyle,
    "strikethrough": QFont.StrikeOut
}
```

## Import Process

### Step 1: Load and Parse

```python
def import_vscode_theme(file_path: str) -> Dict:
    with open(file_path, 'r') as f:
        vscode_theme = json.load(f)

    # Handle both .json and .tmTheme formats
    if file_path.endswith('.tmTheme'):
        vscode_theme = parse_tmtheme(vscode_theme)

    return vscode_theme
```

### Step 2: Map Properties

```python
def map_vscode_to_qt(vscode_theme: Dict) -> Dict:
    qt_theme = {
        "name": vscode_theme.get("name", "Imported Theme"),
        "type": vscode_theme.get("type", "dark"),
        "colors": {}
    }

    # Map UI colors
    for vscode_key, qt_key in VSCODE_TO_QT_MAP.items():
        if vscode_key in vscode_theme.get("colors", {}):
            color = vscode_theme["colors"][vscode_key]
            qt_theme["colors"][qt_key] = convert_color_format(color)

    return qt_theme
```

### Step 3: Generate Missing Properties

```python
def generate_missing_properties(theme: Dict) -> Dict:
    """Generate Qt-specific properties not in VSCode."""

    base_bg = theme["colors"].get("window.background", "#1e1e1e")
    base_fg = theme["colors"].get("window.foreground", "#d4d4d4")

    # Generate Qt-specific properties
    generated = {
        # QWidget defaults
        "widget.background": base_bg,
        "widget.foreground": base_fg,

        # QGroupBox
        "groupBox.border": lighten(base_bg, 20),
        "groupBox.title": base_fg,

        # QTabWidget (if not mapped)
        "tabWidget.pane": base_bg,
        "tabWidget.tab": darken(base_bg, 10),

        # QSlider
        "slider.groove": darken(base_bg, 20),
        "slider.handle": theme["colors"].get("button.background", "#0066cc"),

        # QProgressBar
        "progressBar.chunk": theme["colors"].get("progressBar.background",
                                                 "#0066cc"),

        # QToolTip
        "toolTip.background": lighten(base_bg, 10),
        "toolTip.foreground": base_fg,

        # QDockWidget
        "dock.background": theme["colors"].get("panel.background", base_bg),
        "dock.border": theme["colors"].get("panel.border", "#333333")
    }

    # Merge generated with existing
    for key, value in generated.items():
        if key not in theme["colors"]:
            theme["colors"][key] = value

    return theme
```

### Step 4: Validate and Optimize

```python
def validate_imported_theme(theme: Dict) -> ValidationResult:
    """Validate imported theme for Qt compatibility."""

    errors = []
    warnings = []

    # Check required properties
    required = ["window.background", "window.foreground",
                "button.background", "button.foreground"]

    for prop in required:
        if prop not in theme["colors"]:
            warnings.append(f"Missing required property: {prop}")

    # Validate color formats
    for key, color in theme["colors"].items():
        if not is_valid_qt_color(color):
            errors.append(f"Invalid color format for {key}: {color}")

    # Check contrast ratios
    bg = theme["colors"].get("window.background")
    fg = theme["colors"].get("window.foreground")
    if bg and fg:
        ratio = calculate_contrast_ratio(bg, fg)
        if ratio < 4.5:
            warnings.append(f"Low contrast ratio: {ratio:.2f}")

    return ValidationResult(errors, warnings)
```

## Marketplace Integration

### Fetching from VSCode Marketplace

```python
class VSCodeMarketplace:
    """Integration with VSCode Extension Marketplace."""

    API_URL = "https://marketplace.visualstudio.com/_apis/public/gallery"

    @classmethod
    def search_themes(cls, query: str) -> List[ThemeInfo]:
        """Search for themes in marketplace."""
        # Query marketplace API
        # Parse results
        # Return theme information

    @classmethod
    def download_theme(cls, extension_id: str) -> Theme:
        """Download and import theme from marketplace."""
        # Download extension package
        # Extract theme files
        # Import theme
        # Return Theme object
```

## Compatibility Levels

### Level 1: Full Compatibility
Themes that map perfectly to Qt with no missing properties.

### Level 2: High Compatibility
Themes with 90%+ property coverage, minor properties generated.

### Level 3: Good Compatibility
Themes with 70-90% coverage, some properties generated or approximated.

### Level 4: Basic Compatibility
Themes with <70% coverage, significant generation required.

## Known Limitations

### 1. Unsupported VSCode Features
- Semantic highlighting tokens
- Language-specific color customizations
- Bracket pair colorization
- Indent guides with gradients

### 2. Qt-Specific Limitations
- No direct equivalent for some VSCode UI elements
- Different widget hierarchy requires approximation
- Style sheet limitations vs CSS

### 3. Color Space Differences
- VSCode uses sRGB, Qt may use device RGB
- Alpha compositing differences
- Gradient rendering variations

## Extension Mechanism

### Custom Mappers

```python
class CustomVSCodeMapper:
    """Override default mapping behavior."""

    def map_property(self, vscode_key: str, vscode_value: str) -> Tuple[str, str]:
        """Custom property mapping logic."""
        # Custom mapping implementation
        return qt_key, qt_value

    def post_process(self, theme: Theme) -> Theme:
        """Post-process imported theme."""
        # Additional processing
        return theme
```

### Theme Transformers

```python
class VSCodeThemeTransformer:
    """Transform VSCode themes during import."""

    def transform_colors(self, colors: Dict) -> Dict:
        """Transform color properties."""
        pass

    def transform_tokens(self, tokens: List) -> List:
        """Transform token colors."""
        pass
```

## Testing Compatibility

### Compatibility Test Suite

```python
class VSCodeCompatibilityTest:
    """Test VSCode theme compatibility."""

    def test_property_coverage(self, theme: Theme) -> float:
        """Calculate property coverage percentage."""
        pass

    def test_color_accuracy(self, original: Dict, imported: Theme) -> float:
        """Test color conversion accuracy."""
        pass

    def test_visual_similarity(self, vscode_screenshot: Image,
                              qt_screenshot: Image) -> float:
        """Compare visual similarity."""
        pass
```

## Best Practices

### For Theme Authors
1. Include all standard VSCode properties
2. Use hex colors for better compatibility
3. Test in both VSCode and VFWidgets
4. Document any custom properties

### For Importers
1. Always validate imported themes
2. Generate missing properties sensibly
3. Preserve theme metadata
4. Handle edge cases gracefully

## Future Enhancements

### Planned Features
1. Live sync with VSCode settings
2. Automatic theme updates from marketplace
3. AI-based property inference
4. Visual theme comparison tool
5. Theme compatibility analyzer
6. Batch import tool for theme packs

---

*For implementation details, see the [API Reference](api-REFERENCE.md) and [Architecture Design](architecture-DESIGN.md).*