#!/usr/bin/env python3
"""Customization Example - Menus, Shortcuts, Themes, Modes

This example demonstrates advanced customization features:
- Menu bar integration
- Keyboard shortcuts (default + custom)
- Theme system integration
- Frameless vs Embedded modes
- Status bar customization

What you'll learn:
- Setting a menu bar with set_menubar()
- Working with default VS Code shortcuts
- Registering custom shortcuts
- Theme integration (if vfwidgets-theme available)
- Choosing between frameless and embedded modes
- Advanced status bar usage

Run this example:
    python examples/04_customization.py
"""

import sys

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QMenuBar, QTextEdit

from vfwidgets_vilocode_window import ViloCodeWindow

# Check if theme system is available
try:
    from vfwidgets_theme import ThemedApplication

    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False


def create_menubar(window: ViloCodeWindow) -> QMenuBar:
    """Create a menu bar with File, Edit, and View menus.

    Args:
        window: ViloCodeWindow instance

    Returns:
        Configured QMenuBar
    """
    menubar = QMenuBar()

    # File menu
    file_menu = menubar.addMenu("File")

    new_action = QAction("New", window)
    new_action.setShortcut("Ctrl+N")
    new_action.triggered.connect(lambda: window.set_status_message("📄 New file", 2000))
    file_menu.addAction(new_action)

    open_action = QAction("Open...", window)
    open_action.setShortcut("Ctrl+O")
    open_action.triggered.connect(lambda: window.set_status_message("📂 Open file", 2000))
    file_menu.addAction(open_action)

    save_action = QAction("Save", window)
    save_action.setShortcut("Ctrl+S")
    save_action.triggered.connect(lambda: window.set_status_message("💾 Save file", 2000))
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
    edit_menu.addAction(undo_action)

    redo_action = QAction("Redo", window)
    redo_action.setShortcut("Ctrl+Shift+Z")
    edit_menu.addAction(redo_action)

    edit_menu.addSeparator()

    find_action = QAction("Find...", window)
    find_action.setShortcut("Ctrl+F")
    find_action.triggered.connect(lambda: window.set_status_message("🔍 Find", 2000))
    edit_menu.addAction(find_action)

    # View menu
    view_menu = menubar.addMenu("View")

    toggle_sidebar_action = QAction("Toggle Sidebar", window)
    toggle_sidebar_action.setShortcut("Ctrl+B")
    toggle_sidebar_action.triggered.connect(window.toggle_sidebar)
    view_menu.addAction(toggle_sidebar_action)

    toggle_status_action = QAction("Toggle Status Bar", window)
    toggle_status_action.triggered.connect(
        lambda: window.set_status_bar_visible(not window.get_status_bar().isVisible())
    )
    view_menu.addAction(toggle_status_action)

    return menubar


def main() -> None:
    """Create a customized ViloCodeWindow."""
    # Use ThemedApplication if available for automatic theme support
    if THEME_AVAILABLE:
        app = ThemedApplication(sys.argv)
        print("✓ Theme system available - automatic theming enabled")
    else:
        app = QApplication(sys.argv)
        print("✗ Theme system not available - using fallback colors")

    # Create window (frameless by default, embedded if parent provided)
    window = ViloCodeWindow()
    window.setWindowTitle("ViloCodeWindow - Customization Demo")
    window.resize(1200, 700)

    # ==================== Menu Bar ====================
    menubar = create_menubar(window)
    window.set_menu_bar(menubar)

    # ==================== Main Content ====================
    editor = QTextEdit()

    # Get all default shortcuts for display
    shortcuts_info = []
    all_shortcuts = window.get_all_shortcuts()
    for _name, definition in sorted(all_shortcuts.items()):
        shortcuts_info.append(f"  {definition.key_sequence:<20} {definition.description}")

    shortcuts_text = "\n".join(shortcuts_info)

    editor.setPlainText(
        f"""# Customization Demo

This example demonstrates advanced customization features.

## Menu Bar Integration
The menu bar is integrated into the title bar (frameless mode).
Try: File, Edit, and View menus above.

## Keyboard Shortcuts

### Default VS Code Shortcuts (auto-loaded):
{shortcuts_text}

### Custom Shortcuts (added by this example):
  Ctrl+1                Open Editor 1
  Ctrl+2                Open Editor 2
  Alt+T                 Toggle Theme (if available)

Try pressing these shortcuts!

## Theme System
Theme system: {"✓ Available" if THEME_AVAILABLE else "✗ Not available (using fallback colors)"}

When vfwidgets-theme is available:
- Automatic theme application to all components
- ActivityBar, SideBar, AuxiliaryBar all themed
- VS Code Dark+ colors by default
- Switch themes with Alt+T

## Window Modes

### Frameless Mode (current):
- No parent widget = automatic frameless window
- Custom title bar with window controls
- Draggable title bar
- Menu bar integrated into title bar

### Embedded Mode:
- Has parent widget = embedded mode
- No title bar or window controls
- Can be embedded in any QWidget
- See 01_minimal.py for example

## Status Bar
The status bar is fully customizable:
- set_status_message(text, timeout)
- get_status_bar() returns QStatusBar
- set_status_bar_visible(visible)
- Add custom widgets to status bar

## Public API Summary
All features use public API only:
✓ set_menubar(menubar)
✓ register_custom_shortcut(name, key, callback, desc)
✓ get_all_shortcuts()
✓ set_shortcut(action, key)
✓ get_status_bar()
✓ set_status_message()
✓ toggle_sidebar() / toggle_auxiliary_bar()
"""
    )
    window.set_main_content(editor)

    # ==================== Custom Shortcuts ====================
    def open_editor_1() -> None:
        window.set_status_message("📝 Opening Editor 1", 2000)

    def open_editor_2() -> None:
        window.set_status_message("📝 Opening Editor 2", 2000)

    def toggle_theme() -> None:
        if THEME_AVAILABLE:
            from vfwidgets_theme import get_theme_manager

            manager = get_theme_manager()
            themes = manager.get_available_themes()
            current = manager.get_current_theme_name()

            # Cycle through themes
            theme_names = list(themes.keys())
            current_index = theme_names.index(current) if current in theme_names else 0
            next_index = (current_index + 1) % len(theme_names)
            next_theme = theme_names[next_index]

            manager.set_theme(next_theme)
            window.set_status_message(f"🎨 Theme: {next_theme}", 3000)
        else:
            window.set_status_message("Theme system not available", 2000)

    # Register custom shortcuts
    window.register_custom_shortcut("open_editor_1", "Ctrl+1", open_editor_1, "Open Editor 1")
    window.register_custom_shortcut("open_editor_2", "Ctrl+2", open_editor_2, "Open Editor 2")
    window.register_custom_shortcut("toggle_theme", "Alt+T", toggle_theme, "Toggle Theme")

    # ==================== Status Bar Customization ====================
    window.get_status_bar()
    # You can add permanent widgets to the status bar:
    # status_bar.addPermanentWidget(my_widget)

    # ==================== Initial Status ====================
    theme_info = (
        "Theme system available - press Alt+T to cycle themes"
        if THEME_AVAILABLE
        else "Theme system not available"
    )
    window.set_status_message(
        f"Menu bar integrated | Default + custom shortcuts active | {theme_info}"
    )

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
