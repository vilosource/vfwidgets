# Multi-Session Terminal Server Implementation Plan

## Overview

This document outlines the implementation plan for adding multi-session server support to the `vfwidgets-terminal` package. The previous viloxterm implementation served as reference - now we create our own clean implementation.

## Goals

1. **Add multi-session server** to terminal widget package
2. **Keep backwards compatibility** with existing embedded server mode
3. **Provide reference implementation** users can adopt or customize
4. **Maintain clean architecture** without ViloxTerm-specific code

## Architecture

### Current State

```
vfwidgets-terminal/
├── src/vfwidgets_terminal/
│   ├── terminal.py              # TerminalWidget (supports server_url)
│   ├── embedded_server.py       # EmbeddedTerminalServer (1:1 mode)
│   └── constants.py
```

**Current behavior:**
```python
# Each widget creates its own server
terminal1 = TerminalWidget()  # Server on port 5001
terminal2 = TerminalWidget()  # Server on port 5002
terminal3 = TerminalWidget()  # Server on port 5003
```

### Target State

```
vfwidgets-terminal/
├── src/vfwidgets_terminal/
│   ├── terminal.py              # TerminalWidget (enhanced)
│   ├── embedded_server.py       # EmbeddedTerminalServer (legacy)
│   ├── multi_session_server.py  # MultiSessionTerminalServer (new)
│   ├── backends/                # Backend abstraction (new)
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── unix_backend.py
│   │   └── windows_backend.py
│   ├── session.py               # TerminalSession model (new)
│   └── constants.py
└── examples/
    ├── simple_terminal.py       # Single terminal (embedded mode)
    ├── multi_terminal_app.py    # Multiple terminals (shared server)
    └── custom_server.py         # Custom server implementation
```

**New usage modes:**

```python
# Mode 1: Embedded (backwards compatible)
terminal = TerminalWidget()

# Mode 2: Shared server (new)
server = MultiSessionTerminalServer(port=5000)
server.start()
terminal1 = TerminalWidget(server_url="http://localhost:5000")
terminal2 = TerminalWidget(server_url="http://localhost:5000")

# Mode 3: Custom server (protocol-based)
terminal = TerminalWidget(server_url="http://custom:5000")
```

## Implementation Phases

### Phase 1: Backend Abstraction Layer

**Goal:** Create platform-agnostic PTY management

**Files to create:**

1. **`src/vfwidgets_terminal/backends/base.py`**
   - Abstract `TerminalBackend` class
   - Platform-agnostic interface for PTY operations
   - Based on reference implementation but simplified

2. **`src/vfwidgets_terminal/backends/unix_backend.py`**
   - Unix/Linux PTY implementation using `pty.fork()`
   - Uses `select.select()` for non-blocking I/O
   - Handles process lifecycle and signals

3. **`src/vfwidgets_terminal/backends/windows_backend.py`**
   - Windows ConPTY implementation (requires `pywinpty`)
   - Conditional import (optional dependency)

4. **`src/vfwidgets_terminal/backends/__init__.py`**
   - Factory function `create_backend()`
   - Auto-detects platform and creates appropriate backend

**Key Design Principles:**
- Backend is shared across sessions (one instance handles all PTYs)
- Clean separation between server logic and PTY management
- Easy to test and mock
- Cross-platform from day one

### Phase 2: Session Model

**Goal:** Define session data structure

**File to create:** `src/vfwidgets_terminal/session.py`

```python
from dataclasses import dataclass, field
from typing import Optional, Dict, List
import time

@dataclass
class TerminalSession:
    """Represents a single terminal session."""

    session_id: str
    command: str = "bash"
    args: List[str] = field(default_factory=list)
    cwd: Optional[str] = None
    env: Dict[str, str] = field(default_factory=dict)

    # Terminal dimensions
    rows: int = 24
    cols: int = 80

    # Process info (set by backend)
    fd: Optional[int] = None              # PTY file descriptor
    child_pid: Optional[int] = None       # Process ID

    # Lifecycle tracking
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    active: bool = True

    # Extensibility
    metadata: Dict[str, any] = field(default_factory=dict)
```

### Phase 3: MultiSessionTerminalServer

**Goal:** Create reference multi-session server implementation

**File to create:** `src/vfwidgets_terminal/multi_session_server.py`

**Key Components:**

