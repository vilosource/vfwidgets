"""ViloWeb - Educational web browser built with VFWidgets.

This package provides a complete, working web browser that demonstrates:
- Modern browser architecture (tabs, bookmarks, navigation)
- Chrome-style frameless window design
- Qt WebEngine integration
- QWebChannel Python↔JavaScript bridges
- Theme system integration
- Clean code organization

Educational Focus:
    ViloWeb is designed as a learning resource for:
    - Building Qt-based applications
    - Understanding browser architecture
    - Implementing Chrome-style UI with frameless windows
    - Managing complex widget hierarchies
    - Integrating theme systems

Quick Start:
    >>> import sys
    >>> from viloweb import main
    >>> sys.exit(main())

Components:
    - ChromeMainWindow: Chrome-style frameless browser window (v0.2.0)
    - MainWindow: Top-level browser window with tab bar (v0.1.0 - legacy)
    - BrowserTab: Individual tab wrapping vfwidgets-webview
    - ViloWebBridge: QWebChannel bridge for Python↔JavaScript
    - BookmarkManager: JSON-based bookmark storage
    - ViloWebApplication: Application class with theme integration

Example:
    >>> from viloweb import ViloWebApplication
    >>> app = ViloWebApplication()
    >>> app.run()
"""

from .application import ViloWebApplication, main
from .browser import BrowserTab, ViloWebBridge
from .managers import BookmarkManager
from .ui import ChromeMainWindow, MainWindow

__version__ = "0.2.0"
__all__ = [
    "ViloWebApplication",
    "ChromeMainWindow",
    "MainWindow",
    "BrowserTab",
    "ViloWebBridge",
    "BookmarkManager",
    "main",
]
