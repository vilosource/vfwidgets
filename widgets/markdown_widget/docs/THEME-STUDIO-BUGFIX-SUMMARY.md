# Theme Studio Integration Bug Fix

## Problem

When using the markdown widget in Theme Studio and changing `markdown.colors.code.background`, the code block background color was not updating visually in the preview.

## Root Causes (Two Bugs)

### Bug 1: Flat Dictionary Structure Not Supported

The `ThemeBridge._get_nested_value()` method only supported **nested dictionary structures** like:
```python
{"markdown": {"colors": {"code": {"background": "#55ffff"}}}}
```

But Theme Studio sends theme colors as a **flat dictionary** with dot-notation keys:
```python
{"markdown.colors.code.background": "#55ffff"}
```

The token resolution was failing silently, reporting "Token not found" even though the token existed in the flat structure.

### Bug 2: CSS Specificity Issue

Even after fixing token resolution, CSS variables weren't applying because:

1. **viewer.css** defines defaults with: `body[data-theme="dark"] { --md-code-bg: #161b22; }`
2. **ThemeBridge** was injecting on: `document.documentElement.style.cssText` (the `<html>` tag)
3. **CSS Specificity**: `body[data-theme="dark"]` selector is MORE SPECIFIC than `:root` or `html`

Result: The hardcoded defaults in `viewer.css` always won, overriding ThemeBridge's injected values.

## Fix

### Fix 1: Support Flat Dictionary Structure

**File**: `src/vfwidgets_markdown/bridges/theme_bridge.py:234-263`

Modified `_get_nested_value()` to support **both** flat and nested structures:

```python
def _get_nested_value(self, colors: dict, path: str) -> Optional[str]:
    """Get value from nested dict using dot notation path.

    Supports both flat and nested structures:
    - Flat: {"markdown.colors.foreground": "#fff"}
    - Nested: {"markdown": {"colors": {"foreground": "#fff"}}}
    """
    # Try direct lookup first (flat structure from Theme Studio)
    if path in colors:
        value = colors[path]
        return value if isinstance(value, str) else None

    # Fall back to nested traversal (nested structure from JSON files)
    parts = path.split(".")
    current = colors

    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None

    return current if isinstance(current, str) else None
```

### Fix 2: Inject CSS Variables on Body Element

**File**: `src/vfwidgets_markdown/bridges/theme_bridge.py:284`

Changed CSS injection target from `document.documentElement` to `document.body`:

```javascript
// Before:
document.documentElement.style.cssText += "...";

// After:
document.body.style.cssText += "...";
```

**Why**: Inline styles on `body` element have the SAME specificity as `body[data-theme="dark"]` selector, but inline styles win due to style attribute specificity rules. This overrides the hardcoded defaults in `viewer.css`.

## Testing

### Unit Tests
Added 2 new tests in `tests/unit/test_theme_bridge.py`:
- `test_flat_structure_token_resolution` - Validates flat structure from Theme Studio
- `test_flat_with_fallback` - Validates fallback token resolution with flat structure

**All 84 tests pass** (was 82, +2 new tests)

### Integration Test
Playwright test `test_current_theme_bridge_css` confirms CSS applies correctly in browser:
```
Baseline (Prism CSS) background: rgba(0, 0, 0, 0)
After ThemeBridge override: rgb(255, 0, 0)
✅ PASSED
```

### Theme Studio Verification
Logs confirm token resolution now works:

**Before**:
```
[WARNING] md-code-bg: No value (tried markdown.colors.code.background, ['input.background', 'widget.background'], no default)
[WARNING] Token 'markdown.colors.code.background' not found
```

**After**:
```
[DEBUG] md-code-bg: #55ffff (from markdown.colors.code.background)
[DEBUG] Resolved 8 CSS variables
[DEBUG] [JS Console] [ThemeBridge] Applied 8 CSS variables
[DEBUG] [JS Console] [ThemeBridge] Injected custom CSS
```

## Impact

- ✅ **Theme Studio**: Markdown widget now responds to theme token changes
- ✅ **JSON Files**: Still supports nested structure from theme JSON files
- ✅ **Backward Compatible**: All existing tests pass
- ✅ **Fallback Chains**: Fallback token resolution still works with flat structure

## Files Modified

1. `src/vfwidgets_markdown/bridges/theme_bridge.py`:
   - Fixed `_get_nested_value()` to support flat dicts (line 234-263)
   - Changed CSS injection to `document.body` (line 284)
2. `tests/unit/test_theme_bridge.py`:
   - Added 2 flat structure tests
   - Updated CSS injection test to expect `document.body`

## Result

Both bugs are now fixed:
- ✅ **Token Resolution**: Flat dictionaries from Theme Studio now work
- ✅ **CSS Application**: Variables inject on `body` element, overriding hardcoded defaults
- ✅ **All Tests Pass**: 84/84 tests passing

The markdown widget should now correctly respond to theme changes in Theme Studio, with code block backgrounds updating in real-time.
