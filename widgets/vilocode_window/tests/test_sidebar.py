"""Tests for SideBar component."""

import pytest
from PySide6.QtWidgets import QLabel

from vfwidgets_vilocode_window.components.sidebar import SideBar


@pytest.fixture
def app(qapp):
    """Provide QApplication instance."""
    return qapp


def test_sidebar_creation(app):
    """Test SideBar can be created."""
    sidebar = SideBar()
    assert sidebar is not None
    assert sidebar.width() == 250  # Default width


def test_add_panel(app):
    """Test adding panels to sidebar."""
    sidebar = SideBar()
    panel = QLabel("Test Panel")

    sidebar.add_panel("test_panel", panel, "Test Panel Title")
    assert "test_panel" in sidebar._panels
    assert sidebar._panels["test_panel"][0] == panel
    assert sidebar._panels["test_panel"][1] == "Test Panel Title"


def test_remove_panel(app):
    """Test removing panels from sidebar."""
    sidebar = SideBar()
    panel = QLabel("Test Panel")

    sidebar.add_panel("test_panel", panel, "Test Panel Title")
    assert "test_panel" in sidebar._panels

    sidebar.remove_panel("test_panel")
    assert "test_panel" not in sidebar._panels


def test_show_panel(app, qtbot):
    """Test switching panels."""
    sidebar = SideBar()
    panel1 = QLabel("Panel 1")
    panel2 = QLabel("Panel 2")

    sidebar.add_panel("panel1", panel1, "Panel 1")
    sidebar.add_panel("panel2", panel2, "Panel 2")

    with qtbot.waitSignal(sidebar.panel_changed, timeout=1000) as blocker:
        sidebar.show_panel("panel2")

    assert blocker.args == ["panel2"]
    assert sidebar.get_current_panel() == "panel2"


def test_get_panel(app):
    """Test getting panel widget by ID."""
    sidebar = SideBar()
    panel = QLabel("Test Panel")

    sidebar.add_panel("test_panel", panel, "Test Panel Title")

    retrieved_panel = sidebar.get_panel("test_panel")
    assert retrieved_panel == panel

    nonexistent_panel = sidebar.get_panel("nonexistent")
    assert nonexistent_panel is None


def test_get_current_panel(app):
    """Test getting current panel ID."""
    sidebar = SideBar()
    panel1 = QLabel("Panel 1")
    panel2 = QLabel("Panel 2")

    sidebar.add_panel("panel1", panel1, "Panel 1")
    sidebar.add_panel("panel2", panel2, "Panel 2")

    # First panel should be shown by default
    assert sidebar.get_current_panel() == "panel1"

    sidebar.show_panel("panel2")
    assert sidebar.get_current_panel() == "panel2"


def test_toggle_visibility(app, qtbot):
    """Test toggling sidebar visibility."""
    sidebar = SideBar()
    sidebar.show()  # Make it visible first

    # Should be visible after show()
    assert sidebar.isVisible() is True

    with qtbot.waitSignal(sidebar.visibility_changed, timeout=1000) as blocker:
        sidebar.set_visible(False, animated=False)

    assert blocker.args == [False]
    assert sidebar.isVisible() is False

    with qtbot.waitSignal(sidebar.visibility_changed, timeout=1000) as blocker:
        sidebar.set_visible(True, animated=False)

    assert blocker.args == [True]
    assert sidebar.isVisible() is True


def test_set_visible(app, qtbot):
    """Test setting sidebar visibility."""
    sidebar = SideBar()

    with qtbot.waitSignal(sidebar.visibility_changed, timeout=1000) as blocker:
        sidebar.set_visible(False, animated=False)

    assert blocker.args == [False]
    assert sidebar.isVisible() is False

    with qtbot.waitSignal(sidebar.visibility_changed, timeout=1000) as blocker:
        sidebar.set_visible(True, animated=False)

    assert blocker.args == [True]
    assert sidebar.isVisible() is True


def test_set_width(app, qtbot):
    """Test setting sidebar width."""
    sidebar = SideBar()

    with qtbot.waitSignal(sidebar.width_changed, timeout=1000) as blocker:
        sidebar.set_width(300)

    assert blocker.args == [300]
    assert sidebar.get_width() == 300


def test_width_constraints(app):
    """Test sidebar width constraints."""
    sidebar = SideBar()

    # Test minimum width
    sidebar.set_width(50)  # Below minimum (150)
    assert sidebar.get_width() == 150

    # Test maximum width
    sidebar.set_width(1000)  # Above maximum (500)
    assert sidebar.get_width() == 500

    # Test normal width
    sidebar.set_width(300)
    assert sidebar.get_width() == 300


def test_panel_memory_on_visibility_toggle(app):
    """Test that current panel is preserved when toggling visibility."""
    sidebar = SideBar()
    panel1 = QLabel("Panel 1")
    panel2 = QLabel("Panel 2")

    sidebar.add_panel("panel1", panel1, "Panel 1")
    sidebar.add_panel("panel2", panel2, "Panel 2")

    sidebar.show_panel("panel2")
    assert sidebar.get_current_panel() == "panel2"

    # Hide sidebar
    sidebar.set_visible(False, animated=False)
    assert sidebar.get_current_panel() == "panel2"  # Panel ID preserved

    # Show sidebar again
    sidebar.set_visible(True, animated=False)
    assert sidebar.get_current_panel() == "panel2"  # Still panel2


def test_remove_current_panel(app):
    """Test removing the currently visible panel."""
    sidebar = SideBar()
    panel1 = QLabel("Panel 1")
    panel2 = QLabel("Panel 2")

    sidebar.add_panel("panel1", panel1, "Panel 1")
    sidebar.add_panel("panel2", panel2, "Panel 2")

    sidebar.show_panel("panel2")
    assert sidebar.get_current_panel() == "panel2"

    # Remove current panel
    sidebar.remove_panel("panel2")

    # Should fall back to first available panel
    assert sidebar.get_current_panel() == "panel1"


def test_update_existing_panel(app):
    """Test updating an existing panel."""
    sidebar = SideBar()
    panel1 = QLabel("Panel 1")
    panel2 = QLabel("Panel 2 Updated")

    sidebar.add_panel("test_panel", panel1, "Title 1")
    assert sidebar.get_panel("test_panel") == panel1

    # Update with new widget
    sidebar.add_panel("test_panel", panel2, "Title 2")
    assert sidebar.get_panel("test_panel") == panel2
    assert sidebar._panels["test_panel"][1] == "Title 2"
