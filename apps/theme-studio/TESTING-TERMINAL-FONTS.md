# Testing Terminal Font Changes

## The Bugs That Were Fixed

**Problem**: When editing terminal font tokens (like `terminal.fontSize`), the changes were not being applied to the terminal preview. The font size value would update in the inspector, but the terminal text would remain the same size.

**Root Causes**:
1. The terminal widget's `on_theme_changed()` method only extracted color tokens from the theme. It had no code to read font tokens. The `xterm_theme` dictionary only contained colors, not fonts.
2. The `set_theme()` method only used `setOption('theme', ...)` which applies colors only in xterm.js. Font properties need individual `setOption()` calls.

## The Fixes

Updated `/home/kuja/GitHub/vfwidgets/widgets/terminal_widget/src/vfwidgets_terminal/terminal.py`:

### Fix 1: Added Font Token Helper Method (lines 1913-1969)
```python
def _get_font_with_fallback(self, token_name, theme=None, default=None):
    """Get font with hierarchical fallback:
    1. terminal.{token_name} (widget-specific)
    2. fonts.mono or fonts.size (base)
    3. default value
    """
```

This mirrors the existing `_get_color_with_fallback()` pattern for consistency.

### Fix 2: Updated Theme Dictionary (lines 2110-2113)
Added font properties to `xterm_theme` dict:
```python
xterm_theme = {
    # ... colors ...
    # Font properties (NEW!)
    "fontFamily": self._get_font_with_fallback("fontFamily", theme, "Consolas..."),
    "fontSize": self._get_font_with_fallback("fontSize", theme, 14),
    "lineHeight": self._get_font_with_fallback("lineHeight", theme, 1.2),
    "letterSpacing": self._get_font_with_fallback("letterSpacing", theme, 0),
}
```

### Fix 3: Updated set_theme() Method (lines 1824-1860)
Changed `set_theme()` to apply font properties correctly to xterm.js:
```python
def set_theme(self, theme_dict):
    # Separate font properties from colors
    font_properties = ["fontFamily", "fontSize", "lineHeight", "letterSpacing"]
    color_dict = {k: v for k, v in theme_dict.items() if k not in font_properties}

    # Apply colors with setOption('theme', ...)
    js_commands.append(f"window.terminal.setOption('theme', {js_theme});")

    # Apply each font property individually (CRITICAL!)
    for prop in font_properties:
        if prop in theme_dict:
            js_commands.append(f"window.terminal.setOption('{prop}', {js_value});")
```

**Why this matters**: xterm.js only accepts color properties in the `theme` option. Font properties must be set individually using `setOption('fontSize', ...)`, etc.

### 3. Font Token Resolution Hierarchy

For `terminal.fontSize`:
1. Check `terminal.fontSize` (widget-specific override)
2. Check `fonts.size` (base font size)
3. Use default: `14`

For `terminal.fontFamily`:
1. Check `terminal.fontFamily` (widget-specific override)
2. Check `fonts.mono` (monospace font list)
3. Use default: `"Consolas, Monaco, 'Courier New', monospace"`

## How to Test the Fix

1. **Launch theme-studio**:
   ```bash
   cd /home/kuja/GitHub/vfwidgets/apps/theme-studio
   python -m src.theme_studio
   ```

2. **Load Terminal Widget**:
   - In the preview dropdown, select a plugin with a terminal widget
   - You should see a terminal with text

3. **Edit terminal font size**:
   - Click "Fonts" tab in left panel
   - Expand "TERMINAL" category
   - Click "fontSize"
   - Current value is likely 14 (default)

4. **Increase the font size**:
   - Change the spinner value to 20
   - Press Enter or click outside

5. **Observe the change**:
   - ✅ The terminal text should immediately get bigger!
   - ✅ The change applies in real-time
   - ✅ You can undo with Ctrl+Z and the text shrinks back

6. **Test other terminal font tokens**:
   - `terminal.fontFamily` - Change to "JetBrains Mono" or "Courier New"
   - `terminal.lineHeight` - Try 1.5 for more spacing
   - `terminal.letterSpacing` - Try 1 or 2 for wider letters

## Signal Flow (Now Working)

```
Font Editor Widget
  └─ property_changed signal
      └─ InspectorPanel._on_font_property_changed()
          └─ ThemeController.queue_font_change()
              └─ SetFontCommand created
                  └─ ThemeDocument.set_font()
                      └─ font_changed signal
                          └─ Window._on_font_changed()
                              └─ TerminalWidget.on_theme_changed()
                                  └─ _get_font_with_fallback() (NEW!)
                                      └─ JavaScript updates xterm.js
                                          └─ TERMINAL TEXT RESIZES! ✓
```

## Key Implementation Details

### Font Family List Handling
Font families are stored as lists in the theme:
```json
{
  "fonts.mono": ["JetBrains Mono", "Fira Code", "Consolas", "monospace"]
}
```

The helper method converts this to a CSS string for xterm.js:
```python
if token_name == "fontFamily" and isinstance(value, list):
    value = ", ".join(value)
    # Result: "JetBrains Mono, Fira Code, Consolas, monospace"
```

### xterm.js Font Options
The terminal uses xterm.js which accepts these font options:
- `fontFamily` - CSS font-family string
- `fontSize` - Font size in pixels (integer)
- `lineHeight` - Line height multiplier (float, e.g., 1.2)
- `letterSpacing` - Letter spacing in pixels (integer)

All of these now read from theme tokens with proper fallbacks!

## Expected Behavior

### Before Fix:
- Changing `terminal.fontSize` → No visual change
- Terminal text stays same size
- Inspector shows updated value
- Very frustrating!

### After Fix:
- Changing `terminal.fontSize` → Terminal text immediately resizes
- Changing `terminal.fontFamily` → Terminal font changes
- All font properties apply in real-time
- Undo/redo works correctly

## Fallback Behavior

If font tokens are not defined in the theme:
- `terminal.fontSize` → falls back to `fonts.size` (13) → falls back to 14
- `terminal.fontFamily` → falls back to `fonts.mono` → falls back to "Consolas..."
- `terminal.lineHeight` → falls back to default 1.2
- `terminal.letterSpacing` → falls back to default 0

This ensures the terminal always has sensible font settings even with incomplete themes!
