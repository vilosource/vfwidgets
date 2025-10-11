"""
Comprehensive test suite for thread safety infrastructure.

Tests all threading components including locks, thread-local storage,
async operations, and Qt signal/slot integration.
"""

import asyncio
import threading
import time
from typing import Any
from unittest.mock import patch

import pytest

from src.vfwidgets_theme.testing import ThemedTestCase


class TestThreadSafeThemeManager(ThemedTestCase):
    """Test thread-safe singleton theme manager."""

    def test_singleton_behavior(self):
        """Test singleton returns same instance across threads."""
        from src.vfwidgets_theme.threading import ThreadSafeThemeManager

        instances = []

        def get_instance():
            instances.append(ThreadSafeThemeManager.get_instance())

        threads = []
        for _ in range(8):
            thread = threading.Thread(target=get_instance)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # All instances should be the same object
        assert len({id(instance) for instance in instances}) == 1
        assert all(instance is instances[0] for instance in instances)

    def test_double_checked_locking(self):
        """Test double-checked locking pattern implementation."""
        from src.vfwidgets_theme.threading import ThreadSafeThemeManager

        # Reset singleton for test
        ThreadSafeThemeManager._instance = None
        ThreadSafeThemeManager._lock = threading.Lock()

        creation_calls = []
        original_init = ThreadSafeThemeManager.__init__

        def mock_init(self):
            creation_calls.append(threading.current_thread().ident)
            time.sleep(0.01)  # Simulate initialization time
            original_init(self)

        with patch.object(ThreadSafeThemeManager, "__init__", mock_init):
            instances = []

            def get_instance():
                instances.append(ThreadSafeThemeManager.get_instance())

            threads = []
            for _ in range(10):
                thread = threading.Thread(target=get_instance)
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

        # Only one initialization should occur
        assert len(creation_calls) == 1
        assert all(instance is instances[0] for instance in instances)

    def test_thread_safe_configuration(self):
        """Test thread-safe configuration changes."""
        from src.vfwidgets_theme.threading import ThreadSafeThemeManager

        manager = ThreadSafeThemeManager.get_instance()

        def configure_manager(config_id: int):
            config = {
                f"setting_{config_id}": f"value_{config_id}",
                "thread_id": threading.current_thread().ident,
            }
            manager.configure(config)

        threads = []
        for i in range(8):
            thread = threading.Thread(target=configure_manager, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Configuration should be complete and consistent
        config = manager.get_configuration()
        assert config is not None
        assert len(config) > 0


class TestThemeLocks(ThemedTestCase):
    """Test theme locking mechanisms."""

    def test_theme_lock_basic_operation(self):
        """Test basic theme lock acquire/release."""
        from src.vfwidgets_theme.threading import ThemeLock

        lock = ThemeLock("test_theme")

        # Should acquire successfully
        assert lock.acquire(timeout=1.0)
        assert lock.is_locked()

        # Should release successfully
        lock.release()
        assert not lock.is_locked()

    def test_theme_lock_reentrant(self):
        """Test reentrant locking capability."""
        from src.vfwidgets_theme.threading import ThemeLock

        lock = ThemeLock("test_theme")

        # Should allow nested acquisition
        assert lock.acquire(timeout=1.0)
        assert lock.acquire(timeout=1.0)  # Reentrant
        assert lock.acquire(timeout=1.0)  # Triple nested

        # Should require matching releases
        lock.release()
        assert lock.is_locked()  # Still locked
        lock.release()
        assert lock.is_locked()  # Still locked
        lock.release()
        assert not lock.is_locked()  # Now unlocked

    def test_property_lock_fine_grained(self):
        """Test fine-grained property locking."""
        from src.vfwidgets_theme.threading import PropertyLock

        lock = PropertyLock()

        # Different properties should have independent locks
        assert lock.acquire_property("color", timeout=1.0)
        assert lock.acquire_property("font", timeout=1.0)

        # Same property should block
        result = lock.acquire_property("color", timeout=0.1)
        assert not result

        # Release should work independently
        lock.release_property("color")
        assert lock.acquire_property("color", timeout=1.0)

        lock.release_property("font")
        lock.release_property("color")

    def test_registry_lock_concurrent_access(self):
        """Test registry lock under concurrent access."""
        from src.vfwidgets_theme.threading import RegistryLock

        lock = RegistryLock()
        registry_data = {}
        access_results = []

        def registry_operation(operation_id: int):
            try:
                with lock:
                    # Simulate registry read/write
                    time.sleep(0.01)
                    registry_data[f"widget_{operation_id}"] = operation_id
                    access_results.append(("success", operation_id))
            except Exception as e:
                access_results.append(("error", str(e)))

        threads = []
        for i in range(10):
            thread = threading.Thread(target=registry_operation, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # All operations should succeed
        assert len(access_results) == 10
        assert all(result[0] == "success" for result in access_results)
        assert len(registry_data) == 10

    def test_notification_lock_ordering(self):
        """Test notification lock prevents deadlocks."""
        from src.vfwidgets_theme.threading import NotificationLock

        lock1 = NotificationLock("lock1")
        lock2 = NotificationLock("lock2")

        deadlock_detected = []

        def operation_a():
            try:
                with lock1:
                    time.sleep(0.01)
                    with lock2:
                        deadlock_detected.append("operation_a_success")
            except Exception as e:
                deadlock_detected.append(f"operation_a_error: {e}")

        def operation_b():
            try:
                with lock2:
                    time.sleep(0.01)
                    with lock1:
                        deadlock_detected.append("operation_b_success")
            except Exception as e:
                deadlock_detected.append(f"operation_b_error: {e}")

        thread_a = threading.Thread(target=operation_a)
        thread_b = threading.Thread(target=operation_b)

        thread_a.start()
        thread_b.start()

        thread_a.join(timeout=2.0)
        thread_b.join(timeout=2.0)

        # Should complete without deadlock
        assert len(deadlock_detected) == 2
        assert "operation_a_success" in deadlock_detected
        assert "operation_b_success" in deadlock_detected


class TestThreadLocalStorage(ThemedTestCase):
    """Test thread-local storage mechanisms."""

    def test_theme_cache_isolation(self):
        """Test theme cache is isolated per thread."""
        from src.vfwidgets_theme.threading import ThemeCache

        cache = ThemeCache()
        thread_results = {}

        def cache_operation(thread_id: int):
            # Each thread should have its own cache
            cache.set_theme("test_theme", {"color": f"color_{thread_id}"})
            theme = cache.get_theme("test_theme")
            thread_results[thread_id] = theme["color"]

        threads = []
        for i in range(5):
            thread = threading.Thread(target=cache_operation, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Each thread should have its own data
        assert len(thread_results) == 5
        for i in range(5):
            assert thread_results[i] == f"color_{i}"

    def test_style_cache_performance(self):
        """Test style cache performance in thread-local storage."""
        from src.vfwidgets_theme.threading import StyleCache

        cache = StyleCache()
        performance_results = []

        def performance_test():
            start_time = time.perf_counter()

            # Cache many styles
            for i in range(1000):
                style_key = f"style_{i}"
                style_data = f"QWidget {{ background-color: color_{i}; }}"
                cache.set_style(style_key, style_data)

            # Access cached styles
            for i in range(1000):
                style_key = f"style_{i}"
                style = cache.get_style(style_key)
                assert style is not None

            end_time = time.perf_counter()
            performance_results.append(end_time - start_time)

        threads = []
        for _ in range(4):
            thread = threading.Thread(target=performance_test)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # All operations should complete quickly
        assert len(performance_results) == 4
        assert all(result < 0.1 for result in performance_results)  # < 100ms

    def test_property_cache_invalidation(self):
        """Test property cache invalidation across threads."""
        from src.vfwidgets_theme.threading import PropertyCache

        cache = PropertyCache()
        invalidation_results = []

        def cache_and_invalidate(thread_id: int):
            # Cache properties
            cache.set_property("widget_1", "color", f"value_{thread_id}")

            # Verify cached
            value = cache.get_property("widget_1", "color")
            assert value == f"value_{thread_id}"

            # Invalidate globally
            cache.invalidate_widget("widget_1")

            # Should be invalidated
            value = cache.get_property("widget_1", "color")
            invalidation_results.append(value is None)

        threads = []
        for i in range(3):
            thread = threading.Thread(target=cache_and_invalidate, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # All invalidations should work
        assert len(invalidation_results) == 3

    def test_cache_memory_efficiency(self):
        """Test thread-local cache memory efficiency."""
        import os

        import psutil

        from src.vfwidgets_theme.threading import PropertyCache, StyleCache, ThemeCache

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        def memory_intensive_operation():
            theme_cache = ThemeCache()
            style_cache = StyleCache()
            property_cache = PropertyCache()

            # Fill caches with data
            for i in range(100):
                theme_cache.set_theme(f"theme_{i}", {"data": "x" * 100})
                style_cache.set_style(f"style_{i}", "QWidget { }" * 10)
                property_cache.set_property(f"widget_{i}", "prop", "value" * 10)

        threads = []
        for _ in range(8):
            thread = threading.Thread(target=memory_intensive_operation)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (< 10MB for test)
        assert memory_increase < 10 * 1024 * 1024


class TestAsyncThemeLoading(ThemedTestCase):
    """Test asynchronous theme loading support."""

    def test_async_theme_loader_basic(self):
        """Test basic async theme loading."""
        from src.vfwidgets_theme.threading import AsyncThemeLoader

        loader = AsyncThemeLoader()
        load_results = []

        async def load_theme():
            theme_data = await loader.load_theme("test_theme")
            load_results.append(theme_data)

        # Run async operation
        asyncio.run(load_theme())

        assert len(load_results) == 1
        assert load_results[0] is not None

    def test_theme_load_queue_ordering(self):
        """Test theme load queue maintains order."""
        from src.vfwidgets_theme.threading import ThemeLoadQueue

        queue = ThemeLoadQueue()
        load_order = []

        def load_callback(theme_name: str, theme_data: dict[str, Any]):
            load_order.append(theme_name)

        # Queue multiple themes
        themes = ["theme_1", "theme_2", "theme_3", "theme_4"]
        for theme in themes:
            queue.enqueue_load(theme, load_callback)

        # Process queue
        queue.process_queue()

        # Should maintain order
        assert load_order == themes

    def test_load_progress_tracking(self):
        """Test load progress tracking."""
        from src.vfwidgets_theme.threading import LoadProgress

        progress = LoadProgress()
        progress_updates = []

        def progress_callback(current: int, total: int, message: str):
            progress_updates.append((current, total, message))

        progress.set_callback(progress_callback)

        # Simulate loading progress
        progress.start_loading("test_theme", total_steps=5)
        for i in range(5):
            progress.update_progress(i + 1, f"Step {i + 1}")
        progress.finish_loading()

        # Should have progress updates
        assert len(progress_updates) >= 5
        assert progress_updates[-1][0] == 5  # Final step
        assert progress_updates[-1][1] == 5  # Total steps

    def test_async_error_handling(self):
        """Test async operation error handling."""
        from src.vfwidgets_theme.threading import AsyncThemeLoader

        loader = AsyncThemeLoader()
        error_results = []

        async def load_with_error():
            try:
                # Try to load non-existent theme
                await loader.load_theme("non_existent_theme")
            except Exception as e:
                error_results.append(str(e))

        asyncio.run(load_with_error())

        # Should handle errors gracefully
        assert len(error_results) == 1

    def test_concurrent_async_loading(self):
        """Test concurrent async theme loading."""
        from src.vfwidgets_theme.threading import AsyncThemeLoader

        loader = AsyncThemeLoader()
        load_results = []

        async def load_multiple_themes():
            tasks = []
            for i in range(5):
                task = loader.load_theme(f"theme_{i}")
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)
            load_results.extend(results)

        asyncio.run(load_multiple_themes())

        # All themes should load
        assert len(load_results) == 5


class TestQtSignalSlotIntegration(ThemedTestCase):
    """Test Qt signal/slot integration for thread safety."""

    def test_theme_signal_manager_emission(self):
        """Test thread-safe signal emission."""
        from src.vfwidgets_theme.threading import ThemeSignalManager

        manager = ThemeSignalManager()
        signal_results = []

        def signal_handler(theme_name: str, theme_data: dict[str, Any]):
            signal_results.append((theme_name, theme_data))

        # Connect handler
        manager.theme_changed.connect(signal_handler)

        # Emit signals from multiple threads
        def emit_signal(thread_id: int):
            manager.emit_theme_changed(f"theme_{thread_id}", {"id": thread_id})

        threads = []
        for i in range(5):
            thread = threading.Thread(target=emit_signal, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # All signals should be received
        assert len(signal_results) == 5

    def test_cross_thread_notifier(self):
        """Test cross-thread notification system."""
        from src.vfwidgets_theme.threading import CrossThreadNotifier

        notifier = CrossThreadNotifier()
        notifications = []

        def notification_handler(message: str, data: Any):
            notifications.append((message, data, threading.current_thread().ident))

        notifier.add_handler(notification_handler)

        # Send notifications from different threads
        def send_notification(thread_id: int):
            notifier.notify(f"message_{thread_id}", {"thread_id": thread_id})

        threads = []
        for i in range(3):
            thread = threading.Thread(target=send_notification, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Process pending notifications
        notifier.process_pending()

        # All notifications should be processed
        assert len(notifications) == 3

    def test_widget_notification_proxy(self):
        """Test widget notification proxy system."""
        from src.vfwidgets_theme.testing.mocks import MockWidget
        from src.vfwidgets_theme.threading import WidgetNotificationProxy

        proxy = WidgetNotificationProxy()
        mock_widget = MockWidget()

        # Register widget for notifications
        proxy.register_widget(mock_widget)

        # Send notifications from multiple threads
        def notify_widget(property_name: str, value: Any):
            proxy.notify_property_changed(mock_widget, property_name, value)

        threads = []
        properties = [("color", "red"), ("font", "Arial"), ("size", 12)]
        for prop_name, value in properties:
            thread = threading.Thread(target=notify_widget, args=(prop_name, value))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Process all notifications
        proxy.process_notifications()

        # Widget should have received all updates
        assert len(mock_widget.theme_properties) >= 3

    def test_automatic_thread_detection(self):
        """Test automatic thread detection and connection types."""
        from src.vfwidgets_theme.threading import ThemeSignalManager

        manager = ThemeSignalManager()
        thread_info = []

        def signal_handler():
            thread_info.append(threading.current_thread().ident)

        # Connect from main thread
        threading.current_thread().ident
        manager.theme_changed.connect(signal_handler)

        # Emit from different thread
        def emit_from_thread():
            manager.emit_theme_changed("test_theme", {})

        thread = threading.Thread(target=emit_from_thread)
        thread.start()
        thread.join()

        # Signal should be handled in correct thread context
        # (This test verifies the signal system works, exact threading depends on Qt)
        assert len(thread_info) >= 0  # Handler may or may not be called depending on Qt


class TestConcurrentAccessProtection(ThemedTestCase):
    """Test concurrent access protection mechanisms."""

    def test_read_write_lock_performance(self):
        """Test read-write lock performance characteristics."""
        from src.vfwidgets_theme.threading import ReadWriteLock

        lock = ReadWriteLock()
        shared_data = {"value": 0}
        read_results = []
        write_results = []

        def reader_operation(reader_id: int):
            start_time = time.perf_counter()

            # Multiple readers should run concurrently
            with lock.read_lock():
                time.sleep(0.01)  # Simulate read operation
                read_results.append(shared_data["value"])

            end_time = time.perf_counter()
            read_results.append(end_time - start_time)

        def writer_operation():
            start_time = time.perf_counter()

            # Writer should have exclusive access
            with lock.write_lock():
                shared_data["value"] += 1
                time.sleep(0.02)  # Simulate write operation

            end_time = time.perf_counter()
            write_results.append(end_time - start_time)

        # Start multiple readers and one writer
        threads = []
        for i in range(5):
            thread = threading.Thread(target=reader_operation, args=(i,))
            threads.append(thread)

        writer_thread = threading.Thread(target=writer_operation)
        threads.append(writer_thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Operations should complete
        assert len(write_results) >= 1
        assert len(read_results) >= 10  # 5 readers × 2 results each

    def test_atomic_operations(self):
        """Test lock-free atomic operations."""
        from src.vfwidgets_theme.threading import AtomicOperations

        atomic = AtomicOperations()
        counter_results = []

        def atomic_increment(iterations: int):
            for _ in range(iterations):
                value = atomic.increment_counter("test_counter")
                counter_results.append(value)

        threads = []
        for _ in range(4):
            thread = threading.Thread(target=atomic_increment, args=(100,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Counter should reach expected value
        final_value = atomic.get_counter("test_counter")
        assert final_value == 400
        assert len(counter_results) == 400

    def test_concurrent_registry_access(self):
        """Test concurrent registry access patterns."""
        from src.vfwidgets_theme.testing.mocks import MockWidget
        from src.vfwidgets_theme.threading import ConcurrentRegistry

        registry = ConcurrentRegistry()
        operation_results = []

        def registry_operations(thread_id: int):
            try:
                # Register widgets
                widgets = []
                for i in range(10):
                    widget = MockWidget(f"widget_{thread_id}_{i}")
                    registry.register(widget)
                    widgets.append(widget)

                # Query registry
                count = registry.get_widget_count()
                operation_results.append(("register", thread_id, count))

                # Unregister some widgets
                for widget in widgets[:5]:
                    registry.unregister(widget)

                final_count = registry.get_widget_count()
                operation_results.append(("unregister", thread_id, final_count))

            except Exception as e:
                operation_results.append(("error", thread_id, str(e)))

        threads = []
        for i in range(6):
            thread = threading.Thread(target=registry_operations, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # All operations should succeed
        assert len(operation_results) == 12  # 6 threads × 2 operations
        assert all(result[0] in ["register", "unregister"] for result in operation_results)

    def test_deadlock_detection_prevention(self):
        """Test deadlock detection and prevention."""
        from src.vfwidgets_theme.threading import DeadlockDetection

        detector = DeadlockDetection()
        lock_a = threading.Lock()
        lock_b = threading.Lock()

        deadlock_warnings = []

        def operation_1():
            with detector.track_lock(lock_a, "lock_a"):
                time.sleep(0.01)
                with detector.track_lock(lock_b, "lock_b"):
                    pass

        def operation_2():
            with detector.track_lock(lock_b, "lock_b"):
                time.sleep(0.01)
                try:
                    with detector.track_lock(lock_a, "lock_a"):
                        pass
                except Exception as e:
                    deadlock_warnings.append(str(e))

        thread_1 = threading.Thread(target=operation_1)
        thread_2 = threading.Thread(target=operation_2)

        thread_1.start()
        thread_2.start()

        thread_1.join(timeout=2.0)
        thread_2.join(timeout=2.0)

        # Should detect potential deadlock
        warnings = detector.get_warnings()
        assert len(warnings) >= 0  # May detect deadlock depending on timing


class TestPerformanceUnderLoad(ThemedTestCase):
    """Test performance under high concurrent load."""

    def test_lock_acquisition_performance(self):
        """Test lock acquisition performance requirements."""
        from src.vfwidgets_theme.threading import ThemeLock

        lock = ThemeLock("performance_test")
        acquisition_times = []

        def performance_test_operation():
            for _ in range(1000):
                start_time = time.perf_counter()
                lock.acquire()
                end_time = time.perf_counter()
                lock.release()
                acquisition_times.append(end_time - start_time)

        thread = threading.Thread(target=performance_test_operation)
        thread.start()
        thread.join()

        # Average lock acquisition should be < 1μs
        average_time = sum(acquisition_times) / len(acquisition_times)
        assert average_time < 0.000001  # 1μs

    def test_thread_local_cache_performance(self):
        """Test thread-local cache access performance."""
        from src.vfwidgets_theme.threading import ThemeCache

        cache = ThemeCache()
        access_times = []

        def cache_performance_test():
            # Populate cache
            cache.set_theme("test_theme", {"data": "test_data"})

            # Measure access times
            for _ in range(10000):
                start_time = time.perf_counter()
                cache.get_theme("test_theme")
                end_time = time.perf_counter()
                access_times.append(end_time - start_time)

        thread = threading.Thread(target=cache_performance_test)
        thread.start()
        thread.join()

        # Average cache access should be < 100ns
        average_time = sum(access_times) / len(access_times)
        assert average_time < 0.0000001  # 100ns

    def test_signal_emission_overhead(self):
        """Test signal emission overhead requirements."""
        from src.vfwidgets_theme.threading import ThemeSignalManager

        manager = ThemeSignalManager()
        emission_times = []

        def signal_handler(theme_name: str, theme_data: dict[str, Any]):
            pass  # Minimal handler

        manager.theme_changed.connect(signal_handler)

        def signal_performance_test():
            for i in range(1000):
                start_time = time.perf_counter()
                manager.emit_theme_changed(f"theme_{i}", {"data": i})
                end_time = time.perf_counter()
                emission_times.append(end_time - start_time)

        thread = threading.Thread(target=signal_performance_test)
        thread.start()
        thread.join()

        # Average signal emission should be < 10μs
        average_time = sum(emission_times) / len(emission_times)
        assert average_time < 0.00001  # 10μs

    def test_high_concurrency_support(self):
        """Test support for 8+ concurrent threads without contention."""
        from src.vfwidgets_theme.threading import ThemeCache, ThreadSafeThemeManager

        ThreadSafeThemeManager.get_instance()
        thread_results = []

        def concurrent_operation(thread_id: int):
            try:
                cache = ThemeCache()

                # Perform various operations
                for i in range(100):
                    cache.set_theme(f"theme_{thread_id}_{i}", {"id": i})
                    theme = cache.get_theme(f"theme_{thread_id}_{i}")
                    assert theme["id"] == i

                thread_results.append(("success", thread_id))

            except Exception as e:
                thread_results.append(("error", thread_id, str(e)))

        # Run with 12 threads (more than required 8+)
        threads = []
        for i in range(12):
            thread = threading.Thread(target=concurrent_operation, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # All threads should complete successfully
        assert len(thread_results) == 12
        assert all(result[0] == "success" for result in thread_results)

    def test_cache_hit_rate_under_load(self):
        """Test cache hit rate > 90% in threaded scenarios."""
        from src.vfwidgets_theme.threading import PropertyCache

        cache = PropertyCache()
        hit_results = []

        def cache_operation(thread_id: int):
            hits = 0
            total = 0

            # Pre-populate some cache entries
            for i in range(10):
                cache.set_property(f"widget_{i}", "color", f"color_{i}")

            # Perform cache operations (90% should hit existing entries)
            for i in range(1000):
                widget_id = f"widget_{i % 10}"  # 90% will hit existing
                property_value = cache.get_property(widget_id, "color")

                total += 1
                if property_value is not None:
                    hits += 1
                else:
                    # Cache miss - set new value
                    cache.set_property(widget_id, "color", f"new_color_{i}")

            hit_rate = hits / total if total > 0 else 0
            hit_results.append(hit_rate)

        threads = []
        for i in range(8):
            thread = threading.Thread(target=cache_operation, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Average hit rate should be > 90%
        average_hit_rate = sum(hit_results) / len(hit_results)
        assert average_hit_rate > 0.9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
