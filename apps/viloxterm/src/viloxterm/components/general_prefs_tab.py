"""General preferences tab for ViloxTerm.

Handles startup, window behavior, and session management settings.
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
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
)

from vfwidgets_theme import ThemedQWidget

from ..models.preferences_model import GeneralPreferences

logger = logging.getLogger(__name__)


class GeneralPreferencesTab(ThemedQWidget):
    """Tab widget for general application preferences."""

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

        # Create preference sections
        container_layout.addWidget(self._create_startup_group())
        container_layout.addWidget(self._create_window_behavior_group())
        container_layout.addWidget(self._create_session_management_group())

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

        # Restore session
        self.restore_session_check = QCheckBox("Restore previous session on startup")
        layout.addRow("", self.restore_session_check)

        # Tabs on startup
        self.tabs_on_startup_spin = QSpinBox()
        self.tabs_on_startup_spin.setRange(1, 20)
        self.tabs_on_startup_spin.setSuffix(" tabs")
        layout.addRow("Open on startup:", self.tabs_on_startup_spin)

        # Default shell
        shell_layout = QHBoxLayout()
        self.default_shell_edit = QLineEdit()
        self.default_shell_edit.setPlaceholderText("System default")
        shell_layout.addWidget(self.default_shell_edit)

        browse_shell_btn = QPushButton("Browse...")
        browse_shell_btn.setMaximumWidth(100)
        browse_shell_btn.clicked.connect(self._browse_shell)
        shell_layout.addWidget(browse_shell_btn)

        layout.addRow("Default shell:", shell_layout)

        # Starting directory
        self.starting_dir_combo = QComboBox()
        self.starting_dir_combo.addItems(
            ["Home directory", "Last used directory", "Custom directory"]
        )
        self.starting_dir_combo.currentIndexChanged.connect(self._on_starting_dir_changed)
        layout.addRow("Starting directory:", self.starting_dir_combo)

        # Custom directory
        custom_dir_layout = QHBoxLayout()
        self.custom_dir_edit = QLineEdit()
        self.custom_dir_edit.setPlaceholderText("/path/to/directory")
        self.custom_dir_edit.setEnabled(False)
        custom_dir_layout.addWidget(self.custom_dir_edit)

        browse_dir_btn = QPushButton("Browse...")
        browse_dir_btn.setMaximumWidth(100)
        browse_dir_btn.clicked.connect(self._browse_directory)
        browse_dir_btn.setEnabled(False)
        self.browse_dir_btn = browse_dir_btn
        custom_dir_layout.addWidget(browse_dir_btn)

        layout.addRow("Custom directory:", custom_dir_layout)

        return group

    def _create_window_behavior_group(self) -> QGroupBox:
        """Create the window behavior settings group.

        Returns:
            QGroupBox with window behavior settings
        """
        group = QGroupBox("Window Behavior")
        layout = QFormLayout(group)

        # Close on last tab
        self.close_on_last_tab_check = QCheckBox("Close window when last tab closes")
        layout.addRow("", self.close_on_last_tab_check)

        # Confirm close multiple tabs
        self.confirm_close_check = QCheckBox("Confirm before closing multiple tabs")
        layout.addRow("", self.confirm_close_check)

        # Show tab bar with single tab
        self.show_tab_bar_check = QCheckBox("Show tab bar when only one tab exists")
        layout.addRow("", self.show_tab_bar_check)

        # Frameless window
        self.frameless_window_check = QCheckBox("Use frameless window (Chrome-style)")
        layout.addRow("", self.frameless_window_check)

        return group

    def _create_session_management_group(self) -> QGroupBox:
        """Create the session management settings group.

        Returns:
            QGroupBox with session management settings
        """
        group = QGroupBox("Session Management")
        layout = QFormLayout(group)

        # Save tab layout
        self.save_tab_layout_check = QCheckBox("Save and restore tab layout")
        layout.addRow("", self.save_tab_layout_check)

        # Save working directories
        self.save_working_dirs_check = QCheckBox("Save and restore working directories")
        layout.addRow("", self.save_working_dirs_check)

        return group

    def _browse_shell(self) -> None:
        """Open file dialog to select shell executable."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Shell Executable",
            "/bin",
            "Executables (*)",
        )

        if file_path:
            self.default_shell_edit.setText(file_path)

    def _browse_directory(self) -> None:
        """Open directory dialog to select custom starting directory."""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select Starting Directory",
            str(Path.home()),
        )

        if dir_path:
            self.custom_dir_edit.setText(dir_path)

    def _on_starting_dir_changed(self, index: int) -> None:
        """Handle starting directory combo box change.

        Args:
            index: Selected index (0=home, 1=last, 2=custom)
        """
        is_custom = index == 2
        self.custom_dir_edit.setEnabled(is_custom)
        self.browse_dir_btn.setEnabled(is_custom)

    def load_preferences(self, preferences: GeneralPreferences) -> None:
        """Load preferences into UI widgets.

        Args:
            preferences: GeneralPreferences to load
        """
        self._preferences = preferences

        # Startup
        self.restore_session_check.setChecked(preferences.restore_session)
        self.tabs_on_startup_spin.setValue(preferences.tabs_on_startup)
        self.default_shell_edit.setText(preferences.default_shell)

        # Starting directory
        dir_map = {"home": 0, "last": 1, "custom": 2}
        index = dir_map.get(preferences.starting_directory, 0)
        self.starting_dir_combo.setCurrentIndex(index)
        self.custom_dir_edit.setText(preferences.custom_directory)

        # Window behavior
        self.close_on_last_tab_check.setChecked(preferences.close_on_last_tab)
        self.confirm_close_check.setChecked(preferences.confirm_close_multiple_tabs)
        self.show_tab_bar_check.setChecked(preferences.show_tab_bar_single_tab)
        self.frameless_window_check.setChecked(preferences.frameless_window)

        # Session management
        self.save_tab_layout_check.setChecked(preferences.save_tab_layout)
        self.save_working_dirs_check.setChecked(preferences.save_working_directories)

    def save_preferences(self) -> GeneralPreferences:
        """Save UI values to preferences model.

        Returns:
            GeneralPreferences with current UI values
        """
        # Startup
        self._preferences.restore_session = self.restore_session_check.isChecked()
        self._preferences.tabs_on_startup = self.tabs_on_startup_spin.value()
        self._preferences.default_shell = self.default_shell_edit.text()

        # Starting directory
        dir_values = ["home", "last", "custom"]
        self._preferences.starting_directory = dir_values[self.starting_dir_combo.currentIndex()]
        self._preferences.custom_directory = self.custom_dir_edit.text()

        # Window behavior
        self._preferences.close_on_last_tab = self.close_on_last_tab_check.isChecked()
        self._preferences.confirm_close_multiple_tabs = self.confirm_close_check.isChecked()
        self._preferences.show_tab_bar_single_tab = self.show_tab_bar_check.isChecked()
        self._preferences.frameless_window = self.frameless_window_check.isChecked()

        # Session management
        self._preferences.save_tab_layout = self.save_tab_layout_check.isChecked()
        self._preferences.save_working_directories = self.save_working_dirs_check.isChecked()

        return self._preferences
