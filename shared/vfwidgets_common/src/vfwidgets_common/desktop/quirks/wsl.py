"""WSL-specific quirks and workarounds."""

import os

from ..config import EnvironmentInfo
from .base import PlatformQuirk


class WSLSoftwareRenderingQuirk(PlatformQuirk):
    """Force software rendering in WSL environments.

    WSL often has issues with OpenGL hardware acceleration, especially WSL1
    and older WSL2 versions without WSLg. This quirk forces software rendering
    for Qt and Chromium-based components.
    """

    @property
    def name(self) -> str:
        return "WSL Software Rendering"

    @property
    def description(self) -> str:
        return "Forces software rendering for Qt and WebEngine in WSL"

    def is_applicable(self, env: EnvironmentInfo) -> bool:
        """Apply in WSL environments unless user has already configured."""
        # Respect user's existing configuration
        if os.environ.get("LIBGL_ALWAYS_SOFTWARE"):
            return False
        return env.is_wsl

    def apply(self) -> dict[str, str]:
        """Apply WSL software rendering configuration."""
        changes = {}

        # Force software OpenGL rendering
        if "LIBGL_ALWAYS_SOFTWARE" not in os.environ:
            os.environ["LIBGL_ALWAYS_SOFTWARE"] = "1"
            changes["LIBGL_ALWAYS_SOFTWARE"] = "1"

        # Qt Quick software backend
        if "QT_QUICK_BACKEND" not in os.environ:
            os.environ["QT_QUICK_BACKEND"] = "software"
            changes["QT_QUICK_BACKEND"] = "software"

        # WebEngine/Chromium flags for WSL
        chromium_flags = self._get_chromium_flags()
        existing_flags = os.environ.get("QTWEBENGINE_CHROMIUM_FLAGS", "")

        if chromium_flags:
            # Merge with existing flags
            if existing_flags:
                merged_flags = f"{existing_flags} {chromium_flags}"
            else:
                merged_flags = chromium_flags

            os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = merged_flags
            changes["QTWEBENGINE_CHROMIUM_FLAGS"] = merged_flags

        return changes

    def _get_chromium_flags(self) -> str:
        """Get Chromium flags for WSL environment."""
        flags = [
            "--disable-gpu",
            "--disable-software-rasterizer",
            "--disable-dev-shm-usage",
            "--no-sandbox",  # Required in WSL
            "--disable-setuid-sandbox",
            "--disable-accelerated-2d-canvas",
            "--disable-accelerated-video-decode",
            "--num-raster-threads=1",
        ]
        return " ".join(flags)
