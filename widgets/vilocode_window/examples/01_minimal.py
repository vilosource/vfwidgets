#!/usr/bin/env python3
"""Minimal ViloCodeWindow Example - Hello World

This is the simplest possible ViloCodeWindow usage.
Just create a window, add content, and show it.

What you'll learn:
- Creating a ViloCodeWindow instance
- Setting main content with set_main_content()
- Displaying a status message
- Showing the window

Run this example:
    python examples/01_minimal.py
"""

import sys

from PySide6.QtWidgets import QApplication, QTextEdit

from vfwidgets_vilocode_window import ViloCodeWindow


def main() -> None:
    """Create a minimal ViloCodeWindow."""
    app = QApplication(sys.argv)

    # Create the window
    window = ViloCodeWindow()
    window.setWindowTitle("ViloCodeWindow - Minimal Example")
    window.resize(1000, 600)

    # Add main content - any QWidget works
    editor = QTextEdit()
    editor.setPlainText(
        """Welcome to ViloCodeWindow!

This is the simplest example showing:
✓ Creating a ViloCodeWindow
✓ Adding main content with set_main_content()
✓ Setting a status message
✓ Automatic frameless window detection

The window automatically provides:
- Frameless window with custom title bar (when no parent)
- Draggable title bar
- Minimize/maximize/close buttons
- Status bar at the bottom
- VS Code Dark+ styling (when vfwidgets-theme available)

Try:
1. Drag the title bar to move the window
2. Double-click the title bar to maximize
3. Click the window control buttons
"""
    )
    window.set_main_content(editor)

    # Set status bar message
    window.set_status_message("Hello from ViloCodeWindow! Press Ctrl+B to toggle sidebar")

    # Show and run
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
