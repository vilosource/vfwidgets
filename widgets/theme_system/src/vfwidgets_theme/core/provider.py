"""ThemeProvider implementation with caching and error recovery.

This module provides concrete implementations of the ThemeProvider protocol,
handling theme data access, caching, and coordination with the broader
theme system. It follows the Single Responsibility Principle by focusing
on theme data provision and access.

Key Classes:
- DefaultThemeProvider: Standard theme provider implementation
- CachedThemeProvider: Provider with intelligent LRU caching
- CompositeThemeProvider: Provider that combines multiple sources

Design Principles:
- Protocol Implementation: Concrete implementation of ThemeProvider protocol
- Performance: Efficient theme data access with sub-microsecond caching
- Error Recovery: Graceful fallbacks for missing themes/properties
- Thread Safety: Safe concurrent access with minimal locking
- Memory Efficiency: Intelligent caching with automatic cleanup

Performance Requirements:
- Property access: < 1μs (cached)
- Cache hit rate: > 90%
- Memory overhead: < 100 bytes per registered widget
- Thread-safe concurrent access
"""

import threading
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Optional

from ..errors import PropertyNotFoundError, ThemeNotFoundError
from ..fallbacks import get_fallback_color, get_fallback_property
from ..logging import get_debug_logger

# Import foundation modules
from ..protocols import ColorValue, PropertyKey, PropertyValue, ThemeData, ThemeProvider

# Import core components
from .theme import PropertyResolver, Theme

logger = get_debug_logger(__name__)


@dataclass
class ProviderStats:
    """Statistics for provider operations."""

    theme_access_count: int = 0
    color_access_count: int = 0
    property_access_count: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    errors: int = 0
    total_access_time: float = 0.0


