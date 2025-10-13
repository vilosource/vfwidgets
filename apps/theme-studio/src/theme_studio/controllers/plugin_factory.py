"""Plugin Widget Factory - Controller for creating preview widget instances.

This module provides the factory controller for safely creating preview widget
instances from plugin metadata, with comprehensive error handling and fallback
widgets for unavailable plugins.

Architecture:
- PluginWidgetFactory: Controller for widget instantiation
- Error handling with fallback widgets
- Separated from view (DiscoveredWidgetPlugin) for clean MVC

Example:
    factory = PluginWidgetFactory(metadata)
    widget = factory.create_widget(parent=container)
"""

import logging
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from vfwidgets_theme import WidgetMetadata

logger = logging.getLogger(__name__)

__all__ = ["PluginWidgetFactory"]


class PluginWidgetFactory:
    """Controller for creating preview widget instances.

    This factory handles the creation of preview widgets from metadata,
    providing error handling and fallback widgets when plugins are
    unavailable or fail to instantiate.

    Example:
        >>> factory = PluginWidgetFactory(metadata)
        >>> widget = factory.create_widget(parent=container)
    """

    def __init__(self, metadata: WidgetMetadata):
        """Initialize the factory with plugin metadata.

        Args:
            metadata: WidgetMetadata describing the plugin
        """
        self.metadata = metadata

    def create_widget(self, parent: Optional[QWidget] = None) -> QWidget:
        """Create a preview widget instance.

        This method attempts to create a widget using the plugin's preview_factory.
        If the plugin is unavailable or creation fails, it returns an appropriate
        fallback widget.

        Args:
            parent: Parent widget for Qt ownership

        Returns:
            Widget instance (either actual preview or fallback)

        Example:
            >>> widget = factory.create_widget(parent=container)
        """
        # Check availability
        if not self.metadata.is_available:
            logger.warning(
                f"Plugin '{self.metadata.name}' not available: {self.metadata.error_message}"
            )
            return self._create_unavailable_widget(parent)

        # Check for preview factory
        if self.metadata.preview_factory is None:
            error_msg = f"Plugin '{self.metadata.name}' has no preview_factory"
            logger.error(error_msg)
            return self._create_error_widget(parent, error_msg)

        # Attempt to create widget
        try:
            config = self.metadata.preview_config or {}
            widget = self.metadata.preview_factory(parent, **config)

            if not isinstance(widget, QWidget):
                error_msg = (
                    f"preview_factory returned {type(widget).__name__}, "
                    f"expected QWidget subclass"
                )
                logger.error(error_msg)
                return self._create_error_widget(parent, error_msg)

            logger.info(f"Created preview widget for plugin '{self.metadata.name}'")
            return widget

        except Exception as e:
            error_msg = f"Failed to create widget: {e}"
            logger.exception(f"Plugin '{self.metadata.name}': {error_msg}")
            return self._create_error_widget(parent, error_msg)

    def _create_unavailable_widget(self, parent: Optional[QWidget] = None) -> QWidget:
        """Create a fallback widget for unavailable plugins.

        Args:
            parent: Parent widget

        Returns:
            Widget displaying unavailability information
        """
        widget = QWidget(parent)
        layout = QVBoxLayout(widget)

        # Title
        title = QLabel(f"<b>{self.metadata.name}</b>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Status
        status = QLabel("⚠ Plugin Not Available")
        status.setStyleSheet("color: #ff9800; font-size: 14px;")
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(status)

        # Error message
        if self.metadata.error_message:
            error_label = QLabel(self.metadata.error_message)
            error_label.setWordWrap(True)
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet("color: #666; font-size: 11px; margin: 10px;")
            layout.addWidget(error_label)

        # Package info
        info = QLabel(f"Package: {self.metadata.package_name}")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet("color: #888; font-size: 10px;")
        layout.addWidget(info)

        layout.addStretch()
        widget.setMinimumSize(300, 200)
        return widget

    def _create_error_widget(
        self, parent: Optional[QWidget] = None, error_message: str = "Unknown error"
    ) -> QWidget:
        """Create a fallback widget for creation errors.

        Args:
            parent: Parent widget
            error_message: Error message to display

        Returns:
            Widget displaying error information
        """
        widget = QWidget(parent)
        layout = QVBoxLayout(widget)

        # Title
        title = QLabel(f"<b>{self.metadata.name}</b>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Status
        status = QLabel("❌ Widget Creation Failed")
        status.setStyleSheet("color: #f44336; font-size: 14px;")
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(status)

        # Error message
        error_label = QLabel(error_message)
        error_label.setWordWrap(True)
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_label.setStyleSheet("color: #666; font-size: 11px; margin: 10px;")
        layout.addWidget(error_label)

        # Package info
        info = QLabel(f"Package: {self.metadata.package_name}")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet("color: #888; font-size: 10px;")
        layout.addWidget(info)

        layout.addStretch()
        widget.setMinimumSize(300, 200)
        return widget
