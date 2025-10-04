"""ViloxTerm main application."""

import logging
from pathlib import Path

from chrome_tabbed_window import ChromeTabbedWindow
from vfwidgets_terminal import TerminalWidget, MultiSessionTerminalServer
from vfwidgets_multisplit import MultisplitWidget, SplitterStyle, WherePosition
from vfwidgets_keybinding import KeybindingManager, ActionDefinition

from .components import ThemeDialog, MenuButton
from .providers import TerminalProvider

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

        # Create terminal provider for MultisplitWidget
        self.terminal_provider = TerminalProvider(self.terminal_server)

        # Track when we're performing a split (to auto-focus new pane)
        self._splitting_in_progress = False

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
                    id="pane.split_vertical",
                    description="Split Vertical",
                    default_shortcut="Ctrl+Shift+V",
                    category="Pane",
                    callback=self._on_split_vertical,
                ),
                ActionDefinition(
                    id="pane.split_horizontal",
                    description="Split Horizontal",
                    default_shortcut="Ctrl+Shift+H",
                    category="Pane",
                    callback=self._on_split_horizontal,
                ),
                ActionDefinition(
                    id="pane.close",
                    description="Close Pane",
                    default_shortcut="Ctrl+W",
                    category="Pane",
                    callback=self._on_close_pane,
                ),
                ActionDefinition(
                    id="tab.close",
                    description="Close Tab",
                    default_shortcut="Ctrl+Shift+W",
                    category="Tab",
                    callback=self._on_close_tab,
                ),
            ]
        )

        # Load saved keybindings (or use defaults)
        self.keybinding_manager.load_bindings()

        # Apply shortcuts to window
        self.actions = self.keybinding_manager.apply_shortcuts(self)

        logger.info("Set up keyboard shortcuts with KeybindingManager")

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

        # Create MultisplitWidget with provider and minimal splitter style
        # Use minimal style (1px borders) for clean terminal appearance
        multisplit = MultisplitWidget(
            provider=self.terminal_provider, splitter_style=SplitterStyle.minimal()
        )

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

        # Get the initial terminal widget (created by initialize_empty)
        # MultisplitWidget creates the first pane with widget_id="default"
        initial_pane_id = multisplit.get_focused_pane()
        if not initial_pane_id:
            # Fallback: if no focused pane yet, wait for pane_added
            logger.warning("No initial pane found, waiting for pane_added signal")
            multisplit.pane_added.connect(
                lambda pane_id: self._on_initial_pane_ready(multisplit, tab_index, pane_id)
            )
            return

        terminal = multisplit.get_widget(initial_pane_id)
        if isinstance(terminal, TerminalWidget):
            # Connect to terminalReady signal (one-shot connection)
            def on_ready():
                logger.info(f"Terminal ready, switching to tab {tab_index}")
                self.setCurrentIndex(tab_index)
                # Disconnect after first use
                terminal.terminalReady.disconnect(on_ready)

            terminal.terminalReady.connect(on_ready)
            logger.debug(f"Waiting for terminal in pane {initial_pane_id} to be ready")
        else:
            # Not a terminal widget, switch immediately
            logger.warning("Widget is not a TerminalWidget, switching immediately")
            self.setCurrentIndex(tab_index)

    def _on_initial_pane_ready(
        self, multisplit: MultisplitWidget, tab_index: int, pane_id: str
    ) -> None:
        """Handle initial pane added (fallback case).

        Args:
            multisplit: The MultisplitWidget
            tab_index: Index of the tab
            pane_id: ID of the pane that was added
        """
        from vfwidgets_terminal import TerminalWidget

        terminal = multisplit.get_widget(pane_id)
        if isinstance(terminal, TerminalWidget):

            def on_ready():
                logger.info(f"Terminal ready (delayed), switching to tab {tab_index}")
                self.setCurrentIndex(tab_index)
                terminal.terminalReady.disconnect(on_ready)

            terminal.terminalReady.connect(on_ready)
            logger.debug(f"Connected to terminal ready signal for pane {pane_id}")
        else:
            # Not a terminal, switch immediately
            self.setCurrentIndex(tab_index)

    def _show_theme_dialog(self) -> None:
        """Show theme selection dialog."""
        dialog = ThemeDialog(self)
        dialog.exec()
        logger.info("Theme dialog closed")

    def _on_new_tab_requested(self) -> None:
        """Handle new tab request from ChromeTabbedWindow's built-in + button.

        Overrides ChromeTabbedWindow._on_new_tab_requested() to create
        terminal tabs instead of placeholder widgets.
        """
        tab_count = self.count()
        logger.info(f"New tab button clicked, current count: {tab_count}")
        self.add_new_terminal_tab(f"Terminal {tab_count + 1}")

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

    def _on_split_vertical(self) -> None:
        """Handle split vertical request from menu.

        Splits the focused pane vertically (creates horizontal divider).
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

        # Split pane (BOTTOM = vertical split with horizontal divider)
        success = multisplit.split_pane(
            focused_pane, new_widget_id, WherePosition.BOTTOM, ratio=0.5
        )

        if success:
            logger.info(f"Split pane {focused_pane} vertically")
        else:
            logger.warning(f"Failed to split pane {focused_pane}")
            self._splitting_in_progress = False

    def _on_split_horizontal(self) -> None:
        """Handle split horizontal request from menu.

        Splits the focused pane horizontally (creates vertical divider).
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

        # Split pane (RIGHT = horizontal split with vertical divider)
        success = multisplit.split_pane(focused_pane, new_widget_id, WherePosition.RIGHT, ratio=0.5)

        if success:
            logger.info(f"Split pane {focused_pane} horizontally")
        else:
            logger.warning(f"Failed to split pane {focused_pane}")
            self._splitting_in_progress = False

    def _on_close_pane(self) -> None:
        """Handle close pane request from menu.

        Closes the currently focused pane.
        """
        multisplit = self.currentWidget()
        if not isinstance(multisplit, MultisplitWidget):
            logger.warning("Current tab is not a MultisplitWidget")
            return

        focused_pane = multisplit.get_focused_pane()
        if not focused_pane:
            logger.warning("No focused pane to close")
            return

        # Remove the pane
        success = multisplit.remove_pane(focused_pane)

        if success:
            logger.info(f"Closed pane {focused_pane}")
        else:
            logger.warning(f"Failed to close pane {focused_pane}")

    def _on_close_tab(self) -> None:
        """Handle close tab request from menu.

        Closes the currently active tab.
        """
        current_index = self.currentIndex()
        self._on_tab_close_requested(current_index)

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
