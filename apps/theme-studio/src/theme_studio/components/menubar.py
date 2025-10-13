"""Menu bar builder for VFTheme Studio.

Uses KeybindingManager for user-customizable keyboard shortcuts.
"""

from PySide6.QtWidgets import QMenuBar


def create_menu_bar(parent) -> QMenuBar:
    """Create and configure the application menu bar.

    Uses QActions from parent.actions_by_id (created by KeybindingManager).
    This allows user-customizable keyboard shortcuts with persistent storage.

    Args:
        parent: Parent window with actions_by_id dict

    Returns:
        Configured QMenuBar
    """
    menubar = parent.menuBar()

    # Get actions dict from parent (created by KeybindingManager)
    actions = parent.actions_by_id

    # ====================  FILE MENU ====================
    file_menu = menubar.addMenu("&File")

    file_menu.addAction(actions.get("file.new"))
    file_menu.addAction(actions.get("file.new_from_template"))
    file_menu.addSeparator()

    file_menu.addAction(actions.get("file.open"))
    file_menu.addSeparator()

    file_menu.addAction(actions.get("file.save"))
    file_menu.addAction(actions.get("file.save_as"))
    file_menu.addSeparator()

    file_menu.addAction(actions.get("file.export"))
    file_menu.addSeparator()

    file_menu.addAction(actions.get("file.exit"))

    # ====================  EDIT MENU ====================
    edit_menu = menubar.addMenu("&Edit")

    # Undo/Redo actions (will be enabled/disabled by undo stack)
    undo_action = actions.get("edit.undo")
    redo_action = actions.get("edit.redo")
    if undo_action:
        undo_action.setEnabled(False)  # Initially disabled
        edit_menu.addAction(undo_action)
    if redo_action:
        redo_action.setEnabled(False)  # Initially disabled
        edit_menu.addAction(redo_action)
    edit_menu.addSeparator()

    edit_menu.addAction(actions.get("edit.find"))
    edit_menu.addSeparator()

    edit_menu.addAction(actions.get("edit.preferences"))

    # ====================  THEME MENU ====================
    theme_menu = menubar.addMenu("&Theme")

    theme_menu.addAction(actions.get("theme.validate_accessibility"))
    theme_menu.addAction(actions.get("theme.compare"))

    # ====================  VIEW MENU ====================
    view_menu = menubar.addMenu("&View")

    view_menu.addAction(actions.get("view.zoom_in"))
    view_menu.addAction(actions.get("view.zoom_out"))
    view_menu.addAction(actions.get("view.reset_zoom"))
    view_menu.addSeparator()

    view_menu.addAction(actions.get("view.fullscreen"))

    # ====================  TOOLS MENU ====================
    tools_menu = menubar.addMenu("T&ools")

    tools_menu.addAction(actions.get("tools.palette_extractor"))
    tools_menu.addAction(actions.get("tools.color_harmonizer"))
    tools_menu.addAction(actions.get("tools.bulk_edit"))

    # ====================  WINDOW MENU ====================
    window_menu = menubar.addMenu("&Window")

    window_menu.addAction(actions.get("window.reset_layout"))

    # ====================  HELP MENU ====================
    help_menu = menubar.addMenu("&Help")

    help_menu.addAction(actions.get("help.documentation"))
    help_menu.addAction(actions.get("help.about"))

    return menubar
