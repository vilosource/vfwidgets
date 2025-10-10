"""Comprehensive environment detection for cross-platform desktop integration."""

import logging
import os
import platform
from typing import Optional

from .config import EnvironmentInfo

logger = logging.getLogger(__name__)


def detect_wsl() -> tuple[bool, bool]:
    """Detect if running in Windows Subsystem for Linux.

    Returns:
        Tuple of (is_wsl, is_wsl2)
    """
    if platform.system().lower() != "linux":
        return False, False

    # Check for WSL indicators in /proc/version
    if os.path.exists("/proc/version"):
        try:
            with open("/proc/version") as f:
                version_info = f.read().lower()
                if "microsoft" in version_info or "wsl" in version_info:
                    # WSL2 has different kernel version patterns
                    is_wsl2 = "wsl2" in version_info or "microsoft" in version_info
                    return True, is_wsl2
        except OSError:
            pass

    return False, False


def detect_remote_desktop() -> bool:
    """Detect if running in a remote desktop session.

    Returns:
        True if in remote desktop, False otherwise
    """
    system = platform.system().lower()

    if system == "windows":
        # Check for Terminal Services/RDP session
        if os.environ.get("SESSIONNAME", "").startswith("RDP-"):
            return True

    elif system == "linux":
        # Check for SSH with X11 forwarding
        if os.environ.get("SSH_CONNECTION") and os.environ.get("DISPLAY"):
            return True

        # Check for VNC indicators
        if "vnc" in os.environ.get("DISPLAY", "").lower():
            return True

    return False


def detect_desktop_environment() -> Optional[str]:
    """Detect the desktop environment on Linux.

    Returns:
        Desktop environment name or None
    """
    if platform.system().lower() != "linux":
        return None

    # Check XDG_CURRENT_DESKTOP (most reliable)
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
    elif "lxde" in desktop_env:
        return "LXDE"
    elif "lxqt" in desktop_env:
        return "LXQt"

    # Fallback checks for older systems
    if os.environ.get("KDE_FULL_SESSION"):
        return "KDE"
    elif os.environ.get("GNOME_DESKTOP_SESSION_ID"):
        return "GNOME"
    elif os.environ.get("DESKTOP_SESSION"):
        session = os.environ["DESKTOP_SESSION"].lower()
        if "xfce" in session:
            return "XFCE"
        elif "mate" in session:
            return "MATE"

    return None


def detect_display_server() -> Optional[str]:
    """Detect the display server (X11 or Wayland) on Linux.

    Returns:
        "wayland", "x11", or None
    """
    if platform.system().lower() != "linux":
        return None

    # Check XDG_SESSION_TYPE
    session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()
    if session_type in ("wayland", "x11"):
        return session_type

    # Check WAYLAND_DISPLAY
    if os.environ.get("WAYLAND_DISPLAY"):
        return "wayland"

    # Check DISPLAY (X11)
    if os.environ.get("DISPLAY"):
        return "x11"

    return None


def detect_container() -> bool:
    """Detect if running inside a container (Docker, LXC, etc.).

    Returns:
        True if in container, False otherwise
    """
    # Check for /.dockerenv
    if os.path.exists("/.dockerenv"):
        return True

    # Check /proc/1/cgroup for container indicators
    if os.path.exists("/proc/1/cgroup"):
        try:
            with open("/proc/1/cgroup") as f:
                content = f.read()
                if "docker" in content or "lxc" in content:
                    return True
        except OSError:
            pass

    return False


def detect_vm() -> bool:
    """Detect if running in a virtual machine.

    Returns:
        True if in VM, False otherwise
    """
    system = platform.system().lower()

    if system == "linux":
        # Check for common VM indicators
        try:
            # Check DMI info
            if os.path.exists("/sys/class/dmi/id/product_name"):
                with open("/sys/class/dmi/id/product_name") as f:
                    product = f.read().lower()
                    if any(
                        vm in product for vm in ["virtualbox", "vmware", "qemu", "kvm", "hyper-v"]
                    ):
                        return True
        except OSError:
            pass

    return False


