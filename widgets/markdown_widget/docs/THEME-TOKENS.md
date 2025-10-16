# MarkdownViewer Theme Tokens Reference

**Version:** 2.0
**Date:** 2025-10-16
**Widget:** MarkdownViewer
**Package:** vfwidgets_markdown

## Overview

The MarkdownViewer widget integrates with the VFWidgets theme system to provide automatic theming of markdown content. This document lists all theme tokens used by the widget and how they map to visual elements.

## Theme Token Mappings

The `theme_config` dictionary defines how theme tokens are applied to the markdown viewer:

```python
theme_config = {
    "md_bg": "editor.background",
    "md_fg": "editor.foreground",
    "md_link": "button.background",
    "md_code_bg": "input.background",
    "md_code_fg": "input.foreground",
    "md_blockquote_border": "widget.border",
    "md_blockquote_bg": "widget.background",
    "md_table_border": "widget.border",
    "md_table_header_bg": "editor.lineHighlightBackground",
    "md_scrollbar_bg": "editor.background",
    "md_scrollbar_thumb": "scrollbar.activeBackground",
    "md_scrollbar_thumb_hover": "scrollbar.hoverBackground",
}
```

## Token Details

### Content Tokens

| CSS Variable | Theme Token | Purpose | Example Usage |
|-------------|-------------|---------|---------------|
| `--md-bg` | `editor.background` | Main background color | Body background, content area |
| `--md-fg` | `editor.foreground` | Main text color | Paragraph text, headings, lists |
| `--md-link` | `button.background` | Link color | Hyperlinks, anchor elements |

**Why these tokens?**
- `editor.background/foreground`: Provides consistency with code editors and text areas
- `button.background` for links: Uses the accent color scheme, making links visually distinct

### Code Block Tokens

| CSS Variable | Theme Token | Purpose | Example Usage |
|-------------|-------------|---------|---------------|
| `--md-code-bg` | `input.background` | Code block background | Inline code, code fences |
| `--md-code-fg` | `input.foreground` | Code text color | Code content |

**Why these tokens?**
- Input colors provide good contrast for monospace content
- Distinguishes code from regular text while remaining readable

### UI Element Tokens

| CSS Variable | Theme Token | Purpose | Example Usage |
|-------------|-------------|---------|---------------|
| `--md-blockquote-border` | `widget.border` | Blockquote left border | > quoted text |
| `--md-blockquote-bg` | `widget.background` | Blockquote background | Quote background area |
| `--md-table-border` | `widget.border` | Table cell borders | Grid lines in tables |
| `--md-table-header-bg` | `editor.lineHighlightBackground` | Table header background | Header row background |

**Why these tokens?**
- Widget tokens provide subtle UI element styling
- Line highlight for table headers creates visual hierarchy

### Scrollbar Tokens

| CSS Variable | Theme Token | Purpose | Example Usage |
|-------------|-------------|---------|---------------|
| `--md-scrollbar-bg` | `editor.background` | Scrollbar track | Background of scroll area |
| `--md-scrollbar-thumb` | `scrollbar.activeBackground` | Scrollbar thumb | Draggable scroll indicator |
| `--md-scrollbar-thumb-hover` | `scrollbar.hoverBackground` | Thumb on hover | Interactive feedback |

**Why these tokens?**
- Standard scrollbar tokens ensure consistency with other scrollable widgets
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

For Theme Studio plugin integration, the widget declares only base tokens to pass validation:

```python
theme_tokens = {
    "background": "colors.background",
    "foreground": "colors.foreground",
}
```

The full token mapping in `theme_config` is applied at runtime via `on_theme_changed()`.

## Required vs Optional Tokens

**Required Tokens:**
- `colors.background` - Base background (used if editor.background not available)
- `colors.foreground` - Base foreground (used if editor.foreground not available)

**Optional Tokens** (all others):
- `editor.background`
- `editor.foreground`
- `button.background`
- `input.background`
- `input.foreground`
- `widget.border`
- `widget.background`
- `editor.lineHighlightBackground`
- `scrollbar.activeBackground`
- `scrollbar.hoverBackground`

If optional tokens are not defined in the theme, CSS fallback values (shown in the CSS examples above) are used.

## Customizing Theme Tokens

### For Widget Users

To customize how the markdown viewer appears with your theme:

1. **Edit your theme JSON file** to include the tokens you want to customize:

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

2. **The viewer automatically applies** these colors when the theme changes

### For Widget Developers

To modify the token mappings:

1. Edit `theme_config` in `markdown_viewer.py`
2. Update the CSS variables in `viewer.css`
3. Test with multiple themes to ensure proper contrast

## Token Selection Rationale

### Why not use `textLink.*` tokens?

The `textLink.*` tokens don't exist in the standard VSCode theme specification. We use `button.background` instead because:
- It provides the accent color that works well for links
- It's guaranteed to exist in all themes
- It maintains visual hierarchy (links stand out from body text)

### Why not use `editor.code.*` tokens?

These tokens were proposed but aren't part of the current theme system. We use:
- `input.background` - Provides subtle contrast for code blocks
- `input.foreground` - Ensures good readability for code text

### Why not use dedicated markdown tokens?

We align with existing editor tokens to:
- Ensure consistency across the application
- Leverage tested color combinations
- Avoid theme fragmentation
- Work with any VSCode-compatible theme

## Examples

### Dark Theme Example

```json
{
  "editor.background": "#1a1a1a",
  "editor.foreground": "#d4d4d4",
  "button.background": "#0e639c",
  "input.background": "#3c3c3c",
  "widget.border": "#3c3c3c"
}
```

**Result:** Dark background, light text, blue links, dark gray code blocks

### Light Theme Example

```json
{
  "editor.background": "#ffffff",
  "editor.foreground": "#000000",
  "button.background": "#0066cc",
  "input.background": "#f3f3f3",
  "widget.border": "#cccccc"
}
```

**Result:** White background, black text, blue links, light gray code blocks

## See Also

- [Theme Integration Guide](theme-integration-GUIDE.md) - Comprehensive guide on theme system integration
- [MarkdownViewer API](API.md) - Full widget API documentation
- [VSCode Theme Specification](https://code.visualstudio.com/api/references/theme-color) - Standard theme token reference
