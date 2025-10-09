"""ViloxTerm main application."""

import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QKeySequence

from chrome_tabbed_window import ChromeTabbedWindow
from vfwidgets_terminal import TerminalWidget, MultiSessionTerminalServer
from vfwidgets_multisplit import MultisplitWidget, SplitterStyle, WherePosition, Direction
from vfwidgets_keybinding import KeybindingManager, ActionDefinition

from .components import (
    ThemeDialog,
    MenuButton,
    TerminalThemeDialog,
    TerminalPreferencesDialog,
    AboutDialog,
)
from .providers import TerminalProvider
from .terminal_theme_manager import TerminalThemeManager
from .terminal_preferences_manager import TerminalPreferencesManager

logger = logging.getLogger(__name__)


class ViloxTermApp(ChromeTabbedWindow):
    """ViloxTerm application - Chrome-style terminal emulator.

    Uses ChromeTabbedWindow as the top-level frameless window with
    MultisplitWidget in each tab containing TerminalWidget instances.
    Shares a single MultiSessionTerminalServer for memory efficiency.

    Architecture:
        ChromeTabbedWindow (Frameless)
        └─ Tab Content (per tab)
           └─ MultisplitWidget
              └─ TerminalWidget(s) in splittable panes
    """

    # Class-level window ID counter for unique window identification
    _window_id_counter = 0

    def __init__(self, shared_server=None, create_initial_tab=True):
        """Initialize ViloxTerm application.

        Args:
            shared_server: Optional MultiSessionTerminalServer to share between windows.
                          If None, creates a new server (first window).
            create_initial_tab: Whether to create an initial "Terminal 1" tab.
                               Set to False when detaching tabs to avoid creating unwanted tabs.
                               Defaults to True for normal window creation.
        """
        # ChromeTabbedWindow as top-level (triggers frameless mode)
        super().__init__()

        # Assign unique window ID and increment counter
        ViloxTermApp._window_id_counter += 1
        self._window_id = ViloxTermApp._window_id_counter

        # Track child windows (prevent garbage collection)
        self._child_windows = []

        # Track parent window (None for main window, set by parent for child windows)
        self._parent_window = None

        # Create or use shared terminal server
        if shared_server:
            # Share server with other windows
            self.terminal_server = shared_server
            self._owns_server = False
            logger.info("Using shared terminal server")
        else:
            # Create own server (first window)
            self.terminal_server = MultiSessionTerminalServer(port=0)
            self.terminal_server.start()
            self._owns_server = True
            logger.info(f"Created terminal server on port {self.terminal_server.port}")

        # Create terminal theme manager
        self.terminal_theme_manager = TerminalThemeManager()

        # Create terminal preferences manager
        self.terminal_preferences_manager = TerminalPreferencesManager()

        # Create terminal provider for MultisplitWidget
        self.terminal_provider = TerminalProvider(self.terminal_server, event_filter=self)

        # Apply default terminal theme to new terminals
        default_theme = self.terminal_theme_manager.get_default_theme()
        self.terminal_provider.set_default_theme(default_theme)
        logger.info(f"Applied default terminal theme: {default_theme.get('name', 'unknown')}")

        # Apply default terminal preferences to new terminals
        default_preferences = self.terminal_preferences_manager.load_preferences()
        self.terminal_provider.set_default_config(default_preferences)
        logger.info("Applied default terminal preferences")

        # Track when we're performing a split (to auto-focus new pane)
        self._splitting_in_progress = False

        # Track tab counter for proper tab naming
        self._tab_counter = 1

        # Customize window after parent init
        self.setWindowTitle(f"ViloxTerm - Window {self._window_id}")
        self.resize(1200, 800)
        self.setTabsClosable(True)

        # Note: ChromeTabbedWindow has a built-in "+" button
        # We override _on_new_tab_requested() to handle it

        # Set up keyboard shortcuts FIRST (so actions are available for menu)
        self._setup_keybinding_manager()

        # Set up window controls (must be after parent __init__ and keybindings)
        self._setup_window_controls()

        # Set up signals (after window controls exist)
        self._setup_signals()

        # Create initial tab (unless caller explicitly requests not to)
        if create_initial_tab:
            self.add_new_terminal_tab("Terminal 1")

    def _setup_window_controls(self) -> None:
        """Set up custom window controls with menu button.

        Adds a menu button to the window controls for theme selection.
        ChromeTabbedWindow already creates WindowControls in frameless mode,
        so we need to modify the existing layout.
        """
        # Debug: Check window mode
        logger.info(
            f"Window mode: {self._window_mode}, Has controls: {hasattr(self, '_window_controls')}"
        )

        # Check if we have window controls (only in frameless mode)
        if not hasattr(self, "_window_controls") or not self._window_controls:
            logger.warning(
                f"No window controls found - parent={self.parent()}, window_mode={self._window_mode}"
            )
            return

        # Get the existing window controls layout
        controls_layout = self._window_controls.layout()
        if not controls_layout:
            logger.warning("Window controls have no layout")
            return

        # Create menu button with keybinding actions
        self.menu_button = MenuButton(self._window_controls, keybinding_actions=self.actions)

        # Connect menu button to app for dynamic menu updates
        self.menu_button.set_parent_app(self)

        # Insert menu button at the beginning (before minimize button)
        controls_layout.insertWidget(0, self.menu_button)

        # Update the fixed size to accommodate 4 buttons (46px each)
        self._window_controls.setFixedSize(184, 32)

        logger.info("Added menu button to window controls")

    def _setup_signals(self) -> None:
        """Set up signal connections."""
        # Handle tab close
        self.tabCloseRequested.connect(self._on_tab_close_requested)

        # Handle tab detachment
        self.tabDetachRequested.connect(self._detach_tab_to_window)

        # Note: Tab migration to existing window is handled directly in
        # _customize_tab_context_menu() via action.triggered connections

        # Handle menu button actions (other actions use keybindings directly)
        if hasattr(self, "menu_button"):
            self.menu_button.change_theme_requested.connect(self._show_theme_dialog)
            self.menu_button.new_window_requested.connect(self._open_new_window)
            self.menu_button.about_requested.connect(self._show_about_dialog)

        # Handle terminal session ending (auto-close panes when terminal exits)
        # Use QueuedConnection for cross-thread signal (Flask-SocketIO thread -> Qt main thread)
        self.terminal_server.session_ended.connect(
            self._on_session_ended, Qt.ConnectionType.QueuedConnection
        )

    def _setup_keybinding_manager(self) -> None:
        """Set up keyboard shortcut manager with user-customizable bindings."""
        # Define storage location
        storage_path = Path.home() / ".config" / "viloxterm" / "keybindings.json"

        # Create manager with persistence and auto-save
        self.keybinding_manager = KeybindingManager(storage_path=str(storage_path), auto_save=True)

        # Register all actions with callbacks
        self.keybinding_manager.register_actions(
            [
                ActionDefinition(
                    id="pane.split_horizontal",
                    description="Split Horizontal",
                    default_shortcut="Ctrl+Shift+H",  # H = Horizontal divider = top/bottom split
                    category="Pane",
                    callback=self._on_split_horizontal,
                ),
                ActionDefinition(
                    id="pane.split_vertical",
                    description="Split Vertical",
                    default_shortcut="Ctrl+Shift+V",  # V = Vertical divider = left/right split
                    category="Pane",
                    callback=self._on_split_vertical,
                ),
                ActionDefinition(
                    id="pane.close",
                    description="Close Pane",
                    default_shortcut="Ctrl+W",
                    category="Pane",
                    callback=self._on_close_pane,
                ),
                # Pane Navigation
                ActionDefinition(
                    id="pane.navigate_left",
                    description="Navigate Left",
                    default_shortcut="Ctrl+Shift+Left",
                    category="Pane",
                    callback=lambda: self._on_navigate_pane(Direction.LEFT),
                ),
                ActionDefinition(
                    id="pane.navigate_right",
                    description="Navigate Right",
                    default_shortcut="Ctrl+Shift+Right",
                    category="Pane",
                    callback=lambda: self._on_navigate_pane(Direction.RIGHT),
                ),
                ActionDefinition(
                    id="pane.navigate_up",
                    description="Navigate Up",
                    default_shortcut="Ctrl+Shift+Up",
                    category="Pane",
                    callback=lambda: self._on_navigate_pane(Direction.UP),
                ),
                ActionDefinition(
                    id="pane.navigate_down",
                    description="Navigate Down",
                    default_shortcut="Ctrl+Shift+Down",
                    category="Pane",
                    callback=lambda: self._on_navigate_pane(Direction.DOWN),
                ),
                ActionDefinition(
                    id="tab.close",
                    description="Close Tab",
                    default_shortcut="Ctrl+Shift+W",
                    category="Tab",
                    callback=self._on_close_tab,
                ),
                # Tab Navigation
                ActionDefinition(
                    id="tab.new",
                    description="New Tab",
                    default_shortcut="Ctrl+Shift+T",
                    category="Tab",
                    callback=self._on_new_tab,
                ),
                ActionDefinition(
                    id="tab.next",
                    description="Next Tab",
                    default_shortcut="Ctrl+PgDown",
                    category="Tab",
                    callback=self._on_next_tab,
                ),
                ActionDefinition(
                    id="tab.previous",
                    description="Previous Tab",
                    default_shortcut="Ctrl+PgUp",
                    category="Tab",
                    callback=self._on_previous_tab,
                ),
                # Quick jump to tabs 1-9
                ActionDefinition(
                    id="tab.jump_1",
                    description="Jump to Tab 1",
                    default_shortcut="Alt+1",
                    category="Tab",
                    callback=lambda: self._on_jump_to_tab(1),
                ),
                ActionDefinition(
                    id="tab.jump_2",
                    description="Jump to Tab 2",
                    default_shortcut="Alt+2",
                    category="Tab",
                    callback=lambda: self._on_jump_to_tab(2),
                ),
                ActionDefinition(
                    id="tab.jump_3",
                    description="Jump to Tab 3",
                    default_shortcut="Alt+3",
                    category="Tab",
                    callback=lambda: self._on_jump_to_tab(3),
                ),
                ActionDefinition(
                    id="tab.jump_4",
                    description="Jump to Tab 4",
                    default_shortcut="Alt+4",
                    category="Tab",
                    callback=lambda: self._on_jump_to_tab(4),
                ),
                ActionDefinition(
                    id="tab.jump_5",
                    description="Jump to Tab 5",
                    default_shortcut="Alt+5",
                    category="Tab",
                    callback=lambda: self._on_jump_to_tab(5),
                ),
                ActionDefinition(
                    id="tab.jump_6",
                    description="Jump to Tab 6",
                    default_shortcut="Alt+6",
                    category="Tab",
                    callback=lambda: self._on_jump_to_tab(6),
                ),
                ActionDefinition(
                    id="tab.jump_7",
                    description="Jump to Tab 7",
                    default_shortcut="Alt+7",
                    category="Tab",
                    callback=lambda: self._on_jump_to_tab(7),
                ),
                ActionDefinition(
                    id="tab.jump_8",
                    description="Jump to Tab 8",
                    default_shortcut="Alt+8",
                    category="Tab",
                    callback=lambda: self._on_jump_to_tab(8),
                ),
                ActionDefinition(
                    id="tab.jump_9",
                    description="Jump to Tab 9",
                    default_shortcut="Alt+9",
                    category="Tab",
                    callback=lambda: self._on_jump_to_tab(9),
                ),
                # Appearance
                ActionDefinition(
                    id="appearance.terminal_theme",
                    description="Terminal Colors & Fonts",
                    default_shortcut="Ctrl+Shift+,",
                    category="Appearance",
                    callback=self._show_terminal_theme_dialog,
                ),
                ActionDefinition(
                    id="appearance.terminal_preferences",
                    description="Terminal Preferences",
                    default_shortcut="Ctrl+,",
                    category="Appearance",
                    callback=self._show_terminal_preferences_dialog,
                ),
                ActionDefinition(
                    id="appearance.reset_zoom",
                    description="Reset Terminal Zoom",
                    default_shortcut="Ctrl+0",
                    category="Appearance",
                    callback=self._on_reset_zoom,
                ),
            ]
        )

        # Load saved keybindings (or use defaults)
        self.keybinding_manager.load_bindings()

        # Apply shortcuts to window
        self.actions = self.keybinding_manager.apply_shortcuts(self)

        logger.info("Set up keyboard shortcuts with KeybindingManager")

        # Install event filter to intercept shortcuts before they reach terminal
        self.installEventFilter(self)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """Intercept keyboard events to handle application shortcuts.

        This ensures shortcuts like Ctrl+PgDn work even when the terminal
        (QWebEngineView) has focus, which would normally capture these keys.
        """
        if event.type() == QEvent.Type.KeyPress:
            key_event = event

            # Debug: Log the key event details
            key_name = QKeySequence(key_event.key()).toString()
            modifiers = key_event.modifiers()
            logger.debug(
                f"Key event: key={key_name} (0x{key_event.key():x}), "
                f"modifiers={modifiers}, text='{key_event.text()}'"
            )

            # Check if this matches any of our registered shortcuts
            # Note: modifiers() returns KeyboardModifier enum, use .value to get int
            key_sequence = QKeySequence(int(modifiers.value) | int(key_event.key()))
            logger.debug(f"Checking sequence: {key_sequence.toString()}")

            # Check all registered actions
            for action_id, action in self.actions.items():
                if action.shortcut().matches(key_sequence) == QKeySequence.SequenceMatch.ExactMatch:
                    # Trigger the action and consume the event
                    logger.info(
                        f"✅ Intercepted shortcut: {action.shortcut().toString()} for {action_id}"
                    )
                    action.trigger()
                    return True  # Event handled, don't propagate

        return super().eventFilter(obj, event)

    def add_new_terminal_tab(self, title: str = "Terminal") -> None:
        """Create a new tab with MultisplitWidget containing terminals.

        Each tab contains a MultisplitWidget that can dynamically split
        into multiple terminal panes.

        Uses Qt best practice: add tab in background, wait for terminal
        to be ready, then switch to it. This eliminates transparency flash.

        Args:
            title: Tab title
        """
        # Store current index to maintain user context
        current_index = self.currentIndex()

        # Create MultisplitWidget with provider and custom dark splitter style
        # Use minimal 1px borders with dark colors to match terminal theme
        dark_splitter_style = SplitterStyle(
            handle_width=1,
            handle_margin_horizontal=0,
            handle_margin_vertical=0,
            handle_bg="#3a3a3a",  # Dark gray for dividers
            handle_hover_bg="#505050",  # Slightly lighter on hover
            border_width=0,
            show_hover_effect=True,
            cursor_on_hover=True,
            hit_area_padding=3,  # 3px padding on each side for easier grabbing (7px total hit area)
        )
        multisplit = MultisplitWidget(
            provider=self.terminal_provider, splitter_style=dark_splitter_style
        )

        # Install event filter to intercept keyboard shortcuts
        # This must be done BEFORE the terminal widgets are created
        multisplit.installEventFilter(self)

        # Set dark background for MultisplitWidget container to match terminal theme
        multisplit.setStyleSheet("background-color: #1e1e1e;")

        # Connect to pane_added signal for auto-focus on split
        multisplit.pane_added.connect(self._on_pane_added)

        # Connect to focus_changed signal for visual indicators (v0.2.0)
        multisplit.focus_changed.connect(self._on_focus_changed)

        # Add tab in BACKGROUND (don't switch yet)
        index = self.addTab(multisplit, title)

        # Wait for initial terminal to be ready before switching
        # This is the Qt best practice: prepare widgets before showing them
        self._wait_for_terminal_ready(multisplit, index, current_index)

        logger.info(f"Created new tab: {title} at index {index} (waiting for terminal ready)")

    def _wait_for_terminal_ready(
        self, multisplit: MultisplitWidget, tab_index: int, previous_index: int
    ) -> None:
        """Wait for initial terminal to be ready, then switch to the tab.

        Qt best practice: Don't show widgets until they're fully initialized.
        This eliminates the transparency flash by keeping the tab in the
        background until the WebView has loaded and the terminal is ready.

        Args:
            multisplit: The MultisplitWidget in the new tab
            tab_index: Index of the newly created tab
            previous_index: Index of the previously active tab
        """
        from vfwidgets_terminal import TerminalWidget

        def connect_to_terminal_ready(terminal: TerminalWidget):
            """Connect to terminal ready signal and switch tabs when ready."""

            def on_ready():
                logger.info(f"Terminal ready, switching to tab {tab_index}")
                self.setCurrentIndex(tab_index)
                # Disconnect after first use
                try:
                    terminal.terminalReady.disconnect(on_ready)
                except RuntimeError:
                    pass  # Already disconnected

            terminal.terminalReady.connect(on_ready)
            # Connect shortcut handling
            terminal.shortcutPressed.connect(self._on_terminal_shortcut)
            logger.debug(f"Connected to terminalReady signal, waiting for terminal to be ready")

        # Check if initial pane already exists (it's created during __init__)
        initial_pane_id = multisplit.get_focused_pane()
        if initial_pane_id:
            # Pane already exists, get the widget
            terminal = multisplit.get_widget(initial_pane_id)
            if isinstance(terminal, TerminalWidget):
                logger.debug(f"Initial pane {initial_pane_id} already exists")
                connect_to_terminal_ready(terminal)
            else:
                # Not a terminal widget yet, wait for it to be created
                logger.debug(f"Pane exists but widget not ready, waiting for pane_added")

                def on_pane_added(pane_id: str):
                    """Handle pane_added signal."""
                    widget = multisplit.get_widget(pane_id)
                    if isinstance(widget, TerminalWidget):
                        connect_to_terminal_ready(widget)
                        try:
                            multisplit.pane_added.disconnect(on_pane_added)
                        except RuntimeError:
                            pass

                multisplit.pane_added.connect(on_pane_added)
        else:
            # No pane yet, wait for pane_added signal
            logger.debug(f"No initial pane yet, waiting for pane_added signal")

            def on_pane_added(pane_id: str):
                """Handle pane_added signal."""
                terminal = multisplit.get_widget(pane_id)
                if isinstance(terminal, TerminalWidget):
                    connect_to_terminal_ready(terminal)
                    try:
                        multisplit.pane_added.disconnect(on_pane_added)
                    except RuntimeError:
                        pass
                else:
                    logger.warning("Widget is not a TerminalWidget")
                    self.setCurrentIndex(tab_index)

            multisplit.pane_added.connect(on_pane_added)

    def _show_theme_dialog(self) -> None:
        """Show application theme selection dialog."""
        dialog = ThemeDialog(self)
        dialog.exec()
        logger.info("Application theme dialog closed")

    def _show_about_dialog(self) -> None:
        """Show About ViloxTerm dialog."""
        dialog = AboutDialog(self)
        dialog.exec()
        logger.info("About dialog closed")

    def _show_terminal_theme_dialog(self) -> None:
        """Show terminal theme customization dialog."""
        dialog = TerminalThemeDialog(self.terminal_theme_manager, self)
        dialog.themeApplied.connect(self._apply_terminal_theme_to_all)
        dialog.exec()
        logger.info("Terminal theme dialog closed")

    def _show_terminal_preferences_dialog(self) -> None:
        """Show terminal preferences dialog."""
        current_config = self.terminal_preferences_manager.load_preferences()
        dialog = TerminalPreferencesDialog(current_config, self)
        dialog.preferencesApplied.connect(self._apply_terminal_preferences_to_all)
        dialog.exec()
        logger.info("Terminal preferences dialog closed")

    def _on_reset_zoom(self) -> None:
        """Reset zoom to 100% on the currently focused terminal.

        Triggered by Ctrl+0 shortcut or menu item.
        Useful for undoing accidental zoom changes from Ctrl+scroll.
        """
        multisplit = self.currentWidget()
        if not isinstance(multisplit, MultisplitWidget):
            logger.warning("No MultisplitWidget found - cannot reset zoom")
            return

        # Get currently focused pane
        focused_pane_id = multisplit.get_focused_pane()
        if not focused_pane_id:
            logger.warning("No focused pane - cannot reset zoom")
            return

        # Get terminal widget in focused pane
        terminal = multisplit.get_widget(focused_pane_id)
        if terminal and isinstance(terminal, TerminalWidget):
            terminal.reset_zoom()
            logger.info(f"Reset zoom to 100% for terminal in pane {focused_pane_id[:8]}")
        else:
            logger.warning(f"Widget in pane {focused_pane_id[:8]} is not a TerminalWidget")

    def _open_new_window(self) -> None:
        """Open a new ViloxTerm window.

        Creates a new window instance that shares the same terminal server
        for memory efficiency. The new window is tracked to prevent garbage
        collection.
        """
        logger.info("Opening new ViloxTerm window")

        # Create new window with shared server
        new_window = ViloxTermApp(shared_server=self.terminal_server)

        # Set parent window reference
        new_window._parent_window = self

        # Track window to prevent garbage collection
        self._child_windows.append(new_window)

        # Handle cleanup when child window closes
        new_window.destroyed.connect(lambda: self._on_child_window_closed(new_window))

        # Show the window
        new_window.show()

        logger.info(f"New window created. Total windows: {len(self._child_windows) + 1}")

    def _on_child_window_closed(self, window) -> None:
        """Handle cleanup when a child window closes.

        Args:
            window: The ViloxTermApp instance that was closed
        """
        if window in self._child_windows:
            self._child_windows.remove(window)
            logger.info(f"Child window closed. Remaining windows: {len(self._child_windows) + 1}")

    def _customize_tab_context_menu(self, menu, tab_index: int) -> None:
        """Add multi-window menu items to tab context menu.

        Adds "Move to Window >" submenu with list of available target windows.

        Args:
            menu: QMenu to add items to
            tab_index: Index of the tab being right-clicked
        """
        # Get available target windows
        target_windows = self.get_available_target_windows()

        if target_windows:
            # Create submenu with available windows
            move_submenu = menu.addMenu("Move to Window")

            # Populate with window titles and connect actions
            for window_title, window_ref in target_windows:
                action = move_submenu.addAction(window_title)
                # Use lambda with default argument to capture current values
                action.triggered.connect(
                    lambda checked=False, idx=tab_index, win=window_ref: self._move_tab_to_window(
                        idx, win
                    )
                )
        else:
            # No other windows available - add disabled action
            no_windows_action = menu.addAction("Move to Window")
            no_windows_action.setEnabled(False)

    def get_available_target_windows(self) -> list:
        """Get list of available target windows for tab migration.

        Returns list of (window_title, window_ref) tuples for all windows
        except the current window.

        Returns:
            List of (str, ViloxTermApp) tuples, empty if no other windows available
        """
        # Find the main window (has _parent_window = None)
        if self._parent_window is None:
            # We are the main window
            main_window = self
        else:
            # We are a child window, traverse to main
            main_window = self._parent_window

        # Collect all windows: main + all children
        all_windows = [main_window] + main_window._child_windows

        # Filter out current window and build result list
        target_windows = [
            (window.windowTitle(), window) for window in all_windows if window != self
        ]

        return target_windows

    def _detach_tab_to_window(self, index: int) -> None:
        """Detach a tab to a new window.

        Called when user right-clicks "Move to New Window" or drags tab vertically.

        Args:
            index: Tab index to detach
        """
        logger.info(f"Detaching tab {index} to new window")

        # Get tab data before removing
        tab_data = self.get_tab_data(index)
        if not tab_data:
            logger.warning(f"Cannot detach tab {index}: invalid index")
            return

        # Handle last tab case: create a replacement tab first
        if self.count() == 1:
            logger.info("Detaching last tab - creating replacement tab first")
            # Create new terminal tab before removing the last one
            self._on_new_tab()

        # Remove tab from this window (transfers ownership)
        # CRITICAL: Must removeTab before addTab (widget can only have one parent)
        self.removeTab(index)
        logger.info(f"Removed tab {index} from source window")

        # Create new window with shared server (no initial tab - we're adding the detached tab)
        new_window = ViloxTermApp(shared_server=self.terminal_server, create_initial_tab=False)

        # Add tab to new window
        new_window.addTab(tab_data["widget"], tab_data["text"])
        if not tab_data["icon"].isNull():
            new_window.setTabIcon(0, tab_data["icon"])
        if tab_data["tooltip"]:
            new_window.setTabToolTip(0, tab_data["tooltip"])

        # Set parent window reference
        new_window._parent_window = self

        # Track window to prevent garbage collection
        self._child_windows.append(new_window)

        # Handle cleanup when child window closes
        new_window.destroyed.connect(lambda: self._on_child_window_closed(new_window))

        # Show the new window
        new_window.show()

        logger.info(f"Tab detached to new window. Total windows: {len(self._child_windows) + 1}")

    def _move_tab_to_window(self, source_index: int, target_window) -> None:
        """Move a tab to an existing window.

        Called when user selects "Move to Window > Window X" from context menu.

        Args:
            source_index: Tab index to move from this window
            target_window: ViloxTermApp instance to move tab to
        """
        logger.info(f"Moving tab {source_index} to window {target_window.windowTitle()}")

        # Get tab data before removing
        tab_data = self.get_tab_data(source_index)
        if not tab_data:
            logger.warning(f"Cannot move tab {source_index}: invalid index")
            return

        # Handle last tab case: create a replacement tab first
        if self.count() == 1:
            logger.info("Moving last tab - creating replacement tab first")
            # Create new terminal tab before removing the last one
            self._tab_counter += 1
            self.add_new_terminal_tab(f"Terminal {self._tab_counter}")

        # Remove tab from this window (transfers ownership)
        # CRITICAL: Must removeTab before addTab (widget can only have one parent)
        self.removeTab(source_index)
        logger.info(f"Removed tab {source_index} from source window")

        # Add tab to target window
        new_index = target_window.addTab(tab_data["widget"], tab_data["text"])
        if not tab_data["icon"].isNull():
            target_window.setTabIcon(new_index, tab_data["icon"])
        if tab_data["tooltip"]:
            target_window.setTabToolTip(new_index, tab_data["tooltip"])

        # Focus target window and new tab
        target_window.activateWindow()
        target_window.setCurrentIndex(new_index)

        logger.info(f"Tab moved to {target_window.windowTitle()}, new index: {new_index}")

    def _apply_terminal_theme_to_all(self, theme: dict) -> None:
        """Apply terminal theme to all existing terminals.

        Args:
            theme: Terminal theme dictionary
        """
        applied_count = 0

        # Iterate all tabs
        for tab_index in range(self.count()):
            multisplit = self.widget(tab_index)
            if not isinstance(multisplit, MultisplitWidget):
                continue

            # Get all panes in this tab
            pane_ids = multisplit.get_pane_ids()

            # Apply theme to each terminal widget
            for pane_id in pane_ids:
                widget = multisplit.get_widget(pane_id)
                if isinstance(widget, TerminalWidget):
                    widget.set_terminal_theme(theme)
                    applied_count += 1

        logger.info(f"Applied terminal theme to {applied_count} terminals")

        # Update terminal provider to use this theme for new terminals
        self.terminal_provider.set_default_theme(theme)

    def _apply_terminal_preferences_to_all(self, config: dict) -> None:
        """Apply terminal preferences to all existing terminals.

        Args:
            config: Terminal configuration dictionary
        """
        applied_count = 0

        # Iterate all tabs
        for tab_index in range(self.count()):
            multisplit = self.widget(tab_index)
            if not isinstance(multisplit, MultisplitWidget):
                continue

            # Get all panes in this tab
            pane_ids = multisplit.get_pane_ids()

            # Apply configuration to each terminal widget
            for pane_id in pane_ids:
                widget = multisplit.get_widget(pane_id)
                if isinstance(widget, TerminalWidget):
                    widget.set_terminal_config(config)
                    applied_count += 1

        logger.info(f"Applied terminal preferences to {applied_count} terminals")

        # Save preferences to disk
        self.terminal_preferences_manager.save_preferences(config)

        # Update terminal provider to use these preferences for new terminals
        self.terminal_provider.set_default_config(config)

    def _on_new_tab_requested(self) -> None:
        """Handle new tab request from ChromeTabbedWindow's built-in + button.

        Overrides ChromeTabbedWindow._on_new_tab_requested() to create
        terminal tabs instead of placeholder widgets.
        """
        self._tab_counter += 1
        logger.info(f"New tab button clicked, creating Terminal {self._tab_counter}")
        self.add_new_terminal_tab(f"Terminal {self._tab_counter}")

    def _on_tab_close_requested(self, index: int) -> None:
        """Handle tab close request.

        Args:
            index: Index of tab to close
        """
        if self.count() > 1:
            # Remove tab
            self.removeTab(index)
            logger.info(f"Closed tab at index {index}")
        else:
            # Last tab - close the window
            logger.info("Closing last tab - exiting application")
            self.close()

    def _get_next_focus_pane(
        self, multisplit: "MultisplitWidget", closing_pane_id: str
    ) -> Optional[str]:
        """Determine which pane should receive focus after closing a pane.

        Follows the "undo split" pattern - focuses the sibling pane that
        will remain after the closed pane's removal.

        Args:
            multisplit: MultisplitWidget containing the pane
            closing_pane_id: ID of pane being closed

        Returns:
            Pane ID to focus, or None if no panes will remain
        """
        # Import types at function level to avoid circular import
        from vfwidgets_multisplit.core.nodes import LeafNode
        from vfwidgets_multisplit.core.types import PaneId

        # Access internal model to traverse tree
        pane_node = multisplit._model.get_pane(PaneId(closing_pane_id))

        if not pane_node or not pane_node.parent:
            # No parent means it's the root/only pane
            return None

        parent = pane_node.parent

        # Find sibling pane in parent's children
        for child in parent.children:
            if isinstance(child, LeafNode):
                sibling_id = str(child.pane_id)
                if sibling_id != closing_pane_id:
                    return sibling_id

        # Fallback: return any other pane
        all_panes = multisplit.get_pane_ids()
        remaining = [pid for pid in all_panes if pid != closing_pane_id]
        return remaining[0] if remaining else None

    def _close_pane_with_auto_focus(
        self, multisplit: "MultisplitWidget", pane_id: str, reason: str = "unknown"
    ) -> bool:
        """Close a pane and automatically focus its sibling (undo split pattern).

        This is the single source of truth for pane closure with auto-focus,
        used by both manual close (Ctrl+W) and auto-close (terminal exit).

        Args:
            multisplit: MultisplitWidget containing the pane
            pane_id: ID of pane to close
            reason: Reason for closure (for logging)

        Returns:
            True if pane was successfully closed
        """
        logger.info(f"Closing pane {pane_id} (reason: {reason})")

        # Determine which pane to focus after removal
        next_focus_pane = self._get_next_focus_pane(multisplit, pane_id)
        logger.debug(f"Next focus pane after {reason}: {next_focus_pane}")

        # Remove the pane
        success = multisplit.remove_pane(pane_id)

        if success:
            logger.info(f"Successfully closed pane {pane_id}")

            # Auto-focus the sibling pane (mimics "undo split" behavior)
            if next_focus_pane:
                logger.info(f"Auto-focusing sibling pane: {next_focus_pane}")
                multisplit.focus_pane(next_focus_pane)
            else:
                logger.debug("No sibling pane to focus (last pane)")
        else:
            logger.warning(f"Failed to close pane {pane_id}")

        return success

    def _on_session_ended(self, session_id: str) -> None:
        """Handle terminal session ending (process exited).

        Automatically closes the pane associated with the session.
        If it's the last pane in a tab, closes the tab.
        If it's the last tab, closes the application.

        Args:
            session_id: Session ID that ended
        """
        logger.info(f"Terminal session ended: {session_id}")

        # Find which pane this session belongs to
        pane_id = self.terminal_provider.get_pane_for_session(session_id)
        if not pane_id:
            logger.warning(f"No pane found for session {session_id}")
            return

        # Find which tab contains this pane
        for tab_index in range(self.count()):
            multisplit = self.widget(tab_index)
            if not isinstance(multisplit, MultisplitWidget):
                continue

            # Check if this tab contains the pane
            if pane_id in multisplit.get_pane_ids():
                logger.info(f"Found pane {pane_id} in tab {tab_index}")

                # Check if this is the last pane in the tab
                pane_count = len(multisplit.get_pane_ids())

                if pane_count == 1:
                    # Last pane - close the entire tab
                    logger.info("Last pane in tab - closing tab")
                    self._on_tab_close_requested(tab_index)
                else:
                    # Multiple panes - use common helper for close + auto-focus
                    self._close_pane_with_auto_focus(multisplit, pane_id, reason="terminal exit")

                return

        logger.warning(f"Could not find pane {pane_id} in any tab")

    def _on_pane_added(self, pane_id: str) -> None:
        """Handle pane added signal - auto-focus new panes from splits.

        Args:
            pane_id: ID of newly added pane
        """
        multisplit = self.currentWidget()
        if isinstance(multisplit, MultisplitWidget):
            # Get the terminal widget
            terminal = multisplit.get_widget(pane_id)
            if terminal and isinstance(terminal, TerminalWidget):
                # ALWAYS connect shortcut handling for all terminals
                terminal.shortcutPressed.connect(self._on_terminal_shortcut)
                logger.debug(f"Connected shortcut handler for pane: {pane_id}")

            # Only auto-focus if this pane was added from a split operation
            if self._splitting_in_progress:
                # Focus the new pane
                multisplit.focus_pane(pane_id)
                if terminal and isinstance(terminal, TerminalWidget):
                    # Terminal is focused and ready for input
                    logger.debug(f"Auto-focused new terminal in pane: {pane_id}")

                self._splitting_in_progress = False

    def _on_focus_changed(self, old_pane_id: str, new_pane_id: str) -> None:
        """Handle focus changes with theme-aware backgrounds.

        CRITICAL: Margins are NEVER changed (always 3px). Only background color
        changes between focus/unfocus to prevent terminal resize and content shift.

        Args:
            old_pane_id: Pane that lost focus (empty string if none)
            new_pane_id: Pane that gained focus (empty string if none)
        """
        multisplit = self.currentWidget()
        if not isinstance(multisplit, MultisplitWidget):
            return

        # Get theme-aware focus color (existing logic)
        try:
            from vfwidgets_theme.core.tokens import ColorTokenRegistry
            from vfwidgets_theme.core.manager import ThemeManager

            theme_mgr = ThemeManager.get_instance()
            current_theme = theme_mgr.current_theme

            # Fallback chain: focusBorder -> input.focusBorder -> editor.selectionBackground
            try:
                focus_color = ColorTokenRegistry.get("focusBorder", current_theme)
            except (KeyError, AttributeError):
                try:
                    focus_color = ColorTokenRegistry.get("input.focusBorder", current_theme)
                except (KeyError, AttributeError):
                    try:
                        focus_color = ColorTokenRegistry.get(
                            "editor.selectionBackground", current_theme
                        )
                    except (KeyError, AttributeError):
                        # Final fallback based on theme type
                        focus_color = "#007ACC" if current_theme.type == "dark" else "#0078d4"
        except (ImportError, Exception):
            # Fallback if theme system not available (assume dark theme)
            focus_color = "#007ACC"

        # Get theme-aware unfocused color from terminal theme
        unfocused_color = "#1e1e1e"  # Fallback
        try:
            terminal_theme = self.terminal_theme_manager.get_default_theme()
            if "background" in terminal_theme:
                unfocused_color = terminal_theme["background"]
        except Exception:
            pass

        from PySide6.QtGui import QPalette, QColor

        # Clear old focus (change to unfocused color - blends with terminal)
        if old_pane_id:
            old_terminal = multisplit.get_widget(old_pane_id)
            if old_terminal and isinstance(old_terminal, TerminalWidget):
                # DO NOT change margins - keep at 3px
                # Only change background color to blend with terminal
                palette = old_terminal.palette()
                palette.setColor(QPalette.ColorRole.Window, QColor(unfocused_color))
                old_terminal.setPalette(palette)
                old_terminal.setAutoFillBackground(True)

        # Add new focus (change to focus color - visible border)
        if new_pane_id:
            new_terminal = multisplit.get_widget(new_pane_id)
            if new_terminal and isinstance(new_terminal, TerminalWidget):
                # DO NOT change margins - keep at 3px
                # Only change background color to focus color
                palette = new_terminal.palette()
                palette.setColor(QPalette.ColorRole.Window, QColor(focus_color))
                new_terminal.setPalette(palette)
                new_terminal.setAutoFillBackground(True)

        logger.debug(
            f"Focus changed: "
            f"{old_pane_id[:8] if old_pane_id else 'None'} -> "
            f"{new_pane_id[:8] if new_pane_id else 'None'}"
        )

    def _on_split_horizontal(self) -> None:
        """Handle horizontal split request (top/bottom panes).

        Creates a horizontal divider, splitting the pane into top and bottom.
        Triggered by Ctrl+Shift+H.
        """
        multisplit = self.currentWidget()
        if not isinstance(multisplit, MultisplitWidget):
            logger.warning("Current tab is not a MultisplitWidget")
            return

        focused_pane = multisplit.get_focused_pane()
        if not focused_pane:
            logger.warning("No focused pane to split")
            return

        # Create new terminal widget ID
        new_widget_id = f"terminal_{id(multisplit)}_{focused_pane}_bottom"

        # Mark split in progress for auto-focus
        self._splitting_in_progress = True

        # Split pane (BOTTOM = horizontal divider between top/bottom panes)
        success = multisplit.split_pane(
            focused_pane, new_widget_id, WherePosition.BOTTOM, ratio=0.5
        )

        if success:
            logger.info(f"Split pane {focused_pane} horizontally (top/bottom)")
        else:
            logger.warning(f"Failed to split pane {focused_pane}")
            self._splitting_in_progress = False

    def _on_split_vertical(self) -> None:
        """Handle vertical split request (left/right panes).

        Creates a vertical divider, splitting the pane into left and right.
        Triggered by Ctrl+Shift+V.
        """
        multisplit = self.currentWidget()
        if not isinstance(multisplit, MultisplitWidget):
            logger.warning("Current tab is not a MultisplitWidget")
            return

        focused_pane = multisplit.get_focused_pane()
        if not focused_pane:
            logger.warning("No focused pane to split")
            return

        # Create new terminal widget ID
        new_widget_id = f"terminal_{id(multisplit)}_{focused_pane}_right"

        # Mark split in progress for auto-focus
        self._splitting_in_progress = True

        # Split pane (RIGHT = vertical divider between left/right panes)
        success = multisplit.split_pane(focused_pane, new_widget_id, WherePosition.RIGHT, ratio=0.5)

        if success:
            logger.info(f"Split pane {focused_pane} vertically (left/right)")
        else:
            logger.warning(f"Failed to split pane {focused_pane}")
            self._splitting_in_progress = False

    def _on_close_pane(self) -> None:
        """Handle close pane request from menu.

        Closes the currently focused pane. If this is the last pane in the tab,
        closes the entire tab instead.
        """
        multisplit = self.currentWidget()
        if not isinstance(multisplit, MultisplitWidget):
            logger.warning("Current tab is not a MultisplitWidget")
            return

        focused_pane = multisplit.get_focused_pane()
        if not focused_pane:
            logger.warning("No focused pane to close")
            return

        # Check if this is the last pane in the tab
        pane_count = len(multisplit.get_pane_ids())

        if pane_count == 1:
            # Last pane - close the entire tab instead
            logger.info("Closing last pane - will close entire tab")
            current_index = self.currentIndex()
            self._on_tab_close_requested(current_index)
            return

        # Remove the pane (multiple panes exist) - use common helper for close + auto-focus
        self._close_pane_with_auto_focus(multisplit, focused_pane, reason="manual close")

    def _on_navigate_pane(self, direction: Direction) -> None:
        """Navigate focus to adjacent pane in the specified direction.

        Args:
            direction: Direction to navigate (LEFT, RIGHT, UP, DOWN)
        """
        multisplit = self.currentWidget()
        if not isinstance(multisplit, MultisplitWidget):
            logger.warning("Current tab is not a MultisplitWidget")
            return

        # Use MultisplitWidget's built-in navigation
        success = multisplit.navigate_focus(direction)

        if success:
            logger.debug(f"Navigated focus {direction.value}")
        else:
            logger.debug(f"No pane in {direction.value} direction")

    def _on_terminal_shortcut(self, action_id: str) -> None:
        """Handle shortcut pressed from terminal JavaScript."""
        logger.info(f"Terminal shortcut pressed: {action_id}")

        # Trigger the corresponding action
        if action_id in self.actions:
            self.actions[action_id].trigger()
        else:
            logger.warning(f"Unknown action ID from terminal: {action_id}")

    def _on_close_tab(self) -> None:
        """Handle close tab request from menu.

        Closes the currently active tab.
        """
        current_index = self.currentIndex()
        self._on_tab_close_requested(current_index)

    def _on_new_tab(self) -> None:
        """Handle new tab request from keyboard shortcut.

        Creates a new tab with auto-incremented name.
        """
        self._tab_counter += 1
        self.add_new_terminal_tab(f"Terminal {self._tab_counter}")
        logger.info(f"Created new tab via shortcut: Terminal {self._tab_counter}")

    def _on_next_tab(self) -> None:
        """Navigate to next tab with wrap-around.

        Moves to the next tab, wrapping around to first tab if at the end.
        """
        tab_count = self.count()
        if tab_count <= 1:
            return  # No other tabs to switch to

        current = self.currentIndex()
        next_index = (current + 1) % tab_count
        self.setCurrentIndex(next_index)
        logger.debug(f"Switched to next tab: {next_index}")

    def _on_previous_tab(self) -> None:
        """Navigate to previous tab with wrap-around.

        Moves to the previous tab, wrapping around to last tab if at the beginning.
        """
        tab_count = self.count()
        if tab_count <= 1:
            return  # No other tabs to switch to

        current = self.currentIndex()
        prev_index = (current - 1) % tab_count
        self.setCurrentIndex(prev_index)
        logger.debug(f"Switched to previous tab: {prev_index}")

    def _on_jump_to_tab(self, tab_number: int) -> None:
        """Jump to specific tab by number (1-9).

        Args:
            tab_number: Tab number (1-9, where 1 is first tab)
        """
        if not 1 <= tab_number <= 9:
            logger.warning(f"Invalid tab number: {tab_number}")
            return

        index = tab_number - 1  # Convert to 0-based index
        if index >= self.count():
            logger.debug(f"Tab {tab_number} does not exist (only {self.count()} tabs)")
            return

        self.setCurrentIndex(index)
        logger.debug(f"Jumped to tab {tab_number} (index {index})")

    def closeEvent(self, event) -> None:
        """Handle window close event.

        If this window owns the terminal server, shut it down.
        Otherwise, just close the window (server is shared).

        Args:
            event: Close event
        """
        logger.info("ViloxTerm window closing")

        # Only shutdown server if we own it
        if self._owns_server:
            logger.info("Shutting down terminal server (owner window closing)")
            self.terminal_server.shutdown()
            logger.info("Terminal server shut down")
        else:
            logger.info("Window closed (server owned by another window)")

        # Accept close event
        super().closeEvent(event)
        event.accept()
