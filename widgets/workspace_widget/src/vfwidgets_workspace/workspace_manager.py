"""Workspace configuration and session management."""

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QFileSystemWatcher, QObject, Signal

from .models import WorkspaceConfig, WorkspaceFolder, WorkspaceSession
from .protocols import ErrorHandler, ErrorSeverity, WorkspaceValidator

logger = logging.getLogger(__name__)


class WorkspaceManager(QObject):
    """Manages workspace configuration and session persistence.

    Workspace config location: <workspace_root>/.workspace.json
    Session location: ~/.config/vfwidgets/workspaces/sessions/<hash>.json
    Recent workspaces: ~/.config/vfwidgets/workspace/recent.json
    """

    # Signals
    workspace_opened = Signal(list)  # list[WorkspaceFolder]
    workspace_closed = Signal()
    folder_added = Signal(object)  # WorkspaceFolder
    folder_removed = Signal(str)  # folder_path
    config_changed = Signal()  # External config file changed
    workspace_file_changed = Signal(str)  # Portable workspace file path changed

    def __init__(
        self,
        config_class: type = WorkspaceConfig,
        config_filename: str = ".workspace.json",
        session_dir: Optional[Path] = None,
        workspace_file_extension: str = ".workspace",
        workspace_file_type_name: str = "Workspace Files",
        error_handler: Optional[ErrorHandler] = None,
        validator: Optional[WorkspaceValidator] = None,
        parent: Optional[QObject] = None,
    ):
        """Initialize workspace manager.

        Args:
            config_class: Config class (WorkspaceConfig or subclass)
            config_filename: Name of workspace config file
            session_dir: Directory for session files (None = default)
            workspace_file_extension: File extension for portable workspace files (e.g., ".workspace", ".reamde")
            workspace_file_type_name: Human-readable name for file dialogs (e.g., "Workspace Files")
            error_handler: Custom error handler (None = use default)
            validator: Custom workspace validator (None = use default)
            parent: Parent QObject
        """
        super().__init__(parent)

        self._config_class = config_class
        self._config_filename = config_filename
        self._session_dir = session_dir or self._get_default_session_dir()
        self._workspace_file_extension = workspace_file_extension
        self._workspace_file_type_name = workspace_file_type_name
        self._error_handler = error_handler
        self._validator = validator

        # State
        self._folders: list[WorkspaceFolder] = []
        self._config: Optional[WorkspaceConfig] = None
        self._workspace_path: Optional[Path] = None
        self._current_workspace_file: Optional[Path] = None  # Portable workspace file path

        # Config file watcher
        self._config_watcher = QFileSystemWatcher(self)
        self._config_watcher.fileChanged.connect(self._on_config_changed)

        # Recent workspaces file
        self._recent_workspaces_file = (
            Path.home() / ".config" / "vfwidgets" / "workspace" / "recent.json"
        )

    # =========================================================================
    # Workspace Operations
    # =========================================================================

    def open_workspace(self, folder_path: Path) -> list[WorkspaceFolder]:
        """Open workspace and return folders.

        Args:
            folder_path: Path to workspace root folder

        Returns:
            List of workspace folders

        Raises:
            ValueError: If workspace fails validation
        """
        # Try to load config
        config_path = folder_path / self._config_filename

        if config_path.exists():
            # Load from config file
            try:
                config = self._load_config(config_path)
            except json.JSONDecodeError as e:
                # Corrupt config - let error handler decide
                if self._error_handler:
                    self._error_handler.handle_error(
                        ErrorSeverity.ERROR,
                        f"Config file corrupt: {e}",
                        exception=e,
                        context={"config_path": str(config_path)},
                    )
                # Use default config
                config = self._config_class.from_folder(folder_path)
        else:
            # No config - create single-folder workspace
            config = self._config_class.from_folder(folder_path)

        # Store state
        self._folders = config.folders
        self._config = config
        self._workspace_path = folder_path

        # Watch config file
        if config_path.exists():
            self._config_watcher.addPath(str(config_path))

        # Add to recent workspaces
        self.add_recent_workspace(str(folder_path.absolute()), config.name, len(config.folders))

        # Emit signal
        self.workspace_opened.emit(self._folders)

        return self._folders

    def close_workspace(self) -> None:
        """Close current workspace."""
        if not self._workspace_path and not self._current_workspace_file:
            return

        # Stop watching config
        if self._workspace_path:
            config_path = self._workspace_path / self._config_filename
            if str(config_path) in self._config_watcher.files():
                self._config_watcher.removePath(str(config_path))

        # Clear state
        self._folders.clear()
        self._config = None
        self._workspace_path = None
        self._current_workspace_file = None

        # Emit signal
        self.workspace_closed.emit()

    def add_folder(self, folder_path: Path) -> WorkspaceFolder:
        """Add folder to workspace.

        Args:
            folder_path: Path to folder

        Returns:
            Created WorkspaceFolder

        Raises:
            ValueError: If workspace not open or folder invalid
        """
        if not self._config:
            raise ValueError("No workspace open")

        # Create folder
        folder = WorkspaceFolder.from_path(folder_path)

        # Add to config
        self._config.folders.append(folder)
        self._folders.append(folder)

        # Save config
        self.save_config()

        # Emit signal
        self.folder_added.emit(folder)

        return folder

    def remove_folder(self, folder_path: str) -> None:
        """Remove folder from workspace.

        Args:
            folder_path: Absolute path to folder
        """
        if not self._config:
            return

        # Find and remove folder
        self._config.folders = [f for f in self._config.folders if f.path != folder_path]
        self._folders = [f for f in self._folders if f.path != folder_path]

        # Save config
        self.save_config()

        # Emit signal
        self.folder_removed.emit(folder_path)

    def rename_folder(self, folder_path: str, new_name: str) -> None:
        """Rename workspace folder display name.

        Args:
            folder_path: Absolute path to folder
            new_name: New display name
        """
        if not self._config:
            return

        # Find and rename
        for folder in self._config.folders:
            if folder.path == folder_path:
                folder.name = new_name
                break

        for folder in self._folders:
            if folder.path == folder_path:
                folder.name = new_name
                break

        # Save config
        self.save_config()

    # =========================================================================
    # Config Management
    # =========================================================================

    def _load_config(self, config_path: Path) -> WorkspaceConfig:
        """Load config from JSON file.

        Args:
            config_path: Path to config file

        Returns:
            WorkspaceConfig instance

        Raises:
            json.JSONDecodeError: If config file is corrupt
        """
        with open(config_path, encoding="utf-8") as f:
            data = json.load(f)

        return self._config_class.from_dict(data)

    def save_config(self) -> None:
        """Save current config to file."""
        if not self._workspace_path or not self._config:
            return

        config_path = self._workspace_path / self._config_filename

        # Temporarily remove from watcher (avoid triggering fileChanged)
        if str(config_path) in self._config_watcher.files():
            self._config_watcher.removePath(str(config_path))

        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(self._config.to_dict(), f, indent=2, ensure_ascii=False)

        except OSError as e:
            if self._error_handler:
                self._error_handler.handle_error(
                    ErrorSeverity.ERROR,
                    f"Failed to save config: {e}",
                    exception=e,
                    context={"config_path": str(config_path)},
                )
        finally:
            # Re-add to watcher
            if config_path.exists():
                self._config_watcher.addPath(str(config_path))

    def _on_config_changed(self, path: str) -> None:
        """Handle external config file change.

        Args:
            path: Path to changed config file
        """
        # Reload config
        try:
            config = self._load_config(Path(path))
            self._config = config
            self._folders = config.folders

            # Emit signal
            self.config_changed.emit()

        except (json.JSONDecodeError, OSError) as e:
            if self._error_handler:
                self._error_handler.handle_error(
                    ErrorSeverity.WARNING,
                    f"Config file changed but failed to reload: {e}",
                    exception=e,
                )

    # =========================================================================
    # Portable Workspace Files
    # =========================================================================

    def save_workspace_file(self, file_path: Path) -> bool:
        """Save workspace configuration to portable file.

        Saves the complete workspace configuration (folders, excluded folders,
        custom data) to a portable .workspace file that can be stored anywhere
        and loaded later. This is separate from session state (UI state).

        Args:
            file_path: Path where to save workspace file (e.g., /docs/project.workspace)

        Returns:
            True if saved successfully, False otherwise

        Example:
            >>> manager.save_workspace_file(Path("/docs/my-project.workspace"))
            True
        """
        if not self._config:
            logger.warning("No workspace config to save")
            return False

        try:
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Save config to file
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self._config.to_dict(), f, indent=2, ensure_ascii=False)

            # Track this as current workspace file
            self._current_workspace_file = file_path
            logger.info(f"Saved workspace to file: {file_path}")

            # Emit signal
            self.workspace_file_changed.emit(str(file_path))

            return True

        except OSError as e:
            if self._error_handler:
                self._error_handler.handle_error(
                    ErrorSeverity.ERROR,
                    f"Failed to save workspace file: {e}",
                    exception=e,
                    context={"file_path": str(file_path)},
                )
            logger.error(f"Failed to save workspace file {file_path}: {e}")
            return False

    def load_workspace_file(self, file_path: Path) -> bool:
        """Load workspace configuration from portable file.

        Loads a workspace from a .workspace file and opens it. This replaces
        any currently open workspace.

        Args:
            file_path: Path to workspace file to load

        Returns:
            True if loaded successfully, False otherwise

        Example:
            >>> manager.load_workspace_file(Path("/docs/my-project.workspace"))
            True
        """
        if not file_path.exists():
            logger.error(f"Workspace file does not exist: {file_path}")
            if self._error_handler:
                self._error_handler.handle_error(
                    ErrorSeverity.ERROR,
                    f"Workspace file not found: {file_path}",
                    context={"file_path": str(file_path)},
                )
            return False

        try:
            # Load config from file
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            config = self._config_class.from_dict(data)

            # Close current workspace if any
            if self._workspace_path:
                self.close_workspace()

            # Set config
            self._config = config
            self._folders = config.folders.copy()
            self._current_workspace_file = file_path

            # For portable files, we don't have a single workspace_path
            # (multi-root workspaces have multiple paths)
            # Set to None to indicate portable mode
            self._workspace_path = None

            logger.info(f"Loaded workspace from file: {file_path} ({len(self._folders)} folders)")

            # Emit signals
            self.workspace_opened.emit(self._folders)
            self.workspace_file_changed.emit(str(file_path))

            # Add to recent workspaces
            self.add_recent_workspace(str(file_path), config.name, len(config.folders))

            return True

        except (json.JSONDecodeError, OSError, KeyError) as e:
            if self._error_handler:
                self._error_handler.handle_error(
                    ErrorSeverity.ERROR,
                    f"Failed to load workspace file: {e}",
                    exception=e,
                    context={"file_path": str(file_path)},
                )
            logger.error(f"Failed to load workspace file {file_path}: {e}")
            return False

    def get_workspace_file_path(self) -> Optional[Path]:
        """Get path to current workspace file (if opened from file).

        Returns:
            Path to workspace file, or None if opened from folder

        Example:
            >>> path = manager.get_workspace_file_path()
            >>> if path:
            ...     print(f"Workspace file: {path}")
        """
        return self._current_workspace_file

    def is_workspace_from_file(self) -> bool:
        """Check if current workspace was opened from portable file.

        Returns:
            True if opened from .workspace file, False if opened from folder

        Example:
            >>> if manager.is_workspace_from_file():
            ...     print("Workspace is from portable file")
        """
        return self._current_workspace_file is not None

    def get_workspace_file_extension(self) -> str:
        """Get the configured workspace file extension.

        Returns:
            File extension (e.g., ".workspace", ".reamde", ".viloxterm")

        Example:
            >>> ext = manager.get_workspace_file_extension()
            >>> print(f"Extension: {ext}")  # ".reamde"
        """
        return self._workspace_file_extension

    def get_workspace_file_type_name(self) -> str:
        """Get the human-readable workspace file type name.

        Returns:
            File type name for file dialogs (e.g., "Reamde Workspace Files")

        Example:
            >>> name = manager.get_workspace_file_type_name()
            >>> print(f"File type: {name}")  # "Reamde Workspace Files"
        """
        return self._workspace_file_type_name

    def get_file_dialog_filter(self) -> str:
        """Get the file dialog filter string for workspace files.

        Returns:
            Filter string in Qt file dialog format

        Example:
            >>> filter = manager.get_file_dialog_filter()
            >>> print(filter)  # "Reamde Workspace Files (*.reamde);;All Files (*)"
        """
        return (
            f"{self._workspace_file_type_name} (*{self._workspace_file_extension});;All Files (*)"
        )

    # =========================================================================
    # Session Management
    # =========================================================================

    def load_session(self, workspace_path: Path) -> Optional[WorkspaceSession]:
        """Load session for workspace.

        Args:
            workspace_path: Path to workspace root

        Returns:
            WorkspaceSession if found, None otherwise
        """
        session_hash = self._compute_session_hash(workspace_path)
        session_path = self._session_dir / f"{session_hash}.json"

        if not session_path.exists():
            return None

        try:
            with open(session_path, encoding="utf-8") as f:
                data = json.load(f)
            return WorkspaceSession.from_dict(data)

        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to load session: {e}")
            return None

    def save_session(self, session: WorkspaceSession) -> None:
        """Save session to file.

        Args:
            session: Session to save
        """
        if not self._workspace_path:
            return

        session_hash = self._compute_session_hash(self._workspace_path)
        session_path = self._session_dir / f"{session_hash}.json"

        # Ensure directory exists
        session_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(session_path, "w", encoding="utf-8") as f:
                json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)

        except OSError as e:
            logger.error(f"Failed to save session: {e}")

    @staticmethod
    def _compute_session_hash(workspace_path: Path) -> str:
        """Compute hash for session filename.

        Args:
            workspace_path: Path to workspace root

        Returns:
            16-character hex hash
        """
        return hashlib.md5(str(workspace_path).encode()).hexdigest()[:16]

    @staticmethod
    def _get_default_session_dir() -> Path:
        """Get default session directory.

        Returns:
            Path to session directory
        """
        return Path.home() / ".config" / "vfwidgets" / "workspaces" / "sessions"

    # =========================================================================
    # Recent Workspaces
    # =========================================================================

    def get_recent_workspaces(self, max_count: int = 10) -> list[dict]:
        """Get recently opened workspaces.

        Args:
            max_count: Maximum number to return

        Returns:
            List of recent workspace dictionaries
        """
        recent = self._load_recent_workspaces()
        return recent[:max_count]

    def add_recent_workspace(self, workspace_path: str, name: str, folder_count: int) -> None:
        """Add workspace to recent list.

        Args:
            workspace_path: Absolute path to workspace
            name: Workspace name
            folder_count: Number of folders in workspace
        """
        recent = self._load_recent_workspaces()

        # Create entry
        entry = {
            "path": workspace_path,
            "name": name,
            "folder_count": folder_count,
            "last_opened": datetime.now().isoformat(),
        }

        # Remove if already exists (move to front)
        recent = [r for r in recent if r["path"] != workspace_path]

        # Add to front
        recent.insert(0, entry)

        # Limit to 10
        recent = recent[:10]

        # Save
        self._save_recent_workspaces(recent)

    def _load_recent_workspaces(self) -> list[dict]:
        """Load recent workspaces from file.

        Returns:
            List of recent workspace dictionaries
        """
        if not self._recent_workspaces_file.exists():
            return []

        try:
            with open(self._recent_workspaces_file, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []

    def _save_recent_workspaces(self, recent: list[dict]) -> None:
        """Save recent workspaces to file.

        Args:
            recent: List of recent workspace dictionaries
        """
        # Ensure directory exists
        self._recent_workspaces_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(self._recent_workspaces_file, "w", encoding="utf-8") as f:
                json.dump(recent, f, indent=2, ensure_ascii=False)
        except OSError as e:
            logger.error(f"Failed to save recent workspaces: {e}")

    # =========================================================================
    # Query Methods
    # =========================================================================

    def get_folders(self) -> list[WorkspaceFolder]:
        """Get list of workspace folders.

        Returns:
            List of WorkspaceFolder objects
        """
        return self._folders.copy()

    def get_config(self) -> Optional[WorkspaceConfig]:
        """Get current workspace configuration.

        Returns:
            WorkspaceConfig or None if no workspace open
        """
        return self._config

    def is_workspace_open(self) -> bool:
        """Check if workspace is currently open.

        Returns:
            True if workspace open, False otherwise
        """
        return self._workspace_path is not None