class DefaultThemeProvider:
    """Standard implementation of ThemeProvider protocol.

    Provides theme data access with fallback support, validation,
    and performance optimization. This is the default provider
    used by the theme system.

    Features:
    - Thread-safe theme storage and access
    - Property resolution with fallback support
    - Performance monitoring and statistics
    - Error recovery with graceful degradation
    """

    def __init__(self, themes: Optional[dict[str, Theme]] = None):
        """Initialize provider with optional theme collection.

        Args:
            themes: Dictionary of themes keyed by name

        """
        self._themes: dict[str, Theme] = themes or {}
        self._current_theme: Optional[Theme] = None
        self._property_resolver: Optional[PropertyResolver] = None
        self._stats = ProviderStats()
        self._lock = threading.RLock()
        logger.debug("DefaultThemeProvider initialized")

    def get_theme_data(self, theme_name: str) -> ThemeData:
        """Get complete theme data for specified theme.

        Args:
            theme_name: Name of theme to get

        Returns:
            Complete theme data dictionary

        Raises:
            ThemeNotFoundError: If theme not found

        """
        start_time = time.time()

        try:
            with self._lock:
                if theme_name not in self._themes:
                    raise ThemeNotFoundError(f"Theme '{theme_name}' not found")

                theme = self._themes[theme_name]
                theme_data = theme.to_dict()

                self._stats.theme_access_count += 1
                self._stats.total_access_time += time.time() - start_time

                logger.debug(f"Retrieved theme data for: {theme_name}")
                return theme_data

        except Exception as e:
            with self._lock:
                self._stats.errors += 1
            if isinstance(e, ThemeNotFoundError):
                raise
            else:
                logger.error(f"Error getting theme data for {theme_name}: {e}")
                raise ThemeNotFoundError(f"Error accessing theme '{theme_name}': {e}")

    def get_color(self, color_key: str, theme_name: Optional[str] = None) -> ColorValue:
        """Get color value with fallback support.

        Args:
            color_key: Key of color to retrieve
            theme_name: Theme name (uses current theme if None)

        Returns:
            Color value string

        Raises:
            ThemeNotFoundError: If theme not found (property errors use fallbacks)

        """
        start_time = time.time()

        try:
            with self._lock:
                # Determine which theme to use
                target_theme_name = theme_name
                if target_theme_name is None and self._current_theme:
                    target_theme_name = self._current_theme.name

                # Try to get color from theme
                if target_theme_name and target_theme_name in self._themes:
                    theme = self._themes[target_theme_name]

                    # Try direct color access
                    if color_key in theme.colors:
                        color = theme.colors[color_key]
                        # Create property resolver for this theme if needed
                        if (
                            self._property_resolver is None
                            or self._property_resolver.theme != theme
                        ):
                            self._property_resolver = PropertyResolver(theme)
                        # Resolve any references in the color value
                        resolved_color = self._property_resolver.resolve_reference(
                            color, theme.to_dict()
                        )

                        self._stats.color_access_count += 1
                        self._stats.total_access_time += time.time() - start_time

                        logger.debug(
                            f"Retrieved color '{color_key}' from theme '{target_theme_name}': {resolved_color}"
                        )
                        return resolved_color

                # Fallback to global fallback system
                fallback_color = get_fallback_color(color_key)

                self._stats.color_access_count += 1
                self._stats.total_access_time += time.time() - start_time

                logger.debug(f"Used fallback color for '{color_key}': {fallback_color}")
                return fallback_color

        except Exception as e:
            with self._lock:
                self._stats.errors += 1
            logger.error(f"Error getting color '{color_key}': {e}")
            # Return fallback color instead of raising
            return get_fallback_color(color_key)

    def get_property(
        self, property_key: PropertyKey, theme_name: Optional[str] = None
    ) -> PropertyValue:
        """Get theme property with fallback support.

        Args:
            property_key: Key of property to retrieve (supports dot notation)
            theme_name: Theme name (uses current theme if None)

        Returns:
            Property value (can be any type)

        Raises:
            ThemeNotFoundError: If theme not found (property errors use fallbacks)

        """
        start_time = time.time()

        try:
            with self._lock:
                # Determine which theme to use
                target_theme_name = theme_name
                if target_theme_name is None and self._current_theme:
                    target_theme_name = self._current_theme.name

                # Try to get property from theme
                if target_theme_name and target_theme_name in self._themes:
                    theme = self._themes[target_theme_name]
                    theme_data = theme.to_dict()

                    try:
                        # Use dot notation to access nested properties
                        property_value = self._get_nested_property(theme_data, property_key)

                        if property_value is not None:
                            # Resolve any references in the property value
                            if isinstance(property_value, str):
                                # Create property resolver for this theme if needed
                                if (
                                    self._property_resolver is None
                                    or self._property_resolver.theme != theme
                                ):
                                    self._property_resolver = PropertyResolver(theme)
                                resolved_value = self._property_resolver.resolve_reference(
                                    property_value, theme_data
                                )
                            else:
                                resolved_value = property_value

                            self._stats.property_access_count += 1
                            self._stats.total_access_time += time.time() - start_time

                            logger.debug(
                                f"Retrieved property '{property_key}' from theme '{target_theme_name}': {resolved_value}"
                            )
                            return resolved_value

                    except (KeyError, AttributeError, TypeError):
                        # Property not found in theme, will use fallback
                        pass

                # Fallback to global fallback system
                fallback_value = get_fallback_property(property_key)

                self._stats.property_access_count += 1
                self._stats.total_access_time += time.time() - start_time

                logger.debug(f"Used fallback property for '{property_key}': {fallback_value}")
                return fallback_value

        except Exception as e:
            with self._lock:
                self._stats.errors += 1
            logger.error(f"Error getting property '{property_key}': {e}")
            # Return fallback property instead of raising
            return get_fallback_property(property_key)

    def _get_nested_property(self, data: dict[str, Any], property_key: str) -> Any:
        """Get nested property using dot notation."""
        keys = property_key.split(".")
        current = data

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None

        return current

    def list_themes(self) -> list[str]:
        """List all available themes.

        Returns:
            List of theme names

        """
        with self._lock:
            return list(self._themes.keys())

    def has_theme(self, theme_name: str) -> bool:
        """Check if theme exists.

        Args:
            theme_name: Theme name to check

        Returns:
            True if theme exists

        """
        with self._lock:
            return theme_name in self._themes

    def set_current_theme(self, theme_name: str) -> None:
        """Set the current active theme.

        Args:
            theme_name: Name of theme to set as current

        Raises:
            ThemeNotFoundError: If theme doesn't exist

        """
        with self._lock:
            if theme_name not in self._themes:
                raise ThemeNotFoundError(f"Theme '{theme_name}' not found")

            self._current_theme = self._themes[theme_name]
            logger.debug(f"Set current theme to: {theme_name}")

    def add_theme(self, theme: Theme) -> None:
        """Add a theme to the provider.

        Args:
            theme: Theme to add

        """
        with self._lock:
            self._themes[theme.name] = theme
            logger.debug(f"Added theme: {theme.name}")

    def remove_theme(self, theme_name: str) -> bool:
        """Remove a theme from the provider.

        Args:
            theme_name: Name of theme to remove

        Returns:
            True if theme was removed, False if not found

        """
        with self._lock:
            if theme_name in self._themes:
                # Don't remove current theme without setting a new one
                if self._current_theme and self._current_theme.name == theme_name:
                    self._current_theme = None

                del self._themes[theme_name]
                logger.debug(f"Removed theme: {theme_name}")
                return True

            return False

    def get_statistics(self) -> dict[str, Any]:
        """Get provider statistics."""
        with self._lock:
            total_accesses = (
                self._stats.theme_access_count
                + self._stats.color_access_count
                + self._stats.property_access_count
            )

            avg_access_time = self._stats.total_access_time / max(1, total_accesses)

            return {
                "total_themes": len(self._themes),
                "current_theme": self._current_theme.name if self._current_theme else None,
                "theme_access_count": self._stats.theme_access_count,
                "color_access_count": self._stats.color_access_count,
                "property_access_count": self._stats.property_access_count,
                "total_accesses": total_accesses,
                "cache_hits": self._stats.cache_hits,
                "cache_misses": self._stats.cache_misses,
                "errors": self._stats.errors,
                "total_access_time": self._stats.total_access_time,
                "average_access_time": avg_access_time,
            }


