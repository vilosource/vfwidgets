"""
Test suite for ThemeRepository.

Tests theme storage and retrieval operations including:
- Theme loading from various sources (JSON, VSCode formats)
- Theme saving with proper formatting
- Theme discovery in directories
- Built-in theme management
- Thread-safe storage operations
- Caching and indexing
- Error handling and recovery
"""

import pytest
import json
import tempfile
import threading
import time
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, patch, mock_open

# Import the modules under test
from vfwidgets_theme.core.repository import (
    ThemeRepository, FileThemeLoader, BuiltinThemeManager,
    ThemeCache, ThemeDiscovery, create_theme_repository
)
from vfwidgets_theme.core.theme import Theme
from vfwidgets_theme.errors import ThemeNotFoundError, ThemeLoadError, ThemeValidationError
from vfwidgets_theme.testing import ThemedTestCase, MockTheme


class TestThemeRepository(ThemedTestCase):
    """Test ThemeRepository storage and retrieval operations."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.repository = ThemeRepository()
        self.sample_theme_data = {
            "name": "test-theme",
            "version": "1.0.0",
            "colors": {
                "primary": "#007acc",
                "secondary": "#ffffff"
            },
            "styles": {
                "button": "background-color: @colors.primary;"
            }
        }

    def test_repository_initialization(self):
        """Test repository initialization with default settings."""
        repo = ThemeRepository()
        self.assertIsNotNone(repo)
        self.assertEqual(len(repo.list_themes()), 0)
        self.assertIsInstance(repo._cache, ThemeCache)
        self.assertIsInstance(repo._discovery, ThemeDiscovery)

    def test_repository_with_custom_components(self):
        """Test repository initialization with custom components."""
        custom_cache = ThemeCache(max_size=500)
        custom_discovery = ThemeDiscovery()

        repo = ThemeRepository(cache=custom_cache, discovery=custom_discovery)
        self.assertIs(repo._cache, custom_cache)
        self.assertIs(repo._discovery, custom_discovery)

    def test_add_theme(self):
        """Test adding theme to repository."""
        theme = Theme.from_dict(self.sample_theme_data)

        self.repository.add_theme(theme)
        self.assertIn("test-theme", self.repository.list_themes())
        retrieved = self.repository.get_theme("test-theme")
        self.assertEqual(retrieved.name, "test-theme")

    def test_get_theme_existing(self):
        """Test getting existing theme."""
        theme = Theme.from_dict(self.sample_theme_data)
        self.repository.add_theme(theme)

        retrieved = self.repository.get_theme("test-theme")
        self.assertEqual(retrieved.name, "test-theme")
        self.assertEqual(retrieved.version, "1.0.0")

    def test_get_theme_nonexistent(self):
        """Test getting non-existent theme raises error."""
        with self.assertRaises(ThemeNotFoundError) as context:
            self.repository.get_theme("nonexistent")

        self.assertIn("nonexistent", str(context.exception))

    def test_has_theme(self):
        """Test checking if theme exists."""
        self.assertFalse(self.repository.has_theme("test-theme"))

        theme = Theme.from_dict(self.sample_theme_data)
        self.repository.add_theme(theme)

        self.assertTrue(self.repository.has_theme("test-theme"))

    def test_remove_theme(self):
        """Test removing theme from repository."""
        theme = Theme.from_dict(self.sample_theme_data)
        self.repository.add_theme(theme)

        self.assertTrue(self.repository.has_theme("test-theme"))
        removed = self.repository.remove_theme("test-theme")
        self.assertTrue(removed)
        self.assertFalse(self.repository.has_theme("test-theme"))

    def test_remove_nonexistent_theme(self):
        """Test removing non-existent theme returns False."""
        removed = self.repository.remove_theme("nonexistent")
        self.assertFalse(removed)

    def test_list_themes(self):
        """Test listing all themes."""
        self.assertEqual(self.repository.list_themes(), [])

        theme1 = Theme.from_dict({**self.sample_theme_data, "name": "theme1"})
        theme2 = Theme.from_dict({**self.sample_theme_data, "name": "theme2"})

        self.repository.add_theme(theme1)
        self.repository.add_theme(theme2)

        themes = self.repository.list_themes()
        self.assertEqual(len(themes), 2)
        self.assertIn("theme1", themes)
        self.assertIn("theme2", themes)

    def test_clear_themes(self):
        """Test clearing all themes."""
        theme1 = Theme.from_dict({**self.sample_theme_data, "name": "theme1"})
        theme2 = Theme.from_dict({**self.sample_theme_data, "name": "theme2"})

        self.repository.add_theme(theme1)
        self.repository.add_theme(theme2)
        self.assertEqual(len(self.repository.list_themes()), 2)

        self.repository.clear_themes()
        self.assertEqual(len(self.repository.list_themes()), 0)

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_file')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_from_file_json(self, mock_file, mock_is_file, mock_exists):
        """Test loading theme from JSON file."""
        mock_exists.return_value = True
        mock_is_file.return_value = True
        mock_file.return_value.read.return_value = json.dumps(self.sample_theme_data)

        theme = self.repository.load_from_file("test_theme.json")

        self.assertEqual(theme.name, "test-theme")
        self.assertEqual(theme.version, "1.0.0")
        mock_file.assert_called_once()

    @patch('pathlib.Path.exists')
    def test_load_from_file_nonexistent(self, mock_exists):
        """Test loading from non-existent file raises error."""
        mock_exists.return_value = False

        with self.assertRaises(ThemeLoadError) as context:
            self.repository.load_from_file("nonexistent.json")

        self.assertIn("nonexistent.json", str(context.exception))

    @patch('pathlib.Path.parent.mkdir')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_to_file(self, mock_file, mock_mkdir):
        """Test saving theme to file."""
        theme = Theme.from_dict(self.sample_theme_data)

        self.repository.save_to_file(theme, "output.json")

        mock_mkdir.assert_called_once()
        mock_file.assert_called_once()
        # Verify JSON was written
        handle = mock_file.return_value
        written_content = ''.join(call.args[0] for call in handle.write.call_args_list)
        self.assertIn('"name": "test-theme"', written_content)

    def test_discover_themes_in_directory(self):
        """Test discovering themes in directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test theme files
            theme1_file = temp_path / "theme1.json"
            theme2_file = temp_path / "theme2.json"

            theme1_file.write_text(json.dumps({**self.sample_theme_data, "name": "theme1"}))
            theme2_file.write_text(json.dumps({**self.sample_theme_data, "name": "theme2"}))

            discovered = self.repository.discover_themes(temp_path)

            self.assertEqual(len(discovered), 2)
            theme_names = [theme.name for theme in discovered]
            self.assertIn("theme1", theme_names)
            self.assertIn("theme2", theme_names)

    def test_caching_behavior(self):
        """Test that repository uses caching for performance."""
        theme = Theme.from_dict(self.sample_theme_data)
        self.repository.add_theme(theme)

        # First access should populate cache
        retrieved1 = self.repository.get_theme("test-theme")

        # Second access should hit cache
        with patch.object(self.repository._themes, 'get') as mock_get:
            retrieved2 = self.repository.get_theme("test-theme")
            # Cache should prevent direct dict access
            mock_get.assert_not_called()

        self.assertEqual(retrieved1.name, retrieved2.name)

    def test_thread_safety(self):
        """Test repository thread safety with concurrent operations."""
        theme_template = self.sample_theme_data.copy()
        results = []
        errors = []

        def worker(worker_id: int):
            """Worker function for concurrent testing."""
            try:
                for i in range(10):
                    theme_data = theme_template.copy()
                    theme_data["name"] = f"worker-{worker_id}-theme-{i}"
                    theme = Theme.from_dict(theme_data)

                    self.repository.add_theme(theme)
                    retrieved = self.repository.get_theme(theme.name)
                    results.append(f"{worker_id}-{i}")

                    # Simulate some processing time
                    time.sleep(0.001)
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
        self.assertEqual(len(results), 50)  # 5 workers * 10 themes each
        self.assertEqual(len(self.repository.list_themes()), 50)


