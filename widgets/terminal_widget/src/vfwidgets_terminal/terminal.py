"""Terminal Widget - Main PySide6 terminal widget implementation."""

import json
import logging
import warnings
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional

from PySide6.QtCore import QEvent, QObject, QPoint, QThread, QUrl, Signal, Slot, Qt
from PySide6.QtGui import QAction, QContextMenuEvent, QMouseEvent
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QApplication, QMenu, QVBoxLayout, QWidget

try:
    from vfwidgets_theme.widgets.base import ThemedWidget

    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False
    ThemedWidget = object

from .constants import DEFAULT_COLS, DEFAULT_ROWS, DEFAULT_SCROLLBACK
from .embedded_server import EmbeddedTerminalServer

logger = logging.getLogger(__name__)


# Phase 2: Event Data Classes for structured event information
@dataclass
class ProcessEvent:
    """Structured data for process-related events."""

    command: str
    pid: Optional[int] = None
    working_directory: Optional[str] = None
    timestamp: datetime = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class KeyEvent:
    """Structured data for keyboard events."""

    key: str
    code: str
    ctrl: bool
    alt: bool
    shift: bool
    timestamp: datetime = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class ContextMenuEvent:
    """Structured data for context menu events."""

    position: QPoint
    global_position: Optional[QPoint] = None
    selected_text: str = ""
    cursor_position: Optional[tuple[int, int]] = None
    timestamp: datetime = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = datetime.now()


# Phase 3: Event Categories for configuration
class EventCategory(Enum):
    """Event categories for filtering and configuration."""

    LIFECYCLE = "lifecycle"  # terminalReady, terminalClosed, serverStarted
    PROCESS = "process"  # processStarted, processFinished
    CONTENT = "content"  # outputReceived, errorReceived, inputSent
    INTERACTION = "interaction"  # keyPressed, selectionChanged
    FOCUS = "focus"  # focusReceived, focusLost
    APPEARANCE = "appearance"  # sizeChanged, titleChanged, bellActivated


@dataclass
class EventConfig:
    """Configuration for terminal events."""

    enabled_categories: set[EventCategory] = None
    throttle_high_frequency: bool = True
    debug_logging: bool = False
    enable_deprecation_warnings: bool = True

    def __post_init__(self) -> None:
        if self.enabled_categories is None:
            self.enabled_categories = set(EventCategory)


def _emit_deprecation_warning(old_signal_name: str, new_signal_name: str):
    """Emit a deprecation warning for old signal names."""
    warnings.warn(
        f"Signal '{old_signal_name}' is deprecated. Use '{new_signal_name}' instead. "
        f"The old signal will be removed in a future version.",
        DeprecationWarning,
        stacklevel=3,
    )


