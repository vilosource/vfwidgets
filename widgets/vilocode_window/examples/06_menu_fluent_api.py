"""Example 06: Menu Bar - Fluent API

Demonstrates the new fluent MenuBuilder API for creating menus.
This is the recommended approach - clean, readable, and automatically handles:
- Menu bar creation
- Theme integration
- Lazy integration (no initialization order traps)

Compare this with old approach:
- OLD: 67 lines with manual QMenuBar creation, theme workarounds
- NEW: ~30 lines with fluent API
"""

import sys

from PySide6.QtWidgets import QApplication, QTextEdit

from vfwidgets_vilocode_window import ViloCodeWindow


class MenuDemoWindow(ViloCodeWindow):
    """Demo window showing fluent menu API."""

    def __init__(self):
        super().__init__(
            enable_default_shortcuts=True,
            show_activity_bar=False,
            show_sidebar=False,
            show_auxiliary_bar=False,
        )

        self.setWindowTitle("Menu Fluent API Demo")
        self.resize(800, 600)

        # Setup content
        self._setup_content()

        # Setup menus using fluent API
        self._setup_menus()

    def _setup_content(self):
        """Setup main content area."""
        editor = QTextEdit()
        editor.setPlaceholderText(
            "Fluent Menu API Demo\n\n"
            "Notice how clean the menu setup code is!\n"
            "Try the menu items above - they demonstrate:\n\n"
            "• Simple actions with callbacks\n"
            "• Keyboard shortcuts\n"
            "• Separators\n"
            "• Checkable items (toggles)\n"
            "• Submenus\n"
            "• Action groups (radio buttons)\n\n"
            "All with automatic theme integration!"
        )
        self.set_main_content(editor)

    def _setup_menus(self):
        """Setup menus using fluent API - clean and readable!"""

        # File menu
        (
            self.add_menu("&File")
            .add_action("&New", self._on_new, "Ctrl+N", tooltip="Create new file")
            .add_action("&Open...", self._on_open, "Ctrl+O", tooltip="Open file")
            .add_separator()
            .add_action("&Save", self._on_save, "Ctrl+S", tooltip="Save file")
            .add_action("Save &As...", self._on_save_as, "Ctrl+Shift+S")
            .add_separator()
            .add_submenu("Recent Files")
            .add_action("file1.txt", lambda: self._open_recent("file1.txt"))
            .add_action("file2.txt", lambda: self._open_recent("file2.txt"))
            .add_action("file3.txt", lambda: self._open_recent("file3.txt"))
            .end_submenu()
            .add_separator()
            .add_action("E&xit", self.close, "Ctrl+Q", tooltip="Exit application")
        )

        # Edit menu
        (
            self.add_menu("&Edit")
            .add_action("&Undo", self._on_undo, "Ctrl+Z")
            .add_action("&Redo", self._on_redo, "Ctrl+Y")
            .add_separator()
            .add_action("Cu&t", self._on_cut, "Ctrl+X")
            .add_action("&Copy", self._on_copy, "Ctrl+C")
            .add_action("&Paste", self._on_paste, "Ctrl+V")
        )

        # View menu with toggles
        (
            self.add_menu("&View")
            .add_checkable(
                "Show &Sidebar",
                lambda checked: print(f"Sidebar: {checked}"),
                checked=False,
                shortcut="Ctrl+B",
            )
            .add_checkable(
                "Show &Minimap",
                lambda checked: print(f"Minimap: {checked}"),
                checked=True,
            )
            .add_separator()
            .add_submenu("Zoom")
            .add_action("Zoom &In", self._on_zoom_in, "Ctrl++")
            .add_action("Zoom &Out", self._on_zoom_out, "Ctrl+-")
            .add_action("&Reset Zoom", self._on_zoom_reset, "Ctrl+0")
            .end_submenu()
        )

        # Settings menu with action group (radio buttons)
        settings = self.add_menu("&Settings")
        settings.add_action_group(
            [
                ("&Small Font", lambda: self._set_font_size("small")),
                ("&Medium Font", lambda: self._set_font_size("medium")),
                ("&Large Font", lambda: self._set_font_size("large")),
            ],
            exclusive=True,
            default_index=1,  # Medium selected by default
        )

        settings.add_separator()

        # Theme submenu (if theme system available)
        try:
            from vfwidgets_theme.widgets.dialogs import ThemePickerDialog

            settings.add_action(
                "Theme &Preferences...",
                lambda: ThemePickerDialog(self).exec(),
                tooltip="Change application theme",
            )
        except ImportError:
            pass

    # Action callbacks
    def _on_new(self):
        print("New file")

    def _on_open(self):
        print("Open file")

    def _on_save(self):
        print("Save file")

    def _on_save_as(self):
        print("Save as...")

    def _open_recent(self, filename: str):
        print(f"Open recent: {filename}")

    def _on_undo(self):
        print("Undo")

    def _on_redo(self):
        print("Redo")

    def _on_cut(self):
        print("Cut")

    def _on_copy(self):
        print("Copy")

    def _on_paste(self):
        print("Paste")

    def _on_zoom_in(self):
        print("Zoom in")

    def _on_zoom_out(self):
        print("Zoom out")

    def _on_zoom_reset(self):
        print("Reset zoom")

    def _set_font_size(self, size: str):
        print(f"Font size: {size}")


def main():
    """Run the demo."""
    app = QApplication(sys.argv)

    # Enable theme system if available
    try:
        from vfwidgets_theme import ThemedApplication

        app = ThemedApplication.create_or_get_application()
        app.set_theme("dark")
    except ImportError:
        print("Theme system not available - using default styling")

    window = MenuDemoWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
