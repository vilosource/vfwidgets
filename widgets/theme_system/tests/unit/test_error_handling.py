"""
Test suite for error handling and fallback system.

Tests the robust error handling mechanisms that ensure the theme system
never crashes applications. Validates that all error scenarios have
appropriate fallbacks and recovery mechanisms.

Test Coverage:
- Extended exception hierarchy
- Fallback theme mechanism
- Logging infrastructure
- Error recovery strategies
- Performance requirements for error handling
"""

import logging
import threading
import time
import unittest
from io import StringIO
from unittest.mock import Mock, patch

# Import modules under test
from src.vfwidgets_theme.errors import (
    # Error recovery
    InvalidThemeFormatError,
    PropertyNotFoundError,
    # Exception hierarchy
    ThemeError,
    ThemeLoadError,
    ThemeNotFoundError,
    ThemeSystemNotInitializedError,
    create_error_recovery_manager,
)
from src.vfwidgets_theme.fallbacks import (
    # Fallback theme system
    MINIMAL_THEME,
    FallbackColorSystem,
    create_fallback_color_system,
    get_fallback_color,
    get_fallback_property,
    get_fallback_theme,
)
from src.vfwidgets_theme.logging import (
    # Logging infrastructure
    ThemeLogger,
    create_theme_logger,
    get_performance_logger,
    log_performance_warning,
    log_theme_error,
)


class TestExceptionHierarchy(unittest.TestCase):
    """Test the extended exception hierarchy."""

    def test_theme_error_base_class(self):
        """Test ThemeError is proper base class."""
        # All custom exceptions should inherit from ThemeError
        self.assertTrue(issubclass(ThemeNotFoundError, ThemeError))
        self.assertTrue(issubclass(ThemeLoadError, ThemeError))
        self.assertTrue(issubclass(PropertyNotFoundError, ThemeError))
        self.assertTrue(issubclass(InvalidThemeFormatError, ThemeError))
        self.assertTrue(issubclass(ThemeSystemNotInitializedError, ThemeError))

    def test_theme_not_found_error(self):
        """Test ThemeNotFoundError functionality."""
        error = ThemeNotFoundError("dark-mode")
        self.assertIn("dark-mode", str(error))
        self.assertIsInstance(error, ThemeError)

        # Should contain theme name in message
        error_with_message = ThemeNotFoundError("invalid-theme", "Custom message")
        self.assertIn("Custom message", str(error_with_message))

    def test_theme_load_error(self):
        """Test ThemeLoadError functionality."""
        error = ThemeLoadError("Failed to parse theme.json: invalid JSON")
        self.assertIn("theme.json", str(error))
        self.assertIsInstance(error, ThemeError)

    def test_property_not_found_error(self):
        """Test PropertyNotFoundError functionality."""
        error = PropertyNotFoundError("primary_color")
        self.assertIn("primary_color", str(error))
        self.assertIsInstance(error, ThemeError)

    def test_invalid_theme_format_error(self):
        """Test InvalidThemeFormatError functionality."""
        error = InvalidThemeFormatError("Missing required field: colors")
        self.assertIn("colors", str(error))
        self.assertIsInstance(error, ThemeError)

    def test_theme_system_not_initialized_error(self):
        """Test ThemeSystemNotInitializedError functionality."""
        error = ThemeSystemNotInitializedError()
        self.assertIn("not initialized", str(error).lower())
        self.assertIsInstance(error, ThemeError)


