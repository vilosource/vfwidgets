"""Discovered Widget Plugin - Adapter for dynamically discovered plugins.

This module provides the view adapter that bridges dynamically discovered
widgets (via entry points) to Theme Studio's PreviewPlugin interface.

Architecture:
- DiscoveredWidgetPlugin: View adapter implementing PreviewPlugin
- Delegates widget creation to PluginWidgetFactory (controller)
- Separates view concerns (adapter interface) from controller (creation logic)

Example:
    plugin = DiscoveredWidgetPlugin(metadata)
    widget = plugin.create_preview_widget(parent=container)
"""

from typing import Optional

from PySide6.QtWidgets import QWidget
from vfwidgets_theme import WidgetMetadata

from ..controllers.plugin_factory import PluginWidgetFactory
from .plugin_base import PreviewPlugin

__all__ = ["DiscoveredWidgetPlugin"]


class DiscoveredWidgetPlugin(PreviewPlugin):
    """Preview plugin adapter for dynamically discovered widgets (MVC View).

    This adapter implements the PreviewPlugin interface for widgets discovered
    through entry points, delegating widget creation to PluginWidgetFactory
    (controller) for clean separation of concerns.

    Example:
        >>> plugin = DiscoveredWidgetPlugin(metadata)
        >>> print(plugin.get_name())
        'Terminal Widget'
        >>> widget = plugin.create_preview_widget(parent=container)
    """

    def __init__(self, metadata: WidgetMetadata):
        """Initialize the plugin adapter with metadata.

        Args:
            metadata: WidgetMetadata from plugin discovery
        """
        self.metadata = metadata
        self.factory = PluginWidgetFactory(metadata)

    def get_name(self) -> str:
        """Get plugin display name.

        Returns:
            Plugin name for display in UI
        """
        return self.metadata.name

    def get_description(self) -> str:
        """Get plugin description.

        Returns:
            Brief description of what this plugin previews
        """
        if self.metadata.preview_description:
            return self.metadata.preview_description

        # Generate description from metadata
        parts = [
            f"{self.metadata.widget_class_name} from {self.metadata.package_name}",
        ]

        if self.metadata.token_count > 0:
            parts.append(f"({self.metadata.token_count} theme tokens)")

        if not self.metadata.is_available:
            parts.append(f"[Unavailable: {self.metadata.error_message}]")

        return " ".join(parts)

    def create_preview_widget(self, parent: Optional[QWidget] = None) -> QWidget:
        """Create the preview widget.

        This widget will be displayed in the preview canvas and should
        demonstrate the theme's appearance. Delegates to PluginWidgetFactory
        (controller) for actual creation.

        Args:
            parent: Parent widget

        Returns:
            QWidget to display in canvas (either actual preview or fallback)
        """
        return self.factory.create_widget(parent)

    def is_available(self) -> bool:
        """Check if the plugin is available for use.

        Returns:
            True if plugin can create widgets, False if errored
        """
        return self.metadata.is_available

    def get_token_categories(self) -> list[str]:
        """Get token categories used by this widget.

        Returns:
            List of token category names (e.g., ['editor', 'terminal'])
        """
        return self.metadata.token_categories

    def get_token_count(self) -> int:
        """Get the number of theme tokens used by this widget.

        Returns:
            Count of theme tokens
        """
        return self.metadata.token_count
