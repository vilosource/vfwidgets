"""Preview plugins for VFTheme Studio.

Plugins provide widget previews that demonstrate theme appearance.
"""

from .discovered_plugin import DiscoveredWidgetPlugin
from .generic_widgets import GenericWidgetsPlugin
from .plugin_base import PreviewPlugin

__all__ = ["PreviewPlugin", "GenericWidgetsPlugin", "DiscoveredWidgetPlugin"]
