#!/usr/bin/env python3
"""Basic terminal widget usage example.

This example demonstrates the simplest way to use the TerminalWidget.
It creates a single terminal window with default settings.
"""

import sys

from PySide6.QtWidgets import QApplication, QMainWindow
from vfwidgets_terminal import TerminalWidget


def main():
    """Run the basic terminal example."""
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("VFWidgets Terminal - Basic Example")

    # Create main window
    window = QMainWindow()
    window.setWindowTitle("Terminal Widget - Basic Usage")
    window.setGeometry(100, 100, 800, 600)

    # Create terminal widget with default settings
    terminal = TerminalWidget()

    # Connect signals to see events
    terminal.terminal_ready.connect(lambda: print("✅ Terminal is ready!"))
    terminal.command_started.connect(lambda cmd: print(f"▶️  Command started: {cmd}"))
    terminal.terminal_closed.connect(lambda code: print(f"🔚 Terminal closed with code: {code}"))

    # Set terminal as central widget
    window.setCentralWidget(terminal)

    # Show window
    window.show()

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
