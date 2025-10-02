"""
Chrome-accurate tab renderer for ChromeTabbedWindow.

Provides pixel-perfect Chrome browser tab rendering with curves, gradients, and shadows.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, Optional, Any

from PySide6.QtCore import QPointF, QRect, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)


class TabState(Enum):
    """Tab visual states."""
    NORMAL = 0
    HOVER = 1
    ACTIVE = 2
    PRESSED = 3


class ChromeTabRenderer:
    """
    Renderer for Chrome-style tabs with accurate curves and colors.

    This class handles all the visual rendering of Chrome tabs including:
    - Tab shape with proper curves
    - Colors and gradients
    - Shadows and depth
    - State-based rendering
    - Theme integration (uses theme colors when available)
    """

    # Chrome tab dimensions
    TAB_HEIGHT = 34
    TAB_MIN_WIDTH = 100
    TAB_MAX_WIDTH = 240
    TAB_CURVE_WIDTH = 15  # Width of the curved edges
    TAB_OVERLAP = 14  # How much tabs overlap

    # Chrome colors (light theme) - FALLBACK when no theme available
    COLOR_BACKGROUND = QColor("#DEE1E6")  # Tab bar background
    COLOR_TAB_NORMAL = QColor("#F2F3F5")  # Inactive tab
    COLOR_TAB_HOVER = QColor("#F8F9FA")  # Hovered inactive tab
    COLOR_TAB_ACTIVE = QColor("#FFFFFF")  # Active tab
    COLOR_TAB_PRESSED = QColor("#E8EAED")  # Pressed tab
    COLOR_BORDER = QColor("#C1C3C7")  # Tab borders
    COLOR_SEPARATOR = QColor("#B8BCC3")  # Between inactive tabs
    COLOR_TEXT = QColor("#3C4043")  # Active tab text
    COLOR_TEXT_INACTIVE = QColor("#5F6368")  # Inactive tab text
    COLOR_CLOSE_HOVER = QColor("#5F6368")  # Close button hover
    COLOR_CLOSE_PRESSED = QColor("#3C4043")  # Close button pressed

    @classmethod
    def get_tab_colors(cls, theme: Optional[Any] = None) -> Dict[str, QColor]:
        """
        Get tab colors from theme or fallback to Chrome defaults.

        Args:
            theme: Theme object from ThemedWidget.get_current_theme(), or None for fallback

        Returns:
            Dictionary with color keys: background, tab_normal, tab_hover, tab_active,
            tab_pressed, border, text, text_inactive, close_hover, close_pressed
        """
        if theme is None or not hasattr(theme, 'colors'):
            # Fallback to hardcoded Chrome colors when no theme available
            return {
                'background': cls.COLOR_BACKGROUND,
                'tab_normal': cls.COLOR_TAB_NORMAL,
                'tab_hover': cls.COLOR_TAB_HOVER,
                'tab_active': cls.COLOR_TAB_ACTIVE,
                'tab_pressed': cls.COLOR_TAB_PRESSED,
                'border': cls.COLOR_BORDER,
                'text': cls.COLOR_TEXT,
                'text_inactive': cls.COLOR_TEXT_INACTIVE,
                'close_hover': cls.COLOR_CLOSE_HOVER,
                'close_pressed': cls.COLOR_CLOSE_PRESSED,
            }

        # Extract colors from theme
        colors = theme.colors

        # Try VS Code tokens first, fallback to generic theme colors
        bg = colors.get('colors.background', '#2d2d2d')
        fg = colors.get('colors.foreground', '#cccccc')
        hover = colors.get('colors.hover', '#404040')
        border_color = colors.get('colors.border', '#555555')

        return {
            'background': QColor(colors.get('tab.inactiveBackground', colors.get('editorGroupHeader.tabsBackground', hover))),
            'tab_normal': QColor(colors.get('tab.inactiveBackground', bg)),
            'tab_hover': QColor(colors.get('tab.hoverBackground', hover)),
            'tab_active': QColor(colors.get('tab.activeBackground', colors.get('colors.primary', '#007acc'))),
            'tab_pressed': QColor(colors.get('tab.hoverBackground', hover)),
            'border': QColor(colors.get('tab.border', colors.get('editorGroupHeader.tabsBorder', border_color))),
            'text': QColor(colors.get('tab.activeForeground', fg)),
            'text_inactive': QColor(colors.get('tab.inactiveForeground', fg)),
            'close_hover': QColor(colors.get('tab.inactiveForeground', fg)),
            'close_pressed': QColor(colors.get('tab.activeForeground', fg)),
        }

    @classmethod
    def draw_tab(
        cls,
        painter: QPainter,
        rect: QRect,
        text: str,
        state: TabState,
        has_close_button: bool = False,
        is_closable: bool = False,
        close_button_state: TabState = TabState.NORMAL,
        theme: Optional[Any] = None
    ) -> None:
        """
        Draw a complete Chrome-style tab.

        Args:
            painter: QPainter to draw with
            rect: Rectangle to draw the tab in
            text: Tab text to display
            state: Current tab state
            has_close_button: Whether to show close button
            is_closable: Whether tabs are closable
            close_button_state: State of close button if shown
            theme: Optional theme object for color extraction
        """
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Get theme colors
        colors = cls.get_tab_colors(theme)

        # Create tab shape path
        tab_path = cls._create_chrome_tab_path(rect, state)

        # Draw tab background with gradient
        cls._draw_tab_background(painter, tab_path, rect, state, colors)

        # Draw tab border
        cls._draw_tab_border(painter, tab_path, state, colors)

        # Draw tab text
        text_rect = rect.adjusted(
            cls.TAB_CURVE_WIDTH,  # Left padding
            0,
            -cls.TAB_CURVE_WIDTH - (30 if is_closable else 10),  # Right padding
            0
        )
        cls._draw_tab_text(painter, text_rect, text, state, colors)

        # Draw close button if needed
        if is_closable and has_close_button:
            close_rect = QRect(
                rect.right() - cls.TAB_CURVE_WIDTH - 24,
                rect.center().y() - 8,
                16,
                16
            )
            cls._draw_close_button(painter, close_rect, close_button_state, colors)

        painter.restore()

    @classmethod
    def _create_chrome_tab_path(cls, rect: QRect, state: TabState) -> QPainterPath:
        """
        Create the Chrome tab shape path with proper curves.

        Chrome tabs have a distinctive trapezoid shape with curved corners.
        """
        path = QPainterPath()

        # Adjust rect for active tab (slightly taller)
        if state == TabState.ACTIVE:
            rect = rect.adjusted(0, -2, 0, 0)

        # Tab shape coordinates
        left = rect.left()
        right = rect.right()
        top = rect.top()
        bottom = rect.bottom()
        curve = cls.TAB_CURVE_WIDTH

        # Start from bottom left
        path.moveTo(left - curve, bottom)

        # Left curve (bottom to top)
        path.cubicTo(
            QPointF(left - curve/2, bottom),  # Control point 1
            QPointF(left, top + curve/2),  # Control point 2
            QPointF(left + curve/2, top)  # End point
        )

        # Top edge
        path.lineTo(right - curve/2, top)

        # Right curve (top to bottom)
        path.cubicTo(
            QPointF(right, top + curve/2),  # Control point 1
            QPointF(right + curve/2, bottom),  # Control point 2
            QPointF(right + curve, bottom)  # End point
        )

        # Bottom edge (implicit close)
        path.lineTo(left - curve, bottom)

        return path

    @classmethod
    def _draw_tab_background(
        cls,
        painter: QPainter,
        path: QPainterPath,
        rect: QRect,
        state: TabState,
        colors: Dict[str, QColor]
    ) -> None:
        """Draw tab background with appropriate color/gradient."""
        # Select color based on state
        if state == TabState.ACTIVE:
            color = colors['tab_active']
        elif state == TabState.HOVER:
            color = colors['tab_hover']
        elif state == TabState.PRESSED:
            color = colors['tab_pressed']
        else:
            color = colors['tab_normal']

        # Create subtle gradient for depth
        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        gradient.setColorAt(0, color)
        gradient.setColorAt(1, color.darker(102))  # Very subtle darkening

        # Fill the tab
        painter.fillPath(path, QBrush(gradient))

        # Add subtle shadow for active tab
        if state == TabState.ACTIVE:
            shadow_path = QPainterPath()
            shadow_path.addRect(rect.left() - cls.TAB_CURVE_WIDTH, rect.bottom() - 1,
                               rect.width() + 2 * cls.TAB_CURVE_WIDTH, 2)
            painter.fillPath(shadow_path, QColor(0, 0, 0, 20))

    @classmethod
    def _draw_tab_border(cls, painter: QPainter, path: QPainterPath, state: TabState, colors: Dict[str, QColor]) -> None:
        """Draw tab border/outline."""
        # Active tabs have a subtle border, inactive tabs have separator lines
        if state == TabState.ACTIVE:
            pen = QPen(colors['border'], 1)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawPath(path)
        elif state == TabState.NORMAL:
            # Draw separator line on right edge only
            # This is handled by the tab bar to avoid overlaps
            pass

    @classmethod
    def _draw_tab_text(
        cls,
        painter: QPainter,
        rect: QRect,
        text: str,
        state: TabState,
        colors: Dict[str, QColor]
    ) -> None:
        """Draw tab text with appropriate styling."""
        # Set text color
        if state == TabState.ACTIVE:
            painter.setPen(colors['text'])
        else:
            painter.setPen(colors['text_inactive'])

        # Set font (Chrome uses Segoe UI on Windows, SF Pro on macOS)
        font = QFont("Segoe UI", 9)
        font.setWeight(QFont.Weight.Normal)
        painter.setFont(font)

        # Draw text with elision
        metrics = painter.fontMetrics()
        elided_text = metrics.elidedText(text, Qt.TextElideMode.ElideRight, rect.width())
        painter.drawText(rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, elided_text)

    @classmethod
    def _draw_close_button(
        cls,
        painter: QPainter,
        rect: QRect,
        state: TabState,
        colors: Dict[str, QColor]
    ) -> None:
        """Draw tab close button (X)."""
        # Draw hover background
        if state == TabState.HOVER:
            painter.fillRect(rect, QColor(0, 0, 0, 20))
        elif state == TabState.PRESSED:
            painter.fillRect(rect, QColor(0, 0, 0, 30))

        # Draw X
        if state == TabState.HOVER or state == TabState.PRESSED:
            painter.setPen(QPen(colors['close_hover'], 1.5))
        else:
            painter.setPen(QPen(colors['text_inactive'], 1))

        margin = 4
        painter.drawLine(
            rect.left() + margin, rect.top() + margin,
            rect.right() - margin, rect.bottom() - margin
        )
        painter.drawLine(
            rect.left() + margin, rect.bottom() - margin,
            rect.right() - margin, rect.top() + margin
        )

    @classmethod
    def draw_new_tab_button(cls, painter: QPainter, rect: QRect, state: TabState, theme: Optional[Any] = None) -> None:
        """
        Draw the new tab (+) button.

        Args:
            painter: QPainter to draw with
            rect: Rectangle to draw the button in
            state: Button state
            theme: Optional theme object for color extraction
        """
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Get theme colors
        colors = cls.get_tab_colors(theme)

        # Draw hover/pressed background
        if state == TabState.HOVER:
            painter.fillRect(rect, QColor(0, 0, 0, 15))
        elif state == TabState.PRESSED:
            painter.fillRect(rect, QColor(0, 0, 0, 25))

        # Draw plus sign
        painter.setPen(QPen(colors['text_inactive'], 1.5))
        center = rect.center()
        size = 6

        # Horizontal line
        painter.drawLine(center.x() - size, center.y(), center.x() + size, center.y())

        # Vertical line
        painter.drawLine(center.x(), center.y() - size, center.x(), center.y() + size)

        painter.restore()

    @classmethod
    def draw_tab_bar_background(cls, painter: QPainter, rect: QRect, theme: Optional[Any] = None) -> None:
        """
        Draw the tab bar background.

        Args:
            painter: QPainter to draw with
            rect: Rectangle to fill
            theme: Optional theme object for color extraction
        """
        colors = cls.get_tab_colors(theme)
        painter.fillRect(rect, colors['background'])
