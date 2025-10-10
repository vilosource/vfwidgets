# VFWidgets Terminal

A powerful PySide6 terminal emulator widget powered by xterm.js for the VFWidgets collection.

## Features

- 🖥️ **Full Terminal Emulation** - Complete terminal experience using xterm.js
- 🎛️ **Easy Integration** - Drop-in widget for any PySide6/Qt application
- 🔌 **Three Usage Modes** - Embedded, Multi-Session, or Custom Server
- 💾 **Memory Efficient** - Multi-session mode uses 63% less memory
- 📡 **Rich Signal System** - Comprehensive signals for terminal events
- 🎨 **Customizable Themes** - Built-in dark/light themes with vfwidgets-theme integration
- 📋 **Copy/Paste Support** - X11-style clipboard with auto-copy and multiple paste methods
- 🔍 **Output Capture** - Capture and process terminal output programmatically
- 🚀 **Developer Friendly** - Extensive API for terminal control
- 🖱️ **Interactive Features** - Clickable links, search, custom key bindings
- 🌐 **Cross-Platform** - Works on Linux, macOS, and Windows

## Installation

```bash
# Install from local path
pip install ./widgets/terminal_widget

# Install in editable mode for development
pip install -e ./widgets/terminal_widget

# Install with development dependencies
pip install -e "./widgets/terminal_widget[dev]"

# Install with full features (psutil, pygments)
pip install -e "./widgets/terminal_widget[full]"
```

## Quick Start

### Basic Usage

```python
from PySide6.QtWidgets import QApplication, QMainWindow
from vfwidgets_terminal import TerminalWidget

app = QApplication([])
window = QMainWindow()

# Create terminal widget
terminal = TerminalWidget()
window.setCentralWidget(terminal)

window.show()
app.exec()
```

### Different Shells and Commands

```python
# Python REPL
terminal = TerminalWidget(command='python', args=['-i'])

# Custom shell
terminal = TerminalWidget(command='zsh')

# SSH session
terminal = TerminalWidget(command='ssh', args=['user@host'])

# With working directory
terminal = TerminalWidget(command='bash', cwd='/home/user/project')

# With environment variables
terminal = TerminalWidget(
    command='bash',
    env={'NODE_ENV': 'development', 'DEBUG': '1'}
)
```

### Signal Handling

```python
terminal = TerminalWidget()

# Connect to signals
terminal.terminal_ready.connect(on_ready)
terminal.output_received.connect(on_output)
terminal.command_finished.connect(on_command_done)
terminal.terminal_closed.connect(on_closed)

def on_output(data: str):
    print(f"Output: {data}")

def on_command_done(exit_code: int):
    print(f"Command finished with code: {exit_code}")
```

### Programmatic Control

```python
# Send commands
terminal.send_command("ls -la")
terminal.send_command("echo 'Hello World'")

# Send raw input
terminal.send_input("y\n")  # Answer 'yes' to prompt

# Clear terminal
terminal.clear()

# Reset terminal state
terminal.reset()

# Execute script
script = """
echo "Starting setup..."
npm install
npm run build
echo "Done!"
"""
terminal.execute_script(script)

# Change directory
terminal.set_working_directory("/home/user/project")
```

### Output Capture and Processing

```python
# Enable output capture
terminal = TerminalWidget(capture_output=True)

# Get captured output
output = terminal.get_output()
last_10_lines = terminal.get_output(last_n_lines=10)

# Save output to file
terminal.save_output("terminal_session.txt")

# Filter output in real-time
def filter_errors(output: str) -> str:
    if "ERROR" in output:
        return f"⚠️ {output}"
    return output

terminal = TerminalWidget(output_filter=filter_errors)

# Parse output
import json

def json_parser(output: str):
    try:
        return json.loads(output)
    except:
        return output

terminal = TerminalWidget(output_parser=json_parser)
```

### Terminal Configuration

Configure xterm.js behavior options (scrollback, cursor, scrolling, typography, etc.):

```python
# Using configuration dictionary
terminal = TerminalWidget(
    terminal_config={
        # Typography & Spacing
        "lineHeight": 1.3,          # Line spacing (1.0 = tight, 1.5 = relaxed)
        "letterSpacing": 0.5,        # Character spacing in pixels
        # Scrolling
        "scrollback": 10000,
        "scrollSensitivity": 2,
        "fastScrollSensitivity": 10,
        # Cursor
        "cursorStyle": "bar",
        "cursorBlink": True,
        # Behavior
        "bellStyle": "visual",
        "tabStopWidth": 4,
        "rightClickSelectsWord": True
    }
)

# Using presets
from vfwidgets_terminal.presets import TERMINAL_CONFIGS

# Developer preset (10k scrollback, visual bell, bar cursor)
terminal = TerminalWidget(terminal_config=TERMINAL_CONFIGS["developer"])

# Power user preset (50k scrollback, no cursor blink)
terminal = TerminalWidget(terminal_config=TERMINAL_CONFIGS["power_user"])

# Log viewer preset (100k scrollback, fast scrolling)
terminal = TerminalWidget(terminal_config=TERMINAL_CONFIGS["log_viewer"])

# Runtime configuration changes
terminal.set_terminal_config({"scrollback": 50000})
current_config = terminal.get_terminal_config()
```

