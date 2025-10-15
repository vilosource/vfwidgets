# Terminal Font Changes Fix - COMPLETE

## Summary

Terminal font tokens (like `terminal.fontSize`) are now fully functional in theme-studio. When you change these values in the Fonts panel, the terminal preview immediately updates with the new font settings.

## The Problem

When editing terminal font tokens in theme-studio:
1. The value would update in the inspector ✓
2. The theme document would store the new value ✓
3. The theme would be passed to the terminal widget ✓
4. **BUT** the terminal text would NOT resize ✗

## Root Causes

### Issue 1: Missing Font Token Reading (Fixed Previously)
The terminal widget's `on_theme_changed()` method only read color tokens. Font tokens were ignored.

**Location**: `/home/kuja/GitHub/vfwidgets/widgets/terminal_widget/src/vfwidgets_terminal/terminal.py`

**What was missing**: No `_get_font_with_fallback()` method, no font properties in `xterm_theme` dict

### Issue 2: Incorrect xterm.js API Usage (Fixed Now)
The `set_theme()` method only used `setOption('theme', {...})` which in xterm.js applies **colors only**.

**The critical mistake**:
```python
# OLD CODE - Only applies colors
js_code = f"window.terminal.setOption('theme', {js_theme});"
```

**The xterm.js reality**:
- `setOption('theme', {...})` - accepts colors only (background, foreground, cursor, ansi colors)
- `setOption('fontSize', 20)` - required for font size
- `setOption('fontFamily', "...")` - required for font family
- `setOption('lineHeight', 1.2)` - required for line height
- `setOption('letterSpacing', 0)` - required for letter spacing

## The Complete Fix

### Part 1: Font Token Resolution (lines 1913-1969)
Added `_get_font_with_fallback()` method to read font tokens with proper fallback:

```python
def _get_font_with_fallback(self, token_name, theme=None, default=None):
    """Get font with hierarchical fallback:
    1. terminal.{token_name} (widget-specific override)
    2. fonts.mono or fonts.size (base font)
    3. default value
    """
```

**Hierarchy example for `fontSize`**:
1. Try `terminal.fontSize` → Found! Use 20
2. If not found, try `fonts.size` → Found! Use 13
3. If not found, use default → 14

### Part 2: Include Fonts in Theme Dict (lines 2110-2113)
Updated `on_theme_changed()` to add font properties to `xterm_theme`:

```python
xterm_theme = {
    # ... 20+ color properties ...
    "fontFamily": self._get_font_with_fallback("fontFamily", theme, "Consolas, Monaco, ..."),
    "fontSize": self._get_font_with_fallback("fontSize", theme, 14),
    "lineHeight": self._get_font_with_fallback("lineHeight", theme, 1.2),
    "letterSpacing": self._get_font_with_fallback("letterSpacing", theme, 0),
}
```

### Part 3: Apply Fonts Correctly to xterm.js (lines 1824-1860)
Updated `set_theme()` to separate colors and fonts, applying each correctly:

```python
def set_theme(self, theme_dict):
    # Separate font properties from color properties
    font_properties = ["fontFamily", "fontSize", "lineHeight", "letterSpacing"]
    color_dict = {k: v for k, v in theme_dict.items() if k not in font_properties}

    # Build JavaScript commands
    js_commands = []

    # Set color theme (xterm.js 'theme' option)
    if color_dict:
        js_theme = json.dumps(color_dict)
        js_commands.append(f"window.terminal.setOption('theme', {js_theme});")

    # Set font properties individually (CRITICAL!)
    for prop in font_properties:
        if prop in theme_dict:
            value = theme_dict[prop]
            js_value = json.dumps(value)
            js_commands.append(f"window.terminal.setOption('{prop}', {js_value});")
            logger.debug(f"🔍 Setting terminal {prop} = {value}")

    # Execute all commands
    if js_commands:
        js_code = f"if (window.terminal) {{ {' '.join(js_commands)} }}"
        self.inject_javascript(js_code)
```

**Why this works**:
- Colors applied via `setOption('theme', {background: ..., foreground: ...})`
- Each font property applied via `setOption('fontSize', 20)`, etc.
- xterm.js receives the properties in the format it expects
- Terminal immediately re-renders with new font settings

## Testing the Fix

### 1. Launch theme-studio
```bash
cd /home/kuja/GitHub/vfwidgets/apps/theme-studio
python -m src.theme_studio
```

### 2. Load Terminal Widget
- In preview dropdown, select a plugin with terminal widget
- Wait for terminal to load (you should see a prompt)

