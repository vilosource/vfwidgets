# Signals

## Overview

MultiSplit provides a comprehensive signal system that enables applications to respond to layout changes, user interactions, and state transitions. The signals follow Qt conventions while providing rich contextual information for building responsive user interfaces.

## What This Covers

- **Lifecycle Signals**: Widget creation, modification, and removal events
- **User Action Signals**: Focus changes, selection updates, user interactions
- **Layout Signals**: Structure changes, divider movements, size adjustments
- **State Signals**: Validation events, error conditions, recovery operations
- **Performance Signals**: Timing information, resource usage, optimization events

## What This Doesn't Cover

- Signal implementation details (handled by framework)
- Custom signal creation (use standard Qt signals)
- Widget-specific signals (defined by individual widgets)
- Internal model signals (used only within MVC layers)

---

## Widget Lifecycle Signals

### Widget Management Events

```python
# Signal: widget_needed
widget_needed = Signal(str, str)  # (widget_id, pane_id)
"""
Emitted when MultiSplit needs a widget instance from the provider.

Emitted during:
- Layout restoration from saved state
- Undo/redo operations that recreate widgets
- Widget replacement operations
- Dynamic layout reconstruction

Parameters:
- widget_id (str): Identifier for the needed widget
- pane_id (str): Target pane where widget will be placed

Example Usage:
    def on_widget_needed(widget_id: str, pane_id: str):
        print(f"Creating widget {widget_id} for pane {pane_id}")
        widget = create_widget_for_id(widget_id)
        # Widget provider handles the actual creation

    splitter.widget_needed.connect(on_widget_needed)
"""

# Signal: widget_added
widget_added = Signal(str, str, QWidget)  # (widget_id, pane_id, widget)
"""
Emitted after widget is successfully added to layout.

Parameters:
- widget_id (str): Widget identifier
- pane_id (str): Pane containing the widget
- widget (QWidget): The actual widget instance

Example Usage:
    def on_widget_added(widget_id: str, pane_id: str, widget: QWidget):
        print(f"Widget {widget_id} added to pane {pane_id}")

        # Setup widget-specific connections
        if isinstance(widget, CodeEditor):
            widget.textChanged.connect(self.on_editor_changed)
            self.register_editor(widget, widget_id)

    splitter.widget_added.connect(on_widget_added)
"""

# Signal: widget_closing
widget_closing = Signal(str, QWidget)  # (widget_id, widget)
"""
Emitted before widget is removed from layout.

This is the final opportunity to:
- Save widget state
- Clean up resources
- Update application state
- Cache widget for reuse

Parameters:
- widget_id (str): Widget identifier
- widget (QWidget): Widget instance being removed

Example Usage:
    def on_widget_closing(widget_id: str, widget: QWidget):
        # Save widget state before removal
        if hasattr(widget, 'save_state'):
            self.widget_states[widget_id] = widget.save_state()

        # Clean up connections
        if isinstance(widget, CodeEditor):
            self.unregister_editor(widget_id)

        print(f"Widget {widget_id} is closing")

    splitter.widget_closing.connect(on_widget_closing)
"""

# Signal: widget_removed
widget_removed = Signal(str, str)  # (widget_id, pane_id)
"""
Emitted after widget is removed from layout.

Parameters:
- widget_id (str): Widget identifier that was removed
- pane_id (str): Pane that contained the widget

Example Usage:
    def on_widget_removed(widget_id: str, pane_id: str):
        print(f"Widget {widget_id} removed from pane {pane_id}")

        # Update UI state
        self.update_window_title()
        self.update_recent_files_menu()

        # Handle empty state
        if self.splitter.is_empty:
            self.show_welcome_screen()

    splitter.widget_removed.connect(on_widget_removed)
"""
```

### Widget State Changes

```python
# Signal: widget_replaced
widget_replaced = Signal(str, str, str, QWidget, QWidget)
# (pane_id, old_widget_id, new_widget_id, old_widget, new_widget)
"""
Emitted when widget in pane is replaced with different widget.

Parameters:
- pane_id (str): Pane where replacement occurred
- old_widget_id (str): Previous widget identifier
- new_widget_id (str): New widget identifier
- old_widget (QWidget): Previous widget instance
- new_widget (QWidget): New widget instance

Example Usage:
    def on_widget_replaced(pane_id: str, old_widget_id: str, new_widget_id: str,
                          old_widget: QWidget, new_widget: QWidget):
        print(f"Pane {pane_id}: {old_widget_id} -> {new_widget_id}")

        # Transfer state if possible
        if hasattr(old_widget, 'save_state') and hasattr(new_widget, 'restore_state'):
            state = old_widget.save_state()
            new_widget.restore_state(state)

    splitter.widget_replaced.connect(on_widget_replaced)
"""

# Signal: widget_modified
widget_modified = Signal(str, str, dict)  # (widget_id, pane_id, changes)
"""
Emitted when widget content or state is modified.

Note: Only emitted if widget reports modifications through standard signals.

Parameters:
- widget_id (str): Modified widget identifier
- pane_id (str): Pane containing the widget
- changes (dict): Dictionary describing changes

Example Usage:
    def on_widget_modified(widget_id: str, pane_id: str, changes: dict):
        print(f"Widget {widget_id} modified: {changes}")

        # Update modification indicators
        if 'content_modified' in changes:
            self.update_pane_title(pane_id, modified=True)

        # Auto-save if enabled
        if self.auto_save_enabled:
            self.schedule_auto_save(widget_id)

    splitter.widget_modified.connect(on_widget_modified)
"""
```

