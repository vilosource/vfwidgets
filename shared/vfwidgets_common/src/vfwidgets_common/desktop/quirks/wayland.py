"""Wayland-specific quirks and workarounds."""

import os

from ..config import EnvironmentInfo
from .base import PlatformQuirk


class WaylandScalingQuirk(PlatformQuirk):
    """Fix HiDPI scaling issues on Wayland.

    Wayland has different scaling behavior than X11. This quirk ensures
    proper Qt scaling configuration for Wayland sessions.
    """

    @property
    def name(self) -> str:
        return "Wayland HiDPI Scaling"

    @property
    def description(self) -> str:
        return "Configures proper HiDPI scaling for Wayland display server"

    def is_applicable(self, env: EnvironmentInfo) -> bool:
        """Apply on Wayland sessions unless already configured."""
        # Only apply on Wayland
        if env.display_server != "wayland":
            return False

        # Respect user's existing configuration
        if os.environ.get("QT_AUTO_SCREEN_SCALE_FACTOR"):
            return False

        return True

    def apply(self) -> dict[str, str]:
        """Apply Wayland scaling configuration."""
        changes = {}

        # Enable Qt automatic HiDPI scaling
        if "QT_AUTO_SCREEN_SCALE_FACTOR" not in os.environ:
            os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
            changes["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

        # Force Wayland platform if not set
        if "QT_QPA_PLATFORM" not in os.environ:
            os.environ["QT_QPA_PLATFORM"] = "wayland"
            changes["QT_QPA_PLATFORM"] = "wayland"

        return changes


class WaylandXdgDesktopPortalQuirk(PlatformQuirk):
    """Enable XDG Desktop Portal for Wayland.

    Ensures Qt uses XDG Desktop Portal for file dialogs and other
    desktop integration on Wayland.
    """

    @property
    def name(self) -> str:
        return "Wayland XDG Desktop Portal"

    @property
    def description(self) -> str:
        return "Enables XDG Desktop Portal integration for Wayland"

    def is_applicable(self, env: EnvironmentInfo) -> bool:
        """Apply on Wayland sessions."""
        return env.display_server == "wayland"

    def apply(self) -> dict[str, str]:
        """Apply XDG Desktop Portal configuration."""
        changes = {}

        # Enable file dialog portal
        if "QT_QPA_PLATFORMTHEME" not in os.environ:
            # Use native theme integration
            os.environ["QT_QPA_PLATFORMTHEME"] = "gnome"
            changes["QT_QPA_PLATFORMTHEME"] = "gnome"

        return changes
