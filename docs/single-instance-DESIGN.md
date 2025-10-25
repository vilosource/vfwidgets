# SingleInstanceApplication - Design Document

## Overview

`SingleInstanceApplication` is a reusable component in `vfwidgets_common` that provides single-instance application behavior using Qt's IPC mechanisms (`QLocalServer`/`QLocalSocket`).

## Problem Statement

Many GUI applications should only run one instance at a time. When a user tries to launch a second instance, the preferred behavior is:
1. Detect that an instance is already running
2. Pass the command/data to the running instance
3. Exit the second instance immediately
4. Activate/focus the running instance window

**Use Cases**:
- Document viewers (reamde): Open new files in existing window tabs
- Terminal emulators (ViloxTerm): Create new terminal in existing window
- IDE applications: Focus existing window instead of opening duplicate

## Architecture

### Component Design

```
┌─────────────────────────────────────────────────┐
│        SingleInstanceApplication                │
│             (QApplication)                      │
├─────────────────────────────────────────────────┤
│ + __init__(argv, app_id)                        │
│ + is_primary_instance() -> bool                 │
│ + run() -> int                                  │
│ + handle_message(message: dict) [abstract]      │
│ + send_to_running_instance(message: dict)       │
│ + bring_to_front()                              │
├─────────────────────────────────────────────────┤
│ - _local_server: QLocalServer                   │
│ - _is_primary: bool                             │
│ - _app_id: str                                  │
│ - _create_local_server() -> bool                │
│ - _connect_to_existing(message: dict) -> bool   │
│ - _on_new_connection()                          │
└─────────────────────────────────────────────────┘
```

### IPC Protocol

**Transport**: QLocalSocket over named socket/pipe
**Format**: JSON messages
**Platform paths**:
- Linux/macOS: `/tmp/vfwidgets-{app_id}-{user}`
- Windows: `\\.\pipe\vfwidgets-{app_id}-{user}`

**Message Structure**:
```json
{
    "action": "string",
    "data": {}
}
```

**Standard Actions**:
- `"open"` - Open file/resource
- `"focus"` - Bring window to front
- `"custom"` - Application-specific action

### Lifecycle

#### Primary Instance (First Launch)
```
1. Create QApplication
2. Try to create QLocalServer with app_id
   ├─ Success → _is_primary = True
   │   ├─ Connect to newConnection signal
   │   └─ Start event loop
   └─ Failure (server exists) → _is_primary = False
       └─ Go to Secondary Instance flow
```

#### Secondary Instance (Subsequent Launch)
```
1. Create QApplication
2. Try to create QLocalServer (fails)
3. Connect to existing server via QLocalSocket
4. Send message with command-line args/data
5. Wait for acknowledgment (timeout: 5s)
6. Exit with code 0
```

#### Message Handling (Primary Instance)
```
1. QLocalServer receives new connection
2. Read data from socket until complete
3. Parse JSON message
4. Call handle_message() with parsed dict
5. Subclass processes message
6. Send acknowledgment back to sender
```

## API Design

### Basic Usage

```python
from vfwidgets_common import SingleInstanceApplication

class MyApp(SingleInstanceApplication):
    def __init__(self, argv):
        super().__init__(argv, app_id="myapp")
        self.main_window = None

    def handle_message(self, message: dict):
        """Handle messages from other instances."""
        action = message.get("action")

        if action == "open":
            file_path = message.get("file")
            self.main_window.open_file(file_path)
            self.bring_to_front()

        elif action == "focus":
            self.bring_to_front()

    def run(self, initial_file=None):
        """Run the application."""
        if not self.is_primary_instance():
            # Secondary instance - send message and exit
            message = {
                "action": "open",
                "file": initial_file
            }
            return self.send_to_running_instance(message)

        # Primary instance - create window and run
        self.main_window = MyMainWindow()
        if initial_file:
            self.main_window.open_file(initial_file)
        self.main_window.show()

        return self.exec()

# Entry point
def main():
    import sys
    file_path = sys.argv[1] if len(sys.argv) > 1 else None
    app = MyApp(sys.argv)
    sys.exit(app.run(file_path))
```

### Advanced Usage - Custom Messages

```python
class AdvancedApp(SingleInstanceApplication):
    def handle_message(self, message: dict):
        action = message.get("action")
        data = message.get("data", {})

        if action == "custom":
            command = data.get("command")
            args = data.get("args", [])
            self.execute_command(command, args)

# Send custom message from CLI
app = AdvancedApp(sys.argv)
if not app.is_primary_instance():
    message = {
        "action": "custom",
        "data": {
            "command": "refresh",
            "args": ["--force"]
        }
    }
    sys.exit(app.send_to_running_instance(message))
```

## Public API Reference

### Constructor

```python
def __init__(
    self,
    argv: list[str],
    app_id: str,
    prefer_dark: bool = False,
    theme_config: Optional[dict] = None,
)
```

**Parameters**:
- `argv`: Command-line arguments (passed to QApplication)
- `app_id`: Unique application identifier (used for IPC server name)
- `prefer_dark`: If True, automatically select a dark theme on startup (default: False)
- `theme_config`: Optional theme configuration dict (for ThemedApplication, if available)