Available configuration options:

**Typography & Spacing:**
- `lineHeight` (float): Line spacing multiplier (default: 1.2, range: 1.0-2.0)
  - `1.0`: Tight/compact spacing
  - `1.2`: Normal spacing (default)
  - `1.5`: Relaxed/generous spacing
- `letterSpacing` (float): Horizontal character spacing in pixels (default: 0, range: 0-5)

**Scrolling:**
- `scrollback` (int): Number of scrollback lines (default: 1000)
- `scrollSensitivity` (int): Mouse wheel scroll speed (default: 1)
- `fastScrollSensitivity` (int): Shift+scroll speed (default: 5)
- `fastScrollModifier` (str): 'alt', 'ctrl', or 'shift' (default: 'shift')

**Cursor:**
- `cursorBlink` (bool): Whether cursor blinks (default: true)
- `cursorStyle` (str): 'block', 'underline', or 'bar' (default: 'block')

**Behavior:**
- `tabStopWidth` (int): Width of tab stops (default: 4)
- `bellStyle` (str): 'none', 'sound', or 'visual' (default: 'none')
- `rightClickSelectsWord` (bool): Select word on right click (default: false)
- `convertEol` (bool): Convert \n to \r\n (default: false)

Available presets: `default`, `developer`, `power_user`, `minimal`, `accessible`, `log_viewer`, `remote`

### Theme Configuration

Terminal themes support both colors and typography customization:

```python
# Custom theme with spacing customization
my_theme = {
    "name": "My Custom Theme",
    "terminal": {
        # Typography & Spacing
        "fontFamily": "Monaco, Consolas, 'Courier New', monospace",
        "fontSize": 14,
        "lineHeight": 1.4,       # 40% extra line spacing
        "letterSpacing": 0.5,    # 0.5px between characters

        # Colors
        "background": "#1e1e1e",
        "foreground": "#d4d4d4",
        "cursor": "#ffcc00",
        "cursorAccent": "#1e1e1e",
        "selectionBackground": "rgba(38, 79, 120, 0.3)",

        # ANSI colors
        "black": "#000000",
        "red": "#cd3131",
        "green": "#0dbc79",
        "yellow": "#e5e510",
        "blue": "#2472c8",
        "magenta": "#bc3fbc",
        "cyan": "#11a8cd",
        "white": "#e5e5e5",
        "brightBlack": "#555753",
        "brightRed": "#f14c4c",
        "brightGreen": "#23d18b",
        "brightYellow": "#f5f543",
        "brightBlue": "#3b8eea",
        "brightMagenta": "#d670d6",
        "brightCyan": "#29b8db",
        "brightWhite": "#f5f5f5",
    }
}

# Apply theme
terminal.set_terminal_theme(my_theme)

# Get current theme
current_theme = terminal.get_terminal_theme()
```

**Example Spacing Presets:**

```python
# Compact theme (tight spacing)
COMPACT_THEME = {
    "terminal": {
        "lineHeight": 1.0,    # No extra spacing
        "letterSpacing": 0,
        # ... colors
    }
}

# Relaxed theme (generous spacing)
RELAXED_THEME = {
    "terminal": {
        "lineHeight": 1.5,    # 50% extra spacing
        "letterSpacing": 1,   # 1px between characters
        # ... colors
    }
}

# Accessible theme (maximum readability)
ACCESSIBLE_THEME = {
    "terminal": {
        "fontSize": 15,
        "lineHeight": 1.6,    # 60% extra spacing
        "letterSpacing": 1.5, # 1.5px between characters
        # ... high contrast colors
    }
}
```

### Read-Only Mode

```python
# Create read-only terminal (useful for log viewers)
terminal = TerminalWidget(read_only=True)

# Toggle read-only mode
terminal.set_read_only(True)
```

### Multi-Session Server Mode (Recommended for Multiple Terminals)

Use a shared server for memory-efficient multi-terminal applications:

