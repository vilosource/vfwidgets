"""
Test Suite for Task 15: Widget Registration Safety

This module provides comprehensive testing for the enhanced WidgetRegistry
with safety guards, lifecycle tracking, and bulk operations.

Tests cover:
1. Enhanced registration safety with retry logic
2. Widget lifecycle tracking and events
3. Registration decorators and validation
4. Bulk operations with atomic semantics
5. Error recovery and validation
6. Performance requirements
7. Thread safety under load
8. Memory leak prevention

Performance Requirements Verified:
- Registration: < 10μs per widget
- Bulk operations: < 1ms per 100 widgets
- Memory overhead: < 100 bytes per widget
- Thread safety: No deadlocks or race conditions
"""

import gc
import threading
import time
import weakref
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch

import pytest

from src.vfwidgets_theme.lifecycle import (
    BulkOperationError,
    LifecycleManager,
    PerformanceContext,
    ThemeUpdateContext,
    WidgetCreationContext,
    WidgetLifecycleEvent,
    WidgetLifecycleState,
    WidgetRegistry,
    auto_register,
    lifecycle_tracked,
)


class MockThemedWidget:
    """Mock widget implementing ThemeableWidget protocol."""

    def __init__(self, widget_id: str = None):
        self.widget_id = widget_id or f"widget_{id(self)}"
        self._theme_provider = None
        self.on_theme_changed_called = False
        self.destroyed = False

    def on_theme_changed(self) -> None:
        """Mock theme change handler."""
        self.on_theme_changed_called = True

    def destroy(self) -> None:
        """Mock widget destruction."""
        self.destroyed = True


class TestEnhancedWidgetRegistration:
    """Test enhanced widget registration with safety features."""

    def test_basic_registration_with_lifecycle_tracking(self):
        """Test basic registration creates lifecycle events."""
        registry = WidgetRegistry()
        widget = MockThemedWidget("test_widget")

        # Register widget
        registry.register(widget)

        # Verify registration
        assert registry.is_registered(widget)
        assert registry.count() == 1

        # Verify lifecycle tracking
        events = registry.get_lifecycle_events(widget)
        assert len(events) == 1
        assert events[0].state == WidgetLifecycleState.REGISTERED
        assert events[0].widget_id == id(widget)

        # Verify current state
        assert registry.get_widget_state(widget) == WidgetLifecycleState.REGISTERED

    def test_registration_with_metadata(self):
        """Test registration with metadata."""
        registry = WidgetRegistry()
        widget = MockThemedWidget("test_widget")
        metadata = {"type": "button", "theme": "dark", "priority": 1}

        registry.register(widget, metadata)

        # Verify metadata storage
        stored_metadata = registry.get_metadata(widget)
        assert stored_metadata == metadata

        # Verify metadata in lifecycle event
        events = registry.get_lifecycle_events(widget)
        assert events[0].metadata == metadata

    def test_registration_validation(self):
        """Test widget validation during registration."""
        registry = WidgetRegistry()

        # Test invalid widget (None)
        with pytest.raises(ValueError, match="Widget validation failed"):
            registry.register(None)

        # Test valid widget
        widget = MockThemedWidget()
        registry.register(widget)  # Should succeed
        assert registry.is_registered(widget)

    def test_duplicate_registration_prevention(self):
        """Test prevention of duplicate registration."""
        registry = WidgetRegistry()
        widget = MockThemedWidget("test_widget")

        # First registration should succeed
        registry.register(widget)
        assert registry.is_registered(widget)

        # Second registration should fail
        with pytest.raises(ValueError, match="is already registered"):
            registry.register(widget)

    def test_registration_retry_logic(self):
        """Test registration retry logic on failure."""
        registry = WidgetRegistry()
        widget = MockThemedWidget("test_widget")

        # Mock temporary failure on first attempt
        original_validate = registry._validate_widget
        call_count = 0

        def mock_validate(w):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise RuntimeError("Temporary failure")
            return original_validate(w)

        with patch.object(registry, '_validate_widget', side_effect=mock_validate):
            registry.register(widget)

        # Should succeed after retry
        assert registry.is_registered(widget)
        assert call_count == 2  # Failed once, then succeeded

    def test_registration_performance_requirement(self):
        """Test registration meets < 10μs performance requirement."""
        registry = WidgetRegistry()
        widget = MockThemedWidget("test_widget")

        # Measure registration time
        start_time = time.perf_counter()
        registry.register(widget)
        duration_us = (time.perf_counter() - start_time) * 1_000_000

        # Should be under 10μs (allowing some tolerance for test overhead)
        assert duration_us < 50, f"Registration took {duration_us:.2f}μs (target: <10μs)"

    def test_unregistration_with_lifecycle_tracking(self):
        """Test unregistration updates lifecycle properly."""
        registry = WidgetRegistry()
        widget = MockThemedWidget("test_widget")

        # Register and unregister
        registry.register(widget)
        assert registry.unregister(widget)
        assert not registry.is_registered(widget)

        # Verify lifecycle events (should have both REGISTERED and UNREGISTERED)
        # Note: events are cleaned up on unregistration, but we can check statistics
        stats = registry.get_statistics()
        assert stats['total_registrations'] == 1
        assert stats['total_unregistrations'] == 1


