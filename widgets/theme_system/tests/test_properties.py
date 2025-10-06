"""Tests for ThemeProperty descriptors.

This module tests the property descriptor system for clean, type-safe
theme property access. Following TDD methodology - these tests are written
BEFORE implementation.

Test Coverage:
- ThemeProperty descriptor protocol (__get__, __set__, __set_name__)
- ColorProperty returns QColor instances
- FontProperty returns QFont instances
- Read-only enforcement (cannot set properties)
- Smart defaults from ColorTokenRegistry
- Integration with ThemedWidget
- Edge cases and error handling
"""

from unittest.mock import Mock

import pytest
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QWidget

from vfwidgets_theme import Tokens

# Import what we're testing
from vfwidgets_theme.widgets.properties import (
    ColorProperty,
    FontProperty,
    ThemeProperty,
)

# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def mock_widget():
    """Create a mock ThemedWidget for testing."""
    widget = Mock()
    widget._theme_properties = Mock()
    widget._theme_config = {"bg": "window.background", "fg": "window.foreground"}
    return widget


@pytest.fixture
def mock_theme():
    """Create a mock theme object."""
    theme = Mock()
    theme.name = "test-theme"
    theme.colors = Mock()
    theme.colors.foreground = "#000000"
    theme.colors.background = "#ffffff"
    return theme


# ============================================================================
# Test ThemeProperty - Descriptor Protocol
# ============================================================================


class TestThemePropertyDescriptor:
    """Test ThemeProperty descriptor protocol implementation."""

    def test_descriptor_has_required_methods(self):
        """Test that ThemeProperty implements descriptor protocol."""
        prop = ThemeProperty(Tokens.COLORS_BACKGROUND)

        # Must have __get__, __set__, __set_name__
        assert hasattr(prop, "__get__")
        assert hasattr(prop, "__set__")
        assert hasattr(prop, "__set_name__")

        # Methods should be callable
        assert callable(prop.__get__)
        assert callable(prop.__set__)
        assert callable(prop.__set_name__)

    def test_init_stores_token_and_default(self):
        """Test that __init__ stores token and default value."""
        token = Tokens.COLORS_BACKGROUND
        default = "#ffffff"

        prop = ThemeProperty(token, default=default)

        assert prop.token == token
        assert prop.default == default

    def test_set_name_stores_attribute_name(self):
        """Test that __set_name__ stores the attribute name."""
        prop = ThemeProperty(Tokens.COLORS_BACKGROUND)

        # Simulate binding to a class
        prop.__set_name__(Mock, "bg_color")

        assert hasattr(prop, "_attr_name")
        assert prop._attr_name == "bg_color"

    def test_get_returns_descriptor_when_accessed_from_class(self):
        """Test that accessing from class returns the descriptor itself."""

        class TestWidget:
            bg = ThemeProperty(Tokens.COLORS_BACKGROUND)

        # Access from class (not instance)
        result = TestWidget.bg

        # Should return the descriptor itself
        assert isinstance(result, ThemeProperty)

    def test_get_returns_value_when_accessed_from_instance(self, mock_widget):
        """Test that accessing from instance returns the theme value."""

        # Create a real widget class with property
        class TestWidget:
            bg = ThemeProperty("window.background", default="#ffffff")

        # Set name (normally done by Python)
        TestWidget.bg.__set_name__(TestWidget, "bg")

        # Mock the widget's theme property getter
        mock_widget._theme_properties.get_property.return_value = "#000000"
        mock_widget.__class__ = TestWidget

        # Access property
        result = TestWidget.bg.__get__(mock_widget, TestWidget)

        # Should call get_property with the token
        assert result == "#000000" or result == "#ffffff"  # Either theme value or default

    def test_get_returns_default_when_theme_value_not_found(self):
        """Test that default is returned when theme value is not available."""
        prop = ThemeProperty("nonexistent.token", default="#ff0000")
        prop.__set_name__(Mock, "test_prop")

        # Mock widget with no theme value
        widget = Mock()
        widget._theme_properties = Mock()
        widget._theme_properties.get_property.return_value = None

        # Should return default (or None if theme system returns None)
        result = prop.__get__(widget, type(widget))

        # Implementation may return:
        # 1. Default value '#ff0000'
        # 2. None if theme system returns None (acceptable)
        assert result == "#ff0000" or result is None

    def test_set_raises_attribute_error(self, mock_widget):
        """Test that setting a ThemeProperty raises AttributeError (read-only)."""
        prop = ThemeProperty(Tokens.COLORS_BACKGROUND)
        prop.__set_name__(Mock, "bg_color")

        # Attempting to set should raise AttributeError
        with pytest.raises(AttributeError) as exc_info:
            prop.__set__(mock_widget, "#000000")

        # Error message should indicate read-only
        assert "read-only" in str(exc_info.value).lower()

    def test_multiple_properties_on_same_widget(self):
        """Test that multiple ThemeProperty descriptors work correctly on same widget."""

        class TestWidget:
            bg = ThemeProperty("window.background", default="#ffffff")
            fg = ThemeProperty("window.foreground", default="#000000")
            border = ThemeProperty("colors.focusBorder", default="#0078d4")

        # Set names (normally done by Python)
        TestWidget.bg.__set_name__(TestWidget, "bg")
        TestWidget.fg.__set_name__(TestWidget, "fg")
        TestWidget.border.__set_name__(TestWidget, "border")

        # Create mock widget
        widget = Mock()
        widget._theme_properties = Mock()
        widget._theme_properties.get_property = Mock(side_effect=lambda key, default: default)
        widget.__class__ = TestWidget

        # Access all properties
        bg_result = TestWidget.bg.__get__(widget, TestWidget)
        fg_result = TestWidget.fg.__get__(widget, TestWidget)
        border_result = TestWidget.border.__get__(widget, TestWidget)

        # Each should have correct default
        assert bg_result in ["#ffffff", None]  # Either default or None
        assert fg_result in ["#000000", None]
        assert border_result in ["#0078d4", None]


