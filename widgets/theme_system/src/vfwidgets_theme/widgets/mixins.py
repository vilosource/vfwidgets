"""Theming mixins for composable behavior.

This module provides mixins that can be combined with any widget class
to add theming capabilities. This provides an alternative to inheritance
for adding theming to existing widget classes.

Key Classes:
- ThemeableMixin: Core theming behavior for any widget
- PropertyMixin: Standalone property access capabilities
- NotificationMixin: Theme change notification handling
- CacheMixin: Property caching capabilities
- LifecycleMixin: Cleanup and registration management

Task 9 Implementation Features:
- Composable theming behavior through mixins
- Support for existing Qt widget classes
- Property-based theming without inheritance
- Lifecycle management for mixed-in widgets
- Performance optimization through caching
"""

import threading
import uuid
import weakref
from typing import TYPE_CHECKING, Any, Callable, Optional

try:
    from PySide6.QtCore import QObject, Signal, pyqtSignal
    from PySide6.QtWidgets import QWidget

    QT_AVAILABLE = True
except ImportError:
    # Fallback for testing without Qt
    QT_AVAILABLE = False

    class QWidget:
        def __init__(self, parent=None):
            pass

        def setStyleSheet(self, stylesheet):
            pass

        def update(self):
            pass

    class QObject:
        pass

    class Signal:
        def __init__(self, *args):
            self._callbacks = []

        def emit(self, *args):
            for callback in self._callbacks:
                try:
                    callback(*args)
                except Exception:
                    pass

        def connect(self, callback):
            self._callbacks.append(callback)

    pyqtSignal = Signal

# Import foundation modules
from ..core.manager import ThemeManager
from ..core.theme import Theme
from ..errors import ThemeError, get_global_error_recovery_manager
from ..lifecycle import LifecycleManager, WidgetRegistry
from ..logging import get_debug_logger

if TYPE_CHECKING:
    from .base import ThemeAccess, ThemePropertiesManager

logger = get_debug_logger(__name__)