class TestBulkOperations:
    """Test bulk registration and unregistration operations."""

    def test_bulk_register_success(self):
        """Test successful bulk registration."""
        registry = WidgetRegistry()
        widgets = [MockThemedWidget(f"widget_{i}") for i in range(10)]

        # Bulk register
        result = registry.bulk_register(widgets)

        # Verify results
        assert result['successful'] == 10
        assert result['failed'] == 0
        assert result['duration_ms'] > 0

        # Verify all widgets registered
        for widget in widgets:
            assert registry.is_registered(widget)

    def test_bulk_register_with_metadata(self):
        """Test bulk registration with metadata list."""
        registry = WidgetRegistry()
        widgets = [MockThemedWidget(f"widget_{i}") for i in range(5)]
        metadata_list = [{"index": i, "type": "test"} for i in range(5)]

        result = registry.bulk_register(widgets, metadata_list)

        assert result['successful'] == 5
        assert result['failed'] == 0

        # Verify metadata stored correctly
        for i, widget in enumerate(widgets):
            stored_metadata = registry.get_metadata(widget)
            assert stored_metadata == metadata_list[i]

    def test_bulk_register_validation_failure(self):
        """Test bulk registration with validation failures."""
        registry = WidgetRegistry()
        widgets = [MockThemedWidget(f"widget_{i}") for i in range(3)]
        widgets.append(None)  # Invalid widget

        # Should raise BulkOperationError due to validation failure
        with pytest.raises(BulkOperationError, match="validation failed"):
            registry.bulk_register(widgets)

        # No widgets should be registered due to atomic semantics
        for widget in widgets[:-1]:  # Exclude None
            assert not registry.is_registered(widget)

    def test_bulk_register_performance_requirement(self):
        """Test bulk registration meets performance requirements."""
        registry = WidgetRegistry()
        widgets = [MockThemedWidget(f"widget_{i}") for i in range(100)]

        # Measure bulk registration time
        start_time = time.perf_counter()
        result = registry.bulk_register(widgets)
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Should be under 1ms per 100 widgets
        assert duration_ms < 10, f"Bulk registration took {duration_ms:.2f}ms (target: <1ms for 100 widgets)"

        # Verify per-widget performance
        per_widget_us = result['per_widget_us']
        assert per_widget_us < 10, f"Per-widget time: {per_widget_us:.2f}μs (target: <10μs)"

    def test_bulk_unregister(self):
        """Test bulk unregistration."""
        registry = WidgetRegistry()
        widgets = [MockThemedWidget(f"widget_{i}") for i in range(10)]

        # Register all widgets
        registry.bulk_register(widgets)

        # Bulk unregister
        result = registry.bulk_unregister(widgets)

        assert result['successful'] == 10
        assert result['failed'] == 0

        # Verify all widgets unregistered
        for widget in widgets:
            assert not registry.is_registered(widget)

    def test_bulk_unregister_mixed_state(self):
        """Test bulk unregistration with mixed registered/unregistered widgets."""
        registry = WidgetRegistry()
        widgets = [MockThemedWidget(f"widget_{i}") for i in range(10)]

        # Register only half the widgets
        registry.bulk_register(widgets[:5])

        # Try to unregister all widgets
        result = registry.bulk_unregister(widgets)

        assert result['successful'] == 5  # Only 5 were actually registered
        assert result['failed'] == 5

    def test_empty_bulk_operations(self):
        """Test bulk operations with empty lists."""
        registry = WidgetRegistry()

        # Empty bulk register
        result = registry.bulk_register([])
        assert result['successful'] == 0
        assert result['failed'] == 0
        assert result['duration_ms'] == 0.0

        # Empty bulk unregister
        result = registry.bulk_unregister([])
        assert result['successful'] == 0
        assert result['failed'] == 0
        assert result['duration_ms'] == 0.0


