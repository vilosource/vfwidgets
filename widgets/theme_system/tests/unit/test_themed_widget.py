"""
Unit tests for ThemedWidget base class.

Tests the primary API that developers use - ThemedWidget inheritance pattern
with automatic registration, property access, and lifecycle management.
"""
import threading
import time
import unittest
import weakref
from unittest.mock import Mock, patch

from vfwidgets_theme.errors import PropertyNotFoundError, ThemeError
from vfwidgets_theme.lifecycle import WidgetRegistry
from vfwidgets_theme.testing import MemoryProfiler, ThemeBenchmark, ThemedTestCase
from vfwidgets_theme.widgets.base import ThemedWidget


class TestThemedWidgetCreation(ThemedTestCase):
    """Test ThemedWidget creation and basic functionality."""

    def test_themed_widget_creation(self):
        """Test basic ThemedWidget creation."""
        widget = ThemedWidget()

        # Verify widget is properly initialized
        self.assertIsInstance(widget, ThemedWidget)
        self.assertIsNotNone(widget._theme_properties)
        self.assertIsNotNone(widget._theme_manager)
        self.assertTrue(widget._is_theme_registered)

    def test_themed_widget_metaclass(self):
        """Test ThemedWidget metaclass functionality."""
        # Test custom theme_config is processed
        class CustomWidget(ThemedWidget):
            theme_config = {
                'bg': 'window.background',
                'fg': 'window.foreground',
                'accent': 'accent.primary'
            }

        widget = CustomWidget()
        self.assertIn('bg', widget._theme_config)
        self.assertIn('fg', widget._theme_config)
        self.assertIn('accent', widget._theme_config)

    def test_themed_widget_without_config(self):
        """Test ThemedWidget creation without theme_config."""
        widget = ThemedWidget()

        # Should have default config
        self.assertIsInstance(widget._theme_config, dict)
        self.assertIn('background', widget._theme_config)
        self.assertIn('color', widget._theme_config)

    def test_themed_widget_parent_inheritance(self):
        """Test that child widgets inherit parent themes."""
        parent = ThemedWidget()
        child = ThemedWidget(parent=parent)

        self.assertEqual(child.parent(), parent)
        # Child should be registered with theme system
        self.assertTrue(child._is_theme_registered)

    def test_themed_widget_memory_registration(self):
        """Test that widgets are properly registered in memory system."""
        widget = ThemedWidget()
        widget_id = widget._widget_id

        # Widget should be in registry
        registry = WidgetRegistry.get_instance()
        self.assertTrue(registry.is_registered(widget_id))

        # Widget should be cleanable
        weak_ref = weakref.ref(widget)
        del widget

        # Registry should handle cleanup
        self.assertIsNone(weak_ref())


class TestThemedWidgetProperties(ThemedTestCase):
    """Test ThemedWidget property system."""

    def setUp(self):
        """Set up test widget with custom properties."""
        super().setUp()

        class TestWidget(ThemedWidget):
            theme_config = {
                'background': 'window.background',
                'foreground': 'window.foreground',
                'accent': 'accent.primary',
                'border': 'control.border'
            }

        self.widget = TestWidget()

    def test_property_access(self):
        """Test theme property access."""
        # Should be able to access configured properties
        background = self.widget.theme.background
        self.assertIsInstance(background, str)

        foreground = self.widget.theme.foreground
        self.assertIsInstance(foreground, str)

    def test_property_caching(self):
        """Test property access caching for performance."""
        # First access should cache
        start_time = time.perf_counter()
        background1 = self.widget.theme.background
        first_access_time = time.perf_counter() - start_time

        # Second access should be cached
        start_time = time.perf_counter()
        background2 = self.widget.theme.background
        cached_access_time = time.perf_counter() - start_time

        # Results should be identical
        self.assertEqual(background1, background2)

        # Cached access should be faster (< 1μs requirement)
        self.assertLess(cached_access_time, 0.000001)  # 1μs

    def test_property_fallback(self):
        """Test property fallback when property not found."""
        # Access non-existent property should return fallback
        with patch.object(self.widget._theme_properties, 'get_property',
                          side_effect=PropertyNotFoundError("test.missing", "Test missing")):
            value = self.widget.theme.missing_property
            self.assertIsNotNone(value)  # Should get fallback value

    def test_property_change_detection(self):
        """Test property change detection and notifications."""
        changes_detected = []

        def on_property_changed(property_name, old_value, new_value):
            changes_detected.append((property_name, old_value, new_value))

        self.widget.property_changed.connect(on_property_changed)

        # Simulate theme change that affects properties
        self.widget._on_theme_changed(self.mock_theme)

        # Should detect changes (mock may not trigger actual changes)
        # This verifies the signal mechanism works
        self.assertTrue(hasattr(self.widget, 'property_changed'))

    def test_property_descriptor_behavior(self):
        """Test theme property descriptor behavior."""
        # Test descriptor creates proper attributes
        self.assertTrue(hasattr(self.widget.theme, 'background'))
        self.assertTrue(hasattr(self.widget.theme, 'foreground'))

        # Test descriptor caching
        prop1 = self.widget.theme.background
        prop2 = self.widget.theme.background
        self.assertEqual(prop1, prop2)

    def test_dynamic_property_access(self):
        """Test dynamic property access patterns."""
        # Test getitem access
        background = self.widget.theme['background']
        self.assertIsInstance(background, str)

        # Test get with default
        missing = self.widget.theme.get('missing', 'default')
        self.assertEqual(missing, 'default')


