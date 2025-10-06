"""Theme Event System with Qt Integration

Provides Qt signals/slots based event system for efficient theme change notifications
with debouncing, performance optimization, and testing support.
"""

import logging
import time
import weakref
from dataclasses import dataclass, field
from threading import RLock
from typing import Any, Dict, List, Optional, Set

try:
    from PySide6.QtCore import QObject, QTimer, Signal, Slot
    from PySide6.QtWidgets import QWidget

    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False

    # Mock Qt classes for environments without PySide6
    class QObject:
        def __init__(self, parent=None):
            self.parent = parent

    class Signal:
        def __init__(self, *args):
            self._connections = []

        def connect(self, func):
            self._connections.append(func)

        def disconnect(self, func=None):
            if func is None:
                self._connections.clear()
            elif func in self._connections:
                self._connections.remove(func)

        def emit(self, *args):
            for func in self._connections:
                try:
                    func(*args)
                except Exception as e:
                    print(f"Signal emission error: {e}")

    class QTimer:
        def __init__(self):
            self._timeout_callbacks = []
            self._interval = 100
            self._single_shot = False

        def timeout(self):
            class TimeoutSignal:
                def connect(self, func):
                    pass

            return TimeoutSignal()

        def start(self, msec=None):
            pass

        def stop(self):
            pass

        def setSingleShot(self, single_shot):
            self._single_shot = single_shot

        def setInterval(self, msec):
            self._interval = msec

    def Slot(*args):
        def decorator(func):
            return func

        return decorator


@dataclass
class EventRecord:
    """Records an event for replay and debugging."""

    timestamp: float
    event_type: str
    data: Dict[str, Any] = field(default_factory=dict)
    widget_id: Optional[str] = None
    property_name: Optional[str] = None
    old_value: Any = None
    new_value: Any = None


