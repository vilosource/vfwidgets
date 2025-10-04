# Previous ViloxTerm Implementation Analysis

## Overview

This document analyzes the terminal server implementation from the previous ViloxTerm project (`/home/kuja/GitHub/vfwidgets/tmp/viloxterm`) and compares it with the proposed architecture for the new vfwidgets terminal system.

**Key Finding:** The previous implementation already solved the multi-session server problem using a singleton `TerminalServerManager` that handles multiple terminal sessions through a single Flask/SocketIO server.

## Architecture Comparison

### Previous Implementation (tmp/viloxterm)

**Components:**
1. **`TerminalServerManager`** - Singleton server managing multiple sessions
2. **`TerminalBackend`** - Abstract backend interface (Unix/Windows)
3. **`TerminalSession`** - Session data class
4. **`TerminalWidget`** - Qt widget that creates sessions via the singleton server

**Key Pattern:**
```python
# Singleton server instance
terminal_server = TerminalServerManager()

# Widget creates session through shared server
class TerminalWidget(QWidget):
    def start_terminal(self, command=None, cwd=None):
        # Create session via singleton
        self.session_id = terminal_server.create_session(command=command, cwd=cwd)

        # Get URL for this session
        url = terminal_server.get_terminal_url(self.session_id)

        # Load in WebView
        self.web_view.load(QUrl(url))
```

### Proposed Architecture (New Design)

**Components:**
1. **`MultiSessionTerminalServer`** - Standalone server managing sessions
2. **`TerminalWidget`** - Protocol client that can connect to any server
3. **Protocol Specification** - Language-agnostic SocketIO protocol

**Key Pattern:**
```python
# Option 1: Shared server (like previous implementation)
server = MultiSessionTerminalServer(port=5000)
server.start()
terminal = TerminalWidget(server_url="http://localhost:5000")

# Option 2: Embedded server (backwards compatibility)
terminal = TerminalWidget()  # Creates own server

# Option 3: Custom server
terminal = TerminalWidget(server_url="http://custom-server:5000")
```

## Architecture Diagrams

### Previous Implementation

```
┌─────────────────────────────────────────────┐
│  TerminalServerManager (Singleton)          │
│  Port: 5000 (auto-allocated)                │
│                                             │
│  sessions = {                               │
│    "abc123": TerminalSession(...)          │
│    "def456": TerminalSession(...)          │
│    "ghi789": TerminalSession(...)          │
│  }                                          │
│                                             │
│  Flask Routes:                              │
│  • /terminal/<session_id>                   │
│                                             │
│  SocketIO Handlers (/terminal):             │
│  • connect    (join room = session_id)      │
│  • pty-input  (route by session_id)         │
│  • pty-output (emit to room = session_id)   │
│  • resize     (route by session_id)         │
│  • disconnect (leave room)                  │
│  • heartbeat  (keep session alive)          │
└─────────────────────────────────────────────┘
              ▲
              │ WebView connects to:
              │ http://localhost:5000/terminal/<session_id>
              │
┌─────────────┴─────────────┬─────────────────┬────────────────┐
│                           │                 │                │
│  TerminalWidget #1        │ TerminalWidget  │ TerminalWidget │
│  session_id: abc123       │ session_id:     │ session_id:    │
│  QWebEngineView           │ def456          │ ghi789         │
│                           │ QWebEngineView  │ QWebEngineView │
└───────────────────────────┴─────────────────┴────────────────┘
```

### Proposed Architecture (Shared Server Mode)

```
┌─────────────────────────────────────────────┐
│  MultiSessionTerminalServer                 │
│  Port: 5000                                 │
│                                             │
│  sessions = {                               │
│    "abc123": TerminalSession(...)          │
│    "def456": TerminalSession(...)          │
│  }                                          │
│                                             │
│  SocketIO Namespace: /pty                   │
│  • create_session                           │
│  • pty-input                                │
│  • pty-output                               │
│  • resize                                   │
│  • session_closed                           │
└─────────────────────────────────────────────┘
              ▲
              │ SocketIO connection
              │
┌─────────────┴─────────────┬─────────────────┐
│                           │                 │
│  TerminalWidget #1        │ TerminalWidget  │
│  server_url: localhost    │ server_url:     │
│  session_id: abc123       │ localhost       │
│  QWebEngineView           │ session_id:     │
│                           │ def456          │
└───────────────────────────┴─────────────────┘
```

