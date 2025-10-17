"""WebView hosting layer for QWebEngineView integration.

This module provides a clean abstraction for QWebEngineView setup,
making it reusable across different webview-based widgets.
"""

import logging
from typing import Optional

from PySide6.QtCore import QObject, Qt, QUrl, Signal
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings

logger = logging.getLogger(__name__)


class WebViewHost(QObject):
    """Host for QWebEngineView content with common setup patterns.

    Provides:
    - QWebEnginePage creation and configuration
    - QWebChannel setup for Python ↔ JavaScript communication
    - Transparency configuration (3-layer pattern)
    - Page lifecycle signals
    - Common settings and security policies

    This class is designed to be reusable across all webview-based widgets
    (markdown widget, terminal widget, PDF viewer, etc.).

    Example:
        host = WebViewHost(parent_widget=my_widget)

        # Configure transparency
        host.set_transparent(True)

        # Load HTML
        host.load_url(html_url)

        # Register bridge object for JS communication
        host.register_bridge_object("pythonBridge", my_bridge)

        # Connect to lifecycle signals
        host.load_finished.connect(on_page_loaded)

    Signals:
        load_started: Emitted when page load starts
        load_progress(int): Emitted with load progress (0-100)
        load_finished(bool): Emitted when load finishes (success)
    """

    # Signals for page lifecycle
    load_started = Signal()
    load_progress = Signal(int)  # Progress 0-100
    load_finished = Signal(bool)  # Success/failure

    def __init__(self, parent_widget):
        """Initialize webview host.

        Args:
            parent_widget: Parent QWidget (typically the QWebEngineView)
        """
        super().__init__(parent_widget)
        self._parent_widget = parent_widget
        self._page: Optional[QWebEnginePage] = None
        self._channel: Optional[QWebChannel] = None
        self._is_transparent = False
        self._initialized = False

        logger.debug("WebViewHost created")

    def initialize(self, allow_remote_access: bool = False) -> QWebEnginePage:
        """Initialize and return QWebEnginePage.

        Creates page with standard configuration. This should be called
        once during widget initialization.

        Args:
            allow_remote_access: If True, enable LocalContentCanAccessRemoteUrls.
                               This allows local HTML to access remote URLs (e.g., CDN).
                               Default: False (secure by default)

                               Examples:
                               - True: Markdown widget (needs markdown-it from CDN)
                               - False: Terminal widget (xterm.js bundled locally)

        Returns:
            Configured QWebEnginePage instance

        Raises:
            RuntimeError: If already initialized
        """
        if self._initialized:
            raise RuntimeError("WebViewHost already initialized")

        # Create page
        self._page = QWebEnginePage(self._parent_widget)

        # Connect lifecycle signals
        self._page.loadStarted.connect(self._on_load_started)
        self._page.loadProgress.connect(self._on_load_progress)
        self._page.loadFinished.connect(self._on_load_finished)

        # Apply common settings
        self._configure_settings(allow_remote_access=allow_remote_access)

        # Create QWebChannel for Python ↔ JS communication
        self._channel = QWebChannel(self._page)
        self._page.setWebChannel(self._channel)

        self._initialized = True
        logger.debug(f"WebViewHost initialized (remote_access={allow_remote_access})")

        return self._page

    def _configure_settings(self, allow_remote_access: bool = False) -> None:
        """Configure QWebEngineSettings with secure defaults.

        Args:
            allow_remote_access: If True, enable LocalContentCanAccessRemoteUrls
        """
        if not self._page:
            return

        settings = self._page.settings()

        # Enable useful features
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)

        # Configurable remote access (secure by default)
        if allow_remote_access:
            settings.setAttribute(
                QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True
            )
            logger.debug("Remote URL access enabled")

        # Enable for development/debugging (disable in production if needed)
        settings.setAttribute(QWebEngineSettings.WebAttribute.ErrorPageEnabled, True)

        logger.debug("WebEngineSettings configured")

    def get_page(self) -> Optional[QWebEnginePage]:
        """Get the QWebEnginePage instance.

        Returns:
            QWebEnginePage if initialized, None otherwise
        """
        return self._page

    def load_url(self, url: QUrl) -> None:
        """Load URL in page.

        Args:
            url: QUrl to load (typically file:// for local HTML)

        Raises:
            RuntimeError: If not initialized
        """
        if not self._initialized or not self._page:
            raise RuntimeError("WebViewHost not initialized, call initialize() first")

        logger.debug(f"Loading URL: {url.toString()}")
        self._page.setUrl(url)

    def register_bridge_object(self, name: str, obj: QObject) -> None:
        """Register Python object for JavaScript access via QWebChannel.

        The object will be available in JavaScript as:
            new QWebChannel(qt.webChannelTransport, function(channel) {
                const pythonObj = channel.objects.name;
                pythonObj.someMethod();
            });

        Args:
            name: JavaScript name for the object
            obj: QObject with @Slot methods to expose to JavaScript

        Raises:
            RuntimeError: If not initialized

        Important:
            Keep a reference to obj to prevent garbage collection!
            The host keeps references automatically.
        """
        if not self._initialized or not self._channel:
            raise RuntimeError("WebViewHost not initialized")

        self._channel.registerObject(name, obj)
        logger.debug(f"Registered bridge object: {name}")

        # Keep reference to prevent GC (store in channel's dict)
        if not hasattr(self._channel, "_bridge_objects"):
            self._channel._bridge_objects = {}
        self._channel._bridge_objects[name] = obj

    def set_transparent(self, transparent: bool = True) -> None:
        """Configure page transparency (3-layer pattern).

        When True, applies transparency at:
        1. QWidget attributes (set on parent_widget externally)
        2. QWebEnginePage background
        3. HTML body background (via CSS, set by content)

        Args:
            transparent: If True, make page background transparent

        Note:
            Caller must also set these on the parent QWebEngineView:
                view.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
                view.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)
        """
        if not self._initialized or not self._page:
            logger.warning(
                "Cannot set transparency - host not initialized. "
                "Call initialize() first, then set_transparent()"
            )
            return

        self._is_transparent = transparent

        if transparent:
            # Layer 2: Set page background to transparent
            self._page.setBackgroundColor(Qt.GlobalColor.transparent)
            logger.debug("Page background set to transparent")
        else:
            # Set to white background
            from PySide6.QtGui import QColor

            self._page.setBackgroundColor(QColor(255, 255, 255))
            logger.debug("Page background set to white")

    def run_javascript(self, script: str, callback: Optional[callable] = None) -> None:
        """Execute JavaScript in page.

        Args:
            script: JavaScript code to execute
            callback: Optional callback for result: callback(result)

        Raises:
            RuntimeError: If not initialized
        """
        if not self._initialized or not self._page:
            raise RuntimeError("WebViewHost not initialized")

        if callback:
            self._page.runJavaScript(script, callback)
        else:
            self._page.runJavaScript(script)

    def is_transparent(self) -> bool:
        """Check if transparency is enabled.

        Returns:
            True if transparent mode is enabled
        """
        return self._is_transparent

    def is_initialized(self) -> bool:
        """Check if host is initialized.

        Returns:
            True if initialize() has been called
        """
        return self._initialized

    # Lifecycle signal handlers
    def _on_load_started(self) -> None:
        """Handle page load started."""
        logger.debug("Page load started")
        self.load_started.emit()

    def _on_load_progress(self, progress: int) -> None:
        """Handle page load progress.

        Args:
            progress: Load progress percentage (0-100)
        """
        logger.debug(f"Page load progress: {progress}%")
        self.load_progress.emit(progress)

    def _on_load_finished(self, success: bool) -> None:
        """Handle page load finished.

        Args:
            success: True if load succeeded, False if failed
        """
        if success:
            logger.debug("Page load finished successfully")
        else:
            logger.error("Page load failed")

        self.load_finished.emit(success)

    def shutdown(self) -> None:
        """Clean up resources.

        Should be called when widget is destroyed.
        """
        if self._channel:
            # Unregister all bridge objects
            if hasattr(self._channel, "_bridge_objects"):
                for name in list(self._channel._bridge_objects.keys()):
                    logger.debug(f"Unregistering bridge object: {name}")
                self._channel._bridge_objects.clear()

        if self._page:
            self._page.deleteLater()
            self._page = None

        self._channel = None
        self._initialized = False
        logger.debug("WebViewHost shutdown complete")
