"""Full KeybindingManager application example.

Demonstrates:
- Action registration with categories
- Persistent storage
- Custom callbacks
- Querying keybindings
- Resetting to defaults
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QTextEdit
from vfwidgets_keybinding import ActionDefinition, KeybindingManager


class EditorWindow(QMainWindow):
    """Simple text editor with keyboard shortcuts."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("KeybindingManager - Full Example")
        self.resize(1000, 700)

        # Create text editor
        self.editor = QTextEdit()
        self.editor.setPlaceholderText(
            "Try the keyboard shortcuts:\n"
            "- Ctrl+N: New document\n"
            "- Ctrl+S: Save document\n"
            "- Ctrl+O: Open document\n"
            "- Ctrl+Q: Quit\n\n"
            "- Ctrl+C: Copy\n"
            "- Ctrl+X: Cut\n"
            "- Ctrl+V: Paste\n\n"
            "- Ctrl+F: Find\n"
            "- Ctrl+H: Replace\n\n"
            "- F1: Show shortcuts\n"
            "- F12: Reset shortcuts to defaults"
        )
        self.setCentralWidget(self.editor)

        # Setup keybinding manager with persistent storage
        storage_path = Path.home() / ".config" / "keybinding_example" / "shortcuts.json"
        self.manager = KeybindingManager(storage_path=str(storage_path), auto_save=True)

        # Register all actions
        self._register_actions()

        # Load saved keybindings (or use defaults)
        self.manager.load_bindings()

        # Apply shortcuts to window and create menu bar
        # (menu bar will reference the QActions created by apply_shortcuts)
        self.applied_actions = self.manager.apply_shortcuts(self)
        self._create_menu_bar()

    def _register_actions(self):
        """Register all application actions."""
        # File category
        self.manager.register_actions(
            [
                ActionDefinition(
                    id="file.new",
                    description="New Document",
                    default_shortcut="Ctrl+N",
                    category="File",
                    callback=self._new_document,
                ),
                ActionDefinition(
                    id="file.open",
                    description="Open Document",
                    default_shortcut="Ctrl+O",
                    category="File",
                    callback=self._open_document,
                ),
                ActionDefinition(
                    id="file.save",
                    description="Save Document",
                    default_shortcut="Ctrl+S",
                    category="File",
                    callback=self._save_document,
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
        self.manager.register_actions(
            [
                ActionDefinition(
                    id="edit.copy",
                    description="Copy",
                    default_shortcut="Ctrl+C",
                    category="Edit",
                    callback=self.editor.copy,
                ),
                ActionDefinition(
                    id="edit.cut",
                    description="Cut",
                    default_shortcut="Ctrl+X",
                    category="Edit",
                    callback=self.editor.cut,
                ),
                ActionDefinition(
                    id="edit.paste",
                    description="Paste",
                    default_shortcut="Ctrl+V",
                    category="Edit",
                    callback=self.editor.paste,
                ),
            ]
        )

        # Search category
        self.manager.register_actions(
            [
                ActionDefinition(
                    id="search.find",
                    description="Find",
                    default_shortcut="Ctrl+F",
                    category="Search",
                    callback=self._find,
                ),
                ActionDefinition(
                    id="search.replace",
                    description="Replace",
                    default_shortcut="Ctrl+H",
                    category="Search",
                    callback=self._replace,
                ),
            ]
        )

        # Help category
        self.manager.register_actions(
            [
                ActionDefinition(
                    id="help.shortcuts",
                    description="Show Keyboard Shortcuts",
                    default_shortcut="F1",
                    category="Help",
                    callback=self._show_shortcuts,
                ),
                ActionDefinition(
                    id="help.reset",
                    description="Reset Shortcuts to Defaults",
                    default_shortcut="F12",
                    category="Help",
                    callback=self._reset_shortcuts,
                ),
            ]
        )

    def _create_menu_bar(self):
        """Create menu bar showing all actions organized by category.

        Note: We don't set shortcuts here because apply_shortcuts() already
        created QActions with shortcuts. We just reference those in the menu.
        """
        menubar = self.menuBar()

        # Get all categories
        for category in self.manager.get_categories():
            menu = menubar.addMenu(category)

            # Get actions in this category
            for action_def in self.manager.get_actions_by_category(category):
                # Get the QAction that was already created with shortcut
                qaction = self.applied_actions.get(action_def.id)
                if qaction:
                    menu.addAction(qaction)

    def _new_document(self):
        """Create new document."""
        self.editor.clear()
        self.statusBar().showMessage("New document created", 2000)

    def _open_document(self):
        """Open document."""
        self.statusBar().showMessage("Open document dialog would appear here", 2000)

    def _save_document(self):
        """Save document."""
        self.statusBar().showMessage("Document saved", 2000)

    def _find(self):
        """Find text."""
        self.statusBar().showMessage("Find dialog would appear here", 2000)

    def _replace(self):
        """Replace text."""
        self.statusBar().showMessage("Replace dialog would appear here", 2000)

    def _show_shortcuts(self):
        """Show all keyboard shortcuts."""
        message = "Keyboard Shortcuts:\n\n"

        for category in self.manager.get_categories():
            message += f"=== {category} ===\n"
            for action_def in self.manager.get_actions_by_category(category):
                shortcut = self.manager.get_binding(action_def.id)
                shortcut_str = shortcut if shortcut else "(not bound)"
                message += f"  {action_def.description}: {shortcut_str}\n"
            message += "\n"

        QMessageBox.information(self, "Keyboard Shortcuts", message)

    def _reset_shortcuts(self):
        """Reset all shortcuts to defaults."""
        reply = QMessageBox.question(
            self,
            "Reset Shortcuts",
            "Reset all keyboard shortcuts to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.manager.reset_to_defaults()
            self.statusBar().showMessage("Shortcuts reset to defaults", 3000)


def main():
    app = QApplication(sys.argv)
    window = EditorWindow()
    window.show()

    print("\n" + "=" * 60)
    print("KeybindingManager - Full Application Example")
    print("=" * 60)
    print("\nThis example demonstrates:")
    print("  - Multiple action categories (File, Edit, Search, Help)")
    print("  - Persistent storage (shortcuts saved to ~/.config/)")
    print("  - Auto-save (changes persist across restarts)")
    print("  - Menu bar integration")
    print("  - Querying bindings")
    print("  - Resetting to defaults")
    print("\nPress F1 to see all keyboard shortcuts")
    print("Press F12 to reset shortcuts to defaults")
    print("=" * 60 + "\n")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