## Key Implementation Details

### 1. Backend Abstraction Layer

**Previous Implementation:** ✅ **Excellent design**

```python
# backends/base.py
class TerminalBackend(ABC):
    """Platform-agnostic interface for terminal operations."""

    def __init__(self):
        self.sessions: dict[str, TerminalSession] = {}

    @abstractmethod
    def start_process(self, session: TerminalSession) -> bool: pass

    @abstractmethod
    def read_output(self, session: TerminalSession, max_bytes=1024*20) -> str: pass

    @abstractmethod
    def write_input(self, session: TerminalSession, data: str) -> bool: pass

    @abstractmethod
    def resize(self, session: TerminalSession, rows: int, cols: int) -> bool: pass

    @abstractmethod
    def is_process_alive(self, session: TerminalSession) -> bool: pass

    @abstractmethod
    def terminate_process(self, session: TerminalSession) -> bool: pass
```

**Benefits:**
- Clean separation between server logic and PTY management
- Cross-platform support (Unix/Windows) via factory pattern
- Backend is shared across all sessions (singleton pattern)
- Easy to test and mock

**Recommendation:** Adopt this exact pattern for new implementation

### 2. Session Management

**Previous Implementation:**

```python
@dataclass
class TerminalSession:
    session_id: str
    fd: Optional[int] = None              # PTY file descriptor
    child_pid: Optional[int] = None       # Process PID
    command: str = "bash"
    cmd_args: list = field(default_factory=list)
    cwd: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    rows: int = 24
    cols: int = 80
    active: bool = True
    platform_data: dict = field(default_factory=dict)
```

**Proposed Specification:**

```python
@dataclass
class TerminalSession:
    session_id: str
    command: str = "bash"
    args: List[str] = field(default_factory=list)
    cwd: Optional[str] = None
    env: Dict[str, str] = field(default_factory=dict)
    rows: int = 24
    cols: int = 80
    fd: Optional[int] = None
    child_pid: Optional[int] = None
    running: bool = False
```

**Comparison:**
- ✅ Both track session_id, command, cwd, rows, cols, fd, child_pid
- ✅ Previous has `last_activity` for timeout tracking (excellent feature)
- ✅ Previous has `created_at` for session age tracking
- ✅ Previous has `platform_data` for extensibility
- ⚠️ Proposed has `env` for environment variables (missing in previous)

**Recommendation:** Merge both - use previous as base, add `env` support

### 3. Server Lifecycle and Singleton Pattern

**Previous Implementation:**

```python
class TerminalServerManager(QObject):
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
```

**Benefits:**
- Thread-safe singleton creation
- Application-wide shared server instance
- Automatic lifecycle management (atexit, signal handlers)

**Trade-offs:**
- Hard to use multiple independent servers
- Testing requires factory reset
- Couples widget to specific server implementation

**Recommendation:** Keep singleton for ViloxTerm app, but make it optional:

```python
# ViloxTerm app: Use singleton
terminal_server = TerminalServerManager.get_instance()
widget = TerminalWidget(server=terminal_server)

# Standalone widget: Create own server
widget = TerminalWidget()  # Auto-creates server

# Custom integration: Provide URL
widget = TerminalWidget(server_url="http://localhost:5000")
```

### 4. SocketIO Protocol Details

#### Previous Implementation

**Namespace:** `/terminal`

**URL Pattern:** `/terminal/<session_id>`

**Connection:**
```python
@self.socketio.on("connect", namespace="/terminal")
def handle_connect(auth=None):
    session_id = request.args.get("session_id")
    if session_id not in self.sessions:
        return False
    join_room(session_id)
```

**Message Routing:**
```python
# Input from client
@self.socketio.on("pty-input", namespace="/terminal")
def handle_pty_input(data):
    session_id = data.get("session_id")
    session = self.sessions[session_id]
    self.backend.write_input(session, data["input"])

# Output to client (emitted to room)
self.socketio.emit(
    "pty-output",
    {"output": output, "session_id": session_id},
    namespace="/terminal",
    room=session_id  # ← Only clients in this room receive
)
```

