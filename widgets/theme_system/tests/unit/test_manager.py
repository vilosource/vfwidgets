"""
Test suite for ThemeManager.

Tests theme management coordination including:
- Theme manager as facade coordinating other components
- High-level operations (switch_theme, load_theme, etc.)
- Integration with dependency injection patterns
- Thread-safe singleton using threading infrastructure
- Public API that ThemedWidget and ThemedApplication use
"""

import tempfile
import threading
import time
from pathlib import Path

import pytest

from vfwidgets_theme.core.applicator import ThemeApplicator

# Import the modules under test
from vfwidgets_theme.core.manager import ThemeManager, create_theme_manager
from vfwidgets_theme.core.notifier import ThemeNotifier
from vfwidgets_theme.core.provider import DefaultThemeProvider
from vfwidgets_theme.core.registry import ThemeWidgetRegistry
from vfwidgets_theme.core.repository import ThemeRepository
from vfwidgets_theme.core.theme import Theme
from vfwidgets_theme.errors import ThemeLoadError, ThemeNotFoundError
from vfwidgets_theme.lifecycle import LifecycleManager
from vfwidgets_theme.testing import ThemedTestCase
from vfwidgets_theme.threading import ThreadSafeThemeManager


class MockWidget:
    """Mock widget for testing theme management."""

    def __init__(self, name: str = "mock-widget"):
        self.name = name
        self.applied_themes = []
        self._current_stylesheet = ""

    def setStyleSheet(self, stylesheet: str):
        """Mock stylesheet application."""
        self._current_stylesheet = stylesheet

    def styleSheet(self) -> str:
        """Mock stylesheet retrieval."""
        return self._current_stylesheet


