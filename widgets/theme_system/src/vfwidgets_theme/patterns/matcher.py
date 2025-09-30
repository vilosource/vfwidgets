"""
Pattern Recognition with Caching - Task 14

This module implements high-performance pattern matching that complements
the CSS selector system from Task 13. It provides:

- Glob patterns (e.g., "*Dialog", "Custom*")
- Regex patterns for advanced matching
- Custom pattern functions via plugins
- Priority-based resolution when multiple patterns match
- High-performance caching with >90% hit rate
- Integration with ThemeMapping's CSS selectors

Key Features:
- LRU caching for sub-millisecond pattern matching
- Plugin system for custom pattern types
- Priority system for conflict resolution
- Seamless integration with existing ThemeMapping
- Comprehensive performance monitoring
"""

import re
import glob
import fnmatch
import weakref
import threading
import time
from typing import (
    Any, Dict, List, Optional, Union, Set, Tuple, Callable,
    Pattern, NamedTuple, TYPE_CHECKING, Protocol
)
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from functools import lru_cache
from collections import OrderedDict, defaultdict

if TYPE_CHECKING:
    from ..widgets.base import ThemedWidget

from ..protocols import PropertyKey, PropertyValue, ThemeData
from ..errors import ThemeError
from ..logging import get_debug_logger

logger = get_debug_logger(__name__)


class PatternError(ThemeError):
    """Raised when pattern operations fail."""
    pass


class PatternType(Enum):
    """Types of patterns supported by the matcher."""
    GLOB = "glob"           # shell-style wildcards: *.txt, test_*
    REGEX = "regex"         # regular expressions: test_\d+
    CUSTOM = "custom"       # custom function patterns
    PLUGIN = "plugin"       # patterns from plugins


class PatternPriority(IntEnum):
    """Priority levels for pattern resolution."""
    LOWEST = 0
    LOW = 100
    NORMAL = 500
    HIGH = 800
    HIGHEST = 1000
    CRITICAL = 9999  # Always wins


class MatchResult(NamedTuple):
    """Result of a pattern match operation."""
    matched: bool
    score: float           # 0.0 to 1.0, higher is better match
    metadata: Dict[str, Any] = {}


class PatternFunction(Protocol):
    """Protocol for custom pattern functions."""

    def __call__(self, target: str, widget: 'ThemedWidget') -> MatchResult:
        """
        Check if target matches the pattern.

        Args:
            target: String to match against
            widget: Widget instance for context

        Returns:
            MatchResult indicating match status and quality
        """
        ...


@dataclass
class Pattern:
    """Represents a pattern with metadata."""
    pattern: str
    pattern_type: PatternType
    priority: PatternPriority = PatternPriority.NORMAL
    name: Optional[str] = None
    description: Optional[str] = None
    enabled: bool = True
    custom_function: Optional[PatternFunction] = None
    plugin_name: Optional[str] = None
    created_at: float = field(default_factory=time.time)

    def __post_init__(self):
        """Validate pattern after creation."""
        if self.pattern_type == PatternType.CUSTOM and self.custom_function is None:
            raise PatternError("Custom patterns require a custom_function")
        if self.pattern_type == PatternType.PLUGIN and self.plugin_name is None:
            raise PatternError("Plugin patterns require a plugin_name")


