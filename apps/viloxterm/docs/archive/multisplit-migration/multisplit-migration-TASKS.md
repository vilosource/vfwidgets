# ViloxTerm MultisplitWidget v0.2.0 Migration - Task Breakdown

**Source**: multisplit-migration-WIP.md
**Status**: Ready to Execute
**Estimated Total Time**: 60-90 minutes

---

## Task 0: Pre-Implementation Verification

### Task 0.1: Verify TerminalWidget API

**Objective**: Check if TerminalWidget exposes session_id attribute

**File to Check**: `vfwidgets/widgets/terminal_widget/src/vfwidgets_terminal/terminal.py`

**Steps**:
1. Read TerminalWidget class definition
2. Look for `session_id` attribute or property
3. If missing, note that we need to add it

**Success Criteria**:
- [ ] Confirmed `session_id` is accessible from TerminalWidget instances

**Output**: Document finding in implementation notes

**Estimated Time**: 5 minutes

---

### Task 0.2: Verify MultiSessionTerminalServer API

**Objective**: Check if MultiSessionTerminalServer has terminate_session() method

**File to Check**: `vfwidgets/widgets/terminal_widget/src/vfwidgets_terminal/multi_session_server.py`

**Steps**:
1. Read MultiSessionTerminalServer class definition
2. Look for `terminate_session()` or `close_session()` method
3. Check method signature and behavior
4. If missing, note that we need to add it

**Success Criteria**:
- [ ] Confirmed `terminate_session(session_id)` method exists
- [ ] Understood how to properly terminate sessions

**Output**: Document method signature and usage

**Estimated Time**: 5 minutes

---

## Phase 1: Required Migration (Breaking Changes)

### Task 1.1: Update Import in app.py

**Objective**: Modernize imports to use v0.2.0 clean package exports

**File**: `/home/kuja/GitHub/vfwidgets/apps/viloxterm/src/viloxterm/app.py`

**Current Code (Lines 15-16)**:
```python
from vfwidgets_multisplit import MultisplitWidget, SplitterStyle
from vfwidgets_multisplit.core.types import WherePosition
```

**New Code**:
```python
from vfwidgets_multisplit import MultisplitWidget, SplitterStyle, WherePosition
```

**Steps**:
1. Open `app.py`
2. Locate lines 15-16
3. Replace with single import line
4. Save file

**Success Criteria**:
- [ ] Import statement updated
- [ ] File saves without syntax errors
- [ ] No other code changes needed (WherePosition usage is the same)

**Estimated Time**: 2 minutes

---

### Task 1.2: Update Import in terminal_provider.py

**Objective**: Use v0.2.0 main package import for WidgetProvider

**File**: `/home/kuja/GitHub/vfwidgets/apps/viloxterm/src/viloxterm/providers/terminal_provider.py`

**Current Code (Line 8)**:
```python
from vfwidgets_multisplit.view.container import WidgetProvider
```

**New Code**:
```python
from vfwidgets_multisplit import WidgetProvider
```

**Steps**:
1. Open `terminal_provider.py`
2. Locate line 8
3. Replace import statement
4. Save file

**Success Criteria**:
- [ ] Import statement updated
- [ ] File saves without syntax errors
- [ ] WidgetProvider class is still accessible

**Estimated Time**: 1 minute

---

### Task 1.3: Add session_id Tracking to TerminalProvider

**Objective**: Track session IDs so we can clean them up in widget_closing()

**File**: `/home/kuja/GitHub/vfwidgets/apps/viloxterm/src/viloxterm/providers/terminal_provider.py`

**Location**: Add to class `__init__` and `provide_widget`

**Code to Add**:

```python
# In __init__ method (after line 28):
self.pane_to_session: dict[str, str] = {}  # Map pane_id -> session_id

# In provide_widget method (after line 44, before line 45):
# Store session mapping for cleanup
self.pane_to_session[pane_id] = session_id
```

**Steps**:
1. Open `terminal_provider.py`
2. Add `self.pane_to_session = {}` to `__init__` method
3. Add `self.pane_to_session[pane_id] = session_id` in `provide_widget` after session creation
4. Save file

**Success Criteria**:
- [ ] Dictionary initialized in `__init__`
- [ ] Session mapping stored in `provide_widget`
- [ ] No syntax errors

**Rationale**: We need to know which session belongs to which pane for cleanup

**Estimated Time**: 3 minutes

---

### Task 1.4: Implement widget_closing() Lifecycle Hook

**Objective**: Properly terminate terminal sessions when panes are closed

**File**: `/home/kuja/GitHub/vfwidgets/apps/viloxterm/src/viloxterm/providers/terminal_provider.py`