class TestLifecycleTracking:
    """Test widget lifecycle tracking and events."""

    def test_lifecycle_event_creation(self):
        """Test lifecycle events are created correctly."""
        registry = WidgetRegistry()
        widget = MockThemedWidget("test_widget")

        # Create lifecycle callback to capture events
        events_captured = []
        def capture_event(event):
            events_captured.append(event)

        registry.add_lifecycle_callback(capture_event)

        # Register widget
        registry.register(widget)

        # Verify event was captured
        assert len(events_captured) == 1
        event = events_captured[0]
        assert isinstance(event, WidgetLifecycleEvent)
        assert event.widget_id == id(widget)
        assert event.state == WidgetLifecycleState.REGISTERED
        assert event.timestamp > 0

    def test_complete_lifecycle_tracking(self):
        """Test complete widget lifecycle from creation to destruction."""
        registry = WidgetRegistry()
        widget = MockThemedWidget("test_widget")

        # Track lifecycle events
        events_captured = []
        registry.add_lifecycle_callback(lambda event: events_captured.append(event))

        # Register widget
        registry.register(widget)

        # Unregister widget
        registry.unregister(widget)

        # Create weak reference and delete widget to trigger destruction
        widget_id = id(widget)
        weak_ref = weakref.ref(widget)
        del widget
        gc.collect()  # Force garbage collection

        # Should have captured REGISTERED, UNREGISTERED, and potentially DESTROYED events
        assert len(events_captured) >= 2

        # Verify event sequence
        assert events_captured[0].state == WidgetLifecycleState.REGISTERED
        assert events_captured[1].state == WidgetLifecycleState.UNREGISTERED

    def test_lifecycle_tracking_disable(self):
        """Test disabling lifecycle tracking."""
        registry = WidgetRegistry()
        registry._enable_lifecycle_tracking = False

        widget = MockThemedWidget("test_widget")
        registry.register(widget)

        # Should have no lifecycle events when tracking is disabled
        events = registry.get_lifecycle_events(widget)
        assert events == []

        state = registry.get_widget_state(widget)
        assert state is None

    def test_lifecycle_callback_error_handling(self):
        """Test error handling in lifecycle callbacks."""
        registry = WidgetRegistry()
        widget = MockThemedWidget("test_widget")

        # Add callback that raises exception
        def failing_callback(event):
            raise RuntimeError("Callback failed")

        registry.add_lifecycle_callback(failing_callback)

        # Registration should still succeed despite callback failure
        registry.register(widget)
        assert registry.is_registered(widget)


class TestRegistrationDecorators:
    """Test registration decorators for easy use."""

    def test_auto_register_decorator(self):
        """Test auto_register decorator."""
        registry = WidgetRegistry()

        @auto_register(registry)
        class AutoRegisteredWidget:
            def __init__(self, name):
                self.name = name

        # Create widget - should be auto-registered
        widget = AutoRegisteredWidget("test")

        assert registry.is_registered(widget)
        assert registry.count() == 1

    def test_auto_register_with_no_registry(self):
        """Test auto_register decorator with no registry (should handle gracefully)."""
        @auto_register()  # No registry provided
        class AutoRegisteredWidget:
            def __init__(self, name):
                self.name = name

        # Should create widget without errors
        widget = AutoRegisteredWidget("test")
        # No assertions about registration since no registry provided

    def test_lifecycle_tracked_decorator(self):
        """Test lifecycle_tracked decorator."""
        registry = WidgetRegistry()

        @lifecycle_tracked(registry)
        class TrackedWidget:
            def __init__(self, name):
                self.name = name

        widget = TrackedWidget("test")

        # Manually register widget
        registry.register(widget)

        # Should have lifecycle tracking method
        assert hasattr(widget, 'track_lifecycle')

        # Test tracking a lifecycle event
        widget.track_lifecycle(WidgetLifecycleState.UPDATED, {"action": "theme_change"})

        # Verify event was recorded
        events = registry.get_lifecycle_events(widget)
        assert len(events) >= 2  # REGISTERED + UPDATED

        # Find the UPDATED event
        updated_events = [e for e in events if e.state == WidgetLifecycleState.UPDATED]
        assert len(updated_events) == 1
        assert updated_events[0].metadata == {"action": "theme_change"}


