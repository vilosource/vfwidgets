"""
Tab model for ChromeTabbedWindow.

Manages all tab data and emits signals for state changes.
Follows Qt Model pattern with exact QTabWidget behavior.
"""

from __future__ import annotations

from typing import Any, Optional

from PySide6.QtCore import Property, QObject, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget

from .tab_data import TabData


class TabModel(QObject):
    """
    Model that manages tab data and state for ChromeTabbedWindow.

    Matches QTabWidget's internal data model exactly, including:
    - Tab data management
    - Current index tracking
    - Signal emission for all state changes
    - Property notifications
    """

    # Signals matching QTabWidget exactly
    currentChanged = Signal(int)  # index
    tabCloseRequested = Signal(int)  # index
    tabBarClicked = Signal(int)  # index
    tabBarDoubleClicked = Signal(int)  # index

    # Tab editing signals (new in v1.1)
    tabRenameStarted = Signal(int)  # index
    tabRenameFinished = Signal(int, str)  # index, new_text
    tabRenameCancelled = Signal(int)  # index

    # Internal model signals (not exposed in v1.0)
    _tabAdded = Signal(int)  # index
    _tabRemoved = Signal(int)  # index
    _tabMoved = Signal(int, int)  # from, to
    _tabTextChanged = Signal(int)  # index
    _tabIconChanged = Signal(int)  # index

    def __init__(self, parent: Optional[QObject] = None) -> None:
        """Initialize the tab model."""
        super().__init__(parent)

        self._tabs: list[TabData] = []
        self._current_index: int = -1

        # QTabWidget compatible properties
        self._tab_position: int = 0  # North
        self._tab_shape: int = 0  # Rounded
        self._elide_mode: int = 0  # Qt.TextElideMode.ElideNone
        self._uses_scroll_buttons: bool = True
        self._document_mode: bool = False
        self._tabs_closable: bool = False
        self._movable: bool = False
        self._tabs_editable: bool = False  # New in v1.1: inline tab text editing
        self._icon_size = None  # Will use default

    # ==================== Core Tab Management ====================

    def add_tab(
        self, widget: Optional[QWidget], text: str = "", icon: Optional[QIcon] = None
    ) -> int:
        """
        Add a new tab to the model.

        Returns the index of the added tab.
        Matches QTabWidget.addTab() exactly.
        """
        # Just delegate to insert_tab to avoid duplicate logic
        return self.insert_tab(len(self._tabs), widget, text, icon)

    def insert_tab(
        self, index: int, widget: Optional[QWidget], text: str = "", icon: Optional[QIcon] = None
    ) -> int:
        """
        Insert a tab at the specified index.

        Returns the actual index where the tab was inserted.
        Matches QTabWidget.insertTab() exactly.
        """
        if widget is not None and not isinstance(widget, QWidget):
            return -1  # QTabWidget behavior

        # Clamp index to valid range (QTabWidget behavior)
        index = max(0, min(index, len(self._tabs)))

        tab_data = TabData(widget=widget, text=text, icon=icon, index=index)

        self._tabs.insert(index, tab_data)

        # Update indices for all tabs after insertion point
        for i in range(index + 1, len(self._tabs)):
            self._tabs[i].index = i

        self._tabAdded.emit(index)

        # QTabWidget behavior: if inserting before current, update index
        if index <= self._current_index and self._current_index >= 0:
            self._current_index += 1

        # First tab becomes current
        if len(self._tabs) == 1:
            self.set_current_index(0)

        return index

    def remove_tab(self, index: int) -> None:
        """
        Remove the tab at the specified index.

        Matches QTabWidget.removeTab() exactly including:
        - Current index adjustment
        - Signal emission
        - No-op for invalid indices
        """
        if not self.is_valid_index(index):
            return  # QTabWidget behavior: silently ignore

        was_current = index == self._current_index
        tab_count_before = len(self._tabs)

        # Remove the tab
        removed_tab = self._tabs.pop(index)

        # Clear parent if widget exists (QTabWidget behavior)
        if removed_tab.widget:
            removed_tab.widget.setParent(None)

        # Update indices for remaining tabs
        for i in range(index, len(self._tabs)):
            self._tabs[i].index = i

        self._tabRemoved.emit(index)

        # Handle current index update (QTabWidget logic)
        if tab_count_before == 1:
            # Last tab removed
            self._current_index = -1
            self.currentChanged.emit(-1)
        elif was_current:
            # Current tab was removed
            if index < len(self._tabs):
                # Select next tab (same index position)
                self.set_current_index(index)
            elif len(self._tabs) > 0:
                # Was last tab, select new last
                self.set_current_index(len(self._tabs) - 1)
            else:
                self._current_index = -1
                self.currentChanged.emit(-1)
        elif index < self._current_index:
            # Removed before current, adjust index
            self._current_index -= 1

    def move_tab(self, from_index: int, to_index: int) -> None:
        """
        Move a tab from one index to another.

        Matches QTabWidget's internal tab movement.
        """
        if not self.is_valid_index(from_index) or not self.is_valid_index(to_index):
            return

        if from_index == to_index:
            return

        tab = self._tabs.pop(from_index)
        self._tabs.insert(to_index, tab)

        # Update all affected indices
        start = min(from_index, to_index)
        end = max(from_index, to_index) + 1
        for i in range(start, end):
            if i < len(self._tabs):
                self._tabs[i].index = i

        # Update current index if needed
        if self._current_index == from_index:
            self._current_index = to_index
        elif from_index < self._current_index <= to_index:
            self._current_index -= 1
        elif to_index <= self._current_index < from_index:
            self._current_index += 1

        self._tabMoved.emit(from_index, to_index)

    # ==================== Tab Properties ====================

    def set_tab_text(self, index: int, text: str) -> None:
        """Set the text for the tab at index."""
        if not self.is_valid_index(index):
            return

        self._tabs[index].text = text
        self._tabTextChanged.emit(index)

    def tab_text(self, index: int) -> str:
        """Get the text for the tab at index."""
        if not self.is_valid_index(index):
            return ""
        return self._tabs[index].text

    def set_tab_icon(self, index: int, icon: QIcon) -> None:
        """Set the icon for the tab at index."""
        if not self.is_valid_index(index):
            return

        self._tabs[index].icon = icon
        self._tabIconChanged.emit(index)

    def tab_icon(self, index: int) -> Optional[QIcon]:
        """Get the icon for the tab at index."""
        if not self.is_valid_index(index):
            return QIcon()  # QTabWidget returns empty icon
        return self._tabs[index].icon or QIcon()

    def set_tab_tool_tip(self, index: int, tip: str) -> None:
        """Set the tooltip for the tab at index."""
        if not self.is_valid_index(index):
            return
        self._tabs[index].tool_tip = tip

    def tab_tool_tip(self, index: int) -> str:
        """Get the tooltip for the tab at index."""
        if not self.is_valid_index(index):
            return ""
        return self._tabs[index].tool_tip

    def set_tab_whats_this(self, index: int, text: str) -> None:
        """Set the What's This text for the tab at index."""
        if not self.is_valid_index(index):
            return
        self._tabs[index].whats_this = text

    def tab_whats_this(self, index: int) -> str:
        """Get the What's This text for the tab at index."""
        if not self.is_valid_index(index):
            return ""
        return self._tabs[index].whats_this

    def set_tab_enabled(self, index: int, enabled: bool) -> None:
        """Enable or disable the tab at index."""
        if not self.is_valid_index(index):
            return
        self._tabs[index].enabled = enabled

    def is_tab_enabled(self, index: int) -> bool:
        """Check if the tab at index is enabled."""
        if not self.is_valid_index(index):
            return False
        return self._tabs[index].enabled

    def set_tab_visible(self, index: int, visible: bool) -> None:
        """Show or hide the tab at index."""
        if not self.is_valid_index(index):
            return
        self._tabs[index].visible = visible

    def is_tab_visible(self, index: int) -> bool:
        """Check if the tab at index is visible."""
        if not self.is_valid_index(index):
            return False
        return self._tabs[index].visible

    def set_tab_data(self, index: int, data: Any) -> None:
        """Set custom data for the tab at index."""
        if not self.is_valid_index(index):
            return
        self._tabs[index].data[0] = data  # Qt.UserRole = 0

    def tab_data(self, index: int) -> Any:
        """Get custom data for the tab at index."""
        if not self.is_valid_index(index):
            return None
        return self._tabs[index].data.get(0)  # Qt.UserRole = 0

    def widget(self, index: int) -> Optional[QWidget]:
        """Get the widget for the tab at index."""
        if not self.is_valid_index(index):
            return None
        return self._tabs[index].widget

    # ==================== Current Index Management ====================

    def current_index(self) -> int:
        """Get the current tab index."""
        return self._current_index

    def set_current_index(self, index: int) -> None:
        """
        Set the current tab index.

        Emits currentChanged if the index actually changes.
        Matches QTabWidget.setCurrentIndex() exactly.
        """
        # QTabWidget behavior: clamp to valid range or -1
        if len(self._tabs) == 0 or index < 0:
            index = -1
        elif index >= len(self._tabs):
            return  # QTabWidget ignores out of bounds

        if index == self._current_index:
            return  # No change

        # Check if tab is enabled (QTabWidget won't switch to disabled)
        if index >= 0 and not self._tabs[index].enabled:
            return

        self._current_index = index

        # Always emit signal when index changes
        self.currentChanged.emit(index)

    def current_widget(self) -> Optional[QWidget]:
        """Get the widget of the current tab."""
        if self._current_index < 0 or self._current_index >= len(self._tabs):
            return None
        return self._tabs[self._current_index].widget

    def set_current_widget(self, widget: QWidget) -> None:
        """Set the current tab by widget."""
        for i, tab in enumerate(self._tabs):
            if tab.widget == widget:
                self.set_current_index(i)
                return

    # ==================== Tab Count and Validation ====================

    def count(self) -> int:
        """Get the number of tabs."""
        return len(self._tabs)

    def is_valid_index(self, index: int) -> bool:
        """Check if an index is valid."""
        return 0 <= index < len(self._tabs)

    def index_of(self, widget: QWidget) -> int:
        """Get the index of a widget, or -1 if not found."""
        for i, tab in enumerate(self._tabs):
            if tab.widget == widget:
                return i
        return -1

    def clear(self) -> None:
        """Remove all tabs."""
        while len(self._tabs) > 0:
            self.remove_tab(0)

    # ==================== Tab Bar Properties ====================

    def tabs_closable(self) -> bool:
        """Check if tabs show close buttons."""
        return self._tabs_closable

    def set_tabs_closable(self, closable: bool) -> None:
        """Set whether tabs show close buttons."""
        self._tabs_closable = closable

    def tabs_movable(self) -> bool:
        """Check if tabs can be moved."""
        return self._movable

    def set_tabs_movable(self, movable: bool) -> None:
        """Set whether tabs can be moved."""
        self._movable = movable

    def tabs_editable(self) -> bool:
        """
        Check if tabs can be renamed via double-click.

        Returns:
            True if tabs are editable, False otherwise
        """
        return self._tabs_editable

    def set_tabs_editable(self, editable: bool) -> None:
        """
        Set whether tabs can be renamed via double-click.

        Args:
            editable: True to enable inline tab editing, False to disable
        """
        self._tabs_editable = editable

    # ==================== Qt Properties ====================

    # Using Property for QML compatibility as per Qt patterns
    countProperty = Property(int, count, notify=_tabAdded)
    currentIndexProperty = Property(int, current_index, set_current_index, notify=currentChanged)