class LRUCache:
    """
    High-performance LRU cache optimized for pattern matching.

    Features:
    - Thread-safe operations
    - Configurable size limits
    - Performance monitoring
    - Efficient O(1) access and updates
    """

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._cache: OrderedDict[str, Any] = OrderedDict()
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache, moving it to end (most recent)."""
        with self._lock:
            if key in self._cache:
                # Move to end (most recently used)
                value = self._cache.pop(key)
                self._cache[key] = value
                self._hits += 1
                return value

            self._misses += 1
            return None

    def put(self, key: str, value: Any) -> None:
        """Put value in cache, evicting LRU if necessary."""
        with self._lock:
            if key in self._cache:
                # Update existing
                self._cache.pop(key)
                self._cache[key] = value
            else:
                # Add new
                if len(self._cache) >= self.max_size:
                    # Remove least recently used
                    self._cache.popitem(last=False)
                    self._evictions += 1

                self._cache[key] = value

    def clear(self) -> None:
        """Clear all cached entries."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            self._evictions = 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        with self._lock:
            total = self._hits + self._misses
            hit_rate = self._hits / total if total > 0 else 0.0

            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hits': self._hits,
                'misses': self._misses,
                'evictions': self._evictions,
                'hit_rate': hit_rate
            }


class PatternMatcher:
    """
    High-performance pattern matching engine with caching.

    This class complements the CSS selector system from Task 13 by providing
    additional pattern matching capabilities including glob patterns, regex,
    and custom functions.

    Features:
    - Multiple pattern types (glob, regex, custom, plugin)
    - LRU caching for sub-millisecond matching
    - Priority-based conflict resolution
    - Plugin system for extensibility
    - Comprehensive performance monitoring
    - Thread-safe operations
    """

    def __init__(self, cache_size: int = 1000, debug: bool = False):
        """
        Initialize pattern matcher.

        Args:
            cache_size: Maximum number of cached match results
            debug: Enable debug logging
        """
        self.debug = debug

        # Pattern storage
        self._patterns: List[Pattern] = []
        self._patterns_lock = threading.RLock()

        # High-performance caching
        self._match_cache = LRUCache(cache_size)
        self._pattern_cache = LRUCache(cache_size // 2)  # Compiled patterns

        # Plugin system
        self._plugins: Dict[str, 'PatternPlugin'] = {}

        # Performance tracking
        self._stats = {
            'patterns_matched': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'pattern_failures': 0,
            'average_match_time': 0.0,
            'total_match_time': 0.0,
            'match_count': 0,
        }
        self._stats_lock = threading.RLock()

        # Compiled regex cache
        self._regex_cache: Dict[str, re.Pattern] = {}
        self._regex_lock = threading.RLock()

        if self.debug:
            logger.debug("PatternMatcher initialized")

    def add_pattern(self, pattern: str, pattern_type: PatternType,
                   priority: PatternPriority = PatternPriority.NORMAL,
                   name: Optional[str] = None,
                   description: Optional[str] = None,
                   custom_function: Optional[PatternFunction] = None,
                   plugin_name: Optional[str] = None) -> int:
        """
        Add a pattern to the matcher.

        Args:
            pattern: Pattern string
            pattern_type: Type of pattern
            priority: Priority for conflict resolution
            name: Optional pattern name
            description: Optional description
            custom_function: Function for custom patterns
            plugin_name: Plugin name for plugin patterns

        Returns:
            Pattern index for later reference

        Raises:
            PatternError: If pattern is invalid
        """
        try:
            # Validate pattern
            self._validate_pattern(pattern, pattern_type, custom_function, plugin_name)

            # Create pattern object
            pattern_obj = Pattern(
                pattern=pattern,
                pattern_type=pattern_type,
                priority=priority,
                name=name,
                description=description,
                custom_function=custom_function,
                plugin_name=plugin_name
            )

            # Pre-compile regex patterns for performance
            if pattern_type == PatternType.REGEX:
                self._compile_regex_pattern(pattern)

            # Add to storage
            with self._patterns_lock:
                pattern_index = len(self._patterns)
                self._patterns.append(pattern_obj)

            # Clear caches since patterns changed
            self._clear_caches()

            if self.debug:
                logger.debug(f"Added pattern {pattern_index}: {pattern} ({pattern_type.value})")

            return pattern_index

        except Exception as e:
            with self._stats_lock:
                self._stats['pattern_failures'] += 1
            raise PatternError(f"Failed to add pattern '{pattern}': {e}")

    def remove_pattern(self, pattern_index: int) -> bool:
        """Remove a pattern by index."""
        try:
            with self._patterns_lock:
                if 0 <= pattern_index < len(self._patterns):
                    self._patterns[pattern_index] = None  # Mark as deleted
                    self._clear_caches()

                    if self.debug:
                        logger.debug(f"Removed pattern {pattern_index}")

                    return True
            return False

        except Exception as e:
            logger.error(f"Failed to remove pattern {pattern_index}: {e}")
            return False

    def match_patterns(self, target: str, widget: 'ThemedWidget',
                      context: Optional[Dict[str, Any]] = None) -> List[Tuple[int, Pattern, MatchResult]]:
        """
        Find all patterns that match the target string.

        Args:
            target: String to match against
            widget: Widget instance for context
            context: Additional context for matching

        Returns:
            List of (pattern_index, pattern, match_result) tuples
        """
        start_time = time.perf_counter()

        try:
            # Generate cache key
            cache_key = self._generate_cache_key(target, widget, context)

            # Check cache first
            cached_result = self._match_cache.get(cache_key)
            if cached_result is not None:
                with self._stats_lock:
                    self._stats['cache_hits'] += 1
                return cached_result

            with self._stats_lock:
                self._stats['cache_misses'] += 1

            # Perform actual matching
            matches = self._match_patterns_uncached(target, widget, context)

            # Cache result
            self._match_cache.put(cache_key, matches)

            # Update statistics
            match_time = time.perf_counter() - start_time
            with self._stats_lock:
                self._stats['patterns_matched'] += len(matches)
                self._stats['total_match_time'] += match_time
                self._stats['match_count'] += 1
                self._stats['average_match_time'] = (
                    self._stats['total_match_time'] / self._stats['match_count']
                )

            if self.debug and matches:
                logger.debug(f"Matched {len(matches)} patterns for '{target}' in {match_time*1000:.2f}ms")

            return matches

        except Exception as e:
            with self._stats_lock:
                self._stats['pattern_failures'] += 1
            logger.error(f"Pattern matching failed for '{target}': {e}")
            return []

    def get_best_match(self, target: str, widget: 'ThemedWidget',
                      context: Optional[Dict[str, Any]] = None) -> Optional[Tuple[int, Pattern, MatchResult]]:
        """
        Get the best matching pattern based on priority and match score.

        Args:
            target: String to match against
            widget: Widget instance for context
            context: Additional context for matching

        Returns:
            Best matching (pattern_index, pattern, match_result) or None
        """
        matches = self.match_patterns(target, widget, context)

        if not matches:
            return None

        # Sort by priority (descending), then by match score (descending)
        best_match = max(matches, key=lambda m: (m[1].priority.value, m[2].score))

        return best_match

    def add_plugin(self, plugin: 'PatternPlugin') -> None:
        """Add a pattern plugin."""
        self._plugins[plugin.name] = plugin

        if self.debug:
            logger.debug(f"Added plugin: {plugin.name}")

    def remove_plugin(self, plugin_name: str) -> bool:
        """Remove a pattern plugin."""
        if plugin_name in self._plugins:
            del self._plugins[plugin_name]
            # Disable patterns using this plugin
            with self._patterns_lock:
                for pattern in self._patterns:
                    if pattern and pattern.plugin_name == plugin_name:
                        pattern.enabled = False

            self._clear_caches()

            if self.debug:
                logger.debug(f"Removed plugin: {plugin_name}")

            return True
        return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        with self._stats_lock, self._patterns_lock:
            active_patterns = sum(1 for p in self._patterns if p is not None and p.enabled)

            return {
                'total_patterns': len(self._patterns),
                'active_patterns': active_patterns,
                'plugin_count': len(self._plugins),
                'match_cache_stats': self._match_cache.get_stats(),
                'pattern_cache_stats': self._pattern_cache.get_stats(),
                'performance_stats': self._stats.copy(),
            }

    def clear_caches(self) -> None:
        """Clear all caches."""
        self._clear_caches()

    def benchmark_performance(self, iterations: int = 1000) -> Dict[str, float]:
        """
        Benchmark pattern matching performance.

        Args:
            iterations: Number of test iterations

        Returns:
            Performance metrics in milliseconds
        """
        # Create test widget
        test_widget = MockWidget("benchmark_widget")
        test_targets = [
            "TestWidget",
            "CustomDialog",
            "main_button",
            "user_input_field",
            "status_label_01",
        ]

        # Warm up cache
        for target in test_targets:
            self.match_patterns(target, test_widget)

        # Benchmark
        start_time = time.perf_counter()

        for i in range(iterations):
            target = test_targets[i % len(test_targets)]
            self.match_patterns(target, test_widget)

        total_time = (time.perf_counter() - start_time) * 1000  # Convert to ms
        avg_time = total_time / iterations

        return {
            'total_time_ms': total_time,
            'average_time_ms': avg_time,
            'iterations': iterations,
            'patterns_per_second': iterations / (total_time / 1000),
        }

    # Private methods

    def _match_patterns_uncached(self, target: str, widget: 'ThemedWidget',
                                context: Optional[Dict[str, Any]] = None) -> List[Tuple[int, Pattern, MatchResult]]:
        """Perform actual pattern matching without caching."""
        matches = []

        # Pre-filter enabled patterns for better performance
        active_patterns = []
        with self._patterns_lock:
            for i, pattern in enumerate(self._patterns):
                if pattern is not None and pattern.enabled:
                    active_patterns.append((i, pattern))

        # Match patterns without holding the lock
        for i, pattern in active_patterns:
            try:
                result = self._match_single_pattern(pattern, target, widget, context)
                if result.matched:
                    matches.append((i, pattern, result))

            except Exception as e:
                if self.debug:
                    logger.warning(f"Pattern {i} matching error: {e}")

        return matches

    def _match_single_pattern(self, pattern: Pattern, target: str,
                            widget: 'ThemedWidget', context: Optional[Dict[str, Any]] = None) -> MatchResult:
        """Match a single pattern against the target."""
        try:
            if pattern.pattern_type == PatternType.GLOB:
                return self._match_glob_pattern(pattern.pattern, target)

            elif pattern.pattern_type == PatternType.REGEX:
                return self._match_regex_pattern(pattern.pattern, target)

            elif pattern.pattern_type == PatternType.CUSTOM:
                return pattern.custom_function(target, widget)

            elif pattern.pattern_type == PatternType.PLUGIN:
                plugin = self._plugins.get(pattern.plugin_name)
                if plugin:
                    return plugin.match(pattern.pattern, target, widget, context)
                else:
                    logger.warning(f"Plugin '{pattern.plugin_name}' not found")
                    return MatchResult(False, 0.0)

            else:
                return MatchResult(False, 0.0)

        except Exception as e:
            if self.debug:
                logger.warning(f"Pattern matching error: {e}")
            return MatchResult(False, 0.0)

    def _match_glob_pattern(self, pattern: str, target: str) -> MatchResult:
        """Match using shell-style glob patterns."""
        matched = fnmatch.fnmatch(target, pattern)

        # Calculate match score based on specificity
        score = 0.0
        if matched:
            # Higher score for more specific patterns (fewer wildcards)
            wildcards = pattern.count('*') + pattern.count('?')
            specificity = max(0, len(pattern) - wildcards) / len(pattern) if pattern else 0
            score = specificity

        return MatchResult(matched, score)

    def _match_regex_pattern(self, pattern: str, target: str) -> MatchResult:
        """Match using regular expressions."""
        try:
            # Get compiled regex from cache
            compiled_regex = self._get_compiled_regex(pattern)
            match = compiled_regex.search(target)

            if match:
                # Score based on match length relative to target length
                score = len(match.group(0)) / len(target) if target else 0
                return MatchResult(True, score, {'match': match})
            else:
                return MatchResult(False, 0.0)

        except Exception as e:
            if self.debug:
                logger.warning(f"Regex matching error: {e}")
            return MatchResult(False, 0.0)

    def _get_compiled_regex(self, pattern: str) -> re.Pattern:
        """Get compiled regex pattern from cache."""
        with self._regex_lock:
            if pattern not in self._regex_cache:
                self._regex_cache[pattern] = re.compile(pattern)
            return self._regex_cache[pattern]

    def _compile_regex_pattern(self, pattern: str) -> None:
        """Pre-compile regex pattern for performance."""
        try:
            self._get_compiled_regex(pattern)
        except re.error as e:
            raise PatternError(f"Invalid regex pattern '{pattern}': {e}")

    def _validate_pattern(self, pattern: str, pattern_type: PatternType,
                         custom_function: Optional[PatternFunction] = None,
                         plugin_name: Optional[str] = None) -> None:
        """Validate a pattern before adding it."""
        if not pattern:
            raise PatternError("Pattern cannot be empty")

        if pattern_type == PatternType.REGEX:
            try:
                re.compile(pattern)
            except re.error as e:
                raise PatternError(f"Invalid regex pattern: {e}")

        elif pattern_type == PatternType.CUSTOM:
            if custom_function is None:
                raise PatternError("Custom patterns require a custom_function")

        elif pattern_type == PatternType.PLUGIN:
            if plugin_name is None:
                raise PatternError("Plugin patterns require a plugin_name")
            if plugin_name not in self._plugins:
                raise PatternError(f"Plugin '{plugin_name}' not found")

    def _generate_cache_key(self, target: str, widget: 'ThemedWidget',
                          context: Optional[Dict[str, Any]] = None) -> str:
        """Generate a cache key for pattern matching."""
        # Include widget context for caching
        widget_sig = f"{type(widget).__name__}:{getattr(widget, '_widget_id', id(widget))}"

        # Include context if provided
        context_sig = ""
        if context:
            context_sig = str(hash(frozenset(context.items())))

        return f"{target}::{widget_sig}::{context_sig}"

    def _clear_caches(self) -> None:
        """Clear all caches."""
        self._match_cache.clear()
        self._pattern_cache.clear()

        with self._regex_lock:
            self._regex_cache.clear()


class MockWidget:
    """Mock widget for testing."""

    def __init__(self, widget_id: str):
        self._widget_id = widget_id
        self._theme_classes = set()
        self._theme_attributes = {}

    def add_class(self, class_name: str):
        self._theme_classes.add(class_name)
        return self

    def set_attribute(self, name: str, value: str):
        self._theme_attributes[name] = value
        return self


# Utility functions for common patterns

def glob_pattern(pattern: str) -> Tuple[str, PatternType]:
    """Create a glob pattern tuple."""
    return (pattern, PatternType.GLOB)

def regex_pattern(pattern: str) -> Tuple[str, PatternType]:
    """Create a regex pattern tuple."""
    return (pattern, PatternType.REGEX)

def widget_name_pattern(name: str) -> str:
    """Create a pattern that matches widget names."""
    return f"*{name}*"

def widget_type_pattern(widget_type: str) -> str:
    """Create a pattern that matches widget types."""
    return f"{widget_type}*"

def dialog_pattern() -> str:
    """Create a pattern that matches all dialogs."""
    return "*Dialog*"

def button_pattern() -> str:
    """Create a pattern that matches all buttons."""
    return "*Button*"


__all__ = [
    "PatternMatcher",
    "PatternType",
    "PatternPriority",
    "Pattern",
    "MatchResult",
    "PatternFunction",
    "PatternError",
    "LRUCache",
    "glob_pattern",
    "regex_pattern",
    "widget_name_pattern",
    "widget_type_pattern",
    "dialog_pattern",
    "button_pattern",
]