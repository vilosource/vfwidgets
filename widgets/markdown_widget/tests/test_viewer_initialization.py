"""Tests for MarkdownViewer async initialization and content queueing."""

import pytest

from vfwidgets_markdown import MarkdownViewer


def test_set_markdown_before_ready(qtbot):
    """Test that set_markdown() works immediately after construction."""
    viewer = MarkdownViewer()
    qtbot.addWidget(viewer)

    # Should not raise, should not display nothing
    test_content = "# Test Heading\n\nTest content"
    viewer.set_markdown(test_content)

    # Verify content is queued (viewer should not be ready yet)
    assert not viewer.is_ready()
    assert viewer._pending_render == test_content

    # Wait for viewer to be ready
    with qtbot.waitSignal(viewer.viewer_ready, timeout=5000):
        pass

    # Verify viewer is now ready and pending content was cleared
    assert viewer.is_ready()
    assert viewer._pending_render is None

    # Wait for content to load
    with qtbot.waitSignal(viewer.content_loaded, timeout=5000):
        pass


def test_constructor_with_initial_content(qtbot):
    """Test passing content in constructor."""
    test_content = "# Hello from Constructor"
    viewer = MarkdownViewer(initial_content=test_content)
    qtbot.addWidget(viewer)

    # Content should be queued
    assert not viewer.is_ready()
    assert viewer._pending_render == test_content

    # Wait for ready
    with qtbot.waitSignal(viewer.viewer_ready, timeout=5000):
        pass

    assert viewer.is_ready()
    assert viewer._pending_render is None

    # Wait for content to load
    with qtbot.waitSignal(viewer.content_loaded, timeout=5000):
        pass


def test_constructor_with_base_path(qtbot, tmp_path):
    """Test passing base_path in constructor."""
    test_path = tmp_path / "test_dir"
    test_path.mkdir()

    viewer = MarkdownViewer(base_path=test_path)
    qtbot.addWidget(viewer)

    # Base path should be queued
    assert not viewer.is_ready()
    assert viewer._pending_base_path == test_path

    # Wait for ready
    with qtbot.waitSignal(viewer.viewer_ready, timeout=5000):
        pass

    assert viewer.is_ready()
    assert viewer._base_path == test_path
    assert viewer._pending_base_path is None


def test_multiple_sets_before_ready(qtbot):
    """Test calling set_markdown() multiple times before ready."""
    viewer = MarkdownViewer()
    qtbot.addWidget(viewer)

    viewer.set_markdown("# First")
    viewer.set_markdown("# Second")
    viewer.set_markdown("# Third")  # This should win

    # Only the last content should be queued
    assert viewer._pending_render == "# Third"

    # Wait for ready
    with qtbot.waitSignal(viewer.viewer_ready, timeout=5000):
        pass

    assert viewer.is_ready()
    assert viewer._pending_render is None

    # Wait for content to load
    with qtbot.waitSignal(viewer.content_loaded, timeout=5000):
        pass


def test_load_file_returns_boolean(qtbot, tmp_path):
    """Test load_file() returns boolean status."""
    # Create test file
    test_file = tmp_path / "test.md"
    test_file.write_text("# Test File Content")

    viewer = MarkdownViewer()
    qtbot.addWidget(viewer)

    # Load existing file should return True
    result = viewer.load_file(test_file)
    assert result is True

    # Load non-existent file should return False
    result = viewer.load_file(tmp_path / "nonexistent.md")
    assert result is False


def test_load_file_accepts_path_object(qtbot, tmp_path):
    """Test load_file() accepts Path objects."""
    test_file = tmp_path / "test.md"
    test_file.write_text("# Path Object Test")

    viewer = MarkdownViewer()
    qtbot.addWidget(viewer)

    # Should accept Path object
    result = viewer.load_file(test_file)
    assert result is True

    # Should also accept string
    result = viewer.load_file(str(test_file))
    assert result is True


def test_load_file_sets_base_path(qtbot, tmp_path):
    """Test load_file() automatically sets base path."""
    test_file = tmp_path / "test.md"
    test_file.write_text("# Test with Images\n\n![image](image.png)")

    viewer = MarkdownViewer()
    qtbot.addWidget(viewer)

    viewer.load_file(test_file)

    # Base path should be queued to parent directory
    assert viewer._pending_base_path == test_file.parent

    # Wait for ready
    with qtbot.waitSignal(viewer.viewer_ready, timeout=5000):
        pass

    # Base path should be set
    assert viewer._base_path == test_file.parent


def test_is_ready_state(qtbot):
    """Test is_ready() returns correct state."""
    viewer = MarkdownViewer()
    qtbot.addWidget(viewer)

    # Should not be ready immediately
    assert viewer.is_ready() is False

    # Wait for ready signal
    with qtbot.waitSignal(viewer.viewer_ready, timeout=5000):
        pass

    # Should be ready after signal
    assert viewer.is_ready() is True


def test_set_markdown_after_ready(qtbot):
    """Test set_markdown() after viewer is ready."""
    viewer = MarkdownViewer()
    qtbot.addWidget(viewer)

    # Wait for ready
    with qtbot.waitSignal(viewer.viewer_ready, timeout=5000):
        pass

    assert viewer.is_ready()

    # Now set content - should render immediately
    viewer.set_markdown("# After Ready")

    # Should not be queued
    assert viewer._pending_render is None

    # Wait for content to load
    with qtbot.waitSignal(viewer.content_loaded, timeout=5000):
        pass


def test_set_base_path_before_ready(qtbot, tmp_path):
    """Test set_base_path() before viewer is ready."""
    viewer = MarkdownViewer()
    qtbot.addWidget(viewer)

    test_path = tmp_path / "base"
    test_path.mkdir()

    # Set before ready
    viewer.set_base_path(str(test_path))

    # Should be queued
    assert viewer._pending_base_path == test_path
    assert viewer._base_path is None

    # Wait for ready
    with qtbot.waitSignal(viewer.viewer_ready, timeout=5000):
        pass

    # Should be applied
    assert viewer._base_path == test_path
    assert viewer._pending_base_path is None


def test_combined_constructor_params(qtbot, tmp_path):
    """Test constructor with both initial_content and base_path."""
    test_path = tmp_path / "base"
    test_path.mkdir()

    viewer = MarkdownViewer(initial_content="# Combined Test", base_path=test_path)
    qtbot.addWidget(viewer)

    # Both should be queued
    assert viewer._pending_render == "# Combined Test"
    assert viewer._pending_base_path == test_path

    # Wait for ready
    with qtbot.waitSignal(viewer.viewer_ready, timeout=5000):
        pass

    # Both should be applied
    assert viewer.is_ready()
    assert viewer._pending_render is None
    assert viewer._pending_base_path is None
    assert viewer._base_path == test_path

    # Wait for content to load
    with qtbot.waitSignal(viewer.content_loaded, timeout=5000):
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
