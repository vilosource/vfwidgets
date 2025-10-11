"""VFWidgets Markdown Widget - MVC Architecture.

A professional markdown editor widget with proper Model-View-Controller architecture.
"""

from vfwidgets_markdown.models import (
    DocumentObserver,
    MarkdownDocument,
    SectionUpdateEvent,
    TextAppendEvent,
    TextReplaceEvent,
)
from vfwidgets_markdown.widgets import (
    MarkdownEditorWidget,
    MarkdownTextEditor,
    MarkdownTocView,
    MarkdownViewer,
)

__version__ = "2.0.0"

__all__ = [
    # Model
    "MarkdownDocument",
    "DocumentObserver",
    "TextReplaceEvent",
    "TextAppendEvent",
    "SectionUpdateEvent",
    # Widgets
    "MarkdownTextEditor",
    "MarkdownTocView",
    "MarkdownEditorWidget",
    "MarkdownViewer",
]