class TestFallbackThemeMechanism(unittest.TestCase):
    """Test the fallback theme mechanism."""

    def test_minimal_theme_structure(self):
        """Test MINIMAL_THEME has required structure."""
        # Must have essential properties
        self.assertIn("colors", MINIMAL_THEME)
        self.assertIn("fonts", MINIMAL_THEME)
        self.assertIn("spacing", MINIMAL_THEME)

        # Colors must have basic values
        colors = MINIMAL_THEME["colors"]
        self.assertIn("primary", colors)
        self.assertIn("background", colors)
        self.assertIn("text", colors)
        self.assertIn("border", colors)

        # Must be valid color values
        for color_value in colors.values():
            self.assertIsInstance(color_value, str)
            # Should be hex colors
            if color_value.startswith("#"):
                self.assertTrue(len(color_value) in [4, 7, 9])  # #rgb, #rrggbb, or #rrggbbaa

    def test_minimal_theme_always_works(self):
        """Test MINIMAL_THEME provides all essential properties."""
        # Should never be empty
        self.assertGreater(len(MINIMAL_THEME), 0)

        # Should have safe defaults for all critical properties
        self.assertIsInstance(MINIMAL_THEME["colors"]["primary"], str)
        self.assertIsInstance(MINIMAL_THEME["colors"]["background"], str)
        self.assertIsInstance(MINIMAL_THEME["fonts"]["default"], str)
        self.assertIsInstance(MINIMAL_THEME["spacing"]["default"], int)

    def test_fallback_color_system_creation(self):
        """Test FallbackColorSystem creation and basic functionality."""
        color_system = create_fallback_color_system()
        self.assertIsInstance(color_system, FallbackColorSystem)

        # Should provide fallback colors
        primary = color_system.get_color("primary")
        self.assertIsInstance(primary, str)
        self.assertTrue(primary.startswith("#"))

        # Should handle missing colors gracefully
        unknown_color = color_system.get_color("unknown_color_that_doesnt_exist")
        self.assertIsInstance(unknown_color, str)
        self.assertTrue(unknown_color.startswith("#"))

    def test_get_fallback_theme(self):
        """Test get_fallback_theme function."""
        theme = get_fallback_theme()

        # Should return valid theme data
        self.assertIsInstance(theme, dict)
        self.assertIn("colors", theme)

        # Should be the minimal theme
        self.assertEqual(theme, MINIMAL_THEME)

    def test_get_fallback_color(self):
        """Test get_fallback_color function."""
        # Should return valid colors for known keys
        primary = get_fallback_color("primary")
        self.assertIsInstance(primary, str)
        self.assertTrue(primary.startswith("#"))

        # Should return fallback for unknown keys
        unknown = get_fallback_color("completely_unknown_color")
        self.assertIsInstance(unknown, str)
        self.assertTrue(unknown.startswith("#"))

        # Performance test: < 100μs
        start_time = time.perf_counter()
        for _ in range(1000):
            get_fallback_color("primary")
        end_time = time.perf_counter()
        avg_time = (end_time - start_time) / 1000
        self.assertLess(avg_time, 0.0001, "Fallback color resolution too slow")

    def test_get_fallback_property(self):
        """Test get_fallback_property function."""
        # Should return valid properties for known keys
        font_size = get_fallback_property("fonts.size")
        self.assertIsNotNone(font_size)

        # Should return None for unknown keys
        unknown = get_fallback_property("completely_unknown_property")
        self.assertIsNone(unknown)

        # Should handle nested properties
        primary_color = get_fallback_property("colors.primary")
        self.assertIsInstance(primary_color, str)


