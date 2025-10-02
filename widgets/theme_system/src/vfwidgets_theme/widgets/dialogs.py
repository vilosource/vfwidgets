"""Theme switching dialog components.

This module provides complete dialog solutions for theme switching:
- ThemePickerDialog: Modal dialog for theme selection with preview
- ThemeSettingsWidget: Embeddable widget for settings panels

Example:
    from vfwidgets_theme.widgets.dialogs import ThemePickerDialog

    # Show theme picker dialog
    dialog = ThemePickerDialog(preview_mode=True)
    if dialog.exec():
        print(f"Selected theme: {dialog.selected_theme}")

"""

from typing import Optional

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ..logging import get_debug_logger
from .application import ThemedApplication
from .helpers import ThemePreview
from .primitives import ThemeComboBox, ThemeListWidget

logger = get_debug_logger(__name__)


class ThemePickerDialog(QDialog):
    """Modal dialog for theme selection with live preview.

    This dialog provides a complete theme selection experience with:
    - List of available themes with metadata
    - Live preview mode (optional)
    - OK/Cancel buttons
    - Automatic theme restoration on cancel (in preview mode)

    Args:
        parent: Optional parent widget
        preview_mode: Enable live preview (default: True)
        title: Dialog title (default: "Select Theme")

    Example:
        >>> dialog = ThemePickerDialog(preview_mode=True)
        >>> if dialog.exec():
        ...     print(f"User selected: {dialog.selected_theme}")
        ... else:
        ...     print("User cancelled")

    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        preview_mode: bool = True,
        title: str = "Select Theme",
    ):
        """Initialize theme picker dialog."""
        super().__init__(parent)

        self._app = ThemedApplication.instance()
        self._preview_mode = preview_mode
        self._preview = ThemePreview() if preview_mode else None
        self._selected_theme: Optional[str] = None

        # Setup UI
        self.setWindowTitle(title)
        self.setModal(True)
        self._setup_ui()

        logger.debug(f"ThemePickerDialog created (preview_mode={preview_mode})")

    def _setup_ui(self) -> None:
        """Setup dialog UI."""
        layout = QVBoxLayout(self)

        # Add description label
        label = QLabel("Select a theme:")
        layout.addWidget(label)

        # Add theme list
        self._list_widget = ThemeListWidget()
        layout.addWidget(self._list_widget)

        # In preview mode, disconnect list widget's direct theme changing
        # and use our own preview handler instead
        if self._preview_mode and self._preview:
            # Disconnect the list widget's built-in theme changing
            self._list_widget.blockSignals(True)
            self._list_widget.currentItemChanged.disconnect()
            self._list_widget.blockSignals(False)

            # Connect our preview handler
            self._list_widget.currentItemChanged.connect(self._on_selection_changed)

        # Add button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Set reasonable size
        self.resize(400, 500)

    def _on_selection_changed(self, current, previous) -> None:
        """Handle theme selection change for preview."""
        if current and self._preview:
            theme_name = current.text()
            self._preview.preview(theme_name)
            logger.debug(f"Previewing theme: {theme_name}")

    def accept(self) -> None:
        """Accept dialog and apply selected theme."""
        current_item = self._list_widget.currentItem()
        if current_item:
            self._selected_theme = current_item.text()

            # Commit preview if in preview mode
            if self._preview:
                self._preview.commit()

            # Apply theme if not already applied
            if self._app and self._selected_theme:
                self._app.set_theme(self._selected_theme)

            logger.debug(f"Theme picker accepted: {self._selected_theme}")

        super().accept()

    def reject(self) -> None:
        """Reject dialog and restore original theme."""
        # Cancel preview if in preview mode
        if self._preview:
            self._preview.cancel()
            logger.debug("Theme picker cancelled, restored original theme")

        super().reject()

    @property
    def selected_theme(self) -> Optional[str]:
        """Get the selected theme name.

        Returns:
            Selected theme name, or None if cancelled

        Example:
            >>> dialog = ThemePickerDialog()
            >>> if dialog.exec():
            ...     print(dialog.selected_theme)

        """
        return self._selected_theme


class ThemeSettingsWidget(QWidget):
    """Embeddable widget for theme settings.

    This widget can be embedded in settings panels, preferences windows,
    or any other container. It provides theme selection without being modal.

    Args:
        parent: Optional parent widget
        widget_type: Type of selection widget ("combo", "list", "buttons")
        show_label: Show descriptive label (default: True)

    Example:
        >>> # Embed in settings dialog
        >>> settings_widget = ThemeSettingsWidget(widget_type="combo")
        >>> layout.addWidget(settings_widget)

    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        widget_type: str = "combo",
        show_label: bool = True,
    ):
        """Initialize theme settings widget."""
        super().__init__(parent)

        self._widget_type = widget_type
        self._show_label = show_label

        # Setup UI
        self._setup_ui()

        logger.debug(f"ThemeSettingsWidget created (type={widget_type})")

    def _setup_ui(self) -> None:
        """Setup widget UI."""
        layout = QVBoxLayout(self)

        # Add label if requested
        if self._show_label:
            label = QLabel("Theme:")
            layout.addWidget(label)

        # Add appropriate widget based on type
        if self._widget_type == "list":
            self._list_widget = ThemeListWidget()
            layout.addWidget(self._list_widget)
        else:
            # Default to combo
            self._combo = ThemeComboBox()
            layout.addWidget(self._combo)


if __name__ == "__main__":
    # Example usage
    import sys

    from vfwidgets_theme import ThemedApplication

    app = ThemedApplication(sys.argv)
    app.set_theme("dark")

    # Show picker dialog
    dialog = ThemePickerDialog(preview_mode=True)
    if dialog.exec():
        print(f"Selected theme: {dialog.selected_theme}")
    else:
        print("Cancelled")

    sys.exit(app.exec())
