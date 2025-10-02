#!/usr/bin/env python3
"""
Example 04: Input Forms and Dialogs
=====================================

Demonstrates themed input widgets, forms, and dialogs.

What this demonstrates:
- Themed input widgets (QLineEdit, QTextEdit)
- Themed option widgets (QCheckBox, QRadioButton)
- ThemedDialog for settings/preferences
- Form layouts with themed widgets
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QTextEdit,
    QVBoxLayout,
)

from vfwidgets_theme import ThemedApplication, ThemedDialog, ThemedMainWindow, ThemedQWidget


class PreferencesDialog(ThemedDialog):
    """A themed dialog for user preferences."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.setMinimumSize(400, 300)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Title
        title = QLabel("Application Preferences")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        form_layout.addRow("Username:", self.username_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("your.email@example.com")
        form_layout.addRow("Email:", self.email_input)

        layout.addLayout(form_layout)

        # Options group
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()

        self.auto_save_check = QCheckBox("Enable auto-save")
        self.auto_save_check.setChecked(True)
        options_layout.addWidget(self.auto_save_check)

        self.notifications_check = QCheckBox("Enable notifications")
        options_layout.addWidget(self.notifications_check)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        btn_ok = QPushButton("OK")
        btn_ok.setMinimumWidth(80)
        btn_ok.clicked.connect(self.accept)
        button_layout.addWidget(btn_ok)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setMinimumWidth(80)
        btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(btn_cancel)

        layout.addLayout(button_layout)


class InputFormWindow(ThemedMainWindow):
    """Main window demonstrating input forms."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Input Forms Demo")
        self.setMinimumSize(600, 500)
        self.setup_ui()

    def setup_ui(self):
        # Create central widget
        central = ThemedQWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title = QLabel("Themed Input Widgets Demo")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # Text inputs group
        text_group = QGroupBox("Text Inputs")
        text_layout = QVBoxLayout()

        name_label = QLabel("Name:")
        text_layout.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your name")
        self.name_input.setMinimumHeight(32)
        text_layout.addWidget(self.name_input)

        bio_label = QLabel("Bio:")
        text_layout.addWidget(bio_label)

        self.bio_input = QTextEdit()
        self.bio_input.setPlaceholderText("Tell us about yourself...")
        self.bio_input.setMaximumHeight(100)
        text_layout.addWidget(self.bio_input)

        text_group.setLayout(text_layout)
        layout.addWidget(text_group)

        # Checkboxes group
        check_group = QGroupBox("Interests")
        check_layout = QVBoxLayout()

        self.check_coding = QCheckBox("Coding")
        self.check_design = QCheckBox("Design")
        self.check_music = QCheckBox("Music")

        check_layout.addWidget(self.check_coding)
        check_layout.addWidget(self.check_design)
        check_layout.addWidget(self.check_music)

        check_group.setLayout(check_layout)
        layout.addWidget(check_group)

        # Radio buttons group
        radio_group = QGroupBox("Experience Level")
        radio_layout = QVBoxLayout()

        self.radio_button_group = QButtonGroup(self)

        self.radio_beginner = QRadioButton("Beginner")
        self.radio_intermediate = QRadioButton("Intermediate")
        self.radio_advanced = QRadioButton("Advanced")
        self.radio_beginner.setChecked(True)

        self.radio_button_group.addButton(self.radio_beginner)
        self.radio_button_group.addButton(self.radio_intermediate)
        self.radio_button_group.addButton(self.radio_advanced)

        radio_layout.addWidget(self.radio_beginner)
        radio_layout.addWidget(self.radio_intermediate)
        radio_layout.addWidget(self.radio_advanced)

        radio_group.setLayout(radio_layout)
        layout.addWidget(radio_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        btn_preferences = QPushButton("Preferences...")
        btn_preferences.setMinimumSize(120, 36)
        btn_preferences.clicked.connect(self.show_preferences)
        button_layout.addWidget(btn_preferences)

        btn_submit = QPushButton("Submit")
        btn_submit.setMinimumSize(120, 36)
        btn_submit.clicked.connect(self.on_submit)
        button_layout.addWidget(btn_submit)

        layout.addLayout(button_layout)

        # Add stretch
        layout.addStretch()

    def show_preferences(self):
        """Show preferences dialog."""
        dialog = PreferencesDialog(self)
        if dialog.exec():
            # User clicked OK
            print("Preferences accepted")
        else:
            # User clicked Cancel
            print("Preferences cancelled")

    def on_submit(self):
        """Handle form submission."""
        name = self.name_input.text()
        bio = self.bio_input.toPlainText()

        interests = []
        if self.check_coding.isChecked():
            interests.append("Coding")
        if self.check_design.isChecked():
            interests.append("Design")
        if self.check_music.isChecked():
            interests.append("Music")

        level = "Beginner"
        if self.radio_intermediate.isChecked():
            level = "Intermediate"
        elif self.radio_advanced.isChecked():
            level = "Advanced"

        print("\n=== Form Submitted ===")
        print(f"Name: {name}")
        print(f"Bio: {bio[:50]}..." if len(bio) > 50 else f"Bio: {bio}")
        print(f"Interests: {', '.join(interests) if interests else 'None'}")
        print(f"Level: {level}")
        print("======================\n")


def main():
    app = ThemedApplication(sys.argv)

    window = InputFormWindow()
    window.show()

    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
