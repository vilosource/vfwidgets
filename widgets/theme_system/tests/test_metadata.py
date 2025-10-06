"""
Tests for theme metadata system.

This module tests:
- ThemeInfo dataclass structure and validation
- ThemeMetadataProvider functionality
- Theme metadata retrieval and management
"""

from vfwidgets_theme.core.theme import Theme
from vfwidgets_theme.widgets.metadata import (
    ThemeInfo,
    ThemeMetadataProvider,
)


class TestThemeInfo:
    """Test ThemeInfo dataclass."""

    def test_theme_info_creation(self):
        """Test basic ThemeInfo creation."""
        info = ThemeInfo(
            name="vscode",
            display_name="VS Code Dark+",
            description="Microsoft VS Code's default dark theme",
            type="dark",
            tags=["popular", "editor"],
        )

        assert info.name == "vscode"
        assert info.display_name == "VS Code Dark+"
        assert info.description == "Microsoft VS Code's default dark theme"
        assert info.type == "dark"
        assert info.tags == ["popular", "editor"]
        assert info.author is None
        assert info.preview_colors == {}

    def test_theme_info_with_author(self):
        """Test ThemeInfo with author information."""
        info = ThemeInfo(
            name="custom",
            display_name="Custom Theme",
            description="A custom theme",
            type="light",
            tags=["custom"],
            author="John Doe",
        )

        assert info.author == "John Doe"

    def test_theme_info_with_preview_colors(self):
        """Test ThemeInfo with preview colors."""
        preview_colors = {
            "background": "#1e1e1e",
            "foreground": "#d4d4d4",
            "accent": "#007acc",
        }

        info = ThemeInfo(
            name="dark",
            display_name="Dark Theme",
            description="A dark theme",
            type="dark",
            tags=["dark"],
            preview_colors=preview_colors,
        )

        assert info.preview_colors == preview_colors
        assert info.preview_colors["background"] == "#1e1e1e"

    def test_theme_info_required_fields(self):
        """Test that required fields are enforced."""
        # Should work with all required fields
        info = ThemeInfo(
            name="test",
            display_name="Test",
            description="Test theme",
            type="dark",
            tags=[],
        )
        assert info is not None

    def test_theme_info_type_values(self):
        """Test valid theme type values."""
        # Dark theme
        dark = ThemeInfo(
            name="dark",
            display_name="Dark",
            description="Dark theme",
            type="dark",
            tags=[],
        )
        assert dark.type == "dark"

        # Light theme
        light = ThemeInfo(
            name="light",
            display_name="Light",
            description="Light theme",
            type="light",
            tags=[],
        )
        assert light.type == "light"

    def test_theme_info_empty_tags(self):
        """Test ThemeInfo with empty tags list."""
        info = ThemeInfo(
            name="test",
            display_name="Test",
            description="Test",
            type="dark",
            tags=[],
        )
        assert info.tags == []

    def test_theme_info_multiple_tags(self):
        """Test ThemeInfo with multiple tags."""
        tags = ["popular", "dark", "editor", "vscode"]
        info = ThemeInfo(
            name="test",
            display_name="Test",
            description="Test",
            type="dark",
            tags=tags,
        )
        assert len(info.tags) == 4
        assert "popular" in info.tags
        assert "vscode" in info.tags


