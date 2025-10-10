"""ViloWeb main application window."""

import logging
from pathlib import Path

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QKeySequence

from vfwidgets_vilocode_window import ViloCodeWindow

from .browser import BrowserTab
from .managers import BookmarkManager
from .panels import BookmarksPanel, HomePanel

logger = logging.getLogger(__name__)


def create_icon_from_text(text: str, size: int = 24) -> QIcon:
    """Create an icon from Unicode text/emoji.

    Args:
        text: Unicode character or emoji to render
        size: Icon size in pixels

    Returns:
        QIcon with rendered text
    """
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    font = QFont("Segoe UI Symbol", int(size * 0.6))
    painter.setFont(font)
    painter.setPen(QColor("#cccccc"))

    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, text)
    painter.end()

    return QIcon(pixmap)


def get_data_dir() -> Path:
    """Get ViloWeb data directory, create if not exists.

    Returns:
        Path to ~/.viloweb/ directory
    """
    data_dir = Path.home() / ".viloweb"
    data_dir.mkdir(exist_ok=True)
    return data_dir


class ViloWebApp(ViloCodeWindow):
    """Main ViloWeb browser application window.

    This class extends ViloCodeWindow to create a full-featured web browser
    with VS Code-style layout (activity bar, sidebar, main pane).

    Features (Phase 1 MVP):
    - Single browser tab with navigation
    - Bookmark management with persistence
    - Sidebar panels (Home, Bookmarks)
    - Theme integration
    - Keyboard shortcuts
    """

    def __init__(self):
        """Initialize ViloWeb application."""
        super().__init__(enable_default_shortcuts=True)

        self.setWindowTitle("ViloWeb Browser - Phase 1 MVP")
        self.resize(1400, 900)

        logger.info("Initializing ViloWeb Browser")

        # Initialize data managers
        self.bookmark_manager = BookmarkManager(get_data_dir())

        # Current browser tab (Phase 1: single tab only)
        self.browser_tab = None

        # Initialize UI components
        self._setup_browser_tab()
        self._setup_activity_bar()
        self._setup_sidebar_panels()
        self._setup_keyboard_shortcuts()
        self._setup_status_bar()

        logger.info("ViloWeb Browser initialized successfully")

    def _setup_browser_tab(self):
        """Set up browser tab in main pane."""
        # Create browser tab with initial blank page
        self.browser_tab = BrowserTab(parent=self, initial_url="about:blank")

        # Connect browser signals
        self.browser_tab.title_changed.connect(self._on_page_title_changed)
        self.browser_tab.url_changed.connect(self._on_page_url_changed)
        self.browser_tab.loading_progress_changed.connect(self._on_loading_progress)
        self.browser_tab.load_finished.connect(self._on_load_finished)
        self.browser_tab.bookmark_requested.connect(self._on_bookmark_requested)

        # Set as main content
        self.set_main_content(self.browser_tab)

        logger.debug("Browser tab initialized")

    def _setup_activity_bar(self):
        """Set up activity bar with Home and Bookmarks icons."""
        # Add activity items
        self.add_activity_item("home", create_icon_from_text("🏠"), "Home")
        self.add_activity_item("bookmarks", create_icon_from_text("📚"), "Bookmarks")

        # Set home as active by default
        self.set_active_activity_item("home")

        # Connect activity item clicks to show panels
        self.activity_item_clicked.connect(self._on_activity_clicked)

        logger.debug("Activity bar initialized")

    def _setup_sidebar_panels(self):
        """Set up sidebar panels (Home, Bookmarks)."""
        # Home panel (placeholder)
        self.home_panel = HomePanel()
        self.home_panel.site_clicked.connect(self._navigate_to_url)
        self.add_sidebar_panel("home", self.home_panel, "HOME")

        # Bookmarks panel
        self.bookmarks_panel = BookmarksPanel(self.bookmark_manager)
        self.bookmarks_panel.bookmark_clicked.connect(self._navigate_to_url)
        self.add_sidebar_panel("bookmarks", self.bookmarks_panel, "BOOKMARKS")

        # Show home panel by default
        self.show_sidebar_panel("home")

        # Connect panel changes to activity bar
        self.sidebar_panel_changed.connect(self._on_panel_changed)

        logger.debug("Sidebar panels initialized")

    def _setup_keyboard_shortcuts(self):
        """Set up custom keyboard shortcuts for browser actions."""
        # Ctrl+D - Bookmark current page
        self.register_custom_shortcut(
            "bookmark_page",
            QKeySequence("Ctrl+D"),
            self._on_bookmark_requested,
            "Bookmark current page",
        )

        # Ctrl+L - Focus address bar
        self.register_custom_shortcut(
            "focus_address_bar",
            QKeySequence("Ctrl+L"),
            self._focus_address_bar,
            "Focus address bar",
        )

        # Alt+Left - Back
        self.register_custom_shortcut(
            "navigate_back", QKeySequence("Alt+Left"), self.browser_tab.go_back, "Go back"
        )

        # Alt+Right - Forward
        self.register_custom_shortcut(
            "navigate_forward",
            QKeySequence("Alt+Right"),
            self.browser_tab.go_forward,
            "Go forward",
        )

        # F5 / Ctrl+R - Refresh
        self.register_custom_shortcut(
            "refresh_page", QKeySequence("F5"), self.browser_tab.refresh, "Refresh page"
        )

        logger.debug("Keyboard shortcuts registered")

    def _setup_status_bar(self):
        """Set up status bar with initial message."""
        self.set_status_message("ViloWeb Browser ready | Navigate to any URL to get started")

    # Slots for browser signals

    @Slot(str)
    def _on_page_title_changed(self, title: str):
        """Handle page title changed.

        Args:
            title: New page title
        """
        # Update window title with page title
        self.setWindowTitle(f"{title} - ViloWeb Browser")

    @Slot(str)
    def _on_page_url_changed(self, url: str):
        """Handle page URL changed.

        Args:
            url: New URL
        """
        # Could update UI elements based on URL here
        pass

    @Slot(int)
    def _on_loading_progress(self, progress: int):
        """Handle page loading progress.

        Args:
            progress: Loading progress (0-100)
        """
        if progress < 100:
            self.set_status_message(f"Loading... {progress}%")

    @Slot(bool)
    def _on_load_finished(self, ok: bool):
        """Handle page load finished.

        Args:
            ok: Whether load was successful
        """
        if ok:
            url = self.browser_tab.current_url

            # Check if current page is bookmarked
            is_bookmarked = self.bookmark_manager.is_bookmarked(url)
            bookmark_status = "⭐ Bookmarked" if is_bookmarked else ""

            self.set_status_message(f"✓ Page loaded | {url} | {bookmark_status}")
        else:
            self.set_status_message("✗ Failed to load page")

    @Slot(str, str)
    def _on_bookmark_requested(self, url: str = None, title: str = None):
        """Handle bookmark request.

        Args:
            url: URL to bookmark (defaults to current page)
            title: Page title (defaults to current page)
        """
        # Use current page if not specified
        if url is None:
            url = self.browser_tab.current_url
        if title is None:
            title = self.browser_tab.current_title

        # Skip about:blank
        if url == "about:blank":
            self.set_status_message("Cannot bookmark blank page")
            return

        # Check if already bookmarked
        if self.bookmark_manager.is_bookmarked(url):
            # Remove bookmark
            self.bookmark_manager.remove_bookmark(url)
            self.bookmarks_panel.refresh()
            self.set_status_message(f"✓ Bookmark removed: {title}")
            logger.info(f"Bookmark removed: {title} ({url})")
        else:
            # Add bookmark
            self.bookmark_manager.add_bookmark(url=url, title=title)
            self.bookmarks_panel.refresh()
            self.set_status_message(f"✓ Bookmarked: {title}")
            logger.info(f"Bookmark added: {title} ({url})")

    # Slots for UI interaction

    @Slot(str)
    def _on_activity_clicked(self, item_id: str):
        """Handle activity bar item clicks.

        Args:
            item_id: ID of clicked activity item
        """
        self.show_sidebar_panel(item_id)

    @Slot(str)
    def _on_panel_changed(self, panel_id: str):
        """Handle sidebar panel changes.

        Args:
            panel_id: ID of new active panel
        """
        self.set_active_activity_item(panel_id)

    @Slot(str)
    def _navigate_to_url(self, url: str):
        """Navigate browser to URL.

        Args:
            url: URL to navigate to
        """
        self.browser_tab.navigate_to(url)
        logger.info(f"Navigating to: {url}")

    @Slot()
    def _focus_address_bar(self):
        """Focus the URL address bar."""
        self.browser_tab.nav_bar.url_bar.setFocus()
        self.browser_tab.nav_bar.url_bar.selectAll()
        logger.debug("Address bar focused")
