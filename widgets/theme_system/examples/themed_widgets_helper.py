"""Helper module for creating themed Qt widgets in examples.

This module provides pre-configured themed versions of common Qt widgets
that will automatically respond to theme changes.
"""

from PySide6.QtWidgets import QLabel, QListWidget, QPushButton, QTextEdit

from vfwidgets_theme.widgets.base import create_themed_widget

# Create themed versions of common widgets
ThemedLabel = create_themed_widget(QLabel, theme_config={
    'color': 'foreground',
    'background-color': 'background',
})

ThemedTextEdit = create_themed_widget(QTextEdit, theme_config={
    'color': 'editor.foreground',
    'background-color': 'editor.background',
    'border': '1px solid',
    'border-color': 'editorWidget.border',
    'selection-color': 'editor.selectionBackground',
    'selection-background-color': 'editor.selectionForeground',
})

ThemedPushButton = create_themed_widget(QPushButton, theme_config={
    'color': 'button.foreground',
    'background-color': 'button.background',
    'border': '1px solid',
    'border-color': 'button.border',
    'padding': '5px 15px',
})

ThemedListWidget = create_themed_widget(QListWidget, theme_config={
    'color': 'list.foreground',
    'background-color': 'list.background',
    'border': '1px solid',
    'border-color': 'list.border',
})

__all__ = [
    'ThemedLabel',
    'ThemedTextEdit',
    'ThemedPushButton',
    'ThemedListWidget',
]