**Key Features:**
- ✅ Uses SocketIO rooms for message isolation
- ✅ Each session has its own room = session_id
- ✅ Heartbeat mechanism to keep sessions alive
- ✅ Auto-cleanup of inactive sessions (60min timeout)
- ✅ Background task for reading PTY output

#### Proposed Specification

**Namespace:** `/pty`

**Connection:**
```javascript
const socket = io('http://localhost:5000/pty');
socket.emit('create_session', {command: 'bash'}, (response) => {
    const session_id = response.session_id;
});
```

**Comparison:**
- ⚠️ Different namespace: `/terminal` (previous) vs `/pty` (proposed)
- ⚠️ Different URL pattern: previous uses Flask route + query param, proposed uses SocketIO only
- ✅ Both use session_id for message routing
- ✅ Both support resize, input/output events

**Recommendation:** Use `/pty` namespace (clearer intent), adopt room-based routing from previous implementation

### 5. Session Creation

#### Previous Implementation

```python
def create_session(self, command="bash", cmd_args="", cwd=None) -> str:
    if len(self.sessions) >= self.max_sessions:
        raise RuntimeError(f"Maximum sessions ({self.max_sessions}) reached")

    session_id = str(uuid.uuid4())[:8]  # Short UUID (8 chars)
    args_list = shlex.split(cmd_args) if cmd_args else []

    session = TerminalSession(
        session_id=session_id,
        command=command,
        cmd_args=args_list,
        cwd=cwd
    )

    self.sessions[session_id] = session

    # Start server if not running
    if not self.running:
        self.start_server()

    return session_id
```

**Features:**
- ✅ Session limit enforcement (20 max)
- ✅ Lazy server startup (only starts when first session created)
- ✅ Short session IDs (8 characters instead of full UUID)
- ✅ Shell argument parsing with `shlex`

**Widget Integration:**
```python
def start_terminal(self, command=None, cwd=None):
    # Create session
    self.session_id = terminal_server.create_session(command=command, cwd=cwd)

    # Get URL
    url = terminal_server.get_terminal_url(self.session_id)

    # Load in WebView
    self.web_view.load(QUrl(url))
```

#### Proposed Specification

```python
# Via SocketIO
@socketio.on('create_session', namespace='/pty')
def create_session(data):
    session_id = str(uuid.uuid4())
    session = TerminalSession(
        session_id=session_id,
        command=data.get('command', 'bash'),
        args=data.get('args', []),
        cwd=data.get('cwd'),
        env=data.get('env', {})
    )
    self.sessions[session_id] = session
    self._spawn_pty(session)
    return {'session_id': session_id}
```

**Comparison:**
- ✅ Previous uses Python method call, proposed uses SocketIO event (more flexible)
- ✅ Previous has session limit enforcement (missing in proposed spec)
- ✅ Previous uses short UUIDs (better UX)
- ⚠️ Proposed supports environment variables (missing in previous)

**Recommendation:**
- Use SocketIO for session creation (protocol-based)
- Add session limit enforcement
- Use short UUIDs (8 chars)
- Add environment variable support

### 6. Output Reading Strategy

**Previous Implementation:**

```python
def _read_and_forward_pty_output(self, session_id: str):
    """Background task reading PTY output."""
    session = self.sessions.get(session_id)

    while self.running and session and session.active:
        # Poll backend
        if self.backend.poll_process(session, timeout=0.01):
            output = self.backend.read_output(session)
            if output:
                # Emit to room (only clients in session's room)
                self.socketio.emit(
                    "pty-output",
                    {"output": output, "session_id": session_id},
                    namespace="/terminal",
                    room=session_id
                )

        # Check if alive
        if not self.backend.is_process_alive(session):
            session.active = False
            self.session_ended.emit(session_id)
            break

        self.socketio.sleep(0.01)
```

**Key Features:**
- ✅ One background task per session
- ✅ Uses SocketIO's `start_background_task()` (thread-safe)
- ✅ 10ms polling interval (responsive)
- ✅ Room-based emission (automatic message isolation)
- ✅ Process liveness check
- ✅ Qt signal on session end (`session_ended.emit()`)

