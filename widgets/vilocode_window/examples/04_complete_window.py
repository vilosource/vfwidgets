#!/usr/bin/env python3
"""Complete example showing all ViloCodeWindow features.

This example demonstrates:
- Frameless window with custom title bar
- Working window controls (minimize, maximize, close)
- Draggable title bar
- Double-click to maximize
- VS Code-style layout with all components
- Status bar with messages
- Window title display
"""

import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from vfwidgets_vilocode_window import ViloCodeWindow


def main():
    """Create and show a complete ViloCodeWindow."""
    app = QApplication(sys.argv)

    # Create the window
    window = ViloCodeWindow()
    window.setWindowTitle("ViloCodeWindow - Complete Demo")
    window.resize(1200, 800)

    # Set up status bar messages
    messages = [
        "✓ Frameless window with custom title bar",
        "✓ Drag title bar to move window",
        "✓ Double-click title bar to maximize",
        "✓ Click minimize/maximize/close buttons",
        "✓ VS Code-style layout active",
        "✓ Status bar showing dynamic messages",
    ]

    current_msg = [0]

    def update_status():
        window.set_status_message(messages[current_msg[0] % len(messages)])
        current_msg[0] += 1

    # Update status every 2 seconds
    timer = QTimer()
    timer.timeout.connect(update_status)
    timer.start(2000)

    # Initial message
    window.set_status_message("Welcome to ViloCodeWindow! Drag the title bar to move.")

    # Show information
    print("=" * 70)
    print("ViloCodeWindow - Complete Demo")
    print("=" * 70)
    print()
    print("Features demonstrated:")
    print("  • Frameless window with custom title bar")
    print("  • Working window controls (minimize, maximize, close)")
    print("  • Draggable title bar (click and drag)")
    print("  • Double-click title bar to maximize/restore")
    print("  • VS Code-style layout (activity bar, sidebar, main pane, status bar)")
    print("  • Dynamic status bar messages")
    print()
    print("Try these actions:")
    print("  1. Drag the title bar to move the window")
    print("  2. Double-click the title bar to maximize")
    print("  3. Click the minimize button (−)")
    print("  4. Click the maximize button (□)")
    print("  5. Click the close button (✕) to exit")
    print()
    print("The status bar message will change every 2 seconds.")
    print("=" * 70)

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
