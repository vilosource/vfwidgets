"""File system watcher for detecting external file changes.

This module monitors open markdown files for external modifications
and notifies the application to reload them.
"""

import logging
from pathlib import Path

from PySide6.QtCore import QFileSystemWatcher, QObject, Signal

logger = logging.getLogger(__name__)


class FileWatcher(QObject):
    """Watches markdown files for external changes.

    Uses Qt's QFileSystemWatcher to monitor file system changes.
    Emits signals when watched files are modified externally.

    Signals:
        file_changed: Emitted when a watched file is modified (file_path: str)
        file_deleted: Emitted when a watched file is deleted (file_path: str)

    Example:
        >>> watcher = FileWatcher()
        >>> watcher.file_changed.connect(lambda path: print(f"Changed: {path}"))
        >>> watcher.watch_file("/tmp/test.md")
        >>> # External process modifies /tmp/test.md
        >>> # Signal emitted: "Changed: /tmp/test.md"
    """

    # Signals
    file_changed = Signal(str)  # file_path
    file_deleted = Signal(str)  # file_path

    def __init__(self):
        """Initialize file watcher."""
        super().__init__()
        self._watcher = QFileSystemWatcher()
        self._watched_files: set[str] = set()

        # Connect QFileSystemWatcher signals
        self._watcher.fileChanged.connect(self._on_file_changed)
        # Note: directoryChanged is not used for file watching

        logger.info("FileWatcher initialized")

    def watch_file(self, file_path: str) -> bool:
        """Start watching a file for changes.

        Args:
            file_path: Absolute path to file to watch

        Returns:
            True if file is now being watched, False on error

        Example:
            >>> watcher.watch_file("/tmp/test.md")
            True
        """
        path = Path(file_path).resolve()
        path_str = str(path)

        # Already watching
        if path_str in self._watched_files:
            logger.debug(f"Already watching: {path_str}")
            return True

        # Check file exists
        if not path.exists():
            logger.warning(f"Cannot watch non-existent file: {path_str}")
            return False

        # Add to watcher
        if self._watcher.addPath(path_str):
            self._watched_files.add(path_str)
            logger.info(f"Now watching: {path_str}")
            return True
        else:
            logger.error(f"Failed to watch file: {path_str}")
            return False

    def unwatch_file(self, file_path: str) -> bool:
        """Stop watching a file.

        Args:
            file_path: Path to file to stop watching

        Returns:
            True if file was being watched and is now unwatched

        Example:
            >>> watcher.unwatch_file("/tmp/test.md")
            True
        """
        path = Path(file_path).resolve()
        path_str = str(path)

        if path_str not in self._watched_files:
            logger.debug(f"File not being watched: {path_str}")
            return False

        # Remove from watcher
        self._watcher.removePath(path_str)
        self._watched_files.remove(path_str)
        logger.info(f"Stopped watching: {path_str}")
        return True

    def is_watching(self, file_path: str) -> bool:
        """Check if file is currently being watched.

        Args:
            file_path: Path to check

        Returns:
            True if file is being watched

        Example:
            >>> watcher.is_watching("/tmp/test.md")
            True
        """
        path = Path(file_path).resolve()
        return str(path) in self._watched_files

    def get_watched_files(self) -> list[str]:
        """Get list of all watched file paths.

        Returns:
            List of absolute file paths being watched

        Example:
            >>> watcher.get_watched_files()
            ['/tmp/file1.md', '/tmp/file2.md']
        """
        return list(self._watched_files)

    def clear_all(self) -> None:
        """Stop watching all files.

        Example:
            >>> watcher.clear_all()
        """
        if self._watched_files:
            for path in list(self._watched_files):
                self.unwatch_file(path)
            logger.info("Cleared all watched files")

    def _on_file_changed(self, file_path: str) -> None:
        """Handle QFileSystemWatcher fileChanged signal.

        Args:
            file_path: Path to changed file
        """
        path = Path(file_path)

        # Check if file still exists
        if not path.exists():
            logger.warning(f"File deleted: {file_path}")
            self.file_deleted.emit(file_path)

            # Remove from watched files
            if file_path in self._watched_files:
                self._watched_files.remove(file_path)

        else:
            logger.info(f"File changed: {file_path}")
            self.file_changed.emit(file_path)

            # Re-add to watcher (QFileSystemWatcher sometimes drops files after changes)
            if file_path in self._watched_files:
                # Try to re-add to ensure continued monitoring
                if not self._watcher.addPath(file_path):
                    logger.warning(f"Failed to re-add file to watcher: {file_path}")
