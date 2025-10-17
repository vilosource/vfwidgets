"""UI components for ViloWeb.

This package contains all UI-related classes:
- MainWindow: Top-level browser window with tab management (v0.1.0 - legacy)
- ChromeMainWindow: Chrome-style frameless browser window (v0.2.0 - current)
"""

from .chrome_main_window import ChromeMainWindow
from .main_window import MainWindow

__all__ = ["ChromeMainWindow", "MainWindow"]
