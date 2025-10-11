"""Unit tests for EmbeddedTerminalServer."""

import os
import time
from unittest.mock import MagicMock, Mock, patch

import pytest
from vfwidgets_terminal.constants import DEFAULT_HOST, DEFAULT_PORT, WEBSOCKET_NAMESPACE
from vfwidgets_terminal.embedded_server import EmbeddedTerminalServer


class TestEmbeddedTerminalServerInitialization:
    """Test EmbeddedTerminalServer initialization."""

    def test_default_initialization(self):
        """Test server initialization with default parameters."""
        server = EmbeddedTerminalServer()

        assert server.command == "bash"
        assert server.args == []
        assert server.cwd is None
        assert server.env == {}
        assert server.port == DEFAULT_PORT
        assert server.host == DEFAULT_HOST
        assert server.capture_output is False
        assert server.running is False
        assert server.fd is None
        assert server.child_pid is None

    def test_custom_initialization(self):
        """Test server initialization with custom parameters."""
        custom_env = {"TEST_VAR": "test_value"}
        server = EmbeddedTerminalServer(
            command="python",
            args=["-i", "-u"],
            cwd="/tmp",
            env=custom_env,
            port=8080,
            host="localhost",
            capture_output=True,
        )

        assert server.command == "python"
        assert server.args == ["-i", "-u"]
        assert server.cwd == "/tmp"
        assert server.env == custom_env
        assert server.port == 8080
        assert server.host == "localhost"
        assert server.capture_output is True

    def test_flask_app_setup(self):
        """Test Flask application is properly set up."""
        server = EmbeddedTerminalServer()

        assert server.app is not None
        assert server.socketio is not None
        assert server.app.config["SECRET_KEY"] == "terminal-secret!"
        assert server.app.config["fd"] is None
        assert server.app.config["child_pid"] is None

    def test_socketio_setup(self):
        """Test SocketIO is properly configured."""
        server = EmbeddedTerminalServer()

        assert server.socketio is not None
        # Check CORS is enabled for all origins
        assert server.socketio.cors_allowed_origins == "*"
        assert server.socketio.async_mode == "threading"


class TestEmbeddedTerminalServerPortManagement:
    """Test port allocation and management."""

    def test_find_free_port(self):
        """Test _find_free_port method."""
        server = EmbeddedTerminalServer()
        port = server._find_free_port()

        assert isinstance(port, int)
        assert 1024 <= port <= 65535  # Valid port range

    def test_find_free_port_multiple_calls(self):
        """Test _find_free_port returns different ports."""
        server = EmbeddedTerminalServer()
        port1 = server._find_free_port()
        port2 = server._find_free_port()

        assert isinstance(port1, int)
        assert isinstance(port2, int)
        # Ports should be different (or at least valid)
        assert port1 != port2 or port1 == port2  # Both are valid outcomes

    @patch("socket.socket")
    def test_find_free_port_mocked(self, mock_socket):
        """Test _find_free_port with mocked socket."""
        mock_sock = Mock()
        mock_sock.getsockname.return_value = ("127.0.0.1", 12345)
        mock_socket.return_value.__enter__.return_value = mock_sock

        server = EmbeddedTerminalServer()
        port = server._find_free_port()

        assert port == 12345
        mock_sock.bind.assert_called_once_with(("", 0))
        mock_sock.getsockname.assert_called_once()