def needs_software_rendering(env_info: Optional[EnvironmentInfo] = None) -> bool:
    """Determine if software rendering is required.

    Args:
        env_info: Pre-detected environment info (optional)

    Returns:
        True if software rendering should be used, False otherwise
    """
    # User has already configured, respect their choice
    if os.environ.get("LIBGL_ALWAYS_SOFTWARE"):
        return False

    # If env_info provided, use it
    if env_info:
        if env_info.is_wsl:
            return True
        if env_info.is_remote_desktop:
            return True
        if env_info.is_container:
            return True
        return False

    # Otherwise detect on the fly
    is_wsl, _ = detect_wsl()
    if is_wsl:
        return True

    if detect_remote_desktop():
        return True

    if detect_container():
        return True

    return False


def detect_capabilities(env_info: EnvironmentInfo) -> tuple[bool, bool, bool]:
    """Detect desktop capabilities.

    Args:
        env_info: Environment information

    Returns:
        Tuple of (supports_system_tray, supports_notifications, supports_global_shortcuts)
    """
    # System tray support
    system_tray = True
    if env_info.is_wsl or env_info.is_remote_desktop:
        system_tray = False

    # Notifications support
    notifications = True
    if env_info.os == "linux" and not env_info.desktop_env:
        notifications = False

    # Global shortcuts support
    global_shortcuts = True
    if env_info.is_wsl or env_info.is_remote_desktop or env_info.is_container:
        global_shortcuts = False

    return system_tray, notifications, global_shortcuts


def detect_environment() -> EnvironmentInfo:
    """Detect complete environment information.

    This is the main entry point for environment detection.

    Returns:
        EnvironmentInfo with all detected information
    """
    # Basic OS info
    os_name = platform.system().lower()
    os_version = platform.release()
    machine = platform.machine()

    # Linux-specific detection
    desktop_env = None
    display_server = None
    session_type = None
    if os_name == "linux":
        desktop_env = detect_desktop_environment()
        display_server = detect_display_server()
        session_type = os.environ.get("XDG_SESSION_TYPE")

    # Special environments
    is_wsl, is_wsl2 = detect_wsl()
    is_remote = detect_remote_desktop()
    is_container = detect_container()
    is_vm = detect_vm()

    # Create partial env info for needs_software_rendering
    partial_env = EnvironmentInfo(
        os=os_name,
        os_version=os_version,
        machine=machine,
        is_wsl=is_wsl,
        is_remote_desktop=is_remote,
        is_container=is_container,
    )

    # Graphics capabilities
    needs_sw_rendering = needs_software_rendering(partial_env)
    has_hw_accel = not needs_sw_rendering

    # Desktop capabilities
    env_info = EnvironmentInfo(
        os=os_name,
        os_version=os_version,
        machine=machine,
        desktop_env=desktop_env,
        display_server=display_server,
        session_type=session_type,
        is_wsl=is_wsl,
        is_wsl2=is_wsl2,
        is_remote_desktop=is_remote,
        is_container=is_container,
        is_vm=is_vm,
        needs_software_rendering=needs_sw_rendering,
        has_hardware_acceleration=has_hw_accel,
    )

    # Detect capabilities
    sys_tray, notif, shortcuts = detect_capabilities(env_info)
    env_info.supports_system_tray = sys_tray
    env_info.supports_notifications = notif
    env_info.supports_global_shortcuts = shortcuts

    logger.debug(f"Detected environment: {os_name}/{desktop_env}/{display_server}")
    if is_wsl:
        logger.debug(f"  WSL detected (WSL2: {is_wsl2})")
    if is_remote:
        logger.debug("  Remote desktop detected")
    if needs_sw_rendering:
        logger.debug("  Software rendering required")

    return env_info
