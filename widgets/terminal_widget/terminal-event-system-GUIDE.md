# VFWidgets Terminal Event System Guide

## Overview

The VFWidgets Terminal Widget provides a comprehensive, Qt-compliant event system that follows standard GUI design patterns. This guide shows developers how to effectively use the terminal widget's events in their applications.

## ✨ Key Features

- **Qt-Compliant Signal Names**: All signals follow Qt/PySide6 naming conventions (camelCase, past tense)
- **Structured Event Data**: Rich event data classes provide detailed context
- **Event Categories**: Configure which types of events to receive
- **Backwards Compatibility**: Existing code continues to work with deprecation warnings
- **Helper Methods**: Intuitive APIs for common use cases
- **Type Safety**: Full type hints for IDE integration

## 🎯 Quick Start

### Basic Usage

```python
from PySide6.QtWidgets import QApplication, QMainWindow
from vfwidgets_terminal import TerminalWidget

app = QApplication([])
window = QMainWindow()

# Create terminal with default event configuration
terminal = TerminalWidget(debug=True)

# Connect to lifecycle events
terminal.terminalReady.connect(lambda: print("✅ Terminal is ready!"))
terminal.processStarted.connect(lambda event: print(f"🚀 Process started: {event.command}"))

# Connect to user interaction events
terminal.keyPressed.connect(lambda event: print(f"⌨️ Key: {event.key}"))
terminal.selectionChanged.connect(lambda text: print(f"📝 Selected: {text[:50]}"))

window.setCentralWidget(terminal)
window.show()
app.exec()
```

## 📊 Event Categories

Events are organized into categories that can be enabled/disabled:

| Category | Events | Description |
|----------|--------|-------------|
| `LIFECYCLE` | terminalReady, terminalClosed, serverStarted | Terminal startup/shutdown |
| `PROCESS` | processStarted, processFinished | Command execution |
| `CONTENT` | outputReceived, errorReceived, inputSent | Terminal I/O |
| `INTERACTION` | keyPressed, selectionChanged, contextMenuRequested | User actions |
| `FOCUS` | focusReceived, focusLost | Focus management |
| `APPEARANCE` | sizeChanged, titleChanged, bellActivated | Display changes |

### Configuring Event Categories

```python
from vfwidgets_terminal import TerminalWidget, EventConfig, EventCategory

# Create custom event configuration
config = EventConfig(
    enabled_categories={
        EventCategory.LIFECYCLE,
        EventCategory.PROCESS,
        EventCategory.INTERACTION
    },
    throttle_high_frequency=True,
    debug_logging=True
)

terminal = TerminalWidget(event_config=config)

# Or configure after creation
terminal.configure_events(config)

# Enable/disable individual categories
terminal.enable_event_category(EventCategory.FOCUS)
terminal.disable_event_category(EventCategory.APPEARANCE)
```

## 🎪 Event Data Classes

Modern signals provide structured data objects instead of primitive parameters:

### ProcessEvent

```python
from vfwidgets_terminal import ProcessEvent

def handle_process_started(event: ProcessEvent):
    print(f"Command: {event.command}")
    print(f"PID: {event.pid}")
    print(f"Working Directory: {event.working_directory}")
    print(f"Started at: {event.timestamp}")

terminal.processStarted.connect(handle_process_started)
```

### KeyEvent

```python
from vfwidgets_terminal import KeyEvent

def handle_key_press(event: KeyEvent):
    if event.ctrl and event.key == 'c':
        print("Ctrl+C detected!")
    elif event.alt and event.key == 'Enter':
        print("Alt+Enter combo!")

    print(f"Key: {event.key}, Code: {event.code}")
    print(f"Modifiers: Ctrl={event.ctrl}, Alt={event.alt}, Shift={event.shift}")

terminal.keyPressed.connect(handle_key_press)
```

### ContextMenuEvent

```python
from vfwidgets_terminal import ContextMenuEvent
from PySide6.QtWidgets import QMenu, QAction

def handle_context_menu(event: ContextMenuEvent):
    print(f"Right-click at: ({event.position.x()}, {event.position.y()})")
    print(f"Selected text: {event.selected_text}")

    # Create custom context menu
    menu = QMenu()
    if event.selected_text:
        action = QAction(f"Process '{event.selected_text[:20]}...'")
        menu.addAction(action)

    return menu

terminal.contextMenuRequested.connect(handle_context_menu)
```

## 🚀 Common Use Cases

