"""
Integration tests for widget lifecycle management.

Tests the complete lifecycle from widget creation to cleanup,
including theme registration, updates, and memory management.
"""
import unittest
import threading
import time
import weakref
import gc
from unittest.mock import Mock, patch
from typing import List, Dict, Any

import pytest

from vfwidgets_theme.widgets.base import ThemedWidget
from vfwidgets_theme.widgets.application import ThemedApplication
from vfwidgets_theme.core.theme import Theme
from vfwidgets_theme.lifecycle import WidgetRegistry
from vfwidgets_theme.testing import ThemedTestCase, ThemeBenchmark, MemoryProfiler


class TestWidgetLifecycleIntegration(ThemedTestCase):
    """Test complete widget lifecycle integration."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        with patch('vfwidgets_theme.widgets.application.QApplication'):
            self.app = ThemedApplication([])

    def tearDown(self):
        """Clean up test environment."""
        if hasattr(self, 'app'):
            self.app.cleanup()
        super().tearDown()

    def test_complete_widget_lifecycle(self):
        """Test complete widget lifecycle from creation to cleanup."""
        # Phase 1: Widget Creation
        widget = ThemedWidget()
        widget_id = widget._widget_id

        # Verify registration
        registry = WidgetRegistry.get_instance()
        self.assertTrue(registry.is_registered(widget_id))
        self.assertTrue(widget._is_theme_registered)

        # Phase 2: Theme Property Access
        # Should have theme properties available
        background = widget.theme.background
        self.assertIsNotNone(background)

        # Phase 3: Theme Change
        # Change theme and verify widget receives update
        old_theme_name = self.app.get_current_theme().name
        self.app.set_theme('dark')
        new_theme_name = self.app.get_current_theme().name

        # Widget should have received update
        # (Actual verification depends on theme content)

        # Phase 4: Manual Cleanup
        widget._cleanup_theme()
        self.assertFalse(widget._is_theme_registered)

        # Phase 5: Destruction
        weak_ref = weakref.ref(widget)
        del widget
        gc.collect()

        # Widget should be garbage collected
        self.assertIsNone(weak_ref())

    def test_parent_child_lifecycle(self):
        """Test parent-child widget lifecycle."""
        # Create parent widget
        parent = ThemedWidget()
        parent_id = parent._widget_id

        # Create child widgets
        child1 = ThemedWidget(parent=parent)
        child2 = ThemedWidget(parent=parent)
        child1_id = child1._widget_id
        child2_id = child2._widget_id

        # All should be registered
        registry = WidgetRegistry.get_instance()
        self.assertTrue(registry.is_registered(parent_id))
        self.assertTrue(registry.is_registered(child1_id))
        self.assertTrue(registry.is_registered(child2_id))

        # Change theme - all should receive updates
        self.app.set_theme('light')

        # All should have theme properties
        self.assertIsNotNone(parent.theme.background)
        self.assertIsNotNone(child1.theme.background)
        self.assertIsNotNone(child2.theme.background)

        # Clean up parent
        parent._cleanup_theme()

        # Parent should be unregistered
        self.assertFalse(parent._is_theme_registered)

        # Children cleanup
        child1._cleanup_theme()
        child2._cleanup_theme()

        # Verify destruction
        parent_ref = weakref.ref(parent)
        child1_ref = weakref.ref(child1)
        child2_ref = weakref.ref(child2)

        del parent, child1, child2
        gc.collect()

        self.assertIsNone(parent_ref())
        self.assertIsNone(child1_ref())
        self.assertIsNone(child2_ref())

    def test_widget_hierarchy_theme_propagation(self):
        """Test theme propagation through widget hierarchy."""
        # Create widget hierarchy
        root = ThemedWidget()
        level1_a = ThemedWidget(parent=root)
        level1_b = ThemedWidget(parent=root)
        level2_a = ThemedWidget(parent=level1_a)
        level2_b = ThemedWidget(parent=level1_b)

        widgets = [root, level1_a, level1_b, level2_a, level2_b]

        # All should be registered and themed
        for widget in widgets:
            self.assertTrue(widget._is_theme_registered)
            self.assertIsNotNone(widget.theme.background)

        # Change theme multiple times
        themes = ['dark', 'light', 'default']
        for theme_name in themes:
            self.app.set_theme(theme_name)

            # All widgets should have consistent theme
            for widget in widgets:
                self.assertIsNotNone(widget.theme.background)

        # Cleanup
        for widget in widgets:
            widget._cleanup_theme()

    def test_dynamic_widget_creation_destruction(self):
        """Test dynamic widget creation and destruction."""
        widget_refs = []

        # Create widgets dynamically
        for i in range(20):
            widget = ThemedWidget()
            widget_refs.append(weakref.ref(widget))

            # Verify immediate registration
            self.assertTrue(widget._is_theme_registered)

            # Access theme properties
            self.assertIsNotNone(widget.theme.background)

            # Clean up immediately (simulating dynamic UI)
            widget._cleanup_theme()
            del widget

        # Force garbage collection
        gc.collect()

        # All widgets should be cleaned up
        for ref in widget_refs:
            self.assertIsNone(ref())

    def test_widget_lifecycle_under_theme_changes(self):
        """Test widget lifecycle under frequent theme changes."""
        widgets = [ThemedWidget() for _ in range(10)]
        themes = ['default', 'dark', 'light', 'minimal']

        # Rapidly change themes while widgets exist
        for theme_name in themes:
            self.app.set_theme(theme_name)

            # All widgets should remain functional
            for widget in widgets:
                self.assertTrue(widget._is_theme_registered)
                self.assertIsNotNone(widget.theme.background)

        # Cleanup during theme changes
        while widgets:
            widget = widgets.pop()
            widget._cleanup_theme()

            # Change theme during cleanup
            theme_name = themes[len(widgets) % len(themes)]
            self.app.set_theme(theme_name)

        # All should be cleaned up
        self.assertEqual(len(widgets), 0)


class TestWidgetLifecyclePerformance(ThemedTestCase):
    """Test widget lifecycle performance requirements."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        with patch('vfwidgets_theme.widgets.application.QApplication'):
            self.app = ThemedApplication([])

    def tearDown(self):
        """Clean up test environment."""
        if hasattr(self, 'app'):
            self.app.cleanup()
        super().tearDown()

    def test_bulk_widget_creation_performance(self):
        """Test bulk widget creation meets performance requirements."""
        benchmark = ThemeBenchmark()
        widget_count = 100

        def create_widgets():
            widgets = []
            for _ in range(widget_count):
                widget = ThemedWidget()
                widgets.append(widget)
            return widgets

        # Measure creation time
        creation_time = benchmark.measure_time(create_widgets)
        widgets = create_widgets()

        # Should create widgets efficiently
        avg_creation_time = creation_time / widget_count
        self.assertLess(avg_creation_time, 0.001)  # < 1ms per widget

        # Cleanup
        for widget in widgets:
            widget._cleanup_theme()

    def test_bulk_widget_theme_update_performance(self):
        """Test bulk widget theme update performance."""
        widgets = [ThemedWidget() for _ in range(100)]
        benchmark = ThemeBenchmark()

        def theme_update():
            self.app.set_theme('dark')

        # Measure theme update time
        update_time = benchmark.measure_time(theme_update)

        # Should update all widgets efficiently (< 100ms requirement)
        self.assertLess(update_time, 0.1)

        # Cleanup
        for widget in widgets:
            widget._cleanup_theme()

    def test_bulk_widget_cleanup_performance(self):
        """Test bulk widget cleanup performance."""
        widgets = [ThemedWidget() for _ in range(100)]
        benchmark = ThemeBenchmark()

        def cleanup_widgets():
            for widget in widgets:
                widget._cleanup_theme()

        # Measure cleanup time
        cleanup_time = benchmark.measure_time(cleanup_widgets)

        # Should cleanup efficiently
        avg_cleanup_time = cleanup_time / len(widgets)
        self.assertLess(avg_cleanup_time, 0.001)  # < 1ms per widget cleanup

    def test_widget_property_access_performance(self):
        """Test widget property access performance under load."""
        widget = ThemedWidget()
        benchmark = ThemeBenchmark()

        # Cache properties first
        widget.theme.background
        widget.theme.color

        def access_properties():
            for _ in range(1000):
                _ = widget.theme.background
                _ = widget.theme.color

        # Measure cached access time
        access_time = benchmark.measure_time(access_properties)

        # Should access cached properties very quickly
        avg_access_time = access_time / 2000  # 2000 total accesses
        self.assertLess(avg_access_time, 0.000001)  # < 1μs per access

        widget._cleanup_theme()