class ThemeableMixin:
    """Mixin for adding theming capabilities to any widget.

    This mixin can be combined with any widget class to add
    theming support without requiring inheritance from ThemedWidget.

    Usage:
        class MyWidget(QWidget, ThemeableMixin):
            def __init__(self):
                super().__init__()
                self.setup_theming()

    The mixin provides:
    - Automatic theme registration and cleanup
    - Property-based theme access
    - Theme change notifications
    - Error recovery and fallbacks
    """

    def __init__(self, *args, **kwargs):
        """Initialize themeable mixin."""
        super().__init__(*args, **kwargs)

        # Themeable mixin state
        self._themeable_widget_id: Optional[str] = None
        self._themeable_manager: Optional[ThemeManager] = None
        self._themeable_properties: Optional[ThemePropertiesManager] = None
        self._themeable_access: Optional[ThemeAccess] = None
        self._is_themeable_registered = False
        self._is_themeable_ready = False

    def setup_theming(self, theme_config: Optional[dict[str, str]] = None) -> None:
        """Set up theming for this widget.

        Args:
            theme_config: Optional theme property mapping

        """
        try:
            # Generate unique widget ID
            self._themeable_widget_id = str(uuid.uuid4())

            # Get theme manager instance
            self._themeable_manager = ThemeManager.get_instance()

            # Import here to avoid circular imports
            from .base import ThemeAccess, ThemePropertiesManager

            # Set up properties manager
            self._themeable_properties = ThemePropertiesManager(self)
            self._themeable_access = ThemeAccess(self)

            # Register with widget registry
            registry = WidgetRegistry.get_instance()
            registry.register_widget(self._themeable_widget_id, weakref.ref(self))
            self._is_themeable_registered = True

            # Connect to theme changes
            if self._themeable_manager:
                try:
                    self._themeable_manager.theme_changed.connect(self._on_themeable_theme_changed)
                except Exception as e:
                    logger.warning(f"Could not connect theme change signal: {e}")

            # Set theme config if provided
            if theme_config:
                self._themeable_config = theme_config

            self._is_themeable_ready = True

            logger.debug(f"Theming set up for mixin widget {self._themeable_widget_id}")

        except Exception as e:
            logger.error(f"Error setting up theming mixin: {e}")
            self._is_themeable_ready = False

            # Use error recovery
            error_manager = get_global_error_recovery_manager()
            error_manager.handle_error(
                ThemeError(f"Themeable mixin setup failed: {e}"),
                context={
                    "widget_type": type(self).__name__,
                    "widget_id": getattr(self, "_themeable_widget_id", None),
                },
            )

    @property
    def theme(self) -> Optional["ThemeAccess"]:
        """Get theme property access object."""
        return self._themeable_access

    @property
    def is_themeable_ready(self) -> bool:
        """Check if themeable mixin is ready."""
        return self._is_themeable_ready

    def _get_theme_property(self, property_path: str, default_value: Any = None) -> Any:
        """Get theme property through the properties manager."""
        if self._themeable_properties:
            return self._themeable_properties.get_property(property_path, default_value)
        return default_value

    def _set_theme_property(self, property_path: str, value: Any) -> None:
        """Set theme property through the properties manager."""
        if self._themeable_properties:
            self._themeable_properties.set_property(property_path, value)

    def _on_themeable_theme_changed(self, theme: Theme) -> None:
        """Handle theme change notifications."""
        try:
            if not self._is_themeable_ready:
                return

            # Invalidate property cache
            if self._themeable_properties:
                self._themeable_properties.invalidate_cache()

            # Call user-defined handler if it exists
            if hasattr(self, "on_theme_changed") and callable(self.on_theme_changed):
                try:
                    self.on_theme_changed()
                except Exception as e:
                    logger.error(f"Error in user theme change handler: {e}")

            # Update widget if it has styling methods
            if hasattr(self, "setStyleSheet"):
                stylesheet = self._generate_themeable_stylesheet()
                if stylesheet:
                    self.setStyleSheet(stylesheet)

            # Update widget if it has update method
            if hasattr(self, "update"):
                self.update()

            logger.debug(f"Theme changed for themeable mixin widget {self._themeable_widget_id}")

        except Exception as e:
            logger.error(f"Error handling theme change in mixin: {e}")

    def _generate_themeable_stylesheet(self) -> str:
        """Generate stylesheet for themeable widget."""
        try:
            if not self._is_themeable_ready or not self._themeable_access:
                return ""

            # Get basic theme properties
            background = self._themeable_access.get("background", "#ffffff")
            color = self._themeable_access.get("color", "#000000")

            # Generate basic stylesheet
            stylesheet = f"""
            {self.__class__.__name__} {{
                background-color: {background};
                color: {color};
            }}
            """

            return stylesheet.strip()

        except Exception as e:
            logger.error(f"Error generating stylesheet for themeable mixin: {e}")
            return ""

    def cleanup_theming(self) -> None:
        """Clean up themeable mixin resources."""
        try:
            if self._is_themeable_registered:
                # Disconnect signals
                if self._themeable_manager:
                    try:
                        self._themeable_manager.theme_changed.disconnect(
                            self._on_themeable_theme_changed
                        )
                    except Exception:
                        pass  # May already be disconnected

                # Unregister from registry
                if self._themeable_widget_id:
                    registry = WidgetRegistry.get_instance()
                    registry.unregister_widget(self._themeable_widget_id)

                self._is_themeable_registered = False

            # Clear references
            self._themeable_manager = None
            self._themeable_properties = None
            self._themeable_access = None

            logger.debug(
                f"Themeable mixin cleanup completed for widget {self._themeable_widget_id}"
            )

        except Exception as e:
            logger.error(f"Error during themeable mixin cleanup: {e}")


class PropertyMixin:
    """Mixin for standalone property access capabilities.

    Provides property-based theme access without full theming setup.
    Useful for widgets that only need property access.
    """

    def __init__(self, *args, **kwargs):
        """Initialize property mixin."""
        super().__init__(*args, **kwargs)
        self._property_manager: Optional[ThemePropertiesManager] = None
        self._property_access: Optional[ThemeAccess] = None

    def setup_properties(self) -> None:
        """Set up property access."""
        try:
            # Import here to avoid circular imports
            from .base import ThemeAccess, ThemePropertiesManager

            self._property_manager = ThemePropertiesManager(self)
            self._property_access = ThemeAccess(self)

            logger.debug("Property access set up")

        except Exception as e:
            logger.error(f"Error setting up property access: {e}")

    @property
    def properties(self) -> Optional["ThemeAccess"]:
        """Get property access object."""
        return self._property_access

    def get_property(self, property_path: str, default_value: Any = None) -> Any:
        """Get property value."""
        if self._property_manager:
            return self._property_manager.get_property(property_path, default_value)
        return default_value

    def set_property(self, property_path: str, value: Any) -> None:
        """Set property value."""
        if self._property_manager:
            self._property_manager.set_property(property_path, value)


