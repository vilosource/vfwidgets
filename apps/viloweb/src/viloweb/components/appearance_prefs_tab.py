"""Appearance preferences tab for ViloxWeb.

Handles theme, window appearance, and UI customization settings.
"""

import logging
from pathlib import Path

from PySide6.QtCore import Qt
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
    QVBoxLayout,
)

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

        # Top bar background color
        color_layout = QHBoxLayout()
        self.top_bar_color_edit = QLineEdit()
        self.top_bar_color_edit.setPlaceholderText("Theme default (empty = auto)")
        self.top_bar_color_edit.setMaximumWidth(150)
        color_layout.addWidget(self.top_bar_color_edit)

        pick_color_btn = QPushButton("Pick Color...")
        pick_color_btn.setMaximumWidth(120)
        pick_color_btn.clicked.connect(self._pick_top_bar_color)
        color_layout.addWidget(pick_color_btn)

        clear_color_btn = QPushButton("Reset")
        clear_color_btn.setMaximumWidth(80)
        clear_color_btn.clicked.connect(lambda: self.top_bar_color_edit.setText(""))
        color_layout.addWidget(clear_color_btn)

        layout.addRow("Top bar background:", color_layout)

        # Accent line below tab bar
        self.show_accent_line_check = QCheckBox("Show accent line below tab bar")
        self.show_accent_line_check.setChecked(True)
        self.show_accent_line_check.stateChanged.connect(self._on_accent_line_toggled)
        layout.addRow("", self.show_accent_line_check)

        # Accent line color
        accent_color_layout = QHBoxLayout()
        self.accent_line_color_edit = QLineEdit()
        self.accent_line_color_edit.setPlaceholderText("Active tab color (empty = auto)")
        self.accent_line_color_edit.setMaximumWidth(150)
        accent_color_layout.addWidget(self.accent_line_color_edit)

        pick_accent_color_btn = QPushButton("Pick Color...")
        pick_accent_color_btn.setMaximumWidth(120)
        pick_accent_color_btn.clicked.connect(self._pick_accent_line_color)
        accent_color_layout.addWidget(pick_accent_color_btn)

        clear_accent_color_btn = QPushButton("Reset")
        clear_accent_color_btn.setMaximumWidth(80)
        clear_accent_color_btn.clicked.connect(lambda: self.accent_line_color_edit.setText(""))
        accent_color_layout.addWidget(clear_accent_color_btn)

        layout.addRow("Accent line color:", accent_color_layout)

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

        return group

    def _browse_theme(self) -> None:
        """Open file dialog to browse for custom theme."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Theme File", str(Path.home()), "JSON Files (*.json)"
        )

        if file_path:
            self.custom_theme_edit.setText(file_path)

    def _pick_top_bar_color(self) -> None:
        """Open color picker for top bar background."""
        from PySide6.QtWidgets import QColorDialog
        from PySide6.QtGui import QColor

        # Get current color if set
        current_text = self.top_bar_color_edit.text()
        initial_color = QColor(current_text) if current_text else QColor(30, 30, 30)

        # Show color dialog
        color = QColorDialog.getColor(initial_color, self, "Pick Top Bar Background Color")

        if color.isValid():
            # Format as #RRGGBB
            self.top_bar_color_edit.setText(color.name())

    def _pick_accent_line_color(self) -> None:
        """Open color picker for accent line."""
        from PySide6.QtGui import QColor
        from PySide6.QtWidgets import QColorDialog

        # Get current color if set
        current_text = self.accent_line_color_edit.text()
        initial_color = QColor(current_text) if current_text else QColor(0, 120, 215)

        # Show color dialog
        color = QColorDialog.getColor(initial_color, self, "Pick Accent Line Color")

        if color.isValid():
            # Format as #RRGGBB
            self.accent_line_color_edit.setText(color.name())

    def _on_accent_line_toggled(self, state: int) -> None:
        """Handle accent line checkbox toggle.

        Args:
            state: Qt.CheckState value
        """
        enabled = state == Qt.CheckState.Checked.value
        self.accent_line_color_edit.setEnabled(enabled)

    def _on_opacity_changed(self, value: int) -> None:
        """Handle opacity slider change.

        Args:
            value: Opacity value (10-100)
        """
        self.opacity_label.setText(f"{value}%")

    def load_preferences(self, prefs: AppearancePreferences) -> None:
        """Load preferences into UI controls.

        Args:
            prefs: AppearancePreferences to load
        """
        self._preferences = prefs

        # Theme
        theme_map = {"dark": 0, "light": 1, "default": 2, "minimal": 3}
        self.theme_combo.setCurrentIndex(theme_map.get(prefs.application_theme.lower(), 0))
        self.sync_system_check.setChecked(prefs.sync_with_system)
        self.custom_theme_edit.setText(prefs.custom_theme_path)

        # Colors
        self.top_bar_color_edit.setText(prefs.top_bar_background_color)
        self.accent_line_color_edit.setText(prefs.accent_line_color)
        self.show_accent_line_check.setChecked(prefs.show_accent_line)

        # Window
        self.opacity_slider.setValue(prefs.window_opacity)
        self.opacity_label.setText(f"{prefs.window_opacity}%")

    def save_preferences(self) -> AppearancePreferences:
        """Save UI values to preferences model.

        Returns:
            AppearancePreferences with current values
        """
        theme_names = ["dark", "light", "default", "minimal"]
        theme = theme_names[self.theme_combo.currentIndex()]

        self._preferences.application_theme = theme
        self._preferences.sync_with_system = self.sync_system_check.isChecked()
        self._preferences.custom_theme_path = self.custom_theme_edit.text()
        self._preferences.top_bar_background_color = self.top_bar_color_edit.text()
        self._preferences.accent_line_color = self.accent_line_color_edit.text()
        self._preferences.show_accent_line = self.show_accent_line_check.isChecked()
        self._preferences.window_opacity = self.opacity_slider.value()

        return self._preferences
