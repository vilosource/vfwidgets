"""Browser components for ViloWeb.

This package contains the core browser functionality:
- BrowserTab: Wraps vfwidgets_webview.BrowserWidget
- ViloWebBridge: QWebChannel bridge for Python↔JavaScript
- Future: Extension system, download manager, etc.
"""

from .browser_tab import BrowserTab
from .viloweb_bridge import ViloWebBridge

__all__ = ["BrowserTab", "ViloWebBridge"]