class NotificationMixin:
    """Mixin for theme change notification handling.

    Provides theme change notification capabilities without full theming.
    """

    def __init__(self, *args, **kwargs):
        """Initialize notification mixin."""
        super().__init__(*args, **kwargs)

        # Create Qt signals if available
        if QT_AVAILABLE:
            if not hasattr(self, "theme_changed"):
                self.theme_changed = pyqtSignal(str)
            if not hasattr(self, "theme_applied"):
                self.theme_applied = pyqtSignal()
        else:
            if not hasattr(self, "theme_changed"):
                self.theme_changed = Signal(str)
            if not hasattr(self, "theme_applied"):
                self.theme_applied = Signal()

        self._notification_manager: Optional[ThemeManager] = None
        self._notification_callbacks: set[Callable] = set()

    def setup_notifications(self) -> None:
        """Set up theme change notifications."""
        try:
            self._notification_manager = ThemeManager.get_instance()

            if self._notification_manager:
                try:
                    self._notification_manager.theme_changed.connect(
                        self._on_notification_theme_changed
                    )
                except Exception as e:
                    logger.warning(f"Could not connect notification signal: {e}")

            logger.debug("Theme notifications set up")

        except Exception as e:
            logger.error(f"Error setting up theme notifications: {e}")

    def add_theme_change_callback(self, callback: Callable[[Theme], None]) -> None:
        """Add a theme change callback."""
        self._notification_callbacks.add(callback)

    def remove_theme_change_callback(self, callback: Callable[[Theme], None]) -> None:
        """Remove a theme change callback."""
        self._notification_callbacks.discard(callback)

    def _on_notification_theme_changed(self, theme: Theme) -> None:
        """Handle theme change notifications."""
        try:
            # Emit Qt signals
            if hasattr(self, "theme_changed"):
                self.theme_changed.emit(theme.name)
            if hasattr(self, "theme_applied"):
                self.theme_applied.emit()

            # Call registered callbacks
            for callback in self._notification_callbacks:
                try:
                    callback(theme)
                except Exception as e:
                    logger.error(f"Error in theme change callback: {e}")

            # Call user-defined handler if it exists
            if hasattr(self, "on_theme_changed") and callable(self.on_theme_changed):
                try:
                    self.on_theme_changed()
                except Exception as e:
                    logger.error(f"Error in user theme change handler: {e}")

        except Exception as e:
            logger.error(f"Error handling theme change notification: {e}")


class CacheMixin:
    """Mixin for property caching capabilities.

    Provides efficient property caching for performance optimization.
    """

    def __init__(self, *args, **kwargs):
        """Initialize cache mixin."""
        super().__init__(*args, **kwargs)
        self._cache: dict[str, Any] = {}
        self._cache_lock = threading.RLock()
        self._cache_hits = 0
        self._cache_misses = 0

    def get_cached_property(self, property_path: str, getter: Callable[[], Any]) -> Any:
        """Get property with caching."""
        with self._cache_lock:
            if property_path in self._cache:
                self._cache_hits += 1
                return self._cache[property_path]

            self._cache_misses += 1
            value = getter()
            self._cache[property_path] = value
            return value

    def set_cached_property(self, property_path: str, value: Any) -> None:
        """Set cached property value."""
        with self._cache_lock:
            self._cache[property_path] = value

    def invalidate_cache(self, property_path: Optional[str] = None) -> None:
        """Invalidate cache (specific property or all)."""
        with self._cache_lock:
            if property_path:
                self._cache.pop(property_path, None)
            else:
                self._cache.clear()

    @property
    def cache_hit_rate(self) -> float:
        """Get cache hit rate."""
        total = self._cache_hits + self._cache_misses
        return self._cache_hits / total if total > 0 else 0.0

    def get_cache_statistics(self) -> dict[str, Any]:
        """Get cache statistics."""
        return {
            "cache_size": len(self._cache),
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "hit_rate": self.cache_hit_rate,
        }


class LifecycleMixin:
    """Mixin for cleanup and registration management.

    Provides automatic lifecycle management for mixed-in widgets.
    """

    def __init__(self, *args, **kwargs):
        """Initialize lifecycle mixin."""
        super().__init__(*args, **kwargs)
        self._lifecycle_widget_id: Optional[str] = None
        self._lifecycle_manager: Optional[LifecycleManager] = None
        self._is_lifecycle_registered = False

    def setup_lifecycle(self) -> None:
        """Set up lifecycle management."""
        try:
            self._lifecycle_widget_id = str(uuid.uuid4())
            self._lifecycle_manager = LifecycleManager.get_instance()

            # Register with widget registry
            registry = WidgetRegistry.get_instance()
            registry.register_widget(self._lifecycle_widget_id, weakref.ref(self))
            self._is_lifecycle_registered = True

            logger.debug(f"Lifecycle management set up for widget {self._lifecycle_widget_id}")

        except Exception as e:
            logger.error(f"Error setting up lifecycle management: {e}")

    def cleanup_lifecycle(self) -> None:
        """Clean up lifecycle management."""
        try:
            if self._is_lifecycle_registered and self._lifecycle_widget_id:
                registry = WidgetRegistry.get_instance()
                registry.unregister_widget(self._lifecycle_widget_id)
                self._is_lifecycle_registered = False

            self._lifecycle_manager = None

            logger.debug(f"Lifecycle cleanup completed for widget {self._lifecycle_widget_id}")

        except Exception as e:
            logger.error(f"Error during lifecycle cleanup: {e}")

    def __del__(self) -> None:
        """Automatic cleanup on destruction."""
        try:
            self.cleanup_lifecycle()
        except Exception:
            # Ignore errors during destruction
            pass


