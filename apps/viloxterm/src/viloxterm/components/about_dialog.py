"""About dialog for ViloxTerm."""

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QWidget
from PySide6.QtGui import QFont

from viloxterm.__version__ import (
    __version__,
    __author__,
    __license__,
    __description__,
)


class AboutDialog(QDialog):
    """About dialog displaying ViloxTerm version and information."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize about dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("About ViloxTerm")
        self.setModal(True)
        self.setFixedSize(400, 300)

        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Application name
        name_label = QLabel("ViloxTerm")
        name_font = QFont()
        name_font.setPointSize(24)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)

        # Version
        version_label = QLabel(f"Version {__version__}")
        version_font = QFont()
        version_font.setPointSize(12)
        version_label.setFont(version_font)
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)

        # Description
        description_label = QLabel(__description__)
        description_label.setWordWrap(True)
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(description_label)

        # Spacing
        layout.addStretch()

        # License and author info
        info_label = QLabel(
            f"<br>"
            f"<b>Author:</b> {__author__}<br>"
            f"<b>License:</b> {__license__}<br>"
            f"<br>"
            f"<b>Built with:</b><br>"
            f"• VFWidgets (Theme System, Multisplit, Terminal)<br>"
            f"• PySide6 (Qt for Python)<br>"
            f"• Chrome Tabbed Window"
        )
        info_label.setWordWrap(True)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)

        # Spacing
        layout.addStretch()

        # Close button
        close_button = QPushButton("Close")
        close_button.setDefault(True)
        close_button.clicked.connect(self.accept)
        close_button.setFixedWidth(100)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Apply stylesheet for better appearance
        self.setStyleSheet(
            """
            QDialog {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #e0e0e0;
            }
            QPushButton {
                background-color: #3a3a3a;
                color: #e0e0e0;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border: 1px solid #666666;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
            """
        )
