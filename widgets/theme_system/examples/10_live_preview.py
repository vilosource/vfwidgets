"""Example 10: Live Theme Preview.

This example demonstrates the ThemePreview system for trying themes
before committing to them.

Key Features:
- ThemePreview class for non-destructive previewing
- Preview multiple themes
- Commit to keep changes
- Cancel to restore original

Run:
    python examples/10_live_preview.py
"""

import sys

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QVBoxLayout,
)

from vfwidgets_theme import ThemedApplication
from vfwidgets_theme.widgets import ThemedMainWindow, ThemedQWidget, ThemePreview


class MainWindow(ThemedMainWindow):
    """Main application window with live preview."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Live Preview Example")
        self.resize(700, 500)

        # Create preview system
        self.preview = ThemePreview()
        self.app = ThemedApplication.instance()

        # Create central widget
        central = ThemedQWidget()
        layout = QVBoxLayout(central)

        # Add title
        title = QLabel("Live Theme Preview Example")
        title.setStyleSheet("font-size: 18pt; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        # Add description
        desc = QLabel(
            "Select themes from the list to preview them.\n"
            "Use 'Keep This Theme' to commit or 'Cancel' to restore original."
        )
        desc.setStyleSheet("padding: 10px;")
        layout.addWidget(desc)

        # Add theme list
        self.theme_list = QListWidget()
        self.theme_list.addItems(self.app.get_available_themes())
        self.theme_list.currentTextChanged.connect(self.on_preview_theme)
        layout.addWidget(self.theme_list)

        # Add buttons
        btn_layout = QHBoxLayout()

        self.btn_commit = QPushButton("Keep This Theme")
        self.btn_commit.clicked.connect(self.on_commit)
        self.btn_commit.setStyleSheet("padding: 10px; font-size: 12pt;")
        btn_layout.addWidget(self.btn_commit)

        self.btn_cancel = QPushButton("Cancel (Restore Original)")
        self.btn_cancel.clicked.connect(self.on_cancel)
        self.btn_cancel.setStyleSheet("padding: 10px; font-size: 12pt;")
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)

        self.setCentralWidget(central)

        # Update button states
        self.update_buttons()

    def on_preview_theme(self, theme_name):
        """Preview selected theme."""
        if theme_name:
            self.preview.preview(theme_name)
            self.update_buttons()

    def on_commit(self):
        """Commit to current theme."""
        self.preview.commit()
        self.update_buttons()

    def on_cancel(self):
        """Cancel preview and restore original."""
        self.preview.cancel()
        self.update_buttons()

    def update_buttons(self):
        """Update button states based on preview status."""
        is_previewing = self.preview.is_previewing
        self.btn_commit.setEnabled(is_previewing)
        self.btn_cancel.setEnabled(is_previewing)


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
