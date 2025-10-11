#!/usr/bin/env python3
"""
themed_input.py - Themed input field with validation styling

Shows how to create input fields that respond to theme changes and
provide visual feedback for validation states.

Key Concepts:
- Input field theming
- Validation state styling
- Focus state handling
- Placeholder text styling

Example usage:
    python themed_input.py
"""

import re
import sys

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout

from vfwidgets_theme import ThemedApplication, ThemedWidget


class ThemedInput(ThemedWidget, QLineEdit):
    """A themed input field with validation state styling."""

    theme_config = {
        "bg": "input.background",
        "fg": "input.foreground",
        "border": "input.border",
        "focus_border": "input.focus.border",
        "error_border": "input.error.border",
        "success_border": "input.success.border",
        "warning_border": "input.warning.border",
        "placeholder": "input.placeholder",
        "font": "input.font",
    }

    # Validation state changed signal
    validation_changed = Signal(str)  # 'valid', 'invalid', 'warning', 'empty'

    def __init__(self, placeholder="", validation_pattern=None, parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self._validation_pattern = validation_pattern
        self._validation_state = "empty"

        # Connect signals
        self.textChanged.connect(self._on_text_changed)
        self.editingFinished.connect(self._validate_input)

        # Apply initial styling
        self.update_styling()

    def on_theme_changed(self):
        """Called automatically when theme changes."""
        self.update_styling()

    def set_validation_pattern(self, pattern):
        """Set validation regex pattern."""
        self._validation_pattern = pattern
        self._validate_input()

    def set_validation_state(self, state):
        """Manually set validation state ('valid', 'invalid', 'warning', 'empty')."""
        if state != self._validation_state:
            self._validation_state = state
            self.update_styling()
            self.validation_changed.emit(state)

    def get_validation_state(self):
        """Get current validation state."""
        return self._validation_state

    def _on_text_changed(self, text):
        """Handle text changes."""
        if not text:
            self.set_validation_state("empty")
        else:
            self._validate_input()

    def _validate_input(self):
        """Validate current input."""
        text = self.text()

        if not text:
            self.set_validation_state("empty")
            return

        if self._validation_pattern:
            if re.match(self._validation_pattern, text):
                self.set_validation_state("valid")
            else:
                self.set_validation_state("invalid")
        else:
            # No pattern = always valid if not empty
            self.set_validation_state("valid")

    def update_styling(self):
        """Update input styling based on theme and validation state."""
        # Get theme colors
        bg_color = self.theme.get("bg", "#ffffff")
        fg_color = self.theme.get("fg", "#000000")
        border_color = self.theme.get("border", "#cccccc")
        focus_border = self.theme.get("focus_border", "#0066cc")
        error_border = self.theme.get("error_border", "#cc0000")
        success_border = self.theme.get("success_border", "#00aa00")
        warning_border = self.theme.get("warning_border", "#ff9900")
        self.theme.get("placeholder", "#888888")
        font = self.theme.get("font", "Arial, sans-serif")

        # Choose border color based on validation state
        if self._validation_state == "invalid":
            pass
        elif self._validation_state == "valid":
            pass
        elif self._validation_state == "warning":
            pass
        else:  # empty
            pass

        # Generate stylesheet
        stylesheet = f"""
        QLineEdit {{
            background-color: {bg_color};
            color: {fg_color};
            border: 2px solid {border_color};
            border-radius: 4px;
            padding: 8px 12px;
            font-family: {font};
            font-size: 13px;
        }}

        QLineEdit:focus {{
            border-color: {focus_border};
        }}

        QLineEdit[validation_state="invalid"] {{
            border-color: {error_border};
        }}

        QLineEdit[validation_state="valid"] {{
            border-color: {success_border};
        }}

        QLineEdit[validation_state="warning"] {{
            border-color: {warning_border};
        }}
        """

        self.setStyleSheet(stylesheet)
        # Set dynamic property for CSS selector
        self.setProperty("validation_state", self._validation_state)
        self.style().polish(self)


class ValidationLabel(ThemedWidget, QLabel):
    """Label that shows validation messages."""

    theme_config = {
        "error_color": "status.error",
        "success_color": "status.success",
        "warning_color": "status.warning",
        "info_color": "status.info",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(20)

    def on_theme_changed(self):
        """Called automatically when theme changes."""
        self.update_styling()

    def set_message(self, message, message_type="info"):
        """Set validation message with type ('error', 'success', 'warning', 'info')."""
        self.setText(message)
        self._message_type = message_type
        self.update_styling()

    def clear_message(self):
        """Clear the validation message."""
        self.setText("")

    def update_styling(self):
        """Update label styling based on message type."""
        if not hasattr(self, "_message_type"):
            return

        # Get theme colors
        error_color = self.theme.get("error_color", "#cc0000")
        success_color = self.theme.get("success_color", "#00aa00")
        warning_color = self.theme.get("warning_color", "#ff9900")
        info_color = self.theme.get("info_color", "#0066cc")

        # Choose color based on message type
        color_map = {
            "error": error_color,
            "success": success_color,
            "warning": warning_color,
            "info": info_color,
        }

        color = color_map.get(self._message_type, info_color)

        self.setStyleSheet(
            f"""
        QLabel {{
            color: {color};
            font-size: 11px;
            font-style: italic;
        }}
        """
        )


class InputDemo(ThemedWidget):
    """Demo window showing themed input fields with validation."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Themed Input Demo")
        self.setMinimumSize(600, 500)

        # Create main layout
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Themed Input Field Examples")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Create input examples
        self.create_input_examples(layout)

        # Theme controls
        layout.addStretch()
        self.create_theme_controls(layout)

    def create_input_examples(self, layout):
        """Create various input field examples."""
        # Basic inputs group
        basic_group = QGroupBox("Basic Input Fields")
        basic_layout = QFormLayout(basic_group)

        # Simple input
        simple_input = ThemedInput("Enter any text...")
        simple_label = ValidationLabel()
        simple_input.validation_changed.connect(
            lambda state: simple_label.set_message(
                f"State: {state.title()}", "info" if state != "invalid" else "error"
            )
        )
        basic_layout.addRow("Simple Input:", simple_input)
        basic_layout.addRow("", simple_label)

        # Email input
        email_input = ThemedInput(
            "Enter email address...", r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        )
        email_label = ValidationLabel()
        email_input.validation_changed.connect(
            lambda state: self.update_email_label(email_label, state)
        )
        basic_layout.addRow("Email:", email_input)
        basic_layout.addRow("", email_label)

        # Phone input
        phone_input = ThemedInput("Enter phone number...", r"^\+?[\d\s\-\(\)]{10,}$")
        phone_label = ValidationLabel()
        phone_input.validation_changed.connect(
            lambda state: self.update_phone_label(phone_label, state)
        )
        basic_layout.addRow("Phone:", phone_input)
        basic_layout.addRow("", phone_label)

        layout.addWidget(basic_group)

        # Advanced inputs group
        advanced_group = QGroupBox("Advanced Validation")
        advanced_layout = QFormLayout(advanced_group)

        # Password input
        password_input = ThemedInput(
            "Enter password...", r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$"
        )
        password_input.setEchoMode(QLineEdit.Password)
        password_label = ValidationLabel()
        password_input.validation_changed.connect(
            lambda state: self.update_password_label(password_label, state)
        )
        advanced_layout.addRow("Password:", password_input)
        advanced_layout.addRow("", password_label)

        # URL input
        url_input = ThemedInput(
            "Enter URL...",
            r"^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$",
        )
        url_label = ValidationLabel()
        url_input.validation_changed.connect(lambda state: self.update_url_label(url_label, state))
        advanced_layout.addRow("URL:", url_input)
        advanced_layout.addRow("", url_label)

        layout.addWidget(advanced_group)

    def update_email_label(self, label, state):
        """Update email validation label."""
        messages = {
            "empty": ("Enter an email address", "info"),
            "invalid": ("Please enter a valid email address", "error"),
            "valid": ("Valid email address", "success"),
        }
        msg, msg_type = messages.get(state, ("", "info"))
        label.set_message(msg, msg_type)

    def update_phone_label(self, label, state):
        """Update phone validation label."""
        messages = {
            "empty": ("Enter a phone number", "info"),
            "invalid": ("Please enter a valid phone number", "error"),
            "valid": ("Valid phone number", "success"),
        }
        msg, msg_type = messages.get(state, ("", "info"))
        label.set_message(msg, msg_type)

    def update_password_label(self, label, state):
        """Update password validation label."""
        messages = {
            "empty": (
                "Password must be at least 8 characters with uppercase, lowercase, and number",
                "info",
            ),
            "invalid": ("Password does not meet requirements", "error"),
            "valid": ("Strong password", "success"),
        }
        msg, msg_type = messages.get(state, ("", "info"))
        label.set_message(msg, msg_type)

    def update_url_label(self, label, state):
        """Update URL validation label."""
        messages = {
            "empty": ("Enter a URL starting with http:// or https://", "info"),
            "invalid": ("Please enter a valid URL", "error"),
            "valid": ("Valid URL", "success"),
        }
        msg, msg_type = messages.get(state, ("", "info"))
        label.set_message(msg, msg_type)

    def create_theme_controls(self, layout):
        """Create theme switching controls."""
        from .themed_button import ThemedButton

        controls_layout = QHBoxLayout()

        # Theme buttons
        light_btn = ThemedButton("Light Theme")
        light_btn.clicked.connect(lambda: self.switch_theme("light"))
        controls_layout.addWidget(light_btn)

        dark_btn = ThemedButton("Dark Theme")
        dark_btn.clicked.connect(lambda: self.switch_theme("dark"))
        controls_layout.addWidget(dark_btn)

        high_contrast_btn = ThemedButton("High Contrast")
        high_contrast_btn.clicked.connect(lambda: self.switch_theme("high_contrast"))
        controls_layout.addWidget(high_contrast_btn)

        layout.addLayout(controls_layout)

    def switch_theme(self, theme_name):
        """Switch to a different theme."""
        app = ThemedApplication.instance()
        if app:
            try:
                app.set_theme(theme_name)
                print(f"Switched to {theme_name} theme")
            except Exception as e:
                print(f"Could not switch to {theme_name} theme: {e}")


def main():
    """Run the themed input demo."""
    # Create themed application
    app = ThemedApplication(sys.argv)

    # Define themes with input styling
    light_theme = {
        "name": "light",
        "input": {
            "background": "#ffffff",
            "foreground": "#333333",
            "border": "#cccccc",
            "focus": {"border": "#0066cc"},
            "error": {"border": "#cc3333"},
            "success": {"border": "#33aa33"},
            "warning": {"border": "#ff9933"},
            "placeholder": "#999999",
            "font": "Arial, sans-serif",
        },
        "status": {
            "error": "#cc3333",
            "success": "#33aa33",
            "warning": "#ff9933",
            "info": "#0066cc",
        },
        "button": {
            "background": "#f0f0f0",
            "foreground": "#333333",
            "border": "#cccccc",
            "hover": {"background": "#e0e0e0"},
            "pressed": {"background": "#d0d0d0"},
            "font": "Arial, sans-serif",
        },
    }

    dark_theme = {
        "name": "dark",
        "input": {
            "background": "#3a3a3a",
            "foreground": "#ffffff",
            "border": "#555555",
            "focus": {"border": "#66aaff"},
            "error": {"border": "#ff6666"},
            "success": {"border": "#66ff66"},
            "warning": {"border": "#ffaa66"},
            "placeholder": "#aaaaaa",
            "font": "Arial, sans-serif",
        },
        "status": {
            "error": "#ff6666",
            "success": "#66ff66",
            "warning": "#ffaa66",
            "info": "#66aaff",
        },
        "button": {
            "background": "#555555",
            "foreground": "#ffffff",
            "border": "#777777",
            "hover": {"background": "#666666"},
            "pressed": {"background": "#444444"},
            "font": "Arial, sans-serif",
        },
    }

    high_contrast_theme = {
        "name": "high_contrast",
        "input": {
            "background": "#000000",
            "foreground": "#ffffff",
            "border": "#ffffff",
            "focus": {"border": "#ffff00"},
            "error": {"border": "#ff0000"},
            "success": {"border": "#00ff00"},
            "warning": {"border": "#ff8800"},
            "placeholder": "#cccccc",
            "font": "Arial, sans-serif",
        },
        "status": {
            "error": "#ff0000",
            "success": "#00ff00",
            "warning": "#ff8800",
            "info": "#ffff00",
        },
        "button": {
            "background": "#333333",
            "foreground": "#ffffff",
            "border": "#ffffff",
            "hover": {"background": "#555555"},
            "pressed": {"background": "#222222"},
            "font": "Arial, sans-serif",
        },
    }

    # Register themes
    app.register_theme("light", light_theme)
    app.register_theme("dark", dark_theme)
    app.register_theme("high_contrast", high_contrast_theme)

    # Set initial theme
    app.set_theme("light")

    # Create and show demo
    demo = InputDemo()
    demo.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
