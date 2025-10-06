"""Backend abstraction for cross-platform terminal support."""

from .base import TerminalBackend
from .unix_backend import UnixTerminalBackend

__all__ = ["TerminalBackend", "UnixTerminalBackend", "create_backend"]


def create_backend() -> TerminalBackend:
    """
    Create appropriate terminal backend for current platform.

    Returns:
        TerminalBackend instance for the current platform

    Raises:
        RuntimeError: If platform is not supported
    """
    import sys

    if sys.platform == "win32":
        try:
            from .windows_backend import WindowsTerminalBackend

            return WindowsTerminalBackend()
        except ImportError as e:
            raise RuntimeError(
                "Windows terminal backend requires pywinpty. " "Install with: pip install pywinpty"
            ) from e
    else:
        # Unix-like systems (Linux, macOS, BSD)
        return UnixTerminalBackend()
