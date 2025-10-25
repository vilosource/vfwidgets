# VFWidgets Workspace Widget - Specification

**Version:** 1.0
**Date:** 2025-10-24
**Status:** Planning
**Package:** `vfwidgets-workspace`

## Overview

A generic, reusable workspace widget for file-based applications in the VFWidgets ecosystem. Provides VS Code-style multi-folder workspace management with file tree explorer, session persistence, and theme integration.

**Target Applications:**
- Reamde (markdown viewer)
- ViloxTerm (terminal emulator for project workspaces)
- Theme Studio (theme file collections)
- ViloWeb (web development projects)
- Any file-based application requiring workspace functionality

## Design Philosophy

### Core Principles
1. **Generic by Default** - No file-type assumptions, fully parameterizable
2. **Extension Points** - Subclassing and callbacks for customization
3. **MVC Architecture** - Clean separation of model, view, controller
4. **Theme Integration** - Automatic VS Code-compatible theming via ThemedWidget
5. **Session Management** - Built-in persistence with override capability
6. **Zero Dependencies** - Only depends on `vfwidgets-theme` (optional) and PySide6

### What This Widget Provides

✅ **Multi-folder workspace management** (add/remove/rename folders)
✅ **File tree explorer** with custom `QAbstractItemModel`
✅ **File filtering** (extensions + custom callbacks)
✅ **Session persistence** (expanded folders, scroll position, per-root state)
✅ **Theme integration** via `ThemedWidget`
✅ **Recent workspaces** list
✅ **Workspace configuration** (extensible via subclassing)
✅ **Context menus** (extensible via callbacks)
✅ **Filesystem watching** (auto-refresh on changes)

### What This Widget Does NOT Provide

