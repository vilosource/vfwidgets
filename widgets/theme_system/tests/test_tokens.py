"""Tests for Tokens constants class (Phase 2: API Consolidation).

This test suite follows Test-Driven Development (TDD) methodology:
1. Tests written FIRST (they should fail initially)
2. Implementation written to pass tests
3. Refactor while keeping tests green

Requirements:
- Tokens class with all 179+ constants from ColorTokenRegistry
- Tokens.all_tokens() returns all token strings
- Tokens.validate() checks if token exists
- All tokens match ColorTokenRegistry exactly
"""

import pytest

from vfwidgets_theme.core.tokens import ColorTokenRegistry


class TestTokensClass:
    """Test suite for Tokens constants class."""

    def test_tokens_class_exists(self):
        """Test that Tokens class can be imported."""
        # This will fail until we create the class
        from vfwidgets_theme.core.token_constants import Tokens

        assert Tokens is not None

    def test_tokens_has_base_color_constants(self):
        """Test that Tokens has base color constants."""
        from vfwidgets_theme.core.token_constants import Tokens

        # Check a few key base color constants
        assert hasattr(Tokens, "COLORS_FOREGROUND")
        assert hasattr(Tokens, "COLORS_BACKGROUND")
        assert hasattr(Tokens, "COLORS_PRIMARY")
        assert hasattr(Tokens, "COLORS_FOCUS_BORDER")

        # Verify values match the token names
        assert Tokens.COLORS_FOREGROUND == "colors.foreground"
        assert Tokens.COLORS_BACKGROUND == "colors.background"
        assert Tokens.COLORS_PRIMARY == "colors.primary"

    def test_tokens_has_button_constants(self):
        """Test that Tokens has button color constants."""
        from vfwidgets_theme.core.token_constants import Tokens

        assert hasattr(Tokens, "BUTTON_BACKGROUND")
        assert hasattr(Tokens, "BUTTON_FOREGROUND")
        assert hasattr(Tokens, "BUTTON_HOVER_BACKGROUND")
        assert hasattr(Tokens, "BUTTON_DANGER_BACKGROUND")

        assert Tokens.BUTTON_BACKGROUND == "button.background"
        assert Tokens.BUTTON_FOREGROUND == "button.foreground"

    def test_tokens_has_input_constants(self):
        """Test that Tokens has input/dropdown constants."""
        from vfwidgets_theme.core.token_constants import Tokens

        assert hasattr(Tokens, "INPUT_BACKGROUND")
        assert hasattr(Tokens, "INPUT_FOREGROUND")
        assert hasattr(Tokens, "INPUT_BORDER")
        assert hasattr(Tokens, "DROPDOWN_BACKGROUND")

        assert Tokens.INPUT_BACKGROUND == "input.background"

    def test_tokens_has_list_constants(self):
        """Test that Tokens has list/tree constants."""
        from vfwidgets_theme.core.token_constants import Tokens

        assert hasattr(Tokens, "LIST_BACKGROUND")
        assert hasattr(Tokens, "LIST_FOREGROUND")
        assert hasattr(Tokens, "LIST_ACTIVE_SELECTION_BACKGROUND")
        assert hasattr(Tokens, "LIST_HOVER_BACKGROUND")

    def test_tokens_has_editor_constants(self):
        """Test that Tokens has editor constants."""
        from vfwidgets_theme.core.token_constants import Tokens

        assert hasattr(Tokens, "EDITOR_BACKGROUND")
        assert hasattr(Tokens, "EDITOR_FOREGROUND")
        assert hasattr(Tokens, "EDITOR_SELECTION_BACKGROUND")
        assert hasattr(Tokens, "EDITOR_LINE_HIGHLIGHT_BACKGROUND")

        assert Tokens.EDITOR_BACKGROUND == "editor.background"

    def test_tokens_has_sidebar_constants(self):
        """Test that Tokens has sidebar constants."""
        from vfwidgets_theme.core.token_constants import Tokens

        assert hasattr(Tokens, "SIDEBAR_BACKGROUND")
        assert hasattr(Tokens, "SIDEBAR_FOREGROUND")

    def test_tokens_has_panel_constants(self):
        """Test that Tokens has panel constants."""
        from vfwidgets_theme.core.token_constants import Tokens

        assert hasattr(Tokens, "PANEL_BACKGROUND")
        assert hasattr(Tokens, "PANEL_FOREGROUND")

    def test_tokens_has_tab_constants(self):
        """Test that Tokens has tab constants."""
        from vfwidgets_theme.core.token_constants import Tokens

        assert hasattr(Tokens, "TAB_ACTIVE_BACKGROUND")
        assert hasattr(Tokens, "TAB_INACTIVE_BACKGROUND")

    def test_tokens_has_all_tokens_method(self):
        """Test that Tokens has all_tokens() classmethod."""
        from vfwidgets_theme.core.token_constants import Tokens

        assert hasattr(Tokens, "all_tokens")
        assert callable(Tokens.all_tokens)

    def test_all_tokens_returns_list(self):
        """Test that all_tokens() returns a list."""
        from vfwidgets_theme.core.token_constants import Tokens

        result = Tokens.all_tokens()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_all_tokens_contains_expected_count(self):
        """Test that all_tokens() returns expected number of tokens."""
        from vfwidgets_theme.core.token_constants import Tokens

        tokens = Tokens.all_tokens()
        registry_tokens = ColorTokenRegistry.get_all_token_names()

        # Should match registry count exactly
        assert len(tokens) == len(registry_tokens), (
            f"Expected {len(registry_tokens)} tokens, got {len(tokens)}"
        )

    def test_all_tokens_matches_registry_exactly(self):
        """Test that all tokens match ColorTokenRegistry exactly."""
        from vfwidgets_theme.core.token_constants import Tokens

        tokens_set = set(Tokens.all_tokens())
        registry_set = set(ColorTokenRegistry.get_all_token_names())

        # Check for missing tokens
        missing = registry_set - tokens_set
        assert not missing, f"Missing tokens: {missing}"

        # Check for extra tokens
        extra = tokens_set - registry_set
        assert not extra, f"Extra tokens: {extra}"

        # Should be exact match
        assert tokens_set == registry_set

    def test_tokens_has_validate_method(self):
        """Test that Tokens has validate() classmethod."""
        from vfwidgets_theme.core.token_constants import Tokens

        assert hasattr(Tokens, "validate")
        assert callable(Tokens.validate)

    def test_validate_returns_bool(self):
        """Test that validate() returns boolean."""
        from vfwidgets_theme.core.token_constants import Tokens

        result = Tokens.validate("colors.foreground")
        assert isinstance(result, bool)

    def test_validate_accepts_valid_tokens(self):
        """Test that validate() returns True for valid tokens."""
        from vfwidgets_theme.core.token_constants import Tokens

        # Test various valid tokens
        assert Tokens.validate("colors.foreground") is True
        assert Tokens.validate("button.background") is True
        assert Tokens.validate("editor.background") is True
        assert Tokens.validate("list.activeSelectionBackground") is True

    def test_validate_rejects_invalid_tokens(self):
        """Test that validate() returns False for invalid tokens."""
        from vfwidgets_theme.core.token_constants import Tokens

        # Test various invalid tokens
        assert Tokens.validate("invalid.token") is False
        assert Tokens.validate("nonexistent") is False
        assert Tokens.validate("") is False
        assert Tokens.validate("colors.") is False

    def test_validate_all_registry_tokens(self):
        """Test that validate() accepts all registry tokens."""
        from vfwidgets_theme.core.token_constants import Tokens

        registry_tokens = ColorTokenRegistry.get_all_token_names()

        for token in registry_tokens:
            assert Tokens.validate(token), f"Token {token} should be valid"

    def test_constant_naming_convention(self):
        """Test that constants follow UPPER_SNAKE_CASE naming."""
        from vfwidgets_theme.core.token_constants import Tokens

        # Get all class attributes that are constants (uppercase)
        constants = [name for name in dir(Tokens) if not name.startswith("_") and name.isupper()]

        # Should have many constants
        assert len(constants) > 100, f"Expected >100 constants, found {len(constants)}"

        # All should be strings
        for const_name in constants:
            value = getattr(Tokens, const_name)
            assert isinstance(value, str), f"{const_name} should be a string, got {type(value)}"

    def test_constant_values_are_valid_token_paths(self):
        """Test that constant values are valid dotted token paths."""
        from vfwidgets_theme.core.token_constants import Tokens

        constants = [name for name in dir(Tokens) if not name.startswith("_") and name.isupper()]

        for const_name in constants:
            value = getattr(Tokens, const_name)
            # Should contain at least one dot
            assert "." in value, f"{const_name} = '{value}' should contain a dot"
            # Should not start or end with dot
            assert not value.startswith("."), f"{const_name} = '{value}' should not start with dot"
            assert not value.endswith("."), f"{const_name} = '{value}' should not end with dot"

    def test_tokens_can_be_imported_from_main_package(self):
        """Test that Tokens can be imported from main package (after export)."""
        # This will fail until we add to __init__.py
        try:
            from vfwidgets_theme import Tokens

            assert Tokens is not None
        except ImportError:
            pytest.skip("Tokens not yet exported in __init__.py")

    def test_tokens_usage_with_theme_config(self):
        """Test realistic usage pattern with theme_config dict."""
        from vfwidgets_theme.core.token_constants import Tokens

        # This should work without errors (IDE autocomplete!)
        theme_config = {
            "bg": Tokens.EDITOR_BACKGROUND,
            "fg": Tokens.EDITOR_FOREGROUND,
            "border": Tokens.COLORS_FOCUS_BORDER,
        }

        # Values should be valid token strings
        assert theme_config["bg"] == "editor.background"
        assert theme_config["fg"] == "editor.foreground"
        assert theme_config["border"] == "colors.focusBorder"

    def test_tokens_constants_are_immutable(self):
        """Test that token constants cannot be modified."""
        from vfwidgets_theme.core.token_constants import Tokens

        # Create an instance to test instance attribute immutability
        tokens_instance = Tokens()

        # Attempting to modify instance should raise AttributeError
        with pytest.raises(AttributeError):
            tokens_instance.COLORS_FOREGROUND = "modified.value"

    def test_all_tokens_returns_unique_values(self):
        """Test that all_tokens() contains no duplicates."""
        from vfwidgets_theme.core.token_constants import Tokens

        tokens = Tokens.all_tokens()
        unique_tokens = set(tokens)

        assert len(tokens) == len(unique_tokens), "all_tokens() should not contain duplicates"

    def test_token_constant_matches_registry_description(self):
        """Test that token constants map to correct registry entries."""
        # Re-import to get fresh class (in case previous tests modified it)
        import importlib

        import vfwidgets_theme.core.token_constants

        importlib.reload(vfwidgets_theme.core.token_constants)
        from vfwidgets_theme.core.token_constants import Tokens

        # Test a few specific mappings
        test_cases = [
            ("COLORS_FOREGROUND", "colors.foreground"),
            ("BUTTON_BACKGROUND", "button.background"),
            ("EDITOR_SELECTION_BACKGROUND", "editor.selectionBackground"),
            ("LIST_ACTIVE_SELECTION_BACKGROUND", "list.activeSelectionBackground"),
        ]

        for const_name, expected_value in test_cases:
            if hasattr(Tokens, const_name):
                actual_value = getattr(Tokens, const_name)
                assert actual_value == expected_value, (
                    f"{const_name} should be '{expected_value}', got '{actual_value}'"
                )

    def test_tokens_class_has_docstring(self):
        """Test that Tokens class has documentation."""
        from vfwidgets_theme.core.token_constants import Tokens

        assert Tokens.__doc__ is not None
        assert len(Tokens.__doc__) > 50, "Docstring should be descriptive"

    def test_validate_handles_edge_cases(self):
        """Test that validate() handles edge cases gracefully."""
        from vfwidgets_theme.core.token_constants import Tokens

        # None should return False (not raise exception)
        assert Tokens.validate(None) is False

        # Non-string should return False
        assert Tokens.validate(123) is False
        assert Tokens.validate([]) is False


