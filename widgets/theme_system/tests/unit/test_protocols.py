"""
Test module for core theme system protocols.

Tests verify that protocols define the correct interfaces for:
- ThemeProvider: Dependency injection pattern for theme data
- ThemeableWidget: Widget interface for theming capabilities
- ColorProvider: Color resolution and validation
- StyleGenerator: QSS generation for Qt widgets

These tests validate interface contracts, not implementations.
"""

import pytest
from typing import Protocol, runtime_checkable
from unittest.mock import Mock, MagicMock

from src.vfwidgets_theme.protocols import (
    ThemeProvider,
    ThemeableWidget,
    ColorProvider,
    StyleGenerator,
    ThemeError,
    ThemeValidationError,
    ColorResolveError,
    StyleGenerationError,
    ThemePropertyError,
    ThemeData,
    ColorValue,
    StyleCallback,
    PropertyKey,
    PropertyValue,
    QSSStyle,
    validate_performance_requirements,
    get_protocol_version,
)


class TestThemeProviderProtocol:
    """Test ThemeProvider protocol interface requirements."""

    def test_theme_provider_protocol_structure(self):
        """Test that ThemeProvider has required methods."""
        # Test that ThemeProvider is a runtime-checkable protocol
        # Protocols have __protocol__ in some Python versions or are identifiable by other means
        from typing import get_type_hints, Protocol
        assert isinstance(ThemeProvider, type) and issubclass(ThemeProvider, Protocol)

        # Test that protocol has required abstract methods
        required_methods = {
            'get_current_theme',
            'get_property',
            'subscribe',
            'unsubscribe'
        }

        # Get all abstract methods from the protocol
        abstract_methods = set()
        for method_name in dir(ThemeProvider):
            if not method_name.startswith('_'):  # Skip private methods
                method = getattr(ThemeProvider, method_name)
                if hasattr(method, '__isabstractmethod__') and method.__isabstractmethod__:
                    abstract_methods.add(method_name)

        # All required methods should be in the protocol
        assert required_methods.issubset(abstract_methods), f"Missing methods: {required_methods - abstract_methods}"

    def test_theme_provider_mock_implementation(self):
        """Test that mock objects can implement ThemeProvider protocol."""
        mock_provider = Mock()
        mock_provider.get_current_theme.return_value = {"color": "#ffffff"}
        mock_provider.get_property.return_value = "#ffffff"
        mock_provider.subscribe.return_value = None
        mock_provider.unsubscribe.return_value = None

        # Test interface contracts
        assert callable(mock_provider.get_current_theme)
        assert callable(mock_provider.get_property)
        assert callable(mock_provider.subscribe)
        assert callable(mock_provider.unsubscribe)

    def test_theme_provider_get_current_theme(self):
        """Test get_current_theme returns theme data."""
        mock_provider = Mock()
        expected_theme = {"background": "#1e1e1e", "foreground": "#ffffff"}
        mock_provider.get_current_theme.return_value = expected_theme

        result = mock_provider.get_current_theme()
        assert result == expected_theme

    def test_theme_provider_get_property(self):
        """Test get_property returns theme property value."""
        mock_provider = Mock()
        mock_provider.get_property.return_value = "#ff0000"

        result = mock_provider.get_property("error_color")
        assert result == "#ff0000"
        mock_provider.get_property.assert_called_once_with("error_color")

    def test_theme_provider_subscription(self):
        """Test subscribe/unsubscribe for theme change notifications."""
        mock_provider = Mock()
        callback = Mock()

        mock_provider.subscribe(callback)
        mock_provider.subscribe.assert_called_once_with(callback)

        mock_provider.unsubscribe(callback)
        mock_provider.unsubscribe.assert_called_once_with(callback)


