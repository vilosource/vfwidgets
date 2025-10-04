#!/usr/bin/env python3
"""Example 09: Theme Editor Dialog - Visual Theme Customization
================================================================

Demonstrates using the ThemeEditorDialog for visual theme creation
and editing with import/export capabilities.

What you'll learn:
- How to open the theme editor dialog
- Creating new themes visually
- Editing existing themes
- Importing and exporting themes
- Live preview and validation

Features showcased:
- Phase 1: Token browser (200 tokens organized by category)
- Phase 2: Visual color/font editors
- Phase 3: Live preview with sample widgets
- Phase 4: Accessibility validation (WCAG AA/AAA)
- Phase 5: Import/Export with metadata editing

Run:
    python examples/09_theme_editor_dialog.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtWidgets import (
    QGroupBox,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from vfwidgets_theme import ThemedApplication, ThemedMainWindow, ThemedQWidget
from vfwidgets_theme.widgets import ThemeEditorDialog


class ThemeEditorDemo(ThemedMainWindow):
    """Demo application for theme editor."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Theme Editor - Visual Theme Customization")
        self.setMinimumSize(600, 500)
        self.setup_ui()

    def setup_ui(self):
        """Setup UI."""
        central = ThemedQWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title = QLabel("🎨 Visual Theme Editor")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # Description
        desc = QLabel(
            "The Theme Editor provides a complete visual interface for\n"
            "creating and customizing themes without writing code."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Features
        features_group = QGroupBox("Theme Editor Features")
        features_layout = QVBoxLayout(features_group)

        features = QTextEdit()
        features.setReadOnly(True)
        features.setMaximumHeight(200)
        features.setPlainText(
            "✅ TOKEN BROWSER\n"
            "   • 200 theme tokens organized into 15 categories\n"
            "   • Search and filter tokens\n"
            "   • Hierarchical tree view\n\n"
            "✅ VISUAL EDITORS\n"
            "   • Color picker with hex/rgb/rgba formats\n"
            "   • Font selection with preview\n"
            "   • Live token updates\n\n"
            "✅ LIVE PREVIEW\n"
            "   • Real-time preview with sample widgets\n"
            "   • See changes instantly\n"
            "   • Comprehensive widget samples\n\n"
            "✅ VALIDATION\n"
            "   • WCAG AA/AAA accessibility checking\n"
            "   • Contrast ratio calculations\n"
            "   • Error and warning display\n\n"
            "✅ IMPORT/EXPORT\n"
            "   • Save themes as JSON files\n"
            "   • Load existing theme files\n"
            "   • Edit theme metadata"
        )
        features_layout.addWidget(features)

        layout.addWidget(features_group)

        # Buttons
        button_group = QGroupBox("Try It Out")
        button_layout = QVBoxLayout(button_group)

        # Create theme button
        create_btn = QPushButton("📝 Create New Theme")
        create_btn.setMinimumHeight(44)
        create_btn.clicked.connect(self.create_theme)
        button_layout.addWidget(create_btn)

        # Edit current theme button
        edit_btn = QPushButton("✏️ Edit Current Theme")
        edit_btn.setMinimumHeight(44)
        edit_btn.clicked.connect(self.edit_current_theme)
        button_layout.addWidget(edit_btn)

        layout.addWidget(button_group)

        layout.addStretch()

        # Info
        info = QLabel(
            "💡 The theme editor is a complete visual tool for theme customization.\n"
            "Create professional themes without touching a single line of code!"
        )
        info.setAlignment(alignment=None)
        info.setWordWrap(True)
        info.setStyleSheet("font-size: 11px; color: #888; padding: 10px;")
        layout.addWidget(info)

    def create_theme(self):
        """Open theme editor to create a new theme."""
        app = ThemedApplication.instance()
        current_theme = str(app.current_theme_name) if app else "dark"

        # Open theme editor in create mode
        dialog = ThemeEditorDialog(
            parent=self,
            base_theme=current_theme,
            mode="create",
        )

        # Show dialog
        if dialog.exec():
            # User clicked OK - theme was saved
            theme = dialog.get_theme()
            print(f"✅ Theme created: {theme.name}")
        else:
            # User clicked Cancel
            print("❌ Theme creation cancelled")

    def edit_current_theme(self):
        """Open theme editor to edit current theme."""
        app = ThemedApplication.instance()
        current_theme = str(app.current_theme_name) if app else "dark"

        # Open theme editor in edit mode
        dialog = ThemeEditorDialog(
            parent=self,
            base_theme=current_theme,
            mode="edit",
        )

        # Show dialog
        if dialog.exec():
            theme = dialog.get_theme()
            print(f"✅ Theme edited: {theme.name}")

            # Apply the edited theme
            if app:
                app.theme_manager.register_theme(theme)
                app.set_theme(theme.name)


def main():
    """Main entry point."""
    app = ThemedApplication(sys.argv)
    app.set_theme("dark")

    window = ThemeEditorDemo()
    window.show()

    print("\n" + "=" * 60)
    print("THEME EDITOR DEMO")
    print("=" * 60)
    print("\nClick 'Create New Theme' to open the visual theme editor!")
    print("\nFeatures:")
    print("  • Browse and edit 200 theme tokens")
    print("  • Visual color and font pickers")
    print("  • Live preview of changes")
    print("  • WCAG accessibility validation")
    print("  • Import/Export themes as JSON")
    print("\n" + "=" * 60 + "\n")

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
