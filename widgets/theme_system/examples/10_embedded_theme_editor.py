#!/usr/bin/env python3
"""Example 10: Embedded Theme Editor - Settings Integration
============================================================

Demonstrates embedding the ThemeEditorWidget into application settings
or preferences dialogs.

What you'll learn:
- How to embed ThemeEditorWidget in custom dialogs
- Integration with application settings
- Using theme editor as part of larger UI

This pattern is useful for:
- Application preferences/settings dialogs
- Configuration panels
- Customization interfaces

Run:
    python examples/10_embedded_theme_editor.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtWidgets import (
    QCheckBox,
    QDialogButtonBox,
    QLabel,
    QTabWidget,
    QVBoxLayout,
)

from vfwidgets_theme import ThemedApplication, ThemedDialog, ThemedMainWindow, ThemedQWidget
from vfwidgets_theme.widgets import ThemeEditorWidget


class PreferencesDialog(ThemedDialog):
    """Application preferences dialog with embedded theme editor."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Application Preferences")
        self.setMinimumSize(1000, 700)
        self.setup_ui()

    def setup_ui(self):
        """Setup UI."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("⚙️ Application Preferences")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        # Tabs for different settings sections
        tabs = QTabWidget()

        # General settings tab
        general_tab = ThemedQWidget()
        general_layout = QVBoxLayout(general_tab)
        general_layout.addWidget(QLabel("General Settings:"))
        general_layout.addWidget(QCheckBox("Enable auto-save"))
        general_layout.addWidget(QCheckBox("Show line numbers"))
        general_layout.addWidget(QCheckBox("Enable word wrap"))
        general_layout.addStretch()
        tabs.addTab(general_tab, "General")

        # Appearance tab with embedded theme editor
        appearance_tab = ThemedQWidget()
        appearance_layout = QVBoxLayout(appearance_tab)

        info = QLabel("Customize the application theme visually.\nChanges preview in real-time!")
        info.setWordWrap(True)
        info.setStyleSheet("padding: 10px;")
        appearance_layout.addWidget(info)

        # EMBEDDED THEME EDITOR
        self.theme_editor = ThemeEditorWidget(
            base_theme="dark",
            show_preview=True,  # Show live preview
            show_validation=True,  # Show accessibility validation
            compact_mode=False,  # Full-featured mode
        )
        appearance_layout.addWidget(self.theme_editor)

        tabs.addTab(appearance_tab, "Appearance")

        # Advanced settings tab
        advanced_tab = ThemedQWidget()
        advanced_layout = QVBoxLayout(advanced_tab)
        advanced_layout.addWidget(QLabel("Advanced Settings:"))
        advanced_layout.addWidget(QCheckBox("Enable debug mode"))
        advanced_layout.addWidget(QCheckBox("Use hardware acceleration"))
        advanced_layout.addStretch()
        tabs.addTab(advanced_tab, "Advanced")

        layout.addWidget(tabs)

        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Apply
        )
        button_box.accepted.connect(self.on_accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.on_apply)
        layout.addWidget(button_box)

    def on_apply(self):
        """Apply settings without closing."""
        # Get theme from editor
        theme = self.theme_editor.get_theme()

        # Register and apply
        app = ThemedApplication.instance()
        if app:
            app.theme_manager.register_theme(theme)
            app.set_theme(theme.name)

        print(f"✅ Theme applied: {theme.name}")

    def on_accept(self):
        """OK button clicked."""
        self.on_apply()
        self.accept()


class EmbeddedEditorDemo(ThemedMainWindow):
    """Demo application."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Embedded Theme Editor - Settings Integration")
        self.setMinimumSize(600, 400)
        self.setup_ui()

    def setup_ui(self):
        """Setup UI."""
        central = ThemedQWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # Title
        title = QLabel("🎨 Embedded Theme Editor")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # Description
        desc = QLabel(
            "This example shows how to embed the ThemeEditorWidget\n"
            "into your application's preferences or settings dialog.\n\n"
            "Click the button below to open the preferences dialog\n"
            "with the theme editor embedded in the 'Appearance' tab."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addStretch()

        # Open preferences button
        from PySide6.QtWidgets import QPushButton

        prefs_btn = QPushButton("⚙️ Open Preferences")
        prefs_btn.setMinimumHeight(50)
        prefs_btn.clicked.connect(self.show_preferences)
        layout.addWidget(prefs_btn)

        layout.addStretch()

        # Info
        info = QLabel(
            "💡 Use case: Embed ThemeEditorWidget in settings dialogs\n"
            "for seamless theme customization within your app!"
        )
        info.setWordWrap(True)
        info.setStyleSheet("font-size: 11px; color: #888;")
        layout.addWidget(info)

    def show_preferences(self):
        """Show preferences dialog."""
        dialog = PreferencesDialog(self)
        dialog.exec()


def main():
    """Main entry point."""
    app = ThemedApplication(sys.argv)
    app.set_theme("dark")

    window = EmbeddedEditorDemo()
    window.show()

    print("\n" + "=" * 60)
    print("EMBEDDED THEME EDITOR DEMO")
    print("=" * 60)
    print("\nClick 'Open Preferences' to see the theme editor")
    print("embedded in the Appearance tab!")
    print("\nPattern:")
    print("  theme_editor = ThemeEditorWidget(")
    print("      base_theme='dark',")
    print("      show_preview=True,")
    print("      show_validation=True")
    print("  )")
    print("  layout.addWidget(theme_editor)")
    print("\n" + "=" * 60 + "\n")

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
