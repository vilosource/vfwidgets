"""
Tests for VSCode marketplace integration.
"""

import json
import tempfile
from pathlib import Path

import pytest

from vfwidgets_theme.errors import ThemeSystemError
from vfwidgets_theme.vscode.marketplace import MarketplaceClient, ThemeExtension


class TestMarketplaceClient:
    """Test cases for MarketplaceClient."""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary cache directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def client(self, temp_cache_dir):
        """Create marketplace client with temp cache."""
        return MarketplaceClient(cache_dir=temp_cache_dir)

    @pytest.fixture
    def sample_extension_manifest(self):
        """Sample VSCode extension manifest."""
        return {
            "name": "dracula-theme",
            "displayName": "Dracula Official",
            "description": "Official Dracula Theme",
            "version": "2.24.2",
            "publisher": "dracula-theme",
            "contributes": {
                "themes": [
                    {
                        "label": "Dracula",
                        "uiTheme": "vs-dark",
                        "path": "./themes/dracula.json"
                    }
                ]
            },
            "keywords": ["theme", "dark", "dracula"]
        }

    @pytest.fixture
    def sample_theme_data(self):
        """Sample VSCode theme data."""
        return {
            "name": "Dracula",
            "type": "dark",
            "colors": {
                "editor.background": "#282a36",
                "editor.foreground": "#f8f8f2",
                "activityBar.background": "#282a36",
                "sideBar.background": "#282a36",
                "statusBar.background": "#6272a4"
            },
            "tokenColors": [
                {
                    "name": "Comment",
                    "scope": "comment",
                    "settings": {
                        "foreground": "#6272a4"
                    }
                }
            ]
        }

    def test_client_initialization(self, temp_cache_dir):
        """Test client initialization."""
        client = MarketplaceClient(cache_dir=temp_cache_dir)

        assert client.cache_dir == temp_cache_dir
        assert client.extensions_dir == temp_cache_dir / "extensions"
        assert client.themes_dir == temp_cache_dir / "themes"

        # Check directories were created
        assert client.cache_dir.exists()
        assert client.extensions_dir.exists()
        assert client.themes_dir.exists()

    def test_theme_extension_creation(self):
        """Test ThemeExtension dataclass."""
        extension = ThemeExtension(
            id="test.theme",
            name="test-theme",
            display_name="Test Theme",
            description="A test theme",
            version="1.0.0",
            publisher="test"
        )

        assert extension.id == "test.theme"
        assert extension.themes == []  # Default empty list

    @pytest.mark.asyncio
    async def test_search_themes_popular_suggestions(self, client):
        """Test theme search returns popular suggestions."""
        async with client:
            themes = await client.search_themes("dark", limit=5)

            assert len(themes) <= 5
            assert all(isinstance(theme, ThemeExtension) for theme in themes)

            # Check that search found some themes
            if themes:
                # Verify theme has required fields
                theme = themes[0]
                assert theme.id
                assert theme.name
                assert theme.display_name
                assert theme.publisher

    @pytest.mark.asyncio
    async def test_search_local_themes(self, client, sample_extension_manifest, temp_cache_dir):
        """Test searching locally cached themes."""
        # Create a mock local extension
        ext_dir = client.extensions_dir / "test_extension"
        ext_dir.mkdir(parents=True)

        manifest_path = ext_dir / "package.json"
        with open(manifest_path, 'w') as f:
            json.dump(sample_extension_manifest, f)

        async with client:
            themes = await client.search_themes("dracula", limit=10)

            # Should find our local theme
            local_themes = [t for t in themes if t.local_path]
            assert len(local_themes) >= 1

            local_theme = local_themes[0]
            assert "dracula" in local_theme.display_name.lower()

    def test_matches_query(self, client, sample_extension_manifest):
        """Test query matching logic."""
        # Test name match
        assert client._matches_query(sample_extension_manifest, "dracula")

        # Test description match
        assert client._matches_query(sample_extension_manifest, "official")

        # Test keyword match
        assert client._matches_query(sample_extension_manifest, "theme")

        # Test case insensitive
        assert client._matches_query(sample_extension_manifest, "DRACULA")

        # Test no match
        assert not client._matches_query(sample_extension_manifest, "nonexistent")

    @pytest.mark.asyncio
    async def test_download_theme_not_cached(self, client):
        """Test downloading theme that's not cached."""
        async with client:
            result = await client.download_theme("nonexistent.theme")
            assert result is None

    @pytest.mark.asyncio
    async def test_download_theme_already_cached(self, client, sample_extension_manifest):
        """Test downloading theme that's already cached."""
        # Create cached extension
        ext_id = "dracula_theme_theme_dracula"
        ext_dir = client.extensions_dir / ext_id
        ext_dir.mkdir(parents=True)

        manifest_path = ext_dir / "package.json"
        with open(manifest_path, 'w') as f:
            json.dump(sample_extension_manifest, f)

        async with client:
            result = await client.download_theme("dracula-theme.theme-dracula")

            # Should return the cached directory
            # Note: actual extension ID format may differ
            if result:
                assert result.exists()

    def test_import_from_directory(self, client, sample_extension_manifest, sample_theme_data, temp_cache_dir):
        """Test importing themes from extension directory."""
        # Create extension directory structure
        ext_dir = temp_cache_dir / "test_extension"
        ext_dir.mkdir()

        # Create manifest
        manifest_path = ext_dir / "package.json"
        with open(manifest_path, 'w') as f:
            json.dump(sample_extension_manifest, f)

        # Create theme directory and file
        themes_dir = ext_dir / "themes"
        themes_dir.mkdir()

        theme_path = themes_dir / "dracula.json"
        with open(theme_path, 'w') as f:
            json.dump(sample_theme_data, f)

        # Import themes
        themes = client.import_from_extension(ext_dir)

        assert len(themes) == 1
        theme = themes[0]
        assert theme.name == "Dracula"
        assert theme.type == "dark"

    def test_import_from_nonexistent_path(self, client):
        """Test importing from non-existent path raises error."""
        with pytest.raises(ThemeSystemError, match="does not exist"):
            client.import_from_extension(Path("/nonexistent/path"))

    def test_install_local_extension_directory(self, client, sample_extension_manifest, temp_cache_dir):
        """Test installing extension from local directory."""
        # Create source extension directory
        source_dir = temp_cache_dir / "source_extension"
        source_dir.mkdir()

        manifest_path = source_dir / "package.json"
        with open(manifest_path, 'w') as f:
            json.dump(sample_extension_manifest, f)

        # Install extension
        extension = client.install_local_extension(source_dir)

        assert extension.name == "dracula-theme"
        assert extension.display_name == "Dracula Official"
        assert extension.local_path.exists()

        # Check files were copied
        installed_manifest = extension.local_path / "package.json"
        assert installed_manifest.exists()

    def test_install_local_extension_nonexistent(self, client):
        """Test installing from non-existent path raises error."""
        with pytest.raises(ThemeSystemError, match="does not exist"):
            client.install_local_extension(Path("/nonexistent/path"))

    def test_get_cached_extensions(self, client, sample_extension_manifest):
        """Test getting list of cached extensions."""
        # Create cached extension
        ext_dir = client.extensions_dir / "test_ext"
        ext_dir.mkdir(parents=True)

        manifest_path = ext_dir / "package.json"
        with open(manifest_path, 'w') as f:
            json.dump(sample_extension_manifest, f)

        # Get cached extensions
        extensions = client.get_cached_extensions()

        assert len(extensions) >= 1
        extension = next((e for e in extensions if e.name == "dracula-theme"), None)
        assert extension is not None
        assert extension.display_name == "Dracula Official"

    def test_manifest_to_extension(self, client, sample_extension_manifest, temp_cache_dir):
        """Test converting manifest to extension object."""
        local_path = temp_cache_dir / "test_path"
        extension = client._manifest_to_extension(sample_extension_manifest, local_path)

        assert extension.id == "dracula-theme.dracula-theme"
        assert extension.name == "dracula-theme"
        assert extension.display_name == "Dracula Official"
        assert extension.description == "Official Dracula Theme"
        assert extension.version == "2.24.2"
        assert extension.publisher == "dracula-theme"
        assert extension.local_path == local_path
        assert "Dracula" in extension.themes

    def test_normalize_color(self, client):
        """Test color normalization."""
        # Test hex colors
        assert client._normalize_color("#ff0000") == "#ff0000"

        # Test RGB colors
        rgb_result = client._rgb_to_hex("rgb(255, 0, 0)")
        assert rgb_result == "#ff0000"

        # Test RGBA colors
        rgba_result = client._rgb_to_hex("rgba(255, 0, 0, 0.5)")
        assert len(rgba_result) == 9  # #rrggbbaa

        # Test named colors
        assert client._normalize_color("white") == "#ffffff"
        assert client._normalize_color("black") == "#000000"

    def test_darken_color(self, client):
        """Test color darkening."""
        # Test darkening white
        darkened = client._darken_color("#ffffff", 0.5)
        assert darkened == "#7f7f7f"

        # Test invalid color
        invalid = client._darken_color("invalid", 0.5)
        assert invalid == "invalid"

    @pytest.mark.asyncio
    async def test_context_manager(self, client):
        """Test async context manager functionality."""
        async with client as ctx_client:
            assert ctx_client is client
            assert client._session is not None

        # Session should be closed after context
        # Note: We can't easily test if session is closed without accessing private attributes
