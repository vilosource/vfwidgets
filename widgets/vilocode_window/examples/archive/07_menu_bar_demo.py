#!/usr/bin/env python3
"""Example demonstrating menu bar integration in ViloCodeWindow.

This example shows:
- Creating a QMenuBar
- Adding menus and actions
- Setting the menu bar in frameless mode
- Menu bar appears in the title bar
"""

import sys

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QMenuBar

from vfwidgets_vilocode_window import ViloCodeWindow


def main():
    """Demonstrate menu bar integration."""
    app = QApplication(sys.argv)

    # Create window
    window = ViloCodeWindow()
    window.setWindowTitle("ViloCodeWindow - Menu Bar Demo")
    window.resize(1200, 800)

    # Create menu bar
    menubar = QMenuBar()

    # File menu
    file_menu = menubar.addMenu("File")

    new_action = QAction("New", window)
    new_action.setShortcut("Ctrl+N")
    new_action.triggered.connect(lambda: window.set_status_message("New file", 2000))
    file_menu.addAction(new_action)

    open_action = QAction("Open...", window)
    open_action.setShortcut("Ctrl+O")
    open_action.triggered.connect(lambda: window.set_status_message("Open file", 2000))
    file_menu.addAction(open_action)

    save_action = QAction("Save", window)
    save_action.setShortcut("Ctrl+S")
    save_action.triggered.connect(lambda: window.set_status_message("Save file", 2000))
    file_menu.addAction(save_action)

    file_menu.addSeparator()

    exit_action = QAction("Exit", window)
    exit_action.setShortcut("Ctrl+Q")
    exit_action.triggered.connect(window.close)
    file_menu.addAction(exit_action)

    # Edit menu
    edit_menu = menubar.addMenu("Edit")

    undo_action = QAction("Undo", window)
    undo_action.setShortcut("Ctrl+Z")
    undo_action.triggered.connect(lambda: window.set_status_message("Undo", 2000))
    edit_menu.addAction(undo_action)

    redo_action = QAction("Redo", window)
    redo_action.setShortcut("Ctrl+Y")
    redo_action.triggered.connect(lambda: window.set_status_message("Redo", 2000))
    edit_menu.addAction(redo_action)

    edit_menu.addSeparator()

    cut_action = QAction("Cut", window)
    cut_action.setShortcut("Ctrl+X")
    cut_action.triggered.connect(lambda: window.set_status_message("Cut", 2000))
    edit_menu.addAction(cut_action)

    copy_action = QAction("Copy", window)
    copy_action.setShortcut("Ctrl+C")
    copy_action.triggered.connect(lambda: window.set_status_message("Copy", 2000))
    edit_menu.addAction(copy_action)

    paste_action = QAction("Paste", window)
    paste_action.setShortcut("Ctrl+V")
    paste_action.triggered.connect(lambda: window.set_status_message("Paste", 2000))
    edit_menu.addAction(paste_action)

    # View menu
    view_menu = menubar.addMenu("View")

    toggle_sidebar_action = QAction("Toggle Sidebar", window)
    toggle_sidebar_action.setShortcut("Ctrl+B")
    toggle_sidebar_action.triggered.connect(
        lambda: window.set_status_message("Toggle Sidebar", 2000)
    )
    view_menu.addAction(toggle_sidebar_action)

    toggle_statusbar_action = QAction("Toggle Status Bar", window)
    toggle_statusbar_action.setShortcut("Ctrl+Shift+S")
    toggle_statusbar_action.triggered.connect(
        lambda: window.set_status_bar_visible(not window.is_status_bar_visible())
    )
    view_menu.addAction(toggle_statusbar_action)

    view_menu.addSeparator()

    fullscreen_action = QAction("Toggle Fullscreen", window)
    fullscreen_action.setShortcut("F11")
    fullscreen_action.triggered.connect(
        lambda: (window.showNormal() if window.isMaximized() else window.showMaximized())
    )
    view_menu.addAction(fullscreen_action)

    # Help menu
    help_menu = menubar.addMenu("Help")

    about_action = QAction("About", window)
    about_action.triggered.connect(
        lambda: window.set_status_message("ViloCodeWindow - VS Code-style frameless window", 3000)
    )
    help_menu.addAction(about_action)

    # Set the menu bar
    window.set_menu_bar(menubar)

    # Set initial status message
    window.set_status_message(
        "Menu bar integrated! Try File > New or Edit > Copy. Watch the status bar for feedback."
    )

    print("=" * 70)
    print("ViloCodeWindow - Menu Bar Demo")
    print("=" * 70)
    print()
    print("Features:")
    print("  • Menu bar appears in the title bar (frameless mode)")
    print("  • File menu: New, Open, Save, Exit")
    print("  • Edit menu: Undo, Redo, Cut, Copy, Paste")
    print("  • View menu: Toggle Sidebar, Toggle Status Bar, Fullscreen")
    print("  • Help menu: About")
    print()
    print("Keyboard Shortcuts:")
    print("  • Ctrl+N           - New file")
    print("  • Ctrl+O           - Open file")
    print("  • Ctrl+S           - Save file")
    print("  • Ctrl+Z / Ctrl+Y  - Undo / Redo")
    print("  • Ctrl+X / C / V   - Cut / Copy / Paste")
    print("  • Ctrl+B           - Toggle Sidebar")
    print("  • Ctrl+Shift+S     - Toggle Status Bar")
    print("  • F11              - Toggle Fullscreen")
    print("  • Ctrl+Q           - Exit")
    print()
    print("Click on menu items or use keyboard shortcuts!")
    print("=" * 70)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
