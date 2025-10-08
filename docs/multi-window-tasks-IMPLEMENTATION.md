# Multi-Window Feature - Implementation Tasks

**Goal**: Add "New Window" functionality to ViloxTerm
**Architecture**: Widget signals → Application handles window creation
**Reference**: See `multi-window-architecture-DESIGN.md`

---

## Phase 1: ChromeTabbedWindow Widget Enhancements

### Task 1.1: Add newWindowRequested Signal
**File**: `widgets/chrome-tabbed-window/src/chrome_tabbed_window/chrome_tabbed_window.py`

- [ ] Add `newWindowRequested = Signal()` to class signals section
- [ ] Add docstring explaining when signal is emitted
- [ ] Update class docstring to mention new signal

**Location**: After line 99 (after existing signals)

**Code**:
```python
# Add to signal section
newWindowRequested = Signal()  # Emitted when user requests new window
```

---

### Task 1.2: Add get_tab_data Helper Method
**File**: `widgets/chrome-tabbed-window/src/chrome_tabbed_window/chrome_tabbed_window.py`

- [ ] Add `get_tab_data(index)` method
- [ ] Return dict with widget, text, icon, tooltip
- [ ] Add error handling for invalid index
- [ ] Add docstring with example usage

**Location**: After QTabWidget API methods (around line 800)

**Code**:
```python
def get_tab_data(self, index: int) -> Optional[dict]:
    """Get tab data for transfer to another window.

    Useful for implementing tab detachment or window merging.

    Args:
        index: Tab index to get data for

    Returns:
        Dictionary with keys:
            - widget: The QWidget for this tab
            - text: Tab text
            - icon: Tab icon (QIcon)
            - tooltip: Tab tooltip text
        Returns None if index is invalid.

    Example:
        >>> tab_data = window.get_tab_data(0)
        >>> new_window.addTab(tab_data["widget"], tab_data["text"])
    """
    if index < 0 or index >= self.count():
        return None

    return {
        "widget": self.widget(index),
        "text": self.tabText(index),
        "icon": self.tabIcon(index),
        "tooltip": self.tabToolTip(index)
    }
```

---

### Task 1.3: Update ChromeTabbedWindow Documentation
**File**: `widgets/chrome-tabbed-window/README.md`

- [ ] Add "Multiple Windows" section
- [ ] Explain newWindowRequested signal
- [ ] Add example showing window creation
- [ ] Link to ViloxTerm as reference implementation

**Location**: After "Theme System Integration" section

---

## Phase 2: ViloxTerm Menu Integration

### Task 2.1: Add new_window_requested Signal to MenuButton
**File**: `apps/viloxterm/src/viloxterm/components/menu_button.py`

- [ ] Add `new_window_requested = Signal()` to MenuButton class (line ~20)
- [ ] Add "New Window" menu action at top of menu
- [ ] Connect menu action to signal
- [ ] Add keyboard shortcut hint (optional)

**Location**: Line 20 (add signal), Line 45 (add menu item)

**Code**:
```python
# Add signal (line ~20)
new_window_requested = Signal()

# Add menu item (line ~45, before other items)
def __init__(self, parent, keybinding_actions):
    super().__init__(parent)
    self._menu = QMenu(self)

    # Add "New Window" at top
    new_window_action = self._menu.addAction("New Window")
    new_window_action.triggered.connect(self.new_window_requested.emit)
    # Optional: new_window_action.setShortcut("Ctrl+Shift+N")

    self._menu.addSeparator()

    # Rest of menu items...
```

---

### Task 2.2: Connect Menu Signal in ViloxTermApp
**File**: `apps/viloxterm/src/viloxterm/app.py`

- [ ] Connect `menu_button.new_window_requested` signal in `_setup_signals()` method
- [ ] Create `_open_new_window()` method stub

**Location**: In `_setup_signals()` method (around line 120)

**Code**:
```python
def _setup_signals(self):
    # Existing signals...

    # Connect new window signal
    self.menu_button.new_window_requested.connect(self._open_new_window)
```

---

## Phase 3: ViloxTerm Window Management

### Task 3.1: Add Window Tracking Infrastructure
**File**: `apps/viloxterm/src/viloxterm/app.py`

- [ ] Add `_child_windows` list to `__init__`
- [ ] Add `_owns_server` flag to `__init__`
- [ ] Modify `__init__` to accept optional `shared_server` parameter
- [ ] Update constructor docstring

**Location**: In `__init__` method (around line 36-70)

