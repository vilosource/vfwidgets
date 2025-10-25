"""Main entry point for reamde command-line tool."""

import sys
from pathlib import Path

# IMPORTANT: Configure environment BEFORE importing Qt modules
# This must happen before ReamdeApp import to ensure proper Qt WebEngine initialization in WSL
from vfwidgets_common import configure_all_for_webengine

# Configure WSL/Remote Desktop environment variables BEFORE Qt initialization
configure_all_for_webengine()

from .app import ReamdeApp  # noqa: E402


def main() -> int:
    """Main entry point for reamde.

    Usage:
        reamde [FILE]

    Args:
        FILE: Optional markdown file to open

    Returns:
        Exit code (0 on success, 1 on failure)
    """
    # Parse command-line arguments
    file_path = None
    if len(sys.argv) > 1:
        file_path = sys.argv[1]

        # Resolve to absolute path
        file_path = str(Path(file_path).resolve())

    # Create and run application
    app = ReamdeApp(sys.argv)
    return app.run(file_path)


if __name__ == "__main__":
    sys.exit(main())
