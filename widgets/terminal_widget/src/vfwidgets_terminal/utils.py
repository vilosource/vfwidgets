"""Utility functions for terminal widget."""

import os
import sys


def get_default_shell() -> str:
    """
    Get the default shell for the current platform.

    Returns:
        Shell command appropriate for the platform:
        - Windows: "powershell.exe" or "cmd.exe"
        - Unix: User's shell from $SHELL or "bash"

    Examples:
        >>> # On Windows
        >>> get_default_shell()
        'powershell.exe'

        >>> # On Linux
        >>> get_default_shell()
        '/bin/bash'
    """
    if sys.platform == "win32":
        # Windows: prefer PowerShell, fallback to cmd
        powershell_path = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
        if os.path.exists(powershell_path):
            return "powershell.exe"
        return "cmd.exe"
    else:
        # Unix: use user's shell from environment or fallback to bash
        return os.environ.get("SHELL", "bash")
