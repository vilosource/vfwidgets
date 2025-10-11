"""Tests for core model module."""

import unittest

from vfwidgets_multisplit.core.model import PaneModel
from vfwidgets_multisplit.core.nodes import LeafNode, SplitNode
from vfwidgets_multisplit.core.types import NodeId, Orientation, PaneId, WidgetId
from vfwidgets_multisplit.core.utils import generate_node_id, generate_pane_id


class TestPaneModel(unittest.TestCase):
    """Test PaneModel functionality."""

    def test_pane_model_creation(self):
        """Test model creation and registry."""
        model = PaneModel()
        self.assertIsNone(model.root)
        self.assertEqual(len(model.get_all_pane_ids()), 0)

        # Add root
        leaf = LeafNode(PaneId("p1"), WidgetId("w1"))
        model.root = leaf
        model._rebuild_registry()

        self.assertEqual(model.get_pane(PaneId("p1")), leaf)
        self.assertEqual(len(model.get_all_pane_ids()), 1)

    def test_model_with_split_tree(self):
        """Test model with split tree structure."""
        # Create tree structure
        root = SplitNode(node_id=generate_node_id(), orientation=Orientation.HORIZONTAL)
        leaf1 = LeafNode(generate_pane_id(), WidgetId("editor"))
        leaf2 = LeafNode(generate_pane_id(), WidgetId("terminal"))

        root.add_child(leaf1)
        root.add_child(leaf2)

        model = PaneModel(root=root)

        # Test registry
        self.assertEqual(len(model.get_all_pane_ids()), 2)
        self.assertEqual(model.get_pane(leaf1.pane_id), leaf1)
        self.assertEqual(model.get_pane(leaf2.pane_id), leaf2)

    def test_model_serialization(self):
        """Test model serialization/deserialization."""
        model = PaneModel(root=LeafNode(PaneId("p1"), WidgetId("editor:main.py")))

        data = model.to_dict()
        self.assertEqual(data["root"]["type"], "leaf")
        self.assertEqual(data["root"]["widget_id"], "editor:main.py")

        model2 = PaneModel.from_dict(data)
        self.assertIsInstance(model2.root, LeafNode)
        self.assertEqual(model2.root.widget_id, WidgetId("editor:main.py"))

    def test_complex_tree_serialization(self):
        """Test serialization of complex tree structure."""
        # Create complex tree
        root = SplitNode(node_id=NodeId("root"), orientation=Orientation.VERTICAL)

        # Top pane
        top_pane = LeafNode(PaneId("top"), WidgetId("editor"))

        # Bottom split
        bottom_split = SplitNode(node_id=NodeId("bottom_split"), orientation=Orientation.HORIZONTAL)

        left_pane = LeafNode(PaneId("left"), WidgetId("terminal"))
        right_pane = LeafNode(PaneId("right"), WidgetId("browser"))

        bottom_split.add_child(left_pane, 0.7)
        bottom_split.add_child(right_pane, 0.3)

        root.add_child(top_pane, 0.6)
        root.add_child(bottom_split, 0.4)

        model = PaneModel(root=root, focused_pane_id=PaneId("top"))

        # Test serialization
        data = model.to_dict()
        self.assertEqual(data["focused_pane_id"], "top")
        self.assertEqual(data["root"]["type"], "split")
        self.assertEqual(len(data["root"]["children"]), 2)

        # Test deserialization
        model2 = PaneModel.from_dict(data)
        self.assertIsInstance(model2.root, SplitNode)
        self.assertEqual(model2.focused_pane_id, PaneId("top"))
        self.assertEqual(len(model2.get_all_pane_ids()), 3)  # top, left, right

    def test_model_validation(self):
        """Test model validation."""
        # Empty model is valid
        model = PaneModel()
        valid, errors = model.validate()
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)

        # Simple leaf is valid
        model.root = LeafNode(PaneId("p1"), WidgetId("w1"))
        valid, errors = model.validate()
        self.assertTrue(valid)


if __name__ == "__main__":
    unittest.main()
