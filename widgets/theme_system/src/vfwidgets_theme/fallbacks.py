"""Fallback theme mechanism for VFWidgets Theme System.

This module provides the MINIMAL_THEME that ALWAYS works and graceful
degradation strategies. Ensures applications remain functional even
when themes fail completely.

Philosophy:
- MINIMAL_THEME is hardcoded and never depends on external resources
- Fallback colors are safe and accessible (meet WCAG guidelines)
- Performance is critical - fallback resolution < 100μs
- All fallbacks are thread-safe and memory-efficient

The fallback system is the safety net that ensures ThemedWidget
always provides working values, even in catastrophic failure scenarios.

Performance Requirements:
- get_fallback_color(): < 100μs
- get_fallback_theme(): < 100μs (immediate return)
- get_fallback_property(): < 100μs
- Zero memory allocations for repeated calls
"""

import threading
from copy import deepcopy
from typing import Any, Dict, Optional

# MINIMAL_THEME - The theme that ALWAYS works
# This is hardcoded and never depends on external resources
MINIMAL_THEME: Dict[str, Any] = {
    "name": "minimal",
    "version": "1.0.0",
    "metadata": {
        "description": "Hardcoded minimal theme for error recovery",
        "author": "VFWidgets Theme System"
    },

    "colors": {
        # Primary colors - safe, accessible defaults (NAMESPACED keys)
        "colors.primary": "#007acc",      # Blue - widely recognizable as primary
        "colors.secondary": "#6c757d",    # Gray - neutral secondary
        "colors.background": "#ffffff",   # White - maximum contrast
        "colors.surface": "#f8f9fa",      # Light gray - subtle surface
        "colors.text": "#212529",         # Dark gray - high contrast text
        "colors.text_secondary": "#6c757d",  # Medium gray - secondary text

        # Status colors - standard, accessible
        "colors.success": "#28a745",      # Green - universally understood
        "colors.warning": "#ffc107",      # Yellow - attention without alarm
        "colors.error": "#dc3545",        # Red - clear error indication
        "colors.info": "#17a2b8",         # Teal - informational

        # UI element colors
        "colors.border": "#dee2e6",       # Light gray - subtle borders
        "colors.divider": "#e9ecef",      # Very light gray - content separation
        "colors.shadow": "#00000010",     # Transparent black - subtle shadows
        "colors.focus": "#007acc40",      # Semi-transparent primary - focus rings

        # Interactive states
        "colors.hover": "#0056b3",        # Darker blue - clear hover state
        "colors.active": "#004085",       # Even darker blue - active state
        "colors.disabled": "#6c757d",     # Gray - clearly disabled
        "colors.disabled_bg": "#e9ecef",  # Light gray - disabled background
    },

    "fonts": {
        # Safe, widely available fonts
        "default": "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        "monospace": "'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, monospace",
        "heading": "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",

        # Font sizes in pixels (absolute, predictable)
        "size": 14,
        "size_small": 12,
        "size_large": 16,
        "size_heading": 20,

        # Font weights
        "weight_normal": 400,
        "weight_medium": 500,
        "weight_bold": 600,

        # Line heights (unitless for scalability)
        "line_height": 1.5,
        "line_height_tight": 1.25,
        "line_height_loose": 1.75,
    },

    "spacing": {
        # Spacing scale in pixels (8px base unit)
        "xs": 4,      # Extra small
        "sm": 8,      # Small
        "default": 16,  # Default/medium
        "md": 16,     # Medium (alias for default)
        "lg": 24,     # Large
        "xl": 32,     # Extra large
        "xxl": 48,    # Extra extra large

        # Component-specific spacing
        "padding": 16,
        "margin": 16,
        "gap": 8,
        "border_radius": 4,

        # Layout spacing
        "container_padding": 24,
        "section_gap": 32,
        "component_gap": 16,
    },

    "dimensions": {
        # Standard component dimensions
        "button_height": 36,
        "input_height": 36,
        "icon_size": 20,
        "avatar_size": 32,

        # Border widths
        "border_width": 1,
        "border_width_thick": 2,
        "focus_ring_width": 2,

        # Z-index scale
        "z_dropdown": 1000,
        "z_modal": 2000,
        "z_tooltip": 3000,
        "z_toast": 4000,
    },

    "animation": {
        # Animation durations in milliseconds
        "duration_fast": 150,
        "duration_normal": 300,
        "duration_slow": 500,

        # Easing functions (CSS-compatible)
        "easing_ease": "ease",
        "easing_ease_in": "ease-in",
        "easing_ease_out": "ease-out",
        "easing_ease_in_out": "ease-in-out",
    },

    "shadows": {
        # Box shadow definitions (CSS-compatible)
        "none": "none",
        "sm": "0 1px 2px rgba(0, 0, 0, 0.05)",
        "default": "0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06)",
        "md": "0 4px 6px rgba(0, 0, 0, 0.07), 0 2px 4px rgba(0, 0, 0, 0.06)",
        "lg": "0 10px 15px rgba(0, 0, 0, 0.1), 0 4px 6px rgba(0, 0, 0, 0.05)",
        "xl": "0 20px 25px rgba(0, 0, 0, 0.1), 0 10px 10px rgba(0, 0, 0, 0.04)",
    }
}


