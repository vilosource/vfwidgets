#!/usr/bin/env python3
"""
Example 01: Hello World
========================

The simplest possible themed Qt application.
Just a few lines to get a themed widget running!

What this demonstrates:
- Creating a themed application
- Using ThemedQWidget for simple single inheritance
- Automatic theme application with zero configuration
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from vfwidgets_theme import ThemedApplication, ThemedQWidget


class HelloWidget(ThemedQWidget):
    """A simple themed widget displaying 'Hello World'."""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        # Create a label as the central content
        from PySide6.QtWidgets import QVBoxLayout
        layout = QVBoxLayout(self)

        label = QLabel("Hello, Themed World!")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 24px; font-weight: bold;")

        layout.addWidget(label)

        self.setMinimumSize(400, 200)
        self.setWindowTitle("Hello World - VFWidgets Theme System")


def main():
    app = ThemedApplication(sys.argv)

    widget = HelloWidget()
    widget.show()

    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
