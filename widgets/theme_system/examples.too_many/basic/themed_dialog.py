#!/usr/bin/env python3
"""themed_dialog.py - Simple themed dialog examples.

Shows how to create dialogs that respond to theme changes with
consistent styling across all dialog components.

Key Concepts:
- Dialog theming
- Modal and modeless dialogs
- Custom dialog layouts
- Button box styling
- Message dialogs

Example usage:
    python themed_dialog.py
"""

import sys

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
)

from vfwidgets_theme import ThemedApplication, ThemedWidget


class ThemedDialog(ThemedWidget, QDialog):
    """Base themed dialog class."""

    theme_config = {
        "bg": "dialog.background",
        "fg": "dialog.foreground",
        "border": "dialog.border",
        "title_bg": "dialog.title.background",
        "title_fg": "dialog.title.foreground",
        "button_bg": "dialog.button.background",
        "button_fg": "dialog.button.foreground",
        "button_border": "dialog.button.border",
        "font": "dialog.font",
    }

    def __init__(self, title="Dialog", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(300, 200)

        # Apply initial styling
        self.update_styling()

    def on_theme_changed(self):
        """Called automatically when theme changes."""
        self.update_styling()

    def update_styling(self):
        """Update dialog styling based on current theme."""
        # Get theme colors
        bg_color = self.theme.get("bg", "#ffffff")
        fg_color = self.theme.get("fg", "#000000")
        border_color = self.theme.get("border", "#cccccc")
        font = self.theme.get("font", "Arial, sans-serif")

        # Generate stylesheet
        stylesheet = f"""
        QDialog {{
            background-color: {bg_color};
            color: {fg_color};
            border: 2px solid {border_color};
            border-radius: 8px;
            font-family: {font};
            font-size: 13px;
        }}

        QLabel {{
            color: {fg_color};
            font-family: {font};
        }}

        QLineEdit, QTextEdit, QComboBox, QSpinBox {{
            background-color: {bg_color};
            color: {fg_color};
            border: 1px solid {border_color};
            border-radius: 4px;
            padding: 4px;
            font-family: {font};
        }}

        QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {{
            border: 2px solid #0066cc;
        }}

        QPushButton {{
            background-color: #f0f0f0;
            color: #333333;
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 6px 12px;
            font-family: {font};
            min-width: 80px;
        }}

        QPushButton:hover {{
            background-color: #e0e0e0;
        }}

        QPushButton:pressed {{
            background-color: #d0d0d0;
        }}

        QPushButton:default {{
            background-color: #0066cc;
            color: white;
            border-color: #0055aa;
        }}

        QPushButton:default:hover {{
            background-color: #0055aa;
        }}

        QCheckBox {{
            color: {fg_color};
            font-family: {font};
        }}
        """

        self.setStyleSheet(stylesheet)


class SimpleMessageDialog(ThemedDialog):
    """Simple message dialog with custom styling."""

    def __init__(self, title, message, icon=None, parent=None):
        super().__init__(title, parent)
        self.setup_ui(message, icon)

    def setup_ui(self, message, icon):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)

        # Message layout
        message_layout = QHBoxLayout()

        # Icon (if provided)
        if icon:
            icon_label = QLabel()
            # You could set an actual icon here
            icon_label.setText("ℹ️")  # Using emoji as placeholder
            icon_label.setStyleSheet("font-size: 32px;")
            message_layout.addWidget(icon_label)

        # Message
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_layout.addWidget(message_label)

        layout.addLayout(message_layout)

        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)


class InputDialog(ThemedDialog):
    """Input dialog for getting user input."""

    def __init__(self, title, prompt, default_text="", parent=None):
        super().__init__(title, parent)
        self._input_value = ""
        self.setup_ui(prompt, default_text)

    def setup_ui(self, prompt, default_text):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)

        # Prompt
        prompt_label = QLabel(prompt)
        layout.addWidget(prompt_label)

        # Input field
        self.input_field = QLineEdit(default_text)
        self.input_field.selectAll()
        layout.addWidget(self.input_field)

        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Set focus to input field
        self.input_field.setFocus()

    def accept(self):
        """Accept the dialog and store input value."""
        self._input_value = self.input_field.text()
        super().accept()

    def get_input(self):
        """Get the input value."""
        return self._input_value

    @staticmethod
    def get_text(parent, title, prompt, default_text=""):
        """Static method to get text input from user."""
        dialog = InputDialog(title, prompt, default_text, parent)
        if dialog.exec() == QDialog.Accepted:
            return dialog.get_input(), True
        return "", False