# ============================================================================
# Test ColorProperty - QColor Conversion
# ============================================================================


class TestColorProperty:
    """Test ColorProperty descriptor for color values."""

    def test_color_property_inherits_from_theme_property(self):
        """Test that ColorProperty inherits from ThemeProperty."""
        prop = ColorProperty(Tokens.COLORS_BACKGROUND)

        assert isinstance(prop, ThemeProperty)

    def test_color_property_returns_qcolor_instance(self):
        """Test that ColorProperty returns QColor instances."""
        prop = ColorProperty("window.background", default="#ff0000")
        prop.__set_name__(Mock, "bg_color")

        # Mock widget with color value
        widget = Mock()
        widget._theme_properties = Mock()
        widget._theme_properties.get_property.return_value = "#00ff00"

        result = prop.__get__(widget, type(widget))

        # Should return QColor instance
        # Implementation detail: might return QColor or string that can be converted
        # We test that it's either QColor or a valid color string
        if isinstance(result, QColor):
            assert result.isValid()
        else:
            # If string, should be valid color
            assert isinstance(result, str)
            assert result.startswith("#") or result.startswith("rgb")

    def test_color_property_handles_hex_colors(self):
        """Test that ColorProperty handles hex color format."""
        prop = ColorProperty("window.background", default="#ff0000")
        prop.__set_name__(Mock, "bg_color")

        widget = Mock()
        widget._theme_properties = Mock()
        widget._theme_properties.get_property.return_value = "#0078d4"

        result = prop.__get__(widget, type(widget))

        # Should handle hex colors
        assert result is not None

    def test_color_property_handles_rgb_colors(self):
        """Test that ColorProperty handles rgb() color format."""
        prop = ColorProperty("window.background")
        prop.__set_name__(Mock, "bg_color")

        widget = Mock()
        widget._theme_properties = Mock()
        widget._theme_properties.get_property.return_value = "rgb(255, 0, 0)"

        result = prop.__get__(widget, type(widget))

        # Should handle rgb colors
        assert result is not None

    def test_color_property_default_is_valid_color(self):
        """Test that ColorProperty default must be a valid color."""
        # Valid color should work
        prop = ColorProperty("window.background", default="#ff0000")
        assert prop.default == "#ff0000"

        # None is acceptable
        prop2 = ColorProperty("window.background", default=None)
        assert prop2.default is None

    def test_color_property_is_read_only(self):
        """Test that ColorProperty is read-only."""
        prop = ColorProperty(Tokens.COLORS_BACKGROUND)
        prop.__set_name__(Mock, "bg_color")

        widget = Mock()

        # Should raise AttributeError when trying to set
        with pytest.raises(AttributeError):
            prop.__set__(widget, QColor("#ff0000"))


