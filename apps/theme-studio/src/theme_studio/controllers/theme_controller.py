"""Theme Controller - MVC Controller for theme editing operations.

This controller implements the Command Pattern to decouple UI interactions
from document updates. It uses a command queue with deferred execution to
ensure that all UI events (like dialog cleanup) complete before theme
updates are applied.

Architecture:
    UI (InspectorPanel) → ThemeController.queue_*() → Command Queue → Document

This prevents lifecycle issues where modal dialogs interfere with theme
updates, eliminating segmentation faults caused by Qt object lifetime conflicts.
"""

import logging
from typing import List, Tuple

from PySide6.QtCore import QObject, QTimer

from ..models.theme_document import ThemeDocument

logger = logging.getLogger(__name__)


class ThemeController(QObject):
    """Controller for theme editing operations.

    Uses command queue pattern to defer document updates until after
    UI events have completed processing. This prevents Qt lifecycle
    conflicts that cause segfaults.

    Example:
        controller = ThemeController(document)

        # UI calls this - queues command, returns immediately
        controller.queue_token_change("button.background", "#FF0000")

        # Dialog closes, UI cleanup completes
        # ... then command executes on next event loop iteration
    """

    def __init__(self, document: ThemeDocument):
        """Initialize controller.

        Args:
            document: ThemeDocument to control
        """
        super().__init__()
        self._document = document
        self._pending_commands: List[Tuple] = []

        # Timer for deferred execution
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._execute_pending_commands)

    def queue_token_change(self, token_name: str, token_value: str) -> None:
        """Queue a token value change.

        The change will be applied on the next event loop iteration,
        ensuring proper event processing order.

        Args:
            token_name: Token to change (e.g., "button.background")
            token_value: New value (e.g., "#FF0000")
        """
        logger.debug(f"queue_token_change: Queuing {token_name}={token_value}")
        self._pending_commands.append(('set_token', token_name, token_value))

        # Start timer if not already running
        if not self._timer.isActive():
            logger.debug("queue_token_change: Starting deferred execution timer")
            self._timer.start(0)  # Execute on next event loop iteration
        else:
            logger.debug("queue_token_change: Timer already active, command added to queue")

    def _execute_pending_commands(self) -> None:
        """Execute all queued commands.

        This runs after the event loop has processed all pending UI events,
        ensuring safe execution when UI components (like dialogs) have
        completed their lifecycle.
        """
        logger.debug(f"_execute_pending_commands: START, {len(self._pending_commands)} commands queued")

        # Make a copy and clear immediately to prevent re-entrancy issues
        commands = self._pending_commands.copy()
        self._pending_commands.clear()

        # Execute each command
        for i, command in enumerate(commands):
            cmd_type = command[0]
            logger.debug(f"_execute_pending_commands: Executing command {i+1}/{len(commands)}: {cmd_type}")

            if cmd_type == 'set_token':
                _, token_name, token_value = command
                logger.debug(f"_execute_pending_commands: Setting token {token_name}={token_value}")
                self._document.set_token(token_name, token_value)
                logger.debug("_execute_pending_commands: Token set successfully")
            # Future commands can be added here (e.g., 'delete_token', 'rename_token')

        logger.debug("_execute_pending_commands: END")

    def get_document(self) -> ThemeDocument:
        """Get the controlled document.

        Returns:
            ThemeDocument instance
        """
        return self._document
