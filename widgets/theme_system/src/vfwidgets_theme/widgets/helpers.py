"""Theme switching helper functions.

This module provides one-liner helper functions for common theme switching patterns:
- add_theme_menu(): Add a theme selection menu to a window
- add_theme_toolbar(): Add a theme selection toolbar to a window
- ThemePreview: Preview themes with commit/cancel capability
- ThemeSettings: Persistent theme preferences using QSettings

Example:
    from vfwidgets_theme.widgets.helpers import add_theme_menu, add_theme_toolbar
    from vfwidgets_theme import ThemedApplication

    app = ThemedApplication(sys.argv)
    window = QMainWindow()

    # One-liner to add theme menu
    add_theme_menu(window)

    # One-liner to add theme toolbar
    add_theme_toolbar(window)

"""

from typing import Optional

from PySide6.QtCore import QSettings
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import QMainWindow, QMenu, QToolBar

from ..logging import get_debug_logger
from .application import ThemedApplication
from .primitives import ThemeComboBox

logger = get_debug_logger(__name__)


def add_theme_menu(
    window: QMainWindow, menu_name: str = "Theme", parent_menu: Optional[QMenu] = None
) -> QMenu:
    """Add a theme selection menu to a window.

    This is a one-liner helper that adds a fully functional theme switching
    menu to your application's menu bar.

    Args:
        window: The main window to add the menu to
        menu_name: Name of the menu (default: "Theme")
        parent_menu: Optional parent menu to nest under (if None, adds to menubar)

    Returns:
        The created theme menu

    Example:
        >>> window = QMainWindow()
        >>> add_theme_menu(window)  # Adds "Theme" menu to menubar
        >>> add_theme_menu(window, "Appearance")  # Custom name

    """
    app = ThemedApplication.instance()
    if app is None:
        logger.warning("add_theme_menu called without ThemedApplication instance")
        return None

    # Get or create menubar
    menubar = window.menuBar()

    # Create theme menu
    if parent_menu:
        theme_menu = parent_menu.addMenu(menu_name)
    else:
        theme_menu = menubar.addMenu(menu_name)

    # Create action group for mutual exclusivity
    # Store as window property to prevent garbage collection
    action_group = QActionGroup(theme_menu)
    action_group.setExclusive(True)

    # Get available themes
    themes_info = app.get_all_theme_info()
    current_theme = app.current_theme_name

    # Add action for each theme
    for theme_name, theme_info in themes_info.items():
        action = QAction(theme_info.display_name, theme_menu)
        action.setCheckable(True)
        action.setData(theme_name)

        # Set tooltip
        tooltip = f"{theme_info.description}"
        if theme_info.type:
            tooltip += f"\nType: {theme_info.type}"
        action.setToolTip(tooltip)

        # Check if current theme
        if theme_name == current_theme:
            action.setChecked(True)

        # Connect to theme switching
        action.triggered.connect(lambda checked, name=theme_name: app.set_theme(name))

        # Add to group and menu
        action_group.addAction(action)
        theme_menu.addAction(action)

    # Update menu when theme changes
    def update_checked_action(new_theme_name: str):
        try:
            for action in action_group.actions():
                if action.data() == new_theme_name:
                    action.setChecked(True)
                    break
        except RuntimeError:
            # Action group may be deleted, ignore
            pass

    app.theme_changed.connect(update_checked_action)

    logger.debug(f"Added theme menu '{menu_name}' with {len(themes_info)} themes")
    return theme_menu


def add_theme_toolbar(
    window: QMainWindow, toolbar_name: str = "Theme", widget_type: str = "combo"
) -> QToolBar:
    """Add a theme selection toolbar to a window.

    This is a one-liner helper that adds a fully functional theme switching
    toolbar to your application.

    Args:
        window: The main window to add the toolbar to
        toolbar_name: Name of the toolbar (default: "Theme")
        widget_type: Type of widget to use ("combo", "buttons", "list")

    Returns:
        The created toolbar

    Example:
        >>> window = QMainWindow()
        >>> add_theme_toolbar(window)  # Adds combo box toolbar
        >>> add_theme_toolbar(window, widget_type="buttons")  # Radio buttons

    """
    app = ThemedApplication.instance()
    if app is None:
        logger.warning("add_theme_toolbar called without ThemedApplication instance")
        return None

    # Create toolbar
    toolbar = QToolBar(toolbar_name, window)
    window.addToolBar(toolbar)

    # Add appropriate widget based on type
    if widget_type == "combo":
        combo = ThemeComboBox()
        toolbar.addWidget(combo)
    else:
        # For now, default to combo
        # TODO: Add support for button groups and list widgets
        combo = ThemeComboBox()
        toolbar.addWidget(combo)

    logger.debug(f"Added theme toolbar '{toolbar_name}' with {widget_type} widget")
    return toolbar


