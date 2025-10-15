"""Advanced preferences tab for ViloxTerm.

Handles performance settings and experimental features.
"""

import logging

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QScrollArea,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
)

from vfwidgets_theme import ThemedQWidget

from ..models.preferences_model import AdvancedPreferences

logger = logging.getLogger(__name__)


class AdvancedPreferencesTab(ThemedQWidget):
    """Tab widget for advanced preferences.

    Contains performance settings and experimental features.
    """

    def __init__(self, parent=None):
        """Initialize the advanced preferences tab.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self._preferences: AdvancedPreferences = AdvancedPreferences()
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
        container_layout.addWidget(self._create_performance_group())
        container_layout.addWidget(self._create_behavior_group())
        container_layout.addWidget(self._create_experimental_group())

        container_layout.addStretch()

        scroll.setWidget(container)
        layout.addWidget(scroll)

    def _create_performance_group(self) -> QGroupBox:
        """Create the performance settings group.

        Returns:
            QGroupBox with performance settings
        """
        group = QGroupBox("Performance")
        layout = QFormLayout(group)

        # Hardware acceleration
        self.hw_accel_combo = QComboBox()
        self.hw_accel_combo.addItems(["Auto", "On", "Off"])
        layout.addRow("Hardware acceleration:", self.hw_accel_combo)

        # WebEngine cache size
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(0, 500)
        self.cache_size_spin.setSuffix(" MB")
        layout.addRow("WebEngine cache size:", self.cache_size_spin)

        # Maximum tabs
        self.max_tabs_spin = QSpinBox()
        self.max_tabs_spin.setRange(1, 1000)
        layout.addRow("Maximum tabs:", self.max_tabs_spin)

        # Terminal renderer
        self.renderer_combo = QComboBox()
        self.renderer_combo.addItems(["Auto", "Canvas", "DOM", "WebGL"])
        layout.addRow("Terminal renderer:", self.renderer_combo)

        return group

    def _create_behavior_group(self) -> QGroupBox:
        """Create the behavior settings group.

        Returns:
            QGroupBox with behavior settings
        """
        group = QGroupBox("Behavior")
        layout = QFormLayout(group)

        # Enable animations
        self.animations_check = QCheckBox("Enable UI animations")
        layout.addRow("", self.animations_check)

        # Terminal server port
        self.server_port_spin = QSpinBox()
        self.server_port_spin.setRange(0, 65535)
        self.server_port_spin.setSpecialValueText("Auto")
        layout.addRow("Terminal server port:", self.server_port_spin)

        # Log level
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        layout.addRow("Log level:", self.log_level_combo)

        return group

    def _create_experimental_group(self) -> QGroupBox:
        """Create the experimental features group.

        Returns:
            QGroupBox with experimental settings
        """
        group = QGroupBox("Experimental Features")
        layout = QFormLayout(group)

        # Warning label
        warning_label = QLabel("⚠️ Warning: These features are experimental and may be unstable.")
        warning_label.setStyleSheet("color: #ff9800; font-weight: bold;")
        warning_label.setWordWrap(True)
        layout.addRow("", warning_label)

        # Ligature support
        self.ligatures_check = QCheckBox("Enable font ligatures (requires font support)")
        layout.addRow("", self.ligatures_check)

        # GPU rendering
        self.gpu_rendering_check = QCheckBox("Enable GPU rendering (may cause issues)")
        layout.addRow("", self.gpu_rendering_check)

        # Custom CSS
        layout.addRow("", QLabel("Custom CSS (advanced users only):"))
        self.custom_css_edit = QTextEdit()
        self.custom_css_edit.setPlaceholderText("/* Enter custom CSS here */")
        self.custom_css_edit.setMaximumHeight(100)
        layout.addRow("", self.custom_css_edit)

        return group

    def load_preferences(self, preferences: AdvancedPreferences) -> None:
        """Load preferences into UI widgets.

        Args:
            preferences: AdvancedPreferences to load
        """
        self._preferences = preferences

        # Performance
        accel_map = {"auto": 0, "on": 1, "off": 2}
        index = accel_map.get(preferences.hardware_acceleration.lower(), 0)
        self.hw_accel_combo.setCurrentIndex(index)

        self.cache_size_spin.setValue(preferences.webengine_cache_size)
        self.max_tabs_spin.setValue(preferences.max_tabs)

        renderer_map = {"auto": 0, "canvas": 1, "dom": 2, "webgl": 3}
        renderer_index = renderer_map.get(preferences.terminal_renderer.lower(), 0)
        self.renderer_combo.setCurrentIndex(renderer_index)

        # Behavior
        self.animations_check.setChecked(preferences.enable_animations)
        self.server_port_spin.setValue(preferences.terminal_server_port)

        log_index = self.log_level_combo.findText(preferences.log_level.upper())
        if log_index >= 0:
            self.log_level_combo.setCurrentIndex(log_index)

        # Experimental
        self.ligatures_check.setChecked(preferences.ligature_support)
        self.gpu_rendering_check.setChecked(preferences.gpu_rendering)
        self.custom_css_edit.setPlainText(preferences.custom_css)

    def save_preferences(self) -> AdvancedPreferences:
        """Save UI values to preferences model.

        Returns:
            AdvancedPreferences with current UI values
        """
        # Performance
        accel_values = ["auto", "on", "off"]
        self._preferences.hardware_acceleration = accel_values[self.hw_accel_combo.currentIndex()]
        self._preferences.webengine_cache_size = self.cache_size_spin.value()
        self._preferences.max_tabs = self.max_tabs_spin.value()

        renderer_values = ["auto", "canvas", "dom", "webgl"]
        self._preferences.terminal_renderer = renderer_values[self.renderer_combo.currentIndex()]

        # Behavior
        self._preferences.enable_animations = self.animations_check.isChecked()
        self._preferences.terminal_server_port = self.server_port_spin.value()
        self._preferences.log_level = self.log_level_combo.currentText()

        # Experimental
        self._preferences.ligature_support = self.ligatures_check.isChecked()
        self._preferences.gpu_rendering = self.gpu_rendering_check.isChecked()
        self._preferences.custom_css = self.custom_css_edit.toPlainText()

        return self._preferences
