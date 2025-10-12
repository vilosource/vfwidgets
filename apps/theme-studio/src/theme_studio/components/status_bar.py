"""Status bar widget for VFTheme Studio."""

from PySide6.QtWidgets import QLabel, QStatusBar


class StatusBarWidget(QStatusBar):
    """Custom status bar with three sections."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Section 1: Theme info (left, permanent)
        self.theme_label = QLabel("No theme loaded")
        self.addPermanentWidget(self.theme_label, stretch=2)

        # Section 2: Token status (center, permanent)
        self.token_label = QLabel("Tokens: 0/197")
        self.addPermanentWidget(self.token_label, stretch=1)

        # Section 3: Status message (right, temporary)
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
        """Update token count.

        Args:
            defined: Number of defined tokens
            total: Total number of tokens
        """
        percentage = int((defined / total) * 100) if total > 0 else 0
        self.token_label.setText(f"Tokens: {defined}/{total} defined ({percentage}%)")

    def show_status(self, message: str, timeout: int = 3000):
        """Show temporary status message.

        Args:
            message: Status message
            timeout: Display duration in milliseconds (0 = permanent)
        """
        self.showMessage(message, timeout)