---

## User Action Signals

### Focus and Selection Events

```python
# Signal: pane_focused
pane_focused = Signal(str)  # (pane_id)
"""
Emitted when pane receives focus.

Parameters:
- pane_id (str): Newly focused pane identifier

Example Usage:
    def on_pane_focused(pane_id: str):
        print(f"Pane {pane_id} focused")

        # Update window title with focused widget
        widget = self.splitter.get_widget(pane_id)
        if hasattr(widget, 'get_display_title'):
            self.setWindowTitle(widget.get_display_title())

        # Update context menus
        self.update_context_menus(widget)

    splitter.pane_focused.connect(on_pane_focused)
"""

# Signal: focus_changed
focus_changed = Signal(str, str)  # (old_pane_id, new_pane_id)
"""
Emitted when focus moves between panes.

Parameters:
- old_pane_id (str): Previously focused pane (empty string if none)
- new_pane_id (str): Newly focused pane

Example Usage:
    def on_focus_changed(old_pane_id: str, new_pane_id: str):
        print(f"Focus changed: {old_pane_id} -> {new_pane_id}")

        # Update focus indicators
        if old_pane_id:
            self.update_pane_border(old_pane_id, focused=False)
        self.update_pane_border(new_pane_id, focused=True)

        # Save/restore selection state
        if old_pane_id:
            self.save_selection_state(old_pane_id)
        self.restore_selection_state(new_pane_id)

    splitter.focus_changed.connect(on_focus_changed)
"""

# Signal: pane_selected
pane_selected = Signal(str, bool)  # (pane_id, selected)
"""
Emitted when pane selection state changes.

Parameters:
- pane_id (str): Pane whose selection changed
- selected (bool): True if now selected, False if deselected

Example Usage:
    def on_pane_selected(pane_id: str, selected: bool):
        print(f"Pane {pane_id} {'selected' if selected else 'deselected'}")

        # Update visual state
        self.update_pane_selection_indicator(pane_id, selected)

        # Enable/disable multi-pane actions
        selected_count = len(self.splitter.selected_pane_ids)
        self.close_selected_action.setEnabled(selected_count > 0)

    splitter.pane_selected.connect(on_pane_selected)
"""

# Signal: selection_changed
selection_changed = Signal(list)  # (selected_pane_ids)
"""
Emitted when overall selection state changes.

Parameters:
- selected_pane_ids (list[str]): Currently selected pane IDs

Example Usage:
    def on_selection_changed(selected_pane_ids: list[str]):
        count = len(selected_pane_ids)
        print(f"Selection changed: {count} panes selected")

        # Update status bar
        if count == 0:
            self.statusbar.showMessage("No panes selected")
        elif count == 1:
            self.statusbar.showMessage(f"1 pane selected")
        else:
            self.statusbar.showMessage(f"{count} panes selected")

        # Update action availability
        self.update_selection_actions(selected_pane_ids)

    splitter.selection_changed.connect(on_selection_changed)
"""
```

### User Interaction Events

```python
# Signal: pane_clicked
pane_clicked = Signal(str, QMouseEvent)  # (pane_id, event)
"""
Emitted when user clicks on pane.

Parameters:
- pane_id (str): Clicked pane identifier
- event (QMouseEvent): Mouse event details

Example Usage:
    def on_pane_clicked(pane_id: str, event: QMouseEvent):
        print(f"Pane {pane_id} clicked with button {event.button()}")

        if event.button() == Qt.MiddleButton:
            # Middle click closes pane
            self.splitter.close_pane(pane_id)
        elif event.button() == Qt.RightButton:
            # Right click shows context menu
            self.show_pane_context_menu(pane_id, event.globalPos())

    splitter.pane_clicked.connect(on_pane_clicked)
"""

# Signal: pane_double_clicked
pane_double_clicked = Signal(str, QMouseEvent)  # (pane_id, event)
"""
Emitted when user double-clicks on pane.

Parameters:
- pane_id (str): Double-clicked pane identifier
- event (QMouseEvent): Mouse event details

Example Usage:
    def on_pane_double_clicked(pane_id: str, event: QMouseEvent):
        print(f"Pane {pane_id} double-clicked")

        # Double-click maximizes/restores pane
        if self.is_pane_maximized(pane_id):
            self.restore_pane_size(pane_id)
        else:
            self.maximize_pane(pane_id)

    splitter.pane_double_clicked.connect(on_pane_double_clicked)
"""

# Signal: pane_context_menu_requested
pane_context_menu_requested = Signal(str, QPoint)  # (pane_id, global_pos)
"""
Emitted when context menu is requested for pane.

Parameters:
- pane_id (str): Pane identifier
- global_pos (QPoint): Global position for menu

Example Usage:
    def on_pane_context_menu_requested(pane_id: str, global_pos: QPoint):
        print(f"Context menu requested for pane {pane_id}")

        menu = QMenu()

        # Add pane-specific actions
        menu.addAction("Close", lambda: self.splitter.close_pane(pane_id))
        menu.addAction("Split Right", lambda: self.split_pane_right(pane_id))
        menu.addAction("Split Down", lambda: self.split_pane_down(pane_id))

        # Add widget-specific actions
        widget = self.splitter.get_widget(pane_id)
        if hasattr(widget, 'add_context_actions'):
            widget.add_context_actions(menu)

        menu.exec_(global_pos)

    splitter.pane_context_menu_requested.connect(on_pane_context_menu_requested)
"""
```

