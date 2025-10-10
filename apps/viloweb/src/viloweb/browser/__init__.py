"""Browser components module.

This module contains the core browser components:
- BrowserTab: Single browser tab with QWebEngineView
- NavigationBar: URL bar and navigation controls
"""

from .tab import BrowserTab
from .navigation import NavigationBar

__all__ = ["BrowserTab", "NavigationBar"]