class ThemePreview:
    """Preview themes with commit/cancel capability.

    This class allows previewing themes temporarily without persisting the change.
    Users can preview multiple themes and then either commit to keep the change
    or cancel to restore the original theme.

    Example:
        >>> preview = ThemePreview()
        >>> preview.preview("light")  # Try light theme
        >>> preview.preview("dark")   # Try dark theme
        >>> preview.commit()          # Keep dark theme
        >>>
        >>> # Or cancel to restore original
        >>> preview.cancel()

    """

    def __init__(self):
        """Initialize theme preview system."""
        self._original_theme: Optional[str] = None
        self._app = ThemedApplication.instance()

        if self._app is None:
            logger.warning("ThemePreview created without ThemedApplication instance")

    def preview(self, theme_name: str) -> None:
        """Preview a theme without persisting.

        Args:
            theme_name: Name of theme to preview

        Example:
            >>> preview.preview("light")

        """
        if self._app is None:
            return

        # Store original theme on first preview
        if self._original_theme is None:
            self._original_theme = self._app.current_theme_name
            logger.debug(f"Stored original theme: {self._original_theme}")

        # Apply preview theme (without persisting)
        self._app.set_theme(theme_name, persist=False)
        logger.debug(f"Previewing theme: {theme_name}")

        # Emit preview started signal if first preview
        if hasattr(self._app, "theme_preview_started"):
            self._app.theme_preview_started.emit(theme_name)

    def commit(self) -> None:
        """Keep the currently previewed theme.

        Clears the stored original theme, making the current theme permanent.

        Example:
            >>> preview.preview("light")
            >>> preview.commit()  # Keep light theme

        """
        if self._original_theme is not None:
            logger.debug(f"Committed preview, keeping theme: {self._app.current_theme_name}")

            # Emit preview ended signal
            if hasattr(self._app, "theme_preview_ended"):
                self._app.theme_preview_ended.emit(self._app.current_theme_name)

            self._original_theme = None

    def cancel(self) -> None:
        """Cancel preview and restore original theme.

        Restores the theme that was active before preview started.

        Example:
            >>> preview.preview("light")
            >>> preview.cancel()  # Restore original theme

        """
        if self._original_theme is not None and self._app is not None:
            logger.debug(f"Cancelled preview, restoring theme: {self._original_theme}")

            # Restore original
            self._app.set_theme(self._original_theme)

            # Emit preview ended signal
            if hasattr(self._app, "theme_preview_ended"):
                self._app.theme_preview_ended.emit(self._original_theme)

            self._original_theme = None

    @property
    def is_previewing(self) -> bool:
        """Check if currently previewing a theme.

        Returns:
            True if a preview is active, False otherwise

        Example:
            >>> preview.preview("light")
            >>> preview.is_previewing
            True
            >>> preview.commit()
            >>> preview.is_previewing
            False

        """
        return self._original_theme is not None


class ThemeSettings:
    """Persistent theme preferences using QSettings.

    This class handles saving and loading theme preferences using Qt's
    QSettings system, allowing themes to persist across application restarts.

    Args:
        organization: Organization name for QSettings
        application: Application name for QSettings
        auto_save: Automatically save when theme changes (default: False)

    Example:
        >>> settings = ThemeSettings("MyCompany", "MyApp", auto_save=True)
        >>> settings.save_theme("dark")
        >>> # Later...
        >>> theme = settings.load_theme()
        >>> app.set_theme(theme)

    """

    def __init__(self, organization: str, application: str, auto_save: bool = False):
        """Initialize theme settings manager."""
        self._settings = QSettings(organization, application)
        self._app = ThemedApplication.instance()
        self._auto_save = auto_save

        if self._auto_save and self._app:
            # Connect to theme changes for auto-save
            self._app.theme_changed.connect(self._on_theme_changed)

        logger.debug(f"ThemeSettings initialized for {organization}/{application}")

    def save_theme(self, theme_name: str) -> None:
        """Save theme preference.

        Args:
            theme_name: Name of theme to save

        Example:
            >>> settings.save_theme("dark")

        """
        self._settings.setValue("theme/current", theme_name)
        self._settings.sync()
        logger.debug(f"Saved theme preference: {theme_name}")

    def load_theme(self, default: Optional[str] = None) -> Optional[str]:
        """Load saved theme preference.

        Args:
            default: Default theme to return if no preference saved

        Returns:
            Saved theme name, or default if no preference exists

        Example:
            >>> theme = settings.load_theme(default="dark")
            >>> app.set_theme(theme)

        """
        theme_name = self._settings.value("theme/current", default)
        logger.debug(f"Loaded theme preference: {theme_name}")
        return theme_name

    def clear(self) -> None:
        """Clear saved theme preference.

        Example:
            >>> settings.clear()

        """
        self._settings.remove("theme/current")
        self._settings.sync()
        logger.debug("Cleared theme preference")

    def _on_theme_changed(self, theme_name: str) -> None:
        """Handle theme change for auto-save."""
        if self._auto_save:
            self.save_theme(theme_name)
