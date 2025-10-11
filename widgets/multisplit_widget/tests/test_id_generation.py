"""Tests for ID generation system."""

import unittest

from vfwidgets_multisplit.core.types import NodeId, PaneId, WidgetId
from vfwidgets_multisplit.core.utils import (
    generate_node_id,
    generate_pane_id,
    generate_widget_id,
    parse_widget_id,
    validate_id_format,
)


class TestIDTypes(unittest.TestCase):
    """Test ID type definitions."""

    def test_pane_id_type(self):
        """Test PaneId type can be created."""
        pane_id = PaneId("test_pane_id")
        self.assertEqual(str(pane_id), "test_pane_id")
        self.assertIsInstance(pane_id, str)

    def test_node_id_type(self):
        """Test NodeId type can be created."""
        node_id = NodeId("test_node_id")
        self.assertEqual(str(node_id), "test_node_id")
        self.assertIsInstance(node_id, str)

    def test_widget_id_type(self):
        """Test WidgetId type can be created."""
        widget_id = WidgetId("test_widget_id")
        self.assertEqual(str(widget_id), "test_widget_id")
        self.assertIsInstance(widget_id, str)

    def test_id_types_are_distinct(self):
        """Test that ID types are distinct from each other."""
        pane_id = PaneId("test_id")
        node_id = NodeId("test_id")
        widget_id = WidgetId("test_id")

        # They should have the same string value but be different types
        self.assertEqual(str(pane_id), str(node_id))
        self.assertEqual(str(node_id), str(widget_id))

        # Type checking would distinguish them (MyPy/type checker level)
        # At runtime, they're all strings but with different type annotations


class TestIDGeneration(unittest.TestCase):
    """Test ID generation functions."""

    def test_pane_id_generation(self):
        """Test pane ID generation."""
        id1 = generate_pane_id()
        id2 = generate_pane_id()

        # IDs should be unique
        self.assertNotEqual(id1, id2)

        # IDs should follow format
        self.assertTrue(validate_id_format(str(id1), "pane"))
        self.assertTrue(str(id1).startswith("pane_"))

    def test_node_id_generation(self):
        """Test node ID generation."""
        id1 = generate_node_id()
        id2 = generate_node_id()

        self.assertNotEqual(id1, id2)
        self.assertTrue(validate_id_format(str(id1), "node"))

    def test_widget_id_generation(self):
        """Test widget ID generation."""
        widget_id = generate_widget_id("editor", "main.py")

        self.assertEqual(str(widget_id), "editor:main.py")
        self.assertTrue(validate_id_format(str(widget_id), "widget"))

    def test_widget_id_parsing(self):
        """Test widget ID parsing."""
        widget_id = generate_widget_id("terminal", "session1")
        type_hint, identifier = parse_widget_id(widget_id)

        self.assertEqual(type_hint, "terminal")
        self.assertEqual(identifier, "session1")

    def test_id_validation(self):
        """Test ID format validation."""
        # Valid formats
        self.assertTrue(validate_id_format("pane_12345678", "pane"))
        self.assertTrue(validate_id_format("node_abcdef01", "node"))
        self.assertTrue(validate_id_format("editor:file.txt", "widget"))

        # Invalid formats
        self.assertFalse(validate_id_format("invalid", "pane"))
        self.assertFalse(validate_id_format("pane-12345678", "pane"))
        self.assertFalse(validate_id_format("editor", "widget"))
        self.assertFalse(validate_id_format("", "pane"))


if __name__ == "__main__":
    unittest.main()
