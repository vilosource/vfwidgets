#!/usr/bin/env python3
"""
Example 06: Role Markers (Type-Safe Edition)
=============================================

Demonstrates the role marker system for semantic widget styling using
the type-safe WidgetRole enum (NEW in 2.0.0-rc4).

Role markers allow you to apply semantic styling to widgets without
writing custom stylesheets. Now with IDE autocomplete and type safety!

Available Roles (WidgetRole enum):
- WidgetRole.EDITOR - Monospace font, editor-specific colors
- WidgetRole.DANGER - Red color scheme for destructive actions
- WidgetRole.SUCCESS - Green color scheme for positive actions
- WidgetRole.WARNING - Yellow/orange color scheme for warnings
- WidgetRole.SECONDARY - Muted color scheme for secondary actions
- WidgetRole.PRIMARY - Primary action styling
- WidgetRole.INFO - Informational styling

Old Way (still works):
    button.setProperty("role", "danger")

New Way (recommended - type-safe with autocomplete):
    from vfwidgets_theme import WidgetRole, set_widget_role
    set_widget_role(button, WidgetRole.DANGER)

This example shows both the old and new approaches!
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

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
    WidgetRole,
    set_widget_role,
)


class RoleMarkersWindow(ThemedMainWindow):
    """Window demonstrating all role markers."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Role Markers Example")
        self.setMinimumSize(800, 600)
        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface."""
        # Central widget
        from vfwidgets_theme import ThemedQWidget
        central = ThemedQWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Role Markers Demo")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Description
        desc = QLabel(
            "Role markers provide semantic styling without custom CSS.\n"
            "NEW: Use the WidgetRole enum for type-safe, autocomplete-friendly role setting!\n"
            "Old way still works: widget.setProperty('role', 'danger')\n"
            "New way (recommended): set_widget_role(widget, WidgetRole.DANGER)"
        )
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Button roles section
        button_group = self.create_button_roles_group()
        layout.addWidget(button_group)

        # Editor role section
        editor_group = self.create_editor_role_group()
        layout.addWidget(editor_group)

        layout.addStretch()

    def create_button_roles_group(self):
        """Create group box showing button role markers."""
        group = QGroupBox("Button Role Markers")
        layout = QVBoxLayout(group)
        layout.setSpacing(15)

        # Default button (no role)
        default_layout = QHBoxLayout()
        default_btn = QPushButton("Default Button")
        default_btn.setMinimumHeight(36)
        default_label = QLabel("No role property - uses standard button styling")
        default_layout.addWidget(default_btn)
        default_layout.addWidget(default_label)
        default_layout.addStretch()
        layout.addLayout(default_layout)

        # Danger button (NEW TYPE-SAFE API)
        danger_layout = QHBoxLayout()
        danger_btn = QPushButton("Delete")
        set_widget_role(danger_btn, WidgetRole.DANGER)  # NEW: Type-safe!
        danger_btn.setMinimumHeight(36)
        danger_label = QLabel('WidgetRole.DANGER - Red styling for destructive actions')
        danger_layout.addWidget(danger_btn)
        danger_layout.addWidget(danger_label)
        danger_layout.addStretch()
        layout.addLayout(danger_layout)

        # Success button (NEW TYPE-SAFE API)
        success_layout = QHBoxLayout()
        success_btn = QPushButton("Save")
        set_widget_role(success_btn, WidgetRole.SUCCESS)  # NEW: Type-safe!
        success_btn.setMinimumHeight(36)
        success_label = QLabel('WidgetRole.SUCCESS - Green styling for positive actions')
        success_layout.addWidget(success_btn)
        success_layout.addWidget(success_label)
        success_layout.addStretch()
        layout.addLayout(success_layout)

        # Warning button (NEW TYPE-SAFE API)
        warning_layout = QHBoxLayout()
        warning_btn = QPushButton("Proceed with Caution")
        set_widget_role(warning_btn, WidgetRole.WARNING)  # NEW: Type-safe!
        warning_btn.setMinimumHeight(36)
        warning_label = QLabel('WidgetRole.WARNING - Yellow styling for warnings')
        warning_layout.addWidget(warning_btn)
        warning_layout.addWidget(warning_label)
        warning_layout.addStretch()
        layout.addLayout(warning_layout)

        # Secondary button (NEW TYPE-SAFE API)
        secondary_layout = QHBoxLayout()
        secondary_btn = QPushButton("Cancel")
        set_widget_role(secondary_btn, WidgetRole.SECONDARY)  # NEW: Type-safe!
        secondary_btn.setMinimumHeight(36)
        secondary_label = QLabel('WidgetRole.SECONDARY - Muted styling for secondary actions')
        secondary_layout.addWidget(secondary_btn)
        secondary_layout.addWidget(secondary_label)
        secondary_layout.addStretch()
        layout.addLayout(secondary_layout)

        return group

    def create_editor_role_group(self):
        """Create group box showing editor role marker."""
        group = QGroupBox("Editor Role Marker")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)

        # Description
        desc = QLabel(
            'The "editor" role automatically applies:\n'
            '• Monospace font (11pt Courier New/Consolas)\n'
            '• Editor-specific background color\n'
            '• Editor-specific foreground color\n'
            '• Proper selection colors'
        )
        layout.addWidget(desc)

        # Two editors side by side for comparison
        compare_layout = QHBoxLayout()

        # Left: Regular text edit
        left_layout = QVBoxLayout()
        left_label = QLabel("Regular QTextEdit (no role):")
        left_layout.addWidget(left_label)

        regular_edit = QTextEdit()
        regular_edit.setPlainText("This text uses the default UI font.\nNotice the font is sans-serif.")
        regular_edit.setMaximumHeight(150)
        left_layout.addWidget(regular_edit)
        compare_layout.addLayout(left_layout)

        # Right: Editor with role (NEW TYPE-SAFE API)
        right_layout = QVBoxLayout()
        right_label = QLabel('QTextEdit with WidgetRole.EDITOR:')
        right_layout.addWidget(right_label)

        editor_edit = QTextEdit()
        set_widget_role(editor_edit, WidgetRole.EDITOR)  # NEW: Type-safe!
        editor_edit.setPlainText("This text uses the editor font.\nNotice the font is monospace (Courier New).")
        editor_edit.setMaximumHeight(150)
        right_layout.addWidget(editor_edit)
        compare_layout.addLayout(right_layout)

        layout.addLayout(compare_layout)

        return group


def main():
    """Main application entry point."""
    app = ThemedApplication(sys.argv)

    # Use vscode theme to see role markers clearly
    app.set_theme("vscode")

    window = RoleMarkersWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
