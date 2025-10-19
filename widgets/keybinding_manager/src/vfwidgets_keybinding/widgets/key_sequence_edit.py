"""Key sequence input widget for capturing keyboard shortcuts.

This widget provides a specialized QLineEdit for capturing keyboard shortcuts
in a user-friendly way. It handles key press events, formats shortcuts properly,
and provides validation.
"""

from __future__ import annotations

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent, QKeySequence
from PySide6.QtWidgets import QLineEdit

logger = logging.getLogger(__name__)


class KeySequenceEdit(QLineEdit):
    """A specialized line edit widget for capturing keyboard shortcuts.

    This widget captures key press events and displays them as formatted
    shortcut strings (e.g., "Ctrl+Shift+K"). It handles modifiers properly,
    ignores inappropriate keys, and provides a clear button.

    Features:
    - Captures all standard modifiers (Ctrl, Shift, Alt, Meta)
    - Formats shortcuts using Qt's standard format
    - Validates shortcuts (non-empty, valid QKeySequence)
    - Emits signal when shortcut changes
    - Shows clear button when not empty
    - Can be set to read-only for display purposes

    Signals:
        shortcut_changed: Emitted when the shortcut is changed, passes new shortcut string

    Example:
        >>> edit = KeySequenceEdit()
        >>> edit.setShortcut("Ctrl+Shift+K")
        >>> edit.shortcut_changed.connect(lambda s: print(f"New shortcut: {s}"))
        >>> shortcut = edit.shortcut()  # Returns "Ctrl+Shift+K"
    """

    # Signal emitted when shortcut changes
    shortcut_changed = Signal(str)  # Emits the new shortcut string

    # Keys to ignore (they don't make sense as shortcuts)
    IGNORED_KEYS = {
        Qt.Key.Key_unknown,
        Qt.Key.Key_Tab,
        Qt.Key.Key_Backtab,
        Qt.Key.Key_CapsLock,
        Qt.Key.Key_NumLock,
        Qt.Key.Key_ScrollLock,
        Qt.Key.Key_Shift,
        Qt.Key.Key_Control,
        Qt.Key.Key_Meta,
        Qt.Key.Key_Alt,
        Qt.Key.Key_AltGr,
        Qt.Key.Key_Super_L,
        Qt.Key.Key_Super_R,
        Qt.Key.Key_Menu,
        Qt.Key.Key_Hyper_L,
        Qt.Key.Key_Hyper_R,
    }

    def __init__(self, parent: object | None = None) -> None:
        """Initialize the key sequence edit widget.

        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)

        # Configure widget
        self.setPlaceholderText("Press shortcut keys...")
        self.setClearButtonEnabled(True)  # Show clear button when not empty
        self.setReadOnly(False)  # Can be changed to read-only later

        # Track current shortcut
        self._current_shortcut: str = ""

        # Connect clear button to reset
        self.textChanged.connect(self._on_text_changed)

        logger.debug("KeySequenceEdit initialized")

    def shortcut(self) -> str:
        """Get the current shortcut string.

        Returns:
            Current shortcut string (e.g., "Ctrl+Shift+K"), or empty string if none

        Example:
            >>> edit = KeySequenceEdit()
            >>> edit.setShortcut("Ctrl+S")
            >>> print(edit.shortcut())  # "Ctrl+S"
        """
        return self._current_shortcut

    def setShortcut(self, shortcut: str) -> None:
        """Set the shortcut string.

        Args:
            shortcut: Shortcut string to set (e.g., "Ctrl+Shift+K"), or empty to clear

        Example:
            >>> edit = KeySequenceEdit()
            >>> edit.setShortcut("Ctrl+Alt+Delete")
        """
        # Validate and format the shortcut
        if shortcut:
            key_sequence = QKeySequence(shortcut)
            if not key_sequence.isEmpty():
                formatted = key_sequence.toString(QKeySequence.SequenceFormat.NativeText)
                self._current_shortcut = formatted
                self.setText(formatted)
                logger.debug(f"Set shortcut to: {formatted}")
            else:
                logger.warning(f"Invalid shortcut string: {shortcut}")
                self._current_shortcut = ""
                self.clear()
        else:
            self._current_shortcut = ""
            self.clear()

    def clearShortcut(self) -> None:
        """Clear the current shortcut.

        Example:
            >>> edit = KeySequenceEdit()
            >>> edit.setShortcut("Ctrl+S")
            >>> edit.clearShortcut()  # Now empty
        """
        self._current_shortcut = ""
        self.clear()
        self.shortcut_changed.emit("")
        logger.debug("Shortcut cleared")

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle key press events to capture shortcuts.

        This is the core of the widget - it intercepts key presses and
        converts them to shortcut strings.

        Args:
            event: Key press event from Qt
        """
        # Don't capture if read-only
        if self.isReadOnly():
            super().keyPressEvent(event)
            return

        key = event.key()

        # Ignore inappropriate keys
        if key in self.IGNORED_KEYS:
            event.ignore()
            return

        # Handle Escape to clear
        if key == Qt.Key.Key_Escape:
            self.clearShortcut()
            event.accept()
            return

        # Build the key combination
        modifiers = event.modifiers()

        # Convert to QKeySequence format (combines modifiers and key)
        key_combination = int(modifiers.value) | key

        # Create QKeySequence from the combination
        key_sequence = QKeySequence(key_combination)

        # Format as string
        shortcut_str = key_sequence.toString(QKeySequence.SequenceFormat.NativeText)

        # Update widget
        if shortcut_str:
            self._current_shortcut = shortcut_str
            self.setText(shortcut_str)
            self.shortcut_changed.emit(shortcut_str)
            logger.debug(f"Captured shortcut: {shortcut_str}")
        else:
            logger.debug(f"Ignored key: {key}")

        event.accept()

    def _on_text_changed(self, text: str) -> None:
        """Handle text changes (e.g., from clear button).

        Args:
            text: New text content
        """
        # If text was cleared (e.g., via clear button), reset shortcut
        if not text and self._current_shortcut:
            self._current_shortcut = ""
            self.shortcut_changed.emit("")
            logger.debug("Shortcut cleared via text change")

    def isValid(self) -> bool:
        """Check if the current shortcut is valid.

        Returns:
            True if shortcut is non-empty and forms a valid QKeySequence

        Example:
            >>> edit = KeySequenceEdit()
            >>> edit.setShortcut("Ctrl+S")
            >>> print(edit.isValid())  # True
            >>> edit.clearShortcut()
            >>> print(edit.isValid())  # False
        """
        if not self._current_shortcut:
            return False

        key_sequence = QKeySequence(self._current_shortcut)
        return not key_sequence.isEmpty()
