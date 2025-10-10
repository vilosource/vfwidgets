"""Sidebar component for VS Code-style window.

Provides a collapsible sidebar with stackable panels.
"""

from typing import Optional

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QLabel, QStackedWidget, QVBoxLayout, QWidget

# Check if theme system is available
try:
    from vfwidgets_theme import ThemedWidget

    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False
    ThemedWidget = object  # type: ignore


class SideBarHeader(QWidget):
    """Header showing current panel title.

    Layout: [Title Label] [Stretch] [Optional Buttons]
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize sidebar header.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        self.setFixedHeight(35)
        self.setStyleSheet("background-color: #252526; border-bottom: 1px solid #1e1e1e;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(0)

        # Title label
        self._title_label = QLabel("")
        self._title_label.setStyleSheet(
            "color: #cccccc; font-weight: bold; font-size: 11px; "
            "text-transform: uppercase; border: none;"
        )
        layout.addWidget(self._title_label)

    def set_title(self, title: str) -> None:
        """Set the header title.

        Args:
            title: Title text to display
        """
        self._title_label.setText(title)


class ResizeHandle(QWidget):
    """Vertical resize handle for sidebars.

    Features:
    - 4px wide, full height
    - Cursor changes to SizeHorCursor on hover
    - Drag to resize adjacent widget
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
            self.resize_moved.emit(delta_x)
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
    _SideBarBase = type("_SideBarBase", (ThemedWidget, QWidget), {})  # type: ignore
else:
    _SideBarBase = QWidget  # type: ignore


class SideBar(_SideBarBase):  # type: ignore
    """Collapsible sidebar with stackable panels.

    Structure:
    ┌─────────────────┐
    │ PANEL TITLE     │  ← Header
    ├─────────────────┤
    │                 │
    │  Panel Content  │  ← QStackedWidget
    │  (one at a time)│
    │                 │
    └─────────────────┘

    Features:
    - Multiple panels, one visible at a time
    - Collapsible (toggle visibility)
    - Resizable width (drag border)
    - Panel title shown in header
    """

    panel_changed = Signal(str)  # panel_id
    visibility_changed = Signal(bool)  # is_visible
    width_changed = Signal(int)  # new_width

    # Theme configuration (VS Code tokens)
    theme_config = {
        "background": "sideBar.background",
        "foreground": "sideBar.foreground",
        "border": "sideBar.border",
        "title_foreground": "sideBarTitle.foreground",
    }

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize sidebar.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._panels: dict[str, tuple[QWidget, str]] = {}  # panel_id -> (widget, title)
        self._current_panel: Optional[str] = None
        self._min_width = 150
        self._max_width = 500
        self._default_width = 250
        self._last_width = self._default_width  # Remember width before collapse
        self._animation: Optional[QPropertyAnimation] = None  # Collapse/expand animation
        self._animating_to_visible: bool = False  # Track target visibility for animation
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        self.setFixedWidth(self._default_width)
        # Apply fallback color if theme not available
        if not THEME_AVAILABLE:
            self.setStyleSheet("background-color: #252526;")

        # Main layout with resize handle
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Horizontal layout for content + resize handle
        h_layout = QVBoxLayout()
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(0)

        # Header
        self._header = SideBarHeader(self)
        h_layout.addWidget(self._header)

        # Content stack
        self._stack = QStackedWidget(self)
        self._stack.setStyleSheet("background-color: #252526; border: none;")
        h_layout.addWidget(self._stack, 1)

        main_layout.addLayout(h_layout, 1)

        # Resize handle on right edge
        self._resize_handle = ResizeHandle(self)
        self._resize_handle.resize_moved.connect(self._on_resize)
        main_layout.addWidget(
            self._resize_handle, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop
        )

    def add_panel(self, panel_id: str, widget: QWidget, title: str = "") -> None:
        """Add a stackable panel.

        Args:
            panel_id: Unique identifier for this panel
            widget: Widget to display in panel
            title: Panel title to show in header
        """
        if panel_id in self._panels:
            # Panel exists, update it
            old_widget, _ = self._panels[panel_id]
            index = self._stack.indexOf(old_widget)
            self._stack.removeWidget(old_widget)
            old_widget.setParent(None)
            self._stack.insertWidget(index, widget)
            self._panels[panel_id] = (widget, title)
        else:
            # Add new panel
            self._stack.addWidget(widget)
            self._panels[panel_id] = (widget, title)

            # If this is the first panel, show it
            if len(self._panels) == 1:
                self.show_panel(panel_id)

    def remove_panel(self, panel_id: str) -> None:
        """Remove a panel.

        Args:
            panel_id: ID of panel to remove
        """
        if panel_id not in self._panels:
            return

        widget, _ = self._panels[panel_id]
        self._stack.removeWidget(widget)
        widget.setParent(None)
        del self._panels[panel_id]

        # If we removed the current panel, show another one
        if self._current_panel == panel_id:
            self._current_panel = None
            if self._panels:
                # Show the first available panel
                first_panel_id = next(iter(self._panels))
                self.show_panel(first_panel_id)
            else:
                self._header.set_title("")

    def show_panel(self, panel_id: str) -> None:
        """Switch to specified panel.

        Args:
            panel_id: ID of panel to show
        """
        if panel_id not in self._panels:
            return

        widget, title = self._panels[panel_id]
        self._stack.setCurrentWidget(widget)
        self._header.set_title(title)
        self._current_panel = panel_id
        self.panel_changed.emit(panel_id)

    def get_panel(self, panel_id: str) -> Optional[QWidget]:
        """Get panel widget by ID.

        Args:
            panel_id: ID of panel to get

        Returns:
            Panel widget, or None if not found
        """
        if panel_id in self._panels:
            widget, _ = self._panels[panel_id]
            return widget
        return None

    def get_current_panel(self) -> Optional[str]:
        """Get the currently visible panel ID.

        Returns:
            Current panel ID, or None if no panel is visible
        """
        return self._current_panel

    def toggle_visibility(self) -> None:
        """Toggle sidebar visibility with smooth animation."""
        self.set_visible(not self.isVisible())

    def set_visible(self, visible: bool, animated: bool = True) -> None:
        """Show/hide sidebar with optional animation.

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
        """Set sidebar width.

        Args:
            width: New width in pixels (constrained to min/max)
        """
        width = max(self._min_width, min(self._max_width, width))
        self.setFixedWidth(width)
        self.width_changed.emit(width)

    def get_width(self) -> int:
        """Get current sidebar width.

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
