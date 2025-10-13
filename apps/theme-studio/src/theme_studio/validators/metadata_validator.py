"""Validators for theme metadata fields."""

import re
from typing import Optional


class MetadataValidator:
    """Validator for theme metadata fields.

    Provides validation for theme name, version, and type fields
    with helpful error messages.
    """

    # Semantic version regex: 1.0.0, 2.1.5-beta, 3.2.1-alpha.1, etc.
    SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+(?:-[a-zA-Z0-9.\-]+)?$")

    # Valid theme types
    VALID_TYPES = ["dark", "light", "high-contrast"]

    @staticmethod
    def validate_name(value: str) -> tuple[bool, Optional[str]]:
        """Validate theme name.

        Args:
            value: Theme name to validate

        Returns:
            Tuple of (is_valid, error_message)
            - (True, None) if valid
            - (False, error_message) if invalid
        """
        # Check if empty or whitespace-only
        if not value or not value.strip():
            return (False, "Theme name cannot be empty")

        return (True, None)

    @staticmethod
    def validate_version(value: str) -> tuple[bool, Optional[str]]:
        """Validate theme version (semantic version format).

        Args:
            value: Version string to validate

        Returns:
            Tuple of (is_valid, error_message)
            - (True, None) if valid
            - (False, error_message) if invalid

        Valid examples:
            - "1.0.0"
            - "2.1.5"
            - "1.0.0-beta"
            - "3.2.1-alpha.1"

        Invalid examples:
            - "1.0" (missing patch version)
            - "v1.0.0" (no prefix allowed)
            - "1.0.0.0" (too many version parts)
            - "abc" (not numeric)
        """
        if not value or not value.strip():
            return (False, "Version cannot be empty")

        # Check against semantic version regex
        if not MetadataValidator.SEMVER_PATTERN.match(value):
            return (False, "Must be semantic version (e.g., 1.0.0, 2.1.5-beta)")

        return (True, None)

    @staticmethod
    def validate_type(value: str) -> tuple[bool, Optional[str]]:
        """Validate theme type.

        Args:
            value: Theme type to validate

        Returns:
            Tuple of (is_valid, error_message)
            - (True, None) if valid
            - (False, error_message) if invalid

        Valid values:
            - "dark"
            - "light"
            - "high-contrast"
        """
        if value not in MetadataValidator.VALID_TYPES:
            return (
                False,
                f"Type must be one of: {', '.join(MetadataValidator.VALID_TYPES)}",
            )

        return (True, None)

    @staticmethod
    def validate_author(value: str) -> tuple[bool, Optional[str]]:
        """Validate author field (always valid, optional).

        Args:
            value: Author name to validate

        Returns:
            Always (True, None) - author field accepts any string
        """
        return (True, None)

    @staticmethod
    def validate_description(value: str) -> tuple[bool, Optional[str]]:
        """Validate description field (always valid, optional).

        Args:
            value: Description text to validate

        Returns:
            Always (True, None) - description field accepts any string
        """
        return (True, None)
