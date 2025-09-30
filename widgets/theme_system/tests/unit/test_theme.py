"""
Comprehensive tests for Theme data model.

Tests for Task 7: Theme Data Model with Validation
- Immutable Theme dataclass
- Copy-on-write ThemeBuilder
- JSON schema validation with ThemeValidator
- Theme composition and merging with ThemeComposer
- Property resolution with PropertyResolver
- Performance optimizations and caching

These tests validate the core theme data structures and operations
that power ThemedWidget with immutable, validated theme data.
"""

import pytest
import json
import time
from typing import Dict, Any, Optional
from dataclasses import FrozenInstanceError
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import the components we're testing
from vfwidgets_theme.core.theme import (
    Theme, ThemeBuilder, ThemeValidator, ThemeComposer, PropertyResolver,
    ColorPalette, StyleProperties, ThemeMetadata, TokenColors,
    validate_theme_data, create_theme_from_dict
)
from vfwidgets_theme.errors import (
    ThemeLoadError, InvalidThemeFormatError, PropertyNotFoundError
)
from vfwidgets_theme.protocols import ColorValue, PropertyKey, PropertyValue
from vfwidgets_theme.testing import ThemedTestCase, ThemeBenchmark


class TestThemeImmutability(ThemedTestCase):
    """Test that Theme is truly immutable and thread-safe."""

    def test_theme_is_frozen_dataclass(self):
        """Theme should be a frozen dataclass preventing modification."""
        theme = Theme(
            name="test",
            version="1.0.0",
            colors={"primary": "#ff0000"},
            styles={"font-family": "Arial"},
            metadata={"author": "test"}
        )

        # Verify frozen behavior
        with pytest.raises(FrozenInstanceError):
            theme.name = "modified"  # type: ignore

        with pytest.raises(FrozenInstanceError):
            theme.colors = {}  # type: ignore

        with pytest.raises(FrozenInstanceError):
            theme.styles = {}  # type: ignore

    def test_theme_hash_consistency(self):
        """Theme hash should be consistent for equality comparisons."""
        theme1 = Theme(
            name="test",
            colors={"primary": "#ff0000"},
            styles={"font": "Arial"}
        )
        theme2 = Theme(
            name="test",
            colors={"primary": "#ff0000"},
            styles={"font": "Arial"}
        )
        theme3 = Theme(
            name="different",
            colors={"primary": "#ff0000"},
            styles={"font": "Arial"}
        )

        # Same data should have same hash
        assert hash(theme1) == hash(theme2)
        assert theme1 == theme2

        # Different data should have different hash
        assert hash(theme1) != hash(theme3)
        assert theme1 != theme3

    def test_theme_concurrent_access_safety(self):
        """Theme should be safe for concurrent access."""
        theme = Theme(
            name="concurrent_test",
            colors={f"color_{i}": f"#{i:06x}" for i in range(100)},
            styles={f"prop_{i}": f"value_{i}" for i in range(100)}
        )

        def access_theme_properties():
            """Access various theme properties concurrently."""
            results = []
            for i in range(50):
                color = theme.get_color(f"color_{i}", "#default")
                prop = theme.get_property(f"prop_{i}", "default")
                results.extend([color, prop])
            return results

        # Run concurrent access
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(access_theme_properties) for _ in range(10)]
            results = [future.result() for future in as_completed(futures)]

        # All threads should get consistent results
        first_result = results[0]
        assert all(result == first_result for result in results)


