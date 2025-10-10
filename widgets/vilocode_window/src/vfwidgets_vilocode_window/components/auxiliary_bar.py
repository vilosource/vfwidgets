"""Auxiliary bar component for VS Code-style window.

Provides a right sidebar (auxiliary panel) with single content.
"""

from typing import Optional

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

# Check if theme system is available
try:
    from vfwidgets_theme import ThemedWidget

    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False
    ThemedWidget = object  # type: ignore


class AuxiliaryBarResizeHandle(QWidget):
    """Vertical resize handle for auxiliary bar (left edge).

    Features:
    - 4px wide, full height
    - Cursor changes to SizeHorCursor on hover
    - Drag to resize auxiliary bar
    """

    resize_started = Signal()
    resize_moved = Signal(int)  # delta_x
    resize_finished = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize resize handle.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._dragging = False
        self._drag_start_x = 0.0
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        self.setFixedWidth(4)
        self.setCursor(Qt.CursorShape.SizeHorCursor)
        self.setStyleSheet("background-color: transparent;")

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press to start drag.

        Args:
            event: Mouse event
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._drag_start_x = event.globalPosition().x()
            self.resize_started.emit()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse move during drag.

        Args:
            event: Mouse event
        """
        if self._dragging:
            delta_x = int(event.globalPosition().x() - self._drag_start_x)
            self._drag_start_x = event.globalPosition().x()
            # Negative delta because we're resizing from the left edge
            self.resize_moved.emit(-delta_x)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle mouse release to finish drag.

        Args:
            event: Mouse event
        """
        if event.button() == Qt.MouseButton.LeftButton and self._dragging:
            self._dragging = False
            self.resize_finished.emit()
            event.accept()


# Create base class with conditional theme support
if THEME_AVAILABLE:
    _AuxiliaryBarBase = type("_AuxiliaryBarBase", (ThemedWidget, QWidget), {})  # type: ignore
else:
    _AuxiliaryBarBase = QWidget  # type: ignore


class AuxiliaryBar(_AuxiliaryBarBase):  # type: ignore
    """Right sidebar (auxiliary panel).

    Features:
    - Single content widget (not stackable)
    - Hidden by default
    - Resizable width (drag left border)
    - No header (just content)
    """

    visibility_changed = Signal(bool)  # is_visible
    width_changed = Signal(int)  # new_width

    # Theme configuration (VS Code tokens - reuse sidebar colors)
    theme_config = {
        "background": "sideBar.background",
        "foreground": "sideBar.foreground",
        "border": "sideBar.border",
    }

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize auxiliary bar.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._content: Optional[QWidget] = None
        self._min_width = 150
        self._max_width = 500
        self._default_width = 300
        self._last_width = self._default_width  # Remember width before collapse
        self._animation: Optional[QPropertyAnimation] = None  # Collapse/expand animation
        self._animating_to_visible: bool = False  # Track target visibility for animation
        self._setup_ui()
        self.setVisible(False)  # Hidden by default

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        self.setFixedWidth(self._default_width)
        # Apply fallback color if theme not available
        if not THEME_AVAILABLE:
            self.setStyleSheet("background-color: #252526;")

        # Main horizontal layout: resize handle + content
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Resize handle on left edge
        self._resize_handle = AuxiliaryBarResizeHandle(self)
        self._resize_handle.resize_moved.connect(self._on_resize)
        main_layout.addWidget(self._resize_handle)

        # Content layout
        self._content_layout = QVBoxLayout()
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0)
        main_layout.addLayout(self._content_layout, 1)

    def set_content(self, widget: QWidget) -> None:
        """Set the auxiliary bar content widget.

        Args:
            widget: Widget to display in auxiliary bar
        """
        # Remove old content if any
        if self._content:
            self._content_layout.removeWidget(self._content)
            self._content.setParent(None)

        # Add new content
        self._content = widget
        self._content_layout.addWidget(widget)

    def get_content(self) -> Optional[QWidget]:
        """Get the current content widget.

        Returns:
            Content widget, or None if not set
        """
        return self._content

    def toggle_visibility(self) -> None:
        """Toggle auxiliary bar visibility with smooth animation."""
        self.set_visible(not self.isVisible())

    def set_visible(self, visible: bool, animated: bool = True) -> None:
        """Show/hide auxiliary bar with optional animation.

        Args:
            visible: True to show, False to hide
            animated: True to animate the transition (default)
        """
        # If already in desired state, just emit signal and return
        if visible == self.isVisible():
            self.visibility_changed.emit(visible)
            return

        if not animated:
            # Instant toggle without animation
            super().setVisible(visible)
            self.visibility_changed.emit(visible)
            return

        # Stop any running animation
        if self._animation:
            if self._animation.state() == QPropertyAnimation.State.Running:
                self._animation.stop()

        # Create animation if not exists (set self as parent for proper lifecycle)
        if self._animation is None:
            self._animation = QPropertyAnimation(self, b"maximumWidth", self)
            self._animation.setDuration(200)
            self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            # Connect to slot once - we'll use instance variable to track state
            self._animation.finished.connect(self._on_animation_finished)

        # Store target visibility in instance variable (no lambda needed)
        self._animating_to_visible = visible

        if visible:
            # Expand: 0 → last width
            super().setVisible(True)  # Make visible immediately
            self._animation.setStartValue(0)
            self._animation.setEndValue(self._last_width)
        else:
            # Collapse: current width → 0
            self._last_width = self.width()  # Remember current width
            self._animation.setStartValue(self._last_width)
            self._animation.setEndValue(0)

        self._animation.start()

    def _on_animation_finished(self) -> None:
        """Handle animation completion.

        Uses self._animating_to_visible to determine target state.
        """
        if not self._animating_to_visible:
            # Hide after collapse animation completes
            super().setVisible(False)
            # Restore width for next expand
            self.setMaximumWidth(self._last_width)
        else:
            # After expand, remove max width constraint
            self.setMaximumWidth(self._max_width)

        self.visibility_changed.emit(self._animating_to_visible)

    def set_width(self, width: int) -> None:
        """Set auxiliary bar width.

        Args:
            width: New width in pixels (constrained to min/max)
        """
        width = max(self._min_width, min(self._max_width, width))
        self.setFixedWidth(width)
        self.width_changed.emit(width)

    def get_width(self) -> int:
        """Get current auxiliary bar width.

        Returns:
            Width in pixels
        """
        return int(self.width())

    def _on_resize(self, delta_x: int) -> None:
        """Handle resize drag.

        Args:
            delta_x: Change in x position
        """
        new_width = self.width() + delta_x
        self.set_width(new_width)
