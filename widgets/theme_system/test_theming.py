#!/usr/bin/env python3
"""Test if theming actually works - verify stylesheet is applied."""

import sys

from PySide6.QtWidgets import QPushButton, QVBoxLayout

from vfwidgets_theme import ThemedApplication, ThemedMainWindow

app = ThemedApplication(sys.argv)

# Explicitly set vscode theme
print("Setting vscode theme...")
result = app.set_theme("vscode")
print(f"set_theme result: {result}")

# Verify vscode theme is loaded
current = app.get_current_theme()
if current:
    print(f"Current theme: {current.name}")
    print(f"Theme type: {current.type}")
    print(f"Button background: {current.get('button.background')}")
else:
    print("ERROR: No theme is set!")

window = ThemedMainWindow()
window.setWindowTitle("Theme Test")
window.setMinimumSize(400, 300)

# Create central widget manually
from PySide6.QtWidgets import QWidget

central = QWidget()
window.setCentralWidget(central)
layout = QVBoxLayout(central)

# Add a button
button = QPushButton("Test Button")
layout.addWidget(button)

# Check if stylesheet is applied
print(f"\nWindow stylesheet length: {len(window.styleSheet())}")
print(f"Window stylesheet preview:\n{window.styleSheet()[:500]}...")

if len(window.styleSheet()) > 0:
    print("\n✅ Stylesheet IS being applied!")
else:
    print("\n❌ Stylesheet NOT applied!")

window.show()
sys.exit(app.exec())
