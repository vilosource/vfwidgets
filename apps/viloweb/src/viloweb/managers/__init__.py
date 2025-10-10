"""Data managers module.

This module contains data persistence managers:
- BookmarkManager: Bookmark storage and management (JSON)
- HistoryManager: Browsing history (SQLite) - future
"""

from .bookmarks import BookmarkManager

__all__ = ["BookmarkManager"]