**Code**:
```python
def __init__(self, shared_server=None, parent=None):
    """Initialize ViloxTerm application.

    Args:
        shared_server: Optional MultiSessionTerminalServer to share between windows.
                      If None, creates a new server (first window).
        parent: Parent widget (usually None for top-level window)
    """
    super().__init__(parent)

    # Track child windows (prevent garbage collection)
    self._child_windows = []

    # Create or use shared terminal server
    if shared_server:
        # Share server with other windows
        self.terminal_server = shared_server
        self._owns_server = False
        logger.info("Using shared terminal server")
    else:
        # Create own server (first window)
        self.terminal_server = MultiSessionTerminalServer(port=0)
        self.terminal_server.start()
        self._owns_server = True
        logger.info(f"Created terminal server on port {self.terminal_server.port}")

    # Rest of initialization...
```

---

### Task 3.2: Implement _open_new_window Method
**File**: `apps/viloxterm/src/viloxterm/app.py`

- [ ] Create `_open_new_window()` method
- [ ] Create new ViloxTermApp instance with shared server
- [ ] Track window in `_child_windows` list
- [ ] Connect cleanup handler
- [ ] Show the window
- [ ] Add logging

**Location**: After `_show_terminal_theme_dialog()` method (around line 490)

**Code**:
```python
def _open_new_window(self) -> None:
    """Open a new ViloxTerm window.

    Creates a new window instance that shares the same terminal server
    for memory efficiency. The new window is tracked to prevent garbage
    collection.
    """
    logger.info("Opening new ViloxTerm window")

    # Create new window with shared server
    new_window = ViloxTermApp(shared_server=self.terminal_server)

    # Track window to prevent garbage collection
    self._child_windows.append(new_window)

    # Handle cleanup when child window closes
    new_window.destroyed.connect(
        lambda: self._on_child_window_closed(new_window)
    )

    # Show the window
    new_window.show()

    logger.info(f"New window created. Total windows: {len(self._child_windows) + 1}")
```

---

### Task 3.3: Implement Window Cleanup Handler
**File**: `apps/viloxterm/src/viloxterm/app.py`

- [ ] Create `_on_child_window_closed()` method
- [ ] Remove window from tracking list
- [ ] Add logging

**Location**: After `_open_new_window()` method

**Code**:
```python
def _on_child_window_closed(self, window) -> None:
    """Handle cleanup when a child window closes.

    Args:
        window: The ViloxTermApp instance that was closed
    """
    if window in self._child_windows:
        self._child_windows.remove(window)
        logger.info(f"Child window closed. Remaining windows: {len(self._child_windows) + 1}")
```

---

### Task 3.4: Update closeEvent for Server Cleanup
**File**: `apps/viloxterm/src/viloxterm/app.py`

- [ ] Modify `closeEvent()` to check `_owns_server` flag
- [ ] Only shutdown server if this window owns it
- [ ] Add logging

**Location**: Find existing `closeEvent()` or add after cleanup methods

**Code**:
```python
def closeEvent(self, event) -> None:
    """Handle application shutdown.

    If this window owns the terminal server, shut it down.
    Otherwise, just close the window (server is shared).
    """
    logger.info("ViloxTerm window closing")

    # Only shutdown server if we own it
    if self._owns_server:
        logger.info("Shutting down terminal server (owner window closing)")
        self.terminal_server.shutdown()
    else:
        logger.info("Window closed (server owned by another window)")

    super().closeEvent(event)
```

---

## Phase 4: Testing & Verification

### Task 4.1: Manual Testing Checklist

- [ ] **Test 1: Basic Window Creation**
  - Start ViloxTerm
  - Click hamburger menu → "New Window"
  - Verify second window appears
  - Verify window title is correct
  - Verify window has all UI elements (menu, tabs, etc.)

- [ ] **Test 2: Terminal Functionality**
  - Create terminal in first window
  - Create terminal in second window
  - Run `echo "Window 1"` in first window
  - Run `echo "Window 2"` in second window
  - Verify both terminals work independently

- [ ] **Test 3: Multiple Terminals Per Window**
  - In first window: Create 3 terminals in different tabs
  - In second window: Create 2 terminals in different tabs
  - Split panes in both windows
  - Verify all terminals work correctly

- [ ] **Test 4: Window Independence**
  - Close first window
  - Verify second window stays open
  - Verify terminals in second window still work
  - Create new terminal in second window
  - Verify it works

- [ ] **Test 5: Theme System**
  - Open two windows
  - Change theme in first window (hamburger → Change App Theme)
  - Verify theme saves to config
  - Open third window
  - Verify new window loads saved theme

- [ ] **Test 6: Clean Shutdown**
  - Open 3 windows
  - Close all windows
  - Check `ps aux | grep viloxterm` - should be no processes
  - Check `ps aux | grep MultiSessionTerminalServer` - should be no processes
  - Verify no zombie processes

