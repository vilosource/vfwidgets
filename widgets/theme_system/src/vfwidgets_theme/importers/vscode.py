"""VSCode Theme Importer.

This module provides VSCode theme import capabilities including:
- VSCode theme JSON format parsing
- Color mapping from VSCode to Qt properties
- tokenColors handling for syntax highlighting
- Support for both dark and light themes
- Theme validation and error handling
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from ..core.theme import Theme
from ..errors import ThemeError
from ..logging import get_debug_logger

logger = get_debug_logger(__name__)


class VSCodeImportError(ThemeError):
    """Error during VSCode theme import."""

    pass


@dataclass
class VSCodeThemeInfo:
    """Information about a VSCode theme."""

    name: str
    type: str  # light, dark, or hc (high contrast)
    description: str
    author: str
    version: str


class VSCodeColorMapper:
    """Maps VSCode color keys to Qt theme properties."""

    # VSCode to Qt color mappings
    COLOR_MAP = {
        # Editor colors
        "editor.background": "window.background",
        "editor.foreground": "window.foreground",
        "editorCursor.foreground": "cursor.foreground",
        "editor.selectionBackground": "selection.background",
        "editor.selectionForeground": "selection.foreground",
        "editor.lineHighlightBackground": "line.highlight.background",
        # UI colors
        "foreground": "ui.foreground",
        "focusBorder": "ui.focus.border",
        "selection.background": "ui.selection.background",
        "descriptionForeground": "ui.description.foreground",
        "errorForeground": "ui.error.foreground",
        "textLink.foreground": "ui.link.foreground",
        "textLink.activeForeground": "ui.link.active.foreground",
        # Button colors
        "button.background": "button.background",
        "button.foreground": "button.foreground",
        "button.hoverBackground": "button.hover.background",
        "button.border": "button.border",
        # Input colors
        "input.background": "input.background",
        "input.foreground": "input.foreground",
        "input.border": "input.border",
        "input.placeholderForeground": "input.placeholder.foreground",
        "inputOption.activeBorder": "input.option.active.border",
        "inputValidation.errorBackground": "input.validation.error.background",
        "inputValidation.errorForeground": "input.validation.error.foreground",
        "inputValidation.errorBorder": "input.validation.error.border",
        # Dropdown colors
        "dropdown.background": "dropdown.background",
        "dropdown.foreground": "dropdown.foreground",
        "dropdown.border": "dropdown.border",
        # List colors
        "list.activeSelectionBackground": "list.selection.active.background",
        "list.activeSelectionForeground": "list.selection.active.foreground",
        "list.inactiveSelectionBackground": "list.selection.inactive.background",
        "list.inactiveSelectionForeground": "list.selection.inactive.foreground",
        "list.hoverBackground": "list.hover.background",
        "list.hoverForeground": "list.hover.foreground",
        # Activity bar
        "activityBar.background": "activitybar.background",
        "activityBar.foreground": "activitybar.foreground",
        "activityBar.border": "activitybar.border",
        "activityBarBadge.background": "activitybar.badge.background",
        "activityBarBadge.foreground": "activitybar.badge.foreground",
        # Side bar
        "sideBar.background": "sidebar.background",
        "sideBar.foreground": "sidebar.foreground",
        "sideBar.border": "sidebar.border",
        "sideBarTitle.foreground": "sidebar.title.foreground",
        "sideBarSectionHeader.background": "sidebar.section.header.background",
        "sideBarSectionHeader.foreground": "sidebar.section.header.foreground",
        # Editor group
        "editorGroup.border": "editor.group.border",
        "editorGroupHeader.tabsBackground": "editor.group.header.tabs.background",
        "editorGroupHeader.noTabsBackground": "editor.group.header.background",
        # Tab colors
        "tab.activeBackground": "tab.active.background",
        "tab.activeForeground": "tab.active.foreground",
        "tab.activeBorder": "tab.active.border",
        "tab.inactiveBackground": "tab.inactive.background",
        "tab.inactiveForeground": "tab.inactive.foreground",
        "tab.border": "tab.border",
        # Panel colors
        "panel.background": "panel.background",
        "panel.border": "panel.border",
        "panelTitle.activeBorder": "panel.title.active.border",
        "panelTitle.activeForeground": "panel.title.active.foreground",
        "panelTitle.inactiveForeground": "panel.title.inactive.foreground",
        # Status bar
        "statusBar.background": "statusbar.background",
        "statusBar.foreground": "statusbar.foreground",
        "statusBar.border": "statusbar.border",
        "statusBar.debuggingBackground": "statusbar.debugging.background",
        "statusBar.debuggingForeground": "statusbar.debugging.foreground",
        "statusBar.noFolderBackground": "statusbar.no.folder.background",
        # Title bar
        "titleBar.activeBackground": "titlebar.active.background",
        "titleBar.activeForeground": "titlebar.active.foreground",
        "titleBar.inactiveBackground": "titlebar.inactive.background",
        "titleBar.inactiveForeground": "titlebar.inactive.foreground",
        "titleBar.border": "titlebar.border",
        # Menu bar
        "menubar.selectionBackground": "menubar.selection.background",
        "menubar.selectionForeground": "menubar.selection.foreground",
        "menu.background": "menu.background",
        "menu.foreground": "menu.foreground",
        "menu.selectionBackground": "menu.selection.background",
        "menu.selectionForeground": "menu.selection.foreground",
        "menu.separatorBackground": "menu.separator.background",
        # Notification colors
        "notificationCenter.border": "notification.center.border",
        "notificationCenterHeader.foreground": "notification.center.header.foreground",
        "notificationCenterHeader.background": "notification.center.header.background",
        "notifications.foreground": "notification.foreground",
        "notifications.background": "notification.background",
        "notifications.border": "notification.border",
        "notificationLink.foreground": "notification.link.foreground",
        # Extensions
        "extensionButton.prominentBackground": "extension.button.prominent.background",
        "extensionButton.prominentForeground": "extension.button.prominent.foreground",
        "extensionButton.prominentHoverBackground": "extension.button.prominent.hover.background",
        # Git colors
        "gitDecoration.addedResourceForeground": "git.decoration.added.foreground",
        "gitDecoration.modifiedResourceForeground": "git.decoration.modified.foreground",
        "gitDecoration.deletedResourceForeground": "git.decoration.deleted.foreground",
        "gitDecoration.untrackedResourceForeground": "git.decoration.untracked.foreground",
        "gitDecoration.conflictingResourceForeground": "git.decoration.conflicting.foreground",
        # Terminal colors
        "terminal.background": "terminal.background",
        "terminal.foreground": "terminal.foreground",
        "terminal.ansiBlack": "terminal.ansi.black",
        "terminal.ansiBlue": "terminal.ansi.blue",
        "terminal.ansiBrightBlack": "terminal.ansi.bright.black",
        "terminal.ansiBrightBlue": "terminal.ansi.bright.blue",
        "terminal.ansiBrightCyan": "terminal.ansi.bright.cyan",
        "terminal.ansiBrightGreen": "terminal.ansi.bright.green",
        "terminal.ansiBrightMagenta": "terminal.ansi.bright.magenta",
        "terminal.ansiBrightRed": "terminal.ansi.bright.red",
        "terminal.ansiBrightWhite": "terminal.ansi.bright.white",
        "terminal.ansiBrightYellow": "terminal.ansi.bright.yellow",
        "terminal.ansiCyan": "terminal.ansi.cyan",
        "terminal.ansiGreen": "terminal.ansi.green",
        "terminal.ansiMagenta": "terminal.ansi.magenta",
        "terminal.ansiRed": "terminal.ansi.red",
        "terminal.ansiWhite": "terminal.ansi.white",
        "terminal.ansiYellow": "terminal.ansi.yellow",
    }

    # Fallback mappings for unknown VSCode colors
    FALLBACK_PATTERNS = {
        "background": "background",
        "foreground": "foreground",
        "border": "border",
        "shadow": "shadow",
        "selection": "selection",
        "hover": "hover",
        "active": "active",
        "inactive": "inactive",
    }

    def __init__(self, include_unmapped: bool = False):
        """Initialize color mapper.

        Args:
            include_unmapped: Whether to include unmapped colors with original keys

        """
        self.include_unmapped = include_unmapped
        self._unmapped_colors: set[str] = set()

    def map_colors(self, vscode_colors: dict[str, str]) -> dict[str, str]:
        """Map VSCode colors to Qt theme colors.

        Args:
            vscode_colors: Dictionary of VSCode color keys and values

        Returns:
            Dictionary of mapped Qt theme colors

        """
        mapped_colors = {}

        for vscode_key, color_value in vscode_colors.items():
            # Direct mapping
            if vscode_key in self.COLOR_MAP:
                qt_key = self.COLOR_MAP[vscode_key]
                mapped_colors[qt_key] = color_value
            elif self.include_unmapped:
                # Try fallback pattern matching
                qt_key = self._find_fallback_mapping(vscode_key)
                if qt_key:
                    mapped_colors[qt_key] = color_value
                else:
                    # Keep original key if no mapping found
                    mapped_colors[f"vscode.{vscode_key}"] = color_value
                    self._unmapped_colors.add(vscode_key)

        return mapped_colors

    def _find_fallback_mapping(self, vscode_key: str) -> Optional[str]:
        """Find fallback mapping for unmapped VSCode color key."""
        vscode_key_lower = vscode_key.lower()

        for pattern, _qt_suffix in self.FALLBACK_PATTERNS.items():
            if pattern in vscode_key_lower:
                # Convert camelCase to dot notation
                parts = []
                current_part = ""

                for char in vscode_key:
                    if char.isupper() and current_part:
                        parts.append(current_part.lower())
                        current_part = char.lower()
                    else:
                        current_part += char.lower()

                if current_part:
                    parts.append(current_part)

                return ".".join(parts)

        return None

    def get_unmapped_colors(self) -> set[str]:
        """Get set of colors that couldn't be mapped."""
        return self._unmapped_colors.copy()


