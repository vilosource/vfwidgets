# ViloxTerm Preferences System - Implementation Summary

## What We've Built

A comprehensive, unified preferences system for ViloxTerm that consolidates all application and terminal settings into a single, easy-to-use tabbed dialog.

### Architecture Overview

```
PreferencesDialog
├── General Tab          ✅ COMPLETE
├── Appearance Tab       ✅ COMPLETE
├── Terminal Tab         ⏳ TODO (refactor existing)
├── Keyboard Shortcuts   ⏳ TODO
└── Advanced Tab         ⏳ TODO
```

## Completed Work

### 1. Data Model ✅

**File**: `src/viloxterm/models/preferences_model.py`

Three dataclass-based preference categories:

```python
@dataclass
class GeneralPreferences:
    # Startup settings
    restore_session: bool = False
    default_shell: str = ""
    starting_directory: str = "home"  # "home", "last", "custom"
    custom_directory: str = ""
    tabs_on_startup: int = 1

    # Window behavior
    close_on_last_tab: bool = True
    confirm_close_multiple_tabs: bool = True
    show_tab_bar_single_tab: bool = True
    frameless_window: bool = True

    # Session management
    save_tab_layout: bool = False
    save_working_directories: bool = True

@dataclass
class AppearancePreferences:
    # Theme
    application_theme: str = "dark"
    sync_with_system: bool = False
    custom_theme_path: str = ""

    # Window appearance
    window_opacity: int = 100  # 10-100%
    background_blur: bool = False
    window_padding: int = 0

    # UI elements
    tab_bar_position: str = "top"  # "top" or "bottom"
    show_menu_button: bool = True
    show_window_title: bool = True
    ui_font_size: int = 9

    # Focus indicators
    focus_border_width: int = 3
    focus_border_color: str = ""  # Empty = theme default
    unfocused_dim_amount: int = 0  # 0-50%

@dataclass
class AdvancedPreferences:
    # Performance
    hardware_acceleration: str = "auto"
    webengine_cache_size: int = 50  # MB
    max_tabs: int = 100
    terminal_renderer: str = "auto"

    # Behavior
    enable_animations: bool = True
    terminal_server_port: int = 0  # 0 = auto
    log_level: str = "INFO"

    # Experimental
    ligature_support: bool = False
    gpu_rendering: bool = False
    custom_css: str = ""
```

**Container class**:
```python
@dataclass
class PreferencesModel:
    general: GeneralPreferences
    appearance: AppearancePreferences
    advanced: AdvancedPreferences

    def to_dict(self) -> dict:
        """Serialize to JSON"""

    @classmethod
    def from_dict(cls, data: dict) -> "PreferencesModel":
        """Deserialize from JSON"""
```

### 2. Preferences Manager ✅

**File**: `src/viloxterm/app_preferences_manager.py`

Handles persistence and validation:

```python
class AppPreferencesManager:
    def __init__(self, config_dir: Optional[Path] = None):
        """Defaults to ~/.config/viloxterm"""

    def load_preferences(self) -> PreferencesModel:
        """Load from app_preferences.json"""

    def save_preferences(self, prefs: PreferencesModel) -> bool:
        """Save to app_preferences.json"""

    def validate_preferences(self, prefs: PreferencesModel) -> list[str]:
        """Returns list of validation errors"""

    def reset_to_defaults(self) -> PreferencesModel:
        """Get fresh defaults"""
```

**Storage location**: `~/.config/viloxterm/app_preferences.json`

**Validation includes**:
- Valid file paths for shells/directories
- Opacity range (10-100%)
- Port ranges (0-65535)
- Tab bar position ("top" or "bottom")
- Log level validity
- And more...

### 3. Preferences Dialog ✅

**File**: `src/viloxterm/components/preferences_dialog.py`

Main dialog with tabbed interface:

```python
class PreferencesDialog(ThemedDialog):
    # Signals
    preferences_applied = Signal(PreferencesModel)
    terminal_preferences_applied = Signal(dict)
    keybinding_changed = Signal(str, str)

    def __init__(self, parent=None):
        """Loads current preferences from disk"""

    def set_keybinding_manager(self, manager):
        """For keyboard shortcuts tab integration"""
```