```python
class MultiSessionTerminalServer:
    """
    Reference implementation of multi-session terminal server.

    Features:
    - Single Flask/SocketIO server handling multiple sessions
    - Session-based routing using SocketIO rooms
    - Automatic session cleanup
    - Heartbeat mechanism
    - Cross-platform via backend abstraction
    """

    def __init__(self, port: int = 0, host: str = "127.0.0.1"):
        self.port = port
        self.host = host
        self.sessions: Dict[str, TerminalSession] = {}
        self.backend = None
        self.app = None
        self.socketio = None
        self.running = False
        self.max_sessions = 20

    def start(self) -> int:
        """Start the server and return the port."""

    def create_session(self, command="bash", args=None, cwd=None, env=None) -> str:
        """Create a new terminal session and return session_id."""

    def destroy_session(self, session_id: str):
        """Destroy a terminal session."""

    def get_session_url(self, session_id: str) -> str:
        """Get the URL for connecting to a session."""

    def shutdown(self):
        """Shutdown server and cleanup all sessions."""
```

**SocketIO Protocol:**

Namespace: `/pty`

**Events:**

1. **Client → Server: `create_session`**
   ```json
   {
       "command": "bash",
       "args": ["-l"],
       "cwd": "/home/user",
       "env": {"TERM": "xterm-256color"},
       "rows": 24,
       "cols": 80
   }

   Response: {"session_id": "abc12345"}
   ```

2. **Client → Server: `connect`**
   - Query param: `?session_id=abc12345`
   - Action: `join_room(session_id)`

3. **Client → Server: `pty-input`**
   ```json
   {"session_id": "abc12345", "input": "ls\n"}
   ```

4. **Server → Client: `pty-output`**
   ```json
   {"session_id": "abc12345", "output": "file1\nfile2\n"}
   ```
   - Emitted to room: Only clients in `session_id` room receive

5. **Client → Server: `resize`**
   ```json
   {"session_id": "abc12345", "rows": 40, "cols": 120}
   ```

6. **Client → Server: `heartbeat`**
   ```json
   {"session_id": "abc12345"}
   ```
   - Updates `session.last_activity`

7. **Server → Client: `session_closed`**
   ```json
   {"session_id": "abc12345", "exit_code": 0}
   ```

**Key Features from Reference:**

1. **Room-based routing:**
   ```python
   @self.socketio.on("connect", namespace="/pty")
   def handle_connect():
       session_id = request.args.get("session_id")
       if session_id in self.sessions:
           join_room(session_id)

   # Output only goes to clients in this session's room
   self.socketio.emit("pty-output", {...}, room=session_id, namespace="/pty")
   ```

2. **Background output reader:**
   ```python
   def _start_output_reader(self, session_id: str):
       """Background task to read PTY output and forward to client."""
       def reader():
           session = self.sessions[session_id]
           while session.active and self.running:
               if self.backend.poll_process(session, timeout=0.01):
                   output = self.backend.read_output(session)
                   if output:
                       self.socketio.emit(
                           "pty-output",
                           {"session_id": session_id, "output": output},
                           room=session_id,
                           namespace="/pty"
                       )

               if not self.backend.is_process_alive(session):
                   session.active = False
                   self.socketio.emit("session_closed",
                       {"session_id": session_id, "exit_code": 0},
                       room=session_id, namespace="/pty")
                   break

               self.socketio.sleep(0.01)

       self.socketio.start_background_task(reader)
   ```

3. **Session cleanup:**
   ```python
   def cleanup_inactive_sessions(self, timeout_seconds=3600):
       """Remove sessions inactive for > timeout."""
       now = time.time()
       to_remove = []

       for session_id, session in self.sessions.items():
           # Timeout check
           if now - session.last_activity > timeout_seconds:
               to_remove.append(session_id)
           # Dead process check
           elif not self.backend.is_process_alive(session):
               to_remove.append(session_id)

       for session_id in to_remove:
           self.destroy_session(session_id)
   ```

4. **Periodic cleanup task:**
   ```python
   def _start_cleanup_task(self):
       def cleanup_loop():
           while self.running:
               time.sleep(60)  # Every minute
               self.cleanup_inactive_sessions()

       threading.Thread(target=cleanup_loop, daemon=True).start()
   ```

### Phase 4: Update TerminalWidget

**Goal:** Add support for connecting to multi-session server

**File to update:** `src/vfwidgets_terminal/terminal.py`

**Changes needed:**

1. **Add session_id tracking:**
   ```python
   class TerminalWidget(QWidget):
       def __init__(self, server_url=None, port=0, ...):
           self.server_url = server_url
           self.session_id = None  # Track our session ID
           self.server = None
   ```

2. **Session creation when using external server:**
   ```python
   def _start_terminal(self):
       if self.server_url:
           # Connect to external multi-session server
           self.session_id = self._create_session_via_socketio()
           url = f"{self.server_url}?session_id={self.session_id}"
           self._load_terminal_url(url)
       else:
           # Embedded mode (existing code)
           self.server = EmbeddedTerminalServer(...)
           self.server.start()
   ```

