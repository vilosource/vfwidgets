"""Tests for core types module."""

import unittest

from vfwidgets_multisplit.core.types import (
    Orientation,
    SizeConstraints,
    WherePosition,
    WidgetId,
)


class TestWherePosition(unittest.TestCase):
    """Test WherePosition enum."""

    def test_where_position_complete(self):
        """Test all WherePosition values are present."""
        positions = [
            WherePosition.LEFT,
            WherePosition.RIGHT,
            WherePosition.TOP,
            WherePosition.BOTTOM,
            WherePosition.BEFORE,
            WherePosition.AFTER,
            WherePosition.REPLACE,
        ]
        self.assertEqual(len(positions), 7)
        self.assertTrue(all(isinstance(p, WherePosition) for p in positions))

    def test_to_orientation_handles_new_positions(self):
        """Test to_orientation() method handles BEFORE and AFTER correctly."""
        # BEFORE and AFTER should return None (no orientation)
        self.assertIsNone(WherePosition.BEFORE.to_orientation())
        self.assertIsNone(WherePosition.AFTER.to_orientation())

        # Existing positions should still work
        self.assertEqual(WherePosition.LEFT.to_orientation(), Orientation.HORIZONTAL)
        self.assertEqual(WherePosition.RIGHT.to_orientation(), Orientation.HORIZONTAL)
        self.assertEqual(WherePosition.TOP.to_orientation(), Orientation.VERTICAL)
        self.assertEqual(WherePosition.BOTTOM.to_orientation(), Orientation.VERTICAL)
        self.assertIsNone(WherePosition.REPLACE.to_orientation())


class TestSizeConstraints(unittest.TestCase):
    """Test SizeConstraints dataclass."""

    def test_size_constraints_creation(self):
        """Test size constraints creation with defaults."""
        constraints = SizeConstraints()
        self.assertEqual(constraints.min_width, 50)
        self.assertEqual(constraints.min_height, 50)
        self.assertIsNone(constraints.max_width)
        self.assertIsNone(constraints.max_height)

    def test_size_constraints_validation(self):
        """Test size constraints validation."""
        # Valid constraints
        constraints = SizeConstraints(min_width=100, min_height=50)
        self.assertEqual(constraints.min_width, 100)
        self.assertEqual(constraints.min_height, 50)

        # Invalid: negative minimums
        with self.assertRaises(ValueError):
            SizeConstraints(min_width=-1)

        with self.assertRaises(ValueError):
            SizeConstraints(min_height=-1)

        # Invalid: max < min
        with self.assertRaises(ValueError):
            SizeConstraints(min_width=100, max_width=50)

        with self.assertRaises(ValueError):
            SizeConstraints(min_height=100, max_height=50)

    def test_clamp_size(self):
        """Test size clamping functionality."""
        constraints = SizeConstraints(min_width=100, min_height=50, max_width=200, max_height=150)

        # Below minimum
        self.assertEqual(constraints.clamp_size(50, 25), (100, 50))

        # Within range
        self.assertEqual(constraints.clamp_size(150, 100), (150, 100))

        # Above maximum
        self.assertEqual(constraints.clamp_size(300, 200), (200, 150))

        # Mixed
        self.assertEqual(constraints.clamp_size(50, 200), (100, 150))

    def test_clamp_size_no_max(self):
        """Test size clamping with no maximum limits."""
        constraints = SizeConstraints(min_width=100, min_height=50)

        # Below minimum
        self.assertEqual(constraints.clamp_size(50, 25), (100, 50))

        # Large values should not be clamped
        self.assertEqual(constraints.clamp_size(1000, 500), (1000, 500))


class TestNodeParentReferences(unittest.TestCase):
    """Test parent reference functionality in nodes."""

    def test_parent_references(self):
        """Test parent tracking in tree."""
        from vfwidgets_multisplit.core.nodes import LeafNode, SplitNode
        from vfwidgets_multisplit.core.utils import generate_node_id, generate_pane_id

        root = SplitNode(node_id=generate_node_id(), orientation=Orientation.HORIZONTAL)
        leaf1 = LeafNode(pane_id=generate_pane_id(), widget_id=WidgetId("w1"))
        leaf2 = LeafNode(pane_id=generate_pane_id(), widget_id=WidgetId("w2"))

        root.add_child(leaf1)
        root.add_child(leaf2)

        self.assertEqual(leaf1.parent, root)
        self.assertEqual(leaf2.parent, root)
        self.assertEqual(leaf1.get_root(), root)
        self.assertEqual(leaf1.get_depth(), 1)

    def test_node_manipulation(self):
        """Test add/remove/replace child functionality."""
        from vfwidgets_multisplit.core.nodes import LeafNode, SplitNode
        from vfwidgets_multisplit.core.utils import generate_node_id, generate_pane_id

        root = SplitNode(node_id=generate_node_id(), orientation=Orientation.HORIZONTAL)
        leaf1 = LeafNode(pane_id=generate_pane_id(), widget_id=WidgetId("w1"))
        leaf2 = LeafNode(pane_id=generate_pane_id(), widget_id=WidgetId("w2"))
        leaf3 = LeafNode(pane_id=generate_pane_id(), widget_id=WidgetId("w3"))

        # Test add_child
        root.add_child(leaf1, 0.6)
        root.add_child(leaf2, 0.4)
        self.assertEqual(len(root.children), 2)
        self.assertEqual(root.ratios, [0.6, 0.4])

        # Test replace_child
        root.replace_child(leaf2, leaf3)
        self.assertEqual(leaf2.parent, None)
        self.assertEqual(leaf3.parent, root)
        self.assertIn(leaf3, root.children)
        self.assertNotIn(leaf2, root.children)

        # Test remove_child
        root.remove_child(leaf1)
        self.assertEqual(leaf1.parent, None)
        self.assertEqual(len(root.children), 1)
        self.assertEqual(len(root.ratios), 1)
        self.assertEqual(root.ratios[0], 1.0)  # Should be renormalized


if __name__ == "__main__":
    unittest.main()
