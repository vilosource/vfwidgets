"""Undo/redo commands for token editing."""

from PySide6.QtGui import QUndoCommand


class SetTokenCommand(QUndoCommand):
    """Command for setting a token value (supports undo/redo)."""

    def __init__(self, document, token_name: str, new_value: str, old_value: str):
        """Initialize command.

        Args:
            document: ThemeDocument to modify
            token_name: Name of token to set
            new_value: New token value
            old_value: Old token value (for undo)
        """
        super().__init__(f"Set {token_name}")
        self._document = document
        self._token_name = token_name
        self._new_value = new_value
        self._old_value = old_value

    def redo(self):
        """Apply the command (set new value)."""
        self._document.set_token(self._token_name, self._new_value)

    def undo(self):
        """Undo the command (restore old value)."""
        self._document.set_token(self._token_name, self._old_value)

    def id(self) -> int:
        """Return command ID for merging consecutive edits."""
        # Return hash of token name so consecutive edits to same token can merge
        return hash(self._token_name) & 0x7FFFFFFF

    def mergeWith(self, other: QUndoCommand) -> bool:
        """Merge with another command if editing same token.

        Args:
            other: Other command to potentially merge with

        Returns:
            True if merged, False otherwise
        """
        if not isinstance(other, SetTokenCommand):
            return False

        if other._token_name != self._token_name:
            return False

        # Merge by updating our new_value to other's new_value
        # Keep our old_value (so undo goes back to original)
        self._new_value = other._new_value
        return True
