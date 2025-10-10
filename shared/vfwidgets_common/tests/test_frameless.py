"""Tests for FramelessWindowBehavior."""

import pytest
from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QWidget
from vfwidgets_common import FramelessWindowBehavior


class MockWidget(QWidget):
    """Mock widget for testing."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(0, 0, 800, 600)
        self.cursor_set = None
        self._mock_window_handle = MockWindowHandle()

    def setCursor(self, cursor):
        """Track cursor changes."""
        self.cursor_set = cursor
        super().setCursor(cursor)

    def windowHandle(self):
        """Mock window handle."""
        return self._mock_window_handle


class MockWindowHandle:
    """Mock window handle for testing native APIs."""

    def __init__(self):
        self.system_move_called = False
        self.system_resize_called = False
        self.system_resize_edge = None

    def startSystemMove(self):
        """Mock startSystemMove."""
        self.system_move_called = True

    def startSystemResize(self, edge):
        """Mock startSystemResize."""
        self.system_resize_called = True
        self.system_resize_edge = edge


class TestFramelessWindowBehavior:
    """Test suite for FramelessWindowBehavior."""

    def test_init_default(self):
        """Test default initialization."""
        behavior = FramelessWindowBehavior()

        assert behavior.resize_margin == 5
        assert behavior.enable_resize is True
        assert behavior.enable_drag is True
        assert behavior.enable_double_click_maximize is True
        assert behavior.draggable_widget is None

    def test_init_custom(self, qtbot):
        """Test custom initialization."""
        widget = QWidget()
        qtbot.addWidget(widget)
        behavior = FramelessWindowBehavior(
            draggable_widget=widget,
            resize_margin=10,
            enable_resize=False,
            enable_drag=False,
        )

        assert behavior.draggable_widget is widget
        assert behavior.resize_margin == 10
        assert behavior.enable_resize is False
        assert behavior.enable_drag is False

    def test_get_resize_edge_top_left(self, qtbot):
        """Test edge detection for top-left corner."""
        widget = MockWidget()
        qtbot.addWidget(widget)
        behavior = FramelessWindowBehavior(resize_margin=5)

        # Top-left corner (within 5px margin)
        edge = behavior._get_resize_edge(widget, QPoint(2, 2))
        assert edge == (Qt.Edge.LeftEdge | Qt.Edge.TopEdge)

    def test_get_resize_edge_top_right(self, qtbot):
        """Test edge detection for top-right corner."""
        widget = MockWidget()
        qtbot.addWidget(widget)
        behavior = FramelessWindowBehavior(resize_margin=5)

        # Top-right corner
        edge = behavior._get_resize_edge(widget, QPoint(798, 2))
        assert edge == (Qt.Edge.RightEdge | Qt.Edge.TopEdge)

    def test_get_resize_edge_bottom_left(self, qtbot):
        """Test edge detection for bottom-left corner."""
        widget = MockWidget()
        qtbot.addWidget(widget)
        behavior = FramelessWindowBehavior(resize_margin=5)

        # Bottom-left corner
        edge = behavior._get_resize_edge(widget, QPoint(2, 598))
        assert edge == (Qt.Edge.LeftEdge | Qt.Edge.BottomEdge)

    def test_get_resize_edge_bottom_right(self, qtbot):
        """Test edge detection for bottom-right corner."""
        widget = MockWidget()
        qtbot.addWidget(widget)
        behavior = FramelessWindowBehavior(resize_margin=5)

        # Bottom-right corner
        edge = behavior._get_resize_edge(widget, QPoint(798, 598))
        assert edge == (Qt.Edge.RightEdge | Qt.Edge.BottomEdge)

    def test_get_resize_edge_left(self, qtbot):
        """Test edge detection for left edge."""
        widget = MockWidget()
        qtbot.addWidget(widget)
        behavior = FramelessWindowBehavior(resize_margin=5)

        # Left edge (not corner)
        edge = behavior._get_resize_edge(widget, QPoint(2, 300))
        assert edge == Qt.Edge.LeftEdge

    def test_get_resize_edge_right(self, qtbot):
        """Test edge detection for right edge."""
        widget = MockWidget()
        qtbot.addWidget(widget)
        behavior = FramelessWindowBehavior(resize_margin=5)

        # Right edge
        edge = behavior._get_resize_edge(widget, QPoint(798, 300))
        assert edge == Qt.Edge.RightEdge

    def test_get_resize_edge_top(self, qtbot):
        """Test edge detection for top edge."""
        widget = MockWidget()
        qtbot.addWidget(widget)
        behavior = FramelessWindowBehavior(resize_margin=5)

        # Top edge
        edge = behavior._get_resize_edge(widget, QPoint(400, 2))
        assert edge == Qt.Edge.TopEdge

    def test_get_resize_edge_bottom(self, qtbot):
        """Test edge detection for bottom edge."""
        widget = MockWidget()
        qtbot.addWidget(widget)
        behavior = FramelessWindowBehavior(resize_margin=5)

        # Bottom edge
        edge = behavior._get_resize_edge(widget, QPoint(400, 598))
        assert edge == Qt.Edge.BottomEdge

    def test_get_resize_edge_center(self, qtbot):
        """Test no edge detection in center."""
        widget = MockWidget()
        qtbot.addWidget(widget)
        behavior = FramelessWindowBehavior(resize_margin=5)

        # Center (no edge)
        edge = behavior._get_resize_edge(widget, QPoint(400, 300))
        assert edge == Qt.Edge(0)

    def test_get_resize_edge_disabled(self, qtbot):
        """Test edge detection when resize is disabled."""
        widget = MockWidget()
        qtbot.addWidget(widget)
        behavior = FramelessWindowBehavior(enable_resize=False)

        # Should always return no edge when resize disabled
        edge = behavior._get_resize_edge(widget, QPoint(2, 2))
        assert edge == Qt.Edge(0)

    def test_update_cursor_top_left_corner(self, qtbot):
        """Test cursor update for top-left corner."""
        widget = MockWidget()
        qtbot.addWidget(widget)
        behavior = FramelessWindowBehavior()

        behavior._update_cursor_for_edge(widget, Qt.Edge.TopEdge | Qt.Edge.LeftEdge)
        assert widget.cursor_set == Qt.CursorShape.SizeFDiagCursor

    def test_update_cursor_top_right_corner(self, qtbot):
        """Test cursor update for top-right corner."""
        widget = MockWidget()
        qtbot.addWidget(widget)
        behavior = FramelessWindowBehavior()

        behavior._update_cursor_for_edge(widget, Qt.Edge.TopEdge | Qt.Edge.RightEdge)
        assert widget.cursor_set == Qt.CursorShape.SizeBDiagCursor

    def test_update_cursor_horizontal(self, qtbot):
        """Test cursor update for horizontal edges."""
        widget = MockWidget()
        qtbot.addWidget(widget)
        behavior = FramelessWindowBehavior()

        behavior._update_cursor_for_edge(widget, Qt.Edge.LeftEdge)
        assert widget.cursor_set == Qt.CursorShape.SizeHorCursor

    def test_update_cursor_vertical(self, qtbot):
        """Test cursor update for vertical edges."""
        widget = MockWidget()
        qtbot.addWidget(widget)
        behavior = FramelessWindowBehavior()

        behavior._update_cursor_for_edge(widget, Qt.Edge.TopEdge)
        assert widget.cursor_set == Qt.CursorShape.SizeVerCursor

    def test_update_cursor_no_edge(self, qtbot):
        """Test cursor update when no edge."""
        widget = MockWidget()
        qtbot.addWidget(widget)
        behavior = FramelessWindowBehavior()

        behavior._update_cursor_for_edge(widget, Qt.Edge(0))
        assert widget.cursor_set == Qt.CursorShape.ArrowCursor

    def test_is_draggable_area_with_widget(self, qtbot):
        """Test draggable area detection with specific widget."""
        parent = MockWidget()
        qtbot.addWidget(parent)
        draggable = QWidget(parent)
        draggable.setGeometry(0, 0, 800, 30)  # Title bar area

        behavior = FramelessWindowBehavior(draggable_widget=draggable)

        # Position in draggable widget
        assert behavior._is_in_draggable_area(parent, QPoint(400, 15)) is True

        # Position outside draggable widget
        assert behavior._is_in_draggable_area(parent, QPoint(400, 100)) is False

    def test_is_draggable_area_with_callback(self, qtbot):
        """Test draggable area detection with custom callback."""
        widget = MockWidget()
        qtbot.addWidget(widget)
        called_with = []

        def custom_check(w, pos):
            called_with.append((w, pos))
            return pos.y() < 30  # Top 30px is draggable

        behavior = FramelessWindowBehavior(is_draggable_area=custom_check)

        result = behavior._is_in_draggable_area(widget, QPoint(400, 15))
        assert result is True
        assert len(called_with) == 1
        assert called_with[0][0] is widget

    def test_is_draggable_area_default(self, qtbot):
        """Test default draggable area (no widget, no callback)."""
        widget = MockWidget()
        qtbot.addWidget(widget)
        behavior = FramelessWindowBehavior()

        # Default should be False (no draggable area defined)
        assert behavior._is_in_draggable_area(widget, QPoint(400, 15)) is False

    def test_custom_resize_margin(self, qtbot):
        """Test custom resize margin."""
        widget = MockWidget()
        qtbot.addWidget(widget)
        behavior = FramelessWindowBehavior(resize_margin=10)

        # Just inside 10px margin
        edge = behavior._get_resize_edge(widget, QPoint(9, 300))
        assert edge == Qt.Edge.LeftEdge

        # Just outside 10px margin
        edge = behavior._get_resize_edge(widget, QPoint(11, 300))
        assert edge == Qt.Edge(0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
