"""Example 09: Settings Dialog with Theme Picker.

This example demonstrates using ThemePickerDialog for modal theme selection
with live preview capability.

Key Features:
- ThemePickerDialog with preview mode
- Live preview while browsing themes
- Commit or cancel changes
- Automatic theme restoration on cancel

Run:
    python examples/09_settings_dialog.py
"""

import sys

from PySide6.QtWidgets import (
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from vfwidgets_theme import ThemedApplication
from vfwidgets_theme.widgets import ThemedMainWindow, ThemedQWidget, ThemePickerDialog


class MainWindow(ThemedMainWindow):
    """Main application window with settings dialog."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings Dialog Example")
        self.resize(600, 400)

        # Create central widget
        central = ThemedQWidget()
        layout = QVBoxLayout(central)

        # Add title
        title = QLabel("Theme Picker Dialog Example")
        title.setStyleSheet("font-size: 18pt; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        # Add description
        desc = QLabel(
            "Click the button below to open the theme picker dialog.\n\n"
            "In the dialog:\n"
            "- Browse available themes\n"
            "- See live preview as you select different themes\n"
            "- Click OK to keep the selected theme\n"
            "- Click Cancel to restore the original theme\n\n"
            "This is perfect for settings/preferences dialogs!"
        )
        desc.setStyleSheet("padding: 10px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Add button to open picker
        self.btn_picker = QPushButton("Open Theme Picker...")
        self.btn_picker.setStyleSheet("padding: 10px; font-size: 12pt;")
        self.btn_picker.clicked.connect(self.open_theme_picker)
        layout.addWidget(self.btn_picker)

        layout.addStretch()

        self.setCentralWidget(central)

    def open_theme_picker(self):
        """Open theme picker dialog."""
        # Create dialog with preview mode enabled
        dialog = ThemePickerDialog(
            parent=self,
            preview_mode=True,
            title="Select Application Theme"
        )

        # Show dialog (modal)
        if dialog.exec():
            # User clicked OK
            selected = dialog.selected_theme
            QMessageBox.information(
                self,
                "Theme Selected",
                f"You selected: {selected}\n\nThe theme has been applied!"
            )
        else:
            # User clicked Cancel
            QMessageBox.information(
                self,
                "Theme Selection Cancelled",
                "Original theme has been restored."
            )


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
