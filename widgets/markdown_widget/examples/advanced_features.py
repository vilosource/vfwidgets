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
from vfwidgets_markdown import MarkdownViewer


class ExampleWindow(QMainWindow):
    """Example window demonstrating advanced features."""

    def __init__(self):
        """Initialize the example window."""
        super().__init__()
        self.setWindowTitle("MarkdownViewer - Advanced Example")
        self.resize(600, 400)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout(central_widget)

        # Add markdown viewer widget
        self.viewer = MarkdownViewer()
        layout.addWidget(self.viewer)

        # Control panel
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)

        # Add controls
        self.status_label = QLabel("Status: Ready")
        control_layout.addWidget(self.status_label)

        control_layout.addStretch()

        mermaid_btn = QPushButton("Show Mermaid")
        mermaid_btn.clicked.connect(self.show_mermaid)
        control_layout.addWidget(mermaid_btn)

        math_btn = QPushButton("Show Math")
        math_btn.clicked.connect(self.show_math)
        control_layout.addWidget(math_btn)

        layout.addWidget(control_panel)

        # Connect signals
        self.viewer.content_loaded.connect(lambda: self.status_label.setText("Status: Loaded"))

    def show_mermaid(self):
        """Show markdown with mermaid diagram."""
        self.viewer.set_markdown(
            """
# Mermaid Diagram

```mermaid
graph TD
    A[Start] --> B[Process]
    B --> C[End]
```
        """
        )
        self.status_label.setText("Status: Showing Mermaid")

    def show_math(self):
        """Show markdown with math equations."""
        self.viewer.set_markdown(
            """
# Math Equations

Inline: $E = mc^2$

Block:
$$
\\int_0^\\infty e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}
$$
        """
        )
        self.status_label.setText("Status: Showing Math")


def main():
    """Run the example application."""
    app = QApplication(sys.argv)
    window = ExampleWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
