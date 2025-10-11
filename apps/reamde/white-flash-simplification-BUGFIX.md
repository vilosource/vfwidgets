# White Flash Prevention - Simplification

**Date:** 2025-10-11
**Issue:** Over-engineered white flash prevention that didn't match proven terminal widget pattern
**Fix:** Simplified to use only `page().setBackgroundColor()` with static fallback

## Problem

After initial implementation of white flash prevention with 4 layers of protection:
1. Tab container stylesheet (MarkdownViewerTab)
2. Widget stylesheet (QWebEngineView)
3. Page background (setBackgroundColor)
4. HTML template defaults

The white flash persisted when opening new tabs with `reamde OTHERFILE.md`.

## Root Cause

The `_get_initial_background_color()` method tried to access `self.theme` during `__init__`, but:
- ThemedWidget hasn't completed initialization yet
- Theme hasn't been applied via deferred mechanism
- `self.theme` is empty or doesn't exist

This resulted in fallback colors that might not match the actual theme applied later, causing visual inconsistency.

## Solution

Simplified to match the proven terminal widget pattern:

### 1. Static Fallback Color

**Before:**
```python
def _get_initial_background_color(self) -> str:
    """Get theme-aware background color for WebView."""
    if not THEME_AVAILABLE:
        return "#1a1a1a"

    try:
        if hasattr(self, "theme") and self.theme:
            if hasattr(self.theme, "md_bg"):
                return self.theme.md_bg
            if hasattr(self.theme, "editor") and hasattr(self.theme.editor, "background"):
                return self.theme.editor.background
    except Exception:
        pass

    return "#1a1a1a"
```

**After:**
```python
def _get_initial_background_color(self) -> str:
    """Get initial background color for WebView.

    Returns a static dark fallback that prevents white flash on startup.
    The actual theme colors will be applied later via on_theme_changed().
    """
    # Static dark fallback (prevents white flash on startup)
    # Actual theme colors applied later via deferred theme mechanism
    return "#1a1a1a"
```

### 2. Removed Widget Stylesheet

**Before:**
```python
bg_color = self._get_initial_background_color()
page.setBackgroundColor(QColor(bg_color))

# Also set stylesheet on the QWebEngineView widget itself
self.setStyleSheet(f"QWebEngineView {{ background-color: {bg_color}; }}")
```

**After:**
```python
# Set background color to prevent white flash on load
# This sets the page background (visible while loading or if content has transparency)
# The actual theme colors are applied to HTML content via JavaScript in on_theme_changed()
bg_color = self._get_initial_background_color()
page.setBackgroundColor(QColor(bg_color))
```

## Why This Works

1. **Page background is set ONCE during init** with a sensible static dark color
2. **Theme colors applied later** via deferred theme mechanism and JavaScript
3. **No race conditions** trying to access theme during init
4. **Matches proven pattern** from terminal widget's lessons-learned

From terminal widget's `lessons-learned-GUIDE.md`:
> Set the QWebEngineView background color to match the terminal theme immediately upon creation.
> The background color is applied before any content loads, eliminating the visible white background.

## Key Lesson

**Don't try to be theme-aware during `__init__`!**

During widget construction:
- ThemedWidget hasn't finished initializing
- Theme hasn't been applied yet (deferred via QTimer.singleShot)
- `self.theme` is not available

Use a **static fallback** and let the deferred theme mechanism handle the actual theme colors.

## Related Files

- `widgets/markdown_widget/src/vfwidgets_markdown/widgets/markdown_viewer.py` - Main fix
- `widgets/terminal_widget/docs/lessons-learned-GUIDE.md` - Pattern documentation
- `widgets/terminal_widget/src/vfwidgets_terminal/terminal.py:702-703` - Reference implementation

## Testing

Manual testing:
1. Start reamde: `reamde README.md`
2. Open second file: `reamde OTHERFILE.md` (new tab)
3. Check for white flash when new tab opens
4. Verify theme colors applied after page loads

Expected: Dark background visible throughout loading, no white flash.

## Commits

- e8716e5 - fix(markdown): simplify white flash prevention to match terminal widget
- 65d9d60 - docs(terminal): add lesson about static background color during init
