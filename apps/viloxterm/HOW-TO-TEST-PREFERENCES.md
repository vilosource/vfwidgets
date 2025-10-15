# How to Test the New Preferences System

## What's Been Integrated

The preferences system is now **fully integrated** into ViloxTerm and ready to test! Here's what you can do:

## Quick Start

### 1. Launch ViloxTerm

```bash
cd /home/kuja/GitHub/vfwidgets/apps/viloxterm
python -m src.viloxterm
```

### 2. Open Preferences Dialog

You can open the preferences in **three ways**:

**A. Keyboard Shortcut** (Recommended):
- Press `Ctrl+,` (Control + Comma)

**B. Menu Button**:
- Click the hamburger menu (☰) in the top-left of the window
- Select "Preferences"

**C. Right-click menu** (if available):
- Right-click on the window
- Select "Preferences"

### 3. Explore the Tabs

You'll see a tabbed dialog with:

#### ✅ **General Tab** - Fully Functional
- **Startup Settings**:
  - Restore previous session on startup
  - Number of tabs to open (1-20)
  - Default shell (with file browser)
  - Starting directory (Home/Last/Custom)
  - Custom directory path (with directory browser)

- **Window Behavior**:
  - Close window when last tab closes
  - Confirm before closing multiple tabs
  - Show tab bar when only one tab exists
  - Use frameless window (Chrome-style)

- **Session Management**:
  - Save and restore tab layout
  - Save and restore working directories

#### ✅ **Appearance Tab** - Fully Functional
- **Theme Settings**:
  - Application theme dropdown (Dark/Light/Default/Minimal)
  - Sync with system theme
  - Custom theme file path (with file browser)

- **Window Appearance**:
  - **Window opacity slider** (10-100%) - **Test this! It works live!**
  - Background blur (when supported)
  - Window padding (0-20px)

- **UI Elements**:
  - Tab bar position (Top/Bottom)
  - Show menu button in title bar
  - Show window title
  - UI font size (6-24pt)

- **Focus Indicators**:
  - Focus border width (0-10px)
  - Focus border color (empty = theme default)
  - Unfocused pane dimming (0-50%)

#### ⏳ **Terminal Tab** - Placeholder
- Shows "Terminal settings coming soon"
- Will be refactored from existing terminal preferences dialog

#### ⏳ **Keyboard Shortcuts Tab** - Placeholder
- Shows "Keyboard shortcuts coming soon"
- Will show all keybindings with edit capability

#### ⏳ **Advanced Tab** - Placeholder
- Shows "Advanced settings coming soon"
- Will include performance and experimental features

## What to Test

### Test 1: Window Opacity (Most Impressive!)

