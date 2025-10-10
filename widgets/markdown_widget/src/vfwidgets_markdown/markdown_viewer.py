"""Implementation of MarkdownViewer widget."""

import json
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, QUrl, Signal, Slot
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget


class JavaScriptBridge(QObject):
    """Bridge object for Qt ↔ JavaScript communication."""

    # Signals to emit to Python
    message_received = Signal(dict)

    @Slot(str)
    def receiveMessage(self, message_json: str) -> None:
        """Receive message from JavaScript.

        Args:
            message_json: JSON string from JavaScript
        """
        try:
            message = json.loads(message_json)
            self.message_received.emit(message)
        except json.JSONDecodeError as e:
            print(f"[MarkdownViewer] Invalid JSON from JavaScript: {e}")


class MarkdownViewer(QWebEngineView):
    """Markdown viewer widget with support for diagrams, syntax highlighting, and math.

    Features:
    - Full markdown support (CommonMark + GFM)
    - Mermaid diagrams (flowchart, sequence, class, gantt, state, etc.)
    - Syntax highlighting with Prism.js (300+ languages)
    - Math equations with KaTeX (inline and block LaTeX)
    - Theme support (light/dark)
    - TOC extraction API
    - Signals for integration with editors

    Signals:
        content_loaded: Emitted when markdown rendering completes
        toc_changed(list): Emitted when table of contents changes
        rendering_failed(str): Emitted when rendering fails with error message
        viewer_ready: Emitted when viewer is initialized and ready
    """

    # Define custom signals
    content_loaded = Signal()
    toc_changed = Signal(list)
    rendering_failed = Signal(str)
    viewer_ready = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the MarkdownViewer.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Internal state
        self._current_markdown = ""
        self._current_toc = []
        self._is_ready = False

        # Setup web engine
        self._setup_webengine()

        # Setup QWebChannel bridge
        self._setup_bridge()

        # Load HTML template
        self._load_template()

    def _setup_webengine(self) -> None:
        """Configure QWebEngineView and page settings."""
        # Create custom page
        page = QWebEnginePage(self)
        self.setPage(page)

        # Configure settings
        settings = page.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, False)

        # Disable caching for development (allows resource updates without restart)
        from PySide6.QtWebEngineCore import QWebEngineProfile

        profile = page.profile()
        profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.NoCache)

        print("[MarkdownViewer] WebEngine configured")

    def _setup_bridge(self) -> None:
        """Setup QWebChannel for Qt ↔ JavaScript communication."""
        self._channel = QWebChannel(self.page())
        self._bridge = JavaScriptBridge(self)

        # Connect bridge signals
        self._bridge.message_received.connect(self._on_javascript_message)

        # Register bridge object
        self._channel.registerObject("qtBridge", self._bridge)
        self.page().setWebChannel(self._channel)

        print("[MarkdownViewer] QWebChannel bridge setup complete")

    def _load_template(self) -> None:
        """Load the HTML template with resources."""
        # Get path to resources
        resources_dir = Path(__file__).parent / "resources"
        html_path = resources_dir / "viewer.html"

        if not html_path.exists():
            error_msg = f"Template not found: {html_path}"
            print(f"[MarkdownViewer] ERROR: {error_msg}")
            self.rendering_failed.emit(error_msg)
            return

        # Read template
        with open(html_path, encoding="utf-8") as f:
            html_content = f.read()

        # Set base URL for relative resource loading
        base_url = QUrl.fromLocalFile(str(resources_dir) + "/")

        # Load HTML
        self.setHtml(html_content, base_url)
        print("[MarkdownViewer] Template loaded")

    @Slot(dict)
    def _on_javascript_message(self, message: dict) -> None:
        """Handle messages from JavaScript.

        Args:
            message: Message dictionary from JavaScript
        """
        msg_type = message.get("type")

        if msg_type == "ready":
            self._is_ready = True
            self.viewer_ready.emit()
            print("[MarkdownViewer] Viewer ready")

        elif msg_type == "content_loaded":
            self.content_loaded.emit()
            print("[MarkdownViewer] Content loaded")

        elif msg_type == "toc_changed":
            self._current_toc = message.get("data", [])
            self.toc_changed.emit(self._current_toc)
            print(f"[MarkdownViewer] TOC updated: {len(self._current_toc)} headings")

        elif msg_type == "rendering_failed":
            error = message.get("error", "Unknown error")
            self.rendering_failed.emit(error)
            print(f"[MarkdownViewer] Rendering failed: {error}")

        else:
            print(f"[MarkdownViewer] Unknown message type: {msg_type}")

    def set_markdown(self, content: str) -> None:
        """Set markdown content to render.

        Args:
            content: Markdown content string
        """
        self._current_markdown = content

        # Escape content for JavaScript
        escaped_content = json.dumps(content)

        # Call JavaScript render function
        js_code = f"window.MarkdownViewer.render({escaped_content});"
        self.page().runJavaScript(js_code)

        print(f"[MarkdownViewer] Rendering {len(content)} bytes of markdown")

    def load_file(self, path: str) -> None:
        """Load markdown from file.

        Args:
            path: Path to markdown file
        """
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
            self.set_markdown(content)
            print(f"[MarkdownViewer] Loaded file: {path}")
        except Exception as e:
            error_msg = f"Failed to load file: {e}"
            print(f"[MarkdownViewer] ERROR: {error_msg}")
            self.rendering_failed.emit(error_msg)

    def get_toc(self) -> list:
        """Get table of contents from current markdown.

        Returns:
            List of heading dictionaries with keys:
            - level: Heading level (1-6)
            - text: Heading text
            - id: HTML element ID for navigation
            - line: Line number in source (always 0 for now)
        """
        return self._current_toc.copy()

    def scroll_to_heading(self, heading_id: str) -> None:
        """Scroll to heading by ID.

        Args:
            heading_id: HTML element ID of the heading
        """
        escaped_id = json.dumps(heading_id)
        js_code = f"window.MarkdownViewer.scrollToHeading({escaped_id});"
        self.page().runJavaScript(js_code)

    def set_theme(self, theme: str) -> None:
        """Set viewer theme.

        Args:
            theme: Theme name ('light', 'dark', or custom)
        """
        escaped_theme = json.dumps(theme)
        js_code = f"window.MarkdownViewer.setTheme({escaped_theme});"
        self.page().runJavaScript(js_code)
        print(f"[MarkdownViewer] Theme set to: {theme}")

    def is_ready(self) -> bool:
        """Check if viewer is ready to render.

        Returns:
            True if viewer is ready, False otherwise
        """
        return self._is_ready
