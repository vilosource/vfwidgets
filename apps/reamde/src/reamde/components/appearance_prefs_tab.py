"""Appearance preferences tab for Reamde.

Handles theme, window appearance, and markdown rendering settings.
"""

import logging

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSlider,
    QSpinBox,
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

        # Create sections
        container_layout.addWidget(self._create_theme_group())
        container_layout.addWidget(self._create_window_group())
        container_layout.addWidget(self._create_markdown_rendering_group())

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
        self.theme_combo.addItems(["Dark", "Light", "Default"])
        layout.addRow("Application theme:", self.theme_combo)

        # Sync with system
        self.sync_system_check = QCheckBox("Sync with system theme (when available)")
        layout.addRow("", self.sync_system_check)

        return group

    def _create_window_group(self) -> QGroupBox:
        """Create the window settings group.

        Returns:
            QGroupBox with window settings
        """
        group = QGroupBox("Window")
        layout = QFormLayout(group)

        # Window opacity with slider and label
        opacity_container = QHBoxLayout()

        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(10, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.opacity_slider.setTickInterval(10)
        opacity_container.addWidget(self.opacity_slider)

        self.opacity_label = QLabel("100%")
        self.opacity_label.setMinimumWidth(50)
        opacity_container.addWidget(self.opacity_label)

        # Connect slider to label
        self.opacity_slider.valueChanged.connect(lambda v: self.opacity_label.setText(f"{v}%"))

        layout.addRow("Window opacity:", opacity_container)

        return group

    def _create_markdown_rendering_group(self) -> QGroupBox:
        """Create the markdown rendering settings group.

        Returns:
            QGroupBox with markdown rendering settings
        """
        group = QGroupBox("Markdown Rendering")
        layout = QFormLayout(group)

        # Font family (empty = default)
        self.font_family_combo = QComboBox()
        self.font_family_combo.setEditable(False)
        self.font_family_combo.addItem("Default")
        # TODO: Add system fonts
        layout.addRow("Font family:", self.font_family_combo)

        # Font size
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 72)
        self.font_size_spin.setValue(16)
        self.font_size_spin.setSuffix(" pt")
        layout.addRow("Font size:", self.font_size_spin)

        # Line height with slider and label
        line_height_container = QHBoxLayout()

        self.line_height_spin = QDoubleSpinBox()
        self.line_height_spin.setRange(1.0, 3.0)
        self.line_height_spin.setSingleStep(0.1)
        self.line_height_spin.setValue(1.6)
        self.line_height_spin.setDecimals(1)
        line_height_container.addWidget(self.line_height_spin)

        layout.addRow("Line height:", line_height_container)

        # Max content width
        self.max_width_spin = QSpinBox()
        self.max_width_spin.setRange(0, 2000)
        self.max_width_spin.setValue(800)
        self.max_width_spin.setSuffix(" px")
        self.max_width_spin.setSpecialValueText("Full width")
        layout.addRow("Max content width:", self.max_width_spin)

        return group

    def load_preferences(self, preferences: AppearancePreferences) -> None:
        """Load preferences into UI.

        Args:
            preferences: AppearancePreferences to load
        """
        self._preferences = preferences

        # Theme
        theme_index = {"dark": 0, "light": 1, "default": 2}.get(
            preferences.application_theme.lower(), 0
        )
        self.theme_combo.setCurrentIndex(theme_index)
        self.sync_system_check.setChecked(preferences.sync_with_system)

        # Window
        self.opacity_slider.setValue(preferences.window_opacity)

        # Markdown Rendering
        # Font family (default = index 0)
        if preferences.font_family:
            # TODO: Find and set the font family
            pass
        else:
            self.font_family_combo.setCurrentIndex(0)

        self.font_size_spin.setValue(preferences.font_size)
        self.line_height_spin.setValue(preferences.line_height)
        self.max_width_spin.setValue(preferences.max_content_width)

    def save_preferences(self) -> AppearancePreferences:
        """Collect preferences from UI.

        Returns:
            AppearancePreferences with current UI values
        """
        # Theme
        theme_map = ["dark", "light", "default"]
        theme = theme_map[self.theme_combo.currentIndex()]

        # Font family
        font_family = ""
        if self.font_family_combo.currentIndex() > 0:
            font_family = self.font_family_combo.currentText()

        return AppearancePreferences(
            # Theme
            application_theme=theme,
            sync_with_system=self.sync_system_check.isChecked(),
            # Window
            window_opacity=self.opacity_slider.value(),
            # Markdown Rendering
            font_family=font_family,
            font_size=self.font_size_spin.value(),
            line_height=self.line_height_spin.value(),
            max_content_width=self.max_width_spin.value(),
        )
