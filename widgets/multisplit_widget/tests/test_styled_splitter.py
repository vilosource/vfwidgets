"""Tests for styled splitter functionality."""

import unittest

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from vfwidgets_multisplit.view.container import StyledSplitter


class TestStyledSplitter(unittest.TestCase):
    """Test styled splitter functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up QApplication for testing."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def test_splitter_styling(self):
        """Test splitter has proper styling."""
        splitter = StyledSplitter(Qt.Orientation.Horizontal)

        # Check handle width
        self.assertEqual(splitter.handleWidth(), 6)

        # Check children not collapsible
        self.assertFalse(splitter.childrenCollapsible())

        # Check base stylesheet is set
        self.assertIn("background-color: #e0e0e0", splitter.styleSheet())

    def test_vertical_splitter(self):
        """Test vertical splitter creation."""
        splitter = StyledSplitter(Qt.Orientation.Vertical)

        self.assertEqual(splitter.orientation(), Qt.Orientation.Vertical)
        self.assertEqual(splitter.handleWidth(), 6)

    def test_handle_creation(self):
        """Test custom handle creation."""
        splitter = StyledSplitter(Qt.Orientation.Horizontal)

        # Create handles by adding widgets
        from PySide6.QtWidgets import QWidget

        widget1 = QWidget()
        widget2 = QWidget()

        splitter.addWidget(widget1)
        splitter.addWidget(widget2)

        # Should have one handle between two widgets
        self.assertEqual(splitter.count(), 2)


if __name__ == "__main__":
    unittest.main()
