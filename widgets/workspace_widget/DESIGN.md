# VFWidgets Workspace Widget - Technical Design Document

**Version:** 1.0
**Date:** 2025-10-24
**Status:** Design Phase
**Companion Document:** SPECIFICATION.md

## Purpose

This document describes **HOW to implement** the Workspace Widget. It provides:
- Detailed architecture with component relationships
- Implementation algorithms for complex components
- Sequence diagrams for key operations
- State machines for lifecycle management
- Error handling paths
- Performance implementation strategies
- Thread safety analysis

**Audience:** Developers implementing the workspace widget.

**Companion Document:** See SPECIFICATION.md for WHAT to build (public API, features, usage examples).

---

## Table of Contents

1. [Architecture Details](#architecture-details)
2. [MultiRootFileSystemModel Implementation](#multirootfilesystemmodel-implementation)
3. [Sequence Diagrams](#sequence-diagrams)
4. [State Machines](#state-machines)
5. [Error Handling Paths](#error-handling-paths)
6. [Performance Implementation](#performance-implementation)
7. [Thread Safety Analysis](#thread-safety-analysis)
8. [Implementation Checklist](#implementation-checklist)

---

## Architecture Details

### Component Relationships

```
┌─────────────────────────────────────────────────────────────────┐
│                        WorkspaceWidget                          │
│                         (QWidget)                               │
│                                                                 │
│  ┌─────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │ WorkspaceManager│  │ MultiRootFSModel │  │FileExplorerWgt│ │
│  │   (QObject)     │  │(QAbstractItemMdl)│  │ (ThemedWidget)│ │
│  │                 │  │                  │  │               │ │
│  │ Owns:           │  │ Owns:            │  │ Contains:     │ │
│  │ - folders list  │  │ - TreeNode tree  │  │ - QTreeView   │ │
│  │ - config file   │  │ - FileInfo cache │  │ - model ref   │ │
│  │ - session file  │  │ - QFileSysWatch  │  │               │ │
│  └────────┬────────┘  └────────┬─────────┘  └───────┬───────┘ │
│           │                    │                    │         │
│           │                    │                    │         │
│           ├────────────────────┼────────────────────┤         │
│           │    Signals/Slots   │                    │         │
│           └────────────────────┴────────────────────┘         │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Extension Point Handlers                    │  │
│  │  - FileConflictHandler                                   │  │
│  │  - ErrorHandler                                          │  │
│  │  - IconProvider                                          │  │
│  │  - WorkspaceValidator                                    │  │
│  │  - ContextMenuProvider                                   │  │
│  │  - WorkspaceLifecycleHooks                               │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Ownership Model

**WorkspaceWidget owns:**
- `WorkspaceManager` (parent=self)
- `MultiRootFileSystemModel` (parent=self)
- `FileExplorerWidget` (parent=self)
- All extension point handlers (stored as instance variables)

**WorkspaceManager owns:**
- `list[WorkspaceFolder]` (current workspace folders)
- `WorkspaceConfig` instance (current config)
- `QFileSystemWatcher` for config file watching

**MultiRootFileSystemModel owns:**
- `list[TreeNode]` (root nodes, one per workspace folder)
- `dict[str, FileInfo]` (filesystem cache)
- `QFileSystemWatcher` for folder watching

**FileExplorerWidget owns:**
- `QTreeView` (the actual tree widget)
- Reference to model (doesn't own)

### Signal/Slot Connections

```python
# WorkspaceManager → WorkspaceWidget (forwarding)
manager.workspace_opened → widget.workspace_opened
manager.workspace_closed → widget.workspace_closed
manager.folder_added → widget.folder_added
manager.folder_removed → widget.folder_removed

# MultiRootFileSystemModel → WorkspaceWidget
model.file_system_changed → widget._on_filesystem_changed

# FileExplorerWidget → WorkspaceWidget (forwarding)
explorer.file_selected → widget.file_selected
explorer.file_double_clicked → widget.file_double_clicked
explorer.folder_expanded → widget.folder_expanded
explorer.folder_collapsed → widget.folder_collapsed
explorer.context_menu_requested → widget.context_menu_requested

# QFileSystemWatcher → MultiRootFileSystemModel
watcher.fileChanged → model._on_file_changed
watcher.directoryChanged → model._on_directory_changed

# WorkspaceWidget internal
widget.workspace_opened → widget._on_workspace_opened_internal
widget.workspace_closed → widget._on_workspace_closed_internal
```

### Initialization Sequence

```python
class WorkspaceWidget(QWidget):
    def __init__(
        self,
        file_extensions: Optional[list[str]] = None,
        excluded_folders: Optional[list[str]] = None,
        filter_callback: Optional[Callable[[FileInfo, WorkspaceFolder], bool]] = None,
        config_class: type = WorkspaceConfig,
        config_filename: str = ".workspace.json",
        session_dir: Optional[Path] = None,
        conflict_handler: Optional[FileConflictHandler] = None,
        error_handler: Optional[ErrorHandler] = None,
        icon_provider: Optional[IconProvider] = None,
        workspace_validator: Optional[WorkspaceValidator] = None,
        context_menu_provider: Optional[ContextMenuProvider] = None,
        lifecycle_hooks: Optional[WorkspaceLifecycleHooks] = None,
        parent: Optional[QWidget] = None
    ):
        """Initialize workspace widget.

        Args:
            file_extensions: File extensions to show (None = all files)
            excluded_folders: Folders to exclude from tree
            filter_callback: Custom filter function
            config_class: Config class (WorkspaceConfig or subclass)
            config_filename: Name of workspace config file
            session_dir: Directory for session files (None = default)
            conflict_handler: Custom file conflict handler (None = use default)
            error_handler: Custom error handler (None = use default)
            icon_provider: Custom icon provider (None = use default)
            workspace_validator: Custom workspace validator (None = use default)
            context_menu_provider: Custom context menu provider (None = use default)
            lifecycle_hooks: Custom lifecycle hooks (None = use default)
            parent: Parent widget
        """
        super().__init__(parent)

        # Phase 1: Create handlers (no dependencies)
        self._conflict_handler = conflict_handler or DefaultFileConflictHandler(self)
        self._error_handler = error_handler or DefaultErrorHandler(self)
        self._icon_provider = icon_provider or DefaultIconProvider()
        self._validator = workspace_validator or DefaultWorkspaceValidator()
        self._context_menu_provider = context_menu_provider or DefaultContextMenuProvider(self)
        self._lifecycle_hooks = lifecycle_hooks or DefaultLifecycleHooks()

        # Phase 2: Create model (depends on handlers)
        self._model = MultiRootFileSystemModel(
            file_extensions=file_extensions,
            excluded_folders=excluded_folders,
            filter_callback=filter_callback,
            icon_provider=self._icon_provider,
            parent=self
        )

        # Phase 3: Create manager (depends on handlers)
        self._manager = WorkspaceManager(
            config_class=config_class,
            config_filename=config_filename,
            session_dir=session_dir,
            error_handler=self._error_handler,
            validator=self._validator,
            parent=self
        )

        # Phase 4: Create view (depends on model)
        self._explorer = FileExplorerWidget(parent=self)
        self._explorer.set_model(self._model)

        # Phase 5: Setup UI layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._explorer)

        # Phase 6: Connect signals
        self._connect_signals()

        # Phase 7: Initialize state
        self._current_workspace_path: Optional[Path] = None
        self._auto_watch_mode = AutoWatchMode.MANUAL
```

---

## MultiRootFileSystemModel Implementation

### Overview

The most complex component. Must implement QAbstractItemModel for a multi-root tree structure.

### Internal Data Structure

```python
class TreeNode:
    """Internal node in the multi-root filesystem tree.

    Represents either:
    - A workspace folder root (parent=None)
    - A directory in the filesystem (parent=TreeNode, is_dir=True)
    - A file in the filesystem (parent=TreeNode, is_dir=False)
    """

    def __init__(
        self,
        path: str,              # Absolute filesystem path
        parent: Optional["TreeNode"] = None,
        workspace_folder: Optional[WorkspaceFolder] = None
    ):
        self.path = path
        self.parent = parent
        self.workspace_folder = workspace_folder  # Set for root nodes only

        # Children management
        self.children: Optional[list[TreeNode]] = None  # None = not loaded yet
        self.children_loaded = False

        # Cached filesystem info
        self.file_info: Optional[FileInfo] = None

        # Row in parent's children list (cached for performance)
        self.row = 0

    @property
    def is_root(self) -> bool:
        """True if this is a workspace folder root."""
        return self.parent is None

    @property
    def is_dir(self) -> bool:
        """True if this represents a directory."""
        if self.file_info:
            return self.file_info.is_dir
        # Root nodes are always directories
        return self.is_root or Path(self.path).is_dir()

    def load_children(self, filter_func: Callable) -> None:
        """Load children from filesystem.

        Only called when node is expanded in tree view.
        Applies filtering during load.
        """
        if self.children_loaded:
            return

        self.children = []

        try:
            path = Path(self.path)
            if not path.is_dir():
                self.children_loaded = True
                return

            # Scan directory
            for item in sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
                # Apply filter
                if filter_func(item):
                    child_node = TreeNode(str(item), parent=self)
                    child_node.row = len(self.children)
                    self.children.append(child_node)

            self.children_loaded = True

        except (PermissionError, OSError) as e:
            # Log error, leave children empty
            logger.warning(f"Failed to load children for {self.path}: {e}")
            self.children = []
            self.children_loaded = True
```

### QAbstractItemModel Implementation

```python
class MultiRootFileSystemModel(QAbstractItemModel):
    """Multi-root filesystem model for workspace tree.

    Tree structure:
        (Invalid QModelIndex = virtual root)
        ├─ WorkspaceFolder 1 (row=0, parent=invalid)
        │  ├─ folder1/ (row=0, parent=WF1)
        │  │  ├─ file1.py (row=0, parent=folder1)
        │  │  └─ file2.py (row=1, parent=folder1)
        │  └─ file3.md (row=1, parent=WF1)
        └─ WorkspaceFolder 2 (row=1, parent=invalid)
           └─ ...
    """

    def __init__(self, ...):
        super().__init__(parent)

        # Root nodes (one per workspace folder)
        self._root_nodes: list[TreeNode] = []

        # Filesystem cache (path → FileInfo)
        self._file_cache: dict[str, FileInfo] = {}

        # Filtering configuration
        self._file_extensions: list[str] = file_extensions or []
        self._excluded_folders: set[str] = set(excluded_folders or [])
        self._filter_callback = filter_callback
        self._filter_enabled = True

        # Filesystem watcher
        self._watcher = QFileSystemWatcher(self)
        self._watcher.fileChanged.connect(self._on_file_changed)
        self._watcher.directoryChanged.connect(self._on_directory_changed)

        # Icon provider
        self._icon_provider = icon_provider

    # =========================================================================
    # QAbstractItemModel Interface
    # =========================================================================

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        """Create index for given row, column, parent.

        Algorithm:
        1. If parent is invalid (virtual root):
           - Children are workspace folder roots
           - Return index with root_nodes[row] as internal pointer

        2. If parent is valid (actual node):
           - Get parent node from parent.internalPointer()
           - Ensure parent's children are loaded
           - Return index with children[row] as internal pointer
        """
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        # Parent is virtual root → children are workspace roots
        if not parent.isValid():
            if 0 <= row < len(self._root_nodes):
                node = self._root_nodes[row]
                return self.createIndex(row, column, node)
            return QModelIndex()

        # Parent is actual node
        parent_node: TreeNode = parent.internalPointer()

        # Ensure children loaded
        if not parent_node.children_loaded:
            parent_node.load_children(self._should_include_file)

        # Get child at row
        if parent_node.children and 0 <= row < len(parent_node.children):
            child_node = parent_node.children[row]
            return self.createIndex(row, column, child_node)

        return QModelIndex()

    def parent(self, index: QModelIndex) -> QModelIndex:
        """Return parent of given index.

        Algorithm:
        1. If index is invalid → return invalid
        2. Get node from index.internalPointer()
        3. If node.parent is None → parent is virtual root (invalid)
        4. Otherwise → create index for parent node
        """
        if not index.isValid():
            return QModelIndex()

        node: TreeNode = index.internalPointer()

        # Root nodes have no parent (virtual root)
        if node.parent is None:
            return QModelIndex()

        # Create index for parent
        parent_node = node.parent
        return self.createIndex(parent_node.row, 0, parent_node)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Return number of rows (children) under parent.

        Algorithm:
        1. If parent is invalid → return number of workspace roots
        2. Get node from parent.internalPointer()
        3. If node is file → return 0
        4. If node is directory:
           - If children not loaded → load them
           - Return len(children)
        """
        # Virtual root → count workspace folders
        if not parent.isValid():
            return len(self._root_nodes)

        # Get node
        node: TreeNode = parent.internalPointer()

        # Files have no children
        if not node.is_dir:
            return 0

        # Directories: load children if needed
        if not node.children_loaded:
            node.load_children(self._should_include_file)

        return len(node.children) if node.children else 0

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Return number of columns (always 1 for tree)."""
        return 1

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Return data for given index and role.

        Roles:
        - DisplayRole: filename
        - DecorationRole: icon (from IconProvider)
        - ToolTipRole: absolute path
        - UserRole: FileInfo object
        - UserRole+1: WorkspaceFolder object (for roots only)
        """
        if not index.isValid():
            return None

        node: TreeNode = index.internalPointer()

        # DisplayRole: filename
        if role == Qt.ItemDataRole.DisplayRole:
            if node.is_root and node.workspace_folder:
                return node.workspace_folder.display_name
            return Path(node.path).name

        # DecorationRole: icon
        elif role == Qt.ItemDataRole.DecorationRole:
            # Get FileInfo (load if needed)
            file_info = self._get_file_info(node)

            if node.is_root and node.workspace_folder:
                # Workspace folder icon
                is_expanded = False  # TODO: track expanded state
                return self._icon_provider.get_workspace_folder_icon(
                    node.workspace_folder, is_expanded
                )
            elif file_info.is_dir:
                # Folder icon
                is_expanded = False  # TODO: track expanded state
                return self._icon_provider.get_folder_icon(file_info, is_expanded)
            else:
                # File icon
                return self._icon_provider.get_file_icon(file_info)

        # ToolTipRole: absolute path
        elif role == Qt.ItemDataRole.ToolTipRole:
            return node.path

        # UserRole: FileInfo
        elif role == Qt.ItemDataRole.UserRole:
            return self._get_file_info(node)

        # UserRole+1: WorkspaceFolder (roots only)
        elif role == Qt.ItemDataRole.UserRole + 1:
            return node.workspace_folder if node.is_root else None

        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        """Return flags for index."""
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        return (
            Qt.ItemFlag.ItemIsEnabled |
            Qt.ItemFlag.ItemIsSelectable
        )

    def hasChildren(self, parent: QModelIndex = QModelIndex()) -> bool:
        """Return True if parent has children.

        Optimization: Return True for directories without loading children.
        """
        # Virtual root always has children (workspace folders)
        if not parent.isValid():
            return len(self._root_nodes) > 0

        node: TreeNode = parent.internalPointer()

        # Files never have children
        if not node.is_dir:
            return False

        # Directories: assume they have children until proven otherwise
        # This avoids loading children just to check count
        if not node.children_loaded:
            return True  # Assume yes, will load when expanded

        # Children loaded: check actual count
        return len(node.children) > 0 if node.children else False

    # =========================================================================
    # Workspace Management
    # =========================================================================

    def set_folders(self, folders: list[WorkspaceFolder]) -> None:
        """Set workspace folders (replace all).

        Algorithm:
        1. beginResetModel()
        2. Clear old watchers
        3. Clear cache
        4. Create new root nodes
        5. Setup watchers for new folders
        6. endResetModel()
        """
        self.beginResetModel()

        # Clear old watchers
        watched_dirs = self._watcher.directories()
        if watched_dirs:
            self._watcher.removePaths(watched_dirs)

        # Clear cache
        self._file_cache.clear()

        # Create root nodes
        self._root_nodes.clear()
        for i, folder in enumerate(folders):
            node = TreeNode(
                path=folder.path,
                parent=None,
                workspace_folder=folder
            )
            node.row = i
            self._root_nodes.append(node)

            # Watch folder for changes
            self._watcher.addPath(folder.path)

        self.endResetModel()

    # =========================================================================
    # Filtering
    # =========================================================================

    def _should_include_file(self, path: Path) -> bool:
        """Determine if file/folder should be included in tree.

        Filter precedence:
        1. Excluded folders (never include)
        2. Hidden files (if show_hidden_files=False)
        3. File extensions (if set)
        4. Custom callback (if set)
        5. All filters must pass (AND logic)
        """
        # Check excluded folders
        if path.is_dir() and path.name in self._excluded_folders:
            return False

        # Check hidden files
        if path.name.startswith('.') and not self._show_hidden_files:
            return False

        # For files: check extension filter
        if path.is_file() and self._file_extensions:
            ext = path.suffix.lower()
            if ext not in self._file_extensions:
                return False

        # Custom callback
        if self._filter_callback and path.is_file():
            # Create FileInfo
            file_info = FileInfo(
                name=path.name,
                relative_path="",  # TODO: compute relative path
                is_dir=path.is_dir(),
                size=path.stat().st_size if path.is_file() else 0,
                modified_time=path.stat().st_mtime
            )

            # Get workspace folder (walk up to root)
            workspace_folder = None  # TODO: determine workspace folder

            if not self._filter_callback(file_info, workspace_folder):
                return False

        return True

    # =========================================================================
    # Filesystem Watching
    # =========================================================================

    def _on_directory_changed(self, path: str) -> None:
        """Handle directory change from QFileSystemWatcher.

        Algorithm:
        1. Find TreeNode for this path
        2. If not found → ignore (not visible in tree)
        3. Mark children as not loaded
        4. Emit dataChanged for this node
        5. If expanded → reload children
        """
        # Find node for this path
        node = self._find_node_by_path(path)
        if not node:
            return  # Not in tree

        # Mark children as stale
        node.children_loaded = False
        node.children = None

        # Get model index for node
        index = self._index_for_node(node)
        if index.isValid():
            self.dataChanged.emit(index, index)

    def _on_file_changed(self, path: str) -> None:
        """Handle file change from QFileSystemWatcher."""
        # Invalidate cache
        if path in self._file_cache:
            del self._file_cache[path]

        # Find node and emit dataChanged
        node = self._find_node_by_path(path)
        if node:
            index = self._index_for_node(node)
            if index.isValid():
                self.dataChanged.emit(index, index)

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _get_file_info(self, node: TreeNode) -> FileInfo:
        """Get FileInfo for node (from cache or filesystem)."""
        if node.path in self._file_cache:
            return self._file_cache[node.path]

        # Load from filesystem
        path = Path(node.path)
        file_info = FileInfo(
            name=path.name,
            relative_path=self._get_relative_path(node),
            is_dir=path.is_dir(),
            size=path.stat().st_size if path.is_file() else 0,
            modified_time=path.stat().st_mtime
        )

        # Cache it
        self._file_cache[node.path] = file_info
        return file_info

    def _find_node_by_path(self, path: str) -> Optional[TreeNode]:
        """Find TreeNode by absolute path (recursive search)."""
        # Check roots
        for root in self._root_nodes:
            if root.path == path:
                return root
            # Recursively search children
            node = self._find_node_in_subtree(root, path)
            if node:
                return node
        return None

    def _find_node_in_subtree(self, node: TreeNode, path: str) -> Optional[TreeNode]:
        """Recursively search subtree for path."""
        if not node.children_loaded or not node.children:
            return None

        for child in node.children:
            if child.path == path:
                return child
            # Recurse
            found = self._find_node_in_subtree(child, path)
            if found:
                return found
        return None

    def _index_for_node(self, node: TreeNode) -> QModelIndex:
        """Create QModelIndex for given node."""
        if node.parent is None:
            # Root node
            return self.createIndex(node.row, 0, node)
        else:
            # Child node
            return self.createIndex(node.row, 0, node)

    def _get_relative_path(self, node: TreeNode) -> str:
        """Get path relative to workspace folder root."""
        # Walk up to root
        parts = []
        current = node
        while current and not current.is_root:
            parts.append(Path(current.path).name)
            current = current.parent

        # Reverse to get path from root down
        parts.reverse()
        return "/".join(parts)
```

### Performance Optimizations

**1. Lazy Loading**
- Children only loaded when node expanded (`hasChildren()` returns True without loading)
- Avoids scanning entire filesystem on workspace open

**2. Caching**
- FileInfo cached by absolute path
- Cache invalidated on filesystem changes
- Typical memory: ~100 bytes per file

**3. Sorted Insertion**
- Children sorted during load (folders first, then alphabetical)
- No sorting needed on display

**4. Row Caching**
- Each node caches its row in parent's children list
- Avoids linear search in `index()` calls

---

## WorkspaceManager Implementation

### Overview

WorkspaceManager handles workspace configuration and session persistence. It:
- Loads/saves workspace configuration (`.workspace.json`)
- Loads/saves UI session state (`~/.config/app/workspaces/sessions/<hash>.json`)
- Manages workspace folder list
- Watches config file for external changes
- Provides workspace lifecycle methods

### Responsibilities

| Responsibility | Description |
|----------------|-------------|
| **Config Management** | Load, save, validate workspace config files |
| **Session Management** | Persist and restore UI state (expanded folders, scroll position) |
| **Folder Management** | Add, remove, rename workspace folders |
| **File Watching** | Detect external changes to config file |
| **Recent Workspaces** | Track and persist recently opened workspaces |

### Class Structure

```python
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

    def __init__(
        self,
        config_class: type = WorkspaceConfig,
        config_filename: str = ".workspace.json",
        session_dir: Optional[Path] = None,
        error_handler: Optional[ErrorHandler] = None,
        validator: Optional[WorkspaceValidator] = None,
        parent: Optional[QObject] = None
    ):
        """Initialize workspace manager.

        Args:
            config_class: Config class (WorkspaceConfig or subclass)
            config_filename: Name of workspace config file
            session_dir: Directory for session files (None = default)
            error_handler: Custom error handler (None = use default)
            validator: Custom workspace validator (None = use default)
            parent: Parent QObject
        """
        super().__init__(parent)

        self._config_class = config_class
        self._config_filename = config_filename
        self._session_dir = session_dir or self._get_default_session_dir()
        self._error_handler = error_handler
        self._validator = validator

        # State
        self._folders: list[WorkspaceFolder] = []
        self._config: Optional[WorkspaceConfig] = None
        self._workspace_path: Optional[Path] = None

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
            ConfigError: If config file is corrupt
            ValidationError: If workspace fails validation
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
                        context={"config_path": str(config_path)}
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

        # Watch config file if it exists
        if config_path.exists():
            self._config_watcher.addPath(str(config_path))

        # Add to recent workspaces
        self.add_recent_workspace(
            str(folder_path),
            config.name or folder_path.name,
            len(config.folders)
        )

        # Emit signal
        self.workspace_opened.emit(self._folders)
        return self._folders

    def close_workspace(self) -> None:
        """Close current workspace."""
        if not self._workspace_path:
            return

        # Stop watching config file
        config_path = self._workspace_path / self._config_filename
        if str(config_path) in self._config_watcher.files():
            self._config_watcher.removePath(str(config_path))

        # Clear state
        self._folders.clear()
        self._config = None
        self._workspace_path = None

        # Emit signal
        self.workspace_closed.emit()

    def add_folder(self, folder_path: Path, name: Optional[str] = None) -> WorkspaceFolder:
        """Add folder to workspace.

        Args:
            folder_path: Path to folder to add
            name: Optional display name (default: folder name)

        Returns:
            The added WorkspaceFolder

        Raises:
            ValueError: If workspace not open or folder already exists
        """
        if not self._config:
            raise ValueError("No workspace open")

        # Check if already exists
        for folder in self._folders:
            if folder.path == str(folder_path):
                raise ValueError(f"Folder already in workspace: {folder_path}")

        # Create WorkspaceFolder
        workspace_folder = WorkspaceFolder(
            path=str(folder_path),
            name=name or folder_path.name
        )

        # Add to list
        self._folders.append(workspace_folder)
        self._config.folders = self._folders

        # Save config
        self.save_config()

        # Emit signal
        self.folder_added.emit(workspace_folder)
        return workspace_folder

    def remove_folder(self, folder_path: str) -> bool:
        """Remove folder from workspace.

        Args:
            folder_path: Path to folder to remove

        Returns:
            True if removed, False if not found
        """
        if not self._config:
            return False

        # Find and remove
        for i, folder in enumerate(self._folders):
            if folder.path == folder_path:
                removed = self._folders.pop(i)
                self._config.folders = self._folders

                # Save config
                self.save_config()

                # Emit signal
                self.folder_removed.emit(folder_path)
                return True

        return False

    def rename_folder(self, folder_path: str, new_name: str) -> bool:
        """Set custom display name for a folder.

        Args:
            folder_path: Path to folder
            new_name: New display name

        Returns:
            True if renamed, False if not found
        """
        if not self._config:
            return False

        # Find and rename
        for folder in self._folders:
            if folder.path == folder_path:
                folder.name = new_name
                self._config.folders = self._folders

                # Save config
                self.save_config()
                return True

        return False

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
            json.JSONDecodeError: If config is corrupt
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Convert to config class
        return self._config_class.from_dict(data)

    def save_config(self) -> None:
        """Save current config to file.

        Handles file watching to avoid triggering fileChanged signal.
        """
        if not self._workspace_path or not self._config:
            return

        config_path = self._workspace_path / self._config_filename

        # Temporarily remove from watcher (avoid triggering fileChanged)
        if str(config_path) in self._config_watcher.files():
            self._config_watcher.removePath(str(config_path))

        try:
            # Ensure directory exists
            config_path.parent.mkdir(parents=True, exist_ok=True)

            # Write config
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config.to_dict(), f, indent=2, ensure_ascii=False)

        except OSError as e:
            if self._error_handler:
                self._error_handler.handle_error(
                    ErrorSeverity.ERROR,
                    f"Failed to save config: {e}",
                    exception=e,
                    context={"config_path": str(config_path)}
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
                    exception=e
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
            with open(session_path, 'r', encoding='utf-8') as f:
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
            with open(session_path, 'w', encoding='utf-8') as f:
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
        import hashlib
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

    def add_recent_workspace(
        self,
        workspace_path: str,
        name: str,
        folder_count: int
    ) -> None:
        """Add workspace to recent list.

        Args:
            workspace_path: Absolute path to workspace
            name: Workspace name
            folder_count: Number of folders in workspace
        """
        recent = self._load_recent_workspaces()

        # Create entry
        from datetime import datetime
        entry = {
            "path": workspace_path,
            "name": name,
            "folder_count": folder_count,
            "last_opened": datetime.now().isoformat()
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
            with open(self._recent_workspaces_file, 'r', encoding='utf-8') as f:
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
            with open(self._recent_workspaces_file, 'w', encoding='utf-8') as f:
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
```

### Config File Format

**Example `.workspace.json`:**

```json
{
  "version": 1,
  "name": "My Project",
  "folders": [
    {
      "path": "/home/user/project",
      "name": "Main Project"
    },
    {
      "path": "/home/user/shared-lib",
      "name": "Shared Library"
    }
  ],
  "excluded_folders": [
    "node_modules",
    ".git",
    "__pycache__"
  ],
  "custom_data": {
    "app_specific_field": "value"
  }
}
```

### Session File Format

**Example session file (`~/.config/vfwidgets/workspaces/sessions/a1b2c3d4e5f6g7h8.json`):**

```json
{
  "workspace_name": "My Project",
  "last_opened": "2025-10-24T14:30:00",
  "expanded_folders": [
    "/home/user/project/src",
    "/home/user/project/src/components",
    "/home/user/shared-lib"
  ],
  "scroll_position": 150,
  "active_file": "/home/user/project/src/main.py"
}
```

### Error Handling

```python
# Example error scenarios and handling:

# 1. Corrupt config file
try:
    config = manager.load_config(config_path)
except json.JSONDecodeError:
    # Fallback to default config
    config = WorkspaceConfig.from_folder(folder_path)
    logger.warning("Config corrupt, using defaults")

# 2. Disk full when saving
try:
    manager.save_config()
except OSError as e:
    if e.errno == errno.ENOSPC:
        # Disk full - keep config in memory, warn user
        error_handler.handle_error(
            ErrorSeverity.CRITICAL,
            "Disk full - cannot save config",
            exception=e
        )

# 3. Permission denied
try:
    session = manager.load_session(workspace_path)
except PermissionError:
    # Can't read session - use defaults
    session = None
    logger.warning("Session file not readable")
```

---

## FileExplorerWidget Implementation

### Overview

FileExplorerWidget is the view component that displays the workspace tree. It:
- Wraps QTreeView with theming support
- Forwards user interactions as signals
- Tracks expanded/collapsed state for icon updates
- Provides context menu integration

### Class Structure

```python
# Check if theme system available
try:
    from vfwidgets_theme import ThemedWidget
    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False
    ThemedWidget = object  # type: ignore

# Conditional base class (ThemedWidget if available, else QWidget)
if THEME_AVAILABLE:
    _BaseClass = type("_BaseClass", (ThemedWidget, QWidget), {})
else:
    _BaseClass = QWidget

class FileExplorerWidget(_BaseClass):
    """File tree view with automatic theme integration.

    Responsibilities:
    - Display QTreeView with workspace model
    - Track expanded/collapsed state
    - Forward user interactions as signals
    - Apply theme colors via ThemedWidget
    """

    # Theme configuration (VS Code sidebar colors)
    theme_config = {
        # Container
        "background": "sideBar.background",
        "foreground": "sideBar.foreground",

        # List selection
        "selection_bg": "list.activeSelectionBackground",
        "selection_fg": "list.activeSelectionForeground",
        "inactive_selection_bg": "list.inactiveSelectionBackground",
        "hover_bg": "list.hoverBackground",

        # Tree guides
        "indent_guide": "tree.indentGuidesStroke",

        # Icons
        "icon_fg": "icon.foreground",
    }

    # Signals
    file_selected = Signal(str)  # absolute_path
    file_double_clicked = Signal(str)  # absolute_path
    folder_expanded = Signal(str, str)  # folder_path, workspace_folder_path
    folder_collapsed = Signal(str, str)  # folder_path, workspace_folder_path
    context_menu_requested = Signal(QPoint, object, object)  # position, item, workspace_folder

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Expanded state tracking
        self._expanded_paths: set[str] = set()

        # Setup UI
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup tree view and layout."""
        # Create tree view
        self._tree_view = QTreeView(self)
        self._tree_view.setHeaderHidden(True)
        self._tree_view.setUniformRowHeights(True)
        self._tree_view.setAnimated(False)  # Performance: disable animation
        self._tree_view.setIndentation(20)
        self._tree_view.setExpandsOnDoubleClick(False)  # We handle double-click for file opening

        # Selection behavior
        self._tree_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._tree_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        # Connect signals
        self._tree_view.clicked.connect(self._on_clicked)
        self._tree_view.doubleClicked.connect(self._on_double_clicked)
        self._tree_view.expanded.connect(self._on_expanded)
        self._tree_view.collapsed.connect(self._on_collapsed)

        # Context menu
        self._tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree_view.customContextMenuRequested.connect(self._on_context_menu)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._tree_view)

        # Apply theme if available
        if THEME_AVAILABLE:
            # ThemedWidget will automatically apply colors via theme_config
            pass
        else:
            # Fallback to hardcoded dark theme
            self._apply_fallback_theme()

    def _apply_fallback_theme(self) -> None:
        """Fallback theme when vfwidgets-theme not available."""
        self._tree_view.setStyleSheet("""
            QTreeView {
                background-color: #252526;
                color: #cccccc;
                border: none;
                outline: none;
            }
            QTreeView::item {
                padding: 4px;
                border-radius: 2px;
            }
            QTreeView::item:hover {
                background-color: #2a2d2e;
            }
            QTreeView::item:selected:active {
                background-color: #094771;
                color: #ffffff;
            }
            QTreeView::item:selected:!active {
                background-color: #37373d;
                color: #cccccc;
            }
        """)

    def theme_changed(self) -> None:
        """Called by ThemedWidget when theme changes.

        Override to apply theme colors to QTreeView via stylesheet.
        """
        if not THEME_AVAILABLE:
            return

        # Get theme colors
        bg = self.get_theme_color("background")
        fg = self.get_theme_color("foreground")
        sel_bg = self.get_theme_color("selection_bg")
        sel_fg = self.get_theme_color("selection_fg")
        inactive_sel_bg = self.get_theme_color("inactive_selection_bg")
        hover_bg = self.get_theme_color("hover_bg")

        # Apply via stylesheet (QTreeView doesn't support Qt properties for all features)
        stylesheet = f"""
            QTreeView {{
                background-color: {bg};
                color: {fg};
                border: none;
                outline: none;
            }}
            QTreeView::item {{
                padding: 4px;
                border-radius: 2px;
            }}
            QTreeView::item:hover {{
                background-color: {hover_bg};
            }}
            QTreeView::item:selected:active {{
                background-color: {sel_bg};
                color: {sel_fg};
            }}
            QTreeView::item:selected:!active {{
                background-color: {inactive_sel_bg};
            }}
        """
        self._tree_view.setStyleSheet(stylesheet)

    def set_model(self, model: QAbstractItemModel) -> None:
        """Set the tree model.

        Args:
            model: MultiRootFileSystemModel instance
        """
        self._tree_view.setModel(model)

    def _on_clicked(self, index: QModelIndex) -> None:
        """Handle single click on item."""
        if not index.isValid():
            return

        # Get file info from model
        file_info: FileInfo = index.data(Qt.ItemDataRole.UserRole)
        if file_info and not file_info.is_dir:
            # File clicked - emit selection signal
            self.file_selected.emit(file_info.absolute_path)

    def _on_double_clicked(self, index: QModelIndex) -> None:
        """Handle double click on item."""
        if not index.isValid():
            return

        # Get file info from model
        file_info: FileInfo = index.data(Qt.ItemDataRole.UserRole)

        if file_info and not file_info.is_dir:
            # File double-clicked - emit open signal
            self.file_double_clicked.emit(file_info.absolute_path)
        elif file_info and file_info.is_dir:
            # Folder double-clicked - toggle expansion
            if self._tree_view.isExpanded(index):
                self._tree_view.collapse(index)
            else:
                self._tree_view.expand(index)

    def _on_expanded(self, index: QModelIndex) -> None:
        """Track when node expanded."""
        if not index.isValid():
            return

        node: TreeNode = index.internalPointer()
        if not node:
            return

        # Track expanded state
        self._expanded_paths.add(node.path)

        # Notify model to update expanded state for icon
        model = self._tree_view.model()
        if hasattr(model, 'set_expanded'):
            model.set_expanded(node.path, True)

        # Get workspace folder
        workspace_folder = node.get_workspace_folder()
        workspace_folder_path = workspace_folder.path if workspace_folder else ""

        # Emit signal
        self.folder_expanded.emit(node.path, workspace_folder_path)

    def _on_collapsed(self, index: QModelIndex) -> None:
        """Track when node collapsed."""
        if not index.isValid():
            return

        node: TreeNode = index.internalPointer()
        if not node:
            return

        # Track collapsed state
        self._expanded_paths.discard(node.path)

        # Notify model to update expanded state for icon
        model = self._tree_view.model()
        if hasattr(model, 'set_expanded'):
            model.set_expanded(node.path, False)

        # Get workspace folder
        workspace_folder = node.get_workspace_folder()
        workspace_folder_path = workspace_folder.path if workspace_folder else ""

        # Emit signal
        self.folder_collapsed.emit(node.path, workspace_folder_path)

    def _on_context_menu(self, position: QPoint) -> None:
        """Handle context menu request."""
        # Get item at position
        index = self._tree_view.indexAt(position)
        if not index.isValid():
            return

        # Get item data
        node: TreeNode = index.internalPointer()
        if not node:
            return

        file_info: FileInfo = index.data(Qt.ItemDataRole.UserRole)
        workspace_folder: WorkspaceFolder = index.data(Qt.ItemDataRole.UserRole + 1)

        # Emit signal for parent widget to handle
        global_pos = self.mapToGlobal(position)
        self.context_menu_requested.emit(global_pos, file_info or node, workspace_folder)

    def is_expanded(self, path: str) -> bool:
        """Check if path is currently expanded.

        Args:
            path: Absolute path to check

        Returns:
            True if path is expanded, False otherwise
        """
        return path in self._expanded_paths

    def expand_path(self, path: str) -> bool:
        """Expand folder at path.

        Args:
            path: Absolute path to folder

        Returns:
            True if successful, False if path not found
        """
        # Find index for path
        index = self._find_index_by_path(path)
        if not index.isValid():
            return False

        self._tree_view.expand(index)
        return True

    def collapse_path(self, path: str) -> bool:
        """Collapse folder at path.

        Args:
            path: Absolute path to folder

        Returns:
            True if successful, False if path not found
        """
        # Find index for path
        index = self._find_index_by_path(path)
        if not index.isValid():
            return False

        self._tree_view.collapse(index)
        return True

    def scroll_to(self, path: str) -> bool:
        """Scroll to make path visible.

        Args:
            path: Absolute path to scroll to

        Returns:
            True if successful, False if path not found
        """
        index = self._find_index_by_path(path)
        if not index.isValid():
            return False

        self._tree_view.scrollTo(index, QAbstractItemView.ScrollHint.PositionAtCenter)
        return True

    def select_path(self, path: str) -> bool:
        """Select item at path.

        Args:
            path: Absolute path to select

        Returns:
            True if successful, False if path not found
        """
        index = self._find_index_by_path(path)
        if not index.isValid():
            return False

        self._tree_view.setCurrentIndex(index)
        return True

    def _find_index_by_path(self, path: str) -> QModelIndex:
        """Find model index for absolute file path.

        Args:
            path: Absolute path to find

        Returns:
            QModelIndex for path, or invalid index if not found
        """
        model = self._tree_view.model()
        if not model:
            return QModelIndex()

        # Helper to recursively search tree
        def search_subtree(parent_index: QModelIndex) -> Optional[QModelIndex]:
            for row in range(model.rowCount(parent_index)):
                index = model.index(row, 0, parent_index)
                node: TreeNode = index.internalPointer()

                if node and node.path == path:
                    return index

                # Recurse into children if loaded
                if node and node.children_loaded and node.children:
                    result = search_subtree(index)
                    if result and result.isValid():
                        return result

            return None

        # Search from root
        return search_subtree(QModelIndex()) or QModelIndex()
```

### Integration with Model

The FileExplorerWidget communicates expanded state changes to the Model:

```python
# In MultiRootFileSystemModel:
class MultiRootFileSystemModel(QAbstractItemModel):
    def __init__(self, ...):
        ...
        self._expanded_paths: set[str] = set()

    def set_expanded(self, path: str, expanded: bool) -> None:
        """Called by view when node expanded/collapsed.

        Updates expanded state and refreshes icon.
        """
        if expanded:
            self._expanded_paths.add(path)
        else:
            self._expanded_paths.discard(path)

        # Find node and emit dataChanged for icon update
        node = self._find_node_by_path(path)
        if node:
            index = self._index_for_node(node)
            if index.isValid():
                self.dataChanged.emit(index, index, [Qt.ItemDataRole.DecorationRole])

    def is_expanded(self, path: str) -> bool:
        """Check if path is expanded (for icon selection)."""
        return path in self._expanded_paths

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Return data for given index and role."""
        if not index.isValid():
            return None

        node: TreeNode = index.internalPointer()

        # ... existing roles ...

        # DecorationRole: icon
        elif role == Qt.ItemDataRole.DecorationRole:
            file_info = self._get_file_info(node)

            if node.is_root and node.workspace_folder:
                # Workspace folder icon
                is_expanded = self.is_expanded(node.path)
                return self._icon_provider.get_workspace_folder_icon(
                    node.workspace_folder, is_expanded
                )
            elif file_info.is_dir:
                # Folder icon
                is_expanded = self.is_expanded(node.path)
                return self._icon_provider.get_folder_icon(file_info, is_expanded)
            else:
                # File icon
                return self._icon_provider.get_file_icon(file_info)

        # ... rest of roles ...
```

---

## WorkspaceWidget Convenience Methods Implementation

This section covers the implementation of high-level convenience methods in WorkspaceWidget that provide advanced features like session management, file navigation, tab synchronization, and fuzzy file search.

### Overview

WorkspaceWidget acts as a facade that orchestrates Model, Manager, and View. These convenience methods provide:
- Session save/restore for UI state persistence
- File navigation (reveal, highlight, find)
- Tab widget integration
- User-friendly helper methods

### Session Save/Restore Implementation

**Purpose:** Persist and restore UI state (expanded folders, scroll position, active file) across application restarts.

**Key Challenge:** Collecting UI state from QTreeView and restoring it correctly.

#### Collecting UI State

```python
class WorkspaceWidget(QWidget):
    def save_session(self) -> WorkspaceSession:
        """Collect current UI state into a session object.

        Returns:
            WorkspaceSession with current state

        Implementation Note:
            - Recursively walks tree to find expanded nodes
            - Gets scroll position from QTreeView's vertical scrollbar
            - Active file tracked separately
        """
        # Get expanded folders
        expanded_folders = []
        model = self._explorer._tree_view.model()

        def collect_expanded(parent_index: QModelIndex) -> None:
            """Recursively collect expanded folder paths."""
            for row in range(model.rowCount(parent_index)):
                index = model.index(row, 0, parent_index)

                # Check if expanded
                if self._explorer._tree_view.isExpanded(index):
                    node: TreeNode = index.internalPointer()
                    if node:
                        expanded_folders.append(node.path)

                    # Recurse into children
                    collect_expanded(index)

        # Start from root
        collect_expanded(QModelIndex())

        # Get scroll position
        scrollbar = self._explorer._tree_view.verticalScrollBar()
        scroll_position = scrollbar.value()

        # Create session
        from datetime import datetime
        return WorkspaceSession(
            workspace_name=self._current_workspace_path.name if self._current_workspace_path else "",
            last_opened=datetime.now().isoformat(),
            expanded_folders=expanded_folders,
            scroll_position=scroll_position,
            active_file=self._active_file_path
        )
```

#### Restoring UI State

```python
    def restore_session(self, session: WorkspaceSession) -> None:
        """Restore UI state from session.

        Args:
            session: Session to restore

        Implementation Note:
            - Expands folders by finding their QModelIndex
            - Uses QTimer for scroll restoration (must wait for layout)
            - Highlights active file last
        """
        model = self._explorer._tree_view.model()

        # Expand folders
        for folder_path in session.expanded_folders:
            # Find index for this path
            index = self._find_index_by_path(folder_path)
            if index.isValid():
                # Expand this folder
                self._explorer._tree_view.expand(index)

        # Restore scroll position (delayed to allow tree layout)
        # QTimer needed because expand() doesn't immediately update layout
        QTimer.singleShot(100, lambda: self._restore_scroll(session.scroll_position))

        # Restore active file
        if session.active_file:
            self.highlight_file(session.active_file)

    def _restore_scroll(self, position: int) -> None:
        """Helper to restore scroll position.

        Args:
            position: Vertical scroll position (pixels)
        """
        scrollbar = self._explorer._tree_view.verticalScrollBar()
        scrollbar.setValue(position)
```

#### Integration with Open/Close

```python
    def open_workspace(self, folder_path: Path) -> bool:
        """Open workspace (enhanced with session restore)."""
        # ... existing open logic ...

        # After workspace opened successfully
        if success:
            # Load session
            session = self._manager.load_session(folder_path)
            if session:
                # Restore UI state
                self.restore_session(session)

        return success

    def close_workspace(self) -> None:
        """Close workspace (enhanced with session save)."""
        if self._current_workspace_path:
            # Save session before closing
            session = self.save_session()
            self._manager.save_session(session)

        # ... existing close logic ...
```

---

### File Navigation Implementation

**Purpose:** Provide methods to programmatically navigate to files in the tree (reveal, highlight, find).

#### Finding QModelIndex by Path

```python
    def _find_index_by_path(self, file_path: str) -> QModelIndex:
        """Find QModelIndex for absolute file path.

        Args:
            file_path: Absolute path to file or folder

        Returns:
            QModelIndex for file, or invalid index if not found

        Algorithm:
            1. Determine which workspace folder contains the file
            2. Get relative path from workspace root
            3. Walk down tree following path components
            4. Return index of final component
        """
        file_path_obj = Path(file_path)

        # Find workspace folder that contains this path
        workspace_folder = None
        for folder in self._manager.get_folders():
            folder_path = Path(folder.path)
            try:
                # Check if file_path is under folder_path
                file_path_obj.relative_to(folder_path)
                workspace_folder = folder
                break
            except ValueError:
                # Not a relative path
                continue

        if not workspace_folder:
            return QModelIndex()  # File not in any workspace folder

        # Get relative path components
        rel_path = file_path_obj.relative_to(workspace_folder.path)
        components = rel_path.parts  # ('src', 'main.py')

        # Get model
        model = self._explorer._tree_view.model()
        current_index = QModelIndex()

        # Find workspace folder root index
        for row in range(model.rowCount(current_index)):
            index = model.index(row, 0, current_index)
            node: TreeNode = index.internalPointer()
            if node and node.workspace_folder == workspace_folder:
                current_index = index
                break

        if not current_index.isValid():
            return QModelIndex()  # Workspace folder not found

        # Walk down path components
        for component in components:
            found = False

            # Ensure children loaded (lazy loading)
            if model.canFetchMore(current_index):
                model.fetchMore(current_index)

            # Search children for matching component
            for row in range(model.rowCount(current_index)):
                child_index = model.index(row, 0, current_index)
                display_name = child_index.data(Qt.ItemDataRole.DisplayRole)

                if display_name == component:
                    current_index = child_index
                    found = True
                    break

            if not found:
                return QModelIndex()  # Component not found

        return current_index
```

#### Reveal File

```python
    def reveal_file(self, file_path: str) -> bool:
        """Reveal file in tree (expand parents, scroll to view, select).

        Args:
            file_path: Absolute path to file

        Returns:
            True if file found and revealed, False otherwise

        Side Effects:
            - Expands all parent folders
            - Scrolls tree to make file visible
            - Selects file in tree
            - Emits active_file_changed signal
        """
        # Find model index for file
        index = self._find_index_by_path(file_path)

        if not index.isValid():
            return False

        # Expand all parent folders
        parent = index.parent()
        while parent.isValid():
            self._explorer._tree_view.expand(parent)
            parent = parent.parent()

        # Scroll to make visible (centered in view)
        self._explorer._tree_view.scrollTo(
            index,
            QAbstractItemView.ScrollHint.PositionAtCenter
        )

        # Select item
        self._explorer._tree_view.setCurrentIndex(index)

        # Update active file tracking
        self._active_file_path = file_path

        # Emit signal
        self.active_file_changed.emit(file_path)

        return True
```

#### Highlight File

```python
    def highlight_file(self, file_path: str) -> bool:
        """Highlight file in tree (select without expanding parents).

        Args:
            file_path: Absolute path to file

        Returns:
            True if file found and highlighted, False otherwise

        Note:
            Unlike reveal_file(), this does NOT expand parent folders.
            Use this when parents are already expanded (e.g., session restore).
        """
        index = self._find_index_by_path(file_path)

        if not index.isValid():
            return False

        # Select without expanding
        self._explorer._tree_view.setCurrentIndex(index)
        self._active_file_path = file_path

        return True
```

---

### Tab Widget Synchronization

**Purpose:** Auto-sync workspace selection with tab widget (when tab changes, highlight file in workspace).

```python
    def sync_with_tab_widget(
        self,
        tab_widget: QTabWidget,
        file_path_attr: str = "file_path",
        auto_sync: bool = True
    ) -> None:
        """Enable automatic synchronization with a tab widget.

        Args:
            tab_widget: Tab widget to sync with
            file_path_attr: Attribute name on tab widgets containing file path
            auto_sync: If True, automatically highlight file when tab changes

        Usage:
            # Assuming each tab widget has a .file_path attribute
            workspace.sync_with_tab_widget(my_tab_widget)

            # Now when user switches tabs, workspace automatically highlights that file
        """
        self._synced_tab_widget = tab_widget
        self._tab_file_path_attr = file_path_attr

        if auto_sync:
            # Connect to tab change signal
            tab_widget.currentChanged.connect(self._on_synced_tab_changed)

    def _on_synced_tab_changed(self, tab_index: int) -> None:
        """Handle tab change in synced tab widget.

        Args:
            tab_index: Index of newly selected tab
        """
        if not hasattr(self, '_synced_tab_widget'):
            return

        # Get widget for this tab
        widget = self._synced_tab_widget.widget(tab_index)
        if not widget:
            return

        # Get file path from widget
        if hasattr(widget, self._tab_file_path_attr):
            file_path = getattr(widget, self._tab_file_path_attr)

            if file_path:
                # Highlight in workspace (don't reveal - too disruptive)
                self.highlight_file(str(file_path))
```

---

### Fuzzy File Search

**Purpose:** Find files by name with optional fuzzy matching (useful for "Quick Open" features).

```python
    def find_file(self, filename: str, fuzzy: bool = False) -> list[str]:
        """Find files by name.

        Args:
            filename: File name to search for (case-insensitive)
            fuzzy: If True, use fuzzy matching; if False, exact match

        Returns:
            List of absolute file paths matching the search

        Fuzzy Matching Algorithm:
            All characters in search string must appear in order in the filename.
            Example: "mdc" matches "MainDocController.py"
        """
        results = []
        all_files = self.get_all_files()

        if fuzzy:
            # Fuzzy matching: all characters must appear in order
            filename_lower = filename.lower()

            for file_path in all_files:
                file_name = Path(file_path).name.lower()

                # Check if all search characters appear in order
                search_idx = 0
                for char in file_name:
                    if search_idx < len(filename_lower) and char == filename_lower[search_idx]:
                        search_idx += 1

                # Match if all search characters found
                if search_idx == len(filename_lower):
                    results.append(file_path)
        else:
            # Exact match (case-insensitive)
            filename_lower = filename.lower()

            for file_path in all_files:
                if Path(file_path).name.lower() == filename_lower:
                    results.append(file_path)

        return results

    def get_all_files(self) -> list[str]:
        """Get list of all files in workspace (recursive).

        Returns:
            List of absolute file paths

        Implementation:
            Walks the tree model recursively collecting all file paths.
            Includes files from all workspace folders.
        """
        files = []
        model = self._explorer._tree_view.model()

        def collect_files(parent_index: QModelIndex) -> None:
            """Recursively collect file paths."""
            for row in range(model.rowCount(parent_index)):
                index = model.index(row, 0, parent_index)
                node: TreeNode = index.internalPointer()

                if node:
                    file_info = model._get_file_info(node)

                    if file_info.is_dir:
                        # Recurse into directory
                        # Ensure children loaded
                        if model.canFetchMore(index):
                            model.fetchMore(index)
                        collect_files(index)
                    else:
                        # Add file
                        files.append(node.path)

        # Start from root
        collect_files(QModelIndex())

        return files
```

---

### Additional Helper Methods

```python
    def refresh(self) -> None:
        """Refresh workspace file tree (reload from disk).

        Preserves:
            - Current workspace folders
            - Expanded state (best effort)

        Use Case:
            External file system changes not caught by QFileSystemWatcher
        """
        # Get current expanded paths
        expanded_paths = []
        for folder_path in self._collect_expanded_paths():
            expanded_paths.append(folder_path)

        # Reload model
        self._model.refresh()

        # Restore expanded state
        for folder_path in expanded_paths:
            index = self._find_index_by_path(folder_path)
            if index.isValid():
                self._explorer._tree_view.expand(index)

    def _collect_expanded_paths(self) -> list[str]:
        """Collect currently expanded folder paths."""
        expanded = []
        model = self._explorer._tree_view.model()

        def collect(parent_index: QModelIndex) -> None:
            for row in range(model.rowCount(parent_index)):
                index = model.index(row, 0, parent_index)
                if self._explorer._tree_view.isExpanded(index):
                    node: TreeNode = index.internalPointer()
                    if node:
                        expanded.append(node.path)
                    collect(index)

        collect(QModelIndex())
        return expanded

    def reveal_in_file_manager(self, file_path: str) -> bool:
        """Open file manager and select the file.

        Args:
            file_path: Absolute path to file

        Returns:
            True if file manager opened successfully

        Implementation:
            Platform-specific commands:
            - Linux: xdg-open (Nautilus, Dolphin, etc.)
            - macOS: open -R
            - Windows: explorer /select
        """
        import subprocess
        import sys

        try:
            if sys.platform == 'win32':
                subprocess.run(['explorer', '/select,', file_path])
            elif sys.platform == 'darwin':
                subprocess.run(['open', '-R', file_path])
            else:
                # Linux - xdg-open opens folder, not file
                folder = str(Path(file_path).parent)
                subprocess.run(['xdg-open', folder])

            return True
        except Exception as e:
            logger.error(f"Failed to open file manager: {e}")
            return False
```

---

## Sequence Diagrams

### 1. Open Workspace

```
User                WorkspaceWidget      LifecycleHooks    Validator       Manager         Model           View
 │                        │                    │              │              │              │              │
 │ open_workspace(path)   │                    │              │              │              │              │
 ├───────────────────────>│                    │              │              │              │              │
 │                        │                    │              │              │              │              │
 │                        │ before_workspace_open(path)       │              │              │              │
 │                        ├───────────────────>│              │              │              │              │
 │                        │                    │              │              │              │              │
 │                        │ True/False         │              │              │              │              │
 │                        │<───────────────────┤              │              │              │              │
 │                        │                    │              │              │              │              │
 │                        │ [if False]         │              │              │              │              │
 │<───────False───────────┤                    │              │              │              │              │
 │                        │                    │              │              │              │              │
 │                        │ [if True]          │              │              │              │              │
 │                        │ validate_workspace_folder(path)   │              │              │              │
 │                        ├──────────────────────────────────>│              │              │              │
 │                        │                    │              │              │              │              │
 │                        │ ValidationResult   │              │              │              │              │
 │                        │<──────────────────────────────────┤              │              │              │
 │                        │                    │              │              │              │              │
 │                        │ [if !valid]        │              │              │              │              │
 │<───────False───────────┤                    │              │              │              │              │
 │                        │                    │              │              │              │              │
 │                        │ [if valid]         │              │              │              │              │
 │                        │ open_workspace(path)              │              │              │              │
 │                        ├───────────────────────────────────┼─────────────>│              │              │
 │                        │                    │              │              │              │              │
 │                        │                    │              │              │ load_config()│              │
 │                        │                    │              │              ├─────────────>│              │
 │                        │                    │              │              │              │              │
 │                        │                    │              │              │ WorkspaceConfig             │
 │                        │                    │              │              │<─────────────┤              │
 │                        │                    │              │              │              │              │
 │                        │                    │              │              │ create folders list         │
 │                        │                    │              │              ├─────────────>│              │
 │                        │                    │              │              │              │              │
 │                        │ folders            │              │              │              │              │
 │                        │<───────────────────────────────────┼──────────────┤              │              │
 │                        │                    │              │              │              │              │
 │                        │ set_folders(folders)              │              │              │              │
 │                        ├───────────────────────────────────┼──────────────┼─────────────>│              │
 │                        │                    │              │              │              │              │
 │                        │                    │              │              │              │ beginResetModel()
 │                        │                    │              │              │              ├─────────────>│
 │                        │                    │              │              │              │              │
 │                        │                    │              │              │              │ create TreeNodes
 │                        │                    │              │              │              ├─────────────>│
 │                        │                    │              │              │              │              │
 │                        │                    │              │              │              │ endResetModel()
 │                        │                    │              │              │              ├─────────────>│
 │                        │                    │              │              │              │              │
 │                        │                    │              │              │              │ refresh tree │
 │                        │                    │              │              │              │<─────────────┤
 │                        │                    │              │              │              │              │
 │                        │ load_session()     │              │              │              │              │
 │                        ├───────────────────────────────────┼─────────────>│              │              │
 │                        │                    │              │              │              │              │
 │                        │ WorkspaceSession   │              │              │              │              │
 │                        │<───────────────────────────────────┼──────────────┤              │              │
 │                        │                    │              │              │              │              │
 │                        │ restore_session(session)          │              │              │              │
 │                        ├───────────────────────────────────┼──────────────┼──────────────┼─────────────>│
 │                        │                    │              │              │              │              │
 │                        │                    │              │              │              │ expand folders
 │                        │                    │              │              │              │ scroll to pos
 │                        │                    │              │              │              │<─────────────┤
 │                        │                    │              │              │              │              │
 │                        │ after_workspace_opened(folders)   │              │              │              │
 │                        ├───────────────────>│              │              │              │              │
 │                        │                    │              │              │              │              │
 │                        │ workspace_opened.emit(folders)    │              │              │              │
 │                        ├───────────────────────────────────┼──────────────┼──────────────┼─────────────>│
 │                        │                    │              │              │              │              │
 │<───────True────────────┤                    │              │              │              │              │
 │                        │                    │              │              │              │              │
```

**Key Points:**
1. Lifecycle hooks can cancel operation (return False)
2. Validation happens before loading config
3. Model reset triggers view refresh automatically
4. Session restored after model populated
5. Signals emitted last (after everything succeeds)

### 2. File Modified Externally

```
QFileSystemWatcher    Model          WorkspaceWidget   ConflictHandler    App
      │                  │                  │                  │            │
      │ fileChanged(path)│                  │                  │            │
      ├─────────────────>│                  │                  │            │
      │                  │                  │                  │            │
      │                  │ _on_file_changed()                  │            │
      │                  ├─────────────────>│                  │            │
      │                  │                  │                  │            │
      │                  │ invalidate cache │                  │            │
      │                  │<─────────────────┤                  │            │
      │                  │                  │                  │            │
      │                  │ check if file exists               │            │
      │                  ├─────────────────>│                  │            │
      │                  │                  │                  │            │
      │                  │ [if deleted]     │                  │            │
      │                  │ handle_file_deleted(path, ws_folder)            │
      │                  ├─────────────────────────────────────>│            │
      │                  │                  │                  │            │
      │                  │                  │  FileConflictAction.CLOSE    │
      │                  │<─────────────────────────────────────┤            │
      │                  │                  │                  │            │
      │                  │ file_deleted.emit(path, ws_folder)  │            │
      │                  ├─────────────────────────────────────┼───────────>│
      │                  │                  │                  │            │
      │                  │ file_close_requested.emit(path)     │            │
      │                  ├─────────────────────────────────────┼───────────>│
      │                  │                  │                  │            │
      │                  │                  │                  │  close_tab(path)
      │                  │                  │                  │<───────────┤
      │                  │                  │                  │            │
      │                  │ [if modified]    │                  │            │
      │                  │ handle_file_modified(path, ws_folder)           │
      │                  ├─────────────────────────────────────>│            │
      │                  │                  │                  │            │
      │                  │                  │  FileConflictAction.PROMPT_RELOAD
      │                  │<─────────────────────────────────────┤            │
      │                  │                  │                  │            │
      │                  │ file_modified.emit(path, ws_folder) │            │
      │                  ├─────────────────────────────────────┼───────────>│
      │                  │                  │                  │            │
      │                  │ file_reload_prompt_requested.emit(path)          │
      │                  ├─────────────────────────────────────┼───────────>│
      │                  │                  │                  │            │
      │                  │                  │                  │  show_reload_dialog()
      │                  │                  │                  │<───────────┤
      │                  │                  │                  │            │
      │                  │                  │                  │  [user: Yes]
      │                  │                  │                  │  reload_file(path)
      │                  │                  │                  │<───────────┤
      │                  │                  │                  │            │
```

**Key Points:**
1. QFileSystemWatcher runs in separate thread (Qt handles this)
2. Model detects change, delegates to ConflictHandler
3. Handler returns action (RELOAD, PROMPT_RELOAD, IGNORE, CLOSE, SHOW_DIFF)
4. Widget emits signals for app to handle actual action
5. Widget only detects and coordinates - app does the work

### 3. Add Folder to Workspace

```
User           WorkspaceWidget    LifecycleHooks   Validator     Manager       Model          View
 │                    │                  │              │            │            │             │
 │ add_folder(path)   │                  │              │            │            │             │
 ├───────────────────>│                  │              │            │            │             │
 │                    │                  │              │            │            │             │
 │                    │ before_folder_add(path)         │            │            │             │
 │                    ├─────────────────>│              │            │            │             │
 │                    │                  │              │            │            │             │
 │                    │ True/False       │              │            │            │             │
 │                    │<─────────────────┤              │            │            │             │
 │                    │                  │              │            │            │             │
 │                    │ [if False]       │              │            │            │             │
 │<───────False───────┤                  │              │            │            │             │
 │                    │                  │              │            │            │             │
 │                    │ [if True]        │              │            │            │             │
 │                    │ validate_workspace_folder(path) │            │            │             │
 │                    ├────────────────────────────────>│            │            │             │
 │                    │                  │              │            │            │             │
 │                    │ ValidationResult │              │            │            │             │
 │                    │<────────────────────────────────┤            │            │             │
 │                    │                  │              │            │            │             │
 │                    │ add_folder(path, name)          │            │            │             │
 │                    ├─────────────────────────────────┼───────────>│            │             │
 │                    │                  │              │            │            │             │
 │                    │                  │              │            │ create WorkspaceFolder   │
 │                    │                  │              │            ├───────────>│             │
 │                    │                  │              │            │            │             │
 │                    │                  │              │            │ append to folders        │
 │                    │                  │              │            ├───────────>│             │
 │                    │                  │              │            │            │             │
 │                    │                  │              │            │ save_config()            │
 │                    │                  │              │            ├───────────>│             │
 │                    │                  │              │            │            │             │
 │                    │ WorkspaceFolder  │              │            │            │             │
 │                    │<─────────────────────────────────┼────────────┤            │             │
 │                    │                  │              │            │            │             │
 │                    │ get current folder count        │            │            │             │
 │                    ├─────────────────────────────────┼────────────┼───────────>│             │
 │                    │                  │              │            │            │             │
 │                    │ count = N        │              │            │            │             │
 │                    │<─────────────────────────────────┼────────────┼────────────┤             │
 │                    │                  │              │            │            │             │
 │                    │ beginInsertRows(invalid, N, N)  │            │            │             │
 │                    ├─────────────────────────────────┼────────────┼───────────>│             │
 │                    │                  │              │            │            │             │
 │                    │                  │              │            │            │ create TreeNode
 │                    │                  │              │            │            ├────────────>│
 │                    │                  │              │            │            │             │
 │                    │                  │              │            │            │ append to roots
 │                    │                  │              │            │            ├────────────>│
 │                    │                  │              │            │            │             │
 │                    │ endInsertRows()  │              │            │            │             │
 │                    ├─────────────────────────────────┼────────────┼───────────>│             │
 │                    │                  │              │            │            │             │
 │                    │                  │              │            │            │ refresh     │
 │                    │                  │              │            │            │<────────────┤
 │                    │                  │              │            │            │             │
 │                    │ after_folder_added(workspace_folder)         │            │             │
 │                    ├─────────────────>│              │            │            │             │
 │                    │                  │              │            │            │             │
 │                    │ folder_added.emit(workspace_folder)          │            │             │
 │                    ├─────────────────────────────────┼────────────┼────────────┼────────────>│
 │                    │                  │              │            │            │             │
 │<───────True────────┤                  │              │            │            │             │
 │                    │                  │              │            │            │             │
```

**Key Points:**
1. Lifecycle hooks and validation before operation
2. Manager updates config and saves to disk
3. Model uses beginInsertRows/endInsertRows for proper view update
4. Tree automatically shows new folder (Qt handles view refresh)

---

## State Machines

### Workspace Lifecycle State

```
                    ┌─────────────┐
                    │             │
            ┌──────>│ NO_WORKSPACE│<──────┐
            │       │             │       │
            │       └─────────────┘       │
            │              │              │
            │              │ open_workspace()
            │              ▼              │
            │       ┌─────────────┐       │
            │       │             │       │
            │       │  OPENING    │       │
            │       │             │       │
            │       └─────────────┘       │
            │              │              │
            │              │ (success)    │ close_workspace()
            │              ▼              │
            │       ┌─────────────┐       │
            │       │             │       │
      close │       │    OPEN     │───────┘
    workspace()     │             │
            │       └─────────────┘
            │         │         │
            │         │         │ add_folder()
            │         │         │ remove_folder()
            │         │         │ rename_folder()
            │         │         ▼
            │         │    ┌─────────────┐
            │         │    │             │
            │         │    │  MODIFYING  │
            │         │    │             │
            │         │    └─────────────┘
            │         │         │
            │         │         │ (success)
            │         │<────────┘
            │         │
            │         │ close_workspace()
            │         ▼
            │    ┌─────────────┐
            │    │             │
            └────│   CLOSING   │
                 │             │
                 └─────────────┘
                       │
                       │ (success)
                       ▼
                 ┌─────────────┐
                 │             │
                 │ NO_WORKSPACE│
                 │             │
                 └─────────────┘
```

**State Transitions:**

| Current State | Event | Next State | Actions |
|--------------|-------|------------|---------|
| NO_WORKSPACE | open_workspace() | OPENING | Validate, load config |
| OPENING | Success | OPEN | Load model, restore session, emit signal |
| OPENING | Failure | NO_WORKSPACE | Emit error, cleanup |
| OPEN | add_folder() | MODIFYING | Validate, update config |
| MODIFYING | Success | OPEN | Update model, save config |
| MODIFYING | Failure | OPEN | Revert, emit error |
| OPEN | close_workspace() | CLOSING | Save session, clear model |
| CLOSING | Success | NO_WORKSPACE | Emit signal |

**Implementation:**

```python
class WorkspaceState(Enum):
    NO_WORKSPACE = "no_workspace"
    OPENING = "opening"
    OPEN = "open"
    MODIFYING = "modifying"
    CLOSING = "closing"

class WorkspaceWidget(QWidget):
    def __init__(self, ...):
        ...
        self._state = WorkspaceState.NO_WORKSPACE

    def open_workspace(self, folder_path: Path) -> bool:
        # Check state
        if self._state != WorkspaceState.NO_WORKSPACE:
            self._error_handler.handle_error(
                ErrorSeverity.WARNING,
                "Workspace already open. Close current workspace first."
            )
            return False

        # Transition to OPENING
        self._state = WorkspaceState.OPENING

        try:
            # ... perform open operation ...

            # Transition to OPEN
            self._state = WorkspaceState.OPEN
            return True

        except Exception as e:
            # Revert to NO_WORKSPACE
            self._state = WorkspaceState.NO_WORKSPACE
            self._error_handler.handle_error(
                ErrorSeverity.ERROR,
                f"Failed to open workspace: {e}",
                exception=e
            )
            return False
```

### File Watcher State

```
                ┌──────────────┐
                │              │
        ┌──────>│  UNWATCHED   │
        │       │              │
        │       └──────────────┘
        │              │
        │              │ watch_file(path)
        │              ▼
        │       ┌──────────────┐
        │       │              │
        │       │   WATCHING   │<──────────┐
        │       │              │           │
        │       └──────────────┘           │
        │              │                   │
        │              │ file_changed      │
        │              ▼                   │
        │       ┌──────────────┐           │
        │       │              │           │
        │       │   DETECTED   │           │
        │       │   CHANGE     │           │
        │       └──────────────┘           │
        │              │                   │
        │              │ call handler      │
        │              ▼                   │
        │       ┌──────────────┐           │
        │       │              │           │
        │       │  PROCESSING  │           │
        │       │   CONFLICT   │           │
        │       └──────────────┘           │
        │              │                   │
        │              │ (action returned) │
        │              ├───────────────────┘
        │              │ (continue watching)
        │              │
        │              │ unwatch_file(path)
        │              ▼
        │       ┌──────────────┐
        │       │              │
        └───────│  UNWATCHED   │
                │              │
                └──────────────┘
```

**Per-file state tracking:**

```python
class FileWatchState(Enum):
    UNWATCHED = "unwatched"
    WATCHING = "watching"
    DETECTED_CHANGE = "detected_change"
    PROCESSING_CONFLICT = "processing_conflict"

class WorkspaceWidget(QWidget):
    def __init__(self, ...):
        ...
        self._watched_files: dict[str, FileWatchState] = {}

    def watch_file(self, file_path: str) -> None:
        if file_path in self._watched_files:
            return  # Already watching

        self._file_watcher.addPath(file_path)
        self._watched_files[file_path] = FileWatchState.WATCHING

    def _on_file_changed(self, file_path: str):
        if file_path not in self._watched_files:
            return

        # Transition to DETECTED_CHANGE
        self._watched_files[file_path] = FileWatchState.DETECTED_CHANGE

        # Transition to PROCESSING_CONFLICT
        self._watched_files[file_path] = FileWatchState.PROCESSING_CONFLICT

        # Call conflict handler
        action = self._conflict_handler.handle_file_modified(file_path)

        # Apply action
        self._apply_conflict_action(file_path, action)

        # Transition back to WATCHING (or UNWATCHED if closed)
        if action == FileConflictAction.CLOSE:
            self.unwatch_file(file_path)
        else:
            self._watched_files[file_path] = FileWatchState.WATCHING
```

---

## Error Handling Paths

### Error Categories

1. **Validation Errors** - User-facing, expected
   - Folder doesn't exist
   - Folder not readable
   - Nested workspace detected

2. **Configuration Errors** - Recoverable
   - Corrupt JSON file
   - Invalid config version
   - Missing required fields

3. **Filesystem Errors** - Partial recovery
   - Permission denied
   - Disk full
   - File locked

4. **Internal Errors** - Should not happen
   - Model state inconsistent
   - Signal connection failed
   - Memory allocation failed

### Error Propagation

```
Error Source → Detection Point → Handler → UI/Log → Recovery

Examples:

1. Corrupt Config File:
   Manager.load_config()
     → JSONDecodeError
     → ErrorHandler.handle_error(ERROR, "Corrupt config", exc)
     → QMessageBox + log
     → Use default config, continue

2. Permission Denied:
   Model._on_directory_changed()
     → PermissionError
     → ErrorHandler.handle_error(WARNING, "Cannot read dir", exc)
     → Log only (no UI popup)
     → Skip directory, continue

3. Filesystem Full:
   Manager.save_config()
     → OSError (ENOSPC)
     → ErrorHandler.handle_error(CRITICAL, "Disk full", exc)
     → QMessageBox.Critical
     → Keep config in memory, warn user

4. Model Index Invalid:
   Model.data()
     → index.internalPointer() is None
     → ErrorHandler.handle_error(ERROR, "Internal model error", exc)
     → Log + assert in debug
     → Return None, continue
```

### Error Recovery Strategies

```python
class WorkspaceWidget(QWidget):
    def open_workspace(self, folder_path: Path) -> bool:
        """Open workspace with error recovery."""
        try:
            # Validate
            result = self._validator.validate_workspace_folder(folder_path)
            if not result.is_valid:
                # User-facing error
                self._error_handler.handle_error(
                    ErrorSeverity.WARNING,
                    f"Invalid workspace: {result.error_message}"
                )
                return False

            # Load config
            try:
                config = self._manager.load_config(folder_path)
            except JSONDecodeError as e:
                # Recoverable: use default config
                self._error_handler.handle_error(
                    ErrorSeverity.WARNING,
                    "Config file corrupt, using defaults",
                    exception=e
                )
                config = WorkspaceConfig.from_folder(folder_path)
            except PermissionError as e:
                # Unrecoverable: can't read config
                self._error_handler.handle_error(
                    ErrorSeverity.ERROR,
                    "Cannot read config file",
                    exception=e
                )
                return False

            # Set folders (model operation)
            try:
                self._model.set_folders(config.folders)
            except Exception as e:
                # Critical: model in bad state
                self._error_handler.handle_error(
                    ErrorSeverity.CRITICAL,
                    "Failed to load workspace folders",
                    exception=e
                )
                # Attempt recovery
                if self.recover_from_error():
                    return False  # Recovered, but open failed
                else:
                    # Cannot recover - reset to clean state
                    self.reset_to_defaults()
                    return False

            return True

        except Exception as e:
            # Unexpected error - log and fail gracefully
            self._error_handler.handle_error(
                ErrorSeverity.CRITICAL,
                f"Unexpected error opening workspace: {e}",
                exception=e
            )
            return False
```

### Partial Failure Handling

**Scenario:** Multi-folder workspace, one folder becomes inaccessible.

```python
def set_folders(self, folders: list[WorkspaceFolder]) -> None:
    """Set folders with partial failure handling."""
    self.beginResetModel()

    # Clear old state
    self._root_nodes.clear()
    self._file_cache.clear()

    # Try to load each folder
    successful_folders = []
    for i, folder in enumerate(folders):
        try:
            # Validate folder
            if not Path(folder.path).exists():
                logger.warning(f"Folder does not exist: {folder.path}")
                continue

            if not os.access(folder.path, os.R_OK):
                logger.warning(f"Folder not readable: {folder.path}")
                continue

            # Create node
            node = TreeNode(
                path=folder.path,
                parent=None,
                workspace_folder=folder
            )
            node.row = len(successful_folders)
            self._root_nodes.append(node)
            successful_folders.append(folder)

            # Watch folder
            self._watcher.addPath(folder.path)

        except Exception as e:
            logger.error(f"Failed to add folder {folder.path}: {e}")
            # Continue with other folders

    self.endResetModel()

    # Warn if some folders failed
    if len(successful_folders) < len(folders):
        failed_count = len(folders) - len(successful_folders)
        self._error_handler.handle_error(
            ErrorSeverity.WARNING,
            f"{failed_count} folders could not be loaded"
        )
```

---

## Performance Implementation

### Caching Strategy

**1. FileInfo Cache**

```python
class MultiRootFileSystemModel(QAbstractItemModel):
    def __init__(self, ...):
        ...
        # Cache: absolute_path → FileInfo
        self._file_cache: dict[str, FileInfo] = {}

        # Cache statistics (for debugging/profiling)
        self._cache_hits = 0
        self._cache_misses = 0

    def _get_file_info(self, node: TreeNode) -> FileInfo:
        """Get FileInfo with caching."""
        # Check cache
        if node.path in self._file_cache:
            self._cache_hits += 1
            return self._file_cache[node.path]

        # Cache miss - load from filesystem
        self._cache_misses += 1
        path = Path(node.path)

        try:
            stat = path.stat()
            file_info = FileInfo(
                name=path.name,
                relative_path=self._get_relative_path(node),
                is_dir=path.is_dir(),
                size=stat.st_size if path.is_file() else 0,
                modified_time=stat.st_mtime
            )
        except (OSError, PermissionError) as e:
            # Fallback for inaccessible files
            file_info = FileInfo(
                name=path.name,
                relative_path=self._get_relative_path(node),
                is_dir=False,
                size=0,
                modified_time=0
            )

        # Cache it
        self._file_cache[node.path] = file_info
        return file_info

    def get_cache_stats(self) -> tuple[int, int, float]:
        """Get cache statistics.

        Returns:
            (hits, misses, hit_rate)
        """
        total = self._cache_hits + self._cache_misses
        hit_rate = self._cache_hits / total if total > 0 else 0.0
        return (self._cache_hits, self._cache_misses, hit_rate)
```

**Expected Cache Performance:**
- Initial load: 0% hit rate (cold cache)
- After navigation: 80-90% hit rate (warm cache)
- After external changes: Drops to ~50% (invalidated entries)

**2. Children Loading (Lazy)**

```python
class TreeNode:
    def load_children(self, filter_func: Callable) -> None:
        """Load children lazily when node expanded."""
        if self.children_loaded:
            return  # Already loaded

        # Start timing (for performance monitoring)
        start_time = time.perf_counter()

        self.children = []

        try:
            path = Path(self.path)

            # Use scandir for better performance than iterdir
            with os.scandir(path) as entries:
                # Collect and sort
                sorted_entries = sorted(
                    entries,
                    key=lambda e: (not e.is_dir(), e.name.lower())
                )

                for entry in sorted_entries:
                    # Apply filter
                    if filter_func(Path(entry.path)):
                        child_node = TreeNode(entry.path, parent=self)
                        child_node.row = len(self.children)
                        self.children.append(child_node)

            self.children_loaded = True

        except (PermissionError, OSError) as e:
            logger.warning(f"Failed to load children for {self.path}: {e}")
            self.children = []
            self.children_loaded = True

        # Log performance
        elapsed = time.perf_counter() - start_time
        if elapsed > 0.1:  # Warn if slow
            logger.warning(
                f"Slow directory scan: {self.path} took {elapsed:.3f}s "
                f"({len(self.children)} items)"
            )
```

**Performance Targets:**
- Directory with < 100 files: < 10ms
- Directory with 100-1000 files: < 100ms
- Directory with 1000+ files: < 500ms

### Optimization Techniques

**1. Debounced Filesystem Watcher**

```python
class MultiRootFileSystemModel(QAbstractItemModel):
    def __init__(self, ...):
        ...
        # Debounce timer for batching changes
        self._refresh_timer = QTimer()
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.setInterval(500)  # 500ms debounce
        self._refresh_timer.timeout.connect(self._apply_pending_changes)

        # Pending changes
        self._pending_changes: set[str] = set()

    def _on_directory_changed(self, path: str) -> None:
        """Handle directory change with debouncing."""
        # Add to pending changes
        self._pending_changes.add(path)

        # Restart timer (debounce)
        self._refresh_timer.start()

    def _apply_pending_changes(self) -> None:
        """Apply all pending changes at once."""
        if not self._pending_changes:
            return

        # Process changes
        for path in self._pending_changes:
            node = self._find_node_by_path(path)
            if node:
                # Mark children as stale
                node.children_loaded = False
                node.children = None

                # Emit dataChanged
                index = self._index_for_node(node)
                if index.isValid():
                    self.dataChanged.emit(index, index)

        # Clear pending
        self._pending_changes.clear()
```

**Benefit:** Reduces UI updates during rapid file changes (e.g., build process).

**2. Incremental Tree Expansion**

```python
class FileExplorerWidget(ThemedWidget):
    def expand_all(self) -> None:
        """Expand all folders incrementally to avoid blocking UI."""
        # Get all top-level items
        model = self._tree_view.model()
        root_index = QModelIndex()

        # Expand in chunks using QTimer
        self._expansion_queue = []
        for row in range(model.rowCount(root_index)):
            index = model.index(row, 0, root_index)
            self._expansion_queue.append(index)

        # Start incremental expansion
        self._expansion_timer = QTimer()
        self._expansion_timer.setSingleShot(False)
        self._expansion_timer.setInterval(10)  # 10ms between expansions
        self._expansion_timer.timeout.connect(self._expand_next)
        self._expansion_timer.start()

    def _expand_next(self) -> None:
        """Expand next item in queue."""
        if not self._expansion_queue:
            self._expansion_timer.stop()
            return

        # Expand one item
        index = self._expansion_queue.pop(0)
        self._tree_view.expand(index)

        # Add children to queue
        model = self._tree_view.model()
        for row in range(model.rowCount(index)):
            child_index = model.index(row, 0, index)
            if model.hasChildren(child_index):
                self._expansion_queue.append(child_index)
```

**Benefit:** UI remains responsive even when expanding large trees.

---

## Thread Safety Analysis

### Qt Threading Model

**Main Thread (GUI Thread):**
- All QWidget operations
- Model/view operations
- Signal/slot connections

**QFileSystemWatcher Internal Thread:**
- Filesystem monitoring (platform-specific)
- Emits signals on main thread (Qt handles marshaling)

### Thread Safety Requirements

**1. QAbstractItemModel is NOT thread-safe**

All model operations must be on main thread:
```python
# ✅ Good: Called from main thread
def _on_directory_changed(self, path: str) -> None:
    # This is already on main thread (QFileSystemWatcher emits on main thread)
    node = self._find_node_by_path(path)
    ...

# ❌ Bad: Don't do this
def load_large_workspace_in_background():
    thread = QThread()
    # WRONG: Model operations on worker thread
    model.set_folders(folders)  # Will crash!
```

**2. FileInfo Cache Access**

Cache is only accessed from main thread (via model methods), so no locking needed.

**3. QFileSystemWatcher Thread Safety**

QFileSystemWatcher uses internal thread for monitoring, but:
- `addPath()`, `removePath()` are thread-safe
- Signals are emitted on main thread
- No additional synchronization needed

### Async Operations (Future Enhancement)

If we want to load large workspaces without blocking:

```python
class MultiRootFileSystemModel(QAbstractItemModel):
    def set_folders_async(self, folders: list[WorkspaceFolder]) -> None:
        """Load folders asynchronously (future enhancement).

        NOT IMPLEMENTED IN V1 - all operations are synchronous.
        """
        # Potential approach using QThreadPool:
        # 1. Scan filesystem in worker thread
        # 2. Build TreeNode structure in worker
        # 3. Marshal back to main thread
        # 4. beginResetModel() on main thread
        # 5. Swap tree structure
        # 6. endResetModel() on main thread
        pass
```

**Decision for V1:** Keep all operations synchronous.
- Simpler implementation
- Easier to debug
- Performance is acceptable for < 100K files
- Can add async in V2 if needed

---

## Examples Implementation

Following the VFWidgets monorepo pattern, the `examples/` directory contains progressively complex demonstrations of the public API. Each example is numbered and builds upon previous concepts.

### Purpose of Examples

1. **Live Documentation** - Runnable code showing how to use the widget
2. **Progressive Learning** - Start simple, add complexity gradually
3. **Integration Testing** - Examples serve as integration tests
4. **Developer Onboarding** - New users can copy/modify examples
5. **API Validation** - If example is hard to write, API might be wrong

### Example Progression Strategy

**Incremental Demonstration:**
- Each example adds ONE new concept
- Early examples are minimal (< 50 lines)
- Later examples show real-world integration
- Final example demonstrates complete use case

**Example Naming Convention:**
```
examples/
├── 01_basic_single_folder.py      # Simplest possible usage
├── 02_multi_folder_workspace.py   # Multiple folders
├── 03_file_filtering.py           # Extension filtering
├── 04_session_persistence.py      # Save/restore UI state
├── 05_file_navigation.py          # reveal_file, find_file
├── 06_tab_integration.py          # Sync with tabs
├── 07_custom_icons.py             # Custom IconProvider
├── 08_context_menu.py             # Custom context menu
├── 09_lifecycle_hooks.py          # Workspace hooks
├── 10_error_handling.py           # Error handler protocol
├── 11_full_markdown_editor.py     # Complete application
└── README.md                       # Index of examples
```

### Examples Mapped to Implementation Phases

| Example | Phase | Dependencies | Demonstrates |
|---------|-------|--------------|--------------|
| 01 | Phase 5 | Core + Model + Manager + View + Widget | Basic workspace open, file selection |
| 02 | Phase 5 | + Config loading | Multi-folder from .workspace.json |
| 03 | Phase 5 | + File filtering | Extension filters, custom callbacks |
| 04 | Phase 5 | + Session management | Save/restore session |
| 05 | Phase 5 | + File navigation | reveal_file(), find_file() |
| 06 | Phase 5 | + Tab sync | sync_with_tab_widget() |
| 07 | Phase 6 | + IconProvider | Custom icons |
| 08 | Phase 6 | + ContextMenuProvider | Custom context menus |
| 09 | Phase 6 | + LifecycleHooks | before/after hooks |
| 10 | Phase 6 | + ErrorHandler | Error handling protocol |
| 11 | Phase 7 | All features | Full markdown editor |

---

### Example 01: Basic Single Folder

**File:** `examples/01_basic_single_folder.py`

**Demonstrates:**
- Import WorkspaceWidget
- Open single folder workspace
- Handle file selection signal
- Display in basic window

**Implementation Phase:** Phase 5 (after WorkspaceWidget facade complete)

```python
#!/usr/bin/env python3
"""Example 01: Basic Single Folder Workspace

Demonstrates:
- Opening a single folder workspace
- Handling file selection signal
- Minimal working example
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QSplitter
from PySide6.QtCore import Qt

from vfwidgets_workspace import WorkspaceWidget


class BasicWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Basic Workspace Example")
        self.resize(1000, 700)

        # Create workspace widget
        self.workspace = WorkspaceWidget()

        # Create text display
        self.text_display = QTextEdit()
        self.text_display.setPlaceholderText("Select a file from the workspace...")

        # Layout with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.workspace)
        splitter.addWidget(self.text_display)
        splitter.setSizes([250, 750])

        self.setCentralWidget(splitter)

        # Connect signals
        self.workspace.file_selected.connect(self.on_file_selected)

        # Open workspace (current directory for demo)
        workspace_path = Path.cwd()
        self.workspace.open_workspace(workspace_path)

    def on_file_selected(self, file_path: str):
        """Handle file selection."""
        print(f"Selected: {file_path}")

        # Load and display file content (text files only)
        path = Path(file_path)

        if path.suffix in ['.txt', '.md', '.py', '.json']:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.text_display.setPlainText(content)
            except Exception as e:
                self.text_display.setPlainText(f"Error reading file: {e}")
        else:
            self.text_display.setPlainText(f"File: {file_path}\n\nBinary or unsupported file type")


def main():
    app = QApplication(sys.argv)
    window = BasicWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

---

### Example 02: Multi-Folder Workspace

**File:** `examples/02_multi_folder_workspace.py`

**Demonstrates:**
- Loading workspace from `.workspace.json` config
- Multiple workspace folders
- Folder name display in tree

**Implementation Phase:** Phase 5

```python
#!/usr/bin/env python3
"""Example 02: Multi-Folder Workspace

Demonstrates:
- Loading workspace configuration from .workspace.json
- Multiple workspace folders in one workspace
- Folder hierarchy display
"""

import sys
import json
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt

from vfwidgets_workspace import WorkspaceWidget


class MultiFolderWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Folder Workspace Example")
        self.resize(800, 600)

        # Create layout
        central = QWidget()
        layout = QVBoxLayout(central)

        # Status label
        self.status = QLabel("No workspace open")
        layout.addWidget(self.status)

        # Workspace widget
        self.workspace = WorkspaceWidget()
        layout.addWidget(self.workspace)

        self.setCentralWidget(central)

        # Connect signals
        self.workspace.workspace_opened.connect(self.on_workspace_opened)
        self.workspace.file_selected.connect(self.on_file_selected)

        # Create example config
        self.create_example_config()

        # Open workspace
        self.workspace.open_workspace(Path.cwd())

    def create_example_config(self):
        """Create example .workspace.json config."""
        config = {
            "version": 1,
            "name": "Example Multi-Folder Project",
            "folders": [
                {
                    "path": str(Path.cwd() / "src"),
                    "name": "Source Code"
                },
                {
                    "path": str(Path.cwd() / "tests"),
                    "name": "Tests"
                },
                {
                    "path": str(Path.cwd() / "docs"),
                    "name": "Documentation"
                }
            ],
            "excluded_folders": [
                "node_modules",
                "__pycache__",
                ".git"
            ]
        }

        config_path = Path.cwd() / ".workspace.json"

        # Only create if doesn't exist
        if not config_path.exists():
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"Created example config: {config_path}")

    def on_workspace_opened(self, folders):
        """Handle workspace opened."""
        folder_count = len(folders)
        folder_names = [f.name for f in folders]

        self.status.setText(
            f"Workspace opened: {folder_count} folders - {', '.join(folder_names)}"
        )

    def on_file_selected(self, file_path: str):
        """Handle file selection."""
        self.status.setText(f"Selected: {Path(file_path).name}")


def main():
    app = QApplication(sys.argv)
    window = MultiFolderWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

---

### Example 03: File Filtering

**File:** `examples/03_file_filtering.py`

**Demonstrates:**
- Extension-based filtering
- Custom filter callback
- Excluded folders

**Implementation Phase:** Phase 5

```python
#!/usr/bin/env python3
"""Example 03: File Filtering

Demonstrates:
- Filtering files by extension
- Custom filter callbacks
- Excluded folders
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QComboBox

from vfwidgets_workspace import WorkspaceWidget, FileInfo, WorkspaceFolder


class FilterExample(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Filtering Example")
        self.resize(800, 600)

        # Layout
        central = QWidget()
        layout = QVBoxLayout(central)

        # Filter selector
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "All Files",
            "Python Files (.py)",
            "Markdown Files (.md)",
            "Text Files (.txt, .md, .rst)",
            "Custom: Only README files"
        ])
        self.filter_combo.currentTextChanged.connect(self.change_filter)
        layout.addWidget(QLabel("Filter:"))
        layout.addWidget(self.filter_combo)

        # Workspace
        self.workspace = WorkspaceWidget(
            excluded_folders=["__pycache__", ".git", "node_modules", ".venv"]
        )
        layout.addWidget(self.workspace)

        self.setCentralWidget(central)

        # Open workspace
        self.workspace.open_workspace(Path.cwd())

    def change_filter(self, filter_name: str):
        """Change active filter."""
        self.workspace.close_workspace()

        if filter_name == "Python Files (.py)":
            workspace = WorkspaceWidget(
                file_extensions=[".py"],
                excluded_folders=["__pycache__", ".git"]
            )
        elif filter_name == "Markdown Files (.md)":
            workspace = WorkspaceWidget(
                file_extensions=[".md"],
                excluded_folders=[".git"]
            )
        elif filter_name == "Text Files (.txt, .md, .rst)":
            workspace = WorkspaceWidget(
                file_extensions=[".txt", ".md", ".rst"],
                excluded_folders=[".git"]
            )
        elif filter_name == "Custom: Only README files":
            # Custom callback filter
            def readme_filter(file_info: FileInfo, workspace_folder: WorkspaceFolder) -> bool:
                # Show all directories
                if file_info.is_dir:
                    return True
                # Only show README files
                name = Path(file_info.path).name.lower()
                return name.startswith("readme")

            workspace = WorkspaceWidget(
                filter_callback=readme_filter,
                excluded_folders=[".git"]
            )
        else:  # All Files
            workspace = WorkspaceWidget(
                excluded_folders=["__pycache__", ".git", "node_modules"]
            )

        # Replace widget
        old_workspace = self.workspace
        layout = self.centralWidget().layout()
        layout.replaceWidget(old_workspace, workspace)
        old_workspace.deleteLater()
        self.workspace = workspace

        # Open workspace
        self.workspace.open_workspace(Path.cwd())


def main():
    app = QApplication(sys.argv)
    window = FilterExample()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

---

### Example 04: Session Persistence

**File:** `examples/04_session_persistence.py`

**Demonstrates:**
- Session save on close
- Session restore on open
- Persistent expanded folders
- Scroll position restoration

**Implementation Phase:** Phase 5

```python
#!/usr/bin/env python3
"""Example 04: Session Persistence

Demonstrates:
- Automatic session save/restore
- Expanded folders persistence
- Scroll position preservation
- Active file restoration
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout

from vfwidgets_workspace import WorkspaceWidget


class SessionExample(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Session Persistence Example")
        self.resize(800, 600)

        # Layout
        central = QWidget()
        layout = QVBoxLayout(central)

        # Instructions
        info = QLabel(
            "1. Expand some folders in the tree\n"
            "2. Select a file\n"
            "3. Close workspace\n"
            "4. Re-open workspace\n"
            "→ Expanded folders and active file are restored!"
        )
        layout.addWidget(info)

        # Buttons
        btn_layout = QHBoxLayout()
        self.open_btn = QPushButton("Open Workspace")
        self.close_btn = QPushButton("Close Workspace")
        self.open_btn.clicked.connect(self.open_workspace)
        self.close_btn.clicked.connect(self.close_workspace)
        btn_layout.addWidget(self.open_btn)
        btn_layout.addWidget(self.close_btn)
        layout.addLayout(btn_layout)

        # Status
        self.status = QLabel("No workspace open")
        layout.addWidget(self.status)

        # Workspace (session persistence enabled by default)
        self.workspace = WorkspaceWidget()
        self.workspace.workspace_opened.connect(self.on_opened)
        self.workspace.workspace_closed.connect(self.on_closed)
        self.workspace.active_file_changed.connect(self.on_file_changed)
        layout.addWidget(self.workspace)

        self.setCentralWidget(central)

        self.workspace_path = Path.cwd()

    def open_workspace(self):
        """Open workspace (session auto-restored)."""
        success = self.workspace.open_workspace(self.workspace_path)
        if success:
            self.status.setText(f"Workspace opened: {self.workspace_path}")
            self.open_btn.setEnabled(False)
            self.close_btn.setEnabled(True)

    def close_workspace(self):
        """Close workspace (session auto-saved)."""
        self.workspace.close_workspace()

    def on_opened(self, folders):
        self.status.setText(f"✅ Workspace opened ({len(folders)} folders) - Session restored")

    def on_closed(self):
        self.status.setText("Workspace closed - Session saved")
        self.open_btn.setEnabled(True)
        self.close_btn.setEnabled(False)

    def on_file_changed(self, file_path: str):
        self.status.setText(f"Active file: {Path(file_path).name}")


def main():
    app = QApplication(sys.argv)
    window = SessionExample()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

---

### Example 05: File Navigation

**File:** `examples/05_file_navigation.py`

**Demonstrates:**
- `reveal_file()` - expand parents, scroll, select
- `highlight_file()` - select without expand
- `find_file()` - fuzzy and exact search

**Implementation Phase:** Phase 5

```python
#!/usr/bin/env python3
"""Example 05: File Navigation

Demonstrates:
- reveal_file() - Expand parents and scroll to file
- highlight_file() - Select file without expanding
- find_file() - Search with fuzzy matching
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel,
    QPushButton, QLineEdit, QHBoxLayout, QListWidget
)

from vfwidgets_workspace import WorkspaceWidget


class NavigationExample(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Navigation Example")
        self.resize(1200, 700)

        # Layout
        central = QWidget()
        layout = QVBoxLayout(central)

        # Search section
        layout.addWidget(QLabel("Search Files (fuzzy matching):"))
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to search (e.g., 'readme' or 'rm')")
        self.search_input.textChanged.connect(self.search_files)
        self.search_btn = QPushButton("Find Exact")
        self.search_btn.clicked.connect(lambda: self.search_files(fuzzy=False))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)
        layout.addLayout(search_layout)

        # Results list
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.reveal_selected_result)
        layout.addWidget(QLabel("Results (double-click to reveal):"))
        layout.addWidget(self.results_list)

        # Workspace
        self.workspace = WorkspaceWidget()
        layout.addWidget(self.workspace)

        self.setCentralWidget(central)

        # Open workspace
        self.workspace.open_workspace(Path.cwd())

    def search_files(self, fuzzy: bool = True):
        """Search for files."""
        query = self.search_input.text()

        if not query:
            self.results_list.clear()
            return

        # Find files
        results = self.workspace.find_file(query, fuzzy=fuzzy)

        # Display results
        self.results_list.clear()
        for file_path in results[:50]:  # Limit to 50 results
            # Show relative path for readability
            rel_path = Path(file_path).relative_to(Path.cwd())
            self.results_list.addItem(str(rel_path))
            self.results_list.item(self.results_list.count() - 1).setData(
                0x0100,  # UserRole
                file_path
            )

        if not results:
            self.results_list.addItem("No matches found")
        elif len(results) > 50:
            self.results_list.addItem(f"... and {len(results) - 50} more")

    def reveal_selected_result(self, item):
        """Reveal selected file in workspace."""
        file_path = item.data(0x0100)  # UserRole
        if file_path:
            # Reveal file (expands parents, scrolls to view)
            success = self.workspace.reveal_file(file_path)
            if success:
                print(f"Revealed: {file_path}")


def main():
    app = QApplication(sys.argv)
    window = NavigationExample()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

---

### Example 06: Tab Integration

**File:** `examples/06_tab_integration.py`

**Demonstrates:**
- `sync_with_tab_widget()` - Auto-sync workspace with tabs
- Highlighting active file when tab switches
- Bidirectional sync

**Implementation Phase:** Phase 5

```python
#!/usr/bin/env python3
"""Example 06: Tab Integration

Demonstrates:
- sync_with_tab_widget() - Auto-highlight file when tab changes
- Opening files in tabs
- Bidirectional workspace ↔ tabs synchronization
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QHBoxLayout, QWidget,
    QSplitter, QTextEdit
)
from PySide6.QtCore import Qt

from vfwidgets_workspace import WorkspaceWidget

# Import ChromeTabbedWindow if available
try:
    from chrome_tabbed_window import ChromeTabbedWindow
    CHROME_TABS_AVAILABLE = True
except ImportError:
    from PySide6.QtWidgets import QTabWidget as ChromeTabbedWindow
    CHROME_TABS_AVAILABLE = False
    print("Note: chrome-tabbed-window not installed, using QTabWidget")


class EditorTab(QTextEdit):
    """Simple text editor tab with file_path attribute."""

    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self.file_path = file_path  # Required for sync

        # Load file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.setPlainText(f.read())
        except Exception as e:
            self.setPlainText(f"Error loading file: {e}")


class TabIntegrationExample(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tab Integration Example")
        self.resize(1400, 800)

        # Main layout
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Workspace
        self.workspace = WorkspaceWidget()
        self.workspace.file_double_clicked.connect(self.open_file_in_tab)
        splitter.addWidget(self.workspace)

        # Tab widget
        self.tab_widget = ChromeTabbedWindow()
        splitter.addWidget(self.tab_widget)

        splitter.setSizes([300, 1100])
        self.setCentralWidget(splitter)

        # Enable auto-sync: when tab changes, highlight file in workspace
        self.workspace.sync_with_tab_widget(
            self.tab_widget,
            file_path_attr="file_path",
            auto_sync=True
        )

        # Open workspace
        self.workspace.open_workspace(Path.cwd())

    def open_file_in_tab(self, file_path: str):
        """Open file in new tab."""
        file_name = Path(file_path).name

        # Check if already open
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if hasattr(tab, 'file_path') and tab.file_path == file_path:
                # Already open - switch to it
                self.tab_widget.setCurrentIndex(i)
                return

        # Open new tab
        editor = EditorTab(file_path)
        index = self.tab_widget.addTab(editor, file_name)
        self.tab_widget.setCurrentIndex(index)

        # Note: When tab switches, workspace automatically highlights the file
        # (due to sync_with_tab_widget)


def main():
    app = QApplication(sys.argv)
    window = TabIntegrationExample()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

---

### Example 07-10: Extension Point Examples

**Files:** `examples/07_custom_icons.py`, `08_context_menu.py`, `09_lifecycle_hooks.py`, `10_error_handling.py`

**Implementation Phase:** Phase 6 (Extension Points)

**Note:** Full implementations of these examples should demonstrate:
- 07: IconProvider protocol with custom SVG icons
- 08: ContextMenuProvider with custom actions
- 09: WorkspaceLifecycleHooks with validation
- 10: ErrorHandler protocol with user-friendly error dialogs

(Detailed code omitted for brevity - follow same pattern as examples 01-06)

---

### Example 11: Full Markdown Editor

**File:** `examples/11_full_markdown_editor.py`

**Demonstrates:**
- Complete application using WorkspaceWidget
- Markdown editor with live preview
- Tab management
- Session persistence
- Custom context menus
- All features integrated

**Implementation Phase:** Phase 7 (Polish)

**Note:** This is the "showcase" example (~300-400 lines) demonstrating a real-world application similar to Reamde.

---

### Examples README

**File:** `examples/README.md`

```markdown
# WorkspaceWidget Examples

Progressive examples demonstrating the WorkspaceWidget API.

## Quick Start

Run any example:
```bash
python examples/01_basic_single_folder.py
```

## Example Index

| # | File | Demonstrates | Complexity |
|---|------|--------------|------------|
| 01 | `01_basic_single_folder.py` | Open folder, handle selection | ⭐ Basic |
| 02 | `02_multi_folder_workspace.py` | Multi-folder config | ⭐ Basic |
| 03 | `03_file_filtering.py` | Extension/callback filters | ⭐⭐ Intermediate |
| 04 | `04_session_persistence.py` | Save/restore UI state | ⭐⭐ Intermediate |
| 05 | `05_file_navigation.py` | reveal, highlight, find | ⭐⭐ Intermediate |
| 06 | `06_tab_integration.py` | Tab widget sync | ⭐⭐ Intermediate |
| 07 | `07_custom_icons.py` | IconProvider protocol | ⭐⭐⭐ Advanced |
| 08 | `08_context_menu.py` | ContextMenuProvider | ⭐⭐⭐ Advanced |
| 09 | `09_lifecycle_hooks.py` | Lifecycle hooks | ⭐⭐⭐ Advanced |
| 10 | `10_error_handling.py` | ErrorHandler protocol | ⭐⭐⭐ Advanced |
| 11 | `11_full_markdown_editor.py` | Complete application | ⭐⭐⭐⭐ Full |

## Learning Path

**Beginners:** Start with 01-03
**Intermediate:** Continue with 04-06
**Advanced:** Study 07-10 for extension points
**Complete Reference:** Review 11 for full integration

## Requirements

```bash
pip install vfwidgets-workspace
pip install chrome-tabbed-window  # Optional, for example 06
```

## API Documentation

See `../docs/` for complete API reference.
```

---

### Testing Examples as Part of CI

Examples can be validated in CI pipeline:

```python
# In tests/test_examples.py
import subprocess
import sys
from pathlib import Path

def test_examples_runnable():
    """Verify all examples can be imported without errors."""
    examples_dir = Path(__file__).parent.parent / "examples"

    for example_file in sorted(examples_dir.glob("0*.py")):
        # Run with --help or import test
        result = subprocess.run(
            [sys.executable, "-c", f"import {example_file.stem}"],
            cwd=examples_dir.parent,
            capture_output=True
        )

        assert result.returncode == 0, f"Example {example_file.name} failed to import"
```

---

## Implementation Checklist

### Phase 1: Core Data Structures
- [ ] Implement `TreeNode` class
- [ ] Implement `FileInfo` dataclass
- [ ] Implement `WorkspaceFolder` dataclass
- [ ] Implement `WorkspaceConfig` dataclass
- [ ] Implement `WorkspaceSession` dataclass
- [ ] Write unit tests for data models

### Phase 2: MultiRootFileSystemModel
- [ ] Implement `index()` method
- [ ] Implement `parent()` method
- [ ] Implement `rowCount()` method
- [ ] Implement `columnCount()` method
- [ ] Implement `data()` method (DisplayRole, DecorationRole, etc.)
- [ ] Implement `flags()` method
- [ ] Implement `hasChildren()` method
- [ ] Implement `set_folders()` method
- [ ] Implement file filtering logic
- [ ] Implement filesystem caching
- [ ] Implement filesystem watching
- [ ] Write unit tests for model

### Phase 3: WorkspaceManager
- [ ] Implement `open_workspace()` method
- [ ] Implement `close_workspace()` method
- [ ] Implement `add_folder()` method
- [ ] Implement `remove_folder()` method
- [ ] Implement `rename_folder()` method
- [ ] Implement config loading/saving
- [ ] Implement session loading/saving
- [ ] Write unit tests for manager

### Phase 4: FileExplorerWidget
- [ ] Create QTreeView setup
- [ ] Implement ThemedWidget integration
- [ ] Implement `theme_changed()` method
- [ ] Connect signals to model
- [ ] Write unit tests for widget

### Phase 5: WorkspaceWidget (Facade)
- [ ] Implement constructor with dependency injection
- [ ] Implement `open_workspace()` with lifecycle hooks
- [ ] Implement `close_workspace()` with lifecycle hooks
- [ ] Implement `add_folder()` with validation
- [ ] Implement `remove_folder()` with validation
- [ ] Implement session save/restore methods
- [ ] Implement file navigation methods (reveal, highlight, find)
- [ ] Implement tab synchronization
- [ ] Implement all convenience methods
- [ ] Implement factory methods
- [ ] Implement builder pattern
- [ ] Connect all signals
- [ ] Write integration tests
- [ ] **Create Example 01:** Basic single folder (`examples/01_basic_single_folder.py`)
- [ ] **Create Example 02:** Multi-folder workspace (`examples/02_multi_folder_workspace.py`)
- [ ] **Create Example 03:** File filtering (`examples/03_file_filtering.py`)
- [ ] **Create Example 04:** Session persistence (`examples/04_session_persistence.py`)
- [ ] **Create Example 05:** File navigation (`examples/05_file_navigation.py`)
- [ ] **Create Example 06:** Tab integration (`examples/06_tab_integration.py`)
- [ ] **Create examples/README.md** with example index

### Phase 6: Extension Point Implementations
- [ ] Implement `DefaultFileConflictHandler`
- [ ] Implement `DefaultErrorHandler`
- [ ] Implement `DefaultIconProvider`
- [ ] Implement `DefaultWorkspaceValidator`
- [ ] Implement `DefaultContextMenuProvider`
- [ ] Implement `DefaultLifecycleHooks`
- [ ] Write tests for all handlers
- [ ] **Create Example 07:** Custom icons (`examples/07_custom_icons.py`)
- [ ] **Create Example 08:** Context menu (`examples/08_context_menu.py`)
- [ ] **Create Example 09:** Lifecycle hooks (`examples/09_lifecycle_hooks.py`)
- [ ] **Create Example 10:** Error handling (`examples/10_error_handling.py`)

### Phase 7: Performance & Polish
- [ ] Profile model performance
- [ ] Optimize cache hit rate
- [ ] Implement debounced refresh
- [ ] Add performance logging
- [ ] Memory leak testing
- [ ] Write performance tests
- [ ] **Create Example 11:** Full markdown editor (`examples/11_full_markdown_editor.py`)

### Phase 8: Documentation & CI
- [ ] Update README with installation guide
- [ ] Update README with quick start
- [ ] Update README with API overview
- [ ] Create API documentation (Sphinx/MkDocs)
- [ ] Add examples to CI test suite (`tests/test_examples.py`)
- [ ] Verify all examples run without errors
- [ ] Add troubleshooting guide
- [ ] Add migration guide (if applicable)

---

## Summary

This design document provides implementation details for:

1. **Architecture** - Component ownership, signal connections, initialization order
2. **Core Components** - Complete implementations for Model, Manager, View, Widget
3. **Convenience Methods** - Session management, file navigation, tab sync, fuzzy search
4. **Sequence Diagrams** - Step-by-step flows for complex operations
5. **State Machines** - Lifecycle and file watching state management
6. **Error Handling** - Categorization, propagation paths, recovery strategies
7. **Performance** - Caching, lazy loading, debouncing, profiling
8. **Thread Safety** - Qt threading model, synchronization requirements
9. **Examples** - 11 progressive examples demonstrating the public API

**Key Features of Examples:**
- Progressive learning from basic (01) to advanced (11)
- Each example demonstrates ONE new concept
- Complete runnable code for immediate use
- Tied to implementation phases for validation
- Examples serve as integration tests

**Next Step:** Begin implementation following the phased checklist, starting with Phase 1 (Core Data Structures). Create examples alongside implementation to validate API usability.

