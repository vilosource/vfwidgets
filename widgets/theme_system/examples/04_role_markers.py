#!/usr/bin/env python3
"""Example 04: Role Markers - Semantic Widget Styling
======================================================

Demonstrates the role marker system for semantic widget styling without
writing custom stylesheets.

What you'll learn:
- How to use role markers for semantic button styles
- Available role types (danger, success, warning, primary, secondary)
- How to use the "editor" role for monospace fonts
- Type-safe role setting with WidgetRole enum

Key concept:
Role markers let you say "this is a delete button" or "this is code"
and the theme system automatically applies the right colors and fonts.

API:
- widget.setProperty("role", "danger") - Old way (still works)
- set_widget_role(widget, WidgetRole.DANGER) - New way (type-safe)

Run:
    python examples/04_role_markers.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from vfwidgets_theme import (
    ThemedApplication,
    ThemedMainWindow,
    ThemedQWidget,
    WidgetRole,
    set_widget_role,
)


class RoleMarkersWindow(ThemedMainWindow):
    """Window demonstrating role markers."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Role Markers - Semantic Styling")
        self.setMinimumSize(750, 650)
        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface."""
        central = ThemedQWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("🎨 Role Markers - Semantic Styling")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # Description
        desc = QLabel(
            "Role markers provide semantic styling without custom CSS.\n"
            "Just set a role, and the theme handles the colors!"
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Button roles
        layout.addWidget(self.create_button_roles())

        # Editor role
        layout.addWidget(self.create_editor_role())

        # Status
        self.status_label = QLabel("Click any button to see it in action!")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("padding: 10px;")
        layout.addWidget(self.status_label)

        layout.addStretch()

        # Footer
        footer = QLabel(
            "💡 Two ways to set roles:\n"
            "Old: button.setProperty('role', 'danger')\n"
            "New: set_widget_role(button, WidgetRole.DANGER)  ← Type-safe!"
        )
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setWordWrap(True)
        footer.setStyleSheet("font-size: 11px; color: #888;")
        layout.addWidget(footer)

    def create_button_roles(self) -> QGroupBox:
        """Create button roles demonstration."""
        group = QGroupBox("Button Roles (Semantic Actions)")
        layout = QVBoxLayout(group)

        # Row 1: Danger and Success
        row1 = QHBoxLayout()

        delete_btn = QPushButton("🗑️ Delete Item")
        delete_btn.setMinimumHeight(40)
        set_widget_role(delete_btn, WidgetRole.DANGER)  # Red
        delete_btn.clicked.connect(lambda: self.on_action("Delete"))
        row1.addWidget(delete_btn)

        save_btn = QPushButton("💾 Save Changes")
        save_btn.setMinimumHeight(40)
        set_widget_role(save_btn, WidgetRole.SUCCESS)  # Green
        save_btn.clicked.connect(lambda: self.on_action("Save"))
        row1.addWidget(save_btn)

        layout.addLayout(row1)

        # Row 2: Warning and Info
        row2 = QHBoxLayout()

        warning_btn = QPushButton("⚠️ Proceed with Caution")
        warning_btn.setMinimumHeight(40)
        set_widget_role(warning_btn, WidgetRole.WARNING)  # Yellow/Orange
        warning_btn.clicked.connect(lambda: self.on_action("Warning"))
        row2.addWidget(warning_btn)

        info_btn = QPushButton("ℹ️ Show Info")
        info_btn.setMinimumHeight(40)
        set_widget_role(info_btn, WidgetRole.INFO)  # Blue
        info_btn.clicked.connect(lambda: self.on_action("Info"))
        row2.addWidget(info_btn)

        layout.addLayout(row2)

        # Row 3: Primary and Secondary
        row3 = QHBoxLayout()

        primary_btn = QPushButton("⭐ Primary Action")
        primary_btn.setMinimumHeight(40)
        set_widget_role(primary_btn, WidgetRole.PRIMARY)  # Accent color
        primary_btn.clicked.connect(lambda: self.on_action("Primary"))
        row3.addWidget(primary_btn)

        secondary_btn = QPushButton("➖ Secondary Action")
        secondary_btn.setMinimumHeight(40)
        set_widget_role(secondary_btn, WidgetRole.SECONDARY)  # Muted
        secondary_btn.clicked.connect(lambda: self.on_action("Secondary"))
        row3.addWidget(secondary_btn)

        layout.addLayout(row3)

        return group

    def create_editor_role(self) -> QGroupBox:
        """Create editor role demonstration."""
        group = QGroupBox("Editor Role (Monospace Font)")
        layout = QVBoxLayout(group)

        label = QLabel("The 'editor' role gives monospace font + editor colors:")
        layout.addWidget(label)

        # Code editor with role marker
        code_editor = QTextEdit()
        code_editor.setPlaceholderText("Enter code here...")
        code_editor.setMaximumHeight(120)

        # Set editor role - gives monospace font automatically!
        set_widget_role(code_editor, WidgetRole.EDITOR)

        # Add sample code
        code_editor.setPlainText(
            "# Python code with monospace font\n"
            "def hello_world():\n"
            "    print('Role markers are awesome!')\n"
            "    return True"
        )

        layout.addWidget(code_editor)

        return group

    def on_action(self, action: str):
        """Handle button actions."""
        self.status_label.setText(f"✅ {action} button clicked!")


def main():
    """Main entry point."""
    app = ThemedApplication(sys.argv)

    window = RoleMarkersWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
