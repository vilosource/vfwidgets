"""
Tests for Phase 2 Theme System features.

This module tests the four Phase 2 features:
1. Theme inheritance (ThemeBuilder.extend())
2. Theme composition (ThemeComposer.compose())
3. Accessibility validation (WCAG contrast ratios)
4. Enhanced error messages (docs links, property listings)
"""

import pytest

from src.vfwidgets_theme.core.theme import (
    ThemeBuilder,
    ThemeComposer,
    ThemeValidator,
)


class TestThemeInheritance:
    """Test suite for theme inheritance feature."""

    def test_extend_from_theme_instance(self):
        """Test extending from a Theme instance."""
        # Create parent theme
        parent = (ThemeBuilder("parent")
            .set_type("dark")
            .add_color("colors.background", "#1e1e1e")
            .add_color("colors.foreground", "#d4d4d4")
            .add_color("button.background", "#0e639c")
            .build())

        # Create child theme extending parent
        child = (ThemeBuilder("child")
            .extend(parent)
            .add_color("button.background", "#ff0000")  # Override
            .build())

        # Child inherits parent's colors
        assert child.colors["colors.background"] == "#1e1e1e"
        assert child.colors["colors.foreground"] == "#d4d4d4"

        # Child overrides parent's button color
        assert child.colors["button.background"] == "#ff0000"

        # Child inherits parent's type
        assert child.type == "dark"

    def test_extend_preserves_child_values_set_before(self):
        """Test that values set before extend() are not overridden."""
        parent = (ThemeBuilder("parent")
            .add_color("colors.primary", "#007acc")
            .build())

        # Set value BEFORE extend
        child = (ThemeBuilder("child")
            .add_color("colors.primary", "#ff0000")  # Set first
            .extend(parent)                          # Then extend
            .build())

        # Child's value should be preserved (not overridden by parent)
        assert child.colors["colors.primary"] == "#ff0000"

    def test_extend_inherits_styles_and_metadata(self):
        """Test that styles and metadata are inherited."""
        parent = (ThemeBuilder("parent")
            .add_style("font.family", "Consolas")
            .add_metadata("author", "Test Author")
            .add_metadata("description", "Parent theme")
            .build())

        child = (ThemeBuilder("child")
            .extend(parent)
            .build())

        # Styles inherited
        assert child.styles["font.family"] == "Consolas"

        # Metadata inherited
        assert child.metadata["author"] == "Test Author"
        assert child.metadata["description"] == "Parent theme"

        # Parent reference stored
        assert child.metadata["parent_theme"] == "parent"

    def test_extend_inherits_token_colors(self):
        """Test that token colors are inherited."""
        parent = (ThemeBuilder("parent")
            .add_token_color("comment", {"foreground": "#608b4e"}, "Comments")
            .add_token_color("keyword", {"foreground": "#569cd6"}, "Keywords")
            .build())

        child = (ThemeBuilder("child")
            .extend(parent)
            .add_token_color("string", {"foreground": "#ce9178"}, "Strings")
            .build())

        # Child has parent's token colors plus its own
        assert len(child.token_colors) == 3
        assert child.token_colors[0]["name"] == "Comments"
        assert child.token_colors[1]["name"] == "Keywords"
        assert child.token_colors[2]["name"] == "Strings"

    def test_extend_chain(self):
        """Test extending from a theme that already extends another."""
        grandparent = (ThemeBuilder("grandparent")
            .add_color("colors.background", "#000000")
            .add_color("colors.foreground", "#ffffff")
            .build())

        parent = (ThemeBuilder("parent")
            .extend(grandparent)
            .add_color("button.background", "#0e639c")
            .build())

        child = (ThemeBuilder("child")
            .extend(parent)
            .add_color("button.foreground", "#ffffff")
            .build())

        # Child inherits from entire chain
        assert child.colors["colors.background"] == "#000000"  # From grandparent
        assert child.colors["button.background"] == "#0e639c"  # From parent
        assert child.colors["button.foreground"] == "#ffffff"  # From child

    def test_get_parent_returns_parent_theme(self):
        """Test that get_parent() returns the parent theme."""
        parent = ThemeBuilder("parent").build()

        builder = ThemeBuilder("child")
        assert builder.get_parent() is None  # No parent yet

        builder.extend(parent)
        assert builder.get_parent() == parent  # Parent set

    def test_get_parent_returns_none_when_no_parent(self):
        """Test that get_parent() returns None when no parent."""
        builder = ThemeBuilder("standalone")
        assert builder.get_parent() is None


