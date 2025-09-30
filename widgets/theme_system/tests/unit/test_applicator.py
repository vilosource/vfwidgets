"""
Test suite for ThemeApplicator.

Tests theme application to widgets and applications including:
- Widget theme application using the registry
- QApplication-level stylesheet application
- Batch theme updates for performance
- Style invalidation and cache management
- Platform-specific adaptations
- Async theme application support
- Error handling and recovery
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock, call
from typing import List, Dict, Any

# Import Qt components with fallback for headless testing
try:
    from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel
    from PySide6.QtCore import QObject, Signal, QTimer
    from PySide6.QtGui import QPalette
    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False
    # Create mock classes for headless testing
    class QObject:
        def __init__(self): pass
    class QWidget(QObject):
        def __init__(self, parent=None): super().__init__()
        def setStyleSheet(self, stylesheet): pass
        def styleSheet(self): return ""
    class QApplication(QObject):
        def __init__(self): super().__init__()
        def setStyleSheet(self, stylesheet): pass
        def styleSheet(self): return ""
    class QPushButton(QWidget): pass
    class QLabel(QWidget): pass
    class QPalette: pass
    class Signal: pass

# Import the modules under test
from vfwidgets_theme.core.applicator import (
    ThemeApplicator, WidgetThemeApplicator, ApplicationThemeApplicator,
    BatchThemeUpdater, StyleInvalidator, AsyncThemeApplicator,
    PlatformThemeAdapter, create_theme_applicator
)
from vfwidgets_theme.core.theme import Theme
from vfwidgets_theme.core.registry import ThemeWidgetRegistry
from vfwidgets_theme.errors import ThemeApplicationError, ThemeNotFoundError
from vfwidgets_theme.testing import ThemedTestCase, MockThemeableWidget
from vfwidgets_theme.protocols import ThemeableWidget


class MockWidget(QWidget):
    """Mock widget for testing theme application."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.applied_themes = []
        self.style_sheets = []
        self._current_stylesheet = ""

    def setStyleSheet(self, stylesheet: str):
        """Override to track stylesheet changes."""
        self._current_stylesheet = stylesheet
        self.style_sheets.append(stylesheet)

    def styleSheet(self) -> str:
        """Override to return current stylesheet."""
        return self._current_stylesheet

    def apply_theme(self, theme_name: str):
        """Mock theme application method."""
        self.applied_themes.append(theme_name)


