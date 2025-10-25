"""Workspace management for Reamde.

This module provides the ReamdeWorkspaceManager class which integrates the
vfwidgets-workspace widget with Reamde's window and file management.
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QPoint
from PySide6.QtWidgets import QMenu

try:
    from vfwidgets_workspace import WorkspaceWidget

    WORKSPACE_AVAILABLE = True
except ImportError:
    WORKSPACE_AVAILABLE = False
    WorkspaceWidget = None


if TYPE_CHECKING:
    from .window import ReamdeWindow

logger = logging.getLogger(__name__)


class ReamdeWorkspaceManager(QObject):
    """Manages workspace widget and file operations for Reamde.

    This class bridges the WorkspaceWidget with Reamde's window,
    handling file selection, context menus, and session persistence.
    """

    def __init__(self, window: "ReamdeWindow"):
        """Initialize workspace manager.

        Args:
            window: Parent ReamdeWindow instance
        """
        super().__init__(window)
        self.window = window

        if not WORKSPACE_AVAILABLE:
            logger.warning("vfwidgets-workspace not available, workspace features disabled")
            self.workspace_widget = None
            return

        # Create workspace widget with markdown file filtering
        # Use file_extensions to filter for markdown files only
        markdown_extensions = [".md", ".markdown", ".mdown", ".mkd"]
        self.workspace_widget = WorkspaceWidget(
            file_extensions=markdown_extensions,
            workspace_file_extension=".reamde",
            workspace_file_type_name="Reamde Workspace Files",
            parent=window,
        )

        logger.debug(f"Workspace configured for markdown files: {markdown_extensions}")

        # Setup signal connections
        self._setup_signals()

        logger.info("ReamdeWorkspaceManager initialized")

    def _setup_signals(self) -> None:
        """Connect workspace widget signals to handlers."""
        if not self.workspace_widget:
            return

        # File selection
        self.workspace_widget.file_double_clicked.connect(self._on_file_selected)

        # Workspace lifecycle
        self.workspace_widget.workspace_opened.connect(self._on_workspace_opened)
        self.workspace_widget.workspace_closed.connect(self._on_workspace_closed)

        # Note: Context menu is handled via ContextMenuProvider protocol, not signals
        # Could implement custom provider in future if needed

        logger.debug("Workspace signals connected")

    # Public API

    def open_folder(self, folder_path: Path) -> bool:
        """Open folder in workspace.

        Args:
            folder_path: Path to folder to open

        Returns:
            True if opened successfully
        """
        if not self.workspace_widget:
            logger.warning("Workspace not available")
            return False

        try:
            success = self.workspace_widget.open_workspace(folder_path)
            if success:
                logger.info(f"Opened workspace folder: {folder_path}")
            return success
        except Exception as e:
            logger.error(f"Failed to open workspace folder: {e}", exc_info=True)
            return False

    def add_folder(self, folder_path: Path) -> bool:
        """Add folder to workspace.

        If no workspace is open yet, this will open the folder as the first workspace.
        Otherwise, it adds to the existing workspace.

        Args:
            folder_path: Path to folder to add

        Returns:
            True if added successfully
        """
        if not self.workspace_widget:
            logger.warning("Workspace not available")
            return False

        try:
            # Check if workspace is already open
            if not self.is_workspace_open():
                # No workspace yet - open this as the first workspace
                logger.info("No workspace open, opening folder as new workspace")
                return self.open_folder(folder_path)

            # Workspace exists - add to it
            success = self.workspace_widget.add_folder(folder_path)
            if success:
                logger.info(f"Added folder to workspace: {folder_path}")
            return success
        except Exception as e:
            logger.error(f"Failed to add folder to workspace: {e}", exc_info=True)
            return False

    def close_workspace(self) -> None:
        """Close current workspace."""
        if not self.workspace_widget:
            return

        try:
            self.workspace_widget.close_workspace()
            logger.info("Workspace closed")
        except Exception as e:
            logger.error(f"Failed to close workspace: {e}", exc_info=True)

    def get_workspace_folders(self) -> list[str]:
        """Get list of workspace folder paths.

        Returns:
            List of unique absolute folder paths (duplicates removed)
        """
        if not self.workspace_widget:
            return []

        try:
            # Access internal manager to get folders
            # TODO: WorkspaceWidget should expose get_folders() publicly
            folders = self.workspace_widget._manager.get_folders()

            # Convert to paths and deduplicate while preserving order
            seen = set()
            unique_folders = []
            for f in folders:
                path_str = str(f.path)
                if path_str not in seen:
                    seen.add(path_str)
                    unique_folders.append(path_str)

            return unique_folders
        except Exception as e:
            logger.error(f"Failed to get workspace folders: {e}", exc_info=True)
            return []

    def get_expanded_folders(self) -> list[str]:
        """Get list of expanded folder paths.

        Returns:
            List of unique absolute paths of expanded folders (duplicates removed)
        """
        if not self.workspace_widget:
            return []

        try:
            # Save session to get expanded folders
            # TODO: WorkspaceWidget should expose get_expanded_folders() publicly
            session = self.workspace_widget.save_session()
            expanded = session.expanded_folders if session.expanded_folders else []

            # Deduplicate while preserving order
            seen = set()
            unique_expanded = []
            for folder in expanded:
                if folder not in seen:
                    seen.add(folder)
                    unique_expanded.append(folder)

            return unique_expanded
        except Exception as e:
            logger.error(f"Failed to get expanded folders: {e}", exc_info=True)
            return []

    def restore_expanded_state(self, folder_paths: list[str]) -> None:
        """Restore expanded state from session.

        Args:
            folder_paths: List of folder paths to expand
        """
        if not self.workspace_widget:
            return

        try:
            # WorkspaceWidget uses restore_session() for state restoration
            # TODO: WorkspaceWidget should expose set_expanded_folders() publicly
            self.workspace_widget._restore_expanded_folders(folder_paths)
            logger.debug(f"Restored {len(folder_paths)} expanded folders")
        except Exception as e:
            logger.error(f"Failed to restore expanded state: {e}", exc_info=True)

    def reveal_active_file(self) -> None:
        """Highlight and scroll to active file in tree."""
        if not self.workspace_widget:
            return

        # Get active file from window
        current_index = self.window._tabs.currentIndex()
        if current_index < 0:
            return

        from .window import MarkdownViewerTab

        widget = self.window._tabs.widget(current_index)
        if isinstance(widget, MarkdownViewerTab) and widget.file_path:
            try:
                self.workspace_widget.reveal_file(str(widget.file_path))
            except Exception as e:
                logger.debug(f"Could not reveal file in workspace: {e}")

    def is_workspace_open(self) -> bool:
        """Check if workspace is currently open.

        Returns:
            True if workspace is open
        """
        if not self.workspace_widget:
            return False

        try:
            folders = self.get_workspace_folders()
            return len(folders) > 0
        except Exception:
            return False

    # Portable Workspace Files

    def save_workspace_file(self, file_path: Path, include_session: bool = True) -> bool:
        """Save workspace to portable .reamde file with Reamde session data.

        Args:
            file_path: Where to save workspace file
            include_session: Whether to include current session (open files, view modes)

        Returns:
            True if saved successfully
        """
        if not self.workspace_widget:
            logger.warning("No workspace widget available")
            return False

        try:
            # Get current workspace config
            config = self.workspace_widget._manager.get_config()
            if not config:
                logger.warning("No workspace config to save")
                return False

            # Convert to ReamdeWorkspaceConfig if needed
            from .models.workspace_config import ReamdeWorkspaceConfig

            if not isinstance(config, ReamdeWorkspaceConfig):
                reamde_config = ReamdeWorkspaceConfig.from_workspace_config(config)
            else:
                reamde_config = config

            # Include session data if requested
            if include_session:
                # Get open files from window
                open_files = []
                active_index = -1
                view_modes = {}

                if hasattr(self.window, "_open_files"):
                    open_files = list(self.window._open_files.keys())
                    current_index = self.window._tabs.currentIndex()

                    # Get view modes
                    from .window import MarkdownViewerTab

                    for file_path, tab_index in self.window._open_files.items():
                        widget = self.window._tabs.widget(tab_index)
                        if isinstance(widget, MarkdownViewerTab):
                            view_mode = widget.get_view_mode()
                            view_modes[file_path] = view_mode.value

                        if tab_index == current_index:
                            active_index = open_files.index(file_path)

                # Store in config
                reamde_config.set_session_data(open_files, active_index, view_modes)

            # Temporarily set config in manager
            original_config = self.workspace_widget._manager._config
            self.workspace_widget._manager._config = reamde_config

            # Save using WorkspaceWidget's method
            success = self.workspace_widget._manager.save_workspace_file(file_path)

            # Restore original config
            self.workspace_widget._manager._config = original_config

            if success:
                logger.info(f"Saved Reamde workspace to: {file_path}")

            return success

        except Exception as e:
            logger.error(f"Failed to save workspace file: {e}", exc_info=True)
            return False

    def load_workspace_file(self, file_path: Path, restore_session: bool = True) -> bool:
        """Load workspace from portable .reamde file with Reamde session data.

        Args:
            file_path: Path to workspace file
            restore_session: Whether to restore session (open files, view modes)

        Returns:
            True if loaded successfully
        """
        if not self.workspace_widget:
            logger.warning("No workspace widget available")
            return False

        try:
            # Load using WorkspaceWidget's method
            success = self.workspace_widget._manager.load_workspace_file(file_path)

            if not success:
                return False

            # Get config (should be loaded now)
            config = self.workspace_widget._manager.get_config()

            # Restore Reamde session if available
            if restore_session and config:
                from .models.workspace_config import ReamdeWorkspaceConfig

                # Convert to ReamdeWorkspaceConfig if needed
                if isinstance(config, ReamdeWorkspaceConfig):
                    reamde_config = config
                else:
                    reamde_config = ReamdeWorkspaceConfig.from_workspace_config(config)

                # Get session data
                open_files, active_index, view_modes = reamde_config.get_session_data()

                # Restore files
                if open_files:
                    for file_path_str in open_files:
                        self.window.open_file(file_path_str)

                    # Restore view modes
                    if view_modes:
                        from .window import MarkdownViewerTab

                        for file_path_str, view_mode_str in view_modes.items():
                            if file_path_str in self.window._open_files:
                                tab_index = self.window._open_files[file_path_str]
                                widget = self.window._tabs.widget(tab_index)
                                if isinstance(widget, MarkdownViewerTab):
                                    from .models.view_mode import ViewMode

                                    try:
                                        view_mode = ViewMode(view_mode_str)
                                        widget.set_view_mode(view_mode)
                                    except ValueError:
                                        pass  # Invalid view mode, skip

                    # Set active file
                    if 0 <= active_index < len(open_files):
                        active_file = open_files[active_index]
                        if active_file in self.window._open_files:
                            tab_index = self.window._open_files[active_file]
                            self.window._tabs.setCurrentIndex(tab_index)

            logger.info(f"Loaded Reamde workspace from: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to load workspace file: {e}", exc_info=True)
            return False

    # Signal Handlers

    def _on_file_selected(self, file_path: str) -> None:
        """Handle file selection from tree.

        Args:
            file_path: Absolute path to selected file
        """
        # Only open markdown files
        if Path(file_path).suffix.lower() not in [".md", ".markdown", ".mdown", ".mkd"]:
            logger.debug(f"Skipping non-markdown file: {file_path}")
            return

        # Open file in window
        self.window.open_file(file_path)
        logger.debug(f"Opened file from workspace: {file_path}")

    def _on_workspace_opened(self, folders: list) -> None:
        """Handle workspace opened event.

        Args:
            folders: List of workspace folder objects
        """
        logger.info(f"Workspace opened with {len(folders)} folders")

        # Show sidebar (if hidden)
        if not self.window.is_sidebar_visible():
            self.window.toggle_sidebar()

        # Update window title
        self._update_window_title()

        # Enable workspace menu actions
        self._enable_workspace_actions(True)

    def _on_workspace_closed(self) -> None:
        """Handle workspace closed event."""
        logger.info("Workspace closed")

        # Update window title
        self._update_window_title()

        # Disable workspace menu actions
        self._enable_workspace_actions(False)

    def _show_file_context_menu(self, file_path: str, pos: QPoint) -> None:
        """Show context menu for file.

        Args:
            file_path: Absolute path to file
            pos: Global position for menu
        """
        menu = QMenu(self.window)

        # Open action
        open_action = menu.addAction("Open")
        open_action.triggered.connect(lambda: self.window.open_file(file_path))

        menu.addSeparator()

        # Copy path action
        copy_action = menu.addAction("Copy Path")
        copy_action.triggered.connect(lambda: self._copy_path(file_path))

        # Reveal in system
        reveal_action = menu.addAction("Reveal in File Manager")
        reveal_action.triggered.connect(lambda: self._reveal_in_system(file_path))

        # Show menu
        menu.exec(pos)

    # Helper Methods

    def _update_window_title(self) -> None:
        """Update window title based on workspace state."""
        # This is handled by ReamdeWindow, just notify
        pass

    def _enable_workspace_actions(self, enabled: bool) -> None:
        """Enable/disable workspace menu actions.

        Args:
            enabled: True to enable, False to disable
        """
        # This will be connected by ReamdeWindow
        pass

    def _copy_path(self, file_path: str) -> None:
        """Copy file path to clipboard.

        Args:
            file_path: Path to copy
        """
        from PySide6.QtWidgets import QApplication

        clipboard = QApplication.clipboard()
        clipboard.setText(file_path)
        logger.debug(f"Copied path to clipboard: {file_path}")

    def _reveal_in_system(self, file_path: str) -> None:
        """Reveal file in system file manager.

        Args:
            file_path: Path to file
        """
        import platform
        import subprocess

        try:
            system = platform.system()
            if system == "Darwin":  # macOS
                subprocess.run(["open", "-R", file_path])
            elif system == "Windows":
                subprocess.run(["explorer", "/select,", file_path])
            else:  # Linux
                # Try xdg-open on parent directory
                parent = str(Path(file_path).parent)
                subprocess.run(["xdg-open", parent])

            logger.debug(f"Revealed file in system: {file_path}")
        except Exception as e:
            logger.error(f"Failed to reveal file: {e}", exc_info=True)
