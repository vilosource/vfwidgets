"""
Tests for VSCode theme importer.
"""

import pytest
import json
import tempfile
from pathlib import Path

from vfwidgets_theme.vscode.importer import VSCodeThemeImporter, VSCodeTokenColor
from vfwidgets_theme.core.theme import Theme
from vfwidgets_theme.errors import ThemeSystemError


class TestVSCodeThemeImporter:
    """Test cases for VSCodeThemeImporter."""

    @pytest.fixture
    def importer(self):
        """Create theme importer."""
        return VSCodeThemeImporter()

    @pytest.fixture
    def sample_vscode_theme(self):
        """Sample VSCode theme data."""
        return {
            "name": "Test Dark Theme",
            "type": "dark",
            "colors": {
                "editor.background": "#1e1e1e",
                "editor.foreground": "#d4d4d4",
                "activityBar.background": "#2d2d30",
                "sideBar.background": "#252526",
                "statusBar.background": "#007acc",
                "tab.activeBackground": "#1e1e1e",
                "tab.inactiveBackground": "#2d2d30",
                "titleBar.activeBackground": "#3c3c3c",
                "input.background": "#3c3c3c",
                "button.background": "#0e639c",
                "list.activeSelectionBackground": "#094771",
                "focusBorder": "#007fd4"
            },
            "tokenColors": [
                {
                    "name": "Comment",
                    "scope": "comment",
                    "settings": {
                        "foreground": "#6A9955",
                        "fontStyle": "italic"
                    }
                },
                {
                    "name": "String",
                    "scope": ["string", "string.quoted"],
                    "settings": {
                        "foreground": "#ce9178"
                    }
                },
                {
                    "name": "Keyword",
                    "scope": "keyword",
                    "settings": {
                        "foreground": "#569cd6"
                    }
                }
            ]
        }

    @pytest.fixture
    def sample_light_theme(self):
        """Sample light VSCode theme."""
        return {
            "name": "Test Light Theme",
            "type": "light",
            "colors": {
                "editor.background": "#ffffff",
                "editor.foreground": "#000000",
                "activityBar.background": "#f3f3f3",
                "sideBar.background": "#f8f8f8"
            },
            "tokenColors": []
        }

    def test_determine_theme_type_explicit(self, importer):
        """Test theme type determination with explicit type."""
        dark_theme = {"type": "dark", "colors": {}}
        assert importer._determine_theme_type(dark_theme) == "dark"

        light_theme = {"type": "light", "colors": {}}
        assert importer._determine_theme_type(light_theme) == "light"

    def test_determine_theme_type_inferred(self, importer):
        """Test theme type determination by inference."""
        # Dark background
        dark_theme = {"colors": {"editor.background": "#1e1e1e"}}
        assert importer._determine_theme_type(dark_theme) == "dark"

        # Light background
        light_theme = {"colors": {"editor.background": "#ffffff"}}
        assert importer._determine_theme_type(light_theme) == "light"

        # Default to dark
        no_colors = {"colors": {}}
        assert importer._determine_theme_type(no_colors) == "dark"

    def test_normalize_color_hex(self, importer):
        """Test hex color normalization."""
        assert importer._normalize_color("#ff0000") == "#ff0000"
        assert importer._normalize_color(" #00ff00 ") == "#00ff00"

    def test_normalize_color_rgb(self, importer):
        """Test RGB color normalization."""
        assert importer._normalize_color("rgb(255, 0, 0)") == "#ff0000"
        assert importer._normalize_color("rgba(255, 0, 0, 0.5)") == "#ff000080"

    def test_normalize_color_named(self, importer):
        """Test named color normalization."""
        assert importer._normalize_color("white") == "#ffffff"
        assert importer._normalize_color("black") == "#000000"
        assert importer._normalize_color("red") == "#ff0000"
        assert importer._normalize_color("transparent") == "#00000000"

    def test_rgb_to_hex_conversion(self, importer):
        """Test RGB to hex conversion."""
        assert importer._rgb_to_hex("rgb(255, 0, 0)") == "#ff0000"
        assert importer._rgb_to_hex("rgb(0, 255, 0)") == "#00ff00"
        assert importer._rgb_to_hex("rgb(0, 0, 255)") == "#0000ff"

        # With alpha
        assert importer._rgb_to_hex("rgba(255, 0, 0, 0.5)") == "#ff000080"
        assert importer._rgb_to_hex("rgba(255, 0, 0, 1.0)") == "#ff0000ff"

        # Invalid format
        assert importer._rgb_to_hex("invalid") == "#000000"

    def test_extract_colors(self, importer, sample_vscode_theme):
        """Test color extraction from VSCode theme."""
        colors = importer._extract_colors(sample_vscode_theme)

        # Check mapped colors
        assert colors.background == "#1e1e1e"
        assert colors.text == "#d4d4d4"
        assert colors.sidebar_background == "#252526"
        assert colors.statusbar_background == "#007acc"
        assert colors.focus_border == "#007fd4"

    def test_extract_token_colors(self, importer, sample_vscode_theme):
        """Test token color extraction."""
        token_colors = importer._extract_token_colors(sample_vscode_theme)

        assert len(token_colors) == 3

        # Check comment token
        comment_token = token_colors[0]
        assert comment_token.name == "Comment"
        assert comment_token.scope == ["comment"]
        assert comment_token.settings["foreground"] == "#6A9955"

        # Check string token
        string_token = token_colors[1]
        assert string_token.name == "String"
        assert string_token.scope == ["string", "string.quoted"]

    def test_normalize_scope(self, importer):
        """Test scope normalization."""
        # String scope
        assert importer._normalize_scope("comment") == ["comment"]

        # Comma-separated scopes
        assert importer._normalize_scope("string, string.quoted") == ["string", "string.quoted"]

        # List scope
        assert importer._normalize_scope(["keyword", "storage"]) == ["keyword", "storage"]

        # Empty/None scope
        assert importer._normalize_scope(None) is None
        assert importer._normalize_scope("") is None

    def test_import_theme(self, importer, sample_vscode_theme):
        """Test full theme import."""
        theme = importer.import_theme(sample_vscode_theme, "Test Theme")

        assert isinstance(theme, Theme)
        assert theme.name == "Test Theme"
        assert theme.type == "dark"
        assert theme.description == "Imported from VSCode theme: Test Theme"

        # Check colors were mapped
        assert theme.colors.background == "#1e1e1e"
        assert theme.colors.text == "#d4d4d4"

        # Check token colors in metadata
        assert "vscode_token_colors" in theme.metadata
        token_colors = theme.metadata["vscode_token_colors"]
        assert len(token_colors) == 3

    def test_import_light_theme(self, importer, sample_light_theme):
        """Test importing light theme."""
        theme = importer.import_theme(sample_light_theme, "Light Theme")

        assert theme.type == "light"
        assert theme.colors.background == "#ffffff"
        assert theme.colors.text == "#000000"

    def test_import_from_file(self, importer, sample_vscode_theme):
        """Test importing theme from file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_vscode_theme, f)
            theme_path = Path(f.name)

        try:
            theme = importer.import_from_file(theme_path)

            assert isinstance(theme, Theme)
            assert theme.type == "dark"
            assert theme.colors.background == "#1e1e1e"

        finally:
            theme_path.unlink()

    def test_import_from_nonexistent_file(self, importer):
        """Test importing from non-existent file raises error."""
        with pytest.raises(ThemeSystemError, match="does not exist"):
            importer.import_from_file(Path("/nonexistent/theme.json"))

    def test_import_from_invalid_json(self, importer):
        """Test importing from invalid JSON raises error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json {")
            invalid_path = Path(f.name)

        try:
            with pytest.raises(ThemeSystemError, match="Invalid JSON"):
                importer.import_from_file(invalid_path)

        finally:
            invalid_path.unlink()

    def test_add_color_fallbacks(self, importer):
        """Test color fallback addition."""
        mapped_colors = {}
        vscode_colors = {
            "editor.background": "#282a36",
            "editor.foreground": "#f8f8f2"
        }

        importer._add_color_fallbacks(mapped_colors, vscode_colors)

        assert mapped_colors["background"] == "#282a36"
        assert mapped_colors["text"] == "#f8f8f2"
        assert "sidebar_background" in mapped_colors
        assert "statusbar_background" in mapped_colors

    def test_darken_color(self, importer):
        """Test color darkening."""
        # Darken white by 50%
        result = importer._darken_color("#ffffff", 0.5)
        assert result == "#7f7f7f"

        # Darken red by 25%
        result = importer._darken_color("#ff0000", 0.25)
        assert result == "#bf0000"

        # Invalid color returns unchanged
        result = importer._darken_color("invalid", 0.5)
        assert result == "invalid"

    def test_export_to_vscode(self, importer, sample_vscode_theme):
        """Test exporting theme to VSCode format."""
        # First import a theme
        theme = importer.import_theme(sample_vscode_theme, "Test Theme")

        # Export to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_path = Path(f.name)

        try:
            importer.export_to_vscode(theme, output_path)

            # Read back and verify
            with open(output_path, 'r') as f:
                exported_data = json.load(f)

            assert exported_data["name"] == "Test Theme"
            assert exported_data["type"] == "dark"
            assert "colors" in exported_data
            assert "tokenColors" in exported_data

            # Check some colors were mapped back
            colors = exported_data["colors"]
            assert "editor.background" in colors
            assert "editor.foreground" in colors

        finally:
            output_path.unlink()

    def test_convert_to_vscode_format(self, importer, sample_vscode_theme):
        """Test converting theme to VSCode format."""
        # Import theme first
        theme = importer.import_theme(sample_vscode_theme, "Test Theme")

        # Convert back to VSCode format
        vscode_data = importer._convert_to_vscode_format(theme)

        assert vscode_data["name"] == "Test Theme"
        assert vscode_data["type"] == "dark"

        # Check colors
        colors = vscode_data["colors"]
        assert "editor.background" in colors
        assert "editor.foreground" in colors

        # Check token colors
        token_colors = vscode_data["tokenColors"]
        assert len(token_colors) == 3

    def test_vscode_token_color_dataclass(self):
        """Test VSCodeTokenColor dataclass."""
        token = VSCodeTokenColor()
        assert token.name is None
        assert token.scope is None
        assert token.settings is None

        token = VSCodeTokenColor(
            name="Comment",
            scope=["comment"],
            settings={"foreground": "#6A9955"}
        )
        assert token.name == "Comment"
        assert token.scope == ["comment"]
        assert token.settings["foreground"] == "#6A9955"