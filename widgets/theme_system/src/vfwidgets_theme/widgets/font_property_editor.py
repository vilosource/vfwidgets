"""Font Property Editor Widget - Theme Editor Component.

This module provides the FontPropertyEditorWidget for editing individual font properties
(size, weight, line height, letter spacing) with Theme.fonts token integration.

Phase 4: Font Property Editing
"""

from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ..core.theme import Theme
from ..errors import FontPropertyError
from ..logging import get_debug_logger
from .base import ThemedWidget

logger = get_debug_logger(__name__)


class FontPropertyEditorWidget(ThemedWidget, QWidget):
    """Editor for individual font properties (size, weight, line height, letter spacing).

    This widget provides a form-based interface for editing font properties
    with appropriate controls for each property type.

    Features:
    - Font size: spinbox (6-144pt)
    - Font weight: combo with 100-900 and names (normal, bold, etc)
    - Line height: double spinbox (0.5-3.0)
    - Letter spacing: double spinbox (-5.0 to 5.0)
    - Validation feedback with error messages
    - Real-time updates via signals

    Signals:
        property_changed(str, object): Emitted when property changes (token_path, new_value)
    """

    # Signals
    property_changed = Signal(str, object)  # (token_path, new_value)

    # Weight mapping (name -> int)
    WEIGHT_MAP = {
        "100 (Thin)": 100,
        "200 (Extra Light)": 200,
        "300 (Light)": 300,
        "400 (Normal)": 400,
        "500 (Medium)": 500,
        "600 (Semi Bold)": 600,
        "700 (Bold)": 700,
        "800 (Extra Bold)": 800,
        "900 (Black)": 900,
    }

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize font property editor.

        Args:
            parent: Parent widget

        """
        super().__init__(parent)

        # Current state
        self._current_token: Optional[str] = None
        self._current_theme: Optional[Theme] = None
        self._updating: bool = False  # Flag to prevent signal loops

        # Setup UI
        self._setup_ui()

        logger.debug("FontPropertyEditorWidget initialized")

    def _setup_ui(self) -> None:
        """Set up user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Token label
        self._token_label = QLabel("No token selected")
        self._token_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        layout.addWidget(self._token_label)

        # Form layout for properties
        self._form = QFormLayout()
        self._form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        # Font size spinbox (6-144pt)
        self._size_spin = QSpinBox()
        self._size_spin.setRange(6, 144)
        self._size_spin.setValue(13)
        self._size_spin.setSuffix(" pt")
        self._size_spin.valueChanged.connect(self._on_size_changed)
        self._form.addRow("Font Size:", self._size_spin)

        # Font weight combo
        self._weight_combo = QComboBox()
        self._weight_combo.addItems(list(self.WEIGHT_MAP.keys()))
        self._weight_combo.setCurrentText("400 (Normal)")
        self._weight_combo.currentTextChanged.connect(self._on_weight_changed)
        self._form.addRow("Font Weight:", self._weight_combo)

        # Line height spinbox (0.5-3.0)
        self._line_height_spin = QDoubleSpinBox()
        self._line_height_spin.setRange(0.5, 3.0)
        self._line_height_spin.setValue(1.4)
        self._line_height_spin.setSingleStep(0.1)
        self._line_height_spin.setDecimals(1)
        self._line_height_spin.setSuffix("×")
        self._line_height_spin.valueChanged.connect(self._on_line_height_changed)
        self._form.addRow("Line Height:", self._line_height_spin)

        # Letter spacing spinbox (-5.0 to 5.0)
        self._letter_spacing_spin = QDoubleSpinBox()
        self._letter_spacing_spin.setRange(-5.0, 5.0)
        self._letter_spacing_spin.setValue(0.0)
        self._letter_spacing_spin.setSingleStep(0.1)
        self._letter_spacing_spin.setDecimals(1)
        self._letter_spacing_spin.setSuffix(" px")
        self._letter_spacing_spin.valueChanged.connect(self._on_letter_spacing_changed)
        self._form.addRow("Letter Spacing:", self._letter_spacing_spin)

        layout.addLayout(self._form)

        # Error label (hidden by default)
        self._error_label = QLabel()
        self._error_label.setStyleSheet("color: #FF6B6B; font-weight: bold;")
        self._error_label.setWordWrap(True)
        self._error_label.hide()
        layout.addWidget(self._error_label)

        # Help text
        self._help_label = QLabel()
        self._help_label.setWordWrap(True)
        self._help_label.setStyleSheet("color: #888; font-size: 9pt; margin-top: 10px;")
        layout.addWidget(self._help_label)

        layout.addStretch()

        # Initially hide all editors
        self._hide_all_editors()

    def _hide_all_editors(self) -> None:
        """Hide all property editors."""
        # Hide size row
        self._form.setRowVisible(self._size_spin, False)

        # Hide weight row
        self._form.setRowVisible(self._weight_combo, False)

        # Hide line height row
        self._form.setRowVisible(self._line_height_spin, False)

        # Hide letter spacing row
        self._form.setRowVisible(self._letter_spacing_spin, False)

    def set_token(self, token_path: str, current_value, theme: Theme) -> None:
        """Set the token being edited.

        Args:
            token_path: Token path (e.g., "terminal.fontSize")
            current_value: Current value of the token
            theme: Theme to resolve from

        """
        self._current_token = token_path
        self._current_theme = theme
        self._updating = True  # Prevent signal emission during setup

        # Update token label
        self._token_label.setText(f"Editing: {token_path}")

        # Clear error
        self._clear_error()

        # Hide all editors first
        self._hide_all_editors()

        # Show appropriate editor based on token type
        if self._is_size_token(token_path):
            self._show_size_editor(current_value)
        elif self._is_weight_token(token_path):
            self._show_weight_editor(current_value)
        elif self._is_line_height_token(token_path):
            self._show_line_height_editor(current_value)
        elif self._is_letter_spacing_token(token_path):
            self._show_letter_spacing_editor(current_value)

        self._updating = False

        logger.debug(f"Set token: {token_path} = {current_value}")

    def _is_size_token(self, token_path: str) -> bool:
        """Check if token is a font size token."""
        return "Size" in token_path or token_path == "fonts.size"

    def _is_weight_token(self, token_path: str) -> bool:
        """Check if token is a font weight token."""
        return "Weight" in token_path or token_path == "fonts.weight"

    def _is_line_height_token(self, token_path: str) -> bool:
        """Check if token is a line height token."""
        return "lineHeight" in token_path

    def _is_letter_spacing_token(self, token_path: str) -> bool:
        """Check if token is a letter spacing token."""
        return "letterSpacing" in token_path

    def _show_size_editor(self, current_value) -> None:
        """Show font size spinbox.

        Args:
            current_value: Current font size value

        """
        # Show size spinbox row
        self._form.setRowVisible(self._size_spin, True)

        # Set value
        if isinstance(current_value, (int, float)):
            self._size_spin.setValue(int(current_value))

        # Update help text
        self._help_label.setText(
            "Font size in points (6-144pt). Used for rendering text at different scales."
        )

    def _show_weight_editor(self, current_value) -> None:
        """Show font weight combo.

        Args:
            current_value: Current font weight value

        """
        # Show weight combo row
        self._form.setRowVisible(self._weight_combo, True)

        # Set value
        if isinstance(current_value, int):
            # Find matching weight
            for display_name, weight_value in self.WEIGHT_MAP.items():
                if weight_value == current_value:
                    self._weight_combo.setCurrentText(display_name)
                    break
        elif isinstance(current_value, str):
            # Map string weight to display name
            weight_str_map = {
                "normal": "400 (Normal)",
                "bold": "700 (Bold)",
            }
            display_name = weight_str_map.get(current_value.lower(), "400 (Normal)")
            self._weight_combo.setCurrentText(display_name)

        # Update help text
        self._help_label.setText(
            "Font weight controls thickness/boldness. 400 is normal, 700 is bold."
        )

    def _show_line_height_editor(self, current_value) -> None:
        """Show line height spinbox.

        Args:
            current_value: Current line height value

        """
        # Show line height spinbox row
        self._form.setRowVisible(self._line_height_spin, True)

        # Set value
        if isinstance(current_value, (int, float)):
            self._line_height_spin.setValue(float(current_value))

        # Update help text
        self._help_label.setText(
            "Line height multiplier (0.5-3.0×). 1.4× means 140% of font size. "
            "Larger values increase spacing between lines."
        )

    def _show_letter_spacing_editor(self, current_value) -> None:
        """Show letter spacing spinbox.

        Args:
            current_value: Current letter spacing value

        """
        # Show letter spacing spinbox row
        self._form.setRowVisible(self._letter_spacing_spin, True)

        # Set value
        if isinstance(current_value, (int, float)):
            self._letter_spacing_spin.setValue(float(current_value))

        # Update help text
        self._help_label.setText(
            "Letter spacing in pixels (-5.0 to 5.0px). "
            "Positive values spread letters apart, negative brings them closer."
        )

    def _on_size_changed(self, value: int) -> None:
        """Handle font size change."""
        if self._updating or not self._current_token:
            return

        self._validate_and_emit(value)

    def _on_weight_changed(self, display_name: str) -> None:
        """Handle font weight change."""
        if self._updating or not self._current_token:
            return

        # Convert display name to weight value
        weight = self.WEIGHT_MAP.get(display_name, 400)
        self._validate_and_emit(weight)

    def _on_line_height_changed(self, value: float) -> None:
        """Handle line height change."""
        if self._updating or not self._current_token:
            return

        self._validate_and_emit(value)

    def _on_letter_spacing_changed(self, value: float) -> None:
        """Handle letter spacing change."""
        if self._updating or not self._current_token:
            return

        self._validate_and_emit(value)

    def _validate_and_emit(self, new_value) -> None:
        """Validate new value before emitting.

        Args:
            new_value: New property value to validate

        """
        if not self._current_token:
            return

        try:
            # Validate using Theme constructor
            # Create test theme with the new value
            test_fonts = dict(self._current_theme.fonts) if self._current_theme else {}
            test_fonts[self._current_token] = new_value

            # Validation happens in Theme __post_init__
            Theme(name="validation_test", fonts=test_fonts)

            # Clear error
            self._clear_error()

            # Emit change
            self.property_changed.emit(self._current_token, new_value)

            logger.debug(f"Property changed: {self._current_token} = {new_value}")

        except (FontPropertyError, Exception) as e:
            # Show error in UI
            self._show_error(str(e))
            logger.warning(f"Validation error: {e}")

    def _show_error(self, message: str) -> None:
        """Show error message.

        Args:
            message: Error message to display

        """
        self._error_label.setText(f"⚠️ {message}")
        self._error_label.show()

    def _clear_error(self) -> None:
        """Clear error message."""
        self._error_label.clear()
        self._error_label.hide()

    def get_current_token(self) -> Optional[str]:
        """Get currently edited token.

        Returns:
            Current token path or None

        """
        return self._current_token
