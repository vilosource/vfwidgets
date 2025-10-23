"""Terminal widget provider for MultisplitWidget integration."""

import logging
from typing import Callable, Optional

from PySide6.QtWidgets import QWidget

from vfwidgets_multisplit import WidgetProvider
from vfwidgets_terminal import TerminalWidget, MultiSessionTerminalServer

logger = logging.getLogger(__name__)


class TerminalProvider(WidgetProvider):
    """Provides TerminalWidget instances for MultisplitWidget panes.

    Creates terminal widgets on-demand for each pane, sharing a single
    MultiSessionTerminalServer for memory efficiency (63% reduction vs
    embedded servers).
    """

    def __init__(
        self, server_factory: Callable[[], MultiSessionTerminalServer], event_filter=None
    ) -> None:
        """Initialize terminal provider.

        Args:
            server_factory: Callable that returns/creates MultiSessionTerminalServer instance
                           (enables lazy initialization for ~500ms startup improvement)
            event_filter: Optional QObject to install as event filter on terminals
        """
        self._server_factory = server_factory
        self._server: Optional[MultiSessionTerminalServer] = None
        self.pane_to_session: dict[str, str] = {}  # Map pane_id -> session_id for cleanup
        self.session_to_pane: dict[str, str] = {}  # Map session_id -> pane_id for auto-close
        self._default_config: Optional[dict] = None  # Default terminal config for new terminals
        self._event_filter = event_filter  # Event filter to install on terminals

        # OSC 7: Working directory tracking
        self.pane_to_cwd: dict[str, Optional[str]] = {}  # Track CWD per pane
        self._next_terminal_cwd: Optional[str] = None  # CWD for next terminal creation

    @property
    def server(self) -> MultiSessionTerminalServer:
        """Get terminal server instance, creating on first access (lazy initialization).

        Returns:
            MultiSessionTerminalServer instance
        """
        if self._server is None:
            self._server = self._server_factory()
        return self._server

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Create a new terminal widget for a pane.

        Creates a unique terminal session on the shared server and
        returns a TerminalWidget connected to that session.

        Args:
            widget_id: Unique widget identifier
            pane_id: Pane identifier

        Returns:
            TerminalWidget connected to shared server session
        """
        # OSC 7: Get CWD for new terminal (if set by split operation)
        cwd = self._next_terminal_cwd
        self._next_terminal_cwd = None  # Clear for next use

        # Create session on shared server with CWD
        session_id = self.server.create_session(cwd=cwd)
        logger.info(
            f"Created terminal session: {session_id} for pane: {pane_id}"
            f"{f' with CWD: {cwd}' if cwd else ''}"
        )

        # Store bidirectional mapping for cleanup and auto-close
        self.pane_to_session[pane_id] = session_id
        self.session_to_pane[session_id] = pane_id

        # Get session URL
        session_url = self.server.get_session_url(session_id)

        # Create terminal widget connected to session
        # Pass configuration via constructor so it's applied during initialization
        # Theme is automatically applied via ThemedWidget inheritance
        terminal = TerminalWidget(
            server_url=session_url,
            terminal_config=self._default_config,
            cwd=cwd,  # OSC 7: Pass initial CWD to widget
        )

        # OSC 7: Connect CWD tracking signal
        terminal.workingDirectoryChanged.connect(
            lambda new_cwd: self._on_terminal_cwd_changed(pane_id, new_cwd)
        )

        # OSC 7: Initialize CWD tracking for this pane
        self.pane_to_cwd[pane_id] = cwd

        # Install event filter if provided
        if self._event_filter:
            terminal.installEventFilter(self._event_filter)
            logger.debug(f"Installed event filter on terminal: {widget_id}")

        logger.debug(f"Created terminal widget: {widget_id} (session: {session_id})")

        return terminal

    def widget_closing(self, widget_id: str, pane_id: str, widget: QWidget) -> None:
        """Clean up terminal session when pane closes.

        Called automatically by MultisplitWidget v0.2.0 before widget removal.
        Ensures terminal sessions are properly terminated on the server.

        Args:
            widget_id: Widget identifier
            pane_id: Pane identifier
            widget: The TerminalWidget being closed
        """
        # Get session_id from our tracking dict
        session_id = self.pane_to_session.get(pane_id)

        if session_id:
            try:
                # Terminate session on server
                self.server.destroy_session(session_id)
                logger.info(f"Terminated session {session_id} for pane {pane_id}")

                # Remove from both tracking dicts
                del self.pane_to_session[pane_id]
                if session_id in self.session_to_pane:
                    del self.session_to_pane[session_id]

                # OSC 7: Remove CWD tracking
                if pane_id in self.pane_to_cwd:
                    del self.pane_to_cwd[pane_id]

            except Exception as e:
                logger.error(f"Failed to terminate session {session_id}: {e}")
        else:
            logger.warning(f"No session found for pane {pane_id}")

    def set_default_config(self, config: dict) -> None:
        """Set default configuration for new terminal widgets.

        Args:
            config: Terminal configuration dictionary
        """
        self._default_config = config.copy()
        logger.info("Set default terminal configuration")

    def get_default_config(self) -> Optional[dict]:
        """Get current default configuration.

        Returns:
            Default configuration dictionary, or None if not set
        """
        return self._default_config.copy() if self._default_config else None

    def get_pane_for_session(self, session_id: str) -> Optional[str]:
        """Get pane_id associated with a session_id.

        Args:
            session_id: Terminal session ID

        Returns:
            Pane ID if found, None otherwise
        """
        return self.session_to_pane.get(session_id)

    def _on_terminal_cwd_changed(self, pane_id: str, cwd: str) -> None:
        """Track CWD changes for each pane (OSC 7 callback).

        Args:
            pane_id: Pane identifier
            cwd: New current working directory
        """
        self.pane_to_cwd[pane_id] = cwd
        logger.debug(f"Pane {pane_id[:8]} CWD updated: {cwd}")

    def get_pane_cwd(self, pane_id: str) -> Optional[str]:
        """Get current working directory for a pane (OSC 7).

        Args:
            pane_id: Pane identifier

        Returns:
            Current working directory path, or None if not known
        """
        return self.pane_to_cwd.get(pane_id)

    def set_next_terminal_cwd(self, cwd: Optional[str]) -> None:
        """Set CWD for the next terminal to be created (OSC 7).

        This is used when splitting panes to inherit the CWD from the focused terminal.

        Args:
            cwd: Current working directory path for next terminal
        """
        self._next_terminal_cwd = cwd
        logger.debug(f"Set next terminal CWD: {cwd}")
