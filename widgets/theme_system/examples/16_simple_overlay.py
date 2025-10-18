#!/usr/bin/env python3
"""Example 16: Simple Theme Overlay - Runtime Color Customization

This example demonstrates the simplest use of the Theme Overlay System (v2.0.0):
- Setting app-level color overrides at runtime
- No QApplication subclassing required
- Immediate visual feedback

The overlay system allows you to customize colors without modifying theme files.

Usage:
    python examples/16_simple_overlay.py
"""

import sys

from PySide6.QtWidgets import QLabel, QPushButton, QTextEdit, QVBoxLayout

from vfwidgets_theme import ThemedApplication, ThemedWidget
from vfwidgets_theme.core.manager import ThemeManager


class SimpleOverlayDemo(ThemedWidget):
    """Demo widget showing simple overlay usage."""

    theme_config = {
        "background": "editor.background",
        "foreground": "editor.foreground",
    }

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Theme Overlay System - Simple Example")
        title.setStyleSheet("font-size: 18pt; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        # Description
        desc = QLabel(
            "This demo shows how to override colors at runtime without modifying theme files.\n"
            "Click the buttons below to change the editor background color."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("padding: 10px;")
        layout.addWidget(desc)

        # Editor (demonstrates background override)
        self.editor = QTextEdit()
        self.editor.setPlainText(
            "# This is a sample text editor\n"
            "# The background color changes when you click the buttons below\n\n"
            "def hello_world():\n"
            '    print("Hello from the Theme Overlay System!")\n\n'
            "hello_world()"
        )
        self.editor.setMinimumHeight(200)
        layout.addWidget(self.editor)

        # Control buttons
        controls_layout = QVBoxLayout()

        btn_purple = QPushButton("Set Purple Background")
        btn_purple.clicked.connect(lambda: self.set_override("editor.background", "#2e1a47"))
        controls_layout.addWidget(btn_purple)

        btn_blue = QPushButton("Set Blue Background")
        btn_blue.clicked.connect(lambda: self.set_override("editor.background", "#1e2a47"))
        controls_layout.addWidget(btn_blue)

        btn_green = QPushButton("Set Green Background")
        btn_green.clicked.connect(lambda: self.set_override("editor.background", "#1a2e1a"))
        controls_layout.addWidget(btn_green)

        btn_reset = QPushButton("Reset to Theme Default")
        btn_reset.clicked.connect(self.clear_override)
        controls_layout.addWidget(btn_reset)

        layout.addLayout(controls_layout)

        # Status label
        self.status_label = QLabel("Using theme default colors")
        self.status_label.setStyleSheet("padding: 10px; font-style: italic;")
        layout.addWidget(self.status_label)

    def set_override(self, token: str, color: str):
        """Set a color override."""
        manager = ThemeManager.get_instance()
        manager.set_app_override(token, color)
        self.status_label.setText(f"Override set: {token} = {color}")

    def clear_override(self):
        """Clear color override."""
        manager = ThemeManager.get_instance()
        manager.remove_app_override("editor.background")
        self.status_label.setText("Using theme default colors")


def main():
    """Main entry point."""
    # Create application
    app = ThemedApplication(sys.argv)

    # Load a theme (optional - defaults to system theme)
    app.set_theme("dark")

    # Create and show main window
    window = SimpleOverlayDemo()
    window.setWindowTitle("Example 16: Simple Theme Overlay")
    window.resize(600, 500)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
