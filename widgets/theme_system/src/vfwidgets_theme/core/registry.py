"""Widget registry with WeakRefs for automatic memory management.

This module provides the widget registry system that automatically manages
themed widgets using weak references. This ensures widgets are automatically
cleaned up when they go out of scope, preventing memory leaks.

Key Classes:
- WidgetRegistry: WeakRef-based registry for automatic cleanup
- RegistryEntry: Metadata container for registered widgets
- RegistryEventHandler: Event handling for registry operations

Design Principles:
- Automatic Memory Management: WeakRefs prevent memory leaks
- Thread Safety: All operations are thread-safe
- Event Driven: Registry operations emit events for coordination
- Metadata Tracking: Rich metadata for each registered widget

This uses the existing WidgetRegistry from lifecycle.py and extends it
with theme-specific functionality.

This will be implemented in Task 8.
"""

import threading
import time
import weakref
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional, Protocol, TypeVar

from ..lifecycle import WidgetRegistry as BaseWidgetRegistry
from ..logging import get_debug_logger

# Import foundation modules
from ..protocols import ThemeableWidget

logger = get_debug_logger(__name__)

T = TypeVar("T", bound=ThemeableWidget)


class RegistryEventType(Enum):
    """Types of registry events."""

    WIDGET_REGISTERED = "widget_registered"
    WIDGET_UNREGISTERED = "widget_unregistered"
    THEME_APPLIED = "theme_applied"
    REGISTRY_CLEARED = "registry_cleared"


@dataclass
class RegistryEntry:
    """Metadata container for registered widgets.

    Stores information about registered widgets including:
    - Widget reference (weak)
    - Registration timestamp
    - Theme metadata
    - Event callbacks
    """

    widget_ref: weakref.ReferenceType
    widget_id: str
    widget_type: str
    registration_time: float
    theme_metadata: dict[str, Any]
    callbacks: list[Callable[[], None]]

    @property
    def widget(self) -> Optional[ThemeableWidget]:
        """Get the widget instance (may be None if collected)."""
        return self.widget_ref()

    @property
    def is_alive(self) -> bool:
        """Check if the widget is still alive."""
        return self.widget is not None


class RegistryEventHandler(Protocol):
    """Protocol for handling registry events."""

    def on_widget_registered(self, entry: RegistryEntry) -> None:
        """Handle widget registration event."""
        ...

    def on_widget_unregistered(self, widget_id: str) -> None:
        """Handle widget unregistration event."""
        ...

    def on_theme_applied(self, widget_id: str, theme_name: str) -> None:
        """Handle theme application event."""
        ...


