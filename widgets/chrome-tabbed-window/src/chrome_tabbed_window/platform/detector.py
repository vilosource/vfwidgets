"""
Platform detection for ChromeTabbedWindow.

Detects the current platform and its capabilities.
"""

from __future__ import annotations

import os
import platform
from typing import Optional

from PySide6.QtGui import QGuiApplication

from .capabilities import PlatformCapabilities


class PlatformDetector:
    """
    Detects platform information and capabilities.

    This class analyzes the current environment to determine what
    features are available and how the UI should adapt.
    """

    @staticmethod
    def detect() -> PlatformCapabilities:
        """
        Detect current platform capabilities.

        Returns a PlatformCapabilities object with all detected information.
        """
        # Basic platform detection
        system = platform.system()
        platform_name = PlatformDetector._normalize_platform_name(system)
        window_system = PlatformDetector._detect_window_system()
        desktop_env = PlatformDetector._detect_desktop_environment()

        # Create capabilities object
        caps = PlatformCapabilities(
            platform_name=platform_name,
            window_system=window_system,
            desktop_environment=desktop_env
        )

        # Detect specific capabilities
        PlatformDetector._detect_window_capabilities(caps)
        PlatformDetector._detect_input_capabilities(caps)
        PlatformDetector._detect_display_capabilities(caps)
        PlatformDetector._detect_special_environments(caps)
        PlatformDetector._detect_quirks(caps)

        return caps

    @staticmethod
    def _normalize_platform_name(system: str) -> str:
        """Normalize platform name."""
        system_lower = system.lower()
        if system_lower == "windows":
            return "Windows"
        elif system_lower == "darwin":
            return "macOS"
        elif system_lower == "linux":
            return "Linux"
        else:
            return system  # Unknown platform

    @staticmethod
    def _detect_window_system() -> str:
        """Detect the window system."""
        if QGuiApplication.instance():
            platform_name = QGuiApplication.platformName()
            if platform_name == "windows":
                return "Win32"
            elif platform_name == "cocoa":
                return "Cocoa"
            elif platform_name == "xcb":
                return "X11"
            elif platform_name == "wayland":
                return "Wayland"
            else:
                return platform_name

        # Fallback based on OS
        system = platform.system().lower()
        if system == "windows":
            return "Win32"
        elif system == "darwin":
            return "Cocoa"
        elif system == "linux":
            # Check for Wayland
            if os.environ.get("WAYLAND_DISPLAY"):
                return "Wayland"
            else:
                return "X11"
        else:
            return "Unknown"

    @staticmethod
    def _detect_desktop_environment() -> Optional[str]:
        """Detect the desktop environment on Linux."""
        if platform.system().lower() != "linux":
            return None

        # Check environment variables
        desktop_env = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
        if "kde" in desktop_env:
            return "KDE"
        elif "gnome" in desktop_env:
            return "GNOME"
        elif "xfce" in desktop_env:
            return "XFCE"
        elif "mate" in desktop_env:
            return "MATE"
        elif "cinnamon" in desktop_env:
            return "Cinnamon"

        # Fallback checks
        if os.environ.get("KDE_FULL_SESSION"):
            return "KDE"
        elif os.environ.get("GNOME_DESKTOP_SESSION_ID"):
            return "GNOME"

        return None

    @staticmethod
    def _detect_window_capabilities(caps: PlatformCapabilities) -> None:
        """Detect window management capabilities."""
        # Platform-specific capabilities
        if caps.platform_name == "Windows":
            caps.supports_frameless = True
            caps.supports_custom_titlebar = True
            caps.supports_system_move = True
            caps.supports_system_resize = True
            caps.supports_transparency = True
            caps.supports_blur_behind = True

        elif caps.platform_name == "macOS":
            caps.supports_frameless = True
            caps.supports_custom_titlebar = True
            caps.supports_system_move = True
            caps.supports_system_resize = True
            caps.supports_transparency = True
            caps.supports_blur_behind = False  # Limited support

        elif caps.platform_name == "Linux":
            if caps.window_system == "X11":
                caps.supports_frameless = True
                caps.supports_custom_titlebar = True
                caps.supports_system_move = True
                caps.supports_system_resize = True
                caps.supports_transparency = True
                caps.supports_blur_behind = False  # Depends on compositor
            elif caps.window_system == "Wayland":
                # Wayland has more limitations
                caps.supports_frameless = False  # Client-side decorations required
                caps.supports_custom_titlebar = True
                caps.supports_system_move = False  # Limited in Wayland
                caps.supports_system_resize = False  # Limited in Wayland
                caps.supports_transparency = True
                caps.supports_blur_behind = False

    @staticmethod
    def _detect_input_capabilities(caps: PlatformCapabilities) -> None:
        """Detect input capabilities."""
        # Most platforms support these
        caps.supports_native_drag_drop = True

        # Touch support detection
        if QGuiApplication.instance():
            # Check if touch devices are available
            # This is a simplified check - real implementation would be more thorough
            caps.supports_touch_gestures = False  # Conservative default

    @staticmethod
    def _detect_display_capabilities(caps: PlatformCapabilities) -> None:
        """Detect display capabilities."""
        if caps.platform_name == "Windows":
            # Windows 10+ has per-monitor DPI support
            version = platform.version()
            try:
                major = int(version.split('.')[0])
                if major >= 10:
                    caps.supports_per_monitor_dpi = True
            except (ValueError, IndexError):
                caps.supports_per_monitor_dpi = False

            caps.supports_dark_mode_detection = True

        elif caps.platform_name == "macOS":
            caps.supports_per_monitor_dpi = True
            caps.supports_dark_mode_detection = True

        elif caps.platform_name == "Linux":
            caps.supports_per_monitor_dpi = True  # Modern Linux supports this
            caps.supports_dark_mode_detection = True  # Through Qt theming

    @staticmethod
    def _detect_special_environments(caps: PlatformCapabilities) -> None:
        """Detect special environments."""
        # WSL detection
        if caps.platform_name == "Linux":
            # Check for WSL indicators
            if os.path.exists("/proc/version"):
                try:
                    with open("/proc/version") as f:
                        version_info = f.read().lower()
                        if "microsoft" in version_info or "wsl" in version_info:
                            caps.is_wsl = True
                except OSError:
                    pass

        # Remote desktop detection (simplified)
        if caps.platform_name == "Windows":
            # Check for Terminal Services
            if os.environ.get("SESSIONNAME", "").startswith("RDP-"):
                caps.is_remote_desktop = True

    @staticmethod
    def _detect_quirks(caps: PlatformCapabilities) -> None:
        """Detect platform-specific quirks and limitations."""
        if caps.is_wsl:
            caps.add_quirk("wsl_frameless_unreliable")
            caps.add_quirk("wsl_transparency_issues")

        if caps.window_system == "Wayland":
            caps.add_quirk("wayland_limited_window_control")
            caps.add_quirk("wayland_no_global_position")

        if caps.platform_name == "Linux" and caps.desktop_environment == "KDE":
            caps.add_quirk("kde_compositor_effects")

        if caps.is_remote_desktop:
            caps.add_quirk("remote_desktop_performance")
            caps.add_quirk("remote_desktop_transparency")
