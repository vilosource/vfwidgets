"""Core theme data model.

This module defines the immutable, validated theme data structures that represent
themes in the VFWidgets theme system. All themes are immutable once created to
ensure thread safety and prevent accidental modification.

Key Classes:
- Theme: Immutable theme data model with validation
- ThemeBuilder: Copy-on-write theme construction
- ThemeValidator: JSON schema validation
- ThemeComposer: Intelligent theme merging
- PropertyResolver: Fast property lookup with caching
- TokenColors: Syntax highlighting token support

Design Principles:
- Immutability: Themes cannot be modified after creation
- Validation: All theme data is validated on creation
- Type Safety: Complete type annotations and runtime validation
- Performance: Optimized for fast access and minimal memory usage
- Copy-on-Write: Efficient theme modifications through builder pattern
- Caching: Sub-microsecond property access through intelligent caching

Implemented in Task 7.
"""

import json
import re
import threading
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

from ..errors import InvalidThemeFormatError, PropertyNotFoundError, ThemeLoadError
from ..logging import get_debug_logger

# Import foundation modules
from ..protocols import ColorValue, PropertyKey, PropertyValue

# Type aliases for clarity
ColorPalette = Dict[str, ColorValue]
StyleProperties = Dict[str, Any]
ThemeMetadata = Dict[str, Any]
TokenColors = List[Dict[str, Any]]

# Color validation patterns
HEX_COLOR_PATTERN = re.compile(r'^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{6}|[A-Fa-f0-9]{8})$')
RGB_COLOR_PATTERN = re.compile(r'^rgb\(\s*([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])\s*,\s*([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])\s*,\s*([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])\s*\)$')
RGBA_COLOR_PATTERN = re.compile(r'^rgba\(\s*([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])\s*,\s*([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])\s*,\s*([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])\s*,\s*(0|1|0\.[0-9]+)\s*\)$')
HSL_COLOR_PATTERN = re.compile(r'^hsl\(\s*(\d+)\s*,\s*(\d+)%\s*,\s*(\d+)%\s*\)$')
VERSION_PATTERN = re.compile(r'^\d+\.\d+\.\d+(?:-[a-zA-Z0-9]+)?$')

# Named colors (subset of CSS named colors)
NAMED_COLORS = {
    'black', 'white', 'red', 'green', 'blue', 'yellow', 'cyan', 'magenta',
    'gray', 'grey', 'darkred', 'darkgreen', 'darkblue', 'darkgray', 'darkgrey',
    'lightgray', 'lightgrey', 'transparent'
}

logger = get_debug_logger(__name__)


