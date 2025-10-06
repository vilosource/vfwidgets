"""Terminal Preferences Dialog for ViloxTerm.

This dialog allows users to configure terminal behavior settings like scrollback,
cursor style, bell style, and scroll sensitivity.
"""

import logging
from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
)

from vfwidgets_theme import ThemedDialog, ThemedQWidget
from vfwidgets_terminal import presets

logger = logging.getLogger(__name__)


class TerminalPreferencesDialog(ThemedDialog):
    """Dialog for configuring terminal behavior preferences."""

    # Signal emitted when preferences are applied
    preferencesApplied = Signal(dict)

    def __init__(self, current_config: Optional[dict] = None, parent=None):
        """Initialize the terminal preferences dialog.

        Args:
            current_config: Current terminal configuration dictionary
            parent: Parent widget
        """
        super().__init__(parent)

        self.current_config = current_config.copy() if current_config else self._get_defaults()

        self.setWindowTitle("Terminal Preferences")
        self.resize(600, 500)

        self._setup_ui()
        self._load_config()

    def _get_defaults(self) -> dict:
        """Get default terminal configuration.

        Returns:
            Dictionary with default terminal settings
        """
        # Use the default preset from terminal widget
        return presets.DEFAULT_CONFIG.copy()

    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Top bar (buttons)
        top_bar = self._create_top_bar()
        layout.addWidget(top_bar, 0)

        # Scrollable preferences panel
        prefs_panel = self._create_preferences_panel()
        layout.addWidget(prefs_panel, 1)

        # Bottom button bar
        bottom_bar = self._create_bottom_bar()
        layout.addWidget(bottom_bar, 0)

    def _create_top_bar(self) -> ThemedQWidget:
        """Create the top bar with action buttons.

        Returns:
            ThemedQWidget containing the top bar
        """
        widget = ThemedQWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 5)
        layout.setSpacing(6)

        # First row: Title
        title_layout = QHBoxLayout()
        title_label = QLabel("Terminal Behavior Settings")
        title_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)

        # Second row: Preset selector and reset button
        preset_layout = QHBoxLayout()

        preset_layout.addWidget(QLabel("Load Preset:"))

        self.preset_combo = QComboBox()
        # Add "Custom" as first option for user-modified configs
        self.preset_combo.addItem("Custom")
        self.preset_combo.addItems(presets.list_presets())
        self.preset_combo.setMaximumWidth(150)
        self.preset_combo.currentTextChanged.connect(self._on_preset_selected)
        preset_layout.addWidget(self.preset_combo)

        preset_layout.addStretch()

        # Reset to defaults button
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setMaximumWidth(130)
        reset_btn.clicked.connect(self._reset_to_defaults)
        preset_layout.addWidget(reset_btn)

        layout.addLayout(preset_layout)

        return widget

    def _create_preferences_panel(self) -> ThemedQWidget:
        """Create the scrollable preferences panel.

        Returns:
            ThemedQWidget containing the preferences form
        """
        # Outer container (ensures theme inheritance)
        outer = ThemedQWidget()
        outer_layout = QVBoxLayout(outer)
        outer_layout.setContentsMargins(0, 0, 0, 0)

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

        # Inner container
        container = ThemedQWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(10, 5, 10, 5)

        # Create preference sections
        container_layout.addWidget(self._create_general_group())
        container_layout.addWidget(self._create_cursor_group())
        container_layout.addWidget(self._create_scrolling_group())
        container_layout.addWidget(self._create_behavior_group())

        container_layout.addStretch()

        scroll.setWidget(container)
        outer_layout.addWidget(scroll)

        return outer

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

    def _create_bottom_bar(self) -> ThemedQWidget:
        """Create the bottom button bar.

        Returns:
            ThemedQWidget containing bottom buttons
        """
        widget = ThemedQWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 5, 10, 10)

        layout.addStretch()

        # Apply button
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.on_apply)
        layout.addWidget(apply_btn)

        # OK button
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.on_ok)
        ok_btn.setDefault(True)
        layout.addWidget(ok_btn)

        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)

        return widget

    def _load_config(self) -> None:
        """Load configuration values into UI widgets."""
        # Temporarily disconnect preset combo to avoid triggering preset selection
        self.preset_combo.currentTextChanged.disconnect(self._on_preset_selected)

        # Check if current config matches any preset
        matching_preset = self._find_matching_preset()
        if matching_preset:
            index = self.preset_combo.findText(matching_preset)
            if index >= 0:
                self.preset_combo.setCurrentIndex(index)
        else:
            # Set to "Custom" if no preset matches
            self.preset_combo.setCurrentIndex(0)  # "Custom" is first item

        # Reconnect the signal
        self.preset_combo.currentTextChanged.connect(self._on_preset_selected)

        # Load values into UI controls
        self.scrollback_spin.setValue(self.current_config.get("scrollback", 1000))
        self.tab_width_spin.setValue(self.current_config.get("tabStopWidth", 4))

        cursor_style = self.current_config.get("cursorStyle", "block")
        index = self.cursor_style_combo.findText(cursor_style)
        if index >= 0:
            self.cursor_style_combo.setCurrentIndex(index)

        self.cursor_blink_check.setChecked(self.current_config.get("cursorBlink", True))

        self.scroll_sensitivity_spin.setValue(self.current_config.get("scrollSensitivity", 1))
        self.fast_scroll_sensitivity_spin.setValue(
            self.current_config.get("fastScrollSensitivity", 5)
        )

        fast_scroll_mod = self.current_config.get("fastScrollModifier", "shift")
        index = self.fast_scroll_modifier_combo.findText(fast_scroll_mod)
        if index >= 0:
            self.fast_scroll_modifier_combo.setCurrentIndex(index)

        bell_style = self.current_config.get("bellStyle", "none")
        index = self.bell_style_combo.findText(bell_style)
        if index >= 0:
            self.bell_style_combo.setCurrentIndex(index)

        self.right_click_word_check.setChecked(
            self.current_config.get("rightClickSelectsWord", False)
        )
        self.convert_eol_check.setChecked(self.current_config.get("convertEol", False))

    def _save_config(self) -> None:
        """Save UI values to configuration dictionary."""
        self.current_config = {
            "scrollback": self.scrollback_spin.value(),
            "tabStopWidth": self.tab_width_spin.value(),
            "cursorStyle": self.cursor_style_combo.currentText(),
            "cursorBlink": self.cursor_blink_check.isChecked(),
            "scrollSensitivity": self.scroll_sensitivity_spin.value(),
            "fastScrollSensitivity": self.fast_scroll_sensitivity_spin.value(),
            "fastScrollModifier": self.fast_scroll_modifier_combo.currentText(),
            "bellStyle": self.bell_style_combo.currentText(),
            "rightClickSelectsWord": self.right_click_word_check.isChecked(),
            "convertEol": self.convert_eol_check.isChecked(),
        }

    def _reset_to_defaults(self) -> None:
        """Reset all preferences to default values."""
        self.current_config = self._get_defaults()
        self._load_config()
        logger.info("Reset terminal preferences to defaults")

    def _find_matching_preset(self) -> Optional[str]:
        """Find which preset matches the current configuration.

        Returns:
            Preset name if a match is found, None otherwise
        """
        for preset_name in presets.list_presets():
            try:
                preset_config = presets.get_config(preset_name)
                if preset_config == self.current_config:
                    return preset_name
            except KeyError:
                continue
        return None

    def _on_value_changed(self) -> None:
        """Handle manual value changes - switch to 'Custom' preset."""
        # When user manually changes a value, switch combo to "Custom"
        # (but only if it's not already on Custom)
        if self.preset_combo.currentText() != "Custom":
            # Temporarily disconnect to avoid triggering preset load
            self.preset_combo.currentTextChanged.disconnect(self._on_preset_selected)
            self.preset_combo.setCurrentIndex(0)  # Set to "Custom"
            self.preset_combo.currentTextChanged.connect(self._on_preset_selected)

    def _on_preset_selected(self, preset_name: str) -> None:
        """Handle preset selection from combo box.

        Args:
            preset_name: Name of the selected preset
        """
        if not preset_name or preset_name == "Custom":
            return

        try:
            config = presets.get_config(preset_name)
            self.current_config = config
            self._load_config()
            logger.info(f"Loaded '{preset_name}' preset")
        except KeyError as e:
            logger.error(f"Failed to load preset: {e}")

    def on_apply(self) -> None:
        """Handle Apply button click."""
        self._save_config()
        self.preferencesApplied.emit(self.current_config)
        logger.info(f"Applied terminal preferences: {self.current_config}")

    def on_ok(self) -> None:
        """Handle OK button click."""
        self.on_apply()
        self.accept()

    def get_config(self) -> dict:
        """Get the current configuration.

        Returns:
            Dictionary with current terminal preferences
        """
        return self.current_config.copy()