```python
from vfwidgets_terminal import MultiSessionTerminalServer, TerminalWidget

# Create shared server once
server = MultiSessionTerminalServer(port=0)  # Auto-allocate port
server.start()

# Create multiple terminals sharing the server
def create_terminal():
    # Create session first
    session_id = server.create_session(command="bash")

    # Get session URL
    session_url = server.get_session_url(session_id)

    # Connect widget to session
    return TerminalWidget(server_url=session_url)

# Create terminals
terminal1 = create_terminal()
terminal2 = create_terminal()
# ... up to 20 terminals (configurable)

# Cleanup on exit
server.shutdown()
```

**Benefits:**
- **63% less memory:** 20 terminals = ~110MB vs ~300MB (embedded mode)
- **Centralized management:** One server handles all sessions
- **Scalable:** Supports 5-20+ concurrent terminals efficiently

**When to use:**
- Applications with 5+ terminals
- Multi-terminal IDEs (like ViloxTerm)
- Memory-constrained environments

### External/Custom Server Mode

```python
# Connect to custom terminal server
terminal = TerminalWidget(server_url='http://localhost:5000')

## Advanced Examples

See the `examples/` directory for complete examples:

- `basic_usage.py` - Simple terminal window
- `advanced_features.py` - Multiple terminals with tabs, output capture, and controls

## API Reference

### TerminalWidget

#### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `command` | str | 'bash' | Shell command to execute |
| `args` | List[str] | None | Command arguments |
| `cwd` | str | None | Working directory |
| `env` | Dict[str, str] | None | Environment variables |
| `server_url` | str | None | External server URL |
| `port` | int | 0 | Server port (0 for random) |
| `host` | str | '127.0.0.1' | Server host |
| `rows` | int | 24 | Terminal rows |
| `cols` | int | 80 | Terminal columns |
| `scrollback` | int | 1000 | Scrollback buffer lines (DEPRECATED) |
| `theme` | str | 'dark' | Color theme |
| `terminal_config` | Dict | None | xterm.js configuration options |
| `capture_output` | bool | False | Enable output capture |
| `output_filter` | Callable | None | Output filter function |
| `output_parser` | Callable | None | Output parser function |
| `read_only` | bool | False | Read-only mode |
| `debug` | bool | False | Enable debug logging |
| `event_config` | EventConfig | None | Event system configuration |

#### Signals

| Signal | Parameters | Description |
|--------|------------|-------------|
| `terminal_ready` | - | Terminal is ready for use |
| `terminal_closed` | int (exit_code) | Terminal closed |
| `command_started` | str (command) | Command execution started |
| `command_finished` | int (exit_code) | Command execution finished |
| `output_received` | str (data) | Output data received |
| `error_received` | str (data) | Error data received |
| `input_sent` | str (data) | Input sent to terminal |
| `resize_occurred` | int, int (rows, cols) | Terminal resized |
| `connection_lost` | - | Connection to server lost |
| `connection_restored` | - | Connection restored |
| `server_started` | str (url) | Server started |

#### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `send_command(command: str)` | None | Send command to terminal |
| `send_input(text: str)` | None | Send raw input |
| `clear()` | None | Clear terminal screen |
| `reset()` | None | Reset terminal state |
| `get_output(last_n_lines: int)` | str | Get captured output |
| `save_output(filepath: str)` | None | Save output to file |
| `set_read_only(read_only: bool)` | None | Set read-only mode |
| `execute_script(script: str)` | None | Execute multi-line script |
| `get_process_info()` | Dict | Get process information |
| `set_working_directory(path: str)` | None | Change working directory |
| `set_terminal_config(config: dict)` | None | Set xterm.js configuration |
| `get_terminal_config()` | Dict | Get current terminal configuration |
| `set_terminal_theme(theme: dict)` | None | Set terminal colors and fonts |
| `get_terminal_theme()` | Dict | Get current terminal theme |
| `close_terminal()` | None | Close terminal |

## Copy/Paste Features

The terminal widget supports X11-style copy/paste behavior for a seamless terminal experience:

### Auto-Copy on Selection (Enabled by Default)
- Simply **select text** with your mouse or keyboard
- Selected text is **automatically copied** to the system clipboard
- No need to press Ctrl+C or use a context menu

### Multiple Paste Methods
1. **Middle-Click Paste** (X11-style, recommended)
   - Select text anywhere in the terminal
   - Middle-click (mouse wheel button) to paste at cursor position
   - Fast and intuitive workflow for terminal power users

2. **Right-Click Paste** (Context menu)
   - Right-click in the terminal to open context menu
   - Select "Paste" to paste clipboard content at cursor
   - Also shows "Copy" option when text is selected

3. **Keyboard Paste** (Traditional)
   - Press `Ctrl+Shift+V` to paste clipboard content
   - Works everywhere in the terminal

### Programmatic Control
```python
# Enable/disable auto-copy on selection
terminal.set_auto_copy_on_selection(True)  # Default: True

# Enable/disable middle-click paste
terminal.set_middle_click_paste(True)  # Default: True

