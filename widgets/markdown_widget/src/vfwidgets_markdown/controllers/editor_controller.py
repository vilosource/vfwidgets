"""Editor controller for coordinating model and view interactions.

This controller provides:
- Pause/resume rendering for bulk operations
- Throttling/debouncing for performance
- Coordination between editor, model, and viewer
"""

from typing import Any

from PySide6.QtCore import QObject, QTimer

from vfwidgets_markdown.models import MarkdownDocument


class MarkdownEditorController(QObject):
    """Controller that coordinates markdown editor, document, and viewer.

    This controller implements performance optimizations:
    - Pause/resume rendering during bulk text operations
    - Throttle/debounce viewer updates to prevent lag during typing
    - Manage observer relationships

    Example:
        ```python
        controller = MarkdownEditorController(document, editor, viewer)

        # Pause rendering for bulk operation
        controller.pause_rendering()
        for line in large_file:
            document.append_text(line)
        controller.resume_rendering()

        # Enable throttling (300ms debounce)
        controller.set_throttle_mode(True, 300)
        ```
    """

    def __init__(
        self,
        document: MarkdownDocument,
        editor: Any,  # MarkdownTextEditor (avoid circular import)
        viewer: Any,  # Any viewer with on_document_changed method
    ):
        """Initialize the controller.

        Args:
            document: The markdown document model
            editor: The text editor widget
            viewer: The viewer widget (e.g., HTML renderer)
        """
        super().__init__()
        self._document = document
        self._editor = editor
        self._viewer = viewer

        # Rendering state
        self._rendering_paused = False
        self._pending_update = False

        # Throttle state
        self._throttle_enabled = False
        self._throttle_timer = QTimer(self)
        self._throttle_timer.setSingleShot(True)
        self._throttle_timer.timeout.connect(self._on_throttle_timeout)
        self._throttle_interval_ms = 300

        # Replace viewer's observer with our throttled version
        self._original_viewer_callback = None
        if hasattr(viewer, "on_document_changed"):
            self._original_viewer_callback = viewer.on_document_changed
            # Remove viewer from direct observation
            if viewer in document._observers:
                document.remove_observer(viewer)
            # Add controller as observer instead
            document.add_observer(self)

    def on_document_changed(self, event):
        """Observer callback - called when document changes.

        This intercepts document changes and applies throttling/pause logic
        before forwarding to the viewer.

        Args:
            event: The document change event
        """
        if self._rendering_paused:
            # Mark that we need to update when resumed
            self._pending_update = True
            return

        if self._throttle_enabled:
            # Restart throttle timer
            self._throttle_timer.stop()
            self._throttle_timer.start(self._throttle_interval_ms)
        else:
            # Immediate update
            if self._original_viewer_callback:
                self._original_viewer_callback(event)

    def _on_throttle_timeout(self):
        """Called when throttle timer expires - perform the deferred update."""
        if self._original_viewer_callback and not self._rendering_paused:
            # Trigger a full refresh by getting current text
            from vfwidgets_markdown.models import TextReplaceEvent

            event = TextReplaceEvent(
                version=self._document.get_version(), text=self._document.get_text()
            )
            self._original_viewer_callback(event)

    def pause_rendering(self):
        """Pause viewer rendering during bulk operations.

        While paused, the viewer will not be notified of document changes.
        Call resume_rendering() to trigger a single update with the final state.

        Example:
            ```python
            controller.pause_rendering()
            for i in range(1000):
                document.append_text(f"Line {i}\\n")
            controller.resume_rendering()  # Single update with final result
            ```
        """
        self._rendering_paused = True
        self._pending_update = False

    def resume_rendering(self):
        """Resume viewer rendering and trigger update if needed.

        If any changes occurred while paused, triggers a single update
        with the current document state.
        """
        self._rendering_paused = False

        if self._pending_update:
            self._pending_update = False
            # Trigger full refresh
            if self._original_viewer_callback:
                from vfwidgets_markdown.models import TextReplaceEvent

                event = TextReplaceEvent(
                    version=self._document.get_version(), text=self._document.get_text()
                )
                self._original_viewer_callback(event)

    def set_throttle_mode(self, enabled: bool, interval_ms: int = 300):
        """Enable or disable throttled rendering.

        When enabled, viewer updates are debounced - multiple rapid changes
        will result in a single viewer update after the interval expires.

        Args:
            enabled: True to enable throttling, False to disable
            interval_ms: Debounce interval in milliseconds (default: 300)

        Example:
            ```python
            # Enable 500ms debounce for typing performance
            controller.set_throttle_mode(True, 500)

            # User types quickly - viewer updates only after 500ms pause

            # Disable for immediate updates
            controller.set_throttle_mode(False)
            ```
        """
        self._throttle_enabled = enabled
        self._throttle_interval_ms = interval_ms

        if not enabled:
            # Stop any pending throttle
            self._throttle_timer.stop()

    def is_rendering_paused(self) -> bool:
        """Check if rendering is currently paused.

        Returns:
            True if rendering is paused, False otherwise
        """
        return self._rendering_paused

    def is_throttle_enabled(self) -> bool:
        """Check if throttle mode is enabled.

        Returns:
            True if throttling is enabled, False otherwise
        """
        return self._throttle_enabled

    def get_throttle_interval(self) -> int:
        """Get the current throttle interval.

        Returns:
            Throttle interval in milliseconds
        """
        return self._throttle_interval_ms
