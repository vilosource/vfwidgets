"""Title bar component for frameless windows.

Provides a custom title bar with window controls and drag area.
"""

from typing import Optional

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QHBoxLayout, QLabel, QMenuBar, QWidget

from .window_controls import WindowControls

# Try to import ThemedWidget
try:
    from vfwidgets_theme import ThemedWidget

    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False
    ThemedWidget = object  # type: ignore


class DraggableMenuBar(QMenuBar):
    """QMenuBar that allows window dragging when clicking on empty areas.

    This menubar forwards mouse events to its parent (TitleBar) when clicking
    on areas that are not menu items, allowing the window to be dragged.
    """

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press - ignore empty areas for window dragging."""
        # Check if click is on an actual menu action
        action = self.actionAt(event.pos())
        if action is not None:
            # Click is on a menu item - handle normally
            super().mousePressEvent(event)
        else:
            # Click is on empty area - ignore to let parent window handle dragging
            event.ignore()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse move - ignore when not in menu for window dragging."""
        # If not in an active menu, ignore to let parent handle dragging
        if not self.activeAction() and event.buttons() != Qt.MouseButton.NoButton:
            event.ignore()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle mouse release - ignore if not in menu."""
        # If not in menu, ignore to let parent handle
        if not self.activeAction():
            event.ignore()
        else:
            super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """Handle double click - forward to parent if not on menu item."""
        action = self.actionAt(event.pos())
        if action is not None:
            super().mouseDoubleClickEvent(event)
        else:
            parent = self.parent()
            if parent and hasattr(parent, "mouseDoubleClickEvent"):
                parent_pos = self.mapToParent(event.pos())
                from PySide6.QtCore import QPointF

                parent_event = QMouseEvent(
                    event.type(),
                    QPointF(parent_pos),
                    event.scenePosition(),
                    event.globalPosition(),
                    event.button(),
                    event.buttons(),
                    event.modifiers(),
                    event.source(),
                )
                parent.mouseDoubleClickEvent(parent_event)
                event.accept()
            else:
                super().mouseDoubleClickEvent(event)


# Create base class with ThemedWidget if available
if THEME_AVAILABLE:
    _TitleBarBase = type("_TitleBarBase", (ThemedWidget, QWidget), {})
else:
    _TitleBarBase = QWidget  # type: ignore


class TitleBar(_TitleBarBase):
    """Custom title bar for frameless windows.

    Includes title text, optional menu bar, window controls, and drag-to-move functionality.
    """

    # Theme configuration (if theme system available)
    if THEME_AVAILABLE:
        theme_config = {
            "background": "titleBar.activeBackground",
            "foreground": "titleBar.activeForeground",
        }

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._drag_position: Optional[QPoint] = None
        self._menu_bar: Optional[QMenuBar] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        self.setFixedHeight(30)

        # Only set hardcoded stylesheet if theme system is not available
        if not THEME_AVAILABLE:
            self.setStyleSheet("background-color: #323233; color: #cccccc;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 0, 0)
        layout.setSpacing(0)

        # Title label (will be set by parent window)
        self._title_label = QLabel("ViloCodeWindow")
        # Only set hardcoded color if theme system is not available
        if not THEME_AVAILABLE:
            self._title_label.setStyleSheet("color: #cccccc; font-size: 13px;")
        else:
            self._title_label.setStyleSheet("font-size: 13px;")  # Theme will handle color
        # Allow mouse events to pass through to title bar for dragging
        self._title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        layout.addWidget(self._title_label)

        # Menu bar will be inserted here if set
        # (using insertWidget in set_menu_bar)

        # Stretch to push controls to right
        layout.addStretch(1)

        # Window controls
        self._window_controls = WindowControls(self)
        layout.addWidget(self._window_controls)

        # Store layout for menu bar insertion
        self._layout = layout

    def set_title(self, title: str) -> None:
        """Set the title text."""
        self._title_label.setText(title)

    def set_menu_bar(self, menubar: QMenuBar) -> None:
        """Set the menu bar to display in the title bar.

        Args:
            menubar: QMenuBar widget to display
        """
        # Remove existing menu bar if any
        if self._menu_bar:
            self._layout.removeWidget(self._menu_bar)
            self._menu_bar.setParent(None)

        if menubar:
            # Convert to DraggableMenuBar if it's a regular QMenuBar
            if isinstance(menubar, QMenuBar) and not isinstance(menubar, DraggableMenuBar):
                # Create new DraggableMenuBar and transfer menus
                draggable_menubar = DraggableMenuBar(self)

                # Transfer all actions/menus from original menubar
                actions_to_transfer = list(menubar.actions())  # Make a copy of the list
                for action in actions_to_transfer:
                    # Remove from old menubar and add to new one
                    menubar.removeAction(action)
                    draggable_menubar.addAction(action)

                self._menu_bar = draggable_menubar
            else:
                self._menu_bar = menubar

            # Hide title label when menu bar is present (like VS Code)
            self._title_label.hide()

            # Style menu bar to fit in title bar
            # Try to get theme colors if available
            try:
                from vfwidgets_theme import get_themed_application

                app = get_themed_application()
                if app and app.get_current_theme():
                    theme = app.get_current_theme()
                    fg_color = theme.get_color("menu.foreground", "#cccccc")
                    hover_bg = theme.get_color("menu.selectionBackground", "#2d2d30")
                    active_bg = theme.get_color("menu.selectionBackground", "#007acc")
                else:
                    fg_color = "#cccccc"
                    hover_bg = "#2d2d30"
                    active_bg = "#007acc"
            except (ImportError, AttributeError):
                fg_color = "#cccccc"
                hover_bg = "#2d2d30"
                active_bg = "#007acc"

            self._menu_bar.setStyleSheet(
                f"""
                QMenuBar {{
                    background-color: transparent;
                    color: {fg_color};
                    border: none;
                    padding: 0px;
                    margin: 0px;
                }}
                QMenuBar::item {{
                    background-color: transparent;
                    padding: 5px 10px;
                    color: {fg_color};
                }}
                QMenuBar::item:selected {{
                    background-color: {hover_bg};
                }}
                QMenuBar::item:pressed {{
                    background-color: {active_bg};
                }}
            """
            )
            # Insert at beginning (position 0, before title label)
            self._layout.insertWidget(0, self._menu_bar)
        else:
            self._menu_bar = None
            # Show title label when no menu bar
            self._title_label.show()

    def integrate_menu_bar(self, menubar: QMenuBar) -> None:
        """Integrate menu bar into title bar with automatic theme integration.

        This is the new recommended method that replaces set_menu_bar().
        It handles:
        - Action transfer to DraggableMenuBar
        - Automatic theme color application
        - Theme change listeners for updates

        Args:
            menubar: QMenuBar widget to integrate
        """
        # Remove old if exists
        if self._menu_bar:
            self._layout.removeWidget(self._menu_bar)
            self._menu_bar.setParent(None)
            self._menu_bar.deleteLater()
            self._menu_bar = None

        if not menubar:
            self._title_label.show()
            return

        # Create draggable wrapper
        if isinstance(menubar, QMenuBar) and not isinstance(menubar, DraggableMenuBar):
            draggable_menubar = DraggableMenuBar(self)

            # Transfer actions (FIX: remove from old first)
            actions_to_transfer = list(menubar.actions())
            for action in actions_to_transfer:
                menubar.removeAction(action)
                draggable_menubar.addAction(action)

            self._menu_bar = draggable_menubar
        else:
            self._menu_bar = menubar

        # Hide title when menu present
        self._title_label.hide()

        # Apply theme styling
        self._apply_menu_styling()

        # Register theme change listener
        self._register_theme_listener()

        # Add to layout
        self._layout.insertWidget(0, self._menu_bar)

    def _apply_menu_styling(self, theme=None) -> None:
        """Apply theme-aware styling to menu bar.

        Args:
            theme: Optional theme to use (uses current theme if None)
        """
        if not self._menu_bar:
            return

        # Get theme colors
        try:
            from vfwidgets_theme import get_themed_application

            app = get_themed_application()
            if app and app.get_current_theme():
                current_theme = theme or app.get_current_theme()
                fg = current_theme.get_color("menu.foreground", "#cccccc")
                hover_bg = current_theme.get_color("menu.selectionBackground", "#2d2d30")
                active_bg = current_theme.get_color("menubar.selectionBackground", "#007acc")
            else:
                fg, hover_bg, active_bg = "#cccccc", "#2d2d30", "#007acc"
        except (ImportError, AttributeError):
            fg, hover_bg, active_bg = "#cccccc", "#2d2d30", "#007acc"

        # Apply stylesheet
        self._menu_bar.setStyleSheet(
            f"""
            QMenuBar {{
                background-color: transparent;
                color: {fg};
                border: none;
                padding: 0px;
                margin: 0px;
            }}
            QMenuBar::item {{
                background-color: transparent;
                padding: 5px 10px;
                color: {fg};
            }}
            QMenuBar::item:selected {{
                background-color: {hover_bg};
            }}
            QMenuBar::item:pressed {{
                background-color: {active_bg};
            }}
        """
        )

    def _register_theme_listener(self) -> None:
        """Register listener for theme changes to auto-update menu styling."""
        try:
            from vfwidgets_theme import get_themed_application

            app = get_themed_application()
            if app:
                # Connect to theme changed signal
                if hasattr(app, "theme_changed"):
                    app.theme_changed.connect(self._apply_menu_styling)
        except (ImportError, AttributeError):
            pass  # Theme system not available

    def get_menu_bar(self) -> Optional[QMenuBar]:
        """Get the current menu bar.

        Returns:
            The menu bar widget, or None if not set
        """
        return self._menu_bar

    def update_menu_bar_styling(self) -> None:
        """Public method to update menu bar styling (called from window).

        DEPRECATED: Use _apply_menu_styling() instead (called automatically).
        This is kept for backward compatibility.
        """
        self._apply_menu_styling()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press - ignore to let parent window handle dragging."""
        # Let the parent window (ViloCodeWindow) handle dragging
        event.ignore()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse move - ignore to let parent window handle dragging."""
        # Let the parent window handle dragging
        event.ignore()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle mouse release."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = None
            event.accept()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """Handle double-click to maximize."""
        if event.button() == Qt.MouseButton.LeftButton:
            window = self.window()
            if window.isMaximized():
                window.showNormal()
            else:
                window.showMaximized()
            event.accept()
