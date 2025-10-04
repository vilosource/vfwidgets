#!/usr/bin/env python3
"""
Custom Terminal Server Example

This example shows how to implement a minimal custom terminal server
that works with TerminalWidget. This demonstrates the protocol-based
architecture - any server implementing the protocol can be used.

This is useful for:
- Custom authentication
- Remote terminal servers
- Integration with existing infrastructure
- Special logging or monitoring

Usage:
    1. Run this script to start the custom server
    2. The server will print its URL
    3. Create TerminalWidget with that URL
"""

import sys
import uuid
from pathlib import Path

# Add parent directory to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from flask import Flask, request
from flask_socketio import SocketIO, join_room, emit
from vfwidgets_terminal.backends import create_backend
from vfwidgets_terminal.session import TerminalSession


class CustomTerminalServer:
    """
    Minimal custom terminal server implementation.

    This demonstrates the minimum requirements to create a compatible server.
    """

    def __init__(self, port=5001):
        self.port = port
        self.app = Flask(__name__)
        self.app.config["SECRET_KEY"] = "custom_server_secret"

        self.socketio = SocketIO(
            self.app,
            cors_allowed_origins="*",
            async_mode="threading"
        )

        self.sessions = {}
        self.backend = create_backend()
        print(f"Created backend: {self.backend.get_platform_name()}")

        self._setup_routes()

    def _setup_routes(self):
        """Setup SocketIO event handlers."""

        @self.socketio.on('create_session', namespace='/pty')
        def create_session(data):
            """Create a new terminal session."""
            # Generate session ID
            session_id = str(uuid.uuid4())[:8]

            # Create session
            session = TerminalSession(
                session_id=session_id,
                command=data.get('command', 'bash'),
                args=data.get('args', []),
                cwd=data.get('cwd'),
                env=data.get('env', {}),
                rows=data.get('rows', 24),
                cols=data.get('cols', 80)
            )

            # Start PTY process
            if self.backend.start_process(session):
                self.sessions[session_id] = session

                # Start output reader
                self.socketio.start_background_task(
                    target=self._read_output,
                    session_id=session_id
                )

                print(f"Created session: {session_id}")
                return {'session_id': session_id}
            else:
                return {'error': 'Failed to start process'}

        @self.socketio.on('connect', namespace='/pty')
        def handle_connect():
            """Handle client connection."""
            session_id = request.args.get('session_id')
            if session_id and session_id in self.sessions:
                join_room(session_id)
                print(f"Client connected to session: {session_id}")
            else:
                print(f"Connection rejected: session {session_id} not found")
                return False

        @self.socketio.on('pty-input', namespace='/pty')
        def handle_input(data):
            """Handle input from client."""
            session_id = data.get('session_id')
            if session_id in self.sessions:
                session = self.sessions[session_id]
                self.backend.write_input(session, data['input'])

        @self.socketio.on('resize', namespace='/pty')
        def handle_resize(data):
            """Handle terminal resize."""
            session_id = data.get('session_id')
            if session_id in self.sessions:
                session = self.sessions[session_id]
                rows = data.get('rows', 24)
                cols = data.get('cols', 80)
                self.backend.resize(session, rows, cols)
                print(f"Resized session {session_id} to {rows}x{cols}")

        @self.socketio.on('heartbeat', namespace='/pty')
        def handle_heartbeat(data):
            """Handle heartbeat from client."""
            session_id = data.get('session_id')
            if session_id in self.sessions:
                self.sessions[session_id].update_activity()

    def _read_output(self, session_id):
        """Read PTY output and forward to client (background task)."""
        session = self.sessions.get(session_id)

        while session and session.active:
            # Poll for data
            if self.backend.poll_process(session, timeout=0.01):
                output = self.backend.read_output(session)
                if output:
                    # Send to client (only those in this session's room)
                    self.socketio.emit(
                        'pty-output',
                        {'session_id': session_id, 'output': output},
                        room=session_id,
                        namespace='/pty'
                    )

            # Check if process is alive
            if not self.backend.is_process_alive(session):
                print(f"Session {session_id} process ended")
                session.active = False
                self.socketio.emit(
                    'session_closed',
                    {'session_id': session_id, 'exit_code': 0},
                    room=session_id,
                    namespace='/pty'
                )
                break

            self.socketio.sleep(0.01)

        # Cleanup
        if session_id in self.sessions:
            del self.sessions[session_id]

    def run(self):
        """Run the server."""
        print(f"\nCustom Terminal Server starting on port {self.port}")
        print(f"Connect terminals to: http://localhost:{self.port}")
        print("="*60)
        print("\nTo use this server from Python:")
        print(f"    terminal = TerminalWidget(server_url='http://localhost:{self.port}')")
        print("\nPress Ctrl+C to stop\n")

        self.socketio.run(
            self.app,
            port=self.port,
            debug=False,
            allow_unsafe_werkzeug=True
        )


def main():
    """Run custom server."""
    server = CustomTerminalServer(port=5001)
    try:
        server.run()
    except KeyboardInterrupt:
        print("\nServer stopped")


if __name__ == "__main__":
    main()
