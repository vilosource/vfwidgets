"""
Theme Persistence Module

This module provides theme persistence capabilities including:
- JSON serialization and deserialization
- Theme validation on load
- Automatic backup before save
- Migration support for old formats
- Compression for large themes
"""

from .storage import (
    ThemePersistence,
    ThemeValidationResult,
    PersistenceError,
    ThemeFormatError,
    BackupManager,
)

__all__ = [
    'ThemePersistence',
    'ThemeValidationResult',
    'PersistenceError',
    'ThemeFormatError',
    'BackupManager',
]