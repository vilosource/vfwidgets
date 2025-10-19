"""KeySequenceEdit widget example.

This example demonstrates how to use the KeySequenceEdit widget
to capture keyboard shortcuts from the user.
"""

import sys

from PySide6.QtWidgets import (
    QApplication,
    QFormLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from vfwidgets_keybinding.widgets import KeySequenceEdit


class KeySequenceDemo(QMainWindow):
    """Demo window showing KeySequenceEdit usage."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("KeySequenceEdit Demo")
        self.resize(500, 300)

        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Add instructions
        instructions = QLabel(
            "Click in the fields below and press key combinations.\n"
            "Examples: Ctrl+S, Ctrl+Shift+K, Alt+F1, etc.\n"
            "Press Escape to clear, or use the X button."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Create form with multiple KeySequenceEdit widgets
        form_layout = QFormLayout()
        layout.addLayout(form_layout)

        # Edit 1 - Basic usage
        self.edit1 = KeySequenceEdit()
        self.edit1.setShortcut("Ctrl+S")  # Set initial value
        self.edit1.shortcut_changed.connect(lambda s: self.on_shortcut_changed("Save", s))
        form_layout.addRow("Save:", self.edit1)

        # Edit 2 - Empty initially
        self.edit2 = KeySequenceEdit()
        self.edit2.shortcut_changed.connect(lambda s: self.on_shortcut_changed("Open", s))
        form_layout.addRow("Open:", self.edit2)

        # Edit 3 - Read-only display
        self.edit3 = KeySequenceEdit()
        self.edit3.setShortcut("Ctrl+Q")
        self.edit3.setReadOnly(True)
        form_layout.addRow("Quit (read-only):", self.edit3)

        # Add status label
        self.status_label = QLabel("Status: Ready")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        # Add buttons
        button_layout = QVBoxLayout()
        layout.addLayout(button_layout)

        # Get values button
        get_btn = QPushButton("Get Current Shortcuts")
        get_btn.clicked.connect(self.show_current_shortcuts)
        button_layout.addWidget(get_btn)

        # Clear all button
        clear_btn = QPushButton("Clear All Shortcuts")
        clear_btn.clicked.connect(self.clear_all)
        button_layout.addWidget(clear_btn)

        # Validate button
        validate_btn = QPushButton("Validate All Shortcuts")
        validate_btn.clicked.connect(self.validate_all)
        button_layout.addWidget(validate_btn)

        layout.addStretch()

    def on_shortcut_changed(self, name: str, shortcut: str):
        """Handle shortcut changes."""
        if shortcut:
            self.status_label.setText(f"Status: {name} changed to '{shortcut}'")
        else:
            self.status_label.setText(f"Status: {name} cleared")

    def show_current_shortcuts(self):
        """Display current shortcut values."""
        save = self.edit1.shortcut()
        open_sc = self.edit2.shortcut()
        quit_sc = self.edit3.shortcut()

        message = (
            f"Current shortcuts:\n"
            f"  Save: {save or '(none)'}\n"
            f"  Open: {open_sc or '(none)'}\n"
            f"  Quit: {quit_sc or '(none)'}"
        )
        self.status_label.setText(message)

    def clear_all(self):
        """Clear all editable shortcuts."""
        self.edit1.clearShortcut()
        self.edit2.clearShortcut()
        # edit3 is read-only, so skip it
        self.status_label.setText("Status: All shortcuts cleared")

    def validate_all(self):
        """Validate all shortcuts."""
        save_valid = self.edit1.isValid()
        open_valid = self.edit2.isValid()
        quit_valid = self.edit3.isValid()

        message = (
            f"Validation results:\n"
            f"  Save: {'✓ Valid' if save_valid else '✗ Invalid/Empty'}\n"
            f"  Open: {'✓ Valid' if open_valid else '✗ Invalid/Empty'}\n"
            f"  Quit: {'✓ Valid' if quit_valid else '✗ Invalid/Empty'}"
        )
        self.status_label.setText(message)


def main():
    app = QApplication(sys.argv)
    window = KeySequenceDemo()
    window.show()

    print("KeySequenceEdit Demo")
    print("=" * 50)
    print("- Click in the fields and press key combinations")
    print("- Press Escape to clear a field")
    print("- Use the X button to clear")
    print("- Read-only fields cannot be edited")
    print("=" * 50)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
