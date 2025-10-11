"""Reamde - Single-instance markdown document viewer.

A modern markdown viewer with tabbed interface, VS Code-style layout,
and single-instance behavior for efficient document management.

Example:
    Launch from command line:

    $ reamde README.md

    Open additional files in the same instance:

    $ reamde DOCS.md  # Opens in new tab
"""

__version__ = "0.1.0"

from .app import ReamdeApp
from .window import ReamdeWindow

__all__ = ["ReamdeApp", "ReamdeWindow", "__version__"]
