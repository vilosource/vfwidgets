"""
ThemeRepository for theme storage and retrieval operations.

This module provides the ThemeRepository class that handles theme lifecycle
storage, loading from various sources, theme discovery, and caching.
It follows the Single Responsibility Principle by focusing solely on
theme data persistence and retrieval.

Key Classes:
- ThemeRepository: Main repository for theme storage and retrieval
- FileThemeLoader: Loads themes from files (JSON, YAML, VSCode formats)
- BuiltinThemeManager: Manages built-in themes
- ThemeCache: LRU cache for theme performance optimization
- ThemeDiscovery: Discovers themes in directories

Design Principles:
- Single Responsibility: Repository focuses only on theme storage/retrieval
- Performance: Efficient caching and indexing for fast access
- Thread Safety: All operations are thread-safe
- Extensibility: Support for multiple theme formats and sources
- Error Recovery: Graceful handling of invalid themes and I/O errors

Performance Requirements:
- Theme loading: < 200ms including validation
- Cached access: < 1μs (through caching layer)
- Memory overhead: < 2KB per managed theme
"""

import json
import yaml
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Set
from collections import OrderedDict
from dataclasses import dataclass
import weakref

# Import foundation modules
from ..protocols import ThemeData
from ..errors import ThemeNotFoundError, ThemeLoadError, ThemeValidationError
from ..logging import get_debug_logger
from ..fallbacks import MINIMAL_THEME
from .theme import Theme, ThemeValidator

logger = get_debug_logger(__name__)


@dataclass
class ThemeMetadata:
    """Metadata for themes in repository."""
    name: str
    version: str
    file_path: Optional[Path]
    loaded_time: float
    access_count: int
    last_accessed: float


