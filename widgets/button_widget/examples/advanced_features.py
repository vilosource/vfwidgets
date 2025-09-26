#!/usr/bin/env python3
"""Advanced features example for ButtonWidget."""

import sys

from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)
from vfwidgets_button import ButtonStyle, ButtonWidget


class ExampleWindow(QMainWindow):
    """Example window demonstrating advanced button features."""

    def __init__(self):
        """Initialize the example window."""
        super().__init__()
        self.setWindowTitle("ButtonWidget - Advanced Example")
        self.resize(800, 600)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout(central_widget)

        # Title
        title = QLabel("Enhanced Button Widget Showcase")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        # Button styles showcase
        styles_group = QGroupBox("Button Styles")
        styles_layout = QGridLayout(styles_group)

        # Create buttons with different styles
        self.style_buttons = {}
        for i, style in enumerate(ButtonStyle):
            btn = ButtonWidget(style.value.title(), style=style)
            btn.clicked.connect(lambda checked, s=style: self.on_button_clicked(s))
            btn.double_clicked.connect(lambda s=style: self.on_double_clicked(s))
            btn.long_pressed.connect(lambda s=style: self.on_long_pressed(s))

            row = i // 4
            col = i % 4
            styles_layout.addWidget(btn, row, col)
            self.style_buttons[style] = btn

        layout.addWidget(styles_group)

        # Interactive controls
        controls_group = QGroupBox("Interactive Controls")
        controls_layout = QVBoxLayout(controls_group)

        # Test button for modifications
        self.test_button = ButtonWidget("Test Button", style=ButtonStyle.PRIMARY)
        self.test_button.clicked.connect(lambda: self.update_status("Clicked"))
        self.test_button.double_clicked.connect(lambda: self.update_status("Double clicked!"))
        self.test_button.long_pressed.connect(lambda: self.update_status("Long pressed!"))
        controls_layout.addWidget(self.test_button)

        # Control panel
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)

        # Style selector
        control_layout.addWidget(QLabel("Style:"))
        self.style_combo = QComboBox()
        for style in ButtonStyle:
            self.style_combo.addItem(style.value.title(), style)
        self.style_combo.currentIndexChanged.connect(self.change_test_button_style)
        control_layout.addWidget(self.style_combo)

        # Feature toggles
        self.animated_check = QCheckBox("Animated")
        self.animated_check.setChecked(True)
        self.animated_check.toggled.connect(self.toggle_animation)
        control_layout.addWidget(self.animated_check)

        self.rounded_check = QCheckBox("Rounded")
        self.rounded_check.setChecked(True)
        self.rounded_check.toggled.connect(self.toggle_rounded)
        control_layout.addWidget(self.rounded_check)

        self.shadow_check = QCheckBox("Shadow")
        self.shadow_check.setChecked(True)
        self.shadow_check.toggled.connect(self.toggle_shadow)
        control_layout.addWidget(self.shadow_check)

        self.enabled_check = QCheckBox("Enabled")
        self.enabled_check.setChecked(True)
        self.enabled_check.toggled.connect(self.toggle_enabled)
        control_layout.addWidget(self.enabled_check)

        control_layout.addStretch()

        controls_layout.addWidget(control_panel)
        layout.addWidget(controls_group)

        # Status display
        status_group = QGroupBox("Event Log")
        status_layout = QVBoxLayout(status_group)

        self.status_label = QLabel(
            "Ready - Try clicking, double-clicking, or long-pressing buttons"
        )
        self.status_label.setStyleSheet("padding: 10px; background: #f0f0f0; border-radius: 4px;")
        self.status_label.setWordWrap(True)
        status_layout.addWidget(self.status_label)

        layout.addWidget(status_group)
        layout.addStretch()

    def on_button_clicked(self, style: ButtonStyle):
        """Handle button click."""
        self.update_status(f"Clicked: {style.value.title()} button")

    def on_double_clicked(self, style: ButtonStyle):
        """Handle double click."""
        self.update_status(f"Double-clicked: {style.value.title()} button")

    def on_long_pressed(self, style: ButtonStyle):
        """Handle long press."""
        self.update_status(f"Long-pressed: {style.value.title()} button (held for 1+ seconds)")

    def change_test_button_style(self):
        """Change test button style."""
        style = self.style_combo.currentData()
        if style:
            self.test_button.set_style(style)
            self.update_status(f"Changed test button style to: {style.value.title()}")

    def toggle_animation(self, checked: bool):
        """Toggle animation."""
        self.test_button.set_animated(checked)
        self.update_status(f"Animation: {'enabled' if checked else 'disabled'}")

    def toggle_rounded(self, checked: bool):
        """Toggle rounded corners."""
        self.test_button.set_rounded(checked)
        self.update_status(f"Rounded corners: {'enabled' if checked else 'disabled'}")

    def toggle_shadow(self, checked: bool):
        """Toggle shadow effect."""
        self.test_button.set_shadow(checked)
        self.update_status(f"Shadow: {'enabled' if checked else 'disabled'}")

    def toggle_enabled(self, checked: bool):
        """Toggle button enabled state."""
        self.test_button.setEnabled(checked)
        self.update_status(f"Button: {'enabled' if checked else 'disabled'}")

    def update_status(self, message: str):
        """Update status label."""
        self.status_label.setText(message)
        print(f"Event: {message}")


def main():
    """Run the example application."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Use Fusion style for consistent look

    window = ExampleWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
