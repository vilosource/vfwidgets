"""Metadata for theme-studio editing.

This package contains metadata registries that provide descriptions, defaults,
and validation for theme tokens being edited.
"""

from .font_token_metadata import (
    FontTokenCategory,
    FontTokenInfo,
    FontTokenMetadataRegistry,
)

__all__ = [
    "FontTokenCategory",
    "FontTokenInfo",
    "FontTokenMetadataRegistry",
]
