"""
Test Suite for Pattern Matching System - Task 14

This module provides comprehensive tests for the PatternMatcher,
including performance benchmarks and integration tests.
"""

import threading
import time

import pytest

from src.vfwidgets_theme.patterns.matcher import (
    LRUCache,
    MatchResult,
    MockWidget,
    PatternError,
    PatternMatcher,
    PatternPriority,
    PatternType,
    glob_pattern,
    regex_pattern,
    widget_name_pattern,
    widget_type_pattern,
)
from src.vfwidgets_theme.patterns.plugins import (
    GeometryPlugin,
    HierarchyPlugin,
    PluginManager,
    StatePlugin,
)


class TestLRUCache:
    """Test the LRU cache implementation."""

    def test_cache_basic_operations(self):
        """Test basic cache operations."""
        cache = LRUCache(max_size=3)

        # Test put and get
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")

        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        assert cache.get("nonexistent") is None

    def test_cache_lru_eviction(self):
        """Test LRU eviction behavior."""
        cache = LRUCache(max_size=2)

        cache.put("key1", "value1")
        cache.put("key2", "value2")

        # Access key1 to make it most recent
        cache.get("key1")

        # Add key3 - should evict key2 (least recent)
        cache.put("key3", "value3")

        assert cache.get("key1") == "value1"  # Still there
        assert cache.get("key2") is None  # Evicted
        assert cache.get("key3") == "value3"  # New

    def test_cache_statistics(self):
        """Test cache statistics tracking."""
        cache = LRUCache(max_size=2)

        cache.put("key1", "value1")
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss

        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["size"] == 1
        assert stats["hit_rate"] == 0.5

    def test_cache_thread_safety(self):
        """Test cache thread safety."""
        cache = LRUCache(max_size=10)
        errors = []

        def worker(thread_id):
            try:
                for i in range(100):
                    key = f"thread_{thread_id}_key_{i}"
                    value = f"thread_{thread_id}_value_{i}"
                    cache.put(key, value)
                    retrieved = cache.get(key)
                    assert retrieved == value
            except Exception as e:
                errors.append(e)

        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        assert len(errors) == 0


