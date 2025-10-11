"""
Window control buttons for ChromeTabbedWindow.

Provides minimize, maximize/restore, and close buttons for frameless windows.
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QWidget


class WindowControlButton(QPushButton):
    """Base class for window control buttons with Chrome styling."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedSize(46, 32)  # Chrome button dimensions
        self.setCursor(Qt.CursorShape.ArrowCursor)

        self._is_hovered = False
        self._is_pressed = False

    def _is_dark_theme(self) -> bool:
        """Detect if current theme is dark by checking parent theme type."""
        parent_widget = self.parent()
        while parent_widget:
            if hasattr(parent_widget, "get_current_theme"):
                theme = parent_widget.get_current_theme()
                if theme and hasattr(theme, "type"):
                    return theme.type == "dark"
            parent_widget = parent_widget.parent()
        # Default to dark theme if unable to detect
        return True

    def _get_theme_colors(self):
        """Get colors from theme or fallback to theme-appropriate defaults."""
        # Try to get theme from parent chain
        parent_widget = self.parent()
        while parent_widget:
            if hasattr(parent_widget, "get_current_theme"):
                theme = parent_widget.get_current_theme()
                if theme and hasattr(theme, "colors"):
                    colors = theme.colors

                    # Try multiple token name variations for better compatibility
                    # Handle both namespaced (colors.X) and non-namespaced (X) tokens

                    # Icon color: try icon.foreground, colors.foreground, window.foreground
                    icon_color = (
                        colors.get("icon.foreground")
                        or colors.get("colors.foreground")
                        or colors.get("window.foreground")
                    )

                    # Toolbar hover background
                    hover_bg_color = (
                        colors.get("toolbar.hoverBackground")
                        or colors.get("colors.toolbar.hoverBackground")
                        or "rgba(0, 0, 0, 0.1)"
                    )
                    hover_bg = QColor(hover_bg_color)

                    # Toolbar hover foreground
                    hover_icon_color = colors.get("toolbar.hoverForeground") or colors.get(
                        "colors.toolbar.hoverForeground"
                    )
                    if not hover_icon_color:
                        # Auto-calculate contrasting color based on hover background lightness
                        hover_icon_color = "#ffffff" if hover_bg.lightness() < 128 else "#000000"

                    # Toolbar active background
                    active_bg_color = (
                        colors.get("toolbar.activeBackground")
                        or colors.get("colors.toolbar.activeBackground")
                        or "rgba(0, 0, 0, 0.2)"
                    )

                    # If we found an icon color, use it; otherwise use smart fallback
                    if icon_color:
                        return {
                            "normal": QColor(0, 0, 0, 0),
                            "hover": hover_bg,
                            "pressed": QColor(active_bg_color),
                            "icon": QColor(icon_color),
                            "hover_icon": QColor(hover_icon_color),
                        }
            parent_widget = parent_widget.parent()

        # Fallback to theme-appropriate defaults based on detected theme type
        is_dark = self._is_dark_theme()

        if is_dark:
            # Dark theme: light icons on dark background
            return {
                "normal": QColor(0, 0, 0, 0),
                "hover": QColor(255, 255, 255, 26),  # 10% white
                "pressed": QColor(255, 255, 255, 51),  # 20% white
                "icon": QColor(255, 255, 255, 204),  # 80% white
                "hover_icon": QColor(255, 255, 255, 230),  # 90% white
            }
        else:
            # Light theme: dark icons on light background
            return {
                "normal": QColor(0, 0, 0, 0),
                "hover": QColor(0, 0, 0, 26),  # 10% black
                "pressed": QColor(0, 0, 0, 51),  # 20% black
                "icon": QColor(0, 0, 0, 153),  # 60% black
                "hover_icon": QColor(0, 0, 0, 179),  # 70% black
            }

    def enterEvent(self, event) -> None:
        """Handle mouse enter."""
        self._is_hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        """Handle mouse leave."""
        self._is_hovered = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle mouse release."""
        self._is_pressed = False
        self.update()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint the button."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get theme colors
        colors = self._get_theme_colors()

        # Draw background
        if self._is_pressed:
            painter.fillRect(self.rect(), colors["pressed"])
        elif self._is_hovered:
            painter.fillRect(self.rect(), colors["hover"])
        else:
            painter.fillRect(self.rect(), colors["normal"])

        # Draw icon (implemented in subclasses)
        self.draw_icon(painter)

    def draw_icon(self, painter: QPainter) -> None:
        """Draw the button icon. Override in subclasses."""
        pass


class MinimizeButton(WindowControlButton):
    """Minimize button with Chrome styling."""

    def draw_icon(self, painter: QPainter) -> None:
        """Draw minimize icon (horizontal line)."""
        colors = self._get_theme_colors()
        # Use hover icon color when hovered/pressed for proper contrast
        icon_color = (
            colors["hover_icon"] if (self._is_hovered or self._is_pressed) else colors["icon"]
        )
        painter.setPen(QPen(icon_color, 1))
        y = self.height() // 2
        painter.drawLine(18, y, 28, y)


class MaximizeButton(WindowControlButton):
    """Maximize/Restore button with Chrome styling."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.is_maximized = False

    def set_maximized(self, maximized: bool) -> None:
        """Update button state based on window state."""
        self.is_maximized = maximized
        self.update()

    def draw_icon(self, painter: QPainter) -> None:
        """Draw maximize or restore icon."""
        colors = self._get_theme_colors()

        # Use hover icon color when hovered/pressed for proper contrast
        icon_color = (
            colors["hover_icon"] if (self._is_hovered or self._is_pressed) else colors["icon"]
        )
        painter.setPen(QPen(icon_color, 1))

        if self.is_maximized:
            # Draw restore icon (two overlapping squares)
            # Back square
            painter.drawRect(20, 12, 8, 8)
            # Front square - fill with matching color to create overlap effect
            bg_color = (
                colors["hover"] if (self._is_hovered or self._is_pressed) else colors["normal"]
            )
            painter.fillRect(18, 14, 8, 8, bg_color)
            painter.drawRect(18, 14, 8, 8)
        else:
            # Draw maximize icon (square)
            painter.drawRect(18, 12, 10, 10)


