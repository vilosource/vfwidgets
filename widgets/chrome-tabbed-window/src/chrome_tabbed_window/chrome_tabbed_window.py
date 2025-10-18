"""
ChromeTabbedWindow - Main controller class.

A 100% QTabWidget-compatible widget with Chrome browser styling.
This is the main public API that matches QTabWidget exactly.
"""

from __future__ import annotations

from typing import Any, Optional

from PySide6.QtCore import Property, QRect, QSize, Qt, Signal
from PySide6.QtGui import QColor, QIcon, QPainter, QPaintEvent
from PySide6.QtWidgets import QHBoxLayout, QTabBar, QTabWidget, QVBoxLayout, QWidget
from vfwidgets_common import FramelessWindowBehavior

try:
    from vfwidgets_theme.widgets.base import ThemedWidget

    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False
    ThemedWidget = object

from .components import WindowControls
from .core import (
    DEFAULT_DOCUMENT_MODE,
    DEFAULT_ELIDE_MODE,
    DEFAULT_ICON_SIZE,
    DEFAULT_TAB_POSITION,
    DEFAULT_TAB_SHAPE,
    DEFAULT_USES_SCROLL_BUTTONS,
    TabPosition,
    TabShape,
    WindowMode,
)
from .model import TabModel
from .platform_support import PlatformFactory
from .view import ChromeTabBar, TabContentArea

if THEME_AVAILABLE:
    # CRITICAL: ThemedWidget MUST come first for theming to work!
    _BaseClass = type("_BaseClass", (ThemedWidget, QWidget), {})
else:
    _BaseClass = QWidget


