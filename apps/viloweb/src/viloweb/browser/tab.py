"""Browser tab component with QWebEngineView."""

import logging
from typing import Optional

from PySide6.QtCore import Signal, Slot, QUrl
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView

from .navigation import NavigationBar

logger = logging.getLogger(__name__)


class BrowserTab(QWidget):
    """Single browser tab with web view and navigation controls.

    Combines NavigationBar and QWebEngineView into a complete browsing tab.

    Properties:
        current_url: Current page URL
        current_title: Current page title
        loading_progress: Page loading progress (0-100)

    Signals:
        title_changed(str): Emitted when page title changes
        url_changed(str): Emitted when URL changes
        loading_progress_changed(int): Emitted during page load (0-100)
        load_finished(bool): Emitted when page load finishes
        bookmark_requested(str, str): Emitted when user wants to bookmark (url, title)
    """

    # Signals
    title_changed = Signal(str)
    url_changed = Signal(str)
    loading_progress_changed = Signal(int)
    load_finished = Signal(bool)
    bookmark_requested = Signal(str, str)  # url, title

    def __init__(self, parent: Optional[QWidget] = None, initial_url: str = ""):
        """Initialize browser tab.

        Args:
            parent: Parent widget
            initial_url: Initial URL to load (empty for blank page)
        """
        super().__init__(parent)

        self._current_url = initial_url or "about:blank"
        self._current_title = "New Tab"
        self._loading_progress = 0

        self._setup_ui()
        self._connect_signals()

        # Load initial URL if provided
        if initial_url:
            self.navigate_to(initial_url)

        logger.debug(f"BrowserTab created with initial URL: {self._current_url}")

    def _setup_ui(self):
        """Set up UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Navigation bar
        self.nav_bar = NavigationBar(self)
        layout.addWidget(self.nav_bar)

        # Web engine view
        self.web_view = QWebEngineView(self)
        layout.addWidget(self.web_view, stretch=1)

        # Set background color
        self.setStyleSheet(
            """
            BrowserTab {
                background-color: #1e1e1e;
            }
        """
        )

    def _connect_signals(self):
        """Connect signals between components."""
        # Navigation bar signals
        self.nav_bar.navigate_to_url.connect(self.navigate_to)
        self.nav_bar.home_requested.connect(self._on_home_requested)
        self.nav_bar.bookmark_requested.connect(self._on_bookmark_requested)
        self.nav_bar.back_btn.clicked.connect(self.go_back)
        self.nav_bar.forward_btn.clicked.connect(self.go_forward)
        self.nav_bar.refresh_btn.clicked.connect(self.refresh)
        self.nav_bar.stop_btn.clicked.connect(self.stop_loading)

        # Web view signals
        self.web_view.loadProgress.connect(self._on_load_progress)
        self.web_view.loadFinished.connect(self._on_load_finished)
        self.web_view.titleChanged.connect(self._on_title_changed)
        self.web_view.urlChanged.connect(self._on_url_changed)

        # Update navigation buttons when history changes
        page = self.web_view.page()
        page.urlChanged.connect(self._update_navigation_buttons)

    @Slot(str)
    def navigate_to(self, url: str):
        """Navigate to URL.

        Handles URL validation and conversion:
        - Adds http:// if no scheme provided
        - Treats non-URLs as search queries (future enhancement)

        Args:
            url: URL or search query to navigate to
        """
        url = url.strip()

        # Add scheme if missing
        if not url.startswith(("http://", "https://", "file://", "about:")):
            # Check if it looks like a domain (has dots)
            if "." in url and " " not in url:
                url = "http://" + url
            else:
                # Treat as search query (for now, just prefix with http://)
                url = "http://" + url

        logger.info(f"Navigating to: {url}")
        self.web_view.setUrl(QUrl(url))

    def go_back(self):
        """Navigate back in history."""
        if self.web_view.page().history().canGoBack():
            self.web_view.back()
            logger.debug("Navigated back")

    def go_forward(self):
        """Navigate forward in history."""
        if self.web_view.page().history().canGoForward():
            self.web_view.forward()
            logger.debug("Navigated forward")

    def refresh(self):
        """Refresh current page."""
        self.web_view.reload()
        logger.debug("Page refreshed")

    def stop_loading(self):
        """Stop page loading."""
        self.web_view.stop()
        logger.debug("Page loading stopped")

    @Slot()
    def _on_home_requested(self):
        """Handle home button clicked."""
        # For now, navigate to about:blank
        # In future, load from settings
        self.navigate_to("about:blank")

    @Slot()
    def _on_bookmark_requested(self):
        """Handle bookmark button clicked."""
        self.bookmark_requested.emit(self._current_url, self._current_title)

    @Slot(int)
    def _on_load_progress(self, progress: int):
        """Handle page load progress.

        Args:
            progress: Loading progress (0-100)
        """
        self._loading_progress = progress
        self.nav_bar.set_loading_progress(progress)
        self.loading_progress_changed.emit(progress)

    @Slot(bool)
    def _on_load_finished(self, ok: bool):
        """Handle page load finished.

        Args:
            ok: Whether load was successful
        """
        if ok:
            logger.info(f"Page loaded successfully: {self._current_url}")
        else:
            logger.warning(f"Page load failed: {self._current_url}")

        self.load_finished.emit(ok)

    @Slot(str)
    def _on_title_changed(self, title: str):
        """Handle page title changed.

        Args:
            title: New page title
        """
        self._current_title = title or "Untitled"
        logger.debug(f"Title changed: {self._current_title}")
        self.title_changed.emit(self._current_title)

    @Slot(QUrl)
    def _on_url_changed(self, url: QUrl):
        """Handle URL changed.

        Args:
            url: New URL
        """
        url_str = url.toString()
        self._current_url = url_str
        self.nav_bar.set_url(url_str)
        logger.debug(f"URL changed: {url_str}")
        self.url_changed.emit(url_str)
        self._update_navigation_buttons()

    def _update_navigation_buttons(self):
        """Update back/forward button enabled state."""
        history = self.web_view.page().history()
        self.nav_bar.set_can_go_back(history.canGoBack())
        self.nav_bar.set_can_go_forward(history.canGoForward())

    @property
    def current_url(self) -> str:
        """Get current page URL."""
        return self._current_url

    @property
    def current_title(self) -> str:
        """Get current page title."""
        return self._current_title

    @property
    def loading_progress(self) -> int:
        """Get current loading progress (0-100)."""
        return self._loading_progress
