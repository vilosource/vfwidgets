"""Example 07: Theme Menu Integration.

This example demonstrates how to add theme switching to an application
using a menu bar - a one-liner approach for adding professional theme
selection to any Qt application.

Key Features:
- add_theme_menu() one-liner helper
- Automatic theme switching from menu
- Visual checkmarks for current theme
- Theme metadata in tooltips

Run:
    python examples/07_theme_menu.py
"""

import sys

from PySide6.QtWidgets import QLabel, QVBoxLayout

from vfwidgets_theme import ThemedApplication
from vfwidgets_theme.widgets import ThemedMainWindow, ThemedQWidget, add_theme_menu


class MainWindow(ThemedMainWindow):
    """Main application window with theme menu."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Theme Menu Example")
        self.resize(600, 400)

        # Create central widget
        central = ThemedQWidget()
        layout = QVBoxLayout(central)

        # Add content
        label = QLabel(
            "Theme Menu Example\n\n"
            "Use the 'Theme' menu in the menu bar to switch themes.\n\n"
            "Notice:\n"
            "- Current theme is checked\n"
            "- Hover over menu items to see theme descriptions\n"
            "- Theme changes apply instantly\n"
            "- Menu stays synchronized with app theme"
        )
        label.setStyleSheet("font-size: 14pt; padding: 20px;")
        layout.addWidget(label)

        self.setCentralWidget(central)

        # ONE-LINER: Add theme menu to menubar
        add_theme_menu(self)

        # You can also customize the menu
        # add_theme_menu(self, menu_name="Appearance")


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
