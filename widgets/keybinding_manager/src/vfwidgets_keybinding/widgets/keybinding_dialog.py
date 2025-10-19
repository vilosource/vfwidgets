"""Dialog for managing keyboard shortcuts.

This widget provides a complete UI for viewing and editing keyboard shortcuts
in an application. It displays actions grouped by category, allows searching,
detects conflicts, and provides reset functionality.
"""

from __future__ import annotations

import logging

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..manager import KeybindingManager
from ..registry import ActionDefinition
from .key_sequence_edit import KeySequenceEdit

logger = logging.getLogger(__name__)


class KeybindingDialog(QDialog):
    """Dialog for managing keyboard shortcuts.

    This dialog provides a complete UI for managing keyboard shortcuts:
    - Displays all actions grouped by category
    - Search/filter functionality
    - Inline editing with KeySequenceEdit
    - Conflict detection
    - Reset to defaults (per-action and all)
    - Apply/OK/Cancel buttons

    Signals:
        shortcuts_changed: Emitted when shortcuts are applied (passes manager)

    Example:
        >>> manager = KeybindingManager("~/.config/myapp/keys.json")
        >>> # ... register actions ...
        >>> dialog = KeybindingDialog(manager, parent=main_window)
        >>> if dialog.exec() == QDialog.DialogCode.Accepted:
        ...     print("User saved changes")
    """

    # Signal emitted when shortcuts are applied
    shortcuts_changed = Signal(object)  # Passes the KeybindingManager

    def __init__(
        self,
        manager: KeybindingManager,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize the keybinding dialog.

        Args:
            manager: KeybindingManager instance to manage
            parent: Optional parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Keyboard Shortcuts")
        self.resize(800, 600)

        self._manager = manager
        self._pending_changes: dict[str, str | None] = {}  # action_id -> shortcut
        self._original_bindings: dict[str, str | None] = {}  # Backup for cancel

        # Store original bindings for cancel/reset
        self._original_bindings = self._manager.get_all_bindings().copy()

        self._setup_ui()
        self._populate_table()

        logger.debug("KeybindingDialog initialized")

    def _setup_ui(self) -> None:
        """Create the dialog UI layout."""
        layout = QVBoxLayout(self)

        # Header with instructions
        header = QLabel(
            "Configure keyboard shortcuts. Click in the Shortcut column to change. "
            "Press Escape to clear a shortcut."
        )
        header.setWordWrap(True)
        layout.addWidget(header)

        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Filter actions...")
        self._search_input.textChanged.connect(self._filter_table)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self._search_input)
        layout.addLayout(search_layout)

        # Table for shortcuts
        self._table = QTableWidget()
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["Category", "Action", "Shortcut", ""])
        self._table.horizontalHeader().setStretchLastSection(False)
        self._table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )
        self._table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self._table)

        # Conflict warning label
        self._conflict_label = QLabel()
        self._conflict_label.setStyleSheet("color: red;")
        self._conflict_label.setWordWrap(True)
        self._conflict_label.setVisible(False)
        layout.addWidget(self._conflict_label)

        # Bottom buttons
        button_layout = QHBoxLayout()

        # Reset buttons on left
        self._reset_btn = QPushButton("Reset Selected")
        self._reset_btn.setToolTip("Reset the selected shortcut to its default")
        self._reset_btn.clicked.connect(self._reset_selected)
        button_layout.addWidget(self._reset_btn)

        self._reset_all_btn = QPushButton("Reset All")
        self._reset_all_btn.setToolTip("Reset all shortcuts to their defaults")
        self._reset_all_btn.clicked.connect(self._reset_all)
        button_layout.addWidget(self._reset_all_btn)

        button_layout.addStretch()

        # Standard dialog buttons on right
        self._button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Apply
        )
        self._button_box.accepted.connect(self.accept)
        self._button_box.rejected.connect(self.reject)
        self._button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(
            self._apply_changes
        )
        button_layout.addWidget(self._button_box)

        layout.addLayout(button_layout)

    def _populate_table(self) -> None:
        """Populate the table with all actions from the manager."""
        self._table.setRowCount(0)  # Clear existing rows

        # Get all actions sorted by category then description
        all_actions = self._manager._registry.get_all()
        sorted_actions = sorted(all_actions, key=lambda a: (a.category, a.description))

        # Add each action as a row
        for action in sorted_actions:
            self._add_action_row(action)

        logger.debug(f"Populated table with {len(sorted_actions)} actions")

    def _add_action_row(self, action: ActionDefinition) -> None:
        """Add a row for an action to the table.

        Args:
            action: Action definition to add
        """
        row = self._table.rowCount()
        self._table.insertRow(row)

        # Column 0: Category
        category_item = QTableWidgetItem(action.category)
        category_item.setFlags(category_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self._table.setItem(row, 0, category_item)

        # Column 1: Description
        desc_item = QTableWidgetItem(action.description)
        desc_item.setFlags(desc_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        desc_item.setData(Qt.ItemDataRole.UserRole, action.id)  # Store action ID
        self._table.setItem(row, 1, desc_item)

        # Column 2: Shortcut (KeySequenceEdit widget)
        current_shortcut = self._manager.get_binding(action.id)
        shortcut_edit = KeySequenceEdit()
        if current_shortcut:
            shortcut_edit.setShortcut(current_shortcut)
        shortcut_edit.shortcut_changed.connect(
            lambda s, aid=action.id: self._on_shortcut_changed(aid, s)
        )
        self._table.setCellWidget(row, 2, shortcut_edit)

        # Column 3: Reset button for this row
        reset_btn = QPushButton("Reset")
        reset_btn.setMaximumWidth(80)
        reset_btn.clicked.connect(lambda checked, aid=action.id: self._reset_action(aid))
        self._table.setCellWidget(row, 3, reset_btn)

    @Slot(str, str)
    def _on_shortcut_changed(self, action_id: str, new_shortcut: str) -> None:
        """Handle shortcut change from KeySequenceEdit.

        Args:
            action_id: ID of the action that changed
            new_shortcut: New shortcut string (or empty)
        """
        # Store pending change
        self._pending_changes[action_id] = new_shortcut if new_shortcut else None

        # Check for conflicts
        self._check_conflicts()

        logger.debug(f"Shortcut changed for '{action_id}': {new_shortcut or '(cleared)'}")

    def _check_conflicts(self) -> None:
        """Check for shortcut conflicts and display warning."""
        # Build map of shortcuts to action IDs (including pending changes)
        shortcut_map: dict[str, list[str]] = {}

        # Start with current bindings
        for action_id, shortcut in self._manager.get_all_bindings().items():
            # Apply pending changes
            if action_id in self._pending_changes:
                shortcut = self._pending_changes[action_id]

            if shortcut:  # Only check non-empty shortcuts
                if shortcut not in shortcut_map:
                    shortcut_map[shortcut] = []
                shortcut_map[shortcut].append(action_id)

        # Find conflicts (shortcuts with multiple actions)
        conflicts = {k: v for k, v in shortcut_map.items() if len(v) > 1}

        if conflicts:
            # Build warning message
            conflict_lines = []
            for shortcut, action_ids in conflicts.items():
                # Get action descriptions
                descriptions = []
                for aid in action_ids:
                    action = self._manager._registry.get(aid)
                    if action:
                        descriptions.append(action.description)
                conflict_lines.append(f"{shortcut}: {', '.join(descriptions)}")

            warning = "⚠ Shortcut conflicts detected:\n" + "\n".join(conflict_lines)
            self._conflict_label.setText(warning)
            self._conflict_label.setVisible(True)
            logger.warning(f"Conflicts detected: {conflicts}")
        else:
            self._conflict_label.setVisible(False)

    @Slot()
    def _filter_table(self) -> None:
        """Filter table rows based on search input."""
        search_text = self._search_input.text().lower()

        for row in range(self._table.rowCount()):
            # Get category and description
            category_item = self._table.item(row, 0)
            desc_item = self._table.item(row, 1)

            if category_item and desc_item:
                category = category_item.text().lower()
                description = desc_item.text().lower()

                # Show row if search text is in category or description
                matches = search_text in category or search_text in description
                self._table.setRowHidden(row, not matches)

    @Slot()
    def _reset_selected(self) -> None:
        """Reset the currently selected shortcut to its default."""
        current_row = self._table.currentRow()
        if current_row < 0:
            return

        desc_item = self._table.item(current_row, 1)
        if desc_item:
            action_id = desc_item.data(Qt.ItemDataRole.UserRole)
            self._reset_action(action_id)

    def _reset_action(self, action_id: str) -> None:
        """Reset a specific action to its default shortcut.

        Args:
            action_id: ID of action to reset
        """
        action = self._manager._registry.get(action_id)
        if not action:
            return

        # Find the row for this action
        for row in range(self._table.rowCount()):
            desc_item = self._table.item(row, 1)
            if desc_item and desc_item.data(Qt.ItemDataRole.UserRole) == action_id:
                # Get the KeySequenceEdit widget
                shortcut_edit = self._table.cellWidget(row, 2)
                if isinstance(shortcut_edit, KeySequenceEdit):
                    # Set to default shortcut
                    default = action.default_shortcut or ""
                    shortcut_edit.setShortcut(default)
                    # This will trigger shortcut_changed signal

                logger.debug(f"Reset '{action_id}' to default: {action.default_shortcut}")
                break

    @Slot()
    def _reset_all(self) -> None:
        """Reset all shortcuts to their defaults."""
        for row in range(self._table.rowCount()):
            desc_item = self._table.item(row, 1)
            if desc_item:
                action_id = desc_item.data(Qt.ItemDataRole.UserRole)
                action = self._manager._registry.get(action_id)
                if action:
                    shortcut_edit = self._table.cellWidget(row, 2)
                    if isinstance(shortcut_edit, KeySequenceEdit):
                        default = action.default_shortcut or ""
                        shortcut_edit.setShortcut(default)

        logger.info("Reset all shortcuts to defaults")

    @Slot()
    def _apply_changes(self) -> None:
        """Apply pending changes to the manager."""
        if not self._pending_changes:
            logger.debug("No changes to apply")
            return

        # Apply all pending changes
        for action_id, shortcut in self._pending_changes.items():
            self._manager.set_binding(action_id, shortcut)

        # Clear pending changes
        self._pending_changes.clear()

        # Update original bindings (so cancel doesn't revert)
        self._original_bindings = self._manager.get_all_bindings().copy()

        # Emit signal
        self.shortcuts_changed.emit(self._manager)

        logger.info(f"Applied {len(self._pending_changes)} shortcut changes")

    def accept(self) -> None:
        """Handle OK button - apply changes and close."""
        self._apply_changes()
        super().accept()

    def reject(self) -> None:
        """Handle Cancel button - revert changes and close."""
        # Revert all changes
        for action_id, original_shortcut in self._original_bindings.items():
            self._manager.set_binding(action_id, original_shortcut)

        logger.debug("Reverted all changes")
        super().reject()