class ThemeWidgetRegistry:
    """Widget registry with theme-specific functionality.

    Extends the base WidgetRegistry with theme-specific features:
    - Theme application tracking
    - Event handling for theme operations
    - Widget metadata management
    - Performance monitoring

    This class will be fully implemented in Task 8.
    """

    def __init__(self, base_registry: Optional[BaseWidgetRegistry] = None):
        """Initialize theme widget registry.

        Args:
            base_registry: Optional base registry to extend

        """
        self._base_registry = base_registry
        self._entries: dict[str, RegistryEntry] = {}
        self._event_handlers: list[RegistryEventHandler] = []
        self._lock = threading.RLock()
        logger.debug("ThemeWidgetRegistry initialized")

    def register_widget(
        self,
        widget: ThemeableWidget,
        theme_metadata: Optional[dict[str, Any]] = None,
        callbacks: Optional[list[Callable[[], None]]] = None,
    ) -> str:
        """Register a themed widget with metadata.

        This method will:
        1. Create a weak reference to the widget
        2. Generate a unique widget ID
        3. Store theme metadata
        4. Set up cleanup callbacks
        5. Emit registration event

        Implementation will be added in Task 8.
        """
        with self._lock:
            widget_id = f"widget_{id(widget)}_{int(time.time() * 1000000)}"

            def cleanup_callback(ref):
                """Called when widget is garbage collected."""
                logger.debug(f"Widget {widget_id} garbage collected, cleaning up")
                self._remove_entry(widget_id)

            widget_ref = weakref.ref(widget, cleanup_callback)

            entry = RegistryEntry(
                widget_ref=widget_ref,
                widget_id=widget_id,
                widget_type=type(widget).__name__,
                registration_time=time.time(),
                theme_metadata=theme_metadata or {},
                callbacks=callbacks or [],
            )

            self._entries[widget_id] = entry

            # Emit registration event
            for handler in self._event_handlers:
                try:
                    handler.on_widget_registered(entry)
                except Exception as e:
                    logger.error(f"Error in registration event handler: {e}")

            logger.debug(f"Registered widget {widget_id} of type {entry.widget_type}")
            return widget_id

    def unregister_widget(self, widget_id: str) -> bool:
        """Unregister a widget by ID.

        Implementation will be added in Task 8.
        """
        with self._lock:
            if widget_id in self._entries:
                self._remove_entry(widget_id)
                logger.debug(f"Unregistered widget {widget_id}")
                return True
            return False

    def get_widget(self, widget_id: str) -> Optional[ThemeableWidget]:
        """Get widget by ID (may be None if collected)."""
        with self._lock:
            entry = self._entries.get(widget_id)
            return entry.widget if entry else None

    def get_entry(self, widget_id: str) -> Optional[RegistryEntry]:
        """Get registry entry by widget ID."""
        with self._lock:
            return self._entries.get(widget_id)

    def list_widgets(self, include_dead: bool = False) -> list[str]:
        """List all registered widget IDs."""
        with self._lock:
            if include_dead:
                return list(self._entries.keys())
            return [wid for wid, entry in self._entries.items() if entry.is_alive]

    def get_widget_count(self, include_dead: bool = False) -> int:
        """Get count of registered widgets."""
        return len(self.list_widgets(include_dead))

    def count(self) -> int:
        """Get count of active registered widgets (compatibility method)."""
        return self.get_widget_count(include_dead=False)

    def cleanup_dead_references(self) -> int:
        """Clean up dead widget references manually."""
        with self._lock:
            dead_ids = [wid for wid, entry in self._entries.items() if not entry.is_alive]
            for widget_id in dead_ids:
                self._remove_entry(widget_id)
            logger.debug(f"Cleaned up {len(dead_ids)} dead widget references")
            return len(dead_ids)

    def add_event_handler(self, handler: RegistryEventHandler) -> None:
        """Add an event handler."""
        self._event_handlers.append(handler)
        logger.debug(f"Added event handler: {type(handler).__name__}")

    def remove_event_handler(self, handler: RegistryEventHandler) -> bool:
        """Remove an event handler."""
        try:
            self._event_handlers.remove(handler)
            logger.debug(f"Removed event handler: {type(handler).__name__}")
            return True
        except ValueError:
            return False

    def apply_theme_to_widget(self, widget_id: str, theme_name: str) -> bool:
        """Apply theme to specific widget and track it.

        Implementation will be added in Task 8.
        """
        with self._lock:
            entry = self._entries.get(widget_id)
            if not entry or not entry.is_alive:
                return False

            # Update theme metadata
            entry.theme_metadata["current_theme"] = theme_name
            entry.theme_metadata["last_theme_applied"] = time.time()

            # Emit theme application event
            for handler in self._event_handlers:
                try:
                    handler.on_theme_applied(widget_id, theme_name)
                except Exception as e:
                    logger.error(f"Error in theme application event handler: {e}")

            logger.debug(f"Applied theme '{theme_name}' to widget {widget_id}")
            return True

    def _remove_entry(self, widget_id: str) -> None:
        """Internal method to remove an entry."""
        if widget_id in self._entries:
            del self._entries[widget_id]

            # Emit unregistration event
            for handler in self._event_handlers:
                try:
                    handler.on_widget_unregistered(widget_id)
                except Exception as e:
                    logger.error(f"Error in unregistration event handler: {e}")


class DefaultRegistryEventHandler:
    """Default implementation of registry event handler.

    Provides basic logging and statistics tracking for registry events.
    This class will be fully implemented in Task 8.
    """

    def __init__(self):
        """Initialize default event handler."""
        self._registration_count = 0
        self._unregistration_count = 0
        self._theme_application_count = 0
        logger.debug("DefaultRegistryEventHandler initialized")

    def on_widget_registered(self, entry: RegistryEntry) -> None:
        """Handle widget registration."""
        self._registration_count += 1
        logger.debug(f"Widget registered: {entry.widget_id} ({entry.widget_type})")

    def on_widget_unregistered(self, widget_id: str) -> None:
        """Handle widget unregistration."""
        self._unregistration_count += 1
        logger.debug(f"Widget unregistered: {widget_id}")

    def on_theme_applied(self, widget_id: str, theme_name: str) -> None:
        """Handle theme application."""
        self._theme_application_count += 1
        logger.debug(f"Theme '{theme_name}' applied to widget {widget_id}")

    @property
    def statistics(self) -> dict[str, int]:
        """Get event handler statistics."""
        return {
            "registrations": self._registration_count,
            "unregistrations": self._unregistration_count,
            "theme_applications": self._theme_application_count,
        }


# Factory function for creating widget registry
def create_widget_registry(
    base_registry: Optional[BaseWidgetRegistry] = None,
) -> ThemeWidgetRegistry:
    """Create theme widget registry with default configuration.

    Implementation will be completed in Task 8.
    """
    registry = ThemeWidgetRegistry(base_registry)

    # Add default event handler
    default_handler = DefaultRegistryEventHandler()
    registry.add_event_handler(default_handler)

    logger.debug("Created theme widget registry with default configuration")
    return registry


__all__ = [
    "ThemeWidgetRegistry",
    "RegistryEntry",
    "RegistryEventHandler",
    "RegistryEventType",
    "DefaultRegistryEventHandler",
    "create_widget_registry",
]
