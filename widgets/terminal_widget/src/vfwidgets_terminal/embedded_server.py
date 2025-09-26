"""Embedded terminal server using Flask and SocketIO."""

import fcntl
import logging
import os
import pty
import select
import socket
import struct
import termios
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

from flask import Flask
from flask_socketio import SocketIO
from PySide6.QtCore import QObject, Signal

from .constants import DEFAULT_HOST, DEFAULT_PORT, MAX_READ_BYTES, WEBSOCKET_NAMESPACE

logger = logging.getLogger(__name__)
logging.getLogger("werkzeug").setLevel(logging.ERROR)


class EmbeddedTerminalServer(QObject):
    """Embedded Flask/SocketIO server for terminal emulation."""

    # Qt signals for communication with widget
    output_received = Signal(str)
    process_started = Signal()
    process_ended = Signal(int)  # exit code

    def __init__(
        self,
        command: str = "bash",
        args: Optional[List[str]] = None,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        port: int = DEFAULT_PORT,
        host: str = DEFAULT_HOST,
        capture_output: bool = False,
    ):
        """Initialize the embedded terminal server.

        Args:
            command: Command to execute
            args: Command arguments
            cwd: Working directory
            env: Environment variables
            port: Server port (0 for random)
            host: Server host
            capture_output: Whether to capture output
        """
        super().__init__()

        self.command = command
        self.args = args or []
        self.cwd = cwd
        self.env = env or {}
        self.port = port
        self.host = host
        self.capture_output = capture_output

        # Flask app and SocketIO
        self.app = None
        self.socketio = None

        # Terminal process
        self.fd = None
        self.child_pid = None
        self.running = False

        # Server thread
        self.server_thread = None

        # Output buffer
        self.output_buffer = []

        # Initialize Flask app
        self._setup_flask_app()

    def _setup_flask_app(self):
        """Set up Flask application and SocketIO handlers."""
        self.app = Flask(__name__)
        self.app.config["SECRET_KEY"] = "terminal-secret!"
        self.app.config["fd"] = None
        self.app.config["child_pid"] = None

        self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode="threading")

        # Setup routes
        @self.app.route("/")
        def index():
            """Serve the terminal HTML page."""
            return self._get_terminal_html()

        # Setup SocketIO handlers
        @self.socketio.on("pty-input", namespace=WEBSOCKET_NAMESPACE)
        def pty_input(data):
            """Handle input from browser terminal."""
            if self.app.config["fd"]:
                # Only log non-trivial inputs (not individual keystrokes)
                # logger.debug(f"Received input: {data['input']}")
                os.write(self.app.config["fd"], data["input"].encode())

        @self.socketio.on("resize", namespace=WEBSOCKET_NAMESPACE)
        def resize(data):
            """Handle terminal resize."""
            if self.app.config["fd"]:
                rows = data.get("rows", 24)
                cols = data.get("cols", 80)
                logger.debug(f"Terminal resized to {rows}x{cols}")
                self._set_winsize(self.app.config["fd"], rows, cols)

        @self.socketio.on("connect", namespace=WEBSOCKET_NAMESPACE)
        def connect():
            """Handle new client connection."""
            logger.info("Client connected")
            if self.app.config["child_pid"]:
                return

            # Fork PTY
            (child_pid, fd) = pty.fork()
            if child_pid == 0:
                # Child process - execute command
                if self.cwd:
                    os.chdir(self.cwd)

                # Merge environment variables
                env = os.environ.copy()
                env.update(self.env)

                # Build command
                cmd = [self.command] + self.args

                # Execute
                os.execvpe(cmd[0], cmd, env)
            else:
                # Parent process
                self.app.config["fd"] = fd
                self.app.config["child_pid"] = child_pid
                self.fd = fd
                self.child_pid = child_pid

                # Set initial size
                self._set_winsize(fd, 24, 80)

                # Start output reader
                self.socketio.start_background_task(target=self._read_and_forward_output)

                logger.info(f"Started process {child_pid}: {self.command}")
                self.process_started.emit()

        @self.socketio.on("disconnect", namespace=WEBSOCKET_NAMESPACE)
        def disconnect():
            """Handle client disconnection."""
            logger.info("Client disconnected")

    def _set_winsize(self, fd: int, rows: int, cols: int):
        """Set terminal window size.

        Args:
            fd: File descriptor
            rows: Number of rows
            cols: Number of columns
        """
        winsize = struct.pack("HHHH", rows, cols, 0, 0)
        fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)

    def _read_and_forward_output(self):
        """Read output from PTY and forward to client."""
        while self.running:
            self.socketio.sleep(0.01)

            if self.app.config["fd"]:
                timeout_sec = 0
                (data_ready, _, _) = select.select([self.app.config["fd"]], [], [], timeout_sec)

                if data_ready:
                    try:
                        output = os.read(self.app.config["fd"], MAX_READ_BYTES).decode(
                            errors="ignore"
                        )

                        # Emit to browser
                        self.socketio.emit(
                            "pty-output", {"output": output}, namespace=WEBSOCKET_NAMESPACE
                        )

                        # Capture if requested
                        if self.capture_output:
                            self.output_buffer.append(output)
                            self.output_received.emit(output)

                    except OSError as e:
                        # Process ended
                        logger.info(f"Process ended: {e}")
                        break

        # Check exit status if process has ended
        exit_code = 0
        if self.child_pid:
            try:
                pid, status = os.waitpid(self.child_pid, os.WNOHANG)
                if pid == self.child_pid:
                    if os.WIFEXITED(status):
                        exit_code = os.WEXITSTATUS(status)
                        logger.info(f"Process {self.child_pid} exited with code {exit_code}")
                    elif os.WIFSIGNALED(status):
                        sig = os.WTERMSIG(status)
                        logger.info(f"Process {self.child_pid} terminated by signal {sig}")
                        exit_code = -sig
            except:
                pass

        # Emit process ended signal
        logger.debug(f"Emitting process_ended signal with exit code {exit_code}")
        self.process_ended.emit(exit_code)

    def _get_terminal_html(self):
        """Get the terminal HTML template."""
        # Load template from resources
        template_path = Path(__file__).parent / "resources" / "terminal.html"

        if template_path.exists():
            with open(template_path) as f:
                return f.read()
        else:
            # Fallback to embedded template
            return self._get_embedded_html()

    def _get_embedded_html(self):
        """Get embedded HTML template as fallback."""
        return """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Terminal</title>
    <link rel="stylesheet" href="https://unpkg.com/xterm@4.19.0/css/xterm.css">
    <style>
        body { margin: 0; padding: 0; background: #1e1e1e; }
        #terminal { width: 100%; height: 100vh; }
    </style>
</head>
<body>
    <div id="terminal"></div>
    <script src="https://unpkg.com/xterm@4.19.0/lib/xterm.js"></script>
    <script src="https://unpkg.com/xterm-addon-fit@0.5.0/lib/xterm-addon-fit.js"></script>
    <script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
    <script>
        const term = new Terminal({
            cursorBlink: true,
            scrollback: 1000,
            theme: {
                background: '#1e1e1e',
                foreground: '#d4d4d4'
            }
        });

        const fitAddon = new FitAddon.FitAddon();
        term.loadAddon(fitAddon);
        term.open(document.getElementById('terminal'));
        fitAddon.fit();

        const socket = io('/pty');

        term.onData(data => {
            socket.emit('pty-input', {input: data});
        });

        socket.on('pty-output', data => {
            term.write(data.output);
        });

        socket.on('connect', () => {
            fitAddon.fit();
            const dims = fitAddon.proposeDimensions();
            if (dims) {
                socket.emit('resize', {
                    rows: dims.rows,
                    cols: dims.cols
                });
            }
        });

        window.onresize = () => {
            fitAddon.fit();
            const dims = fitAddon.proposeDimensions();
            if (dims) {
                socket.emit('resize', {
                    rows: dims.rows,
                    cols: dims.cols
                });
            }
        };

        // Copy/paste support
        term.attachCustomKeyEventHandler(e => {
            if (e.type !== 'keydown') return true;
            if (e.ctrlKey && e.shiftKey) {
                const key = e.key.toLowerCase();
                if (key === 'c' || key === 'x') {
                    const selection = term.getSelection();
                    navigator.clipboard.writeText(selection);
                    return false;
                } else if (key === 'v') {
                    navigator.clipboard.readText().then(text => {
                        term.paste(text);
                    });
                    return false;
                }
            }
            return true;
        });
    </script>
</body>
</html>"""

    def _find_free_port(self) -> int:
        """Find a free port to use.

        Returns:
            Available port number
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            return s.getsockname()[1]

    def start(self) -> int:
        """Start the terminal server.

        Returns:
            Port number the server is running on
        """
        if self.running:
            return self.port

        logger.info(f"Starting embedded terminal server on {self.host}:{self.port}")
        self.running = True

        # Find port if needed
        if self.port == 0:
            self.port = self._find_free_port()

        # Start server in thread
        def run_server():
            self.socketio.run(
                self.app,
                debug=False,
                port=self.port,
                host=self.host,
                allow_unsafe_werkzeug=True,
                use_reloader=False,
            )

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        logger.debug("Server thread started")

        logger.info(f"Server started on {self.host}:{self.port}")
        return self.port

    def stop(self) -> Optional[int]:
        """Stop the terminal server.

        Returns:
            Exit code of the process
        """
        logger.info("Stopping embedded terminal server")
        self.running = False
        exit_code = 0

        # Terminate child process
        if self.child_pid:
            try:
                os.kill(self.child_pid, 15)  # SIGTERM
                logger.debug(f"Sent SIGTERM to process {self.child_pid}")

                # Wait for process to exit and get exit code
                pid, status = os.waitpid(self.child_pid, 0)
                if os.WIFEXITED(status):
                    exit_code = os.WEXITSTATUS(status)
                    logger.info(f"Process {pid} exited with code {exit_code}")
                elif os.WIFSIGNALED(status):
                    sig = os.WTERMSIG(status)
                    logger.info(f"Process {pid} terminated by signal {sig}")
                    exit_code = -sig
            except ProcessLookupError:
                logger.debug(f"Process {self.child_pid} already exited")
            except Exception as e:
                logger.debug(f"Error stopping process: {e}")

        # Close file descriptor
        if self.fd:
            try:
                os.close(self.fd)
            except OSError:
                pass

        logger.info("Server stopped")
        return exit_code

    def send_input(self, text: str):
        """Send input to the terminal.

        Args:
            text: Text to send
        """
        if self.fd:
            os.write(self.fd, text.encode())

    def reset_terminal(self):
        """Reset the terminal."""
        # Send reset sequence
        if self.fd:
            os.write(self.fd, b"\x1bc")  # ESC c

    def get_process_info(self) -> Dict[str, Any]:
        """Get information about the running process.

        Returns:
            Process information dictionary
        """
        info = {
            "pid": self.child_pid,
            "command": self.command,
            "args": self.args,
            "running": self.running,
        }

        # Add process stats if psutil is available
        try:
            import psutil

            if self.child_pid:
                proc = psutil.Process(self.child_pid)
                info.update(
                    {
                        "cpu_percent": proc.cpu_percent(),
                        "memory_info": proc.memory_info()._asdict(),
                        "status": proc.status(),
                    }
                )
        except (ImportError, psutil.NoSuchProcess):
            pass

        return info
