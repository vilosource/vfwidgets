"""Tests for BookmarkManager."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from viloweb import BookmarkManager


@pytest.fixture
def temp_storage():
    """Create temporary storage directory."""
    with TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def manager(temp_storage):
    """Create BookmarkManager with temporary storage."""
    return BookmarkManager(temp_storage)


def test_initialization(temp_storage):
    """Test manager initialization."""
    manager = BookmarkManager(temp_storage)
    assert manager.get_bookmark_count() == 0


def test_add_bookmark(manager):
    """Test adding a bookmark."""
    success = manager.add_bookmark("Test", "https://example.com")
    assert success is True
    assert manager.get_bookmark_count() == 1


def test_add_duplicate_bookmark(manager):
    """Test that duplicate URLs are rejected."""
    manager.add_bookmark("Test 1", "https://example.com")
    success = manager.add_bookmark("Test 2", "https://example.com")
    assert success is False
    assert manager.get_bookmark_count() == 1


def test_add_empty_url(manager):
    """Test that empty URLs are rejected."""
    success = manager.add_bookmark("Empty", "")
    assert success is False
    assert manager.get_bookmark_count() == 0


def test_add_about_blank(manager):
    """Test that about:blank is rejected."""
    success = manager.add_bookmark("Blank", "about:blank")
    assert success is False
    assert manager.get_bookmark_count() == 0


def test_remove_bookmark(manager):
    """Test removing a bookmark."""
    manager.add_bookmark("Test", "https://example.com")
    success = manager.remove_bookmark("https://example.com")
    assert success is True
    assert manager.get_bookmark_count() == 0


def test_remove_nonexistent(manager):
    """Test removing non-existent bookmark."""
    success = manager.remove_bookmark("https://nonexistent.com")
    assert success is False


def test_get_all_bookmarks(manager):
    """Test getting all bookmarks."""
    manager.add_bookmark("Test 1", "https://example1.com")
    manager.add_bookmark("Test 2", "https://example2.com")

    bookmarks = manager.get_all_bookmarks()
    assert len(bookmarks) == 2
    assert all("title" in bm and "url" in bm and "created" in bm for bm in bookmarks)


def test_bookmarks_sorted_by_creation(manager):
    """Test that bookmarks are sorted by creation time (newest first)."""
    manager.add_bookmark("Old", "https://old.com")
    manager.add_bookmark("New", "https://new.com")

    bookmarks = manager.get_all_bookmarks()
    # Newest should be first
    assert bookmarks[0]["title"] == "New"
    assert bookmarks[1]["title"] == "Old"


def test_search_by_title(manager):
    """Test searching bookmarks by title."""
    manager.add_bookmark("Python Docs", "https://python.org")
    manager.add_bookmark("JavaScript Docs", "https://javascript.info")

    results = manager.search_bookmarks("python")
    assert len(results) == 1
    assert results[0]["title"] == "Python Docs"


def test_search_by_url(manager):
    """Test searching bookmarks by URL."""
    manager.add_bookmark("Example", "https://example.com")
    manager.add_bookmark("Test", "https://test.com")

    results = manager.search_bookmarks("example")
    assert len(results) == 1
    assert results[0]["url"] == "https://example.com"


def test_search_case_insensitive(manager):
    """Test that search is case-insensitive."""
    manager.add_bookmark("Python", "https://python.org")

    results = manager.search_bookmarks("PYTHON")
    assert len(results) == 1


def test_search_empty_query(manager):
    """Test that empty query returns all bookmarks."""
    manager.add_bookmark("Test 1", "https://test1.com")
    manager.add_bookmark("Test 2", "https://test2.com")

    results = manager.search_bookmarks("")
    assert len(results) == 2


def test_clear_all_bookmarks(manager):
    """Test clearing all bookmarks."""
    manager.add_bookmark("Test 1", "https://test1.com")
    manager.add_bookmark("Test 2", "https://test2.com")

    manager.clear_all_bookmarks()
    assert manager.get_bookmark_count() == 0


def test_persistence(temp_storage):
    """Test that bookmarks persist across manager instances."""
    # Create manager and add bookmark
    manager1 = BookmarkManager(temp_storage)
    manager1.add_bookmark("Test", "https://example.com")

    # Create new manager with same storage
    manager2 = BookmarkManager(temp_storage)
    assert manager2.get_bookmark_count() == 1

    bookmarks = manager2.get_all_bookmarks()
    assert bookmarks[0]["title"] == "Test"


def test_export_bookmarks(manager, temp_storage):
    """Test exporting bookmarks."""
    manager.add_bookmark("Test", "https://example.com")

    export_path = temp_storage / "export.json"
    success = manager.export_bookmarks(export_path)

    assert success is True
    assert export_path.exists()

    # Verify export format
    with open(export_path, "r") as f:
        data = json.load(f)

    assert "version" in data
    assert "bookmarks" in data
    assert len(data["bookmarks"]) == 1


def test_import_bookmarks_merge(temp_storage):
    """Test importing bookmarks with merge."""
    # Create first manager with bookmarks
    manager1 = BookmarkManager(temp_storage / "manager1")
    manager1.add_bookmark("Test 1", "https://test1.com")
    manager1.add_bookmark("Test 2", "https://test2.com")

    export_path = temp_storage / "export.json"
    manager1.export_bookmarks(export_path)

    # Create second manager with one bookmark
    manager2 = BookmarkManager(temp_storage / "manager2")
    manager2.add_bookmark("Existing", "https://existing.com")

    # Import with merge
    success = manager2.import_bookmarks(export_path, merge=True)
    assert success is True
    assert manager2.get_bookmark_count() == 3  # 1 existing + 2 imported


def test_import_bookmarks_replace(temp_storage):
    """Test importing bookmarks with replace."""
    # Create first manager with bookmarks
    manager1 = BookmarkManager(temp_storage / "manager1")
    manager1.add_bookmark("Test 1", "https://test1.com")
    manager1.add_bookmark("Test 2", "https://test2.com")

    export_path = temp_storage / "export.json"
    manager1.export_bookmarks(export_path)

    # Create second manager with one bookmark
    manager2 = BookmarkManager(temp_storage / "manager2")
    manager2.add_bookmark("Existing", "https://existing.com")

    # Import with replace
    success = manager2.import_bookmarks(export_path, merge=False)
    assert success is True
    assert manager2.get_bookmark_count() == 2  # Only imported bookmarks

    # Original bookmark should be gone
    results = manager2.search_bookmarks("Existing")
    assert len(results) == 0


def test_title_truncation(manager):
    """Test that long titles are truncated."""
    long_title = "A" * 300  # Very long title
    manager.add_bookmark(long_title, "https://example.com")

    bookmarks = manager.get_all_bookmarks()
    assert len(bookmarks[0]["title"]) == 200  # Truncated to 200


def test_title_from_url(manager):
    """Test that URL is used as title if title is empty."""
    manager.add_bookmark("   ", "https://example.com")  # Whitespace only

    bookmarks = manager.get_all_bookmarks()
    assert "example.com" in bookmarks[0]["title"]


def test_corrupt_file_recovery(temp_storage):
    """Test that manager handles corrupt bookmark file."""
    # Create corrupt file
    bookmarks_file = temp_storage / "bookmarks.json"
    bookmarks_file.write_text("{ invalid json }")

    # Manager should handle gracefully
    manager = BookmarkManager(temp_storage)
    assert manager.get_bookmark_count() == 0

    # Corrupt file should be backed up
    backup_file = temp_storage / "bookmarks.json.corrupt"
    assert backup_file.exists()


def test_missing_fields_in_file(temp_storage):
    """Test that manager handles file with missing fields."""
    # Create file with missing 'bookmarks' field
    bookmarks_file = temp_storage / "bookmarks.json"
    bookmarks_file.write_text('{"version": "1.0"}')

    # Manager should handle gracefully
    manager = BookmarkManager(temp_storage)
    assert manager.get_bookmark_count() == 0

    # Should be able to add bookmarks
    manager.add_bookmark("Test", "https://example.com")
    assert manager.get_bookmark_count() == 1
