"""Theme Package Manager System - Task 20.

This module provides theme packaging and distribution management:
- ThemePackageManager: Main package management interface
- .vftheme format support for packaging themes
- Dependency resolution and version management
- Installation and uninstallation of theme packages
"""

from .manager import ThemePackage, ThemePackageManager

__all__ = ["ThemePackageManager", "ThemePackage"]
