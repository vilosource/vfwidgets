# Public API

## Overview

The MultiSplit public API provides complete control over split-pane layouts through widget methods, properties, and events. This API follows Qt conventions while maintaining clean separation between layout management and widget content through the widget provider pattern.

## What This Covers

- **Widget Methods**: Split operations, navigation, layout manipulation
- **Properties**: State access, configuration, runtime information
- **Event System**: User interaction handling and lifecycle events
- **Configuration**: Size constraints, global settings, behavior tuning
- **Error Handling**: Exception types, error recovery, validation

## What This Doesn't Cover

- Widget provider implementation (see [Protocols](protocols.md))
- Internal signal mechanics (see [Signals](signals.md))
- Command system internals (handled by Controller layer)
- Model data structures (handled by Model layer)

---

## Core Widget Class

### MultiSplitWidget

```python
from vfwidgets_multisplit import MultiSplitWidget, WherePosition, WidgetProvider

class MultiSplitWidget(QWidget):
    """Main split-pane layout widget"""

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize MultiSplit widget.

        Args:
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self._model = PaneModel()
        self._controller = PaneController(self._model)
        self._view = PaneView(self._model, self)
        self._widget_provider: Optional[WidgetProvider] = None
        self._validation_mode = ValidationMode.STRICT
```

---

## Widget Management Methods

### Primary Widget Operations

```python
def set_root_widget(self, widget: QWidget, widget_id: str) -> bool:
    """
    Set the root widget for the layout.

    Args:
        widget: Widget instance to place as root
        widget_id: Stable identifier for the widget

    Returns:
        True if successful, False if validation fails

    Raises:
        ValueError: If widget_id is empty or invalid
        WidgetProviderError: If no provider is set

    Example:
        editor = CodeEditor()
        success = splitter.set_root_widget(editor, "editor:main.py")
    """

def split_with_widget(self, pane_id: str, where: WherePosition,
                     widget: QWidget, widget_id: str,
                     ratio: float = 0.5) -> Optional[str]:
    """
    Split existing pane and add new widget.

    Args:
        pane_id: ID of pane to split
        where: Position for new widget (LEFT, RIGHT, TOP, BOTTOM)
        widget: Widget instance to add
        widget_id: Stable identifier for the widget
        ratio: Size ratio for new pane (0.1-0.9)

    Returns:
        New pane ID if successful, None if failed

    Raises:
        PaneNotFoundError: If pane_id doesn't exist
        InvalidRatioError: If ratio is outside valid range
        MaxPanesExceededError: If maximum pane limit reached

    Example:
        terminal = Terminal()
        new_pane = splitter.split_with_widget(
            "pane-1", WherePosition.BOTTOM, terminal, "terminal:1", 0.3
        )
    """

def replace_widget(self, pane_id: str, widget: QWidget,
                  widget_id: str) -> bool:
    """
    Replace widget in existing pane.

    Args:
        pane_id: ID of pane to update
        widget: New widget instance
        widget_id: New widget identifier

    Returns:
        True if successful, False if failed

    Raises:
        PaneNotFoundError: If pane_id doesn't exist
        LockedPaneError: If pane is locked

    Example:
        new_editor = CodeEditor()
        success = splitter.replace_widget(
            "pane-2", new_editor, "editor:new_file.py"
        )
    """
```

### Widget Provider Management

```python
def set_widget_provider(self, provider: WidgetProvider) -> None:
    """
    Set the widget provider for layout restoration.

    Args:
        provider: Object implementing WidgetProvider protocol

    Raises:
        TypeError: If provider doesn't implement required methods

    Example:
        class MyProvider:
            def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
                return self.create_widget(widget_id)

            def widget_closing(self, widget_id: str, widget: QWidget) -> None:
                self.save_widget_state(widget_id, widget)

        splitter.set_widget_provider(MyProvider())
    """

def get_widget_provider(self) -> Optional[WidgetProvider]:
    """
    Get current widget provider.

    Returns:
        Current provider or None if not set
    """

def get_widget(self, pane_id: str) -> Optional[QWidget]:
    """
    Get widget instance for pane.

    Args:
        pane_id: ID of pane

    Returns:
        Widget instance or None if pane not found

    Example:
        editor = splitter.get_widget("pane-1")
        if isinstance(editor, CodeEditor):
            editor.save_file()
    """
```

