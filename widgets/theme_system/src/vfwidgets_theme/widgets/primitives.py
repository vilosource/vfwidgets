"""Theme switching primitive widgets.

This module provides basic building blocks for theme switching UIs:
- ThemeComboBox: Dropdown selector for themes
- ThemeListWidget: List view with rich metadata display
- ThemeButtonGroup: Radio or toggle button group for themes

Example:
    from vfwidgets_theme.widgets.primitives import ThemeComboBox
    from vfwidgets_theme import ThemedApplication

    app = ThemedApplication(sys.argv)
    combo = ThemeComboBox()
    layout.addWidget(combo)  # Auto-syncs with app theme

"""

from typing import Literal, Optional

from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from ..logging import get_debug_logger
from .application import ThemedApplication
from .base import ThemedWidget

logger = get_debug_logger(__name__)


class ThemeComboBox(ThemedWidget, QComboBox):
    """A combo box that automatically syncs with application theme.

    This widget provides a dropdown for theme selection that:
    - Auto-populates from available themes
    - Syncs bidirectionally with app (UI ↔ App)
    - Updates when theme changes externally
    - Prevents infinite signal loops

    Args:
        parent: Optional parent widget

    Example:
        >>> app = ThemedApplication(sys.argv)
        >>> combo = ThemeComboBox()
        >>> layout.addWidget(combo)
        >>> # Combo automatically switches themes when selection changes

    """

    theme_config = {}  # No theme tokens needed for this widget

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._syncing = False  # Flag to prevent infinite loops

        # Get app instance
        self._app = ThemedApplication.instance()
        if self._app is None:
            logger.warning("ThemeComboBox created without ThemedApplication instance")
            return

        # Populate with available themes
        self._populate_themes()

        # Set current theme
        self._update_current_theme()

        # Connect signals
        self.currentTextChanged.connect(self._on_combo_changed)
        self._app.theme_changed.connect(self._on_app_theme_changed)

        logger.debug("ThemeComboBox initialized")

    def _populate_themes(self) -> None:
        """Populate combo box with available themes."""
        if self._app is None:
            return

        themes = self._app.get_available_themes()
        theme_names = [t.name if hasattr(t, 'name') else str(t) for t in themes]
        self.addItems(theme_names)
        logger.debug(f"Populated combo with {len(theme_names)} themes")

    def _update_current_theme(self) -> None:
        """Update combo to show current theme."""
        if self._app is None:
            return

        current_theme = self._app.current_theme_name
        if current_theme:
            self.blockSignals(True)
            self.setCurrentText(current_theme)
            self.blockSignals(False)

    def _on_combo_changed(self, theme_name: str) -> None:
        """Handle combo box selection change."""
        if self._syncing or not theme_name:
            return

        logger.debug(f"Combo changed to: {theme_name}")
        self._syncing = True
        try:
            if self._app:
                self._app.set_theme(theme_name)
        finally:
            self._syncing = False

    def _on_app_theme_changed(self, theme_name: str) -> None:
        """Update UI when app theme changes externally."""
        if self._syncing:
            return

        logger.debug(f"App theme changed to: {theme_name}, updating combo")
        self._syncing = True
        try:
            self.blockSignals(True)
            self.setCurrentText(theme_name)
            self.blockSignals(False)
        finally:
            self._syncing = False

    def on_theme_changed(self) -> None:
        """Called when theme changes (ThemedWidget protocol)."""
        # Already handled by _on_app_theme_changed
        pass


class ThemeListWidget(ThemedWidget, QListWidget):
    """A list widget that displays themes with rich metadata.

    This widget provides a list view for theme selection that:
    - Auto-populates from available themes
    - Displays theme metadata (description, type, etc.)
    - Syncs bidirectionally with app
    - Shows current theme as selected

    Args:
        parent: Optional parent widget

    Example:
        >>> app = ThemedApplication(sys.argv)
        >>> list_widget = ThemeListWidget()
        >>> layout.addWidget(list_widget)

    """

    theme_config = {}

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._syncing = False

        # Get app instance
        self._app = ThemedApplication.instance()
        if self._app is None:
            logger.warning("ThemeListWidget created without ThemedApplication instance")
            return

        # Populate with themes
        self._populate_themes()

        # Set current theme
        self._update_current_theme()

        # Connect signals
        self.currentItemChanged.connect(self._on_selection_changed)
        self._app.theme_changed.connect(self._on_app_theme_changed)

        logger.debug("ThemeListWidget initialized")

    def _populate_themes(self) -> None:
        """Populate list with available themes."""
        if self._app is None:
            return

        themes_info = self._app.get_all_theme_info()

        for theme_name, theme_info in themes_info.items():
            item = QListWidgetItem(theme_name)

            # Add tooltip with metadata
            tooltip = f"{theme_info.display_name}\n{theme_info.description}"
            if theme_info.type:
                tooltip += f"\nType: {theme_info.type}"
            item.setToolTip(tooltip)

            self.addItem(item)

        logger.debug(f"Populated list with {len(themes_info)} themes")

    def _update_current_theme(self) -> None:
        """Update list to show current theme selected."""
        if self._app is None:
            return

        current_theme = self._app.current_theme_name
        if not current_theme:
            return

        # Find and select matching item
        for i in range(self.count()):
            item = self.item(i)
            if item.text() == current_theme:
                self.blockSignals(True)
                self.setCurrentItem(item)
                self.blockSignals(False)
                break

    def _on_selection_changed(self, current: Optional[QListWidgetItem],
                             previous: Optional[QListWidgetItem]) -> None:
        """Handle selection change."""
        if self._syncing or current is None:
            return

        theme_name = current.text()
        logger.debug(f"List selection changed to: {theme_name}")

        self._syncing = True
        try:
            if self._app:
                self._app.set_theme(theme_name)
        finally:
            self._syncing = False

    def _on_app_theme_changed(self, theme_name: str) -> None:
        """Update UI when app theme changes externally."""
        if self._syncing:
            return

        logger.debug(f"App theme changed to: {theme_name}, updating list")
        self._syncing = True
        try:
            # Find and select matching item
            for i in range(self.count()):
                item = self.item(i)
                if item.text() == theme_name:
                    self.blockSignals(True)
                    self.setCurrentItem(item)
                    self.blockSignals(False)
                    break
        finally:
            self._syncing = False

    def on_theme_changed(self) -> None:
        """Called when theme changes (ThemedWidget protocol)."""
        # Already handled by _on_app_theme_changed
        pass


