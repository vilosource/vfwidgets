"""Model layer - Pure Python document model with observer pattern."""

from vfwidgets_markdown.models.document import MarkdownDocument
from vfwidgets_markdown.models.events import (
    SectionUpdateEvent,
    TextAppendEvent,
    TextReplaceEvent,
)
from vfwidgets_markdown.models.protocols import DocumentObserver

__all__ = [
    "DocumentObserver",
    "TextReplaceEvent",
    "TextAppendEvent",
    "SectionUpdateEvent",
    "MarkdownDocument",
]
