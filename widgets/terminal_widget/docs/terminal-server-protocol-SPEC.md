# Terminal Server Protocol Specification

## Version 1.0

This document specifies the protocol for terminal servers that can work with `TerminalWidget`. Any server implementing this protocol can provide terminal services to the widget.

## Overview

**Architecture:**
```
TerminalWidget (Client)
    ↕
SocketIO over HTTP
    ↕
Terminal Server (Your Implementation)
    ↕
PTY/Shell Processes
```

**Key Concept:** The widget is a client that connects to ANY server implementing this protocol.

## Transport Layer

### Protocol: SocketIO over HTTP/HTTPS

**Why SocketIO?**
- Bidirectional communication (client ↔ server)
- Automatic reconnection
- Binary data support
- Wide language support

**Namespace:** `/pty`

All SocketIO events use the `/pty` namespace.

### Connection

**Client connects to:**
```
ws://server:port/socket.io/?session={session_id}&EIO=4&transport=websocket
```

**Query Parameters:**
- `session` (optional): Session ID to connect to existing session
- `EIO`: Engine.IO version (4)
- `transport`: websocket

## Message Types

### 1. Session Management

#### 1.1 Create Session

**Direction:** Client → Server

**Event:** `create_session`

**Purpose:** Request new terminal session creation

**Payload:**
```json
{
    "command": "bash",           // Required: Shell command
    "args": ["-l"],              // Optional: Command arguments
    "cwd": "/home/user",         // Optional: Working directory
    "env": {                     // Optional: Environment variables
        "PATH": "/usr/bin",
        "TERM": "xterm-256color"
    },
    "cols": 80,                  // Optional: Terminal columns (default: 80)
    "rows": 24                   // Optional: Terminal rows (default: 24)
}
```

**Response:**
```json
{
    "session_id": "abc-123-def-456",  // UUID of created session
    "url": "http://server:5000?session=abc-123-def-456"  // Optional: Direct URL
}
```

**Error Response:**
```json
{
    "error": "Failed to create session",
    "message": "Detailed error message"
}
```

#### 1.2 Close Session

**Direction:** Client → Server

**Event:** `close_session`

**Purpose:** Request session termination

**Payload:**
```json
{
    "session_id": "abc-123-def-456"
}
```

**Response:**
```json
{
    "success": true,
    "exit_code": 0  // Process exit code
}
```

#### 1.3 Session Closed (Notification)

**Direction:** Server → Client

**Event:** `session_closed`

**Purpose:** Notify client that session ended

**Payload:**
```json
{
    "session_id": "abc-123-def-456",
    "exit_code": 0,
    "reason": "process_exited"  // or "timeout", "killed", etc.
}
```

### 2. Data Transfer

#### 2.1 Input (Keyboard)

**Direction:** Client → Server

**Event:** `pty-input`

**Purpose:** Send user input to terminal

**Payload:**
```json
{
    "session_id": "abc-123-def-456",
    "input": "ls -la\n"
}
```

**Notes:**
- Input is UTF-8 encoded string
- Special keys sent as escape sequences (e.g., `\x03` for Ctrl+C)
- No response expected (fire-and-forget)

#### 2.2 Output (Display)

**Direction:** Server → Client

**Event:** `pty-output`

**Purpose:** Send terminal output to client

**Payload:**
```json
{
    "session_id": "abc-123-def-456",
    "output": "file1\nfile2\nfile3\n"
}
```

**Notes:**
- Output is UTF-8 encoded string
- May include ANSI escape codes for colors/formatting
- Server should emit in chunks (not line-by-line for performance)

### 3. Terminal Control

#### 3.1 Resize Terminal

**Direction:** Client → Server

**Event:** `resize`

**Purpose:** Change terminal dimensions

**Payload:**
```json
{
    "session_id": "abc-123-def-456",
    "rows": 40,
    "cols": 120
}
```

**Notes:**
- Server must call `ioctl(TIOCSWINSZ)` to resize PTY
- No response expected

### 4. Connection Events

#### 4.1 Connect

**Direction:** Client → Server

**Event:** `connect`

**Purpose:** Initial WebSocket connection established

**Server Actions:**
- Authenticate client (if required)
- Associate client with session (if `session` query param present)
- Send any queued messages

