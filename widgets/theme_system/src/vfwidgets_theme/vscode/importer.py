"""
VSCode theme importer for converting VSCode themes to our theme format.

This module handles the conversion of VSCode theme JSON files into our
internal theme representation, mapping colors and properties appropriately.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

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
    """
    Imports VSCode themes and converts them to our theme format.

    Handles both color themes and token color mappings from VSCode
    theme JSON files.
    """

    # Mapping from VSCode color keys to our theme properties
    COLOR_MAPPINGS = {
        # Editor colors
        'editor.background': 'background',
        'editor.foreground': 'text',
        'editor.selectionBackground': 'selection_background',
        'editor.selectionForeground': 'selection_text',
        'editor.lineHighlightBackground': 'line_highlight',
        'editor.findMatchBackground': 'find_match_background',
        'editor.findMatchHighlightBackground': 'find_highlight_background',

        # Activity Bar
        'activityBar.background': 'sidebar_background',
        'activityBar.foreground': 'sidebar_text',
        'activityBar.inactiveForeground': 'sidebar_text_inactive',

        # Side Bar
        'sideBar.background': 'sidebar_background',
        'sideBar.foreground': 'sidebar_text',
        'sideBar.border': 'sidebar_border',

        # Status Bar
        'statusBar.background': 'statusbar_background',
        'statusBar.foreground': 'statusbar_text',
        'statusBar.border': 'statusbar_border',

        # Tab colors
        'tab.activeBackground': 'tab_active_background',
        'tab.activeForeground': 'tab_active_text',
        'tab.inactiveBackground': 'tab_inactive_background',
        'tab.inactiveForeground': 'tab_inactive_text',
        'tab.border': 'tab_border',

        # Title Bar
        'titleBar.activeBackground': 'titlebar_background',
        'titleBar.activeForeground': 'titlebar_text',
        'titleBar.inactiveBackground': 'titlebar_inactive_background',
        'titleBar.inactiveForeground': 'titlebar_inactive_text',

        # Menu Bar
        'menubar.selectionBackground': 'menu_selection_background',
        'menubar.selectionForeground': 'menu_selection_text',

        # Input controls
        'input.background': 'input_background',
        'input.foreground': 'input_text',
        'input.border': 'input_border',

        # Button controls
        'button.background': 'button_background',
        'button.foreground': 'button_text',
        'button.hoverBackground': 'button_hover_background',

        # Dropdown controls
        'dropdown.background': 'dropdown_background',
        'dropdown.foreground': 'dropdown_text',
        'dropdown.border': 'dropdown_border',

        # List/tree controls
        'list.activeSelectionBackground': 'list_selection_background',
        'list.activeSelectionForeground': 'list_selection_text',
        'list.hoverBackground': 'list_hover_background',
        'list.hoverForeground': 'list_hover_text',

        # Panel
        'panel.background': 'panel_background',
        'panel.border': 'panel_border',

        # Terminal
        'terminal.background': 'terminal_background',
        'terminal.foreground': 'terminal_text',

        # Scrollbar
        'scrollbar.shadow': 'scrollbar_shadow',
        'scrollbarSlider.background': 'scrollbar_background',
        'scrollbarSlider.hoverBackground': 'scrollbar_hover_background',
        'scrollbarSlider.activeBackground': 'scrollbar_active_background',

        # Border colors
        'focusBorder': 'focus_border',
        'contrastBorder': 'contrast_border',
        'contrastActiveBorder': 'contrast_active_border',

        # Text colors
        'foreground': 'text',
        'descriptionForeground': 'text_secondary',
        'errorForeground': 'text_error',

        # Badge
        'badge.background': 'badge_background',
        'badge.foreground': 'badge_text',

        # Progress bar
        'progressBar.background': 'progress_background',

        # Editor widget
        'editorWidget.background': 'widget_background',
        'editorWidget.border': 'widget_border',

        # Peek view
        'peekView.border': 'peek_border',
        'peekViewEditor.background': 'peek_editor_background',
        'peekViewResult.background': 'peek_result_background',

        # Git decoration
        'gitDecoration.modifiedResourceForeground': 'git_modified',
        'gitDecoration.deletedResourceForeground': 'git_deleted',
        'gitDecoration.untrackedResourceForeground': 'git_untracked',
        'gitDecoration.addedResourceForeground': 'git_added',

        # Notification
        'notificationCenter.border': 'notification_border',
        'notificationCenterHeader.background': 'notification_header_background',
        'notifications.background': 'notification_background',
        'notifications.foreground': 'notification_text',
    }

    def __init__(self):
        """Initialize the VSCode theme importer."""
        pass

    def import_from_file(self, theme_path: Path) -> Theme:
        """
        Import theme from VSCode theme file.

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
            with open(theme_path, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)

            theme_name = theme_path.stem
            return self.import_theme(theme_data, theme_name)

        except json.JSONDecodeError as e:
            raise ThemeSystemError(f"Invalid JSON in theme file {theme_path}: {e}")
        except Exception as e:
            raise ThemeSystemError(f"Error importing theme from {theme_path}: {e}")

    def import_theme(self, theme_data: Dict[str, Any], theme_name: str) -> Theme:
        """
        Import theme from VSCode theme data.

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
                animation_duration=200
            )
        )

        # Add token colors as metadata
        if token_colors:
            theme.metadata = theme.metadata or {}
            theme.metadata['vscode_token_colors'] = token_colors

        logger.info(f"Successfully converted VSCode theme: {theme_name}")
        return theme

    def _determine_theme_type(self, theme_data: Dict[str, Any]) -> str:
        """Determine if theme is light or dark."""
        # Check explicit type
        theme_type = theme_data.get('type')
        if theme_type in ['light', 'dark']:
            return theme_type

        # Try to infer from colors
        colors = theme_data.get('colors', {})
        background = colors.get('editor.background', '#ffffff')

        # Simple heuristic: check if background is dark
        if background.startswith('#'):
            # Convert hex to brightness
            hex_color = background[1:]
            if len(hex_color) == 6:
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                brightness = (r * 299 + g * 587 + b * 114) / 1000
                return 'dark' if brightness < 128 else 'light'

        # Default to dark
        return 'dark'

    def _extract_colors(self, theme_data: Dict[str, Any]) -> ThemeColors:
        """Extract and map colors from VSCode theme."""
        vscode_colors = theme_data.get('colors', {})
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
            return '#000000'

        color = color.strip()

        # Handle hex colors
        if color.startswith('#'):
            return color

        # Handle rgba/rgb colors - convert to hex
        if color.startswith('rgba(') or color.startswith('rgb('):
            return self._rgb_to_hex(color)

        # Handle named colors (limited support)
        named_colors = {
            'white': '#ffffff',
            'black': '#000000',
            'red': '#ff0000',
            'green': '#008000',
            'blue': '#0000ff',
            'transparent': '#00000000'
        }
        return named_colors.get(color.lower(), color)

    def _rgb_to_hex(self, rgb_color: str) -> str:
        """Convert RGB/RGBA color to hex format."""
        try:
            # Extract numbers from rgb(a) string
            import re
            numbers = re.findall(r'\d+(?:\.\d+)?', rgb_color)

            if len(numbers) >= 3:
                r = int(float(numbers[0]))
                g = int(float(numbers[1]))
                b = int(float(numbers[2]))

                # Handle alpha channel if present
                if len(numbers) >= 4:
                    a = int(float(numbers[3]) * 255)
                    return f'#{r:02x}{g:02x}{b:02x}{a:02x}'
                else:
                    return f'#{r:02x}{g:02x}{b:02x}'

        except (ValueError, IndexError):
            pass

        return '#000000'

    def _add_color_fallbacks(self, mapped_colors: Dict[str, str], vscode_colors: Dict[str, str]):
        """Add fallback colors for essential properties."""
        # Ensure we have basic colors
        if 'background' not in mapped_colors:
            mapped_colors['background'] = vscode_colors.get('editor.background', '#1e1e1e')

        if 'text' not in mapped_colors:
            mapped_colors['text'] = vscode_colors.get('editor.foreground', '#d4d4d4')

        # Generate complementary colors if missing
        if 'sidebar_background' not in mapped_colors:
            mapped_colors['sidebar_background'] = self._darken_color(mapped_colors['background'], 0.1)

        if 'statusbar_background' not in mapped_colors:
            mapped_colors['statusbar_background'] = self._darken_color(mapped_colors['background'], 0.2)

    def _darken_color(self, color: str, factor: float) -> str:
        """Darken a color by the given factor."""
        if not color.startswith('#'):
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

                return f'#{r:02x}{g:02x}{b:02x}'

        except (ValueError, IndexError):
            pass

        return color

    def _extract_token_colors(self, theme_data: Dict[str, Any]) -> List[VSCodeTokenColor]:
        """Extract token color rules from theme."""
        token_colors = []
        token_color_data = theme_data.get('tokenColors', [])

        for token_data in token_color_data:
            if isinstance(token_data, dict):
                token_color = VSCodeTokenColor(
                    name=token_data.get('name'),
                    scope=self._normalize_scope(token_data.get('scope')),
                    settings=token_data.get('settings', {})
                )
                token_colors.append(token_color)

        return token_colors

    def _normalize_scope(self, scope) -> Optional[List[str]]:
        """Normalize token scope to list format."""
        if not scope:
            return None

        if isinstance(scope, str):
            # Split comma-separated scopes
            return [s.strip() for s in scope.split(',') if s.strip()]
        elif isinstance(scope, list):
            return [str(s).strip() for s in scope if str(s).strip()]

        return None

    def export_to_vscode(self, theme: Theme, output_path: Path) -> None:
        """
        Export our theme to VSCode format.

        Args:
            theme: Theme to export
            output_path: Output file path

        Raises:
            ThemeSystemError: If export fails
        """
        logger.info(f"Exporting theme to VSCode format: {output_path}")

        try:
            vscode_theme = self._convert_to_vscode_format(theme)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(vscode_theme, f, indent=2, ensure_ascii=False)

            logger.info(f"Successfully exported theme to: {output_path}")

        except Exception as e:
            raise ThemeSystemError(f"Error exporting theme to VSCode format: {e}")

    def _convert_to_vscode_format(self, theme: Theme) -> Dict[str, Any]:
        """Convert our theme to VSCode format."""
        vscode_theme = {
            'name': theme.name,
            'type': theme.type,
            'colors': {},
            'tokenColors': []
        }

        # Reverse map our colors to VSCode format
        reverse_mappings = {v: k for k, v in self.COLOR_MAPPINGS.items()}

        for attr_name in dir(theme.colors):
            if not attr_name.startswith('_'):
                color_value = getattr(theme.colors, attr_name)
                if color_value and attr_name in reverse_mappings:
                    vscode_key = reverse_mappings[attr_name]
                    vscode_theme['colors'][vscode_key] = color_value

        # Add token colors if available
        if theme.metadata and 'vscode_token_colors' in theme.metadata:
            token_colors = theme.metadata['vscode_token_colors']
            for token_color in token_colors:
                if isinstance(token_color, VSCodeTokenColor):
                    token_data = {}
                    if token_color.name:
                        token_data['name'] = token_color.name
                    if token_color.scope:
                        token_data['scope'] = token_color.scope
                    if token_color.settings:
                        token_data['settings'] = token_color.settings
                    vscode_theme['tokenColors'].append(token_data)

        return vscode_theme