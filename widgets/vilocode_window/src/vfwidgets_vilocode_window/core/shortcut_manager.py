"""Shortcut manager for handling keyboard shortcuts.

This module provides a centralized manager for registering, activating,
and customizing keyboard shortcuts.
"""

from typing import Callable, Optional

from PySide6.QtCore import QObject, Qt, Signal, Slot
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QWidget

from .shortcuts import DefaultShortcuts, ShortcutDefinition


class ShortcutManager(QObject):
    """Manager for keyboard shortcuts.

    Handles registration, activation, and customization of shortcuts.
    Emits signals when shortcuts are triggered.

    Signals:
        shortcut_triggered: Emitted when a shortcut is activated (action_name)
    """

    shortcut_triggered = Signal(str)  # action_name

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the shortcut manager.

        Args:
            parent: Parent widget that shortcuts will be attached to
        """
        super().__init__(parent)
        self._parent_widget = parent
        self._shortcuts: dict[str, QShortcut] = {}
        self._callbacks: dict[str, Callable[[], None]] = {}
        self._definitions: dict[str, ShortcutDefinition] = {}

    def register_shortcut(
        self,
        action_name: str,
        shortcut_def: ShortcutDefinition,
        callback: Optional[Callable[[], None]] = None,
    ) -> None:
        """Register a keyboard shortcut.

        Args:
            action_name: Unique action identifier (e.g., "TOGGLE_SIDEBAR")
            shortcut_def: Shortcut definition with key sequence and description
            callback: Optional callback function to execute when triggered
        """
        # Remove existing shortcut if any
        if action_name in self._shortcuts:
            self.unregister_shortcut(action_name)

        # Create Qt shortcut
        shortcut = QShortcut(QKeySequence(shortcut_def.key_sequence), self._parent_widget)
        shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)

        # Connect to internal handler
        shortcut.activated.connect(lambda: self._on_shortcut_activated(action_name))

        # Store shortcut and definition
        self._shortcuts[action_name] = shortcut
        self._definitions[action_name] = shortcut_def

        # Store callback if provided
        if callback:
            self._callbacks[action_name] = callback

    def unregister_shortcut(self, action_name: str) -> None:
        """Unregister a keyboard shortcut.

        Args:
            action_name: Action identifier to unregister
        """
        if action_name in self._shortcuts:
            shortcut = self._shortcuts[action_name]
            shortcut.setEnabled(False)
            shortcut.deleteLater()
            del self._shortcuts[action_name]

        if action_name in self._callbacks:
            del self._callbacks[action_name]

        if action_name in self._definitions:
            del self._definitions[action_name]

    def set_shortcut_enabled(self, action_name: str, enabled: bool) -> None:
        """Enable or disable a shortcut.

        Args:
            action_name: Action identifier
            enabled: True to enable, False to disable
        """
        if action_name in self._shortcuts:
            self._shortcuts[action_name].setEnabled(enabled)

    def update_shortcut_key(self, action_name: str, key_sequence: str) -> None:
        """Update the key sequence for a shortcut.

        Args:
            action_name: Action identifier
            key_sequence: New key sequence (e.g., "Ctrl+Shift+B")
        """
        if action_name in self._shortcuts:
            self._shortcuts[action_name].setKey(QKeySequence(key_sequence))
            # Update definition
            if action_name in self._definitions:
                self._definitions[action_name].key_sequence = key_sequence

    def register_callback(self, action_name: str, callback: Callable[[], None]) -> None:
        """Register or update a callback for an action.

        Args:
            action_name: Action identifier
            callback: Callback function to execute
        """
        self._callbacks[action_name] = callback

    def unregister_callback(self, action_name: str) -> None:
        """Unregister a callback for an action.

        Args:
            action_name: Action identifier
        """
        if action_name in self._callbacks:
            del self._callbacks[action_name]

    def get_shortcut_definition(self, action_name: str) -> Optional[ShortcutDefinition]:
        """Get the definition for a shortcut.

        Args:
            action_name: Action identifier

        Returns:
            ShortcutDefinition if found, None otherwise
        """
        return self._definitions.get(action_name)

    def get_all_shortcuts(self) -> dict[str, ShortcutDefinition]:
        """Get all registered shortcut definitions.

        Returns:
            Dictionary mapping action names to definitions
        """
        return self._definitions.copy()

    def load_default_shortcuts(self) -> None:
        """Load all default VS Code-compatible shortcuts.

        This registers all shortcuts from DefaultShortcuts class.
        """
        for action_name, shortcut_def in DefaultShortcuts.get_all_shortcuts().items():
            self.register_shortcut(action_name, shortcut_def)

    def clear_all_shortcuts(self) -> None:
        """Clear all registered shortcuts."""
        action_names = list(self._shortcuts.keys())
        for action_name in action_names:
            self.unregister_shortcut(action_name)

    @Slot()
    def _on_shortcut_activated(self, action_name: str) -> None:
        """Handle shortcut activation.

        Args:
            action_name: Action identifier that was triggered
        """
        # Emit signal
        self.shortcut_triggered.emit(action_name)

        # Execute callback if registered
        if action_name in self._callbacks:
            self._callbacks[action_name]()
