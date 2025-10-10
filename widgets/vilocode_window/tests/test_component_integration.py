"""Integration tests for component interactions."""

import pytest
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel

from vfwidgets_vilocode_window import ViloCodeWindow


@pytest.fixture
def app(qapp):
    """Provide QApplication instance."""
    return qapp


def test_activity_bar_to_sidebar_integration(app, qtbot):
    """Test ActivityBar item click switches SideBar panel."""
    window = ViloCodeWindow()

    # Add sidebar panels
    panel1 = QLabel("Panel 1")
    panel2 = QLabel("Panel 2")
    window.add_sidebar_panel("panel1", panel1, "Panel 1")
    window.add_sidebar_panel("panel2", panel2, "Panel 2")

    # Add activity items
    icon = QIcon()
    window.add_activity_item("panel1", icon, "Panel 1")
    window.add_activity_item("panel2", icon, "Panel 2")

    # Connect activity bar to sidebar
    def on_activity_clicked(item_id: str):
        window.show_sidebar_panel(item_id)

    window.activity_item_clicked.connect(on_activity_clicked)

    # Simulate activity item click
    with qtbot.waitSignal(window.sidebar_panel_changed, timeout=1000) as blocker:
        window._activity_bar._items["panel2"].clicked.emit()

    assert blocker.args == ["panel2"]
    assert window._sidebar.get_current_panel() == "panel2"


def test_sidebar_to_activity_bar_integration(app, qtbot):
    """Test SideBar panel change updates ActivityBar active item."""
    window = ViloCodeWindow()

    # Add sidebar panels
    panel1 = QLabel("Panel 1")
    panel2 = QLabel("Panel 2")
    window.add_sidebar_panel("panel1", panel1, "Panel 1")
    window.add_sidebar_panel("panel2", panel2, "Panel 2")

    # Add activity items
    icon = QIcon()
    window.add_activity_item("panel1", icon, "Panel 1")
    window.add_activity_item("panel2", icon, "Panel 2")

    # Connect sidebar to activity bar
    def on_panel_changed(panel_id: str):
        window.set_active_activity_item(panel_id)

    window.sidebar_panel_changed.connect(on_panel_changed)

    # Change panel
    window.show_sidebar_panel("panel2")

    assert window.get_active_activity_item() == "panel2"
    assert window._activity_bar._items["panel2"]._is_active is True
    assert window._activity_bar._items["panel1"]._is_active is False


def test_bidirectional_activity_sidebar_integration(app, qtbot):
    """Test bidirectional ActivityBar ↔ SideBar integration."""
    window = ViloCodeWindow()

    # Setup panels and items
    panel1 = QLabel("Panel 1")
    panel2 = QLabel("Panel 2")
    window.add_sidebar_panel("panel1", panel1, "Panel 1")
    window.add_sidebar_panel("panel2", panel2, "Panel 2")

    icon = QIcon()
    window.add_activity_item("panel1", icon, "Panel 1")
    window.add_activity_item("panel2", icon, "Panel 2")

    # Setup bidirectional connection
    def on_activity_clicked(item_id: str):
        window.show_sidebar_panel(item_id)

    def on_panel_changed(panel_id: str):
        window.set_active_activity_item(panel_id)

    window.activity_item_clicked.connect(on_activity_clicked)
    window.sidebar_panel_changed.connect(on_panel_changed)

    # Test activity bar → sidebar
    window._activity_bar._items["panel2"].clicked.emit()
    assert window._sidebar.get_current_panel() == "panel2"
    assert window.get_active_activity_item() == "panel2"

    # Test sidebar → activity bar (via API)
    window.show_sidebar_panel("panel1")
    assert window._sidebar.get_current_panel() == "panel1"
    assert window.get_active_activity_item() == "panel1"


