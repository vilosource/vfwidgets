# Terminal Server Architecture

## Overview

This document explains how the TerminalWidget manages embedded servers and addresses the question: **"Does each terminal need its own server?"**

**Answer: YES - By design, each TerminalWidget creates its own embedded server instance.**

## Architecture

### Current Design

Each `TerminalWidget` instance creates and manages:
1. **EmbeddedTerminalServer** - Flask/SocketIO server
2. **Unique Port** - Auto-allocated by the OS
3. **PTY Process** - Pseudo-terminal running a shell
4. **WebView** - Qt WebEngine displaying xterm.js
5. **Server Thread** - Background thread running Flask

### Visual Architecture

```
ViloxTerm Application
│
├─ Tab 1: "Project"
│  └─ MultisplitWidget
│     ├─ Pane A: TerminalWidget #1
│     │  ├─ EmbeddedTerminalServer (port 5001, thread 1)
│     │  ├─ PTY (bash, pid 1234)
│     │  └─ WebView → http://localhost:5001
│     │
│     └─ Pane B: TerminalWidget #2
│        ├─ EmbeddedTerminalServer (port 5002, thread 2)
│        ├─ PTY (bash, pid 1235)
│        └─ WebView → http://localhost:5002
│
├─ Tab 2: "Development"
│  └─ MultisplitWidget
│     ├─ Pane C: TerminalWidget #3
│     │  ├─ EmbeddedTerminalServer (port 5003, thread 3)
│     │  ├─ PTY (python, pid 1236)
│     │  └─ WebView → http://localhost:5003
│     │
│     └─ Pane D: TerminalWidget #4
│        ├─ EmbeddedTerminalServer (port 5004, thread 4)
│        ├─ PTY (bash, pid 1237)
│        └─ WebView → http://localhost:5004
```

**Key Point:** Each terminal is completely self-contained with its own server instance, port, and PTY.

## Why Each Terminal Needs Its Own Server

### 1. Process Isolation

Each terminal runs its own PTY (pseudo-terminal) process:
- PTY is a system-level resource with its own file descriptor
- Each PTY runs exactly ONE shell/command
- PTYs cannot be shared between multiple terminal instances

```python
# From embedded_server.py:219
self.child_pid, self.fd = pty.fork()
# ↑ Creates ONE PTY for ONE process
```

### 2. Socket/WebSocket Connection Model

Flask-SocketIO servers are designed for 1:1 relationships:
- Each SocketIO server manages ONE PTY
- Each server binds to ONE port
- Each WebView connects to ONE server

**Attempting to share a server between terminals would require:**
- Complex session management
- PTY multiplexing
- Connection routing logic
- Significantly more complex architecture

### 3. Lifecycle Independence

Each terminal has its own lifecycle:
- Terminal created → Server starts → PTY spawns
- Terminal closed → PTY killed → Server stops
- Terminals can be created/destroyed independently

**Shared server problems:**
- How to handle partial shutdowns?
- What if one terminal crashes?
- How to manage per-terminal state?

### 4. Automatic Port Allocation

The OS handles port conflicts automatically:

```python
# From embedded_server.py:306-311
def _find_free_port(self) -> int:
    """Find a free port to use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))  # OS assigns next available port
        return s.getsockname()[1]
```

**Usage:**
```python
terminal = TerminalWidget(port=0)  # Auto-allocate
# Server automatically gets unique port (5001, 5002, etc.)
```

## Code Evidence

### TerminalWidget Creates Server

From `terminal.py:906-914`:
```python
# Start embedded server
logger.info("Starting embedded terminal server")
self.server = EmbeddedTerminalServer(
    command=self.command,
    args=self.args,
    cwd=self.cwd,
    env=self.env,
    port=self.port,  # ← Each terminal gets its own
    host=self.host,
    capture_output=self.capture_output,
)
```

### Port Auto-Allocation

From `embedded_server.py:332-334`:
```python
# Find port if needed
if self.port == 0:
    self.port = self._find_free_port()  # ← Unique port per server
```

### Server Lifecycle

From `embedded_server.py:329-351`:
```python
def start(self) -> int:
    """Start the terminal server."""
    if self.running:
        return self.port  # Already running

    # Find port if needed
    if self.port == 0:
        self.port = self._find_free_port()

    # Start server in thread
    def run_server():
        self.socketio.run(
            self.app,
            debug=False,
            port=self.port,      # ← Unique port
            host=self.host,
            allow_unsafe_werkzeug=True,
            use_reloader=False,  # ← No reloading (production mode)
        )

    self.server_thread = threading.Thread(target=run_server, daemon=True)
    self.server_thread.start()
```

## Resource Considerations

### Per-Terminal Overhead

Each terminal consumes:
- **Memory:** ~10-20 MB (Flask server + xterm.js + WebView)
- **Threads:** 1 server thread + Flask worker threads
- **Port:** 1 port (from ephemeral port range 49152-65535)
- **PTY:** 1 file descriptor + 1 shell process

### Realistic Limits

**Recommended Maximum:** 16-20 terminals per application

**Math:**
- 20 terminals × 15 MB = ~300 MB RAM
- 20 servers on ports 5001-5020
- ~20-40 threads total
- Well within system limits

**System Limits (typical Linux):**
- Max open files: 1024-4096 (ulimit -n)
- Max threads: 32000+ (varies by system)
- Ephemeral ports: 16384 ports available

### Resource Exhaustion Scenarios