3. **Session creation helper:**
   ```python
   def _create_session_via_socketio(self) -> str:
       """Create session on external server via SocketIO."""
       import socketio

       sio = socketio.Client()
       sio.connect(self.server_url, namespaces=['/pty'])

       response = sio.call('create_session', {
           'command': self.command,
           'args': self.args,
           'cwd': self.cwd,
           'env': self.env,
           'rows': 24,
           'cols': 80
       }, namespace='/pty')

       sio.disconnect()
       return response['session_id']
   ```

4. **Cleanup handling:**
   ```python
   def cleanup(self):
       if self.server_url and self.session_id:
           # Send close_session to external server
           self._close_session_via_socketio()
       elif self.server:
           # Embedded mode cleanup (existing)
           self.server.stop()
   ```

### Phase 5: Update terminal.html

**Goal:** Support session-based connection

**File to update:** `src/vfwidgets_terminal/resources/terminal.html`

**Changes needed:**

1. **Parse session_id from URL:**
   ```javascript
   const urlParams = new URLSearchParams(window.location.search);
   const sessionId = urlParams.get('session_id');
   ```

2. **Connect with session_id:**
   ```javascript
   let socketPath = '/socket.io/';
   let namespace = '/pty';

   // For multi-session server, include session_id
   if (sessionId) {
       socket = io(namespace, {
           path: socketPath,
           query: {session_id: sessionId}
       });
   } else {
       // Embedded server mode (existing)
       socket = io(namespace, {path: socketPath});
   }
   ```

3. **Include session_id in messages:**
   ```javascript
   // Send input
   term.onData(data => {
       socket.emit('pty-input', {
           session_id: sessionId,
           input: data
       });
   });

   // Receive output
   socket.on('pty-output', (data) => {
       if (data.session_id === sessionId) {
           term.write(data.output);
       }
   });

   // Handle resize
   term.onResize(({rows, cols}) => {
       socket.emit('resize', {
           session_id: sessionId,
           rows: rows,
           cols: cols
       });
   });

   // Session closed
   socket.on('session_closed', (data) => {
       if (data.session_id === sessionId) {
           term.write('\r\n\r\n[Process exited]\r\n');
       }
   });
   ```

4. **Add heartbeat:**
   ```javascript
   // Send heartbeat every 30 seconds
   if (sessionId) {
       setInterval(() => {
           socket.emit('heartbeat', {session_id: sessionId});
       }, 30000);
   }
   ```

### Phase 6: Examples

**Goal:** Provide clear usage examples

#### Example 1: Simple Terminal (Embedded Mode)

**File:** `examples/01_simple_terminal.py`

```python
"""Simple terminal using embedded server (one terminal)."""
import sys
from PySide6.QtWidgets import QApplication
from vfwidgets_terminal import TerminalWidget

app = QApplication(sys.argv)

# Embedded mode - widget creates its own server
terminal = TerminalWidget()
terminal.resize(800, 600)
terminal.show()

sys.exit(app.exec())
```

#### Example 2: Multi-Terminal Application

**File:** `examples/02_multi_terminal_app.py`

```python
"""Multiple terminals sharing a single server."""
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget
from vfwidgets_terminal import TerminalWidget, MultiSessionTerminalServer

class MultiTerminalApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Terminal Demo")

        # Create shared server
        self.server = MultiSessionTerminalServer(port=5000)
        self.server.start()

        # Create tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Add multiple terminals (all using shared server)
        for i in range(5):
            terminal = TerminalWidget(
                server_url="http://localhost:5000"
            )
            self.tabs.addTab(terminal, f"Terminal {i+1}")

        self.resize(1000, 700)

    def closeEvent(self, event):
        # Cleanup
        self.server.shutdown()
        event.accept()

app = QApplication(sys.argv)
window = MultiTerminalApp()
window.show()
sys.exit(app.exec())
```

#### Example 3: Custom Server Implementation

**File:** `examples/03_custom_server.py`

