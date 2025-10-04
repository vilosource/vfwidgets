# ViloxTerm MultisplitWidget v0.2.0 Migration Plan

**Status**: Ready for Implementation
**Created**: 2025-10-04
**Target**: Migrate ViloxTerm to MultisplitWidget v0.2.0

---

## Executive Summary

ViloxTerm currently uses MultisplitWidget v0.1.x with several breaking changes in v0.2.0. This plan outlines the migration strategy to adopt v0.2.0 and leverage new features to improve terminal management and fix the flashing issues.

### Key Benefits of Migration

1. **Fixed Container Architecture** - Eliminates flashing during splits (root cause fixed)
2. **Widget Lookup APIs** - Simplified terminal widget access (no manual tracking)
3. **Lifecycle Hooks** - Proper terminal session cleanup on pane close
4. **Focus Tracking** - Better focus management with `focus_changed` signal
5. **Cleaner Imports** - Simplified package structure

---

## Current Usage Analysis

### Files Affected

1. **app.py** (Primary user)
   - Line 15-16: Import statements ❌ OLD
   - Line 187: Signal connection ❌ MISSING
   - Line 183: Constructor - ✅ OK but can be improved

2. **terminal_provider.py** (WidgetProvider implementation)
   - Line 8: Import statement ❌ OLD
   - Line 30-55: `provide_widget()` - ✅ OK
   - **MISSING**: `widget_closing()` lifecycle hook ❌

### Issues Identified

#### 1. Old Import Paths (Breaking Change)

**Current (app.py:15-16)**:
```python
from vfwidgets_multisplit import MultisplitWidget, SplitterStyle
from vfwidgets_multisplit.core.types import WherePosition
```

**Current (terminal_provider.py:8)**:
```python
from vfwidgets_multisplit.view.container import WidgetProvider
```

**Problem**: Deep imports from internal modules - will continue to work but not recommended in v0.2.0

#### 2. Missing `widget_closing()` Hook (New Feature)

**Current**: TerminalProvider doesn't implement `widget_closing()`

**Problem**: Terminal sessions are not properly cleaned up when panes close. Sessions remain alive on the server, wasting resources.

#### 3. No `pane_added` Signal Handler (Current Code Works)

**Current (app.py:187)**:
```python
multisplit.pane_added.connect(self._on_pane_added)
```

**Status**: ✅ This signal still exists and works in v0.2.0

#### 4. Missing `focus_changed` Signal (New Feature)

**Current**: Not using `focus_changed` signal

**Opportunity**: Could add visual focus indicators for better UX (e.g., highlight focused terminal pane)

#### 5. No Widget Lookup Usage (New Feature)

**Current**: Auto-focus logic uses `multisplit.focus_pane()` directly (line 236)

**Opportunity**: Could use `get_widget()` to access terminal widgets for operations

---

## Breaking Changes Impact

### 1. Import Paths (Low Impact)

**Old imports still work** but are not recommended. Migration is optional but recommended for future-proofing.

**Priority**: Medium
**Risk**: Low
**Effort**: Minimal

### 2. `widget_closing()` Signature (No Impact)

ViloxTerm **doesn't currently implement** `widget_closing()`, so the signature change doesn't break anything. However, **not implementing it** means terminal sessions leak.

**Priority**: HIGH (resource leak)
**Risk**: Low
**Effort**: Low

---

## Migration Plan

### Phase 1: Breaking Changes (Required)

#### Task 1.1: Update Import Statements

**File**: `app.py`

**Change**:
```python
# OLD
from vfwidgets_multisplit import MultisplitWidget, SplitterStyle
from vfwidgets_multisplit.core.types import WherePosition

# NEW
from vfwidgets_multisplit import MultisplitWidget, SplitterStyle, WherePosition
```

**File**: `terminal_provider.py`

**Change**:
```python
# OLD
from vfwidgets_multisplit.view.container import WidgetProvider

# NEW
from vfwidgets_multisplit import WidgetProvider
```

**Effort**: 2 minutes
**Risk**: None
**Testing**: Run app, verify no import errors

---

#### Task 1.2: Implement `widget_closing()` Hook

**File**: `terminal_provider.py`

**Add**:
```python
def widget_closing(self, widget_id: str, pane_id: str, widget: QWidget) -> None:
    """Clean up terminal session when pane closes.

    Called automatically before widget removal - ensures terminal
    sessions are properly terminated on the server.

    Args:
        widget_id: Widget identifier
        pane_id: Pane identifier
        widget: The TerminalWidget being closed
    """
    # Extract session_id from terminal widget
    if isinstance(widget, TerminalWidget):
        session_id = widget.session_id  # Assuming TerminalWidget exposes this

        # Terminate session on server
        try:
            self.server.terminate_session(session_id)
            logger.info(f"Terminated session {session_id} for pane {pane_id}")
        except Exception as e:
            logger.error(f"Failed to terminate session {session_id}: {e}")
    else:
        logger.warning(f"widget_closing called on non-terminal widget: {type(widget)}")
```

