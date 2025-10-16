"""UI components for Reamde."""

from .appearance_prefs_tab import AppearancePreferencesTab
from .general_prefs_tab import GeneralPreferencesTab
from .markdown_prefs_tab import MarkdownPreferencesTab
from .preferences_dialog import PreferencesDialog

__all__ = [
    "PreferencesDialog",
    "GeneralPreferencesTab",
    "AppearancePreferencesTab",
    "MarkdownPreferencesTab",
]
