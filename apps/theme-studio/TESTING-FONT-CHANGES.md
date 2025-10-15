# Testing Font Changes in Preview Widgets

## The Bug That Was Fixed

**Problem**: When editing font tokens (like `tabs.fontSize`), the changes were not being applied to the preview widgets. The value would update in the inspector, but the tabs in the preview would remain the same size.

**Root Cause**: The `StylesheetGenerator` in the widget library had hardcoded font values with comments like "no font tokens exist yet". It wasn't reading the actual font tokens from the theme.

## The Fix

Updated `StylesheetGenerator` to:
1. Added helper methods to read font tokens from theme:
   - `_get_font_value()` - Get raw font value with fallback
   - `_get_font_family()` - Get font family as CSS string
   - `_get_font_size()` - Get font size with px unit

2. Updated stylesheet generation methods to use font tokens:
   - `_generate_widget_styles()` - Uses `fonts.ui` and `fonts.size`
   - `_generate_tab_styles()` - Uses `tabs.fontFamily` and `tabs.fontSize`

3. Font tokens now flow from theme → stylesheet → preview widget

## How to Test the Fix

1. **Launch theme-studio**:
   ```bash
   cd /home/kuja/GitHub/vfwidgets/apps/theme-studio
   python -m src.theme_studio
   ```

2. **Select Generic Widgets plugin**:
   - In the preview area, select "Generic Widgets" from the dropdown
   - You should see tabs labeled "Tab 1", "Tab 2", "Tab 3"

3. **Edit tab font size**:
   - Click "Fonts" tab in the left panel
   - Expand "TABS" category
   - Click "fontSize"
   - In the inspector, you'll see "Font Size:" spinner
   - Current value is likely 14 (default)

4. **Increase the font size**:
   - Click the up arrow or type a larger value (e.g., 20)
   - Press Enter or click outside

5. **Observe the change**:
   - ✅ The tab labels in the preview should immediately get bigger
   - ✅ The change should be visible in real-time
   - ✅ You can undo with Ctrl+Z and the tabs shrink back

6. **Test other font tokens**:
   - Try changing `tabs.fontFamily` to "Arial" or "Comic Sans MS"
   - Try changing `fonts.size` (affects general UI elements)
   - All changes should apply immediately to the preview

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
                              └─ StylesheetGenerator (NOW READS FONTS!)
                                  └─ Preview widget stylesheet updated
                                      └─ VISUAL CHANGE! ✓
```

## Files Modified

1. **widget library** (fixes apply to all apps using theme system):
   - `/home/kuja/GitHub/vfwidgets/widgets/theme_system/src/vfwidgets_theme/widgets/stylesheet_generator.py`
     - Added `_get_font_value()` method (line 54-66)
     - Added `_get_font_family()` method (line 68-84)
     - Added `_get_font_size()` method (line 86-102)
     - Updated `_generate_widget_styles()` to use `fonts.ui` and `fonts.size` (line 136-137)
     - Updated `_generate_tab_styles()` to use `tabs.fontFamily` and `tabs.fontSize` (line 573-574)

## Expected Behavior

### Before Fix:
- Changing `tabs.fontSize` → No visual change
- Inspector shows updated value
- Preview tabs remain same size
- Very confusing!

### After Fix:
- Changing `tabs.fontSize` → Tabs immediately resize
- Inspector shows updated value
- Preview reflects the change in real-time
- Undo/redo works correctly
- All font tokens now affect preview appearance

## Additional Font Tokens to Test

- `fonts.ui` - General UI font family
- `fonts.size` - General UI font size
- `fonts.mono` - Monospace font for code/terminal
- `tabs.fontFamily` - Tab label font family
- `tabs.fontSize` - Tab label font size
- `tabs.fontWeight` - Tab label font weight

All of these should now affect the preview widget appearance when changed!
