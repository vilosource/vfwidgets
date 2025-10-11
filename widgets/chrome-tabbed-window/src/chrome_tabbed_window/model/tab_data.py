"""
Tab data structure for ChromeTabbedWindow.

Stores all data associated with a single tab, matching QTabWidget's data model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget


@dataclass
class TabData:
    """
    Data for a single tab matching QTabWidget's data structure.

    This is a pure data class with no behavior. All logic is in TabModel.
    """

    # Core data matching QTabWidget
    widget: Optional[QWidget] = None
    text: str = ""
    icon: Optional[QIcon] = None
    tool_tip: str = ""
    whats_this: str = ""
    enabled: bool = True
    visible: bool = True

    # Internal tracking
    index: int = -1
    data: dict[int, Any] = field(default_factory=dict)  # Custom user data

    def __post_init__(self) -> None:
        """Validate initial state."""
        if self.widget is not None and not isinstance(self.widget, QWidget):
            raise TypeError(f"widget must be QWidget or None, got {type(self.widget)}")

        if self.icon is not None and not isinstance(self.icon, QIcon):
            raise TypeError(f"icon must be QIcon or None, got {type(self.icon)}")

    def copy(self) -> TabData:
        """Create a shallow copy of the tab data."""
        return TabData(
            widget=self.widget,
            text=self.text,
            icon=self.icon,
            tool_tip=self.tool_tip,
            whats_this=self.whats_this,
            enabled=self.enabled,
            visible=self.visible,
            index=self.index,
            data=self.data.copy(),
        )