class TestThemeValidation(ThemedTestCase):
    """Test Theme validation during creation."""

    def test_theme_requires_name(self):
        """Theme must have a valid name."""
        # Valid name should work
        theme = Theme(name="valid_name")
        assert theme.name == "valid_name"

        # Empty name should fail validation
        with pytest.raises(InvalidThemeFormatError):
            Theme(name="")

        # None name should fail
        with pytest.raises((TypeError, InvalidThemeFormatError)):
            Theme(name=None)  # type: ignore

    def test_theme_version_validation(self):
        """Theme version should follow semantic versioning."""
        # Valid versions
        for version in ["1.0.0", "2.1.3", "10.0.0-beta"]:
            theme = Theme(name="test", version=version)
            assert theme.version == version

        # Invalid versions should fail
        invalid_versions = ["", "1", "1.0", "invalid", "1.0.0.0"]
        for version in invalid_versions:
            with pytest.raises(InvalidThemeFormatError):
                Theme(name="test", version=version)

    def test_color_palette_validation(self):
        """Color palette should validate color formats."""
        # Valid colors
        valid_colors = {
            "hex3": "#f00",
            "hex6": "#ff0000",
            "hex8": "#ff0000ff",
            "rgb": "rgb(255, 0, 0)",
            "rgba": "rgba(255, 0, 0, 0.5)",
            "named": "red",
            "hsl": "hsl(0, 100%, 50%)"
        }
        theme = Theme(name="test", colors=valid_colors)
        assert theme.colors == valid_colors

        # Invalid colors should fail
        invalid_colors = {
            "bad_hex": "#gg0000",
            "bad_rgb": "rgb(300, 0, 0)",  # > 255
            "bad_format": "not_a_color"
        }

        for key, bad_color in invalid_colors.items():
            with pytest.raises(InvalidThemeFormatError):
                Theme(name="test", colors={key: bad_color})

    def test_styles_validation(self):
        """Style properties should be validated."""
        # Valid styles
        valid_styles = {
            "font-family": "Arial, sans-serif",
            "font-size": "12px",
            "background-color": "#ffffff",
            "border": "1px solid #000000",
            "margin": "10px 5px"
        }
        theme = Theme(name="test", styles=valid_styles)
        assert theme.styles == valid_styles

        # Styles should allow CSS-like values
        css_styles = {
            "display": "flex",
            "justify-content": "center",
            "grid-template-columns": "1fr 2fr 1fr"
        }
        theme = Theme(name="test", styles=css_styles)
        assert theme.styles == css_styles

    def test_metadata_validation(self):
        """Metadata should be flexible but validated."""
        valid_metadata = {
            "author": "Test Author",
            "description": "A test theme",
            "homepage": "https://example.com",
            "license": "MIT",
            "tags": ["dark", "minimal"],
            "created": "2024-01-01",
            "updated": "2024-01-15"
        }
        theme = Theme(name="test", metadata=valid_metadata)
        assert theme.metadata == valid_metadata

        # Required metadata fields
        theme = Theme(name="test", metadata={"author": "Required"})
        assert "author" in theme.metadata


class TestThemeBuilder(ThemedTestCase):
    """Test ThemeBuilder for copy-on-write operations."""

    def test_builder_from_theme(self):
        """Builder should create from existing theme."""
        original = Theme(
            name="original",
            colors={"primary": "#ff0000"},
            styles={"font": "Arial"}
        )

        builder = ThemeBuilder.from_theme(original)
        assert builder.name == "original"
        assert builder.colors == {"primary": "#ff0000"}
        assert builder.styles == {"font": "Arial"}

    def test_builder_modifications(self):
        """Builder should allow modifications before building."""
        builder = ThemeBuilder("test")

        # Modify properties
        builder.set_name("modified")
        builder.add_color("primary", "#0000ff")
        builder.add_style("font-family", "Helvetica")
        builder.set_metadata({"author": "builder"})

        theme = builder.build()
        assert theme.name == "modified"
        assert theme.colors["primary"] == "#0000ff"
        assert theme.styles["font-family"] == "Helvetica"
        assert theme.metadata["author"] == "builder"

    def test_builder_validation_on_build(self):
        """Builder should validate when building theme."""
        builder = ThemeBuilder("test")
        builder.add_color("bad", "#invalid_color")

        with pytest.raises(InvalidThemeFormatError):
            builder.build()

        # Fix the issue and build should work
        builder.add_color("bad", "#ff0000")
        theme = builder.build()
        assert theme.colors["bad"] == "#ff0000"

    def test_builder_rollback_support(self):
        """Builder should support rollback for invalid modifications."""
        original = Theme(name="test", colors={"primary": "#ff0000"})
        builder = ThemeBuilder.from_theme(original)

        # Create checkpoint
        builder.checkpoint()

        # Make invalid change
        builder.add_color("bad", "#invalid")

        # Rollback to checkpoint
        builder.rollback()

        # Should be back to original state
        theme = builder.build()
        assert theme.colors == {"primary": "#ff0000"}
        assert "bad" not in theme.colors

    def test_builder_performance(self):
        """Builder operations should be performant."""
        large_theme = Theme(
            name="large",
            colors={f"color_{i}": f"#{i:06x}" for i in range(1000)},
            styles={f"style_{i}": f"value_{i}" for i in range(1000)}
        )

        # Builder creation should be fast
        start_time = time.perf_counter()
        builder = ThemeBuilder.from_theme(large_theme)
        creation_time = time.perf_counter() - start_time
        assert creation_time < 0.01, f"Builder creation took {creation_time:.3f}s"

        # Modifications should be fast
        start_time = time.perf_counter()
        for i in range(100):
            builder.add_color(f"new_{i}", f"#{i:06x}")
        modification_time = time.perf_counter() - start_time
        assert modification_time < 0.05, f"100 modifications took {modification_time:.3f}s"

        # Build should be fast
        start_time = time.perf_counter()
        theme = builder.build()
        build_time = time.perf_counter() - start_time
        assert build_time < 0.1, f"Build took {build_time:.3f}s"


