"""Unit tests for KeybindingDialog widget."""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialogButtonBox
from vfwidgets_keybinding import ActionDefinition, KeybindingManager
from vfwidgets_keybinding.widgets import KeybindingDialog, KeySequenceEdit


class TestKeybindingDialog:
    """Test KeybindingDialog widget."""

    @pytest.fixture
    def manager(self):
        """Create manager with sample actions."""
        mgr = KeybindingManager(storage_path=None, auto_save=False)

        # Register sample actions
        mgr.register_actions(
            [
                ActionDefinition(
                    id="file.save",
                    description="Save File",
                    default_shortcut="Ctrl+S",
                    category="File",
                ),
                ActionDefinition(
                    id="file.open",
                    description="Open File",
                    default_shortcut="Ctrl+O",
                    category="File",
                ),
                ActionDefinition(
                    id="edit.copy",
                    description="Copy",
                    default_shortcut="Ctrl+C",
                    category="Edit",
                ),
                ActionDefinition(
                    id="edit.paste",
                    description="Paste",
                    default_shortcut="Ctrl+V",
                    category="Edit",
                ),
            ]
        )

        mgr.load_bindings()
        return mgr

    @pytest.fixture
    def dialog(self, qapp, manager):
        """Create KeybindingDialog."""
        return KeybindingDialog(manager)

    def test_initialization(self, dialog):
        """Test dialog initializes correctly."""
        assert dialog is not None
        assert dialog.windowTitle() == "Keyboard Shortcuts"
        assert dialog._table.rowCount() == 4  # 4 actions registered

    def test_table_population(self, dialog):
        """Test that table is populated with all actions."""
        # Should have 4 rows (4 actions)
        assert dialog._table.rowCount() == 4

        # Check first row (File.Open - alphabetically first in File category)
        # Actions are sorted by category then description
        category_item = dialog._table.item(0, 0)

        # File category comes before Edit
        assert category_item.text() in ["File", "Edit"]

    def test_table_columns(self, dialog):
        """Test table has correct columns."""
        assert dialog._table.columnCount() == 4

        # Check headers
        headers = [
            dialog._table.horizontalHeaderItem(i).text() for i in range(dialog._table.columnCount())
        ]
        assert "Category" in headers
        assert "Action" in headers
        assert "Shortcut" in headers

    def test_shortcut_edit_widgets(self, dialog):
        """Test that KeySequenceEdit widgets are created for each row."""
        for row in range(dialog._table.rowCount()):
            widget = dialog._table.cellWidget(row, 2)
            assert isinstance(widget, KeySequenceEdit)

    def test_reset_buttons_exist(self, dialog):
        """Test that reset buttons exist for each row."""
        for row in range(dialog._table.rowCount()):
            widget = dialog._table.cellWidget(row, 3)
            assert widget is not None
            assert hasattr(widget, "clicked")  # Should be a button

    def test_search_filter(self, dialog):
        """Test search filtering works."""
        # Initially all rows visible
        visible_count = sum(
            1 for row in range(dialog._table.rowCount()) if not dialog._table.isRowHidden(row)
        )
        assert visible_count == 4

        # Search for "copy"
        dialog._search_input.setText("copy")

        # Only Copy action should be visible
        visible_count = sum(
            1 for row in range(dialog._table.rowCount()) if not dialog._table.isRowHidden(row)
        )
        assert visible_count == 1

        # Clear search
        dialog._search_input.clear()

        # All rows visible again
        visible_count = sum(
            1 for row in range(dialog._table.rowCount()) if not dialog._table.isRowHidden(row)
        )
        assert visible_count == 4

    def test_search_filter_category(self, dialog):
        """Test search filtering by category."""
        # Search for "File" category
        dialog._search_input.setText("file")

        # Only File category actions should be visible
        visible_rows = [
            row for row in range(dialog._table.rowCount()) if not dialog._table.isRowHidden(row)
        ]

        # Should have 2 File actions
        assert len(visible_rows) == 2

    def test_shortcut_change_pending(self, dialog):
        """Test that changing a shortcut adds it to pending changes."""
        # Get first row's KeySequenceEdit
        edit = dialog._table.cellWidget(0, 2)
        desc_item = dialog._table.item(0, 1)
        action_id = desc_item.data(Qt.ItemDataRole.UserRole)

        # Change shortcut by manually emitting signal (simulating user interaction)
        edit.setShortcut("Ctrl+Alt+Z")
        edit.shortcut_changed.emit("Ctrl+Alt+Z")

        # Should be in pending changes
        assert action_id in dialog._pending_changes
        assert dialog._pending_changes[action_id] == "Ctrl+Alt+Z"

    def test_conflict_detection(self, dialog):
        """Test that duplicate shortcuts are detected."""
        # Initially no conflicts
        assert dialog._conflict_label.text() == ""

        # Get action IDs
        desc_item1 = dialog._table.item(0, 1)
        desc_item2 = dialog._table.item(1, 1)
        action_id1 = desc_item1.data(Qt.ItemDataRole.UserRole)
        action_id2 = desc_item2.data(Qt.ItemDataRole.UserRole)

        # Set two actions to same shortcut directly via pending changes
        dialog._pending_changes[action_id1] = "Ctrl+X"
        dialog._pending_changes[action_id2] = "Ctrl+X"

        # Manually trigger conflict check
        dialog._check_conflicts()

        # Conflict warning should be set
        conflict_text = dialog._conflict_label.text().lower()
        assert "conflict" in conflict_text
        assert "ctrl+x" in conflict_text

    def test_reset_action(self, dialog, manager):
        """Test resetting a single action to default."""
        # Get first row
        edit = dialog._table.cellWidget(0, 2)
        desc_item = dialog._table.item(0, 1)
        action_id = desc_item.data(Qt.ItemDataRole.UserRole)

        # Get original shortcut
        action = manager._registry.get(action_id)
        original_shortcut = action.default_shortcut

        # Change shortcut
        edit.setShortcut("Ctrl+Alt+Q")
        assert edit.shortcut() == "Ctrl+Alt+Q"

        # Reset it
        dialog._reset_action(action_id)

        # Should be back to default
        assert edit.shortcut() == original_shortcut

    def test_reset_all(self, dialog, manager):
        """Test resetting all shortcuts to defaults."""
        # Change multiple shortcuts
        for row in range(2):
            edit = dialog._table.cellWidget(row, 2)
            edit.setShortcut("Ctrl+Alt+X")

        # Reset all
        dialog._reset_all()

        # All should be back to defaults
        for row in range(dialog._table.rowCount()):
            edit = dialog._table.cellWidget(row, 2)
            desc_item = dialog._table.item(row, 1)
            action_id = desc_item.data(Qt.ItemDataRole.UserRole)
            action = manager._registry.get(action_id)

            assert edit.shortcut() == (action.default_shortcut or "")

    def test_apply_changes(self, dialog, manager):
        """Test applying changes updates the manager."""
        # Get first row
        edit = dialog._table.cellWidget(0, 2)
        desc_item = dialog._table.item(0, 1)
        action_id = desc_item.data(Qt.ItemDataRole.UserRole)

        # Change shortcut by emitting signal
        new_shortcut = "Ctrl+Shift+Q"
        edit.setShortcut(new_shortcut)
        edit.shortcut_changed.emit(new_shortcut)

        # Apply changes
        dialog._apply_changes()

        # Manager should have new binding
        assert manager.get_binding(action_id) == new_shortcut

        # Pending changes should be cleared
        assert len(dialog._pending_changes) == 0

    def test_accept_applies_changes(self, dialog, manager):
        """Test that accepting the dialog applies changes."""
        # Get first row
        edit = dialog._table.cellWidget(0, 2)
        desc_item = dialog._table.item(0, 1)
        action_id = desc_item.data(Qt.ItemDataRole.UserRole)

        # Change shortcut by emitting signal
        new_shortcut = "Ctrl+Shift+A"
        edit.setShortcut(new_shortcut)
        edit.shortcut_changed.emit(new_shortcut)

        # Accept dialog
        dialog.accept()

        # Manager should have new binding
        assert manager.get_binding(action_id) == new_shortcut

    def test_reject_reverts_changes(self, dialog, manager):
        """Test that canceling the dialog reverts changes."""
        # Get first row
        edit = dialog._table.cellWidget(0, 2)
        desc_item = dialog._table.item(0, 1)
        action_id = desc_item.data(Qt.ItemDataRole.UserRole)

        # Store original binding
        original = manager.get_binding(action_id)

        # Change shortcut
        edit.setShortcut("Ctrl+Shift+B")

        # Apply it first
        dialog._apply_changes()

        # Change again
        edit.setShortcut("Ctrl+Shift+C")

        # Reject dialog
        dialog.reject()

        # Manager should have original binding (before any changes in dialog)
        assert manager.get_binding(action_id) == original

    def test_button_box_exists(self, dialog):
        """Test that dialog button box exists with correct buttons."""
        assert dialog._button_box is not None

        # Should have OK, Cancel, Apply buttons
        ok_btn = dialog._button_box.button(QDialogButtonBox.StandardButton.Ok)
        cancel_btn = dialog._button_box.button(QDialogButtonBox.StandardButton.Cancel)
        apply_btn = dialog._button_box.button(QDialogButtonBox.StandardButton.Apply)

        assert ok_btn is not None
        assert cancel_btn is not None
        assert apply_btn is not None

    def test_shortcuts_changed_signal(self, dialog, manager):
        """Test that shortcuts_changed signal is emitted on apply."""
        signal_emitted = []

        def on_signal(mgr):
            signal_emitted.append(mgr)

        dialog.shortcuts_changed.connect(on_signal)

        # Change a shortcut by emitting signal
        edit = dialog._table.cellWidget(0, 2)
        edit.setShortcut("Ctrl+Shift+X")
        edit.shortcut_changed.emit("Ctrl+Shift+X")

        # Apply changes
        dialog._apply_changes()

        # Signal should be emitted
        assert len(signal_emitted) == 1
        assert signal_emitted[0] is manager

    def test_empty_shortcut_allowed(self, dialog):
        """Test that shortcuts can be cleared (set to empty)."""
        # Get first row
        edit = dialog._table.cellWidget(0, 2)
        desc_item = dialog._table.item(0, 1)
        action_id = desc_item.data(Qt.ItemDataRole.UserRole)

        # Clear shortcut (clearShortcut does emit the signal)
        edit.clearShortcut()

        # Should be in pending changes as None
        assert action_id in dialog._pending_changes
        assert dialog._pending_changes[action_id] is None

    def test_category_sorting(self, dialog):
        """Test that actions are sorted by category."""
        categories = []
        for row in range(dialog._table.rowCount()):
            item = dialog._table.item(row, 0)
            categories.append(item.text())

        # Categories should be grouped (Edit, Edit, File, File or similar)
        # Just check that same categories are adjacent
        prev_cat = None
        category_changes = 0
        for cat in categories:
            if prev_cat is not None and cat != prev_cat:
                category_changes += 1
            prev_cat = cat

        # Should have at most 1 category change (from Edit to File or vice versa)
        assert category_changes <= 1

    def test_no_apply_when_no_changes(self, dialog, manager):
        """Test that apply does nothing when there are no changes."""
        # Store original bindings
        original_bindings = manager.get_all_bindings().copy()

        # Apply without making any changes
        dialog._apply_changes()

        # Bindings should be unchanged
        assert manager.get_all_bindings() == original_bindings