---

## Navigation Methods

### Focus Management

```python
def focus_pane(self, pane_id: str) -> bool:
    """
    Set focus to specific pane.

    Args:
        pane_id: ID of pane to focus

    Returns:
        True if focus changed, False if already focused or invalid

    Raises:
        PaneNotFoundError: If pane_id doesn't exist

    Example:
        splitter.focus_pane("pane-3")
    """

def focus_next_pane(self) -> bool:
    """
    Focus next pane in traversal order.

    Returns:
        True if focus changed, False if no change possible

    Example:
        # Cycle through panes with Tab key
        QShortcut(QKeySequence.NextChild, self, splitter.focus_next_pane)
    """

def focus_previous_pane(self) -> bool:
    """
    Focus previous pane in traversal order.

    Returns:
        True if focus changed, False if no change possible

    Example:
        # Reverse cycle with Shift+Tab
        QShortcut(QKeySequence.PreviousChild, self, splitter.focus_previous_pane)
    """

def focus_direction(self, direction: Direction) -> bool:
    """
    Focus pane in specific direction from current.

    Args:
        direction: UP, DOWN, LEFT, RIGHT

    Returns:
        True if focus changed, False if no pane in direction

    Example:
        # Vim-style navigation
        splitter.focus_direction(Direction.LEFT)   # h
        splitter.focus_direction(Direction.RIGHT)  # l
    """
```

### Pane Discovery

```python
def find_panes_by_widget_type(self, widget_type: type) -> list[str]:
    """
    Find all panes containing widgets of specific type.

    Args:
        widget_type: Widget class to search for

    Returns:
        List of pane IDs containing matching widgets

    Example:
        editor_panes = splitter.find_panes_by_widget_type(CodeEditor)
        for pane_id in editor_panes:
            editor = splitter.get_widget(pane_id)
            editor.save_file()
    """

def find_pane_by_widget_id(self, widget_id: str) -> Optional[str]:
    """
    Find pane containing specific widget ID.

    Args:
        widget_id: Widget identifier to search for

    Returns:
        Pane ID if found, None otherwise

    Example:
        pane_id = splitter.find_pane_by_widget_id("editor:main.py")
        if pane_id:
            splitter.focus_pane(pane_id)
    """
```

---

## Layout Operations

### Pane Management

```python
def close_pane(self, pane_id: str) -> bool:
    """
    Close and remove pane from layout.

    Args:
        pane_id: ID of pane to close

    Returns:
        True if closed, False if failed or is last pane

    Raises:
        PaneNotFoundError: If pane_id doesn't exist
        LockedPaneError: If pane is locked
        LastPaneError: If attempting to close the only pane

    Example:
        if splitter.pane_count > 1:
            splitter.close_pane("pane-2")
    """

def close_current_pane(self) -> bool:
    """
    Close currently focused pane.

    Returns:
        True if closed, False if failed

    Example:
        # Close current pane with Ctrl+W
        QShortcut(QKeySequence("Ctrl+W"), self, splitter.close_current_pane)
    """

def swap_panes(self, pane_id_a: str, pane_id_b: str) -> bool:
    """
    Swap widgets between two panes.

    Args:
        pane_id_a: First pane ID
        pane_id_b: Second pane ID

    Returns:
        True if swapped, False if failed

    Raises:
        PaneNotFoundError: If either pane doesn't exist
        LockedPaneError: If either pane is locked

    Example:
        # Swap current pane with next
        current = splitter.current_pane_id
        next_pane = splitter.get_next_pane_id(current)
        splitter.swap_panes(current, next_pane)
    """
```

