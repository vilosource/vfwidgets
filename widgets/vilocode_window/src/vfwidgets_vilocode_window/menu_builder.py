"""Fluent menu builder for ViloCodeWindow.

This module provides MenuBuilder, a fluent interface for building menus
with method chaining. Eliminates initialization order traps and provides
clean, readable menu construction.

Example:
    >>> window.add_menu("File") \
    ...     .add_action("Open", on_open, "Ctrl+O") \
    ...     .add_separator() \
    ...     .add_action("Exit", window.close, "Ctrl+Q")

    >>> window.add_menu("Edit") \
    ...     .add_submenu("Advanced") \
    ...         .add_action("Format Document") \
    ...         .add_action("Sort Lines") \
    ...     .end_submenu()
"""

from typing import Callable, Optional

from PySide6.QtCore import QObject
from PySide6.QtGui import QActionGroup, QIcon
from PySide6.QtWidgets import QMenu


class MenuBuilder:
    """Fluent interface for building menus.

    MenuBuilder provides a clean, chainable API for constructing menus
    without worrying about initialization order or manual action creation.

    All methods return self for method chaining.

    Attributes:
        _menu: The QMenu being built
        _window: Reference to parent ViloCodeWindow
        _submenu_stack: Stack of nested submenus for context tracking
    """

    def __init__(self, menu: QMenu, window: QObject):
        """Initialize MenuBuilder.

        Args:
            menu: QMenu to build with this builder
            window: Parent ViloCodeWindow instance
        """
        self._menu = menu
        self._window = window
        self._submenu_stack: list[QMenu] = []

    def add_action(
        self,
        text: str,
        callback: Optional[Callable] = None,
        shortcut: Optional[str] = None,
        icon: Optional[QIcon] = None,
        tooltip: Optional[str] = None,
        enabled: bool = True,
        checkable: bool = False,
        checked: bool = False,
    ) -> "MenuBuilder":
        """Add an action to the current menu.

        Args:
            text: Action text (use & for mnemonic, e.g., "&Open")
            callback: Function to call when triggered (optional)
            shortcut: Keyboard shortcut (e.g., "Ctrl+O") (optional)
            icon: QIcon for the action (optional)
            tooltip: Tooltip and status tip text (optional)
            enabled: Whether action is enabled (default: True)
            checkable: Whether action is checkable (default: False)
            checked: Initial checked state if checkable (default: False)

        Returns:
            Self for method chaining

        Example:
            >>> builder.add_action("Open", on_open, "Ctrl+O",
            ...                    tooltip="Open a file")
        """
        action = self._current_menu().addAction(text)

        if callback:
            action.triggered.connect(callback)
        if shortcut:
            action.setShortcut(shortcut)
        if icon:
            action.setIcon(icon)
        if tooltip:
            action.setToolTip(tooltip)
            action.setStatusTip(tooltip)

        action.setEnabled(enabled)

        if checkable:
            action.setCheckable(True)
            action.setChecked(checked)

        return self

    def add_separator(self) -> "MenuBuilder":
        """Add a separator line to the current menu.

        Returns:
            Self for method chaining

        Example:
            >>> builder.add_action("Open") \
            ...     .add_separator() \
            ...     .add_action("Exit")
        """
        self._current_menu().addSeparator()
        return self

    def add_submenu(self, title: str) -> "MenuBuilder":
        """Add a submenu and switch context to it.

        All subsequent add_action() calls will add to this submenu
        until end_submenu() is called.

        Args:
            title: Submenu title (use & for mnemonic)

        Returns:
            Self for method chaining

        Example:
            >>> builder.add_submenu("Recent Files") \
            ...     .add_action("file1.txt") \
            ...     .add_action("file2.txt") \
            ...     .end_submenu()
        """
        submenu = self._current_menu().addMenu(title)
        self._submenu_stack.append(submenu)
        return self

    def end_submenu(self) -> "MenuBuilder":
        """Return to parent menu context.

        Must be called after add_submenu() to balance the context stack.

        Returns:
            Self for method chaining

        Raises:
            ValueError: If called without matching add_submenu()

        Example:
            >>> builder.add_submenu("Tools") \
            ...     .add_action("Option 1") \
            ...     .end_submenu() \
            ...     .add_action("Back in main menu")
        """
        if not self._submenu_stack:
            raise ValueError(
                "end_submenu() called without matching add_submenu(). "
                "Each add_submenu() must have a corresponding end_submenu()."
            )
        self._submenu_stack.pop()
        return self

    def add_checkable(
        self,
        text: str,
        callback: Optional[Callable[[bool], None]] = None,
        checked: bool = False,
        shortcut: Optional[str] = None,
        tooltip: Optional[str] = None,
        enabled: bool = True,
    ) -> "MenuBuilder":
        """Add a checkable (toggle) action.

        Convenience method for adding actions with checkable=True.
        Callback receives bool parameter with checked state.

        Args:
            text: Action text
            callback: Function called with bool (checked state)
            checked: Initial checked state (default: False)
            shortcut: Keyboard shortcut (optional)
            tooltip: Tooltip text (optional)
            enabled: Whether enabled (default: True)

        Returns:
            Self for method chaining

        Example:
            >>> def on_toggle(checked: bool):
            ...     print(f"Toggled: {checked}")
            >>> builder.add_checkable("Show Sidebar", on_toggle, checked=True)
        """
        return self.add_action(
            text=text,
            callback=callback,
            shortcut=shortcut,
            tooltip=tooltip,
            enabled=enabled,
            checkable=True,
            checked=checked,
        )

    def add_action_group(
        self,
        actions: list[tuple[str, Callable]],
        exclusive: bool = True,
        default_index: int = 0,
    ) -> "MenuBuilder":
        """Add a group of mutually exclusive actions (radio buttons).

        Args:
            actions: List of (text, callback) tuples
            exclusive: Whether actions are mutually exclusive (default: True)
            default_index: Index of initially checked action (default: 0)

        Returns:
            Self for method chaining

        Example:
            >>> builder.add_action_group([
            ...     ("Small", lambda: set_size("small")),
            ...     ("Medium", lambda: set_size("medium")),
            ...     ("Large", lambda: set_size("large")),
            ... ], default_index=1)
        """
        group = QActionGroup(self._current_menu())
        group.setExclusive(exclusive)

        for idx, (text, callback) in enumerate(actions):
            action = self._current_menu().addAction(text)
            action.setCheckable(True)
            action.setChecked(idx == default_index)
            action.triggered.connect(callback)
            group.addAction(action)

        return self

    def _current_menu(self) -> QMenu:
        """Get current menu context.

        Returns:
            Current menu (submenu if in nested context, else root menu)
        """
        return self._submenu_stack[-1] if self._submenu_stack else self._menu
