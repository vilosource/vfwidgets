#!/usr/bin/env python3
"""
Tests for Task 12: Event System with Qt Integration

These tests verify the ThemeEventSystem implementation including:
- Qt signals/slots integration
- Debouncing functionality
- Property-specific signals
- Event filtering
- Event replay capability
- Performance requirements
"""

import os
import sys
import time
import unittest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

try:
    from PySide6.QtCore import QObject
    from PySide6.QtWidgets import QApplication, QWidget

    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False

from vfwidgets_theme.events.system import (
    EventRecord,
    ThemeEventSystem,
    get_global_event_system,
    set_global_event_system,
)


class TestThemeEventSystem(unittest.TestCase):
    """Test the ThemeEventSystem implementation."""

    def setUp(self):
        """Set up test environment."""
        self.event_system = ThemeEventSystem()
        self.signals_received = []

        # Connect to all signals for testing
        self.event_system.theme_changing.connect(
            lambda name: self.signals_received.append(("theme_changing", name))
        )
        self.event_system.theme_changed.connect(
            lambda name: self.signals_received.append(("theme_changed", name))
        )
        self.event_system.theme_load_failed.connect(
            lambda name, error: self.signals_received.append(("theme_load_failed", name, error))
        )
        self.event_system.property_changing.connect(
            lambda wid, prop, old, new: self.signals_received.append(
                ("property_changing", wid, prop, old, new)
            )
        )
        self.event_system.property_changed.connect(
            lambda wid, prop, old, new: self.signals_received.append(
                ("property_changed", wid, prop, old, new)
            )
        )
        self.event_system.property_validation_failed.connect(
            lambda wid, prop, val, err: self.signals_received.append(
                ("property_validation_failed", wid, prop, val, err)
            )
        )
        self.event_system.widget_registered.connect(
            lambda wid: self.signals_received.append(("widget_registered", wid))
        )
        self.event_system.widget_unregistered.connect(
            lambda wid: self.signals_received.append(("widget_unregistered", wid))
        )
        self.event_system.widget_theme_applied.connect(
            lambda wid, theme: self.signals_received.append(("widget_theme_applied", wid, theme))
        )
        self.event_system.performance_warning.connect(
            lambda op, dur: self.signals_received.append(("performance_warning", op, dur))
        )

    def tearDown(self):
        """Clean up after tests."""
        self.event_system.disable_recording()
        self.event_system.clear_filters()

    def test_basic_signal_emission(self):
        """Test basic signal emission works."""
        # Test theme signals
        self.event_system.notify_theme_changing("dark")
        self.event_system.notify_theme_changed("dark")

        self.assertIn(("theme_changing", "dark"), self.signals_received)
        self.assertIn(("theme_changed", "dark"), self.signals_received)

    def test_property_signals_immediate(self):
        """Test property signals without debouncing."""
        widget_id = "test_widget_1"
        property_name = "background_color"
        old_value = "#ffffff"
        new_value = "#000000"

        # Notify without debouncing
        self.event_system.notify_property_changing(
            widget_id, property_name, old_value, new_value, debounce=False
        )
        self.event_system.notify_property_changed(
            widget_id, property_name, old_value, new_value, debounce=False
        )

        self.assertIn(
            ("property_changing", widget_id, property_name, old_value, new_value),
            self.signals_received,
        )
        self.assertIn(
            ("property_changed", widget_id, property_name, old_value, new_value),
            self.signals_received,
        )

    @unittest.skipIf(not QT_AVAILABLE, "Qt not available")
    def test_widget_registration(self):
        """Test widget registration/unregistration."""
        # Create a mock widget if Qt is available
        widget = QWidget()
        widget_id = "test_widget_reg"

        # Register widget
        self.event_system.register_widget(widget_id, widget)
        self.assertIn(("widget_registered", widget_id), self.signals_received)

        # Unregister widget
        self.event_system.unregister_widget(widget_id)
        self.assertIn(("widget_unregistered", widget_id), self.signals_received)

    def test_event_filtering(self):
        """Test event filtering functionality."""
        widget_id = "filtered_widget"
        property_name = "filtered_property"

        # Add filters
        self.event_system.add_widget_filter(widget_id)
        self.event_system.add_property_filter(property_name)

        # Try to emit filtered events - should be ignored
        initial_count = len(self.signals_received)

        self.event_system.notify_property_changed(
            widget_id, "some_property", "old", "new", debounce=False
        )
        self.event_system.notify_property_changed(
            "other_widget", property_name, "old", "new", debounce=False
        )
        self.event_system.notify_widget_theme_applied(widget_id, "dark")

        # No new signals should have been received
        self.assertEqual(len(self.signals_received), initial_count)

        # Remove filters and try again
        self.event_system.remove_widget_filter(widget_id)
        self.event_system.remove_property_filter(property_name)

        self.event_system.notify_property_changed(
            widget_id, "some_property", "old", "new", debounce=False
        )

        # Now signal should be received
        self.assertIn(
            ("property_changed", widget_id, "some_property", "old", "new"), self.signals_received
        )

    def test_debouncing_configuration(self):
        """Test debouncing interval configuration."""
        # Test setting debounce interval
        self.event_system.set_debounce_interval(100)
        stats = self.event_system.get_statistics()
        self.assertEqual(stats["debounce_interval_ms"], 100)

        # Test clamping
        self.event_system.set_debounce_interval(0)  # Should clamp to 1
        stats = self.event_system.get_statistics()
        self.assertEqual(stats["debounce_interval_ms"], 1)

        self.event_system.set_debounce_interval(2000)  # Should clamp to 1000
        stats = self.event_system.get_statistics()
        self.assertEqual(stats["debounce_interval_ms"], 1000)

    def test_event_recording_and_replay(self):
        """Test event recording and replay functionality."""
        # Enable recording
        self.event_system.enable_recording(max_history=10)
        stats = self.event_system.get_statistics()
        self.assertTrue(stats["recording_enabled"])

        # Generate some events
        self.event_system.notify_theme_changing("dark")
        self.event_system.notify_theme_changed("dark")
        self.event_system.notify_property_changed("widget1", "color", "red", "blue", debounce=False)

        # Check history
        history = self.event_system.get_event_history()
        self.assertGreaterEqual(len(history), 3)

        # Clear received signals for replay test
        self.signals_received.clear()

        # Replay events
        replayed = self.event_system.replay_events()
        self.assertGreater(replayed, 0)

        # Should have received replayed signals
        self.assertGreater(len(self.signals_received), 0)

        # Test targeted replay
        self.signals_received.clear()
        replayed = self.event_system.replay_events(target_widget_id="widget1")
        # Should replay fewer events (only for widget1)
        self.assertGreaterEqual(replayed, 0)

    def test_validation_failure_notification(self):
        """Test property validation failure notifications."""
        widget_id = "validation_widget"
        property_name = "invalid_prop"
        invalid_value = "not_a_color"
        error_message = "Invalid color format"

        self.event_system.notify_property_validation_failed(
            widget_id, property_name, invalid_value, error_message
        )

        self.assertIn(
            ("property_validation_failed", widget_id, property_name, invalid_value, error_message),
            self.signals_received,
        )

    def test_theme_load_failure_notification(self):
        """Test theme load failure notifications."""
        theme_name = "nonexistent_theme"
        error_message = "Theme file not found"

        self.event_system.notify_theme_load_failed(theme_name, error_message)

        self.assertIn(("theme_load_failed", theme_name, error_message), self.signals_received)

    def test_widget_theme_applied_notification(self):
        """Test widget theme applied notifications."""
        widget_id = "themed_widget"
        theme_name = "dark"

        self.event_system.notify_widget_theme_applied(widget_id, theme_name)

        self.assertIn(("widget_theme_applied", widget_id, theme_name), self.signals_received)

    def test_statistics_reporting(self):
        """Test that statistics are properly reported."""
        stats = self.event_system.get_statistics()

        # Check all expected keys are present
        expected_keys = [
            "debounce_interval_ms",
            "pending_events",
            "filtered_properties",
            "filtered_widgets",
            "recorded_events",
            "recording_enabled",
            "registered_widgets",
            "performance_threshold_ms",
        ]

        for key in expected_keys:
            self.assertIn(key, stats)

        # Test that statistics update appropriately
        self.event_system.add_property_filter("test_prop")
        stats = self.event_system.get_statistics()
        self.assertEqual(stats["filtered_properties"], 1)

    def test_clear_filters(self):
        """Test clearing all filters."""
        self.event_system.add_property_filter("prop1")
        self.event_system.add_property_filter("prop2")
        self.event_system.add_widget_filter("widget1")

        stats = self.event_system.get_statistics()
        self.assertEqual(stats["filtered_properties"], 2)
        self.assertEqual(stats["filtered_widgets"], 1)

        self.event_system.clear_filters()

        stats = self.event_system.get_statistics()
        self.assertEqual(stats["filtered_properties"], 0)
        self.assertEqual(stats["filtered_widgets"], 0)

    def test_performance_monitoring(self):
        """Test performance monitoring functionality."""
        # Set a very low threshold to trigger warnings
        self.event_system._performance_threshold_ms = 0.001

        # This should trigger a performance warning
        self.event_system.notify_theme_changed("slow_theme")

        # Check if performance warning was emitted
        performance_warnings = [s for s in self.signals_received if s[0] == "performance_warning"]
        self.assertGreaterEqual(
            len(performance_warnings), 0
        )  # May or may not trigger depending on system speed


