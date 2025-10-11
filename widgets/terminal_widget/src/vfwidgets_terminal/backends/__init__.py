"""Backend abstraction for cross-platform terminal support."""

import sys

from .base import TerminalBackend

# Unix backend only available on Unix systems (uses fcntl, pty, termios)
if sys.platform != "win32":
    from .unix_backend import UnixTerminalBackend

__all__ = ["TerminalBackend", "create_backend"]

# Add UnixTerminalBackend to exports only on Unix
if sys.platform != "win32":
    __all__.append("UnixTerminalBackend")


def create_backend() -> TerminalBackend:
    """
    Create appropriate terminal backend for current platform.

    Returns:
        TerminalBackend instance for the current platform

    Raises:
        RuntimeError: If platform is not supported
    """
    if sys.platform == "win32":
        try:
            from .windows_backend import WindowsTerminalBackend

            return WindowsTerminalBackend()
        except ImportError as e:
            raise RuntimeError(
                "Windows terminal backend requires pywinpty. "
                "Install with: pip install pywinpty"
            ) from e
    else:
        # Unix-like systems (Linux, macOS, BSD)
        from .unix_backend import UnixTerminalBackend

        return UnixTerminalBackend()
