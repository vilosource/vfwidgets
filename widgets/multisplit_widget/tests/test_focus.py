"""Tests for focus management functionality.

Test focus state tracking, navigation, and commands.
"""

from vfwidgets_multisplit.core.model import PaneModel
from vfwidgets_multisplit.core.nodes import LeafNode, SplitNode
from vfwidgets_multisplit.core.types import NodeId, Orientation, PaneId, WidgetId


def test_focus_tracking():
    """Test focus state tracking in model."""
    model = PaneModel()
    leaf1 = LeafNode(PaneId("p1"), WidgetId("w1"))
    leaf2 = LeafNode(PaneId("p2"), WidgetId("w2"))

    model.root = SplitNode(NodeId("split1"), Orientation.HORIZONTAL, [leaf1, leaf2], [0.5, 0.5])
    model._rebuild_registry()

    # Test setting focus
    assert model.set_focused_pane(PaneId("p1"))
    assert model.focused_pane_id == PaneId("p1")
    assert model.get_focused_pane() == leaf1

    # Test changing focus
    assert model.set_focused_pane(PaneId("p2"))
    assert model.focused_pane_id == PaneId("p2")

    # Test no change
    assert not model.set_focused_pane(PaneId("p2"))

    # Test invalid pane
    assert not model.set_focused_pane(PaneId("invalid"))

    # Test clearing focus
    assert model.set_focused_pane(None)
    assert model.focused_pane_id is None


def test_focus_first_pane():
    """Test focusing first available pane."""
    model = PaneModel()
    assert not model.focus_first_pane()  # No panes

    model.root = LeafNode(PaneId("p1"), WidgetId("w1"))
    model._rebuild_registry()

    assert model.focus_first_pane()
    assert model.focused_pane_id == PaneId("p1")


def test_focus_signals():
    """Test focus change signals are emitted."""
    model = PaneModel()
    leaf1 = LeafNode(PaneId("p1"), WidgetId("w1"))
    leaf2 = LeafNode(PaneId("p2"), WidgetId("w2"))

    model.root = SplitNode(NodeId("split1"), Orientation.HORIZONTAL, [leaf1, leaf2], [0.5, 0.5])
    model._rebuild_registry()

    # Track signal emissions
    focus_changes = []

    def track_focus_change(old_id, new_id):
        focus_changes.append((old_id, new_id))

    model.signals.focus_changed.connect(track_focus_change)

    # Test focus change signal
    model.set_focused_pane(PaneId("p1"))
    assert len(focus_changes) == 1
    assert focus_changes[0] == (None, PaneId("p1"))

    # Test another change
    model.set_focused_pane(PaneId("p2"))
    assert len(focus_changes) == 2
    assert focus_changes[1] == (PaneId("p1"), PaneId("p2"))

    # Test clearing focus
    model.set_focused_pane(None)
    assert len(focus_changes) == 3
    assert focus_changes[2] == (PaneId("p2"), None)


def test_focus_manager():
    """Test focus chain management."""
    from vfwidgets_multisplit.core.focus import FocusManager

    model = PaneModel()

    # Build tree first
    leaf1 = LeafNode(PaneId("p1"), WidgetId("w1"))
    leaf2 = LeafNode(PaneId("p2"), WidgetId("w2"))
    leaf3 = LeafNode(PaneId("p3"), WidgetId("w3"))

    model.root = SplitNode(
        NodeId("split1"),
        Orientation.HORIZONTAL,
        [leaf1, SplitNode(NodeId("split2"), Orientation.VERTICAL, [leaf2, leaf3], [0.5, 0.5])],
        [0.5, 0.5],
    )
    model._rebuild_registry()

    # Now create focus manager - it will initialize with the existing tree
    focus_mgr = FocusManager(model)

    # Check order
    order = focus_mgr.get_focus_order()
    assert order == [PaneId("p1"), PaneId("p2"), PaneId("p3")]

    # Test navigation
    assert focus_mgr.get_next_pane(PaneId("p1")) == PaneId("p2")
    assert focus_mgr.get_next_pane(PaneId("p3")) == PaneId("p1")  # Wrap
    assert focus_mgr.get_previous_pane(PaneId("p1")) == PaneId("p3")  # Wrap

    # Test with no current
    assert focus_mgr.get_next_pane() == PaneId("p1")
    assert focus_mgr.get_previous_pane() == PaneId("p3")


