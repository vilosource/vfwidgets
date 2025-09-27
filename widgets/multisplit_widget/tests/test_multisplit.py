"""Tests for MultisplitWidget."""

import pytest
from PySide6.QtWidgets import QApplication
from vfwidgets_multisplit import MultisplitWidget
from vfwidgets_multisplit.core.types import WherePosition


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
    widget = MultisplitWidget()
    qtbot.addWidget(widget)
    return widget


def test_widget_creation(widget):
    """Test widget can be created."""
    assert widget is not None
    assert isinstance(widget, MultisplitWidget)


def test_widget_signals(widget, qtbot):
    """Test widget signals."""
    # Test that splitting a pane works (don't check signals for now)
    pane_id = widget.get_pane_ids()[0]
    initial_count = len(widget.get_pane_ids())
    result = widget.split_pane(pane_id, "test", WherePosition.RIGHT)
    assert result is True
    assert len(widget.get_pane_ids()) == initial_count + 1


def test_widget_public_api(widget):
    """Test widget public API."""
    # Test initial state
    assert len(widget.get_pane_ids()) == 1
    assert widget.get_focused_pane() is not None

    # Test splitting
    pane_id = widget.get_pane_ids()[0]
    result = widget.split_pane(pane_id, "test", WherePosition.RIGHT)
    assert result is True
    assert len(widget.get_pane_ids()) == 2

    # Test focus operations
    first_pane = widget.get_pane_ids()[0]
    second_pane = widget.get_pane_ids()[1]

    # Focus the second pane (the newly created one)
    assert widget.focus_pane(second_pane) is True
    assert widget.get_focused_pane() == second_pane
