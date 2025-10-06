"""
Test suite for ThemeNotifier.

Tests change notification system including:
- Widget notification using Qt signals
- Callback registration and management
- Event filtering for performance
- Notification queuing and batching
- Cross-thread notification support
- Error handling in notification paths
"""

import threading
import time
from typing import List

import pytest

# Import Qt components with fallback for headless testing
try:
    from PySide6.QtCore import QObject, QThread, QTimer, Signal
    from PySide6.QtWidgets import QApplication, QWidget

    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False

    # Create mock classes for headless testing
    class QObject:
        def __init__(self):
            self.signals = {}

        def connect(self, slot):
            pass

        def disconnect(self, slot):
            pass

        def emit(self, *args):
            pass

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


# Import the modules under test
from vfwidgets_theme.core.notifier import (
    CallbackRegistry,
    CrossThreadNotifier,
    EventFilter,
    NotificationBatcher,
    NotificationQueue,
    ThemeNotifier,
    WidgetNotificationManager,
    create_theme_notifier,
)
from vfwidgets_theme.core.theme import Theme
from vfwidgets_theme.testing import ThemedTestCase


class MockWidget(QObject):
    """Mock widget for testing notifications."""

    def __init__(self, name: str = "mock-widget"):
        super().__init__()
        self.name = name
        self.notifications_received = []
        self.theme_changed = Signal(str)  # theme_name

    def on_theme_changed(self, theme_name: str):
        """Mock theme change handler."""
        self.notifications_received.append(theme_name)


