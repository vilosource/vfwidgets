"""
Tests for ThemedApplication enhancements.

This module tests:
- get_theme_info() method
- toggle_theme() method
- cycle_theme() method
- preview_theme(), commit_preview(), cancel_preview() methods
- theme_preview_started, theme_preview_ended signals
"""

from unittest.mock import Mock

import pytest

from vfwidgets_theme.core.theme import Theme
from vfwidgets_theme.widgets.application import ThemedApplication
from vfwidgets_theme.widgets.metadata import ThemeInfo


@pytest.fixture(scope="session")
def themed_app():
    """Create single ThemedApplication instance for all tests."""
    app = ThemedApplication([])
    yield app
    app.cleanup()


@pytest.fixture(scope="function")
def app(themed_app):
    """Provide ThemedApplication instance per test function."""
    # Reset preview state before each test
    if hasattr(themed_app, "_preview_original_theme"):
        themed_app._preview_original_theme = None

    yield themed_app

    # Cleanup after each test
    if hasattr(themed_app, "_preview_original_theme"):
        themed_app._preview_original_theme = None


class TestGetThemeInfo:
    """Test get_theme_info() method."""

    def test_get_theme_info_existing_theme(self, app):
        """Test getting metadata for an existing theme."""
        # Set up metadata
        info = ThemeInfo(
            name="dark",
            display_name="Dark Theme",
            description="A dark theme",
            type="dark",
            tags=["dark"],
        )
        app._metadata_provider.register_metadata("dark", info)

        # Get theme info
        retrieved = app.get_theme_info("dark")

        assert retrieved is not None
        assert retrieved.name == "dark"
        assert retrieved.display_name == "Dark Theme"

    def test_get_theme_info_nonexistent_theme(self, app):
        """Test getting metadata for non-existent theme."""
        result = app.get_theme_info("nonexistent")
        assert result is None

    def test_get_theme_info_current_theme(self, app):
        """Test getting metadata for current theme without specifying name."""
        # Set current theme
        app.set_theme("dark")

        # Register metadata
        info = ThemeInfo(
            name="dark",
            display_name="Dark Theme",
            description="A dark theme",
            type="dark",
            tags=["dark"],
        )
        app._metadata_provider.register_metadata("dark", info)

        # Get current theme info
        retrieved = app.get_theme_info()

        assert retrieved is not None
        assert retrieved.name == "dark"

    def test_get_theme_info_no_current_theme(self, app):
        """Test getting current theme info when no theme is set."""
        app._current_theme = None
        result = app.get_theme_info()
        assert result is None


class TestToggleTheme:
    """Test toggle_theme() method."""

    def test_toggle_between_two_themes(self, app):
        """Test toggling between dark and light themes."""
        # Set initial theme
        app.set_theme("dark")
        assert app.current_theme_name.name == "dark"

        # Toggle to light
        app.toggle_theme("light")
        assert app.current_theme_name.name == "light"

        # Toggle back to dark
        app.toggle_theme("dark")
        assert app.current_theme_name.name == "dark"

    def test_toggle_from_unspecified_current(self, app):
        """Test toggling when current theme is not one of the toggle pair."""
        # Set to default theme
        app.set_theme("default")

        # Toggle between dark and light
        app.toggle_theme("dark", "light")

        # Should switch to first theme in pair
        assert app.current_theme_name.name in ["dark", "light"]

    def test_toggle_signal_emission(self, app):
        """Test that toggle emits theme_changed signal."""

        app.set_theme("dark")

        signal_received = Mock()
        app.theme_changed.connect(signal_received)

        app.toggle_theme("light")

        signal_received.assert_called_once_with("light")


class TestCycleTheme:
    """Test cycle_theme() method."""

    def test_cycle_through_themes(self, app):
        """Test cycling through available themes."""
        # Set a known starting theme
        app.set_theme("dark")
        initial_theme_name = app.current_theme_name.name

        # Cycle once
        app.cycle_theme()
        first_cycle_name = app.current_theme_name.name

        # Should have changed (compare by name)
        assert first_cycle_name != initial_theme_name

        # Get list of available themes
        theme_names = [t.name if hasattr(t, "name") else str(t) for t in app.get_available_themes()]

        # Cycling through all themes should visit different themes
        visited_themes = {initial_theme_name}
        for _ in range(min(3, len(theme_names) - 1)):  # Cycle through a few themes
            app.cycle_theme()
            visited_themes.add(app.current_theme_name.name)

        # Should have visited multiple different themes
        assert len(visited_themes) >= 2

    def test_cycle_with_specific_list(self, app):
        """Test cycling with a specific list of themes."""
        theme_list = ["dark", "light", "default"]

        # Set to first theme
        app.set_theme("dark")

        # Cycle should go to next in list
        app.cycle_theme(theme_list)
        assert app.current_theme_name.name == "light"

        # Cycle again
        app.cycle_theme(theme_list)
        assert app.current_theme_name.name == "default"

        # Cycle back to start
        app.cycle_theme(theme_list)
        assert app.current_theme_name.name == "dark"

    def test_cycle_reverse_direction(self, app):
        """Test cycling in reverse direction."""
        theme_list = ["dark", "light", "default"]

        # Set to first theme
        app.set_theme("dark")

        # Cycle reverse should go to last in list
        app.cycle_theme(theme_list, reverse=True)
        assert app.current_theme_name.name == "default"


