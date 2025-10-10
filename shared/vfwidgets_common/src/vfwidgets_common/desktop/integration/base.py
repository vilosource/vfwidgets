"""Base class for platform-specific desktop integration backends."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication

from ..config import DesktopConfig, EnvironmentInfo, IntegrationStatus


class DesktopIntegrationBackend(ABC):
    """Abstract base class for desktop integration backends.

    Each platform (Linux XDG, Windows, macOS) implements this interface
    to provide platform-specific desktop integration.
    """

    def __init__(self, config: DesktopConfig, env: EnvironmentInfo):
        """Initialize backend.

        Args:
            config: Desktop integration configuration
            env: Detected environment information
        """
        self.config = config
        self.env = env

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Human-readable platform name (e.g., 'Linux XDG', 'Windows', 'macOS')."""
        pass

    @abstractmethod
    def check_status(self) -> IntegrationStatus:
        """Check if desktop integration is installed.

        Returns:
            Status object with installation details
        """
        pass

    @abstractmethod
    def install(self) -> bool:
        """Install desktop integration (icons, shortcuts, etc.).

        Returns:
            True if installation succeeded, False otherwise
        """
        pass

    @abstractmethod
    def setup_icon(self, app: "QApplication") -> bool:
        """Set up application icon.

        This is called after QApplication is created to configure
        the application icon from available sources.

        Args:
            app: The QApplication instance

        Returns:
            True if icon was set, False otherwise
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.platform_name}>"
