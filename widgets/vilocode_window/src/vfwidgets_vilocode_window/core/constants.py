"""Constants for ViloCodeWindow.

This module contains enums and constant values used throughout the widget.
"""

from enum import Enum, auto


class WindowMode(Enum):
    """Window display mode.

    Attributes:
        Frameless: Top-level window without native frame (custom title bar)
        Embedded: Widget embedded in another parent widget
    """

    Frameless = auto()
    Embedded = auto()

    def __str__(self) -> str:
        return self.name
