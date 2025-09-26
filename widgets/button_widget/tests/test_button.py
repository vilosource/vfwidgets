"""Tests for ButtonWidget."""

import pytest
from PySide6.QtWidgets import QApplication
from vfwidgets_button import ButtonWidget


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()


@pytest.fixture
def widget(qapp, qtbot):
    """Create widget instance for testing."""
    widget = ButtonWidget()
    qtbot.addWidget(widget)
    return widget


def test_widget_creation(widget):
    """Test widget can be created."""
    assert widget is not None
    assert isinstance(widget, ButtonWidget)


def test_widget_signals(widget, qtbot):
    """Test widget signals."""
    with qtbot.waitSignal(widget.value_changed, timeout=100):
        widget.set_value("test")


def test_widget_value(widget):
    """Test widget value get/set."""
    test_value = "test_value"
    widget.set_value(test_value)
    # Implement actual value checking based on widget logic
    # assert widget.get_value() == test_value