- [ ] **Test 7: Shared Server Verification**
  - Open two windows
  - Check server port in logs (both should show same port)
  - Close first window (owner)
  - Verify second window terminals stop working (expected - server shut down)
  - OR verify server stays alive (if we implement server handoff)

- [ ] **Test 8: Memory Usage**
  - Start ViloxTerm, note memory usage
  - Open 5 windows
  - Create 2 terminals per window
  - Check total memory usage
  - Compare to 5 separate ViloxTerm processes
  - Verify shared server reduces memory

- [ ] **Test 9: Window Positions**
  - Open two windows
  - Move them to different screen positions
  - Close and reopen ViloxTerm
  - Verify windows open in reasonable positions (not stacked)

- [ ] **Test 10: Error Handling**
  - Try to open 20 windows rapidly
  - Verify no crashes
  - Close all windows
  - Verify clean shutdown

---

### Task 4.2: Code Quality Checks

- [ ] Run black formatter on modified files
- [ ] Run ruff linter on modified files
- [ ] Check for any TODO/FIXME comments
- [ ] Verify logging statements use appropriate levels
- [ ] Check for memory leaks (window references)

**Commands**:
```bash
# Format
black apps/viloxterm/src/viloxterm/app.py
black apps/viloxterm/src/viloxterm/components/menu_button.py
black widgets/chrome-tabbed-window/src/chrome_tabbed_window/chrome_tabbed_window.py

# Lint
ruff check apps/viloxterm/src/
ruff check widgets/chrome-tabbed-window/src/
```

---

### Task 4.3: Documentation Updates

- [ ] Update ViloxTerm README.md with "Multiple Windows" section
- [ ] Add screenshot showing multiple windows (optional)
- [ ] Update CHANGELOG.md with feature addition
- [ ] Verify all docstrings are complete

---

## Phase 5: Git Commit & Push

### Task 5.1: Review Changes
- [ ] Run `git status` to see all modified files
- [ ] Run `git diff` to review changes
- [ ] Verify no unintended changes
- [ ] Check for debug print statements (remove them)

---

### Task 5.2: Commit Changes
- [ ] Stage all files: `git add -A`
- [ ] Create commit with descriptive message
- [ ] Push to remote: `git push`

**Commit Message Template**:
```
feat(viloxterm): add multiple window support

Phase 1: ChromeTabbedWindow Enhancements
- Add newWindowRequested signal
- Add get_tab_data() helper method for tab transfer
- Update documentation

Phase 2: ViloxTerm Menu Integration
- Add "New Window" menu option
- Connect menu signal to window creation

Phase 3: Window Management
- Implement shared terminal server between windows
- Track child windows to prevent garbage collection
- Handle clean shutdown when owner window closes
- Support multiple independent windows

Features:
- Open multiple ViloxTerm windows from menu
- Windows share terminal server for memory efficiency
- Each window operates independently
- Clean shutdown of all windows
- Theme system works across all windows

Testing:
- Manual testing completed for all scenarios
- Memory usage verified (shared server reduces usage)
- Clean shutdown verified (no zombie processes)
```

---

## Success Criteria

✅ User can open new windows via hamburger menu
✅ New windows contain independent terminal tabs
✅ Terminals work correctly in all windows
✅ Windows share terminal server (memory efficient)
✅ Theme system works in all windows
✅ Closing one window doesn't affect others
✅ Closing owner window shuts down server cleanly
✅ No memory leaks or zombie processes
✅ All manual tests pass

---

## Future Enhancements (Post-MVP)

**Not in this task list, for future consideration:**

- [ ] Tab detachment (drag tab to new window)
- [ ] Drag tab between windows to merge
- [ ] "Merge All Windows" menu option
- [ ] Remember window positions across sessions
- [ ] Keyboard shortcut for new window (Ctrl+Shift+N)
- [ ] Server handoff (when owner window closes, transfer to another window)
- [ ] "Close All Windows" option
- [ ] Multi-monitor awareness

---

## Notes & Decisions

### Server Strategy Decision
**Chosen**: Share server between windows (memory efficient)
**Alternative**: Each window creates own server (isolated but uses more memory)

**Reasoning**:
- Matches current multi-tab architecture
- 63% memory reduction benefit applies
- Simpler initial implementation
- Can change later if needed

### Window Ownership
**Primary Window**: First window created (owns server)
**Child Windows**: Windows opened from menu (share server)

**Behavior**: When primary closes, server shuts down, all windows lose terminals
**Future**: Could transfer ownership to another window

---

## Implementation Status

**Started**: 2025-10-08
**Target Completion**: TBD
**Current Phase**: Planning Complete ✅

---

**Last Updated**: 2025-10-08
