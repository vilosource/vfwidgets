"""Composite markdown editor widget - combines all MVC components.

This is the main user-facing widget that internally creates and wires
together the model, views, and controller. Users don't need to understand
the architecture - just instantiate this widget and use it.
"""

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QSplitter, QWidget

from vfwidgets_markdown.models import MarkdownDocument
from vfwidgets_markdown.widgets.text_editor import MarkdownTextEditor
from vfwidgets_markdown.widgets.toc_view import MarkdownTocView


class MarkdownEditorWidget(QWidget):
    """Complete markdown editor widget with text editing and table of contents.

    This is a composite widget that internally creates and manages:
    - MarkdownDocument (model)
    - MarkdownTextEditor (view)
    - MarkdownTocView (view)

    The architecture is hidden from users - they just get a working
    markdown editor with TOC navigation.

    Example - Basic usage:
        ```python
        editor = MarkdownEditorWidget()
        editor.set_text("# Hello\\n\\nWorld")
        ```

    Example - Access document:
        ```python
        editor = MarkdownEditorWidget()
        doc = editor.get_document()
        doc.append_text("\\n## New section")
        ```

    Example - Signals:
        ```python
        editor = MarkdownEditorWidget()
        editor.content_changed.connect(lambda: print("Content changed!"))
        ```
    """

    # Qt Signals
    content_changed = Signal()  # Emitted when content changes
    cursor_moved = Signal(int, int)  # line, column

    def __init__(self, initial_text: str = "", parent: Optional[QWidget] = None):
        """Initialize the markdown editor widget.

        Args:
            initial_text: Optional initial markdown content
            parent: Optional parent widget
        """
        super().__init__(parent)

        # Create the model (pure Python, no Qt)
        self._document = MarkdownDocument(initial_text)

        # Create views
        self._editor = MarkdownTextEditor(self._document)
        self._toc_view = MarkdownTocView(self._document)

        # Setup UI
        self._setup_ui()

        # Connect signals
        self._connect_signals()

    def _setup_ui(self):
        """Create the UI layout."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)

        # TOC on left (narrower)
        splitter.addWidget(self._toc_view)

        # Editor on right (wider)
        splitter.addWidget(self._editor)

        # Set initial sizes: TOC gets 1 part, editor gets 3 parts
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        layout.addWidget(splitter)

    def _connect_signals(self):
        """Connect internal signals."""
        # TOC heading click → Editor scroll
        self._toc_view.heading_clicked.connect(self._editor.scroll_to_heading)

        # Editor signals → Forward to external users
        self._editor.content_modified.connect(self.content_changed.emit)
        self._editor.cursor_moved.connect(self.cursor_moved.emit)

    # Public API

    def set_text(self, text: str):
        """Set the complete markdown text.

        Args:
            text: The markdown content to display
        """
        self._document.set_text(text)

    def append_text(self, text: str):
        """Append text to the end of the document.

        This is optimized - views will receive an append event
        instead of replacing all content.

        Args:
            text: The text to append
        """
        self._document.append_text(text)

    def get_text(self) -> str:
        """Get the current markdown text.

        Returns:
            The current markdown content
        """
        return self._document.get_text()

    def get_document(self) -> MarkdownDocument:
        """Get direct access to the document model.

        This allows advanced usage like adding custom observers.

        Returns:
            The internal document model
        """
        return self._document

    def get_editor(self) -> MarkdownTextEditor:
        """Get direct access to the text editor widget.

        This allows customization of editor behavior.

        Returns:
            The internal text editor widget
        """
        return self._editor

    def get_toc_view(self) -> MarkdownTocView:
        """Get direct access to the TOC view widget.

        This allows customization of TOC appearance.

        Returns:
            The internal TOC view widget
        """
        return self._toc_view

    def clear(self):
        """Clear all content."""
        self._document.set_text("")

    def set_read_only(self, read_only: bool):
        """Set whether the editor is read-only.

        Args:
            read_only: True to make read-only, False to allow editing
        """
        self._editor.setReadOnly(read_only)

    def is_read_only(self) -> bool:
        """Check if editor is read-only.

        Returns:
            True if read-only, False if editable
        """
        return self._editor.isReadOnly()
