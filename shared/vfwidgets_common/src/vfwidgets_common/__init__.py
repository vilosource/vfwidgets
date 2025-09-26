"""VFWidgets Common - Shared utilities and base classes for VFWidgets."""

__version__ = "0.1.0"

from .base_widget import VFBaseWidget
from .utils import load_widget_icon, setup_widget_style

__all__ = [
    "VFBaseWidget",
    "setup_widget_style",
    "load_widget_icon",
]
