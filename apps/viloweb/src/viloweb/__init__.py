"""ViloWeb - Modern web browser application.

ViloWeb is a full-featured web browser built with ViloCodeWindow and Qt WebEngine:
- VS Code-style window layout (activity bar, sidebar, main pane)
- Multiple tabs with Chrome-style tab widget (optional)
- Bookmark management with folders and persistence
- Browsing history with search
- Theme system integration
- Full keyboard shortcut support
"""

__version__ = "0.1.0"
__author__ = "Vilosource"
__email__ = "vilosource@viloforge.com"

from .app import ViloWebApp

__all__ = ["ViloWebApp"]
