#!/usr/bin/env python3
"""Tutorial 04: VSCode Theme Import.
===============================

This tutorial shows how to import and use VSCode themes.

What you'll learn:
- Importing VSCode theme files
- Converting VSCode themes to VFWidgets format
- Using imported themes in applications
- Best practices for theme conversion

Note: This is a demonstration of the concept. Full VSCode theme
import would require additional implementation.
"""

import json
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from vfwidgets_theme import ThemedApplication, ThemedWidget


class VSCodeThemeImporter:
    """Simulated VSCode theme importer."""

    @staticmethod
    def import_theme(theme_data):
        """Convert VSCode theme to VFWidgets format."""
        if isinstance(theme_data, str):
            # Assume it's JSON
            try:
                theme_data = json.loads(theme_data)
            except json.JSONDecodeError:
                return None

        # Extract relevant colors from VSCode theme
        colors = theme_data.get("colors", {})
        theme_data.get("tokenColors", [])

        # Map VSCode colors to VFWidgets structure
        vf_theme = {
            "name": theme_data.get("name", "imported"),
            "window": {
                "background": colors.get("editor.background", "#ffffff"),
                "foreground": colors.get("editor.foreground", "#000000"),
            },
            "editor": {
                "background": colors.get("editor.background", "#ffffff"),
                "foreground": colors.get("editor.foreground", "#000000"),
                "selection": colors.get("editor.selectionBackground", "#add6ff"),
                "line_highlight": colors.get("editor.lineHighlightBackground", "#f5f5f5"),
            },
            "sidebar": {
                "background": colors.get("sideBar.background", "#f3f3f3"),
                "foreground": colors.get("sideBar.foreground", "#333333"),
            },
            "statusbar": {
                "background": colors.get("statusBar.background", "#007acc"),
                "foreground": colors.get("statusBar.foreground", "#ffffff"),
            },
            "button": {
                "background": colors.get("button.background", "#0e639c"),
                "foreground": colors.get("button.foreground", "#ffffff"),
                "hover": {"background": colors.get("button.hoverBackground", "#1177bb")},
                "border": colors.get("button.background", "#0e639c"),
            },
            "accent": {"primary": colors.get("focusBorder", "#007fd4")},
        }

        return vf_theme

    @staticmethod
    def get_sample_themes():
        """Get sample VSCode themes for demonstration."""
        monokai = {
            "name": "Monokai",
            "colors": {
                "editor.background": "#272822",
                "editor.foreground": "#f8f8f2",
                "editor.selectionBackground": "#49483e",
                "editor.lineHighlightBackground": "#3e3d32",
                "sideBar.background": "#1e1f1c",
                "sideBar.foreground": "#a6a6a6",
                "statusBar.background": "#414339",
                "statusBar.foreground": "#f8f8f2",
                "button.background": "#66d9ef",
                "button.foreground": "#272822",
                "button.hoverBackground": "#a6e22e",
                "focusBorder": "#f92672",
            },
        }

        one_dark = {
            "name": "One Dark",
            "colors": {
                "editor.background": "#282c34",
                "editor.foreground": "#abb2bf",
                "editor.selectionBackground": "#3e4451",
                "editor.lineHighlightBackground": "#2c313c",
                "sideBar.background": "#21252b",
                "sideBar.foreground": "#9da5b4",
                "statusBar.background": "#21252b",
                "statusBar.foreground": "#abb2bf",
                "button.background": "#61afef",
                "button.foreground": "#ffffff",
                "button.hoverBackground": "#528bff",
                "focusBorder": "#61afef",
            },
        }

        github_light = {
            "name": "GitHub Light",
            "colors": {
                "editor.background": "#ffffff",
                "editor.foreground": "#24292e",
                "editor.selectionBackground": "#c8e1ff",
                "editor.lineHighlightBackground": "#f6f8fa",
                "sideBar.background": "#f6f8fa",
                "sideBar.foreground": "#586069",
                "statusBar.background": "#24292e",
                "statusBar.foreground": "#ffffff",
                "button.background": "#28a745",
                "button.foreground": "#ffffff",
                "button.hoverBackground": "#269f42",
                "focusBorder": "#0366d6",
            },
        }

        return [monokai, one_dark, github_light]


