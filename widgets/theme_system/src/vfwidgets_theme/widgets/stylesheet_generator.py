"""Stylesheet Generator - Comprehensive Qt Stylesheet Generation.

This module generates complete Qt stylesheets from themes, targeting ALL Qt widget types
with proper cascade to child widgets.

Key Features:
- Comprehensive coverage of all Qt widget types
- Proper descendant selectors for cascade
- All pseudo-states (:hover, :pressed, :disabled, :focus, :checked)
- Property selector support for role markers (role="danger", role="editor")
- Smart fallbacks using ColorTokenRegistry defaults

Widget Types Covered:
1. Buttons: QPushButton, QToolButton, QRadioButton, QCheckBox
2. Inputs: QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox
3. Lists: QListWidget, QListView, QTreeWidget, QTreeView
4. Tables: QTableWidget, QTableView
5. Combos: QComboBox
6. Tabs: QTabWidget, QTabBar
7. Menus: QMenuBar, QMenu, QAction
8. Scrollbars: QScrollBar
9. Containers: QGroupBox, QFrame, QSplitter, QToolBar, QStatusBar, QDockWidget
10. Text: QLabel
11. Misc: QProgressBar, QSlider, QDial

Usage:
    generator = StylesheetGenerator(theme, "MyWidget")
    stylesheet = generator.generate_comprehensive_stylesheet()
    widget.setStyleSheet(stylesheet)
"""

from ..core.theme import Theme
from ..core.tokens import ColorTokenRegistry
from ..logging import get_debug_logger

logger = get_debug_logger(__name__)


