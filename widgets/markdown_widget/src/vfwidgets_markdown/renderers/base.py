"""Base classes and protocols for markdown renderers.

This module defines the abstract interface that all markdown renderers
must implement, allowing for pluggable rendering backends.
"""

from dataclasses import dataclass, field
from typing import Optional, Protocol, runtime_checkable


@dataclass
class RendererCapabilities:
    """Describes what a renderer implementation can do.

    This allows widgets to query renderer features and adjust
    UI accordingly (e.g., disable diagram button if not supported).
    """

    supports_live_preview: bool = True
    supports_syntax_highlighting: bool = True
    supports_math: bool = False
    supports_diagrams: bool = False
    supports_toc_extraction: bool = True
    supports_html_export: bool = True
    requires_javascript: bool = True

    # Supported markdown extensions (e.g., "footnote", "tables", etc.)
    extensions: list[str] = field(default_factory=list)


@dataclass
class RenderResult:
    """Result of a rendering operation.

    Includes the rendered HTML and optional metadata like
    table of contents, errors, or custom renderer-specific data.
    """

    html: str
    toc: Optional[list[dict]] = None  # [{level: int, text: str, id: str}, ...]
    metadata: Optional[dict] = None  # Custom renderer metadata
    errors: Optional[list[str]] = None  # Rendering errors/warnings

    @property
    def success(self) -> bool:
        """Whether rendering succeeded without errors."""
        return not self.errors or len(self.errors) == 0


@runtime_checkable
class RendererProtocol(Protocol):
    """Abstract protocol for markdown renderers.

    All markdown renderer implementations must conform to this protocol.
    This allows the markdown viewer widget to work with any renderer
    implementation without coupling to specific rendering technology.

    Implementations can be:
    - JavaScript-based (markdown-it, marked, etc.) running in QWebEngineView
    - Python-based (python-markdown, mistune, etc.) with server-side rendering
    - Remote (external service, API, etc.)

    Example:
        class MyRenderer:
            @property
            def capabilities(self) -> RendererCapabilities:
                return RendererCapabilities(
                    supports_diagrams=True,
                    extensions=["footnote", "tables"]
                )

            def initialize(self) -> None:
                # Load resources, setup environment
                pass

            def render(self, markdown: str) -> RenderResult:
                html = my_markdown_library.render(markdown)
                return RenderResult(html=html)

            # ... implement other protocol methods

        # Use with markdown viewer
        renderer = MyRenderer()
        viewer = MarkdownViewer(renderer=renderer)
    """

    @property
    def capabilities(self) -> RendererCapabilities:
        """Get renderer capabilities and feature set.

        Returns:
            RendererCapabilities describing what this renderer supports
        """
        ...

    def initialize(self) -> None:
        """Initialize renderer (load libraries, setup environment, etc.).

        Called once when widget is created. Should be idempotent - calling
        multiple times should be safe and have no additional effect.

        For JavaScript-based renderers, this might load the HTML page.
        For Python-based renderers, this might initialize the markdown library.

        Raises:
            RuntimeError: If initialization fails
        """
        ...

    def shutdown(self) -> None:
        """Clean up renderer resources.

        Called when widget is destroyed. Should release any held resources
        (memory, file handles, network connections, etc.).

        Should be safe to call multiple times (idempotent).
        """
        ...

    def render(self, markdown: str) -> RenderResult:
        """Render markdown to HTML.

        This is the core method that transforms markdown source into HTML.

        Args:
            markdown: Raw markdown source text

        Returns:
            RenderResult with HTML and optional metadata (TOC, errors)

        Raises:
            RuntimeError: If renderer not initialized or rendering fails critically

        Note:
            Non-critical errors (e.g., malformed markdown) should be returned
            in RenderResult.errors rather than raising exceptions.
        """
        ...

    def set_theme(self, theme_data: dict[str, str]) -> None:
        """Apply theme to renderer.

        For JavaScript-based renderers, this typically injects CSS variables.
        For Python-based renderers, this might update syntax highlighting colors.

        Args:
            theme_data: CSS custom properties dict
                Example: {
                    "--md-fg": "#c9d1d9",
                    "--md-bg": "#0d1117",
                    "--md-code-bg": "#161b22"
                }

        Note:
            Theme application may be asynchronous (e.g., JavaScript execution).
            Renderers should handle theme changes gracefully even during rendering.
        """
        ...

    def get_toc(self) -> list[dict]:
        """Extract table of contents from last rendered document.

        Returns:
            List of heading dicts: [
                {"level": 1, "text": "Introduction", "id": "introduction"},
                {"level": 2, "text": "Overview", "id": "overview"},
                ...
            ]

            Empty list if no headings or TOC extraction not supported.

        Note:
            This typically returns cached TOC from the last render() call.
            No need to re-parse the document.
        """
        ...

    def export_html(self, markdown: str, standalone: bool = True) -> str:
        """Export complete standalone HTML document.

        Creates a full HTML document suitable for saving to a file
        or opening in a browser. Includes all necessary CSS, JavaScript,
        and other resources inline.

        Args:
            markdown: Raw markdown source to export
            standalone: If True, include full HTML structure with <html>,
                <head>, <body> tags and all resources inline.
                If False, return only the rendered HTML fragment.

        Returns:
            Complete HTML document (if standalone=True) or HTML fragment

        Note:
            Standalone exports should include:
            - All CSS (including syntax highlighting)
            - All JavaScript (if needed for interactive features)
            - Proper character encoding declarations
            - Title and meta tags
        """
        ...
