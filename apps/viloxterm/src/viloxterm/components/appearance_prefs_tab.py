"""Appearance preferences tab for ViloxTerm.

Handles theme, window appearance, and UI customization settings.
"""

import logging
from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QVBoxLayout,
)
from PySide6.QtCore import Qt

from vfwidgets_theme import ThemedQWidget

from ..models.preferences_model import AppearancePreferences

logger = logging.getLogger(__name__)


class AppearancePreferencesTab(ThemedQWidget):
    """Tab widget for appearance preferences."""

    def __init__(self, parent=None):
        """Initialize the appearance preferences tab.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self._preferences: AppearancePreferences = AppearancePreferences()
        self._setup_ui()

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
        container_layout.addWidget(self._create_theme_group())
        container_layout.addWidget(self._create_window_group())
        container_layout.addWidget(self._create_ui_elements_group())
        container_layout.addWidget(self._create_focus_indicators_group())

        container_layout.addStretch()

        scroll.setWidget(container)
        layout.addWidget(scroll)

    def _create_theme_group(self) -> QGroupBox:
        """Create the theme settings group.

        Returns:
            QGroupBox with theme settings
        """
        group = QGroupBox("Theme")
        layout = QFormLayout(group)

        # Application theme
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light", "Default", "Minimal"])
        layout.addRow("Application theme:", self.theme_combo)

        # Sync with system
        self.sync_system_check = QCheckBox("Sync with system theme (when available)")
        layout.addRow("", self.sync_system_check)

        # Custom theme path
        theme_path_layout = QHBoxLayout()
        self.custom_theme_edit = QLineEdit()
        self.custom_theme_edit.setPlaceholderText("Path to custom theme file")
        theme_path_layout.addWidget(self.custom_theme_edit)

        browse_theme_btn = QPushButton("Browse...")
        browse_theme_btn.setMaximumWidth(100)
        browse_theme_btn.clicked.connect(self._browse_theme)
        theme_path_layout.addWidget(browse_theme_btn)

        layout.addRow("Custom theme:", theme_path_layout)

        return group

    def _create_window_group(self) -> QGroupBox:
        """Create the window appearance settings group.

        Returns:
            QGroupBox with window settings
        """
        group = QGroupBox("Window")
        layout = QFormLayout(group)

        # Window opacity
        opacity_layout = QHBoxLayout()
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(10, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.opacity_slider.setTickInterval(10)
        self.opacity_slider.valueChanged.connect(self._on_opacity_changed)
        opacity_layout.addWidget(self.opacity_slider)

        self.opacity_label = QLabel("100%")
        self.opacity_label.setMinimumWidth(50)
        self.opacity_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        opacity_layout.addWidget(self.opacity_label)

        layout.addRow("Window opacity:", opacity_layout)

        # Background blur
        self.bg_blur_check = QCheckBox("Background blur (when supported)")
        layout.addRow("", self.bg_blur_check)

        # Window padding
        self.window_padding_spin = QSpinBox()
        self.window_padding_spin.setRange(0, 20)
        self.window_padding_spin.setSuffix(" px")
        layout.addRow("Window padding:", self.window_padding_spin)

        return group

    def _create_ui_elements_group(self) -> QGroupBox:
        """Create the UI elements settings group.

        Returns:
            QGroupBox with UI element settings
        """
        group = QGroupBox("UI Elements")
        layout = QFormLayout(group)

        # Tab bar position
        self.tab_bar_position_combo = QComboBox()
        self.tab_bar_position_combo.addItems(["Top", "Bottom"])
        layout.addRow("Tab bar position:", self.tab_bar_position_combo)

        # Show menu button
        self.show_menu_btn_check = QCheckBox("Show menu button in title bar")
        layout.addRow("", self.show_menu_btn_check)

        # Show window title
        self.show_title_check = QCheckBox("Show window title")
        layout.addRow("", self.show_title_check)

        # UI font size
        self.ui_font_size_spin = QSpinBox()
        self.ui_font_size_spin.setRange(6, 24)
        self.ui_font_size_spin.setSuffix(" pt")
        layout.addRow("UI font size:", self.ui_font_size_spin)

        return group

    def _create_focus_indicators_group(self) -> QGroupBox:
        """Create the focus indicators settings group.

        Returns:
            QGroupBox with focus indicator settings
        """
        group = QGroupBox("Focus Indicators")
        layout = QFormLayout(group)

        # Focus border width
        self.focus_border_width_spin = QSpinBox()
        self.focus_border_width_spin.setRange(0, 10)
        self.focus_border_width_spin.setSuffix(" px")
        layout.addRow("Focus border width:", self.focus_border_width_spin)

        # Focus border color
        color_layout = QHBoxLayout()
        self.focus_color_edit = QLineEdit()
        self.focus_color_edit.setPlaceholderText("Theme default (empty = auto)")
        color_layout.addWidget(self.focus_color_edit)

        # TODO: Add color picker button
        # color_picker_btn = QPushButton("...")
        # color_picker_btn.setMaximumWidth(40)
        # color_layout.addWidget(color_picker_btn)

        layout.addRow("Focus border color:", color_layout)

        # Unfocused dim amount
        dim_layout = QHBoxLayout()
        self.unfocused_dim_slider = QSlider(Qt.Orientation.Horizontal)
        self.unfocused_dim_slider.setRange(0, 50)
        self.unfocused_dim_slider.setValue(0)
        self.unfocused_dim_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.unfocused_dim_slider.setTickInterval(10)
        self.unfocused_dim_slider.valueChanged.connect(self._on_dim_changed)
        dim_layout.addWidget(self.unfocused_dim_slider)

        self.dim_label = QLabel("0%")
        self.dim_label.setMinimumWidth(50)
        self.dim_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        dim_layout.addWidget(self.dim_label)

        layout.addRow("Unfocused pane dimming:", dim_layout)

        return group

    def _browse_theme(self) -> None:
        """Open file dialog to select custom theme file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Theme File",
            str(Path.home() / ".config" / "viloxterm"),
            "JSON Files (*.json);;All Files (*)",
        )

        if file_path:
            self.custom_theme_edit.setText(file_path)

    def _on_opacity_changed(self, value: int) -> None:
        """Handle opacity slider change.

        Args:
            value: Opacity value (10-100)
        """
        self.opacity_label.setText(f"{value}%")

    def _on_dim_changed(self, value: int) -> None:
        """Handle dim slider change.

        Args:
            value: Dim amount (0-50)
        """
        self.dim_label.setText(f"{value}%")

    def load_preferences(self, preferences: AppearancePreferences) -> None:
        """Load preferences into UI widgets.

        Args:
            preferences: AppearancePreferences to load
        """
        self._preferences = preferences

        # Theme
        theme_map = {"dark": 0, "light": 1, "default": 2, "minimal": 3}
        index = theme_map.get(preferences.application_theme.lower(), 0)
        self.theme_combo.setCurrentIndex(index)

        self.sync_system_check.setChecked(preferences.sync_with_system)
        self.custom_theme_edit.setText(preferences.custom_theme_path)

        # Window
        self.opacity_slider.setValue(preferences.window_opacity)
        self.bg_blur_check.setChecked(preferences.background_blur)
        self.window_padding_spin.setValue(preferences.window_padding)

        # UI Elements
        pos_map = {"top": 0, "bottom": 1}
        pos_index = pos_map.get(preferences.tab_bar_position.lower(), 0)
        self.tab_bar_position_combo.setCurrentIndex(pos_index)

        self.show_menu_btn_check.setChecked(preferences.show_menu_button)
        self.show_title_check.setChecked(preferences.show_window_title)
        self.ui_font_size_spin.setValue(preferences.ui_font_size)

        # Focus Indicators
        self.focus_border_width_spin.setValue(preferences.focus_border_width)
        self.focus_color_edit.setText(preferences.focus_border_color)
        self.unfocused_dim_slider.setValue(preferences.unfocused_dim_amount)

    def save_preferences(self) -> AppearancePreferences:
        """Save UI values to preferences model.

        Returns:
            AppearancePreferences with current UI values
        """
        # Theme
        theme_values = ["dark", "light", "default", "minimal"]
        self._preferences.application_theme = theme_values[self.theme_combo.currentIndex()]
        self._preferences.sync_with_system = self.sync_system_check.isChecked()
        self._preferences.custom_theme_path = self.custom_theme_edit.text()

        # Window
        self._preferences.window_opacity = self.opacity_slider.value()
        self._preferences.background_blur = self.bg_blur_check.isChecked()
        self._preferences.window_padding = self.window_padding_spin.value()

        # UI Elements
        pos_values = ["top", "bottom"]
        self._preferences.tab_bar_position = pos_values[self.tab_bar_position_combo.currentIndex()]
        self._preferences.show_menu_button = self.show_menu_btn_check.isChecked()
        self._preferences.show_window_title = self.show_title_check.isChecked()
        self._preferences.ui_font_size = self.ui_font_size_spin.value()

        # Focus Indicators
        self._preferences.focus_border_width = self.focus_border_width_spin.value()
        self._preferences.focus_border_color = self.focus_color_edit.text()
        self._preferences.unfocused_dim_amount = self.unfocused_dim_slider.value()

        return self._preferences
