#!/usr/bin/env python3
"""Basic usage example for ButtonWidget."""

import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from vfwidgets_button import ButtonWidget


def main():
    """Run the example application."""
    app = QApplication(sys.argv)

    # Create main window
    window = QMainWindow()
    window.setWindowTitle("ButtonWidget Example")
    window.resize(400, 300)

    # Create central widget
    central_widget = QWidget()
    window.setCentralWidget(central_widget)

    # Create layout
    layout = QVBoxLayout(central_widget)

    # Create and add our custom widget
    custom_widget = ButtonWidget()
    layout.addWidget(custom_widget)

    # Connect signals
    custom_widget.value_changed.connect(lambda v: print(f"Value changed: {v}"))

    # Show window
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
