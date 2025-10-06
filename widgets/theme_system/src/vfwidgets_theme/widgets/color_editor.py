"""Color Editor Widget - Theme Editor Component.

This module provides the ColorEditorWidget for visual color editing with
format conversion and validation.

Phase 2: Color Editing
"""

from typing import Optional

from PySide6.QtCore import QSize, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..core.theme import (
    HEX_COLOR_PATTERN,
    RGB_COLOR_PATTERN,
    RGBA_COLOR_PATTERN,
)
from ..logging import get_debug_logger
from .base import ThemedWidget

logger = get_debug_logger(__name__)


class ColorEditorWidget(ThemedWidget, QWidget):
    """Visual color editor with format conversion.

    Features:
    - Color picker dialog (QColorDialog)
    - Hex/RGB/RGBA input fields with validation
    - Color preview swatch
    - Format conversion (hex ↔ rgb ↔ rgba)
    - Live color updates

    Signals:
        color_changed(str): Emitted when color value changes (in current format)
    """

    # Signals
    color_changed = Signal(str)  # Color value in current format

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize color editor.

        Args:
            parent: Parent widget

        """
        super().__init__(parent)

        # Current color state
        self._current_color: Optional[QColor] = None
        self._current_format: str = "hex"  # "hex", "rgb", "rgba"
        self._token_path: str = ""

        # Setup UI
        self._setup_ui()

        logger.debug("ColorEditorWidget initialized")

    def _setup_ui(self) -> None:
        """Setup user interface."""
        layout = QVBoxLayout(self)

        # Token info
        self._token_label = QLabel("No token selected")
        self._token_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(self._token_label)

        # Color preview and picker
        preview_layout = QHBoxLayout()

        # Color preview swatch
        self._color_swatch = QWidget()
        self._color_swatch.setMinimumSize(QSize(100, 100))
        self._color_swatch.setMaximumSize(QSize(100, 100))
        self._color_swatch.setStyleSheet("background-color: #1e1e1e; border: 2px solid #666;")
        preview_layout.addWidget(self._color_swatch)

        # Picker button
        picker_layout = QVBoxLayout()
        self._picker_button = QPushButton("Choose Color...")
        self._picker_button.clicked.connect(self._open_color_picker)
        picker_layout.addWidget(self._picker_button)
        picker_layout.addStretch()
        preview_layout.addLayout(picker_layout)

        preview_layout.addStretch()
        layout.addLayout(preview_layout)

        # Color format inputs
        format_group = QGroupBox("Color Format")
        format_group.setMaximumWidth(400)  # Compact width for color inputs
        format_layout = QGridLayout(format_group)

        # Hex input
        format_layout.addWidget(QLabel("Hex:"), 0, 0)
        self._hex_input = QLineEdit()
        self._hex_input.setPlaceholderText("#RRGGBB or #RRGGBBAA")
        self._hex_input.setMaximumWidth(280)  # Enough for ~32 characters
        self._hex_input.textChanged.connect(lambda: self._on_input_changed("hex"))
        format_layout.addWidget(self._hex_input, 0, 1)

        # RGB input
        format_layout.addWidget(QLabel("RGB:"), 1, 0)
        self._rgb_input = QLineEdit()
        self._rgb_input.setPlaceholderText("rgb(R, G, B)")
        self._rgb_input.setMaximumWidth(280)  # Enough for ~32 characters
        self._rgb_input.textChanged.connect(lambda: self._on_input_changed("rgb"))
        format_layout.addWidget(self._rgb_input, 1, 1)

        # RGBA input
        format_layout.addWidget(QLabel("RGBA:"), 2, 0)
        self._rgba_input = QLineEdit()
        self._rgba_input.setPlaceholderText("rgba(R, G, B, A)")
        self._rgba_input.setMaximumWidth(280)  # Enough for ~32 characters
        self._rgba_input.textChanged.connect(lambda: self._on_input_changed("rgba"))
        format_layout.addWidget(self._rgba_input, 2, 1)

        layout.addWidget(format_group)

        # Format info
        self._format_info = QLabel("Tip: All formats are auto-converted")
        self._format_info.setStyleSheet("color: #888; font-size: 10pt;")
        layout.addWidget(self._format_info)

        layout.addStretch()

    def _open_color_picker(self) -> None:
        """Open Qt color picker dialog."""
        # Get initial color
        initial_color = self._current_color or QColor("#1e1e1e")

        # Open picker
        color = QColorDialog.getColor(
            initial_color, self, "Choose Color", QColorDialog.ColorDialogOption.ShowAlphaChannel
        )

        if color.isValid():
            self.set_color(color)
            logger.debug(f"Color picked: {color.name()}")

    def _on_input_changed(self, format_type: str) -> None:
        """Handle manual input changes.

        Args:
            format_type: Format that changed ("hex", "rgb", "rgba")

        """
        # Get input value
        if format_type == "hex":
            value = self._hex_input.text()
        elif format_type == "rgb":
            value = self._rgb_input.text()
        else:
            value = self._rgba_input.text()

        # Parse and validate
        color = self._parse_color_string(value)
        if color and color.isValid():
            # Update color without triggering input change again
            self._update_color_silent(color)
            self._current_format = format_type
            self.color_changed.emit(value)

    def _parse_color_string(self, value: str) -> Optional[QColor]:
        """Parse color string in any format.

        Args:
            value: Color string (hex, rgb, rgba)

        Returns:
            QColor if valid, None otherwise

        """
        value = value.strip()

        # Hex format
        if HEX_COLOR_PATTERN.match(value):
            return QColor(value)

        # RGB format
        rgb_match = RGB_COLOR_PATTERN.match(value)
        if rgb_match:
            r, g, b = map(int, rgb_match.groups())
            return QColor(r, g, b)

        # RGBA format
        rgba_match = RGBA_COLOR_PATTERN.match(value)
        if rgba_match:
            r, g, b = map(int, rgba_match.groups()[:3])
            a = float(rgba_match.groups()[3])
            color = QColor(r, g, b)
            color.setAlphaF(a)
            return color

        return None

    def _update_color_silent(self, color: QColor) -> None:
        """Update color without emitting signals.

        Args:
            color: New color

        """
        self._current_color = color

        # Block signals to prevent recursion
        self._hex_input.blockSignals(True)
        self._rgb_input.blockSignals(True)
        self._rgba_input.blockSignals(True)

        # Update all format inputs
        self._hex_input.setText(color.name(QColor.NameFormat.HexArgb))
        self._rgb_input.setText(f"rgb({color.red()}, {color.green()}, {color.blue()})")
        self._rgba_input.setText(
            f"rgba({color.red()}, {color.green()}, {color.blue()}, {color.alphaF():.2f})"
        )

        # Update color swatch
        self._color_swatch.setStyleSheet(
            f"background-color: {color.name(QColor.NameFormat.HexArgb)}; "
            f"border: 2px solid #666;"
        )

        # Unblock signals
        self._hex_input.blockSignals(False)
        self._rgb_input.blockSignals(False)
        self._rgba_input.blockSignals(False)

    def set_color(self, color: QColor) -> None:
        """Set color and update all inputs.

        Args:
            color: New color

        """
        self._update_color_silent(color)

        # Emit signal with current format
        if self._current_format == "hex":
            value = color.name(QColor.NameFormat.HexArgb)
        elif self._current_format == "rgb":
            value = f"rgb({color.red()}, {color.green()}, {color.blue()})"
        else:
            value = f"rgba({color.red()}, {color.green()}, {color.blue()}, {color.alphaF():.2f})"

        self.color_changed.emit(value)
        logger.debug(f"Color set: {value}")

    def set_color_from_string(self, value: str) -> bool:
        """Set color from string value.

        Args:
            value: Color string (hex, rgb, rgba)

        Returns:
            True if successfully parsed and set

        """
        color = self._parse_color_string(value)
        if color and color.isValid():
            self._update_color_silent(color)

            # Determine format from input
            if HEX_COLOR_PATTERN.match(value):
                self._current_format = "hex"
            elif RGB_COLOR_PATTERN.match(value):
                self._current_format = "rgb"
            elif RGBA_COLOR_PATTERN.match(value):
                self._current_format = "rgba"

            return True

        logger.warning(f"Invalid color string: {value}")
        return False

    def set_token(self, token_path: str, token_value: str) -> None:
        """Set token being edited.

        Args:
            token_path: Token path (e.g., "button.background")
            token_value: Current token value

        """
        self._token_path = token_path
        self._token_label.setText(f"Editing: {token_path}")

        # Load color value
        if token_value:
            self.set_color_from_string(token_value)
        else:
            # Default to black if no value
            self.set_color(QColor("#000000"))

        logger.info(f"Token loaded: {token_path} = {token_value}")

    def get_color(self) -> Optional[QColor]:
        """Get current color.

        Returns:
            Current QColor or None

        """
        return self._current_color

    def get_color_string(self, format_type: Optional[str] = None) -> str:
        """Get color as string in specified format.

        Args:
            format_type: Format ("hex", "rgb", "rgba"), uses current if None

        Returns:
            Color string in requested format

        """
        if not self._current_color:
            return ""

        format_type = format_type or self._current_format
        color = self._current_color

        if format_type == "hex":
            return color.name(QColor.NameFormat.HexArgb)
        elif format_type == "rgb":
            return f"rgb({color.red()}, {color.green()}, {color.blue()})"
        else:
            return f"rgba({color.red()}, {color.green()}, {color.blue()}, {color.alphaF():.2f})"

    def clear(self) -> None:
        """Clear editor."""
        self._current_color = None
        self._token_path = ""
        self._token_label.setText("No token selected")
        self._hex_input.clear()
        self._rgb_input.clear()
        self._rgba_input.clear()
        self._color_swatch.setStyleSheet("background-color: #1e1e1e; border: 2px solid #666;")
