"""ViloCodeWindow - VS Code-style application window.

This module implements the main ViloCodeWindow widget.
"""

from typing import TYPE_CHECKING, Callable, Optional

if TYPE_CHECKING:
    from .components.activity_bar import ActivityBar
    from .components.auxiliary_bar import AuxiliaryBar
    from .components.sidebar import SideBar
    from .components.title_bar import TitleBar

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QIcon, QMouseEvent, QPainter, QPaintEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMenuBar,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)
from vfwidgets_common import FramelessWindowBehavior

from .core.constants import WindowMode
from .core.shortcut_manager import ShortcutManager

# Check if theme system is available
try:
    from vfwidgets_theme import ThemedWidget

    THEME_AVAILABLE = True

    class ViloCodeWindowBase(ThemedWidget, QWidget):  # type: ignore
        """Base class with theme support."""

        pass

except ImportError:
    THEME_AVAILABLE = False

    class ViloCodeWindowBase(QWidget):  # type: ignore[no-redef]
        """Base class without theme support."""

        pass


class ViloCodeWindow(ViloCodeWindowBase):
    """VS Code-style application window.

    A frameless window widget with activity bar, sidebar, main pane,
    and auxiliary bar. Provides a complete foundation for building
    IDE-style applications.

    The widget automatically detects whether it's being used as a
    top-level window (frameless mode) or embedded in another widget.

    Args:
        parent: Optional parent widget
        enable_default_shortcuts: Enable VS Code-compatible keyboard shortcuts

    Signals:
        activity_item_clicked: Emitted when an activity item is clicked (item_id)
        sidebar_panel_changed: Emitted when sidebar panel changes (panel_id)
        sidebar_visibility_changed: Emitted when sidebar visibility changes (is_visible)
        auxiliary_bar_visibility_changed: Emitted when auxiliary bar visibility changes (is_visible)

    Example:
        >>> from vfwidgets_vilocode_window import ViloCodeWindow
        >>> window = ViloCodeWindow()
        >>> window.show()
    """

    # Theme configuration (if theme system available)
    if THEME_AVAILABLE:
        theme_config = {
            "window_background": "editor.background",
            "titlebar_background": "titleBar.activeBackground",
            "titlebar_foreground": "titleBar.activeForeground",
            "statusbar_background": "statusBar.background",
            "statusbar_foreground": "statusBar.foreground",
            "border_color": "panel.border",
        }

    # Signals
    activity_item_clicked = Signal(str)  # item_id
    sidebar_panel_changed = Signal(str)  # panel_id
    sidebar_visibility_changed = Signal(bool)  # is_visible
    auxiliary_bar_visibility_changed = Signal(bool)  # is_visible

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        enable_default_shortcuts: bool = True,
    ):
        super().__init__(parent)

        # Mode detection
        self._window_mode = self._detect_window_mode()

        # Setup frameless window if needed
        if self._window_mode == WindowMode.Frameless:
            self._setup_frameless_window()

        # Components (create in later tasks)
        self._activity_bar: Optional[ActivityBar] = None
        self._sidebar: Optional[SideBar] = None
        self._main_pane: Optional[QWidget] = None
        self._auxiliary_bar: Optional[AuxiliaryBar] = None
        self._status_bar: QStatusBar  # Will be initialized in _setup_ui
        self._menu_bar: Optional[QMenuBar] = None
        self._title_bar: Optional[TitleBar] = None  # Will be initialized in _setup_ui if frameless

        # Main content management
        self._main_content: Optional[QWidget] = None
        self._content_layout: Optional[QHBoxLayout] = None

        # Frameless window behavior (initialized after _setup_ui creates title_bar)
        self._frameless_behavior: Optional[FramelessWindowBehavior] = None

        # Keyboard shortcuts
        self._shortcut_manager = ShortcutManager(self)
        self._enable_default_shortcuts = enable_default_shortcuts

        self._setup_ui()

        if enable_default_shortcuts:
            self._setup_default_shortcuts()

    def _detect_window_mode(self) -> WindowMode:
        """Detect if widget is top-level (frameless) or embedded.

        Returns:
            WindowMode.Frameless if no parent (top-level window)
            WindowMode.Embedded if has parent (embedded widget)
        """
        if self.parent() is None:
            return WindowMode.Frameless
        else:
            return WindowMode.Embedded

    def _setup_frameless_window(self) -> None:
        """Set up frameless window for top-level mode."""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowSystemMenuHint
            | Qt.WindowType.WindowMinMaxButtonsHint
            | Qt.WindowType.WindowCloseButtonHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumSize(600, 400)
        self.setMouseTracking(True)  # Enable mouse tracking for resize edge detection

        # Frameless behavior will be initialized in _setup_ui after title_bar is created

    def _initialize_frameless_behavior(self) -> None:
        """Initialize frameless window behavior after title_bar is created."""
        if self._window_mode != WindowMode.Frameless or self._title_bar is None:
            return

        # Create frameless behavior with title bar as draggable widget
        self._frameless_behavior = FramelessWindowBehavior(
            draggable_widget=self._title_bar,
            resize_margin=5,
            enable_resize=True,
            enable_drag=True,
            enable_double_click_maximize=True,
        )

    def _setup_ui(self) -> None:
        """Set up the user interface layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Title bar (frameless mode only)
        if self._window_mode == WindowMode.Frameless:
            from .components import TitleBar

            self._title_bar = TitleBar(self)
            self._title_bar.setObjectName("titleBar")
            self._title_bar.setAccessibleName("Title Bar")
            self._title_bar.setAccessibleDescription(
                "Custom window title bar with menu and controls"
            )
            main_layout.addWidget(self._title_bar)
        else:
            self._title_bar = None

        # Content layout (horizontal: activity + sidebar + main + auxiliary)
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        self._content_layout = content_layout  # Store for set_main_content()

        # Activity Bar
        from .components import ActivityBar

        self._activity_bar = ActivityBar(self)
        self._activity_bar.setObjectName("activityBar")
        self._activity_bar.setAccessibleName("Activity Bar")
        self._activity_bar.setAccessibleDescription(
            "VS Code-style activity bar with application views"
        )
        self._activity_bar.item_clicked.connect(self._on_activity_item_clicked)
        content_layout.addWidget(self._activity_bar)

        # Sidebar
        from .components import SideBar

        self._sidebar = SideBar(self)
        self._sidebar.setObjectName("sidebar")
        self._sidebar.setAccessibleName("Sidebar")
        self._sidebar.setAccessibleDescription("Collapsible sidebar for application panels")
        self._sidebar.panel_changed.connect(self._on_sidebar_panel_changed)
        self._sidebar.visibility_changed.connect(self._on_sidebar_visibility_changed)
        content_layout.addWidget(self._sidebar)

        main_label = QLabel("Main Pane\n(Content Area)")
        main_label.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4;")
        main_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_label.setObjectName("mainPane")
        main_label.setAccessibleName("Main Pane")
        main_label.setAccessibleDescription("Primary content area for application")
        content_layout.addWidget(main_label, 1)  # Stretch=1
        self._main_pane = main_label  # Store placeholder for set_main_content()

        # Auxiliary Bar
        from .components import AuxiliaryBar

        self._auxiliary_bar = AuxiliaryBar(self)
        self._auxiliary_bar.setObjectName("auxiliaryBar")
        self._auxiliary_bar.setAccessibleName("Auxiliary Bar")
        self._auxiliary_bar.setAccessibleDescription("Right auxiliary panel for secondary content")
        self._auxiliary_bar.visibility_changed.connect(self._on_auxiliary_bar_visibility_changed)
        content_layout.addWidget(self._auxiliary_bar)

        main_layout.addLayout(content_layout, 1)  # Stretch=1

        # Status bar
        self._status_bar = QStatusBar(self)
        self._status_bar.setObjectName("statusBar")
        self._status_bar.setAccessibleName("Status Bar")
        self._status_bar.setAccessibleDescription(
            "Application status bar showing current state and information"
        )
        self._status_bar.setStyleSheet("background-color: #007acc; color: #ffffff;")
        self._status_bar.showMessage("Ready")
        main_layout.addWidget(self._status_bar)

        # Apply theme colors after all components are created
        self._apply_theme_colors()

        # Initialize frameless behavior after title_bar is created
        self._initialize_frameless_behavior()

    def _setup_default_shortcuts(self) -> None:
        """Set up default VS Code-compatible shortcuts.

        Registers all default shortcuts and connects them to appropriate handlers.
        """
        # Load all default shortcut definitions
        self._shortcut_manager.load_default_shortcuts()

        # Register callbacks for view shortcuts
        self._shortcut_manager.register_callback("TOGGLE_SIDEBAR", self.toggle_sidebar)
        self._shortcut_manager.register_callback("TOGGLE_AUXILIARY_BAR", self.toggle_auxiliary_bar)
        self._shortcut_manager.register_callback("TOGGLE_STATUS_BAR", self._toggle_status_bar)

        # Register callbacks for window shortcuts (wrap methods that return values)
        def close_window() -> None:
            self.close()

        def minimize_window() -> None:
            self.showMinimized()

        self._shortcut_manager.register_callback("CLOSE_WINDOW", close_window)
        self._shortcut_manager.register_callback("MINIMIZE_WINDOW", minimize_window)
        self._shortcut_manager.register_callback("MAXIMIZE_WINDOW", self._toggle_maximize)

        # Register callbacks for panel focus shortcuts
        self._shortcut_manager.register_callback("FOCUS_SIDEBAR", self._focus_sidebar)
        self._shortcut_manager.register_callback("FOCUS_MAIN_PANE", self._focus_main_pane)

    def _toggle_status_bar(self) -> None:
        """Toggle status bar visibility (internal handler)."""
        self.set_status_bar_visible(not self.is_status_bar_visible())

    def _toggle_maximize(self) -> None:
        """Toggle maximize/restore window (internal handler)."""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint window background in frameless mode."""
        if self._window_mode == WindowMode.Frameless:
            painter = QPainter(self)

            # Get background color (fallback for now - ThemedWidget uses stylesheets)
            bg_color = self._get_fallback_color("window_background")
            border_color = self._get_fallback_color("border_color")

            # Fill background
            painter.fillRect(self.rect(), bg_color)

            # Draw border for definition
            painter.setPen(border_color)
            painter.drawRect(self.rect().adjusted(0, 0, -1, -1))

        super().paintEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press for window dragging and resizing."""
        if self._window_mode == WindowMode.Frameless and self._frameless_behavior:
            if self._frameless_behavior.handle_press(self, event):
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse move for window dragging and resize cursor updates."""
        if self._window_mode == WindowMode.Frameless and self._frameless_behavior:
            if self._frameless_behavior.handle_move(self, event):
                return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle mouse release to clear drag state."""
        if self._window_mode == WindowMode.Frameless and self._frameless_behavior:
            if self._frameless_behavior.handle_release(self, event):
                return
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """Handle double-click for maximize/restore."""
        if self._window_mode == WindowMode.Frameless and self._frameless_behavior:
            if self._frameless_behavior.handle_double_click(self, event):
                return
        super().mouseDoubleClickEvent(event)

    def _get_fallback_color(self, token: str) -> QColor:
        """Get fallback color when theme system unavailable.

        Args:
            token: Color token name

        Returns:
            QColor for the requested token
        """
        fallback_colors = {
            "window_background": "#1e1e1e",
            "titlebar_background": "#323233",
            "titlebar_foreground": "#cccccc",
            "statusbar_background": "#007acc",
            "statusbar_foreground": "#ffffff",
            "border_color": "#333333",
        }
        return QColor(fallback_colors.get(token, "#1e1e1e"))

    def _apply_theme_colors(self) -> None:
        """Apply theme colors to all components.

        When theme system is available, ThemedWidget handles styling via stylesheets.
        This method applies fallback colors when theme system is unavailable.
        """
        if not THEME_AVAILABLE:
            # Apply fallback colors only when theme system unavailable
            if self._title_bar:
                bg = self._get_fallback_color("titlebar_background")
                fg = self._get_fallback_color("titlebar_foreground")
                self._title_bar.setStyleSheet(f"background-color: {bg.name()}; color: {fg.name()};")

            if self._status_bar:
                bg = self._get_fallback_color("statusbar_background")
                fg = self._get_fallback_color("statusbar_foreground")
                self._status_bar.setStyleSheet(
                    f"background-color: {bg.name()}; color: {fg.name()};"
                )
        # else: ThemedWidget handles styling via stylesheets automatically

    def on_theme_changed(self) -> None:
        """Handle theme changes.

        This method is called automatically by ThemedWidget when the theme changes.
        ThemedWidget handles styling via stylesheets, so we just trigger a repaint.
        """
        if self._window_mode == WindowMode.Frameless:
            self.update()  # Repaint frameless window background

    # Status Bar API
    def get_status_bar(self) -> QStatusBar:
        """Get the status bar widget for customization.

        Returns:
            The status bar widget
        """
        return self._status_bar

    def set_status_bar_visible(self, visible: bool) -> None:
        """Show/hide status bar.

        Args:
            visible: True to show, False to hide
        """
        self._status_bar.setVisible(visible)

    def is_status_bar_visible(self) -> bool:
        """Check if status bar is visible.

        Returns:
            True if visible, False otherwise
        """
        return self._status_bar.isVisible()

    def set_status_message(self, message: str, timeout: int = 0) -> None:
        """Convenience method to show status message.

        Args:
            message: Status message to display
            timeout: Time in milliseconds (0 = until next message)
        """
        self._status_bar.showMessage(message, timeout)

    def setWindowTitle(self, title: str) -> None:
        """Set the window title.

        Overrides QWidget.setWindowTitle to also update the custom title bar.

        Args:
            title: Window title text
        """
        super().setWindowTitle(title)
        if self._title_bar and hasattr(self._title_bar, "set_title"):
            self._title_bar.set_title(title)

    # Main Content API
    def set_main_content(self, widget: QWidget) -> None:
        """Set the main content area widget.

        Replaces the placeholder main pane with your custom widget.
        Use any Qt widget here: QTextEdit, ChromeTabbedWindow, MultisplitWidget, etc.

        Args:
            widget: The widget to display in the main content area

        Example:
            editor = QTextEdit()
            window.set_main_content(editor)
        """
        if self._content_layout is None:
            raise RuntimeError("Content layout not initialized")

        # Remove current main content widget
        if self._main_content is not None:
            self._content_layout.removeWidget(self._main_content)
            self._main_content.setParent(None)
        elif self._main_pane is not None:
            # First time: remove the placeholder
            self._content_layout.removeWidget(self._main_pane)
            self._main_pane.setParent(None)
            self._main_pane = None

        # Add new widget
        self._main_content = widget
        # Insert at position 2 (after activity bar [0] and sidebar [1])
        self._content_layout.insertWidget(2, widget, 1)  # stretch=1

    def get_main_content(self) -> Optional[QWidget]:
        """Get the current main content widget.

        Returns:
            The main content widget, or None if not set (placeholder still showing)

        Example:
            current_editor = window.get_main_content()
            if current_editor:
                print("Content is set")
        """
        return self._main_content

    # Activity Bar API
    def add_activity_item(self, item_id: str, icon: QIcon, tooltip: str = "") -> None:
        """Add an item to the activity bar.

        Args:
            item_id: Unique identifier for this item
            icon: Icon to display
            tooltip: Tooltip text

        Example:
            >>> from PySide6.QtGui import QIcon
            >>> icon = QIcon.fromTheme("document-new")
            >>> window.add_activity_item("explorer", icon, "Explorer")
        """
        if self._activity_bar:
            self._activity_bar.add_item(item_id, icon, tooltip)

    def remove_activity_item(self, item_id: str) -> None:
        """Remove an item from the activity bar.

        Args:
            item_id: ID of item to remove
        """
        if self._activity_bar:
            self._activity_bar.remove_item(item_id)

    def set_active_activity_item(self, item_id: str) -> None:
        """Set the active (highlighted) activity item.

        Args:
            item_id: ID of item to activate
        """
        if self._activity_bar:
            self._activity_bar.set_active_item(item_id)

    def get_active_activity_item(self) -> Optional[str]:
        """Get the currently active activity item ID.

        Returns:
            Active item ID, or None if no item is active
        """
        if self._activity_bar:
            return self._activity_bar.get_active_item()
        return None

    def _on_activity_item_clicked(self, item_id: str) -> None:
        """Handle activity item click.

        Args:
            item_id: ID of clicked item
        """
        # Emit public signal
        self.activity_item_clicked.emit(item_id)

    # Sidebar API
    def add_sidebar_panel(self, panel_id: str, widget: QWidget, title: str = "") -> None:
        """Add a panel to the sidebar.

        Args:
            panel_id: Unique identifier for this panel
            widget: Widget to display in panel
            title: Panel title to show in header

        Example:
            >>> from PySide6.QtWidgets import QTextEdit
            >>> explorer = QTextEdit()
            >>> window.add_sidebar_panel("explorer", explorer, "Explorer")
        """
        if self._sidebar:
            self._sidebar.add_panel(panel_id, widget, title)

    def remove_sidebar_panel(self, panel_id: str) -> None:
        """Remove a panel from the sidebar.

        Args:
            panel_id: ID of panel to remove
        """
        if self._sidebar:
            self._sidebar.remove_panel(panel_id)

    def show_sidebar_panel(self, panel_id: str) -> None:
        """Switch to specified sidebar panel.

        Args:
            panel_id: ID of panel to show
        """
        if self._sidebar:
            self._sidebar.show_panel(panel_id)

    def get_sidebar_panel(self, panel_id: str) -> Optional[QWidget]:
        """Get sidebar panel widget by ID.

        Args:
            panel_id: ID of panel to get

        Returns:
            Panel widget, or None if not found
        """
        if self._sidebar:
            return self._sidebar.get_panel(panel_id)
        return None

    def toggle_sidebar(self) -> None:
        """Toggle sidebar visibility."""
        if self._sidebar:
            self._sidebar.toggle_visibility()

    def set_sidebar_visible(self, visible: bool, animated: bool = True) -> None:
        """Show/hide sidebar.

        Args:
            visible: True to show, False to hide
            animated: True to animate the transition (default)
        """
        if self._sidebar:
            self._sidebar.set_visible(visible, animated=animated)

    def is_sidebar_visible(self) -> bool:
        """Check if sidebar is visible.

        Returns:
            True if visible, False otherwise
        """
        if self._sidebar:
            return bool(self._sidebar.isVisible())
        return False

    def _on_sidebar_panel_changed(self, panel_id: str) -> None:
        """Handle sidebar panel change.

        Args:
            panel_id: ID of new panel
        """
        # Emit public signal
        self.sidebar_panel_changed.emit(panel_id)

    def _on_sidebar_visibility_changed(self, is_visible: bool) -> None:
        """Handle sidebar visibility change.

        Args:
            is_visible: True if visible, False otherwise
        """
        # Emit public signal
        self.sidebar_visibility_changed.emit(is_visible)

    # Auxiliary Bar API
    def set_auxiliary_content(self, widget: QWidget) -> None:
        """Set the auxiliary bar content widget.

        Args:
            widget: Widget to display in auxiliary bar

        Example:
            >>> from PySide6.QtWidgets import QTextEdit
            >>> debug_console = QTextEdit()
            >>> window.set_auxiliary_content(debug_console)
        """
        if self._auxiliary_bar:
            self._auxiliary_bar.set_content(widget)

    def get_auxiliary_content(self) -> Optional[QWidget]:
        """Get the auxiliary bar content widget.

        Returns:
            Content widget, or None if not set
        """
        if self._auxiliary_bar:
            return self._auxiliary_bar.get_content()
        return None

    def toggle_auxiliary_bar(self) -> None:
        """Toggle auxiliary bar visibility."""
        if self._auxiliary_bar:
            self._auxiliary_bar.toggle_visibility()

    def set_auxiliary_bar_visible(self, visible: bool, animated: bool = True) -> None:
        """Show/hide auxiliary bar.

        Args:
            visible: True to show, False to hide
            animated: True to animate the transition (default)
        """
        if self._auxiliary_bar:
            self._auxiliary_bar.set_visible(visible, animated=animated)

    def is_auxiliary_bar_visible(self) -> bool:
        """Check if auxiliary bar is visible.

        Returns:
            True if visible, False otherwise
        """
        if self._auxiliary_bar:
            return bool(self._auxiliary_bar.isVisible())
        return False

    def _on_auxiliary_bar_visibility_changed(self, is_visible: bool) -> None:
        """Handle auxiliary bar visibility change.

        Args:
            is_visible: True if visible, False otherwise
        """
        # Emit public signal
        self.auxiliary_bar_visibility_changed.emit(is_visible)

    # Menu Bar API
    def set_menu_bar(self, menubar: QMenuBar) -> None:
        """Set the menu bar.

        In frameless mode, the menu bar is added to the title bar.
        In embedded mode, the menu bar is stored and can be accessed via get_menu_bar().

        Args:
            menubar: QMenuBar widget to set

        Example:
            >>> from PySide6.QtWidgets import QMenuBar
            >>> menubar = QMenuBar()
            >>> file_menu = menubar.addMenu("File")
            >>> file_menu.addAction("New", lambda: print("New file"))
            >>> file_menu.addAction("Open", lambda: print("Open file"))
            >>> window.set_menu_bar(menubar)
        """
        self._menu_bar = menubar

        if self._window_mode == WindowMode.Frameless:
            # Add to title bar
            if self._title_bar and hasattr(self._title_bar, "set_menu_bar"):
                self._title_bar.set_menu_bar(menubar)
        # In embedded mode, developer can access via get_menu_bar() and place it themselves

    def get_menu_bar(self) -> Optional[QMenuBar]:
        """Get the menu bar widget.

        Returns:
            The menu bar widget, or None if not set

        Example:
            >>> menubar = window.get_menu_bar()
            >>> if menubar:
            ...     menubar.addMenu("Edit")
        """
        return self._menu_bar

    # Keyboard Shortcut API
    def set_shortcut(self, action_name: str, key_sequence: str) -> None:
        """Set or update a keyboard shortcut.

        Args:
            action_name: Action identifier (e.g., "TOGGLE_SIDEBAR")
            key_sequence: Qt key sequence string (e.g., "Ctrl+Shift+B")

        Example:
            >>> window.set_shortcut("TOGGLE_SIDEBAR", "Ctrl+Shift+B")
        """
        self._shortcut_manager.update_shortcut_key(action_name, key_sequence)

    def register_custom_shortcut(
        self,
        action_name: str,
        key_sequence: str,
        callback: Callable[[], None],
        description: str = "",
    ) -> None:
        """Register a custom keyboard shortcut.

        Args:
            action_name: Unique action identifier
            key_sequence: Qt key sequence string (e.g., "Ctrl+K")
            callback: Function to call when shortcut is triggered
            description: Human-readable description

        Example:
            >>> def my_action():
            ...     print("Custom action triggered")
            >>> window.register_custom_shortcut(
            ...     "MY_CUSTOM_ACTION", "Ctrl+K", my_action, "My custom action"
            ... )
        """
        from .core.shortcuts import ShortcutDefinition

        shortcut_def = ShortcutDefinition(
            key_sequence=key_sequence, description=description, category="custom"
        )
        self._shortcut_manager.register_shortcut(action_name, shortcut_def, callback)

    def remove_shortcut(self, action_name: str) -> None:
        """Remove a keyboard shortcut.

        Args:
            action_name: Action identifier to remove

        Example:
            >>> window.remove_shortcut("TOGGLE_SIDEBAR")
        """
        self._shortcut_manager.unregister_shortcut(action_name)

    def enable_shortcut(self, action_name: str, enabled: bool = True) -> None:
        """Enable or disable a keyboard shortcut.

        Args:
            action_name: Action identifier
            enabled: True to enable, False to disable

        Example:
            >>> window.enable_shortcut("CLOSE_WINDOW", False)  # Disable Ctrl+W
        """
        self._shortcut_manager.set_shortcut_enabled(action_name, enabled)

    def get_shortcut_info(self, action_name: str) -> Optional[dict]:
        """Get information about a shortcut.

        Args:
            action_name: Action identifier

        Returns:
            Dictionary with shortcut info (key_sequence, description, category)
            or None if not found

        Example:
            >>> info = window.get_shortcut_info("TOGGLE_SIDEBAR")
            >>> print(info["key_sequence"])  # "Ctrl+B"
        """
        shortcut_def = self._shortcut_manager.get_shortcut_definition(action_name)
        if shortcut_def:
            return {
                "key_sequence": shortcut_def.key_sequence,
                "description": shortcut_def.description,
                "category": shortcut_def.category,
            }
        return None

    def get_all_shortcuts(self) -> dict:
        """Get all registered shortcuts.

        Returns:
            Dictionary mapping action names to shortcut info

        Example:
            >>> shortcuts = window.get_all_shortcuts()
            >>> for name, definition in shortcuts.items():
            ...     print(f"{name}: {definition.key_sequence}")
        """
        return self._shortcut_manager.get_all_shortcuts()

    # Focus management helpers (Task 1.22)
    def _focus_sidebar(self) -> None:
        """Set focus to current sidebar panel (internal)."""
        if self._sidebar and self._sidebar.isVisible():
            # Get current panel widget
            panel_widget = self._sidebar.get_current_panel_widget()
            if panel_widget:
                panel_widget.setFocus(Qt.FocusReason.ShortcutFocusReason)

    def _focus_main_pane(self) -> None:
        """Set focus to main pane content (internal)."""
        if self._main_pane:
            content_widget = self._main_pane.get_content()
            if content_widget:
                content_widget.setFocus(Qt.FocusReason.ShortcutFocusReason)

    def _toggle_fullscreen(self) -> None:
        """Toggle fullscreen mode (internal)."""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