### Move Operations

```python
def move_pane(self, source_pane_id: str, target_pane_id: str,
              where: WherePosition) -> bool:
    """
    Move pane to new position relative to target.

    Args:
        source_pane_id: Pane to move
        target_pane_id: Reference pane for positioning
        where: Position relative to target

    Returns:
        True if moved, False if failed

    Raises:
        PaneNotFoundError: If either pane doesn't exist
        InvalidMoveError: If move would create invalid structure

    Example:
        # Move pane to right of target
        splitter.move_pane("pane-1", "pane-2", WherePosition.RIGHT)
    """

def extract_pane(self, pane_id: str) -> Optional[QWidget]:
    """
    Remove pane and return its widget.

    Args:
        pane_id: ID of pane to extract

    Returns:
        Widget instance if successful, None if failed

    Raises:
        PaneNotFoundError: If pane doesn't exist
        LastPaneError: If attempting to extract the only pane

    Example:
        # Extract widget for use elsewhere
        widget = splitter.extract_pane("pane-3")
        if widget:
            other_container.addWidget(widget)
    """
```

---

## Divider Control

### Ratio Management

```python
def move_divider(self, split_node_id: str, divider_index: int,
                ratio: float) -> bool:
    """
    Move divider to set new ratio.

    Args:
        split_node_id: ID of split node containing divider
        divider_index: Index of divider (0-based)
        ratio: New ratio for first child (0.1-0.9)

    Returns:
        True if moved, False if failed

    Raises:
        SplitNotFoundError: If split node doesn't exist
        InvalidRatioError: If ratio is outside valid range

    Example:
        # Set left pane to 30% width
        splitter.move_divider("split-1", 0, 0.3)
    """

def reset_ratios(self, split_node_id: Optional[str] = None) -> bool:
    """
    Reset ratios to equal distribution.

    Args:
        split_node_id: Specific split to reset, or None for all

    Returns:
        True if reset, False if failed

    Example:
        # Reset all splits to equal ratios
        splitter.reset_ratios()

        # Reset specific split
        splitter.reset_ratios("split-2")
    """

def get_divider_position(self, split_node_id: str,
                        divider_index: int) -> Optional[float]:
    """
    Get current divider ratio.

    Args:
        split_node_id: ID of split node
        divider_index: Index of divider

    Returns:
        Current ratio or None if not found

    Example:
        ratio = splitter.get_divider_position("split-1", 0)
        if ratio and ratio < 0.2:
            splitter.reset_ratios("split-1")
    """
```

### Size Constraints

```python
def set_pane_constraints(self, pane_id: str,
                        constraints: SizeConstraints) -> bool:
    """
    Set size constraints for pane.

    Args:
        pane_id: ID of pane
        constraints: Size constraint specification

    Returns:
        True if set, False if failed

    Example:
        constraints = SizeConstraints(
            min_width=200, min_height=100,
            max_width=800, preferred_width=400
        )
        splitter.set_pane_constraints("pane-1", constraints)
    """

def get_pane_constraints(self, pane_id: str) -> Optional[SizeConstraints]:
    """
    Get size constraints for pane.

    Args:
        pane_id: ID of pane

    Returns:
        Current constraints or None if not found
    """

def clear_pane_constraints(self, pane_id: str) -> bool:
    """
    Remove size constraints from pane.

    Args:
        pane_id: ID of pane

    Returns:
        True if cleared, False if failed
    """
```

---

## Undo/Redo Operations

### History Management

