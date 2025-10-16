"""Preferences dialog for Reamde.

Provides a tabbed interface for all application settings.
"""

import logging
from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from vfwidgets_theme import ThemedDialog, ThemedQWidget

from ..models.preferences_model import PreferencesModel
from ..preferences_manager import PreferencesManager
from .appearance_prefs_tab import AppearancePreferencesTab
from .general_prefs_tab import GeneralPreferencesTab
from .markdown_prefs_tab import MarkdownPreferencesTab

logger = logging.getLogger(__name__)


class PreferencesDialog(ThemedDialog):
    """Preferences dialog with tabbed interface.

    Combines all Reamde settings into a single dialog:
    - General (startup, window behavior, session)
    - Appearance (theme, window, markdown rendering)
    - Markdown (rendering features, behavior)
    """

    # Signal emitted when user clicks Apply or OK
    preferences_applied = Signal(PreferencesModel)

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize preferences dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Preferences manager
        self.prefs_manager = PreferencesManager()

        # Current preferences
        self.preferences = self.prefs_manager.load_preferences()

        self.setWindowTitle("Preferences")
        self.resize(700, 600)

        self._setup_ui()
        self._load_preferences()

    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget, 1)

        # Create tabs (placeholders for now)
        self._create_tabs()

        # Bottom button bar
        bottom_bar = self._create_bottom_bar()
        layout.addWidget(bottom_bar, 0)

    def _create_tabs(self) -> None:
        """Create preference tabs."""
        # General tab
        self.general_tab = GeneralPreferencesTab()
        self.tab_widget.addTab(self.general_tab, "General")

        # Appearance tab
        self.appearance_tab = AppearancePreferencesTab()
        self.tab_widget.addTab(self.appearance_tab, "Appearance")

        # Markdown tab
        self.markdown_tab = MarkdownPreferencesTab()
        self.tab_widget.addTab(self.markdown_tab, "Markdown")

    def _create_bottom_bar(self) -> ThemedQWidget:
        """Create the bottom button bar.

        Returns:
            ThemedQWidget containing Apply/OK/Cancel buttons
        """
        bottom_bar = ThemedQWidget()
        layout = QHBoxLayout(bottom_bar)
        layout.setContentsMargins(10, 10, 10, 10)

        # Stretch to push buttons right
        layout.addStretch()

        # Apply button
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.on_apply)
        layout.addWidget(self.apply_button)

        # OK button
        self.ok_button = QPushButton("OK")
        self.ok_button.setDefault(True)
        self.ok_button.clicked.connect(self.on_ok)
        layout.addWidget(self.ok_button)

        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        layout.addWidget(self.cancel_button)

        return bottom_bar

    def _load_preferences(self) -> None:
        """Load current preferences into UI."""
        # Load preferences into each tab
        self.general_tab.load_preferences(self.preferences.general)
        self.appearance_tab.load_preferences(self.preferences.appearance)
        self.markdown_tab.load_preferences(self.preferences.markdown)

    def _save_preferences(self) -> bool:
        """Collect preferences from UI and save.

        Returns:
            True if saved successfully
        """
        # Collect preferences from each tab
        self.preferences.general = self.general_tab.save_preferences()
        self.preferences.appearance = self.appearance_tab.save_preferences()
        self.preferences.markdown = self.markdown_tab.save_preferences()

        # Save to disk
        return self.prefs_manager.save_preferences(self.preferences)

    def on_apply(self) -> None:
        """Handle Apply button click."""
        if self._save_preferences():
            # Emit signal for live application
            self.preferences_applied.emit(self.preferences)
            logger.info("Preferences applied")

    def on_ok(self) -> None:
        """Handle OK button click."""
        if self._save_preferences():
            # Emit signal for live application
            self.preferences_applied.emit(self.preferences)
            self.accept()