class ThemeCache:
    """
    LRU cache for theme performance optimization.

    Provides fast access to frequently used themes with automatic
    eviction based on size limits and access patterns.
    """

    def __init__(self, max_size: int = 100):
        """
        Initialize theme cache.

        Args:
            max_size: Maximum number of themes to cache
        """
        self.max_size = max_size
        self._cache: OrderedDict[str, Theme] = OrderedDict()
        self._lock = threading.RLock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }
        logger.debug(f"ThemeCache initialized with max_size: {max_size}")

    @property
    def size(self) -> int:
        """Get current cache size."""
        with self._lock:
            return len(self._cache)

    def get(self, key: str) -> Optional[Theme]:
        """
        Get theme from cache.

        Args:
            key: Theme name

        Returns:
            Cached theme or None if not found
        """
        with self._lock:
            if key in self._cache:
                # Move to end (most recently used)
                theme = self._cache.pop(key)
                self._cache[key] = theme
                self._stats["hits"] += 1
                logger.debug(f"Cache hit for theme: {key}")
                return theme

            self._stats["misses"] += 1
            logger.debug(f"Cache miss for theme: {key}")
            return None

    def put(self, key: str, theme: Theme) -> None:
        """
        Put theme in cache.

        Args:
            key: Theme name
            theme: Theme object to cache
        """
        with self._lock:
            if key in self._cache:
                # Update existing entry
                self._cache.pop(key)
            elif len(self._cache) >= self.max_size:
                # Evict least recently used
                evicted_key = next(iter(self._cache))
                self._cache.pop(evicted_key)
                self._stats["evictions"] += 1
                logger.debug(f"Evicted theme from cache: {evicted_key}")

            self._cache[key] = theme
            logger.debug(f"Cached theme: {key}")

    def invalidate(self, key: str) -> bool:
        """
        Invalidate specific cache entry.

        Args:
            key: Theme name to invalidate

        Returns:
            True if entry was removed, False if not found
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"Invalidated cache entry: {key}")
                return True
            return False

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            logger.debug("Cache cleared")

    def get_statistics(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            hit_rate = self._stats["hits"] / (self._stats["hits"] + self._stats["misses"]) \
                if (self._stats["hits"] + self._stats["misses"]) > 0 else 0.0

            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "evictions": self._stats["evictions"],
                "hit_rate": hit_rate
            }


class FileThemeLoader:
    """
    Loader for file-based themes.

    Supports multiple file formats:
    - JSON (.json)
    - YAML (.yaml, .yml)
    - VSCode themes (.json with specific structure)
    """

    SUPPORTED_EXTENSIONS = {".json", ".yaml", ".yml"}

    def __init__(self):
        """Initialize file theme loader."""
        self._validator = ThemeValidator()
        logger.debug("FileThemeLoader initialized")

    def can_load(self, source: Any) -> bool:
        """
        Check if loader can handle the source.

        Args:
            source: File path or Path object

        Returns:
            True if loader can handle the source
        """
        if isinstance(source, (str, Path)):
            path = Path(source)
            return path.suffix.lower() in self.SUPPORTED_EXTENSIONS
        return False

    def load_theme(self, file_path: Union[str, Path]) -> Theme:
        """
        Load theme from file.

        Args:
            file_path: Path to theme file

        Returns:
            Loaded Theme object

        Raises:
            ThemeLoadError: If file cannot be loaded or parsed
            ThemeValidationError: If theme data is invalid
        """
        path = Path(file_path)
        logger.debug(f"Loading theme from file: {path}")

        if not path.exists():
            raise ThemeLoadError(f"Theme file not found: {path}")

        if not path.is_file():
            raise ThemeLoadError(f"Path is not a file: {path}")

        try:
            with open(path, 'r', encoding='utf-8') as f:
                if path.suffix.lower() == '.json':
                    data = json.load(f)
                elif path.suffix.lower() in {'.yaml', '.yml'}:
                    data = yaml.safe_load(f)
                else:
                    raise ThemeLoadError(f"Unsupported file format: {path.suffix}")

            # Validate theme data
            validation_result = self._validator.validate_theme_data(data)
            if not validation_result.is_valid:
                error_msg = "\n".join(validation_result.errors)
                raise ThemeValidationError(f"Invalid theme data in {path}: {error_msg}")

            # Create theme from validated data
            theme = Theme.from_dict(data)
            logger.debug(f"Successfully loaded theme '{theme.name}' from {path}")
            return theme

        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise ThemeLoadError(f"Failed to parse theme file {path}: {e}")
        except Exception as e:
            raise ThemeLoadError(f"Error loading theme from {path}: {e}")


class BuiltinThemeManager:
    """
    Manager for built-in themes.

    Provides access to default themes that are shipped with the system:
    - default: Standard light theme
    - dark: Standard dark theme
    - light: High contrast light theme
    - minimal: Fallback theme with safe defaults
    """

    def __init__(self):
        """Initialize builtin theme manager."""
        self._themes: Dict[str, Theme] = {}
        self._load_builtin_themes()
        logger.debug(f"BuiltinThemeManager initialized with {len(self._themes)} themes")

    def _load_builtin_themes(self) -> None:
        """Load all built-in themes."""
        # Default theme
        default_theme_data = {
            "name": "default",
            "version": "1.0.0",
            "colors": {
                "primary": "#007acc",
                "secondary": "#ffffff",
                "background": "#ffffff",
                "foreground": "#333333",
                "border": "#cccccc",
                "hover": "#e6f2ff",
                "active": "#0066a3",
                "disabled": "#999999",
                "error": "#d32f2f",
                "warning": "#f57c00",
                "success": "#2e7d32",
                "info": "#1976d2"
            },
            "styles": {
                "button": "background-color: @colors.primary; color: @colors.secondary; border: 1px solid @colors.border;",
                "button:hover": "background-color: @colors.hover;",
                "button:active": "background-color: @colors.active;",
                "input": "background-color: @colors.background; color: @colors.foreground; border: 1px solid @colors.border;",
                "label": "color: @colors.foreground;"
            },
            "metadata": {
                "description": "Default light theme",
                "author": "VFWidgets",
                "builtin": True
            }
        }

        # Dark theme
        dark_theme_data = {
            "name": "dark",
            "version": "1.0.0",
            "colors": {
                "primary": "#007acc",
                "secondary": "#ffffff",
                "background": "#2d2d2d",
                "foreground": "#cccccc",
                "border": "#555555",
                "hover": "#404040",
                "active": "#0066a3",
                "disabled": "#666666",
                "error": "#f44336",
                "warning": "#ff9800",
                "success": "#4caf50",
                "info": "#2196f3"
            },
            "styles": {
                "button": "background-color: @colors.primary; color: @colors.secondary; border: 1px solid @colors.border;",
                "button:hover": "background-color: @colors.hover;",
                "button:active": "background-color: @colors.active;",
                "input": "background-color: @colors.background; color: @colors.foreground; border: 1px solid @colors.border;",
                "label": "color: @colors.foreground;"
            },
            "metadata": {
                "description": "Standard dark theme",
                "author": "VFWidgets",
                "builtin": True
            }
        }

        # Light theme (high contrast)
        light_theme_data = {
            "name": "light",
            "version": "1.0.0",
            "colors": {
                "primary": "#0056b3",
                "secondary": "#ffffff",
                "background": "#ffffff",
                "foreground": "#000000",
                "border": "#808080",
                "hover": "#e0e7ff",
                "active": "#003d82",
                "disabled": "#808080",
                "error": "#b71c1c",
                "warning": "#e65100",
                "success": "#1b5e20",
                "info": "#0d47a1"
            },
            "styles": {
                "button": "background-color: @colors.primary; color: @colors.secondary; border: 2px solid @colors.border;",
                "button:hover": "background-color: @colors.hover;",
                "button:active": "background-color: @colors.active;",
                "input": "background-color: @colors.background; color: @colors.foreground; border: 2px solid @colors.border;",
                "label": "color: @colors.foreground; font-weight: bold;"
            },
            "metadata": {
                "description": "High contrast light theme",
                "author": "VFWidgets",
                "builtin": True
            }
        }

        # Create theme objects
        try:
            self._themes["default"] = Theme.from_dict(default_theme_data)
            self._themes["dark"] = Theme.from_dict(dark_theme_data)
            self._themes["light"] = Theme.from_dict(light_theme_data)

            # Add minimal theme as fallback
            self._themes["minimal"] = Theme.from_dict(MINIMAL_THEME)

        except Exception as e:
            logger.error(f"Error loading built-in themes: {e}")
            # Ensure minimal theme is always available
            self._themes["minimal"] = Theme.from_dict(MINIMAL_THEME)

    def list_themes(self) -> List[str]:
        """List all built-in theme names."""
        return list(self._themes.keys())

    def get_theme(self, name: str) -> Theme:
        """
        Get built-in theme by name.

        Args:
            name: Theme name

        Returns:
            Built-in theme

        Raises:
            ThemeNotFoundError: If theme not found
        """
        if name not in self._themes:
            raise ThemeNotFoundError(f"Built-in theme '{name}' not found")

        return self._themes[name]

    def has_theme(self, name: str) -> bool:
        """Check if built-in theme exists."""
        return name in self._themes


class ThemeDiscovery:
    """
    Theme discovery service for finding themes in directories.

    Scans directories for theme files and loads them automatically.
    Supports recursive scanning and multiple file formats.
    """

    def __init__(self, loader: Optional[FileThemeLoader] = None):
        """
        Initialize theme discovery.

        Args:
            loader: File loader to use (creates default if None)
        """
        self._loader = loader or FileThemeLoader()
        logger.debug("ThemeDiscovery initialized")

    def discover_in_directory(self, directory: Union[str, Path], recursive: bool = True) -> List[Theme]:
        """
        Discover themes in directory.

        Args:
            directory: Directory to scan
            recursive: Whether to scan subdirectories

        Returns:
            List of discovered themes
        """
        dir_path = Path(directory)
        themes = []

        if not dir_path.exists() or not dir_path.is_dir():
            logger.warning(f"Directory not found or not a directory: {dir_path}")
            return themes

        logger.debug(f"Discovering themes in: {dir_path} (recursive={recursive})")

        # Get file pattern based on supported extensions
        patterns = ["*.json", "*.yaml", "*.yml"]

        for pattern in patterns:
            if recursive:
                files = dir_path.rglob(pattern)
            else:
                files = dir_path.glob(pattern)

            for file_path in files:
                try:
                    if self._loader.can_load(file_path):
                        theme = self._loader.load_theme(file_path)
                        themes.append(theme)
                        logger.debug(f"Discovered theme: {theme.name} from {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to load theme from {file_path}: {e}")

        logger.debug(f"Discovered {len(themes)} themes in {dir_path}")
        return themes


class ThemeRepository:
    """
    Main repository for theme storage and retrieval.

    Coordinates theme operations including:
    - Theme storage and retrieval
    - File-based loading and saving
    - Built-in theme management
    - Caching for performance
    - Theme discovery
    - Thread-safe operations

    Follows Single Responsibility Principle by focusing only on
    theme persistence and retrieval operations.
    """

    def __init__(
        self,
        cache: Optional[ThemeCache] = None,
        discovery: Optional[ThemeDiscovery] = None,
        builtin_manager: Optional[BuiltinThemeManager] = None
    ):
        """
        Initialize theme repository.

        Args:
            cache: Cache for theme performance optimization
            discovery: Theme discovery service
            builtin_manager: Built-in theme manager
        """
        self._themes: Dict[str, Theme] = {}
        self._metadata: Dict[str, ThemeMetadata] = {}
        self._cache = cache or ThemeCache()
        self._discovery = discovery or ThemeDiscovery()
        self._builtin_manager = builtin_manager or BuiltinThemeManager()
        self._file_loader = FileThemeLoader()
        self._lock = threading.RLock()

        # Load built-in themes
        self._load_builtin_themes()

        logger.debug("ThemeRepository initialized")

    def _load_builtin_themes(self) -> None:
        """Load built-in themes into repository."""
        try:
            for theme_name in self._builtin_manager.list_themes():
                theme = self._builtin_manager.get_theme(theme_name)
                self._themes[theme_name] = theme
                self._metadata[theme_name] = ThemeMetadata(
                    name=theme_name,
                    version=theme.version,
                    file_path=None,  # Built-in themes have no file path
                    loaded_time=time.time(),
                    access_count=0,
                    last_accessed=0.0
                )
                logger.debug(f"Loaded built-in theme: {theme_name}")
        except Exception as e:
            logger.error(f"Error loading built-in themes: {e}")

    def add_theme(self, theme: Theme) -> None:
        """
        Add theme to repository.

        Args:
            theme: Theme to add
        """
        with self._lock:
            self._themes[theme.name] = theme
            self._metadata[theme.name] = ThemeMetadata(
                name=theme.name,
                version=theme.version,
                file_path=None,
                loaded_time=time.time(),
                access_count=0,
                last_accessed=0.0
            )

            # Update cache
            self._cache.put(theme.name, theme)

            logger.debug(f"Added theme to repository: {theme.name}")

    def get_theme(self, name: str) -> Theme:
        """
        Get theme by name.

        Args:
            name: Theme name

        Returns:
            Theme object

        Raises:
            ThemeNotFoundError: If theme not found
        """
        with self._lock:
            # Try cache first
            cached_theme = self._cache.get(name)
            if cached_theme:
                self._update_access_metadata(name)
                return cached_theme

            # Check repository
            if name in self._themes:
                theme = self._themes[name]
                self._cache.put(name, theme)
                self._update_access_metadata(name)
                return theme

            raise ThemeNotFoundError(f"Theme '{name}' not found in repository")

    def has_theme(self, name: str) -> bool:
        """
        Check if theme exists in repository.

        Args:
            name: Theme name

        Returns:
            True if theme exists
        """
        with self._lock:
            return name in self._themes

    def remove_theme(self, name: str) -> bool:
        """
        Remove theme from repository.

        Args:
            name: Theme name to remove

        Returns:
            True if theme was removed, False if not found
        """
        with self._lock:
            if name in self._themes:
                del self._themes[name]
                if name in self._metadata:
                    del self._metadata[name]
                self._cache.invalidate(name)
                logger.debug(f"Removed theme from repository: {name}")
                return True
            return False

    def list_themes(self) -> List[str]:
        """
        List all theme names in repository.

        Returns:
            List of theme names
        """
        with self._lock:
            return list(self._themes.keys())

    def clear_themes(self) -> None:
        """Clear all themes from repository (except built-ins)."""
        with self._lock:
            # Keep track of built-in themes
            builtin_themes = {}
            builtin_metadata = {}

            for name in list(self._themes.keys()):
                if name in self._metadata and self._metadata[name].file_path is None:
                    # This is a built-in theme, preserve it
                    builtin_themes[name] = self._themes[name]
                    builtin_metadata[name] = self._metadata[name]

            self._themes = builtin_themes
            self._metadata = builtin_metadata
            self._cache.clear()

            logger.debug("Cleared all non-builtin themes from repository")

    def load_from_file(self, file_path: Union[str, Path]) -> Theme:
        """
        Load theme from file and add to repository.

        Args:
            file_path: Path to theme file

        Returns:
            Loaded theme

        Raises:
            ThemeLoadError: If file cannot be loaded
        """
        theme = self._file_loader.load_theme(file_path)

        with self._lock:
            self._themes[theme.name] = theme
            self._metadata[theme.name] = ThemeMetadata(
                name=theme.name,
                version=theme.version,
                file_path=Path(file_path),
                loaded_time=time.time(),
                access_count=0,
                last_accessed=0.0
            )
            self._cache.put(theme.name, theme)

        logger.debug(f"Loaded theme '{theme.name}' from file: {file_path}")
        return theme

    def save_to_file(self, theme: Theme, file_path: Union[str, Path]) -> None:
        """
        Save theme to file.

        Args:
            theme: Theme to save
            file_path: Path to save file

        Raises:
            ThemeLoadError: If file cannot be saved
        """
        path = Path(file_path)

        try:
            # Ensure parent directory exists
            path.parent.mkdir(parents=True, exist_ok=True)

            # Convert theme to dictionary
            theme_data = theme.to_dict()

            # Save based on file extension
            with open(path, 'w', encoding='utf-8') as f:
                if path.suffix.lower() == '.json':
                    json.dump(theme_data, f, indent=2, ensure_ascii=False)
                elif path.suffix.lower() in {'.yaml', '.yml'}:
                    yaml.dump(theme_data, f, default_flow_style=False, allow_unicode=True)
                else:
                    raise ThemeLoadError(f"Unsupported file format: {path.suffix}")

            logger.debug(f"Saved theme '{theme.name}' to file: {path}")

        except Exception as e:
            raise ThemeLoadError(f"Failed to save theme to {path}: {e}")

    def discover_themes(self, directory: Union[str, Path], recursive: bool = True) -> List[Theme]:
        """
        Discover and load themes from directory.

        Args:
            directory: Directory to scan
            recursive: Whether to scan subdirectories

        Returns:
            List of discovered themes
        """
        themes = self._discovery.discover_in_directory(directory, recursive)

        # Add discovered themes to repository
        with self._lock:
            for theme in themes:
                if theme.name not in self._themes:
                    self._themes[theme.name] = theme
                    self._metadata[theme.name] = ThemeMetadata(
                        name=theme.name,
                        version=theme.version,
                        file_path=None,  # Discovery doesn't track individual file paths
                        loaded_time=time.time(),
                        access_count=0,
                        last_accessed=0.0
                    )
                    self._cache.put(theme.name, theme)

        logger.debug(f"Discovered and loaded {len(themes)} themes from {directory}")
        return themes

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get repository statistics.

        Returns:
            Dictionary with repository statistics
        """
        with self._lock:
            cache_stats = self._cache.get_statistics()

            total_access_count = sum(meta.access_count for meta in self._metadata.values())
            builtin_count = sum(1 for meta in self._metadata.values() if meta.file_path is None)

            return {
                "total_themes": len(self._themes),
                "builtin_themes": builtin_count,
                "loaded_themes": len(self._themes) - builtin_count,
                "total_access_count": total_access_count,
                "cache_stats": cache_stats
            }

    def _update_access_metadata(self, name: str) -> None:
        """Update access metadata for theme."""
        if name in self._metadata:
            metadata = self._metadata[name]
            metadata.access_count += 1
            metadata.last_accessed = time.time()


def create_theme_repository(
    cache_size: int = 100,
    discovery: Optional[ThemeDiscovery] = None,
    builtin_manager: Optional[BuiltinThemeManager] = None
) -> ThemeRepository:
    """
    Factory function for creating theme repository with defaults.

    Args:
        cache_size: Maximum cache size
        discovery: Custom theme discovery service
        builtin_manager: Custom built-in theme manager

    Returns:
        Configured theme repository
    """
    cache = ThemeCache(max_size=cache_size)
    discovery = discovery or ThemeDiscovery()
    builtin_manager = builtin_manager or BuiltinThemeManager()

    repository = ThemeRepository(
        cache=cache,
        discovery=discovery,
        builtin_manager=builtin_manager
    )

    logger.debug("Created theme repository with default configuration")
    return repository


__all__ = [
    "ThemeRepository",
    "FileThemeLoader",
    "BuiltinThemeManager",
    "ThemeCache",
    "ThemeDiscovery",
    "ThemeMetadata",
    "create_theme_repository",
]