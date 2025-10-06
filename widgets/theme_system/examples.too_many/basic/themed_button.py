#!/usr/bin/env python3
"""themed_button.py - Simple themed button example.

Shows how to create a button that responds to theme changes.
This demonstrates the basics of using ThemedWidget for a simple button.

Key Concepts:
- Inheriting from ThemedWidget
- Using theme_config to map theme properties
- Responding to theme changes
- Using theme properties in styling

Example usage:
    python themed_button.py
"""

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from vfwidgets_theme import ThemedApplication, ThemedWidget


class ThemedButton(ThemedWidget, QPushButton):
    """A themed button that changes appearance based on the current theme."""

    # Map theme properties to semantic names
    theme_config = {
        "bg": "button.background",
        "fg": "button.foreground",
        "border": "button.border",
        "hover_bg": "button.hover.background",
        "hover_fg": "button.hover.foreground",
        "pressed_bg": "button.pressed.background",
        "font": "button.font",
    }

    def __init__(self, text="Themed Button", parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setMinimumSize(120, 40)

        # Apply initial styling
        self.update_styling()

    def on_theme_changed(self):
        """Called automatically when theme changes."""
        self.update_styling()

    def update_styling(self):
        """Update button styling based on current theme."""
        # Get theme colors with fallbacks
        bg_color = self.theme.get("bg", "#e0e0e0")
        fg_color = self.theme.get("fg", "#000000")
        border_color = self.theme.get("border", "#cccccc")
        hover_bg = self.theme.get("hover_bg", "#d0d0d0")
        hover_fg = self.theme.get("hover_fg", "#000000")
        pressed_bg = self.theme.get("pressed_bg", "#c0c0c0")
        font = self.theme.get("font", "Arial, sans-serif")

        # Generate stylesheet
        stylesheet = f"""
        QPushButton {{
            background-color: {bg_color};
            color: {fg_color};
            border: 2px solid {border_color};
            border-radius: 5px;
            font-family: {font};
            font-size: 12px;
            padding: 8px 16px;
        }}

        QPushButton:hover {{
            background-color: {hover_bg};
            color: {hover_fg};
        }}

        QPushButton:pressed {{
            background-color: {pressed_bg};
        }}
        """

        self.setStyleSheet(stylesheet)


class ButtonDemo(ThemedWidget):
    """Demo window showing themed buttons."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Themed Button Demo")
        self.setMinimumSize(400, 300)

        # Create layout
        layout = QVBoxLayout(self)

        # Add title
        title = QLabel("Themed Button Examples")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Create buttons
        buttons = [
            ThemedButton("Primary Button"),
            ThemedButton("Secondary Button"),
            ThemedButton("Action Button"),
        ]

        # Add buttons to layout
        for button in buttons:
            layout.addWidget(button)

        # Add theme switcher
        theme_layout = QHBoxLayout()

        # Light theme button
        light_btn = ThemedButton("Light Theme")
        light_btn.clicked.connect(lambda: self.switch_theme("light"))
        theme_layout.addWidget(light_btn)

        # Dark theme button
        dark_btn = ThemedButton("Dark Theme")
        dark_btn.clicked.connect(lambda: self.switch_theme("dark"))
        theme_layout.addWidget(dark_btn)

        layout.addLayout(theme_layout)
        layout.addStretch()

    def switch_theme(self, theme_name):
        """Switch to a different theme."""
        app = ThemedApplication.instance()
        if app:
            try:
                app.set_theme(theme_name)
                print(f"Switched to {theme_name} theme")
            except Exception as e:
                print(f"Could not switch to {theme_name} theme: {e}")


def main():
    """Run the themed button demo."""
    # Create themed application
    app = ThemedApplication(sys.argv)

    # Register basic themes
    light_theme = {
        "name": "light",
        "button": {
            "background": "#f0f0f0",
            "foreground": "#333333",
            "border": "#cccccc",
            "hover": {"background": "#e0e0e0", "foreground": "#000000"},
            "pressed": {"background": "#d0d0d0"},
            "font": "Arial, sans-serif",
        },
    }

    dark_theme = {
        "name": "dark",
        "button": {
            "background": "#555555",
            "foreground": "#ffffff",
            "border": "#777777",
            "hover": {"background": "#666666", "foreground": "#ffffff"},
            "pressed": {"background": "#444444"},
            "font": "Arial, sans-serif",
        },
    }

    # Register themes with application
    app.register_theme("light", light_theme)
    app.register_theme("dark", dark_theme)

    # Set initial theme
    app.set_theme("light")

    # Create and show demo
    demo = ButtonDemo()
    demo.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
