"""
VFWidgets Theme System - Pattern Recognition

This module provides pattern recognition capabilities for theme matching,
complementing the CSS selector system with additional pattern types.
"""

from .matcher import PatternMatcher, PatternType, PatternPriority
from .plugins import PluginManager, PatternPlugin

__all__ = [
    "PatternMatcher",
    "PatternType",
    "PatternPriority",
    "PluginManager",
    "PatternPlugin",
]