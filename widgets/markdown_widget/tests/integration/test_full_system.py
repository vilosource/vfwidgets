"""Integration tests for the full markdown widget system."""

from pytestqt.qtbot import QtBot

from vfwidgets_markdown import (
    MarkdownDocument,
    MarkdownEditorWidget,
    MarkdownTextEditor,
    MarkdownTocView,
    MarkdownViewer,
)


class TestMarkdownViewerIntegration:
    """Test MarkdownViewer in both simple and advanced modes."""

    def test_viewer_simple_mode(self, qtbot: QtBot):
        """Test viewer in simple mode (internal document)."""
        viewer = MarkdownViewer()
        qtbot.addWidget(viewer)

        # Should have internal document
        assert viewer._owns_document is True
        assert viewer._document is not None

        # Set markdown should work
        viewer.set_markdown("# Test")
        assert viewer._document.get_text() == "# Test"

    def test_viewer_advanced_mode(self, qtbot: QtBot):
        """Test viewer in advanced mode (external document)."""
        document = MarkdownDocument("# Initial")
        viewer = MarkdownViewer(document=document)
        qtbot.addWidget(viewer)

        # Should use external document
        assert viewer._owns_document is False
        assert viewer._document is document

        # Document changes should update viewer
        document.set_text("# Updated")
        assert viewer._document.get_text() == "# Updated"

    def test_multiple_viewers_shared_document(self, qtbot: QtBot):
        """Test multiple viewers observing same document."""
        document = MarkdownDocument("# Shared")
        viewer1 = MarkdownViewer(document=document)
        viewer2 = MarkdownViewer(document=document)
        qtbot.addWidget(viewer1)
        qtbot.addWidget(viewer2)

        # Both should observe same document
        assert viewer1._document is viewer2._document
        assert len(document._observers) == 2

        # Update via document
        document.set_text("# Changed")
        assert viewer1._document.get_text() == "# Changed"
        assert viewer2._document.get_text() == "# Changed"


class TestEditorViewerIntegration:
    """Test editor and viewer working together."""

    def test_editor_and_viewer_synchronization(self, qtbot: QtBot):
        """Test editor and viewer stay synchronized via shared document."""
        document = MarkdownDocument("# Start")
        editor = MarkdownTextEditor(document)
        viewer = MarkdownViewer(document=document)
        qtbot.addWidget(editor)
        qtbot.addWidget(viewer)

        # Both should show same content
        assert editor.toPlainText() == "# Start"
        assert viewer._document.get_text() == "# Start"

        # Edit in editor
        editor.setPlainText("# Modified")

        # Viewer should update (via document observer)
        assert viewer._document.get_text() == "# Modified"

    def test_editor_viewer_and_toc_synchronization(self, qtbot: QtBot):
        """Test editor, viewer, and TOC all synchronized."""
        content = "# Title\n\n## Section 1\n\n## Section 2"
        document = MarkdownDocument(content)

        editor = MarkdownTextEditor(document)
        viewer = MarkdownViewer(document=document)
        toc = MarkdownTocView(document)

        qtbot.addWidget(editor)
        qtbot.addWidget(viewer)
        qtbot.addWidget(toc)

        # All should have same document
        assert editor._document is document
        assert viewer._document is document
        assert toc._document is document

        # TOC should show 3 headings
        toc_entries = document.get_toc()
        assert len(toc_entries) == 3

        # Modify document
        new_content = "# New Title\n\n## New Section"
        document.set_text(new_content)

        # All views should update
        assert editor.toPlainText() == new_content
        assert viewer._document.get_text() == new_content
        new_toc = document.get_toc()
        assert len(new_toc) == 2


