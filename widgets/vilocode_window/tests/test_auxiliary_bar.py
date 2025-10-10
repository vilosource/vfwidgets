"""Tests for AuxiliaryBar component."""

import pytest
from PySide6.QtWidgets import QLabel

from vfwidgets_vilocode_window.components.auxiliary_bar import AuxiliaryBar


@pytest.fixture
def app(qapp):
    """Provide QApplication instance."""
    return qapp


def test_auxiliary_bar_creation(app):
    """Test AuxiliaryBar can be created."""
    aux_bar = AuxiliaryBar()
    assert aux_bar is not None
    assert aux_bar.width() == 300  # Default width
    assert aux_bar.isVisible() is False  # Hidden by default


def test_set_content(app):
    """Test setting auxiliary bar content."""
    aux_bar = AuxiliaryBar()
    content = QLabel("Test Content")

    aux_bar.set_content(content)
    assert aux_bar.get_content() == content


def test_replace_content(app):
    """Test replacing auxiliary bar content."""
    aux_bar = AuxiliaryBar()
    content1 = QLabel("Content 1")
    content2 = QLabel("Content 2")

    aux_bar.set_content(content1)
    assert aux_bar.get_content() == content1

    aux_bar.set_content(content2)
    assert aux_bar.get_content() == content2


def test_toggle_visibility(app, qtbot):
    """Test toggling auxiliary bar visibility."""
    aux_bar = AuxiliaryBar()

    # Initially hidden
    assert aux_bar.isVisible() is False

    with qtbot.waitSignal(aux_bar.visibility_changed, timeout=1000) as blocker:
        aux_bar.set_visible(True, animated=False)

    assert blocker.args == [True]
    assert aux_bar.isVisible() is True

    with qtbot.waitSignal(aux_bar.visibility_changed, timeout=1000) as blocker:
        aux_bar.set_visible(False, animated=False)

    assert blocker.args == [False]
    assert aux_bar.isVisible() is False


def test_set_visible(app, qtbot):
    """Test setting auxiliary bar visibility."""
    aux_bar = AuxiliaryBar()

    with qtbot.waitSignal(aux_bar.visibility_changed, timeout=1000) as blocker:
        aux_bar.set_visible(True, animated=False)

    assert blocker.args == [True]
    assert aux_bar.isVisible() is True

    with qtbot.waitSignal(aux_bar.visibility_changed, timeout=1000) as blocker:
        aux_bar.set_visible(False, animated=False)

    assert blocker.args == [False]
    assert aux_bar.isVisible() is False


def test_set_width(app, qtbot):
    """Test setting auxiliary bar width."""
    aux_bar = AuxiliaryBar()

    with qtbot.waitSignal(aux_bar.width_changed, timeout=1000) as blocker:
        aux_bar.set_width(400)

    assert blocker.args == [400]
    assert aux_bar.get_width() == 400


def test_width_constraints(app):
    """Test auxiliary bar width constraints."""
    aux_bar = AuxiliaryBar()

    # Test minimum width
    aux_bar.set_width(50)  # Below minimum (150)
    assert aux_bar.get_width() == 150

    # Test maximum width
    aux_bar.set_width(1000)  # Above maximum (500)
    assert aux_bar.get_width() == 500

    # Test normal width
    aux_bar.set_width(350)
    assert aux_bar.get_width() == 350


def test_get_content_when_empty(app):
    """Test getting content when none is set."""
    aux_bar = AuxiliaryBar()
    assert aux_bar.get_content() is None


def test_visibility_signal_on_set_visible(app, qtbot):
    """Test visibility_changed signal is emitted on set_visible."""
    aux_bar = AuxiliaryBar()

    # Test showing
    with qtbot.waitSignal(aux_bar.visibility_changed, timeout=1000) as blocker:
        aux_bar.set_visible(True, animated=False)

    assert blocker.signal_triggered
    assert blocker.args == [True]

    # Test hiding
    with qtbot.waitSignal(aux_bar.visibility_changed, timeout=1000) as blocker:
        aux_bar.set_visible(False, animated=False)

    assert blocker.signal_triggered
    assert blocker.args == [False]
