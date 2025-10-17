# Markdown Renderer Protocol - Design Specification

## Overview

The `RendererProtocol` defines an abstract interface for pluggable markdown rendering engines. This allows the markdown widget to support multiple rendering backends (JavaScript-based, Python-based, server-side, etc.) without coupling to a specific implementation.

**Inspired by**: VS Code's webview architecture, terminal widget's theme handling patterns

---

## Design Goals

1. **Pluggability**: Swap renderers without changing widget code
2. **Testability**: Test renderers in isolation from Qt widget
3. **Flexibility**: Support both client-side (JS) and server-side (Python) rendering
4. **Consistency**: Uniform API regardless of implementation
5. **Reusability**: Pattern applicable to other content-rendering widgets

---

## Core Protocol Definition

### Python Protocol (Abstract Interface)

```python
from typing import Protocol, Optional, runtime_checkable
from dataclasses import dataclass


@dataclass
class RendererCapabilities:
    """Describes what a renderer implementation can do."""

    supports_live_preview: bool = True
    supports_syntax_highlighting: bool = True
    supports_math: bool = False
    supports_diagrams: bool = False
    supports_toc_extraction: bool = True
    supports_html_export: bool = True
    requires_javascript: bool = True

    # Supported markdown extensions
    extensions: list[str] = None

    def __post_init__(self):
        if self.extensions is None:
            self.extensions = []


@dataclass
class RenderResult:
    """Result of rendering operation."""

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

    Implementations can be:
    - JavaScript-based (markdown-it, marked, etc.)
    - Python-based (python-markdown, mistune, etc.)
    - Server-side (external service, static site generator, etc.)
    """

    @property
    def capabilities(self) -> RendererCapabilities:
        """Get renderer capabilities and feature set."""
        ...

    def initialize(self) -> None:
        """Initialize renderer (load libraries, setup environment, etc.).

        Called once when widget is created. Should be idempotent.
        """
        ...

    def shutdown(self) -> None:
        """Clean up renderer resources.

        Called when widget is destroyed. Should release any held resources.
        """
        ...

    def render(self, markdown: str) -> RenderResult:
        """Render markdown to HTML.

        Args:
            markdown: Raw markdown source text

        Returns:
            RenderResult with HTML and optional metadata
        """
        ...

    def set_theme(self, theme_data: dict[str, str]) -> None:
        """Apply theme to renderer.

        Args:
            theme_data: CSS custom properties dict
                Example: {"--md-fg": "#c9d1d9", "--md-bg": "#0d1117"}
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
        """
        ...

    def export_html(self, markdown: str, standalone: bool = True) -> str:
        """Export complete standalone HTML document.

        Args:
            markdown: Raw markdown source
            standalone: Include full HTML structure, CSS, JS

        Returns:
            Complete HTML document suitable for saving to file
        """
        ...
```

---

## Implementation Classes

### 1. MarkdownItRenderer (Current Implementation)

JavaScript-based renderer using markdown-it library in QWebEngineView.