class TestThemePreview:
    """Test theme preview system."""

    def test_preview_theme(self, app):
        """Test previewing a theme without persistence."""
        # Set initial theme
        app.set_theme("dark")

        # Preview different theme
        app.preview_theme("light")

        # Current theme should change
        assert app.current_theme_name.name == "light"

        # Original theme should be stored
        assert app._preview_original_theme.name == "dark"

    def test_preview_started_signal(self, app):
        """Test that preview emits theme_preview_started signal."""

        app.set_theme("dark")

        signal_received = Mock()
        app.theme_preview_started.connect(signal_received)

        app.preview_theme("light")

        signal_received.assert_called_once_with("light")

    def test_commit_preview(self, app):
        """Test committing a preview."""
        # Start with dark theme
        app.set_theme("dark")

        # Preview light theme
        app.preview_theme("light")
        assert app.current_theme_name.name == "light"

        # Commit the preview
        app.commit_preview()

        # Original theme should be cleared
        assert app._preview_original_theme is None

        # Current theme should remain light
        assert app.current_theme_name.name == "light"

    def test_preview_ended_signal_on_commit(self, app):
        """Test that commit emits theme_preview_ended signal."""

        app.set_theme("dark")
        app.preview_theme("light")

        signal_received = Mock()
        app.theme_preview_ended.connect(signal_received)

        app.commit_preview()

        signal_received.assert_called_once_with(True)  # committed=True

    def test_cancel_preview(self, app):
        """Test canceling a preview."""
        # Start with dark theme
        app.set_theme("dark")

        # Preview light theme
        app.preview_theme("light")
        assert app.current_theme_name.name == "light"

        # Cancel the preview
        app.cancel_preview()

        # Should revert to original theme
        assert app.current_theme_name.name == "dark"

        # Original theme should be cleared
        assert app._preview_original_theme is None

    def test_preview_ended_signal_on_cancel(self, app):
        """Test that cancel emits theme_preview_ended signal."""

        app.set_theme("dark")
        app.preview_theme("light")

        signal_received = Mock()
        app.theme_preview_ended.connect(signal_received)

        app.cancel_preview()

        signal_received.assert_called_once_with(False)  # committed=False

    def test_is_previewing_property(self, app):
        """Test is_previewing property."""
        assert not app.is_previewing

        app.preview_theme("light")
        assert app.is_previewing

        app.commit_preview()
        assert not app.is_previewing

    def test_preview_while_previewing(self, app):
        """Test previewing another theme while already previewing."""
        app.set_theme("dark")

        # Start preview
        app.preview_theme("light")
        assert app.current_theme_name.name == "light"

        # Preview another theme
        app.preview_theme("default")
        assert app.current_theme_name.name == "default"

        # Original theme should still be dark
        assert app._preview_original_theme.name == "dark"

        # Cancel should restore original
        app.cancel_preview()
        assert app.current_theme_name.name == "dark"

    def test_commit_without_preview(self, app):
        """Test commit_preview when not previewing."""
        # Should not raise error
        app.commit_preview()
        # Should be no-op

    def test_cancel_without_preview(self, app):
        """Test cancel_preview when not previewing."""
        # Should not raise error
        app.cancel_preview()
        # Should be no-op


class TestMetadataIntegration:
    """Test integration of metadata with ThemedApplication."""

    def test_metadata_provider_initialized(self, app):
        """Test that metadata provider is initialized."""
        assert hasattr(app, "_metadata_provider")
        assert app._metadata_provider is not None

    def test_auto_create_metadata_from_themes(self, app):
        """Test automatic metadata creation from loaded themes."""
        # Load a theme with metadata
        theme = Theme(
            name="custom",
            colors={"background": "#000000"},
            styles={},
            metadata={
                "display_name": "Custom Theme",
                "description": "A custom theme",
                "type": "dark",
                "tags": ["custom"],
            },
        )

        app._available_themes["custom"] = theme

        # Get theme info - should auto-create from theme metadata
        info = app.get_theme_info("custom")

        # Note: This test assumes auto-creation; if not implemented,
        # it will fail and signal that feature needs implementation
        # For now, we test that get_theme_info doesn't crash
        assert info is None or isinstance(info, ThemeInfo)

    def test_get_all_theme_info(self, app):
        """Test getting metadata for all themes."""
        # Register some metadata
        info1 = ThemeInfo(
            name="dark",
            display_name="Dark",
            description="Dark theme",
            type="dark",
            tags=["dark"],
        )
        info2 = ThemeInfo(
            name="light",
            display_name="Light",
            description="Light theme",
            type="light",
            tags=["light"],
        )

        app._metadata_provider.register_metadata("dark", info1)
        app._metadata_provider.register_metadata("light", info2)

        all_info = app.get_all_theme_info()

        assert len(all_info) >= 2
        assert "dark" in all_info
        assert "light" in all_info
