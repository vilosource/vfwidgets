"""Bookmark management with JSON persistence."""

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class Bookmark:
    """Bookmark data model.

    Attributes:
        title: Page title
        url: Page URL
        folder: Folder name (empty string for root)
        added: ISO format timestamp when added
        tags: List of tag strings (future enhancement)
        favicon: Base64 encoded favicon (future enhancement)
    """

    title: str
    url: str
    folder: str = ""
    added: str = ""
    tags: Optional[List[str]] = None
    favicon: Optional[str] = None

    def __post_init__(self):
        """Set default values after initialization."""
        if not self.added:
            self.added = datetime.now().isoformat()
        if self.tags is None:
            self.tags = []


class BookmarkManager:
    """Manage bookmarks with JSON file persistence.

    Storage location: ~/.viloweb/bookmarks.json

    File format:
    {
        "version": 1,
        "bookmarks": [
            {
                "title": "Example",
                "url": "https://example.com",
                "folder": "",
                "added": "2025-10-10T12:00:00",
                "tags": [],
                "favicon": null
            }
        ],
        "folders": []
    }
    """

    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize bookmark manager.

        Args:
            data_dir: Directory to store bookmarks.json (default: ~/.viloweb/)
        """
        if data_dir is None:
            data_dir = Path.home() / ".viloweb"

        self.data_dir = data_dir
        self.bookmarks_file = data_dir / "bookmarks.json"

        # Ensure directory exists
        self.data_dir.mkdir(exist_ok=True)

        # In-memory storage
        self._bookmarks: List[Bookmark] = []
        self._folders: List[str] = []

        # Load existing bookmarks
        self.load()

        logger.info(f"BookmarkManager initialized with {len(self._bookmarks)} bookmarks")

    def load(self):
        """Load bookmarks from JSON file."""
        if not self.bookmarks_file.exists():
            logger.info("No bookmarks file found, starting fresh")
            return

        try:
            with open(self.bookmarks_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Load bookmarks
            self._bookmarks = [Bookmark(**b) for b in data.get("bookmarks", [])]
            self._folders = data.get("folders", [])

            logger.info(f"Loaded {len(self._bookmarks)} bookmarks from {self.bookmarks_file}")
        except Exception as e:
            logger.error(f"Error loading bookmarks: {e}")
            self._bookmarks = []
            self._folders = []

    def save(self):
        """Save bookmarks to JSON file."""
        try:
            data = {
                "version": 1,
                "bookmarks": [asdict(b) for b in self._bookmarks],
                "folders": self._folders,
            }

            with open(self.bookmarks_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved {len(self._bookmarks)} bookmarks to {self.bookmarks_file}")
        except Exception as e:
            logger.error(f"Error saving bookmarks: {e}")

    def add_bookmark(self, url: str, title: str, folder: str = "") -> Bookmark:
        """Add a new bookmark.

        Args:
            url: Page URL
            title: Page title
            folder: Folder name (empty for root)

        Returns:
            Created Bookmark object
        """
        # Check if bookmark already exists
        existing = self.get_bookmark_by_url(url)
        if existing:
            logger.warning(f"Bookmark already exists: {url}")
            return existing

        bookmark = Bookmark(title=title, url=url, folder=folder)
        self._bookmarks.append(bookmark)
        self.save()

        logger.info(f"Added bookmark: {title} ({url})")
        return bookmark

    def remove_bookmark(self, url: str) -> bool:
        """Remove a bookmark by URL.

        Args:
            url: Bookmark URL to remove

        Returns:
            True if bookmark was removed, False if not found
        """
        original_count = len(self._bookmarks)
        self._bookmarks = [b for b in self._bookmarks if b.url != url]

        if len(self._bookmarks) < original_count:
            self.save()
            logger.info(f"Removed bookmark: {url}")
            return True

        logger.warning(f"Bookmark not found: {url}")
        return False

    def get_bookmark_by_url(self, url: str) -> Optional[Bookmark]:
        """Get bookmark by URL.

        Args:
            url: Bookmark URL

        Returns:
            Bookmark if found, None otherwise
        """
        for bookmark in self._bookmarks:
            if bookmark.url == url:
                return bookmark
        return None

    def get_all_bookmarks(self) -> List[Bookmark]:
        """Get all bookmarks.

        Returns:
            List of all bookmarks
        """
        return self._bookmarks.copy()

    def get_bookmarks_by_folder(self, folder: str) -> List[Bookmark]:
        """Get bookmarks in a specific folder.

        Args:
            folder: Folder name (empty string for root)

        Returns:
            List of bookmarks in the folder
        """
        return [b for b in self._bookmarks if b.folder == folder]

    def get_folders(self) -> List[str]:
        """Get list of all folders.

        Returns:
            List of folder names
        """
        return self._folders.copy()

    def add_folder(self, folder_name: str) -> bool:
        """Add a new folder.

        Args:
            folder_name: Name of folder to create

        Returns:
            True if folder was created, False if already exists
        """
        if folder_name in self._folders:
            logger.warning(f"Folder already exists: {folder_name}")
            return False

        self._folders.append(folder_name)
        self.save()
        logger.info(f"Added folder: {folder_name}")
        return True

    def remove_folder(self, folder_name: str) -> bool:
        """Remove a folder (bookmarks in folder are moved to root).

        Args:
            folder_name: Name of folder to remove

        Returns:
            True if folder was removed, False if not found
        """
        if folder_name not in self._folders:
            logger.warning(f"Folder not found: {folder_name}")
            return False

        # Move bookmarks in this folder to root
        for bookmark in self._bookmarks:
            if bookmark.folder == folder_name:
                bookmark.folder = ""

        self._folders.remove(folder_name)
        self.save()
        logger.info(f"Removed folder: {folder_name}")
        return True

    def is_bookmarked(self, url: str) -> bool:
        """Check if URL is bookmarked.

        Args:
            url: URL to check

        Returns:
            True if URL is bookmarked, False otherwise
        """
        return self.get_bookmark_by_url(url) is not None
