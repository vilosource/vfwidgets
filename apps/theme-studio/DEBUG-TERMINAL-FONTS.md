# Debugging Terminal Font Changes

## Current Status

The terminal widget font support has been implemented, but you reported it's not working in theme-studio.

## What SHOULD Happen

When you change `terminal.fontSize` in theme-studio:

1. **Font Editor** → `property_changed` signal
2. **InspectorPanel** → `_on_font_property_changed()`
3. **ThemeController** → `queue_font_change()`
4. **SetFontCommand** → `ThemeDocument.set_font()`
5. **ThemeDocument** → `font_changed` signal emitted
6. **Window** → `_on_font_changed()` → `_deferred_update_preview_theme()`
7. **Window** → `_update_preview_theme(theme)`
8. **Terminal Widget** → `on_theme_changed(theme)` called ✓
9. **Terminal Widget** → `_get_font_with_fallback()` → reads `terminal.fontSize`
10. **Terminal Widget** → Updates xterm.js via JavaScript
11. **Result**: Terminal text size changes ✓

## Potential Issues

### Issue 1: Terminal Not Loaded Yet
The terminal widget loads asynchronously (xterm.js in QWebEngineView). If `on_theme_changed()` is called before the terminal is ready:
- Theme is stored in `_pending_themed_app_theme`
- Applied later in `_configure_terminal()` when terminal connects
- **This should work automatically**

### Issue 2: Theme Object Missing Fonts
If the theme being passed to `on_theme_changed()` doesn't have fonts:
- Font fallback uses defaults
- Terminal font doesn't change
- **Check logs for font information**

### Issue 3: Terminal Widget Not in Preview
If you're not actually viewing the terminal widget:
- No terminal widget exists to update
- **Select "terminal" from preview dropdown**

## How to Debug

1. **Launch theme-studio with verbose logging**:
   ```bash
   cd /home/kuja/GitHub/vfwidgets/apps/theme-studio
   python -m src.theme_studio 2>&1 | tee terminal-debug.log
   ```

2. **Select terminal widget**:
   - In preview dropdown, select "terminal" (if available)
   - Wait for terminal to load (you should see a terminal prompt)

3. **Change terminal font**:
   - Click "Fonts" → "TERMINAL" → "fontSize"
   - Change from 14 to 20
   - Press Enter

4. **Check the logs** for these key messages:
   ```
   🔍 [Theme Studio] About to call plugin_widget.on_theme_changed()
   🔍 [Theme Studio] theme has fonts: True
   🔍 [Theme Studio] theme.fonts keys: [...]
   🔍 [Theme Studio] theme.fonts['terminal.fontSize'] = 20
   ```

   Then in terminal widget logs:
   ```
   🔍 ========== on_theme_changed() START ==========
   🔍 Terminal is_connected: True
   🔍 _get_font_with_fallback(token_name=fontSize, default=14)
   ✅ Terminal font 'fontSize': using terminal.fontSize = 20
   ```

## Added Logging

I've added logging to `/home/kuja/GitHub/vfwidgets/apps/theme-studio/src/theme_studio/window.py` (lines 706-714) to show:
- Whether theme has fonts attribute
- What font keys are in the theme
- Specific values for terminal.fontSize and fonts.mono

This will help us see if fonts are being passed correctly.

## Testing Steps

1. **Start fresh**:
   ```bash
   python -m src.theme_studio
   ```

2. **Load a theme or create new**

3. **Select terminal from preview dropdown**:
   - If terminal is not in the list, the widget might not be installed
   - Check: `python -c "import vfwidgets_terminal; print('OK')"`

4. **Wait for terminal to load**:
   - You should see xterm.js terminal with prompt
   - Check logs for: `🔍 Terminal is_connected: True`

5. **Change terminal.fontSize**:
   - Fonts → TERMINAL → fontSize
   - Change to 20
   - Look at terminal - does text get bigger?

6. **Check logs**:
   - Search for `[Theme Studio]` messages
   - Search for `on_theme_changed()` messages from terminal widget
   - Look for any errors or warnings

## Expected Log Output

### When Terminal Loads:
```
🔍 ========== on_theme_changed() START ==========
🔍 Received theme parameter: <Theme ...>
🔍 Terminal is_connected: True
🔍 _get_font_with_fallback(token_name=fontFamily, default=Consolas...)
✅ Terminal font 'fontFamily': using fonts.mono = JetBrains Mono, ...
🔍 _get_font_with_fallback(token_name=fontSize, default=14)
✅ Terminal font 'fontSize': using fonts.size = 13  (or default 14)
```

### When You Change terminal.fontSize:
```
🔍 [Theme Studio] About to call plugin_widget.on_theme_changed()
🔍 [Theme Studio] theme.fonts['terminal.fontSize'] = 20
🔍 ========== on_theme_changed() START ==========
🔍 Terminal is_connected: True
🔍 _get_font_with_fallback(token_name=fontSize, default=14)
✅ Terminal font 'fontSize': using terminal.fontSize = 20
[JavaScript executes: term.options.fontSize = 20]
```

## What to Report Back

Please run the test and tell me:
1. **Is "terminal" in the preview dropdown?**
2. **Does the terminal load successfully?** (do you see a prompt?)
3. **What do the logs say?** (search for `[Theme Studio]` and `terminal.fontSize`)
4. **Does the terminal text actually resize?**

This will help me identify exactly where the problem is!
