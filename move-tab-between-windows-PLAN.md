# Move Tab Between Windows - Implementation Plan

## Overview
Add context menu option to move tabs between existing ViloxTerm windows without drag-and-drop.

## Changes Required

### 1. ViloxTermApp - Add Window ID Tracking
**File**: `apps/viloxterm/src/viloxterm/app.py`

- Add class variable: `_window_id_counter = 0`
- In `__init__`: Increment counter, assign `self._window_id`
- Update window title: `self.setWindowTitle(f"ViloxTerm - Window {self._window_id}")`
- Store reference to main/parent window for child windows

**Why**: All windows currently have identical "ViloxTerm" title, making them indistinguishable in menus and taskbar.

### 2. ChromeTabBar - Add New Signal
**File**: `widgets/chrome-tabbed-window/src/chrome_tabbed_window/view/chrome_tab_bar.py`

- Add `tabMoveToWindowRequested = Signal(int, object)` to carry tab index + target window reference

**Why**: Need communication channel between tab bar context menu and app-level transfer handler.

### 3. ChromeTabBar - Enhance Context Menu
**File**: `widgets/chrome-tabbed-window/src/chrome_tabbed_window/view/chrome_tab_bar.py:472`

Changes to `contextMenuEvent()` method:
- After "Move to New Window" action, add separator
- Add "Move to Window >" submenu
- Query parent for available windows via `parent().parent().get_available_target_windows()`
  - Navigation: ChromeTabBar → ChromeTabbedWindow → ViloxTermApp
- Populate submenu with window titles (from `windowTitle()`)
- Connect each action to emit `tabMoveToWindowRequested` with (tab_index, target_window)
- Disable submenu if only one window exists (no valid targets)

**Why**: Provides user-facing menu interface for selecting target window.

### 4. ViloxTermApp - Add Window Discovery
**File**: `apps/viloxterm/src/viloxterm/app.py`

Add `get_available_target_windows()` method:
- Collect all windows: traverse up to main window, then get all children from `_child_windows`
- Return list of `(window_title, window_ref)` tuples
- Exclude current window (self) from results
- Handle case where main window is calling (no parent) vs child window (has parent)

**Why**: Context menu needs to discover all available target windows for tab migration.

### 5. ViloxTermApp - Add Transfer Handler
**File**: `apps/viloxterm/src/viloxterm/app.py`

- Connect `tabMoveToWindowRequested` signal in `_setup_signals()`
- Implement `_move_tab_to_window(source_index: int, target_window: ViloxTermApp)`:
  1. Extract from source tab:
     - Widget via `self.widget(source_index)`
     - Tab text via `self.tabText(source_index)`
     - Tab icon via `self.tabIcon(source_index)`
  2. Remove tab from source window: `self.removeTab(source_index)`
  3. Add tab to target window: `target_window.addTab(widget, icon, text)`
  4. Focus target window: `target_window.activateWindow()`
  5. Focus new tab: `target_window.setCurrentIndex(new_index)`

**Why**: Core logic for transferring tab between windows while preserving widget state.

### 6. Edge Case: Last Tab Protection
**File**: `apps/viloxterm/src/viloxterm/app.py`

In `_move_tab_to_window()`, before removing tab:
- Check if `self.count() == 1` (this is the last tab)
- If true, create replacement tab first:
  - Increment `self._tab_counter`
  - Call `self.add_new_terminal_tab(f"Terminal {self._tab_counter}")`
- Then proceed with removal

**Why**: Prevents window with zero tabs, which could cause UI/state issues.

## Architecture Decisions

### Window Tracking Approach
- Use class-level counter for unique IDs (simple, deterministic)
- Main window doesn't track itself in `_child_windows` (current design)
- Child windows reference parent/main window (need to add)

### Signal Path
```
ChromeTabBar (context menu)
  └─> tabMoveToWindowRequested(int, object)
      └─> ViloxTermApp._move_tab_to_window()
```

### Window Discovery
```
Child Window → parent reference → Main Window → _child_windows list
```

## Testing Checklist

- [ ] Multiple windows show distinct titles (Window 1, Window 2, etc.)
- [ ] Right-click tab → verify "Move to Window >" appears
- [ ] Submenu shows other available windows by title
- [ ] Submenu disabled/hidden when only one window exists
- [ ] Moving tab transfers widget to target window
- [ ] Tab text and icon preserved after move
- [ ] Target window receives focus and switches to moved tab
- [ ] Last tab scenario creates replacement tab in source window
- [ ] Window tracking remains consistent after moves
- [ ] Terminal widget continues working after move (shared server)

## Edge Cases to Handle

1. **Last tab in window**: Create replacement before removal
2. **Single window**: Disable/hide submenu (no valid targets)
3. **Window closed during menu display**: Validate target still exists before transfer
4. **Rapid successive moves**: Ensure signals process correctly
5. **Terminal state preservation**: Widget reparenting must maintain PTY connection

## Files Modified

1. `apps/viloxterm/src/viloxterm/app.py` - Window ID tracking, discovery, transfer handler
2. `widgets/chrome-tabbed-window/src/chrome_tabbed_window/view/chrome_tab_bar.py` - Signal + context menu
