#!/usr/bin/env python3
"""
Unit tests for StylesheetGenerator.

Tests the stylesheet generation system including:
- Comprehensive stylesheet generation
- Widget-specific style sections
- Role marker support
- Descendant selector generation
- Theme token integration
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest

from vfwidgets_theme.core.theme import Theme
from vfwidgets_theme.widgets.stylesheet_generator import StylesheetGenerator


class TestStylesheetGenerator(unittest.TestCase):
    """Test StylesheetGenerator functionality."""

    def setUp(self):
        """Create a test theme for stylesheet generation."""
        self.test_theme = Theme(
            name="test",
            type="dark",
            colors={
                # Base colors
                "colors.background": "#1e1e1e",
                "colors.foreground": "#d4d4d4",
                "colors.focusBorder": "#007acc",
                "colors.contrastBorder": "#3c3c3c",
                "colors.disabledForeground": "#555555",

                # Button colors
                "button.background": "#0e639c",
                "button.foreground": "#ffffff",
                "button.border": "none",
                "button.hoverBackground": "#1177bb",
                "button.pressedBackground": "#094771",
                "button.disabledBackground": "#555555",
                "button.disabledForeground": "#999999",

                # Secondary button
                "button.secondary.background": "#313131",
                "button.secondary.foreground": "#cccccc",
                "button.secondary.hoverBackground": "#3e3e3e",

                # Danger button
                "button.danger.background": "#dc3545",
                "button.danger.hoverBackground": "#c82333",

                # Success button
                "button.success.background": "#28a745",
                "button.success.hoverBackground": "#218838",

                # Warning button
                "button.warning.background": "#ffc107",
                "button.warning.foreground": "#000000",
                "button.warning.hoverBackground": "#e0a800",

                # Input colors
                "input.background": "#3c3c3c",
                "input.foreground": "#cccccc",
                "input.border": "#3c3c3c",
                "input.placeholderForeground": "#989898",
                "input.focusBorder": "#007acc",
                "input.disabledBackground": "#555555",
                "input.disabledForeground": "#999999",

                # Editor colors
                "editor.background": "#1e1e1e",
                "editor.foreground": "#d4d4d4",
                "editor.selectionBackground": "#264f78",

                # List colors
                "list.background": "#252526",
                "list.foreground": "#cccccc",
                "list.activeSelectionBackground": "#094771",
                "list.activeSelectionForeground": "#ffffff",
                "list.inactiveSelectionBackground": "#37373d",
                "list.hoverBackground": "#2a2d2e",

                # Tab colors
                "tab.activeBackground": "#1e1e1e",
                "tab.activeForeground": "#ffffff",
                "tab.inactiveBackground": "#2d2d2d",
                "tab.inactiveForeground": "#969696",
                "tab.hoverBackground": "#2a2d2e",
                "tab.border": "#252526",

                # Menu colors
                "menu.background": "#252526",
                "menu.foreground": "#cccccc",
                "menu.border": "#454545",
                "menu.selectionBackground": "#094771",
                "menu.selectionForeground": "#ffffff",
                "menu.separatorBackground": "#454545",
                "menubar.background": "#252526",

                # Scrollbar colors
                "scrollbarSlider.background": "#79797966",
                "scrollbarSlider.hoverBackground": "#797979cc",
                "scrollbarSlider.activeBackground": "#bfbfbf66",

                # Combobox colors
                "combobox.background": "#3c3c3c",
                "combobox.foreground": "#cccccc",
                "combobox.border": "#3c3c3c",
                "combobox.arrowForeground": "#999999",
                "dropdown.listBackground": "#252526",

                # Table colors
                "table.gridColor": "#3c3c3c",
                "table.headerBackground": "#2d2d2d",
                "table.headerForeground": "#cccccc",

                # Status bar
                "statusBar.background": "#007acc",
                "statusBar.foreground": "#ffffff",

                # Progress bar
                "progressBar.background": "#007acc",

                # Splitter
                "splitter.background": "#3c3c3c",

                # Fonts
                "font.default.family": "Segoe UI, Arial, sans-serif",
                "font.default.size": "9pt",
                "font.editor.family": "Courier New, Consolas, monospace",
                "font.editor.size": "11pt",
                "font.button.family": "Segoe UI, Arial, sans-serif",
                "font.button.size": "9pt",
                "font.list.family": "Segoe UI, Arial, sans-serif",
                "font.list.size": "9pt",
                "font.tab.family": "Segoe UI, Arial, sans-serif",
                "font.tab.size": "9pt",
                "font.menu.family": "Segoe UI, Arial, sans-serif",
                "font.menu.size": "9pt",
            }
        )

    def test_generator_initialization(self):
        """Test StylesheetGenerator initialization."""
        generator = StylesheetGenerator(self.test_theme, "TestWidget")
        self.assertEqual(generator.theme, self.test_theme)
        self.assertEqual(generator.widget_class_name, "TestWidget")

    def test_comprehensive_stylesheet_generation(self):
        """Test that comprehensive stylesheet is generated."""
        generator = StylesheetGenerator(self.test_theme, "TestWidget")
        stylesheet = generator.generate_comprehensive_stylesheet()

        self.assertIsNotNone(stylesheet)
        self.assertIsInstance(stylesheet, str)
        self.assertGreater(len(stylesheet), 500, "Stylesheet should be substantial")

    def test_widget_styles_section(self):
        """Test that widget base styles are generated."""
        generator = StylesheetGenerator(self.test_theme, "TestWidget")
        stylesheet = generator.generate_comprehensive_stylesheet()

        # Should contain widget class name
        self.assertIn("TestWidget {", stylesheet)

        # Should contain base colors
        self.assertIn("#1e1e1e", stylesheet)  # background
        self.assertIn("#d4d4d4", stylesheet)  # foreground

        # Should contain font
        self.assertIn("Segoe UI", stylesheet)

    def test_button_styles_section(self):
        """Test that button styles are generated."""
        generator = StylesheetGenerator(self.test_theme, "TestWidget")
        stylesheet = generator.generate_comprehensive_stylesheet()

        # QPushButton
        self.assertIn("TestWidget QPushButton", stylesheet)
        self.assertIn("#0e639c", stylesheet)  # button background

        # Button states
        self.assertIn("QPushButton:hover", stylesheet)
        self.assertIn("QPushButton:pressed", stylesheet)
        self.assertIn("QPushButton:disabled", stylesheet)
        self.assertIn("QPushButton:focus", stylesheet)

    def test_button_role_markers(self):
        """Test that button role marker styles are generated."""
        generator = StylesheetGenerator(self.test_theme, "TestWidget")
        stylesheet = generator.generate_comprehensive_stylesheet()

        # Role markers
        self.assertIn('QPushButton[role="secondary"]', stylesheet)
        self.assertIn('QPushButton[role="danger"]', stylesheet)
        self.assertIn('QPushButton[role="success"]', stylesheet)
        self.assertIn('QPushButton[role="warning"]', stylesheet)

        # Role colors
        self.assertIn("#dc3545", stylesheet)  # danger
        self.assertIn("#28a745", stylesheet)  # success
        self.assertIn("#ffc107", stylesheet)  # warning

    def test_input_styles_section(self):
        """Test that input widget styles are generated."""
        generator = StylesheetGenerator(self.test_theme, "TestWidget")
        stylesheet = generator.generate_comprehensive_stylesheet()

        # Input widgets
        self.assertIn("TestWidget QLineEdit", stylesheet)
        self.assertIn("TestWidget QTextEdit", stylesheet)
        self.assertIn("TestWidget QPlainTextEdit", stylesheet)
        self.assertIn("TestWidget QSpinBox", stylesheet)

        # Input states
        self.assertIn("QLineEdit:focus", stylesheet)
        self.assertIn("QLineEdit:disabled", stylesheet)

    def test_editor_role_marker(self):
        """Test that editor role marker styles are generated."""
        generator = StylesheetGenerator(self.test_theme, "TestWidget")
        stylesheet = generator.generate_comprehensive_stylesheet()

        # Editor role
        self.assertIn('QTextEdit[role="editor"]', stylesheet)
        self.assertIn('QPlainTextEdit[role="editor"]', stylesheet)

        # Editor font (monospace)
        self.assertIn("Courier New", stylesheet)

        # Editor colors
        self.assertIn("#264f78", stylesheet)  # selection background

    def test_list_styles_section(self):
        """Test that list widget styles are generated."""
        generator = StylesheetGenerator(self.test_theme, "TestWidget")
        stylesheet = generator.generate_comprehensive_stylesheet()

        # List widgets
        self.assertIn("TestWidget QListWidget", stylesheet)
        self.assertIn("TestWidget QListView", stylesheet)
        self.assertIn("TestWidget QTreeWidget", stylesheet)
        self.assertIn("TestWidget QTreeView", stylesheet)
        self.assertIn("TestWidget QTableWidget", stylesheet)

        # List states
        self.assertIn("::item:selected", stylesheet)
        self.assertIn("::item:hover", stylesheet)

    def test_combo_styles_section(self):
        """Test that combobox styles are generated."""
        generator = StylesheetGenerator(self.test_theme, "TestWidget")
        stylesheet = generator.generate_comprehensive_stylesheet()

        self.assertIn("TestWidget QComboBox", stylesheet)
        self.assertIn("QComboBox:hover", stylesheet)
        self.assertIn("QComboBox::drop-down", stylesheet)
        self.assertIn("QComboBox::down-arrow", stylesheet)

    def test_tab_styles_section(self):
        """Test that tab widget styles are generated."""
        generator = StylesheetGenerator(self.test_theme, "TestWidget")
        stylesheet = generator.generate_comprehensive_stylesheet()

        self.assertIn("TestWidget QTabWidget", stylesheet)
        self.assertIn("TestWidget QTabBar::tab", stylesheet)
        self.assertIn("QTabBar::tab:selected", stylesheet)
        self.assertIn("QTabBar::tab:hover", stylesheet)

    def test_menu_styles_section(self):
        """Test that menu styles are generated."""
        generator = StylesheetGenerator(self.test_theme, "TestWidget")
        stylesheet = generator.generate_comprehensive_stylesheet()

        self.assertIn("TestWidget QMenuBar", stylesheet)
        self.assertIn("TestWidget QMenu", stylesheet)
        self.assertIn("QMenuBar::item", stylesheet)
        self.assertIn("QMenu::item:selected", stylesheet)
        self.assertIn("QMenu::separator", stylesheet)

    def test_scrollbar_styles_section(self):
        """Test that scrollbar styles are generated."""
        generator = StylesheetGenerator(self.test_theme, "TestWidget")
        stylesheet = generator.generate_comprehensive_stylesheet()

        self.assertIn("TestWidget QScrollBar:vertical", stylesheet)
        self.assertIn("TestWidget QScrollBar:horizontal", stylesheet)
        self.assertIn("QScrollBar::handle:vertical", stylesheet)
        self.assertIn("QScrollBar::handle:horizontal", stylesheet)

    def test_container_styles_section(self):
        """Test that container widget styles are generated."""
        generator = StylesheetGenerator(self.test_theme, "TestWidget")
        stylesheet = generator.generate_comprehensive_stylesheet()

        self.assertIn("TestWidget QGroupBox", stylesheet)
        self.assertIn("TestWidget QFrame", stylesheet)
        self.assertIn("TestWidget QSplitter", stylesheet)
        self.assertIn("TestWidget QToolBar", stylesheet)
        self.assertIn("TestWidget QStatusBar", stylesheet)

    def test_text_styles_section(self):
        """Test that text widget styles are generated."""
        generator = StylesheetGenerator(self.test_theme, "TestWidget")
        stylesheet = generator.generate_comprehensive_stylesheet()

        self.assertIn("TestWidget QLabel", stylesheet)
        self.assertIn("QLabel:disabled", stylesheet)

    def test_misc_styles_section(self):
        """Test that miscellaneous widget styles are generated."""
        generator = StylesheetGenerator(self.test_theme, "TestWidget")
        stylesheet = generator.generate_comprehensive_stylesheet()

        self.assertIn("TestWidget QProgressBar", stylesheet)
        self.assertIn("QProgressBar::chunk", stylesheet)

    def test_descendant_selectors(self):
        """Test that descendant selectors are properly generated."""
        generator = StylesheetGenerator(self.test_theme, "MyCustomWidget")
        stylesheet = generator.generate_comprehensive_stylesheet()

        # All selectors should start with widget class name
        # This ensures styles cascade to child widgets
        self.assertIn("MyCustomWidget QPushButton", stylesheet)
        self.assertIn("MyCustomWidget QLineEdit", stylesheet)
        self.assertIn("MyCustomWidget QLabel", stylesheet)

    def test_theme_token_integration(self):
        """Test that theme tokens are properly used."""
        generator = StylesheetGenerator(self.test_theme, "TestWidget")
        stylesheet = generator.generate_comprehensive_stylesheet()

        # Verify actual color values from theme are in stylesheet
        self.assertIn("#0e639c", stylesheet)  # button.background
        self.assertIn("#1177bb", stylesheet)  # button.hoverBackground
        self.assertIn("#094771", stylesheet)  # button.pressedBackground

    def test_minimal_theme(self):
        """Test stylesheet generation with minimal theme data."""
        minimal_theme = Theme(
            name="minimal",
            type="light",
            colors={
                "colors.background": "#ffffff",
                "colors.foreground": "#000000",
            }
        )

        generator = StylesheetGenerator(minimal_theme, "TestWidget")
        stylesheet = generator.generate_comprehensive_stylesheet()

        # Should generate stylesheet even with minimal data (uses fallbacks)
        self.assertIsNotNone(stylesheet)
        self.assertGreater(len(stylesheet), 100)
        self.assertIn("#ffffff", stylesheet)
        self.assertIn("#000000", stylesheet)

    def test_all_widget_types_covered(self):
        """Test that all major Qt widget types are covered."""
        generator = StylesheetGenerator(self.test_theme, "TestWidget")
        stylesheet = generator.generate_comprehensive_stylesheet()

        # List of all widget types that should be styled
        widget_types = [
            "QPushButton", "QToolButton", "QRadioButton", "QCheckBox",
            "QLineEdit", "QTextEdit", "QPlainTextEdit", "QSpinBox", "QDoubleSpinBox",
            "QListWidget", "QListView", "QTreeWidget", "QTreeView",
            "QTableWidget", "QTableView", "QHeaderView",
            "QComboBox", "QTabWidget", "QTabBar",
            "QMenuBar", "QMenu", "QScrollBar",
            "QGroupBox", "QFrame", "QSplitter", "QToolBar", "QStatusBar",
            "QLabel", "QProgressBar"
        ]

        for widget_type in widget_types:
            self.assertIn(widget_type, stylesheet,
                         f"Widget type {widget_type} should be in stylesheet")

    def test_pseudo_states_coverage(self):
        """Test that all major pseudo-states are covered."""
        generator = StylesheetGenerator(self.test_theme, "TestWidget")
        stylesheet = generator.generate_comprehensive_stylesheet()

        # Pseudo-states that should be covered
        # Note: :checked is not included because it's mostly used for checkboxes/radio buttons
        # which inherit default Qt styling, and our theme system doesn't override it
        pseudo_states = [
            ":hover", ":pressed", ":disabled", ":focus",
            ":selected", "::item", "::tab"
        ]

        for state in pseudo_states:
            self.assertIn(state, stylesheet,
                         f"Pseudo-state {state} should be in stylesheet")

    def test_font_hierarchy(self):
        """Test that font hierarchy is properly implemented."""
        generator = StylesheetGenerator(self.test_theme, "TestWidget")
        stylesheet = generator.generate_comprehensive_stylesheet()

        # Default UI font
        self.assertIn("Segoe UI", stylesheet)

        # Editor font (monospace)
        self.assertIn("Courier New", stylesheet)

    def test_no_empty_sections(self):
        """Test that stylesheet doesn't contain empty sections."""
        generator = StylesheetGenerator(self.test_theme, "TestWidget")
        stylesheet = generator.generate_comprehensive_stylesheet()

        # Should not have excessive consecutive newlines (more than 4)
        # Note: 4 newlines is acceptable for section separation
        self.assertNotIn("\n\n\n\n\n", stylesheet)


if __name__ == '__main__':
    unittest.main()
