"""Implementation of MarkdownViewer widget."""

import json
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, QTimer, QUrl, Signal, Slot
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget

# Optional theme support
try:
    from vfwidgets_theme.widgets.base import ThemedWidget

    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False
    ThemedWidget = object


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


# Create base class dynamically based on theme availability
if THEME_AVAILABLE:
    _BaseClass = type("_BaseClass", (ThemedWidget, QWebEngineView), {})
else:
    _BaseClass = QWebEngineView


class MarkdownViewer(_BaseClass):
    """Markdown viewer widget with support for diagrams, syntax highlighting, and optional theming.

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
        scroll_position_changed(float): Emitted when scroll position changes (0.0-1.0)
        heading_clicked(str): Emitted when heading is clicked with heading ID
        link_clicked(str): Emitted when link is clicked with URL
    """

    # Define custom signals
    content_loaded = Signal()
    toc_changed = Signal(list)
    rendering_failed = Signal(str)
    viewer_ready = Signal()
    scroll_position_changed = Signal(float)
    heading_clicked = Signal(str)
    link_clicked = Signal(str)

    # Theme configuration - maps theme tokens to CSS variables
    theme_config = {
        "md_bg": "editor.background",
        "md_fg": "editor.foreground",
        "md_link": "textLink.foreground",
        "md_code_bg": "editor.code.background",
        "md_code_fg": "editor.code.foreground",
        "md_blockquote_border": "editor.blockquote.border",
        "md_blockquote_bg": "editor.blockquote.background",
        "md_table_border": "widget.border",
        "md_table_header_bg": "list.headerBackground",
    }

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
        self._base_path: Optional[Path] = None
        self._image_resolver: Optional[callable] = None

        # Editor integration state
        self._sync_mode = False
        self._saved_scroll_position: Optional[float] = None
        self._debounce_delay = 0
        self._debounce_timer: Optional[QTimer] = None
        self._pending_content: Optional[str] = None

        # Setup web engine
        self._setup_webengine()

        # Setup QWebChannel bridge
        self._setup_bridge()

        # Load HTML template
        self._load_template()

    def _setup_webengine(self) -> None:
        """Configure QWebEngineView and page settings."""
        # Create custom page with navigation handling
        from PySide6.QtGui import QDesktopServices
        from PySide6.QtWebEngineCore import QWebEngineProfile

        class MarkdownPage(QWebEnginePage):
            """Custom page that handles link navigation."""

            def acceptNavigationRequest(self, url, nav_type, is_main_frame):
                """Handle navigation requests - open external links in browser."""
                # Allow navigation to the initial page
                if url.toString().startswith("file://") or url.scheme() == "qrc":
                    return True

                # Open external links (http/https) in system browser
                if url.scheme() in ("http", "https"):
                    print(f"[MarkdownViewer] Opening external link: {url.toString()}")
                    QDesktopServices.openUrl(url)
                    return False  # Don't navigate in the view

                # Allow other schemes (data:, etc.)
                return True

            def javaScriptConsoleMessage(self, level, message, line_number, source_id):
                """Forward JavaScript console messages to Python console."""
                print(f"[JS Console] {message} (line {line_number})")

        page = MarkdownPage(self)
        self.setPage(page)

        # Configure settings
        settings = page.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, False)

        # Disable caching for development (allows resource updates without restart)
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

        elif msg_type == "scroll_position_changed":
            position = message.get("position", 0.0)
            self.scroll_position_changed.emit(position)

        elif msg_type == "heading_clicked":
            heading_id = message.get("heading_id", "")
            self.heading_clicked.emit(heading_id)

        elif msg_type == "link_clicked":
            url = message.get("url", "")
            self.link_clicked.emit(url)

        else:
            print(f"[MarkdownViewer] Unknown message type: {msg_type}")

    def set_markdown(self, content: str) -> None:
        """Set markdown content to render.

        Args:
            content: Markdown content string
        """
        self._current_markdown = content

        # Use debouncing if enabled
        if self._debounce_delay > 0 and self._debounce_timer is not None:
            self._pending_content = content
            self._debounce_timer.start(self._debounce_delay)
        else:
            self._render_markdown(content)

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

    def set_syntax_theme(self, theme: str) -> None:
        """Set syntax highlighting theme independently of main theme.

        Args:
            theme: Prism theme name (e.g., 'prism', 'prism-vscode-dark')
        """
        escaped_theme = json.dumps(theme)
        js_code = f"window.MarkdownViewer.setSyntaxTheme({escaped_theme});"
        self.page().runJavaScript(js_code)
        print(f"[MarkdownViewer] Syntax theme set to: {theme}")

    def on_theme_changed(self) -> None:
        """Called automatically when the theme changes (ThemedWidget callback).

        This method is called by the theme system when a theme change occurs.
        It updates the viewer's CSS variables based on the current theme.
        """
        if not THEME_AVAILABLE:
            return

        # Determine if we're using dark theme
        # Get theme from application
        is_dark = False
        try:
            from PySide6.QtWidgets import QApplication

            app = QApplication.instance()
            if app and hasattr(app, "get_current_theme"):
                current_theme = app.get_current_theme()
                if current_theme and hasattr(current_theme, "type"):
                    is_dark = current_theme.type == "dark"
        except Exception:
            pass  # Fallback to light theme

        # Update JavaScript viewer theme
        theme_name = "dark" if is_dark else "light"
        self.set_theme(theme_name)

        # Inject CSS variables from theme
        if hasattr(self, "theme"):
            css_vars = "\n".join(
                [
                    f"--{key.replace('_', '-')}: {getattr(self.theme, key)};"
                    for key in self.theme_config.keys()
                    if hasattr(self.theme, key) and getattr(self.theme, key) is not None
                ]
            )

            # Escape CSS vars for safe JavaScript embedding
            escaped_css_vars = (
                css_vars.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
            )

            js_code = f"""
            (function() {{
                var style = document.getElementById('theme-vars');
                if (!style) {{
                    style = document.createElement('style');
                    style.id = 'theme-vars';
                    document.head.appendChild(style);
                }}
                style.textContent = ':root {{ {escaped_css_vars} }}';
            }})();
            """
            self.page().runJavaScript(js_code)
            print(f"[MarkdownViewer] Theme updated to: {theme_name}")

    def is_ready(self) -> bool:
        """Check if viewer is ready to render.

        Returns:
            True if viewer is ready, False otherwise
        """
        return self._is_ready

    def set_base_path(self, path: str) -> None:
        """Set base path for resolving relative image paths.

        Args:
            path: Directory path to use as base for relative images
        """
        self._base_path = Path(path).resolve()
        print(f"[MarkdownViewer] Base path set to: {self._base_path}")

    def set_image_resolver(self, resolver: callable) -> None:
        """Set custom image resolver callback.

        The resolver is called for each image in the markdown with the image
        source as argument. It should return the resolved path/URL.

        Args:
            resolver: Callable that takes (src: str) and returns resolved path/URL

        Example:
            def my_resolver(src: str) -> str:
                if src.startswith("asset://"):
                    return f"/path/to/assets/{src[8:]}"
                return src

            viewer.set_image_resolver(my_resolver)
        """
        self._image_resolver = resolver
        print("[MarkdownViewer] Custom image resolver set")

    def _resolve_image_path(self, src: str) -> str:
        """Resolve image path using base_path and custom resolver.

        Args:
            src: Image source from markdown

        Returns:
            Resolved image path/URL
        """
        # If custom resolver is set, use it first
        if self._image_resolver:
            resolved = self._image_resolver(src)
            if resolved != src:
                print(f"[MarkdownViewer] Resolved '{src}' -> '{resolved}' (custom resolver)")
                return resolved

        # Handle absolute URLs (http://, https://, data:)
        if src.startswith(("http://", "https://", "data:")):
            return src

        # Handle absolute file paths
        if Path(src).is_absolute():
            return QUrl.fromLocalFile(src).toString()

        # Handle relative paths with base_path
        if self._base_path:
            resolved_path = (self._base_path / src).resolve()
            if resolved_path.exists():
                url = QUrl.fromLocalFile(str(resolved_path)).toString()
                print(f"[MarkdownViewer] Resolved '{src}' -> '{url}' (base_path)")
                return url
            else:
                print(f"[MarkdownViewer] Warning: Image not found: {resolved_path}")

        # Return as-is if no resolution possible
        return src

    def _preprocess_images(self, content: str) -> str:
        """Pre-process markdown content to resolve image paths.

        Args:
            content: Markdown content

        Returns:
            Content with resolved image paths
        """
        import re

        # Match markdown image syntax: ![alt](src "title") or ![alt](src)
        pattern = r'!\[([^\]]*)\]\(([^)]+?)(?:\s+"([^"]*)")?\)'

        def replace_image(match):
            alt_text = match.group(1)
            src = match.group(2).strip()
            title = match.group(3)

            # Resolve the image path
            resolved_src = self._resolve_image_path(src)

            # Reconstruct the markdown image syntax
            if title:
                return f'![{alt_text}]({resolved_src} "{title}")'
            else:
                return f"![{alt_text}]({resolved_src})"

        processed = re.sub(pattern, replace_image, content)
        return processed

    def enable_sync_mode(self, enabled: bool = True) -> None:
        """Enable sync mode to preserve scroll position during updates.

        When enabled, the viewer will restore the scroll position after
        rendering new content. Useful for live preview scenarios.

        Args:
            enabled: True to enable sync mode, False to disable
        """
        self._sync_mode = enabled
        print(f"[MarkdownViewer] Sync mode: {'enabled' if enabled else 'disabled'}")

    def set_debounce_delay(self, delay_ms: int) -> None:
        """Set debounce delay for content updates.

        When set, content updates are delayed by the specified amount.
        Useful for live preview to avoid updating on every keystroke.

        Args:
            delay_ms: Delay in milliseconds (0 to disable debouncing)
        """
        self._debounce_delay = delay_ms

        if delay_ms > 0 and self._debounce_timer is None:
            self._debounce_timer = QTimer()
            self._debounce_timer.setSingleShot(True)
            self._debounce_timer.timeout.connect(self._apply_pending_content)

        print(f"[MarkdownViewer] Debounce delay set to {delay_ms}ms")

    def _apply_pending_content(self) -> None:
        """Apply pending content after debounce delay."""
        if self._pending_content is not None:
            content = self._pending_content
            self._pending_content = None
            self._render_markdown(content)

    def _render_markdown(self, content: str) -> None:
        """Internal method to render markdown content.

        Args:
            content: Markdown content to render
        """
        # Save scroll position if sync mode is enabled
        if self._sync_mode:
            js_code = "window.MarkdownViewer.getScrollPosition();"
            self.page().runJavaScript(
                js_code, lambda pos: setattr(self, "_saved_scroll_position", pos)
            )

        # Pre-process images if base_path or resolver is set
        if self._base_path or self._image_resolver:
            content = self._preprocess_images(content)

        # Escape content for JavaScript
        escaped_content = json.dumps(content)

        # Call JavaScript render function
        js_code = f"window.MarkdownViewer.render({escaped_content});"
        self.page().runJavaScript(js_code)

        # Restore scroll position if sync mode is enabled
        if self._sync_mode and self._saved_scroll_position is not None:
            restore_js = f"window.MarkdownViewer.setScrollPosition({self._saved_scroll_position});"
            # Use a small delay to ensure content is rendered first
            QTimer.singleShot(50, lambda: self.page().runJavaScript(restore_js))

        print(f"[MarkdownViewer] Rendering {len(content)} bytes of markdown")
