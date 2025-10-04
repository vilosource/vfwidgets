#!/usr/bin/env python3
"""Example 08: Custom Themes - Creating Your Own Themes
========================================================

Demonstrates how to create custom themes programmatically using
ThemeBuilder and theme composition.

What you'll learn:
- Creating themes from scratch with ThemeBuilder
- Theme inheritance with .extend()
- Theme composition with ThemeComposer
- Registering custom themes with the application

Key APIs:
- ThemeBuilder: Fluent API for theme construction
- .extend(parent): Inherit from existing theme
- ThemeComposer: Merge multiple themes

Run:
    python examples/08_custom_themes.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from vfwidgets_theme import ThemedApplication, ThemedMainWindow, ThemedQWidget
from vfwidgets_theme.core.theme import ThemeBuilder


class CustomThemesDemo(ThemedMainWindow):
    """Demo of custom theme creation."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Custom Themes - Create Your Own")
        self.setMinimumSize(700, 600)
        self.create_custom_themes()
        self.setup_ui()

    def create_custom_themes(self):
        """Create and register custom themes."""
        app = ThemedApplication.instance()

        # 1. Theme from scratch
        purple_theme = (
            ThemeBuilder("purple")
            .set_type("dark")
            .add_color("colors.background", "#1a0033")
            .add_color("colors.foreground", "#e0d0ff")
            .add_color("button.background", "#6b2c91")
            .add_color("button.foreground", "#ffffff")
            .add_color("button.hoverBackground", "#8b3cb1")
            .add_color("input.background", "#2d1b4e")
            .add_color("input.foreground", "#e0d0ff")
            .build()
        )

        # 2. Theme inheritance (extend existing)
        ocean_theme = (
            ThemeBuilder("ocean")
            .extend("dark")  # Inherit from dark theme
            .add_color("colors.background", "#001a2e")  # Override just a few colors
            .add_color("button.background", "#0077be")
            .add_color("button.hoverBackground", "#0096ed")
            .build()
        )

        # 3. High contrast variant
        high_contrast = (
            ThemeBuilder("high_contrast")
            .extend("light")  # Start from light
            .add_color("colors.background", "#ffffff")  # Maximum contrast
            .add_color("colors.foreground", "#000000")
            .add_color("button.background", "#000000")
            .add_color("button.foreground", "#ffffff")
            .add_color("input.border", "#000000")
            .build()
        )

        # Register custom themes
        if app:
            app.theme_manager.register_theme(purple_theme)
            app.theme_manager.register_theme(ocean_theme)
            app.theme_manager.register_theme(high_contrast)

    def setup_ui(self):
        """Setup UI."""
        central = ThemedQWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("🎨 Custom Theme Creation")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # Theme selector
        theme_group = QGroupBox("Try Custom Themes")
        theme_layout = QVBoxLayout(theme_group)

        theme_layout.addWidget(QLabel("Select a theme:"))

        self.theme_combo = QComboBox()
        self.theme_combo.setMinimumHeight(36)

        app = ThemedApplication.instance()
        if app:
            themes = app.available_themes
            self.theme_combo.addItems(themes)

        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        theme_layout.addWidget(self.theme_combo)

        layout.addWidget(theme_group)

        # Code example
        code_group = QGroupBox("How These Were Created")
        code_layout = QVBoxLayout(code_group)

        code_example = QTextEdit()
        code_example.setReadOnly(True)
        code_example.setMaximumHeight(250)
        code_example.setPlainText(
            "# 1. From scratch\n"
            "purple_theme = (ThemeBuilder('purple')\n"
            "    .set_type('dark')\n"
            "    .add_color('colors.background', '#1a0033')\n"
            "    .add_color('button.background', '#6b2c91')\n"
            "    .build())\n\n"
            "# 2. Inheritance (extend existing)\n"
            "ocean_theme = (ThemeBuilder('ocean')\n"
            "    .extend('dark')  # Inherit everything from dark\n"
            "    .add_color('colors.background', '#001a2e')  # Override\n"
            "    .build())\n\n"
            "# 3. Register with app\n"
            "app.theme_manager.register_theme(purple_theme)"
        )
        code_layout.addWidget(code_example)

        layout.addWidget(code_group)

        # Sample widgets
        sample_group = QGroupBox("Sample Widgets")
        sample_layout = QVBoxLayout(sample_group)

        for text in ["Button 1", "Button 2", "Button 3"]:
            btn = QPushButton(text)
            btn.setMinimumHeight(36)
            sample_layout.addWidget(btn)

        layout.addWidget(sample_group)

        layout.addStretch()

        # Info
        info = QLabel(
            "💡 ThemeBuilder uses a fluent API for easy theme construction.\n"
            "Use .extend() to inherit from existing themes and only override what you need!"
        )
        info.setWordWrap(True)
        info.setStyleSheet("font-size: 11px; color: #888;")
        layout.addWidget(info)

    def on_theme_changed(self, theme_name: str):
        """Handle theme change."""
        if theme_name:
            app = ThemedApplication.instance()
            if app:
                app.set_theme(theme_name)


def main():
    """Main entry point."""
    app = ThemedApplication(sys.argv)

    window = CustomThemesDemo()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
