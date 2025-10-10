"""Bookmarks panel for sidebar."""

import logging
from typing import Optional

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QMenu,
    QMessageBox,
)

from ..managers.bookmarks import BookmarkManager

logger = logging.getLogger(__name__)


class BookmarksPanel(QWidget):
    """Bookmarks panel with list view and management.

    Displays all bookmarks in a list view with:
    - Click to open bookmark
    - Context menu for edit/delete
    - Refresh on external changes

    Signals:
        bookmark_clicked(str): Emitted when bookmark is clicked (url)
    """

    # Signals
    bookmark_clicked = Signal(str)  # url

    def __init__(self, bookmark_manager: BookmarkManager, parent: Optional[QWidget] = None):
        """Initialize bookmarks panel.

        Args:
            bookmark_manager: BookmarkManager instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.bookmark_manager = bookmark_manager

        self._setup_ui()
        self._connect_signals()
        self.refresh()

        logger.debug("BookmarksPanel created")

    def _setup_ui(self):
        """Set up UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Bookmarks list
        self.list_widget = QListWidget()
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        layout.addWidget(self.list_widget)

        # Refresh button (for debugging/manual refresh)
        self.refresh_btn = QPushButton("Refresh")
        layout.addWidget(self.refresh_btn)

        # Style the panel
        self.setStyleSheet(
            """
            BookmarksPanel {
                background-color: #252526;
            }
            QListWidget {
                background-color: #252526;
                color: #cccccc;
                border: none;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 3px;
            }
            QListWidget::item:hover {
                background-color: #2a2d2e;
            }
            QListWidget::item:selected {
                background-color: #094771;
                color: #ffffff;
            }
            QPushButton {
                background-color: #0e639c;
                color: #ffffff;
                border: none;
                padding: 8px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #0d5a8f;
            }
        """
        )

    def _connect_signals(self):
        """Connect signals."""
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
        self.refresh_btn.clicked.connect(self.refresh)

    def refresh(self):
        """Refresh bookmarks list from manager."""
        self.list_widget.clear()

        bookmarks = self.bookmark_manager.get_all_bookmarks()

        if not bookmarks:
            # Show placeholder
            item = QListWidgetItem("No bookmarks yet")
            item.setFlags(Qt.ItemFlag.NoItemFlags)  # Not selectable
            self.list_widget.addItem(item)
            return

        for bookmark in bookmarks:
            item = QListWidgetItem(f"📑 {bookmark.title}")
            item.setData(Qt.ItemDataRole.UserRole, bookmark.url)
            item.setToolTip(bookmark.url)
            self.list_widget.addItem(item)

        logger.debug(f"Refreshed bookmarks panel: {len(bookmarks)} bookmarks")

    @Slot(QListWidgetItem)
    def _on_item_double_clicked(self, item: QListWidgetItem):
        """Handle bookmark double-clicked.

        Args:
            item: Clicked list item
        """
        url = item.data(Qt.ItemDataRole.UserRole)
        if url:
            logger.info(f"Bookmark clicked: {url}")
            self.bookmark_clicked.emit(url)

    @Slot(object)
    def _show_context_menu(self, pos):
        """Show context menu for bookmarks.

        Args:
            pos: Position where context menu was requested
        """
        item = self.list_widget.itemAt(pos)
        if not item:
            return

        url = item.data(Qt.ItemDataRole.UserRole)
        if not url:
            return

        menu = QMenu(self)

        # Open action
        open_action = menu.addAction("Open")
        open_action.triggered.connect(lambda: self.bookmark_clicked.emit(url))

        menu.addSeparator()

        # Edit action (future enhancement - for now just show)
        edit_action = menu.addAction("Edit...")
        edit_action.setEnabled(False)  # Not implemented yet

        # Delete action
        delete_action = menu.addAction("Delete")
        delete_action.triggered.connect(lambda: self._delete_bookmark(url))

        menu.exec(self.list_widget.mapToGlobal(pos))

    def _delete_bookmark(self, url: str):
        """Delete a bookmark with confirmation.

        Args:
            url: URL of bookmark to delete
        """
        reply = QMessageBox.question(
            self,
            "Delete Bookmark",
            "Are you sure you want to delete this bookmark?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.bookmark_manager.remove_bookmark(url):
                logger.info(f"Bookmark deleted: {url}")
                self.refresh()
            else:
                logger.error(f"Failed to delete bookmark: {url}")