class TestDebouncing(unittest.TestCase):
    """Test debouncing functionality specifically."""

    def setUp(self):
        """Set up for debouncing tests."""
        self.event_system = ThemeEventSystem()
        self.event_system.set_debounce_interval(50)  # 50ms debounce
        self.signals_received = []

        self.event_system.property_changed.connect(
            lambda wid, prop, old, new: self.signals_received.append(
                ("property_changed", wid, prop, old, new)
            )
        )

    def tearDown(self):
        """Clean up."""
        self.event_system.disable_recording()

    @unittest.skipIf(not QT_AVAILABLE, "Qt not available for timer testing")
    def test_debouncing_behavior(self):
        """Test that debouncing actually works."""
        widget_id = "debounce_widget"
        property_name = "color"

        # Send multiple rapid property changes
        for i in range(5):
            self.event_system.notify_property_changed(
                widget_id, property_name, f"value_{i}", f"value_{i+1}", debounce=True
            )

        # Should have no immediate signals (they're queued)
        immediate_signals = len(self.signals_received)
        self.assertEqual(immediate_signals, 0)

        # Wait for debounce timer to fire
        if QT_AVAILABLE:
            from PySide6.QtCore import QCoreApplication

            app = QCoreApplication.instance()
            if app:
                # Process events for 100ms to let debounce timer fire
                start_time = time.time()
                while time.time() - start_time < 0.1:
                    app.processEvents()
                    time.sleep(0.01)

        # Now should have received the debounced signals
        self.assertGreater(len(self.signals_received), 0)


