# ViloxTerm Preferences System - Implementation Progress

## Status: In Progress

### Completed Components

#### 1. Data Model ✅
- **File**: `src/viloxterm/models/preferences_model.py`
- **Classes**:
  - `GeneralPreferences` - Startup, window behavior, session management
  - `AppearancePreferences` - Theme, window appearance, UI customization
  - `AdvancedPreferences` - Performance, experimental features
  - `PreferencesModel` - Container for all preferences
- **Features**:
  - Dataclass-based with type hints
  - `to_dict()` / `from_dict()` for JSON serialization
  - Default values for all settings

#### 2. Preferences Manager ✅
- **File**: `src/viloxterm/app_preferences_manager.py`
- **Class**: `AppPreferencesManager`
- **Features**:
  - Load/save to `~/.config/viloxterm/app_preferences.json`
  - Validation with detailed error messages
  - Reset to defaults functionality
  - Follows same pattern as `TerminalPreferencesManager`

#### 3. Base Preferences Dialog ✅
- **File**: `src/viloxterm/components/preferences_dialog.py`
- **Class**: `PreferencesDialog`
- **Features**:
  - Tabbed interface using `QTabWidget`
  - Inherits from `ThemedDialog` for theme consistency
  - Apply/OK/Cancel buttons
  - Signals for preference changes
  - Integration points for all tabs

#### 4. General Preferences Tab ✅
- **File**: `src/viloxterm/components/general_prefs_tab.py`
- **Class**: `GeneralPreferencesTab`
- **Settings**:
  - **Startup**: Restore session, tabs on startup, default shell, starting directory
  - **Window Behavior**: Close on last tab, confirm close, show tab bar, frameless mode
  - **Session Management**: Save layout, save working directories
- **Features**:
  - File/directory browsers for paths
  - Smart enable/disable for conditional fields
  - Full load/save integration

#### 5. Appearance Preferences Tab ✅
- **File**: `src/viloxterm/components/appearance_prefs_tab.py`
- **Class**: `AppearancePreferencesTab`
- **Settings**:
  - **Theme**: Application theme selection, system sync, custom theme path
  - **Window**: Opacity slider (10-100%), background blur, window padding
  - **UI Elements**: Tab bar position, menu button visibility, UI font size
  - **Focus Indicators**: Border width, border color, unfocused dimming
- **Features**:
  - Live opacity percentage display
  - Theme file browser
  - Sliders with value labels

### Remaining Components

#### 6. Terminal Preferences Tab (Refactor) ⏳
- **Action**: Extract content from `TerminalPreferencesDialog` into `TerminalPreferencesTab`
- **Reuse**: Existing UI creation methods from `TerminalPreferencesDialog`
- **Settings**:
  - Scrollback, tab width, TERM variable
  - Cursor style & blink
  - Scroll sensitivity & modifiers
  - Bell style
  - Right-click behavior, EOL conversion

#### 7. Keyboard Shortcuts Tab ⏳
- **File**: `src/viloxterm/components/keyboard_shortcuts_tab.py` (to create)
- **Features Needed**:
  - Table/tree view of all keybindings by category
  - Search/filter functionality
  - Click-to-edit with key capture
  - Conflict detection
  - Reset to defaults (per-action or all)
  - Import/export profiles

#### 8. Advanced Preferences Tab ⏳
- **File**: `src/viloxterm/components/advanced_prefs_tab.py` (to create)
- **Settings**:
  - **Performance**: Hardware acceleration, cache size, max tabs, renderer
  - **Behavior**: Animations, server port, log level
  - **Experimental**: Ligatures, GPU rendering, custom CSS

#### 9. Integration with App ⏳
- Update `app.py`:
  - Load preferences at startup
  - Apply opacity, focus borders, etc.
  - Connect live updates
- Update menu button:
  - "Preferences..." instead of "Terminal Preferences"
  - Connect to new unified dialog
- Update shortcuts:
  - Ctrl+, opens Preferences (currently Terminal Prefs only)

#### 10. Testing ⏳
- Verify all settings load/save correctly
- Test validation catches invalid values
- Test live application of changes
- Test persistence across restarts

### Next Steps

1. **Integrate Appearance tab into dialog** (5 min)
2. **Refactor Terminal preferences tab** (30 min)
3. **Create Advanced preferences tab** (30 min)
4. **Create Keyboard Shortcuts tab** (1-2 hours)
5. **Wire up preferences in app.py** (1 hour)
6. **Test end-to-end** (30 min)

### Architecture Decisions

1. **Separate managers**: `AppPreferencesManager` for app settings, `TerminalPreferencesManager` for terminal-specific
2. **Dataclass model**: Type-safe, easy serialization, clear defaults
3. **Tab-based UI**: Each concern gets its own scrollable tab
4. **Validation**: Centralized in manager, checked before save
5. **Signals**: Clean separation between UI and application logic

### Files Created

```
apps/viloxterm/src/viloxterm/
├── models/
│   ├── __init__.py                    ✅
│   └── preferences_model.py           ✅
├── app_preferences_manager.py         ✅
└── components/
    ├── preferences_dialog.py          ✅
    ├── general_prefs_tab.py           ✅
    └── appearance_prefs_tab.py        ✅
```

### Files To Create

```
apps/viloxterm/src/viloxterm/components/
├── terminal_prefs_tab.py              ⏳ (refactor from existing)
├── keyboard_shortcuts_tab.py          ⏳
├── advanced_prefs_tab.py              ⏳
└── keybinding_capture_dialog.py      ⏳ (for key capture)
```

### Integration Points

**In `app.py`:**
- Load preferences in `__init__`
- Apply window opacity: `self.setWindowOpacity(prefs.appearance.window_opacity / 100)`
- Apply focus border width in `_on_focus_changed()`
- Listen to `preferences_applied` signal for live updates

**In `menu_button.py`:**
- Change action text from "Terminal Preferences" to "Preferences..."
- Connect to new `PreferencesDialog` instead of `TerminalPreferencesDialog`

**In keybinding system:**
- Expose current bindings to Keyboard Shortcuts tab
- Apply changes from tab back to `KeybindingManager`
- Trigger save after changes

### Storage Locations

- App preferences: `~/.config/viloxterm/app_preferences.json` (NEW)
- Terminal preferences: `~/.config/viloxterm/terminal_preferences.json` (existing)
- Keybindings: `~/.config/viloxterm/keybindings.json` (existing)
- Application theme: QSettings `ViloxTerm/ViloxTerm` → `theme/current` (existing)

### Known Limitations

1. **Restart required**: Some settings (frameless mode, tab bar position) require app restart
2. **System theme sync**: Platform-specific, may not work on all systems
3. **Background blur**: Only works on platforms that support it (macOS, some Linux compositors)
4. **Custom CSS**: Experimental feature, no validation yet

### Testing Checklist

- [ ] Preferences dialog opens with Ctrl+,
- [ ] All tabs load without errors
- [ ] General tab: all settings save/load correctly
- [ ] Appearance tab: opacity slider works, theme changes apply
- [ ] Terminal tab: existing settings continue to work
- [ ] Keyboard Shortcuts tab: can view and edit bindings
- [ ] Advanced tab: warnings shown for experimental features
- [ ] Apply button updates app without closing dialog
- [ ] OK button applies and closes
- [ ] Cancel button discards changes
- [ ] Settings persist across app restarts
- [ ] Invalid settings show error message
- [ ] Reset to defaults works for each category
