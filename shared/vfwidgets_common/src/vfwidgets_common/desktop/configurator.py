"""Main desktop configuration orchestrator."""

import logging
import sys
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication

from .config import DesktopConfig, EnvironmentInfo
from .environment import detect_environment
from .integration.base import DesktopIntegrationBackend
from .quirks import apply_all_quirks

logger = logging.getLogger(__name__)


class DesktopConfigurator:
    """Main orchestrator for desktop configuration.

    Coordinates environment detection, quirk application, desktop integration,
    and QApplication creation.

    Example:
        config = DesktopConfig(
            app_name="viloxterm",
            app_display_name="ViloxTerm",
            icon_name="viloxterm",
            desktop_categories="System;TerminalEmulator;",
        )

        configurator = DesktopConfigurator(config)
        app = configurator.configure()
    """

    def __init__(self, config: DesktopConfig):
        """Initialize configurator.

        Args:
            config: Desktop configuration
        """
        self.config = config
        self.env: Optional[EnvironmentInfo] = None
        self.backend: Optional[DesktopIntegrationBackend] = None

    def configure(self) -> "QApplication":
        """Execute complete desktop configuration pipeline.

        This is the main entry point that:
        1. Detects environment
        2. Applies platform quirks
        3. Checks/installs desktop integration
        4. Creates QApplication
        5. Sets up icon and metadata

        Returns:
            Configured QApplication instance ready to use
        """
        # Step 1: Detect environment
        logger.info("Detecting environment...")
        self.env = detect_environment()
        logger.debug(f"Environment: {self.env.os}/{self.env.desktop_env}/{self.env.display_server}")

        # Step 2: Apply platform quirks
        logger.info("Applying platform quirks...")
        quirks_applied = apply_all_quirks(self.env)
        if quirks_applied:
            logger.info(f"Applied {len(quirks_applied)} environment variable changes")

        # Step 3: Select integration backend
        self.backend = self._select_backend()
        logger.debug(f"Using integration backend: {self.backend.platform_name}")

        # Step 4: Check integration status
        status = self.backend.check_status()
        logger.debug(f"Integration status: installed={status.is_installed}")

        # Step 5: Auto-install if needed
        if not status.is_installed and self.config.auto_install:
            logger.info("Desktop integration not installed, attempting auto-install...")
            if self.backend.install():
                logger.info("Desktop integration installed successfully")
            else:
                logger.warning("Desktop integration installation failed")

        # Step 6: Create QApplication
        app = self._create_application()

        # Step 7: Set up icon
        if self.backend.setup_icon(app):
            logger.debug("Application icon configured")
        else:
            logger.debug("Could not configure application icon")

        # Step 8: Set application metadata
        self._set_application_metadata(app)

        logger.info("Desktop configuration complete")
        return app

    def _select_backend(self) -> DesktopIntegrationBackend:
        """Select appropriate integration backend for platform.

        Returns:
            Integration backend instance
        """
        if self.env.os == "linux":
            from .integration.linux_xdg import LinuxXDGIntegration

            return LinuxXDGIntegration(self.config, self.env)

        # elif self.env.os == "windows":
        #     from .integration.windows import WindowsIntegration
        #     return WindowsIntegration(self.config, self.env)
        #
        # elif self.env.os == "darwin":
        #     from .integration.macos import MacOSIntegration
        #     return MacOSIntegration(self.config, self.env)

        # Fallback: null backend that does nothing
        return NullIntegration(self.config, self.env)

    def _create_application(self) -> "QApplication":
        """Create QApplication instance.

        Returns:
            QApplication instance
        """
        if not self.config.create_application:
            raise RuntimeError("create_application is False but configure() needs to create app")

        # Import Qt here (after quirks have been applied)
        from PySide6.QtWidgets import QApplication

        # Use custom application class if provided
        app_class = self.config.application_class or QApplication

        # Create application
        app = app_class(sys.argv, **self.config.application_kwargs)

        return app

    def _set_application_metadata(self, app: "QApplication") -> None:
        """Set application metadata on QApplication.

        Args:
            app: QApplication instance
        """
        app.setApplicationName(self.config.app_name)
        app.setApplicationDisplayName(self.config.app_display_name)

        # IMPORTANT: setDesktopFileName is crucial for Wayland window matching
        # Without this, Wayland compositors can't match windows to .desktop files
        app.setDesktopFileName(self.config.app_name)


class NullIntegration(DesktopIntegrationBackend):
    """Null integration backend for unsupported platforms.

    Does nothing but provides required interface.
    """

    @property
    def platform_name(self) -> str:
        return "Unsupported Platform"

    def check_status(self):
        from .config import IntegrationStatus

        return IntegrationStatus(
            is_installed=False,
            has_desktop_file=False,
            has_icon=False,
            missing_files=[],
            platform_name=self.platform_name,
        )

    def install(self) -> bool:
        logger.warning(f"Desktop integration not supported on {self.env.os}")
        return False

    def setup_icon(self, app) -> bool:
        return False
