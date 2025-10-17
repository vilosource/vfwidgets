"""QWebChannel bridge for ViloWeb - Python↔JavaScript communication.

Educational Focus:
    This module demonstrates:
    - QWebChannel bridge architecture
    - Exposing Python functionality to JavaScript
    - Bi-directional communication patterns
    - Signal-based event handling

    The bridge allows JavaScript on web pages to call Python methods
    and receive notifications from Python code.

Architecture:
    ViloWebBridge is a QObject with @Slot methods that JavaScript can call.
    It emits signals when events occur, allowing the main window to react.

Example JavaScript Usage:
    // Available after WebChannelHelper.setup_channel(browser, bridge, "viloWeb")
    window.viloWeb.log_from_js("info", "Hello from JavaScript!");
    window.viloWeb.bookmark_current_page();
    window.viloWeb.request_theme_info();
"""

import logging
from typing import Optional

from PySide6.QtCore import QObject, Signal, Slot

logger = logging.getLogger(__name__)


class ViloWebBridge(QObject):
    """Python↔JavaScript bridge for ViloWeb browser.

    Educational Note:
        This class exposes Python functionality to JavaScript via QWebChannel.
        All public methods marked with @Slot can be called from JavaScript.

        Pattern:
        - JavaScript calls Python: window.viloWeb.method_name(args)
        - Python notifies JavaScript: Emit signals, JS listens via QWebChannel

        Security Note:
            Be careful what you expose! Any JavaScript on ANY page can call
            these methods. Never expose file system operations, command execution,
            or sensitive data without proper validation.

    Signals:
        bookmark_requested: User clicked "bookmark" from page JavaScript
        log_message: JavaScript wants to log a message to Python console

    Example:
        >>> bridge = ViloWebBridge()
        >>> bridge.bookmark_requested.connect(lambda: print("Bookmark requested!"))
        >>> channel = WebChannelHelper.setup_channel(browser, bridge, "viloWeb")
        >>> # JavaScript can now call: window.viloWeb.bookmark_current_page()
    """

    # Signals for notifying Python code
    bookmark_requested = Signal()  # User wants to bookmark current page
    log_message = Signal(str, str)  # (level, message) - JS wants to log

    def __init__(self, parent: Optional[QObject] = None):
        """Initialize ViloWeb bridge.

        Args:
            parent: Parent QObject
        """
        super().__init__(parent)
        logger.debug("ViloWebBridge initialized")

    # ===== JavaScript-Callable Methods =====

    @Slot(str, str)
    def log_from_js(self, level: str, message: str) -> None:
        """Log message from JavaScript to Python console.

        Args:
            level: Log level ("debug", "info", "warning", "error")
            message: Message to log

        JavaScript Example:
            window.viloWeb.log_from_js("info", "Page loaded successfully");

        Educational Note:
            This is useful for debugging and monitoring what JavaScript
            is doing on the page. It bridges the console.log world (JS)
            to the logging module world (Python).
        """
        log_level = getattr(logging, level.upper(), logging.INFO)
        logger.log(log_level, f"[JS] {message}")
        self.log_message.emit(level, message)

    @Slot()
    def bookmark_current_page(self) -> None:
        """Request to bookmark current page from JavaScript.

        JavaScript Example:
            // Add a "Bookmark this page" button to any website
            const btn = document.createElement('button');
            btn.textContent = 'Bookmark';
            btn.onclick = () => window.viloWeb.bookmark_current_page();
            document.body.prepend(btn);

        Educational Note:
            This demonstrates how JavaScript can trigger Python actions.
            The bridge emits a signal, and the main window handles the
            actual bookmark creation (since the bridge doesn't know
            about the bookmark manager).

            Why this pattern?
            - Separation of concerns: Bridge doesn't manage bookmarks
            - Flexibility: Different windows can handle bookmarks differently
            - Testability: Easy to test signal emission separately
        """
        logger.info("JavaScript requested bookmark")
        self.bookmark_requested.emit()

    @Slot(str, result=bool)
    def can_execute_command(self, command: str) -> bool:
        """Check if a command is safe to execute.

        Args:
            command: Command name to check

        Returns:
            True if command is allowed, False otherwise

        JavaScript Example:
            if (window.viloWeb.can_execute_command("bookmark")) {
                window.viloWeb.bookmark_current_page();
            }

        Educational Note:
            This is a security pattern: JavaScript asks permission before
            calling sensitive operations. In this MVP, we're very restrictive.

            In a real browser, you'd have:
            - Permission system (per-domain permissions)
            - User confirmation dialogs
            - Sandboxed execution context
        """
        # MVP: Only allow explicitly whitelisted commands
        allowed_commands = {"bookmark", "log", "theme_info"}

        is_allowed = command in allowed_commands
        logger.debug(f"Command check: {command} -> {is_allowed}")
        return is_allowed

    @Slot(result=str)
    def get_bridge_version(self) -> str:
        """Get ViloWeb bridge version.

        Returns:
            Bridge version string

        JavaScript Example:
            const version = window.viloWeb.get_bridge_version();
            console.log(`Bridge version: ${version}`);

        Educational Note:
            Version reporting helps debug integration issues and enables
            feature detection from JavaScript side.
        """
        return "1.0.0"

    @Slot(result=str)
    def get_browser_info(self) -> str:
        """Get browser information.

        Returns:
            JSON string with browser info

        JavaScript Example:
            const info = JSON.parse(window.viloWeb.get_browser_info());
            console.log(`Running on: ${info.browser}`);

        Educational Note:
            This demonstrates returning structured data to JavaScript.
            We return JSON string (not dict) because QWebChannel handles
            strings more reliably than complex Python objects.
        """
        import json

        info = {
            "browser": "ViloWeb",
            "version": "0.1.0",
            "engine": "Qt WebEngine",
            "bridge_version": "1.0.0",
        }

        return json.dumps(info)

    @Slot(str)
    def inject_page_script(self, script_name: str) -> None:
        """Request injection of a named script template.

        Args:
            script_name: Name of script template to inject

        JavaScript Example:
            window.viloWeb.inject_page_script("dark_mode_toggle");

        Educational Note:
            This is a placeholder for a future feature: allowing JavaScript
            to request Python to inject additional scripts. In a full browser,
            this would be part of the extension system.

            Why not let JS inject scripts directly?
            - Security: Python controls what scripts exist
            - CSP bypass: Only Python can inject via QWebEngineScript
            - Consistency: Centralized script management
        """
        logger.info(f"Script injection requested: {script_name}")
        # MVP: Just log it. Full implementation would emit signal
        # and let main window handle via extension system
        logger.debug("Script injection not yet implemented in MVP")

    # ===== Helper Methods (not exposed to JS) =====

    def shutdown(self) -> None:
        """Clean up bridge resources.

        Educational Note:
            This is called when the browser closes. While QWebChannel
            doesn't require explicit cleanup, this is a good place for
            future cleanup logic (closing files, stopping timers, etc.).
        """
        logger.info("ViloWebBridge shutting down")
        # MVP: Nothing to clean up
        logger.debug("Bridge shutdown complete")