```python
def undo(self) -> bool:
    """
    Undo last command.

    Returns:
        True if undone, False if nothing to undo

    Example:
        # Undo with Ctrl+Z
        QShortcut(QKeySequence.Undo, self, splitter.undo)
    """

def redo(self) -> bool:
    """
    Redo last undone command.

    Returns:
        True if redone, False if nothing to redo

    Example:
        # Redo with Ctrl+Y
        QShortcut(QKeySequence.Redo, self, splitter.redo)
    """

def can_undo(self) -> bool:
    """
    Check if undo is available.

    Returns:
        True if commands available to undo

    Example:
        undo_action.setEnabled(splitter.can_undo())
    """

def can_redo(self) -> bool:
    """
    Check if redo is available.

    Returns:
        True if commands available to redo

    Example:
        redo_action.setEnabled(splitter.can_redo())
    """

def clear_history(self) -> None:
    """
    Clear all undo/redo history.

    Example:
        # Clear history after major operation
        splitter.restore_layout(saved_layout)
        splitter.clear_history()
    """

def get_undo_stack_size(self) -> int:
    """
    Get number of undoable commands.

    Returns:
        Number of commands in undo stack
    """
```

### Transaction Support

```python
def begin_transaction(self, description: str = "") -> None:
    """
    Begin command transaction for atomic operations.

    Args:
        description: Human-readable description

    Example:
        # Atomic multi-pane operation
        splitter.begin_transaction("Create 2x2 grid")
        try:
            splitter.split_with_widget(root, RIGHT, widget1, "w1")
            splitter.split_with_widget(pane1, BOTTOM, widget2, "w2")
            splitter.split_with_widget(pane2, BOTTOM, widget3, "w3")
            splitter.commit_transaction()
        except Exception:
            splitter.rollback_transaction()
    """

def commit_transaction(self) -> bool:
    """
    Commit current transaction.

    Returns:
        True if committed, False if no transaction
    """

def rollback_transaction(self) -> bool:
    """
    Rollback current transaction.

    Returns:
        True if rolled back, False if no transaction
    """

def is_in_transaction(self) -> bool:
    """
    Check if currently in transaction.

    Returns:
        True if transaction active
    """
```

---

## Persistence Operations

### Save/Restore Layout

```python
def save_layout(self) -> dict:
    """
    Save current layout to dictionary.

    Returns:
        Serialized layout data

    Example:
        layout = splitter.save_layout()
        with open("layout.json", "w") as f:
            json.dump(layout, f, indent=2)
    """

def restore_layout(self, layout_data: dict) -> bool:
    """
    Restore layout from dictionary.

    Args:
        layout_data: Previously saved layout

    Returns:
        True if restored, False if failed

    Raises:
        LayoutVersionError: If layout format is incompatible
        WidgetProviderError: If no provider set
        ValidationError: If restored layout is invalid

    Example:
        with open("layout.json", "r") as f:
            layout = json.load(f)
        success = splitter.restore_layout(layout)
    """

def export_layout(self, file_path: str,
                 include_metadata: bool = True) -> bool:
    """
    Export layout to file.

    Args:
        file_path: Target file path
        include_metadata: Whether to include metadata

    Returns:
        True if exported, False if failed

    Example:
        splitter.export_layout("workspace.json")
    """

def import_layout(self, file_path: str) -> bool:
    """
    Import layout from file.

    Args:
        file_path: Source file path

    Returns:
        True if imported, False if failed

    Example:
        if splitter.import_layout("workspace.json"):
            print("Layout restored successfully")
    """
```

### Session Management

```python
def save_session(self, include_widget_states: bool = False) -> dict:
    """
    Save complete session including widget states.

    Args:
        include_widget_states: Whether to save widget states

    Returns:
        Complete session data

    Note:
        Widget state saving requires provider support

    Example:
        session = splitter.save_session(include_widget_states=True)
        app_data = {"layout": session, "user_prefs": get_preferences()}
    """

def restore_session(self, session_data: dict) -> bool:
    """
    Restore complete session.

    Args:
        session_data: Previously saved session

    Returns:
        True if restored, False if failed

    Example:
        success = splitter.restore_session(app_data["layout"])
    """
```

---

