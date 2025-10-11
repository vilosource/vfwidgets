"""
Constants and enums for ChromeTabbedWindow.

Defines all constants used throughout the application.
"""

from enum import IntEnum

from PySide6.QtCore import QSize

# Chrome Visual Constants
TAB_HEIGHT = 34
TAB_MIN_WIDTH = 100
TAB_MAX_WIDTH = 240
TAB_OVERLAP = 14
TAB_CURVE_RADIUS = 8
CLOSE_BUTTON_SIZE = 16
CLOSE_BUTTON_MARGIN = 8

# Chrome Colors (Light Theme)
COLOR_BACKGROUND = "#DEE1E6"
COLOR_TAB_INACTIVE = "#F4F6F8"
COLOR_TAB_ACTIVE = "#FFFFFF"
COLOR_TAB_HOVER = "#F8F9FA"
COLOR_BORDER = "#C1C4C9"
COLOR_TEXT = "#202124"
COLOR_TEXT_INACTIVE = "#5F6368"
COLOR_CLOSE_HOVER = "#E8EAED"
COLOR_CLOSE_PRESSED = "#D32F2F"

# Animation Constants
ANIMATION_DURATION_MS = 200
ANIMATION_EASING = "OutCubic"  # QEasingCurve.Type.OutCubic

# Default Sizes
DEFAULT_ICON_SIZE = QSize(16, 16)
DEFAULT_MINIMUM_SIZE = QSize(200, 150)
DEFAULT_SIZE_HINT = QSize(400, 300)

# QTabWidget Compatibility Enums
# Use QTabWidget enums for 100% compatibility


class TabPosition(IntEnum):
    """Tab position enum matching QTabWidget.TabPosition."""

    North = 0
    South = 1
    West = 2
    East = 3


class TabShape(IntEnum):
    """Tab shape enum matching QTabWidget.TabShape."""

    Rounded = 0
    Triangular = 1


class WindowMode(IntEnum):
    """Window mode for ChromeTabbedWindow."""

    Embedded = 0  # Normal widget embedded in parent
    Frameless = 1  # Top-level frameless window


# Property Defaults (matching QTabWidget)
DEFAULT_TAB_POSITION = TabPosition.North
DEFAULT_TAB_SHAPE = TabShape.Rounded
DEFAULT_DOCUMENT_MODE = False
DEFAULT_TABS_CLOSABLE = False
DEFAULT_MOVABLE = False
DEFAULT_USES_SCROLL_BUTTONS = True
DEFAULT_ELIDE_MODE = 0  # Qt.TextElideMode.ElideNone
