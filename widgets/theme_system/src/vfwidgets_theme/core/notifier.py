"""ThemeNotifier for handling change notifications.

This module provides the ThemeNotifier class that handles theme change
notifications across widgets and the application. It follows the Single
Responsibility Principle by focusing solely on notification coordination
and delivery.

Key Classes:
- ThemeNotifier: Main coordinator for theme change notifications
- WidgetNotificationManager: Manages widget-specific notifications
- CallbackRegistry: Manages notification callbacks
- NotificationQueue: Queues and batches notifications
- EventFilter: Filters notifications for performance
- CrossThreadNotifier: Handles cross-thread notifications
- NotificationBatcher: Batches notifications for efficiency

Design Principles:
- Single Responsibility: Notifier focuses only on notification delivery
- Performance: Event filtering and batching for efficiency
- Thread Safety: Safe cross-thread notification delivery
- Error Recovery: Graceful handling of notification errors
- Memory Efficiency: Weak references to prevent memory leaks

Performance Requirements:
- Notification overhead: < 10μs per widget
- Cross-thread latency: < 1ms
- Memory overhead: < 100 bytes per registered widget
- Batch processing: Configurable batch sizes and intervals
"""

import threading
import time
import uuid
import weakref
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Callable, Deque, Dict, List, Optional, Tuple

# Import Qt components with fallback for headless testing
try:
    from PySide6.QtCore import QMetaObject, QObject, Qt, QThread, QTimer, Signal
    from PySide6.QtWidgets import QApplication, QWidget
    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False
    # Create mock classes for headless testing
    class QObject:
        def __init__(self):
            self.signals = {}
        def connect(self, slot): pass
        def disconnect(self, slot): pass
        def emit(self, *args): pass
    class Signal:
        def __init__(self, *types):
            self._slots = []
        def connect(self, slot):
            self._slots.append(slot)
        def disconnect(self, slot):
            if slot in self._slots:
                self._slots.remove(slot)
        def emit(self, *args):
            for slot in self._slots:
                try:
                    slot(*args)
                except Exception:
                    pass

# Import foundation modules
from ..logging import get_debug_logger
from ..protocols import ThemeChangeCallback

logger = get_debug_logger(__name__)


@dataclass
class NotificationStats:
    """Statistics for notification operations."""

    notifications_sent: int = 0
    widgets_registered: int = 0
    callbacks_registered: int = 0
    errors: int = 0
    total_time: float = 0.0
    filtered_notifications: int = 0
    batched_notifications: int = 0


@dataclass
class NotificationItem:
    """Individual notification item."""

    theme_name: str
    widget_id: str
    timestamp: float = field(default_factory=time.time)
    priority: int = 0  # Higher = more important


