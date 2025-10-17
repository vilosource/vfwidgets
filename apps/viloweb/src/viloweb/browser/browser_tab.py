"""Browser tab - wraps BrowserWidget with tab-specific features.

Educational Focus:
    This module demonstrates:
    - Tab architecture in modern browsers
    - State management per tab (URL, title, icon)
    - Signal-based communication with parent window
    - Resource management (cleanup on close)

Architecture:
    BrowserTab is a thin wrapper around vfwidgets_webview.BrowserWidget
    that adds tab-specific behavior:
    - Emits signals for title/icon/url changes
    - Provides tab state properties (can_go_back, can_go_forward)
    - Handles cleanup when tab closes
"""

import logging
from typing import Optional

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QIcon
from vfwidgets_webview import BrowserWidget

logger = logging.getLogger(__name__)


class BrowserTab(QObject):
    """Represents a single browser tab.

    Educational Note:
        Modern browsers use a "tab" abstraction that owns:
        - Navigation state (history, current URL)
        - Page metadata (title, icon)
        - Rendering context (the actual web view)

        This class wraps BrowserWidget to add tab-level concerns
        like state tracking and parent window communication.

    Signals:
        title_changed: Emitted when page title changes
        icon_changed: Emitted when page icon (favicon) changes
        url_changed: Emitted when URL changes
        load_progress: Emitted during page load (0-100)

    Example:
        >>> tab = BrowserTab()
        >>> tab.title_changed.connect(lambda title: print(f"Title: {title}"))
        >>> tab.navigate("https://example.com")
    """

    # Tab state signals
    title_changed = Signal(str)  # New page title
    icon_changed = Signal(QIcon)  # New favicon
    url_changed = Signal(str)  # New URL
    load_progress = Signal(int)  # Load progress (0-100)

    def __init__(self, parent: Optional[QObject] = None):
        """Initialize browser tab.

        Args:
            parent: Parent QObject (usually MainWindow)
        """
        super().__init__(parent)

        # Create wrapped browser widget
        self._browser = BrowserWidget()
        logger.debug(f"Created BrowserTab (id: {id(self)})")

        # Connect browser signals to our tab signals
        self._setup_signal_forwarding()

        # Tab state
        self._title = "New Tab"
        self._url = ""
        self._icon = QIcon()

    def _setup_signal_forwarding(self) -> None:
        """Connect browser widget signals to tab signals.

        Educational Note:
            This is the "signal forwarding" pattern. The tab re-emits
            signals from the browser widget, allowing the parent window
            to listen to tab-level events without knowing about the
            internal browser widget.

            Why this pattern?
            - Encapsulation: Parent doesn't need to know about BrowserWidget
            - Flexibility: We can add tab-specific logic before forwarding
            - Consistency: All tab events come from one source (the tab)
        """
        logger.debug("Setting up signal forwarding")

        # Forward title changes
        self._browser.webview.title_changed.connect(self._on_title_changed)

        # Forward icon changes
        self._browser.webview.icon_changed.connect(self._on_icon_changed)

        # Forward URL changes
        self._browser.webview.url_changed.connect(self._on_url_changed)

        # Forward load progress
        self._browser.webview.load_progress.connect(self.load_progress.emit)

    @Slot(str)
    def _on_title_changed(self, title: str) -> None:
        """Handle title change from browser widget.

        Educational Note:
            We cache the title so other code can query it synchronously
            via the .title property without needing to inspect the widget.
        """
        self._title = title or "New Tab"
        logger.debug(f"Tab title changed: {self._title}")
        self.title_changed.emit(self._title)

    @Slot(QIcon)
    def _on_icon_changed(self, icon: QIcon) -> None:
        """Handle icon change from browser widget."""
        self._icon = icon
        logger.debug("Tab icon changed")
        self.icon_changed.emit(self._icon)

    @Slot(str)
    def _on_url_changed(self, url: str) -> None:
        """Handle URL change from browser widget."""
        self._url = url
        logger.debug(f"Tab URL changed: {self._url}")
        self.url_changed.emit(self._url)

    # ===== Public Properties =====

    @property
    def widget(self) -> BrowserWidget:
        """Get the browser widget for display in UI.

        Returns:
            The wrapped BrowserWidget

        Educational Note:
            This exposes the internal widget so it can be added to
            the tab bar's widget area. The parent window needs this
            to display the tab content.
        """
        return self._browser

    @property
    def title(self) -> str:
        """Get current page title.

        Returns:
            Page title or "New Tab"
        """
        return self._title

    @property
    def url(self) -> str:
        """Get current URL.

        Returns:
            Current URL string
        """
        return self._url

    @property
    def icon(self) -> QIcon:
        """Get current page icon (favicon).

        Returns:
            Page icon
        """
        return self._icon

    @property
    def can_go_back(self) -> bool:
        """Check if tab can navigate back.

        Returns:
            True if back navigation is available
        """
        return self._browser.webview.page().history().canGoBack()

    @property
    def can_go_forward(self) -> bool:
        """Check if tab can navigate forward.

        Returns:
            True if forward navigation is available
        """
        return self._browser.webview.page().history().canGoForward()

    # ===== Public Methods =====

    def navigate(self, url: str) -> None:
        """Navigate to URL.

        Args:
            url: URL to navigate to

        Example:
            >>> tab.navigate("https://github.com")
        """
        logger.info(f"Tab navigating to: {url}")
        self._browser.navigate(url)

    def go_back(self) -> None:
        """Navigate back in history."""
        logger.debug("Tab going back")
        self._browser.go_back()

    def go_forward(self) -> None:
        """Navigate forward in history."""
        logger.debug("Tab going forward")
        self._browser.go_forward()

    def reload(self) -> None:
        """Reload current page."""
        logger.debug("Tab reloading")
        self._browser.reload()

    def stop(self) -> None:
        """Stop loading current page."""
        logger.debug("Tab stopping load")
        self._browser.stop()

    def cleanup(self) -> None:
        """Clean up tab resources.

        Educational Note:
            This is called when the tab is closed. It's important to
            properly clean up web views to prevent memory leaks.

            Qt WebEngine pages hold significant resources (JavaScript
            contexts, render processes, etc.) that need proper cleanup.
        """
        logger.info(f"Cleaning up BrowserTab (id: {id(self)})")

        # Clear user scripts to help with cleanup
        self._browser.clear_user_scripts()

        # The browser widget will be deleted by Qt's parent-child system
        # but we log it for educational purposes
        logger.debug("Tab cleanup complete")
