"""Main entry point for reamde command-line tool."""

import sys
from pathlib import Path

from .app import ReamdeApp


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
