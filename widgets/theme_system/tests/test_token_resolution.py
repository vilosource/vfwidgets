"""Tests for unified token resolution API.

This module tests the new unified token resolution system that integrates
ThemedWidget with the override system.

Test Coverage:
- Token type resolvers (ColorTokenResolver, etc.)
- ThemeManager.resolve_token() method
- Override priority (user > app > theme)
- Fallback handling
- ThemedWidget integration
- Cache invalidation
"""

import pytest
from PySide6.QtWidgets import QWidget

from vfwidgets_theme.widgets.base import ThemedWidget


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def manager_with_theme():
    """Create ThemeManager with a test theme loaded."""
    from vfwidgets_theme.core.manager import create_theme_manager

    manager = create_theme_manager()

    # Use the built-in dark theme for testing
    if not manager.has_theme("dark"):
        # If no theme loaded, load the default
        from pathlib import Path
        theme_dir = Path(__file__).parent.parent / "themes"
        if theme_dir.exists():
            manager.discover_themes(theme_dir, recursive=False)

    if manager.has_theme("dark"):
        manager.set_theme("dark")

    yield manager

    # Cleanup: clear overrides for next test
    manager.clear_user_overrides(notify=False)
    manager.clear_app_overrides(notify=False)


# ============================================================================
# Token Resolver Tests
# ============================================================================

class TestTokenResolvers:
    """Test individual token type resolvers."""

    def test_color_resolver_exists(self):
        """ColorTokenResolver should be importable."""
        from vfwidgets_theme.core.token_types import ColorTokenResolver
        assert ColorTokenResolver is not None

    def test_color_resolver_can_override(self):
        """ColorTokenResolver should support override system."""
        from vfwidgets_theme.core.token_types import ColorTokenResolver

        resolver = ColorTokenResolver()
        assert resolver.can_override() is True

    def test_color_resolver_validate_hex(self):
        """ColorTokenResolver should validate hex colors."""
        from vfwidgets_theme.core.token_types import ColorTokenResolver

        resolver = ColorTokenResolver()
        assert resolver.validate_value("#ff0000") is True
        assert resolver.validate_value("#FFF") is True
        assert resolver.validate_value("#ffffff") is True

    def test_color_resolver_validate_named(self):
        """ColorTokenResolver should validate named colors."""
        from vfwidgets_theme.core.token_types import ColorTokenResolver

        resolver = ColorTokenResolver()
        assert resolver.validate_value("red") is True
        assert resolver.validate_value("blue") is True
        assert resolver.validate_value("transparent") is True

    def test_color_resolver_validate_invalid(self):
        """ColorTokenResolver should reject invalid colors."""
        from vfwidgets_theme.core.token_types import ColorTokenResolver

        resolver = ColorTokenResolver()
        assert resolver.validate_value("invalid") is False
        assert resolver.validate_value("") is False
        assert resolver.validate_value("#gg0000") is False

    def test_color_resolver_from_theme(self, manager_with_theme):
        """ColorTokenResolver should resolve colors from theme."""
        from vfwidgets_theme.core.token_types import ColorTokenResolver

        resolver = ColorTokenResolver()

        # Get theme from manager
        theme = manager_with_theme.current_theme

        # Test direct attribute access
        color = resolver.resolve_from_theme(
            theme,
            "editor.background",
            fallback="#ffffff"
        )
        # Should return a color (exact value depends on theme)
        assert color is not None

    def test_color_resolver_from_theme_fallback(self, manager_with_theme):
        """ColorTokenResolver should use fallback for missing tokens."""
        from vfwidgets_theme.core.token_types import ColorTokenResolver

        resolver = ColorTokenResolver()

        # Get theme from manager
        theme = manager_with_theme.current_theme

        color = resolver.resolve_from_theme(
            theme,
            "nonexistent.token",
            fallback="#ffffff"
        )
        assert color == "#ffffff"

    def test_token_type_enum_exists(self):
        """TokenType enum should be importable."""
        from vfwidgets_theme.core.token_types import TokenType
        assert TokenType is not None

    def test_token_type_has_color(self):
        """TokenType should have COLOR value."""
        from vfwidgets_theme.core.token_types import TokenType
        assert hasattr(TokenType, "COLOR")

    def test_token_type_has_font(self):
        """TokenType should have FONT value."""
        from vfwidgets_theme.core.token_types import TokenType
        assert hasattr(TokenType, "FONT")


# ============================================================================
# ThemeManager.resolve_token() Tests
# ============================================================================