class TestThemeValidator(ThemedTestCase):
    """Test ThemeValidator for JSON schema validation."""

    def setup_method(self, method):
        """Set up validator for each test."""
        self.validator = ThemeValidator()

    def test_validator_basic_theme(self):
        """Validator should validate basic theme structure."""
        basic_theme = {
            "name": "basic",
            "version": "1.0.0",
            "colors": {"primary": "#ff0000"},
            "styles": {"font-family": "Arial"}
        }

        assert self.validator.validate(basic_theme)
        assert len(self.validator.get_errors()) == 0

    def test_validator_vscode_compatibility(self):
        """Validator should handle VSCode theme format."""
        vscode_theme = {
            "name": "VS Code Theme",
            "type": "dark",
            "colors": {
                "editor.background": "#1e1e1e",
                "editor.foreground": "#d4d4d4",
                "activityBar.background": "#333333"
            },
            "tokenColors": [
                {
                    "name": "Comment",
                    "scope": "comment",
                    "settings": {
                        "foreground": "#6A9955"
                    }
                }
            ]
        }

        assert self.validator.validate(vscode_theme)

    def test_validator_error_reporting(self):
        """Validator should provide detailed error reports."""
        invalid_theme = {
            "name": "",  # Invalid: empty name
            "colors": {
                "bad_color": "#invalid"  # Invalid: bad color format
            },
            "styles": {
                123: "invalid_key"  # Invalid: non-string key
            }
        }

        assert not self.validator.validate(invalid_theme)
        errors = self.validator.get_errors()
        assert len(errors) > 0

        # Check error details
        error_messages = [error["message"] for error in errors]
        assert any("name" in msg.lower() for msg in error_messages)
        assert any("color" in msg.lower() for msg in error_messages)

    def test_validator_suggestions(self):
        """Validator should provide suggestions for common mistakes."""
        theme_with_typo = {
            "name": "test",
            "colours": {"primary": "#ff0000"}  # Typo: should be "colors"
        }

        assert not self.validator.validate(theme_with_typo)
        suggestions = self.validator.get_suggestions()
        assert any("colors" in suggestion for suggestion in suggestions)

    def test_validator_performance(self):
        """Validator should validate quickly."""
        large_theme = {
            "name": "large_theme",
            "colors": {f"color_{i}": f"#{i:06x}" for i in range(1000)},
            "styles": {f"style_{i}": f"value_{i}" for i in range(1000)}
        }

        start_time = time.perf_counter()
        result = self.validator.validate(large_theme)
        validation_time = time.perf_counter() - start_time

        assert result  # Should be valid
        assert validation_time < 0.1, f"Validation took {validation_time:.3f}s"


