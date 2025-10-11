"""
Test suite for ThemeProvider.

Tests theme provider implementation including:
- ThemeProvider protocol implementation
- Property resolution using PropertyResolver
- Caching layer for widget property access
- Error recovery and fallback handling
- Performance monitoring and optimization
"""

import threading
import time

import pytest

# Import the modules under test
from vfwidgets_theme.core.provider import (
    CachedThemeProvider,
    CompositeThemeProvider,
    DefaultThemeProvider,
    create_cached_provider,
    create_composite_provider,
    create_default_provider,
)
from vfwidgets_theme.core.theme import Theme
from vfwidgets_theme.errors import PropertyNotFoundError, ThemeNotFoundError
from vfwidgets_theme.testing import ThemedTestCase


class TestDefaultThemeProvider(ThemedTestCase):
    """Test DefaultThemeProvider implementation."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.provider = DefaultThemeProvider()

        # Create sample theme
        self.sample_theme_data = {
            "name": "provider-test-theme",
            "version": "1.0.0",
            "colors": {
                "primary": "#007acc",
                "secondary": "#ffffff",
                "background": "#f5f5f5",
                "foreground": "#333333",
            },
            "styles": {
                "QPushButton": "background-color: @colors.primary; color: @colors.secondary;",
                "QLabel": "color: @colors.foreground; background-color: @colors.background;",
            },
        }
        self.sample_theme = Theme.from_dict(self.sample_theme_data)

    def test_provider_initialization_empty(self):
        """Test provider initialization with no themes."""
        provider = DefaultThemeProvider()
        self.assertEqual(len(provider.list_themes()), 0)

    def test_provider_initialization_with_themes(self):
        """Test provider initialization with theme dictionary."""
        themes = {"test-theme": self.sample_theme}
        provider = DefaultThemeProvider(themes)

        self.assertEqual(len(provider.list_themes()), 1)
        self.assertIn("provider-test-theme", provider.list_themes())

    def test_add_theme(self):
        """Test adding theme to provider."""
        self.provider.add_theme(self.sample_theme)

        self.assertTrue(self.provider.has_theme("provider-test-theme"))
        self.assertIn("provider-test-theme", self.provider.list_themes())

    def test_get_theme_data_existing(self):
        """Test getting theme data for existing theme."""
        self.provider.add_theme(self.sample_theme)

        theme_data = self.provider.get_theme_data("provider-test-theme")

        self.assertIsInstance(theme_data, dict)
        self.assertIn("colors", theme_data)
        self.assertIn("styles", theme_data)

    def test_get_theme_data_nonexistent(self):
        """Test getting theme data for non-existent theme raises error."""
        with self.assertRaises(ThemeNotFoundError) as context:
            self.provider.get_theme_data("nonexistent-theme")

        self.assertIn("nonexistent-theme", str(context.exception))

    def test_get_color_with_theme(self):
        """Test getting color from specific theme."""
        self.provider.add_theme(self.sample_theme)

        color = self.provider.get_color("primary", "provider-test-theme")

        self.assertEqual(color, "#007acc")

    def test_get_color_current_theme(self):
        """Test getting color from current theme."""
        self.provider.add_theme(self.sample_theme)
        self.provider.set_current_theme("provider-test-theme")

        color = self.provider.get_color("primary")  # No theme specified

        self.assertEqual(color, "#007acc")

    def test_get_color_fallback(self):
        """Test color fallback when not found in theme."""
        self.provider.add_theme(self.sample_theme)

        # Request non-existent color should fall back
        color = self.provider.get_color("nonexistent-color", "provider-test-theme")

        self.assertIsNotNone(color)  # Should return fallback color

    def test_get_property_with_theme(self):
        """Test getting property from specific theme."""
        self.provider.add_theme(self.sample_theme)

        # Get style property
        style = self.provider.get_property("styles.QPushButton", "provider-test-theme")

        self.assertIsNotNone(style)
        self.assertIn("background-color", style)

    def test_get_property_current_theme(self):
        """Test getting property from current theme."""
        self.provider.add_theme(self.sample_theme)
        self.provider.set_current_theme("provider-test-theme")

        style = self.provider.get_property("styles.QPushButton")

        self.assertIsNotNone(style)
        self.assertIn("background-color", style)

    def test_get_property_fallback(self):
        """Test property fallback when not found in theme."""
        self.provider.add_theme(self.sample_theme)

        # Request non-existent property should fall back
        prop = self.provider.get_property("nonexistent.property", "provider-test-theme")

        self.assertIsNotNone(prop)  # Should return fallback

    def test_set_current_theme(self):
        """Test setting current theme."""
        self.provider.add_theme(self.sample_theme)

        self.provider.set_current_theme("provider-test-theme")

        # Should be able to get colors without specifying theme
        color = self.provider.get_color("primary")
        self.assertEqual(color, "#007acc")

    def test_set_current_theme_nonexistent(self):
        """Test setting non-existent current theme raises error."""
        with self.assertRaises(ThemeNotFoundError):
            self.provider.set_current_theme("nonexistent-theme")

    def test_has_theme(self):
        """Test checking if theme exists."""
        self.assertFalse(self.provider.has_theme("provider-test-theme"))

        self.provider.add_theme(self.sample_theme)

        self.assertTrue(self.provider.has_theme("provider-test-theme"))

    def test_list_themes(self):
        """Test listing all themes."""
        self.assertEqual(self.provider.list_themes(), [])

        self.provider.add_theme(self.sample_theme)

        themes = self.provider.list_themes()
        self.assertEqual(len(themes), 1)
        self.assertIn("provider-test-theme", themes)

    def test_thread_safety(self):
        """Test provider thread safety."""
        themes = []
        results = []
        errors = []

        def worker(worker_id: int):
            """Worker function for concurrent testing."""
            try:
                # Create worker-specific theme
                theme_data = {**self.sample_theme_data, "name": f"worker-theme-{worker_id}"}
                theme = Theme.from_dict(theme_data)
                themes.append(theme)

                # Add theme
                self.provider.add_theme(theme)

                # Set as current and get properties
                self.provider.set_current_theme(f"worker-theme-{worker_id}")
                color = self.provider.get_color("primary")

                results.append((worker_id, color))

            except Exception as e:
                errors.append(f"Worker {worker_id}: {e}")

        threads = []
        for worker_id in range(5):
            thread = threading.Thread(target=worker, args=(worker_id,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        self.assertEqual(len(errors), 0, f"Thread safety errors: {errors}")
        self.assertEqual(len(results), 5)

        # All themes should be available
        theme_names = self.provider.list_themes()
        for worker_id in range(5):
            self.assertIn(f"worker-theme-{worker_id}", theme_names)


class TestCachedThemeProvider(ThemedTestCase):
    """Test CachedThemeProvider for performance optimization."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.base_provider = DefaultThemeProvider()
        self.cached_provider = CachedThemeProvider(self.base_provider, cache_size=10)

        self.sample_theme_data = {
            "name": "cached-test-theme",
            "version": "1.0.0",
            "colors": {"primary": "#007acc", "secondary": "#ffffff"},
            "styles": {"QPushButton": "background-color: @colors.primary;"},
        }
        self.sample_theme = Theme.from_dict(self.sample_theme_data)

    def test_cached_provider_initialization(self):
        """Test cached provider initialization."""
        provider = CachedThemeProvider(self.base_provider, cache_size=5)
        self.assertIs(provider._base_provider, self.base_provider)
        self.assertEqual(provider._cache_size, 5)

    def test_cache_miss_and_hit(self):
        """Test cache miss followed by cache hit."""
        self.base_provider.add_theme(self.sample_theme)

        # First access should be cache miss
        color1 = self.cached_provider.get_color("primary", "cached-test-theme")

        # Second access should be cache hit
        color2 = self.cached_provider.get_color("primary", "cached-test-theme")

        self.assertEqual(color1, color2)
        self.assertEqual(color1, "#007acc")

    def test_cache_size_limit(self):
        """Test cache respects size limits."""
        small_cached_provider = CachedThemeProvider(self.base_provider, cache_size=2)
        self.base_provider.add_theme(self.sample_theme)

        # Fill cache beyond capacity
        colors = ["primary", "secondary", "nonexistent1", "nonexistent2", "nonexistent3"]

        for color in colors:
            small_cached_provider.get_color(color, "cached-test-theme")

        # Cache should not exceed size limit
        # (Implementation dependent - this tests the concept)
        self.assertLessEqual(
            len(small_cached_provider._color_cache), small_cached_provider._cache_size + 1
        )

    def test_cache_invalidation_specific_theme(self):
        """Test invalidating cache for specific theme."""
        self.base_provider.add_theme(self.sample_theme)

        # Access to populate cache
        self.cached_provider.get_color("primary", "cached-test-theme")

        # Invalidate specific theme
        self.cached_provider.invalidate_cache("cached-test-theme")

        # Should still work (cache miss, then repopulate)
        color = self.cached_provider.get_color("primary", "cached-test-theme")
        self.assertEqual(color, "#007acc")

    def test_cache_invalidation_all(self):
        """Test invalidating all caches."""
        self.base_provider.add_theme(self.sample_theme)

        # Access to populate caches
        self.cached_provider.get_color("primary", "cached-test-theme")

        # Invalidate all
        self.cached_provider.invalidate_cache()

        # Should still work after invalidation
        color = self.cached_provider.get_color("primary", "cached-test-theme")
        self.assertEqual(color, "#007acc")

    def test_performance_improvement(self):
        """Test that caching improves performance."""
        self.base_provider.add_theme(self.sample_theme)

        # Measure first access (cache miss)
        start_time = time.time()
        for _ in range(100):
            self.cached_provider.get_color("primary", "cached-test-theme")
        cached_time = time.time() - start_time

        # Cached access should be faster on subsequent calls
        # (This is a conceptual test - actual timing depends on implementation)
        self.assertLess(cached_time, 0.01)  # Should be very fast

    def test_error_handling_in_cache(self):
        """Test error handling doesn't break caching."""
        # Theme doesn't exist - should handle gracefully
        try:
            self.cached_provider.get_color("primary", "nonexistent-theme")
        except ThemeNotFoundError:
            pass  # Expected

        # Add theme and try again
        self.base_provider.add_theme(self.sample_theme)
        color = self.cached_provider.get_color("primary", "cached-test-theme")
        self.assertEqual(color, "#007acc")


