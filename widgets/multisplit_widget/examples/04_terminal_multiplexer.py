#!/usr/bin/env python3
"""
Terminal Multiplexer - MultiSplit Widget Example

This example demonstrates using MultisplitWidget with terminal widgets
to create a tmux/screen-like terminal multiplexer interface.

Key Learning Points:
1. Using TerminalWidget with MultisplitWidget
2. Managing multiple terminal sessions
3. Minimal divider style for terminal UIs
4. Focus handling with QWebEngineView-based widgets

Usage:
- File > New Terminal: Creates new terminal in current pane
- Split menu: Split current terminal pane horizontally/vertically
- Click between terminals to change focus
- Ctrl+Shift+H: Split horizontally
- Ctrl+Shift+V: Split vertically
- Ctrl+W: Close current terminal pane
"""

import sys
from pathlib import Path
from typing import Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Also add terminal_widget to path
terminal_widget_path = Path(__file__).parent.parent.parent / "terminal_widget" / "src"
sys.path.insert(0, str(terminal_widget_path))

from PySide6.QtCore import QTimer
from PySide6.QtGui import QAction, QColor
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QWidget,
)
from vfwidgets_multisplit import MultisplitWidget, SplitterStyle, WherePosition, WidgetProvider

try:
    from vfwidgets_terminal import TerminalWidget
    TERMINAL_AVAILABLE = True
except ImportError:
    TERMINAL_AVAILABLE = False
    print("WARNING: vfwidgets_terminal not available. Install it first:")
    print("  pip install -e ./widgets/terminal_widget")


class TerminalPane(QWidget):
    """Enhanced terminal pane with synchronized background colors.

    CRITICAL: This widget demonstrates the proper pattern for embedding QWebEngineView
    widgets (like TerminalWidget) in MultisplitWidget to prevent white flash during
    initialization. The key insight is that FOUR background colors must match:

    1. MultisplitWidget container background
    2. TerminalPane container background
    3. QWebEngineView page background
    4. xterm.js terminal theme background

    All four are synchronized by extracting the color from TerminalWidget's theme.
    """

    def __init__(self, terminal_id: str, pane_id: str, background_color: str):
        super().__init__()
        self.terminal_id = terminal_id
        self.pane_id = pane_id

        # CRITICAL LAYER 0: Set container background FIRST, before any widgets
        # This ensures the container never shows default white background
        # The background_color is passed from the provider who knows the theme
        self.setStyleSheet(f"background-color: {background_color};")

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header with terminal info
        self.header = QLabel()
        self.header.setStyleSheet("""
            QLabel {
                background-color: #2d2d30;
                border-bottom: 1px solid #555;
                padding: 2px 8px;
                font-size: 10px;
                color: #ccc;
            }
        """)
        self.header.setText(f"🖥️  Terminal {terminal_id} | Pane: {pane_id[:8]}...")

        # Create terminal widget
        if TERMINAL_AVAILABLE:
            self.terminal = TerminalWidget()

            # LAYER 2: Set QWebEngineView page background to match terminal
            # TerminalWidget already does this in terminal.py:618, but we ensure it here
            self.terminal.web_view.page().setBackgroundColor(QColor(background_color))

            # LAYER 3: xterm.js theme background is already set by TerminalWidget
            # All three layers (container, page, xterm) now match - no flash!
        else:
            # Fallback to placeholder with provided background
            self.terminal = QLabel("Terminal widget not available\nInstall vfwidgets_terminal")
            self.terminal.setStyleSheet(f"background-color: {background_color}; color: #ccc; padding: 20px;")

        # Add to layout
        layout.addWidget(self.header)
        layout.addWidget(self.terminal, 1)

    def setFocus(self, reason):
        """Override setFocus to properly focus the terminal widget.

        CRITICAL for QWebEngineView-based widgets:
        When using widgets based on QWebEngineView (like TerminalWidget),
        you must override setFocus() to forward focus to the actual
        web view, not just the container widget.
        """
        super().setFocus(reason)
        if TERMINAL_AVAILABLE and hasattr(self, 'terminal'):
            self.terminal.setFocus(reason)