class ThemeEventSystem(QObject):
    """Qt-integrated event system with debouncing and performance optimization.

    This system provides:
    - Qt signals/slots for theme change notifications
    - Debouncing to prevent rapid updates
    - Property-specific signals for granular updates
    - Event filtering for performance
    - Event replay capability for testing
    """

    # Global theme signals
    theme_changing = Signal(str)  # theme_name - Before change
    theme_changed = Signal(str)  # theme_name - After change
    theme_load_failed = Signal(str, str)  # theme_name, error_message

    # Property-specific signals
    property_changing = Signal(
        str, str, object, object
    )  # widget_id, property, old, new - Before change
    property_changed = Signal(
        str, str, object, object
    )  # widget_id, property, old, new - After change
    property_validation_failed = Signal(str, str, object, str)  # widget_id, property, value, error

    # Widget lifecycle signals
    widget_registered = Signal(str)  # widget_id
    widget_unregistered = Signal(str)  # widget_id
    widget_theme_applied = Signal(str, str)  # widget_id, theme_name

    # Performance monitoring signals
    performance_warning = Signal(str, float)  # operation, duration_ms

    def __init__(self, parent=None):
        super().__init__(parent)

        # Debouncing configuration
        self._debounce_interval_ms = 50  # 50ms debounce by default
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._flush_pending_events)

        # Pending events for debouncing
        self._pending_events: List[EventRecord] = []
        self._pending_lock = RLock()

        # Event filtering
        self._filtered_properties: Set[str] = set()  # Properties to ignore
        self._filtered_widgets: Set[str] = set()  # Widgets to ignore
        self._max_events_per_cycle = 100  # Max events to process per debounce cycle

        # Event replay for testing
        self._recording_enabled = False
        self._event_history: List[EventRecord] = []
        self._max_history_size = 1000

        # Performance monitoring
        self._performance_threshold_ms = 10.0  # Warn if operations take longer
        self._logger = logging.getLogger(__name__)

        # Widget weak references for cleanup
        self._widget_refs: Dict[str, weakref.ReferenceType] = {}

    def enable_recording(self, max_history: int = 1000) -> None:
        """Enable event recording for replay and debugging."""
        self._recording_enabled = True
        self._max_history_size = max_history
        self._event_history.clear()
        self._logger.info(f"Event recording enabled (max history: {max_history})")

    def disable_recording(self) -> None:
        """Disable event recording."""
        self._recording_enabled = False
        self._event_history.clear()
        self._logger.info("Event recording disabled")

    def get_event_history(self) -> List[EventRecord]:
        """Get recorded event history."""
        return self._event_history.copy()

    def replay_events(self, target_widget_id: Optional[str] = None) -> int:
        """Replay recorded events.

        Args:
            target_widget_id: If specified, only replay events for this widget

        Returns:
            Number of events replayed

        """
        replayed = 0
        for event in self._event_history:
            if target_widget_id and event.widget_id != target_widget_id:
                continue

            try:
                self._replay_single_event(event)
                replayed += 1
            except Exception as e:
                self._logger.warning(f"Failed to replay event {event.event_type}: {e}")

        self._logger.info(f"Replayed {replayed} events")
        return replayed

    def set_debounce_interval(self, ms: int) -> None:
        """Set debouncing interval in milliseconds."""
        self._debounce_interval_ms = max(1, min(1000, ms))  # Clamp between 1ms and 1s
        self._logger.info(f"Debounce interval set to {self._debounce_interval_ms}ms")

    def add_property_filter(self, property_name: str) -> None:
        """Add property to filter list (events will be ignored)."""
        self._filtered_properties.add(property_name)
        self._logger.debug(f"Added property filter: {property_name}")

    def remove_property_filter(self, property_name: str) -> None:
        """Remove property from filter list."""
        self._filtered_properties.discard(property_name)
        self._logger.debug(f"Removed property filter: {property_name}")

    def add_widget_filter(self, widget_id: str) -> None:
        """Add widget to filter list (events will be ignored)."""
        self._filtered_widgets.add(widget_id)
        self._logger.debug(f"Added widget filter: {widget_id}")

    def remove_widget_filter(self, widget_id: str) -> None:
        """Remove widget from filter list."""
        self._filtered_widgets.discard(widget_id)
        self._logger.debug(f"Removed widget filter: {widget_id}")

    def clear_filters(self) -> None:
        """Clear all event filters."""
        self._filtered_properties.clear()
        self._filtered_widgets.clear()
        self._logger.info("Cleared all event filters")

    def register_widget(self, widget_id: str, widget: "QWidget") -> None:
        """Register a widget for event tracking."""
        # Store weak reference to widget
        self._widget_refs[widget_id] = weakref.ref(
            widget, lambda ref: self._cleanup_widget(widget_id)
        )

        # Record and emit registration
        self._record_event("widget_registered", widget_id=widget_id)
        self.widget_registered.emit(widget_id)
        self._logger.debug(f"Registered widget: {widget_id}")

    def unregister_widget(self, widget_id: str) -> None:
        """Unregister a widget from event tracking."""
        if widget_id in self._widget_refs:
            del self._widget_refs[widget_id]

        # Remove from filters
        self._filtered_widgets.discard(widget_id)

        # Record and emit unregistration
        self._record_event("widget_unregistered", widget_id=widget_id)
        self.widget_unregistered.emit(widget_id)
        self._logger.debug(f"Unregistered widget: {widget_id}")

    def notify_theme_changing(self, theme_name: str) -> None:
        """Notify that a theme change is about to occur."""
        start_time = time.perf_counter()

        self._record_event("theme_changing", data={"theme_name": theme_name})
        self.theme_changing.emit(theme_name)

        self._check_performance("theme_changing", start_time)

    def notify_theme_changed(self, theme_name: str) -> None:
        """Notify that a theme change has completed."""
        start_time = time.perf_counter()

        self._record_event("theme_changed", data={"theme_name": theme_name})
        self.theme_changed.emit(theme_name)

        self._check_performance("theme_changed", start_time)

    def notify_theme_load_failed(self, theme_name: str, error_message: str) -> None:
        """Notify that theme loading failed."""
        self._record_event(
            "theme_load_failed", data={"theme_name": theme_name, "error": error_message}
        )
        self.theme_load_failed.emit(theme_name, error_message)

    def notify_property_changing(
        self,
        widget_id: str,
        property_name: str,
        old_value: Any,
        new_value: Any,
        debounce: bool = True,
    ) -> None:
        """Notify that a property is about to change."""
        # Apply filters
        if self._is_filtered(widget_id, property_name):
            return

        event = EventRecord(
            timestamp=time.time(),
            event_type="property_changing",
            widget_id=widget_id,
            property_name=property_name,
            old_value=old_value,
            new_value=new_value,
        )

        if debounce:
            self._queue_event(event)
        else:
            self._emit_property_changing(event)

    def notify_property_changed(
        self,
        widget_id: str,
        property_name: str,
        old_value: Any,
        new_value: Any,
        debounce: bool = True,
    ) -> None:
        """Notify that a property has changed."""
        # Apply filters
        if self._is_filtered(widget_id, property_name):
            return

        event = EventRecord(
            timestamp=time.time(),
            event_type="property_changed",
            widget_id=widget_id,
            property_name=property_name,
            old_value=old_value,
            new_value=new_value,
        )

        if debounce:
            self._queue_event(event)
        else:
            self._emit_property_changed(event)

    def notify_property_validation_failed(
        self, widget_id: str, property_name: str, invalid_value: Any, error_message: str
    ) -> None:
        """Notify that property validation failed."""
        self._record_event(
            "property_validation_failed",
            widget_id=widget_id,
            property_name=property_name,
            data={"invalid_value": invalid_value, "error": error_message},
        )
        self.property_validation_failed.emit(widget_id, property_name, invalid_value, error_message)

    def notify_widget_theme_applied(self, widget_id: str, theme_name: str) -> None:
        """Notify that theme was applied to a widget."""
        if widget_id in self._filtered_widgets:
            return

        self._record_event(
            "widget_theme_applied", widget_id=widget_id, data={"theme_name": theme_name}
        )
        self.widget_theme_applied.emit(widget_id, theme_name)

    def get_statistics(self) -> Dict[str, Any]:
        """Get event system statistics."""
        return {
            "debounce_interval_ms": self._debounce_interval_ms,
            "pending_events": len(self._pending_events),
            "filtered_properties": len(self._filtered_properties),
            "filtered_widgets": len(self._filtered_widgets),
            "recorded_events": len(self._event_history),
            "recording_enabled": self._recording_enabled,
            "registered_widgets": len(self._widget_refs),
            "performance_threshold_ms": self._performance_threshold_ms,
        }

    # Private methods

    def _is_filtered(self, widget_id: str, property_name: str) -> bool:
        """Check if event should be filtered out."""
        return widget_id in self._filtered_widgets or property_name in self._filtered_properties

    def _queue_event(self, event: EventRecord) -> None:
        """Queue event for debounced processing."""
        with self._pending_lock:
            self._pending_events.append(event)

            # Start/restart debounce timer
            if not self._debounce_timer.isActive():
                self._debounce_timer.start(self._debounce_interval_ms)

    @Slot()
    def _flush_pending_events(self) -> None:
        """Process all pending events."""
        start_time = time.perf_counter()

        with self._pending_lock:
            events_to_process = self._pending_events[: self._max_events_per_cycle]
            self._pending_events = self._pending_events[self._max_events_per_cycle :]

            # If more events remain, restart timer
            if self._pending_events:
                self._debounce_timer.start(self._debounce_interval_ms)

        # Process events outside of lock
        for event in events_to_process:
            try:
                if event.event_type == "property_changing":
                    self._emit_property_changing(event)
                elif event.event_type == "property_changed":
                    self._emit_property_changed(event)
            except Exception as e:
                self._logger.error(f"Error processing event {event.event_type}: {e}")

        self._check_performance("flush_pending_events", start_time, len(events_to_process))

    def _emit_property_changing(self, event: EventRecord) -> None:
        """Emit property_changing signal."""
        self._record_event_if_enabled(event)
        self.property_changing.emit(
            event.widget_id, event.property_name, event.old_value, event.new_value
        )

    def _emit_property_changed(self, event: EventRecord) -> None:
        """Emit property_changed signal."""
        self._record_event_if_enabled(event)
        self.property_changed.emit(
            event.widget_id, event.property_name, event.old_value, event.new_value
        )

    def _record_event(
        self,
        event_type: str,
        widget_id: Optional[str] = None,
        property_name: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record an event for replay/debugging."""
        if not self._recording_enabled:
            return

        event = EventRecord(
            timestamp=time.time(),
            event_type=event_type,
            widget_id=widget_id,
            property_name=property_name,
            data=data or {},
        )

        self._record_event_if_enabled(event)

    def _record_event_if_enabled(self, event: EventRecord) -> None:
        """Record event if recording is enabled."""
        if not self._recording_enabled:
            return

        self._event_history.append(event)

        # Trim history if too large
        if len(self._event_history) > self._max_history_size:
            self._event_history = self._event_history[-self._max_history_size :]

    def _replay_single_event(self, event: EventRecord) -> None:
        """Replay a single recorded event."""
        if event.event_type == "property_changing":
            self.property_changing.emit(
                event.widget_id, event.property_name, event.old_value, event.new_value
            )
        elif event.event_type == "property_changed":
            self.property_changed.emit(
                event.widget_id, event.property_name, event.old_value, event.new_value
            )
        elif event.event_type == "theme_changing":
            self.theme_changing.emit(event.data.get("theme_name", ""))
        elif event.event_type == "theme_changed":
            self.theme_changed.emit(event.data.get("theme_name", ""))
        # Add other event types as needed

    def _cleanup_widget(self, widget_id: str) -> None:
        """Clean up when widget is garbage collected."""
        self.unregister_widget(widget_id)

    def _check_performance(
        self, operation: str, start_time: float, count: Optional[int] = None
    ) -> None:
        """Check if operation exceeded performance threshold."""
        duration_ms = (time.perf_counter() - start_time) * 1000

        if duration_ms > self._performance_threshold_ms:
            context = f" (processed {count} events)" if count else ""
            self._logger.warning(
                f"Performance warning: {operation} took {duration_ms:.2f}ms{context}"
            )
            self.performance_warning.emit(operation, duration_ms)


# Global instance - can be used directly or injected
_global_event_system: Optional[ThemeEventSystem] = None


def get_global_event_system() -> ThemeEventSystem:
    """Get the global theme event system instance."""
    global _global_event_system
    if _global_event_system is None:
        _global_event_system = ThemeEventSystem()
    return _global_event_system


def set_global_event_system(event_system: ThemeEventSystem) -> None:
    """Set a custom global theme event system (useful for testing)."""
    global _global_event_system
    _global_event_system = event_system
