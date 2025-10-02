"""Implementation of ButtonWidget - A theme-aware PySide6 button widget."""

from enum import Enum
from typing import Optional

from PySide6.QtCore import QPropertyAnimation, QSize, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QIcon
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QPushButton

try:
    from vfwidgets_theme.widgets.base import ThemedWidget
    from vfwidgets_theme.widgets.roles import WidgetRole, set_widget_role
    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False
    ThemedWidget = object
    WidgetRole = None


# Deprecated: Use WidgetRole from theme system instead
class ButtonStyle(Enum):
    """Button style presets (DEPRECATED - use WidgetRole instead).

    This enum is deprecated in favor of vfwidgets_theme.WidgetRole.
    It is kept for backward compatibility only.
    """

    DEFAULT = "default"
    PRIMARY = "primary"
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"
    INFO = "info"
    DARK = "dark"


if THEME_AVAILABLE:
    class ButtonWidget(ThemedWidget, QPushButton):
        """Theme-aware enhanced button widget.

        This button automatically adapts to the application theme and supports
        semantic roles (PRIMARY, SUCCESS, WARNING, DANGER) via the theme system.

        Signals:
            clicked: Emitted when button is clicked
            double_clicked: Emitted on double click
            long_pressed: Emitted when button is held for >1 second
            style_changed: Emitted when button style changes

        Theme Integration:
            The button uses the theme system's WidgetRole for semantic styling.
            Colors automatically update when the app theme changes.

        Example:
            from vfwidgets_theme import ThemedApplication, WidgetRole
            from vfwidgets_button import ButtonWidget

            app = ThemedApplication(sys.argv)
            btn = ButtonWidget("Click Me", role=WidgetRole.PRIMARY)
            app.set_theme("dark")  # Button automatically updates
        """

        # Theme configuration - maps theme tokens to button properties
        theme_config = {
            'bg': 'button.background',
            'fg': 'button.foreground',
            'hover_bg': 'button.hoverBackground',
            'pressed_bg': 'button.pressedBackground',
            'disabled_bg': 'button.disabledBackground',
            'disabled_fg': 'button.disabledForeground',
            'border': 'button.border',
        }

        # Custom signals
        double_clicked = Signal()
        long_pressed = Signal()
        style_changed = Signal(str)

        def __init__(
            self,
            text: str = "",
            parent: Optional[QPushButton] = None,
            role: Optional[WidgetRole] = None,
            style: Optional[ButtonStyle] = None,  # Deprecated, for backward compat
            animated: bool = True,
            rounded: bool = True,
            shadow: bool = True,
        ) -> None:
            """Initialize the ButtonWidget.

            Args:
                text: Button text
                parent: Parent widget
                role: Semantic role (WidgetRole.PRIMARY, SUCCESS, WARNING, DANGER)
                style: DEPRECATED - use role parameter instead
                animated: Enable hover animations
                rounded: Use rounded corners
                shadow: Add drop shadow effect
            """
            # Store button-specific params before calling super().__init__
            self._role = role
            self._animated = animated
            self._rounded = rounded
            self._shadow_enabled = shadow
            self._long_press_timer = None
            self._animation: Optional[QPropertyAnimation] = None

            # Handle deprecated style parameter
            if style is not None and role is None:
                # Map old ButtonStyle to new WidgetRole
                role_mapping = {
                    ButtonStyle.PRIMARY: WidgetRole.PRIMARY,
                    ButtonStyle.SUCCESS: WidgetRole.SUCCESS,
                    ButtonStyle.WARNING: WidgetRole.WARNING,
                    ButtonStyle.DANGER: WidgetRole.DANGER,
                    ButtonStyle.DEFAULT: None,
                    ButtonStyle.INFO: None,
                    ButtonStyle.DARK: None,
                }
                self._role = role_mapping.get(style)

            # Use cooperative multiple inheritance - this calls both ThemedWidget
            # and QPushButton __init__ in the right order via MRO
            super().__init__(text=text, parent=parent)

            # Initialize button-specific features after Qt widget is ready
            self._long_press_timer = QTimer()
            self._long_press_timer.timeout.connect(self._on_long_press)

            # Apply role if specified
            if self._role is not None:
                set_widget_role(self, self._role)

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

            # Apply theme
            self.on_theme_changed()

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

        def on_theme_changed(self) -> None:
            """Called automatically when the theme changes.

            Regenerates stylesheet using current theme tokens.
            """
            border_radius = "6px" if self._rounded else "0px"

            # Get colors from theme system
            bg = self.theme.bg
            fg = self.theme.fg
            hover_bg = self.theme.hover_bg
            pressed_bg = self.theme.pressed_bg
            disabled_bg = self.theme.disabled_bg
            disabled_fg = self.theme.disabled_fg

            stylesheet = f"""
                QPushButton {{
                    background-color: {bg};
                    color: {fg};
                    border: none;
                    border-radius: {border_radius};
                    padding: 8px 16px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {hover_bg};
                }}
                QPushButton:pressed {{
                    background-color: {pressed_bg};
                }}
                QPushButton:disabled {{
                    background-color: {disabled_bg};
                    color: {disabled_fg};
                }}
            """
            self.setStyleSheet(stylesheet)

        def set_role(self, role: WidgetRole) -> None:
            """Set button semantic role.

            Args:
                role: Semantic role (PRIMARY, SUCCESS, WARNING, DANGER)
            """
            self._role = role
            set_widget_role(self, role)
            self.style_changed.emit(role.value if role else "default")

        def get_role(self) -> Optional[WidgetRole]:
            """Get current button role.

            Returns:
                Current widget role or None
            """
            return self._role

        # Deprecated methods for backward compatibility
        def set_style(self, style: ButtonStyle) -> None:
            """Set button style (DEPRECATED - use set_role instead).

            Args:
                style: Button style preset
            """
            # Map to new role system
            role_mapping = {
                ButtonStyle.PRIMARY: WidgetRole.PRIMARY,
                ButtonStyle.SUCCESS: WidgetRole.SUCCESS,
                ButtonStyle.WARNING: WidgetRole.WARNING,
                ButtonStyle.DANGER: WidgetRole.DANGER,
                ButtonStyle.DEFAULT: None,
                ButtonStyle.INFO: None,
                ButtonStyle.DARK: None,
            }
            role = role_mapping.get(style)
            if role:
                self.set_role(role)
            self.style_changed.emit(style.value)

        def get_style(self) -> ButtonStyle:
            """Get current button style (DEPRECATED).

            Returns:
                ButtonStyle enum value (for backward compatibility)
            """
            # Map role back to style
            if self._role == WidgetRole.PRIMARY:
                return ButtonStyle.PRIMARY
            elif self._role == WidgetRole.SUCCESS:
                return ButtonStyle.SUCCESS
            elif self._role == WidgetRole.WARNING:
                return ButtonStyle.WARNING
            elif self._role == WidgetRole.DANGER:
                return ButtonStyle.DANGER
            else:
                return ButtonStyle.DEFAULT

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
            self.on_theme_changed()  # Reapply theme

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

else:
    # Fallback when theme system is not available
    class ButtonWidget(QPushButton):
        """ButtonWidget without theme support (theme system not installed)."""

        double_clicked = Signal()
        long_pressed = Signal()
        style_changed = Signal(str)

        def __init__(self, text: str = "", parent=None, **kwargs):
            super().__init__(text, parent)
            raise ImportError(
                "vfwidgets-theme is required for ButtonWidget. "
                "Install with: pip install vfwidgets-theme"
            )