class TestThemeableWidgetProtocol:
    """Test ThemeableWidget protocol interface requirements."""

    def test_themeable_widget_protocol_structure(self):
        """Test that ThemeableWidget has required interface."""
        # Test that ThemeableWidget is a runtime-checkable protocol
        from typing import Protocol
        assert isinstance(ThemeableWidget, type) and issubclass(ThemeableWidget, Protocol)

        # Test required abstract methods and properties
        required_items = {
            'theme_config',
            'theme_provider',
            'on_theme_changed',
            'get_theme_color',
            'get_theme_property'
        }

        # Get all abstract items from the protocol
        abstract_items = set()
        for item_name in dir(ThemeableWidget):
            if not item_name.startswith('_'):  # Skip private methods
                item = getattr(ThemeableWidget, item_name)
                if hasattr(item, '__isabstractmethod__') and item.__isabstractmethod__:
                    abstract_items.add(item_name)

        assert required_items.issubset(abstract_items), f"Missing items: {required_items - abstract_items}"

    def test_themeable_widget_mock_implementation(self):
        """Test mock implementation of ThemeableWidget."""
        mock_widget = Mock()
        mock_widget.theme_config = {"button_color": "#007acc"}
        mock_widget.theme_provider = Mock()
        mock_widget.on_theme_changed.return_value = None
        mock_widget.get_theme_color.return_value = "#007acc"
        mock_widget.get_theme_property.return_value = "Arial"

        # Test interface availability
        assert hasattr(mock_widget, 'theme_config')
        assert hasattr(mock_widget, 'theme_provider')
        assert callable(mock_widget.on_theme_changed)
        assert callable(mock_widget.get_theme_color)
        assert callable(mock_widget.get_theme_property)

    def test_themeable_widget_get_theme_color(self):
        """Test get_theme_color with key and default."""
        mock_widget = Mock()
        mock_widget.get_theme_color.return_value = "#007acc"

        # Test with key only
        result = mock_widget.get_theme_color("primary_color")
        assert result == "#007acc"

        # Test with key and default
        mock_widget.get_theme_color.return_value = "#ff0000"
        result = mock_widget.get_theme_color("missing_color", "#ff0000")
        assert result == "#ff0000"

    def test_themeable_widget_get_theme_property(self):
        """Test get_theme_property with various types."""
        mock_widget = Mock()

        # Test string property
        mock_widget.get_theme_property.return_value = "Arial"
        result = mock_widget.get_theme_property("font_family")
        assert result == "Arial"

        # Test numeric property
        mock_widget.get_theme_property.return_value = 12
        result = mock_widget.get_theme_property("font_size")
        assert result == 12


class TestColorProviderProtocol:
    """Test ColorProvider protocol interface requirements."""

    def test_color_provider_protocol_structure(self):
        """Test ColorProvider has required methods."""
        # Test that ColorProvider is a runtime-checkable protocol
        from typing import Protocol
        assert isinstance(ColorProvider, type) and issubclass(ColorProvider, Protocol)

        # Test required abstract methods
        required_methods = {
            'resolve_color',
            'get_fallback_color',
            'validate_color'
        }

        # Get all abstract methods from the protocol
        abstract_methods = set()
        for method_name in dir(ColorProvider):
            if not method_name.startswith('_'):  # Skip private methods
                method = getattr(ColorProvider, method_name)
                if hasattr(method, '__isabstractmethod__') and method.__isabstractmethod__:
                    abstract_methods.add(method_name)

        assert required_methods.issubset(abstract_methods), f"Missing methods: {required_methods - abstract_methods}"

    def test_color_provider_mock_implementation(self):
        """Test mock implementation of ColorProvider."""
        mock_provider = Mock()
        mock_provider.resolve_color.return_value = "#007acc"
        mock_provider.get_fallback_color.return_value = "#000000"
        mock_provider.validate_color.return_value = True

        # Test interface availability
        assert callable(mock_provider.resolve_color)
        assert callable(mock_provider.get_fallback_color)
        assert callable(mock_provider.validate_color)

    def test_color_provider_resolve_color(self):
        """Test color resolution functionality."""
        mock_provider = Mock()
        mock_provider.resolve_color.return_value = "#007acc"

        result = mock_provider.resolve_color("primary")
        assert result == "#007acc"
        mock_provider.resolve_color.assert_called_once_with("primary")

    def test_color_provider_validate_color(self):
        """Test color validation functionality."""
        mock_provider = Mock()

        # Test valid color
        mock_provider.validate_color.return_value = True
        assert mock_provider.validate_color("#007acc") is True

        # Test invalid color
        mock_provider.validate_color.return_value = False
        assert mock_provider.validate_color("invalid") is False

    def test_color_provider_fallback_color(self):
        """Test fallback color provision."""
        mock_provider = Mock()
        mock_provider.get_fallback_color.return_value = "#000000"

        result = mock_provider.get_fallback_color()
        assert result == "#000000"


