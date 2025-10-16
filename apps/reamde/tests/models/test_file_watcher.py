"""Tests for FileWatcher."""

import pytest
from reamde.models.file_watcher import FileWatcher


@pytest.mark.skip("Not implemented yet - Phase 1")
def test_file_watcher_init():
    """Test FileWatcher initialization."""
    watcher = FileWatcher()
    assert watcher is not None


@pytest.mark.skip("Not implemented yet - Phase 1")
def test_watch_file(tmp_path):
    """Test watching a file."""
    pass


@pytest.mark.skip("Not implemented yet - Phase 1")
def test_file_changed_signal(tmp_path):
    """Test file_changed signal is emitted."""
    pass
