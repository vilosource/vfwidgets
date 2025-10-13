"""Theme Document Model - Observable theme with undo/redo support."""

import json
from pathlib import Path

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QUndoStack
from vfwidgets_theme.core.repository import FileThemeLoader
from vfwidgets_theme.core.theme import Theme


class ThemeDocument(QObject):
    """Observable theme document with change tracking.

    Wraps a vfwidgets_theme.Theme object and provides:
    - Signals for token and metadata changes
    - Modified state tracking
    - File path management
    - Save/load operations
    - Undo/redo stack

    Signals:
        token_changed(str, str): Emitted when a token value changes (name, new_value)
        metadata_changed(str, str): Emitted when metadata changes (field, new_value)
        modified(bool): Emitted when modified state changes
        file_path_changed(str): Emitted when file path changes
    """

    # Signals
    token_changed = Signal(str, str)  # token_name, new_value
    metadata_changed = Signal(str, str)  # field_name, new_value
    modified = Signal(bool)  # is_modified
    file_path_changed = Signal(str)  # file_path

    def __init__(self, theme: Theme = None):
        """Initialize theme document.

        Args:
            theme: Theme object to wrap, or None to create default
        """
        super().__init__()

        # Wrapped theme
        if theme is not None:
            self._theme = theme
        else:
            # Create default empty theme with required base tokens
            # All themes MUST have colors.background, colors.foreground, colors.border
            self._theme = Theme(
                name="Untitled",
                version="1.0.0",
                type="dark",
                colors={
                    "colors.background": "#1e1e1e",  # Default dark background
                    "colors.foreground": "#d4d4d4",  # Default dark foreground
                    "colors.border": "#333333",  # Default dark border
                },
                metadata={"created_with": "VFTheme Studio"},
            )

        # Document state
        self._file_path = None
        self._modified = False

        # Undo/redo stack (prepared for Phase 2)
        self._undo_stack = QUndoStack(self)

        # Mark initial state as clean (no unsaved changes)
        self._undo_stack.setClean()

        # Connect undo stack clean state to modified flag
        # When we undo back to clean state, document should not be modified
        self._undo_stack.cleanChanged.connect(self._on_undo_clean_changed)

    @property
    def theme(self) -> Theme:
        """Get the wrapped theme object."""
        return self._theme

    @property
    def file_path(self) -> str | None:
        """Get the file path."""
        return self._file_path

    @property
    def file_name(self) -> str | None:
        """Get the file name without path."""
        if self._file_path:
            return Path(self._file_path).name
        return None

    def is_modified(self) -> bool:
        """Check if document has unsaved changes.

        Returns True if:
        - Document has been modified via set_token() OR
        - Undo stack is not clean (has unsaved undo/redo state)

        When using the undo stack (via ThemeController), the stack's clean state
        takes precedence. When bypassing the stack (direct set_token calls),
        the _modified flag is used.
        """
        # Check both modified flag and undo stack state
        # If undo stack has changes (not clean), document is modified
        if not self._undo_stack.isClean():
            return True
        # Otherwise, use the modified flag (for direct set_token calls)
        return self._modified

    def _on_undo_clean_changed(self, is_clean: bool):
        """Handle undo stack clean state changes.

        Args:
            is_clean: True if undo stack is at clean (saved) state
        """
        # When undo stack becomes clean, clear modified flag
        if is_clean:
            self._set_modified(False)

    def get_token(self, name: str) -> str:
        """Get token value.

        Args:
            name: Token name (e.g., "button.background")

        Returns:
            Token value (hex color or font string), or empty string if not defined
        """
        return self._theme.colors.get(name, "")

    def set_token(self, name: str, value: str):
        """Set token value.

        For Phase 1, this is a direct set (no undo support yet).
        Phase 2 will add QUndoCommand integration.

        Args:
            name: Token name
            value: Token value (hex color or font string)
        """
        old_value = self._theme.colors.get(name)

        # Only emit if value actually changed
        if old_value != value:
            self._theme.colors[name] = value
            self._set_modified(True)
            self.token_changed.emit(name, value)

    def get_all_tokens(self) -> dict[str, str]:
        """Get all defined tokens.

        Returns:
            Dictionary of token name -> value
        """
        return dict(self._theme.colors)

    def get_token_count(self) -> tuple[int, int]:
        """Get count of defined vs total tokens.

        Returns:
            Tuple of (defined_count, total_count)
        """
        defined = len(self._theme.colors)
        # Total tokens from ColorTokenRegistry (will import in Phase 1)
        total = 197  # Hardcoded for now, will get from registry later
        return (defined, total)

    def set_name(self, name: str):
        """Set theme name.

        Args:
            name: New theme name
        """
        old_value = self._theme.name
        if old_value != name:
            # Theme is frozen dataclass, use object.__setattr__ to bypass
            object.__setattr__(self._theme, "name", name)
            self._set_modified(True)
            self.metadata_changed.emit("name", name)

    def set_version(self, version: str):
        """Set theme version.

        Args:
            version: New theme version (semantic version format)
        """
        old_value = self._theme.version
        if old_value != version:
            # Theme is frozen dataclass, use object.__setattr__ to bypass
            object.__setattr__(self._theme, "version", version)
            self._set_modified(True)
            self.metadata_changed.emit("version", version)

    def set_type(self, type: str):
        """Set theme type.

        Args:
            type: New theme type (dark, light, high-contrast)
        """
        old_value = self._theme.type
        if old_value != type:
            # Theme is frozen dataclass, use object.__setattr__ to bypass
            object.__setattr__(self._theme, "type", type)
            self._set_modified(True)
            self.metadata_changed.emit("type", type)

    def set_metadata_field(self, key: str, value: str):
        """Set a metadata field (author, description, etc.).

        Args:
            key: Metadata field name
            value: New field value
        """
        old_value = self._theme.metadata.get(key, "")
        if old_value != value:
            self._theme.metadata[key] = value
            self._set_modified(True)
            self.metadata_changed.emit(key, value)

    def get_metadata_field(self, key: str, default: str = "") -> str:
        """Get a metadata field value.

        Args:
            key: Metadata field name
            default: Default value if field not set

        Returns:
            Metadata field value or default
        """
        return self._theme.metadata.get(key, default)

    def save(self, file_path: str = None):
        """Save theme to file.

        Args:
            file_path: Path to save to, or None to use current path

        Raises:
            ValueError: If no file path specified and no current path
            Exception: If save fails
        """
        # Determine save path
        path = file_path or self._file_path
        if not path:
            raise ValueError("No file path specified")

        # Convert theme to dict and save as JSON
        theme_dict = self._theme.to_dict()

        # Write to file
        with open(path, "w", encoding="utf-8") as f:
            json.dump(theme_dict, f, indent=2, ensure_ascii=False)

        # Update document state
        if file_path:
            self._file_path = file_path
            self.file_path_changed.emit(file_path)

        # Mark as saved (not modified) and set undo stack clean state
        self._set_modified(False)
        self._undo_stack.setClean()

    def load(self, file_path: str):
        """Load theme from file.

        Args:
            file_path: Path to theme JSON file

        Raises:
            Exception: If load fails
        """
        # Load theme using FileThemeLoader
        loader = FileThemeLoader()
        self._theme = loader.load_theme(file_path)

        # Update document state
        self._file_path = file_path
        self._set_modified(False)

        # Clear undo stack and mark as clean (freshly loaded = no undo history)
        self._undo_stack.clear()
        self._undo_stack.setClean()

        # Emit signals
        self.file_path_changed.emit(file_path)

        # Emit token_changed for all tokens (to update UI)
        for token_name, token_value in self._theme.colors.items():
            self.token_changed.emit(token_name, token_value)

        # Emit metadata_changed for all metadata fields (to update UI)
        self.metadata_changed.emit("name", self._theme.name)
        self.metadata_changed.emit("version", self._theme.version)
        self.metadata_changed.emit("type", self._theme.type)
        for key, value in self._theme.metadata.items():
            if key in ("author", "description"):
                self.metadata_changed.emit(key, value)

    def _set_modified(self, modified: bool):
        """Set modified state and emit signal if changed.

        Args:
            modified: New modified state
        """
        if self._modified != modified:
            self._modified = modified
            self.modified.emit(modified)

    # Undo/redo methods (prepared for Phase 2)
    def undo(self):
        """Undo last change (Phase 2)."""
        self._undo_stack.undo()

    def redo(self):
        """Redo last undone change (Phase 2)."""
        self._undo_stack.redo()

    def can_undo(self) -> bool:
        """Check if undo is available (Phase 2)."""
        return self._undo_stack.canUndo()

    def can_redo(self) -> bool:
        """Check if redo is available (Phase 2)."""
        return self._undo_stack.canRedo()
