"""Keyboard shortcut constants for VS Code compatibility.

This module defines all keyboard shortcuts that match VS Code's defaults.
Users can customize these through the ViloCodeWindow API.
"""

from dataclasses import dataclass


@dataclass
class ShortcutDefinition:
    """Definition of a keyboard shortcut.

    Attributes:
        key_sequence: Qt key sequence string (e.g., "Ctrl+B")
        description: Human-readable description
        category: Shortcut category (view, file, edit, etc.)
    """

    key_sequence: str
    description: str
    category: str = "general"


class DefaultShortcuts:
    """Default VS Code-compatible keyboard shortcuts.

    These shortcuts match VS Code's default keybindings where possible.
    Platform-specific variations (Cmd vs Ctrl) are handled automatically.
    """

    # View shortcuts
    TOGGLE_SIDEBAR = ShortcutDefinition(
        key_sequence="Ctrl+B",
        description="Toggle sidebar visibility",
        category="view",
    )

    TOGGLE_AUXILIARY_BAR = ShortcutDefinition(
        key_sequence="Ctrl+Alt+B",
        description="Toggle auxiliary bar visibility",
        category="view",
    )

    TOGGLE_STATUS_BAR = ShortcutDefinition(
        key_sequence="Ctrl+Shift+S",
        description="Toggle status bar visibility",
        category="view",
    )

    # Window shortcuts
    CLOSE_WINDOW = ShortcutDefinition(
        key_sequence="Ctrl+W",
        description="Close window",
        category="window",
    )

    MINIMIZE_WINDOW = ShortcutDefinition(
        key_sequence="Ctrl+M",
        description="Minimize window",
        category="window",
    )

    MAXIMIZE_WINDOW = ShortcutDefinition(
        key_sequence="F11",
        description="Toggle maximize window",
        category="window",
    )

    # Panel shortcuts
    FOCUS_ACTIVITY_BAR = ShortcutDefinition(
        key_sequence="Ctrl+Alt+A",
        description="Focus activity bar",
        category="panel",
    )

    FOCUS_SIDEBAR = ShortcutDefinition(
        key_sequence="Ctrl+0",
        description="Focus sidebar",
        category="panel",
    )

    FOCUS_MAIN_PANE = ShortcutDefinition(
        key_sequence="Ctrl+1",
        description="Focus main pane",
        category="panel",
    )

    @classmethod
    def get_all_shortcuts(cls) -> dict[str, ShortcutDefinition]:
        """Get all default shortcuts as a dictionary.

        Returns:
            Dictionary mapping action name to ShortcutDefinition
        """
        shortcuts = {}
        for name in dir(cls):
            if name.isupper() and not name.startswith("_"):
                attr = getattr(cls, name)
                if isinstance(attr, ShortcutDefinition):
                    shortcuts[name] = attr
        return shortcuts

    @classmethod
    def get_shortcuts_by_category(cls, category: str) -> dict[str, ShortcutDefinition]:
        """Get shortcuts filtered by category.

        Args:
            category: Category name (view, window, panel, etc.)

        Returns:
            Dictionary of shortcuts in the specified category
        """
        all_shortcuts = cls.get_all_shortcuts()
        return {
            name: shortcut
            for name, shortcut in all_shortcuts.items()
            if shortcut.category == category
        }
