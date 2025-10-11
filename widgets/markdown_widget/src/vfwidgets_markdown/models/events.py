"""Event classes for document change notifications."""

from dataclasses import dataclass


@dataclass
class TextReplaceEvent:
    """Event fired when document text is completely replaced.

    This is an O(n) operation - all views must re-render completely.
    """

    version: int
    """Document version after this change."""

    text: str
    """The new complete text of the document."""


@dataclass
class TextAppendEvent:
    """Event fired when text is appended to the document.

    This is an O(m) operation where m = len(text).
    Views can optimize by only rendering the appended text.
    """

    version: int
    """Document version after this change."""

    text: str
    """The text that was appended."""

    start_position: int
    """Character position where the text was appended."""


@dataclass
class SectionUpdateEvent:
    """Event fired when a specific section is updated.

    This is an O(n) operation but provides context about what changed.
    Views can optimize by only updating the affected section.
    """

    version: int
    """Document version after this change."""

    heading_id: str
    """The ID of the heading whose section was updated."""

    content: str
    """The new content of the section (including the heading)."""