class FallbackColorSystem:
    """Fallback color system with intelligent defaults.

    Provides color resolution with automatic fallbacks for missing
    or invalid colors. Optimized for performance with caching.

    Performance Requirements:
    - get_color(): < 100μs for any color lookup
    - validate_color(): < 50μs for color validation
    - Thread-safe operation
    - Zero memory allocations for repeated calls

    Example:
        color_system = FallbackColorSystem()
        primary = color_system.get_color("primary")  # "#007acc"
        unknown = color_system.get_color("unknown")  # fallback color

    """

    def __init__(self):
        self._lock = threading.RLock()
        self._fallback_color = "#000000"  # Black - safest fallback
        self._color_aliases = {
            # Common color aliases for flexibility
            "primary_color": "colors.primary",
            "background_color": "colors.background",
            "text_color": "colors.text",
            "border_color": "colors.border",
            "accent": "colors.primary",
            "fg": "colors.text",
            "bg": "colors.background",
            # Legacy simple key mappings for backward compatibility
            "primary": "colors.primary",
            "secondary": "colors.secondary",
            "background": "colors.background",
            "surface": "colors.surface",
            "text": "colors.text",
            "text_secondary": "colors.text_secondary",
            "success": "colors.success",
            "warning": "colors.warning",
            "error": "colors.error",
            "info": "colors.info",
            "border": "colors.border",
            "divider": "colors.divider",
            "shadow": "colors.shadow",
            "focus": "colors.focus",
            "hover": "colors.hover",
            "active": "colors.active",
            "disabled": "colors.disabled",
            "disabled_bg": "colors.disabled_bg",
        }

    def get_color(self, color_key: str) -> str:
        """Get color value with automatic fallback.

        Args:
            color_key: Color key to resolve.

        Returns:
            Valid color value. Never None.

        Performance: < 100μs for any lookup.

        """
        # Check color aliases first
        actual_key = self._color_aliases.get(color_key, color_key)

        # Get color from minimal theme
        colors = MINIMAL_THEME.get("colors", {})
        color_value = colors.get(actual_key)

        if color_value and self._is_valid_color(color_value):
            return color_value

        # Return safe fallback
        return self._fallback_color

    def _is_valid_color(self, color: Any) -> bool:
        """Validate color value quickly.

        Args:
            color: Color value to validate.

        Returns:
            True if color is valid.

        Performance: < 50μs for validation.

        """
        if not isinstance(color, str):
            return False

        color = color.strip().lower()

        # Check hex colors
        if color.startswith('#'):
            if len(color) not in [4, 7]:
                return False
            return all(c in '0123456789abcdef' for c in color[1:])

        # Check rgb/rgba colors (basic validation)
        if color.startswith(('rgb(', 'rgba(')):
            return True

        # Check named colors (common ones)
        named_colors = {
            'red', 'green', 'blue', 'black', 'white', 'gray', 'grey',
            'yellow', 'orange', 'purple', 'brown', 'pink', 'cyan',
            'magenta', 'lime', 'navy', 'olive', 'teal', 'silver',
            'maroon', 'aqua', 'fuchsia'
        }
        return color in named_colors

    def get_fallback_color(self) -> str:
        """Get the ultimate fallback color.

        Returns:
            Safe fallback color that always works.

        Performance: < 10μs (immediate return).

        """
        return self._fallback_color

    def set_fallback_color(self, color: str) -> None:
        """Set the ultimate fallback color.

        Args:
            color: New fallback color (must be valid).

        Note:
            Only use this for testing or special cases.

        """
        if self._is_valid_color(color):
            with self._lock:
                self._fallback_color = color


# Global fallback color system instance
_global_fallback_system: Optional[FallbackColorSystem] = None
_fallback_lock = threading.Lock()


def create_fallback_color_system() -> FallbackColorSystem:
    """Create a new fallback color system.

    Returns:
        New FallbackColorSystem instance.

    """
    return FallbackColorSystem()


