#!/usr/bin/env python3
"""Example demonstrating status bar API.

Shows how to use the status bar API to display messages and control visibility.
"""

import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from vfwidgets_vilocode_window import ViloCodeWindow


def main():
    """Create window with status bar demonstration."""
    app = QApplication(sys.argv)

    window = ViloCodeWindow()
    window.setWindowTitle("ViloCodeWindow - Status Bar Demo")
    window.resize(1200, 800)

    # Get the main pane area and add controls
    # For now, we'll just use the status bar API
    window.set_status_message("Welcome to ViloCodeWindow!", 2000)

    # Create a timer to update status messages
    messages = [
        "Status bar API working...",
        "set_status_message() - displays messages",
        "get_status_bar() - returns QStatusBar",
        "set_status_bar_visible() - show/hide",
        "is_status_bar_visible() - check visibility",
    ]

    current_msg = [0]

    def update_message():
        window.set_status_message(messages[current_msg[0] % len(messages)])
        current_msg[0] += 1

    timer = QTimer()
    timer.timeout.connect(update_message)
    timer.start(3000)  # Update every 3 seconds

    # Show initial status
    print("=" * 60)
    print("ViloCodeWindow Status Bar Demo")
    print("=" * 60)
    print(f"Status bar visible: {window.is_status_bar_visible()}")
    print(f"Status bar type: {type(window.get_status_bar()).__name__}")
    print("\nStatus messages will rotate every 3 seconds...")
    print("Close the window to exit.")
    print("=" * 60)

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
