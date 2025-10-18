"""Color Token Registry - Complete Token System for Theme 2.0.

This module defines all 170+ color tokens used in the VFWidgets theme system,
organized into 14 categories following VSCode's hierarchical approach.

Key Features:
- Complete token registry with descriptions
- Hierarchical organization (14 categories)
- Token validation
- Smart defaults for missing tokens
- Documentation for every token

Categories:
1. Base Colors (10 tokens)
2. Button Colors (15 tokens)
3. Input/Dropdown Colors (18 tokens)
4. List/Tree Colors (22 tokens)
5. Editor Colors (35+ tokens)
6. Sidebar Colors (12 tokens)
7. Panel Colors (15 tokens)
8. Tab Colors (20 tokens)
9. Activity Bar Colors (10 tokens)
10. Status Bar Colors (12 tokens)
11. Title Bar Colors (10 tokens)
12. Menu Colors (15 tokens)
13. Scrollbar Colors (8 tokens)
14. Miscellaneous (10 tokens)

Total: ~190 tokens
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class TokenCategory(Enum):
    """Token categories for organization."""

    BASE = "base"
    BUTTON = "button"
    INPUT = "input"
    LIST = "list"
    EDITOR = "editor"
    SIDEBAR = "sidebar"
    PANEL = "panel"
    TAB = "tab"
    ACTIVITY_BAR = "activityBar"
    STATUS_BAR = "statusBar"
    TITLE_BAR = "titleBar"
    MENU = "menu"
    SCROLLBAR = "scrollbar"
    TERMINAL = "terminal"
    MARKDOWN = "markdown"
    MISC = "misc"


@dataclass
class ColorToken:
    """Represents a single color token with metadata."""

    name: str
    category: TokenCategory
    description: str
    default_light: str  # Default value for light themes
    default_dark: str  # Default value for dark themes
    required: bool = True  # Whether token must be defined


class ColorTokenRegistry:
    """Registry of all color tokens in the theme system."""

    # Base Colors Category
    BASE_COLORS: list[ColorToken] = [
        ColorToken(
            "colors.foreground",
            TokenCategory.BASE,
            "Default foreground color for text",
            "#000000",
            "#d4d4d4",
        ),
        ColorToken(
            "colors.background",
            TokenCategory.BASE,
            "Default background color",
            "#ffffff",
            "#1e1e1e",
        ),
        ColorToken(
            "colors.focusBorder",
            TokenCategory.BASE,
            "Overall border color for focused elements",
            "#0078d4",
            "#007acc",
        ),
        ColorToken(
            "colors.contrastBorder",
            TokenCategory.BASE,
            "Extra contrast border for high contrast themes",
            "#cccccc",
            "#3c3c3c",
        ),
        ColorToken(
            "colors.errorForeground",
            TokenCategory.BASE,
            "Overall foreground color for error messages",
            "#dc3545",
            "#f48771",
        ),
        ColorToken(
            "colors.warningForeground",
            TokenCategory.BASE,
            "Overall foreground color for warning messages",
            "#ffc107",
            "#cca700",
        ),
        ColorToken(
            "colors.disabledForeground",
            TokenCategory.BASE,
            "Overall foreground for disabled elements",
            "#999999",
            "#555555",
        ),
        ColorToken(
            "colors.descriptionForeground",
            TokenCategory.BASE,
            "Foreground color for description text",
            "#6c757d",
            "#999999",
        ),
        ColorToken(
            "colors.iconForeground",
            TokenCategory.BASE,
            "Default color for icons",
            "#424242",
            "#c5c5c5",
        ),
        ColorToken(
            "colors.primary", TokenCategory.BASE, "Primary brand/accent color", "#0078d4", "#007acc"
        ),
        ColorToken(
            "colors.secondary",
            TokenCategory.BASE,
            "Secondary brand/accent color",
            "#6c757d",
            "#999999",
        ),
    ]

    # Button Colors Category
    BUTTON_COLORS: list[ColorToken] = [
        # Primary button (default)
        ColorToken(
            "button.background",
            TokenCategory.BUTTON,
            "Button background color",
            "#0078d4",
            "#0e639c",
        ),
        ColorToken(
            "button.foreground",
            TokenCategory.BUTTON,
            "Button foreground color",
            "#ffffff",
            "#ffffff",
        ),
        ColorToken(
            "button.border",
            TokenCategory.BUTTON,
            "Button border color (use 'none' for no border)",
            "none",
            "none",
        ),
        ColorToken(
            "button.hoverBackground",
            TokenCategory.BUTTON,
            "Button background when hovering",
            "#106ebe",
            "#1177bb",
        ),
        ColorToken(
            "button.hoverForeground",
            TokenCategory.BUTTON,
            "Button foreground when hovering",
            "#ffffff",
            "#ffffff",
            False,
        ),
        ColorToken(
            "button.pressedBackground",
            TokenCategory.BUTTON,
            "Button background when pressed",
            "#005a9e",
            "#094771",
        ),
        ColorToken(
            "button.disabledBackground",
            TokenCategory.BUTTON,
            "Button background when disabled",
            "#cccccc",
            "#555555",
        ),
        ColorToken(
            "button.disabledForeground",
            TokenCategory.BUTTON,
            "Button foreground when disabled",
            "#999999",
            "#999999",
        ),
        # Secondary button variant
        ColorToken(
            "button.secondary.background",
            TokenCategory.BUTTON,
            "Secondary button background",
            "#f0f0f0",
            "#313131",
        ),
        ColorToken(
            "button.secondary.foreground",
            TokenCategory.BUTTON,
            "Secondary button foreground",
            "#323130",
            "#cccccc",
        ),
        ColorToken(
            "button.secondary.hoverBackground",
            TokenCategory.BUTTON,
            "Secondary button hover background",
            "#e0e0e0",
            "#3e3e3e",
        ),
        # Danger button variant
        ColorToken(
            "button.danger.background",
            TokenCategory.BUTTON,
            "Danger button background (destructive actions)",
            "#dc3545",
            "#dc3545",
        ),
        ColorToken(
            "button.danger.hoverBackground",
            TokenCategory.BUTTON,
            "Danger button hover background",
            "#c82333",
            "#c82333",
        ),
        # Success button variant
        ColorToken(
            "button.success.background",
            TokenCategory.BUTTON,
            "Success button background (positive actions)",
            "#28a745",
            "#28a745",
        ),
        ColorToken(
            "button.success.hoverBackground",
            TokenCategory.BUTTON,
            "Success button hover background",
            "#218838",
            "#218838",
        ),
        # Warning button variant
        ColorToken(
            "button.warning.background",
            TokenCategory.BUTTON,
            "Warning button background (caution actions)",
            "#ffc107",
            "#ffc107",
        ),
        ColorToken(
            "button.warning.foreground",
            TokenCategory.BUTTON,
            "Warning button foreground",
            "#000000",
            "#000000",
        ),
        ColorToken(
            "button.warning.hoverBackground",
            TokenCategory.BUTTON,
            "Warning button hover background",
            "#e0a800",
            "#e0a800",
        ),
    ]

    # Input/Dropdown Colors Category
    INPUT_COLORS: list[ColorToken] = [
        # Text input (QLineEdit, QTextEdit)
        ColorToken(
            "input.background", TokenCategory.INPUT, "Input field background", "#ffffff", "#3c3c3c"
        ),
        ColorToken(
            "input.foreground", TokenCategory.INPUT, "Input field foreground", "#000000", "#cccccc"
        ),
        ColorToken("input.border", TokenCategory.INPUT, "Input field border", "#cccccc", "#3c3c3c"),
        ColorToken(
            "input.placeholderForeground",
            TokenCategory.INPUT,
            "Input field placeholder text foreground",
            "#999999",
            "#989898",
        ),
        ColorToken(
            "input.focusBorder",
            TokenCategory.INPUT,
            "Input field border when focused",
            "#0078d4",
            "#007acc",
        ),
        ColorToken(
            "input.focusBackground",
            TokenCategory.INPUT,
            "Input field background when focused",
            "#ffffff",
            "#3c3c3c",
            False,
        ),
        ColorToken(
            "input.disabledBackground",
            TokenCategory.INPUT,
            "Input field background when disabled",
            "#f0f0f0",
            "#555555",
        ),
        ColorToken(
            "input.disabledForeground",
            TokenCategory.INPUT,
            "Input field foreground when disabled",
            "#999999",
            "#999999",
        ),
        ColorToken(
            "input.errorBorder",
            TokenCategory.INPUT,
            "Input field border for validation errors",
            "#dc3545",
            "#f48771",
        ),
        # Dropdown/Combo (QComboBox)
        ColorToken(
            "dropdown.background", TokenCategory.INPUT, "Dropdown background", "#ffffff", "#3c3c3c"
        ),
        ColorToken(
            "dropdown.foreground", TokenCategory.INPUT, "Dropdown foreground", "#000000", "#cccccc"
        ),
        ColorToken("dropdown.border", TokenCategory.INPUT, "Dropdown border", "#cccccc", "#3c3c3c"),
        ColorToken(
            "dropdown.listBackground",
            TokenCategory.INPUT,
            "Dropdown popup list background",
            "#ffffff",
            "#252526",
        ),
        ColorToken(
            "dropdown.listForeground",
            TokenCategory.INPUT,
            "Dropdown popup list foreground",
            "#000000",
            "#cccccc",
        ),
        # Combobox specific
        ColorToken(
            "combobox.background", TokenCategory.INPUT, "Combobox background", "#ffffff", "#3c3c3c"
        ),
        ColorToken(
            "combobox.foreground", TokenCategory.INPUT, "Combobox foreground", "#000000", "#cccccc"
        ),
        ColorToken("combobox.border", TokenCategory.INPUT, "Combobox border", "#cccccc", "#3c3c3c"),
        ColorToken(
            "combobox.arrowForeground",
            TokenCategory.INPUT,
            "Combobox dropdown arrow color",
            "#424242",
            "#999999",
        ),
    ]

    # List/Tree Colors Category
    LIST_COLORS: list[ColorToken] = [
        ColorToken(
            "list.background", TokenCategory.LIST, "List/tree background", "#ffffff", "#252526"
        ),
        ColorToken(
            "list.foreground", TokenCategory.LIST, "List/tree foreground", "#000000", "#cccccc"
        ),
        # Selection (active window)
        ColorToken(
            "list.activeSelectionBackground",
            TokenCategory.LIST,
            "List/tree background when selected and window is focused",
            "#0078d4",
            "#094771",
        ),
        ColorToken(
            "list.activeSelectionForeground",
            TokenCategory.LIST,
            "List/tree foreground when selected and window is focused",
            "#ffffff",
            "#ffffff",
        ),
        # Selection (inactive window)
        ColorToken(
            "list.inactiveSelectionBackground",
            TokenCategory.LIST,
            "List/tree background when selected and window is unfocused",
            "#e0e0e0",
            "#37373d",
        ),
        ColorToken(
            "list.inactiveSelectionForeground",
            TokenCategory.LIST,
            "List/tree foreground when selected and window is unfocused",
            "#000000",
            "#cccccc",
        ),
        # Hover
        ColorToken(
            "list.hoverBackground",
            TokenCategory.LIST,
            "List/tree background when hovering",
            "#f0f0f0",
            "#2a2d2e",
        ),
        ColorToken(
            "list.hoverForeground",
            TokenCategory.LIST,
            "List/tree foreground when hovering",
            "#000000",
            "#cccccc",
            False,
        ),
        # Focus (keyboard)
        ColorToken(
            "list.focusBackground",
            TokenCategory.LIST,
            "List/tree background for focused item via keyboard",
            "#e0e0e0",
            "#062f4a",
        ),
        ColorToken(
            "list.focusForeground",
            TokenCategory.LIST,
            "List/tree foreground for focused item via keyboard",
            "#000000",
            "#cccccc",
            False,
        ),
        ColorToken(
            "list.focusOutline",
            TokenCategory.LIST,
            "List/tree outline color for focused item",
            "#0078d4",
            "#007acc",
        ),
        # Special item states
        ColorToken(
            "list.highlightForeground",
            TokenCategory.LIST,
            "List/tree foreground for matched highlights (e.g., search)",
            "#0078d4",
            "#75beff",
        ),
        ColorToken(
            "list.invalidItemForeground",
            TokenCategory.LIST,
            "List/tree foreground for invalid items",
            "#dc3545",
            "#f48771",
        ),
        ColorToken(
            "list.errorForeground",
            TokenCategory.LIST,
            "List/tree foreground for error items",
            "#dc3545",
            "#f48771",
        ),
        ColorToken(
            "list.warningForeground",
            TokenCategory.LIST,
            "List/tree foreground for warning items",
            "#ffc107",
            "#cca700",
        ),
        # Tree-specific
        ColorToken(
            "tree.indentGuidesStroke",
            TokenCategory.LIST,
            "Tree indent guide line color",
            "#cccccc",
            "#585858",
        ),
        # Table-specific
        ColorToken(
            "table.gridColor", TokenCategory.LIST, "Table grid line color", "#e0e0e0", "#3c3c3c"
        ),
        ColorToken(
            "table.headerBackground",
            TokenCategory.LIST,
            "Table header background",
            "#f0f0f0",
            "#2d2d2d",
        ),
        ColorToken(
            "table.headerForeground",
            TokenCategory.LIST,
            "Table header foreground",
            "#000000",
            "#cccccc",
        ),
        # List/tree drop target
        ColorToken(
            "list.dropBackground",
            TokenCategory.LIST,
            "List/tree background for drag-and-drop target",
            "#0078d4",
            "#062f4a",
            False,
        ),
    ]

    # Editor Colors Category (35+ tokens)
    EDITOR_COLORS: list[ColorToken] = [
        # Basic editor
        ColorToken(
            "editor.background",
            TokenCategory.EDITOR,
            "Editor background color",
            "#ffffff",
            "#1e1e1e",
        ),
        ColorToken(
            "editor.foreground",
            TokenCategory.EDITOR,
            "Editor default foreground color",
            "#000000",
            "#d4d4d4",
        ),
        # Selection
        ColorToken(
            "editor.selectionBackground",
            TokenCategory.EDITOR,
            "Color of editor selection",
            "#add6ff",
            "#264f78",
        ),
        ColorToken(
            "editor.selectionForeground",
            TokenCategory.EDITOR,
            "Color of selected text",
            "#000000",
            "#ffffff",
            False,
        ),
        ColorToken(
            "editor.inactiveSelectionBackground",
            TokenCategory.EDITOR,
            "Color of selection when editor is unfocused",
            "#e5ebf1",
            "#3a3d41",
        ),
        # Current line
        ColorToken(
            "editor.lineHighlightBackground",
            TokenCategory.EDITOR,
            "Background color for line highlight",
            "#f0f0f0",
            "#282828",
        ),
        ColorToken(
            "editor.lineHighlightBorder",
            TokenCategory.EDITOR,
            "Border color for line highlight",
            "transparent",
            "transparent",
            False,
        ),
        # Cursor
        ColorToken(
            "editor.cursorForeground",
            TokenCategory.EDITOR,
            "Color of editor cursor",
            "#000000",
            "#aeafad",
        ),
        # Line numbers
        ColorToken(
            "editorLineNumber.foreground",
            TokenCategory.EDITOR,
            "Color of editor line numbers",
            "#999999",
            "#858585",
        ),
        ColorToken(
            "editorLineNumber.activeForeground",
            TokenCategory.EDITOR,
            "Color of active editor line number",
            "#000000",
            "#c6c6c6",
        ),
        # Indentation guides
        ColorToken(
            "editorIndentGuide.background",
            TokenCategory.EDITOR,
            "Color of editor indentation guides",
            "#d3d3d3",
            "#404040",
        ),
        ColorToken(
            "editorIndentGuide.activeBackground",
            TokenCategory.EDITOR,
            "Color of active editor indentation guide",
            "#999999",
            "#707070",
        ),
        # Whitespace
        ColorToken(
            "editorWhitespace.foreground",
            TokenCategory.EDITOR,
            "Color of whitespace characters",
            "#d3d3d3",
            "#404040",
        ),
        # Bracket matching
        ColorToken(
            "editorBracketMatch.background",
            TokenCategory.EDITOR,
            "Background color of matching brackets",
            "#add6ff",
            "#0064001a",
        ),
        ColorToken(
            "editorBracketMatch.border",
            TokenCategory.EDITOR,
            "Border color of matching brackets",
            "#888888",
            "#888888",
        ),
        # Editor widgets (find, hover, suggest)
        ColorToken(
            "editorWidget.background",
            TokenCategory.EDITOR,
            "Background color of editor widgets (find, hover)",
            "#f0f0f0",
            "#252526",
        ),
        ColorToken(
            "editorWidget.border",
            TokenCategory.EDITOR,
            "Border color of editor widgets",
            "#cccccc",
            "#454545",
        ),
        ColorToken(
            "editorWidget.foreground",
            TokenCategory.EDITOR,
            "Foreground color of editor widgets",
            "#000000",
            "#cccccc",
            False,
        ),
        # Suggest widget
        ColorToken(
            "editorSuggestWidget.background",
            TokenCategory.EDITOR,
            "Background color of suggestion widget",
            "#f0f0f0",
            "#252526",
        ),
        ColorToken(
            "editorSuggestWidget.border",
            TokenCategory.EDITOR,
            "Border color of suggestion widget",
            "#cccccc",
            "#454545",
        ),
        ColorToken(
            "editorSuggestWidget.foreground",
            TokenCategory.EDITOR,
            "Foreground color of suggestion widget",
            "#000000",
            "#d4d4d4",
        ),
        ColorToken(
            "editorSuggestWidget.selectedBackground",
            TokenCategory.EDITOR,
            "Background color of selected suggestion",
            "#0078d4",
            "#094771",
        ),
        ColorToken(
            "editorSuggestWidget.highlightForeground",
            TokenCategory.EDITOR,
            "Color of matched highlights in suggestion widget",
            "#0078d4",
            "#75beff",
        ),
        # Hover widget
        ColorToken(
            "editorHoverWidget.background",
            TokenCategory.EDITOR,
            "Background color of hover widget",
            "#f0f0f0",
            "#252526",
        ),
        ColorToken(
            "editorHoverWidget.border",
            TokenCategory.EDITOR,
            "Border color of hover widget",
            "#cccccc",
            "#454545",
        ),
        ColorToken(
            "editorHoverWidget.foreground",
            TokenCategory.EDITOR,
            "Foreground color of hover widget",
            "#000000",
            "#cccccc",
            False,
        ),
        # Gutter (line numbers area)
        ColorToken(
            "editorGutter.background",
            TokenCategory.EDITOR,
            "Background color of editor gutter",
            "#f0f0f0",
            "#1e1e1e",
            False,
        ),
        ColorToken(
            "editorGutter.addedBackground",
            TokenCategory.EDITOR,
            "Editor gutter decoration for added lines",
            "#28a745",
            "#28a745",
            False,
        ),
        ColorToken(
            "editorGutter.deletedBackground",
            TokenCategory.EDITOR,
            "Editor gutter decoration for deleted lines",
            "#dc3545",
            "#dc3545",
            False,
        ),
        ColorToken(
            "editorGutter.modifiedBackground",
            TokenCategory.EDITOR,
            "Editor gutter decoration for modified lines",
            "#0078d4",
            "#007acc",
            False,
        ),
        # Rulers
        ColorToken(
            "editorRuler.foreground",
            TokenCategory.EDITOR,
            "Color of editor rulers",
            "#d3d3d3",
            "#5a5a5a",
        ),
        # Find match
        ColorToken(
            "editor.findMatchBackground",
            TokenCategory.EDITOR,
            "Color of current find match",
            "#ffff00",
            "#9e6a03",
            False,
        ),
        ColorToken(
            "editor.findMatchHighlightBackground",
            TokenCategory.EDITOR,
            "Color of other find matches",
            "#ffff0066",
            "#ea5c0055",
            False,
        ),
    ]

    # Sidebar Colors Category
    SIDEBAR_COLORS: list[ColorToken] = [
        ColorToken(
            "sideBar.background",
            TokenCategory.SIDEBAR,
            "Sidebar background color",
            "#f3f3f3",
            "#252526",
        ),
        ColorToken(
            "sideBar.foreground",
            TokenCategory.SIDEBAR,
            "Sidebar foreground color",
            "#000000",
            "#cccccc",
        ),
        ColorToken(
            "sideBar.border", TokenCategory.SIDEBAR, "Sidebar border color", "#e0e0e0", "#2b2b2b"
        ),
        ColorToken(
            "sideBarTitle.foreground",
            TokenCategory.SIDEBAR,
            "Sidebar title foreground color",
            "#000000",
            "#bbbbbb",
        ),
        ColorToken(
            "sideBarSectionHeader.background",
            TokenCategory.SIDEBAR,
            "Sidebar section header background",
            "#e0e0e0",
            "#2d2d2d",
        ),
        ColorToken(
            "sideBarSectionHeader.foreground",
            TokenCategory.SIDEBAR,
            "Sidebar section header foreground",
            "#000000",
            "#cccccc",
        ),
        ColorToken(
            "sideBarSectionHeader.border",
            TokenCategory.SIDEBAR,
            "Sidebar section header border",
            "transparent",
            "#cccccc33",
            False,
        ),
    ]

    # Panel Colors Category
    PANEL_COLORS: list[ColorToken] = [
        ColorToken(
            "panel.background", TokenCategory.PANEL, "Panel background color", "#ffffff", "#1e1e1e"
        ),
        ColorToken(
            "panel.foreground",
            TokenCategory.PANEL,
            "Panel foreground color",
            "#000000",
            "#d4d4d4",
            False,
        ),
        ColorToken("panel.border", TokenCategory.PANEL, "Panel border color", "#e0e0e0", "#2b2b2b"),
        ColorToken(
            "panelTitle.activeForeground",
            TokenCategory.PANEL,
            "Active panel title foreground",
            "#000000",
            "#e7e7e7",
        ),
        ColorToken(
            "panelTitle.activeBorder",
            TokenCategory.PANEL,
            "Active panel title border (bottom)",
            "#0078d4",
            "#007acc",
        ),
        ColorToken(
            "panelTitle.inactiveForeground",
            TokenCategory.PANEL,
            "Inactive panel title foreground",
            "#999999",
            "#999999",
        ),
        ColorToken(
            "panelSection.border",
            TokenCategory.PANEL,
            "Panel section border",
            "#e0e0e0",
            "#2b2b2b",
            False,
        ),
        ColorToken(
            "panelSection.dropBackground",
            TokenCategory.PANEL,
            "Panel drag-and-drop background",
            "#0078d4",
            "#53595d80",
            False,
        ),
    ]

    # Tab Colors Category
    TAB_COLORS: list[ColorToken] = [
        # Active tab
        ColorToken(
            "tab.activeBackground", TokenCategory.TAB, "Active tab background", "#ffffff", "#1e1e1e"
        ),
        ColorToken(
            "tab.activeForeground", TokenCategory.TAB, "Active tab foreground", "#000000", "#ffffff"
        ),
        ColorToken(
            "tab.activeBorder",
            TokenCategory.TAB,
            "Active tab border (bottom)",
            "transparent",
            "transparent",
            False,
        ),
        ColorToken(
            "tab.activeBorderTop",
            TokenCategory.TAB,
            "Active tab border (top)",
            "transparent",
            "#007acc",
            False,
        ),
        # Inactive tabs
        ColorToken(
            "tab.inactiveBackground",
            TokenCategory.TAB,
            "Inactive tab background",
            "#ececec",
            "#2d2d2d",
        ),
        ColorToken(
            "tab.inactiveForeground",
            TokenCategory.TAB,
            "Inactive tab foreground",
            "#666666",
            "#969696",
        ),
        # Hover
        ColorToken(
            "tab.hoverBackground",
            TokenCategory.TAB,
            "Tab background when hovering",
            "#f0f0f0",
            "#2a2d2e",
        ),
        ColorToken(
            "tab.hoverForeground",
            TokenCategory.TAB,
            "Tab foreground when hovering",
            "#000000",
            "#ffffff",
            False,
        ),
        ColorToken(
            "tab.hoverBorder",
            TokenCategory.TAB,
            "Tab border when hovering",
            "transparent",
            "transparent",
            False,
        ),
        # Unfocused window
        ColorToken(
            "tab.unfocusedActiveBackground",
            TokenCategory.TAB,
            "Active tab background in unfocused window",
            "#ffffff",
            "#1e1e1e",
        ),
        ColorToken(
            "tab.unfocusedActiveForeground",
            TokenCategory.TAB,
            "Active tab foreground in unfocused window",
            "#000000",
            "#ffffff80",
        ),
        ColorToken(
            "tab.unfocusedInactiveBackground",
            TokenCategory.TAB,
            "Inactive tab background in unfocused window",
            "#ececec",
            "#2d2d2d",
        ),
        ColorToken(
            "tab.unfocusedInactiveForeground",
            TokenCategory.TAB,
            "Inactive tab foreground in unfocused window",
            "#666666",
            "#96969680",
        ),
        # Tab bar
        ColorToken("tab.border", TokenCategory.TAB, "Border between tabs", "#e0e0e0", "#252526"),
        ColorToken(
            "tabBar.background",
            TokenCategory.TAB,
            "Tab bar background",
            "#f3f3f3",
            "#252526",
            False,
        ),
        ColorToken(
            "tabBar.border", TokenCategory.TAB, "Tab bar border", "transparent", "#252526", False
        ),
        # Modified indicator
        ColorToken(
            "tab.modifiedBorder",
            TokenCategory.TAB,
            "Border for modified tabs (unsaved)",
            "#0078d4",
            "#007acc",
            False,
        ),
    ]

    # Activity Bar Colors Category
    ACTIVITYBAR_COLORS: list[ColorToken] = [
        ColorToken(
            "activityBar.background",
            TokenCategory.ACTIVITY_BAR,
            "Activity bar background",
            "#2c2c2c",
            "#333333",
        ),
        ColorToken(
            "activityBar.foreground",
            TokenCategory.ACTIVITY_BAR,
            "Activity bar foreground (icons)",
            "#ffffff",
            "#ffffff",
        ),
        ColorToken(
            "activityBar.inactiveForeground",
            TokenCategory.ACTIVITY_BAR,
            "Activity bar inactive foreground",
            "#999999",
            "#999999",
        ),
        ColorToken(
            "activityBar.border",
            TokenCategory.ACTIVITY_BAR,
            "Activity bar border",
            "transparent",
            "#2b2b2b",
            False,
        ),
        ColorToken(
            "activityBar.activeBorder",
            TokenCategory.ACTIVITY_BAR,
            "Activity bar active item border (left)",
            "#0078d4",
            "#007acc",
            False,
        ),
        ColorToken(
            "activityBar.activeBackground",
            TokenCategory.ACTIVITY_BAR,
            "Activity bar active item background",
            "transparent",
            "transparent",
            False,
        ),
        ColorToken(
            "activityBarBadge.background",
            TokenCategory.ACTIVITY_BAR,
            "Activity bar notification badge background",
            "#0078d4",
            "#007acc",
        ),
        ColorToken(
            "activityBarBadge.foreground",
            TokenCategory.ACTIVITY_BAR,
            "Activity bar notification badge foreground",
            "#ffffff",
            "#ffffff",
        ),
    ]

    # Status Bar Colors Category
    STATUSBAR_COLORS: list[ColorToken] = [
        ColorToken(
            "statusBar.background",
            TokenCategory.STATUS_BAR,
            "Status bar background",
            "#007acc",
            "#007acc",
        ),
        ColorToken(
            "statusBar.foreground",
            TokenCategory.STATUS_BAR,
            "Status bar foreground",
            "#ffffff",
            "#ffffff",
        ),
        ColorToken(
            "statusBar.border",
            TokenCategory.STATUS_BAR,
            "Status bar border",
            "transparent",
            "#2b2b2b",
            False,
        ),
        ColorToken(
            "statusBar.debuggingBackground",
            TokenCategory.STATUS_BAR,
            "Status bar background when debugging",
            "#cc6633",
            "#cc6633",
        ),
        ColorToken(
            "statusBar.debuggingForeground",
            TokenCategory.STATUS_BAR,
            "Status bar foreground when debugging",
            "#ffffff",
            "#ffffff",
        ),
        ColorToken(
            "statusBar.noFolderBackground",
            TokenCategory.STATUS_BAR,
            "Status bar background when no folder open",
            "#68217a",
            "#68217a",
        ),
        ColorToken(
            "statusBar.noFolderForeground",
            TokenCategory.STATUS_BAR,
            "Status bar foreground when no folder open",
            "#ffffff",
            "#ffffff",
            False,
        ),
        ColorToken(
            "statusBarItem.activeBackground",
            TokenCategory.STATUS_BAR,
            "Status bar item background when clicked",
            "#0078d480",
            "#ffffff25",
        ),
        ColorToken(
            "statusBarItem.hoverBackground",
            TokenCategory.STATUS_BAR,
            "Status bar item background when hovering",
            "#0078d450",
            "#ffffff15",
        ),
        ColorToken(
            "statusBarItem.prominentBackground",
            TokenCategory.STATUS_BAR,
            "Status bar prominent item background",
            "#0078d4",
            "#00000080",
            False,
        ),
        ColorToken(
            "statusBarItem.prominentHoverBackground",
            TokenCategory.STATUS_BAR,
            "Status bar prominent item background when hovering",
            "#106ebe",
            "#0000004d",
            False,
        ),
    ]

    # Title Bar Colors Category
    TITLEBAR_COLORS: list[ColorToken] = [
        ColorToken(
            "titleBar.activeBackground",
            TokenCategory.TITLE_BAR,
            "Title bar background when window is focused",
            "#dddddd",
            "#3c3c3c",
        ),
        ColorToken(
            "titleBar.activeForeground",
            TokenCategory.TITLE_BAR,
            "Title bar foreground when window is focused",
            "#000000",
            "#cccccc",
        ),
        ColorToken(
            "titleBar.inactiveBackground",
            TokenCategory.TITLE_BAR,
            "Title bar background when window is unfocused",
            "#dddddd99",
            "#3c3c3c99",
        ),
        ColorToken(
            "titleBar.inactiveForeground",
            TokenCategory.TITLE_BAR,
            "Title bar foreground when window is unfocused",
            "#00000099",
            "#cccccc99",
        ),
        ColorToken(
            "titleBar.border",
            TokenCategory.TITLE_BAR,
            "Title bar border",
            "transparent",
            "#00000060",
            False,
        ),
    ]

    # Menu Colors Category
    MENU_COLORS: list[ColorToken] = [
        ColorToken("menu.background", TokenCategory.MENU, "Menu background", "#ffffff", "#252526"),
        ColorToken("menu.foreground", TokenCategory.MENU, "Menu foreground", "#000000", "#cccccc"),
        ColorToken("menu.border", TokenCategory.MENU, "Menu border", "#cccccc", "#454545"),
        ColorToken(
            "menu.selectionBackground",
            TokenCategory.MENU,
            "Menu item background when selected",
            "#0078d4",
            "#094771",
        ),
        ColorToken(
            "menu.selectionForeground",
            TokenCategory.MENU,
            "Menu item foreground when selected",
            "#ffffff",
            "#ffffff",
        ),
        ColorToken(
            "menu.separatorBackground",
            TokenCategory.MENU,
            "Menu separator color",
            "#e0e0e0",
            "#454545",
        ),
        # Menu bar
        ColorToken(
            "menubar.background",
            TokenCategory.MENU,
            "Menu bar background",
            "#f3f3f3",
            "#3c3c3c",
            False,
        ),
        ColorToken(
            "menubar.foreground",
            TokenCategory.MENU,
            "Menu bar foreground",
            "#000000",
            "#cccccc",
            False,
        ),
        ColorToken(
            "menubar.selectionBackground",
            TokenCategory.MENU,
            "Menu bar item background when selected",
            "#0078d4",
            "#094771",
        ),
        ColorToken(
            "menubar.selectionForeground",
            TokenCategory.MENU,
            "Menu bar item foreground when selected",
            "#ffffff",
            "#ffffff",
        ),
        ColorToken(
            "menubar.selectionBorder",
            TokenCategory.MENU,
            "Menu bar selection border",
            "transparent",
            "transparent",
            False,
        ),
    ]

    # Scrollbar Colors Category
    SCROLLBAR_COLORS: list[ColorToken] = [
        ColorToken(
            "scrollbar.shadow",
            TokenCategory.SCROLLBAR,
            "Scrollbar shadow when content is scrolled",
            "#00000033",
            "#00000033",
        ),
        ColorToken(
            "scrollbarSlider.background",
            TokenCategory.SCROLLBAR,
            "Scrollbar slider background",
            "#64646466",
            "#79797966",
        ),
        ColorToken(
            "scrollbarSlider.hoverBackground",
            TokenCategory.SCROLLBAR,
            "Scrollbar slider background when hovering",
            "#646464b3",
            "#797979cc",
        ),
        ColorToken(
            "scrollbarSlider.activeBackground",
            TokenCategory.SCROLLBAR,
            "Scrollbar slider background when active",
            "#00000099",
            "#bfbfbf66",
        ),
    ]

    # Miscellaneous Colors Category
    MISC_COLORS: list[ColorToken] = [
        # Badges (notification counters)
        ColorToken(
            "badge.background", TokenCategory.MISC, "Badge background color", "#0078d4", "#007acc"
        ),
        ColorToken(
            "badge.foreground", TokenCategory.MISC, "Badge foreground color", "#ffffff", "#ffffff"
        ),
        # Notifications
        ColorToken(
            "notificationCenter.border",
            TokenCategory.MISC,
            "Notification center border",
            "#cccccc",
            "#2b2b2b",
            False,
        ),
        ColorToken(
            "notifications.background",
            TokenCategory.MISC,
            "Notification background",
            "#f0f0f0",
            "#252526",
        ),
        ColorToken(
            "notifications.foreground",
            TokenCategory.MISC,
            "Notification foreground",
            "#000000",
            "#cccccc",
        ),
        ColorToken(
            "notifications.border", TokenCategory.MISC, "Notification border", "#cccccc", "#2b2b2b"
        ),
        # Progress bar
        ColorToken(
            "progressBar.background",
            TokenCategory.MISC,
            "Progress bar background",
            "#0078d4",
            "#007acc",
        ),
        # Splitter
        ColorToken(
            "splitter.background",
            TokenCategory.MISC,
            "Splitter handle color",
            "#e0e0e0",
            "#3c3c3c",
            False,
        ),
    ]

    # Terminal Colors Category
    TERMINAL_COLORS: list[ColorToken] = [
        # Core terminal colors
        ColorToken(
            "terminal.colors.background",
            TokenCategory.TERMINAL,
            "Terminal background color",
            "#ffffff",
            "#1e1e1e",
        ),
        ColorToken(
            "terminal.colors.foreground",
            TokenCategory.TERMINAL,
            "Terminal foreground color",
            "#333333",
            "#cccccc",
        ),
        ColorToken(
            "terminalCursor.foreground",
            TokenCategory.TERMINAL,
            "Terminal cursor color",
            "#000000",
            "#ffffff",
        ),
        ColorToken(
            "terminalCursor.background",
            TokenCategory.TERMINAL,
            "Terminal cursor background",
            "#ffffff",
            "#000000",
            False,
        ),
        ColorToken(
            "terminal.selectionBackground",
            TokenCategory.TERMINAL,
            "Terminal selection background",
            "#add6ff80",
            "#264f7880",
        ),
        # ANSI Colors (normal)
        ColorToken(
            "terminal.colors.ansiBlack", TokenCategory.TERMINAL, "ANSI Black", "#000000", "#000000"
        ),
        ColorToken(
            "terminal.colors.ansiRed", TokenCategory.TERMINAL, "ANSI Red", "#cd3131", "#cd3131"
        ),
        ColorToken(
            "terminal.colors.ansiGreen", TokenCategory.TERMINAL, "ANSI Green", "#00bc00", "#0dbc79"
        ),
        ColorToken(
            "terminal.colors.ansiYellow",
            TokenCategory.TERMINAL,
            "ANSI Yellow",
            "#949800",
            "#e5e510",
        ),
        ColorToken(
            "terminal.colors.ansiBlue", TokenCategory.TERMINAL, "ANSI Blue", "#0451a5", "#2472c8"
        ),
        ColorToken(
            "terminal.colors.ansiMagenta",
            TokenCategory.TERMINAL,
            "ANSI Magenta",
            "#bc05bc",
            "#bc3fbc",
        ),
        ColorToken(
            "terminal.colors.ansiCyan", TokenCategory.TERMINAL, "ANSI Cyan", "#0598bc", "#11a8cd"
        ),
        ColorToken(
            "terminal.colors.ansiWhite", TokenCategory.TERMINAL, "ANSI White", "#555555", "#e5e5e5"
        ),
        # ANSI Colors (bright)
        ColorToken(
            "terminal.colors.ansiBrightBlack",
            TokenCategory.TERMINAL,
            "ANSI Bright Black",
            "#666666",
            "#666666",
        ),
        ColorToken(
            "terminal.colors.ansiBrightRed",
            TokenCategory.TERMINAL,
            "ANSI Bright Red",
            "#cd3131",
            "#f14c4c",
        ),
        ColorToken(
            "terminal.colors.ansiBrightGreen",
            TokenCategory.TERMINAL,
            "ANSI Bright Green",
            "#14ce14",
            "#23d18b",
        ),
        ColorToken(
            "terminal.colors.ansiBrightYellow",
            TokenCategory.TERMINAL,
            "ANSI Bright Yellow",
            "#b5ba00",
            "#f5f543",
        ),
        ColorToken(
            "terminal.colors.ansiBrightBlue",
            TokenCategory.TERMINAL,
            "ANSI Bright Blue",
            "#0451a5",
            "#3b8eea",
        ),
        ColorToken(
            "terminal.colors.ansiBrightMagenta",
            TokenCategory.TERMINAL,
            "ANSI Bright Magenta",
            "#bc05bc",
            "#d670d6",
        ),
        ColorToken(
            "terminal.colors.ansiBrightCyan",
            TokenCategory.TERMINAL,
            "ANSI Bright Cyan",
            "#0598bc",
            "#29b8db",
        ),
        ColorToken(
            "terminal.colors.ansiBrightWhite",
            TokenCategory.TERMINAL,
            "ANSI Bright White",
            "#a5a5a5",
            "#e5e5e5",
        ),
    ]

    # Markdown Colors Category
    MARKDOWN_COLORS: list[ColorToken] = [
        # Content colors
        ColorToken(
            "markdown.colors.background",
            TokenCategory.MARKDOWN,
            "Markdown background color",
            "#ffffff",
            "#0d1117",
            False,  # Optional - falls back to editor.background
        ),
        ColorToken(
            "markdown.colors.foreground",
            TokenCategory.MARKDOWN,
            "Markdown foreground/text color",
            "#24292f",
            "#c9d1d9",
            False,  # Optional - falls back to editor.foreground
        ),
        ColorToken(
            "markdown.colors.link",
            TokenCategory.MARKDOWN,
            "Markdown link color",
            "#0969da",
            "#58a6ff",
            False,  # Optional - falls back to button.background
        ),
        # Code block colors
        ColorToken(
            "markdown.colors.code.background",
            TokenCategory.MARKDOWN,
            "Markdown code block background",
            "#f6f8fa",
            "#161b22",
            False,  # Optional - falls back to input.background
        ),
        ColorToken(
            "markdown.colors.code.foreground",
            TokenCategory.MARKDOWN,
            "Markdown code block foreground",
            "#24292f",
            "#e6edf3",
            False,  # Optional - falls back to input.foreground
        ),
        # Blockquote colors
        ColorToken(
            "markdown.colors.blockquote.border",
            TokenCategory.MARKDOWN,
            "Markdown blockquote border color",
            "#d0d7de",
            "#3b434b",
            False,  # Optional - falls back to widget.border
        ),
        ColorToken(
            "markdown.colors.blockquote.background",
            TokenCategory.MARKDOWN,
            "Markdown blockquote background",
            "#f6f8fa",
            "rgba(110, 118, 129, 0.1)",
            False,  # Optional - falls back to widget.background
        ),
        # Table colors
        ColorToken(
            "markdown.colors.table.border",
            TokenCategory.MARKDOWN,
            "Markdown table border color",
            "#d0d7de",
            "#30363d",
            False,  # Optional - falls back to widget.border
        ),
        ColorToken(
            "markdown.colors.table.headerBackground",
            TokenCategory.MARKDOWN,
            "Markdown table header background",
            "#f6f8fa",
            "#161b22",
            False,  # Optional - falls back to editor.lineHighlightBackground
        ),
        # Scrollbar colors
        ColorToken(
            "markdown.colors.scrollbar.background",
            TokenCategory.MARKDOWN,
            "Markdown scrollbar background",
            "#ffffff",
            "#0d1117",
            False,  # Optional - falls back to editor.background
        ),
        ColorToken(
            "markdown.colors.scrollbar.thumb",
            TokenCategory.MARKDOWN,
            "Markdown scrollbar thumb",
            "#d0d7de",
            "#484f58",
            False,  # Optional - falls back to scrollbar.activeBackground
        ),
        ColorToken(
            "markdown.colors.scrollbar.thumbHover",
            TokenCategory.MARKDOWN,
            "Markdown scrollbar thumb on hover",
            "#b1bac4",
            "#6e7681",
            False,  # Optional - falls back to scrollbar.hoverBackground
        ),
    ]

    # Combine all tokens
    ALL_TOKENS: list[ColorToken] = (
        BASE_COLORS
        + BUTTON_COLORS
        + INPUT_COLORS
        + LIST_COLORS
        + EDITOR_COLORS
        + SIDEBAR_COLORS
        + PANEL_COLORS
        + TAB_COLORS
        + ACTIVITYBAR_COLORS
        + STATUSBAR_COLORS
        + TITLEBAR_COLORS
        + MENU_COLORS
        + SCROLLBAR_COLORS
        + TERMINAL_COLORS
        + MARKDOWN_COLORS
        + MISC_COLORS
    )

    @classmethod
    def get_all_token_names(cls) -> list[str]:
        """Get list of all token names."""
        return [token.name for token in cls.ALL_TOKENS]

    @classmethod
    def get_required_token_names(cls) -> list[str]:
        """Get list of required token names."""
        return [token.name for token in cls.ALL_TOKENS if token.required]

    @classmethod
    def get_tokens_by_category(cls, category: TokenCategory) -> list[ColorToken]:
        """Get all tokens in a category."""
        return [token for token in cls.ALL_TOKENS if token.category == category]

    @classmethod
    def get_token(cls, name: str) -> Optional[ColorToken]:
        """Get token by name."""
        for token in cls.ALL_TOKENS:
            if token.name == name:
                return token
        return None

    @classmethod
    def get_default_value(cls, token_name: str, is_dark_theme: bool) -> Optional[str]:
        """Get default value for a token."""
        token = cls.get_token(token_name)
        if token:
            return token.default_dark if is_dark_theme else token.default_light
        return None

    @classmethod
    def validate_theme_tokens(cls, theme_colors: dict[str, str]) -> list[str]:
        """Validate theme has all required tokens.

        Returns:
            List of missing required token names (empty if valid)

        """
        required = set(cls.get_required_token_names())
        provided = set(theme_colors.keys())
        missing = required - provided
        return sorted(missing)

    @classmethod
    def get_token_count(cls) -> int:
        """Get total number of tokens."""
        return len(cls.ALL_TOKENS)

    @classmethod
    def get_category_counts(cls) -> dict[str, int]:
        """Get token count per category."""
        counts = {}
        for category in TokenCategory:
            tokens = cls.get_tokens_by_category(category)
            counts[category.value] = len(tokens)
        return counts

    @classmethod
    def get(cls, token: str, theme: "Theme") -> str:
        """Get token value with theme-aware smart defaults and override support.

        This is the key integration point between ColorTokenRegistry and StylesheetGenerator.
        It implements the fallback chain (v2.0.0 with overlay support):
        1. Check ThemeManager overrides (user > app) [NEW in v2.0.0]
        2. Check if theme defines this token
        3. Use registry default based on theme type (dark/light)
        4. Smart heuristic based on token name

        Args:
            token: Token name (e.g., 'button.background')
            theme: Theme instance to get value from

        Returns:
            Token value (color or other string value)

        Example:
            >>> registry = ColorTokenRegistry()
            >>> # For a minimal dark theme with only 13 tokens
            >>> value = ColorTokenRegistry.get('button.background', dark_theme)
            >>> # Returns '#0e639c' (dark default) instead of hardcoded light blue

        """
        # 1. Check ThemeManager overrides FIRST (v2.0.0)
        # This allows runtime color customization without modifying themes
        try:
            from .manager import ThemeManager
            manager = ThemeManager.get_instance()
            override_color = manager.get_effective_color(token)
            if override_color:
                return override_color
        except Exception:
            # If ThemeManager not available or fails, continue with normal resolution
            pass

        # 2. Check if theme defines this token (simplified - no dual-format support)
        # Use direct dict access instead of get_property to avoid exception
        value = None
        if token in theme.colors:
            value = theme.colors[token]
        elif token in theme.styles:
            value = theme.styles[token]
        elif token in theme.metadata:
            value = theme.metadata[token]

        if value is not None:
            return value

        # 2. Use registry default based on theme type
        token_obj = cls.get_token(token)
        if token_obj:
            # Determine if theme is dark
            is_dark = cls._is_dark_theme(theme)
            return token_obj.default_dark if is_dark else token_obj.default_light

        # 3. Smart heuristic based on token name
        return cls._get_smart_default(token, theme)

    @classmethod
    def _is_dark_theme(cls, theme: "Theme") -> bool:
        """Determine if theme is dark based on type field or heuristic."""
        # First check explicit type field
        if hasattr(theme, "type"):
            return theme.type in ("dark", "high-contrast")

        # Fallback: Heuristic based on background color
        # If background is dark, it's a dark theme
        bg = theme.colors.get("colors.background", "#ffffff")
        if isinstance(bg, str) and bg.startswith("#"):
            # Parse hex color and check luminance
            hex_color = bg.lstrip("#")
            if len(hex_color) >= 6:
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                # Simple luminance calculation
                luminance = 0.299 * r + 0.587 * g + 0.114 * b
                return luminance < 128  # Dark if luminance < 128

        # Default to light if can't determine
        return False

    @classmethod
    def _get_smart_default(cls, token: str, theme: "Theme") -> str:
        """Smart heuristic for unknown tokens based on naming patterns."""
        is_dark = cls._is_dark_theme(theme)

        # Background tokens
        if "background" in token.lower() or token.endswith(".bg"):
            return "#1e1e1e" if is_dark else "#ffffff"

        # Foreground/text tokens
        if "foreground" in token.lower() or token.endswith(".fg") or "text" in token.lower():
            return "#d4d4d4" if is_dark else "#000000"

        # Border tokens
        if "border" in token.lower():
            return "#3c3c3c" if is_dark else "#cccccc"

        # Hover tokens - slightly lighter/darker
        if "hover" in token.lower():
            return "#2a2d2e" if is_dark else "#f0f0f0"

        # Selection tokens
        if "selection" in token.lower():
            return "#264f78" if is_dark else "#add6ff"

        # Active/focus tokens (accent color)
        if "active" in token.lower() or "focus" in token.lower():
            return "#007acc" if is_dark else "#0078d4"

        # Disabled tokens
        if "disabled" in token.lower():
            return "#555555" if is_dark else "#999999"

        # Error tokens
        if "error" in token.lower() or "danger" in token.lower():
            return "#f48771" if is_dark else "#dc3545"

        # Warning tokens
        if "warning" in token.lower():
            return "#cca700" if is_dark else "#ffc107"

        # Success tokens
        if "success" in token.lower():
            return "#28a745" if is_dark else "#28a745"

        # Default fallback - use base foreground/background
        if is_dark:
            return "#d4d4d4"  # Light text for dark themes
        else:
            return "#000000"  # Dark text for light themes