**Features**:
- Inherits from `ThemedDialog` for automatic theme support
- Apply/OK/Cancel buttons
- Validates before saving
- Emits signals for live application of changes
- Graceful error handling

### 4. General Preferences Tab ✅

**File**: `src/viloxterm/components/general_prefs_tab.py`

**UI Features**:
- **Startup Group**:
  - Restore session checkbox
  - Tabs on startup spinner (1-20)
  - Default shell text field with file browser
  - Starting directory combo (Home/Last/Custom)
  - Custom directory field (enabled only when "Custom" selected)

- **Window Behavior Group**:
  - Close on last tab checkbox
  - Confirm before closing multiple tabs
  - Show tab bar when single tab
  - Frameless window (Chrome-style)

- **Session Management Group**:
  - Save and restore tab layout
  - Save and restore working directories

**Smart UX**:
- Custom directory field auto-enables/disables based on combo selection
- File/directory browsers for path selection
- Tooltips and clear labels

### 5. Appearance Preferences Tab ✅

**File**: `src/viloxterm/components/appearance_prefs_tab.py`

**UI Features**:
- **Theme Group**:
  - Application theme combo (Dark/Light/Default/Minimal)
  - Sync with system theme checkbox
  - Custom theme path field with file browser

- **Window Group**:
  - Opacity slider (10-100%) with live percentage display
  - Background blur checkbox
  - Window padding spinner (0-20px)

- **UI Elements Group**:
  - Tab bar position combo (Top/Bottom)
  - Show menu button checkbox
  - Show window title checkbox
  - UI font size spinner (6-24pt)

- **Focus Indicators Group**:
  - Focus border width spinner (0-10px)
  - Focus border color field (empty = theme default)
  - Unfocused pane dimming slider (0-50%) with live percentage

**Interactive Elements**:
- Sliders show current value percentages
- File browser for custom themes
- Real-time label updates

### 6. Test Script ✅

**File**: `test_preferences_dialog.py`

Quick test without running full ViloxTerm:

```bash
cd /home/kuja/GitHub/vfwidgets/apps/viloxterm
python test_preferences_dialog.py
```

Tests:
- Dialog creation
- Theme integration
- Signal connections
- Preference loading/saving

## Remaining Work

### Terminal Preferences Tab (1-2 hours)

**What to do**:
1. Create `terminal_prefs_tab.py`
2. Extract UI creation methods from existing `TerminalPreferencesDialog`
3. Reuse all existing widgets (scrollback, cursor, bell, etc.)
4. Wire up load/save to existing `TerminalPreferencesManager`

**Why it's easy**: The UI already exists, just needs to be extracted into a tab widget.

### Advanced Preferences Tab (30 min)

**What to do**:
1. Create `advanced_prefs_tab.py`
2. Create form widgets for performance settings
3. Add warning labels for experimental features
4. Wire up to `AdvancedPreferences` model

**Straightforward**: Similar structure to General/Appearance tabs.

### Keyboard Shortcuts Tab (2-3 hours)

**What to do**:
1. Create `keyboard_shortcuts_tab.py`
2. Create table/tree view of keybindings by category
3. Implement search/filter box
4. Create key capture dialog
5. Add conflict detection
6. Wire to `KeybindingManager`

**Most complex**: Requires tree view, key capture, and conflict UI.

### Integration with App (1-2 hours)

**Changes to `app.py`**:
```python
# In __init__:
self.app_prefs_manager = AppPreferencesManager()
self.app_prefs = self.app_prefs_manager.load_preferences()

# Apply preferences:
self.setWindowOpacity(self.app_prefs.appearance.window_opacity / 100.0)

# Connect to prefs dialog:
prefs_dialog.preferences_applied.connect(self._apply_app_preferences)

def _apply_app_preferences(self, prefs: PreferencesModel):
    """Apply preferences to running app."""
    # Apply opacity
    self.setWindowOpacity(prefs.appearance.window_opacity / 100.0)

    # Apply theme
    app = QApplication.instance()
    if hasattr(app, 'set_theme'):
        app.set_theme(prefs.appearance.application_theme)

    # Apply focus border width (update _on_focus_changed)
    # etc.
```

