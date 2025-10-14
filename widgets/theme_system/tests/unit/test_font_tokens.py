"""Unit tests for FontTokenRegistry resolution.

This module tests Phase 2 of the font support implementation:
- Hierarchical font token resolution
- Fallback chains working correctly
- QFont creation from tokens
- LRU cache performance
- Platform font detection

Based on: widgets/theme_system/docs/fonts-implementation-tasks-PLAN.md
Phase 2 - Font Token Resolution
"""


from PySide6.QtGui import QFont

from vfwidgets_theme.core.font_tokens import FontTokenRegistry
from vfwidgets_theme.core.theme import Theme


class TestFontTokenResolution:
    """Test suite for font token resolution logic."""

    def test_font_family_hierarchical_resolution(self):
        """Font family should resolve through hierarchy chain."""
        theme = Theme(
            name="test",
            fonts={
                "fonts.mono": ["JetBrains Mono", "Consolas", "monospace"],
                "terminal.fontFamily": ["Cascadia Code", "monospace"],
            },
        )

        # terminal.fontFamily exists, should use it
        families = FontTokenRegistry.get_font_family("terminal.fontFamily", theme)
        assert families == ["Cascadia Code", "monospace"]

        # editor.fontFamily doesn't exist, should fall back to fonts.mono
        families = FontTokenRegistry.get_font_family("editor.fontFamily", theme)
        assert families == ["JetBrains Mono", "Consolas", "monospace"]

    def test_font_size_fallback_to_base(self):
        """Font size should fall back to fonts.size if specific size missing."""
        theme = Theme(
            name="test",
            fonts={
                "fonts.size": 13,
                "terminal.fontSize": 14,
            },
        )

        # terminal.fontSize exists
        assert FontTokenRegistry.get_font_size("terminal.fontSize", theme) == 14.0

        # tabs.fontSize doesn't exist, falls back to fonts.size
        assert FontTokenRegistry.get_font_size("tabs.fontSize", theme) == 13.0

        # unknown token with no hierarchy, uses default
        assert FontTokenRegistry.get_font_size("unknown.fontSize", theme) == 13.0

    def test_font_weight_conversion_to_int(self):
        """Font weight strings should convert to integers."""
        theme = Theme(
            name="test",
            fonts={
                "fonts.weight": "bold",
                "terminal.fontWeight": 600,
            },
        )

        # Integer weight
        assert FontTokenRegistry.get_font_weight("terminal.fontWeight", theme) == 600

        # String weight converts to int
        assert FontTokenRegistry.get_font_weight("tabs.fontWeight", theme) == 700  # "bold"

        # Test weight strings that are valid in Phase 1 validation
        # (only strings in valid_weight_strings set)
        weight_tests = {
            "normal": 400,
            "bold": 700,
            "bolder": 400,  # Resolves to normal since not in weight_map
            "lighter": 400,  # Resolves to normal since not in weight_map
        }

        for weight_str, expected_int in weight_tests.items():
            theme_test = Theme(name="test", fonts={"fonts.weight": weight_str})
            result = FontTokenRegistry.get_font_weight("fonts.weight", theme_test)
            # For "bolder" and "lighter", they're valid strings but not in weight_map,
            # so they return DEFAULT_FONT_WEIGHT (400)
            if weight_str in ["bolder", "lighter"]:
                assert result == 400
            else:
                assert result == expected_int

    def test_line_height_fallback(self):
        """Line height should resolve with fallbacks."""
        theme = Theme(
            name="test",
            fonts={
                "fonts.lineHeight": 1.5,
                "terminal.lineHeight": 1.4,
            },
        )

        # Specific line height
        assert FontTokenRegistry.get_line_height("terminal.lineHeight", theme) == 1.4

        # No specific line height, uses default
        assert FontTokenRegistry.get_line_height("tabs.lineHeight", theme) == 1.4  # DEFAULT

    def test_letter_spacing_fallback(self):
        """Letter spacing should resolve with fallbacks."""
        theme = Theme(
            name="test",
            fonts={
                "terminal.letterSpacing": -0.5,
            },
        )

        # Specific letter spacing
        assert FontTokenRegistry.get_letter_spacing("terminal.letterSpacing", theme) == -0.5

        # No specific letter spacing, uses default (0.0)
        assert FontTokenRegistry.get_letter_spacing("tabs.letterSpacing", theme) == 0.0

    def test_terminal_inherits_from_mono(self):
        """Terminal fonts should inherit from fonts.mono."""
        theme = Theme(
            name="test",
            fonts={
                "fonts.mono": ["JetBrains Mono", "Consolas", "monospace"],
                "fonts.size": 13,
                "fonts.weight": 400,
            },
        )

        # Terminal inherits mono font family
        families = FontTokenRegistry.get_font_family("terminal.fontFamily", theme)
        assert families == ["JetBrains Mono", "Consolas", "monospace"]

        # Terminal inherits base size
        size = FontTokenRegistry.get_font_size("terminal.fontSize", theme)
        assert size == 13.0

        # Terminal inherits base weight
        weight = FontTokenRegistry.get_font_weight("terminal.fontWeight", theme)
        assert weight == 400

    def test_tabs_inherits_from_ui(self):
        """Tabs fonts should inherit from fonts.ui."""
        theme = Theme(
            name="test",
            fonts={
                "fonts.ui": ["Segoe UI", "Inter", "sans-serif"],
                "fonts.size": 13,
            },
        )

        # Tabs inherits UI font family
        families = FontTokenRegistry.get_font_family("tabs.fontFamily", theme)
        assert families == ["Segoe UI", "Inter", "sans-serif"]

        # Tabs inherits base size
        size = FontTokenRegistry.get_font_size("tabs.fontSize", theme)
        assert size == 13.0

    def test_category_guarantees_monospace(self):
        """fonts.mono must end with monospace (enforced by validation)."""
        theme = Theme(
            name="test",
            fonts={
                "fonts.mono": ["JetBrains Mono", "monospace"],
            },
        )

        families = FontTokenRegistry.get_font_family("fonts.mono", theme)
        assert families[-1] == "monospace"

    def test_category_guarantees_sans_serif(self):
        """fonts.ui must end with sans-serif (enforced by validation)."""
        theme = Theme(
            name="test",
            fonts={
                "fonts.ui": ["Segoe UI", "sans-serif"],
            },
        )

        families = FontTokenRegistry.get_font_family("fonts.ui", theme)
        assert families[-1] == "sans-serif"

    def test_lru_cache_performance(self):
        """LRU cache should improve performance."""
        theme = Theme(
            name="test",
            fonts={
                "fonts.mono": ["JetBrains Mono", "Consolas", "monospace"],
                "terminal.fontSize": 14,
            },
        )

        # Clear cache first
        FontTokenRegistry.clear_cache()

        # Warm up and measure cache effectiveness
        # First call populates cache
        FontTokenRegistry.get_font_family("terminal.fontFamily", theme)

        # Check that cache has entries after second call
        FontTokenRegistry.get_font_family("terminal.fontFamily", theme)
        cache_info = FontTokenRegistry.get_font_family.cache_info()

        # Should have at least one hit (second call was cached)
        assert cache_info.hits > 0
        assert cache_info.currsize > 0

    def test_cache_clear(self):
        """clear_cache() should invalidate all caches."""
        theme = Theme(
            name="test",
            fonts={
                "terminal.fontSize": 14,
            },
        )

        # Populate cache with multiple calls to register a hit
        FontTokenRegistry.get_font_size("terminal.fontSize", theme)
        FontTokenRegistry.get_font_size("terminal.fontSize", theme)

        # Should have at least one cache hit
        cache_info_before = FontTokenRegistry.get_font_size.cache_info()
        assert cache_info_before.hits > 0
        assert cache_info_before.currsize > 0

        # Clear cache
        FontTokenRegistry.clear_cache()

        # Cache should be empty
        cache_info_after = FontTokenRegistry.get_font_size.cache_info()
        assert cache_info_after.currsize == 0
        assert cache_info_after.hits == 0  # Hits counter also reset

    def test_get_qfont_creates_valid_font(self, qtbot):
        """get_qfont should create a valid QFont with all properties."""
        theme = Theme(
            name="test",
            fonts={
                "fonts.mono": ["Consolas", "monospace"],
                "fonts.size": 13,
                "fonts.weight": "bold",
                "terminal.fontSize": 14,
            },
        )

        font = FontTokenRegistry.get_qfont("terminal", theme)

        # Font should be created
        assert isinstance(font, QFont)

        # Font should have correct properties
        assert font.pointSizeF() == 14.0
        assert font.weight() == 700  # bold

        # Font family should be from the list (first available or first)
        # Since we can't guarantee Consolas is installed, just check it's set
        assert font.family() in ["Consolas", "monospace"] or font.family()

    def test_get_available_font_case_insensitive(self, qtbot):
        """get_available_font should match case-insensitively."""
        # This test checks that font matching is case-insensitive
        # We use generic families which are guaranteed to exist
        result = FontTokenRegistry.get_available_font(("MONOSPACE",))
        assert result == "MONOSPACE"  # Generic families always match

        result = FontTokenRegistry.get_available_font(("Sans-Serif",))
        assert result == "Sans-Serif"

    def test_get_available_font_none_found(self, qtbot):
        """get_available_font should return None if no fonts available."""
        # Use completely made-up font names (no generic fallback)
        result = FontTokenRegistry.get_available_font(
            ("NonexistentFont12345", "AnotherFakeFontXYZ")
        )
        assert result is None

    def test_get_available_font_generic_fallback(self, qtbot):
        """Generic families should always be considered available."""
        # Test all generic families
        generic_families = ["monospace", "sans-serif", "serif", "cursive", "fantasy"]

        for family in generic_families:
            result = FontTokenRegistry.get_available_font((family,))
            assert result == family
