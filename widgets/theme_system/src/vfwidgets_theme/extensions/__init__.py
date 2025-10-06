"""Extension system for theme framework.

This module provides a secure plugin system for extending theme capabilities.
Extensions are sandboxed for security and can provide additional theme
processing, custom widgets, and theme transformations.
"""

from .api import ExtensionAPI
from .loader import ExtensionLoader
from .sandbox import ExtensionSandbox
from .system import Extension, ExtensionSystem

__all__ = ["ExtensionSystem", "Extension", "ExtensionSandbox", "ExtensionAPI", "ExtensionLoader"]