class TestThemeManagerResolveToken:
    """Test ThemeManager.resolve_token() method."""

    def test_resolve_token_method_exists(self, manager_with_theme):
        """ThemeManager should have resolve_token() method."""
        assert hasattr(manager_with_theme, "resolve_token")

    def test_resolve_color_with_user_override(self, manager_with_theme):
        """User override should take priority over theme."""
        manager = manager_with_theme

        # Set user override (use a token that exists in theme)
        manager.set_user_override("colors.background", "#ff0000")

        # Resolve should return override
        from vfwidgets_theme.core.token_types import TokenType
        color = manager.resolve_token("colors.background", TokenType.COLOR)
        assert color == "#ff0000"

    def test_resolve_color_with_app_override(self, manager_with_theme):
        """App override should override theme but not user."""
        manager = manager_with_theme

        # Set app override
        manager.set_app_override("colors.background", "#00ff00")

        # Resolve should return app override
        from vfwidgets_theme.core.token_types import TokenType
        color = manager.resolve_token("colors.background", TokenType.COLOR)
        assert color == "#00ff00"

    def test_resolve_color_without_override(self, manager_with_theme):
        """Should fall back to theme value when no override."""
        manager = manager_with_theme

        # No overrides set - use token that exists in theme
        from vfwidgets_theme.core.token_types import TokenType
        color = manager.resolve_token("colors.background", TokenType.COLOR)

        # Should return theme value (not None)
        assert color is not None
        assert isinstance(color, str)

    def test_resolve_color_priority_user_over_app(self, manager_with_theme):
        """User override should have priority over app override."""
        manager = manager_with_theme

        # Set both overrides
        manager.set_app_override("colors.background", "#00ff00")
        manager.set_user_override("colors.background", "#ff0000")

        # User override should win
        from vfwidgets_theme.core.token_types import TokenType
        color = manager.resolve_token("colors.background", TokenType.COLOR)
        assert color == "#ff0000"

    def test_resolve_color_priority_app_over_theme(self, manager_with_theme):
        """App override should have priority over theme."""
        manager = manager_with_theme

        # Set only app override
        manager.set_app_override("colors.background", "#00ff00")

        # App override should win over theme
        from vfwidgets_theme.core.token_types import TokenType
        color = manager.resolve_token("colors.background", TokenType.COLOR)
        assert color == "#00ff00"

    def test_resolve_with_fallback(self, manager_with_theme):
        """Should return fallback when token not found."""
        manager = manager_with_theme

        from vfwidgets_theme.core.token_types import TokenType
        color = manager.resolve_token(
            "nonexistent.token",
            TokenType.COLOR,
            fallback="#ffffff"
        )
        assert color == "#ffffff"

    def test_resolve_without_fallback(self, manager_with_theme):
        """Should return None when token not found and no fallback."""
        manager = manager_with_theme

        from vfwidgets_theme.core.token_types import TokenType
        color = manager.resolve_token(
            "nonexistent.token",
            TokenType.COLOR
        )
        assert color is None

    def test_resolve_skip_overrides(self, manager_with_theme):
        """Should skip overrides when check_overrides=False."""
        manager = manager_with_theme

        # Get the original theme value first
        from vfwidgets_theme.core.token_types import TokenType
        original_color = manager.resolve_token(
            "colors.background",
            TokenType.COLOR,
            check_overrides=False
        )

        # Set user override
        manager.set_user_override("colors.background", "#ff0000")

        # Resolve with check_overrides=False should return theme value (same as original)
        color = manager.resolve_token(
            "colors.background",
            TokenType.COLOR,
            check_overrides=False
        )
        assert color == original_color  # Theme value, not override
        assert color != "#ff0000"  # Not the override


# ============================================================================
# Convenience Method Tests
# ============================================================================

class TestConvenienceMethods:
    """Test convenience methods for common token types."""

    def test_resolve_color_method_exists(self, manager_with_theme):
        """ThemeManager should have resolve_color() method."""
        assert hasattr(manager_with_theme, "resolve_color")

    def test_resolve_font_method_exists(self, manager_with_theme):
        """ThemeManager should have resolve_font() method."""
        assert hasattr(manager_with_theme, "resolve_font")

    def test_resolve_size_method_exists(self, manager_with_theme):
        """ThemeManager should have resolve_size() method."""
        assert hasattr(manager_with_theme, "resolve_size")

    def test_resolve_color_convenience(self, manager_with_theme):
        """resolve_color() should work same as explicit resolve_token()."""
        manager = manager_with_theme

        manager.set_user_override("colors.background", "#ff0000")

        # Both methods should return same result
        from vfwidgets_theme.core.token_types import TokenType
        color1 = manager.resolve_token("colors.background", TokenType.COLOR)
        color2 = manager.resolve_color("colors.background")

        assert color1 == color2
        assert color2 == "#ff0000"

    def test_resolve_color_with_fallback(self, manager_with_theme):
        """resolve_color() should support fallback."""
        manager = manager_with_theme

        color = manager.resolve_color(
            "nonexistent.token",
            fallback="#ffffff"
        )
        assert color == "#ffffff"


