"""Title bar component for frameless windows.

Provides a custom title bar with window controls and drag area.
"""

from typing import Optional

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from .window_controls import WindowControls


class TitleBar(QWidget):
    """Custom title bar for frameless windows.

    Includes title text, window controls, and drag-to-move functionality.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._drag_position: Optional[QPoint] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        self.setFixedHeight(30)
        self.setStyleSheet("background-color: #323233; color: #cccccc;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 0, 0)
        layout.setSpacing(0)

        # Title label (will be set by parent window)
        self._title_label = QLabel("ViloCodeWindow")
        self._title_label.setStyleSheet("color: #cccccc; font-size: 13px;")
        layout.addWidget(self._title_label)

        # Stretch to push controls to right
        layout.addStretch(1)

        # Window controls
        self._window_controls = WindowControls(self)
        layout.addWidget(self._window_controls)

    def set_title(self, title: str) -> None:
        """Set the title text."""
        self._title_label.setText(title)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press for window dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = (
                event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse move for window dragging."""
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_position is not None:
            # Move window
            self.window().move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle mouse release."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = None
            event.accept()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """Handle double-click to maximize."""
        if event.button() == Qt.MouseButton.LeftButton:
            window = self.window()
            if window.isMaximized():
                window.showNormal()
            else:
                window.showMaximized()
            event.accept()
