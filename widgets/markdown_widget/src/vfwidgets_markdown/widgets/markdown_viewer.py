"""Implementation of MarkdownViewer widget."""

import json
import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, Qt, QTimer, QUrl, Signal, Slot
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget

# Import Phase 1 components
from vfwidgets_common.webview import WebViewHost  # Now from vfwidgets_common!

from vfwidgets_markdown.bridges.theme_bridge import (
    ThemeBridge,
    ThemeTokenMapping,
)

# Import model for architecture integration
from vfwidgets_markdown.models import MarkdownDocument

logger = logging.getLogger(__name__)

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
            logger.error(f"Invalid JSON from JavaScript: {e}")


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

    Async Initialization:
        This widget uses QWebEngineView which initializes asynchronously.
        **You don't need to worry about this** - the widget automatically queues
        content until ready. All methods are safe to call immediately after construction.

    Quick Start:
        # Simple usage - content in constructor
        viewer = MarkdownViewer(initial_content="# Hello World")

        # Or set content after creation (automatically queued)
        viewer = MarkdownViewer()
        viewer.set_markdown("# Hello")  # Safe to call immediately

        # Or load from file
        viewer = MarkdownViewer()
        viewer.load_file("README.md")  # Automatic base path handling

    When to use viewer_ready signal:
        Most applications don't need to handle viewer_ready explicitly.
        Connect to it only if you need to perform actions exactly when
        rendering completes or want to show a loading indicator.

    Signals:
        content_loaded: Emitted when markdown rendering completes
        toc_changed(list): Emitted when table of contents changes
        rendering_failed(str): Emitted when rendering fails with error message
        viewer_ready: Emitted when viewer is initialized and ready
        scroll_position_changed(float): Emitted when scroll position changes (0.0-1.0)
        heading_clicked(str): Emitted when heading is clicked with heading ID
        link_clicked(str): Emitted when link is clicked with URL
        shortcut_triggered(str, str): Emitted when custom shortcut is triggered (action, combo)
    """

    # Define custom signals
    content_loaded = Signal()
    toc_changed = Signal(list)
    rendering_failed = Signal(str)
    viewer_ready = Signal()
    scroll_position_changed = Signal(float)
    heading_clicked = Signal(str)
    link_clicked = Signal(str)
    shortcut_triggered = Signal(str, str)  # (action, combo)

    # Theme configuration - maps theme tokens to CSS variables
    # Theme configuration with widget-specific tokens and fallbacks
    # Uses hierarchical resolution: markdown.colors.* → generic tokens
    # Similar to terminal widget's pattern for better theme customization
    theme_config = {
        "md_bg": "markdown.colors.background",
        "md_fg": "markdown.colors.foreground",
        "md_link": "markdown.colors.link",
        "md_code_bg": "markdown.colors.code.background",
        "md_code_fg": "markdown.colors.code.foreground",
        "md_blockquote_border": "markdown.colors.blockquote.border",
        "md_blockquote_bg": "markdown.colors.blockquote.background",
        "md_table_border": "markdown.colors.table.border",
        "md_table_header_bg": "markdown.colors.table.headerBackground",
        "md_scrollbar_bg": "markdown.colors.scrollbar.background",
        "md_scrollbar_thumb": "markdown.colors.scrollbar.thumb",
        "md_scrollbar_thumb_hover": "markdown.colors.scrollbar.thumbHover",
    }

    def __init__(
        self,
        document: Optional[MarkdownDocument] = None,
        initial_content: str = "",
        base_path: Optional[Path] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize the MarkdownViewer.

        The viewer uses an auto-wrapping pattern:
        - If no document is provided, creates an internal document (simple mode)
        - If document is provided, uses external document (architecture mode)

        In both cases, the viewer observes the document via observer pattern.

        Content can be provided in the constructor and will be loaded automatically
        when the viewer is ready (no need to manually handle viewer_ready signal).

        Args:
            document: Optional MarkdownDocument to observe. If None, creates internal document.
            initial_content: Markdown content to load when viewer is ready
            base_path: Base path for resolving relative image URLs
            parent: Parent widget

        Example:
            # Simple usage with initial content
            viewer = MarkdownViewer(initial_content="# Hello World")

            # With base path for images
            viewer = MarkdownViewer(
                initial_content="# Project\\n\\n![logo](logo.png)",
                base_path=Path("/path/to/project")
            )
        """
        super().__init__(parent)

        # Auto-wrapping: Always use a document (internal or external)
        if document:
            # Advanced mode - use external document
            self._document = document
            self._owns_document = False
        else:
            # Simple mode - create internal document
            self._document = MarkdownDocument()
            self._owns_document = True

        # Always observe the document (Python observer pattern)
        self._document.add_observer(self)

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

        # Content queueing for async initialization
        self._pending_render: Optional[str] = None
        self._pending_base_path: Optional[Path] = None

        # Theme queueing for async initialization
        # Store theme when on_theme_changed() is called before viewer is ready
        self._pending_theme = None

        # Keyboard shortcuts state
        self._shortcuts_enabled = False
        self._custom_shortcuts: dict = {}

        # Setup WebViewHost (Phase 1 component)
        # Enable remote access for markdown-it CDN resources
        self._host = WebViewHost(self)
        page = self._host.initialize(allow_remote_access=True)
        self.setPage(page)

        # Configure transparency (3-layer pattern)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent")
        self._host.set_transparent(True)

        # Setup custom page for link navigation
        self._setup_custom_page()

        # Setup QWebChannel bridge for JavaScript communication
        self._bridge = JavaScriptBridge(self)
        self._bridge.message_received.connect(self._on_javascript_message)
        self._host.register_bridge_object("qtBridge", self._bridge)

        # Setup ThemeBridge (Phase 1 component) if theme support available
        if THEME_AVAILABLE:
            self._theme_bridge = ThemeBridge(
                page=self._host.get_page(),
                token_mappings=self._build_theme_token_mappings(),
                css_injection_callback=self._build_prism_override_css,
            )

        # Load HTML template
        self._load_template()

        # Apply theme when viewer is ready (for QWebEngineView async initialization)
        if THEME_AVAILABLE:
            self.viewer_ready.connect(
                self._apply_initial_theme, Qt.ConnectionType.SingleShotConnection
            )

        # Set initial content and base path if provided
        # These will be queued until viewer is ready
        if base_path:
            self.set_base_path(str(base_path))
        if initial_content:
            self.set_markdown(initial_content)

    def _build_theme_token_mappings(self) -> list[ThemeTokenMapping]:
        """Build ThemeTokenMapping list from theme_config.

        Returns:
            List of ThemeTokenMapping objects with fallback chains
        """
        # Define fallback mappings (copied from old _get_color_with_fallback)
        fallback_map = {
            "markdown.colors.background": ["editor.background", "colors.background"],
            "markdown.colors.foreground": ["editor.foreground", "colors.foreground"],
            "markdown.colors.link": ["button.background", "colors.foreground"],
            "markdown.colors.code.background": ["input.background", "widget.background"],
            "markdown.colors.code.foreground": ["input.foreground", "colors.foreground"],
            "markdown.colors.blockquote.border": ["widget.border", "colors.border"],
            "markdown.colors.blockquote.background": [
                "widget.background",
                "editor.background",
            ],
            "markdown.colors.table.border": ["widget.border", "colors.border"],
            "markdown.colors.table.headerBackground": [
                "editor.lineHighlightBackground",
                "widget.background",
            ],
            "markdown.colors.scrollbar.background": ["editor.background", "colors.background"],
            "markdown.colors.scrollbar.thumb": [
                "scrollbar.activeBackground",
                "widget.border",
            ],
            "markdown.colors.scrollbar.thumbHover": [
                "scrollbar.hoverBackground",
                "scrollbar.activeBackground",
            ],
        }

        mappings = []
        for css_var_name, token_path in self.theme_config.items():
            # Convert underscore to kebab-case for CSS variables
            css_var = css_var_name.replace("_", "-")

            # Get fallback paths for this token
            fallback_paths = fallback_map.get(token_path, [])

            mappings.append(
                ThemeTokenMapping(
                    css_var=css_var,
                    token_path=token_path,
                    fallback_paths=fallback_paths,
                    default_value=None,  # No hard defaults
                )
            )

        return mappings

    def _build_prism_override_css(self, css_vars: dict) -> str:
        """Build Prism.js override CSS to apply theme colors to code blocks.

        This is passed to ThemeBridge as the css_injection_callback.

        Args:
            css_vars: CSS variables that were set (dict of --var-name: value)

        Returns:
            CSS string to override Prism.js hardcoded backgrounds
        """
        # Maximum specificity override for Prism.js
        return """
            /* Override Prism.js hardcoded backgrounds with maximum specificity */
            body #content pre[class*="language-"],
            body #content pre.language-,
            body pre[class*="language-"],
            pre[class*="language-"] {
                background-color: var(--md-code-bg) !important;
                background: var(--md-code-bg) !important;
            }

            body #content code[class*="language-"],
            body code[class*="language-"],
            code[class*="language-"] {
                background-color: transparent !important;
                background: transparent !important;
                color: var(--md-code-fg) !important;
            }

            body #content :not(pre) > code[class*="language-"],
            :not(pre) > code[class*="language-"] {
                background-color: var(--md-code-bg) !important;
                background: var(--md-code-bg) !important;
            }

            /* Override regular code blocks (non-Prism) with maximum specificity */
            body #content pre,
            #content pre {
                background-color: var(--md-code-bg) !important;
                background: var(--md-code-bg) !important;
            }

            body #content code,
            #content code {
                background-color: var(--md-code-bg) !important;
                background: var(--md-code-bg) !important;
                color: var(--md-code-fg) !important;
            }

            body #content pre code,
            #content pre code {
                background-color: transparent !important;
                background: transparent !important;
            }
        """

    def _setup_custom_page(self) -> None:
        """Setup custom QWebEnginePage for link navigation handling.

        This replaces the default page with a custom one that opens external
        links in the system browser instead of navigating in the view.
        """
        from PySide6.QtGui import QDesktopServices
        from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile

        # Get the current page created by WebViewHost
        original_page = self.page()

        class MarkdownPage(QWebEnginePage):
            """Custom page that handles link navigation."""

            def acceptNavigationRequest(self, url, nav_type, is_main_frame):
                """Handle navigation requests - open external links in browser."""
                # Allow navigation to the initial page
                if url.toString().startswith("file://") or url.scheme() == "qrc":
                    return True

                # Open external links (http/https) in system browser
                if url.scheme() in ("http", "https"):
                    logger.debug(f"Opening external link: {url.toString()}")
                    QDesktopServices.openUrl(url)
                    return False  # Don't navigate in the view

                # Allow other schemes (data:, etc.)
                return True

            def javaScriptConsoleMessage(self, level, message, line_number, source_id):
                """Forward JavaScript console messages to Python console."""
                logger.debug(f"[JS Console] {message} (line {line_number})")

        # Create custom page with same parent
        custom_page = MarkdownPage(self)

        # Copy settings from original page
        from PySide6.QtWebEngineCore import QWebEngineSettings

        custom_settings = custom_page.settings()

        custom_settings.setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True
        )
        custom_settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        custom_settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)

        # Disable caching for development
        profile = custom_page.profile()
        profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.NoCache)

        # Set transparency
        custom_page.setBackgroundColor(Qt.GlobalColor.transparent)

        # Copy web channel from original page
        custom_page.setWebChannel(original_page.webChannel())

        # Replace the page
        self.setPage(custom_page)

        # Update host's internal reference
        self._host._page = custom_page

        logger.debug("Custom page setup complete")

    def _load_template(self) -> None:
        """Load the HTML template via renderer."""
        from vfwidgets_markdown.renderers.markdown_it import MarkdownItRenderer

        # Create renderer
        self._renderer = MarkdownItRenderer(self._host.get_page())

        try:
            self._renderer.initialize()
            logger.debug("Renderer initialized successfully")
        except Exception as e:
            error_msg = f"Failed to initialize renderer: {e}"
            logger.error(error_msg)
            self.rendering_failed.emit(error_msg)

    @Slot(dict)
    def _on_javascript_message(self, message: dict) -> None:
        """Handle messages from JavaScript.

        Args:
            message: Message dictionary from JavaScript
        """
        msg_type = message.get("type")

        if msg_type == "ready":
            self._is_ready = True
            logger.info("Viewer ready")

            # Process any pending base path
            if self._pending_base_path is not None:
                logger.debug(f"Setting pending base path: {self._pending_base_path}")
                self._base_path = self._pending_base_path
                self._pending_base_path = None

            # Process any pending content
            if self._pending_render is not None:
                logger.debug(f"Rendering pending content ({len(self._pending_render)} chars)")
                content_to_render = self._pending_render
                self._pending_render = None
                self._render_markdown(content_to_render)

            self.viewer_ready.emit()

        elif msg_type == "content_loaded":
            self.content_loaded.emit()
            logger.debug("Content loaded")

        elif msg_type == "toc_changed":
            self._current_toc = message.get("data", [])
            self.toc_changed.emit(self._current_toc)
            logger.debug(f"TOC updated: {len(self._current_toc)} headings")

        elif msg_type == "rendering_failed":
            error = message.get("error", "Unknown error")
            self.rendering_failed.emit(error)
            logger.error(f"Rendering failed: {error}")

        elif msg_type == "scroll_position_changed":
            position = message.get("position", 0.0)
            self.scroll_position_changed.emit(position)

        elif msg_type == "heading_clicked":
            heading_id = message.get("heading_id", "")
            self.heading_clicked.emit(heading_id)

        elif msg_type == "link_clicked":
            url = message.get("url", "")
            self.link_clicked.emit(url)

        elif msg_type == "shortcut_triggered":
            action = message.get("action", "")
            combo = message.get("combo", "")
            self.shortcut_triggered.emit(action, combo)

        else:
            print(f"[MarkdownViewer] Unknown message type: {msg_type}")

    def on_document_changed(self, event) -> None:
        """Observer callback - called when document changes.

        This is a Python observer method, NOT a Qt slot.
        It's called directly by the model's _notify_observers().

        This method handles both TextReplaceEvent and TextAppendEvent,
        and applies debouncing if enabled.

        Args:
            event: TextReplaceEvent, TextAppendEvent, or SectionUpdateEvent
        """
        # Get the full text from the document
        content = self._document.get_text()
        self._current_markdown = content

        # Use debouncing if enabled
        if self._debounce_delay > 0 and self._debounce_timer is not None:
            self._pending_content = content
            self._debounce_timer.start(self._debounce_delay)
        else:
            self._render_markdown(content)

    def set_markdown(self, content: str) -> None:
        """Set markdown content to render.

        This method is safe to call immediately after widget creation.
        If the viewer is not yet ready, content will be queued and rendered
        automatically when initialization completes.

        This method works in both simple and advanced modes:
        - Simple mode: Updates internal document, which triggers observer
        - Advanced mode: Updates external document, which triggers observer

        Args:
            content: Markdown content string

        Example:
            viewer = MarkdownViewer()
            viewer.set_markdown("# Hello")  # Safe - content queued if not ready
        """
        # Update the document (triggers observer callback)
        self._document.set_text(content)

    def load_file(self, path: str | Path) -> bool:
        """Load markdown content from a file.

        This is a convenience method that:
        1. Reads the file
        2. Sets the markdown content
        3. Sets the base path for relative URLs

        Safe to call immediately after widget creation - content will be
        queued if viewer is not ready.

        Args:
            path: Path to markdown file (string or Path object)

        Returns:
            True if file was loaded successfully, False otherwise

        Example:
            viewer = MarkdownViewer()
            success = viewer.load_file("README.md")
            if not success:
                print("Failed to load file")
        """
        try:
            file_path = Path(path)
            content = file_path.read_text(encoding="utf-8")
            self.set_markdown(content)
            self.set_base_path(str(file_path.parent))
            print(f"[MarkdownViewer] Loaded file: {path}")
            return True
        except Exception as e:
            error_msg = f"Failed to load file {path}: {e}"
            logger.error(error_msg)
            self.rendering_failed.emit(error_msg)
            return False

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
        logger.debug(f"Theme set to: {theme}")

    def set_syntax_theme(self, theme: str) -> None:
        """Set syntax highlighting theme independently of main theme.

        Args:
            theme: Prism theme name (e.g., 'prism', 'prism-vscode-dark')
        """
        escaped_theme = json.dumps(theme)
        js_code = f"window.MarkdownViewer.setSyntaxTheme({escaped_theme});"
        self.page().runJavaScript(js_code)
        print(f"[MarkdownViewer] Syntax theme set to: {theme}")

    def on_theme_changed(self, theme=None) -> None:
        """Called automatically when the theme changes (ThemedWidget callback).

        This method is called by the theme system when a theme change occurs.
        It updates the viewer's CSS variables based on the current theme.

        Args:
            theme: Optional Theme object. If not provided, uses get_current_theme() from ThemedWidget.

        Note: This method may be called before the viewer is ready. If not ready,
        the theme will be applied when viewer_ready signal is emitted.
        """
        if not THEME_AVAILABLE:
            return

        # Store theme for deferred application if viewer isn't ready yet
        # This handles the case where Theme Studio calls on_theme_changed() before
        # the viewer finishes loading
        #
        # IMPORTANT: Don't overwrite existing pending theme with None!
        # ThemedWidget base class may call on_theme_changed(None) after Theme Studio
        # has already set a valid theme. We must preserve the valid theme.
        if theme is not None:
            self._pending_theme = theme
            logger.debug(f"Stored pending theme: {theme.name}")
        elif self._pending_theme is not None:
            logger.debug(f"Keeping existing pending theme: {self._pending_theme.name}")
        else:
            logger.debug("No theme parameter and no pending theme")

        # Don't apply theme if viewer not ready yet - will be applied via viewer_ready signal
        if not self._is_ready:
            logger.debug("Viewer not ready, deferring theme application")
            return

        # Use provided theme, pending theme, or get from widget's theme manager
        if theme is None:
            if self._pending_theme is not None:
                theme = self._pending_theme
                logger.debug(f"Using pending theme: {theme.name}")
            else:
                theme = self.get_current_theme()
                logger.debug(f"Got theme from widget: {theme.name}")

        if not theme or not hasattr(theme, "colors"):
            logger.warning("No theme available for markdown viewer")
            return

        # Determine if we're using dark theme
        is_dark = False
        if theme and hasattr(theme, "type"):
            is_dark = theme.type == "dark"

        # Update JavaScript viewer theme (light/dark mode)
        theme_name = "dark" if is_dark else "light"
        self.set_theme(theme_name)

        # Delegate CSS variable injection to ThemeBridge
        result = self._theme_bridge.apply_theme(theme)

        if not result.success:
            logger.error(f"Theme application failed: {result.errors}")
        elif result.missing_tokens:
            logger.warning(f"Missing theme tokens: {result.missing_tokens}")
        else:
            logger.info(
                f"Theme updated to: {theme_name} with {len(result.css_variables_set)} CSS variables"
            )

    def _apply_initial_theme(self) -> None:
        """Apply initial theme when viewer is ready.

        This is connected to viewer_ready signal with SingleShot to apply
        theme once the QWebEngineView is fully initialized and ready to
        receive JavaScript commands.
        """
        logger.debug("Applying initial theme (viewer is ready)")
        self.on_theme_changed()

    def is_ready(self) -> bool:
        """Check if viewer is ready to render.

        Returns:
            True if viewer is ready, False otherwise
        """
        return self._is_ready

    def set_base_path(self, path: str) -> None:
        """Set base path for resolving relative image paths.

        Safe to call before viewer is ready - will be applied when ready.

        Args:
            path: Directory path to use as base for relative images
        """
        resolved_path = Path(path).resolve()

        if not self._is_ready:
            print(f"[MarkdownViewer] Viewer not ready, queueing base path: {resolved_path}")
            self._pending_base_path = resolved_path
        else:
            self._base_path = resolved_path
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

        If viewer is not ready, content is queued and will be rendered
        automatically when initialization completes.

        Args:
            content: Markdown content to render
        """
        # Queue content if viewer is not ready yet
        if not self._is_ready:
            logger.debug(f"Viewer not ready, queueing content ({len(content)} chars)")
            self._pending_render = content
            return

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

        logger.debug(f"Rendering {len(content)} bytes of markdown")

    def enable_shortcuts(self, enabled: bool = True) -> None:
        """Enable built-in keyboard shortcuts.

        Built-in shortcuts:
        - Ctrl/Cmd+F: Find in page
        - Ctrl/Cmd+Plus: Zoom in
        - Ctrl/Cmd+Minus: Zoom out
        - Ctrl/Cmd+0: Reset zoom
        - Home: Scroll to top
        - End: Scroll to bottom
        - PageUp/PageDown: Scroll by page
        - Escape: Clear search/selection

        Args:
            enabled: True to enable shortcuts, False to disable
        """
        self._shortcuts_enabled = enabled
        js_code = f"window.MarkdownViewer.enableShortcuts({json.dumps(enabled)});"
        self.page().runJavaScript(js_code)
        print(f"[MarkdownViewer] Shortcuts: {'enabled' if enabled else 'disabled'}")

    def set_custom_shortcuts(self, shortcuts: dict) -> None:
        """Set custom keyboard shortcuts.

        Args:
            shortcuts: Dictionary mapping key combinations to actions
                      Format: {"Ctrl+K": "custom_action", ...}

        Example:
            viewer.set_custom_shortcuts({
                "Ctrl+K": "toggle_theme",
                "Ctrl+B": "toggle_sidebar"
            })
        """
        self._custom_shortcuts = shortcuts
        js_code = f"window.MarkdownViewer.setCustomShortcuts({json.dumps(shortcuts)});"
        self.page().runJavaScript(js_code)
        print(f"[MarkdownViewer] Custom shortcuts set: {len(shortcuts)} bindings")

    def export_html(
        self, file_path: str, include_styles: bool = True, callback: callable = None
    ) -> None:
        """Export rendered content to HTML file.

        Args:
            file_path: Path to save HTML file
            include_styles: Include CSS styles in export (default: True)
            callback: Optional callback when export completes

        Example:
            viewer.export_html("output.html")
            viewer.export_html("output.html", include_styles=False)
        """

        def handle_html(html: str):
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(html)
                print(f"[MarkdownViewer] Exported HTML to: {file_path}")
                if callback:
                    callback(True, file_path)
            except Exception as e:
                print(f"[MarkdownViewer] Export failed: {e}")
                if callback:
                    callback(False, str(e))

        if include_styles:
            js_code = "window.MarkdownViewer.getFullHTML();"
        else:
            js_code = "window.MarkdownViewer.getRenderedHTML();"

        self.page().runJavaScript(js_code, handle_html)

    def export_pdf(self, file_path: str, callback: callable = None) -> None:
        """Export rendered content to PDF file.

        Uses Qt's PDF printing functionality.

        Args:
            file_path: Path to save PDF file
            callback: Optional callback when export completes

        Example:
            viewer.export_pdf("output.pdf")
        """
        from PySide6.QtCore import QMarginsF
        from PySide6.QtGui import QPageLayout, QPageSize
        from PySide6.QtPrintSupport import QPrinter

        def handle_pdf(success: bool):
            if success:
                print(f"[MarkdownViewer] Exported PDF to: {file_path}")
                if callback:
                    callback(True, file_path)
            else:
                print("[MarkdownViewer] PDF export failed")
                if callback:
                    callback(False, "PDF generation failed")

        try:
            # Create printer
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(file_path)

            # Set page layout
            page_layout = QPageLayout(
                QPageSize(QPageSize.A4), QPageLayout.Portrait, QMarginsF(15, 15, 15, 15)
            )
            printer.setPageLayout(page_layout)

            # Print to PDF
            self.page().printToPdf(file_path)
            handle_pdf(True)

        except Exception as e:
            print(f"[MarkdownViewer] PDF export error: {e}")
            handle_pdf(False)

    def closeEvent(self, event):
        """Handle widget closing - remove observer to prevent memory leaks."""
        self._document.remove_observer(self)
        super().closeEvent(event)


# ============================================================================
# Theme Studio Integration - Plugin Discovery
# ============================================================================


def get_preview_metadata():
    """Get preview metadata for Theme Studio plugin discovery.

    This function is called by Theme Studio's plugin discovery system via
    entry points to automatically register the markdown viewer widget as a
    preview plugin.

    Returns:
        WidgetMetadata: Metadata describing the markdown viewer for preview
    """
    from vfwidgets_theme import PluginAvailability, WidgetMetadata

    def create_preview_markdown_viewer(parent=None):
        """Create a markdown viewer configured for preview.

        Args:
            parent: Parent widget

        Returns:
            MarkdownViewer configured for preview mode with sample content
        """
        from PySide6.QtWidgets import QSizePolicy

        # Create sample markdown content to showcase theme colors
        sample_content = """# Markdown Preview

