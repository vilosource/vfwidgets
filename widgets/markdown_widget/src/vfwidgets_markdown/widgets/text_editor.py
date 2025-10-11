"""Markdown text editor that observes the document model."""

import re
from typing import Optional

from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QPlainTextEdit, QWidget

from vfwidgets_markdown.models import (
    MarkdownDocument,
    TextAppendEvent,
    TextReplaceEvent,
)


class MarkdownTextEditor(QPlainTextEdit):
    """Text editor that observes a MarkdownDocument model.

    This widget uses an auto-wrapping pattern:
    - If no document is provided, creates an internal document (simple mode)
    - If document is provided, uses external document (architecture mode)

    This widget demonstrates the dual pattern approach:
    - Uses Python observer pattern to react to model changes
    - Uses Qt signals/slots for UI coordination with other views
    """

    # Qt Signals for UI coordination (view-to-view communication)
    content_modified = Signal()  # Emitted when user edits content
    cursor_moved = Signal(int, int)  # line, column

    def __init__(
        self, document: Optional[MarkdownDocument] = None, parent: Optional[QWidget] = None
    ):
        """Initialize the editor.

        The editor uses an auto-wrapping pattern:
        - If no document is provided, creates an internal document (simple mode)
        - If document is provided, uses external document (architecture mode)

        Args:
            document: Optional document model to observe. If None, creates internal document.
            parent: Optional parent widget
        """
        super().__init__(parent)

        # Auto-wrapping: Always use a document (internal or external)
        if document:
            # Advanced mode - use external document
            self._document = document
            self._owns_document = False
        else:
            # Simple mode - create internal document
            self._document = MarkdownDocument()
            self._owns_document = True

        self._updating_from_model = False

        # Add this view as an observer (Python observer pattern)
        self._document.add_observer(self)

        # Set initial content from model
        self.setPlainText(self._document.get_text())

        # Connect Qt's built-in signals to our slots
        self.textChanged.connect(self._on_qt_text_changed)
        self.cursorPositionChanged.connect(self._on_cursor_position_changed)

    def on_document_changed(self, event):
        """Observer callback - called when model changes.

        This is a Python observer method, NOT a Qt slot.
        It's called directly by the model's _notify_observers().

        Args:
            event: TextReplaceEvent, TextAppendEvent, or SectionUpdateEvent
        """
        # Prevent update loops
        self._updating_from_model = True
        try:
            if isinstance(event, TextReplaceEvent):
                # Full text replacement - O(n) operation
                # Save cursor position to restore after setText
                cursor = self.textCursor()
                cursor_position = cursor.position()

                self.setPlainText(event.text)

                # Restore cursor position (if still valid)
                if cursor_position <= len(event.text):
                    cursor = self.textCursor()
                    cursor.setPosition(cursor_position)
                    self.setTextCursor(cursor)
            elif isinstance(event, TextAppendEvent):
                # Efficient append - O(m) where m = len(text)
                cursor = self.textCursor()
                cursor.movePosition(QTextCursor.End)
                cursor.insertText(event.text)
        finally:
            # Always clear flag, even if exception occurs
            self._updating_from_model = False

    @Slot()
    def _on_qt_text_changed(self):
        """Qt slot - responds to textChanged signal.

        This is called when the user types or when we programmatically
        change the text. We use the _updating_from_model flag to
        distinguish between the two cases.
        """
        if not self._updating_from_model:
            # User edited - update model directly (Pragmatic MVC)
            self._document.set_text(self.toPlainText())
            # Emit our custom Qt signal for other views
            self.content_modified.emit()

    @Slot()
    def _on_cursor_position_changed(self):
        """Qt slot - responds to cursor position changes."""
        cursor = self.textCursor()
        line = cursor.blockNumber()
        column = cursor.columnNumber()
        self.cursor_moved.emit(line, column)

    @Slot(str)
    def scroll_to_heading(self, heading_id: str):
        """Qt slot - scroll to show a heading.

        This can be connected to TOC's heading_clicked signal for
        view-to-view coordination.

        Args:
            heading_id: The heading ID to scroll to (e.g., "my-heading")
        """
        text = self.toPlainText()
        lines = text.split("\n")

        # Search for the heading
        for line_num, line in enumerate(lines):
            # Check if this line is a heading
            match = re.match(r"^(#{1,6})\s+(.+)$", line.strip())
            if match:
                heading_text = match.group(2).strip()
                # Generate GitHub-style ID
                check_id = heading_text.lower()
                check_id = re.sub(r"[^\w\s-]", "", check_id)
                check_id = re.sub(r"[\s]+", "-", check_id)

                if check_id == heading_id:
                    # Found it! Scroll to this line
                    cursor = self.textCursor()
                    cursor.movePosition(QTextCursor.Start)
                    for _ in range(line_num):
                        cursor.movePosition(QTextCursor.Down)
                    self.setTextCursor(cursor)
                    self.centerCursor()
                    break

    def set_text(self, text: str) -> None:
        """Set the complete text content.

        Convenience method that works in both simple and advanced modes.

        Args:
            text: The new text content
        """
        self._document.set_text(text)

    def get_text(self) -> str:
        """Get the current text content.

        Convenience method that works in both simple and advanced modes.

        Returns:
            The complete text content
        """
        return self._document.get_text()

    def append_text(self, text: str) -> None:
        """Append text to the end of the document.

        Efficient for streaming/incremental updates.

        Args:
            text: The text to append
        """
        self._document.append_text(text)

    def get_document(self) -> MarkdownDocument:
        """Get the underlying document model (for advanced usage).

        Returns:
            The MarkdownDocument instance
        """
        return self._document

    def closeEvent(self, event):
        """Handle widget closing - remove observer to prevent memory leaks."""
        self._document.remove_observer(self)
        super().closeEvent(event)
