"""ViloCodeWindow - VS Code-style application window for PySide6.

A frameless, themeable window widget with activity bar, sidebar, main pane,
and auxiliary bar. Designed for building IDE-style applications.

Example:
    >>> from vfwidgets_vilocode_window import ViloCodeWindow
    >>> window = ViloCodeWindow()
    >>> window.show()
"""

__version__ = "0.1.0"

from .vilocode_window import ViloCodeWindow

__all__ = ["ViloCodeWindow", "__version__"]
