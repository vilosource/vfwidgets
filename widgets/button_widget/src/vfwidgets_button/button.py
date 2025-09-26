"""Implementation of ButtonWidget - An enhanced PySide6 button with animations and styles."""

from enum import Enum
from typing import Optional

from PySide6.QtCore import QPropertyAnimation, QSize, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QIcon
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QPushButton


class ButtonStyle(Enum):
    """Button style presets."""

    DEFAULT = "default"
    PRIMARY = "primary"
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"
    INFO = "info"
    DARK = "dark"


class ButtonWidget(QPushButton):
    """Enhanced button widget with animations and multiple style presets.

    Signals:
        clicked: Emitted when button is clicked
        double_clicked: Emitted on double click
        long_pressed: Emitted when button is held for >1 second
        style_changed: Emitted when button style changes
    """

    # Custom signals
    double_clicked = Signal()
    long_pressed = Signal()
    style_changed = Signal(str)

    # Style definitions
    STYLES = {
        ButtonStyle.DEFAULT: {
            "normal": "#f0f0f0",
            "hover": "#e0e0e0",
            "pressed": "#d0d0d0",
            "text": "#333333",
        },
        ButtonStyle.PRIMARY: {
            "normal": "#007bff",
            "hover": "#0056b3",
            "pressed": "#004085",
            "text": "#ffffff",
        },
        ButtonStyle.SUCCESS: {
            "normal": "#28a745",
            "hover": "#218838",
            "pressed": "#1e7e34",
            "text": "#ffffff",
        },
        ButtonStyle.WARNING: {
            "normal": "#ffc107",
            "hover": "#e0a800",
            "pressed": "#d39e00",
            "text": "#212529",
        },
        ButtonStyle.DANGER: {
            "normal": "#dc3545",
            "hover": "#c82333",
            "pressed": "#bd2130",
            "text": "#ffffff",
        },
        ButtonStyle.INFO: {
            "normal": "#17a2b8",
            "hover": "#138496",
            "pressed": "#117a8b",
            "text": "#ffffff",
        },
        ButtonStyle.DARK: {
            "normal": "#343a40",
            "hover": "#23272b",
            "pressed": "#1d2124",
            "text": "#ffffff",
        },
    }

    def __init__(
        self,
        text: str = "",
        parent: Optional[QPushButton] = None,
        style: ButtonStyle = ButtonStyle.DEFAULT,
        animated: bool = True,
        rounded: bool = True,
        shadow: bool = True,
    ) -> None:
        """Initialize the ButtonWidget.

        Args:
            text: Button text
            parent: Parent widget
            style: Button style preset
            animated: Enable hover animations
            rounded: Use rounded corners
            shadow: Add drop shadow effect
        """
        super().__init__(text, parent)

        self._style = style
        self._animated = animated
        self._rounded = rounded
        self._shadow_enabled = shadow
        self._long_press_timer = QTimer()
        self._long_press_timer.timeout.connect(self._on_long_press)
        self._animation: Optional[QPropertyAnimation] = None

        self._setup_ui()
        self._setup_animations()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Set up the widget UI."""
        # Set size hints
        self.setMinimumHeight(36)
        self.setMinimumWidth(80)

        # Set font
        font = QFont()
        font.setPointSize(10)
        font.setWeight(QFont.Weight.Medium)
        self.setFont(font)

        # Apply style
        self.set_style(self._style)

        # Add shadow effect if enabled
        if self._shadow_enabled:
            self._setup_shadow()

    def _setup_shadow(self) -> None:
        """Set up drop shadow effect."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 50))
        self.setGraphicsEffect(shadow)

    def _setup_animations(self) -> None:
        """Set up hover animations."""
        if not self._animated:
            return

        # Property for animation
        self._opacity = 1.0

    def _connect_signals(self) -> None:
        """Connect internal signals."""
        self.pressed.connect(self._on_pressed)
        self.released.connect(self._on_released)

    def _on_pressed(self) -> None:
        """Handle button press."""
        self._long_press_timer.start(1000)  # 1 second for long press

    def _on_released(self) -> None:
        """Handle button release."""
        self._long_press_timer.stop()

    def _on_long_press(self) -> None:
        """Handle long press detection."""
        self._long_press_timer.stop()
        self.long_pressed.emit()

    def set_style(self, style: ButtonStyle) -> None:
        """Set button style.

        Args:
            style: Button style preset
        """
        self._style = style
        colors = self.STYLES[style]

        border_radius = "6px" if self._rounded else "0px"

        stylesheet = f"""
            QPushButton {{
                background-color: {colors["normal"]};
                color: {colors["text"]};
                border: none;
                border-radius: {border_radius};
                padding: 8px 16px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {colors["hover"]};
            }}
            QPushButton:pressed {{
                background-color: {colors["pressed"]};
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #666666;
            }}
        """
        self.setStyleSheet(stylesheet)
        self.style_changed.emit(style.value)

    def get_style(self) -> ButtonStyle:
        """Get current button style.

        Returns:
            Current button style
        """
        return self._style

    def set_animated(self, animated: bool) -> None:
        """Enable/disable animations.

        Args:
            animated: Animation state
        """
        self._animated = animated
        if animated:
            self._setup_animations()

    def set_rounded(self, rounded: bool) -> None:
        """Enable/disable rounded corners.

        Args:
            rounded: Rounded corners state
        """
        self._rounded = rounded
        self.set_style(self._style)  # Reapply style

    def set_shadow(self, enabled: bool) -> None:
        """Enable/disable drop shadow.

        Args:
            enabled: Shadow state
        """
        self._shadow_enabled = enabled
        if enabled:
            self._setup_shadow()
        else:
            self.setGraphicsEffect(None)

    def mouseDoubleClickEvent(self, event) -> None:
        """Handle double click event."""
        super().mouseDoubleClickEvent(event)
        self.double_clicked.emit()

    def set_icon_with_text(self, icon: QIcon, text: str) -> None:
        """Set both icon and text.

        Args:
            icon: Button icon
            text: Button text
        """
        self.setIcon(icon)
        self.setText(text)
        self.setIconSize(QSize(16, 16))
