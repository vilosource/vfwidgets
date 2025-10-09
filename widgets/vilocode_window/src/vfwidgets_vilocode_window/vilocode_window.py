"""ViloCodeWindow - VS Code-style application window.

This module implements the main ViloCodeWindow widget.
"""

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPaintEvent
from PySide6.QtWidgets import QHBoxLayout, QLabel, QStatusBar, QVBoxLayout, QWidget

from .core.constants import WindowMode
from .core.shortcut_manager import ShortcutManager

# Check if theme system is available
try:
    from vfwidgets_theme import ThemedWidget

    THEME_AVAILABLE = True

    # Create base class with ThemedWidget mixin
    class _ViloCodeWindowBase(ThemedWidget, QWidget):
        """Base class with theme support."""

        pass

except ImportError:
    THEME_AVAILABLE = False

    # Fallback without theme support
    class _ViloCodeWindowBase(QWidget):
        """Base class without theme support."""

        pass


class ViloCodeWindow(_ViloCodeWindowBase):
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
        self._activity_bar = None
        self._sidebar = None
        self._main_pane = None
        self._auxiliary_bar = None
        self._status_bar = None
        self._menu_bar = None

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

    def _setup_ui(self) -> None:
        """Set up the user interface layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Title bar (frameless mode only)
        if self._window_mode == WindowMode.Frameless:
            from .components import TitleBar

            self._title_bar = TitleBar(self)
            main_layout.addWidget(self._title_bar)
        else:
            self._title_bar = None

        # Content layout (horizontal: activity + sidebar + main + auxiliary)
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Placeholder widgets (implement in Phase 2)
        activity_label = QLabel("Activity\nBar")
        activity_label.setFixedWidth(48)
        activity_label.setStyleSheet("background-color: #2c2c2c; color: #cccccc;")
        activity_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(activity_label)

        sidebar_label = QLabel("Sidebar")
        sidebar_label.setFixedWidth(250)
        sidebar_label.setStyleSheet("background-color: #252526; color: #cccccc;")
        sidebar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(sidebar_label)

        main_label = QLabel("Main Pane\n(Content Area)")
        main_label.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4;")
        main_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(main_label, 1)  # Stretch=1

        auxiliary_label = QLabel("Auxiliary")
        auxiliary_label.setFixedWidth(300)
        auxiliary_label.setStyleSheet("background-color: #252526; color: #cccccc;")
        auxiliary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        auxiliary_label.hide()  # Hidden by default
        content_layout.addWidget(auxiliary_label)

        main_layout.addLayout(content_layout, 1)  # Stretch=1

        # Status bar
        self._status_bar = QStatusBar(self)
        self._status_bar.setStyleSheet("background-color: #007acc; color: #ffffff;")
        self._status_bar.showMessage("Ready")
        main_layout.addWidget(self._status_bar)

        # Apply theme colors after all components are created
        self._apply_theme_colors()

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

        # Register callbacks for window shortcuts
        self._shortcut_manager.register_callback("CLOSE_WINDOW", self.close)
        self._shortcut_manager.register_callback("MINIMIZE_WINDOW", self.showMinimized)
        self._shortcut_manager.register_callback("MAXIMIZE_WINDOW", self._toggle_maximize)

        # Panel focus shortcuts will be implemented when real panels exist
        # For now, they're registered but have no callbacks

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
        self, action_name: str, key_sequence: str, callback: callable, description: str = ""
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

    # Placeholder methods (implemented in Phase 2)
    def toggle_sidebar(self) -> None:
        """Toggle sidebar visibility (placeholder for Phase 1)."""
        pass

    def toggle_auxiliary_bar(self) -> None:
        """Toggle auxiliary bar visibility (placeholder for Phase 1)."""
        pass