# Programmatic copy/paste
terminal._copy_to_clipboard("text to copy")
terminal._paste_from_clipboard()
```

### All Keyboard Shortcuts

- **Paste**: `Ctrl+Shift+V` or middle-click or right-click → Paste
- **Copy**: Select text (auto-copies) or right-click → Copy
- **Clear**: `Ctrl+L`
- **Search**: `Ctrl+Shift+F` (in browser)

## Requirements

### All Platforms
- Python 3.9+
- PySide6 >= 6.9.0
- Flask & Flask-SocketIO
- Modern web browser engine (Qt WebEngine)

### Windows-Specific
- **pywinpty** (required for terminal functionality)
  ```bash
  pip install pywinpty
  ```
- **Important**: Use `MultiSessionTerminalServer` on Windows (not `EmbeddedTerminalServer`)
- Use `cmd.exe` or `powershell` as the command (not `bash`)

## Troubleshooting

### Windows: ImportError for fcntl/pty/termios

**Error**: `ModuleNotFoundError: No module named 'fcntl'`

**Solution**: Use `MultiSessionTerminalServer` instead of direct `TerminalWidget()`:

```python
from vfwidgets_terminal import MultiSessionTerminalServer, TerminalWidget

# Install pywinpty first: pip install pywinpty

# Create multi-session server
server = MultiSessionTerminalServer(port=0)
server.start()

# Create terminal with Windows shell
session_id = server.create_session(command='cmd.exe')  # or 'powershell'
session_url = server.get_session_url(session_id)
terminal = TerminalWidget(server_url=session_url)

# Cleanup on exit
server.shutdown()
```

**Why**: `EmbeddedTerminalServer` (used by default `TerminalWidget()`) requires Unix-specific modules. `MultiSessionTerminalServer` uses the cross-platform backend system with `pywinpty` for Windows.

### Windows: Missing pywinpty

**Error**: `RuntimeError: Windows terminal backend requires pywinpty`

**Solution**: Install pywinpty package:
```bash
pip install pywinpty
```

### WSL/VM Graphics Issues

The widget automatically configures environment for WSL/VM compatibility. To disable:

```python
import os
os.environ['VFWIDGETS_NO_AUTO_SETUP'] = '1'

from vfwidgets_terminal import TerminalWidget
```

### Terminal Not Loading

Ensure all dependencies are installed:
```bash
pip install -e "./widgets/terminal_widget[dev]"
```

### Server Port Conflicts

The widget uses a random port by default. To specify a fixed port:
```python
terminal = TerminalWidget(port=8765)
```

## Documentation

### Comprehensive Guides

- **[Lessons Learned](docs/lessons-learned-GUIDE.md)** - Critical lessons from multi-session implementation
- **[Backend Implementation](docs/backend-implementation-GUIDE.md)** - Guide to implementing custom backends
- **[Server Implementation](docs/server-implementation-GUIDE.md)** - Guide to implementing custom servers
- **[Protocol Specification](docs/terminal-server-protocol-SPEC.md)** - Complete SocketIO protocol
- **[Architecture Design](docs/architecture-DESIGN.md)** - System architecture and design decisions
- **[Theme Integration](docs/theme-integration-lessons-GUIDE.md)** - Theme system integration guide

### Quick Links

- **Examples:** See `examples/README.md` for usage examples
- **API Reference:** See `docs/api.md` for complete API documentation
- **Usage Guide:** See `docs/usage.md` for detailed usage patterns

## Development

```bash
# Run tests
cd widgets/terminal_widget
pytest

# Format code
black src/

# Lint
ruff check src/

# Type check
mypy src/
```

## Architecture

### Embedded Mode (1-5 terminals)
```
TerminalWidget #1 → EmbeddedServer (port 5001) → PTY #1
TerminalWidget #2 → EmbeddedServer (port 5002) → PTY #2
```

### Multi-Session Mode (5-20+ terminals - **Recommended**)
```
MultiSessionTerminalServer (port 5000)
├─ Session abc123 → PTY #1
├─ Session def456 → PTY #2
└─ Session ghi789 → PTY #3

TerminalWidget #1, #2, #3 → All connect to port 5000
```

**Memory Comparison:**
- Embedded (20 terminals): ~300 MB
- Multi-Session (20 terminals): ~110 MB (63% reduction)

For complete architecture details, see [Architecture Design](docs/architecture-DESIGN.md)

## License

MIT License - See LICENSE file for details.

## Credits

- Powered by [xterm.js](https://xtermjs.org/)
- Inspired by [pyxtermjs](https://github.com/cs01/pyxtermjs)
- Part of the VFWidgets collection

## Author

**Vilosource**
Email: vilosource@viloforge.com