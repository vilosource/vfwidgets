"""Protocol definitions for the model layer."""

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from vfwidgets_markdown.models.events import (
        SectionUpdateEvent,
        TextAppendEvent,
        TextReplaceEvent,
    )


class DocumentObserver(Protocol):
    """Protocol for observing document changes.

    Any class implementing this protocol can observe a MarkdownDocument.
    No inheritance required - duck typing via Protocol.
    """

    def on_document_changed(
        self,
        event: "TextReplaceEvent | TextAppendEvent | SectionUpdateEvent",
    ) -> None:
        """Called when the document changes.

        Args:
            event: The change event (TextReplaceEvent, TextAppendEvent, or SectionUpdateEvent)
        """
        ...
