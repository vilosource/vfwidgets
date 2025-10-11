"""Markdown document model - pure Python, no Qt dependencies."""

from typing import Optional

from vfwidgets_markdown.models.events import (
    SectionUpdateEvent,
    TextAppendEvent,
    TextReplaceEvent,
)
from vfwidgets_markdown.models.protocols import DocumentObserver


class MarkdownDocument:
    """The document model - single source of truth for document state.

    This is pure Python with NO Qt dependencies. It can be imported and used
    without a QApplication.

    The model maintains document state and notifies observers of changes via
    the observer pattern.
    """

    def __init__(self, content: str = ""):
        """Initialize the document.

        Args:
            content: Initial document content
        """
        self._content: str = content
        self._version: int = 0
        self._observers: list[DocumentObserver] = []

        # TOC caching
        self._toc_cache: Optional[list[dict]] = None
        self._toc_cache_version: int = -1

    # State access methods

    def get_text(self) -> str:
        """Get the current document text.

        Returns:
            The complete document text
        """
        return self._content

    def get_version(self) -> int:
        """Get the current document version.

        The version increments with each change. Views can use this to
        detect if they're out of sync.

        Returns:
            The current version number
        """
        return self._version

    def get_toc(self) -> list[dict]:
        """Get the table of contents.

        This is cached and only re-parsed when the document changes.

        Returns:
            List of TOC entries, each with keys: 'level', 'text', 'id'
        """
        # Return cached TOC if still valid
        if self._toc_cache_version == self._version:
            return self._toc_cache if self._toc_cache is not None else []

        # Parse TOC and cache it
        self._toc_cache = self._parse_toc()
        self._toc_cache_version = self._version
        return self._toc_cache

    # State mutation methods

    def set_text(self, text: str) -> None:
        """Replace the entire document text.

        This is an O(n) operation. Use append_text() for better performance
        when adding to the end.

        Args:
            text: The new document text
        """
        self._content = text
        self._version += 1
        self._notify_observers(TextReplaceEvent(self._version, text))

    def append_text(self, text: str) -> None:
        """Append text to the end of the document.

        This is O(m) where m = len(text), much better than O(n) for set_text().
        Use this for AI streaming scenarios.

        Args:
            text: The text to append
        """
        start_position = len(self._content)
        self._content += text
        self._version += 1
        self._notify_observers(TextAppendEvent(self._version, text, start_position))

    def update_section(self, heading_id: str, content: str) -> bool:
        """Update a specific section of the document.

        Args:
            heading_id: The ID of the heading (e.g., "my-heading")
            content: The new content for that section (including heading)

        Returns:
            True if section was found and updated, False otherwise
        """
        if not heading_id:
            raise ValueError("heading_id cannot be empty")

        # TODO: Implement section parsing and update
        # This is a Phase 1 stub - will be implemented in Phase 2
        return False

    # Observer pattern methods

    def add_observer(self, observer: DocumentObserver) -> None:
        """Add an observer to be notified of changes.

        Args:
            observer: Object implementing DocumentObserver protocol
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: DocumentObserver) -> None:
        """Remove an observer.

        Args:
            observer: The observer to remove
        """
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify_observers(
        self, event: TextReplaceEvent | TextAppendEvent | SectionUpdateEvent
    ) -> None:
        """Notify all observers of a change.

        Args:
            event: The change event
        """
        for observer in self._observers:
            observer.on_document_changed(event)

    # Internal helper methods

    def _parse_toc(self) -> list[dict]:
        """Parse the table of contents from the document.

        Parses markdown headings (# Title, ## Section, etc.) and generates
        GitHub-style IDs for each heading.

        Returns:
            List of TOC entries with 'level', 'text', and 'id' keys
        """
        import re

        toc = []
        lines = self._content.split("\n")

        for line in lines:
            # Match markdown headings: # Title, ## Section, etc.
            match = re.match(r"^(#{1,6})\s+(.+)$", line.strip())
            if match:
                hashes = match.group(1)
                text = match.group(2).strip()
                level = len(hashes)

                # Generate GitHub-style ID: lowercase, replace spaces with hyphens,
                # remove special characters
                heading_id = text.lower()
                heading_id = re.sub(r"[^\w\s-]", "", heading_id)
                heading_id = re.sub(r"[\s]+", "-", heading_id)

                toc.append(
                    {
                        "level": level,
                        "text": text,
                        "id": heading_id,
                    }
                )

        return toc
