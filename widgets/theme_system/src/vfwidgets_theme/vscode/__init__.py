"""VSCode integration module for theme system.

This module provides integration with VSCode themes and marketplace,
allowing users to import and use VSCode themes directly.
"""

from .importer import VSCodeThemeImporter
from .marketplace import MarketplaceClient, ThemeExtension

__all__ = [
    'MarketplaceClient',
    'ThemeExtension',
    'VSCodeThemeImporter'
]
