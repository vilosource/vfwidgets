"""
Visual Testing Framework for VFWidgets Theme System

This module provides screenshot-based visual regression testing capabilities:
- Widget rendering capture
- Image comparison with tolerance
- Visual diff generation
- Baseline management
- CI/CD integration support
"""

from .framework import VisualTestFramework
from .comparison import ImageComparator
from .diff_generator import DiffGenerator

__all__ = [
    "VisualTestFramework",
    "ImageComparator",
    "DiffGenerator"
]