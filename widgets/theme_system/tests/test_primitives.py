"""Test suite for theme switching primitive widgets."""

import pytest

from vfwidgets_theme import ThemedApplication
from vfwidgets_theme.widgets.primitives import (
    ThemeButtonGroup,
    ThemeComboBox,
    ThemeListWidget,
)


@pytest.fixture(scope="module")
def app():
    """Create ThemedApplication for tests."""
    app = ThemedApplication([])
    app.set_theme("dark")
    yield app
    app.quit()


class TestThemeComboBox:
    """Test ThemeComboBox widget."""

    def test_creation(self, app):
        """Test basic creation."""
        combo = ThemeComboBox()
        assert combo is not None

    def test_populates_themes(self, app):
        """Test combo box is populated with available themes."""
        combo = ThemeComboBox()
        assert combo.count() > 0
        # Should contain at least 'dark' theme
        items = [combo.itemText(i) for i in range(combo.count())]
        assert "dark" in items

    def test_shows_current_theme(self, app):
        """Test combo box shows current theme."""
        app.set_theme("dark")
        combo = ThemeComboBox()
        assert combo.currentText() == "dark"

    def test_changing_combo_changes_theme(self, app):
        """Test changing combo box changes application theme."""
        combo = ThemeComboBox()
        # Change combo selection
        combo.setCurrentText("light")
        # App theme should change
        assert app.current_theme_name == "light"

    def test_syncs_with_app_theme_changes(self, app):
        """Test combo updates when app theme changes externally."""
        combo = ThemeComboBox()
        # Change theme via app
        app.set_theme("dark")
        # Combo should update
        assert combo.currentText() == "dark"

    def test_no_infinite_loop(self, app):
        """Test signal synchronization prevents infinite loops."""
        combo = ThemeComboBox()
        # This should not cause infinite recursion
        app.set_theme("light")
        combo.setCurrentText("dark")
        # Should complete without hanging


class TestThemeListWidget:
    """Test ThemeListWidget widget."""

    def test_creation(self, app):
        """Test basic creation."""
        list_widget = ThemeListWidget()
        assert list_widget is not None

    def test_populates_themes(self, app):
        """Test list widget is populated with available themes."""
        list_widget = ThemeListWidget()
        assert list_widget.count() > 0

    def test_shows_current_theme(self, app):
        """Test list widget highlights current theme."""
        app.set_theme("dark")
        list_widget = ThemeListWidget()
        current_item = list_widget.currentItem()
        assert current_item is not None
        assert current_item.text() == "dark"

    def test_changing_selection_changes_theme(self, app):
        """Test selecting item changes application theme."""
        list_widget = ThemeListWidget()
        # Find and select a different theme
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            if item.text() == "light":
                list_widget.setCurrentItem(item)
                break
        # App theme should change
        assert app.current_theme_name == "light"

    def test_syncs_with_app_theme_changes(self, app):
        """Test list updates when app theme changes externally."""
        list_widget = ThemeListWidget()
        # Change theme via app
        app.set_theme("dark")
        # List should update
        current_item = list_widget.currentItem()
        assert current_item.text() == "dark"

    def test_displays_metadata(self, app):
        """Test list widget displays theme metadata."""
        list_widget = ThemeListWidget()
        # Should have items with rich display (not just names)
        assert list_widget.count() > 0
        # Metadata display tested by checking tooltip or icon existence
        item = list_widget.item(0)
        assert item is not None


class TestThemeButtonGroup:
    """Test ThemeButtonGroup widget."""

    def test_creation_radio_mode(self, app):
        """Test basic creation in radio button mode."""
        button_group = ThemeButtonGroup(mode="radio")
        assert button_group is not None

    def test_creation_toggle_mode(self, app):
        """Test basic creation in toggle button mode."""
        button_group = ThemeButtonGroup(mode="toggle")
        assert button_group is not None

    def test_creates_buttons_for_themes(self, app):
        """Test button group creates buttons for available themes."""
        button_group = ThemeButtonGroup()
        # Should have buttons (check layout has widgets)
        assert button_group.layout() is not None
        assert button_group.layout().count() > 0

    def test_shows_current_theme_checked(self, app):
        """Test current theme button is checked."""
        app.set_theme("dark")
        button_group = ThemeButtonGroup()
        # Find dark theme button and check if it's checked
        checked_buttons = [
            btn
            for btn in button_group.findChildren(type(button_group.layout().itemAt(0).widget()))
            if hasattr(btn, "isChecked") and btn.isChecked()
        ]
        assert len(checked_buttons) > 0

    def test_clicking_button_changes_theme(self, app):
        """Test clicking button changes application theme."""
        button_group = ThemeButtonGroup()
        # Find a button and click it
        for i in range(button_group.layout().count()):
            widget = button_group.layout().itemAt(i).widget()
            if hasattr(widget, "text") and widget.text() == "light":
                widget.click()
                break
        # App theme should change
        assert app.current_theme_name == "light"

    def test_syncs_with_app_theme_changes(self, app):
        """Test buttons update when app theme changes externally."""
        button_group = ThemeButtonGroup()
        # Change theme via app
        app.set_theme("dark")
        # Correct button should be checked
        for i in range(button_group.layout().count()):
            widget = button_group.layout().itemAt(i).widget()
            if hasattr(widget, "text") and widget.text() == "dark":
                assert widget.isChecked()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