class TestThemeComposition:
    """Test suite for theme composition feature."""

    def test_compose_two_themes_basic(self):
        """Test basic composition of two themes."""
        theme1 = (ThemeBuilder("theme1")
            .add_color("colors.background", "#ffffff")
            .add_color("colors.foreground", "#000000")
            .build())

        theme2 = (ThemeBuilder("theme2")
            .add_color("button.background", "#0e639c")
            .build())

        composer = ThemeComposer()
        composed = composer.compose(theme1, theme2)

        # Composed theme has colors from both
        assert composed.colors["colors.background"] == "#ffffff"
        assert composed.colors["colors.foreground"] == "#000000"
        assert composed.colors["button.background"] == "#0e639c"

    def test_compose_override_priority(self):
        """Test that later theme overrides earlier theme."""
        theme1 = (ThemeBuilder("theme1")
            .add_color("colors.primary", "#111111")
            .build())

        theme2 = (ThemeBuilder("theme2")
            .add_color("colors.primary", "#222222")
            .build())

        composer = ThemeComposer()
        composed = composer.compose(theme1, theme2)

        # theme2 overrides theme1
        assert composed.colors["colors.primary"] == "#222222"

    def test_compose_chain_multiple_themes(self):
        """Test composing a chain of multiple themes."""
        theme1 = (ThemeBuilder("t1")
            .add_color("colors.background", "#ffffff")
            .build())

        theme2 = (ThemeBuilder("t2")
            .add_color("button.background", "#0e639c")
            .build())

        theme3 = (ThemeBuilder("t3")
            .add_color("input.background", "#3c3c3c")
            .build())

        composer = ThemeComposer()
        composed = composer.compose_chain([theme1, theme2, theme3])

        # All colors present
        assert composed.colors["colors.background"] == "#ffffff"
        assert composed.colors["button.background"] == "#0e639c"
        assert composed.colors["input.background"] == "#3c3c3c"

    def test_compose_caching(self):
        """Test that composition results are cached."""
        theme1 = ThemeBuilder("theme1").build()
        theme2 = ThemeBuilder("theme2").build()

        composer = ThemeComposer()

        # First composition
        result1 = composer.compose(theme1, theme2)

        # Second composition (should be cached)
        result2 = composer.compose(theme1, theme2)

        # Should return same instance (cached)
        assert result1 is result2

    def test_compose_clear_cache(self):
        """Test clearing composition cache."""
        theme1 = ThemeBuilder("theme1").build()
        theme2 = ThemeBuilder("theme2").build()

        composer = ThemeComposer()

        # Compose and cache
        result1 = composer.compose(theme1, theme2)

        # Clear cache
        composer.clear_cache()

        # Compose again (creates new instance)
        result2 = composer.compose(theme1, theme2)

        # Different instances (cache was cleared)
        assert result1 is not result2
        # But same content
        assert result1.colors == result2.colors