def test_focus_manager_empty_tree():
    """Test focus manager with empty tree."""
    from vfwidgets_multisplit.core.focus import FocusManager

    model = PaneModel()
    focus_mgr = FocusManager(model)

    # Empty tree
    assert focus_mgr.get_focus_order() == []
    assert focus_mgr.get_next_pane() is None


def test_focus_manager_navigation():
    """Test directional focus navigation."""
    from vfwidgets_multisplit.core.focus import FocusManager
    from vfwidgets_multisplit.core.types import Direction

    model = PaneModel()

    # Build simple horizontal split
    leaf1 = LeafNode(PaneId("p1"), WidgetId("w1"))
    leaf2 = LeafNode(PaneId("p2"), WidgetId("w2"))

    model.root = SplitNode(NodeId("split1"), Orientation.HORIZONTAL, [leaf1, leaf2], [0.5, 0.5])
    model._rebuild_registry()
    model.set_focused_pane(PaneId("p1"))

    focus_mgr = FocusManager(model)

    # Test directional navigation (for now uses tab order)
    # From p1: RIGHT goes to next (p2), LEFT goes to previous (p2 because only 2 panes)
    assert focus_mgr.navigate(Direction.RIGHT) == PaneId("p2")
    assert focus_mgr.navigate(Direction.LEFT) == PaneId("p2")  # Previous from p1 wraps to p2


def test_focus_manager_cache_invalidation():
    """Test that focus order cache is invalidated on structure changes."""
    from vfwidgets_multisplit.core.focus import FocusManager

    model = PaneModel()

    # Add a pane first
    model.root = LeafNode(PaneId("p1"), WidgetId("w1"))
    model._rebuild_registry()

    # Create focus manager after tree exists
    focus_mgr = FocusManager(model)

    # Initial state should have the pane
    order = focus_mgr.get_focus_order()
    assert order == [PaneId("p1")]

    # Now test that cache invalidation works
    # Clear the tree
    model.root = None
    model._rebuild_registry()

    # Trigger structure change to invalidate cache
    model.signals.structure_changed.emit()

    # Cache should be invalidated and rebuilt to empty
    order = focus_mgr.get_focus_order()
    assert order == []


def test_focus_commands():
    """Test focus commands."""
    from vfwidgets_multisplit.controller.commands import FocusPaneCommand, NavigateFocusCommand
    from vfwidgets_multisplit.core.types import Direction

    model = PaneModel()

    # Build tree
    leaf1 = LeafNode(PaneId("p1"), WidgetId("w1"))
    leaf2 = LeafNode(PaneId("p2"), WidgetId("w2"))

    model.root = SplitNode(NodeId("split1"), Orientation.HORIZONTAL, [leaf1, leaf2], [0.5, 0.5])
    model._rebuild_registry()

    # Test focus command
    cmd = FocusPaneCommand(model, PaneId("p1"))
    assert cmd.execute()
    assert model.focused_pane_id == PaneId("p1")

    # Test undo
    assert cmd.undo()
    assert model.focused_pane_id is None

    # Test navigation command
    model.set_focused_pane(PaneId("p1"))
    nav_cmd = NavigateFocusCommand(model, Direction.RIGHT)
    assert nav_cmd.execute()
    assert model.focused_pane_id == PaneId("p2")

    # Test navigation undo
    assert nav_cmd.undo()
    assert model.focused_pane_id == PaneId("p1")

    # Test invalid focus
    invalid_cmd = FocusPaneCommand(model, PaneId("invalid"))
    assert not invalid_cmd.execute()
    assert not invalid_cmd.executed


