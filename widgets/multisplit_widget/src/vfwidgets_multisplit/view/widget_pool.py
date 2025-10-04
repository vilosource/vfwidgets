"""
WidgetPool - Production Implementation

Fixed container for all pane widgets in the MultisplitWidget.
Part of the Fixed Container Architecture (Layer 1).
"""

from typing import Optional

from PySide6.QtWidgets import QWidget


class WidgetPool:
    """
    Manages a fixed container for all pane widgets.

    Key Principle: Widgets are added ONCE via setParent() and never reparented.
    This eliminates GPU texture re-synchronization flashes in QWebEngineView.

    Architecture:
        - Layer 1: WidgetPool (this class) - Fixed container
        - Layer 2: GeometryManager - Pure calculation
        - Layer 3: VisualRenderer - Geometry application
    """

    def __init__(self, container: QWidget):
        """
        Initialize the widget pool.

        Args:
            container: The fixed parent widget for ALL pane widgets.
                      This container never changes for the lifetime of the pool.
        """
        self._container = container
        self._widgets: dict[str, QWidget] = {}
        self._visible_panes: set[str] = set()

    def add_widget(self, pane_id: str, widget: QWidget) -> None:
        """
        Add a widget to the pool.

        CRITICAL: This is the ONLY place where setParent() is called on pane widgets.
        After this point, the widget NEVER moves to a different parent.

        Args:
            pane_id: Unique identifier for the pane
            widget: The widget to add

        Raises:
            ValueError: If a widget for this pane_id already exists
        """
        if pane_id in self._widgets:
            raise ValueError(f"Widget for pane '{pane_id}' already exists in pool")

        # ONLY reparenting point in the entire system
        widget.setParent(self._container)
        widget.setVisible(False)  # Hidden by default, renderer controls visibility
        widget.lower()  # Start at bottom of z-order

        self._widgets[pane_id] = widget

    def remove_widget(self, pane_id: str) -> None:
        """
        Remove a widget from the pool and delete it.

        Args:
            pane_id: Identifier of the pane to remove
        """
        if pane_id not in self._widgets:
            return

        widget = self._widgets[pane_id]

        # Clean up visibility tracking
        self._visible_panes.discard(pane_id)

        # Detach and schedule for deletion
        widget.setParent(None)
        widget.deleteLater()

        del self._widgets[pane_id]

    def get_widget(self, pane_id: str) -> Optional[QWidget]:
        """
        Get a widget from the pool.

        Args:
            pane_id: Identifier of the pane

        Returns:
            The widget, or None if not found
        """
        return self._widgets.get(pane_id)

    def has_widget(self, pane_id: str) -> bool:
        """
        Check if a widget exists in the pool.

        Args:
            pane_id: Identifier of the pane

        Returns:
            True if the widget exists in the pool
        """
        return pane_id in self._widgets

    def get_all_pane_ids(self) -> set[str]:
        """
        Get all pane IDs in the pool.

        Returns:
            Set of all pane IDs
        """
        return set(self._widgets.keys())

    def mark_visible(self, pane_id: str) -> None:
        """
        Mark a pane as visible.

        Used for tracking which panes should be visible after layout updates.

        Args:
            pane_id: Identifier of the pane
        """
        self._visible_panes.add(pane_id)

    def mark_hidden(self, pane_id: str) -> None:
        """
        Mark a pane as hidden.

        Args:
            pane_id: Identifier of the pane
        """
        self._visible_panes.discard(pane_id)

    def get_visible_panes(self) -> set[str]:
        """
        Get all panes marked as visible.

        Returns:
            Set of pane IDs that should be visible
        """
        return self._visible_panes.copy()

    def hide_all(self) -> None:
        """
        Hide all widgets in the pool.

        Used when preparing for a full re-render.
        """
        for widget in self._widgets.values():
            widget.setVisible(False)
        self._visible_panes.clear()

    def clear(self) -> None:
        """
        Remove and delete all widgets from the pool.

        Used during cleanup/destruction.
        """
        for pane_id in list(self._widgets.keys()):
            self.remove_widget(pane_id)

    def __len__(self) -> int:
        """Return the number of widgets in the pool."""
        return len(self._widgets)

    def __contains__(self, pane_id: str) -> bool:
        """Check if a pane_id exists in the pool."""
        return pane_id in self._widgets