**Dependencies**:
- Check if `TerminalWidget` exposes `session_id` attribute
- Check if `MultiSessionTerminalServer` has `terminate_session()` method
- Add these if missing

**Effort**: 15-30 minutes (including dependency checks)
**Risk**: Low (optional hook, won't break if fails)
**Testing**:
- Split panes, close panes, verify sessions are terminated
- Check server session count before/after

---

### Phase 2: New Features (Optional but Recommended)

#### Task 2.1: Add Visual Focus Indicators

**File**: `app.py`

**Add to `__init__`**:
```python
# In add_new_terminal_tab(), after creating multisplit:
multisplit.focus_changed.connect(self._on_focus_changed)
```

**Add new method**:
```python
def _on_focus_changed(self, old_pane_id: str, new_pane_id: str) -> None:
    """Handle focus changes - add visual indicators.

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
            # Remove focus styling (adjust for your theme)
            old_widget.setStyleSheet("")

    # Add new focus border
    if new_pane_id:
        new_widget = multisplit.get_widget(new_pane_id)
        if new_widget:
            # Add focus styling (adjust for your theme)
            new_widget.setStyleSheet("border: 2px solid #0078d4")

    logger.debug(f"Focus changed: {old_pane_id[:8] if old_pane_id else 'None'} -> {new_pane_id[:8] if new_pane_id else 'None'}")
```

**Benefits**:
- Clear visual indication of focused terminal
- Helps users understand which terminal receives input
- Improves multi-pane workflow

**Effort**: 10 minutes
**Risk**: None (purely additive)
**Testing**: Split panes, click between them, verify border appears

---

#### Task 2.2: Use Widget Lookup for Operations

**File**: `app.py`

**Current (line 234-236)**:
```python
if self._splitting_in_progress:
    multisplit = self.currentWidget()
    if isinstance(multisplit, MultisplitWidget):
        multisplit.focus_pane(pane_id)
```

**Enhanced**:
```python
if self._splitting_in_progress:
    multisplit = self.currentWidget()
    if isinstance(multisplit, MultisplitWidget):
        # Focus the pane
        multisplit.focus_pane(pane_id)

        # Optional: Access the terminal widget for additional setup
        terminal = multisplit.get_widget(pane_id)
        if terminal and isinstance(terminal, TerminalWidget):
            # Could do terminal-specific setup here
            # e.g., terminal.set_theme(current_theme)
            pass
```

**Benefits**:
- Demonstrates new widget lookup API
- Enables terminal-specific operations after split
- Cleaner than manual tracking

**Effort**: 5 minutes
**Risk**: None
**Testing**: Split panes, verify behavior unchanged

---

#### Task 2.3: Add Session Save/Restore (Advanced)

**Benefit**: Restore terminal layout across app restarts

**File**: `app.py`

**Add to `__init__`**:
```python
# Load previous session
self.session_file = Path.home() / ".config" / "viloxterm" / "layout.json"
self._load_session()
```

**Add methods**:
```python
def _load_session(self) -> None:
    """Load saved terminal layout."""
    if self.session_file.exists():
        try:
            with open(self.session_file, 'r') as f:
                session_data = f.read()

            # Load into current tab's multisplit
            multisplit = self.currentWidget()
            if isinstance(multisplit, MultisplitWidget):
                multisplit.load_session(session_data)
                logger.info("Loaded saved terminal layout")
        except Exception as e:
            logger.error(f"Failed to load session: {e}")

def _save_session(self) -> None:
    """Save current terminal layout."""
    multisplit = self.currentWidget()
    if isinstance(multisplit, MultisplitWidget):
        try:
            session_data = multisplit.save_session()
            self.session_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.session_file, 'w') as f:
                f.write(session_data)
            logger.info("Saved terminal layout")
        except Exception as e:
            logger.error(f"Failed to save session: {e}")

def closeEvent(self, event) -> None:
    """Handle window close event."""
    # Save session before shutdown
    self._save_session()

    # Shutdown terminal server
    logger.info("Shutting down terminal server...")
    self.terminal_server.shutdown()
    logger.info("Terminal server shut down")

    # Accept close event
    super().closeEvent(event)
    event.accept()
```

**Caveat**: Session restore only saves **layout structure** (pane IDs). Terminal **session state** (command history, output) is not preserved - terminals will start fresh.

**Effort**: 20 minutes
**Risk**: Medium (file I/O, JSON parsing)
**Testing**: Create layout, close app, reopen, verify layout restored

---

### Phase 3: Testing & Validation

#### Test Plan

1. **Import Tests**
   - Run app after updating imports
   - Verify no import errors
   - Check all MultisplitWidget features work

2. **Lifecycle Tests**
   - Create multiple panes
   - Close panes one by one
   - Verify terminal sessions are terminated (check server log)
   - No session leaks after closing all panes

3. **Focus Tests** (if implementing focus indicators)
   - Split panes multiple times
   - Click between different terminal panes
   - Verify focus border appears on correct pane
   - Test with different themes

4. **Widget Lookup Tests**
   - Split panes
   - Verify auto-focus works (should be unchanged)
   - If enhanced, verify terminal setup runs

5. **Session Tests** (if implementing save/restore)
   - Create complex layout (3-4 panes)
   - Close app
   - Reopen app
   - Verify layout structure restored
   - Verify new terminal sessions are created

#### Regression Tests

- All existing keyboard shortcuts work (Ctrl+Shift+V, Ctrl+Shift+H, Ctrl+W, etc.)
- Tab management works (create, close tabs)
- Theme switching works
- Menu button works
- Window controls work (minimize, maximize, close)
- Frameless window mode works

---

## Implementation Order

### Recommended Sequence

1. **Phase 1, Task 1.1** - Update imports (2 min)
   - Low risk, quick win
   - Makes code future-proof

2. **Phase 1, Task 1.2** - Implement `widget_closing()` (30 min)
   - HIGH priority - fixes resource leak
   - Check TerminalWidget and MultiSessionTerminalServer APIs first

3. **Test** - Verify Phase 1 works (15 min)
   - Run app, split/close panes
   - Check server logs for session cleanup

4. **Phase 2, Task 2.1** - Focus indicators (10 min)
   - Nice UX improvement
   - Low risk, purely additive

5. **Test** - Verify focus indicators (5 min)

6. **Phase 2, Task 2.2** - Widget lookup (5 min)
   - Optional, demonstrates new API

7. **Phase 2, Task 2.3** - Session save/restore (20 min)
   - Optional, advanced feature
   - Can be done later

8. **Full regression test** - (15 min)
   - Test all features
   - Test with multiple tabs

### Total Estimated Time

- **Minimum (Phase 1 only)**: 45 minutes
- **Recommended (Phase 1 + 2.1 + 2.2)**: 60 minutes
- **Full (All phases)**: 90 minutes

---

## Risk Assessment

### Low Risk Items
- Import updates (Phase 1.1) ✅
- Focus indicators (Phase 2.1) ✅
- Widget lookup usage (Phase 2.2) ✅

### Medium Risk Items
- `widget_closing()` implementation (Phase 1.2) ⚠️
  - **Mitigation**: Wrap in try/except, log errors
  - **Validation**: Check TerminalWidget API first

- Session save/restore (Phase 2.3) ⚠️
  - **Mitigation**: Graceful fallback if load fails
  - **Validation**: Test file I/O errors

### Rollback Plan

If issues occur:
1. **Phase 1.1** - Revert import changes (git revert)
2. **Phase 1.2** - Comment out `widget_closing()` body
3. **Phase 2.x** - Remove signal connections, delete new methods

All changes are additive and isolated - easy to remove.

---

## Dependencies

### Required Checks

Before implementing Phase 1.2 (`widget_closing()`):

1. **Check TerminalWidget API**:
   ```python
   # Does TerminalWidget expose session_id?
   terminal = TerminalWidget(server_url="...")
   print(terminal.session_id)  # Should print session ID
   ```

2. **Check MultiSessionTerminalServer API**:
   ```python
   # Does server have terminate_session()?
   server = MultiSessionTerminalServer(port=0)
   server.terminate_session(session_id)  # Should terminate cleanly
   ```

3. **If missing**:
   - Add `session_id` property to `TerminalWidget`
   - Add `terminate_session()` method to `MultiSessionTerminalServer`
   - Update this plan with those tasks

---

## Success Criteria

### Phase 1 Success
- ✅ App runs without import errors
- ✅ All existing features work (split, close, tabs, etc.)
- ✅ Terminal sessions are cleaned up on pane close
- ✅ No flashing during splits (Fixed Container Architecture benefit)

### Phase 2 Success
- ✅ Visual focus indicator shows active terminal
- ✅ Widget lookup API used successfully
- ✅ Session save/restore works (if implemented)

---

## Next Steps

1. **Review this plan** - Confirm approach
2. **Check dependencies** - Verify TerminalWidget and server APIs
3. **Implement Phase 1** - Minimal migration (imports + lifecycle)
4. **Test Phase 1** - Verify no regressions
5. **Implement Phase 2** - Optional enhancements
6. **Document changes** - Update ViloxTerm README

---

## Questions for Review

1. Do we want visual focus indicators? (Phase 2.1)
2. Do we want session save/restore? (Phase 2.3)
3. Are there other v0.2.0 features we should leverage?
4. Should we update ViloxTerm's README to document MultisplitWidget v0.2.0 usage?

---

**Ready to proceed?** Start with Phase 1, Task 1.1 (import updates).