class StylesheetGenerator:
    """Generates comprehensive Qt stylesheets from themes."""

    def __init__(self, theme: Theme, widget_class_name: str):
        """Initialize stylesheet generator.

        Args:
            theme: Theme to generate stylesheet from
            widget_class_name: Class name of widget (e.g., "MyWidget")
                              Used as prefix for descendant selectors

        """
        self.theme = theme
        self.widget_class_name = widget_class_name

    def generate_comprehensive_stylesheet(self) -> str:
        """Generate complete stylesheet targeting all child widgets.

        Returns:
            Complete Qt stylesheet as string

        """
        sections = [
            self._generate_widget_styles(),
            self._generate_button_styles(),
            self._generate_input_styles(),
            self._generate_list_styles(),
            self._generate_combo_styles(),
            self._generate_tab_styles(),
            self._generate_menu_styles(),
            self._generate_scrollbar_styles(),
            self._generate_container_styles(),
            self._generate_text_styles(),
            self._generate_misc_styles(),
        ]

        # Filter out empty sections and join
        stylesheet = "\n\n".join(s for s in sections if s and s.strip())

        logger.debug(f"Generated stylesheet for {self.widget_class_name} ({len(stylesheet)} chars)")
        return stylesheet

    def _generate_widget_styles(self) -> str:
        """Generate styles for the widget itself."""
        bg = ColorTokenRegistry.get("colors.background", self.theme)
        fg = ColorTokenRegistry.get("colors.foreground", self.theme)
        # Use sensible defaults for fonts - no font tokens exist yet
        font_family = "'Segoe UI', 'San Francisco', 'Helvetica Neue', sans-serif"
        font_size = "14px"

        return f"""
/* Widget itself */
{self.widget_class_name} {{
    background-color: {bg};
    color: {fg};
    font-family: {font_family};
    font-size: {font_size};
}}
"""

    def _generate_button_styles(self) -> str:
        """Generate comprehensive button styles."""
        prefix = self.widget_class_name

        # Get button tokens
        btn_bg = ColorTokenRegistry.get("button.background", self.theme)
        btn_fg = ColorTokenRegistry.get("button.foreground", self.theme)
        btn_border = ColorTokenRegistry.get("button.border", self.theme)
        btn_hover_bg = ColorTokenRegistry.get("button.hoverBackground", self.theme)
        btn_pressed_bg = ColorTokenRegistry.get("button.pressedBackground", self.theme)
        btn_disabled_bg = ColorTokenRegistry.get("button.disabledBackground", self.theme)
        btn_disabled_fg = ColorTokenRegistry.get("button.disabledForeground", self.theme)

        # Secondary button
        btn_sec_bg = ColorTokenRegistry.get("button.secondary.background", self.theme)
        btn_sec_fg = ColorTokenRegistry.get("button.secondary.foreground", self.theme)
        btn_sec_hover = ColorTokenRegistry.get("button.secondary.hoverBackground", self.theme)

        # Danger button
        btn_danger_bg = ColorTokenRegistry.get("button.danger.background", self.theme)
        btn_danger_hover = ColorTokenRegistry.get("button.danger.hoverBackground", self.theme)

        # Success button
        btn_success_bg = ColorTokenRegistry.get("button.success.background", self.theme)
        btn_success_hover = ColorTokenRegistry.get("button.success.hoverBackground", self.theme)

        # Warning button
        btn_warning_bg = ColorTokenRegistry.get("button.warning.background", self.theme)
        btn_warning_fg = ColorTokenRegistry.get("button.warning.foreground", self.theme)
        btn_warning_hover = ColorTokenRegistry.get("button.warning.hoverBackground", self.theme)

        # Focus border
        focus_border = ColorTokenRegistry.get("colors.focusBorder", self.theme)

        # Font - use sensible defaults
        btn_font = "'Segoe UI', 'San Francisco', 'Helvetica Neue', sans-serif"
        btn_font_size = "14px"

        return f"""
/* QPushButton - Base styles */
{prefix} QPushButton {{
    background-color: {btn_bg};
    color: {btn_fg};
    border: {btn_border};
    border-radius: 2px;
    padding: 4px 14px;
    min-height: 22px;
    font-family: {btn_font};
    font-size: {btn_font_size};
}}

{prefix} QPushButton:hover {{
    background-color: {btn_hover_bg};
}}

{prefix} QPushButton:pressed {{
    background-color: {btn_pressed_bg};
}}

{prefix} QPushButton:disabled {{
    background-color: {btn_disabled_bg};
    color: {btn_disabled_fg};
}}

{prefix} QPushButton:focus {{
    border: 1px solid {focus_border};
    outline: none;
}}

/* Secondary button variant */
{prefix} QPushButton[role="secondary"] {{
    background-color: {btn_sec_bg};
    color: {btn_sec_fg};
    border: 1px solid {ColorTokenRegistry.get("input.border", self.theme)};
}}

{prefix} QPushButton[role="secondary"]:hover {{
    background-color: {btn_sec_hover};
}}

/* Danger button variant */
{prefix} QPushButton[role="danger"] {{
    background-color: {btn_danger_bg};
    color: #ffffff;
}}

{prefix} QPushButton[role="danger"]:hover {{
    background-color: {btn_danger_hover};
}}

/* Success button variant */
{prefix} QPushButton[role="success"] {{
    background-color: {btn_success_bg};
    color: #ffffff;
}}

{prefix} QPushButton[role="success"]:hover {{
    background-color: {btn_success_hover};
}}

/* Warning button variant */
{prefix} QPushButton[role="warning"] {{
    background-color: {btn_warning_bg};
    color: {btn_warning_fg};
}}

{prefix} QPushButton[role="warning"]:hover {{
    background-color: {btn_warning_hover};
}}

/* QToolButton */
{prefix} QToolButton {{
    background-color: {btn_bg};
    color: {btn_fg};
    border: {btn_border};
    border-radius: 2px;
    padding: 4px;
}}

{prefix} QToolButton:hover {{
    background-color: {btn_hover_bg};
}}

{prefix} QToolButton:pressed {{
    background-color: {btn_pressed_bg};
}}

/* QRadioButton and QCheckBox */
{prefix} QRadioButton,
{prefix} QCheckBox {{
    color: {ColorTokenRegistry.get("colors.foreground", self.theme)};
    spacing: 5px;
}}

{prefix} QRadioButton:disabled,
{prefix} QCheckBox:disabled {{
    color: {ColorTokenRegistry.get("colors.disabledForeground", self.theme)};
}}
"""

    def _generate_input_styles(self) -> str:
        """Generate styles for input widgets."""
        prefix = self.widget_class_name

        # Input tokens
        input_bg = ColorTokenRegistry.get("input.background", self.theme)
        input_fg = ColorTokenRegistry.get("input.foreground", self.theme)
        input_border = ColorTokenRegistry.get("input.border", self.theme)
        ColorTokenRegistry.get("input.placeholderForeground", self.theme)
        input_focus_border = ColorTokenRegistry.get("input.focusBorder", self.theme)
        input_disabled_bg = ColorTokenRegistry.get("input.disabledBackground", self.theme)
        input_disabled_fg = ColorTokenRegistry.get("input.disabledForeground", self.theme)

        # Editor tokens (for role="editor")
        editor_bg = ColorTokenRegistry.get("editor.background", self.theme)
        editor_fg = ColorTokenRegistry.get("editor.foreground", self.theme)
        editor_selection = ColorTokenRegistry.get("editor.selectionBackground", self.theme)
        # Use sensible defaults for fonts - no font tokens exist yet
        editor_font = "'Consolas', 'Monaco', 'Courier New', monospace"
        editor_font_size = "13px"

        # Default font
        default_font = "'Segoe UI', 'San Francisco', 'Helvetica Neue', sans-serif"
        default_font_size = "14px"

        return f"""
/* QLineEdit */
{prefix} QLineEdit {{
    background-color: {input_bg};
    color: {input_fg};
    border: 1px solid {input_border};
    border-radius: 2px;
    padding: 4px;
    font-family: {default_font};
    font-size: {default_font_size};
}}

{prefix} QLineEdit:focus {{
    border-color: {input_focus_border};
}}

{prefix} QLineEdit:disabled {{
    background-color: {input_disabled_bg};
    color: {input_disabled_fg};
}}

/* QTextEdit and QPlainTextEdit - Default (non-editor role) */
{prefix} QTextEdit,
{prefix} QPlainTextEdit {{
    background-color: {input_bg};
    color: {input_fg};
    border: 1px solid {input_border};
    padding: 4px;
    font-family: {default_font};
    font-size: {default_font_size};
}}

{prefix} QTextEdit:focus,
{prefix} QPlainTextEdit:focus {{
    border-color: {input_focus_border};
}}

{prefix} QTextEdit:disabled,
{prefix} QPlainTextEdit:disabled {{
    background-color: {input_disabled_bg};
    color: {input_disabled_fg};
}}

/* Editor role - Monospace font, editor-specific colors */
/* IMPORTANT: Both selectors are needed:
   - QTextEdit[role="editor"] matches when the widget itself IS a QTextEdit
   - {prefix} QTextEdit[role="editor"] matches QTextEdit children of {prefix}
   Without the first, widgets that inherit from QTextEdit won't style correctly! */
QTextEdit[role="editor"],
QPlainTextEdit[role="editor"],
{prefix} QTextEdit[role="editor"],
{prefix} QPlainTextEdit[role="editor"] {{
    background-color: {editor_bg};
    color: {editor_fg};
    border: none;
    padding: 8px;
    font-family: {editor_font};
    font-size: {editor_font_size};
    selection-background-color: {editor_selection};
}}

/* QSpinBox and QDoubleSpinBox */
{prefix} QSpinBox,
{prefix} QDoubleSpinBox {{
    background-color: {input_bg};
    color: {input_fg};
    border: 1px solid {input_border};
    border-radius: 2px;
    padding: 2px;
}}

{prefix} QSpinBox:focus,
{prefix} QDoubleSpinBox:focus {{
    border-color: {input_focus_border};
}}

{prefix} QSpinBox:disabled,
{prefix} QDoubleSpinBox:disabled {{
    background-color: {input_disabled_bg};
    color: {input_disabled_fg};
}}
"""

    def _generate_list_styles(self) -> str:
        """Generate styles for list and tree widgets."""
        prefix = self.widget_class_name

        # List tokens
        list_bg = ColorTokenRegistry.get("list.background", self.theme)
        list_fg = ColorTokenRegistry.get("list.foreground", self.theme)
        list_sel_bg = ColorTokenRegistry.get("list.activeSelectionBackground", self.theme)
        list_sel_fg = ColorTokenRegistry.get("list.activeSelectionForeground", self.theme)
        list_inactive_sel_bg = ColorTokenRegistry.get(
            "list.inactiveSelectionBackground", self.theme
        )
        list_hover_bg = ColorTokenRegistry.get("list.hoverBackground", self.theme)

        # Font - use sensible defaults
        list_font = "'Segoe UI', 'San Francisco', 'Helvetica Neue', sans-serif"
        list_font_size = "14px"

        return f"""
/* QListWidget and QListView */
{prefix} QListWidget,
{prefix} QListView {{
    background-color: {list_bg};
    color: {list_fg};
    border: none;
    outline: none;
    font-family: {list_font};
    font-size: {list_font_size};
}}

{prefix} QListWidget::item,
{prefix} QListView::item {{
    padding: 4px;
}}

{prefix} QListWidget::item:selected,
{prefix} QListView::item:selected {{
    background-color: {list_sel_bg};
    color: {list_sel_fg};
}}

{prefix} QListWidget::item:selected:!active,
{prefix} QListView::item:selected:!active {{
    background-color: {list_inactive_sel_bg};
}}

{prefix} QListWidget::item:hover,
{prefix} QListView::item:hover {{
    background-color: {list_hover_bg};
}}

/* QTreeWidget and QTreeView */
{prefix} QTreeWidget,
{prefix} QTreeView {{
    background-color: {list_bg};
    color: {list_fg};
    border: none;
    outline: none;
    font-family: {list_font};
    font-size: {list_font_size};
}}

{prefix} QTreeWidget::item,
{prefix} QTreeView::item {{
    padding: 4px;
}}

{prefix} QTreeWidget::item:selected,
{prefix} QTreeView::item:selected {{
    background-color: {list_sel_bg};
    color: {list_sel_fg};
}}

{prefix} QTreeWidget::item:selected:!active,
{prefix} QTreeView::item:selected:!active {{
    background-color: {list_inactive_sel_bg};
}}

{prefix} QTreeWidget::item:hover,
{prefix} QTreeView::item:hover {{
    background-color: {list_hover_bg};
}}

/* QTableWidget and QTableView */
{prefix} QTableWidget,
{prefix} QTableView {{
    background-color: {list_bg};
    color: {list_fg};
    gridline-color: {ColorTokenRegistry.get("table.gridColor", self.theme)};
    border: none;
}}

{prefix} QTableWidget::item:selected,
{prefix} QTableView::item:selected {{
    background-color: {list_sel_bg};
    color: {list_sel_fg};
}}

{prefix} QHeaderView::section {{
    background-color: {ColorTokenRegistry.get("table.headerBackground", self.theme)};
    color: {ColorTokenRegistry.get("table.headerForeground", self.theme)};
    padding: 4px;
    border: none;
    border-bottom: 1px solid {ColorTokenRegistry.get("table.gridColor", self.theme)};
}}
"""

    def _generate_combo_styles(self) -> str:
        """Generate styles for combobox."""
        prefix = self.widget_class_name

        combo_bg = ColorTokenRegistry.get("combobox.background", self.theme)
        combo_fg = ColorTokenRegistry.get("combobox.foreground", self.theme)
        combo_border = ColorTokenRegistry.get("combobox.border", self.theme)
        combo_arrow = ColorTokenRegistry.get("combobox.arrowForeground", self.theme)
        dropdown_bg = ColorTokenRegistry.get("dropdown.listBackground", self.theme)

        return f"""
/* QComboBox */
{prefix} QComboBox {{
    background-color: {combo_bg};
    color: {combo_fg};
    border: 1px solid {combo_border};
    border-radius: 2px;
    padding: 4px;
    min-height: 20px;
}}

{prefix} QComboBox:hover {{
    background-color: {ColorTokenRegistry.get("list.hoverBackground", self.theme)};
}}

{prefix} QComboBox:focus {{
    border-color: {ColorTokenRegistry.get("input.focusBorder", self.theme)};
}}

{prefix} QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

{prefix} QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid {combo_arrow};
    width: 0;
    height: 0;
}}

{prefix} QComboBox QAbstractItemView {{
    background-color: {dropdown_bg};
    color: {combo_fg};
    selection-background-color: {ColorTokenRegistry.get("list.activeSelectionBackground", self.theme)};
    selection-color: {ColorTokenRegistry.get("list.activeSelectionForeground", self.theme)};
    border: 1px solid {combo_border};
}}
"""

    def _generate_tab_styles(self) -> str:
        """Generate styles for tabs."""
        prefix = self.widget_class_name

        # Tab tokens
        tab_active_bg = ColorTokenRegistry.get("tab.activeBackground", self.theme)
        tab_active_fg = ColorTokenRegistry.get("tab.activeForeground", self.theme)
        tab_inactive_bg = ColorTokenRegistry.get("tab.inactiveBackground", self.theme)
        tab_inactive_fg = ColorTokenRegistry.get("tab.inactiveForeground", self.theme)
        tab_hover_bg = ColorTokenRegistry.get("tab.hoverBackground", self.theme)
        tab_border = ColorTokenRegistry.get("tab.border", self.theme)

        # Font - use sensible defaults
        tab_font = "'Segoe UI', 'San Francisco', 'Helvetica Neue', sans-serif"
        tab_font_size = "14px"

        return f"""
/* QTabWidget */
{prefix} QTabWidget::pane {{
    border: 1px solid {tab_border};
    background-color: {tab_active_bg};
}}

{prefix} QTabBar::tab {{
    background-color: {tab_inactive_bg};
    color: {tab_inactive_fg};
    border: 1px solid {tab_border};
    padding: 6px 12px;
    font-family: {tab_font};
    font-size: {tab_font_size};
}}

{prefix} QTabBar::tab:selected {{
    background-color: {tab_active_bg};
    color: {tab_active_fg};
    border-bottom-color: {tab_active_bg};
}}

{prefix} QTabBar::tab:hover {{
    background-color: {tab_hover_bg};
}}

{prefix} QTabBar::tab:!selected {{
    margin-top: 2px;
}}
"""

    def _generate_menu_styles(self) -> str:
        """Generate styles for menus."""
        prefix = self.widget_class_name

        # Menu tokens
        menu_bg = ColorTokenRegistry.get("menu.background", self.theme)
        menu_fg = ColorTokenRegistry.get("menu.foreground", self.theme)
        menu_border = ColorTokenRegistry.get("menu.border", self.theme)
        menu_sel_bg = ColorTokenRegistry.get("menu.selectionBackground", self.theme)
        menu_sel_fg = ColorTokenRegistry.get("menu.selectionForeground", self.theme)

        # Font - use sensible defaults
        menu_font = "'Segoe UI', 'San Francisco', 'Helvetica Neue', sans-serif"
        menu_font_size = "14px"
        menubar_bg = ColorTokenRegistry.get("menubar.background", self.theme)

        return f"""
/* QMenuBar */
{prefix} QMenuBar {{
    background-color: {menubar_bg};
    color: {menu_fg};
    border-bottom: 1px solid {menu_border};
    font-family: {menu_font};
    font-size: {menu_font_size};
}}

{prefix} QMenuBar::item {{
    padding: 4px 8px;
    background-color: transparent;
}}

{prefix} QMenuBar::item:selected {{
    background-color: {menu_sel_bg};
    color: {menu_sel_fg};
}}

{prefix} QMenuBar::item:pressed {{
    background-color: {menu_sel_bg};
}}

/* QMenu */
{prefix} QMenu {{
    background-color: {menu_bg};
    color: {menu_fg};
    border: 1px solid {menu_border};
    font-family: {menu_font};
    font-size: {menu_font_size};
}}

{prefix} QMenu::item {{
    padding: 6px 20px;
}}

{prefix} QMenu::item:selected {{
    background-color: {menu_sel_bg};
    color: {menu_sel_fg};
}}

{prefix} QMenu::item:disabled {{
    color: {ColorTokenRegistry.get("colors.disabledForeground", self.theme)};
}}

{prefix} QMenu::separator {{
    height: 1px;
    background-color: {ColorTokenRegistry.get("menu.separatorBackground", self.theme)};
    margin: 4px 0;
}}
"""

    def _generate_scrollbar_styles(self) -> str:
        """Generate styles for scrollbars."""
        prefix = self.widget_class_name

        scrollbar_bg = ColorTokenRegistry.get("scrollbarSlider.background", self.theme)
        scrollbar_hover = ColorTokenRegistry.get("scrollbarSlider.hoverBackground", self.theme)
        scrollbar_active = ColorTokenRegistry.get("scrollbarSlider.activeBackground", self.theme)

        return f"""
/* QScrollBar - Vertical */
{prefix} QScrollBar:vertical {{
    background-color: transparent;
    width: 14px;
    margin: 0;
}}

{prefix} QScrollBar::handle:vertical {{
    background-color: {scrollbar_bg};
    min-height: 20px;
    border-radius: 7px;
    margin: 2px;
}}

{prefix} QScrollBar::handle:vertical:hover {{
    background-color: {scrollbar_hover};
}}

{prefix} QScrollBar::handle:vertical:pressed {{
    background-color: {scrollbar_active};
}}

{prefix} QScrollBar::add-line:vertical,
{prefix} QScrollBar::sub-line:vertical {{
    height: 0;
}}

{prefix} QScrollBar::add-page:vertical,
{prefix} QScrollBar::sub-page:vertical {{
    background: none;
}}

/* QScrollBar - Horizontal */
{prefix} QScrollBar:horizontal {{
    background-color: transparent;
    height: 14px;
    margin: 0;
}}

{prefix} QScrollBar::handle:horizontal {{
    background-color: {scrollbar_bg};
    min-width: 20px;
    border-radius: 7px;
    margin: 2px;
}}

{prefix} QScrollBar::handle:horizontal:hover {{
    background-color: {scrollbar_hover};
}}

{prefix} QScrollBar::handle:horizontal:pressed {{
    background-color: {scrollbar_active};
}}

{prefix} QScrollBar::add-line:horizontal,
{prefix} QScrollBar::sub-line:horizontal {{
    width: 0;
}}

{prefix} QScrollBar::add-page:horizontal,
{prefix} QScrollBar::sub-page:horizontal {{
    background: none;
}}
"""

    def _generate_container_styles(self) -> str:
        """Generate styles for container widgets."""
        prefix = self.widget_class_name

        border_color = ColorTokenRegistry.get("colors.contrastBorder", self.theme)
        bg_color = ColorTokenRegistry.get("colors.background", self.theme)
        fg_color = ColorTokenRegistry.get("colors.foreground", self.theme)
        splitter_bg = ColorTokenRegistry.get("splitter.background", self.theme)

        return f"""
/* QGroupBox */
{prefix} QGroupBox {{
    color: {fg_color};
    border: 1px solid {border_color};
    border-radius: 4px;
    margin-top: 8px;
    padding-top: 8px;
}}

{prefix} QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 4px;
    color: {fg_color};
}}

/* QFrame */
{prefix} QFrame[frameShape="4"],
{prefix} QFrame[frameShape="5"] {{
    border: 1px solid {border_color};
}}

/* QSplitter */
{prefix} QSplitter::handle {{
    background-color: {splitter_bg};
}}

{prefix} QSplitter::handle:horizontal {{
    width: 1px;
}}

{prefix} QSplitter::handle:vertical {{
    height: 1px;
}}

/* QToolBar */
{prefix} QToolBar {{
    background-color: {bg_color};
    border: none;
    spacing: 4px;
    padding: 4px;
}}

/* QStatusBar */
{prefix} QStatusBar {{
    background-color: {ColorTokenRegistry.get("statusBar.background", self.theme)};
    color: {ColorTokenRegistry.get("statusBar.foreground", self.theme)};
    border-top: 1px solid {border_color};
}}
"""

    def _generate_text_styles(self) -> str:
        """Generate styles for text widgets."""
        prefix = self.widget_class_name

        fg_color = ColorTokenRegistry.get("colors.foreground", self.theme)

        return f"""
/* QLabel */
{prefix} QLabel {{
    color: {fg_color};
    background-color: transparent;
}}

{prefix} QLabel:disabled {{
    color: {ColorTokenRegistry.get("colors.disabledForeground", self.theme)};
}}
"""

    def _generate_misc_styles(self) -> str:
        """Generate styles for miscellaneous widgets."""
        prefix = self.widget_class_name

        progress_bg = ColorTokenRegistry.get("progressBar.background", self.theme)

        return f"""
/* QProgressBar */
{prefix} QProgressBar {{
    border: 1px solid {ColorTokenRegistry.get("colors.contrastBorder", self.theme)};
    border-radius: 2px;
    text-align: center;
    background-color: {ColorTokenRegistry.get("colors.background", self.theme)};
}}

{prefix} QProgressBar::chunk {{
    background-color: {progress_bg};
    border-radius: 2px;
}}
"""
