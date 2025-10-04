"""ViloxTerm main entry point."""

import sys
import logging

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
