"""Test complete MVP functionality."""

import tempfile
import unittest
from pathlib import Path

from PySide6.QtWidgets import QApplication, QWidget
from vfwidgets_multisplit.core.types import Direction, WherePosition
from vfwidgets_multisplit.multisplit import MultisplitWidget
from vfwidgets_multisplit.view.container import WidgetProvider


class TestWidgetProvider(WidgetProvider):
    """Test widget provider."""

    def provide_widget(self, widget_id, pane_id):
        """Provide a test widget."""
        widget = QWidget()
        widget.setObjectName(f"test_widget_{widget_id}_{pane_id}")
        return widget


class TestMVPComplete(unittest.TestCase):
    """Test complete MVP functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up QApplication for testing."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up test environment."""
        self.provider = TestWidgetProvider()

    def test_mvp_complete(self):
        """Test complete MVP functionality."""
        # Create widget
        widget = MultisplitWidget(self.provider)

        # Test initialization
        self.assertEqual(len(widget.get_pane_ids()), 1)

        # Test splitting
        pane_id = widget.get_pane_ids()[0]
        self.assertTrue(widget.split_pane(pane_id, "editor:test.py", WherePosition.RIGHT))
        self.assertEqual(len(widget.get_pane_ids()), 2)

        # Test focus
        widget.focus_pane(widget.get_pane_ids()[0])
        self.assertEqual(widget.get_focused_pane(), widget.get_pane_ids()[0])

        # Test navigation
        widget.navigate_focus(Direction.RIGHT)
        self.assertEqual(widget.get_focused_pane(), widget.get_pane_ids()[1])

        # Test undo/redo (undo the split operation)
        self.assertTrue(widget.can_undo())
        undo_success = widget.undo()
        self.assertTrue(undo_success)
        # After undo, should have 1 pane (the original)
        pane_count = len(widget.get_pane_ids())
        print(f"Pane count after undo: {pane_count}")
        self.assertEqual(pane_count, 1)

        self.assertTrue(widget.can_redo())
        redo_success = widget.redo()
        self.assertTrue(redo_success)
        # After redo, should have 2 panes again
        self.assertEqual(len(widget.get_pane_ids()), 2)

        # Test constraints
        self.assertTrue(widget.set_constraints(widget.get_pane_ids()[0], min_width=100))

        # Test persistence
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            filepath = Path(f.name)
            try:
                self.assertTrue(widget.save_layout(filepath))

                # Clear and reload
                widget.initialize_empty()
                self.assertEqual(len(widget.get_pane_ids()), 1)

                self.assertTrue(widget.load_layout(filepath))
                self.assertEqual(len(widget.get_pane_ids()), 2)
            finally:
                filepath.unlink(missing_ok=True)

        print("✅ MVP COMPLETE - All features working!")

    def test_validation_system(self):
        """Test validation system integration."""
        widget = MultisplitWidget(self.provider)

        # Test invalid ratio
        pane_id = widget.get_pane_ids()[0]

        # Connect to validation signal to catch errors
        validation_errors = []
        widget.validation_failed.connect(validation_errors.append)

        # Attempt invalid split
        result = widget.split_pane(pane_id, "test", WherePosition.RIGHT, 0.01)
        self.assertFalse(result)
        self.assertTrue(len(validation_errors) > 0)

    def test_error_widgets(self):
        """Test error widget functionality."""
        from vfwidgets_multisplit.view.error_widget import ErrorWidget, ValidationOverlay

        # Test error widget
        error_widget = ErrorWidget("Test error message")
        self.assertIsNotNone(error_widget)

        # Test validation overlay
        overlay = ValidationOverlay()
        overlay.show_validation_error("Test validation error", 100)
        self.assertEqual(len(overlay.messages), 1)

    def test_styled_splitter(self):
        """Test styled splitter functionality."""
        from PySide6.QtCore import Qt
        from vfwidgets_multisplit.view.container import StyledSplitter

        splitter = StyledSplitter(Qt.Orientation.Horizontal)
        self.assertEqual(splitter.handleWidth(), 6)
        self.assertFalse(splitter.childrenCollapsible())

    def test_widget_provider_integration(self):
        """Test widget provider integration."""
        widget = MultisplitWidget()

        # Set provider after creation
        widget.set_widget_provider(self.provider)

        # Split to trigger widget creation
        pane_id = widget.get_pane_ids()[0]
        widget.split_pane(pane_id, "test:widget", WherePosition.RIGHT)

        # Should have widgets for both panes
        self.assertEqual(len(widget.get_pane_ids()), 2)

    def test_json_persistence(self):
        """Test JSON persistence functionality."""
        widget = MultisplitWidget(self.provider)

        # Create complex layout
        pane_id = widget.get_pane_ids()[0]
        widget.split_pane(pane_id, "test1", WherePosition.RIGHT)
        new_pane = widget.get_pane_ids()[1]
        widget.split_pane(new_pane, "test2", WherePosition.BOTTOM)

        # Export to JSON
        json_str = widget.get_layout_json()
        self.assertIsInstance(json_str, str)
        self.assertTrue(len(json_str) > 0)

        # Clear and restore
        widget.initialize_empty()
        self.assertEqual(len(widget.get_pane_ids()), 1)

        # Import from JSON
        self.assertTrue(widget.set_layout_json(json_str))
        self.assertEqual(len(widget.get_pane_ids()), 3)


if __name__ == "__main__":
    unittest.main()
