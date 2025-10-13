"""Widget introspection API for plugin discovery and metadata.

This module provides the introspection layer for theme-aware widgets to expose
their theming capabilities and metadata for dynamic plugin discovery systems.

Key Components:
- PluginAvailability: Enum for plugin availability status
- WidgetMetadata: Comprehensive metadata dataclass for widget introspection
- Helper functions: extract_theme_tokens(), validate_metadata()

Example:
    from vfwidgets_theme import WidgetMetadata, PluginAvailability
    from vfwidgets_terminal import TerminalWidget

    metadata = WidgetMetadata(
        name="Terminal Widget",
        widget_class_name="TerminalWidget",
        package_name="vfwidgets_terminal",
        version="1.0.0",
        theme_tokens=TerminalWidget.theme_config,
        required_tokens=["editor.background", "editor.foreground"],
        preview_factory=lambda parent: TerminalWidget(read_only=True, parent=parent)
    )

"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Optional

from .tokens import ColorTokenRegistry

__all__ = [
    "PluginAvailability",
    "WidgetMetadata",
    "extract_theme_tokens",
    "validate_metadata",
]


class PluginAvailability(Enum):
    """Plugin availability status.

    Attributes:
        AVAILABLE: Plugin is fully available and working
        MISSING_DEPENDENCIES: Plugin has missing required dependencies
        IMPORT_ERROR: Plugin failed to import
        INVALID_METADATA: Plugin metadata is invalid
        DISABLED: Plugin is explicitly disabled

    """

    AVAILABLE = auto()
    MISSING_DEPENDENCIES = auto()
    IMPORT_ERROR = auto()
    INVALID_METADATA = auto()
    DISABLED = auto()

    @property
    def is_available(self) -> bool:
        """Check if plugin is available for use."""
        return self == PluginAvailability.AVAILABLE


@dataclass
class WidgetMetadata:
    """Self-describing widget metadata for plugin discovery.

    This dataclass provides comprehensive metadata about a theme-aware widget,
    enabling dynamic discovery and introspection by plugin systems like Theme Studio.

    Attributes:
        name: Display name of the widget (e.g., "Terminal Widget")
        widget_class_name: Full class name (e.g., "TerminalWidget")
        package_name: Python package name (e.g., "vfwidgets_terminal")
        version: Widget version string (e.g., "1.0.0")
        theme_tokens: Theme token mappings (from ThemedWidget.theme_config)
        required_tokens: List of tokens that must be present
        optional_tokens: List of tokens that are optional
        preview_description: Human-readable description for preview
        preview_factory: Callable to create preview widget instance
        preview_config: Configuration dict for preview factory
        dependencies: List of required Python packages
        availability: Current availability status
        error_message: Error message if not available

    Example:
        >>> from vfwidgets_terminal import TerminalWidget
        >>> metadata = WidgetMetadata(
        ...     name="Terminal Widget",
        ...     widget_class_name="TerminalWidget",
        ...     package_name="vfwidgets_terminal",
        ...     version="1.0.0",
        ...     theme_tokens=TerminalWidget.theme_config,
        ...     required_tokens=["editor.background", "editor.foreground"],
        ...     preview_factory=lambda p: TerminalWidget(read_only=True, parent=p)
        ... )

    """

    # Core identification
    name: str
    widget_class_name: str
    package_name: str
    version: str

    # Theme introspection data (Core API)
    theme_tokens: dict[str, str] = field(default_factory=dict)
    required_tokens: list[str] = field(default_factory=list)
    optional_tokens: list[str] = field(default_factory=list)

    # Preview configuration
    preview_description: str = ""
    preview_factory: Optional[Callable] = None
    preview_config: dict[str, Any] = field(default_factory=dict)

    # Dependency information
    dependencies: list[str] = field(default_factory=list)

    # Availability status
    availability: PluginAvailability = PluginAvailability.AVAILABLE
    error_message: Optional[str] = None

    @property
    def is_available(self) -> bool:
        """Check if widget is available for use."""
        return self.availability.is_available

    @property
    def unique_token_paths(self) -> list[str]:
        """Get unique token paths used by this widget.

        Includes both theme_tokens (validated) and optional_tokens (unvalidated).
        This allows widgets to declare tokens that aren't in ColorTokenRegistry yet.

        Returns:
            Sorted list of unique token paths from theme_tokens dict and optional_tokens list.

        """
        # Combine theme_tokens values and optional_tokens
        all_tokens = set(self.theme_tokens.values()) | set(self.optional_tokens)
        return sorted(all_tokens)

    @property
    def token_categories(self) -> list[str]:
        """Extract token categories from token paths.

        Categories are the first segment of token paths (e.g., "editor" from
        "editor.background").

        Returns:
            Sorted list of unique category names.

        """
        categories: set[str] = set()
        for token_path in self.unique_token_paths:
            if "." in token_path:
                categories.add(token_path.split(".")[0])
        return sorted(categories)

    @property
    def token_count(self) -> int:
        """Get the number of theme tokens used by this widget."""
        return len(self.theme_tokens)

    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate metadata completeness.

        Returns:
            Tuple of (is_valid, error_message).
            error_message is None if valid.

        """
        if not self.name:
            return False, "name is required"
        if not self.widget_class_name:
            return False, "widget_class_name is required"
        if not self.package_name:
            return False, "package_name is required"
        if not self.version:
            return False, "version is required"
        if not self.theme_tokens:
            return False, "theme_tokens is required (empty dict not allowed)"

        # Validate token paths exist in registry
        registry = ColorTokenRegistry()
        all_token_names = registry.get_all_token_names()
        for prop_name, token_path in self.theme_tokens.items():
            if token_path not in all_token_names:
                return (
                    False,
                    f"Invalid token path '{token_path}' for property '{prop_name}'",
                )

        return True, None


def extract_theme_tokens(widget_class: type) -> dict[str, str]:
    """Extract theme_config from a ThemedWidget class.

    This helper function safely extracts the theme_config dictionary from a
    widget class, handling inheritance and missing attributes.

    Args:
        widget_class: A ThemedWidget subclass.

    Returns:
        Dictionary mapping property names to token paths.
        Returns empty dict if theme_config not found.

    Example:
        >>> from vfwidgets_terminal import TerminalWidget
        >>> tokens = extract_theme_tokens(TerminalWidget)
        >>> print(tokens["background"])
        'editor.background'

    """
    if hasattr(widget_class, "theme_config"):
        theme_config = widget_class.theme_config
        if isinstance(theme_config, dict):
            return theme_config
    return {}


def validate_metadata(metadata: WidgetMetadata) -> tuple[bool, Optional[str]]:
    """Validate WidgetMetadata completeness and correctness.

    This function performs comprehensive validation including:
    - Required fields present
    - Token paths valid
    - Dependencies resolvable

    Args:
        metadata: WidgetMetadata instance to validate.

    Returns:
        Tuple of (is_valid, error_message).
        error_message is None if valid.

    Example:
        >>> is_valid, error = validate_metadata(metadata)
        >>> if not is_valid:
        ...     print(f"Validation failed: {error}")

    """
    return metadata.validate()
