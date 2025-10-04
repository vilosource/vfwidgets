# MultisplitWidget API Improvements - Implementation Plan

**Created**: 2025-10-04
**Status**: Approved - Ready for Implementation
**Current Version**: 0.1.0
**Target Version**: 0.2.0

## Version Strategy

**We are in early development (0.x)** - We can make breaking changes without deprecation:
- ✅ **0.x versions**: Can break API between minor versions (0.1 → 0.2)
- ✅ **No deprecation needed**: Just remove/change and document in migration guide
- ✅ **Faster iteration**: Don't maintain old APIs we'll never use
- ❌ **1.0+ versions**: MUST follow semantic versioning with deprecation period

**This plan uses the EARLY-STAGE approach**: Clean breaks, clear migration docs, no deprecated code.

## Executive Summary

This plan addresses critical developer experience issues discovered during debugging session:
1. **Missing widget lifecycle notifications** → causes crashes
2. **Confusing signal architecture** → unclear which signal to use
3. **No widget lookup API** → forces manual tracking
4. **Exposed internal implementation** → couples consumers to internals
5. **Inconsistent code cleanup** → confusing comments and unused code

**Approach**: Make clean breaks now (0.x), establish stable API for 1.0 later.

## Table of Contents

1. [Phase 0: Code Cleanup & API Boundary Enforcement](#phase-0-code-cleanup--api-boundary-enforcement)
2. [Phase 1: Widget Lifecycle Hook](#phase-1-widget-lifecycle-hook)
3. [Phase 2: Widget Lookup API](#phase-2-widget-lookup-api)
4. [Phase 3: Focus Signal Cleanup](#phase-3-focus-signal-cleanup)
5. [Phase 4: Package Exports](#phase-4-package-exports)
6. [Phase 5: Documentation](#phase-5-documentation)
7. [Phase 6: Testing](#phase-6-testing)
8. [Implementation Checklist](#implementation-checklist)

---

## PHASE 0: Code Cleanup & API Boundary Enforcement

**Priority**: CRITICAL - Must be done BEFORE new features
**Rationale**: Prevents future technical debt and API confusion

### Task 0.1: Make Internal Attributes Private

**File**: `src/vfwidgets_multisplit/multisplit.py`
**Lines**: ~84-89 (`__init__` method)

**Current Code (BAD)**:
```python
# Public attributes expose internal implementation
self.model = PaneModel()
self.controller = PaneController(self.model)
self.container = PaneContainer(self.model, provider, self)
self.focus_manager = FocusManager(self.model)
self.session_manager = SessionManager(self.model)
```

**New Code (GOOD)**:
```python
# Private attributes enforce API boundary
self._model = PaneModel()
self._controller = PaneController(self._model)
self._container = PaneContainer(self._model, provider, self)
self._focus_manager = FocusManager(self._model)
self._session_manager = SessionManager(self._model)
```

**Why**:
- Forces consumers to use public API methods
- Prevents coupling to internal implementation details
- Makes it clear what's stable vs. what might change

---

### Task 0.2: Update All Internal References

**File**: `src/vfwidgets_multisplit/multisplit.py`
**Scope**: All methods (~30 references)

**Pattern**: Replace all `self.model` → `self._model` (and same for other attributes)

**Example Changes**:
```python
# In _connect_signals()
self.container.widget_needed → self._container.widget_needed
self.container.pane_focused → self._container.pane_focused
self.model.signals → self._model.signals

# In split_pane()
self.controller.split_pane → self._controller.split_pane

# In navigate_focus()
self.focus_manager.navigate → self._focus_manager.navigate

# In save_layout()
self.session_manager.save_to_file → self._session_manager.save_to_file
```

**Verification**:
```bash
# After changes, grep should find NO public attribute access
grep -E "self\.(model|container|controller|focus_manager|session_manager)\." src/vfwidgets_multisplit/multisplit.py
```

---

### Task 0.3: Remove Internal Access from Examples

**File**: `examples/03_keyboard_driven_splitting.py`
**Line**: 413

**Remove**:
```python
# BAD: Accessing internal model directly
self.multisplit.model.signals.focus_changed.connect(self.on_model_focus_changed)
```

**Replace With** (after Phase 3 adds public signal):
```python
# GOOD: Using public API
self.multisplit.focus_changed.connect(self.on_model_focus_changed)
```

**NOTE**: This change depends on Phase 3 (focus_changed signal). Mark as `# TODO: Update after Phase 3`

---

### Task 0.4: Remove Internal Access from Prototype

**File**: `examples/03_geometry_prototype.py`

**Decision Required**:
- **Option A**: Move to `examples/prototype/` folder (internal/dev only)
- **Option B**: Rewrite to use public API only
- **Option C**: Delete (Phase 1 validation is complete, report exists)

**Recommendation**: **Option C - DELETE**

**Rationale**:
- This was a Phase 1 proof-of-concept test
- Results are documented in `docs/phase1-results-REPORT.md`
- Shipping internal test code as examples confuses users
- If needed for development, keep in `examples/prototype/` (gitignored)

**Action**:
```bash
git rm examples/03_geometry_prototype.py
```

---

### Task 0.5: Audit All Public Methods

**File**: `src/vfwidgets_multisplit/multisplit.py`

**Objective**: Ensure internal methods have underscore prefix

**Current Status** (verify):
```python
# These are already private ✓
def _connect_signals(self)
def _forward_pane_added(self)
def _on_splitter_moved(self)
```

**Verification Command**:
```bash
# List all public methods (no underscore)
grep "^    def [^_]" src/vfwidgets_multisplit/multisplit.py

# Expected output: Only documented public API methods
# - initialize_empty()
# - split_pane()
# - remove_pane()
# - focus_pane()
# - navigate_focus()
# - set_constraints()
# - undo(), redo(), can_undo(), can_redo()
# - save_layout(), load_layout()
# - get_layout_json(), set_layout_json()
# - get_pane_ids(), get_focused_pane()
```

**Action**: If any unlisted methods are found → add underscore prefix

---

### Task 0.6: ~~Add Deprecated Properties~~ SKIP - Clean Break Instead

**DECISION**: **DO NOT ADD DEPRECATED PROPERTIES** - We're in 0.x

**Rationale**:
- We're pre-1.0, so we can make breaking changes
- No need to maintain compatibility code we'll delete anyway
- Simpler codebase without deprecation warnings
- Clear migration guide is sufficient

**Instead**:
1. Make attributes private (`_model`, `_container`) immediately
2. Document breaking changes in migration guide
3. Update all examples to show correct usage
4. Any external code using internal APIs will get clear error (AttributeError)

**Migration Path**:
```python
# 0.1.x code that will break:
multisplit.model  # AttributeError in 0.2.0

# Migration guide shows:
# ❌ OLD (0.1): multisplit.model.get_all_pane_ids()
# ✅ NEW (0.2): multisplit.get_pane_ids()
```

**Why This Is Better for 0.x**:
- Cleaner codebase (no deprecated code)
- Forces users to update properly
- We're not promising stability yet
- Faster to implement and test

---

### Task 0.7: Clean Up "OLD ARCHITECTURE" Comments

**File**: `src/vfwidgets_multisplit/view/container.py`

**Find All Comments**:
```bash
grep -n "OLD ARCHITECTURE" src/vfwidgets_multisplit/view/container.py
```

**Action Plan**:

1. **For comments describing DELETED code** → DELETE the comment
   ```python
   # BEFORE
   # OLD ARCHITECTURE: _build_widget_tree() method removed

   # AFTER
   # (Comment deleted - code is gone, no need for comment)
   ```

2. **For comments describing code that STILL EXISTS** → Update to explain WHY
   ```python
   # BEFORE
   # OLD ARCHITECTURE: Removed - now using Fixed Container Architecture
   self._current_tree: Optional[PaneNode] = None  # Still needed for reconciliation

   # AFTER
   # Tree reconciliation cache: Stores previous tree to compute efficient diffs
   self._current_tree: Optional[PaneNode] = None
   ```

**Principle**: Comments should explain CURRENT code, not describe history

---

### Task 0.8: Remove Unused Imports and Dead Code

**Files**: All source files in `src/vfwidgets_multisplit/`

**Automated Detection**:
```bash
# Check for unused imports
ruff check --select F401 src/vfwidgets_multisplit/

# Or use pylint
pylint --disable=all --enable=unused-import src/vfwidgets_multisplit/
```

**Manual Audit Checklist**:
- [ ] Remove imports not used in file
- [ ] Remove methods with no callers
- [ ] Remove class attributes never accessed
- [ ] Remove commented-out code (if no TODO)
- [ ] Remove debug print statements

**Why**: Clean codebase = easier to understand = better DX

---

### Task 0.9: Enforce API Boundary with __all__

**File**: `src/vfwidgets_multisplit/view/container.py`
**Location**: End of file (after all class definitions)

**Add Explicit Exports**:
```python
# Public API exports
__all__ = [
    "WidgetProvider",  # Protocol - users implement this
    "PaneContainer",   # Used internally by MultisplitWidget (users don't instantiate)
]

# NOTE: PaneContainer is technically public but users should NOT
# instantiate it directly. MultisplitWidget creates and manages it.
```

**Repeat for other modules** that export public APIs

**Why**:
- Documents which classes are part of public API
- `from module import *` only imports listed items
- IDEs can use this for better autocomplete

---

### Task 0.10: Add Type Hints for Private Attributes

**File**: `src/vfwidgets_multisplit/multisplit.py`
**Location**: Top of `MultisplitWidget` class

**Add Class-Level Type Hints**:
```python
class MultisplitWidget(QWidget):
    """Main MultiSplit widget with complete public API.

    This widget provides a recursive split-pane interface with:
    - Dynamic splitting in any direction
    - Focus management and keyboard navigation
    - Drag-to-resize dividers
    - Session persistence
    - Undo/redo support
    - Widget provider pattern for flexibility
    """

    # ============================================================
    # PRIVATE IMPLEMENTATION (DO NOT ACCESS DIRECTLY)
    # ============================================================
    # These are internal components. The public API provides
    # methods to interact with these safely. Accessing these
    # directly will break in future versions.
    # ============================================================
    _model: PaneModel
    _controller: PaneController
    _container: PaneContainer
    _focus_manager: FocusManager
    _session_manager: SessionManager

    # ============================================================
    # PUBLIC SIGNALS
    # ============================================================
    widget_needed: Signal  # (widget_id: str, pane_id: str)
    pane_added: Signal     # (pane_id: str)
    pane_removed: Signal   # (pane_id: str)
    focus_changed: Signal  # (old_pane_id: str, new_pane_id: str) - NEW in v0.2
    pane_focused: Signal   # (pane_id: str) - DEPRECATED, use focus_changed
    layout_changed: Signal # ()
    validation_failed: Signal  # (errors: list)
```

**Why**:
- Type checkers warn if users access `_private` attributes
- Clear documentation of what's public vs private
- Better IDE autocomplete

---

## PHASE 1: Widget Lifecycle Hook

**Priority**: CRITICAL - Fixes Crashes
**Dependencies**: Phase 0 complete

### Task 1.1: Add widget_closing() to WidgetProvider Protocol

**File**: `src/vfwidgets_multisplit/view/container.py`
**Lines**: ~113-119 (WidgetProvider Protocol)

**Current**:
```python
class WidgetProvider(Protocol):
    """Protocol for widget provider."""

    def provide_widget(self, widget_id: WidgetId, pane_id: PaneId) -> QWidget:
        """Provide widget for pane."""
        ...
```

**Add Method**:
```python
class WidgetProvider(Protocol):
    """Protocol for widget provider.

    Implement this protocol to provide custom widgets to MultisplitWidget.
    """

    def provide_widget(self, widget_id: WidgetId, pane_id: PaneId) -> QWidget:
        """Provide widget for a pane.

        Called when MultisplitWidget needs a widget for a pane.

        Args:
            widget_id: Identifier for the widget type/content to create
            pane_id: Unique ID for the pane this widget will be in

        Returns:
            QWidget instance to display in the pane

        Example:
            def provide_widget(self, widget_id, pane_id):
                if widget_id == "editor":
                    return QTextEdit()
                elif widget_id == "terminal":
                    return TerminalWidget()
                else:
                    return QLabel(f"Unknown: {widget_id}")
        """
        ...

    def widget_closing(self, widget_id: WidgetId, pane_id: PaneId, widget: QWidget) -> None:
        """Called BEFORE widget is removed from MultisplitWidget.

        Override this method to clean up resources when a pane is closed:
        - Save widget state (file content, scroll position, etc.)
        - Disconnect signals to prevent memory leaks
        - Close file handles, network connections, etc.
        - Remove widget from your tracking dictionaries

        The default implementation does nothing (safe to omit).

        Args:
            widget_id: The widget ID used to create this widget
            pane_id: The pane ID this widget was in
            widget: The actual widget being removed (still valid Qt object)

        Example:
            def widget_closing(self, widget_id, pane_id, widget):
                # Save state before widget is destroyed
                if isinstance(widget, TextEditor):
                    self.save_editor_state(widget_id, widget.get_content())

                # Clean up tracking
                if pane_id in self.widgets:
                    del self.widgets[pane_id]

                # Disconnect signals
                try:
                    widget.content_changed.disconnect()
                except:
                    pass

        Note:
            This is called BEFORE the widget is deleted. The widget is
            still a valid Qt object. Don't call deleteLater() on it -
            MultisplitWidget handles widget destruction.
        """
        pass  # Default: no-op (backward compatible)
```

**Why**: Provides notification BEFORE widget deletion for cleanup

---

### Task 1.2: Call widget_closing() in PaneContainer.remove_pane()

**File**: `src/vfwidgets_multisplit/view/container.py`
**Lines**: ~546-570 (remove_pane method)

**Current Code**:
```python
def remove_pane(self, pane_id: PaneId):
    """Remove pane widget from pool."""
    if self._widget_pool.has_widget(pane_id):
        widget = self._widget_pool.get_widget(pane_id)
        # ... cleanup code ...
        self._widget_pool.remove_widget(pane_id)
```

**Updated Code**:
```python
def remove_pane(self, pane_id: PaneId):
    """Remove pane widget from pool.

    NEW: Calls provider.widget_closing() before removal.
    """
    # Get the pane node to find widget_id
    pane_node = self._model.get_pane(pane_id)

    if self._widget_pool.has_widget(pane_id):
        widget = self._widget_pool.get_widget(pane_id)

        # NEW: Notify provider BEFORE removal (lifecycle hook)
        if pane_node and self.provider:
            try:
                self.provider.widget_closing(
                    widget_id=pane_node.widget_id,
                    pane_id=pane_id,
                    widget=widget
                )
                logger.debug(f"Called provider.widget_closing() for pane {pane_id}")
            except AttributeError:
                # Provider doesn't implement widget_closing() - backward compatible
                logger.debug(f"Provider does not implement widget_closing() - skipping")
                pass
            except Exception as e:
                # Log but don't crash if provider's cleanup fails
                logger.warning(f"Error in provider.widget_closing() for pane {pane_id}: {e}")

        # Clean up child monitoring timer if it exists
        if widget:
            timer = widget.property("child_monitor_timer")
            if timer:
                logger.debug(f"Stopping child monitor timer for pane {pane_id}")
                timer.stop()
                timer.deleteLater()
                widget.setProperty("child_monitor_timer", None)

        self._widget_pool.remove_widget(pane_id)
        logger.info(f"Removed pane {pane_id} from pool")

    logger.debug(f"Cleaned up all resources for pane {pane_id}")
```

**Why**:
- Calls lifecycle hook before widget destruction
- Backward compatible (AttributeError handled)
- Safe (Exception in hook doesn't crash widget)

---

### Task 1.3: Update Keyboard Example to Use Lifecycle Hook

**File**: `examples/03_keyboard_driven_splitting.py`
**Lines**: ~334-345 (KeyboardProvider class)

**Add Method**:
```python
class KeyboardProvider(WidgetProvider):
    """Provider for keyboard-controlled panes."""

    def __init__(self):
        self.panes: dict[str, KeyboardPaneWidget] = {}
        self.document_counter = 0

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Create a keyboard-controlled pane."""
        # ... existing code ...
        self.panes[pane_id] = pane_widget
        return pane_widget

    # NEW: Proper lifecycle management
    def widget_closing(self, widget_id: str, pane_id: str, widget: QWidget) -> None:
        """Clean up when widget is being removed."""
        if pane_id in self.panes:
            print(f"[PROVIDER] widget_closing: Removing {pane_id[:8]} from tracking")
            del self.panes[pane_id]
        else:
            print(f"[PROVIDER] widget_closing: {pane_id[:8]} not in tracking (already removed?)")
```

**Also Remove** from `on_model_focus_changed()` (lines ~717-726):
```python
# REMOVE THIS - no longer needed with lifecycle hook:
# Clean up deleted panes from provider tracking
current_panes = set(self.multisplit.get_pane_ids())
deleted_panes = set(self.provider.panes.keys()) - current_panes
for deleted_id in deleted_panes:
    print(f"[CLEANUP] Removing deleted pane {deleted_id[:8]} from provider")
    del self.provider.panes[deleted_id]
```

**Why**: Demonstrates best practice, automatic cleanup

---

### Task 1.4: Update Other Examples

**Files**:
- `examples/01_basic_text_editor.py` - TextEditorProvider
- `examples/02_tabbed_split_panes.py` - TabbedProvider
- `examples/04_advanced_dynamic_workspace.py` - WorkspaceProvider (if exists)

**Pattern**: Add `widget_closing()` method to each provider

**Example for TextEditorProvider**:
```python
def widget_closing(self, widget_id: str, pane_id: str, widget: QWidget) -> None:
    """Clean up editor when pane is closed."""
    # Save unsaved changes?
    if hasattr(widget, 'is_modified') and widget.is_modified:
        # Could prompt to save here
        pass

    # Remove from tracking
    if pane_id in self.editors:
        del self.editors[pane_id]
```

---

## PHASE 2: Widget Lookup API

**Priority**: HIGH - Major DX Improvement
**Dependencies**: Phase 0 complete

### Task 2.1: Add get_widget() Method

**File**: `src/vfwidgets_multisplit/multisplit.py`
**Location**: After `get_focused_pane()` method (~312)

**Add Method**:
```python
def get_widget(self, pane_id: str) -> Optional[QWidget]:
    """Get the widget instance for a pane.

    This is useful when you need direct access to the widget in a pane,
    for example to call widget-specific methods or get/set state.

    Args:
        pane_id: ID of the pane

    Returns:
        The widget in the pane, or None if pane doesn't exist

    Example:
        # Get widget and call custom method
        widget = multisplit.get_widget(pane_id)
        if widget and isinstance(widget, MyCustomWidget):
            widget.save_current_state()

        # Check widget type
        widget = multisplit.get_widget(focused_pane)
        if isinstance(widget, TextEditor):
            print(f"Current text: {widget.toPlainText()}")

    Note:
        This returns the raw widget without any wrapper containers.
        The widget is managed by MultisplitWidget - don't delete it manually.

    See Also:
        - get_all_widgets(): Get dict of all pane widgets
        - find_pane_by_widget(): Find pane ID from widget reference
    """
    return self._container._widget_pool.get_widget(pane_id)
```

**Why**: Official API for widget access without manual tracking

---

### Task 2.2: Add get_all_widgets() Helper

**File**: `src/vfwidgets_multisplit/multisplit.py`
**Location**: After `get_widget()`

**Add Method**:
```python
def get_all_widgets(self) -> Dict[str, QWidget]:
    """Get all pane widgets as a dictionary.

    Returns:
        Dictionary mapping pane_id -> widget for all current panes

    Example:
        # Save state of all editors
        for pane_id, widget in multisplit.get_all_widgets().items():
            if isinstance(widget, TextEditor):
                widget.save_to_disk()

        # Count widget types
        editors = sum(1 for w in multisplit.get_all_widgets().values()
                     if isinstance(w, TextEditor))
        print(f"Open editors: {editors}")

    Note:
        The returned dict is a snapshot. If panes are added/removed,
        call this method again to get updated dict.
    """
    result = {}
    for pane_id in self.get_pane_ids():
        widget = self.get_widget(pane_id)
        if widget:
            result[pane_id] = widget
    return result
```

**Why**: Convenience for iterating all widgets

---

### Task 2.3: Add find_pane_by_widget() Helper

**File**: `src/vfwidgets_multisplit/multisplit.py`
**Location**: After `get_all_widgets()`

**Add Method**:
```python
def find_pane_by_widget(self, widget: QWidget) -> Optional[str]:
    """Find which pane contains a widget.

    This checks if the widget or any of its ancestors is a pane widget.
    Useful when handling widget events and you need the pane ID.

    Args:
        widget: Widget to search for (can be child widget within pane)

    Returns:
        Pane ID containing the widget, or None if not found

    Example:
        # In a widget event handler
        def on_widget_clicked(self, widget):
            pane_id = self.multisplit.find_pane_by_widget(widget)
            if pane_id:
                print(f"Widget is in pane: {pane_id}")
                self.multisplit.focus_pane(pane_id)

        # Find pane for child widget
        button = QWidget.find_child(QPushButton)
        pane_id = multisplit.find_pane_by_widget(button)

    Note:
        This searches up the widget hierarchy, so it works even if
        you pass a deeply nested child widget.
    """
    return self._container._find_widget_pane(widget)
```

**Why**: Helps with event handling when you have widget but need pane ID

---

## PHASE 3: Focus Signal Cleanup

**Priority**: MEDIUM - API Clarity
**Dependencies**: Phase 0 complete

### Task 3.1: Add focus_changed Signal (Clean Break - No Deprecation)

**File**: `src/vfwidgets_multisplit/multisplit.py`
**Lines**: ~33-40 (Signal definitions)

**DECISION**: **REMOVE `pane_focused` entirely** - We're in 0.x

**Current (0.1)**:
```python
class MultisplitWidget(QWidget):
    # Signals
    widget_needed = Signal(str, str)  # widget_id, pane_id
    pane_added = Signal(str)  # pane_id
    pane_removed = Signal(str)  # pane_id
    pane_focused = Signal(str)  # pane_id ← REMOVE THIS
    layout_changed = Signal()
    validation_failed = Signal(list)  # error messages
```

**New (0.2) - Clean Break**:
```python
class MultisplitWidget(QWidget):
    """Main MultiSplit widget with complete public API.

    Signals:
        widget_needed(widget_id: str, pane_id: str):
            Emitted when a widget is needed for a pane.

        pane_added(pane_id: str):
            Emitted when a new pane is added.

        pane_removed(pane_id: str):
            Emitted when a pane is removed.

        focus_changed(old_pane_id: str, new_pane_id: str):
            Emitted when focus moves between panes.

            Args:
                old_pane_id: Previously focused pane (empty string if none)
                new_pane_id: Newly focused pane (empty string if cleared)

            Example:
                multisplit.focus_changed.connect(
                    lambda old, new: print(f"Focus: {old} -> {new}")
                )

        layout_changed():
            Emitted when the pane layout changes (split, remove, etc).

        validation_failed(errors: list):
            Emitted when an operation fails validation.
    """

    # Signals
    widget_needed = Signal(str, str)  # widget_id, pane_id
    pane_added = Signal(str)  # pane_id
    pane_removed = Signal(str)  # pane_id
    focus_changed = Signal(str, str)  # old_pane_id, new_pane_id - NEW in v0.2
    # pane_focused REMOVED in 0.2 - use focus_changed
    layout_changed = Signal()
    validation_failed = Signal(list)  # error messages
```

**Why Clean Break is Better**:
- No confusing dual signals (old + new)
- Simpler codebase to maintain
- Clear migration path in docs
- We're pre-1.0, this is expected

---

### Task 3.2: Forward Model Signal to Public Signal (Clean Break)

**File**: `src/vfwidgets_multisplit/multisplit.py`
**Lines**: ~117-119 (`_connect_signals` method)

**Current (0.1)**:
```python
self._model.signals.focus_changed.connect(
    lambda old, new: self.pane_focused.emit(str(new)) if new else None
)
```

**New (0.2) - Clean Break**:
```python
# Forward model focus changes to PUBLIC signal
self._model.signals.focus_changed.connect(
    lambda old, new: self.focus_changed.emit(
        str(old) if old else "",  # Empty string if None
        str(new) if new else ""   # Empty string if None
    )
)

# NO backward compatibility - pane_focused signal removed entirely
```

**Why Clean Break**:
- Single, clear signal to use
- No legacy code to maintain
- Migration guide documents the change
- We're in 0.x, this is the time for clean breaks

---

### Task 3.3: Update Examples to Use New Signal

**File**: `examples/03_keyboard_driven_splitting.py`
**Lines**: ~413

**Current**:
```python
# Accessing internal model
self.multisplit.model.signals.focus_changed.connect(self.on_model_focus_changed)
```

**Updated**:
```python
# Using public API (after Phase 3)
self.multisplit.focus_changed.connect(self.on_model_focus_changed)
```

**Also Update Handler Signature** (same file, ~704):
```python
# Method signature already correct, just update docstring
def on_model_focus_changed(self, old_id: str, new_id: str):
    """Handle focus change from MultisplitWidget.focus_changed signal.

    This is the CORRECT way to track focus changes.
    DON'T use multisplit.model.signals - that's internal API.
    """
    print(f"[FOCUS] Focus changed: {old_id[:8] if old_id else 'None'} -> {new_id[:8] if new_id else 'None'}")
    # ... rest of method ...
```

---

## PHASE 4: Package Exports

**Priority**: MEDIUM - Convenience
**Dependencies**: None

### Task 4.1: Export Common Types from Main Package

**File**: `src/vfwidgets_multisplit/__init__.py`

**Current**:
```python
"""MultisplitWidget - A custom PySide6 widget."""

__version__ = "0.1.0"

from .core.types import SplitterStyle
from .multisplit import MultisplitWidget

__all__ = ["MultisplitWidget", "SplitterStyle"]
```

**Updated**:
```python
"""MultisplitWidget - A custom PySide6 widget.

Main Exports:
    MultisplitWidget: Main widget class for dynamic split panes
    SplitterStyle: Configuration for splitter appearance
    WidgetProvider: Protocol for providing widgets to panes
    WherePosition: Enum for split directions (RIGHT, LEFT, TOP, BOTTOM)
    Direction: Enum for focus navigation (UP, DOWN, LEFT, RIGHT)

Example - Basic usage:
    from vfwidgets_multisplit import (
        MultisplitWidget,
        WidgetProvider,
        WherePosition
    )

    class MyProvider(WidgetProvider):
        def provide_widget(self, widget_id, pane_id):
            return QTextEdit()

    multisplit = MultisplitWidget(provider=MyProvider())
    multisplit.split_pane(pane_id, "editor-2", WherePosition.RIGHT)

Example - Focus tracking:
    from vfwidgets_multisplit import MultisplitWidget

    multisplit = MultisplitWidget(provider=provider)
    multisplit.focus_changed.connect(lambda old, new: print(f"Focus: {old} -> {new}"))

Example - Navigation:
    from vfwidgets_multisplit import MultisplitWidget, Direction

    multisplit.navigate_focus(Direction.RIGHT)
"""

__version__ = "0.2.0"

from .core.types import Direction, SplitterStyle, WherePosition
from .multisplit import MultisplitWidget
from .view.container import WidgetProvider

__all__ = [
    "MultisplitWidget",
    "SplitterStyle",
    "WidgetProvider",
    "WherePosition",
    "Direction",
]
```

**Why**: Users don't need to know internal package structure

---

### Task 4.2: Update All Examples to Use New Imports

**Files**: All examples (`01_*.py`, `02_*.py`, `03_*.py`, `04_*.py`)

**Pattern - Change From**:
```python
from vfwidgets_multisplit import MultisplitWidget
from vfwidgets_multisplit.core.types import WherePosition
from vfwidgets_multisplit.view.container import WidgetProvider
```

**Change To**:
```python
from vfwidgets_multisplit import (
    MultisplitWidget,
    WidgetProvider,
    WherePosition,
)
```

**Benefits**:
- Cleaner imports
- Demonstrates best practice
- Single source of imports

---

## PHASE 5: Documentation

**Priority**: HIGH - Users need docs
**Dependencies**: Phases 0-4 complete

### Task 5.1: Create API Best Practices Guide

**File**: `docs/api-best-practices-GUIDE.md` (NEW)

**Contents**: See separate section below (too long for here)

**Key Sections**:
1. Widget Provider Lifecycle
2. Focus Tracking
3. Widget Access
4. API Boundaries - What NOT to Do
5. Future Compatibility

---

### Task 5.2: Create API Stability Guarantees Document

**File**: `docs/api-stability-GUIDE.md` (NEW)

**Contents**: See separate section below

**Key Sections**:
1. What's Stable (Semantic Versioning)
2. Deprecated APIs (Will be removed in 1.0)
3. Internal APIs (May change anytime)
4. Migration Path

---

### Task 5.3: Update Main README

**File**: `README.md`

**Add Section**: "API Stability" with link to docs

**Add Section**: "Upgrading from 0.1 to 0.2" with:
- New lifecycle hook
- New widget access methods
- New focus signal
- Deprecated APIs

---

### Task 5.4: Update Examples README

**File**: `examples/README.md`

**Add Note**:
```markdown
## Best Practices

All examples follow these best practices:
- ✅ Use only public API (no accessing `._private` attributes)
- ✅ Implement `widget_closing()` for cleanup
- ✅ Use `focus_changed` signal (not `pane_focused`)
- ✅ Use `get_widget()` method (not manual tracking)
- ✅ Import from main package (not internal modules)
```

---

### Task 5.5: Create Migration Guide

**File**: `docs/migration-0.2-GUIDE.md` (NEW)

**Contents**: See separate section below

**Key Sections**:
1. Breaking Changes (NONE)
2. New Features
3. Deprecated Features
4. Code Examples (Before/After)

---

## PHASE 6: Testing

**Priority**: CRITICAL - Ensure quality
**Dependencies**: Phases 0-5 complete

### Task 6.1: Add Test for widget_closing() Hook

**File**: `tests/test_widget_lifecycle.py` (NEW)

**Test Cases**:
```python
def test_widget_closing_called_on_remove():
    """Verify widget_closing() is called when pane removed."""

def test_widget_closing_receives_correct_parameters():
    """Verify widget_closing() gets widget_id, pane_id, widget."""

def test_widget_closing_backward_compatible():
    """Verify works when provider doesn't implement hook."""

def test_widget_closing_exception_doesnt_crash():
    """Verify exception in widget_closing() is handled gracefully."""
```

---

### Task 6.2: Add Test for Widget Lookup API

**File**: `tests/test_widget_access.py` (NEW)

**Test Cases**:
```python
def test_get_widget_returns_correct_widget():
    """Verify get_widget() returns the widget in pane."""

def test_get_widget_returns_none_for_invalid_id():
    """Verify get_widget() returns None for non-existent pane."""

def test_get_all_widgets_returns_all_panes():
    """Verify get_all_widgets() returns dict of all panes."""

def test_find_pane_by_widget_finds_by_widget():
    """Verify find_pane_by_widget() finds pane."""

def test_find_pane_by_widget_finds_by_ancestor():
    """Verify find_pane_by_widget() finds by child widget."""
```

---

### Task 6.3: Add Test for Focus Signal

**File**: `tests/test_focus_signals.py` (NEW)

**Test Cases**:
```python
def test_focus_changed_emits_with_both_ids():
    """Verify focus_changed emits old and new pane IDs."""

def test_pane_focused_still_works():
    """Verify pane_focused signal still works (backward compat)."""

def test_both_signals_emit_on_focus_change():
    """Verify both signals emit on same focus change."""
```

---

### Task 6.4: Update Existing Tests

**Files**: All test files

**Changes**:
- Update imports to use new package exports
- Update to use `multisplit._model` instead of `multisplit.model`
- Ensure all tests still pass

---

### Task 6.5: Add Test for Private Attribute Access

**File**: `tests/test_api_boundaries.py` (NEW)

**Test Cases**:
```python
def test_private_attributes_have_underscore():
    """Verify internal attributes are marked private."""
    multisplit = MultisplitWidget()
    assert hasattr(multisplit, '_model')
    assert hasattr(multisplit, '_container')
    assert hasattr(multisplit, '_controller')

def test_deprecated_model_access_warns():
    """Verify accessing model property shows deprecation warning."""
    import warnings
    multisplit = MultisplitWidget()

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        _ = multisplit.model
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)

def test_public_api_methods_exist():
    """Verify all documented public methods exist."""
    multisplit = MultisplitWidget()

    # Core operations
    assert hasattr(multisplit, 'initialize_empty')
    assert hasattr(multisplit, 'split_pane')
    assert hasattr(multisplit, 'remove_pane')

    # Focus
    assert hasattr(multisplit, 'focus_pane')
    assert hasattr(multisplit, 'navigate_focus')
    assert hasattr(multisplit, 'get_focused_pane')

    # Widget access (NEW)
    assert hasattr(multisplit, 'get_widget')
    assert hasattr(multisplit, 'get_all_widgets')
    assert hasattr(multisplit, 'find_pane_by_widget')

    # Layout
    assert hasattr(multisplit, 'get_pane_ids')
    assert hasattr(multisplit, 'save_layout')
    assert hasattr(multisplit, 'load_layout')
```

---

### Task 6.6: Add Linting Rules

**File**: `pyproject.toml`

**Add Section**:
```toml
[tool.ruff]
select = [
    "F",    # pyflakes - catches unused imports
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "N",    # pep8-naming - enforce naming conventions
]

[tool.ruff.lint.pep8-naming]
classmethod-decorators = ["classmethod"]
staticmethod-decorators = ["staticmethod"]

[tool.ruff.lint]
ignore = [
    "E501",  # Line too long (let formatter handle it)
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

**Add to CI**:
```bash
# Run before each commit
ruff check src/ tests/ examples/
```

---

## Implementation Checklist

### Phase 0: Code Cleanup (MUST DO FIRST)

- [ ] **0.1** Make model, container, etc. private (`_model`, `_container`)
- [ ] **0.2** Update all internal references to use private names
- [ ] **0.3** Remove `multisplit.model.signals` from keyboard example (after Phase 3)
- [ ] **0.4** Delete or move `03_geometry_prototype.py`
- [ ] **0.5** Audit public methods - ensure _ prefix on internals
- [ ] **0.6** ~~Add deprecated properties~~ SKIP - Clean break instead (0.x version)
- [ ] **0.7** Clean up "OLD ARCHITECTURE" comments
- [ ] **0.8** Remove unused imports and dead code
- [ ] **0.9** Add `__all__` to enforce API boundaries
- [ ] **0.10** Add type hints for private attributes

### Phase 1: Widget Lifecycle

- [ ] **1.1** Add `widget_closing()` to WidgetProvider protocol
- [ ] **1.2** Call `widget_closing()` in PaneContainer.remove_pane()
- [ ] **1.3** Update keyboard example to use lifecycle hook
- [ ] **1.4** Update other examples (01, 02, 04) with lifecycle hooks

### Phase 2: Widget Access API

- [ ] **2.1** Add `get_widget(pane_id)` method
- [ ] **2.2** Add `get_all_widgets()` helper method
- [ ] **2.3** Add `find_pane_by_widget(widget)` helper method

### Phase 3: Focus Signals

- [ ] **3.1** Add `focus_changed` signal to MultisplitWidget
- [ ] **3.2** Forward model.focus_changed to public signal
- [ ] **3.3** Update keyboard example to use new signal

### Phase 4: Package Exports

- [ ] **4.1** Export WidgetProvider, WherePosition, Direction from main package
- [ ] **4.2** Update all examples to use new imports

### Phase 5: Documentation

- [ ] **5.1** Create `docs/api-best-practices-GUIDE.md`
- [ ] **5.2** Create `docs/api-stability-GUIDE.md`
- [ ] **5.3** Update main README.md
- [ ] **5.4** Update `examples/README.md`
- [ ] **5.5** Create `docs/migration-0.2-GUIDE.md`

### Phase 6: Testing

- [ ] **6.1** Add tests for widget_closing() hook
- [ ] **6.2** Add tests for widget access API
- [ ] **6.3** Add tests for focus signals
- [ ] **6.4** Update existing tests for new imports
- [ ] **6.5** Add tests for API boundary enforcement
- [ ] **6.6** Configure linting rules (ruff)

---

## Verification Steps

After implementation, verify:

1. **All tests pass**: `pytest tests/`
2. **No lint errors**: `ruff check src/ tests/ examples/`
3. **Examples run**: Test each example file
4. **Deprecation warnings work**: Run examples, check for warnings
5. **Public API only**: `grep -r "multisplit\._" examples/` → should find nothing
6. **Type hints work**: `mypy src/vfwidgets_multisplit/` (if configured)

---

## Summary

**Total Tasks**: 34 tasks across 6 phases

**Execution Order**:
1. **Phase 0** (10 tasks) - CLEANUP FIRST - prevents future confusion
2. **Phase 1** (4 tasks) - Fix lifecycle bugs
3. **Phase 2** (3 tasks) - Add widget access API
4. **Phase 3** (3 tasks) - Clean up focus signals
5. **Phase 4** (2 tasks) - Better imports
6. **Phase 5** (5 tasks) - Document everything
7. **Phase 6** (6 tasks) - Test + enforce

**Breaking Changes in 0.2.0**: YES - Clean breaks for better API (we're in 0.x)
- `multisplit.model` → Use public methods instead (get_pane_ids(), etc.)
- `multisplit.container` → Use public methods instead (get_widget(), etc.)
- `multisplit.pane_focused` signal → Use `multisplit.focus_changed` instead

**Backward Compatibility**: NO - This is 0.x, we can break things
- Migration guide documents all changes
- Examples show correct usage
- Clear error messages (AttributeError) guide users

**Key Principles for 0.x Development**:
- ✅ Private attributes MUST have underscore prefix
- ✅ Examples MUST use only public API
- ✅ Public API MUST be documented
- ✅ Internal APIs MUST be clearly marked
- ✅ **Clean breaks OK** - No deprecation needed in 0.x
- ✅ **Migration guide** - Document breaking changes clearly
- ✅ Code cleanup BEFORE adding features
- ✅ **Stability promise at 1.0** - Then we'll do proper deprecation

---

## Appendix A: Best Practices Guide Template

(See separate `docs/api-best-practices-GUIDE.md` file)

## Appendix B: API Stability Guide Template

(See separate `docs/api-stability-GUIDE.md` file)

## Appendix C: Migration Guide Template

(See separate `docs/migration-0.2-GUIDE.md` file)