class CachedThemeProvider:
    """Theme provider with intelligent LRU caching.

    Wraps another provider and adds caching for performance optimization.
    Includes cache invalidation, memory management, and statistics.

    Features:
    - LRU cache with configurable size limits
    - Cache invalidation by theme or globally
    - Performance statistics and hit rate tracking
    - Thread-safe cache operations
    - Memory-efficient cache management
    """

    def __init__(self, base_provider: ThemeProvider, cache_size: int = 1000):
        """Initialize cached provider.

        Args:
            base_provider: Provider to wrap with caching
            cache_size: Maximum cache entries

        """
        self._base_provider = base_provider
        self._cache_size = cache_size
        self._color_cache: OrderedDict[str, ColorValue] = OrderedDict()
        self._property_cache: OrderedDict[str, PropertyValue] = OrderedDict()
        self._theme_cache: OrderedDict[str, ThemeData] = OrderedDict()
        self._lock = threading.RLock()
        self._stats = ProviderStats()
        logger.debug(f"CachedThemeProvider initialized with cache size: {cache_size}")

    def get_theme_data(self, theme_name: str) -> ThemeData:
        """Get theme data with caching."""
        cache_key = theme_name

        with self._lock:
            # Check cache first
            if cache_key in self._theme_cache:
                # Move to end (most recently used)
                theme_data = self._theme_cache.pop(cache_key)
                self._theme_cache[cache_key] = theme_data
                self._stats.cache_hits += 1
                logger.debug(f"Theme cache hit for: {cache_key}")
                return theme_data

            # Cache miss - get from base provider
            self._stats.cache_misses += 1
            theme_data = self._base_provider.get_theme_data(theme_name)

            # Cache the result
            self._cache_theme_data(cache_key, theme_data)

            logger.debug(f"Theme cache miss, cached: {cache_key}")
            return theme_data

    def get_color(self, color_key: str, theme_name: Optional[str] = None) -> ColorValue:
        """Get color with caching."""
        cache_key = f"{theme_name or 'current'}:{color_key}"

        with self._lock:
            # Check cache first
            if cache_key in self._color_cache:
                # Move to end (most recently used)
                color = self._color_cache.pop(cache_key)
                self._color_cache[cache_key] = color
                self._stats.cache_hits += 1
                logger.debug(f"Color cache hit for: {cache_key}")
                return color

            # Cache miss - get from base provider
            self._stats.cache_misses += 1
            color = self._base_provider.get_color(color_key, theme_name)

            # Cache the result
            self._cache_color(cache_key, color)

            logger.debug(f"Color cache miss, cached: {cache_key}")
            return color

    def get_property(
        self, property_key: PropertyKey, theme_name: Optional[str] = None
    ) -> PropertyValue:
        """Get property with caching."""
        cache_key = f"{theme_name or 'current'}:{property_key}"

        with self._lock:
            # Check cache first
            if cache_key in self._property_cache:
                # Move to end (most recently used)
                prop = self._property_cache.pop(cache_key)
                self._property_cache[cache_key] = prop
                self._stats.cache_hits += 1
                logger.debug(f"Property cache hit for: {cache_key}")
                return prop

            # Cache miss - get from base provider
            self._stats.cache_misses += 1
            prop = self._base_provider.get_property(property_key, theme_name)

            # Cache the result
            self._cache_property(cache_key, prop)

            logger.debug(f"Property cache miss, cached: {cache_key}")
            return prop

    def _cache_color(self, key: str, color: ColorValue) -> None:
        """Cache color with LRU eviction."""
        self._color_cache[key] = color
        self._manage_cache_size(self._color_cache)

    def _cache_property(self, key: str, prop: PropertyValue) -> None:
        """Cache property with LRU eviction."""
        self._property_cache[key] = prop
        self._manage_cache_size(self._property_cache)

    def _cache_theme_data(self, key: str, theme_data: ThemeData) -> None:
        """Cache theme data with LRU eviction."""
        self._theme_cache[key] = theme_data
        self._manage_cache_size(self._theme_cache)

    def _manage_cache_size(self, cache: OrderedDict) -> None:
        """Manage cache size with LRU eviction."""
        while len(cache) > self._cache_size:
            # Remove oldest entry
            oldest_key = next(iter(cache))
            del cache[oldest_key]
            logger.debug(f"Evicted cache entry: {oldest_key}")

    def invalidate_cache(self, theme_name: Optional[str] = None) -> None:
        """Invalidate cache for theme or all themes.

        Args:
            theme_name: Theme to invalidate (None for all)

        """
        with self._lock:
            if theme_name:
                # Remove entries for specific theme
                keys_to_remove = []

                for key in self._color_cache:
                    if key.startswith(f"{theme_name}:"):
                        keys_to_remove.append(key)
                for key in keys_to_remove:
                    del self._color_cache[key]

                keys_to_remove = []
                for key in self._property_cache:
                    if key.startswith(f"{theme_name}:"):
                        keys_to_remove.append(key)
                for key in keys_to_remove:
                    del self._property_cache[key]

                if theme_name in self._theme_cache:
                    del self._theme_cache[theme_name]

                logger.debug(f"Invalidated cache for theme: {theme_name}")
            else:
                # Clear all caches
                self._color_cache.clear()
                self._property_cache.clear()
                self._theme_cache.clear()
                logger.debug("Invalidated all caches")

    def list_themes(self) -> list[str]:
        """List themes from base provider."""
        return self._base_provider.list_themes()

    def has_theme(self, theme_name: str) -> bool:
        """Check if theme exists in base provider."""
        return self._base_provider.has_theme(theme_name)

    def get_statistics(self) -> dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._stats.cache_hits + self._stats.cache_misses
            hit_rate = self._stats.cache_hits / max(1, total_requests)

            base_stats = {}
            if hasattr(self._base_provider, "get_statistics"):
                base_stats = self._base_provider.get_statistics()

            return {
                **base_stats,
                "cache_size": self._cache_size,
                "color_cache_entries": len(self._color_cache),
                "property_cache_entries": len(self._property_cache),
                "theme_cache_entries": len(self._theme_cache),
                "total_cache_entries": (
                    len(self._color_cache) + len(self._property_cache) + len(self._theme_cache)
                ),
                "cache_hits": self._stats.cache_hits,
                "cache_misses": self._stats.cache_misses,
                "cache_hit_rate": hit_rate,
            }


