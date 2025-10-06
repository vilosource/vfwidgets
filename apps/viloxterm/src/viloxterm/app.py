"""ViloxTerm main application."""

import logging
from pathlib import Path

from PySide6.QtCore import QEvent, QObject
from PySide6.QtGui import QKeySequence

from chrome_tabbed_window import ChromeTabbedWindow
from vfwidgets_terminal import TerminalWidget, MultiSessionTerminalServer
from vfwidgets_multisplit import MultisplitWidget, SplitterStyle, WherePosition, Direction
from vfwidgets_keybinding import KeybindingManager, ActionDefinition

from .components import ThemeDialog, MenuButton, TerminalThemeDialog, TerminalPreferencesDialog
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

    def __init__(self):
        """Initialize ViloxTerm application."""
        # ChromeTabbedWindow as top-level (triggers frameless mode)
        super().__init__()

        # Create shared terminal server (memory efficient!)
        self.terminal_server = MultiSessionTerminalServer(port=0)
        self.terminal_server.start()
        logger.info(f"Terminal server started on port {self.terminal_server.port}")

        # Create terminal theme manager
        self.terminal_theme_manager = TerminalThemeManager()

        # Create terminal preferences manager
        self.terminal_preferences_manager = TerminalPreferencesManager()

        # Create terminal provider for MultisplitWidget
        self.terminal_provider = TerminalProvider(self.terminal_server)

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
        self.setWindowTitle("ViloxTerm")
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

        # Create initial tab
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

        # Insert menu button at the beginning (before minimize button)
        controls_layout.insertWidget(0, self.menu_button)

        # Update the fixed size to accommodate 4 buttons (46px each)
        self._window_controls.setFixedSize(184, 32)

        logger.info("Added menu button to window controls")

    def _setup_signals(self) -> None:
        """Set up signal connections."""
        # Handle tab close
        self.tabCloseRequested.connect(self._on_tab_close_requested)

        # Handle menu button theme action (other actions use keybindings directly)
        if hasattr(self, "menu_button"):
            self.menu_button.change_theme_requested.connect(self._show_theme_dialog)

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

    def _on_pane_added(self, pane_id: str) -> None:
        """Handle pane added signal - auto-focus new panes from splits.

        Args:
            pane_id: ID of newly added pane
        """
        # Only auto-focus if this pane was added from a split operation
        if self._splitting_in_progress:
            multisplit = self.currentWidget()
            if isinstance(multisplit, MultisplitWidget):
                # Focus the new pane
                multisplit.focus_pane(pane_id)

                # Use v0.2.0 widget lookup API to access terminal
                terminal = multisplit.get_widget(pane_id)
                if terminal and isinstance(terminal, TerminalWidget):
                    # Terminal is focused and ready for input
                    logger.debug(f"Auto-focused new terminal in pane: {pane_id}")

            self._splitting_in_progress = False

    def _on_focus_changed(self, old_pane_id: str, new_pane_id: str) -> None:
        """Handle focus changes - add visual indicators.

        Adds a subtle border to the focused terminal pane for better UX
        in multi-pane layouts.

        Args:
            old_pane_id: Pane that lost focus (empty string if none)
            new_pane_id: Pane that gained focus (empty string if none)
        """
        multisplit = self.currentWidget()
        if not isinstance(multisplit, MultisplitWidget):
            return

        # Clear old focus border
        if old_pane_id:
            old_widget = multisplit.get_widget(old_pane_id)
            if old_widget:
                old_widget.setStyleSheet("")

        # Add new focus border
        if new_pane_id:
            new_widget = multisplit.get_widget(new_pane_id)
            if new_widget:
                # Subtle blue border for focused pane
                # TODO: Make color theme-aware
                new_widget.setStyleSheet("border: 2px solid #0078d4")

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

        # Remove the pane (multiple panes exist)
        success = multisplit.remove_pane(focused_pane)

        if success:
            logger.info(f"Closed pane {focused_pane}")
        else:
            logger.warning(f"Failed to close pane {focused_pane}")

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

        Args:
            event: Close event
        """
        # Shutdown terminal server
        logger.info("Shutting down terminal server...")
        self.terminal_server.shutdown()
        logger.info("Terminal server shut down")

        # Accept close event
        super().closeEvent(event)
        event.accept()