class ThemeButtonGroup(ThemedWidget, QWidget):
    """A button group for theme selection (radio or toggle mode).

    This widget provides a button group for theme selection that:
    - Creates buttons for available themes
    - Supports radio button or toggle button modes
    - Syncs bidirectionally with app
    - Shows current theme as checked

    Args:
        parent: Optional parent widget
        mode: Button mode - "radio" for radio buttons, "toggle" for toggle buttons
        orientation: Layout orientation - "horizontal" or "vertical"

    Example:
        >>> app = ThemedApplication(sys.argv)
        >>> button_group = ThemeButtonGroup(mode="radio", orientation="horizontal")
        >>> layout.addWidget(button_group)

    """

    theme_config = {}

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        mode: Literal["radio", "toggle"] = "radio",
        orientation: Literal["horizontal", "vertical"] = "horizontal",
    ):
        super().__init__(parent)
        self._syncing = False
        self._mode = mode

        # Get app instance
        self._app = ThemedApplication.instance()
        if self._app is None:
            logger.warning("ThemeButtonGroup created without ThemedApplication instance")
            return

        # Create layout
        if orientation == "horizontal":
            self._layout = QHBoxLayout(self)
        else:
            self._layout = QVBoxLayout(self)

        self.setLayout(self._layout)

        # Create button group for mutual exclusivity
        self._button_group = QButtonGroup(self)
        self._button_group.setExclusive(True)

        # Create buttons
        self._create_buttons()

        # Set current theme
        self._update_current_theme()

        # Connect signals
        self._button_group.buttonClicked.connect(self._on_button_clicked)
        self._app.theme_changed.connect(self._on_app_theme_changed)

        logger.debug(f"ThemeButtonGroup initialized in {mode} mode")

    def _create_buttons(self) -> None:
        """Create buttons for available themes."""
        if self._app is None:
            return

        themes_info = self._app.get_all_theme_info()

        for theme_name, theme_info in themes_info.items():
            if self._mode == "radio":
                button = QRadioButton(theme_name)
            else:
                button = QPushButton(theme_name)
                button.setCheckable(True)

            # Add tooltip
            tooltip = f"{theme_info.display_name}\n{theme_info.description}"
            button.setToolTip(tooltip)

            # Store theme name
            button.setProperty("theme_name", theme_name)

            # Add to layout and group
            self._layout.addWidget(button)
            self._button_group.addButton(button)

        logger.debug(f"Created {len(themes_info)} theme buttons")

    def _update_current_theme(self) -> None:
        """Update buttons to show current theme checked."""
        if self._app is None:
            return

        current_theme = self._app.current_theme_name
        if not current_theme:
            return

        # Find and check matching button
        for button in self._button_group.buttons():
            theme_name = button.property("theme_name")
            if theme_name == current_theme:
                button.blockSignals(True)
                button.setChecked(True)
                button.blockSignals(False)
                break

    def _on_button_clicked(self, button) -> None:
        """Handle button click."""
        if self._syncing:
            return

        theme_name = button.property("theme_name")
        logger.debug(f"Button clicked for theme: {theme_name}")

        self._syncing = True
        try:
            if self._app:
                self._app.set_theme(theme_name)
        finally:
            self._syncing = False

    def _on_app_theme_changed(self, theme_name: str) -> None:
        """Update UI when app theme changes externally."""
        if self._syncing:
            return

        logger.debug(f"App theme changed to: {theme_name}, updating buttons")
        self._syncing = True
        try:
            # Find and check matching button
            for button in self._button_group.buttons():
                btn_theme = button.property("theme_name")
                button.blockSignals(True)
                button.setChecked(btn_theme == theme_name)
                button.blockSignals(False)
        finally:
            self._syncing = False

    def on_theme_changed(self) -> None:
        """Called when theme changes (ThemedWidget protocol)."""
        # Already handled by _on_app_theme_changed
        pass
