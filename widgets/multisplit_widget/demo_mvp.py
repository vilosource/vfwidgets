#!/usr/bin/env python3
"""
MultiSplit Widget MVP Demo

Demonstrates all features of the completed MultiSplit widget:
- Dynamic splitting in any direction
- Focus management with visual indicators
- Keyboard navigation (Tab, Shift+Tab, Alt+Arrows)
- Drag-to-resize dividers
- Undo/redo support
- Session persistence
- Validation system
- Widget provider pattern
"""

import sys
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QTextEdit,
    QToolBar,
    QWidget,
)

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from vfwidgets_multisplit import MultisplitWidget
from vfwidgets_multisplit.core.types import PaneId, WherePosition, WidgetId
from vfwidgets_multisplit.view.container import WidgetProvider


class DemoWidgetProvider(WidgetProvider):
    """Demo widget provider that creates different widget types."""

    def __init__(self):
        """Initialize provider."""
        self.widget_count = 0

    def provide_widget(self, widget_id: WidgetId, pane_id: PaneId) -> QWidget:
        """Provide a widget based on the widget_id.

        Args:
            widget_id: Type and identifier like 'editor:main.py'
            pane_id: Pane that will contain the widget

        Returns:
            QWidget instance
        """
        widget_str = str(widget_id)

        if widget_str.startswith("editor:"):
            # Create editor widget
            filename = widget_str.split(":", 1)[1]
            editor = QTextEdit()
            editor.setPlainText(f"# {filename}\n\n# Editor pane {pane_id}\n\n")
            editor.setFont(editor.font())
            return editor

        elif widget_str.startswith("terminal:"):
            # Create terminal-like widget
            terminal_id = widget_str.split(":", 1)[1]
            terminal = QTextEdit()
            terminal.setStyleSheet("""
                QTextEdit {
                    background-color: #1e1e1e;
                    color: #00ff00;
                    font-family: monospace;
                }
            """)
            terminal.setPlainText(f"$ Terminal {terminal_id} (Pane: {pane_id})\n$ ")
            return terminal

        elif widget_str.startswith("preview:"):
            # Create preview widget
            content = widget_str.split(":", 1)[1]
            preview = QLabel(f"<h2>Preview: {content}</h2><p>Pane ID: {pane_id}</p>")
            preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
            preview.setStyleSheet("""
                QLabel {
                    background-color: #f5f5f5;
                    padding: 20px;
                }
            """)
            return preview

        else:
            # Default widget
            self.widget_count += 1
            widget = QLabel(f"Widget #{self.widget_count}\nType: {widget_id}\nPane: {pane_id}")
            widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            widget.setStyleSheet("border: 1px solid #ccc; padding: 10px;")
            return widget


