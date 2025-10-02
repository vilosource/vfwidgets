"""
Visual Testing Framework for VFWidgets Theme System

This module provides screenshot-based visual regression testing capabilities:
- Widget rendering capture
- Image comparison with tolerance
- Visual diff generation
- Baseline management
- CI/CD integration support
"""

from .comparison import ImageComparator
from .diff_generator import DiffGenerator
from .framework import VisualTestFramework

__all__ = [
    "VisualTestFramework",
    "ImageComparator",
    "DiffGenerator"
]
