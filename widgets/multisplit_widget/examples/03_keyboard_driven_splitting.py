#!/usr/bin/env python3
"""
Keyboard-Driven Split Control - MultiSplit Widget Example

This example demonstrates advanced keyboard control for power users:
- Vim-like keyboard commands for splitting and navigation
- Command palette for quick actions
- Keyboard focus navigation between panes
- Advanced hotkey combinations
- Modal interaction patterns

Key Learning Points:
1. Advanced keyboard event handling with MultiSplit
2. Modal command interfaces (like Vim command mode)
3. Focus navigation patterns
4. Power-user workflow optimization
5. Custom event filters for global shortcuts

Usage:
- Ctrl+Space: Open command palette
- Leader key (Space): Enter command mode
- h/j/k/l: Navigate panes (vim-style)
- s/v: Split horizontal/vertical
- c: Close pane
- n: New document
- ESC: Exit command mode
"""

import sys
from enum import Enum
from pathlib import Path
from typing import Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtCore import QEvent, QObject, Qt, QTimer, Signal
from PySide6.QtGui import QFont, QKeyEvent
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)
from vfwidgets_multisplit import MultisplitWidget, WherePosition, WidgetProvider


class Mode(Enum):
    NORMAL = "normal"
    COMMAND = "command"
    INSERT = "insert"


