"""Syntax highlighting engine for TextMate grammar support.

This module provides TextMate grammar-based syntax highlighting
compatible with VSCode themes and language definitions.
"""

from .grammar import GrammarLoader, TextMateGrammar
from .highlighter import SyntaxHighlighter, Token, TokenType
from .language_detector import LanguageDetector
from .theme_mapper import ThemeColorMapper

__all__ = [
    "SyntaxHighlighter",
    "Token",
    "TokenType",
    "TextMateGrammar",
    "GrammarLoader",
    "LanguageDetector",
    "ThemeColorMapper",
]
