"""
Chrome-style main window for ViloWeb using ChromeTabbedWindow.

Educational Note:
    This module demonstrates how to build a Chrome-style browser window using VFWidgets'
    ChromeTabbedWindow component. Key patterns shown:

    - Using ChromeTabbedWindow as top-level widget (parent=None) for frameless mode
    - Adding custom UI elements (hamburger menu, navigation bar) via corner widgets
    - Managing browser tabs with BrowserTab wrapper pattern
    - Sharing QWebChannel across multiple tabs to avoid crashes
    - Integrating bookmark system with UI and JavaScript bridge
    - Theme integration via ThemedWidget mixin (automatic)

Architecture:
    ChromeMainWindow (this class)
    └── ChromeTabbedWindow (parent class, provides Chrome-style tabs + frameless mode)
        ├── ThemedWidget (mixin, automatic theme integration)
        ├── FramelessWindowBehavior (composition, drag/resize)
        ├── ChromeTabBar (built-in, tab rendering)
        ├── TabContentArea (built-in, page content)
        ├── WindowControls (built-in, min/max/close buttons)
        ├── QToolButton + QMenu (custom, hamburger menu - added by us)
        ├── QWidget (custom, navigation bar - added by us)
        ├── BookmarkManager (custom, bookmark storage)
        ├── ViloWebBridge (custom, QWebChannel bridge)
        ├── QWebChannel (shared, Python↔JavaScript)
        └── List[BrowserTab] (tracking, all open tabs)
"""

from typing import Optional, List
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QToolButton, QMenu, QHBoxLayout, QPushButton
from PySide6.QtGui import QAction

from chrome_tabbed_window import ChromeTabbedWindow
from viloweb.browser.browser_tab import BrowserTab
from viloweb.browser.viloweb_bridge import ViloWebBridge
from viloweb.managers.bookmark_manager import BookmarkManager