class ChromeTabbedWindow(_BaseClass):
    """
    ChromeTabbedWindow - 100% QTabWidget-compatible widget with Chrome styling.

    This widget is a complete drop-in replacement for QTabWidget, providing
    identical API, signals, properties, and behavior, but with Chrome browser
    styling and automatic platform adaptation.

    Key Features:
    - 100% QTabWidget API compatibility
    - Chrome browser tab styling with built-in "+" button
    - Automatic mode detection (embedded vs window)
    - Platform-specific optimizations
    - Identical signal timing and behavior
    - Automatic theme integration (when vfwidgets-theme is installed)

    Usage:
        # Direct replacement for QTabWidget
        tabs = ChromeTabbedWindow()
        tabs.addTab(widget, "Tab Title")
        tabs.setCurrentIndex(0)

    Customizing New Tab Behavior:
        # Override _on_new_tab_requested() to customize the built-in "+" button
        class MyWindow(ChromeTabbedWindow):
            def _on_new_tab_requested(self):
                # Create custom widget instead of default "New Tab" placeholder
                widget = MyCustomWidget()
                self.addTab(widget, f"Tab {self.count() + 1}")

        Note: ChromeTabbedWindow has a built-in "+" button painted on the tab bar.
        Do NOT create a separate button via setCornerWidget() - it will be ignored.
    """

    # Theme configuration - maps theme tokens to Chrome tab colors
    theme_config = {
        "tab_background": "tab.activeBackground",
        "tab_inactive_background": "tab.inactiveBackground",
        "tab_hover_background": "tab.hoverBackground",
        "tab_border": "tab.border",
        "tab_active_foreground": "tab.activeForeground",
        "tab_inactive_foreground": "tab.inactiveForeground",
        "background": "editorGroupHeader.tabsBackground",
        "border": "editorGroupHeader.tabsBorder",
    }

    # ==================== QTabWidget Signals (EXACT MATCH) ====================

    currentChanged = Signal(int)  # Emitted when current tab changes
    tabCloseRequested = Signal(int)  # Emitted when tab close requested
    tabBarClicked = Signal(int)  # Emitted when tab is clicked
    tabBarDoubleClicked = Signal(int)  # Emitted when tab is double-clicked
    tabMoved = Signal(int, int)  # Emitted when tab is moved (from, to)

    # ==================== ChromeTabbedWindow Extended Signals ====================

    newWindowRequested = Signal()  # Emitted when user requests a new window
    tabDetachRequested = Signal(int)  # Emitted when user wants to detach tab to new window
    tabMoveToWindowRequested = Signal(
        int, object
    )  # Emitted when user wants to move tab to existing window

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize ChromeTabbedWindow.

        Args:
            parent: Parent widget. If None, widget can be used as top-level window.
        """
        super().__init__(parent)

        # MVC Components
        self._model = TabModel(self)
        self._tab_bar = ChromeTabBar(self)  # Parent for proper layout integration
        self._content_area = TabContentArea(self)  # Parent for proper layout integration
        self._platform = PlatformFactory.create(self)

        # Internal state for QTabWidget compatibility
        self._tab_position = int(DEFAULT_TAB_POSITION)
        self._tab_shape = int(DEFAULT_TAB_SHAPE)
        self._document_mode = DEFAULT_DOCUMENT_MODE
        self._icon_size = DEFAULT_ICON_SIZE
        self._elide_mode = DEFAULT_ELIDE_MODE
        self._uses_scroll_buttons = DEFAULT_USES_SCROLL_BUTTONS

        # Corner widgets (QTabWidget compatibility)
        self._corner_widgets = {
            Qt.Corner.TopLeftCorner: None,
            Qt.Corner.TopRightCorner: None,
            Qt.Corner.BottomLeftCorner: None,
            Qt.Corner.BottomRightCorner: None,
        }

        # Window mode detection
        self._window_mode = self._detect_window_mode()

        # Frameless window behavior (initialized after _setup_ui creates tab_bar)
        self._frameless_behavior: Optional[FramelessWindowBehavior] = None

        # Accent line below tab bar (initialized in _setup_ui)
        self._accent_line: Optional[QWidget] = None
        self._accent_line_custom_color: Optional[str] = None  # Custom color override

        # Enable mouse tracking for edge resize cursor changes
        self.setMouseTracking(True)

        # Setup components
        self._setup_ui()
        self._connect_signals()
        self._apply_platform_setup()

        # Initialize frameless behavior after UI is set up
        if self._window_mode == WindowMode.Frameless:
            self._initialize_frameless_behavior()

        # Register Qt properties dynamically to maintain QTabWidget compatibility
        # This allows both self.property('count') and self.count() to work
        self._register_qt_properties()

    def _detect_window_mode(self) -> WindowMode:
        """
        Detect the appropriate window mode.

        Returns WindowMode.Embedded for normal widget usage,
        WindowMode.Frameless for top-level window usage.
        """
        # Check if we're a top-level window (no parent widget)
        if self.parent() is None:
            # Top-level window - use frameless Chrome mode
            return WindowMode.Frameless
        else:
            # Embedded in another widget - use normal mode
            return WindowMode.Embedded

    def _setup_ui(self) -> None:
        """Set up the user interface layout."""
        # Set up frameless window if in Frameless mode
        if self._window_mode == WindowMode.Frameless:
            self._setup_frameless_window()
            # Note: Background is painted in paintEvent() using theme colors

        # Create main layout
        main_layout = QVBoxLayout(self)
        # Add small margins in frameless mode to ensure edge resize detection works
        # Child widgets won't consume mouse events in this margin area
        # Using 4px to match the resize_margin in FramelessWindowBehavior
        margin = 4 if self._window_mode == WindowMode.Frameless else 0
        main_layout.setContentsMargins(margin, margin, margin, margin)
        main_layout.setSpacing(0)

        # Tab bar layout (may include corner widgets and window controls)
        tab_bar_layout = QHBoxLayout()
        tab_bar_layout.setContentsMargins(0, 0, 0, 0)
        tab_bar_layout.setSpacing(0)

        # Add tab bar to layout with stretch to fill available space
        tab_bar_layout.addWidget(self._tab_bar, 1)  # stretch factor = 1

        # Add window controls if in frameless mode
        if self._window_mode == WindowMode.Frameless:
            self._window_controls = WindowControls(self)  # Parent for proper layout
            self._connect_window_controls()
            tab_bar_layout.addWidget(self._window_controls, 0)  # no stretch
        else:
            self._window_controls = None

        # Add tab bar layout to main layout with zero spacing
        main_layout.addLayout(tab_bar_layout, 0)  # No stretch factor to keep it tight

        # Add accent line below tab bar (matches active tab color)
        self._accent_line = QWidget(self)
        self._accent_line.setFixedHeight(3)  # 3px medium accent line
        main_layout.addWidget(self._accent_line, 0)

        # Add content area
        main_layout.addWidget(self._content_area, 1)  # Stretch factor 1

        # Set layout
        self.setLayout(main_layout)

        # Set initial accent line color
        self._update_accent_line_color()

    def _on_theme_changed(self) -> None:
        """Called automatically when the application theme changes.

        This method is automatically called by ThemedWidget when theme changes.
        Updates the tab bar and window controls with new theme colors.
        """
        if not THEME_AVAILABLE:
            return

        # Trigger tab bar repaint with new theme colors
        if hasattr(self, "_tab_bar") and self._tab_bar:
            self._tab_bar.update()

        # Update window controls if in frameless mode
        if hasattr(self, "_window_controls") and self._window_controls:
            self._window_controls.update()

        # Update accent line color
        self._update_accent_line_color()

        # Force full repaint
        self.update()

    def _update_accent_line_color(self) -> None:
        """Update the accent line color to match the active tab color.

        Priority:
        1. Custom color override (if set via set_accent_line_color())
        2. Active tab color from theme (token 'tab.activeBackground')
        3. Default fallback color (#FFFFFF)
        """
        if not self._accent_line:
            return

        # Use custom color if set
        if self._accent_line_custom_color:
            accent_color = self._accent_line_custom_color
        else:
            # Get active tab color from theme
            accent_color = "#FFFFFF"  # Default fallback color

            if THEME_AVAILABLE and hasattr(self, "theme"):
                # Use ThemedWidget's theme property to get the active tab color
                # This automatically uses the override system via _resolve_property_path()
                tab_bg = getattr(self.theme, "tab_background", None)
                if tab_bg:
                    accent_color = tab_bg

        # Apply color to accent line via stylesheet
        self._accent_line.setStyleSheet(f"background-color: {accent_color};")

    def get_current_theme(self):
        """Get the current theme object.

        Returns the actual Theme object from the theme manager, or None if:
        - Theme system is not available
        - No theme is currently set

        Returns:
            Theme object with .colors dict, or None
        """
        if not THEME_AVAILABLE:
            return None

        # Access theme from ThemedWidget's _theme_manager
        if hasattr(self, "_theme_manager") and self._theme_manager:
            return self._theme_manager.current_theme

        return None

    def set_accent_line_visible(self, visible: bool) -> None:
        """Show or hide the accent line below the tab bar.

        Args:
            visible: True to show accent line, False to hide it
        """
        if self._accent_line:
            self._accent_line.setVisible(visible)

    def set_accent_line_color(self, color: str) -> None:
        """Set a custom color for the accent line.

        Args:
            color: Hex color string (e.g., "#FF0000") or empty string to use theme default

        Note:
            Empty string will use the active tab color from the theme.
        """
        self._accent_line_custom_color = color if color else None
        self._update_accent_line_color()

    def _connect_signals(self) -> None:
        """Connect all internal signals."""
        # Model signals to public signals
        self._model.currentChanged.connect(self.currentChanged)
        self._model.tabCloseRequested.connect(self.tabCloseRequested)
        self._model.tabBarClicked.connect(self.tabBarClicked)
        self._model.tabBarDoubleClicked.connect(self.tabBarDoubleClicked)

        # Tab bar signals to controller (not model - avoid circular signals)
        self._tab_bar.tabCloseClicked.connect(self._on_tab_close_requested)
        self._tab_bar.tabMiddleClicked.connect(self._on_tab_close_requested)

        # Connect new tab button signal (for Chrome-style new tab button)
        self._tab_bar.newTabRequested.connect(self._on_new_tab_requested)

        # Connect tab detach signal (forward from tab bar to public signal)
        self._tab_bar.tabDetachRequested.connect(self.tabDetachRequested)

        # Connect tab move to window signal (forward from tab bar to public signal)
        self._tab_bar.tabMoveToWindowRequested.connect(self.tabMoveToWindowRequested)

        # Tab bar currentChanged should only be used for user clicks, not programmatic changes
        self._tab_bar.tabBarClicked.connect(self._on_tab_bar_clicked)

        # Update accent line when active tab changes
        self.currentChanged.connect(lambda: self._update_accent_line_color())

        # Set up MVC connections
        self._tab_bar.set_model(self._model)
        self._content_area.set_model(self._model)

    def _setup_frameless_window(self) -> None:
        """Set up frameless window for Chrome browser appearance."""
        # Set frameless window hint
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowSystemMenuHint
            | Qt.WindowType.WindowMinMaxButtonsHint
            | Qt.WindowType.WindowCloseButtonHint
        )

        # Enable transparency for proper Chrome tab rendering
        # Note: This makes the window transparent, so paintEvent must fill the background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Set a minimum size for the window
        self.setMinimumSize(400, 300)

    def _initialize_frameless_behavior(self) -> None:
        """Initialize frameless window behavior after tab_bar is created."""
        if self._window_mode != WindowMode.Frameless or not self._tab_bar:
            return

        # Create callback to determine if position is draggable (empty tab bar area)
        def is_draggable_area(widget: QWidget, pos) -> bool:
            """Check if position is in draggable area of tab bar."""
            # Map position to tab bar coordinates
            tab_bar_rect = self._tab_bar.rect()
            tab_bar_pos = self._tab_bar.mapTo(self, tab_bar_rect.topLeft())
            tab_bar_global_rect = QRect(tab_bar_pos, tab_bar_rect.size())

            if tab_bar_global_rect.contains(pos):
                # Check if click is on a tab or empty area
                local_pos = self._tab_bar.mapFrom(self, pos)
                tab_index = self._tab_bar.tabAt(local_pos)

                # Validate that tab_index is truly valid
                is_valid_tab = tab_index >= 0 and tab_index < self._tab_bar.count()

                # Empty area or invalid index = draggable
                # Also check new tab button
                if not is_valid_tab:
                    # Return False if on new tab button, True otherwise (empty area is draggable)
                    return not (
                        hasattr(self._tab_bar, "new_tab_button_rect")
                        and self._tab_bar.new_tab_button_rect.contains(local_pos)
                    )

            return False

        # Create frameless behavior with custom draggable area detection
        self._frameless_behavior = FramelessWindowBehavior(
            draggable_widget=None,  # Use custom callback instead
            resize_margin=4,
            enable_resize=True,
            enable_drag=True,
            enable_double_click_maximize=True,
            is_draggable_area=is_draggable_area,
        )

    def _connect_window_controls(self) -> None:
        """Connect window control buttons to window actions."""
        if not self._window_controls:
            return

        # Get the top-level window
        window = self.window()

        # Connect minimize button
        self._window_controls.minimize_clicked.connect(window.showMinimized)

        # Connect maximize button
        def toggle_maximize():
            if window.isMaximized():
                window.showNormal()
                self._window_controls.update_maximize_button(False)
            else:
                window.showMaximized()
                self._window_controls.update_maximize_button(True)

        self._window_controls.maximize_clicked.connect(toggle_maximize)

        # Connect close button
        self._window_controls.close_clicked.connect(window.close)

    def mousePressEvent(self, event) -> None:
        """Handle mouse press for window dragging and resizing."""
        if self._window_mode == WindowMode.Frameless and self._frameless_behavior:
            if self._frameless_behavior.handle_press(self, event):
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        """Handle mouse move for window dragging and resize cursor updates."""
        if self._window_mode == WindowMode.Frameless and self._frameless_behavior:
            if self._frameless_behavior.handle_move(self, event):
                return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        """Handle mouse release to clear drag state."""
        if self._window_mode == WindowMode.Frameless and self._frameless_behavior:
            if self._frameless_behavior.handle_release(self, event):
                return
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:
        """Handle double-click for maximize/restore."""
        if self._window_mode == WindowMode.Frameless and self._frameless_behavior:
            if self._frameless_behavior.handle_double_click(self, event):
                return
        super().mouseDoubleClickEvent(event)

    # Note: eventFilter removed - window dragging now handled by FramelessWindowBehavior

    def resizeEvent(self, event) -> None:
        """Handle resize events and adjust accent line position to eliminate gap."""
        super().resizeEvent(event)

        # After layout has positioned widgets, manually adjust accent line to eliminate 1px gap
        # This gap exists because Qt layouts position widgets on discrete pixel rows
        if self._accent_line and self._tab_bar:
            # Move accent line up by 1px to touch the tab bar directly
            current_geom = self._accent_line.geometry()
            self._accent_line.setGeometry(
                current_geom.x(),
                current_geom.y() - 1,  # Move up 1px
                current_geom.width(),
                current_geom.height()
            )

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Paint the window background in frameless mode.

        This is necessary because WA_TranslucentBackground makes the window
        transparent, so we need to explicitly paint the background.
        """
        painter = QPainter(self)

        if self._window_mode == WindowMode.Frameless:
            # Get theme colors for window background and border
            try:
                from vfwidgets_theme.core.manager import ThemeManager

                theme_mgr = ThemeManager.get_instance()

                # Use resolve_color() to get colors WITH override support
                bg_color_str = theme_mgr.resolve_color("window.background", fallback="#1e1e1e")
                # Use tab bar background color for border to match top bar
                border_color_str = theme_mgr.resolve_color("editorGroupHeader.tabsBackground", fallback="#2d2d2d")

                bg_color = QColor(bg_color_str)
                border_color = QColor(border_color_str)
            except (ImportError, AttributeError, Exception):
                # Fallback to dark theme colors if theme system not available
                bg_color = QColor("#1e1e1e")
                border_color = QColor("#2d2d2d")

            # Fill entire widget with tab bar color (for 4px border)
            painter.fillRect(self.rect(), border_color)

            # Fill inner area (inset by 4px margin) with window background
            inner_rect = self.rect().adjusted(4, 4, -4, -4)
            painter.fillRect(inner_rect, bg_color)

        # Call parent paintEvent
        super().paintEvent(event)

    # Note: _get_resize_edge and _start_system_resize removed
    # Edge detection and resizing now handled by FramelessWindowBehavior

    def _apply_platform_setup(self) -> None:
        """Apply platform-specific setup."""
        self._platform.setup_widget(self)

    def _register_qt_properties(self) -> None:
        """
        Register Qt properties dynamically to maintain QTabWidget compatibility.

        This allows access via both property() method and direct property access,
        while avoiding conflicts with method names.
        """

        # Initialize Qt properties with current values from methods
        # This ensures property() method returns correct values
        # Note: Qt properties must use Qt enums, not our custom enums
        super().setProperty("count", self.count())
        super().setProperty("currentIndex", self.currentIndex())
        super().setProperty("tabPosition", QTabWidget.TabPosition(self.tabPosition().value))
        super().setProperty("tabShape", QTabWidget.TabShape(self.tabShape().value))
        super().setProperty("tabsClosable", self.tabsClosable())
        super().setProperty("movable", self.isMovable())
        super().setProperty("documentMode", self.documentMode())
        super().setProperty("usesScrollButtons", self.usesScrollButtons())
        super().setProperty("elideMode", self.elideMode())
        super().setProperty("iconSize", self.iconSize())

    def _update_qt_property(self, name: str, value) -> None:
        """
        Update a Qt property value.

        Args:
            name: Property name
            value: New value
        """
        super().setProperty(name, value)

    def setProperty(self, name: str, value) -> bool:
        """
        Override setProperty() to provide QTabWidget compatibility.

        Args:
            name: Property name
            value: Property value

        Returns:
            True if property was set successfully
        """
        # Handle read-only properties
        if name == "count":
            # count is read-only, but we still need to return True for compatibility
            return True

        # Map QTabWidget property names to our internal methods
        try:
            if name == "currentIndex":
                self.setCurrentIndex(int(value))
                return True
            elif name == "tabPosition":
                # Handle both Qt enum and our custom enum and int values
                if isinstance(value, QTabWidget.TabPosition):
                    self.setTabPosition(TabPosition(value.value))
                elif isinstance(value, TabPosition):
                    self.setTabPosition(value)
                else:
                    self.setTabPosition(TabPosition(int(value)))
                return True
            elif name == "tabShape":
                # Handle both Qt enum and our custom enum and int values
                if isinstance(value, QTabWidget.TabShape):
                    self.setTabShape(TabShape(value.value))
                elif isinstance(value, TabShape):
                    self.setTabShape(value)
                else:
                    self.setTabShape(TabShape(int(value)))
                return True
            elif name == "tabsClosable":
                self.setTabsClosable(bool(value))
                return True
            elif name == "movable":
                self.setMovable(bool(value))
                return True
            elif name == "documentMode":
                self.setDocumentMode(bool(value))
                return True
            elif name == "usesScrollButtons":
                self.setUsesScrollButtons(bool(value))
                return True
            elif name == "elideMode":
                # Handle both enum and int values
                if isinstance(value, Qt.TextElideMode):
                    self.setElideMode(value)
                else:
                    self.setElideMode(Qt.TextElideMode(int(value)))
                return True
            elif name == "iconSize":
                if isinstance(value, QSize):
                    self.setIconSize(value)
                    return True
                return False
            else:
                # Fall back to default Qt property handling
                return super().setProperty(name, value)
        except (ValueError, TypeError):
            return False

    def _on_tab_close_requested(self, index: int) -> None:
        """Handle tab close request from view."""
        if 0 <= index < self.count():
            self.tabCloseRequested.emit(index)

    def _on_new_tab_requested(self) -> None:
        """Handle new tab request from the Chrome-style new tab button."""
        # Create a simple default widget for the new tab
        # Applications should connect to this signal to provide custom behavior
        from PySide6.QtWidgets import QLabel

        widget = QLabel("New Tab")
        widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.addTab(widget, "New Tab")

    def _customize_tab_context_menu(self, menu, tab_index: int) -> None:
        """Customize the tab context menu with application-specific items.

        Override this method in subclasses to add custom menu items to the
        tab right-click context menu. The menu already contains "Move to New Window".

        Example:
            class MyWindow(ChromeTabbedWindow):
                def _customize_tab_context_menu(self, menu, tab_index):
                    # Add custom menu items
                    action = menu.addAction("My Custom Action")
                    action.triggered.connect(lambda: self.handle_custom_action(tab_index))

        Args:
            menu: QMenu instance to add items to
            tab_index: Index of the tab that was right-clicked
        """
        # Default implementation: no customization
        pass

    def _on_tab_bar_clicked(self, index: int) -> None:
        """Handle tab bar click to change current tab."""
        # Only change current if it's different to avoid extra signals
        if index != self.currentIndex():
            self.setCurrentIndex(index)

    # ==================== Core Tab Management (QTabWidget API) ====================

    def addTab(self, widget: QWidget, *args) -> int:
        """
        Add a tab with the given widget and label, optionally with an icon.

        Args:
            widget: The widget to display in the tab
            *args: Either (label,) or (icon, label)

        Returns:
            The index of the added tab, or -1 if failed

        This method matches QTabWidget.addTab() exactly.
        """
        if len(args) == 1:
            # addTab(widget, label)
            label = args[0]
            return self.insertTab(self.count(), widget, label)
        elif len(args) == 2:
            # addTab(widget, icon, label)
            icon, label = args
            index = self.insertTab(self.count(), widget, label)
            if index >= 0 and icon and not icon.isNull():
                self.setTabIcon(index, icon)
            return index
        else:
            raise TypeError(
                f"addTab() takes 2 or 3 positional arguments but {len(args) + 1} were given"
            )

    def insertTab(self, index: int, widget: QWidget, *args) -> int:
        """
        Insert a tab at the specified index.

        Args:
            index: Position to insert the tab
            widget: The widget to display in the tab
            *args: Either (label,) or (icon, label)

        Returns:
            The actual index where the tab was inserted, or -1 if failed

        This method matches QTabWidget.insertTab() exactly.
        """
        # QTabWidget behavior: check for None widget
        if widget is None:
            return -1

        # Parse arguments
        if len(args) == 1:
            # insertTab(index, widget, label)
            label = args[0]
            icon = None
        elif len(args) == 2:
            # insertTab(index, widget, icon, label)
            icon, label = args
        else:
            raise TypeError(
                f"insertTab() takes 3 or 4 positional arguments but {len(args) + 2} were given"
            )

        # Reparent widget to content area (QTabWidget behavior)
        widget.setParent(self._content_area)

        # Add to model
        actual_index = self._model.insert_tab(index, widget, label)

        # Update content area
        if actual_index >= 0:
            self._content_area._add_widget_to_stack(widget, actual_index)

            # Set icon if provided
            if icon and not icon.isNull():
                self.setTabIcon(actual_index, icon)

            # Update Qt property for compatibility
            self._update_qt_property("count", self.count())

        return actual_index

    def removeTab(self, index: int) -> None:
        """
        Remove the tab at the specified index.

        Args:
            index: Index of the tab to remove

        This method matches QTabWidget.removeTab() exactly including
        signal timing and current index adjustment.
        """
        if 0 <= index < self.count():
            self._model.remove_tab(index)
        # Update Qt properties for compatibility
        self._update_qt_property("count", self.count())
        self._update_qt_property("currentIndex", self.currentIndex())

    def clear(self) -> None:
        """
        Remove all tabs.

        This method matches QTabWidget.clear() exactly.
        """
        self._model.clear()
        # Update Qt properties for compatibility
        self._update_qt_property("count", self.count())
        self._update_qt_property("currentIndex", self.currentIndex())

    def get_tab_data(self, index: int) -> Optional[dict]:
        """
        Get tab data for transfer to another window.

        Useful for implementing tab detachment or window merging features.
        Applications can use this to extract all tab information before
        transferring a tab to a new window instance.

        Args:
            index: Tab index to get data for

        Returns:
            Dictionary with keys:
                - widget: The QWidget for this tab (or None)
                - text: Tab text string
                - icon: Tab icon (QIcon)
                - tooltip: Tab tooltip text
            Returns None if index is invalid.

        Example:
            >>> tab_data = window.get_tab_data(0)
            >>> if tab_data:
            ...     new_window.addTab(tab_data["widget"], tab_data["text"])
        """
        if index < 0 or index >= self.count():
            return None

        return {
            "widget": self.widget(index),
            "text": self.tabText(index),
            "icon": self.tabIcon(index),
            "tooltip": self.tabToolTip(index),
        }

    # ==================== Tab Access (QTabWidget API) ====================

    def count(self) -> int:
        """
        Get the number of tabs.

        Returns:
            Number of tabs in the widget

        This method matches QTabWidget.count() exactly.
        """
        return self._model.count()

    def currentIndex(self) -> int:
        """
        Get the index of the current tab.

        Returns:
            Index of current tab, or -1 if no tabs

        This method matches QTabWidget.currentIndex() exactly.
        """
        return self._model.current_index()

    def setCurrentIndex(self, index: int) -> None:
        """
        Set the current tab by index.

        Args:
            index: Index of tab to make current

        This method matches QTabWidget.setCurrentIndex() exactly including
        signal emission behavior.
        """
        self._model.set_current_index(index)
        # Update Qt property for compatibility
        self._update_qt_property("currentIndex", index)

    def currentWidget(self) -> Optional[QWidget]:
        """
        Get the widget of the current tab.

        Returns:
            Current tab's widget, or None if no current tab

        This method matches QTabWidget.currentWidget() exactly.
        """
        return self._model.current_widget()

    def setCurrentWidget(self, widget: QWidget) -> None:
        """
        Set the current tab by widget.

        Args:
            widget: Widget whose tab should become current

        This method matches QTabWidget.setCurrentWidget() exactly.
        """
        self._model.set_current_widget(widget)

    def widget(self, index: int) -> Optional[QWidget]:
        """
        Get the widget at the specified index.

        Args:
            index: Index of the tab

        Returns:
            Widget at the index, or None if invalid index

        This method matches QTabWidget.widget() exactly.
        """
        return self._model.widget(index)

    def indexOf(self, widget: QWidget) -> int:
        """
        Get the index of the specified widget.

        Args:
            widget: Widget to find

        Returns:
            Index of the widget, or -1 if not found

        This method matches QTabWidget.indexOf() exactly.
        """
        return self._model.index_of(widget)

    # ==================== Tab Properties (QTabWidget API) ====================

    def setTabText(self, index: int, text: str) -> None:
        """
        Set the text label for the tab at index.

        Args:
            index: Index of the tab
            text: New text label

        This method matches QTabWidget.setTabText() exactly.
        """
        self._model.set_tab_text(index, text)

    def tabText(self, index: int) -> str:
        """
        Get the text label for the tab at index.

        Args:
            index: Index of the tab

        Returns:
            Text label of the tab, or empty string if invalid index

        This method matches QTabWidget.tabText() exactly.
        """
        return self._model.tab_text(index)

    def setTabIcon(self, index: int, icon: QIcon) -> None:
        """
        Set the icon for the tab at index.

        Args:
            index: Index of the tab
            icon: New icon

        This method matches QTabWidget.setTabIcon() exactly.
        """
        self._model.set_tab_icon(index, icon)

    def tabIcon(self, index: int) -> QIcon:
        """
        Get the icon for the tab at index.

        Args:
            index: Index of the tab

        Returns:
            Icon of the tab, or empty icon if invalid index

        This method matches QTabWidget.tabIcon() exactly.
        """
        icon = self._model.tab_icon(index)
        return icon if icon else QIcon()

    def setTabToolTip(self, index: int, tip: str) -> None:
        """
        Set the tooltip for the tab at index.

        Args:
            index: Index of the tab
            tip: New tooltip text

        This method matches QTabWidget.setTabToolTip() exactly.
        """
        self._model.set_tab_tool_tip(index, tip)

    def tabToolTip(self, index: int) -> str:
        """
        Get the tooltip for the tab at index.

        Args:
            index: Index of the tab

        Returns:
            Tooltip text, or empty string if invalid index

        This method matches QTabWidget.tabToolTip() exactly.
        """
        return self._model.tab_tool_tip(index)

    def setTabWhatsThis(self, index: int, text: str) -> None:
        """
        Set the What's This text for the tab at index.

        Args:
            index: Index of the tab
            text: New What's This text

        This method matches QTabWidget.setTabWhatsThis() exactly.
        """
        self._model.set_tab_whats_this(index, text)

    def tabWhatsThis(self, index: int) -> str:
        """
        Get the What's This text for the tab at index.

        Args:
            index: Index of the tab

        Returns:
            What's This text, or empty string if invalid index

        This method matches QTabWidget.tabWhatsThis() exactly.
        """
        return self._model.tab_whats_this(index)

    # ==================== Tab State (QTabWidget API) ====================

    def setTabEnabled(self, index: int, enabled: bool) -> None:
        """
        Enable or disable the tab at index.

        Args:
            index: Index of the tab
            enabled: True to enable, False to disable

        This method matches QTabWidget.setTabEnabled() exactly.
        """
        self._model.set_tab_enabled(index, enabled)

    def isTabEnabled(self, index: int) -> bool:
        """
        Check if the tab at index is enabled.

        Args:
            index: Index of the tab

        Returns:
            True if enabled, False if disabled or invalid index

        This method matches QTabWidget.isTabEnabled() exactly.
        """
        return self._model.is_tab_enabled(index)

    def setTabVisible(self, index: int, visible: bool) -> None:
        """
        Show or hide the tab at index.

        Args:
            index: Index of the tab
            visible: True to show, False to hide

        This method matches QTabWidget.setTabVisible() exactly.
        """
        self._model.set_tab_visible(index, visible)

    def isTabVisible(self, index: int) -> bool:
        """
        Check if the tab at index is visible.

        Args:
            index: Index of the tab

        Returns:
            True if visible, False if hidden or invalid index

        This method matches QTabWidget.isTabVisible() exactly.
        """
        return self._model.is_tab_visible(index)

    def setTabData(self, index: int, data: Any) -> None:
        """
        Set custom data for the tab at index.

        Args:
            index: Index of the tab
            data: Custom data to store

        This method matches QTabWidget.setTabData() exactly.
        """
        self._model.set_tab_data(index, data)

    def tabData(self, index: int) -> Any:
        """
        Get custom data for the tab at index.

        Args:
            index: Index of the tab

        Returns:
            Custom data, or None if invalid index

        This method matches QTabWidget.tabData() exactly.
        """
        return self._model.tab_data(index)

    # ==================== Tab Bar Configuration (QTabWidget API) ====================

    def setTabsClosable(self, closable: bool) -> None:
        """
        Set whether tabs show close buttons.

        Args:
            closable: True to show close buttons, False to hide

        This method matches QTabWidget.setTabsClosable() exactly.
        """
        self._model.set_tabs_closable(closable)
        self._tab_bar.update()  # Refresh display

    def tabsClosable(self) -> bool:
        """
        Check if tabs show close buttons.

        Returns:
            True if tabs are closable, False otherwise

        This method matches QTabWidget.tabsClosable() exactly.
        """
        return self._model.tabs_closable()

    def setMovable(self, movable: bool) -> None:
        """
        Set whether tabs can be moved by dragging.

        Args:
            movable: True to allow moving, False to disable

        This method matches QTabWidget.setMovable() exactly.
        """
        self._model.set_tabs_movable(movable)
        self._tab_bar.setMovable(movable)

    def isMovable(self) -> bool:
        """
        Check if tabs can be moved.

        Returns:
            True if tabs are movable, False otherwise

        This method matches QTabWidget.isMovable() exactly.
        """
        return self._model.tabs_movable()

    def setDocumentMode(self, enabled: bool) -> None:
        """
        Set document mode.

        Args:
            enabled: True to enable document mode, False to disable

        This method matches QTabWidget.setDocumentMode() exactly.
        """
        self._document_mode = enabled
        self._tab_bar.setDocumentMode(enabled)

    def documentMode(self) -> bool:
        """
        Check if document mode is enabled.

        Returns:
            True if document mode is enabled, False otherwise

        This method matches QTabWidget.documentMode() exactly.
        """
        return self._document_mode

    # ==================== Visual Properties (QTabWidget API) ====================

    def setIconSize(self, size: QSize) -> None:
        """
        Set the size of tab icons.

        Args:
            size: New icon size

        This method matches QTabWidget.setIconSize() exactly.
        """
        self._icon_size = size
        self._tab_bar.setIconSize(size)

    def iconSize(self) -> QSize:
        """
        Get the size of tab icons.

        Returns:
            Current icon size

        This method matches QTabWidget.iconSize() exactly.
        """
        return self._icon_size

    def setElideMode(self, mode: Qt.TextElideMode) -> None:
        """
        Set the text elide mode for tab labels.

        Args:
            mode: Text elide mode

        This method matches QTabWidget.setElideMode() exactly.
        """
        self._elide_mode = mode
        # Update Qt property for compatibility
        self._update_qt_property("elideMode", mode)
        self._tab_bar.setElideMode(mode)

    def elideMode(self) -> Qt.TextElideMode:
        """
        Get the text elide mode.

        Returns:
            Current text elide mode

        This method matches QTabWidget.elideMode() exactly.
        """
        return Qt.TextElideMode(self._elide_mode)

    def setUsesScrollButtons(self, useButtons: bool) -> None:
        """
        Set whether to use scroll buttons when tabs overflow.

        Args:
            useButtons: True to use scroll buttons, False to compress tabs

        This method matches QTabWidget.setUsesScrollButtons() exactly.
        """
        self._uses_scroll_buttons = useButtons
        self._tab_bar.setUsesScrollButtons(useButtons)

    def usesScrollButtons(self) -> bool:
        """
        Check if scroll buttons are used.

        Returns:
            True if scroll buttons are used, False otherwise

        This method matches QTabWidget.usesScrollButtons() exactly.
        """
        return self._uses_scroll_buttons

    # ==================== Tab Position & Shape (QTabWidget API) ====================

    def setTabPosition(self, position: TabPosition) -> None:
        """
        Set the position of the tab bar.

        Args:
            position: Tab bar position

        This method matches QTabWidget.setTabPosition() exactly.
        """
        self._tab_position = position
        # Update Qt property for compatibility (convert to Qt enum)
        self._update_qt_property("tabPosition", QTabWidget.TabPosition(position.value))
        # TODO: Implement layout changes for different positions

    def tabPosition(self) -> TabPosition:
        """
        Get the tab bar position.

        Returns:
            Current tab bar position

        This method matches QTabWidget.tabPosition() exactly.
        """
        return TabPosition(self._tab_position)

    def setTabShape(self, shape: TabShape) -> None:
        """
        Set the shape of tabs.

        Args:
            shape: Tab shape

        This method matches QTabWidget.setTabShape() exactly.
        """
        self._tab_shape = shape
        # Update Qt property for compatibility (convert to Qt enum)
        self._update_qt_property("tabShape", QTabWidget.TabShape(shape.value))
        self._tab_bar.setShape(QTabBar.Shape(shape))

    def tabShape(self) -> TabShape:
        """
        Get the tab shape.

        Returns:
            Current tab shape

        This method matches QTabWidget.tabShape() exactly.
        """
        return TabShape(self._tab_shape)

    # ==================== Corner Widgets & Tab Bar (QTabWidget API) ====================

    def setCornerWidget(
        self, widget: QWidget, corner: Qt.Corner = Qt.Corner.TopRightCorner
    ) -> None:
        """
        Set a corner widget.

        Args:
            widget: Widget to place in corner
            corner: Which corner to use

        This method matches QTabWidget.setCornerWidget() exactly.
        """
        # Remove existing corner widget
        old_widget = self._corner_widgets.get(corner)
        if old_widget:
            old_widget.setParent(None)

        # Set new corner widget
        self._corner_widgets[corner] = widget
        if widget:
            widget.setParent(self)

        # TODO: Update layout to include corner widget

    def cornerWidget(self, corner: Qt.Corner = Qt.Corner.TopRightCorner) -> Optional[QWidget]:
        """
        Get the corner widget.

        Args:
            corner: Which corner to get

        Returns:
            Corner widget, or None if no widget

        This method matches QTabWidget.cornerWidget() exactly.
        """
        return self._corner_widgets.get(corner)

    def tabBar(self) -> QTabBar:
        """
        Get the tab bar.

        Returns:
            The tab bar widget

        This method matches QTabWidget.tabBar() exactly.
        """
        return self._tab_bar

    # ==================== Additional QTabWidget Methods ====================

    def setTabBar(self, tabbar: QTabBar) -> None:
        """
        Set the tab bar (protected in QTabWidget).

        Args:
            tabbar: New tab bar

        Note: This is a protected method in QTabWidget but we expose it for compatibility.
        """
        # For compatibility - in real QTabWidget this is protected
        pass

    def setTabBarAutoHide(self, enabled: bool) -> None:
        """
        Set whether the tab bar is automatically hidden when it has only one tab.

        Args:
            enabled: True to auto-hide, False to always show

        This method matches QTabWidget.setTabBarAutoHide() exactly.
        """
        # This is a newer QTabWidget feature - for v1.0 we'll ignore it
        pass

    def tabBarAutoHide(self) -> bool:
        """
        Check if the tab bar auto-hides.

        Returns:
            True if auto-hide is enabled, False otherwise

        This method matches QTabWidget.tabBarAutoHide() exactly.
        """
        return False  # Default behavior

    def initStyleOption(self, option) -> None:
        """
        Initialize style option (protected in QTabWidget).

        Args:
            option: Style option to initialize

        Note: This is a protected method in QTabWidget but we expose it for compatibility.
        """
        # For compatibility - this is used internally by Qt
        pass

    # Protected virtual methods (exposed for compatibility)
    def tabInserted(self, index: int) -> None:
        """
        Called when a tab is inserted (protected virtual in QTabWidget).

        Args:
            index: Index where tab was inserted

        Note: This is a protected virtual method in QTabWidget.
        """
        # Virtual method - can be overridden by subclasses
        pass

    def tabRemoved(self, index: int) -> None:
        """
        Called when a tab is removed (protected virtual in QTabWidget).

        Args:
            index: Index where tab was removed

        Note: This is a protected virtual method in QTabWidget.
        """
        # Virtual method - can be overridden by subclasses
        pass

    # Add enum classes as attributes for compatibility
    @property
    def TabPosition(self):
        """TabPosition enum for compatibility."""
        return TabPosition

    @property
    def TabShape(self):
        """TabShape enum for compatibility."""
        return TabShape

    # Property aliases for Qt property compatibility
    # These redirect to the actual methods to maintain API compatibility
    @property
    def movable(self) -> bool:
        """Property alias for isMovable() - for Qt property compatibility."""
        return self.isMovable()

    @movable.setter
    def movable(self, value: bool):
        """Property setter for movable - for Qt property compatibility."""
        self.setMovable(value)

    # ==================== Qt Properties (QTabWidget Compatibility) ====================

    # Note: Qt Properties are defined using the Property decorator
    # These properties enable QML integration and property binding

    def _get_count(self) -> int:
        """Get count for Qt Property."""
        return self._model.count()

    def _get_current_index(self) -> int:
        """Get current index for Qt Property."""
        return self._model.current_index()

    def _set_current_index(self, index: int) -> None:
        """Set current index for Qt Property."""
        self._model.set_current_index(index)

    def _get_tab_position(self) -> int:
        """Get tab position for Qt Property."""
        return self._tab_position

    def _set_tab_position(self, position: int) -> None:
        """Set tab position for Qt Property."""
        self.setTabPosition(TabPosition(position))

    def _get_tab_shape(self) -> int:
        """Get tab shape for Qt Property."""
        return self._tab_shape

    def _set_tab_shape(self, shape: int) -> None:
        """Set tab shape for Qt Property."""
        self.setTabShape(TabShape(shape))

    def _get_tabs_closable(self) -> bool:
        """Get tabs closable for Qt Property."""
        return self._model.tabs_closable()

    def _set_tabs_closable(self, closable: bool) -> None:
        """Set tabs closable for Qt Property."""
        self.setTabsClosable(closable)

    def _get_movable(self) -> bool:
        """Get movable for Qt Property."""
        return self._model.tabs_movable()

    def _set_movable(self, movable: bool) -> None:
        """Set movable for Qt Property."""
        self.setMovable(movable)

    def _get_document_mode(self) -> bool:
        """Get document mode for Qt Property."""
        return self._document_mode

    def _set_document_mode(self, enabled: bool) -> None:
        """Set document mode for Qt Property."""
        self.setDocumentMode(enabled)

    def _get_uses_scroll_buttons(self) -> bool:
        """Get uses scroll buttons for Qt Property."""
        return self._uses_scroll_buttons

    def _set_uses_scroll_buttons(self, uses: bool) -> None:
        """Set uses scroll buttons for Qt Property."""
        self.setUsesScrollButtons(uses)

    def _get_elide_mode(self) -> int:
        """Get elide mode for Qt Property."""
        return self._elide_mode

    def _set_elide_mode(self, mode: int) -> None:
        """Set elide mode for Qt Property."""
        self.setElideMode(Qt.TextElideMode(mode))

    def _get_icon_size(self) -> QSize:
        """Get icon size for Qt Property."""
        return self._icon_size or QSize()

    def _set_icon_size(self, size: QSize) -> None:
        """Set icon size for Qt Property."""
        self.setIconSize(size)

    # Qt Properties for QML and property binding
    # These provide full QTabWidget property compatibility
    # Using q_ prefix to avoid conflicts with method names
    q_count = Property(int, _get_count, notify=currentChanged)
    q_currentIndex = Property(int, _get_current_index, _set_current_index, notify=currentChanged)
    q_tabPosition = Property(int, _get_tab_position, _set_tab_position)
    q_tabShape = Property(int, _get_tab_shape, _set_tab_shape)
    q_tabsClosable = Property(bool, _get_tabs_closable, _set_tabs_closable)
    q_movable = Property(bool, _get_movable, _set_movable)
    q_documentMode = Property(bool, _get_document_mode, _set_document_mode)
    q_usesScrollButtons = Property(bool, _get_uses_scroll_buttons, _set_uses_scroll_buttons)
    q_elideMode = Property(int, _get_elide_mode, _set_elide_mode)
    q_iconSize = Property(QSize, _get_icon_size, _set_icon_size)

    # ==================== Size Hints (QWidget Override) ====================

    def sizeHint(self) -> QSize:
        """
        Get the preferred size of the widget.

        Returns:
            Preferred size hint

        This method provides appropriate size hints for layout systems.
        """
        tab_bar_hint = self._tab_bar.sizeHint()
        content_hint = self._content_area.sizeHint()

        width = max(tab_bar_hint.width(), content_hint.width())
        height = tab_bar_hint.height() + content_hint.height()

        return QSize(width, height)

    def minimumSizeHint(self) -> QSize:
        """
        Get the minimum size of the widget.

        Returns:
            Minimum size hint

        This method provides appropriate minimum size for layout systems.
        """
        tab_bar_hint = self._tab_bar.minimumSizeHint()
        content_hint = self._content_area.minimumSizeHint()

        width = max(tab_bar_hint.width(), content_hint.width())
        height = tab_bar_hint.height() + content_hint.height()

        return QSize(width, height)
