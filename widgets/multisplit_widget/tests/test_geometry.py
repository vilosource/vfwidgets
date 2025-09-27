"""Tests for geometry calculator."""

import unittest

from vfwidgets_multisplit.core.geometry import GeometryCalculator
from vfwidgets_multisplit.core.nodes import LeafNode, SplitNode
from vfwidgets_multisplit.core.types import Bounds, Orientation
from vfwidgets_multisplit.core.utils import generate_node_id, generate_pane_id, generate_widget_id


class TestGeometry(unittest.TestCase):
    """Test geometry calculation."""

    def test_single_leaf(self):
        """Test geometry for single leaf node."""
        calc = GeometryCalculator()
        pane_id = generate_pane_id()

        leaf = LeafNode(
            pane_id=pane_id,
            widget_id=generate_widget_id("editor", "test.py"),
        )

        bounds = Bounds(0, 0, 800, 600)
        result = calc.calculate(leaf, bounds)

        # Single leaf gets full bounds
        self.assertEqual(result[pane_id], bounds)

    def test_horizontal_split(self):
        """Test horizontal split geometry."""
        calc = GeometryCalculator(divider_width=4)

        pane1_id = generate_pane_id()
        pane2_id = generate_pane_id()

        root = SplitNode(
            node_id=generate_node_id(),
            orientation=Orientation.HORIZONTAL,
            children=[
                LeafNode(pane1_id, generate_widget_id("editor", "1.py")),
                LeafNode(pane2_id, generate_widget_id("editor", "2.py"))
            ],
            ratios=[0.5, 0.5],
        )

        bounds = Bounds(0, 0, 804, 600)  # 804 = 400 + 4 + 400
        result = calc.calculate(root, bounds)

        # Check first pane
        self.assertEqual(result[pane1_id].x, 0)
        self.assertEqual(result[pane1_id].width, 400)

        # Check second pane (after divider)
        self.assertEqual(result[pane2_id].x, 404)
        self.assertEqual(result[pane2_id].width, 400)

    def test_vertical_split(self):
        """Test vertical split geometry."""
        calc = GeometryCalculator(divider_width=4)

        pane1_id = generate_pane_id()
        pane2_id = generate_pane_id()

        root = SplitNode(
            node_id=generate_node_id(),
            orientation=Orientation.VERTICAL,
            children=[
                LeafNode(pane1_id, generate_widget_id("editor", "1.py")),
                LeafNode(pane2_id, generate_widget_id("terminal", "bash"))
            ],
            ratios=[0.7, 0.3],
        )

        bounds = Bounds(0, 0, 800, 604)  # 604 = 420 + 4 + 180
        result = calc.calculate(root, bounds)

        # Check first pane (70% of available height)
        self.assertEqual(result[pane1_id].y, 0)
        self.assertEqual(result[pane1_id].height, 420)

        # Check second pane (30% of available height)
        self.assertEqual(result[pane2_id].y, 424)
        self.assertEqual(result[pane2_id].height, 180)

    def test_divider_bounds(self):
        """Test divider bounds calculation."""
        calc = GeometryCalculator(divider_width=4)

        root = SplitNode(
            node_id=generate_node_id(),
            orientation=Orientation.HORIZONTAL,
            children=[
                LeafNode(generate_pane_id(), generate_widget_id("editor", "1.py")),
                LeafNode(generate_pane_id(), generate_widget_id("editor", "2.py"))
            ],
            ratios=[0.5, 0.5],
        )

        bounds = Bounds(0, 0, 804, 600)
        dividers = calc.calculate_divider_bounds(root, bounds)

        # Should have one divider
        self.assertEqual(len(dividers), 1)

        # Divider should be vertical, in the middle
        divider = dividers[0]
        self.assertEqual(divider.x, 400)
        self.assertEqual(divider.width, 4)
        self.assertEqual(divider.height, 600)


if __name__ == '__main__':
    unittest.main()
