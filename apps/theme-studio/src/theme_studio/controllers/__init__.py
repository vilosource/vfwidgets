"""Controllers - MVC Controller layer for Theme Studio.

The controller layer decouples UI interactions from document updates,
providing a clean command queue pattern to prevent lifecycle issues.
"""

from .theme_controller import ThemeController

__all__ = ["ThemeController"]
