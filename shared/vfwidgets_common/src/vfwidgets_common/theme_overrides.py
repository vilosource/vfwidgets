"""Universal theme token override system for VFWidgets applications.

This module provides a universal pattern for per-application, per-theme-type
token customization that works with any ThemedApplication.

Key Features:
- Theme-type specific overrides (dark ≠ light ≠ high-contrast)
- No cross-contamination between theme types
- Simple dataclass-based API
- Automatic theme composition
- Comprehensive error handling

Usage:
    >>> from vfwidgets_common.theme_overrides import (
    ...     ThemeOverrides,
    ...     apply_theme_with_overrides
    ... )
    >>>
    >>> # Create overrides
    >>> overrides = ThemeOverrides(
    ...     dark_overrides={"markdown.colors.link": "#58a6ff"},
    ...     light_overrides={"markdown.colors.link": "#0969da"}
    ... )
    >>>
    >>> # Apply theme with overrides
    >>> apply_theme_with_overrides("dark", overrides)
    True

Design Document: apps/reamde/wip/universal-theme-overrides-DESIGN.md
"""

import logging
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication

logger = logging.getLogger(__name__)


@dataclass
class ThemeOverrides:
    """Per-theme-type token overrides.

    Dark, light, and high-contrast themes get separate override sets.
    When a theme is applied, only the matching type's overrides are used.

    This ensures no cross-contamination: dark theme overrides don't affect
    light themes, and vice versa.

    Attributes:
        dark_overrides: Token overrides for all dark themes
        light_overrides: Token overrides for all light themes
        high_contrast_overrides: Token overrides for all high-contrast themes

    Example:
        >>> overrides = ThemeOverrides(
        ...     dark_overrides={
        ...         "markdown.colors.background": "#0d1117",
        ...         "markdown.colors.link": "#58a6ff"
        ...     },
        ...     light_overrides={
        ...         "markdown.colors.background": "#ffffff",
        ...         "markdown.colors.link": "#0969da"
        ...     }
        ... )
        >>>
        >>> # When "dark" theme is active: dark_overrides apply
        >>> # When "monokai" theme is active (type="dark"): dark_overrides apply
        >>> # When "light" theme is active: light_overrides apply
    """

    dark_overrides: dict[str, str] = field(default_factory=dict)
    light_overrides: dict[str, str] = field(default_factory=dict)
    high_contrast_overrides: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Serialize for JSON storage.

        Returns:
            Dictionary with dark_overrides, light_overrides, high_contrast_overrides

        Example:
            >>> overrides = ThemeOverrides(dark_overrides={"token": "#color"})
            >>> data = overrides.to_dict()
            >>> data
            {'dark_overrides': {'token': '#color'}, 'light_overrides': {}, ...}
        """
        return {
            "dark_overrides": self.dark_overrides,
            "light_overrides": self.light_overrides,
            "high_contrast_overrides": self.high_contrast_overrides,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ThemeOverrides":
        """Deserialize from JSON storage.

        Args:
            data: Dictionary with dark_overrides, light_overrides, etc.

        Returns:
            ThemeOverrides instance

        Example:
            >>> data = {'dark_overrides': {'token': '#color'}}
            >>> overrides = ThemeOverrides.from_dict(data)
            >>> overrides.dark_overrides
            {'token': '#color'}
        """
        return cls(
            dark_overrides=data.get("dark_overrides", {}),
            light_overrides=data.get("light_overrides", {}),
            high_contrast_overrides=data.get("high_contrast_overrides", {}),
        )

    def get_overrides_for_theme_type(self, theme_type: str) -> dict[str, str]:
        """Get overrides for specific theme type.

        Args:
            theme_type: "dark", "light", or "high-contrast"

        Returns:
            Dictionary of token overrides for that type

        Example:
            >>> overrides = ThemeOverrides(dark_overrides={"token": "#000"})
            >>> overrides.get_overrides_for_theme_type("dark")
            {'token': '#000'}
            >>> overrides.get_overrides_for_theme_type("light")
            {}
        """
        if theme_type == "dark":
            return self.dark_overrides
        elif theme_type == "light":
            return self.light_overrides
        elif theme_type == "high-contrast":
            return self.high_contrast_overrides
        else:
            logger.warning(f"Unknown theme type '{theme_type}' - returning empty overrides")
            return {}


def apply_theme_with_overrides(
    base_theme_name: str,
    overrides: ThemeOverrides,
    validate: bool = True,
    app: Optional["QApplication"] = None,
) -> bool:
    """Apply theme with per-theme-type overrides.

    This is the ONE FUNCTION all apps call to apply themed overrides.

    Process:
    1. Get base theme from theme manager
    2. Check base theme's type (dark/light/high-contrast)
    3. Select matching overrides (dark_overrides for dark themes, etc.)
    4. If overrides exist: compose base + overrides, then apply
    5. If no overrides: just apply base theme

    Args:
        base_theme_name: Theme name (e.g., "dark", "light", "monokai")
        overrides: ThemeOverrides with type-specific overrides
        validate: If True, validate token paths and color values
        app: QApplication instance (auto-detected if None)

    Returns:
        True if applied successfully, False otherwise

    Example:
        >>> overrides = ThemeOverrides(
        ...     dark_overrides={"markdown.colors.background": "#0d1117"}
        ... )
        >>> apply_theme_with_overrides("dark", overrides)
        True
        # Dark theme applied with background override

        >>> apply_theme_with_overrides("light", overrides)
        True
        # Light theme applied WITHOUT dark overrides
    """
    try:
        from PySide6.QtWidgets import QApplication
    except ImportError:
        logger.error("PySide6 not installed - cannot apply theme overrides")
        return False

    try:
        from vfwidgets_theme.core.theme import ThemeBuilder, ThemeComposer
    except ImportError:
        logger.error("vfwidgets_theme not installed - cannot apply theme overrides")
        return False

    # Get application
    if app is None:
        app = QApplication.instance()

    if not app:
        logger.error("No QApplication instance found - cannot apply theme")
        return False

    if not hasattr(app, "_theme_manager"):
        logger.error(
            "Application is not a ThemedApplication - cannot apply theme overrides. "
            "Use ThemedApplication instead of QApplication."
        )
        return False

    # Get base theme
    try:
        base_theme = app._theme_manager.get_theme(base_theme_name)
    except KeyError:
        available = app._theme_manager.available_themes
        logger.error(
            f"Theme '{base_theme_name}' not found. " f"Available themes: {', '.join(available)}"
        )
        return False
    except Exception as e:
        logger.error(f"Failed to get base theme '{base_theme_name}': {e}")
        return False

    # Get theme type
    theme_type = base_theme.type  # "dark", "light", or "high-contrast"
    logger.debug(f"Base theme '{base_theme_name}' is type '{theme_type}'")

    # Select correct overrides for this theme type
    token_overrides = overrides.get_overrides_for_theme_type(theme_type)

    # If no overrides, just apply base theme
    if not token_overrides:
        logger.debug(f"No overrides for theme type '{theme_type}', applying base theme only")
        try:
            return app.set_theme(base_theme)
        except Exception as e:
            logger.error(f"Failed to apply base theme: {e}")
            return False

    # Validate overrides if requested
    validated_overrides = token_overrides
    if validate:
        validated_overrides = _validate_token_overrides(token_overrides)

        if not validated_overrides:
            logger.warning(
                "All token overrides were invalid - applying base theme without overrides"
            )
            try:
                return app.set_theme(base_theme)
            except Exception as e:
                logger.error(f"Failed to apply base theme: {e}")
                return False

    # Build override theme
    try:
        logger.debug(
            f"Building override theme with {len(validated_overrides)} tokens "
            f"for theme type '{theme_type}'"
        )
        override_builder = ThemeBuilder(f"{base_theme_name}-overrides")
        override_builder.set_type(theme_type)

        for token_path, color_value in validated_overrides.items():
            try:
                override_builder.add_color(token_path, color_value)
            except Exception as e:
                logger.warning(
                    f"Failed to add token '{token_path}' with color '{color_value}': {e}"
                )

        override_theme = override_builder.build()
    except Exception as e:
        logger.error(f"Failed to build override theme: {e}")
        logger.warning("Falling back to base theme without overrides")
        try:
            return app.set_theme(base_theme)
        except Exception as e2:
            logger.error(f"Failed to apply fallback base theme: {e2}")
            return False

    # Compose themes
    try:
        logger.debug("Composing base theme with overrides")
        composer = ThemeComposer()
        effective_theme = composer.compose(
            base_theme, override_theme, name=f"{base_theme_name}-with-overrides"
        )
    except Exception as e:
        logger.error(f"Failed to compose themes: {e}")
        logger.warning("Falling back to base theme without overrides")
        try:
            return app.set_theme(base_theme)
        except Exception as e2:
            logger.error(f"Failed to apply fallback base theme: {e2}")
            return False

    # Apply composed theme
    try:
        success = app.set_theme(effective_theme)
        if success:
            logger.info(
                f"Successfully applied theme '{base_theme_name}' (type '{theme_type}') "
                f"with {len(validated_overrides)} token overrides"
            )
        else:
            logger.error("Failed to apply composed theme (set_theme returned False)")
        return success
    except Exception as e:
        logger.error(f"Failed to apply composed theme: {e}")
        return False


def _validate_token_overrides(token_overrides: dict[str, str]) -> dict[str, str]:
    """Validate token paths and color values.

    Args:
        token_overrides: Dictionary of token_path → color_value

    Returns:
        Dictionary with only valid token overrides
    """
    try:
        from vfwidgets_theme.core.tokens import ColorTokenRegistry

        # Get valid token names
        valid_tokens = set(ColorTokenRegistry.get_all_token_names())
    except (ImportError, AttributeError):
        logger.warning("Cannot validate tokens - vfwidgets_theme not available")
        # Skip validation, return as-is
        return token_overrides

    validated = {}
    for token_path, color_value in token_overrides.items():
        # Validate token path
        if token_path not in valid_tokens:
            logger.warning(
                f"Unknown token '{token_path}' - skipping. "
                f"Token may not exist in theme system. "
                f"Use get_tokens_by_category() to discover valid tokens."
            )
            continue

        # Validate color value
        if not color_value or not isinstance(color_value, str):
            logger.warning(
                f"Invalid color value for token '{token_path}': {color_value!r} - skipping"
            )
            continue

        # Basic color format validation
        color_value = color_value.strip()
        if not _is_valid_color_format(color_value):
            logger.warning(
                f"Invalid color format for token '{token_path}': {color_value!r} - skipping. "
                f"Expected hex (#RRGGBB), rgb(), rgba(), or named color."
            )
            continue

        # Validation passed
        validated[token_path] = color_value

    if len(validated) < len(token_overrides):
        skipped = len(token_overrides) - len(validated)
        logger.info(f"Validated {len(validated)} tokens, skipped {skipped} invalid tokens")

    return validated


def _is_valid_color_format(color: str) -> bool:
    """Check if color string is in valid format.

    Accepts:
    - Hex: #RGB, #RRGGBB, #RRGGBBAA
    - RGB: rgb(r, g, b)
    - RGBA: rgba(r, g, b, a)
    - Named: "red", "blue", etc.

    Args:
        color: Color string to validate

    Returns:
        True if valid format, False otherwise
    """
    color = color.lower().strip()

    # Hex color
    if re.match(r"^#([0-9a-f]{3}|[0-9a-f]{6}|[0-9a-f]{8})$", color):
        return True

    # RGB/RGBA
    if color.startswith("rgb(") or color.startswith("rgba("):
        return True

    # HSL/HSLA
    if color.startswith("hsl(") or color.startswith("hsla("):
        return True

    # Named colors (basic set)
    named_colors = {
        "black",
        "white",
        "red",
        "green",
        "blue",
        "yellow",
        "cyan",
        "magenta",
        "gray",
        "grey",
        "darkred",
        "darkgreen",
        "darkblue",
        "darkgray",
        "darkgrey",
        "lightgray",
        "lightgrey",
        "transparent",
    }
    if color in named_colors:
        return True

    return False


def get_tokens_by_category(category: str) -> list[tuple[str, str, str]]:
    """Get all tokens for a category from the theme system.

    Automatically discovers all tokens in a category, saving developers
    from manually declaring each token.

    Args:
        category: Token category name
            - "markdown" → all markdown.colors.* tokens
            - "terminal" → all terminal.colors.* tokens
            - "editor" → all editor.* tokens
            - etc.

    Returns:
        List of (token_path, label, description) tuples ready for use
        with ThemeOverrideEditor or custom UIs.

    Example:
        >>> # Instead of manually declaring:
        >>> # MARKDOWN_TOKENS = [
        >>> #     ("markdown.colors.background", "Background", "..."),
        >>> #     ("markdown.colors.foreground", "Foreground", "..."),
        >>> #     ... # 10 more lines
        >>> # ]
        >>>
        >>> # Just use:
        >>> MARKDOWN_TOKENS = get_tokens_by_category("markdown")
        >>> len(MARKDOWN_TOKENS)
        12

        >>> # Can also filter:
        >>> MARKDOWN_TOKENS = [
        ...     t for t in get_tokens_by_category("markdown")
        ...     if "scrollbar" not in t[0]
        ... ]
    """
    try:
        from vfwidgets_theme.core.tokens import ColorTokenRegistry
    except ImportError:
        logger.error(
            "vfwidgets_theme not installed - cannot discover tokens. "
            "Install with: pip install vfwidgets-theme"
        )
        return []

    # Get all tokens from registry
    try:
        all_tokens = ColorTokenRegistry.ALL_TOKENS
    except AttributeError:
        logger.error("ColorTokenRegistry.ALL_TOKENS not available")
        return []

    # Filter to category
    # Match both "markdown" and "markdown.colors"
    prefix_patterns = [
        f"{category}.",  # e.g., "markdown."
        f"{category}.colors.",  # e.g., "markdown.colors."
    ]

    category_tokens = [
        token
        for token in all_tokens
        if any(token.name.startswith(prefix) for prefix in prefix_patterns)
    ]

    if not category_tokens:
        logger.warning(f"No tokens found for category '{category}'")
        return []

    # Convert to tuple format
    result = []
    for token in category_tokens:
        # Generate friendly label from token path
        # "markdown.colors.code.background" → "Code Background"
        label = _generate_label(token.name)

        result.append((token.name, label, token.description))

    logger.debug(f"Discovered {len(result)} tokens for category '{category}'")
    return result


def _generate_label(token_path: str) -> str:
    """Generate friendly label from token path.

    Examples:
        "markdown.colors.background" → "Background"
        "markdown.colors.code.background" → "Code Background"
        "terminal.colors.ansiBlack" → "Ansi Black"
    """
    parts = token_path.split(".")

    # Get meaningful parts (skip category prefix)
    # "markdown.colors.code.background" → ["code", "background"]
    if len(parts) > 2:
        meaningful_parts = parts[2:]  # Skip "markdown.colors"
    else:
        meaningful_parts = parts[-1:]  # Just use last part

    # Convert to title case
    # ["code", "background"] → ["Code", "Background"]
    words = []
    for part in meaningful_parts:
        # Split camelCase: "ansiBlack" → ["ansi", "Black"]
        camel_words = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\b)", part)
        if camel_words:
            words.extend(camel_words)
        else:
            words.append(part)

    # Join and title case
    label = " ".join(word.capitalize() for word in words)
    return label


__all__ = [
    "ThemeOverrides",
    "apply_theme_with_overrides",
    "get_tokens_by_category",
]