# ============================================================================
# ThemedWidget Integration Tests
# ============================================================================

class TestThemedWidgetIntegration:
    """Test that ThemedWidget uses token resolution correctly."""

    def test_themed_widget_resolves_overrides(self, qtbot):
        """ThemedWidget should respect color overrides."""
        from vfwidgets_theme.widgets.application import ThemedApplication

        # Get or create app
        app = ThemedApplication.instance()
        if app is None:
            app = ThemedApplication([])

        # Custom widget with theme config
        class TestWidget(ThemedWidget, QWidget):
            theme_config = {
                "bg": "colors.background",
                "fg": "colors.foreground",
            }

        widget = TestWidget()
        qtbot.addWidget(widget)

        # Set override
        app.customize_color("colors.background", "#ff0000")

        # Widget should resolve to override (not theme)
        # Note: May need to trigger theme update
        widget._on_global_theme_changed(app._theme_manager.current_theme.name)

        assert widget.theme.bg == "#ff0000"

    def test_themed_widget_cache_invalidation(self, qtbot):
        """ThemedWidget cache should invalidate when override changes."""
        from vfwidgets_theme.widgets.application import ThemedApplication

        app = ThemedApplication.instance()
        if app is None:
            app = ThemedApplication([])

        class TestWidget(ThemedWidget, QWidget):
            theme_config = {
                "bg": "colors.background",
            }

        widget = TestWidget()
        qtbot.addWidget(widget)

        # Initial value
        initial_bg = widget.theme.bg
        assert initial_bg is not None

        # Set override
        app.customize_color("colors.background", "#00ff00")
        widget._on_global_theme_changed(app._theme_manager.current_theme.name)

        # Should get new value (cache invalidated)
        new_bg = widget.theme.bg
        assert new_bg == "#00ff00"

    def test_themed_widget_multiple_properties(self, qtbot):
        """ThemedWidget should resolve multiple properties with overrides."""
        from vfwidgets_theme.widgets.application import ThemedApplication

        app = ThemedApplication.instance()
        if app is None:
            app = ThemedApplication([])

        class TestWidget(ThemedWidget, QWidget):
            theme_config = {
                "bg": "colors.background",
                "fg": "colors.foreground",
                "tab_bg": "tab.activeBackground",
            }

        widget = TestWidget()
        qtbot.addWidget(widget)

        # Set multiple overrides
        app.customize_color("colors.background", "#111111")
        app.customize_color("tab.activeBackground", "#222222")
        # Don't override colors.foreground

        widget._on_global_theme_changed(app._theme_manager.current_theme.name)

        # Check resolution
        assert widget.theme.bg == "#111111"  # Override
        assert widget.theme.tab_bg == "#222222"  # Override
        # fg should be theme default (not the override)
        assert widget.theme.fg is not None
        assert widget.theme.fg != "#111111"  # Not bg override
        assert widget.theme.fg != "#222222"  # Not tab override

    def test_themed_widget_inherits_theme_config(self, qtbot):
        """Subclasses should inherit and merge theme_config."""
        from vfwidgets_theme.widgets.application import ThemedApplication

        app = ThemedApplication.instance()
        if app is None:
            app = ThemedApplication([])

        # Base widget with theme config
        class BaseWidget(ThemedWidget, QWidget):
            theme_config = {
                "bg": "colors.background",
            }

        # Subclass with additional config
        class DerivedWidget(BaseWidget):
            theme_config = {
                **BaseWidget.theme_config,
                "fg": "colors.foreground",
            }

        widget = DerivedWidget()
        qtbot.addWidget(widget)

        # Both properties should be available and resolve to colors
        bg = widget.theme.bg
        fg = widget.theme.fg
        assert bg is not None
        assert fg is not None
        # Should be valid color strings
        from PySide6.QtGui import QColor
        assert QColor.isValidColor(bg) if isinstance(bg, str) else True
        assert QColor.isValidColor(fg) if isinstance(fg, str) else True


# ============================================================================
# Performance Tests
# ============================================================================