class TestThemeMetadataProvider:
    """Test ThemeMetadataProvider class."""

    def test_provider_creation(self):
        """Test creating a metadata provider."""
        provider = ThemeMetadataProvider()
        assert provider is not None

    def test_register_theme_metadata(self):
        """Test registering theme metadata."""
        provider = ThemeMetadataProvider()

        info = ThemeInfo(
            name="vscode",
            display_name="VS Code Dark+",
            description="Microsoft VS Code's default dark theme",
            type="dark",
            tags=["popular", "editor"],
        )

        provider.register_metadata("vscode", info)
        retrieved = provider.get_metadata("vscode")

        assert retrieved is not None
        assert retrieved.name == "vscode"
        assert retrieved.display_name == "VS Code Dark+"

    def test_get_nonexistent_metadata(self):
        """Test getting metadata for non-existent theme."""
        provider = ThemeMetadataProvider()

        result = provider.get_metadata("nonexistent")
        assert result is None

    def test_get_all_metadata(self):
        """Test getting all registered metadata."""
        provider = ThemeMetadataProvider()

        info1 = ThemeInfo(
            name="dark",
            display_name="Dark Theme",
            description="A dark theme",
            type="dark",
            tags=["dark"],
        )

        info2 = ThemeInfo(
            name="light",
            display_name="Light Theme",
            description="A light theme",
            type="light",
            tags=["light"],
        )

        provider.register_metadata("dark", info1)
        provider.register_metadata("light", info2)

        all_metadata = provider.get_all_metadata()
        assert len(all_metadata) == 2
        assert "dark" in all_metadata
        assert "light" in all_metadata

    def test_has_metadata(self):
        """Test checking if metadata exists."""
        provider = ThemeMetadataProvider()

        info = ThemeInfo(
            name="test",
            display_name="Test",
            description="Test",
            type="dark",
            tags=[],
        )

        assert not provider.has_metadata("test")
        provider.register_metadata("test", info)
        assert provider.has_metadata("test")

    def test_remove_metadata(self):
        """Test removing metadata."""
        provider = ThemeMetadataProvider()

        info = ThemeInfo(
            name="test",
            display_name="Test",
            description="Test",
            type="dark",
            tags=[],
        )

        provider.register_metadata("test", info)
        assert provider.has_metadata("test")

        provider.remove_metadata("test")
        assert not provider.has_metadata("test")

    def test_update_metadata(self):
        """Test updating existing metadata."""
        provider = ThemeMetadataProvider()

        info1 = ThemeInfo(
            name="test",
            display_name="Test v1",
            description="Version 1",
            type="dark",
            tags=["v1"],
        )

        info2 = ThemeInfo(
            name="test",
            display_name="Test v2",
            description="Version 2",
            type="dark",
            tags=["v2"],
        )

        provider.register_metadata("test", info1)
        retrieved1 = provider.get_metadata("test")
        assert retrieved1.display_name == "Test v1"

        provider.register_metadata("test", info2)
        retrieved2 = provider.get_metadata("test")
        assert retrieved2.display_name == "Test v2"

    def test_filter_by_type(self):
        """Test filtering metadata by theme type."""
        provider = ThemeMetadataProvider()

        dark1 = ThemeInfo(
            name="dark1",
            display_name="Dark 1",
            description="Dark theme 1",
            type="dark",
            tags=[],
        )

        dark2 = ThemeInfo(
            name="dark2",
            display_name="Dark 2",
            description="Dark theme 2",
            type="dark",
            tags=[],
        )

        light1 = ThemeInfo(
            name="light1",
            display_name="Light 1",
            description="Light theme 1",
            type="light",
            tags=[],
        )

        provider.register_metadata("dark1", dark1)
        provider.register_metadata("dark2", dark2)
        provider.register_metadata("light1", light1)

        dark_themes = provider.filter_by_type("dark")
        assert len(dark_themes) == 2
        assert all(info.type == "dark" for info in dark_themes)

        light_themes = provider.filter_by_type("light")
        assert len(light_themes) == 1
        assert all(info.type == "light" for info in light_themes)

    def test_filter_by_tag(self):
        """Test filtering metadata by tag."""
        provider = ThemeMetadataProvider()

        info1 = ThemeInfo(
            name="vscode",
            display_name="VS Code",
            description="VS Code theme",
            type="dark",
            tags=["popular", "editor"],
        )

        info2 = ThemeInfo(
            name="custom",
            display_name="Custom",
            description="Custom theme",
            type="dark",
            tags=["custom"],
        )

        info3 = ThemeInfo(
            name="popular",
            display_name="Popular",
            description="Popular theme",
            type="light",
            tags=["popular"],
        )

        provider.register_metadata("vscode", info1)
        provider.register_metadata("custom", info2)
        provider.register_metadata("popular", info3)

        popular_themes = provider.filter_by_tag("popular")
        assert len(popular_themes) == 2
        assert all("popular" in info.tags for info in popular_themes)

        editor_themes = provider.filter_by_tag("editor")
        assert len(editor_themes) == 1

    def test_create_from_theme(self):
        """Test creating ThemeInfo from Theme object."""
        theme = Theme(
            name="test_theme",
            colors={"background": "#1e1e1e", "foreground": "#d4d4d4"},
            styles={},
            metadata={
                "display_name": "Test Theme",
                "description": "A test theme",
                "type": "dark",
                "tags": ["test"],
                "author": "Test Author",
            },
        )

        provider = ThemeMetadataProvider()
        info = provider.create_from_theme(theme)

        assert info.name == "test_theme"
        assert info.display_name == "Test Theme"
        assert info.description == "A test theme"
        assert info.type == "dark"
        assert info.tags == ["test"]
        assert info.author == "Test Author"

    def test_create_from_theme_defaults(self):
        """Test creating ThemeInfo with default values when metadata missing."""
        theme = Theme(
            name="simple_theme",
            colors={"background": "#ffffff"},
            styles={},
        )

        provider = ThemeMetadataProvider()
        info = provider.create_from_theme(theme)

        assert info.name == "simple_theme"
        assert info.display_name == "simple_theme"  # Uses name as default
        assert info.type == "light"  # Default type
        assert info.tags == []
        assert info.author is None
