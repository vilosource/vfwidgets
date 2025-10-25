"""Multi-root filesystem model for workspace widget."""

import logging
from pathlib import Path
from typing import Any, Callable, Optional

from PySide6.QtCore import QAbstractItemModel, QFileSystemWatcher, QModelIndex, Qt, Signal
from PySide6.QtGui import QIcon

from .models import FileInfo, TreeNode, WorkspaceFolder
from .protocols import IconProvider

logger = logging.getLogger(__name__)


class MultiRootFileSystemModel(QAbstractItemModel):
    """QAbstractItemModel for multi-root filesystem tree.

    Displays multiple workspace folders as root items with lazy-loaded children.
    """

    # Signals
    directory_loaded = Signal(str)  # path
    file_changed = Signal(str)  # path

    def __init__(
        self,
        parent=None,
        file_extensions: Optional[list[str]] = None,
        excluded_folders: Optional[list[str]] = None,
        filter_callback: Optional[Callable[[FileInfo, WorkspaceFolder], bool]] = None,
        icon_provider: Optional[IconProvider] = None,
    ):
        """Initialize model.

        Args:
            parent: Parent QObject
            file_extensions: List of extensions to include (None = all)
            excluded_folders: Folder names to exclude
            filter_callback: Custom filter function
            icon_provider: Custom icon provider
        """
        super().__init__(parent)

        self._file_extensions = file_extensions
        self._excluded_folders = excluded_folders or []
        self._filter_callback = filter_callback
        self._icon_provider = icon_provider

        # Root nodes (workspace folders)
        self._root_nodes: list[TreeNode] = []

        # Caches
        self._file_info_cache: dict[str, FileInfo] = {}
        self._expanded_paths: set[str] = set()

        # Filesystem watcher
        self._fs_watcher = QFileSystemWatcher(self)
        self._fs_watcher.directoryChanged.connect(self._on_directory_changed)

    def set_folders(self, folders: list[WorkspaceFolder]) -> None:
        """Set workspace folders (replaces all roots).

        Args:
            folders: List of workspace folders
        """
        self.beginResetModel()

        # Clear existing
        self._root_nodes.clear()
        self._file_info_cache.clear()

        # Create root nodes
        for i, folder in enumerate(folders):
            path = Path(folder.path)

            if not path.exists() or not path.is_dir():
                logger.warning(f"Workspace folder does not exist: {folder.path}")
                continue

            # Create root node
            node = TreeNode(path=str(path.absolute()), parent=None, workspace_folder=folder, row=i)

            # Load file info
            node.file_info = FileInfo.from_path(path)

            self._root_nodes.append(node)

            # Watch directory for changes
            self._fs_watcher.addPath(str(path.absolute()))

        self.endResetModel()

    # =========================================================================
    # QAbstractItemModel Interface
    # =========================================================================

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        """Create index for row/column under parent.

        Args:
            row: Row number
            column: Column number (always 0 for tree)
            parent: Parent index

        Returns:
            QModelIndex for the item
        """
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            # Root level - return workspace folder
            if 0 <= row < len(self._root_nodes):
                return self.createIndex(row, column, self._root_nodes[row])
            return QModelIndex()

        # Get parent node
        parent_node: TreeNode = parent.internalPointer()

        # Load children if not loaded
        if not parent_node.children_loaded:
            self._load_children(parent_node)

        # Get child node
        child = parent_node.child_at(row)
        if child:
            return self.createIndex(row, column, child)

        return QModelIndex()

    def parent(self, index: QModelIndex) -> QModelIndex:
        """Get parent index.

        Args:
            index: Child index

        Returns:
            Parent index (invalid if root)
        """
        if not index.isValid():
            return QModelIndex()

        node: TreeNode = index.internalPointer()

        if node.is_root():
            return QModelIndex()

        parent_node = node.parent
        if parent_node is None:
            return QModelIndex()

        return self.createIndex(parent_node.row, 0, parent_node)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Get number of rows under parent.

        Args:
            parent: Parent index

        Returns:
            Number of children
        """
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            # Root level
            return len(self._root_nodes)

        # Get parent node
        parent_node: TreeNode = parent.internalPointer()

        # Load children if directory and not loaded
        if parent_node.file_info and parent_node.file_info.is_dir:
            if not parent_node.children_loaded:
                self._load_children(parent_node)

        return parent_node.child_count()

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Get number of columns (always 1 for tree)."""
        return 1

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Get data for index and role.

        Args:
            index: Model index
            role: Data role

        Returns:
            Data for the role
        """
        if not index.isValid():
            return None

        node: TreeNode = index.internalPointer()

        if role == Qt.ItemDataRole.DisplayRole:
            # Display name
            if node.is_root() and node.workspace_folder:
                return node.workspace_folder.name
            elif node.file_info:
                return node.file_info.name
            return Path(node.path).name

        elif role == Qt.ItemDataRole.DecorationRole:
            # Icon
            if not node.file_info:
                return None

            if self._icon_provider:
                if node.is_root() and node.workspace_folder:
                    is_expanded = self.is_expanded(node.path)
                    return self._icon_provider.get_workspace_folder_icon(
                        node.workspace_folder, is_expanded
                    )
                elif node.file_info.is_dir:
                    is_expanded = self.is_expanded(node.path)
                    return self._icon_provider.get_folder_icon(node.file_info, is_expanded)
                else:
                    return self._icon_provider.get_file_icon(node.file_info)

            # Default icons
            if node.file_info.is_dir:
                return QIcon.fromTheme("folder")
            else:
                return QIcon.fromTheme("text-x-generic")

        elif role == Qt.ItemDataRole.ToolTipRole:
            # Tooltip (full path)
            return node.path

        elif role == Qt.ItemDataRole.UserRole:
            # File info object
            return node.file_info

        elif role == Qt.ItemDataRole.UserRole + 1:
            # Workspace folder
            return node.workspace_folder

        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        """Get item flags.

        Args:
            index: Model index

        Returns:
            Item flags
        """
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def hasChildren(self, parent: QModelIndex = QModelIndex()) -> bool:
        """Check if item has children.

        Args:
            parent: Parent index

        Returns:
            True if item can have children
        """
        if not parent.isValid():
            # Root always has children (workspace folders)
            return len(self._root_nodes) > 0

        node: TreeNode = parent.internalPointer()

        if node.file_info:
            # Directories have children
            return node.file_info.is_dir

        return False

    def canFetchMore(self, parent: QModelIndex) -> bool:
        """Check if more data can be fetched.

        Args:
            parent: Parent index

        Returns:
            True if children not loaded yet
        """
        if not parent.isValid():
            return False

        node: TreeNode = parent.internalPointer()

        # Can fetch if directory and not loaded
        if node.file_info and node.file_info.is_dir:
            return not node.children_loaded

        return False

    def fetchMore(self, parent: QModelIndex) -> None:
        """Fetch more data (load children).

        Args:
            parent: Parent index
        """
        if not parent.isValid():
            return

        node: TreeNode = parent.internalPointer()

        if not node.children_loaded:
            self._load_children(parent_node=node)

    # =========================================================================
    # Internal Methods
    # =========================================================================

    def _load_children(self, parent_node: TreeNode) -> None:
        """Load children for a directory node.

        Args:
            parent_node: Parent directory node
        """
        if parent_node.children_loaded:
            return

        path = Path(parent_node.path)

        if not path.is_dir():
            parent_node.children = []
            parent_node.children_loaded = True
            return

        try:
            # List directory contents
            entries = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))

            children = []
            row = 0

            for entry in entries:
                # Skip excluded folders
                if entry.is_dir() and entry.name in self._excluded_folders:
                    continue

                # Create file info
                file_info = self._get_file_info(entry)

                # Apply filters
                if not self._should_include(file_info, parent_node.workspace_folder):
                    continue

                # Create child node
                child_node = TreeNode(
                    path=str(entry.absolute()),
                    parent=parent_node,
                    workspace_folder=parent_node.workspace_folder,
                    file_info=file_info,
                    row=row,
                )

                children.append(child_node)
                row += 1

            parent_node.children = children
            parent_node.children_loaded = True

            # Watch directory for changes
            self._fs_watcher.addPath(str(path.absolute()))

            # Emit signal
            self.directory_loaded.emit(str(path.absolute()))

        except PermissionError:
            logger.warning(f"Permission denied: {path}")
            parent_node.children = []
            parent_node.children_loaded = True

    def _get_file_info(self, path: Path) -> FileInfo:
        """Get FileInfo for path (cached).

        Args:
            path: Path to file/folder

        Returns:
            FileInfo object
        """
        path_str = str(path.absolute())

        if path_str in self._file_info_cache:
            return self._file_info_cache[path_str]

        file_info = FileInfo.from_path(path)
        self._file_info_cache[path_str] = file_info

        return file_info

    def _should_include(
        self, file_info: FileInfo, workspace_folder: Optional[WorkspaceFolder]
    ) -> bool:
        """Check if file should be included.

        Args:
            file_info: File information
            workspace_folder: Workspace folder containing file

        Returns:
            True if file should be included
        """
        # Always include directories
        if file_info.is_dir:
            return True

        # Extension filter
        if self._file_extensions:
            if file_info.extension not in self._file_extensions:
                return False

        # Custom filter callback
        if self._filter_callback and workspace_folder:
            return self._filter_callback(file_info, workspace_folder)

        return True

    def _on_directory_changed(self, path: str) -> None:
        """Handle directory change from QFileSystemWatcher.

        Args:
            path: Changed directory path
        """
        logger.debug(f"Directory changed: {path}")

        # Find node for this path
        node = self._find_node_by_path(path)

        if node:
            # Invalidate children
            node.children = None
            node.children_loaded = False

            # Notify views
            index = self._create_index_for_node(node)
            if index.isValid():
                # Force reload
                self.dataChanged.emit(index, index)

        self.file_changed.emit(path)

    def _find_node_by_path(self, path: str) -> Optional[TreeNode]:
        """Find tree node by absolute path.

        Args:
            path: Absolute path

        Returns:
            TreeNode if found, None otherwise
        """
        # Check roots
        for root in self._root_nodes:
            if root.path == path:
                return root

        # TODO: Implement recursive search if needed
        return None

    def _create_index_for_node(self, node: TreeNode) -> QModelIndex:
        """Create QModelIndex for a node.

        Args:
            node: Tree node

        Returns:
            QModelIndex
        """
        if node.is_root():
            return self.createIndex(node.row, 0, node)

        if node.parent:
            return self.createIndex(node.row, 0, node)

        return QModelIndex()

    # =========================================================================
    # Public Helper Methods
    # =========================================================================

    def is_expanded(self, path: str) -> bool:
        """Check if path is currently expanded.

        Args:
            path: Absolute path

        Returns:
            True if expanded
        """
        return path in self._expanded_paths

    def set_expanded(self, path: str, expanded: bool) -> None:
        """Set expanded state for path.

        Args:
            path: Absolute path
            expanded: True if expanded
        """
        if expanded:
            self._expanded_paths.add(path)
        else:
            self._expanded_paths.discard(path)

        # Trigger icon update for this path
        node = self._find_node_by_path(path)
        if node:
            index = self._create_index_for_node(node)
            if index.isValid():
                self.dataChanged.emit(index, index, [Qt.ItemDataRole.DecorationRole])

    def refresh(self) -> None:
        """Refresh entire model (reload from filesystem)."""
        self.beginResetModel()

        # Clear caches
        self._file_info_cache.clear()

        # Mark all nodes as not loaded
        for root in self._root_nodes:
            self._invalidate_node(root)

        self.endResetModel()

    def _invalidate_node(self, node: TreeNode) -> None:
        """Recursively invalidate node and children.

        Args:
            node: Node to invalidate
        """
        node.children = None
        node.children_loaded = False
        node.file_info = None