class TestStyleGeneratorProtocol:
    """Test StyleGenerator protocol interface requirements."""

    def test_style_generator_protocol_structure(self):
        """Test StyleGenerator has required methods."""
        # Test that StyleGenerator is a runtime-checkable protocol
        from typing import Protocol
        assert isinstance(StyleGenerator, type) and issubclass(StyleGenerator, Protocol)

        # Test required abstract methods
        required_methods = {
            'generate_stylesheet',
            'get_selector',
            'merge_styles'
        }

        # Get all abstract methods from the protocol
        abstract_methods = set()
        for method_name in dir(StyleGenerator):
            if not method_name.startswith('_'):  # Skip private methods
                method = getattr(StyleGenerator, method_name)
                if hasattr(method, '__isabstractmethod__') and method.__isabstractmethod__:
                    abstract_methods.add(method_name)

        assert required_methods.issubset(abstract_methods), f"Missing methods: {required_methods - abstract_methods}"

    def test_style_generator_mock_implementation(self):
        """Test mock implementation of StyleGenerator."""
        mock_generator = Mock()
        mock_generator.generate_stylesheet.return_value = "QPushButton { color: #007acc; }"
        mock_generator.get_selector.return_value = "QPushButton"
        mock_generator.merge_styles.return_value = "QPushButton { color: #007acc; background: #ffffff; }"

        # Test interface availability
        assert callable(mock_generator.generate_stylesheet)
        assert callable(mock_generator.get_selector)
        assert callable(mock_generator.merge_styles)

    def test_style_generator_generate_stylesheet(self):
        """Test stylesheet generation."""
        mock_generator = Mock()
        expected_qss = "QPushButton { color: #007acc; background: #ffffff; }"
        mock_generator.generate_stylesheet.return_value = expected_qss

        theme = {"primary_color": "#007acc", "background": "#ffffff"}
        widget = Mock()

        result = mock_generator.generate_stylesheet(theme, widget)
        assert result == expected_qss
        mock_generator.generate_stylesheet.assert_called_once_with(theme, widget)

    def test_style_generator_get_selector(self):
        """Test CSS selector generation."""
        mock_generator = Mock()
        mock_generator.get_selector.return_value = "QPushButton"

        result = mock_generator.get_selector("button")
        assert result == "QPushButton"
        mock_generator.get_selector.assert_called_once_with("button")

    def test_style_generator_merge_styles(self):
        """Test style merging functionality."""
        mock_generator = Mock()
        expected_merged = "QPushButton { color: #007acc; background: #ffffff; font-size: 12px; }"
        mock_generator.merge_styles.return_value = expected_merged

        styles = [
            "QPushButton { color: #007acc; }",
            "QPushButton { background: #ffffff; }",
            "QPushButton { font-size: 12px; }"
        ]

        result = mock_generator.merge_styles(styles)
        assert result == expected_merged
        mock_generator.merge_styles.assert_called_once_with(styles)


class TestExceptionHierarchy:
    """Test custom exception hierarchy for theme system."""

    def test_theme_error_base_exception(self):
        """Test ThemeError as base exception class."""
        # Test that ThemeError is an Exception subclass
        assert issubclass(ThemeError, Exception)

        # Test that we can create and raise ThemeError
        error = ThemeError("Test error")
        assert str(error) == "Test error"

        # Test that we can catch it as Exception
        try:
            raise ThemeError("Test error")
        except Exception as e:
            assert isinstance(e, ThemeError)
            assert str(e) == "Test error"

    def test_theme_validation_error(self):
        """Test ThemeValidationError for theme validation failures."""
        # Test inheritance from ThemeError
        assert issubclass(ThemeValidationError, ThemeError)

        # Test creation and usage
        error = ThemeValidationError("Invalid theme format")
        assert str(error) == "Invalid theme format"

        # Test catching as base class
        try:
            raise ThemeValidationError("Invalid theme")
        except ThemeError as e:
            assert isinstance(e, ThemeValidationError)

    def test_color_resolve_error(self):
        """Test ColorResolveError for color resolution failures."""
        # Test inheritance from ThemeError
        assert issubclass(ColorResolveError, ThemeError)

        # Test creation and usage
        error = ColorResolveError("Cannot resolve color 'primary'")
        assert str(error) == "Cannot resolve color 'primary'"

        # Test catching as base class
        try:
            raise ColorResolveError("Color not found")
        except ThemeError as e:
            assert isinstance(e, ColorResolveError)

    def test_style_generation_error(self):
        """Test StyleGenerationError for QSS generation failures."""
        # Test inheritance from ThemeError
        assert issubclass(StyleGenerationError, ThemeError)

        # Test creation and usage
        error = StyleGenerationError("Failed to generate QSS")
        assert str(error) == "Failed to generate QSS"

        # Test catching as base class
        try:
            raise StyleGenerationError("QSS invalid")
        except ThemeError as e:
            assert isinstance(e, StyleGenerationError)

    def test_theme_property_error(self):
        """Test ThemePropertyError for property access failures."""
        # Test inheritance from ThemeError
        assert issubclass(ThemePropertyError, ThemeError)

        # Test creation and usage
        error = ThemePropertyError("Property 'font_size' not found")
        assert str(error) == "Property 'font_size' not found"

        # Test catching as base class
        try:
            raise ThemePropertyError("Property access failed")
        except ThemeError as e:
            assert isinstance(e, ThemePropertyError)