class TerminalProvider(WidgetProvider):
    """Provides terminal widgets for MultiSplit panes.

    This provider demonstrates:
    1. Creating TerminalWidget instances on demand
    2. Tracking terminal sessions
    3. Cleanup on widget closing
    4. Theme-aware background color extraction
    """

    def __init__(self):
        self.terminals: dict[str, TerminalPane] = {}
        self.terminal_counter = 0
        self._background_color: Optional[str] = None

    def get_background_color(self) -> str:
        """Get the terminal background color for container synchronization.

        This extracts the background color from the terminal theme, allowing
        the MultisplitWidget container to match the terminal background.

        Returns:
            Hex color string (e.g., '#1e1e1e')
        """
        if self._background_color:
            return self._background_color

        # Extract from terminal widget constants
        if TERMINAL_AVAILABLE:
            try:
                from vfwidgets_terminal.constants import DARK_THEME_COLORS
                self._background_color = DARK_THEME_COLORS.get('background', '#1e1e1e')
                return self._background_color
            except ImportError:
                pass

        # Fallback
        self._background_color = '#1e1e1e'
        return self._background_color

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Create a terminal widget pane.

        Args:
            widget_id: Terminal identifier (e.g., "term-1")
            pane_id: Unique pane ID from MultisplitWidget

        Returns:
            TerminalPane widget with embedded terminal
        """
        # Get background color from theme BEFORE creating the pane
        # This ensures the container has the right background from the start
        background_color = self.get_background_color()

        # Create terminal pane with header and background color
        terminal_pane = TerminalPane(widget_id, pane_id, background_color)

        # Store reference
        self.terminals[widget_id] = terminal_pane

        return terminal_pane

    def create_new_terminal(self) -> str:
        """Create a new terminal ID."""
        self.terminal_counter += 1
        return f"term-{self.terminal_counter}"

    def widget_closing(self, widget_id: str, pane_id: str, widget: QWidget) -> None:
        """Handle widget closing - cleanup terminal session.

        Args:
            widget_id: Terminal ID being closed
            pane_id: Pane ID where terminal is
            widget: Actual widget instance
        """
        if widget_id in self.terminals:
            # Note: TerminalWidget automatically cleans up its server
            # when the widget is destroyed, so we don't need manual cleanup

            # Remove from tracking
            del self.terminals[widget_id]
            print(f"Terminal {widget_id} closed")


class TerminalMultiplexerWindow(QMainWindow):
    """Main window demonstrating terminal multiplexing with MultiSplit.

    This example shows the pattern for building terminal multiplexer UIs:
    1. Create TerminalProvider for terminal widgets
    2. Use minimal SplitterStyle for clean terminal look
    3. Handle focus properly for QWebEngineView-based terminals
    4. Provide split/close operations via menus and shortcuts
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Terminal Multiplexer - MultisplitWidget Demo")
        self.setGeometry(100, 100, 1200, 800)

        # Create provider for terminal widgets
        self.provider = TerminalProvider()

        # Create MultiSplit widget with custom dark splitter style for terminals
        # Use 1px handles with dark colors to match terminal theme
        terminal_bg = self.provider.get_background_color()
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
        self.multisplit = MultisplitWidget(provider=self.provider, splitter_style=dark_splitter_style)

        # CRITICAL: Set MultisplitWidget container background to match terminal theme
        # This prevents white flash during pane resize/split operations
        self.multisplit.setStyleSheet(f"background-color: {terminal_bg};")

        self.setCentralWidget(self.multisplit)

        # Setup UI
        self.setup_menus()
        self.setup_toolbar()
        self.setup_statusbar()

        # Connect signals
        self.multisplit.focus_changed.connect(self.on_focus_changed)
        self.multisplit.pane_added.connect(self.on_pane_added)
        self.multisplit.pane_removed.connect(self.on_pane_removed)

        # Initialize with first terminal
        self.create_new_terminal()

        # Update display timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(1000)

    def setup_menus(self):
        """Setup application menus."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        new_action = QAction("&New Terminal", self)
        new_action.setShortcut("Ctrl+Shift+N")
        new_action.triggered.connect(self.create_new_terminal)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Split menu - Core terminal multiplexer functionality!
        split_menu = menubar.addMenu("&Split")

        split_h = QAction("Split &Horizontally", self)
        split_h.setShortcut("Ctrl+Shift+H")
        split_h.triggered.connect(lambda: self.split_current_pane(WherePosition.RIGHT))
        split_menu.addAction(split_h)

        split_v = QAction("Split &Vertically", self)
        split_v.setShortcut("Ctrl+Shift+V")
        split_v.triggered.connect(lambda: self.split_current_pane(WherePosition.BOTTOM))
        split_menu.addAction(split_v)

        split_menu.addSeparator()

        close_pane = QAction("&Close Pane", self)
        close_pane.setShortcut("Ctrl+W")
        close_pane.triggered.connect(self.close_current_pane)
        split_menu.addAction(close_pane)

    def setup_toolbar(self):
        """Setup toolbar with common actions."""
        toolbar = QToolBar("Main")
        self.addToolBar(toolbar)

        # New terminal
        toolbar.addAction("🖥️  New", self.create_new_terminal)

        toolbar.addSeparator()

        # Split actions - tmux-style!
        toolbar.addAction("⬌ Split →", lambda: self.split_current_pane(WherePosition.RIGHT))
        toolbar.addAction("⬍ Split ↓", lambda: self.split_current_pane(WherePosition.BOTTOM))
        toolbar.addAction("❌ Close", self.close_current_pane)

        toolbar.addSeparator()

        # Info
        toolbar.addAction("ℹ️  Info", self.show_info)

    def setup_statusbar(self):
        """Setup status bar."""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready - Terminal multiplexer with drag-to-resize dividers")

    def create_new_terminal(self):
        """Create new terminal in focused pane or first available."""
        focused_pane = self.multisplit.get_focused_pane()

        if not focused_pane:
            # No panes yet - initialize
            term_id = self.provider.create_new_terminal()
            self.multisplit.initialize_empty(term_id)
            self.statusbar.showMessage(f"Created first terminal: {term_id}")
        else:
            # Create new terminal in current pane
            term_id = self.provider.create_new_terminal()
            # Replace current pane content
            if self.multisplit.remove_pane(focused_pane):
                panes = self.multisplit.get_pane_ids()
                if panes:
                    # Split to add new terminal
                    self.multisplit.split_pane(panes[0], term_id, WherePosition.RIGHT, 0.5)
                else:
                    # Initialize if no panes left
                    self.multisplit.initialize_empty(term_id)
                self.statusbar.showMessage(f"Created new terminal: {term_id}")

    def split_current_pane(self, position: WherePosition):
        """Split the currently focused pane - tmux-style terminal splitting!

        This is the core feature for terminal multiplexers:
        - Split any terminal pane at runtime
        - Creates new terminal session in new pane
        - Maintains layout dynamically
        """
        focused_pane = self.multisplit.get_focused_pane()

        if not focused_pane:
            self.statusbar.showMessage("No pane to split")
            return

        # Create new terminal for the split
        term_id = self.provider.create_new_terminal()

        # Perform the split
        success = self.multisplit.split_pane(focused_pane, term_id, position, 0.5)

        if success:
            direction = "horizontally" if position == WherePosition.RIGHT else "vertically"
            self.statusbar.showMessage(f"Split pane {direction} - added {term_id}")
        else:
            self.statusbar.showMessage("Failed to split pane")

    def close_current_pane(self):
        """Close currently focused terminal pane."""
        focused_pane = self.multisplit.get_focused_pane()

        if not focused_pane:
            self.statusbar.showMessage("No pane to close")
            return

        # Ask for confirmation
        reply = QMessageBox.question(
            self,
            "Close Terminal",
            "Close this terminal session?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            success = self.multisplit.remove_pane(focused_pane)
            if success:
                self.statusbar.showMessage(f"Closed pane: {focused_pane[:8]}...")
            else:
                self.statusbar.showMessage("Cannot close - last pane")

    def show_info(self):
        """Show information about current state."""
        focused = self.multisplit.get_focused_pane()
        all_panes = self.multisplit.get_pane_ids()

        info = f"Focus: {focused[:8] if focused else 'None'} | Total terminals: {len(all_panes)}"
        self.statusbar.showMessage(info)

        print("\n=== TERMINAL MULTIPLEXER INFO ===")
        print(f"Focused pane: {focused}")
        print(f"All panes: {all_panes}")
        print(f"Total terminals: {len(self.provider.terminals)}")
        print("=================================\n")

    def on_focus_changed(self, old_pane_id: str, new_pane_id: str):
        """Handle pane focus change."""
        if new_pane_id:
            self.statusbar.showMessage(
                f"Focus: {new_pane_id[:8]}... | Use Ctrl+Shift+H/V to split", 2000
            )

    def on_pane_added(self, pane_id: str):
        """Handle pane added."""
        all_panes = self.multisplit.get_pane_ids()
        print(f"Pane added: {pane_id} | Total: {len(all_panes)}")

    def on_pane_removed(self, pane_id: str):
        """Handle pane removed."""
        all_panes = self.multisplit.get_pane_ids()
        print(f"Pane removed: {pane_id} | Total: {len(all_panes)}")

    def update_status(self):
        """Update status display."""
        focused = self.multisplit.get_focused_pane()
        pane_count = len(self.multisplit.get_pane_ids())
        terminal_count = len(self.provider.terminals)

        if focused:
            msg = f"Focused: {focused[:8]}... | Panes: {pane_count} | Terminals: {terminal_count}"
            # Only update if different from current message
            if msg != self.statusbar.currentMessage():
                self.statusbar.showMessage(msg)


def main():
    """Run the terminal multiplexer example."""
    app = QApplication(sys.argv)

    if not TERMINAL_AVAILABLE:
        print("\n" + "=" * 70)
        print("ERROR: vfwidgets_terminal not available!")
        print("=" * 70)
        print()
        print("This example requires the terminal widget package.")
        print("Install it with:")
        print()
        print("  pip install -e ./widgets/terminal_widget")
        print()
        print("=" * 70)
        print()
        return 1

    print("=" * 70)
    print("TERMINAL MULTIPLEXER - MULTISPLIT WIDGET DEMO")
    print("=" * 70)
    print()
    print("This example demonstrates terminal multiplexing with MultisplitWidget:")
    print("• Multiple terminal sessions in split panes")
    print("• Minimal 1px dividers (terminal UI style)")
    print("• Drag-to-resize dividers for adjusting terminal sizes")
    print("• tmux/screen-like interface")
    print()
    print("Try this:")
    print("1. Type commands in the initial terminal")
    print("2. Split > Split Horizontally (or Ctrl+Shift+H)")
    print("3. New terminal session appears - type in it")
    print("4. Split > Split Vertically (or Ctrl+Shift+V)")
    print("5. Click between terminals to change focus")
    print("6. Drag the dividers to resize terminal panes")
    print("7. Close panes: Split > Close Pane (or Ctrl+W)")
    print()
    print("Key insight: MultisplitWidget + TerminalWidget = Terminal Multiplexer!")
    print("=" * 70)
    print()

    window = TerminalMultiplexerWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