class DebugWebEngineView(QWebEngineView):
    """Enhanced QWebEngineView that captures context menu and mouse events."""

    # Signals to notify parent of mouse events
    right_clicked = Signal(QPoint)
    middle_clicked = Signal(QPoint)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.debug_enabled = False

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Intercept mouse press events to detect middle-click.

        Note: This must be called BEFORE the event reaches QWebEngineView's
        internal widgets. We emit the signal and then let the event propagate.
        """
        if event.button() == Qt.MouseButton.MiddleButton:
            logger.info(
                f"🖱️  WEBVIEW: Middle-click detected at ({event.pos().x()}, {event.pos().y()})"
            )
            # Emit signal to parent (non-blocking)
            self.middle_clicked.emit(event.pos())
            # Accept the event to prevent scrolling behavior
            event.accept()
            return

        # Let other mouse buttons be handled normally
        super().mousePressEvent(event)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        """Intercept context menu events and forward to parent."""
        if self.debug_enabled:
            logger.info(
                f"🖱️  WEBVIEW: Right-click intercepted at ({event.pos().x()}, {event.pos().y()})"
            )

        # Emit signal to parent
        self.right_clicked.emit(event.pos())

        # Forward event to parent widget (our TerminalWidget)
        parent_widget = self.parent()
        if parent_widget and hasattr(parent_widget, "contextMenuEvent"):
            if self.debug_enabled:
                logger.info("🔄 WEBVIEW: Forwarding context menu event to parent")
            parent_widget.contextMenuEvent(event)
        else:
            # Fallback to default behavior
            if self.debug_enabled:
                logger.info("📋 WEBVIEW: Using default context menu")
            super().contextMenuEvent(event)

    def set_debug(self, enabled: bool) -> None:
        """Enable/disable debug logging."""
        self.debug_enabled = enabled


class TerminalBridge(QObject):
    """Bridge between JavaScript (xterm.js) and Python (PySide6).

    This class enables bidirectional communication between the xterm.js terminal
    running in QWebEngineView and the Python TerminalWidget. It exposes xterm.js
    events as Qt signals and provides methods for JavaScript to call.
    """

    # Signals for events from xterm.js (Phase 3: Rich events)
    selection_changed = Signal(str)  # selected text
    cursor_moved = Signal(int, int)  # row, col
    bell_rang = Signal()  # bell/notification
    title_changed = Signal(str)  # terminal title
    key_pressed = Signal(str, str, bool, bool, bool)  # key, code, ctrl, alt, shift
    data_received = Signal(str)  # input data from user
    scroll_occurred = Signal(int)  # scroll position
    shortcut_pressed = Signal(str)  # shortcut action_id (e.g., "pane.navigate_left")
    working_directory_changed = Signal(str)  # OSC 7: current working directory

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._last_selection = ""  # Track current selection for context menu
        self._current_cwd: Optional[str] = None  # Track current working directory
        logger.debug("TerminalBridge initialized")

    @Slot(str)
    def on_selection_changed(self, selected_text: str) -> None:
        """Handle selection change from xterm.js."""
        self._last_selection = selected_text  # Store for context menu
        logger.debug(f"Selection changed: {len(selected_text)} characters selected")
        self.selection_changed.emit(selected_text)

    @Slot(int, int)
    def on_cursor_moved(self, row: int, col: int) -> None:
        """Handle cursor movement from xterm.js."""
        # Only log occasionally to avoid spam
        if row % 10 == 0 or col % 10 == 0:
            logger.debug(f"Cursor moved to ({row}, {col})")
        self.cursor_moved.emit(row, col)

    @Slot()
    def on_bell(self) -> None:
        """Handle bell event from xterm.js."""
        logger.debug("Terminal bell rang")
        self.bell_rang.emit()

    @Slot(str)
    def on_title_changed(self, title: str) -> None:
        """Handle title change from xterm.js."""
        logger.debug(f"Terminal title changed to: {title}")
        self.title_changed.emit(title)

    @Slot(str, str, bool, bool, bool)
    def on_key_pressed(
        self, key: str, code: str, ctrl: bool, alt: bool, shift: bool
    ) -> None:
        """Handle key press from xterm.js."""
        # Only log special keys to avoid spam
        if ctrl or alt or len(key) > 1:
            logger.debug(
                f"Key pressed: {key} (code: {code}, ctrl: {ctrl}, alt: {alt}, shift: {shift})"
            )
        self.key_pressed.emit(key, code, ctrl, alt, shift)

    @Slot(str)
    def on_data_received(self, data: str) -> None:
        """Handle data input from xterm.js."""
        # Only log non-trivial data to avoid spam
        if len(data) > 1 or data in ["\r", "\n"]:
            logger.debug(f"Data received: {repr(data)}")
        self.data_received.emit(data)

    @Slot(int)
    def on_scroll(self, position: int) -> None:
        """Handle scroll event from xterm.js."""
        logger.debug(f"Terminal scrolled to position: {position}")
        self.scroll_occurred.emit(position)

    @Slot(str)
    def on_shortcut_pressed(self, action_id: str) -> None:
        """Handle shortcut from JavaScript (e.g., Ctrl+Shift+Arrow keys).

        Args:
            action_id: Action ID like 'pane.navigate_left' or 'tab.navigate_next'
        """
        logger.info(f"Shortcut pressed from JS: {action_id}")
        self.shortcut_pressed.emit(action_id)

    @Slot(str)
    def on_working_directory_changed(self, cwd: str) -> None:
        """Handle working directory change from OSC 7.

        Called from JavaScript when terminal emits OSC 7 escape sequence.

        Args:
            cwd: Current working directory path
        """
        # Basic validation - don't check existence (might be on remote host)
        if not cwd or not cwd.startswith("/"):
            logger.warning(f"Invalid CWD reported by OSC 7: {cwd}")
            return

        self._current_cwd = cwd
        logger.info(f"OSC 7 - Working directory changed to: {cwd}")
        self.working_directory_changed.emit(cwd)

    def get_current_cwd(self) -> Optional[str]:
        """Get current working directory.

        Returns:
            Current working directory path, or None if not yet reported
        """
        return self._current_cwd

    @Slot(int, int)
    def on_middle_click(self, x: int, y: int) -> None:
        """Handle middle-click from JavaScript for paste operation.

        Args:
            x: X coordinate of click
            y: Y coordinate of click
        """
        logger.info(f"🖱️  Middle-click received from JavaScript at ({x}, {y})")
        # Get parent TerminalWidget and trigger paste
        parent_widget = self.parent()
        if parent_widget and hasattr(parent_widget, "_paste_from_clipboard"):
            parent_widget._paste_from_clipboard()
        else:
            logger.warning(
                "Cannot trigger middle-click paste - parent widget not available"
            )

    @Slot(str, result=str)
    def execute_command(self, command: str) -> str:
        """Execute a command and return result (for future use)."""
        logger.debug(f"JavaScript requested command execution: {command}")
        # This will be implemented later when we add advanced APIs
        return json.dumps({"status": "not_implemented", "command": command})

    @Slot(result=str)
    def get_terminal_info(self) -> str:
        """Get terminal information (for future use)."""
        logger.debug("JavaScript requested terminal info")
        # This will be implemented later
        return json.dumps({"status": "active", "type": "xterm.js"})


if THEME_AVAILABLE:
    _BaseTerminalClass = type("_BaseTerminalClass", (ThemedWidget, QWidget), {})
else:
    _BaseTerminalClass = QWidget


class TerminalWidget(_BaseTerminalClass):
    """PySide6 terminal widget powered by xterm.js.

    A fully-featured terminal emulator widget that can be embedded in Qt applications.
    Supports both embedded and external server modes for flexibility.

    When vfwidgets-theme is installed, automatically adapts to application theme.
    """

    # Theme configuration - maps theme tokens to xterm.js ITheme properties
    # Note: Using editor.* tokens because terminal.* tokens are not populated in built-in themes
    # Terminals are semantically similar to editors (monospace, text-based)
    theme_config = {
        "background": "editor.background",
        "foreground": "editor.foreground",
        "cursor": "editor.foreground",  # Cursor uses editor foreground
        "cursorAccent": "editor.background",  # Cursor accent uses editor background
        "selectionBackground": "editor.selectionBackground",
        # ANSI colors fallback to standard terminal colors
        "black": "terminal.ansiBlack",
        "red": "terminal.ansiRed",
        "green": "terminal.ansiGreen",
        "yellow": "terminal.ansiYellow",
        "blue": "terminal.ansiBlue",
        "magenta": "terminal.ansiMagenta",
        "cyan": "terminal.ansiCyan",
        "white": "terminal.ansiWhite",
        "brightBlack": "terminal.ansiBrightBlack",
        "brightRed": "terminal.ansiBrightRed",
        "brightGreen": "terminal.ansiBrightGreen",
        "brightYellow": "terminal.ansiBrightYellow",
        "brightBlue": "terminal.ansiBrightBlue",
        "brightMagenta": "terminal.ansiBrightMagenta",
        "brightCyan": "terminal.ansiBrightCyan",
        "brightWhite": "terminal.ansiBrightWhite",
    }

    # ============================================================================
    # NEW Qt-Compliant Signals (Phase 1: Proper API Design)
    # ============================================================================

    # Terminal Lifecycle Signals (EventCategory.LIFECYCLE)
    terminalReady = Signal()  # Terminal is ready for use
    terminalClosed = Signal(int)  # Terminal closed with exit code
    serverStarted = Signal(str)  # Server started at URL
    connectionLost = Signal()  # Connection to terminal lost
    connectionRestored = Signal()  # Connection to terminal restored

    # Process Management Signals (EventCategory.PROCESS)
    processStarted = Signal(ProcessEvent)  # Process started with details
    processFinished = Signal(int)  # Process finished with exit code

    # Content Signals (EventCategory.CONTENT)
    outputReceived = Signal(str)  # Terminal output received
    errorReceived = Signal(str)  # Terminal error output received
    inputSent = Signal(str)  # Input sent to terminal

    # User Interaction Signals (EventCategory.INTERACTION)
    keyPressed = Signal(KeyEvent)  # Key pressed with full details
    selectionChanged = Signal(str)  # Text selection changed
    shortcutPressed = Signal(str)  # Shortcut pressed from JavaScript (action_id)
    contextMenuRequested = Signal(ContextMenuEvent)  # Context menu requested

    # Focus & Display Signals (EventCategory.FOCUS, EventCategory.APPEARANCE)
    focusReceived = Signal()  # Terminal received focus
    focusLost = Signal()  # Terminal lost focus
    sizeChanged = Signal(int, int)  # Terminal size changed (rows, cols)
    titleChanged = Signal(str)  # Terminal title changed
    bellActivated = Signal()  # Terminal bell/notification
    scrollOccurred = Signal(int)  # Terminal scrolled to position

    # Working Directory Signals (OSC 7 tracking)
    workingDirectoryChanged = Signal(str)  # Current working directory changed

    # ============================================================================
    # DEPRECATED Signals (Phase 7: Backwards Compatibility)
    # These signals are deprecated and will be removed in a future version.
    # Use the Qt-compliant signals above instead.
    # ============================================================================

    # Deprecated - use terminalReady instead
    terminal_ready = Signal()
    # Deprecated - use terminalClosed instead
    terminal_closed = Signal(int)
    # Deprecated - use processStarted instead
    command_started = Signal(str)
    # Deprecated - use processFinished instead
    command_finished = Signal(int)
    # Deprecated - use outputReceived instead
    output_received = Signal(str)
    # Deprecated - use errorReceived instead
    error_received = Signal(str)
    # Deprecated - use inputSent instead
    input_sent = Signal(str)
    # Deprecated - use sizeChanged instead
    resize_occurred = Signal(int, int)
    # Deprecated - use connectionLost instead
    connection_lost = Signal()
    # Deprecated - use connectionRestored instead
    connection_restored = Signal()
    # Deprecated - use serverStarted instead
    server_started = Signal(str)
    # Deprecated - use focusReceived instead
    focus_received = Signal()
    # Deprecated - use focusLost instead
    focus_lost = Signal()
    # Deprecated - use selectionChanged instead
    selection_changed = Signal(str)
    # Deprecated - future: cursor tracking
    cursor_moved = Signal(int, int)
    # Deprecated - use bellActivated instead
    bell_rang = Signal()
    # Deprecated - use titleChanged instead
    title_changed = Signal(str)
    # Deprecated - use keyPressed instead
    key_pressed = Signal(str, str, bool, bool, bool)
    # Deprecated - use inputSent instead
    terminal_data = Signal(str)
    # Deprecated - use scrollOccurred instead
    scroll_occurred = Signal(int)
    # Deprecated - use contextMenuRequested instead
    context_menu_requested = Signal(QPoint, str)

    def __init__(
        self,
        command: str = "bash",
        args: Optional[list[str]] = None,
        cwd: Optional[str] = None,
        env: Optional[dict[str, str]] = None,
        parent: Optional[QWidget] = None,
        # Server options
        server_url: Optional[str] = None,  # Use external server
        port: int = 0,  # 0 = random port
        host: str = "127.0.0.1",
        # Terminal options
        rows: int = DEFAULT_ROWS,
        cols: int = DEFAULT_COLS,
        scrollback: int = DEFAULT_SCROLLBACK,  # DEPRECATED: Use terminal_config instead
        theme: str = "dark",  # 'dark', 'light', or custom dict
        terminal_config: Optional[dict] = None,  # xterm.js configuration options
        # Developer features
        capture_output: bool = False,
        output_filter: Optional[Callable[[str], str]] = None,
        output_parser: Optional[Callable[[str], Any]] = None,
        read_only: bool = False,
        debug: bool = False,
        # Phase 3: Event configuration
        event_config: Optional[EventConfig] = None,
    ):
        """Initialize the Terminal Widget.

        Args:
            command: Shell command to execute (e.g., 'bash', 'python')
            args: Arguments for the command
            cwd: Working directory for the terminal
            env: Environment variables
            parent: Parent widget
            server_url: URL of external terminal server (if not using embedded)
            port: Port for embedded server (0 for random)
            host: Host for embedded server
            rows: Initial number of terminal rows
            cols: Initial number of terminal columns
            scrollback: Number of scrollback lines (DEPRECATED: use terminal_config)
            theme: Color theme ('dark', 'light', or custom dict)
            terminal_config: xterm.js configuration dict with options like:
                - scrollback: Number of scrollback lines (default: 1000)
                - cursorBlink: Whether cursor blinks (default: true)
                - cursorStyle: 'block', 'underline', or 'bar' (default: 'block')
                - tabStopWidth: Width of tab stops (default: 4)
                - bellStyle: 'none', 'sound', or 'visual' (default: 'none')
                - scrollSensitivity: Mouse wheel scroll speed (default: 1)
                - fastScrollSensitivity: Shift+scroll speed (default: 5)
                - fastScrollModifier: 'alt', 'ctrl', or 'shift' (default: 'shift')
                - rightClickSelectsWord: Select word on right click (default: false)
                - convertEol: Convert \\n to \\r\\n (default: false)
            capture_output: Whether to capture output for retrieval
            output_filter: Function to filter/process output
            output_parser: Function to parse output
            read_only: Make terminal read-only
            debug: Enable debug logging
            event_config: Event system configuration (Phase 3)
        """
        super().__init__(parent)

        # Store configuration
        self.command = command
        self.args = args or []
        self.cwd = cwd
        self.env = env or {}

        # Handle terminal_config early to extract termType for env
        # We need to do this before other initialization that uses self.env
        self._terminal_config_raw = terminal_config

        self.server_url = server_url
        self.port = port
        self.host = host
        self.rows = rows
        self.cols = cols
        self.scrollback = scrollback
        self._user_theme = (
            theme  # Renamed from self.theme to avoid conflict with ThemedWidget
        )
        self.capture_output = capture_output
        self.output_filter = output_filter
        self.output_parser = output_parser
        self.read_only = read_only
        self.debug = debug

        # Internal state
        self.server = None
        self.web_view = None
        self.output_buffer = [] if capture_output else None
        self.is_connected = False
        self.process_info = {}
        self._current_working_directory: Optional[str] = (
            cwd  # Track current CWD from OSC 7
        )

        # Phase 2: QWebChannel bridge for JavaScript communication
        self.bridge = None
        self.web_channel = None

        # Phase 3: Event configuration system
        self.event_config = event_config or EventConfig()

        # Phase 4: Context menu customization
        self.custom_context_menu_handler = None
        self.custom_context_actions = []

        # Copy-paste configuration (X11-style behavior)
        self.auto_copy_on_selection = True  # Auto-copy selected text to clipboard
        self.middle_click_paste_enabled = True  # Paste on middle-click

        # Terminal theme storage
        self._current_terminal_theme: Optional[dict] = None

        # Terminal configuration storage (xterm.js options)
        # Handle terminal_config parameter and backwards compatibility
        if terminal_config is not None:
            self._terminal_config = terminal_config.copy()
            # If scrollback is explicitly set in both places, terminal_config wins
            if (
                scrollback != DEFAULT_SCROLLBACK
                and "scrollback" not in self._terminal_config
            ):
                logger.warning(
                    "scrollback parameter is deprecated. Use terminal_config={'scrollback': ...} instead"
                )
                self._terminal_config["scrollback"] = scrollback

            # Extract termType from terminal_config and set it in environment
            # This allows users to configure TERM variable via terminal preferences
            if "termType" in self._terminal_config:
                term_type = self._terminal_config["termType"]
                # Only set TERM if not already set by user via env parameter
                if "TERM" not in self.env:
                    self.env["TERM"] = term_type
                    logger.debug(f"Setting TERM environment variable to: {term_type}")

        elif scrollback != DEFAULT_SCROLLBACK:
            # Only scrollback parameter provided (old API)
            logger.warning(
                "scrollback parameter is deprecated. Use terminal_config={'scrollback': ...} instead"
            )
            self._terminal_config = {"scrollback": scrollback}
        else:
            self._terminal_config = None

        # If no terminal config and no TERM env set, use default
        if "TERM" not in self.env:
            self.env["TERM"] = "xterm-256color"
            logger.debug("Setting TERM environment variable to default: xterm-256color")

        # Phase 7: Set up signal forwarding for backwards compatibility
        self._setup_signal_forwarding()

        # Setup logging - always log important events
        if debug:
            logging.basicConfig(level=logging.DEBUG)
            logger.setLevel(logging.DEBUG)
        else:
            # Still log important events even when not in debug mode
            logger.setLevel(logging.INFO)

        # Initialize UI and server
        self._setup_ui()
        self._start_terminal()

    def _setup_signal_forwarding(self) -> None:
        """Set up signal forwarding from new signals to deprecated signals for backwards compatibility."""

        # Emit deprecation warnings and forward signals
        def forward_with_warning(old_signal_name: str, new_signal_name: str):
            def forwarder(*args):
                if self.event_config.enable_deprecation_warnings:
                    _emit_deprecation_warning(old_signal_name, new_signal_name)
                return args

            return forwarder

        # Connect new signals to old signals for backwards compatibility
        self.terminalReady.connect(lambda: self.terminal_ready.emit())
        self.terminalClosed.connect(lambda code: self.terminal_closed.emit(code))
        self.processStarted.connect(
            lambda event: self.command_started.emit(event.command)
        )
        self.processFinished.connect(lambda code: self.command_finished.emit(code))
        self.outputReceived.connect(lambda data: self.output_received.emit(data))
        self.errorReceived.connect(lambda data: self.error_received.emit(data))
        self.inputSent.connect(lambda text: self.input_sent.emit(text))
        self.sizeChanged.connect(
            lambda rows, cols: self.resize_occurred.emit(rows, cols)
        )
        self.connectionLost.connect(lambda: self.connection_lost.emit())
        self.connectionRestored.connect(lambda: self.connection_restored.emit())
        self.serverStarted.connect(lambda url: self.server_started.emit(url))
        self.focusReceived.connect(lambda: self.focus_received.emit())
        self.focusLost.connect(lambda: self.focus_lost.emit())
        self.selectionChanged.connect(lambda text: self.selection_changed.emit(text))
        self.bellActivated.connect(lambda: self.bell_rang.emit())
        self.titleChanged.connect(lambda title: self.title_changed.emit(title))
        self.keyPressed.connect(
            lambda event: self.key_pressed.emit(
                event.key, event.code, event.ctrl, event.alt, event.shift
            )
        )
        self.inputSent.connect(
            lambda text: self.terminal_data.emit(text)
        )  # terminal_data was duplicate of input_sent
        self.scrollOccurred.connect(lambda pos: self.scroll_occurred.emit(pos))
        self.contextMenuRequested.connect(
            lambda event: self.context_menu_requested.emit(
                event.position, event.selected_text
            )
        )

        # Connect auto-copy handler
        self.selectionChanged.connect(self._handle_selection_for_auto_copy)

    # Phase 4: Intuitive Developer API Helper Methods

    def configure_events(self, config: EventConfig) -> None:
        """Configure the event system.

        Args:
            config: Event configuration settings
        """
        self.event_config = config
        logger.info(
            f"Event configuration updated: enabled categories={[cat.value for cat in config.enabled_categories]}"
        )

    def enable_event_category(self, category: EventCategory) -> None:
        """Enable a specific event category.

        Args:
            category: Event category to enable
        """
        self.event_config.enabled_categories.add(category)
        logger.debug(f"Enabled event category: {category.value}")

    def disable_event_category(self, category: EventCategory) -> None:
        """Disable a specific event category.

        Args:
            category: Event category to disable
        """
        self.event_config.enabled_categories.discard(category)
        logger.debug(f"Disabled event category: {category.value}")

    def monitor_command_execution(
        self, callback: Callable[[ProcessEvent], None]
    ) -> None:
        """Set up monitoring for command execution (helper method for common use case).

        Args:
            callback: Function to call when process events occur
        """
        self.processStarted.connect(callback)
        logger.debug("Command execution monitoring enabled")

    def add_context_menu_handler(
        self, handler: Callable[[ContextMenuEvent], Optional[QMenu]]
    ) -> None:
        """Add a custom context menu handler (helper method).

        Args:
            handler: Function that creates a custom context menu
        """
        self.custom_context_menu_handler = handler
        logger.debug("Custom context menu handler added")

    def set_selection_handler(self, handler: Callable[[str], None]) -> None:
        """Set up a handler for text selection changes (helper method).

        Args:
            handler: Function to call when selection changes
        """
        self.selectionChanged.connect(handler)
        logger.debug("Selection change handler added")

    def enable_session_recording(self, callback: Callable[[str], None]) -> None:
        """Enable session recording (helper method for common use case).

        Args:
            callback: Function to call with output data for recording
        """
        self.outputReceived.connect(callback)
        logger.debug("Session recording enabled")

    def _setup_ui(self) -> None:
        """Set up the widget UI."""
        # Log WebEngine configuration for debugging WSL and other special environments
        try:
            from vfwidgets_common import log_webengine_configuration

            if self.debug:
                log_webengine_configuration()
        except ImportError:
            # vfwidgets_common not available, skip logging
            pass

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create web view for terminal (use our enhanced version for context menu debugging)
        self.web_view = DebugWebEngineView(self)
        self.web_view.set_debug(self.debug)

        # Set background color to match terminal theme (prevents white flash on startup)
        from PySide6.QtGui import QColor

        bg_color = self._get_initial_background_color()
        self.web_view.page().setBackgroundColor(QColor(bg_color))

        layout.addWidget(self.web_view)

        # Connect right-click signal
        self.web_view.right_clicked.connect(
            lambda pos: logger.info(
                f"🖱️  RIGHT-CLICK: Detected via QWebEngineView at ({pos.x()}, {pos.y()})"
            )
        )

        # Connect middle-click signal for paste
        self.web_view.middle_clicked.connect(self._handle_middle_click)

        # Connect page load signals
        self.web_view.loadFinished.connect(self._on_load_finished)

        # Install event filter on focus proxy for proper focus detection
        # This is needed because QWebEngineView doesn't propagate focus events normally
        self._setup_focus_detection()

        # Set up QWebChannel bridge for JavaScript communication
        self._setup_web_channel_bridge()

    def _setup_focus_detection(self) -> None:
        """Set up proper focus event detection for QWebEngineView.

        QWebEngineView doesn't propagate focus events normally, so we need to
        install an event filter on its focus proxy to detect when the terminal
        actually receives or loses focus.
        """

        # Wait for the web view to be fully initialized
        def setup_after_load():
            focus_proxy = self.web_view.focusProxy()
            if focus_proxy:
                focus_proxy.installEventFilter(self)
                logger.info(
                    "✅ FOCUS SETUP: Installed focus event filter on QWebEngineView focus proxy"
                )
                logger.info(
                    f"🔍 FOCUS SETUP: Focus proxy type: {type(focus_proxy).__name__}"
                )
            else:
                logger.warning(
                    "❌ FOCUS SETUP: QWebEngineView focus proxy not available"
                )

        # Try immediate setup first
        focus_proxy = self.web_view.focusProxy()
        if focus_proxy:
            focus_proxy.installEventFilter(self)
            logger.info("✅ FOCUS SETUP: Installed focus event filter immediately")
            logger.info(
                f"🔍 FOCUS SETUP: Focus proxy type: {type(focus_proxy).__name__}"
            )
        else:
            logger.info(
                "⏳ FOCUS SETUP: Focus proxy not ready, will try after page loads"
            )

        # Also set up after page loads as backup
        def delayed_setup():
            focus_proxy = self.web_view.focusProxy()
            if focus_proxy and not hasattr(focus_proxy, "_vf_filter_installed"):
                focus_proxy.installEventFilter(self)
                focus_proxy._vf_filter_installed = True  # Mark as installed
                logger.info(
                    "✅ FOCUS SETUP: Installed focus event filter after page load"
                )
            elif focus_proxy:
                logger.debug("🔍 FOCUS SETUP: Focus proxy already has filter installed")
            else:
                logger.warning(
                    "❌ FOCUS SETUP: Still no focus proxy available after page load"
                )

        # Set up focus detection after page loads
        self.web_view.loadFinished.connect(
            lambda success: (
                delayed_setup()
                if success
                else logger.warning("❌ FOCUS SETUP: Page failed to load")
            )
        )

    def setFocus(self) -> None:
        """Override setFocus to properly focus the web view.

        When Qt focus is set on TerminalWidget programmatically,
        we need to explicitly set focus on the QWebEngineView to
        ensure the terminal can receive keyboard input immediately.
        """
        super().setFocus()
        # Focus the web view's focus proxy (the actual input receiver)
        focus_proxy = self.web_view.focusProxy()
        if focus_proxy:
            focus_proxy.setFocus()
        else:
            # Fallback: focus the web view itself
            self.web_view.setFocus()

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """Handle events from the QWebEngineView focus proxy.

        This is where we catch the actual focus events that QWebEngineView
        receives but doesn't normally propagate to the parent widget.
        """
        # Log all events when debugging to see what's happening
        if self.debug and obj == self.web_view.focusProxy():
            event_name = (
                event.type().name
                if hasattr(event.type(), "name")
                else str(event.type())
            )
            logger.debug(f"🔍 EVENT FILTER: Received {event_name} on focus proxy")

        if obj == self.web_view.focusProxy():
            if event.type() == QEvent.Type.FocusIn:
                logger.info("🎯 FOCUS: Terminal received focus (via focus proxy)")
                if EventCategory.FOCUS in self.event_config.enabled_categories:
                    self.focusReceived.emit()
                return False  # Let the event continue to be processed
            elif event.type() == QEvent.Type.FocusOut:
                logger.info("❌ FOCUS: Terminal lost focus (via focus proxy)")
                if EventCategory.FOCUS in self.event_config.enabled_categories:
                    self.focusLost.emit()
                return False  # Let the event continue to be processed

        # Pass other events to parent class
        return super().eventFilter(obj, event)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        """Handle context menu requests (Phase 4: Enhanced context menu system).

        Provides a customizable context menu with terminal-specific actions
        and allows developers to add their own custom actions.
        """
        # Log the right-click event for testing
        logger.info(
            f"🖱️  RIGHT-CLICK detected at position ({event.pos().x()}, {event.pos().y()})"
        )

        # Get current selection from the bridge if available
        selected_text = ""
        if self.bridge and hasattr(self.bridge, "_last_selection"):
            selected_text = getattr(self.bridge, "_last_selection", "")

        logger.info(
            f"📝 Selected text: '{selected_text[:50]}{'...' if len(selected_text) > 50 else ''}'"
        )
        logger.info("🎯 Emitting context_menu_requested signal")

        # Create structured context menu event data
        context_event = ContextMenuEvent(
            position=event.pos(),
            global_position=event.globalPos(),
            selected_text=selected_text,
            cursor_position=None,  # TODO: Get from bridge when available
        )

        # Emit signal for developers who want to handle context menu themselves
        if EventCategory.INTERACTION in self.event_config.enabled_categories:
            self.contextMenuRequested.emit(context_event)

        # If developer provided custom handler, use it
        if self.custom_context_menu_handler:
            try:
                logger.info("🔧 Using custom context menu handler")
                menu = self.custom_context_menu_handler(event.pos(), selected_text)
                if menu:
                    logger.info("📋 Showing custom context menu")
                    menu.exec_(event.globalPos())
                    return
                else:
                    logger.info(
                        "❌ Custom handler returned None, falling back to default menu"
                    )
            except Exception as e:
                logger.warning(f"Custom context menu handler failed: {e}")

        # Default context menu
        logger.info("📋 Showing default context menu")
        self._show_default_context_menu(event.globalPos(), selected_text)

    def _show_default_context_menu(
        self, global_pos: QPoint, selected_text: str
    ) -> None:
        """Show the default terminal context menu."""
        logger.debug(
            f"Creating default context menu at global position ({global_pos.x()}, {global_pos.y()})"
        )
        menu = QMenu(self)

        action_count = 0

        # Copy action (only if text is selected)
        if selected_text:
            copy_action = QAction("Copy", self)
            copy_action.triggered.connect(
                lambda: self._copy_to_clipboard(selected_text)
            )
            menu.addAction(copy_action)
            action_count += 1
            logger.debug(f"➕ Added 'Copy' action (text length: {len(selected_text)})")

        # Paste action
        paste_action = QAction("Paste", self)
        paste_action.triggered.connect(self._paste_from_clipboard)
        menu.addAction(paste_action)
        action_count += 1
        logger.debug("➕ Added 'Paste' action")

        if selected_text and selected_text.strip():
            menu.addSeparator()

            # Clear action
            clear_action = QAction("Clear Terminal", self)
            clear_action.triggered.connect(self.clear_terminal)
            menu.addAction(clear_action)
            action_count += 1
            logger.debug("➕ Added 'Clear Terminal' action")

        # Add custom actions if any
        if self.custom_context_actions:
            menu.addSeparator()
            for action in self.custom_context_actions:
                menu.addAction(action)
                action_count += 1
                logger.debug(f"➕ Added custom action: '{action.text()}'")

        logger.info(f"🎯 Displaying context menu with {action_count} actions")
        menu.exec_(global_pos)
        logger.debug("✅ Context menu closed")

    def _copy_to_clipboard(self, text: str) -> None:
        """Copy text to system clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        logger.info(
            f"📋 Copied {len(text)} characters to clipboard: '{text[:30]}{'...' if len(text) > 30 else ''}'"
        )

    def _paste_from_clipboard(self) -> None:
        """Paste text from system clipboard to terminal."""
        clipboard = QApplication.clipboard()
        text = clipboard.text()

        if not text:
            logger.info("📥 Paste attempted but clipboard is empty")
            return

        # Try embedded server first (if available)
        if self.server:
            self.server.send_input(text)
            logger.info(
                f"📥 Pasted {len(text)} characters from clipboard: '{text[:30]}{'...' if len(text) > 30 else ''}'"
            )
        # Otherwise, send via JavaScript to xterm.js (works with external/multi-session server)
        elif self.web_view and self.is_connected:
            # Use JSON encoding to safely pass text to JavaScript
            import json

            text_json = json.dumps(text)
            js_code = f"""
            if (typeof socket !== 'undefined' && socket.emit) {{
                // Build payload with session_id if available (for multi-session server)
                const payload = {{ input: {text_json} }};
                if (typeof sessionId !== 'undefined' && sessionId) {{
                    payload.session_id = sessionId;
                }}
                socket.emit('pty-input', payload);
                console.log('Pasted text via socket:', {text_json});
            }} else {{
                console.error('Socket not available for paste');
            }}
            """
            self.web_view.page().runJavaScript(js_code)
            logger.info(
                f"📥 Pasted {len(text)} characters from clipboard via JavaScript: '{text[:30]}{'...' if len(text) > 30 else ''}'"
            )
        else:
            logger.warning("📥 Paste failed - no server or connection available")

    def _handle_selection_for_auto_copy(self, text: str) -> None:
        """Handle text selection - auto-copy to clipboard if enabled.

        Args:
            text: Selected text from terminal
        """
        if self.auto_copy_on_selection and text:
            self._copy_to_clipboard(text)
            logger.debug(f"✂️  Auto-copied {len(text)} characters on selection")

    def _handle_middle_click(self, pos: QPoint) -> None:
        """Handle middle mouse button click - paste clipboard content if enabled.

        Args:
            pos: Position of the middle-click (not used, but provided by signal)
        """
        if self.middle_click_paste_enabled:
            self._paste_from_clipboard()
            logger.debug(f"🖱️  Middle-click paste at ({pos.x()}, {pos.y()})")

    # Phase 4: Context menu customization API for developers

    def set_context_menu_handler(
        self, handler: Callable[[QPoint, str], Optional[QMenu]]
    ) -> None:
        """Set a custom context menu handler.

        Args:
            handler: Function that takes (position, selected_text) and returns QMenu or None
        """
        self.custom_context_menu_handler = handler
        logger.debug("Custom context menu handler set")

    def add_context_menu_action(self, action: QAction) -> None:
        """Add a custom action to the default context menu.

        Args:
            action: QAction to add to the context menu
        """
        self.custom_context_actions.append(action)
        logger.debug(f"Added custom context menu action: {action.text()}")

    def remove_context_menu_action(self, action: QAction) -> None:
        """Remove a custom action from the context menu.

        Args:
            action: QAction to remove
        """
        if action in self.custom_context_actions:
            self.custom_context_actions.remove(action)
            logger.debug(f"Removed custom context menu action: {action.text()}")

    def clear_context_menu_actions(self) -> None:
        """Clear all custom context menu actions."""
        self.custom_context_actions.clear()
        logger.debug("Cleared all custom context menu actions")

    def set_auto_copy_on_selection(self, enabled: bool) -> None:
        """Enable or disable automatic copying of selected text to clipboard.

        When enabled, any text selected in the terminal will be automatically
        copied to the system clipboard, similar to X11 PRIMARY selection behavior.

        Args:
            enabled: True to enable auto-copy, False to disable

        Example:
            terminal.set_auto_copy_on_selection(True)  # Auto-copy selected text
        """
        self.auto_copy_on_selection = enabled
        logger.info(f"Auto-copy on selection: {'enabled' if enabled else 'disabled'}")

    def set_middle_click_paste(self, enabled: bool) -> None:
        """Enable or disable paste on middle mouse button click.

        When enabled, clicking the middle mouse button will paste clipboard content
        at the cursor position, similar to X11 behavior.

        Args:
            enabled: True to enable middle-click paste, False to disable

        Example:
            terminal.set_middle_click_paste(True)  # Enable middle-click paste
            terminal.set_middle_click_paste(False)  # Disable middle-click paste
        """
        self.middle_click_paste_enabled = enabled
        logger.info(f"Middle-click paste: {'enabled' if enabled else 'disabled'}")

    def _setup_web_channel_bridge(self) -> None:
        """Set up QWebChannel bridge for JavaScript communication.

        This enables bidirectional communication between xterm.js running in the
        QWebEngineView and this Python widget. JavaScript can call methods on
        the bridge, and the bridge can emit signals that this widget listens to.
        """
        # Create bridge and web channel
        self.bridge = TerminalBridge(self)
        self.web_channel = QWebChannel(self)

        # Register the bridge object so JavaScript can access it
        self.web_channel.registerObject("terminalBridge", self.bridge)

        # Set the web channel on the QWebEngineView's page
        self.web_view.page().setWebChannel(self.web_channel)

        # Connect bridge signals to widget signals (Phase 3: Rich events)
        self._connect_bridge_signals()

        logger.debug("QWebChannel bridge set up successfully")

    def _connect_bridge_signals(self) -> None:
        """Connect TerminalBridge signals to TerminalWidget signals."""
        if not self.bridge:
            return

        # Connect rich events from the bridge to new Qt-compliant signals on this widget
        self.bridge.selection_changed.connect(
            lambda text: (
                self.selectionChanged.emit(text)
                if EventCategory.INTERACTION in self.event_config.enabled_categories
                else None
            )
        )
        self.bridge.cursor_moved.connect(
            lambda row, col: (
                self.cursor_moved.emit(row, col)
                if EventCategory.INTERACTION in self.event_config.enabled_categories
                else None
            )
        )
        self.bridge.bell_rang.connect(
            lambda: (
                self.bellActivated.emit()
                if EventCategory.APPEARANCE in self.event_config.enabled_categories
                else None
            )
        )
        self.bridge.title_changed.connect(
            lambda title: (
                self.titleChanged.emit(title)
                if EventCategory.APPEARANCE in self.event_config.enabled_categories
                else None
            )
        )
        self.bridge.key_pressed.connect(
            lambda key, code, ctrl, alt, shift: self._emit_key_event(
                key, code, ctrl, alt, shift
            )
        )
        self.bridge.data_received.connect(
            lambda data: (
                self.inputSent.emit(data)
                if EventCategory.CONTENT in self.event_config.enabled_categories
                else None
            )
        )
        self.bridge.scroll_occurred.connect(
            lambda pos: (
                self.scrollOccurred.emit(pos)
                if EventCategory.APPEARANCE in self.event_config.enabled_categories
                else None
            )
        )
        self.bridge.shortcut_pressed.connect(
            lambda action_id: self.shortcutPressed.emit(action_id)
        )

        # OSC 7: Working directory tracking
        self.bridge.working_directory_changed.connect(
            lambda cwd: self._on_working_directory_changed(cwd)
        )

        logger.debug("Bridge signals connected to widget signals")

    def _emit_key_event(
        self, key: str, code: str, ctrl: bool, alt: bool, shift: bool
    ) -> None:
        """Emit structured key event with category checking."""
        if EventCategory.INTERACTION in self.event_config.enabled_categories:
            key_event = KeyEvent(key=key, code=code, ctrl=ctrl, alt=alt, shift=shift)
            self.keyPressed.emit(key_event)

    def _on_working_directory_changed(self, cwd: str) -> None:
        """Handle CWD change from terminal.

        Args:
            cwd: New current working directory
        """
        self._current_working_directory = cwd
        self.workingDirectoryChanged.emit(cwd)
        logger.info(f"Terminal CWD changed: {cwd}")

    def get_current_working_directory(self) -> Optional[str]:
        """Get current working directory of the terminal.

        Returns:
            Current working directory path, or None if not yet reported via OSC 7
        """
        return self._current_working_directory

    def _start_terminal(self) -> None:
        """Start the terminal server and load the terminal."""
        try:
            if self.server_url:
                # Use external server
                logger.info(f"Connecting to external server: {self.server_url}")
                self._load_terminal_url(self.server_url)
            else:
                # Start embedded server
                logger.info("Starting embedded terminal server")
                self.server = EmbeddedTerminalServer(
                    command=self.command,
                    args=self.args,
                    cwd=self.cwd,
                    env=self.env,
                    port=self.port,
                    host=self.host,
                    capture_output=self.capture_output,
                )

                # Connect server signals
                self._connect_server_signals()

                # Start server
                actual_port = self.server.start()
                terminal_url = f"http://{self.host}:{actual_port}"

                # Give server a moment to start
                QThread.msleep(200)

                # Load terminal
                self._load_terminal_url(terminal_url)
                if EventCategory.LIFECYCLE in self.event_config.enabled_categories:
                    self.serverStarted.emit(terminal_url)
                logger.info(f"Terminal server started at {terminal_url}")

        except Exception as e:
            logger.error(f"Failed to start terminal: {e}")
            self._show_error(f"Terminal failed to start:\n{str(e)}")

    def _connect_server_signals(self) -> None:
        """Connect signals from embedded server."""
        if not self.server:
            return

        logger.debug("Connecting server signals")
        # Connect server signals to widget signals
        if hasattr(self.server, "output_received"):
            self.server.output_received.connect(self._handle_output)
        if hasattr(self.server, "process_started"):
            self.server.process_started.connect(lambda: self._on_command_started())
        if hasattr(self.server, "process_ended"):
            self.server.process_ended.connect(self._on_command_finished)

    def _on_command_started(self) -> None:
        """Handle command started event."""
        logger.debug(f"Command started: {self.command}")

        # Create structured process event data
        process_event = ProcessEvent(
            command=self.command,
            pid=self.server.child_pid if self.server else None,
            working_directory=self.cwd,
        )

        if EventCategory.PROCESS in self.event_config.enabled_categories:
            self.processStarted.emit(process_event)

    def _on_command_finished(self, exit_code: int) -> None:
        """Handle command finished event."""
        logger.debug(f"Command finished with exit code: {exit_code}")

        if EventCategory.PROCESS in self.event_config.enabled_categories:
            self.processFinished.emit(exit_code)

    def _load_terminal_url(self, url: str) -> None:
        """Load terminal URL in web view."""
        logger.debug(f"Loading terminal URL: {url}")
        self.web_view.load(QUrl(url))

    def _on_load_finished(self, success: bool) -> None:
        """Handle terminal page load completion."""
        if success:
            logger.info("Terminal loaded successfully")
            self.is_connected = True

            # Inject any custom configuration BEFORE emitting ready signal
            # This ensures theme is applied before the tab becomes visible
            self._configure_terminal()

            # Now signal that terminal is ready (tab can be shown)
            if EventCategory.LIFECYCLE in self.event_config.enabled_categories:
                self.terminalReady.emit()
            logger.debug("Emitted terminal_ready signal")
        else:
            logger.error("Failed to load terminal")
            if EventCategory.LIFECYCLE in self.event_config.enabled_categories:
                self.connectionLost.emit()
            logger.debug("Emitted connection_lost signal")

    def _configure_terminal(self) -> None:
        """Configure terminal after loading."""
        # Apply terminal configuration (behavior options)
        if self._terminal_config:
            self._apply_config(self._terminal_config)

        # Apply legacy theme (old string-based theme parameter)
        if self._user_theme:
            self._apply_theme(self._user_theme)

        # Apply terminal theme (new dict-based theme)
        if self._current_terminal_theme:
            self._apply_theme(self._current_terminal_theme)

        # Set read-only mode if requested
        if self.read_only:
            self.set_read_only(True)

    def _apply_theme(self, theme_config: dict) -> None:
        """Apply terminal theme by injecting JavaScript to xterm.js.

        Args:
            theme_config: Dictionary with terminal configuration including
                         colors, fonts, and other xterm.js options.
                         Can also be a string for legacy theme names (ignored).
        """
        if not self.web_view:
            logger.warning("Cannot apply theme - web_view not initialized")
            return

        # Handle legacy string theme parameter (from old implementation)
        if isinstance(theme_config, str):
            logger.debug(f"Ignoring legacy string theme: {theme_config}")
            return

        # Extract terminal configuration
        terminal = theme_config.get("terminal", theme_config)

        # Build JavaScript to update xterm.js configuration
        font_family = terminal.get(
            "fontFamily", "Consolas, Monaco, 'Courier New', monospace"
        )
        font_size = terminal.get("fontSize", 14)
        line_height = terminal.get("lineHeight", 1.2)
        letter_spacing = terminal.get("letterSpacing", 0)
        cursor_blink = str(terminal.get("cursorBlink", True)).lower()
        cursor_style = terminal.get("cursorStyle", "block")

        # Colors
        background = terminal.get("background", "#1e1e1e")
        foreground = terminal.get("foreground", "#d4d4d4")
        cursor = terminal.get("cursor", "#ffcc00")
        cursor_accent = terminal.get("cursorAccent", "#1e1e1e")
        selection = terminal.get("selectionBackground", "rgba(38, 79, 120, 0.3)")

        # ANSI colors
        black = terminal.get("black", "#000000")
        red = terminal.get("red", "#cd3131")
        green = terminal.get("green", "#0dbc79")
        yellow = terminal.get("yellow", "#e5e510")
        blue = terminal.get("blue", "#2472c8")
        magenta = terminal.get("magenta", "#bc3fbc")
        cyan = terminal.get("cyan", "#11a8cd")
        white = terminal.get("white", "#e5e5e5")
        bright_black = terminal.get("brightBlack", "#555753")
        bright_red = terminal.get("brightRed", "#f14c4c")
        bright_green = terminal.get("brightGreen", "#23d18b")
        bright_yellow = terminal.get("brightYellow", "#f5f543")
        bright_blue = terminal.get("brightBlue", "#3b8eea")
        bright_magenta = terminal.get("brightMagenta", "#d670d6")
        bright_cyan = terminal.get("brightCyan", "#29b8db")
        bright_white = terminal.get("brightWhite", "#f5f5f5")

        # Escape font family for JavaScript (replace single quotes with escaped quotes)
        font_family_escaped = font_family.replace("'", "\\'")

        js_code = f"""
        if (typeof term !== 'undefined') {{
            // Update font settings
            term.options.fontFamily = '{font_family_escaped}';
            term.options.fontSize = {font_size};
            term.options.lineHeight = {line_height};
            term.options.letterSpacing = {letter_spacing};
            term.options.cursorBlink = {cursor_blink};
            term.options.cursorStyle = '{cursor_style}';

            // Update color theme
            term.options.theme = {{
                background: '{background}',
                foreground: '{foreground}',
                cursor: '{cursor}',
                cursorAccent: '{cursor_accent}',
                selectionBackground: '{selection}',
                black: '{black}',
                red: '{red}',
                green: '{green}',
                yellow: '{yellow}',
                blue: '{blue}',
                magenta: '{magenta}',
                cyan: '{cyan}',
                white: '{white}',
                brightBlack: '{bright_black}',
                brightRed: '{bright_red}',
                brightGreen: '{bright_green}',
                brightYellow: '{bright_yellow}',
                brightBlue: '{bright_blue}',
                brightMagenta: '{bright_magenta}',
                brightCyan: '{bright_cyan}',
                brightWhite: '{bright_white}'
            }};

            console.log('Terminal theme applied: {theme_config.get("name", "custom")}');
        }} else {{
            console.error('Terminal not initialized - cannot apply theme');
        }}
        """

        self.web_view.page().runJavaScript(js_code)
        logger.info(f"Applied terminal theme: {theme_config.get('name', 'custom')}")

    def _apply_config(self, config: dict) -> None:
        """Apply terminal configuration to xterm.js instance via JavaScript injection.

        Args:
            config: Dictionary with configuration options like scrollback, cursorBlink, etc.
        """
        if not self.web_view:
            logger.warning("Cannot apply terminal config: web_view not initialized")
            return

        # Build JavaScript code to update terminal options
        js_updates = []

        # Map of config keys to JavaScript property names (most are the same)
        config_mapping = {
            "scrollback": "scrollback",
            "cursorBlink": "cursorBlink",
            "cursorStyle": "cursorStyle",
            "tabStopWidth": "tabStopWidth",
            "bellStyle": "bellStyle",
            "scrollSensitivity": "scrollSensitivity",
            "fastScrollSensitivity": "fastScrollSensitivity",
            "fastScrollModifier": "fastScrollModifier",
            "rightClickSelectsWord": "rightClickSelectsWord",
            "convertEol": "convertEol",
        }

        for config_key, js_prop in config_mapping.items():
            if config_key in config:
                value = config[config_key]
                # Handle string values vs numeric/boolean
                if isinstance(value, str):
                    js_updates.append(f"term.options.{js_prop} = '{value}';")
                elif isinstance(value, bool):
                    js_value = "true" if value else "false"
                    js_updates.append(f"term.options.{js_prop} = {js_value};")
                else:
                    js_updates.append(f"term.options.{js_prop} = {value};")

        if not js_updates:
            logger.debug("No configuration changes to apply")
            return

        js_code = f"""
        if (typeof term !== 'undefined') {{
            {chr(10).join("            " + update for update in js_updates)}
            console.log('Terminal configuration updated');
        }} else {{
            console.error('Terminal not initialized - cannot apply configuration');
        }}
        """

        self.web_view.page().runJavaScript(js_code)
        logger.info(f"Applied terminal configuration: {', '.join(config.keys())}")

    def _handle_output(self, data: str) -> None:
        """Handle output from terminal."""
        # Apply filter if provided
        if self.output_filter:
            data = self.output_filter(data)

        # Parse if parser provided
        if self.output_parser:
            data = self.output_parser(data)

        # Store in buffer if capturing
        if self.capture_output and self.output_buffer is not None:
            self.output_buffer.append(data)

        # Emit signal
        if EventCategory.CONTENT in self.event_config.enabled_categories:
            self.outputReceived.emit(data)

    def _get_initial_background_color(self) -> str:
        """Get initial background color for WebView.

        Checks terminal config, then application theme type to return
        an appropriate static fallback that prevents flash on startup.

        Returns:
            Hex color string for background
        """
        # If terminal theme config provided, use it
        if self._terminal_config and "background" in self._terminal_config:
            return self._terminal_config["background"]

        # Check application theme type for appropriate fallback
        try:
            from PySide6.QtWidgets import QApplication

            app = QApplication.instance()
            if app and hasattr(app, "get_current_theme"):
                current_theme = app.get_current_theme()
                if current_theme and hasattr(current_theme, "type"):
                    # Return appropriate static color based on theme type
                    if current_theme.type == "dark":
                        return "#1e1e1e"  # Dark background (xterm.js default)
                    else:
                        return "#ffffff"  # Light background
        except Exception:
            pass  # Continue to fallback

        # Default fallback to dark (prevents white flash on startup)
        return "#1e1e1e"

    def _get_error_color(self) -> str:
        """Get theme-aware error color.

        Returns:
            Hex color string for error messages
        """
        try:
            from vfwidgets_theme import ColorTokenRegistry

            # Try to get error color from theme
            return ColorTokenRegistry.get("errorForeground", fallback="#ff0000")
        except ImportError:
            # Theme system not available, use red as fallback
            return "#ff0000"

    def _show_error(self, message: str) -> None:
        """Display error message in the widget."""
        from PySide6.QtWidgets import QLabel

        error_label = QLabel(message)
        error_label.setWordWrap(True)

        # Use theme-aware error color
        error_color = self._get_error_color()
        error_label.setStyleSheet(f"QLabel {{ color: {error_color}; padding: 10px; }}")

        self.layout().addWidget(error_label)

    # Public API methods

    def send_command(self, command: str) -> None:
        """Send a command to the terminal.

        Args:
            command: Command to execute
        """
        logger.debug(f"Sending command: {command}")
        self.send_input(command + "\n")

    def send_input(self, text: str) -> None:
        """Send raw input to the terminal.

        Args:
            text: Text to send
        """
        if self.server:
            # Embedded server - send via server object
            self.server.send_input(text)
        else:
            # External server - send via JavaScript to xterm.js
            # Escape text for JavaScript string literal
            escaped = (
                text.replace("\\", "\\\\")
                .replace("'", "\\'")
                .replace("\n", "\\n")
                .replace("\r", "\\r")
            )
            js_code = f"""
                (function() {{
                    const urlParams = new URLSearchParams(window.location.search);
                    const sessionId = urlParams.get('session_id');
                    const payload = {{ input: '{escaped}' }};
                    if (sessionId) {{
                        payload.session_id = sessionId;
                    }}
                    window.terminalSocket.emit('pty-input', payload);
                }})();
            """
            self.web_view.page().runJavaScript(js_code)

        if EventCategory.CONTENT in self.event_config.enabled_categories:
            self.inputSent.emit(text)

    def clear(self) -> None:
        """Clear the terminal screen."""
        self.send_input("\x0c")  # Ctrl+L

    def clear_terminal(self) -> None:
        """Clear the terminal screen (alias for clear)."""
        logger.info("🧹 Clearing terminal screen via context menu")
        self.clear()

    def reset(self) -> None:
        """Reset terminal state."""
        if self.server:
            self.server.reset_terminal()

    def set_terminal_theme(self, theme: dict) -> None:
        """Set terminal-specific theme.

        This applies colors, fonts, and other visual settings specific to the
        terminal, independent of the application theme.

        The theme is stored and will be applied:
        - Immediately if the terminal is already loaded
        - After page load if the terminal is still initializing

        Args:
            theme: Terminal theme dictionary with 'terminal' key containing:
                  - fontFamily: Font family string
                  - fontSize: Font size in points
                  - background, foreground: Main colors
                  - cursor, cursorAccent: Cursor colors
                  - selectionBackground: Selection highlight color
                  - black, red, green, yellow, blue, magenta, cyan, white: ANSI colors
                  - brightBlack, brightRed, ... brightWhite: Bright ANSI colors

        Example:
            theme = {
                "name": "My Theme",
                "terminal": {
                    "fontFamily": "Monaco",
                    "fontSize": 14,
                    "background": "#1e1e1e",
                    "foreground": "#d4d4d4",
                    ...
                }
            }
            terminal.set_terminal_theme(theme)
        """
        self._current_terminal_theme = theme

        # Apply theme if terminal is already loaded, otherwise it will be
        # applied in _configure_terminal() after page load
        if self.is_connected and self.web_view:
            self._apply_theme(theme)
        else:
            logger.debug(
                f"Stored terminal theme (will apply after load): {theme.get('name', 'custom')}"
            )

    def get_terminal_theme(self) -> dict:
        """Get current terminal theme configuration.

        Returns:
            Dictionary with current terminal theme settings, or empty dict if none set
        """
        return (
            self._current_terminal_theme.copy() if self._current_terminal_theme else {}
        )

    def set_terminal_config(self, config: dict) -> None:
        """Set terminal configuration options.

        This configures xterm.js behavior options like scrollback, cursor style,
        bell behavior, etc. These are independent of visual theme settings.

        The configuration is stored and will be applied:
        - Immediately if the terminal is already loaded
        - After page load if the terminal is still initializing

        Args:
            config: Terminal configuration dictionary with options like:
                   - scrollback: Number of scrollback lines (default: 1000)
                   - cursorBlink: Whether cursor blinks (default: true)
                   - cursorStyle: 'block', 'underline', or 'bar' (default: 'block')
                   - tabStopWidth: Width of tab stops (default: 4)
                   - bellStyle: 'none', 'sound', or 'visual' (default: 'none')
                   - scrollSensitivity: Mouse wheel scroll speed (default: 1)
                   - fastScrollSensitivity: Shift+scroll speed (default: 5)
                   - fastScrollModifier: 'alt', 'ctrl', or 'shift' (default: 'shift')
                   - rightClickSelectsWord: Select word on right click (default: false)
                   - convertEol: Convert \\n to \\r\\n (default: false)

        Example:
            config = {
                "scrollback": 10000,
                "cursorBlink": true,
                "cursorStyle": "block",
                "bellStyle": "visual"
            }
            terminal.set_terminal_config(config)
        """
        self._terminal_config = config.copy()

        # Apply configuration if terminal is already loaded
        if self.is_connected and self.web_view:
            self._apply_config(config)
        else:
            logger.debug("Stored terminal configuration (will apply after load)")

    def get_terminal_config(self) -> dict:
        """Get current terminal configuration options.

        Returns:
            Dictionary with current terminal configuration, or empty dict if none set
        """
        return self._terminal_config.copy() if self._terminal_config else {}

    def get_output(self, last_n_lines: Optional[int] = None) -> str:
        """Get terminal output as string.

        Args:
            last_n_lines: Number of last lines to retrieve

        Returns:
            Terminal output as string
        """
        if not self.capture_output or not self.output_buffer:
            return ""

        lines = self.output_buffer
        if last_n_lines:
            lines = lines[-last_n_lines:]
        return "".join(lines)

    def save_output(self, filepath: str) -> None:
        """Save terminal output to file.

        Args:
            filepath: Path to save file
        """
        output = self.get_output()
        with open(filepath, "w") as f:
            f.write(output)

    def set_read_only(self, read_only: bool) -> None:
        """Set terminal read-only mode.

        Args:
            read_only: Whether terminal should be read-only
        """
        self.read_only = read_only
        # This would inject JavaScript to disable input

    def execute_script(self, script: str) -> None:
        """Execute a multi-line script.

        Args:
            script: Script to execute
        """
        for line in script.splitlines():
            if line.strip():
                self.send_command(line)
                QThread.msleep(100)  # Small delay between commands

    def get_process_info(self) -> dict[str, Any]:
        """Get information about the running process.

        Returns:
            Dictionary with process information
        """
        if self.server:
            return self.server.get_process_info()
        return {}

    def set_working_directory(self, path: str) -> None:
        """Change working directory.

        Args:
            path: New working directory
        """
        self.send_command(f"cd {path}")

    def close_terminal(self) -> None:
        """Close the terminal and cleanup resources."""
        logger.info("Closing terminal")

        if self.server:
            exit_code = self.server.stop()
            self.server = None
            if EventCategory.LIFECYCLE in self.event_config.enabled_categories:
                self.terminalClosed.emit(exit_code or 0)

        self.is_connected = False

    # Phase 5: Advanced Developer API Methods

    def get_selected_text(self) -> str:
        """Get currently selected text in the terminal.

        Returns:
            Selected text or empty string if no selection
        """
        if self.bridge:
            return getattr(self.bridge, "_last_selection", "")
        return ""

    def get_cursor_position(self) -> tuple[int, int]:
        """Get current cursor position.

        Returns:
            Tuple of (row, col) or (0, 0) if unavailable
        """
        # This would need to be implemented via JavaScript bridge in the future
        logger.debug("get_cursor_position not yet fully implemented")
        return (0, 0)

    def get_current_line(self) -> str:
        """Get the current line where cursor is located.

        Returns:
            Current line text or empty string if unavailable
        """
        # This would need to be implemented via JavaScript bridge in the future
        logger.debug("get_current_line not yet fully implemented")
        return ""

    def set_theme(self, theme_dict: dict[str, str]) -> None:
        """Set terminal color theme.

        Args:
            theme_dict: Dictionary with color definitions (background, foreground, etc.)
        """
        self._user_theme = theme_dict
        # Inject JavaScript to update xterm.js theme
        if self.web_view and self.is_connected:
            js_theme = json.dumps(theme_dict)
            # Use setOption('theme', ...) - the proper xterm.js v4 API method
            # This creates a new theme object and triggers proper update/repaint
            js_code = f"if (window.terminal) {{ window.terminal.setOption('theme', {js_theme}); }}"
            self.inject_javascript(js_code)
        logger.debug(f"Theme updated: {len(theme_dict)} colors")

    def _get_current_theme_type(self) -> str:
        """Get current theme type (dark/light) for theme-aware fallbacks.

        Uses self._current_theme_name which is updated BEFORE on_theme_changed()
        is called, ensuring we always get the correct theme type.

        Returns:
            Theme type string: 'dark', 'light', or 'dark' (default)
        """
        try:
            # Use self._current_theme_name (already updated by ThemedWidget)
            # and lookup the theme from the theme manager by name
            if hasattr(self, "_current_theme_name") and self._current_theme_name:
                from vfwidgets_theme import ThemedApplication

                app = ThemedApplication.instance()
                if app and hasattr(app, "_theme_manager") and app._theme_manager:
                    # Get theme by name from theme manager (not from _current_theme which is stale)
                    theme = app._theme_manager.get_theme(self._current_theme_name)
                    if theme and hasattr(theme, "type"):
                        return theme.type
        except Exception as e:
            logger.error(f"Error getting theme type: {e}")

        # Default to dark if we can't determine
        return "dark"

    def on_theme_changed(self) -> None:
        """Called automatically when the application theme changes.

        This method is only available when vfwidgets-theme is installed.
        It converts theme system tokens to xterm.js ITheme format.
        """
        if not THEME_AVAILABLE:
            return

        # Get current theme type for theme-aware fallbacks
        theme_type = self._get_current_theme_type()

        # Theme-aware fallbacks for main colors
        if theme_type == "light":
            main_fallbacks = {
                "background": "#ffffff",  # White background
                "foreground": "#000000",  # Black text
                "cursor": "#000000",  # Black cursor
                "cursorAccent": "#ffffff",  # White cursor accent
                "selectionBackground": "#add6ff",  # Light blue selection
            }
        else:  # dark or unknown
            main_fallbacks = {
                "background": "#1e1e1e",  # Dark gray background
                "foreground": "#d4d4d4",  # Light gray text
                "cursor": "#d4d4d4",  # Light gray cursor
                "cursorAccent": "#1e1e1e",  # Dark gray cursor accent
                "selectionBackground": "#264f78",  # Dark blue selection
            }

        # Standard ANSI color fallbacks (same for light and dark)
        ansi_fallbacks = {
            "black": "#2e3436",
            "red": "#cc0000",
            "green": "#4e9a06",
            "yellow": "#c4a000",
            "blue": "#3465a4",
            "magenta": "#75507b",
            "cyan": "#06989a",
            "white": "#d3d7cf",
            "brightBlack": "#555753",
            "brightRed": "#ef2929",
            "brightGreen": "#8ae234",
            "brightYellow": "#fce94f",
            "brightBlue": "#729fcf",
            "brightMagenta": "#ad7fa8",
            "brightCyan": "#34e2e2",
            "brightWhite": "#eeeeec",
        }

        # Build xterm.js theme dict using theme-aware fallbacks
        # Note: Built-in themes don't populate editor.* tokens, so we use fallbacks
        # directly instead of checking self.theme properties (which may have stale cached values)
        xterm_theme = {
            "background": main_fallbacks["background"],
            "foreground": main_fallbacks["foreground"],
            "cursor": main_fallbacks["cursor"],
            "cursorAccent": main_fallbacks["cursorAccent"],
            "selectionBackground": main_fallbacks["selectionBackground"],
            # ANSI colors with standard fallbacks
            "black": self.theme.black or ansi_fallbacks["black"],
            "red": self.theme.red or ansi_fallbacks["red"],
            "green": self.theme.green or ansi_fallbacks["green"],
            "yellow": self.theme.yellow or ansi_fallbacks["yellow"],
            "blue": self.theme.blue or ansi_fallbacks["blue"],
            "magenta": self.theme.magenta or ansi_fallbacks["magenta"],
            "cyan": self.theme.cyan or ansi_fallbacks["cyan"],
            "white": self.theme.white or ansi_fallbacks["white"],
            "brightBlack": self.theme.brightBlack or ansi_fallbacks["brightBlack"],
            "brightRed": self.theme.brightRed or ansi_fallbacks["brightRed"],
            "brightGreen": self.theme.brightGreen or ansi_fallbacks["brightGreen"],
            "brightYellow": self.theme.brightYellow or ansi_fallbacks["brightYellow"],
            "brightBlue": self.theme.brightBlue or ansi_fallbacks["brightBlue"],
            "brightMagenta": self.theme.brightMagenta
            or ansi_fallbacks["brightMagenta"],
            "brightCyan": self.theme.brightCyan or ansi_fallbacks["brightCyan"],
            "brightWhite": self.theme.brightWhite or ansi_fallbacks["brightWhite"],
        }

        # Debug logging
        print(f"🎨 Terminal theme switching: {theme_type}")
        print(f"   Background: {xterm_theme['background']}")
        print(f"   Foreground: {xterm_theme['foreground']}")

        # Apply theme to xterm.js
        self.set_theme(xterm_theme)

    def add_search_highlight(self, text: str, case_sensitive: bool = False) -> None:
        """Highlight text in the terminal.

        Args:
            text: Text to highlight
            case_sensitive: Whether search should be case sensitive
        """
        if self.web_view and self.is_connected:
            js_text = json.dumps(text)
            js_code = f"""
            if (window.terminal && window.terminal.searchAddon) {{
                window.terminal.searchAddon.findNext({js_text}, {{ caseSensitive: {str(case_sensitive).lower()} }});
            }}
            """
            self.inject_javascript(js_code)
        logger.debug(f"Added search highlight for: {text}")

    def scroll_to_line(self, line_number: int) -> None:
        """Scroll terminal to specific line.

        Args:
            line_number: Line number to scroll to (0-based)
        """
        if self.web_view and self.is_connected:
            js_code = f"""
            if (window.terminal) {{
                window.terminal.scrollToLine({line_number});
            }}
            """
            self.inject_javascript(js_code)
        logger.debug(f"Scrolled to line: {line_number}")

    def inject_javascript(self, js_code: str) -> None:
        """Execute custom JavaScript in the terminal context.

        Args:
            js_code: JavaScript code to execute
        """
        if self.web_view and self.web_view.page():
            self.web_view.page().runJavaScript(js_code)
            logger.debug(f"Injected JavaScript: {js_code[:100]}...")
        else:
            logger.warning("Cannot inject JavaScript: web view not ready")

    def add_keyboard_shortcut(
        self, key_combination: str, callback: Callable[[], None]
    ) -> None:
        """Add custom keyboard shortcut.

        Args:
            key_combination: Key combination (e.g., 'Ctrl+Shift+T')
            callback: Function to call when shortcut is pressed

        Note:
            This is a simplified version. Full implementation would require
            more sophisticated key handling via the bridge.
        """
        # Store the callback for future use
        if not hasattr(self, "_keyboard_shortcuts"):
            self._keyboard_shortcuts = {}

        self._keyboard_shortcuts[key_combination] = callback
        logger.debug(f"Added keyboard shortcut: {key_combination}")

        # In a full implementation, this would set up JavaScript event handlers
        # via the bridge to detect the key combination and call the callback

    def get_terminal_dimensions(self) -> tuple[int, int]:
        """Get terminal dimensions in characters.

        Returns:
            Tuple of (rows, cols)
        """
        return (self.rows, self.cols)

    def set_terminal_size(self, rows: int, cols: int) -> None:
        """Set terminal size in characters.

        Args:
            rows: Number of rows
            cols: Number of columns
        """
        self.rows = rows
        self.cols = cols
        if self.server:
            self.server.resize(rows, cols)

        # Also update xterm.js dimensions
        if self.web_view and self.is_connected:
            js_code = f"""
            if (window.terminal && window.terminal.resize) {{
                window.terminal.resize({cols}, {rows});
            }}
            """
            self.inject_javascript(js_code)

        if EventCategory.APPEARANCE in self.event_config.enabled_categories:
            self.sizeChanged.emit(rows, cols)
        logger.debug(f"Terminal resized to {rows}x{cols}")

    def get_scrollback_buffer(self) -> list[str]:
        """Get scrollback buffer content.

        Returns:
            List of lines in scrollback buffer
        """
        if self.capture_output and self.output_buffer:
            return self.output_buffer.copy()
        return []

    def clear_scrollback_buffer(self) -> None:
        """Clear the scrollback buffer."""
        if self.capture_output and self.output_buffer:
            self.output_buffer.clear()

        # Clear xterm.js scrollback
        if self.web_view and self.is_connected:
            js_code = "if (window.terminal) { window.terminal.clear(); }"
            self.inject_javascript(js_code)

        logger.debug("Scrollback buffer cleared")

    def reset_zoom(self) -> None:
        """Reset terminal zoom/magnification to 100% (default).

        This is useful when users accidentally zoom in/out using Ctrl+scroll
        or Ctrl+plus/minus in the web-based terminal.
        """
        if self.web_view:
            self.web_view.setZoomFactor(1.0)
            logger.debug("Terminal zoom reset to 100%")
        else:
            logger.warning("Cannot reset zoom - web_view not initialized")

    def set_zoom_factor(self, factor: float) -> None:
        """Set terminal zoom/magnification factor.

        Args:
            factor: Zoom factor (1.0 = 100%, 1.5 = 150%, 0.8 = 80%, etc.)
                   Typical range is 0.25 to 5.0

        Example:
            terminal.set_zoom_factor(1.5)  # 150% zoom
            terminal.set_zoom_factor(0.8)  # 80% zoom
        """
        if self.web_view:
            # Clamp to reasonable range
            factor = max(0.25, min(5.0, factor))
            self.web_view.setZoomFactor(factor)
            logger.debug(f"Terminal zoom set to {factor * 100:.0f}%")
        else:
            logger.warning("Cannot set zoom - web_view not initialized")

    def get_zoom_factor(self) -> float:
        """Get current terminal zoom/magnification factor.

        Returns:
            Current zoom factor (1.0 = 100%, 1.5 = 150%, etc.)
            Returns 1.0 if web_view not initialized
        """
        if self.web_view:
            return self.web_view.zoomFactor()
        else:
            logger.warning("Cannot get zoom - web_view not initialized")
            return 1.0

    def enable_logging(self, log_level: str = "INFO") -> None:
        """Enable or change logging level.

        Args:
            log_level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR')
        """
        level = getattr(logging, log_level.upper(), logging.INFO)
        logger.setLevel(level)
        logger.info(f"Logging level set to {log_level}")

    # Note: We don't override focusInEvent/focusOutEvent because QWebEngineView
    # doesn't propagate focus events properly. Instead, we use an event filter
    # on the focus proxy in _setup_focus_detection() and eventFilter() methods.

    def resizeEvent(self, event) -> None:
        """Handle resize event."""
        logger.debug(
            f"Terminal widget resized to {event.size().width()}x{event.size().height()}"
        )
        super().resizeEvent(event)
        # Terminal will handle resize through xterm.js fit addon

    def showEvent(self, event) -> None:
        """Handle show event."""
        logger.debug("Terminal widget shown")
        super().showEvent(event)

    def hideEvent(self, event) -> None:
        """Handle hide event."""
        logger.debug("Terminal widget hidden")
        super().hideEvent(event)

    def closeEvent(self, event) -> None:
        """Handle widget close event."""
        logger.debug("Terminal widget closing")
        self.close_terminal()
        super().closeEvent(event)