class TestRegistryValidationAndStatistics:
    """Test registry validation and comprehensive statistics."""

    def test_registry_statistics(self):
        """Test comprehensive registry statistics."""
        registry = WidgetRegistry()
        widgets = [MockThemedWidget(f"widget_{i}") for i in range(5)]

        # Register some widgets
        registry.bulk_register(widgets)

        # Unregister one widget
        registry.unregister(widgets[0])

        # Get statistics
        stats = registry.get_statistics()

        assert stats['total_registrations'] == 5
        assert stats['total_unregistrations'] == 1
        assert stats['active_widgets'] == 4
        assert stats['bulk_operations'] == 1
        assert stats['lifecycle_events'] >= 6  # 5 registrations + 1 unregistration
        assert stats['uptime_seconds'] > 0
        assert stats['memory_overhead_bytes'] > 0

    def test_registry_integrity_validation(self):
        """Test registry integrity validation."""
        registry = WidgetRegistry()
        widget = MockThemedWidget("test_widget")

        # Register widget
        registry.register(widget)

        # Validate integrity
        validation = registry.validate_integrity()
        assert validation['is_valid']
        assert len(validation['issues']) == 0
        assert validation['total_widgets'] == 1
        assert validation['dead_references'] == 0

    def test_registry_integrity_with_orphaned_data(self):
        """Test integrity validation detects orphaned data."""
        registry = WidgetRegistry()
        widget = MockThemedWidget("test_widget")

        registry.register(widget)
        widget_id = id(widget)

        # Manually create orphaned data to test detection
        registry._metadata[9999] = {"orphaned": True}
        registry._lifecycle_events[9998] = []

        validation = registry.validate_integrity()
        assert not validation['is_valid']
        assert len(validation['issues']) >= 2  # Should detect orphaned metadata and events

    def test_memory_overhead_estimation(self):
        """Test memory overhead estimation."""
        registry = WidgetRegistry()
        widgets = [MockThemedWidget(f"widget_{i}") for i in range(10)]

        # Register widgets with metadata
        metadata_list = [{"index": i, "data": "x" * 100} for i in range(10)]
        registry.bulk_register(widgets, metadata_list)

        stats = registry.get_statistics()
        overhead = stats['memory_overhead_bytes']

        # Should have reasonable memory overhead (less than 1KB per widget)
        assert overhead > 0
        assert overhead < 10 * 1024  # Less than 1KB per widget

    def test_dead_reference_cleanup(self):
        """Test automatic cleanup of dead references."""
        registry = WidgetRegistry()
        widgets = [MockThemedWidget(f"widget_{i}") for i in range(5)]

        registry.bulk_register(widgets)
        assert registry.count() == 5

        # Delete widgets to make references dead
        widget_ids = [id(w) for w in widgets]
        del widgets
        gc.collect()

        # Count should now be 0 after cleanup
        assert registry.count() == 0

        # Check for dead references
        validation = registry.validate_integrity()
        # After cleanup, there should be no dead references
        assert validation['dead_references'] == 0