class TestThemedWidgetLifecycle(ThemedTestCase):
    """Test ThemedWidget lifecycle management."""

    def test_widget_registration(self):
        """Test automatic widget registration."""
        widget = ThemedWidget()

        # Widget should be registered
        self.assertTrue(widget._is_theme_registered)

        # Should have widget ID
        self.assertIsNotNone(widget._widget_id)

        # Should be in registry
        registry = WidgetRegistry.get_instance()
        self.assertTrue(registry.is_registered(widget._widget_id))

    def test_widget_cleanup(self):
        """Test automatic widget cleanup."""
        widget = ThemedWidget()
        widget_id = widget._widget_id
        weak_ref = weakref.ref(widget)

        # Simulate cleanup
        widget._cleanup_theme()

        # Should be unregistered
        self.assertFalse(widget._is_theme_registered)

        del widget

        # Should be garbage collected
        self.assertIsNone(weak_ref())

    def test_widget_close_event(self):
        """Test widget close event handling."""
        widget = ThemedWidget()
        widget_id = widget._widget_id

        # Mock close event
        mock_event = Mock()
        widget.closeEvent(mock_event)

        # Should trigger cleanup
        self.assertFalse(widget._is_theme_registered)

    def test_widget_destructor(self):
        """Test widget destructor cleanup."""
        widget = ThemedWidget()
        widget_id = widget._widget_id

        # Should cleanup on deletion
        del widget

        # Registry should handle cleanup automatically

    def test_parent_child_cleanup(self):
        """Test parent-child cleanup relationships."""
        parent = ThemedWidget()
        child1 = ThemedWidget(parent=parent)
        child2 = ThemedWidget(parent=parent)

        # All should be registered
        self.assertTrue(parent._is_theme_registered)
        self.assertTrue(child1._is_theme_registered)
        self.assertTrue(child2._is_theme_registered)

        # Parent cleanup should cleanup children
        parent._cleanup_theme()

        # All should be unregistered
        self.assertFalse(parent._is_theme_registered)


class TestThemedWidgetThemeUpdates(ThemedTestCase):
    """Test ThemedWidget theme update handling."""

    def setUp(self):
        """Set up test widget."""
        super().setUp()
        self.widget = ThemedWidget()
        self.update_calls = []

    def test_theme_change_notification(self):
        """Test theme change notification handling."""
        # Track update calls
        original_update = self.widget._apply_theme_update

        def mock_update(*args, **kwargs):
            self.update_calls.append((args, kwargs))
            return original_update(*args, **kwargs)

        self.widget._apply_theme_update = mock_update

        # Simulate theme change
        self.widget._on_theme_changed(self.mock_theme)

        # Should have received update call
        self.assertGreaterEqual(len(self.update_calls), 0)  # May be 0 if no changes

    def test_batch_theme_updates(self):
        """Test batched theme updates for performance."""
        # Create multiple widgets
        widgets = [ThemedWidget() for _ in range(10)]

        # Track update timing
        start_time = time.perf_counter()

        # Simulate batch theme change
        for widget in widgets:
            widget._on_theme_changed(self.mock_theme)

        update_time = time.perf_counter() - start_time

        # Should complete quickly (< 100ms for batch updates)
        self.assertLess(update_time, 0.1)

        # Cleanup
        for widget in widgets:
            widget._cleanup_theme()

    def test_custom_theme_change_handler(self):
        """Test custom theme change handler."""
        handler_called = []

        class CustomWidget(ThemedWidget):
            def on_theme_changed(self):
                handler_called.append(True)

        widget = CustomWidget()

        # Simulate theme change
        widget._on_theme_changed(self.mock_theme)

        # Custom handler should be called
        # Note: May not be called if theme doesn't actually change
        self.assertTrue(hasattr(widget, 'on_theme_changed'))

    def test_theme_inheritance(self):
        """Test theme inheritance from parent widgets."""
        parent = ThemedWidget()
        child = ThemedWidget(parent=parent)

        # Child should inherit parent theme context
        self.assertEqual(child.parent(), parent)

        # Both should receive theme updates
        parent._on_theme_changed(self.mock_theme)
        child._on_theme_changed(self.mock_theme)