@dataclass(frozen=True)
class Theme:
    """Immutable theme data model.

    Represents a complete theme with colors, styles, and metadata.
    All validation occurs during creation, and the theme cannot be
    modified afterward to ensure thread safety.

    Features:
    - Immutable dataclass with frozen=True for thread safety
    - Comprehensive validation on creation
    - Fast property access with intelligent fallbacks
    - JSON serialization/deserialization support
    - Hash-based equality for performance
    - VSCode theme format compatibility
    """

    name: str
    version: str = "1.0.0"
    colors: ColorPalette = field(default_factory=dict)
    styles: StyleProperties = field(default_factory=dict)
    metadata: ThemeMetadata = field(default_factory=dict)
    token_colors: TokenColors = field(default_factory=list)
    type: str = "light"  # light, dark, or high-contrast

    # Cached hash for performance
    _hash: Optional[int] = field(default=None, init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        """Validate theme data after creation."""
        logger.debug(f"Creating theme: {self.name}")

        # Validate name
        if not self.name or not isinstance(self.name, str) or not self.name.strip():
            raise InvalidThemeFormatError("Theme name must be a non-empty string")

        # Validate version
        if not VERSION_PATTERN.match(self.version):
            raise InvalidThemeFormatError(
                f"Invalid version format: {self.version}. Must be semantic version (e.g., '1.0.0')"
            )

        # Validate colors
        for key, color in self.colors.items():
            if not self._is_valid_color(color):
                raise InvalidThemeFormatError(f"Invalid color format for '{key}': {color}")

        # Validate theme type
        if self.type not in ("light", "dark", "high-contrast"):
            raise InvalidThemeFormatError(f"Invalid theme type: {self.type}. Must be 'light', 'dark', or 'high-contrast'")

        # Validate token colors structure
        for token in self.token_colors:
            if not isinstance(token, dict) or "scope" not in token or "settings" not in token:
                raise InvalidThemeFormatError("Invalid token color format. Must have 'scope' and 'settings' keys")

        # Cache hash for performance
        object.__setattr__(self, '_hash', self._compute_hash())

        logger.debug(f"Successfully created theme: {self.name} v{self.version}")

    def _is_valid_color(self, color: str) -> bool:
        """Validate color format."""
        if not isinstance(color, str):
            return False

        color = color.strip().lower()

        # Check various color formats
        return (
            HEX_COLOR_PATTERN.match(color) or
            RGB_COLOR_PATTERN.match(color) or
            RGBA_COLOR_PATTERN.match(color) or
            HSL_COLOR_PATTERN.match(color) or
            color in NAMED_COLORS or
            color.startswith('@')  # Allow references
        )

    def _compute_hash(self) -> int:
        """Compute consistent hash for the theme."""
        # Create deterministic hash from theme content
        content = {
            'name': self.name,
            'version': self.version,
            'colors': sorted(self.colors.items()),
            'styles': sorted(self.styles.items()),
            'metadata': sorted(self.metadata.items()),
            'type': self.type
        }
        content_str = json.dumps(content, sort_keys=True)
        return hash(content_str)

    def __hash__(self) -> int:
        """Return cached hash."""
        return self._hash or 0

    def get_color(self, key: str, fallback: Optional[ColorValue] = None) -> ColorValue:
        """Get color value with fallback support."""
        if key in self.colors:
            return self.colors[key]

        if fallback is not None:
            return fallback

        # Try common fallback patterns
        if key.startswith('editor.'):
            base_key = key.replace('editor.', '')
            if base_key in self.colors:
                return self.colors[base_key]

        raise PropertyNotFoundError(f"Color '{key}' not found in theme '{self.name}'")

    def get_property(self, key: PropertyKey, fallback: Optional[PropertyValue] = None) -> PropertyValue:
        """Get theme property with fallback support."""
        # Check colors first
        if key in self.colors:
            return self.colors[key]

        # Check styles
        if key in self.styles:
            return self.styles[key]

        # Check metadata
        if key in self.metadata:
            return self.metadata[key]

        if fallback is not None:
            return fallback

        raise PropertyNotFoundError(f"Property '{key}' not found in theme '{self.name}'")

    def to_dict(self) -> Dict[str, Any]:
        """Convert theme to dictionary for serialization."""
        return {
            'name': self.name,
            'version': self.version,
            'type': self.type,
            'colors': dict(self.colors),
            'styles': dict(self.styles),
            'metadata': dict(self.metadata),
            'tokenColors': self.token_colors
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Theme':
        """Create theme from dictionary."""
        return cls(
            name=data.get('name', 'unnamed'),
            version=data.get('version', '1.0.0'),
            type=data.get('type', 'light'),
            colors=data.get('colors', {}),
            styles=data.get('styles', {}),
            metadata=data.get('metadata', {}),
            token_colors=data.get('tokenColors', [])
        )

    def get_size_estimate(self) -> int:
        """Estimate memory size of theme in bytes."""
        import sys
        return (
            sys.getsizeof(self) +
            sys.getsizeof(self.colors) + sum(sys.getsizeof(k) + sys.getsizeof(v) for k, v in self.colors.items()) +
            sys.getsizeof(self.styles) + sum(sys.getsizeof(k) + sys.getsizeof(v) for k, v in self.styles.items()) +
            sys.getsizeof(self.metadata) + sum(sys.getsizeof(k) + sys.getsizeof(v) for k, v in self.metadata.items()) +
            sys.getsizeof(self.token_colors)
        )


class ThemeBuilder:
    """Copy-on-write theme builder for efficient theme modification.

    Allows modification of themes without mutating the original,
    supporting rollback and validation during construction.

    Features:
    - Copy-on-write efficiency
    - Validation during build process
    - Rollback support with checkpoints
    - Fluent API for theme construction
    """

    def __init__(self, name: str):
        """Initialize builder with theme name."""
        self.name = name
        self.version = "1.0.0"
        self.type = "light"
        self.colors: Dict[str, str] = {}
        self.styles: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}
        self.token_colors: List[Dict[str, Any]] = []

        # Checkpoint support
        self._checkpoints: List[Dict[str, Any]] = []

        # Parent tracking for inheritance
        self._parent: Optional[Theme] = None

        logger.debug(f"Created ThemeBuilder for: {name}")

    @classmethod
    def from_theme(cls, theme: Theme) -> 'ThemeBuilder':
        """Create builder from existing theme."""
        builder = cls(theme.name)
        builder.version = theme.version
        builder.type = theme.type
        builder.colors = dict(theme.colors)
        builder.styles = dict(theme.styles)
        builder.metadata = dict(theme.metadata)
        builder.token_colors = list(theme.token_colors)
        return builder

    def set_name(self, name: str) -> 'ThemeBuilder':
        """Set theme name."""
        self.name = name
        return self

    def set_version(self, version: str) -> 'ThemeBuilder':
        """Set theme version."""
        self.version = version
        return self

    def set_type(self, theme_type: str) -> 'ThemeBuilder':
        """Set theme type."""
        self.type = theme_type
        return self

    def add_color(self, key: str, value: str) -> 'ThemeBuilder':
        """Add or update color."""
        self.colors[key] = value
        return self

    def add_colors(self, colors: Dict[str, str]) -> 'ThemeBuilder':
        """Add multiple colors."""
        self.colors.update(colors)
        return self

    def remove_color(self, key: str) -> 'ThemeBuilder':
        """Remove color."""
        self.colors.pop(key, None)
        return self

    def add_style(self, key: str, value: Any) -> 'ThemeBuilder':
        """Add or update style."""
        self.styles[key] = value
        return self

    def add_styles(self, styles: Dict[str, Any]) -> 'ThemeBuilder':
        """Add multiple styles."""
        self.styles.update(styles)
        return self

    def remove_style(self, key: str) -> 'ThemeBuilder':
        """Remove style."""
        self.styles.pop(key, None)
        return self

    def set_metadata(self, metadata: Dict[str, Any]) -> 'ThemeBuilder':
        """Set theme metadata."""
        self.metadata = dict(metadata)
        return self

    def add_metadata(self, key: str, value: Any) -> 'ThemeBuilder':
        """Add metadata field."""
        self.metadata[key] = value
        return self

    def add_token_color(self, scope: str, settings: Dict[str, str], name: Optional[str] = None) -> 'ThemeBuilder':
        """Add token color for syntax highlighting."""
        token = {'scope': scope, 'settings': settings}
        if name:
            token['name'] = name
        self.token_colors.append(token)
        return self

    def extend(self, parent_theme: Union[str, Theme]) -> 'ThemeBuilder':
        """Inherit from parent theme.

        Copies all colors, styles, and metadata from parent theme.
        Child theme can override specific properties by setting them
        before or after calling extend().

        Args:
            parent_theme: Parent theme name (str) or Theme instance

        Returns:
            Self for method chaining

        Raises:
            ThemeLoadError: If parent theme name not found

        Example:
            >>> custom = (ThemeBuilder("my-variant")
            ...     .extend("dark")
            ...     .add_color("button.background", "#ff0000")
            ...     .build())

        """
        # Resolve parent theme
        if isinstance(parent_theme, str):
            # Import here to avoid circular dependency
            from .repository import BuiltinThemeManager
            mgr = BuiltinThemeManager()
            parent = mgr.get_theme(parent_theme)
            if not parent:
                raise ThemeLoadError(f"Parent theme '{parent_theme}' not found")
        else:
            parent = parent_theme

        # Copy parent properties (child values take precedence)
        self.type = parent.type
        self.version = parent.version

        # Copy parent colors (don't override existing)
        for key, value in parent.colors.items():
            if key not in self.colors:
                self.colors[key] = value

        # Copy parent styles (don't override existing)
        for key, value in parent.styles.items():
            if key not in self.styles:
                self.styles[key] = value

        # Copy parent metadata (don't override existing)
        if parent.metadata:
            for key, value in parent.metadata.items():
                if key not in self.metadata:
                    self.metadata[key] = value

        # Copy parent token colors (append to existing)
        if parent.token_colors:
            self.token_colors.extend(parent.token_colors)

        # Track parent reference
        self._parent = parent

        logger.info(f"Theme '{self.name}' extends '{parent.name}'")
        return self

    def get_parent(self) -> Optional[Theme]:
        """Get parent theme if this theme was created via extend().

        Returns:
            Parent Theme instance, or None if no parent

        """
        return self._parent

    def checkpoint(self) -> 'ThemeBuilder':
        """Create checkpoint for rollback."""
        checkpoint = {
            'name': self.name,
            'version': self.version,
            'type': self.type,
            'colors': dict(self.colors),
            'styles': dict(self.styles),
            'metadata': dict(self.metadata),
            'token_colors': list(self.token_colors)
        }
        self._checkpoints.append(checkpoint)
        return self

    def rollback(self) -> 'ThemeBuilder':
        """Rollback to last checkpoint."""
        if not self._checkpoints:
            logger.warning("No checkpoint to rollback to")
            return self

        checkpoint = self._checkpoints.pop()
        self.name = checkpoint['name']
        self.version = checkpoint['version']
        self.type = checkpoint['type']
        self.colors = checkpoint['colors']
        self.styles = checkpoint['styles']
        self.metadata = checkpoint['metadata']
        self.token_colors = checkpoint['token_colors']

        logger.debug("Rolled back to checkpoint")
        return self

    def build(self) -> Theme:
        """Build immutable theme with validation."""
        try:
            # Add parent reference to metadata if exists
            metadata = dict(self.metadata)
            if self._parent is not None:
                metadata['parent_theme'] = self._parent.name

            theme = Theme(
                name=self.name,
                version=self.version,
                type=self.type,
                colors=dict(self.colors),
                styles=dict(self.styles),
                metadata=metadata,
                token_colors=list(self.token_colors)
            )
            logger.debug(f"Built theme: {theme.name}")
            return theme
        except Exception as e:
            logger.error(f"Failed to build theme '{self.name}': {e}")
            raise


@dataclass
class ValidationResult:
    """Result of theme validation."""

    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


class ThemeValidator:
    """JSON schema validator for theme data.

    Provides comprehensive validation of theme data structures,
    including VSCode theme format compatibility.

    Features:
    - JSON schema validation
    - Color format validation
    - VSCode theme compatibility
    - Detailed error reporting
    - Suggestions for common mistakes
    """

    def __init__(self):
        """Initialize validator."""
        self._errors: List[Dict[str, str]] = []
        self._suggestions: List[str] = []

        # Common property suggestions
        self._property_suggestions = {
            'colours': 'colors',
            'colour': 'color',
            'theme_type': 'type',
            'themetype': 'type',
            'fontfamily': 'font-family',
            'fontsize': 'font-size',
            'backgroundcolor': 'background-color',
            'foregroundcolor': 'foreground-color'
        }

    def validate(self, theme_data: Dict[str, Any]) -> bool:
        """Validate theme data structure."""
        self._errors.clear()
        self._suggestions.clear()

        try:
            # Basic structure validation
            if not self._validate_basic_structure(theme_data):
                return False

            # Validate name
            if not self._validate_name(theme_data.get('name')):
                return False

            # Validate version
            if not self._validate_version(theme_data.get('version', '1.0.0')):
                return False

            # Validate colors
            if not self._validate_colors(theme_data.get('colors', {})):
                return False

            # Validate styles
            if not self._validate_styles(theme_data.get('styles', {})):
                return False

            # Validate token colors if present
            if 'tokenColors' in theme_data:
                if not self._validate_token_colors(theme_data['tokenColors']):
                    return False

            return True

        except Exception as e:
            self._errors.append({
                'field': 'validation',
                'message': f'Validation error: {str(e)}'
            })
            return False

    def _validate_basic_structure(self, data: Dict[str, Any]) -> bool:
        """Validate basic theme structure."""
        if not isinstance(data, dict):
            self._errors.append({
                'field': 'structure',
                'message': 'Theme data must be a dictionary'
            })
            return False

        # Check for common typos
        for key in data.keys():
            if key in self._property_suggestions:
                suggestion = self._property_suggestions[key]
                self._suggestions.append(f"Did you mean '{suggestion}' instead of '{key}'?")

        return True

    def _validate_name(self, name: Any) -> bool:
        """Validate theme name."""
        if not name:
            self._errors.append({
                'field': 'name',
                'message': 'Theme name is required'
            })
            return False

        if not isinstance(name, str):
            self._errors.append({
                'field': 'name',
                'message': 'Theme name must be a string'
            })
            return False

        if not name.strip():
            self._errors.append({
                'field': 'name',
                'message': 'Theme name cannot be empty'
            })
            return False

        return True

    def _validate_version(self, version: str) -> bool:
        """Validate version format."""
        if not VERSION_PATTERN.match(version):
            self._errors.append({
                'field': 'version',
                'message': f'Invalid version format: {version}. Must be semantic version (e.g., "1.0.0")'
            })
            return False
        return True

    def _validate_colors(self, colors: Dict[str, Any]) -> bool:
        """Validate color palette."""
        if not isinstance(colors, dict):
            self._errors.append({
                'field': 'colors',
                'message': 'Colors must be a dictionary'
            })
            return False

        for key, value in colors.items():
            if not isinstance(key, str):
                self._errors.append({
                    'field': f'colors.{key}',
                    'message': 'Color keys must be strings'
                })
                return False

            if not self._is_valid_color(value):
                self._errors.append({
                    'field': f'colors.{key}',
                    'message': f'Invalid color format: {value}'
                })
                return False

        return True

    def _validate_styles(self, styles: Dict[str, Any]) -> bool:
        """Validate style properties."""
        if not isinstance(styles, dict):
            self._errors.append({
                'field': 'styles',
                'message': 'Styles must be a dictionary'
            })
            return False

        for key, value in styles.items():
            if not isinstance(key, str):
                self._errors.append({
                    'field': f'styles.{key}',
                    'message': 'Style keys must be strings'
                })
                return False

        return True

    def _validate_token_colors(self, token_colors: List[Any]) -> bool:
        """Validate token colors for syntax highlighting."""
        if not isinstance(token_colors, list):
            self._errors.append({
                'field': 'tokenColors',
                'message': 'Token colors must be a list'
            })
            return False

        for i, token in enumerate(token_colors):
            if not isinstance(token, dict):
                self._errors.append({
                    'field': f'tokenColors[{i}]',
                    'message': 'Token color must be a dictionary'
                })
                return False

            if 'scope' not in token:
                self._errors.append({
                    'field': f'tokenColors[{i}]',
                    'message': 'Token color must have "scope" field'
                })
                return False

            if 'settings' not in token:
                self._errors.append({
                    'field': f'tokenColors[{i}]',
                    'message': 'Token color must have "settings" field'
                })
                return False

        return True

    def _is_valid_color(self, color: Any) -> bool:
        """Check if color format is valid."""
        if not isinstance(color, str):
            return False

        color = color.strip().lower()

        return (
            HEX_COLOR_PATTERN.match(color) or
            RGB_COLOR_PATTERN.match(color) or
            RGBA_COLOR_PATTERN.match(color) or
            HSL_COLOR_PATTERN.match(color) or
            color in NAMED_COLORS or
            color.startswith('@')  # Allow references
        )

    def get_errors(self) -> List[Dict[str, str]]:
        """Get validation errors."""
        return list(self._errors)

    def get_suggestions(self) -> List[str]:
        """Get suggestions for common mistakes."""
        return list(self._suggestions)

    def validate_semantic(self, theme: 'Theme') -> List[str]:
        """Check semantic consistency of theme.

        Validates:
        - Name vs type consistency (dark theme should have type='dark')
        - Presence of common required tokens
        - Detection of legacy simple-key format
        - Proper namespaced key usage

        Args:
            theme: Theme to validate

        Returns:
            List of semantic validation issues (empty if valid)

        """
        issues = []

        # Check name vs type consistency
        if theme.name == "dark" and theme.type != "dark":
            issues.append(
                f"Theme named 'dark' should have type='dark', got type='{theme.type}'"
            )

        if theme.name == "light" and theme.type != "light":
            issues.append(
                f"Theme named 'light' should have type='light', got type='{theme.type}'"
            )

        # Check for missing common tokens (using namespaced keys)
        common_tokens = [
            'colors.background',
            'colors.foreground',
            'colors.primary'
        ]
        for token in common_tokens:
            if token not in theme.colors:
                issues.append(f"Missing common token: {token}")

        # Check for old simple-key format (legacy detection)
        simple_keys = ['background', 'foreground', 'primary', 'secondary', 'border']
        found_simple = [k for k in simple_keys if k in theme.colors]
        if found_simple:
            issues.append(
                f"Found legacy simple keys: {found_simple}. "
                f"Use namespaced keys like 'colors.background' instead."
            )

        return issues

    def suggest_correction(self, wrong_key: str) -> Optional[str]:
        """Suggest correct token name for typo.

        Uses fuzzy matching to find the closest valid token name
        from ColorTokenRegistry.

        Args:
            wrong_key: Potentially misspelled key

        Returns:
            Suggested correct key, or None if no good match

        """
        try:
            from difflib import get_close_matches

            from ..core.tokens import ColorTokenRegistry

            all_tokens = [t.name for t in ColorTokenRegistry.ALL_TOKENS]
            matches = get_close_matches(wrong_key, all_tokens, n=1, cutoff=0.6)
            return matches[0] if matches else None
        except ImportError:
            return None

    def validate_theme_data(self, data: Dict[str, Any]) -> 'ValidationResult':
        """Validate theme data and return comprehensive results.

        Args:
            data: Theme data dictionary to validate

        Returns:
            ValidationResult with errors, warnings, and suggestions

        """
        is_valid = self.validate(data)
        errors = self.get_errors()
        suggestions = self.get_suggestions()

        return ValidationResult(
            is_valid=is_valid,
            errors=[e['message'] for e in errors],
            warnings=[],
            suggestions=suggestions
        )

    def validate_accessibility(self, theme: Theme) -> ValidationResult:
        """Validate theme accessibility (WCAG compliance).

        Checks:
        - Contrast ratios between text and backgrounds
        - Minimum contrast requirements (4.5:1 for normal text, 3:1 for large text)
        - Focus indicator visibility
        - State color contrast (error, warning, success)

        Args:
            theme: Theme to validate

        Returns:
            ValidationResult with warnings and suggestions

        Example:
            >>> validator = ThemeValidator()
            >>> result = validator.validate_accessibility(theme)
            >>> if not result.is_valid:
            ...     for warning in result.warnings:
            ...         print(warning)

        """
        errors = []
        warnings = []
        suggestions = []

        # Check text/background contrast ratios
        bg = theme.colors.get('colors.background')
        fg = theme.colors.get('colors.foreground')

        if bg and fg:
            ratio = self._calculate_contrast_ratio(bg, fg)

            if ratio < 3.0:
                errors.append(
                    f"Critical: Text contrast ratio {ratio:.2f}:1 is below WCAG minimum (3:1). "
                    f"Text may be unreadable."
                )
                suggestions.append(
                    f"Increase contrast between foreground ({fg}) and background ({bg})"
                )
            elif ratio < 4.5:
                warnings.append(
                    f"Warning: Text contrast ratio {ratio:.2f}:1 is below WCAG AA (4.5:1). "
                    f"May not meet accessibility standards."
                )
                suggestions.append(
                    "Aim for 4.5:1 contrast ratio for normal text, 3:1 for large text"
                )

        # Check button contrast
        btn_bg = theme.colors.get('button.background')
        btn_fg = theme.colors.get('button.foreground')

        if btn_bg and btn_fg:
            btn_ratio = self._calculate_contrast_ratio(btn_bg, btn_fg)

            if btn_ratio < 3.0:
                warnings.append(
                    f"Button contrast ratio {btn_ratio:.2f}:1 is below minimum (3:1)"
                )
                suggestions.append(
                    f"Increase contrast between button foreground ({btn_fg}) and background ({btn_bg})"
                )

        # Check focus indicator contrast
        focus_border = theme.colors.get('colors.focusBorder') or theme.colors.get('colors.focus')
        if bg and focus_border:
            focus_ratio = self._calculate_contrast_ratio(focus_border, bg)

            if focus_ratio < 3.0:
                warnings.append(
                    f"Focus indicator contrast {focus_ratio:.2f}:1 is below minimum (3:1). "
                    f"Focus may not be visible."
                )
                suggestions.append(
                    "Increase contrast for focus border against background"
                )

        # Check error/warning/success color contrast
        for state in ['error', 'warning', 'success']:
            state_color = theme.colors.get(f'colors.{state}')
            if bg and state_color:
                state_ratio = self._calculate_contrast_ratio(state_color, bg)
                if state_ratio < 3.0:
                    warnings.append(
                        f"{state.capitalize()} color contrast {state_ratio:.2f}:1 is below minimum (3:1)"
                    )
                    suggestions.append(
                        f"Increase contrast for {state} color against background"
                    )

        is_valid = len(errors) == 0

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )

    def _calculate_contrast_ratio(self, color1: str, color2: str) -> float:
        """Calculate WCAG contrast ratio between two colors.

        Args:
            color1: First color (hex format)
            color2: Second color (hex format)

        Returns:
            Contrast ratio (1.0 to 21.0)

        Reference:
            https://www.w3.org/TR/WCAG21/#contrast-minimum

        """
        l1 = self._get_relative_luminance(color1)
        l2 = self._get_relative_luminance(color2)

        # Ensure l1 is lighter
        if l2 > l1:
            l1, l2 = l2, l1

        # Calculate contrast ratio: (L1 + 0.05) / (L2 + 0.05)
        ratio = (l1 + 0.05) / (l2 + 0.05)

        return ratio

    def _get_relative_luminance(self, color: str) -> float:
        """Calculate relative luminance of a color.

        Args:
            color: Hex color string (e.g., "#ff0000")

        Returns:
            Relative luminance (0.0 to 1.0)

        Reference:
            https://www.w3.org/TR/WCAG21/#dfn-relative-luminance

        """
        # Parse hex color
        if not color or not isinstance(color, str):
            return 0.5  # Default for invalid colors

        color = color.strip()
        if not color.startswith('#'):
            return 0.5  # Default for invalid colors

        hex_color = color.lstrip('#')

        if len(hex_color) == 3:
            # Expand shorthand: #abc -> #aabbcc
            hex_color = ''.join(c*2 for c in hex_color)

        if len(hex_color) not in (6, 8):  # Allow 8 for rgba
            return 0.5  # Default for invalid colors

        try:
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
        except (ValueError, IndexError):
            return 0.5

        # Apply gamma correction
        def gamma_correct(c):
            if c <= 0.03928:
                return c / 12.92
            else:
                return ((c + 0.055) / 1.055) ** 2.4

        r = gamma_correct(r)
        g = gamma_correct(g)
        b = gamma_correct(b)

        # Calculate luminance
        luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b

        return luminance

    def get_available_properties(self, prefix: str) -> List[str]:
        """Get list of available properties with given prefix.

        Args:
            prefix: Property prefix (e.g., "button", "colors", "editor")

        Returns:
            List of matching property names

        Example:
            >>> validator.get_available_properties("button")
            ['button.background', 'button.foreground', 'button.hoverBackground', ...]

        """
        try:
            from ..core.tokens import ColorTokenRegistry

            all_tokens = [t.name for t in ColorTokenRegistry.ALL_TOKENS]

            if prefix:
                matching = [t for t in all_tokens if t.startswith(prefix + '.')]
            else:
                matching = all_tokens

            return sorted(matching)
        except (ImportError, AttributeError):
            # Fallback if ColorTokenRegistry not available
            return []

    def format_error(self, property_name: str, error_type: str = "not_found") -> str:
        """Format enhanced error message with suggestions and docs link.

        Args:
            property_name: Property that caused the error
            error_type: Type of error ("not_found", "invalid_value", etc.)

        Returns:
            Formatted error message with context

        Example:
            >>> validator.format_error("button.backgroud")
            Property 'button.backgroud' not found
              Did you mean: 'button.background'?
              Available button properties:
                - button.background
                - button.foreground
                - button.hoverBackground
              See: https://vfwidgets.readthedocs.io/themes/tokens#button

        """
        lines = []

        if error_type == "not_found":
            lines.append(f"Property '{property_name}' not found")

            # Suggest correction
            correction = self.suggest_correction(property_name)
            if correction:
                lines.append(f"  Did you mean: '{correction}'?")

            # List available properties in same category
            if '.' in property_name:
                prefix = property_name.split('.')[0]
                available = self.get_available_properties(prefix)

                if available:
                    lines.append(f"  Available {prefix} properties:")
                    for prop in available[:10]:  # Limit to 10
                        lines.append(f"    - {prop}")

                    if len(available) > 10:
                        lines.append(f"    ... and {len(available) - 10} more")

            # Add documentation link
            if '.' in property_name:
                category = property_name.split('.')[0]
                lines.append(f"  See: https://vfwidgets.readthedocs.io/themes/tokens#{category}")

        elif error_type == "invalid_value":
            lines.append(f"Invalid value for property '{property_name}'")
            lines.append("  See: https://vfwidgets.readthedocs.io/themes/tokens")

        return '\n'.join(lines)


