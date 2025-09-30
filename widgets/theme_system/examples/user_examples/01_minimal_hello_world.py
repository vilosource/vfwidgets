#!/usr/bin/env python3
"""
Example 01: Minimal Hello World
================================

The absolute simplest way to create a themed Qt application.
Just 10 lines of code to get a themed widget!

What this demonstrates:
- Creating a themed application
- Creating a themed widget
- Automatic theme application
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from PySide6.QtWidgets import QLabel
from vfwidgets_theme import ThemedWidget, ThemedApplication


class HelloWidget(ThemedWidget, QLabel):
    """A simple label that gets themed automatically."""

    def __init__(self):
        super().__init__()
        self.setText("Hello, Themed World!")
        self.setMinimumSize(300, 100)


def main():
    app = ThemedApplication(sys.argv)

    widget = HelloWidget()
    widget.show()

    return app.exec()


if __name__ == '__main__':
    sys.exit(main())