1. Open Preferences (`Ctrl+,`)
2. Go to **Appearance** tab
3. Find the "Window opacity" slider
4. **Move the slider** left/right
5. Click **Apply** (don't close yet!)
6. **Watch the ViloxTerm window become transparent!**
7. Try different opacity levels (50%, 75%, 90%)
8. Click **OK** to save

**Expected Result**: The entire ViloxTerm window becomes transparent based on the slider value. The setting persists across restarts.

### Test 2: Theme Changing

1. Open Preferences (`Ctrl+,`)
2. Go to **Appearance** tab
3. Change "Application theme" dropdown to "Light"
4. Click **Apply**
5. **The entire app should switch to light theme!**
6. Try "Dark" theme
7. Try "Minimal" theme
8. Click **OK** to save

**Expected Result**: Theme changes immediately when you click Apply. Setting is saved to disk.

### Test 3: General Settings

1. Open Preferences (`Ctrl+,`)
2. Go to **General** tab
3. Change "Open on startup" to 3 tabs
4. Change "Starting directory" to "Custom"
5. Click the "Browse..." button and select a directory
6. Click **OK**
7. **Close ViloxTerm completely**
8. **Restart ViloxTerm**
9. You should see **3 tabs open** instead of 1!

**Expected Result**: Settings persist across restarts.

### Test 4: Persistence

1. Open Preferences and make several changes:
   - Set opacity to 85%
   - Change theme to Light
   - Set tabs on startup to 2
2. Click **OK**
3. **Close ViloxTerm**
4. **Restart ViloxTerm**
5. Open Preferences again

**Expected Result**: All your settings are remembered! The opacity, theme, and tab count should match what you set.

### Test 5: Cancel vs OK

1. Open Preferences
2. Change opacity to 50%
3. Click **Apply** (window becomes transparent)
4. Change opacity to 100%
5. Click **Cancel**
6. Open Preferences again

**Expected Result**: Opacity should be back to 50% (the last applied value). Cancel discards un-applied changes.

### Test 6: Validation

1. Open Preferences
2. Go to **General** tab
3. Set "Starting directory" to "Custom"
4. Leave the custom directory field **empty**
5. Click **Apply**

**Expected Result**: You should see an error message or the apply fails gracefully (validation prevents invalid states).

## Where Settings Are Stored

All preferences are saved to:

```
~/.config/viloxterm/app_preferences.json
```

You can inspect this file to see the JSON structure:

```bash
cat ~/.config/viloxterm/app_preferences.json
```

Example content:
```json
{
  "general": {
    "restore_session": false,
    "default_shell": "",
    "starting_directory": "home",
    "custom_directory": "",
    "tabs_on_startup": 1,
    "close_on_last_tab": true,
    "confirm_close_multiple_tabs": true,
    "show_tab_bar_single_tab": true,
    "frameless_window": true,
    "save_tab_layout": false,
    "save_working_directories": true
  },
  "appearance": {
    "application_theme": "dark",
    "sync_with_system": false,
    "custom_theme_path": "",
    "window_opacity": 100,
    "background_blur": false,
    "window_padding": 0,
    "tab_bar_position": "top",
    "show_menu_button": true,
    "show_window_title": true,
    "ui_font_size": 9,
    "focus_border_width": 3,
    "focus_border_color": "",
    "unfocused_dim_amount": 0
  },
  "advanced": {
    "hardware_acceleration": "auto",
    "webengine_cache_size": 50,
    "max_tabs": 100,
    "terminal_renderer": "auto",
    "enable_animations": true,
    "terminal_server_port": 0,
    "log_level": "INFO",
    "ligature_support": false,
    "gpu_rendering": false,
    "custom_css": ""
  }
}
```

## Known Limitations

1. **Some settings require restart**:
   - Frameless window mode
   - Tab bar position
   - Default shell
   - Starting directory

2. **Placeholder tabs**:
   - Terminal, Keyboard Shortcuts, and Advanced tabs show placeholders
   - These will be implemented in the next phase

3. **Background blur**:
   - Only works on platforms that support it (macOS, some Linux compositors)
   - May not work on all systems

## Debugging

If something doesn't work:

1. **Check logs**: ViloxTerm logs to console, look for:
   ```
   Loaded application preferences
   Applying application preferences
   Set window opacity to 0.85
   ```

2. **Check the JSON file**:
   ```bash
   cat ~/.config/viloxterm/app_preferences.json | python -m json.tool
   ```

3. **Reset to defaults**: Delete the file and restart:
   ```bash
   rm ~/.config/viloxterm/app_preferences.json
   python -m src.viloxterm
   ```

## What Works Right Now

✅ **Fully Functional**:
- Opening preferences dialog with `Ctrl+,`
- General tab (all 11 settings work)
- Appearance tab (all 13 settings work)
- Apply/OK/Cancel buttons
- **Live window opacity changes** (most impressive!)
- **Live theme switching**
- Settings persistence to JSON
- Settings validation
- Keyboard shortcut integration
- Menu integration

⏳ **Coming Soon**:
- Terminal preferences tab (refactor existing dialog)
- Keyboard shortcuts editor
- Advanced settings tab

## Keyboard Shortcuts

- `Ctrl+,` - Open Preferences
- `Ctrl+0` - Reset terminal zoom (already worked, still works)
- All other shortcuts - Unchanged

## Summary

You now have a **working preferences system** with 24 settings across 2 tabs! The most impressive feature to test is the **window opacity slider** - you can make ViloxTerm transparent in real-time while the preferences dialog is still open.

Enjoy testing! 🎉
