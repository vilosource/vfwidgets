#!/usr/bin/env python3
"""
Example 02: Buttons and Layout
================================

Demonstrates themed buttons with layouts and interactions.

What this demonstrates:
- ThemedMainWindow for application windows
- Multiple themed widgets in layouts
- Button click handlers
- How themes apply to different widget types
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from vfwidgets_theme import ThemedApplication, ThemedMainWindow, ThemedQWidget


class ButtonDemoWindow(ThemedMainWindow):
    """Main window demonstrating themed buttons and layouts."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Themed Buttons Demo")
        self.setMinimumSize(500, 350)
        self.click_count = 0
        self.setup_ui()

    def setup_ui(self):
        # Create central widget
        central = ThemedQWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title = QLabel("Themed Buttons Demo")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # Status label
        self.status_label = QLabel("Click any button below!")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Button row 1
        button_row1 = QHBoxLayout()
        button_row1.setSpacing(10)

        btn_primary = QPushButton("Primary Action")
        btn_primary.setMinimumHeight(40)
        btn_primary.clicked.connect(lambda: self.on_button_click("Primary"))
        button_row1.addWidget(btn_primary)

        btn_secondary = QPushButton("Secondary Action")
        btn_secondary.setMinimumHeight(40)
        btn_secondary.clicked.connect(lambda: self.on_button_click("Secondary"))
        button_row1.addWidget(btn_secondary)

        layout.addLayout(button_row1)

        # Button row 2
        button_row2 = QHBoxLayout()
        button_row2.setSpacing(10)

        btn_success = QPushButton("Success")
        btn_success.setMinimumHeight(40)
        btn_success.setStyleSheet("background-color: #28a745; color: white;")
        btn_success.clicked.connect(lambda: self.on_button_click("Success"))
        button_row2.addWidget(btn_success)

        btn_danger = QPushButton("Danger")
        btn_danger.setMinimumHeight(40)
        btn_danger.setStyleSheet("background-color: #dc3545; color: white;")
        btn_danger.clicked.connect(lambda: self.on_button_click("Danger"))
        button_row2.addWidget(btn_danger)

        btn_info = QPushButton("Info")
        btn_info.setMinimumHeight(40)
        btn_info.setStyleSheet("background-color: #17a2b8; color: white;")
        btn_info.clicked.connect(lambda: self.on_button_click("Info"))
        button_row2.addWidget(btn_info)

        layout.addLayout(button_row2)

        # Reset button
        btn_reset = QPushButton("Reset Counter")
        btn_reset.setMinimumHeight(40)
        btn_reset.clicked.connect(self.reset_counter)
        layout.addWidget(btn_reset)

        # Add stretch to push everything up
        layout.addStretch()

        # Footer
        footer = QLabel("All buttons are themed automatically!")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("font-size: 11px; color: #888;")
        layout.addWidget(footer)

    def on_button_click(self, button_name):
        """Handle button clicks."""
        self.click_count += 1
        self.status_label.setText(
            f"You clicked '{button_name}' button! (Total clicks: {self.click_count})"
        )

    def reset_counter(self):
        """Reset the click counter."""
        self.click_count = 0
        self.status_label.setText("Counter reset! Click any button below!")


def main():
    app = ThemedApplication(sys.argv)

    window = ButtonDemoWindow()
    window.show()

    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