class ThemeComposer:
    """Intelligent theme merging and composition.

    Handles theme inheritance, overrides, and composition
    with conflict resolution strategies.

    Features:
    - Theme inheritance chains
    - Conflict resolution strategies
    - Performance-optimized merging
    - Deep property merging
    """

    def __init__(self):
        """Initialize composer."""
        self._composition_cache: Dict[str, Theme] = {}
        self._cache_lock = threading.RLock()

    def compose(self, *themes: Theme, name: Optional[str] = None) -> Theme:
        """Merge multiple themes with priority.

        Later themes override properties from earlier themes.
        Preserves theme type from first theme unless overridden.

        Args:
            *themes: Themes to merge (2 or more required)
            name: Name for composed theme (default: auto-generated)

        Returns:
            New composed theme

        Raises:
            ValueError: If less than 2 themes provided

        Example:
            >>> base = get_theme("vscode")
            >>> buttons = get_theme("custom-buttons")
            >>> inputs = get_theme("custom-inputs")
            >>> app_theme = composer.compose(base, buttons, inputs)

        """
        if len(themes) < 2:
            raise ValueError("compose() requires at least 2 themes")

        # Generate name if not provided
        if name is None:
            theme_names = [t.name for t in themes]
            name = f"composed_{'_'.join(theme_names)}"

        # Check cache
        cache_key = f"{name}_{'_'.join(str(t._hash) for t in themes)}"
        with self._cache_lock:
            if cache_key in self._composition_cache:
                logger.debug(f"Returning cached composition: {cache_key}")
                return self._composition_cache[cache_key]

        # Start with first theme as base
        base_theme = themes[0]
        builder = ThemeBuilder(name)
        builder.set_type(base_theme.type)
        builder.set_version(base_theme.version)

        # Merge themes in order (later overrides earlier)
        for theme in themes:
            # Merge colors
            for key, value in theme.colors.items():
                builder.add_color(key, value)  # Later values override

            # Merge styles
            for key, value in theme.styles.items():
                builder.add_style(key, value)

            # Merge metadata
            if theme.metadata:
                for key, value in theme.metadata.items():
                    builder.add_metadata(key, value)

            # Merge token colors (append all)
            if theme.token_colors:
                for token in theme.token_colors:
                    builder.token_colors.append(token)

        # Add composition metadata
        builder.add_metadata("composed_from", [t.name for t in themes])
        builder.add_metadata("composition_order", [t.name for t in themes])

        # Build composed theme
        composed = builder.build()

        # Cache result
        with self._cache_lock:
            self._composition_cache[cache_key] = composed

        logger.info(f"Composed theme '{name}' from: {[t.name for t in themes]}")
        return composed

    def compose_partial(self, base: Theme, overrides: Dict[str, str], name: Optional[str] = None) -> Theme:
        """Create variant by applying partial overrides to base theme.

        Convenient for small customizations without creating full theme.

        Args:
            base: Base theme to start from
            overrides: Dict of properties to override
            name: Name for variant (default: base.name + "_variant")

        Returns:
            New theme with overrides applied

        Example:
            >>> dark = get_theme("dark")
            >>> variant = composer.compose_partial(dark, {
            ...     "button.background": "#ff0000",
            ...     "button.hoverBackground": "#cc0000"
            ... })

        """
        if name is None:
            name = f"{base.name}_variant"

        builder = ThemeBuilder(name)
        builder.set_type(base.type)
        builder.set_version(base.version)

        # Copy base colors
        for key, value in base.colors.items():
            builder.add_color(key, value)

        # Copy base styles
        for key, value in base.styles.items():
            builder.add_style(key, value)

        # Copy base metadata
        if base.metadata:
            for key, value in base.metadata.items():
                builder.add_metadata(key, value)

        # Copy base token colors
        if base.token_colors:
            for token in base.token_colors:
                builder.token_colors.append(token)

        # Apply overrides
        for key, value in overrides.items():
            builder.add_color(key, value)

        # Add metadata about partial composition
        builder.add_metadata("base_theme", base.name)
        builder.add_metadata("overrides", list(overrides.keys()))

        return builder.build()

    def compose_chain(self, themes: List[Theme]) -> Theme:
        """Compose a chain of themes with later themes overriding earlier ones."""
        if not themes:
            raise ValueError("Cannot compose empty theme chain")

        if len(themes) == 1:
            return themes[0]

        result = themes[0]
        for theme in themes[1:]:
            result = self.compose(result, theme)

        return result

    def compose_with_strategy(self, themes: List[Theme], strategy: str = "last_wins") -> Theme:
        """Compose themes with specific conflict resolution strategy."""
        if strategy == "priority":
            return self._compose_by_priority(themes)
        elif strategy == "last_wins":
            return self.compose_chain(themes)
        else:
            raise ValueError(f"Unknown composition strategy: {strategy}")

    def _compose_by_priority(self, themes: List[Theme]) -> Theme:
        """Compose themes by priority metadata."""
        # Sort by priority (higher priority wins)
        sorted_themes = sorted(
            themes,
            key=lambda t: t.metadata.get('priority', 0)
        )
        return self.compose_chain(sorted_themes)

    def clear_cache(self) -> None:
        """Clear composition cache."""
        with self._cache_lock:
            self._composition_cache.clear()
            logger.debug("Cleared composition cache")


