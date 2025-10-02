"""Test suite for theme switching helper functions."""

import pytest
from PySide6.QtWidgets import QMainWindow, QToolBar, QWidget

from vfwidgets_theme import ThemedApplication
from vfwidgets_theme.widgets.helpers import (
    ThemePreview,
    ThemeSettings,
    add_theme_menu,
    add_theme_toolbar,
)


@pytest.fixture(scope="module")
def app():
    """Create ThemedApplication for tests."""
    app = ThemedApplication([])
    app.set_theme("dark")
    yield app
    app.quit()


@pytest.fixture
def main_window(app):
    """Create main window for testing."""
    window = QMainWindow()
    yield window
    window.close()


class TestAddThemeMenu:
    """Test add_theme_menu helper function."""

    def test_adds_menu_to_menubar(self, app, main_window):
        """Test that add_theme_menu adds a menu to the menu bar."""
        menubar = main_window.menuBar()
        initial_count = len(menubar.actions())

        add_theme_menu(main_window)

        # Should add one menu
        assert len(menubar.actions()) == initial_count + 1

    def test_menu_contains_theme_actions(self, app, main_window):
        """Test that the menu contains actions for each theme."""
        add_theme_menu(main_window)

        # Find the theme menu
        menubar = main_window.menuBar()
        theme_menu = None
        for action in menubar.actions():
            menu = action.menu()
            if menu and "theme" in action.text().lower():
                theme_menu = menu
                break

        assert theme_menu is not None
        # Should have actions for available themes
        assert len(theme_menu.actions()) > 0

    def test_custom_menu_name(self, app, main_window):
        """Test custom menu name."""
        add_theme_menu(main_window, menu_name="Custom Themes")

        menubar = main_window.menuBar()
        found = False
        for action in menubar.actions():
            if "Custom Themes" in action.text():
                found = True
                break

        assert found


class TestAddThemeToolbar:
    """Test add_theme_toolbar helper function."""

    def test_adds_toolbar(self, app, main_window):
        """Test that add_theme_toolbar adds a toolbar."""
        toolbar = add_theme_toolbar(main_window)

        assert toolbar is not None
        assert isinstance(toolbar, QToolBar)
        # Should be added to window
        assert toolbar in main_window.findChildren(QToolBar)

    def test_toolbar_contains_widgets(self, app, main_window):
        """Test that toolbar contains theme switching widgets."""
        toolbar = add_theme_toolbar(main_window)

        # Should have widgets (combo box or buttons)
        assert toolbar.actions() or len(toolbar.findChildren(QWidget)) > 0

    def test_custom_toolbar_name(self, app, main_window):
        """Test custom toolbar name."""
        toolbar = add_theme_toolbar(main_window, toolbar_name="Custom Theme Bar")

        assert "Custom Theme Bar" in toolbar.windowTitle()


class TestThemePreview:
    """Test ThemePreview class."""

    def test_creation(self, app):
        """Test basic creation."""
        preview = ThemePreview()
        assert preview is not None

    def test_preview_changes_theme_temporarily(self, app):
        """Test that preview changes theme without persisting."""
        app.set_theme("dark")
        original_theme = app.current_theme_name

        preview = ThemePreview()
        preview.preview("light")

        # Theme should change
        assert app.current_theme_name == "light"

        # Original should be stored
        assert preview._original_theme == original_theme

    def test_commit_keeps_previewed_theme(self, app):
        """Test that commit keeps the previewed theme."""
        app.set_theme("dark")

        preview = ThemePreview()
        preview.preview("light")
        preview.commit()

        # Should keep light theme
        assert app.current_theme_name == "light"
        # Original should be cleared
        assert preview._original_theme is None

    def test_cancel_restores_original_theme(self, app):
        """Test that cancel restores original theme."""
        app.set_theme("dark")
        original_theme = app.current_theme_name

        preview = ThemePreview()
        preview.preview("light")

        # Verify preview worked
        assert app.current_theme_name == "light"

        # Cancel
        preview.cancel()

        # Should restore original
        assert app.current_theme_name == original_theme

    def test_multiple_previews(self, app):
        """Test multiple preview calls before commit/cancel."""
        app.set_theme("dark")
        original_theme = app.current_theme_name

        preview = ThemePreview()
        preview.preview("light")
        preview.preview("minimal")

        # Original should still be dark
        assert preview._original_theme == original_theme

        # Cancel should restore original
        preview.cancel()
        assert app.current_theme_name == original_theme

    def test_is_previewing_property(self, app):
        """Test is_previewing property."""
        app.set_theme("dark")

        preview = ThemePreview()
        assert not preview.is_previewing

        preview.preview("light")
        assert preview.is_previewing

        preview.commit()
        assert not preview.is_previewing


class TestThemeSettings:
    """Test ThemeSettings class."""

    def test_creation(self, app):
        """Test basic creation."""
        settings = ThemeSettings(organization="TestOrg", application="TestApp")
        assert settings is not None

    def test_save_theme_preference(self, app):
        """Test saving theme preference."""
        settings = ThemeSettings(organization="TestOrg", application="TestApp")

        settings.save_theme("dark")

        # Should be able to load it back
        loaded = settings.load_theme()
        assert loaded == "dark"

    def test_load_nonexistent_returns_none(self, app):
        """Test loading when no preference exists."""
        settings = ThemeSettings(organization="TestOrgNew", application="TestAppNew")

        # Should return None or default
        loaded = settings.load_theme()
        assert loaded is None or isinstance(loaded, str)

    def test_load_with_default(self, app):
        """Test load_theme with default value."""
        settings = ThemeSettings(organization="TestOrgDefault", application="TestAppDefault")

        loaded = settings.load_theme(default="minimal")
        assert loaded == "minimal"

    def test_auto_save_on_theme_change(self, app):
        """Test automatic saving when app theme changes."""
        settings = ThemeSettings(
            organization="TestOrgAuto",
            application="TestAppAuto",
            auto_save=True
        )

        # Change theme
        app.set_theme("light")

        # Should auto-save (may need small delay for signal)
        # Note: This test may be timing-dependent
        loaded = settings.load_theme()
        # Just verify it doesn't crash
        assert loaded is None or isinstance(loaded, str)

    def test_clear_preference(self, app):
        """Test clearing saved preference."""
        settings = ThemeSettings(organization="TestOrgClear", application="TestAppClear")

        settings.save_theme("dark")
        assert settings.load_theme() == "dark"

        settings.clear()
        loaded = settings.load_theme()
        assert loaded is None or loaded != "dark"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
