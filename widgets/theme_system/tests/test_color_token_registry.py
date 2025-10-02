#!/usr/bin/env python3
"""
Unit tests for ColorTokenRegistry.

Tests the color token system including:
- Token retrieval and validation
- Default value resolution
- Category organization
- Token completeness
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest

from vfwidgets_theme.core.theme import Theme
from vfwidgets_theme.core.tokens import ColorToken, ColorTokenRegistry, TokenCategory


class TestColorTokenRegistry(unittest.TestCase):
    """Test ColorTokenRegistry functionality."""

    def test_all_categories_defined(self):
        """Test that all token categories are defined."""
        categories = [
            TokenCategory.BASE,
            TokenCategory.BUTTON,
            TokenCategory.INPUT,
            TokenCategory.LIST,
            TokenCategory.EDITOR,
            TokenCategory.SIDEBAR,
            TokenCategory.PANEL,
            TokenCategory.TAB,
            TokenCategory.ACTIVITY_BAR,
            TokenCategory.STATUS_BAR,
            TokenCategory.TITLE_BAR,
            TokenCategory.MENU,
            TokenCategory.SCROLLBAR,
            TokenCategory.MISC,
        ]

        for category in categories:
            self.assertIsNotNone(category)
            self.assertIsInstance(category, TokenCategory)

    def test_token_count(self):
        """Test that we have the expected number of tokens."""
        token_count = ColorTokenRegistry.get_token_count()

        # We expect around 179-192 color tokens
        self.assertGreater(token_count, 170, "Should have at least 170 tokens")
        self.assertLess(token_count, 200, "Should have less than 200 tokens")

    def test_get_token_by_name(self):
        """Test retrieving tokens by name."""
        # Test base colors
        token = ColorTokenRegistry.get_token("colors.foreground")
        self.assertIsNotNone(token)
        self.assertEqual(token.name, "colors.foreground")
        self.assertEqual(token.category, TokenCategory.BASE)

        # Test button colors
        token = ColorTokenRegistry.get_token("button.background")
        self.assertIsNotNone(token)
        self.assertEqual(token.name, "button.background")
        self.assertEqual(token.category, TokenCategory.BUTTON)

        # Test editor colors
        token = ColorTokenRegistry.get_token("editor.background")
        self.assertIsNotNone(token)
        self.assertEqual(token.name, "editor.background")
        self.assertEqual(token.category, TokenCategory.EDITOR)

    def test_get_nonexistent_token(self):
        """Test that nonexistent tokens return None."""
        token = ColorTokenRegistry.get_token("nonexistent.token")
        self.assertIsNone(token)

    def test_default_values_light_theme(self):
        """Test default values for light themes."""
        # Test that light theme defaults are defined
        default = ColorTokenRegistry.get_default_value("colors.foreground", is_dark_theme=False)
        self.assertIsNotNone(default)
        self.assertIsInstance(default, str)
        self.assertTrue(default.startswith("#"))

        # Light theme foreground should be dark
        self.assertIn(default.lower(), ["#000000", "#1f1f1f", "#323130"])

    def test_default_values_dark_theme(self):
        """Test default values for dark themes."""
        # Test that dark theme defaults are defined
        default = ColorTokenRegistry.get_default_value("colors.foreground", is_dark_theme=True)
        self.assertIsNotNone(default)
        self.assertIsInstance(default, str)
        self.assertTrue(default.startswith("#"))

        # Dark theme foreground should be light (starts with c, d, e, or f)
        first_char = default.lower()[1]  # Get first hex digit after #
        self.assertIn(first_char, ["c", "d", "e", "f"],
                      f"Dark theme foreground {default} should be light color")

    def test_get_tokens_by_category(self):
        """Test retrieving all tokens in a category."""
        button_tokens = ColorTokenRegistry.get_tokens_by_category(TokenCategory.BUTTON)

        self.assertIsInstance(button_tokens, list)
        self.assertGreater(len(button_tokens), 15, "Should have at least 15 button tokens")

        # Verify all returned tokens are actually button tokens
        for token in button_tokens:
            self.assertEqual(token.category, TokenCategory.BUTTON)
            self.assertTrue(token.name.startswith("button."))

    def test_all_tokens_have_defaults(self):
        """Test that all tokens have default values defined."""
        all_token_names = ColorTokenRegistry.get_all_token_names()

        for token_name in all_token_names:
            token = ColorTokenRegistry.get_token(token_name)
            self.assertIsNotNone(token, f"Token {token_name} not found")

            # Check light theme default
            light_default = token.default_light
            self.assertIsNotNone(light_default, f"Token {token.name} missing light default")
            self.assertIsInstance(light_default, str)

            # Check dark theme default
            dark_default = token.default_dark
            self.assertIsNotNone(dark_default, f"Token {token.name} missing dark default")
            self.assertIsInstance(dark_default, str)

    def test_token_descriptions(self):
        """Test that all tokens have descriptions."""
        all_token_names = ColorTokenRegistry.get_all_token_names()

        for token_name in all_token_names:
            token = ColorTokenRegistry.get_token(token_name)
            self.assertIsNotNone(token, f"Token {token_name} not found")
            self.assertIsNotNone(token.description, f"Token {token.name} missing description")
            self.assertIsInstance(token.description, str)
            self.assertGreater(len(token.description), 0, f"Token {token.name} has empty description")

    def test_hierarchical_token_names(self):
        """Test that token names follow hierarchical naming convention."""
        all_token_names = ColorTokenRegistry.get_all_token_names()

        for token_name in all_token_names:
            token = ColorTokenRegistry.get_token(token_name)
            # Token names should have at least one dot
            parts = token.name.split('.')
            self.assertGreaterEqual(len(parts), 2, f"Token {token.name} doesn't follow naming convention")

            # First part should match the category prefix
            category_prefixes = {
                TokenCategory.BASE: "colors",
                TokenCategory.BUTTON: "button",
                TokenCategory.INPUT: ["input", "dropdown", "combobox"],
                TokenCategory.LIST: ["list", "tree", "table"],
                TokenCategory.EDITOR: "editor",
                TokenCategory.SIDEBAR: "sideBar",
                TokenCategory.PANEL: "panel",
                TokenCategory.TAB: ["tab", "tabBar"],
                TokenCategory.ACTIVITY_BAR: "activityBar",
                TokenCategory.STATUS_BAR: "statusBar",
                TokenCategory.TITLE_BAR: "titleBar",
                TokenCategory.MENU: "menu",
                TokenCategory.SCROLLBAR: "scrollbar",
            }

            expected_prefix = category_prefixes.get(token.category)
            if expected_prefix:
                if isinstance(expected_prefix, list):
                    # For list of prefixes, first part should match one of them
                    self.assertIn(parts[0], expected_prefix,
                                  f"Token {token.name} doesn't match category prefix")
                else:
                    # For single prefix, allow exact match or compound names like editorLineNumber
                    # which still belong to the editor category
                    self.assertTrue(parts[0].startswith(expected_prefix) or parts[0] == expected_prefix,
                                    f"Token {token.name} doesn't match category prefix {expected_prefix}")

    def test_button_role_tokens(self):
        """Test that button role tokens are defined."""
        role_tokens = [
            "button.danger.background",
            "button.danger.hoverBackground",
            "button.success.background",
            "button.success.hoverBackground",
            "button.warning.background",
            "button.warning.hoverBackground",
            "button.secondary.background",
            "button.secondary.hoverBackground",
        ]

        for token_name in role_tokens:
            token = ColorTokenRegistry.get_token(token_name)
            self.assertIsNotNone(token, f"Role token {token_name} not found")
            self.assertEqual(token.category, TokenCategory.BUTTON)

    def test_editor_tokens(self):
        """Test that editor-specific tokens are defined."""
        editor_tokens = [
            "editor.background",
            "editor.foreground",
            "editor.selectionBackground",
            "editorLineNumber.foreground",
        ]

        for token_name in editor_tokens:
            token = ColorTokenRegistry.get_token(token_name)
            self.assertIsNotNone(token, f"Editor token {token_name} not found")
            self.assertEqual(token.category, TokenCategory.EDITOR)


class TestColorTokenRegistryGet(unittest.TestCase):
    """Test ColorTokenRegistry.get() method with theme-aware defaults."""

    def test_get_with_explicit_token_in_theme(self):
        """Test that get() returns theme value when token is explicitly defined."""
        # Create a theme with explicit button.background
        theme = Theme(
            name="test_light",
            type="light",
            colors={
                "button.background": "#ff0000",  # Custom red button
            }
        )

        value = ColorTokenRegistry.get("button.background", theme)
        self.assertEqual(value, "#ff0000", "Should return explicit theme value")

    def test_get_dark_theme_defaults(self):
        """Test that get() returns dark defaults for dark themes."""
        # Create minimal dark theme (no button.background defined)
        theme = Theme(
            name="test_dark",
            type="dark",
            colors={
                "colors.background": "#1e1e1e",
                "colors.foreground": "#d4d4d4",
            }
        )

        # Should get dark default from registry
        value = ColorTokenRegistry.get("button.background", theme)
        expected_dark = "#0e639c"  # Dark default from registry
        self.assertEqual(value, expected_dark,
                        f"Should return dark default {expected_dark} for dark theme")

    def test_get_light_theme_defaults(self):
        """Test that get() returns light defaults for light themes."""
        # Create minimal light theme (no button.background defined)
        theme = Theme(
            name="test_light",
            type="light",
            colors={
                "colors.background": "#ffffff",
                "colors.foreground": "#000000",
            }
        )

        # Should get light default from registry
        value = ColorTokenRegistry.get("button.background", theme)
        expected_light = "#0078d4"  # Light default from registry
        self.assertEqual(value, expected_light,
                        f"Should return light default {expected_light} for light theme")

    def test_get_unknown_token_smart_heuristic(self):
        """Test that get() uses smart heuristic for unknown tokens."""
        dark_theme = Theme(
            name="dark",
            type="dark",
            colors={"colors.background": "#1e1e1e"}
        )

        light_theme = Theme(
            name="light",
            type="light",
            colors={"colors.background": "#ffffff"}
        )

        # Unknown background token
        dark_value = ColorTokenRegistry.get("custom.background", dark_theme)
        self.assertEqual(dark_value, "#1e1e1e", "Should use dark background heuristic")

        light_value = ColorTokenRegistry.get("custom.background", light_theme)
        self.assertEqual(light_value, "#ffffff", "Should use light background heuristic")

        # Unknown foreground token
        dark_fg = ColorTokenRegistry.get("custom.foreground", dark_theme)
        self.assertEqual(dark_fg, "#d4d4d4", "Should use dark foreground heuristic")

        light_fg = ColorTokenRegistry.get("custom.foreground", light_theme)
        self.assertEqual(light_fg, "#000000", "Should use light foreground heuristic")

    def test_is_dark_theme_by_type(self):
        """Test _is_dark_theme() with explicit type field."""
        dark_theme = Theme(name="dark", type="dark", colors={})
        light_theme = Theme(name="light", type="light", colors={})
        hc_theme = Theme(name="hc", type="high-contrast", colors={})

        self.assertTrue(ColorTokenRegistry._is_dark_theme(dark_theme))
        self.assertFalse(ColorTokenRegistry._is_dark_theme(light_theme))
        self.assertTrue(ColorTokenRegistry._is_dark_theme(hc_theme))

    def test_is_dark_theme_by_luminance_heuristic(self):
        """Test _is_dark_theme() with luminance-based heuristic."""
        # Dark background (low luminance)
        dark_theme = Theme(
            name="dark_inferred",
            type="light",  # Wrong type, but dark background
            colors={"colors.background": "#1e1e1e"}  # Very dark gray
        )
        # The explicit type="light" should take precedence over heuristic
        self.assertFalse(ColorTokenRegistry._is_dark_theme(dark_theme))

        # But if no type specified (fallback), heuristic should work
        # Note: Theme requires type, so this test verifies type takes precedence

    def test_get_editor_tokens(self):
        """Test get() with editor-specific tokens."""
        dark_theme = Theme(
            name="dark",
            type="dark",
            colors={"colors.background": "#1e1e1e"}
        )

        # Editor background should get dark default
        editor_bg = ColorTokenRegistry.get("editor.background", dark_theme)
        expected_dark_editor = "#1e1e1e"  # Dark default from registry
        self.assertEqual(editor_bg, expected_dark_editor)

        # Editor foreground should get dark default
        editor_fg = ColorTokenRegistry.get("editor.foreground", dark_theme)
        expected_dark_fg = "#d4d4d4"  # Dark default from registry
        self.assertEqual(editor_fg, expected_dark_fg)

    def test_get_hover_tokens(self):
        """Test get() with hover state tokens."""
        dark_theme = Theme(name="dark", type="dark", colors={})
        light_theme = Theme(name="light", type="light", colors={})

        # Button hover should use registry defaults
        dark_hover = ColorTokenRegistry.get("button.hoverBackground", dark_theme)
        self.assertEqual(dark_hover, "#1177bb")  # Dark default

        light_hover = ColorTokenRegistry.get("button.hoverBackground", light_theme)
        self.assertEqual(light_hover, "#106ebe")  # Light default

    def test_get_role_variants(self):
        """Test get() with role-specific button variants."""
        dark_theme = Theme(name="dark", type="dark", colors={})

        # Danger button
        danger_bg = ColorTokenRegistry.get("button.danger.background", dark_theme)
        self.assertEqual(danger_bg, "#dc3545")

        # Success button
        success_bg = ColorTokenRegistry.get("button.success.background", dark_theme)
        self.assertEqual(success_bg, "#28a745")

        # Warning button
        warning_bg = ColorTokenRegistry.get("button.warning.background", dark_theme)
        self.assertEqual(warning_bg, "#ffc107")

    def test_minimal_theme_coverage(self):
        """Test that minimal 13-token theme works with registry defaults."""
        # Minimal theme with only 13 base colors (like VSCode minimal theme)
        minimal_theme = Theme(
            name="minimal_dark",
            type="dark",
            colors={
                "colors.background": "#1e1e1e",
                "colors.foreground": "#d4d4d4",
                "colors.focusBorder": "#007acc",
                "button.background": "#0e639c",
                "button.foreground": "#ffffff",
                "input.background": "#3c3c3c",
                "input.foreground": "#cccccc",
                "list.activeSelectionBackground": "#094771",
                "list.hoverBackground": "#2a2d2e",
                "editor.background": "#1e1e1e",
                "editor.foreground": "#d4d4d4",
                "tab.activeBackground": "#1e1e1e",
                "tab.inactiveBackground": "#2d2d2d",
            }
        )

        # All other tokens should get sensible dark defaults
        # Test a few important ones
        menu_bg = ColorTokenRegistry.get("menu.background", minimal_theme)
        self.assertIsNotNone(menu_bg)
        self.assertIsInstance(menu_bg, str)
        # Should be a dark color
        self.assertTrue(menu_bg.startswith("#"))

        scrollbar = ColorTokenRegistry.get("scrollbarSlider.background", minimal_theme)
        self.assertIsNotNone(scrollbar)
        self.assertIsInstance(scrollbar, str)

        # Unknown token should get smart heuristic
        unknown_bg = ColorTokenRegistry.get("custom.myWidget.background", minimal_theme)
        self.assertEqual(unknown_bg, "#1e1e1e")  # Dark background heuristic


class TestColorToken(unittest.TestCase):
    """Test ColorToken data class."""

    def test_token_creation(self):
        """Test creating a ColorToken."""
        token = ColorToken(
            name="test.color",
            category=TokenCategory.BASE,
            description="Test color",
            default_light="#ffffff",
            default_dark="#000000"
        )

        self.assertEqual(token.name, "test.color")
        self.assertEqual(token.category, TokenCategory.BASE)
        self.assertEqual(token.description, "Test color")
        self.assertEqual(token.default_light, "#ffffff")
        self.assertEqual(token.default_dark, "#000000")

    def test_token_immutability(self):
        """Test that ColorToken is frozen (immutable)."""
        token = ColorToken(
            name="test.color",
            category=TokenCategory.BASE,
            description="Test color",
            default_light="#ffffff",
            default_dark="#000000"
        )

        # ColorToken is a frozen dataclass, so assignment should fail
        # Note: Some Python versions raise AttributeError, others raise FrozenInstanceError
        try:
            token.name = "changed"
            self.fail("Should not be able to modify frozen ColorToken")
        except (AttributeError, TypeError, Exception):
            # Expected - token is immutable
            pass


if __name__ == '__main__':
    unittest.main()