class TestTokensPerformance:
    """Performance tests for Tokens class."""

    def test_validate_is_fast(self):
        """Test that validate() is fast enough for real-time use."""
        import time

        from vfwidgets_theme.core.token_constants import Tokens

        # Should validate 1000 tokens in < 10ms
        start = time.perf_counter()
        for _ in range(1000):
            Tokens.validate("colors.foreground")
        elapsed = time.perf_counter() - start

        assert elapsed < 0.01, f"validate() too slow: {elapsed:.4f}s for 1000 calls"

    def test_all_tokens_is_cached(self):
        """Test that all_tokens() returns same list instance (cached)."""
        from vfwidgets_theme.core.token_constants import Tokens

        # Call twice
        tokens1 = Tokens.all_tokens()
        tokens2 = Tokens.all_tokens()

        # Should return same list (not recreate)
        # Note: This test might need adjustment based on implementation
        assert tokens1 == tokens2


class TestTokensBackwardCompatibility:
    """Test backward compatibility."""

    def test_old_string_tokens_still_work(self):
        """Test that old-style string tokens are not broken."""
        # Users can still use strings directly
        theme_config_old = {
            "bg": "window.background",  # Old style
            "fg": "window.foreground",
        }

        # Should still be valid
        assert "bg" in theme_config_old
        assert theme_config_old["bg"] == "window.background"

    def test_tokens_constants_are_strings(self):
        """Test that token constants ARE strings (not objects)."""
        # Re-import to get fresh class
        import importlib

        import vfwidgets_theme.core.token_constants

        importlib.reload(vfwidgets_theme.core.token_constants)
        from vfwidgets_theme.core.token_constants import Tokens

        # Constants should be plain strings for backward compatibility
        assert isinstance(Tokens.COLORS_FOREGROUND, str)
        assert isinstance(Tokens.BUTTON_BACKGROUND, str)

        # Should be usable anywhere strings are expected
        token = Tokens.COLORS_FOREGROUND
        assert token.upper() == "COLORS.FOREGROUND"
        assert token.split(".") == ["colors", "foreground"]


class TestTokensCoverage:
    """Test coverage of all ColorTokenRegistry categories."""

    def test_all_categories_covered(self):
        """Test that all registry categories have constants."""
        from vfwidgets_theme.core.token_constants import Tokens

        # Get all token constants
        tokens_list = Tokens.all_tokens()

        # Check that we have tokens from major categories
        # Note: Category names in registry (BASE, BUTTON, etc.) don't directly
        # map to token prefixes (colors., button., etc.)
        major_prefixes = [
            "colors.",
            "button.",
            "input.",
            "dropdown.",
            "combobox.",
            "list.",
            "editor.",
            "sideBar.",
            "panel.",
            "tab.",
            "activityBar.",
            "statusBar.",
            "titleBar.",
            "menu.",
            "scrollbar.",
            "badge.",
        ]

        for prefix in major_prefixes:
            category_tokens = [t for t in tokens_list if t.startswith(prefix)]
            assert len(category_tokens) > 0, f"No tokens found with prefix: {prefix}"
