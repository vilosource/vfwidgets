"""Tests for tree utilities."""

import unittest

from vfwidgets_multisplit.core.nodes import LeafNode, SplitNode
from vfwidgets_multisplit.core.tree_utils import (
    find_node_by_id,
    get_all_leaves,
    get_tree_depth,
    normalize_ratios,
    validate_ratios,
    validate_tree_structure,
)
from vfwidgets_multisplit.core.types import Orientation, PaneId
from vfwidgets_multisplit.core.utils import generate_node_id, generate_pane_id, generate_widget_id


class TestTreeUtils(unittest.TestCase):
    """Test tree utility functions."""

    def test_normalize_ratios(self):
        """Test ratio normalization."""
        # Normal case
        ratios = [0.3, 0.7]
        normalized = normalize_ratios(ratios)
        self.assertAlmostEqual(sum(normalized), 1.0)

        # All zeros case
        ratios = [0.0, 0.0, 0.0]
        normalized = normalize_ratios(ratios)
        self.assertAlmostEqual(sum(normalized), 1.0)
        self.assertTrue(all(r == 1.0 / 3.0 for r in normalized))

    def test_validate_ratios(self):
        """Test ratio validation."""
        # Valid ratios
        self.assertTrue(validate_ratios([0.5, 0.5]))
        self.assertTrue(validate_ratios([0.3, 0.3, 0.4]))

        # Invalid ratios
        self.assertFalse(validate_ratios([]))  # Empty
        self.assertFalse(validate_ratios([0.6, 0.6]))  # Sum > 1
        self.assertFalse(validate_ratios([0.5, -0.1, 0.6]))  # Negative

    def test_find_node_by_id(self):
        """Test finding nodes by ID."""
        # Create simple tree
        pane_id = generate_pane_id()
        leaf = LeafNode(pane_id=pane_id, widget_id=generate_widget_id("editor", "main.py"))

        # Find existing node
        found = find_node_by_id(leaf, pane_id)
        self.assertIsNotNone(found)
        self.assertEqual(found.pane_id, pane_id)

        # Find non-existing node
        missing_id = generate_pane_id()
        found = find_node_by_id(leaf, missing_id)
        self.assertIsNone(found)

    def test_get_all_leaves(self):
        """Test collecting all leaf nodes."""
        # Single leaf
        leaf = LeafNode(
            pane_id=generate_pane_id(),
            widget_id=generate_widget_id("editor", "main.py"),
        )
        leaves = get_all_leaves(leaf)
        self.assertEqual(len(leaves), 1)
        self.assertEqual(leaves[0], leaf)

        # Split with multiple leaves
        leaf1 = LeafNode(
            pane_id=generate_pane_id(),
            widget_id=generate_widget_id("editor", "file1.py"),
        )
        leaf2 = LeafNode(
            pane_id=generate_pane_id(),
            widget_id=generate_widget_id("editor", "file2.py"),
        )
        split = SplitNode(
            node_id=generate_node_id(),
            orientation=Orientation.HORIZONTAL,
            children=[leaf1, leaf2],
            ratios=[0.5, 0.5],
        )

        leaves = get_all_leaves(split)
        self.assertEqual(len(leaves), 2)
        self.assertIn(leaf1, leaves)
        self.assertIn(leaf2, leaves)

    def test_get_tree_depth(self):
        """Test tree depth calculation."""
        # Single leaf
        leaf = LeafNode(
            pane_id=generate_pane_id(),
            widget_id=generate_widget_id("editor", "main.py"),
        )
        depth = get_tree_depth(leaf)
        self.assertEqual(depth, 1)

        # Nested tree
        leaf1 = LeafNode(
            pane_id=generate_pane_id(),
            widget_id=generate_widget_id("editor", "file1.py"),
        )
        leaf2 = LeafNode(
            pane_id=generate_pane_id(),
            widget_id=generate_widget_id("editor", "file2.py"),
        )
        split = SplitNode(
            node_id=generate_node_id(),
            orientation=Orientation.HORIZONTAL,
            children=[leaf1, leaf2],
            ratios=[0.5, 0.5],
        )
        depth = get_tree_depth(split)
        self.assertEqual(depth, 2)

    def test_validate_tree_structure(self):
        """Test tree structure validation."""
        # Valid leaf
        leaf = LeafNode(
            pane_id=generate_pane_id(),
            widget_id=generate_widget_id("editor", "main.py"),
        )
        is_valid, errors = validate_tree_structure(leaf)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

        # Invalid leaf (missing pane_id)
        invalid_leaf = LeafNode(
            pane_id=PaneId(""),
            widget_id=generate_widget_id("editor", "main.py"),
        )
        is_valid, errors = validate_tree_structure(invalid_leaf)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)


if __name__ == "__main__":
    unittest.main()
