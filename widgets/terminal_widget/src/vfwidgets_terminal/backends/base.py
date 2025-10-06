"""Abstract base class for terminal backends."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..session import TerminalSession


class TerminalBackend(ABC):
    """
    Abstract base class for terminal backend implementations.

    Provides platform-agnostic interface for terminal operations.
    Subclasses implement platform-specific functionality.
    """

    @abstractmethod
    def start_process(self, session: "TerminalSession") -> bool:
        """
        Start a terminal process for the given session.

        Args:
            session: The terminal session to start

        Returns:
            True if process started successfully, False otherwise
        """
        pass

    @abstractmethod
    def read_output(self, session: "TerminalSession", max_bytes: int = 1024 * 20) -> Optional[str]:
        """
        Read output from the terminal process.

        Args:
            session: The terminal session to read from
            max_bytes: Maximum number of bytes to read

        Returns:
            Output string if available, None otherwise
        """
        pass

    @abstractmethod
    def write_input(self, session: "TerminalSession", data: str) -> bool:
        """
        Write input to the terminal process.

        Args:
            session: The terminal session to write to
            data: The input data to write

        Returns:
            True if write was successful, False otherwise
        """
        pass

    @abstractmethod
    def resize(self, session: "TerminalSession", rows: int, cols: int) -> bool:
        """
        Resize the terminal window.

        Args:
            session: The terminal session to resize
            rows: Number of rows
            cols: Number of columns

        Returns:
            True if resize was successful, False otherwise
        """
        pass

    @abstractmethod
    def is_process_alive(self, session: "TerminalSession") -> bool:
        """
        Check if the terminal process is still running.

        Args:
            session: The terminal session to check

        Returns:
            True if process is alive, False otherwise
        """
        pass

    @abstractmethod
    def terminate_process(self, session: "TerminalSession") -> bool:
        """
        Terminate the terminal process.

        Args:
            session: The terminal session to terminate

        Returns:
            True if termination was successful, False otherwise
        """
        pass

    @abstractmethod
    def cleanup(self, session: "TerminalSession") -> None:
        """
        Clean up resources for a terminal session.

        Args:
            session: The terminal session to clean up
        """
        pass

    @abstractmethod
    def poll_process(self, session: "TerminalSession", timeout: float = 0.01) -> bool:
        """
        Poll the terminal process for available data.

        Args:
            session: The terminal session to poll
            timeout: Timeout in seconds

        Returns:
            True if data is available, False otherwise
        """
        pass

    def get_platform_name(self) -> str:
        """
        Get the name of the platform this backend supports.

        Returns:
            Platform name (e.g., "Unix", "Windows")
        """
        return self.__class__.__name__.replace("TerminalBackend", "")