### 1. Command Execution Monitoring

```python
from vfwidgets_terminal import TerminalWidget, ProcessEvent

terminal = TerminalWidget()

def monitor_commands(event: ProcessEvent):
    """Monitor all commands executed in the terminal."""
    print(f"⚡ Command executed: {event.command}")
    if event.pid:
        print(f"   Process ID: {event.pid}")

    # Log to file, database, etc.
    with open("command_log.txt", "a") as f:
        f.write(f"{event.timestamp}: {event.command}\\n")

# Helper method for common use case
terminal.monitor_command_execution(monitor_commands)
```

### 2. Session Recording

```python
def record_session(output: str):
    """Record all terminal output to a file."""
    with open("session.log", "a") as f:
        f.write(output)

# Helper method for session recording
terminal.enable_session_recording(record_session)

# Or connect directly
terminal.outputReceived.connect(record_session)
```

### 3. Custom Context Menu

```python
from PySide6.QtWidgets import QMenu, QAction
from vfwidgets_terminal import ContextMenuEvent

def create_custom_menu(event: ContextMenuEvent):
    """Create custom context menu based on selection."""
    menu = QMenu()

    if event.selected_text:
        # Add action for selected text
        search_action = QAction(f"🔍 Search for '{event.selected_text[:20]}...'")
        search_action.triggered.connect(lambda: search_web(event.selected_text))
        menu.addAction(search_action)

        # Add action to run as command
        run_action = QAction("▶️ Run as command")
        run_action.triggered.connect(lambda: terminal.send_command(event.selected_text))
        menu.addAction(run_action)

    return menu

def search_web(text: str):
    import webbrowser
    webbrowser.open(f"https://google.com/search?q={text}")

terminal.add_context_menu_handler(create_custom_menu)
```

### 4. Text Selection Handler

```python
def handle_selection(text: str):
    """Process text selection changes."""
    if len(text) > 0:
        print(f"Selected {len(text)} characters: {text[:50]}...")

        # Automatically copy long selections to clipboard
        if len(text) > 100:
            from PySide6.QtWidgets import QApplication
            QApplication.clipboard().setText(text)
            print("📋 Long selection automatically copied!")

# Helper method
terminal.set_selection_handler(handle_selection)
```

### 5. Focus Tracking

```python
def on_focus_received():
    """Handle terminal receiving focus."""
    print("🎯 Terminal gained focus - user is active")
    # Update UI, start monitoring, etc.

def on_focus_lost():
    """Handle terminal losing focus."""
    print("❌ Terminal lost focus - user switched away")
    # Save state, pause monitoring, etc.

terminal.focusReceived.connect(on_focus_received)
terminal.focusLost.connect(on_focus_lost)
```

## 🔄 Migration from Old Signals

The terminal widget maintains backwards compatibility with deprecation warnings:

### Old Signal → New Signal Mapping

| Old Signal (Deprecated) | New Signal | Data Type |
|-------------------------|------------|-----------|
| `terminal_ready` | `terminalReady` | None |
| `command_started` | `processStarted` | ProcessEvent |
| `output_received` | `outputReceived` | str |
| `key_pressed` | `keyPressed` | KeyEvent |
| `context_menu_requested` | `contextMenuRequested` | ContextMenuEvent |
| `focus_received` | `focusReceived` | None |
| `selection_changed` | `selectionChanged` | str |

### Migration Example

```python
# OLD CODE (still works with warnings)
def old_key_handler(key, code, ctrl, alt, shift):
    if ctrl and key == 'c':
        print("Ctrl+C pressed")

terminal.key_pressed.connect(old_key_handler)  # ⚠️ Deprecation warning

# NEW CODE (recommended)
def new_key_handler(event: KeyEvent):
    if event.ctrl and event.key == 'c':
        print("Ctrl+C pressed")

terminal.keyPressed.connect(new_key_handler)  # ✅ Modern approach
```

## ⚡ Performance Considerations

### Event Throttling

High-frequency events (like cursor movement) can be throttled:

```python
from vfwidgets_terminal import EventConfig

config = EventConfig(
    throttle_high_frequency=True,  # Enable throttling
    debug_logging=False           # Disable debug logs for performance
)

terminal = TerminalWidget(event_config=config)
```

### Selective Event Categories

Only enable event categories you need:

```python
from vfwidgets_terminal import EventCategory, EventConfig

# Only monitor process and content events
config = EventConfig(
    enabled_categories={
        EventCategory.PROCESS,
        EventCategory.CONTENT
    }
)

terminal = TerminalWidget(event_config=config)
```