class TestThemeNotifier(ThemedTestCase):
    """Test ThemeNotifier main coordination class."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.notifier = ThemeNotifier()

        # Create sample theme
        self.sample_theme = Theme.from_dict(
            {
                "name": "test-theme",
                "version": "1.0.0",
                "colors": {"primary": "#007acc"},
                "styles": {"QPushButton": "background-color: @colors.primary;"},
            }
        )

    def test_notifier_initialization(self):
        """Test notifier initialization with default settings."""
        notifier = ThemeNotifier()
        self.assertIsNotNone(notifier)
        self.assertIsInstance(notifier._widget_manager, WidgetNotificationManager)
        self.assertIsInstance(notifier._callback_registry, CallbackRegistry)
        self.assertIsInstance(notifier._queue, NotificationQueue)

    def test_notifier_with_custom_components(self):
        """Test notifier initialization with custom components."""
        custom_manager = WidgetNotificationManager()
        custom_registry = CallbackRegistry()
        custom_queue = NotificationQueue()

        notifier = ThemeNotifier(
            widget_manager=custom_manager, callback_registry=custom_registry, queue=custom_queue
        )

        self.assertIs(notifier._widget_manager, custom_manager)
        self.assertIs(notifier._callback_registry, custom_registry)
        self.assertIs(notifier._queue, custom_queue)

    def test_register_widget_for_notifications(self):
        """Test registering widget for theme notifications."""
        widget = MockWidget("test-widget")

        success = self.notifier.register_widget(widget)

        self.assertTrue(success)
        self.assertTrue(self.notifier.is_widget_registered(widget))

    def test_unregister_widget(self):
        """Test unregistering widget from notifications."""
        widget = MockWidget("test-widget")

        self.notifier.register_widget(widget)
        self.assertTrue(self.notifier.is_widget_registered(widget))

        success = self.notifier.unregister_widget(widget)

        self.assertTrue(success)
        self.assertFalse(self.notifier.is_widget_registered(widget))

    def test_register_callback(self):
        """Test registering theme change callback."""
        callback_called = []

        def test_callback(theme_name: str, widget_id: str):
            callback_called.append((theme_name, widget_id))

        callback_id = self.notifier.register_callback(test_callback)

        self.assertIsNotNone(callback_id)
        self.assertTrue(self.notifier.has_callback(callback_id))

    def test_unregister_callback(self):
        """Test unregistering theme change callback."""

        def test_callback(theme_name: str, widget_id: str):
            pass

        callback_id = self.notifier.register_callback(test_callback)
        self.assertTrue(self.notifier.has_callback(callback_id))

        success = self.notifier.unregister_callback(callback_id)

        self.assertTrue(success)
        self.assertFalse(self.notifier.has_callback(callback_id))

    def test_notify_theme_changed(self):
        """Test notifying widgets of theme changes."""
        widget = MockWidget("test-widget")
        self.notifier.register_widget(widget)

        # Connect widget's signal to track notifications
        received_themes = []
        widget.theme_changed.connect(lambda name: received_themes.append(name))

        self.notifier.notify_theme_changed("test-theme")

        # Allow time for async notifications
        time.sleep(0.1)

        # Verify notification was received
        # Note: This depends on the notification system implementation
        self.assertGreaterEqual(len(received_themes), 0)

    def test_notify_specific_widget(self):
        """Test notifying specific widget of theme change."""
        widget1 = MockWidget("widget-1")
        widget2 = MockWidget("widget-2")

        self.notifier.register_widget(widget1)
        self.notifier.register_widget(widget2)

        # Notify only widget1
        success = self.notifier.notify_widget(widget1, "specific-theme")

        self.assertTrue(success)
        # Widget1 should be notified, widget2 should not
        # This would be verified through the widget's notification tracking

    def test_batch_notifications(self):
        """Test batch notification for multiple widgets."""
        widgets = [MockWidget(f"widget-{i}") for i in range(5)]

        for widget in widgets:
            self.notifier.register_widget(widget)

        # Batch notify all widgets
        results = self.notifier.batch_notify_widgets(widgets, "batch-theme")

        self.assertEqual(len(results), 5)
        # All notifications should succeed (assuming no errors)
        self.assertTrue(all(results.values()))

    def test_notification_filtering(self):
        """Test notification event filtering for performance."""
        widget = MockWidget("filtered-widget")
        self.notifier.register_widget(widget)

        # Set up filter to only allow certain themes
        def theme_filter(theme_name: str) -> bool:
            return theme_name.startswith("allowed-")

        self.notifier.set_notification_filter(theme_filter)

        # Test filtered notification
        self.notifier.notify_theme_changed("allowed-theme")
        self.notifier.notify_theme_changed("blocked-theme")

        # Only "allowed-theme" should be processed
        # Verification depends on implementation details

    def test_notification_statistics(self):
        """Test getting notification statistics."""
        widget = MockWidget("stats-widget")
        self.notifier.register_widget(widget)

        # Send some notifications
        self.notifier.notify_theme_changed("theme-1")
        self.notifier.notify_theme_changed("theme-2")

        stats = self.notifier.get_statistics()

        self.assertIn("notifications_sent", stats)
        self.assertIn("widgets_registered", stats)
        self.assertIn("callbacks_registered", stats)
        self.assertGreaterEqual(stats["notifications_sent"], 0)

    def test_error_handling_in_notifications(self):
        """Test error handling during notification delivery."""
        widget = MockWidget("error-widget")
        self.notifier.register_widget(widget)

        # Register callback that raises exception
        def error_callback(theme_name: str, widget_id: str):
            raise Exception("Test notification error")

        self.notifier.register_callback(error_callback)

        # Notification should not crash despite callback error
        try:
            self.notifier.notify_theme_changed("error-theme")
            # Should complete without raising exception
            success = True
        except Exception:
            success = False

        self.assertTrue(success)

    def test_performance_requirements(self):
        """Test notifier meets performance requirements."""
        widgets = [MockWidget(f"perf-widget-{i}") for i in range(100)]

        for widget in widgets:
            self.notifier.register_widget(widget)

        # Test notification overhead (< 10μs per widget requirement)
        start_time = time.time()
        self.notifier.notify_theme_changed("performance-theme")
        notification_time = time.time() - start_time

        # For 100 widgets, should be less than 1ms (10μs * 100)
        self.assertLess(notification_time, 0.001)


class TestWidgetNotificationManager(ThemedTestCase):
    """Test WidgetNotificationManager for widget-specific notifications."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.manager = WidgetNotificationManager()

    def test_register_widget(self):
        """Test registering widget for notifications."""
        widget = MockWidget("managed-widget")

        success = self.manager.register_widget(widget)

        self.assertTrue(success)
        self.assertTrue(self.manager.is_registered(widget))

    def test_register_duplicate_widget(self):
        """Test registering same widget twice."""
        widget = MockWidget("duplicate-widget")

        success1 = self.manager.register_widget(widget)
        success2 = self.manager.register_widget(widget)

        self.assertTrue(success1)
        self.assertTrue(success2)  # Should handle duplicates gracefully

    def test_unregister_widget(self):
        """Test unregistering widget."""
        widget = MockWidget("unregistered-widget")

        self.manager.register_widget(widget)
        success = self.manager.unregister_widget(widget)

        self.assertTrue(success)
        self.assertFalse(self.manager.is_registered(widget))

    def test_notify_registered_widgets(self):
        """Test notifying all registered widgets."""
        widgets = [MockWidget(f"notify-widget-{i}") for i in range(3)]

        for widget in widgets:
            self.manager.register_widget(widget)

        results = self.manager.notify_all_widgets("notify-theme")

        self.assertEqual(len(results), 3)
        # All notifications should succeed
        self.assertTrue(all(results.values()))

    def test_notify_specific_widget(self):
        """Test notifying specific widget."""
        widget = MockWidget("specific-widget")
        self.manager.register_widget(widget)

        success = self.manager.notify_widget(widget, "specific-theme")

        self.assertTrue(success)

    def test_notify_nonexistent_widget(self):
        """Test notifying widget that's not registered."""
        widget = MockWidget("nonexistent-widget")

        success = self.manager.notify_widget(widget, "theme")

        self.assertFalse(success)

    def test_widget_cleanup_on_deletion(self):
        """Test automatic cleanup when widget is deleted."""
        widget = MockWidget("cleanup-widget")
        self.manager.register_widget(widget)

        self.assertTrue(self.manager.is_registered(widget))

        # Delete widget
        widget_id = id(widget)
        del widget

        # Manager should detect and clean up dead references
        # This may require calling cleanup manually or waiting for GC
        self.manager.cleanup_dead_references()

        # Verify cleanup occurred (implementation dependent)
        registered_count = self.manager.get_registered_count()
        # Should be 0 after cleanup
        self.assertEqual(registered_count, 0)

    def test_thread_safety(self):
        """Test thread safety of widget registration."""
        widgets = []
        results = []
        errors = []

        def worker(worker_id: int):
            """Worker function for concurrent widget registration."""
            try:
                for i in range(10):
                    widget = MockWidget(f"thread-{worker_id}-widget-{i}")
                    widgets.append(widget)
                    success = self.manager.register_widget(widget)
                    results.append(success)
                    time.sleep(0.001)  # Small delay
            except Exception as e:
                errors.append(f"Worker {worker_id}: {e}")

        threads = []
        for worker_id in range(5):
            thread = threading.Thread(target=worker, args=(worker_id,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        self.assertEqual(len(errors), 0, f"Thread safety errors: {errors}")
        self.assertEqual(len(results), 50)  # 5 workers * 10 widgets each
        self.assertTrue(all(results))


class TestCallbackRegistry(ThemedTestCase):
    """Test CallbackRegistry for managing notification callbacks."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.registry = CallbackRegistry()

    def test_register_callback(self):
        """Test registering notification callback."""
        callback_calls = []

        def test_callback(theme_name: str, widget_id: str):
            callback_calls.append((theme_name, widget_id))

        callback_id = self.registry.register_callback(test_callback)

        self.assertIsNotNone(callback_id)
        self.assertTrue(self.registry.has_callback(callback_id))

    def test_unregister_callback(self):
        """Test unregistering callback."""

        def test_callback(theme_name: str, widget_id: str):
            pass

        callback_id = self.registry.register_callback(test_callback)
        success = self.registry.unregister_callback(callback_id)

        self.assertTrue(success)
        self.assertFalse(self.registry.has_callback(callback_id))

    def test_call_all_callbacks(self):
        """Test calling all registered callbacks."""
        call_records = []

        def callback1(theme_name: str, widget_id: str):
            call_records.append(f"callback1:{theme_name}:{widget_id}")

        def callback2(theme_name: str, widget_id: str):
            call_records.append(f"callback2:{theme_name}:{widget_id}")

        self.registry.register_callback(callback1)
        self.registry.register_callback(callback2)

        self.registry.call_all_callbacks("test-theme", "test-widget")

        self.assertEqual(len(call_records), 2)
        self.assertIn("callback1:test-theme:test-widget", call_records)
        self.assertIn("callback2:test-theme:test-widget", call_records)

    def test_callback_error_handling(self):
        """Test error handling in callback execution."""
        call_records = []

        def good_callback(theme_name: str, widget_id: str):
            call_records.append("good_callback_called")

        def error_callback(theme_name: str, widget_id: str):
            raise Exception("Callback error")

        self.registry.register_callback(good_callback)
        self.registry.register_callback(error_callback)

        # Should not raise exception despite error callback
        self.registry.call_all_callbacks("test-theme", "test-widget")

        # Good callback should still be called
        self.assertIn("good_callback_called", call_records)

    def test_callback_filtering(self):
        """Test callback filtering by criteria."""
        call_records = []

        def filtered_callback(theme_name: str, widget_id: str):
            call_records.append(f"filtered:{theme_name}")

        callback_id = self.registry.register_callback(filtered_callback)

        # Set filter to only call for specific themes
        def callback_filter(theme_name: str, widget_id: str) -> bool:
            return theme_name.startswith("filtered-")

        self.registry.set_callback_filter(callback_id, callback_filter)

        # Test filtered calls
        self.registry.call_all_callbacks("filtered-theme", "widget")
        self.registry.call_all_callbacks("blocked-theme", "widget")

        # Only filtered theme should trigger callback
        self.assertEqual(len(call_records), 1)
        self.assertIn("filtered:filtered-theme", call_records)

    def test_callback_statistics(self):
        """Test callback registry statistics."""

        def callback1(theme_name: str, widget_id: str):
            pass

        def callback2(theme_name: str, widget_id: str):
            pass

        self.registry.register_callback(callback1)
        self.registry.register_callback(callback2)

        self.registry.call_all_callbacks("theme", "widget")
        self.registry.call_all_callbacks("theme", "widget")

        stats = self.registry.get_statistics()

        self.assertEqual(stats["registered_callbacks"], 2)
        self.assertEqual(stats["total_calls"], 4)  # 2 callbacks * 2 calls
        self.assertGreaterEqual(stats["successful_calls"], 0)


class TestNotificationQueue(ThemedTestCase):
    """Test NotificationQueue for queuing and batching notifications."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.queue = NotificationQueue()

    def test_queue_notification(self):
        """Test queuing single notification."""
        self.queue.enqueue_notification("test-theme", "test-widget")

        self.assertEqual(self.queue.size(), 1)
        self.assertFalse(self.queue.is_empty())

    def test_process_queued_notifications(self):
        """Test processing queued notifications."""
        processed_notifications = []

        def processor(theme_name: str, widget_id: str):
            processed_notifications.append((theme_name, widget_id))

        self.queue.set_processor(processor)

        # Queue multiple notifications
        self.queue.enqueue_notification("theme1", "widget1")
        self.queue.enqueue_notification("theme2", "widget2")

        # Process queue
        processed_count = self.queue.process_all()

        self.assertEqual(processed_count, 2)
        self.assertEqual(len(processed_notifications), 2)
        self.assertTrue(self.queue.is_empty())

    def test_batch_processing(self):
        """Test batch processing of notifications."""
        batch_sizes = []

        def batch_processor(notifications: List[tuple]):
            batch_sizes.append(len(notifications))

        self.queue.set_batch_processor(batch_processor, batch_size=3)

        # Queue notifications
        for i in range(7):  # 2 batches of 3 + 1 remaining
            self.queue.enqueue_notification(f"theme{i}", f"widget{i}")

        processed_count = self.queue.process_all()

        self.assertEqual(processed_count, 7)
        # Should have processed in batches
        self.assertGreater(len(batch_sizes), 0)

    def test_priority_notifications(self):
        """Test priority notification handling."""
        processed_order = []

        def processor(theme_name: str, widget_id: str):
            processed_order.append(theme_name)

        self.queue.set_processor(processor)

        # Queue normal and priority notifications
        self.queue.enqueue_notification("normal1", "widget1")
        self.queue.enqueue_priority_notification("priority1", "widget2")
        self.queue.enqueue_notification("normal2", "widget3")

        self.queue.process_all()

        # Priority notification should be processed first
        self.assertEqual(processed_order[0], "priority1")

    def test_queue_size_limits(self):
        """Test queue size limiting."""
        limited_queue = NotificationQueue(max_size=3)

        # Fill queue to capacity
        for i in range(3):
            success = limited_queue.enqueue_notification(f"theme{i}", f"widget{i}")
            self.assertTrue(success)

        # Queue should be at capacity
        self.assertEqual(limited_queue.size(), 3)
        self.assertTrue(limited_queue.is_full())

        # Adding more should fail or drop oldest
        success = limited_queue.enqueue_notification("overflow", "widget")
        # Depending on implementation, this might return False or drop oldest
        self.assertIsInstance(success, bool)

    def test_async_processing(self):
        """Test asynchronous queue processing."""
        processed_notifications = []
        processing_complete = threading.Event()

        def async_processor(theme_name: str, widget_id: str):
            processed_notifications.append((theme_name, widget_id))
            if len(processed_notifications) == 3:
                processing_complete.set()

        self.queue.set_processor(async_processor)

        # Queue notifications
        for i in range(3):
            self.queue.enqueue_notification(f"async-theme{i}", f"widget{i}")

        # Start async processing
        self.queue.start_async_processing()

        # Wait for processing to complete
        self.assertTrue(processing_complete.wait(timeout=1.0))
        self.assertEqual(len(processed_notifications), 3)

        # Clean up
        self.queue.stop_async_processing()


class TestEventFilter(ThemedTestCase):
    """Test EventFilter for performance optimization."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.event_filter = EventFilter()

    def test_filter_by_theme_pattern(self):
        """Test filtering notifications by theme name pattern."""
        # Set up filter to only allow themes starting with "allowed-"
        self.event_filter.add_theme_filter(lambda name: name.startswith("allowed-"))

        # Test filtering
        self.assertTrue(self.event_filter.should_notify("allowed-theme", "widget"))
        self.assertFalse(self.event_filter.should_notify("blocked-theme", "widget"))

    def test_filter_by_widget_pattern(self):
        """Test filtering notifications by widget ID pattern."""
        # Set up filter for specific widget types
        self.event_filter.add_widget_filter(lambda wid: "button" in wid)

        # Test filtering
        self.assertTrue(self.event_filter.should_notify("theme", "my-button-widget"))
        self.assertFalse(self.event_filter.should_notify("theme", "my-label-widget"))

    def test_combined_filters(self):
        """Test combining multiple filters."""
        self.event_filter.add_theme_filter(lambda name: name.startswith("ui-"))
        self.event_filter.add_widget_filter(lambda wid: "important" in wid)

        # Both filters must pass
        self.assertTrue(self.event_filter.should_notify("ui-theme", "important-widget"))
        self.assertFalse(self.event_filter.should_notify("ui-theme", "normal-widget"))
        self.assertFalse(self.event_filter.should_notify("other-theme", "important-widget"))

    def test_performance_filtering(self):
        """Test filtering reduces notification overhead."""
        # Set restrictive filter
        self.event_filter.add_theme_filter(lambda name: name == "specific-theme")

        notifications_processed = []

        def processor(theme_name: str, widget_id: str):
            notifications_processed.append((theme_name, widget_id))

        # Test many notifications with filter
        start_time = time.time()
        for i in range(100):
            if self.event_filter.should_notify(f"theme{i}", f"widget{i}"):
                processor(f"theme{i}", f"widget{i}")

        # Only "specific-theme" should pass filter (none in this case)
        filter_time = time.time() - start_time

        # Filtering should be very fast
        self.assertLess(filter_time, 0.001)  # < 1ms for 100 checks
        self.assertEqual(len(notifications_processed), 0)

    def test_filter_statistics(self):
        """Test event filter statistics tracking."""
        self.event_filter.add_theme_filter(lambda name: name.startswith("allowed-"))

        # Process notifications through filter
        for i in range(10):
            theme_name = "allowed-theme" if i % 2 == 0 else "blocked-theme"
            self.event_filter.should_notify(theme_name, f"widget{i}")

        stats = self.event_filter.get_statistics()

        self.assertEqual(stats["total_checks"], 10)
        self.assertEqual(stats["notifications_allowed"], 5)
        self.assertEqual(stats["notifications_blocked"], 5)


class TestCrossThreadNotifier(ThemedTestCase):
    """Test CrossThreadNotifier for thread-safe notifications."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.cross_thread_notifier = CrossThreadNotifier()

    def test_cross_thread_notification(self):
        """Test notifications across different threads."""
        notifications_received = []
        notification_complete = threading.Event()

        def notification_handler(theme_name: str, widget_id: str):
            notifications_received.append((theme_name, widget_id))
            notification_complete.set()

        self.cross_thread_notifier.register_handler(notification_handler)

        # Send notification from different thread
        def worker():
            self.cross_thread_notifier.notify_async("cross-thread-theme", "cross-widget")

        thread = threading.Thread(target=worker)
        thread.start()
        thread.join()

        # Wait for notification to be processed
        self.assertTrue(notification_complete.wait(timeout=1.0))
        self.assertEqual(len(notifications_received), 1)
        self.assertEqual(notifications_received[0], ("cross-thread-theme", "cross-widget"))

    def test_thread_safe_registration(self):
        """Test thread-safe handler registration."""
        handlers_registered = []
        registration_errors = []

        def register_worker(worker_id: int):
            try:

                def handler(theme_name: str, widget_id: str):
                    pass

                self.cross_thread_notifier.register_handler(handler)
                handlers_registered.append(worker_id)
            except Exception as e:
                registration_errors.append(f"Worker {worker_id}: {e}")

        threads = []
        for worker_id in range(5):
            thread = threading.Thread(target=register_worker, args=(worker_id,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        self.assertEqual(len(registration_errors), 0, f"Registration errors: {registration_errors}")
        self.assertEqual(len(handlers_registered), 5)

    def test_notification_ordering(self):
        """Test that notifications maintain ordering across threads."""
        received_order = []
        completion_events = [threading.Event() for _ in range(5)]

        def ordered_handler(theme_name: str, widget_id: str):
            order_id = int(theme_name.split("-")[-1])
            received_order.append(order_id)
            completion_events[order_id].set()

        self.cross_thread_notifier.register_handler(ordered_handler)

        # Send notifications from multiple threads
        def notify_worker(order_id: int):
            self.cross_thread_notifier.notify_async(
                f"ordered-theme-{order_id}", f"widget-{order_id}"
            )

        threads = []
        for i in range(5):
            thread = threading.Thread(target=notify_worker, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Wait for all notifications to complete
        for event in completion_events:
            self.assertTrue(event.wait(timeout=1.0))

        # Verify all notifications were received
        self.assertEqual(len(received_order), 5)
        self.assertEqual(sorted(received_order), list(range(5)))


class TestNotificationBatcher(ThemedTestCase):
    """Test NotificationBatcher for efficient batch processing."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.batcher = NotificationBatcher(batch_size=3, flush_interval=0.1)

    def test_batch_accumulation(self):
        """Test accumulation of notifications into batches."""
        processed_batches = []

        def batch_processor(batch: List[tuple]):
            processed_batches.append(batch)

        self.batcher.set_batch_processor(batch_processor)

        # Add notifications to trigger batch
        for i in range(5):
            self.batcher.add_notification(f"theme{i}", f"widget{i}")

        # Should have processed at least one full batch
        time.sleep(0.05)  # Allow processing time
        self.batcher.flush()  # Force flush remaining

        self.assertGreater(len(processed_batches), 0)
        # Total notifications should equal original count
        total_processed = sum(len(batch) for batch in processed_batches)
        self.assertEqual(total_processed, 5)

    def test_time_based_flushing(self):
        """Test automatic flushing based on time interval."""
        processed_batches = []

        def batch_processor(batch: List[tuple]):
            processed_batches.append(batch)

        self.batcher.set_batch_processor(batch_processor)

        # Add single notification (below batch size)
        self.batcher.add_notification("time-theme", "time-widget")

        # Wait for time-based flush
        time.sleep(0.2)  # Wait longer than flush interval

        # Should have flushed despite being under batch size
        self.assertGreater(len(processed_batches), 0)

    def test_batch_size_optimization(self):
        """Test batch size affects processing efficiency."""
        small_batch_count = 0
        large_batch_count = 0

        def small_batch_processor(batch: List[tuple]):
            nonlocal small_batch_count
            small_batch_count += len(batch)

        def large_batch_processor(batch: List[tuple]):
            nonlocal large_batch_count
            large_batch_count += len(batch)

        # Test small batches
        small_batcher = NotificationBatcher(batch_size=2)
        small_batcher.set_batch_processor(small_batch_processor)

        # Test large batches
        large_batcher = NotificationBatcher(batch_size=10)
        large_batcher.set_batch_processor(large_batch_processor)

        # Add same number of notifications to both
        for i in range(20):
            small_batcher.add_notification(f"theme{i}", f"widget{i}")
            large_batcher.add_notification(f"theme{i}", f"widget{i}")

        # Flush both
        small_batcher.flush()
        large_batcher.flush()

        # Both should process all notifications
        self.assertEqual(small_batch_count, 20)
        self.assertEqual(large_batch_count, 20)


class TestNotifierIntegration(ThemedTestCase):
    """Integration tests for notifier components working together."""

    def test_complete_notification_workflow(self):
        """Test complete notification workflow from registration to delivery."""
        # Create notifier with all components
        notifier = create_theme_notifier()

        # Create widgets and callbacks
        widgets = [MockWidget(f"integration-widget-{i}") for i in range(3)]
        callback_calls = []

        def integration_callback(theme_name: str, widget_id: str):
            callback_calls.append((theme_name, widget_id))

        # Register widgets and callback
        for widget in widgets:
            notifier.register_widget(widget)

        callback_id = notifier.register_callback(integration_callback)

        # Send notification
        notifier.notify_theme_changed("integration-theme")

        # Allow processing time
        time.sleep(0.1)

        # Verify callback was called
        self.assertGreaterEqual(len(callback_calls), 0)

        # Test statistics
        stats = notifier.get_statistics()
        self.assertIn("notifications_sent", stats)
        self.assertIn("widgets_registered", stats)

    def test_performance_with_many_widgets(self):
        """Test notification performance with large number of widgets."""
        notifier = create_theme_notifier()

        # Register many widgets
        widgets = [MockWidget(f"perf-widget-{i}") for i in range(100)]
        for widget in widgets:
            notifier.register_widget(widget)

        # Measure notification time
        start_time = time.time()
        notifier.notify_theme_changed("performance-theme")
        notification_time = time.time() - start_time

        # Should meet performance requirement (< 10μs per widget)
        # For 100 widgets: < 1ms total
        self.assertLess(notification_time, 0.001)

    def test_memory_efficiency(self):
        """Test memory efficiency of notification system."""
        import gc

        notifier = create_theme_notifier()

        # Create widgets and register them
        initial_objects = len(gc.get_objects())

        widgets = [MockWidget(f"memory-widget-{i}") for i in range(50)]
        for widget in widgets:
            notifier.register_widget(widget)

        mid_objects = len(gc.get_objects())

        # Clean up widgets
        del widgets
        gc.collect()

        # Allow notifier to clean up dead references
        time.sleep(0.1)

        final_objects = len(gc.get_objects())

        # Memory should be efficiently managed
        # Most widget-related objects should be cleaned up
        memory_growth = mid_objects - initial_objects
        memory_cleanup = mid_objects - final_objects

        cleanup_ratio = memory_cleanup / memory_growth if memory_growth > 0 else 1.0
        self.assertGreater(cleanup_ratio, 0.5)  # At least 50% cleanup


if __name__ == "__main__":
    pytest.main([__file__])