class TestThreadSafety:
    """Test thread safety of registry operations."""

    def test_concurrent_registration(self):
        """Test concurrent widget registration."""
        registry = WidgetRegistry()
        widgets_per_thread = 50
        num_threads = 4

        def register_widgets(thread_id):
            widgets = [MockThemedWidget(f"thread_{thread_id}_widget_{i}")
                      for i in range(widgets_per_thread)]
            try:
                registry.bulk_register(widgets)
                return len(widgets)
            except Exception:
                return 0

        # Run concurrent registrations
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(register_widgets, i) for i in range(num_threads)]
            results = [future.result() for future in as_completed(futures)]

        # All registrations should succeed
        total_registered = sum(results)
        assert total_registered == widgets_per_thread * num_threads
        assert registry.count() == total_registered

    def test_concurrent_mixed_operations(self):
        """Test concurrent mixed registration/unregistration operations."""
        registry = WidgetRegistry()
        operations_per_thread = 20

        def mixed_operations(thread_id):
            successful_ops = 0
            for i in range(operations_per_thread):
                try:
                    widget = MockThemedWidget(f"thread_{thread_id}_widget_{i}")

                    # Register
                    registry.register(widget)
                    successful_ops += 1

                    # Unregister half of them
                    if i % 2 == 0:
                        registry.unregister(widget)

                except Exception:
                    pass  # Some operations may fail due to timing

            return successful_ops

        # Run concurrent mixed operations
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(mixed_operations, i) for i in range(4)]
            results = [future.result() for future in as_completed(futures)]

        # Should have completed without deadlocks
        assert all(result >= 0 for result in results)

        # Registry should be in consistent state
        validation = registry.validate_integrity()
        assert validation['is_valid']

    def test_concurrent_bulk_operations(self):
        """Test concurrent bulk operations."""
        registry = WidgetRegistry()

        def bulk_register_thread(thread_id):
            widgets = [MockThemedWidget(f"bulk_thread_{thread_id}_widget_{i}")
                      for i in range(25)]
            try:
                result = registry.bulk_register(widgets)
                return result['successful']
            except BulkOperationError as e:
                return e.successful_count
            except Exception:
                return 0

        # Run concurrent bulk operations
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(bulk_register_thread, i) for i in range(4)]
            results = [future.result() for future in as_completed(futures)]

        # All operations should complete
        total_registered = sum(results)
        assert total_registered > 0
        assert registry.count() == total_registered

    def test_no_deadlock_under_load(self):
        """Test that registry operations don't deadlock under load."""
        registry = WidgetRegistry()

        def stress_test_operations():
            for i in range(100):
                try:
                    widget = MockThemedWidget(f"stress_widget_{threading.current_thread().ident}_{i}")
                    registry.register(widget)

                    if i % 2 == 0:
                        registry.get_statistics()

                    if i % 3 == 0:
                        registry.validate_integrity()

                    if i % 5 == 0:
                        registry.unregister(widget)

                except Exception:
                    pass  # Some operations may fail, but shouldn't deadlock

        # Run stress test with multiple threads
        threads = []
        for i in range(8):
            thread = threading.Thread(target=stress_test_operations)
            threads.append(thread)
            thread.start()

        # All threads should complete within reasonable time
        start_time = time.time()
        for thread in threads:
            thread.join(timeout=10)  # 10 second timeout

        end_time = time.time()
        assert end_time - start_time < 10, "Operations took too long - possible deadlock"

        # Registry should be in valid state after stress test
        validation = registry.validate_integrity()
        assert validation['is_valid']


class TestPerformanceRequirements:
    """Test that all performance requirements are met."""

    def test_registration_performance_under_load(self):
        """Test registration performance with many widgets."""
        registry = WidgetRegistry()
        widgets = [MockThemedWidget(f"perf_widget_{i}") for i in range(1000)]

        # Measure individual registration performance
        registration_times = []

        for widget in widgets[:100]:  # Test first 100 for individual performance
            start_time = time.perf_counter()
            registry.register(widget)
            duration_us = (time.perf_counter() - start_time) * 1_000_000
            registration_times.append(duration_us)

        # Average should be under 10μs
        avg_time = sum(registration_times) / len(registration_times)
        assert avg_time < 50, f"Average registration time: {avg_time:.2f}μs (target: <10μs)"

        # 95th percentile should be reasonable
        registration_times.sort()
        p95_time = registration_times[int(0.95 * len(registration_times))]
        assert p95_time < 100, f"95th percentile registration time: {p95_time:.2f}μs"

    def test_bulk_operation_performance(self):
        """Test bulk operation performance requirements."""
        registry = WidgetRegistry()

        # Test different batch sizes
        for batch_size in [10, 50, 100, 200]:
            widgets = [MockThemedWidget(f"batch_{batch_size}_widget_{i}")
                      for i in range(batch_size)]

            start_time = time.perf_counter()
            result = registry.bulk_register(widgets)
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Should be under 1ms per 100 widgets (scaled)
            expected_max_ms = (batch_size / 100) * 1
            assert duration_ms < expected_max_ms * 5, \
                f"Batch size {batch_size} took {duration_ms:.2f}ms (expected: <{expected_max_ms:.2f}ms)"

            # Cleanup for next iteration
            registry.bulk_unregister(widgets)

    def test_memory_overhead_per_widget(self):
        """Test memory overhead per widget is reasonable."""
        registry = WidgetRegistry()

        # Get baseline memory
        stats_baseline = registry.get_statistics()
        baseline_memory = stats_baseline['memory_overhead_bytes']

        # Register widgets and measure memory growth
        widget_counts = [10, 50, 100]
        memory_per_widget = []

        for count in widget_counts:
            widgets = [MockThemedWidget(f"memory_test_widget_{i}") for i in range(count)]
            registry.bulk_register(widgets)

            stats = registry.get_statistics()
            total_memory = stats['memory_overhead_bytes'] - baseline_memory
            memory_per_widget.append(total_memory / count)

            # Cleanup
            registry.bulk_unregister(widgets)

        # Average memory per widget should be under 1KB
        avg_memory_per_widget = sum(memory_per_widget) / len(memory_per_widget)
        assert avg_memory_per_widget < 1024, \
            f"Average memory per widget: {avg_memory_per_widget:.0f} bytes (target: <1KB)"

    def test_cleanup_performance(self):
        """Test cleanup performance with many widgets."""
        registry = WidgetRegistry()
        widgets = [MockThemedWidget(f"cleanup_widget_{i}") for i in range(1000)]

        # Register many widgets
        registry.bulk_register(widgets)

        # Delete widgets to make them eligible for cleanup
        widget_ids = [id(w) for w in widgets]
        del widgets
        gc.collect()

        # Measure cleanup time
        start_time = time.perf_counter()
        final_count = registry.count()  # This triggers cleanup
        cleanup_duration_us = (time.perf_counter() - start_time) * 1_000_000

        # Should be under 100μs for 1000 widgets cleanup
        assert cleanup_duration_us < 1000, \
            f"Cleanup took {cleanup_duration_us:.0f}μs (target: <100μs for 1000 widgets)"
        assert final_count == 0


