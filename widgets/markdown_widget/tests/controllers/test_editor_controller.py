"""Tests for MarkdownEditorController."""

from pytestqt.qtbot import QtBot

from vfwidgets_markdown.controllers.editor_controller import MarkdownEditorController
from vfwidgets_markdown.models import MarkdownDocument
from vfwidgets_markdown.widgets.text_editor import MarkdownTextEditor


class MockViewer:
    """Mock viewer for testing controller behavior."""

    def __init__(self):
        self.update_count = 0
        self.last_text = ""
        self.last_version = -1

    def on_document_changed(self, event):
        """Observer callback."""
        self.update_count += 1
        if hasattr(event, "text"):
            self.last_text = event.text
        if hasattr(event, "version"):
            self.last_version = event.version

    def reset(self):
        """Reset counters for testing."""
        self.update_count = 0
        self.last_text = ""
        self.last_version = -1


class TestEditorControllerPauseResume:
    """Test pause/resume rendering functionality."""

    def test_pause_prevents_viewer_updates(self, qtbot: QtBot):
        """Test that pausing prevents viewer from receiving updates."""
        document = MarkdownDocument()
        editor = MarkdownTextEditor(document)
        qtbot.addWidget(editor)

        viewer = MockViewer()
        document.add_observer(viewer)

        controller = MarkdownEditorController(document, editor, viewer)

        # Pause rendering
        controller.pause_rendering()
        assert controller.is_rendering_paused()

        # Make changes
        document.set_text("Change 1")
        document.set_text("Change 2")
        document.set_text("Change 3")

        # Viewer should not have been updated
        assert viewer.update_count == 0

    def test_resume_triggers_single_update(self, qtbot: QtBot):
        """Test that resuming triggers exactly one update with final state."""
        document = MarkdownDocument()
        editor = MarkdownTextEditor(document)
        qtbot.addWidget(editor)

        viewer = MockViewer()
        document.add_observer(viewer)

        controller = MarkdownEditorController(document, editor, viewer)

        # Pause and make changes
        controller.pause_rendering()
        document.set_text("Change 1")
        document.set_text("Change 2")
        document.set_text("Final change")

        # Resume
        controller.resume_rendering()
        assert not controller.is_rendering_paused()

        # Should have exactly one update with final state
        assert viewer.update_count == 1
        assert "Final change" in viewer.last_text

    def test_resume_without_pending_update(self, qtbot: QtBot):
        """Test that resuming without changes doesn't trigger update."""
        document = MarkdownDocument()
        editor = MarkdownTextEditor(document)
        qtbot.addWidget(editor)

        viewer = MockViewer()
        document.add_observer(viewer)

        controller = MarkdownEditorController(document, editor, viewer)

        # Pause and resume without changes
        controller.pause_rendering()
        controller.resume_rendering()

        # No updates should have occurred
        assert viewer.update_count == 0

    def test_multiple_pause_resume_cycles(self, qtbot: QtBot):
        """Test multiple pause/resume cycles work correctly."""
        document = MarkdownDocument()
        editor = MarkdownTextEditor(document)
        qtbot.addWidget(editor)

        viewer = MockViewer()
        document.add_observer(viewer)

        controller = MarkdownEditorController(document, editor, viewer)

        # Cycle 1
        controller.pause_rendering()
        document.set_text("First")
        controller.resume_rendering()
        assert viewer.update_count == 1

        # Cycle 2
        viewer.reset()
        controller.pause_rendering()
        document.set_text("Second")
        controller.resume_rendering()
        assert viewer.update_count == 1
        assert "Second" in viewer.last_text