```python
from typing import Optional
from PySide6.QtWebEngineCore import QWebEnginePage
from vfwidgets_markdown.renderers.base import (
    RendererProtocol,
    RendererCapabilities,
    RenderResult
)


class MarkdownItRenderer:
    """markdown-it based renderer running in QWebEngineView.

    This is the current implementation, refactored to conform to
    RendererProtocol. Maintains all existing features.
    """

    def __init__(self, page: QWebEnginePage):
        """Initialize with QWebEnginePage.

        Args:
            page: QWebEnginePage instance where renderer will run
        """
        self._page = page
        self._initialized = False
        self._last_toc: list[dict] = []

        self._capabilities = RendererCapabilities(
            supports_live_preview=True,
            supports_syntax_highlighting=True,  # Prism.js
            supports_math=False,  # TODO: Add KaTeX
            supports_diagrams=True,  # Mermaid.js
            supports_toc_extraction=True,
            supports_html_export=True,
            requires_javascript=True,
            extensions=[
                "footnote",
                "abbr",
                "deflist",
                "task-lists",
                "container",
            ]
        )

    @property
    def capabilities(self) -> RendererCapabilities:
        return self._capabilities

    def initialize(self) -> None:
        """Load viewer.html and initialize JavaScript libraries."""
        if self._initialized:
            return

        # Load viewer.html (contains markdown-it, prism, mermaid)
        html_path = self._get_viewer_html_path()
        self._page.setUrl(QUrl.fromLocalFile(html_path))

        # Wait for page load before marking as initialized
        # (handled by MarkdownViewer's loadFinished signal)
        self._initialized = True

    def shutdown(self) -> None:
        """Clean up resources."""
        self._page = None
        self._initialized = False

    def render(self, markdown: str) -> RenderResult:
        """Render markdown via JavaScript markdown-it library.

        Args:
            markdown: Markdown source

        Returns:
            RenderResult with rendered HTML
        """
        if not self._initialized:
            return RenderResult(
                html="",
                errors=["Renderer not initialized"]
            )

        # Call JavaScript render function
        js_code = f"""
        (function() {{
            try {{
                const result = window.viewerAPI.render({json.dumps(markdown)});
                return {{
                    success: true,
                    html: result.html,
                    toc: result.toc || []
                }};
            }} catch (e) {{
                return {{
                    success: false,
                    error: e.toString()
                }};
            }}
        }})();
        """

        # Execute JavaScript and get result
        # (In practice, use QWebChannel for async communication)
        result_dict = self._execute_js_sync(js_code)

        if result_dict.get("success"):
            self._last_toc = result_dict.get("toc", [])
            return RenderResult(
                html=result_dict["html"],
                toc=self._last_toc
            )
        else:
            return RenderResult(
                html="",
                errors=[result_dict.get("error", "Unknown error")]
            )

    def set_theme(self, theme_data: dict[str, str]) -> None:
        """Apply theme by injecting CSS variables.

        Args:
            theme_data: CSS custom properties
                Example: {
                    "--md-fg": "#c9d1d9",
                    "--md-bg": "#0d1117",
                    "--md-code-bg": "#161b22",
                    "--md-code-fg": "#c9d1d9"
                }
        """
        if not self._initialized:
            return

        # Build CSS variable string
        css_vars = "; ".join(f"{k}: {v}" for k, v in theme_data.items())

        # Inject into document root
        js_code = f"""
        document.documentElement.style.cssText += "{css_vars};";
        """

        self._page.runJavaScript(js_code)

    def get_toc(self) -> list[dict]:
        """Get TOC from last render."""
        return self._last_toc.copy()

    def export_html(self, markdown: str, standalone: bool = True) -> str:
        """Export standalone HTML document.

        Args:
            markdown: Markdown source
            standalone: Include full HTML structure with CSS/JS

        Returns:
            Complete HTML document
        """
        # Render markdown
        result = self.render(markdown)

        if not standalone:
            return result.html

        # Build full HTML document
        html_template = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        {css}
    </style>
</head>
<body>
    <div id="content">
        {content}
    </div>
    <script>
        {js}
    </script>
</body>
</html>"""

        return html_template.format(
            css=self._get_export_css(),
            content=result.html,
            js=self._get_export_js()
        )

    def _execute_js_sync(self, js_code: str) -> dict:
        """Execute JavaScript synchronously (helper for example)."""
        # In practice, use QWebChannel for async communication
        # This is simplified for the design doc
        pass

    def _get_viewer_html_path(self) -> str:
        """Get path to viewer.html resource."""
        pass

    def _get_export_css(self) -> str:
        """Get CSS for standalone export."""
        pass

    def _get_export_js(self) -> str:
        """Get JavaScript for standalone export."""
        pass
```

---

### 2. PythonMarkdownRenderer (Future Implementation)

Pure Python renderer using `python-markdown` or `mistune` library.