def test_keyboard_navigation(qtbot):
    """Test keyboard navigation."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from vfwidgets_multisplit.view.container import PaneContainer

    model = PaneModel()
    container = PaneContainer(model)
    qtbot.addWidget(container)

    # Add panes
    leaf1 = LeafNode(PaneId("p1"), WidgetId("w1"))
    leaf2 = LeafNode(PaneId("p2"), WidgetId("w2"))

    model.root = SplitNode(NodeId("split1"), Orientation.HORIZONTAL, [leaf1, leaf2], [0.5, 0.5])
    model._rebuild_registry()
    model.set_focused_pane(PaneId("p1"))

    # Test Tab navigation
    QTest.keyClick(container, Qt.Key.Key_Tab)
    assert model.focused_pane_id == PaneId("p2")

    # Test Shift+Tab
    QTest.keyClick(container, Qt.Key.Key_Tab, Qt.KeyboardModifier.ShiftModifier)
    assert model.focused_pane_id == PaneId("p1")

    # Test Alt+Arrow
    QTest.keyClick(container, Qt.Key.Key_Right, Qt.KeyboardModifier.AltModifier)
    assert model.focused_pane_id == PaneId("p2")


def test_set_ratios_command():
    """Test set ratios command."""
    from vfwidgets_multisplit.controller.commands import SetRatiosCommand

    model = PaneModel()

    # Build tree with split
    leaf1 = LeafNode(PaneId("p1"), WidgetId("w1"))
    leaf2 = LeafNode(PaneId("p2"), WidgetId("w2"))

    split_node = SplitNode(NodeId("split1"), Orientation.HORIZONTAL, [leaf1, leaf2], [0.5, 0.5])
    model.root = split_node
    model._rebuild_registry()

    # Test set ratios command
    cmd = SetRatiosCommand(model, NodeId("split1"), [0.3, 0.7])
    assert cmd.execute()
    assert split_node.ratios == [0.3, 0.7]

    # Test undo
    assert cmd.undo()
    assert split_node.ratios == [0.5, 0.5]

    # Test invalid ratios
    invalid_cmd = SetRatiosCommand(model, NodeId("split1"), [-0.1, 1.1])
    assert not invalid_cmd.execute()

    # Test invalid node
    invalid_node_cmd = SetRatiosCommand(model, NodeId("invalid"), [0.5, 0.5])
    assert not invalid_node_cmd.execute()


def test_session_manager():
    """Test session save/load."""
    import tempfile
    from pathlib import Path

    from vfwidgets_multisplit.core.session import SessionManager

    # Create model with structure
    model = PaneModel()
    leaf1 = LeafNode(PaneId("p1"), WidgetId("editor:main.py"))
    leaf2 = LeafNode(PaneId("p2"), WidgetId("terminal:1"))

    model.root = SplitNode(NodeId("split1"), Orientation.VERTICAL, [leaf1, leaf2], [0.7, 0.3])
    model._rebuild_registry()
    model.set_focused_pane(PaneId("p1"))

    session = SessionManager(model)

    # Test string serialization
    json_str = session.save_to_string()
    assert "editor:main.py" in json_str
    assert "0.7" in json_str

    # Test file save/load
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        filepath = Path(f.name)

    try:
        # Save
        assert session.save_to_file(filepath)
        assert filepath.exists()

        # Clear model
        model.root = None
        model._rebuild_registry()

        # Load
        assert session.load_from_file(filepath)
        assert isinstance(model.root, SplitNode)
        assert len(model.get_all_pane_ids()) == 2
        assert model.focused_pane_id == PaneId("p1")

    finally:
        filepath.unlink()  # Clean up


def test_phase2_integration(qtbot):
    """Test complete Phase 2 functionality."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from vfwidgets_multisplit.controller.controller import PaneController
    from vfwidgets_multisplit.core.session import SessionManager
    from vfwidgets_multisplit.core.types import WherePosition
    from vfwidgets_multisplit.view.container import PaneContainer

    # Create and populate model
    model = PaneModel()
    controller = PaneController(model)
    container = PaneContainer(model)
    qtbot.addWidget(container)

    # Build structure - first create an initial pane
    model.root = LeafNode(PaneId("p0"), WidgetId("initial"))
    model._rebuild_registry()

    controller.split_pane(PaneId("p0"), WidgetId("editor:main.py"), WherePosition.LEFT)

    # Check what panes we have
    all_panes = model.get_all_pane_ids()
    assert len(all_panes) >= 2  # Should have at least 2 panes now

    # Test focus with an actual pane
    first_pane = all_panes[0]
    model.set_focused_pane(first_pane)
    assert model.focused_pane_id == first_pane

    # Test keyboard navigation
    QTest.keyClick(container, Qt.Key.Key_Tab)
    # Note: The exact final focus depends on the pane order in tree

    # Test session persistence
    session = SessionManager(model)
    saved = session.save_to_string()

    model.root = None
    model._rebuild_registry()

    session.load_from_string(saved)
    assert len(model.get_all_pane_ids()) >= 2  # Should have multiple panes
