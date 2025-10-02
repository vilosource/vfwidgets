#!/usr/bin/env python3
"""Example 06: New API - Simplified Usage.
=======================================

Demonstrates the new simplified API with convenience classes and smart defaults.

Key improvements:
- ThemedMainWindow and ThemedQWidget for simple single inheritance use cases
- ThemedWidget for flexible multiple inheritance when needed (e.g., with QPushButton)
- Smart property defaults (no more getattr everywhere)
- Clearer intent
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout

from vfwidgets_theme import ThemedApplication, ThemedMainWindow, ThemedQWidget, ThemedWidget


class SimpleThemedButton(ThemedWidget, QPushButton):
    """A simple themed button using ThemedWidget for flexible inheritance."""

    theme_config = {"bg": "colors.primary", "fg": "colors.background", "hover_bg": "colors.accent"}

    def __init__(self, text="Click Me"):
        super().__init__()
        self.setText(text)
        self.setMinimumSize(120, 40)
        self.update_styling()

    def update_styling(self):
        # Clean property access with smart defaults!
        bg = self.theme.bg
        fg = self.theme.fg
        hover_bg = self.theme.hover_bg

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {fg};
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover_bg};
            }}
        """)

    def on_theme_changed(self):
        """Called automatically when theme changes."""
        self.update_styling()


class SimpleWindow(ThemedMainWindow):
    """Main window using new API - single inheritance from ThemedMainWindow!"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("New API Example")
        self.setMinimumSize(400, 300)
        self.setup_ui()

    def setup_ui(self):
        # Create central widget
        central = ThemedQWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignCenter)

        # Title
        title = QLabel("New Simplified API")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Description
        desc = QLabel(
            "This example uses:\n"
            "• ThemedMainWindow for the window\n"
            "• ThemedQWidget for simple widgets\n"
            "• ThemedWidget for flexible inheritance (button)\n"
            "• Smart property defaults (no getattr!)"
        )
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)

        # Button
        button = SimpleThemedButton("Themed Button")
        layout.addWidget(button)


def main():
    app = ThemedApplication(sys.argv)

    # Set a theme
    app.set_theme("dark")

    # Create and show window
    window = SimpleWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
