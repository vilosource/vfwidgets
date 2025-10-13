"""Undo/redo commands for theme metadata editing."""

from PySide6.QtGui import QUndoCommand


class SetMetadataCommand(QUndoCommand):
    """Command for setting a metadata field value (supports undo/redo)."""

    def __init__(self, document, field_name: str, new_value: str, old_value: str):
        """Initialize command.

        Args:
            document: ThemeDocument to modify
            field_name: Name of metadata field to set (name, version, type, author, description)
            new_value: New field value
            old_value: Old field value (for undo)
        """
        super().__init__(f"Set {field_name}")
        self._document = document
        self._field_name = field_name
        self._new_value = new_value
        self._old_value = old_value

    def redo(self):
        """Apply the command (set new value)."""
        # Map field name to appropriate document method
        if self._field_name == "name":
            self._document.set_name(self._new_value)
        elif self._field_name == "version":
            self._document.set_version(self._new_value)
        elif self._field_name == "type":
            self._document.set_type(self._new_value)
        elif self._field_name in ("author", "description"):
            self._document.set_metadata_field(self._field_name, self._new_value)
        else:
            raise ValueError(f"Unknown metadata field: {self._field_name}")

    def undo(self):
        """Undo the command (restore old value)."""
        # Map field name to appropriate document method
        if self._field_name == "name":
            self._document.set_name(self._old_value)
        elif self._field_name == "version":
            self._document.set_version(self._old_value)
        elif self._field_name == "type":
            self._document.set_type(self._old_value)
        elif self._field_name in ("author", "description"):
            self._document.set_metadata_field(self._field_name, self._old_value)
        else:
            raise ValueError(f"Unknown metadata field: {self._field_name}")

    def id(self) -> int:
        """Return command ID for merging consecutive edits."""
        # Return hash of field name so consecutive edits to same field can merge
        return hash(self._field_name) & 0x7FFFFFFF

    def mergeWith(self, other: QUndoCommand) -> bool:
        """Merge with another command if editing same field.

        Args:
            other: Other command to potentially merge with

        Returns:
            True if merged, False otherwise
        """
        if not isinstance(other, SetMetadataCommand):
            return False

        if other._field_name != self._field_name:
            return False

        # Merge by updating our new_value to other's new_value
        # Keep our old_value (so undo goes back to original)
        self._new_value = other._new_value
        return True