class SettingsDialog(ThemedDialog):
    """Settings dialog with various controls."""

    settings_changed = Signal(dict)

    def __init__(self, initial_settings=None, parent=None):
        super().__init__("Settings", parent)
        self._settings = initial_settings or {}
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Set up the settings dialog UI."""
        layout = QVBoxLayout(self)

        # Form layout for settings
        form_layout = QFormLayout()

        # Name setting
        self.name_edit = QLineEdit()
        form_layout.addRow("Name:", self.name_edit)

        # Theme setting
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "Blue", "Custom"])
        form_layout.addRow("Theme:", self.theme_combo)

        # Font size setting
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(12)
        form_layout.addRow("Font Size:", self.font_size_spin)

        # Auto save setting
        self.auto_save_check = QCheckBox("Enable auto save")
        form_layout.addRow("", self.auto_save_check)

        # Notes
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(100)
        self.notes_edit.setPlaceholderText("Additional notes...")
        form_layout.addRow("Notes:", self.notes_edit)

        layout.addLayout(form_layout)

        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.Apply).clicked.connect(self.apply_settings)
        layout.addWidget(button_box)

    def load_settings(self):
        """Load settings into the dialog."""
        self.name_edit.setText(self._settings.get("name", ""))

        theme = self._settings.get("theme", "Light")
        index = self.theme_combo.findText(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)

        self.font_size_spin.setValue(self._settings.get("font_size", 12))
        self.auto_save_check.setChecked(self._settings.get("auto_save", False))
        self.notes_edit.setPlainText(self._settings.get("notes", ""))

    def get_settings(self):
        """Get current settings from the dialog."""
        return {
            "name": self.name_edit.text(),
            "theme": self.theme_combo.currentText(),
            "font_size": self.font_size_spin.value(),
            "auto_save": self.auto_save_check.isChecked(),
            "notes": self.notes_edit.toPlainText(),
        }

    def apply_settings(self):
        """Apply settings without closing dialog."""
        settings = self.get_settings()
        self._settings = settings
        self.settings_changed.emit(settings)

    def accept(self):
        """Accept and apply settings."""
        self.apply_settings()
        super().accept()


class DialogDemo(ThemedWidget):
    """Demo window showing various themed dialogs."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Themed Dialog Demo")
        self.setMinimumSize(600, 400)

        # Current settings
        self.settings = {
            "name": "Demo User",
            "theme": "Light",
            "font_size": 12,
            "auto_save": True,
            "notes": "This is a demo application.",
        }

        self.setup_ui()

    def setup_ui(self):
        """Set up the demo UI."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Themed Dialog Examples")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Dialog buttons
        buttons_layout = QVBoxLayout()

        # Simple message dialog
        msg_btn = QPushButton("Show Message Dialog")
        msg_btn.clicked.connect(self.show_message_dialog)
        buttons_layout.addWidget(msg_btn)

        # Input dialog
        input_btn = QPushButton("Show Input Dialog")
        input_btn.clicked.connect(self.show_input_dialog)
        buttons_layout.addWidget(input_btn)

        # Settings dialog
        settings_btn = QPushButton("Show Settings Dialog")
        settings_btn.clicked.connect(self.show_settings_dialog)
        buttons_layout.addWidget(settings_btn)

        # Qt message box (themed)
        qt_msg_btn = QPushButton("Show Qt Message Box")
        qt_msg_btn.clicked.connect(self.show_qt_message_box)
        buttons_layout.addWidget(qt_msg_btn)

        # Modeless dialog
        modeless_btn = QPushButton("Show Modeless Dialog")
        modeless_btn.clicked.connect(self.show_modeless_dialog)
        buttons_layout.addWidget(modeless_btn)

        layout.addLayout(buttons_layout)

        # Status area
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("border: 1px solid #ccc; padding: 5px; margin: 10px;")
        layout.addWidget(self.status_label)

        # Theme controls
        layout.addStretch()
        self.create_theme_controls(layout)

    def show_message_dialog(self):
        """Show a simple message dialog."""
        dialog = SimpleMessageDialog(
            "Information",
            "This is a themed message dialog.\n\nIt adapts to the current theme automatically.",
            "info",
            self,
        )
        dialog.exec()
        self.status_label.setText("Message dialog closed")

    def show_input_dialog(self):
        """Show an input dialog."""
        text, ok = InputDialog.get_text(self, "Input Required", "Enter your name:", "Default Name")

        if ok:
            self.status_label.setText(f"Input received: {text}")
        else:
            self.status_label.setText("Input dialog cancelled")

    def show_settings_dialog(self):
        """Show a settings dialog."""
        dialog = SettingsDialog(self.settings.copy(), self)
        dialog.settings_changed.connect(self.on_settings_changed)

        if dialog.exec() == QDialog.Accepted:
            self.settings = dialog.get_settings()
            self.status_label.setText("Settings saved")
        else:
            self.status_label.setText("Settings cancelled")

    def show_qt_message_box(self):
        """Show a Qt message box (themed by application)."""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Do you want to continue with this action?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.status_label.setText("User confirmed action")
        else:
            self.status_label.setText("User cancelled action")

    def show_modeless_dialog(self):
        """Show a modeless dialog."""
        dialog = ThemedDialog("Modeless Dialog", self)
        dialog.setModal(False)

        layout = QVBoxLayout(dialog)

        label = QLabel("This is a modeless dialog.\nYou can interact with the main window.")
        layout.addWidget(label)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.show()
        self.status_label.setText("Modeless dialog opened")

    def on_settings_changed(self, settings):
        """Handle settings changes."""
        self.status_label.setText(f"Settings applied: Theme={settings['theme']}")

    def create_theme_controls(self, layout):
        """Create theme switching controls."""
        controls_layout = QHBoxLayout()

        # Theme buttons
        light_btn = QPushButton("Light Theme")
        light_btn.clicked.connect(lambda: self.switch_theme("light"))
        controls_layout.addWidget(light_btn)

        dark_btn = QPushButton("Dark Theme")
        dark_btn.clicked.connect(lambda: self.switch_theme("dark"))
        controls_layout.addWidget(dark_btn)

        blue_btn = QPushButton("Blue Theme")
        blue_btn.clicked.connect(lambda: self.switch_theme("blue"))
        controls_layout.addWidget(blue_btn)

        layout.addLayout(controls_layout)

    def switch_theme(self, theme_name):
        """Switch to a different theme."""
        app = ThemedApplication.instance()
        if app:
            try:
                app.set_theme(theme_name)
                self.status_label.setText(f"Switched to {theme_name} theme")
            except Exception as e:
                self.status_label.setText(f"Could not switch theme: {e}")


def main():
    """Run the themed dialog demo."""
    # Create themed application
    app = ThemedApplication(sys.argv)

    # Define themes with dialog styling
    light_theme = {
        "name": "light",
        "dialog": {
            "background": "#ffffff",
            "foreground": "#333333",
            "border": "#cccccc",
            "title": {"background": "#f0f0f0", "foreground": "#000000"},
            "button": {"background": "#f0f0f0", "foreground": "#333333", "border": "#cccccc"},
            "font": "Arial, sans-serif",
        },
    }

    dark_theme = {
        "name": "dark",
        "dialog": {
            "background": "#2d2d2d",
            "foreground": "#ffffff",
            "border": "#555555",
            "title": {"background": "#3a3a3a", "foreground": "#ffffff"},
            "button": {"background": "#555555", "foreground": "#ffffff", "border": "#777777"},
            "font": "Arial, sans-serif",
        },
    }

    blue_theme = {
        "name": "blue",
        "dialog": {
            "background": "#f0f6ff",
            "foreground": "#003366",
            "border": "#b3d9ff",
            "title": {"background": "#e6f2ff", "foreground": "#003366"},
            "button": {"background": "#e6f2ff", "foreground": "#003366", "border": "#b3d9ff"},
            "font": "Arial, sans-serif",
        },
    }

    # Register themes
    app.register_theme("light", light_theme)
    app.register_theme("dark", dark_theme)
    app.register_theme("blue", blue_theme)

    # Set initial theme
    app.set_theme("light")

    # Create and show demo
    demo = DialogDemo()
    demo.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