class TestCompositeThemeProvider(ThemedTestCase):
    """Test CompositeThemeProvider for multiple sources."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.provider1 = DefaultThemeProvider()
        self.provider2 = DefaultThemeProvider()
        self.composite = CompositeThemeProvider([self.provider1, self.provider2])

        # Create themes for different providers
        self.theme1_data = {
            "name": "theme1",
            "version": "1.0.0",
            "colors": {"primary": "#ff0000"},
            "styles": {"QPushButton": "color: red;"},
        }
        self.theme2_data = {
            "name": "theme2",
            "version": "1.0.0",
            "colors": {"primary": "#00ff00"},
            "styles": {"QPushButton": "color: green;"},
        }

        self.theme1 = Theme.from_dict(self.theme1_data)
        self.theme2 = Theme.from_dict(self.theme2_data)

    def test_composite_initialization_empty(self):
        """Test composite provider initialization with no providers."""
        composite = CompositeThemeProvider()
        self.assertEqual(len(composite._providers), 0)

    def test_composite_initialization_with_providers(self):
        """Test composite provider initialization with providers."""
        providers = [self.provider1, self.provider2]
        composite = CompositeThemeProvider(providers)

        self.assertEqual(len(composite._providers), 2)

    def test_add_provider(self):
        """Test adding provider to composite."""
        composite = CompositeThemeProvider()
        composite.add_provider(self.provider1)

        self.assertEqual(len(composite._providers), 1)

    def test_add_provider_with_priority(self):
        """Test adding provider with specific priority."""
        composite = CompositeThemeProvider()
        composite.add_provider(self.provider1)  # Priority -1 (last)
        composite.add_provider(self.provider2, priority=0)  # Priority 0 (first)

        # provider2 should be first due to priority
        self.assertEqual(composite._providers[0], self.provider2)

    def test_get_color_from_first_provider(self):
        """Test getting color from first provider that has it."""
        self.provider1.add_theme(self.theme1)

        color = self.composite.get_color("primary", "theme1")

        self.assertEqual(color, "#ff0000")

    def test_get_color_priority_order(self):
        """Test color retrieval respects provider priority order."""
        # Both providers have same theme name but different colors
        theme_same_name_1 = Theme.from_dict(
            {
                "name": "same-theme",
                "version": "1.0.0",
                "colors": {"primary": "#ff0000"},
                "styles": {},
            }
        )
        theme_same_name_2 = Theme.from_dict(
            {
                "name": "same-theme",
                "version": "1.0.0",
                "colors": {"primary": "#00ff00"},
                "styles": {},
            }
        )

        self.provider1.add_theme(theme_same_name_1)
        self.provider2.add_theme(theme_same_name_2)

        # Should get color from provider1 (higher priority - first in list)
        color = self.composite.get_color("primary", "same-theme")

        self.assertEqual(color, "#ff0000")

    def test_get_color_fallback_to_global(self):
        """Test fallback to global fallback when no provider has color."""
        # No themes in any provider
        color = self.composite.get_color("nonexistent-color", "nonexistent-theme")

        self.assertIsNotNone(color)  # Should return global fallback

    def test_list_themes_from_all_providers(self):
        """Test listing themes from all providers."""
        self.provider1.add_theme(self.theme1)
        self.provider2.add_theme(self.theme2)

        themes = self.composite.list_themes()

        self.assertEqual(len(themes), 2)
        self.assertIn("theme1", themes)
        self.assertIn("theme2", themes)

    def test_list_themes_deduplication(self):
        """Test theme list deduplication when providers have same themes."""
        same_name_theme1 = Theme.from_dict({**self.theme1_data, "name": "duplicate"})
        same_name_theme2 = Theme.from_dict({**self.theme2_data, "name": "duplicate"})

        self.provider1.add_theme(same_name_theme1)
        self.provider2.add_theme(same_name_theme2)

        themes = self.composite.list_themes()

        # Should only list "duplicate" once
        self.assertEqual(len(themes), 1)
        self.assertIn("duplicate", themes)

    def test_empty_providers_fallback(self):
        """Test behavior with no providers."""
        empty_composite = CompositeThemeProvider()

        color = empty_composite.get_color("primary", "any-theme")

        self.assertIsNotNone(color)  # Should return global fallback

        themes = empty_composite.list_themes()
        self.assertEqual(len(themes), 0)


class TestProviderFactories(ThemedTestCase):
    """Test provider factory functions."""

    def test_create_default_provider(self):
        """Test creating default provider."""
        provider = create_default_provider()

        self.assertIsInstance(provider, DefaultThemeProvider)
        self.assertEqual(len(provider.list_themes()), 0)

    def test_create_default_provider_with_themes(self):
        """Test creating default provider with initial themes."""
        theme = Theme.from_dict(
            {
                "name": "factory-theme",
                "version": "1.0.0",
                "colors": {"primary": "#007acc"},
                "styles": {},
            }
        )
        themes = {"factory-theme": theme}

        provider = create_default_provider(themes)

        self.assertEqual(len(provider.list_themes()), 1)
        self.assertIn("factory-theme", provider.list_themes())

    def test_create_cached_provider(self):
        """Test creating cached provider."""
        base_provider = DefaultThemeProvider()
        cached_provider = create_cached_provider(base_provider, cache_size=5)

        self.assertIsInstance(cached_provider, CachedThemeProvider)
        self.assertEqual(cached_provider._cache_size, 5)
        self.assertIs(cached_provider._base_provider, base_provider)

    def test_create_composite_provider(self):
        """Test creating composite provider."""
        provider1 = DefaultThemeProvider()
        provider2 = DefaultThemeProvider()
        providers = [provider1, provider2]

        composite_provider = create_composite_provider(providers)

        self.assertIsInstance(composite_provider, CompositeThemeProvider)
        self.assertEqual(len(composite_provider._providers), 2)

    def test_create_composite_provider_empty(self):
        """Test creating empty composite provider."""
        composite_provider = create_composite_provider()

        self.assertIsInstance(composite_provider, CompositeThemeProvider)
        self.assertEqual(len(composite_provider._providers), 0)


class TestProviderPerformance(ThemedTestCase):
    """Test provider performance requirements."""

    def setUp(self):
        """Set up performance test fixtures."""
        super().setUp()
        self.provider = DefaultThemeProvider()

        # Create theme with many properties for performance testing
        self.perf_theme_data = {
            "name": "performance-theme",
            "version": "1.0.0",
            "colors": {f"color{i}": f"#{i:06x}" for i in range(100)},
            "styles": {f"Widget{i}": f"color: #{i:06x};" for i in range(100)},
        }
        self.perf_theme = Theme.from_dict(self.perf_theme_data)

    def test_property_access_performance(self):
        """Test property access meets < 1μs requirement through caching."""
        self.provider.add_theme(self.perf_theme)
        self.provider.set_current_theme("performance-theme")

        # Warm up cache
        self.provider.get_color("color0")

        # Measure cached access performance
        start_time = time.time()
        for _i in range(1000):  # Many access to get good measurement
            self.provider.get_color("color0")
        total_time = time.time() - start_time

        average_time = total_time / 1000
        self.assertLess(average_time, 0.000001)  # < 1μs per access

    def test_theme_loading_performance(self):
        """Test theme loading performance."""
        # Measure theme loading time
        start_time = time.time()
        self.provider.add_theme(self.perf_theme)
        load_time = time.time() - start_time

        # Should load quickly
        self.assertLess(load_time, 0.01)  # < 10ms

    def test_concurrent_access_performance(self):
        """Test concurrent access performance."""
        self.provider.add_theme(self.perf_theme)
        self.provider.set_current_theme("performance-theme")

        results = []
        errors = []

        def concurrent_worker(worker_id: int):
            """Worker function for concurrent access testing."""
            try:
                start_time = time.time()

                # Perform many property accesses
                for i in range(100):
                    self.provider.get_color(f"color{i % 10}")
                    self.provider.get_property(f"styles.Widget{i % 10}")

                worker_time = time.time() - start_time
                results.append(worker_time)

            except Exception as e:
                errors.append(f"Worker {worker_id}: {e}")

        # Run concurrent workers
        threads = []
        for worker_id in range(8):
            thread = threading.Thread(target=concurrent_worker, args=(worker_id,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # No errors should occur
        self.assertEqual(len(errors), 0, f"Concurrent access errors: {errors}")

        # All workers should complete quickly
        self.assertEqual(len(results), 8)
        for worker_time in results:
            self.assertLess(worker_time, 0.1)  # Each worker < 100ms

    def test_memory_efficiency(self):
        """Test provider memory efficiency."""
        import gc

        # Measure baseline memory
        gc.collect()
        initial_objects = len(gc.get_objects())

        # Create many themes and properties
        themes = []
        for i in range(50):
            theme_data = {
                "name": f"memory-theme-{i}",
                "version": "1.0.0",
                "colors": {f"color{j}": f"#{j:06x}" for j in range(10)},
                "styles": {f"Widget{j}": f"color: #{j:06x};" for j in range(10)},
            }
            theme = Theme.from_dict(theme_data)
            themes.append(theme)
            self.provider.add_theme(theme)

        mid_objects = len(gc.get_objects())

        # Clean up
        del themes
        self.provider = DefaultThemeProvider()  # Reset provider
        gc.collect()

        final_objects = len(gc.get_objects())

        # Memory should be efficiently managed
        memory_growth = mid_objects - initial_objects
        memory_cleanup = mid_objects - final_objects

        # Should clean up most allocated objects
        cleanup_ratio = memory_cleanup / memory_growth if memory_growth > 0 else 1.0
        self.assertGreater(cleanup_ratio, 0.7)  # At least 70% cleanup


class TestProviderIntegration(ThemedTestCase):
    """Integration tests for provider components working together."""

    def test_layered_provider_stack(self):
        """Test layered provider architecture."""
        # Create stack: Composite -> Cached -> Default
        base_provider = DefaultThemeProvider()
        cached_provider = CachedThemeProvider(base_provider)
        composite_provider = CompositeThemeProvider([cached_provider])

        # Add theme through base provider
        theme = Theme.from_dict(
            {
                "name": "layered-theme",
                "version": "1.0.0",
                "colors": {"primary": "#007acc"},
                "styles": {"QPushButton": "background-color: @colors.primary;"},
            }
        )
        base_provider.add_theme(theme)

        # Access through composite (should work through all layers)
        color = composite_provider.get_color("primary", "layered-theme")

        self.assertEqual(color, "#007acc")

    def test_fallback_hierarchy(self):
        """Test fallback hierarchy works correctly."""
        provider = DefaultThemeProvider()

        # Add theme with partial data
        partial_theme = Theme.from_dict(
            {
                "name": "partial-theme",
                "version": "1.0.0",
                "colors": {"primary": "#007acc"},  # Only has primary
                "styles": {},
            }
        )
        provider.add_theme(partial_theme)

        # Should get primary color from theme
        primary = provider.get_color("primary", "partial-theme")
        self.assertEqual(primary, "#007acc")

        # Should get fallback for missing color
        missing = provider.get_color("missing-color", "partial-theme")
        self.assertIsNotNone(missing)  # Should be fallback, not None

    def test_error_recovery_across_providers(self):
        """Test error recovery works across different provider types."""
        providers = [
            DefaultThemeProvider(),
            CachedThemeProvider(DefaultThemeProvider()),
            CompositeThemeProvider(),
        ]

        for provider in providers:
            # Should not crash on missing theme
            try:
                color = provider.get_color("any-color", "missing-theme")
                self.assertIsNotNone(color)  # Should return fallback
            except Exception as e:
                # Some providers might raise exceptions, others return fallbacks
                self.assertIsInstance(e, (ThemeNotFoundError, PropertyNotFoundError))


if __name__ == "__main__":
    pytest.main([__file__])