**Location**: Add new method after `provide_widget` method (after line 55)

**Code to Add**:

```python
    def widget_closing(self, widget_id: str, pane_id: str, widget: QWidget) -> None:
        """Clean up terminal session when pane closes.

        Called automatically by MultisplitWidget v0.2.0 before widget removal.
        Ensures terminal sessions are properly terminated on the server.

        Args:
            widget_id: Widget identifier
            pane_id: Pane identifier
            widget: The TerminalWidget being closed
        """
        # Get session_id from our tracking dict
        session_id = self.pane_to_session.get(pane_id)

        if session_id:
            try:
                # Terminate session on server
                self.server.terminate_session(session_id)
                logger.info(f"Terminated session {session_id} for pane {pane_id}")

                # Remove from tracking
                del self.pane_to_session[pane_id]

            except Exception as e:
                logger.error(f"Failed to terminate session {session_id}: {e}")
        else:
            logger.warning(f"No session found for pane {pane_id}")
```

**Steps**:
1. Open `terminal_provider.py`
2. Add method after `provide_widget` (around line 56)
3. Ensure proper indentation (method of TerminalProvider class)
4. Save file

**Success Criteria**:
- [ ] Method added with correct signature
- [ ] Proper error handling with try/except
- [ ] Logging for debugging
- [ ] Cleans up tracking dictionary

**Dependencies**:
- Requires Task 0.2 (verify server has terminate_session)
- Requires Task 1.3 (session tracking dict)

**Estimated Time**: 10 minutes

---

### Task 1.5: Test Phase 1 - Import Changes

**Objective**: Verify app runs with new imports

**Steps**:
1. Navigate to viloxterm directory
2. Run: `python -m viloxterm`
3. Verify app starts without import errors
4. Close app

**Success Criteria**:
- [ ] App starts successfully
- [ ] No import errors in console
- [ ] Window appears normally

**Expected Output**: App runs, no errors

**Estimated Time**: 2 minutes

---

### Task 1.6: Test Phase 1 - Session Cleanup

**Objective**: Verify terminal sessions are cleaned up when panes close

**Steps**:
1. Run app: `python -m viloxterm`
2. Note initial session count (check server logs)
3. Split pane horizontally (Ctrl+Shift+H)
4. Split again vertically (Ctrl+Shift+V)
5. Close panes one by one (Ctrl+W)
6. Check server logs for "Terminated session" messages
7. Verify session count decreases

**Success Criteria**:
- [ ] App starts successfully
- [ ] Panes can be split
- [ ] Panes can be closed
- [ ] Log shows "Terminated session" for each closed pane
- [ ] No session leaks (session count returns to baseline)

**Expected Output**:
```
INFO - Created terminal session: sess_123 for pane: pane_abc
INFO - Terminated session sess_123 for pane pane_abc
```

**Debugging**:
- If no "Terminated session" logs → widget_closing() not being called
- If errors → check server API compatibility

**Estimated Time**: 10 minutes

---

## Phase 2: Optional Enhancements

### Task 2.1: Add focus_changed Signal Connection

**Objective**: Set up signal to handle focus changes

**File**: `/home/kuja/GitHub/vfwidgets/apps/viloxterm/src/viloxterm/app.py`

**Location**: In `add_new_terminal_tab` method, after line 187

**Current Code (Line 187)**:
```python
# Connect to pane_added signal for auto-focus on split
multisplit.pane_added.connect(self._on_pane_added)
```

**Add After**:
```python
# Connect to focus_changed signal for visual indicators (v0.2.0)
multisplit.focus_changed.connect(self._on_focus_changed)
```

**Steps**:
1. Open `app.py`
2. Locate `add_new_terminal_tab` method (~line 187)
3. Add signal connection after `pane_added` connection
4. Save file

**Success Criteria**:
- [ ] Signal connection added
- [ ] No syntax errors
- [ ] Proper indentation

**Estimated Time**: 1 minute

---

### Task 2.2: Implement _on_focus_changed Handler

**Objective**: Add visual focus indicators to terminals

**File**: `/home/kuja/GitHub/vfwidgets/apps/viloxterm/src/viloxterm/app.py`

**Location**: Add new method after `_on_pane_added` (after line 238)

**Code to Add**:

