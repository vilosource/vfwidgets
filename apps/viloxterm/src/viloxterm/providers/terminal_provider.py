"""Terminal widget provider for MultisplitWidget integration."""

import logging

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

    def __init__(self, server: MultiSessionTerminalServer) -> None:
        """Initialize terminal provider.

        Args:
            server: Shared MultiSessionTerminalServer instance
        """
        self.server = server
        self.pane_to_session: dict[str, str] = {}  # Map pane_id -> session_id for cleanup

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
        terminal = TerminalWidget(server_url=session_url)

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
