#!/usr/bin/env python3
"""Example 17: Branded Application - Declarative Theme Configuration

This example demonstrates VFThemedApplication with declarative branding:
- Subclass VFThemedApplication with theme_config class attribute
- Define app-level color overrides for branding
- Automatic application of branding on startup
- User preferences persistence

This is the recommended pattern for applications that need consistent branding
across all themes while still allowing users to choose dark/light themes.

Usage:
    python examples/17_branded_app.py
"""

import sys

from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from vfwidgets_theme import ThemedWidget
from vfwidgets_theme.core.manager import ThemeManager
from vfwidgets_theme.widgets.vf_themed_application import VFThemedApplication


class BrandedApp(VFThemedApplication):
    """Example branded application with declarative theme config.

    This application defines brand colors that override theme defaults:
    - Purple accent color (#7c3aed) for primary UI elements
    - Teal accent (#14b8a6) for secondary elements
    - Custom editor background for consistency

    Users can still switch between dark/light themes, but the
    brand colors remain consistent.
    """

    theme_config = {
        # Base theme (user can change this)
        "base_theme": "dark",

        # App-level branding overrides (consistent across all themes)
        "app_overrides": {
            # Editor colors
            "editor.background": "#1e1e2e",
            "editor.foreground": "#cdd6f4",

            # UI accent colors
            "tab.activeBackground": "#7c3aed",  # Purple brand color
            "button.background": "#313244",
            "button.hoverBackground": "#7c3aed",  # Purple on hover

            # Status bar
            "statusBar.background": "#14b8a6",  # Teal brand color
            "statusBar.foreground": "#ffffff",
        },

        # Allow user customization (will be saved)
        "allow_user_customization": True,

        # Persist preferences
        "persist_base_theme": True,
        "persist_user_overrides": True,
    }


class BrandedDemoWindow(ThemedWidget):
    """Demo window showing branded app in action."""

    theme_config = {
        "background": "editor.background",
        "foreground": "editor.foreground",
    }

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Branded Application Example")
        title.setStyleSheet(
            "font-size: 20pt; font-weight: bold; padding: 15px; "
            "color: #7c3aed;"  # Purple brand color
        )
        layout.addWidget(title)

        # Description
        desc = QLabel(
            "This application demonstrates declarative branding with VFThemedApplication.\n\n"
            "Notice the purple and teal accent colors - these are brand colors defined "
            "in the app's theme_config. They remain consistent even when you switch themes.\n\n"
            "Try switching between dark and light themes to see the branding persist!"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("padding: 10px;")
        layout.addWidget(desc)

        # Brand info
        brand_group = QGroupBox("Brand Colors")
        brand_layout = QVBoxLayout(brand_group)

        brand_layout.addWidget(QLabel("🟣 Primary: Purple (#7c3aed) - Tabs, buttons"))
        brand_layout.addWidget(QLabel("🔵 Secondary: Teal (#14b8a6) - Status bar"))
        brand_layout.addWidget(QLabel("⚫ Editor: Dark Blue (#1e1e2e) - Background"))

        layout.addWidget(brand_group)

        # Editor demo
        editor_group = QGroupBox("Branded Editor")
        editor_layout = QVBoxLayout(editor_group)

        self.editor = QTextEdit()
        self.editor.setPlainText(
            "# Branded Editor\n"
            "# Background color: #1e1e2e (brand color)\n"
            "# Foreground color: #cdd6f4 (brand color)\n\n"
            "class BrandedApp(VFThemedApplication):\n"
            "    theme_config = {\n"
            '        "base_theme": "dark",\n'
            '        "app_overrides": {\n'
            '            "editor.background": "#1e1e2e",\n'
            '            "tab.activeBackground": "#7c3aed",\n'
            "            # ... more overrides ...\n"
            "        },\n"
            "    }\n"
        )
        self.editor.setMinimumHeight(200)
        editor_layout.addWidget(self.editor)

        layout.addWidget(editor_group)

        # Controls
        controls_group = QGroupBox("Theme Controls")
        controls_layout = QVBoxLayout(controls_group)

        # Theme selector
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Base Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        controls_layout.addLayout(theme_layout)

        # Brand override info
        self.override_info = QLabel()
        self.update_override_info()
        controls_layout.addWidget(self.override_info)

        # Reset button
        btn_reset = QPushButton("Clear User Customizations")
        btn_reset.clicked.connect(self.clear_user_customizations)
        controls_layout.addWidget(btn_reset)

        layout.addWidget(controls_group)

    def change_theme(self, theme_name: str):
        """Change base theme (branding persists)."""
        app = VFThemedApplication.instance()
        if app:
            app.set_theme(theme_name)
            self.update_override_info()

    def clear_user_customizations(self):
        """Clear user customizations (keep app branding)."""
        app = VFThemedApplication.instance()
        if app:
            app.clear_user_preferences()
            self.update_override_info()

    def update_override_info(self):
        """Update override information display."""
        manager = ThemeManager.get_instance()
        app_overrides = manager.get_app_overrides()
        user_overrides = manager.get_user_overrides()

        text = (
            f"App Branding: {len(app_overrides)} overrides active\n"
            f"User Customizations: {len(user_overrides)} overrides"
        )
        self.override_info.setText(text)


def main():
    """Main entry point."""
    # Create branded application (automatically applies branding)
    app = BrandedApp(sys.argv, app_id="BrandedDemo")

    # Create and show main window
    window = BrandedDemoWindow()
    window.setWindowTitle("Example 17: Branded Application")
    window.resize(700, 650)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
