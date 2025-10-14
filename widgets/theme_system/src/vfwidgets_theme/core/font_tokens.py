"""Font token resolution with hierarchical fallbacks.

This module provides the FontTokenRegistry which resolves font tokens
hierarchically, similar to how color tokens work in the theme system.

Key Features:
- Hierarchical resolution (terminal.fontSize → fonts.size → default)
- Platform font availability detection
- LRU caching for performance (<100μs resolution)
- QFont creation from tokens
- Cross-platform font fallbacks

Design:
- Immutable resolution chains defined in HIERARCHY_MAP
- Static methods for stateless resolution
- Cache invalidation support for theme changes

Phase 2 Implementation - Font Token Resolution
"""

from functools import lru_cache
from typing import Optional

from PySide6.QtGui import QFont, QFontDatabase

from .theme import Theme

# Type alias for the theme parameter to avoid circular imports in type hints
ThemeType = Theme


class FontTokenRegistry:
    """Central registry for font token resolution with hierarchical fallbacks.

    Provides static methods for resolving font tokens with fallback chains,
    similar to color token resolution but specific to font properties.

    Resolution Hierarchy Examples:
        terminal.fontFamily → fonts.mono → ["monospace"] (guaranteed)
        tabs.fontFamily → fonts.ui → ["sans-serif"] (guaranteed)
        terminal.fontSize → fonts.size → 13 (default)

    Performance:
        - LRU cached resolution: <100μs per lookup
        - First resolution: ~1ms (font database query)
        - Cache size: 256 entries per method

    Thread Safety:
        - All methods are thread-safe (no shared mutable state)
        - LRU cache is thread-safe in Python 3.2+
    """

    # Hierarchical resolution chains
    # Each token maps to a list of fallback tokens to try in order
    HIERARCHY_MAP = {
        # Terminal widget fonts (inherit from fonts.mono)
        "terminal.fontFamily": ["terminal.fontFamily", "fonts.mono"],
        "terminal.fontSize": ["terminal.fontSize", "fonts.size"],
        "terminal.fontWeight": ["terminal.fontWeight", "fonts.weight"],
        "terminal.lineHeight": ["terminal.lineHeight", "fonts.lineHeight"],
        "terminal.letterSpacing": ["terminal.letterSpacing", "fonts.letterSpacing"],
        # Tabs widget fonts (inherit from fonts.ui)
        "tabs.fontFamily": ["tabs.fontFamily", "fonts.ui"],
        "tabs.fontSize": ["tabs.fontSize", "fonts.size"],
        "tabs.fontWeight": ["tabs.fontWeight", "fonts.weight"],
        # Editor fonts (inherit from fonts.mono for code)
        "editor.fontFamily": ["editor.fontFamily", "fonts.mono"],
        "editor.fontSize": ["editor.fontSize", "fonts.size"],
        "editor.fontWeight": ["editor.fontWeight", "fonts.weight"],
        "editor.lineHeight": ["editor.lineHeight", "fonts.lineHeight"],
        # UI fonts (general UI elements)
        "ui.fontFamily": ["ui.fontFamily", "fonts.ui"],
        "ui.fontSize": ["ui.fontSize", "fonts.size"],
        "ui.fontWeight": ["ui.fontWeight", "fonts.weight"],
    }

    # Default fallback values
    DEFAULT_FONT_SIZE = 13.0
    DEFAULT_FONT_WEIGHT = 400  # normal
    DEFAULT_LINE_HEIGHT = 1.4
    DEFAULT_LETTER_SPACING = 0.0

    # System default font families (guaranteed to exist)
    SYSTEM_DEFAULTS = {
        "mono": ["monospace"],
        "ui": ["sans-serif"],
        "serif": ["serif"],
    }

    @staticmethod
    @lru_cache(maxsize=256)
    def get_font_family(token: str, theme: Theme) -> list[str]:
        """Get font family list with hierarchical resolution.

        Resolves font family tokens with fallback chains. Always returns
        a list of font families, never None.

        Args:
            token: Font family token (e.g., "terminal.fontFamily")
            theme: Theme to resolve from

        Returns:
            List of font family names with fallbacks

        Examples:
            >>> get_font_family("terminal.fontFamily", theme)
            ["Cascadia Code", "JetBrains Mono", "Consolas", "monospace"]

            >>> get_font_family("tabs.fontFamily", theme)
            ["Segoe UI Semibold", "Inter", "sans-serif"]

        """
        # Get resolution chain
        chain = FontTokenRegistry.HIERARCHY_MAP.get(token, [token])

        # Try each token in chain
        for candidate_token in chain:
            if candidate_token in theme.fonts:
                value = theme.fonts[candidate_token]

                # Convert string to list
                if isinstance(value, str):
                    return [value]
                elif isinstance(value, list):
                    return value

        # Fallback to system defaults based on token category
        if "mono" in token or "terminal" in token or "editor" in token:
            return FontTokenRegistry.SYSTEM_DEFAULTS["mono"]
        elif "ui" in token or "tabs" in token:
            return FontTokenRegistry.SYSTEM_DEFAULTS["ui"]
        elif "serif" in token:
            return FontTokenRegistry.SYSTEM_DEFAULTS["serif"]

        # Ultimate fallback
        return ["sans-serif"]

    @staticmethod
    @lru_cache(maxsize=256)
    def get_font_size(token: str, theme: Theme) -> float:
        """Get font size with hierarchical resolution.

        Returns font size in points (DPI-aware). Always returns a float.

        Args:
            token: Font size token (e.g., "terminal.fontSize")
            theme: Theme to resolve from

        Returns:
            Font size in points (float)

        Examples:
            >>> get_font_size("terminal.fontSize", theme)
            14.0

            >>> get_font_size("tabs.fontSize", theme)  # Falls back to fonts.size
            13.0

        """
        chain = FontTokenRegistry.HIERARCHY_MAP.get(token, [token])

        for candidate_token in chain:
            if candidate_token in theme.fonts:
                value = theme.fonts[candidate_token]
                if isinstance(value, (int, float)):
                    return float(value)

        return FontTokenRegistry.DEFAULT_FONT_SIZE

    @staticmethod
    @lru_cache(maxsize=256)
    def get_font_weight(token: str, theme: Theme) -> int:
        """Get font weight with hierarchical resolution.

        Converts string weights to integer values (100-900).
        Returns Qt-compatible weight values.

        Args:
            token: Font weight token (e.g., "terminal.fontWeight")
            theme: Theme to resolve from

        Returns:
            Font weight as integer (100-900)

        Weight Conversion:
            - "thin" → 100
            - "light" → 300
            - "normal" → 400 (default)
            - "medium" → 500
            - "semibold" → 600
            - "bold" → 700
            - "black" → 900

        Examples:
            >>> get_font_weight("terminal.fontWeight", theme)
            400

            >>> get_font_weight("tabs.fontWeight", theme)  # "semibold"
            600

        """
        chain = FontTokenRegistry.HIERARCHY_MAP.get(token, [token])

        # String to weight mapping
        weight_map = {
            "thin": 100,
            "extralight": 200,
            "light": 300,
            "normal": 400,
            "medium": 500,
            "semibold": 600,
            "bold": 700,
            "extrabold": 800,
            "black": 900,
            # Also support string versions of numbers
            "100": 100,
            "200": 200,
            "300": 300,
            "400": 400,
            "500": 500,
            "600": 600,
            "700": 700,
            "800": 800,
            "900": 900,
        }

        for candidate_token in chain:
            if candidate_token in theme.fonts:
                value = theme.fonts[candidate_token]

                if isinstance(value, int):
                    return value
                elif isinstance(value, str):
                    return weight_map.get(value.lower(), FontTokenRegistry.DEFAULT_FONT_WEIGHT)

        return FontTokenRegistry.DEFAULT_FONT_WEIGHT

    @staticmethod
    @lru_cache(maxsize=256)
    def get_line_height(token: str, theme: Theme) -> float:
        """Get line height multiplier with hierarchical resolution.

        Returns line height as a multiplier (e.g., 1.4 = 140% of font size).

        Args:
            token: Line height token (e.g., "terminal.lineHeight")
            theme: Theme to resolve from

        Returns:
            Line height multiplier (float)

        Examples:
            >>> get_line_height("terminal.lineHeight", theme)
            1.4

            >>> get_line_height("editor.lineHeight", theme)
            1.5

        """
        chain = FontTokenRegistry.HIERARCHY_MAP.get(token, [token])

        for candidate_token in chain:
            if candidate_token in theme.fonts:
                value = theme.fonts[candidate_token]
                if isinstance(value, (int, float)):
                    return float(value)

        return FontTokenRegistry.DEFAULT_LINE_HEIGHT

    @staticmethod
    @lru_cache(maxsize=256)
    def get_letter_spacing(token: str, theme: Theme) -> float:
        """Get letter spacing in pixels with hierarchical resolution.

        Returns letter spacing in pixels (can be negative for tighter spacing).

        Args:
            token: Letter spacing token (e.g., "terminal.letterSpacing")
            theme: Theme to resolve from

        Returns:
            Letter spacing in pixels (float)

        Examples:
            >>> get_letter_spacing("terminal.letterSpacing", theme)
            0.0

            >>> get_letter_spacing("editor.letterSpacing", theme)
            -0.5  # Tighter spacing

        """
        chain = FontTokenRegistry.HIERARCHY_MAP.get(token, [token])

        for candidate_token in chain:
            if candidate_token in theme.fonts:
                value = theme.fonts[candidate_token]
                if isinstance(value, (int, float)):
                    return float(value)

        return FontTokenRegistry.DEFAULT_LETTER_SPACING

    @staticmethod
    def get_qfont(token_prefix: str, theme: Theme) -> QFont:
        """Create QFont from token prefix with hierarchical resolution.

        Convenience method that resolves all font properties and creates
        a QFont instance. This is the primary API for widgets.

        Args:
            token_prefix: Token prefix (e.g., "terminal", "tabs", "ui")
            theme: Theme to resolve from

        Returns:
            Configured QFont instance

        Examples:
            >>> font = get_qfont("terminal", theme)
            >>> font.family()  # "Cascadia Code" (or first available)
            >>> font.pointSizeF()  # 14.0
            >>> font.weight()  # 400

        Note:
            Line height and letter spacing are NOT applied to QFont
            (Qt doesn't support these on QFont directly). Widgets must
            apply these separately if needed.

        """
        # Resolve font properties
        families = FontTokenRegistry.get_font_family(f"{token_prefix}.fontFamily", theme)
        size = FontTokenRegistry.get_font_size(f"{token_prefix}.fontSize", theme)
        weight = FontTokenRegistry.get_font_weight(f"{token_prefix}.fontWeight", theme)

        # Find first available font (convert list to tuple for caching)
        available_family = FontTokenRegistry.get_available_font(tuple(families))

        # Create QFont
        font = QFont(available_family or families[0])
        font.setPointSizeF(size)

        # Convert weight to QFont.Weight enum (Qt 6.9+)
        # Map 100-900 to QFont.Weight values
        if weight <= 100:
            font.setWeight(QFont.Weight.Thin)
        elif weight <= 200:
            font.setWeight(QFont.Weight.ExtraLight)
        elif weight <= 300:
            font.setWeight(QFont.Weight.Light)
        elif weight <= 400:
            font.setWeight(QFont.Weight.Normal)
        elif weight <= 500:
            font.setWeight(QFont.Weight.Medium)
        elif weight <= 600:
            font.setWeight(QFont.Weight.DemiBold)
        elif weight <= 700:
            font.setWeight(QFont.Weight.Bold)
        elif weight <= 800:
            font.setWeight(QFont.Weight.ExtraBold)
        else:
            font.setWeight(QFont.Weight.Black)

        return font

    @staticmethod
    @lru_cache(maxsize=128)
    def get_available_font(families: tuple[str, ...]) -> Optional[str]:
        """Find first available font from list.

        Queries Qt's font database to find the first font that exists
        on the system. Case-insensitive matching.

        Args:
            families: Tuple of font family names (must be tuple for caching)

        Returns:
            First available font family name, or None if none found

        Examples:
            >>> get_available_font(("JetBrains Mono", "Consolas", "monospace"))
            "Consolas"  # If JetBrains Mono not installed

            >>> get_available_font(("Nonexistent Font", "monospace"))
            "monospace"  # Generic family always available

        Note:
            Generic families (monospace, sans-serif, serif) are always
            considered available and will be returned if reached.

        """
        # Get all available fonts (cached by Qt)
        db = QFontDatabase()
        available_fonts = {f.lower() for f in db.families()}

        # Generic families are always available
        generic_families = {"monospace", "sans-serif", "serif", "cursive", "fantasy"}

        for family in families:
            family_lower = family.lower()

            # Check if it's a generic family (always available)
            if family_lower in generic_families:
                return family

            # Check if font is available on system
            if family_lower in available_fonts:
                return family

        # No fonts available
        return None

    @staticmethod
    def clear_cache() -> None:
        """Clear all LRU caches.

        Call this when theme changes to ensure fresh resolution.
        Cache will be repopulated on next access.

        Examples:
            >>> # Theme changed, clear caches
            >>> FontTokenRegistry.clear_cache()

        """
        FontTokenRegistry.get_font_family.cache_clear()
        FontTokenRegistry.get_font_size.cache_clear()
        FontTokenRegistry.get_font_weight.cache_clear()
        FontTokenRegistry.get_line_height.cache_clear()
        FontTokenRegistry.get_letter_spacing.cache_clear()
        FontTokenRegistry.get_available_font.cache_clear()


# Convenience functions for common operations
def resolve_font_family(token: str, theme: Theme) -> list[str]:
    """Convenience wrapper for FontTokenRegistry.get_font_family."""
    return FontTokenRegistry.get_font_family(token, theme)


def resolve_font_size(token: str, theme: Theme) -> float:
    """Convenience wrapper for FontTokenRegistry.get_font_size."""
    return FontTokenRegistry.get_font_size(token, theme)


def resolve_font_weight(token: str, theme: Theme) -> int:
    """Convenience wrapper for FontTokenRegistry.get_font_weight."""
    return FontTokenRegistry.get_font_weight(token, theme)


def create_qfont_from_token(token_prefix: str, theme: Theme) -> QFont:
    """Convenience wrapper for FontTokenRegistry.get_qfont."""
    return FontTokenRegistry.get_qfont(token_prefix, theme)


__all__ = [
    "FontTokenRegistry",
    "resolve_font_family",
    "resolve_font_size",
    "resolve_font_weight",
    "create_qfont_from_token",
]
