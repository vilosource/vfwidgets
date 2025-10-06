#!/usr/bin/env python3
"""
Simple Terminal Example (Embedded Mode)

This example shows the simplest way to use TerminalWidget.
The widget creates its own embedded server automatically.

Usage: python 01_simple_terminal.py
"""

import sys

# Add parent directory to path for development
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMainWindow

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vfwidgets_terminal import TerminalWidget


class SimpleTerminalWindow(QMainWindow):
    """Simple window with a single terminal."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Terminal (Embedded Mode)")
        self.resize(800, 600)

        # Create terminal - it will create its own embedded server
        self.terminal = TerminalWidget()
        self.setCentralWidget(self.terminal)


def main():
    app = QApplication(sys.argv)
    window = SimpleTerminalWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
