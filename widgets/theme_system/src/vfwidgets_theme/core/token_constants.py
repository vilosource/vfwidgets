"""Token constants for IDE autocomplete support.

This module provides all theme tokens as Python constants for better IDE
autocomplete support and type safety. Instead of magic strings, developers
can use constants with full IDE support.

Usage:
    from vfwidgets_theme import Tokens

    # Before (magic strings):
    theme_config = {
        'bg': 'window.background',  # No autocomplete, typos possible
        'fg': 'window.foreground'
    }

    # After (with constants):
    theme_config = {
        'bg': Tokens.WINDOW_BACKGROUND,  # IDE autocomplete! Typo-safe!
        'fg': Tokens.WINDOW_FOREGROUND
    }

All token constants are generated from ColorTokenRegistry to ensure
they stay in sync with the theme system.
"""

from typing import Optional

from .tokens import ColorTokenRegistry


class Tokens:
    """All theme tokens as constants for IDE autocomplete.

    This class provides all 200+ theme tokens as Python constants following
    UPPER_SNAKE_CASE naming convention. The constants are strings that can
    be used anywhere the theme system expects a token name.

    Token categories:
    - Base Colors: COLORS_*
    - Buttons: BUTTON_*
    - Inputs: INPUT_*, DROPDOWN_*, COMBOBOX_*
    - Lists/Trees: LIST_*, TREE_*, TABLE_*
    - Editor: EDITOR_*
    - Sidebar: SIDEBAR_*
    - Panel: PANEL_*
    - Tabs: TAB_*
    - Activity Bar: ACTIVITYBAR_*
    - Status Bar: STATUSBAR_*
    - Title Bar: TITLEBAR_*
    - Menu: MENU_*, MENUBAR_*
    - Scrollbar: SCROLLBAR_*
    - Terminal: TERMINAL_*
    - Miscellaneous: BADGE_*, NOTIFICATIONS_*, PROGRESSBAR_*, SPLITTER_*

    Example:
        from vfwidgets_theme import Tokens

        class MyWidget(ThemedWidget, QWidget):
            theme_config = {
                'bg': Tokens.WINDOW_BACKGROUND,
                'fg': Tokens.WINDOW_FOREGROUND,
                'border': Tokens.COLORS_FOCUS_BORDER
            }

    """

    # ============================================================================
    # BASE COLORS (11 tokens)
    # ============================================================================
    COLORS_FOREGROUND = "colors.foreground"
    COLORS_BACKGROUND = "colors.background"
    COLORS_FOCUS_BORDER = "colors.focusBorder"
    COLORS_CONTRAST_BORDER = "colors.contrastBorder"
    COLORS_ERROR_FOREGROUND = "colors.errorForeground"
    COLORS_WARNING_FOREGROUND = "colors.warningForeground"
    COLORS_DISABLED_FOREGROUND = "colors.disabledForeground"
    COLORS_DESCRIPTION_FOREGROUND = "colors.descriptionForeground"
    COLORS_ICON_FOREGROUND = "colors.iconForeground"
    COLORS_PRIMARY = "colors.primary"
    COLORS_SECONDARY = "colors.secondary"

    # ============================================================================
    # BUTTON COLORS (18 tokens)
    # ============================================================================
    BUTTON_BACKGROUND = "button.background"
    BUTTON_FOREGROUND = "button.foreground"
    BUTTON_BORDER = "button.border"
    BUTTON_HOVER_BACKGROUND = "button.hoverBackground"
    BUTTON_HOVER_FOREGROUND = "button.hoverForeground"
    BUTTON_PRESSED_BACKGROUND = "button.pressedBackground"
    BUTTON_DISABLED_BACKGROUND = "button.disabledBackground"
    BUTTON_DISABLED_FOREGROUND = "button.disabledForeground"
    BUTTON_SECONDARY_BACKGROUND = "button.secondary.background"
    BUTTON_SECONDARY_FOREGROUND = "button.secondary.foreground"
    BUTTON_SECONDARY_HOVER_BACKGROUND = "button.secondary.hoverBackground"
    BUTTON_DANGER_BACKGROUND = "button.danger.background"
    BUTTON_DANGER_HOVER_BACKGROUND = "button.danger.hoverBackground"
    BUTTON_SUCCESS_BACKGROUND = "button.success.background"
    BUTTON_SUCCESS_HOVER_BACKGROUND = "button.success.hoverBackground"
    BUTTON_WARNING_BACKGROUND = "button.warning.background"
    BUTTON_WARNING_FOREGROUND = "button.warning.foreground"
    BUTTON_WARNING_HOVER_BACKGROUND = "button.warning.hoverBackground"

    # ============================================================================
    # INPUT/DROPDOWN COLORS (18 tokens)
    # ============================================================================
    INPUT_BACKGROUND = "input.background"
    INPUT_FOREGROUND = "input.foreground"
    INPUT_BORDER = "input.border"
    INPUT_PLACEHOLDER_FOREGROUND = "input.placeholderForeground"
    INPUT_FOCUS_BORDER = "input.focusBorder"
    INPUT_FOCUS_BACKGROUND = "input.focusBackground"
    INPUT_DISABLED_BACKGROUND = "input.disabledBackground"
    INPUT_DISABLED_FOREGROUND = "input.disabledForeground"
    INPUT_ERROR_BORDER = "input.errorBorder"
    DROPDOWN_BACKGROUND = "dropdown.background"
    DROPDOWN_FOREGROUND = "dropdown.foreground"
    DROPDOWN_BORDER = "dropdown.border"
    DROPDOWN_LIST_BACKGROUND = "dropdown.listBackground"
    DROPDOWN_LIST_FOREGROUND = "dropdown.listForeground"
    COMBOBOX_BACKGROUND = "combobox.background"
    COMBOBOX_FOREGROUND = "combobox.foreground"
    COMBOBOX_BORDER = "combobox.border"
    COMBOBOX_ARROW_FOREGROUND = "combobox.arrowForeground"

    # ============================================================================
    # LIST/TREE COLORS (20 tokens)
    # ============================================================================
    LIST_BACKGROUND = "list.background"
    LIST_FOREGROUND = "list.foreground"
    LIST_ACTIVE_SELECTION_BACKGROUND = "list.activeSelectionBackground"
    LIST_ACTIVE_SELECTION_FOREGROUND = "list.activeSelectionForeground"
    LIST_INACTIVE_SELECTION_BACKGROUND = "list.inactiveSelectionBackground"
    LIST_INACTIVE_SELECTION_FOREGROUND = "list.inactiveSelectionForeground"
    LIST_HOVER_BACKGROUND = "list.hoverBackground"
    LIST_HOVER_FOREGROUND = "list.hoverForeground"
    LIST_FOCUS_BACKGROUND = "list.focusBackground"
    LIST_FOCUS_FOREGROUND = "list.focusForeground"
    LIST_FOCUS_OUTLINE = "list.focusOutline"
    LIST_HIGHLIGHT_FOREGROUND = "list.highlightForeground"
    LIST_INVALID_ITEM_FOREGROUND = "list.invalidItemForeground"
    LIST_ERROR_FOREGROUND = "list.errorForeground"
    LIST_WARNING_FOREGROUND = "list.warningForeground"
    TREE_INDENT_GUIDES_STROKE = "tree.indentGuidesStroke"
    TABLE_GRID_COLOR = "table.gridColor"
    TABLE_HEADER_BACKGROUND = "table.headerBackground"
    TABLE_HEADER_FOREGROUND = "table.headerForeground"
    LIST_DROP_BACKGROUND = "list.dropBackground"

    # ============================================================================
    # EDITOR COLORS (35 tokens)
    # ============================================================================
    EDITOR_BACKGROUND = "editor.background"
    EDITOR_FOREGROUND = "editor.foreground"
    EDITOR_SELECTION_BACKGROUND = "editor.selectionBackground"
    EDITOR_SELECTION_FOREGROUND = "editor.selectionForeground"
    EDITOR_INACTIVE_SELECTION_BACKGROUND = "editor.inactiveSelectionBackground"
    EDITOR_LINE_HIGHLIGHT_BACKGROUND = "editor.lineHighlightBackground"
    EDITOR_LINE_HIGHLIGHT_BORDER = "editor.lineHighlightBorder"
    EDITOR_CURSOR_FOREGROUND = "editor.cursorForeground"
    EDITOR_LINE_NUMBER_FOREGROUND = "editorLineNumber.foreground"
    EDITOR_LINE_NUMBER_ACTIVE_FOREGROUND = "editorLineNumber.activeForeground"
    EDITOR_INDENT_GUIDE_BACKGROUND = "editorIndentGuide.background"
    EDITOR_INDENT_GUIDE_ACTIVE_BACKGROUND = "editorIndentGuide.activeBackground"
    EDITOR_WHITESPACE_FOREGROUND = "editorWhitespace.foreground"
    EDITOR_BRACKET_MATCH_BACKGROUND = "editorBracketMatch.background"
    EDITOR_BRACKET_MATCH_BORDER = "editorBracketMatch.border"
    EDITOR_WIDGET_BACKGROUND = "editorWidget.background"
    EDITOR_WIDGET_BORDER = "editorWidget.border"
    EDITOR_WIDGET_FOREGROUND = "editorWidget.foreground"
    EDITOR_SUGGEST_WIDGET_BACKGROUND = "editorSuggestWidget.background"
    EDITOR_SUGGEST_WIDGET_BORDER = "editorSuggestWidget.border"
    EDITOR_SUGGEST_WIDGET_FOREGROUND = "editorSuggestWidget.foreground"
    EDITOR_SUGGEST_WIDGET_SELECTED_BACKGROUND = "editorSuggestWidget.selectedBackground"
    EDITOR_SUGGEST_WIDGET_HIGHLIGHT_FOREGROUND = "editorSuggestWidget.highlightForeground"
    EDITOR_HOVER_WIDGET_BACKGROUND = "editorHoverWidget.background"
    EDITOR_HOVER_WIDGET_BORDER = "editorHoverWidget.border"
    EDITOR_HOVER_WIDGET_FOREGROUND = "editorHoverWidget.foreground"
    EDITOR_GUTTER_BACKGROUND = "editorGutter.background"
    EDITOR_GUTTER_ADDED_BACKGROUND = "editorGutter.addedBackground"
    EDITOR_GUTTER_DELETED_BACKGROUND = "editorGutter.deletedBackground"
    EDITOR_GUTTER_MODIFIED_BACKGROUND = "editorGutter.modifiedBackground"
    EDITOR_RULER_FOREGROUND = "editorRuler.foreground"
    EDITOR_FIND_MATCH_BACKGROUND = "editor.findMatchBackground"
    EDITOR_FIND_MATCH_HIGHLIGHT_BACKGROUND = "editor.findMatchHighlightBackground"

    # ============================================================================
    # SIDEBAR COLORS (7 tokens)
    # ============================================================================
    SIDEBAR_BACKGROUND = "sideBar.background"
    SIDEBAR_FOREGROUND = "sideBar.foreground"
    SIDEBAR_BORDER = "sideBar.border"
    SIDEBAR_TITLE_FOREGROUND = "sideBarTitle.foreground"
    SIDEBAR_SECTION_HEADER_BACKGROUND = "sideBarSectionHeader.background"
    SIDEBAR_SECTION_HEADER_FOREGROUND = "sideBarSectionHeader.foreground"
    SIDEBAR_SECTION_HEADER_BORDER = "sideBarSectionHeader.border"

    # ============================================================================
    # PANEL COLORS (8 tokens)
    # ============================================================================
    PANEL_BACKGROUND = "panel.background"
    PANEL_FOREGROUND = "panel.foreground"
    PANEL_BORDER = "panel.border"
    PANEL_TITLE_ACTIVE_FOREGROUND = "panelTitle.activeForeground"
    PANEL_TITLE_ACTIVE_BORDER = "panelTitle.activeBorder"
    PANEL_TITLE_INACTIVE_FOREGROUND = "panelTitle.inactiveForeground"
    PANEL_SECTION_BORDER = "panelSection.border"
    PANEL_SECTION_DROP_BACKGROUND = "panelSection.dropBackground"

    # ============================================================================
    # TAB COLORS (17 tokens)
    # ============================================================================
    TAB_ACTIVE_BACKGROUND = "tab.activeBackground"
    TAB_ACTIVE_FOREGROUND = "tab.activeForeground"
    TAB_ACTIVE_BORDER = "tab.activeBorder"
    TAB_ACTIVE_BORDER_TOP = "tab.activeBorderTop"
    TAB_INACTIVE_BACKGROUND = "tab.inactiveBackground"
    TAB_INACTIVE_FOREGROUND = "tab.inactiveForeground"
    TAB_HOVER_BACKGROUND = "tab.hoverBackground"
    TAB_HOVER_FOREGROUND = "tab.hoverForeground"
    TAB_HOVER_BORDER = "tab.hoverBorder"
    TAB_UNFOCUSED_ACTIVE_BACKGROUND = "tab.unfocusedActiveBackground"
    TAB_UNFOCUSED_ACTIVE_FOREGROUND = "tab.unfocusedActiveForeground"
    TAB_UNFOCUSED_INACTIVE_BACKGROUND = "tab.unfocusedInactiveBackground"
    TAB_UNFOCUSED_INACTIVE_FOREGROUND = "tab.unfocusedInactiveForeground"
    TAB_BORDER = "tab.border"
    TAB_BAR_BACKGROUND = "tabBar.background"
    TAB_BAR_BORDER = "tabBar.border"
    TAB_MODIFIED_BORDER = "tab.modifiedBorder"

    # ============================================================================
    # ACTIVITY BAR COLORS (8 tokens)
    # ============================================================================
    ACTIVITYBAR_BACKGROUND = "activityBar.background"
    ACTIVITYBAR_FOREGROUND = "activityBar.foreground"
    ACTIVITYBAR_INACTIVE_FOREGROUND = "activityBar.inactiveForeground"
    ACTIVITYBAR_BORDER = "activityBar.border"
    ACTIVITYBAR_ACTIVE_BORDER = "activityBar.activeBorder"
    ACTIVITYBAR_ACTIVE_BACKGROUND = "activityBar.activeBackground"
    ACTIVITYBAR_BADGE_BACKGROUND = "activityBarBadge.background"
    ACTIVITYBAR_BADGE_FOREGROUND = "activityBarBadge.foreground"

    # ============================================================================
    # STATUS BAR COLORS (11 tokens)
    # ============================================================================
    STATUSBAR_BACKGROUND = "statusBar.background"
    STATUSBAR_FOREGROUND = "statusBar.foreground"
    STATUSBAR_BORDER = "statusBar.border"
    STATUSBAR_DEBUGGING_BACKGROUND = "statusBar.debuggingBackground"
    STATUSBAR_DEBUGGING_FOREGROUND = "statusBar.debuggingForeground"
    STATUSBAR_NO_FOLDER_BACKGROUND = "statusBar.noFolderBackground"
    STATUSBAR_NO_FOLDER_FOREGROUND = "statusBar.noFolderForeground"
    STATUSBAR_ITEM_ACTIVE_BACKGROUND = "statusBarItem.activeBackground"
    STATUSBAR_ITEM_HOVER_BACKGROUND = "statusBarItem.hoverBackground"
    STATUSBAR_ITEM_PROMINENT_BACKGROUND = "statusBarItem.prominentBackground"
    STATUSBAR_ITEM_PROMINENT_HOVER_BACKGROUND = "statusBarItem.prominentHoverBackground"

    # ============================================================================
    # TITLE BAR COLORS (5 tokens)
    # ============================================================================
    TITLEBAR_ACTIVE_BACKGROUND = "titleBar.activeBackground"
    TITLEBAR_ACTIVE_FOREGROUND = "titleBar.activeForeground"
    TITLEBAR_INACTIVE_BACKGROUND = "titleBar.inactiveBackground"
    TITLEBAR_INACTIVE_FOREGROUND = "titleBar.inactiveForeground"
    TITLEBAR_BORDER = "titleBar.border"

    # ============================================================================
    # MENU COLORS (11 tokens)
    # ============================================================================
    MENU_BACKGROUND = "menu.background"
    MENU_FOREGROUND = "menu.foreground"
    MENU_BORDER = "menu.border"
    MENU_SELECTION_BACKGROUND = "menu.selectionBackground"
    MENU_SELECTION_FOREGROUND = "menu.selectionForeground"
    MENU_SEPARATOR_BACKGROUND = "menu.separatorBackground"
    MENUBAR_BACKGROUND = "menubar.background"
    MENUBAR_FOREGROUND = "menubar.foreground"
    MENUBAR_SELECTION_BACKGROUND = "menubar.selectionBackground"
    MENUBAR_SELECTION_FOREGROUND = "menubar.selectionForeground"
    MENUBAR_SELECTION_BORDER = "menubar.selectionBorder"

    # ============================================================================
    # SCROLLBAR COLORS (4 tokens)
    # ============================================================================
    SCROLLBAR_SHADOW = "scrollbar.shadow"
    SCROLLBAR_SLIDER_BACKGROUND = "scrollbarSlider.background"
    SCROLLBAR_SLIDER_HOVER_BACKGROUND = "scrollbarSlider.hoverBackground"
    SCROLLBAR_SLIDER_ACTIVE_BACKGROUND = "scrollbarSlider.activeBackground"

    # ============================================================================
    # MISCELLANEOUS COLORS (8 tokens)
    # ============================================================================
    BADGE_BACKGROUND = "badge.background"
    BADGE_FOREGROUND = "badge.foreground"
    NOTIFICATION_CENTER_BORDER = "notificationCenter.border"
    NOTIFICATIONS_BACKGROUND = "notifications.background"
    NOTIFICATIONS_FOREGROUND = "notifications.foreground"
    NOTIFICATIONS_BORDER = "notifications.border"
    PROGRESSBAR_BACKGROUND = "progressBar.background"
    SPLITTER_BACKGROUND = "splitter.background"

    # ============================================================================
    # TERMINAL COLORS (18 tokens)
    # ============================================================================
    TERMINAL_BACKGROUND = "terminal.background"
    TERMINAL_FOREGROUND = "terminal.foreground"
    TERMINAL_CURSOR_FOREGROUND = "terminalCursor.foreground"
    TERMINAL_CURSOR_BACKGROUND = "terminalCursor.background"
    TERMINAL_SELECTION_BACKGROUND = "terminal.selectionBackground"
    TERMINAL_ANSI_BLACK = "terminal.ansiBlack"
    TERMINAL_ANSI_RED = "terminal.ansiRed"
    TERMINAL_ANSI_GREEN = "terminal.ansiGreen"
    TERMINAL_ANSI_YELLOW = "terminal.ansiYellow"
    TERMINAL_ANSI_BLUE = "terminal.ansiBlue"
    TERMINAL_ANSI_MAGENTA = "terminal.ansiMagenta"
    TERMINAL_ANSI_CYAN = "terminal.ansiCyan"
    TERMINAL_ANSI_WHITE = "terminal.ansiWhite"
    TERMINAL_ANSI_BRIGHT_BLACK = "terminal.ansiBrightBlack"
    TERMINAL_ANSI_BRIGHT_RED = "terminal.ansiBrightRed"
    TERMINAL_ANSI_BRIGHT_GREEN = "terminal.ansiBrightGreen"
    TERMINAL_ANSI_BRIGHT_YELLOW = "terminal.ansiBrightYellow"
    TERMINAL_ANSI_BRIGHT_BLUE = "terminal.ansiBrightBlue"
    TERMINAL_ANSI_BRIGHT_MAGENTA = "terminal.ansiBrightMagenta"
    TERMINAL_ANSI_BRIGHT_CYAN = "terminal.ansiBrightCyan"
    TERMINAL_ANSI_BRIGHT_WHITE = "terminal.ansiBrightWhite"

    # ============================================================================
    # CLASS METHODS
    # ============================================================================

    def __setattr__(self, name: str, value: any) -> None:
        """Prevent modification of token constants."""
        raise AttributeError(f"Token constants are immutable. Cannot set {name}.")

    _all_tokens_cache: Optional[list[str]] = None

    @classmethod
    def all_tokens(cls) -> list[str]:
        """Get list of all token constant values.

        Returns a cached list of all token strings defined in this class.
        This matches exactly with ColorTokenRegistry.get_all_token_names().

        Returns:
            List of all token strings (e.g., ['colors.foreground', 'button.background', ...])

        Example:
            >>> tokens = Tokens.all_tokens()
            >>> print(len(tokens))
            200
            >>> 'colors.foreground' in tokens
            True

        """
        if cls._all_tokens_cache is None:
            # Get all class attributes that are uppercase constants
            cls._all_tokens_cache = [
                value
                for name, value in cls.__dict__.items()
                if not name.startswith("_")  # Skip private
                and name.isupper()  # Only UPPER_SNAKE_CASE
                and isinstance(value, str)  # Only strings
            ]
        return cls._all_tokens_cache

    @classmethod
    def validate(cls, token: Optional[str]) -> bool:
        """Check if a token string is valid.

        Args:
            token: Token string to validate (e.g., 'colors.foreground')

        Returns:
            True if token exists in ColorTokenRegistry, False otherwise

        Example:
            >>> Tokens.validate('colors.foreground')
            True
            >>> Tokens.validate('invalid.token')
            False
            >>> Tokens.validate(None)
            False

        """
        # Handle edge cases
        if token is None or not isinstance(token, str):
            return False

        # Check against registry
        return ColorTokenRegistry.get_token(token) is not None
