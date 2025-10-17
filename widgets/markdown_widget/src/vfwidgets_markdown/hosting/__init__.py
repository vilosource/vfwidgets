"""Qt/WebView hosting layer.

This module provides abstractions for QWebEngineView integration,
resource loading, and page lifecycle management.
"""

from .resource_loader import ResourceLoader
from .webview_host import WebViewHost

__all__ = ["WebViewHost", "ResourceLoader"]