```python
import markdown
from vfwidgets_markdown.renderers.base import (
    RendererProtocol,
    RendererCapabilities,
    RenderResult
)


class PythonMarkdownRenderer:
    """Pure Python markdown renderer using python-markdown library.

    Advantages:
    - No JavaScript required
    - Faster startup (no QWebEngineView initialization)
    - Easier to test (pure Python)
    - Can run in headless environments

    Disadvantages:
    - No live Mermaid diagram rendering
    - More limited syntax highlighting
    - No interactive features
    """

    def __init__(self):
        self._md = None
        self._last_toc = []

        self._capabilities = RendererCapabilities(
            supports_live_preview=True,
            supports_syntax_highlighting=True,  # Pygments
            supports_math=True,  # python-markdown-math
            supports_diagrams=False,  # No Mermaid
            supports_toc_extraction=True,
            supports_html_export=True,
            requires_javascript=False,
            extensions=[
                "extra",
                "codehilite",
                "toc",
                "tables",
                "fenced_code"
            ]
        )

    @property
    def capabilities(self) -> RendererCapabilities:
        return self._capabilities

    def initialize(self) -> None:
        """Initialize python-markdown instance."""
        self._md = markdown.Markdown(
            extensions=[
                "extra",
                "codehilite",
                "toc",
                "tables",
                "fenced_code"
            ],
            extension_configs={
                "codehilite": {
                    "css_class": "highlight",
                    "linenums": False
                }
            }
        )

    def shutdown(self) -> None:
        """Clean up."""
        self._md = None

    def render(self, markdown_text: str) -> RenderResult:
        """Render markdown to HTML using python-markdown.

        Args:
            markdown_text: Markdown source

        Returns:
            RenderResult with HTML
        """
        if not self._md:
            return RenderResult(html="", errors=["Renderer not initialized"])

        try:
            html = self._md.convert(markdown_text)

            # Extract TOC if available
            if hasattr(self._md, "toc_tokens"):
                self._last_toc = self._extract_toc(self._md.toc_tokens)

            # Reset for next render
            self._md.reset()

            return RenderResult(html=html, toc=self._last_toc)

        except Exception as e:
            return RenderResult(html="", errors=[str(e)])

    def set_theme(self, theme_data: dict[str, str]) -> None:
        """Store theme data for export (python-markdown doesn't handle themes).

        Args:
            theme_data: CSS custom properties (stored for export)
        """
        self._theme_data = theme_data

    def get_toc(self) -> list[dict]:
        """Get TOC from last render."""
        return self._last_toc.copy()

    def export_html(self, markdown_text: str, standalone: bool = True) -> str:
        """Export HTML with Pygments CSS.

        Args:
            markdown_text: Markdown source
            standalone: Include full HTML structure

        Returns:
            Complete HTML document with Pygments styling
        """
        result = self.render(markdown_text)

        if not standalone:
            return result.html

        # Include Pygments CSS
        from pygments.formatters import HtmlFormatter
        formatter = HtmlFormatter(style="monokai")
        pygments_css = formatter.get_style_defs(".highlight")

        html_template = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        {pygments_css}
        body {{
            font-family: -apple-system, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 40px auto;
            padding: 0 20px;
        }}
    </style>
</head>
<body>
    {content}
</body>
</html>"""

        return html_template.format(
            pygments_css=pygments_css,
            content=result.html
        )

    def _extract_toc(self, toc_tokens) -> list[dict]:
        """Extract TOC from python-markdown's toc extension."""
        toc = []
        for token in toc_tokens:
            toc.append({
                "level": token["level"],
                "text": token["name"],
                "id": token["id"]
            })
        return toc
```

---

## Usage in MarkdownViewer

### Widget Integration

```python
from vfwidgets_markdown.renderers.base import RendererProtocol
from vfwidgets_markdown.renderers.markdown_it import MarkdownItRenderer
from vfwidgets_markdown.renderers.python_markdown import PythonMarkdownRenderer


class MarkdownViewer(ThemedWidget, QWebEngineView):
    """Markdown viewer widget with pluggable renderer."""

    def __init__(self, renderer: Optional[RendererProtocol] = None, parent=None):
        """Initialize viewer.

        Args:
            renderer: Optional custom renderer. If None, uses default MarkdownItRenderer
            parent: Parent widget
        """
        super().__init__(parent)

        # Use provided renderer or default
        if renderer is None:
            page = QWebEnginePage(self)
            self._renderer = MarkdownItRenderer(page)
            self.setPage(page)
        else:
            self._renderer = renderer

        # Initialize renderer
        self._renderer.initialize()

    def set_markdown(self, markdown: str) -> None:
        """Set markdown content.

        Args:
            markdown: Markdown source text
        """
        result = self._renderer.render(markdown)

        if result.success:
            # Display HTML (method depends on renderer type)
            if self._renderer.capabilities.requires_javascript:
                # JavaScript renderer: already rendered in page
                pass
            else:
                # Python renderer: need to set HTML
                self.setHtml(result.html)

            # Update TOC
            if result.toc:
                self.toc_updated.emit(result.toc)
        else:
            # Show error
            logger.error(f"Rendering failed: {result.errors}")

    def on_theme_changed(self, theme=None) -> None:
        """Apply theme to renderer."""
        theme = theme or self.get_current_theme()
        if not theme:
            return

        # Build theme data from theme tokens
        theme_data = self._build_theme_data(theme)

        # Apply to renderer
        self._renderer.set_theme(theme_data)
```

