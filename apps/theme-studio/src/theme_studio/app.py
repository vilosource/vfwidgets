"""VFTheme Studio - Application class.

Main application class that initializes PySide6.
Uses OS/system theme - no custom theming.
"""

from PySide6.QtWidgets import QApplication


class ThemeStudioApp(QApplication):
    """Main application class for VFTheme Studio.

    This is a plain QApplication that uses the OS/system theme.
    Theme Studio does not apply custom themes to itself - only to preview widgets.
    """

    def __init__(self, argv):
        super().__init__(argv)

        # Application metadata
        self.setApplicationName("VFTheme Studio")
        self.setApplicationVersion("0.1.0-dev")
        self.setOrganizationName("Vilosource")
        self.setOrganizationDomain("viloforge.com")

        # Set application icon (will be added later)
        # self.setWindowIcon(QIcon(":/icons/theme-studio.png"))

        # No theme setup - use OS theme
