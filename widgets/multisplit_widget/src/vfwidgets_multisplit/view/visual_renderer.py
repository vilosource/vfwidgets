"""
VisualRenderer - Production Implementation

Applies widget geometries using ONLY setGeometry() - no reparenting.
Part of the Fixed Container Architecture (Layer 3).
"""

from typing import Optional

from PySide6.QtCore import QRect
from PySide6.QtWidgets import QWidget

from ..core.types import PaneId
from .widget_pool import WidgetPool


class VisualRenderer:
    """
    Applies widget geometries without reparenting.

    This is the third layer of the Fixed Container Architecture.
    It uses ONLY setGeometry() to position widgets - no tree building, no reparenting.

    Architecture:
        - Layer 1: WidgetPool - Fixed container
        - Layer 2: GeometryManager - Pure calculation
        - Layer 3: VisualRenderer (this class) - Geometry application
    """

    def __init__(self, widget_pool: WidgetPool, focus_border: Optional[QWidget] = None):
        """
        Initialize the visual renderer.

        Args:
            widget_pool: The widget pool to get widgets from
            focus_border: Optional focus border widget for visualization
        """
        self._pool = widget_pool
        self._focus_border = focus_border
        self._focused_pane_id: Optional[PaneId] = None

    def render(self, geometries: dict[str, QRect]) -> None:
        """
        Apply geometries to widgets.

        CRITICAL: This method uses ONLY setGeometry() to position widgets.
        No reparenting occurs - widgets stay in the same parent (the pool container).

        Algorithm:
            1. Hide all widgets not in the geometry map
            2. For each geometry:
                - Get widget from pool
                - Apply geometry via setGeometry() (NO REPARENTING)
                - Show widget
                - Raise to ensure proper z-order

        Args:
            geometries: Dictionary mapping pane IDs to their target geometries
        """
        # Get set of panes that should be visible
        visible_panes = set(geometries.keys())

        # Hide panes not in the new layout
        all_panes = self._pool.get_all_pane_ids()
        for pane_id in all_panes:
            if pane_id not in visible_panes:
                widget = self._pool.get_widget(pane_id)
                if widget:
                    widget.setVisible(False)
                self._pool.mark_hidden(pane_id)

        # Apply geometries to visible panes
        for pane_id, geometry in geometries.items():
            widget = self._pool.get_widget(pane_id)
            if widget is None:
                continue

            # Track if widget is newly becoming visible
            was_hidden = not widget.isVisible()

            # CRITICAL: ONLY geometry change, NO reparenting
            widget.setGeometry(geometry)
            widget.setVisible(True)
            widget.raise_()  # Ensure proper z-order (front to back)

            # Only repaint() for newly visible widgets to prevent flash
            # For already-visible widgets being resized, use update() (async)
            # This gives QWebEngineView's GPU compositor time to adjust render buffer
            if was_hidden:
                widget.repaint()  # Force IMMEDIATE repaint for new widgets
            else:
                widget.update()  # Schedule repaint - gives GPU time to adjust

            self._pool.mark_visible(pane_id)

        # Update focus border if present
        self._update_focus_border()

    def set_focused_pane(self, pane_id: Optional[PaneId]) -> None:
        """
        Set the currently focused pane.

        Args:
            pane_id: ID of the pane to focus, or None to clear focus
        """
        self._focused_pane_id = pane_id
        self._update_focus_border()

    def _update_focus_border(self) -> None:
        """
        Update the focus border widget position.

        The focus border is a visual overlay that highlights the focused pane.
        """
        if not self._focus_border:
            return

        if not self._focused_pane_id:
            # No focus - hide the border
            self._focus_border.setVisible(False)
            return

        # Get the focused widget
        focused_widget = self._pool.get_widget(self._focused_pane_id)
        if not focused_widget or not focused_widget.isVisible():
            # Focused pane not visible - hide the border
            self._focus_border.setVisible(False)
            return

        # Position the border around the focused widget
        geometry = focused_widget.geometry()
        self._focus_border.setGeometry(geometry)
        self._focus_border.setVisible(True)
        self._focus_border.raise_()  # Ensure border is on top

    def hide_all(self) -> None:
        """
        Hide all widgets.

        Used when clearing the layout or during cleanup.
        """
        self._pool.hide_all()

        if self._focus_border:
            self._focus_border.setVisible(False)

    def get_visible_panes(self) -> set[str]:
        """
        Get the set of currently visible pane IDs.

        Returns:
            Set of pane IDs that are currently visible
        """
        return self._pool.get_visible_panes()