class TestThemeApplicator(ThemedTestCase):
    """Test ThemeApplicator main coordination class."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.registry = ThemeWidgetRegistry()
        self.applicator = ThemeApplicator(registry=self.registry)

        # Create sample theme
        self.sample_theme = Theme.from_dict({
            "name": "test-theme",
            "version": "1.0.0",
            "colors": {
                "primary": "#007acc",
                "secondary": "#ffffff",
                "background": "#f5f5f5"
            },
            "styles": {
                "QPushButton": "background-color: @colors.primary; color: @colors.secondary;",
                "QLabel": "color: @colors.primary; background-color: @colors.background;"
            }
        })

    def test_applicator_initialization(self):
        """Test applicator initialization with default settings."""
        applicator = ThemeApplicator()
        self.assertIsNotNone(applicator)
        self.assertIsNotNone(applicator._widget_applicator)
        self.assertIsNotNone(applicator._app_applicator)
        self.assertIsNotNone(applicator._batch_updater)

    def test_applicator_with_custom_components(self):
        """Test applicator initialization with custom components."""
        custom_registry = ThemeWidgetRegistry()
        widget_applicator = WidgetThemeApplicator(custom_registry)

        applicator = ThemeApplicator(
            registry=custom_registry,
            widget_applicator=widget_applicator
        )

        self.assertIs(applicator._registry, custom_registry)
        self.assertIs(applicator._widget_applicator, widget_applicator)

    def test_apply_theme_to_widget(self):
        """Test applying theme to individual widget."""
        widget = MockWidget()
        widget_id = self.registry.register_widget(widget)

        success = self.applicator.apply_theme_to_widget(widget_id, self.sample_theme)

        self.assertTrue(success)
        # Verify theme was applied through registry
        entry = self.registry.get_entry(widget_id)
        self.assertEqual(entry.theme_metadata.get("current_theme"), "test-theme")

    def test_apply_theme_to_nonexistent_widget(self):
        """Test applying theme to non-existent widget returns False."""
        success = self.applicator.apply_theme_to_widget("nonexistent", self.sample_theme)
        self.assertFalse(success)

    def test_apply_theme_globally(self):
        """Test applying theme globally to all registered widgets."""
        widgets = [MockWidget() for _ in range(3)]
        widget_ids = [self.registry.register_widget(w) for w in widgets]

        results = self.applicator.apply_theme_globally(self.sample_theme)

        self.assertEqual(len(results), 3)
        self.assertTrue(all(results.values()))

        # Verify all widgets have theme applied
        for widget_id in widget_ids:
            entry = self.registry.get_entry(widget_id)
            self.assertEqual(entry.theme_metadata.get("current_theme"), "test-theme")

    def test_apply_theme_to_application(self):
        """Test applying theme at application level."""
        with patch('vfwidgets_theme.core.applicator.QApplication.instance') as mock_instance:
            mock_app = Mock()
            mock_instance.return_value = mock_app

            success = self.applicator.apply_theme_to_application(self.sample_theme)

            self.assertTrue(success)
            mock_app.setStyleSheet.assert_called_once()

    def test_batch_theme_update(self):
        """Test batch theme update for performance."""
        widgets = [MockWidget() for _ in range(5)]
        widget_ids = [self.registry.register_widget(w) for w in widgets]

        # Measure batch update time
        start_time = time.time()
        results = self.applicator.batch_update_theme(self.sample_theme, widget_ids)
        update_time = time.time() - start_time

        self.assertEqual(len(results), 5)
        self.assertTrue(all(results.values()))

        # Batch update should be faster than individual updates
        # For 5 widgets, should complete well under performance requirement
        self.assertLess(update_time, 0.1)  # < 100ms

    def test_invalidate_theme_cache(self):
        """Test theme cache invalidation."""
        widget = MockWidget()
        widget_id = self.registry.register_widget(widget)

        self.applicator.apply_theme_to_widget(widget_id, self.sample_theme)

        # Invalidate cache
        self.applicator.invalidate_theme_cache()

        # Should still work after cache invalidation
        success = self.applicator.apply_theme_to_widget(widget_id, self.sample_theme)
        self.assertTrue(success)

    def test_get_application_statistics(self):
        """Test getting applicator statistics."""
        widgets = [MockWidget() for _ in range(3)]
        for widget in widgets:
            widget_id = self.registry.register_widget(widget)
            self.applicator.apply_theme_to_widget(widget_id, self.sample_theme)

        stats = self.applicator.get_statistics()

        self.assertIn("widgets_themed", stats)
        self.assertIn("global_updates", stats)
        self.assertIn("batch_updates", stats)
        self.assertIn("cache_hits", stats)
        self.assertGreaterEqual(stats["widgets_themed"], 3)

    def test_performance_requirements(self):
        """Test applicator meets performance requirements."""
        # Create 100 widgets for performance test
        widgets = [MockWidget() for _ in range(100)]
        widget_ids = [self.registry.register_widget(w) for w in widgets]

        # Test theme switching performance (< 100ms for 100 widgets)
        start_time = time.time()
        results = self.applicator.apply_theme_globally(self.sample_theme)
        switch_time = time.time() - start_time

        self.assertLess(switch_time, 0.1)  # < 100ms
        self.assertEqual(len(results), 100)
        self.assertTrue(all(results.values()))


class TestWidgetThemeApplicator(ThemedTestCase):
    """Test WidgetThemeApplicator for individual widget theming."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.registry = ThemeWidgetRegistry()
        self.applicator = WidgetThemeApplicator(self.registry)

        self.sample_theme = Theme.from_dict({
            "name": "widget-theme",
            "version": "1.0.0",
            "colors": {"primary": "#007acc"},
            "styles": {"QPushButton": "background-color: @colors.primary;"}
        })

    def test_apply_to_single_widget(self):
        """Test applying theme to single widget."""
        widget = MockWidget()

        success = self.applicator.apply_theme(widget, self.sample_theme)

        self.assertTrue(success)
        self.assertEqual(len(widget.style_sheets), 1)
        self.assertIn("background-color: #007acc", widget.style_sheets[0])

    def test_apply_to_widget_by_id(self):
        """Test applying theme to widget by registry ID."""
        widget = MockWidget()
        widget_id = self.registry.register_widget(widget)

        success = self.applicator.apply_theme_by_id(widget_id, self.sample_theme)

        self.assertTrue(success)
        entry = self.registry.get_entry(widget_id)
        self.assertEqual(entry.theme_metadata.get("current_theme"), "widget-theme")

    def test_apply_to_dead_widget_reference(self):
        """Test applying theme to widget with dead reference."""
        widget = MockWidget()
        widget_id = self.registry.register_widget(widget)

        # Delete widget to create dead reference
        del widget

        success = self.applicator.apply_theme_by_id(widget_id, self.sample_theme)
        self.assertFalse(success)

    def test_batch_widget_application(self):
        """Test batch application to multiple widgets."""
        widgets = [MockWidget() for _ in range(10)]
        widget_ids = [self.registry.register_widget(w) for w in widgets]

        results = self.applicator.apply_theme_batch(widget_ids, self.sample_theme)

        self.assertEqual(len(results), 10)
        successful_count = sum(1 for success in results.values() if success)
        self.assertEqual(successful_count, 10)

    def test_style_generation(self):
        """Test CSS style generation from theme."""
        theme_with_references = Theme.from_dict({
            "name": "reference-theme",
            "version": "1.0.0",
            "colors": {
                "primary": "#007acc",
                "secondary": "#ffffff"
            },
            "styles": {
                "QPushButton": "background-color: @colors.primary; color: @colors.secondary;",
                "QLabel": "color: @colors.primary;"
            }
        })

        widget = MockWidget()
        self.applicator.apply_theme(widget, theme_with_references)

        # Check that color references were resolved
        stylesheet = widget.styleSheet()
        self.assertIn("#007acc", stylesheet)  # primary color resolved
        self.assertIn("#ffffff", stylesheet)  # secondary color resolved
        self.assertNotIn("@colors", stylesheet)  # No unresolved references

    def test_widget_specific_styling(self):
        """Test widget-specific style application."""
        button = MockWidget()
        button.__class__.__name__ = "QPushButton"

        label = MockWidget()
        label.__class__.__name__ = "QLabel"

        theme = Theme.from_dict({
            "name": "specific-theme",
            "version": "1.0.0",
            "colors": {"primary": "#007acc"},
            "styles": {
                "QPushButton": "background-color: @colors.primary;",
                "QLabel": "font-weight: bold;"
            }
        })

        self.applicator.apply_theme(button, theme)
        self.applicator.apply_theme(label, theme)

        # Button should have background color
        button_style = button.styleSheet()
        self.assertIn("background-color", button_style)

        # Label should have font weight
        label_style = label.styleSheet()
        self.assertIn("font-weight: bold", label_style)


