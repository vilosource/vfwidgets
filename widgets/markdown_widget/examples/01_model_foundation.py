#!/usr/bin/env python3
"""
Demo: Model Foundation - Pure Python, No Qt

This demonstrates the MarkdownDocument model working completely independently
of Qt. No QApplication required!

Features demonstrated:
- Creating a document
- Setting and appending text
- Observer pattern
- TOC parsing
- Version tracking
"""

from vfwidgets_markdown.models import (
    MarkdownDocument,
    TextAppendEvent,
    TextReplaceEvent,
)


def demo_basic_operations():
    """Demonstrate basic document operations."""
    print("=" * 60)
    print("DEMO 1: Basic Document Operations")
    print("=" * 60)

    # Create document
    doc = MarkdownDocument("Initial text")
    print(f"Created document: '{doc.get_text()}'")
    print(f"Version: {doc.get_version()}")
    print()

    # Set text
    doc.set_text("Replaced text")
    print(f"After set_text: '{doc.get_text()}'")
    print(f"Version: {doc.get_version()}")
    print()

    # Append text
    doc.append_text(" + appended")
    print(f"After append_text: '{doc.get_text()}'")
    print(f"Version: {doc.get_version()}")
    print()


def demo_observer_pattern():
    """Demonstrate observer pattern."""
    print("=" * 60)
    print("DEMO 2: Observer Pattern")
    print("=" * 60)

    doc = MarkdownDocument()
    events_received = []

    class EventLogger:
        """Simple observer that logs events."""

        def on_document_changed(self, event):
            events_received.append(event)
            if isinstance(event, TextReplaceEvent):
                print(f"  📝 TextReplaceEvent: version={event.version}, text='{event.text}'")
            elif isinstance(event, TextAppendEvent):
                print(
                    f"  ➕ TextAppendEvent: version={event.version}, "
                    f"text='{event.text}', pos={event.start_position}"
                )

    # Add observer
    logger = EventLogger()
    doc.add_observer(logger)
    print("Added observer\n")

    # Trigger events
    print("Performing operations:")
    doc.set_text("Hello")
    doc.append_text(" World")
    doc.set_text("Goodbye")

    print(f"\nTotal events received: {len(events_received)}")
    print()


def demo_multiple_observers():
    """Demonstrate multiple observers."""
    print("=" * 60)
    print("DEMO 3: Multiple Observers")
    print("=" * 60)

    doc = MarkdownDocument()

    class Observer1:
        def on_document_changed(self, event):
            print(f"  Observer1: Got event {event.__class__.__name__}")

    class Observer2:
        def on_document_changed(self, event):
            print(f"  Observer2: Got event {event.__class__.__name__}")

    # Add two observers
    doc.add_observer(Observer1())
    doc.add_observer(Observer2())

    print("Added two observers\n")
    print("Setting text:")
    doc.set_text("Test")
    print("\nBoth observers notified!")
    print()


def demo_toc_parsing():
    """Demonstrate TOC parsing."""
    print("=" * 60)
    print("DEMO 4: Table of Contents Parsing")
    print("=" * 60)

    markdown_content = """
# My Document

This is the introduction.

## Getting Started

Here's how to get started.

### Installation

Install instructions here.

### Configuration

Configuration details.

## Advanced Topics

More advanced stuff.

### Performance Tuning

Optimization tips.

## Conclusion

Final thoughts.
"""

    doc = MarkdownDocument(markdown_content)
    toc = doc.get_toc()

    print(f"Parsed {len(toc)} headings:\n")
    for entry in toc:
        indent = "  " * (entry["level"] - 1)
        print(f"{indent}[{entry['level']}] {entry['text']}")
        print(f"{indent}    ID: {entry['id']}")

    print()


def demo_toc_caching():
    """Demonstrate TOC caching."""
    print("=" * 60)
    print("DEMO 5: TOC Caching")
    print("=" * 60)

    doc = MarkdownDocument("# Title\n## Section")

    print("First call to get_toc():")
    toc1 = doc.get_toc()
    print(f"  Got {len(toc1)} entries")
    print(f"  Object ID: {id(toc1)}")

    print("\nSecond call to get_toc() (should be cached):")
    toc2 = doc.get_toc()
    print(f"  Got {len(toc2)} entries")
    print(f"  Object ID: {id(toc2)}")
    print(f"  Same object? {toc1 is toc2} ✅")

    print("\nChanging document:")
    doc.set_text("# New Title\n## New Section")

    print("Third call to get_toc() (cache invalidated):")
    toc3 = doc.get_toc()
    print(f"  Got {len(toc3)} entries")
    print(f"  Object ID: {id(toc3)}")
    print(f"  Same as first? {toc1 is toc3} (cache was invalidated)")
    print()


def demo_ai_streaming_simulation():
    """Simulate AI streaming with efficient append."""
    print("=" * 60)
    print("DEMO 6: AI Streaming Simulation")
    print("=" * 60)

    doc = MarkdownDocument()
    event_count = []

    class EventCounter:
        def on_document_changed(self, event):
            event_count.append(event)

    doc.add_observer(EventCounter())

    # Simulate AI streaming chunks
    chunks = [
        "# AI Response\n\n",
        "This is a ",
        "demonstration ",
        "of efficient ",
        "text appending.\n\n",
        "Each chunk ",
        "is appended ",
        "in O(m) time, ",
        "not O(n)!\n",
    ]

    print(f"Streaming {len(chunks)} chunks...")
    for i, chunk in enumerate(chunks, 1):
        doc.append_text(chunk)
        print(f"  Chunk {i}: '{chunk.strip()}'")

    print(f"\nFinal document ({len(doc.get_text())} chars):")
    print(doc.get_text())

    print(f"\nTotal events fired: {len(event_count)}")
    print(f"All were TextAppendEvent: {all(isinstance(e, TextAppendEvent) for e in event_count)}")
    print()


def main():
    """Run all demos."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "MARKDOWN WIDGET MODEL FOUNDATION" + " " * 16 + "║")
    print("║" + " " * 18 + "Pure Python Demo" + " " * 22 + "║")
    print("║" + " " * 12 + "(NO Qt - No QApplication!)" + " " * 19 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    demo_basic_operations()
    demo_observer_pattern()
    demo_multiple_observers()
    demo_toc_parsing()
    demo_toc_caching()
    demo_ai_streaming_simulation()

    print("=" * 60)
    print("✅ All demos completed successfully!")
    print("=" * 60)
    print("\nKey Takeaways:")
    print("  • Model is pure Python - no Qt dependencies")
    print("  • Observer pattern enables automatic synchronization")
    print("  • TOC parsing with caching for performance")
    print("  • Efficient append for AI streaming scenarios")
    print("  • Version tracking for change detection")
    print()
    print("Next: See TASK-101 to build Qt views that observe this model!")
    print()


if __name__ == "__main__":
    main()
