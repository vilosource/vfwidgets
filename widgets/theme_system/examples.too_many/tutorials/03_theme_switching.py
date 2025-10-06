#!/usr/bin/env python3
"""Tutorial 03: Theme Switching.
============================

This tutorial shows advanced theme switching techniques.

What you'll learn:
- Dynamic theme management
- Theme persistence
- Global theme switching
- Theme change animations
- Multi-window theme coordination
"""

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from vfwidgets_theme import ThemedApplication, ThemedWidget


class ThemeSwitcherWidget(ThemedWidget):
    """Advanced theme switching widget with animations."""

    theme_config = {
        "bg": "window.background",
        "fg": "window.foreground",
        "accent": "accent.primary",
        "card_bg": "card.background",
        "card_border": "card.border",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_theme = "light"
        self.animation_enabled = True
        self.setup_ui()

    def setup_ui(self):
        """Set up the theme switching interface."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Advanced Theme Switching")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Theme selection group
        theme_group = QGroupBox("Theme Selection")
        theme_layout = QFormLayout(theme_group)

        # Theme dropdown
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark", "blue", "green", "purple"])
        self.theme_combo.currentTextChanged.connect(self.on_theme_selected)
        theme_layout.addRow("Theme:", self.theme_combo)

        # Animation toggle
        self.animation_check = QCheckBox("Enable Animations")
        self.animation_check.setChecked(True)
        self.animation_check.toggled.connect(self.toggle_animations)
        theme_layout.addRow("", self.animation_check)

        layout.addWidget(theme_group)

        # Quick theme buttons
        quick_group = QGroupBox("Quick Switch")
        quick_layout = QHBoxLayout(quick_group)

        themes = ["light", "dark", "blue", "green", "purple"]
        self.quick_buttons = {}

        for theme in themes:
            btn = QPushButton(theme.title())
            btn.clicked.connect(lambda checked, t=theme: self.switch_theme(t))
            self.quick_buttons[theme] = btn
            quick_layout.addWidget(btn)

        layout.addWidget(quick_group)

        # Theme preview area
        self.preview_area = QWidget()
        preview_layout = QVBoxLayout(self.preview_area)

        self.preview_label = QLabel("Theme Preview Area")
        self.preview_label.setAlignment(Qt.AlignCenter)
        preview_layout.addWidget(self.preview_label)

        self.color_display = QLabel()
        self.color_display.setAlignment(Qt.AlignCenter)
        preview_layout.addWidget(self.color_display)

        layout.addWidget(self.preview_area)

        # Global controls
        global_group = QGroupBox("Global Controls")
        global_layout = QVBoxLayout(global_group)

        self.new_window_btn = QPushButton("Open New Window")
        self.new_window_btn.clicked.connect(self.open_new_window)
        global_layout.addWidget(self.new_window_btn)

        self.sync_label = QLabel("All windows automatically sync themes!")
        self.sync_label.setAlignment(Qt.AlignCenter)
        global_layout.addWidget(self.sync_label)

        layout.addWidget(global_group)

    def on_theme_selected(self, theme_name):
        """Handle theme selection from dropdown."""
        self.switch_theme(theme_name)

    def switch_theme(self, theme_name):
        """Switch to specified theme with optional animation."""
        if theme_name == self.current_theme:
            return

        print(f"Switching from {self.current_theme} to {theme_name}")

        # Animate the transition if enabled
        if self.animation_enabled:
            self.animate_theme_change()

        # Apply the theme globally
        app = ThemedApplication.instance()
        app.set_theme(theme_name)

        self.current_theme = theme_name

        # Update UI state
        self.update_ui_state()

    def animate_theme_change(self):
        """Create a smooth transition animation."""
        # Simple fade effect
        self.setStyleSheet("QWidget { opacity: 0.5; }")
        # In a real implementation, you'd use QPropertyAnimation

    def toggle_animations(self, enabled):
        """Toggle animation support."""
        self.animation_enabled = enabled
        print(f"Animations {'enabled' if enabled else 'disabled'}")

    def update_ui_state(self):
        """Update UI elements to reflect current theme."""
        # Update combo box
        index = self.theme_combo.findText(self.current_theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)

        # Update button states
        for theme, btn in self.quick_buttons.items():
            btn.setEnabled(theme != self.current_theme)

    def open_new_window(self):
        """Open a new themed window to demonstrate global sync."""
        new_window = ThemeSwitcherWidget()
        new_window.setWindowTitle(f"Window #{id(new_window) % 1000}")
        new_window.current_theme = self.current_theme
        new_window.update_ui_state()
        new_window.show()

        # Store reference to prevent garbage collection
        if not hasattr(self, "child_windows"):
            self.child_windows = []
        self.child_windows.append(new_window)

    def on_theme_changed(self):
        """Respond to theme changes."""
        self.update_styling()
        self.update_color_display()

    def update_styling(self):
        """Apply current theme styling."""
        bg = self.theme.get("bg", "#ffffff")
        fg = self.theme.get("fg", "#000000")
        accent = self.theme.get("accent", "#0066cc")
        card_bg = self.theme.get("card_bg", "#f8f8f8")
        card_border = self.theme.get("card_border", "#dddddd")

        # Main widget styling
        self.setStyleSheet(
            f"""
        ThemeSwitcherWidget {{
            background-color: {bg};
            color: {fg};
        }}

        QGroupBox {{
            font-weight: bold;
            border: 2px solid {card_border};
            border-radius: 5px;
            margin: 5px;
            padding-top: 10px;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }}
        """
        )

        # Preview area styling
        self.preview_area.setStyleSheet(
            f"""
        QWidget {{
            background-color: {card_bg};
            border: 2px solid {accent};
            border-radius: 8px;
            padding: 10px;
            margin: 5px;
        }}
        """
        )

        self.preview_label.setStyleSheet(
            f"""
        QLabel {{
            color: {accent};
            font-size: 16px;
            font-weight: bold;
        }}
        """
        )

    def update_color_display(self):
        """Update the color display with current theme colors."""
        bg = self.theme.get("bg", "#ffffff")
        fg = self.theme.get("fg", "#000000")
        accent = self.theme.get("accent", "#0066cc")

        self.color_display.setText(
            f"""
        Background: {bg}
        Foreground: {fg}
        Accent: {accent}
        """
        )


def create_theme_variants():
    """Create multiple theme variants for switching demo."""
    themes = {
        "light": {
            "name": "light",
            "window": {"background": "#ffffff", "foreground": "#333333"},
            "card": {"background": "#f8f8f8", "border": "#dddddd"},
            "accent": {"primary": "#007bff"},
        },
        "dark": {
            "name": "dark",
            "window": {"background": "#2d2d2d", "foreground": "#ffffff"},
            "card": {"background": "#3a3a3a", "border": "#555555"},
            "accent": {"primary": "#66aaff"},
        },
        "blue": {
            "name": "blue",
            "window": {"background": "#e3f2fd", "foreground": "#0d47a1"},
            "card": {"background": "#ffffff", "border": "#90caf9"},
            "accent": {"primary": "#1976d2"},
        },
        "green": {
            "name": "green",
            "window": {"background": "#e8f5e8", "foreground": "#1b5e20"},
            "card": {"background": "#ffffff", "border": "#a5d6a7"},
            "accent": {"primary": "#388e3c"},
        },
        "purple": {
            "name": "purple",
            "window": {"background": "#f3e5f5", "foreground": "#4a148c"},
            "card": {"background": "#ffffff", "border": "#ce93d8"},
            "accent": {"primary": "#7b1fa2"},
        },
    }
    return themes


def main():
    """Main function demonstrating advanced theme switching."""
    print("Tutorial 03: Theme Switching")
    print("=" * 30)

    app = ThemedApplication(sys.argv)

    # Register all theme variants
    themes = create_theme_variants()
    for name, theme in themes.items():
        app.register_theme(name, theme)
        print(f"Registered theme: {name}")

    # Set initial theme
    app.set_theme("light")

    # Create main widget
    widget = ThemeSwitcherWidget()
    widget.setWindowTitle("Tutorial 03: Theme Switching")
    widget.setMinimumSize(600, 500)
    widget.show()

    print("\nTheme switching demo ready!")
    print("- Use dropdown or buttons to switch themes")
    print("- Open multiple windows to see global sync")
    print("- Toggle animations on/off")

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