class CompositeThemeProvider:
    """Provider that combines multiple theme sources.

    Allows themes from multiple providers to be accessed through
    a single interface with priority ordering. The first provider
    in the list has the highest priority.

    Features:
    - Multiple provider support with priority ordering
    - Fallback chain for missing themes/properties
    - Aggregate theme listing with deduplication
    - Error recovery across providers
    """

    def __init__(self, providers: Optional[list[ThemeProvider]] = None):
        """Initialize composite provider.

        Args:
            providers: List of providers in priority order (first = highest priority)

        """
        self._providers: list[ThemeProvider] = providers or []
        self._lock = threading.RLock()
        logger.debug(f"CompositeThemeProvider initialized with {len(self._providers)} providers")

    def add_provider(self, provider: ThemeProvider, priority: int = -1) -> None:
        """Add provider at specified priority.

        Args:
            provider: Provider to add
            priority: Priority index (0 = highest priority, -1 = lowest)

        """
        with self._lock:
            if priority == -1 or priority >= len(self._providers):
                self._providers.append(provider)
            else:
                self._providers.insert(priority, provider)
            logger.debug(f"Added provider at priority {priority}")

    def get_theme_data(self, theme_name: str) -> ThemeData:
        """Get theme data from first provider that has it."""
        with self._lock:
            for provider in self._providers:
                try:
                    return provider.get_theme_data(theme_name)
                except ThemeNotFoundError:
                    continue

            # No provider has the theme
            raise ThemeNotFoundError(f"Theme '{theme_name}' not found in any provider")

    def get_color(self, color_key: str, theme_name: Optional[str] = None) -> ColorValue:
        """Get color from first provider that has it."""
        with self._lock:
            for provider in self._providers:
                try:
                    return provider.get_color(color_key, theme_name)
                except (ThemeNotFoundError, PropertyNotFoundError):
                    continue

            # No provider has the color, use global fallback
            return get_fallback_color(color_key)

    def get_property(
        self, property_key: PropertyKey, theme_name: Optional[str] = None
    ) -> PropertyValue:
        """Get property from first provider that has it."""
        with self._lock:
            for provider in self._providers:
                try:
                    return provider.get_property(property_key, theme_name)
                except (ThemeNotFoundError, PropertyNotFoundError):
                    continue

            # No provider has the property, use global fallback
            return get_fallback_property(property_key)

    def list_themes(self) -> list[str]:
        """List themes from all providers with deduplication."""
        with self._lock:
            themes: set[str] = set()
            for provider in self._providers:
                try:
                    provider_themes = provider.list_themes()
                    themes.update(provider_themes)
                except Exception as e:
                    logger.error(f"Error listing themes from provider: {e}")

            return sorted(themes)

    def has_theme(self, theme_name: str) -> bool:
        """Check if any provider has the theme."""
        with self._lock:
            for provider in self._providers:
                try:
                    if provider.has_theme(theme_name):
                        return True
                except Exception as e:
                    logger.error(f"Error checking theme in provider: {e}")

            return False

    def get_statistics(self) -> dict[str, Any]:
        """Get aggregate statistics from all providers."""
        with self._lock:
            stats = {"total_providers": len(self._providers), "providers": []}

            for i, provider in enumerate(self._providers):
                try:
                    if hasattr(provider, "get_statistics"):
                        provider_stats = provider.get_statistics()
                        provider_stats["priority"] = i
                        stats["providers"].append(provider_stats)
                    else:
                        stats["providers"].append(
                            {
                                "priority": i,
                                "type": type(provider).__name__,
                                "statistics": "not_available",
                            }
                        )
                except Exception as e:
                    logger.error(f"Error getting statistics from provider {i}: {e}")
                    stats["providers"].append({"priority": i, "error": str(e)})

            return stats


# Factory functions for creating providers
def create_default_provider(themes: Optional[dict[str, Theme]] = None) -> DefaultThemeProvider:
    """Create default theme provider.

    Args:
        themes: Optional initial themes

    Returns:
        Configured DefaultThemeProvider

    """
    return DefaultThemeProvider(themes)


def create_cached_provider(
    base_provider: ThemeProvider, cache_size: int = 1000
) -> CachedThemeProvider:
    """Create cached theme provider wrapping another provider.

    Args:
        base_provider: Provider to wrap with caching
        cache_size: Maximum cache size

    Returns:
        Configured CachedThemeProvider

    """
    return CachedThemeProvider(base_provider, cache_size)


def create_composite_provider(
    providers: Optional[list[ThemeProvider]] = None,
) -> CompositeThemeProvider:
    """Create composite provider combining multiple sources.

    Args:
        providers: List of providers in priority order

    Returns:
        Configured CompositeThemeProvider

    """
    return CompositeThemeProvider(providers)


__all__ = [
    "DefaultThemeProvider",
    "CachedThemeProvider",
    "CompositeThemeProvider",
    "ProviderStats",
    "create_default_provider",
    "create_cached_provider",
    "create_composite_provider",
]