**Backend Implementation (Unix):**

```python
def poll_process(self, session: TerminalSession, timeout=0.01) -> bool:
    """Check if data is available without blocking."""
    data_ready, _, _ = select.select([session.fd], [], [], timeout)
    return bool(data_ready)

def read_output(self, session: TerminalSession, max_bytes=1024*20) -> str:
    """Read available output."""
    output = os.read(session.fd, max_bytes).decode(errors="ignore")
    session.last_activity = time.time()
    return output
```

**Recommendation:** Adopt this exact pattern - it's production-proven and efficient

### 7. Session Cleanup

**Previous Implementation:**

```python
def cleanup_inactive_sessions(self, timeout_minutes=30):
    """Clean up inactive sessions."""
    current_time = time.time()
    timeout_seconds = timeout_minutes * 60

    sessions_to_remove = []
    for session_id, session in self.sessions.items():
        # Inactive timeout
        if current_time - session.last_activity > timeout_seconds:
            sessions_to_remove.append(session_id)
        # Dead process
        elif self.backend and not self.backend.is_process_alive(session):
            sessions_to_remove.append(session_id)
        # Marked inactive
        elif not session.active:
            sessions_to_remove.append(session_id)

    for session_id in sessions_to_remove:
        self.destroy_session(session_id)

def _start_cleanup_timer(self):
    """Periodic cleanup (every 60 seconds)."""
    def cleanup_task():
        while self.running:
            time.sleep(60)
            try:
                self.cleanup_inactive_sessions(timeout_minutes=60)
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")

    cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
    cleanup_thread.start()
```

