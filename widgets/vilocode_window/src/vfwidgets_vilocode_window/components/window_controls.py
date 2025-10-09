"""Window controls for frameless windows.

Provides minimize, maximize, and close buttons for the title bar.
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QWidget


class WindowControls(QWidget):
    """Window control buttons (minimize, maximize, close).

    Provides standard window buttons for frameless windows.
    """

    # Signals
    minimize_clicked = Signal()
    maximize_clicked = Signal()
    close_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create buttons
        self._min_button = self._create_button("−", "Minimize")
        self._max_button = self._create_button("□", "Maximize")
        self._close_button = self._create_button("✕", "Close")

        # Connect signals
        self._min_button.clicked.connect(self._on_minimize)
        self._max_button.clicked.connect(self._on_maximize)
        self._close_button.clicked.connect(self._on_close)

        # Add to layout
        layout.addWidget(self._min_button)
        layout.addWidget(self._max_button)
        layout.addWidget(self._close_button)

    def _create_button(self, text: str, tooltip: str) -> QPushButton:
        """Create a window control button."""
        button = QPushButton(text)
        button.setToolTip(tooltip)
        button.setFixedSize(46, 30)
        button.setFlat(True)

        # Style the button
        button.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                border: none;
                color: #cccccc;
                font-size: 16px;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """
        )

        # Special styling for close button
        if text == "✕":
            button.setStyleSheet(
                button.styleSheet()
                + """
            QPushButton:hover {
                background-color: #e81123;
                color: white;
            }
            QPushButton:pressed {
                background-color: #c20010;
                color: white;
            }
        """
            )

        return button

    def _on_minimize(self) -> None:
        """Handle minimize button click."""
        self.minimize_clicked.emit()
        window = self.window()
        if window:
            window.showMinimized()

    def _on_maximize(self) -> None:
        """Handle maximize button click."""
        self.maximize_clicked.emit()
        window = self.window()
        if window:
            if window.isMaximized():
                window.showNormal()
                self._max_button.setText("□")
            else:
                window.showMaximized()
                self._max_button.setText("❐")

    def _on_close(self) -> None:
        """Handle close button click."""
        self.close_clicked.emit()
        window = self.window()
        if window:
            window.close()