class TestPerformance:
    """Test performance of token resolution."""

    def test_resolve_token_performance(self, manager_with_theme, benchmark):
        """resolve_token() should be fast (< 0.5ms)."""
        manager = manager_with_theme

        from vfwidgets_theme.core.token_types import TokenType

        def resolve():
            return manager.resolve_token("editor.background", TokenType.COLOR)

        # Benchmark the resolution
        result = benchmark(resolve)

        # Should return correct value
        assert result is not None

        # Performance target: < 0.5ms (500 microseconds)
        assert benchmark.stats.stats.mean < 0.0005

    def test_resolve_with_cache_hit(self, manager_with_theme, qtbot):
        """Cached resolution should be very fast (< 0.1ms)."""
        from vfwidgets_theme.widgets.application import ThemedApplication

        app = ThemedApplication.instance()
        if app is None:
            app = ThemedApplication([])

        class TestWidget(ThemedWidget, QWidget):
            theme_config = {
                "bg": "editor.background",
            }

        widget = TestWidget()
        qtbot.addWidget(widget)

        # First access (cache miss)
        _ = widget.theme.bg

        # Measure second access (cache hit)
        import time
        start = time.perf_counter()
        _ = widget.theme.bg
        elapsed = time.perf_counter() - start

        # Cache hit should be < 0.1ms (100 microseconds)
        assert elapsed < 0.0001


# ============================================================================
# Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_resolve_empty_token(self, manager_with_theme):
        """Should handle empty token gracefully."""
        manager = manager_with_theme

        from vfwidgets_theme.core.token_types import TokenType
        color = manager.resolve_token("", TokenType.COLOR, fallback="#fff")

        # Should return fallback
        assert color == "#fff"

    def test_resolve_none_token(self, manager_with_theme):
        """Should handle None token gracefully."""
        manager = manager_with_theme

        from vfwidgets_theme.core.token_types import TokenType

        # Should not crash, may return None or fallback
        try:
            color = manager.resolve_token(None, TokenType.COLOR, fallback="#fff")
            assert color is not None  # Should get fallback or handle gracefully
        except (TypeError, AttributeError):
            # Acceptable to raise error for None token
            pass

    def test_resolve_invalid_type(self, manager_with_theme):
        """Should handle invalid token type gracefully."""
        manager = manager_with_theme

        # Try with invalid type object
        try:
            color = manager.resolve_token(
                "editor.background",
                token_type="INVALID",
                fallback="#fff"
            )
            # Should return fallback or theme value
            assert color is not None
        except (ValueError, TypeError):
            # Acceptable to raise error for invalid type
            pass

    def test_override_after_removal(self, manager_with_theme):
        """Override removal should restore theme value."""
        manager = manager_with_theme

        # Get original theme value
        from vfwidgets_theme.core.token_types import TokenType
        original_color = manager.resolve_token("colors.background", TokenType.COLOR)

        # Set and then remove override
        manager.set_user_override("colors.background", "#ff0000")

        # Verify override is active
        override_color = manager.resolve_token("colors.background", TokenType.COLOR)
        assert override_color == "#ff0000"

        # Remove override
        manager.remove_user_override("colors.background")

        # Should return original theme value
        color = manager.resolve_token("colors.background", TokenType.COLOR)
        assert color == original_color  # Back to original theme value
        assert color != "#ff0000"  # Not the override anymore


# ============================================================================
# Thread Safety Tests
# ============================================================================

class TestThreadSafety:
    """Test thread-safe operations."""

    def test_concurrent_resolve(self, manager_with_theme):
        """Multiple threads should be able to resolve tokens safely."""
        import threading

        manager = manager_with_theme
        results = []
        errors = []

        def resolve_many():
            try:
                from vfwidgets_theme.core.token_types import TokenType
                for _ in range(100):
                    color = manager.resolve_token("colors.background", TokenType.COLOR)
                    results.append(color)
            except Exception as e:
                errors.append(e)

        # Start multiple threads
        threads = [threading.Thread(target=resolve_many) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # No errors should occur
        assert len(errors) == 0

        # All results should be valid
        assert len(results) == 1000
        assert all(r is not None for r in results)

    def test_concurrent_override_and_resolve(self, manager_with_theme):
        """Concurrent override changes and resolution should be safe."""
        import threading

        manager = manager_with_theme
        errors = []

        def set_overrides():
            try:
                for i in range(50):
                    manager.set_user_override(
                        "colors.background",
                        f"#{i:02x}0000"
                    )
            except Exception as e:
                errors.append(e)

        def resolve_many():
            try:
                from vfwidgets_theme.core.token_types import TokenType
                for _ in range(50):
                    manager.resolve_token("colors.background", TokenType.COLOR)
            except Exception as e:
                errors.append(e)

        # Start mixed threads
        threads = []
        for _ in range(5):
            threads.append(threading.Thread(target=set_overrides))
            threads.append(threading.Thread(target=resolve_many))

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # No errors should occur
        assert len(errors) == 0
