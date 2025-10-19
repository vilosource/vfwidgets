"""Keyboard shortcuts preferences tab for ViloxTerm.

Provides inline editing of keyboard shortcuts directly in the preferences tab.
"""

import logging
from typing import Optional

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
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

from vfwidgets_keybinding import KeybindingManager
from vfwidgets_keybinding.widgets import KeySequenceEdit
from vfwidgets_theme import ThemedQWidget

logger = logging.getLogger(__name__)


class KeyboardShortcutsTab(ThemedQWidget):
    """Tab for managing keyboard shortcuts with inline editing.

    This tab provides inline editing of keyboard shortcuts directly in the table.
    Users can click on a shortcut cell to edit it, and changes are applied when
    the user clicks Apply in the preferences dialog.

    Features:
    - Inline editing with KeySequenceEdit widgets
    - Real-time conflict detection
    - Reset buttons (per-action and reset-all)
    - Search/filter functionality
    - Automatic validation

    Signals:
        shortcuts_changed: Emitted when shortcuts are modified
    """

    # Signal emitted when shortcuts are changed
    shortcuts_changed = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize keyboard shortcuts tab.

        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)
        self._keybinding_manager: Optional[KeybindingManager] = None
        self._pending_changes: dict[str, Optional[str]] = {}  # action_id -> shortcut
        self._original_bindings: dict[str, Optional[str]] = {}  # For cancel/revert
        self._setup_ui()
        logger.debug("KeyboardShortcutsTab initialized")

    def _setup_ui(self) -> None:
        """Set up the tab UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Header with description
        header = QLabel(
            "Configure keyboard shortcuts by clicking in the Shortcut column.\n"
            "Press Escape to clear a shortcut. Changes apply when you click Apply or OK."
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

        # Reset All button on right
        self._reset_all_btn = QPushButton("Reset All to Defaults")
        self._reset_all_btn.clicked.connect(self._reset_all)
        self._reset_all_btn.setEnabled(False)
        search_layout.addWidget(self._reset_all_btn)

        layout.addLayout(search_layout)

        # Table with inline editing
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

    def set_keybinding_manager(self, manager: KeybindingManager) -> None:
        """Set the keybinding manager and populate the table.

        Args:
            manager: KeybindingManager instance to use
        """
        self._keybinding_manager = manager
        self._reset_all_btn.setEnabled(True)

        # Store original bindings for cancel/revert
        self._original_bindings = self._keybinding_manager.get_all_bindings().copy()

        self._populate_table()
        logger.debug("KeybindingManager set in KeyboardShortcutsTab")

    def _populate_table(self) -> None:
        """Populate the table with all actions and inline editors."""
        if not self._keybinding_manager:
            return

        self._table.setRowCount(0)

        # Get all actions sorted by category then description
        all_actions = self._keybinding_manager._registry.get_all()
        sorted_actions = sorted(all_actions, key=lambda a: (a.category, a.description))

        # Add each action as a row
        for action in sorted_actions:
            self._add_action_row(action)

        logger.debug(f"Populated shortcuts table with {len(sorted_actions)} actions")

    def _add_action_row(self, action) -> None:
        """Add a row for an action with inline editing.

        Args:
            action: ActionDefinition to add
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

        # Column 2: Shortcut (KeySequenceEdit widget for inline editing)
        current_shortcut = self._keybinding_manager.get_binding(action.id)
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
        for action_id, shortcut in self._keybinding_manager.get_all_bindings().items():
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
                    action = self._keybinding_manager._registry.get(aid)
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

    def _reset_action(self, action_id: str) -> None:
        """Reset a specific action to its default shortcut.

        Args:
            action_id: ID of action to reset
        """
        action = self._keybinding_manager._registry.get(action_id)
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
                action = self._keybinding_manager._registry.get(action_id)
                if action:
                    shortcut_edit = self._table.cellWidget(row, 2)
                    if isinstance(shortcut_edit, KeySequenceEdit):
                        default = action.default_shortcut or ""
                        shortcut_edit.setShortcut(default)

        logger.info("Reset all shortcuts to defaults")

    def load_preferences(self) -> None:
        """Load preferences (called by parent dialog).

        For keyboard shortcuts, this refreshes the table and clears pending changes.
        """
        if self._keybinding_manager:
            # Store new original bindings
            self._original_bindings = self._keybinding_manager.get_all_bindings().copy()
            # Clear pending changes
            self._pending_changes.clear()
            # Refresh table
            self._populate_table()

    def save_preferences(self) -> None:
        """Save preferences (called by parent dialog).

        This applies all pending changes to the KeybindingManager.
        """
        if not self._pending_changes:
            logger.debug("No keyboard shortcut changes to save")
            return

        # Apply all pending changes
        for action_id, shortcut in self._pending_changes.items():
            self._keybinding_manager.set_binding(action_id, shortcut)

        logger.info(f"Saved {len(self._pending_changes)} keyboard shortcut changes")

        # Clear pending changes (they're now saved)
        self._pending_changes.clear()

        # Update original bindings
        self._original_bindings = self._keybinding_manager.get_all_bindings().copy()

        # Emit signal
        self.shortcuts_changed.emit()

    def cancel_changes(self) -> None:
        """Cancel all pending changes and revert to original bindings.

        This is called when the user clicks Cancel in the preferences dialog.
        """
        if not self._pending_changes:
            return

        # Revert all changes in the manager
        for action_id, original_shortcut in self._original_bindings.items():
            current = self._keybinding_manager.get_binding(action_id)
            if current != original_shortcut:
                self._keybinding_manager.set_binding(action_id, original_shortcut)

        logger.debug("Cancelled keyboard shortcut changes")

        # Clear pending changes
        self._pending_changes.clear()

        # Refresh table to show original values
        self._populate_table()
