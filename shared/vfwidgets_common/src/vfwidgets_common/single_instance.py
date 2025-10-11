"""Single-instance application support using Qt IPC.

This module provides SingleInstanceApplication, a QApplication subclass that ensures
only one instance of an application runs at a time. When a second instance is launched,
it communicates with the first instance via QLocalServer/QLocalSocket and exits.

Example:
    >>> from vfwidgets_common import SingleInstanceApplication
    >>>
    >>> class MyApp(SingleInstanceApplication):
    ...     def handle_message(self, message: dict):
    ...         print(f"Received: {message}")
    ...         self.bring_to_front()
    >>>
    >>> app = MyApp(sys.argv, app_id="myapp")
    >>> if not app.is_primary_instance():
    ...     app.send_to_running_instance({"action": "focus"})
    ...     sys.exit(0)
    >>> sys.exit(app.exec())
"""

import getpass
import json
import sys
from abc import abstractmethod
from typing import Optional

from PySide6.QtCore import QTimer
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWidgets import QApplication, QWidget


class SingleInstanceApplication(QApplication):
    """QApplication subclass with single-instance behavior via IPC.

    This class ensures only one instance of an application runs at a time.
    When a second instance attempts to launch:
    1. It detects the primary instance via QLocalServer
    2. Sends a message to the primary instance via QLocalSocket
    3. Exits immediately

    The primary instance receives messages through the handle_message() method.

    Attributes:
        _app_id: Unique application identifier
        _is_primary: Whether this is the primary (first) instance
        _local_server: QLocalServer for receiving connections (primary only)
        _main_window: Reference to main window for bring_to_front()

    Example:
        >>> class MyApp(SingleInstanceApplication):
        ...     def __init__(self, argv):
        ...         super().__init__(argv, app_id="myapp")
        ...         self.main_window = None
        ...
        ...     def handle_message(self, message: dict):
        ...         if message.get("action") == "open":
        ...             self.main_window.open_file(message.get("file"))
        ...         self.bring_to_front()
        ...
        ...     def run(self, initial_file=None):
        ...         if not self.is_primary_instance():
        ...             msg = {"action": "open", "file": initial_file}
        ...             return self.send_to_running_instance(msg)
        ...
        ...         self.main_window = MainWindow()
        ...         self.main_window.show()
        ...         return self.exec()
    """

    def __init__(self, argv: list[str], app_id: str):
        """Initialize single-instance application.

        Args:
            argv: Command-line arguments (passed to QApplication)
            app_id: Unique application identifier for IPC server name
        """
        super().__init__(argv)

        self._app_id = app_id
        self._is_primary = False
        self._local_server: Optional[QLocalServer] = None
        self._main_window: Optional[QWidget] = None

        # Try to create local server (only succeeds for primary instance)
        self._is_primary = self._create_local_server()

    @property
    def is_primary_instance(self) -> bool:
        """Check if this is the primary (first) instance.

        Returns:
            True if this is the primary instance, False otherwise
        """
        return self._is_primary

    @property
    def main_window(self) -> Optional[QWidget]:
        """Get the main window reference.

        Returns:
            Main window widget or None
        """
        return self._main_window

    @main_window.setter
    def main_window(self, window: QWidget) -> None:
        """Set the main window reference.

        Args:
            window: Main window widget
        """
        self._main_window = window

    def _get_server_name(self) -> str:
        """Generate unique server name for IPC.

        Includes username to isolate instances between users.

        Returns:
            Server name string (e.g., "vfwidgets-myapp-username")
        """
        try:
            user = getpass.getuser()
        except Exception:
            user = "default"

        return f"vfwidgets-{self._app_id}-{user}"

    def _create_local_server(self) -> bool:
        """Create local server for IPC.

        Attempts to create a QLocalServer. If successful, this is the primary instance.
        If the server name is already in use, this is a secondary instance.

        Returns:
            True if server created (primary instance), False otherwise
        """
        server_name = self._get_server_name()

        # Try to create server first (don't remove yet!)
        self._local_server = QLocalServer(self)
        if self._local_server.listen(server_name):
            # Success - we're the primary instance
            self._local_server.newConnection.connect(self._on_new_connection)
            return True

        # Server name already in use - check if it's alive or stale
        # Try to connect to it
        test_socket = QLocalSocket()
        test_socket.connectToServer(server_name)

        if test_socket.waitForConnected(1000):
            # Server is alive - we're a secondary instance
            test_socket.disconnectFromServer()
            return False

        # Server is stale (from crashed instance) - remove and try again
        print(f"[SingleInstanceApplication] Removing stale server: {server_name}")
        QLocalServer.removeServer(server_name)

        if self._local_server.listen(server_name):
            # Successfully created after removing stale server
            self._local_server.newConnection.connect(self._on_new_connection)
            return True

        # Still can't create server - something is wrong
        print(f"[SingleInstanceApplication] Failed to create server: {server_name}")
        return False

    def _on_new_connection(self) -> None:
        """Handle new connection from secondary instance.

        Reads the message from the socket and calls handle_message().
        """
        if not self._local_server:
            return

        # Get the new connection
        socket = self._local_server.nextPendingConnection()
        if not socket:
            return

        # Read data when available
        def read_data():
            if socket.state() != QLocalSocket.LocalSocketState.ConnectedState:
                return

            # Read all available data
            data = socket.readAll()
            if data.size() == 0:
                return

            try:
                # Parse JSON message
                message_str = bytes(data).decode("utf-8")
                message = json.loads(message_str)

                # Call handler
                self.handle_message(message)

                # Send acknowledgment
                socket.write(b"OK")
                socket.flush()

            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(
                    f"[SingleInstanceApplication] Error parsing message: {e}",
                    file=sys.stderr,
                )
                socket.write(b"ERROR")
                socket.flush()

            finally:
                # Close connection after processing
                QTimer.singleShot(100, socket.disconnectFromServer)

        # Wait for data to be ready
        if socket.bytesAvailable() > 0:
            read_data()
        else:
            socket.readyRead.connect(read_data)

    @abstractmethod
    def handle_message(self, message: dict) -> None:
        """Handle IPC message from another instance.

        This method must be implemented by subclasses to process messages
        received from secondary instances.

        Args:
            message: Dictionary containing message data

        Example:
            >>> def handle_message(self, message: dict):
            ...     action = message.get("action")
            ...     if action == "open":
            ...         self.main_window.open_file(message.get("file"))
            ...     self.bring_to_front()
        """
        pass

    def send_to_running_instance(self, message: dict, timeout: int = 5000) -> int:
        """Send message to the running primary instance.

        Connects to the primary instance via QLocalSocket and sends a JSON message.

        Args:
            message: Dictionary to send (will be JSON-encoded)
            timeout: Connection timeout in milliseconds (default: 5000)

        Returns:
            Exit code: 0 on success, 1 on failure

        Example:
            >>> if not app.is_primary_instance():
            ...     message = {"action": "focus"}
            ...     sys.exit(app.send_to_running_instance(message))
        """
        socket = QLocalSocket()
        server_name = self._get_server_name()

        # Connect to primary instance
        socket.connectToServer(server_name)
        if not socket.waitForConnected(timeout):
            print(
                f"[SingleInstanceApplication] Error: Could not connect to "
                f"running {self._app_id} instance",
                file=sys.stderr,
            )
            print(f"[SingleInstanceApplication] Error: {socket.errorString()}", file=sys.stderr)
            return 1

        try:
            # Send JSON message
            message_str = json.dumps(message)
            message_bytes = message_str.encode("utf-8")
            socket.write(message_bytes)
            socket.flush()

            # Wait for acknowledgment
            if not socket.waitForReadyRead(3000):
                print(
                    "[SingleInstanceApplication] Warning: No response from " "primary instance",
                    file=sys.stderr,
                )
                return 1

            response = bytes(socket.readAll()).decode("utf-8")
            if response != "OK":
                print(
                    f"[SingleInstanceApplication] Warning: Primary instance "
                    f"returned: {response}",
                    file=sys.stderr,
                )
                return 1

            return 0

        except Exception as e:
            print(
                f"[SingleInstanceApplication] Error sending message: {e}",
                file=sys.stderr,
            )
            return 1

        finally:
            socket.disconnectFromServer()
            if socket.state() != QLocalSocket.LocalSocketState.UnconnectedState:
                socket.waitForDisconnected(1000)

    def bring_to_front(self) -> None:
        """Activate and raise the main window to the front.

        This method attempts to bring the application window to the foreground
        and give it focus. Behavior varies by platform:
        - Linux (X11): Uses activateWindow() + raise_() + setFocus()
        - Linux (Wayland): May have limited support due to compositor restrictions
        - macOS: Native activation works reliably
        - Windows: Uses SetForegroundWindow equivalent

        Note: This method requires main_window to be set.

        Example:
            >>> app.main_window = my_window
            >>> app.bring_to_front()
        """
        if not self._main_window:
            return

        # Show window if minimized
        if self._main_window.isMinimized():
            self._main_window.showNormal()

        # Activate and raise window
        self._main_window.activateWindow()
        self._main_window.raise_()
        self._main_window.setFocus()

        # Additional platform-specific activation
        if sys.platform == "darwin":  # macOS
            # On macOS, we need to activate the application itself
            pass  # QApplication.instance().activate() doesn't exist in PySide6
        elif sys.platform == "win32":  # Windows
            # On Windows, activateWindow() should be sufficient
            pass

    def cleanup(self) -> None:
        """Clean up resources before application exit.

        Closes the local server if this is the primary instance.
        Called automatically by Qt on application exit, but can be called
        manually if needed.
        """
        if self._local_server:
            self._local_server.close()
            self._local_server = None
