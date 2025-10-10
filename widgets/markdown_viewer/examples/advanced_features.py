#!/usr/bin/env python3
"""Advanced features example for MarkdownViewerWidget."""

import sys

from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from vfwidgets_markdown_viewer import MarkdownViewerWidget


class ExampleWindow(QMainWindow):
    """Example window demonstrating advanced features."""

    def __init__(self):
        """Initialize the example window."""
        super().__init__()
        self.setWindowTitle("MarkdownViewerWidget - Advanced Example")
        self.resize(600, 400)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout(central_widget)

        # Add custom widget
        self.custom_widget = MarkdownViewerWidget()
        layout.addWidget(self.custom_widget)

        # Control panel
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)

        # Add controls
        self.status_label = QLabel("Status: Ready")
        control_layout.addWidget(self.status_label)

        control_layout.addStretch()

        update_btn = QPushButton("Update Widget")
        update_btn.clicked.connect(self.update_widget)
        control_layout.addWidget(update_btn)

        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_widget)
        control_layout.addWidget(reset_btn)

        layout.addWidget(control_panel)

        # Connect signals
        self.custom_widget.value_changed.connect(self.on_value_changed)

    def update_widget(self):
        """Update the widget with new data."""
        self.custom_widget.set_value("Updated Value")
        self.status_label.setText("Status: Updated")

    def reset_widget(self):
        """Reset the widget to default state."""
        self.custom_widget.set_value(None)
        self.status_label.setText("Status: Reset")

    def on_value_changed(self, value):
        """Handle value changed signal."""
        print(f"Widget value changed to: {value}")
        self.status_label.setText(f"Status: Value = {value}")


def main():
    """Run the example application."""
    app = QApplication(sys.argv)
    window = ExampleWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