def test_all_components_together(app):
    """Test all components working together."""
    window = ViloCodeWindow()

    # Add main content
    main_content = QLabel("Main Content")
    window.set_main_content(main_content)
    assert window.get_main_content() == main_content

    # Add sidebar panels
    panel1 = QLabel("Panel 1")
    panel2 = QLabel("Panel 2")
    window.add_sidebar_panel("panel1", panel1, "Panel 1")
    window.add_sidebar_panel("panel2", panel2, "Panel 2")

    # Add activity items
    icon = QIcon()
    window.add_activity_item("panel1", icon, "Panel 1")
    window.add_activity_item("panel2", icon, "Panel 2")

    # Add auxiliary content
    aux_content = QLabel("Auxiliary Content")
    window.set_auxiliary_content(aux_content)
    assert window.get_auxiliary_content() == aux_content

    # Test sidebar visibility toggle
    window.set_sidebar_visible(False)
    window.set_sidebar_visible(True)
    # Just verify the method works (visibility state depends on parent/layout)

    # Test auxiliary bar visibility toggle
    window.set_auxiliary_bar_visible(False)
    window.set_auxiliary_bar_visible(True)
    # Just verify the method works

    # All components should be working
    assert window._activity_bar is not None
    assert window._sidebar is not None
    assert window._auxiliary_bar is not None


def test_sidebar_visibility_preserves_panel(app):
    """Test sidebar visibility toggle preserves current panel."""
    window = ViloCodeWindow()

    # Add panels
    panel1 = QLabel("Panel 1")
    panel2 = QLabel("Panel 2")
    window.add_sidebar_panel("panel1", panel1, "Panel 1")
    window.add_sidebar_panel("panel2", panel2, "Panel 2")

    # Show panel 2
    window.show_sidebar_panel("panel2")
    assert window._sidebar.get_current_panel() == "panel2"

    # Hide sidebar
    window.set_sidebar_visible(False)
    assert window._sidebar.get_current_panel() == "panel2"  # Still panel2

    # Show sidebar
    window.set_sidebar_visible(True)
    assert window._sidebar.get_current_panel() == "panel2"  # Still panel2


def test_activity_item_without_corresponding_panel(app):
    """Test activity item without corresponding sidebar panel."""
    window = ViloCodeWindow()

    # Add activity item without panel
    icon = QIcon()
    window.add_activity_item("orphan", icon, "Orphan Item")

    # Should not crash when clicked
    window._activity_bar._items["orphan"].clicked.emit()

    # Activity item should still be active
    window.set_active_activity_item("orphan")
    assert window.get_active_activity_item() == "orphan"


def test_sidebar_panel_without_activity_item(app):
    """Test sidebar panel without corresponding activity item."""
    window = ViloCodeWindow()

    # Add panel without activity item
    panel = QLabel("Orphan Panel")
    window.add_sidebar_panel("orphan", panel, "Orphan Panel")

    # Should be able to show panel
    window.show_sidebar_panel("orphan")
    assert window._sidebar.get_current_panel() == "orphan"


def test_multiple_components_signals(app, qtbot):
    """Test signals from multiple components."""
    window = ViloCodeWindow()

    # Setup
    panel = QLabel("Panel")
    window.add_sidebar_panel("panel", panel, "Panel")

    icon = QIcon()
    window.add_activity_item("panel", icon, "Panel")

    aux_content = QLabel("Aux")
    window.set_auxiliary_content(aux_content)

    # Test multiple signals
    signal_counts = {"activity": 0, "sidebar": 0, "auxiliary": 0}

    def count_activity(item_id: str):
        signal_counts["activity"] += 1

    def count_sidebar(panel_id: str):
        signal_counts["sidebar"] += 1

    def count_auxiliary(visible: bool):
        signal_counts["auxiliary"] += 1

    window.activity_item_clicked.connect(count_activity)
    window.sidebar_panel_changed.connect(count_sidebar)
    window.auxiliary_bar_visibility_changed.connect(count_auxiliary)

    # Trigger signals
    window._activity_bar._items["panel"].clicked.emit()
    window.show_sidebar_panel("panel")
    # Use non-animated toggle to avoid animation timing issues in tests
    window.set_auxiliary_bar_visible(True, animated=False)

    assert signal_counts["activity"] == 1
    assert signal_counts["sidebar"] >= 1  # May fire multiple times during setup
    assert signal_counts["auxiliary"] == 1
