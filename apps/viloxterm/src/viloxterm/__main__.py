"""ViloxTerm main entry point."""

import sys
import logging

# IMPORTANT: Desktop integration must happen BEFORE importing Qt modules
# This configures environment variables and platform quirks before Qt initialization
from vfwidgets_common.desktop import configure_desktop

from .themed_app import ViloxTermThemedApp
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

    # Configure desktop integration and create ViloxTermThemedApp
    # This handles:
    # - Platform detection (WSL, Wayland, X11, etc.)
    # - Platform quirks (software rendering, scaling fixes)
    # - Desktop integration (icons, .desktop files)
    # - QApplication creation with theme overlay support
    logger.info("Configuring desktop integration...")

    app = configure_desktop(
        app_name="viloxterm",
        app_display_name="ViloxTerm",
        icon_name="viloxterm",
        desktop_categories="System;TerminalEmulator;Utility;",
        application_class=ViloxTermThemedApp,
    )

    # Theme is now loaded automatically by ViloxTermThemedApp!
    # - Migrates old "theme/current" key to "theme/base_theme" on first run
    # - Loads saved theme preference automatically
    # - Defaults to "dark" if no preference saved
    logger.info("Theme loaded automatically (overlay system v2.0.0)")

    # Create and show main window
    window = ViloxTermApp()
    window.show()

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
