"""KeybindingDialog example.

This example demonstrates the KeybindingDialog widget - a complete UI
for managing keyboard shortcuts in an application.
"""

import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from vfwidgets_keybinding import ActionDefinition, KeybindingManager
from vfwidgets_keybinding.widgets import KeybindingDialog


class DemoApp(QMainWindow):
    """Demo application showing KeybindingDialog usage."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("KeybindingDialog Demo")
        self.resize(800, 600)

        # Create keybinding manager
        self._manager = KeybindingManager(
            storage_path="~/.config/keybinding_demo/shortcuts.json",
            auto_save=True,
        )

        # Register actions across multiple categories
        self._register_actions()

        # Load saved bindings (or use defaults)
        self._manager.load_bindings()

        # Setup UI
        self._setup_ui()

        # Apply shortcuts to this window
        self._manager.apply_shortcuts(self)

        print("\n" + "=" * 60)
        print("KeybindingDialog Demo Application")
        print("=" * 60)
        print("Click 'Configure Shortcuts...' to open the dialog")
        print("Try these features:")
        print("  - Edit shortcuts by clicking in the Shortcut column")
        print("  - Search for actions using the search bar")
        print("  - Reset individual shortcuts or reset all")
        print("  - Conflict detection (try setting duplicate shortcuts)")
        print("  - Apply to test without closing")
        print("  - Cancel to revert changes")
        print("=" * 60)

    def _register_actions(self):
        """Register all application actions."""
        # File category
        self._manager.register_actions(
            [
                ActionDefinition(
                    id="file.new",
                    description="New File",
                    default_shortcut="Ctrl+N",
                    category="File",
                    callback=lambda: self._log("New file"),
                ),
                ActionDefinition(
                    id="file.open",
                    description="Open File",
                    default_shortcut="Ctrl+O",
                    category="File",
                    callback=lambda: self._log("Open file"),
                ),
                ActionDefinition(
                    id="file.save",
                    description="Save File",
                    default_shortcut="Ctrl+S",
                    category="File",
                    callback=lambda: self._log("Save file"),
                ),
                ActionDefinition(
                    id="file.save_as",
                    description="Save As...",
                    default_shortcut="Ctrl+Shift+S",
                    category="File",
                    callback=lambda: self._log("Save as"),
                ),
                ActionDefinition(
                    id="file.close",
                    description="Close File",
                    default_shortcut="Ctrl+W",
                    category="File",
                    callback=lambda: self._log("Close file"),
                ),
                ActionDefinition(
                    id="file.quit",
                    description="Quit Application",
                    default_shortcut="Ctrl+Q",
                    category="File",
                    callback=self.close,
                ),
            ]
        )

        # Edit category
        self._manager.register_actions(
            [
                ActionDefinition(
                    id="edit.undo",
                    description="Undo",
                    default_shortcut="Ctrl+Z",
                    category="Edit",
                    callback=lambda: self._log("Undo"),
                ),
                ActionDefinition(
                    id="edit.redo",
                    description="Redo",
                    default_shortcut="Ctrl+Shift+Z",
                    category="Edit",
                    callback=lambda: self._log("Redo"),
                ),
                ActionDefinition(
                    id="edit.cut",
                    description="Cut",
                    default_shortcut="Ctrl+X",
                    category="Edit",
                    callback=lambda: self._log("Cut"),
                ),
                ActionDefinition(
                    id="edit.copy",
                    description="Copy",
                    default_shortcut="Ctrl+C",
                    category="Edit",
                    callback=lambda: self._log("Copy"),
                ),
                ActionDefinition(
                    id="edit.paste",
                    description="Paste",
                    default_shortcut="Ctrl+V",
                    category="Edit",
                    callback=lambda: self._log("Paste"),
                ),
                ActionDefinition(
                    id="edit.select_all",
                    description="Select All",
                    default_shortcut="Ctrl+A",
                    category="Edit",
                    callback=lambda: self._log("Select all"),
                ),
            ]
        )

        # View category
        self._manager.register_actions(
            [
                ActionDefinition(
                    id="view.zoom_in",
                    description="Zoom In",
                    default_shortcut="Ctrl++",
                    category="View",
                    callback=lambda: self._log("Zoom in"),
                ),
                ActionDefinition(
                    id="view.zoom_out",
                    description="Zoom Out",
                    default_shortcut="Ctrl+-",
                    category="View",
                    callback=lambda: self._log("Zoom out"),
                ),
                ActionDefinition(
                    id="view.reset_zoom",
                    description="Reset Zoom",
                    default_shortcut="Ctrl+0",
                    category="View",
                    callback=lambda: self._log("Reset zoom"),
                ),
                ActionDefinition(
                    id="view.fullscreen",
                    description="Toggle Fullscreen",
                    default_shortcut="F11",
                    category="View",
                    callback=lambda: self._log("Toggle fullscreen"),
                ),
            ]
        )

        # Help category
        self._manager.register_actions(
            [
                ActionDefinition(
                    id="help.documentation",
                    description="Show Documentation",
                    default_shortcut="F1",
                    category="Help",
                    callback=lambda: self._log("Show documentation"),
                ),
                ActionDefinition(
                    id="help.shortcuts",
                    description="Configure Shortcuts...",
                    default_shortcut="Ctrl+K",
                    category="Help",
                    callback=self._show_shortcuts_dialog,
                ),
            ]
        )

    def _setup_ui(self):
        """Setup the main UI."""
        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Menu bar
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")
        file_menu.addAction("New (Ctrl+N)", lambda: self._log("New file"))
        file_menu.addAction("Open (Ctrl+O)", lambda: self._log("Open file"))
        file_menu.addAction("Save (Ctrl+S)", lambda: self._log("Save file"))
        file_menu.addSeparator()
        file_menu.addAction("Quit (Ctrl+Q)", self.close)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        edit_menu.addAction("Undo (Ctrl+Z)", lambda: self._log("Undo"))
        edit_menu.addAction("Redo (Ctrl+Shift+Z)", lambda: self._log("Redo"))
        edit_menu.addSeparator()
        edit_menu.addAction("Cut (Ctrl+X)", lambda: self._log("Cut"))
        edit_menu.addAction("Copy (Ctrl+C)", lambda: self._log("Copy"))
        edit_menu.addAction("Paste (Ctrl+V)", lambda: self._log("Paste"))

        # Help menu
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("Configure Shortcuts... (Ctrl+K)", self._show_shortcuts_dialog)

        # Button to open dialog
        btn = QPushButton("Configure Shortcuts...")
        btn.clicked.connect(self._show_shortcuts_dialog)
        layout.addWidget(btn)

        # Text area for log
        self._text = QTextEdit()
        self._text.setPlaceholderText(
            "Press keyboard shortcuts to test them.\n"
            "Example: Ctrl+S, Ctrl+N, F1, etc.\n\n"
            "Click 'Configure Shortcuts...' to customize them."
        )
        layout.addWidget(self._text)

    def _show_shortcuts_dialog(self):
        """Show the keybinding configuration dialog."""
        dialog = KeybindingDialog(self._manager, parent=self)

        # Connect signal to update menu labels (optional)
        dialog.shortcuts_changed.connect(self._on_shortcuts_changed)

        # Show dialog
        result = dialog.exec()

        if result == KeybindingDialog.DialogCode.Accepted:
            self._log("✓ Shortcuts saved")
        else:
            self._log("✗ Shortcuts dialog cancelled")

    def _on_shortcuts_changed(self, manager):
        """Handle shortcuts being changed."""
        self._log("Shortcuts updated (Apply clicked)")

    def _log(self, message: str):
        """Log a message to the text area."""
        self._text.append(f"→ {message}")


def main():
    app = QApplication(sys.argv)
    window = DemoApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
