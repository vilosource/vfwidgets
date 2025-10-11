"""VFWidgets Common - Shared utilities and base classes for VFWidgets."""

__version__ = "0.1.0"

from .base_widget import VFBaseWidget
from .frameless import FramelessWindowBehavior
from .platform import (
    configure_qt_environment,
    get_desktop_environment,
    get_platform_info,
    is_remote_desktop,
    is_wsl,
    needs_software_rendering,
)
from .single_instance import SingleInstanceApplication
from .utils import load_widget_icon, setup_widget_style
from .webengine import (
    configure_all_for_webengine,
    configure_webengine_environment,
    get_webengine_info,
    log_webengine_configuration,
)

__all__ = [
    # Base classes
    "VFBaseWidget",
    # Frameless window behavior
    "FramelessWindowBehavior",
    # Single instance application
    "SingleInstanceApplication",
    # Utilities
    "setup_widget_style",
    "load_widget_icon",
    # Platform detection
    "is_wsl",
    "is_remote_desktop",
    "get_desktop_environment",
    "needs_software_rendering",
    "configure_qt_environment",
    "get_platform_info",
    # WebEngine configuration
    "configure_webengine_environment",
    "configure_all_for_webengine",
    "get_webengine_info",
    "log_webengine_configuration",
]