class TestThemeComposer(ThemedTestCase):
    """Test ThemeComposer for intelligent theme merging."""

    def setup_method(self, method):
        """Set up composer for each test."""
        self.composer = ThemeComposer()

    def test_compose_basic_themes(self):
        """Composer should merge two themes correctly."""
        base_theme = Theme(
            name="base",
            colors={"primary": "#ff0000", "secondary": "#00ff00"},
            styles={"font-family": "Arial", "font-size": "12px"}
        )

        override_theme = Theme(
            name="override",
            colors={"primary": "#0000ff"},  # Override primary
            styles={"font-size": "14px"}    # Override font-size
        )

        composed = self.composer.compose(base_theme, override_theme)

        # Override values should win
        assert composed.colors["primary"] == "#0000ff"
        assert composed.styles["font-size"] == "14px"

        # Base values should remain
        assert composed.colors["secondary"] == "#00ff00"
        assert composed.styles["font-family"] == "Arial"

    def test_compose_inheritance_chain(self):
        """Composer should handle inheritance chains."""
        grandparent = Theme(
            name="grandparent",
            colors={"a": "#aaa", "b": "#bbb", "c": "#ccc"}
        )
        parent = Theme(
            name="parent",
            colors={"b": "#BBB"},  # Override b
            metadata={"extends": "grandparent"}
        )
        child = Theme(
            name="child",
            colors={"c": "#CCC"},  # Override c
            metadata={"extends": "parent"}
        )

        # Compose inheritance chain
        result = self.composer.compose_chain([grandparent, parent, child])

        assert result.colors["a"] == "#aaa"  # From grandparent
        assert result.colors["b"] == "#BBB"  # From parent
        assert result.colors["c"] == "#CCC"  # From child

    def test_compose_conflict_resolution(self):
        """Composer should handle conflicts with resolution strategies."""
        theme1 = Theme(
            name="theme1",
            colors={"conflict": "#ff0000"},
            metadata={"priority": 1}
        )
        theme2 = Theme(
            name="theme2",
            colors={"conflict": "#00ff00"},
            metadata={"priority": 2}
        )

        # Higher priority should win
        composed = self.composer.compose_with_strategy(
            [theme1, theme2],
            strategy="priority"
        )
        assert composed.colors["conflict"] == "#00ff00"  # theme2 wins

        # Last one wins strategy
        composed = self.composer.compose_with_strategy(
            [theme1, theme2],
            strategy="last_wins"
        )
        assert composed.colors["conflict"] == "#00ff00"  # theme2 wins

    def test_compose_performance(self):
        """Theme composition should be performant."""
        base_theme = Theme(
            name="base",
            colors={f"color_{i}": f"#{i:06x}" for i in range(500)},
            styles={f"style_{i}": f"value_{i}" for i in range(500)}
        )
        override_theme = Theme(
            name="override",
            colors={f"color_{i}": f"#{(i+1000):06x}" for i in range(250)},
            styles={f"style_{i}": f"new_value_{i}" for i in range(250)}
        )

        start_time = time.perf_counter()
        composed = self.composer.compose(base_theme, override_theme)
        composition_time = time.perf_counter() - start_time

        assert composition_time < 0.01, f"Composition took {composition_time:.3f}s"

        # Verify correctness
        assert len(composed.colors) == 750  # 500 + 250 unique
        assert len(composed.styles) == 750