#### 4.2 Disconnect

**Direction:** Client → Server

**Event:** `disconnect`

**Purpose:** Client disconnected (graceful or ungraceful)

**Server Actions:**
- Keep session alive (client may reconnect)
- Optionally: Timeout and close session after N seconds

## HTTP REST API (Optional but Recommended)

### GET /health

**Purpose:** Server health check

**Response:**
```json
{
    "status": "healthy",
    "uptime_seconds": 3600,
    "active_sessions": 12
}
```

### POST /api/sessions

**Purpose:** Create session via REST

**Request:**
```json
{
    "command": "bash",
    "args": ["-l"],
    "cwd": "/home/user",
    "env": {}
}
```

**Response:**
```json
{
    "session_id": "abc-123-def-456",
    "url": "http://server:5000?session=abc-123-def-456"
}
```

### GET /api/sessions

**Purpose:** List active sessions

**Response:**
```json
{
    "sessions": [
        {
            "session_id": "abc-123",
            "command": "bash",
            "created_at": "2025-01-15T10:30:00Z",
            "uptime_seconds": 120
        }
    ]
}
```

### DELETE /api/sessions/{session_id}

**Purpose:** Close session via REST

**Response:**
```json
{
    "success": true,
    "exit_code": 0
}
```

## Implementation Requirements

### Minimum Requirements

✅ **MUST** implement SocketIO server on `/pty` namespace
✅ **MUST** handle `create_session` event
✅ **MUST** handle `pty-input` event
✅ **MUST** emit `pty-output` events
✅ **MUST** handle `resize` event
✅ **MUST** emit `session_closed` on process exit

### Recommended Requirements

⭐ **SHOULD** implement REST API for session management
⭐ **SHOULD** handle reconnections gracefully
⭐ **SHOULD** implement session timeouts
⭐ **SHOULD** validate session_id format
⭐ **SHOULD** limit active sessions per client

### Optional Features

💡 **MAY** implement authentication/authorization
💡 **MAY** implement session persistence
💡 **MAY** implement session recording
💡 **MAY** implement resource limits per session
💡 **MAY** implement session sharing (multiple clients)

## Message Routing

**Critical Rule:** Messages MUST be routed by `session_id`

```
Client A (session: abc-123)
    ↓ pty-input: {session_id: "abc-123", input: "ls"}
Server
    ↓ Route to PTY for session abc-123
PTY abc-123
    ↓ Output: "file1\nfile2\n"
Server
    ↓ pty-output: {session_id: "abc-123", output: "..."}
Client A
```

**Isolation:** Session abc-123 must NEVER receive output from session def-456.

## Error Handling

### Connection Errors

**Client disconnects:**
```javascript
// Server behavior
on('disconnect', (client_sid) => {
    // Keep session alive for 30 seconds
    setTimeout(() => {
        if (!client_reconnected) {
            close_session(session_id);
        }
    }, 30000);
});
```

### Session Errors

**Session not found:**
```json
{
    "error": "session_not_found",
    "session_id": "abc-123",
    "message": "Session does not exist or has been closed"
}
```

**Session limit reached:**
```json
{
    "error": "session_limit_reached",
    "limit": 20,
    "message": "Maximum number of concurrent sessions reached"
}
```

## Security Considerations

### Authentication

**Recommended:** Implement token-based auth

```javascript
// Client connects with token
const socket = io('/pty', {
    auth: {
        token: 'jwt-token-here'
    }
});

// Server validates
io.use((socket, next) => {
    const token = socket.handshake.auth.token;
    if (validate_token(token)) {
        next();
    } else {
        next(new Error('Authentication failed'));
    }
});
```

### Input Validation

✅ **MUST** validate all session_id parameters
✅ **MUST** validate command/args (whitelist allowed commands)
✅ **MUST** sanitize input to prevent command injection
✅ **SHOULD** implement rate limiting on input
✅ **SHOULD** limit session count per user

### Session Isolation

✅ **MUST** ensure sessions cannot access each other's data
✅ **MUST** ensure output routing is correct
✅ **SHOULD** implement resource limits per session

## Example Implementations

### Minimal Python Server

