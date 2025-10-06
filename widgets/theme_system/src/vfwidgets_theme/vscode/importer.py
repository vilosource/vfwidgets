"""VSCode theme importer for converting VSCode themes to our theme format.

This module handles the conversion of VSCode theme JSON files into our
internal theme representation, mapping colors and properties appropriately.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.theme import Theme, ThemeColors, ThemeProperties
from ..errors import ThemeSystemError
from ..logging import get_logger

logger = get_logger(__name__)


@dataclass
class VSCodeTokenColor:
    """Represents a VSCode token color definition."""

    name: Optional[str] = None
    scope: Optional[List[str]] = None
    settings: Optional[Dict[str, str]] = None


class VSCodeThemeImporter:
    """Imports VSCode themes and converts them to our theme format.

    Handles both color themes and token color mappings from VSCode
    theme JSON files.
    """

    # Mapping from VSCode color keys to our NAMESPACED theme properties
    COLOR_MAPPINGS = {
        # Editor colors - map to editor.* tokens
        "editor.background": "editor.background",
        "editor.foreground": "editor.foreground",
        "editor.selectionBackground": "editor.selectionBackground",
        "editor.selectionForeground": "editor.selectionForeground",
        "editor.lineHighlightBackground": "editor.lineHighlightBackground",
        "editor.findMatchBackground": "editor.findMatchBackground",
        "editor.findMatchHighlightBackground": "editor.findMatchHighlightBackground",
        # Activity Bar
        "activityBar.background": "activityBar.background",
        "activityBar.foreground": "activityBar.foreground",
        "activityBar.inactiveForeground": "activityBar.inactiveForeground",
        # Side Bar
        "sideBar.background": "sideBar.background",
        "sideBar.foreground": "sideBar.foreground",
        "sideBar.border": "sideBar.border",
        # Status Bar
        "statusBar.background": "statusBar.background",
        "statusBar.foreground": "statusBar.foreground",
        "statusBar.border": "statusBar.border",
        # Tab colors
        "tab.activeBackground": "tab.activeBackground",
        "tab.activeForeground": "tab.activeForeground",
        "tab.inactiveBackground": "tab.inactiveBackground",
        "tab.inactiveForeground": "tab.inactiveForeground",
        "tab.border": "tab.border",
        # Title Bar
        "titleBar.activeBackground": "titleBar.activeBackground",
        "titleBar.activeForeground": "titleBar.activeForeground",
        "titleBar.inactiveBackground": "titleBar.inactiveBackground",
        "titleBar.inactiveForeground": "titleBar.inactiveForeground",
        # Menu Bar
        "menubar.selectionBackground": "menubar.selectionBackground",
        "menubar.selectionForeground": "menubar.selectionForeground",
        # Input controls
        "input.background": "input.background",
        "input.foreground": "input.foreground",
        "input.border": "input.border",
        # Button controls
        "button.background": "button.background",
        "button.foreground": "button.foreground",
        "button.hoverBackground": "button.hoverBackground",
        # Dropdown controls
        "dropdown.background": "dropdown.background",
        "dropdown.foreground": "dropdown.foreground",
        "dropdown.border": "dropdown.border",
        # List/tree controls
        "list.activeSelectionBackground": "list.activeSelectionBackground",
        "list.activeSelectionForeground": "list.activeSelectionForeground",
        "list.hoverBackground": "list.hoverBackground",
        "list.hoverForeground": "list.hoverForeground",
        # Panel
        "panel.background": "panel.background",
        "panel.border": "panel.border",
        # Terminal
        "terminal.background": "terminal.background",
        "terminal.foreground": "terminal.foreground",
        # Scrollbar
        "scrollbar.shadow": "scrollbar.shadow",
        "scrollbarSlider.background": "scrollbarSlider.background",
        "scrollbarSlider.hoverBackground": "scrollbarSlider.hoverBackground",
        "scrollbarSlider.activeBackground": "scrollbarSlider.activeBackground",
        # Border colors - map to colors.*
        "focusBorder": "colors.focus",
        "contrastBorder": "colors.border",
        "contrastActiveBorder": "colors.border",
        # Text colors - map to colors.*
        "foreground": "colors.foreground",
        "descriptionForeground": "colors.text_secondary",
        "errorForeground": "colors.error",
        # Badge
        "badge.background": "badge.background",
        "badge.foreground": "badge.foreground",
        # Progress bar
        "progressBar.background": "progressBar.background",
        # Editor widget
        "editorWidget.background": "editorWidget.background",
        "editorWidget.border": "editorWidget.border",
        # Peek view
        "peekView.border": "peekView.border",
        "peekViewEditor.background": "peekViewEditor.background",
        "peekViewResult.background": "peekViewResult.background",
        # Git decoration
        "gitDecoration.modifiedResourceForeground": "gitDecoration.modifiedResourceForeground",
        "gitDecoration.deletedResourceForeground": "gitDecoration.deletedResourceForeground",
        "gitDecoration.untrackedResourceForeground": "gitDecoration.untrackedResourceForeground",
        "gitDecoration.addedResourceForeground": "gitDecoration.addedResourceForeground",
        # Notification
        "notificationCenter.border": "notificationCenter.border",
        "notificationCenterHeader.background": "notificationCenterHeader.background",
        "notifications.background": "notifications.background",
        "notifications.foreground": "notifications.foreground",
    }

    def __init__(self):
        """Initialize the VSCode theme importer."""
        pass

    def import_from_file(self, theme_path: Path) -> Theme:
        """Import theme from VSCode theme file.

        Args:
            theme_path: Path to VSCode theme JSON file

        Returns:
            Imported theme

        Raises:
            ThemeSystemError: If theme file cannot be loaded

        """
        logger.info(f"Importing VSCode theme from: {theme_path}")

        if not theme_path.exists():
            raise ThemeSystemError(f"Theme file does not exist: {theme_path}")

        try:
            with open(theme_path, encoding="utf-8") as f:
                theme_data = json.load(f)

            theme_name = theme_path.stem
            return self.import_theme(theme_data, theme_name)

        except json.JSONDecodeError as e:
            raise ThemeSystemError(f"Invalid JSON in theme file {theme_path}: {e}")
        except Exception as e:
            raise ThemeSystemError(f"Error importing theme from {theme_path}: {e}")

    def import_theme(self, theme_data: Dict[str, Any], theme_name: str) -> Theme:
        """Import theme from VSCode theme data.

        Args:
            theme_data: VSCode theme JSON data
            theme_name: Name for the imported theme

        Returns:
            Imported theme

        """
        logger.info(f"Converting VSCode theme: {theme_name}")

        # Extract basic theme info
        theme_type = self._determine_theme_type(theme_data)
        colors = self._extract_colors(theme_data)
        token_colors = self._extract_token_colors(theme_data)

        # Create our theme
        theme = Theme(
            name=theme_name,
            type=theme_type,
            description=f"Imported from VSCode theme: {theme_name}",
            colors=colors,
            properties=ThemeProperties(
                font_family="Consolas, 'Courier New', monospace",
                font_size=14,
                line_height=1.4,
                border_radius=3,
                animation_duration=200,
            ),
        )

        # Add token colors as metadata
        if token_colors:
            theme.metadata = theme.metadata or {}
            theme.metadata["vscode_token_colors"] = token_colors

        logger.info(f"Successfully converted VSCode theme: {theme_name}")
        return theme

    def _determine_theme_type(self, theme_data: Dict[str, Any]) -> str:
        """Determine if theme is light or dark."""
        # Check explicit type
        theme_type = theme_data.get("type")
        if theme_type in ["light", "dark"]:
            return theme_type

        # Try to infer from colors
        colors = theme_data.get("colors", {})
        background = colors.get("editor.background", "#ffffff")

        # Simple heuristic: check if background is dark
        if background.startswith("#"):
            # Convert hex to brightness
            hex_color = background[1:]
            if len(hex_color) == 6:
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                brightness = (r * 299 + g * 587 + b * 114) / 1000
                return "dark" if brightness < 128 else "light"

        # Default to dark
        return "dark"

    def _extract_colors(self, theme_data: Dict[str, Any]) -> ThemeColors:
        """Extract and map colors from VSCode theme."""
        vscode_colors = theme_data.get("colors", {})
        mapped_colors = {}

        # Map known colors
        for vscode_key, our_key in self.COLOR_MAPPINGS.items():
            if vscode_key in vscode_colors:
                color_value = vscode_colors[vscode_key]
                mapped_colors[our_key] = self._normalize_color(color_value)

        # Add fallbacks for essential colors
        self._add_color_fallbacks(mapped_colors, vscode_colors)

        return ThemeColors(**mapped_colors)

    def _normalize_color(self, color: str) -> str:
        """Normalize color value to consistent format."""
        if not isinstance(color, str):
            return "#000000"

        color = color.strip()

        # Handle hex colors
        if color.startswith("#"):
            return color

        # Handle rgba/rgb colors - convert to hex
        if color.startswith("rgba(") or color.startswith("rgb("):
            return self._rgb_to_hex(color)

        # Handle named colors (limited support)
        named_colors = {
            "white": "#ffffff",
            "black": "#000000",
            "red": "#ff0000",
            "green": "#008000",
            "blue": "#0000ff",
            "transparent": "#00000000",
        }
        return named_colors.get(color.lower(), color)

    def _rgb_to_hex(self, rgb_color: str) -> str:
        """Convert RGB/RGBA color to hex format."""
        try:
            # Extract numbers from rgb(a) string
            import re

            numbers = re.findall(r"\d+(?:\.\d+)?", rgb_color)

            if len(numbers) >= 3:
                r = int(float(numbers[0]))
                g = int(float(numbers[1]))
                b = int(float(numbers[2]))

                # Handle alpha channel if present
                if len(numbers) >= 4:
                    a = int(float(numbers[3]) * 255)
                    return f"#{r:02x}{g:02x}{b:02x}{a:02x}"
                else:
                    return f"#{r:02x}{g:02x}{b:02x}"

        except (ValueError, IndexError):
            pass

        return "#000000"

    def _add_color_fallbacks(self, mapped_colors: Dict[str, str], vscode_colors: Dict[str, str]):
        """Add fallback colors for essential properties with namespaced keys."""
        # Ensure we have basic colors (using namespaced keys)
        if "colors.background" not in mapped_colors and "editor.background" not in mapped_colors:
            mapped_colors["colors.background"] = vscode_colors.get("editor.background", "#1e1e1e")

        if "colors.foreground" not in mapped_colors and "editor.foreground" not in mapped_colors:
            mapped_colors["colors.foreground"] = vscode_colors.get("editor.foreground", "#d4d4d4")

        # Generate complementary colors if missing
        bg = mapped_colors.get("editor.background") or mapped_colors.get(
            "colors.background", "#1e1e1e"
        )

        if "sideBar.background" not in mapped_colors:
            mapped_colors["sideBar.background"] = self._darken_color(bg, 0.1)

        if "statusBar.background" not in mapped_colors:
            mapped_colors["statusBar.background"] = self._darken_color(bg, 0.2)

    def _darken_color(self, color: str, factor: float) -> str:
        """Darken a color by the given factor."""
        if not color.startswith("#"):
            return color

        try:
            # Parse hex color
            hex_color = color[1:]
            if len(hex_color) == 6:
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)

                # Darken
                r = max(0, int(r * (1 - factor)))
                g = max(0, int(g * (1 - factor)))
                b = max(0, int(b * (1 - factor)))

                return f"#{r:02x}{g:02x}{b:02x}"

        except (ValueError, IndexError):
            pass

        return color

    def _extract_token_colors(self, theme_data: Dict[str, Any]) -> List[VSCodeTokenColor]:
        """Extract token color rules from theme."""
        token_colors = []
        token_color_data = theme_data.get("tokenColors", [])

        for token_data in token_color_data:
            if isinstance(token_data, dict):
                token_color = VSCodeTokenColor(
                    name=token_data.get("name"),
                    scope=self._normalize_scope(token_data.get("scope")),
                    settings=token_data.get("settings", {}),
                )
                token_colors.append(token_color)

        return token_colors

    def _normalize_scope(self, scope) -> Optional[List[str]]:
        """Normalize token scope to list format."""
        if not scope:
            return None

        if isinstance(scope, str):
            # Split comma-separated scopes
            return [s.strip() for s in scope.split(",") if s.strip()]
        elif isinstance(scope, list):
            return [str(s).strip() for s in scope if str(s).strip()]

        return None

    def export_to_vscode(self, theme: Theme, output_path: Path) -> None:
        """Export our theme to VSCode format.

        Args:
            theme: Theme to export
            output_path: Output file path

        Raises:
            ThemeSystemError: If export fails

        """
        logger.info(f"Exporting theme to VSCode format: {output_path}")

        try:
            vscode_theme = self._convert_to_vscode_format(theme)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(vscode_theme, f, indent=2, ensure_ascii=False)

            logger.info(f"Successfully exported theme to: {output_path}")

        except Exception as e:
            raise ThemeSystemError(f"Error exporting theme to VSCode format: {e}")

    def _convert_to_vscode_format(self, theme: Theme) -> Dict[str, Any]:
        """Convert our theme to VSCode format."""
        vscode_theme = {"name": theme.name, "type": theme.type, "colors": {}, "tokenColors": []}

        # Reverse map our colors to VSCode format
        reverse_mappings = {v: k for k, v in self.COLOR_MAPPINGS.items()}

        for attr_name in dir(theme.colors):
            if not attr_name.startswith("_"):
                color_value = getattr(theme.colors, attr_name)
                if color_value and attr_name in reverse_mappings:
                    vscode_key = reverse_mappings[attr_name]
                    vscode_theme["colors"][vscode_key] = color_value

        # Add token colors if available
        if theme.metadata and "vscode_token_colors" in theme.metadata:
            token_colors = theme.metadata["vscode_token_colors"]
            for token_color in token_colors:
                if isinstance(token_color, VSCodeTokenColor):
                    token_data = {}
                    if token_color.name:
                        token_data["name"] = token_color.name
                    if token_color.scope:
                        token_data["scope"] = token_color.scope
                    if token_color.settings:
                        token_data["settings"] = token_color.settings
                    vscode_theme["tokenColors"].append(token_data)

        return vscode_theme