class CloseButton(WindowControlButton):
    """Close button with Chrome styling."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        # Close button has red hover/pressed colors
        self.hover_color = QColor(224, 67, 67)  # Chrome red
        self.pressed_color = QColor(200, 50, 50)  # Darker red

    def draw_icon(self, painter: QPainter) -> None:
        """Draw close icon (X)."""
        colors = self._get_theme_colors()
        # Use white icon on red background when hovered
        if self._is_hovered or self._is_pressed:
            painter.setPen(QPen(QColor(255, 255, 255), 1))
        else:
            painter.setPen(QPen(colors["icon"], 1))

        # Draw X
        painter.drawLine(19, 13, 27, 21)
        painter.drawLine(27, 13, 19, 21)


class WindowControls(QWidget):
    """
    Window control buttons widget for ChromeTabbedWindow.

    Provides minimize, maximize/restore, and close buttons with Chrome styling.
    """

    # Signals
    minimize_clicked = Signal()
    maximize_clicked = Signal()
    close_clicked = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize window controls."""
        super().__init__(parent)

        # Create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create buttons
        self.minimize_button = MinimizeButton(self)
        self.maximize_button = MaximizeButton(self)
        self.close_button = CloseButton(self)

        # Connect button clicks
        self.minimize_button.clicked.connect(self.minimize_clicked.emit)
        self.maximize_button.clicked.connect(self.maximize_clicked.emit)
        self.close_button.clicked.connect(self.close_clicked.emit)

        # Add buttons to layout
        layout.addWidget(self.minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(self.close_button)

        # Set fixed size for the widget
        self.setFixedSize(138, 32)  # 3 buttons * 46px width

    def update_maximize_button(self, is_maximized: bool) -> None:
        """Update maximize button state based on window state."""
        self.maximize_button.set_maximized(is_maximized)

    def set_platform_style(self, platform: str) -> None:
        """
        Set platform-specific styling.

        Args:
            platform: 'windows', 'macos', or 'linux'
        """
        if platform == "macos":
            # macOS uses traffic light buttons on the left
            # This would require a different implementation
            pass
        # Windows and Linux use similar styles