class CompositeMixin(ThemeableMixin, PropertyMixin, NotificationMixin, CacheMixin, LifecycleMixin):
    """Composite mixin providing all theming capabilities.

    Combines all theming mixins into a single convenient mixin.
    This provides the most complete theming support for widgets
    that need all capabilities.

    Usage:
        class MyWidget(QWidget, CompositeMixin):
            def __init__(self):
                super().__init__()
                self.setup_complete_theming()
    """

    def __init__(self, *args, **kwargs):
        """Initialize composite mixin."""
        super().__init__(*args, **kwargs)

    def setup_complete_theming(self, theme_config: Optional[dict[str, str]] = None) -> None:
        """Set up complete theming with all capabilities."""
        try:
            # Set up all components
            self.setup_theming(theme_config)
            self.setup_properties()
            self.setup_notifications()
            self.setup_lifecycle()

            logger.debug("Complete theming setup completed")

        except Exception as e:
            logger.error(f"Error setting up complete theming: {e}")

    def cleanup_complete_theming(self) -> None:
        """Clean up all theming components."""
        try:
            # Clean up all components
            self.cleanup_theming()
            self.cleanup_lifecycle()

            logger.debug("Complete theming cleanup completed")

        except Exception as e:
            logger.error(f"Error during complete theming cleanup: {e}")


# Utility functions for mixin usage
def add_theming_to_widget(widget: QWidget, theme_config: Optional[dict[str, str]] = None) -> bool:
    """Add theming capabilities to an existing widget instance.

    This function dynamically adds theming to a widget that wasn't
    originally designed with theming support.

    Args:
        widget: Widget to add theming to
        theme_config: Optional theme configuration

    Returns:
        True if theming was added successfully, False otherwise

    """
    try:
        # Check if widget already has theming
        if hasattr(widget, "_is_themeable_ready") and widget._is_themeable_ready:
            return True

        # Add themeable mixin functionality dynamically
        # This is a bit hacky but provides flexibility
        widget.__class__ = type(
            widget.__class__.__name__ + "WithTheming", (widget.__class__, ThemeableMixin), {}
        )

        # Initialize themeable mixin
        ThemeableMixin.__init__(widget)
        widget.setup_theming(theme_config)

        logger.debug(f"Added theming to widget: {type(widget).__name__}")
        return True

    except Exception as e:
        logger.error(f"Error adding theming to widget: {e}")
        return False


def remove_theming_from_widget(widget: QWidget) -> bool:
    """Remove theming capabilities from a widget.

    Args:
        widget: Widget to remove theming from

    Returns:
        True if theming was removed successfully, False otherwise

    """
    try:
        # Clean up theming if present
        if hasattr(widget, "cleanup_theming"):
            widget.cleanup_theming()

        # Remove theming attributes
        theming_attrs = [
            "_themeable_widget_id",
            "_themeable_manager",
            "_themeable_properties",
            "_themeable_access",
            "_is_themeable_registered",
            "_is_themeable_ready",
        ]

        for attr in theming_attrs:
            if hasattr(widget, attr):
                delattr(widget, attr)

        logger.debug(f"Removed theming from widget: {type(widget).__name__}")
        return True

    except Exception as e:
        logger.error(f"Error removing theming from widget: {e}")
        return False


# Decorators for automatic theming setup
def themeable(theme_config: Optional[dict[str, str]] = None):
    """Decorator to automatically set up theming for widget classes.

    Usage:
        @themeable({'bg': 'window.background', 'fg': 'window.foreground'})
        class MyWidget(QWidget, ThemeableMixin):
            pass
    """

    def decorator(cls):
        original_init = cls.__init__

        def new_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            if hasattr(self, "setup_theming"):
                self.setup_theming(theme_config)

        cls.__init__ = new_init
        return cls

    return decorator


__all__ = [
    "ThemeableMixin",
    "PropertyMixin",
    "NotificationMixin",
    "CacheMixin",
    "LifecycleMixin",
    "CompositeMixin",
    "add_theming_to_widget",
    "remove_theming_from_widget",
    "themeable",
]
