"""
Components for ChromeTabbedWindow.

Contains UI components for Chrome-style rendering and window management.
"""

from .chrome_tab_renderer import ChromeTabRenderer, TabState
from .tab_animator import TabAnimator
from .window_controls import WindowControls

__all__ = ["WindowControls", "ChromeTabRenderer", "TabState", "TabAnimator"]