class WidgetNotificationManager:
    """Manages widget-specific notifications.

    Handles registration and notification of individual widgets with:
    - Weak reference storage to prevent memory leaks
    - Thread-safe widget registration
    - Efficient notification delivery
    - Automatic cleanup of dead references
    """

    def __init__(self):
        """Initialize widget notification manager."""
        self._widgets: Dict[str, weakref.ref] = {}
        self._widget_signals: Dict[str, Signal] = {}
        self._lock = threading.RLock()
        logger.debug("WidgetNotificationManager initialized")

    def register_widget(self, widget: QObject) -> bool:
        """Register widget for notifications.

        Args:
            widget: Widget to register

        Returns:
            True if successfully registered

        """
        try:
            with self._lock:
                widget_id = f"widget_{id(widget)}_{int(time.time() * 1000000)}"

                def cleanup_callback(ref):
                    """Called when widget is garbage collected."""
                    logger.debug(f"Widget {widget_id} garbage collected, cleaning up")
                    self._remove_widget(widget_id)

                widget_ref = weakref.ref(widget, cleanup_callback)
                self._widgets[widget_id] = widget_ref

                # Create theme change signal for widget
                if hasattr(widget, 'theme_changed'):
                    self._widget_signals[widget_id] = widget.theme_changed
                else:
                    # Create signal if widget doesn't have one
                    self._widget_signals[widget_id] = Signal(str)

                logger.debug(f"Registered widget {widget_id} for notifications")
                return True

        except Exception as e:
            logger.error(f"Error registering widget: {e}")
            return False

    def unregister_widget(self, widget: QObject) -> bool:
        """Unregister widget from notifications.

        Args:
            widget: Widget to unregister

        Returns:
            True if successfully unregistered

        """
        try:
            with self._lock:
                widget_id_to_remove = None

                # Find widget ID by reference
                for widget_id, widget_ref in self._widgets.items():
                    if widget_ref() is widget:
                        widget_id_to_remove = widget_id
                        break

                if widget_id_to_remove:
                    self._remove_widget(widget_id_to_remove)
                    logger.debug(f"Unregistered widget {widget_id_to_remove}")
                    return True

                return False

        except Exception as e:
            logger.error(f"Error unregistering widget: {e}")
            return False

    def is_registered(self, widget: QObject) -> bool:
        """Check if widget is registered.

        Args:
            widget: Widget to check

        Returns:
            True if widget is registered

        """
        with self._lock:
            for widget_ref in self._widgets.values():
                if widget_ref() is widget:
                    return True
            return False

    def notify_widget(self, widget: QObject, theme_name: str) -> bool:
        """Notify specific widget of theme change.

        Args:
            widget: Widget to notify
            theme_name: Name of new theme

        Returns:
            True if notification was sent

        """
        try:
            with self._lock:
                # Find widget signal
                for widget_id, widget_ref in self._widgets.items():
                    if widget_ref() is widget:
                        signal = self._widget_signals.get(widget_id)
                        if signal:
                            signal.emit(theme_name)
                            logger.debug(f"Notified widget {widget_id} of theme '{theme_name}'")
                            return True
                        break

                return False

        except Exception as e:
            logger.error(f"Error notifying widget: {e}")
            return False

    def notify_all_widgets(self, theme_name: str) -> Dict[str, bool]:
        """Notify all registered widgets of theme change.

        Args:
            theme_name: Name of new theme

        Returns:
            Dictionary mapping widget ID to notification success

        """
        results = {}

        with self._lock:
            for widget_id, widget_ref in list(self._widgets.items()):
                widget = widget_ref()
                if widget is None:
                    # Widget was garbage collected, clean up
                    self._remove_widget(widget_id)
                    results[widget_id] = False
                    continue

                try:
                    signal = self._widget_signals.get(widget_id)
                    if signal:
                        signal.emit(theme_name)
                        results[widget_id] = True
                        logger.debug(f"Notified widget {widget_id} of theme '{theme_name}'")
                    else:
                        results[widget_id] = False

                except Exception as e:
                    logger.error(f"Error notifying widget {widget_id}: {e}")
                    results[widget_id] = False

        return results

    def get_registered_count(self) -> int:
        """Get count of registered widgets."""
        with self._lock:
            return len(self._widgets)

    def cleanup_dead_references(self) -> int:
        """Clean up dead widget references manually."""
        cleaned_count = 0

        with self._lock:
            dead_ids = []
            for widget_id, widget_ref in self._widgets.items():
                if widget_ref() is None:
                    dead_ids.append(widget_id)

            for widget_id in dead_ids:
                self._remove_widget(widget_id)
                cleaned_count += 1

        logger.debug(f"Cleaned up {cleaned_count} dead widget references")
        return cleaned_count

    def _remove_widget(self, widget_id: str) -> None:
        """Internal method to remove widget."""
        if widget_id in self._widgets:
            del self._widgets[widget_id]
        if widget_id in self._widget_signals:
            del self._widget_signals[widget_id]