---

## Layout Structure Signals

### Tree Modification Events

```python
# Signal: pane_added
pane_added = Signal(str, str, str)  # (pane_id, widget_id, operation)
"""
Emitted when new pane is added to layout.

Parameters:
- pane_id (str): New pane identifier
- widget_id (str): Widget placed in new pane
- operation (str): How pane was added ("split", "replace", "restore")

Example Usage:
    def on_pane_added(pane_id: str, widget_id: str, operation: str):
        print(f"Pane {pane_id} added via {operation} with widget {widget_id}")

        # Update pane count display
        self.update_pane_count_display()

        # Configure new pane
        if operation == "split":
            self.setup_split_pane(pane_id)
        elif operation == "restore":
            self.restore_pane_settings(pane_id)

    splitter.pane_added.connect(on_pane_added)
"""

# Signal: pane_removed
pane_removed = Signal(str, str)  # (pane_id, operation)
"""
Emitted when pane is removed from layout.

Parameters:
- pane_id (str): Removed pane identifier
- operation (str): How pane was removed ("close", "merge", "undo")

Example Usage:
    def on_pane_removed(pane_id: str, operation: str):
        print(f"Pane {pane_id} removed via {operation}")

        # Clean up pane-specific state
        self.cleanup_pane_state(pane_id)

        # Update UI
        self.update_pane_count_display()

        # Handle edge cases
        if self.splitter.pane_count == 0:
            self.handle_empty_layout()

    splitter.pane_removed.connect(on_pane_removed)
"""

# Signal: panes_swapped
panes_swapped = Signal(str, str)  # (pane_id_a, pane_id_b)
"""
Emitted when two panes exchange widgets.

Parameters:
- pane_id_a (str): First pane identifier
- pane_id_b (str): Second pane identifier

Example Usage:
    def on_panes_swapped(pane_id_a: str, pane_id_b: str):
        print(f"Panes swapped: {pane_id_a} <-> {pane_id_b}")

        # Update any pane-specific UI state
        self.swap_pane_ui_state(pane_id_a, pane_id_b)

        # Notify widgets of position change
        widget_a = self.splitter.get_widget(pane_id_a)
        widget_b = self.splitter.get_widget(pane_id_b)

        if hasattr(widget_a, 'pane_position_changed'):
            widget_a.pane_position_changed(pane_id_a)
        if hasattr(widget_b, 'pane_position_changed'):
            widget_b.pane_position_changed(pane_id_b)

    splitter.panes_swapped.connect(on_panes_swapped)
"""

# Signal: layout_changed
layout_changed = Signal()
"""
Emitted when overall layout structure changes.

This is a general signal emitted after any structural change.
Use specific signals for detailed information.

Example Usage:
    def on_layout_changed():
        print("Layout structure changed")

        # Update navigation menus
        self.rebuild_window_menu()

        # Save layout state
        if self.auto_save_layout:
            self.save_current_layout()

        # Update window geometry if needed
        self.adjust_window_size_to_content()

    splitter.layout_changed.connect(on_layout_changed)
"""
```

### Split and Merge Events

```python
# Signal: pane_split
pane_split = Signal(str, str, str, float)  # (original_pane_id, new_pane_id, orientation, ratio)
"""
Emitted when pane is split into two.

Parameters:
- original_pane_id (str): Pane that was split
- new_pane_id (str): Newly created pane
- orientation (str): Split orientation ("horizontal" or "vertical")
- ratio (float): Size ratio of first pane

Example Usage:
    def on_pane_split(original_pane_id: str, new_pane_id: str,
                     orientation: str, ratio: float):
        print(f"Pane {original_pane_id} split {orientation} at {ratio:.2f}")
        print(f"New pane: {new_pane_id}")

        # Adjust UI for split layout
        if orientation == "horizontal":
            self.optimize_for_horizontal_split()
        else:
            self.optimize_for_vertical_split()

        # Update pane tracking
        self.register_split_relationship(original_pane_id, new_pane_id)

    splitter.pane_split.connect(on_pane_split)
"""

# Signal: panes_merged
panes_merged = Signal(str, str, str)  # (remaining_pane_id, removed_pane_id, direction)
"""
Emitted when two panes are merged into one.

Parameters:
- remaining_pane_id (str): Pane that remains after merge
- removed_pane_id (str): Pane that was removed
- direction (str): Merge direction ("left", "right", "up", "down")

Example Usage:
    def on_panes_merged(remaining_pane_id: str, removed_pane_id: str, direction: str):
        print(f"Panes merged: {removed_pane_id} -> {remaining_pane_id} ({direction})")

        # Clean up removed pane state
        self.cleanup_pane_references(removed_pane_id)

        # Update remaining pane
        self.expand_pane_features(remaining_pane_id)

        # Adjust layout optimization
        self.optimize_single_pane_layout()

    splitter.panes_merged.connect(on_panes_merged)
"""
```

---

## Divider and Size Signals

### Divider Interaction Events

