"""Central manager for keyboard shortcuts.

The KeybindingManager is the main API for integrating keyboard shortcuts
into your application. It orchestrates the ActionRegistry and KeybindingStorage
to provide a complete keybinding solution.
"""

import logging
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QWidget

from .registry import ActionDefinition, ActionRegistry
from .storage import KeybindingStorage

logger = logging.getLogger(__name__)


class KeybindingManager:
    """Central manager for keyboard shortcuts.

    The KeybindingManager provides a high-level API for:
    - Registering actions
    - Loading/saving keybindings
    - Applying shortcuts to widgets
    - Querying bindings

    This is the main entry point for integrating keybinding management
    into your application.

    Example:
        >>> manager = KeybindingManager(storage_path="~/.config/myapp/keys.json")
        >>>
        >>> # Register actions
        >>> manager.register_action(ActionDefinition(
        ...     id="file.save",
        ...     description="Save File",
        ...     default_shortcut="Ctrl+S",
        ...     category="File"
        ... ))
        >>>
        >>> # Apply shortcuts to widget
        >>> manager.apply_shortcuts(main_window)
    """

    def __init__(self, storage_path: Optional[str] = None, auto_save: bool = True):
        """Initialize keybinding manager.

        Args:
            storage_path: Path to JSON file for persistent storage.
                        If None, keybindings are not persisted.
            auto_save: If True, automatically save when bindings change

        Example:
            >>> manager = KeybindingManager("~/.config/myapp/keybindings.json")
        """
        self._registry = ActionRegistry()
        self._storage = KeybindingStorage(storage_path)
        self._auto_save = auto_save
        self._current_bindings: dict[str, Optional[str]] = {}
        self._applied_actions: dict[str, QAction] = {}  # Track created QActions

        logger.info(f"KeybindingManager initialized (auto_save={auto_save})")

    def register_action(self, action: ActionDefinition) -> None:
        """Register a new action.

        Args:
            action: Action definition to register

        Raises:
            ValueError: If action ID is already registered

        Example:
            >>> manager.register_action(ActionDefinition(
            ...     id="file.save",
            ...     description="Save File",
            ...     default_shortcut="Ctrl+S",
            ...     category="File"
            ... ))
        """
        self._registry.register(action)

        # Add default binding to current bindings if not already set
        if action.id not in self._current_bindings:
            self._current_bindings[action.id] = action.default_shortcut

        logger.debug(f"Registered action: {action.id}")

    def register_actions(self, actions: list[ActionDefinition]) -> None:
        """Register multiple actions at once.

        Args:
            actions: List of action definitions to register

        Example:
            >>> manager.register_actions([
            ...     ActionDefinition(id="file.save", description="Save", default_shortcut="Ctrl+S"),
            ...     ActionDefinition(id="file.open", description="Open", default_shortcut="Ctrl+O"),
            ... ])
        """
        for action in actions:
            self.register_action(action)

        logger.info(f"Registered {len(actions)} actions")

    def load_bindings(self) -> None:
        """Load keybindings from storage.

        Merges stored user customizations with registered action defaults.

        Example:
            >>> manager.load_bindings()  # Load from storage file
        """
        # Get default bindings from registry
        defaults = {action.id: action.default_shortcut for action in self._registry.get_all()}

        # Load user overrides
        overrides = self._storage.load()

        # Merge (user overrides take precedence)
        self._current_bindings = self._storage.merge(defaults, overrides)

        logger.info(f"Loaded {len(self._current_bindings)} keybindings")

    def save_bindings(self) -> bool:
        """Save current keybindings to storage.

        Returns:
            True if save succeeded, False otherwise

        Example:
            >>> manager.save_bindings()
        """
        success = self._storage.save(self._current_bindings)

        if success:
            logger.info("Keybindings saved successfully")
        else:
            logger.error("Failed to save keybindings")

        return success

    def set_binding(self, action_id: str, shortcut: Optional[str]) -> bool:
        """Change the keyboard shortcut for an action.

        Args:
            action_id: ID of action to bind
            shortcut: New keyboard shortcut (e.g., "Ctrl+S"), or None to unbind

        Returns:
            True if binding was changed, False if action doesn't exist

        Example:
            >>> manager.set_binding("file.save", "Ctrl+Alt+S")  # Change binding
            >>> manager.set_binding("file.close", None)  # Unbind action
        """
        # Check if action exists
        action = self._registry.get(action_id)
        if not action:
            logger.warning(f"Cannot set binding: action '{action_id}' not registered")
            return False

        # Update binding
        old_shortcut = self._current_bindings.get(action_id)
        self._current_bindings[action_id] = shortcut

        # Update existing QAction if it exists
        if action_id in self._applied_actions:
            qaction = self._applied_actions[action_id]
            if shortcut:
                qaction.setShortcut(QKeySequence(shortcut))
            else:
                qaction.setShortcut(QKeySequence())

        logger.info(f"Changed binding for '{action_id}': {old_shortcut} → {shortcut}")

        # Auto-save if enabled
        if self._auto_save:
            self.save_bindings()

        return True

    def get_binding(self, action_id: str) -> Optional[str]:
        """Get current keyboard shortcut for an action.

        Args:
            action_id: ID of action to query

        Returns:
            Current shortcut string, or None if unbound/not found

        Example:
            >>> shortcut = manager.get_binding("file.save")
            >>> print(f"Save is bound to: {shortcut}")
        """
        return self._current_bindings.get(action_id)

    def apply_shortcuts(
        self, widget: QWidget, action_ids: Optional[list[str]] = None
    ) -> dict[str, QAction]:
        """Apply keyboard shortcuts to a widget.

        Creates QAction objects for each action and adds them to the widget.
        The shortcuts will work globally within the widget's context.

        Args:
            widget: Widget to apply shortcuts to (usually main window)
            action_ids: Specific action IDs to apply. If None, applies all registered actions.

        Returns:
            Dictionary mapping action IDs to created QAction objects

        Example:
            >>> actions = manager.apply_shortcuts(main_window)
            >>> save_action = actions.get("file.save")
            >>> if save_action:
            ...     save_action.triggered.connect(save_file)
        """
        # Determine which actions to apply
        if action_ids is None:
            actions_to_apply = self._registry.get_all()
        else:
            actions_to_apply = []
            for action_id in action_ids:
                action = self._registry.get(action_id)
                if action is not None:
                    actions_to_apply.append(action)

        created_actions = {}

        for action_def in actions_to_apply:
            # Create QAction
            qaction = QAction(action_def.description, widget)

            # Set shortcut if bound
            shortcut = self._current_bindings.get(action_def.id)
            if shortcut:
                qaction.setShortcut(QKeySequence(shortcut))
                # Use WindowShortcut context to work across all child widgets
                qaction.setShortcutContext(Qt.ShortcutContext.WindowShortcut)

            # Connect callback if provided
            if action_def.callback:
                qaction.triggered.connect(action_def.callback)

            # Add to widget
            widget.addAction(qaction)

            # Track created action
            self._applied_actions[action_def.id] = qaction
            created_actions[action_def.id] = qaction

            logger.debug(f"Applied shortcut for '{action_def.id}': {shortcut}")

        logger.info(f"Applied {len(created_actions)} shortcuts to {widget.__class__.__name__}")
        return created_actions

    def get_all_bindings(self) -> dict[str, Optional[str]]:
        """Get all current keybindings.

        Returns:
            Dictionary mapping action IDs to shortcuts

        Example:
            >>> bindings = manager.get_all_bindings()
            >>> for action_id, shortcut in bindings.items():
            ...     print(f"{action_id}: {shortcut}")
        """
        return self._current_bindings.copy()

    def reset_to_defaults(self) -> None:
        """Reset all keybindings to application defaults.

        This will:
        1. Clear all user customizations
        2. Restore default shortcuts from ActionRegistry
        3. Save to storage (if auto_save enabled)
        4. Update applied QActions

        Example:
            >>> manager.reset_to_defaults()  # Restore all defaults
        """
        # Delete stored customizations
        self._storage.reset()

        # Reload defaults
        self.load_bindings()

        # Update all applied QActions
        for action_id, qaction in self._applied_actions.items():
            shortcut = self._current_bindings.get(action_id)
            if shortcut:
                qaction.setShortcut(QKeySequence(shortcut))
            else:
                qaction.setShortcut(QKeySequence())

        logger.info("Reset all keybindings to defaults")

        # Auto-save if enabled
        if self._auto_save:
            self.save_bindings()

    def get_actions_by_category(self, category: str) -> list[ActionDefinition]:
        """Get all actions in a specific category.

        Args:
            category: Category name to filter by

        Returns:
            List of action definitions in the category

        Example:
            >>> file_actions = manager.get_actions_by_category("File")
            >>> for action in file_actions:
            ...     print(f"{action.description}: {manager.get_binding(action.id)}")
        """
        return self._registry.get_by_category(category)

    def get_categories(self) -> list[str]:
        """Get all action categories.

        Returns:
            Sorted list of unique category names

        Example:
            >>> categories = manager.get_categories()
            >>> print(", ".join(categories))
        """
        return self._registry.get_categories()
