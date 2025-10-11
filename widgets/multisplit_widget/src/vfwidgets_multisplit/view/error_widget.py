"""Error display widget for MultiSplit.

Shows error states when operations fail.
"""

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QPalette
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout, QWidget

try:
    from vfwidgets_theme.widgets.base import ThemedWidget
    from vfwidgets_theme.widgets.roles import WidgetRole, set_widget_role

    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False
    ThemedWidget = object
    WidgetRole = None


if THEME_AVAILABLE:

    class ErrorWidget(ThemedWidget, QWidget):
        """Widget to display error states with theme integration."""

        # Theme configuration - maps theme tokens to error widget properties
        theme_config = {
            "error_fg": "errorForeground",
            "error_bg": "inputValidation.errorBackground",
            "error_border": "inputValidation.errorBorder",
        }

        # Signals
        retry_clicked = Signal()

        def __init__(self, error_message: str = "An error occurred", parent: QWidget = None):
            """Initialize error widget.

            Args:
                error_message: Message to display
                parent: Parent widget
            """
            super().__init__(parent=parent)

            self._message_label = None
            self._retry_button = None
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
            self._message_label = QLabel(message)
            self._message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._message_label.setWordWrap(True)

            # Retry button (optional)
            self._retry_button = QPushButton("Retry")
            self._retry_button.clicked.connect(self.retry_clicked.emit)
            self._retry_button.setMaximumWidth(100)

            # Add to layout
            layout.addWidget(icon_label)
            layout.addWidget(self._message_label)
            layout.addWidget(self._retry_button, alignment=Qt.AlignmentFlag.AlignCenter)

            # Apply theme
            self.on_theme_changed()

        def on_theme_changed(self) -> None:
            """Called automatically when the theme changes."""
            error_fg = self.theme.error_fg
            error_bg = self.theme.error_bg
            error_border = self.theme.error_border

            # Update message label style
            if self._message_label:
                self._message_label.setStyleSheet(f"""
                    QLabel {{
                        color: {error_fg};
                        padding: 10px;
                        font-size: 14px;
                    }}
                """)

            # Update widget background
            self.setStyleSheet(f"""
                ErrorWidget {{
                    background-color: {error_bg};
                    border: 1px solid {error_border};
                    border-radius: 4px;
                }}
            """)

        def set_error(self, message: str):
            """Update error message.

            Args:
                message: New error message
            """
            if self._message_label:
                self._message_label.setText(message)

else:
    # Fallback when theme system is not available
    class ErrorWidget(QWidget):
        """ErrorWidget without theme support (theme system not installed)."""

        retry_clicked = Signal()

        def __init__(self, error_message: str = "An error occurred", parent=None):
            super().__init__(parent)
            raise ImportError(
                "vfwidgets-theme is required for ErrorWidget. "
                "Install with: pip install vfwidgets-theme"
            )


if THEME_AVAILABLE:

    class ValidationOverlay(ThemedWidget, QWidget):
        """Overlay to show validation errors with theme integration."""

        theme_config = {
            "error_bg": "inputValidation.errorBackground",
            "error_fg": "errorForeground",
        }

        def __init__(self, parent: QWidget = None):
            """Initialize validation overlay."""
            super().__init__(parent=parent)

            self.setAutoFillBackground(True)

            # Semi-transparent background
            palette = self.palette()
            palette.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.transparent)
            self.setPalette(palette)

            # Layout for messages
            self.layout = QVBoxLayout(self)
            self.layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

            self.messages = []

        def on_theme_changed(self) -> None:
            """Called automatically when the theme changes."""
            # Re-apply styles to all existing message frames
            error_bg = self.theme.error_bg
            error_fg = self.theme.error_fg

            for frame in self.messages:
                frame.setStyleSheet(f"""
                    QFrame {{
                        background-color: {error_bg};
                        color: {error_fg};
                        padding: 8px 12px;
                        border-radius: 4px;
                        margin: 4px;
                    }}
                """)

        def show_validation_error(self, message: str, duration: int = 3000):
            """Show validation error message.

            Args:
                message: Error message to show
                duration: How long to show (ms)
            """
            # Create message frame
            frame = QFrame()
            error_bg = self.theme.error_bg
            error_fg = self.theme.error_fg

            frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {error_bg};
                    color: {error_fg};
                    padding: 8px 12px;
                    border-radius: 4px;
                    margin: 4px;
                }}
            """)

            label = QLabel(message)
            label.setStyleSheet(f"color: {error_fg};")

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

else:

    class ValidationOverlay(QWidget):
        """ValidationOverlay without theme support (theme system not installed)."""

        def __init__(self, parent: QWidget = None):
            super().__init__(parent)
            raise ImportError(
                "vfwidgets-theme is required for ValidationOverlay. "
                "Install with: pip install vfwidgets-theme"
            )