class CodeEditorWidget(ThemedWidget):
    """A simple code editor widget that demonstrates VSCode theme usage."""

    theme_config = {
        "editor_bg": "editor.background",
        "editor_fg": "editor.foreground",
        "selection_bg": "editor.selection",
        "line_highlight": "editor.line_highlight",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Set up the code editor UI."""
        layout = QVBoxLayout(self)

        # Editor
        self.editor = QTextEdit()
        self.editor.setFont(QFont("Courier New", 10))
        self.editor.setPlainText(
            """# Sample Python Code
def hello_world():
    \"\"\"A simple greeting function.\"\"\"
    message = "Hello, World!"
    print(message)
    return message

class ThemeDemo:
    def __init__(self, theme_name):
        self.theme = theme_name

    def apply_theme(self):
        print(f"Applying {self.theme} theme")
        # Theme application logic here

if __name__ == "__main__":
    demo = ThemeDemo("monokai")
    demo.apply_theme()
    hello_world()
"""
        )
        layout.addWidget(self.editor)

    def on_theme_changed(self):
        """Apply theme to code editor."""
        self.update_styling()

    def update_styling(self):
        """Update editor styling based on theme."""
        bg = self.theme.get("editor_bg", "#ffffff")
        fg = self.theme.get("editor_fg", "#000000")
        selection_bg = self.theme.get("selection_bg", "#add6ff")

        self.editor.setStyleSheet(
            f"""
        QTextEdit {{
            background-color: {bg};
            color: {fg};
            border: none;
            selection-background-color: {selection_bg};
        }}
        """
        )


class VSCodeImportDemo(ThemedWidget):
    """Main demo widget for VSCode theme import."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.imported_themes = {}
        self.setup_ui()

    def setup_ui(self):
        """Set up the demo UI."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("VSCode Theme Import Demo")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Controls
        controls_group = QGroupBox("Theme Import")
        controls_layout = QFormLayout(controls_group)

        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Select a theme...")
        self.theme_combo.currentTextChanged.connect(self.on_theme_selected)
        controls_layout.addRow("Available Themes:", self.theme_combo)

        # Import buttons
        import_layout = QHBoxLayout()

        load_sample_btn = QPushButton("Load Sample Themes")
        load_sample_btn.clicked.connect(self.load_sample_themes)
        import_layout.addWidget(load_sample_btn)

        import_file_btn = QPushButton("Import Theme File")
        import_file_btn.clicked.connect(self.import_theme_file)
        import_layout.addWidget(import_file_btn)

        controls_layout.addRow("Import:", import_layout)

        layout.addWidget(controls_group)

        # Preview area
        preview_group = QGroupBox("Theme Preview")
        preview_layout = QVBoxLayout(preview_group)

        # Code editor
        self.code_editor = CodeEditorWidget()
        preview_layout.addWidget(self.code_editor)

        layout.addWidget(preview_group)

        # Theme info
        self.info_label = QLabel("Load a theme to see preview")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)

    def load_sample_themes(self):
        """Load sample VSCode themes."""
        print("Loading sample VSCode themes...")

        # Get sample themes
        sample_themes = VSCodeThemeImporter.get_sample_themes()

        # Convert and register each theme
        app = ThemedApplication.instance()

        for vscode_theme in sample_themes:
            # Convert to VFWidgets format
            vf_theme = VSCodeThemeImporter.import_theme(vscode_theme)

            if vf_theme:
                theme_name = vf_theme["name"].lower().replace(" ", "_")

                # Register with application
                app.register_theme(theme_name, vf_theme)

                # Add to combo box
                self.theme_combo.addItem(vf_theme["name"])

                # Store for reference
                self.imported_themes[vf_theme["name"]] = vf_theme

                print(f"Imported theme: {vf_theme['name']}")

        self.info_label.setText("Sample themes loaded. Select one from the dropdown.")

    def import_theme_file(self):
        """Import a theme from file (simulated)."""
        # In a real implementation, this would open a file dialog
        # and load a .json theme file
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import VSCode Theme", "", "JSON Files (*.json);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path) as f:
                    theme_data = json.load(f)

                # Convert and register
                vf_theme = VSCodeThemeImporter.import_theme(theme_data)

                if vf_theme:
                    theme_name = vf_theme["name"].lower().replace(" ", "_")

                    # Register with application
                    app = ThemedApplication.instance()
                    app.register_theme(theme_name, vf_theme)

                    # Add to combo box
                    self.theme_combo.addItem(vf_theme["name"])

                    # Store for reference
                    self.imported_themes[vf_theme["name"]] = vf_theme

                    self.info_label.setText(f"Imported theme: {vf_theme['name']}")
                    print(f"Imported theme from file: {vf_theme['name']}")
                else:
                    self.info_label.setText("Failed to import theme")

            except Exception as e:
                self.info_label.setText(f"Error importing theme: {e}")
                print(f"Error importing theme: {e}")

    def on_theme_selected(self, theme_name):
        """Handle theme selection."""
        if theme_name in self.imported_themes:
            # Apply the selected theme
            app = ThemedApplication.instance()
            theme_id = theme_name.lower().replace(" ", "_")

            try:
                app.set_theme(theme_id)
                self.info_label.setText(f"Applied theme: {theme_name}")
                print(f"Applied theme: {theme_name}")
            except Exception as e:
                self.info_label.setText(f"Error applying theme: {e}")


def main():
    """Main function for VSCode import demo."""
    print("Tutorial 04: VSCode Theme Import")
    print("=" * 35)

    app = ThemedApplication(sys.argv)

    # Register a default light theme
    light_theme = {
        "name": "light",
        "window": {"background": "#ffffff", "foreground": "#000000"},
        "editor": {
            "background": "#ffffff",
            "foreground": "#000000",
            "selection": "#add6ff",
            "line_highlight": "#f5f5f5",
        },
        "button": {
            "background": "#e0e0e0",
            "foreground": "#000000",
            "hover": {"background": "#d0d0d0"},
            "border": "#cccccc",
        },
        "accent": {"primary": "#007bff"},
    }

    app.register_theme("light", light_theme)
    app.set_theme("light")

    # Create and show demo
    widget = VSCodeImportDemo()
    widget.setWindowTitle("Tutorial 04: VSCode Theme Import")
    widget.setMinimumSize(700, 600)
    widget.show()

    print("\nVSCode theme import demo ready!")
    print("1. Click 'Load Sample Themes' to import sample VSCode themes")
    print("2. Select a theme from the dropdown to preview it")
    print("3. Use 'Import Theme File' to load your own VSCode themes")

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
