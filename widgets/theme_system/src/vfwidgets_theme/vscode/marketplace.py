"""VSCode marketplace integration for theme downloads.

This module provides functionality to search, download, and import themes
from the VSCode marketplace. Due to authentication requirements for the
official marketplace API, it also supports offline/local theme management.
"""

import hashlib
import json
import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiofiles
import aiohttp

from ..core.theme import Theme
from ..errors import ThemeSystemError
from ..logging import get_logger
from ..utils.file_utils import ensure_directory

logger = get_logger(__name__)


@dataclass
class ThemeExtension:
    """Represents a VSCode theme extension."""

    id: str
    name: str
    display_name: str
    description: str
    version: str
    publisher: str
    download_url: Optional[str] = None
    local_path: Optional[Path] = None
    themes: List[str] = None  # Theme files within extension

    def __post_init__(self):
        if self.themes is None:
            self.themes = []


class MarketplaceClient:
    """VSCode marketplace integration for theme downloads.

    Provides both online marketplace access and local theme management.
    Since the VSCode marketplace API requires authentication, this client
    focuses on local theme support with marketplace-like functionality.
    """

    MARKETPLACE_API = "https://marketplace.visualstudio.com/_apis/public/gallery"

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize marketplace client.

        Args:
            cache_dir: Directory for caching downloaded themes

        """
        self.cache_dir = cache_dir or Path.home() / ".vfwidgets" / "theme_cache"
        self.extensions_dir = self.cache_dir / "extensions"
        self.themes_dir = self.cache_dir / "themes"

        # Ensure directories exist
        ensure_directory(self.cache_dir)
        ensure_directory(self.extensions_dir)
        ensure_directory(self.themes_dir)

        self._extension_cache = {}
        self._session = None

    async def __aenter__(self):
        """Async context manager entry."""
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._session:
            await self._session.close()

    async def search_themes(self, query: str, limit: int = 20) -> List[ThemeExtension]:
        """Search VSCode marketplace for themes.

        Note: Due to marketplace API authentication requirements,
        this currently searches local cache and provides sample results.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of theme extensions

        """
        logger.info(f"Searching themes for query: {query}")

        # Search local cache first
        local_themes = await self._search_local_themes(query, limit)

        # For demonstration, also provide some popular theme suggestions
        suggestions = self._get_popular_theme_suggestions(query, limit - len(local_themes))

        return local_themes + suggestions

    async def _search_local_themes(self, query: str, limit: int) -> List[ThemeExtension]:
        """Search locally cached themes."""
        local_themes = []

        if not self.extensions_dir.exists():
            return local_themes

        for ext_dir in self.extensions_dir.iterdir():
            if ext_dir.is_dir():
                try:
                    manifest_path = ext_dir / "package.json"
                    if manifest_path.exists():
                        async with aiofiles.open(manifest_path) as f:
                            manifest = json.loads(await f.read())

                        if self._matches_query(manifest, query):
                            extension = self._manifest_to_extension(manifest, ext_dir)
                            local_themes.append(extension)

                            if len(local_themes) >= limit:
                                break

                except Exception as e:
                    logger.warning(f"Error reading extension manifest {ext_dir}: {e}")

        return local_themes

    def _matches_query(self, manifest: Dict[str, Any], query: str) -> bool:
        """Check if extension manifest matches search query."""
        query_lower = query.lower()

        # Check name, display name, description
        for field in ["name", "displayName", "description"]:
            value = manifest.get(field, "")
            if isinstance(value, str) and query_lower in value.lower():
                return True

        # Check keywords/tags
        keywords = manifest.get("keywords", [])
        if isinstance(keywords, list):
            for keyword in keywords:
                if isinstance(keyword, str) and query_lower in keyword.lower():
                    return True

        # Check if it's a theme extension
        contributes = manifest.get("contributes", {})
        if "themes" in contributes:
            return True

        return False

    def _get_popular_theme_suggestions(self, query: str, limit: int) -> List[ThemeExtension]:
        """Get suggestions for popular themes based on query."""
        if limit <= 0:
            return []

        popular_themes = [
            {
                "id": "dracula-theme.theme-dracula",
                "name": "theme-dracula",
                "displayName": "Dracula Official",
                "description": "Official Dracula Theme. A dark theme for many editors, shells, and more.",
                "version": "2.24.2",
                "publisher": "dracula-theme",
            },
            {
                "id": "ms-vscode.vscode-json",
                "name": "vscode-json",
                "displayName": "JSON Language Features",
                "description": "Provides rich language support for JSON",
                "version": "1.0.0",
                "publisher": "ms-vscode",
            },
            {
                "id": "github.github-vscode-theme",
                "name": "github-vscode-theme",
                "displayName": "GitHub Theme",
                "description": "GitHub theme for VS Code",
                "version": "6.3.4",
                "publisher": "GitHub",
            },
        ]

        query_lower = query.lower()
        suggestions = []

        for theme_data in popular_themes:
            if len(suggestions) >= limit:
                break

            # Simple matching logic
            if (
                query_lower in theme_data["displayName"].lower()
                or query_lower in theme_data["description"].lower()
                or "dark" in query_lower
                and "dark" in theme_data["description"].lower()
            ):

                extension = ThemeExtension(
                    id=theme_data["id"],
                    name=theme_data["name"],
                    display_name=theme_data["displayName"],
                    description=theme_data["description"],
                    version=theme_data["version"],
                    publisher=theme_data["publisher"],
                )
                suggestions.append(extension)

        return suggestions

    async def download_theme(self, extension_id: str) -> Optional[Path]:
        """Download theme extension.

        Note: This is a placeholder for marketplace downloads.
        In practice, users would install extensions manually or
        we would need VSCode marketplace authentication.

        Args:
            extension_id: Extension identifier

        Returns:
            Path to downloaded extension or None if not available

        """
        logger.info(f"Attempting to download theme: {extension_id}")

        # Check if already cached
        extension_dir = self.extensions_dir / extension_id.replace(".", "_")
        if extension_dir.exists():
            logger.info(f"Theme already cached: {extension_dir}")
            return extension_dir

        # For now, return None since we can't directly download from marketplace
        # without authentication. Users should install themes manually.
        logger.warning(
            f"Theme {extension_id} not found in cache. "
            "Please install manually from VSCode marketplace."
        )
        return None

    def import_from_extension(self, extension_path: Path) -> List[Theme]:
        """Extract themes from a VSCode extension.

        Args:
            extension_path: Path to extension directory or .vsix file

        Returns:
            List of imported themes

        """
        logger.info(f"Importing themes from extension: {extension_path}")

        if not extension_path.exists():
            raise ThemeSystemError(f"Extension path does not exist: {extension_path}")

        themes = []

        try:
            if extension_path.suffix == ".vsix":
                themes = self._import_from_vsix(extension_path)
            elif extension_path.is_dir():
                themes = self._import_from_directory(extension_path)
            else:
                raise ThemeSystemError(f"Unsupported extension format: {extension_path}")

        except Exception as e:
            logger.error(f"Error importing themes from {extension_path}: {e}")
            raise ThemeSystemError(f"Failed to import themes: {e}")

        logger.info(f"Successfully imported {len(themes)} themes")
        return themes

    def _import_from_vsix(self, vsix_path: Path) -> List[Theme]:
        """Import themes from .vsix file."""
        themes = []

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Extract .vsix file (it's a zip)
            with zipfile.ZipFile(vsix_path, "r") as zip_file:
                zip_file.extractall(temp_path)

            # Look for extension directory
            extension_dir = temp_path / "extension"
            if not extension_dir.exists():
                # Some .vsix files extract directly
                extension_dir = temp_path

            themes = self._import_from_directory(extension_dir)

        return themes

    def _import_from_directory(self, extension_dir: Path) -> List[Theme]:
        """Import themes from extension directory."""
        themes = []

        # Read package.json
        manifest_path = extension_dir / "package.json"
        if not manifest_path.exists():
            raise ThemeSystemError("Extension manifest (package.json) not found")

        with open(manifest_path) as f:
            manifest = json.load(f)

        # Get theme contributions
        contributes = manifest.get("contributes", {})
        theme_contributions = contributes.get("themes", [])

        if not theme_contributions:
            logger.warning("No theme contributions found in extension")
            return themes

        # Import each theme
        for theme_contrib in theme_contributions:
            theme_path = extension_dir / theme_contrib["path"]
            if theme_path.exists():
                try:
                    theme = self._load_theme_file(theme_path, theme_contrib)
                    if theme:
                        themes.append(theme)
                except Exception as e:
                    logger.error(f"Error loading theme {theme_path}: {e}")

        return themes

    def _load_theme_file(self, theme_path: Path, contribution: Dict[str, Any]) -> Optional[Theme]:
        """Load a single theme file."""
        try:
            with open(theme_path) as f:
                theme_data = json.load(f)

            # Convert VSCode theme to our Theme format
            from .importer import VSCodeThemeImporter

            importer = VSCodeThemeImporter()
            theme = importer.import_theme(theme_data, contribution.get("label", "Unnamed Theme"))

            return theme

        except Exception as e:
            logger.error(f"Error loading theme file {theme_path}: {e}")
            return None

    def _manifest_to_extension(self, manifest: Dict[str, Any], local_path: Path) -> ThemeExtension:
        """Convert package.json manifest to ThemeExtension."""
        extension_id = f"{manifest.get('publisher', 'unknown')}.{manifest.get('name', 'unknown')}"

        # Find theme files
        themes = []
        contributes = manifest.get("contributes", {})
        theme_contributions = contributes.get("themes", [])

        for theme_contrib in theme_contributions:
            themes.append(theme_contrib.get("label", "Unnamed Theme"))

        return ThemeExtension(
            id=extension_id,
            name=manifest.get("name", "Unknown"),
            display_name=manifest.get("displayName", manifest.get("name", "Unknown")),
            description=manifest.get("description", ""),
            version=manifest.get("version", "1.0.0"),
            publisher=manifest.get("publisher", "Unknown"),
            local_path=local_path,
            themes=themes,
        )

    def get_cached_extensions(self) -> List[ThemeExtension]:
        """Get list of cached extensions."""
        extensions = []

        if not self.extensions_dir.exists():
            return extensions

        for ext_dir in self.extensions_dir.iterdir():
            if ext_dir.is_dir():
                try:
                    manifest_path = ext_dir / "package.json"
                    if manifest_path.exists():
                        with open(manifest_path) as f:
                            manifest = json.load(f)

                        extension = self._manifest_to_extension(manifest, ext_dir)
                        extensions.append(extension)

                except Exception as e:
                    logger.warning(f"Error reading cached extension {ext_dir}: {e}")

        return extensions

    def install_local_extension(self, extension_path: Path) -> ThemeExtension:
        """Install an extension from local path.

        Args:
            extension_path: Path to extension directory or .vsix file

        Returns:
            Installed extension info

        """
        logger.info(f"Installing local extension: {extension_path}")

        if not extension_path.exists():
            raise ThemeSystemError(f"Extension path does not exist: {extension_path}")

        # Generate extension ID from path
        extension_id = hashlib.md5(str(extension_path).encode()).hexdigest()[:16]
        install_dir = self.extensions_dir / extension_id

        try:
            if extension_path.suffix == ".vsix":
                self._install_vsix(extension_path, install_dir)
            elif extension_path.is_dir():
                self._install_directory(extension_path, install_dir)
            else:
                raise ThemeSystemError(f"Unsupported extension format: {extension_path}")

            # Read manifest to create extension info
            manifest_path = install_dir / "package.json"
            with open(manifest_path) as f:
                manifest = json.load(f)

            extension = self._manifest_to_extension(manifest, install_dir)

            logger.info(f"Successfully installed extension: {extension.display_name}")
            return extension

        except Exception as e:
            logger.error(f"Error installing extension {extension_path}: {e}")
            # Clean up on error
            if install_dir.exists():
                shutil.rmtree(install_dir)
            raise ThemeSystemError(f"Failed to install extension: {e}")

    def _install_vsix(self, vsix_path: Path, install_dir: Path) -> None:
        """Install .vsix file to directory."""
        ensure_directory(install_dir)

        with zipfile.ZipFile(vsix_path, "r") as zip_file:
            zip_file.extractall(install_dir)

        # Move contents from extension subdirectory if present
        extension_subdir = install_dir / "extension"
        if extension_subdir.exists():
            for item in extension_subdir.iterdir():
                shutil.move(str(item), str(install_dir / item.name))
            extension_subdir.rmdir()

    def _install_directory(self, source_dir: Path, install_dir: Path) -> None:
        """Install extension directory."""
        if install_dir.exists():
            shutil.rmtree(install_dir)

        shutil.copytree(source_dir, install_dir)