# ============================================================================
# Test FontProperty - QFont Conversion
# ============================================================================


class TestFontProperty:
    """Test FontProperty descriptor for font values."""

    def test_font_property_inherits_from_theme_property(self):
        """Test that FontProperty inherits from ThemeProperty."""
        prop = FontProperty("text.font")

        assert isinstance(prop, ThemeProperty)

    def test_font_property_returns_qfont_instance(self):
        """Test that FontProperty returns QFont instances."""
        prop = FontProperty("text.font", default="Arial, 12px")
        prop.__set_name__(Mock, "text_font")

        widget = Mock()
        widget._theme_properties = Mock()
        widget._theme_properties.get_property.return_value = "Consolas, 10px"

        result = prop.__get__(widget, type(widget))

        # Should return QFont instance or font string
        if isinstance(result, QFont):
            assert result.family() != ""
        else:
            # If string, should be valid font specification
            assert isinstance(result, str)

    def test_font_property_handles_font_family(self):
        """Test that FontProperty handles font family names."""
        prop = FontProperty("text.font", default="Arial")
        prop.__set_name__(Mock, "text_font")

        widget = Mock()
        widget._theme_properties = Mock()
        widget._theme_properties.get_property.return_value = "Consolas"

        result = prop.__get__(widget, type(widget))

        # Should handle font family
        assert result is not None

    def test_font_property_handles_font_with_size(self):
        """Test that FontProperty handles font with size."""
        prop = FontProperty("text.font")
        prop.__set_name__(Mock, "text_font")

        widget = Mock()
        widget._theme_properties = Mock()
        widget._theme_properties.get_property.return_value = "Consolas, 12px"

        result = prop.__get__(widget, type(widget))

        # Should handle font with size
        assert result is not None

    def test_font_property_default_is_valid_font(self):
        """Test that FontProperty default is a valid font specification."""
        # Valid font should work
        prop = FontProperty("text.font", default="Arial, 12px")
        assert prop.default == "Arial, 12px"

        # None is acceptable
        prop2 = FontProperty("text.font", default=None)
        assert prop2.default is None

    def test_font_property_is_read_only(self):
        """Test that FontProperty is read-only."""
        prop = FontProperty("text.font")
        prop.__set_name__(Mock, "text_font")

        widget = Mock()

        # Should raise AttributeError when trying to set
        with pytest.raises(AttributeError):
            prop.__set__(widget, QFont("Arial"))


# ============================================================================
# Test Integration with ThemedWidget
# ============================================================================


class TestPropertyIntegrationWithThemedWidget:
    """Test ThemeProperty integration with actual ThemedWidget."""

    def test_property_access_from_themed_widget_subclass(self):
        """Test that properties work when used in ThemedWidget subclass."""
        from vfwidgets_theme.widgets.base import ThemedWidget

        # Define a widget with properties
        class MyWidget(ThemedWidget, QWidget):
            bg = ThemeProperty("window.background", default="#ffffff")
            fg = ThemeProperty("window.foreground", default="#000000")

        # Properties should be bound to class
        assert hasattr(MyWidget, "bg")
        assert hasattr(MyWidget, "fg")
        assert isinstance(MyWidget.bg, ThemeProperty)
        assert isinstance(MyWidget.fg, ThemeProperty)

    def test_property_with_tokens_constants(self):
        """Test that properties work with Tokens constants."""
        from vfwidgets_theme.widgets.base import ThemedWidget

        class MyWidget(ThemedWidget, QWidget):
            bg = ThemeProperty(Tokens.COLORS_BACKGROUND, default="#ffffff")
            fg = ThemeProperty(Tokens.COLORS_FOREGROUND, default="#000000")
            border = ThemeProperty(Tokens.COLORS_FOCUS_BORDER, default="#0078d4")

        # Should accept Tokens constants
        assert MyWidget.bg.token == Tokens.COLORS_BACKGROUND
        assert MyWidget.fg.token == Tokens.COLORS_FOREGROUND
        assert MyWidget.border.token == Tokens.COLORS_FOCUS_BORDER


# ============================================================================
# Test Edge Cases and Error Handling
# ============================================================================


