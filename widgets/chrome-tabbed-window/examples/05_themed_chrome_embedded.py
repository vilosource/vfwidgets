#!/usr/bin/env python3
"""
Example: Embedded ChromeTabbedWindow with Themes

Shows ChromeTabbedWindow embedded in a ThemedMainWindow,
demonstrating that embedded mode respects parent theme.

Run:
    python examples/05_themed_chrome_embedded.py
"""

import sys
from pathlib import Path

# Add paths
base_dir = Path(__file__).parent.parent
sys.path.insert(0, str(base_dir / "src"))
theme_system_path = base_dir.parent / "theme_system" / "src"
if theme_system_path.exists():
    sys.path.insert(0, str(theme_system_path))

from PySide6.QtWidgets import QVBoxLayout, QTextEdit, QLabel, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt

from chrome_tabbed_window import ChromeTabbedWindow
from vfwidgets_theme import ThemedApplication
from vfwidgets_theme.widgets import ThemedMainWindow, ThemedQWidget, add_theme_menu


class MainWindow(ThemedMainWindow):
    """Main window with embedded chrome tabs."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Embedded Chrome Tabs with Themes")
        self.resize(1000, 700)

        # Create central widget
        central = ThemedQWidget()
        layout = QVBoxLayout(central)

        # Add title and instructions
        title = QLabel("Embedded ChromeTabbedWindow with Theme Support")
        title.setStyleSheet("font-size: 18pt; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        instructions = QLabel(
            "This example shows ChromeTabbedWindow embedded in a ThemedMainWindow. "
            "Both the main window and the tabs respond to theme changes. "
            "Use the Theme menu to switch between different themes."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("padding: 10px; font-size: 11pt;")
        layout.addWidget(instructions)

        # Add chrome tabbed widget (embedded mode - no window controls)
        self.tabs = ChromeTabbedWindow(parent=central)
        self.tabs.setTabsClosable(True)

        # Add tabs
        for i in range(1, 5):
            editor = QTextEdit()
            editor.setPlaceholderText(f"Editor {i}")
            self.tabs.addTab(editor, f"File {i}.txt")

        # Add info tab
        info = QLabel(
            "<h3>Theme Integration</h3>"
            "<p>Both the main window and the Chrome tabs use the same theme!</p>"
            "<ul>"
            "<li>Tab colors match the theme</li>"
            "<li>Text colors adapt to theme</li>"
            "<li>Background colors harmonize</li>"
            "<li>All updates happen automatically</li>"
            "</ul>"
            "<p>Try adding tabs, switching themes, and closing tabs. "
            "Everything stays themed!</p>"
        )
        info.setWordWrap(True)
        info.setTextFormat(Qt.TextFormat.RichText)
        info.setStyleSheet("padding: 20px;")
        self.tabs.addTab(info, "Theme Info")

        layout.addWidget(self.tabs)

        # Add buttons
        button_layout = QHBoxLayout()

        add_tab_btn = QPushButton("Add New Tab")
        add_tab_btn.clicked.connect(self.add_new_tab)
        button_layout.addWidget(add_tab_btn)

        remove_tab_btn = QPushButton("Remove Current Tab")
        remove_tab_btn.clicked.connect(self.remove_current_tab)
        button_layout.addWidget(remove_tab_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.setCentralWidget(central)

        # Add theme menu
        add_theme_menu(self)

        # Track tab count
        self.tab_counter = 5

    def add_new_tab(self):
        """Add a new tab."""
        editor = QTextEdit()
        editor.setPlaceholderText(f"New content {self.tab_counter}")
        self.tabs.addTab(editor, f"New Tab {self.tab_counter}")
        self.tab_counter += 1
        self.tabs.setCurrentIndex(self.tabs.count() - 1)

    def remove_current_tab(self):
        """Remove the current tab."""
        current_idx = self.tabs.currentIndex()
        if current_idx >= 0 and self.tabs.count() > 1:
            self.tabs.removeTab(current_idx)


def main():
    app = ThemedApplication(sys.argv)
    app.set_theme("dark")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
