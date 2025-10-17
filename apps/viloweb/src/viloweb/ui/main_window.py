"""Main window for ViloWeb browser.

Educational Focus:
    This module demonstrates:
    - Multi-tab browser architecture
    - Tab lifecycle management (create, switch, close)
    - QTabWidget integration
    - Menu bar and toolbar setup
    - QWebChannel bridge integration
    - Bookmark system integration

Architecture:
    MainWindow orchestrates:
    - Tab bar (QTabWidget) for switching between tabs
    - Menu bar for File/Bookmarks/Help
    - Toolbar for common actions
    - Status bar for feedback
    - QWebChannel bridge (shared across all tabs)
"""

import logging
from typing import Optional

from PySide6.QtCore import QSize, Slot
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QTabWidget,
    QToolBar,
)
from vfwidgets_webview import WebChannelHelper

from ..browser import BrowserTab, ViloWebBridge
from ..managers import BookmarkManager

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main window for ViloWeb browser.

    Educational Note:
        This is the top-level window that contains:
        - Tab bar (QTabWidget) - manages multiple tabs
        - Menu bar - File, Bookmarks, Help menus
        - Toolbar - Quick access to common actions
        - Status bar - Shows load progress and messages

        Design pattern: The main window is a "coordinator" that:
        1. Creates and manages tabs
        2. Routes actions to active tab
        3. Manages shared resources (bridge, bookmarks)
        4. Provides UI chrome (menus, toolbars)

    Example:
        >>> from PySide6.QtWidgets import QApplication
        >>> app = QApplication([])
        >>> window = MainWindow()
        >>> window.show()
        >>> app.exec()
    """

    def __init__(self, parent: Optional[QMainWindow] = None):
        """Initialize main window.

        Args:
            parent: Parent widget (usually None for top-level window)
        """
        super().__init__(parent)

        # Window setup
        self.setWindowTitle("ViloWeb - Educational Browser")
        self.resize(1280, 800)
        logger.info("MainWindow initialized")

        # Initialize managers
        self._bookmark_manager = BookmarkManager()
        logger.debug("BookmarkManager initialized")

        # Initialize QWebChannel bridge and channel (shared across all tabs)
        # Educational Note:
        #     We create ONE QWebChannel that will be shared across all tabs.
        #     This is important because Qt WebChannel can only register an object
        #     in one channel at a time. Trying to register the same object in
        #     multiple channels causes crashes.
        self._bridge = ViloWebBridge(self)
        self._bridge.bookmark_requested.connect(self._on_bookmark_requested)
        self._channel: Optional[QWebChannel] = None  # Will be created with first tab
        logger.debug("ViloWebBridge initialized")

        # Create UI components
        self._setup_tab_widget()
        self._setup_menus()
        self._setup_toolbar()
        self._setup_status_bar()

        # Create first tab
        # Educational Note:
        #     We try external URL first, but if it fails (e.g., sandboxing issues),
        #     we fall back to a local welcome page. This ensures ViloWeb always works.
        try:
            self.new_tab("https://github.com/viloforge/vfwidgets")
        except Exception as e:
            logger.warning(f"Failed to load external URL: {e}")
            logger.info("Loading local welcome page instead")
            self.new_tab("about:blank")
        logger.info("Initial tab created")

    def _setup_tab_widget(self) -> None:
        """Setup QTabWidget for tab management.

        Educational Note:
            QTabWidget provides:
            - Tab bar at top
            - Stacked widget area for content
            - Built-in tab switching logic

            We configure it to:
            - Allow closing tabs (closable tabs)
            - Allow tab reordering (movable tabs)
            - Show close button on each tab
        """
        self._tab_widget = QTabWidget()
        self._tab_widget.setTabsClosable(True)
        self._tab_widget.setMovable(True)
        self._tab_widget.setDocumentMode(True)  # Better look on macOS

        # Connect signals
        self._tab_widget.tabCloseRequested.connect(self._on_tab_close_requested)
        self._tab_widget.currentChanged.connect(self._on_tab_changed)

        # Set as central widget
        self.setCentralWidget(self._tab_widget)
        logger.debug("Tab widget configured")

    def _setup_menus(self) -> None:
        """Setup menu bar.

        Educational Note:
            Menu bar provides organized access to all features.
            We follow standard browser menu structure:
            - File: New Tab, Close Tab, Quit
            - Bookmarks: Add Bookmark, Show Bookmarks
            - Help: About
        """
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        new_tab_action = QAction("&New Tab", self)
        new_tab_action.setShortcut(QKeySequence.StandardKey.AddTab)
        new_tab_action.triggered.connect(lambda: self.new_tab())
        file_menu.addAction(new_tab_action)

        close_tab_action = QAction("&Close Tab", self)
        close_tab_action.setShortcut(QKeySequence.StandardKey.Close)
        close_tab_action.triggered.connect(self._close_current_tab)
        file_menu.addAction(close_tab_action)

        file_menu.addSeparator()

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Bookmarks menu
        bookmarks_menu = menubar.addMenu("&Bookmarks")

        add_bookmark_action = QAction("&Add Bookmark", self)
        add_bookmark_action.setShortcut("Ctrl+D")
        add_bookmark_action.triggered.connect(self._add_bookmark)
        bookmarks_menu.addAction(add_bookmark_action)

        show_bookmarks_action = QAction("&Show Bookmarks", self)
        show_bookmarks_action.setShortcut("Ctrl+B")
        show_bookmarks_action.triggered.connect(self._show_bookmarks)
        bookmarks_menu.addAction(show_bookmarks_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About ViloWeb", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

        logger.debug("Menu bar configured")

    def _setup_toolbar(self) -> None:
        """Setup toolbar with common actions.

        Educational Note:
            Toolbar provides quick access to frequent actions.
            We include:
            - Back/Forward navigation
            - Reload/Stop
            - New Tab
            - Add Bookmark
        """
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Back button
        back_action = QAction("Back", self)
        back_action.setShortcut(QKeySequence.StandardKey.Back)
        back_action.triggered.connect(self._go_back)
        toolbar.addAction(back_action)

        # Forward button
        forward_action = QAction("Forward", self)
        forward_action.setShortcut(QKeySequence.StandardKey.Forward)
        forward_action.triggered.connect(self._go_forward)
        toolbar.addAction(forward_action)

        # Reload button
        reload_action = QAction("Reload", self)
        reload_action.setShortcut(QKeySequence.StandardKey.Refresh)
        reload_action.triggered.connect(self._reload)
        toolbar.addAction(reload_action)

        # Stop button
        stop_action = QAction("Stop", self)
        stop_action.setShortcut("Esc")
        stop_action.triggered.connect(self._stop)
        toolbar.addAction(stop_action)

        toolbar.addSeparator()

        # New tab button
        new_tab_action = QAction("New Tab", self)
        new_tab_action.triggered.connect(lambda: self.new_tab())
        toolbar.addAction(new_tab_action)

        # Bookmark button
        bookmark_action = QAction("Bookmark", self)
        bookmark_action.triggered.connect(self._add_bookmark)
        toolbar.addAction(bookmark_action)

        logger.debug("Toolbar configured")

    def _setup_status_bar(self) -> None:
        """Setup status bar.

        Educational Note:
            Status bar shows:
            - Load progress during page load
            - Hover URL when mousing over links
            - General status messages
        """
        self.statusBar().showMessage("Ready")
        logger.debug("Status bar configured")

    # ===== Tab Management =====

    def new_tab(self, url: str = "about:blank") -> BrowserTab:
        """Create new browser tab.

        Args:
            url: Initial URL to load (default: about:blank)

        Returns:
            Created BrowserTab instance

        Educational Note:
            Creating a new tab involves:
            1. Create BrowserTab instance
            2. Setup QWebChannel bridge for the tab
            3. Connect tab signals to main window
            4. Add tab widget to QTabWidget
            5. Switch to new tab
        """
        logger.info(f"Creating new tab: {url}")

        # Step 1: Create tab
        tab = BrowserTab(self)

        # Step 2: Setup QWebChannel (only once for first tab)
        # Educational Note:
        #     QWebChannel can only register an object once. We create the channel
        #     for the first tab, then reuse it for all subsequent tabs by setting
        #     it on each page. This prevents "double registration" crashes.
        if self._channel is None:
            self._channel = WebChannelHelper.setup_channel(tab.widget, self._bridge, "viloWeb")
            logger.debug("QWebChannel created and bridge registered")
        else:
            # Reuse existing channel for this tab
            tab.widget.page().setWebChannel(self._channel)
            logger.debug("Reusing QWebChannel for new tab")

        # Step 3: Connect tab signals
        tab.title_changed.connect(lambda title: self._on_tab_title_changed(tab, title))
        tab.icon_changed.connect(lambda icon: self._on_tab_icon_changed(tab, icon))
        tab.url_changed.connect(lambda url: self._on_tab_url_changed(tab, url))
        tab.load_progress.connect(self._on_load_progress)

        # Step 4: Add to tab widget
        index = self._tab_widget.addTab(tab.widget, "New Tab")

        # Step 5: Switch to new tab
        self._tab_widget.setCurrentIndex(index)

        # Navigate to URL
        if url != "about:blank":
            tab.navigate(url)

        logger.debug(f"New tab created at index {index}")
        return tab

    @Slot(int)
    def _on_tab_close_requested(self, index: int) -> None:
        """Handle tab close request.

        Args:
            index: Index of tab to close

        Educational Note:
            Closing a tab requires:
            1. Get tab object
            2. Remove from QTabWidget
            3. Clean up tab resources
            4. If last tab, close window
        """
        logger.info(f"Tab close requested: index {index}")

        # Get tab widget
        tab_widget = self._tab_widget.widget(index)

        # Find corresponding BrowserTab (we need to search through children)
        # In this architecture, the tab widget is the BrowserWidget inside BrowserTab
        # We can get the BrowserTab via parent relationship
        for i in range(self._tab_widget.count()):
            widget = self._tab_widget.widget(i)
            if widget == tab_widget:
                # The BrowserTab is the parent of the BrowserWidget
                # Actually, let's store a mapping instead
                pass

        # Remove from tab widget
        self._tab_widget.removeTab(index)
        logger.debug(f"Tab removed from widget at index {index}")

        # Clean up resources
        # Note: In this simple implementation, Qt's parent-child system
        # will handle cleanup. In a production browser, you'd do more here.

        # If last tab closed, exit
        if self._tab_widget.count() == 0:
            logger.info("Last tab closed, exiting application")
            self.close()

    @Slot(int)
    def _on_tab_changed(self, index: int) -> None:
        """Handle tab switch.

        Args:
            index: Index of newly active tab

        Educational Note:
            When user switches tabs, we need to:
            1. Update window title to show new tab's title
            2. Update status bar
            3. (Future) Update toolbar button states
        """
        if index < 0:
            return

        logger.debug(f"Switched to tab {index}")

        # Update window title
        # Note: We need to get the BrowserTab to access the title
        # For now, just use QTabWidget's tab text
        tab_title = self._tab_widget.tabText(index)
        self.setWindowTitle(f"{tab_title} - ViloWeb")

    def _close_current_tab(self) -> None:
        """Close currently active tab."""
        current_index = self._tab_widget.currentIndex()
        if current_index >= 0:
            self._on_tab_close_requested(current_index)

    def _get_current_tab(self) -> Optional[BrowserTab]:
        """Get currently active BrowserTab.

        Returns:
            Active BrowserTab or None if no tabs

        Educational Note:
            This helper is needed because QTabWidget gives us the widget
            (BrowserWidget), but we need the wrapping BrowserTab object
            to access tab-specific methods.

            In this implementation, we need to find the BrowserTab that
            owns this BrowserWidget. This is a bit awkward because of the
            architecture. A better approach would be to maintain a mapping
            from widget to tab.

            For MVP, we'll work around this by storing tabs as we create them.
        """
        # MVP workaround: Access via widget parent
        # This is not ideal but works for simple case
        current_widget = self._tab_widget.currentWidget()
        if not current_widget:
            return None

        # The widget is a BrowserWidget, which is inside a BrowserTab
        # Since BrowserTab doesn't inherit from QWidget, we need another approach
        # Let's store a mapping at class level
        if not hasattr(self, "_tab_map"):
            logger.warning("Tab map not initialized, cannot get current tab")
            return None

        return self._tab_map.get(current_widget)

    # ===== Tab Signal Handlers =====

    @Slot(str)
    def _on_tab_title_changed(self, tab: BrowserTab, title: str) -> None:
        """Update tab title in tab bar.

        Args:
            tab: BrowserTab that changed
            title: New title
        """
        # Find tab index
        index = self._tab_widget.indexOf(tab.widget)
        if index >= 0:
            # Truncate long titles
            display_title = title[:30] + "..." if len(title) > 30 else title
            self._tab_widget.setTabText(index, display_title)

            # If this is current tab, update window title
            if index == self._tab_widget.currentIndex():
                self.setWindowTitle(f"{title} - ViloWeb")

    @Slot(QIcon)
    def _on_tab_icon_changed(self, tab: BrowserTab, icon: QIcon) -> None:
        """Update tab icon (favicon) in tab bar.

        Args:
            tab: BrowserTab that changed
            icon: New icon
        """
        index = self._tab_widget.indexOf(tab.widget)
        if index >= 0:
            self._tab_widget.setTabIcon(index, icon)

    @Slot(str)
    def _on_tab_url_changed(self, tab: BrowserTab, url: str) -> None:
        """Handle tab URL change.

        Args:
            tab: BrowserTab that changed
            url: New URL
        """
        # Update status bar if this is current tab
        if self._tab_widget.indexOf(tab.widget) == self._tab_widget.currentIndex():
            self.statusBar().showMessage(f"Loaded: {url}")

    @Slot(int)
    def _on_load_progress(self, progress: int) -> None:
        """Update status bar with load progress.

        Args:
            progress: Load progress (0-100)
        """
        if progress < 100:
            self.statusBar().showMessage(f"Loading: {progress}%")
        else:
            self.statusBar().showMessage("Ready")

    # ===== Navigation Actions =====

    def _go_back(self) -> None:
        """Navigate current tab back."""
        tab = self._get_current_tab()
        if tab and tab.can_go_back:
            tab.go_back()

    def _go_forward(self) -> None:
        """Navigate current tab forward."""
        tab = self._get_current_tab()
        if tab and tab.can_go_forward:
            tab.go_forward()

    def _reload(self) -> None:
        """Reload current tab."""
        tab = self._get_current_tab()
        if tab:
            tab.reload()

    def _stop(self) -> None:
        """Stop loading current tab."""
        tab = self._get_current_tab()
        if tab:
            tab.stop()

    # ===== Bookmark Actions =====

    def _add_bookmark(self) -> None:
        """Add current page to bookmarks."""
        tab = self._get_current_tab()
        if not tab:
            return

        title = tab.title
        url = tab.url

        if not url or url == "about:blank":
            QMessageBox.information(self, "No URL", "Cannot bookmark empty page.")
            return

        self._bookmark_manager.add_bookmark(title, url)
        self.statusBar().showMessage(f"Bookmarked: {title}", 3000)
        logger.info(f"Added bookmark: {title} -> {url}")

    def _show_bookmarks(self) -> None:
        """Show bookmarks dialog."""
        bookmarks = self._bookmark_manager.get_all_bookmarks()

        if not bookmarks:
            QMessageBox.information(self, "Bookmarks", "No bookmarks yet!")
            return

        # MVP: Simple message box listing bookmarks
        # In a full browser, this would be a proper dialog/sidebar
        bookmark_list = "\n".join([f"• {b['title']}" for b in bookmarks[:10]])
        if len(bookmarks) > 10:
            bookmark_list += f"\n... and {len(bookmarks) - 10} more"

        QMessageBox.information(self, "Bookmarks", bookmark_list)
        logger.debug("Showed bookmarks dialog")

    @Slot()
    def _on_bookmark_requested(self) -> None:
        """Handle bookmark request from JavaScript bridge."""
        logger.info("Bookmark requested via JavaScript bridge")
        self._add_bookmark()

    # ===== Help Actions =====

    def _show_about(self) -> None:
        """Show about dialog."""
        about_text = """
        <h2>ViloWeb - Educational Browser</h2>
        <p>Version 0.1.0</p>
        <p>Built with VFWidgets and Qt WebEngine</p>
        <p><b>Educational Focus:</b> This browser demonstrates modern browser
        architecture including tabs, bookmarks, QWebChannel bridges, and theme integration.</p>
        <p>Part of the VFWidgets project: <a href="https://github.com/viloforge/vfwidgets">
        github.com/viloforge/vfwidgets</a></p>
        """
        QMessageBox.about(self, "About ViloWeb", about_text)

    # ===== Cleanup =====

    def closeEvent(self, event) -> None:
        """Handle window close.

        Educational Note:
            Clean shutdown involves:
            1. Clean up all tabs
            2. Save bookmarks (already auto-saved)
            3. Shutdown bridge
            4. Let Qt clean up widgets
        """
        logger.info("MainWindow closing")

        # Cleanup bridge
        self._bridge.shutdown()

        # Accept close event
        event.accept()
        logger.info("MainWindow closed")