class CallbackRegistry:
    """Manages notification callbacks.

    Provides registration and execution of theme change callbacks with:
    - Thread-safe callback registration
    - Error handling during callback execution
    - Callback filtering capabilities
    - Statistics tracking
    """

    def __init__(self):
        """Initialize callback registry."""
        self._callbacks: Dict[str, ThemeChangeCallback] = {}
        self._callback_filters: Dict[str, Callable[[str, str], bool]] = {}
        self._lock = threading.RLock()
        self._stats = {
            "registered_callbacks": 0,
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0
        }
        logger.debug("CallbackRegistry initialized")

    def register_callback(self, callback: ThemeChangeCallback) -> str:
        """Register theme change callback.

        Args:
            callback: Callback function

        Returns:
            Unique callback ID

        """
        callback_id = str(uuid.uuid4())

        with self._lock:
            self._callbacks[callback_id] = callback
            self._stats["registered_callbacks"] += 1

        logger.debug(f"Registered callback {callback_id}")
        return callback_id

    def unregister_callback(self, callback_id: str) -> bool:
        """Unregister callback.

        Args:
            callback_id: ID of callback to remove

        Returns:
            True if callback was removed

        """
        with self._lock:
            if callback_id in self._callbacks:
                del self._callbacks[callback_id]
                if callback_id in self._callback_filters:
                    del self._callback_filters[callback_id]
                self._stats["registered_callbacks"] -= 1
                logger.debug(f"Unregistered callback {callback_id}")
                return True

        return False

    def has_callback(self, callback_id: str) -> bool:
        """Check if callback is registered.

        Args:
            callback_id: Callback ID to check

        Returns:
            True if callback exists

        """
        with self._lock:
            return callback_id in self._callbacks

    def call_all_callbacks(self, theme_name: str, widget_id: str) -> None:
        """Call all registered callbacks.

        Args:
            theme_name: Theme name
            widget_id: Widget ID

        """
        with self._lock:
            callbacks_to_call = list(self._callbacks.items())

        for callback_id, callback in callbacks_to_call:
            try:
                # Check callback filter
                callback_filter = self._callback_filters.get(callback_id)
                if callback_filter and not callback_filter(theme_name, widget_id):
                    continue

                callback(theme_name, widget_id)

                with self._lock:
                    self._stats["successful_calls"] += 1

            except Exception as e:
                logger.error(f"Error in callback {callback_id}: {e}")
                with self._lock:
                    self._stats["failed_calls"] += 1

        with self._lock:
            self._stats["total_calls"] += len(callbacks_to_call)

    def set_callback_filter(self, callback_id: str, filter_func: Callable[[str, str], bool]) -> bool:
        """Set filter for specific callback.

        Args:
            callback_id: Callback ID
            filter_func: Filter function

        Returns:
            True if filter was set

        """
        with self._lock:
            if callback_id in self._callbacks:
                self._callback_filters[callback_id] = filter_func
                logger.debug(f"Set filter for callback {callback_id}")
                return True

        return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get callback registry statistics."""
        with self._lock:
            return self._stats.copy()


class NotificationQueue:
    """Queues and batches notifications for efficient processing.

    Provides notification queuing with:
    - Priority notification support
    - Batch processing capabilities
    - Size limits and overflow handling
    - Asynchronous processing support
    """

    def __init__(self, max_size: int = 1000):
        """Initialize notification queue.

        Args:
            max_size: Maximum queue size

        """
        self._queue: Deque[NotificationItem] = deque()
        self._priority_queue: Deque[NotificationItem] = deque()
        self._max_size = max_size
        self._processor: Optional[Callable[[str, str], None]] = None
        self._batch_processor: Optional[Callable[[List[tuple]], None]] = None
        self._batch_size = 10
        self._lock = threading.RLock()
        self._processing_thread: Optional[threading.Thread] = None
        self._stop_processing = threading.Event()
        logger.debug(f"NotificationQueue initialized with max_size: {max_size}")

    def enqueue_notification(self, theme_name: str, widget_id: str) -> bool:
        """Enqueue normal priority notification.

        Args:
            theme_name: Theme name
            widget_id: Widget ID

        Returns:
            True if enqueued successfully

        """
        return self._enqueue(NotificationItem(theme_name, widget_id))

    def enqueue_priority_notification(self, theme_name: str, widget_id: str) -> bool:
        """Enqueue high priority notification.

        Args:
            theme_name: Theme name
            widget_id: Widget ID

        Returns:
            True if enqueued successfully

        """
        return self._enqueue(NotificationItem(theme_name, widget_id, priority=1), priority=True)

    def _enqueue(self, item: NotificationItem, priority: bool = False) -> bool:
        """Internal method to enqueue notification."""
        with self._lock:
            target_queue = self._priority_queue if priority else self._queue

            if self.size() >= self._max_size:
                # Queue is full, drop oldest non-priority notification
                if self._queue:
                    self._queue.popleft()
                    logger.warning("Notification queue full, dropped oldest notification")
                else:
                    logger.error("Priority queue full, cannot enqueue notification")
                    return False

            target_queue.append(item)
            return True

    def size(self) -> int:
        """Get total queue size."""
        with self._lock:
            return len(self._queue) + len(self._priority_queue)

    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return self.size() == 0

    def is_full(self) -> bool:
        """Check if queue is full."""
        return self.size() >= self._max_size

    def set_processor(self, processor: Callable[[str, str], None]) -> None:
        """Set single notification processor."""
        self._processor = processor

    def set_batch_processor(self, processor: Callable[[List[tuple]], None], batch_size: int = 10) -> None:
        """Set batch notification processor."""
        self._batch_processor = processor
        self._batch_size = batch_size

    def process_all(self) -> int:
        """Process all queued notifications."""
        processed_count = 0

        with self._lock:
            # Process priority notifications first
            while self._priority_queue:
                item = self._priority_queue.popleft()
                self._process_single_item(item)
                processed_count += 1

            # Process normal notifications
            if self._batch_processor:
                # Batch processing
                while self._queue:
                    batch = []
                    for _ in range(min(self._batch_size, len(self._queue))):
                        if self._queue:
                            item = self._queue.popleft()
                            batch.append((item.theme_name, item.widget_id))

                    if batch:
                        try:
                            self._batch_processor(batch)
                            processed_count += len(batch)
                        except Exception as e:
                            logger.error(f"Error in batch processor: {e}")

            else:
                # Single processing
                while self._queue:
                    item = self._queue.popleft()
                    self._process_single_item(item)
                    processed_count += 1

        return processed_count

    def _process_single_item(self, item: NotificationItem) -> None:
        """Process single notification item."""
        if self._processor:
            try:
                self._processor(item.theme_name, item.widget_id)
            except Exception as e:
                logger.error(f"Error processing notification: {e}")

    def start_async_processing(self) -> None:
        """Start asynchronous processing thread."""
        if self._processing_thread and self._processing_thread.is_alive():
            return

        self._stop_processing.clear()
        self._processing_thread = threading.Thread(target=self._async_processing_loop)
        self._processing_thread.daemon = True
        self._processing_thread.start()
        logger.debug("Started async notification processing")

    def stop_async_processing(self) -> None:
        """Stop asynchronous processing thread."""
        self._stop_processing.set()
        if self._processing_thread:
            self._processing_thread.join(timeout=1.0)
        logger.debug("Stopped async notification processing")

    def _async_processing_loop(self) -> None:
        """Async processing loop."""
        while not self._stop_processing.is_set():
            try:
                if not self.is_empty():
                    self.process_all()
                time.sleep(0.01)  # Small delay to prevent busy waiting
            except Exception as e:
                logger.error(f"Error in async processing loop: {e}")


class EventFilter:
    """Filters notifications for performance optimization.

    Provides event filtering with:
    - Theme name pattern filtering
    - Widget ID pattern filtering
    - Combined filter conditions
    - Performance statistics
    """

    def __init__(self):
        """Initialize event filter."""
        self._theme_filters: List[Callable[[str], bool]] = []
        self._widget_filters: List[Callable[[str], bool]] = []
        self._stats = {
            "total_checks": 0,
            "notifications_allowed": 0,
            "notifications_blocked": 0
        }
        self._lock = threading.RLock()
        logger.debug("EventFilter initialized")

    def add_theme_filter(self, filter_func: Callable[[str], bool]) -> None:
        """Add theme name filter.

        Args:
            filter_func: Function that returns True if theme should be notified

        """
        with self._lock:
            self._theme_filters.append(filter_func)
            logger.debug("Added theme filter")

    def add_widget_filter(self, filter_func: Callable[[str], bool]) -> None:
        """Add widget ID filter.

        Args:
            filter_func: Function that returns True if widget should be notified

        """
        with self._lock:
            self._widget_filters.append(filter_func)
            logger.debug("Added widget filter")

    def should_notify(self, theme_name: str, widget_id: str) -> bool:
        """Check if notification should be sent.

        Args:
            theme_name: Theme name
            widget_id: Widget ID

        Returns:
            True if notification should be sent

        """
        with self._lock:
            self._stats["total_checks"] += 1

            # Check theme filters
            for theme_filter in self._theme_filters:
                if not theme_filter(theme_name):
                    self._stats["notifications_blocked"] += 1
                    return False

            # Check widget filters
            for widget_filter in self._widget_filters:
                if not widget_filter(widget_id):
                    self._stats["notifications_blocked"] += 1
                    return False

            self._stats["notifications_allowed"] += 1
            return True

    def get_statistics(self) -> Dict[str, Any]:
        """Get filter statistics."""
        with self._lock:
            return self._stats.copy()

    def clear_filters(self) -> None:
        """Clear all filters."""
        with self._lock:
            self._theme_filters.clear()
            self._widget_filters.clear()
            logger.debug("Cleared all filters")


class CrossThreadNotifier:
    """Handles cross-thread notifications safely.

    Provides thread-safe notification delivery with:
    - Qt signal/slot integration for thread safety
    - Handler registration from any thread
    - Asynchronous notification delivery
    - Thread-safe error handling
    """

    def __init__(self):
        """Initialize cross-thread notifier."""
        self._handlers: List[Callable[[str, str], None]] = []
        self._lock = threading.RLock()
        self._executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="notifier")
        logger.debug("CrossThreadNotifier initialized")

    def register_handler(self, handler: Callable[[str, str], None]) -> None:
        """Register notification handler.

        Args:
            handler: Handler function for notifications

        """
        with self._lock:
            self._handlers.append(handler)
            logger.debug("Registered cross-thread notification handler")

    def unregister_handler(self, handler: Callable[[str, str], None]) -> bool:
        """Unregister notification handler.

        Args:
            handler: Handler to remove

        Returns:
            True if handler was removed

        """
        with self._lock:
            try:
                self._handlers.remove(handler)
                logger.debug("Unregistered cross-thread notification handler")
                return True
            except ValueError:
                return False

    def notify_async(self, theme_name: str, widget_id: str) -> None:
        """Send notification asynchronously.

        Args:
            theme_name: Theme name
            widget_id: Widget ID

        """
        def notify_worker():
            """Worker function for async notification."""
            with self._lock:
                handlers = list(self._handlers)

            for handler in handlers:
                try:
                    handler(theme_name, widget_id)
                except Exception as e:
                    logger.error(f"Error in cross-thread notification handler: {e}")

        self._executor.submit(notify_worker)

    def shutdown(self) -> None:
        """Shutdown cross-thread notifier."""
        self._executor.shutdown(wait=True)
        logger.debug("CrossThreadNotifier shutdown")


class NotificationBatcher:
    """Batches notifications for efficient processing.

    Provides notification batching with:
    - Configurable batch sizes
    - Time-based flushing
    - Batch processing callbacks
    - Statistics tracking
    """

    def __init__(self, batch_size: int = 10, flush_interval: float = 0.1):
        """Initialize notification batcher.

        Args:
            batch_size: Maximum batch size
            flush_interval: Time interval for automatic flushing (seconds)

        """
        self._batch_size = batch_size
        self._flush_interval = flush_interval
        self._current_batch: List[Tuple[str, str]] = []
        self._batch_processor: Optional[Callable[[List[tuple]], None]] = None
        self._lock = threading.RLock()
        self._last_flush = time.time()
        self._flush_timer: Optional[threading.Timer] = None
        logger.debug(f"NotificationBatcher initialized: batch_size={batch_size}, flush_interval={flush_interval}")

    def set_batch_processor(self, processor: Callable[[List[tuple]], None]) -> None:
        """Set batch processor function."""
        self._batch_processor = processor

    def add_notification(self, theme_name: str, widget_id: str) -> None:
        """Add notification to current batch.

        Args:
            theme_name: Theme name
            widget_id: Widget ID

        """
        with self._lock:
            self._current_batch.append((theme_name, widget_id))

            # Check if batch is full
            if len(self._current_batch) >= self._batch_size:
                self._flush_batch()
            else:
                # Schedule time-based flush if not already scheduled
                self._schedule_flush()

    def flush(self) -> None:
        """Flush current batch immediately."""
        with self._lock:
            self._flush_batch()

    def _flush_batch(self) -> None:
        """Internal method to flush current batch."""
        if not self._current_batch or not self._batch_processor:
            return

        try:
            batch_to_process = list(self._current_batch)
            self._current_batch.clear()
            self._last_flush = time.time()

            # Cancel pending timer
            if self._flush_timer:
                self._flush_timer.cancel()
                self._flush_timer = None

            self._batch_processor(batch_to_process)
            logger.debug(f"Processed batch of {len(batch_to_process)} notifications")

        except Exception as e:
            logger.error(f"Error processing notification batch: {e}")

    def _schedule_flush(self) -> None:
        """Schedule time-based flush."""
        if self._flush_timer is not None:
            return  # Timer already scheduled

        def flush_callback():
            with self._lock:
                self._flush_timer = None
                if self._current_batch:
                    self._flush_batch()

        self._flush_timer = threading.Timer(self._flush_interval, flush_callback)
        self._flush_timer.start()


class ThemeNotifier:
    """Main coordinator for theme change notifications.

    Coordinates notification operations across:
    - Widget notifications via WidgetNotificationManager
    - Callback execution via CallbackRegistry
    - Notification queuing via NotificationQueue
    - Event filtering via EventFilter
    - Cross-thread delivery via CrossThreadNotifier
    - Batch processing via NotificationBatcher

    Follows Single Responsibility Principle by acting as a facade
    that delegates to specialized notification components.
    """

    def __init__(
        self,
        widget_manager: Optional[WidgetNotificationManager] = None,
        callback_registry: Optional[CallbackRegistry] = None,
        queue: Optional[NotificationQueue] = None,
        event_filter: Optional[EventFilter] = None,
        cross_thread_notifier: Optional[CrossThreadNotifier] = None,
        batcher: Optional[NotificationBatcher] = None
    ):
        """Initialize theme notifier with dependency injection.

        Args:
            widget_manager: Widget notification manager
            callback_registry: Callback registry
            queue: Notification queue
            event_filter: Event filter for performance
            cross_thread_notifier: Cross-thread notifier
            batcher: Notification batcher

        """
        self._widget_manager = widget_manager or WidgetNotificationManager()
        self._callback_registry = callback_registry or CallbackRegistry()
        self._queue = queue or NotificationQueue()
        self._event_filter = event_filter or EventFilter()
        self._cross_thread_notifier = cross_thread_notifier or CrossThreadNotifier()
        self._batcher = batcher or NotificationBatcher()

        self._stats = NotificationStats()
        self._lock = threading.RLock()

        # Set up queue processor
        self._queue.set_processor(self._process_notification)

        # Set up batcher processor
        self._batcher.set_batch_processor(self._process_notification_batch)

        logger.debug("ThemeNotifier initialized with all components")

    def register_widget(self, widget: QObject) -> bool:
        """Register widget for theme notifications.

        Args:
            widget: Widget to register

        Returns:
            True if successfully registered

        """
        success = self._widget_manager.register_widget(widget)

        if success:
            with self._lock:
                self._stats.widgets_registered += 1

        return success

    def unregister_widget(self, widget: QObject) -> bool:
        """Unregister widget from notifications.

        Args:
            widget: Widget to unregister

        Returns:
            True if successfully unregistered

        """
        success = self._widget_manager.unregister_widget(widget)

        if success:
            with self._lock:
                self._stats.widgets_registered -= 1

        return success

    def is_widget_registered(self, widget: QObject) -> bool:
        """Check if widget is registered.

        Args:
            widget: Widget to check

        Returns:
            True if widget is registered

        """
        return self._widget_manager.is_registered(widget)

    def register_callback(self, callback: ThemeChangeCallback) -> str:
        """Register theme change callback.

        Args:
            callback: Callback function

        Returns:
            Unique callback ID

        """
        callback_id = self._callback_registry.register_callback(callback)

        with self._lock:
            self._stats.callbacks_registered += 1

        return callback_id

    def unregister_callback(self, callback_id: str) -> bool:
        """Unregister callback.

        Args:
            callback_id: Callback ID to remove

        Returns:
            True if callback was removed

        """
        success = self._callback_registry.unregister_callback(callback_id)

        if success:
            with self._lock:
                self._stats.callbacks_registered -= 1

        return success

    def has_callback(self, callback_id: str) -> bool:
        """Check if callback is registered.

        Args:
            callback_id: Callback ID to check

        Returns:
            True if callback exists

        """
        return self._callback_registry.has_callback(callback_id)

    def notify_theme_changed(self, theme_name: str) -> None:
        """Notify all registered widgets and callbacks of theme change.

        Args:
            theme_name: Name of new theme

        """
        start_time = time.time()

        try:
            # Notify all widgets
            widget_results = self._widget_manager.notify_all_widgets(theme_name)

            # Call all callbacks
            for widget_id in widget_results:
                if self._event_filter.should_notify(theme_name, widget_id):
                    self._callback_registry.call_all_callbacks(theme_name, widget_id)
                else:
                    with self._lock:
                        self._stats.filtered_notifications += 1

            # Update statistics
            with self._lock:
                self._stats.notifications_sent += len(widget_results)
                self._stats.total_time += time.time() - start_time

            logger.debug(f"Notified all widgets of theme change: {theme_name}")

        except Exception as e:
            logger.error(f"Error in global theme notification: {e}")
            with self._lock:
                self._stats.errors += 1

    def notify_widget(self, widget: QObject, theme_name: str) -> bool:
        """Notify specific widget of theme change.

        Args:
            widget: Widget to notify
            theme_name: Name of new theme

        Returns:
            True if notification was sent

        """
        try:
            widget_id = f"widget_{id(widget)}"

            if not self._event_filter.should_notify(theme_name, widget_id):
                with self._lock:
                    self._stats.filtered_notifications += 1
                return True  # Filtered, but not an error

            success = self._widget_manager.notify_widget(widget, theme_name)

            if success:
                self._callback_registry.call_all_callbacks(theme_name, widget_id)

            with self._lock:
                if success:
                    self._stats.notifications_sent += 1
                else:
                    self._stats.errors += 1

            return success

        except Exception as e:
            logger.error(f"Error notifying specific widget: {e}")
            with self._lock:
                self._stats.errors += 1
            return False

    def batch_notify_widgets(self, widgets: List[QObject], theme_name: str) -> Dict[QObject, bool]:
        """Batch notify multiple widgets efficiently.

        Args:
            widgets: List of widgets to notify
            theme_name: Name of new theme

        Returns:
            Dictionary mapping widget to notification success

        """
        results = {}

        for widget in widgets:
            results[widget] = self.notify_widget(widget, theme_name)

        with self._lock:
            self._stats.batched_notifications += len(widgets)

        return results

    def set_notification_filter(self, filter_func: Callable[[str], bool]) -> None:
        """Set theme name filter for notifications.

        Args:
            filter_func: Function that returns True if theme should be notified

        """
        self._event_filter.add_theme_filter(filter_func)

    def get_statistics(self) -> Dict[str, Any]:
        """Get notification statistics.

        Returns:
            Dictionary with notification statistics

        """
        with self._lock:
            base_stats = {
                "notifications_sent": self._stats.notifications_sent,
                "widgets_registered": self._stats.widgets_registered,
                "callbacks_registered": self._stats.callbacks_registered,
                "errors": self._stats.errors,
                "total_time": self._stats.total_time,
                "filtered_notifications": self._stats.filtered_notifications,
                "batched_notifications": self._stats.batched_notifications,
                "average_time_per_notification": (
                    self._stats.total_time / max(1, self._stats.notifications_sent)
                )
            }

            # Add component statistics
            base_stats.update({
                "callback_stats": self._callback_registry.get_statistics(),
                "filter_stats": self._event_filter.get_statistics()
            })

            return base_stats

    def _process_notification(self, theme_name: str, widget_id: str) -> None:
        """Process single notification from queue."""
        try:
            if self._event_filter.should_notify(theme_name, widget_id):
                self._callback_registry.call_all_callbacks(theme_name, widget_id)
        except Exception as e:
            logger.error(f"Error processing queued notification: {e}")

    def _process_notification_batch(self, batch: List[Tuple[str, str]]) -> None:
        """Process batch of notifications."""
        try:
            for theme_name, widget_id in batch:
                self._process_notification(theme_name, widget_id)

            with self._lock:
                self._stats.batched_notifications += len(batch)

        except Exception as e:
            logger.error(f"Error processing notification batch: {e}")

    def shutdown(self) -> None:
        """Shutdown notifier and clean up resources."""
        try:
            self._queue.stop_async_processing()
            self._cross_thread_notifier.shutdown()
            logger.debug("ThemeNotifier shutdown completed")

        except Exception as e:
            logger.error(f"Error during notifier shutdown: {e}")


def create_theme_notifier(
    max_queue_size: int = 1000,
    batch_size: int = 10,
    flush_interval: float = 0.1
) -> ThemeNotifier:
    """Factory function for creating theme notifier with defaults.

    Args:
        max_queue_size: Maximum notification queue size
        batch_size: Notification batch size
        flush_interval: Batch flush interval in seconds

    Returns:
        Configured theme notifier

    """
    # Create all specialized components
    widget_manager = WidgetNotificationManager()
    callback_registry = CallbackRegistry()
    queue = NotificationQueue(max_size=max_queue_size)
    event_filter = EventFilter()
    cross_thread_notifier = CrossThreadNotifier()
    batcher = NotificationBatcher(batch_size=batch_size, flush_interval=flush_interval)

    notifier = ThemeNotifier(
        widget_manager=widget_manager,
        callback_registry=callback_registry,
        queue=queue,
        event_filter=event_filter,
        cross_thread_notifier=cross_thread_notifier,
        batcher=batcher
    )

    logger.debug("Created theme notifier with default configuration")
    return notifier


__all__ = [
    "ThemeNotifier",
    "WidgetNotificationManager",
    "CallbackRegistry",
    "NotificationQueue",
    "EventFilter",
    "CrossThreadNotifier",
    "NotificationBatcher",
    "NotificationStats",
    "NotificationItem",
    "create_theme_notifier",
]
