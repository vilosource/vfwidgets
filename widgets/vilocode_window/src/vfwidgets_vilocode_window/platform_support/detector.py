"""Platform detection for ViloCodeWindow.

Detects the current platform and its capabilities.
"""

from __future__ import annotations

import os
import platform
from typing import Optional

from PySide6.QtGui import QGuiApplication

from .capabilities import PlatformCapabilities


class PlatformDetector:
    """Detects platform information and capabilities."""

    @staticmethod
    def detect() -> PlatformCapabilities:
        """Detect current platform capabilities."""
        # Basic platform detection
        system = platform.system()
        platform_name = PlatformDetector._normalize_platform_name(system)
        window_system = PlatformDetector._detect_window_system()
        desktop_env = PlatformDetector._detect_desktop_environment()

        # Create capabilities object
        caps = PlatformCapabilities(
            platform_name=platform_name,
            window_system=window_system,
            desktop_environment=desktop_env,
        )

        # Detect specific capabilities
        PlatformDetector._detect_window_capabilities(caps)
        PlatformDetector._detect_special_environments(caps)

        return caps

    @staticmethod
    def _normalize_platform_name(system: str) -> str:
        """Normalize platform name."""
        system_lower = system.lower()
        if system_lower == "windows":  # noqa: SIM116
            return "Windows"
        elif system_lower == "darwin":
            return "macOS"
        elif system_lower == "linux":
            return "Linux"
        else:
            return system

    @staticmethod
    def _detect_window_system() -> str:
        """Detect the window system."""
        if QGuiApplication.instance():
            platform_name = QGuiApplication.platformName()
            if platform_name == "windows":  # noqa: SIM116
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

        # Check common desktop environment variables
        desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").upper()
        if desktop:
            return desktop

        # Check session type
        session = os.environ.get("DESKTOP_SESSION", "").upper()
        if session:
            return session

        return None

    @staticmethod
    def _detect_window_capabilities(caps: PlatformCapabilities) -> None:
        """Detect window management capabilities."""
        # Windows
        if caps.platform_name == "Windows" or caps.platform_name == "macOS":
            caps.supports_frameless = True
            caps.supports_custom_titlebar = True
            caps.supports_system_move = True
            caps.supports_system_resize = True
            caps.supports_transparency = True

        # Linux
        elif caps.platform_name == "Linux":
            if caps.window_system == "X11":
                caps.supports_frameless = True
                caps.supports_custom_titlebar = True
                caps.supports_system_move = True
                caps.supports_system_resize = True
                caps.supports_transparency = True
            elif caps.window_system == "Wayland":
                # Wayland support depends on Qt version
                from PySide6.QtCore import qVersion

                qt_version_str = qVersion()
                major, minor = 0, 0
                try:
                    parts = qt_version_str.split(".")
                    major = int(parts[0])
                    minor = int(parts[1]) if len(parts) > 1 else 0
                except (ValueError, IndexError):
                    pass

                # Qt 6.5+ has better Wayland support
                if major >= 6 and minor >= 5:
                    caps.supports_frameless = True
                    caps.supports_custom_titlebar = True
                    caps.supports_system_move = True
                    caps.supports_system_resize = True
                    caps.supports_transparency = True
                else:
                    # Limited support on older Qt with Wayland
                    caps.supports_frameless = False
                    caps.add_quirk("wayland_old_qt")

    @staticmethod
    def _detect_special_environments(caps: PlatformCapabilities) -> None:
        """Detect special environments like WSL."""
        # WSL detection
        if caps.platform_name == "Linux":
            try:
                with open("/proc/version") as f:
                    version_info = f.read().lower()
                    if "microsoft" in version_info or "wsl" in version_info:
                        caps.is_wsl = True
                        caps.supports_frameless = False  # WSL has issues
                        caps.add_quirk("wsl")
            except (FileNotFoundError, PermissionError):
                pass

        # Remote desktop detection (basic)
        if os.environ.get("SSH_CONNECTION") or os.environ.get("SSH_CLIENT"):
            caps.is_remote_desktop = True
            caps.add_quirk("remote_desktop")