This is a **live preview** of how markdown content looks with the current theme.

## Features Demonstrated

- **Bold text** and *italic text*
- [Links](https://example.com) with theme colors
- `inline code` with background

### Code Blocks

```python
def hello_world():
    print("Hello from themed markdown!")
    return True
```

### Lists

1. First item
2. Second item
3. Third item

- Bullet point
- Another point
  - Nested item

### Blockquote

> This is a blockquote demonstrating the theme's blockquote styling.
> Multiple lines show how the theme handles quote borders and backgrounds.

### Table

| Feature | Status |
|---------|--------|
| Headers | ✓ |
| Rows    | ✓ |
| Styling | ✓ |

---

Try changing themes to see how the markdown content adapts!
"""

        # Create viewer with sample content
        viewer = MarkdownViewer(initial_content=sample_content, parent=parent)

        # Make viewer expand to fill available space
        viewer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        return viewer

    # Define theme tokens used by markdown viewer
    # Declares BASE tokens for validation and widget-specific tokens for Theme Studio
    # The actual theme resolution happens in on_theme_changed() via theme_config with fallbacks
    # Similar pattern to terminal widget which uses hierarchical resolution
    theme_tokens = {
        # Base tokens (REQUIRED - all widgets inherit these)
        "background": "colors.background",
        "foreground": "colors.foreground",
    }

    return WidgetMetadata(
        name="Markdown Viewer",
        widget_class_name="MarkdownViewer",
        package_name="vfwidgets_markdown",
        version="2.0.0",
        theme_tokens=theme_tokens,
        required_tokens=[
            "colors.background",
            "colors.foreground",
        ],
        optional_tokens=[
            # Widget-specific markdown tokens (primary)
            "markdown.colors.background",
            "markdown.colors.foreground",
            "markdown.colors.link",
            "markdown.colors.code.background",
            "markdown.colors.code.foreground",
            "markdown.colors.blockquote.border",
            "markdown.colors.blockquote.background",
            "markdown.colors.table.border",
            "markdown.colors.table.headerBackground",
            "markdown.colors.scrollbar.background",
            "markdown.colors.scrollbar.thumb",
            "markdown.colors.scrollbar.thumbHover",
            # Fallback tokens (used if markdown.* not defined)
            "editor.background",
            "editor.foreground",
            "button.background",
            "input.background",
            "input.foreground",
            "widget.border",
            "widget.background",
            "editor.lineHighlightBackground",
            "scrollbar.activeBackground",
            "scrollbar.hoverBackground",
        ],
        preview_factory=create_preview_markdown_viewer,
        availability=PluginAvailability.AVAILABLE,
    )
