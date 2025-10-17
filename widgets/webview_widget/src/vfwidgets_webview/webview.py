"""WebView wrapper around QWebEngineView.

This module provides a clean, pythonic wrapper around Qt's QWebEngineView.
Instead of directly inheriting from QWebEngineView (tight coupling), we
use composition (loose coupling) to wrap it.

Educational Focus:
    This code demonstrates:
    - Composition over inheritance pattern
    - Signal forwarding from wrapped widget
    - Clean API design hiding Qt complexity
    - How to work with QWebEngineView and QWebEnginePage
"""

import logging
from typing import Optional

from PySide6.QtCore import QUrl, Signal, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWebEngineCore import QWebEngineProfile
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget

from .webpage import WebPage

logger = logging.getLogger(__name__)


class WebView(QWidget):
    """Clean wrapper around QWebEngineView.

    This widget wraps QWebEngineView to provide a simpler, more pythonic API.
    We use composition instead of inheritance to:
    1. Hide Qt complexity from users
    2. Provide cleaner method names
    3. Make it easier to add features later
    4. Keep our API independent of Qt's API changes

    Educational Note:
        COMPOSITION vs INHERITANCE:

        Inheritance (tight coupling):
            class WebView(QWebEngineView):
                # Directly extends Qt class
                # Hard to change Qt's behavior
                # Exposes all Qt internals

        Composition (loose coupling):
            class WebView(QWidget):
                def __init__(self):
                    self._engine_view = QWebEngineView()
                # We control the interface
                # Easy to customize behavior
                # Hide implementation details

        We chose composition for flexibility and clean API.

    Example:
        >>> webview = WebView()
        >>> webview.load("https://example.com")
        >>> webview.back()

    Signals:
        load_started: Page load started
        load_progress(int): Loading progress (0-100)
        load_finished(bool): Load finished (success/failure)
        title_changed(str): Page title changed
        url_changed(str): URL changed
        icon_changed(QIcon): Favicon changed
    """

    # Signals - forwarded from QWebEngineView
    # We emit these when the underlying QWebEngineView emits its signals
    load_started = Signal()
    load_progress = Signal(int)  # 0-100
    load_finished = Signal(bool)  # success/failure
    title_changed = Signal(str)
    url_changed = Signal(str)  # We convert QUrl to str for simplicity
    icon_changed = Signal(QIcon)

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize web view.

        Educational Note:
            Setup order:
            1. Create widget
            2. Create custom WebPage
            3. Create QWebEngineView
            4. Connect signals
            5. Setup layout

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Create custom web page with our enhanced features
        self._page = WebPage(self)

        # Create QWebEngineView (the actual rendering widget)
        self._engine_view = QWebEngineView(self)

        # Set our custom page on the view
        self._engine_view.setPage(self._page)

        # Setup layout to contain the engine view
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # No margins
        layout.addWidget(self._engine_view)

        # Set size policy: expand both horizontally and vertically
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Connect signals from engine view to our signals
        self._connect_signals()

        logger.debug("WebView initialized")

    def _connect_signals(self) -> None:
        """Connect QWebEngineView signals to our signals.

        Educational Note:
            Signal forwarding pattern:
            1. QWebEngineView emits signal (e.g., loadStarted)
            2. We receive it in our internal handler
            3. We emit our own signal (e.g., load_started)

            Why forward instead of direct connection?
            - We can add custom logic before emitting
            - We can transform data (e.g., QUrl → str)
            - We keep internal implementation hidden
            - We can log events for debugging
        """
        # Load events
        self._engine_view.loadStarted.connect(self._on_load_started)
        self._engine_view.loadProgress.connect(self._on_load_progress)
        self._engine_view.loadFinished.connect(self._on_load_finished)

        # Page changes
        self._engine_view.titleChanged.connect(self._on_title_changed)
        self._engine_view.urlChanged.connect(self._on_url_changed)
        self._engine_view.iconChanged.connect(self._on_icon_changed)

        logger.debug("Signals connected")

    # ===== Signal Handlers =====
    # These methods are called when QWebEngineView emits signals
    # We forward them to our own signals (sometimes with modifications)

    @Slot()
    def _on_load_started(self) -> None:
        """Handle load started event."""
        logger.debug("Page load started")
        self.load_started.emit()

    @Slot(int)
    def _on_load_progress(self, progress: int) -> None:
        """Handle load progress event.

        Args:
            progress: Loading progress 0-100
        """
        logger.debug(f"Load progress: {progress}%")
        self.load_progress.emit(progress)

    @Slot(bool)
    def _on_load_finished(self, success: bool) -> None:
        """Handle load finished event.

        Args:
            success: True if loaded successfully, False if error
        """
        if success:
            logger.info(f"Page loaded successfully: {self.url()}")
        else:
            logger.warning(f"Page load failed: {self.url()}")

        self.load_finished.emit(success)

    @Slot(str)
    def _on_title_changed(self, title: str) -> None:
        """Handle title changed event.

        Args:
            title: New page title
        """
        logger.debug(f"Title changed: {title}")
        self.title_changed.emit(title)

    @Slot(QUrl)
    def _on_url_changed(self, qurl: QUrl) -> None:
        """Handle URL changed event.

        Educational Note:
            Qt uses QUrl objects, but Python programmers expect strings.
            We convert QUrl → str here to make the API more pythonic.

        Args:
            qurl: New URL (QUrl object)
        """
        url = qurl.toString()
        logger.debug(f"URL changed: {url}")
        self.url_changed.emit(url)

    @Slot(QIcon)
    def _on_icon_changed(self, icon: QIcon) -> None:
        """Handle icon (favicon) changed event.

        Args:
            icon: New page icon
        """
        logger.debug("Icon changed")
        self.icon_changed.emit(icon)

    # ===== Public API =====
    # These are the methods users of this widget will call

    def load(self, url: str) -> None:
        """Load a URL.

        Educational Note:
            This is the main method for navigating to a page.
            We accept a string and convert to QUrl internally.

            URL handling:
            - "example.com" → "https://example.com"
            - "http://example.com" → "http://example.com"
            - "https://example.com" → "https://example.com"

        Args:
            url: URL to load (string)

        Example:
            >>> webview.load("https://example.com")
            >>> webview.load("example.com")  # Auto-adds https://
        """
        # Ensure URL has a scheme (http:// or https://)
        if not url.startswith(("http://", "https://", "file://")):
            url = "https://" + url

        qurl = QUrl(url)

        if not qurl.isValid():
            logger.error(f"Invalid URL: {url}")
            return

        logger.info(f"Loading URL: {url}")
        self._engine_view.load(qurl)

    def url(self) -> str:
        """Get current URL.

        Returns:
            Current URL as string
        """
        return self._engine_view.url().toString()

    def title(self) -> str:
        """Get current page title.

        Returns:
            Current page title
        """
        return self._engine_view.title()

    def icon(self) -> QIcon:
        """Get current page icon (favicon).

        Returns:
            Current page icon
        """
        return self._engine_view.icon()

    def back(self) -> None:
        """Navigate back in history.

        Educational Note:
            The browser maintains a history stack:
            [google.com] ← [example.com] ← [wikipedia.org] (current)

            Calling back() moves one step backward:
            [google.com] ← [example.com] (current) ← [wikipedia.org]
        """
        if self.can_go_back():
            logger.debug("Navigating back")
            self._engine_view.back()
        else:
            logger.debug("Cannot go back (no history)")

    def forward(self) -> None:
        """Navigate forward in history.

        Educational Note:
            Forward only works after going back:
            1. Visit A → B → C
            2. Go back to B
            3. Now forward() returns to C

            If you visit a new page after back(), forward history is cleared.
        """
        if self.can_go_forward():
            logger.debug("Navigating forward")
            self._engine_view.forward()
        else:
            logger.debug("Cannot go forward (no forward history)")

    def reload(self) -> None:
        """Reload current page.

        Educational Note:
            This re-downloads the page from the server.
            Useful to see updated content or retry after errors.
        """
        logger.debug("Reloading page")
        self._engine_view.reload()

    def stop(self) -> None:
        """Stop loading current page.

        Educational Note:
            Stops any ongoing network requests for the current page.
            Useful for:
            - Slow loading pages
            - Pages stuck loading
            - Saving bandwidth
        """
        logger.debug("Stopping page load")
        self._engine_view.stop()

    def can_go_back(self) -> bool:
        """Check if can navigate back.

        Returns:
            True if there is history to go back to
        """
        return self._engine_view.history().canGoBack()

    def can_go_forward(self) -> bool:
        """Check if can navigate forward.

        Returns:
            True if there is forward history
        """
        return self._engine_view.history().canGoForward()

    def set_zoom_factor(self, factor: float) -> None:
        """Set zoom level.

        Educational Note:
            Zoom factor examples:
            - 0.5 = 50% (smaller text)
            - 1.0 = 100% (normal)
            - 1.5 = 150% (larger text)
            - 2.0 = 200% (very large)

        Args:
            factor: Zoom factor (0.25 to 5.0)
        """
        # Clamp to reasonable range
        factor = max(0.25, min(factor, 5.0))
        logger.debug(f"Setting zoom factor: {factor}")
        self._engine_view.setZoomFactor(factor)

    def zoom_factor(self) -> float:
        """Get current zoom factor.

        Returns:
            Current zoom factor
        """
        return self._engine_view.zoomFactor()

    def run_javascript(self, script: str, callback: Optional[callable] = None) -> None:
        """Execute JavaScript in the page context.

        Educational Note:
            This allows you to run JavaScript code in the loaded web page.
            You can:
            - Manipulate the DOM (change page content)
            - Extract data from the page
            - Interact with page JavaScript
            - Inject custom behavior

            The callback receives the result of the script execution.

        Args:
            script: JavaScript code to execute
            callback: Optional callback to receive result (called with result value)

        Example:
            >>> # Execute without waiting for result
            >>> webview.run_javascript("console.log('Hello from Python!')")

            >>> # Get result via callback
            >>> def handle_title(title):
            ...     print(f"Page title: {title}")
            >>> webview.run_javascript("document.title", handle_title)

            >>> # Modify page content
            >>> webview.run_javascript('''
            ...     document.querySelectorAll('h1').forEach(el => {
            ...         el.style.color = 'red';
            ...     });
            ... ''')
        """
        logger.debug(f"Executing JavaScript: {script[:50]}...")
        if callback:
            self._page.runJavaScript(script, callback)
        else:
            self._page.runJavaScript(script)

    def profile(self) -> "QWebEngineProfile":
        """Get the web engine profile for settings and customization.

        Educational Note:
            The profile controls browser-wide settings:
            - User agent string
            - Cache and storage settings
            - Cookie policies
            - HTTP headers
            - Download handling

            Use this for advanced configuration that applies to all pages
            using this profile.

        Returns:
            QWebEngineProfile instance

        Example:
            >>> # Set custom user agent
            >>> profile = webview.profile()
            >>> profile.setHttpUserAgent("MyBrowser/1.0")

            >>> # Access cookie store
            >>> cookie_store = profile.cookieStore()
            >>> cookie_store.cookieAdded.connect(on_cookie_added)

            >>> # Configure cache
            >>> profile.setHttpCacheType(QWebEngineProfile.DiskHttpCache)
            >>> profile.setCachePath("/var/cache/mybrowser")
        """
        return self._page.profile()

    # ===== Advanced API =====
    # These expose more advanced features for power users

    def page(self) -> WebPage:
        """Get underlying WebPage.

        This is provided for advanced use cases where you need direct
        access to the QWebEnginePage. Most users won't need this.

        Returns:
            The WebPage instance
        """
        return self._page

    def engine_view(self) -> QWebEngineView:
        """Get underlying QWebEngineView.

        This is provided for advanced use cases where you need direct
        access to the QWebEngineView. Most users won't need this.

        Educational Note:
            We hide this by default (clean API), but provide access for
            power users who need Qt's full features.

        Returns:
            The QWebEngineView instance
        """
        return self._engine_view
