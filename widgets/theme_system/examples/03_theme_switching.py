#!/usr/bin/env python3
"""
Example 03: Theme Switching
=============================

Demonstrates dynamic theme switching at runtime.

What this demonstrates:
- Listing available themes
- Switching themes dynamically
- Theme changes propagate to all widgets
- Using the VS Code theme
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QGroupBox, QLabel, QPushButton, QVBoxLayout

from vfwidgets_theme import ThemedApplication, ThemedMainWindow, ThemedQWidget


class ThemeSwitcherWindow(ThemedMainWindow):
    """Main window demonstrating theme switching."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Theme Switching Demo")
        self.setMinimumSize(600, 450)
        self.setup_ui()

    def setup_ui(self):
        # Create central widget
        central = ThemedQWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title = QLabel("Theme Switching Demo")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(title)

        # Theme selector group
        theme_group = QGroupBox("Select Theme")
        theme_layout = QVBoxLayout()

        # Get app instance to access themes
        app = ThemedApplication.instance()

        # Theme dropdown
        theme_label = QLabel("Available Themes:")
        theme_layout.addWidget(theme_label)

        self.theme_combo = QComboBox()
        self.theme_combo.setMinimumHeight(32)

        # Get available themes
        if app:
            themes = app.available_themes
            self.theme_combo.addItems(themes)

            # Set current theme in combo box
            current = app.current_theme_name
            if hasattr(current, 'name'):
                current = current.name
            elif not isinstance(current, str):
                current = str(current)

            index = self.theme_combo.findText(current)
            if index >= 0:
                self.theme_combo.setCurrentIndex(index)

        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        theme_layout.addWidget(self.theme_combo)

        # Theme info
        info_label = QLabel(
            "Try switching themes:\n"
            "• default - Standard light theme\n"
            "• dark - Dark theme\n"
            "• light - High contrast light\n"
            "• vscode - VS Code Dark+ inspired\n"
            "• minimal - Fallback theme"
        )
        info_label.setStyleSheet("font-size: 11px;")
        theme_layout.addWidget(info_label)

        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)

        # Demo widgets group
        demo_group = QGroupBox("Theme Preview")
        demo_layout = QVBoxLayout()

        # Some widgets to show theming
        btn1 = QPushButton("Sample Button 1")
        btn1.setMinimumHeight(36)
        demo_layout.addWidget(btn1)

        btn2 = QPushButton("Sample Button 2")
        btn2.setMinimumHeight(36)
        demo_layout.addWidget(btn2)

        sample_label = QLabel("This text changes with the theme too!")
        sample_label.setAlignment(Qt.AlignCenter)
        demo_layout.addWidget(sample_label)

        demo_group.setLayout(demo_layout)
        layout.addWidget(demo_group)

        # Current theme display
        self.current_theme_label = QLabel()
        self.current_theme_label.setAlignment(Qt.AlignCenter)
        self.update_current_theme_label()
        layout.addWidget(self.current_theme_label)

        # Add stretch
        layout.addStretch()

        # Footer
        footer = QLabel("Notice how all widgets update instantly when you change themes!")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("font-size: 11px; color: #888;")
        layout.addWidget(footer)

    def on_theme_changed(self, theme_name):
        """Handle theme selection change."""
        app = ThemedApplication.instance()
        if app and theme_name:
            app.set_theme(theme_name)
            self.update_current_theme_label()

    def update_current_theme_label(self):
        """Update the current theme display label."""
        app = ThemedApplication.instance()
        if app:
            current = app.current_theme_name
            if hasattr(current, 'name'):
                current = current.name
            elif not isinstance(current, str):
                current = str(current)

            self.current_theme_label.setText(f"Current Theme: {current}")
            self.current_theme_label.setStyleSheet("font-size: 14px; font-weight: bold;")


def main():
    app = ThemedApplication(sys.argv)

    # Start with the default theme
    app.set_theme("default")

    window = ThemeSwitcherWindow()
    window.show()

    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