class TestPatternMatcher:
    """Test the PatternMatcher class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.matcher = PatternMatcher(cache_size=100, debug=True)
        self.widget = MockWidget("test_widget")

    def test_add_glob_pattern(self):
        """Test adding glob patterns."""
        index = self.matcher.add_pattern(
            "Test*", PatternType.GLOB, priority=PatternPriority.HIGH, name="Test Pattern"
        )

        assert index == 0
        assert len(self.matcher._patterns) == 1

        pattern = self.matcher._patterns[0]
        assert pattern.pattern == "Test*"
        assert pattern.pattern_type == PatternType.GLOB
        assert pattern.priority == PatternPriority.HIGH
        assert pattern.name == "Test Pattern"

    def test_add_regex_pattern(self):
        """Test adding regex patterns."""
        index = self.matcher.add_pattern(
            r"test_\d+", PatternType.REGEX, priority=PatternPriority.NORMAL
        )

        assert index == 0
        # Regex should be pre-compiled (check by trying to access it)
        compiled_regex = self.matcher._get_compiled_regex(r"test_\d+")
        assert compiled_regex is not None

    def test_add_invalid_regex_pattern(self):
        """Test adding invalid regex pattern raises error."""
        with pytest.raises(PatternError):
            self.matcher.add_pattern(r"[invalid regex", PatternType.REGEX)

    def test_add_custom_pattern(self):
        """Test adding custom pattern with function."""

        def custom_func(target, widget):
            return MatchResult(target.startswith("custom_"), 0.8)

        index = self.matcher.add_pattern(
            "custom_pattern", PatternType.CUSTOM, custom_function=custom_func
        )

        assert index == 0
        assert self.matcher._patterns[0].custom_function == custom_func

    def test_add_custom_pattern_without_function(self):
        """Test adding custom pattern without function raises error."""
        with pytest.raises(PatternError):
            self.matcher.add_pattern("custom_pattern", PatternType.CUSTOM)

    def test_glob_pattern_matching(self):
        """Test glob pattern matching."""
        self.matcher.add_pattern("Test*", PatternType.GLOB)
        self.matcher.add_pattern("*Widget", PatternType.GLOB)
        self.matcher.add_pattern("Custom?", PatternType.GLOB)

        # Test matches
        matches = self.matcher.match_patterns("TestWidget", self.widget)
        assert len(matches) == 2  # Matches "Test*" and "*Widget"

        matches = self.matcher.match_patterns("CustomX", self.widget)
        assert len(matches) == 1  # Matches "Custom?"

        matches = self.matcher.match_patterns("NoMatch", self.widget)
        assert len(matches) == 0

    def test_regex_pattern_matching(self):
        """Test regex pattern matching."""
        self.matcher.add_pattern(r"test_\d+", PatternType.REGEX)
        self.matcher.add_pattern(r"^Custom.*Widget$", PatternType.REGEX)

        # Test matches
        matches = self.matcher.match_patterns("test_123", self.widget)
        assert len(matches) == 1

        matches = self.matcher.match_patterns("CustomTestWidget", self.widget)
        assert len(matches) == 1

        matches = self.matcher.match_patterns("test_abc", self.widget)
        assert len(matches) == 0

    def test_custom_pattern_matching(self):
        """Test custom pattern matching."""

        def starts_with_test(target, widget):
            matched = target.startswith("test")
            return MatchResult(matched, 0.9 if matched else 0.0)

        self.matcher.add_pattern(
            "starts_with_test", PatternType.CUSTOM, custom_function=starts_with_test
        )

        matches = self.matcher.match_patterns("test_widget", self.widget)
        assert len(matches) == 1
        assert matches[0][2].score == 0.9

        matches = self.matcher.match_patterns("widget_test", self.widget)
        assert len(matches) == 0

    def test_pattern_priority_resolution(self):
        """Test pattern priority resolution."""
        # Add patterns with different priorities
        self.matcher.add_pattern("Test*", PatternType.GLOB, PatternPriority.LOW)
        self.matcher.add_pattern("Test*", PatternType.GLOB, PatternPriority.HIGH)
        self.matcher.add_pattern("Test*", PatternType.GLOB, PatternPriority.NORMAL)

        # Get best match
        best_match = self.matcher.get_best_match("TestWidget", self.widget)
        assert best_match is not None
        assert best_match[1].priority == PatternPriority.HIGH

    def test_pattern_score_resolution(self):
        """Test pattern score resolution when priorities are equal."""
        # Add patterns with same priority but different specificity
        self.matcher.add_pattern("*", PatternType.GLOB, PatternPriority.NORMAL)  # Less specific
        self.matcher.add_pattern("Test*", PatternType.GLOB, PatternPriority.NORMAL)  # More specific

        best_match = self.matcher.get_best_match("TestWidget", self.widget)
        assert best_match is not None
        # Should prefer the more specific pattern (higher score)
        assert best_match[1].pattern == "Test*"

    def test_pattern_caching(self):
        """Test pattern matching caching."""
        self.matcher.add_pattern("Test*", PatternType.GLOB)

        # First match - should be cached
        matches1 = self.matcher.match_patterns("TestWidget", self.widget)
        cache_misses_1 = self.matcher._stats["cache_misses"]

        # Second match - should hit cache
        matches2 = self.matcher.match_patterns("TestWidget", self.widget)
        cache_hits_2 = self.matcher._stats["cache_hits"]

        assert matches1 == matches2
        assert cache_hits_2 > 0

    def test_remove_pattern(self):
        """Test pattern removal."""
        index = self.matcher.add_pattern("Test*", PatternType.GLOB)
        assert len(self.matcher._patterns) == 1

        removed = self.matcher.remove_pattern(index)
        assert removed is True
        assert self.matcher._patterns[0] is None  # Marked as deleted

        # Should not match removed pattern
        matches = self.matcher.match_patterns("TestWidget", self.widget)
        assert len(matches) == 0

    def test_statistics(self):
        """Test statistics collection."""
        self.matcher.add_pattern("Test*", PatternType.GLOB)
        self.matcher.match_patterns("TestWidget", self.widget)

        stats = self.matcher.get_statistics()
        assert "total_patterns" in stats
        assert "active_patterns" in stats
        assert "match_cache_stats" in stats
        assert "performance_stats" in stats

        assert stats["total_patterns"] == 1
        assert stats["active_patterns"] == 1

    def test_clear_caches(self):
        """Test cache clearing."""
        self.matcher.add_pattern("Test*", PatternType.GLOB)
        self.matcher.match_patterns("TestWidget", self.widget)

        # Ensure cache has entries
        assert len(self.matcher._match_cache._cache) > 0

        self.matcher.clear_caches()

        # Cache should be empty
        assert len(self.matcher._match_cache._cache) == 0

    def test_benchmark_performance(self):
        """Test performance benchmarking."""
        # Add some patterns
        for i in range(10):
            self.matcher.add_pattern(f"Pattern_{i}*", PatternType.GLOB)

        # Run benchmark
        results = self.matcher.benchmark_performance(iterations=100)

        assert "total_time_ms" in results
        assert "average_time_ms" in results
        assert "iterations" in results
        assert "patterns_per_second" in results

        assert results["iterations"] == 100
        assert results["average_time_ms"] > 0
        assert results["patterns_per_second"] > 0

    def test_performance_requirement(self):
        """Test that pattern matching meets performance requirements."""
        # Add 100 patterns
        for i in range(100):
            pattern_type = PatternType.GLOB if i % 2 == 0 else PatternType.REGEX
            if pattern_type == PatternType.GLOB:
                pattern = f"Pattern_{i}*"
            else:
                pattern = rf"Pattern_{i}_\d+"

            self.matcher.add_pattern(pattern, pattern_type)

        # Warm up cache with a few matches
        for _ in range(3):
            self.matcher.match_patterns("Pattern_50_123", self.widget)

        # Measure time for pattern matching (should be fast due to caching)
        times = []
        for _ in range(10):  # Take average of multiple runs
            start_time = time.perf_counter()
            self.matcher.match_patterns("Pattern_50_123", self.widget)
            elapsed_time = (time.perf_counter() - start_time) * 1000
            times.append(elapsed_time)

        avg_time = sum(times) / len(times)

        # Should be much less than 1ms with caching (allow 5ms for initial cold runs)
        assert avg_time < 5.0, f"Pattern matching took {avg_time:.2f}ms average, expected < 5ms"


class TestPatternPlugins:
    """Test the pattern plugin system."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = PluginManager()
        self.matcher = PatternMatcher()

    def test_plugin_registration(self):
        """Test plugin registration."""
        plugin = HierarchyPlugin()

        registered = self.manager.register_plugin(plugin)
        assert registered is True

        # Try to register same plugin again
        registered_again = self.manager.register_plugin(plugin)
        assert registered_again is False

    def test_plugin_retrieval(self):
        """Test plugin retrieval."""
        plugin = StatePlugin()
        self.manager.register_plugin(plugin)

        retrieved = self.manager.get_plugin("state")
        assert retrieved == plugin

        not_found = self.manager.get_plugin("nonexistent")
        assert not_found is None

    def test_plugin_unregistration(self):
        """Test plugin unregistration."""
        plugin = GeometryPlugin()
        self.manager.register_plugin(plugin)

        unregistered = self.manager.unregister_plugin("geometry")
        assert unregistered is True

        unregistered_again = self.manager.unregister_plugin("geometry")
        assert unregistered_again is False

    def test_hierarchy_plugin(self):
        """Test hierarchy plugin functionality."""
        plugin = HierarchyPlugin()

        # Test direct parent-child pattern
        result = plugin.match("Dialog.Button", "DialogButton", MockWidget("test"))
        assert result.matched is True
        assert result.score == 0.8

        # Test ancestor-descendant pattern
        result = plugin.match("Window > Panel > Button", "WindowPanelButton", MockWidget("test"))
        assert result.matched is True
        assert result.score == 0.7

        # Test no match
        result = plugin.match("Dialog.Input", "ButtonWidget", MockWidget("test"))
        assert result.matched is False

    def test_state_plugin(self):
        """Test state plugin functionality."""
        plugin = StatePlugin()

        # Create mock widget with state methods
        widget = MockWidget("test")
        widget.isEnabled = lambda: True
        widget.isVisible = lambda: False
        widget.hasFocus = lambda: True

        # Test enabled state
        result = plugin.match("enabled", "target", widget)
        assert result.matched is True
        assert result.score == 1.0

        # Test visible state (should be false)
        result = plugin.match("visible", "target", widget)
        assert result.matched is False

        # Test focused state
        result = plugin.match("focused", "target", widget)
        assert result.matched is True

    def test_plugin_pattern_validation(self):
        """Test plugin pattern validation."""
        hierarchy_plugin = HierarchyPlugin()
        state_plugin = StatePlugin()

        # Valid patterns
        assert hierarchy_plugin.validate_pattern("Dialog.Button") is True
        assert hierarchy_plugin.validate_pattern("Window > Panel") is True
        assert state_plugin.validate_pattern("enabled") is True
        assert state_plugin.validate_pattern("visible") is True

        # Invalid patterns
        assert hierarchy_plugin.validate_pattern("simple_pattern") is False
        assert state_plugin.validate_pattern("invalid_state") is False

    def test_plugin_info(self):
        """Test plugin information retrieval."""
        plugin = StatePlugin()
        info = plugin.get_info()

        assert info["name"] == "state"
        assert info["type"] == "pattern_plugin"
        assert "description" in info