**Example**:
```python
# Basic usage
app = SingleInstanceApplication(sys.argv, app_id="reamde")

# With dark theme preference
app = SingleInstanceApplication(sys.argv, app_id="myapp", prefer_dark=True)

# With custom theme config
app = SingleInstanceApplication(
    sys.argv,
    app_id="myapp",
    theme_config={"default_theme": "monokai", "persist_theme": True}
)
```

### Properties

```python
@property
def is_primary_instance(self) -> bool
```

Returns `True` if this is the primary (first) instance.

**Example**:
```python
if app.is_primary_instance():
    print("I am the primary instance")
else:
    print("Another instance is already running")
```

### Methods

#### handle_message (Abstract)

```python
def handle_message(self, message: dict) -> None
```

**Must be overridden** by subclasses to handle IPC messages.

**Parameters**:
- `message`: Dictionary containing message data from another instance

**Called when**: Another instance sends a message to this (primary) instance

**Example**:
```python
def handle_message(self, message: dict):
    action = message.get("action")
    if action == "open":
        self.window.open_file(message.get("file"))
```

#### send_to_running_instance

```python
def send_to_running_instance(self, message: dict, timeout: int = 5000) -> int
```

Send a message to the running primary instance.

**Parameters**:
- `message`: Dictionary to send (will be JSON-encoded)
- `timeout`: Connection timeout in milliseconds (default: 5000)

**Returns**: Exit code (0 on success, 1 on failure)

**Example**:
```python
if not app.is_primary_instance():
    message = {"action": "focus"}
    sys.exit(app.send_to_running_instance(message))
```

#### bring_to_front

```python
def bring_to_front(self) -> None
```

Activate and raise the primary instance's main window.

**Platform behavior**:
- Linux (X11): Uses `activateWindow()` + `raise_()`
- Linux (Wayland): May require compositor support
- macOS: Native activation
- Windows: Uses `SetForegroundWindow` equivalent

**Example**:
```python
def handle_message(self, message: dict):
    self.bring_to_front()  # Focus window when receiving message
```

## Implementation Details

### Server Name Generation

```python
def _get_server_name(self) -> str:
    """Generate unique server name for this app."""
    import getpass
    user = getpass.getuser()
    return f"vfwidgets-{self._app_id}-{user}"
```

Includes username to avoid conflicts between different users on same machine.

### Connection Timeout

- **Connection timeout**: 5 seconds (configurable)
- **Read timeout**: 3 seconds
- **Write timeout**: 3 seconds

If secondary instance cannot connect within timeout, it exits with error code 1.

### Error Handling

```python
# Secondary instance connection failure
if not self.send_to_running_instance(message):
    print(f"Error: Could not connect to running {app_id} instance",
          file=sys.stderr)
    sys.exit(1)
```

### Cleanup

QLocalServer is automatically cleaned up on application exit:
```python
def closeEvent(self, event):
    if self._local_server:
        self._local_server.close()
        # Socket file is automatically removed on Linux/macOS
    super().closeEvent(event)
```

## Platform Considerations

### Linux
- **Socket path**: `/tmp/vfwidgets-{app_id}-{user}`
- **Permissions**: 0600 (owner only)
- **Auto-cleanup**: Socket file removed on clean exit
- **X11 vs Wayland**: Focus behavior differs

### macOS
- **Socket path**: `/tmp/vfwidgets-{app_id}-{user}`
- **Permissions**: 0600 (owner only)
- **Native activation**: Works reliably

### Windows
- **Named pipe**: `\\.\pipe\vfwidgets-{app_id}-{user}`
- **Permissions**: Current user only
- **Focus**: Uses SetForegroundWindow equivalent

## Testing Strategy

### Unit Tests

1. **Primary instance creation**
   - Verify server starts successfully
   - Check `is_primary_instance() == True`

2. **Secondary instance connection**
   - Start primary instance
   - Start secondary instance
   - Verify secondary exits after sending message

3. **Message passing**
   - Send message from secondary
   - Verify primary receives correct data
   - Check JSON serialization/deserialization

4. **Error handling**
   - Connection timeout
   - Invalid JSON
   - Server crash/restart

5. **Cleanup**
   - Verify server closes on exit
   - Check socket file removed (Linux/macOS)

### Integration Tests

1. **Multiple launches**
   - Launch app 3 times rapidly
   - Verify only 1 instance running

2. **Cross-directory launch**
   - Launch from directory A
   - Launch from directory B with different file
   - Verify file opens in same instance

3. **Window activation**
   - Minimize primary window
   - Launch secondary instance
   - Verify window restores and comes to front

## Security Considerations

1. **User isolation**: Server name includes username to prevent cross-user access
2. **Socket permissions**: 0600 on Linux/macOS (owner only)
3. **Named pipe security**: Windows pipes use current user SID
4. **Message validation**: JSON parsing with error handling
5. **No arbitrary code execution**: Messages are data only, not code

## Future Enhancements

1. **Message acknowledgment**: Explicit ACK/NACK responses
2. **Bi-directional communication**: Primary can send data back to secondary
3. **Multiple windows**: Support for multiple main windows in primary instance
4. **Session management**: Per-desktop/workspace instances on Linux
5. **Plugin hooks**: Allow plugins to register custom message handlers

## References

- Qt QLocalServer: https://doc.qt.io/qt-6/qlocalserver.html
- Qt QLocalSocket: https://doc.qt.io/qt-6/qlocalsocket.html
- D-Bus alternative: For more complex IPC on Linux
- Named pipes on Windows: https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipes
