"""Unit tests for ThemeBridge.

These tests validate theme token resolution, fallback chains,
and CSS variable generation without requiring a real QWebEngineView.
"""

from unittest.mock import Mock

import pytest

from vfwidgets_markdown.bridges.theme_bridge import (
    ThemeBridge,
    ThemeTokenMapping,
)


@pytest.fixture
def mock_page():
    """Mock QWebEnginePage for testing."""
    page = Mock()
    page.runJavaScript = Mock()
    return page


@pytest.fixture
def simple_theme():
    """Simple theme with basic colors."""
    theme = Mock()
    theme.name = "test-theme"
    theme.colors = {
        "markdown": {"colors": {"foreground": "#ffffff", "background": "#000000"}},
        "editor": {"foreground": "#cccccc", "background": "#1e1e1e"},
    }
    return theme


@pytest.fixture
def incomplete_theme():
    """Theme with missing markdown colors (uses fallbacks)."""
    theme = Mock()
    theme.name = "incomplete-theme"
    theme.colors = {"editor": {"foreground": "#cccccc", "background": "#1e1e1e"}}
    return theme


@pytest.fixture
def empty_theme():
    """Theme with no colors (uses defaults)."""
    theme = Mock()
    theme.name = "empty-theme"
    theme.colors = {}
    return theme


class TestThemeTokenMapping:
    """Test ThemeTokenMapping dataclass."""

    def test_basic_mapping(self):
        """Test basic token mapping creation."""
        mapping = ThemeTokenMapping(
            css_var="md-fg",
            token_path="markdown.colors.foreground",
            fallback_paths=["editor.foreground"],
            default_value="#ffffff",
        )

        assert mapping.css_var == "md-fg"
        assert mapping.token_path == "markdown.colors.foreground"
        assert mapping.fallback_paths == ["editor.foreground"]
        assert mapping.default_value == "#ffffff"

    def test_default_fallback_list(self):
        """Test fallback_paths defaults to empty list."""
        mapping = ThemeTokenMapping(css_var="md-fg", token_path="markdown.colors.foreground")

        assert mapping.fallback_paths == []
        assert mapping.default_value is None


class TestThemeBridgeInit:
    """Test ThemeBridge initialization."""

    def test_basic_init(self, mock_page):
        """Test basic initialization."""
        mappings = [
            ThemeTokenMapping("md-fg", "markdown.colors.foreground"),
        ]

        bridge = ThemeBridge(page=mock_page, token_mappings=mappings)

        assert bridge._page == mock_page
        assert bridge._token_mappings == mappings
        assert bridge._css_injection_callback is None
        assert bridge._last_result is None

    def test_init_with_callback(self, mock_page):
        """Test initialization with custom CSS callback."""

        def custom_css(vars):
            return "/* custom */"

        mappings = [
            ThemeTokenMapping("md-fg", "markdown.colors.foreground"),
        ]

        bridge = ThemeBridge(
            page=mock_page, token_mappings=mappings, css_injection_callback=custom_css
        )

        assert bridge._css_injection_callback == custom_css


class TestTokenResolution:
    """Test theme token resolution with fallback chains."""

    def test_resolve_primary_token(self, mock_page, simple_theme):
        """Test resolving token from primary path."""
        mappings = [
            ThemeTokenMapping(
                css_var="md-fg",
                token_path="markdown.colors.foreground",
                fallback_paths=["editor.foreground"],
            )
        ]

        bridge = ThemeBridge(page=mock_page, token_mappings=mappings)
        result = bridge.apply_theme(simple_theme)

        assert result.success
        assert "--md-fg" in result.css_variables_set
        assert result.css_variables_set["--md-fg"] == "#ffffff"
        assert len(result.used_fallbacks) == 0  # Primary path used

    def test_resolve_with_fallback(self, mock_page, incomplete_theme):
        """Test resolving token using fallback path."""
        mappings = [
            ThemeTokenMapping(
                css_var="md-fg",
                token_path="markdown.colors.foreground",  # Missing
                fallback_paths=["editor.foreground"],  # Available
            )
        ]

        bridge = ThemeBridge(page=mock_page, token_mappings=mappings)
        result = bridge.apply_theme(incomplete_theme)

        assert result.success
        assert "--md-fg" in result.css_variables_set
        assert result.css_variables_set["--md-fg"] == "#cccccc"
        assert "md-fg" in result.used_fallbacks
        assert result.used_fallbacks["md-fg"] == "editor.foreground"

    def test_resolve_with_default(self, mock_page, empty_theme):
        """Test resolving token using default value."""
        mappings = [
            ThemeTokenMapping(
                css_var="md-fg",
                token_path="markdown.colors.foreground",  # Missing
                fallback_paths=["editor.foreground"],  # Missing
                default_value="#c9d1d9",  # Use this
            )
        ]

        bridge = ThemeBridge(page=mock_page, token_mappings=mappings)
        result = bridge.apply_theme(empty_theme)

        assert result.success
        assert "--md-fg" in result.css_variables_set
        assert result.css_variables_set["--md-fg"] == "#c9d1d9"
        assert "md-fg" in result.used_fallbacks
        assert result.used_fallbacks["md-fg"] == "default"

    def test_resolve_missing_token_no_default(self, mock_page, empty_theme):
        """Test token with no value and no default."""
        mappings = [
            ThemeTokenMapping(
                css_var="md-fg",
                token_path="markdown.colors.foreground",  # Missing
                fallback_paths=[],  # No fallbacks
                default_value=None,  # No default
            )
        ]

        bridge = ThemeBridge(page=mock_page, token_mappings=mappings)
        result = bridge.apply_theme(empty_theme)

        assert result.success  # Still succeeds, just missing token
        assert "--md-fg" not in result.css_variables_set  # Not set
        assert "markdown.colors.foreground" in result.missing_tokens


class TestCSSInjection:
    """Test CSS variable injection into page."""

    def test_css_injection_called(self, mock_page, simple_theme):
        """Test that runJavaScript is called with correct code."""
        mappings = [
            ThemeTokenMapping("md-fg", "markdown.colors.foreground"),
        ]

        bridge = ThemeBridge(page=mock_page, token_mappings=mappings)
        result = bridge.apply_theme(simple_theme)

        assert result.success
        mock_page.runJavaScript.assert_called_once()

        # Check JavaScript code contains CSS variable
        js_code = mock_page.runJavaScript.call_args[0][0]
        assert "--md-fg: #ffffff" in js_code
        assert "document.body.style.cssText" in js_code

    def test_multiple_css_variables(self, mock_page, simple_theme):
        """Test injection of multiple CSS variables."""
        mappings = [
            ThemeTokenMapping("md-fg", "markdown.colors.foreground"),
            ThemeTokenMapping("md-bg", "markdown.colors.background"),
        ]

        bridge = ThemeBridge(page=mock_page, token_mappings=mappings)
        result = bridge.apply_theme(simple_theme)

        assert result.success
        assert len(result.css_variables_set) == 2
        assert "--md-fg" in result.css_variables_set
        assert "--md-bg" in result.css_variables_set

        js_code = mock_page.runJavaScript.call_args[0][0]
        assert "--md-fg: #ffffff" in js_code
        assert "--md-bg: #000000" in js_code

    def test_custom_css_callback(self, mock_page, simple_theme):
        """Test custom CSS injection via callback."""
        custom_css_called = []

        def custom_css(vars):
            custom_css_called.append(vars)
            return "pre { background: var(--md-code-bg); }"

        mappings = [
            ThemeTokenMapping("md-code-bg", "markdown.colors.code.background"),
        ]

        bridge = ThemeBridge(
            page=mock_page, token_mappings=mappings, css_injection_callback=custom_css
        )

        # Add code background to theme
        simple_theme.colors["markdown"]["colors"]["code"] = {"background": "#161b22"}

        result = bridge.apply_theme(simple_theme)

        assert result.success
        assert len(custom_css_called) == 1  # Callback invoked
        assert "--md-code-bg" in custom_css_called[0]  # Received CSS vars

        js_code = mock_page.runJavaScript.call_args[0][0]
        assert "pre { background: var(--md-code-bg); }" in js_code


class TestThemeValidation:
    """Test theme completeness validation."""

    def test_validate_complete_theme(self, mock_page, simple_theme):
        """Test validating a complete theme."""
        mappings = [
            ThemeTokenMapping("md-fg", "markdown.colors.foreground"),
            ThemeTokenMapping("md-bg", "markdown.colors.background"),
        ]

        bridge = ThemeBridge(page=mock_page, token_mappings=mappings)
        validation = bridge.validate_theme(simple_theme)

        assert validation["complete"] is True
        assert validation["completeness_percentage"] == 100.0
        assert len(validation["missing_tokens"]) == 0
        assert len(validation["present_tokens"]) == 2

    def test_validate_incomplete_theme(self, mock_page, incomplete_theme):
        """Test validating an incomplete theme."""
        mappings = [
            ThemeTokenMapping("md-fg", "markdown.colors.foreground"),  # Missing
            ThemeTokenMapping("md-bg", "markdown.colors.background"),  # Missing
            ThemeTokenMapping("ed-fg", "editor.foreground"),  # Present
        ]

        bridge = ThemeBridge(page=mock_page, token_mappings=mappings)
        validation = bridge.validate_theme(incomplete_theme)

        assert validation["complete"] is False
        assert validation["completeness_percentage"] == pytest.approx(33.33, abs=0.1)
        assert len(validation["missing_tokens"]) == 2
        assert "markdown.colors.foreground" in validation["missing_tokens"]
        assert "markdown.colors.background" in validation["missing_tokens"]
        assert "editor.foreground" in validation["present_tokens"]