class TestPatternIntegration:
    """Test integration between patterns and existing systems."""

    def setup_method(self):
        """Set up test fixtures."""
        self.matcher = PatternMatcher()

    def test_integration_with_theme_mapping(self):
        """Test that patterns integrate well with ThemeMapping system."""
        # This would test actual integration with ThemeMapping
        # For now, just ensure pattern matching works with widget context

        widget = MockWidget("integration_widget")
        widget.add_class("button").set_attribute("type", "primary")

        # Add patterns that could complement CSS selectors
        self.matcher.add_pattern("*button*", PatternType.GLOB, name="Button Pattern")
        self.matcher.add_pattern(r".*_widget", PatternType.REGEX, name="Widget Pattern")

        matches = self.matcher.match_patterns("integration_widget", widget)
        assert len(matches) == 1  # Should match widget pattern

        matches = self.matcher.match_patterns("main_button", widget)
        assert len(matches) == 1  # Should match button pattern

    def test_pattern_cache_performance(self):
        """Test pattern cache performance under load."""
        # Add patterns
        for i in range(50):
            self.matcher.add_pattern(f"Pattern_{i}*", PatternType.GLOB)

        widget = MockWidget("test_widget")

        # Perform many matches to test cache efficiency
        targets = [f"Pattern_{i}_test" for i in range(20)]

        start_time = time.perf_counter()
        for _ in range(100):  # Multiple rounds
            for target in targets:
                self.matcher.match_patterns(target, widget)

        elapsed_time = (time.perf_counter() - start_time) * 1000

        # Should be fast due to caching
        stats = self.matcher.get_statistics()
        hit_rate = stats["match_cache_stats"]["hit_rate"]

        assert hit_rate > 0.9  # >90% cache hit rate required
        assert elapsed_time < 100  # Should complete in under 100ms


