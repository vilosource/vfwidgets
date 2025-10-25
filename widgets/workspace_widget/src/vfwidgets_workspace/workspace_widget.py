"""Main workspace widget - public API facade."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from PySide6.QtCore import QModelIndex, Qt, QTimer, Signal
from PySide6.QtWidgets import QAbstractItemView, QTabWidget, QVBoxLayout, QWidget

from .file_explorer_widget import FileExplorerWidget
from .file_system_model import MultiRootFileSystemModel
from .models import FileInfo, WorkspaceConfig, WorkspaceFolder, WorkspaceSession
from .protocols import (
    ContextMenuProvider,
    ErrorHandler,
    FileConflictHandler,
    IconProvider,
    WorkspaceLifecycleHooks,
    WorkspaceValidator,
)
from .workspace_manager import WorkspaceManager

logger = logging.getLogger(__name__)


class WorkspaceWidget(QWidget):
    """Multi-folder workspace widget with VS Code-like file explorer.

    This is the main public API for the workspace widget.
    """

    # Signals
    workspace_opened = Signal(list)  # list[WorkspaceFolder]
    workspace_closed = Signal()
    folder_added = Signal(object)  # WorkspaceFolder
    folder_removed = Signal(str)  # folder_path
    file_selected = Signal(str)  # file_path
    file_double_clicked = Signal(str)  # file_path
    active_file_changed = Signal(str)  # file_path
    config_changed = Signal()

    def __init__(
        self,
        file_extensions: Optional[list[str]] = None,
        excluded_folders: Optional[list[str]] = None,
        filter_callback: Optional[Callable[[FileInfo, WorkspaceFolder], bool]] = None,
        config_class: type = WorkspaceConfig,
        config_filename: str = ".workspace.json",
        session_dir: Optional[Path] = None,
        workspace_file_extension: str = ".workspace",
        workspace_file_type_name: str = "Workspace Files",
        conflict_handler: Optional[FileConflictHandler] = None,
        error_handler: Optional[ErrorHandler] = None,
        icon_provider: Optional[IconProvider] = None,
        workspace_validator: Optional[WorkspaceValidator] = None,
        context_menu_provider: Optional[ContextMenuProvider] = None,
        lifecycle_hooks: Optional[WorkspaceLifecycleHooks] = None,
        parent: Optional[QWidget] = None,
    ):
        """Initialize workspace widget.

        Args:
            file_extensions: File extensions to include (None = all)
            excluded_folders: Folder names to exclude
            filter_callback: Custom filter function
            config_class: Config class (WorkspaceConfig or subclass)
            config_filename: Name of workspace config file
            session_dir: Directory for session files
            workspace_file_extension: File extension for portable workspace files (e.g., ".workspace", ".reamde", ".viloxterm")
            workspace_file_type_name: Human-readable name for file dialogs (e.g., "Workspace Files", "Reamde Workspace Files")
            conflict_handler: File conflict handler
            error_handler: Error handler
            icon_provider: Icon provider
            workspace_validator: Workspace validator
            context_menu_provider: Context menu provider
            lifecycle_hooks: Lifecycle hooks
            parent: Parent widget
        """
        super().__init__(parent)

        # Store parameters
        self._conflict_handler = conflict_handler
        self._error_handler = error_handler
        self._icon_provider = icon_provider
        self._validator = workspace_validator
        self._context_menu_provider = context_menu_provider
        self._lifecycle_hooks = lifecycle_hooks

        # State
        self._current_workspace_path: Optional[Path] = None
        self._active_file_path: Optional[str] = None

        # Create components
        self._model = MultiRootFileSystemModel(
            parent=self,
            file_extensions=file_extensions,
            excluded_folders=excluded_folders,
            filter_callback=filter_callback,
            icon_provider=icon_provider,
        )

        self._manager = WorkspaceManager(
            config_class=config_class,
            config_filename=config_filename,
            session_dir=session_dir,
            workspace_file_extension=workspace_file_extension,
            workspace_file_type_name=workspace_file_type_name,
            error_handler=error_handler,
            validator=workspace_validator,
            parent=self,
        )

        self._explorer = FileExplorerWidget(self)
        self._explorer.set_model(self._model)

        # Setup UI
        self._setup_ui()

        # Connect signals
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Setup widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._explorer)

    def _connect_signals(self) -> None:
        """Connect internal signals."""
        # Manager signals
        self._manager.workspace_opened.connect(self._on_workspace_opened)
        self._manager.workspace_closed.connect(self._on_workspace_closed)
        self._manager.folder_added.connect(self.folder_added)
        self._manager.folder_removed.connect(self.folder_removed)
        self._manager.config_changed.connect(self.config_changed)

        # Explorer signals
        self._explorer.file_clicked.connect(self._on_file_clicked)
        self._explorer.file_double_clicked.connect(self._on_file_double_clicked)
        self._explorer.folder_expanded.connect(self._on_folder_expanded)
        self._explorer.folder_collapsed.connect(self._on_folder_collapsed)

    # =========================================================================
    # Public API - Workspace Operations
    # =========================================================================

    def open_workspace(self, folder_path: Path) -> bool:
        """Open workspace.

        Args:
            folder_path: Path to workspace root folder

        Returns:
            True if opened successfully
        """
        try:
            # Call lifecycle hook (can cancel)
            if self._lifecycle_hooks:
                if not self._lifecycle_hooks.before_workspace_open(str(folder_path)):
                    return False

            # Validate
            if self._validator:
                result = self._validator.validate_workspace_folder(str(folder_path))
                if not result.valid:
                    logger.error(f"Workspace validation failed: {result.message}")
                    return False

            # Open via manager
            folders = self._manager.open_workspace(folder_path)

            # Set folders in model
            self._model.set_folders(folders)

            # Store path
            self._current_workspace_path = folder_path

            # Load and restore session
            session = self._manager.load_session(folder_path)
            if session:
                self.restore_session(session)

            # Call lifecycle hook
            if self._lifecycle_hooks:
                self._lifecycle_hooks.after_workspace_opened(folders)

            return True

        except Exception as e:
            logger.error(f"Failed to open workspace: {e}")
            if self._error_handler:
                from .protocols import ErrorSeverity

                self._error_handler.handle_error(
                    ErrorSeverity.ERROR, f"Failed to open workspace: {e}", exception=e
                )
            return False

    def close_workspace(self) -> None:
        """Close current workspace."""
        if not self._current_workspace_path:
            return

        # Call lifecycle hook (can cancel)
        if self._lifecycle_hooks:
            if not self._lifecycle_hooks.before_workspace_close():
                return

        # Save session
        session = self.save_session()
        self._manager.save_session(session)

        # Close via manager
        self._manager.close_workspace()

        # Clear model
        self._model.set_folders([])

        # Clear state
        self._current_workspace_path = None
        self._active_file_path = None

        # Call lifecycle hook
        if self._lifecycle_hooks:
            self._lifecycle_hooks.after_workspace_closed()

    def add_folder(self, folder_path: Path) -> Optional[WorkspaceFolder]:
        """Add folder to workspace.

        Args:
            folder_path: Path to folder

        Returns:
            Created WorkspaceFolder or None if failed
        """
        try:
            # Call lifecycle hook
            if self._lifecycle_hooks:
                if not self._lifecycle_hooks.before_folder_add(str(folder_path)):
                    return None

            # Add via manager
            folder = self._manager.add_folder(folder_path)

            # Update model
            folders = self._manager.get_folders()
            self._model.set_folders(folders)

            # Call lifecycle hook
            if self._lifecycle_hooks:
                self._lifecycle_hooks.after_folder_added(folder)

            return folder

        except Exception as e:
            logger.error(f"Failed to add folder: {e}")
            return None

    def remove_folder(self, folder_path: str) -> None:
        """Remove folder from workspace.

        Args:
            folder_path: Absolute path to folder
        """
        # Call lifecycle hook
        if self._lifecycle_hooks:
            if not self._lifecycle_hooks.before_folder_remove(folder_path):
                return

        # Remove via manager
        self._manager.remove_folder(folder_path)

        # Update model
        folders = self._manager.get_folders()
        self._model.set_folders(folders)

        # Call lifecycle hook
        if self._lifecycle_hooks:
            self._lifecycle_hooks.after_folder_removed(folder_path)

    # =========================================================================
    # Public API - Session Management
    # =========================================================================

    def save_session(self) -> WorkspaceSession:
        """Collect current UI state into a session object.

        Returns:
            WorkspaceSession with current state
        """
        # Collect expanded folders
        expanded_folders = []
        model = self._explorer.model()

        if model:

            def collect_expanded(parent_index: QModelIndex) -> None:
                """Recursively collect expanded folder paths."""
                for row in range(model.rowCount(parent_index)):
                    index = model.index(row, 0, parent_index)

                    # Check if expanded
                    if self._explorer._tree_view.isExpanded(index):
                        path = self._explorer._get_path_from_index(index)
                        if path:
                            expanded_folders.append(path)

                        # Recurse into children
                        collect_expanded(index)

            # Start from root
            collect_expanded(QModelIndex())

        # Get scroll position
        scrollbar = self._explorer._tree_view.verticalScrollBar()
        scroll_position = scrollbar.value() if scrollbar else 0

        # Create session
        return WorkspaceSession(
            workspace_name=(
                self._current_workspace_path.name if self._current_workspace_path else ""
            ),
            last_opened=datetime.now().isoformat(),
            expanded_folders=expanded_folders,
            scroll_position=scroll_position,
            active_file=self._active_file_path,
        )

    def restore_session(self, session: WorkspaceSession) -> None:
        """Restore UI state from session.

        Args:
            session: Session to restore
        """
        # Expand folders (delayed to allow model to load)
        QTimer.singleShot(100, lambda: self._restore_expanded_folders(session.expanded_folders))

        # Restore scroll position
        QTimer.singleShot(200, lambda: self._restore_scroll(session.scroll_position))

        # Restore active file
        if session.active_file:
            QTimer.singleShot(300, lambda: self.highlight_file(session.active_file))

    def _restore_expanded_folders(self, expanded_folders: list[str]) -> None:
        """Restore expanded folder state.

        Args:
            expanded_folders: List of paths to expand
        """
        for folder_path in expanded_folders:
            index = self._find_index_by_path(folder_path)
            if index and index.isValid():
                self._explorer._tree_view.expand(index)

    def _restore_scroll(self, position: int) -> None:
        """Restore scroll position.

        Args:
            position: Vertical scroll position (pixels)
        """
        scrollbar = self._explorer._tree_view.verticalScrollBar()
        if scrollbar:
            scrollbar.setValue(position)

    # =========================================================================
    # Public API - File Navigation
    # =========================================================================

    def reveal_file(self, file_path: str) -> bool:
        """Reveal file in tree (expand parents, scroll to view, select).

        Args:
            file_path: Absolute path to file

        Returns:
            True if file found and revealed
        """
        index = self._find_index_by_path(file_path)

        if not index or not index.isValid():
            return False

        # Expand all parent folders
        parent = index.parent()
        while parent.isValid():
            self._explorer._tree_view.expand(parent)
            parent = parent.parent()

        # Scroll to make visible
        self._explorer._tree_view.scrollTo(index, QAbstractItemView.ScrollHint.PositionAtCenter)

        # Select item
        self._explorer._tree_view.setCurrentIndex(index)

        # Update active file
        self._active_file_path = file_path
        self.active_file_changed.emit(file_path)

        return True

    def highlight_file(self, file_path: str) -> bool:
        """Highlight file in tree (select without expanding parents).

        Args:
            file_path: Absolute path to file

        Returns:
            True if file found and highlighted
        """
        index = self._find_index_by_path(file_path)

        if not index or not index.isValid():
            return False

        # Select without expanding
        self._explorer._tree_view.setCurrentIndex(index)
        self._active_file_path = file_path

        return True

    def find_file(self, filename: str, fuzzy: bool = False) -> list[str]:
        """Find files by name.

        Args:
            filename: File name to search for
            fuzzy: If True, use fuzzy matching

        Returns:
            List of absolute file paths
        """
        results = []
        all_files = self.get_all_files()

        if fuzzy:
            # Fuzzy matching
            filename_lower = filename.lower()

            for file_path in all_files:
                file_name = Path(file_path).name.lower()

                # Check if all search characters appear in order
                search_idx = 0
                for char in file_name:
                    if search_idx < len(filename_lower) and char == filename_lower[search_idx]:
                        search_idx += 1

                if search_idx == len(filename_lower):
                    results.append(file_path)
        else:
            # Exact match
            filename_lower = filename.lower()

            for file_path in all_files:
                if Path(file_path).name.lower() == filename_lower:
                    results.append(file_path)

        return results

    def get_all_files(self) -> list[str]:
        """Get list of all files in workspace.

        Returns:
            List of absolute file paths
        """
        files = []
        model = self._explorer.model()

        if not model:
            return files

        def collect_files(parent_index: QModelIndex) -> None:
            """Recursively collect file paths."""
            for row in range(model.rowCount(parent_index)):
                index = model.index(row, 0, parent_index)
                file_info = index.data(Qt.ItemDataRole.UserRole)

                if file_info:
                    if file_info.is_dir:
                        # Recurse into directory
                        if model.canFetchMore(index):
                            model.fetchMore(index)
                        collect_files(index)
                    else:
                        # Add file
                        files.append(file_info.path)

        # Start from root
        collect_files(QModelIndex())

        return files

    def _find_index_by_path(self, file_path: str) -> Optional[QModelIndex]:
        """Find model index for absolute file path.

        Args:
            file_path: Absolute path

        Returns:
            QModelIndex or None if not found
        """
        # This is a simplified version - full implementation would walk the tree
        # For now, return None (TODO: implement full search)
        return None

    # =========================================================================
    # Public API - Tab Integration
    # =========================================================================

    def sync_with_tab_widget(
        self, tab_widget: QTabWidget, file_path_attr: str = "file_path", auto_sync: bool = True
    ) -> None:
        """Enable automatic synchronization with a tab widget.

        Args:
            tab_widget: Tab widget to sync with
            file_path_attr: Attribute name containing file path
            auto_sync: If True, auto-highlight file when tab changes
        """
        self._synced_tab_widget = tab_widget
        self._tab_file_path_attr = file_path_attr

        if auto_sync:
            tab_widget.currentChanged.connect(self._on_synced_tab_changed)

    def _on_synced_tab_changed(self, tab_index: int) -> None:
        """Handle tab change in synced tab widget.

        Args:
            tab_index: Index of newly selected tab
        """
        if not hasattr(self, "_synced_tab_widget"):
            return

        widget = self._synced_tab_widget.widget(tab_index)
        if not widget:
            return

        # Get file path from widget
        if hasattr(widget, self._tab_file_path_attr):
            file_path = getattr(widget, self._tab_file_path_attr)
            if file_path:
                self.highlight_file(str(file_path))

    # =========================================================================
    # Public API - Utility Methods
    # =========================================================================

    def refresh(self) -> None:
        """Refresh workspace file tree."""
        if self._model:
            self._model.refresh()

    # =========================================================================
    # Internal Signal Handlers
    # =========================================================================

    def _on_workspace_opened(self, folders: list[WorkspaceFolder]) -> None:
        """Handle workspace opened.

        Args:
            folders: List of workspace folders
        """
        self.workspace_opened.emit(folders)

    def _on_workspace_closed(self) -> None:
        """Handle workspace closed."""
        self.workspace_closed.emit()

    def _on_file_clicked(self, file_path: str) -> None:
        """Handle file clicked.

        Args:
            file_path: Clicked file path
        """
        self._active_file_path = file_path
        self.file_selected.emit(file_path)

    def _on_file_double_clicked(self, file_path: str) -> None:
        """Handle file double-clicked.

        Args:
            file_path: Double-clicked file path
        """
        self.file_double_clicked.emit(file_path)

    def _on_folder_expanded(self, folder_path: str) -> None:
        """Handle folder expanded.

        Args:
            folder_path: Expanded folder path
        """
        pass

    def _on_folder_collapsed(self, folder_path: str) -> None:
        """Handle folder collapsed.

        Args:
            folder_path: Collapsed folder path
        """
        pass
