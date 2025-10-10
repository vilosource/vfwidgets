"""Sidebar panels module.

This module contains sidebar panel widgets:
- BookmarksPanel: Bookmark management UI
- HomePanel: Homepage with quick links
- HistoryPanel: Browsing history (future)
- SettingsPanel: Browser settings (future)
"""

from .bookmarks import BookmarksPanel
from .home import HomePanel

__all__ = ["BookmarksPanel", "HomePanel"]