## Properties and State

### Layout Information

```python
@property
def current_pane_id(self) -> Optional[str]:
    """Currently focused pane ID."""

@property
def all_pane_ids(self) -> list[str]:
    """All pane IDs in traversal order."""

@property
def selected_pane_ids(self) -> list[str]:
    """Currently selected pane IDs."""

@property
def pane_count(self) -> int:
    """Total number of panes."""

@property
def split_count(self) -> int:
    """Total number of split nodes."""

@property
def is_empty(self) -> bool:
    """True if no panes exist."""

@property
def root_is_split(self) -> bool:
    """True if root node is a split."""

@property
def max_depth(self) -> int:
    """Maximum tree depth."""
```

### Configuration Properties

```python
@property
def validation_mode(self) -> ValidationMode:
    """Current validation mode (STRICT, PERMISSIVE, DISABLED)."""

@validation_mode.setter
def validation_mode(self, mode: ValidationMode) -> None:
    """Set validation mode."""

@property
def max_panes(self) -> int:
    """Maximum allowed panes."""

@max_panes.setter
def max_panes(self, count: int) -> None:
    """Set maximum pane limit."""

@property
def min_pane_size(self) -> QSize:
    """Minimum pane size in pixels."""

@min_pane_size.setter
def min_pane_size(self, size: QSize) -> None:
    """Set minimum pane size."""

@property
def divider_width(self) -> int:
    """Divider width in pixels."""

@divider_width.setter
def divider_width(self, width: int) -> None:
    """Set divider width."""
```

### Runtime State

```python
@property
def modification_count(self) -> int:
    """Number of modifications made."""

@property
def last_modified(self) -> float:
    """Timestamp of last modification."""

@property
def has_unsaved_changes(self) -> bool:
    """True if changes since last save."""

@property
def is_valid(self) -> bool:
    """True if current state is valid."""

@property
def validation_errors(self) -> list[str]:
    """Current validation errors."""

@property
def performance_stats(self) -> dict:
    """Performance statistics."""
```

---

## Event Handling

### User Interaction Events

```python
def mousePressEvent(self, event: QMouseEvent) -> None:
    """Handle mouse press for pane selection and divider interaction."""

def mouseMoveEvent(self, event: QMouseEvent) -> None:
    """Handle mouse move for divider dragging."""

def mouseReleaseEvent(self, event: QMouseEvent) -> None:
    """Handle mouse release to complete divider operations."""

def keyPressEvent(self, event: QKeyEvent) -> None:
    """Handle keyboard navigation and shortcuts."""

def resizeEvent(self, event: QResizeEvent) -> None:
    """Handle widget resize to update layout."""

def contextMenuEvent(self, event: QContextMenuEvent) -> None:
    """Handle right-click context menu."""
```

### Custom Event Handlers

```python
def set_pane_double_click_handler(self, handler: Callable[[str], None]) -> None:
    """
    Set handler for pane double-click events.

    Args:
        handler: Function to call with pane_id

    Example:
        def on_pane_double_click(pane_id: str):
            widget = splitter.get_widget(pane_id)
            if hasattr(widget, 'maximize'):
                widget.maximize()

        splitter.set_pane_double_click_handler(on_pane_double_click)
    """

def set_divider_double_click_handler(self, handler: Callable[[str, int], None]) -> None:
    """
    Set handler for divider double-click events.

    Args:
        handler: Function to call with split_id and divider_index

    Example:
        def on_divider_double_click(split_id: str, divider_index: int):
            splitter.reset_ratios(split_id)

        splitter.set_divider_double_click_handler(on_divider_double_click)
    """

def set_empty_space_click_handler(self, handler: Callable[[QPoint], None]) -> None:
    """
    Set handler for clicks on empty space.

    Args:
        handler: Function to call with click position
    """
```

---

## Error Handling

### Exception Types