class CommandPalette(QDialog):
    """Command palette for quick actions."""

    command_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Command Palette")
        self.setModal(True)
        self.setFixedSize(500, 300)

        # Setup UI
        layout = QVBoxLayout(self)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type command name...")
        self.search_input.textChanged.connect(self.filter_commands)
        layout.addWidget(self.search_input)

        # Command list
        self.command_list = QListWidget()
        self.command_list.itemDoubleClicked.connect(self.execute_selected)
        layout.addWidget(self.command_list)

        # Buttons
        button_layout = QHBoxLayout()
        execute_btn = QPushButton("Execute")
        execute_btn.clicked.connect(self.execute_selected)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)

        button_layout.addWidget(execute_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        # Available commands
        self.commands = {
            "split-horizontal": "Split current pane horizontally",
            "split-vertical": "Split current pane vertically",
            "new-document": "Create new document",
            "close-pane": "Close current pane",
            "navigate-left": "Navigate to left pane",
            "navigate-right": "Navigate to right pane",
            "navigate-up": "Navigate to up pane",
            "navigate-down": "Navigate to down pane",
            "focus-first": "Focus first pane",
            "focus-last": "Focus last pane",
            "maximize-pane": "Maximize current pane",
            "balance-panes": "Balance all pane sizes",
            "save-layout": "Save current layout",
            "load-layout": "Load saved layout",
        }

        self.populate_commands()

        # Focus search input
        self.search_input.setFocus()

    def populate_commands(self):
        """Populate command list."""
        self.command_list.clear()
        for cmd, desc in self.commands.items():
            item = QListWidgetItem(f"{cmd}: {desc}")
            item.setData(Qt.ItemDataRole.UserRole, cmd)
            self.command_list.addItem(item)

    def filter_commands(self, text: str):
        """Filter commands based on search text."""
        self.command_list.clear()
        for cmd, desc in self.commands.items():
            if text.lower() in cmd.lower() or text.lower() in desc.lower():
                item = QListWidgetItem(f"{cmd}: {desc}")
                item.setData(Qt.ItemDataRole.UserRole, cmd)
                self.command_list.addItem(item)

    def execute_selected(self):
        """Execute selected command."""
        current_item = self.command_list.currentItem()
        if current_item:
            command = current_item.data(Qt.ItemDataRole.UserRole)
            self.command_selected.emit(command)
            self.close()

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key events."""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.execute_selected()
        elif event.key() == Qt.Key.Key_Down:
            self.command_list.setFocus()
            if self.command_list.count() > 0:
                self.command_list.setCurrentRow(0)
        else:
            super().keyPressEvent(event)


class KeyboardControlledEditor(QPlainTextEdit):
    """Editor with keyboard control awareness."""

    focus_navigation_requested = Signal(str)  # direction: h/j/k/l

    def __init__(self, document_id: str):
        super().__init__()
        self.document_id = document_id
        self.in_command_mode = False

        # Setup editor
        font = QFont("Consolas", 12)
        self.setFont(font)
        self.setPlainText(
            f"# Document {document_id}\n\nPress Space to enter command mode\nPress Ctrl+Space for command palette"
        )

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key events with command mode awareness."""
        # Check for command mode navigation
        if self.in_command_mode:
            if event.key() == Qt.Key.Key_H:
                self.focus_navigation_requested.emit("left")
                return
            elif event.key() == Qt.Key.Key_J:
                self.focus_navigation_requested.emit("down")
                return
            elif event.key() == Qt.Key.Key_K:
                self.focus_navigation_requested.emit("up")
                return
            elif event.key() == Qt.Key.Key_L:
                self.focus_navigation_requested.emit("right")
                return
            elif event.key() == Qt.Key.Key_Escape:
                self.in_command_mode = False
                self.parent().parent().exit_command_mode()
                return

        # Regular text editing
        super().keyPressEvent(event)

    def set_command_mode(self, enabled: bool):
        """Set command mode state."""
        self.in_command_mode = enabled


class KeyboardPaneWidget(QWidget):
    """Pane widget with keyboard control indicators."""

    def __init__(self, pane_id: str, document_id: str):
        super().__init__()
        self.pane_id = pane_id
        self.document_id = document_id

        # Setup layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Set initial border style (unfocused)
        self.setStyleSheet("""
            QWidget {
                border: 2px solid #e0e0e0;
                background-color: white;
            }
        """)

        # Header with status
        self.header = QFrame()
        self.header.setFrameStyle(QFrame.Shape.StyledPanel)
        self.update_header_style(False)

        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(4, 2, 4, 2)

        self.header_label = QLabel(f"📄 {document_id} | Pane: {pane_id[:8]}...")
        self.header_label.setStyleSheet("font-size: 10px; color: #333;")
        header_layout.addWidget(self.header_label)

        self.mode_label = QLabel("NORMAL")
        self.mode_label.setStyleSheet("font-size: 10px; font-weight: bold; color: #666;")
        header_layout.addWidget(self.mode_label)

        # Editor
        self.editor = KeyboardControlledEditor(document_id)

        # Add to layout
        layout.addWidget(self.header)
        layout.addWidget(self.editor, 1)

    def update_header_style(self, focused: bool):
        """Update header and border style based on focus."""
        print(f"[STYLE] Updating {self.pane_id[:8]} focused={focused}")
        if focused:
            # Blue border around entire pane (using QWidget since class selector doesn't work)
            self.setStyleSheet("""
                QWidget {
                    border: 4px solid #0078d4;
                    background-color: white;
                }
            """)
            # Green header
            self.header.setStyleSheet("""
                QFrame {
                    background-color: #4CAF50;
                    border: none;
                    padding: 2px;
                }
            """)
            print(f"[STYLE] Applied BLUE border to {self.pane_id[:8]}")
        else:
            # Light gray border when unfocused (visible but subtle)
            self.setStyleSheet("""
                QWidget {
                    border: 2px solid #e0e0e0;
                    background-color: white;
                }
            """)
            # Gray header
            self.header.setStyleSheet("""
                QFrame {
                    background-color: #f0f0f0;
                    border: none;
                    padding: 2px;
                }
            """)
            print(f"[STYLE] Applied GRAY border to {self.pane_id[:8]}")

    def set_mode(self, mode: Mode):
        """Set current mode."""
        self.mode_label.setText(mode.value.upper())

        if mode == Mode.COMMAND:
            self.mode_label.setStyleSheet("font-size: 10px; font-weight: bold; color: #ff6600;")
            self.editor.set_command_mode(True)
        else:
            self.mode_label.setStyleSheet("font-size: 10px; font-weight: bold; color: #666;")
            self.editor.set_command_mode(False)


class KeyboardProvider(WidgetProvider):
    """Provider for keyboard-controlled panes."""

    def __init__(self):
        self.panes: dict[str, KeyboardPaneWidget] = {}
        self.document_counter = 0

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Create a keyboard-controlled pane."""
        if widget_id.startswith("doc-"):
            document_id = widget_id
        else:
            self.document_counter += 1
            document_id = f"doc-{self.document_counter}"

        pane_widget = KeyboardPaneWidget(pane_id, document_id)
        self.panes[pane_id] = pane_widget

        return pane_widget

    def get_pane_widget(self, pane_id: str) -> Optional[KeyboardPaneWidget]:
        """Get pane widget by ID."""
        return self.panes.get(pane_id)

    def create_new_document(self) -> str:
        """Create new document ID."""
        self.document_counter += 1
        return f"doc-{self.document_counter}"

    def widget_closing(self, widget_id: str, pane_id: str, widget: QWidget) -> None:
        """Handle widget closing - lifecycle hook called before pane removal."""
        print(f"[LIFECYCLE] widget_closing() called for {widget_id} in pane {pane_id[:8]}")

        # Clean up from tracking dictionary
        if pane_id in self.panes:
            print(f"[PROVIDER] Removing pane {pane_id[:8]} from provider tracking")
            del self.panes[pane_id]
        else:
            print(f"[PROVIDER] Warning: Pane {pane_id[:8]} not found in provider tracking")


class GlobalKeyHandler(QObject):
    """Global key event handler."""

    command_mode_requested = Signal()
    command_palette_requested = Signal()
    split_requested = Signal(str)  # direction
    navigation_requested = Signal(str)  # direction
    action_requested = Signal(str)  # action

    def eventFilter(self, obj, event):
        """Filter global key events."""
        if event.type() == QEvent.Type.KeyPress:
            # Command palette
            if (
                event.modifiers() == Qt.KeyboardModifier.ControlModifier
                and event.key() == Qt.Key.Key_Space
            ):
                self.command_palette_requested.emit()
                return True

            # Leader key for command mode
            if (
                event.key() == Qt.Key.Key_Space
                and event.modifiers() == Qt.KeyboardModifier.NoModifier
            ):
                # Only if no widget has focus or if in a non-text widget
                focused = QApplication.focusWidget()
                if not isinstance(focused, QPlainTextEdit):
                    self.command_mode_requested.emit()
                    return True

        return False


class KeyboardDrivenWindow(QMainWindow):
    """Main window with advanced keyboard controls."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("MultiSplit Keyboard Control - Power User Interface")
        self.setGeometry(100, 100, 1400, 900)

        self.current_mode = Mode.NORMAL
        self.command_timeout = QTimer()
        self.command_timeout.setSingleShot(True)
        self.command_timeout.timeout.connect(self.exit_command_mode)

        # Create provider
        self.provider = KeyboardProvider()

        # Create MultiSplit widget
        self.multisplit = MultisplitWidget(provider=self.provider)
        self.setCentralWidget(self.multisplit)

        # Setup global key handler
        self.key_handler = GlobalKeyHandler()
        QApplication.instance().installEventFilter(self.key_handler)

        # Connect signals
        self.key_handler.command_mode_requested.connect(self.enter_command_mode)
        self.key_handler.command_palette_requested.connect(self.show_command_palette)

        # Connect to public focus_changed signal
        self.multisplit.focus_changed.connect(self.on_focus_changed)

        # Setup UI
        self.setup_statusbar()
        self.setup_help()

        # Initialize
        self.multisplit.initialize_empty("doc-1")
        self.connect_pane_signals()

        # Command palette
        self.command_palette = None

    def setup_statusbar(self):
        """Setup status bar with mode indicator."""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Mode indicator
        self.mode_widget = QLabel("NORMAL")
        self.mode_widget.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                padding: 4px 8px;
                font-weight: bold;
                min-width: 60px;
            }
        """)
        self.statusbar.addPermanentWidget(self.mode_widget)

        self.update_status_message()

    def setup_help(self):
        """Setup help information."""
        help_text = """
        KEYBOARD CONTROLS:

        Global:
        • Ctrl+Space: Command palette
        • Space: Enter command mode (when not editing text)
        • ESC: Exit command mode

        Command Mode (when mode shows COMMAND):
        • h/j/k/l: Navigate left/down/up/right
        • s: Split horizontal
        • v: Split vertical
        • c: Close pane
        • n: New document

        Power User Tips:
        • Focus navigation works across any pane layout
        • Command mode times out after 3 seconds
        • All actions work without mouse
        """

        # Store help for display
        self.help_text = help_text

    def connect_pane_signals(self):
        """Connect signals from pane editors."""
        for pid, pane_widget in list(self.provider.panes.items()):
            try:
                if hasattr(pane_widget, "editor"):
                    # Disconnect first to avoid duplicate connections
                    try:
                        pane_widget.editor.focus_navigation_requested.disconnect(self.navigate_focus)
                    except:
                        pass  # Not connected yet

                    # Connect
                    pane_widget.editor.focus_navigation_requested.connect(self.navigate_focus)
            except RuntimeError as e:
                # Widget was deleted, skip it
                print(f"[SIGNALS] Skipping deleted widget {pid[:8]}: {e}")
                continue

    def enter_command_mode(self):
        """Enter command mode."""
        if self.current_mode == Mode.NORMAL:
            self.current_mode = Mode.COMMAND
            self.update_mode_display()

            # Install command mode event filter
            self.installEventFilter(self)

            # Set timeout
            self.command_timeout.start(3000)  # 3 second timeout

            self.statusbar.showMessage(
                "COMMAND MODE - h/j/k/l: navigate, s/v: split, c: close, n: new, ESC: exit", 3000
            )

    def exit_command_mode(self):
        """Exit command mode."""
        if self.current_mode == Mode.COMMAND:
            self.current_mode = Mode.NORMAL
            self.update_mode_display()

            # Remove event filter
            self.removeEventFilter(self)

            # Stop timeout
            self.command_timeout.stop()

            self.update_status_message()

    def update_mode_display(self):
        """Update mode display in all panes."""
        self.mode_widget.setText(self.current_mode.value.upper())

        if self.current_mode == Mode.COMMAND:
            self.mode_widget.setStyleSheet("""
                QLabel {
                    background-color: #ff6600;
                    color: white;
                    border: 1px solid #e55a00;
                    padding: 4px 8px;
                    font-weight: bold;
                    min-width: 60px;
                }
            """)
        else:
            self.mode_widget.setStyleSheet("""
                QLabel {
                    background-color: #f0f0f0;
                    border: 1px solid #ccc;
                    padding: 4px 8px;
                    font-weight: bold;
                    min-width: 60px;
                }
            """)

        # Update all panes
        for pane_widget in self.provider.panes.values():
            pane_widget.set_mode(self.current_mode)

    def eventFilter(self, obj, event):
        """Handle command mode events."""
        if self.current_mode == Mode.COMMAND and event.type() == QEvent.Type.KeyPress:
            key = event.key()

            # Reset timeout on any key
            self.command_timeout.start(3000)

            if key == Qt.Key.Key_H:
                self.navigate_focus("left")
                return True
            elif key == Qt.Key.Key_J:
                self.navigate_focus("down")
                return True
            elif key == Qt.Key.Key_K:
                self.navigate_focus("up")
                return True
            elif key == Qt.Key.Key_L:
                self.navigate_focus("right")
                return True
            elif key == Qt.Key.Key_S:
                self.split_current_pane(WherePosition.RIGHT)
                self.exit_command_mode()
                return True
            elif key == Qt.Key.Key_V:
                self.split_current_pane(WherePosition.BOTTOM)
                self.exit_command_mode()
                return True
            elif key == Qt.Key.Key_C:
                self.close_current_pane()
                self.exit_command_mode()
                return True
            elif key == Qt.Key.Key_N:
                self.create_new_document()
                self.exit_command_mode()
                return True
            elif key == Qt.Key.Key_Escape:
                self.exit_command_mode()
                return True

        return super().eventFilter(obj, event)

    def show_command_palette(self):
        """Show command palette."""
        if not self.command_palette:
            self.command_palette = CommandPalette(self)
            self.command_palette.command_selected.connect(self.execute_command)

        self.command_palette.search_input.clear()
        self.command_palette.populate_commands()
        self.command_palette.show()
        self.command_palette.search_input.setFocus()

    def execute_command(self, command: str):
        """Execute a command from palette."""
        if command == "split-horizontal":
            self.split_current_pane(WherePosition.RIGHT)
        elif command == "split-vertical":
            self.split_current_pane(WherePosition.BOTTOM)
        elif command == "new-document":
            self.create_new_document()
        elif command == "close-pane":
            self.close_current_pane()
        elif command == "navigate-left":
            self.navigate_focus("left")
        elif command == "navigate-right":
            self.navigate_focus("right")
        elif command == "navigate-up":
            self.navigate_focus("up")
        elif command == "navigate-down":
            self.navigate_focus("down")
        elif command == "focus-first":
            panes = self.multisplit.get_pane_ids()
            if panes:
                self.focus_pane(panes[0])
        elif command == "focus-last":
            panes = self.multisplit.get_pane_ids()
            if panes:
                self.focus_pane(panes[-1])
        else:
            self.statusbar.showMessage(f"Command not implemented: {command}", 2000)

    def navigate_focus(self, direction: str):
        """Navigate focus in specified direction."""
        # This is a simplified implementation - a real one would need
        # to understand the spatial layout of panes
        panes = self.multisplit.get_pane_ids()
        focused = self.multisplit.get_focused_pane()

        if not focused or not panes:
            return

        current_index = panes.index(focused) if focused in panes else 0

        if direction in ["right", "down"]:
            next_index = (current_index + 1) % len(panes)
        else:  # left, up
            next_index = (current_index - 1) % len(panes)

        self.focus_pane(panes[next_index])

    def focus_pane(self, pane_id: str):
        """Focus specific pane."""
        pane_widget = self.provider.get_pane_widget(pane_id)
        if pane_widget and hasattr(pane_widget, "editor"):
            pane_widget.editor.setFocus()

    def split_current_pane(self, position: WherePosition):
        """Split current pane."""
        focused = self.multisplit.get_focused_pane()
        if not focused:
            self.statusbar.showMessage("No pane to split")
            return

        doc_id = self.provider.create_new_document()
        success = self.multisplit.split_pane(focused, doc_id, position, 0.5)

        if success:
            direction = "horizontally" if position == WherePosition.RIGHT else "vertically"
            self.statusbar.showMessage(f"Split {direction} - created {doc_id}")
            self.connect_pane_signals()
        else:
            self.statusbar.showMessage("Failed to split pane")

    def create_new_document(self):
        """Create new document in current pane."""
        focused = self.multisplit.get_focused_pane()
        if focused:
            # Split to create new document
            doc_id = self.provider.create_new_document()
            success = self.multisplit.split_pane(focused, doc_id, WherePosition.RIGHT, 0.5)
            if success:
                self.connect_pane_signals()
                self.statusbar.showMessage(f"Created new document: {doc_id}")
        else:
            doc_id = self.provider.create_new_document()
            self.multisplit.initialize_empty(doc_id)
            self.statusbar.showMessage(f"Created first document: {doc_id}")

    def close_current_pane(self):
        """Close current pane."""
        focused = self.multisplit.get_focused_pane()
        if focused:
            success = self.multisplit.remove_pane(focused)
            if success:
                self.statusbar.showMessage(f"Closed pane: {focused[:8]}...")
            else:
                self.statusbar.showMessage("Cannot close - last pane")

    def update_status_message(self):
        """Update status bar message."""
        focused = self.multisplit.get_focused_pane()
        pane_count = len(self.multisplit.get_pane_ids())

        if self.current_mode == Mode.NORMAL:
            msg = f"Ready | Panes: {pane_count} | Focus: {focused[:8] if focused else 'None'} | Ctrl+Space: palette, Space: command mode"
        else:
            msg = "COMMAND MODE - Use h/j/k/l to navigate, s/v to split, c to close, ESC to exit"

        self.statusbar.showMessage(msg)

    def on_focus_changed(self, old_pane_id: str, new_pane_id: str):
        """Handle focus change event."""
        old_display = old_pane_id[:8] if old_pane_id else "None"
        new_display = new_pane_id[:8] if new_pane_id else "None"
        print(f"[FOCUS] Focus changed: {old_display} -> {new_display}")

        # Update visual focus indicators
        # Note: Deleted panes are automatically cleaned up via widget_closing() lifecycle hook
        for pid, pane_widget in list(self.provider.panes.items()):
            try:
                is_focused = (pid == new_pane_id)
                print(f"[FOCUS] Setting {pid[:8]} focused={is_focused}")
                pane_widget.update_header_style(is_focused)
            except RuntimeError as e:
                # Widget was deleted, skip it
                print(f"[FOCUS] Skipping deleted widget {pid[:8]}: {e}")
                continue

        self.update_status_message()

    def keyPressEvent(self, event: QKeyEvent):
        """Handle window-level key events."""
        # F1 for help
        if event.key() == Qt.Key.Key_F1:
            QMessageBox.information(self, "Keyboard Controls", self.help_text)
            return

        super().keyPressEvent(event)


def main():
    """Run the keyboard-driven example."""
    app = QApplication(sys.argv)

    print("=" * 70)
    print("MULTISPLIT KEYBOARD CONTROL - POWER USER INTERFACE")
    print("=" * 70)
    print()
    print("This example demonstrates advanced keyboard control:")
    print("• Vim-like navigation with h/j/k/l keys")
    print("• Command mode for power users (Space to enter)")
    print("• Command palette for discoverable actions (Ctrl+Space)")
    print("• Modal interaction patterns")
    print("• No mouse required for any operation!")
    print()
    print("Try this workflow:")
    print("1. Press Space to enter COMMAND mode")
    print("2. Press 's' to split horizontally")
    print("3. Press 'n' to create new document")
    print("4. Use h/j/k/l to navigate between panes")
    print("5. Press 'v' to split vertically")
    print("6. Press Ctrl+Space for command palette")
    print("7. Press F1 for full help")
    print()
    print("Key insight: Keyboard control makes complex layouts fast to manage!")
    print("=" * 70)
    print()

    window = KeyboardDrivenWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
