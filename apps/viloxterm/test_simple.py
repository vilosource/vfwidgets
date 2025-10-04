#!/usr/bin/env python3
"""Test simple ViloxTerm setup matching 04_themed_chrome_tabs.py structure."""

import sys
import logging

from PySide6.QtWidgets import QTextEdit

from vfwidgets_theme import ThemedApplication
from chrome_tabbed_window import ChromeTabbedWindow

logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s")
logger = logging.getLogger(__name__)


def main():
    # Create themed application
    app = ThemedApplication(sys.argv)
    app.set_theme("dark")

    # Create chrome tabbed window - EXACTLY like the working example
    window = ChromeTabbedWindow()
    window.setWindowTitle("ViloxTerm Simple Test")
    window.resize(1200, 800)

    # Check if window controls exist
    logger.info(f"Window has _window_controls: {hasattr(window, '_window_controls')}")
    if hasattr(window, "_window_controls"):
        logger.info(f"Window controls value: {window._window_controls}")
        logger.info(f"Window mode: {window._window_mode}")
        if window._window_controls:
            logger.info(f"Window controls layout: {window._window_controls.layout()}")

    # Add simple tabs
    for i in range(1, 3):
        editor = QTextEdit()
        editor.setPlaceholderText(f"Terminal {i}")
        window.addTab(editor, f"Terminal {i}")

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
