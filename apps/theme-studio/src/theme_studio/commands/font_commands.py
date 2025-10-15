"""Font-related undo/redo commands for Theme Studio."""

from PySide6.QtGui import QUndoCommand


class SetFontCommand(QUndoCommand):
    """Command to set a font token value (supports undo/redo).

    This command updates a font token in the theme document and supports
    undo/redo operations through Qt's undo stack.

    Args:
        document: ThemeDocument to modify
        token_path: Font token path (e.g., "terminal.fontSize")
        new_value: New font value (list[str], int, float, or str)
        old_value: Previous font value for undo
    """

    def __init__(self, document, token_path: str, new_value, old_value):
        """Initialize set font command.

        Args:
            document: ThemeDocument instance
            token_path: Font token path
            new_value: New value to set
            old_value: Old value for undo
        """
        # Format command text for undo stack display
        super().__init__(f"Set {token_path}")
        self._document = document
        self._token_path = token_path
        self._new_value = new_value
        self._old_value = old_value

    def redo(self):
        """Apply font change."""
        self._document.set_font(self._token_path, self._new_value)

    def undo(self):
        """Revert font change."""
        if self._old_value is not None:
            self._document.set_font(self._token_path, self._old_value)
        else:
            # If old value was None, remove the token
            self._document.remove_font(self._token_path)
