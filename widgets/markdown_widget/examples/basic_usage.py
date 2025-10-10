#!/usr/bin/env python3
"""Basic usage example for MarkdownViewerWidget."""

import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from vfwidgets_markdown import MarkdownViewer


def main():
    """Run the example application."""
    app = QApplication(sys.argv)

    # Create main window
    window = QMainWindow()
    window.setWindowTitle("MarkdownViewer Example")
    window.resize(400, 300)

    # Create central widget
    central_widget = QWidget()
    window.setCentralWidget(central_widget)

    # Create layout
    layout = QVBoxLayout(central_widget)

    # Create and add markdown viewer widget
    viewer = MarkdownViewer()
    layout.addWidget(viewer)

    # Set some example markdown content
    viewer.set_markdown("# Hello World\n\nThis is **markdown** with *formatting*!")

    # Show window
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
