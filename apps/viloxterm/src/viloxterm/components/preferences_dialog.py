"""Unified preferences dialog for ViloxTerm.

Provides a tabbed interface for all application, terminal, and keyboard settings.
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
from ..app_preferences_manager import AppPreferencesManager
from ..terminal_preferences_manager import TerminalPreferencesManager
from .general_prefs_tab import GeneralPreferencesTab
from .appearance_prefs_tab import AppearancePreferencesTab
from .terminal_prefs_tab import TerminalPreferencesTab
from .advanced_prefs_tab import AdvancedPreferencesTab
from .keyboard_shortcuts_tab import KeyboardShortcutsTab

logger = logging.getLogger(__name__)


class PreferencesDialog(ThemedDialog):
    """Unified preferences dialog with tabbed interface.

    Combines all ViloxTerm settings into a single dialog:
    - General (startup, window behavior)
    - Appearance (theme, UI, focus indicators)
    - Terminal (existing terminal behavior settings)
    - Keyboard Shortcuts (keybinding editor)
    - Advanced (performance, experimental features)
    """

    # Signals
    preferences_applied = Signal(PreferencesModel)  # App preferences
    terminal_preferences_applied = Signal(dict)  # Terminal preferences
    keybinding_changed = Signal(str, str)  # action_id, new_shortcut

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize preferences dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Managers for persistence
        self.app_prefs_manager = AppPreferencesManager()
        self.terminal_prefs_manager = TerminalPreferencesManager()

        # Current preferences
        self.app_preferences = self.app_prefs_manager.load_preferences()
        self.terminal_preferences = self.terminal_prefs_manager.load_preferences()

        # Store reference to keybinding manager (set by caller)
        self.keybinding_manager = None

        self.setWindowTitle("Preferences")
        self.resize(700, 600)

        self._setup_ui()
        self._load_preferences()

    def set_keybinding_manager(self, manager):
        """Set the keybinding manager for the keyboard shortcuts tab.

        Args:
            manager: KeybindingManager instance from main app
        """
        self.keybinding_manager = manager
        # Pass to keyboard shortcuts tab
        if hasattr(self, "keyboard_shortcuts_tab"):
            self.keyboard_shortcuts_tab.set_keybinding_manager(manager)

    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget, 1)

        # Tabs (start with placeholders, will be replaced)
        self._create_tabs()

        # Bottom button bar
        bottom_bar = self._create_bottom_bar()
        layout.addWidget(bottom_bar, 0)

    def _create_tabs(self) -> None:
        """Create preference tabs."""
        # General tab (implemented)
        self.general_tab = GeneralPreferencesTab()
        self.tab_widget.addTab(self.general_tab, "General")

        # Appearance tab (implemented)
        self.appearance_tab = AppearancePreferencesTab()
        self.tab_widget.addTab(self.appearance_tab, "Appearance")

        # Terminal tab (implemented)
        self.terminal_tab = TerminalPreferencesTab()
        self.tab_widget.addTab(self.terminal_tab, "Terminal")

        # Keyboard Shortcuts tab (implemented)
        self.keyboard_shortcuts_tab = KeyboardShortcutsTab()
        self.tab_widget.addTab(self.keyboard_shortcuts_tab, "Keyboard Shortcuts")

        # Advanced tab (implemented)
        self.advanced_tab = AdvancedPreferencesTab()
        self.tab_widget.addTab(self.advanced_tab, "Advanced")

    def _create_placeholder(self, text: str) -> QWidget:
        """Create a placeholder widget for tabs under development.

        Args:
            text: Placeholder text to display

        Returns:
            Themed widget with centered label
        """
        from PySide6.QtWidgets import QLabel
        from PySide6.QtCore import Qt

        widget = ThemedQWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)

        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 14pt; color: #888;")
        layout.addWidget(label)

        return widget

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
        # Load into General tab
        self.general_tab.load_preferences(self.app_preferences.general)

        # Load into Appearance tab
        self.appearance_tab.load_preferences(self.app_preferences.appearance)

        # Load into Terminal tab
        self.terminal_tab.load_preferences(self.terminal_preferences)

        # Load into Advanced tab
        self.advanced_tab.load_preferences(self.app_preferences.advanced)

        # Load into Keyboard Shortcuts tab
        self.keyboard_shortcuts_tab.load_preferences()

        logger.debug("Loading preferences into dialog")

    def _save_preferences(self) -> None:
        """Save UI values to preference models."""
        # Save from General tab
        self.app_preferences.general = self.general_tab.save_preferences()

        # Save from Appearance tab
        self.app_preferences.appearance = self.appearance_tab.save_preferences()

        # Save from Terminal tab
        self.terminal_preferences = self.terminal_tab.save_preferences()

        # Save from Advanced tab
        self.app_preferences.advanced = self.advanced_tab.save_preferences()

        # Save from Keyboard Shortcuts tab
        self.keyboard_shortcuts_tab.save_preferences()

        logger.debug("Saving preferences from dialog")

    def on_apply(self) -> None:
        """Handle Apply button click."""
        self._save_preferences()

        # Validate app preferences
        errors = self.app_prefs_manager.validate_preferences(self.app_preferences)
        if errors:
            logger.warning(f"Preference validation errors: {errors}")
            # TODO: Show error dialog
            return

        # Save to disk
        self.app_prefs_manager.save_preferences(self.app_preferences)
        self.terminal_prefs_manager.save_preferences(self.terminal_preferences)

        # Emit signals for live application
        self.preferences_applied.emit(self.app_preferences)
        self.terminal_preferences_applied.emit(self.terminal_preferences)

        logger.info("Applied and saved all preferences")

    def on_ok(self) -> None:
        """Handle OK button click."""
        self.on_apply()
        self.accept()

    def reject(self) -> None:
        """Handle Cancel button click."""
        # Cancel pending keyboard shortcut changes
        self.keyboard_shortcuts_tab.cancel_changes()
        super().reject()

    def get_app_preferences(self) -> PreferencesModel:
        """Get current application preferences.

        Returns:
            PreferencesModel with current values
        """
        return self.app_preferences

    def get_terminal_preferences(self) -> dict:
        """Get current terminal preferences.

        Returns:
            Dictionary with terminal preferences
        """
        return self.terminal_preferences
