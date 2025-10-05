"""Interactive divider widget for drag-to-resize functionality."""

from typing import Optional

from PySide6.QtCore import QPoint, QRect, Qt, Signal
from PySide6.QtGui import QColor, QCursor, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import QWidget

from ..core.types import Orientation, SplitterStyle

try:
    from vfwidgets_theme.core.manager import ThemeManager
    from vfwidgets_theme.core.tokens import ColorTokenRegistry
    from vfwidgets_theme.widgets.base import ThemedWidget
    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False


class DividerWidget(QWidget):
    """Interactive divider for resizing split panes.

    This widget sits in the gaps between panes and handles mouse
    interaction for drag-to-resize functionality.

    Signals:
        resize_requested: Emitted during drag for live preview (DOES NOT update model)
            Args: node_id (str), divider_index (int), delta_pixels (int)
        resize_committed: Emitted when drag completes (DOES update model via command)
            Args: node_id (str), divider_index (int), delta_pixels (int)
    """

    resize_requested = Signal(str, int, int)  # LIVE preview during drag
    resize_committed = Signal(str, int, int)  # Final commit when drag completes

    def __init__(self,
                 node_id: str,
                 divider_index: int,
                 orientation: Orientation,
                 style: Optional[SplitterStyle] = None,
                 parent: Optional[QWidget] = None):
        """Initialize divider widget.

        Args:
            node_id: ID of the SplitNode this divider belongs to
            divider_index: Index of this divider (0 = first gap, 1 = second gap, etc.)
            orientation: HORIZONTAL (vertical divider line) or VERTICAL (horizontal divider line)
            style: Visual styling configuration
            parent: Parent widget
        """
        super().__init__(parent)

        self.node_id = node_id
        self.divider_index = divider_index
        self.orientation = orientation
        self.style = style or SplitterStyle.comfortable()

        # Mouse tracking state
        self._dragging = False
        self._drag_start_pos: Optional[QPoint] = None
        self._drag_current_pos: Optional[QPoint] = None
        self._hover = False
        self._ignore_next_press = False  # Flag to ignore spurious mouse press after resize

        # CRITICAL: Prevent divider from stealing focus from pane widgets
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)

        # Set initial styling
        self._update_style()

        # Set cursor based on orientation
        if self.style.cursor_on_hover:
            if orientation == Orientation.HORIZONTAL:
                # Horizontal orientation = vertical divider = left-right resize
                self.setCursor(QCursor(Qt.CursorShape.SplitHCursor))
            else:
                # Vertical orientation = horizontal divider = up-down resize
                self.setCursor(QCursor(Qt.CursorShape.SplitVCursor))

    def _update_style(self):
        """Update widget styling based on current state."""
        # Determine background color
        if self._dragging:
            # Dragging state - use hover color or highlight
            bg_color = self._get_hover_color()
        elif self._hover and self.style.show_hover_effect:
            # Hover state
            bg_color = self._get_hover_color()
        else:
            # Normal state
            bg_color = self._get_normal_color()

        # Determine border color
        if self._hover and self.style.show_hover_effect:
            border_color = self.style.handle_hover_border or self._get_border_color()
        else:
            border_color = self.style.handle_border or "transparent"

        # If we have hit area padding, the widget is larger than the visible divider
        # We need to use a transparent background and draw the visible divider manually
        if self.style.hit_area_padding > 0:
            # Widget itself is transparent - we'll draw the visible divider in paintEvent
            stylesheet = """
                DividerWidget {
                    background-color: transparent;
                    border: none;
                }
            """
        else:
            # No padding - widget fills entire area, use simple stylesheet
            stylesheet = f"""
                DividerWidget {{
                    background-color: {bg_color};
                    border: {self.style.border_width}px solid {border_color};
                    border-radius: {self.style.border_radius}px;
                }}
            """
        self.setStyleSheet(stylesheet)

        # Store colors for paintEvent when using padding
        self._current_bg_color = bg_color
        self._current_border_color = border_color

    def _get_normal_color(self) -> str:
        """Get normal state background color."""
        if self.style.handle_bg:
            return self.style.handle_bg

        # Use theme color if available
        if THEME_AVAILABLE:
            try:
                theme_mgr = ThemeManager.get_instance()
                current_theme = theme_mgr.current_theme
                return ColorTokenRegistry.get('editor.background', current_theme)
            except Exception:
                pass

        # Fallback
        return "#2d2d30"

    def _get_hover_color(self) -> str:
        """Get hover/dragging state background color."""
        if self.style.handle_hover_bg:
            return self.style.handle_hover_bg

        # Use theme color if available
        if THEME_AVAILABLE:
            try:
                theme_mgr = ThemeManager.get_instance()
                current_theme = theme_mgr.current_theme
                return ColorTokenRegistry.get('list.hoverBackground', current_theme)
            except Exception:
                pass

        # Fallback
        return "#3c3c3c"

    def _get_border_color(self) -> str:
        """Get border color from theme."""
        if THEME_AVAILABLE:
            try:
                theme_mgr = ThemeManager.get_instance()
                current_theme = theme_mgr.current_theme
                return ColorTokenRegistry.get('widget.border', current_theme)
            except Exception:
                pass

        return "#555555"

    def enterEvent(self, event):
        """Handle mouse enter - show hover state."""
        self._hover = True
        self._update_style()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave - clear hover state."""
        if not self._dragging:  # Keep hover style while dragging
            self._hover = False
            self._update_style()
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press - start drag ONLY if hovering over divider."""
        if event.button() == Qt.MouseButton.LeftButton:
            # CRITICAL: Only handle clicks if we're actually hovering
            # This allows clicks to pass through to pane widgets when not on divider
            if not self._hover:
                event.ignore()  # Pass through to underlying pane widget
                return

            # Ignore spurious mouse press after resize
            if self._ignore_next_press:
                self._ignore_next_press = False
                event.accept()
                return

            self._dragging = True
            # Use global cursor position to track drag
            self._drag_start_global = QCursor.pos()
            self._update_style()
            # Start timer to poll mouse position during drag
            from PySide6.QtCore import QTimer
            self._drag_timer = QTimer(self)
            self._drag_timer.timeout.connect(self._update_drag_position)
            self._drag_timer.start(16)  # ~60 FPS
            event.accept()
        else:
            event.ignore()  # Pass non-left-click events through

    def _update_drag_position(self):
        """Timer callback to update drag position using global cursor."""
        if not self._dragging:
            return

        # Get global cursor position and convert to widget coordinates
        global_pos = QCursor.pos()
        local_pos = self.mapFromGlobal(global_pos)

        # Calculate delta from drag start
        global_delta = global_pos - self._drag_start_global
        if self.orientation == Orientation.HORIZONTAL:
            delta_pixels = global_delta.x()
        else:
            delta_pixels = global_delta.y()

        # Store for paint event
        self._drag_current_pos = local_pos

        # Emit live resize signal for real-time visual feedback
        if delta_pixels != 0 and (not hasattr(self, '_last_delta') or self._last_delta != delta_pixels):
            self._last_delta = delta_pixels
            self.resize_requested.emit(self.node_id, self.divider_index, delta_pixels)

        # Trigger repaint
        self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move - not used when using timer-based tracking."""
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release - end drag and commit final resize to model."""
        if event.button() == Qt.MouseButton.LeftButton and self._dragging:
            # Stop drag timer
            if hasattr(self, '_drag_timer'):
                self._drag_timer.stop()
                self._drag_timer.deleteLater()

            # Emit FINAL commit signal to update model (via SetRatiosCommand)
            final_delta = getattr(self, '_last_delta', 0)
            self.resize_committed.emit(self.node_id, self.divider_index, final_delta)

            self._dragging = False
            self._drag_current_pos = None
            if hasattr(self, '_last_delta'):
                delattr(self, '_last_delta')

            # Update style to remove dragging highlight
            # Check if still hovering
            if not self.underMouse():
                self._hover = False
            self._update_style()

            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        """Paint the divider with optional drag preview."""
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # If we have hit area padding, draw the centered visible divider
        if self.style.hit_area_padding > 0:
            padding = self.style.hit_area_padding
            bg_color = QColor(self._current_bg_color)
            border_color = QColor(self._current_border_color)

            if self.orientation == Orientation.HORIZONTAL:
                # Vertical divider - center horizontally within widget
                visible_rect = QRect(
                    padding,
                    0,
                    self.style.handle_width,
                    self.height()
                )
            else:
                # Horizontal divider - center vertically within widget
                visible_rect = QRect(
                    0,
                    padding,
                    self.width(),
                    self.style.handle_width
                )

            # Draw background
            painter.fillRect(visible_rect, bg_color)

            # Draw border if needed
            if self.style.border_width > 0 and border_color.alpha() > 0:
                pen = QPen(border_color)
                pen.setWidth(self.style.border_width)
                painter.setPen(pen)
                painter.drawRect(visible_rect)

        # Draw drag preview line if dragging
        if self._dragging and self._drag_start_pos and self._drag_current_pos:
            # Draw a highlighted line at the drag position
            pen = QPen(QColor(0, 102, 204, 180))  # Semi-transparent blue
            pen.setWidth(3)
            painter.setPen(pen)

            if self.orientation == Orientation.HORIZONTAL:
                # Vertical line for horizontal splits - draw at X offset from drag start
                drag_x = self._drag_current_pos.x()
                painter.drawLine(drag_x, 0, drag_x, self.height())
            else:
                # Horizontal line for vertical splits - draw at Y offset from drag start
                drag_y = self._drag_current_pos.y()
                painter.drawLine(0, drag_y, self.width(), drag_y)
