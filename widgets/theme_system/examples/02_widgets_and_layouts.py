#!/usr/bin/env python3
"""Example 02: Widgets and Layouts - Automatic Child Theming
=============================================================

Demonstrates how ALL widgets are automatically themed when added to
a themed parent - no manual styling required!

What you'll learn:
- Multiple widget types (buttons, labels, inputs, checkboxes)
- How automatic child theming works
- Layout management with themed widgets
- Widget interactions and signals

Key insight:
When you use ThemedMainWindow or ThemedQWidget, EVERY child widget
you add gets themed automatically. You never have to manually apply
themes to buttons, inputs, or other standard Qt widgets.

Run:
    python examples/02_widgets_and_layouts.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from vfwidgets_theme import ThemedApplication, ThemedMainWindow, ThemedQWidget


class WidgetDemoWindow(ThemedMainWindow):
    """Main window showcasing various themed widgets."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Widgets & Layouts - All Themed Automatically!")
        self.setMinimumSize(700, 600)
        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface."""
        # Create central widget (themed)
        central = ThemedQWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("🎨 All These Widgets Are Themed Automatically!")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        # Buttons group
        button_group = QGroupBox("Buttons (Themed Automatically)")
        button_layout = QHBoxLayout(button_group)

        for text in ["Primary", "Secondary", "Action", "Disabled"]:
            btn = QPushButton(text)
            btn.setMinimumHeight(36)
            if text == "Disabled":
                btn.setEnabled(False)
            btn.clicked.connect(lambda checked, t=text: self.on_button_click(t))
            button_layout.addWidget(btn)

        layout.addWidget(button_group)

        # Input fields group
        input_group = QGroupBox("Input Fields (Themed Automatically)")
        input_layout = QVBoxLayout(input_group)

        # Line edit
        input_layout.addWidget(QLabel("Single-line input:"))
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Type something here...")
        self.line_edit.setMinimumHeight(32)
        input_layout.addWidget(self.line_edit)

        # Text edit
        input_layout.addWidget(QLabel("Multi-line input:"))
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Enter multiple lines of text...")
        self.text_edit.setMaximumHeight(100)
        input_layout.addWidget(self.text_edit)

        layout.addWidget(input_group)

        # Checkboxes group
        checkbox_group = QGroupBox("Checkboxes (Themed Automatically)")
        checkbox_layout = QVBoxLayout(checkbox_group)

        self.checkbox1 = QCheckBox("Enable feature A")
        self.checkbox1.setChecked(True)
        checkbox_layout.addWidget(self.checkbox1)

        self.checkbox2 = QCheckBox("Enable feature B")
        checkbox_layout.addWidget(self.checkbox2)

        self.checkbox3 = QCheckBox("Disabled checkbox")
        self.checkbox3.setEnabled(False)
        checkbox_layout.addWidget(self.checkbox3)

        layout.addWidget(checkbox_group)

        # Status label
        self.status_label = QLabel("👆 Click any button to see interactions!")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("padding: 10px;")
        layout.addWidget(self.status_label)

        # Info footer
        footer = QLabel(
            "💡 Key Point: You didn't write ANY custom stylesheets!\n"
            "All widgets inherit theming from ThemedMainWindow automatically."
        )
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setWordWrap(True)
        footer.setStyleSheet("font-size: 11px; color: #888; padding: 10px;")
        layout.addWidget(footer)

    def on_button_click(self, button_name: str):
        """Handle button clicks."""
        text = self.line_edit.text() or "(empty)"
        self.status_label.setText(f"✅ Button '{button_name}' clicked! Line edit contains: {text}")


def main():
    """Main entry point."""
    app = ThemedApplication(sys.argv)

    window = WidgetDemoWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
