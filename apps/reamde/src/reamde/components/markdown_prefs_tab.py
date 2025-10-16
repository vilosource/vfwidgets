"""Markdown preferences tab for Reamde.

Handles markdown rendering features and behavior settings.
"""

import logging

from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QScrollArea,
    QVBoxLayout,
)
from vfwidgets_theme import ThemedQWidget

from ..models.preferences_model import MarkdownPreferences

logger = logging.getLogger(__name__)


class MarkdownPreferencesTab(ThemedQWidget):
    """Tab widget for markdown preferences."""

    def __init__(self, parent=None):
        """Initialize the markdown preferences tab.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self._preferences: MarkdownPreferences = MarkdownPreferences()
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
        container_layout.addWidget(self._create_rendering_features_group())
        container_layout.addWidget(self._create_behavior_group())

        container_layout.addStretch()

        scroll.setWidget(container)
        layout.addWidget(scroll)

    def _create_rendering_features_group(self) -> QGroupBox:
        """Create the rendering features settings group.

        Returns:
            QGroupBox with rendering features settings
        """
        group = QGroupBox("Rendering Features")
        layout = QFormLayout(group)

        # Syntax highlighting
        self.syntax_highlighting_check = QCheckBox("Enable syntax highlighting for code blocks")
        layout.addRow("", self.syntax_highlighting_check)

        # Math rendering
        self.math_rendering_check = QCheckBox("Enable math equation rendering (LaTeX)")
        layout.addRow("", self.math_rendering_check)

        # Mermaid diagrams
        self.mermaid_diagrams_check = QCheckBox("Enable Mermaid diagram rendering")
        layout.addRow("", self.mermaid_diagrams_check)

        return group

    def _create_behavior_group(self) -> QGroupBox:
        """Create the behavior settings group.

        Returns:
            QGroupBox with behavior settings
        """
        group = QGroupBox("Behavior")
        layout = QFormLayout(group)

        # Auto-reload on change
        self.auto_reload_check = QCheckBox("Automatically reload file when changed externally")
        layout.addRow("", self.auto_reload_check)

        # Scroll sync (future feature, disabled for now)
        self.scroll_sync_check = QCheckBox("Sync scroll position with source (future feature)")
        self.scroll_sync_check.setEnabled(False)
        layout.addRow("", self.scroll_sync_check)

        return group

    def load_preferences(self, preferences: MarkdownPreferences) -> None:
        """Load preferences into UI.

        Args:
            preferences: MarkdownPreferences to load
        """
        self._preferences = preferences

        # Rendering Features
        self.syntax_highlighting_check.setChecked(preferences.enable_syntax_highlighting)
        self.math_rendering_check.setChecked(preferences.enable_math_rendering)
        self.mermaid_diagrams_check.setChecked(preferences.enable_mermaid_diagrams)

        # Behavior
        self.auto_reload_check.setChecked(preferences.auto_reload_on_change)
        self.scroll_sync_check.setChecked(preferences.scroll_sync)

    def save_preferences(self) -> MarkdownPreferences:
        """Collect preferences from UI.

        Returns:
            MarkdownPreferences with current UI values
        """
        return MarkdownPreferences(
            # Rendering Features
            enable_syntax_highlighting=self.syntax_highlighting_check.isChecked(),
            enable_math_rendering=self.math_rendering_check.isChecked(),
            enable_mermaid_diagrams=self.mermaid_diagrams_check.isChecked(),
            # Behavior
            auto_reload_on_change=self.auto_reload_check.isChecked(),
            scroll_sync=self.scroll_sync_check.isChecked(),
        )
