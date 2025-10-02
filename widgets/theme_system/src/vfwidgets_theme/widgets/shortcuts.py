"""Keyboard shortcuts for theme switching.

This module provides keyboard shortcut management for theme switching.

Example:
    from vfwidgets_theme.widgets.shortcuts import ThemeShortcuts

    shortcuts = ThemeShortcuts(main_window)
    shortcuts.add_toggle_shortcut("Ctrl+T")
    shortcuts.add_cycle_shortcut("Ctrl+Shift+T")

"""

from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QWidget

from ..logging import get_debug_logger
from .application import ThemedApplication

logger = get_debug_logger(__name__)


class ThemeShortcuts:
    """Keyboard shortcuts for theme switching.

    This class manages keyboard shortcuts for theme-related operations like
    toggling between light/dark and cycling through available themes.

    Args:
        parent: Parent widget for shortcuts
        context: Shortcut context (default: ApplicationShortcut)

    Example:
        >>> shortcuts = ThemeShortcuts(main_window)
        >>> shortcuts.add_toggle_shortcut("Ctrl+T")  # Toggle light/dark
        >>> shortcuts.add_cycle_shortcut("Ctrl+Shift+T")  # Cycle themes
        >>> shortcuts.add_specific_theme_shortcut("Ctrl+1", "dark")

    """

    def __init__(self, parent: QWidget):
        """Initialize theme shortcuts manager."""
        self._parent = parent
        self._app = ThemedApplication.instance()
        self._shortcuts = []

        if self._app is None:
            logger.warning("ThemeShortcuts created without ThemedApplication instance")

        logger.debug("ThemeShortcuts initialized")

    def add_toggle_shortcut(self, key_sequence: str) -> QShortcut:
        """Add shortcut to toggle between light and dark themes.

        Args:
            key_sequence: Key sequence (e.g., "Ctrl+T")

        Returns:
            The created QShortcut

        Example:
            >>> shortcuts.add_toggle_shortcut("Ctrl+T")

        """
        if self._app is None:
            return None

        shortcut = QShortcut(QKeySequence(key_sequence), self._parent)
        shortcut.activated.connect(self._app.toggle_theme)
        self._shortcuts.append(shortcut)

        logger.debug(f"Added toggle shortcut: {key_sequence}")
        return shortcut

    def add_cycle_shortcut(self, key_sequence: str) -> QShortcut:
        """Add shortcut to cycle through available themes.

        Args:
            key_sequence: Key sequence (e.g., "Ctrl+Shift+T")

        Returns:
            The created QShortcut

        Example:
            >>> shortcuts.add_cycle_shortcut("Ctrl+Shift+T")

        """
        if self._app is None:
            return None

        shortcut = QShortcut(QKeySequence(key_sequence), self._parent)
        shortcut.activated.connect(self._app.cycle_theme)
        self._shortcuts.append(shortcut)

        logger.debug(f"Added cycle shortcut: {key_sequence}")
        return shortcut

    def add_specific_theme_shortcut(
        self,
        key_sequence: str,
        theme_name: str
    ) -> QShortcut:
        """Add shortcut to switch to a specific theme.

        Args:
            key_sequence: Key sequence (e.g., "Ctrl+1")
            theme_name: Name of theme to switch to

        Returns:
            The created QShortcut

        Example:
            >>> shortcuts.add_specific_theme_shortcut("Ctrl+1", "dark")
            >>> shortcuts.add_specific_theme_shortcut("Ctrl+2", "light")

        """
        if self._app is None:
            return None

        shortcut = QShortcut(QKeySequence(key_sequence), self._parent)
        shortcut.activated.connect(lambda: self._app.set_theme(theme_name))
        self._shortcuts.append(shortcut)

        logger.debug(f"Added specific theme shortcut: {key_sequence} -> {theme_name}")
        return shortcut

    def clear_all(self) -> None:
        """Remove all registered shortcuts.

        Example:
            >>> shortcuts.clear_all()

        """
        for shortcut in self._shortcuts:
            shortcut.setEnabled(False)
            shortcut.deleteLater()

        self._shortcuts.clear()
        logger.debug("Cleared all theme shortcuts")
