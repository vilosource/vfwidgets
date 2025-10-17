"""Python ↔ JavaScript communication layer.

This module provides abstractions for bidirectional communication
between Python and JavaScript, including theme application and
general message passing.
"""

from .theme_bridge import ThemeApplicationResult, ThemeBridge, ThemeTokenMapping

__all__ = ["ThemeBridge", "ThemeTokenMapping", "ThemeApplicationResult"]
