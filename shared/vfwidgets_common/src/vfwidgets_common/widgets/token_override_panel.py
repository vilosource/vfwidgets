"""Token override panel for single theme type.

Displays a list of tokens with color pickers for one theme type
(dark, light, or high-contrast).
"""

import logging
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QWidget,
)

logger = logging.getLogger(__name__)


class TokenOverridePanel(QScrollArea):
    """Panel showing token list with color pickers for one theme type.

    Displays a scrollable list of tokens, each with:
    - Checkbox to enable/disable override
    - Color swatch button showing current color
    - Edit button to open color picker
    - Reset button to clear override

    Args:
        tokens: List of (token_path, label, description) tuples
        theme_type: "dark", "light", or "high-contrast"
        parent: Parent widget

    Example:
        >>> tokens = [
        ...     ("markdown.colors.link", "Links", "Hyperlink color"),
        ...     ("markdown.colors.background", "Background", "Main bg color"),
        ... ]
        >>> panel = TokenOverridePanel(tokens, "dark")
        >>> panel.load_tokens({"markdown.colors.link": "#58a6ff"})
        >>> overrides = panel.save_tokens()
        >>> overrides
        {'markdown.colors.link': '#58a6ff'}
    """

    def __init__(
        self,
        tokens: list[tuple[str, str, str]],
        theme_type: str,
        parent: Optional[QWidget] = None,
    ):
        """Initialize panel.

        Args:
            tokens: List of (token_path, label, description) tuples
            theme_type: "dark", "light", or "high-contrast"
            parent: Parent widget
        """
        super().__init__(parent)
        self.tokens = tokens
        self.theme_type = theme_type
        self.token_widgets = {}  # token_path -> (checkbox, color_button)
        self.token_colors = {}  # token_path -> QColor
        self._setup_ui()

    def _setup_ui(self):
        """Build token list with color pickers."""
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        form = QFormLayout(container)
        form.setContentsMargins(10, 10, 10, 10)
        form.setSpacing(8)

        # Add header
        header_label = QLabel(f"<b>{self.theme_type.title()} Theme Overrides</b>")
        form.addRow(header_label)

        # Add each token
        for token_path, label, description in self.tokens:
            row = self._create_token_row(token_path, label, description)
            form.addRow(f"{label}:", row)

        # Add reset all button at bottom
        reset_all_btn = QPushButton("Reset All to Theme Defaults")
        reset_all_btn.setToolTip(
            f"Remove all overrides for {self.theme_type} themes and return to theme defaults"
        )
        reset_all_btn.clicked.connect(self.reset_all)
        form.addRow("", reset_all_btn)

        self.setWidget(container)

    def _create_token_row(self, token_path: str, label: str, description: str) -> QWidget:
        """Create row widget for single token.

        Args:
            token_path: Full token path (e.g., "markdown.colors.link")
            label: Friendly label (e.g., "Links")
            description: Token description

        Returns:
            Widget containing checkbox, color button, edit button, reset button
        """
        row_widget = QWidget()
        row = QHBoxLayout(row_widget)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        # Checkbox to enable override
        checkbox = QCheckBox()
        checkbox.setToolTip(f"Override {token_path}")
        checkbox.stateChanged.connect(lambda state: self._on_checkbox_changed(token_path, state))
        row.addWidget(checkbox)

        # Color swatch button
        color_button = QPushButton()
        color_button.setFixedSize(100, 28)
        color_button.setToolTip(f"Current color for {token_path}\n\n{description}")
        color_button.clicked.connect(lambda: self._pick_color(token_path))
        row.addWidget(color_button)

        # Edit button (same action as color button)
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(lambda: self._pick_color(token_path))
        row.addWidget(edit_btn)

        # Reset button (clear this token's override)
        reset_btn = QPushButton("Reset")
        reset_btn.setToolTip("Remove override for this token (use theme default)")
        reset_btn.clicked.connect(lambda: self._reset_token(token_path))
        row.addWidget(reset_btn)

        row.addStretch()

        # Store widgets for later access
        self.token_widgets[token_path] = (checkbox, color_button)

        return row_widget

    def _on_checkbox_changed(self, token_path: str, state: int):
        """Handle checkbox state change.

        When checkbox is unchecked, clear the color override.

        Args:
            token_path: Token being changed
            state: Qt.CheckState value
        """
        if state == Qt.CheckState.Unchecked.value:
            # Clear the color
            self.token_colors.pop(token_path, None)
            checkbox, color_button = self.token_widgets[token_path]
            color_button.setStyleSheet("")
            color_button.setText("")

    def _pick_color(self, token_path: str):
        """Open color picker for token.

        Args:
            token_path: Token to set color for
        """
        checkbox, color_button = self.token_widgets[token_path]

        # Get current color if set
        current_color = self.token_colors.get(token_path, QColor())

        # Open color picker
        color = QColorDialog.getColor(current_color, self, f"Pick color for {token_path}")

        if color.isValid():
            # Store color
            self.token_colors[token_path] = color

            # Update button appearance
            self._update_color_button(color_button, color)

            # Enable checkbox
            checkbox.setChecked(True)

            logger.debug(f"Set color for '{token_path}': {color.name()}")

    def _update_color_button(self, button: QPushButton, color: QColor):
        """Update button to show color.

        Args:
            button: Button widget to update
            color: Color to show
        """
        # Determine text color based on brightness
        text_color = "white" if color.lightness() < 128 else "black"

        # Set button style
        button.setStyleSheet(
            f"background-color: {color.name()}; "
            f"color: {text_color}; "
            f"border: 1px solid #888;"
        )
        button.setText(color.name())

    def _reset_token(self, token_path: str):
        """Reset single token to theme default (remove override).

        Args:
            token_path: Token to reset
        """
        checkbox, color_button = self.token_widgets[token_path]

        # Uncheck checkbox (disable override)
        checkbox.setChecked(False)

        # Clear button styling
        color_button.setStyleSheet("")
        color_button.setText("")

        # Clear stored color
        self.token_colors.pop(token_path, None)

        logger.debug(f"Reset token '{token_path}' to theme default")

    def reset_all(self):
        """Reset all tokens to theme defaults (remove all overrides).

        Shows confirmation dialog before resetting.
        """
        if not self.token_widgets:
            return

        # Confirmation dialog
        reply = QMessageBox.question(
            self,
            "Reset All Tokens",
            f"Reset all {len(self.token_widgets)} tokens to theme defaults?\n\n"
            f"This will remove all color overrides for {self.theme_type} themes.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,  # Default to No
        )

        if reply != QMessageBox.StandardButton.Yes:
            logger.debug("Reset all cancelled by user")
            return

        # Reset each token
        for token_path in self.token_widgets.keys():
            self._reset_token(token_path)

        logger.info(f"Reset all {len(self.token_widgets)} tokens for {self.theme_type} themes")

    def reset_all_silent(self):
        """Reset all tokens without confirmation dialog.

        Used when resetting from parent widget that already confirmed.
        """
        for token_path in self.token_widgets.keys():
            self._reset_token(token_path)

    def load_tokens(self, token_overrides: dict[str, str]):
        """Load token overrides into UI.

        Args:
            token_overrides: Dictionary of token_path -> color_hex
        """
        for token_path, (checkbox, color_button) in self.token_widgets.items():
            if token_path in token_overrides:
                color_hex = token_overrides[token_path]
                color = QColor(color_hex)

                if color.isValid():
                    # Store color
                    self.token_colors[token_path] = color

                    # Update UI
                    checkbox.setChecked(True)
                    self._update_color_button(color_button, color)
                else:
                    logger.warning(f"Invalid color '{color_hex}' for token '{token_path}'")
            else:
                # Not overridden - reset to defaults
                checkbox.setChecked(False)
                color_button.setStyleSheet("")
                color_button.setText("")

    def save_tokens(self) -> dict[str, str]:
        """Collect token overrides from UI.

        Returns:
            Dictionary of token_path -> color_hex for checked tokens only
        """
        overrides = {}

        for token_path, (checkbox, _color_button) in self.token_widgets.items():
            if checkbox.isChecked() and token_path in self.token_colors:
                color = self.token_colors[token_path]
                if color.isValid():
                    overrides[token_path] = color.name()

        logger.debug(f"Collected {len(overrides)} token overrides for {self.theme_type} themes")
        return overrides
