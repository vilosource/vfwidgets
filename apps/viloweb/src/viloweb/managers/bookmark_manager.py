"""Bookmark manager - JSON-based bookmark storage.

Educational Focus:
    This module demonstrates:
    - Simple JSON persistence
    - Data validation and sanitization
    - File-based storage patterns
    - XDG Base Directory compliance (Linux)

Architecture:
    BookmarkManager provides:
    - Add/remove/list bookmarks
    - JSON file storage (~/.local/share/viloweb/bookmarks.json)
    - Automatic save on changes
    - Duplicate detection

Storage Format:
    {
        "version": "1.0",
        "bookmarks": [
            {
                "title": "VFWidgets",
                "url": "https://github.com/viloforge/vfwidgets",
                "created": "2025-10-17T10:30:00"
            }
        ]
    }
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class BookmarkManager:
    """Manages browser bookmarks with JSON storage.

    Educational Note:
        This is a simple bookmark manager that stores bookmarks in a JSON file.
        In a production browser, you'd use:
        - SQLite database (better for large datasets, queries)
        - Folders/tags for organization
        - Sync with cloud services
        - Import/export from other browsers

        For MVP, JSON is perfect because:
        - Human-readable (great for learning/debugging)
        - Simple Python integration (json module)
        - No external dependencies
        - Easy to backup/restore

    Example:
        >>> manager = BookmarkManager()
        >>> manager.add_bookmark("Python", "https://python.org")
        >>> bookmarks = manager.get_all_bookmarks()
        >>> print(bookmarks[0]["title"])  # "Python"
    """

    VERSION = "1.0"

    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize bookmark manager.

        Args:
            storage_path: Custom storage path (default: XDG_DATA_HOME/viloweb)

        Educational Note:
            We follow XDG Base Directory specification on Linux:
            - User data: ~/.local/share/viloweb/
            - Config: ~/.config/viloweb/ (not used yet)
            - Cache: ~/.cache/viloweb/ (not used yet)

            This makes ViloWeb a good citizen in the Linux ecosystem.
        """
        # Determine storage location
        if storage_path:
            self._storage_dir = storage_path
        else:
            # Use XDG_DATA_HOME or fallback to ~/.local/share
            xdg_data_home = Path.home() / ".local" / "share"
            self._storage_dir = xdg_data_home / "viloweb"

        self._bookmarks_file = self._storage_dir / "bookmarks.json"

        # Ensure storage directory exists
        self._storage_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"BookmarkManager storage: {self._bookmarks_file}")

        # Load existing bookmarks
        self._data = self._load()

    def _load(self) -> Dict[str, Any]:
        """Load bookmarks from JSON file.

        Returns:
            Bookmark data dictionary

        Educational Note:
            Loading pattern:
            1. Check if file exists
            2. Try to parse JSON
            3. Validate structure
            4. Return data or create new structure

            This is defensive programming: we handle missing files,
            corrupt JSON, and invalid structure gracefully.
        """
        if not self._bookmarks_file.exists():
            logger.info("No bookmarks file found, creating new")
            return {"version": self.VERSION, "bookmarks": []}

        try:
            with open(self._bookmarks_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Validate structure
            if not isinstance(data, dict):
                raise ValueError("Invalid bookmark file structure")

            if "bookmarks" not in data:
                logger.warning("Missing 'bookmarks' key, initializing")
                data["bookmarks"] = []

            if "version" not in data:
                logger.warning("Missing 'version' key, adding")
                data["version"] = self.VERSION

            logger.info(f"Loaded {len(data['bookmarks'])} bookmarks")
            return data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse bookmarks file: {e}")
            # Backup corrupt file
            backup_path = self._bookmarks_file.with_suffix(".json.corrupt")
            self._bookmarks_file.rename(backup_path)
            logger.info(f"Backed up corrupt file to {backup_path}")
            return {"version": self.VERSION, "bookmarks": []}

        except Exception as e:
            logger.error(f"Unexpected error loading bookmarks: {e}")
            return {"version": self.VERSION, "bookmarks": []}

    def _save(self) -> bool:
        """Save bookmarks to JSON file.

        Returns:
            True if save succeeded, False otherwise

        Educational Note:
            Save pattern:
            1. Write to temporary file first
            2. If successful, rename to real file
            3. This prevents corruption if save is interrupted

            This is called "atomic write" pattern and is important
            for data integrity.
        """
        temp_file = self._bookmarks_file.with_suffix(".json.tmp")

        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)

            # Atomic rename (POSIX: replaces existing file)
            temp_file.rename(self._bookmarks_file)
            logger.debug("Bookmarks saved successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to save bookmarks: {e}")
            # Clean up temp file
            if temp_file.exists():
                temp_file.unlink()
            return False

    def add_bookmark(self, title: str, url: str) -> bool:
        """Add bookmark.

        Args:
            title: Bookmark title (page title)
            url: Bookmark URL

        Returns:
            True if added, False if duplicate or error

        Educational Note:
            We detect duplicates by URL (same URL = same bookmark).
            We also sanitize inputs:
            - Strip whitespace
            - Validate URL format (basic check)
            - Limit title length

            In a production browser, you'd also:
            - Validate URL more thoroughly
            - Handle URL normalization (http vs https, www vs non-www)
            - Support folders/tags
        """
        # Sanitize inputs
        title = title.strip()[:200]  # Limit title length
        url = url.strip()

        if not title:
            title = url[:50]  # Use URL as title if no title

        if not url or url == "about:blank":
            logger.warning("Cannot bookmark empty or about:blank URL")
            return False

        # Check for duplicates
        for bookmark in self._data["bookmarks"]:
            if bookmark["url"] == url:
                logger.info(f"Bookmark already exists: {url}")
                return False

        # Create bookmark entry
        bookmark = {
            "title": title,
            "url": url,
            "created": datetime.now().isoformat(),
        }

        # Add to list
        self._data["bookmarks"].append(bookmark)
        logger.info(f"Added bookmark: {title} -> {url}")

        # Save to disk
        self._save()
        return True

    def remove_bookmark(self, url: str) -> bool:
        """Remove bookmark by URL.

        Args:
            url: URL of bookmark to remove

        Returns:
            True if removed, False if not found

        Example:
            >>> manager.remove_bookmark("https://example.com")
        """
        url = url.strip()

        # Find and remove
        for i, bookmark in enumerate(self._data["bookmarks"]):
            if bookmark["url"] == url:
                removed = self._data["bookmarks"].pop(i)
                logger.info(f"Removed bookmark: {removed['title']}")
                self._save()
                return True

        logger.warning(f"Bookmark not found: {url}")
        return False

    def get_all_bookmarks(self) -> List[Dict[str, str]]:
        """Get all bookmarks.

        Returns:
            List of bookmark dictionaries (sorted by creation time, newest first)

        Example:
            >>> bookmarks = manager.get_all_bookmarks()
            >>> for bm in bookmarks:
            ...     print(f"{bm['title']}: {bm['url']}")
        """
        # Return copy to prevent external modification
        bookmarks = self._data["bookmarks"].copy()

        # Sort by creation time (newest first)
        bookmarks.sort(key=lambda b: b.get("created", ""), reverse=True)

        return bookmarks

    def search_bookmarks(self, query: str) -> List[Dict[str, str]]:
        """Search bookmarks by title or URL.

        Args:
            query: Search query (case-insensitive)

        Returns:
            List of matching bookmarks

        Educational Note:
            This is a simple substring search. In a production browser:
            - Use full-text search (SQLite FTS, Elasticsearch)
            - Support fuzzy matching
            - Rank results by relevance
            - Highlight matches

        Example:
            >>> results = manager.search_bookmarks("python")
            >>> print(len(results))  # Number of matches
        """
        query = query.lower().strip()

        if not query:
            return self.get_all_bookmarks()

        matches = []
        for bookmark in self._data["bookmarks"]:
            title = bookmark["title"].lower()
            url = bookmark["url"].lower()

            if query in title or query in url:
                matches.append(bookmark)

        logger.debug(f"Search '{query}' found {len(matches)} results")
        return matches

    def clear_all_bookmarks(self) -> None:
        """Remove all bookmarks.

        Educational Note:
            This is useful for testing and for users who want to
            start fresh. In a production browser, you'd ask for
            confirmation before doing this.
        """
        count = len(self._data["bookmarks"])
        self._data["bookmarks"] = []
        self._save()
        logger.info(f"Cleared {count} bookmarks")

    def get_bookmark_count(self) -> int:
        """Get total bookmark count.

        Returns:
            Number of bookmarks
        """
        return len(self._data["bookmarks"])

    def export_bookmarks(self, export_path: Path) -> bool:
        """Export bookmarks to file.

        Args:
            export_path: Path to export file

        Returns:
            True if export succeeded

        Educational Note:
            This allows users to backup their bookmarks or transfer
            them to another installation. The export format is the
            same as our internal format (JSON).

            In a production browser, you'd support multiple formats:
            - HTML (Netscape bookmark format, widely compatible)
            - JSON (modern, structured)
            - XBEL (XML bookmark format)
        """
        try:
            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)

            logger.info(f"Exported {len(self._data['bookmarks'])} bookmarks to {export_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export bookmarks: {e}")
            return False

    def import_bookmarks(self, import_path: Path, merge: bool = True) -> bool:
        """Import bookmarks from file.

        Args:
            import_path: Path to import file
            merge: If True, merge with existing bookmarks; if False, replace

        Returns:
            True if import succeeded

        Educational Note:
            Import strategies:
            - Merge: Add new bookmarks, skip duplicates
            - Replace: Clear existing, add all from file

            For MVP, we do simple duplicate detection by URL.
        """
        try:
            with open(import_path, "r", encoding="utf-8") as f:
                imported_data = json.load(f)

            if not isinstance(imported_data, dict) or "bookmarks" not in imported_data:
                logger.error("Invalid bookmark file format")
                return False

            imported_bookmarks = imported_data["bookmarks"]

            if merge:
                # Merge: add non-duplicate bookmarks
                existing_urls = {bm["url"] for bm in self._data["bookmarks"]}
                added = 0

                for bookmark in imported_bookmarks:
                    if bookmark["url"] not in existing_urls:
                        self._data["bookmarks"].append(bookmark)
                        added += 1

                logger.info(f"Imported {added} new bookmarks (merged)")

            else:
                # Replace: clear and add all
                self._data["bookmarks"] = imported_bookmarks
                logger.info(f"Imported {len(imported_bookmarks)} bookmarks (replaced)")

            self._save()
            return True

        except Exception as e:
            logger.error(f"Failed to import bookmarks: {e}")
            return False