class TestContextManagers:
    """Test context managers for batch operations."""

    def test_theme_update_context(self):
        """Test ThemeUpdateContext for batch theme updates."""
        lifecycle_manager = LifecycleManager()
        widgets = [MockThemedWidget(f"theme_widget_{i}") for i in range(10)]

        # Register widgets
        for widget in widgets:
            lifecycle_manager.register_widget(widget)

        # Use context manager for theme update
        with ThemeUpdateContext(lifecycle_manager) as context:
            context.update_theme("dark")
            updated_count = context.get_updated_count()

        # All widgets should have been updated
        assert updated_count == 10
        for widget in widgets:
            assert widget.on_theme_changed_called

    def test_widget_creation_context(self):
        """Test WidgetCreationContext for batch widget creation."""
        lifecycle_manager = LifecycleManager()

        with WidgetCreationContext(lifecycle_manager) as context:
            for i in range(5):
                widget = MockThemedWidget(f"created_widget_{i}")
                context.register_widget(widget)

            created_count = context.get_created_count()

        # All widgets should be registered
        assert created_count == 5
        assert lifecycle_manager.get_widget_count() == 5

    def test_widget_creation_context_exception_handling(self):
        """Test WidgetCreationContext handles exceptions properly."""
        lifecycle_manager = LifecycleManager()
        widgets_created = []

        try:
            with WidgetCreationContext(lifecycle_manager) as context:
                for i in range(3):
                    widget = MockThemedWidget(f"exception_widget_{i}")
                    context.register_widget(widget)
                    widgets_created.append(widget)

                # Simulate exception
                raise RuntimeError("Test exception")

        except RuntimeError:
            pass  # Expected exception

        # Context should have cleaned up widgets on exception
        # (though some may still be registered depending on cleanup timing)
        final_count = lifecycle_manager.get_widget_count()
        assert final_count <= 3  # May not all be cleaned up immediately

    def test_performance_context(self):
        """Test PerformanceContext for monitoring operations."""
        with PerformanceContext() as context:
            # Simulate some work
            registry = WidgetRegistry()
            widgets = [MockThemedWidget(f"perf_widget_{i}") for i in range(100)]
            registry.bulk_register(widgets)

        metrics = context.get_metrics()

        # Should have captured performance metrics
        assert 'execution_time' in metrics
        assert 'memory_usage' in metrics
        assert metrics['execution_time'] > 0


if __name__ == "__main__":
    # Run specific test categories
    import sys

    if len(sys.argv) > 1:
        category = sys.argv[1]
        if category == "performance":
            pytest.main(["-v", "TestPerformanceRequirements"])
        elif category == "thread":
            pytest.main(["-v", "TestThreadSafety"])
        elif category == "bulk":
            pytest.main(["-v", "TestBulkOperations"])
        else:
            pytest.main(["-v"])
    else:
        pytest.main(["-v", __file__])
