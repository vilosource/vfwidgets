"""Font Family List Editor Widget - Theme Editor Component.

This module provides the FontFamilyListEditor for editing font family fallback lists
with drag-drop reordering and system font availability checking.

Phase 5: Font Family List Editing
"""

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFontDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..core.font_tokens import FontTokenRegistry
from ..core.theme import Theme
from ..errors import FontPropertyError
from ..logging import get_debug_logger
from .base import ThemedWidget

logger = get_debug_logger(__name__)


class FontFamilyListEditor(ThemedWidget, QWidget):
    """Editor for font family fallback lists with drag-drop reordering.

    This widget provides a list-based interface for editing font family lists
    with drag-drop reordering, add/remove buttons, and font availability indicators.

    Features:
    - Drag-drop reordering of font families
    - Add fonts via system font picker dialog
    - Remove fonts with validation (can't remove last generic family)
    - Font availability indicators (checkmark/X icons)
    - Font preview rendering in list items
    - Validation feedback with error messages
    - Real-time updates via signals

    Signals:
        families_changed(str, list): Emitted when family list changes (token_path, new_list)
    """

    # Signals
    families_changed = Signal(str, list)  # (token_path, new_family_list)

    # Generic font families (CSS standard)
    GENERIC_FAMILIES = {"monospace", "sans-serif", "serif", "cursive", "fantasy"}

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize font family list editor.

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

        logger.debug("FontFamilyListEditor initialized")

    def _setup_ui(self) -> None:
        """Set up user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Token label
        self._token_label = QLabel("No token selected")
        self._token_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        layout.addWidget(self._token_label)

        # Help text
        help_text = QLabel(
            "Drag to reorder font families. First available font is used.\n"
            "✓ = Font available on system, ✗ = Font not installed"
        )
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #888; font-size: 9pt; margin-bottom: 5px;")
        layout.addWidget(help_text)

        # Font family list (drag-drop enabled)
        self._family_list = QListWidget()
        self._family_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self._family_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self._family_list.setAlternatingRowColors(True)
        self._family_list.model().rowsMoved.connect(self._on_order_changed)
        layout.addWidget(self._family_list)

        # Button row
        button_layout = QHBoxLayout()

        # Add button (opens system font picker)
        self._add_button = QPushButton("Add Font...")
        self._add_button.clicked.connect(self._on_add_font)
        button_layout.addWidget(self._add_button)

        # Remove button
        self._remove_button = QPushButton("Remove Selected")
        self._remove_button.clicked.connect(self._on_remove_font)
        self._remove_button.setEnabled(False)  # Disabled until selection
        button_layout.addWidget(self._remove_button)

        layout.addLayout(button_layout)

        # Error label (hidden by default)
        self._error_label = QLabel()
        self._error_label.setStyleSheet("color: #FF6B6B; font-weight: bold;")
        self._error_label.setWordWrap(True)
        self._error_label.hide()
        layout.addWidget(self._error_label)

        layout.addStretch()

        # Connect selection change to update remove button state
        self._family_list.itemSelectionChanged.connect(self._on_selection_changed)

    def set_token(self, token_path: str, family_list: list[str], theme: Theme) -> None:
        """Set the font family list being edited.

        Args:
            token_path: Token path (e.g., "terminal.fontFamily")
            family_list: Current font family list
            theme: Theme to resolve from

        """
        self._current_token = token_path
        self._current_theme = theme
        self._updating = True  # Prevent signal emission during setup

        # Update token label
        self._token_label.setText(f"Editing: {token_path}")

        # Clear error
        self._clear_error()

        # Populate list
        self._populate_list(family_list)

        self._updating = False

        logger.debug(f"Set token: {token_path} = {family_list}")

    def _populate_list(self, families: list[str]) -> None:
        """Populate list with font families.

        Args:
            families: Font family list to display

        """
        self._family_list.clear()

        for family in families:
            item = QListWidgetItem()

            # Check if font is available on system
            is_available = FontTokenRegistry.get_available_font((family,)) == family

            # Set display text with availability indicator
            indicator = "✓" if is_available else "✗"
            item.setText(f"{indicator} {family}")

            # Set tooltip
            if is_available:
                item.setToolTip(f"Font '{family}' is available on this system")
            else:
                item.setToolTip(
                    f"Font '{family}' is NOT installed on this system. "
                    "This family will be skipped in the fallback chain."
                )

            # Style based on availability
            if is_available:
                # Green checkmark color
                item.setForeground(Qt.GlobalColor.darkGreen)
            else:
                # Gray/dimmed for unavailable fonts
                item.setForeground(Qt.GlobalColor.gray)

            # Store raw family name in data for later retrieval
            item.setData(Qt.ItemDataRole.UserRole, family)

            self._family_list.addItem(item)

    def _on_add_font(self) -> None:
        """Open font picker dialog to add a font."""
        # Show system font picker
        font_dialog = QFontDialog(self)
        font_dialog.setWindowTitle("Select Font Family to Add")

        if font_dialog.exec():
            selected_font: QFont = font_dialog.selectedFont()
            family = selected_font.family()

            # Check if already in list
            if self._is_family_in_list(family):
                QMessageBox.information(
                    self,
                    "Font Already Added",
                    f"Font family '{family}' is already in the list.",
                )
                return

            # Add to list
            current_families = self._get_current_families()
            current_families.append(family)

            # Repopulate list with new family
            self._populate_list(current_families)

            # Emit change
            self._validate_and_emit(current_families)

            logger.debug(f"Added font family: {family}")

    def _on_remove_font(self) -> None:
        """Remove selected font from list."""
        current_item = self._family_list.currentItem()
        if not current_item:
            return

        # Get raw family name from item data
        family = current_item.data(Qt.ItemDataRole.UserRole)

        # Check if it's the last generic family
        current_families = self._get_current_families()
        if self._is_last_generic_family(family, current_families):
            QMessageBox.warning(
                self,
                "Cannot Remove",
                f"Cannot remove '{family}' - it's the last generic family fallback.\n\n"
                "At least one generic family (monospace, sans-serif, serif, etc.) "
                "must remain in the list to ensure font rendering always works.",
            )
            return

        # Remove from list
        current_families.remove(family)

        # Repopulate list
        self._populate_list(current_families)

        # Emit change
        self._validate_and_emit(current_families)

        logger.debug(f"Removed font family: {family}")

    def _on_order_changed(self, parent, start, end, destination, row) -> None:
        """Handle drag-drop reordering.

        Args:
            parent: Parent model index
            start: Start row
            end: End row
            destination: Destination model index
            row: Target row

        """
        if self._updating:
            return

        # Get new order
        new_families = self._get_current_families()

        # Emit change
        self._validate_and_emit(new_families)

        logger.debug(f"Font families reordered: {new_families}")

    def _on_selection_changed(self) -> None:
        """Handle selection changes in list."""
        # Enable/disable remove button based on selection
        has_selection = self._family_list.currentItem() is not None
        self._remove_button.setEnabled(has_selection)

    def _get_current_families(self) -> list[str]:
        """Get current font family list from UI.

        Returns:
            List of font family names in current order

        """
        families = []
        for i in range(self._family_list.count()):
            item = self._family_list.item(i)
            # Get raw family name from item data
            family = item.data(Qt.ItemDataRole.UserRole)
            families.append(family)
        return families

    def _is_family_in_list(self, family: str) -> bool:
        """Check if font family is already in list.

        Args:
            family: Font family name to check

        Returns:
            True if family is in list

        """
        current_families = self._get_current_families()
        return family in current_families

    def _is_last_generic_family(self, family: str, family_list: list[str]) -> bool:
        """Check if this is the last generic family in the list.

        Args:
            family: Font family to check
            family_list: Current family list

        Returns:
            True if this is the last generic family

        """
        # Count generic families in list
        generic_count = sum(
            1 for f in family_list if f.lower() in self.GENERIC_FAMILIES
        )

        return generic_count == 1 and family.lower() in self.GENERIC_FAMILIES

    def _validate_and_emit(self, new_list: list[str]) -> None:
        """Validate font family list before emitting.

        Args:
            new_list: New font family list to validate

        """
        if not self._current_token or self._updating:
            return

        try:
            # Validate using Theme constructor
            # Create test theme with the new value
            test_fonts = dict(self._current_theme.fonts) if self._current_theme else {}
            test_fonts[self._current_token] = new_list

            # Validation happens in Theme __post_init__
            Theme(name="validation_test", fonts=test_fonts)

            # Clear error
            self._clear_error()

            # Emit change
            self.families_changed.emit(self._current_token, new_list)

            logger.debug(f"Font families changed: {self._current_token} = {new_list}")

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

    def get_current_families(self) -> list[str]:
        """Get current font family list.

        Returns:
            Current font family list

        """
        return self._get_current_families()