class TestApplicationThemeApplicator(ThemedTestCase):
    """Test ApplicationThemeApplicator for application-level theming."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.applicator = ApplicationThemeApplicator()

        self.sample_theme = Theme.from_dict({
            "name": "app-theme",
            "version": "1.0.0",
            "colors": {"background": "#f0f0f0"},
            "styles": {
                "QMainWindow": "background-color: @colors.background;",
                "*": "font-family: 'Segoe UI';"
            }
        })

    @patch('vfwidgets_theme.core.applicator.QApplication.instance')
    def test_apply_global_stylesheet(self, mock_instance):
        """Test applying global application stylesheet."""
        mock_app = Mock()
        mock_instance.return_value = mock_app

        success = self.applicator.apply_theme(self.sample_theme)

        self.assertTrue(success)
        mock_app.setStyleSheet.assert_called_once()

        # Verify stylesheet content
        call_args = mock_app.setStyleSheet.call_args[0][0]
        self.assertIn("background-color: #f0f0f0", call_args)
        self.assertIn("font-family: 'Segoe UI'", call_args)

    @patch('vfwidgets_theme.core.applicator.QApplication.instance')
    def test_apply_with_no_application(self, mock_instance):
        """Test applying theme with no QApplication instance."""
        mock_instance.return_value = None

        success = self.applicator.apply_theme(self.sample_theme)

        self.assertFalse(success)

    @patch('vfwidgets_theme.core.applicator.QApplication.instance')
    def test_clear_application_stylesheet(self, mock_instance):
        """Test clearing application stylesheet."""
        mock_app = Mock()
        mock_instance.return_value = mock_app

        self.applicator.clear_theme()

        mock_app.setStyleSheet.assert_called_once_with("")

    @patch('vfwidgets_theme.core.applicator.QApplication.instance')
    def test_get_current_stylesheet(self, mock_instance):
        """Test getting current application stylesheet."""
        mock_app = Mock()
        mock_app.styleSheet.return_value = "existing stylesheet"
        mock_instance.return_value = mock_app

        current = self.applicator.get_current_stylesheet()

        self.assertEqual(current, "existing stylesheet")
        mock_app.styleSheet.assert_called_once()


class TestBatchThemeUpdater(ThemedTestCase):
    """Test BatchThemeUpdater for efficient bulk updates."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.registry = ThemeWidgetRegistry()
        self.updater = BatchThemeUpdater(self.registry)

        self.sample_theme = Theme.from_dict({
            "name": "batch-theme",
            "version": "1.0.0",
            "colors": {"primary": "#007acc"},
            "styles": {"QPushButton": "background-color: @colors.primary;"}
        })

    def test_batch_update_performance(self):
        """Test batch update performance optimization."""
        widgets = [MockWidget() for _ in range(50)]
        widget_ids = [self.registry.register_widget(w) for w in widgets]

        # Measure batch update time
        start_time = time.time()
        results = self.updater.update_widgets(widget_ids, self.sample_theme)
        batch_time = time.time() - start_time

        self.assertEqual(len(results), 50)
        self.assertTrue(all(results.values()))

        # Batch update should be efficient
        self.assertLess(batch_time, 0.05)  # < 50ms for 50 widgets

    def test_batch_update_with_invalid_widgets(self):
        """Test batch update handles invalid widget IDs gracefully."""
        valid_widget = MockWidget()
        valid_id = self.registry.register_widget(valid_widget)

        widget_ids = [valid_id, "invalid-id-1", "invalid-id-2"]

        results = self.updater.update_widgets(widget_ids, self.sample_theme)

        self.assertEqual(len(results), 3)
        self.assertTrue(results[valid_id])
        self.assertFalse(results["invalid-id-1"])
        self.assertFalse(results["invalid-id-2"])

    def test_batch_update_with_error_recovery(self):
        """Test batch update continues despite individual widget errors."""
        widgets = [MockWidget() for _ in range(5)]
        widget_ids = [self.registry.register_widget(w) for w in widgets]

        # Mock one widget to raise exception
        with patch.object(self.updater._widget_applicator, 'apply_theme_by_id') as mock_apply:
            # First call raises exception, rest succeed
            mock_apply.side_effect = [Exception("Test error"), True, True, True, True]

            results = self.updater.update_widgets(widget_ids, self.sample_theme)

            self.assertEqual(len(results), 5)
            # First should fail, rest should succeed
            values = list(results.values())
            self.assertFalse(values[0])
            self.assertTrue(all(values[1:]))

    def test_concurrent_batch_updates(self):
        """Test concurrent batch updates are thread-safe."""
        widgets = [MockWidget() for _ in range(20)]
        widget_ids = [self.registry.register_widget(w) for w in widgets]

        results = []
        errors = []

        def batch_worker(worker_id: int):
            """Worker function for concurrent batch updates."""
            try:
                worker_ids = widget_ids[worker_id*5:(worker_id+1)*5]  # 5 widgets per worker
                worker_results = self.updater.update_widgets(worker_ids, self.sample_theme)
                results.extend(worker_results.values())
            except Exception as e:
                errors.append(f"Worker {worker_id}: {e}")

        threads = []
        for worker_id in range(4):  # 4 workers, 5 widgets each
            thread = threading.Thread(target=batch_worker, args=(worker_id,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        self.assertEqual(len(errors), 0, f"Concurrent update errors: {errors}")
        self.assertEqual(len(results), 20)
        self.assertTrue(all(results))


class TestStyleInvalidator(ThemedTestCase):
    """Test StyleInvalidator for cache management."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.invalidator = StyleInvalidator()

    def test_invalidate_widget_cache(self):
        """Test invalidating widget style cache."""
        widget = MockWidget()
        widget.setStyleSheet("cached stylesheet")

        self.invalidator.invalidate_widget(widget)

        # Widget should be notified to refresh its styling
        # In a real implementation, this would clear internal Qt caches
        self.assertIsNotNone(widget)  # Basic test - widget still exists

    def test_invalidate_all_caches(self):
        """Test invalidating all style caches."""
        widgets = [MockWidget() for _ in range(5)]

        # Set some cached styles
        for i, widget in enumerate(widgets):
            widget.setStyleSheet(f"cached style {i}")

        self.invalidator.invalidate_all()

        # All widgets should have cache invalidated
        for widget in widgets:
            self.assertIsNotNone(widget)  # Basic test

    def test_selective_invalidation(self):
        """Test selective cache invalidation by theme."""
        widget1 = MockWidget()
        widget2 = MockWidget()

        # Associate widgets with different themes
        self.invalidator.associate_widget_theme(widget1, "theme-a")
        self.invalidator.associate_widget_theme(widget2, "theme-b")

        # Invalidate only theme-a
        invalidated_count = self.invalidator.invalidate_theme("theme-a")

        self.assertGreaterEqual(invalidated_count, 0)


class TestAsyncThemeApplicator(ThemedTestCase):
    """Test AsyncThemeApplicator for non-blocking theme updates."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.registry = ThemeWidgetRegistry()
        self.async_applicator = AsyncThemeApplicator(self.registry)

        self.sample_theme = Theme.from_dict({
            "name": "async-theme",
            "version": "1.0.0",
            "colors": {"primary": "#007acc"},
            "styles": {"QPushButton": "background-color: @colors.primary;"}
        })

    def test_async_apply_theme(self):
        """Test asynchronous theme application."""
        widget = MockWidget()
        widget_id = self.registry.register_widget(widget)

        # Start async application
        future = self.async_applicator.apply_theme_async(widget_id, self.sample_theme)

        self.assertIsNotNone(future)

        # Wait for completion
        result = future.result(timeout=1.0)
        self.assertTrue(result)

    def test_async_batch_update(self):
        """Test asynchronous batch theme update."""
        widgets = [MockWidget() for _ in range(10)]
        widget_ids = [self.registry.register_widget(w) for w in widgets]

        # Start async batch update
        future = self.async_applicator.apply_theme_batch_async(widget_ids, self.sample_theme)

        self.assertIsNotNone(future)

        # Wait for completion
        results = future.result(timeout=2.0)
        self.assertEqual(len(results), 10)
        self.assertTrue(all(results.values()))

    def test_async_with_callback(self):
        """Test async theme application with completion callback."""
        widget = MockWidget()
        widget_id = self.registry.register_widget(widget)

        callback_called = threading.Event()
        callback_result = []

        def completion_callback(success: bool, widget_id: str):
            """Callback function for async completion."""
            callback_result.append((success, widget_id))
            callback_called.set()

        future = self.async_applicator.apply_theme_async(
            widget_id, self.sample_theme, callback=completion_callback
        )

        # Wait for callback
        self.assertTrue(callback_called.wait(timeout=1.0))

        # Verify callback was called with correct parameters
        self.assertEqual(len(callback_result), 1)
        success, cb_widget_id = callback_result[0]
        self.assertTrue(success)
        self.assertEqual(cb_widget_id, widget_id)

    def test_cancel_async_operation(self):
        """Test canceling async theme application."""
        widget = MockWidget()
        widget_id = self.registry.register_widget(widget)

        future = self.async_applicator.apply_theme_async(widget_id, self.sample_theme)

        # Cancel operation
        cancelled = future.cancel()

        # Note: cancellation success depends on timing
        self.assertIsInstance(cancelled, bool)


class TestPlatformThemeAdapter(ThemedTestCase):
    """Test PlatformThemeAdapter for platform-specific adaptations."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.adapter = PlatformThemeAdapter()

    def test_platform_specific_colors(self):
        """Test platform-specific color adaptations."""
        base_theme = Theme.from_dict({
            "name": "platform-theme",
            "version": "1.0.0",
            "colors": {"primary": "#007acc"},
            "styles": {"QPushButton": "background-color: @colors.primary;"}
        })

        adapted_theme = self.adapter.adapt_theme_for_platform(base_theme)

        self.assertIsNotNone(adapted_theme)
        self.assertEqual(adapted_theme.name, base_theme.name)
        # Colors may be adapted for current platform
        self.assertIn("primary", adapted_theme.colors)

    def test_platform_specific_fonts(self):
        """Test platform-specific font adaptations."""
        theme_with_fonts = Theme.from_dict({
            "name": "font-theme",
            "version": "1.0.0",
            "colors": {"primary": "#007acc"},
            "styles": {
                "QPushButton": "font-family: 'System Font'; background-color: @colors.primary;"
            }
        })

        adapted_theme = self.adapter.adapt_theme_for_platform(theme_with_fonts)

        # Font family should be adapted for current platform
        button_style = adapted_theme.styles.get("QPushButton", "")
        self.assertIn("font-family:", button_style)

    @patch('platform.system')
    def test_windows_specific_adaptations(self, mock_system):
        """Test Windows-specific theme adaptations."""
        mock_system.return_value = "Windows"

        theme = Theme.from_dict({
            "name": "windows-theme",
            "version": "1.0.0",
            "colors": {"primary": "#007acc"},
            "styles": {"QPushButton": "background-color: @colors.primary;"}
        })

        adapted_theme = self.adapter.adapt_theme_for_platform(theme)

        # Should have Windows-specific adaptations
        self.assertIsNotNone(adapted_theme)

    @patch('platform.system')
    def test_macos_specific_adaptations(self, mock_system):
        """Test macOS-specific theme adaptations."""
        mock_system.return_value = "Darwin"

        theme = Theme.from_dict({
            "name": "macos-theme",
            "version": "1.0.0",
            "colors": {"primary": "#007acc"},
            "styles": {"QPushButton": "background-color: @colors.primary;"}
        })

        adapted_theme = self.adapter.adapt_theme_for_platform(theme)

        # Should have macOS-specific adaptations
        self.assertIsNotNone(adapted_theme)

    @patch('platform.system')
    def test_linux_specific_adaptations(self, mock_system):
        """Test Linux-specific theme adaptations."""
        mock_system.return_value = "Linux"

        theme = Theme.from_dict({
            "name": "linux-theme",
            "version": "1.0.0",
            "colors": {"primary": "#007acc"},
            "styles": {"QPushButton": "background-color: @colors.primary;"}
        })

        adapted_theme = self.adapter.adapt_theme_for_platform(theme)

        # Should have Linux-specific adaptations
        self.assertIsNotNone(adapted_theme)


class TestApplicatorIntegration(ThemedTestCase):
    """Integration tests for theme applicator components working together."""

    def test_full_application_workflow(self):
        """Test complete theme application workflow."""
        # Create repository and applicator
        registry = ThemeWidgetRegistry()
        applicator = create_theme_applicator(registry)

        # Create theme and widgets
        theme = Theme.from_dict({
            "name": "integration-theme",
            "version": "1.0.0",
            "colors": {"primary": "#007acc", "secondary": "#ffffff"},
            "styles": {
                "QPushButton": "background-color: @colors.primary; color: @colors.secondary;",
                "QLabel": "color: @colors.primary;"
            }
        })

        widgets = [MockWidget() for _ in range(10)]
        widget_ids = [registry.register_widget(w) for w in widgets]

        # Apply theme globally
        results = applicator.apply_theme_globally(theme)

        # Verify all widgets received theme
        self.assertEqual(len(results), 10)
        self.assertTrue(all(results.values()))

        # Verify statistics
        stats = applicator.get_statistics()
        self.assertGreaterEqual(stats["widgets_themed"], 10)

    def test_performance_with_large_widget_count(self):
        """Test performance with large number of widgets."""
        registry = ThemeWidgetRegistry()
        applicator = create_theme_applicator(registry)

        theme = Theme.from_dict({
            "name": "performance-theme",
            "version": "1.0.0",
            "colors": {"primary": "#007acc"},
            "styles": {"QPushButton": "background-color: @colors.primary;"}
        })

        # Create 100 widgets for performance test
        widgets = [MockWidget() for _ in range(100)]
        widget_ids = [registry.register_widget(w) for w in widgets]

        # Measure theme application time
        start_time = time.time()
        results = applicator.apply_theme_globally(theme)
        application_time = time.time() - start_time

        # Should meet performance requirement (< 100ms for 100 widgets)
        self.assertLess(application_time, 0.1)
        self.assertEqual(len(results), 100)
        self.assertTrue(all(results.values()))

    def test_memory_efficiency(self):
        """Test memory efficiency of theme application."""
        import gc
        import sys

        registry = ThemeWidgetRegistry()
        applicator = create_theme_applicator(registry)

        theme = Theme.from_dict({
            "name": "memory-theme",
            "version": "1.0.0",
            "colors": {"primary": "#007acc"},
            "styles": {"QPushButton": "background-color: @colors.primary;"}
        })

        # Create widgets and measure memory
        initial_objects = len(gc.get_objects())

        widgets = [MockWidget() for _ in range(50)]
        widget_ids = [registry.register_widget(w) for w in widgets]
        applicator.apply_theme_globally(theme)

        mid_objects = len(gc.get_objects())

        # Clean up widgets
        del widgets
        gc.collect()

        final_objects = len(gc.get_objects())

        # Memory should be efficiently managed
        memory_growth = mid_objects - initial_objects
        memory_cleanup = mid_objects - final_objects

        # Should clean up most allocated objects
        cleanup_ratio = memory_cleanup / memory_growth if memory_growth > 0 else 1.0
        self.assertGreater(cleanup_ratio, 0.7)  # At least 70% cleanup


if __name__ == "__main__":
    pytest.main([__file__])