"""Example 03: Bookmark Management

This example demonstrates the bookmark system in detail.

Educational Focus:
    - BookmarkManager API
    - JSON storage
    - Bookmark operations (add, remove, search)
    - Import/export functionality

Run:
    python examples/03_bookmark_management.py
"""

import sys
from pathlib import Path
from tempfile import TemporaryDirectory

# Add parent directory to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from viloweb import BookmarkManager


def print_section(title: str) -> None:
    """Print section header."""
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)
    print()


def demo_basic_operations():
    """Demonstrate basic bookmark operations."""
    print_section("Basic Bookmark Operations")

    # Create manager with temporary storage
    with TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir)
        manager = BookmarkManager(storage_path)

        print("1. Adding bookmarks:")
        print("-" * 40)

        bookmarks_to_add = [
            ("VFWidgets", "https://github.com/viloforge/vfwidgets"),
            ("Python", "https://python.org"),
            ("Qt Documentation", "https://doc.qt.io"),
            ("PySide6", "https://doc.qt.io/qtforpython-6/"),
        ]

        for title, url in bookmarks_to_add:
            success = manager.add_bookmark(title, url)
            print(f"  {'✓' if success else '✗'} Added: {title}")

        print(f"\nTotal bookmarks: {manager.get_bookmark_count()}")

        print("\n2. Listing all bookmarks:")
        print("-" * 40)
        bookmarks = manager.get_all_bookmarks()
        for i, bookmark in enumerate(bookmarks, 1):
            print(f"  {i}. {bookmark['title']}")
            print(f"     URL: {bookmark['url']}")
            print(f"     Created: {bookmark['created']}")

        print("\n3. Removing a bookmark:")
        print("-" * 40)
        removed = manager.remove_bookmark("https://python.org")
        print(f"  {'✓' if removed else '✗'} Removed Python bookmark")
        print(f"  Remaining bookmarks: {manager.get_bookmark_count()}")


def demo_search():
    """Demonstrate bookmark search."""
    print_section("Bookmark Search")

    with TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir)
        manager = BookmarkManager(storage_path)

        # Add diverse bookmarks
        test_bookmarks = [
            ("Python Documentation", "https://docs.python.org"),
            ("Python Package Index", "https://pypi.org"),
            ("Qt for Python", "https://doc.qt.io/qtforpython-6/"),
            ("JavaScript MDN", "https://developer.mozilla.org/en-US/docs/Web/JavaScript"),
            ("Rust Documentation", "https://doc.rust-lang.org"),
        ]

        print("Adding test bookmarks...")
        for title, url in test_bookmarks:
            manager.add_bookmark(title, url)

        print(f"Total: {manager.get_bookmark_count()} bookmarks\n")

        # Search examples
        search_queries = ["python", "doc", "javascript", "nonexistent"]

        for query in search_queries:
            results = manager.search_bookmarks(query)
            print(f"Search '{query}': {len(results)} result(s)")
            for result in results:
                print(f"  - {result['title']}")
            print()


def demo_import_export():
    """Demonstrate bookmark import/export."""
    print_section("Bookmark Import/Export")

    with TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create first manager and add bookmarks
        print("1. Creating initial bookmarks:")
        print("-" * 40)
        manager1 = BookmarkManager(tmpdir_path / "manager1")

        initial_bookmarks = [
            ("GitHub", "https://github.com"),
            ("GitLab", "https://gitlab.com"),
        ]

        for title, url in initial_bookmarks:
            manager1.add_bookmark(title, url)
            print(f"  ✓ Added: {title}")

        # Export bookmarks
        export_path = tmpdir_path / "bookmarks_export.json"
        print(f"\n2. Exporting to: {export_path.name}")
        print("-" * 40)
        success = manager1.export_bookmarks(export_path)
        print(f"  {'✓' if success else '✗'} Export {'succeeded' if success else 'failed'}")

        # Create second manager and import
        print("\n3. Importing to new manager:")
        print("-" * 40)
        manager2 = BookmarkManager(tmpdir_path / "manager2")

        # Add one bookmark to test merge
        manager2.add_bookmark("Existing Bookmark", "https://example.com")
        print(f"  Manager2 before import: {manager2.get_bookmark_count()} bookmark(s)")

        # Import with merge
        success = manager2.import_bookmarks(export_path, merge=True)
        print(
            f"  {'✓' if success else '✗'} Import {'succeeded' if success else 'failed'} (merge mode)"
        )
        print(f"  Manager2 after import: {manager2.get_bookmark_count()} bookmark(s)")

        print("\n4. Final bookmarks in manager2:")
        print("-" * 40)
        for bookmark in manager2.get_all_bookmarks():
            print(f"  - {bookmark['title']}")


def demo_duplicate_detection():
    """Demonstrate duplicate URL detection."""
    print_section("Duplicate Detection")

    with TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir)
        manager = BookmarkManager(storage_path)

        print("Attempting to add duplicate URLs:")
        print("-" * 40)

        url = "https://github.com/viloforge/vfwidgets"

        # Add first time
        success1 = manager.add_bookmark("VFWidgets", url)
        print(f"  First add: {'✓ Success' if success1 else '✗ Failed'}")

        # Try to add again (should fail)
        success2 = manager.add_bookmark("VFWidgets (duplicate)", url)
        print(f"  Second add (same URL): {'✓ Success' if success2 else '✗ Blocked (expected)'}")

        print(f"\nTotal bookmarks: {manager.get_bookmark_count()}")
        print("Expected: 1 (duplicate was blocked)")


def main():
    """Run all bookmark demos."""
    print()
    print("=" * 60)
    print("  ViloWeb Example 03: Bookmark Management")
    print("=" * 60)
    print()
    print("This example demonstrates the BookmarkManager API.")
    print("All operations use temporary storage.")
    print()

    try:
        demo_basic_operations()
        demo_search()
        demo_import_export()
        demo_duplicate_detection()

        print()
        print("=" * 60)
        print("  All demos completed successfully!")
        print("=" * 60)
        print()

    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
