"""Manual keybinding file editing example.

This example demonstrates:
- Where the keybindings file is saved
- How to edit it manually
- How changes are loaded on restart
- File format and validation
"""

import json
import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from vfwidgets_keybinding import ActionDefinition, KeybindingManager


class FileEditingDemo(QMainWindow):
    """Demo showing manual file editing workflow."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manual File Editing Demo")
        self.resize(900, 700)

        # Setup storage path
        self.storage_path = Path.home() / ".config" / "keybinding_demo" / "shortcuts.json"

        # Setup keybinding manager
        self.manager = KeybindingManager(str(self.storage_path), auto_save=True)
        self._register_actions()
        self.manager.load_bindings()
        self.manager.apply_shortcuts(self)

        # Setup UI
        self._setup_ui()

    def _register_actions(self):
        """Register demo actions."""
        self.manager.register_actions(
            [
                ActionDefinition(
                    id="demo.action1",
                    description="Demo Action 1",
                    default_shortcut="Ctrl+1",
                    category="Demo",
                    callback=lambda: self.show_message("Action 1 triggered!"),
                ),
                ActionDefinition(
                    id="demo.action2",
                    description="Demo Action 2",
                    default_shortcut="Ctrl+2",
                    category="Demo",
                    callback=lambda: self.show_message("Action 2 triggered!"),
                ),
                ActionDefinition(
                    id="demo.action3",
                    description="Demo Action 3",
                    default_shortcut="Ctrl+3",
                    category="Demo",
                    callback=lambda: self.show_message("Action 3 triggered!"),
                ),
                ActionDefinition(
                    id="app.quit",
                    description="Quit",
                    default_shortcut="Ctrl+Q",
                    category="Application",
                    callback=self.close,
                ),
            ]
        )

    def _setup_ui(self):
        """Setup the user interface."""
        central_widget = QWidget()
        layout = QVBoxLayout()

        # Title
        title = QLabel("Manual Keybinding File Editing Demo")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Information display
        info = QTextEdit()
        info.setReadOnly(True)
        info.setPlainText(self._get_info_text())
        layout.addWidget(info)

        # Buttons
        btn_show_file = QPushButton("Show Keybindings File")
        btn_show_file.clicked.connect(self._show_file)
        layout.addWidget(btn_show_file)

        btn_show_bindings = QPushButton("Show Current Bindings")
        btn_show_bindings.clicked.connect(self._show_bindings)
        layout.addWidget(btn_show_bindings)

        btn_reload = QPushButton("Reload from File")
        btn_reload.clicked.connect(self._reload_bindings)
        layout.addWidget(btn_reload)

        btn_reset = QPushButton("Reset to Defaults")
        btn_reset.clicked.connect(self._reset_bindings)
        layout.addWidget(btn_reset)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def _get_info_text(self) -> str:
        """Get informational text."""
        return f"""
HOW TO MANUALLY EDIT KEYBINDINGS
================================

1. FIND THE FILE
   Location: {self.storage_path}
   {"   ✅ File exists" if self.storage_path.exists() else "   ⚠️  File will be created when you change a binding"}

2. CLOSE THIS APPLICATION
   Important: Always close the app before editing!

3. OPEN THE FILE IN A TEXT EDITOR
   - VS Code, Notepad, TextEdit, nano, vim, etc.

4. EDIT THE JSON
   Example format:
   {{
     "demo.action1": "Ctrl+Shift+1",
     "demo.action2": "Alt+2",
     "demo.action3": null
   }}

5. SAVE THE FILE

6. RESTART THIS APPLICATION
   Your changes will be loaded automatically!

CURRENT SHORTCUTS
=================
Try these shortcuts to test:
  - Ctrl+1: Trigger Action 1
  - Ctrl+2: Trigger Action 2
  - Ctrl+3: Trigger Action 3
  - Ctrl+Q: Quit

EXAMPLE EDITS
=============
Change Ctrl+1 to Ctrl+Shift+1:
  "demo.action1": "Ctrl+Shift+1"

Unbind Action 3:
  "demo.action3": null