```python
# Signal: divider_moved
divider_moved = Signal(str, int, float)  # (split_id, divider_index, ratio)
"""
Emitted when divider position changes.

Parameters:
- split_id (str): Split node identifier
- divider_index (int): Index of moved divider
- ratio (float): New ratio for first child

Example Usage:
    def on_divider_moved(split_id: str, divider_index: int, ratio: float):
        print(f"Divider {divider_index} in split {split_id} moved to {ratio:.3f}")

        # Save divider position preferences
        self.save_divider_preference(split_id, divider_index, ratio)

        # Update size-dependent features
        affected_panes = self.get_panes_in_split(split_id)
        for pane_id in affected_panes:
            widget = self.splitter.get_widget(pane_id)
            if hasattr(widget, 'size_changed'):
                widget.size_changed()

    splitter.divider_moved.connect(on_divider_moved)
"""

# Signal: divider_double_clicked
divider_double_clicked = Signal(str, int)  # (split_id, divider_index)
"""
Emitted when divider is double-clicked.

Parameters:
- split_id (str): Split node identifier
- divider_index (int): Index of double-clicked divider

Example Usage:
    def on_divider_double_clicked(split_id: str, divider_index: int):
        print(f"Divider {divider_index} in split {split_id} double-clicked")

        # Reset to equal ratios
        self.splitter.reset_ratios(split_id)

        # Provide user feedback
        self.show_temporary_message("Divider reset to equal ratios")

    splitter.divider_double_clicked.connect(on_divider_double_clicked)
"""

# Signal: divider_drag_started
divider_drag_started = Signal(str, int, QPoint)  # (split_id, divider_index, start_pos)
"""
Emitted when divider drag operation begins.

Parameters:
- split_id (str): Split node identifier
- divider_index (int): Index of dragged divider
- start_pos (QPoint): Initial drag position

Example Usage:
    def on_divider_drag_started(split_id: str, divider_index: int, start_pos: QPoint):
        print(f"Started dragging divider {divider_index} in split {split_id}")

        # Show drag feedback
        self.show_divider_drag_indicator()

        # Disable updates during drag for performance
        self.splitter.set_updates_enabled(False)

        # Store initial state for snapping
        self.drag_start_ratio = self.splitter.get_divider_position(split_id, divider_index)

    splitter.divider_drag_started.connect(on_divider_drag_started)
"""

# Signal: divider_drag_finished
divider_drag_finished = Signal(str, int, QPoint, float)  # (split_id, divider_index, end_pos, final_ratio)
"""
Emitted when divider drag operation completes.

Parameters:
- split_id (str): Split node identifier
- divider_index (int): Index of dragged divider
- end_pos (QPoint): Final drag position
- final_ratio (float): Final ratio after drag

Example Usage:
    def on_divider_drag_finished(split_id: str, divider_index: int,
                                end_pos: QPoint, final_ratio: float):
        print(f"Finished dragging divider {divider_index} to ratio {final_ratio:.3f}")

        # Re-enable updates
        self.splitter.set_updates_enabled(True)

        # Hide drag feedback
        self.hide_divider_drag_indicator()

        # Save preference
        self.save_divider_preference(split_id, divider_index, final_ratio)

    splitter.divider_drag_finished.connect(on_divider_drag_finished)
"""
```

### Size and Constraint Events

```python
# Signal: pane_resized
pane_resized = Signal(str, QSize, QSize)  # (pane_id, old_size, new_size)
"""
Emitted when pane size changes significantly.

Parameters:
- pane_id (str): Resized pane identifier
- old_size (QSize): Previous size
- new_size (QSize): New size

Example Usage:
    def on_pane_resized(pane_id: str, old_size: QSize, new_size: QSize):
        print(f"Pane {pane_id} resized: {old_size} -> {new_size}")

        # Notify widget of size change
        widget = self.splitter.get_widget(pane_id)
        if hasattr(widget, 'optimal_size_changed'):
            widget.optimal_size_changed(new_size)

        # Update size-dependent UI
        if new_size.width() < 200:
            self.switch_to_compact_mode(pane_id)
        else:
            self.switch_to_normal_mode(pane_id)

    splitter.pane_resized.connect(on_pane_resized)
"""

# Signal: size_constraints_changed
size_constraints_changed = Signal(str, dict)  # (pane_id, constraints)
"""
Emitted when pane size constraints are modified.

Parameters:
- pane_id (str): Pane identifier
- constraints (dict): New constraint values

Example Usage:
    def on_size_constraints_changed(pane_id: str, constraints: dict):
        print(f"Size constraints changed for pane {pane_id}: {constraints}")

        # Update UI to reflect constraints
        min_size = constraints.get('min_size', QSize())
        max_size = constraints.get('max_size', QSize())

        # Adjust current layout if needed
        current_size = self.get_pane_size(pane_id)
        if current_size.width() < min_size.width():
            self.adjust_pane_to_min_size(pane_id)

    splitter.size_constraints_changed.connect(on_size_constraints_changed)
"""

# Signal: minimum_size_changed
minimum_size_changed = Signal(QSize, QSize)  # (old_min_size, new_min_size)
"""
Emitted when overall widget minimum size changes.

Parameters:
- old_min_size (QSize): Previous minimum size
- new_min_size (QSize): New minimum size

Example Usage:
    def on_minimum_size_changed(old_min_size: QSize, new_min_size: QSize):
        print(f"Minimum size changed: {old_min_size} -> {new_min_size}")

        # Adjust window size if needed
        current_size = self.size()
        if (current_size.width() < new_min_size.width() or
            current_size.height() < new_min_size.height()):
            self.resize(new_min_size.expandedTo(current_size))

    splitter.minimum_size_changed.connect(on_minimum_size_changed)
"""
```

