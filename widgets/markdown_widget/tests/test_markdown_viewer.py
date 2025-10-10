"""Tests for MarkdownViewer widget."""

import pytest
from PySide6.QtWidgets import QApplication
from vfwidgets_markdown import MarkdownViewer


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()


@pytest.fixture
def viewer(qapp, qtbot):
    """Create viewer instance for testing."""
    viewer = MarkdownViewer()
    qtbot.addWidget(viewer)
    return viewer


def test_viewer_creation(viewer):
    """Test viewer can be created."""
    assert viewer is not None
    assert isinstance(viewer, MarkdownViewer)


def test_viewer_signals(viewer, qtbot):
    """Test viewer signals."""
    with qtbot.waitSignal(viewer.content_loaded, timeout=100):
        viewer.set_markdown("# Test")


def test_set_markdown(viewer):
    """Test setting markdown content."""
    content = "# Hello World\n\nThis is a test."
    viewer.set_markdown(content)
    # Full implementation will verify rendering


def test_get_toc(viewer):
    """Test TOC extraction."""
    toc = viewer.get_toc()
    assert isinstance(toc, list)
    # Full implementation will test actual TOC data
