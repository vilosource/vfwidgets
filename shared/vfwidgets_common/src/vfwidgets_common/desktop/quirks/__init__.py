"""Platform-specific quirks and workarounds registry."""

import logging

from ..config import EnvironmentInfo
from .base import PlatformQuirk
from .wayland import WaylandScalingQuirk, WaylandXdgDesktopPortalQuirk
from .windows_rdp import WindowsRDPQuirk
from .wsl import WSLSoftwareRenderingQuirk

logger = logging.getLogger(__name__)

# Registry of all available quirks
QUIRKS: list[PlatformQuirk] = [
    WSLSoftwareRenderingQuirk(),
    WaylandScalingQuirk(),
    WaylandXdgDesktopPortalQuirk(),
    WindowsRDPQuirk(),
]


def apply_all_quirks(env: EnvironmentInfo) -> dict[str, str]:
    """Apply all applicable platform quirks.

    Args:
        env: Detected environment information

    Returns:
        Dictionary of all environment variables that were changed
        (key=var_name, value=new_value)
    """
    all_changes: dict[str, str] = {}

    for quirk in QUIRKS:
        if quirk.is_applicable(env):
            logger.info(f"Applying quirk: {quirk.name}")
            logger.debug(f"  {quirk.description}")

            try:
                changes = quirk.apply()
                all_changes.update(changes)

                if changes:
                    logger.debug(f"  Modified environment variables: {list(changes.keys())}")

            except Exception as e:
                logger.warning(f"Failed to apply quirk '{quirk.name}': {e}")

    return all_changes


__all__ = [
    "PlatformQuirk",
    "WSLSoftwareRenderingQuirk",
    "WaylandScalingQuirk",
    "WaylandXdgDesktopPortalQuirk",
    "WindowsRDPQuirk",
    "QUIRKS",
    "apply_all_quirks",
]
