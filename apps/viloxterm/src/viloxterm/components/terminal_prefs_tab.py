"""Terminal preferences tab for ViloxTerm.

Extracted from TerminalPreferencesDialog to work as a tab in the unified preferences.
"""

import logging

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
)

from vfwidgets_theme import ThemedQWidget
from vfwidgets_terminal import presets

logger = logging.getLogger(__name__)


class TerminalPreferencesTab(ThemedQWidget):
    """Tab widget for terminal behavior preferences.

    Contains all terminal-specific settings like scrollback, cursor, scrolling, and behavior.
    """

    def __init__(self, parent=None):
        """Initialize the terminal preferences tab.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self._config: dict = self._get_defaults()
        self._setup_ui()

    def _get_defaults(self) -> dict:
        """Get default terminal configuration.

        Returns:
            Dictionary with default terminal settings
        """
        return presets.DEFAULT_CONFIG.copy()

    def _setup_ui(self) -> None:
        """Set up the tab UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            """
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
        """
        )

        # Container
        container = ThemedQWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(10, 5, 10, 5)

        # Create preference sections
        container_layout.addWidget(self._create_general_group())
        container_layout.addWidget(self._create_font_group())
        container_layout.addWidget(self._create_cursor_group())
        container_layout.addWidget(self._create_scrolling_group())
        container_layout.addWidget(self._create_behavior_group())

        container_layout.addStretch()

        scroll.setWidget(container)
        layout.addWidget(scroll)

    def _create_general_group(self) -> QGroupBox:
        """Create the general settings group.

        Returns:
            QGroupBox with general settings
        """
        group = QGroupBox("General")
        layout = QFormLayout(group)

        # Scrollback lines
        self.scrollback_spin = QSpinBox()
        self.scrollback_spin.setRange(0, 100000)
        self.scrollback_spin.setSingleStep(1000)
        self.scrollback_spin.setSuffix(" lines")
        layout.addRow("Scrollback buffer:", self.scrollback_spin)

        # Tab width
        self.tab_width_spin = QSpinBox()
        self.tab_width_spin.setRange(1, 16)
        self.tab_width_spin.setSuffix(" spaces")
        layout.addRow("Tab width:", self.tab_width_spin)

        # TERM environment variable
        self.term_type_combo = QComboBox()
        self.term_type_combo.setEditable(True)
        self.term_type_combo.addItems(
            [
                "xterm-256color",
                "xterm",
                "xterm-color",
                "screen-256color",
                "screen",
                "tmux-256color",
                "tmux",
            ]
        )
        layout.addRow("Terminal type (TERM):", self.term_type_combo)

        return group

    def _create_font_group(self) -> QGroupBox:
        """Create the font settings group.

        Returns:
            QGroupBox with font settings
        """
        group = QGroupBox("Font")
        layout = QFormLayout(group)

        # Font family
        self.font_family_edit = QLineEdit()
        self.font_family_edit.setPlaceholderText("e.g., JetBrains Mono, Consolas, monospace")
        layout.addRow("Font family:", self.font_family_edit)

        # Font size
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(6, 72)
        self.font_size_spin.setSuffix(" px")
        layout.addRow("Font size:", self.font_size_spin)

        # Line height
        self.line_height_spin = QDoubleSpinBox()
        self.line_height_spin.setRange(0.5, 3.0)
        self.line_height_spin.setSingleStep(0.1)
        self.line_height_spin.setDecimals(1)
        layout.addRow("Line height:", self.line_height_spin)

        # Letter spacing
        self.letter_spacing_spin = QSpinBox()
        self.letter_spacing_spin.setRange(-10, 20)
        self.letter_spacing_spin.setSuffix(" px")
        layout.addRow("Letter spacing:", self.letter_spacing_spin)

        return group

    def _create_cursor_group(self) -> QGroupBox:
        """Create the cursor settings group.

        Returns:
            QGroupBox with cursor settings
        """
        group = QGroupBox("Cursor")
        layout = QFormLayout(group)

        # Cursor style
        self.cursor_style_combo = QComboBox()
        self.cursor_style_combo.addItems(["block", "underline", "bar"])
        layout.addRow("Cursor style:", self.cursor_style_combo)

        # Cursor blink
        self.cursor_blink_check = QCheckBox("Cursor blinks")
        layout.addRow("", self.cursor_blink_check)

        return group

    def _create_scrolling_group(self) -> QGroupBox:
        """Create the scrolling settings group.

        Returns:
            QGroupBox with scrolling settings
        """
        group = QGroupBox("Scrolling")
        layout = QFormLayout(group)

        # Scroll sensitivity
        self.scroll_sensitivity_spin = QSpinBox()
        self.scroll_sensitivity_spin.setRange(1, 20)
        layout.addRow("Mouse wheel sensitivity:", self.scroll_sensitivity_spin)

        # Fast scroll sensitivity
        self.fast_scroll_sensitivity_spin = QSpinBox()
        self.fast_scroll_sensitivity_spin.setRange(1, 50)
        layout.addRow("Fast scroll sensitivity:", self.fast_scroll_sensitivity_spin)

        # Fast scroll modifier
        self.fast_scroll_modifier_combo = QComboBox()
        self.fast_scroll_modifier_combo.addItems(["shift", "ctrl", "alt"])
        layout.addRow("Fast scroll modifier key:", self.fast_scroll_modifier_combo)

        return group

    def _create_behavior_group(self) -> QGroupBox:
        """Create the behavior settings group.

        Returns:
            QGroupBox with behavior settings
        """
        group = QGroupBox("Behavior")
        layout = QFormLayout(group)

        # Bell style
        self.bell_style_combo = QComboBox()
        self.bell_style_combo.addItems(["none", "visual", "sound"])
        layout.addRow("Bell style:", self.bell_style_combo)

        # Right-click selects word
        self.right_click_word_check = QCheckBox("Right-click selects word")
        layout.addRow("", self.right_click_word_check)

        # Convert EOL
        self.convert_eol_check = QCheckBox("Convert LF to CRLF")
        layout.addRow("", self.convert_eol_check)

        return group

    def load_preferences(self, config: dict) -> None:
        """Load terminal configuration into UI widgets.

        Args:
            config: Terminal configuration dictionary
        """
        self._config = config.copy()

        # Load values into UI controls
        self.scrollback_spin.setValue(config.get("scrollback", 1000))
        self.tab_width_spin.setValue(config.get("tabStopWidth", 4))

        # Load TERM type
        term_type = config.get("termType", "xterm-256color")
        index = self.term_type_combo.findText(term_type)
        if index >= 0:
            self.term_type_combo.setCurrentIndex(index)
        else:
            # If custom value, set it
            self.term_type_combo.setEditText(term_type)

        # Load font settings
        self.font_family_edit.setText(config.get("fontFamily", ""))
        self.font_size_spin.setValue(config.get("fontSize", 14))
        self.line_height_spin.setValue(config.get("lineHeight", 1.2))
        self.letter_spacing_spin.setValue(config.get("letterSpacing", 0))

        cursor_style = config.get("cursorStyle", "block")
        index = self.cursor_style_combo.findText(cursor_style)
        if index >= 0:
            self.cursor_style_combo.setCurrentIndex(index)

        self.cursor_blink_check.setChecked(config.get("cursorBlink", True))

        self.scroll_sensitivity_spin.setValue(config.get("scrollSensitivity", 1))
        self.fast_scroll_sensitivity_spin.setValue(config.get("fastScrollSensitivity", 5))

        fast_scroll_mod = config.get("fastScrollModifier", "shift")
        index = self.fast_scroll_modifier_combo.findText(fast_scroll_mod)
        if index >= 0:
            self.fast_scroll_modifier_combo.setCurrentIndex(index)

        bell_style = config.get("bellStyle", "none")
        index = self.bell_style_combo.findText(bell_style)
        if index >= 0:
            self.bell_style_combo.setCurrentIndex(index)

        self.right_click_word_check.setChecked(config.get("rightClickSelectsWord", False))
        self.convert_eol_check.setChecked(config.get("convertEol", False))

    def save_preferences(self) -> dict:
        """Save UI values to configuration dictionary.

        Returns:
            Dictionary with terminal configuration
        """
        self._config = {
            "scrollback": self.scrollback_spin.value(),
            "tabStopWidth": self.tab_width_spin.value(),
            "termType": self.term_type_combo.currentText(),
            "fontFamily": self.font_family_edit.text(),
            "fontSize": self.font_size_spin.value(),
            "lineHeight": self.line_height_spin.value(),
            "letterSpacing": self.letter_spacing_spin.value(),
            "cursorStyle": self.cursor_style_combo.currentText(),
            "cursorBlink": self.cursor_blink_check.isChecked(),
            "scrollSensitivity": self.scroll_sensitivity_spin.value(),
            "fastScrollSensitivity": self.fast_scroll_sensitivity_spin.value(),
            "fastScrollModifier": self.fast_scroll_modifier_combo.currentText(),
            "bellStyle": self.bell_style_combo.currentText(),
            "rightClickSelectsWord": self.right_click_word_check.isChecked(),
            "convertEol": self.convert_eol_check.isChecked(),
        }

        return self._config
