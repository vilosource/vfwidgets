#!/usr/bin/env python3
"""
Modern Terminal Event System Demo

This example demonstrates the new Qt-compliant event system with structured
event data classes and event categories. Run this to see all the modern
events in action.

Usage:
    python examples/modern_events_demo.py

Features demonstrated:
- Modern Qt-compliant signal names
- Structured event data classes
- Event categories and configuration
- Helper methods for common use cases
- Custom context menu handling
"""

import sys
from datetime import datetime
from pathlib import Path

# Add the src directory to path so we can import the widget
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from PySide6.QtCore import QTimer
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMenu,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from vfwidgets_terminal import (
    ContextMenuEvent,
    EventCategory,
    EventConfig,
    KeyEvent,
    ProcessEvent,
    TerminalWidget,
)


class EventLogWidget(QTextEdit):
    """Widget to display event logs in real-time."""

    def __init__(self):
        super().__init__()
        self.setMaximumHeight(200)
        self.setFont(QFont("Consolas", 9))
        self.setStyleSheet(
            """
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #464647;
            }
        """
        )
        self.append("🎪 Modern Terminal Event System Demo")
        self.append("=" * 50)

    def log_event(self, category: str, event_name: str, details: str = ""):
        """Add an event to the log."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        category_emoji = {
            "LIFECYCLE": "🔄",
            "PROCESS": "⚡",
            "CONTENT": "📄",
            "INTERACTION": "🎯",
            "FOCUS": "👁️",
            "APPEARANCE": "🎨",
        }.get(category, "📝")

        log_line = f"[{timestamp}] {category_emoji} {category}: {event_name}"
        if details:
            log_line += f" - {details}"

        self.append(log_line)

        # Auto-scroll to bottom
        cursor = self.textCursor()
        cursor.movePosition(cursor.End)
        self.setTextCursor(cursor)


class ModernEventsDemo(QMainWindow):
    """Main demo window showing modern terminal events."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("VFWidgets Terminal - Modern Event System Demo")
        self.setGeometry(100, 100, 1000, 700)

        # Create main widget and layout
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)

        # Add title
        title = QLabel("🎪 Modern Terminal Event System Demo")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Add description
        desc = QLabel(
            "This demo showcases the new Qt-compliant event system with structured data and categories."
        )
        desc.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(desc)

        # Create event log
        self.event_log = EventLogWidget()
        layout.addWidget(self.event_log)

        # Create terminal with custom event configuration
        self.terminal = TerminalWidget(
            debug=True,
            event_config=EventConfig(
                enabled_categories=set(EventCategory),  # Enable all categories
                debug_logging=True,
                throttle_high_frequency=False,  # Show all events for demo
            ),
        )
        layout.addWidget(self.terminal)

        # Set central widget
        self.setCentralWidget(main_widget)

        # Set up event monitoring
        self._setup_event_monitoring()

        # Set up demo commands
        self._setup_demo_commands()

        self.event_log.log_event("DEMO", "Demo initialized", "All event categories enabled")

    def _setup_event_monitoring(self):
        """Set up comprehensive event monitoring."""

        # === LIFECYCLE EVENTS ===
        self.terminal.terminalReady.connect(
            lambda: self.event_log.log_event(
                "LIFECYCLE", "terminalReady", "Terminal is ready for use"
            )
        )

        self.terminal.serverStarted.connect(
            lambda url: self.event_log.log_event("LIFECYCLE", "serverStarted", f"Server at {url}")
        )

        self.terminal.terminalClosed.connect(
            lambda code: self.event_log.log_event(
                "LIFECYCLE", "terminalClosed", f"Exit code: {code}"
            )
        )

        self.terminal.connectionLost.connect(
            lambda: self.event_log.log_event(
                "LIFECYCLE", "connectionLost", "Lost connection to terminal"
            )
        )

        self.terminal.connectionRestored.connect(
            lambda: self.event_log.log_event(
                "LIFECYCLE", "connectionRestored", "Connection restored"
            )
        )

        # === PROCESS EVENTS ===
        self.terminal.processStarted.connect(self._handle_process_started)
        self.terminal.processFinished.connect(
            lambda code: self.event_log.log_event(
                "PROCESS", "processFinished", f"Exit code: {code}"
            )
        )

        # === CONTENT EVENTS ===
        self.terminal.outputReceived.connect(
            lambda data: self.event_log.log_event(
                "CONTENT", "outputReceived", f"{len(data)} chars: {data[:30]}..."
            )
        )

        self.terminal.errorReceived.connect(
            lambda data: self.event_log.log_event(
                "CONTENT", "errorReceived", f"{len(data)} chars: {data[:30]}..."
            )
        )

        self.terminal.inputSent.connect(
            lambda text: self.event_log.log_event("CONTENT", "inputSent", f"Sent: {text[:30]}...")
        )

        # === INTERACTION EVENTS ===
        self.terminal.keyPressed.connect(self._handle_key_pressed)
        self.terminal.selectionChanged.connect(self._handle_selection_changed)
        self.terminal.contextMenuRequested.connect(self._handle_context_menu)

        # === FOCUS EVENTS ===
        self.terminal.focusReceived.connect(
            lambda: self.event_log.log_event("FOCUS", "focusReceived", "Terminal gained focus")
        )

        self.terminal.focusLost.connect(
            lambda: self.event_log.log_event("FOCUS", "focusLost", "Terminal lost focus")
        )

        # === APPEARANCE EVENTS ===
        self.terminal.sizeChanged.connect(
            lambda rows, cols: self.event_log.log_event(
                "APPEARANCE", "sizeChanged", f"New size: {rows}x{cols}"
            )
        )

        self.terminal.titleChanged.connect(
            lambda title: self.event_log.log_event("APPEARANCE", "titleChanged", f"Title: {title}")
        )

        self.terminal.bellActivated.connect(
            lambda: self.event_log.log_event("APPEARANCE", "bellActivated", "Terminal bell rang!")
        )

        self.terminal.scrollOccurred.connect(
            lambda pos: self.event_log.log_event(
                "APPEARANCE", "scrollOccurred", f"Scroll position: {pos}"
            )
        )

    def _handle_process_started(self, event: ProcessEvent):
        """Handle process started event with structured data."""
        details = f"Command: {event.command}"
        if event.pid:
            details += f", PID: {event.pid}"
        if event.working_directory:
            details += f", CWD: {event.working_directory}"
        details += f", Time: {event.timestamp.strftime('%H:%M:%S')}"

        self.event_log.log_event("PROCESS", "processStarted", details)

    def _handle_key_pressed(self, event: KeyEvent):
        """Handle key press event with structured data."""
        modifiers = []
        if event.ctrl:
            modifiers.append("Ctrl")
        if event.alt:
            modifiers.append("Alt")
        if event.shift:
            modifiers.append("Shift")

        mod_str = "+".join(modifiers)
        if mod_str:
            key_combo = f"{mod_str}+{event.key}"
        else:
            key_combo = event.key

        # Only log interesting keys to avoid spam
        if len(event.key) > 1 or modifiers:  # Special keys or with modifiers
            details = f"Key: {key_combo} (code: {event.code})"
            self.event_log.log_event("INTERACTION", "keyPressed", details)

    def _handle_selection_changed(self, text: str):
        """Handle selection change event."""
        if text:
            preview = text[:30].replace("\n", "\\n")
            if len(text) > 30:
                preview += "..."
            details = f"Selected {len(text)} chars: '{preview}'"
        else:
            details = "Selection cleared"

        self.event_log.log_event("INTERACTION", "selectionChanged", details)

    def _handle_context_menu(self, event: ContextMenuEvent):
        """Handle context menu request with structured data and create custom menu."""
        details = f"Position: ({event.position.x()}, {event.position.y()})"
        if event.selected_text:
            details += f", Selected: '{event.selected_text[:20]}...'"

        self.event_log.log_event("INTERACTION", "contextMenuRequested", details)

        # Create custom context menu
        menu = QMenu(self)

        if event.selected_text:
            # Add action for selected text
            search_action = QAction(f"🔍 Demo: Search '{event.selected_text[:15]}...'", menu)
            search_action.triggered.connect(
                lambda: self.event_log.log_event(
                    "DEMO", "customAction", f"Search requested for: {event.selected_text}"
                )
            )
            menu.addAction(search_action)

            # Add action to process selection
            process_action = QAction("⚡ Demo: Process Selection", menu)
            process_action.triggered.connect(
                lambda: self.event_log.log_event(
                    "DEMO", "customAction", "Custom processing of selected text"
                )
            )
            menu.addAction(process_action)

            menu.addSeparator()

        # Add demo actions
        demo_action = QAction("🎪 This is a Custom Context Menu!", menu)
        demo_action.triggered.connect(
            lambda: self.event_log.log_event(
                "DEMO", "customAction", "Custom context menu action triggered"
            )
        )
        menu.addAction(demo_action)

        # Show menu at global position
        if event.global_position:
            menu.exec(event.global_position)
        else:
            # Fallback to mapping position
            global_pos = self.terminal.mapToGlobal(event.position)
            menu.exec(global_pos)

    def _setup_demo_commands(self):
        """Set up automatic demo commands."""

        def send_demo_commands():
            """Send some demo commands to trigger events."""
            self.event_log.log_event("DEMO", "autoCommands", "Starting automatic demo commands")

            # Send various commands to demonstrate events
            commands = [
                ("echo 'Welcome to the Modern Event System Demo!'", 1000),
                ("echo 'Try these interactions:'", 2000),
                ("echo '- Type some text to see keyPressed events'", 3000),
                ("echo '- Select text to see selectionChanged events'", 4000),
                ("echo '- Right-click to see contextMenuRequested events'", 5000),
                ("echo '- Click in/out of terminal for focus events'", 6000),
                ("echo '- Resize window for sizeChanged events'", 7000),
                ("pwd", 8000),
                ("echo 'Event categories can be configured individually'", 9000),
                ("date", 10000),
            ]

            for command, delay in commands:
                QTimer.singleShot(delay, lambda cmd=command: self.terminal.send_command(cmd))

        # Start demo commands after terminal is ready
        self.terminal.terminalReady.connect(lambda: QTimer.singleShot(2000, send_demo_commands))

    def closeEvent(self, event):
        """Handle window close."""
        self.event_log.log_event("DEMO", "shutdown", "Demo window closing")
        self.terminal.close_terminal()
        super().closeEvent(event)


def main():
    """Run the modern events demo."""
    app = QApplication(sys.argv)
    app.setApplicationName("Modern Terminal Events Demo")

    # Create and show demo window
    demo = ModernEventsDemo()
    demo.show()

    print("\n" + "=" * 60)
    print("🎪 MODERN TERMINAL EVENT SYSTEM DEMO")
    print("=" * 60)
    print("📖 This demo shows the new Qt-compliant event system")
    print("🎯 Try these interactions:")
    print("   • Type in the terminal (keyPressed events)")
    print("   • Select text (selectionChanged events)")
    print("   • Right-click (contextMenuRequested events)")
    print("   • Click in/out of terminal (focus events)")
    print("   • Resize the window (sizeChanged events)")
    print("📊 Watch the event log above the terminal!")
    print("=" * 60)

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
