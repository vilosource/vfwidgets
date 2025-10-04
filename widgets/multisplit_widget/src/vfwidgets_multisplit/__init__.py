"""MultisplitWidget - A custom PySide6 widget for dynamic split panes.

Exports:
    MultisplitWidget: Main widget class
    SplitterStyle: Splitter appearance configuration
    WherePosition: Pane placement positions (LEFT, RIGHT, TOP, BOTTOM, REPLACE)
    Direction: Focus navigation directions (UP, DOWN, LEFT, RIGHT)
    WidgetProvider: Protocol for widget creation

Example:
    from vfwidgets_multisplit import (
        MultisplitWidget,
        WidgetProvider,
        WherePosition,
        Direction,
        SplitterStyle
    )

    class MyProvider(WidgetProvider):
        def provide_widget(self, widget_id, pane_id):
            return QTextEdit()

        def widget_closing(self, widget_id, pane_id, widget):
            # Optional: cleanup before widget removal
            pass

    multisplit = MultisplitWidget(provider=MyProvider())
    multisplit.split_pane(pane_id, "new-widget", WherePosition.RIGHT)
"""

__version__ = "0.1.0"

from .core.types import Direction, SplitterStyle, WherePosition
from .multisplit import MultisplitWidget
from .view.container import WidgetProvider

__all__ = [
    "MultisplitWidget",
    "WidgetProvider",
    "WherePosition",
    "Direction",
    "SplitterStyle",
]
