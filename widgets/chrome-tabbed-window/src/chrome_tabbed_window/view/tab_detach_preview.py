"""Floating preview window shown when detaching a tab."""

from typing import Optional

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPainter, QColor, QPen, QIcon, QFont


class TabDetachPreview(QWidget):
    """Floating preview window shown when detaching a tab.

    This widget appears when the user drags a tab vertically beyond the
    detachment threshold, providing visual feedback during the drag operation.

    The preview is a frameless, semi-transparent window that follows the
    cursor and displays the tab's text and icon.
    """

    def __init__(self, tab_text: str, tab_icon: Optional[QIcon] = None) -> None:
        """Initialize the tab detach preview.

        Args:
            tab_text: Text to display in the preview
            tab_icon: Optional icon to display in the preview
        """
        super().__init__(None)  # No parent - top-level window

        # Frameless, stays on top (no translucent background for WSL compatibility)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool  # Don't show in taskbar
        )
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # Disabled for WSL
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)  # Don't steal focus

        # Store tab info
        self._tab_text = tab_text
        self._tab_icon = tab_icon

        # Preview size (larger for better visibility)
        self.setFixedSize(250, 50)

    def paintEvent(self, event) -> None:
        """Draw semi-transparent tab preview.

        Args:
            event: Paint event
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Solid background with bright border (more visible in WSL)
        painter.setBrush(QColor(255, 255, 255, 255))  # 100% opaque white
        painter.setPen(QPen(QColor(0, 120, 215), 3))  # Thick blue border
        painter.drawRoundedRect(self.rect().adjusted(2, 2, -2, -2), 8, 8)

        # Draw icon if present
        x_offset = 10
        if self._tab_icon and not self._tab_icon.isNull():
            icon_rect = self.rect().adjusted(x_offset, 10, x_offset + 20, -10)
            self._tab_icon.paint(painter, icon_rect)
            x_offset += 30

        # Draw tab text
        painter.setPen(QColor(0, 0, 0))
        font = QFont()
        font.setPointSize(10)
        painter.setFont(font)
        text_rect = self.rect().adjusted(x_offset, 0, -10, 0)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter, self._tab_text)

    def update_position(self, global_pos: QPoint) -> None:
        """Update preview position to follow cursor.

        Args:
            global_pos: Global cursor position
        """
        # Offset from cursor (so cursor doesn't cover preview)
        offset_x = 20
        offset_y = 20
        self.move(global_pos.x() + offset_x, global_pos.y() + offset_y)
