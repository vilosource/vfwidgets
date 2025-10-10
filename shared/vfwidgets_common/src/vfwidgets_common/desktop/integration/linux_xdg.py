"""Linux XDG Desktop Entry Specification integration backend.

This backend implements desktop integration for Linux systems following
the freedesktop.org XDG Desktop Entry Specification. It works with
GNOME, KDE, XFCE, and other compliant desktop environments.
"""

import logging
import os
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication

from ..config import IntegrationStatus
from .base import DesktopIntegrationBackend

logger = logging.getLogger(__name__)


class LinuxXDGIntegration(DesktopIntegrationBackend):
    """XDG Desktop Entry integration for Linux.

    Implements desktop integration following freedesktop.org standards:
    - Desktop entry files in ~/.local/share/applications/
    - Icons in ~/.local/share/icons/hicolor/
    - Database updates using XDG tools
    """

    @property
    def platform_name(self) -> str:
        return "Linux XDG"

    def check_status(self) -> IntegrationStatus:
        """Check if XDG desktop integration is installed."""
        desktop_file_path = self._get_desktop_file_path()
        icon_path = self._get_icon_path()

        has_desktop_file = desktop_file_path.exists()
        has_icon = icon_path.exists() if icon_path else False

        missing_files = []
        if not has_desktop_file:
            missing_files.append(str(desktop_file_path))
        if not has_icon and icon_path:
            missing_files.append(str(icon_path))

        is_installed = has_desktop_file and has_icon

        return IntegrationStatus(
            is_installed=is_installed,
            has_desktop_file=has_desktop_file,
            has_icon=has_icon,
            missing_files=missing_files,
            platform_name=self.platform_name,
            desktop_environment=self.env.desktop_env,
        )

    def install(self) -> bool:
        """Install XDG desktop integration.

        This looks for an install script in common locations and runs it,
        or creates the integration files directly if no script is found.

        Returns:
            True if installation succeeded
        """
        # Try to find and run existing install script
        install_script = self._find_install_script()
        if install_script:
            logger.info(f"Running installation script: {install_script}")
            return self._run_install_script(install_script)

        # Otherwise create integration files directly
        logger.info("No installation script found, creating integration files directly")
        return self._create_integration_files()

    def setup_icon(self, app: "QApplication") -> bool:
        """Set up application icon for Qt application.

        Tries multiple sources in order:
        1. System theme icon (via QIcon.fromTheme)
        2. User-installed icon (~/.local/share/icons/...)
        3. Bundled icon resource

        Args:
            app: The QApplication instance

        Returns:
            True if icon was successfully set
        """
        from PySide6.QtGui import QIcon

        icon_name = self.config.icon_name

        # Try 1: System theme icon (most reliable if installed)
        icon = QIcon.fromTheme(icon_name)
        if not icon.isNull():
            app.setWindowIcon(icon)
            logger.debug(f"Using theme icon: {icon_name}")
            return True

        # Try 2: User-installed icon
        icon_path = self._get_icon_path()
        if icon_path and icon_path.exists():
            icon = QIcon(str(icon_path))
            if not icon.isNull():
                app.setWindowIcon(icon)
                logger.debug(f"Using installed icon: {icon_path}")
                return True

        # Try 3: Bundled resource icon (if available)
        # This would need to be implemented by the application
        logger.warning(f"Could not find icon for: {icon_name}")
        return False

    def _get_desktop_file_path(self) -> Path:
        """Get path to user's desktop file."""
        return Path.home() / ".local/share/applications" / f"{self.config.app_name}.desktop"

    def _get_icon_path(self) -> Optional[Path]:
        """Get path to user's icon file (SVG preferred)."""
        icon_base = Path.home() / ".local/share/icons/hicolor"

        # Try SVG first (scalable)
        svg_path = icon_base / "scalable/apps" / f"{self.config.icon_name}.svg"
        if svg_path.exists():
            return svg_path

        # Try common PNG sizes
        for size in [256, 128, 64, 48]:
            png_path = icon_base / f"{size}x{size}/apps" / f"{self.config.icon_name}.png"
            if png_path.exists():
                return png_path

        return None

    def _find_install_script(self) -> Optional[Path]:
        """Find installation script in common locations.

        Looks for install-user.sh in:
        - Current working directory
        - Application package directory
        - Common installation paths

        Returns:
            Path to install script if found
        """
        # Search paths (in order of preference)
        search_paths = [
            Path.cwd() / "install-user.sh",
            Path.cwd() / f"{self.config.app_name}/install-user.sh",
        ]

        # Try to find application package directory
        try:
            import sys

            # Look for main application module
            app_module_name = self.config.app_name.replace("-", "_")
            if app_module_name in sys.modules:
                app_module = sys.modules[app_module_name]
                if hasattr(app_module, "__file__") and app_module.__file__:
                    app_dir = Path(app_module.__file__).parent.parent
                    search_paths.append(app_dir / "install-user.sh")
        except Exception as e:
            logger.debug(f"Could not determine application directory: {e}")

        # Find first existing script
        for path in search_paths:
            if path.exists() and path.is_file():
                return path

        return None

    def _run_install_script(self, script_path: Path) -> bool:
        """Run installation script.

        Args:
            script_path: Path to installation script

        Returns:
            True if script succeeded
        """
        try:
            # Make script executable
            os.chmod(script_path, 0o755)

            # Run script
            result = subprocess.run(
                [str(script_path)],
                cwd=script_path.parent,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                logger.info("Installation script completed successfully")
                return True
            else:
                logger.error(f"Installation script failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("Installation script timed out")
            return False
        except Exception as e:
            logger.error(f"Failed to run installation script: {e}")
            return False

    def _create_integration_files(self) -> bool:
        """Create desktop integration files directly.

        This is a fallback when no installation script is found.
        Creates minimal .desktop file and attempts to find icon.

        Returns:
            True if files were created successfully
        """
        try:
            # Create desktop file
            desktop_file_path = self._get_desktop_file_path()
            desktop_file_path.parent.mkdir(parents=True, exist_ok=True)

            desktop_content = self._generate_desktop_file_content()
            desktop_file_path.write_text(desktop_content)

            logger.info(f"Created desktop file: {desktop_file_path}")

            # Update desktop database
            self._update_desktop_database()

            return True

        except Exception as e:
            logger.error(f"Failed to create integration files: {e}")
            return False

    def _generate_desktop_file_content(self) -> str:
        """Generate .desktop file content."""
        return f"""[Desktop Entry]
Version=1.0
Type=Application
Name={self.config.app_display_name}
Exec={self.config.app_name}
Icon={self.config.icon_name}
Terminal=false
Categories={self.config.desktop_categories}
StartupNotify=true
"""

    def _update_desktop_database(self) -> None:
        """Update desktop database after changes."""
        try:
            subprocess.run(
                ["update-desktop-database", str(Path.home() / ".local/share/applications")],
                capture_output=True,
                timeout=10,
            )
            logger.debug("Updated desktop database")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.debug("Could not update desktop database (tool not available)")
