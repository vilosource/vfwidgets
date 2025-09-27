"""Tests for command pattern implementation."""

import unittest

from vfwidgets_multisplit.controller.commands import RemovePaneCommand, SplitPaneCommand
from vfwidgets_multisplit.core.model import PaneModel
from vfwidgets_multisplit.core.nodes import LeafNode, SplitNode
from vfwidgets_multisplit.core.types import NodeId, Orientation, PaneId, WherePosition, WidgetId


class TestCommands(unittest.TestCase):
    """Test command pattern functionality."""

    def test_split_pane_command_execute(self):
        """Test split pane command execution."""
        # Create initial model with single pane
        model = PaneModel(
            root=LeafNode(PaneId("p1"), WidgetId("editor"))
        )
        model._rebuild_registry()

        # Create split command
        command = SplitPaneCommand(
            model, PaneId("p1"), WidgetId("terminal"), WherePosition.BOTTOM, 0.3
        )

        # Execute command
        success = command.execute()
        self.assertTrue(success)
        self.assertTrue(command.executed)

        # Verify tree structure changed
        self.assertIsInstance(model.root, SplitNode)
        self.assertEqual(model.root.orientation, Orientation.VERTICAL)
        self.assertEqual(len(model.root.children), 2)
        self.assertEqual(len(model.get_all_pane_ids()), 2)

    def test_split_pane_command_undo(self):
        """Test split pane command undo."""
        # Create initial model
        model = PaneModel(
            root=LeafNode(PaneId("p1"), WidgetId("editor"))
        )
        model._rebuild_registry()

        # Execute and undo split
        command = SplitPaneCommand(
            model, PaneId("p1"), WidgetId("terminal"), WherePosition.RIGHT
        )

        # Execute
        command.execute()
        self.assertEqual(len(model.get_all_pane_ids()), 2)

        # Undo
        success = command.undo()
        self.assertTrue(success)
        self.assertFalse(command.executed)

        # Verify back to original state
        self.assertIsInstance(model.root, LeafNode)
        self.assertEqual(model.root.pane_id, PaneId("p1"))
        self.assertEqual(len(model.get_all_pane_ids()), 1)

    def test_split_pane_replace_position(self):
        """Test split pane with REPLACE position."""
        model = PaneModel(
            root=LeafNode(PaneId("p1"), WidgetId("old"))
        )
        model._rebuild_registry()

        command = SplitPaneCommand(
            model, PaneId("p1"), WidgetId("new"), WherePosition.REPLACE
        )

        command.execute()

        # Should replace the pane entirely
        self.assertIsInstance(model.root, LeafNode)
        self.assertEqual(model.root.widget_id, WidgetId("new"))
        self.assertEqual(len(model.get_all_pane_ids()), 1)

    def test_remove_pane_command(self):
        """Test remove pane command."""
        # Create tree with multiple panes
        root = SplitNode(
            node_id=NodeId("root"),
            orientation=Orientation.HORIZONTAL
        )
        leaf1 = LeafNode(PaneId("p1"), WidgetId("editor"))
        leaf2 = LeafNode(PaneId("p2"), WidgetId("terminal"))

        root.add_child(leaf1)
        root.add_child(leaf2)

        model = PaneModel(root=root)

        # Remove one pane
        command = RemovePaneCommand(model, PaneId("p2"))
        success = command.execute()

        self.assertTrue(success)
        # Should collapse to single leaf
        self.assertIsInstance(model.root, LeafNode)
        self.assertEqual(model.root.pane_id, PaneId("p1"))
        self.assertEqual(len(model.get_all_pane_ids()), 1)

    def test_remove_pane_command_undo(self):
        """Test remove pane command undo."""
        # Create tree with multiple panes
        root = SplitNode(
            node_id=NodeId("root"),
            orientation=Orientation.HORIZONTAL
        )
        leaf1 = LeafNode(PaneId("p1"), WidgetId("editor"))
        leaf2 = LeafNode(PaneId("p2"), WidgetId("terminal"))

        root.add_child(leaf1)
        root.add_child(leaf2)

        model = PaneModel(root=root)

        # Execute and undo removal
        command = RemovePaneCommand(model, PaneId("p2"))
        command.execute()

        # Verify removal
        self.assertEqual(len(model.get_all_pane_ids()), 1)

        # Undo
        success = command.undo()
        self.assertTrue(success)

        # Verify restoration
        self.assertIsInstance(model.root, SplitNode)
        self.assertEqual(len(model.get_all_pane_ids()), 2)

    def test_command_can_execute_undo(self):
        """Test command execution state tracking."""
        model = PaneModel(
            root=LeafNode(PaneId("p1"), WidgetId("test"))
        )

        command = SplitPaneCommand(
            model, PaneId("p1"), WidgetId("new"), WherePosition.RIGHT
        )

        # Initially can execute, cannot undo
        self.assertTrue(command.can_execute())
        self.assertFalse(command.can_undo())

        # After execution
        command.execute()
        self.assertFalse(command.can_execute())
        self.assertTrue(command.can_undo())

        # After undo
        command.undo()
        self.assertTrue(command.can_execute())
        self.assertFalse(command.can_undo())

    def test_split_pane_before_after_positions(self):
        """Test split pane with BEFORE and AFTER positions."""
        # Create parent with existing children
        root = SplitNode(
            node_id=NodeId("root"),
            orientation=Orientation.HORIZONTAL
        )
        leaf1 = LeafNode(PaneId("p1"), WidgetId("first"))
        leaf2 = LeafNode(PaneId("p2"), WidgetId("second"))

        root.add_child(leaf1)
        root.add_child(leaf2)

        model = PaneModel(root=root)

        # Insert BEFORE p2
        command = SplitPaneCommand(
            model, PaneId("p2"), WidgetId("middle"), WherePosition.BEFORE
        )
        command.execute()

        # Should have 3 children now
        self.assertEqual(len(model.root.children), 3)
        self.assertEqual(len(model.get_all_pane_ids()), 3)

        # Check order: p1, new_pane, p2
        children_widgets = [child.widget_id for child in model.root.children]
        self.assertEqual(children_widgets[0], WidgetId("first"))
        self.assertEqual(children_widgets[1], WidgetId("middle"))
        self.assertEqual(children_widgets[2], WidgetId("second"))


if __name__ == '__main__':
    unittest.main()
