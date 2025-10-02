#!/usr/bin/env python3
"""Example 08: VS Code Theme Showcase.
===================================

Demonstrates the VS Code Dark+ inspired theme with various UI elements.

The VS Code theme features:
- Dark background (#1e1e1e) matching VS Code's editor
- Blue accent color (#007acc) matching VS Code's UI
- Carefully chosen colors for buttons, inputs, and other widgets
- Professional developer-friendly appearance
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QSlider,
    QTextEdit,
    QVBoxLayout,
)

from vfwidgets_theme import ThemedApplication, ThemedMainWindow, ThemedQWidget


class VSCodeShowcaseWindow(ThemedMainWindow):
    """Main window showcasing the VS Code theme."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("VS Code Theme Showcase")
        self.setMinimumSize(800, 600)
        self.setup_ui()

    def setup_ui(self):
        # Create central widget
        central = ThemedQWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("VS Code Dark+ Theme")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        # Description
        desc = QLabel(
            "This theme is inspired by Visual Studio Code's Dark+ color scheme.\n"
            "It features the iconic dark background (#1e1e1e) and blue accents (#007acc)."
        )
        desc.setStyleSheet("font-size: 12px; color: #999999;")
        layout.addWidget(desc)

        # Buttons section
        buttons_group = QGroupBox("Buttons")
        buttons_layout = QHBoxLayout()

        primary_btn = QPushButton("Primary Action")
        primary_btn.setMinimumHeight(32)
        buttons_layout.addWidget(primary_btn)

        secondary_btn = QPushButton("Secondary Action")
        secondary_btn.setMinimumHeight(32)
        buttons_layout.addWidget(secondary_btn)

        disabled_btn = QPushButton("Disabled")
        disabled_btn.setEnabled(False)
        disabled_btn.setMinimumHeight(32)
        buttons_layout.addWidget(disabled_btn)

        buttons_group.setLayout(buttons_layout)
        layout.addWidget(buttons_group)

        # Input fields section
        inputs_group = QGroupBox("Input Fields")
        inputs_layout = QVBoxLayout()

        input1 = QLineEdit()
        input1.setPlaceholderText("Enter your name...")
        input1.setMinimumHeight(28)
        inputs_layout.addWidget(input1)

        input2 = QLineEdit()
        input2.setPlaceholderText("Enter your email...")
        input2.setMinimumHeight(28)
        inputs_layout.addWidget(input2)

        combo = QComboBox()
        combo.addItems(["Option 1", "Option 2", "Option 3"])
        combo.setMinimumHeight(28)
        inputs_layout.addWidget(combo)

        inputs_group.setLayout(inputs_layout)
        layout.addWidget(inputs_group)

        # Checkboxes and Radio buttons
        options_group = QGroupBox("Options")
        options_layout = QHBoxLayout()

        # Checkboxes
        check_layout = QVBoxLayout()
        check1 = QCheckBox("Enable feature A")
        check1.setChecked(True)
        check2 = QCheckBox("Enable feature B")
        check3 = QCheckBox("Enable feature C")
        check_layout.addWidget(check1)
        check_layout.addWidget(check2)
        check_layout.addWidget(check3)
        options_layout.addLayout(check_layout)

        # Radio buttons
        radio_layout = QVBoxLayout()
        radio1 = QRadioButton("Mode 1")
        radio1.setChecked(True)
        radio2 = QRadioButton("Mode 2")
        radio3 = QRadioButton("Mode 3")
        radio_layout.addWidget(radio1)
        radio_layout.addWidget(radio2)
        radio_layout.addWidget(radio3)
        options_layout.addLayout(radio_layout)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Text editor
        editor_group = QGroupBox("Text Editor")
        editor_layout = QVBoxLayout()

        editor = QTextEdit()
        editor.setPlaceholderText("# Write your code here...\ndef hello_world():\n    print('Hello from VS Code theme!')")
        editor.setMinimumHeight(150)
        editor_layout.addWidget(editor)

        editor_group.setLayout(editor_layout)
        layout.addWidget(editor_group)

        # Slider
        slider_group = QGroupBox("Slider")
        slider_layout = QVBoxLayout()

        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(100)
        slider.setValue(50)
        slider_layout.addWidget(slider)

        slider_value = QLabel("Value: 50")
        slider.valueChanged.connect(lambda v: slider_value.setText(f"Value: {v}"))
        slider_layout.addWidget(slider_value)

        slider_group.setLayout(slider_layout)
        layout.addWidget(slider_group)

        # Add stretch to push everything up
        layout.addStretch()

        # Status message
        status = QLabel("VS Code theme provides a professional, developer-friendly appearance")
        status.setStyleSheet("color: #007acc; font-size: 11px;")
        status.setAlignment(Qt.AlignCenter)
        layout.addWidget(status)


def main():
    app = ThemedApplication(sys.argv)

    # Set VS Code theme
    app.set_theme("vscode")

    # Create and show window
    window = VSCodeShowcaseWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