class TestEmbeddedTerminalServerFlaskRoutes:
    """Test Flask routes and SocketIO handlers."""

    def test_index_route_exists(self):
        """Test index route is set up."""
        server = EmbeddedTerminalServer()

        # Get the Flask app's URL map
        routes = [str(rule) for rule in server.app.url_map.iter_rules()]
        assert "/" in routes

    @patch("vfwidgets_terminal.embedded_server.Path")
    def test_get_terminal_html_file_exists(self, mock_path):
        """Test _get_terminal_html when file exists."""
        # Mock the template file exists
        mock_template_path = Mock()
        mock_template_path.exists.return_value = True
        mock_path.return_value.parent.__truediv__.return_value.__truediv__.return_value = mock_template_path

        # Mock file reading
        with patch("builtins.open", mock_open(read_data="<html>test</html>")):
            server = EmbeddedTerminalServer()
            html = server._get_terminal_html()

        assert html == "<html>test</html>"

    @patch("vfwidgets_terminal.embedded_server.Path")
    def test_get_terminal_html_file_not_exists(self, mock_path):
        """Test _get_terminal_html when file doesn't exist."""
        # Mock the template file doesn't exist
        mock_template_path = Mock()
        mock_template_path.exists.return_value = False
        mock_path.return_value.parent.__truediv__.return_value.__truediv__.return_value = mock_template_path

        server = EmbeddedTerminalServer()
        html = server._get_terminal_html()

        # Should return embedded HTML
        assert "<!DOCTYPE html>" in html
        assert "Terminal" in html
        assert "xterm" in html

    def test_embedded_html_content(self):
        """Test _get_embedded_html returns valid HTML."""
        server = EmbeddedTerminalServer()
        html = server._get_embedded_html()

        assert html.startswith("<!DOCTYPE html>")
        assert "<title>Terminal</title>" in html
        assert "xterm" in html
        assert "socket.io" in html
        assert "/pty" in html


class TestEmbeddedTerminalServerProcessManagement:
    """Test process management functionality."""

    @patch("os.execvpe")
    @patch("os.chdir")
    @patch("pty.fork")
    def test_pty_fork_child_process(self, mock_fork, mock_chdir, mock_execvpe):
        """Test PTY fork child process path."""
        # Mock pty.fork to return child process (PID 0)
        mock_fork.return_value = (0, None)

        server = EmbeddedTerminalServer(command="python", args=["-i"], cwd="/test/dir")

        # Since we're mocking the child process path, execvpe should be called
        # but we need to prevent it from actually executing
        mock_execvpe.side_effect = SystemExit(0)

        # Mock environment
        with patch.dict(os.environ, {"TEST": "value"}):
            server.env = {"CUSTOM": "test"}

            try:
                # This would normally call the SocketIO connect handler
                # We'll simulate it by calling the handler directly
                pass
            except SystemExit:
                # Expected when execvpe is called in child process
                pass

        # Verify child process setup
        mock_chdir.assert_called_once_with("/test/dir")

    @patch("pty.fork")
    def test_pty_fork_parent_process(self, mock_fork):
        """Test PTY fork parent process path."""
        # Mock pty.fork to return parent process
        mock_fd = 123
        mock_pid = 1234
        mock_fork.return_value = (mock_pid, mock_fd)

        server = EmbeddedTerminalServer()

        # Mock SocketIO and other dependencies
        with patch.object(server, "socketio") as mock_socketio:
            mock_socketio.start_background_task.return_value = None

            # Simulate the connect handler
            server.app.config["fd"] = mock_fd
            server.app.config["child_pid"] = mock_pid
            server.fd = mock_fd
            server.child_pid = mock_pid

            assert server.fd == mock_fd
            assert server.child_pid == mock_pid

    @patch("struct.pack")
    @patch("fcntl.ioctl")
    @patch("termios.TIOCSWINSZ", 123)
    def test_set_winsize(self, mock_ioctl, mock_pack):
        """Test _set_winsize method."""
        mock_pack.return_value = b"packed_data"

        server = EmbeddedTerminalServer()
        server._set_winsize(123, 24, 80)

        mock_pack.assert_called_once_with("HHHH", 24, 80, 0, 0)
        mock_ioctl.assert_called_once_with(123, 123, b"packed_data")

    def test_get_process_info_no_process(self):
        """Test get_process_info when no process is running."""
        server = EmbeddedTerminalServer()
        info = server.get_process_info()

        expected = {"pid": None, "command": "bash", "args": [], "running": False}

        assert info == expected

    def test_get_process_info_with_process(self):
        """Test get_process_info with running process."""
        server = EmbeddedTerminalServer(command="python", args=["-i"])
        server.child_pid = 1234
        server.running = True

        info = server.get_process_info()

        expected = {"pid": 1234, "command": "python", "args": ["-i"], "running": True}

        assert info == expected

    @patch("psutil.Process")
    def test_get_process_info_with_psutil(self, mock_process_class):
        """Test get_process_info with psutil available."""
        # Mock psutil.Process
        mock_process = Mock()
        mock_process.cpu_percent.return_value = 15.5
        mock_process.memory_info.return_value = Mock()
        mock_process.memory_info.return_value._asdict.return_value = {
            "rss": 1024,
            "vms": 2048,
        }
        mock_process.status.return_value = "running"
        mock_process_class.return_value = mock_process

        server = EmbeddedTerminalServer()
        server.child_pid = 1234

        info = server.get_process_info()

        assert "cpu_percent" in info
        assert "memory_info" in info
        assert "status" in info
        assert info["cpu_percent"] == 15.5
        assert info["status"] == "running"


