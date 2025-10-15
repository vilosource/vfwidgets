"""Font Token Metadata Registry - Metadata System for Theme-Studio Font Editing.

This registry provides METADATA for font tokens (descriptions, defaults, validation)
for use by theme-studio's editing interface.

This is SEPARATE from vfwidgets_theme.core.font_tokens.FontTokenRegistry, which
provides RUNTIME RESOLUTION (hierarchical fallback chains) for widgets.

Two registries, two purposes:
- FontTokenMetadataRegistry (here): Editing metadata for theme-studio
- FontTokenRegistry (widget lib): Runtime resolution for widgets

Categories:
1. Base Fonts (7 tokens) - Fallback font families and default properties
2. Terminal (5 tokens) - Terminal-specific font configuration
3. Editor (4 tokens) - Code editor font configuration
4. Tabs (3 tokens) - Tab label font configuration
5. UI (3 tokens) - General UI element font configuration

Total: 22 tokens
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Union


class FontTokenCategory(Enum):
    """Font token categories for organization."""

    BASE_FONTS = "base_fonts"
    TERMINAL = "terminal"
    EDITOR = "editor"
    TABS = "tabs"
    UI = "ui"


@dataclass(frozen=True)
class FontTokenInfo:
    """Metadata about a single font token.

    Exactly mirrors ColorToken structure for consistency.
    Contains information needed for editing (descriptions, defaults, validation).
    """

    path: str  # Token path (e.g., "fonts.mono", "terminal.fontSize")
    category: FontTokenCategory
    description: str
    default_value: Union[list[str], int, float, None]  # None = falls back to parent
    value_type: type  # list, int, or float
    required: bool = False  # Most fonts have fallback resolution
    unit: str = ""  # "pt", "px", "" (dimensionless)
    min_value: Union[int, float, None] = None  # For numeric types
    max_value: Union[int, float, None] = None  # For numeric types


class FontTokenMetadataRegistry:
    """Registry of font token metadata for theme-studio editing.

    Provides metadata (descriptions, defaults, validation) for all font tokens.
    Exactly mirrors ColorTokenRegistry architecture.

    NOT to be confused with FontTokenRegistry in widget library, which provides
    runtime resolution with hierarchical fallbacks.
    """

    # Base Fonts Category (7 tokens)
    BASE_FONTS: list[FontTokenInfo] = [
        FontTokenInfo(
            path="fonts.mono",
            category=FontTokenCategory.BASE_FONTS,
            description="Monospace font family list (fallback chain for code/terminal)",
            default_value=["'Cascadia Code'", "Consolas", "'Courier New'", "monospace"],
            value_type=list,
            required=False,
        ),
        FontTokenInfo(
            path="fonts.ui",
            category=FontTokenCategory.BASE_FONTS,
            description="UI font family list (fallback chain for interface elements)",
            default_value=["'Segoe UI'", "Tahoma", "Geneva", "Verdana", "sans-serif"],
            value_type=list,
            required=False,
        ),
        FontTokenInfo(
            path="fonts.serif",
            category=FontTokenCategory.BASE_FONTS,
            description="Serif font family list (fallback chain for document text)",
            default_value=["Georgia", "'Times New Roman'", "Times", "serif"],
            value_type=list,
            required=False,
        ),
        FontTokenInfo(
            path="fonts.size",
            category=FontTokenCategory.BASE_FONTS,
            description="Default font size in points (base size for all widgets)",
            default_value=13,
            value_type=int,
            required=False,
            unit="pt",
            min_value=6,
            max_value=72,
        ),
        FontTokenInfo(
            path="fonts.weight",
            category=FontTokenCategory.BASE_FONTS,
            description="Default font weight (100-900, normal=400, bold=700)",
            default_value=400,
            value_type=int,
            required=False,
            min_value=100,
            max_value=900,
        ),
        FontTokenInfo(
            path="fonts.lineHeight",
            category=FontTokenCategory.BASE_FONTS,
            description="Default line height multiplier (1.0 = 100%, 1.5 = 150%)",
            default_value=1.5,
            value_type=float,
            required=False,
            min_value=0.5,
            max_value=3.0,
        ),
        FontTokenInfo(
            path="fonts.letterSpacing",
            category=FontTokenCategory.BASE_FONTS,
            description="Default letter spacing in pixels (negative = tighter)",
            default_value=0.0,
            value_type=float,
            required=False,
            unit="px",
            min_value=-5.0,
            max_value=5.0,
        ),
    ]

    # Terminal Category (5 tokens)
    TERMINAL_FONTS: list[FontTokenInfo] = [
        FontTokenInfo(
            path="terminal.fontFamily",
            category=FontTokenCategory.TERMINAL,
            description="Terminal font family list (overrides fonts.mono)",
            default_value=None,  # Falls back to fonts.mono
            value_type=list,
            required=False,
        ),
        FontTokenInfo(
            path="terminal.fontSize",
            category=FontTokenCategory.TERMINAL,
            description="Terminal font size in points (overrides fonts.size)",
            default_value=None,  # Falls back to fonts.size
            value_type=int,
            required=False,
            unit="pt",
            min_value=6,
            max_value=72,
        ),
        FontTokenInfo(
            path="terminal.fontWeight",
            category=FontTokenCategory.TERMINAL,
            description="Terminal font weight (overrides fonts.weight)",
            default_value=None,
            value_type=int,
            required=False,
            min_value=100,
            max_value=900,
        ),
        FontTokenInfo(
            path="terminal.lineHeight",
            category=FontTokenCategory.TERMINAL,
            description="Terminal line height multiplier (overrides fonts.lineHeight)",
            default_value=None,
            value_type=float,
            required=False,
            min_value=0.5,
            max_value=3.0,
        ),
        FontTokenInfo(
            path="terminal.letterSpacing",
            category=FontTokenCategory.TERMINAL,
            description="Terminal letter spacing in pixels (overrides fonts.letterSpacing)",
            default_value=None,
            value_type=float,
            required=False,
            unit="px",
            min_value=-5.0,
            max_value=5.0,
        ),
    ]

    # Editor Category (4 tokens)
    EDITOR_FONTS: list[FontTokenInfo] = [
        FontTokenInfo(
            path="editor.fontFamily",
            category=FontTokenCategory.EDITOR,
            description="Editor font family list (overrides fonts.mono)",
            default_value=None,
            value_type=list,
            required=False,
        ),
        FontTokenInfo(
            path="editor.fontSize",
            category=FontTokenCategory.EDITOR,
            description="Editor font size in points (overrides fonts.size)",
            default_value=None,
            value_type=int,
            required=False,
            unit="pt",
            min_value=6,
            max_value=72,
        ),
        FontTokenInfo(
            path="editor.fontWeight",
            category=FontTokenCategory.EDITOR,
            description="Editor font weight (overrides fonts.weight)",
            default_value=None,
            value_type=int,
            required=False,
            min_value=100,
            max_value=900,
        ),
        FontTokenInfo(
            path="editor.lineHeight",
            category=FontTokenCategory.EDITOR,
            description="Editor line height multiplier (overrides fonts.lineHeight)",
            default_value=None,
            value_type=float,
            required=False,
            min_value=0.5,
            max_value=3.0,
        ),
    ]

    # Tabs Category (3 tokens)
    TABS_FONTS: list[FontTokenInfo] = [
        FontTokenInfo(
            path="tabs.fontFamily",
            category=FontTokenCategory.TABS,
            description="Tab label font family list (overrides fonts.ui)",
            default_value=None,
            value_type=list,
            required=False,
        ),
        FontTokenInfo(
            path="tabs.fontSize",
            category=FontTokenCategory.TABS,
            description="Tab label font size in points (overrides fonts.size)",
            default_value=None,
            value_type=int,
            required=False,
            unit="pt",
            min_value=6,
            max_value=72,
        ),
        FontTokenInfo(
            path="tabs.fontWeight",
            category=FontTokenCategory.TABS,
            description="Tab label font weight (overrides fonts.weight)",
            default_value=None,
            value_type=int,
            required=False,
            min_value=100,
            max_value=900,
        ),
    ]

    # UI Category (3 tokens)
    UI_FONTS: list[FontTokenInfo] = [
        FontTokenInfo(
            path="ui.fontFamily",
            category=FontTokenCategory.UI,
            description="UI element font family list (overrides fonts.ui)",
            default_value=None,
            value_type=list,
            required=False,
        ),
        FontTokenInfo(
            path="ui.fontSize",
            category=FontTokenCategory.UI,
            description="UI element font size in points (overrides fonts.size)",
            default_value=None,
            value_type=int,
            required=False,
            unit="pt",
            min_value=6,
            max_value=72,
        ),
        FontTokenInfo(
            path="ui.fontWeight",
            category=FontTokenCategory.UI,
            description="UI element font weight (overrides fonts.weight)",
            default_value=None,
            value_type=int,
            required=False,
            min_value=100,
            max_value=900,
        ),
    ]

    # Combined list of all tokens
    _all_tokens: list[FontTokenInfo] = (
        BASE_FONTS + TERMINAL_FONTS + EDITOR_FONTS + TABS_FONTS + UI_FONTS
    )

    @classmethod
    def get_all_tokens(cls) -> list[FontTokenInfo]:
        """Get all registered font tokens.

        Returns:
            List of all FontTokenInfo objects (22 tokens)
        """
        return cls._all_tokens.copy()

    @classmethod
    def get_tokens_by_category(cls, category: FontTokenCategory) -> list[FontTokenInfo]:
        """Get all tokens in a specific category.

        Args:
            category: FontTokenCategory enum value

        Returns:
            List of FontTokenInfo objects in that category
        """
        return [t for t in cls._all_tokens if t.category == category]

    @classmethod
    def get_token(cls, path: str) -> FontTokenInfo | None:
        """Get token metadata by path.

        Args:
            path: Font token path (e.g., "terminal.fontSize")

        Returns:
            FontTokenInfo object or None if not found
        """
        for token in cls._all_tokens:
            if token.path == path:
                return token
        return None

    @classmethod
    def validate_value(cls, path: str, value) -> tuple[bool, str]:
        """Validate a font token value.

        Args:
            path: Font token path
            value: Value to validate

        Returns:
            Tuple of (is_valid, error_message)
            If valid, error_message is empty string.
        """
        token = cls.get_token(path)
        if not token:
            return False, f"Unknown token: {path}"

        # None is valid for non-required tokens (means "use fallback")
        if value is None:
            if token.required:
                return False, "This token is required and cannot be empty"
            return True, ""

        # Type check
        if not isinstance(value, token.value_type):
            return False, f"Expected {token.value_type.__name__}, got {type(value).__name__}"

        # Range validation for numeric types
        if token.value_type is int:
            if token.min_value is not None and value < token.min_value:
                return False, f"Value must be >= {token.min_value}"
            if token.max_value is not None and value > token.max_value:
                return False, f"Value must be <= {token.max_value}"

        elif token.value_type is float:
            if token.min_value is not None and value < token.min_value:
                return False, f"Value must be >= {token.min_value}"
            if token.max_value is not None and value > token.max_value:
                return False, f"Value must be <= {token.max_value}"

        elif token.value_type is list:
            if not value:  # Empty list
                return False, "Font family list cannot be empty"
            if not all(isinstance(f, str) for f in value):
                return False, "All font families must be strings"

        return True, ""

    @classmethod
    def get_display_name(cls, path: str) -> str:
        """Get human-readable display name for token.

        Converts "terminal.fontSize" → "Font Size"

        Args:
            path: Token path

        Returns:
            Human-readable name
        """
        # Get last segment
        name = path.split(".")[-1]

        # Convert camelCase to Title Case
        name = re.sub(r"([A-Z])", r" \1", name).title()

        return name


__all__ = [
    "FontTokenCategory",
    "FontTokenInfo",
    "FontTokenMetadataRegistry",
]
