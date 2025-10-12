"""Inspector Panel - Right panel for token details."""

import logging

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QCursor
from PySide6.QtWidgets import (
    QColorDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)
from vfwidgets_theme.core.tokens import ColorTokenRegistry

logger = logging.getLogger(__name__)


class InspectorPanel(QWidget):
    """Inspector panel - displays selected token properties.

    UX: Instant editing with live preview
    - Click color swatch to pick color
    - Changes apply immediately with live preview
    - Use Ctrl+Z to undo
    - No Save/Cancel buttons needed

    Architecture:
        InspectorPanel → ThemeController.queue_token_change() → ThemeDocument

    The controller decouples dialog lifecycle from document updates,
    preventing Qt object lifetime conflicts.
    """

    def __init__(self, parent=None, controller=None):
        """Initialize inspector panel.

        Args:
            parent: Parent widget
            controller: ThemeController instance for queuing changes
        """
        super().__init__(parent)
        self._controller = controller
        self._current_token = None
        self._current_value = None
        self._color_dialog = None  # Keep reference to prevent premature deletion
        self._setup_ui()

    def set_controller(self, controller) -> None:
        """Set the theme controller.

        Args:
            controller: ThemeController instance
        """
        self._controller = controller

    def _setup_ui(self):
        """Setup UI for token inspection."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(10)

        # Title
        self.title_label = QLabel("No Token Selected")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.title_label.setWordWrap(True)
        layout.addWidget(self.title_label)

        # Color preview swatch (clickable!)
        self.color_swatch = QFrame()
        self.color_swatch.setFixedHeight(60)
        self.color_swatch.setFrameShape(QFrame.Box)
        self.color_swatch.setStyleSheet("background-color: #000000; border: 2px solid gray;")
        self.color_swatch.setCursor(QCursor(Qt.PointingHandCursor))
        self.color_swatch.mousePressEvent = lambda e: self._on_color_swatch_clicked()
        self.color_swatch.hide()  # Hidden until token selected
        layout.addWidget(self.color_swatch)

        # Hint label
        self.hint_label = QLabel("💡 Click swatch or value to change color")
        self.hint_label.setStyleSheet("color: gray; font-size: 11px; font-style: italic;")
        self.hint_label.hide()
        layout.addWidget(self.hint_label)

        # Token info group
        self.info_group = QGroupBox("Token Information")
        info_layout = QFormLayout(self.info_group)

        self.token_name_label = QLabel("-")
        self.token_name_label.setWordWrap(True)
        info_layout.addRow("Name:", self.token_name_label)

        # Clickable value display (opens color dialog)
        self.token_value_label = QLabel("-")
        self.token_value_label.setWordWrap(True)
        self.token_value_label.setStyleSheet("padding: 4px; border: 1px solid gray; background: white;")
        self.token_value_label.setCursor(QCursor(Qt.PointingHandCursor))
        self.token_value_label.mousePressEvent = lambda e: self._on_value_clicked()
        info_layout.addRow("Value:", self.token_value_label)

        self.token_category_label = QLabel("-")
        info_layout.addRow("Category:", self.token_category_label)

        self.token_description_label = QLabel("-")
        self.token_description_label.setWordWrap(True)
        info_layout.addRow("Description:", self.token_description_label)

        self.info_group.hide()  # Hidden until token selected
        layout.addWidget(self.info_group)

        # Color details group (only shown for color tokens with values)
        self.color_group = QGroupBox("Color Details")
        color_layout = QFormLayout(self.color_group)

        self.rgb_label = QLabel("-")
        color_layout.addRow("RGB:", self.rgb_label)

        self.hsl_label = QLabel("-")
        color_layout.addRow("HSL:", self.hsl_label)

        self.hex_label = QLabel("-")
        color_layout.addRow("Hex:", self.hex_label)

        self.color_group.hide()  # Hidden until color token selected
        layout.addWidget(self.color_group)

        layout.addStretch()

    def set_token(self, token_name: str, token_value: str):
        """Set the token to inspect.

        Args:
            token_name: Token name (e.g., "button.background")
            token_value: Current token value
        """
        self._current_token = token_name
        self._current_value = token_value

        # Update title
        self.title_label.setText(token_name)

        # Get token metadata from registry
        token_info = ColorTokenRegistry.get_token(token_name)

        # Show info group
        self.info_group.show()

        # Update token info
        self.token_name_label.setText(token_name)
        display_value = token_value if token_value else "(click to set)"
        self.token_value_label.setText(display_value)
        self.token_category_label.setText(token_info.category.value if token_info else "unknown")
        self.token_description_label.setText(token_info.description if token_info else "No description")

        # If token has a value and it's a valid color, show color details
        if token_value:
            try:
                color = QColor(token_value)
                if color.isValid():
                    # Show color swatch with clickable styling
                    self.color_swatch.setStyleSheet(
                        f"background-color: {token_value}; border: 2px solid gray;"
                    )
                    self.color_swatch.show()
                    self.hint_label.show()

                    # Show color group
                    self.color_group.show()

                    # Update color details
                    self.rgb_label.setText(f"rgb({color.red()}, {color.green()}, {color.blue()})")
                    self.hsl_label.setText(
                        f"hsl({color.hslHue()}, {color.hslSaturation()}%, {color.lightness()}%)"
                    )
                    self.hex_label.setText(color.name())
                else:
                    self._hide_color_details()
            except:
                self._hide_color_details()
        else:
            self._hide_color_details()

    def _hide_color_details(self):
        """Hide color-specific details."""
        self.color_swatch.hide()
        self.hint_label.hide()
        self.color_group.hide()

    def clear(self):
        """Clear inspector panel."""
        self._current_token = None
        self._current_value = None
        self.title_label.setText("No Token Selected")
        self.token_name_label.setText("-")
        self.token_value_label.setText("-")
        self.token_category_label.setText("-")
        self.token_description_label.setText("-")
        self.rgb_label.setText("-")
        self.hsl_label.setText("-")
        self.hex_label.setText("-")
        self.info_group.hide()
        self.color_group.hide()
        self.color_swatch.hide()
        self.hint_label.hide()

    def _on_value_clicked(self):
        """Handle value label click - opens modal dialog with color picker.

        Dialog closes automatically when:
        - User clicks a color in the picker
        - User types hex and presses Enter
        - User clicks OK/Apply
        """
        if not self._current_token:
            return

        # Both color swatch and value label open the same color picker dialog
        self._on_color_swatch_clicked()

    def _on_color_swatch_clicked(self):
        """Handle color swatch click - open color picker using Qt's static method.

        Architecture: Uses QColorDialog.getColor() static method which Qt manages entirely.
        This avoids all dialog lifecycle issues since Qt handles creation and deletion.
        """
        logger.debug("_on_color_swatch_clicked: START")
        if not self._current_token:
            logger.debug("_on_color_swatch_clicked: No token selected, returning")
            return

        # Get current color
        current_value = self._current_value if self._current_value else "#ffffff"
        initial_color = QColor(current_value)
        token_name = self._current_token
        logger.debug(f"_on_color_swatch_clicked: Opening color dialog for token={token_name}, color={current_value}")

        # Use Qt's static method - Qt manages everything
        # This is the recommended way for simple color picking
        selected_color = QColorDialog.getColor(
            initial_color,
            self,
            f"Pick Color: {token_name}",
            QColorDialog.ShowAlphaChannel | QColorDialog.DontUseNativeDialog
        )

        logger.debug(f"_on_color_swatch_clicked: Dialog returned, valid={selected_color.isValid()}")

        # Check if user selected a color
        if selected_color.isValid():
            hex_color = selected_color.name()
            logger.debug(f"_on_color_swatch_clicked: Color selected: {hex_color}")

            # Update UI immediately
            logger.debug("_on_color_swatch_clicked: Updating UI")
            self._apply_color_change_immediate(selected_color)

            # Queue document update via controller
            logger.debug(f"_on_color_swatch_clicked: Queuing controller update: {token_name}={hex_color}")
            if self._controller:
                self._controller.queue_token_change(token_name, hex_color)
                logger.debug("_on_color_swatch_clicked: Update queued, END")
            else:
                logger.warning("_on_color_swatch_clicked: No controller set!")
        else:
            logger.debug("_on_color_swatch_clicked: No color selected or cancelled, END")

    def _on_color_dialog_finished(self, dialog, token_name: str, result: int):
        """Handle color dialog finished signal.

        This is called by Qt AFTER the dialog has fully cleaned up, ensuring
        safe execution of document updates.

        Args:
            dialog: QColorDialog instance (may be partially deleted)
            token_name: Token name that was being edited
            result: QDialog.Accepted or QDialog.Rejected
        """
        logger.debug(f"_on_color_dialog_finished: result={result}, token={token_name}")

        # Extract color immediately before any operations
        selected_color = None
        if result == QColorDialog.Accepted:
            try:
                color = dialog.selectedColor()
                if color.isValid():
                    # Convert to hex string immediately (don't keep QColor reference)
                    selected_color = color.name()
                    logger.debug(f"_on_color_dialog_finished: Color selected: {selected_color}")
            except RuntimeError:
                # Dialog already deleted
                logger.warning("_on_color_dialog_finished: Dialog already deleted, cannot get color")

        # IMPORTANT: Disconnect the signal first to prevent re-entrancy
        try:
            dialog.finished.disconnect()
            logger.debug("_on_color_dialog_finished: Disconnected finished signal")
        except (RuntimeError, TypeError):
            pass

        # Close and delete dialog using Qt's proper cleanup
        # Use close() + deleteLater() + setAttribute for proper cleanup
        try:
            dialog.close()
            dialog.setAttribute(Qt.WA_DeleteOnClose, True)
            dialog.deleteLater()
            logger.debug("_on_color_dialog_finished: Dialog scheduled for deletion")
        except RuntimeError:
            logger.debug("_on_color_dialog_finished: Dialog already deleted")

        # Apply color change if user accepted
        if selected_color:
            # Create QColor from hex string for UI update
            color = QColor(selected_color)
            logger.debug("_on_color_dialog_finished: Updating UI")
            self._apply_color_change_immediate(color)

            # Update document via controller
            logger.debug(f"_on_color_dialog_finished: Queuing controller update: {token_name}={selected_color}")
            if self._controller:
                self._controller.queue_token_change(token_name, selected_color)
                logger.debug("_on_color_dialog_finished: Update queued, END")
            else:
                logger.warning("_on_color_dialog_finished: No controller set!")
        else:
            logger.debug("_on_color_dialog_finished: No color selected or dialog cancelled, END")

    def _on_color_changed_live(self, color: QColor):
        """Handle live color changes while dragging color picker.

        This provides instant visual feedback in the preview as the user
        explores different colors.

        Args:
            color: Current color from color picker
        """
        if not color.isValid():
            return

        # Apply directly - no deferred call to avoid lambda capture issues
        self._apply_color_change_immediate(color)

    def _apply_color_change_immediate(self, color: QColor):
        """Apply color change for live preview (no document update).

        Used during dragging to update UI only, without triggering document changes.

        Args:
            color: QColor to display
        """
        if not color.isValid():
            return

        hex_color = color.name()

        # Update UI only (no signal emission)
        self.token_value_label.setText(hex_color)
        self.color_swatch.setStyleSheet(
            f"background-color: {hex_color}; border: 2px solid gray;"
        )

        # Update color details
        self.rgb_label.setText(f"rgb({color.red()}, {color.green()}, {color.blue()})")
        self.hsl_label.setText(
            f"hsl({color.hslHue()}, {color.hslSaturation()}%, {color.lightness()}%)"
        )
        self.hex_label.setText(hex_color)

    # NOTE: _apply_color_change is no longer used with non-modal dialog approach
    # The _on_color_dialog_finished callback handles all updates directly
