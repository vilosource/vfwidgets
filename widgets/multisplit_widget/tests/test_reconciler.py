"""Tests for tree reconciliation."""

import unittest

from vfwidgets_multisplit.core.nodes import LeafNode, SplitNode
from vfwidgets_multisplit.core.types import Orientation
from vfwidgets_multisplit.core.utils import generate_node_id, generate_pane_id, generate_widget_id
from vfwidgets_multisplit.view.tree_reconciler import TreeReconciler


class TestTreeReconciler(unittest.TestCase):
    """Test tree reconciliation."""

    def test_no_changes(self):
        """Test diff with identical trees."""
        reconciler = TreeReconciler()

        pane_id = generate_pane_id()
        tree = LeafNode(
            pane_id=pane_id,
            widget_id=generate_widget_id("editor", "test.py"),
        )

        diff = reconciler.diff(tree, tree)
        self.assertFalse(diff.has_changes())

    def test_all_added(self):
        """Test diff when all panes are new."""
        reconciler = TreeReconciler()

        pane1_id = generate_pane_id()
        pane2_id = generate_pane_id()

        tree = SplitNode(
            node_id=generate_node_id(),
            orientation=Orientation.HORIZONTAL,
            children=[
                LeafNode(pane1_id, generate_widget_id("editor", "1.py")),
                LeafNode(pane2_id, generate_widget_id("editor", "2.py")),
            ],
            ratios=[0.5, 0.5],
        )

        diff = reconciler.diff(None, tree)

        self.assertEqual(diff.added, {pane1_id, pane2_id})
        self.assertEqual(len(diff.removed), 0)

    def test_all_removed(self):
        """Test diff when all panes are removed."""
        reconciler = TreeReconciler()

        pane1_id = generate_pane_id()
        pane2_id = generate_pane_id()

        tree = SplitNode(
            node_id=generate_node_id(),
            orientation=Orientation.HORIZONTAL,
            children=[
                LeafNode(pane1_id, generate_widget_id("editor", "1.py")),
                LeafNode(pane2_id, generate_widget_id("editor", "2.py")),
            ],
            ratios=[0.5, 0.5],
        )

        diff = reconciler.diff(tree, None)

        self.assertEqual(diff.removed, {pane1_id, pane2_id})
        self.assertEqual(len(diff.added), 0)

    def test_pane_modified(self):
        """Test detecting modified panes."""
        reconciler = TreeReconciler()

        pane_id = generate_pane_id()

        old_tree = LeafNode(
            pane_id=pane_id,
            widget_id=generate_widget_id("editor", "old.py"),
        )

        new_tree = LeafNode(
            pane_id=pane_id,
            widget_id=generate_widget_id("editor", "new.py"),
        )

        diff = reconciler.diff(old_tree, new_tree)

        self.assertIn(pane_id, diff.modified)
        self.assertEqual(len(diff.added), 0)
        self.assertEqual(len(diff.removed), 0)

    def test_mixed_changes(self):
        """Test diff with mixed changes."""
        reconciler = TreeReconciler()

        # Common pane that will be kept
        common_id = generate_pane_id()
        removed_id = generate_pane_id()
        added_id = generate_pane_id()

        old_tree = SplitNode(
            node_id=generate_node_id(),
            orientation=Orientation.HORIZONTAL,
            children=[
                LeafNode(common_id, generate_widget_id("editor", "common.py")),
                LeafNode(removed_id, generate_widget_id("editor", "old.py")),
            ],
            ratios=[0.5, 0.5],
        )

        new_tree = SplitNode(
            node_id=generate_node_id(),
            orientation=Orientation.HORIZONTAL,
            children=[
                LeafNode(common_id, generate_widget_id("editor", "common.py")),
                LeafNode(added_id, generate_widget_id("editor", "new.py")),
            ],
            ratios=[0.5, 0.5],
        )

        diff = reconciler.diff(old_tree, new_tree)

        self.assertIn(removed_id, diff.removed)
        self.assertIn(added_id, diff.added)
        self.assertNotIn(common_id, diff.removed)
        self.assertNotIn(common_id, diff.added)


if __name__ == "__main__":
    unittest.main()
