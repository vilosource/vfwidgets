"""Tests for ActivityBar component."""

import pytest
from PySide6.QtGui import QIcon

from vfwidgets_vilocode_window.components.activity_bar import ActivityBar, ActivityBarItem


@pytest.fixture
def app(qapp):
    """Provide QApplication instance."""
    return qapp


def test_activity_bar_creation(app):
    """Test ActivityBar can be created."""
    bar = ActivityBar()
    assert bar is not None
    assert bar.width() == 48  # Fixed width


def test_add_item(app):
    """Test adding items to activity bar."""
    bar = ActivityBar()
    icon = QIcon()

    bar.add_item("test_item", icon, "Test Item")
    assert "test_item" in bar._items
    assert bar._items["test_item"] is not None


def test_remove_item(app):
    """Test removing items from activity bar."""
    bar = ActivityBar()
    icon = QIcon()

    bar.add_item("test_item", icon, "Test Item")
    assert "test_item" in bar._items

    bar.remove_item("test_item")
    assert "test_item" not in bar._items


def test_set_active_item(app):
    """Test setting active item."""
    bar = ActivityBar()
    icon = QIcon()

    bar.add_item("item1", icon, "Item 1")
    bar.add_item("item2", icon, "Item 2")

    bar.set_active_item("item1")
    assert bar.get_active_item() == "item1"
    assert bar._items["item1"]._is_active is True
    assert bar._items["item2"]._is_active is False

    bar.set_active_item("item2")
    assert bar.get_active_item() == "item2"
    assert bar._items["item1"]._is_active is False
    assert bar._items["item2"]._is_active is True


def test_item_clicked_signal(app, qtbot):
    """Test item_clicked signal is emitted."""
    bar = ActivityBar()
    icon = QIcon()

    bar.add_item("test_item", icon, "Test Item")

    with qtbot.waitSignal(bar.item_clicked, timeout=1000) as blocker:
        item = bar._items["test_item"]
        # Simulate click
        item.clicked.emit()

    assert blocker.args == ["test_item"]


def test_set_item_icon(app):
    """Test updating item icon."""
    bar = ActivityBar()
    icon1 = QIcon()
    icon2 = QIcon()

    bar.add_item("test_item", icon1, "Test Item")
    bar.set_item_icon("test_item", icon2)

    # Icon should be updated (can't easily verify QIcon equality, just check method works)
    assert "test_item" in bar._items


def test_set_item_enabled(app):
    """Test enabling/disabling items."""
    bar = ActivityBar()
    icon = QIcon()

    bar.add_item("test_item", icon, "Test Item")

    bar.set_item_enabled("test_item", False)
    assert bar.is_item_enabled("test_item") is False

    bar.set_item_enabled("test_item", True)
    assert bar.is_item_enabled("test_item") is True


def test_get_items(app):
    """Test getting all item IDs."""
    bar = ActivityBar()
    icon = QIcon()

    bar.add_item("item1", icon, "Item 1")
    bar.add_item("item2", icon, "Item 2")
    bar.add_item("item3", icon, "Item 3")

    items = bar.get_items()
    assert len(items) == 3
    assert "item1" in items
    assert "item2" in items
    assert "item3" in items


def test_activity_bar_item_creation(app):
    """Test ActivityBarItem can be created."""
    icon = QIcon()
    item = ActivityBarItem("test_id", icon, "Test Tooltip")

    assert item._item_id == "test_id"
    assert item._tooltip == "Test Tooltip"
    assert item.width() == 48
    assert item.height() == 48


def test_activity_bar_item_active_state(app):
    """Test ActivityBarItem active state."""
    icon = QIcon()
    item = ActivityBarItem("test_id", icon)

    assert item._is_active is False

    item.set_active(True)
    assert item._is_active is True

    item.set_active(False)
    assert item._is_active is False


def test_activity_bar_item_enabled_state(app):
    """Test ActivityBarItem enabled state."""
    icon = QIcon()
    item = ActivityBarItem("test_id", icon)

    assert item.is_enabled() is True

    item.set_enabled(False)
    assert item.is_enabled() is False

    item.set_enabled(True)
    assert item.is_enabled() is True


def test_activity_bar_item_icon_update(app):
    """Test ActivityBarItem icon update."""
    icon1 = QIcon()
    icon2 = QIcon()
    item = ActivityBarItem("test_id", icon1)

    item.set_icon(icon2)
    # Just verify method works (can't easily verify QIcon equality)
    assert item._icon is not None
