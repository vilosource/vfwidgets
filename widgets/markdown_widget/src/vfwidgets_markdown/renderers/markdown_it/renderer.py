"""markdown-it based renderer implementation."""

import logging
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtWebEngineCore import QWebEnginePage

from vfwidgets_markdown.renderers.base import RendererCapabilities, RenderResult

logger = logging.getLogger(__name__)


class MarkdownItRenderer:
    """markdown-it based renderer running in QWebEngineView.

    Implements RendererProtocol using markdown-it library with:
    - Prism.js syntax highlighting
    - Mermaid diagram rendering
    - Full markdown extensions support
    """

    def __init__(self, page: QWebEnginePage):
        self._page = page
        self._initialized = False
        self._last_toc = []

        self._capabilities = RendererCapabilities(
            supports_live_preview=True,
            supports_syntax_highlighting=True,
            supports_math=False,
            supports_diagrams=True,
            supports_toc_extraction=True,
            supports_html_export=True,
            requires_javascript=True,
            extensions=["footnote", "abbr", "deflist", "task-lists", "container"],
        )

    @property
    def capabilities(self) -> RendererCapabilities:
        return self._capabilities

    def initialize(self) -> None:
        """Load viewer.html with all JavaScript libraries."""
        if self._initialized:
            return

        # Get path to HTML template
        renderer_dir = Path(__file__).parent
        html_path = renderer_dir / "html" / "viewer.html"

        if not html_path.exists():
            raise FileNotFoundError(f"viewer.html not found: {html_path}")

        # Load HTML with base URL for resources
        base_url = QUrl.fromLocalFile(str(renderer_dir) + "/")
        with open(html_path, encoding="utf-8") as f:
            html_content = f.read()

        self._page.setHtml(html_content, base_url)
        self._initialized = True
        logger.debug(f"MarkdownItRenderer initialized from {html_path}")

    def shutdown(self) -> None:
        """Clean up resources."""
        self._page = None
        self._initialized = False

    def render(self, markdown: str) -> RenderResult:
        """Render markdown via JavaScript."""
        if not self._initialized:
            return RenderResult(html="", errors=["Renderer not initialized"])

        # This is handled by MarkdownViewer's _render_markdown()
        # The renderer doesn't execute JS directly, the viewer does
        # Return success - actual rendering happens in viewer
        return RenderResult(html=markdown)

    def set_theme(self, theme_data: dict[str, str]) -> None:
        """Theme is handled by ThemeBridge, not renderer."""
        pass

    def get_toc(self) -> list[dict]:
        """Get TOC from last render."""
        return self._last_toc.copy()

    def export_html(self, markdown: str, standalone: bool = True) -> str:
        """Export HTML (delegated to viewer's JavaScript)."""
        # This is handled by MarkdownViewer.export_html()
        pass