### Example: Using Python Renderer

```python
# Create viewer with pure Python renderer (no JavaScript)
renderer = PythonMarkdownRenderer()
viewer = MarkdownViewer(renderer=renderer)

# Check capabilities
if viewer.renderer.capabilities.supports_diagrams:
    print("Mermaid diagrams supported")
else:
    print("No diagram support (pure Python renderer)")

# Set content
viewer.set_markdown("# Hello World\n\n```python\nprint('test')\n```")
```

---

## Testing Strategy

### Unit Tests for Renderers

```python
def test_markdown_it_renderer_basic():
    """Test markdown-it renderer basic functionality."""
    page = QWebEnginePage()
    renderer = MarkdownItRenderer(page)
    renderer.initialize()

    result = renderer.render("# Hello\n\nWorld")

    assert result.success
    assert "<h1" in result.html
    assert "Hello" in result.html
    assert "World" in result.html


def test_python_markdown_renderer_basic():
    """Test Python renderer basic functionality."""
    renderer = PythonMarkdownRenderer()
    renderer.initialize()

    result = renderer.render("# Hello\n\nWorld")

    assert result.success
    assert "<h1" in result.html
    assert "Hello" in result.html


def test_renderer_protocol_conformance():
    """Test that renderers conform to protocol."""
    from vfwidgets_markdown.renderers.base import RendererProtocol

    md_it = MarkdownItRenderer(QWebEnginePage())
    py_md = PythonMarkdownRenderer()

    assert isinstance(md_it, RendererProtocol)
    assert isinstance(py_md, RendererProtocol)
```

---

## Migration Path

### Phase 1: Extract Protocol (No Breaking Changes)
1. Create `renderers/` directory structure
2. Define `RendererProtocol` in `renderers/base.py`
3. Keep existing code in `markdown_viewer.py` unchanged

### Phase 2: Refactor Current Implementation
1. Extract markdown-it logic to `MarkdownItRenderer` class
2. Make `MarkdownViewer` use renderer internally
3. Maintain backward compatibility (same API)

### Phase 3: Add Alternative Implementations
1. Implement `PythonMarkdownRenderer`
2. Add renderer selection to examples
3. Document renderer trade-offs

---

## Benefits

### Immediate
- ✅ Clear separation of concerns (rendering vs. widget logic)
- ✅ Easier to test rendering in isolation
- ✅ Clear interface for theme application

### Long-term
- ✅ Support multiple markdown engines
- ✅ Easier to add new features (math, diagrams, etc.)
- ✅ Can swap to pure Python renderer for lightweight use cases
- ✅ Pattern applicable to other content-rendering widgets

---

## References

- **VS Code Webview API**: https://code.visualstudio.com/api/extension-guides/webview
- **python-markdown**: https://python-markdown.github.io/
- **markdown-it**: https://markdown-it.github.io/
- **Clean Architecture**: `/home/kuja/GitHub/vfwidgets/CleanArchitectureAsTheWay.md`
- **Terminal Widget Pattern**: `/home/kuja/GitHub/vfwidgets/widgets/terminal_widget/docs/terminal-theme-improvements-ANALYSIS.md`

---

**Status**: Design Complete - Ready for Implementation
**Next Steps**: Design ThemeBridge pattern, then implement Phase 1 extraction
