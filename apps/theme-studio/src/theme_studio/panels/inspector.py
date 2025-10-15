"""Inspector Panel - Right panel for token details."""

import logging

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QCursor
from PySide6.QtWidgets import (
    QColorDialog,
    QComboBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QLabel,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from vfwidgets_theme.core.theme import Theme
from vfwidgets_theme.core.tokens import ColorTokenRegistry

from ..validators.metadata_validator import MetadataValidator
from ..validators.token_validator import TokenValidator

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
        self._current_theme = None  # Current theme for font editors
        self._color_dialog = None  # Keep reference to prevent premature deletion
        self._setup_ui()
        self._setup_font_editors()

    def set_controller(self, controller) -> None:
        """Set the theme controller.

        Args:
            controller: ThemeController instance
        """
        self._controller = controller

    def _setup_font_editors(self):
        """Setup font editing widgets from vfwidgets_theme."""
        try:
            from vfwidgets_theme.widgets import (
                FontFamilyListEditor,
                FontPropertyEditorWidget,
            )

            # Create font editors with self as parent (CRITICAL!)
            self._font_property_editor = FontPropertyEditorWidget(self)
            self._font_family_editor = FontFamilyListEditor(self)

            # Connect signals
            self._font_property_editor.property_changed.connect(self._on_font_property_changed)
            self._font_family_editor.families_changed.connect(self._on_font_families_changed)

            # Hide initially (will be added to layout when needed)
            self._font_property_editor.hide()
            self._font_family_editor.hide()

        except ImportError:
            logger.warning("Font editing widgets not available")
            self._font_property_editor = None
            self._font_family_editor = None

    def _setup_metadata_section(self, layout: QVBoxLayout):
        """Setup theme metadata section at top of inspector.

        Args:
            layout: Parent layout to add section to
        """
        # Create collapsible group box
        self.metadata_group = QGroupBox("Theme Properties")
        self.metadata_group.setCheckable(True)
        self.metadata_group.setChecked(True)  # Expanded by default

        form_layout = QFormLayout(self.metadata_group)
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        # Name field (required, validated)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Theme Name")
        self.name_input.textChanged.connect(self._on_name_changed)
        form_layout.addRow("Name:", self.name_input)

        self.name_error_label = QLabel()
        self.name_error_label.setStyleSheet("color: #d32f2f; font-size: 11px; padding: 2px;")
        self.name_error_label.setWordWrap(True)
        self.name_error_label.hide()
        form_layout.addRow("", self.name_error_label)

        # Version field (required, validated)
        self.version_input = QLineEdit()
        self.version_input.setPlaceholderText("1.0.0")
        self.version_input.textChanged.connect(self._on_version_changed)
        form_layout.addRow("Version:", self.version_input)

        self.version_error_label = QLabel()
        self.version_error_label.setStyleSheet("color: #d32f2f; font-size: 11px; padding: 2px;")
        self.version_error_label.setWordWrap(True)
        self.version_error_label.hide()
        form_layout.addRow("", self.version_error_label)

        # Type field (dropdown, always valid)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["dark", "light", "high-contrast"])
        self.type_combo.currentTextChanged.connect(self._on_type_changed)
        form_layout.addRow("Type:", self.type_combo)

        # Author field (optional)
        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("Optional")
        self.author_input.textChanged.connect(self._on_author_changed)
        form_layout.addRow("Author:", self.author_input)

        # Description field (optional, multiline)
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Optional - Describe your theme...")
        self.description_input.setMaximumHeight(100)
        self.description_input.textChanged.connect(self._on_description_changed)
        form_layout.addRow("Description:", self.description_input)

        layout.addWidget(self.metadata_group)

    def _setup_ui(self):
        """Setup UI for token inspection."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(10)

        # Theme Properties Section (metadata) - at the TOP
        self._setup_metadata_section(layout)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

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

        # Text input for direct hex color entry
        self.color_input_label = QLabel("Or enter hex color:")
        self.color_input_label.setStyleSheet("font-size: 11px; margin-top: 8px;")
        self.color_input_label.hide()
        layout.addWidget(self.color_input_label)

        self.color_input = QLineEdit()
        self.color_input.setPlaceholderText("#RRGGBB or color name")
        self.color_input.textChanged.connect(self._on_color_input_changed)
        self.color_input.returnPressed.connect(self._on_color_input_submitted)
        self.color_input.hide()
        layout.addWidget(self.color_input)

        # Validation error label
        self.validation_error_label = QLabel()
        self.validation_error_label.setStyleSheet(
            "color: #d32f2f; font-size: 11px; padding: 4px; background: #ffebee; "
            "border: 1px solid #ef9a9a; border-radius: 3px;"
        )
        self.validation_error_label.setWordWrap(True)
        self.validation_error_label.hide()
        layout.addWidget(self.validation_error_label)

        # Token info group
        self.info_group = QGroupBox("Token Information")
        info_layout = QFormLayout(self.info_group)

        self.token_name_label = QLabel("-")
        self.token_name_label.setWordWrap(True)
        info_layout.addRow("Name:", self.token_name_label)

        # Clickable value display (opens color dialog)
        self.token_value_label = QLabel("-")
        self.token_value_label.setWordWrap(True)
        self.token_value_label.setStyleSheet(
            "padding: 4px; border: 1px solid gray; background: white;"
        )
        self.token_value_label.setCursor(QCursor(Qt.PointingHandCursor))
        self.token_value_label.mousePressEvent = lambda e: self._on_value_clicked()
        info_layout.addRow("Value:", self.token_value_label)

        self.token_category_label = QLabel("-")
        info_layout.addRow("Category:", self.token_category_label)

        self.token_description_label = QLabel("-")
        self.token_description_label.setWordWrap(True)
        info_layout.addRow("Description:", self.token_description_label)

        # Default value display (NEW)
        self.token_default_label = QLabel("-")
        self.token_default_label.setWordWrap(True)
        self.token_default_label.setStyleSheet("color: #666; font-style: italic;")
        info_layout.addRow("Default:", self.token_default_label)

        self.info_group.hide()  # Hidden until token selected
        layout.addWidget(self.info_group)

        # Reset to Default button (NEW)
        from PySide6.QtWidgets import QHBoxLayout, QPushButton
        reset_button_layout = QHBoxLayout()
        self.reset_button = QPushButton("Reset to Default")
        self.reset_button.setToolTip("Reset this token to its default value")
        self.reset_button.clicked.connect(self._on_reset_to_default)
        self.reset_button.hide()  # Hidden until token selected
        reset_button_layout.addStretch()
        reset_button_layout.addWidget(self.reset_button)
        reset_button_layout.addStretch()
        layout.addLayout(reset_button_layout)

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

        # Font editing widgets (added after setup_font_editors creates them)
        # These will be added dynamically when needed

        layout.addStretch()

    def set_token(self, token_name: str, token_value: str):
        """Set the token to inspect.

        Args:
            token_name: Token name (e.g., "button.background")
            token_value: Current token value
        """
        self._current_token = token_name
        self._current_value = token_value
        self._current_theme = None  # Clear theme (this is a color token, not font)

        # Update title
        self.title_label.setText(token_name)

        # Get token metadata from registry
        token_info = ColorTokenRegistry.get_token(token_name)

        # Show info group
        self.info_group.show()

        # Update token info with badge if modified from default
        token_display_name = token_name
        if token_info and token_value:
            theme_type = "dark"
            if self._controller and hasattr(self._controller, '_document'):
                theme_type = self._controller._document.theme.type
            default_value = token_info.default_dark if theme_type == "dark" else token_info.default_light
            if token_value != default_value:
                token_display_name = f"{token_name} ✓"  # Checkmark indicates customized

        self.token_name_label.setText(token_display_name)
        display_value = token_value if token_value else "(click to set)"
        self.token_value_label.setText(display_value)
        self.token_category_label.setText(token_info.category.value if token_info else "unknown")
        self.token_description_label.setText(
            token_info.description if token_info else "No description"
        )

        # Show default value for color tokens (theme-specific)
        if token_info:
            # Get theme type from document (default to "dark" if not available)
            theme_type = "dark"  # Will be improved when we have document reference
            if self._controller and hasattr(self._controller, '_document'):
                theme_type = self._controller._document.theme.type

            default_value = token_info.default_dark if theme_type == "dark" else token_info.default_light
            self.token_default_label.setText(default_value)

            # Enable reset button only if current value differs from default
            if token_value and token_value != default_value:
                self.reset_button.show()
                self.reset_button.setEnabled(True)
            else:
                self.reset_button.show()
                self.reset_button.setEnabled(False)
        else:
            self.token_default_label.setText("(no default)")
            self.reset_button.hide()

        # Show the Value row for color tokens (hidden for font tokens)
        self.token_value_label.show()
        # Also show the "Value:" label in the form layout
        info_layout = self.info_group.layout()
        value_label_item = info_layout.labelForField(self.token_value_label)
        if value_label_item:
            value_label_item.show()

        # Restore clickable styling for color tokens
        self.token_value_label.setStyleSheet(
            "padding: 4px; border: 1px solid gray; background: white;"
        )
        self.token_value_label.setCursor(QCursor(Qt.PointingHandCursor))

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

                    # Show text input for direct color entry
                    self.color_input_label.show()
                    self.color_input.show()
                    # Populate with current value (suppress textChanged signal)
                    self.color_input.blockSignals(True)
                    self.color_input.setText(token_value)
                    self.color_input.blockSignals(False)
                    # Hide validation error on token change
                    self.validation_error_label.hide()

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
            except Exception:
                self._hide_color_details()
        else:
            self._hide_color_details()

    def _hide_color_details(self):
        """Hide color-specific details."""
        self.color_swatch.hide()
        self.hint_label.hide()
        self.color_input_label.hide()
        self.color_input.hide()
        self.validation_error_label.hide()
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
        self.token_default_label.setText("-")  # NEW
        self.rgb_label.setText("-")
        self.hsl_label.setText("-")
        self.hex_label.setText("-")
        self.color_input.clear()
        self.validation_error_label.hide()
        self.info_group.hide()
        self.color_group.hide()
        self.color_swatch.hide()
        self.hint_label.hide()
        self.color_input_label.hide()
        self.color_input.hide()
        self.reset_button.hide()  # NEW
        self._hide_font_editors()

    def set_font_token(self, token_path: str, token_value, theme: Theme):
        """Set a font token to inspect and edit.

        Args:
            token_path: Font token path (e.g., "terminal.fontSize")
            token_value: Current token value (list, int, float, or str)
            theme: Current theme for font editors
        """
        self._current_token = token_path
        self._current_value = token_value
        self._current_theme = theme

        # Update title
        self.title_label.setText(token_path)

        # Hide color editing UI
        self._hide_color_details()

        # Show info group
        self.info_group.show()

        # Update token info with badge if modified from default
        try:
            from ..metadata import FontTokenMetadataRegistry
            font_token_info = FontTokenMetadataRegistry.get_token(token_path)
            token_display_name = token_path
            if font_token_info and token_value is not None:
                if token_value != font_token_info.default_value:
                    token_display_name = f"{token_path} ✓"  # Checkmark indicates customized
        except (ImportError, AttributeError):
            token_display_name = token_path

        self.token_name_label.setText(token_display_name)
        if token_value is not None:
            if isinstance(token_value, list):
                display_value = ", ".join(token_value[:2])
                if len(token_value) > 2:
                    display_value += ", ..."
            else:
                display_value = str(token_value)
        else:
            display_value = "(not set)"

        # Hide the Value row for font tokens (it's redundant - editor shows the value)
        self.token_value_label.hide()
        # Also hide the "Value:" label in the form layout
        info_layout = self.info_group.layout()
        value_label_item = info_layout.labelForField(self.token_value_label)
        if value_label_item:
            value_label_item.hide()

        # Get font token metadata for category, description, and default value
        try:
            from ..metadata import FontTokenMetadataRegistry
            font_token_info = FontTokenMetadataRegistry.get_token(token_path)
            if font_token_info:
                self.token_category_label.setText(font_token_info.category.value.upper())
                self.token_description_label.setText(font_token_info.description)

                # Show default value
                if font_token_info.default_value is not None:
                    if isinstance(font_token_info.default_value, list):
                        default_display = ", ".join(font_token_info.default_value[:2])
                        if len(font_token_info.default_value) > 2:
                            default_display += ", ..."
                    else:
                        default_display = str(font_token_info.default_value)
                    self.token_default_label.setText(default_display)
                else:
                    # None means hierarchical fallback - show that info
                    self.token_default_label.setText("(uses hierarchical fallback)")

                # Enable reset button only if current value differs from default
                if token_value is not None and token_value != font_token_info.default_value:
                    self.reset_button.show()
                    self.reset_button.setEnabled(True)
                else:
                    self.reset_button.show()
                    self.reset_button.setEnabled(False)
            else:
                self.token_category_label.setText("FONT")
                self.token_description_label.setText("Font token")
                self.token_default_label.setText("(no default)")
                self.reset_button.hide()
        except (ImportError, AttributeError):
            self.token_category_label.setText("FONT")
            self.token_description_label.setText("Font token")
            self.token_default_label.setText("(no default)")
            self.reset_button.hide()

        # Determine which font editor to show
        if self._is_font_family_token(token_path):
            # Show font family editor
            self._show_font_family_editor(token_path, token_value, theme)
        else:
            # Show font property editor (size, weight, lineHeight, letterSpacing)
            self._show_font_property_editor(token_path, token_value, theme)

    def _is_font_family_token(self, token_path: str) -> bool:
        """Check if token is a font family token."""
        return (
            "Family" in token_path
            or token_path in ("fonts.mono", "fonts.ui", "fonts.serif")
        )

    def _show_font_property_editor(self, token_path: str, value, theme: Theme):
        """Show font property editor."""
        if not self._font_property_editor:
            return

        # Hide family editor
        if self._font_family_editor:
            self._font_family_editor.hide()

        # Add to layout if not already added
        layout = self.layout()
        if layout.indexOf(self._font_property_editor) == -1:
            # Insert before stretch (last item)
            index = layout.count() - 1
            layout.insertWidget(index, self._font_property_editor)

        self._font_property_editor.set_token(token_path, value, theme)
        self._font_property_editor.show()

    def _show_font_family_editor(self, token_path: str, value, theme: Theme):
        """Show font family list editor."""
        if not self._font_family_editor:
            return

        # Hide property editor
        if self._font_property_editor:
            self._font_property_editor.hide()

        # Add to layout if not already added
        layout = self.layout()
        if layout.indexOf(self._font_family_editor) == -1:
            # Insert before stretch (last item)
            index = layout.count() - 1
            layout.insertWidget(index, self._font_family_editor)

        # Ensure value is a list
        if isinstance(value, str):
            value = [value]
        elif value is None:
            value = []

        self._font_family_editor.set_token(token_path, value, theme)
        self._font_family_editor.show()

    def _hide_font_editors(self):
        """Hide all font editing widgets."""
        if self._font_property_editor:
            self._font_property_editor.hide()
        if self._font_family_editor:
            self._font_family_editor.hide()

    def _on_font_property_changed(self, token_path: str, new_value):
        """Handle font property change from editor."""
        if self._controller:
            self._controller.queue_font_change(token_path, new_value)

    def _on_font_families_changed(self, token_path: str, new_families: list[str]):
        """Handle font family list change from editor."""
        if self._controller:
            self._controller.queue_font_change(token_path, new_families)

    def _on_value_clicked(self):
        """Handle value label click - opens color picker for color tokens only.

        For font tokens, the dedicated font editors are already shown below,
        so clicking the value label does nothing.

        Dialog closes automatically when:
        - User clicks a color in the picker
        - User types hex and presses Enter
        - User clicks OK/Apply
        """
        if not self._current_token:
            return

        # Only open color picker if this is a color token (not a font token)
        # Font tokens have dedicated editors already visible
        if self._current_theme is not None:
            # If _current_theme is set, this is a font token, so don't open color picker
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
        logger.debug(
            f"_on_color_swatch_clicked: Opening color dialog for token={token_name}, color={current_value}"
        )

        # Use Qt's static method - Qt manages everything
        # This is the recommended way for simple color picking
        selected_color = QColorDialog.getColor(
            initial_color,
            self,
            f"Pick Color: {token_name}",
            QColorDialog.ShowAlphaChannel | QColorDialog.DontUseNativeDialog,
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
            logger.debug(
                f"_on_color_swatch_clicked: Queuing controller update: {token_name}={hex_color}"
            )
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
                logger.warning(
                    "_on_color_dialog_finished: Dialog already deleted, cannot get color"
                )

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
            logger.debug(
                f"_on_color_dialog_finished: Queuing controller update: {token_name}={selected_color}"
            )
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
        self.color_swatch.setStyleSheet(f"background-color: {hex_color}; border: 2px solid gray;")

        # Update text input (suppress textChanged signal to avoid validation feedback loop)
        self.color_input.blockSignals(True)
        self.color_input.setText(hex_color)
        self.color_input.blockSignals(False)
        # Hide validation error when color picker is used
        self.validation_error_label.hide()

        # Update color details
        self.rgb_label.setText(f"rgb({color.red()}, {color.green()}, {color.blue()})")
        self.hsl_label.setText(
            f"hsl({color.hslHue()}, {color.hslSaturation()}%, {color.lightness()}%)"
        )
        self.hex_label.setText(hex_color)

    # NOTE: _apply_color_change is no longer used with non-modal dialog approach
    # The _on_color_dialog_finished callback handles all updates directly

    def _on_color_input_changed(self, text: str):
        """Handle text input change - validate color format as user types.

        Args:
            text: Current text in input field
        """
        # Validate the color
        is_valid, error_msg = TokenValidator.validate_color(text)

        if is_valid:
            # Valid color - hide error, update visual feedback
            self.validation_error_label.hide()

            # Update color swatch preview if it's a valid color
            if text.strip():  # Don't preview empty string
                try:
                    color = QColor(text)
                    if color.isValid():
                        self.color_swatch.setStyleSheet(
                            f"background-color: {text}; border: 2px solid gray;"
                        )
                except Exception:
                    pass
        else:
            # Invalid color - show error
            self.validation_error_label.setText(error_msg)
            self.validation_error_label.show()

    def _on_color_input_submitted(self):
        """Handle Enter key press in text input - apply valid color."""
        text = self.color_input.text().strip()

        # Validate
        is_valid, error_msg = TokenValidator.validate_color(text)

        if not is_valid:
            # Show error and don't apply
            self.validation_error_label.setText(error_msg)
            self.validation_error_label.show()
            return

        # Valid color - apply it
        if not self._current_token:
            return

        try:
            color = QColor(text)
            if color.isValid():
                hex_color = color.name()

                # Update UI
                self._apply_color_change_immediate(color)
                self._current_value = hex_color

                # Update document via controller
                if self._controller:
                    self._controller.queue_token_change(self._current_token, hex_color)
                    logger.debug(
                        f"_on_color_input_submitted: Applied color {hex_color} to {self._current_token}"
                    )
        except Exception as e:
            logger.error(f"_on_color_input_submitted: Error applying color: {e}")
            self.validation_error_label.setText(f"Error applying color: {e}")
            self.validation_error_label.show()

    # ==================== METADATA EDITING METHODS ====================

    def _on_name_changed(self, text: str):
        """Handle theme name change.

        Args:
            text: New name text
        """
        # Validate
        is_valid, error_msg = MetadataValidator.validate_name(text)

        if is_valid:
            self.name_error_label.hide()
            # Queue change via controller
            if self._controller:
                self._controller.queue_metadata_change("name", text)
        else:
            # Show error (but don't block - validation is for user feedback only)
            self.name_error_label.setText(error_msg)
            self.name_error_label.show()

    def _on_version_changed(self, text: str):
        """Handle theme version change.

        Args:
            text: New version text
        """
        # Validate
        is_valid, error_msg = MetadataValidator.validate_version(text)

        if is_valid:
            self.version_error_label.hide()
            # Queue change via controller
            if self._controller:
                self._controller.queue_metadata_change("version", text)
        else:
            # Show error (but don't block - validation is for user feedback only)
            self.version_error_label.setText(error_msg)
            self.version_error_label.show()

    def _on_type_changed(self, text: str):
        """Handle theme type change.

        Args:
            text: New type value (dark, light, high-contrast)
        """
        # Type is always valid (dropdown enforces valid values)
        if self._controller:
            self._controller.queue_metadata_change("type", text)

    def _on_author_changed(self):
        """Handle author field change."""
        text = self.author_input.text()
        if self._controller:
            self._controller.queue_metadata_change("author", text)

    def _on_description_changed(self):
        """Handle description field change."""
        text = self.description_input.toPlainText()
        if self._controller:
            self._controller.queue_metadata_change("description", text)

    def populate_metadata_fields(self, document):
        """Populate metadata fields from document.

        Args:
            document: ThemeDocument to read metadata from
        """
        # Block signals to avoid triggering change handlers
        self.name_input.blockSignals(True)
        self.version_input.blockSignals(True)
        self.type_combo.blockSignals(True)
        self.author_input.blockSignals(True)
        self.description_input.blockSignals(True)

        # Populate fields
        self.name_input.setText(document.theme.name)
        self.version_input.setText(document.theme.version)

        # Set type combo box
        type_index = self.type_combo.findText(document.theme.type)
        if type_index >= 0:
            self.type_combo.setCurrentIndex(type_index)

        # Populate metadata fields
        author = document.get_metadata_field("author", "")
        description = document.get_metadata_field("description", "")
        self.author_input.setText(author)
        self.description_input.setPlainText(description)

        # Hide error labels
        self.name_error_label.hide()
        self.version_error_label.hide()

        # Restore signals
        self.name_input.blockSignals(False)
        self.version_input.blockSignals(False)
        self.type_combo.blockSignals(False)
        self.author_input.blockSignals(False)
        self.description_input.blockSignals(False)

    def on_metadata_changed(self, field: str, value: str):
        """Handle metadata change from document (e.g., undo/redo).

        Args:
            field: Metadata field name (name, version, type, author, description)
            value: New field value
        """
        # Block signals to avoid triggering change handlers
        if field == "name":
            self.name_input.blockSignals(True)
            self.name_input.setText(value)
            self.name_input.blockSignals(False)
            self.name_error_label.hide()
        elif field == "version":
            self.version_input.blockSignals(True)
            self.version_input.setText(value)
            self.version_input.blockSignals(False)
            self.version_error_label.hide()
        elif field == "type":
            self.type_combo.blockSignals(True)
            type_index = self.type_combo.findText(value)
            if type_index >= 0:
                self.type_combo.setCurrentIndex(type_index)
            self.type_combo.blockSignals(False)
        elif field == "author":
            self.author_input.blockSignals(True)
            self.author_input.setText(value)
            self.author_input.blockSignals(False)
        elif field == "description":
            self.description_input.blockSignals(True)
            self.description_input.setPlainText(value)
            self.description_input.blockSignals(False)

    def focus_metadata(self):
        """Focus and expand the metadata section (for Ctrl+I shortcut)."""
        # Expand section if collapsed
        if not self.metadata_group.isChecked():
            self.metadata_group.setChecked(True)

        # Focus name field
        self.name_input.setFocus()
        self.name_input.selectAll()

    # ==================== RESET TO DEFAULT METHOD ====================

    def _on_reset_to_default(self):
        """Handle Reset to Default button click."""
        if not self._current_token:
            return

        # Determine if this is a color token or font token
        if self._current_theme is not None:
            # Font token - get default from FontTokenMetadataRegistry
            self._reset_font_token_to_default()
        else:
            # Color token - get default from ColorTokenRegistry
            self._reset_color_token_to_default()

    def _reset_color_token_to_default(self):
        """Reset color token to its default value."""
        from vfwidgets_theme.core.tokens import ColorTokenRegistry

        token_info = ColorTokenRegistry.get_token(self._current_token)
        if not token_info:
            return

        # Get theme type to determine which default to use
        theme_type = "dark"
        if self._controller and hasattr(self._controller, '_document'):
            theme_type = self._controller._document.theme.type

        default_value = token_info.default_dark if theme_type == "dark" else token_info.default_light

        # Apply the default value via controller
        if self._controller:
            self._controller.queue_token_change(self._current_token, default_value)
            logger.debug(
                f"Reset color token {self._current_token} to default: {default_value}"
            )

            # Update UI immediately
            color = QColor(default_value)
            if color.isValid():
                self._apply_color_change_immediate(color)
                self._current_value = default_value

                # Disable reset button (now at default)
                self.reset_button.setEnabled(False)

    def _reset_font_token_to_default(self):
        """Reset font token to its default value."""
        from ..metadata import FontTokenMetadataRegistry

        font_token_info = FontTokenMetadataRegistry.get_token(self._current_token)
        if not font_token_info:
            return

        default_value = font_token_info.default_value

        # Apply the default value via controller
        if self._controller:
            self._controller.queue_font_change(self._current_token, default_value)
            logger.debug(
                f"Reset font token {self._current_token} to default: {default_value}"
            )

            # Update the font editor widget with the new default value
            self._current_value = default_value
            if self._is_font_family_token(self._current_token):
                if self._font_family_editor and self._current_theme:
                    self._font_family_editor.set_token(
                        self._current_token, default_value or [], self._current_theme
                    )
            else:
                if self._font_property_editor and self._current_theme:
                    self._font_property_editor.set_token(
                        self._current_token, default_value, self._current_theme
                    )

            # Disable reset button (now at default)
            self.reset_button.setEnabled(False)