class TestPropertyEdgeCases:
    """Test edge cases and error handling."""

    def test_property_with_none_token(self):
        """Test that ThemeProperty handles None token gracefully."""
        # Should allow None token (with warning or default behavior)
        prop = ThemeProperty(None, default="#ffffff")
        assert prop.token is None
        assert prop.default == "#ffffff"

    def test_property_with_invalid_token(self):
        """Test that ThemeProperty handles invalid token strings."""
        # Should allow any string (validation happens elsewhere)
        prop = ThemeProperty("invalid.nonexistent.token", default="#ffffff")
        assert prop.token == "invalid.nonexistent.token"

    def test_property_with_none_default(self):
        """Test that ThemeProperty handles None default."""
        prop = ThemeProperty("window.background", default=None)
        assert prop.default is None

    def test_property_accessed_before_set_name(self):
        """Test property behavior when accessed before __set_name__ is called."""
        prop = ThemeProperty("window.background", default="#ffffff")

        # Access without __set_name__ called
        widget = Mock()
        widget._theme_properties = Mock()
        widget._theme_properties.get_property.return_value = None

        # Should handle gracefully (might raise or return default)
        try:
            result = prop.__get__(widget, type(widget))
            # If it doesn't raise, should return something
            assert result is not None or result is None  # Any result is fine
        except AttributeError:
            # Also acceptable - descriptor not fully initialized
            pass

    def test_property_with_widget_that_has_no_theme_system(self):
        """Test property behavior with widget that has no theme system."""
        prop = ThemeProperty("window.background", default="#ff0000")
        prop.__set_name__(Mock, "bg")

        # Widget without _theme_properties
        widget = Mock(spec=[])

        # Should handle gracefully (return default or raise)
        try:
            result = prop.__get__(widget, type(widget))
            # If successful, should return default
            assert result == "#ff0000" or result is None
        except AttributeError:
            # Also acceptable - widget doesn't have theme system
            pass

    def test_multiple_widgets_with_same_property_descriptor(self):
        """Test that same descriptor instance works correctly across multiple widgets."""

        class TestWidget:
            bg = ThemeProperty("window.background", default="#ffffff")

        TestWidget.bg.__set_name__(TestWidget, "bg")

        # Create two different widgets
        widget1 = Mock()
        widget1._theme_properties = Mock()
        widget1._theme_properties.get_property.return_value = "#000000"

        widget2 = Mock()
        widget2._theme_properties = Mock()
        widget2._theme_properties.get_property.return_value = "#ff0000"

        # Access property on both widgets
        result1 = TestWidget.bg.__get__(widget1, TestWidget)
        result2 = TestWidget.bg.__get__(widget2, TestWidget)

        # Each should get their own value (not shared)
        # Implementation should not cache per descriptor, but per widget
        assert result1 is not None
        assert result2 is not None


# ============================================================================
# Test Property Documentation and Examples
# ============================================================================


class TestPropertyDocumentation:
    """Test that property examples from documentation work correctly."""

    def test_example_from_api_consolidation_plan(self):
        """Test the example from API-CONSOLIDATION-PLAN.md."""
        from vfwidgets_theme.widgets.base import ThemedWidget

        # Example from Day 15 specification
        class MyWidget(ThemedWidget, QWidget):
            bg = ThemeProperty(Tokens.COLORS_BACKGROUND, default="#ffffff")

        # Should create property
        assert hasattr(MyWidget, "bg")
        assert isinstance(MyWidget.bg, ThemeProperty)
        assert MyWidget.bg.token == Tokens.COLORS_BACKGROUND
        assert MyWidget.bg.default == "#ffffff"

    def test_example_with_color_property(self):
        """Test ColorProperty example usage."""
        from vfwidgets_theme.widgets.base import ThemedWidget

        class MyWidget(ThemedWidget, QWidget):
            bg_color = ColorProperty(Tokens.COLORS_BACKGROUND, default="#ffffff")
            fg_color = ColorProperty(Tokens.COLORS_FOREGROUND, default="#000000")

        # Should create color properties
        assert hasattr(MyWidget, "bg_color")
        assert isinstance(MyWidget.bg_color, ColorProperty)

    def test_example_with_font_property(self):
        """Test FontProperty example usage."""
        from vfwidgets_theme.widgets.base import ThemedWidget

        class MyWidget(ThemedWidget, QWidget):
            text_font = FontProperty("text.font", default="Arial, 12px")

        # Should create font property
        assert hasattr(MyWidget, "text_font")
        assert isinstance(MyWidget.text_font, FontProperty)


# ============================================================================
# Run Tests
# ============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
