"""Base class for platform-specific quirks and workarounds."""

from abc import ABC, abstractmethod

from ..config import EnvironmentInfo


class PlatformQuirk(ABC):
    """Base class for platform-specific workarounds.

    A quirk is a piece of configuration or environment setup that needs
    to be applied for Qt applications to work properly in specific
    environments (WSL, Wayland, Remote Desktop, etc.).

    Quirks are automatically applied based on environment detection.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the quirk."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what this quirk fixes."""
        pass

    @abstractmethod
    def is_applicable(self, env: EnvironmentInfo) -> bool:
        """Check if this quirk should be applied in the current environment.

        Args:
            env: Detected environment information

        Returns:
            True if this quirk should be applied, False otherwise
        """
        pass

    @abstractmethod
    def apply(self) -> dict[str, str]:
        """Apply the quirk by modifying environment variables or settings.

        This method should:
        1. Check if changes are already made (respect user config)
        2. Apply necessary environment variables
        3. Return dict of changes made

        Returns:
            Dictionary of environment variables that were changed
            (key=var_name, value=new_value)
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name}>"