## 🛠️ Advanced Usage

### Dynamic Event Configuration

```python
def toggle_debug_mode():
    """Dynamically toggle debug event logging."""
    current_config = terminal.event_config
    current_config.debug_logging = not current_config.debug_logging
    terminal.configure_events(current_config)

def enable_full_monitoring():
    """Enable all event categories for debugging."""
    terminal.configure_events(EventConfig(
        enabled_categories=set(EventCategory),
        debug_logging=True
    ))
```

### Custom Event Filters

```python
def setup_filtered_monitoring():
    """Set up monitoring with custom filters."""

    def important_commands_only(event: ProcessEvent):
        important_commands = ['git', 'docker', 'kubectl', 'npm']
        if any(cmd in event.command for cmd in important_commands):
            print(f"🎯 Important command: {event.command}")

    def error_detection(output: str):
        if 'error' in output.lower() or 'exception' in output.lower():
            print(f"❌ Error detected: {output[:100]}...")
            # Could send notification, log to special file, etc.

    terminal.processStarted.connect(important_commands_only)
    terminal.outputReceived.connect(error_detection)
```

## 🎨 Theme and Appearance Events

```python
def handle_appearance_changes():
    """Monitor terminal appearance changes."""

    def on_size_changed(rows: int, cols: int):
        print(f"📐 Terminal resized to {rows}x{cols}")
        # Adjust layout, save preferences, etc.

    def on_title_changed(title: str):
        print(f"🏷️ Terminal title: {title}")
        # Update window title, tab name, etc.

    def on_bell_activated():
        print("🔔 Terminal bell!")
        # Flash window, play sound, send notification, etc.

    terminal.sizeChanged.connect(on_size_changed)
    terminal.titleChanged.connect(on_title_changed)
    terminal.bellActivated.connect(on_bell_activated)
```

## 🧪 Testing and Debugging

### Debug Mode

```python
# Enable debug mode for comprehensive event logging
terminal = TerminalWidget(debug=True)

# Or enable specific debug categories
from vfwidgets_terminal import EventConfig, EventCategory

debug_config = EventConfig(
    enabled_categories={EventCategory.INTERACTION, EventCategory.FOCUS},
    debug_logging=True
)
terminal = TerminalWidget(event_config=debug_config)
```

### Event Testing

```python
def test_all_events():
    """Connect to all events for testing."""

    # Lifecycle events
    terminal.terminalReady.connect(lambda: print("✅ LIFECYCLE: Terminal ready"))
    terminal.serverStarted.connect(lambda url: print(f"🚀 LIFECYCLE: Server at {url}"))

    # Process events
    terminal.processStarted.connect(lambda e: print(f"⚡ PROCESS: {e.command} (PID: {e.pid})"))
    terminal.processFinished.connect(lambda code: print(f"🏁 PROCESS: Exit code {code}"))

    # Interaction events
    terminal.keyPressed.connect(lambda e: print(f"⌨️ INTERACTION: {e.key}"))
    terminal.selectionChanged.connect(lambda text: print(f"📝 INTERACTION: Selected {len(text)} chars"))

    # Focus events
    terminal.focusReceived.connect(lambda: print("🎯 FOCUS: Gained"))
    terminal.focusLost.connect(lambda: print("❌ FOCUS: Lost"))

test_all_events()
```

## 📝 Best Practices

1. **Use Event Categories**: Only enable the event categories you need for better performance
2. **Leverage Helper Methods**: Use built-in helper methods for common patterns
3. **Handle Errors Gracefully**: Always handle potential exceptions in event handlers
4. **Use Structured Data**: Take advantage of the rich event data classes
5. **Consider Performance**: Be mindful of high-frequency events like key presses and cursor movement
6. **Migrate Gradually**: Update to new signals when convenient, old signals still work
7. **Test Thoroughly**: Use debug mode during development to understand event flow

## 🔗 Related APIs

- [TerminalWidget API Reference](./terminal-api-REFERENCE.md)
- [Event Configuration Guide](./event-configuration-GUIDE.md)
- [Custom Context Menu Tutorial](./context-menu-TUTORIAL.md)
- [Performance Optimization Tips](./performance-OPTIMIZATION.md)

---

*This guide covers the modern, Qt-compliant event system. For legacy signal compatibility, see the [Migration Guide](./migration-GUIDE.md).*