class ChromeMainWindow(ChromeTabbedWindow):
    """
    ViloWeb main window using ChromeTabbedWindow for frameless Chrome-style UI.

    Educational Note:
        This class demonstrates the following patterns:

        1. Frameless Window Activation:
           - Pass parent=None to ChromeTabbedWindow.__init__()
           - Automatically activates WindowMode.Frameless
           - Adds drag-to-move, edge-resize, and window controls

        2. Browser Tab Management:
           - Create BrowserTab instances (wrapper around BrowserWidget)
           - Use ChromeTabbedWindow.addTab() (QTabWidget API)
           - Connect signals for title/icon/URL updates
           - Track tabs in self._browser_tabs list

        3. QWebChannel Sharing (CRITICAL):
           - Create ONE QWebChannel instance on first tab
           - Reuse same channel for all subsequent tabs
           - Prevents "double registration" crash from v0.1

        4. UI Extension via Corner Widgets:
           - Add hamburger menu to TopLeftCorner
           - No need for QMenuBar (frameless window)
           - Actions accessible via hamburger menu

        5. Theme Integration (Automatic):
           - ChromeTabbedWindow inherits ThemedWidget mixin
           - No manual theme application needed
           - Dark theme applied by application.py

    Attributes:
        _browser_tabs: List of all open BrowserTab instances
        _bookmark_manager: BookmarkManager for JSON bookmark storage
        _bridge: ViloWebBridge for QWebChannel Python↔JavaScript
        _channel: QWebChannel instance (shared across all tabs)
        _hamburger_menu: QToolButton with QMenu for browser actions
        _nav_bar: QWidget with navigation controls (back/forward/reload/stop/URL)
        _url_bar: QLineEdit for URL entry
        _back_btn, _forward_btn, _reload_btn, _stop_btn: Navigation buttons
        _bookmark_btn: Button to bookmark current page
    """

    # Signals
    status_message = Signal(str)  # Status bar messages (for future use)

    def __init__(self):
        """
        Initialize Chrome-style frameless browser window.

        Educational Note:
            CRITICAL: parent=None is what activates frameless mode!

            When ChromeTabbedWindow detects parent=None, it:
            1. Sets Qt.FramelessWindowHint flag
            2. Creates WindowControls (min/max/close buttons)
            3. Initializes FramelessWindowBehavior (drag/resize)
            4. Routes mouse events for window operations

            This is different from ViloxTerm which uses CustomTitleBar as a
            separate component. ChromeTabbedWindow provides everything in one widget.
        """
        # CRITICAL: parent=None activates frameless mode!
        super().__init__(parent=None)

        # Set window properties
        self.setWindowTitle("ViloWeb")
        self.resize(1280, 800)  # Default size

        # Browser tab tracking
        self._browser_tabs: List[BrowserTab] = []

        # Core components (initialized later)
        self._bookmark_manager: Optional[BookmarkManager] = None
        self._bridge: Optional[ViloWebBridge] = None
        self._channel = None  # QWebChannel (created on first tab)

        # UI components (initialized later)
        self._hamburger_menu: Optional[QToolButton] = None

        # NOTE: No custom navigation controls needed!
        # BrowserWidget (used by BrowserTab) already has:
        # - navbar.url_bar (QLineEdit for URL)
        # - navbar.back_button, forward_button, reload_button, stop_button, home_button
        # We access them via: browser_tab.widget.navbar.back_button etc.

        # Initialize components (Task 2.2)
        self._initialize_components()

        # Setup hamburger menu (Task 2.3)
        self._setup_hamburger_menu()

        # NOTE: Navigation bar is NOT needed!
        # BrowserWidget already includes NavigationBar with URL bar and navigation buttons
        # We should NOT add our own navigation bar - that would duplicate the controls

        # Setup signals (Task 3.3)
        self._setup_signals()

        # Create initial tab (Task 2.5)
        self._on_new_tab_requested()

    # ========================================
    # Component Initialization
    # ========================================

    def _initialize_components(self):
        """
        Initialize core browser components.

        Educational Note:
            This method sets up the non-UI components:
            - BookmarkManager: JSON-based bookmark storage
            - ViloWebBridge: QWebChannel bridge for Python↔JavaScript

            QWebChannel is NOT created here - it's created lazily on first tab
            to avoid "object registered before channel created" warnings.
        """
        # Initialize bookmark manager (JSON storage)
        self._bookmark_manager = BookmarkManager()
        print(f"[INFO] BookmarkManager initialized: {self._bookmark_manager._bookmarks_file}")

        # Initialize QWebChannel bridge
        # Note: Bridge is created but channel is NOT created yet
        # Channel will be created on first tab to avoid registration warnings
        self._bridge = ViloWebBridge(self)
        print("[INFO] ViloWebBridge initialized (channel will be created on first tab)")

        # Connect bridge signals to our methods
        # When JavaScript calls window.viloWeb.bookmark_current_page(),
        # the bridge emits bookmark_requested signal which we handle here
        self._bridge.bookmark_requested.connect(self._add_bookmark)

    def _setup_hamburger_menu(self):
        """
        Create hamburger menu as TopLeftCorner widget.

        Educational Note:
            ChromeTabbedWindow supports corner widgets via setCornerWidget().
            We use TopLeftCorner for the hamburger menu (☰) which provides:
            - File actions (New Tab, Close Tab, Quit)
            - Bookmark actions (Add Bookmark, Show Bookmarks)
            - Help actions (About)

            This replaces QMenuBar from v0.1, which doesn't fit in frameless design.
        """
        # Create hamburger button (☰)
        self._hamburger_menu = QToolButton(self)
        self._hamburger_menu.setText("☰")
        self._hamburger_menu.setPopupMode(QToolButton.InstantPopup)
        self._hamburger_menu.setFixedSize(32, 28)  # Match tab bar height

        # Create menu
        menu = QMenu(self)

        # File section
        new_tab_action = QAction("New Tab", self)
        new_tab_action.setShortcut("Ctrl+T")
        new_tab_action.triggered.connect(self._on_new_tab_requested)
        menu.addAction(new_tab_action)

        close_tab_action = QAction("Close Tab", self)
        close_tab_action.setShortcut("Ctrl+W")
        close_tab_action.triggered.connect(lambda: self.removeTab(self.currentIndex()))
        menu.addAction(close_tab_action)

        menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        menu.addAction(quit_action)

        menu.addSeparator()

        # Bookmarks section
        add_bookmark_action = QAction("Add Bookmark", self)
        add_bookmark_action.setShortcut("Ctrl+D")
        add_bookmark_action.triggered.connect(self._add_bookmark)
        menu.addAction(add_bookmark_action)

        show_bookmarks_action = QAction("Show Bookmarks", self)
        show_bookmarks_action.setShortcut("Ctrl+B")
        show_bookmarks_action.triggered.connect(self._show_bookmarks)
        menu.addAction(show_bookmarks_action)

        menu.addSeparator()

        # Help section
        about_action = QAction("About ViloWeb", self)
        about_action.triggered.connect(self._show_about)
        menu.addAction(about_action)

        # Attach menu to button
        self._hamburger_menu.setMenu(menu)

        # Add hamburger menu as corner widget (top-left)
        # This positions it at the left side of the tab bar, before tabs
        self.setCornerWidget(self._hamburger_menu, Qt.TopLeftCorner)
        print("[INFO] Hamburger menu added as TopLeftCorner widget")

    def _show_about(self):
        """Show About dialog."""
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.about(
            self,
            "About ViloWeb",
            "ViloWeb v0.2.0\n\n"
            "Educational web browser demonstrating:\n"
            "- Chrome-style frameless window\n"
            "- Tab management with ChromeTabbedWindow\n"
            "- QWebChannel Python↔JavaScript bridge\n"
            "- JSON-based bookmark system\n\n"
            "Built with VFWidgets and PySide6.",
        )

    # NOTE: _setup_navigation_bar() removed!
    # BrowserWidget already provides NavigationBar with all controls.
    # No need to create duplicate navigation controls.

    def _setup_signals(self):
        """
        Connect signals between components.

        Educational Note:
            This method wires up all signal-slot connections:
            - Bridge signals → Window methods (bookmark_requested - already done in _initialize_components)
            - Tab bar signals → Tab creation (_on_new_tab_requested - already done via override)
            - Current tab changes → UI updates (_on_current_tab_changed)

            Note: Most signals are already connected:
            - Bridge bookmark_requested → _add_bookmark (done in _initialize_components)
            - New tab button → _on_new_tab_requested (automatic via override)
            - Tab signals → handlers (done per-tab in new_browser_tab)

            We just need to connect the currentChanged signal from ChromeTabbedWindow.
        """
        # Connect currentChanged signal to track tab switches
        # This is emitted by ChromeTabbedWindow (inherited from QTabWidget)
        self.currentChanged.connect(self._on_current_tab_changed)
        print("[INFO] Connected currentChanged signal to _on_current_tab_changed")

    # ========================================
    # Tab Management (Override ChromeTabbedWindow)
    # ========================================

    def _on_new_tab_requested(self):
        """
        Override ChromeTabbedWindow._on_new_tab_requested() to create browser tab.

        Educational Note:
            ChromeTabbedWindow calls this method when:
            - User clicks "+" button
            - User presses Ctrl+T

            Default implementation creates a placeholder QWidget.
            We override to create BrowserTab with full browser functionality.

            This is the key integration point between ChromeTabbedWindow and ViloWeb.
        """
        # Create browser tab with VFWidgets homepage as initial URL
        self.new_browser_tab("https://github.com/viloforge/vfwidgets")

    def new_browser_tab(self, url: str = "about:blank") -> BrowserTab:
        """
        Create new browser tab with QWebChannel integration.

        Educational Note:
            This method demonstrates the complete tab creation flow:

            1. Create BrowserTab (wraps BrowserWidget from vfwidgets-webview)
            2. Setup QWebChannel (create on first tab, reuse on others)
            3. Connect signals (title_changed, icon_changed, url_changed)
            4. Add to ChromeTabbedWindow (via addTab, QTabWidget API)
            5. Navigate to URL
            6. Track in self._browser_tabs

            QWebChannel Sharing Pattern (CRITICAL):
                First tab:  Create channel, register bridge, set on page
                Other tabs: Reuse existing channel, just set on page

                This prevents the "double registration" crash from v0.1.

        Args:
            url: Initial URL to navigate to (default: about:blank)

        Returns:
            The created BrowserTab instance
        """
        # Import WebChannelHelper for QWebChannel setup
        from vfwidgets_webview import WebChannelHelper

        # 1. Create BrowserTab (wraps BrowserWidget)
        browser_tab = BrowserTab(parent=self)
        print(f"[INFO] Created BrowserTab for URL: {url}")

        # 2. Setup QWebChannel (CRITICAL: Share across tabs!)
        if self._channel is None:
            # First tab: Create new channel and register bridge
            print("[INFO] First tab: Creating QWebChannel and registering ViloWebBridge")
            self._channel = WebChannelHelper.setup_channel(
                browser_tab.widget,  # BrowserWidget instance
                self._bridge,  # ViloWebBridge instance
                "viloWeb",  # JavaScript object name
            )
        else:
            # Subsequent tabs: Reuse existing channel
            print(f"[INFO] Tab {len(self._browser_tabs) + 1}: Reusing existing QWebChannel")
            browser_tab.widget.page().setWebChannel(self._channel)

        # 3. Connect signals to update UI when tab state changes
        browser_tab.title_changed.connect(self._on_tab_title_changed)
        browser_tab.icon_changed.connect(self._on_tab_icon_changed)
        browser_tab.url_changed.connect(self._on_tab_url_changed)

        # 4. Add tab to ChromeTabbedWindow (QTabWidget API)
        tab_index = self.addTab(browser_tab.widget, "New Tab")
        print(f"[INFO] Added tab at index {tab_index}")

        # 5. Navigate to URL
        browser_tab.navigate(url)

        # 6. Track tab in our list
        self._browser_tabs.append(browser_tab)

        # 7. Switch to the new tab
        self.setCurrentIndex(tab_index)

        # Note: BrowserWidget's NavigationBar enables itself automatically
        # No manual button enabling needed

        return browser_tab

    # ========================================
    # Signal Handlers
    # ========================================

    def _on_current_tab_changed(self, index: int):
        """
        Handle tab switch - update UI state for new active tab.

        Educational Note:
            When user switches tabs, we need to:
            - Update window title to current page title
            - Update URL bar to current page URL
            - Update navigation button states (back/forward)
            - Update bookmark button state (☆ vs ★)

        Args:
            index: Index of newly activated tab
        """
        if index < 0 or index >= len(self._browser_tabs):
            return

        tab = self._browser_tabs[index]

        # Update window title
        title = tab.title if tab.title else "New Tab"
        self.setWindowTitle(f"{title} - ViloWeb")

        # Note: BrowserWidget's NavigationBar automatically updates its own state
        # No manual button updates needed!

    def _on_tab_title_changed(self, title: str):
        """
        Handle tab title change - update tab label and window title.

        Args:
            title: New page title
        """
        # Find which tab sent this signal
        sender_tab = self.sender()
        if not sender_tab:
            return

        # Find tab index
        for i, browser_tab in enumerate(self._browser_tabs):
            if browser_tab == sender_tab:
                # Update tab label
                display_title = title if title else "New Tab"
                self.setTabText(i, display_title)

                # If this is the current tab, update window title too
                if i == self.currentIndex():
                    self.setWindowTitle(f"{display_title} - ViloWeb")
                break

    def _on_tab_icon_changed(self, icon):
        """
        Handle tab icon change - update tab favicon.

        Args:
            icon: New page icon (QIcon)
        """
        # Find which tab sent this signal
        sender_tab = self.sender()
        if not sender_tab:
            return

        # Find tab index
        for i, browser_tab in enumerate(self._browser_tabs):
            if browser_tab == sender_tab:
                # Update tab icon
                self.setTabIcon(i, icon)
                break

    def _on_tab_url_changed(self, url: str):
        """
        Handle tab URL change - update URL bar and navigation buttons.

        Args:
            url: New page URL
        """
        # Find which tab sent this signal
        sender_tab = self.sender()
        if not sender_tab:
            return

        # Find tab index
        for i, browser_tab in enumerate(self._browser_tabs):
            if browser_tab == sender_tab:
                # BrowserWidget's NavigationBar automatically tracks URL changes
                # No manual updates needed
                break

    # NOTE: Navigation actions removed!
    # BrowserWidget's NavigationBar already handles all navigation.
    # No custom navigation methods needed.

    # ========================================
    # Bookmark Actions
    # ========================================

    def _add_bookmark(self):
        """
        Add current page to bookmarks.

        Educational Note:
            This can be called from:
            - Hamburger menu "Add Bookmark" action
            - Bookmark button (☆) click
            - Keyboard shortcut (Ctrl+D)
            - JavaScript bridge: window.viloWeb.bookmark_current_page()
        """
        tab = self.current_browser_tab()
        if not tab:
            return

        # Get current page info
        title = tab.title if tab.title else "Untitled"
        url = tab.url

        if not url or url == "about:blank":
            print("[INFO] Cannot bookmark about:blank")
            return

        # Add to bookmarks
        success = self._bookmark_manager.add_bookmark(title, url)

        if success:
            print(f"[INFO] Bookmarked: {title} - {url}")
            # Update bookmark button icon
            self._update_bookmark_button()

            # Show feedback to user
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.information(
                self,
                "Bookmark Added",
                f"Added bookmark:\n{title}\n{url}",
            )
        else:
            print(f"[INFO] Bookmark already exists: {url}")
            QMessageBox.information(
                self,
                "Bookmark Exists",
                f"This page is already bookmarked:\n{url}",
            )

    def _show_bookmarks(self):
        """
        Show bookmarks dialog.

        Educational Note:
            Opens a simple dialog showing all bookmarks.
            Clicking a bookmark navigates current tab to that URL.
        """
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QListWidget

        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Bookmarks")
        dialog.resize(600, 400)

        # Create layout
        layout = QVBoxLayout(dialog)

        # Create list widget
        list_widget = QListWidget(dialog)

        # Add bookmarks to list
        bookmarks = self._bookmark_manager.get_all_bookmarks()
        for bookmark in bookmarks:
            title = bookmark.get("title", "Untitled")
            url = bookmark.get("url", "")
            list_widget.addItem(f"{title} - {url}")

        # Connect double-click to navigate
        def on_bookmark_clicked(item):
            # Extract URL from item text (format: "Title - URL")
            text = item.text()
            url = text.split(" - ", 1)[-1] if " - " in text else text

            # Navigate current tab
            tab = self.current_browser_tab()
            if tab:
                tab.navigate(url)

            # Close dialog
            dialog.accept()

        list_widget.itemDoubleClicked.connect(on_bookmark_clicked)
        layout.addWidget(list_widget)

        # Add buttons
        button_layout = QHBoxLayout()

        open_button = QPushButton("Open", dialog)
        open_button.clicked.connect(
            lambda: (
                on_bookmark_clicked(list_widget.currentItem())
                if list_widget.currentItem()
                else None
            )
        )
        button_layout.addWidget(open_button)

        close_button = QPushButton("Close", dialog)
        close_button.clicked.connect(dialog.reject)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

        # Show dialog
        dialog.exec()

    # ========================================
    # Helper Methods
    # ========================================

    def current_browser_tab(self) -> Optional[BrowserTab]:
        """
        Get currently active browser tab.

        Returns:
            Current BrowserTab instance, or None if no tabs
        """
        index = self.currentIndex()
        if index < 0 or index >= len(self._browser_tabs):
            return None
        return self._browser_tabs[index]

    # NOTE: Helper methods for navigation controls removed!
    # BrowserWidget's NavigationBar manages its own button states and URL bar.
    # No custom update methods needed.
