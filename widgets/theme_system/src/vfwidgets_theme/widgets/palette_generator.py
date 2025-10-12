"""Palette Generator - Qt QPalette Generation from Themes.

This module generates complete Qt QPalette objects from themes, complementing
the StylesheetGenerator by handling color roles that QSS cannot control.

Key Features:
- Automatic mapping of theme tokens to QPalette.ColorRole
- Handles alternating row colors (Base/AlternateBase)
- Supports all Qt color groups (Active, Inactive, Disabled)
- Smart fallbacks using ColorTokenRegistry defaults

QPalette Color Roles Covered:
- Window, WindowText - Window backgrounds and text
- Base, AlternateBase - Item view backgrounds (alternating rows)
- Text, BrightText - General text colors
- Button, ButtonText - Button backgrounds and text
- Highlight, HighlightedText - Selection colors
- Link, LinkVisited - Hyperlink colors
- ToolTipBase, ToolTipText - Tooltip colors
- PlaceholderText - Input placeholder text

Usage:
    generator = PaletteGenerator(theme)
    palette = generator.generate_palette()
    widget.setPalette(palette)

Design Philosophy:
PaletteGenerator completes the theming solution by handling the ~20% of Qt
styling that QSS cannot control. Combined with StylesheetGenerator, widgets
get complete, automatic theming without custom code.
"""

from PySide6.QtGui import QColor, QPalette

from ..core.theme import Theme
from ..logging import get_debug_logger

logger = get_debug_logger(__name__)


class PaletteGenerator:
    """Generates Qt QPalette from themes."""

    def __init__(self, theme: Theme):
        """Initialize palette generator.

        Args:
            theme: Theme to generate palette from

        """
        self.theme = theme

    def generate_palette(self) -> QPalette:
        """Generate complete QPalette from theme.

        Returns:
            QPalette configured with theme colors

        """
        palette = QPalette()

        # Generate for all color groups
        self._apply_active_colors(palette)
        self._apply_inactive_colors(palette)
        self._apply_disabled_colors(palette)

        logger.debug(f"Generated QPalette for theme '{self.theme.name}'")
        return palette

    def _get_color(self, token_name: str, default: str) -> QColor:
        """Get color from theme with fallback to default.

        Args:
            token_name: Token name (e.g., 'list.background')
            default: Default color hex string

        Returns:
            QColor object

        """
        value = self.theme.colors.get(token_name, default)
        return QColor(value)

    def _apply_active_colors(self, palette: QPalette) -> None:
        """Apply colors for active (focused) widgets.

        Args:
            palette: QPalette to modify

        """
        # Window colors
        window_bg = self._get_color('window.background', '#1e1e1e')
        window_fg = self._get_color('window.foreground', '#cccccc')
        palette.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, window_bg)
        palette.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, window_fg)

        # Base colors (for item views - alternating rows)
        base_bg = self._get_color('list.background', '#252526')
        alternate_bg = self._get_color('list.hoverBackground', '#2a2d2e')
        text_fg = self._get_color('list.foreground', '#cccccc')

        palette.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, base_bg)
        palette.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.AlternateBase, alternate_bg)
        palette.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, text_fg)

        # Bright text (for contrast on dark backgrounds)
        bright_text = self._get_color('colors.foreground', '#ffffff')
        palette.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.BrightText, bright_text)

        # Button colors
        button_bg = self._get_color('button.background', '#2d2d2d')
        button_fg = self._get_color('button.foreground', '#cccccc')
        palette.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, button_bg)
        palette.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, button_fg)

        # Highlight colors (selections)
        highlight_bg = self._get_color('list.activeSelectionBackground', '#094771')
        highlight_fg = self._get_color('list.activeSelectionForeground', '#ffffff')
        palette.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Highlight, highlight_bg)
        palette.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.HighlightedText, highlight_fg)

        # Link colors
        link = self._get_color('textLink.foreground', '#4080d0')
        link_visited = self._get_color('textLink.activeForeground', '#6060c0')
        palette.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Link, link)
        palette.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.LinkVisited, link_visited)

        # Tooltip colors
        tooltip_bg = self._get_color('editorWidget.background', '#252526')
        tooltip_fg = self._get_color('editorWidget.foreground', '#cccccc')
        palette.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipBase, tooltip_bg)
        palette.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipText, tooltip_fg)

        # Placeholder text
        placeholder = self._get_color('input.placeholderForeground', '#666666')
        palette.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.PlaceholderText, placeholder)

    def _apply_inactive_colors(self, palette: QPalette) -> None:
        """Apply colors for inactive (unfocused) widgets.

        Args:
            palette: QPalette to modify

        """
        # Most colors same as active, except selections

        # Copy active colors
        for role in [
            QPalette.ColorRole.Window,
            QPalette.ColorRole.WindowText,
            QPalette.ColorRole.Base,
            QPalette.ColorRole.AlternateBase,
            QPalette.ColorRole.Text,
            QPalette.ColorRole.BrightText,
            QPalette.ColorRole.Button,
            QPalette.ColorRole.ButtonText,
            QPalette.ColorRole.Link,
            QPalette.ColorRole.LinkVisited,
            QPalette.ColorRole.ToolTipBase,
            QPalette.ColorRole.ToolTipText,
            QPalette.ColorRole.PlaceholderText,
        ]:
            color = palette.color(QPalette.ColorGroup.Active, role)
            palette.setColor(QPalette.ColorGroup.Inactive, role, color)

        # Different selection colors when unfocused
        inactive_highlight_bg = self._get_color('list.inactiveSelectionBackground', '#3a3d41')
        inactive_highlight_fg = self._get_color('list.inactiveSelectionForeground', '#cccccc')
        palette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Highlight, inactive_highlight_bg)
        palette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.HighlightedText, inactive_highlight_fg)

    def _apply_disabled_colors(self, palette: QPalette) -> None:
        """Apply colors for disabled widgets.

        Args:
            palette: QPalette to modify

        """
        # Disabled colors - dimmed versions
        disabled_bg = self._get_color('widget.background', '#2d2d2d')
        disabled_fg = self._get_color('disabledForeground', '#666666')
        disabled_button_bg = self._get_color('button.background', '#2d2d2d')
        disabled_button_fg = self._get_color('disabledForeground', '#666666')

        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, disabled_bg)
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, disabled_fg)
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, disabled_bg)
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.AlternateBase, disabled_bg)
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, disabled_fg)
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.BrightText, disabled_fg)
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, disabled_button_bg)
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, disabled_button_fg)
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, disabled_bg)
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText, disabled_fg)
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.PlaceholderText, disabled_fg)