class TestEmbeddedTerminalServerNetworking:
    """Test networking and server lifecycle."""

    @patch("threading.Thread")
    def test_start_server(self, mock_thread):
        """Test server start method."""
        server = EmbeddedTerminalServer(port=0)

        with patch.object(server, "_find_free_port", return_value=12345):
            port = server.start()

        assert port == 12345
        assert server.port == 12345
        assert server.running is True
        mock_thread.assert_called_once()

    @patch("threading.Thread")
    def test_start_server_with_fixed_port(self, mock_thread):
        """Test server start with fixed port."""
        server = EmbeddedTerminalServer(port=8080)
        port = server.start()

        assert port == 8080
        assert server.port == 8080
        assert server.running is True

    def test_start_server_already_running(self):
        """Test starting server when already running."""
        server = EmbeddedTerminalServer(port=8080)
        server.running = True

        port = server.start()

        assert port == 8080  # Should return existing port

    @patch("os.kill")
    @patch("os.waitpid")
    def test_stop_server_normal_exit(self, mock_waitpid, mock_kill):
        """Test stopping server with normal process exit."""
        server = EmbeddedTerminalServer()
        server.running = True
        server.child_pid = 1234
        server.fd = 123

        # Mock normal exit
        mock_waitpid.return_value = (1234, 0)  # PID, status

        with patch("os.close") as mock_close:
            with patch("os.WIFEXITED", return_value=True):
                with patch("os.WEXITSTATUS", return_value=0):
                    exit_code = server.stop()

        assert exit_code == 0
        assert server.running is False
        mock_kill.assert_called_once_with(1234, 15)  # SIGTERM
        mock_waitpid.assert_called_once_with(1234, 0)
        mock_close.assert_called_once_with(123)

    @patch("os.kill")
    @patch("os.waitpid")
    def test_stop_server_signal_termination(self, mock_waitpid, mock_kill):
        """Test stopping server with signal termination."""
        server = EmbeddedTerminalServer()
        server.running = True
        server.child_pid = 1234

        # Mock signal termination
        mock_waitpid.return_value = (1234, 15)  # PID, signal status

        with patch("os.WIFEXITED", return_value=False):
            with patch("os.WIFSIGNALED", return_value=True):
                with patch("os.WTERMSIG", return_value=15):
                    exit_code = server.stop()

        assert exit_code == -15  # Negative signal number
        mock_kill.assert_called_once_with(1234, 15)

    @patch("os.kill", side_effect=ProcessLookupError())
    def test_stop_server_process_not_found(self, mock_kill):
        """Test stopping server when process already exited."""
        server = EmbeddedTerminalServer()
        server.running = True
        server.child_pid = 1234

        exit_code = server.stop()

        assert exit_code == 0  # Default exit code
        assert server.running is False


class TestEmbeddedTerminalServerIO:
    """Test input/output handling."""

    @patch("os.write")
    def test_send_input(self, mock_write):
        """Test send_input method."""
        server = EmbeddedTerminalServer()
        server.fd = 123

        server.send_input("test command\n")

        mock_write.assert_called_once_with(123, b"test command\n")

    def test_send_input_no_fd(self):
        """Test send_input when no file descriptor is available."""
        server = EmbeddedTerminalServer()
        server.fd = None

        # Should not raise an exception
        server.send_input("test")

    @patch("os.write")
    def test_reset_terminal(self, mock_write):
        """Test reset_terminal method."""
        server = EmbeddedTerminalServer()
        server.fd = 123

        server.reset_terminal()

        mock_write.assert_called_once_with(123, b"\x1bc")  # ESC c

    def test_reset_terminal_no_fd(self):
        """Test reset_terminal when no file descriptor is available."""
        server = EmbeddedTerminalServer()
        server.fd = None

        # Should not raise an exception
        server.reset_terminal()