### 3. Edit Terminal Font Size
- Click "Fonts" tab in left panel
- Expand "TERMINAL" category
- Click "fontSize"
- Change value from 14 to 20
- Press Enter

### 4. Expected Result
✅ **Terminal text immediately gets bigger!**
✅ Change applies in real-time
✅ Undo with Ctrl+Z shrinks text back
✅ All font tokens work: fontSize, fontFamily, lineHeight, letterSpacing

## Signal Flow (Now Complete)

```
Font Editor Widget
  └─ property_changed signal
      └─ InspectorPanel._on_font_property_changed()
          └─ ThemeController.queue_font_change()
              └─ SetFontCommand created
                  └─ ThemeDocument.set_font()
                      └─ font_changed signal
                          └─ Window._on_font_changed()
                              └─ Window._deferred_update_preview_theme()
                                  └─ Window._update_preview_theme(theme)
                                      └─ TerminalWidget.on_theme_changed(theme) ✓
                                          └─ _get_font_with_fallback() ✓
                                              └─ xterm_theme dict with fonts ✓
                                                  └─ set_theme(xterm_theme) ✓
                                                      └─ setOption('fontSize', 20) ✓
                                                          └─ xterm.js re-renders ✓
                                                              └─ TERMINAL TEXT RESIZES! ✓✓✓
```

## Token Hierarchy Examples

### Example 1: terminal.fontSize = 20
```
User sets: terminal.fontSize = 20

Resolution:
1. terminal.fontSize exists → Use 20 ✓
2. JavaScript: window.terminal.setOption('fontSize', 20)
3. Result: Terminal text is 20px
```

### Example 2: Only fonts.size = 13
```
Theme has: fonts.size = 13 (no terminal.fontSize)

Resolution:
1. terminal.fontSize not found
2. fonts.size exists → Use 13 ✓
3. JavaScript: window.terminal.setOption('fontSize', 13)
4. Result: Terminal text is 13px
```

### Example 3: No font tokens at all
```
Theme has: no font tokens

Resolution:
1. terminal.fontSize not found
2. fonts.size not found
3. Use default → 14 ✓
4. JavaScript: window.terminal.setOption('fontSize', 14)
5. Result: Terminal text is 14px
```

## Font Tokens Supported

All terminal font tokens now work correctly:

- `terminal.fontSize` - Font size in pixels (default: 14)
  - Falls back to `fonts.size`

- `terminal.fontFamily` - Font family CSS string (default: "Consolas, Monaco, 'Courier New', monospace")
  - Falls back to `fonts.mono` (converted from list to CSS string)

- `terminal.lineHeight` - Line height multiplier (default: 1.2)
  - No fallback, uses default if not specified

- `terminal.letterSpacing` - Letter spacing in pixels (default: 0)
  - No fallback, uses default if not specified

## Why the Previous Fix Didn't Work

The previous fix added:
1. ✓ Font token reading (`_get_font_with_fallback()`)
2. ✓ Font properties in theme dict
3. ✗ **BUT** passed them to xterm.js incorrectly

The font properties were being included in the `theme` object:
```javascript
window.terminal.setOption('theme', {
    background: "#1e1e1e",
    foreground: "#d4d4d4",
    fontSize: 20,  // ← xterm.js IGNORES this!
})
```

xterm.js **silently ignores** non-color properties in the `theme` object. Font properties must be set individually.

## The Lesson

When integrating with third-party libraries (like xterm.js):
1. **Read the documentation carefully** - Different options have different setters
2. **Test the actual behavior** - Don't assume APIs work a certain way
3. **Add debug logging** - Helps identify where data flow breaks
4. **Verify at each layer** - Theme → Widget → JavaScript → Render

In this case, the theme system was working perfectly. The widget was reading tokens correctly. The problem was in the final step: translating to the xterm.js API.

## Files Modified

1. `/home/kuja/GitHub/vfwidgets/widgets/terminal_widget/src/vfwidgets_terminal/terminal.py`
   - Added `_get_font_with_fallback()` method (lines 1913-1969)
   - Updated `on_theme_changed()` to include fonts in xterm_theme (lines 2110-2113)
   - **Fixed `set_theme()` to apply fonts correctly** (lines 1824-1860)

## Status

✅ **COMPLETE** - Terminal font changes now work in theme-studio!

All font tokens (fontSize, fontFamily, lineHeight, letterSpacing) now apply immediately to the terminal preview when edited.
