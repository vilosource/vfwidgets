#!/usr/bin/env python3
"""Example 07: Theme Helpers - Quick Integration Utilities
===========================================================

Demonstrates helper utilities for quickly adding theme selection UI
to your applications.

What you'll learn:
- add_theme_menu() - One-liner for theme menu
- add_theme_toolbar() - One-liner for theme toolbar
- ThemeShortcuts - Keyboard shortcuts for theme switching

These helpers make it trivial to add professional theme selection
to any application!

Run:
    python examples/07_theme_helpers.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtWidgets import QLabel, QTextEdit, QVBoxLayout

from vfwidgets_theme import ThemedApplication, ThemedMainWindow, ThemedQWidget
from vfwidgets_theme.widgets import (
    ThemeShortcuts,
    add_theme_menu,
    add_theme_toolbar,
)


class HelpersDemo(ThemedMainWindow):
    """Demo of theme helper utilities."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Theme Helpers - Quick Integration")
        self.setMinimumSize(700, 500)
        self.setup_ui()
        self.setup_theme_helpers()

    def setup_ui(self):
        """Setup UI."""
        central = ThemedQWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("🎨 Theme Helper Utilities")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # Instructions
        instructions = QTextEdit()
        instructions.setReadOnly(True)
        instructions.setMaximumHeight(300)
        instructions.setPlainText(
            "This example demonstrates theme helper utilities:\n\n"
            "1. THEME MENU (see menu bar)\n"
            "   - Added with: add_theme_menu(self)\n"
            "   - Automatically lists all themes\n"
            "   - Shows current theme with checkmark\n"
            "   - One line of code!\n\n"
            "2. THEME TOOLBAR (see toolbar)\n"
            "   - Added with: add_theme_toolbar(self)\n"
            "   - Dropdown for quick theme switching\n"
            "   - One line of code!\n\n"
            "3. KEYBOARD SHORTCUTS\n"
            "   - Ctrl+1: Switch to first theme\n"
            "   - Ctrl+2: Switch to second theme\n"
            "   - Ctrl+3: Switch to third theme\n"
            "   - Ctrl+T: Cycle through themes\n\n"
            "Try them now!"
        )
        layout.addWidget(instructions)

        # Info
        info = QLabel(
            "💡 These helpers make it trivial to add professional theme\n"
            "selection to any application. No boilerplate code needed!"
        )
        info.setWordWrap(True)
        info.setStyleSheet("font-size: 11px; color: #888; padding: 10px;")
        layout.addWidget(info)

    def setup_theme_helpers(self):
        """Setup theme helper utilities."""
        # 1. Add theme menu (ONE LINER!)
        add_theme_menu(self)

        # 2. Add theme toolbar (ONE LINER!)
        add_theme_toolbar(self)

        # 3. Add keyboard shortcuts
        shortcuts = ThemeShortcuts(self)

        # Customize shortcuts if desired
        # shortcuts.set_theme_1_shortcut("Ctrl+Shift+1")
        # shortcuts.set_cycle_themes_shortcut("F9")


def main():
    """Main entry point."""
    app = ThemedApplication(sys.argv)

    window = HelpersDemo()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
