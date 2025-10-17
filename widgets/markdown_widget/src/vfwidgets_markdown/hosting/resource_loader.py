"""Resource loading for webview content.

This module handles loading HTML/CSS/JS resources from package files
and generating proper URLs for QWebEngineView.
"""

import logging
from pathlib import Path

from PySide6.QtCore import QUrl

logger = logging.getLogger(__name__)


class ResourceLoader:
    """Loads HTML/CSS/JS resources for webview content.

    Handles:
    - Locating resource files in package
    - Generating QUrl for local files
    - Content Security Policy headers
    - Resource validation

    Example:
        loader = ResourceLoader(resources_dir=Path("/path/to/resources"))
        html_url = loader.get_html_url("viewer.html")
        css_path = loader.get_resource_path("css/viewer.css")
    """

    def __init__(self, resources_dir: Path):
        """Initialize resource loader.

        Args:
            resources_dir: Base directory containing HTML/CSS/JS resources
        """
        self._resources_dir = resources_dir
        logger.debug(f"ResourceLoader initialized with dir: {resources_dir}")

    def get_html_url(self, html_filename: str) -> QUrl:
        """Get QUrl for HTML file.

        Args:
            html_filename: Name of HTML file (e.g., "viewer.html")

        Returns:
            QUrl pointing to local file

        Raises:
            FileNotFoundError: If HTML file doesn't exist
        """
        html_path = self._resources_dir / html_filename

        if not html_path.exists():
            raise FileNotFoundError(f"HTML file not found: {html_path}")

        url = QUrl.fromLocalFile(str(html_path.absolute()))
        logger.debug(f"HTML URL: {url.toString()}")
        return url

    def get_resource_path(self, relative_path: str) -> Path:
        """Get absolute path to resource file.

        Args:
            relative_path: Path relative to resources_dir
                (e.g., "css/viewer.css", "js/viewer.js")

        Returns:
            Absolute Path to resource

        Raises:
            FileNotFoundError: If resource doesn't exist
        """
        resource_path = self._resources_dir / relative_path

        if not resource_path.exists():
            raise FileNotFoundError(f"Resource not found: {resource_path}")

        return resource_path.absolute()

    def resource_exists(self, relative_path: str) -> bool:
        """Check if resource file exists.

        Args:
            relative_path: Path relative to resources_dir

        Returns:
            True if resource exists, False otherwise
        """
        resource_path = self._resources_dir / relative_path
        return resource_path.exists()

    def get_resources_dir(self) -> Path:
        """Get base resources directory.

        Returns:
            Absolute path to resources directory
        """
        return self._resources_dir.absolute()

    @staticmethod
    def get_default_csp() -> str:
        """Get default Content Security Policy.

        Returns:
            CSP header value suitable for QWebEngineView

        Note:
            This allows local resources and common CDNs.
            Adjust based on security requirements.
        """
        return (
            "default-src 'self' data: https: 'unsafe-inline' 'unsafe-eval'; "
            "img-src 'self' data: https: http:;"
        )

    def validate_resources(self, required_files: list[str]) -> tuple[list[str], list[str]]:
        """Validate that required resource files exist.

        Args:
            required_files: List of relative paths to check
                (e.g., ["viewer.html", "css/viewer.css", "js/viewer.js"])

        Returns:
            Tuple of (found_files, missing_files)
        """
        found = []
        missing = []

        for rel_path in required_files:
            if self.resource_exists(rel_path):
                found.append(rel_path)
            else:
                missing.append(rel_path)

        return found, missing
