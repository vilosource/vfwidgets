"""Platform capabilities detection for ViloCodeWindow.

Determines what features are available on the current platform.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PlatformCapabilities:
    """Capabilities available on the current platform.

    Used to determine what features can be enabled and how to adapt
    the UI for the best user experience on each platform.
    """

    # Core platform info
    platform_name: str  # "Windows", "macOS", "Linux"
    window_system: str  # "Win32", "Cocoa", "X11", "Wayland"
    desktop_environment: Optional[str] = None  # "KDE", "GNOME", etc.

    # Window management capabilities
    supports_frameless: bool = False
    supports_custom_titlebar: bool = False
    supports_system_move: bool = False
    supports_system_resize: bool = False
    supports_transparency: bool = False

    # Special environments
    is_wsl: bool = False
    is_remote_desktop: bool = False

    # Quirks and limitations
    quirks: list[str] = field(default_factory=list)

    @property
    def can_use_frameless_mode(self) -> bool:
        """Check if frameless mode can be used reliably."""
        return (
            self.supports_frameless
            and self.supports_custom_titlebar
            and self.supports_system_move
            and not self.is_wsl  # WSL has issues with frameless windows
        )

    @property
    def should_use_embedded_mode(self) -> bool:
        """Check if embedded mode should be preferred."""
        return not self.can_use_frameless_mode

    def has_quirk(self, quirk_name: str) -> bool:
        """Check if a specific quirk is present."""
        return quirk_name in self.quirks

    def add_quirk(self, quirk_name: str) -> None:
        """Add a platform quirk."""
        if quirk_name not in self.quirks:
            self.quirks.append(quirk_name)