```python
    def _on_focus_changed(self, old_pane_id: str, new_pane_id: str) -> None:
        """Handle focus changes - add visual indicators.

        Adds a subtle border to the focused terminal pane for better UX
        in multi-pane layouts.

        Args:
            old_pane_id: Pane that lost focus (empty string if none)
            new_pane_id: Pane that gained focus (empty string if none)
        """
        multisplit = self.currentWidget()
        if not isinstance(multisplit, MultisplitWidget):
            return

        # Clear old focus border
        if old_pane_id:
            old_widget = multisplit.get_widget(old_pane_id)
            if old_widget:
                old_widget.setStyleSheet("")

        # Add new focus border
        if new_pane_id:
            new_widget = multisplit.get_widget(new_pane_id)
            if new_widget:
                # Subtle blue border for focused pane
                # TODO: Make color theme-aware
                new_widget.setStyleSheet("border: 2px solid #0078d4")

        logger.debug(
            f"Focus changed: "
            f"{old_pane_id[:8] if old_pane_id else 'None'} -> "
            f"{new_pane_id[:8] if new_pane_id else 'None'}"
        )
```

**Steps**:
1. Open `app.py`
2. Add method after `_on_pane_added` method (~line 239)
3. Ensure proper indentation (method of ViloxTermApp class)
4. Save file

**Success Criteria**:
- [ ] Method added with correct signature
- [ ] Uses `get_widget()` API from v0.2.0
- [ ] Proper logging
- [ ] Handles empty string IDs

**Note**: Border color #0078d4 is a subtle blue. Can be customized later for themes.

**Estimated Time**: 8 minutes

---

### Task 2.3: Test Phase 2 - Focus Indicators

**Objective**: Verify visual focus indicators work

**Steps**:
1. Run app: `python -m viloxterm`
2. Split pane horizontally (Ctrl+Shift+H)
3. Click in left terminal pane
4. Verify blue border appears on left pane
5. Click in right terminal pane
6. Verify border moves to right pane (left border disappears)
7. Split vertically (Ctrl+Shift+V)
8. Click between all panes
9. Verify border always shows on focused pane

