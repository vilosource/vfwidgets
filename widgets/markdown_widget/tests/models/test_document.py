"""Tests for MarkdownDocument model."""

import pytest

from vfwidgets_markdown.models import (
    MarkdownDocument,
    TextAppendEvent,
    TextReplaceEvent,
)


class TestMarkdownDocumentBasics:
    """Test basic document operations."""

    def test_init_empty(self):
        """Test creating an empty document."""
        doc = MarkdownDocument()
        assert doc.get_text() == ""
        assert doc.get_version() == 0

    def test_init_with_content(self):
        """Test creating a document with initial content."""
        doc = MarkdownDocument("Hello World")
        assert doc.get_text() == "Hello World"
        assert doc.get_version() == 0

    def test_set_text(self):
        """Test setting document text."""
        doc = MarkdownDocument()
        doc.set_text("New text")
        assert doc.get_text() == "New text"
        assert doc.get_version() == 1

    def test_append_text(self):
        """Test appending text."""
        doc = MarkdownDocument("Hello")
        doc.append_text(" World")
        assert doc.get_text() == "Hello World"
        assert doc.get_version() == 1

    def test_version_tracking(self):
        """Test that version increments with each change."""
        doc = MarkdownDocument()
        assert doc.get_version() == 0

        doc.set_text("First")
        assert doc.get_version() == 1

        doc.append_text(" Second")
        assert doc.get_version() == 2

        doc.set_text("Third")
        assert doc.get_version() == 3


class TestMarkdownDocumentObserver:
    """Test observer pattern."""

    def test_add_observer(self):
        """Test adding an observer."""
        doc = MarkdownDocument()
        events = []

        class Observer:
            def on_document_changed(self, event):
                events.append(event)

        observer = Observer()
        doc.add_observer(observer)
        doc.set_text("Test")

        assert len(events) == 1
        assert isinstance(events[0], TextReplaceEvent)

    def test_remove_observer(self):
        """Test removing an observer."""
        doc = MarkdownDocument()
        events = []

        class Observer:
            def on_document_changed(self, event):
                events.append(event)

        observer = Observer()
        doc.add_observer(observer)
        doc.set_text("Test1")
        assert len(events) == 1

        doc.remove_observer(observer)
        doc.set_text("Test2")
        assert len(events) == 1  # No new events

    def test_multiple_observers(self):
        """Test multiple observers receive notifications."""
        doc = MarkdownDocument()
        events1 = []
        events2 = []

        class Observer1:
            def on_document_changed(self, event):
                events1.append(event)

        class Observer2:
            def on_document_changed(self, event):
                events2.append(event)

        doc.add_observer(Observer1())
        doc.add_observer(Observer2())
        doc.set_text("Test")

        assert len(events1) == 1
        assert len(events2) == 1

    def test_set_text_event(self):
        """Test that set_text emits TextReplaceEvent."""
        doc = MarkdownDocument()
        events = []

        class Observer:
            def on_document_changed(self, event):
                events.append(event)

        doc.add_observer(Observer())
        doc.set_text("Hello")

        assert len(events) == 1
        assert isinstance(events[0], TextReplaceEvent)
        assert events[0].text == "Hello"
        assert events[0].version == 1

    def test_append_text_event(self):
        """Test that append_text emits TextAppendEvent."""
        doc = MarkdownDocument("Hello")
        events = []

        class Observer:
            def on_document_changed(self, event):
                events.append(event)

        doc.add_observer(Observer())
        doc.append_text(" World")

        assert len(events) == 1
        assert isinstance(events[0], TextAppendEvent)
        assert events[0].text == " World"
        assert events[0].start_position == 5
        assert events[0].version == 1


class TestMarkdownDocumentTOC:
    """Test table of contents parsing."""

    def test_empty_document(self):
        """Test TOC for empty document."""
        doc = MarkdownDocument()
        toc = doc.get_toc()
        assert toc == []

    def test_single_heading(self):
        """Test TOC with single heading."""
        doc = MarkdownDocument("# Title")
        toc = doc.get_toc()

        assert len(toc) == 1
        assert toc[0]["level"] == 1
        assert toc[0]["text"] == "Title"
        assert toc[0]["id"] == "title"

    def test_multiple_headings(self):
        """Test TOC with multiple headings."""
        doc = MarkdownDocument(
            """
# Title
## Section 1
### Subsection
## Section 2
"""
        )
        toc = doc.get_toc()

        assert len(toc) == 4
        assert toc[0]["level"] == 1
        assert toc[0]["text"] == "Title"
        assert toc[1]["level"] == 2
        assert toc[1]["text"] == "Section 1"
        assert toc[2]["level"] == 3
        assert toc[2]["text"] == "Subsection"
        assert toc[3]["level"] == 2
        assert toc[3]["text"] == "Section 2"

    def test_github_id_generation(self):
        """Test GitHub-style ID generation."""
        doc = MarkdownDocument(
            """
# Title With Spaces
## Section-With-Hyphens
### Special!@#$%Characters
"""
        )
        toc = doc.get_toc()

        assert toc[0]["id"] == "title-with-spaces"
        assert toc[1]["id"] == "section-with-hyphens"
        assert toc[2]["id"] == "specialcharacters"

    def test_toc_caching(self):
        """Test that TOC is cached."""
        doc = MarkdownDocument("# Title")

        # First call - parse
        toc1 = doc.get_toc()

        # Second call - should return cached
        toc2 = doc.get_toc()

        # Should be the same object (cached)
        assert toc1 is toc2

    def test_toc_cache_invalidation(self):
        """Test that TOC cache is invalidated on change."""
        doc = MarkdownDocument("# Title 1")
        toc1 = doc.get_toc()

        # Change document
        doc.set_text("# Title 2")
        toc2 = doc.get_toc()

        # Should be different objects (cache invalidated)
        assert toc1 is not toc2
        assert toc2[0]["text"] == "Title 2"


class TestMarkdownDocumentErrors:
    """Test error handling."""

    def test_update_section_empty_id(self):
        """Test that update_section raises ValueError for empty ID."""
        doc = MarkdownDocument()
        with pytest.raises(ValueError, match="heading_id cannot be empty"):
            doc.update_section("", "content")
