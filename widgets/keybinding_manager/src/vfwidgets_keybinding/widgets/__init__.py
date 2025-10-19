"""UI widgets for keyboard shortcut management.

This module provides reusable UI components for displaying and editing
keyboard shortcuts in Qt applications.
"""

from .key_sequence_edit import KeySequenceEdit
from .keybinding_dialog import KeybindingDialog

__all__ = [
    "KeySequenceEdit",
    "KeybindingDialog",
]
