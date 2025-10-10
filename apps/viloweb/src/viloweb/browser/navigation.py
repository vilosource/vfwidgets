"""Navigation bar component for browser."""

import logging
from typing import Optional

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QToolButton,
    QLineEdit,
    QProgressBar,
    QLabel,
)

logger = logging.getLogger(__name__)


class NavigationBar(QWidget):
    """Navigation controls and URL address bar.

    Provides:
    - Back/Forward/Refresh/Stop/Home buttons
    - URL address bar with enter to navigate
    - Loading progress indicator
    - HTTPS lock indicator
    - Bookmark button

    Signals:
        navigate_to_url(str): Emitted when user enters a URL
        bookmark_requested(): Emitted when bookmark button clicked
        home_requested(): Emitted when home button clicked
    """

    # Signals
    navigate_to_url = Signal(str)
    bookmark_requested = Signal()
    home_requested = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize navigation bar.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Set up UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Back button
        self.back_btn = QToolButton()
        self.back_btn.setText("←")
        self.back_btn.setToolTip("Back (Alt+Left)")
        self.back_btn.setEnabled(False)
        layout.addWidget(self.back_btn)

        # Forward button
        self.forward_btn = QToolButton()
        self.forward_btn.setText("→")
        self.forward_btn.setToolTip("Forward (Alt+Right)")
        self.forward_btn.setEnabled(False)
        layout.addWidget(self.forward_btn)

        # Refresh button
        self.refresh_btn = QToolButton()
        self.refresh_btn.setText("⟳")
        self.refresh_btn.setToolTip("Refresh (Ctrl+R)")
        layout.addWidget(self.refresh_btn)

        # Stop button (hidden by default)
        self.stop_btn = QToolButton()
        self.stop_btn.setText("")
        self.stop_btn.setToolTip("Stop loading")
        self.stop_btn.setVisible(False)
        layout.addWidget(self.stop_btn)

        # Home button
        self.home_btn = QToolButton()
        self.home_btn.setText("<�")
        self.home_btn.setToolTip("Home")
        layout.addWidget(self.home_btn)

        # HTTPS indicator
        self.https_label = QLabel()
        self.https_label.setFixedWidth(20)
        self.https_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.https_label)

        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL or search...")
        layout.addWidget(self.url_bar, stretch=1)

        # Bookmark button
        self.bookmark_btn = QToolButton()
        self.bookmark_btn.setText("P")
        self.bookmark_btn.setToolTip("Bookmark this page (Ctrl+D)")
        layout.addWidget(self.bookmark_btn)

        # Progress bar (under URL bar, initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(3)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximum(100)

        # Style the navigation bar
        self.setStyleSheet(
            """
            NavigationBar {
                background-color: #252526;
                border-bottom: 1px solid #3c3c3c;
            }
            QToolButton {
                background-color: transparent;
                border: none;
                color: #cccccc;
                font-size: 16px;
                padding: 5px 8px;
                border-radius: 3px;
            }
            QToolButton:hover {
                background-color: #3c3c3c;
            }
            QToolButton:pressed {
                background-color: #4c4c4c;
            }
            QToolButton:disabled {
                color: #666666;
            }
            QLineEdit {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 6px 10px;
                color: #cccccc;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #007acc;
                background-color: #2d2d30;
            }
            QProgressBar {
                border: none;
                background-color: transparent;
            }
            QProgressBar::chunk {
                background-color: #007acc;
            }
            QLabel {
                color: #cccccc;
            }
        """
        )

    def _connect_signals(self):
        """Connect internal signals."""
        self.url_bar.returnPressed.connect(self._on_url_entered)
        self.home_btn.clicked.connect(self.home_requested.emit)
        self.bookmark_btn.clicked.connect(self.bookmark_requested.emit)

    @Slot()
    def _on_url_entered(self):
        """Handle URL entered in address bar."""
        url = self.url_bar.text().strip()
        if url:
            self.navigate_to_url.emit(url)

    def set_url(self, url: str):
        """Set URL in address bar without triggering navigation.

        Args:
            url: URL to display
        """
        self.url_bar.setText(url)
        self._update_https_indicator(url)

    def set_loading_progress(self, progress: int):
        """Set loading progress (0-100).

        Args:
            progress: Loading progress percentage
        """
        if progress < 100:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(progress)
            self.refresh_btn.setVisible(False)
            self.stop_btn.setVisible(True)
        else:
            self.progress_bar.setVisible(False)
            self.refresh_btn.setVisible(True)
            self.stop_btn.setVisible(False)

    def set_can_go_back(self, can_go: bool):
        """Enable/disable back button.

        Args:
            can_go: Whether back navigation is possible
        """
        self.back_btn.setEnabled(can_go)

    def set_can_go_forward(self, can_go: bool):
        """Enable/disable forward button.

        Args:
            can_go: Whether forward navigation is possible
        """
        self.forward_btn.setEnabled(can_go)

    def _update_https_indicator(self, url: str):
        """Update HTTPS lock indicator.

        Args:
            url: Current URL
        """
        if url.startswith("https://"):
            self.https_label.setText("=")
            self.https_label.setToolTip("Secure connection (HTTPS)")
        else:
            self.https_label.setText("")
            self.https_label.setToolTip("")