def get_global_fallback_color_system() -> FallbackColorSystem:
    """Get the global fallback color system.

    Returns:
        Global FallbackColorSystem instance (thread-safe singleton).

    """
    global _global_fallback_system

    if _global_fallback_system is None:
        with _fallback_lock:
            if _global_fallback_system is None:
                _global_fallback_system = FallbackColorSystem()

    return _global_fallback_system


# Convenience functions for quick access
def get_fallback_theme() -> Dict[str, Any]:
    """Get the minimal fallback theme.

    Returns:
        Deep copy of MINIMAL_THEME for safe usage.

    Performance: < 100μs through optimized copying.
    Memory: Creates new copy each time to prevent mutation.

    """
    return deepcopy(MINIMAL_THEME)


def get_fallback_color(color_key: str) -> str:
    """Get fallback color for a specific key.

    Args:
        color_key: Color key to resolve.

    Returns:
        Valid color value from minimal theme or ultimate fallback.

    Performance: < 100μs for any color lookup.

    """
    color_system = get_global_fallback_color_system()
    return color_system.get_color(color_key)


def get_fallback_property(property_path: str) -> Any:
    """Get fallback property value from minimal theme.

    Args:
        property_path: Property path (e.g., "colors.primary", "fonts.size").

    Returns:
        Property value from minimal theme, or None if not found.

    Performance: < 100μs for any property lookup.

    Example:
        primary_color = get_fallback_property("colors.primary")
        font_size = get_fallback_property("fonts.size")
        spacing = get_fallback_property("spacing.default")

    """
    try:
        # Split path and navigate through theme
        parts = property_path.split('.')
        current = MINIMAL_THEME

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        return current

    except (AttributeError, KeyError, TypeError):
        return None


def validate_theme_completeness(theme_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate theme completeness and fill missing values.

    Args:
        theme_data: Theme data to validate and complete.

    Returns:
        Complete theme data with fallbacks for missing values.

    Performance: < 5ms for complete theme validation.

    Example:
        incomplete_theme = {"colors": {"primary": "#007acc"}}
        complete_theme = validate_theme_completeness(incomplete_theme)
        # complete_theme now has all required properties

    """
    if not isinstance(theme_data, dict):
        return get_fallback_theme()

    # Start with fallback theme as base
    complete_theme = get_fallback_theme()

    # Merge provided theme data
    _deep_merge(complete_theme, theme_data)

    return complete_theme


def _deep_merge(target: Dict[str, Any], source: Dict[str, Any]) -> None:
    """Deep merge source dictionary into target dictionary.

    Args:
        target: Target dictionary to merge into.
        source: Source dictionary to merge from.

    Note:
        Modifies target dictionary in place.

    """
    for key, value in source.items():
        if (
            key in target
            and isinstance(target[key], dict)
            and isinstance(value, dict)
        ):
            _deep_merge(target[key], value)
        else:
            target[key] = value


def get_safe_color_palette() -> Dict[str, str]:
    """Get a safe color palette for emergency fallbacks.

    Returns:
        Dictionary of safe, accessible colors with namespaced keys.

    Performance: < 50μs (immediate return of pre-defined palette).

    Example:
        palette = get_safe_color_palette()
        safe_red = palette["colors.error"]  # "#dc3545"

    """
    return {
        "colors.primary": "#007acc",
        "colors.secondary": "#6c757d",
        "colors.background": "#ffffff",
        "colors.text": "#212529",
        "colors.success": "#28a745",
        "colors.warning": "#ffc107",
        "colors.error": "#dc3545",
        "colors.info": "#17a2b8",
        "colors.border": "#dee2e6",
        "colors.black": "#000000",
        "colors.white": "#ffffff",
    }


def reset_fallback_system() -> None:
    """Reset the global fallback system (for testing).

    Note:
        This is primarily for testing purposes.

    """
    global _global_fallback_system
    with _fallback_lock:
        _global_fallback_system = None


# Performance optimization: pre-compile color validation regex
import re

_hex_color_pattern = re.compile(r'^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$')


def is_valid_hex_color(color: str) -> bool:
    """Fast hex color validation using compiled regex.

    Args:
        color: Color string to validate.

    Returns:
        True if valid hex color.

    Performance: < 10μs using compiled regex.

    """
    return bool(_hex_color_pattern.match(color))


# Export all public interfaces
__all__ = [
    # Core fallback data
    "MINIMAL_THEME",

    # Fallback color system
    "FallbackColorSystem",
    "create_fallback_color_system",
    "get_global_fallback_color_system",

    # Convenience functions
    "get_fallback_theme",
    "get_fallback_color",
    "get_fallback_property",
    "validate_theme_completeness",
    "get_safe_color_palette",

    # Utilities
    "is_valid_hex_color",
    "reset_fallback_system",
]
