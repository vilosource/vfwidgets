"""Pytest configuration for HTML/JS tests."""

from pathlib import Path

import pytest


@pytest.fixture
def resources_dir():
    """Get path to renderer resources."""
    return (
        Path(__file__).parent.parent.parent
        / "src"
        / "vfwidgets_markdown"
        / "renderers"
        / "markdown_it"
    )


@pytest.fixture
def viewer_html(resources_dir):
    """Get viewer.html content."""
    html_path = resources_dir / "html" / "viewer.html"
    return html_path.read_text()