class TestPropertyResolver(ThemedTestCase):
    """Test PropertyResolver for fast property lookup."""

    def setup_method(self, method):
        """Set up resolver for each test."""
        self.theme = Theme(
            name="test",
            colors={
                "primary": "#ff0000",
                "secondary": "#00ff00",
                "accent": "@primary",  # Reference
                "derived": "@colors.primary"  # Path reference
            },
            styles={
                "main-font": "Arial",
                "header-font": "@main-font",  # Reference
                "computed-size": "calc(@base-size + 2px)"  # Computed
            },
            metadata={
                "base-size": "12px"
            }
        )
        self.resolver = PropertyResolver(self.theme)

    def test_resolver_direct_access(self):
        """Resolver should provide fast direct property access."""
        # Direct color access
        assert self.resolver.get_color("primary") == "#ff0000"
        assert self.resolver.get_color("secondary") == "#00ff00"

        # Direct style access
        assert self.resolver.get_style("main-font") == "Arial"

    def test_resolver_reference_resolution(self):
        """Resolver should resolve property references."""
        # Color reference
        assert self.resolver.get_color("accent") == "#ff0000"  # Resolves @primary

        # Style reference
        assert self.resolver.get_style("header-font") == "Arial"  # Resolves @main-font

    def test_resolver_path_references(self):
        """Resolver should resolve path-based references."""
        # Path-based color reference
        assert self.resolver.get_color("derived") == "#ff0000"  # Resolves @colors.primary

    def test_resolver_computed_properties(self):
        """Resolver should handle computed properties."""
        # Computed property with metadata reference
        result = self.resolver.get_style("computed-size")
        assert "calc(" in result and "12px" in result

    def test_resolver_fallback_handling(self):
        """Resolver should handle missing properties with fallbacks."""
        # Missing property with fallback
        assert self.resolver.get_color("missing", "#default") == "#default"
        assert self.resolver.get_style("missing", "default") == "default"

        # Missing property without fallback should raise
        with pytest.raises(PropertyNotFoundError):
            self.resolver.get_color("missing")

    def test_resolver_caching_performance(self):
        """Resolver should cache resolved properties for performance."""
        # First access should resolve and cache
        start_time = time.perf_counter()
        color1 = self.resolver.get_color("accent")  # Requires resolution
        first_access_time = time.perf_counter() - start_time

        # Second access should be from cache
        start_time = time.perf_counter()
        color2 = self.resolver.get_color("accent")
        cached_access_time = time.perf_counter() - start_time

        assert color1 == color2 == "#ff0000"
        assert cached_access_time < first_access_time / 10  # Should be much faster
        assert cached_access_time < 0.000001  # Sub-microsecond requirement

    def test_resolver_circular_reference_detection(self):
        """Resolver should detect and handle circular references."""
        circular_theme = Theme(
            name="circular",
            colors={
                "a": "@b",
                "b": "@c",
                "c": "@a"  # Circular reference
            }
        )
        resolver = PropertyResolver(circular_theme)

        with pytest.raises(InvalidThemeFormatError, match="circular"):
            resolver.get_color("a")

    def test_resolver_concurrent_access(self):
        """Resolver should be thread-safe for concurrent access."""
        def resolve_properties():
            """Resolve various properties concurrently."""
            results = []
            for _ in range(100):
                results.append(self.resolver.get_color("primary"))
                results.append(self.resolver.get_color("accent"))  # Requires resolution
                results.append(self.resolver.get_style("main-font"))
            return results

        # Run concurrent access
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(resolve_properties) for _ in range(8)]
            results = [future.result() for future in as_completed(futures)]

        # All results should be consistent
        first_result = results[0]
        assert all(result == first_result for result in results)


class TestThemeHelperFunctions(ThemedTestCase):
    """Test helper functions for theme operations."""

    def test_validate_theme_data(self):
        """validate_theme_data should validate raw dictionary data."""
        # Valid theme data
        valid_data = {
            "name": "test",
            "version": "1.0.0",
            "colors": {"primary": "#ff0000"},
            "styles": {"font": "Arial"}
        }
        assert validate_theme_data(valid_data)

        # Invalid theme data
        invalid_data = {
            "name": "",  # Invalid
            "colors": {"bad": "#invalid"}  # Invalid
        }
        assert not validate_theme_data(invalid_data)

    def test_create_theme_from_dict(self):
        """create_theme_from_dict should create Theme from dictionary."""
        theme_data = {
            "name": "dict_theme",
            "version": "2.0.0",
            "colors": {
                "primary": "#0066cc",
                "secondary": "#cc6600"
            },
            "styles": {
                "font-family": "Helvetica",
                "font-size": "14px"
            },
            "metadata": {
                "author": "Test Creator"
            }
        }

        theme = create_theme_from_dict(theme_data)

        assert theme.name == "dict_theme"
        assert theme.version == "2.0.0"
        assert theme.colors["primary"] == "#0066cc"
        assert theme.styles["font-family"] == "Helvetica"
        assert theme.metadata["author"] == "Test Creator"

    def test_theme_json_serialization(self):
        """Theme should support JSON serialization/deserialization."""
        original_theme = Theme(
            name="json_test",
            version="1.0.0",
            colors={"primary": "#ff0000", "secondary": "#00ff00"},
            styles={"font": "Arial", "size": "12px"},
            metadata={"author": "JSON Test"}
        )

        # Convert to JSON and back
        theme_dict = original_theme.to_dict()
        json_str = json.dumps(theme_dict)
        loaded_dict = json.loads(json_str)
        restored_theme = create_theme_from_dict(loaded_dict)

        # Should be identical
        assert restored_theme == original_theme
        assert restored_theme.name == original_theme.name
        assert restored_theme.colors == original_theme.colors
        assert restored_theme.styles == original_theme.styles


