"""Pytest configuration for ViloWeb tests."""

import sys
from pathlib import Path

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for testing.

    pytest-qt provides this automatically, but we define it here
    for clarity and to ensure it uses ThemedApplication if available.
    """
    from PySide6.QtWidgets import QApplication

    # Try to use ThemedApplication if available
    try:
        from vfwidgets_theme import ThemedApplication

        app = ThemedApplication.instance() or ThemedApplication([])
    except ImportError:
        app = QApplication.instance() or QApplication([])

    yield app

    # Cleanup happens automatically
