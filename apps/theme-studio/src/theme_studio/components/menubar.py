"""Menu bar builder for VFTheme Studio."""

from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMenuBar


def create_menu_bar(parent) -> QMenuBar:
    """Create and configure the application menu bar.

    Args:
        parent: Parent window

    Returns:
        Configured QMenuBar
    """
    menubar = parent.menuBar()

    # File menu
    file_menu = menubar.addMenu("&File")

    file_menu.addAction(_create_action(
        parent, "New Theme", QKeySequence.New,
        lambda: parent.new_theme()
    ))
    file_menu.addAction(_create_action(
        parent, "New from Template...", QKeySequence("Ctrl+Shift+N"),
        lambda: print("New from template (stub)")
    ))
    file_menu.addSeparator()

    file_menu.addAction(_create_action(
        parent, "Open Theme...", QKeySequence.Open,
        lambda: parent.open_theme()
    ))
    file_menu.addSeparator()

    file_menu.addAction(_create_action(
        parent, "Save", QKeySequence.Save,
        lambda: parent.save_theme()
    ))
    file_menu.addAction(_create_action(
        parent, "Save As...", QKeySequence("Ctrl+Shift+S"),
        lambda: parent.save_theme_as()
    ))
    file_menu.addSeparator()

    file_menu.addAction(_create_action(
        parent, "Export...", QKeySequence("Ctrl+E"),
        lambda: print("Export (stub)")
    ))
    file_menu.addSeparator()

    file_menu.addAction(_create_action(
        parent, "Exit", QKeySequence.Quit,
        lambda: parent.close()
    ))

    # Edit menu
    edit_menu = menubar.addMenu("&Edit")

    # Create undo/redo actions and store them on parent for state updates
    parent.undo_action = _create_action(
        parent, "Undo", QKeySequence.Undo,
        lambda: parent.undo()
    )
    parent.undo_action.setEnabled(False)  # Initially disabled
    edit_menu.addAction(parent.undo_action)

    parent.redo_action = _create_action(
        parent, "Redo", QKeySequence.Redo,
        lambda: parent.redo()
    )
    parent.redo_action.setEnabled(False)  # Initially disabled
    edit_menu.addAction(parent.redo_action)
    edit_menu.addSeparator()

    edit_menu.addAction(_create_action(
        parent, "Find Token...", QKeySequence.Find,
        lambda: print("Find token (stub)")
    ))
    edit_menu.addSeparator()

    edit_menu.addAction(_create_action(
        parent, "Preferences...", QKeySequence.Preferences,
        lambda: print("Preferences (stub)")
    ))

    # Theme menu
    theme_menu = menubar.addMenu("&Theme")

    theme_menu.addAction(_create_action(
        parent, "Validate Accessibility", QKeySequence("F7"),
        lambda: print("Validate accessibility (stub)")
    ))
    theme_menu.addAction(_create_action(
        parent, "Compare Themes...", QKeySequence("Ctrl+D"),
        lambda: print("Compare themes (stub)")
    ))

    # View menu
    view_menu = menubar.addMenu("&View")

    view_menu.addAction(_create_action(
        parent, "Zoom In", QKeySequence.ZoomIn,
        lambda: print("Zoom in (stub)")
    ))
    view_menu.addAction(_create_action(
        parent, "Zoom Out", QKeySequence.ZoomOut,
        lambda: print("Zoom out (stub)")
    ))
    view_menu.addAction(_create_action(
        parent, "Reset Zoom", QKeySequence("Ctrl+0"),
        lambda: print("Reset zoom (stub)")
    ))
    view_menu.addSeparator()

    view_menu.addAction(_create_action(
        parent, "Fullscreen", QKeySequence("F11"),
        lambda: parent.toggle_fullscreen()
    ))

    # Tools menu
    tools_menu = menubar.addMenu("T&ools")

    tools_menu.addAction(_create_action(
        parent, "Palette Extractor...", QKeySequence("Ctrl+Shift+P"),
        lambda: print("Palette extractor (stub)")
    ))
    tools_menu.addAction(_create_action(
        parent, "Color Harmonizer...", QKeySequence("Ctrl+H"),
        lambda: print("Color harmonizer (stub)")
    ))
    tools_menu.addAction(_create_action(
        parent, "Bulk Edit...", QKeySequence("Ctrl+B"),
        lambda: print("Bulk edit (stub)")
    ))

    # Window menu
    window_menu = menubar.addMenu("&Window")

    window_menu.addAction(_create_action(
        parent, "Reset Layout", QKeySequence("Ctrl+Shift+R"),
        lambda: print("Reset layout (stub)")
    ))

    # Help menu
    help_menu = menubar.addMenu("&Help")

    help_menu.addAction(_create_action(
        parent, "Documentation", QKeySequence.HelpContents,
        lambda: print("Documentation (stub)")
    ))
    help_menu.addAction(_create_action(
        parent, "About VFTheme Studio...", QKeySequence(""),
        lambda: parent.show_about()
    ))

    return menubar


def _create_action(parent, text: str, shortcut, slot) -> QAction:
    """Helper to create an action with shortcut.

    Args:
        parent: Parent widget
        text: Action text
        shortcut: Keyboard shortcut
        slot: Slot to connect

    Returns:
        Configured QAction
    """
    action = QAction(text, parent)
    if shortcut:
        action.setShortcut(shortcut)
    action.triggered.connect(slot)
    return action