**Success Criteria**:
- [ ] Border appears on focused pane
- [ ] Border disappears from unfocused pane
- [ ] Border color is visible (blue #0078d4)
- [ ] Works with multiple panes (3-4 splits)
- [ ] No console errors

**Expected Behavior**:
- Only one pane should have border at a time
- Border should follow clicks between panes

**Debugging**:
- If no border → Check if signal is connected
- If border doesn't move → Check old_pane_id clearing
- If multiple borders → Check stylesheet clearing logic

**Estimated Time**: 5 minutes

---

### Task 2.4: Enhance split_pane Auto-Focus (Optional)

**Objective**: Demonstrate widget lookup API usage

**File**: `/home/kuja/GitHub/vfwidgets/apps/viloxterm/src/viloxterm/app.py`

**Location**: In `_on_pane_added` method (line 234-237)

**Current Code**:
```python
if self._splitting_in_progress:
    multisplit = self.currentWidget()
    if isinstance(multisplit, MultisplitWidget):
        multisplit.focus_pane(pane_id)
        logger.debug(f"Auto-focused new pane after split: {pane_id}")
    self._splitting_in_progress = False
```

**Enhanced Code**:
```python
if self._splitting_in_progress:
    multisplit = self.currentWidget()
    if isinstance(multisplit, MultisplitWidget):
        # Focus the new pane
        multisplit.focus_pane(pane_id)

        # Use v0.2.0 widget lookup API to access terminal
        terminal = multisplit.get_widget(pane_id)
        if terminal and isinstance(terminal, TerminalWidget):
            # Terminal is focused and ready for input
            logger.debug(f"Auto-focused new terminal in pane: {pane_id}")

    self._splitting_in_progress = False
```

**Steps**:
1. Open `app.py`
2. Locate `_on_pane_added` method (~line 234)
3. Replace focus logic with enhanced version
4. Add TerminalWidget import at top if needed
5. Save file

**Success Criteria**:
- [ ] Code updated
- [ ] Uses `get_widget()` API
- [ ] No syntax errors
- [ ] Auto-focus still works

**Note**: This is mainly demonstrative - shows how to access widgets. Could be extended for terminal-specific setup.

**Estimated Time**: 5 minutes

---

## Phase 3: Final Validation

### Task 3.1: Comprehensive Regression Test

**Objective**: Verify all ViloxTerm features still work

**Test Cases**:

1. **Basic Functionality**
   - [ ] App starts without errors
   - [ ] Window appears in frameless mode
   - [ ] Window controls work (minimize, maximize, close)

2. **Tab Management**
   - [ ] Create new tab (+ button)
   - [ ] Switch between tabs
   - [ ] Close tab (X button)
   - [ ] Close tab with Ctrl+Shift+W
   - [ ] Last tab closes window

3. **Pane Splitting**
   - [ ] Split horizontal (Ctrl+Shift+H)
   - [ ] Split vertical (Ctrl+Shift+V)
   - [ ] Multiple splits (create 4 panes)
   - [ ] Close pane (Ctrl+W)
   - [ ] Cannot close last pane

4. **Terminal Functionality**
   - [ ] Type in terminal
   - [ ] Run commands (ls, pwd, etc.)
   - [ ] Terminal output displays correctly
   - [ ] Each pane has independent terminal

5. **Focus Management**
   - [ ] Click between panes changes focus
   - [ ] Focus border appears (Phase 2 only)
   - [ ] Keyboard input goes to focused terminal

6. **Menu & Theme**
   - [ ] Menu button works
   - [ ] Theme dialog opens
   - [ ] Shortcuts shown in menu

7. **Session Cleanup**
   - [ ] Split panes (3-4 terminals)
   - [ ] Close panes one by one
   - [ ] Check logs for session cleanup
   - [ ] No session leaks

8. **No Flashing**
   - [ ] Split pane multiple times rapidly
   - [ ] No visual flashing/flickering
   - [ ] Smooth split animations

**Estimated Time**: 15 minutes

---

### Task 3.2: Performance Validation

**Objective**: Verify no performance regressions

**Test Cases**:

1. **Split Performance**
   - [ ] Split 10+ panes
   - [ ] Splits happen quickly (<100ms)
   - [ ] No lag or stuttering

2. **Memory Usage**
   - [ ] Note baseline memory (1 pane)
   - [ ] Create 10 panes
   - [ ] Note memory increase
   - [ ] Close all panes
   - [ ] Memory returns to near baseline
   - [ ] No memory leaks

3. **Rendering Performance**
   - [ ] No flashing during splits (Fixed Container)
   - [ ] Terminal output renders smoothly
   - [ ] Multiple terminals can output simultaneously

**Expected Results**:
- Splits should be instant
- Memory should be cleaned up when panes close
- No flashing (key v0.2.0 benefit)

**Estimated Time**: 10 minutes

---

### Task 3.3: Documentation Update

**Objective**: Document MultisplitWidget v0.2.0 usage in ViloxTerm

**File**: `/home/kuja/GitHub/vfwidgets/apps/viloxterm/README.md`

**Content to Add**:

Section to add under "Architecture" or "Dependencies":

```markdown
### MultisplitWidget Integration

ViloxTerm uses [MultisplitWidget v0.2.0](../../widgets/multisplit_widget/) for terminal pane management:

- **Fixed Container Architecture** - Eliminates flashing during splits
- **Widget Lifecycle Hooks** - Automatic session cleanup via `widget_closing()`
- **Focus Tracking** - Visual indicators show active terminal pane
- **Widget Lookup APIs** - Direct access to terminal widgets

Each tab contains a `MultisplitWidget` that can be dynamically split into multiple terminal panes. Terminal sessions are managed by a shared `MultiSessionTerminalServer` for memory efficiency.

See `providers/terminal_provider.py` for the `WidgetProvider` implementation.
```

**Steps**:
1. Open `README.md`
2. Find appropriate section (Architecture or Dependencies)
3. Add MultisplitWidget integration section
4. Save file

**Success Criteria**:
- [ ] Documentation added
- [ ] Links to MultisplitWidget docs
- [ ] Describes key features used
- [ ] Markdown renders correctly

**Estimated Time**: 5 minutes

---

## Implementation Tracking

Use TodoWrite to track progress through tasks:

```
Phase 0: Pre-Implementation (10 min)
- [ ] Task 0.1: Verify TerminalWidget API
- [ ] Task 0.2: Verify MultiSessionTerminalServer API

Phase 1: Required Migration (25 min)
- [ ] Task 1.1: Update import in app.py
- [ ] Task 1.2: Update import in terminal_provider.py
- [ ] Task 1.3: Add session_id tracking
- [ ] Task 1.4: Implement widget_closing() hook
- [ ] Task 1.5: Test imports
- [ ] Task 1.6: Test session cleanup

Phase 2: Enhancements (20 min)
- [ ] Task 2.1: Add focus_changed signal connection
- [ ] Task 2.2: Implement _on_focus_changed handler
- [ ] Task 2.3: Test focus indicators
- [ ] Task 2.4: Enhance split auto-focus (optional)

Phase 3: Validation (30 min)
- [ ] Task 3.1: Comprehensive regression test
- [ ] Task 3.2: Performance validation
- [ ] Task 3.3: Documentation update
```

---

## Summary

**Total Tasks**: 15 tasks
**Minimum Path**: Phase 0 + Phase 1 (8 tasks, ~35 min)
**Recommended Path**: Phase 0 + Phase 1 + Phase 2 (12 tasks, ~55 min)
**Complete Path**: All phases (15 tasks, ~85 min)

**Next Step**: Begin with Task 0.1 (Verify TerminalWidget API)
