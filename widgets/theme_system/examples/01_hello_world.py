#!/usr/bin/env python3
"""Example 01: Hello World - The Simplest Themed App
=====================================================

The absolute simplest themed Qt application - just 20 lines!

What you'll learn:
- How to create a ThemedApplication
- How to use ThemedMainWindow for automatic theming
- Zero-configuration theming (no setup required!)

Key concepts:
- ThemedApplication: Drop-in replacement for QApplication
- ThemedMainWindow: Automatically themed main window
- All child widgets are themed automatically

Run:
    python examples/01_hello_world.py
"""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout

from vfwidgets_theme import ThemedApplication, ThemedMainWindow, ThemedQWidget


class HelloWindow(ThemedMainWindow):
    """A simple themed main window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hello VFWidgets Theme System!")
        self.setMinimumSize(500, 300)

        # Create central widget
        central = ThemedQWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)

        # Add a welcoming label - automatically themed!
        welcome = QLabel("🎨 Welcome to VFWidgets Theme System 2.0!")
        welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome.setStyleSheet("font-size: 18px; font-weight: bold; padding: 20px;")
        layout.addWidget(welcome)

        # Add description
        description = QLabel(
            "This window and all its child widgets are automatically themed.\n\n"
            "No configuration required!\n"
            "No manual stylesheet writing!\n"
            "Just inherit from ThemedMainWindow and you're done."
        )
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)
        layout.addWidget(description)

        layout.addStretch()


def main():
    """Main entry point."""
    # 1. Create ThemedApplication (instead of QApplication)
    app = ThemedApplication(sys.argv)

    # 2. Create your window (using ThemedMainWindow)
    window = HelloWindow()
    window.show()

    # 3. Run the app
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