class TestAccessibilityValidation:
    """Test suite for accessibility validation feature."""

    def test_validate_good_contrast(self):
        """Test validation passes for good contrast."""
        theme = (ThemeBuilder("good-contrast")
            .add_color("colors.background", "#ffffff")
            .add_color("colors.foreground", "#000000")
            .build())

        validator = ThemeValidator()
        result = validator.validate_accessibility(theme)

        # Should be valid (21:1 contrast ratio)
        assert result.is_valid
        assert len(result.errors) == 0

    def test_validate_poor_contrast_fails(self):
        """Test validation fails for poor contrast."""
        theme = (ThemeBuilder("poor-contrast")
            .add_color("colors.background", "#ffffff")
            .add_color("colors.foreground", "#eeeeee")  # Very low contrast
            .build())

        validator = ThemeValidator()
        result = validator.validate_accessibility(theme)

        # Should have errors or warnings
        assert not result.is_valid or len(result.warnings) > 0

    def test_validate_button_contrast(self):
        """Test validation checks button contrast."""
        theme = (ThemeBuilder("button-contrast")
            .add_color("button.background", "#ffffff")
            .add_color("button.foreground", "#f0f0f0")  # Low contrast
            .build())

        validator = ThemeValidator()
        result = validator.validate_accessibility(theme)

        # Should have warnings about button contrast
        assert len(result.warnings) > 0
        assert any("button" in w.lower() for w in result.warnings)

    def test_contrast_ratio_calculation(self):
        """Test WCAG contrast ratio calculation."""
        validator = ThemeValidator()

        # White on black = maximum contrast (~21:1)
        ratio1 = validator._calculate_contrast_ratio("#ffffff", "#000000")
        assert 20.9 <= ratio1 <= 21.1

        # Same color = minimum contrast (1:1)
        ratio2 = validator._calculate_contrast_ratio("#ffffff", "#ffffff")
        assert 0.9 <= ratio2 <= 1.1

        # Gray on white = moderate contrast
        ratio3 = validator._calculate_contrast_ratio("#777777", "#ffffff")
        assert 4.0 <= ratio3 <= 5.0

    def test_relative_luminance_calculation(self):
        """Test relative luminance calculation."""
        validator = ThemeValidator()

        # White = maximum luminance (1.0)
        lum_white = validator._get_relative_luminance("#ffffff")
        assert 0.99 <= lum_white <= 1.0

        # Black = minimum luminance (0.0)
        lum_black = validator._get_relative_luminance("#000000")
        assert 0.0 <= lum_black <= 0.01

        # Gray = middle luminance
        lum_gray = validator._get_relative_luminance("#808080")
        assert 0.2 <= lum_gray <= 0.3


class TestEnhancedErrorMessages:
    """Test suite for enhanced error messages feature."""

    def test_get_available_properties_with_prefix(self):
        """Test getting available properties by prefix."""
        validator = ThemeValidator()

        # Get button properties
        button_props = validator.get_available_properties("button")

        # Should have button properties
        assert len(button_props) > 0
        assert "button.background" in button_props
        assert "button.foreground" in button_props
        assert all(p.startswith("button.") for p in button_props)

    def test_get_available_properties_sorted(self):
        """Test that properties are returned sorted."""
        validator = ThemeValidator()

        props = validator.get_available_properties("button")

        # Should be sorted
        assert props == sorted(props)

    def test_format_error_not_found(self):
        """Test formatting error for property not found."""
        validator = ThemeValidator()

        error_msg = validator.format_error("button.backgroud", "not_found")

        # Should contain helpful information
        assert "button.backgroud" in error_msg
        assert "not found" in error_msg.lower()
        assert "button.background" in error_msg  # Suggestion
        assert "available button properties" in error_msg.lower()
        assert "https://" in error_msg  # Documentation link

    def test_format_error_includes_suggestions(self):
        """Test that error includes property suggestions."""
        validator = ThemeValidator()

        error_msg = validator.format_error("button.hoverBg", "not_found")

        # Should suggest correct property
        assert "button.hoverBackground" in error_msg or "did you mean" in error_msg.lower()

    def test_format_error_includes_docs_link(self):
        """Test that error includes documentation link."""
        validator = ThemeValidator()

        error_msg = validator.format_error("button.invalid", "not_found")

        # Should have docs link
        assert "vfwidgets.readthedocs.io" in error_msg
        assert "#button" in error_msg

    def test_format_error_lists_available_properties(self):
        """Test that error lists available properties."""
        validator = ThemeValidator()

        error_msg = validator.format_error("input.invalidProp", "not_found")

        # Should list input properties
        assert "available input properties" in error_msg.lower()
        # Should have some property examples
        assert "input." in error_msg


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