```python
class MultiSplitError(Exception):
    """Base exception for MultiSplit operations."""

class PaneNotFoundError(MultiSplitError):
    """Raised when pane ID is not found."""

class SplitNotFoundError(MultiSplitError):
    """Raised when split node ID is not found."""

class InvalidRatioError(MultiSplitError):
    """Raised when ratio is outside valid range."""

class MaxPanesExceededError(MultiSplitError):
    """Raised when pane limit is reached."""

class LockedPaneError(MultiSplitError):
    """Raised when attempting to modify locked pane."""

class LastPaneError(MultiSplitError):
    """Raised when attempting to close the only pane."""

class WidgetProviderError(MultiSplitError):
    """Raised when widget provider operation fails."""

class LayoutVersionError(MultiSplitError):
    """Raised when layout version is incompatible."""

class ValidationError(MultiSplitError):
    """Raised when validation fails."""
```

### Error Recovery

```python
def validate_state(self) -> list[str]:
    """
    Validate current state and return errors.

    Returns:
        List of validation error messages

    Example:
        errors = splitter.validate_state()
        if errors:
            print(f"Validation failed: {errors}")
            splitter.repair_state()
    """

def repair_state(self) -> bool:
    """
    Attempt to repair invalid state.

    Returns:
        True if repair successful, False if failed

    Example:
        if not splitter.is_valid:
            if splitter.repair_state():
                print("State repaired successfully")
            else:
                splitter.reset()
    """

def reset(self) -> None:
    """
    Reset to clean empty state.

    Example:
        # Emergency reset
        try:
            splitter.restore_layout(corrupted_layout)
        except Exception:
            splitter.reset()
            splitter.set_root_widget(default_widget, "default")
    """
```

---

## Performance Features

### Batch Operations

```python
def set_updates_enabled(self, enabled: bool) -> None:
    """
    Enable/disable UI updates for batch operations.

    Args:
        enabled: Whether to enable updates

    Example:
        # Batch multiple operations
        splitter.set_updates_enabled(False)
        try:
            for widget, widget_id in widgets:
                splitter.split_with_widget(current, RIGHT, widget, widget_id)
        finally:
            splitter.set_updates_enabled(True)
    """

def force_update(self) -> None:
    """
    Force immediate layout update.

    Example:
        splitter.force_update()  # Ensure layout is current
    """
```

### Optimization Settings

```python
def set_lazy_validation(self, enabled: bool) -> None:
    """
    Enable/disable lazy validation for performance.

    Args:
        enabled: Whether to defer validation
    """

def set_command_merging(self, enabled: bool) -> None:
    """
    Enable/disable command merging optimization.

    Args:
        enabled: Whether to merge rapid commands
    """

def get_performance_metrics(self) -> dict:
    """
    Get performance timing information.

    Returns:
        Dictionary with timing metrics

    Example:
        metrics = splitter.get_performance_metrics()
        avg_split_time = metrics["avg_split_time_ms"]
    """
```

---

## Common Pitfalls

### ❌ Widget Management Errors

```python
# DON'T: Create widgets without provider
splitter = MultiSplitWidget()
editor = CodeEditor()
splitter.set_root_widget(editor, "editor:main.py")  # May fail on restore

# DO: Always set provider first
splitter = MultiSplitWidget()
splitter.set_widget_provider(MyProvider())
editor = CodeEditor()
splitter.set_root_widget(editor, "editor:main.py")
```

### ❌ Invalid Operations

```python
# DON'T: Close the only pane
if splitter.pane_count == 1:
    splitter.close_current_pane()  # Raises LastPaneError

# DO: Check pane count first
if splitter.pane_count > 1:
    splitter.close_current_pane()
```

### ❌ State Assumptions

```python
# DON'T: Assume panes exist
pane_id = "pane-1"
widget = splitter.get_widget(pane_id)  # May return None
widget.setFocus()  # AttributeError if None

# DO: Always check existence
pane_id = "pane-1"
widget = splitter.get_widget(pane_id)
if widget:
    widget.setFocus()
```