class TestEditorControllerThrottling:
    """Test throttling/debouncing functionality."""

    def test_throttle_mode_can_be_enabled(self, qtbot: QtBot):
        """Test that throttle mode can be enabled and configured."""
        document = MarkdownDocument()
        editor = MarkdownTextEditor(document)
        qtbot.addWidget(editor)

        viewer = MockViewer()
        document.add_observer(viewer)

        controller = MarkdownEditorController(document, editor, viewer)

        # Enable throttling
        controller.set_throttle_mode(True, 500)

        assert controller.is_throttle_enabled()
        assert controller.get_throttle_interval() == 500

    def test_throttle_mode_can_be_disabled(self, qtbot: QtBot):
        """Test that throttle mode can be disabled."""
        document = MarkdownDocument()
        editor = MarkdownTextEditor(document)
        qtbot.addWidget(editor)

        viewer = MockViewer()
        document.add_observer(viewer)

        controller = MarkdownEditorController(document, editor, viewer)

        # Enable then disable
        controller.set_throttle_mode(True, 300)
        controller.set_throttle_mode(False)

        assert not controller.is_throttle_enabled()

    def test_throttle_debounces_updates(self, qtbot: QtBot):
        """Test that throttling debounces multiple rapid updates."""
        document = MarkdownDocument()
        editor = MarkdownTextEditor(document)
        qtbot.addWidget(editor)

        viewer = MockViewer()
        document.add_observer(viewer)

        controller = MarkdownEditorController(document, editor, viewer)

        # Enable throttling with 100ms interval
        controller.set_throttle_mode(True, 100)

        # Make rapid changes
        document.set_text("Change 1")
        document.set_text("Change 2")
        document.set_text("Change 3")

        # Should not have updated yet
        assert viewer.update_count == 0

        # Wait for throttle timer to expire
        qtbot.wait(150)

        # Should now have exactly one update
        assert viewer.update_count == 1
        assert "Change 3" in viewer.last_text

    def test_throttle_respects_pause(self, qtbot: QtBot):
        """Test that throttling doesn't update while paused."""
        document = MarkdownDocument()
        editor = MarkdownTextEditor(document)
        qtbot.addWidget(editor)

        viewer = MockViewer()
        document.add_observer(viewer)

        controller = MarkdownEditorController(document, editor, viewer)

        # Enable throttling and pause
        controller.set_throttle_mode(True, 100)
        controller.pause_rendering()

        # Make changes
        document.set_text("Test")

        # Wait for throttle timer
        qtbot.wait(150)

        # Should not have updated (paused)
        assert viewer.update_count == 0

        # Resume
        controller.resume_rendering()

        # Should now update
        assert viewer.update_count == 1


class TestEditorControllerIntegration:
    """Integration tests for controller with real components."""

    def test_controller_integrates_with_editor(self, qtbot: QtBot):
        """Test that controller works with real editor widget."""
        document = MarkdownDocument("Initial text")
        editor = MarkdownTextEditor(document)
        qtbot.addWidget(editor)

        viewer = MockViewer()
        document.add_observer(viewer)

        controller = MarkdownEditorController(document, editor, viewer)

        # Editor should show initial text
        assert editor.toPlainText() == "Initial text"

        # Pause, modify, resume
        controller.pause_rendering()
        document.set_text("Updated text")
        controller.resume_rendering()

        # Editor should show updated text (via its own observer)
        assert editor.toPlainText() == "Updated text"
        # Viewer should have been updated via controller
        assert viewer.update_count == 1

    def test_controller_removes_viewer_from_direct_observation(self, qtbot: QtBot):
        """Test that controller intercepts viewer updates."""
        document = MarkdownDocument()
        editor = MarkdownTextEditor(document)
        qtbot.addWidget(editor)

        viewer = MockViewer()
        document.add_observer(viewer)

        # Verify viewer is observing before controller
        assert viewer in document._observers

        controller = MarkdownEditorController(document, editor, viewer)

        # Controller should have removed viewer and added itself
        assert viewer not in document._observers
        assert controller in document._observers

    def test_normal_operation_without_pause_or_throttle(self, qtbot: QtBot):
        """Test that updates work normally without pause or throttle."""
        document = MarkdownDocument()
        editor = MarkdownTextEditor(document)
        qtbot.addWidget(editor)

        viewer = MockViewer()
        document.add_observer(viewer)

        # Note: controller is created but we're testing direct document updates
        MarkdownEditorController(document, editor, viewer)

        # Make changes without pause or throttle
        document.set_text("Test 1")
        assert viewer.update_count == 1

        document.set_text("Test 2")
        assert viewer.update_count == 2

        document.set_text("Test 3")
        assert viewer.update_count == 3