class TestLoggingInfrastructure(unittest.TestCase):
    """Test the logging infrastructure."""

    def setUp(self):
        """Set up test fixtures."""
        # Capture log output for testing
        self.log_stream = StringIO()
        self.test_handler = logging.StreamHandler(self.log_stream)

    def test_theme_logger_creation(self):
        """Test ThemeLogger creation and configuration."""
        logger = create_theme_logger("test_component")
        self.assertIsInstance(logger, ThemeLogger)

        # Should have proper name
        self.assertEqual(logger.logger.name, "vftheme.test_component")

        # Should support different log levels
        self.assertTrue(hasattr(logger, "debug"))
        self.assertTrue(hasattr(logger, "info"))
        self.assertTrue(hasattr(logger, "warning"))
        self.assertTrue(hasattr(logger, "error"))

    def test_structured_logging(self):
        """Test structured logging with proper formatting."""
        logger = create_theme_logger("test")

        # Clear existing handlers and add our test handler
        logger.logger.handlers.clear()
        logger.logger.addHandler(self.test_handler)
        logger.logger.setLevel(logging.DEBUG)

        # Test structured log entry
        logger.error(
            "Theme loading failed",
            extra={"theme_name": "dark-mode", "error_type": "ThemeLoadError"},
        )

        log_output = self.log_stream.getvalue()
        self.assertIn("Theme loading failed", log_output)
        # Note: The extra data might be in the log record but not necessarily in the formatted output

    def test_performance_logging(self):
        """Test performance-specific logging."""
        perf_logger = get_performance_logger()
        self.assertIsInstance(perf_logger, ThemeLogger)

        # Should log slow operations
        perf_logger.logger.handlers.clear()
        perf_logger.logger.addHandler(self.test_handler)
        perf_logger.logger.setLevel(logging.DEBUG)

        log_performance_warning("Theme switch took too long", 150.5)

        log_output = self.log_stream.getvalue()
        self.assertIn("took too long", log_output)

    def test_log_theme_error(self):
        """Test theme error logging helper."""
        logger = create_theme_logger("test")
        logger.logger.handlers.clear()
        logger.logger.addHandler(self.test_handler)
        logger.logger.setLevel(logging.DEBUG)

        error = ThemeNotFoundError("missing-theme")
        log_theme_error(logger, error, context={"widget": "Button"})

        log_output = self.log_stream.getvalue()
        self.assertIn("ThemeNotFoundError", log_output)

    def test_debug_mode_logging(self):
        """Test debug mode provides detailed logging."""
        logger = create_theme_logger("test", debug=True)
        logger.logger.handlers.clear()
        logger.logger.addHandler(self.test_handler)

        logger.debug("Debug message with details", extra={"property": "color"})

        log_output = self.log_stream.getvalue()
        # In debug mode, should include detailed information
        self.assertIn("Debug message", log_output)