❌ **File opening logic** (emit signal, app handles it)
❌ **Tab management** (app's responsibility)
❌ **File editing** (app's responsibility)
❌ **File-type specific features** (app extends config for this)
❌ **Window chrome** (integrates with `ViloCodeWindow` or any parent)

## Quick Start Guide

### 5-Minute Quickstart

Get started with WorkspaceWidget in under 5 minutes:

```python
from PySide6.QtWidgets import QApplication, QMainWindow
from vfwidgets_workspace import WorkspaceWidget
from pathlib import Path

# 1. Create the application
app = QApplication([])

# 2. Create workspace widget (zero configuration)
workspace = WorkspaceWidget()

# 3. Connect to file selection
workspace.file_selected.connect(lambda path: print(f"Selected: {path}"))

# 4. Open a folder
workspace.open_workspace(Path("/home/user/my-project"))

# 5. Add to UI
window = QMainWindow()
window.setCentralWidget(workspace)
window.show()

app.exec()
```

**That's it!** You now have a working multi-folder workspace with:
- ✅ File tree explorer
- ✅ Automatic theme integration (if vfwidgets-theme installed)
- ✅ Session persistence (remembers expanded folders)
- ✅ Filesystem watching (auto-refresh on changes)

### Factory Methods for Common Use Cases

Instead of configuring manually, use pre-configured factory methods:

```python
# Markdown files (Reamde, documentation apps)
workspace = WorkspaceWidget.for_markdown()
# Pre-configured: [".md", ".markdown", ".mdown"]
# Excludes: [".git", "node_modules"]

# Python projects
workspace = WorkspaceWidget.for_python()
# Pre-configured: [".py", ".pyi", ".pyx"]
# Excludes: ["__pycache__", ".venv", "venv", "build", "dist", ".pytest_cache"]

# Web development
workspace = WorkspaceWidget.for_web()
# Pre-configured: [".html", ".css", ".js", ".ts", ".jsx", ".tsx", ".vue"]
# Excludes: ["node_modules", "dist", "build", ".cache"]

# JavaScript/TypeScript projects
workspace = WorkspaceWidget.for_javascript()
# Pre-configured: [".js", ".ts", ".jsx", ".tsx", ".json"]
# Excludes: ["node_modules", "dist", "build"]

# All files (no filtering)
workspace = WorkspaceWidget.for_all_files()
# Shows everything except hidden files (configurable)

# Minimal configuration (empty, configure manually)
workspace = WorkspaceWidget.empty()
# No extensions, no exclusions, manual configuration required
```

### Builder Pattern API

For complex configurations, use the fluent builder API:

```python
workspace = (
    WorkspaceWidget.builder()
    .with_extensions([".py", ".pyi"])
    .exclude_folders(["__pycache__", ".venv"])
    .with_config_file(".myapp-workspace.json")
    .with_auto_watch()  # Automatically watch opened files
    .with_auto_recovery()  # Recover from corrupt configs
    .build()
)

# Or use fluent API on instance
workspace = WorkspaceWidget()
workspace.configure() \
    .filter_extensions([".py"]) \
    .exclude_folders(["__pycache__"]) \
    .enable_auto_watch() \
    .apply()
```

### Progressive Complexity Examples

**Level 1: Basic (just open a folder)**
```python
workspace = WorkspaceWidget()
workspace.file_selected.connect(open_file)
workspace.open_workspace(Path("/home/user/docs"))
```

**Level 2: With file filtering**
```python
workspace = WorkspaceWidget(file_extensions=[".md", ".txt"])
workspace.file_selected.connect(open_file)
workspace.open_workspace(Path("/home/user/docs"))
```

**Level 3: With custom config**
```python
@dataclass
class MyConfig(WorkspaceConfig):
    auto_save: bool = True
    preview_mode: str = "split"

workspace = WorkspaceWidget(config_class=MyConfig)
workspace.file_selected.connect(open_file)
workspace.open_workspace(Path("/home/user/docs"))

# Access custom config
if workspace.get_config().auto_save:
    enable_auto_save()
```

**Level 4: Full customization (protocols)**
```python
class MyConflictHandler:
    def handle_file_modified(self, file_path, workspace_folder=None):
        return FileConflictAction.RELOAD  # Always reload

class MyIconProvider:
    def get_file_icon(self, file_info):
        return QIcon(f":/icons/{file_info.extension}.svg")

workspace = WorkspaceWidget(
    file_extensions=[".md"],
    conflict_handler=MyConflictHandler(),
    icon_provider=MyIconProvider(),
    config_class=MyConfig
)
```

### Integration with Existing Apps

**With ViloCodeWindow (sidebar pattern):**
```python
from vilocode_window import ViloCodeWindow

window = ViloCodeWindow()
workspace = WorkspaceWidget.for_markdown()

# Add to sidebar
window.add_sidebar_panel("explorer", workspace, "FILES")

# Connect to tab widget
workspace.file_selected.connect(window.open_file_in_tab)
```

**With QMainWindow (docking pattern):**
```python
from PySide6.QtWidgets import QMainWindow, QDockWidget

window = QMainWindow()
workspace = WorkspaceWidget.for_python()

# Add as dock widget
dock = QDockWidget("Workspace", window)
dock.setWidget(workspace)
window.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)

workspace.file_selected.connect(open_in_editor)
```

## Architecture

### MVC Pattern

```
┌─────────────────────────────────────────────────────────┐
│                    Application Layer                     │
│  (Reamde, ViloxTerm, etc. - uses WorkspaceWidget API)   │
└────────────────────┬────────────────────────────────────┘
                     │
          ┌──────────▼──────────┐
          │  WorkspaceWidget    │  ← Main API
          │  (Facade)           │
          └──────────┬──────────┘
                     │
     ┌───────────────┼───────────────┐
     │               │               │
┌────▼────┐    ┌────▼────┐    ┌────▼────┐
│  Model  │    │  View   │    │Controller│
│         │    │         │    │          │
│ Multi   │    │  File   │    │Workspace │
│ Root    │◄───┤ Explorer│◄───┤ Manager  │
│ FSModel │    │ Widget  │    │          │
└─────────┘    └─────────┘    └──────────┘
     │              │               │
     └──────────────┴───────────────┘
                    │
            ┌───────▼────────┐
            │  Data Models   │
            │ - WorkspaceFolder
            │ - FileInfo
            │ - WorkspaceConfig
            │ - WorkspaceSession
            └────────────────┘
```

### Component Diagram

```
WorkspaceWidget (QWidget)
├── MultiRootFileSystemModel (QAbstractItemModel)
│   ├── WorkspaceFolder data (list)
│   ├── FileInfo cache (dict)
│   ├── QFileSystemWatcher
│   └── Filter logic (extensions + callback)
│
├── FileExplorerWidget (ThemedWidget + QTreeView)
│   ├── QTreeView (visual display)
│   ├── Theme styling (automatic)
│   └── Signals (file_selected, folder_expanded, etc.)
│
├── WorkspaceManager (QObject)
│   ├── Workspace lifecycle (open/close)
│   ├── Folder operations (add/remove/rename)
│   ├── Config persistence
│   └── Session management
│
└── Integration Points
    ├── Signals (for app integration)
    ├── Extensible config (subclassing)
    └── Filter callbacks (custom logic)
```

## Data Models

### WorkspaceFolder

```python
@dataclass
class WorkspaceFolder:
    """Represents a single folder root in a workspace.

    Pure data class with no Qt dependencies (clean architecture).
    """
    path: str  # Absolute path to folder
    name: Optional[str] = None  # Custom display name (overrides basename)

    @property
    def display_name(self) -> str:
        """Get the display name for this folder.

        Returns custom name if set, otherwise basename of path.

        Examples:
            WorkspaceFolder("/home/user/docs").display_name == "docs"
            WorkspaceFolder("/home/user/docs", "API Docs").display_name == "API Docs"
        """
        if self.name:
            return self.name
        return Path(self.path).name

    def to_dict(self) -> dict:
        """Serialize to dictionary for JSON storage."""
        return {
            "path": self.path,
            "name": self.name
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WorkspaceFolder":
        """Deserialize from dictionary."""
        return cls(
            path=data["path"],
            name=data.get("name")
        )
```

### FileInfo

```python
@dataclass
class FileInfo:
    """Information about a file or folder in the tree.

    Pure data class with no Qt dependencies.
    Used by MultiRootFileSystemModel to cache filesystem data.
    """
    name: str  # Filename or folder name (basename)
    relative_path: str  # Path relative to workspace folder root
    is_dir: bool  # True if folder, False if file
    size: int = 0  # File size in bytes (0 for folders)
    modified_time: float = 0.0  # Modification timestamp (Unix epoch)

    @property
    def extension(self) -> str:
        """Get file extension (lowercase, with dot).

        Examples:
            "file.txt" -> ".txt"
            "script.py" -> ".py"
            "folder" -> ""
        """
        return Path(self.name).suffix.lower()
```

### WorkspaceConfig

```python
@dataclass
class WorkspaceConfig:
    """Generic workspace configuration.

    Extensible via subclassing for app-specific settings.
    Supports both typed subclassing and ad-hoc custom_data dict.
    """

    # Core settings
    name: str  # Display name for workspace
    version: int = 2  # Config version (for migration)

    # Multi-folder support
    folders: list[WorkspaceFolder] = field(default_factory=list)

    # File filtering (app can override)
    excluded_folders: list[str] = field(default_factory=lambda: [
        "node_modules", ".git", "__pycache__", ".venv",
        "venv", "dist", "build", ".direnv", ".idea", ".vscode"
    ])
    included_extensions: list[str] = field(default_factory=list)  # Empty = all files

    # UI preferences
    show_hidden_files: bool = False  # Show files/folders starting with "."
    sort_folders_first: bool = True  # Folders before files in tree

    # Theme overrides (workspace-specific colors)
    theme_overrides: dict[str, str] = field(default_factory=dict)
    # Example: {"editor.background": "#1a1a2e", "sideBar.background": "#16161e"}

    # Recent files (up to 10)
    recent_files: list[str] = field(default_factory=list)

    # Custom data (for ad-hoc settings without subclassing)
    custom_data: dict[str, Any] = field(default_factory=dict)

    # DEPRECATED: Backward compatibility (version 1 used root_path)
    root_path: Optional[str] = None

    def __post_init__(self):
        """Migrate old single-folder format to new multi-folder format."""
        if self.root_path and not self.folders:
            # Migrate from version 1
            self.folders = [WorkspaceFolder(path=self.root_path)]
            self.root_path = None

    def to_dict(self) -> dict:
        """Serialize to dictionary for JSON storage."""
        return {
            "name": self.name,
            "version": self.version,
            "folders": [f.to_dict() for f in self.folders],
            "excluded_folders": self.excluded_folders,
            "included_extensions": self.included_extensions,
            "show_hidden_files": self.show_hidden_files,
            "sort_folders_first": self.sort_folders_first,
            "theme_overrides": self.theme_overrides,
            "recent_files": self.recent_files,
            "custom_data": self.custom_data
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WorkspaceConfig":
        """Deserialize from dictionary."""
        # Convert folders dict list to WorkspaceFolder objects
        folders_data = data.get("folders", [])
        folders = [WorkspaceFolder.from_dict(f) for f in folders_data]

        return cls(
            name=data["name"],
            version=data.get("version", 1),
            folders=folders,
            excluded_folders=data.get("excluded_folders", []),
            included_extensions=data.get("included_extensions", []),
            show_hidden_files=data.get("show_hidden_files", False),
            sort_folders_first=data.get("sort_folders_first", True),
            theme_overrides=data.get("theme_overrides", {}),
            recent_files=data.get("recent_files", []),
            custom_data=data.get("custom_data", {}),
            root_path=data.get("root_path")  # For migration
        )

    @classmethod
    def from_folder(cls, folder_path: Path, name: Optional[str] = None) -> "WorkspaceConfig":
        """Create default config for a folder.

        Args:
            folder_path: Path to folder
            name: Optional workspace name (defaults to folder basename)

        Returns:
            WorkspaceConfig with single folder
        """
        return cls(
            name=name or folder_path.name,
            folders=[WorkspaceFolder(path=str(folder_path.resolve()))]
        )
```

### WorkspaceRootState

```python
@dataclass
class WorkspaceRootState:
    """Session state for a single workspace root folder.

    Used to persist UI state (expanded folders, scroll position) per root.
    """
    path: str  # Workspace folder path (must match WorkspaceFolder.path)
    expanded_folders: list[str] = field(default_factory=list)  # Relative paths
    scroll_position: int = 0  # Vertical scroll offset in pixels

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "path": self.path,
            "expanded_folders": self.expanded_folders,
            "scroll_position": self.scroll_position
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WorkspaceRootState":
        """Deserialize from dictionary."""
        return cls(
            path=data["path"],
            expanded_folders=data.get("expanded_folders", []),
            scroll_position=data.get("scroll_position", 0)
        )
```

### WorkspaceSession

```python
@dataclass
class WorkspaceSession:
    """Session state for an entire workspace.

    Apps typically extend this with app-specific state (open files, etc.).
    This base class only handles workspace UI state.
    """
    workspace_name: str  # Name of workspace
    workspace_roots: list[WorkspaceRootState] = field(default_factory=list)
    sidebar_width: int = 250  # Sidebar width in pixels
    sidebar_visible: bool = True  # Sidebar visibility

    # App-specific data (extensible)
    custom_data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Serialize to dictionary for JSON storage."""
        return {
            "workspace_name": self.workspace_name,
            "workspace_roots": [r.to_dict() for r in self.workspace_roots],
            "sidebar_width": self.sidebar_width,
            "sidebar_visible": self.sidebar_visible,
            "custom_data": self.custom_data
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WorkspaceSession":
        """Deserialize from dictionary."""
        roots_data = data.get("workspace_roots", [])
        roots = [WorkspaceRootState.from_dict(r) for r in roots_data]

        return cls(
            workspace_name=data["workspace_name"],
            workspace_roots=roots,
            sidebar_width=data.get("sidebar_width", 250),
            sidebar_visible=data.get("sidebar_visible", True),
            custom_data=data.get("custom_data", {})
        )
```

## Extension Points and Protocols

### Design Philosophy

The workspace widget follows **SOLID principles** with clear separation of concerns:

1. **Open/Closed Principle**: Open for extension via protocols, closed for modification
2. **Dependency Inversion**: Depend on abstractions (protocols), not concrete implementations
3. **Single Responsibility**: Each handler has one clear responsibility
4. **Interface Segregation**: Focused protocols with specific methods
5. **Liskov Substitution**: Default implementations can be replaced with custom ones

### Public API Boundaries

```
┌─────────────────────────────────────────────────────────┐
│            WorkspaceWidget (Public API)                  │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Extension Points (Protocols)                     │  │
│  │  - FileConflictHandler                            │  │
│  │  - ErrorHandler                                   │  │
│  │  - IconProvider                                   │  │
│  │  - WorkspaceValidator                             │  │
│  │  - ContextMenuProvider                            │  │
│  │  - WorkspaceLifecycleHooks                        │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Default Implementations (Built-in)               │  │
│  │  - DefaultFileConflictHandler                     │  │
│  │  - DefaultErrorHandler                            │  │
│  │  - DefaultIconProvider                            │  │
│  │  - DefaultWorkspaceValidator                      │  │
│  │  - DefaultContextMenuProvider                     │  │
│  │  - DefaultLifecycleHooks                          │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Signals (Non-blocking Notifications)             │  │
│  │  - file_modified, file_deleted, file_moved        │  │
│  │  - error_occurred, warning_occurred               │  │
│  │  - workspace_opened, workspace_closed             │  │
│  │  - file_selected, folder_expanded, etc.           │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Factory Methods & Convenience API                │  │
│  │  - for_markdown(), for_python(), for_web()        │  │
│  │  - builder(), refresh(), find_file()              │  │
│  │  - sync_with_tab_widget(), reveal_in_file_manager│  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘

App provides custom implementations or uses defaults
All protocols have default implementations for zero-configuration usage
```

### Extension Pattern

All extension points follow the same pattern:

```python
# 1. Protocol defines the contract (typing.Protocol)
class MyHandlerProtocol(Protocol):
    def handle_something(self, data: Any) -> Result: ...

# 2. Default implementation provided
class DefaultMyHandler:
    def handle_something(self, data: Any) -> Result:
        # Built-in behavior
        pass

# 3. App can provide custom implementation
class MyCustomHandler:
    def handle_something(self, data: Any) -> Result:
        # Custom behavior
        pass

# 4. Dependency injection via constructor or setter
workspace = WorkspaceWidget(my_handler=MyCustomHandler())
# or
workspace.set_my_handler(MyCustomHandler())

# 5. Signals emitted for non-blocking notification
workspace.something_happened.connect(my_observer)
```

## File Conflict Handling

### Protocol Definition

```python
from typing import Protocol
from enum import Enum
from pathlib import Path

class FileConflictAction(Enum):
    """Action to take when file conflict detected."""
    RELOAD = "reload"              # Reload file silently
    PROMPT_RELOAD = "prompt"       # Ask user to reload
    IGNORE = "ignore"              # Ignore the change
    CLOSE = "close"                # Close the file
    SHOW_DIFF = "diff"             # Show diff and let user choose

class FileConflictHandler(Protocol):
    """Protocol for handling file conflicts.

    File conflicts occur when:
    - File is modified externally while open in app
    - File is deleted externally while open in app
    - File is moved/renamed externally while open in app
    """

    def handle_file_modified(
        self,
        file_path: str,
        workspace_folder: Optional[str] = None
    ) -> FileConflictAction:
        """Handle file modified externally.

        Args:
            file_path: Absolute path to modified file
            workspace_folder: Workspace folder path (if file is in workspace)

        Returns:
            Action to take (RELOAD, PROMPT_RELOAD, IGNORE)
        """
        ...

    def handle_file_deleted(
        self,
        file_path: str,
        workspace_folder: Optional[str] = None
    ) -> FileConflictAction:
        """Handle file deleted externally.

        Args:
            file_path: Absolute path to deleted file
            workspace_folder: Workspace folder path (if file was in workspace)

        Returns:
            Action to take (CLOSE, IGNORE)
        """
        ...

    def handle_file_moved(
        self,
        old_path: str,
        new_path: str,
        workspace_folder: Optional[str] = None
    ) -> FileConflictAction:
        """Handle file moved/renamed externally.

        Args:
            old_path: Previous absolute path
            new_path: New absolute path
            workspace_folder: Workspace folder path (if file is in workspace)

        Returns:
            Action to take (typically RELOAD with new path)
        """
        ...
```

### Default Implementation

```python
class DefaultFileConflictHandler:
    """Default file conflict handler.

    Strategy:
    - Modified: Prompt user to reload
    - Deleted: Prompt user (keep in memory or close)
    - Moved: Track new path automatically
    """

    def __init__(self, parent: Optional[QWidget] = None):
        self.parent = parent

    def handle_file_modified(
        self,
        file_path: str,
        workspace_folder: Optional[str] = None
    ) -> FileConflictAction:
        """Prompt user to reload modified file."""
        return FileConflictAction.PROMPT_RELOAD

    def handle_file_deleted(
        self,
        file_path: str,
        workspace_folder: Optional[str] = None
    ) -> FileConflictAction:
        """Prompt user when file deleted."""
        # Default: Keep file in memory, warn user
        if self.parent:
            result = QMessageBox.warning(
                self.parent,
                "File Deleted",
                f"File was deleted externally:\n{file_path}\n\n"
                "Keep open in memory or close?",
                QMessageBox.StandardButton.Ignore | QMessageBox.StandardButton.Close
            )
            return (
                FileConflictAction.CLOSE
                if result == QMessageBox.StandardButton.Close
                else FileConflictAction.IGNORE
            )
        return FileConflictAction.CLOSE

    def handle_file_moved(
        self,
        old_path: str,
        new_path: str,
        workspace_folder: Optional[str] = None
    ) -> FileConflictAction:
        """Automatically track moved file."""
        return FileConflictAction.RELOAD  # Reload from new path
```

### Usage Examples

```python
# Example 1: Use default handler (prompts user)
workspace = WorkspaceWidget()
# Uses DefaultFileConflictHandler automatically

# Example 2: Silent auto-reload
class AutoReloadHandler:
    def handle_file_modified(self, file_path, workspace_folder=None):
        return FileConflictAction.RELOAD  # Always reload silently

    def handle_file_deleted(self, file_path, workspace_folder=None):
        return FileConflictAction.CLOSE  # Always close

    def handle_file_moved(self, old_path, new_path, workspace_folder=None):
        return FileConflictAction.RELOAD

workspace.set_conflict_handler(AutoReloadHandler())

# Example 3: Custom diff viewer
class DiffHandler:
    def __init__(self, app):
        self.app = app

    def handle_file_modified(self, file_path, workspace_folder=None):
        # Show diff, let user choose
        return FileConflictAction.SHOW_DIFF

workspace.set_conflict_handler(DiffHandler(app))

# Example 4: Signal-based (non-blocking)
@Slot(str, str)
def on_file_modified(file_path, workspace_folder):
    print(f"File modified: {file_path}")
    # Handle in background, don't block UI

workspace.file_modified.connect(on_file_modified)
```

### Integration with WorkspaceWidget

```python
class WorkspaceWidget(QWidget):
    # Signals for non-blocking notification
    file_modified = Signal(str, str)  # file_path, workspace_folder
    file_deleted = Signal(str, str)   # file_path, workspace_folder
    file_moved = Signal(str, str, str)  # old_path, new_path, workspace_folder

    def __init__(
        self,
        conflict_handler: Optional[FileConflictHandler] = None,
        # ... other params ...
    ):
        super().__init__()

        # Use provided handler or default
        self._conflict_handler = conflict_handler or DefaultFileConflictHandler(self)

        # Setup file watching for conflict detection
        self._file_watcher = QFileSystemWatcher()
        self._file_watcher.fileChanged.connect(self._on_file_changed)
        self._file_watcher.directoryChanged.connect(self._on_directory_changed)

    def set_conflict_handler(self, handler: FileConflictHandler) -> None:
        """Set custom file conflict handler.

        Args:
            handler: Object implementing FileConflictHandler protocol
        """
        self._conflict_handler = handler

    def watch_file(self, file_path: str) -> None:
        """Add file to conflict watch list.

        Apps should call this when opening a file for editing.

        Args:
            file_path: Absolute path to file to watch
        """
        if file_path not in self._file_watcher.files():
            self._file_watcher.addPath(file_path)

    def unwatch_file(self, file_path: str) -> None:
        """Remove file from conflict watch list.

        Apps should call this when closing a file.

        Args:
            file_path: Absolute path to file to stop watching
        """
        if file_path in self._file_watcher.files():
            self._file_watcher.removePath(file_path)

    def _on_file_changed(self, file_path: str):
        """Handle file change detected by watcher."""
        # Determine workspace folder
        workspace_folder = self._get_workspace_for_file(file_path)

        # Check if file still exists
        if not Path(file_path).exists():
            # File deleted
            action = self._conflict_handler.handle_file_deleted(file_path, workspace_folder)
            self.file_deleted.emit(file_path, workspace_folder or "")
        else:
            # File modified
            action = self._conflict_handler.handle_file_modified(file_path, workspace_folder)
            self.file_modified.emit(file_path, workspace_folder or "")

        # Emit signal for app to handle action
        self._apply_conflict_action(file_path, action)

    def _apply_conflict_action(self, file_path: str, action: FileConflictAction):
        """Apply conflict action (emits signals for app to handle)."""
        # Widget only emits signals, app handles the actual action
        if action == FileConflictAction.RELOAD:
            self.file_reload_requested.emit(file_path)
        elif action == FileConflictAction.PROMPT_RELOAD:
            self.file_reload_prompt_requested.emit(file_path)
        elif action == FileConflictAction.CLOSE:
            self.file_close_requested.emit(file_path)
        elif action == FileConflictAction.SHOW_DIFF:
            self.file_diff_requested.emit(file_path)
        # IGNORE: do nothing

    # Additional signals for action requests
    file_reload_requested = Signal(str)         # file_path
    file_reload_prompt_requested = Signal(str)  # file_path
    file_close_requested = Signal(str)          # file_path
    file_diff_requested = Signal(str)           # file_path
```

## Error Handling

### Protocol Definition

```python
from enum import Enum

class ErrorSeverity(Enum):
    """Error severity levels."""
    INFO = "info"          # Informational, no action needed
    WARNING = "warning"    # Warning, user should be aware
    ERROR = "error"        # Error, operation failed
    CRITICAL = "critical"  # Critical, app may be unstable

class ErrorHandler(Protocol):
    """Protocol for handling errors.

    Errors can occur from:
    - Filesystem operations (permission denied, disk full)
    - Config file parsing (invalid JSON, corrupt data)
    - Session file loading (corrupt, incompatible version)
    - Workspace validation (invalid folder, nested workspaces)
    """

    def handle_error(
        self,
        severity: ErrorSeverity,
        message: str,
        exception: Optional[Exception] = None,
        context: Optional[dict] = None
    ) -> bool:
        """Handle an error.

        Args:
            severity: Error severity level
            message: Human-readable error message
            exception: Original exception (if any)
            context: Additional context (file path, operation, etc.)

        Returns:
            True if error was handled, False to propagate
        """
        ...
```

### Default Implementation

```python
class DefaultErrorHandler:
    """Default error handler with logging and user notifications."""

    def __init__(self, parent: Optional[QWidget] = None, logger: Optional[logging.Logger] = None):
        self.parent = parent
        self.logger = logger or logging.getLogger(__name__)

    def handle_error(
        self,
        severity: ErrorSeverity,
        message: str,
        exception: Optional[Exception] = None,
        context: Optional[dict] = None
    ) -> bool:
        """Handle error with logging and optional user notification."""
        # Log the error
        context_str = f" (context: {context})" if context else ""
        if exception:
            self.logger.error(f"{message}{context_str}", exc_info=exception)
        else:
            log_method = {
                ErrorSeverity.INFO: self.logger.info,
                ErrorSeverity.WARNING: self.logger.warning,
                ErrorSeverity.ERROR: self.logger.error,
                ErrorSeverity.CRITICAL: self.logger.critical,
            }[severity]
            log_method(f"{message}{context_str}")

        # Show user notification for WARNING and above
        if severity in (ErrorSeverity.WARNING, ErrorSeverity.ERROR, ErrorSeverity.CRITICAL) and self.parent:
            icon = {
                ErrorSeverity.WARNING: QMessageBox.Icon.Warning,
                ErrorSeverity.ERROR: QMessageBox.Icon.Critical,
                ErrorSeverity.CRITICAL: QMessageBox.Icon.Critical,
            }[severity]

            QMessageBox(icon, "Workspace Error", message, QMessageBox.StandardButton.Ok, self.parent).exec()

        return True  # Error handled
```

### Usage

```python
# Custom error handler that logs to file
class FileErrorHandler:
    def __init__(self, log_file: Path):
        self.log_file = log_file

    def handle_error(self, severity, message, exception=None, context=None):
        with open(self.log_file, 'a') as f:
            f.write(f"[{severity.value}] {message}\n")
        return True

workspace = WorkspaceWidget(error_handler=FileErrorHandler(Path("errors.log")))

# Or via signals (non-blocking)
@Slot(str, str, object)
def on_error(severity, message, exception):
    print(f"[{severity}] {message}")

workspace.error_occurred.connect(on_error)
```

## Icon System

### Protocol Definition

```python
class IconProvider(Protocol):
    """Protocol for providing file/folder icons.

    Allows apps to customize icons based on file type, state, etc.
    """

    def get_file_icon(self, file_info: FileInfo) -> QIcon:
        """Get icon for a file.

        Args:
            file_info: Information about the file

        Returns:
            QIcon to display
        """
        ...

    def get_folder_icon(
        self,
        file_info: FileInfo,
        is_expanded: bool = False
    ) -> QIcon:
        """Get icon for a folder.

        Args:
            file_info: Information about the folder
            is_expanded: True if folder is expanded in tree

        Returns:
            QIcon to display (can differ for open/closed)
        """
        ...

    def get_workspace_folder_icon(
        self,
        workspace_folder: WorkspaceFolder,
        is_expanded: bool = False
    ) -> QIcon:
        """Get icon for a workspace root folder.

        Args:
            workspace_folder: Workspace folder object
            is_expanded: True if folder is expanded

        Returns:
            QIcon to display (typically different from regular folder)
        """
        ...
```

### Default Implementation

```python
class DefaultIconProvider:
    """Default icon provider using Qt theme icons."""

    # File type icon mapping (extension -> icon name)
    FILE_ICONS = {
        ".py": "text-x-python",
        ".js": "text-javascript",
        ".ts": "text-typescript",
        ".html": "text-html",
        ".css": "text-css",
        ".json": "text-x-generic",
        ".xml": "text-xml",
        ".md": "text-x-generic",
        ".txt": "text-x-generic",
        ".pdf": "application-pdf",
        ".jpg": "image-jpeg",
        ".png": "image-png",
        ".svg": "image-svg+xml",
    }

    def get_file_icon(self, file_info: FileInfo) -> QIcon:
        """Get icon based on file extension."""
        extension = file_info.extension
        icon_name = self.FILE_ICONS.get(extension, "text-x-generic")
        icon = QIcon.fromTheme(icon_name)

        # Fallback to generic icon if theme doesn't provide one
        if icon.isNull():
            icon = QIcon.fromTheme("text-x-generic")

        return icon

    def get_folder_icon(self, file_info: FileInfo, is_expanded: bool = False) -> QIcon:
        """Get folder icon (open or closed)."""
        icon_name = "folder-open" if is_expanded else "folder"
        icon = QIcon.fromTheme(icon_name)

        if icon.isNull():
            icon = QIcon.fromTheme("folder")

        return icon

    def get_workspace_folder_icon(
        self,
        workspace_folder: WorkspaceFolder,
        is_expanded: bool = False
    ) -> QIcon:
        """Get workspace folder icon (same as folder but could be different)."""
        # Could use a different icon for workspace roots
        return self.get_folder_icon(
            FileInfo(name=workspace_folder.display_name, relative_path="", is_dir=True),
            is_expanded
        )
```

### Usage

```python
# Custom icon provider with language-specific icons
class CustomIconProvider:
    def get_file_icon(self, file_info: FileInfo) -> QIcon:
        # Load custom SVG icons from resources
        if file_info.extension == ".py":
            return QIcon(":/icons/python.svg")
        elif file_info.extension == ".js":
            return QIcon(":/icons/javascript.svg")
        # ... etc
        return QIcon.fromTheme("text-x-generic")

    def get_folder_icon(self, file_info: FileInfo, is_expanded: bool) -> QIcon:
        # Custom folder icons
        return QIcon(":/icons/folder-open.svg" if is_expanded else ":/icons/folder.svg")

    def get_workspace_folder_icon(self, workspace_folder, is_expanded):
        # Special icon for workspace roots
        return QIcon(":/icons/workspace.svg")

workspace = WorkspaceWidget(icon_provider=CustomIconProvider())
```

## Context Menu System

### Protocol Definition

```python
class ContextMenuProvider(Protocol):
    """Protocol for providing context menu items.

    Allows apps to customize right-click menus for files, folders,
    and workspace roots.
    """

    def get_file_menu_actions(
        self,
        file_info: FileInfo,
        workspace_folder: WorkspaceFolder
    ) -> list[QAction]:
        """Get context menu actions for a file.

        Args:
            file_info: Information about the file
            workspace_folder: Workspace folder containing the file

        Returns:
            List of QAction objects to show in context menu
        """
        ...

    def get_folder_menu_actions(
        self,
        file_info: FileInfo,
        workspace_folder: WorkspaceFolder
    ) -> list[QAction]:
        """Get context menu actions for a folder.

        Args:
            file_info: Information about the folder
            workspace_folder: Workspace folder containing the folder

        Returns:
            List of QAction objects to show in context menu
        """
        ...

    def get_workspace_folder_menu_actions(
        self,
        workspace_folder: WorkspaceFolder
    ) -> list[QAction]:
        """Get context menu actions for a workspace root folder.

        Args:
            workspace_folder: Workspace folder object

        Returns:
            List of QAction objects to show in context menu
        """
        ...
```

### Default Implementation

```python
class DefaultContextMenuProvider:
    """Default context menu provider with common actions."""

    def __init__(self, parent: Optional[QWidget] = None):
        self.parent = parent

    def get_file_menu_actions(
        self,
        file_info: FileInfo,
        workspace_folder: WorkspaceFolder
    ) -> list[QAction]:
        """Provide default file context menu."""
        actions = []

        # Open action
        open_action = QAction("Open", self.parent)
        actions.append(open_action)

        # Separator
        actions.append(None)  # None = separator

        # Reveal in file manager
        reveal_action = QAction("Reveal in File Manager", self.parent)
        actions.append(reveal_action)

        # Copy path
        copy_path_action = QAction("Copy Path", self.parent)
        actions.append(copy_path_action)

        copy_relative_path_action = QAction("Copy Relative Path", self.parent)
        actions.append(copy_relative_path_action)

        # Separator
        actions.append(None)

        # Properties
        properties_action = QAction("Properties", self.parent)
        actions.append(properties_action)

        return actions

    def get_folder_menu_actions(
        self,
        file_info: FileInfo,
        workspace_folder: WorkspaceFolder
    ) -> list[QAction]:
        """Provide default folder context menu."""
        actions = []

        # Expand/Collapse
        expand_action = QAction("Expand All", self.parent)
        actions.append(expand_action)

        collapse_action = QAction("Collapse All", self.parent)
        actions.append(collapse_action)

        # Separator
        actions.append(None)

        # Reveal in file manager
        reveal_action = QAction("Reveal in File Manager", self.parent)
        actions.append(reveal_action)

        # Copy path
        copy_path_action = QAction("Copy Path", self.parent)
        actions.append(copy_path_action)

        return actions

    def get_workspace_folder_menu_actions(
        self,
        workspace_folder: WorkspaceFolder
    ) -> list[QAction]:
        """Provide default workspace folder context menu."""
        actions = []

        # Rename
        rename_action = QAction("Rename Folder", self.parent)
        actions.append(rename_action)

        # Remove from workspace
        remove_action = QAction("Remove from Workspace", self.parent)
        actions.append(remove_action)

        # Separator
        actions.append(None)

        # Add folder to workspace
        add_folder_action = QAction("Add Folder to Workspace...", self.parent)
        actions.append(add_folder_action)

        # Separator
        actions.append(None)

        # Reveal in file manager
        reveal_action = QAction("Reveal in File Manager", self.parent)
        actions.append(reveal_action)

        # Copy path
        copy_path_action = QAction("Copy Path", self.parent)
        actions.append(copy_path_action)

        return actions
```

### Usage Examples

```python
# Example 1: Use default context menu
workspace = WorkspaceWidget()
# Uses DefaultContextMenuProvider automatically

# Example 2: Custom context menu
class MyContextMenuProvider:
    def __init__(self, app_controller):
        self.app = app_controller

    def get_file_menu_actions(self, file_info, workspace_folder):
        actions = []

        # Custom "Open in External Editor" action
        if file_info.extension == ".md":
            action = QAction("Open in Typora", None)
            action.triggered.connect(
                lambda: self.app.open_in_typora(file_info.absolute_path)
            )
            actions.append(action)

        # Default actions
        actions.append(QAction("Reveal in File Manager", None))
        actions.append(QAction("Copy Path", None))

        return actions

    def get_folder_menu_actions(self, file_info, workspace_folder):
        # Custom folder actions
        return [
            QAction("New Markdown File...", None),
            QAction("Export Folder as PDF", None),
        ]

    def get_workspace_folder_menu_actions(self, workspace_folder):
        # Custom workspace actions
        return [
            QAction("Workspace Settings", None),
            QAction("Remove from Workspace", None),
        ]

workspace = WorkspaceWidget(context_menu_provider=MyContextMenuProvider(app))

# Example 3: Extend default menu
class ExtendedContextMenuProvider(DefaultContextMenuProvider):
    def get_file_menu_actions(self, file_info, workspace_folder):
        # Get default actions
        actions = super().get_file_menu_actions(file_info, workspace_folder)

        # Add custom action at the top
        custom_action = QAction("My Custom Action", self.parent)
        actions.insert(0, custom_action)
        actions.insert(1, None)  # Separator

        return actions

workspace = WorkspaceWidget(context_menu_provider=ExtendedContextMenuProvider())
```

### Integration with WorkspaceWidget

```python
class WorkspaceWidget(QWidget):
    """Workspace widget with context menu support."""

    # Signal for manual context menu handling (alternative to protocol)
    context_menu_requested = Signal(QPoint, object, object)
    # position, item (FileInfo or WorkspaceFolder), workspace_folder

    def __init__(
        self,
        context_menu_provider: Optional[ContextMenuProvider] = None,
        # ... other params ...
    ):
        super().__init__()

        # Use provided provider or default
        self._context_menu_provider = context_menu_provider or DefaultContextMenuProvider(self)

    def set_context_menu_provider(self, provider: ContextMenuProvider) -> None:
        """Set custom context menu provider.

        Args:
            provider: Object implementing ContextMenuProvider protocol
        """
        self._context_menu_provider = provider

    def _on_context_menu(self, position: QPoint):
        """Handle context menu request from tree view."""
        # Get item at position
        index = self._tree_view.indexAt(position)
        if not index.isValid():
            return

        item = index.internalPointer()  # FileInfo or WorkspaceFolder
        workspace_folder = self._get_workspace_folder_for_index(index)

        # Get actions from provider
        if isinstance(item, WorkspaceFolder):
            actions = self._context_menu_provider.get_workspace_folder_menu_actions(item)
        elif isinstance(item, FileInfo):
            if item.is_dir:
                actions = self._context_menu_provider.get_folder_menu_actions(
                    item, workspace_folder
                )
            else:
                actions = self._context_menu_provider.get_file_menu_actions(
                    item, workspace_folder
                )
        else:
            return

        # Build and show menu
        menu = QMenu(self)
        for action in actions:
            if action is None:
                menu.addSeparator()
            else:
                menu.addAction(action)

        # Emit signal for additional customization
        self.context_menu_requested.emit(
            self.mapToGlobal(position), item, workspace_folder
        )

        # Show menu
        menu.exec(self.mapToGlobal(position))
```

### Action Connection Pattern

```python
# Helper for connecting context menu actions to app functionality
class MyApp:
    def setup_workspace(self):
        self.workspace = WorkspaceWidget(
            context_menu_provider=MyContextMenuProvider(self)
        )

        # Connect signals for built-in actions
        self.workspace.context_menu_action_triggered.connect(
            self._handle_context_action
        )

    def _handle_context_action(self, action_name: str, item: object):
        """Handle standard context menu actions."""
        if action_name == "reveal_in_file_manager":
            self._reveal_in_file_manager(item)
        elif action_name == "copy_path":
            QApplication.clipboard().setText(item.absolute_path)
        elif action_name == "rename_folder":
            self._rename_workspace_folder(item)
        # ... etc
```

## Workspace Validation

### Protocol Definition

```python
class ValidationResult:
    """Result of workspace validation."""
    def __init__(self, is_valid: bool, error_message: str = "", warnings: list[str] = None):
        self.is_valid = is_valid
        self.error_message = error_message
        self.warnings = warnings or []

class WorkspaceValidator(Protocol):
    """Protocol for validating workspace folders.

    Validation occurs when:
    - Opening a workspace
    - Adding a folder to workspace
    - Detecting external changes
    """

    def validate_workspace_folder(self, folder_path: Path) -> ValidationResult:
        """Validate a folder before adding to workspace.

        Args:
            folder_path: Path to folder to validate

        Returns:
            ValidationResult with is_valid and error/warning messages
        """
        ...

    def validate_workspace_config(
        self,
        config: WorkspaceConfig,
        config_path: Path
    ) -> ValidationResult:
        """Validate workspace configuration file.

        Args:
            config: Loaded configuration object
            config_path: Path to config file

        Returns:
            ValidationResult with is_valid and error/warning messages
        """
        ...
```

### Default Implementation

```python
class DefaultWorkspaceValidator:
    """Default workspace validator with common checks."""

    # System folders that should never be workspaces
    FORBIDDEN_PATHS = ["/", "/bin", "/usr", "/etc", "/sys", "/proc", "/dev"]

    def validate_workspace_folder(self, folder_path: Path) -> ValidationResult:
        """Validate folder with common checks."""
        warnings = []

        # Check: Folder exists
        if not folder_path.exists():
            return ValidationResult(False, f"Folder does not exist: {folder_path}")

        # Check: Is a directory
        if not folder_path.is_dir():
            return ValidationResult(False, f"Not a directory: {folder_path}")

        # Check: Not a system folder
        resolved = folder_path.resolve()
        if str(resolved) in self.FORBIDDEN_PATHS:
            return ValidationResult(False, f"Cannot use system folder as workspace: {resolved}")

        # Check: Readable
        if not os.access(folder_path, os.R_OK):
            return ValidationResult(False, f"Folder is not readable: {folder_path}")

        # Warning: Very large folder
        try:
            file_count = sum(1 for _ in folder_path.rglob("*"))
            if file_count > 10000:
                warnings.append(f"Large workspace ({file_count} items) may be slow")
        except Exception:
            pass  # Ignore errors counting files

        # Warning: Nested workspace
        # (check if folder is inside another workspace)
        parent = folder_path.parent
        while parent != parent.parent:  # Stop at root
            if (parent / ".workspace.json").exists() or (parent / ".reamde-workspace.json").exists():
                warnings.append(f"Workspace is nested inside another workspace at {parent}")
                break
            parent = parent.parent

        return ValidationResult(True, warnings=warnings)

    def validate_workspace_config(
        self,
        config: WorkspaceConfig,
        config_path: Path
    ) -> ValidationResult:
        """Validate configuration object."""
        warnings = []

        # Check: All folders exist
        for folder in config.folders:
            if not Path(folder.path).exists():
                warnings.append(f"Folder in config does not exist: {folder.path}")

        # Check: Version compatibility
        if config.version > 2:
            return ValidationResult(
                False,
                f"Config version {config.version} not supported (max version: 2)"
            )

        return ValidationResult(True, warnings=warnings)
```

### Usage

```python
# Custom validator with project-specific rules
class ProjectValidator:
    def validate_workspace_folder(self, folder_path: Path) -> ValidationResult:
        # Must contain specific files
        if not (folder_path / "README.md").exists():
            return ValidationResult(False, "Project must have README.md")

        # Must not be inside .git folder
        if ".git" in folder_path.parts:
            return ValidationResult(False, "Cannot use .git folder as workspace")

        return ValidationResult(True)

    def validate_workspace_config(self, config, config_path):
        # Project-specific config validation
        if not config.custom_data.get("project_type"):
            return ValidationResult(False, "Config must specify project_type")

        return ValidationResult(True)

workspace = WorkspaceWidget(workspace_validator=ProjectValidator())
```

## Lifecycle Hooks

### Protocol Definition

```python
class WorkspaceLifecycleHooks(Protocol):
    """Protocol for intercepting workspace lifecycle events.

    Allows apps to execute custom logic before and after workspace operations.
    All 'before' hooks can return False to cancel the operation.
    """

    def before_workspace_open(self, folder_path: Path) -> bool:
        """Called before opening a workspace.

        Args:
            folder_path: Path to folder being opened

        Returns:
            True to allow operation, False to cancel
        """
        ...

    def after_workspace_opened(self, folders: list[WorkspaceFolder]) -> None:
        """Called after workspace successfully opened.

        Args:
            folders: List of workspace folders that were opened
        """
        ...

    def before_workspace_close(self) -> bool:
        """Called before closing workspace.

        Returns:
            True to allow operation, False to cancel
        """
        ...

    def after_workspace_closed(self) -> None:
        """Called after workspace closed."""
        ...

    def before_folder_add(self, folder_path: Path) -> bool:
        """Called before adding folder to workspace.

        Args:
            folder_path: Path to folder being added

        Returns:
            True to allow operation, False to cancel
        """
        ...

    def after_folder_added(self, workspace_folder: WorkspaceFolder) -> None:
        """Called after folder added to workspace.

        Args:
            workspace_folder: The folder that was added
        """
        ...

    def before_folder_remove(self, folder_path: str) -> bool:
        """Called before removing folder from workspace.

        Args:
            folder_path: Path to folder being removed

        Returns:
            True to allow operation, False to cancel
        """
        ...

    def after_folder_removed(self, folder_path: str) -> None:
        """Called after folder removed from workspace.

        Args:
            folder_path: Path to folder that was removed
        """
        ...

    def before_config_save(self, config: WorkspaceConfig) -> bool:
        """Called before saving workspace config.

        Args:
            config: Configuration being saved

        Returns:
            True to allow operation, False to cancel
        """
        ...

    def after_config_saved(self, config: WorkspaceConfig, config_path: Path) -> None:
        """Called after config saved.

        Args:
            config: Configuration that was saved
            config_path: Path where config was saved
        """
        ...

    def before_session_save(self, session: WorkspaceSession) -> bool:
        """Called before saving session.

        Args:
            session: Session being saved

        Returns:
            True to allow operation, False to cancel
        """
        ...

    def after_session_saved(self, session: WorkspaceSession) -> None:
        """Called after session saved.

        Args:
            session: Session that was saved
        """
        ...
```

### Default Implementation

```python
class DefaultLifecycleHooks:
    """Default lifecycle hooks (no-op implementation)."""

    def before_workspace_open(self, folder_path: Path) -> bool:
        return True  # Allow operation

    def after_workspace_opened(self, folders: list[WorkspaceFolder]) -> None:
        pass  # No action

    def before_workspace_close(self) -> bool:
        return True

    def after_workspace_closed(self) -> None:
        pass

    def before_folder_add(self, folder_path: Path) -> bool:
        return True

    def after_folder_added(self, workspace_folder: WorkspaceFolder) -> None:
        pass

    def before_folder_remove(self, folder_path: str) -> bool:
        return True

    def after_folder_removed(self, folder_path: str) -> None:
        pass

    def before_config_save(self, config: WorkspaceConfig) -> bool:
        return True

    def after_config_saved(self, config: WorkspaceConfig, config_path: Path) -> None:
        pass

    def before_session_save(self, session: WorkspaceSession) -> bool:
        return True

    def after_session_saved(self, session: WorkspaceSession) -> None:
        pass
```

### Usage Examples

```python
# Example 1: Validate workspace requirements
class RequirementsValidator:
    """Ensure workspace contains required files."""

    def before_workspace_open(self, folder_path: Path) -> bool:
        # Check for required files
        if not (folder_path / "README.md").exists():
            QMessageBox.warning(
                None,
                "Missing README",
                f"Workspace must contain README.md file.\n\n{folder_path}"
            )
            return False  # Cancel open

        return True  # Allow

    def after_workspace_opened(self, folders: list[WorkspaceFolder]) -> None:
        # Log successful open
        logger.info(f"Opened workspace with {len(folders)} folders")

workspace = WorkspaceWidget(lifecycle_hooks=RequirementsValidator())

# Example 2: Prompt user before closing
class CloseConfirmation:
    """Confirm before closing workspace with unsaved changes."""

    def __init__(self, app_controller):
        self.app = app_controller

    def before_workspace_close(self) -> bool:
        # Check for unsaved changes
        if self.app.has_unsaved_changes():
            result = QMessageBox.question(
                None,
                "Unsaved Changes",
                "You have unsaved changes. Close workspace anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            return result == QMessageBox.StandardButton.Yes

        return True

workspace = WorkspaceWidget(lifecycle_hooks=CloseConfirmation(app))

# Example 3: Auto-save on close
class AutoSaveHooks:
    """Automatically save session and config on close."""

    def __init__(self, app_controller):
        self.app = app_controller

    def before_workspace_close(self) -> bool:
        # Auto-save all open files
        self.app.save_all_files()
        return True

    def after_workspace_closed(self) -> None:
        # Clean up resources
        self.app.cleanup_workspace_resources()

workspace = WorkspaceWidget(lifecycle_hooks=AutoSaveHooks(app))

# Example 4: Track workspace analytics
class AnalyticsHooks:
    """Track workspace usage for analytics."""

    def after_workspace_opened(self, folders: list[WorkspaceFolder]) -> None:
        # Track workspace open event
        analytics.track("workspace_opened", {
            "folder_count": len(folders),
            "primary_folder": folders[0].path if folders else None
        })

    def after_folder_added(self, workspace_folder: WorkspaceFolder) -> None:
        analytics.track("folder_added_to_workspace")

    def after_workspace_closed(self) -> None:
        analytics.track("workspace_closed")

workspace = WorkspaceWidget(lifecycle_hooks=AnalyticsHooks())

# Example 5: Partial implementation (only implement needed hooks)
class CustomHooks:
    """Only implement the hooks you need."""

    def before_folder_add(self, folder_path: Path) -> bool:
        # Custom logic for folder add
        if self._is_blacklisted(folder_path):
            return False
        return True

    # Other hooks not implemented - widget uses defaults

workspace = WorkspaceWidget(lifecycle_hooks=CustomHooks())
```

### Integration with WorkspaceWidget

```python
class WorkspaceWidget(QWidget):
    """Workspace widget with lifecycle hooks support."""

    def __init__(
        self,
        lifecycle_hooks: Optional[WorkspaceLifecycleHooks] = None,
        # ... other params ...
    ):
        super().__init__()

        # Use provided hooks or default (no-op)
        self._lifecycle_hooks = lifecycle_hooks or DefaultLifecycleHooks()

    def set_lifecycle_hooks(self, hooks: WorkspaceLifecycleHooks) -> None:
        """Set custom lifecycle hooks.

        Args:
            hooks: Object implementing WorkspaceLifecycleHooks protocol
        """
        self._lifecycle_hooks = hooks

    def open_workspace(self, folder_path: Path) -> bool:
        """Open workspace with lifecycle hooks."""
        # Before hook
        if not self._lifecycle_hooks.before_workspace_open(folder_path):
            logger.info(f"Workspace open cancelled by lifecycle hook: {folder_path}")
            return False  # Cancelled by hook

        # Perform operation
        try:
            # ... actual workspace open logic ...
            folders = self._manager.open_workspace(folder_path)
        except Exception as e:
            # Handle error, don't call after hook
            self._error_handler.handle_error(
                ErrorSeverity.ERROR,
                f"Failed to open workspace: {e}",
                exception=e
            )
            return False

        # After hook (only called if operation succeeded)
        self._lifecycle_hooks.after_workspace_opened(folders)

        return True

    def close_workspace(self) -> None:
        """Close workspace with lifecycle hooks."""
        # Before hook
        if not self._lifecycle_hooks.before_workspace_close():
            logger.info("Workspace close cancelled by lifecycle hook")
            return  # Cancelled by hook

        # Perform operation
        self._manager.close_workspace()

        # After hook
        self._lifecycle_hooks.after_workspace_closed()

    # Similar pattern for all other lifecycle operations...
```

### Combining Hooks with Signals

```python
# Hooks and signals serve different purposes:
# - Hooks: Intercept and potentially cancel operations
# - Signals: Observe operations (non-blocking, can't cancel)

class MyApp:
    def setup_workspace(self):
        # Use hooks for validation/cancellation
        self.workspace = WorkspaceWidget(
            lifecycle_hooks=MyLifecycleHooks(self)
        )

        # Use signals for observation/updates
        self.workspace.workspace_opened.connect(self._on_workspace_opened)
        self.workspace.workspace_closed.connect(self._on_workspace_closed)

    def _on_workspace_opened(self, folders: list[WorkspaceFolder]):
        # Update UI, load additional data, etc.
        # Cannot cancel operation (already done)
        self.statusBar().showMessage(f"Opened workspace with {len(folders)} folders")

# Both hooks AND signals are called:
# 1. before_workspace_open() hook - can cancel
# 2. Actual workspace open operation
# 3. after_workspace_opened() hook
# 4. workspace_opened signal emitted
```

## Active File Tracking

### Public API

```python
class WorkspaceWidget(QWidget):
    """Workspace widget with active file tracking."""

    # Signal emitted when active file changes in UI
    active_file_changed = Signal(str)  # file_path

    def highlight_file(self, file_path: str) -> bool:
        """Highlight a file in the tree (e.g., current tab).

        Selects the file in the tree view without expanding folders or scrolling.

        Args:
            file_path: Absolute path to file to highlight

        Returns:
            True if file was found and highlighted, False otherwise
        """
        pass

    def reveal_file(self, file_path: str) -> bool:
        """Reveal a file in the tree (expand folders, scroll to show).

        Expands parent folders and scrolls to make the file visible,
        then highlights it.

        Args:
            file_path: Absolute path to file to reveal

        Returns:
            True if file was found and revealed, False otherwise
        """
        pass

    def get_highlighted_file(self) -> Optional[str]:
        """Get currently highlighted file path.

        Returns:
            Absolute path to highlighted file, or None if no selection
        """
        pass

    def clear_highlight(self) -> None:
        """Clear current file highlight."""
        pass
```

### Usage

```python
# Sync workspace selection with active tab
@Slot(int)
def on_tab_changed(index: int):
    """When tab changes, highlight file in workspace."""
    if index >= 0:
        widget = tabs.widget(index)
        if hasattr(widget, 'file_path') and widget.file_path:
            workspace.highlight_file(str(widget.file_path))

tabs.currentChanged.connect(on_tab_changed)

# Reveal file when opening from external source
def open_file_from_external(file_path: str):
    """Open file and reveal in workspace."""
    # Open the file
    open_in_editor(file_path)

    # Reveal in workspace tree
    workspace.reveal_file(file_path)
```

## Keyboard Navigation

### Default Keyboard Shortcuts

The widget provides standard tree navigation (handled by QTreeView):

| Key | Action |
|-----|--------|
| **Arrow Up/Down** | Navigate between items |
| **Arrow Left** | Collapse folder (or move to parent) |
| **Arrow Right** | Expand folder (or move to first child) |
| **Home** | Jump to first item |
| **End** | Jump to last item |
| **Page Up/Down** | Scroll one page |
| **Enter/Return** | Open selected file |
| **Space** | Toggle folder expand/collapse |
| **Type-ahead** | Jump to item by typing name |
| **Ctrl+F** | Focus search/filter (if enabled) |
| **F5** | Refresh workspace |
| **Delete** | Context menu delete (if enabled) |
| **F2** | Rename (if enabled) |

### Customization

```python
class WorkspaceWidget(QWidget):
    """Workspace widget with customizable keyboard shortcuts."""

    def set_keyboard_shortcuts(self, shortcuts: dict[str, str]) -> None:
        """Set custom keyboard shortcuts.

        Args:
            shortcuts: Mapping of action -> key sequence
                      e.g., {"refresh": "F5", "search": "Ctrl+F"}
        """
        pass

    def enable_type_ahead(self, enabled: bool = True) -> None:
        """Enable/disable type-ahead search.

        When enabled, typing letters jumps to matching file names.

        Args:
            enabled: True to enable, False to disable
        """
        pass
```

### Integration with keybinding_manager

```python
# Future integration with vfwidgets-keybinding_manager
from vfwidgets_keybinding_manager import KeybindingManager

keybindings = KeybindingManager()
keybindings.bind("workspace.refresh", "F5", workspace.refresh)
keybindings.bind("workspace.search", "Ctrl+F", workspace.show_search)
keybindings.bind("workspace.reveal_active", "Ctrl+K R", lambda: workspace.reveal_file(current_file))
```

## Recent Workspaces

### Data Structure

```python
@dataclass
class RecentWorkspace:
    """Information about a recently opened workspace."""
    path: str  # Absolute path to primary folder
    name: str  # Workspace name (from config or basename)
    folder_count: int  # Number of folders in workspace
    last_opened: str  # ISO format timestamp: "2025-10-24T10:30:00"

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "name": self.name,
            "folder_count": self.folder_count,
            "last_opened": self.last_opened
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RecentWorkspace":
        return cls(
            path=data["path"],
            name=data["name"],
            folder_count=data.get("folder_count", 1),
            last_opened=data["last_opened"]
        )

# Storage format: ~/.config/<app>/workspaces/recent.json
{
    "version": 1,
    "recent": [
        {
            "path": "/home/user/docs",
            "name": "docs",
            "folder_count": 2,
            "last_opened": "2025-10-24T10:30:00"
        },
        {
            "path": "/home/user/notes",
            "name": "notes",
            "folder_count": 1,
            "last_opened": "2025-10-23T15:20:00"
        }
    ],
    "max_recent": 10
}
```

### Public API

```python
class WorkspaceWidget(QWidget):
    """Workspace widget with recent workspaces support."""

    # Signal when recent list changes
    recent_workspaces_changed = Signal()

    def get_recent_workspaces(self, max_count: int = 10) -> list[RecentWorkspace]:
        """Get list of recently opened workspaces.

        Args:
            max_count: Maximum number to return

        Returns:
            List of RecentWorkspace objects, sorted by last_opened (newest first)
        """
        pass

    def add_recent_workspace(self, workspace_path: str, name: str, folder_count: int = 1) -> None:
        """Add workspace to recent list (or update timestamp if exists).

        Args:
            workspace_path: Absolute path to primary folder
            name: Workspace name
            folder_count: Number of folders in workspace
        """
        pass

    def remove_recent_workspace(self, workspace_path: str) -> None:
        """Remove workspace from recent list.

        Args:
            workspace_path: Absolute path to workspace to remove
        """
        pass

    def clear_recent_workspaces(self) -> None:
        """Clear all recent workspaces."""
        pass
```

### Automatic Cleanup

```python
# On load, remove non-existent folders
def _load_recent_workspaces(self) -> list[RecentWorkspace]:
    """Load recent workspaces and clean up invalid entries."""
    recents = self._read_recent_file()

    # Filter out non-existent paths
    valid_recents = [
        r for r in recents
        if Path(r.path).exists()
    ]

    # If list changed, save cleaned version
    if len(valid_recents) != len(recents):
        self._save_recent_file(valid_recents)

    return valid_recents
```

## Model: MultiRootFileSystemModel

Custom `QAbstractItemModel` for displaying multiple folder roots in a tree.

### Architecture

```
Model Structure (Example with 2 workspace folders):

(root - invalid QModelIndex)
├─ WorkspaceFolder "docs"         [row 0, col 0, parent=invalid]
│  ├─ folder: getting-started/    [row 0, col 0, parent=docs_index]
│  │  ├─ file: install.md         [row 0, col 0, parent=getting-started_index]
│  │  └─ file: quickstart.md      [row 1, col 0, parent=getting-started_index]
│  ├─ folder: api/                [row 1, col 0, parent=docs_index]
│  └─ file: README.md             [row 2, col 0, parent=docs_index]
│
└─ WorkspaceFolder "examples"     [row 1, col 0, parent=invalid]
   ├─ file: basic.py              [row 0, col 0, parent=examples_index]
   └─ file: advanced.py           [row 1, col 0, parent=examples_index]
```

### Key Features

- **Lazy loading**: Filesystem data populated on-demand
- **Caching**: `_filesystem_cache: dict[str, dict[str, FileInfo]]`
- **Filtering**: Extensions + custom callback
- **Watching**: `QFileSystemWatcher` for auto-refresh
- **Sorting**: Folders-first, alphabetical

### File Filtering API

```python
# Built-in extension filtering
model.set_file_extensions([".py", ".js", ".ts"])

# Custom filter callback (optional, for advanced cases)
def my_filter(file_info: FileInfo, workspace_folder: WorkspaceFolder) -> bool:
    """Custom filter: only Python files > 1KB."""
    return file_info.extension == ".py" and file_info.size > 1024

model.set_filter_callback(my_filter)

# Both filters are AND-ed together:
# - File must match extension (if extensions specified)
# - File must pass callback (if callback specified)
```

### Implementation Skeleton

```python
class MultiRootFileSystemModel(QAbstractItemModel):
    """Custom model for multi-root file tree.

    See multi-folder-mvc-DESIGN.md for full implementation.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._folders: list[WorkspaceFolder] = []
        self._filesystem_cache: dict[str, dict[str, FileInfo]] = {}
        self._watcher = QFileSystemWatcher()

        # Filtering
        self._file_extensions: list[str] = []
        self._excluded_folders: list[str] = []
        self._filter_callback: Optional[Callable[[FileInfo, WorkspaceFolder], bool]] = None

    # File filtering API
    def set_file_extensions(self, extensions: list[str]) -> None:
        """Set file extensions to show (e.g., [".md", ".txt"])."""
        self._file_extensions = [ext.lower() for ext in extensions]
        self._refresh_all()

    def set_excluded_folders(self, folders: list[str]) -> None:
        """Set folders to exclude (e.g., ["node_modules", ".git"])."""
        self._excluded_folders = folders
        self._refresh_all()

    def set_filter_callback(
        self,
        callback: Optional[Callable[[FileInfo, WorkspaceFolder], bool]]
    ) -> None:
        """Set custom filter callback.

        Args:
            callback: Function that takes (FileInfo, WorkspaceFolder) and returns bool.
                     Return True to include file, False to exclude.
                     If None, only extension filtering applies.
        """
        self._filter_callback = callback
        self._refresh_all()

    # Workspace folder management
    def set_folders(self, folders: list[WorkspaceFolder]) -> None:
        """Set the workspace folders to display."""
        self.beginResetModel()

        # Clear old watchers
        if self._watcher.directories():
            self._watcher.removePaths(self._watcher.directories())

        self._folders = folders
        self._filesystem_cache.clear()

        # Setup watchers and populate cache for new folders
        for folder in folders:
            self._watch_folder_recursive(folder.path)
            self._populate_cache(folder.path)

        self.endResetModel()

    # QAbstractItemModel interface
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Return number of rows under parent."""
        # Implementation: see multi-folder-mvc-DESIGN.md
        pass

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Return number of columns (always 1 for tree)."""
        return 1

    def parent(self, index: QModelIndex) -> QModelIndex:
        """Return parent of given index."""
        # Implementation: see multi-folder-mvc-DESIGN.md
        pass

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        """Create index for given row, column, parent."""
        # Implementation: see multi-folder-mvc-DESIGN.md
        pass

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Return data for given index and role."""
        # Implementation: see multi-folder-mvc-DESIGN.md
        pass

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        """Return flags for index."""
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
```

## View: FileExplorerWidget

Tree view widget with theme integration.

### Features

- **ThemedWidget integration** (automatic VS Code theming)
- **Signals** for file selection, folder expansion
- **No business logic** (pure view)
- **Fallback theme** when vfwidgets-theme not available

### Implementation

```python
# Conditional base class (depends on vfwidgets-theme availability)
try:
    from vfwidgets_theme import ThemedWidget
    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False
    ThemedWidget = object  # type: ignore

if THEME_AVAILABLE:
    _BaseClass = type("_BaseClass", (ThemedWidget, QWidget), {})
else:
    _BaseClass = QWidget

class FileExplorerWidget(_BaseClass):
    """File tree view with theme integration.

    Pure view component - no business logic.
    """

    # Signals
    file_selected = Signal(str)  # Absolute file path
    file_double_clicked = Signal(str)  # Absolute file path
    folder_expanded = Signal(str, str)  # workspace_folder_path, relative_path
    folder_collapsed = Signal(str, str)  # workspace_folder_path, relative_path
    context_menu_requested = Signal(QPoint, object)  # position, FileInfo or WorkspaceFolder

    # Theme configuration (VS Code tokens)
    theme_config = {
        "background": "sideBar.background",
        "foreground": "sideBar.foreground",
        "selection_bg": "list.activeSelectionBackground",
        "selection_fg": "list.activeSelectionForeground",
        "inactive_selection_bg": "list.inactiveSelectionBackground",
        "hover_bg": "list.hoverBackground",
        "border": "sideBar.border",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tree_view: Optional[QTreeView] = None
        self._model: Optional[MultiRootFileSystemModel] = None
        self._setup_ui()

    def set_model(self, model: MultiRootFileSystemModel) -> None:
        """Set the model for tree view."""
        self._model = model
        self._tree_view.setModel(model)

    def theme_changed(self):
        """Apply theme colors to tree view (called by ThemedWidget)."""
        if not THEME_AVAILABLE:
            return

        # Get theme colors
        bg = self.get_theme_color("background")
        fg = self.get_theme_color("foreground")
        sel_bg = self.get_theme_color("selection_bg")
        sel_fg = self.get_theme_color("selection_fg")
        inactive_sel_bg = self.get_theme_color("inactive_selection_bg")
        hover_bg = self.get_theme_color("hover_bg")

        # Apply via stylesheet
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
```

## Controller: WorkspaceManager

Manages workspace lifecycle and configuration.

### Responsibilities

- Open/close workspace
- Add/remove/rename folders
- Load/save configuration
- Session management (hybrid approach)
- Emit signals for integration

### Implementation

```python
class WorkspaceManager(QObject):
    """Controller for workspace operations.

    Provides built-in session management (hybrid approach):
    - Default: saves sessions automatically to ~/.config/<app>/workspaces/
    - Override: apps can provide custom session storage
    """

    # Signals
    workspace_opened = Signal(list)  # list[WorkspaceFolder]
    workspace_closed = Signal()
    folder_added = Signal(object)  # WorkspaceFolder
    folder_removed = Signal(str)  # folder_path
    config_changed = Signal(object)  # WorkspaceConfig

    def __init__(
        self,
        config_class: type = WorkspaceConfig,
        config_filename: str = ".workspace.json",
        session_dir: Optional[Path] = None,
        parent: Optional[QObject] = None
    ):
        """Initialize workspace manager.

        Args:
            config_class: Config class (WorkspaceConfig or subclass)
            config_filename: Name of workspace config file
            session_dir: Directory for session files (default: ~/.config/<app>/workspaces/)
            parent: Parent QObject
        """
        super().__init__(parent)
        self._config_class = config_class
        self._config_filename = config_filename
        self._session_dir = session_dir

        self._folders: list[WorkspaceFolder] = []
        self._config: Optional[WorkspaceConfig] = None

    # Workspace lifecycle
    def open_workspace(self, folder_path: Path) -> bool:
        """Open a folder as workspace (single folder initially)."""
        pass

    def close_workspace(self) -> None:
        """Close current workspace."""
        pass

    # Multi-folder operations
    def add_folder(self, folder_path: Path, name: Optional[str] = None) -> bool:
        """Add a folder to existing workspace."""
        pass

    def remove_folder(self, folder_path: str) -> bool:
        """Remove a folder from workspace."""
        pass

    def rename_folder(self, folder_path: str, new_name: str) -> bool:
        """Set custom display name for a folder."""
        pass

    # Session management (hybrid approach)
    def save_session(self, session: WorkspaceSession) -> None:
        """Save workspace session (default implementation).

        Apps can override this for custom session storage.
        """
        pass

    def load_session(self) -> Optional[WorkspaceSession]:
        """Load workspace session (default implementation).

        Apps can override this for custom session retrieval.
        """
        pass

    # Configuration
    def load_config(self) -> Optional[WorkspaceConfig]:
        """Load workspace config from first folder."""
        pass

    def save_config(self, config: WorkspaceConfig) -> None:
        """Save workspace config to first folder."""
        pass
```

## Main API: WorkspaceWidget

Facade that combines all components.

### Usage Example (Generic)

```python
from vfwidgets_workspace import WorkspaceWidget

# Create widget for Python files
workspace = WorkspaceWidget(
    file_extensions=[".py", ".pyi", ".pyx"],
    excluded_folders=["__pycache__", ".venv", "venv"],
    config_filename=".myapp-workspace.json"
)

# Connect signals
workspace.file_selected.connect(lambda path: print(f"Selected: {path}"))
workspace.workspace_opened.connect(lambda folders: print(f"Opened: {folders}"))

# Add to UI (e.g., ViloCodeWindow sidebar)
main_window.add_sidebar_panel("explorer", workspace, "FILES")

# Open workspace programmatically
workspace.open_workspace(Path("/home/user/myproject"))

# Or let user choose via file dialog
folder = QFileDialog.getExistingDirectory(None, "Open Workspace")
if folder:
    workspace.open_workspace(Path(folder))
```

### Usage Example (with Custom Filter)

```python
from vfwidgets_workspace import WorkspaceWidget, FileInfo, WorkspaceFolder

def my_custom_filter(file_info: FileInfo, workspace_folder: WorkspaceFolder) -> bool:
    """Only show Python files larger than 1KB."""
    return file_info.extension == ".py" and file_info.size > 1024

workspace = WorkspaceWidget(
    file_extensions=[".py"],  # Pre-filter by extension
    filter_callback=my_custom_filter  # Then apply custom logic
)
```

### Usage Example (with Extended Config)

```python
from vfwidgets_workspace import WorkspaceWidget, WorkspaceConfig
from dataclasses import dataclass

@dataclass
class MyAppWorkspaceConfig(WorkspaceConfig):
    """App-specific workspace configuration."""

    # Add app-specific fields
    enable_linting: bool = True
    linter_config: str = "pyproject.toml"
    auto_format_on_save: bool = False

workspace = WorkspaceWidget(
    config_class=MyAppWorkspaceConfig,
    config_filename=".myapp-workspace.json"
)

# Access extended config
config = workspace.get_config()
if config.enable_linting:
    print(f"Linter config: {config.linter_config}")
```

### Complete API

```python
class WorkspaceWidget(QWidget):
    """Main workspace widget (facade).

    Combines MultiRootFileSystemModel, FileExplorerWidget, and WorkspaceManager
    into a single, easy-to-use component.
    """

    # Signals (forwarded from components)
    file_selected = Signal(str)
    file_double_clicked = Signal(str)
    folder_expanded = Signal(str, str)
    folder_collapsed = Signal(str, str)
    workspace_opened = Signal(list)  # list[WorkspaceFolder]
    workspace_closed = Signal()
    folder_added = Signal(object)  # WorkspaceFolder
    folder_removed = Signal(str)
    context_menu_requested = Signal(QPoint, object)

    def __init__(
        self,
        file_extensions: Optional[list[str]] = None,
        excluded_folders: Optional[list[str]] = None,
        filter_callback: Optional[Callable[[FileInfo, WorkspaceFolder], bool]] = None,
        config_class: type = WorkspaceConfig,
        config_filename: str = ".workspace.json",
        session_dir: Optional[Path] = None,
        parent: Optional[QWidget] = None
    ):
        """Initialize workspace widget.

        Args:
            file_extensions: File extensions to show (None = all files)
                            Example: [".py", ".pyi"]
            excluded_folders: Folders to exclude from tree
                             Example: ["__pycache__", "node_modules"]
            filter_callback: Custom filter function (file_info, folder) -> bool
                            Return True to include, False to exclude
            config_class: Config class (WorkspaceConfig or subclass)
            config_filename: Name of workspace config file
            session_dir: Directory for session files (None = default)
            parent: Parent widget
        """
        pass

    # Workspace operations
    def open_workspace(self, folder_path: Path) -> bool:
        """Open a folder as workspace."""
        pass

    def close_workspace(self) -> None:
        """Close current workspace."""
        pass

    def add_folder(self, folder_path: Path, name: Optional[str] = None) -> bool:
        """Add folder to existing workspace."""
        pass

    def remove_folder(self, folder_path: str) -> bool:
        """Remove folder from workspace."""
        pass

    def rename_folder(self, folder_path: str, new_name: str) -> bool:
        """Set custom display name for a folder."""
        pass

    # Query state
    def is_workspace_open(self) -> bool:
        """Check if workspace is currently open."""
        pass

    def get_folders(self) -> list[WorkspaceFolder]:
        """Get list of workspace folders."""
        pass

    def get_config(self) -> Optional[WorkspaceConfig]:
        """Get current workspace configuration."""
        pass

    # Session management (hybrid - apps can override)
    def save_session(self) -> WorkspaceSession:
        """Save and return current session state."""
        pass

    def restore_session(self, session: WorkspaceSession) -> None:
        """Restore session state (expanded folders, scroll, etc.)."""
        pass

    # File filtering (can be changed at runtime)
    def set_file_extensions(self, extensions: list[str]) -> None:
        """Change file extensions filter."""
        pass

    def set_excluded_folders(self, folders: list[str]) -> None:
        """Change excluded folders."""
        pass

    def set_filter_callback(
        self,
        callback: Optional[Callable[[FileInfo, WorkspaceFolder], bool]]
    ) -> None:
        """Set or clear custom filter callback."""
        pass

    # ========================================================================
    # Factory Methods (Class Methods for Pre-configured Instances)
    # ========================================================================

    @classmethod
    def for_markdown(cls, parent: Optional[QWidget] = None) -> "WorkspaceWidget":
        """Create workspace pre-configured for Markdown files.

        Pre-configured settings:
        - Extensions: [".md", ".markdown", ".mdown"]
        - Excluded: [".git", "node_modules", "__pycache__"]
        - Config file: ".reamde-workspace.json"

        Args:
            parent: Parent widget

        Returns:
            WorkspaceWidget instance configured for Markdown
        """
        pass

    @classmethod
    def for_python(cls, parent: Optional[QWidget] = None) -> "WorkspaceWidget":
        """Create workspace pre-configured for Python projects.

        Pre-configured settings:
        - Extensions: [".py", ".pyi", ".pyx"]
        - Excluded: ["__pycache__", ".venv", "venv", "build", "dist", ".pytest_cache", ".mypy_cache"]
        - Config file: ".workspace.json"

        Args:
            parent: Parent widget

        Returns:
            WorkspaceWidget instance configured for Python
        """
        pass

    @classmethod
    def for_web(cls, parent: Optional[QWidget] = None) -> "WorkspaceWidget":
        """Create workspace pre-configured for web development.

        Pre-configured settings:
        - Extensions: [".html", ".css", ".js", ".ts", ".jsx", ".tsx", ".vue"]
        - Excluded: ["node_modules", "dist", "build", ".cache", ".next"]
        - Config file: ".workspace.json"

        Args:
            parent: Parent widget

        Returns:
            WorkspaceWidget instance configured for web development
        """
        pass

    @classmethod
    def for_javascript(cls, parent: Optional[QWidget] = None) -> "WorkspaceWidget":
        """Create workspace pre-configured for JavaScript/TypeScript projects.

        Pre-configured settings:
        - Extensions: [".js", ".ts", ".jsx", ".tsx", ".json", ".mjs"]
        - Excluded: ["node_modules", "dist", "build", ".cache"]
        - Config file: ".workspace.json"

        Args:
            parent: Parent widget

        Returns:
            WorkspaceWidget instance configured for JavaScript
        """
        pass

    @classmethod
    def for_all_files(cls, parent: Optional[QWidget] = None) -> "WorkspaceWidget":
        """Create workspace showing all files (no filtering).

        Pre-configured settings:
        - Extensions: None (show all)
        - Excluded: [".git", "__pycache__"]
        - Config file: ".workspace.json"

        Args:
            parent: Parent widget

        Returns:
            WorkspaceWidget instance showing all files
        """
        pass

    @classmethod
    def empty(cls, parent: Optional[QWidget] = None) -> "WorkspaceWidget":
        """Create workspace with minimal configuration.

        No pre-configured settings - requires manual configuration.

        Args:
            parent: Parent widget

        Returns:
            WorkspaceWidget instance with no defaults
        """
        pass

    @classmethod
    def builder(cls) -> "WorkspaceWidgetBuilder":
        """Create a builder for fluent configuration.

        Returns:
            WorkspaceWidgetBuilder instance

        Example:
            workspace = (
                WorkspaceWidget.builder()
                .with_extensions([".py"])
                .exclude_folders(["__pycache__"])
                .with_auto_watch()
                .build()
            )
        """
        pass

    # ========================================================================
    # Convenience API (Helper Methods for Common Operations)
    # ========================================================================

    def refresh(self) -> None:
        """Refresh workspace tree from filesystem.

        Reloads all folders and files, updates the tree view.
        Preserves expanded state if possible.
        """
        pass

    def expand_all(self) -> None:
        """Expand all folders in the tree."""
        pass

    def collapse_all(self) -> None:
        """Collapse all folders in the tree."""
        pass

    def find_file(self, filename: str, fuzzy: bool = False) -> list[str]:
        """Find file(s) by name in workspace.

        Args:
            filename: File name to search for (e.g., "README.md")
            fuzzy: If True, use fuzzy matching (e.g., "readm" matches "README.md")

        Returns:
            List of absolute paths to matching files
        """
        pass

    def get_all_files(self, folder_path: Optional[str] = None) -> list[str]:
        """Get all files in workspace (flat list).

        Args:
            folder_path: If provided, only get files from this workspace folder

        Returns:
            List of absolute file paths
        """
        pass

    def is_file_in_workspace(self, file_path: str) -> bool:
        """Check if file path is part of any workspace folder.

        Args:
            file_path: Absolute path to file

        Returns:
            True if file is in workspace, False otherwise
        """
        pass

    def get_workspace_folder_for_file(self, file_path: str) -> Optional[WorkspaceFolder]:
        """Get workspace folder that contains this file.

        Args:
            file_path: Absolute path to file

        Returns:
            WorkspaceFolder containing the file, or None if not in workspace
        """
        pass

    def get_relative_path(
        self,
        file_path: str,
        workspace_folder: Optional[str] = None
    ) -> Optional[str]:
        """Get path relative to workspace folder.

        Args:
            file_path: Absolute path to file
            workspace_folder: Workspace folder path (if None, auto-detect)

        Returns:
            Relative path from workspace folder, or None if not in workspace
        """
        pass

    def reveal_in_file_manager(self, file_path: str) -> bool:
        """Open file manager and select this file.

        Platform-aware implementation:
        - Windows: Opens Explorer with file selected
        - macOS: Opens Finder with file selected
        - Linux: Opens default file manager with file selected

        Args:
            file_path: Absolute path to file

        Returns:
            True if successful, False otherwise
        """
        pass

    # ========================================================================
    # Tab Integration Helpers
    # ========================================================================

    def sync_with_tab_widget(
        self,
        tab_widget: QTabWidget,
        file_path_attr: str = "file_path",
        auto_sync: bool = True
    ) -> None:
        """Automatically sync workspace selection with tab widget.

        Args:
            tab_widget: QTabWidget or ChromeTabbedWindow to sync with
            file_path_attr: Attribute name on tab widgets containing file path
                           (default: "file_path")
            auto_sync: If True, automatically highlights file when tab changes

        Example:
            workspace.sync_with_tab_widget(self.tabs, file_path_attr="file_path")
            # Now when you switch tabs, workspace highlights the active file
        """
        pass

    def set_active_file(self, file_path: str) -> bool:
        """Set active file (highlights and reveals in tree).

        Combines highlight_file() and reveal_file() into single call.

        Args:
            file_path: Absolute path to file

        Returns:
            True if file was found and set as active, False otherwise
        """
        pass

    # ========================================================================
    # File Watching Configuration
    # ========================================================================

    def set_auto_watch_mode(self, mode: "AutoWatchMode") -> None:
        """Set automatic file watching mode.

        Args:
            mode: AutoWatchMode enum value

        Modes:
            - MANUAL: App must call watch_file() manually (default)
            - AUTO_ON_SELECT: Automatically watch when file_selected emitted
            - AUTO_ON_OPEN: Automatically watch when app signals file opened
        """
        pass

    def enable_auto_watch(self, enabled: bool = True) -> None:
        """Enable/disable automatic file watching.

        Shortcut for set_auto_watch_mode(AUTO_ON_SELECT).

        Args:
            enabled: True to enable auto-watch, False to disable
        """
        pass

    # ========================================================================
    # Filter Configuration Helpers
    # ========================================================================

    def set_filter_enabled(self, enabled: bool) -> None:
        """Enable or disable file filtering temporarily.

        Args:
            enabled: True to enable filtering, False to show all files

        Note:
            When disabled, all files are shown (except excluded folders).
            Filter configuration is preserved and reapplied when re-enabled.
        """
        pass

    def set_excluded_extensions(self, extensions: list[str]) -> None:
        """Set file extensions to HIDE (inverse of set_file_extensions).

        Args:
            extensions: List of extensions to exclude (e.g., [".pyc", ".log"])

        Note:
            This is mutually exclusive with set_file_extensions().
            Calling one clears the other.
        """
        pass

    # ========================================================================
    # Error Recovery
    # ========================================================================

    def reset_to_defaults(self) -> None:
        """Reset workspace to default state.

        Clears corrupt config, resets UI to defaults, keeps workspace open.
        Useful for recovering from errors.
        """
        pass

    def recover_from_error(self) -> bool:
        """Attempt to recover from error state.

        Tries to:
        - Reload corrupt config from backup
        - Reset session to clean state
        - Refresh filesystem model

        Returns:
            True if recovered successfully, False if manual intervention needed
        """
        pass
```

## Workspace Widget Builder

For complex configurations, use the builder pattern:

```python
class WorkspaceWidgetBuilder:
    """Builder for creating WorkspaceWidget with fluent API."""

    def __init__(self):
        self._file_extensions: Optional[list[str]] = None
        self._excluded_folders: Optional[list[str]] = None
        self._config_filename: str = ".workspace.json"
        self._auto_watch: bool = False
        self._auto_recovery: bool = False
        self._conflict_handler: Optional[FileConflictHandler] = None
        self._error_handler: Optional[ErrorHandler] = None
        self._icon_provider: Optional[IconProvider] = None
        self._lifecycle_hooks: Optional[WorkspaceLifecycleHooks] = None
        self._parent: Optional[QWidget] = None

    def with_extensions(self, extensions: list[str]) -> "WorkspaceWidgetBuilder":
        """Set file extensions filter."""
        self._file_extensions = extensions
        return self

    def exclude_folders(self, folders: list[str]) -> "WorkspaceWidgetBuilder":
        """Set folders to exclude."""
        self._excluded_folders = folders
        return self

    def with_config_file(self, filename: str) -> "WorkspaceWidgetBuilder":
        """Set config filename."""
        self._config_filename = filename
        return self

    def with_auto_watch(self, enabled: bool = True) -> "WorkspaceWidgetBuilder":
        """Enable automatic file watching."""
        self._auto_watch = enabled
        return self

    def with_auto_recovery(self, enabled: bool = True) -> "WorkspaceWidgetBuilder":
        """Enable automatic error recovery."""
        self._auto_recovery = enabled
        return self

    def with_conflict_handler(self, handler: FileConflictHandler) -> "WorkspaceWidgetBuilder":
        """Set custom file conflict handler."""
        self._conflict_handler = handler
        return self

    def with_error_handler(self, handler: ErrorHandler) -> "WorkspaceWidgetBuilder":
        """Set custom error handler."""
        self._error_handler = handler
        return self

    def with_icon_provider(self, provider: IconProvider) -> "WorkspaceWidgetBuilder":
        """Set custom icon provider."""
        self._icon_provider = provider
        return self

    def with_lifecycle_hooks(self, hooks: WorkspaceLifecycleHooks) -> "WorkspaceWidgetBuilder":
        """Set lifecycle hooks."""
        self._lifecycle_hooks = hooks
        return self

    def with_parent(self, parent: QWidget) -> "WorkspaceWidgetBuilder":
        """Set parent widget."""
        self._parent = parent
        return self

    def build(self) -> WorkspaceWidget:
        """Build and return the WorkspaceWidget instance."""
        widget = WorkspaceWidget(
            file_extensions=self._file_extensions,
            excluded_folders=self._excluded_folders,
            config_filename=self._config_filename,
            conflict_handler=self._conflict_handler,
            error_handler=self._error_handler,
            icon_provider=self._icon_provider,
            lifecycle_hooks=self._lifecycle_hooks,
            parent=self._parent
        )

        if self._auto_watch:
            widget.enable_auto_watch()

        if self._auto_recovery:
            widget._enable_auto_recovery()

        return widget
```

## AutoWatchMode Enum

```python
from enum import Enum

class AutoWatchMode(Enum):
    """Automatic file watching modes."""

    MANUAL = "manual"
    """App must manually call watch_file() for each opened file."""

    AUTO_ON_SELECT = "auto_on_select"
    """Automatically watch file when file_selected signal emitted."""

    AUTO_ON_OPEN = "auto_on_open"
    """Automatically watch file when app emits file_opened signal."""


# Usage
workspace = WorkspaceWidget()
workspace.set_auto_watch_mode(AutoWatchMode.AUTO_ON_SELECT)

# Or use convenience method
workspace.enable_auto_watch()  # Same as AUTO_ON_SELECT
```

## Session Management (Hybrid Approach)

### Default Behavior

By default, the widget handles session persistence automatically:

```python
# Default session storage location
~/.config/<app_name>/workspaces/
├── recent.json                    # Recent workspaces list
└── sessions/
    ├── <hash1>.json               # Session for workspace 1
    ├── <hash2>.json               # Session for workspace 2
    └── <hash3>.json               # Session for workspace 3
```

Hash computation: `hashlib.md5(workspace_primary_folder_path.encode()).hexdigest()[:16]`

### Override for Custom Session Management

Apps can override session management:

```python
class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create workspace widget
        self.workspace = WorkspaceWidget()

        # Override session management
        self.workspace.workspace_opened.connect(self._on_workspace_opened)
        self.workspace.workspace_closed.connect(self._on_workspace_closed)

    def _on_workspace_opened(self, folders: list[WorkspaceFolder]):
        """Handle workspace opened - load app-specific session."""
        # Load session from custom location (e.g., database, cloud)
        session_data = self.my_session_manager.load(folders[0].path)

        # Restore workspace UI state
        workspace_session = WorkspaceSession.from_dict(session_data["workspace"])
        self.workspace.restore_session(workspace_session)

        # Restore app-specific state
        self.restore_my_app_state(session_data["app_state"])

    def _on_workspace_closed(self):
        """Handle workspace closed - save app-specific session."""
        # Save workspace UI state
        workspace_session = self.workspace.save_session()

        # Combine with app-specific state
        session_data = {
            "workspace": workspace_session.to_dict(),
            "app_state": self.get_my_app_state()
        }

        # Save to custom location
        self.my_session_manager.save(session_data)
```

## Theme Integration

### Automatic Theming

When `vfwidgets-theme` is installed, the widget automatically applies VS Code-compatible theming:

```python
# Theme tokens used (from theme_config)
{
    "background": "sideBar.background",        # Tree background
    "foreground": "sideBar.foreground",        # Text color
    "selection_bg": "list.activeSelectionBackground",  # Selected item (active)
    "selection_fg": "list.activeSelectionForeground",  # Selected text (active)
    "inactive_selection_bg": "list.inactiveSelectionBackground",  # Selected (inactive)
    "hover_bg": "list.hoverBackground",        # Hover state
    "border": "sideBar.border"                 # Border color
}
```

### Fallback Theme

When `vfwidgets-theme` is NOT installed, a hardcoded dark theme is used:

```python
# Fallback theme (similar to VS Code Dark+)
QTreeView {
    background-color: #252526;  /* Dark gray */
    color: #cccccc;             /* Light gray */
    border: none;
}
QTreeView::item:hover {
    background-color: #2a2d2e;  /* Slightly lighter on hover */
}
QTreeView::item:selected:active {
    background-color: #094771;  /* Blue selection */
    color: #ffffff;             /* White text */
}
QTreeView::item:selected:!active {
    background-color: #37373d;  /* Gray selection (inactive) */
}
```

## Context Menus (Extensible)

The widget provides a `context_menu_requested` signal that apps can use to add custom context menu items:

```python
def _on_context_menu(self, pos: QPoint, item: Union[FileInfo, WorkspaceFolder]):
    """Handle context menu request."""
    menu = QMenu(self)

    if isinstance(item, WorkspaceFolder):
        # Workspace folder context menu
        menu.addAction("Rename Folder", lambda: self._rename_folder(item))
        menu.addAction("Remove from Workspace", lambda: self._remove_folder(item))
        menu.addSeparator()
        menu.addAction("Reveal in File Manager", lambda: self._reveal(item.path))

    elif isinstance(item, FileInfo):
        # File/folder context menu
        if item.is_dir:
            menu.addAction("New File...", lambda: self._new_file(item))
        else:
            menu.addAction("Open", lambda: self._open_file(item))
            menu.addAction("Open in External Editor", lambda: self._open_external(item))
            menu.addSeparator()
            menu.addAction("Copy Path", lambda: self._copy_path(item))
            menu.addAction("Delete", lambda: self._delete_file(item))

    menu.exec(pos)

# Connect signal
workspace.context_menu_requested.connect(_on_context_menu)
```

## Advanced Filtering

### Filter Behavior Clarifications

```python
# Question: What does set_file_extensions([]) mean?
workspace.set_file_extensions([])  # Shows ALL files (empty list = no filter)
workspace.set_file_extensions(None)  # Shows ALL files (None = no filter)
workspace.set_file_extensions([".py"])  # Shows ONLY .py files

# Question: How do extension and callback filters interact?
workspace.set_file_extensions([".py", ".md"])
workspace.set_filter_callback(lambda f, w: f.size > 1024)
# Result: Shows .py OR .md files AND size > 1024 (filters are AND-ed)

# Question: Can I temporarily disable filtering?
workspace.set_filter_enabled(False)  # Shows all files, keeps filter config
workspace.set_filter_enabled(True)   # Re-applies filter config

# Question: What's the difference between excluded_extensions and excluded_folders?
workspace.set_excluded_folders(["node_modules", ".git"])  # Never traverse these folders
workspace.set_excluded_extensions([".pyc", ".log"])  # Hide these file types (inverse of set_file_extensions)

# Note: excluded_extensions and file_extensions are mutually exclusive
workspace.set_file_extensions([".py"])  # Include mode: show these
workspace.set_excluded_extensions([".pyc"])  # Exclude mode: hide these (clears include mode)
```

### Filter Precedence

```
Folder Filtering (happens first):
1. Is folder in excluded_folders? → SKIP
2. Is folder hidden and show_hidden_files=False? → SKIP
3. Otherwise → TRAVERSE

File Filtering (happens during traversal):
1. Is file extension in file_extensions (if set)? → YES/NO
2. Does file pass filter_callback (if set)? → YES/NO
3. Is file extension in excluded_extensions (if set)? → YES/NO
4. Result: ALL filters must pass (AND logic)
```

### Performance Considerations

```python
# ❌ Slow: callback runs for every file
def slow_filter(file_info, workspace_folder):
    # Opens file to check contents
    with open(file_info.absolute_path) as f:
        return "TODO" in f.read()  # SLOW!

# ✅ Fast: use extensions first, then callback for remaining files
workspace.set_file_extensions([".py"])  # Filter 90% of files fast
workspace.set_filter_callback(lambda f, w: f.size < 100000)  # Only checks .py files
```

## Common Patterns

### Pattern 1: Basic Markdown Viewer

```python
from PySide6.QtWidgets import QApplication, QMainWindow
from vfwidgets_workspace import WorkspaceWidget
from pathlib import Path

class MarkdownViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create workspace for Markdown files
        self.workspace = WorkspaceWidget.for_markdown(self)

        # Connect signals
        self.workspace.file_selected.connect(self.open_markdown_file)

        # Add to UI
        self.setCentralWidget(self.workspace)

    def open_markdown_file(self, file_path: str):
        # Open and render markdown file
        with open(file_path) as f:
            content = f.read()
        # ... render markdown ...

# Usage
app = QApplication([])
viewer = MarkdownViewer()
viewer.workspace.open_workspace(Path("/home/user/docs"))
viewer.show()
app.exec()
```

### Pattern 2: IDE-style with Sidebar and Tabs

```python
from vilocode_window import ViloCodeWindow
from chrome_tabbed_window import ChromeTabbedWindow
from vfwidgets_workspace import WorkspaceWidget

class IDEWindow(ViloCodeWindow):
    def __init__(self):
        super().__init__()

        # Create workspace
        self.workspace = WorkspaceWidget.for_python(self)

        # Create tabs
        self.tabs = ChromeTabbedWindow()

        # Sync workspace with tabs
        self.workspace.sync_with_tab_widget(self.tabs)

        # Connect signals
        self.workspace.file_selected.connect(self.open_file_in_tab)

        # Add to UI
        self.add_sidebar_panel("explorer", self.workspace, "FILES")
        self.set_central_widget(self.tabs)

    def open_file_in_tab(self, file_path: str):
        # Check if already open
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if hasattr(widget, 'file_path') and widget.file_path == file_path:
                self.tabs.setCurrentIndex(i)
                return

        # Open new tab
        editor = CodeEditor(file_path)
        self.tabs.addTab(editor, Path(file_path).name)
        self.tabs.setCurrentWidget(editor)
```

### Pattern 3: Multi-folder Project with Custom Config

```python
@dataclass
class ProjectConfig(WorkspaceConfig):
    """Extended config for project management."""
    project_type: str = "python"  # python, web, rust, etc.
    build_command: str = "make"
    test_command: str = "pytest"
    linter_enabled: bool = True

class ProjectManager:
    def __init__(self):
        self.workspace = WorkspaceWidget(
            config_class=ProjectConfig,
            config_filename=".project.json"
        )

        # Access extended config
        self.workspace.workspace_opened.connect(self._on_workspace_opened)

    def _on_workspace_opened(self, folders: list[WorkspaceFolder]):
        config = self.workspace.get_config()

        if config.linter_enabled:
            self.start_linter()

        # Setup build system
        self.build_cmd = config.build_command
        self.test_cmd = config.test_command
```

### Pattern 4: Custom File Conflict Handling

```python
class AutoReloadConflictHandler:
    """Automatically reload modified files."""

    def __init__(self, tab_widget):
        self.tabs = tab_widget

    def handle_file_modified(self, file_path, workspace_folder=None):
        # Find tab with this file
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if hasattr(widget, 'file_path') and widget.file_path == file_path:
                # Reload file in tab
                widget.reload_from_disk()
                return FileConflictAction.RELOAD

        # Not open, ignore
        return FileConflictAction.IGNORE

    def handle_file_deleted(self, file_path, workspace_folder=None):
        # Close tab if open
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if hasattr(widget, 'file_path') and widget.file_path == file_path:
                self.tabs.removeTab(i)
                return FileConflictAction.CLOSE

        return FileConflictAction.IGNORE

# Usage
workspace = WorkspaceWidget(
    conflict_handler=AutoReloadConflictHandler(tabs)
)
```

### Pattern 5: Workspace with Lifecycle Validation

```python
class WorkspaceValidator:
    """Validate workspace before opening."""

    def before_workspace_open(self, folder_path: Path) -> bool:
        # Check for required files
        required_files = ["README.md", "LICENSE"]
        missing = [f for f in required_files if not (folder_path / f).exists()]

        if missing:
            result = QMessageBox.question(
                None,
                "Missing Files",
                f"Workspace is missing: {', '.join(missing)}\nOpen anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            return result == QMessageBox.StandardButton.Yes

        return True

workspace = WorkspaceWidget(lifecycle_hooks=WorkspaceValidator())
```

## Troubleshooting

### Issue: Files not showing in tree

**Symptoms:** Workspace opens but tree is empty or missing files.

**Causes:**
1. File extensions filter too restrictive
2. Folders excluded
3. Files hidden by custom callback

**Solutions:**
```python
# Check current filter settings
print(workspace._model._file_extensions)  # Debug: see current filter
print(workspace._model._excluded_folders)

# Temporarily disable filtering to test
workspace.set_filter_enabled(False)

# Reset to show all files
workspace.set_file_extensions(None)  # or []
workspace.set_excluded_folders([])
workspace.refresh()
```

### Issue: Workspace session not persisting

**Symptoms:** Expanded folders/scroll position not restored on reopen.

**Causes:**
1. Session dir not writable
2. Custom session management interfering
3. Workspace config hash changed

**Solutions:**
```python
# Check session directory
import os
session_dir = Path.home() / ".config" / "myapp" / "workspaces" / "sessions"
print(f"Session dir exists: {session_dir.exists()}")
print(f"Session dir writable: {os.access(session_dir, os.W_OK)}")

# Manually save/load session for debugging
session = workspace.save_session()
print(f"Session data: {session.to_dict()}")

# Restore session
workspace.restore_session(session)
```

### Issue: Theme colors not applying

**Symptoms:** Workspace uses fallback dark theme instead of app theme.

**Causes:**
1. vfwidgets-theme not installed
2. ThemedApplication not used
3. Theme changed after workspace created

**Solutions:**
```python
# Check if theme system available
try:
    from vfwidgets_theme import ThemedWidget
    print("Theme system available")
except ImportError:
    print("Theme system NOT available - using fallback")

# Manually trigger theme update
if hasattr(workspace, 'theme_changed'):
    workspace.theme_changed()
```

### Issue: File conflicts not detected

**Symptoms:** External file changes not triggering conflict handler.

**Causes:**
1. File not watched (forgot to call watch_file)
2. Auto-watch mode not enabled
3. QFileSystemWatcher limitation (too many files)

**Solutions:**
```python
# Enable auto-watch
workspace.enable_auto_watch()

# Manually watch file
workspace.watch_file("/path/to/file")

# Check what's being watched
print(f"Watched files: {workspace._file_watcher.files()}")

# Check platform limitations
import sys
if sys.platform == "linux":
    # Linux has inotify limits
    print("Check: /proc/sys/fs/inotify/max_user_watches")
```

### Issue: Performance slow with large workspaces

**Symptoms:** Sluggish UI, slow expand/collapse, high CPU usage.

**Causes:**
1. Too many files (>100,000)
2. Deep folder nesting
3. Expensive filter callback

**Solutions:**
```python
# Add excluded folders to reduce file count
workspace.set_excluded_folders([
    "node_modules", ".git", "__pycache__",
    "venv", ".venv", "dist", "build"
])

# Use extension filter instead of callback
workspace.set_file_extensions([".py", ".md"])  # Fast
# Instead of:
# workspace.set_filter_callback(lambda f, w: f.extension in [".py", ".md"])  # Slow

# Check file count
all_files = workspace.get_all_files()
print(f"Total files: {len(all_files)}")
if len(all_files) > 50000:
    print("WARNING: Large workspace may be slow")
```

## Performance Guidelines

### File Count Limits

| Files | Performance | Recommendation |
|-------|-------------|----------------|
| < 1,000 | Excellent | No optimization needed |
| 1,000 - 10,000 | Good | Use basic filtering |
| 10,000 - 50,000 | Acceptable | Use aggressive filtering, exclude build folders |
| 50,000 - 100,000 | Slow | Consider splitting workspace or lazy loading |
| > 100,000 | Very Slow | Not recommended, split into multiple workspaces |

### Optimization Strategies

**1. Aggressive Folder Exclusion**
```python
workspace.set_excluded_folders([
    # Version control
    ".git", ".svn", ".hg",

    # Build artifacts
    "node_modules", "dist", "build", "target",
    "__pycache__", ".pytest_cache", ".mypy_cache",

    # Virtual environments
    "venv", ".venv", "env", ".env",

    # IDE
    ".idea", ".vscode", ".vs",

    # OS
    ".DS_Store", "Thumbs.db",
])
```

**2. Extension Filtering**
```python
# ✅ Fast: only scan relevant files
workspace.set_file_extensions([".py", ".pyi"])

# ❌ Slow: scans all files, then filters
workspace.set_filter_callback(lambda f, w: f.extension == ".py")
```

**3. Lazy Expansion**
```python
# Don't auto-expand all folders on open
# Let user expand as needed
# (This is the default behavior)
```

**4. Debounced Refresh**
```python
# For apps with frequent file changes, debounce refreshes
from PySide6.QtCore import QTimer

class DebouncedWorkspace(WorkspaceWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._refresh_timer = QTimer()
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.timeout.connect(super().refresh)

    def refresh(self):
        # Debounce: only refresh after 500ms of no calls
        self._refresh_timer.start(500)
```

### Memory Usage

**Typical memory usage:**
- 1,000 files: ~5 MB
- 10,000 files: ~50 MB
- 100,000 files: ~500 MB

**Optimization:**
```python
# Clear file info cache periodically
workspace._model._filesystem_cache.clear()
workspace.refresh()
```

## Testing Guide

### Unit Testing with pytest-qt

```python
import pytest
from pathlib import Path
from vfwidgets_workspace import WorkspaceWidget, WorkspaceFolder

def test_workspace_opens_folder(qtbot, tmp_path):
    """Test opening a workspace folder."""
    # Create test folder
    test_folder = tmp_path / "test_workspace"
    test_folder.mkdir()
    (test_folder / "file1.py").write_text("# test")

    # Create workspace
    workspace = WorkspaceWidget()
    qtbot.addWidget(workspace)

    # Open workspace
    result = workspace.open_workspace(test_folder)
    assert result is True

    # Verify folder loaded
    folders = workspace.get_folders()
    assert len(folders) == 1
    assert folders[0].path == str(test_folder)

def test_file_filtering(qtbot, tmp_path):
    """Test file extension filtering."""
    # Create test files
    test_folder = tmp_path / "test_workspace"
    test_folder.mkdir()
    (test_folder / "script.py").write_text("")
    (test_folder / "readme.md").write_text("")
    (test_folder / "data.json").write_text("")

    # Create workspace with filter
    workspace = WorkspaceWidget(file_extensions=[".py"])
    qtbot.addWidget(workspace)
    workspace.open_workspace(test_folder)

    # Get all files
    all_files = workspace.get_all_files()

    # Should only see .py file
    assert len(all_files) == 1
    assert all_files[0].endswith("script.py")

def test_file_selection_signal(qtbot, tmp_path):
    """Test file selection emits signal."""
    # Create test workspace
    test_folder = tmp_path / "test_workspace"
    test_folder.mkdir()
    test_file = test_folder / "test.py"
    test_file.write_text("")

    workspace = WorkspaceWidget()
    qtbot.addWidget(workspace)
    workspace.open_workspace(test_folder)

    # Spy on signal
    with qtbot.waitSignal(workspace.file_selected, timeout=1000) as blocker:
        # Simulate file selection
        workspace._tree_view.selectAll()

    # Verify signal emitted
    assert blocker.signal_triggered
```

### Integration Testing

```python
def test_full_workspace_workflow(qtbot, tmp_path):
    """Test complete workspace workflow."""
    # Setup
    workspace = WorkspaceWidget.for_python()
    qtbot.addWidget(workspace)

    folder1 = tmp_path / "project1"
    folder1.mkdir()
    (folder1 / "main.py").write_text("print('hello')")

    # 1. Open workspace
    workspace.open_workspace(folder1)
    assert workspace.is_workspace_open()

    # 2. Add another folder
    folder2 = tmp_path / "project2"
    folder2.mkdir()
    workspace.add_folder(folder2, "Project 2")
    assert len(workspace.get_folders()) == 2

    # 3. Save session
    session = workspace.save_session()
    assert session.workspace_name is not None

    # 4. Close and reopen
    workspace.close_workspace()
    assert not workspace.is_workspace_open()

    workspace.open_workspace(folder1)
    workspace.restore_session(session)
    assert len(workspace.get_folders()) == 2
```

### Mocking for Tests

```python
from unittest.mock import Mock, patch

def test_custom_conflict_handler(qtbot):
    """Test custom file conflict handler."""
    # Create mock handler
    mock_handler = Mock()
    mock_handler.handle_file_modified.return_value = FileConflictAction.RELOAD

    # Create workspace with mock
    workspace = WorkspaceWidget(conflict_handler=mock_handler)
    qtbot.addWidget(workspace)

    # Simulate file change
    workspace._on_file_changed("/path/to/file.py")

    # Verify handler called
    mock_handler.handle_file_modified.assert_called_once_with(
        "/path/to/file.py",
        workspace_folder=None
    )
```

### Testing Custom Extensions

```python
def test_custom_config_class():
    """Test workspace with custom config class."""
    @dataclass
    class MyConfig(WorkspaceConfig):
        custom_field: str = "default"

    workspace = WorkspaceWidget(config_class=MyConfig)

    # Create config
    config = MyConfig(
        name="test",
        custom_field="custom_value"
    )

    # Save and load
    config_dict = config.to_dict()
    assert "custom_field" in config.custom_data

    loaded = MyConfig.from_dict(config_dict)
    assert loaded.custom_field == "custom_value"
```

## Package Structure

```
widgets/workspace_widget/
├── pyproject.toml                 # Package metadata
├── README.md                      # User documentation
├── SPECIFICATION.md               # This file
├── CHANGELOG.md                   # Version history
├── src/
│   └── vfwidgets_workspace/
│       ├── __init__.py            # Public API exports
│       ├── workspace_widget.py    # WorkspaceWidget (main facade)
│       ├── models/
│       │   ├── __init__.py
│       │   ├── workspace_folder.py   # WorkspaceFolder dataclass
│       │   ├── file_info.py          # FileInfo dataclass
│       │   ├── workspace_config.py   # WorkspaceConfig
│       │   └── workspace_session.py  # WorkspaceSession, WorkspaceRootState
│       ├── components/
│       │   ├── __init__.py
│       │   ├── multi_root_model.py   # MultiRootFileSystemModel
│       │   └── file_explorer.py      # FileExplorerWidget
│       ├── controllers/
│       │   ├── __init__.py
│       │   └── workspace_manager.py  # WorkspaceManager
│       └── protocols/
│           ├── __init__.py
│           └── filter_protocol.py    # FilterCallback protocol
├── tests/
│   ├── __init__.py
│   ├── test_models.py             # Test data models
│   ├── test_multi_root_model.py   # Test QAbstractItemModel
│   ├── test_file_explorer.py      # Test view
│   ├── test_workspace_manager.py  # Test controller
│   └── test_workspace_widget.py   # Integration tests
└── examples/
    ├── 01_basic_single_folder.py  # Simple single-folder workspace
    ├── 02_multi_folder.py         # Multi-folder workspace
    ├── 03_custom_filter.py        # Custom file filtering
    ├── 04_extended_config.py      # Subclassed configuration
    ├── 05_custom_session.py       # Custom session management
    └── 06_context_menu.py         # Custom context menus
```

## Dependencies

```toml
[project]
name = "vfwidgets-workspace"
version = "0.1.0"
description = "Generic workspace widget for file-based applications"
dependencies = [
    "PySide6>=6.5.0",
]

[project.optional-dependencies]
theme = [
    "vfwidgets-theme>=2.0.0",  # For automatic theming
]
dev = [
    "pytest>=7.0",
    "pytest-qt>=4.0",
    "black>=23.0",
    "ruff>=0.1.0",
    "mypy>=1.0",
]
```

## Future Enhancements

### Phase 1 (MVP) - Included in v0.1.0
- ✅ Multi-folder workspace management
- ✅ File tree explorer with filtering
- ✅ Session persistence
- ✅ Theme integration
- ✅ Basic context menus

### Phase 2 - Future Versions
- ⏳ File operations (create, delete, rename, move)
- ⏳ Drag-and-drop support
- ⏳ Search within workspace (filter tree in real-time)
- ⏳ File watcher optimizations (debouncing, batching)
- ⏳ Keyboard shortcuts (customize via keybinding_manager)
- ⏳ Breadcrumb navigation (show current folder path)

### Phase 3 - Advanced Features
- ⏳ Git integration (show status icons, modified files)
- ⏳ File preview on hover
- ⏳ Virtual folders (custom grouping, not filesystem-based)
- ⏳ Workspace templates (predefined configurations)
- ⏳ Multi-workspace support (switch between multiple workspaces)

## Use Cases

### 1. Markdown Viewer (Reamde)
```python
from vfwidgets_workspace import WorkspaceWidget

workspace = WorkspaceWidget(
    file_extensions=[".md", ".markdown", ".mdown"],
    config_filename=".reamde-workspace.json"
)
workspace.file_selected.connect(open_markdown_file)
```

### 2. Terminal Emulator (ViloxTerm)
```python
workspace = WorkspaceWidget(
    file_extensions=[".sh", ".bash", ".zsh", ".py"],
    excluded_folders=[".git", "__pycache__"],
    config_filename=".viloxterm-workspace.json"
)
workspace.file_selected.connect(run_in_terminal)
```

### 3. Theme Editor (Theme Studio)
```python
workspace = WorkspaceWidget(
    file_extensions=[".json", ".xml", ".css"],
    config_filename=".themestudio-workspace.json"
)
workspace.file_selected.connect(open_theme_file)
```

### 4. Web Browser (ViloWeb)
```python
workspace = WorkspaceWidget(
    file_extensions=[".html", ".css", ".js", ".vue", ".jsx"],
    excluded_folders=["node_modules", "dist"],
    config_filename=".viloweb-workspace.json"
)
workspace.file_selected.connect(preview_in_browser)
```

### 5. Code Editor (Future)
```python
workspace = WorkspaceWidget(
    file_extensions=[".py", ".js", ".ts", ".java", ".cpp", ".rs"],
    excluded_folders=["__pycache__", "node_modules", "target"],
    config_filename=".code-workspace.json"
)
workspace.file_selected.connect(open_in_editor)
```

## Summary

**VFWidgets Workspace Widget** is a generic, reusable component that provides:

1. **Multi-folder workspace management** (VS Code-style)
2. **File tree explorer** with custom model and theme integration
3. **Extensible configuration** (subclassing + custom data)
4. **Flexible file filtering** (extensions + callbacks)
5. **Hybrid session management** (built-in default + override capability)
6. **Clean MVC architecture** (testable, maintainable)

**95% of workspace functionality** is generic and reusable across all VFWidgets apps!

---

**Next Steps:**
1. Implement MultiRootFileSystemModel (most complex component)
2. Implement FileExplorerWidget (ThemedWidget integration)
3. Implement WorkspaceManager (lifecycle + config)
4. Implement WorkspaceWidget (facade)
5. Write tests and examples
6. Document extension points