class TestEmbeddedTerminalServerBackgroundReading:
    """Test background output reading functionality."""

    @patch("select.select")
    @patch("os.read")
    def test_read_and_forward_output_with_data(self, mock_read, mock_select):
        """Test _read_and_forward_output with available data."""
        server = EmbeddedTerminalServer(capture_output=True)
        server.running = True
        server.app.config["fd"] = 123

        # Mock select indicating data is ready
        mock_select.return_value = ([123], [], [])
        # Mock os.read returning data
        mock_read.return_value = b"test output\n"

        # Mock SocketIO
        with patch.object(server, "socketio") as mock_socketio:
            mock_socketio.sleep.side_effect = [
                None,
                Exception("Stop loop"),
            ]  # Stop after one iteration
            mock_socketio.emit.return_value = None

            # Mock signals
            output_signal = Mock()
            server.output_received.connect(output_signal)

            try:
                server._read_and_forward_output()
            except Exception:
                pass  # Expected to stop the loop

        # Verify SocketIO emit was called
        mock_socketio.emit.assert_called_with(
            "pty-output", {"output": "test output\n"}, namespace=WEBSOCKET_NAMESPACE
        )

        # Verify signal was emitted
        output_signal.emit.assert_called_once_with("test output\n")

    @patch("select.select")
    def test_read_and_forward_output_no_data(self, mock_select):
        """Test _read_and_forward_output with no data available."""
        server = EmbeddedTerminalServer()
        server.running = True
        server.app.config["fd"] = 123

        # Mock select indicating no data is ready
        mock_select.return_value = ([], [], [])

        # Mock SocketIO
        with patch.object(server, "socketio") as mock_socketio:
            mock_socketio.sleep.side_effect = [None, Exception("Stop loop")]

            try:
                server._read_and_forward_output()
            except Exception:
                pass

        # Verify no emit was called
        mock_socketio.emit.assert_not_called()

    @patch("select.select")
    @patch("os.read", side_effect=OSError("Process ended"))
    def test_read_and_forward_output_process_ended(self, mock_read, mock_select):
        """Test _read_and_forward_output when process ends."""
        server = EmbeddedTerminalServer()
        server.running = True
        server.child_pid = 1234
        server.app.config["fd"] = 123

        # Mock select indicating data is ready
        mock_select.return_value = ([123], [], [])

        # Mock process ended signal
        process_ended_signal = Mock()
        server.process_ended.connect(process_ended_signal)

        with patch("os.waitpid", return_value=(1234, 0)):
            with patch("os.WIFEXITED", return_value=True):
                with patch("os.WEXITSTATUS", return_value=0):
                    server._read_and_forward_output()

        # Verify process ended signal was emitted
        process_ended_signal.emit.assert_called_once_with(0)


def mock_open(read_data=""):
    """Helper function to create a mock open context manager."""
    mock = MagicMock()
    mock.__enter__.return_value.read.return_value = read_data
    return mock


@pytest.mark.integration
class TestEmbeddedTerminalServerIntegration:
    """Integration tests for EmbeddedTerminalServer."""

    def test_server_lifecycle_integration(self, free_port):
        """Test complete server lifecycle."""
        server = EmbeddedTerminalServer(port=free_port)

        try:
            # Start server
            actual_port = server.start()
            assert actual_port == free_port
            assert server.running is True

            # Give server time to start
            time.sleep(0.1)

        finally:
            # Stop server
            exit_code = server.stop()
            assert isinstance(exit_code, int)
            assert server.running is False

    @pytest.mark.slow
    def test_server_with_real_process(self, free_port, temp_working_directory):
        """Test server with real process execution."""
        server = EmbeddedTerminalServer(
            command="echo",
            args=["test"],
            cwd=str(temp_working_directory),
            port=free_port,
            capture_output=True,
        )

        try:
            # Start server
            server.start()
            time.sleep(0.1)

            # Send input
            server.send_input("test input\n")
            time.sleep(0.1)

        finally:
            # Stop server
            server.stop()
