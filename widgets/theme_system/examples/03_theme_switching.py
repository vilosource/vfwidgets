#!/usr/bin/env python3
"""Example 03: Theme Switching - Dynamic Theme Changes
=======================================================

Demonstrates how to switch themes at runtime and how theme changes
automatically propagate to all widgets.

What you'll learn:
- How to list available themes
- How to switch themes dynamically
- How theme changes affect all widgets instantly
- How to get the current theme name

Key API:
- app.available_themes - List all registered themes
- app.set_theme(name) - Switch to a different theme
- app.current_theme_name - Get current theme

Run:
    python examples/03_theme_switching.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from vfwidgets_theme import ThemedApplication, ThemedMainWindow, ThemedQWidget


class ThemeSwitcherWindow(ThemedMainWindow):
    """Window demonstrating dynamic theme switching."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Theme Switching Demo")
        self.setMinimumSize(600, 500)
        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface."""
        central = ThemedQWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title = QLabel("🎨 Dynamic Theme Switching")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # Theme selector group
        theme_group = QGroupBox("Select a Theme")
        theme_layout = QVBoxLayout(theme_group)

        # Get themed application instance
        app = ThemedApplication.instance()

        # Theme dropdown
        theme_layout.addWidget(QLabel("Available themes:"))
        self.theme_combo = QComboBox()
        self.theme_combo.setMinimumHeight(36)

        # Populate with available themes
        if app:
            themes = app.available_themes
            self.theme_combo.addItems(themes)

            # Set current theme
            current = str(app.current_theme_name)
            index = self.theme_combo.findText(current)
            if index >= 0:
                self.theme_combo.setCurrentIndex(index)

        # Connect theme change
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        theme_layout.addWidget(self.theme_combo)

        # Theme descriptions
        theme_info = QLabel(
            "• vscode - VS Code Dark+ theme (dark)\n"
            "• dark - GitHub-inspired dark theme\n"
            "• light - High contrast light theme\n"
            "• default - Microsoft-inspired light theme\n"
            "• minimal - Monochrome fallback theme"
        )
        theme_info.setStyleSheet("font-size: 11px; padding: 10px;")
        theme_layout.addWidget(theme_info)

        layout.addWidget(theme_group)

        # Sample widgets group
        sample_group = QGroupBox("Sample Widgets (Watch Them Change!)")
        sample_layout = QVBoxLayout(sample_group)

        # Sample buttons
        for text in ["Sample Button 1", "Sample Button 2", "Sample Button 3"]:
            btn = QPushButton(text)
            btn.setMinimumHeight(40)
            sample_layout.addWidget(btn)

        layout.addWidget(sample_group)

        # Current theme display
        self.theme_status = QLabel()
        self.theme_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.theme_status.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        self.update_theme_status()
        layout.addWidget(self.theme_status)

        layout.addStretch()

        # Footer
        footer = QLabel(
            "💡 Notice: When you change themes, ALL widgets update instantly!\n"
            "No manual updates, no refresh needed - it just works."
        )
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setWordWrap(True)
        footer.setStyleSheet("font-size: 11px; color: #888;")
        layout.addWidget(footer)

    def on_theme_changed(self, theme_name: str):
        """Handle theme selection change."""
        if theme_name:
            app = ThemedApplication.instance()
            if app:
                app.set_theme(theme_name)
                self.update_theme_status()

    def update_theme_status(self):
        """Update the theme status label."""
        app = ThemedApplication.instance()
        if app:
            current = str(app.current_theme_name)
            self.theme_status.setText(f"✅ Current Theme: {current}")


def main():
    """Main entry point."""
    app = ThemedApplication(sys.argv)

    # Start with vscode theme
    app.set_theme("vscode")

    window = ThemeSwitcherWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
