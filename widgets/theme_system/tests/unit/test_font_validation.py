"""Unit tests for font validation in Theme.

This module tests Phase 1 of the font support implementation:
- Theme accepts fonts field
- Font validation works correctly
- Invalid fonts raise clear errors
- Package themes load with fonts

Based on: widgets/theme_system/docs/fonts-implementation-tasks-PLAN.md
Phase 1 - Core Font Infrastructure
"""

import pytest

from vfwidgets_theme.core.theme import Theme
from vfwidgets_theme.errors import FontPropertyError, FontValidationError


class TestFontValidation:
    """Test suite for font validation logic."""

    def test_theme_with_fonts_validates(self):
        """Valid font configuration should pass validation."""
        theme = Theme(
            name="test",
            fonts={
                "fonts.mono": ["JetBrains Mono", "Consolas", "monospace"],
                "fonts.ui": ["Segoe UI", "sans-serif"],
                "fonts.size": 13,
                "fonts.weight": "normal",
                "terminal.fontSize": 14,
                "terminal.lineHeight": 1.4,
            },
        )
        assert theme.fonts["fonts.mono"] == ["JetBrains Mono", "Consolas", "monospace"]
        assert theme.fonts["fonts.size"] == 13

    def test_invalid_font_family_type_raises(self):
        """Font family must be string or list of strings."""
        with pytest.raises(FontPropertyError) as exc_info:
            Theme(
                name="test",
                fonts={"fonts.mono": 123},  # Invalid type
            )
        assert "Must be string or list of strings" in str(exc_info.value)

    def test_invalid_font_size_raises(self):
        """Font size must be a number."""
        with pytest.raises(FontPropertyError) as exc_info:
            Theme(
                name="test",
                fonts={"terminal.fontSize": "14px"},  # Must be number
            )
        assert "Must be a number" in str(exc_info.value)

    def test_invalid_font_weight_raises(self):
        """Font weight must be 100-900 or valid string."""
        with pytest.raises(FontPropertyError) as exc_info:
            Theme(
                name="test",
                fonts={"fonts.weight": 950},  # Out of range
            )
        assert "Must be 100, 200, ..., 900" in str(exc_info.value)

    def test_negative_font_size_raises(self):
        """Font size must be positive."""
        with pytest.raises(FontPropertyError) as exc_info:
            Theme(
                name="test",
                fonts={"terminal.fontSize": -5},
            )
        assert "Must be positive" in str(exc_info.value)

    def test_font_size_too_large_raises(self):
        """Font size must be <= 144 pt."""
        with pytest.raises(FontPropertyError) as exc_info:
            Theme(
                name="test",
                fonts={"terminal.fontSize": 200},
            )
        assert "Must be <= 144 pt" in str(exc_info.value)

    def test_missing_mono_fallback_raises(self):
        """fonts.mono must end with 'monospace'."""
        with pytest.raises(FontValidationError) as exc_info:
            Theme(
                name="test",
                fonts={"fonts.mono": ["JetBrains Mono"]},  # Missing monospace fallback
            )
        assert "must end with 'monospace' fallback" in str(exc_info.value)

    def test_fonts_mono_must_end_with_monospace(self):
        """fonts.mono must have monospace as final fallback."""
        # This should pass
        theme = Theme(
            name="test",
            fonts={"fonts.mono": ["JetBrains Mono", "Consolas", "monospace"]},
        )
        assert theme.fonts["fonts.mono"][-1] == "monospace"

        # This should fail
        with pytest.raises(FontValidationError):
            Theme(
                name="test",
                fonts={"fonts.mono": ["JetBrains Mono", "Consolas"]},
            )

    def test_fonts_ui_must_end_with_sans_serif(self):
        """fonts.ui must have sans-serif as final fallback."""
        # This should pass
        theme = Theme(
            name="test",
            fonts={"fonts.ui": ["Segoe UI", "sans-serif"]},
        )
        assert theme.fonts["fonts.ui"][-1] == "sans-serif"

        # This should fail
        with pytest.raises(FontValidationError):
            Theme(
                name="test",
                fonts={"fonts.ui": ["Segoe UI", "Arial"]},
            )

    def test_font_weight_string_conversion(self):
        """Valid font weight strings should be accepted."""
        valid_weights = ["normal", "bold", "bolder", "lighter", "400", "700"]

        for weight in valid_weights:
            theme = Theme(
                name="test",
                fonts={"fonts.weight": weight},
            )
            assert theme.fonts["fonts.weight"] == weight

    def test_fractional_font_sizes_allowed(self):
        """Font sizes can be fractional (float)."""
        theme = Theme(
            name="test",
            fonts={
                "terminal.fontSize": 13.5,
                "tabs.fontSize": 11.75,
            },
        )
        assert theme.fonts["terminal.fontSize"] == 13.5
        assert theme.fonts["tabs.fontSize"] == 11.75

    def test_empty_font_family_list(self):
        """Empty font family list should raise error."""
        with pytest.raises(FontPropertyError) as exc_info:
            Theme(
                name="test",
                fonts={"fonts.mono": []},
            )
        assert "cannot be empty" in str(exc_info.value)

    def test_theme_without_fonts_uses_defaults(self):
        """Theme without fonts field should work (empty dict)."""
        theme = Theme(
            name="test",
            colors={"colors.background": "#000000"},
        )
        assert theme.fonts == {}

    def test_font_property_error_message(self):
        """FontPropertyError should include property name and value."""
        with pytest.raises(FontPropertyError) as exc_info:
            Theme(
                name="test",
                fonts={"terminal.fontSize": "large"},
            )

        error = exc_info.value
        assert error.property_name == "terminal.fontSize"
        assert "terminal.fontSize" in str(error)
        assert "Must be a number" in str(error)

    def test_font_validation_error_message(self):
        """FontValidationError should include clear message about requirement."""
        with pytest.raises(FontValidationError) as exc_info:
            Theme(
                name="test",
                fonts={"fonts.mono": ["JetBrains Mono", "Courier"]},
            )

        error = exc_info.value
        assert "monospace" in str(error)
        assert "fallback" in str(error).lower()
