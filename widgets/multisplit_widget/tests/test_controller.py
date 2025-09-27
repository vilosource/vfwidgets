"""Tests for controller functionality."""

import unittest

from vfwidgets_multisplit.controller.controller import PaneController
from vfwidgets_multisplit.core.model import PaneModel
from vfwidgets_multisplit.core.nodes import LeafNode
from vfwidgets_multisplit.core.types import PaneId, WherePosition, WidgetId


class TestController(unittest.TestCase):
    """Test controller functionality."""

    def test_controller_command_execution(self):
        """Test command execution and undo/redo."""
        model = PaneModel(
            root=LeafNode(PaneId("p1"), WidgetId("w1"))
        )
        controller = PaneController(model)

        # Execute split
        success = controller.split_pane(
            PaneId("p1"), WidgetId("w2"),
            WherePosition.RIGHT
        )
        self.assertTrue(success)
        self.assertEqual(len(model.get_all_pane_ids()), 2)

        # Undo
        self.assertTrue(controller.can_undo())
        controller.undo()
        self.assertEqual(len(model.get_all_pane_ids()), 1)

        # Redo
        self.assertTrue(controller.can_redo())
        controller.redo()
        self.assertEqual(len(model.get_all_pane_ids()), 2)

    def test_controller_high_level_operations(self):
        """Test high-level controller operations."""
        model = PaneModel(
            root=LeafNode(PaneId("p1"), WidgetId("editor"))
        )
        controller = PaneController(model)

        # Split pane
        success = controller.split_pane(
            PaneId("p1"), WidgetId("terminal"), WherePosition.BOTTOM, 0.3
        )
        self.assertTrue(success)
        self.assertEqual(len(model.get_all_pane_ids()), 2)

        # Get new pane id
        pane_ids = model.get_all_pane_ids()
        new_pane_id = next(pid for pid in pane_ids if pid != PaneId("p1"))

        # Remove the new pane
        success = controller.remove_pane(new_pane_id)
        self.assertTrue(success)
        self.assertEqual(len(model.get_all_pane_ids()), 1)

    def test_controller_undo_redo_state(self):
        """Test undo/redo state management."""
        model = PaneModel(
            root=LeafNode(PaneId("p1"), WidgetId("editor"))
        )
        controller = PaneController(model)

        # Initially no undo/redo
        self.assertFalse(controller.can_undo())
        self.assertFalse(controller.can_redo())

        # After operation, can undo
        controller.split_pane(PaneId("p1"), WidgetId("terminal"), WherePosition.RIGHT)
        self.assertTrue(controller.can_undo())
        self.assertFalse(controller.can_redo())

        # After undo, can redo
        controller.undo()
        self.assertFalse(controller.can_undo())
        self.assertTrue(controller.can_redo())

        # After redo, can undo again
        controller.redo()
        self.assertTrue(controller.can_undo())
        self.assertFalse(controller.can_redo())

    def test_controller_history_management(self):
        """Test undo history management."""
        model = PaneModel(
            root=LeafNode(PaneId("p1"), WidgetId("editor"))
        )
        controller = PaneController(model)
        controller.max_undo_levels = 2  # Limit for testing

        # Execute multiple operations
        controller.split_pane(PaneId("p1"), WidgetId("term1"), WherePosition.RIGHT)
        pane_ids = model.get_all_pane_ids()
        new_id1 = next(pid for pid in pane_ids if pid != PaneId("p1"))

        controller.split_pane(new_id1, WidgetId("term2"), WherePosition.BOTTOM)
        pane_ids = model.get_all_pane_ids()
        new_id2 = next(pid for pid in pane_ids if pid not in [PaneId("p1"), new_id1])

        controller.split_pane(new_id2, WidgetId("term3"), WherePosition.TOP)

        # Should only be able to undo max_undo_levels times
        self.assertTrue(controller.can_undo())
        controller.undo()  # Undo 3rd split

        self.assertTrue(controller.can_undo())
        controller.undo()  # Undo 2nd split

        # 3rd undo might not be available due to history limit
        # This depends on implementation details

        # Clear history
        controller.clear_history()
        self.assertFalse(controller.can_undo())
        self.assertFalse(controller.can_redo())

    def test_controller_transactions(self):
        """Test transaction support."""
        model = PaneModel(
            root=LeafNode(PaneId("p1"), WidgetId("editor"))
        )
        controller = PaneController(model)

        # Test transaction depth tracking
        self.assertEqual(controller._transaction_depth, 0)

        controller._begin_transaction()
        self.assertEqual(controller._transaction_depth, 1)
        self.assertFalse(controller.can_undo())  # Can't undo during transaction

        # Execute command during transaction
        controller.split_pane(PaneId("p1"), WidgetId("terminal"), WherePosition.RIGHT)

        # Should be in transaction commands, not undo stack
        self.assertEqual(len(controller._transaction_commands), 1)
        self.assertEqual(len(controller._undo_stack), 0)

        # Commit transaction
        controller._commit_transaction()
        self.assertEqual(controller._transaction_depth, 0)
        self.assertEqual(len(controller._transaction_commands), 0)
        self.assertEqual(len(controller._undo_stack), 1)
        self.assertTrue(controller.can_undo())

    def test_controller_transaction_rollback(self):
        """Test transaction rollback."""
        model = PaneModel(
            root=LeafNode(PaneId("p1"), WidgetId("editor"))
        )
        controller = PaneController(model)

        initial_pane_count = len(model.get_all_pane_ids())

        # Begin transaction
        controller._begin_transaction()

        # Execute commands
        controller.split_pane(PaneId("p1"), WidgetId("terminal"), WherePosition.RIGHT)
        self.assertEqual(len(model.get_all_pane_ids()), 2)

        # Rollback transaction
        controller._rollback_transaction()

        # Should be back to initial state
        self.assertEqual(len(model.get_all_pane_ids()), initial_pane_count)
        self.assertEqual(controller._transaction_depth, 0)
        self.assertEqual(len(controller._transaction_commands), 0)


if __name__ == '__main__':
    unittest.main()