class TestFileThemeLoader(ThemedTestCase):
    """Test FileThemeLoader for loading themes from files."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.loader = FileThemeLoader()

    def test_can_load_json_file(self):
        """Test loader can handle JSON files."""
        self.assertTrue(self.loader.can_load("theme.json"))
        self.assertTrue(self.loader.can_load(Path("theme.json")))

    def test_can_load_yaml_file(self):
        """Test loader can handle YAML files."""
        self.assertTrue(self.loader.can_load("theme.yaml"))
        self.assertTrue(self.loader.can_load("theme.yml"))

    def test_cannot_load_invalid_file(self):
        """Test loader rejects invalid file types."""
        self.assertFalse(self.loader.can_load("theme.txt"))
        self.assertFalse(self.loader.can_load("theme"))
        self.assertFalse(self.loader.can_load(123))

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_file')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_json_theme(self, mock_file, mock_is_file, mock_exists):
        """Test loading valid JSON theme."""
        theme_data = {
            "name": "test-theme",
            "version": "1.0.0",
            "colors": {"primary": "#007acc"}
        }

        mock_exists.return_value = True
        mock_is_file.return_value = True
        mock_file.return_value.read.return_value = json.dumps(theme_data)

        theme = self.loader.load_theme("test.json")

        self.assertEqual(theme.name, "test-theme")
        self.assertEqual(theme.version, "1.0.0")

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_file')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_invalid_json(self, mock_file, mock_is_file, mock_exists):
        """Test loading invalid JSON raises error."""
        mock_exists.return_value = True
        mock_is_file.return_value = True
        mock_file.return_value.read.return_value = "invalid json content"

        with self.assertRaises(ThemeLoadError):
            self.loader.load_theme("invalid.json")

    def test_load_nonexistent_file(self):
        """Test loading non-existent file raises error."""
        with self.assertRaises(ThemeLoadError):
            self.loader.load_theme("nonexistent.json")


class TestBuiltinThemeManager(ThemedTestCase):
    """Test BuiltinThemeManager for managing built-in themes."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.manager = BuiltinThemeManager()

    def test_initialization(self):
        """Test manager initialization."""
        self.assertIsNotNone(self.manager)
        # Should have some built-in themes
        themes = self.manager.list_themes()
        self.assertGreater(len(themes), 0)

    def test_has_default_themes(self):
        """Test manager has expected default themes."""
        themes = self.manager.list_themes()
        expected_themes = ["default", "dark", "light"]

        for theme_name in expected_themes:
            self.assertIn(theme_name, themes)

    def test_get_builtin_theme(self):
        """Test getting built-in theme."""
        theme = self.manager.get_theme("default")
        self.assertIsNotNone(theme)
        self.assertEqual(theme.name, "default")

    def test_get_nonexistent_builtin_theme(self):
        """Test getting non-existent built-in theme raises error."""
        with self.assertRaises(ThemeNotFoundError):
            self.manager.get_theme("nonexistent-builtin")

    def test_theme_validation(self):
        """Test that built-in themes are valid."""
        for theme_name in self.manager.list_themes():
            theme = self.manager.get_theme(theme_name)
            # Verify theme has required properties
            self.assertIsNotNone(theme.name)
            self.assertIsNotNone(theme.version)
            self.assertIsInstance(theme.colors, dict)


