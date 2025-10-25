"""Protocols for workspace widget extension points."""

from enum import Enum
from typing import Optional, Protocol

from PySide6.QtGui import QAction, QIcon

from .models import FileInfo, WorkspaceFolder


class FileConflictAction(Enum):
    """Action to take when file conflict detected."""

    RELOAD = "reload"  # Reload file without prompting
    PROMPT_RELOAD = "prompt"  # Ask user to reload
    IGNORE = "ignore"  # Ignore the change
    CLOSE = "close"  # Close the file
    SHOW_DIFF = "diff"  # Show diff viewer


class FileConflictHandler(Protocol):
    """Protocol for handling file conflicts (external modifications)."""

    def handle_file_modified(
        self, file_path: str, workspace_folder: Optional[str] = None
    ) -> FileConflictAction:
        """Handle file modified externally.

        Args:
            file_path: Absolute path to modified file
            workspace_folder: Workspace folder path (if known)

        Returns:
            Action to take
        """
        ...

    def handle_file_deleted(
        self, file_path: str, workspace_folder: Optional[str] = None
    ) -> FileConflictAction:
        """Handle file deleted externally.

        Args:
            file_path: Absolute path to deleted file
            workspace_folder: Workspace folder path (if known)

        Returns:
            Action to take
        """
        ...

    def handle_file_moved(
        self, old_path: str, new_path: str, workspace_folder: Optional[str] = None
    ) -> FileConflictAction:
        """Handle file moved/renamed externally.

        Args:
            old_path: Original path
            new_path: New path
            workspace_folder: Workspace folder path (if known)

        Returns:
            Action to take
        """
        ...


class ErrorSeverity(Enum):
    """Error severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorHandler(Protocol):
    """Protocol for handling errors."""

    def handle_error(
        self,
        severity: ErrorSeverity,
        message: str,
        exception: Optional[Exception] = None,
        context: Optional[dict] = None,
    ) -> None:
        """Handle an error.

        Args:
            severity: Error severity level
            message: Human-readable error message
            exception: Optional exception object
            context: Optional context dictionary
        """
        ...


class IconProvider(Protocol):
    """Protocol for providing file/folder icons."""

    def get_file_icon(self, file_info: FileInfo) -> QIcon:
        """Get icon for a file.

        Args:
            file_info: File information

        Returns:
            QIcon for the file
        """
        ...

    def get_folder_icon(self, file_info: FileInfo, is_expanded: bool = False) -> QIcon:
        """Get icon for a folder.

        Args:
            file_info: Folder information
            is_expanded: Whether folder is currently expanded

        Returns:
            QIcon for the folder
        """
        ...

    def get_workspace_folder_icon(
        self, workspace_folder: WorkspaceFolder, is_expanded: bool = False
    ) -> QIcon:
        """Get icon for a workspace folder root.

        Args:
            workspace_folder: Workspace folder
            is_expanded: Whether folder is currently expanded

        Returns:
            QIcon for the workspace folder
        """
        ...


class ValidationResult:
    """Result of workspace validation."""

    def __init__(self, valid: bool, message: str = ""):
        """Initialize validation result.

        Args:
            valid: Whether validation passed
            message: Error/warning message if not valid
        """
        self.valid = valid
        self.message = message

    @classmethod
    def success(cls) -> "ValidationResult":
        """Create success result."""
        return cls(True)

    @classmethod
    def failure(cls, message: str) -> "ValidationResult":
        """Create failure result with message."""
        return cls(False, message)


class WorkspaceValidator(Protocol):
    """Protocol for validating workspace folders."""

    def validate_workspace_folder(self, folder_path: str) -> ValidationResult:
        """Validate a workspace folder before opening.

        Args:
            folder_path: Absolute path to folder

        Returns:
            ValidationResult indicating if valid
        """
        ...


class ContextMenuProvider(Protocol):
    """Protocol for providing context menu actions."""

    def get_file_menu_actions(
        self, file_info: FileInfo, workspace_folder: WorkspaceFolder
    ) -> list[QAction]:
        """Get context menu actions for a file.

        Args:
            file_info: File information
            workspace_folder: Workspace folder containing file

        Returns:
            List of QAction objects
        """
        ...

    def get_folder_menu_actions(
        self, file_info: FileInfo, workspace_folder: WorkspaceFolder
    ) -> list[QAction]:
        """Get context menu actions for a folder.

        Args:
            file_info: Folder information
            workspace_folder: Workspace folder containing folder

        Returns:
            List of QAction objects
        """
        ...

    def get_workspace_folder_menu_actions(self, workspace_folder: WorkspaceFolder) -> list[QAction]:
        """Get context menu actions for a workspace folder root.

        Args:
            workspace_folder: Workspace folder

        Returns:
            List of QAction objects
        """
        ...


class WorkspaceLifecycleHooks(Protocol):
    """Protocol for workspace lifecycle hooks."""

    def before_workspace_open(self, folder_path: str) -> bool:
        """Called before opening workspace.

        Args:
            folder_path: Path to workspace folder

        Returns:
            True to proceed, False to cancel
        """
        ...

    def after_workspace_opened(self, folders: list[WorkspaceFolder]) -> None:
        """Called after workspace opened successfully.

        Args:
            folders: List of workspace folders
        """
        ...

    def before_workspace_close(self) -> bool:
        """Called before closing workspace.

        Returns:
            True to proceed, False to cancel
        """
        ...

    def after_workspace_closed(self) -> None:
        """Called after workspace closed."""
        ...

    def before_folder_add(self, folder_path: str) -> bool:
        """Called before adding folder to workspace.

        Args:
            folder_path: Path to folder

        Returns:
            True to proceed, False to cancel
        """
        ...

    def after_folder_added(self, workspace_folder: WorkspaceFolder) -> None:
        """Called after folder added successfully.

        Args:
            workspace_folder: Added folder
        """
        ...

    def before_folder_remove(self, folder_path: str) -> bool:
        """Called before removing folder from workspace.

        Args:
            folder_path: Path to folder

        Returns:
            True to proceed, False to cancel
        """
        ...

    def after_folder_removed(self, folder_path: str) -> None:
        """Called after folder removed.

        Args:
            folder_path: Path to removed folder
        """
        ...

    def before_config_save(self) -> bool:
        """Called before saving workspace config.

        Returns:
            True to proceed, False to cancel
        """
        ...

    def after_config_saved(self) -> None:
        """Called after config saved successfully."""
        ...

    def before_session_save(self) -> bool:
        """Called before saving workspace session.

        Returns:
            True to proceed, False to cancel
        """
        ...

    def after_session_saved(self) -> None:
        """Called after session saved successfully."""
        ...