```python
from flask import Flask, request
from flask_socketio import SocketIO, emit
import pty
import os
import select
import threading

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

sessions = {}  # session_id -> {fd, pid}

@socketio.on('create_session', namespace='/pty')
def create_session(data):
    """Create new terminal session."""
    session_id = str(uuid.uuid4())
    command = data.get('command', 'bash')

    # Fork PTY
    pid, fd = pty.fork()
    if pid == 0:
        # Child: exec command
        os.execvp(command, [command])
    else:
        # Parent: store session
        sessions[session_id] = {'fd': fd, 'pid': pid}

        # Start output reader
        threading.Thread(
            target=read_output,
            args=(session_id, fd),
            daemon=True
        ).start()

        return {'session_id': session_id}

@socketio.on('pty-input', namespace='/pty')
def handle_input(data):
    """Handle input from client."""
    session_id = data['session_id']
    input_data = data['input']

    session = sessions.get(session_id)
    if session:
        os.write(session['fd'], input_data.encode())

@socketio.on('resize', namespace='/pty')
def handle_resize(data):
    """Handle terminal resize."""
    session_id = data['session_id']
    rows = data['rows']
    cols = data['cols']

    session = sessions.get(session_id)
    if session:
        fcntl.ioctl(session['fd'], termios.TIOCSWINSZ,
                   struct.pack('HHHH', rows, cols, 0, 0))

def read_output(session_id, fd):
    """Read PTY output and emit to client."""
    while session_id in sessions:
        r, _, _ = select.select([fd], [], [], 0.1)
        if r:
            try:
                output = os.read(fd, 1024).decode('utf-8')
                socketio.emit('pty-output', {
                    'session_id': session_id,
                    'output': output
                }, namespace='/pty')
            except OSError:
                break

    # Session ended
    socketio.emit('session_closed', {
        'session_id': session_id,
        'exit_code': 0
    }, namespace='/pty')
    del sessions[session_id]

if __name__ == '__main__':
    socketio.run(app, port=5000)
```

### Client Connection (JavaScript)

```javascript
// Connect to server
const socket = io('http://localhost:5000/pty');

// Request new session
socket.emit('create_session', {
    command: 'bash',
    args: ['-l'],
    cwd: '/home/user'
}, (response) => {
    const sessionId = response.session_id;

    // Setup terminal
    const term = new Terminal();
    term.open(document.getElementById('terminal'));

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

    // Handle session closed
    socket.on('session_closed', (data) => {
        if (data.session_id === sessionId) {
            term.write('\r\n[Process exited]\r\n');
        }
    });
});
```

## Testing Your Implementation

### Checklist

- [ ] Create session returns valid session_id
- [ ] Input reaches correct session
- [ ] Output from session A doesn't reach session B
- [ ] Resize updates PTY window size
- [ ] Session closes on process exit
- [ ] Multiple concurrent sessions work
- [ ] Client reconnection works
- [ ] Session cleanup on disconnect

### Test with TerminalWidget

```python
from vfwidgets_terminal import TerminalWidget

# Test your server
terminal = TerminalWidget(
    server_url="http://localhost:5000"
)
terminal.show()

# Should:
# 1. Connect to your server
# 2. Request session creation
# 3. Display terminal
# 4. Send/receive data correctly
```

## Reference Implementation

See `vfwidgets-terminal/src/vfwidgets_terminal/multi_session_server.py` for a production-ready reference implementation with:
- Session management
- Session persistence
- Resource limits
- Error handling
- Full REST API

You can use it as-is or customize for your needs.

## Protocol Versioning

**Current Version:** 1.0

**Version Negotiation:**
```json
// Client sends version in connect
{
    "protocol_version": "1.0"
}

// Server responds with supported version
{
    "protocol_version": "1.0",
    "server": "MyTerminalServer/1.0"
}
```

**Future Versions:**
- Version 1.1: May add optional features
- Version 2.0: May include breaking changes

## Support

**Questions about the protocol?**
- File issue: https://github.com/vilosource/vfwidgets/issues
- See examples: `vfwidgets-terminal/examples/custom_server.py`
- Reference implementation: `vfwidgets-terminal/src/vfwidgets_terminal/multi_session_server.py`

## License

This protocol specification is released under MIT License.
Implementations may use any license.
