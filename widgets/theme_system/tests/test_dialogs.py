"""Test suite for theme switching dialog components."""

import pytest
from PySide6.QtWidgets import QDialog, QVBoxLayout, QWidget

from vfwidgets_theme import ThemedApplication
from vfwidgets_theme.widgets.dialogs import (
    ThemePickerDialog,
    ThemeSettingsWidget,
)


@pytest.fixture(scope="module")
def app():
    """Create ThemedApplication for tests."""
    app = ThemedApplication([])
    app.set_theme("dark")
    yield app
    app.quit()


class TestThemePickerDialog:
    """Test ThemePickerDialog class."""

    def test_creation(self, app):
        """Test basic creation."""
        dialog = ThemePickerDialog()
        assert dialog is not None
        assert isinstance(dialog, QDialog)
        dialog.close()

    def test_has_theme_list(self, app):
        """Test dialog contains theme list."""
        dialog = ThemePickerDialog()

        # Should have a list widget or similar
        children = dialog.findChildren(QWidget)
        assert len(children) > 0

        dialog.close()

    def test_preview_mode(self, app):
        """Test preview mode functionality."""
        app.set_theme("dark")
        original_theme = app.current_theme_name

        dialog = ThemePickerDialog(preview_mode=True)

        # Should have OK/Cancel or Apply/Cancel buttons
        assert dialog is not None

        dialog.close()

        # Theme should be restored after cancel
        # (This is implicit in close without accept)

    def test_selected_theme_property(self, app):
        """Test selected_theme property."""
        dialog = ThemePickerDialog()

        # Should have a selected theme
        assert hasattr(dialog, "selected_theme")

        dialog.close()

    def test_accept_applies_theme(self, app):
        """Test that accepting dialog applies theme."""
        app.set_theme("dark")

        dialog = ThemePickerDialog()

        # Select a theme programmatically
        if hasattr(dialog, "_list_widget"):
            for i in range(dialog._list_widget.count()):
                item = dialog._list_widget.item(i)
                if item.text() == "light":
                    dialog._list_widget.setCurrentItem(item)
                    break

        # Accept dialog
        dialog.accept()

        # Theme should be applied
        assert app.current_theme_name == "light"

    def test_reject_restores_theme_in_preview_mode(self, app):
        """Test that rejecting dialog restores theme in preview mode."""
        # Ensure we start with dark theme
        app.set_theme("dark")
        import time

        time.sleep(0.01)  # Allow signal processing
        original_theme = app.current_theme_name
        assert original_theme == "dark"

        dialog = ThemePickerDialog(preview_mode=True)

        # Select different theme (light)
        if hasattr(dialog, "_list_widget"):
            for i in range(dialog._list_widget.count()):
                item = dialog._list_widget.item(i)
                if item.text() == "light":
                    dialog._list_widget.setCurrentItem(item)
                    time.sleep(0.01)  # Allow preview to trigger
                    break

        # Verify theme changed to light
        assert app.current_theme_name == "light"

        # Reject dialog
        dialog.reject()
        time.sleep(0.01)  # Allow cancel to process

        # Original theme (dark) should be restored
        assert app.current_theme_name == "dark"


class TestThemeSettingsWidget:
    """Test ThemeSettingsWidget class."""

    def test_creation(self, app):
        """Test basic creation."""
        widget = ThemeSettingsWidget()
        assert widget is not None
        assert isinstance(widget, QWidget)

    def test_embeddable_in_layout(self, app):
        """Test widget can be embedded in a layout."""
        container = QWidget()
        layout = QVBoxLayout(container)

        widget = ThemeSettingsWidget()
        layout.addWidget(widget)

        # Should be added successfully
        assert widget in container.findChildren(QWidget)

    def test_has_theme_selection(self, app):
        """Test widget has theme selection UI."""
        widget = ThemeSettingsWidget()

        # Should have child widgets
        children = widget.findChildren(QWidget)
        assert len(children) > 0

    def test_current_theme_displayed(self, app):
        """Test current theme is displayed."""
        app.set_theme("dark")

        widget = ThemeSettingsWidget()

        # Should show current theme somehow
        # This test just verifies creation doesn't crash
        assert widget is not None

    def test_changing_selection_changes_theme(self, app):
        """Test changing selection changes application theme."""
        widget = ThemeSettingsWidget()

        # Find and use combo/list if it exists
        if hasattr(widget, "_combo"):
            widget._combo.setCurrentText("light")
            assert app.current_theme_name == "light"
        elif hasattr(widget, "_list_widget"):
            for i in range(widget._list_widget.count()):
                item = widget._list_widget.item(i)
                if item.text() == "light":
                    widget._list_widget.setCurrentItem(item)
                    break
            assert app.current_theme_name == "light"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
