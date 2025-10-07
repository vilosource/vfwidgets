"""Terminal widget provider for MultisplitWidget integration."""

import logging
from typing import Optional

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

    def __init__(self, server: MultiSessionTerminalServer, event_filter=None) -> None:
        """Initialize terminal provider.

        Args:
            server: Shared MultiSessionTerminalServer instance
            event_filter: Optional QObject to install as event filter on terminals
        """
        self.server = server
        self.pane_to_session: dict[str, str] = {}  # Map pane_id -> session_id for cleanup
        self._default_theme: Optional[dict] = None  # Default terminal theme for new terminals
        self._default_config: Optional[dict] = None  # Default terminal config for new terminals
        self._event_filter = event_filter  # Event filter to install on terminals

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
        # Create session on shared server
        session_id = self.server.create_session(command="bash")
        logger.info(f"Created terminal session: {session_id} for pane: {pane_id}")

        # Store session mapping for cleanup
        self.pane_to_session[pane_id] = session_id

        # Get session URL
        session_url = self.server.get_session_url(session_id)

        # Create terminal widget connected to session
        # Pass configuration via constructor so it's applied during initialization
        terminal = TerminalWidget(
            server_url=session_url,
            terminal_config=self._default_config,
        )

        # Apply default theme if set (theme is applied after config in _configure_terminal)
        if self._default_theme:
            terminal.set_terminal_theme(self._default_theme)
            logger.debug(f"Applied default theme to terminal: {widget_id}")

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

                # Remove from tracking
                del self.pane_to_session[pane_id]

            except Exception as e:
                logger.error(f"Failed to terminate session {session_id}: {e}")
        else:
            logger.warning(f"No session found for pane {pane_id}")

    def set_default_theme(self, theme: dict) -> None:
        """Set default theme for new terminal widgets.

        Args:
            theme: Terminal theme dictionary
        """
        self._default_theme = theme.copy()
        logger.info(f"Set default terminal theme: {theme.get('name', 'custom')}")

    def get_default_theme(self) -> Optional[dict]:
        """Get current default theme.

        Returns:
            Default theme dictionary, or None if not set
        """
        return self._default_theme.copy() if self._default_theme else None

    def set_default_config(self, config: dict) -> None:
        """Set default configuration for new terminal widgets.

        Args:
            config: Terminal configuration dictionary
        """
        self._default_config = config.copy()
        logger.info(f"Set default terminal configuration")

    def get_default_config(self) -> Optional[dict]:
        """Get current default configuration.

        Returns:
            Default configuration dictionary, or None if not set
        """
        return self._default_config.copy() if self._default_config else None
