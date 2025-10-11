"""ReamdeApp - Application class with single-instance behavior."""

from pathlib import Path
from typing import Optional

from vfwidgets_common import SingleInstanceApplication

from .window import ReamdeWindow


class ReamdeApp(SingleInstanceApplication):
    """Reamde application with single-instance behavior.

    This application ensures only one instance runs at a time. When a second
    instance is launched, it sends the file path to the first instance and exits.

    Example:
        >>> app = ReamdeApp(sys.argv)
        >>> sys.exit(app.run(file_path="README.md"))
    """

    def __init__(self, argv: list[str]):
        """Initialize the Reamde application.

        Args:
            argv: Command-line arguments
        """
        super().__init__(argv, app_id="reamde")

        self.window: Optional[ReamdeWindow] = None

    def handle_message(self, message: dict) -> None:
        """Handle IPC message from another instance.

        Args:
            message: Dictionary containing message data

        Message format:
            {
                "action": "open" | "focus",
                "file": "/path/to/file.md"  # optional, for "open" action
            }
        """
        action = message.get("action")

        if action == "open":
            file_path = message.get("file")
            if file_path and self.window:
                # Open file in new tab
                self.window.open_file(file_path, focus=True)
                # Bring window to front
                self.window.bring_to_front()

        elif action == "focus":
            # Just bring window to front
            if self.window:
                self.window.bring_to_front()

    def run(self, file_path: Optional[str] = None) -> int:
        """Run the application.

        Args:
            file_path: Optional file path to open on startup

        Returns:
            Exit code (0 on success, 1 on failure)
        """
        # If not primary instance, send message and exit
        if not self.is_primary_instance:
            if file_path:
                # Send "open" message with file path
                message = {"action": "open", "file": str(Path(file_path).resolve())}
            else:
                # Just focus the existing window
                message = {"action": "focus"}

            return self.send_to_running_instance(message, timeout=5000)

        # Primary instance - create window and run
        self.window = ReamdeWindow()
        self.main_window = self.window  # For bring_to_front()

        # Open initial file if provided
        if file_path:
            self.window.open_file(file_path)

        # Show window
        self.window.show()

        # Run event loop
        return self.exec()