---

## State and Validation Signals

### Validation Events

```python
# Signal: validation_failed
validation_failed = Signal(list, str)  # (errors, operation)
"""
Emitted when state validation fails.

Parameters:
- errors (list[str]): List of validation error messages
- operation (str): Operation that triggered validation

Example Usage:
    def on_validation_failed(errors: list[str], operation: str):
        print(f"Validation failed during {operation}:")
        for error in errors:
            print(f"  - {error}")

        # Show error dialog
        error_text = f"Operation '{operation}' failed validation:\n" + "\n".join(errors)
        QMessageBox.warning(self, "Validation Error", error_text)

        # Attempt automatic repair
        if self.auto_repair_enabled:
            self.splitter.repair_state()

    splitter.validation_failed.connect(on_validation_failed)
"""

# Signal: state_repaired
state_repaired = Signal(list, list)  # (fixed_errors, remaining_errors)
"""
Emitted after automatic state repair attempt.

Parameters:
- fixed_errors (list[str]): Errors that were successfully fixed
- remaining_errors (list[str]): Errors that could not be fixed

Example Usage:
    def on_state_repaired(fixed_errors: list[str], remaining_errors: list[str]):
        print(f"State repair completed:")
        print(f"  Fixed: {len(fixed_errors)} errors")
        print(f"  Remaining: {len(remaining_errors)} errors")

        if remaining_errors:
            # Manual intervention required
            self.show_manual_repair_dialog(remaining_errors)
        else:
            # Success message
            self.show_temporary_message("State automatically repaired")

    splitter.state_repaired.connect(on_state_repaired)
"""

# Signal: corruption_detected
corruption_detected = Signal(str, dict)  # (corruption_type, details)
"""
Emitted when serious state corruption is detected.

Parameters:
- corruption_type (str): Type of corruption detected
- details (dict): Additional information about the corruption

Example Usage:
    def on_corruption_detected(corruption_type: str, details: dict):
        print(f"Corruption detected: {corruption_type}")
        print(f"Details: {details}")

        # Emergency save before repair attempt
        self.emergency_save_session()

        # Show critical error dialog
        msg = f"Critical error detected: {corruption_type}\n"
        msg += "Session has been saved. Application will attempt recovery."
        QMessageBox.critical(self, "Critical Error", msg)

        # Attempt recovery
        self.splitter.reset()
        self.restore_emergency_session()

    splitter.corruption_detected.connect(on_corruption_detected)
"""
```

### Undo/Redo Events

```python
# Signal: command_executed
command_executed = Signal(str, dict)  # (command_name, command_data)
"""
Emitted when command is successfully executed.

Parameters:
- command_name (str): Name of executed command
- command_data (dict): Command parameters and results

Example Usage:
    def on_command_executed(command_name: str, command_data: dict):
        print(f"Command executed: {command_name}")

        # Update undo/redo UI
        self.undo_action.setEnabled(self.splitter.can_undo())
        self.redo_action.setEnabled(self.splitter.can_redo())

        # Log command for debugging
        self.command_history.append({
            'name': command_name,
            'data': command_data,
            'timestamp': time.time()
        })

    splitter.command_executed.connect(on_command_executed)
"""

# Signal: command_undone
command_undone = Signal(str, dict)  # (command_name, command_data)
"""
Emitted when command is undone.

Parameters:
- command_name (str): Name of undone command
- command_data (dict): Command parameters

Example Usage:
    def on_command_undone(command_name: str, command_data: dict):
        print(f"Command undone: {command_name}")

        # Update UI state
        self.undo_action.setEnabled(self.splitter.can_undo())
        self.redo_action.setEnabled(self.splitter.can_redo())

        # Show feedback
        self.show_temporary_message(f"Undid: {command_name}")

    splitter.command_undone.connect(on_command_undone)
"""

# Signal: command_redone
command_redone = Signal(str, dict)  # (command_name, command_data)
"""
Emitted when command is redone.

Parameters:
- command_name (str): Name of redone command
- command_data (dict): Command parameters

Example Usage:
    def on_command_redone(command_name: str, command_data: dict):
        print(f"Command redone: {command_name}")

        # Update UI state
        self.undo_action.setEnabled(self.splitter.can_undo())
        self.redo_action.setEnabled(self.splitter.can_redo())

        # Show feedback
        self.show_temporary_message(f"Redid: {command_name}")

    splitter.command_redone.connect(on_command_redone)
"""

# Signal: history_cleared
history_cleared = Signal()
"""
Emitted when undo/redo history is cleared.

Example Usage:
    def on_history_cleared():
        print("Command history cleared")

        # Update UI
        self.undo_action.setEnabled(False)
        self.redo_action.setEnabled(False)

        # Clear history-dependent features
        self.clear_command_log()

    splitter.history_cleared.connect(on_history_cleared)
"""
```

---

## Performance and Resource Signals

### Timing and Performance Events

