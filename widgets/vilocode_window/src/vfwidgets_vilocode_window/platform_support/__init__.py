"""Platform-specific support for frameless windows.

This module provides platform detection and platform-specific adapters for
Windows, macOS, Linux (X11/Wayland), and WSL.
"""

from .base import BasePlatformAdapter, IPlatformAdapter, PlatformFactory
from .capabilities import PlatformCapabilities
from .detector import PlatformDetector

__all__ = [
    "BasePlatformAdapter",
    "IPlatformAdapter",
    "PlatformFactory",
    "PlatformCapabilities",
    "PlatformDetector",
]
