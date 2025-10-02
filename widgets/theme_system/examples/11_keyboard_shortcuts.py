"""Example 11: Keyboard Shortcuts for Theme Switching.

This example demonstrates ThemeShortcuts for adding keyboard shortcuts
to quickly switch themes.

Key Features:
- Toggle between light/dark with Ctrl+T
- Cycle through all themes with Ctrl+Shift+T
- Direct theme selection with Ctrl+1, Ctrl+2, etc.

Run:
    python examples/11_keyboard_shortcuts.py
"""

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QTextEdit, QVBoxLayout

from vfwidgets_theme import ThemedApplication
from vfwidgets_theme.widgets import ThemedMainWindow, ThemedQWidget, ThemeShortcuts


class MainWindow(ThemedMainWindow):
    """Main application window with keyboard shortcuts."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Keyboard Shortcuts Example")
        self.resize(700, 500)

        # Create central widget
        central = ThemedQWidget()
        layout = QVBoxLayout(central)

        # Add title
        title = QLabel("Theme Keyboard Shortcuts Example")
        title.setStyleSheet("font-size: 18pt; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        # Add description with shortcuts info
        desc_text = """
<h3>Available Keyboard Shortcuts:</h3>

<table style="font-size: 12pt; padding: 10px;">
<tr><td><b>Ctrl+T</b></td><td>Toggle between light and dark themes</td></tr>
<tr><td><b>Ctrl+Shift+T</b></td><td>Cycle through all available themes</td></tr>
<tr><td><b>Ctrl+1</b></td><td>Switch to Dark theme</td></tr>
<tr><td><b>Ctrl+2</b></td><td>Switch to Light theme</td></tr>
<tr><td><b>Ctrl+3</b></td><td>Switch to Minimal theme</td></tr>
</table>

<p style="padding-top: 20px;">
Try the shortcuts! Notice how fast and convenient it is to switch themes
without using menus or dialogs.
</p>

<p>
This is perfect for power users and developers who prefer keyboard navigation.
</p>
"""
        desc = QLabel(desc_text)
        desc.setWordWrap(True)
        desc.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(desc)

        # Add text editor
        editor = QTextEdit()
        editor.setPlainText(
            "Sample editor content.\n\n"
            "Use the keyboard shortcuts to switch themes:\n"
            "- Ctrl+T: Toggle light/dark\n"
            "- Ctrl+Shift+T: Cycle themes\n"
            "- Ctrl+1/2/3: Direct theme selection"
        )
        layout.addWidget(editor)

        self.setCentralWidget(central)

        # Setup keyboard shortcuts
        shortcuts = ThemeShortcuts(self)

        # Toggle between light/dark
        shortcuts.add_toggle_shortcut("Ctrl+T")

        # Cycle through all themes
        shortcuts.add_cycle_shortcut("Ctrl+Shift+T")

        # Direct shortcuts to specific themes
        shortcuts.add_specific_theme_shortcut("Ctrl+1", "dark")
        shortcuts.add_specific_theme_shortcut("Ctrl+2", "light")
        shortcuts.add_specific_theme_shortcut("Ctrl+3", "minimal")


def main():
    # Create themed application
    app = ThemedApplication(sys.argv)
    app.set_theme("dark")

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