**Features:**
- ✅ Three cleanup triggers: timeout, dead process, manual inactive flag
- ✅ Configurable timeout (default 60 minutes)
- ✅ Automatic periodic cleanup (every 60 seconds)
- ✅ Daemon thread (won't block app shutdown)

**Recommendation:** Essential feature - must include in new implementation

### 8. Heartbeat Mechanism

**Previous Implementation:**

```python
@self.socketio.on("heartbeat", namespace="/terminal")
def handle_heartbeat(data):
    """Handle heartbeat from client to keep session alive."""
    session_id = data.get("session_id")
    if session_id and session_id in self.sessions:
        self.sessions[session_id].last_activity = time.time()
```

**Client Side (JavaScript):**
```javascript
// Send heartbeat every 30 seconds
setInterval(() => {
    socket.emit('heartbeat', {session_id: sessionId});
}, 30000);
```

**Benefits:**
- Prevents session timeout for active terminals
- Distinguishes between "client connected" and "user actively using"
- Simple and lightweight

**Recommendation:** Add to protocol specification as optional but recommended

## Key Differences Summary

| Feature | Previous (tmp/viloxterm) | Proposed (New) | Recommendation |
|---------|--------------------------|----------------|----------------|
| **Architecture** | Singleton server | Pluggable server | Hybrid: Singleton for apps, pluggable for widget |
| **Backend Abstraction** | ✅ Yes (Unix/Windows) | ❌ Not specified | Adopt from previous |
| **Namespace** | `/terminal` | `/pty` | Use `/pty` (clearer) |
| **Session ID** | 8-char UUID | Full UUID | Use 8-char (better UX) |
| **Session Limit** | ✅ 20 max | ❌ Not specified | Add to spec |
| **Cleanup Strategy** | ✅ Timeout + dead process | ❌ Not specified | Adopt from previous |
| **Heartbeat** | ✅ Yes | ❌ Not in spec | Add to spec |
| **Room-based Routing** | ✅ Yes | ❌ Not in spec | Add to spec |
| **Environment Variables** | ❌ No | ✅ Yes | Add to previous |
| **Qt Integration** | ✅ QObject + signals | ❌ Not specified | Keep for apps |
| **Widget Factory** | ✅ IWidget interface | ❌ Not specified | ViloxTerm-specific |

## Implementation Recommendations

### Phase 1: Port Proven Components

**Priority 1 (Core):**
1. ✅ **Backend Abstraction** - Copy `backends/` directory entirely
   - `base.py`, `unix_backend.py`, `windows_backend.py`, `factory.py`
   - This is production-tested and cross-platform

2. ✅ **Session Model** - Enhance `TerminalSession` dataclass
   ```python
   from tmp/viloxterm: last_activity, created_at, platform_data
   Add: env (environment variables)
   ```

3. ✅ **Room-based Routing** - Use SocketIO rooms for message isolation
   ```python
   join_room(session_id)  # On connect
   emit("pty-output", {...}, room=session_id)  # Automatic isolation
   ```

**Priority 2 (Production Features):**
4. ✅ **Session Cleanup** - Port entire cleanup system
   - Inactive session timeout
   - Dead process detection
   - Periodic cleanup task

5. ✅ **Heartbeat** - Add to protocol spec
   ```
   Client → Server: heartbeat {session_id}
   Updates session.last_activity timestamp
   ```

6. ✅ **Session Limits** - Enforce max sessions per server
   ```python
   MAX_SESSIONS = 20  # Configurable
   if len(sessions) >= MAX_SESSIONS:
       raise RuntimeError("Session limit reached")
   ```

**Priority 3 (Developer Experience):**
7. ✅ **Short Session IDs** - Use 8-char UUIDs
   ```python
   session_id = str(uuid.uuid4())[:8]
   ```

8. ✅ **Lazy Server Start** - Only start when first session created
   ```python
   if not self.running:
       self.start_server()
   ```

### Phase 2: Enhance for Widget Use

**Add Protocol-Based Design:**

```python
class MultiSessionTerminalServer:
    """
    Standalone server (not singleton).
    Can be used independently or as reference implementation.
    """
    def __init__(self, port=5000, host="127.0.0.1"):
        self.port = port
        self.host = host
        # Copy server logic from TerminalServerManager
```

**Add Optional Singleton:**

```python
class TerminalServerManager(MultiSessionTerminalServer):
    """
    Singleton wrapper for application use.
    ViloxTerm uses this; widget library provides MultiSessionTerminalServer.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        # Singleton pattern from previous
        pass
```

**Widget Flexibility:**

```python
class TerminalWidget(QWidget):
    def __init__(self, server=None, server_url=None):
        if server:
            # Use provided server instance
            self.server = server
        elif server_url:
            # Connect to external server
            self.server_url = server_url
        else:
            # Create embedded server (backwards compatible)
            self.server = EmbeddedTerminalServer()
```

### Phase 3: Update Protocol Spec

**Add to `terminal-server-protocol-SPEC.md`:**

1. **Heartbeat Event:**
   ```json
   // Client → Server (every 30 seconds)
   emit('heartbeat', {session_id: "abc123"})

   // Server updates: session.last_activity = time.time()
   ```

2. **Room-based Routing:**
   ```
   On connect: join_room(session_id)
   On emit: emit("pty-output", {...}, room=session_id)
   On disconnect: leave_room(session_id)
   ```

3. **Session Limits:**
   ```json
   // Error response if limit reached
   {
       "error": "session_limit_reached",
       "limit": 20,
       "message": "Maximum concurrent sessions reached"
   }
   ```

4. **Session Cleanup Events:**
   ```json
   // Server → Client
   emit('session_cleanup_warning', {
       session_id: "abc123",
       reason: "inactivity",
       seconds_remaining: 300
   })
   ```

## Migration Path for ViloxTerm

### Current State (tmp/viloxterm)
```
ViloxTerm App
├─ Uses: viloxterm.TerminalServerManager (singleton)
├─ Widget: viloxterm.TerminalWidget
├─ Backend: viloxterm.backends (Unix/Windows)
└─ Protocol: Custom (Flask routes + SocketIO)
```

### Target State (New Architecture)
```
ViloxTerm App
├─ Uses: vfwidgets_terminal.MultiSessionTerminalServer
├─ Widget: vfwidgets_terminal.TerminalWidget
├─ Backend: vfwidgets_terminal.backends (ported from previous)
└─ Protocol: Standardized (/pty namespace)
```

### Migration Steps

**Step 1: Extract Backend**
```bash
# Copy backend abstraction to widget package
cp -r tmp/viloxterm/packages/viloxterm/src/viloxterm/backends \
      widgets/terminal_widget/src/vfwidgets_terminal/backends
```

**Step 2: Create MultiSessionTerminalServer**
```python
# Based on previous TerminalServerManager but without singleton
# File: widgets/terminal_widget/src/vfwidgets_terminal/multi_session_server.py

class MultiSessionTerminalServer(QObject):
    def __init__(self, port=0, host="127.0.0.1"):
        # Copy implementation from TerminalServerManager
        # Remove singleton pattern
        # Add protocol compliance (/pty namespace)
```

**Step 3: Update TerminalWidget**
```python
# Add server parameter for flexibility
class TerminalWidget(QWidget):
    def __init__(self, server=None, server_url=None, port=0):
        if server_url:
            self.use_external_server(server_url)
        elif server:
            self.use_shared_server(server)
        else:
            self.use_embedded_server(port)
```

**Step 4: ViloxTerm Integration**
```python
# apps/viloxterm/main.py
from vfwidgets_terminal import MultiSessionTerminalServer, TerminalWidget

class ViloxTermApp:
    def __init__(self):
        # Single shared server for all terminals
        self.terminal_server = MultiSessionTerminalServer(port=5000)
        self.terminal_server.start()

    def create_terminal(self):
        # All terminals share the server
        return TerminalWidget(server=self.terminal_server)
```

## Code Reuse Checklist

From `tmp/viloxterm` → New Implementation:

- [ ] `backends/base.py` - TerminalBackend abstract class
- [ ] `backends/unix_backend.py` - Unix PTY implementation
- [ ] `backends/windows_backend.py` - Windows ConPTY implementation
- [ ] `backends/factory.py` - Backend factory with singleton pattern
- [ ] Session cleanup logic from `server.py:317-336`
- [ ] Heartbeat handling from `server.py:99-105`
- [ ] Background task pattern from `server.py:160-194`
- [ ] Room-based routing from `server.py:84-113`
- [ ] Session limit enforcement from `server.py:200-201`
- [ ] Process liveness checking from `unix_backend.py:113-126`
- [ ] Graceful shutdown from `server.py:279-309`
- [ ] Short UUID generation from `server.py:203`

## Testing Strategy

**From Previous Implementation:**

✅ **What was tested:**
- Cross-platform support (Unix/Windows)
- Multiple concurrent sessions (20+)
- Session isolation (output routing)
- Process lifecycle management
- WebView integration
- Plugin system integration

**What to add for new implementation:**
- Protocol compliance testing
- Custom server integration
- Embedded vs shared server modes
- Session persistence (optional feature)
- REST API (optional feature)

## Conclusion

**Key Insight:** The previous ViloxTerm implementation (`tmp/viloxterm`) already solved the multi-session terminal server problem excellently. The new implementation in `vfwidgets-terminal` will create a clean, reusable version:

1. **Learned from Reference:**
   - Backend abstraction layer design
   - Session cleanup mechanisms
   - Room-based message routing
   - Heartbeat system
   - Background task pattern

2. **Implement Clean Version:**
   - New implementation in `vfwidgets_terminal` package (not copied from tmp/viloxterm)
   - Standardized `/pty` namespace
   - Non-singleton by default (flexible architecture)
   - Protocol-based design
   - Well-documented examples

3. **Developer Experience:**
   - Clear protocol specification
   - Three usage modes (embedded/shared/custom)
   - Comprehensive documentation
   - Reference examples

**Implementation Plan:**

See: `widgets/terminal_widget/docs/multi-session-server-IMPLEMENTATION.md`

**Note:** The tmp/viloxterm code served as reference only. We're creating our own clean implementation in the terminal widget package that ViloxTerm (and other apps) will use as a library.

## References

**Previous Implementation:**
- Source: `/home/kuja/GitHub/vfwidgets/tmp/viloxterm/packages/viloxterm/src/viloxterm/`
- Backend: `backends/base.py`, `unix_backend.py`, `windows_backend.py`
- Server: `server.py` (TerminalServerManager)
- Widget: `widget.py` (TerminalWidget)

**New Architecture Docs:**
- Protocol: `terminal-server-protocol-SPEC.md`
- Design: `shared-server-refactoring-DESIGN.md`
- Current: `terminal-server-architecture-ARCHITECTURE.md`