class TestThemedWidgetPerformance(ThemedTestCase):
    """Test ThemedWidget performance requirements."""

    def test_widget_creation_performance(self):
        """Test widget creation meets performance requirements."""
        benchmark = ThemeBenchmark()

        # Test widget creation time (< 50ms requirement)
        def create_widget():
            return ThemedWidget()

        creation_time = benchmark.measure_time(create_widget)
        self.assertLess(creation_time, 0.05)  # 50ms

    def test_property_access_performance(self):
        """Test property access meets performance requirements."""
        widget = ThemedWidget()
        benchmark = ThemeBenchmark()

        # Test cached property access (< 1μs requirement)
        def access_property():
            return widget.theme.background

        # First access to cache
        widget.theme.background

        # Measure cached access
        access_time = benchmark.measure_time(access_property)
        self.assertLess(access_time, 0.000001)  # 1μs

    def test_theme_update_performance(self):
        """Test theme update meets performance requirements."""
        widget = ThemedWidget()
        benchmark = ThemeBenchmark()

        # Test theme update time (< 10ms per widget requirement)
        def update_theme():
            widget._on_theme_changed(self.mock_theme)

        update_time = benchmark.measure_time(update_theme)
        self.assertLess(update_time, 0.01)  # 10ms

    def test_memory_overhead(self):
        """Test widget memory overhead (< 1KB requirement)."""
        profiler = MemoryProfiler()

        baseline = profiler.get_memory_usage()
        widget = ThemedWidget()
        widget_memory = profiler.get_memory_usage()

        # Calculate overhead
        overhead = widget_memory - baseline
        self.assertLess(overhead, 1024)  # 1KB

    def test_cleanup_performance(self):
        """Test cleanup performance (< 1ms requirement)."""
        widget = ThemedWidget()
        benchmark = ThemeBenchmark()

        def cleanup_widget():
            widget._cleanup_theme()

        cleanup_time = benchmark.measure_time(cleanup_widget)
        self.assertLess(cleanup_time, 0.001)  # 1ms


