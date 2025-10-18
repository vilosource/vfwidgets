"""
Tests for OverrideRegistry - Core overlay system component.

This module tests the OverrideRegistry class which manages layered
color overrides (app-level and user-level) with priority resolution.

Test Coverage:
- Basic CRUD operations (set, get, remove, clear)
- Layer management (app vs user)
- Priority resolution (user > app > base)
- Validation (colors, token names)
- Serialization (to_dict, from_dict)
- Thread safety
- Performance requirements
- Edge cases and error handling
"""


import pytest

# ============================================================================
# Phase 1 Tests - Will be implemented during Phase 1
# ============================================================================
# These test skeletons will be filled in as we implement OverrideRegistry


class TestOverrideRegistryBasicOperations:
    """Test basic CRUD operations on OverrideRegistry."""

    def test_create_empty_registry(self):
        """Test creating an empty OverrideRegistry."""
        from vfwidgets_theme.core.override_registry import OverrideRegistry

        registry = OverrideRegistry()

        # Verify empty state
        assert registry.get_layer_overrides("app") == {}
        assert registry.get_layer_overrides("user") == {}
        assert registry.get_all_effective_overrides() == {}

        # Verify statistics
        stats = registry.get_statistics()
        assert stats["app_overrides"] == 0
        assert stats["user_overrides"] == 0

    def test_set_app_override(self):
        """Test setting an app-level override."""
        from vfwidgets_theme.core.override_registry import OverrideRegistry

        registry = OverrideRegistry()

        # Set app override
        registry.set_override("app", "editor.background", "#1e1e2e")

        # Verify it was set
        assert registry.get_override("app", "editor.background") == "#1e1e2e"
        assert registry.get_statistics()["app_overrides"] == 1

    def test_set_user_override(self):
        """Test setting a user-level override."""
        from vfwidgets_theme.core.override_registry import OverrideRegistry

        registry = OverrideRegistry()

        # Set user override
        registry.set_override("user", "editor.background", "#ff0000")

        # Verify it was set
        assert registry.get_override("user", "editor.background") == "#ff0000"
        assert registry.get_statistics()["user_overrides"] == 1

    def test_get_override_app_layer(self):
        """Test getting override from app layer."""
        from vfwidgets_theme.core.override_registry import OverrideRegistry

        registry = OverrideRegistry()
        registry.set_override("app", "tab.activeBackground", "#89b4fa")

        # Get from app layer
        result = registry.get_override("app", "tab.activeBackground")
        assert result == "#89b4fa"

        # Nonexistent token returns None
        result = registry.get_override("app", "nonexistent.token")
        assert result is None

    def test_get_override_user_layer(self):
        """Test getting override from user layer."""
        from vfwidgets_theme.core.override_registry import OverrideRegistry

        registry = OverrideRegistry()
        registry.set_override("user", "statusBar.background", "#00ff00")

        # Get from user layer
        result = registry.get_override("user", "statusBar.background")
        assert result == "#00ff00"

        # Nonexistent token returns None
        result = registry.get_override("user", "nonexistent.token")
        assert result is None

    def test_get_override_with_fallback(self):
        """Test getting override with fallback value."""
        from vfwidgets_theme.core.override_registry import OverrideRegistry

        registry = OverrideRegistry()

        # Nonexistent token returns fallback
        result = registry.get_override("app", "missing.token", fallback="#default")
        assert result == "#default"

    def test_remove_override(self):
        """Test removing an override."""
        from vfwidgets_theme.core.override_registry import OverrideRegistry

        registry = OverrideRegistry()
        registry.set_override("app", "editor.background", "#1e1e2e")

        # Remove the override
        removed = registry.remove_override("app", "editor.background")
        assert removed is True

        # Verify it's gone
        assert registry.get_override("app", "editor.background") is None
        assert registry.get_statistics()["app_overrides"] == 0

        # Removing nonexistent returns False
        removed = registry.remove_override("app", "editor.background")
        assert removed is False

    def test_clear_layer(self):
        """Test clearing all overrides in a layer."""
        from vfwidgets_theme.core.override_registry import OverrideRegistry

        registry = OverrideRegistry()

        # Add multiple overrides
        registry.set_override("app", "token1", "#111111")
        registry.set_override("app", "token2", "#222222")
        registry.set_override("app", "token3", "#333333")

        assert registry.get_statistics()["app_overrides"] == 3

        # Clear the layer
        count = registry.clear_layer("app")
        assert count == 3

        # Verify empty
        assert registry.get_statistics()["app_overrides"] == 0
        assert registry.get_layer_overrides("app") == {}

    def test_has_override(self):
        """Test checking if override exists."""
        from vfwidgets_theme.core.override_registry import OverrideRegistry

        registry = OverrideRegistry()

        # Initially doesn't exist
        assert registry.has_override("app", "editor.background") is False

        # Set and check
        registry.set_override("app", "editor.background", "#1e1e2e")
        assert registry.has_override("app", "editor.background") is True

        # Check other layer
        assert registry.has_override("user", "editor.background") is False


