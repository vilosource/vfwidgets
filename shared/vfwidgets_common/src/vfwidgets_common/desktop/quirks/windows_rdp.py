"""Windows Remote Desktop specific quirks."""

import os

from ..config import EnvironmentInfo
from .base import PlatformQuirk


class WindowsRDPQuirk(PlatformQuirk):
    """Optimize Qt rendering for Windows Remote Desktop sessions.

    RDP sessions often have limited graphics capabilities. This quirk
    optimizes Qt rendering for remote desktop environments.
    """

    @property
    def name(self) -> str:
        return "Windows RDP Optimization"

    @property
    def description(self) -> str:
        return "Optimizes Qt rendering for Remote Desktop sessions"

    def is_applicable(self, env: EnvironmentInfo) -> bool:
        """Apply in Windows RDP sessions."""
        return env.os == "windows" and env.is_remote_desktop

    def apply(self) -> dict[str, str]:
        """Apply RDP optimization configuration."""
        changes = {}

        # Disable GPU acceleration in RDP
        if "QT_OPENGL" not in os.environ:
            os.environ["QT_OPENGL"] = "software"
            changes["QT_OPENGL"] = "software"

        # Optimize WebEngine for RDP
        chromium_flags = "--disable-gpu --disable-software-rasterizer"
        existing_flags = os.environ.get("QTWEBENGINE_CHROMIUM_FLAGS", "")

        if chromium_flags:
            if existing_flags:
                merged_flags = f"{existing_flags} {chromium_flags}"
            else:
                merged_flags = chromium_flags

            os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = merged_flags
            changes["QTWEBENGINE_CHROMIUM_FLAGS"] = merged_flags

        return changes
