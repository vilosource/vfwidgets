"""VFWidgets Theme System - Pattern Recognition.

This module provides pattern recognition capabilities for theme matching,
complementing the CSS selector system with additional pattern types.
"""

from .matcher import PatternMatcher, PatternPriority, PatternType
from .plugins import PatternPlugin, PluginManager

__all__ = [
    "PatternMatcher",
    "PatternType",
    "PatternPriority",
    "PluginManager",
    "PatternPlugin",
]
