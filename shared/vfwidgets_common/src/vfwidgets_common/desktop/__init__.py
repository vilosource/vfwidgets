"""Unified cross-platform desktop integration for VFWidgets.

This module provides comprehensive desktop integration including:
- Platform detection (OS, desktop environment, display server)
- Platform-specific quirks and workarounds
- Desktop integration (icons, .desktop files, shortcuts)
- Application configuration and setup

Example:
    from vfwidgets_common.desktop import configure_desktop

    app = configure_desktop(
        app_name="viloxterm",
        app_display_name="ViloxTerm",
        icon_name="viloxterm",
        desktop_categories="System;TerminalEmulator;",
    )

    window = MyMainWindow()
    window.show()
    sys.exit(app.exec())
"""

from typing import Any, Optional

from .config import DesktopConfig, EnvironmentInfo, IntegrationStatus
from .configurator import DesktopConfigurator
from .environment import detect_environment


def configure_desktop(
    app_name: str,
    app_display_name: str,
    icon_name: str,
    desktop_categories: Optional[str] = None,
    auto_install: bool = True,
    application_class: Optional[type] = None,
    **application_kwargs: Any,
):
    """Configure desktop integration and create QApplication.

    This is the main entry point for desktop configuration. It handles:
    - Platform detection (WSL, Wayland, X11, etc.)
    - Platform-specific quirks (software rendering, scaling fixes)
    - Desktop integration (icons, .desktop files)
    - QApplication creation with proper metadata

    Args:
        app_name: Internal application name (e.g., "viloxterm")
        app_display_name: Display name shown to users (e.g., "ViloxTerm")
        icon_name: Name of the icon (e.g., "viloxterm")
        desktop_categories: Desktop menu categories (e.g., "System;TerminalEmulator;")
        auto_install: Whether to auto-install desktop integration if missing
        application_class: QApplication class to use (default: PySide6.QtWidgets.QApplication)
        **application_kwargs: Additional kwargs passed to application_class constructor

    Returns:
        Configured QApplication instance

    Example:
        from vfwidgets_common.desktop import configure_desktop

        app = configure_desktop(
            app_name="viloxterm",
            app_display_name="ViloxTerm",
            icon_name="viloxterm",
            desktop_categories="System;TerminalEmulator;",
        )

        window = MyMainWindow()
        window.show()
        sys.exit(app.exec())
    """
    config = DesktopConfig(
        app_name=app_name,
        app_display_name=app_display_name,
        icon_name=icon_name,
        desktop_categories=desktop_categories or "",
        auto_install=auto_install,
        create_application=True,
        application_class=application_class,
        application_kwargs=application_kwargs,
    )

    configurator = DesktopConfigurator(config)
    return configurator.configure()


__all__ = [
    "configure_desktop",
    "DesktopConfig",
    "DesktopConfigurator",
    "EnvironmentInfo",
    "IntegrationStatus",
    "detect_environment",
]