class TestThemeCache(ThemedTestCase):
    """Test ThemeCache for performance optimization."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.cache = ThemeCache(max_size=3)
        self.theme = Theme.from_dict({
            "name": "test-theme",
            "version": "1.0.0",
            "colors": {"primary": "#007acc"}
        })

    def test_cache_initialization(self):
        """Test cache initialization with size limits."""
        cache = ThemeCache(max_size=10)
        self.assertEqual(cache.max_size, 10)
        self.assertEqual(cache.size, 0)

    def test_cache_put_and_get(self):
        """Test basic cache put and get operations."""
        self.cache.put("test-theme", self.theme)

        cached = self.cache.get("test-theme")
        self.assertIsNotNone(cached)
        self.assertEqual(cached.name, "test-theme")

    def test_cache_miss(self):
        """Test cache miss returns None."""
        result = self.cache.get("nonexistent")
        self.assertIsNone(result)

    def test_cache_size_limit(self):
        """Test cache respects size limits with LRU eviction."""
        # Fill cache to capacity
        for i in range(3):
            theme_data = {"name": f"theme-{i}", "version": "1.0.0", "colors": {}}
            theme = Theme.from_dict(theme_data)
            self.cache.put(f"theme-{i}", theme)

        self.assertEqual(self.cache.size, 3)

        # Add one more - should evict oldest (theme-0)
        theme_data = {"name": "theme-3", "version": "1.0.0", "colors": {}}
        theme = Theme.from_dict(theme_data)
        self.cache.put("theme-3", theme)

        self.assertEqual(self.cache.size, 3)
        self.assertIsNone(self.cache.get("theme-0"))  # Evicted
        self.assertIsNotNone(self.cache.get("theme-3"))  # New entry

    def test_cache_clear(self):
        """Test cache clear operation."""
        self.cache.put("test-theme", self.theme)
        self.assertEqual(self.cache.size, 1)

        self.cache.clear()
        self.assertEqual(self.cache.size, 0)
        self.assertIsNone(self.cache.get("test-theme"))

    def test_cache_invalidate(self):
        """Test cache invalidation by key."""
        self.cache.put("test-theme", self.theme)
        self.assertIsNotNone(self.cache.get("test-theme"))

        invalidated = self.cache.invalidate("test-theme")
        self.assertTrue(invalidated)
        self.assertIsNone(self.cache.get("test-theme"))

    def test_cache_statistics(self):
        """Test cache statistics tracking."""
        # Initial state
        stats = self.cache.get_statistics()
        self.assertEqual(stats["hits"], 0)
        self.assertEqual(stats["misses"], 0)

        # Cache miss
        self.cache.get("nonexistent")
        stats = self.cache.get_statistics()
        self.assertEqual(stats["misses"], 1)

        # Cache put and hit
        self.cache.put("test-theme", self.theme)
        self.cache.get("test-theme")
        stats = self.cache.get_statistics()
        self.assertEqual(stats["hits"], 1)


class TestThemeDiscovery(ThemedTestCase):
    """Test ThemeDiscovery for finding themes in directories."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.discovery = ThemeDiscovery()

    def test_discover_in_empty_directory(self):
        """Test discovery in empty directory returns empty list."""
        with tempfile.TemporaryDirectory() as temp_dir:
            themes = self.discovery.discover_in_directory(temp_dir)
            self.assertEqual(len(themes), 0)

    def test_discover_json_themes(self):
        """Test discovering JSON theme files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test theme files
            theme_data = {"name": "discovered-theme", "version": "1.0.0", "colors": {}}
            theme_file = temp_path / "discovered-theme.json"
            theme_file.write_text(json.dumps(theme_data))

            themes = self.discovery.discover_in_directory(temp_dir)

            self.assertEqual(len(themes), 1)
            self.assertEqual(themes[0].name, "discovered-theme")

    def test_discover_ignores_invalid_files(self):
        """Test discovery ignores invalid files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create invalid files
            (temp_path / "not-a-theme.txt").write_text("not a theme")
            (temp_path / "invalid.json").write_text("invalid json")

            # Create valid theme
            theme_data = {"name": "valid-theme", "version": "1.0.0", "colors": {}}
            (temp_path / "valid.json").write_text(json.dumps(theme_data))

            themes = self.discovery.discover_in_directory(temp_dir)

            self.assertEqual(len(themes), 1)
            self.assertEqual(themes[0].name, "valid-theme")

    def test_discover_with_subdirectories(self):
        """Test discovery with recursive subdirectory search."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create subdirectory with theme
            sub_dir = temp_path / "subdir"
            sub_dir.mkdir()

            theme_data = {"name": "nested-theme", "version": "1.0.0", "colors": {}}
            theme_file = sub_dir / "nested-theme.json"
            theme_file.write_text(json.dumps(theme_data))

            themes = self.discovery.discover_in_directory(temp_dir, recursive=True)

            self.assertEqual(len(themes), 1)
            self.assertEqual(themes[0].name, "nested-theme")


class TestRepositoryIntegration(ThemedTestCase):
    """Integration tests for repository components working together."""

    def test_repository_with_all_components(self):
        """Test repository with cache, discovery, and loaders."""
        repo = create_theme_repository()

        # Test built-in themes are available
        themes = repo.list_themes()
        self.assertGreater(len(themes), 0)
        self.assertIn("default", themes)

        # Test getting built-in theme
        default_theme = repo.get_theme("default")
        self.assertEqual(default_theme.name, "default")

    def test_performance_requirements(self):
        """Test repository meets performance requirements."""
        repo = ThemeRepository()
        theme = Theme.from_dict({
            "name": "perf-test",
            "version": "1.0.0",
            "colors": {"primary": "#007acc"}
        })

        # Test theme loading performance (< 200ms requirement)
        start_time = time.time()
        repo.add_theme(theme)
        retrieved = repo.get_theme("perf-test")
        load_time = time.time() - start_time

        self.assertLess(load_time, 0.2)  # < 200ms
        self.assertEqual(retrieved.name, "perf-test")

        # Test cached access performance (< 1μs requirement through caching)
        start_time = time.time()
        for _ in range(100):
            repo.get_theme("perf-test")
        batch_time = time.time() - start_time

        avg_time = batch_time / 100
        self.assertLess(avg_time, 0.001)  # < 1ms average (cache should make this much faster)

    def test_memory_overhead(self):
        """Test repository memory overhead (< 2KB per theme requirement)."""
        import sys

        repo = ThemeRepository()

        # Measure baseline memory
        baseline_size = sys.getsizeof(repo) + sum(
            sys.getsizeof(v) for v in repo.__dict__.values()
        )

        # Add themes and measure growth
        themes_count = 10
        for i in range(themes_count):
            theme_data = {
                "name": f"memory-test-{i}",
                "version": "1.0.0",
                "colors": {"primary": "#007acc", "secondary": "#ffffff"}
            }
            theme = Theme.from_dict(theme_data)
            repo.add_theme(theme)

        # Calculate memory per theme
        final_size = sys.getsizeof(repo) + sum(
            sys.getsizeof(v) for v in repo.__dict__.values()
        )

        memory_per_theme = (final_size - baseline_size) / themes_count

        # Should be less than 2KB per theme
        self.assertLess(memory_per_theme, 2048)


if __name__ == "__main__":
    pytest.main([__file__])