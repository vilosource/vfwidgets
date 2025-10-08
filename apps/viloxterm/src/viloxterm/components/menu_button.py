"""Menu button for ViloxTerm window controls."""

from typing import Optional, Dict

from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QPainter, QPen, QAction
from PySide6.QtWidgets import QWidget, QMenu

from chrome_tabbed_window.components.window_controls import WindowControlButton


class MenuButton(WindowControlButton):
    """Menu button styled to match window control buttons.

    Displays a hamburger menu icon (three horizontal lines) and shows
    a context menu when clicked.
    """

    # Signals emitted when menu actions are triggered
    new_window_requested = Signal()
    split_vertical_requested = Signal()
    split_horizontal_requested = Signal()
    close_pane_requested = Signal()
    close_tab_requested = Signal()
    change_theme_requested = Signal()

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        keybinding_actions: Optional[Dict[str, QAction]] = None,
    ) -> None:
        """Initialize menu button.

        Args:
            parent: Parent widget
            keybinding_actions: Dict of action IDs to QActions from KeybindingManager
                              (shortcuts are automatically included from these actions)
        """
        super().__init__(parent)

        # Store parent app reference for dynamic menu updates
        self._parent_app = None

        # Create context menu
        self._menu = QMenu(self)

        # Add "New Window" action at top (not managed by keybindings)
        new_window_action = self._menu.addAction("New Window")
        new_window_action.triggered.connect(self.new_window_requested.emit)

        # Placeholder for "Move Tab to Window" submenu (populated dynamically)
        self._move_to_window_submenu = None

        # Separator
        self._menu.addSeparator()

        # Add keybinding-managed actions if provided
        if keybinding_actions:
            # Tab management section
            if "tab.new" in keybinding_actions:
                self._menu.addAction(keybinding_actions["tab.new"])
            if "tab.next" in keybinding_actions:
                self._menu.addAction(keybinding_actions["tab.next"])
            if "tab.previous" in keybinding_actions:
                self._menu.addAction(keybinding_actions["tab.previous"])

            # Separator
            self._menu.addSeparator()

            # Add pane actions
            if "pane.split_vertical" in keybinding_actions:
                self._menu.addAction(keybinding_actions["pane.split_vertical"])
            if "pane.split_horizontal" in keybinding_actions:
                self._menu.addAction(keybinding_actions["pane.split_horizontal"])

            # Separator
            self._menu.addSeparator()

            # Add close actions
            if "pane.close" in keybinding_actions:
                self._menu.addAction(keybinding_actions["pane.close"])
            if "tab.close" in keybinding_actions:
                self._menu.addAction(keybinding_actions["tab.close"])

        # Separator - Appearance section
        self._menu.addSeparator()

        # Add keybinding-managed appearance actions
        if keybinding_actions:
            # Terminal preferences (Ctrl+,)
            if "appearance.terminal_preferences" in keybinding_actions:
                self._menu.addAction(keybinding_actions["appearance.terminal_preferences"])

            # Terminal theme customization (Ctrl+Shift+,)
            if "appearance.terminal_theme" in keybinding_actions:
                self._menu.addAction(keybinding_actions["appearance.terminal_theme"])

        # Add "Change Theme" action (not managed by keybindings)
        change_theme_action = self._menu.addAction("Change App Theme...")
        change_theme_action.triggered.connect(self.change_theme_requested.emit)

    def set_parent_app(self, app) -> None:
        """Set parent application for dynamic menu updates.

        Args:
            app: ViloxTermApp instance to query for available windows
        """
        self._parent_app = app

    def _update_move_to_window_submenu(self) -> None:
        """Update 'Move Tab to Window' submenu with current available windows.

        This method is called each time before showing the menu to ensure
        the window list is up-to-date.
        """
        # Remove old submenu/action if it exists
        if self._move_to_window_submenu:
            # Handle both QMenu (submenu) and QAction (disabled item)
            if hasattr(self._move_to_window_submenu, 'menuAction'):
                # It's a QMenu
                self._menu.removeAction(self._move_to_window_submenu.menuAction())
            else:
                # It's a QAction
                self._menu.removeAction(self._move_to_window_submenu)
            self._move_to_window_submenu = None

        # Only add submenu if parent app is set
        if not self._parent_app:
            return

        # Get available target windows
        target_windows = self._parent_app.get_available_target_windows()

        # Get current tab index
        current_tab_index = self._parent_app.currentIndex()

        # Get menu actions to find insertion point (after "New Window")
        actions = self._menu.actions()
        insert_before_action = actions[1] if len(actions) > 1 else None

        if target_windows and current_tab_index >= 0:
            # Create submenu with available windows
            self._move_to_window_submenu = QMenu("Move Tab to Window", self._menu)

            # Populate with window titles and connect actions
            for window_title, window_ref in target_windows:
                action = self._move_to_window_submenu.addAction(window_title)
                # Use lambda with default arguments to capture current values
                action.triggered.connect(
                    lambda checked=False, idx=current_tab_index, win=window_ref: self._parent_app._move_tab_to_window(
                        idx, win
                    )
                )

            # Insert submenu after "New Window", before separator
            self._menu.insertMenu(insert_before_action, self._move_to_window_submenu)
        else:
            # No other windows or no current tab - add disabled action
            disabled_action = QAction("Move Tab to Window", self._menu)
            disabled_action.setEnabled(False)
            self._move_to_window_submenu = disabled_action

            # Insert disabled action after "New Window", before separator
            self._menu.insertAction(insert_before_action, disabled_action)

    def mousePressEvent(self, event) -> None:
        """Override to show menu on click instead of default button behavior."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Update dynamic menu items before showing
            self._update_move_to_window_submenu()

            # Show menu below the button
            pos = self.mapToGlobal(QPoint(0, self.height()))
            self._menu.exec(pos)
            event.accept()
        else:
            super().mousePressEvent(event)

    def draw_icon(self, painter: QPainter) -> None:
        """Draw hamburger menu icon (3 horizontal lines).

        Args:
            painter: QPainter for drawing
        """
        colors = self._get_theme_colors()

        # Use hover icon color when hovered/pressed for proper contrast
        icon_color = (
            colors["hover_icon"] if (self._is_hovered or self._is_pressed) else colors["icon"]
        )
        painter.setPen(QPen(icon_color, 2, Qt.PenStyle.SolidLine))

        # Calculate positions
        center_x = self.width() // 2
        center_y = self.height() // 2
        line_width = 12

        # Draw three horizontal lines
        # Top line
        painter.drawLine(
            center_x - line_width // 2, center_y - 5, center_x + line_width // 2, center_y - 5
        )
        # Middle line
        painter.drawLine(center_x - line_width // 2, center_y, center_x + line_width // 2, center_y)
        # Bottom line
        painter.drawLine(
            center_x - line_width // 2, center_y + 5, center_x + line_width // 2, center_y + 5
        )