class PropertyResolver:
    """Fast property lookup with caching and reference resolution.

    Handles property references (@property, @colors.primary),
    computed properties, and inheritance chains with
    sub-microsecond cached access.

    Features:
    - Property reference resolution (@property syntax)
    - Computed property support (calc() expressions)
    - Inheritance chain resolution
    - LRU caching for performance
    - Circular reference detection
    """

    def __init__(self, theme: Theme, max_cache_size: int = 1000):
        """Initialize resolver with theme and cache size."""
        self.theme = theme
        self._cache: Dict[str, Any] = {}
        self._resolving: Set[str] = set()  # Circular reference detection
        self._cache_lock = threading.RLock()
        self._max_cache_size = max_cache_size

        # Precompile reference patterns
        self._ref_pattern = re.compile(r'@([a-zA-Z][a-zA-Z0-9_.-]*)')
        self._calc_pattern = re.compile(r'calc\(([^)]+)\)')

        logger.debug(f"Created PropertyResolver for theme: {theme.name}")

    @lru_cache(maxsize=1000)
    def get_color(self, key: str, fallback: Optional[str] = None) -> str:
        """Get color with caching and reference resolution."""
        cache_key = f"color:{key}"

        with self._cache_lock:
            if cache_key in self._cache:
                return self._cache[cache_key]

        try:
            # Check for circular references
            if cache_key in self._resolving:
                raise InvalidThemeFormatError(f"Circular reference detected for color '{key}'")

            self._resolving.add(cache_key)

            # Get raw value
            if key in self.theme.colors:
                value = self.theme.colors[key]
            else:
                if fallback is None:
                    raise PropertyNotFoundError(f"Color '{key}' not found")
                value = fallback

            # Resolve references
            resolved = self._resolve_references(value)

            # Cache result
            with self._cache_lock:
                if len(self._cache) >= self._max_cache_size:
                    # Simple cache eviction - remove oldest 10%
                    items_to_remove = len(self._cache) // 10
                    for _ in range(items_to_remove):
                        self._cache.pop(next(iter(self._cache)))

                self._cache[cache_key] = resolved

            return resolved

        finally:
            self._resolving.discard(cache_key)

    @lru_cache(maxsize=1000)
    def get_style(self, key: str, fallback: Optional[Any] = None) -> Any:
        """Get style with caching and reference resolution."""
        cache_key = f"style:{key}"

        with self._cache_lock:
            if cache_key in self._cache:
                return self._cache[cache_key]

        try:
            # Check for circular references
            if cache_key in self._resolving:
                raise InvalidThemeFormatError(f"Circular reference detected for style '{key}'")

            self._resolving.add(cache_key)

            # Get raw value
            if key in self.theme.styles:
                value = self.theme.styles[key]
            else:
                if fallback is None:
                    raise PropertyNotFoundError(f"Style '{key}' not found")
                value = fallback

            # Resolve references if string
            if isinstance(value, str):
                resolved = self._resolve_references(value)
            else:
                resolved = value

            # Cache result
            with self._cache_lock:
                if len(self._cache) >= self._max_cache_size:
                    # Simple cache eviction
                    items_to_remove = len(self._cache) // 10
                    for _ in range(items_to_remove):
                        self._cache.pop(next(iter(self._cache)))

                self._cache[cache_key] = resolved

            return resolved

        finally:
            self._resolving.discard(cache_key)

    def _resolve_references(self, value: str) -> str:
        """Resolve property references in value."""
        if not isinstance(value, str) or '@' not in value:
            return value

        def replace_reference(match):
            ref = match.group(1)

            # Handle path references (colors.primary)
            if '.' in ref:
                parts = ref.split('.')
                if parts[0] == 'colors' and len(parts) == 2:
                    return self.get_color(parts[1], f"#{parts[1]}")
                elif parts[0] == 'styles' and len(parts) == 2:
                    return str(self.get_style(parts[1], f"value-{parts[1]}"))

            # Simple reference - try colors first, then styles, then metadata
            if ref in self.theme.colors:
                return self.get_color(ref)
            elif ref in self.theme.styles:
                return str(self.get_style(ref))
            elif ref in self.theme.metadata:
                return str(self.theme.metadata[ref])
            else:
                logger.warning(f"Unresolved reference: @{ref}")
                return f"@{ref}"  # Return unresolved

        # Replace all references
        resolved = self._ref_pattern.sub(replace_reference, value)

        # Handle calc() expressions
        if 'calc(' in resolved:
            resolved = self._resolve_calc_expressions(resolved)

        return resolved

    def _resolve_calc_expressions(self, value: str) -> str:
        """Resolve calc() expressions."""
        def replace_calc(match):
            expression = match.group(1)
            try:
                # Simple arithmetic evaluation (be careful with security)
                # Only allow basic math operations
                if any(char in expression for char in ['import', 'exec', 'eval', '__']):
                    return f"calc({expression})"  # Return unresolved for safety

                # Replace px, em, etc. with just numbers for calculation
                expr = re.sub(r'(\d+(?:\.\d+)?)px', r'\1', expression)
                expr = re.sub(r'(\d+(?:\.\d+)?)em', r'\1', expression)

                # Evaluate simple expressions
                result = eval(expr)
                return f"{result}px"  # Add px back
            except:
                return f"calc({expression})"  # Return original on error

        return self._calc_pattern.sub(replace_calc, value)

    def get_property(self, key: str, fallback: Optional[Any] = None) -> Any:
        """Get any property (color, style, or metadata)."""
        # Try colors first
        if key in self.theme.colors:
            return self.get_color(key, fallback)

        # Try styles
        if key in self.theme.styles:
            return self.get_style(key, fallback)

        # Try metadata
        if key in self.theme.metadata:
            return self.theme.metadata[key]

        if fallback is not None:
            return fallback

        raise PropertyNotFoundError(f"Property '{key}' not found")

    def resolve_reference(self, value: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Public method to resolve property references in a value.

        Args:
            value: The value that may contain references (@property syntax)
            context: Optional theme dict context (ignored - uses self.theme)

        Returns:
            Resolved value with all references expanded

        """
        return self._resolve_references(value)

    def clear_cache(self) -> None:
        """Clear property cache."""
        with self._cache_lock:
            self._cache.clear()
        self.get_color.cache_clear()
        self.get_style.cache_clear()
        logger.debug("Cleared property resolver cache")


class ThemeCollection:
    """Collection of related themes.

    Manages a collection of themes with features like:
    - Theme discovery and loading
    - Version management
    - Theme inheritance
    - Bulk operations
    """

    def __init__(self, name: str):
        """Initialize theme collection."""
        self._name = name
        self._themes: Dict[str, Theme] = {}
        self._theme_lock = threading.RLock()
        logger.debug(f"Created theme collection: {name}")

    @property
    def name(self) -> str:
        """Get collection name."""
        return self._name

    def add_theme(self, theme: Theme) -> None:
        """Add theme to collection."""
        with self._theme_lock:
            self._themes[theme.name] = theme
            logger.debug(f"Added theme '{theme.name}' to collection '{self._name}'")

    def get_theme(self, name: str) -> Optional[Theme]:
        """Get theme by name."""
        with self._theme_lock:
            return self._themes.get(name)

    def list_themes(self) -> List[str]:
        """List all theme names in collection."""
        with self._theme_lock:
            return list(self._themes.keys())

    def remove_theme(self, name: str) -> bool:
        """Remove theme from collection."""
        with self._theme_lock:
            if name in self._themes:
                del self._themes[name]
                logger.debug(f"Removed theme '{name}' from collection '{self._name}'")
                return True
            return False

    def clear(self) -> None:
        """Clear all themes from collection."""
        with self._theme_lock:
            self._themes.clear()
            logger.debug(f"Cleared all themes from collection '{self._name}'")


def validate_theme_data(data: Dict[str, Any]) -> bool:
    """Validate raw theme data structure."""
    logger.debug("Validating theme data structure")
    validator = ThemeValidator()
    return validator.validate(data)


def create_theme_from_dict(data: Dict[str, Any]) -> Theme:
    """Create Theme instance from dictionary data."""
    logger.debug("Creating theme from dictionary data")

    # Validate first
    if not validate_theme_data(data):
        raise InvalidThemeFormatError("Invalid theme data format")

    return Theme.from_dict(data)


def load_theme_from_file(file_path: Union[str, Path]) -> Theme:
    """Load theme from JSON file."""
    path = Path(file_path)
    if not path.exists():
        raise ThemeLoadError(f"Theme file not found: {path}")

    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        return create_theme_from_dict(data)
    except json.JSONDecodeError as e:
        raise InvalidThemeFormatError(f"Invalid JSON in theme file {path}: {e}")
    except Exception as e:
        raise ThemeLoadError(f"Failed to load theme from {path}: {e}")


def save_theme_to_file(theme: Theme, file_path: Union[str, Path]) -> None:
    """Save theme to JSON file."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(theme.to_dict(), f, indent=2, sort_keys=True)
        logger.debug(f"Saved theme '{theme.name}' to {path}")
    except Exception as e:
        raise ThemeLoadError(f"Failed to save theme to {path}: {e}")


# Export all public classes and functions
__all__ = [
    "Theme",
    "ThemeBuilder",
    "ThemeValidator",
    "ThemeComposer",
    "PropertyResolver",
    "ThemeCollection",
    "TokenColors",
    "ColorPalette",
    "StyleProperties",
    "ThemeMetadata",
    "validate_theme_data",
    "create_theme_from_dict",
    "load_theme_from_file",
    "save_theme_to_file",
]
