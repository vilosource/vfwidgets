"""Preview plugins for VFTheme Studio.

Plugins provide widget previews that demonstrate theme appearance.
"""

from .generic_widgets import GenericWidgetsPlugin
from .plugin_base import PreviewPlugin

__all__ = ["PreviewPlugin", "GenericWidgetsPlugin"]
