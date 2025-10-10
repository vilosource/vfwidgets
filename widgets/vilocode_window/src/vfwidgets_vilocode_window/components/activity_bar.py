"""Activity bar component for VS Code-style window.

Provides a vertical icon bar on the left edge with clickable items.
"""

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QIcon, QMouseEvent, QPainter, QPaintEvent
from PySide6.QtWidgets import QVBoxLayout, QWidget

# Check if theme system is available
try:
    from vfwidgets_theme import ThemedWidget

    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False
    ThemedWidget = object  # type: ignore


class ActivityBarItem(QWidget):
    """Single item in activity bar (icon button).

    States:
    - Normal: Default appearance
    - Hover: Slightly lighter background
    - Active: Border highlight on left edge
    - Pressed: Darker background
    """

    clicked = Signal()

    def __init__(
        self, item_id: str, icon: QIcon, tooltip: str = "", parent: Optional[QWidget] = None
    ) -> None:
        """Initialize activity bar item.

        Args:
            item_id: Unique identifier for this item
            icon: Icon to display
            tooltip: Tooltip text
            parent: Parent widget
        """
        super().__init__(parent)
        self._item_id = item_id
        self._icon = icon
        self._tooltip = tooltip
        self._is_active = False
        self._is_hovered = False
        self._is_pressed = False
        self._is_enabled = True

        self.setFixedSize(48, 48)  # Square button
        self.setToolTip(tooltip)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)

    def set_active(self, active: bool) -> None:
        """Set the active state of this item."""
        self._is_active = active
        self.update()

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable this item."""
        self._is_enabled = enabled
        if enabled:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ForbiddenCursor)
        self.update()

    def is_enabled(self) -> bool:
        """Check if item is enabled."""
        return self._is_enabled

    def set_icon(self, icon: QIcon) -> None:
        """Update the icon for this item."""
        self._icon = icon
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press."""
        if event.button() == Qt.MouseButton.LeftButton and self._is_enabled:
            self._is_pressed = True
            self.update()
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle mouse release."""
        if event.button() == Qt.MouseButton.LeftButton and self._is_enabled:
            self._is_pressed = False
            if self.rect().contains(event.pos()):
                self.clicked.emit()
            self.update()
            event.accept()

    def enterEvent(self, event) -> None:  # type: ignore
        """Handle mouse enter."""
        self._is_hovered = True
        self.update()

    def leaveEvent(self, event) -> None:  # type: ignore
        """Handle mouse leave."""
        self._is_hovered = False
        self._is_pressed = False
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint the activity bar item."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get colors from parent ActivityBar if available
        parent_bar = self.parent()
        parent_widget = parent_bar if isinstance(parent_bar, QWidget) else None
        bg_color = self._get_background_color(parent_widget)
        border_color = self._get_active_border_color(parent_widget)

        # Draw background
        painter.fillRect(self.rect(), bg_color)

        # Draw left border if active
        if self._is_active:
            painter.fillRect(0, 0, 2, self.height(), border_color)

        # Draw icon centered
        if not self._icon.isNull():
            icon_size = 24  # Icon size in pixels
            x = (self.width() - icon_size) // 2
            y = (self.height() - icon_size) // 2

            # Adjust opacity for disabled state
            if not self._is_enabled:
                painter.setOpacity(0.4)

            pixmap = self._icon.pixmap(icon_size, icon_size)
            painter.drawPixmap(x, y, pixmap)

    def _get_background_color(self, parent_bar: Optional[QWidget]) -> QColor:
        """Get background color based on state.

        Args:
            parent_bar: Parent ActivityBar widget

        Returns:
            Background color for current state
        """
        # Try to get theme colors from parent if available
        if parent_bar and THEME_AVAILABLE and hasattr(parent_bar, "get_theme_color"):
            if self._is_active:
                # Active state
                active_bg = parent_bar.get_theme_color("active_background")  # type: ignore
                if active_bg:
                    return QColor(active_bg)
            # Normal/hover/pressed use base background
            bg = parent_bar.get_theme_color("background")  # type: ignore
            if bg:
                base_color = QColor(bg)
                if self._is_pressed:
                    # Darker for pressed
                    return base_color.darker(120)
                elif self._is_hovered:
                    # Lighter for hover
                    return base_color.lighter(120)
                return base_color

        # Fallback colors (VS Code Dark+ theme)
        if not self._is_enabled:
            return QColor("#2c2c2c")  # Disabled
        elif self._is_pressed:
            return QColor("#1e1e1e")  # Pressed (darker)
        elif self._is_active:
            return QColor("#383838")  # Active (lighter)
        elif self._is_hovered:
            return QColor("#333333")  # Hover (slightly lighter)
        else:
            return QColor("#2c2c2c")  # Normal

    def _get_active_border_color(self, parent_bar: Optional[QWidget]) -> QColor:
        """Get active border color.

        Args:
            parent_bar: Parent ActivityBar widget

        Returns:
            Border color for active state
        """
        # Try to get theme color from parent
        if parent_bar and THEME_AVAILABLE and hasattr(parent_bar, "get_theme_color"):
            border = parent_bar.get_theme_color("active_border")  # type: ignore
            if border:
                return QColor(border)

        # Fallback color (VS Code Dark+ blue)
        return QColor("#007acc")


# Create base class with conditional theme support
if THEME_AVAILABLE:
    _ActivityBarBase = type("_ActivityBarBase", (ThemedWidget, QWidget), {})  # type: ignore
else:
    _ActivityBarBase = QWidget  # type: ignore


class ActivityBar(_ActivityBarBase):  # type: ignore
    """Vertical icon bar on the left edge.

    Features:
    - Fixed width (~48px)
    - Vertical layout of icon buttons
    - One active (highlighted) item at a time
    - Emits signals when items clicked
    """

    item_clicked = Signal(str)  # item_id

    # Theme configuration (VS Code tokens)
    theme_config = {
        "background": "activityBar.background",
        "foreground": "activityBar.foreground",
        "inactive_foreground": "activityBar.inactiveForeground",
        "border": "activityBar.border",
        "active_border": "activityBar.activeBorder",
        "active_background": "activityBar.activeBackground",
    }

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize activity bar.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._items: dict[str, ActivityBarItem] = {}
        self._active_item: Optional[str] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        self.setFixedWidth(48)
        # Apply fallback color if theme not available
        if not THEME_AVAILABLE:
            self.setStyleSheet("background-color: #2c2c2c;")

        # Vertical layout for items
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._layout.addStretch(1)  # Push items to top initially

    def add_item(self, item_id: str, icon: QIcon, tooltip: str = "") -> None:
        """Add an activity bar item.

        Args:
            item_id: Unique identifier for this item
            icon: Icon to display
            tooltip: Tooltip text
        """
        if item_id in self._items:
            # Item already exists, update it
            self._items[item_id].set_icon(icon)
            self._items[item_id].setToolTip(tooltip)
            return

        # Create new item
        item = ActivityBarItem(item_id, icon, tooltip, self)
        item.clicked.connect(lambda: self._on_item_clicked(item_id))

        # Insert before the stretch
        self._layout.insertWidget(self._layout.count() - 1, item)
        self._items[item_id] = item

    def remove_item(self, item_id: str) -> None:
        """Remove an activity bar item.

        Args:
            item_id: ID of item to remove
        """
        if item_id not in self._items:
            return

        item = self._items[item_id]
        self._layout.removeWidget(item)
        item.deleteLater()
        del self._items[item_id]

        # Clear active item if this was it
        if self._active_item == item_id:
            self._active_item = None

    def set_active_item(self, item_id: str) -> None:
        """Set the active (highlighted) item.

        Args:
            item_id: ID of item to activate
        """
        # Deactivate current active item
        if self._active_item and self._active_item in self._items:
            self._items[self._active_item].set_active(False)

        # Activate new item
        self._active_item = item_id
        if item_id and item_id in self._items:
            self._items[item_id].set_active(True)

    def get_active_item(self) -> Optional[str]:
        """Get the currently active item ID.

        Returns:
            Active item ID, or None if no item is active
        """
        return self._active_item

    def set_item_icon(self, item_id: str, icon: QIcon) -> None:
        """Update item icon.

        Args:
            item_id: ID of item to update
            icon: New icon
        """
        if item_id in self._items:
            self._items[item_id].set_icon(icon)

    def set_item_enabled(self, item_id: str, enabled: bool) -> None:
        """Enable/disable item.

        Args:
            item_id: ID of item to update
            enabled: True to enable, False to disable
        """
        if item_id in self._items:
            self._items[item_id].set_enabled(enabled)

    def is_item_enabled(self, item_id: str) -> bool:
        """Check if item is enabled.

        Args:
            item_id: ID of item to check

        Returns:
            True if enabled, False if disabled or doesn't exist
        """
        if item_id in self._items:
            return self._items[item_id].is_enabled()
        return False

    def get_items(self) -> list[str]:
        """Get all item IDs in order.

        Returns:
            List of item IDs in display order
        """
        items = []
        for i in range(self._layout.count() - 1):  # Exclude stretch
            widget = self._layout.itemAt(i).widget()
            if isinstance(widget, ActivityBarItem):
                items.append(widget._item_id)
        return items

    def _on_item_clicked(self, item_id: str) -> None:
        """Handle item click.

        Args:
            item_id: ID of clicked item
        """
        if not self.is_item_enabled(item_id):
            return

        # Set as active
        self.set_active_item(item_id)

        # Emit signal
        self.item_clicked.emit(item_id)