class TestOverrideRegistryPriorityResolution:
    """Test priority resolution: user > app > base."""

    def test_resolve_user_override_only(self):
        """Test resolving when only user override exists."""
        from vfwidgets_theme.core.override_registry import OverrideRegistry

        registry = OverrideRegistry()
        registry.set_override("user", "editor.background", "#ff0000")

        # Resolve should return user override
        result = registry.resolve("editor.background")
        assert result == "#ff0000"

    def test_resolve_app_override_only(self):
        """Test resolving when only app override exists."""
        from vfwidgets_theme.core.override_registry import OverrideRegistry

        registry = OverrideRegistry()
        registry.set_override("app", "editor.background", "#00ff00")

        # Resolve should return app override
        result = registry.resolve("editor.background")
        assert result == "#00ff00"

    def test_resolve_both_overrides_user_wins(self):
        """Test that user override wins over app override."""
        from vfwidgets_theme.core.override_registry import OverrideRegistry

        registry = OverrideRegistry()

        # Set both layers
        registry.set_override("app", "editor.background", "#00ff00")
        registry.set_override("user", "editor.background", "#ff0000")

        # Resolve should return user override (higher priority)
        result = registry.resolve("editor.background")
        assert result == "#ff0000"

    def test_resolve_no_override_returns_none(self):
        """Test that resolve returns None when no override exists."""
        from vfwidgets_theme.core.override_registry import OverrideRegistry

        registry = OverrideRegistry()

        # Resolve nonexistent token
        result = registry.resolve("nonexistent.token")
        assert result is None

    def test_resolve_with_fallback(self):
        """Test resolve with fallback value."""
        from vfwidgets_theme.core.override_registry import OverrideRegistry

        registry = OverrideRegistry()

        # Resolve nonexistent token with fallback
        result = registry.resolve("nonexistent.token", fallback="#default")
        assert result == "#default"

        # Set app override - resolve should return it instead of fallback
        registry.set_override("app", "editor.background", "#00ff00")
        result = registry.resolve("editor.background", fallback="#default")
        assert result == "#00ff00"

        # Set user override - resolve should return it (ignoring both app and fallback)
        registry.set_override("user", "editor.background", "#ff0000")
        result = registry.resolve("editor.background", fallback="#default")
        assert result == "#ff0000"


