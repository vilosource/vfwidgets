# ViloxTerm Keybinding Manager Integration Guide

**For**: Developers working on ViloxTerm keyboard shortcuts
**Status**: Living Document
**Last Updated**: 2025-10-19

This guide explains how ViloxTerm integrates with the `vfwidgets-keybinding` widget to provide customizable keyboard shortcuts.

---

## Architecture Overview

ViloxTerm uses a clean separation between:
1. **Action registration** - What actions exist and their default shortcuts
2. **Shortcut management** - The KeybindingManager from `vfwidgets-keybinding` widget
3. **UI integration** - Applying shortcuts to the window and showing them in preferences

```
┌─────────────────────────────────────────────────┐
│ ViloxTermApp (ChromeTabbedWindow)              │
│                                                  │
│  ┌───────────────────────────────────────────┐  │
│  │ _setup_keybinding_manager()              │  │
│  │ - Creates KeybindingManager instance     │  │
│  │ - Registers all ActionDefinitions        │  │
│  │ - Loads saved bindings from JSON         │  │
│  │ - Applies shortcuts to window            │  │
│  └───────────────────────────────────────────┘  │
│                                                  │
│  ┌───────────────────────────────────────────┐  │
│  │ KeybindingManager                         │  │
│  │ (from vfwidgets-keybinding widget)        │  │
│  │                                            │  │
│  │ - ActionRegistry (all actions)            │  │
│  │ - KeybindingStorage (JSON persistence)   │  │
│  │ - apply_shortcuts() → QActions            │  │
│  └───────────────────────────────────────────┘  │
│                                                  │
│  ┌───────────────────────────────────────────┐  │
│  │ PreferencesDialog                         │  │
│  │ - Keyboard Shortcuts tab (TODO)           │  │
│  │ - set_keybinding_manager() ✅            │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

---

## Current Implementation

### 1. KeybindingManager Setup

**File**: `app.py:195-373`

The `_setup_keybinding_manager()` method initializes the keybinding system:

```python
def _setup_keybinding_manager(self) -> None:
    """Set up keyboard shortcut manager with user-customizable bindings."""
    # Storage location for user customizations
    storage_path = Path.home() / ".config" / "viloxterm" / "keybindings.json"

    # Create manager with auto-save enabled
    self.keybinding_manager = KeybindingManager(
        storage_path=str(storage_path),
        auto_save=True
    )

    # Register all actions (see below)
    self.keybinding_manager.register_actions([...])

    # Load saved bindings (or use defaults)
    self.keybinding_manager.load_bindings()

    # Apply shortcuts to window (creates QActions)
    self.actions = self.keybinding_manager.apply_shortcuts(self)
```

**Key points**:
- Auto-save is enabled so any programmatic binding changes persist automatically
- Storage path is in standard XDG config directory
- `apply_shortcuts(self)` creates QAction objects and sets them on the window

### 2. Action Registration

**File**: `app.py:204-365`

Actions are registered using `ActionDefinition` from the keybinding manager:

```python
ActionDefinition(
    id="pane.split_horizontal",           # Unique dot-separated identifier
    description="Split Horizontal",        # Human-readable description
    default_shortcut="Ctrl+Shift+\\",     # Default keyboard shortcut
    category="Pane",                       # Category for grouping in UI
    callback=self._on_split_horizontal,   # Method to call when triggered
)
```

**Current actions** (19 total):

**Pane category** (7 actions):
- `pane.split_horizontal` - `Ctrl+Shift+\`
- `pane.split_vertical` - `Ctrl+Shift+-`
- `pane.close` - `Ctrl+W`
- `pane.navigate_left` - `Ctrl+Shift+Left`
- `pane.navigate_right` - `Ctrl+Shift+Right`
- `pane.navigate_up` - `Ctrl+Shift+Up`
- `pane.navigate_down` - `Ctrl+Shift+Down`

**Tab category** (10 actions):
- `tab.new` - `Ctrl+Shift+T`
- `tab.close` - `Ctrl+Shift+W`
- `tab.next` - `Ctrl+PgDown`
- `tab.previous` - `Ctrl+PgUp`
- `tab.jump_1` through `tab.jump_9` - `Alt+1` through `Alt+9`

**Appearance category** (2 actions):
- `appearance.preferences` - `Ctrl+,`
- `appearance.reset_zoom` - `Ctrl+0`

### 3. Shortcut Application

The `apply_shortcuts()` method creates QAction objects:

```python
# Returns dict mapping action_id -> QAction
self.actions = self.keybinding_manager.apply_shortcuts(self)

# Each QAction:
# - Has the current shortcut set
# - Is connected to the callback
# - Is added to the window so shortcuts work
```

**Result**: All shortcuts are automatically working app-wide!

### 4. Menu Integration

**File**: `app.py:159`

The menu button receives actions for display:

```python
self.menu_button = MenuButton(
    self._window_controls,
    keybinding_actions=self.actions  # QActions with shortcuts
)
```

The menu displays shortcuts next to each action for user reference.

### 5. Preferences Dialog Integration

**File**: `app.py:574`

The KeybindingManager is passed to preferences dialog:

```python
def _show_preferences_dialog(self) -> None:
    dialog = PreferencesDialog(self, self.preferences)
    dialog.set_keybinding_manager(self.keybinding_manager)  # ✅ Ready
    # ...
