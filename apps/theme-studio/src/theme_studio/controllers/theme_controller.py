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
        self._pending_commands: list[tuple] = []

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
        self._pending_commands.append(("set_token", token_name, token_value))

        # Start timer if not already running
        if not self._timer.isActive():
            logger.debug("queue_token_change: Starting deferred execution timer")
            self._timer.start(0)  # Execute on next event loop iteration
        else:
            logger.debug("queue_token_change: Timer already active, command added to queue")

    def queue_metadata_change(self, field: str, value: str) -> None:
        """Queue a metadata field change.

        The change will be applied on the next event loop iteration,
        ensuring proper event processing order.

        Args:
            field: Metadata field to change (name, version, type, author, description)
            value: New field value
        """
        logger.debug(f"queue_metadata_change: Queuing {field}={value}")
        self._pending_commands.append(("set_metadata", field, value))

        # Start timer if not already running
        if not self._timer.isActive():
            logger.debug("queue_metadata_change: Starting deferred execution timer")
            self._timer.start(0)  # Execute on next event loop iteration
        else:
            logger.debug("queue_metadata_change: Timer already active, command added to queue")

    def _execute_pending_commands(self) -> None:
        """Execute all queued commands.

        This runs after the event loop has processed all pending UI events,
        ensuring safe execution when UI components (like dialogs) have
        completed their lifecycle.

        Creates QUndoCommand objects and pushes them to the undo stack.
        """
        logger.debug(
            f"_execute_pending_commands: START, {len(self._pending_commands)} commands queued"
        )

        # Make a copy and clear immediately to prevent re-entrancy issues
        commands = self._pending_commands.copy()
        self._pending_commands.clear()

        # Execute each command
        for i, command in enumerate(commands):
            cmd_type = command[0]
            logger.debug(
                f"_execute_pending_commands: Executing command {i + 1}/{len(commands)}: {cmd_type}"
            )

            if cmd_type == "set_token":
                _, token_name, token_value = command
                logger.debug(
                    f"_execute_pending_commands: Creating SetTokenCommand for {token_name}={token_value}"
                )

                # Get old value for undo
                old_value = self._document.get_token(token_name)

                # Create and push undo command
                from ..commands.token_commands import SetTokenCommand

                undo_command = SetTokenCommand(self._document, token_name, token_value, old_value)
                self._document._undo_stack.push(undo_command)
                logger.debug("_execute_pending_commands: Command pushed to undo stack")

            elif cmd_type == "set_metadata":
                _, field_name, field_value = command
                logger.debug(
                    f"_execute_pending_commands: Creating SetMetadataCommand for {field_name}={field_value}"
                )

                # Get old value for undo
                if field_name == "name":
                    old_value = self._document.theme.name
                elif field_name == "version":
                    old_value = self._document.theme.version
                elif field_name == "type":
                    old_value = self._document.theme.type
                elif field_name in ("author", "description"):
                    old_value = self._document.get_metadata_field(field_name, "")
                else:
                    logger.error(f"Unknown metadata field: {field_name}")
                    continue

                # Create and push undo command
                from ..commands.metadata_commands import SetMetadataCommand

                undo_command = SetMetadataCommand(
                    self._document, field_name, field_value, old_value
                )
                self._document._undo_stack.push(undo_command)
                logger.debug("_execute_pending_commands: Command pushed to undo stack")

            # Future commands can be added here (e.g., 'delete_token', 'rename_token')

        logger.debug("_execute_pending_commands: END")

    def get_document(self) -> ThemeDocument:
        """Get the controlled document.

        Returns:
            ThemeDocument instance
        """
        return self._document