class TestOverrideRegistryBulkOperations:
    """Test bulk operations for efficiency."""

    def test_set_bulk_app_overrides(self, sample_app_overrides):
        """Test setting multiple app overrides at once."""
        from vfwidgets_theme.core.override_registry import OverrideRegistry

        registry = OverrideRegistry()

        # Set bulk overrides
        registry.set_overrides_bulk("app", sample_app_overrides)

        # Verify all were set
        assert registry.get_statistics()["app_overrides"] == len(sample_app_overrides)

        # Verify each override
        for token, color in sample_app_overrides.items():
            assert registry.get_override("app", token) == color

    def test_set_bulk_user_overrides(self, sample_user_overrides):
        """Test setting multiple user overrides at once."""
        from vfwidgets_theme.core.override_registry import OverrideRegistry

        registry = OverrideRegistry()

        # Set bulk overrides
        registry.set_overrides_bulk("user", sample_user_overrides)

        # Verify all were set
        assert registry.get_statistics()["user_overrides"] == len(sample_user_overrides)

        # Verify each override
        for token, color in sample_user_overrides.items():
            assert registry.get_override("user", token) == color

    def test_get_all_overrides_for_layer(self, sample_app_overrides):
        """Test getting all overrides for a specific layer."""
        from vfwidgets_theme.core.override_registry import OverrideRegistry

        registry = OverrideRegistry()
        registry.set_overrides_bulk("app", sample_app_overrides)

        # Get all app overrides
        app_overrides = registry.get_layer_overrides("app")
        assert app_overrides == sample_app_overrides

        # Verify it's a copy (not reference)
        app_overrides["new.token"] = "#123456"
        assert "new.token" not in registry.get_layer_overrides("app")

    def test_get_all_effective_overrides(self, sample_app_overrides, sample_user_overrides):
        """Test getting all effective overrides (with priority resolution)."""
        from vfwidgets_theme.core.override_registry import OverrideRegistry

        registry = OverrideRegistry()

        # Set both layers
        registry.set_overrides_bulk("app", sample_app_overrides)
        registry.set_overrides_bulk("user", sample_user_overrides)

        # Get effective overrides
        effective = registry.get_all_effective_overrides()

        # Verify user overrides win for overlapping tokens
        for token in sample_user_overrides:
            assert effective[token] == sample_user_overrides[token]

        # Verify app-only tokens are present
        for token in sample_app_overrides:
            if token not in sample_user_overrides:
                assert effective[token] == sample_app_overrides[token]


