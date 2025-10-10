"""ViloxTerm main entry point."""

import sys
import logging

# IMPORTANT: Desktop integration must happen BEFORE importing Qt modules
# This configures environment variables and platform quirks before Qt initialization
from vfwidgets_common.desktop import configure_desktop

from vfwidgets_theme import ThemedApplication
from .app import ViloxTermApp


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def main():
    """Main entry point for ViloxTerm."""
    setup_logging()
    logger = logging.getLogger(__name__)

    # Configure desktop integration and create ThemedApplication
    # This handles:
    # - Platform detection (WSL, Wayland, X11, etc.)
    # - Platform quirks (software rendering, scaling fixes)
    # - Desktop integration (icons, .desktop files)
    # - QApplication creation
    logger.info("Configuring desktop integration...")

    theme_config = {"persist_theme": True, "auto_detect_system": False}
    app = configure_desktop(
        app_name="viloxterm",
        app_display_name="ViloxTerm",
        icon_name="viloxterm",
        desktop_categories="System;TerminalEmulator;Utility;",
        application_class=ThemedApplication,
        theme_config=theme_config,
    )

    # Load saved theme from ViloxTerm config if available
    try:
        from PySide6.QtCore import QSettings

        settings = QSettings("ViloxTerm", "ViloxTerm")
        saved_theme = settings.value("theme/current")

        if saved_theme:
            logger.info(f"Loading saved theme: {saved_theme}")
            if not app.set_theme(saved_theme):
                logger.warning(f"Failed to load saved theme '{saved_theme}', using default")
                app.set_theme("dark")
        else:
            # No saved theme, use default
            app.set_theme("dark")
    except Exception as e:
        logger.warning(f"Error loading theme preference: {e}, using default theme")
        app.set_theme("dark")

    # Create and show main window
    window = ViloxTermApp()
    window.show()

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
