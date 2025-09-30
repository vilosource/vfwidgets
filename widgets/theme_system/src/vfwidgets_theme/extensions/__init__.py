"""
Extension system for theme framework.

This module provides a secure plugin system for extending theme capabilities.
Extensions are sandboxed for security and can provide additional theme
processing, custom widgets, and theme transformations.
"""

from .system import ExtensionSystem, Extension
from .sandbox import ExtensionSandbox
from .api import ExtensionAPI
from .loader import ExtensionLoader

__all__ = [
    'ExtensionSystem',
    'Extension',
    'ExtensionSandbox',
    'ExtensionAPI',
    'ExtensionLoader'
]