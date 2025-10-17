"""vfwidgets-webview: Clean, reusable web browser widget for PySide6.

This package provides a simple, well-designed browser widget that can be
embedded in any PySide6 application. It features:

- Complete browser widget with navigation
- Theme system integration
- Clean, documented API
- Minimal dependencies

Basic Usage:
    >>> from vfwidgets_webview import BrowserWidget
    >>> browser = BrowserWidget()
    >>> browser.navigate("https://example.com")
    >>> browser.show()

Components:
    - BrowserWidget: Complete browser (navigation + webview)
    - NavigationBar: Standalone navigation bar
    - WebView: Themed QWebEngineView wrapper
    - WebPage: Custom QWebEnginePage with extra features
"""

# Import all components
from .browser_widget import BrowserWidget
from .navigation_bar import NavigationBar
from .webpage import WebPage
from .webview import WebView

__version__ = "0.1.0"
__all__ = [
    "BrowserWidget",
    "NavigationBar",
    "WebView",
    "WebPage",
]
