"""ViloWeb application - main application class with theme integration.

Educational Focus:
    This module demonstrates:
    - QApplication subclass with custom initialization
    - Theme system integration
    - Application-wide configuration
    - Logging setup
    - Clean startup/shutdown

Architecture:
    ViloWebApplication is the entry point that:
    - Sets up logging
    - Integrates theme system
    - Creates main window
    - Handles application-level events
"""

import logging
import os
import sys
from typing import List, Optional

# IMPORTANT: Configure Qt WebEngine BEFORE importing Qt
# Educational Note:
#     These environment variables MUST be set before Qt modules are imported.
#     Qt WebEngine reads these during module initialization, not at runtime.
#
#     Why these specific flags?
#     - --no-zygote: Disables the zygote process forking model
#     - --no-sandbox: Disables Chromium's sandbox (requires kernel features)
#     - --in-process-gpu: Runs GPU process in main process
#     - --disable-dev-shm-usage: Avoids /dev/shm issues in containers
#
#     This combination works on most Linux environments including:
#     - Standard Linux desktops
#     - Containers (Docker, Podman)
#     - WSL (Windows Subsystem for Linux)
#     - VMs with limited kernel features
#
#     For production: Configure proper sandboxing with kernel support

# Set Qt WebEngine sandbox disable
if "QTWEBENGINE_DISABLE_SANDBOX" not in os.environ:
    os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"

# Set Chromium flags for Qt WebEngine
if "QTWEBENGINE_CHROMIUM_FLAGS" not in os.environ:
    chromium_flags = [
        "--no-zygote",  # Disable zygote process
        "--no-sandbox",  # Disable sandbox
        "--in-process-gpu",  # GPU in main process
        "--disable-dev-shm-usage",  # Avoid /dev/shm issues
        "--disable-gpu-sandbox",  # Disable GPU sandbox
    ]
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = " ".join(chromium_flags)

from PySide6.QtWidgets import QApplication

# Try to import theme system (optional dependency)
try:
    from vfwidgets_theme import ThemedApplication

    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False
    ThemedApplication = None

from .ui import ChromeMainWindow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


class ViloWebApplication:
    """Main application class for ViloWeb.

    Educational Note:
        This class encapsulates the entire application lifecycle:
        1. Initialize QApplication
        2. Setup theme system (if available)
        3. Create main window
        4. Run event loop
        5. Clean shutdown

        Design pattern: This is a "facade" that hides Qt complexity
        from the main() entry point. It provides a clean API:
        - app = ViloWebApplication()
        - sys.exit(app.run())

    Example:
        >>> app = ViloWebApplication()
        >>> sys.exit(app.run())
    """

    def __init__(self, argv: Optional[List[str]] = None):
        """Initialize ViloWeb application.

        Args:
            argv: Command line arguments (default: sys.argv)

        Educational Note:
            We defer QApplication creation to __init__ so users can
            customize before calling run(). This is the "two-phase
            initialization" pattern.
        """
        self._argv = argv or sys.argv

        # Qt WebEngine flags are already set via environment variables
        # (see module-level setup before Qt imports)
        logger.debug(
            f"QTWEBENGINE_CHROMIUM_FLAGS={os.environ.get('QTWEBENGINE_CHROMIUM_FLAGS', 'not set')}"
        )

        # Create QApplication or ThemedApplication
        if THEME_AVAILABLE and ThemedApplication:
            logger.info("Theme system available, using ThemedApplication")
            self._qapp = ThemedApplication(self._argv)
            self._setup_theme()
        else:
            logger.info("Theme system not available, using standard QApplication")
            self._qapp = QApplication(self._argv)

        # Set application metadata
        self._qapp.setApplicationName("ViloWeb")
        self._qapp.setApplicationVersion("0.2.0")  # Updated to v0.2.0
        self._qapp.setOrganizationName("Viloforge")
        self._qapp.setOrganizationDomain("viloforge.com")

        logger.info("ViloWeb application initialized")

        # Main window (created in run())
        self._main_window: Optional[ChromeMainWindow] = None

    def _setup_theme(self) -> None:
        """Setup theme system with default theme.

        Educational Note:
            ThemedApplication provides centralized theme management.
            All ThemedWidgets automatically respond to theme changes.

            We load a default theme from vfwidgets-theme's included themes.
            Users can later switch themes via the UI (future feature).

            Theme system benefits:
            - Consistent look across all widgets
            - Dark mode support
            - VSCode theme compatibility
            - Performance optimized (<100ms theme switches)
        """
        if not THEME_AVAILABLE or not hasattr(self._qapp, "set_theme"):
            return

        try:
            # Try to load default dark theme
            # Educational Note:
            #     We try multiple ways to load a theme because the API
            #     has evolved. This defensive approach ensures we work
            #     with different versions of vfwidgets-theme.

            # Try method 1: Use built-in themes (newer API)
            try:
                from vfwidgets_theme.importers import load_builtin_theme

                theme = load_builtin_theme("dark")
                self._qapp.set_theme(theme)
                logger.info("Applied built-in theme: dark")
                return
            except (ImportError, AttributeError):
                pass

            # Try method 2: Use theme repository (older API)
            try:
                repo = self._qapp._theme_repository
                theme = repo.get_theme("dark")
                if theme:
                    self._qapp.set_theme(theme)
                    logger.info("Applied repository theme: dark")
                    return
            except (AttributeError, KeyError):
                pass

            logger.info("No default theme loaded, using system theme")

        except Exception as e:
            logger.warning(f"Failed to load default theme: {e}")
            logger.info("Continuing with system theme")

    def run(self) -> int:
        """Run the application.

        Returns:
            Exit code from QApplication.exec()

        Educational Note:
            This is the main event loop. It:
            1. Creates main window
            2. Shows it
            3. Enters Qt event loop (blocks until app quits)
            4. Returns exit code

            The event loop processes:
            - User input (mouse, keyboard)
            - Timer events
            - Network events
            - Custom signals/slots
        """
        logger.info("Starting ViloWeb main window")

        # Create and show main window (ChromeMainWindow with frameless design)
        self._main_window = ChromeMainWindow()
        self._main_window.show()

        logger.info("Entering Qt event loop")

        # Enter event loop
        exit_code = self._qapp.exec()

        logger.info(f"Application exiting with code {exit_code}")
        return exit_code

    @property
    def main_window(self) -> Optional[ChromeMainWindow]:
        """Get main window instance.

        Returns:
            ChromeMainWindow instance or None if not created yet
        """
        return self._main_window


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for ViloWeb.

    Args:
        argv: Command line arguments (default: sys.argv)

    Returns:
        Exit code

    Educational Note:
        This is the entry point function that:
        1. Creates ViloWebApplication
        2. Runs it
        3. Returns exit code to OS

        It's kept simple because all logic is in ViloWebApplication.

        Why separate main() from ViloWebApplication?
        - Testability: Can create app without running event loop
        - Flexibility: Can customize app before running
        - Clarity: Clear separation between setup and execution

    Example:
        >>> if __name__ == "__main__":
        ...     sys.exit(main())
    """
    app = ViloWebApplication(argv)
    return app.run()
