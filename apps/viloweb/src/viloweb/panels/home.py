"""Home panel for sidebar."""

import logging
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

logger = logging.getLogger(__name__)


class HomePanel(QWidget):
    """Home panel with quick links (placeholder for Phase 1).

    Future features (Phase 10):
    - Quick links grid
    - Recently visited sites
    - Most visited sites
    - Customizable tiles

    Signals:
        site_clicked(str): Emitted when quick link is clicked (url)
    """

    # Signals
    site_clicked = Signal(str)  # url

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize home panel.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._setup_ui()
        logger.debug("HomePanel created")

    def _setup_ui(self):
        """Set up UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Placeholder content
        label = QLabel(
            "🏠 Home Panel\n\n"
            "Quick links and recently visited sites\n"
            "will be available in a future update.\n\n"
            "For now, use the address bar to navigate!"
        )
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        layout.addWidget(label, stretch=1)

        # Style the panel
        self.setStyleSheet(
            """
            HomePanel {
                background-color: #252526;
            }
            QLabel {
                color: #cccccc;
                font-size: 14px;
                padding: 20px;
            }
        """
        )