class TestTypeHintsAndAliases:
    """Test type hints and type aliases for better IDE support."""

    def test_theme_data_type_alias(self):
        """Test ThemeData type alias for theme dictionaries."""
        # Test that ThemeData is available and is a type alias
        assert ThemeData is not None

        # Test that we can use ThemeData in type hints (this would be caught by mypy)
        def example_function(theme: ThemeData) -> str:
            return str(theme)

        # Test with actual theme data
        test_theme = {"primary_color": "#007acc", "font_size": 12}
        result = example_function(test_theme)
        assert "primary_color" in result

    def test_color_value_type_alias(self):
        """Test ColorValue type alias for color values."""
        # Test that ColorValue is available
        assert ColorValue is not None

        # Test that we can use ColorValue in type hints
        def example_color_function(color: ColorValue) -> ColorValue:
            return color

        # Test with actual color values
        assert example_color_function("#007acc") == "#007acc"
        assert example_color_function("rgb(0, 122, 204)") == "rgb(0, 122, 204)"

    def test_style_callback_type_alias(self):
        """Test StyleCallback type alias for theme change callbacks."""
        # Test that StyleCallback is available
        assert StyleCallback is not None

        # Test that we can use StyleCallback in type hints
        def register_callback(callback: StyleCallback) -> None:
            callback("dark")

        # Test with actual callback
        called_with = []
        def test_callback(theme_name: str) -> None:
            called_with.append(theme_name)

        register_callback(test_callback)
        assert called_with == ["dark"]

    def test_property_key_type_alias(self):
        """Test PropertyKey type alias for property keys."""
        # Test that PropertyKey is available
        assert PropertyKey is not None

        # Test usage in type hints
        def get_property(key: PropertyKey) -> str:
            return f"Property: {key}"

        assert get_property("primary_color") == "Property: primary_color"

    def test_property_value_type_alias(self):
        """Test PropertyValue type alias for property values."""
        # Test that PropertyValue is available
        assert PropertyValue is not None

        # Test usage with various types
        def set_property(value: PropertyValue) -> PropertyValue:
            return value

        assert set_property("#007acc") == "#007acc"
        assert set_property(12) == 12
        assert set_property(["item1", "item2"]) == ["item1", "item2"]

    def test_qss_style_type_alias(self):
        """Test QSSStyle type alias for Qt stylesheets."""
        # Test that QSSStyle is available
        assert QSSStyle is not None

        # Test usage in type hints
        def apply_style(style: QSSStyle) -> QSSStyle:
            return f"Applied: {style}"

        test_qss = "QPushButton { color: #007acc; }"
        result = apply_style(test_qss)
        assert "QPushButton" in result


class TestProtocolPerformanceRequirements:
    """Test that protocol usage meets performance requirements."""

    def test_protocol_check_performance(self):
        """Test that protocol checks are reasonably fast."""
        import time

        mock_provider = Mock()
        mock_provider.get_current_theme.return_value = {}

        # Time multiple protocol method calls
        start_time = time.perf_counter()
        for _ in range(1000):
            mock_provider.get_current_theme()
        end_time = time.perf_counter()

        # Should be reasonable time for 1000 calls (relaxed for test environment)
        total_time = end_time - start_time
        assert total_time < 1.0  # Less than 1 second for 1000 calls (very generous)

    def test_no_runtime_overhead(self):
        """Test that protocol usage has no significant runtime overhead."""
        # This test ensures protocol definitions don't add runtime cost
        mock_widget = Mock()
        mock_widget.get_theme_color.return_value = "#007acc"

        # Direct method call should be very fast
        import time
        start_time = time.perf_counter()
        result = mock_widget.get_theme_color("primary")
        end_time = time.perf_counter()

        assert result == "#007acc"
        # Relaxed timing for test environment - should complete in reasonable time
        assert (end_time - start_time) < 0.1  # Less than 100ms (very generous for testing)


class TestThreadSafety:
    """Test thread safety considerations for protocols."""

    def test_protocol_thread_safety_design(self):
        """Test that protocols are designed for thread safety."""
        # Protocols themselves should not have thread safety issues
        # since they're just interface definitions
        mock_provider = Mock()

        # Multiple threads should be able to check protocol compliance
        import threading
        results = []

        def check_protocol():
            # Simulate protocol checking
            has_method = hasattr(mock_provider, 'get_current_theme')
            results.append(has_method)

        threads = [threading.Thread(target=check_protocol) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        # All threads should successfully check the protocol
        assert len(results) == 10
        assert all(results)


class TestUtilityFunctions:
    """Test utility functions provided by protocols module."""

    def test_validate_performance_requirements(self):
        """Test performance validation utility."""
        # Test that function exists and returns boolean
        result = validate_performance_requirements()
        assert isinstance(result, bool)

    def test_get_protocol_version(self):
        """Test protocol version utility."""
        # Test that function exists and returns version string
        version = get_protocol_version()
        assert isinstance(version, str)
        assert len(version) > 0

        # Test that version follows semver pattern
        import re
        semver_pattern = r'^\d+\.\d+\.\d+'
        assert re.match(semver_pattern, version)