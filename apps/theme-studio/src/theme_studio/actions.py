"""Action definitions for VFTheme Studio keyboard shortcuts.

This module defines all application actions using the keybinding_manager widget,
enabling user-customizable keyboard shortcuts with persistent storage.
"""

from vfwidgets_keybinding import ActionDefinition


def get_action_definitions() -> list[ActionDefinition]:
    """Get all action definitions for VFTheme Studio.

    Returns:
        List of ActionDefinition objects organized by category
    """
    return [
        # ==================== FILE ACTIONS ====================
        ActionDefinition(
            id="file.new",
            description="New Theme",
            default_shortcut="Ctrl+N",
            category="File",
        ),
        ActionDefinition(
            id="file.new_from_template",
            description="New from Template...",
            default_shortcut="Ctrl+Shift+N",
            category="File",
        ),
        ActionDefinition(
            id="file.open",
            description="Open Theme...",
            default_shortcut="Ctrl+O",
            category="File",
        ),
        ActionDefinition(
            id="file.save",
            description="Save",
            default_shortcut="Ctrl+S",
            category="File",
        ),
        ActionDefinition(
            id="file.save_as",
            description="Save As...",
            default_shortcut="Ctrl+Shift+S",
            category="File",
        ),
        ActionDefinition(
            id="file.export",
            description="Export...",
            default_shortcut="Ctrl+E",
            category="File",
        ),
        ActionDefinition(
            id="file.exit",
            description="Exit",
            default_shortcut="Ctrl+Q",
            category="File",
        ),
        # ==================== EDIT ACTIONS ====================
        ActionDefinition(
            id="edit.undo",
            description="Undo",
            default_shortcut="Ctrl+Z",
            category="Edit",
        ),
        ActionDefinition(
            id="edit.redo",
            description="Redo",
            default_shortcut="Ctrl+Shift+Z",
            category="Edit",
        ),
        ActionDefinition(
            id="edit.find",
            description="Find Token...",
            default_shortcut="Ctrl+F",
            category="Edit",
        ),
        ActionDefinition(
            id="edit.preferences",
            description="Preferences...",
            default_shortcut="Ctrl+,",
            category="Edit",
        ),
        # ==================== THEME ACTIONS ====================
        ActionDefinition(
            id="theme.validate_accessibility",
            description="Validate Accessibility",
            default_shortcut="F7",
            category="Theme",
        ),
        ActionDefinition(
            id="theme.compare",
            description="Compare Themes...",
            default_shortcut="Ctrl+D",
            category="Theme",
        ),
        # ==================== VIEW ACTIONS ====================
        ActionDefinition(
            id="view.zoom_in",
            description="Zoom In",
            default_shortcut="Ctrl++",
            category="View",
        ),
        ActionDefinition(
            id="view.zoom_out",
            description="Zoom Out",
            default_shortcut="Ctrl+-",
            category="View",
        ),
        ActionDefinition(
            id="view.reset_zoom",
            description="Reset Zoom",
            default_shortcut="Ctrl+0",
            category="View",
        ),
        ActionDefinition(
            id="view.fullscreen",
            description="Fullscreen",
            default_shortcut="F11",
            category="View",
        ),
        # ==================== TOOLS ACTIONS ====================
        ActionDefinition(
            id="tools.palette_extractor",
            description="Palette Extractor...",
            default_shortcut="Ctrl+Shift+P",
            category="Tools",
        ),
        ActionDefinition(
            id="tools.color_harmonizer",
            description="Color Harmonizer...",
            default_shortcut="Ctrl+H",
            category="Tools",
        ),
        ActionDefinition(
            id="tools.bulk_edit",
            description="Bulk Edit...",
            default_shortcut="Ctrl+B",
            category="Tools",
        ),
        # ==================== WINDOW ACTIONS ====================
        ActionDefinition(
            id="window.reset_layout",
            description="Reset Layout",
            default_shortcut="Ctrl+Shift+R",
            category="Window",
        ),
        # ==================== HELP ACTIONS ====================
        ActionDefinition(
            id="help.documentation",
            description="Documentation",
            default_shortcut="F1",
            category="Help",
        ),
        ActionDefinition(
            id="help.about",
            description="About VFTheme Studio...",
            default_shortcut="",  # No shortcut
            category="Help",
        ),
    ]
