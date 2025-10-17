"""Theme override editor widget.

Main widget with tabbed interface for editing theme overrides across
all theme types (dark, light, high-contrast).
"""

import logging
from typing import Optional

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ..theme_overrides import ThemeOverrides
from .token_override_panel import TokenOverridePanel

logger = logging.getLogger(__name__)


class ThemeOverrideEditor(QWidget):
    """Universal editor for theme token overrides.

    Provides tabbed interface for editing color overrides:
    - Tab 1: Dark Themes
    - Tab 2: Light Themes
    - Tab 3: High Contrast

    Each tab shows the same token list with independent color pickers.

    Args:
        overrideable_tokens: List of (token_path, label, description) tuples
        parent: Parent widget

    Usage:
        >>> tokens = [
        ...     ("markdown.colors.background", "Background", "Main bg color"),
        ...     ("markdown.colors.link", "Links", "Hyperlink color"),
        ... ]
        >>> editor = ThemeOverrideEditor(tokens)
        >>> editor.load_overrides(my_overrides)
        >>> # User edits colors...
        >>> new_overrides = editor.save_overrides()

    Example:
        >>> # In your preferences tab:
        >>> MARKDOWN_TOKENS = [
        ...     ("markdown.colors.link", "Links", "Link color"),
        ... ]
        >>> self.override_editor = ThemeOverrideEditor(MARKDOWN_TOKENS)
        >>> layout.addWidget(self.override_editor)
    """

    def __init__(
        self,
        overrideable_tokens: list[tuple[str, str, str]],
        parent: Optional[QWidget] = None,
    ):
        """Initialize editor.

        Args:
            overrideable_tokens: List of (token_path, label, description) tuples
                Example: ("markdown.colors.link", "Links", "Hyperlink color")
            parent: Parent widget
        """
        super().__init__(parent)
        self.overrideable_tokens = overrideable_tokens
        self._setup_ui()

    def _setup_ui(self):
        """Build tabbed UI: Dark / Light / High Contrast."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Info label
        info = QLabel(
            "<b>Theme Color Overrides</b><br>"
            "Customize colors per theme type. Dark overrides apply to all dark themes "
            "(Dark, Monokai, etc.), light overrides to all light themes."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        # Tabs for each theme type
        self.tabs = QTabWidget()

        # Create panel for each theme type
        self.dark_panel = TokenOverridePanel(self.overrideable_tokens, "dark", parent=self)
        self.light_panel = TokenOverridePanel(self.overrideable_tokens, "light", parent=self)
        self.hc_panel = TokenOverridePanel(self.overrideable_tokens, "high-contrast", parent=self)

        self.tabs.addTab(self.dark_panel, "Dark Themes")
        self.tabs.addTab(self.light_panel, "Light Themes")
        self.tabs.addTab(self.hc_panel, "High Contrast")

        layout.addWidget(self.tabs)

        # Global reset button
        button_row = QHBoxLayout()
        button_row.addStretch()

        reset_all_btn = QPushButton("Reset All Tabs")
        reset_all_btn.setToolTip(
            "Remove ALL overrides across all theme types (Dark, Light, High Contrast)"
        )
        reset_all_btn.clicked.connect(self.reset_all_tabs)
        button_row.addWidget(reset_all_btn)

        layout.addLayout(button_row)

    def load_overrides(self, overrides: ThemeOverrides):
        """Load overrides into UI.

        Args:
            overrides: ThemeOverrides with dark/light/high-contrast overrides
        """
        self.dark_panel.load_tokens(overrides.dark_overrides)
        self.light_panel.load_tokens(overrides.light_overrides)
        self.hc_panel.load_tokens(overrides.high_contrast_overrides)

        logger.debug("Loaded theme overrides into editor")

    def save_overrides(self) -> ThemeOverrides:
        """Collect overrides from UI.

        Returns:
            ThemeOverrides with collected dark/light/high-contrast overrides
        """
        overrides = ThemeOverrides(
            dark_overrides=self.dark_panel.save_tokens(),
            light_overrides=self.light_panel.save_tokens(),
            high_contrast_overrides=self.hc_panel.save_tokens(),
        )

        total = (
            len(overrides.dark_overrides)
            + len(overrides.light_overrides)
            + len(overrides.high_contrast_overrides)
        )
        logger.debug(f"Saved {total} total token overrides from editor")

        return overrides

    def reset_all_tabs(self):
        """Reset all theme types to defaults.

        Shows confirmation dialog before resetting.
        """
        # Confirmation dialog
        reply = QMessageBox.question(
            self,
            "Reset All Theme Types",
            "Reset ALL theme types (Dark, Light, High Contrast) to defaults?\n\n"
            "This will remove all token overrides across all tabs.\n\n"
            "This action cannot be undone until you save preferences.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,  # Default to No
        )

        if reply != QMessageBox.StandardButton.Yes:
            logger.debug("Reset all tabs cancelled by user")
            return

        # Reset each panel (silent = no per-panel confirmation)
        self.dark_panel.reset_all_silent()
        self.light_panel.reset_all_silent()
        self.hc_panel.reset_all_silent()

        logger.info("Reset all token overrides across all theme types to defaults")

        # Show success message
        QMessageBox.information(
            self,
            "Reset Complete",
            "All theme type overrides have been reset to defaults.\n\n"
            "Changes will not take effect until you click Apply or OK.",
        )
