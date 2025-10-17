# MarkdownViewer Theme Tokens Reference

**Version:** 3.0
**Date:** 2025-10-16
**Widget:** MarkdownViewer
**Package:** vfwidgets_markdown
**Pattern:** Hierarchical token resolution with widget-specific namespace

## Overview

The MarkdownViewer widget uses a **hierarchical token resolution system** similar to the terminal widget. This allows themes to customize markdown rendering specifically using `markdown.colors.*` tokens, while falling back to generic tokens if markdown-specific ones aren't defined.

## Hierarchical Token Resolution

The widget uses a **three-tier fallback system**:

1. **Widget-specific tokens** (`markdown.colors.*`) - Highest priority
2. **Generic tokens** (`editor.*`, `input.*`, etc.) - Fallback
3. **Base tokens** (`colors.*`) - Ultimate fallback

This pattern allows:
- Theme designers to create markdown-specific color schemes
- Backward compatibility with existing themes
- Graceful degradation when tokens are missing

## Theme Token Mappings

The `theme_config` dictionary defines primary tokens with automatic fallbacks:

```python
theme_config = {
    "md_bg": "markdown.colors.background",           # → editor.background → colors.background
    "md_fg": "markdown.colors.foreground",           # → editor.foreground → colors.foreground
    "md_link": "markdown.colors.link",               # → button.background → colors.foreground
    "md_code_bg": "markdown.colors.code.background", # → input.background → widget.background
    "md_code_fg": "markdown.colors.code.foreground", # → input.foreground → colors.foreground
    "md_blockquote_border": "markdown.colors.blockquote.border",       # → widget.border → colors.border
    "md_blockquote_bg": "markdown.colors.blockquote.background",       # → widget.background → editor.background
    "md_table_border": "markdown.colors.table.border",                 # → widget.border → colors.border
    "md_table_header_bg": "markdown.colors.table.headerBackground",    # → editor.lineHighlightBackground → widget.background
    "md_scrollbar_bg": "markdown.colors.scrollbar.background",         # → editor.background → colors.background
    "md_scrollbar_thumb": "markdown.colors.scrollbar.thumb",           # → scrollbar.activeBackground → widget.border
    "md_scrollbar_thumb_hover": "markdown.colors.scrollbar.thumbHover", # → scrollbar.hoverBackground → scrollbar.activeBackground
}
```

## Token Details

### Content Tokens

| CSS Variable | Primary Token | Fallback Chain | Purpose |
|-------------|---------------|----------------|---------|
| `--md-bg` | `markdown.colors.background` | → `editor.background` → `colors.background` | Main background color |
| `--md-fg` | `markdown.colors.foreground` | → `editor.foreground` → `colors.foreground` | Main text color |
| `--md-link` | `markdown.colors.link` | → `button.background` → `colors.foreground` | Link color |

**Token Resolution:**
- **Primary**: `markdown.colors.*` tokens allow theme-specific markdown customization
- **Fallback**: Generic editor/button tokens provide sensible defaults
- **Base**: `colors.*` tokens ensure something always renders

### Code Block Tokens

| CSS Variable | Primary Token | Fallback Chain | Purpose |
|-------------|---------------|----------------|---------|
| `--md-code-bg` | `markdown.colors.code.background` | → `input.background` → `widget.background` | Code block background |
| `--md-code-fg` | `markdown.colors.code.foreground` | → `input.foreground` → `colors.foreground` | Code text color |

**Token Resolution:**
- **Primary**: `markdown.colors.code.*` allows custom code block styling
- **Fallback**: Input colors provide good contrast for monospace content
- Distinguishes code from regular text while remaining readable

### UI Element Tokens

| CSS Variable | Primary Token | Fallback Chain | Purpose |
|-------------|---------------|----------------|---------|
| `--md-blockquote-border` | `markdown.colors.blockquote.border` | → `widget.border` → `colors.border` | Blockquote left border |
| `--md-blockquote-bg` | `markdown.colors.blockquote.background` | → `widget.background` → `editor.background` | Blockquote background |
| `--md-table-border` | `markdown.colors.table.border` | → `widget.border` → `colors.border` | Table cell borders |
| `--md-table-header-bg` | `markdown.colors.table.headerBackground` | → `editor.lineHighlightBackground` → `widget.background` | Table header background |

**Token Resolution:**
- **Primary**: `markdown.colors.blockquote.*` and `markdown.colors.table.*` allow precise control
- **Fallback**: Widget tokens provide subtle UI element styling
- Line highlight for table headers creates visual hierarchy

### Scrollbar Tokens

| CSS Variable | Primary Token | Fallback Chain | Purpose |
|-------------|---------------|----------------|---------|
| `--md-scrollbar-bg` | `markdown.colors.scrollbar.background` | → `editor.background` → `colors.background` | Scrollbar track |
| `--md-scrollbar-thumb` | `markdown.colors.scrollbar.thumb` | → `scrollbar.activeBackground` → `widget.border` | Scrollbar thumb |
| `--md-scrollbar-thumb-hover` | `markdown.colors.scrollbar.thumbHover` | → `scrollbar.hoverBackground` → `scrollbar.activeBackground` | Thumb hover state |

