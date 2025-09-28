"""
Platform adapters for ChromeTabbedWindow.

Handles platform-specific functionality and capabilities.
"""

from .base import BasePlatformAdapter, IPlatformAdapter, PlatformFactory
from .capabilities import PlatformCapabilities
from .detector import PlatformDetector

# Platform-specific adapters (imported dynamically)
try:
    from .windows import WindowsPlatformAdapter
except ImportError:
    WindowsPlatformAdapter = None

try:
    from .macos import MacOSPlatformAdapter
except ImportError:
    MacOSPlatformAdapter = None

try:
    from .linux import LinuxPlatformAdapter
except ImportError:
    LinuxPlatformAdapter = None

__all__ = [
    "BasePlatformAdapter",
    "PlatformFactory",
    "IPlatformAdapter",
    "PlatformCapabilities",
    "PlatformDetector",
    "WindowsPlatformAdapter",
    "MacOSPlatformAdapter",
    "LinuxPlatformAdapter",
]
