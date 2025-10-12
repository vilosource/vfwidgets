"""Base class for preview plugins."""

from abc import ABC, abstractmethod

from PySide6.QtWidgets import QWidget


class PreviewPlugin(ABC):
    """Base class for preview plugins.

    Plugins create widgets that demonstrate how the theme looks
    on different UI components.

    Phase 1: Static widget display
    Phase 2: Interactive state simulation
    """

    @abstractmethod
    def get_name(self) -> str:
        """Get plugin display name.

        Returns:
            Plugin name for display in UI
        """
        pass

    @abstractmethod
    def create_preview_widget(self, parent=None) -> QWidget:
        """Create the preview widget.

        This widget will be displayed in the preview canvas and should
        demonstrate the theme's appearance.

        Args:
            parent: Parent widget

        Returns:
            QWidget to display in canvas
        """
        pass

    def get_description(self) -> str:
        """Get plugin description.

        Returns:
            Brief description of what this plugin previews
        """
        return ""
