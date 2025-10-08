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

        # Create context menu
        self._menu = QMenu(self)

        # Add "New Window" action at top (not managed by keybindings)
        new_window_action = self._menu.addAction("New Window")
        new_window_action.triggered.connect(self.new_window_requested.emit)

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

    def mousePressEvent(self, event) -> None:
        """Override to show menu on click instead of default button behavior."""
        if event.button() == Qt.MouseButton.LeftButton:
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