```python
# Signal: performance_warning
performance_warning = Signal(str, float, dict)  # (operation, duration_ms, context)
"""
Emitted when operation takes longer than expected.

Parameters:
- operation (str): Name of slow operation
- duration_ms (float): Operation duration in milliseconds
- context (dict): Additional context information

Example Usage:
    def on_performance_warning(operation: str, duration_ms: float, context: dict):
        print(f"Performance warning: {operation} took {duration_ms:.1f}ms")
        print(f"Context: {context}")

        # Log performance issue
        self.performance_log.append({
            'operation': operation,
            'duration': duration_ms,
            'context': context,
            'timestamp': time.time()
        })

        # Show warning for very slow operations
        if duration_ms > 1000:  # 1 second
            self.show_temporary_message(f"Slow operation: {operation}")

    splitter.performance_warning.connect(on_performance_warning)
"""

# Signal: memory_usage_changed
memory_usage_changed = Signal(dict)  # (usage_stats)
"""
Emitted when memory usage changes significantly.

Parameters:
- usage_stats (dict): Memory usage statistics

Example Usage:
    def on_memory_usage_changed(usage_stats: dict):
        total_mb = usage_stats.get('total_mb', 0)
        widget_count = usage_stats.get('widget_count', 0)

        print(f"Memory usage: {total_mb:.1f}MB for {widget_count} widgets")

        # Show warning for high usage
        if total_mb > 500:  # 500MB threshold
            self.show_memory_warning(total_mb)

        # Update memory display
        self.update_memory_indicator(total_mb)

    splitter.memory_usage_changed.connect(on_memory_usage_changed)
"""

# Signal: optimization_applied
optimization_applied = Signal(str, dict)  # (optimization_type, results)
"""
Emitted when performance optimization is applied.

Parameters:
- optimization_type (str): Type of optimization
- results (dict): Optimization results and metrics

Example Usage:
    def on_optimization_applied(optimization_type: str, results: dict):
        print(f"Optimization applied: {optimization_type}")
        print(f"Results: {results}")

        # Log optimization
        improvement = results.get('improvement_percent', 0)
        if improvement > 10:  # Significant improvement
            message = f"Performance improved {improvement:.1f}% ({optimization_type})"
            self.show_temporary_message(message)

    splitter.optimization_applied.connect(on_optimization_applied)
"""
```

### Resource Management Events

```python
# Signal: widget_pool_changed
widget_pool_changed = Signal(int, int, int)  # (active_count, pooled_count, total_created)
"""
Emitted when widget pool statistics change.

Parameters:
- active_count (int): Number of widgets in use
- pooled_count (int): Number of widgets in pool
- total_created (int): Total widgets created since start

Example Usage:
    def on_widget_pool_changed(active_count: int, pooled_count: int, total_created: int):
        print(f"Widget pool: {active_count} active, {pooled_count} pooled, {total_created} total")

        # Update debug display
        if self.debug_mode:
            self.update_widget_pool_display(active_count, pooled_count, total_created)

        # Warn about pool exhaustion
        if pooled_count == 0 and active_count > 50:
            print("Warning: Widget pool exhausted with high active count")

    splitter.widget_pool_changed.connect(on_widget_pool_changed)
"""

# Signal: cache_statistics_changed
cache_statistics_changed = Signal(dict)  # (cache_stats)
"""
Emitted when cache performance statistics change.

Parameters:
- cache_stats (dict): Cache hit/miss ratios and sizes

Example Usage:
    def on_cache_statistics_changed(cache_stats: dict):
        hit_ratio = cache_stats.get('hit_ratio', 0)
        cache_size = cache_stats.get('size_mb', 0)

        print(f"Cache stats: {hit_ratio:.1%} hit ratio, {cache_size:.1f}MB")

        # Adjust cache size if needed
        if hit_ratio < 0.5:  # Poor hit ratio
            self.increase_cache_size()
        elif cache_size > 100:  # Too large
            self.trim_cache()

    splitter.cache_statistics_changed.connect(on_cache_statistics_changed)
"""
```

---

## Error and Recovery Signals

### Error Events

```python
# Signal: error_occurred
error_occurred = Signal(str, Exception, dict)  # (operation, error, context)
"""
Emitted when recoverable error occurs.

Parameters:
- operation (str): Operation that failed
- error (Exception): The exception that occurred
- context (dict): Additional context information

Example Usage:
    def on_error_occurred(operation: str, error: Exception, context: dict):
        print(f"Error in {operation}: {error}")
        print(f"Context: {context}")

        # Log error
        self.error_log.append({
            'operation': operation,
            'error': str(error),
            'type': type(error).__name__,
            'context': context,
            'timestamp': time.time()
        })

        # Show user-friendly error message
        self.show_error_message(operation, str(error))

    splitter.error_occurred.connect(on_error_occurred)
"""

# Signal: recovery_attempted
recovery_attempted = Signal(str, bool, str)  # (error_type, success, details)
"""
Emitted when automatic error recovery is attempted.

Parameters:
- error_type (str): Type of error being recovered from
- success (bool): Whether recovery was successful
- details (str): Details about recovery attempt

Example Usage:
    def on_recovery_attempted(error_type: str, success: bool, details: str):
        print(f"Recovery from {error_type}: {'success' if success else 'failed'}")
        print(f"Details: {details}")

        if success:
            self.show_temporary_message(f"Recovered from {error_type}")
        else:
            self.show_error_message("Recovery Failed", details)
            # May need manual intervention

    splitter.recovery_attempted.connect(on_recovery_attempted)
"""

# Signal: critical_error
critical_error = Signal(str, Exception)  # (operation, error)
"""
Emitted when critical, non-recoverable error occurs.

Parameters:
- operation (str): Operation that failed critically
- error (Exception): The critical error

Example Usage:
    def on_critical_error(operation: str, error: Exception):
        print(f"CRITICAL ERROR in {operation}: {error}")

        # Emergency save
        try:
            self.emergency_save_all()
        except:
            pass  # Don't make it worse

        # Show critical error dialog
        msg = f"Critical error in {operation}:\n{error}\n\n"
        msg += "Application state has been saved and will restart."
        QMessageBox.critical(self, "Critical Error", msg)

        # Restart application
        self.restart_application()

    splitter.critical_error.connect(on_critical_error)
"""
```

