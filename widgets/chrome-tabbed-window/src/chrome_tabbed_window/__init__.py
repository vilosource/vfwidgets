"""
ChromeTabbedWindow - A Chrome-style tabbed window widget for PySide6/PyQt6.

A professional, cross-platform tabbed window component with QTabWidget API compatibility.
"""

__version__ = "1.0.0"
__author__ = "VFWidgets Team"
__all__ = [
    "ChromeTabbedWindow",
    "PlatformCapabilities",
    "WindowMode",
    "TabPosition",
    "TabShape",
]

# Import main class and public types
from .chrome_tabbed_window import ChromeTabbedWindow
from .core.constants import TabPosition, TabShape, WindowMode
from .platform.capabilities import PlatformCapabilities