**Token Resolution:**
- **Primary**: `markdown.colors.scrollbar.*` allows custom scrollbar styling
- **Fallback**: Standard scrollbar tokens ensure consistency with other scrollable widgets
- Hover states provide interactive feedback

## CSS Variable Usage

These tokens are injected into the viewer's HTML as CSS variables. The viewer's CSS stylesheet references them like this:

```css
body {
    color: var(--md-fg, #c9d1d9);
    background-color: var(--md-bg, #0d1117);
}

a {
    color: var(--md-link, #58a6ff);
}

code {
    background-color: var(--md-code-bg, #161b22);
    color: var(--md-code-fg, #e6edf3);
}

blockquote {
    border-left-color: var(--md-blockquote-border, #3b434b);
    background-color: var(--md-blockquote-bg, rgba(110, 118, 129, 0.1));
}

table {
    border-color: var(--md-table-border, #30363d);
}

th {
    background-color: var(--md-table-header-bg, #161b22);
}

::-webkit-scrollbar {
    background-color: var(--md-scrollbar-bg, #0d1117);
}

::-webkit-scrollbar-thumb {
    background-color: var(--md-scrollbar-thumb, #484f58);
}

::-webkit-scrollbar-thumb:hover {
    background-color: var(--md-scrollbar-thumb-hover, #6e7681);
}
```

## Theme Studio Integration

The widget declares all markdown-specific tokens in its metadata:

```python
# Required tokens (must exist in theme)
theme_tokens = {
    "background": "colors.background",
    "foreground": "colors.foreground",
}

# Optional tokens (used if defined, fallback otherwise)
optional_tokens = [
    # Widget-specific markdown tokens (primary)
    "markdown.colors.background",
    "markdown.colors.foreground",
    "markdown.colors.link",
    "markdown.colors.code.background",
    "markdown.colors.code.foreground",
    "markdown.colors.blockquote.border",
    "markdown.colors.blockquote.background",
    "markdown.colors.table.border",
    "markdown.colors.table.headerBackground",
    "markdown.colors.scrollbar.background",
    "markdown.colors.scrollbar.thumb",
    "markdown.colors.scrollbar.thumbHover",
    # Fallback tokens (used if markdown.* not defined)
    "editor.background",
    "editor.foreground",
    "button.background",
    "input.background",
    "input.foreground",
    "widget.border",
    "widget.background",
    "editor.lineHighlightBackground",
    "scrollbar.activeBackground",
    "scrollbar.hoverBackground",
]
```

**Theme Studio Features:**
- **Widget Filter**: Shows all 24 tokens (12 markdown-specific + 12 fallback) when markdown widget is selected
- **Token Browser**: Displays both `markdown.colors.*` and fallback tokens for complete theme design
- **Live Preview**: Theme changes apply immediately to the markdown preview

The full token mapping in `theme_config` is applied at runtime via `on_theme_changed()`.

## Required vs Optional Tokens

**Required Tokens (must exist):**
- `colors.background` - Ultimate fallback for all background colors
- `colors.foreground` - Ultimate fallback for all text colors

**Widget-Specific Tokens (highest priority if defined):**
- `markdown.colors.background` - Markdown-specific background
- `markdown.colors.foreground` - Markdown-specific text color
- `markdown.colors.link` - Link color for markdown
- `markdown.colors.code.background` - Code block background
- `markdown.colors.code.foreground` - Code text color
- `markdown.colors.blockquote.border` - Blockquote border color
- `markdown.colors.blockquote.background` - Blockquote background
- `markdown.colors.table.border` - Table border color
- `markdown.colors.table.headerBackground` - Table header background
- `markdown.colors.scrollbar.background` - Scrollbar track
- `markdown.colors.scrollbar.thumb` - Scrollbar thumb
- `markdown.colors.scrollbar.thumbHover` - Scrollbar thumb hover

**Fallback Tokens (used if markdown.* not defined):**
- `editor.background`, `editor.foreground` - For content area
- `button.background` - For links
- `input.background`, `input.foreground` - For code blocks
- `widget.border`, `widget.background` - For UI elements
- `editor.lineHighlightBackground` - For table headers
- `scrollbar.activeBackground`, `scrollbar.hoverBackground` - For scrollbars

**Resolution Order:**
1. Try `markdown.colors.*` token (widget-specific)
2. Try fallback token (generic)
3. Try `colors.*` token (base)
4. Use CSS hardcoded fallback if all fail

## Customizing Theme Tokens

### For Theme Designers

You have three levels of customization:

**Level 1: Use existing theme (no changes needed)**
- Widget uses fallback tokens automatically
- Works with any VSCode-compatible theme

**Level 2: Customize generic tokens (affects all widgets)**
```json
{
  "colors": {
    "editor.background": "#1a1a1a",
    "editor.foreground": "#d4d4d4",
    "button.background": "#0066cc",
    "input.background": "#2d2d30",
    "input.foreground": "#cccccc"
  }
}
```

