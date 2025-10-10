"""Configuration dataclasses for desktop integration."""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class DesktopConfig:
    """Configuration for desktop integration.

    Args:
        app_name: Internal application name (e.g., "viloxterm")
        app_display_name: Display name shown to users (e.g., "ViloxTerm")
        icon_name: Name of the icon (e.g., "viloxterm")
        desktop_categories: Desktop menu categories (Linux, e.g., "System;TerminalEmulator;")
        auto_install: Whether to automatically install desktop integration if missing
        create_application: Whether to create QApplication instance
        application_class: QApplication class to use (default: PySide6.QtWidgets.QApplication)
        application_kwargs: Additional kwargs passed to application_class constructor
    """

    app_name: str
    app_display_name: str
    icon_name: str
    desktop_categories: str = ""
    auto_install: bool = True
    create_application: bool = True
    application_class: Optional[type] = None
    application_kwargs: dict[str, Any] = field(default_factory=dict)


@dataclass
class EnvironmentInfo:
    """Complete environment information for platform detection.

    This consolidates all platform detection into a single structure.
    """

    # Operating System
    os: str  # "linux", "windows", "darwin"
    os_version: str
    machine: str  # "x86_64", "arm64", etc.

    # Desktop Environment (Linux)
    desktop_env: Optional[str] = None  # "GNOME", "KDE", "XFCE", "MATE", "Cinnamon"
    display_server: Optional[str] = None  # "wayland", "x11"
    session_type: Optional[str] = None  # From XDG_SESSION_TYPE

    # Special Environments
    is_wsl: bool = False
    is_wsl2: bool = False  # WSL2 vs WSL1
    is_remote_desktop: bool = False
    is_container: bool = False  # Docker, etc.
    is_vm: bool = False  # VirtualBox, VMware, etc.

    # Graphics Capabilities
    needs_software_rendering: bool = False
    has_hardware_acceleration: bool = True

    # Desktop Capabilities
    supports_system_tray: bool = True
    supports_notifications: bool = True
    supports_global_shortcuts: bool = True


@dataclass
class IntegrationStatus:
    """Status of desktop integration installation.

    Args:
        is_installed: Whether desktop integration is fully installed
        has_desktop_file: Whether desktop entry file exists
        has_icon: Whether application icon exists
        missing_files: List of missing integration files
        platform_name: Name of the platform (e.g., "Linux XDG", "Windows", "macOS")
        desktop_environment: Detected desktop environment if applicable
    """

    is_installed: bool
    has_desktop_file: bool
    has_icon: bool
    missing_files: list[str]
    platform_name: str
    desktop_environment: Optional[str] = None
