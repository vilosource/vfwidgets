"""
Chrome-style tab bar view component.

Renders tabs with Chrome browser styling and animations.
Pure view component - no business logic, only rendering.
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QPoint, QRect, QSize, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QMouseEvent, QPainter, QPainterPath, QPaintEvent, QPen
from PySide6.QtWidgets import QSizePolicy, QTabBar, QWidget

from ..components import ChromeTabRenderer, TabState
from ..model import TabModel


class ChromeTabBar(QTabBar):
    """
    Chrome-style tab bar view.

    Renders tabs with Chrome's signature slanted edges and smooth animations.
    This is a pure view component - all data comes from TabModel.

    In v1.0, we extend QTabBar to ensure compatibility while customizing appearance.
    """

    # View signals for user interaction
    tabCloseClicked = Signal(int)  # Request to close tab at index
    tabMiddleClicked = Signal(int)  # Middle click on tab
    newTabRequested = Signal()  # Request to add new tab

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the Chrome tab bar."""
        super().__init__(parent)

        # Chrome styling constants
        self.TAB_HEIGHT = 34
        self.TAB_MIN_WIDTH = 100
        self.TAB_MAX_WIDTH = 240
        self.TAB_OVERLAP = 14
        self.TAB_CURVE = 8
        self.CLOSE_BUTTON_SIZE = 16

        # Chrome colors (light theme for v1.0)
        self.COLOR_BACKGROUND = QColor("#DEE1E6")
        self.COLOR_TAB_INACTIVE = QColor("#F4F6F8")
        self.COLOR_TAB_ACTIVE = QColor("#FFFFFF")
        self.COLOR_TAB_HOVER = QColor("#F8F9FA")
        self.COLOR_BORDER = QColor("#C1C4C9")
        self.COLOR_TEXT = QColor("#202124")
        self.COLOR_TEXT_INACTIVE = QColor("#5F6368")

        # Hover tracking
        self._hovered_tab = -1
        self._close_button_hovered = -1

        # New tab button
        self.new_tab_button_rect = QRect()
        self.new_tab_button_hovered = False
        self.new_tab_button_size = QSize(28, 28)

        # Drag and drop state
        self._drag_start_position = None
        self._dragged_tab_index = -1
        self._drag_indicator_position = -1
        self._is_dragging = False

        # Chrome-like tab constraints
        self.CHROME_MIN_TAB_WIDTH = 52  # Minimum width (favicon + close button)
        self.CHROME_MAX_TAB_WIDTH = ChromeTabRenderer.TAB_MAX_WIDTH

        # Animation removed - was causing tab removal sync issues

        # Set base properties
        self.setMouseTracking(True)
        self.setDocumentMode(True)
        self.setExpanding(False)  # Critical: allows tab compression
        self.setDrawBase(False)

        # Set size policy to expand horizontally
        size_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        size_policy.setHorizontalStretch(1)  # Ensure it stretches
        self.setSizePolicy(size_policy)

    def set_model(self, model: TabModel) -> None:
        """
        Connect to the tab model.

        The view observes the model for changes but never modifies it.
        """
        self._model = model

        # Connect to model signals for updates
        model._tabAdded.connect(self._on_tab_added)
        model._tabRemoved.connect(self._on_tab_removed)
        model._tabTextChanged.connect(self._on_tab_text_changed)
        model._tabIconChanged.connect(self._on_tab_icon_changed)
        model.currentChanged.connect(self._on_current_changed)

        # Initialize view from model
        self._sync_with_model()

    def _sync_with_model(self) -> None:
        """Synchronize view with current model state."""
        if not hasattr(self, '_model'):
            return

        # Clear and rebuild tabs
        while self.count() > 0:
            self.removeTab(0)

        for i in range(self._model.count()):
            self.addTab(self._model.tab_text(i))
            if self._model.tab_icon(i):
                self.setTabIcon(i, self._model.tab_icon(i))
            self.setTabToolTip(i, self._model.tab_tool_tip(i))
            self.setTabEnabled(i, self._model.is_tab_enabled(i))

        self.setCurrentIndex(self._model.current_index())

    def _on_tab_added(self, index: int) -> None:
        """Handle tab addition from model."""
        text = self._model.tab_text(index) if hasattr(self, '_model') else ""
        self.insertTab(index, text)

        # Animation removed to ensure proper sync

    def _on_tab_removed(self, index: int) -> None:
        """Handle tab removal from model."""
        if index < self.count():
            # For now, skip animation and directly remove tab to fix the sync issue
            # Animation can be re-enabled once the basic functionality works
            self.removeTab(index)

    def _on_tab_text_changed(self, index: int) -> None:
        """Handle tab text change from model."""
        if hasattr(self, '_model') and index < self.count():
            self.setTabText(index, self._model.tab_text(index))

    def _on_tab_icon_changed(self, index: int) -> None:
        """Handle tab icon change from model."""
        if hasattr(self, '_model') and index < self.count():
            self.setTabIcon(index, self._model.tab_icon(index))

    def _on_current_changed(self, index: int) -> None:
        """Handle current tab change from model."""
        if index != self.currentIndex():
            self.setCurrentIndex(index)

    # ==================== Chrome Rendering ====================

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Custom paint event for Chrome-style tabs.

        This is where the Chrome visual magic happens.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Use ChromeTabRenderer for background
        ChromeTabRenderer.draw_tab_bar_background(painter, self.rect())

        # No need to calculate here - tabSizeHint handles it

        # Paint tabs from back to front (inactive first, active last)
        for i in range(self.count()):
            if i != self.currentIndex():
                self._paint_chrome_tab_with_renderer(painter, i, False)

        # Paint active tab on top
        if self.currentIndex() >= 0:
            self._paint_chrome_tab_with_renderer(painter, self.currentIndex(), True)


        # Paint new tab button
        self.new_tab_button_rect = self._calculate_new_tab_button_position()
        state = TabState.HOVER if self.new_tab_button_hovered else TabState.NORMAL
        ChromeTabRenderer.draw_new_tab_button(painter, self.new_tab_button_rect, state)

        # Paint drag indicator if dragging
        if self._is_dragging and self._drag_indicator_position >= 0:
            self._paint_drag_indicator(painter)

    def _paint_chrome_tab_with_renderer(self, painter: QPainter, index: int, is_active: bool) -> None:
        """Paint a single Chrome-style tab using ChromeTabRenderer."""
        rect = self.tabRect(index)
        text = self.tabText(index)

        # Determine tab state
        if is_active:
            state = TabState.ACTIVE
        elif index == self._hovered_tab:
            state = TabState.HOVER
        else:
            state = TabState.NORMAL

        # Check if close button is hovered for this tab
        close_button_state = TabState.NORMAL
        if index == self._close_button_hovered and hasattr(self, '_model') and self._model.tabs_closable():
            close_button_state = TabState.HOVER

        # Use ChromeTabRenderer to draw the tab
        ChromeTabRenderer.draw_tab(
            painter,
            rect,
            text,
            state,
            has_close_button=True,
            is_closable=hasattr(self, '_model') and self._model.tabs_closable(),
            close_button_state=close_button_state
        )

    def _paint_chrome_tab(self, painter: QPainter, index: int, is_active: bool) -> None:
        """Paint a single Chrome-style tab."""
        rect = self.tabRect(index)

        # Determine colors
        if is_active:
            bg_color = self.COLOR_TAB_ACTIVE
            text_color = self.COLOR_TEXT
        elif index == self._hovered_tab:
            bg_color = self.COLOR_TAB_HOVER
            text_color = self.COLOR_TEXT
        else:
            bg_color = self.COLOR_TAB_INACTIVE
            text_color = self.COLOR_TEXT_INACTIVE

        # Create Chrome tab shape path
        path = self._create_chrome_tab_path(rect)

        # Fill tab
        painter.fillPath(path, QBrush(bg_color))

        # Draw border
        pen = QPen(self.COLOR_BORDER, 1)
        painter.setPen(pen)
        painter.drawPath(path)

        # Draw text
        text_rect = rect.adjusted(10, 0, -30, 0)  # Leave room for close button
        painter.setPen(text_color)
        text = self.tabText(index)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                        self.fontMetrics().elidedText(text, Qt.TextElideMode.ElideRight, text_rect.width()))

        # Draw close button if closable
        if hasattr(self, '_model') and self._model.tabs_closable():
            self._paint_close_button(painter, index, rect)

    def _create_chrome_tab_path(self, rect: QRect) -> QPainterPath:
        """Create the distinctive Chrome tab shape."""
        path = QPainterPath()

        # Chrome tabs have slanted edges
        slant = 10
        radius = self.TAB_CURVE

        # Start from bottom left
        path.moveTo(rect.left() - slant, rect.bottom())

        # Left slanted edge
        path.lineTo(rect.left() + slant, rect.top() + radius)

        # Top left curve
        path.quadTo(rect.left() + slant, rect.top(),
                   rect.left() + slant + radius, rect.top())

        # Top edge
        path.lineTo(rect.right() - slant - radius, rect.top())

        # Top right curve
        path.quadTo(rect.right() - slant, rect.top(),
                   rect.right() - slant, rect.top() + radius)

        # Right slanted edge
        path.lineTo(rect.right() + slant, rect.bottom())

        # Bottom edge
        path.lineTo(rect.left() - slant, rect.bottom())

        return path

    def _paint_close_button(self, painter: QPainter, index: int, tab_rect: QRect) -> None:
        """Paint the tab close button."""
        button_rect = self._close_button_rect(tab_rect)

        # Hover effect
        if index == self._close_button_hovered:
            painter.fillRect(button_rect, QColor("#E0E0E0"))

        # Draw X
        painter.setPen(QPen(self.COLOR_TEXT_INACTIVE, 1.5))
        margin = 4
        painter.drawLine(button_rect.left() + margin, button_rect.top() + margin,
                        button_rect.right() - margin, button_rect.bottom() - margin)
        painter.drawLine(button_rect.left() + margin, button_rect.bottom() - margin,
                        button_rect.right() - margin, button_rect.top() + margin)

    def _close_button_rect(self, tab_rect: QRect) -> QRect:
        """Get the close button rect for a tab."""
        # Match ChromeTabRenderer's positioning
        # ChromeTabRenderer places close button at: rect.right() - TAB_CURVE_WIDTH - 24
        # with size 16x16, where TAB_CURVE_WIDTH = 15
        size = self.CLOSE_BUTTON_SIZE  # 16
        x = tab_rect.right() - 15 - 24  # TAB_CURVE_WIDTH=15, offset=24
        y = tab_rect.center().y() - 8  # Center vertically (size/2=8)
        return QRect(x, y, size, size)

    # ==================== Mouse Handling ====================

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press events."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if new tab button clicked
            if self.new_tab_button_rect.contains(event.pos()):
                self.newTabRequested.emit()
                return

            index = self.tabAt(event.pos())
            # Double-validate tab index to prevent operations on non-existent tabs
            # Qt's tabAt() can return stale indices after tab removal due to deferred layout updates
            if index >= 0:
                # CRITICAL: Check if the index is actually valid BEFORE using it
                if index >= self.count():
                    # Qt returned an invalid index - treat as empty area click
                    event.ignore()
                    return

                # Now we know the index is truly valid
                # Check if close button clicked
                tab_rect = self.tabRect(index)
                close_rect = self._close_button_rect(tab_rect)

                if close_rect.contains(event.pos()) and hasattr(self, '_model') and self._model.tabs_closable():
                    # Final validation before emitting signal
                    if index < self.count():
                        self.tabCloseClicked.emit(index)
                    return

                # Start potential drag operation
                self._drag_start_position = event.pos()
                self._dragged_tab_index = index
            else:
                # Clicked on empty area - ignore event so parent can handle for window dragging
                event.ignore()
                return

        elif event.button() == Qt.MouseButton.MiddleButton:
            index = self.tabAt(event.pos())
            # Also validate middle-click tab index
            if index >= 0 and index < self.count():
                self.tabMiddleClicked.emit(index)
                return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse move for hover effects and drag detection."""
        # Handle drag detection and movement
        if self._drag_start_position is not None and not self._is_dragging:
            # Check if we should start dragging
            if (event.pos() - self._drag_start_position).manhattanLength() > 5:
                self._start_tab_drag()

        if self._is_dragging:
            # Update drag indicator position
            self._update_drag_indicator(event.pos())
            return

        index = self.tabAt(event.pos())

        # If we're not over a tab and left button is pressed, ignore for window dragging
        if index == -1 and event.buttons() == Qt.MouseButton.LeftButton:
            event.ignore()
            return

        # Update hovered tab with animation
        if index != self._hovered_tab:
            old_hovered = self._hovered_tab
            self._hovered_tab = index

            # Update hover state (animation removed)

            self.update()

        # Check new tab button hover
        new_tab_hovered = self.new_tab_button_rect.contains(event.pos())
        if new_tab_hovered != self.new_tab_button_hovered:
            self.new_tab_button_hovered = new_tab_hovered
            self.update()

        # Check close button hover
        if index >= 0 and hasattr(self, '_model') and self._model.tabs_closable():
            tab_rect = self.tabRect(index)
            close_rect = self._close_button_rect(tab_rect)
            if close_rect.contains(event.pos()):
                if self._close_button_hovered != index:
                    self._close_button_hovered = index
                    self.update()
            elif self._close_button_hovered == index:
                self._close_button_hovered = -1
                self.update()

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle mouse release events."""
        if event.button() == Qt.MouseButton.LeftButton:
            if self._is_dragging:
                self._end_tab_drag(event.pos())
                return

            # Reset drag state even if not dragging
            self._drag_start_position = None
            self._dragged_tab_index = -1

        super().mouseReleaseEvent(event)

    def leaveEvent(self, event) -> None:
        """Handle mouse leave."""
        # Animate hover out effect
        if hasattr(self, '_animator') and self._hovered_tab >= 0:
            self._animator.animate_hover(self, False)

        self._hovered_tab = -1
        self._close_button_hovered = -1
        self.new_tab_button_hovered = False
        self.update()
        super().leaveEvent(event)

    def resizeEvent(self, event) -> None:
        """Handle resize events to trigger tab recalculation."""
        super().resizeEvent(event)
        # Trigger geometry update which will call tabSizeHint
        self.updateGeometry()
        # Update new tab button position
        self.new_tab_button_rect = self._calculate_new_tab_button_position()
        self.update()

    def tabInserted(self, index: int) -> None:
        """Called when a tab is inserted."""
        super().tabInserted(index)
        # Trigger geometry update for tab width recalculation
        self.updateGeometry()
        # Update new tab button position
        self.new_tab_button_rect = self._calculate_new_tab_button_position()

    def tabRemoved(self, index: int) -> None:
        """Called when a tab is removed."""
        super().tabRemoved(index)
        # Trigger geometry update for tab width recalculation
        self.updateGeometry()
        # Update new tab button position
        self.new_tab_button_rect = self._calculate_new_tab_button_position()
        # Trigger repaint to ensure visual update
        self.update()

    # ==================== Size Management ====================

    # DO NOT override tabRect() - let Qt handle tab positioning

    # Let Qt calculate sizeHint based on tabSizeHint

    def minimumTabSizeHint(self, index: int) -> QSize:
        """Return minimum size for a tab."""
        return QSize(self.CHROME_MIN_TAB_WIDTH, ChromeTabRenderer.TAB_HEIGHT)

    def tabSizeHint(self, index: int) -> QSize:
        """Return preferred size for a tab with Chrome-like dynamic width."""
        if self.count() == 0:
            return super().tabSizeHint(index)

        # Calculate available width
        available_width = self.width()

        # During initialization, return maximum width
        if available_width <= 0 or available_width < 200:
            return QSize(self.CHROME_MAX_TAB_WIDTH, ChromeTabRenderer.TAB_HEIGHT)

        # Reserve space for new tab button
        new_tab_space = self.new_tab_button_size.width() + 20  # button + margins
        available_width -= new_tab_space

        # Account for window controls in frameless mode
        if hasattr(self.parent(), '_window_controls') and self.parent()._window_controls:
            available_width -= 138  # WindowControls fixed width

        # Calculate width per tab
        width_per_tab = available_width // self.count()

        # Apply Chrome's min/max constraints
        width_per_tab = max(self.CHROME_MIN_TAB_WIDTH, width_per_tab)
        width_per_tab = min(self.CHROME_MAX_TAB_WIDTH, width_per_tab)

        return QSize(width_per_tab, ChromeTabRenderer.TAB_HEIGHT)

    def _calculate_new_tab_button_position(self) -> QRect:
        """Position new tab button after last tab."""
        if self.count() > 0:
            # Use Qt's actual tab positioning
            last_tab_rect = self.tabRect(self.count() - 1)
            x = last_tab_rect.right() + 8
            y = last_tab_rect.center().y() - self.new_tab_button_size.height() // 2
        else:
            x = 8
            y = (self.height() - self.new_tab_button_size.height()) // 2

        return QRect(x, y, self.new_tab_button_size.width(),
                     self.new_tab_button_size.height())

    def _paint_drag_indicator(self, painter: QPainter) -> None:
        """Paint insertion indicator between tabs during drag operation."""
        if self._drag_indicator_position < 0:
            return

        # Calculate indicator position
        if self._drag_indicator_position >= self.count():
            # After last tab
            if self.count() > 0:
                last_rect = self.tabRect(self.count() - 1)
                x = last_rect.right()
            else:
                x = 8
        else:
            # Between tabs
            tab_rect = self.tabRect(self._drag_indicator_position)
            x = tab_rect.left()

        # Draw vertical line as insertion indicator
        painter.save()
        painter.setPen(QPen(QColor(0, 120, 215), 2))  # Windows blue
        painter.drawLine(x, 5, x, self.height() - 5)
        painter.restore()

    def _start_tab_drag(self) -> None:
        """Start tab drag operation."""
        if self._dragged_tab_index < 0:
            return

        self._is_dragging = True
        self.setCursor(Qt.CursorShape.ClosedHandCursor)
        self.update()

    def _update_drag_indicator(self, mouse_pos: QPoint) -> None:
        """Update drag indicator position based on mouse position."""
        if not self._is_dragging:
            return

        # Calculate drop position
        drop_index = self._calculate_drop_index(mouse_pos)

        if drop_index != self._drag_indicator_position:
            self._drag_indicator_position = drop_index
            self.update()

    def _calculate_drop_index(self, mouse_pos: QPoint) -> int:
        """Calculate where tab would be dropped based on mouse position."""
        # Find which tab position this corresponds to
        for i in range(self.count()):
            tab_rect = self.tabRect(i)
            if mouse_pos.x() < tab_rect.center().x():
                return i

        # After all tabs
        return self.count()

    def _end_tab_drag(self, mouse_pos: QPoint) -> None:
        """End tab drag operation and perform reorder if needed."""
        if not self._is_dragging:
            return

        drop_index = self._calculate_drop_index(mouse_pos)

        # Perform reorder if position changed
        if (drop_index != self._dragged_tab_index and
            drop_index != self._dragged_tab_index + 1 and
            hasattr(self, '_model')):

            # Adjust drop index if moving left
            if drop_index > self._dragged_tab_index:
                drop_index -= 1

            # Perform tab reordering (animation removed)

            # Update model
            self._model.move_tab(self._dragged_tab_index, drop_index)

        # Reset drag state
        self._is_dragging = False
        self._drag_start_position = None
        self._dragged_tab_index = -1
        self._drag_indicator_position = -1
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()

    # Dynamic width calculation is now handled in tabSizeHint()
