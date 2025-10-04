"""Test suite for themed MultisplitWidget integration."""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel
from vfwidgets_multisplit import MultisplitWidget
from vfwidgets_multisplit.view.container import StyledSplitter
from vfwidgets_multisplit.view.error_widget import ErrorWidget, ValidationOverlay
from vfwidgets_theme import ThemedApplication


@pytest.fixture(scope="module")
def app():
    """Create ThemedApplication for tests."""
    app = ThemedApplication([])
    app.set_theme("dark")
    yield app
    app.quit()


def test_styled_splitter_creation(app):
    """Test StyledSplitter with theme integration."""
    splitter = StyledSplitter(Qt.Orientation.Horizontal)
    assert splitter.theme is not None
    assert hasattr(splitter, 'on_theme_changed')


def test_styled_splitter_theme_access(app):
    """Test theme token access in splitter."""
    splitter = StyledSplitter(Qt.Orientation.Vertical)
    # Should have access to configured theme tokens
    assert splitter.theme.handle_bg is not None
    assert splitter.theme.handle_hover_bg is not None
    assert splitter.theme.handle_border is not None


def test_error_widget_creation(app):
    """Test ErrorWidget with theme integration."""
    error = ErrorWidget("Test error")
    assert error.theme is not None
    assert hasattr(error, 'on_theme_changed')


def test_error_widget_theme_access(app):
    """Test theme token access in error widget."""
    error = ErrorWidget("Test error")
    assert error.theme.error_fg is not None
    assert error.theme.error_bg is not None
    assert error.theme.error_border is not None


def test_error_widget_update_message(app):
    """Test updating error message."""
    error = ErrorWidget("Initial error")
    error.set_error("Updated error")
    assert error._message_label.text() == "Updated error"


def test_validation_overlay_creation(app):
    """Test ValidationOverlay with theme integration."""
    overlay = ValidationOverlay()
    assert overlay.theme is not None
    assert hasattr(overlay, 'on_theme_changed')


def test_validation_overlay_show_error(app):
    """Test showing validation error."""
    overlay = ValidationOverlay()
    overlay.show_validation_error("Validation failed", duration=100)
    assert len(overlay.messages) == 1


def test_multisplit_widget_basic(app):
    """Test basic MultisplitWidget creation (components should be themed)."""
    # Create simple widget provider
    class SimpleProvider:
        def provide_widget(self, widget_id, pane_id):
            return QLabel(f"Pane {pane_id}")

    widget = MultisplitWidget(provider=SimpleProvider())
    assert widget is not None
    # The container should use StyledSplitter (which is themed)
    assert widget._container is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
