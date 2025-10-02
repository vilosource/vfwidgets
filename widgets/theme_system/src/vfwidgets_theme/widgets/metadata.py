"""Theme metadata system for VFWidgets.

This module provides:
- ThemeInfo: Dataclass for storing theme metadata
- ThemeMetadataProvider: Manager for theme metadata

The metadata system allows rich theme information including:
- Display names and descriptions
- Theme types (dark/light)
- Tags for categorization
- Author information
- Preview colors for UI display
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ..core.theme import Theme


@dataclass
class ThemeInfo:
    """Theme metadata information.

    This dataclass contains rich metadata about a theme that can be used
    for display in theme switching UIs, theme browsers, and settings dialogs.

    Attributes:
        name: Internal theme identifier (e.g., "vscode_dark")
        display_name: User-friendly display name (e.g., "VS Code Dark+")
        description: Detailed theme description
        type: Theme type - "dark" or "light"
        tags: List of tags for categorization (e.g., ["popular", "editor"])
        author: Optional theme author name
        preview_colors: Dictionary of key colors for preview display
                       (e.g., {"background": "#1e1e1e", "foreground": "#d4d4d4"})

    Example:
        >>> info = ThemeInfo(
        ...     name="vscode_dark",
        ...     display_name="VS Code Dark+",
        ...     description="Microsoft VS Code's default dark theme",
        ...     type="dark",
        ...     tags=["popular", "editor", "vscode"],
        ...     author="Microsoft",
        ...     preview_colors={
        ...         "background": "#1e1e1e",
        ...         "foreground": "#d4d4d4",
        ...         "accent": "#007acc"
        ...     }
        ... )

    """

    name: str
    display_name: str
    description: str
    type: str  # "dark" or "light"
    tags: List[str]
    author: Optional[str] = None
    preview_colors: Dict[str, str] = field(default_factory=dict)


class ThemeMetadataProvider:
    """Provider for managing theme metadata.

    This class manages a registry of ThemeInfo objects and provides
    methods for querying, filtering, and managing theme metadata.

    Example:
        >>> provider = ThemeMetadataProvider()
        >>> info = ThemeInfo(
        ...     name="dark",
        ...     display_name="Dark Theme",
        ...     description="A dark theme",
        ...     type="dark",
        ...     tags=["dark"]
        ... )
        >>> provider.register_metadata("dark", info)
        >>> dark_themes = provider.filter_by_type("dark")

    """

    def __init__(self):
        """Initialize the metadata provider."""
        self._metadata: Dict[str, ThemeInfo] = {}

    def register_metadata(self, theme_name: str, info: ThemeInfo) -> None:
        """Register metadata for a theme.

        Args:
            theme_name: Name of the theme
            info: ThemeInfo object containing metadata

        Example:
            >>> provider = ThemeMetadataProvider()
            >>> info = ThemeInfo(name="dark", display_name="Dark", ...)
            >>> provider.register_metadata("dark", info)

        """
        self._metadata[theme_name] = info

    def get_metadata(self, theme_name: str) -> Optional[ThemeInfo]:
        """Get metadata for a specific theme.

        Args:
            theme_name: Name of the theme

        Returns:
            ThemeInfo if found, None otherwise

        Example:
            >>> provider = ThemeMetadataProvider()
            >>> info = provider.get_metadata("vscode")
            >>> if info:
            ...     print(info.display_name)

        """
        return self._metadata.get(theme_name)

    def get_all_metadata(self) -> Dict[str, ThemeInfo]:
        """Get all registered metadata.

        Returns:
            Dictionary mapping theme names to ThemeInfo objects

        Example:
            >>> provider = ThemeMetadataProvider()
            >>> all_metadata = provider.get_all_metadata()
            >>> for name, info in all_metadata.items():
            ...     print(f"{info.display_name}: {info.description}")

        """
        return self._metadata.copy()

    def has_metadata(self, theme_name: str) -> bool:
        """Check if metadata exists for a theme.

        Args:
            theme_name: Name of the theme

        Returns:
            True if metadata exists, False otherwise

        Example:
            >>> provider = ThemeMetadataProvider()
            >>> if provider.has_metadata("dark"):
            ...     info = provider.get_metadata("dark")

        """
        return theme_name in self._metadata

    def remove_metadata(self, theme_name: str) -> None:
        """Remove metadata for a theme.

        Args:
            theme_name: Name of the theme to remove

        Example:
            >>> provider = ThemeMetadataProvider()
            >>> provider.remove_metadata("old_theme")

        """
        if theme_name in self._metadata:
            del self._metadata[theme_name]

    def filter_by_type(self, theme_type: str) -> List[ThemeInfo]:
        """Filter themes by type.

        Args:
            theme_type: Type to filter by ("dark" or "light")

        Returns:
            List of ThemeInfo objects matching the type

        Example:
            >>> provider = ThemeMetadataProvider()
            >>> dark_themes = provider.filter_by_type("dark")
            >>> for theme in dark_themes:
            ...     print(theme.display_name)

        """
        return [
            info for info in self._metadata.values()
            if info.type == theme_type
        ]

    def filter_by_tag(self, tag: str) -> List[ThemeInfo]:
        """Filter themes by tag.

        Args:
            tag: Tag to filter by

        Returns:
            List of ThemeInfo objects containing the tag

        Example:
            >>> provider = ThemeMetadataProvider()
            >>> popular_themes = provider.filter_by_tag("popular")
            >>> for theme in popular_themes:
            ...     print(theme.display_name)

        """
        return [
            info for info in self._metadata.values()
            if tag in info.tags
        ]

    def create_from_theme(self, theme: Theme) -> ThemeInfo:
        """Create ThemeInfo from a Theme object.

        Extracts metadata from the Theme object's metadata dictionary
        and creates a ThemeInfo object. Provides sensible defaults
        for missing metadata.

        Args:
            theme: Theme object to extract metadata from

        Returns:
            ThemeInfo object with extracted or default metadata

        Example:
            >>> theme = Theme(name="custom", colors={...}, metadata={...})
            >>> provider = ThemeMetadataProvider()
            >>> info = provider.create_from_theme(theme)

        """
        metadata = getattr(theme, "metadata", {})

        # Extract metadata with defaults
        display_name = metadata.get("display_name", theme.name)
        description = metadata.get("description", "")
        theme_type = metadata.get("type", "light")
        tags = metadata.get("tags", [])
        author = metadata.get("author")

        # Extract preview colors from theme colors
        preview_colors = {}
        if hasattr(theme, "colors") and isinstance(theme.colors, dict):
            # Use main colors for preview
            for key in ["background", "foreground", "accent", "primary"]:
                if key in theme.colors:
                    preview_colors[key] = theme.colors[key]

        return ThemeInfo(
            name=theme.name,
            display_name=display_name,
            description=description,
            type=theme_type,
            tags=tags,
            author=author,
            preview_colors=preview_colors,
        )


__all__ = [
    "ThemeInfo",
    "ThemeMetadataProvider",
]