**Problem:** Creating 100+ terminals could exhaust resources

**Mitigation:**
```python
class TerminalProvider(WidgetProvider):
    MAX_TERMINALS = 20  # Configurable limit

    def provide_widget(self, widget_id, pane_id):
        if len(self.terminals) >= self.MAX_TERMINALS:
            raise RuntimeError(
                f"Terminal limit reached ({self.MAX_TERMINALS}). "
                "Close some terminals before creating new ones."
            )

        terminal = TerminalWidget(port=0)
        self.terminals[pane_id] = terminal
        return terminal
```

## Best Practices

### 1. Always Use Port Auto-Allocation

```python
# ✅ CORRECT - Auto-allocate port
terminal = TerminalWidget(port=0)

# ❌ WRONG - Hardcoded port (will conflict!)
terminal = TerminalWidget(port=5000)
```

### 2. Implement Proper Cleanup

```python
class TerminalProvider(WidgetProvider):
    def cleanup_terminal(self, pane_id):
        """Clean up terminal when pane closes."""
        terminal = self.terminals.pop(pane_id, None)
        if terminal and hasattr(terminal, 'cleanup'):
            terminal.cleanup()  # Stops server, kills PTY, frees port
```

### 3. Track Terminal Count

```python
class ViloxTermApp:
    def update_status_bar(self):
        count = len(self.terminal_provider.terminals)
        self.status_bar.showMessage(f"Terminals: {count}/20")

        if count >= 18:  # Near limit
            self.status_bar.setStyleSheet("color: orange;")
```

### 4. Test Port Allocation

```python
def test_unique_ports():
    """Verify each terminal gets unique port."""
    terminals = [TerminalWidget(port=0) for _ in range(10)]

    # Extract ports
    ports = [t.server.port for t in terminals]

    # All must be unique
    assert len(ports) == len(set(ports)), "Port conflict detected!"

    # Cleanup
    for t in terminals:
        t.cleanup()
```

## Common Questions

### Q: Why not use a single server with session multiplexing?

**A:** Significantly more complex with minimal benefit.

**Single Server Approach:**
- Pros: Fewer threads, fewer ports
- Cons: Complex session routing, shared failure domain, harder to debug

**Multi-Server Approach (current):**
- Pros: Simple isolation, clean lifecycle, easy debugging, crash isolation
- Cons: More threads/ports (but well within limits)

**Verdict:** Multi-server is simpler and more robust.

### Q: Will 12 servers running simultaneously cause issues?

**A:** No, this is well within normal system limits.

**Evidence:**
- Web browsers run 100+ background processes
- IDEs run dozens of language servers
- Terminal multiplexers (tmux) run similar architecture
- 12 Flask servers ~= 200 MB RAM (acceptable)

### Q: What happens if port allocation fails?

**A:** `_find_free_port()` uses OS-level socket binding which automatically finds available ports. Failure only occurs if:
1. All 16384 ephemeral ports are exhausted (extremely rare)
2. System has severe resource constraints

**Handling:**
```python
try:
    terminal = TerminalWidget(port=0)
except OSError as e:
    logger.error(f"Failed to allocate port: {e}")
    show_error_dialog("Cannot create terminal: No ports available")
```

### Q: Can terminals share resources like themes or configuration?

**A:** Yes! Only the **server/PTY** must be separate.

**Shareable Resources:**
- Theme configuration (via theme system)
- Terminal settings (font, colors, etc.)
- Keyboard shortcuts
- Configuration state

**Must Be Separate:**
- Flask server instance
- Port number
- PTY file descriptor
- Shell process

## Debugging

### Check Active Servers

```bash
# List all Flask servers
netstat -an | grep LISTEN | grep 50

# Should see:
# tcp  0.0.0.0:5001  LISTEN  (Terminal 1)
# tcp  0.0.0.0:5002  LISTEN  (Terminal 2)
# tcp  0.0.0.0:5003  LISTEN  (Terminal 3)
```

### Monitor Resource Usage

```bash
# Check memory per terminal
ps aux | grep python | grep flask

# Check thread count
ps -eLf | grep viloxterm | wc -l
```

### Verify Port Uniqueness

```python
# In ViloxTerm debug mode
def debug_terminal_ports(self):
    ports = []
    for pane_id, terminal in self.terminal_provider.terminals.items():
        port = terminal.server.port if terminal.server else "N/A"
        ports.append((pane_id, port))
        print(f"Terminal {pane_id}: port {port}")

    # Check for duplicates
    port_values = [p for _, p in ports if p != "N/A"]
    if len(port_values) != len(set(port_values)):
        print("⚠️  WARNING: Duplicate ports detected!")
```

## Conclusion

**The current TerminalWidget architecture is correct by design:**

✅ Each terminal has its own server instance
✅ Port conflicts prevented by automatic allocation
✅ Clean isolation and lifecycle management
✅ Resource usage well within acceptable limits
✅ No changes needed to the current design

**For ViloxTerm implementation:**
- Use `port=0` for all terminals (auto-allocate)
- Implement proper cleanup on terminal close
- Track terminal count for user feedback
- Document the 16-20 terminal recommendation

## References

- **TerminalWidget Source:** `widgets/terminal_widget/src/vfwidgets_terminal/terminal.py`
- **EmbeddedServer Source:** `widgets/terminal_widget/src/vfwidgets_terminal/embedded_server.py`
- **Theme Integration:** `widgets/terminal_widget/docs/theme-integration-lessons-GUIDE.md`