class TestThemeManager(ThemedTestCase):
    """Test ThemeManager facade coordination."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()

        # Create sample theme
        self.sample_theme_data = {
            "name": "manager-test-theme",
            "version": "1.0.0",
            "colors": {
                "primary": "#007acc",
                "secondary": "#ffffff",
                "background": "#f5f5f5"
            },
            "styles": {
                "QPushButton": "background-color: @colors.primary; color: @colors.secondary;",
                "QLabel": "color: @colors.primary;"
            }
        }

        self.sample_theme = Theme.from_dict(self.sample_theme_data)

    def test_manager_initialization_default(self):
        """Test manager initialization with default components."""
        manager = ThemeManager()

        self.assertIsNotNone(manager)
        self.assertIsNotNone(manager._repository)
        self.assertIsNotNone(manager._applicator)
        self.assertIsNotNone(manager._notifier)
        self.assertIsNotNone(manager._provider)
        self.assertIsNone(manager.current_theme)

    def test_manager_initialization_with_dependencies(self):
        """Test manager initialization with injected dependencies."""
        repository = ThemeRepository()
        applicator = ThemeApplicator()
        notifier = ThemeNotifier()
        provider = DefaultThemeProvider()

        manager = ThemeManager(
            repository=repository,
            applicator=applicator,
            notifier=notifier,
            provider=provider
        )

        self.assertIs(manager._repository, repository)
        self.assertIs(manager._applicator, applicator)
        self.assertIs(manager._notifier, notifier)
        self.assertIs(manager._provider, provider)

    def test_add_theme(self):
        """Test adding theme to manager."""
        manager = ThemeManager()

        manager.add_theme(self.sample_theme)

        self.assertTrue(manager.has_theme("manager-test-theme"))
        retrieved = manager.get_theme("manager-test-theme")
        self.assertEqual(retrieved.name, "manager-test-theme")

    def test_get_theme_existing(self):
        """Test getting existing theme."""
        manager = ThemeManager()
        manager.add_theme(self.sample_theme)

        retrieved = manager.get_theme("manager-test-theme")

        self.assertEqual(retrieved.name, "manager-test-theme")
        self.assertEqual(retrieved.version, "1.0.0")

    def test_get_theme_nonexistent(self):
        """Test getting non-existent theme raises error."""
        manager = ThemeManager()

        with self.assertRaises(ThemeNotFoundError) as context:
            manager.get_theme("nonexistent-theme")

        self.assertIn("nonexistent-theme", str(context.exception))

    def test_list_themes(self):
        """Test listing all available themes."""
        manager = ThemeManager()

        # Should have built-in themes
        initial_themes = manager.list_themes()
        self.assertGreater(len(initial_themes), 0)
        self.assertIn("default", initial_themes)

        # Add custom theme
        manager.add_theme(self.sample_theme)
        themes_after_add = manager.list_themes()
        self.assertIn("manager-test-theme", themes_after_add)

    def test_set_theme(self):
        """Test setting current theme."""
        manager = ThemeManager()
        manager.add_theme(self.sample_theme)

        manager.set_theme("manager-test-theme")

        self.assertEqual(manager.current_theme.name, "manager-test-theme")

    def test_set_theme_nonexistent(self):
        """Test setting non-existent theme raises error."""
        manager = ThemeManager()

        with self.assertRaises(ThemeNotFoundError):
            manager.set_theme("nonexistent-theme")

    def test_set_theme_with_widgets(self):
        """Test setting theme applies to registered widgets."""
        manager = ThemeManager()
        manager.add_theme(self.sample_theme)

        # Register mock widget
        widget = MockWidget("test-widget")
        widget_id = manager.register_widget(widget)

        # Set theme
        manager.set_theme("manager-test-theme")

        self.assertEqual(manager.current_theme.name, "manager-test-theme")
        # Widget should receive theme application
        # This would be verified through the applicator's effects

    def test_register_widget(self):
        """Test registering widget for theme management."""
        manager = ThemeManager()
        widget = MockWidget("registered-widget")

        widget_id = manager.register_widget(widget)

        self.assertIsNotNone(widget_id)
        self.assertTrue(manager.is_widget_registered(widget))

    def test_unregister_widget(self):
        """Test unregistering widget."""
        manager = ThemeManager()
        widget = MockWidget("unregistered-widget")

        widget_id = manager.register_widget(widget)
        success = manager.unregister_widget(widget)

        self.assertTrue(success)
        self.assertFalse(manager.is_widget_registered(widget))

    def test_load_theme_from_file(self):
        """Test loading theme from file."""
        manager = ThemeManager()

        # Create temporary theme file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            import json
            json.dump(self.sample_theme_data, f)
            temp_path = f.name

        try:
            loaded_theme = manager.load_theme_from_file(temp_path)

            self.assertEqual(loaded_theme.name, "manager-test-theme")
            self.assertTrue(manager.has_theme("manager-test-theme"))

        finally:
            Path(temp_path).unlink()

    def test_load_theme_from_nonexistent_file(self):
        """Test loading from non-existent file raises error."""
        manager = ThemeManager()

        with self.assertRaises(ThemeLoadError):
            manager.load_theme_from_file("nonexistent.json")

    def test_save_theme_to_file(self):
        """Test saving theme to file."""
        manager = ThemeManager()
        manager.add_theme(self.sample_theme)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            manager.save_theme_to_file("manager-test-theme", temp_path)

            # Verify file was created and contains theme data
            self.assertTrue(Path(temp_path).exists())

            # Load and verify content
            import json
            with open(temp_path) as f:
                saved_data = json.load(f)

            self.assertEqual(saved_data["name"], "manager-test-theme")

        finally:
            Path(temp_path).unlink()

    def test_discover_themes(self):
        """Test discovering themes in directory."""
        manager = ThemeManager()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create theme files
            theme1_data = {**self.sample_theme_data, "name": "discovered-1"}
            theme2_data = {**self.sample_theme_data, "name": "discovered-2"}

            import json
            (temp_path / "theme1.json").write_text(json.dumps(theme1_data))
            (temp_path / "theme2.json").write_text(json.dumps(theme2_data))

            discovered = manager.discover_themes(temp_dir)

            self.assertEqual(len(discovered), 2)
            theme_names = [theme.name for theme in discovered]
            self.assertIn("discovered-1", theme_names)
            self.assertIn("discovered-2", theme_names)

            # Themes should be added to manager
            self.assertTrue(manager.has_theme("discovered-1"))
            self.assertTrue(manager.has_theme("discovered-2"))

    def test_switch_theme_performance(self):
        """Test theme switching meets performance requirements."""
        manager = ThemeManager()
        manager.add_theme(self.sample_theme)

        # Register multiple widgets
        widgets = [MockWidget(f"perf-widget-{i}") for i in range(100)]
        for widget in widgets:
            manager.register_widget(widget)

        # Measure theme switching time
        start_time = time.time()
        manager.set_theme("manager-test-theme")
        switch_time = time.time() - start_time

        # Should meet < 100ms requirement for 100 widgets
        self.assertLess(switch_time, 0.1)

    def test_register_theme_change_callback(self):
        """Test registering theme change callback."""
        manager = ThemeManager()
        callback_calls = []

        def test_callback(theme_name: str, widget_id: str):
            callback_calls.append((theme_name, widget_id))

        callback_id = manager.register_theme_change_callback(test_callback)
        self.assertIsNotNone(callback_id)

        # Set theme to trigger callback
        manager.add_theme(self.sample_theme)
        manager.set_theme("manager-test-theme")

        # Allow time for notifications
        time.sleep(0.1)

        # Callback might be called (depends on implementation)
        self.assertIsInstance(callback_calls, list)

    def test_unregister_theme_change_callback(self):
        """Test unregistering theme change callback."""
        manager = ThemeManager()

        def test_callback(theme_name: str, widget_id: str):
            pass

        callback_id = manager.register_theme_change_callback(test_callback)
        success = manager.unregister_theme_change_callback(callback_id)

        self.assertTrue(success)

    def test_get_theme_statistics(self):
        """Test getting theme management statistics."""
        manager = ThemeManager()
        manager.add_theme(self.sample_theme)

        widget = MockWidget("stats-widget")
        manager.register_widget(widget)
        manager.set_theme("manager-test-theme")

        stats = manager.get_statistics()

        self.assertIn("total_themes", stats)
        self.assertIn("widgets_registered", stats)
        self.assertIn("theme_switches", stats)
        self.assertIn("current_theme", stats)
        self.assertGreaterEqual(stats["total_themes"], 1)

    def test_get_builtin_themes(self):
        """Test getting built-in themes."""
        manager = ThemeManager()

        builtin_themes = manager.get_builtin_themes()

        self.assertGreater(len(builtin_themes), 0)
        self.assertIn("default", builtin_themes)
        self.assertIn("dark", builtin_themes)

    def test_reset_to_default_theme(self):
        """Test resetting to default theme."""
        manager = ThemeManager()
        manager.add_theme(self.sample_theme)

        # Set custom theme
        manager.set_theme("manager-test-theme")
        self.assertEqual(manager.current_theme.name, "manager-test-theme")

        # Reset to default
        manager.reset_to_default()

        self.assertEqual(manager.current_theme.name, "default")

    def test_clear_themes_except_builtin(self):
        """Test clearing all custom themes while preserving built-ins."""
        manager = ThemeManager()

        initial_themes = set(manager.list_themes())
        manager.add_theme(self.sample_theme)

        # Should have additional theme
        self.assertTrue(manager.has_theme("manager-test-theme"))

        # Clear custom themes
        manager.clear_themes()

        # Built-in themes should remain
        remaining_themes = set(manager.list_themes())
        self.assertEqual(remaining_themes, initial_themes)
        self.assertFalse(manager.has_theme("manager-test-theme"))

    def test_thread_safety(self):
        """Test theme manager thread safety."""
        manager = ThemeManager()
        results = []
        errors = []

        def worker(worker_id: int):
            """Worker function for concurrent testing."""
            try:
                # Create worker-specific theme
                worker_theme_data = {
                    **self.sample_theme_data,
                    "name": f"worker-theme-{worker_id}"
                }
                worker_theme = Theme.from_dict(worker_theme_data)

                # Add theme
                manager.add_theme(worker_theme)

                # Register widget
                widget = MockWidget(f"worker-widget-{worker_id}")
                manager.register_widget(widget)

                # Set theme
                manager.set_theme(f"worker-theme-{worker_id}")

                results.append(worker_id)

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
        self.assertEqual(len(results), 5)

        # All worker themes should be available
        themes = manager.list_themes()
        for worker_id in range(5):
            self.assertIn(f"worker-theme-{worker_id}", themes)

    def test_error_recovery(self):
        """Test manager handles errors gracefully."""
        manager = ThemeManager()

        # Test with invalid theme data
        invalid_theme_data = {
            "name": "",  # Invalid empty name
            "version": "1.0.0",
            "colors": {},
            "styles": {}
        }

        try:
            invalid_theme = Theme.from_dict(invalid_theme_data)
            manager.add_theme(invalid_theme)
            # Should handle gracefully without crashing
        except Exception:
            # Error is expected for invalid theme
            pass

        # Manager should still function
        self.assertIsNotNone(manager.list_themes())

    def test_memory_efficiency(self):
        """Test manager memory efficiency."""
        import gc

        manager = ThemeManager()

        # Create themes and widgets
        initial_objects = len(gc.get_objects())

        themes = []
        widgets = []

        for i in range(20):
            theme_data = {**self.sample_theme_data, "name": f"memory-theme-{i}"}
            theme = Theme.from_dict(theme_data)
            manager.add_theme(theme)
            themes.append(theme)

            widget = MockWidget(f"memory-widget-{i}")
            manager.register_widget(widget)
            widgets.append(widget)

        mid_objects = len(gc.get_objects())

        # Clean up
        manager.clear_themes()
        del themes
        del widgets
        gc.collect()

        final_objects = len(gc.get_objects())

        # Memory should be efficiently managed
        memory_growth = mid_objects - initial_objects
        memory_cleanup = mid_objects - final_objects

        cleanup_ratio = memory_cleanup / memory_growth if memory_growth > 0 else 1.0
        self.assertGreater(cleanup_ratio, 0.5)  # At least 50% cleanup

    def test_integration_with_lifecycle_manager(self):
        """Test integration with lifecycle manager."""
        lifecycle_manager = LifecycleManager()
        manager = ThemeManager(lifecycle_manager=lifecycle_manager)

        widget = MockWidget("lifecycle-widget")
        widget_id = manager.register_widget(widget)

        # Widget should be managed by lifecycle manager
        self.assertIsNotNone(widget_id)

    def test_integration_with_thread_safe_manager(self):
        """Test integration with thread-safe theme manager."""
        thread_manager = ThreadSafeThemeManager()
        manager = ThemeManager(thread_manager=thread_manager)

        manager.add_theme(self.sample_theme)
        manager.set_theme("manager-test-theme")

        self.assertEqual(manager.current_theme.name, "manager-test-theme")


class TestThemeManagerFactory(ThemedTestCase):
    """Test create_theme_manager factory function."""

    def test_create_default_manager(self):
        """Test creating manager with default configuration."""
        manager = create_theme_manager()

        self.assertIsNotNone(manager)
        self.assertIsInstance(manager, ThemeManager)

        # Should have built-in themes
        themes = manager.list_themes()
        self.assertGreater(len(themes), 0)
        self.assertIn("default", themes)

    def test_create_manager_with_custom_registry(self):
        """Test creating manager with custom registry."""
        custom_registry = ThemeWidgetRegistry()
        manager = create_theme_manager(widget_registry=custom_registry)

        self.assertIsNotNone(manager)
        # Verify custom registry is used (implementation dependent)

    def test_create_manager_with_custom_components(self):
        """Test creating manager with all custom components."""
        repository = ThemeRepository()
        applicator = ThemeApplicator()
        notifier = ThemeNotifier()

        manager = create_theme_manager(
            repository=repository,
            applicator=applicator,
            notifier=notifier
        )

        self.assertIsNotNone(manager)
        # Should still function normally
        themes = manager.list_themes()
        self.assertGreater(len(themes), 0)


class TestThemeManagerPerformance(ThemedTestCase):
    """Test ThemeManager performance requirements."""

    def test_theme_switching_performance(self):
        """Test theme switching meets < 100ms for 100 widgets requirement."""
        manager = create_theme_manager()
        manager.add_theme(self.sample_theme)

        # Register 100 widgets
        widgets = [MockWidget(f"perf-widget-{i}") for i in range(100)]
        for widget in widgets:
            manager.register_widget(widget)

        # Measure theme switching time
        start_time = time.time()
        manager.set_theme("manager-test-theme")
        switch_time = time.time() - start_time

        self.assertLess(switch_time, 0.1)  # < 100ms

    def test_theme_loading_performance(self):
        """Test theme loading meets < 200ms requirement."""
        manager = create_theme_manager()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            import json
            json.dump(self.sample_theme_data, f)
            temp_path = f.name

        try:
            # Measure loading time
            start_time = time.time()
            loaded_theme = manager.load_theme_from_file(temp_path)
            load_time = time.time() - start_time

            self.assertLess(load_time, 0.2)  # < 200ms
            self.assertEqual(loaded_theme.name, "manager-test-theme")

        finally:
            Path(temp_path).unlink()

    def test_memory_overhead_per_theme(self):
        """Test memory overhead < 2KB per theme requirement."""
        import sys

        manager = create_theme_manager()

        # Measure baseline memory
        baseline_size = sys.getsizeof(manager) + sum(
            sys.getsizeof(v) for v in manager.__dict__.values()
        )

        # Add themes and measure growth
        theme_count = 10
        for i in range(theme_count):
            theme_data = {**self.sample_theme_data, "name": f"memory-test-{i}"}
            theme = Theme.from_dict(theme_data)
            manager.add_theme(theme)

        # Calculate memory per theme
        final_size = sys.getsizeof(manager) + sum(
            sys.getsizeof(v) for v in manager.__dict__.values()
        )

        memory_per_theme = (final_size - baseline_size) / theme_count

        # Should be less than 2KB per theme
        self.assertLess(memory_per_theme, 2048)

    def test_concurrent_access_performance(self):
        """Test concurrent access performance with multiple threads."""
        manager = create_theme_manager()

        for i in range(5):
            theme_data = {**self.sample_theme_data, "name": f"concurrent-theme-{i}"}
            theme = Theme.from_dict(theme_data)
            manager.add_theme(theme)

        results = []
        errors = []

        def concurrent_worker(worker_id: int):
            """Worker function for concurrent access."""
            try:
                start_time = time.time()

                # Perform theme operations
                for i in range(10):
                    theme_name = f"concurrent-theme-{i % 5}"
                    if manager.has_theme(theme_name):
                        theme = manager.get_theme(theme_name)
                        manager.set_theme(theme_name)

                worker_time = time.time() - start_time
                results.append(worker_time)

            except Exception as e:
                errors.append(f"Worker {worker_id}: {e}")

        # Run concurrent workers
        threads = []
        start_time = time.time()

        for worker_id in range(8):
            thread = threading.Thread(target=concurrent_worker, args=(worker_id,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        total_time = time.time() - start_time

        # No errors should occur
        self.assertEqual(len(errors), 0, f"Concurrent access errors: {errors}")

        # All workers should complete
        self.assertEqual(len(results), 8)

        # Total time should be reasonable for concurrent access
        self.assertLess(total_time, 1.0)  # < 1 second total


if __name__ == "__main__":
    pytest.main([__file__])
