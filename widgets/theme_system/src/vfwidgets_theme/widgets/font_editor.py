"""Font Editor Widget - Theme Editor Component.

This module provides the FontEditorWidget for visual font editing.

Phase 2: Visual Editors
"""

from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import (
    QComboBox,
    QFontDialog,
    QGridLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..logging import get_debug_logger
from .base import ThemedWidget

logger = get_debug_logger(__name__)


class FontEditorWidget(ThemedWidget, QWidget):
    """Visual font editor with preview.

    Features:
    - Font family selector
    - Font size spinbox
    - Font weight selector
    - Font picker dialog (QFontDialog)
    - Live font preview

    Signals:
        font_changed(str): Emitted when font changes (as CSS string)
    """

    # Signals
    font_changed = Signal(str)  # Font as CSS string

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize font editor.

        Args:
            parent: Parent widget

        """
        super().__init__(parent)

        # Current font state
        self._current_font: QFont = QFont("Consolas", 12)
        self._token_path: str = ""

        # Setup UI
        self._setup_ui()

        logger.debug("FontEditorWidget initialized")

    def _setup_ui(self) -> None:
        """Setup user interface."""
        layout = QVBoxLayout(self)

        # Token info
        self._token_label = QLabel("No token selected")
        self._token_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(self._token_label)

        # Font picker button
        self._picker_button = QPushButton("Choose Font...")
        self._picker_button.clicked.connect(self._open_font_picker)
        layout.addWidget(self._picker_button)

        # Font properties
        props_group = QGroupBox("Font Properties")
        props_layout = QGridLayout(props_group)

        # Font family
        props_layout.addWidget(QLabel("Family:"), 0, 0)
        self._family_combo = QComboBox()
        self._family_combo.addItems(self._get_monospace_fonts())
        self._family_combo.currentTextChanged.connect(self._on_family_changed)
        props_layout.addWidget(self._family_combo, 0, 1)

        # Font size
        props_layout.addWidget(QLabel("Size:"), 1, 0)
        self._size_spin = QSpinBox()
        self._size_spin.setRange(6, 72)
        self._size_spin.setValue(12)
        self._size_spin.setSuffix(" pt")
        self._size_spin.valueChanged.connect(self._on_size_changed)
        props_layout.addWidget(self._size_spin, 1, 1)

        # Font weight
        props_layout.addWidget(QLabel("Weight:"), 2, 0)
        self._weight_combo = QComboBox()
        self._weight_combo.addItems(
            [
                "Thin (100)",
                "Extra Light (200)",
                "Light (300)",
                "Normal (400)",
                "Medium (500)",
                "Semi Bold (600)",
                "Bold (700)",
                "Extra Bold (800)",
                "Black (900)",
            ]
        )
        self._weight_combo.setCurrentIndex(3)  # Normal
        self._weight_combo.currentIndexChanged.connect(self._on_weight_changed)
        props_layout.addWidget(self._weight_combo, 2, 1)

        layout.addWidget(props_group)

        # Font preview
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)

        self._preview_text = QTextEdit()
        self._preview_text.setPlainText(
            "The quick brown fox jumps over the lazy dog\n"
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ\n"
            "abcdefghijklmnopqrstuvwxyz\n"
            "0123456789 !@#$%^&*()_+-=[]{}|;:',.<>?/"
        )
        self._preview_text.setFont(self._current_font)
        self._preview_text.setMaximumHeight(120)
        preview_layout.addWidget(self._preview_text)

        layout.addWidget(preview_group)

        layout.addStretch()

    def _get_monospace_fonts(self) -> list[str]:
        """Get list of monospace fonts.

        Returns:
            List of monospace font family names

        """
        database = QFontDatabase()
        all_families = database.families()

        # Common monospace fonts (prefer these)
        preferred = [
            "Consolas",
            "Monaco",
            "Menlo",
            "Courier New",
            "Courier",
            "DejaVu Sans Mono",
            "Liberation Mono",
            "Ubuntu Mono",
            "Fira Code",
            "Source Code Pro",
            "JetBrains Mono",
            "Cascadia Code",
            "SF Mono",
            "Roboto Mono",
        ]

        # Find monospace fonts
        monospace = []
        for family in preferred:
            if family in all_families:
                monospace.append(family)

        # Add other monospace fonts
        for family in all_families:
            if family not in monospace and database.isFixedPitch(family):
                monospace.append(family)

        return monospace if monospace else ["Courier New"]

    def _open_font_picker(self) -> None:
        """Open Qt font picker dialog."""
        font, ok = QFontDialog.getFont(self._current_font, self, "Choose Font")

        if ok:
            self.set_font(font)
            logger.debug(f"Font picked: {font.family()} {font.pointSize()}pt")

    def _on_family_changed(self, family: str) -> None:
        """Handle font family change.

        Args:
            family: New font family

        """
        self._current_font.setFamily(family)
        self._update_preview()
        self._emit_font_changed()

    def _on_size_changed(self, size: int) -> None:
        """Handle font size change.

        Args:
            size: New font size in points

        """
        self._current_font.setPointSize(size)
        self._update_preview()
        self._emit_font_changed()

    def _on_weight_changed(self, index: int) -> None:
        """Handle font weight change.

        Args:
            index: Weight combo index

        """
        weights = [100, 200, 300, 400, 500, 600, 700, 800, 900]
        weight = weights[index] if index < len(weights) else 400
        self._current_font.setWeight(QFont.Weight(weight))
        self._update_preview()
        self._emit_font_changed()

    def _update_preview(self) -> None:
        """Update font preview."""
        self._preview_text.setFont(self._current_font)

    def _emit_font_changed(self) -> None:
        """Emit font changed signal with CSS string."""
        css_font = self._font_to_css()
        self.font_changed.emit(css_font)
        logger.debug(f"Font changed: {css_font}")

    def _font_to_css(self) -> str:
        """Convert QFont to CSS font string.

        Returns:
            CSS font string (e.g., "12pt 'Consolas'")

        """
        family = self._current_font.family()
        size = self._current_font.pointSize()
        weight = self._current_font.weight()

        # Build CSS string
        css_parts = []

        # Font weight (if not normal)
        if weight != 400:
            css_parts.append(str(weight))

        # Font size
        css_parts.append(f"{size}pt")

        # Font family (quoted if contains spaces)
        if " " in family:
            css_parts.append(f"'{family}'")
        else:
            css_parts.append(family)

        return " ".join(css_parts)

    def _css_to_font(self, css_string: str) -> QFont:
        """Parse CSS font string to QFont.

        Args:
            css_string: CSS font string

        Returns:
            Parsed QFont

        """
        # Simple parser for common formats:
        # "12pt Consolas"
        # "12pt 'Courier New'"
        # "700 14pt Monaco"

        parts = css_string.split()
        font = QFont()

        for i, part in enumerate(parts):
            # Size (ends with pt, px, or is a number)
            if "pt" in part or "px" in part:
                size = int(part.replace("pt", "").replace("px", ""))
                font.setPointSize(size)

            # Weight (numeric 100-900)
            elif part.isdigit() and 100 <= int(part) <= 900:
                font.setWeight(QFont.Weight(int(part)))

            # Family (everything else, strip quotes)
            else:
                family = part.strip("'\"")
                # If last part, use it as family
                if i == len(parts) - 1 or (i == len(parts) - 2 and "pt" in parts[-1]):
                    font.setFamily(family)

        return font

    def set_font(self, font: QFont) -> None:
        """Set font and update controls.

        Args:
            font: New font

        """
        self._current_font = font

        # Update controls (block signals to prevent recursion)
        self._family_combo.blockSignals(True)
        self._size_spin.blockSignals(True)
        self._weight_combo.blockSignals(True)

        # Set family
        index = self._family_combo.findText(font.family())
        if index >= 0:
            self._family_combo.setCurrentIndex(index)

        # Set size
        self._size_spin.setValue(font.pointSize())

        # Set weight (find closest match)
        weight = font.weight()
        weight_values = [100, 200, 300, 400, 500, 600, 700, 800, 900]
        closest_index = min(range(len(weight_values)), key=lambda i: abs(weight_values[i] - weight))
        self._weight_combo.setCurrentIndex(closest_index)

        # Unblock signals
        self._family_combo.blockSignals(False)
        self._size_spin.blockSignals(False)
        self._weight_combo.blockSignals(False)

        # Update preview and emit
        self._update_preview()
        self._emit_font_changed()

    def set_font_from_css(self, css_string: str) -> bool:
        """Set font from CSS string.

        Args:
            css_string: CSS font string

        Returns:
            True if successfully parsed

        """
        try:
            font = self._css_to_font(css_string)
            self.set_font(font)
            return True
        except Exception as e:
            logger.warning(f"Failed to parse CSS font: {css_string} - {e}")
            return False

    def set_token(self, token_path: str, token_value: str) -> None:
        """Set token being edited.

        Args:
            token_path: Token path (e.g., "editor.font")
            token_value: Current token value (CSS font string)

        """
        self._token_path = token_path
        self._token_label.setText(f"Editing: {token_path}")

        # Load font value
        if token_value:
            self.set_font_from_css(token_value)
        else:
            # Default font
            self.set_font(QFont("Consolas", 12))

        logger.info(f"Token loaded: {token_path} = {token_value}")

    def get_font(self) -> QFont:
        """Get current font.

        Returns:
            Current QFont

        """
        return self._current_font

    def get_font_css(self) -> str:
        """Get font as CSS string.

        Returns:
            CSS font string

        """
        return self._font_to_css()

    def clear(self) -> None:
        """Clear editor."""
        self._current_font = QFont("Consolas", 12)
        self._token_path = ""
        self._token_label.setText("No token selected")
        self.set_font(self._current_font)
