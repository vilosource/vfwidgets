"""Tests for SingleInstanceApplication IPC mechanisms.

Note: Full integration tests that create multiple SingleInstanceApplication instances
need to run in separate processes, as QApplication can only be instantiated once per process.
These tests focus on the IPC layer (QLocalServer/QLocalSocket) which can be tested directly.
"""

import getpass
import json

from PySide6.QtCore import QTimer
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from pytestqt.qtbot import QtBot


def get_server_name(app_id: str) -> str:
    """Generate server name (matches SingleInstanceApplication logic)."""
    try:
        user = getpass.getuser()
    except Exception:
        user = "default"
    return f"vfwidgets-{app_id}-{user}"


class TestIPCMechanism:
    """Test QLocalServer/QLocalSocket IPC (underlying mechanism)."""

    def test_server_creation(self, qtbot: QtBot):
        """Test creating a local server."""
        app_id = "test-server-1"
        server_name = get_server_name(app_id)

        # Remove any stale server
        QLocalServer.removeServer(server_name)

        # Create server
        server = QLocalServer()
        assert server.listen(server_name)
        assert server.isListening()

        # Cleanup
        server.close()

    def test_server_name_uniqueness(self, qtbot: QtBot):
        """Test that server names prevent multiple instances."""
        app_id = "test-unique-123"
        server_name = get_server_name(app_id)

        QLocalServer.removeServer(server_name)

        # Create first server
        server1 = QLocalServer()
        assert server1.listen(server_name)

        # Try to create second server with same name (should fail)
        server2 = QLocalServer()
        assert not server2.listen(server_name)

        # Cleanup
        server1.close()

    def test_client_server_connection(self, qtbot: QtBot):
        """Test basic client-server connection."""
        app_id = "test-connect-1"
        server_name = get_server_name(app_id)

        QLocalServer.removeServer(server_name)

        # Create server
        server = QLocalServer()
        assert server.listen(server_name)

        # Create client and connect
        client = QLocalSocket()
        client.connectToServer(server_name)

        # Wait for connection
        assert client.waitForConnected(3000)
        assert client.state() == QLocalSocket.LocalSocketState.ConnectedState

        # Wait for server to receive connection
        if not server.hasPendingConnections():
            qtbot.wait(500)

        assert server.hasPendingConnections()

        # Cleanup
        client.disconnectFromServer()
        client.waitForDisconnected(1000)
        server.close()

    def test_message_passing(self, qtbot: QtBot):
        """Test sending and receiving JSON messages."""
        app_id = "test-message-1"
        server_name = get_server_name(app_id)

        QLocalServer.removeServer(server_name)

        # Create server
        server = QLocalServer()
        assert server.listen(server_name)

        # Track received messages
        received_messages = []

        def on_new_connection():
            socket = server.nextPendingConnection()
            if not socket:
                return

            def read_data():
                data = socket.readAll()
                if data.size() > 0:
                    message_str = bytes(data).decode("utf-8")
                    message = json.loads(message_str)
                    received_messages.append(message)

                    # Send acknowledgment
                    socket.write(b"OK")
                    socket.flush()

            if socket.bytesAvailable() > 0:
                read_data()
            else:
                socket.readyRead.connect(read_data)

        server.newConnection.connect(on_new_connection)

        # Create client
        client = QLocalSocket()
        client.connectToServer(server_name)
        assert client.waitForConnected(3000)

        # Send message
        test_message = {"action": "test", "data": "hello"}
        message_str = json.dumps(test_message)
        client.write(message_str.encode("utf-8"))
        client.flush()

        # Give server time to process
        qtbot.wait(500)

        # Wait for response
        if client.bytesAvailable() == 0:
            assert client.waitForReadyRead(3000)
        response = bytes(client.readAll()).decode("utf-8")
        assert response == "OK"

        # Check message received
        assert len(received_messages) == 1
        assert received_messages[0] == test_message

        # Cleanup
        client.disconnectFromServer()
        client.waitForDisconnected(1000)
        server.close()

    def test_multiple_messages(self, qtbot: QtBot):
        """Test sending multiple messages sequentially."""
        app_id = "test-multi-msg"
        server_name = get_server_name(app_id)

        QLocalServer.removeServer(server_name)

        server = QLocalServer()
        assert server.listen(server_name)

        received_messages = []

        def on_new_connection():
            socket = server.nextPendingConnection()
            if not socket:
                return

            def read_data():
                data = socket.readAll()
                if data.size() > 0:
                    message_str = bytes(data).decode("utf-8")
                    message = json.loads(message_str)
                    received_messages.append(message)
                    socket.write(b"OK")
                    socket.flush()
                    # Disconnect after processing
                    QTimer.singleShot(50, socket.disconnectFromServer)

            if socket.bytesAvailable() > 0:
                read_data()
            else:
                socket.readyRead.connect(read_data)

        server.newConnection.connect(on_new_connection)

        # Send multiple messages
        test_messages = [
            {"action": "open", "file": "file1.txt"},
            {"action": "open", "file": "file2.txt"},
            {"action": "focus"},
        ]

        for msg in test_messages:
            client = QLocalSocket()
            client.connectToServer(server_name)
            assert client.waitForConnected(3000)

            message_str = json.dumps(msg)
            client.write(message_str.encode("utf-8"))
            client.flush()

            # Give server time to process
            qtbot.wait(500)

            if client.bytesAvailable() == 0:
                assert client.waitForReadyRead(3000)
            response = bytes(client.readAll()).decode("utf-8")
            assert response == "OK"

            client.disconnectFromServer()
            client.waitForDisconnected(1000)

            qtbot.wait(100)

        # Check all messages received
        assert len(received_messages) == 3
        for i, msg in enumerate(test_messages):
            assert received_messages[i] == msg

        # Cleanup
        server.close()

    def test_invalid_json(self, qtbot: QtBot):
        """Test handling of invalid JSON."""
        app_id = "test-bad-json"
        server_name = get_server_name(app_id)

        QLocalServer.removeServer(server_name)

        server = QLocalServer()
        assert server.listen(server_name)

        errors = []

        def on_new_connection():
            socket = server.nextPendingConnection()
            if not socket:
                return

            def read_data():
                data = socket.readAll()
                if data.size() > 0:
                    try:
                        message_str = bytes(data).decode("utf-8")
                        json.loads(message_str)
                        socket.write(b"OK")
                    except json.JSONDecodeError:
                        errors.append("JSON decode error")
                        socket.write(b"ERROR")
                    socket.flush()

            if socket.bytesAvailable() > 0:
                read_data()
            else:
                socket.readyRead.connect(read_data)

        server.newConnection.connect(on_new_connection)

        # Send invalid JSON
        client = QLocalSocket()
        client.connectToServer(server_name)
        assert client.waitForConnected(3000)

        client.write(b"not valid json {{{")
        client.flush()

        # Give server time to process
        qtbot.wait(500)

        # Wait for response
        if client.bytesAvailable() == 0:
            assert client.waitForReadyRead(3000)
        response = bytes(client.readAll()).decode("utf-8")
        assert response == "ERROR"
        assert len(errors) == 1

        # Cleanup
        client.disconnectFromServer()
        client.waitForDisconnected(1000)
        server.close()

    def test_connection_timeout(self, qtbot: QtBot):
        """Test timeout when connecting to non-existent server."""
        server_name = get_server_name("nonexistent-app-999")

        # Don't create server - test connection failure
        client = QLocalSocket()
        client.connectToServer(server_name)

        # Should timeout
        assert not client.waitForConnected(1000)
        assert client.state() != QLocalSocket.LocalSocketState.ConnectedState

    def test_server_name_includes_username(self):
        """Test that server name includes username for isolation."""
        server_name = get_server_name("myapp")

        assert "vfwidgets" in server_name
        assert "myapp" in server_name

        # Should include some user identifier
        try:
            user = getpass.getuser()
            assert user in server_name
        except Exception:
            # If getpass fails, should use "default"
            assert "default" in server_name


def test_server_name_generation():
    """Test server name generation function."""
    name1 = get_server_name("app1")
    name2 = get_server_name("app2")

    # Different app_ids should produce different names
    assert name1 != name2
    assert "app1" in name1
    assert "app2" in name2

    # Both should have prefix
    assert name1.startswith("vfwidgets-")
    assert name2.startswith("vfwidgets-")
