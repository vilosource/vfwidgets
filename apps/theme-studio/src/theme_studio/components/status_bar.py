"""Status bar widget for VFTheme Studio."""

from PySide6.QtWidgets import QLabel, QStatusBar


class StatusBarWidget(QStatusBar):
    """Custom status bar with four sections."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Section 1: Theme info (left, permanent)
        self.theme_label = QLabel("No theme loaded")
        self.addPermanentWidget(self.theme_label, stretch=2)

        # Section 2: Color token status (center, permanent)
        self.token_label = QLabel("Colors: 0/197")
        self.addPermanentWidget(self.token_label, stretch=1)

        # Section 3: Font token status (center, permanent)
        self.font_label = QLabel("Fonts: 0/22")
        self.addPermanentWidget(self.font_label, stretch=1)

        # Section 4: Status message (right, temporary)
        self.showMessage("Ready")

    def update_theme_info(self, theme_name: str, is_modified: bool = False):
        """Update theme information.

        Args:
            theme_name: Name of current theme
            is_modified: Whether theme has unsaved changes
        """
        modified_indicator = "*" if is_modified else ""
        self.theme_label.setText(f"ⓘ Theme: {theme_name}{modified_indicator}")

    def update_token_count(self, defined: int, total: int = 197):
        """Update color token count.

        Args:
            defined: Number of defined color tokens
            total: Total number of color tokens
        """
        percentage = int((defined / total) * 100) if total > 0 else 0
        self.token_label.setText(f"Colors: {defined}/{total} ({percentage}%)")

    def update_font_count(self, defined: int, total: int = 22):
        """Update font token count.

        Args:
            defined: Number of defined font tokens
            total: Total number of font tokens
        """
        percentage = int((defined / total) * 100) if total > 0 else 0
        self.font_label.setText(f"Fonts: {defined}/{total} ({percentage}%)")

    def show_status(self, message: str, timeout: int = 3000):
        """Show temporary status message.

        Args:
            message: Status message
            timeout: Display duration in milliseconds (0 = permanent)
        """
        self.showMessage(message, timeout)
