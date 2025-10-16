"""Window controller for Reamde application.

This controller coordinates between the data models and the window view,
implementing the core business logic for file operations and session management.
"""

import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, Signal

from ..models.document import DocumentCollection
from ..models.file_watcher import FileWatcher
from ..models.recent_files import RecentFilesManager
from ..models.session import SessionManager, SessionState
from ..utils.error_handler import ErrorHandler

logger = logging.getLogger(__name__)


class WindowController(QObject):
    """Controller for coordinating window operations and models.

    This is the main business logic layer that sits between the view (ReamdeWindow)
    and the models (DocumentCollection, SessionManager, etc.).

    Responsibilities:
    - File operations (open, close, save)
    - Session persistence (save/restore on startup/shutdown)
    - Recent files tracking
    - File watching for external changes
    - Error handling and user feedback

    Signals:
        file_opened: Emitted when file is opened (file_path: str)
        file_closed: Emitted when file is closed (file_path: str)
        active_file_changed: Emitted when active file changes (file_path: str or None)
        session_restored: Emitted after session is restored on startup

    Example:
        >>> controller = WindowController(parent_window)
        >>> controller.open_file("/tmp/README.md")
        >>> controller.get_active_document()
        DocumentModel(file_path='/tmp/README.md', ...)
    """

    # Signals
    file_opened = Signal(str)  # file_path
    file_closed = Signal(str)  # file_path
    active_file_changed = Signal(object)  # file_path (str or None)
    session_restored = Signal()  # No args

    def __init__(self, parent=None):
        """Initialize window controller.

        Args:
            parent: Parent QWidget (typically ReamdeWindow) for error dialogs
        """
        super().__init__(parent)
        self.parent_widget = parent

        # Initialize models
        self.documents = DocumentCollection()
        self.session_manager = SessionManager()
        self.recent_files = RecentFilesManager()
        self.file_watcher = FileWatcher()

        # Connect model signals
        self._connect_signals()

        logger.info("WindowController initialized")

    def _connect_signals(self) -> None:
        """Connect internal model signals."""
        # Document collection signals
        self.documents.active_changed.connect(self._on_active_document_changed)

        # File watcher signals
        self.file_watcher.file_changed.connect(self._on_file_changed_externally)
        self.file_watcher.file_deleted.connect(self._on_file_deleted_externally)

    def open_file(self, file_path: str, set_active: bool = True) -> bool:
        """Open a file and add to document collection.

        Args:
            file_path: Path to file to open
            set_active: If True, make this the active document

        Returns:
            True if file opened successfully, False otherwise

        Example:
            >>> controller.open_file("/tmp/README.md")
            True
        """
        try:
            path = Path(file_path)

            # Check if already open
            if self.documents.is_file_open(str(path)):
                logger.info(f"File already open: {path}")
                if set_active:
                    self.documents.set_active_document(str(path))
                return True

            # Add document (will raise exception if file doesn't exist)
            self.documents.add_document(str(path))

            # Set as active if requested
            if set_active:
                self.documents.set_active_document(str(path))

            # Start watching for external changes
            self.file_watcher.watch_file(str(path))

            # Add to recent files
            self.recent_files.add_file(str(path))

            logger.info(f"File opened: {path}")
            self.file_opened.emit(str(path))
            return True

        except FileNotFoundError as e:
            ErrorHandler.handle_file_error(self.parent_widget, Path(file_path), e, "opening")
            return False
        except PermissionError as e:
            ErrorHandler.handle_file_error(self.parent_widget, Path(file_path), e, "opening")
            return False
        except Exception as e:
            ErrorHandler.handle_file_error(self.parent_widget, Path(file_path), e, "opening")
            return False

    def close_file(self, file_path: str, check_modified: bool = True) -> bool:
        """Close a file and remove from document collection.

        Args:
            file_path: Path to file to close
            check_modified: If True, prompt user if file has unsaved changes

        Returns:
            True if file closed, False if user cancelled

        Example:
            >>> controller.close_file("/tmp/README.md")
            True
        """
        try:
            doc = self.documents.get_document(file_path)
            if not doc:
                logger.warning(f"Cannot close - file not open: {file_path}")
                return False

            # Check for unsaved changes
            if check_modified and doc.is_modified:
                title = "Unsaved Changes"
                message = f"Save changes to {Path(file_path).name}?"
                if not ErrorHandler.confirm_action(
                    self.parent_widget, title, message, default_yes=True
                ):
                    # User chose No - discard changes and close
                    pass
                else:
                    # User chose Yes - save first
                    if not self.save_file(file_path):
                        # Save failed, don't close
                        return False

            # Stop watching file
            self.file_watcher.unwatch_file(file_path)

            # Remove from collection
            self.documents.remove_document(file_path)

            logger.info(f"File closed: {file_path}")
            self.file_closed.emit(file_path)
            return True

        except Exception as e:
            logger.error(f"Error closing file {file_path}: {e}", exc_info=True)
            ErrorHandler.show_warning(
                self.parent_widget, "Error Closing File", f"Failed to close file: {e}"
            )
            return False

    def save_file(self, file_path: Optional[str] = None) -> bool:
        """Save a file to disk.

        Args:
            file_path: Path to file to save (None = active document)

        Returns:
            True if saved successfully, False otherwise

        Example:
            >>> controller.save_file("/tmp/README.md")
            True
        """
        try:
            # Get document to save
            if file_path:
                doc = self.documents.get_document(file_path)
            else:
                doc = self.documents.get_active_document()

            if not doc:
                logger.warning("Cannot save - no document specified or active")
                return False

            # Save to disk
            doc.save_to_file()

            logger.info(f"File saved: {doc.file_path}")
            return True

        except PermissionError as e:
            ErrorHandler.handle_file_error(self.parent_widget, Path(doc.file_path), e, "saving")
            return False
        except OSError as e:
            ErrorHandler.handle_file_error(self.parent_widget, Path(doc.file_path), e, "saving")
            return False
        except Exception as e:
            ErrorHandler.handle_file_error(self.parent_widget, Path(doc.file_path), e, "saving")
            return False

    def close_all_files(self, check_modified: bool = True) -> bool:
        """Close all open files.

        Args:
            check_modified: If True, check each file for unsaved changes

        Returns:
            True if all files closed, False if user cancelled any

        Example:
            >>> controller.close_all_files()
            True
        """
        # Get list of files (copy, as we'll be modifying the collection)
        file_paths = list(self.documents.get_open_file_paths())

        for file_path in file_paths:
            if not self.close_file(file_path, check_modified):
                # User cancelled, stop closing
                return False

        return True

    def get_active_document(self):
        """Get the currently active document.

        Returns:
            DocumentModel or None

        Example:
            >>> doc = controller.get_active_document()
            >>> doc.title if doc else "No active document"
            'README.md'
        """
        return self.documents.get_active_document()

    def get_open_files(self) -> list[str]:
        """Get list of all open file paths.

        Returns:
            List of absolute file paths

        Example:
            >>> controller.get_open_files()
            ['/tmp/file1.md', '/tmp/file2.md']
        """
        return self.documents.get_open_file_paths()

    def set_active_file(self, file_path: str) -> bool:
        """Set the active file.

        Args:
            file_path: Path to file to make active

        Returns:
            True if successful, False if file not open

        Example:
            >>> controller.set_active_file("/tmp/README.md")
            True
        """
        return self.documents.set_active_document(file_path)

    def has_unsaved_changes(self) -> bool:
        """Check if any document has unsaved changes.

        Returns:
            True if any document is modified

        Example:
            >>> controller.has_unsaved_changes()
            False
        """
        return self.documents.has_unsaved_changes()

    def save_session(self) -> None:
        """Save current session state to disk.

        Saves list of open files and active file index for restoration.

        Example:
            >>> controller.save_session()
        """
        try:
            # Get current state
            open_files = self.documents.get_open_file_paths()
            active_doc = self.documents.get_active_document()

            # Find active index
            active_index = -1
            if active_doc:
                try:
                    active_index = open_files.index(active_doc.file_path)
                except ValueError:
                    pass

            # Create session state
            state = SessionState(open_files=open_files, active_file_index=active_index)

            # Save
            self.session_manager.save_session(state)
            logger.info("Session saved successfully")

        except Exception as e:
            logger.error(f"Failed to save session: {e}", exc_info=True)
            # Don't show error dialog on exit - just log

    def restore_session(self) -> None:
        """Restore previous session from disk.

        Opens all files that were open in the previous session.

        Example:
            >>> controller.restore_session()
        """
        try:
            # Load session
            state = self.session_manager.load_session()
            if not state:
                logger.info("No previous session to restore")
                return

            # Open files
            for file_path in state.open_files:
                # Don't set active yet
                self.open_file(file_path, set_active=False)

            # Set active file
            if 0 <= state.active_file_index < len(state.open_files):
                active_path = state.open_files[state.active_file_index]
                self.documents.set_active_document(active_path)

            logger.info(f"Session restored: {len(state.open_files)} files")
            self.session_restored.emit()

        except Exception as e:
            ErrorHandler.handle_session_error(self.parent_widget, e)

    def get_recent_files(self, max_count: Optional[int] = None) -> list[str]:
        """Get list of recent files.

        Args:
            max_count: Maximum number of files to return (None = all)

        Returns:
            List of file paths in LRU order (most recent first)

        Example:
            >>> files = controller.get_recent_files(max_count=10)
            >>> len(files)
            10
        """
        files = self.recent_files.get_recent_files(only_existing=True)
        if max_count:
            return files[:max_count]
        return files

    def _on_active_document_changed(self, file_path) -> None:
        """Handle active document change from document collection.

        Args:
            file_path: New active file path (str or None)
        """
        logger.debug(f"Active document changed: {file_path}")
        self.active_file_changed.emit(file_path)

    def _on_file_changed_externally(self, file_path: str) -> None:
        """Handle external file modification.

        Args:
            file_path: Path to changed file
        """
        logger.info(f"File changed externally: {file_path}")

        # Ask user if they want to reload
        path = Path(file_path)
        title = "File Changed"
        message = (
            f"The file {path.name} has been modified by another program.\n\n"
            f"Do you want to reload it?"
        )

        if ErrorHandler.confirm_action(self.parent_widget, title, message, default_yes=True):
            # Reload file
            try:
                doc = self.documents.get_document(file_path)
                if doc:
                    # Re-read content
                    new_content = path.read_text(encoding="utf-8")
                    doc.content = new_content
                    doc.is_modified = False
                    logger.info(f"File reloaded: {file_path}")

            except Exception as e:
                ErrorHandler.handle_file_error(self.parent_widget, path, e, "reloading")

    def _on_file_deleted_externally(self, file_path: str) -> None:
        """Handle external file deletion.

        Args:
            file_path: Path to deleted file
        """
        logger.warning(f"File deleted externally: {file_path}")

        # Notify user
        path = Path(file_path)
        title = "File Deleted"
        message = f"The file {path.name} has been deleted by another program."

        ErrorHandler.show_warning(self.parent_widget, title, message)

        # Close the file
        self.close_file(file_path, check_modified=False)