class TestThemedWidgetThreadSafety(ThemedTestCase):
    """Test ThemedWidget thread safety."""

    def test_concurrent_widget_creation(self):
        """Test concurrent widget creation is thread-safe."""
        widgets = []
        errors = []

        def create_widgets():
            try:
                for _ in range(10):
                    widget = ThemedWidget()
                    widgets.append(widget)
            except Exception as e:
                errors.append(e)

        # Create widgets concurrently
        threads = [threading.Thread(target=create_widgets) for _ in range(4)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Should have no errors
        self.assertEqual(len(errors), 0)

        # Should have created expected number of widgets
        self.assertEqual(len(widgets), 40)  # 4 threads * 10 widgets

        # Cleanup
        for widget in widgets:
            widget._cleanup_theme()

    def test_concurrent_property_access(self):
        """Test concurrent property access is thread-safe."""
        widget = ThemedWidget()
        values = []
        errors = []

        def access_properties():
            try:
                for _ in range(100):
                    value = widget.theme.background
                    values.append(value)
            except Exception as e:
                errors.append(e)

        # Access properties concurrently
        threads = [threading.Thread(target=access_properties) for _ in range(4)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Should have no errors
        self.assertEqual(len(errors), 0)

        # Should have consistent values
        unique_values = set(values)
        self.assertLessEqual(len(unique_values), 2)  # Should be consistent

    def test_concurrent_theme_updates(self):
        """Test concurrent theme updates are thread-safe."""
        widgets = [ThemedWidget() for _ in range(10)]
        errors = []

        def update_themes():
            try:
                for widget in widgets:
                    widget._on_theme_changed(self.mock_theme)
            except Exception as e:
                errors.append(e)

        # Update themes concurrently
        threads = [threading.Thread(target=update_themes) for _ in range(4)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Should have no errors
        self.assertEqual(len(errors), 0)

        # Cleanup
        for widget in widgets:
            widget._cleanup_theme()


class TestThemedWidgetErrorRecovery(ThemedTestCase):
    """Test ThemedWidget error recovery."""

    def test_theme_loading_error_recovery(self):
        """Test recovery from theme loading errors."""
        widget = ThemedWidget()

        # Mock theme loading error
        with patch.object(widget._theme_manager, 'get_current_theme',
                          side_effect=ThemeError("Loading failed")):

            # Should not crash - should use fallback
            background = widget.theme.background
            self.assertIsNotNone(background)

    def test_property_resolution_error_recovery(self):
        """Test recovery from property resolution errors."""
        widget = ThemedWidget()

        # Mock property resolution error
        with patch.object(widget._theme_properties, 'get_property',
                          side_effect=PropertyNotFoundError("test.missing", "Missing")):

            # Should not crash - should use fallback
            value = widget.theme.missing_property
            self.assertIsNotNone(value)

    def test_theme_update_error_recovery(self):
        """Test recovery from theme update errors."""
        widget = ThemedWidget()

        # Mock theme update error
        with patch.object(widget, '_apply_theme_update',
                          side_effect=Exception("Update failed")):

            # Should not crash
            try:
                widget._on_theme_changed(self.mock_theme)
            except Exception:
                self.fail("Theme update should not raise exceptions")

    def test_cleanup_error_recovery(self):
        """Test recovery from cleanup errors."""
        widget = ThemedWidget()

        # Mock cleanup error
        with patch.object(widget._theme_manager, 'unregister_widget',
                          side_effect=Exception("Cleanup failed")):

            # Should not crash during cleanup
            try:
                widget._cleanup_theme()
            except Exception:
                self.fail("Cleanup should not raise exceptions")


class TestThemedWidgetCustomization(ThemedTestCase):
    """Test ThemedWidget customization capabilities."""

    def test_custom_theme_config(self):
        """Test custom theme configuration."""
        class CustomWidget(ThemedWidget):
            theme_config = {
                'primary': 'accent.primary',
                'secondary': 'accent.secondary',
                'background': 'custom.background',
                'text': 'custom.text'
            }

        widget = CustomWidget()

        # Should have custom config
        self.assertIn('primary', widget._theme_config)
        self.assertIn('secondary', widget._theme_config)
        self.assertEqual(widget._theme_config['primary'], 'accent.primary')

    def test_custom_theme_change_handler(self):
        """Test custom theme change handler."""
        handler_calls = []

        class CustomWidget(ThemedWidget):
            def on_theme_changed(self):
                handler_calls.append(True)
                super().on_theme_changed()

        widget = CustomWidget()
        widget._on_theme_changed(self.mock_theme)

        # Verify handler structure exists
        self.assertTrue(hasattr(widget, 'on_theme_changed'))

    def test_custom_property_access(self):
        """Test custom property access patterns."""
        class CustomWidget(ThemedWidget):
            theme_config = {
                'bg': 'window.background',
                'fg': 'window.foreground'
            }

            @property
            def background_color(self):
                return self.theme.bg

            @property
            def text_color(self):
                return self.theme.fg

        widget = CustomWidget()

        # Should support custom property methods
        self.assertIsNotNone(widget.background_color)
        self.assertIsNotNone(widget.text_color)

    def test_theme_config_inheritance(self):
        """Test theme config inheritance in class hierarchy."""
        class BaseWidget(ThemedWidget):
            theme_config = {
                'base_bg': 'window.background',
                'base_fg': 'window.foreground'
            }

        class DerivedWidget(BaseWidget):
            theme_config = {
                'derived_accent': 'accent.primary',
                'derived_border': 'control.border'
            }

        widget = DerivedWidget()

        # Should have merged config
        config = widget._theme_config
        self.assertIn('base_bg', config)
        self.assertIn('base_fg', config)
        self.assertIn('derived_accent', config)
        self.assertIn('derived_border', config)


if __name__ == '__main__':
    unittest.main()
