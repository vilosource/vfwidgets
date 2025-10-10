"""ViloWeb main entry point."""

import sys
import logging

# IMPORTANT: Configure environment BEFORE importing Qt modules
# This must happen before importing Qt to ensure proper Qt WebEngine initialization
from vfwidgets_common import configure_all_for_webengine, is_wsl

from vfwidgets_theme import ThemedApplication
from .app import ViloWebApp


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def configure_environment():
    """Configure environment for optimal Qt WebEngine performance.

    This detects WSL and other special environments and automatically
    configures the necessary environment variables for software rendering.
    """
    logger = logging.getLogger(__name__)

    # Configure Qt and WebEngine environment variables
    changes = configure_all_for_webengine()

    if changes:
        logger.info(f"Auto-configured environment for {', '.join(changes.keys())}")
        if is_wsl():
            logger.info("WSL detected: Using software rendering for Qt WebEngine")


def main():
    """Main entry point for ViloWeb."""
    setup_logging()
    logger = logging.getLogger(__name__)

    # Configure environment BEFORE creating QApplication
    configure_environment()

    # Create themed application with theme persistence enabled
    theme_config = {"persist_theme": True, "auto_detect_system": False}
    app = ThemedApplication(sys.argv, theme_config=theme_config)

    # Load saved theme from ViloWeb config if available
    try:
        from PySide6.QtCore import QSettings

        settings = QSettings("ViloWeb", "ViloWeb")
        saved_theme = settings.value("theme/current")

        if saved_theme:
            logger.info(f"Loading saved theme: {saved_theme}")
            if not app.set_theme(saved_theme):
                logger.warning(f"Failed to load saved theme '{saved_theme}', using default")
                app.set_theme("Dark Default")
        else:
            # No saved theme, use default
            app.set_theme("Dark Default")
    except Exception as e:
        logger.warning(f"Error loading theme preference: {e}, using default theme")
        app.set_theme("Dark Default")

    # Create and show main window
    window = ViloWebApp()
    window.show()

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
