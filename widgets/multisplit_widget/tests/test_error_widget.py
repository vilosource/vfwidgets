"""Tests for error widget functionality."""

import unittest

from PySide6.QtWidgets import QApplication
from vfwidgets_multisplit.view.error_widget import ErrorWidget, ValidationOverlay


class TestErrorWidget(unittest.TestCase):
    """Test error widget functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up QApplication for testing."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def test_error_widget_creation(self):
        """Test error widget creation."""
        widget = ErrorWidget("Test error message")

        # Should have icon, message, and button
        self.assertTrue(widget.layout().count() >= 3)

    def test_error_message_update(self):
        """Test updating error message."""
        widget = ErrorWidget("Initial message")
        widget.set_error("Updated message")

        # Find the message label and check it was updated
        found_updated_message = False
        for i in range(widget.layout().count()):
            item = widget.layout().itemAt(i)
            if item and item.widget():
                from PySide6.QtWidgets import QLabel
                if isinstance(item.widget(), QLabel):
                    if item.widget().text() == "Updated message":
                        found_updated_message = True
                        break

        self.assertTrue(found_updated_message)

    def test_validation_overlay(self):
        """Test validation overlay functionality."""
        overlay = ValidationOverlay()

        # Initially no messages
        self.assertEqual(len(overlay.messages), 0)

        # Add a message
        overlay.show_validation_error("Test validation error", 100)
        self.assertEqual(len(overlay.messages), 1)

    def test_retry_signal(self):
        """Test retry button signal."""
        widget = ErrorWidget("Test error")

        # Should have retry_clicked signal
        self.assertTrue(hasattr(widget, 'retry_clicked'))


if __name__ == '__main__':
    unittest.main()
