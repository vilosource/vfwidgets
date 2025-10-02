#!/usr/bin/env python3
"""
Example: ChromeTabbedWindow with Theme System Integration

Demonstrates ChromeTabbedWindow working with ThemedApplication
to support dynamic theme switching.

Run:
    python examples/04_themed_chrome_tabs.py
"""

import sys
from pathlib import Path

# Add both chrome-tabbed-window and theme_system to path
base_dir = Path(__file__).parent.parent
sys.path.insert(0, str(base_dir / "src"))

theme_system_path = base_dir.parent / "theme_system" / "src"
if theme_system_path.exists():
    sys.path.insert(0, str(theme_system_path))

from PySide6.QtWidgets import QTextEdit, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QWidget
from PySide6.QtCore import Qt

from chrome_tabbed_window import ChromeTabbedWindow
from vfwidgets_theme import ThemedApplication


def main():
    # Create themed application
    app = ThemedApplication(sys.argv)
    app.set_theme("dark")

    # Create chrome tabbed window (automatically themed!)
    window = ChromeTabbedWindow()
    window.setWindowTitle("Themed Chrome Tabs Example")
    window.resize(900, 600)

    # Add some tabs
    for i in range(1, 4):
        editor = QTextEdit()
        editor.setPlaceholderText(f"Content for Tab {i}...")
        window.addTab(editor, f"Tab {i}")

    # Add a tab with theme switching controls
    theme_tab = QWidget()
    theme_layout = QVBoxLayout(theme_tab)

    info_label = QLabel(
        "<h2>Chrome Tabs with Theme System</h2>"
        "<p>Click the buttons below to switch themes.</p>"
        "<p>Notice how the tab colors change automatically!</p>"
        "<ul>"
        "<li><b>Dark theme:</b> Tabs use dark colors</li>"
        "<li><b>Light theme:</b> Tabs use light colors</li>"
        "<li><b>Default theme:</b> VS Code default colors</li>"
        "<li><b>Minimal theme:</b> Minimalist color scheme</li>"
        "</ul>"
        "<p>The theme colors come from the VFWidgets theme system, "
        "which supports VS Code theme importing!</p>"
    )
    info_label.setWordWrap(True)
    info_label.setAlignment(Qt.AlignmentFlag.AlignTop)
    info_label.setTextFormat(Qt.TextFormat.RichText)
    info_label.setStyleSheet("padding: 20px; font-size: 14px;")
    theme_layout.addWidget(info_label)

    # Add theme switching buttons
    button_layout = QHBoxLayout()
    button_layout.setContentsMargins(20, 10, 20, 10)

    for theme_name in ["dark", "light", "default", "minimal"]:
        btn = QPushButton(f"{theme_name.capitalize()} Theme")
        btn.clicked.connect(lambda checked, name=theme_name: app.set_theme(name))
        btn.setMinimumHeight(40)
        button_layout.addWidget(btn)

    theme_layout.addLayout(button_layout)
    theme_layout.addStretch()

    window.addTab(theme_tab, "Theme Switcher")

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