---

## Signal Connection Patterns

### Basic Connection Pattern

```python
class MyApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.splitter = MultiSplitWidget()
        self.setup_signal_connections()

    def setup_signal_connections(self):
        """Connect all MultiSplit signals to handlers"""

        # Widget lifecycle
        self.splitter.widget_added.connect(self.on_widget_added)
        self.splitter.widget_closing.connect(self.on_widget_closing)
        self.splitter.widget_removed.connect(self.on_widget_removed)

        # User actions
        self.splitter.pane_focused.connect(self.on_pane_focused)
        self.splitter.pane_clicked.connect(self.on_pane_clicked)
        self.splitter.pane_double_clicked.connect(self.on_pane_double_clicked)

        # Layout changes
        self.splitter.layout_changed.connect(self.on_layout_changed)
        self.splitter.pane_split.connect(self.on_pane_split)
        self.splitter.divider_moved.connect(self.on_divider_moved)

        # Error handling
        self.splitter.error_occurred.connect(self.on_error_occurred)
        self.splitter.validation_failed.connect(self.on_validation_failed)
```

### Selective Connection Pattern

```python
class MinimalApplication(QWidget):
    def __init__(self):
        super().__init__()
        self.splitter = MultiSplitWidget()

        # Connect only essential signals
        self.splitter.widget_closing.connect(self.save_widget_state)
        self.splitter.layout_changed.connect(self.update_window_title)
        self.splitter.error_occurred.connect(self.handle_error)

    def save_widget_state(self, widget_id: str, widget: QWidget):
        """Save widget state before closure"""
        if hasattr(widget, 'save_state'):
            self.widget_states[widget_id] = widget.save_state()

    def update_window_title(self):
        """Update title based on current layout"""
        count = self.splitter.pane_count
        self.setWindowTitle(f"MyApp - {count} panes")

    def handle_error(self, operation: str, error: Exception, context: dict):
        """Basic error handling"""
        print(f"Error in {operation}: {error}")
```

### Advanced Signal Processing

```python
class AdvancedApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.splitter = MultiSplitWidget()
        self.signal_processor = SignalProcessor()
        self.setup_advanced_connections()

    def setup_advanced_connections(self):
        """Setup advanced signal processing"""

        # Batch similar signals
        self.signal_processor.batch_signals([
            self.splitter.divider_moved,
            self.splitter.pane_resized
        ], self.on_layout_geometry_changed, delay_ms=100)

        # Filter signals by conditions
        self.signal_processor.filter_signal(
            self.splitter.widget_modified,
            lambda widget_id, pane_id, changes: 'content' in changes,
            self.on_content_modified
        )

        # Transform signal data
        self.signal_processor.transform_signal(
            self.splitter.pane_focused,
            lambda pane_id: self.splitter.get_widget(pane_id),
            self.on_widget_focused
        )

    def on_layout_geometry_changed(self, batched_signals: list):
        """Handle batched geometry changes"""
        print(f"Processed {len(batched_signals)} geometry changes")
        self.update_layout_dependent_features()

    def on_content_modified(self, widget_id: str, pane_id: str, changes: dict):
        """Handle only content modifications"""
        print(f"Content modified in {widget_id}")
        self.update_modification_indicator(pane_id, True)

    def on_widget_focused(self, widget: QWidget):
        """Handle focus with actual widget instance"""
        if hasattr(widget, 'get_status_info'):
            self.statusbar.showMessage(widget.get_status_info())
```

---

## Common Pitfalls

### ❌ Signal Connection Mistakes

```python
# DON'T: Connect to non-existent signals
splitter.pane_activated.connect(handler)  # No such signal!

# DON'T: Wrong parameter count in handler
def bad_handler(pane_id: str):  # Missing parameters!
    pass
splitter.focus_changed.connect(bad_handler)  # Expects (old_id, new_id)

# DO: Check signal signatures and parameter counts
def good_handler(old_pane_id: str, new_pane_id: str):
    print(f"Focus: {old_pane_id} -> {new_pane_id}")
splitter.focus_changed.connect(good_handler)
```

### ❌ Signal Handler Errors

```python
# DON'T: Cause side effects that trigger more signals
def bad_layout_handler():
    # This will trigger more layout_changed signals!
    splitter.split_with_widget(...)

# DON'T: Perform expensive operations in signal handlers
def slow_handler(pane_id: str):
    time.sleep(1)  # Blocks UI!
    expensive_database_operation()

# DO: Use queued operations for complex work
def good_handler(pane_id: str):
    QTimer.singleShot(0, lambda: self.handle_async(pane_id))
```

