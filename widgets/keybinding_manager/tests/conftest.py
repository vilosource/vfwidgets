"""Shared pytest fixtures for KeybindingManager tests."""

import tempfile
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    """Create Qt application for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def temp_storage_file():
    """Create temporary file for storage tests."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        file_path = Path(f.name)

    yield file_path

    # Cleanup
    if file_path.exists():
        file_path.unlink()
