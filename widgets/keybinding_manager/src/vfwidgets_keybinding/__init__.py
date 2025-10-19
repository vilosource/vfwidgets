"""VFWidgets KeybindingManager - Configurable keyboard shortcuts for Qt applications.

A reusable widget library for managing customizable keyboard shortcuts in PySide6/PyQt6
applications. Provides action registry, keybinding management, persistence, and UI.

Quick Start:
    >>> from vfwidgets_keybinding import KeybindingManager, ActionDefinition
    >>>
    >>> manager = KeybindingManager("~/.config/myapp/keybindings.json")
    >>> manager.register_action(ActionDefinition(
    ...     id="file.save",
    ...     description="Save File",
    ...     default_shortcut="Ctrl+S",
    ...     category="File"
    ... ))
    >>> manager.apply_shortcuts(main_window)

Version: 0.1.0 (Development)
"""

__version__ = "0.1.0"

from .manager import KeybindingManager
from .registry import ActionDefinition, ActionRegistry
from .storage import KeybindingStorage

# UI widgets (optional, for preferences dialogs)
from .widgets import KeybindingDialog, KeySequenceEdit

__all__ = [
    # Main API (most users only need this)
    "KeybindingManager",
    "ActionDefinition",
    # UI Widgets
    "KeySequenceEdit",
    "KeybindingDialog",
    # Advanced usage
    "ActionRegistry",
    "KeybindingStorage",
    # Version
    "__version__",
]
