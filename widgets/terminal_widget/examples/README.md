# Terminal Widget Examples

This directory contains examples showing different usage modes of the VFWidgets Terminal.

## Quick Start

### Example 1: Simple Terminal (Embedded Mode)

The simplest way to use TerminalWidget - it creates its own server automatically.

```bash
python 01_simple_terminal.py
```

**Use this when:**
- You have 1-5 terminals
- You want the simplest API
- Memory usage isn't a concern

**Code:**
```python
from vfwidgets_terminal import TerminalWidget

terminal = TerminalWidget()  # Auto-creates embedded server
```

### Example 2: Multi-Terminal App (Shared Server)

Multiple terminals sharing a single server. **Recommended for applications with many terminals.**

```bash
python 02_multi_terminal_app.py
```

**Use this when:**
- You have 5+ terminals
- Memory efficiency matters (63% reduction)
- You want centralized session management

**Benefits:**
- 20 terminals: 300MB → 110MB (63% less memory)
- Scalable architecture
- Clean session management

**Code:**
```python
from vfwidgets_terminal import MultiSessionTerminalServer, TerminalWidget

# Create shared server
server = MultiSessionTerminalServer(port=5000)
server.start()

# Create sessions and connect terminals to them
session_id1 = server.create_session(command="bash")
terminal1 = TerminalWidget(server_url=server.get_session_url(session_id1))

session_id2 = server.create_session(command="bash")
terminal2 = TerminalWidget(server_url=server.get_session_url(session_id2))

# ... 20 terminals sharing one server!
```

### Example 3: Custom Server

Implement your own terminal server using the protocol.

**Terminal Run the server:**
```bash
python 03_custom_server.py
```

Then in another terminal, create widgets that connect to it:
```python
from vfwidgets_terminal import TerminalWidget

terminal = TerminalWidget(server_url="http://localhost:5001")
```

**Use this when:**
- You need custom authentication
- You want remote terminal servers
- You're integrating with existing infrastructure
- You need special logging/monitoring

## Usage Modes Comparison

| Mode | Terminals | Memory (20) | Use Case |
|------|-----------|-------------|----------|
| **Embedded** | 1-5 | ~300MB | Simple apps, few terminals |
| **Shared Server** | 5-20+ | ~110MB | Multi-terminal apps (ViloxTerm) |
| **Custom** | Any | Varies | Enterprise, remote, custom needs |

## Example Features

### 01_simple_terminal.py
- Single terminal window
- Embedded server (automatic)
- Minimal code (~30 lines)

### 02_multi_terminal_app.py
- Tabbed interface
- Dynamic terminal creation
- Shared server architecture
- Memory efficient
- Session management

### 03_custom_server.py
- Minimal protocol implementation (~150 lines)
- Shows required SocketIO events
- Platform-agnostic backend
- Room-based message routing

## Protocol Requirements

If implementing a custom server, you must handle:

**SocketIO Namespace:** `/pty`

**Required Events:**
- `create_session` - Create new session
- `connect` - Join session room
- `pty-input` - Handle user input
- `pty-output` - Send terminal output
- `resize` - Handle terminal resize

**Optional but Recommended:**
- `heartbeat` - Keep session alive
- `session_closed` - Notify session end

See `03_custom_server.py` for minimal implementation.

## For ViloxTerm

Use Example 2 (Multi-Terminal App) as reference:

```python
from vfwidgets_terminal import MultiSessionTerminalServer, TerminalWidget

class ViloxTermApp:
    def __init__(self):
        # Create shared server
        self.terminal_server = MultiSessionTerminalServer(port=5000)
        self.terminal_server.start()

    def create_terminal_widget(self):
        # Create session on server
        session_id = self.terminal_server.create_session(command="bash")

        # Connect terminal to session
        return TerminalWidget(
            server_url=self.terminal_server.get_session_url(session_id)
        )
```

## Testing

To test the examples:

```bash
# Test simple terminal
python 01_simple_terminal.py

# Test multi-terminal (creates 5 terminals, click + for more)
python 02_multi_terminal_app.py

# Test custom server (run in separate terminals)
# Terminal 1:
python 03_custom_server.py

# Terminal 2:
python -c "from vfwidgets_terminal import TerminalWidget; from PySide6.QtWidgets import QApplication; import sys; app = QApplication(sys.argv); t = TerminalWidget(server_url='http://localhost:5001'); t.show(); sys.exit(app.exec())"
```

## Documentation

- **Implementation Plan:** `../docs/multi-session-server-IMPLEMENTATION.md`
- **Protocol Spec:** `/apps/viloxterm/docs/terminal-server-protocol-SPEC.md`
- **Architecture:** `/apps/viloxterm/docs/`

## Common Mistakes to Avoid

### ❌ Wrong: Creating Widget Before Session

```python
server = MultiSessionTerminalServer()
server.start()
terminal = TerminalWidget(server_url="http://localhost:5000")  # 404 Error!
```

### ✅ Correct: Create Session First

```python
server = MultiSessionTerminalServer()
server.start()

# 1. Create session
session_id = server.create_session()

# 2. Get session URL
url = server.get_session_url(session_id)

# 3. Connect widget
terminal = TerminalWidget(server_url=url)
```

### ❌ Wrong: Hardcoded Ports

```python
server = MultiSessionTerminalServer(port=5000)  # May conflict
```

### ✅ Correct: Auto-Allocated Ports

```python
server = MultiSessionTerminalServer(port=0)  # OS chooses available port
```

### ❌ Wrong: Reusing Session IDs

```python
session_id = server.create_session()
terminal1 = TerminalWidget(server_url=server.get_session_url(session_id))
terminal2 = TerminalWidget(server_url=server.get_session_url(session_id))  # Conflict!
```

### ✅ Correct: Unique Session Per Terminal

```python
session_id1 = server.create_session()
session_id2 = server.create_session()
terminal1 = TerminalWidget(server_url=server.get_session_url(session_id1))
terminal2 = TerminalWidget(server_url=server.get_session_url(session_id2))
```

## Troubleshooting

**Terminal doesn't connect:**
- Check server is running and port is correct
- Verify firewall isn't blocking localhost connections
- Check console for SocketIO connection errors
- **Most common:** Session wasn't created before widget connection

**Session not found (404 Error):**
- ✅ **Solution:** Always create session BEFORE connecting widget
- Ensure server is started before creating sessions
- Verify session_id in URL matches created session
- Check server logs for "Session not found" errors

**Multiple terminals show same session:**
- Each terminal needs unique session
- Don't reuse session_ids
- Call `server.create_session()` for each terminal

**White flash on startup:**
- This has been fixed in v2.0 by setting QWebEngineView background color
- If you see white flash, ensure you're using latest version

## Contributing

When adding examples, follow this pattern:
1. Numbered filename: `04_feature_name.py`
2. Docstring explaining the example
3. Clear use case
4. ~50-200 lines (keep it focused)
5. Update this README
