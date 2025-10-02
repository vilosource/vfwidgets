"""Example 08: Theme Toolbar Integration.

This example demonstrates how to add a theme switching toolbar to an
application - a quick way to add visible theme controls to your app.

Key Features:
- add_theme_toolbar() one-liner helper
- Dropdown combo box for theme selection
- Always-visible theme switcher
- Automatic synchronization

Run:
    python examples/08_theme_toolbar.py
"""

import sys

from PySide6.QtWidgets import QLabel, QTextEdit, QVBoxLayout

from vfwidgets_theme import ThemedApplication
from vfwidgets_theme.widgets import ThemedMainWindow, ThemedQWidget, add_theme_toolbar


class MainWindow(ThemedMainWindow):
    """Main application window with theme toolbar."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Theme Toolbar Example")
        self.resize(700, 500)

        # Create central widget
        central = ThemedQWidget()
        layout = QVBoxLayout(central)

        # Add title
        title = QLabel("Theme Toolbar Example")
        title.setStyleSheet("font-size: 18pt; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        # Add description
        desc = QLabel(
            "Use the dropdown in the toolbar above to switch themes.\n"
            "The theme selector is always visible and easy to access."
        )
        desc.setStyleSheet("padding: 10px;")
        layout.addWidget(desc)

        # Add text editor to show theming
        editor = QTextEdit()
        editor.setPlainText(
            "This is a sample text editor.\n\n"
            "Try switching themes using the toolbar dropdown.\n"
            "Notice how the entire application updates instantly:\n"
            "- Background colors\n"
            "- Text colors\n"
            "- Widget styles\n"
            "- Scrollbars\n"
            "- etc."
        )
        layout.addWidget(editor)

        self.setCentralWidget(central)

        # ONE-LINER: Add theme toolbar
        add_theme_toolbar(self)

        # You can also customize
        # add_theme_toolbar(self, toolbar_name="Appearance", widget_type="combo")


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
