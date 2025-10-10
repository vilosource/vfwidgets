"""ViloxTerm - Modern terminal emulator application.

ViloxTerm demonstrates the integration of multiple VFWidgets components:
- ChromeTabbedWindow for Chrome-style tabs
- MultisplitWidget for dynamic split panes
- TerminalWidget for xterm.js terminals
- Theme System for unified theming
"""

__version__ = "1.1.1-dev"
__author__ = "Vilosource"
__email__ = "vilosource@viloforge.com"

from .app import ViloxTermApp

__all__ = ["ViloxTermApp"]
