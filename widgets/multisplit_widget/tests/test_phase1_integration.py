"""Phase 1 integration tests."""

import unittest

from vfwidgets_multisplit.controller.controller import PaneController
from vfwidgets_multisplit.core.model import PaneModel
from vfwidgets_multisplit.core.nodes import LeafNode, SplitNode
from vfwidgets_multisplit.core.types import PaneId, WherePosition, WidgetId


class TestPhase1Integration(unittest.TestCase):
    """Test complete Phase 1 functionality integration."""

    def test_phase1_integration(self):
        """Test complete Phase 1 functionality."""
        # Create model
        model = PaneModel()

        # Create controller
        controller = PaneController(model)

        # NOTE: Container testing requires Qt app, so we'll focus on Model+Controller
        # container = PaneContainer(model)

        # Add initial pane
        leaf = LeafNode(PaneId("p1"), WidgetId("editor:main.py"))
        model.root = leaf
        model._rebuild_registry()

        # Verify initial state
        self.assertIsInstance(model.root, LeafNode)
        self.assertEqual(len(model.get_all_pane_ids()), 1)

        # Split pane
        success = controller.split_pane(
            PaneId("p1"),
            WidgetId("terminal:1"),
            WherePosition.BOTTOM
        )

        self.assertTrue(success)

        # Verify structure
        self.assertIsInstance(model.root, SplitNode)
        self.assertEqual(len(model.get_all_pane_ids()), 2)

        # Test undo
        self.assertTrue(controller.can_undo())
        controller.undo()
        self.assertIsInstance(model.root, LeafNode)
        self.assertEqual(len(model.get_all_pane_ids()), 1)

        # Test redo
        self.assertTrue(controller.can_redo())
        controller.redo()
        self.assertIsInstance(model.root, SplitNode)
        self.assertEqual(len(model.get_all_pane_ids()), 2)

    def test_complex_splitting_operations(self):
        """Test complex splitting operations."""
        model = PaneModel()
        controller = PaneController(model)

        # Start with single pane
        leaf = LeafNode(PaneId("main"), WidgetId("editor"))
        model.root = leaf
        model._rebuild_registry()

        # Split horizontally
        controller.split_pane(PaneId("main"), WidgetId("terminal"), WherePosition.RIGHT, 0.7)
        self.assertEqual(len(model.get_all_pane_ids()), 2)

        # Get the new pane ID
        pane_ids = model.get_all_pane_ids()
        terminal_id = next(pid for pid in pane_ids if pid != PaneId("main"))

        # Split the terminal vertically
        controller.split_pane(terminal_id, WidgetId("browser"), WherePosition.BOTTOM, 0.6)
        self.assertEqual(len(model.get_all_pane_ids()), 3)

        # Verify structure: should have horizontal split with nested vertical split
        self.assertIsInstance(model.root, SplitNode)
        self.assertEqual(model.root.orientation.value, "horizontal")
        self.assertEqual(len(model.root.children), 2)

        # First child should be the main editor
        first_child = model.root.children[0]
        self.assertIsInstance(first_child, LeafNode)
        self.assertEqual(first_child.widget_id, WidgetId("editor"))

        # Second child should be a vertical split
        second_child = model.root.children[1]
        self.assertIsInstance(second_child, SplitNode)
        self.assertEqual(second_child.orientation.value, "vertical")
        self.assertEqual(len(second_child.children), 2)

    def test_pane_removal_operations(self):
        """Test pane removal and tree collapse."""
        model = PaneModel()
        controller = PaneController(model)

        # Create complex tree
        leaf = LeafNode(PaneId("main"), WidgetId("editor"))
        model.root = leaf
        model._rebuild_registry()

        # Split to create 3 panes
        controller.split_pane(PaneId("main"), WidgetId("terminal"), WherePosition.RIGHT)
        pane_ids = model.get_all_pane_ids()
        terminal_id = next(pid for pid in pane_ids if pid != PaneId("main"))

        controller.split_pane(terminal_id, WidgetId("browser"), WherePosition.BOTTOM)
        self.assertEqual(len(model.get_all_pane_ids()), 3)

        # Remove one pane - should collapse split
        pane_ids = model.get_all_pane_ids()
        browser_id = next(pid for pid in pane_ids if pid not in [PaneId("main"), terminal_id])

        controller.remove_pane(browser_id)

        # Should be back to 2 panes with horizontal split
        self.assertEqual(len(model.get_all_pane_ids()), 2)
        self.assertIsInstance(model.root, SplitNode)
        self.assertEqual(model.root.orientation.value, "horizontal")

        # Remove another pane - should collapse to single pane
        controller.remove_pane(terminal_id)
        self.assertEqual(len(model.get_all_pane_ids()), 1)
        self.assertIsInstance(model.root, LeafNode)
        self.assertEqual(model.root.pane_id, PaneId("main"))

    def test_model_serialization_integration(self):
        """Test model serialization with complex structures."""
        model = PaneModel()
        controller = PaneController(model)

        # Create complex structure
        leaf = LeafNode(PaneId("main"), WidgetId("editor"))
        model.root = leaf
        model._rebuild_registry()

        controller.split_pane(PaneId("main"), WidgetId("terminal"), WherePosition.BOTTOM, 0.3)
        pane_ids = model.get_all_pane_ids()
        next(pid for pid in pane_ids if pid != PaneId("main"))

        controller.split_pane(PaneId("main"), WidgetId("sidebar"), WherePosition.LEFT, 0.2)

        # Serialize
        data = model.to_dict()
        self.assertIsNotNone(data['root'])
        self.assertEqual(data['root']['type'], 'split')

        # Deserialize
        restored_model = PaneModel.from_dict(data)
        self.assertEqual(len(restored_model.get_all_pane_ids()), 3)

        # Verify structure is equivalent
        self.assertIsInstance(restored_model.root, SplitNode)

    def test_command_undo_redo_chain(self):
        """Test complex undo/redo chains."""
        model = PaneModel()
        controller = PaneController(model)

        # Start simple
        leaf = LeafNode(PaneId("main"), WidgetId("editor"))
        model.root = leaf
        model._rebuild_registry()

        initial_count = len(model.get_all_pane_ids())
        self.assertEqual(initial_count, 1)

        # Perform series of operations with specific targets
        # Split main pane right
        controller.split_pane(PaneId("main"), WidgetId("terminal"), WherePosition.RIGHT)
        self.assertEqual(len(model.get_all_pane_ids()), 2)

        # Split main pane bottom
        controller.split_pane(PaneId("main"), WidgetId("browser"), WherePosition.BOTTOM)
        self.assertEqual(len(model.get_all_pane_ids()), 3)

        # Undo operations one by one
        self.assertTrue(controller.can_undo())
        controller.undo()  # Undo browser split
        self.assertEqual(len(model.get_all_pane_ids()), 2)

        self.assertTrue(controller.can_undo())
        controller.undo()  # Undo terminal split
        self.assertEqual(len(model.get_all_pane_ids()), 1)

        self.assertFalse(controller.can_undo())

        # Redo operations
        self.assertTrue(controller.can_redo())
        controller.redo()  # Redo terminal split
        self.assertEqual(len(model.get_all_pane_ids()), 2)

        self.assertTrue(controller.can_redo())
        controller.redo()  # Redo browser split
        self.assertEqual(len(model.get_all_pane_ids()), 3)

        self.assertFalse(controller.can_redo())


if __name__ == '__main__':
    unittest.main()