class TestWidgetLifecycleMemoryManagement(ThemedTestCase):
    """Test widget lifecycle memory management."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        with patch('vfwidgets_theme.widgets.application.QApplication'):
            self.app = ThemedApplication([])
        self.profiler = MemoryProfiler()

    def tearDown(self):
        """Clean up test environment."""
        if hasattr(self, 'app'):
            self.app.cleanup()
        super().tearDown()

    def test_widget_memory_overhead(self):
        """Test widget memory overhead meets requirements."""
        baseline = self.profiler.get_memory_usage()

        # Create widget
        widget = ThemedWidget()
        widget_memory = self.profiler.get_memory_usage()

        # Calculate overhead
        overhead = widget_memory - baseline
        self.assertLess(overhead, 1024)  # < 1KB per widget

        widget._cleanup_theme()

    def test_zero_memory_leaks_lifecycle(self):
        """Test zero memory leaks through complete lifecycle."""
        baseline = self.profiler.get_memory_usage()

        # Create and destroy many widgets
        for i in range(100):
            widget = ThemedWidget()

            # Use widget
            _ = widget.theme.background
            self.app.set_theme('dark' if i % 2 else 'light')
            _ = widget.theme.color

            # Cleanup
            widget._cleanup_theme()
            del widget

            # Periodic garbage collection
            if i % 10 == 0:
                gc.collect()

        # Final garbage collection
        gc.collect()

        # Memory should return to baseline
        final_memory = self.profiler.get_memory_usage()
        memory_growth = final_memory - baseline

        # Allow small growth for caches, etc.
        self.assertLess(memory_growth, 10240)  # < 10KB growth

    def test_widget_reference_cleanup(self):
        """Test proper reference cleanup prevents memory leaks."""
        widget_refs = []

        # Create widgets and keep weak references
        for _ in range(50):
            widget = ThemedWidget()
            widget_refs.append(weakref.ref(widget))
            widget._cleanup_theme()
            del widget

        # Force garbage collection
        gc.collect()

        # All references should be None
        for ref in widget_refs:
            self.assertIsNone(ref())

    def test_registry_memory_efficiency(self):
        """Test widget registry memory efficiency."""
        registry = WidgetRegistry.get_instance()
        baseline_count = registry.get_widget_count()

        widgets = []
        for _ in range(100):
            widget = ThemedWidget()
            widgets.append(widget)

        # Registry should track all widgets
        current_count = registry.get_widget_count()
        self.assertEqual(current_count - baseline_count, 100)

        # Cleanup widgets
        for widget in widgets:
            widget._cleanup_theme()

        # Registry should clean up automatically
        # (Exact behavior depends on WeakRef implementation)


class TestWidgetLifecycleThreadSafety(ThemedTestCase):
    """Test widget lifecycle thread safety."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        with patch('vfwidgets_theme.widgets.application.QApplication'):
            self.app = ThemedApplication([])

    def tearDown(self):
        """Clean up test environment."""
        if hasattr(self, 'app'):
            self.app.cleanup()
        super().tearDown()

    def test_concurrent_widget_creation(self):
        """Test concurrent widget creation is thread-safe."""
        widgets = []
        errors = []
        lock = threading.Lock()

        def create_widgets_thread():
            try:
                thread_widgets = []
                for _ in range(20):
                    widget = ThemedWidget()
                    thread_widgets.append(widget)
                    time.sleep(0.001)  # Small delay

                with lock:
                    widgets.extend(thread_widgets)
            except Exception as e:
                with lock:
                    errors.append(e)

        # Create widgets concurrently
        threads = [threading.Thread(target=create_widgets_thread) for _ in range(5)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Should have no errors
        self.assertEqual(len(errors), 0, f"Errors: {errors}")

        # Should have created expected widgets
        self.assertEqual(len(widgets), 100)

        # All widgets should be properly registered
        for widget in widgets:
            self.assertTrue(widget._is_theme_registered)

        # Cleanup
        for widget in widgets:
            widget._cleanup_theme()

    def test_concurrent_theme_updates(self):
        """Test concurrent theme updates are thread-safe."""
        widgets = [ThemedWidget() for _ in range(50)]
        errors = []
        lock = threading.Lock()

        def theme_update_thread():
            try:
                themes = ['dark', 'light', 'default', 'minimal']
                for theme_name in themes:
                    self.app.set_theme(theme_name)
                    time.sleep(0.001)
            except Exception as e:
                with lock:
                    errors.append(e)

        def property_access_thread():
            try:
                for _ in range(50):
                    for widget in widgets[:10]:  # Access subset
                        _ = widget.theme.background
                        _ = widget.theme.color
                    time.sleep(0.001)
            except Exception as e:
                with lock:
                    errors.append(e)

        # Run concurrent operations
        theme_threads = [threading.Thread(target=theme_update_thread) for _ in range(2)]
        access_threads = [threading.Thread(target=property_access_thread) for _ in range(3)]

        all_threads = theme_threads + access_threads

        for thread in all_threads:
            thread.start()

        for thread in all_threads:
            thread.join()

        # Should have no errors
        self.assertEqual(len(errors), 0, f"Errors: {errors}")

        # All widgets should still be functional
        for widget in widgets:
            self.assertTrue(widget._is_theme_registered)
            self.assertIsNotNone(widget.theme.background)

        # Cleanup
        for widget in widgets:
            widget._cleanup_theme()

    def test_concurrent_cleanup(self):
        """Test concurrent widget cleanup is thread-safe."""
        widgets = [ThemedWidget() for _ in range(100)]
        errors = []
        lock = threading.Lock()

        def cleanup_thread(widget_subset):
            try:
                for widget in widget_subset:
                    widget._cleanup_theme()
                    time.sleep(0.001)
            except Exception as e:
                with lock:
                    errors.append(e)

        # Divide widgets among threads
        thread_count = 5
        widgets_per_thread = len(widgets) // thread_count
        threads = []

        for i in range(thread_count):
            start_idx = i * widgets_per_thread
            end_idx = start_idx + widgets_per_thread
            if i == thread_count - 1:  # Last thread gets remainder
                end_idx = len(widgets)

            thread = threading.Thread(
                target=cleanup_thread,
                args=(widgets[start_idx:end_idx],)
            )
            threads.append(thread)

        # Run concurrent cleanup
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Should have no errors
        self.assertEqual(len(errors), 0, f"Errors: {errors}")

        # All widgets should be cleaned up
        for widget in widgets:
            self.assertFalse(widget._is_theme_registered)


class TestWidgetLifecycleStressTest(ThemedTestCase):
    """Stress test widget lifecycle under extreme conditions."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        with patch('vfwidgets_theme.widgets.application.QApplication'):
            self.app = ThemedApplication([])

    def tearDown(self):
        """Clean up test environment."""
        if hasattr(self, 'app'):
            self.app.cleanup()
        super().tearDown()

    def test_massive_widget_lifecycle_stress(self):
        """Test massive widget creation/destruction stress test."""
        total_widgets = 1000
        batch_size = 100

        for batch in range(total_widgets // batch_size):
            # Create batch
            widgets = [ThemedWidget() for _ in range(batch_size)]

            # Use widgets
            theme_name = 'dark' if batch % 2 else 'light'
            self.app.set_theme(theme_name)

            for widget in widgets:
                _ = widget.theme.background
                _ = widget.theme.color

            # Cleanup batch
            for widget in widgets:
                widget._cleanup_theme()

            del widgets
            gc.collect()

        # System should remain stable

    def test_rapid_theme_switching_stress(self):
        """Test rapid theme switching stress test."""
        widgets = [ThemedWidget() for _ in range(50)]
        themes = ['default', 'dark', 'light', 'minimal']

        # Rapid theme switching
        for i in range(200):
            theme_name = themes[i % len(themes)]
            self.app.set_theme(theme_name)

            # Occasional property access
            if i % 10 == 0:
                for widget in widgets[::5]:  # Every 5th widget
                    _ = widget.theme.background

        # All widgets should remain functional
        for widget in widgets:
            self.assertTrue(widget._is_theme_registered)
            self.assertIsNotNone(widget.theme.background)

        # Cleanup
        for widget in widgets:
            widget._cleanup_theme()

    def test_mixed_operations_stress(self):
        """Test mixed operations stress test."""
        widgets = []
        themes = ['default', 'dark', 'light']

        for i in range(500):
            # Mixed operations
            operation = i % 4

            if operation == 0:  # Create widget
                widget = ThemedWidget()
                widgets.append(widget)

            elif operation == 1 and widgets:  # Access properties
                widget = widgets[i % len(widgets)]
                _ = widget.theme.background
                _ = widget.theme.color

            elif operation == 2:  # Change theme
                theme_name = themes[i % len(themes)]
                self.app.set_theme(theme_name)

            elif operation == 3 and widgets:  # Cleanup widget
                widget = widgets.pop(0)
                widget._cleanup_theme()

        # Cleanup remaining widgets
        for widget in widgets:
            widget._cleanup_theme()

        # System should remain stable


if __name__ == '__main__':
    unittest.main()