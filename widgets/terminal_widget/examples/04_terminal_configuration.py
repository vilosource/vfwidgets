#!/usr/bin/env python3
"""
Terminal Configuration Example

This example demonstrates how to configure xterm.js behavior options for TerminalWidget.
Shows both constructor-based and runtime configuration, plus using presets.

Usage: python 04_terminal_configuration.py
"""

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

# Add parent directory to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vfwidgets_terminal import TerminalWidget
from vfwidgets_terminal.presets import TERMINAL_CONFIGS, list_presets


class TerminalConfigurationWindow(QMainWindow):
    """Demo window showing terminal configuration options."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Terminal Configuration Demo")
        self.resize(1400, 900)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # Create splitter for controls and terminals
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Left side: Configuration controls
        controls_widget = self._create_controls()
        splitter.addWidget(controls_widget)

        # Right side: Terminal tabs
        self.tab_widget = QTabWidget()
        splitter.addWidget(self.tab_widget)

        # Set splitter sizes (30% controls, 70% terminal)
        splitter.setSizes([400, 1000])

        # Create initial terminals with different presets
        self._create_demo_terminals()

    def _create_controls(self) -> QWidget:
        """Create the configuration controls panel."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title = QLabel("Terminal Configuration")
        title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        layout.addWidget(title)

        # Preset selector
        preset_group = QGroupBox("Configuration Presets")
        preset_layout = QVBoxLayout(preset_group)

        preset_combo_layout = QHBoxLayout()
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(list_presets())
        preset_combo_layout.addWidget(QLabel("Preset:"))
        preset_combo_layout.addWidget(self.preset_combo)
        preset_layout.addLayout(preset_combo_layout)

        apply_preset_btn = QPushButton("Apply Preset to Current Terminal")
        apply_preset_btn.clicked.connect(self._apply_preset)
        preset_layout.addWidget(apply_preset_btn)

        new_terminal_btn = QPushButton("New Terminal with Preset")
        new_terminal_btn.clicked.connect(self._create_terminal_with_preset)
        preset_layout.addWidget(new_terminal_btn)

        layout.addWidget(preset_group)

        # Typography settings (NEW: lineHeight and letterSpacing)
        typography_group = self._create_typography_group()
        layout.addWidget(typography_group)

        # Scrolling settings
        scroll_group = self._create_scroll_group()
        layout.addWidget(scroll_group)

        # Cursor settings
        cursor_group = self._create_cursor_group()
        layout.addWidget(cursor_group)

        # Behavior settings
        behavior_group = self._create_behavior_group()
        layout.addWidget(behavior_group)

        # Apply button
        apply_btn = QPushButton("Apply Custom Settings")
        apply_btn.setStyleSheet("font-weight: bold; padding: 8px;")
        apply_btn.clicked.connect(self._apply_custom_settings)
        layout.addWidget(apply_btn)

        layout.addStretch()

        return widget

    def _create_typography_group(self) -> QGroupBox:
        """Create typography configuration group for lineHeight and letterSpacing."""
        group = QGroupBox("Typography & Spacing")
        layout = QFormLayout(group)

        # Line height control (multiplier: 1.0 to 2.0)
        self.line_height_spin = QDoubleSpinBox()
        self.line_height_spin.setRange(1.0, 2.0)
        self.line_height_spin.setValue(1.2)
        self.line_height_spin.setSingleStep(0.1)
        self.line_height_spin.setDecimals(1)
        self.line_height_spin.setSuffix("x")
        self.line_height_spin.setToolTip(
            "Line spacing multiplier (1.0 = tight, 1.5 = relaxed)"
        )
        layout.addRow("Line height:", self.line_height_spin)

        # Letter spacing control (pixels: 0 to 5)
        self.letter_spacing_spin = QDoubleSpinBox()
        self.letter_spacing_spin.setRange(0, 5)
        self.letter_spacing_spin.setValue(0)
        self.letter_spacing_spin.setSingleStep(0.5)
        self.letter_spacing_spin.setDecimals(1)
        self.letter_spacing_spin.setSuffix(" px")
        self.letter_spacing_spin.setToolTip("Horizontal spacing between characters")
        layout.addRow("Letter spacing:", self.letter_spacing_spin)

        # Add quick presets
        presets_layout = QHBoxLayout()

        compact_btn = QPushButton("Compact")
        compact_btn.setToolTip("lineHeight: 1.0, letterSpacing: 0")
        compact_btn.clicked.connect(
            lambda: (
                self.line_height_spin.setValue(1.0),
                self.letter_spacing_spin.setValue(0),
            )
        )
        presets_layout.addWidget(compact_btn)

        normal_btn = QPushButton("Normal")
        normal_btn.setToolTip("lineHeight: 1.2, letterSpacing: 0")
        normal_btn.clicked.connect(
            lambda: (
                self.line_height_spin.setValue(1.2),
                self.letter_spacing_spin.setValue(0),
            )
        )
        presets_layout.addWidget(normal_btn)

        relaxed_btn = QPushButton("Relaxed")
        relaxed_btn.setToolTip("lineHeight: 1.5, letterSpacing: 1")
        relaxed_btn.clicked.connect(
            lambda: (
                self.line_height_spin.setValue(1.5),
                self.letter_spacing_spin.setValue(1.0),
            )
        )
        presets_layout.addWidget(relaxed_btn)

        layout.addRow("Quick presets:", presets_layout)

        return group

    def _create_scroll_group(self) -> QGroupBox:
        """Create scrolling configuration group."""
        group = QGroupBox("Scrolling")
        layout = QFormLayout(group)

        self.scrollback_spin = QSpinBox()
        self.scrollback_spin.setRange(0, 200000)
        self.scrollback_spin.setValue(1000)
        self.scrollback_spin.setSingleStep(1000)
        self.scrollback_spin.setSuffix(" lines")
        layout.addRow("Scrollback buffer:", self.scrollback_spin)

        self.scroll_sensitivity_spin = QSpinBox()
        self.scroll_sensitivity_spin.setRange(1, 20)
        self.scroll_sensitivity_spin.setValue(1)
        layout.addRow("Scroll sensitivity:", self.scroll_sensitivity_spin)

        self.fast_scroll_spin = QSpinBox()
        self.fast_scroll_spin.setRange(1, 50)
        self.fast_scroll_spin.setValue(5)
        layout.addRow("Fast scroll sensitivity:", self.fast_scroll_spin)

        self.fast_scroll_modifier = QComboBox()
        self.fast_scroll_modifier.addItems(["shift", "ctrl", "alt"])
        layout.addRow("Fast scroll modifier:", self.fast_scroll_modifier)

        return group

    def _create_cursor_group(self) -> QGroupBox:
        """Create cursor configuration group."""
        group = QGroupBox("Cursor")
        layout = QFormLayout(group)

        self.cursor_style_combo = QComboBox()
        self.cursor_style_combo.addItems(["block", "underline", "bar"])
        layout.addRow("Cursor style:", self.cursor_style_combo)

        self.cursor_blink_check = QCheckBox("Cursor blinks")
        self.cursor_blink_check.setChecked(True)
        layout.addRow("", self.cursor_blink_check)

        return group

    def _create_behavior_group(self) -> QGroupBox:
        """Create behavior configuration group."""
        group = QGroupBox("Behavior")
        layout = QFormLayout(group)

        self.tab_width_spin = QSpinBox()
        self.tab_width_spin.setRange(1, 16)
        self.tab_width_spin.setValue(4)
        self.tab_width_spin.setSuffix(" spaces")
        layout.addRow("Tab width:", self.tab_width_spin)

        self.bell_style_combo = QComboBox()
        self.bell_style_combo.addItems(["none", "visual", "sound"])
        layout.addRow("Bell style:", self.bell_style_combo)

        self.right_click_word_check = QCheckBox("Right-click selects word")
        layout.addRow("", self.right_click_word_check)

        self.convert_eol_check = QCheckBox("Convert LF to CRLF")
        layout.addRow("", self.convert_eol_check)

        return group

    def _create_demo_terminals(self):
        """Create demo terminals with different presets."""
        # Terminal with default config
        default_terminal = TerminalWidget()
        self.tab_widget.addTab(default_terminal, "Default Config")

        # Terminal with developer preset
        dev_config = TERMINAL_CONFIGS["developer"]
        dev_terminal = TerminalWidget(terminal_config=dev_config)
        self.tab_widget.addTab(dev_terminal, "Developer Preset")

        # Terminal with power user preset
        power_config = TERMINAL_CONFIGS["power_user"]
        power_terminal = TerminalWidget(terminal_config=power_config)
        self.tab_widget.addTab(power_terminal, "Power User Preset")

        # Terminal with minimal preset
        minimal_config = TERMINAL_CONFIGS["minimal"]
        minimal_terminal = TerminalWidget(terminal_config=minimal_config)
        self.tab_widget.addTab(minimal_terminal, "Minimal Preset")

    def _get_current_terminal(self) -> TerminalWidget:
        """Get the currently active terminal widget."""
        current_widget = self.tab_widget.currentWidget()
        if isinstance(current_widget, TerminalWidget):
            return current_widget
        return None

    def _apply_preset(self):
        """Apply selected preset to current terminal."""
        terminal = self._get_current_terminal()
        if not terminal:
            return

        preset_name = self.preset_combo.currentText()
        config = TERMINAL_CONFIGS[preset_name]

        terminal.set_terminal_config(config)

        # Update UI controls to match preset
        self._load_config_into_ui(config)

        print(f"Applied '{preset_name}' preset to current terminal")

    def _create_terminal_with_preset(self):
        """Create a new terminal with the selected preset."""
        preset_name = self.preset_combo.currentText()
        config = TERMINAL_CONFIGS[preset_name]

        terminal = TerminalWidget(terminal_config=config)
        tab_index = self.tab_widget.addTab(terminal, f"{preset_name.title()}")
        self.tab_widget.setCurrentIndex(tab_index)

        print(f"Created new terminal with '{preset_name}' preset")

    def _apply_custom_settings(self):
        """Apply custom settings from UI controls."""
        terminal = self._get_current_terminal()
        if not terminal:
            return

        config = {
            # Typography
            "lineHeight": self.line_height_spin.value(),
            "letterSpacing": self.letter_spacing_spin.value(),
            # Scrolling
            "scrollback": self.scrollback_spin.value(),
            "scrollSensitivity": self.scroll_sensitivity_spin.value(),
            "fastScrollSensitivity": self.fast_scroll_spin.value(),
            "fastScrollModifier": self.fast_scroll_modifier.currentText(),
            # Cursor
            "cursorStyle": self.cursor_style_combo.currentText(),
            "cursorBlink": self.cursor_blink_check.isChecked(),
            # Behavior
            "tabStopWidth": self.tab_width_spin.value(),
            "bellStyle": self.bell_style_combo.currentText(),
            "rightClickSelectsWord": self.right_click_word_check.isChecked(),
            "convertEol": self.convert_eol_check.isChecked(),
        }

        terminal.set_terminal_config(config)
        print(f"Applied custom configuration: {config}")

    def _load_config_into_ui(self, config: dict):
        """Load configuration values into UI controls."""
        # Typography
        self.line_height_spin.setValue(config.get("lineHeight", 1.2))
        self.letter_spacing_spin.setValue(config.get("letterSpacing", 0))

        # Scrolling
        self.scrollback_spin.setValue(config.get("scrollback", 1000))
        self.scroll_sensitivity_spin.setValue(config.get("scrollSensitivity", 1))
        self.fast_scroll_spin.setValue(config.get("fastScrollSensitivity", 5))

        modifier = config.get("fastScrollModifier", "shift")
        index = self.fast_scroll_modifier.findText(modifier)
        if index >= 0:
            self.fast_scroll_modifier.setCurrentIndex(index)

        # Cursor
        cursor_style = config.get("cursorStyle", "block")
        index = self.cursor_style_combo.findText(cursor_style)
        if index >= 0:
            self.cursor_style_combo.setCurrentIndex(index)

        self.cursor_blink_check.setChecked(config.get("cursorBlink", True))

        # Behavior
        self.tab_width_spin.setValue(config.get("tabStopWidth", 4))

        bell_style = config.get("bellStyle", "none")
        index = self.bell_style_combo.findText(bell_style)
        if index >= 0:
            self.bell_style_combo.setCurrentIndex(index)

        self.right_click_word_check.setChecked(
            config.get("rightClickSelectsWord", False)
        )
        self.convert_eol_check.setChecked(config.get("convertEol", False))


def main():
    """Run the terminal configuration demo."""
    app = QApplication(sys.argv)

    # Print available presets
    print("Available terminal configuration presets:")
    for preset_name in list_presets():
        print(f"  - {preset_name}")
    print()

    window = TerminalConfigurationWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