class TestErrorHandling:
    """Test error handling in ThemeBridge."""

    def test_apply_theme_with_none_theme(self, mock_page):
        """Test applying None theme."""
        mappings = [
            ThemeTokenMapping("md-fg", "markdown.colors.foreground"),
        ]

        bridge = ThemeBridge(page=mock_page, token_mappings=mappings)
        result = bridge.apply_theme(None)

        assert result.success is False
        assert "No theme provided" in result.errors
        assert len(result.css_variables_set) == 0

    def test_get_nested_value_with_invalid_path(self, mock_page):
        """Test _get_nested_value with invalid path."""
        bridge = ThemeBridge(page=mock_page, token_mappings=[])

        colors = {"markdown": {"colors": {"foreground": "#fff"}}}

        # Valid path
        assert bridge._get_nested_value(colors, "markdown.colors.foreground") == "#fff"

        # Invalid paths
        assert bridge._get_nested_value(colors, "markdown.colors.invalid") is None
        assert bridge._get_nested_value(colors, "invalid.path") is None
        assert bridge._get_nested_value(colors, "markdown.colors.foreground.extra") is None


class TestLastResult:
    """Test get_last_result() functionality."""

    def test_last_result_initially_none(self, mock_page):
        """Test last result is None before first application."""
        bridge = ThemeBridge(page=mock_page, token_mappings=[])
        assert bridge.get_last_result() is None

    def test_last_result_after_apply(self, mock_page, simple_theme):
        """Test last result is stored after application."""
        mappings = [
            ThemeTokenMapping("md-fg", "markdown.colors.foreground"),
        ]

        bridge = ThemeBridge(page=mock_page, token_mappings=mappings)
        result1 = bridge.apply_theme(simple_theme)

        last_result = bridge.get_last_result()
        assert last_result is not None
        assert last_result.success == result1.success
        assert last_result.css_variables_set == result1.css_variables_set


class TestFlatStructureSupport:
    """Test flat dict structure support (from Theme Studio)."""

    def test_flat_structure_token_resolution(self, mock_page):
        """Test resolving tokens from flat color dict (Theme Studio format)."""
        from vfwidgets_theme.core.theme import Theme

        # Create theme with flat structure (how Theme Studio sends it)
        flat_theme = Theme(
            name="Test Flat",
            colors={
                "colors.background": "#1e1e1e",
                "colors.foreground": "#d4d4d4",
                "markdown.colors.code.background": "#55ffff",  # Flat key!
            },
        )

        mappings = [
            ThemeTokenMapping("md-code-bg", "markdown.colors.code.background"),
        ]

        bridge = ThemeBridge(page=mock_page, token_mappings=mappings)
        result = bridge.apply_theme(flat_theme)

        assert result.success
        assert "--md-code-bg" in result.css_variables_set
        assert result.css_variables_set["--md-code-bg"] == "#55ffff"
        assert len(result.missing_tokens) == 0

    def test_flat_with_fallback(self, mock_page):
        """Test flat structure with fallback token resolution."""
        from vfwidgets_theme.core.theme import Theme

        # Primary token missing, but fallback present
        flat_theme = Theme(
            name="Test Fallback",
            colors={
                "input.background": "#2d2d2d",  # Fallback present
            },
        )

        mappings = [
            ThemeTokenMapping(
                "md-code-bg",
                "markdown.colors.code.background",
                fallback_paths=["input.background", "widget.background"],
            ),
        ]

        bridge = ThemeBridge(page=mock_page, token_mappings=mappings)
        result = bridge.apply_theme(flat_theme)

        assert result.success
        assert "--md-code-bg" in result.css_variables_set
        assert result.css_variables_set["--md-code-bg"] == "#2d2d2d"
        assert "md-code-bg" in result.used_fallbacks
        assert result.used_fallbacks["md-code-bg"] == "input.background"
