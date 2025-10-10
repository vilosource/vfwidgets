"""Frameless window behavior for VFWidgets.

This module provides reusable frameless window dragging and resizing functionality
that can be composed into any QWidget-based frameless window widget.

Example usage:
    class MyFramelessWindow(QWidget):
        def __init__(self):
            super().__init__()

            # Set up frameless window flags
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

            # Create frameless behavior
            self._frameless = FramelessWindowBehavior(
                draggable_widget=self._title_bar,
                resize_margin=5,
                enable_resize=True,
            )

        def mousePressEvent(self, event):
            if self._frameless.handle_press(self, event):
                return
            super().mousePressEvent(event)
"""

from typing import Callable, Optional

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QWidget


class FramelessWindowBehavior:
    """Encapsulates frameless window dragging and resizing behavior.

    This class provides native window manager integration for window dragging
    and edge resizing, with automatic fallback to manual position updates for
    older Qt versions or platforms without native support.

    The behavior is designed to be composed into frameless window widgets rather
    than inherited, allowing for flexible widget hierarchies and avoiding MRO
    conflicts.

    Attributes:
        resize_margin: Pixel width of the resize edge detection area
        enable_resize: Whether to enable edge resizing
        enable_drag: Whether to enable window dragging
        enable_double_click_maximize: Whether double-click toggles maximize
    """

    def __init__(
        self,
        draggable_widget: Optional[QWidget] = None,
        resize_margin: int = 5,
        enable_resize: bool = True,
        enable_drag: bool = True,
        enable_double_click_maximize: bool = True,
        is_draggable_area: Optional[Callable[[QWidget, QPoint], bool]] = None,
    ):
        """Initialize frameless window behavior.

        Args:
            draggable_widget: Specific widget that should be draggable (e.g. title bar).
                            If None, uses position-based detection.
            resize_margin: Pixel width of edge detection for resizing
            enable_resize: Enable window edge resizing
            enable_drag: Enable window dragging
            enable_double_click_maximize: Enable double-click to maximize
            is_draggable_area: Optional callback to determine if position is draggable.
                             Takes (widget, pos) and returns bool.
        """
        self.draggable_widget = draggable_widget
        self.resize_margin = resize_margin
        self.enable_resize = enable_resize
        self.enable_drag = enable_drag
        self.enable_double_click_maximize = enable_double_click_maximize
        self.is_draggable_area = is_draggable_area

        # Internal state
        self._drag_position: Optional[QPoint] = None
        self._using_system_move: bool = False
        self._resize_edge: Qt.Edge = Qt.Edge(0)

    def handle_press(self, widget: QWidget, event: QMouseEvent) -> bool:
        """Handle mouse press event for window dragging and resizing.

        Args:
            widget: The widget receiving the event
            event: The mouse press event

        Returns:
            True if event was handled, False to propagate to widget
        """
        if event.button() != Qt.MouseButton.LeftButton:
            return False

        # Check for edge resize first
        if self.enable_resize:
            edge = self._get_resize_edge(widget, event.pos())
            if edge != Qt.Edge(0):
                self._resize_edge = edge
                return self._start_system_resize(widget, edge)

        # Check for draggable area
        if self.enable_drag and self._is_in_draggable_area(widget, event.pos()):
            return self._start_drag(widget, event)

        return False

    def handle_move(self, widget: QWidget, event: QMouseEvent) -> bool:
        """Handle mouse move event for window dragging and cursor updates.

        Args:
            widget: The widget receiving the event
            event: The mouse move event

        Returns:
            True if event was handled, False to propagate to widget
        """
        # Handle manual drag (fallback when system move not available)
        if (
            self.enable_drag
            and event.buttons() == Qt.MouseButton.LeftButton
            and self._drag_position is not None
            and not self._using_system_move
        ):
            new_pos = event.globalPosition().toPoint() - self._drag_position
            widget.move(new_pos)
            event.accept()
            return True

        # Update cursor for resize edges when not dragging
        if self.enable_resize and not event.buttons():
            edge = self._get_resize_edge(widget, event.pos())
            self._update_cursor_for_edge(widget, edge)
            return True

        return False

    def handle_release(self, widget: QWidget, event: QMouseEvent) -> bool:
        """Handle mouse release event to clear drag state.

        Args:
            widget: The widget receiving the event
            event: The mouse release event

        Returns:
            True if event was handled, False to propagate to widget
        """
        if event.button() == Qt.MouseButton.LeftButton:
            # Clear drag state
            self._drag_position = None
            self._using_system_move = False
            self._resize_edge = Qt.Edge(0)
            return True

        return False

    def handle_double_click(self, widget: QWidget, event: QMouseEvent) -> bool:
        """Handle double-click to maximize/restore window.

        Args:
            widget: The widget receiving the event
            event: The double-click event

        Returns:
            True if event was handled, False to propagate to widget
        """
        if not self.enable_double_click_maximize:
            return False

        if event.button() == Qt.MouseButton.LeftButton:
            if self._is_in_draggable_area(widget, event.pos()):
                window = widget.window()
                if window.isMaximized():
                    window.showNormal()
                else:
                    window.showMaximized()
                event.accept()
                return True

        return False

    def _is_in_draggable_area(self, widget: QWidget, pos: QPoint) -> bool:
        """Check if position is in a draggable area.

        Args:
            widget: The widget to check
            pos: Position in widget coordinates

        Returns:
            True if position is in draggable area
        """
        # Use custom callback if provided
        if self.is_draggable_area:
            return self.is_draggable_area(widget, pos)

        # Check if draggable widget specified
        if self.draggable_widget:
            # Check if pos is within draggable widget's geometry
            return self.draggable_widget.geometry().contains(pos)

        # Default: no draggable area
        return False

    def _start_drag(self, widget: QWidget, event: QMouseEvent) -> bool:
        """Start window drag operation.

        Args:
            widget: The widget to drag
            event: The mouse press event

        Returns:
            True if drag started successfully
        """
        # Try native system move first (Qt 5.15+)
        if hasattr(widget.windowHandle(), "startSystemMove"):
            widget.windowHandle().startSystemMove()
            self._using_system_move = True
            event.accept()
            return True

        # Fallback to manual drag
        self._drag_position = event.globalPosition().toPoint() - widget.frameGeometry().topLeft()
        event.accept()
        return True

    def _start_system_resize(self, widget: QWidget, edge: Qt.Edge) -> bool:
        """Start system resize operation if supported.

        Args:
            widget: The widget to resize
            edge: The edge(s) to resize from

        Returns:
            True if resize started successfully
        """
        # Try Qt's native window resizing (Qt 5.15+)
        if hasattr(widget.windowHandle(), "startSystemResize"):
            widget.windowHandle().startSystemResize(edge)
            return True

        # Manual resize not implemented (would need more complex state tracking)
        return False

    def _get_resize_edge(self, widget: QWidget, pos: QPoint) -> Qt.Edge:
        """Detect which edge/corner mouse is over for resizing.

        Args:
            widget: The widget to check
            pos: Position in widget coordinates

        Returns:
            Qt.Edge flags indicating which edge(s) are near
        """
        if not self.enable_resize:
            return Qt.Edge(0)

        rect = widget.rect()
        margin = self.resize_margin

        edges = Qt.Edge(0)

        # Check horizontal edges
        if pos.x() <= margin:
            edges |= Qt.Edge.LeftEdge
        elif pos.x() >= rect.width() - margin:
            edges |= Qt.Edge.RightEdge

        # Check vertical edges
        if pos.y() <= margin:
            edges |= Qt.Edge.TopEdge
        elif pos.y() >= rect.height() - margin:
            edges |= Qt.Edge.BottomEdge

        return edges

    def _update_cursor_for_edge(self, widget: QWidget, edge: Qt.Edge) -> None:
        """Update the mouse cursor based on the resize edge.

        Args:
            widget: The widget to update cursor for
            edge: The edge(s) near the mouse cursor
        """
        if edge == Qt.Edge(0):  # No edge
            widget.setCursor(Qt.CursorShape.ArrowCursor)
        elif edge == (Qt.Edge.TopEdge | Qt.Edge.LeftEdge):
            widget.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif edge == (Qt.Edge.TopEdge | Qt.Edge.RightEdge):
            widget.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif edge == (Qt.Edge.BottomEdge | Qt.Edge.LeftEdge):
            widget.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif edge == (Qt.Edge.BottomEdge | Qt.Edge.RightEdge):
            widget.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif edge == Qt.Edge.LeftEdge or edge == Qt.Edge.RightEdge:
            widget.setCursor(Qt.CursorShape.SizeHorCursor)
        elif edge == Qt.Edge.TopEdge or edge == Qt.Edge.BottomEdge:
            widget.setCursor(Qt.CursorShape.SizeVerCursor)
        else:
            widget.setCursor(Qt.CursorShape.ArrowCursor)