```

**Status**: The dialog has the manager, but the UI tab is not yet implemented (see WIP tasks).

---

## Storage Format

**File**: `~/.config/viloxterm/keybindings.json`

User customizations are stored as JSON:

```json
{
  "pane.split_horizontal": "Ctrl+Shift+\\",
  "pane.split_vertical": "Ctrl+Shift+-",
  "pane.close": "Ctrl+W",
  "tab.new": "Ctrl+Shift+T",
  "tab.close": "Ctrl+Shift+W",
  "appearance.preferences": "Ctrl+,"
}
```

**Behavior**:
- Only changed bindings are stored (defaults are not saved)
- Missing entries use default shortcuts
- Invalid shortcuts are ignored (with warning log)
- Auto-saves on any binding change

---

## Adding New Shortcuts

To add a new keyboard shortcut:

### Step 1: Define the action callback

```python
def _on_my_action(self) -> None:
    """Handle my custom action."""
    logger.debug("My action triggered!")
    # Implementation...
```

### Step 2: Register the action

Add to `_setup_keybinding_manager()`:

```python
ActionDefinition(
    id="category.my_action",
    description="My Action",
    default_shortcut="Ctrl+Shift+M",
    category="MyCategory",
    callback=self._on_my_action,
),
```

### Step 3: Update documentation

Add to `keyboard-shortcuts-SPEC.md`:

```markdown
| My Action | `Ctrl+Shift+M` | ✅ Implemented | MyCategory | Does something cool |
```

That's it! The shortcut will automatically:
- Work app-wide
- Appear in the menu
- Be customizable via JSON
- Load/save correctly

---

## Testing Shortcuts

### Manual testing

1. Run ViloxTerm
2. Press the shortcut key
3. Verify the action is triggered

### Custom binding testing

1. Edit `~/.config/viloxterm/keybindings.json`
2. Add/modify a binding:
   ```json
   {
     "pane.split_horizontal": "Alt+H"
   }
   ```
3. Restart ViloxTerm
4. Press the new shortcut
5. Verify it works

### Conflict detection

Watch for warnings in the log:
```
[WARNING] Shortcut 'Ctrl+W' is already in use by action 'pane.close'
```

---

## KeybindingManager API

The KeybindingManager provides these methods:

### Querying bindings

```python
# Get current shortcut for an action
shortcut = manager.get_binding("pane.split_horizontal")
# Returns: "Ctrl+Shift+\\"

# Get all bindings
all_bindings = manager.get_bindings()
# Returns: {"pane.split_horizontal": "Ctrl+Shift+\\", ...}
```

### Modifying bindings

```python
# Set new binding
manager.set_binding("pane.split_horizontal", "Alt+H")
# Auto-saves to JSON

# Reset single binding to default
manager.reset_binding("pane.split_horizontal")

# Reset all bindings to defaults
manager.reset_to_defaults()
```

### Action registry

```python
# Get all registered actions
actions = manager.get_actions()

# Get actions by category
pane_actions = manager.get_actions_by_category("Pane")
```

---

## UI Integration (Pending)

### What's needed

The Keyboard Shortcuts preferences tab needs:

1. **KeySequenceEdit widget** - Captures key presses
2. **Shortcuts list widget** - Shows all actions grouped by category
3. **Edit/Reset buttons** - Modify individual shortcuts
4. **Reset All button** - Restore all defaults

### Current status

**Implemented** ✅:
- PreferencesDialog has `set_keybinding_manager()` method
- Manager instance is passed to dialog
- Placeholder tab exists

**Pending** ❌:
- KeySequenceEdit widget (in keybinding_manager widget)
- Keyboard shortcuts preferences tab UI
- Wiring between UI and manager

See `wip/keyboard-shortcuts-ui-TASKS.md` for implementation plan.

---

## Common Issues

### Shortcut not working

**Check**:
1. Is the action registered in `_setup_keybinding_manager()`?
2. Is the callback method defined?
3. Is the shortcut conflicting with another action?
4. Check logs for warnings about invalid shortcuts

### Binding not persisting

**Check**:
1. Is auto-save enabled? (`KeybindingManager(auto_save=True)`)
2. Is the storage path writable?
3. Is the JSON file valid? (malformed JSON will be ignored)

### Menu not showing shortcut

**Check**:
1. Is the action in `self.actions`?
2. Is the action passed to MenuButton?
3. Is the shortcut string valid for QKeySequence?

---

## References

### Internal docs
- `keyboard-shortcuts-SPEC.md` - Complete shortcut reference
- `wip/keyboard-shortcuts-ui-TASKS.md` - UI implementation tasks

### External docs
- [KeybindingManager widget README](../../../widgets/keybinding_manager/README.md)
- [KeybindingManager architecture](../../../widgets/keybinding_manager/docs/architecture-DESIGN.md)
- [QKeySequence documentation](https://doc.qt.io/qt-6/qkeysequence.html)

---

## Future Enhancements

**Phase 2** - UI for customization:
- Visual shortcut editor in preferences
- Conflict detection and warnings
- Search/filter shortcuts
- Import/export profiles

**Phase 3** - Advanced features:
- Context-aware bindings (different shortcuts in different modes)
- Chord sequences (e.g., `Ctrl+K Ctrl+S`)
- Mouse button bindings
- Multi-step macros
