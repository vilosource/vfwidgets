# Terminal Server Implementation Guide

## Overview

This guide shows you how to implement a custom terminal server that works with the vfwidgets-terminal TerminalWidget. By implementing the SocketIO protocol, you can create servers with custom authentication, remote access, logging, or integrate with existing infrastructure.

**Complete Working Example:** See `examples/03_custom_server.py` for a minimal (~150 line) reference implementation.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Protocol Requirements](#protocol-requirements)
3. [Step-by-Step Implementation](#step-by-step-implementation)
4. [Room-Based Routing](#room-based-routing)
5. [Session Lifecycle](#session-lifecycle)
6. [Authentication](#authentication)
7. [Testing Your Server](#testing-your-server)
8. [Common Patterns](#common-patterns)

---

## Quick Start

### Minimal Server (5 Minutes)

```python
from flask import Flask, request
from flask_socketio import SocketIO, join_room, emit
from vfwidgets_terminal.backends import create_backend
from vfwidgets_terminal.session import TerminalSession
import uuid

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key"
socketio = SocketIO(app, cors_allowed_origins="*")

sessions = {}
backend = create_backend()

@socketio.on('create_session', namespace='/pty')
def create_session(data):
    session_id = str(uuid.uuid4())[:8]
    session = TerminalSession(
        session_id=session_id,
        command=data.get('command', 'bash'),
        rows=data.get('rows', 24),
        cols=data.get('cols', 80)
    )

    if backend.start_process(session):
        sessions[session_id] = session
        socketio.start_background_task(
            target=read_output_loop,
            session_id=session_id
        )
        return {'session_id': session_id}
    return {'error': 'Failed to start'}

@socketio.on('connect', namespace='/pty')
def handle_connect():
    session_id = request.args.get('session_id')
    if session_id in sessions:
        join_room(session_id)

@socketio.on('pty-input', namespace='/pty')
def handle_input(data):
    session_id = data.get('session_id')
    if session_id in sessions:
        backend.write_input(sessions[session_id], data['input'])

def read_output_loop(session_id):
    session = sessions[session_id]
    while session.active:
        if backend.poll_process(session, timeout=0.01):
            output = backend.read_output(session)
            if output:
                socketio.emit(
                    'pty-output',
                    {'session_id': session_id, 'output': output},
                    room=session_id,
                    namespace='/pty'
                )
        if not backend.is_process_alive(session):
            session.active = False
            socketio.emit(
                'session_closed',
                {'session_id': session_id, 'exit_code': 0},
                room=session_id,
                namespace='/pty'
            )
            break
        socketio.sleep(0.01)

if __name__ == '__main__':
    socketio.run(app, port=5001)
```

That's it! A working terminal server in ~60 lines.

---

## Protocol Requirements

### Required SocketIO Events

**Namespace:** All events use `/pty` namespace.

| Event | Direction | Required | Purpose |
|-------|-----------|----------|---------|
| `create_session` | Client → Server | ✅ Yes | Create new terminal session |
| `connect` | Client → Server | ✅ Yes | Join session room |
| `pty-input` | Client → Server | ✅ Yes | Send user input to terminal |
| `pty-output` | Server → Client | ✅ Yes | Send terminal output to client |
| `resize` | Client → Server | ⚠️ Recommended | Handle terminal resize |
| `heartbeat` | Client → Server | ⚠️ Recommended | Keep session alive |
| `session_closed` | Server → Client | ⚠️ Recommended | Notify session ended |

### Message Formats

**create_session:**
```python
# Client sends:
{
    'command': 'bash',          # Shell command
    'args': ['-l'],             # Optional arguments
    'cwd': '/home/user',        # Optional working directory
    'env': {'VAR': 'value'},    # Optional environment
    'rows': 24,                 # Terminal rows
    'cols': 80                  # Terminal columns
}

# Server responds:
{'session_id': 'abc12345'}  # Success
# OR
{'error': 'Error message'}   # Failure
```

**pty-input:**
```python
# Client sends:
{
    'session_id': 'abc12345',
    'input': 'ls -la\n'
}
```

**pty-output:**
```python
# Server sends:
{
    'session_id': 'abc12345',
    'output': 'file1.txt\nfile2.txt\n'
}
```

**resize:**
```python
# Client sends:
{
    'session_id': 'abc12345',
    'rows': 30,
    'cols': 100
}
```

**heartbeat:**
```python
# Client sends (every 30 seconds):
{
    'session_id': 'abc12345'
}
```

**session_closed:**
```python
# Server sends:
{
    'session_id': 'abc12345',
    'exit_code': 0
}
```

---

## Step-by-Step Implementation

### Step 1: Set Up Flask and SocketIO

```python
from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key"  # Change in production!

socketio = SocketIO(
    app,
    cors_allowed_origins="*",  # Or specify allowed origins
    async_mode="threading"      # Use threading for background tasks
)
```

**Key Points:**
- `cors_allowed_origins="*"` allows all origins (restrict in production)
- `async_mode="threading"` enables background tasks for reading PTY output
- Secret key should be random and secure in production

### Step 2: Initialize Backend and Sessions

```python
from vfwidgets_terminal.backends import create_backend

# Global state
sessions = {}  # session_id -> TerminalSession
backend = create_backend()  # Auto-detects platform (Unix/Windows)

print(f"Using backend: {backend.get_platform_name()}")
```

**Why Global?**
- Flask/SocketIO handlers need access to sessions and backend
- Alternative: Use Flask application context or dependency injection

### Step 3: Implement create_session Handler

```python
import uuid
from vfwidgets_terminal.session import TerminalSession

@socketio.on('create_session', namespace='/pty')
def create_session(data):
    """Create a new terminal session."""
    # Generate unique session ID (8 chars for brevity)
    session_id = str(uuid.uuid4())[:8]

    # Create session object
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
    if backend.start_process(session):
        # Store session
        sessions[session_id] = session

        # Start background task to read output
        socketio.start_background_task(
            target=read_output_loop,
            session_id=session_id
        )

        print(f"Created session: {session_id}")
        return {'session_id': session_id}
    else:
        print(f"Failed to start session")
        return {'error': 'Failed to start process'}
```

**Critical Points:**
1. **Session ID:** Use UUID to avoid collisions
2. **Error Handling:** Return error dict if process fails to start
3. **Background Task:** Start IMMEDIATELY after process starts
4. **Session Storage:** Add to dict BEFORE starting background task

### Step 4: Implement connect Handler

```python
from flask import request
from flask_socketio import join_room

@socketio.on('connect', namespace='/pty')
def handle_connect():
    """Handle client connection."""
    # Get session ID from query params
    session_id = request.args.get('session_id')

    # Validate session exists
    if session_id and session_id in sessions:
        # Join room (enables room-based routing)
        join_room(session_id)
        print(f"Client connected to session: {session_id}")
    else:
        print(f"Connection rejected: invalid session {session_id}")
        return False  # Reject connection
```

**Room-Based Routing:**
- `join_room(session_id)` adds client to a SocketIO "room"
- Messages sent to `room=session_id` only go to clients in that room
- This provides automatic message isolation between sessions

### Step 5: Implement pty-input Handler

```python
@socketio.on('pty-input', namespace='/pty')
def handle_input(data):
    """Handle input from client."""
    session_id = data.get('session_id')

    # Validate session
    if session_id and session_id in sessions:
        session = sessions[session_id]

        # Write to PTY
        backend.write_input(session, data['input'])
```

**Simple!** Just pass input to backend.

### Step 6: Implement resize Handler

```python
@socketio.on('resize', namespace='/pty')
def handle_resize(data):
    """Handle terminal resize."""
    session_id = data.get('session_id')

    if session_id and session_id in sessions:
        session = sessions[session_id]
        rows = data.get('rows', 24)
        cols = data.get('cols', 80)

        if backend.resize(session, rows, cols):
            print(f"Resized session {session_id} to {rows}x{cols}")
```

### Step 7: Implement heartbeat Handler

```python
@socketio.on('heartbeat', namespace='/pty')
def handle_heartbeat(data):
    """Handle heartbeat to keep session alive."""
    session_id = data.get('session_id')

    if session_id and session_id in sessions:
        # Update activity timestamp
        sessions[session_id].update_activity()
```

**Why Heartbeat?**
- Client sends every 30 seconds
- Allows server to distinguish active vs. abandoned sessions
- Used by cleanup logic to remove inactive sessions

### Step 8: Implement Output Reading Loop

```python
from flask_socketio import emit

def read_output_loop(session_id):
    """Background task: Read PTY output and forward to client."""
    session = sessions.get(session_id)

    while session and session.active:
        # Poll for data (non-blocking, 10ms timeout)
        if backend.poll_process(session, timeout=0.01):
            # Read output
            output = backend.read_output(session)

            if output:
                # Send to client (room-based routing)
                socketio.emit(
                    'pty-output',
                    {'session_id': session_id, 'output': output},
                    room=session_id,  # Only clients in this room get it
                    namespace='/pty'
                )

        # Check if process is still alive
        if not backend.is_process_alive(session):
            print(f"Session {session_id} process ended")
            session.active = False

            # Notify client
            socketio.emit(
                'session_closed',
                {'session_id': session_id, 'exit_code': 0},
                room=session_id,
                namespace='/pty'
            )
            break

        # Small sleep to avoid busy-waiting
        socketio.sleep(0.01)  # Use socketio.sleep, not time.sleep!

    # Cleanup
    if session_id in sessions:
        del sessions[session_id]
```

**Critical Points:**
1. **Use socketio.sleep()** not `time.sleep()` - socketio.sleep() yields to event loop
2. **Room-based emit** ensures only clients in session's room receive output
3. **Check is_process_alive()** to detect when shell exits
4. **Cleanup session** after loop exits

### Step 9: Run the Server

```python
if __name__ == '__main__':
    socketio.run(
        app,
        port=5001,
        debug=False,
        allow_unsafe_werkzeug=True  # Only for development!
    )
```

**Production:** Use a proper WSGI server like Gunicorn with gevent/eventlet.

---

## Room-Based Routing

### Why Rooms?

**Problem:** With multiple sessions, how do you ensure output goes to the right client?

**Solution:** SocketIO rooms provide automatic isolation.

### How It Works

```python
# Client A connects with session_id=abc123
join_room('abc123')  # Client A joins room "abc123"

# Client B connects with session_id=def456
join_room('def456')  # Client B joins room "def456"

# Send output for session abc123
emit('pty-output', {'output': 'data'}, room='abc123')
# → Only Client A receives this

# Send output for session def456
emit('pty-output', {'output': 'data'}, room='def456')
# → Only Client B receives this
```

**Benefits:**
- No manual client tracking
- No message filtering needed
- Scales to hundreds of sessions
- Built into SocketIO

---

## Session Lifecycle

### Complete Flow

```
1. Client: emit('create_session', {...})
2. Server: Creates TerminalSession
3. Server: backend.start_process(session)
4. Server: Start background output reader
5. Server: return {'session_id': '...'}

6. Client: Connect to server with session_id
7. Server: join_room(session_id)

8. Loop: Client sends input, server sends output
9. Every 30s: Client sends heartbeat

10. Process exits OR timeout
11. Server: emit('session_closed')
12. Server: Cleanup session
```

---

## Authentication

### Adding Auth to Your Server

```python
from functools import wraps
from flask import request

def require_auth(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not validate_token(token):  # Your validation logic
            return {'error': 'Unauthorized'}, 401
        return f(*args, **kwargs)
    return decorated

@socketio.on('create_session', namespace='/pty')
@require_auth
def create_session(data):
    # ... rest of handler
    pass
```

### Token-Based Auth

```python
# Client provides token when connecting
terminal = TerminalWidget(
    server_url="http://server:5001?token=abc123"
)

# Server validates on connect
@socketio.on('connect', namespace='/pty')
def handle_connect():
    token = request.args.get('token')
    if not validate_token(token):
        return False  # Reject connection
    # ... rest of handler
```

---

## Testing Your Server

### Manual Test

```bash
# Terminal 1: Start server
python your_server.py

# Terminal 2: Test with TerminalWidget
python -c "
from vfwidgets_terminal import TerminalWidget
from PySide6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
terminal = TerminalWidget(server_url='http://localhost:5001')
terminal.show()
sys.exit(app.exec())
"
```

### Automated Test

```python
import pytest
from socketio import Client

def test_server():
    # Connect client
    sio = Client()
    sio.connect('http://localhost:5001', namespaces=['/pty'])

    # Create session
    result = sio.emit('create_session', {
        'command': 'bash',
        'rows': 24,
        'cols': 80
    }, namespace='/pty', callback=True)

    assert 'session_id' in result
    session_id = result['session_id']

    # Connect to session
    sio.disconnect()
    sio.connect(f'http://localhost:5001?session_id={session_id}',
                namespaces=['/pty'])

    # Test input/output
    received_output = []

    @sio.on('pty-output', namespace='/pty')
    def on_output(data):
        received_output.append(data['output'])

    sio.emit('pty-input', {
        'session_id': session_id,
        'input': 'echo test\n'
    }, namespace='/pty')

    sio.sleep(1)

    assert any('test' in output for output in received_output)

    sio.disconnect()
```

---

## Common Patterns

### Pattern 1: Session Cleanup

```python
import time

def cleanup_inactive_sessions():
    """Remove sessions inactive for > 1 hour."""
    timeout = 3600  # 1 hour
    now = time.time()

    to_remove = []
    for session_id, session in sessions.items():
        if session.is_inactive(timeout):
            to_remove.append(session_id)

    for session_id in to_remove:
        backend.cleanup(sessions[session_id])
        del sessions[session_id]
        print(f"Cleaned up inactive session: {session_id}")

# Run cleanup periodically
def cleanup_loop():
    while True:
        socketio.sleep(60)  # Every minute
        cleanup_inactive_sessions()

# Start cleanup task
socketio.start_background_task(target=cleanup_loop)
```

### Pattern 2: Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@socketio.on('pty-input', namespace='/pty')
def handle_input(data):
    session_id = data.get('session_id')
    logger.info(f"Input for {session_id}: {repr(data['input'][:50])}")
    # ... handle input
```

### Pattern 3: Rate Limiting

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per minute"]
)

@socketio.on('create_session', namespace='/pty')
@limiter.limit("5 per minute")
def create_session(data):
    # ... handler
    pass
```

---

## Next Steps

1. **Review Example:** See `examples/03_custom_server.py` for complete implementation
2. **Read Protocol Spec:** See `terminal-server-protocol-SPEC.md` for full protocol details
3. **Review Backend Guide:** See `backend-implementation-GUIDE.md` if customizing PTY handling
4. **Check Lessons Learned:** See `lessons-learned-GUIDE.md` for common pitfalls

---

## Summary

Implementing a custom terminal server requires:

1. ✅ Flask + SocketIO setup
2. ✅ Backend initialization (create_backend())
3. ✅ Session management (dict of sessions)
4. ✅ Required event handlers (create_session, connect, pty-input)
5. ✅ Background output reader (socketio.start_background_task)
6. ✅ Room-based routing (join_room + emit with room param)
7. ✅ Heartbeat and cleanup (optional but recommended)

The protocol is simple, the patterns are clear, and the reference implementation is < 200 lines.

---

**Document Version:** 1.0.0
**Last Updated:** 2025-10-02
**Reference:** `examples/03_custom_server.py`
