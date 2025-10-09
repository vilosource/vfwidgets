#!/usr/bin/env python3
"""Basic example showing a frameless ViloCodeWindow.

This example demonstrates the simplest usage of ViloCodeWindow,
showing the frameless window with placeholder components.
"""

import sys

from PySide6.QtWidgets import QApplication

from vfwidgets_vilocode_window import ViloCodeWindow


def main():
    """Create and show a basic frameless window."""
    app = QApplication(sys.argv)

    # Create the window (automatically detects frameless mode)
    window = ViloCodeWindow()
    window.setWindowTitle("ViloCodeWindow - Basic Example")
    window.resize(1200, 800)

    # Update status bar message
    window.set_status_message("ViloCodeWindow Phase 1 - Frameless mode active")

    # Show the window
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
