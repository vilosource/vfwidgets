"""Action registry for keyboard shortcuts.

Provides ActionDefinition and ActionRegistry for managing application actions
that can be bound to keyboard shortcuts.
"""

import logging
from dataclasses import dataclass
from typing import Callable, Optional

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ActionDefinition:
    """Definition of an action that can be bound to keyboard shortcuts.

    An action represents a command that can be triggered by the user,
    either through keyboard shortcuts, menus, or buttons.

    Attributes:
        id: Unique identifier for the action (e.g., "file.save", "edit.copy")
        description: Human-readable description shown in UI
        default_shortcut: Default keyboard shortcut (e.g., "Ctrl+S")
        category: Category for grouping actions (e.g., "File", "Edit")
        callback: Optional function to execute when triggered

    Example:
        >>> save_action = ActionDefinition(
        ...     id="file.save",
        ...     description="Save File",
        ...     default_shortcut="Ctrl+S",
        ...     category="File"
        ... )
    """

    id: str
    description: str
    default_shortcut: Optional[str] = None
    category: Optional[str] = None
    callback: Optional[Callable[[], None]] = None

    def __post_init__(self) -> None:
        """Validate action definition after initialization."""
        if not self.id:
            raise ValueError("Action ID cannot be empty")
        if not self.description:
            raise ValueError("Action description cannot be empty")
        if "." not in self.id:
            raise ValueError(
                f"Action ID must be dot-separated (e.g., 'category.action'), got: '{self.id}'"
            )


class ActionRegistry:
    """Registry for managing application actions.

    The ActionRegistry maintains a central database of all available actions
    in the application. It supports registering, unregistering, querying, and
    grouping actions by category.

    This follows the Command Pattern, decoupling action definitions from
    their keybindings.

    Example:
        >>> registry = ActionRegistry()
        >>> registry.register(ActionDefinition(
        ...     id="file.save",
        ...     description="Save File",
        ...     default_shortcut="Ctrl+S",
        ...     category="File"
        ... ))
        >>> action = registry.get("file.save")
        >>> print(action.description)
        Save File
    """

    def __init__(self) -> None:
        """Initialize empty action registry."""
        self._actions: dict[str, ActionDefinition] = {}
        logger.info("ActionRegistry initialized")

    def register(self, action: ActionDefinition) -> None:
        """Register a new action.

        Args:
            action: Action definition to register

        Raises:
            ValueError: If action ID is already registered

        Example:
            >>> registry.register(ActionDefinition(
            ...     id="edit.copy",
            ...     description="Copy",
            ...     default_shortcut="Ctrl+C"
            ... ))
        """
        if action.id in self._actions:
            raise ValueError(
                f"Action '{action.id}' is already registered. "
                f"Use unregister() first if you want to replace it."
            )

        self._actions[action.id] = action
        logger.debug(f"Registered action: {action.id}")

    def unregister(self, action_id: str) -> None:
        """Unregister an action.

        Args:
            action_id: ID of action to remove

        Raises:
            KeyError: If action ID is not registered

        Example:
            >>> registry.unregister("edit.copy")
        """
        if action_id not in self._actions:
            raise KeyError(
                f"Action '{action_id}' is not registered. "
                f"Available actions: {', '.join(self._actions.keys())}"
            )

        del self._actions[action_id]
        logger.debug(f"Unregistered action: {action_id}")

    def get(self, action_id: str) -> Optional[ActionDefinition]:
        """Get action definition by ID.

        Args:
            action_id: ID of action to retrieve

        Returns:
            ActionDefinition if found, None otherwise

        Example:
            >>> action = registry.get("file.save")
            >>> if action:
            ...     print(action.description)
        """
        return self._actions.get(action_id)

    def get_all(self) -> list[ActionDefinition]:
        """Get all registered actions.

        Returns:
            List of all action definitions

        Example:
            >>> actions = registry.get_all()
            >>> print(f"Total actions: {len(actions)}")
        """
        return list(self._actions.values())

    def get_by_category(self, category: str) -> list[ActionDefinition]:
        """Get all actions in a specific category.

        Args:
            category: Category name to filter by

        Returns:
            List of actions in the specified category

        Example:
            >>> file_actions = registry.get_by_category("File")
            >>> for action in file_actions:
            ...     print(action.description)
        """
        return [action for action in self._actions.values() if action.category == category]

    def get_categories(self) -> list[str]:
        """Get all unique categories.

        Returns:
            Sorted list of category names

        Example:
            >>> categories = registry.get_categories()
            >>> print(", ".join(categories))
            Edit, File, View
        """
        categories = {
            action.category for action in self._actions.values() if action.category is not None
        }
        return sorted(categories)

    def clear(self) -> None:
        """Remove all registered actions.

        Warning:
            This will clear ALL actions. Use with caution.

        Example:
            >>> registry.clear()
            >>> assert len(registry.get_all()) == 0
        """
        self._actions.clear()
        logger.info("Cleared all actions from registry")