class DemoMainWindow(QMainWindow):
    """Main window demonstrating MultiSplit widget."""

    def __init__(self):
        """Initialize demo window."""
        super().__init__()

        self.setWindowTitle("MultiSplit Widget MVP Demo")
        self.setGeometry(100, 100, 1200, 800)

        # Create widget provider
        self.provider = DemoWidgetProvider()

        # Create MultiSplit widget
        self.multisplit = MultisplitWidget(provider=self.provider)
        self.setCentralWidget(self.multisplit)

        # Initialize with editor
        self.multisplit.initialize_empty("editor:main.py")

        # Setup UI
        self.setup_toolbar()
        self.setup_menubar()
        self.setup_statusbar()

        # Connect signals
        self.multisplit.pane_added.connect(self.on_pane_added)
        self.multisplit.pane_removed.connect(self.on_pane_removed)
        self.multisplit.pane_focused.connect(self.on_pane_focused)
        self.multisplit.validation_failed.connect(self.on_validation_failed)

        # Show initial status
        self.update_status()

    def setup_toolbar(self):
        """Set up toolbar with actions."""
        toolbar = QToolBar("Main")
        self.addToolBar(toolbar)

        # Split actions
        split_right = QAction("Split →", self)
        split_right.triggered.connect(lambda: self.split_current(WherePosition.RIGHT))
        toolbar.addAction(split_right)

        split_down = QAction("Split ↓", self)
        split_down.triggered.connect(lambda: self.split_current(WherePosition.BOTTOM))
        toolbar.addAction(split_down)

        split_left = QAction("Split ←", self)
        split_left.triggered.connect(lambda: self.split_current(WherePosition.LEFT))
        toolbar.addAction(split_left)

        split_up = QAction("Split ↑", self)
        split_up.triggered.connect(lambda: self.split_current(WherePosition.TOP))
        toolbar.addAction(split_up)

        toolbar.addSeparator()

        # Remove action
        remove = QAction("Remove Pane", self)
        remove.setShortcut(QKeySequence("Ctrl+W"))
        remove.triggered.connect(self.remove_current)
        toolbar.addAction(remove)

        toolbar.addSeparator()

        # Undo/Redo
        undo = QAction("Undo", self)
        undo.setShortcut(QKeySequence.StandardKey.Undo)
        undo.triggered.connect(self.multisplit.undo)
        toolbar.addAction(undo)

        redo = QAction("Redo", self)
        redo.setShortcut(QKeySequence.StandardKey.Redo)
        redo.triggered.connect(self.multisplit.redo)
        toolbar.addAction(redo)

        toolbar.addSeparator()

        # Save/Load
        save = QAction("Save Layout", self)
        save.triggered.connect(self.save_layout)
        toolbar.addAction(save)

        load = QAction("Load Layout", self)
        load.triggered.connect(self.load_layout)
        toolbar.addAction(load)

    def setup_menubar(self):
        """Set up menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        save_action = QAction("&Save Layout", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_layout)
        file_menu.addAction(save_action)

        load_action = QAction("&Load Layout", self)
        load_action.setShortcut(QKeySequence.StandardKey.Open)
        load_action.triggered.connect(self.load_layout)
        file_menu.addAction(load_action)

        file_menu.addSeparator()

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        # Widget type submenu
        widget_menu = view_menu.addMenu("Split with...")

        editor_action = QAction("Editor", self)
        editor_action.triggered.connect(
            lambda: self.split_with_type("editor:untitled.py")
        )
        widget_menu.addAction(editor_action)

        terminal_action = QAction("Terminal", self)
        terminal_action.triggered.connect(
            lambda: self.split_with_type("terminal:1")
        )
        widget_menu.addAction(terminal_action)

        preview_action = QAction("Preview", self)
        preview_action.triggered.connect(
            lambda: self.split_with_type("preview:document")
        )
        widget_menu.addAction(preview_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        keys_action = QAction("&Keyboard Shortcuts", self)
        keys_action.triggered.connect(self.show_shortcuts)
        help_menu.addAction(keys_action)

    def setup_statusbar(self):
        """Set up status bar."""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Pane count label
        self.pane_count_label = QLabel("Panes: 1")
        self.statusbar.addWidget(self.pane_count_label)

        # Focus label
        self.focus_label = QLabel("Focus: -")
        self.statusbar.addWidget(self.focus_label)

        # Undo/redo status
        self.undo_label = QLabel("")
        self.statusbar.addPermanentWidget(self.undo_label)

    def split_current(self, position: WherePosition):
        """Split current pane."""
        current = self.multisplit.get_focused_pane()
        if not current:
            panes = self.multisplit.get_pane_ids()
            if panes:
                current = panes[0]

        if current:
            # Determine widget type based on position
            if position in (WherePosition.LEFT, WherePosition.RIGHT):
                widget_id = "editor:split.py"
            else:
                widget_id = "terminal:2"

            success = self.multisplit.split_pane(
                current, widget_id, position, 0.5
            )
            if success:
                self.update_status()

    def split_with_type(self, widget_id: str):
        """Split with specific widget type."""
        current = self.multisplit.get_focused_pane()
        if current:
            self.multisplit.split_pane(
                current, widget_id, WherePosition.RIGHT, 0.5
            )
            self.update_status()

    def remove_current(self):
        """Remove current pane."""
        current = self.multisplit.get_focused_pane()
        if current:
            if len(self.multisplit.get_pane_ids()) > 1:
                self.multisplit.remove_pane(current)
                self.update_status()
            else:
                self.statusbar.showMessage("Cannot remove last pane", 2000)

    def save_layout(self):
        """Save layout to file."""
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Layout", "", "JSON Files (*.json)"
        )
        if filepath:
            if self.multisplit.save_layout(Path(filepath)):
                self.statusbar.showMessage(f"Layout saved to {filepath}", 3000)
            else:
                QMessageBox.warning(self, "Error", "Failed to save layout")

    def load_layout(self):
        """Load layout from file."""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Load Layout", "", "JSON Files (*.json)"
        )
        if filepath:
            if self.multisplit.load_layout(Path(filepath)):
                self.statusbar.showMessage(f"Layout loaded from {filepath}", 3000)
                self.update_status()
            else:
                QMessageBox.warning(self, "Error", "Failed to load layout")

    def update_status(self):
        """Update status bar."""
        # Pane count
        count = len(self.multisplit.get_pane_ids())
        self.pane_count_label.setText(f"Panes: {count}")

        # Undo/redo
        undo_text = "↶ Undo" if self.multisplit.can_undo() else ""
        redo_text = "↷ Redo" if self.multisplit.can_redo() else ""
        self.undo_label.setText(f"{undo_text} {redo_text}".strip())

    def on_pane_added(self, pane_id: str):
        """Handle pane added."""
        self.statusbar.showMessage(f"Pane {pane_id} added", 2000)
        self.update_status()

    def on_pane_removed(self, pane_id: str):
        """Handle pane removed."""
        self.statusbar.showMessage(f"Pane {pane_id} removed", 2000)
        self.update_status()

    def on_pane_focused(self, pane_id: str):
        """Handle pane focused."""
        self.focus_label.setText(f"Focus: {pane_id[:8]}...")

    def on_validation_failed(self, errors: list):
        """Handle validation failure."""
        if errors:
            QMessageBox.warning(
                self, "Validation Error",
                "Operation failed:\n" + "\n".join(errors)
            )

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About MultiSplit MVP",
            "<h2>MultiSplit Widget MVP</h2>"
            "<p>A production-ready recursive split-pane widget for PySide6</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Dynamic splitting in any direction</li>"
            "<li>Focus management with visual indicators</li>"
            "<li>Keyboard navigation</li>"
            "<li>Drag-to-resize dividers</li>"
            "<li>Undo/redo support</li>"
            "<li>Session persistence</li>"
            "<li>Validation system</li>"
            "<li>Widget provider pattern</li>"
            "</ul>"
            "<p><b>Architecture:</b> Strict MVC with 115+ tests</p>"
        )

    def show_shortcuts(self):
        """Show keyboard shortcuts."""
        QMessageBox.information(
            self,
            "Keyboard Shortcuts",
            "<h3>Navigation</h3>"
            "<p><b>Tab</b> - Next pane<br>"
            "<b>Shift+Tab</b> - Previous pane<br>"
            "<b>Alt+Arrow</b> - Navigate in direction</p>"
            "<h3>Operations</h3>"
            "<p><b>Ctrl+W</b> - Remove current pane<br>"
            "<b>Ctrl+Z</b> - Undo<br>"
            "<b>Ctrl+Y</b> - Redo<br>"
            "<b>Ctrl+S</b> - Save layout<br>"
            "<b>Ctrl+O</b> - Load layout</p>"
        )


def main():
    """Run the demo application."""
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle("Fusion")

    # Create and show main window
    window = DemoMainWindow()
    window.show()

    # Show welcome message
    QTimer.singleShot(500, lambda: window.statusbar.showMessage(
        "Welcome to MultiSplit MVP Demo! Try splitting panes with toolbar buttons or Tab to navigate.", 5000
    ))

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
