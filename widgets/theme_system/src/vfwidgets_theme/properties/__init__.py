"""
Property system for theme management.

This module provides the enhanced property system for Phase 2,
including type-safe descriptors, validation, and caching.
"""

from .descriptors import PropertyDescriptor, ValidationError

__all__ = [
    "PropertyDescriptor",
    "ValidationError"
]