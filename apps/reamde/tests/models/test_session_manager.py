"""Tests for SessionManager."""

import pytest

from reamde.models.session import SessionManager, SessionState


@pytest.mark.skip("Not implemented yet - Phase 1")
def test_session_manager_init():
    """Test SessionManager initialization."""
    manager = SessionManager()
    assert manager is not None


@pytest.mark.skip("Not implemented yet - Phase 1")
def test_save_and_load_session(tmp_path):
    """Test saving and loading session."""
    manager = SessionManager()
    session = SessionState(open_files=["/tmp/file1.md", "/tmp/file2.md"], active_file_index=1)

    # Save
    manager.save_session(session)

    # Load
    loaded = manager.load_session()
    assert loaded.open_files == session.open_files
    assert loaded.active_file_index == session.active_file_index


@pytest.mark.skip("Not implemented yet - Phase 1")
def test_session_version_migration():
    """Test session version migration."""
    pass
