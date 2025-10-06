"""Minimal KeybindingManager example.

This example shows the absolute minimum code needed to use
the KeybindingManager. You can run this in under 5 minutes.
"""

import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit
from vfwidgets_keybinding import ActionDefinition, KeybindingManager


def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Minimal KeybindingManager Example")
    window.resize(800, 600)

    # Create text editor
    editor = QTextEdit()
    editor.setPlaceholderText("Press Ctrl+Q to quit...")
    window.setCentralWidget(editor)

    # Create keybinding manager
    manager = KeybindingManager()

    # Register quit action
    manager.register_action(
        ActionDefinition(
            id="app.quit",
            description="Quit Application",
            default_shortcut="Ctrl+Q",
            callback=app.quit,
        )
    )

    # Apply shortcuts to window
    manager.apply_shortcuts(window)

    window.show()
    print("Press Ctrl+Q to quit")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