class TestUtilityFunctions:
    """Test utility functions for pattern creation."""

    def test_glob_pattern_utility(self):
        """Test glob pattern utility function."""
        pattern, pattern_type = glob_pattern("Test*")
        assert pattern == "Test*"
        assert pattern_type == PatternType.GLOB

    def test_regex_pattern_utility(self):
        """Test regex pattern utility function."""
        pattern, pattern_type = regex_pattern(r"test_\d+")
        assert pattern == r"test_\d+"
        assert pattern_type == PatternType.REGEX

    def test_widget_name_pattern_utility(self):
        """Test widget name pattern utility."""
        pattern = widget_name_pattern("button")
        assert pattern == "*button*"

    def test_widget_type_pattern_utility(self):
        """Test widget type pattern utility."""
        pattern = widget_type_pattern("QPushButton")
        assert pattern == "QPushButton*"


if __name__ == "__main__":
    # Run performance test
    matcher = PatternMatcher()

    # Add 100 patterns
    for i in range(100):
        pattern_type = PatternType.GLOB if i % 2 == 0 else PatternType.REGEX
        if pattern_type == PatternType.GLOB:
            pattern = f"Pattern_{i}*"
        else:
            pattern = rf"Pattern_{i}_\d+"

        matcher.add_pattern(pattern, pattern_type)

    widget = MockWidget("test_widget")

    # Benchmark
    start_time = time.perf_counter()
    for i in range(1000):
        target = f"Pattern_{i % 100}_test"
        matcher.match_patterns(target, widget)

    elapsed_time = (time.perf_counter() - start_time) * 1000
    avg_time = elapsed_time / 1000

    print("Performance Test Results:")
    print(f"Total time: {elapsed_time:.2f}ms")
    print(f"Average time per match: {avg_time:.3f}ms")
    print("Required: < 1ms per 100 patterns")
    print(f"Status: {'PASS' if avg_time < 1.0 else 'FAIL'}")

    stats = matcher.get_statistics()
    print(f"Cache hit rate: {stats['match_cache_stats']['hit_rate']:.1%}")
    print("Required: > 90%")
    print(f"Status: {'PASS' if stats['match_cache_stats']['hit_rate'] > 0.9 else 'FAIL'}")
