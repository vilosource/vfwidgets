"""Token type definitions and resolvers.

This module provides the infrastructure for unified token resolution
across different token types (colors, fonts, sizes, etc.).

Key Classes:
- TokenType: Enumeration of supported token types
- TokenResolver: Base class for type-specific resolvers
- ColorTokenResolver: Resolver for color tokens
- TOKEN_RESOLVERS: Global registry of resolvers by type

Design:
- Each token type has a dedicated resolver
- Resolvers can opt into override system support
- Type-specific validation ensures correctness
- Extensible for new token types

Performance:
- Fast type dispatch via dictionary lookup
- Minimal overhead per resolution
- Cacheable results at widget level
"""

from enum import Enum, auto
from typing import Any, Optional, TYPE_CHECKING

from PySide6.QtGui import QColor

from ..logging import get_debug_logger

if TYPE_CHECKING:
    from .theme import Theme

logger = get_debug_logger(__name__)


class TokenType(Enum):
    """Types of theme tokens that can be resolved.

    Each type corresponds to a specific kind of theme property
    and may have different resolution logic and override support.
    """

    COLOR = auto()      # Color values (hex, rgb, named)
    FONT = auto()       # Font family names
    FONT_SIZE = auto()  # Font sizes (px, pt)
    SIZE = auto()       # Dimensions (width, height, etc.)
    SPACING = auto()    # Padding, margin, gap
    BORDER = auto()     # Border properties
    OPACITY = auto()    # Opacity/alpha values
    RADIUS = auto()     # Border radius values
    SHADOW = auto()     # Shadow properties
    OTHER = auto()      # Generic values