class TestErrorRecoveryStrategies(unittest.TestCase):
    """Test error recovery strategies."""

    def setUp(self):
        """Set up error recovery manager."""
        self.recovery_manager = create_error_recovery_manager()

    def test_automatic_fallback_to_minimal_theme(self):
        """Test automatic fallback when theme loading fails."""
        # Simulate theme load failure
        error = ThemeLoadError("Corrupted theme file")

        recovered_theme = self.recovery_manager.recover_from_error(error, operation="load_theme")

        # Should return minimal theme
        self.assertEqual(recovered_theme, MINIMAL_THEME)

    def test_property_level_fallbacks(self):
        """Test property-level fallback resolution."""
        # Simulate missing property
        error = PropertyNotFoundError("custom_border_color")

        recovered_value = self.recovery_manager.recover_from_error(
            error, operation="get_property", context={"property_key": "custom_border_color"}
        )

        # Should return fallback color
        self.assertIsInstance(recovered_value, str)
        self.assertTrue(recovered_value.startswith("#"))

    def test_silent_recovery_with_logging(self):
        """Test that recovery is silent but logged."""
        with patch("vfwidgets_theme.logging.get_performance_logger") as mock_logger:
            mock_logger_instance = Mock()
            mock_logger.return_value = mock_logger_instance

            error = ThemeNotFoundError("missing-theme")
            self.recovery_manager.recover_from_error(error, operation="switch_theme")

            # Should have logged the error
            mock_logger_instance.warning.assert_called()

    def test_user_notification_for_critical_issues(self):
        """Test user notification system for critical errors."""
        critical_error = ThemeSystemNotInitializedError()

        with patch("vfwidgets_theme.errors.notify_user") as mock_notify:
            self.recovery_manager.recover_from_error(
                critical_error, operation="initialize_theme_system", notify_user=True
            )

            # Should notify user for critical errors
            mock_notify.assert_called_once()

    def test_error_recovery_performance(self):
        """Test error recovery meets performance requirements."""
        error = PropertyNotFoundError("test_property")

        # Performance test: < 1ms overhead
        start_time = time.perf_counter()
        for _ in range(1000):
            self.recovery_manager.recover_from_error(error, operation="get_property")
        end_time = time.perf_counter()

        avg_time = (end_time - start_time) / 1000
        self.assertLess(avg_time, 0.001, "Error handling too slow")

    def test_thread_safe_error_handling(self):
        """Test error handling is thread-safe."""
        results = []
        errors = []

        def worker():
            try:
                error = ThemeLoadError("Thread test error")
                result = self.recovery_manager.recover_from_error(error, operation="load_theme")
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Run multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # Should have no errors and correct results
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(results), 10)

        # All results should be the minimal theme
        for result in results:
            self.assertEqual(result, MINIMAL_THEME)

    def test_graceful_degradation(self):
        """Test graceful degradation strategies."""
        # Test partial theme application
        corrupted_theme = {"colors": {"primary": "#invalid"}}

        result = self.recovery_manager.apply_graceful_degradation(corrupted_theme, "apply_theme")

        # Should fix invalid colors
        self.assertNotEqual(result["colors"]["primary"], "#invalid")
        self.assertTrue(result["colors"]["primary"].startswith("#"))

        # Should preserve valid parts
        self.assertIn("colors", result)

    def test_zero_memory_leaks_in_error_paths(self):
        """Test no memory leaks in error handling paths."""
        import gc

        # Get initial object count
        gc.collect()
        initial_objects = len(gc.get_objects())

        # Generate many errors and recoveries
        for i in range(100):
            error = ThemeLoadError(f"Test error {i}")
            self.recovery_manager.recover_from_error(error, operation="test")

        # Force garbage collection
        gc.collect()
        final_objects = len(gc.get_objects())

        # Should not have significant object growth
        object_growth = final_objects - initial_objects
        self.assertLess(object_growth, 50, f"Potential memory leak: {object_growth} objects")


class TestErrorHandlingIntegration(unittest.TestCase):
    """Integration tests for complete error handling system."""

    def test_end_to_end_error_recovery(self):
        """Test complete error recovery workflow."""
        # Simulate complete system failure
        with patch("vfwidgets_theme.fallbacks.get_fallback_theme") as mock_fallback:
            mock_fallback.return_value = MINIMAL_THEME

            # Create error recovery manager
            recovery_manager = create_error_recovery_manager()

            # Simulate theme system failure
            error = ThemeSystemNotInitializedError()
            result = recovery_manager.recover_from_error(
                error, operation="get_theme", fallback_data=None
            )

            # Should return working theme
            self.assertIsNotNone(result)
            mock_fallback.assert_called_once()

    def test_error_cascading_prevention(self):
        """Test that errors don't cascade through the system."""
        recovery_manager = create_error_recovery_manager()

        # Simulate multiple cascading errors
        errors = [
            ThemeLoadError("Primary theme failed"),
            ThemeLoadError("Fallback theme failed"),
            PropertyNotFoundError("Fallback property missing"),
        ]

        # Should handle cascading errors without crashing
        for error in errors:
            result = recovery_manager.recover_from_error(error, operation="cascade_test")
            # Should always get a valid result
            self.assertIsNotNone(result)

    def test_error_reporting_integration(self):
        """Test integration with logging and reporting systems."""
        with patch("vfwidgets_theme.logging.create_theme_logger") as mock_logger_factory:
            mock_logger = Mock()
            mock_logger_factory.return_value = mock_logger

            recovery_manager = create_error_recovery_manager()
            error = InvalidThemeFormatError("Bad format")

            recovery_manager.recover_from_error(error, operation="validate_theme", log_error=True)

            # Should have logged the error
            mock_logger.error.assert_called()


if __name__ == "__main__":
    unittest.main()
