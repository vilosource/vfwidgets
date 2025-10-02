#!/usr/bin/env python3
"""
Example 02: Theme Switching
============================

Shows how to switch between themes dynamically.
Users can select themes from a dropdown and see instant updates.

What this demonstrates:
- Listing available themes
- Switching themes at runtime
- Responding to theme changes in widgets
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QFrame, QLabel, QPushButton, QVBoxLayout, QWidget

from vfwidgets_theme import ThemedApplication, ThemedWidget


class ThemeSwitcherWidget(ThemedWidget, QWidget):
    """A widget that allows switching themes and shows the current theme."""

    # Map semantic names to theme properties
    theme_config = {
        'background': 'colors.background',
        'foreground': 'colors.foreground',
        'primary': 'colors.primary',
        'accent': 'colors.accent'
    }

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.update_styling()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Title
        self.title = QLabel("Theme Switcher Demo")
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)

        # Current theme display
        self.theme_info = QLabel()
        self.theme_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.theme_info)

        # Theme selector
        self.theme_selector = QComboBox()
        app = ThemedApplication.instance()
        if app:
            self.theme_selector.addItems(app.available_themes)
            self.theme_selector.currentTextChanged.connect(self.switch_theme)
        layout.addWidget(self.theme_selector)

        # Sample content
        self.content_frame = QFrame()
        self.content_frame.setFrameStyle(QFrame.Box)
        content_layout = QVBoxLayout(self.content_frame)

        self.sample_label = QLabel("This is sample text that changes with the theme")
        content_layout.addWidget(self.sample_label)

        self.sample_button = QPushButton("Sample Button")
        content_layout.addWidget(self.sample_button)

        layout.addWidget(self.content_frame)

        # Set minimum size
        self.setMinimumSize(400, 300)

    def switch_theme(self, theme_name):
        """Switch to the selected theme."""
        app = ThemedApplication.instance()
        if app:
            app.set_theme(theme_name)

    def on_theme_changed(self):
        """Called automatically when theme changes."""
        self.update_styling()
        self.update_info()

    def update_info(self):
        """Update the theme info display."""
        app = ThemedApplication.instance()
        if app:
            theme_name = app.current_theme_name
            theme_type = app.theme_type
            self.theme_info.setText(f"Current Theme: {theme_name} ({theme_type})")

    def update_styling(self):
        """Apply theme colors to the widget."""
        # Access theme properties through our mapping
        bg = getattr(self.theme, 'background', '#ffffff')
        fg = getattr(self.theme, 'foreground', '#000000')
        primary = getattr(self.theme, 'primary', '#0066cc')

        # Apply styles
        self.setStyleSheet(f"""
            ThemeSwitcherWidget {{
                background-color: {bg};
                color: {fg};
            }}
            QLabel {{
                color: {fg};
                font-size: 14px;
            }}
            QLabel#title {{
                font-size: 18px;
                font-weight: bold;
                color: {primary};
            }}
            QComboBox {{
                padding: 5px;
                background-color: {bg};
                color: {fg};
                border: 1px solid {primary};
            }}
            QPushButton {{
                padding: 8px;
                background-color: {primary};
                color: {bg};
                border: none;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {fg};
            }}
        """)

        # Set object name for title styling
        self.title.setObjectName("title")


def main():
    app = ThemedApplication(sys.argv)

    # Start with light theme
    app.set_theme('light')

    widget = ThemeSwitcherWidget()
    widget.setWindowTitle("Theme Switching Example")
    widget.show()

    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
