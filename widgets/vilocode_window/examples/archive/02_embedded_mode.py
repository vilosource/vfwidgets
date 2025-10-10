#!/usr/bin/env python3
"""Example showing ViloCodeWindow in embedded mode.

This example demonstrates using ViloCodeWindow as an embedded widget
inside another parent widget.
"""

import sys

from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget

from vfwidgets_vilocode_window import ViloCodeWindow


def main():
    """Create a main window with embedded ViloCodeWindow."""
    app = QApplication(sys.argv)

    # Create main window
    main_window = QMainWindow()
    main_window.setWindowTitle("ViloCodeWindow - Embedded Mode Example")
    main_window.resize(1400, 900)

    # Central widget
    central_widget = QWidget()
    main_window.setCentralWidget(central_widget)

    layout = QVBoxLayout(central_widget)
    layout.setContentsMargins(10, 10, 10, 10)

    # Add label
    label = QLabel("This is a main window with ViloCodeWindow embedded below:")
    layout.addWidget(label)

    # Create embedded ViloCodeWindow (has parent, so embedded mode)
    vilocode = ViloCodeWindow(parent=central_widget)
    vilocode.set_status_message("ViloCodeWindow in embedded mode (no frameless window)")
    layout.addWidget(vilocode)

    main_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
