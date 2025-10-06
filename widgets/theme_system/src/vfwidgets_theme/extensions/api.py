"""Extension API for theme system.

Provides safe APIs that extensions can use to interact with the theme system
and access required functionality.
"""

import weakref
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from ..core.theme import Theme, ThemeColors
from ..errors import ExtensionError
from ..logging import get_logger

logger = get_logger(__name__)


class ExtensionAPI:
    """Safe API interface for extensions.

    Provides controlled access to theme system functionality while
    maintaining security boundaries.
    """

    def __init__(self):
        """Initialize extension API."""
        self._registered_apis: Dict[str, Any] = {}
        self._theme_manager = None  # Will be set by system
        self._event_system = None  # Will be set by system

        # API version
        self.version = "1.0.0"

        logger.debug("Extension API initialized")

    def register_api(self, name: str, api_object: Any) -> None:
        """Register an API for extensions to use.

        Args:
            name: API name
            api_object: API object to register

        """
        self._registered_apis[name] = api_object
        logger.debug(f"Registered API: {name}")

    def get_api(self, name: str) -> Optional[Any]:
        """Get registered API by name.

        Args:
            name: API name

        Returns:
            API object or None if not found

        """
        return self._registered_apis.get(name)

    # Theme Management API
    def get_current_theme(self) -> Optional[Theme]:
        """Get currently active theme.

        Returns:
            Current theme or None

        """
        if self._theme_manager:
            return self._theme_manager.get_current_theme()
        return None

    def get_theme_by_name(self, name: str) -> Optional[Theme]:
        """Get theme by name.

        Args:
            name: Theme name

        Returns:
            Theme or None if not found

        """
        if self._theme_manager:
            return self._theme_manager.get_theme(name)
        return None

    def list_themes(self) -> List[Theme]:
        """Get list of available themes.

        Returns:
            List of themes

        """
        if self._theme_manager:
            return self._theme_manager.list_themes()
        return []

    def create_theme(self, name: str, base_theme: Optional[Theme] = None) -> Theme:
        """Create a new theme.

        Args:
            name: Theme name
            base_theme: Base theme to inherit from

        Returns:
            Created theme

        Raises:
            ExtensionError: If theme creation fails

        """
        try:
            if base_theme:
                # Create copy of base theme
                theme = Theme(
                    name=name,
                    type=base_theme.type,
                    description=f"Extension theme based on {base_theme.name}",
                    colors=ThemeColors(**base_theme.colors.__dict__),
                    properties=base_theme.properties.__class__(**base_theme.properties.__dict__),
                )
            else:
                # Create minimal theme
                theme = Theme(name=name, type="dark", description="Extension-created theme")

            return theme

        except Exception as e:
            raise ExtensionError(f"Failed to create theme: {e}")

    def modify_theme_colors(self, theme: Theme, color_changes: Dict[str, str]) -> Theme:
        """Modify theme colors.

        Args:
            theme: Theme to modify
            color_changes: Dictionary of color attribute names to new values

        Returns:
            Modified theme

        Raises:
            ExtensionError: If modification fails

        """
        try:
            # Create a copy to avoid modifying original
            modified_theme = Theme(
                name=f"{theme.name}_modified",
                type=theme.type,
                description=f"Modified {theme.description}",
                colors=ThemeColors(**theme.colors.__dict__),
                properties=theme.properties.__class__(**theme.properties.__dict__),
            )

            # Apply color changes
            for attr_name, color_value in color_changes.items():
                if hasattr(modified_theme.colors, attr_name):
                    setattr(modified_theme.colors, attr_name, color_value)
                else:
                    logger.warning(f"Unknown color attribute: {attr_name}")

            return modified_theme

        except Exception as e:
            raise ExtensionError(f"Failed to modify theme colors: {e}")

    # Color Utilities
    def darken_color(self, color: str, factor: float = 0.2) -> str:
        """Darken a color.

        Args:
            color: Hex color string
            factor: Darkening factor (0.0 to 1.0)

        Returns:
            Darkened color

        """
        return self._adjust_color_brightness(color, -factor)

    def lighten_color(self, color: str, factor: float = 0.2) -> str:
        """Lighten a color.

        Args:
            color: Hex color string
            factor: Lightening factor (0.0 to 1.0)

        Returns:
            Lightened color

        """
        return self._adjust_color_brightness(color, factor)

    def mix_colors(self, color1: str, color2: str, ratio: float = 0.5) -> str:
        """Mix two colors.

        Args:
            color1: First hex color
            color2: Second hex color
            ratio: Mix ratio (0.0 = all color1, 1.0 = all color2)

        Returns:
            Mixed color

        """
        try:
            # Parse hex colors
            r1, g1, b1 = self._parse_hex_color(color1)
            r2, g2, b2 = self._parse_hex_color(color2)

            # Mix colors
            r = int(r1 * (1 - ratio) + r2 * ratio)
            g = int(g1 * (1 - ratio) + g2 * ratio)
            b = int(b1 * (1 - ratio) + b2 * ratio)

            return f"#{r:02x}{g:02x}{b:02x}"

        except Exception:
            logger.warning(f"Failed to mix colors {color1} and {color2}")
            return color1

    def _adjust_color_brightness(self, color: str, factor: float) -> str:
        """Adjust color brightness by factor."""
        try:
            r, g, b = self._parse_hex_color(color)

            if factor > 0:
                # Lighten: move towards white
                r = int(r + (255 - r) * factor)
                g = int(g + (255 - g) * factor)
                b = int(b + (255 - b) * factor)
            else:
                # Darken: move towards black
                factor = abs(factor)
                r = int(r * (1 - factor))
                g = int(g * (1 - factor))
                b = int(b * (1 - factor))

            # Clamp values
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))

            return f"#{r:02x}{g:02x}{b:02x}"

        except Exception:
            logger.warning(f"Failed to adjust brightness of color {color}")
            return color

    def _parse_hex_color(self, color: str) -> tuple:
        """Parse hex color string to RGB values."""
        if not color.startswith("#") or len(color) != 7:
            raise ValueError(f"Invalid hex color: {color}")

        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)

        return r, g, b

    # Event System API
    def emit_event(self, event_name: str, **kwargs) -> None:
        """Emit an event.

        Args:
            event_name: Name of event
            **kwargs: Event data

        """
        if self._event_system:
            self._event_system.emit(event_name, **kwargs)

    def subscribe_to_event(self, event_name: str, callback: Callable) -> None:
        """Subscribe to an event.

        Args:
            event_name: Event name
            callback: Callback function

        """
        if self._event_system:
            self._event_system.subscribe(event_name, callback)

    # Logging API
    def log_info(self, message: str) -> None:
        """Log info message."""
        logger.info(f"Extension: {message}")

    def log_warning(self, message: str) -> None:
        """Log warning message."""
        logger.warning(f"Extension: {message}")

    def log_error(self, message: str) -> None:
        """Log error message."""
        logger.error(f"Extension: {message}")

    def log_debug(self, message: str) -> None:
        """Log debug message."""
        logger.debug(f"Extension: {message}")

    # File System API (restricted)
    def read_theme_file(self, file_path: Path) -> str:
        """Read theme file content (restricted to theme directories).

        Args:
            file_path: Path to theme file

        Returns:
            File content

        Raises:
            ExtensionError: If file access is not allowed

        """
        # Validate file path
        if not self._is_safe_theme_path(file_path):
            raise ExtensionError(f"Access to file path not allowed: {file_path}")

        try:
            with open(file_path, encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            raise ExtensionError(f"Failed to read file {file_path}: {e}")

    def _is_safe_theme_path(self, file_path: Path) -> bool:
        """Check if file path is safe for theme operations."""
        # Convert to absolute path
        abs_path = file_path.resolve()

        # Define allowed directories
        allowed_dirs = [
            Path.home() / ".vfwidgets" / "themes",
            Path.home() / ".vfwidgets" / "cache",
            Path.cwd() / "themes",  # Local themes directory
        ]

        # Check if path is within allowed directories
        for allowed_dir in allowed_dirs:
            try:
                abs_path.relative_to(allowed_dir)
                return True
            except ValueError:
                continue

        return False

    # Configuration API
    def get_extension_config(self, extension_name: str, key: str, default: Any = None) -> Any:
        """Get extension configuration value.

        Args:
            extension_name: Extension name
            key: Configuration key
            default: Default value

        Returns:
            Configuration value

        """
        # TODO: Implement configuration storage
        logger.debug(f"Getting config for {extension_name}.{key}")
        return default

    def set_extension_config(self, extension_name: str, key: str, value: Any) -> None:
        """Set extension configuration value.

        Args:
            extension_name: Extension name
            key: Configuration key
            value: Configuration value

        """
        # TODO: Implement configuration storage
        logger.debug(f"Setting config for {extension_name}.{key} = {value}")

    # Validation API
    def validate_theme(self, theme: Theme) -> List[str]:
        """Validate theme and return list of issues.

        Args:
            theme: Theme to validate

        Returns:
            List of validation issues (empty if valid)

        """
        issues = []

        # Basic validation
        if not theme.name:
            issues.append("Theme must have a name")

        if not theme.type:
            issues.append("Theme must have a type")

        if theme.type not in ["light", "dark"]:
            issues.append("Theme type must be 'light' or 'dark'")

        # Color validation
        if theme.colors:
            for attr_name in dir(theme.colors):
                if not attr_name.startswith("_"):
                    color_value = getattr(theme.colors, attr_name)
                    if color_value and not self._is_valid_color(color_value):
                        issues.append(f"Invalid color value for {attr_name}: {color_value}")

        return issues

    def _is_valid_color(self, color: str) -> bool:
        """Check if color string is valid."""
        if not isinstance(color, str):
            return False

        if color.startswith("#"):
            # Hex color
            hex_part = color[1:]
            if len(hex_part) in [3, 6, 8]:  # RGB, RRGGBB, RRGGBBAA
                try:
                    int(hex_part, 16)
                    return True
                except ValueError:
                    return False

        # Could add support for rgb(), rgba(), named colors, etc.
        return False

    # Widget API
    def create_custom_widget(self, widget_class: type, **kwargs) -> Any:
        """Create custom widget (placeholder for Qt integration).

        Args:
            widget_class: Widget class
            **kwargs: Widget parameters

        Returns:
            Widget instance

        """
        # TODO: Implement safe widget creation
        logger.debug(f"Creating custom widget: {widget_class.__name__}")
        return None

    # Utility API
    def interpolate_value(self, start: float, end: float, factor: float) -> float:
        """Interpolate between two values.

        Args:
            start: Start value
            end: End value
            factor: Interpolation factor (0.0 to 1.0)

        Returns:
            Interpolated value

        """
        return start + (end - start) * max(0.0, min(1.0, factor))

    def clamp_value(self, value: float, min_val: float, max_val: float) -> float:
        """Clamp value to range.

        Args:
            value: Value to clamp
            min_val: Minimum value
            max_val: Maximum value

        Returns:
            Clamped value

        """
        return max(min_val, min(max_val, value))

    # System Integration
    def set_theme_manager(self, theme_manager) -> None:
        """Set theme manager reference (internal use)."""
        self._theme_manager = weakref.ref(theme_manager) if theme_manager else None

    def set_event_system(self, event_system) -> None:
        """Set event system reference (internal use)."""
        self._event_system = weakref.ref(event_system) if event_system else None
