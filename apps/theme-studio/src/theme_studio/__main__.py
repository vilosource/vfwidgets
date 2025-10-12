"""VFTheme Studio - Main entry point.

This module provides the CLI entry point for VFTheme Studio.
"""

import logging
import sys

from . import __version__


def main():
    """Main entry point for VFTheme Studio application."""
    # Configure logging for theme_studio
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    )

    try:
        from .app import ThemeStudioApp
        from .window import ThemeStudioWindow

        # Create application
        app = ThemeStudioApp(sys.argv)

        # Create and show main window
        window = ThemeStudioWindow()
        window.show()

        # Run event loop
        return app.exec()

    except ImportError as e:
        # Fallback if dependencies not installed
        print("=" * 70)
        print(f"VFTheme Studio v{__version__}")
        print("Visual Theme Designer for VFWidgets Applications")
        print("=" * 70)
        print()
        print("ERROR: Missing dependencies")
        print(f"  {e}")
        print()
        print("Please install required dependencies:")
        print("  pip install -e ../../widgets/theme_system")
        print("  pip install -e ../../widgets/vilocode_window")
        print()
        print("Or install with theme-studio package:")
        print("  pip install -e .")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
