"""Pluggable markdown rendering engines.

This module defines the abstract RendererProtocol and provides
concrete implementations for different rendering backends.
"""

from .base import RendererCapabilities, RendererProtocol, RenderResult
from .markdown_it import MarkdownItRenderer

__all__ = [
    "RendererProtocol",
    "RendererCapabilities",
    "RenderResult",
    "MarkdownItRenderer",
]