class TestThemePerformance(ThemedTestCase):
    """Test Theme performance requirements."""

    def setup_method(self, method):
        """Set up performance test data."""
        self.large_theme = Theme(
            name="performance_test",
            colors={f"color_{i}": f"#{i:06x}" for i in range(1000)},
            styles={f"style_{i}": f"value_{i}" for i in range(1000)},
            metadata={f"meta_{i}": f"data_{i}" for i in range(100)}
        )

    def test_theme_loading_performance(self):
        """Theme loading should be < 50ms for typical themes."""
        theme_data = {
            "name": "perf_test",
            "colors": {f"color_{i}": f"#{i:06x}" for i in range(100)},
            "styles": {f"style_{i}": f"value_{i}" for i in range(100)}
        }

        start_time = time.perf_counter()
        theme = create_theme_from_dict(theme_data)
        loading_time = time.perf_counter() - start_time

        assert loading_time < 0.05, f"Theme loading took {loading_time:.3f}s"

    def test_property_access_performance(self):
        """Cached property access should be < 1μs."""
        resolver = PropertyResolver(self.large_theme)

        # First access to warm cache
        resolver.get_color("color_500")

        # Measure cached access
        start_time = time.perf_counter()
        for _ in range(1000):
            resolver.get_color("color_500")
        total_time = time.perf_counter() - start_time

        average_time = total_time / 1000
        assert average_time < 0.000001, f"Average access time: {average_time:.6f}s"

    def test_theme_validation_performance(self):
        """Theme validation should be < 100ms."""
        validator = ThemeValidator()
        large_theme_data = {
            "name": "validation_perf",
            "colors": {f"color_{i}": f"#{i:06x}" for i in range(500)},
            "styles": {f"style_{i}": f"value_{i}" for i in range(500)}
        }

        start_time = time.perf_counter()
        result = validator.validate(large_theme_data)
        validation_time = time.perf_counter() - start_time

        assert result  # Should be valid
        assert validation_time < 0.1, f"Validation took {validation_time:.3f}s"

    def test_memory_overhead_per_theme(self):
        """Memory overhead should be < 500KB per theme."""
        import sys

        # Measure theme memory usage
        theme_size = sys.getsizeof(self.large_theme)
        colors_size = sys.getsizeof(self.large_theme.colors)
        styles_size = sys.getsizeof(self.large_theme.styles)
        metadata_size = sys.getsizeof(self.large_theme.metadata)

        total_size = theme_size + colors_size + styles_size + metadata_size

        # Should be under 500KB (512,000 bytes)
        assert total_size < 512000, f"Theme memory usage: {total_size} bytes"

    def test_composition_performance(self):
        """Theme composition should be < 10ms."""
        base_theme = Theme(
            name="base",
            colors={f"color_{i}": f"#{i:06x}" for i in range(250)},
            styles={f"style_{i}": f"value_{i}" for i in range(250)}
        )
        override_theme = Theme(
            name="override",
            colors={f"color_{i}": f"#{(i+1000):06x}" for i in range(125)},
            styles={f"style_{i}": f"new_value_{i}" for i in range(125)}
        )

        composer = ThemeComposer()
        start_time = time.perf_counter()
        composed = composer.compose(base_theme, override_theme)
        composition_time = time.perf_counter() - start_time

        assert composition_time < 0.01, f"Composition took {composition_time:.3f}s"


# Performance benchmark integration
class TestThemeBenchmarks(ThemedTestCase):
    """Integration with performance benchmarking system."""

    def test_theme_benchmark_integration(self):
        """Verify Theme integrates with benchmarking framework."""
        from vfwidgets_theme.testing.benchmarks import ThemeBenchmark

        benchmark = ThemeBenchmark()

        theme = Theme(
            name="benchmark_test",
            colors={"primary": "#ff0000"},
            styles={"font": "Arial"}
        )

        # Benchmark theme operations
        results = benchmark.benchmark_property_access(theme, iterations=1000)

        assert results.average_time < 0.000001  # Sub-microsecond
        assert results.total_operations == 1000
        assert results.errors == 0


if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([__file__, "-v", "--cov=vfwidgets_theme.core.theme"])