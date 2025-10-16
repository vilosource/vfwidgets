"""General preferences tab for Reamde.

Handles startup, window behavior, and session management settings.
"""

import logging

from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
)
from vfwidgets_theme import ThemedQWidget

from ..models.preferences_model import GeneralPreferences

logger = logging.getLogger(__name__)


class GeneralPreferencesTab(ThemedQWidget):
    """Tab widget for general preferences."""

    def __init__(self, parent=None):
        """Initialize the general preferences tab.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self._preferences: GeneralPreferences = GeneralPreferences()
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
        container_layout.addWidget(self._create_startup_group())
        container_layout.addWidget(self._create_window_behavior_group())

        container_layout.addStretch()

        scroll.setWidget(container)
        layout.addWidget(scroll)

    def _create_startup_group(self) -> QGroupBox:
        """Create the startup settings group.

        Returns:
            QGroupBox with startup settings
        """
        group = QGroupBox("Startup")
        layout = QFormLayout(group)

        # Restore previous session
        self.restore_session_check = QCheckBox("Restore previous session on startup")
        layout.addRow("", self.restore_session_check)

        # Max recent files
        self.max_recent_spin = QSpinBox()
        self.max_recent_spin.setRange(1, 100)
        layout.addRow("Maximum recent files:", self.max_recent_spin)

        return group

    def _create_window_behavior_group(self) -> QGroupBox:
        """Create the window behavior settings group.

        Returns:
            QGroupBox with window behavior settings
        """
        group = QGroupBox("Window Behavior")
        layout = QFormLayout(group)

        # Confirm close multiple tabs
        self.confirm_close_check = QCheckBox("Confirm before closing window with multiple tabs")
        layout.addRow("", self.confirm_close_check)

        # Show tab bar with single tab
        self.show_tab_bar_check = QCheckBox("Show tab bar when only one tab is open")
        layout.addRow("", self.show_tab_bar_check)

        return group

    def load_preferences(self, preferences: GeneralPreferences) -> None:
        """Load preferences into UI.

        Args:
            preferences: GeneralPreferences to load
        """
        self._preferences = preferences

        # Startup
        self.restore_session_check.setChecked(preferences.restore_previous_session)
        self.max_recent_spin.setValue(preferences.max_recent_files)

        # Window Behavior
        self.confirm_close_check.setChecked(preferences.confirm_close_multiple_tabs)
        self.show_tab_bar_check.setChecked(preferences.show_tab_bar_single_tab)

    def save_preferences(self) -> GeneralPreferences:
        """Collect preferences from UI.

        Returns:
            GeneralPreferences with current UI values
        """
        return GeneralPreferences(
            # Startup
            restore_previous_session=self.restore_session_check.isChecked(),
            max_recent_files=self.max_recent_spin.value(),
            # Window Behavior
            confirm_close_multiple_tabs=self.confirm_close_check.isChecked(),
            show_tab_bar_single_tab=self.show_tab_bar_check.isChecked(),
        )
