"""Preferences dialog for ViloxWeb.

Provides a dialog interface for application settings.
"""

import logging

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from vfwidgets_theme import ThemedDialog, ThemedQWidget

from ..models.preferences_model import PreferencesModel
from ..preferences_manager import PreferencesManager
from .appearance_prefs_tab import AppearancePreferencesTab

logger = logging.getLogger(__name__)


class PreferencesDialog(ThemedDialog):
    """Preferences dialog for ViloxWeb.

    Provides a simple dialog for managing application preferences.
    Currently only has appearance settings.
    """

    # Signals
    preferences_applied = Signal(PreferencesModel)  # Emitted when preferences applied

    def __init__(self, parent: QWidget | None = None):
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
        self.resize(600, 500)

        self._setup_ui()
        self._load_preferences()

    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Appearance tab (main content)
        self.appearance_tab = AppearancePreferencesTab()
        layout.addWidget(self.appearance_tab, 1)

        # Bottom button bar
        bottom_bar = self._create_bottom_bar()
        layout.addWidget(bottom_bar, 0)

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

    def _load_preferences(self) -> None:
        """Load current preferences into UI."""
        self.appearance_tab.load_preferences(self.preferences.appearance)
        logger.debug("Loading preferences into dialog")

    def _save_preferences(self) -> None:
        """Save UI values to preference models."""
        self.preferences.appearance = self.appearance_tab.save_preferences()
        logger.debug("Saving preferences from dialog")

    def on_apply(self) -> None:
        """Handle Apply button click."""
        self._save_preferences()

        # Validate preferences
        errors = self.prefs_manager.validate_preferences(self.preferences)
        if errors:
            logger.warning(f"Preference validation errors: {errors}")
            # TODO: Show error dialog
            return

        # Save to disk
        self.prefs_manager.save_preferences(self.preferences)

        # Emit signal for live application
        self.preferences_applied.emit(self.preferences)

        logger.info("Applied and saved preferences")

    def on_ok(self) -> None:
        """Handle OK button click."""
        self.on_apply()
        self.accept()

    def get_preferences(self) -> PreferencesModel:
        """Get current preferences.

        Returns:
            PreferencesModel with current values
        """
        return self.preferences
