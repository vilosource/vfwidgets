"""Unit tests for TerminalWidget."""

from unittest.mock import Mock, patch

from PySide6.QtWidgets import QWidget


class TestTerminalWidget:
    """Test suite for TerminalWidget."""

    @patch("vfwidgets_terminal.terminal.EmbeddedTerminalServer")
    def test_initialization(self, mock_server, qtbot):
        """Test TerminalWidget initialization."""
        from vfwidgets_terminal import TerminalWidget

        # Mock the server
        mock_server_instance = Mock()
        mock_server_instance.start.return_value = 12345
        mock_server.return_value = mock_server_instance

        # Create widget
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Check widget properties
        assert isinstance(widget, QWidget)
        assert widget.command == "bash"
        assert widget.args == []
        assert widget.host == "127.0.0.1"

        # Check that server was created
        mock_server.assert_called_once()

    @patch("vfwidgets_terminal.terminal.EmbeddedTerminalServer")
    def test_custom_command(self, mock_server, qtbot):
        """Test TerminalWidget with custom command."""
        from vfwidgets_terminal import TerminalWidget

        # Mock the server
        mock_server_instance = Mock()
        mock_server_instance.start.return_value = 12345
        mock_server.return_value = mock_server_instance

        # Create widget with Python command
        widget = TerminalWidget(command="python", args=["-i"], cwd="/tmp")
        qtbot.addWidget(widget)

        assert widget.command == "python"
        assert widget.args == ["-i"]
        assert widget.cwd == "/tmp"

    @patch("vfwidgets_terminal.terminal.EmbeddedTerminalServer")
    def test_external_server(self, mock_server, qtbot):
        """Test TerminalWidget with external server."""
        from vfwidgets_terminal import TerminalWidget

        # Create widget with external server URL
        widget = TerminalWidget(server_url="http://localhost:5000")
        qtbot.addWidget(widget)

        # Server should not be created for external mode
        mock_server.assert_not_called()
        assert widget.server_url == "http://localhost:5000"

    @patch("vfwidgets_terminal.terminal.EmbeddedTerminalServer")
    def test_signals(self, mock_server, qtbot):
        """Test TerminalWidget signals."""
        from vfwidgets_terminal import TerminalWidget

        # Mock the server
        mock_server_instance = Mock()
        mock_server_instance.start.return_value = 12345
        mock_server.return_value = mock_server_instance

        # Create widget
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Test signal connections
        ready_signal = Mock()
        widget.terminal_ready.connect(ready_signal)

        closed_signal = Mock()
        widget.terminal_closed.connect(closed_signal)

        # Verify signals exist and can be connected
        assert hasattr(widget, "terminal_ready")
        assert hasattr(widget, "terminal_closed")
        assert hasattr(widget, "command_started")
        assert hasattr(widget, "output_received")

    @patch("vfwidgets_terminal.terminal.EmbeddedTerminalServer")
    def test_send_command(self, mock_server, qtbot):
        """Test sending commands to terminal."""
        from vfwidgets_terminal import TerminalWidget

        # Mock the server
        mock_server_instance = Mock()
        mock_server_instance.start.return_value = 12345
        mock_server_instance.send_input = Mock()
        mock_server.return_value = mock_server_instance

        # Create widget
        widget = TerminalWidget()
        qtbot.addWidget(widget)
        widget.server = mock_server_instance

        # Send command
        widget.send_command("ls -la")

        # Verify command was sent to server
        mock_server_instance.send_input.assert_called_with("ls -la\n")

    @patch("vfwidgets_terminal.terminal.EmbeddedTerminalServer")
    def test_output_capture(self, mock_server, qtbot):
        """Test output capture functionality."""
        from vfwidgets_terminal import TerminalWidget

        # Mock the server
        mock_server_instance = Mock()
        mock_server_instance.start.return_value = 12345
        mock_server.return_value = mock_server_instance

        # Create widget with capture enabled
        widget = TerminalWidget(capture_output=True)
        qtbot.addWidget(widget)

        # Verify output buffer is created
        assert widget.output_buffer is not None
        assert widget.capture_output is True

        # Simulate output
        widget._handle_output("Test output\n")
        widget._handle_output("More output\n")

        # Check captured output
        output = widget.get_output()
        assert "Test output" in output
        assert "More output" in output

    @patch("vfwidgets_terminal.terminal.EmbeddedTerminalServer")
    def test_output_filter(self, mock_server, qtbot):
        """Test output filtering."""
        from vfwidgets_terminal import TerminalWidget

        # Define filter function
        def uppercase_filter(text):
            return text.upper()

        # Mock the server
        mock_server_instance = Mock()
        mock_server_instance.start.return_value = 12345
        mock_server.return_value = mock_server_instance

        # Create widget with filter
        widget = TerminalWidget(capture_output=True, output_filter=uppercase_filter)
        qtbot.addWidget(widget)

        # Simulate output
        widget._handle_output("test output")

        # Check filtered output
        output = widget.get_output()
        assert output == "TEST OUTPUT"

    @patch("vfwidgets_terminal.terminal.EmbeddedTerminalServer")
    def test_themes(self, mock_server, qtbot):
        """Test theme configuration."""
        from vfwidgets_terminal import TerminalWidget

        # Mock the server
        mock_server_instance = Mock()
        mock_server_instance.start.return_value = 12345
        mock_server.return_value = mock_server_instance

        # Test dark theme (default)
        widget_dark = TerminalWidget(theme="dark")
        qtbot.addWidget(widget_dark)
        assert widget_dark.theme == "dark"

        # Test light theme
        widget_light = TerminalWidget(theme="light")
        qtbot.addWidget(widget_light)
        assert widget_light.theme == "light"

    @patch("vfwidgets_terminal.terminal.EmbeddedTerminalServer")
    def test_read_only_mode(self, mock_server, qtbot):
        """Test read-only mode."""
        from vfwidgets_terminal import TerminalWidget

        # Mock the server
        mock_server_instance = Mock()
        mock_server_instance.start.return_value = 12345
        mock_server.return_value = mock_server_instance

        # Create widget in read-only mode
        widget = TerminalWidget(read_only=True)
        qtbot.addWidget(widget)

        assert widget.read_only is True

        # Test toggling read-only
        widget.set_read_only(False)
        assert widget.read_only is False

    @patch("vfwidgets_terminal.terminal.EmbeddedTerminalServer")
    def test_close_terminal(self, mock_server, qtbot):
        """Test closing the terminal."""
        from vfwidgets_terminal import TerminalWidget

        # Mock the server
        mock_server_instance = Mock()
        mock_server_instance.start.return_value = 12345
        mock_server_instance.stop.return_value = 0
        mock_server.return_value = mock_server_instance

        # Create widget
        widget = TerminalWidget()
        qtbot.addWidget(widget)
        widget.server = mock_server_instance

        # Connect to signal
        qtbot.waitSignal(widget.terminal_closed, timeout=100)

        # Close terminal
        widget.close_terminal()

        # Verify server was stopped
        mock_server_instance.stop.assert_called_once()
        assert widget.server is None