**Changes to menu**:
Replace terminal preferences action with full preferences:
```python
# OLD:
if "appearance.terminal_preferences" in keybinding_actions:
    self._menu.addAction(keybinding_actions["appearance.terminal_preferences"])

# NEW:
preferences_action = QAction("Preferences...", self)
preferences_action.setShortcut("Ctrl+,")
preferences_action.triggered.connect(self.preferences_requested.emit)
self._menu.addAction(preferences_action)
```

## Usage Examples

### Current Implementation (What Works Now)

```python
from viloxterm.components import PreferencesDialog

# Create dialog
dialog = PreferencesDialog(parent=main_window)

# Connect signals
dialog.preferences_applied.connect(app.apply_preferences)
dialog.terminal_preferences_applied.connect(app.apply_terminal_prefs)

# Show dialog
if dialog.exec():
    # User clicked OK
    app_prefs = dialog.get_app_preferences()
    term_prefs = dialog.get_terminal_preferences()
```

### Future Usage (After Integration)

```python
# In ViloxTermApp:
def _show_preferences_dialog(self):
    dialog = PreferencesDialog(self)
    dialog.set_keybinding_manager(self.keybinding_manager)
    dialog.preferences_applied.connect(self._apply_app_preferences)
    dialog.terminal_preferences_applied.connect(
        self._apply_terminal_preferences_to_all
    )
    dialog.exec()

# Triggered by Ctrl+, or menu item
```

## Benefits of This Design

1. **Unified Interface**: One place for all settings
2. **Type Safety**: Dataclass models catch errors at development time
3. **Validation**: Comprehensive validation before save
4. **Modularity**: Each tab is independent
5. **Extensibility**: Easy to add new settings
6. **Persistence**: Automatic JSON serialization
7. **Theme Integration**: Uses `ThemedDialog` for consistent appearance
8. **Signal-Based**: Clean separation of UI and application logic

## File Structure

```
apps/viloxterm/src/viloxterm/
├── models/
│   ├── __init__.py
│   └── preferences_model.py          ✅ NEW
├── app_preferences_manager.py        ✅ NEW
├── terminal_preferences_manager.py   (existing)
└── components/
    ├── __init__.py                   (updated)
    ├── preferences_dialog.py         ✅ NEW
    ├── general_prefs_tab.py          ✅ NEW
    ├── appearance_prefs_tab.py       ✅ NEW
    ├── terminal_prefs_tab.py         ⏳ TODO
    ├── keyboard_shortcuts_tab.py     ⏳ TODO
    ├── advanced_prefs_tab.py         ⏳ TODO
    └── terminal_preferences_dialog.py (keep for now, deprecate later)
```

## Testing Status

✅ **Verified**:
- Preferences dialog imports successfully
- Models serialize/deserialize correctly
- Manager loads/saves to JSON
- General tab UI complete
- Appearance tab UI complete

⏳ **Pending**:
- Full app integration test
- Live preference application
- Persistence across restarts
- All tabs complete and integrated

## Next Steps

To complete this implementation:

1. **Terminal Tab** - Refactor existing dialog into tab (1-2 hours)
2. **Advanced Tab** - Simple form-based UI (30 min)
3. **Keyboard Shortcuts Tab** - Tree view with key capture (2-3 hours)
4. **App Integration** - Wire up to main app (1-2 hours)
5. **Testing** - End-to-end verification (1 hour)

**Total remaining**: ~6-9 hours of development

## How to Test Current Work

```bash
cd /home/kuja/GitHub/vfwidgets/apps/viloxterm

# Test dialog (no X11 needed for import test)
python3 -c "from src.viloxterm.components import PreferencesDialog; print('OK')"

# Test with GUI (requires display)
python test_preferences_dialog.py
```

## Summary

We've built a solid foundation for ViloxTerm preferences:
- ✅ Complete data model with validation
- ✅ Persistent storage manager
- ✅ Themed dialog framework
- ✅ General settings UI (100% complete)
- ✅ Appearance settings UI (100% complete)
- ⏳ Terminal settings (needs refactor)
- ⏳ Keyboard shortcuts (needs implementation)
- ⏳ Advanced settings (needs implementation)
- ⏳ App integration (needs wiring)

The hardest architectural decisions are done. The remaining work is straightforward UI implementation and integration.