```python
"""Example of implementing a custom terminal server."""
import uuid
from flask import Flask, request
from flask_socketio import SocketIO, join_room, emit
from vfwidgets_terminal.backends import create_backend
from vfwidgets_terminal.session import TerminalSession

class CustomTerminalServer:
    """Minimal custom server implementation."""

    def __init__(self, port=5000):
        self.port = port
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.sessions = {}
        self.backend = create_backend()
        self._setup_routes()

    def _setup_routes(self):
        @self.socketio.on('create_session', namespace='/pty')
        def create_session(data):
            session_id = str(uuid.uuid4())[:8]
            session = TerminalSession(
                session_id=session_id,
                command=data.get('command', 'bash'),
                args=data.get('args', []),
                cwd=data.get('cwd'),
                env=data.get('env', {})
            )

            # Start PTY process
            self.backend.start_process(session)
            self.sessions[session_id] = session

            # Start output reader
            self._start_output_reader(session_id)

            return {'session_id': session_id}

        @self.socketio.on('connect', namespace='/pty')
        def handle_connect():
            session_id = request.args.get('session_id')
            if session_id in self.sessions:
                join_room(session_id)

        @self.socketio.on('pty-input', namespace='/pty')
        def handle_input(data):
            session_id = data.get('session_id')
            if session_id in self.sessions:
                session = self.sessions[session_id]
                self.backend.write_input(session, data['input'])

        @self.socketio.on('resize', namespace='/pty')
        def handle_resize(data):
            session_id = data.get('session_id')
            if session_id in self.sessions:
                session = self.sessions[session_id]
                self.backend.resize(session, data['rows'], data['cols'])

    def _start_output_reader(self, session_id):
        def reader():
            session = self.sessions[session_id]
            while session.active:
                if self.backend.poll_process(session):
                    output = self.backend.read_output(session)
                    if output:
                        self.socketio.emit('pty-output',
                            {'session_id': session_id, 'output': output},
                            room=session_id, namespace='/pty')

                if not self.backend.is_process_alive(session):
                    self.socketio.emit('session_closed',
                        {'session_id': session_id, 'exit_code': 0},
                        room=session_id, namespace='/pty')
                    break

                self.socketio.sleep(0.01)

        self.socketio.start_background_task(reader)

    def run(self):
        self.socketio.run(self.app, port=self.port)

if __name__ == '__main__':
    server = CustomTerminalServer(port=5000)
    server.run()
```

Then use with terminal:
```python
from vfwidgets_terminal import TerminalWidget

terminal = TerminalWidget(server_url="http://localhost:5000")
terminal.show()
```

## Testing Strategy

### Unit Tests

1. **Backend tests** (`tests/test_backends.py`)
   - PTY creation and lifecycle
   - Input/output handling
   - Resize operations
   - Process management

2. **Session tests** (`tests/test_session.py`)
   - Session creation
   - Session cleanup
   - Timeout handling

3. **Server tests** (`tests/test_multi_session_server.py`)
   - Session routing
   - Multiple concurrent sessions
   - Cleanup mechanisms

### Integration Tests

1. **Widget + embedded server** (existing)
2. **Widget + multi-session server**
3. **Multiple widgets + shared server**

### Performance Tests

1. **Resource usage**
   - 1 terminal (embedded) vs 20 terminals (embedded)
   - 20 terminals (shared server)
   - Memory comparison

2. **Session limits**
   - Max concurrent sessions
   - Session cleanup efficiency

## Migration Guide

### For Existing Users (Backwards Compatible)

**Before (still works):**
```python
terminal = TerminalWidget()
```

**After (same behavior):**
```python
terminal = TerminalWidget()  # Still creates embedded server
```

### For ViloxTerm Application

**Before (tmp/viloxterm):**
```python
from viloxterm import TerminalServerManager, TerminalWidget

server = TerminalServerManager()  # Singleton
terminal = TerminalWidget()
terminal.start_terminal()
```

**After (clean implementation):**
```python
from vfwidgets_terminal import MultiSessionTerminalServer, TerminalWidget

server = MultiSessionTerminalServer(port=5000)
server.start()
terminal = TerminalWidget(server_url="http://localhost:5000")
```

## Documentation Updates

1. **README.md**
   - Add multi-session server section
   - Usage examples for all three modes
   - Performance comparison

2. **API.md**
   - Document `MultiSessionTerminalServer` class
   - Document backend abstraction
   - Protocol specification reference

3. **MIGRATION.md**
   - Guide for upgrading from embedded to shared server
   - ViloxTerm-specific migration

## Success Criteria

- ✅ Backwards compatible (existing code still works)
- ✅ Multi-session server working with 20+ concurrent terminals
- ✅ Cross-platform (Unix/Windows)
- ✅ Memory efficient (shared server uses <50% resources vs embedded)
- ✅ Clean API (easy to use in all three modes)
- ✅ Well documented with examples
- ✅ Fully tested (unit + integration)

## Timeline Estimate

- **Phase 1 (Backend):** 2-3 days
- **Phase 2 (Session):** 1 day
- **Phase 3 (Server):** 3-4 days
- **Phase 4 (Widget):** 2 days
- **Phase 5 (HTML):** 1 day
- **Phase 6 (Examples):** 1 day
- **Testing:** 2-3 days
- **Documentation:** 1-2 days

**Total:** ~2 weeks

## Next Steps

1. Start with Phase 1 (Backend abstraction)
2. Write tests alongside implementation (TDD)
3. Create examples as we go (validate API design)
4. Document lessons learned
5. Get feedback before finalizing API
