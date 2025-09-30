"""
Icon theme support for VSCode-compatible icon themes.

This module provides support for icon themes including file type icons,
folder icons, and custom icon sets. Supports both SVG icons and icon fonts.
"""

from .theme import IconTheme, IconProvider
from .font_loader import IconFontLoader
from .svg_handler import SVGIconHandler
from .file_associations import FileAssociationManager

__all__ = [
    'IconTheme',
    'IconProvider',
    'IconFontLoader',
    'SVGIconHandler',
    'FileAssociationManager'
]