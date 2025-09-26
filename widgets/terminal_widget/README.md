# VFWidgets Terminal

A powerful PySide6 terminal emulator widget powered by xterm.js for the VFWidgets collection.

## Features

- 🖥️ **Full Terminal Emulation** - Complete terminal experience using xterm.js
- 🎛️ **Easy Integration** - Drop-in widget for any PySide6/Qt application
- 🔌 **Flexible Architecture** - Embedded or external server modes
- 📡 **Rich Signal System** - Comprehensive signals for terminal events
- 🎨 **Customizable Themes** - Built-in dark/light themes
- 📋 **Copy/Paste Support** - Full clipboard integration
- 🔍 **Output Capture** - Capture and process terminal output programmatically
- 🚀 **Developer Friendly** - Extensive API for terminal control
- 🖱️ **Interactive Features** - Clickable links, search, custom key bindings

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

### Themes

```python
# Built-in themes
terminal = TerminalWidget(theme='dark')  # default
terminal = TerminalWidget(theme='light')

# Custom theme (future feature)
custom_theme = {
    'background': '#282c34',
    'foreground': '#abb2bf',
    'cursor': '#528bff',
    # ... more colors
}
terminal = TerminalWidget(theme=custom_theme)
```

### Read-Only Mode

```python
# Create read-only terminal (useful for log viewers)
terminal = TerminalWidget(read_only=True)

# Toggle read-only mode
terminal.set_read_only(True)
```

### External Server Mode

```python
# Connect to existing terminal server
terminal = TerminalWidget(server_url='http://localhost:5000')
```

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
| `scrollback` | int | 1000 | Scrollback buffer lines |
| `theme` | str | 'dark' | Color theme |
| `capture_output` | bool | False | Enable output capture |
| `output_filter` | Callable | None | Output filter function |
| `output_parser` | Callable | None | Output parser function |
| `read_only` | bool | False | Read-only mode |
| `debug` | bool | False | Enable debug logging |

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
| `close_terminal()` | None | Close terminal |

## Keyboard Shortcuts

- **Copy**: `Ctrl+Shift+C`
- **Paste**: `Ctrl+Shift+V`
- **Clear**: `Ctrl+L`
- **Search**: `Ctrl+Shift+F` (in browser)

## Requirements

- Python 3.9+
- PySide6 >= 6.9.0
- Flask & Flask-SocketIO
- Modern web browser engine (Qt WebEngine)

## Troubleshooting

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

```
┌─────────────────────────────────┐
│     PySide6 Application         │
├─────────────────────────────────┤
│     TerminalWidget              │
├─────────────────────────────────┤
│     QWebEngineView              │
│            ↕                    │
│   EmbeddedTerminalServer        │
├─────────────────────────────────┤
│   Flask + SocketIO (localhost)  │
│            ↕                    │
│    PTY Process + WebSocket      │
│            ↕                    │
│         xterm.js                │
└─────────────────────────────────┘
```

## License

MIT License - See LICENSE file for details.

## Credits

- Powered by [xterm.js](https://xtermjs.org/)
- Inspired by [pyxtermjs](https://github.com/cs01/pyxtermjs)
- Part of the VFWidgets collection

## Author

**Vilosource**
Email: vilosource@viloforge.com