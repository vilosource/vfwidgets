"""Themed ButtonWidget example demonstrating theme system integration.

This example shows:
- Basic themed button usage
- Theme switching (dark/light)
- Different WidgetRole values
- Backward compatibility with old ButtonStyle API
"""

import sys

from PySide6.QtWidgets import QApplication, QHBoxLayout, QPushButton, QVBoxLayout, QWidget
from vfwidgets_button import ButtonWidget
from vfwidgets_theme import ThemedApplication, WidgetRole


class ThemedButtonDemo(QWidget):
    """Demo window showing themed buttons."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Themed ButtonWidget Demo")
        self.setMinimumWidth(600)

        layout = QVBoxLayout()

        # Theme switcher
        theme_layout = QHBoxLayout()
        self.light_btn = QPushButton("Light Theme")
        self.dark_btn = QPushButton("Dark Theme")
        self.light_btn.clicked.connect(lambda: self.switch_theme("light"))
        self.dark_btn.clicked.connect(lambda: self.switch_theme("dark"))
        theme_layout.addWidget(self.light_btn)
        theme_layout.addWidget(self.dark_btn)
        layout.addLayout(theme_layout)

        # Default button
        layout.addWidget(ButtonWidget("Default Button"))

        # Semantic role buttons
        layout.addWidget(ButtonWidget("Primary Button", role=WidgetRole.PRIMARY))
        layout.addWidget(ButtonWidget("Success Button", role=WidgetRole.SUCCESS))
        layout.addWidget(ButtonWidget("Warning Button", role=WidgetRole.WARNING))
        layout.addWidget(ButtonWidget("Danger Button", role=WidgetRole.DANGER))

        # Button with customization
        rounded_btn = ButtonWidget("Rounded with Shadow", role=WidgetRole.PRIMARY)
        layout.addWidget(rounded_btn)

        # Button without shadow
        no_shadow = ButtonWidget("No Shadow", role=WidgetRole.SUCCESS, shadow=False)
        layout.addWidget(no_shadow)

        # Non-rounded button
        no_round = ButtonWidget("Square Corners", role=WidgetRole.WARNING, rounded=False)
        layout.addWidget(no_round)

        # Disabled button
        disabled = ButtonWidget("Disabled Button", role=WidgetRole.DANGER)
        disabled.setEnabled(False)
        layout.addWidget(disabled)

        self.setLayout(layout)

    def switch_theme(self, theme_name: str):
        """Switch application theme."""
        app = QApplication.instance()
        if isinstance(app, ThemedApplication):
            app.set_theme(theme_name)


def main():
    # Use ThemedApplication instead of QApplication
    app = ThemedApplication(sys.argv)

    # Set initial theme
    app.set_theme("dark")

    # Create and show demo window
    demo = ThemedButtonDemo()
    demo.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
