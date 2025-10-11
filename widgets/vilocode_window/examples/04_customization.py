#!/usr/bin/env python3
"""Customization Example - Menus, Shortcuts, Themes, Modes

This example demonstrates advanced customization features:
- Menu bar with fluent API (NEW!)
- Keyboard shortcuts (default + custom)
- Theme system integration
- Frameless vs Embedded modes
- Status bar customization

What you'll learn:
- Creating menus with the fluent API (add_menu())
- Working with default VS Code shortcuts
- Registering custom shortcuts
- Theme integration (if vfwidgets-theme available)
- Choosing between frameless and embedded modes
- Advanced status bar usage

Run this example:
    python examples/04_customization.py
"""

import sys

from PySide6.QtWidgets import QApplication, QTextEdit

from vfwidgets_vilocode_window import ViloCodeWindow

# Check if theme system is available
try:
    from vfwidgets_theme import ThemedApplication

    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False


def setup_menus(window: ViloCodeWindow) -> None:
    """Setup menus using the new fluent API.

    Args:
        window: ViloCodeWindow instance
    """
    # File menu - fluent API makes this clean and readable
    (
        window.add_menu("&File")
        .add_action(
            "New",
            lambda: window.set_status_message("📄 New file", 2000),
            "Ctrl+N",
        )
        .add_action(
            "Open...",
            lambda: window.set_status_message("📂 Open file", 2000),
            "Ctrl+O",
        )
        .add_action(
            "Save",
            lambda: window.set_status_message("💾 Save file", 2000),
            "Ctrl+S",
        )
        .add_separator()
        .add_action("Exit", window.close, "Ctrl+Q")
    )

    # Edit menu
    (
        window.add_menu("&Edit")
        .add_action("Undo", shortcut="Ctrl+Z")
        .add_action("Redo", shortcut="Ctrl+Shift+Z")
        .add_separator()
        .add_action(
            "Find...",
            lambda: window.set_status_message("🔍 Find", 2000),
            "Ctrl+F",
        )
    )

    # View menu
    (
        window.add_menu("&View")
        .add_action("Toggle Sidebar", window.toggle_sidebar, "Ctrl+B")
        .add_action(
            "Toggle Status Bar",
            lambda: window.set_status_bar_visible(not window.get_status_bar().isVisible()),
        )
    )


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

    # ==================== Menu Bar (Fluent API) ====================
    setup_menus(window)

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
