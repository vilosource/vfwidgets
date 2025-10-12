"""Multi-session terminal server implementation."""

import atexit
import logging
import shlex
import signal
import socket
import threading
import time
import uuid
from pathlib import Path
from typing import Optional

from flask import Flask, request, send_from_directory
from flask_socketio import SocketIO, join_room, leave_room
from PySide6.QtCore import QObject, Signal

from .backends import create_backend
from .session import TerminalSession

logging.getLogger("werkzeug").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)


class MultiSessionTerminalServer(QObject):
    """
    Multi-session terminal server.

    Single Flask/SocketIO server handling multiple terminal sessions with
    session-based routing, automatic cleanup, and heartbeat mechanism.

    Features:
    - Multiple concurrent sessions (default max: 20)
    - Session-based message routing using SocketIO rooms
    - Automatic session cleanup (timeout + dead process detection)
    - Heartbeat mechanism to keep active sessions alive
    - Cross-platform via backend abstraction

    Usage:
        server = MultiSessionTerminalServer(port=5000)
        server.start()

        # Create session
        session_id = server.create_session(command="bash")
        url = server.get_session_url(session_id)

        # Use url in TerminalWidget
        terminal = TerminalWidget(server_url=url)
    """

    # Signal emitted when a terminal session process exits
    session_ended = Signal(str)  # session_id

    def __init__(self, port: int = 0, host: str = "127.0.0.1", max_sessions: int = 20):
        """
        Initialize multi-session terminal server.

        Args:
            port: Port to listen on (0 for auto-allocation)
            host: Host to bind to (default: localhost)
            max_sessions: Maximum concurrent sessions (default: 20)
        """
        super().__init__()

        self.port = port
        self.host = host
        self.max_sessions = max_sessions

        self.app: Optional[Flask] = None
        self.socketio: Optional[SocketIO] = None
        self.server_thread: Optional[threading.Thread] = None
        self.sessions: dict[str, TerminalSession] = {}
        self.backend = None
        self.running = False

        self._setup_flask_app()

        # Register cleanup handlers
        atexit.register(self.shutdown)
        signal.signal(signal.SIGTERM, lambda sig, frame: self.shutdown())
        signal.signal(signal.SIGINT, lambda sig, frame: self.shutdown())

    def _setup_flask_app(self):
        """Setup Flask application with SocketIO."""
        self.app = Flask(__name__)
        self.app.config["SECRET_KEY"] = "terminal_server_secret!"
        self.socketio = SocketIO(
            self.app, cors_allowed_origins="*", async_mode="threading"
        )

        # Serve terminal HTML for session
        @self.app.route("/terminal/<session_id>")
        def terminal_page(session_id):
            """Serve terminal page for a specific session."""
            logger.info(f"HTTP request for terminal page, session: {session_id}")
            logger.debug(f"Active sessions: {list(self.sessions.keys())}")

            if session_id not in self.sessions:
                logger.error(
                    f"Session {session_id} not found. Available: {list(self.sessions.keys())}"
                )
                return f"Session not found: {session_id}", 404

            # Serve from resources directory
            resources_dir = Path(__file__).parent / "resources"
            logger.debug(f"Serving terminal.html from {resources_dir}")

            if not resources_dir.exists():
                logger.error(f"Resources directory not found: {resources_dir}")
                return "Resources directory not found", 500

            html_path = resources_dir / "terminal.html"
            if not html_path.exists():
                logger.error(f"terminal.html not found at {html_path}")
                return "terminal.html not found", 500

            return send_from_directory(resources_dir, "terminal.html")

        # Serve static JavaScript files
        @self.app.route("/static/js/<path:filename>")
        def serve_js(filename):
            """Serve JavaScript files from resources/js."""
            resources_dir = Path(__file__).parent / "resources"
            js_dir = resources_dir / "js"
            logger.debug(f"Serving JS file: {filename} from {js_dir}")
            return send_from_directory(js_dir, filename)

        # Serve static CSS files
        @self.app.route("/static/css/<path:filename>")
        def serve_css(filename):
            """Serve CSS files from resources/css."""
            resources_dir = Path(__file__).parent / "resources"
            css_dir = resources_dir / "css"
            logger.debug(f"Serving CSS file: {filename} from {css_dir}")
            return send_from_directory(css_dir, filename)

        # SocketIO event handlers
        @self.socketio.on("connect", namespace="/pty")
        def handle_connect():
            """Handle client connection."""
            session_id = request.args.get("session_id")
            if not session_id or session_id not in self.sessions:
                logger.warning(f"Connection rejected for unknown session: {session_id}")
                return False

            join_room(session_id)
            logger.info(f"Client connected to session {session_id}")

            # Start terminal process if not already started
            session = self.sessions[session_id]
            if not session.child_pid:
                self._start_terminal_process(session_id)

        @self.socketio.on("disconnect", namespace="/pty")
        def handle_disconnect():
            """Handle client disconnection."""
            session_id = request.args.get("session_id")
            if session_id:
                leave_room(session_id)
                logger.info(f"Client disconnected from session {session_id}")

        @self.socketio.on("create_session", namespace="/pty")
        def handle_create_session(data):
            """Handle session creation request."""
            try:
                command = data.get("command", "bash")
                args = data.get("args", [])
                cwd = data.get("cwd")
                env = data.get("env", {})
                rows = data.get("rows", 24)
                cols = data.get("cols", 80)

                session_id = self.create_session(
                    command=command, args=args, cwd=cwd, env=env, rows=rows, cols=cols
                )

                return {"session_id": session_id}

            except RuntimeError as e:
                return {"error": str(e)}

        @self.socketio.on("pty-input", namespace="/pty")
        def handle_pty_input(data):
            """Handle input from client."""
            session_id = data.get("session_id")
            if session_id and session_id in self.sessions:
                session = self.sessions[session_id]
                if self.backend and session:
                    self.backend.write_input(session, data["input"])

        @self.socketio.on("resize", namespace="/pty")
        def handle_resize(data):
            """Handle terminal resize."""
            session_id = data.get("session_id")
            if session_id and session_id in self.sessions:
                session = self.sessions[session_id]
                if self.backend and session:
                    rows = data.get("rows", 24)
                    cols = data.get("cols", 80)
                    if self.backend.resize(session, rows, cols):
                        logger.debug(f"Resized session {session_id} to {rows}x{cols}")

        @self.socketio.on("heartbeat", namespace="/pty")
        def handle_heartbeat(data):
            """Handle heartbeat from client to keep session alive."""
            session_id = data.get("session_id")
            if session_id and session_id in self.sessions:
                self.sessions[session_id].update_activity()
                logger.debug(f"Heartbeat received for session {session_id}")

    def _start_terminal_process(self, session_id: str):
        """Start a terminal process for a session."""
        session = self.sessions.get(session_id)
        if not session or session.child_pid:
            return

        # Initialize backend if not already done
        if not self.backend:
            try:
                self.backend = create_backend()
                logger.info(
                    f"Created terminal backend: {self.backend.get_platform_name()}"
                )
            except Exception as e:
                logger.error(f"Failed to create terminal backend: {e}")
                return

        # Start the process using the backend
        if self.backend.start_process(session):
            # Start background task to read output
            self.socketio.start_background_task(
                target=self._read_and_forward_pty_output, session_id=session_id
            )
            logger.info(
                f"Started terminal process for session {session_id}, "
                f"PID: {session.child_pid}"
            )

    def _read_and_forward_pty_output(self, session_id: str):
        """Read PTY output and forward to client (background task)."""
        session = self.sessions.get(session_id)

        while self.running and session and session.active:
            if not self.backend:
                logger.error(f"No backend available for session {session_id}")
                break

            try:
                # Check if process is still alive FIRST (before I/O operations)
                # This properly handles zombie processes via waitpid()
                if not self.backend.is_process_alive(session):
                    logger.info(f"Terminal process ended for session {session_id}")
                    session.active = False
                    self.socketio.emit(
                        "session_closed",
                        {"session_id": session_id, "exit_code": 0},
                        namespace="/pty",
                        room=session_id,
                    )
                    # Emit signal from background thread - Qt should handle cross-thread signal
                    logger.info(
                        f"Emitting session_ended signal for session {session_id}"
                    )
                    self.session_ended.emit(session_id)
                    logger.info(
                        f"session_ended signal emitted for session {session_id}"
                    )
                    break

                # Process is alive, poll and read output
                if self.backend.poll_process(session, timeout=0.01):
                    output = self.backend.read_output(session)
                    if output:
                        self.socketio.emit(
                            "pty-output",
                            {"output": output, "session_id": session_id},
                            namespace="/pty",
                            room=session_id,
                        )

            except Exception as e:
                logger.error(f"Error reading terminal output: {e}", exc_info=True)
                session.active = False
                self.session_ended.emit(session_id)
                break

            self.socketio.sleep(0.01)

    def create_session(
        self,
        command: Optional[str] = None,
        args=None,
        cwd: Optional[str] = None,
        env=None,
        rows: int = 24,
        cols: int = 80,
    ) -> str:
        """
        Create a new terminal session.

        Args:
            command: Shell command to run (default: None = auto-detect platform shell)
            args: Command arguments (list or string)
            cwd: Working directory
            env: Environment variables
            rows: Terminal rows
            cols: Terminal columns

        Returns:
            session_id for the created session

        Raises:
            RuntimeError: If maximum sessions reached

        Note:
            If command is None, automatically detects platform-appropriate shell:
            - Windows: powershell.exe or cmd.exe
            - Unix: $SHELL environment variable or bash
        """
        if len(self.sessions) >= self.max_sessions:
            raise RuntimeError(
                f"Maximum number of sessions ({self.max_sessions}) reached"
            )

        # Start server if not running (must be running before creating sessions)
        if not self.running:
            self.start()

        # Generate short session ID (8 chars)
        session_id = str(uuid.uuid4())[:8]

        # Parse args if string
        if isinstance(args, str):
            args_list = shlex.split(args) if args else []
        else:
            args_list = args or []

        # Prepare environment variables with default TERM if not provided
        session_env = env or {}
        if "TERM" not in session_env:
            session_env["TERM"] = "xterm-256color"
            logger.debug("Setting TERM environment variable to default: xterm-256color")

        # Build session parameters
        session_params = {
            "session_id": session_id,
            "args": args_list,
            "cwd": cwd,
            "env": session_env,
            "rows": rows,
            "cols": cols,
        }

        # Only include command if explicitly provided
        # Otherwise, TerminalSession will use its default_factory (get_default_shell)
        if command is not None:
            session_params["command"] = command

        session = TerminalSession(**session_params)

        self.sessions[session_id] = session
        logger.info(f"Created terminal session {session_id} (not started yet)")

        return session_id

    def destroy_session(self, session_id: str):
        """
        Destroy a terminal session.

        Args:
            session_id: Session to destroy
        """
        session = self.sessions.get(session_id)
        if not session:
            return

        session.active = False

        # Use backend to clean up the session
        if self.backend:
            self.backend.cleanup(session)

        # Remove from sessions
        del self.sessions[session_id]
        logger.info(f"Destroyed terminal session {session_id}")

    def get_session_url(self, session_id: str) -> str:
        """
        Get the URL for a terminal session.

        Args:
            session_id: Session ID

        Returns:
            Full URL for connecting to session

        Raises:
            ValueError: If session not found
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        url = f"http://{self.host}:{self.port}/terminal/{session_id}?session_id={session_id}"
        logger.info(f"Generated URL for session {session_id}: {url}")
        return url

    def start(self) -> int:
        """
        Start the Flask/SocketIO server.

        Returns:
            Port the server is running on
        """
        if self.running:
            return self.port

        self.running = True

        # Find available port if needed
        if self.port == 0:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("", 0))
                self.port = s.getsockname()[1]

        # Start server in background thread
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

        # Wait for server to start
        time.sleep(1.0)
        logger.info(f"Multi-session terminal server started on {self.host}:{self.port}")

        # Start periodic cleanup
        self._start_cleanup_task()

        return self.port

    def shutdown(self):
        """Shutdown the server and cleanup all sessions."""
        if not self.running:
            return

        logger.info("Shutting down multi-session terminal server...")
        self.running = False

        # Destroy all sessions
        session_ids = list(self.sessions.keys())
        for session_id in session_ids:
            self.destroy_session(session_id)

        # Stop server
        if self.socketio:
            try:
                if hasattr(self.socketio, "stop"):
                    self.socketio.stop()
            except (RuntimeError, AttributeError) as e:
                logger.warning(f"Graceful shutdown failed: {e}")

        logger.info("Multi-session terminal server shutdown complete")

    def cleanup_inactive_sessions(self, timeout_seconds: float = 3600):
        """
        Clean up inactive sessions.

        Args:
            timeout_seconds: Inactivity timeout (default: 1 hour)
        """
        sessions_to_remove = []

        for session_id, session in self.sessions.items():
            # Check inactivity timeout
            if session.is_inactive(timeout_seconds):
                logger.info(f"Session {session_id} inactive for > {timeout_seconds}s")
                sessions_to_remove.append(session_id)
            # Check if process died
            elif self.backend and not self.backend.is_process_alive(session):
                logger.info(f"Session {session_id} process is dead")
                sessions_to_remove.append(session_id)
            # Check active flag
            elif not session.active:
                logger.info(f"Session {session_id} marked inactive")
                sessions_to_remove.append(session_id)

        for session_id in sessions_to_remove:
            logger.info(f"Cleaning up inactive session {session_id}")
            self.destroy_session(session_id)

    def _start_cleanup_task(self):
        """Start periodic cleanup of inactive sessions."""

        def cleanup_loop():
            while self.running:
                time.sleep(60)  # Run cleanup every minute
                try:
                    self.cleanup_inactive_sessions(timeout_seconds=3600)  # 1 hour
                except Exception as e:
                    logger.error(f"Error during session cleanup: {e}")

        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()