### ❌ Memory Leaks in Connections

```python
# DON'T: Create circular references
class BadWidget:
    def __init__(self, splitter):
        self.splitter = splitter
        # Circular reference - widget holds splitter, splitter holds widget
        splitter.widget_added.connect(lambda w_id, p_id, w: self.store_widget(w))

# DO: Use weak references or proper cleanup
class GoodWidget:
    def __init__(self, splitter):
        self.splitter_ref = weakref.ref(splitter)
        splitter.widget_added.connect(self.on_widget_added)

    def cleanup(self):
        splitter = self.splitter_ref()
        if splitter:
            splitter.widget_added.disconnect(self.on_widget_added)
```

### ❌ Signal Ordering Assumptions

```python
# DON'T: Assume signal order
def bad_handler():
    # Assuming widget_added comes before layout_changed
    # This assumption may be wrong!
    widget = self.last_added_widget
    widget.setup()

# DO: Use signal parameters, not assumptions
def good_handler(widget_id: str, pane_id: str, widget: QWidget):
    # Use the provided widget instance
    widget.setup()
```

### ❌ Exception Handling in Signals

```python
# DON'T: Let exceptions propagate from signal handlers
def bad_handler(pane_id: str):
    widget = self.widgets[pane_id]  # May raise KeyError!
    widget.focus()

# DO: Handle exceptions in signal handlers
def good_handler(pane_id: str):
    try:
        widget = self.widgets.get(pane_id)
        if widget:
            widget.focus()
    except Exception as e:
        print(f"Error in signal handler: {e}")
```

---

## Quick Reference

### Lifecycle Signals
| Signal | Parameters | Purpose |
|--------|------------|---------|
| `widget_needed` | `(widget_id, pane_id)` | Provider should create widget |
| `widget_added` | `(widget_id, pane_id, widget)` | Widget added to layout |
| `widget_closing` | `(widget_id, widget)` | Widget about to be removed |
| `widget_removed` | `(widget_id, pane_id)` | Widget removed from layout |
| `widget_replaced` | `(pane_id, old_id, new_id, old_widget, new_widget)` | Widget replaced |

### User Action Signals
| Signal | Parameters | Purpose |
|--------|------------|---------|
| `pane_focused` | `(pane_id)` | Pane gained focus |
| `focus_changed` | `(old_pane_id, new_pane_id)` | Focus moved between panes |
| `pane_clicked` | `(pane_id, event)` | User clicked pane |
| `pane_double_clicked` | `(pane_id, event)` | User double-clicked pane |
| `selection_changed` | `(selected_pane_ids)` | Selection state changed |

### Layout Signals
| Signal | Parameters | Purpose |
|--------|------------|---------|
| `layout_changed` | `()` | Overall structure changed |
| `pane_added` | `(pane_id, widget_id, operation)` | New pane created |
| `pane_removed` | `(pane_id, operation)` | Pane removed |
| `pane_split` | `(original_id, new_id, orientation, ratio)` | Pane split into two |
| `panes_merged` | `(remaining_id, removed_id, direction)` | Two panes merged |

### Divider Signals
| Signal | Parameters | Purpose |
|--------|------------|---------|
| `divider_moved` | `(split_id, index, ratio)` | Divider position changed |
| `divider_double_clicked` | `(split_id, index)` | Divider double-clicked |
| `divider_drag_started` | `(split_id, index, start_pos)` | Drag operation began |
| `divider_drag_finished` | `(split_id, index, end_pos, ratio)` | Drag operation completed |

### State Signals
| Signal | Parameters | Purpose |
|--------|------------|---------|
| `validation_failed` | `(errors, operation)` | State validation failed |
| `state_repaired` | `(fixed_errors, remaining_errors)` | Automatic repair completed |
| `corruption_detected` | `(corruption_type, details)` | Serious corruption found |
| `command_executed` | `(command_name, command_data)` | Command successfully executed |

---

## Validation Checklist

- ✅ All signal handlers have correct parameter counts
- ✅ Signal handlers don't cause infinite signal loops
- ✅ Expensive operations are queued, not done directly in handlers
- ✅ Exception handling is present in all signal handlers
- ✅ Signal connections are properly cleaned up when widgets are destroyed
- ✅ No assumptions about signal emission order
- ✅ Memory leaks from circular references are avoided
- ✅ Signal handlers don't modify layout during layout change signals
- ✅ UI updates from signals are batched when appropriate
- ✅ Debug/logging code doesn't impact performance

## Related Documents

- **[Public API](public-api.md)** - Widget methods that emit these signals
- **[Protocols](protocols.md)** - Interfaces that receive signal notifications
- **[Widget Provider](../02-architecture/widget-provider.md)** - Provider signal handling
- **[Usage Guide](../06-guides/usage-guide.md)** - Practical signal usage examples
- **[Controller Design](../04-design/controller-design.md)** - Command execution signals
- **[Model Design](../04-design/model-design.md)** - Internal model signals
- **[View Design](../04-design/view-design.md)** - UI event signal handling
- **[Focus Management](../04-design/focus-management.md)** - Focus-related signals

---

The signal system provides comprehensive event notification for all MultiSplit operations, enabling applications to build rich, responsive user interfaces that react appropriately to layout changes and user interactions.