### ❌ Ratio Mistakes

```python
# DON'T: Use invalid ratios
splitter.move_divider("split-1", 0, 0.05)  # Too small
splitter.move_divider("split-1", 0, 1.1)   # Too large

# DO: Keep ratios in valid range (0.1-0.9)
splitter.move_divider("split-1", 0, 0.3)   # Valid
```

### ❌ Transaction Errors

```python
# DON'T: Forget to commit transactions
splitter.begin_transaction()
splitter.split_with_widget(...)
# Transaction never committed - changes lost

# DO: Always commit or rollback
splitter.begin_transaction()
try:
    splitter.split_with_widget(...)
    splitter.commit_transaction()
except Exception:
    splitter.rollback_transaction()
```

---

## Quick Reference

### Core Operations
| Method | Purpose | Returns |
|--------|---------|---------|
| `set_root_widget()` | Set initial widget | `bool` |
| `split_with_widget()` | Add widget by splitting | `Optional[str]` |
| `replace_widget()` | Replace widget in pane | `bool` |
| `close_pane()` | Remove pane | `bool` |
| `focus_pane()` | Change focus | `bool` |

### Layout Control
| Method | Purpose | Returns |
|--------|---------|---------|
| `move_divider()` | Adjust split ratio | `bool` |
| `reset_ratios()` | Equal distribution | `bool` |
| `swap_panes()` | Exchange widgets | `bool` |
| `move_pane()` | Relocate pane | `bool` |
| `extract_pane()` | Remove and return widget | `Optional[QWidget]` |

### State Access
| Property | Type | Purpose |
|----------|------|---------|
| `current_pane_id` | `Optional[str]` | Focused pane |
| `all_pane_ids` | `list[str]` | All pane IDs |
| `pane_count` | `int` | Number of panes |
| `is_empty` | `bool` | No panes exist |
| `is_valid` | `bool` | State is valid |

### History Operations
| Method | Purpose | Returns |
|--------|---------|---------|
| `undo()` | Reverse last command | `bool` |
| `redo()` | Reapply command | `bool` |
| `can_undo()` | Check undo availability | `bool` |
| `can_redo()` | Check redo availability | `bool` |
| `clear_history()` | Remove all history | `None` |

### Persistence Operations
| Method | Purpose | Returns |
|--------|---------|---------|
| `save_layout()` | Serialize layout | `dict` |
| `restore_layout()` | Load layout | `bool` |
| `export_layout()` | Save to file | `bool` |
| `import_layout()` | Load from file | `bool` |

---

## Validation Checklist

- ✅ Widget provider is set before first widget operation
- ✅ All widget IDs are unique and stable
- ✅ Ratios are kept in valid range (0.1-0.9)
- ✅ Pane existence is checked before operations
- ✅ Transactions are properly committed or rolled back
- ✅ Error handling covers all exception types
- ✅ State validation is performed after complex operations
- ✅ Layout saves/restores are tested with real data
- ✅ Focus management works with keyboard navigation
- ✅ Performance is acceptable with large pane counts

## Related Documents

- **[Protocols](protocols.md)** - Widget provider and visitor interfaces
- **[Signals](signals.md)** - Complete signal reference and usage
- **[Widget Provider](../02-architecture/widget-provider.md)** - Provider pattern details
- **[MVC Architecture](../02-architecture/mvc-architecture.md)** - System architecture
- **[Usage Guide](../06-guides/usage-guide.md)** - Common usage patterns
- **[Integration Guide](../06-guides/integration-guide.md)** - Application integration
- **[Tree Structure](../02-architecture/tree-structure.md)** - Layout fundamentals
- **[Development Rules](../03-implementation/development-rules.md)** - Critical constraints

---

The public API provides complete control over MultiSplit layouts while maintaining clean separation of concerns through the widget provider pattern and robust error handling.