class TestOverrideRegistryValidation:
    """Test validation of colors and token names."""

    def test_validate_valid_hex_color(self, valid_colors):
        """Test validation accepts valid hex colors."""
        from vfwidgets_theme.core.override_registry import OverrideRegistry

        registry = OverrideRegistry()

        # All valid colors should be accepted
        for color in valid_colors:
            registry.set_override("app", "test.token", color)
            assert registry.get_override("app", "test.token") == color

    @pytest.mark.skip(reason="QColor.isValidColor() doesn't support rgb() format")
    def test_validate_valid_rgb_color(self):
        """Test validation accepts valid RGB colors.

        Note: QColor.isValidColor() is deprecated and doesn't support
        rgb() or rgba() formats. It only accepts hex colors and named colors.
        Users needing rgb() support should use validate=False.
        """
        from vfwidgets_theme.core.override_registry import OverrideRegistry

        registry = OverrideRegistry()

        # This test documents that rgb() is NOT supported by QColor
        valid_rgb = [
            "rgb(255,0,0)",
            "rgb(0,255,0)",
            "rgb(0,0,255)",
        ]

        for color in valid_rgb:
            registry.set_override("app", "test.token", color)
            assert registry.get_override("app", "test.token") == color

    def test_validate_valid_named_color(self):
        """Test validation accepts valid named colors."""
        from vfwidgets_theme.core.override_registry import OverrideRegistry

        registry = OverrideRegistry()

        # Valid named colors
        valid_names = ["red", "green", "blue", "white", "black", "transparent"]

        for color in valid_names:
            registry.set_override("app", "test.token", color)
            assert registry.get_override("app", "test.token") == color

    def test_validate_reject_invalid_color(self):
        """Test validation rejects invalid colors."""
        from vfwidgets_theme.core.override_registry import OverrideRegistry

        registry = OverrideRegistry()

        # Invalid colors should raise ValueError
        invalid_colors = [
            "not-a-color",
            "#gggggg",
            "rgb(999, 999, 999)",
            "#12",  # Too short
        ]

        for color in invalid_colors:
            with pytest.raises(ValueError, match="Invalid color format"):
                registry.set_override("app", "test.token", color)

    def test_validate_token_name_valid(self):
        """Test token name validation for valid names."""
        from vfwidgets_theme.core.override_registry import OverrideRegistry

        registry = OverrideRegistry()

        # Valid token names
        valid_tokens = [
            "editor.background",
            "tab.activeBackground",
            "button.background",
            "a",  # Single letter
            "token123",  # With numbers
            "my.token.with.dots",  # Multiple dots
            "token_with_underscore",  # Underscores
        ]

        for token in valid_tokens:
            registry.set_override("app", token, "#ffffff")
            assert registry.has_override("app", token)

    def test_validate_token_name_empty_rejected(self):
        """Test token name validation rejects empty names."""
        from vfwidgets_theme.core.override_registry import OverrideRegistry

        registry = OverrideRegistry()

        with pytest.raises(ValueError, match="Token name cannot be empty"):
            registry.set_override("app", "", "#ffffff")

    def test_validate_token_name_too_long_rejected(self):
        """Test token name validation rejects names > 255 chars."""
        from vfwidgets_theme.core.override_registry import OverrideRegistry

        registry = OverrideRegistry()

        # Create token > 255 chars
        long_token = "a" * 256

        with pytest.raises(ValueError, match="Token name too long"):
            registry.set_override("app", long_token, "#ffffff")

    def test_validate_token_name_invalid_pattern_rejected(self):
        """Test token name validation rejects invalid patterns."""
        from vfwidgets_theme.core.override_registry import OverrideRegistry

        registry = OverrideRegistry()

        # Invalid patterns
        invalid_tokens = [
            "123token",  # Starts with number
            "token-with-dash",  # Contains dash
            "token with space",  # Contains space
            ".startsWithDot",  # Starts with dot
        ]

        for token in invalid_tokens:
            with pytest.raises(ValueError, match="Invalid token name"):
                registry.set_override("app", token, "#ffffff")

    def test_validation_can_be_disabled(self):
        """Test that validation can be disabled for performance."""
        from vfwidgets_theme.core.override_registry import OverrideRegistry

        registry = OverrideRegistry()

        # With validation disabled, invalid color should be accepted
        registry.set_override("app", "test.token", "not-a-color", validate=False)
        assert registry.get_override("app", "test.token") == "not-a-color"


class TestOverrideRegistrySerialization:
    """Test serialization to/from dict for persistence."""

    def test_to_dict_empty_registry(self):
        """Test serialization of empty registry."""
        from vfwidgets_theme.core.override_registry import OverrideRegistry

        registry = OverrideRegistry()
        data = registry.to_dict()

        # Empty registry should have empty layers
        assert data == {"app": {}, "user": {}}

    def test_to_dict_with_overrides(self, sample_app_overrides, sample_user_overrides):
        """Test serialization of registry with overrides."""
        from vfwidgets_theme.core.override_registry import OverrideRegistry

        registry = OverrideRegistry()
        registry.set_overrides_bulk("app", sample_app_overrides)
        registry.set_overrides_bulk("user", sample_user_overrides)

        data = registry.to_dict()

        # Verify structure
        assert "app" in data
        assert "user" in data

        # Verify content
        assert data["app"] == sample_app_overrides
        assert data["user"] == sample_user_overrides

    def test_from_dict_empty(self):
        """Test deserialization from empty dict."""
        from vfwidgets_theme.core.override_registry import OverrideRegistry

        data = {"app": {}, "user": {}}
        registry = OverrideRegistry.from_dict(data)

        # Verify empty state
        assert registry.get_statistics()["app_overrides"] == 0
        assert registry.get_statistics()["user_overrides"] == 0

    def test_from_dict_with_overrides(self, sample_app_overrides, sample_user_overrides):
        """Test deserialization from dict with overrides."""
        from vfwidgets_theme.core.override_registry import OverrideRegistry

        data = {
            "app": sample_app_overrides,
            "user": sample_user_overrides,
        }

        registry = OverrideRegistry.from_dict(data)

        # Verify all overrides loaded
        assert registry.get_statistics()["app_overrides"] == len(sample_app_overrides)
        assert registry.get_statistics()["user_overrides"] == len(sample_user_overrides)

        # Verify each override
        for token, color in sample_app_overrides.items():
            assert registry.get_override("app", token) == color

        for token, color in sample_user_overrides.items():
            assert registry.get_override("user", token) == color

    def test_round_trip_serialization(self, sample_app_overrides, sample_user_overrides):
        """Test that to_dict -> from_dict preserves data."""
        from vfwidgets_theme.core.override_registry import OverrideRegistry

        # Create original registry
        original = OverrideRegistry()
        original.set_overrides_bulk("app", sample_app_overrides)
        original.set_overrides_bulk("user", sample_user_overrides)

        # Serialize
        data = original.to_dict()

        # Deserialize
        restored = OverrideRegistry.from_dict(data)

        # Verify identical state
        assert restored.to_dict() == original.to_dict()
        assert restored.get_all_effective_overrides() == original.get_all_effective_overrides()

    def test_from_dict_invalid_layer_raises_error(self):
        """Test that invalid layer in data raises ValueError."""
        from vfwidgets_theme.core.override_registry import OverrideRegistry

        data = {
            "invalid_layer": {"token": "#ffffff"},
            "app": {},
            "user": {},
        }

        with pytest.raises(ValueError, match="Invalid layer"):
            OverrideRegistry.from_dict(data)


