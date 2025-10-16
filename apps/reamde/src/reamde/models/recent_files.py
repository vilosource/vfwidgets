"""Recent files manager for Reamde.

This module manages the list of recently opened files with LRU ordering.
"""

import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, QSettings, Signal

logger = logging.getLogger(__name__)


class RecentFilesManager(QObject):
    """Manages recently opened files with LRU (Least Recently Used) ordering.

    Files are stored in QSettings for persistence across sessions.
    The list is automatically limited to MAX_RECENT_FILES.

    Signals:
        recent_files_changed: Emitted when the recent files list changes

    Example:
        >>> manager = RecentFilesManager()
        >>> manager.add_file("/tmp/test.md")
        >>> manager.get_recent_files()
        ['/tmp/test.md']
    """

    # Maximum number of recent files to keep
    MAX_RECENT_FILES = 20

    # Signal
    recent_files_changed = Signal()

    def __init__(self, max_files: Optional[int] = None):
        """Initialize recent files manager.

        Args:
            max_files: Maximum number of recent files (default: 20)

        Example:
            >>> manager = RecentFilesManager(max_files=10)
        """
        super().__init__()
        self.settings = QSettings("reamde", "reamde")
        self.max_files = max_files or self.MAX_RECENT_FILES
        logger.info(f"RecentFilesManager initialized (max_files={self.max_files})")

    def add_file(self, file_path: str) -> None:
        """Add file to recent files list (or move to front if exists).

        Implements LRU - most recently used file goes to the front.

        Args:
            file_path: Absolute path to file

        Example:
            >>> manager.add_file("/tmp/test.md")
            >>> manager.get_recent_files()[0]
            '/tmp/test.md'
        """
        # Normalize path
        path = Path(file_path).resolve()
        path_str = str(path)

        # Get current list
        recent = self._load_recent_files()

        # Remove if already exists (will be re-added at front)
        if path_str in recent:
            recent.remove(path_str)

        # Add to front
        recent.insert(0, path_str)

        # Trim to max size
        recent = recent[: self.max_files]

        # Save
        self._save_recent_files(recent)
        self.recent_files_changed.emit()

        logger.info(f"Added to recent files: {path_str}")

    def remove_file(self, file_path: str) -> bool:
        """Remove file from recent files list.

        Args:
            file_path: Path to file to remove

        Returns:
            True if file was in list and removed, False otherwise

        Example:
            >>> manager.remove_file("/tmp/test.md")
            True
        """
        # Normalize path
        path = Path(file_path).resolve()
        path_str = str(path)

        # Get current list
        recent = self._load_recent_files()

        if path_str in recent:
            recent.remove(path_str)
            self._save_recent_files(recent)
            self.recent_files_changed.emit()
            logger.info(f"Removed from recent files: {path_str}")
            return True

        return False

    def get_recent_files(self, only_existing: bool = True) -> list[str]:
        """Get list of recent files in LRU order (most recent first).

        Args:
            only_existing: If True, only return files that still exist

        Returns:
            List of file paths, most recent first

        Example:
            >>> files = manager.get_recent_files()
            >>> files[0]  # Most recent
            '/tmp/test.md'
        """
        recent = self._load_recent_files()

        if only_existing:
            # Filter out non-existent files
            existing = [f for f in recent if Path(f).exists()]

            # If any were filtered out, save the cleaned list
            if len(existing) != len(recent):
                removed_count = len(recent) - len(existing)
                logger.info(f"Removed {removed_count} non-existent files from recent list")
                self._save_recent_files(existing)
                recent = existing

        return recent

    def clear_all(self) -> None:
        """Clear all recent files.

        Example:
            >>> manager.clear_all()
        """
        self._save_recent_files([])
        self.recent_files_changed.emit()
        logger.info("Cleared all recent files")

    def contains(self, file_path: str) -> bool:
        """Check if file is in recent files list.

        Args:
            file_path: Path to check

        Returns:
            True if file is in recent list

        Example:
            >>> manager.contains("/tmp/test.md")
            True
        """
        path = Path(file_path).resolve()
        recent = self._load_recent_files()
        return str(path) in recent

    def count(self) -> int:
        """Get number of recent files.

        Returns:
            Number of files in recent list

        Example:
            >>> manager.count()
            5
        """
        return len(self._load_recent_files())

    def _load_recent_files(self) -> list[str]:
        """Load recent files from QSettings.

        Returns:
            List of file paths
        """
        self.settings.beginGroup("recent_files")
        recent = self.settings.value("files", [], type=list)
        self.settings.endGroup()

        # Ensure it's a list of strings
        if not isinstance(recent, list):
            recent = []

        return recent

    def _save_recent_files(self, files: list[str]) -> None:
        """Save recent files to QSettings.

        Args:
            files: List of file paths to save
        """
        self.settings.beginGroup("recent_files")
        self.settings.setValue("files", files)
        self.settings.endGroup()
        self.settings.sync()
