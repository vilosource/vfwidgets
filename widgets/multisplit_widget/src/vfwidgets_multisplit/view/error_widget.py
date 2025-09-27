"""Error display widget for MultiSplit.

Shows error states when operations fail.
"""

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QPalette
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout, QWidget


class ErrorWidget(QWidget):
    """Widget to display error states."""

    # Signals
    retry_clicked = Signal()

    def __init__(self, error_message: str = "An error occurred",
                 parent: QWidget = None):
        """Initialize error widget.

        Args:
            error_message: Message to display
            parent: Parent widget
        """
        super().__init__(parent)

        self.setup_ui(error_message)

    def setup_ui(self, message: str):
        """Set up the error UI."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Error icon
        icon_label = QLabel("⚠️")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        font = QFont()
        font.setPointSize(32)
        icon_label.setFont(font)

        # Error message
        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setWordWrap(True)

        # Style with error colors
        message_label.setStyleSheet("""
            QLabel {
                color: #d32f2f;
                padding: 10px;
                font-size: 14px;
            }
        """)

        # Retry button (optional)
        retry_button = QPushButton("Retry")
        retry_button.clicked.connect(self.retry_clicked.emit)
        retry_button.setMaximumWidth(100)

        # Add to layout
        layout.addWidget(icon_label)
        layout.addWidget(message_label)
        layout.addWidget(retry_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Set background
        self.setStyleSheet("""
            ErrorWidget {
                background-color: #ffebee;
                border: 1px solid #ffcdd2;
                border-radius: 4px;
            }
        """)

    def set_error(self, message: str):
        """Update error message.

        Args:
            message: New error message
        """
        # Find message label and update
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, QLabel) and widget.text() != "⚠️":
                widget.setText(message)
                break


class ValidationOverlay(QWidget):
    """Overlay to show validation errors."""

    def __init__(self, parent: QWidget = None):
        """Initialize validation overlay."""
        super().__init__(parent)

        self.setAutoFillBackground(True)

        # Semi-transparent background
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window,
                        Qt.GlobalColor.transparent)
        self.setPalette(palette)

        # Layout for messages
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop |
                                Qt.AlignmentFlag.AlignRight)

        self.messages = []

    def show_validation_error(self, message: str, duration: int = 3000):
        """Show validation error message.

        Args:
            message: Error message to show
            duration: How long to show (ms)
        """
        # Create message frame
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #f44336;
                color: white;
                padding: 8px 12px;
                border-radius: 4px;
                margin: 4px;
            }
        """)

        label = QLabel(message)
        label.setStyleSheet("color: white;")

        frame_layout = QVBoxLayout(frame)
        frame_layout.addWidget(label)
        frame_layout.setContentsMargins(8, 4, 8, 4)

        self.layout.addWidget(frame)
        self.messages.append(frame)

        # Auto-hide after duration
        QTimer.singleShot(duration, lambda: self.hide_message(frame))

    def hide_message(self, frame: QWidget):
        """Hide and remove message frame."""
        if frame in self.messages:
            self.messages.remove(frame)
            frame.deleteLater()