class TokenColorMapper:
    """Maps VSCode tokenColors to theme token colors."""

    def __init__(self):
        """Initialize token color mapper."""
        pass

    def map_token_colors(self, token_colors: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Map VSCode tokenColors to theme format.

        Args:
            token_colors: List of VSCode token color objects

        Returns:
            List of theme token color objects

        """
        mapped_tokens = []

        for token in token_colors:
            if not isinstance(token, dict):
                continue

            # Extract required fields
            scope = token.get("scope")
            settings = token.get("settings", {})
            name = token.get("name", "")

            if not scope or not settings:
                continue

            # Normalize scope (can be string or list)
            if isinstance(scope, str):
                scopes = [scope.strip()]
            elif isinstance(scope, list):
                scopes = [s.strip() for s in scope if isinstance(s, str)]
            else:
                continue

            # Map settings
            mapped_settings = {}
            if "foreground" in settings:
                mapped_settings["foreground"] = settings["foreground"]
            if "background" in settings:
                mapped_settings["background"] = settings["background"]
            if "fontStyle" in settings:
                mapped_settings["fontStyle"] = settings["fontStyle"]

            # Create mapped token
            for scope_name in scopes:
                mapped_token = {"scope": scope_name, "settings": mapped_settings}

                if name:
                    mapped_token["name"] = name

                mapped_tokens.append(mapped_token)

        return mapped_tokens


class VSCodeImporter:
    """Import VSCode themes with intelligent mapping."""

    def __init__(self, include_unmapped_colors: bool = False, validate_imported: bool = True):
        """Initialize VSCode importer.

        Args:
            include_unmapped_colors: Whether to include colors that can't be mapped
            validate_imported: Whether to validate imported themes

        """
        self.color_mapper = VSCodeColorMapper(include_unmapped=include_unmapped_colors)
        self.token_mapper = TokenColorMapper()
        self.validate_imported = validate_imported

    def import_theme(self, vscode_path: Path) -> Theme:
        """Import VSCode theme from file.

        Args:
            vscode_path: Path to VSCode theme JSON file

        Returns:
            Imported Theme object

        Raises:
            VSCodeImportError: If import fails

        """
        try:
            # Load VSCode theme data
            vscode_data = self._load_vscode_file(vscode_path)

            # Extract theme info
            theme_info = self._extract_theme_info(vscode_data)

            # Import theme
            return self._import_from_data(vscode_data, theme_info)

        except Exception as e:
            raise VSCodeImportError(f"Failed to import VSCode theme from {vscode_path}: {e}") from e

    def import_from_data(
        self, vscode_data: dict[str, Any], theme_name: Optional[str] = None
    ) -> Theme:
        """Import VSCode theme from data dictionary.

        Args:
            vscode_data: VSCode theme data dictionary
            theme_name: Optional override for theme name

        Returns:
            Imported Theme object

        """
        try:
            # Extract theme info
            theme_info = self._extract_theme_info(vscode_data)

            # Override name if provided
            if theme_name:
                theme_info.name = theme_name

            return self._import_from_data(vscode_data, theme_info)

        except Exception as e:
            raise VSCodeImportError(f"Failed to import VSCode theme from data: {e}") from e

    def _load_vscode_file(self, file_path: Path) -> dict[str, Any]:
        """Load VSCode theme file."""
        if not file_path.exists():
            raise VSCodeImportError(f"VSCode theme file not found: {file_path}")

        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise VSCodeImportError(f"Invalid JSON in VSCode theme file: {e}") from e
        except Exception as e:
            raise VSCodeImportError(f"Failed to read VSCode theme file: {e}") from e

        if not isinstance(data, dict):
            raise VSCodeImportError("VSCode theme file must contain a JSON object")

        return data

    def _extract_theme_info(self, vscode_data: dict[str, Any]) -> VSCodeThemeInfo:
        """Extract theme information from VSCode data."""
        return VSCodeThemeInfo(
            name=vscode_data.get("name", "Imported VSCode Theme"),
            type=vscode_data.get("type", "dark").lower(),
            description=vscode_data.get("description", "Imported from VSCode theme"),
            author=vscode_data.get("author", "Unknown"),
            version=vscode_data.get("version", "1.0.0"),
        )

    def _import_from_data(self, vscode_data: dict[str, Any], theme_info: VSCodeThemeInfo) -> Theme:
        """Import theme from VSCode data and theme info."""
        logger.debug(f"Importing VSCode theme: {theme_info.name}")

        # Map colors
        vscode_colors = vscode_data.get("colors", {})
        mapped_colors = self.color_mapper.map_colors(vscode_colors)

        logger.debug(f"Mapped {len(mapped_colors)} colors from {len(vscode_colors)} VSCode colors")

        # Map token colors
        vscode_tokens = vscode_data.get("tokenColors", [])
        mapped_tokens = self.token_mapper.map_token_colors(vscode_tokens)

        logger.debug(
            f"Mapped {len(mapped_tokens)} token colors from {len(vscode_tokens)} VSCode tokens"
        )

        # Create metadata
        metadata = {
            "description": theme_info.description,
            "author": theme_info.author,
            "imported_from": "vscode",
            "original_type": vscode_data.get("type", "unknown"),
        }

        # Add unmapped color info if any
        unmapped_colors = self.color_mapper.get_unmapped_colors()
        if unmapped_colors:
            metadata["unmapped_colors"] = list(unmapped_colors)
            logger.debug(f"Unmapped colors: {len(unmapped_colors)} colors")

        # Determine theme type
        if theme_info.type in ("dark", "light"):
            theme_type = theme_info.type
        elif theme_info.type in ("hc", "high-contrast"):
            theme_type = "high-contrast"
        else:
            # Try to infer from background color
            bg_color = mapped_colors.get("window.background") or mapped_colors.get(
                "editor.background"
            )
            if bg_color:
                theme_type = self._infer_theme_type(bg_color)
            else:
                theme_type = "dark"  # Default fallback

        # Create Theme object
        theme = Theme(
            name=theme_info.name,
            version=theme_info.version,
            type=theme_type,
            colors=mapped_colors,
            styles={},  # VSCode themes don't typically have style properties
            metadata=metadata,
            token_colors=mapped_tokens,
        )

        logger.debug(f"Successfully imported VSCode theme: {theme.name} ({theme.type})")
        return theme

    def _infer_theme_type(self, background_color: str) -> str:
        """Infer theme type from background color."""
        if not background_color or not background_color.startswith("#"):
            return "dark"

        try:
            # Remove # and convert to RGB
            hex_color = background_color[1:]
            if len(hex_color) == 3:
                hex_color = "".join(c * 2 for c in hex_color)

            # Calculate luminance
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0

            # Simple luminance calculation
            luminance = 0.299 * r + 0.587 * g + 0.114 * b

            # Theme is light if luminance > 0.5
            return "light" if luminance > 0.5 else "dark"

        except (ValueError, IndexError):
            return "dark"

    def get_import_summary(self) -> dict[str, Any]:
        """Get summary of last import operation."""
        return {
            "mapped_colors": len(self.color_mapper.COLOR_MAP),
            "unmapped_colors": len(self.color_mapper.get_unmapped_colors()),
            "fallback_patterns": len(self.color_mapper.FALLBACK_PATTERNS),
        }