Use F-keys:
  "demo.action1": "F1",
  "demo.action2": "F2"

Platform-specific (macOS use Meta for Cmd):
  "demo.action1": "Meta+1"

TIPS
====
  - Use the buttons below to inspect the file
  - Click "Reload from File" to test changes without restarting
  - Click "Reset to Defaults" to undo all changes
  - Invalid JSON will be ignored (app uses defaults)
"""

    def _show_file(self):
        """Show the keybindings file content."""
        if not self.storage_path.exists():
            QMessageBox.information(
                self,
                "File Not Found",
                f"Keybindings file doesn't exist yet.\n\n"
                f"It will be created at:\n{self.storage_path}\n\n"
                f"Try changing a binding first by editing this demo app's code!",
            )
            return

        try:
            content = self.storage_path.read_text()
            # Pretty print JSON
            data = json.loads(content)
            pretty = json.dumps(data, indent=2, sort_keys=True)

            msg = f"File Location:\n{self.storage_path}\n\n"
            msg += f"Contents:\n{pretty}\n\n"
            msg += "You can edit this file with any text editor while the app is closed."

            QMessageBox.information(self, "Keybindings File", msg)

        except Exception as e:
            QMessageBox.warning(
                self, "Error Reading File", f"Failed to read keybindings file:\n{e}"
            )

    def _show_bindings(self):
        """Show current keybindings."""
        bindings = self.manager.get_all_bindings()

        msg = "Current Keyboard Shortcuts:\n\n"
        for action_id, shortcut in sorted(bindings.items()):
            shortcut_str = shortcut if shortcut else "(not bound)"
            msg += f"  {action_id}: {shortcut_str}\n"

        msg += "\n💡 Tip: Edit the file manually to customize these!"

        QMessageBox.information(self, "Current Bindings", msg)

    def _reload_bindings(self):
        """Reload bindings from file without restarting."""
        reply = QMessageBox.question(
            self,
            "Reload Bindings",
            "This will reload keybindings from the file.\n\n"
            "Have you edited the file?\n\n"
            "Note: You should close the app before editing!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.manager.load_bindings()

                # Re-apply to update QActions
                self.manager.apply_shortcuts(self)

                QMessageBox.information(
                    self,
                    "Bindings Reloaded",
                    "Keybindings have been reloaded from file.\n\n"
                    "Try the shortcuts to test your changes!",
                )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Failed to reload bindings:\n{e}\n\n" f"Check if the JSON file is valid.",
                )

    def _reset_bindings(self):
        """Reset all bindings to defaults."""
        reply = QMessageBox.question(
            self,
            "Reset to Defaults",
            "This will reset all keyboard shortcuts to their default values.\n\n" "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.manager.reset_to_defaults()

            QMessageBox.information(
                self,
                "Reset Complete",
                "All shortcuts have been reset to defaults.\n\n"
                "Default shortcuts:\n"
                "  - Ctrl+1: Action 1\n"
                "  - Ctrl+2: Action 2\n"
                "  - Ctrl+3: Action 3\n"
                "  - Ctrl+Q: Quit",
            )

    def show_message(self, text: str):
        """Show a temporary message."""
        self.statusBar().showMessage(text, 3000)


def main():
    app = QApplication(sys.argv)
    window = FileEditingDemo()
    window.show()

    print("\n" + "=" * 70)
    print("Manual Keybinding File Editing Demo")
    print("=" * 70)
    print("\nThis demo shows how users can manually edit the keybindings file.")
    print("\nInstructions:")
    print("  1. Run the app and try the shortcuts (Ctrl+1, Ctrl+2, Ctrl+3)")
    print("  2. Click 'Show Keybindings File' to see the file location")
    print("  3. Close the app")
    print("  4. Edit the JSON file with a text editor")
    print("  5. Restart the app to see your changes")
    print("\nAlternatively:")
    print("  - Click 'Show Current Bindings' to see active shortcuts")
    print("  - Click 'Reload from File' to test changes without restarting")
    print("  - Click 'Reset to Defaults' to undo all customizations")
    print("=" * 70 + "\n")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
