"""Complete browser widget with navigation and web view.

This module provides the main BrowserWidget that combines:
- NavigationBar (URL bar + navigation buttons)
- WebView (web content display)

This is the top-level widget most applications will use.

Educational Focus:
    This code demonstrates:
    - Composite pattern (combining multiple widgets)
    - Signal/slot wiring between components
    - Delegation pattern (forwarding calls to child widgets)
    - Building complex widgets from simple components
    - Public API design (hiding implementation details)

Example:
    >>> browser = BrowserWidget()
    >>> browser.navigate("https://example.com")
    >>> browser.show()
"""

import logging
from typing import Optional

from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWebEngineCore import QWebEngineScript
from PySide6.QtWidgets import QVBoxLayout, QWidget

from .navigation_bar import NavigationBar
from .webpage import WebPage
from .webview import WebView

logger = logging.getLogger(__name__)


class BrowserWidget(QWidget):
    """Complete browser widget with navigation and content.

    This is the main widget for embedding a full browser in your application.
    It combines a NavigationBar (URL bar + buttons) with a WebView (web content).

    Educational Note:
        This demonstrates the COMPOSITE PATTERN:
        - BrowserWidget is composed of NavigationBar + WebView
        - It acts as a facade, hiding the complexity
        - Provides a simple API while delegating to child widgets
        - Wires signals between children automatically

        Think of this as a "control panel" (navbar) plus a "screen" (webview).

    Example:
        >>> browser = BrowserWidget()
        >>> browser.navigate("https://example.com")
        >>> browser.load_finished.connect(lambda s: print(f"Loaded: {s}"))
        >>> browser.show()

    Signals:
        load_started: Web page started loading
        load_progress(int): Loading progress (0-100%)
        load_finished(bool): Loading finished (success/failure)
        title_changed(str): Page title changed
        url_changed(str): URL changed
        icon_changed(QIcon): Page icon (favicon) changed

    Public API:
        navigate(url): Load a URL
        back(): Go back in history
        forward(): Go forward in history
        reload(): Reload current page
        stop(): Stop loading
        home(): Go to home page (defaults to example.com)
        get_url(): Get current URL
        get_title(): Get current page title
        focus_url_bar(): Focus the URL bar for typing

    Architecture:
        ┌─────────────────────────────────────────┐
        │           BrowserWidget                 │
        ├─────────────────────────────────────────┤
        │  ┌───────────────────────────────────┐  │
        │  │      NavigationBar                │  │
        │  │  [◄][►][⟲][🏠] https://...       │  │
        │  │  ═══════════════════ 67%          │  │
        │  └───────────────────────────────────┘  │
        │  ┌───────────────────────────────────┐  │
        │  │                                   │  │
        │  │         WebView                   │  │
        │  │     (web page content)            │  │
        │  │                                   │  │
        │  └───────────────────────────────────┘  │
        └─────────────────────────────────────────┘
    """

    # Forward WebView signals (so users don't need to access .webview)
    load_started = Signal()
    load_progress = Signal(int)
    load_finished = Signal(bool)
    title_changed = Signal(str)
    url_changed = Signal(str)
    icon_changed = Signal(QIcon)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        home_url: str = "https://example.com",
    ):
        """Initialize browser widget.

        Educational Note:
            Initialization pattern for composite widgets:
            1. Call super().__init__()
            2. Store configuration (like home_url)
            3. Create child widgets
            4. Setup layout
            5. Wire signals between children
            6. Connect children to our own signals

        Args:
            parent: Parent widget
            home_url: URL to navigate to when home button is clicked
        """
        super().__init__(parent)

        # Configuration
        self._home_url = home_url

        # Create child widgets
        self.navbar = NavigationBar(self)
        self.webview = WebView(self)

        # Setup layout
        self._setup_layout()

        # Wire signals
        self._connect_signals()

        logger.debug(f"BrowserWidget initialized with home_url={home_url}")

    def _setup_layout(self) -> None:
        """Arrange navigation bar and web view vertically.

        Educational Note:
            Simple vertical layout:
            - Navigation bar at top (fixed height)
            - Web view below (expands to fill space)
            - No margins/spacing for seamless look
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # No margins
        layout.setSpacing(0)  # No spacing between navbar and webview

        # Add widgets (top to bottom)
        layout.addWidget(self.navbar)  # Fixed height
        layout.addWidget(self.webview)  # Expands to fill space

        logger.debug("Layout configured")

    def _connect_signals(self) -> None:
        """Wire signals between components.

        Educational Note:
            This is the "glue" that makes the components work together:

            1. Navigation bar → WebView:
               - User clicks back → webview.back()
               - User submits URL → webview.load()
               - etc.

            2. WebView → Navigation bar:
               - URL changes → update URL bar
               - Loading state → show/hide progress
               - History changes → enable/disable back/forward

            3. WebView → BrowserWidget:
               - Forward all signals to our users
               - Users interact with BrowserWidget, not internal components

            This demonstrates DELEGATION and SIGNAL FORWARDING patterns.
        """
        # === Navigation bar → WebView ===
        # User interacts with navbar, we tell webview what to do

        self.navbar.back_clicked.connect(self.webview.back)
        self.navbar.forward_clicked.connect(self.webview.forward)
        self.navbar.reload_clicked.connect(self.webview.reload)
        self.navbar.stop_clicked.connect(self.webview.stop)
        self.navbar.home_clicked.connect(self._on_home_clicked)
        self.navbar.url_submitted.connect(self._on_url_submitted)

        # === WebView → Navigation bar ===
        # WebView state changes, we update navbar

        self.webview.load_started.connect(self._on_load_started)
        self.webview.load_progress.connect(self._on_load_progress)
        self.webview.load_finished.connect(self._on_load_finished)
        self.webview.url_changed.connect(self._on_url_changed)

        # Update back/forward button states when history changes
        # Note: QWebEngineView doesn't have history signals, so we
        # update on URL changes (good enough for MVP)
        self.webview.url_changed.connect(self._update_navigation_buttons)

        # === WebView → BrowserWidget (forward to our users) ===

        self.webview.load_started.connect(self.load_started)
        self.webview.load_progress.connect(self.load_progress)
        self.webview.load_finished.connect(self.load_finished)
        self.webview.title_changed.connect(self.title_changed)
        self.webview.url_changed.connect(self.url_changed)
        self.webview.icon_changed.connect(self.icon_changed)

        logger.debug("Signals connected")

    # ===== Signal Handlers =====
    # These handle communication between navbar and webview

    @Slot()
    def _on_home_clicked(self) -> None:
        """Handle home button click."""
        logger.info(f"Navigating to home: {self._home_url}")
        self.webview.load(self._home_url)

    @Slot(str)
    def _on_url_submitted(self, url: str) -> None:
        """Handle URL submission from navbar.

        Educational Note:
            Users can type:
            - Full URL: https://example.com
            - Domain: example.com (we'll add https://)
            - Search query: "how to make pizza" (future feature)

            For MVP, we just load the URL.
        """
        logger.info(f"User submitted URL: {url}")
        self.webview.load(url)

    @Slot()
    def _on_load_started(self) -> None:
        """Handle load started event."""
        logger.debug("Load started")
        self.navbar.set_loading(True)
        self.navbar.set_progress(0)

    @Slot(int)
    def _on_load_progress(self, progress: int) -> None:
        """Handle load progress update."""
        logger.debug(f"Load progress: {progress}%")
        self.navbar.set_progress(progress)

    @Slot(bool)
    def _on_load_finished(self, success: bool) -> None:
        """Handle load finished event."""
        logger.info(f"Load finished: {'success' if success else 'failed'}")
        self.navbar.set_loading(False)
        self.navbar.set_progress(100)

        # Update navigation buttons
        self._update_navigation_buttons()

    @Slot(str)
    def _on_url_changed(self, url: str) -> None:
        """Handle URL change (update navbar)."""
        logger.debug(f"URL changed: {url}")
        self.navbar.set_url(url)

    @Slot()
    def _update_navigation_buttons(self) -> None:
        """Update back/forward button enabled state.

        Educational Note:
            We check the webview's history to see if back/forward
            navigation is possible, then enable/disable buttons accordingly.
        """
        can_back = self.webview.can_go_back()
        can_forward = self.webview.can_go_forward()

        self.navbar.set_back_enabled(can_back)
        self.navbar.set_forward_enabled(can_forward)

        logger.debug(f"Navigation buttons updated: back={can_back}, forward={can_forward}")

    # ===== Public API =====
    # These methods are what users of BrowserWidget will call

    def navigate(self, url: str) -> None:
        """Navigate to a URL.

        This is the primary method for loading web pages.

        Args:
            url: URL to load (can be just domain like "example.com")

        Example:
            >>> browser.navigate("https://example.com")
            >>> browser.navigate("example.com")  # https:// added automatically
        """
        logger.info(f"Navigate called: {url}")
        self.webview.load(url)

    def back(self) -> None:
        """Go back in history.

        Educational Note:
            This delegates to webview.back()
            The webview will handle checking if back is possible.
        """
        logger.info("Back navigation requested")
        self.webview.back()

    def forward(self) -> None:
        """Go forward in history."""
        logger.info("Forward navigation requested")
        self.webview.forward()

    def reload(self) -> None:
        """Reload current page."""
        logger.info("Reload requested")
        self.webview.reload()

    def stop(self) -> None:
        """Stop loading current page."""
        logger.info("Stop loading requested")
        self.webview.stop()

    def home(self) -> None:
        """Navigate to home page."""
        logger.info(f"Home navigation requested: {self._home_url}")
        self.webview.load(self._home_url)

    def get_url(self) -> str:
        """Get current URL.

        Returns:
            Current URL as string
        """
        return self.webview.url()

    def get_title(self) -> str:
        """Get current page title.

        Returns:
            Current page title
        """
        return self.webview.title()

    def focus_url_bar(self) -> None:
        """Focus the URL bar for typing.

        Educational Note:
            This is useful for implementing keyboard shortcuts like Ctrl+L.
            The navbar handles the actual focusing and text selection.
        """
        logger.debug("Focusing URL bar")
        self.navbar.focus_url_bar()

    def set_home_url(self, url: str) -> None:
        """Set the home page URL.

        Args:
            url: URL to use as home page
        """
        logger.info(f"Home URL changed: {self._home_url} → {url}")
        self._home_url = url

    # ===== Advanced API (Phase 1 Extensions) =====

    def run_javascript(self, script: str, callback: Optional[callable] = None) -> None:
        """Execute JavaScript in the page context.

        This is a convenience method that delegates to the underlying WebView.
        Use this to manipulate page content, extract data, or inject custom behavior.

        Args:
            script: JavaScript code to execute
            callback: Optional callback to receive result

        Example:
            >>> # Change all h1 elements to red
            >>> browser.run_javascript('''
            ...     document.querySelectorAll('h1').forEach(el => {
            ...         el.style.color = 'red';
            ...     });
            ... ''')

            >>> # Get page metadata
            >>> def show_title(title):
            ...     print(f"Title: {title}")
            >>> browser.run_javascript("document.title", show_title)
        """
        logger.debug("Delegating JavaScript execution to webview")
        self.webview.run_javascript(script, callback)

    def page(self) -> WebPage:
        """Get the QWebEnginePage for advanced configuration.

        Use this when you need:
        - QWebChannel setup for Python↔JavaScript bridge
        - Advanced JavaScript execution control
        - Page lifecycle hooks
        - Custom page behavior

        Returns:
            The underlying WebPage instance

        Example:
            >>> # Setup QWebChannel for extension communication
            >>> from PySide6.QtWebChannel import QWebChannel
            >>> channel = QWebChannel()
            >>> bridge = MyBridge()
            >>> channel.registerObject("pyBridge", bridge)
            >>> browser.page().setWebChannel(channel)
        """
        return self.webview.page()

    def profile(self) -> "QWebEngineProfile":  # noqa: F821
        """Get the QWebEngineProfile for browser-wide settings.

        Use this when you need:
        - Custom user agent configuration
        - Cache and cookie management
        - Storage settings
        - Download handling

        Returns:
            QWebEngineProfile instance

        Example:
            >>> # Configure cache
            >>> profile = browser.profile()
            >>> profile.setHttpCacheType(QWebEngineProfile.DiskHttpCache)
            >>> profile.setCachePath("/var/cache/mybrowser")

            >>> # Access cookie store
            >>> cookie_store = profile.cookieStore()
            >>> cookie_store.cookieAdded.connect(on_cookie)
        """
        return self.webview.profile()

    def settings(self) -> "QWebEngineSettings":  # noqa: F821
        """Get page settings for feature configuration.

        Use this to enable/disable browser features like JavaScript,
        images, plugins, etc.

        Returns:
            QWebEngineSettings instance

        Example:
            >>> # Configure JavaScript
            >>> from PySide6.QtWebEngineCore import QWebEngineSettings
            >>> settings = browser.settings()
            >>> settings.setAttribute(
            ...     QWebEngineSettings.WebAttribute.JavascriptEnabled,
            ...     True
            ... )
        """
        return self.webview.page().settings()

    def set_user_agent(self, user_agent: str) -> None:
        """Set custom user agent string.

        This is a convenience method for the common task of setting
        a custom user agent.

        Args:
            user_agent: User agent string to identify browser

        Example:
            >>> browser.set_user_agent("ViloWeb/1.0 Educational Browser")
        """
        logger.info(f"Setting user agent: {user_agent}")
        self.profile().setHttpUserAgent(user_agent)

    # ===== User Script Injection API =====

    def inject_user_script(
        self,
        source_code: str,
        name: str = "user-script",
        injection_point: QWebEngineScript.InjectionPoint = (
            QWebEngineScript.InjectionPoint.DocumentCreation
        ),
        world_id: QWebEngineScript.ScriptWorldId = QWebEngineScript.ScriptWorldId.MainWorld,
        runs_on_subframes: bool = True,
    ) -> None:
        """Inject JavaScript that runs on every page load (CSP-safe).

        This is a convenience method that delegates to the underlying WebView.
        See WebView.inject_user_script() for full documentation.

        Args:
            source_code: JavaScript code to inject
            name: Script identifier (used for removal/management)
            injection_point: When to inject (DocumentCreation recommended)
            world_id: JavaScript world (MainWorld for DOM access)
            runs_on_subframes: Whether to inject in iframes too

        Example:
            >>> # Setup QWebChannel for extensions
            >>> browser.inject_user_script(qwebchannel_init, name="qwebchannel")
        """
        logger.debug("Delegating user script injection to webview")
        self.webview.inject_user_script(
            source_code, name, injection_point, world_id, runs_on_subframes
        )

    def remove_user_script(self, name: str) -> bool:
        """Remove a previously injected user script.

        Args:
            name: Script identifier

        Returns:
            True if script was found and removed

        Example:
            >>> browser.inject_user_script("test", name="test-script")
            >>> browser.remove_user_script("test-script")  # Returns True
        """
        return self.webview.remove_user_script(name)

    def clear_user_scripts(self) -> None:
        """Remove all user scripts.

        Example:
            >>> browser.clear_user_scripts()
        """
        self.webview.clear_user_scripts()