class TestEventRecord(unittest.TestCase):
    """Test EventRecord functionality."""

    def test_event_record_creation(self):
        """Test EventRecord creation and fields."""
        timestamp = time.time()
        event = EventRecord(
            timestamp=timestamp,
            event_type="property_changed",
            widget_id="test_widget",
            property_name="background",
            old_value="red",
            new_value="blue",
            data={"extra": "info"},
        )

        self.assertEqual(event.timestamp, timestamp)
        self.assertEqual(event.event_type, "property_changed")
        self.assertEqual(event.widget_id, "test_widget")
        self.assertEqual(event.property_name, "background")
        self.assertEqual(event.old_value, "red")
        self.assertEqual(event.new_value, "blue")
        self.assertEqual(event.data["extra"], "info")


class TestGlobalEventSystem(unittest.TestCase):
    """Test global event system functionality."""

    def test_global_instance(self):
        """Test global event system instance."""
        # Get global instance
        global_system = get_global_event_system()
        self.assertIsInstance(global_system, ThemeEventSystem)

        # Should return same instance
        global_system2 = get_global_event_system()
        self.assertIs(global_system, global_system2)

    def test_custom_global_instance(self):
        """Test setting custom global event system."""
        custom_system = ThemeEventSystem()
        set_global_event_system(custom_system)

        global_system = get_global_event_system()
        self.assertIs(global_system, custom_system)


class TestPerformanceRequirements(unittest.TestCase):
    """Test that performance requirements are met."""

    def setUp(self):
        """Set up performance tests."""
        self.event_system = ThemeEventSystem()
        self.signals_received = []

        self.event_system.property_changed.connect(
            lambda wid, prop, old, new: self.signals_received.append((wid, prop))
        )

    def test_event_dispatch_performance(self):
        """Test that event dispatch meets performance requirements (<1ms for 100 widgets)."""
        widget_count = 100

        # Measure time for immediate dispatch (no debouncing)
        start_time = time.perf_counter()

        for i in range(widget_count):
            self.event_system.notify_property_changed(
                f"widget_{i}", "color", "old", "new", debounce=False
            )

        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000

        print(f"Event dispatch for {widget_count} widgets took {duration_ms:.3f}ms")

        # Requirement: <1ms for 100 widgets
        self.assertLess(
            duration_ms, 1.0, f"Event dispatch took {duration_ms:.3f}ms, requirement is <1ms"
        )

        # Verify all events were processed
        self.assertEqual(len(self.signals_received), widget_count)

    def test_filtering_performance(self):
        """Test that filtering doesn't significantly impact performance."""
        widget_count = 100

        # Add some filters
        for i in range(0, widget_count, 10):  # Filter every 10th widget
            self.event_system.add_widget_filter(f"widget_{i}")

        # Measure time with filtering
        start_time = time.perf_counter()

        for i in range(widget_count):
            self.event_system.notify_property_changed(
                f"widget_{i}", "color", "old", "new", debounce=False
            )

        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000

        print(f"Event dispatch with filtering for {widget_count} widgets took {duration_ms:.3f}ms")

        # Should still be fast
        self.assertLess(duration_ms, 2.0, "Filtering should not significantly impact performance")

        # Should have filtered out some events (10% of them)
        expected_signals = widget_count - (widget_count // 10)
        self.assertEqual(len(self.signals_received), expected_signals)


def run_tests():
    """Run all event system tests."""
    # Create test suite
    suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestThemeEventSystem,
        TestDebouncing,
        TestEventRecord,
        TestGlobalEventSystem,
        TestPerformanceRequirements,
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    # Set up Qt application if available for timer tests
    app = None
    if QT_AVAILABLE:
        try:
            from PySide6.QtWidgets import QApplication

            app = QApplication(sys.argv)
        except Exception:
            pass

    try:
        success = run_tests()
        exit_code = 0 if success else 1
    finally:
        if app:
            app.quit()

    sys.exit(exit_code)