class TokenResolver:
    """Base class for token type-specific resolvers.

    Subclasses implement resolution logic for specific token types
    and specify whether the type supports the override system.
    """

    def can_override(self) -> bool:
        """Whether this token type supports override system.

        Returns:
            True if this token type can be overridden by users/apps

        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement can_override()"
        )

    def resolve_from_theme(
        self,
        theme: "Theme",
        token: str,
        fallback: Optional[Any] = None
    ) -> Optional[Any]:
        """Resolve token from theme data.

        Args:
            theme: Theme object to resolve from
            token: Token name (e.g., "editor.background")
            fallback: Value to return if token not found

        Returns:
            Resolved token value or fallback

        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement resolve_from_theme()"
        )

    def validate_value(self, value: Any) -> bool:
        """Validate that value is appropriate for this token type.

        Args:
            value: Value to validate

        Returns:
            True if value is valid for this token type

        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement validate_value()"
        )


class ColorTokenResolver(TokenResolver):
    """Resolver for color tokens.

    Supports:
    - Hex colors (#rgb, #rrggbb, #rrggbbaa)
    - Named colors (red, blue, transparent, etc.)
    - RGB/RGBA functions (rgb(r,g,b), rgba(r,g,b,a))
    - Override system integration
    """

    def can_override(self) -> bool:
        """Colors support the override system."""
        return True

    def resolve_from_theme(
        self,
        theme: "Theme",
        token: str,
        fallback: Optional[str] = None
    ) -> Optional[str]:
        """Resolve color from theme's color tokens.

        Args:
            theme: Theme object with colors attribute
            token: Color token name (e.g., "editor.background")
            fallback: Fallback color if token not found

        Returns:
            Color value from theme or fallback

        """
        try:
            # Navigate to colors
            if not hasattr(theme, 'colors'):
                return fallback

            colors = theme.colors

            # Try dictionary access first (most common case)
            if isinstance(colors, dict):
                # Try direct key access with dots
                if token in colors:
                    color = colors[token]
                    if isinstance(color, str):
                        return color

                # Try nested dictionary navigation
                parts = token.split('.')
                if len(parts) > 1:
                    current = colors
                    for part in parts:
                        if isinstance(current, dict) and part in current:
                            current = current[part]
                        else:
                            break
                    else:
                        # Successfully navigated all parts
                        if isinstance(current, str):
                            return current

            # Try attribute access as fallback
            # Convert "editor.background" to "editor_background"
            attr_name = token.replace('.', '_')

            if hasattr(colors, attr_name):
                color = getattr(colors, attr_name)
                if isinstance(color, str):
                    return color

            return fallback

        except Exception as e:
            logger.debug(f"Error resolving color token {token}: {e}")
            return fallback

    def validate_value(self, value: Any) -> bool:
        """Validate color format using Qt's QColor.

        Args:
            value: Color value to validate

        Returns:
            True if color is valid

        """
        if not isinstance(value, str):
            return False

        if not value:  # Empty string
            return False

        return QColor.isValidColor(value)


class FontTokenResolver(TokenResolver):
    """Resolver for font family tokens.

    Note: Fonts do not currently support the override system,
    but this can be added in the future.
    """

    def can_override(self) -> bool:
        """Fonts don't support overrides (yet)."""
        return False

    def resolve_from_theme(
        self,
        theme: "Theme",
        token: str,
        fallback: Optional[str] = None
    ) -> Optional[str]:
        """Resolve font from theme data.

        Args:
            theme: Theme object
            token: Font token name
            fallback: Fallback font if not found

        Returns:
            Font family name or fallback

        """
        # TODO: Implement font resolution when theme supports fonts
        # For now, just return fallback
        return fallback

    def validate_value(self, value: Any) -> bool:
        """Validate font family name.

        Args:
            value: Font family name

        Returns:
            True if value is a non-empty string

        """
        return isinstance(value, str) and len(value) > 0


class SizeTokenResolver(TokenResolver):
    """Resolver for size/dimension tokens.

    Handles: widths, heights, font sizes, etc.
    """

    def can_override(self) -> bool:
        """Sizes don't support overrides (yet)."""
        return False

    def resolve_from_theme(
        self,
        theme: "Theme",
        token: str,
        fallback: Optional[str] = None
    ) -> Optional[str]:
        """Resolve size from theme data.

        Args:
            theme: Theme object
            token: Size token name
            fallback: Fallback size if not found

        Returns:
            Size value or fallback

        """
        # TODO: Implement size resolution when theme supports sizes
        return fallback

    def validate_value(self, value: Any) -> bool:
        """Validate size value.

        Args:
            value: Size value (should be string with unit, e.g., "12px")

        Returns:
            True if value is a valid size

        """
        if not isinstance(value, str):
            return False

        # Simple validation: should have digits and optional unit
        import re
        return bool(re.match(r'^\d+(\.\d+)?(px|pt|em|rem|%)?$', value))


class GenericTokenResolver(TokenResolver):
    """Generic resolver for OTHER token types.

    Used as fallback for token types that don't have
    a dedicated resolver.
    """

    def can_override(self) -> bool:
        """Generic tokens don't support overrides."""
        return False

    def resolve_from_theme(
        self,
        theme: "Theme",
        token: str,
        fallback: Optional[Any] = None
    ) -> Optional[Any]:
        """Attempt generic resolution from theme.

        Args:
            theme: Theme object
            token: Token name
            fallback: Fallback value

        Returns:
            Resolved value or fallback

        """
        # Try to navigate theme by dot-separated path
        try:
            parts = token.split('.')
            current = theme

            for part in parts:
                if hasattr(current, part):
                    current = getattr(current, part)
                elif isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return fallback

            return current if current is not None else fallback

        except Exception as e:
            logger.debug(f"Error resolving generic token {token}: {e}")
            return fallback

    def validate_value(self, value: Any) -> bool:
        """Generic validation - accept any non-None value.

        Args:
            value: Value to validate

        Returns:
            True if value is not None

        """
        return value is not None


# ============================================================================
# Global Registry
# ============================================================================

# Registry of resolvers by token type
TOKEN_RESOLVERS: dict[TokenType, TokenResolver] = {
    TokenType.COLOR: ColorTokenResolver(),
    TokenType.FONT: FontTokenResolver(),
    TokenType.FONT_SIZE: SizeTokenResolver(),  # Reuse size resolver
    TokenType.SIZE: SizeTokenResolver(),
    TokenType.SPACING: SizeTokenResolver(),  # Reuse size resolver
    TokenType.BORDER: GenericTokenResolver(),
    TokenType.OPACITY: GenericTokenResolver(),
    TokenType.RADIUS: SizeTokenResolver(),
    TokenType.SHADOW: GenericTokenResolver(),
    TokenType.OTHER: GenericTokenResolver(),
}


def get_resolver(token_type: TokenType) -> TokenResolver:
    """Get resolver for a specific token type.

    Args:
        token_type: Type of token to get resolver for

    Returns:
        TokenResolver instance for the type

    Raises:
        ValueError: If token type is invalid

    """
    if token_type not in TOKEN_RESOLVERS:
        raise ValueError(
            f"No resolver registered for token type {token_type}. "
            f"Available types: {', '.join(t.name for t in TOKEN_RESOLVERS.keys())}"
        )

    return TOKEN_RESOLVERS[token_type]


__all__ = [
    "TokenType",
    "TokenResolver",
    "ColorTokenResolver",
    "FontTokenResolver",
    "SizeTokenResolver",
    "GenericTokenResolver",
    "TOKEN_RESOLVERS",
    "get_resolver",
]
