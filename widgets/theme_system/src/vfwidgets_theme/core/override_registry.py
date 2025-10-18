"""
Override Registry - Layered color override management.

This module implements the OverrideRegistry class which manages
app-level and user-level color overrides with priority resolution.

Architecture:
- Two layers: "app" (lower priority) and "user" (higher priority)
- Priority resolution: user > app > base theme
- Thread-safe operations using RLock
- Validation of colors and token names
- Serialization support for persistence

Performance Targets:
- resolve() < 0.1ms (100 microseconds)
- bulk operations (100 overrides) < 50ms
- Thread-safe with minimal lock contention

Usage:
    registry = OverrideRegistry()

    # Set overrides
    registry.set_override("app", "editor.background", "#1e1e2e")
    registry.set_override("user", "editor.background", "#user123")

    # Resolve with priority
    color = registry.resolve("editor.background")  # Returns "#user123"

    # Bulk operations
    registry.set_overrides_bulk("app", {
        "tab.activeBackground": "#89b4fa",
        "button.background": "#313244",
    })
"""

import re
import threading
from typing import Dict, Optional, Set
from PySide6.QtGui import QColor


class OverrideRegistry:
    """Manages layered color overrides with priority resolution.

    This class provides thread-safe management of color overrides
    across two layers (app and user) with automatic priority resolution.

    Attributes:
        VALID_LAYERS: Set of valid layer names ("app", "user")
        MAX_TOKEN_LENGTH: Maximum length for token names (255 chars)
        MAX_OVERRIDES_PER_LAYER: Maximum overrides per layer (10,000)
        TOKEN_PATTERN: Regex pattern for valid token names
    """

    # Class constants
    VALID_LAYERS: Set[str] = {"app", "user"}
    MAX_TOKEN_LENGTH: int = 255
    MAX_OVERRIDES_PER_LAYER: int = 10000
    TOKEN_PATTERN: re.Pattern = re.compile(r'^[a-zA-Z][a-zA-Z0-9._]*$')

    # Layer priority (higher number = higher priority)
    _LAYER_PRIORITY: Dict[str, int] = {
        "app": 1,
        "user": 2,
    }

    def __init__(self):
        """Initialize empty override registry with thread safety."""
        self._layers: Dict[str, Dict[str, str]] = {
            "app": {},
            "user": {},
        }
        self._lock = threading.RLock()

    # ========================================================================
    # Core CRUD Operations
    # ========================================================================

    def set_override(
        self,
        layer: str,
        token: str,
        value: str,
        validate: bool = True
    ) -> None:
        """Set a color override in the specified layer.

        Args:
            layer: Layer name ("app" or "user")
            token: Color token name (e.g., "editor.background")
            value: Color value (hex, rgb, or named color)
            validate: Whether to validate color and token (default: True)

        Raises:
            ValueError: If layer is invalid, token is invalid, or color is invalid
            RuntimeError: If layer is at maximum capacity
        """
        with self._lock:
            # Validate layer
            if layer not in self.VALID_LAYERS:
                raise ValueError(
                    f"Invalid layer '{layer}'. Must be one of: {', '.join(self.VALID_LAYERS)}"
                )

            # Validate token name if requested
            if validate:
                self._validate_token_name(token)

            # Validate color if requested
            if validate:
                self._validate_color(value)

            # Check capacity
            if token not in self._layers[layer]:
                if len(self._layers[layer]) >= self.MAX_OVERRIDES_PER_LAYER:
                    raise RuntimeError(
                        f"Layer '{layer}' is at maximum capacity "
                        f"({self.MAX_OVERRIDES_PER_LAYER} overrides)"
                    )

            # Set the override
            self._layers[layer][token] = value

    def get_override(
        self,
        layer: str,
        token: str,
        fallback: Optional[str] = None
    ) -> Optional[str]:
        """Get override from a specific layer.

        Args:
            layer: Layer name ("app" or "user")
            token: Color token name
            fallback: Value to return if override doesn't exist

        Returns:
            Color value if override exists, fallback otherwise

        Raises:
            ValueError: If layer is invalid
        """
        with self._lock:
            if layer not in self.VALID_LAYERS:
                raise ValueError(
                    f"Invalid layer '{layer}'. Must be one of: {', '.join(self.VALID_LAYERS)}"
                )

            return self._layers[layer].get(token, fallback)

    def remove_override(self, layer: str, token: str) -> bool:
        """Remove an override from the specified layer.

        Args:
            layer: Layer name ("app" or "user")
            token: Color token name

        Returns:
            True if override was removed, False if it didn't exist

        Raises:
            ValueError: If layer is invalid
        """
        with self._lock:
            if layer not in self.VALID_LAYERS:
                raise ValueError(
                    f"Invalid layer '{layer}'. Must be one of: {', '.join(self.VALID_LAYERS)}"
                )

            if token in self._layers[layer]:
                del self._layers[layer][token]
                return True
            return False

    def clear_layer(self, layer: str) -> int:
        """Clear all overrides in the specified layer.

        Args:
            layer: Layer name ("app" or "user")

        Returns:
            Number of overrides that were cleared

        Raises:
            ValueError: If layer is invalid
        """
        with self._lock:
            if layer not in self.VALID_LAYERS:
                raise ValueError(
                    f"Invalid layer '{layer}'. Must be one of: {', '.join(self.VALID_LAYERS)}"
                )

            count = len(self._layers[layer])
            self._layers[layer].clear()
            return count

    def has_override(self, layer: str, token: str) -> bool:
        """Check if an override exists in the specified layer.

        Args:
            layer: Layer name ("app" or "user")
            token: Color token name

        Returns:
            True if override exists, False otherwise

        Raises:
            ValueError: If layer is invalid
        """
        with self._lock:
            if layer not in self.VALID_LAYERS:
                raise ValueError(
                    f"Invalid layer '{layer}'. Must be one of: {', '.join(self.VALID_LAYERS)}"
                )

            return token in self._layers[layer]

    # ========================================================================
    # Priority Resolution
    # ========================================================================

    def resolve(self, token: str, fallback: Optional[str] = None) -> Optional[str]:
        """Resolve color with priority: user > app > fallback.

        This is the main method for getting effective color values
        with proper layer priority resolution.

        Args:
            token: Color token name
            fallback: Value to return if no override exists

        Returns:
            Color value from highest priority layer, or fallback
        """
        with self._lock:
            # Check user layer first (highest priority)
            if token in self._layers["user"]:
                return self._layers["user"][token]

            # Check app layer second
            if token in self._layers["app"]:
                return self._layers["app"][token]

            # No override found
            return fallback

    # ========================================================================
    # Bulk Operations
    # ========================================================================

    def set_overrides_bulk(
        self,
        layer: str,
        overrides: Dict[str, str],
        validate: bool = True
    ) -> None:
        """Set multiple overrides at once for efficiency.

        Args:
            layer: Layer name ("app" or "user")
            overrides: Dictionary of token -> color mappings
            validate: Whether to validate colors and tokens

        Raises:
            ValueError: If layer, any token, or any color is invalid
            RuntimeError: If bulk operation would exceed capacity
        """
        with self._lock:
            # Validate layer
            if layer not in self.VALID_LAYERS:
                raise ValueError(
                    f"Invalid layer '{layer}'. Must be one of: {', '.join(self.VALID_LAYERS)}"
                )

            # Validate all before setting any
            if validate:
                for token, color in overrides.items():
                    self._validate_token_name(token)
                    self._validate_color(color)

            # Check capacity
            new_tokens = set(overrides.keys()) - set(self._layers[layer].keys())
            if len(self._layers[layer]) + len(new_tokens) > self.MAX_OVERRIDES_PER_LAYER:
                raise RuntimeError(
                    f"Bulk operation would exceed maximum capacity "
                    f"for layer '{layer}' ({self.MAX_OVERRIDES_PER_LAYER} overrides)"
                )

            # Set all overrides
            self._layers[layer].update(overrides)

    def get_layer_overrides(self, layer: str) -> Dict[str, str]:
        """Get all overrides for a specific layer.

        Args:
            layer: Layer name ("app" or "user")

        Returns:
            Dictionary copy of all overrides in the layer

        Raises:
            ValueError: If layer is invalid
        """
        with self._lock:
            if layer not in self.VALID_LAYERS:
                raise ValueError(
                    f"Invalid layer '{layer}'. Must be one of: {', '.join(self.VALID_LAYERS)}"
                )

            return self._layers[layer].copy()

    def get_all_effective_overrides(self) -> Dict[str, str]:
        """Get all effective overrides with priority resolution.

        Returns a dictionary of all tokens with overrides,
        where the value is from the highest priority layer.

        Returns:
            Dictionary of token -> effective color mappings
        """
        with self._lock:
            result = {}

            # Start with app layer (lower priority)
            result.update(self._layers["app"])

            # Override with user layer (higher priority)
            result.update(self._layers["user"])

            return result

    # ========================================================================
    # Serialization
    # ========================================================================

    def to_dict(self) -> Dict[str, Dict[str, str]]:
        """Serialize registry to dictionary for persistence.

        Returns:
            Dictionary with layer -> overrides structure
        """
        with self._lock:
            return {
                layer: overrides.copy()
                for layer, overrides in self._layers.items()
            }

    @classmethod
    def from_dict(cls, data: Dict[str, Dict[str, str]]) -> "OverrideRegistry":
        """Deserialize registry from dictionary.

        Args:
            data: Dictionary with layer -> overrides structure

        Returns:
            New OverrideRegistry instance with loaded data

        Raises:
            ValueError: If data contains invalid layers
        """
        registry = cls()

        for layer, overrides in data.items():
            if layer not in cls.VALID_LAYERS:
                raise ValueError(
                    f"Invalid layer '{layer}' in serialized data. "
                    f"Must be one of: {', '.join(cls.VALID_LAYERS)}"
                )

            # Use bulk set for efficiency (validation disabled for trusted data)
            registry.set_overrides_bulk(layer, overrides, validate=False)

        return registry

    # ========================================================================
    # Validation (Private)
    # ========================================================================

    @classmethod
    def _validate_token_name(cls, token: str) -> None:
        """Validate token name format.

        Args:
            token: Token name to validate

        Raises:
            ValueError: If token name is invalid
        """
        if not token:
            raise ValueError("Token name cannot be empty")

        if len(token) > cls.MAX_TOKEN_LENGTH:
            raise ValueError(
                f"Token name too long: {len(token)} characters "
                f"(max: {cls.MAX_TOKEN_LENGTH})"
            )

        if not cls.TOKEN_PATTERN.match(token):
            raise ValueError(
                f"Invalid token name: '{token}'. "
                f"Must start with letter and contain only letters, numbers, dots, and underscores"
            )

    @classmethod
    def _validate_color(cls, color: str) -> None:
        """Validate color format using Qt's QColor.

        Args:
            color: Color value to validate

        Raises:
            ValueError: If color format is invalid
        """
        if not QColor.isValidColor(color):
            raise ValueError(f"Invalid color format: '{color}'")

    # ========================================================================
    # Utility Methods
    # ========================================================================

    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about current override state.

        Returns:
            Dictionary with statistics (override counts per layer)
        """
        with self._lock:
            return {
                f"{layer}_overrides": len(overrides)
                for layer, overrides in self._layers.items()
            }

    def __repr__(self) -> str:
        """String representation for debugging."""
        stats = self.get_statistics()
        return (
            f"OverrideRegistry("
            f"app={stats['app_overrides']}, "
            f"user={stats['user_overrides']})"
        )
