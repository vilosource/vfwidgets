"""Implementation of MarkdownViewerWidget."""

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

# Uncomment to use base class:
# from vfwidgets_common import VFBaseWidget


class MarkdownViewerWidget(QWidget):  # or VFBaseWidget if using common
    """Custom markdown_viewer widget.

    Signals:
        value_changed: Emitted when the widget value changes
    """

    # Define custom signals
    value_changed = Signal(object)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the MarkdownViewerWidget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the widget UI."""
        layout = QVBoxLayout(self)

        # Example content
        self.label = QLabel("MarkdownViewerWidget Widget")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        # Set some default styling
        self.setStyleSheet("""
            QLabel {
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
        """)

    def set_value(self, value: object) -> None:
        """Set the widget value.

        Args:
            value: The new value
        """
        # Implementation here
        self.value_changed.emit(value)

    def get_value(self) -> object:
        """Get the current widget value.

        Returns:
            The current value
        """
        # Implementation here
        return None
