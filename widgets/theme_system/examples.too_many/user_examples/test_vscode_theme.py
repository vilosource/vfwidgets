#!/usr/bin/env python3
"""Test VS Code theme loading."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from PySide6.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget

from vfwidgets_theme import ThemedApplication

app = ThemedApplication(sys.argv)

print("Available themes:", app.available_themes)
print("Has vscode:", "vscode" in app.available_themes)

# Try to set theme
try:
    result = app.set_theme("vscode")
    print(f"Set theme result: {result}")

    current = app.current_theme_name
    if hasattr(current, "name"):
        current = current.name
    print(f"Current theme: {current}")
except Exception as e:
    print(f"Error setting theme: {e}")
    import traceback

    traceback.print_exc()

# Create window to test theme
window = QMainWindow()
window.setWindowTitle("VS Code Theme Test")
window.setMinimumSize(400, 300)

central = QWidget()
window.setCentralWidget(central)

layout = QVBoxLayout(central)
label = QLabel("Testing VS Code Theme")
label.setStyleSheet("font-size: 18px;")
layout.addWidget(label)

window.show()

sys.exit(app.exec())
