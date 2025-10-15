"""Token value validator."""

import re
from typing import Optional

from PySide6.QtGui import QColor


class TokenValidator:
    """Validates token values for correctness.

    Validates:
    - Color hex formats (#RGB, #RRGGBB, #RRGGBBAA)
    - Color rgb/rgba formats
    - Color names (Qt color names)
    - Empty values (allowed - means use default)
    """

    # Hex color patterns
    HEX_3 = re.compile(r'^#[0-9A-Fa-f]{3}$')  # #RGB
    HEX_6 = re.compile(r'^#[0-9A-Fa-f]{6}$')  # #RRGGBB
    HEX_8 = re.compile(r'^#[0-9A-Fa-f]{8}$')  # #RRGGBBAA

    @classmethod
    def validate_color(cls, value: str) -> tuple[bool, Optional[str]]:
        """Validate a color token value.

        Args:
            value: Color value to validate

        Returns:
            Tuple of (is_valid, error_message)
            If valid: (True, None)
            If invalid: (False, "error message")
        """
        # Empty is valid (means use default)
        if not value or value.strip() == "":
            return (True, None)

        value = value.strip()

        # Try to parse as QColor (handles hex, rgb, rgba, color names)
        color = QColor(value)
        if color.isValid():
            return (True, None)

        # If not valid, provide helpful error message
        if value.startswith('#'):
            if len(value) not in [4, 7, 9]:  # #RGB, #RRGGBB, #RRGGBBAA
                return (False, f"Invalid hex color: '{value}'. Use #RGB, #RRGGBB, or #RRGGBBAA format.")
            return (False, f"Invalid hex color: '{value}'. Check that all characters are valid hex digits (0-9, A-F).")

        if value.startswith('rgb'):
            return (False, f"Invalid rgb color: '{value}'. Use format: rgb(r, g, b) or rgba(r, g, b, a).")

        return (False, f"Invalid color: '{value}'. Use hex (#RRGGBB), rgb(r,g,b), or color name.")

    @classmethod
    def validate_token(cls, token_name: str, value: str) -> tuple[bool, Optional[str]]:
        """Validate any token value based on token type.

        Args:
            token_name: Name of the token
            value: Value to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # For now, assume all tokens are colors
        # Future: Could check token registry for type
        return cls.validate_color(value)

    @classmethod
    def normalize_color(cls, value: str) -> str:
        """Normalize a color value to standard format.

        Args:
            value: Color value

        Returns:
            Normalized color value (#RRGGBB format)
        """
        if not value or value.strip() == "":
            return ""

        color = QColor(value)
        if color.isValid():
            return color.name()  # Returns #RRGGBB

        return value  # Return as-is if invalid
