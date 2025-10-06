"""Platform detection utilities for VFWidgets.

Provides cross-widget platform detection including WSL, remote desktop,
and other special environment detection.
"""

import os
import platform
from typing import Optional


def is_wsl() -> bool:
    """Detect if running in Windows Subsystem for Linux.

    Returns:
        True if running in WSL, False otherwise
    """
    if platform.system().lower() != "linux":
        return False

    # Check for WSL indicators in /proc/version
    if os.path.exists("/proc/version"):
        try:
            with open("/proc/version") as f:
                version_info = f.read().lower()
                return "microsoft" in version_info or "wsl" in version_info
        except OSError:
            pass

    return False


def is_remote_desktop() -> bool:
    """Detect if running in a remote desktop session.

    Returns:
        True if in remote desktop, False otherwise
    """
    system = platform.system().lower()

    if system == "windows":
        # Check for Terminal Services/RDP session
        if os.environ.get("SESSIONNAME", "").startswith("RDP-"):
            return True

    # Could add more checks for VNC, X11 forwarding, etc.
    return False


def get_desktop_environment() -> Optional[str]:
    """Detect the desktop environment on Linux.

    Returns:
        Desktop environment name (KDE, GNOME, etc.) or None
    """
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


def needs_software_rendering() -> bool:
    """Determine if software rendering is required.

    This checks for environments where hardware OpenGL is not available
    or unreliable, such as WSL, remote desktop, or specific virtualization.

    Returns:
        True if software rendering should be used, False otherwise
    """
    # WSL requires software rendering for Qt WebEngine
    if is_wsl():
        return True

    # Remote desktop may benefit from software rendering
    if is_remote_desktop():
        return True

    # Check if already configured by user
    if os.environ.get("LIBGL_ALWAYS_SOFTWARE"):
        # User has already configured, respect their choice
        return False

    return False


def configure_qt_environment() -> dict[str, str]:
    """Configure Qt environment variables for optimal performance.

    This should be called BEFORE creating QApplication to ensure
    proper initialization in special environments like WSL.

    Returns:
        Dictionary of environment variables that were set
    """
    changes = {}

    if needs_software_rendering():
        # Set software rendering for Qt
        if "LIBGL_ALWAYS_SOFTWARE" not in os.environ:
            os.environ["LIBGL_ALWAYS_SOFTWARE"] = "1"
            changes["LIBGL_ALWAYS_SOFTWARE"] = "1"

        if "QT_QUICK_BACKEND" not in os.environ:
            os.environ["QT_QUICK_BACKEND"] = "software"
            changes["QT_QUICK_BACKEND"] = "software"

    return changes


def get_platform_info() -> dict[str, any]:
    """Get comprehensive platform information.

    Returns:
        Dictionary containing platform details
    """
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "is_wsl": is_wsl(),
        "is_remote_desktop": is_remote_desktop(),
        "desktop_environment": get_desktop_environment(),
        "needs_software_rendering": needs_software_rendering(),
    }
