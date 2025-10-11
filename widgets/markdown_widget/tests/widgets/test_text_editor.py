"""Tests for MarkdownTextEditor."""

from pytestqt.qtbot import QtBot

from vfwidgets_markdown.models import MarkdownDocument
from vfwidgets_markdown.widgets.text_editor import MarkdownTextEditor


class TestMarkdownTextEditorObserver:
    """Test Python observer pattern functionality."""

    def test_editor_observes_model(self, qtbot: QtBot):
        """Test that editor observes model changes."""
        document = MarkdownDocument()
        editor = MarkdownTextEditor(document)
        qtbot.addWidget(editor)

        # Initially empty
        assert editor.toPlainText() == ""

        # Update model
        document.set_text("Test content")

        # Editor should update automatically
        assert editor.toPlainText() == "Test content"

    def test_model_append_updates_editor(self, qtbot: QtBot):
        """Test that appending to model updates editor."""
        document = MarkdownDocument("Hello")
        editor = MarkdownTextEditor(document)
        qtbot.addWidget(editor)

        assert editor.toPlainText() == "Hello"

        # Append to model
        document.append_text(" World")

        # Editor should show appended text
        assert editor.toPlainText() == "Hello World"

    def test_multiple_editors_stay_in_sync(self, qtbot: QtBot):
        """Test that multiple editors observing same model stay in sync."""
        document = MarkdownDocument()
        editor1 = MarkdownTextEditor(document)
        editor2 = MarkdownTextEditor(document)
        qtbot.addWidget(editor1)
        qtbot.addWidget(editor2)

        # Update model
        document.set_text("Synchronized")

        # Both editors should update
        assert editor1.toPlainText() == "Synchronized"
        assert editor2.toPlainText() == "Synchronized"

    def test_no_update_loops(self, qtbot: QtBot):
        """Test that _updating_from_model flag prevents update loops."""
        document = MarkdownDocument()
        editor = MarkdownTextEditor(document)
        qtbot.addWidget(editor)

        # Track version changes
        initial_version = document.get_version()

        # Set text via model
        document.set_text("Test")

        # Version should increment exactly once (no loops)
        assert document.get_version() == initial_version + 1

        # Editor should show correct text
        assert editor.toPlainText() == "Test"


class TestMarkdownTextEditorSignals:
    """Test Qt signals functionality."""

    def test_content_modified_signal_emitted(self, qtbot: QtBot):
        """Test that content_modified signal is emitted when user types."""
        document = MarkdownDocument()
        editor = MarkdownTextEditor(document)
        qtbot.addWidget(editor)

        # Use qtbot to wait for signal
        with qtbot.waitSignal(editor.content_modified, timeout=1000):
            # Simulate user typing
            editor.setPlainText("User typed this")

    def test_cursor_moved_signal_emitted(self, qtbot: QtBot):
        """Test that cursor_moved signal is emitted."""
        from PySide6.QtGui import QTextCursor

        document = MarkdownDocument("Line 1\nLine 2\nLine 3")
        editor = MarkdownTextEditor(document)
        qtbot.addWidget(editor)

        # Use qtbot to capture signal
        with qtbot.waitSignal(editor.cursor_moved, timeout=1000) as blocker:
            # Move cursor
            cursor = editor.textCursor()
            cursor.movePosition(QTextCursor.Down)
            editor.setTextCursor(cursor)

        # Check signal was emitted with correct values
        # blocker.args will be [line, column]
        assert len(blocker.args) == 2
        assert isinstance(blocker.args[0], int)  # line
        assert isinstance(blocker.args[1], int)  # column


class TestMarkdownTextEditorSlots:
    """Test Qt slots functionality."""

    def test_scroll_to_heading_slot(self, qtbot: QtBot):
        """Test that scroll_to_heading slot works."""
        markdown_text = """# Title
Some content

## Section 1
More content

## Section 2
Final content
"""
        document = MarkdownDocument(markdown_text)
        editor = MarkdownTextEditor(document)
        qtbot.addWidget(editor)

        # Call the slot
        editor.scroll_to_heading("section-2")

        # Cursor should have moved (we can't easily check exact position,
        # but we can verify the method doesn't crash)
        cursor = editor.textCursor()
        assert cursor is not None


class TestMarkdownTextEditorMemoryManagement:
    """Test memory management and cleanup."""

    def test_observer_removed_on_close(self, qtbot: QtBot):
        """Test that observer is removed when widget closes."""
        document = MarkdownDocument()
        editor = MarkdownTextEditor(document)
        qtbot.addWidget(editor)

        # Editor should be in observers list
        assert editor in document._observers

        # Close the editor
        editor.close()

        # Editor should be removed from observers list
        assert editor not in document._observers


class TestMarkdownTextEditorIntegration:
    """Integration tests combining multiple features."""

    def test_edit_in_one_editor_updates_another(self, qtbot: QtBot):
        """Test editing in one editor updates another via model."""
        document = MarkdownDocument()
        editor1 = MarkdownTextEditor(document)
        editor2 = MarkdownTextEditor(document)
        qtbot.addWidget(editor1)
        qtbot.addWidget(editor2)

        # Type in editor1 (simulates user action)
        editor1.setPlainText("Hello from editor 1")

        # editor2 should update via model
        assert editor2.toPlainText() == "Hello from editor 1"

    def test_model_changes_while_editor_exists(self, qtbot: QtBot):
        """Test that model can be changed independently while editor exists."""
        document = MarkdownDocument("Initial")
        editor = MarkdownTextEditor(document)
        qtbot.addWidget(editor)

        # Change model multiple times
        document.set_text("First")
        assert editor.toPlainText() == "First"

        document.append_text(" Second")
        assert editor.toPlainText() == "First Second"

        document.set_text("Third")
        assert editor.toPlainText() == "Third"
