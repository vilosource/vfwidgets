"""ViloxTerm main entry point."""

import sys
import logging

# IMPORTANT: Configure environment BEFORE importing Qt modules
# This must happen before ThemedApplication import to ensure proper Qt WebEngine initialization
from vfwidgets_common import configure_all_for_webengine, is_wsl

from vfwidgets_theme import ThemedApplication
from .app import ViloxTermApp


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
    """Main entry point for ViloxTerm."""
    setup_logging()

    # Configure environment BEFORE creating QApplication
    configure_environment()

    # Create themed application
    app = ThemedApplication(sys.argv)
    app.set_theme("dark")

    # Create and show main window
    window = ViloxTermApp()
    window.show()

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