class TestCompositeWidgetIntegration:
    """Test the MarkdownEditorWidget composite."""

    def test_composite_widget_creation(self, qtbot: QtBot):
        """Test composite widget creates all components."""
        widget = MarkdownEditorWidget()
        qtbot.addWidget(widget)

        # Should have all components
        assert widget._document is not None
        assert widget._editor is not None
        assert widget._toc_view is not None

        # Components should share document
        assert widget._editor._document is widget._document
        assert widget._toc_view._document is widget._document

    def test_composite_widget_api(self, qtbot: QtBot):
        """Test composite widget public API."""
        widget = MarkdownEditorWidget("# Initial")
        qtbot.addWidget(widget)

        # Test get_text
        assert widget.get_text() == "# Initial"

        # Test set_text
        widget.set_text("# Changed")
        assert widget.get_text() == "# Changed"
        assert widget._editor.toPlainText() == "# Changed"

        # Test append_text
        widget.append_text("\n\n## Section")
        text = widget.get_text()
        assert "# Changed" in text
        assert "## Section" in text

        # Test clear
        widget.clear()
        assert widget.get_text() == ""

    def test_composite_widget_signals(self, qtbot: QtBot):
        """Test composite widget emits signals."""
        widget = MarkdownEditorWidget("# Title\n\nParagraph")
        qtbot.addWidget(widget)

        # Test content_changed signal - use editor's signal directly
        with qtbot.waitSignal(widget.content_changed, timeout=1000):
            # Trigger by editing in the editor
            editor = widget.get_editor()
            editor.setPlainText("# Test")

        # Test cursor_moved signal
        # Setting text resets cursor to start (0,0), so moving to end should emit signal
        with qtbot.waitSignal(widget.cursor_moved, timeout=1000):
            editor = widget.get_editor()
            cursor = editor.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            editor.setTextCursor(cursor)

    def test_composite_widget_read_only(self, qtbot: QtBot):
        """Test composite widget read-only mode."""
        widget = MarkdownEditorWidget("# Test")
        qtbot.addWidget(widget)

        # Initially editable
        assert not widget.is_read_only()

        # Make read-only
        widget.set_read_only(True)
        assert widget.is_read_only()
        assert widget._editor.isReadOnly()

        # Make editable again
        widget.set_read_only(False)
        assert not widget.is_read_only()
        assert not widget._editor.isReadOnly()


class TestControllerIntegration:
    """Test controller integration with views."""

    def test_controller_with_viewer(self, qtbot: QtBot):
        """Test controller managing viewer updates."""
        from vfwidgets_markdown.controllers import MarkdownEditorController

        document = MarkdownDocument()
        editor = MarkdownTextEditor(document)
        viewer = MarkdownViewer(document=document)
        qtbot.addWidget(editor)
        qtbot.addWidget(viewer)

        # Create controller
        controller = MarkdownEditorController(document, editor, viewer)

        # Pause rendering
        controller.pause_rendering()

        # Make changes
        document.set_text("Change 1")
        document.set_text("Change 2")
        document.set_text("Final")

        # Viewer should update via controller
        controller.resume_rendering()

        # Check final state
        assert viewer._document.get_text() == "Final"


class TestMemoryManagement:
    """Test memory management and cleanup."""

    def test_observer_cleanup_on_close(self, qtbot: QtBot):
        """Test observers are cleaned up when widgets close."""
        document = MarkdownDocument()
        editor = MarkdownTextEditor(document)
        viewer = MarkdownViewer(document=document)
        toc = MarkdownTocView(document)

        qtbot.addWidget(editor)
        qtbot.addWidget(viewer)
        qtbot.addWidget(toc)

        # All should be observers
        assert len(document._observers) == 3

        # Close editor
        editor.close()
        assert len(document._observers) == 2

        # Close viewer
        viewer.close()
        assert len(document._observers) == 1

        # Close TOC
        toc.close()
        assert len(document._observers) == 0


class TestAIStreamingScenario:
    """Test AI streaming use case."""

    def test_efficient_streaming_with_append(self, qtbot: QtBot):
        """Test efficient streaming using append_text."""
        document = MarkdownDocument()
        editor = MarkdownTextEditor(document)
        viewer = MarkdownViewer(document=document)

        qtbot.addWidget(editor)
        qtbot.addWidget(viewer)

        # Simulate AI streaming
        chunks = ["# AI", " Response", "\n\n", "This is", " a", " streaming", " response."]

        for chunk in chunks:
            document.append_text(chunk)

        # Final text should be complete
        expected = "# AI Response\n\nThis is a streaming response."
        assert document.get_text() == expected
        assert editor.toPlainText() == expected
        assert viewer._document.get_text() == expected

    def test_streaming_with_controller_throttling(self, qtbot: QtBot):
        """Test streaming with controller throttling."""
        from vfwidgets_markdown.controllers import MarkdownEditorController

        document = MarkdownDocument()
        editor = MarkdownTextEditor(document)
        viewer = MarkdownViewer(document=document)

        qtbot.addWidget(editor)
        qtbot.addWidget(viewer)

        controller = MarkdownEditorController(document, editor, viewer)
        controller.set_throttle_mode(True, 100)

        # Stream rapidly
        for i in range(10):
            document.append_text(f"Chunk {i} ")

        # Wait for throttle
        qtbot.wait(150)

        # Should have final result
        text = document.get_text()
        assert "Chunk 9" in text
