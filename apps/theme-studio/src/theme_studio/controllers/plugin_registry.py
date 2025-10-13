"""Plugin Registry Controller - Observable plugin discovery system.

This module provides the controller for discovering and managing preview plugins
through Python entry points. Follows Theme Studio's MVC pattern with QObject signals
for observability.

Architecture:
- PluginRegistry: Observable controller (QObject with signals)
- Entry point discovery via importlib.metadata
- Error resilience with comprehensive error signals
- Compatible with Theme Studio's existing MVC patterns

Example:
    registry = PluginRegistry(parent)
    registry.plugin_discovered.connect(on_plugin_discovered)
    registry.discovery_completed.connect(on_discovery_completed)
    plugins = registry.discover_plugins()
"""

import logging
from importlib.metadata import EntryPoint, entry_points
from typing import Optional

from PySide6.QtCore import QObject, Signal
from vfwidgets_theme import PluginAvailability, WidgetMetadata

logger = logging.getLogger(__name__)

__all__ = ["PluginRegistry", "PluginLoadError"]


class PluginLoadError(Exception):
    """Exception raised when a plugin fails to load."""

    pass


class PluginRegistry(QObject):
    """Observable plugin registry controller (MVC Controller).

    This controller manages plugin discovery through Python entry points,
    emitting signals for each discovery event to maintain observability
    consistent with Theme Studio's MVC architecture.

    Signals:
        discovery_started: Emitted when plugin discovery begins
        plugin_discovered(str, WidgetMetadata): Emitted for each discovered plugin
        plugin_failed(str, str): Emitted when a plugin fails to load
        discovery_completed(int): Emitted when discovery finishes (count of plugins)
        plugins_changed(): Emitted when the plugin list changes
        error_occurred(str, str, Exception): Emitted on any error

    Example:
        >>> registry = PluginRegistry(parent_widget)
        >>> registry.plugin_discovered.connect(
        ...     lambda name, meta: print(f"Found: {name}")
        ... )
        >>> plugins = registry.discover_plugins()
    """

    # Signals for observable pattern
    discovery_started = Signal()
    plugin_discovered = Signal(str, object)  # (plugin_name, WidgetMetadata)
    plugin_failed = Signal(str, str)  # (plugin_name, error_message)
    discovery_completed = Signal(int)  # (plugin_count)
    plugins_changed = Signal()
    error_occurred = Signal(str, str, Exception)  # (context, message, exception)

    ENTRY_POINT_GROUP = "vfwidgets.preview"

    def __init__(self, parent: Optional[QObject] = None):
        """Initialize the plugin registry.

        Args:
            parent: Parent QObject for proper Qt ownership
        """
        super().__init__(parent)
        self._plugins: dict[str, WidgetMetadata] = {}
        self._discovered = False

    @property
    def plugins(self) -> dict[str, WidgetMetadata]:
        """Get the dictionary of discovered plugins.

        Returns:
            Dictionary mapping plugin names to WidgetMetadata.
        """
        return self._plugins.copy()

    @property
    def available_plugins(self) -> dict[str, WidgetMetadata]:
        """Get only the available (not errored) plugins.

        Returns:
            Dictionary of plugins with AVAILABLE status.
        """
        return {
            name: metadata
            for name, metadata in self._plugins.items()
            if metadata.is_available
        }

    def discover_plugins(self) -> dict[str, WidgetMetadata]:
        """Discover plugins via entry points, emit signals.

        This method scans for entry points in the 'vfwidgets.preview' group,
        loads their metadata, and emits signals for each discovery event.

        Returns:
            Dictionary mapping plugin names to WidgetMetadata.

        Example:
            >>> registry = PluginRegistry()
            >>> plugins = registry.discover_plugins()
            >>> for name, metadata in plugins.items():
            ...     print(f"{name}: {metadata.version}")
        """
        self.discovery_started.emit()
        self._plugins.clear()
        discovered_count = 0

        try:
            eps = entry_points(group=self.ENTRY_POINT_GROUP)
        except Exception as e:
            error_msg = f"Failed to read entry points: {e}"
            logger.error(error_msg)
            self.error_occurred.emit("discover_plugins", error_msg, e)
            self.discovery_completed.emit(0)
            return {}

        for ep in eps:
            try:
                metadata = self._load_entry_point_safe(ep)
                self._plugins[ep.name] = metadata

                if metadata.is_available:
                    self.plugin_discovered.emit(ep.name, metadata)
                    discovered_count += 1
                    logger.info(f"Discovered plugin: {ep.name} v{metadata.version}")
                else:
                    self.plugin_failed.emit(ep.name, metadata.error_message or "Unknown error")
                    logger.warning(
                        f"Plugin '{ep.name}' not available: {metadata.error_message}"
                    )

            except PluginLoadError as e:
                error_metadata = self._create_error_metadata(ep, e)
                self._plugins[ep.name] = error_metadata
                self.plugin_failed.emit(ep.name, str(e))
                logger.error(f"Failed to load plugin '{ep.name}': {e}")

            except Exception as e:
                error_msg = f"Unexpected error loading plugin '{ep.name}': {e}"
                self.error_occurred.emit("discover_plugins", error_msg, e)
                logger.exception(error_msg)

                error_metadata = self._create_error_metadata(
                    ep, PluginLoadError(f"Unexpected error: {e}")
                )
                self._plugins[ep.name] = error_metadata
                self.plugin_failed.emit(ep.name, str(e))

        self._discovered = True
        self.plugins_changed.emit()
        self.discovery_completed.emit(discovered_count)
        logger.info(
            f"Plugin discovery completed: {discovered_count} available, "
            f"{len(self._plugins) - discovered_count} failed"
        )

        return self.plugins

    def refresh_plugins(self) -> dict[str, WidgetMetadata]:
        """Refresh plugin discovery.

        Re-scans entry points and updates the plugin registry.

        Returns:
            Updated dictionary of plugins.
        """
        logger.info("Refreshing plugin registry")
        return self.discover_plugins()

    def get_plugin(self, name: str) -> Optional[WidgetMetadata]:
        """Get metadata for a specific plugin by name.

        Args:
            name: Plugin name (entry point name)

        Returns:
            WidgetMetadata if found, None otherwise
        """
        return self._plugins.get(name)

    def _load_entry_point_safe(self, ep: EntryPoint) -> WidgetMetadata:
        """Safely load entry point and validate metadata.

        Args:
            ep: EntryPoint to load

        Returns:
            WidgetMetadata from the entry point

        Raises:
            PluginLoadError: If loading or validation fails
        """
        try:
            # Load the entry point (should return a callable)
            get_metadata_func = ep.load()
        except ImportError as e:
            raise PluginLoadError(f"Import error: {e}") from e
        except Exception as e:
            raise PluginLoadError(f"Failed to load entry point: {e}") from e

        # Call the function to get metadata
        if not callable(get_metadata_func):
            raise PluginLoadError(
                f"Entry point '{ep.name}' must be a callable returning WidgetMetadata"
            )

        try:
            metadata = get_metadata_func()
        except Exception as e:
            raise PluginLoadError(f"Error calling metadata function: {e}") from e

        # Validate metadata type
        if not isinstance(metadata, WidgetMetadata):
            raise PluginLoadError(
                f"Entry point must return WidgetMetadata, got {type(metadata).__name__}"
            )

        # Validate metadata contents
        is_valid, error_msg = metadata.validate()
        if not is_valid:
            raise PluginLoadError(f"Invalid metadata: {error_msg}")

        return metadata

    def _create_error_metadata(self, ep: EntryPoint, error: PluginLoadError) -> WidgetMetadata:
        """Create error metadata for a failed plugin load.

        Args:
            ep: EntryPoint that failed to load
            error: Exception that occurred

        Returns:
            WidgetMetadata with error status
        """
        return WidgetMetadata(
            name=ep.name,
            widget_class_name="Unknown",
            package_name=ep.value.split(":")[0] if ":" in ep.value else ep.value,
            version="unknown",
            theme_tokens={},
            availability=PluginAvailability.IMPORT_ERROR,
            error_message=str(error),
        )