**Level 3: Markdown-specific customization (recommended)**
```json
{
  "colors": {
    "markdown.colors.background": "#1a1a1a",
    "markdown.colors.foreground": "#d4d4d4",
    "markdown.colors.link": "#0066cc",
    "markdown.colors.code.background": "#2d2d30",
    "markdown.colors.code.foreground": "#cccccc",
    "markdown.colors.blockquote.border": "#454545",
    "markdown.colors.blockquote.background": "#2a2a2a",
    "markdown.colors.table.border": "#454545",
    "markdown.colors.table.headerBackground": "#2d2d30",
    "markdown.colors.scrollbar.background": "#1a1a1a",
    "markdown.colors.scrollbar.thumb": "#454545",
    "markdown.colors.scrollbar.thumbHover": "#555555"
  }
}
```

**Best Practice**: Define markdown-specific tokens for precise control while keeping fallback tokens for backward compatibility

### For Widget Developers

To modify the token mappings:

1. Edit `theme_config` in `markdown_viewer.py`
2. Update the CSS variables in `viewer.css`
3. Test with multiple themes to ensure proper contrast

## Design Rationale

### Why Hierarchical Resolution?

The hierarchical token system provides the best of both worlds:

**Backward Compatibility:**
- Existing themes work without modification
- Fallback to generic tokens ensures rendering
- No breaking changes for theme designers

**Precise Control:**
- Theme designers can customize markdown specifically
- `markdown.colors.*` namespace prevents conflicts
- Matches terminal_widget pattern for consistency

**Graceful Degradation:**
- Three-tier fallback ensures something always renders
- CSS hardcoded values as final fallback
- No blank or broken rendering

### Why These Fallback Tokens?

**For content (`editor.*`):**
- Provides consistency with code editors
- Well-tested color combinations
- Good contrast and readability

**For code (`input.*`):**
- Distinguishes code from regular text
- Monospace-friendly contrast
- Matches form input styling

**For UI elements (`widget.*`):**
- Subtle, non-intrusive styling
- Consistent with other UI widgets
- Platform-appropriate appearance

**For links (`button.*`):**
- Uses accent color scheme
- Visually distinct from body text
- Maintains visual hierarchy

### Pattern Consistency

This widget follows the same pattern as `terminal_widget`:
- Widget-specific namespace (`markdown.colors.*` / `terminal.colors.*`)
- Hierarchical fallback resolution
- Metadata declares all tokens for Theme Studio
- Backward compatible with existing themes

## Examples

### Example 1: Generic Tokens Only (Backward Compatible)

```json
{
  "colors": {
    "editor.background": "#1a1a1a",
    "editor.foreground": "#d4d4d4",
    "button.background": "#0e639c",
    "input.background": "#3c3c3c",
    "widget.border": "#3c3c3c"
  }
}
```

**Resolution:**
- Background: `editor.background` (#1a1a1a)
- Foreground: `editor.foreground` (#d4d4d4)
- Links: `button.background` (#0e639c)
- Code: `input.background` (#3c3c3c)

**Result:** Dark background, light text, blue links, dark gray code blocks

### Example 2: Markdown-Specific Customization

```json
{
  "colors": {
    "markdown.colors.background": "#0d1117",
    "markdown.colors.foreground": "#c9d1d9",
    "markdown.colors.link": "#58a6ff",
    "markdown.colors.code.background": "#161b22",
    "markdown.colors.code.foreground": "#e6edf3",
    "markdown.colors.blockquote.border": "#3b434b",
    "markdown.colors.blockquote.background": "rgba(110, 118, 129, 0.1)",
    "markdown.colors.table.border": "#30363d",
    "markdown.colors.table.headerBackground": "#161b22"
  }
}
```

**Resolution:**
- All tokens use `markdown.colors.*` (no fallback needed)
- Custom GitHub-dark inspired markdown theme
- Different from application's generic editor theme

**Result:** GitHub-dark markdown styling, independent of editor theme

### Example 3: Mixed Approach

```json
{
  "colors": {
    "editor.background": "#ffffff",
    "editor.foreground": "#000000",
    "markdown.colors.link": "#0066cc",
    "markdown.colors.code.background": "#f6f8fa"
  }
}
```

**Resolution:**
- Background: `editor.background` (#ffffff) - uses fallback
- Foreground: `editor.foreground` (#000000) - uses fallback
- Links: `markdown.colors.link` (#0066cc) - uses markdown-specific
- Code: `markdown.colors.code.background` (#f6f8fa) - uses markdown-specific

**Result:** Custom link and code styling, generic background/foreground

## See Also

- [Theme Integration Guide](theme-integration-GUIDE.md) - Comprehensive guide on theme system integration
- [MarkdownViewer API](API.md) - Full widget API documentation
- [VSCode Theme Specification](https://code.visualstudio.com/api/references/theme-color) - Standard theme token reference
