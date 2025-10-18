#!/usr/bin/env python3
"""Example 18: Customizable Application - User Color Preferences

This example demonstrates VFThemedApplication with user customization:
- Declarative list of customizable tokens
- User preference persistence via QSettings
- Color picker for user customization
- Validation and error handling

This pattern is ideal for applications that want to provide users with
customization options while maintaining control over the UI design.

Usage:
    python examples/18_customizable_app.py
"""

import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QListWidget, QColorDialog,
    QGroupBox, QMessageBox
)
from PySide6.QtGui import QColor
from vfwidgets_theme import ThemedWidget
from vfwidgets_theme.widgets.vf_themed_application import VFThemedApplication
from vfwidgets_theme.core.manager import ThemeManager


class CustomizableApp(VFThemedApplication):
    """Example application with user customization.

    This app defines which tokens users can customize:
    - Editor colors (background, foreground, selection)
    - Button colors (background, foreground)

    All other colors are locked to app defaults to maintain design integrity.
    """

    theme_config = {
        # Base theme
        "base_theme": "dark",

        # App branding (locked - users cannot change)
        "app_overrides": {
            "statusBar.background": "#0ea5e9",
            "statusBar.foreground": "#ffffff",
        },

        # Allow user customization
        "allow_user_customization": True,

        # Define which tokens users CAN customize
        "customizable_tokens": [
            "editor.background",
            "editor.foreground",
            "editor.selectionBackground",
            "button.background",
            "button.foreground",
        ],

        # Persist user preferences
        "persist_user_overrides": True,
        "settings_key_prefix": "customizable_demo/",
    }


class CustomizableDemoWindow(ThemedWidget):
    """Demo window with user customization interface."""

    theme_config = {
        "background": "editor.background",
        "foreground": "editor.foreground",
    }

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.refresh_customization_list()

    def setup_ui(self):
        """Setup the user interface."""
        layout = QHBoxLayout(self)

        # Left panel: Editor demo
        left_panel = QVBoxLayout()

        title = QLabel("User Customization Demo")
        title.setStyleSheet("font-size: 18pt; font-weight: bold; padding: 10px;")
        left_panel.addWidget(title)

        desc = QLabel(
            "This app allows users to customize specific colors while "
            "keeping the overall design consistent.\n\n"
            "Click a color in the list to customize it with a color picker."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("padding: 10px;")
        left_panel.addWidget(desc)

        # Editor
        editor_group = QGroupBox("Customizable Editor")
        editor_layout = QVBoxLayout(editor_group)

        self.editor = QTextEdit()
        self.editor.setPlainText(
            "# Select some text to see the selection color\n"
            "# Customize editor colors in the panel on the right\n\n"
            "class CustomizableApp(VFThemedApplication):\n"
            "    theme_config = {\n"
            '        "allow_user_customization": True,\n'
            '        "customizable_tokens": [\n'
            '            "editor.background",\n'
            '            "editor.foreground",\n'
            '            "editor.selectionBackground",\n'
            "        ],\n"
            "    }\n"
        )
        self.editor.setMinimumHeight(300)
        editor_layout.addWidget(self.editor)

        left_panel.addWidget(editor_group)

        # Status info
        self.status_label = QLabel()
        self.update_status()
        left_panel.addWidget(self.status_label)

        layout.addLayout(left_panel, 2)

        # Right panel: Customization controls
        right_panel = QVBoxLayout()

        controls_title = QLabel("Customization Options")
        controls_title.setStyleSheet("font-size: 14pt; font-weight: bold; padding: 5px;")
        right_panel.addWidget(controls_title)

        # Customizable tokens list
        list_label = QLabel("Click a color to customize:")
        right_panel.addWidget(list_label)

        self.token_list = QListWidget()
        self.token_list.itemDoubleClicked.connect(self.customize_selected_token)
        right_panel.addWidget(self.token_list)

        # Control buttons
        btn_customize = QPushButton("Customize Selected Color")
        btn_customize.clicked.connect(self.customize_selected_token)
        right_panel.addWidget(btn_customize)

        btn_reset_selected = QPushButton("Reset Selected to Default")
        btn_reset_selected.clicked.connect(self.reset_selected_token)
        right_panel.addWidget(btn_reset_selected)

        btn_reset_all = QPushButton("Reset All to Defaults")
        btn_reset_all.clicked.connect(self.reset_all_customizations)
        right_panel.addWidget(btn_reset_all)

        right_panel.addStretch()

        layout.addLayout(right_panel, 1)

    def refresh_customization_list(self):
        """Refresh the list of customizable tokens."""
        self.token_list.clear()

        app = VFThemedApplication.instance()
        if not app:
            return

        customizable = app.get_customizable_tokens()
        manager = ThemeManager.get_instance()
        user_overrides = manager.get_user_overrides()

        for token in customizable:
            # Show token name and whether it's customized
            status = "✓ customized" if token in user_overrides else "default"
            current_color = manager.get_effective_color(token, fallback="#000000")
            item_text = f"{token} ({status}) - {current_color}"
            self.token_list.addItem(item_text)

        self.update_status()

    def customize_selected_token(self):
        """Open color picker for selected token."""
        current_item = self.token_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a color to customize")
            return

        # Extract token name from list item
        item_text = current_item.text()
        token = item_text.split(" (")[0]

        app = VFThemedApplication.instance()
        if not app:
            return

        # Get current color
        manager = ThemeManager.get_instance()
        current_color_str = manager.get_effective_color(token, fallback="#ffffff")
        current_color = QColor(current_color_str)

        # Open color picker
        color = QColorDialog.getColor(current_color, self, f"Choose color for {token}")

        if color.isValid():
            # Set user customization
            success = app.customize_color(token, color.name(), persist=True)
            if success:
                self.refresh_customization_list()
                QMessageBox.information(
                    self, "Success",
                    f"Customized {token} to {color.name()}\n\n"
                    "Your preference has been saved and will be restored next time."
                )
            else:
                QMessageBox.warning(
                    self, "Error",
                    f"Failed to customize {token}"
                )

    def reset_selected_token(self):
        """Reset selected token to default."""
        current_item = self.token_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a color to reset")
            return

        # Extract token name
        item_text = current_item.text()
        token = item_text.split(" (")[0]

        app = VFThemedApplication.instance()
        if app:
            app.reset_color(token, persist=True)
            self.refresh_customization_list()

    def reset_all_customizations(self):
        """Reset all customizations."""
        reply = QMessageBox.question(
            self, "Confirm Reset",
            "Reset all color customizations to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            app = VFThemedApplication.instance()
            if app:
                app.clear_user_preferences()
                self.refresh_customization_list()

    def update_status(self):
        """Update status information."""
        manager = ThemeManager.get_instance()
        app_overrides = manager.get_app_overrides()
        user_overrides = manager.get_user_overrides()

        text = (
            f"App Defaults: {len(app_overrides)} locked colors\n"
            f"User Customizations: {len(user_overrides)} personalized colors\n"
            f"\nℹ️ Your preferences are automatically saved"
        )
        self.status_label.setText(text)
        self.status_label.setStyleSheet("padding: 10px; background: #0ea5e9; color: white;")


def main():
    """Main entry point."""
    # Create customizable application
    app = CustomizableApp(sys.argv, app_id="CustomizableDemo")

    # Create and show main window
    window = CustomizableDemoWindow()
    window.setWindowTitle("Example 18: Customizable Application")
    window.resize(900, 600)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
