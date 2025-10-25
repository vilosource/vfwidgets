"""Core data models for workspace widget."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


@dataclass
class FileInfo:
    """Information about a file or directory.

    Attributes:
        path: Absolute path to file/directory
        name: Display name (filename)
        is_dir: True if directory, False if file
        size: File size in bytes (None for directories)
        modified: Last modified timestamp (None if unavailable)
        extension: File extension (e.g., ".py"), empty for directories
    """

    path: str
    name: str
    is_dir: bool
    size: Optional[int] = None
    modified: Optional[datetime] = None
    extension: str = ""

    @classmethod
    def from_path(cls, path: Path) -> "FileInfo":
        """Create FileInfo from a Path object.

        Args:
            path: Path to file or directory

        Returns:
            FileInfo instance
        """
        is_dir = path.is_dir()
        size = None if is_dir else path.stat().st_size
        modified = datetime.fromtimestamp(path.stat().st_mtime)
        extension = "" if is_dir else path.suffix

        return cls(
            path=str(path.absolute()),
            name=path.name,
            is_dir=is_dir,
            size=size,
            modified=modified,
            extension=extension,
        )


@dataclass
class WorkspaceFolder:
    """Represents a root folder in a workspace.

    Attributes:
        path: Absolute path to folder
        name: Display name for folder (defaults to folder name)
    """

    path: str
    name: str = ""

    def __post_init__(self):
        """Set default name from path if not provided."""
        if not self.name:
            self.name = Path(self.path).name

    @classmethod
    def from_path(cls, path: Path, name: Optional[str] = None) -> "WorkspaceFolder":
        """Create WorkspaceFolder from a Path object.

        Args:
            path: Path to folder
            name: Optional display name

        Returns:
            WorkspaceFolder instance
        """
        return cls(path=str(path.absolute()), name=name or path.name)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {"path": self.path, "name": self.name}

    @classmethod
    def from_dict(cls, data: dict) -> "WorkspaceFolder":
        """Create from dictionary (JSON deserialization)."""
        return cls(path=data["path"], name=data.get("name", ""))


@dataclass
class WorkspaceConfig:
    """Workspace configuration (stored in .workspace.json).

    Attributes:
        version: Config format version (always 1 for now)
        name: Workspace name
        folders: List of workspace folders
        excluded_folders: Folder names to exclude globally
        custom_data: Application-specific custom data
    """

    version: int = 1
    name: str = ""
    folders: list[WorkspaceFolder] = field(default_factory=list)
    excluded_folders: list[str] = field(default_factory=list)
    custom_data: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_folder(cls, folder_path: Path, name: Optional[str] = None) -> "WorkspaceConfig":
        """Create single-folder workspace config.

        Args:
            folder_path: Path to folder
            name: Optional workspace name

        Returns:
            WorkspaceConfig with single folder
        """
        folder = WorkspaceFolder.from_path(folder_path)
        return cls(
            name=name or folder.name,
            folders=[folder],
            excluded_folders=["__pycache__", ".git", "node_modules", ".venv"],
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "version": self.version,
            "name": self.name,
            "folders": [f.to_dict() for f in self.folders],
            "excluded_folders": self.excluded_folders,
            "custom_data": self.custom_data,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WorkspaceConfig":
        """Create from dictionary (JSON deserialization)."""
        folders = [WorkspaceFolder.from_dict(f) for f in data.get("folders", [])]

        return cls(
            version=data.get("version", 1),
            name=data.get("name", ""),
            folders=folders,
            excluded_folders=data.get("excluded_folders", []),
            custom_data=data.get("custom_data", {}),
        )


@dataclass
class WorkspaceSession:
    """Workspace session state (UI state persistence).

    Stored in ~/.config/vfwidgets/workspaces/sessions/<hash>.json

    Attributes:
        workspace_name: Name of workspace
        last_opened: ISO timestamp of last open
        expanded_folders: List of expanded folder paths
        scroll_position: Vertical scroll position (pixels)
        active_file: Currently active file path
    """

    workspace_name: str
    last_opened: str
    expanded_folders: list[str] = field(default_factory=list)
    scroll_position: int = 0
    active_file: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "workspace_name": self.workspace_name,
            "last_opened": self.last_opened,
            "expanded_folders": self.expanded_folders,
            "scroll_position": self.scroll_position,
            "active_file": self.active_file,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WorkspaceSession":
        """Create from dictionary (JSON deserialization)."""
        return cls(
            workspace_name=data["workspace_name"],
            last_opened=data["last_opened"],
            expanded_folders=data.get("expanded_folders", []),
            scroll_position=data.get("scroll_position", 0),
            active_file=data.get("active_file"),
        )


@dataclass
class TreeNode:
    """Internal tree node for QAbstractItemModel.

    Represents a file or folder in the multi-root tree structure.

    Attributes:
        path: Absolute path to file/folder
        parent: Parent node (None for workspace roots)
        workspace_folder: Which workspace folder this belongs to
        children: Child nodes (None = not loaded yet)
        children_loaded: Whether children have been loaded
        file_info: Cached FileInfo for this node
        row: Row index within parent
    """

    path: str
    parent: Optional["TreeNode"] = None
    workspace_folder: Optional[WorkspaceFolder] = None
    children: Optional[list["TreeNode"]] = None
    children_loaded: bool = False
    file_info: Optional[FileInfo] = None
    row: int = 0

    def is_root(self) -> bool:
        """Check if this is a workspace root node."""
        return self.parent is None

    def child_count(self) -> int:
        """Get number of children (0 if not loaded)."""
        if self.children is None:
            return 0
        return len(self.children)

    def child_at(self, row: int) -> Optional["TreeNode"]:
        """Get child at row index."""
        if self.children is None or row < 0 or row >= len(self.children):
            return None
        return self.children[row]
