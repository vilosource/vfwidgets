"""
Core components for ChromeTabbedWindow.

Contains the fundamental data structures and constants.
"""

from .constants import *

__all__ = [
    # Constants
    "TAB_HEIGHT",
    "TAB_MIN_WIDTH",
    "TAB_MAX_WIDTH",
    "TAB_OVERLAP",
    "TAB_CURVE_RADIUS",
    "CLOSE_BUTTON_SIZE",
    "CLOSE_BUTTON_MARGIN",
    # Colors
    "COLOR_BACKGROUND",
    "COLOR_TAB_INACTIVE",
    "COLOR_TAB_ACTIVE",
    "COLOR_TAB_HOVER",
    "COLOR_BORDER",
    "COLOR_TEXT",
    "COLOR_TEXT_INACTIVE",
    "COLOR_CLOSE_HOVER",
    "COLOR_CLOSE_PRESSED",
    # Enums
    "TabPosition",
    "TabShape",
    "WindowMode",
    # Defaults
    "DEFAULT_ICON_SIZE",
    "DEFAULT_MINIMUM_SIZE",
    "DEFAULT_SIZE_HINT",
    "DEFAULT_TAB_POSITION",
    "DEFAULT_TAB_SHAPE",
    "DEFAULT_DOCUMENT_MODE",
    "DEFAULT_TABS_CLOSABLE",
    "DEFAULT_MOVABLE",
    "DEFAULT_USES_SCROLL_BUTTONS",
    "DEFAULT_ELIDE_MODE",
]