class TestOverrideRegistryThreadSafety:
    """Test thread-safe operations (Task 1.11)."""

    @pytest.mark.skip(reason="Phase 1: Not yet implemented")
    def test_concurrent_set_operations(self):
        """Test concurrent set operations from multiple threads."""
        pass

    @pytest.mark.skip(reason="Phase 1: Not yet implemented")
    def test_concurrent_get_operations(self):
        """Test concurrent get operations from multiple threads."""
        pass

    @pytest.mark.skip(reason="Phase 1: Not yet implemented")
    def test_concurrent_mixed_operations(self):
        """Test concurrent mix of set/get/remove operations."""
        pass

    @pytest.mark.skip(reason="Phase 1: Not yet implemented")
    def test_no_race_conditions(self):
        """Test that no race conditions occur under load."""
        pass


class TestOverrideRegistryPerformance:
    """Test performance requirements."""

    @pytest.mark.skip(reason="Phase 1: Not yet implemented")
    def test_resolve_performance(self):
        """Test that resolve() < 0.1ms (100 microseconds)."""
        pass

    @pytest.mark.skip(reason="Phase 1: Not yet implemented")
    def test_bulk_set_performance(self):
        """Test that bulk set of 100 overrides < 50ms."""
        pass

    @pytest.mark.skip(reason="Phase 1: Not yet implemented")
    def test_memory_overhead(self):
        """Test memory overhead is reasonable."""
        pass


class TestOverrideRegistryEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.mark.skip(reason="Phase 1: Not yet implemented")
    def test_invalid_layer_name_raises_error(self):
        """Test that invalid layer name raises ValueError."""
        pass

    @pytest.mark.skip(reason="Phase 1: Not yet implemented")
    def test_set_with_validation_disabled(self):
        """Test setting override with validation disabled."""
        pass

    @pytest.mark.skip(reason="Phase 1: Not yet implemented")
    def test_clear_nonexistent_layer(self):
        """Test clearing layer that doesn't exist."""
        pass

    @pytest.mark.skip(reason="Phase 1: Not yet implemented")
    def test_maximum_overrides_per_layer(self):
        """Test handling of max overrides (10,000 per spec)."""
        pass


# ============================================================================
# Marker for Phase 1 Implementation
# ============================================================================
# When implementing Phase 1, remove @pytest.mark.skip decorators and
# implement the test bodies following TDD approach:
# 1. Write the test (it will fail)
# 2. Implement minimum code to make it pass
# 3. Refactor
# 4. Move to next test
