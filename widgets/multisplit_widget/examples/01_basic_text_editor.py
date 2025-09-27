#!/usr/bin/env python3
"""
Basic Multi-Document Text Editor - MultiSplit Widget Example

This example demonstrates the core strength of MultiSplit widget:
- Dynamic runtime pane splitting
- Multiple text editors in different panes
- Focus management between editors
- Basic file operations

Key Learning Points:
1. How to implement a WidgetProvider for text editors
2. Runtime pane splitting with user interaction
3. Managing multiple document instances
4. Focus handling between different editors

Usage:
- File > New Document: Creates new editor in current pane
- Split menu: Split current editor pane horizontally/vertically
- Click between editors to change focus
- Use toolbar to see which editor is focused
"""

import sys
from pathlib import Path
from typing import Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtCore import QTimer, Signal
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QWidget,
)
from vfwidgets_multisplit import MultisplitWidget
from vfwidgets_multisplit.core.types import WherePosition
from vfwidgets_multisplit.view.container import WidgetProvider


class DocumentEditor(QPlainTextEdit):
    """Enhanced text editor for document editing."""

    document_modified = Signal(str)  # document_id

    def __init__(self, document_id: str, file_path: Optional[str] = None):
        super().__init__()
        self.document_id = document_id
        self.file_path = file_path
        self.is_modified = False

        # Setup editor
        self.setup_editor()

        # Connect signals
        self.textChanged.connect(self.on_text_changed)

        # Load file if provided
        if file_path:
            self.load_file(file_path)
        else:
            self.setPlainText("# New Document\n\nStart typing here...")
            self.is_modified = False

    def setup_editor(self):
        """Setup editor appearance and behavior."""
        # Font
        font = QFont("Consolas", 12)
        font.setFixedPitch(True)
        self.setFont(font)

        # Tab width
        self.setTabStopDistance(40)

        # Line wrapping
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)

        # Show line numbers would be nice, but keeping simple for this example

    def on_text_changed(self):
        """Handle text changes."""
        if not self.is_modified:
            self.is_modified = True
            self.document_modified.emit(self.document_id)

    def load_file(self, file_path: str) -> bool:
        """Load file content."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            self.setPlainText(content)
            self.file_path = file_path
            self.is_modified = False
            return True

        except Exception as e:
            QMessageBox.warning(self, "Load Error", f"Could not load file:\n{e}")
            return False

    def save_file(self, file_path: Optional[str] = None) -> bool:
        """Save file content."""
        if file_path:
            self.file_path = file_path

        if not self.file_path:
            return False

        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(self.toPlainText())

            self.is_modified = False
            return True

        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Could not save file:\n{e}")
            return False

    def get_display_name(self) -> str:
        """Get display name for this document."""
        if self.file_path:
            name = Path(self.file_path).name
        else:
            name = f"Document-{self.document_id}"

        if self.is_modified:
            name += " *"

        return name


class TextEditorProvider(WidgetProvider):
    """Provides text editor widgets for MultiSplit panes."""

    def __init__(self):
        self.editors: dict[str, DocumentEditor] = {}
        self.document_counter = 0

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Create a text editor widget."""
        # Create container with editor info
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(2, 2, 2, 2)

        # Header with document info
        header = QLabel()
        header.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                padding: 4px 8px;
                font-size: 10px;
                color: #666;
            }
        """)

        # Create document editor
        if widget_id.startswith("file:"):
            # Loading existing file
            file_path = widget_id[5:]  # Remove "file:" prefix
            editor = DocumentEditor(widget_id, file_path)
            header.setText(f"📄 {editor.get_display_name()} | Pane: {pane_id[:8]}")
        else:
            # New document
            editor = DocumentEditor(widget_id)
            header.setText(f"📝 {editor.get_display_name()} | Pane: {pane_id[:8]}")

        # Store editor reference
        self.editors[widget_id] = editor

        # Update header when document changes
        editor.document_modified.connect(
            lambda: header.setText(f"📝 {editor.get_display_name()} | Pane: {pane_id[:8]}")
        )

        # Add to layout
        layout.addWidget(header)
        layout.addWidget(editor, 1)

        return container

    def get_editor(self, widget_id: str) -> Optional[DocumentEditor]:
        """Get editor by widget ID."""
        return self.editors.get(widget_id)

    def create_new_document(self) -> str:
        """Create a new document ID."""
        self.document_counter += 1
        return f"doc-{self.document_counter}"

    def widget_closing(self, widget_id: str, widget: QWidget) -> None:
        """Handle widget closing."""
        if widget_id in self.editors:
            editor = self.editors[widget_id]

            # Check if modified and ask to save
            if editor.is_modified:
                reply = QMessageBox.question(
                    widget,
                    "Unsaved Changes",
                    f"Document '{editor.get_display_name()}' has unsaved changes.\nSave before closing?",
                    QMessageBox.StandardButton.Save
                    | QMessageBox.StandardButton.Discard
                    | QMessageBox.StandardButton.Cancel,
                )

                if reply == QMessageBox.StandardButton.Save:
                    if not editor.file_path:
                        # Need to get save location
                        file_path, _ = QFileDialog.getSaveFileName(
                            widget, "Save Document", "", "Text Files (*.txt);;All Files (*)"
                        )
                        if file_path:
                            editor.save_file(file_path)
                    else:
                        editor.save_file()
                elif reply == QMessageBox.StandardButton.Cancel:
                    return  # Don't close

            # Remove from tracking
            del self.editors[widget_id]


class TextEditorWindow(QMainWindow):
    """Main window demonstrating runtime pane splitting with text editors."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("MultiSplit Text Editor - Runtime Splitting Demo")
        self.setGeometry(100, 100, 1200, 800)

        # Create provider
        self.provider = TextEditorProvider()

        # Create MultiSplit widget
        self.multisplit = MultisplitWidget(provider=self.provider)
        self.setCentralWidget(self.multisplit)

        # Setup UI
        self.setup_menus()
        self.setup_toolbar()
        self.setup_statusbar()

        # Connect signals
        self.multisplit.pane_focused.connect(self.on_pane_focused)
        self.multisplit.pane_added.connect(self.on_pane_added)
        self.multisplit.pane_removed.connect(self.on_pane_removed)

        # Initialize with first document
        self.create_new_document()

        # Update display timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(1000)  # Update every second

    def setup_menus(self):
        """Setup application menus."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        new_action = QAction("&New Document", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.create_new_document)
        file_menu.addAction(new_action)

        open_action = QAction("&Open File...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_current)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_as_current)
        file_menu.addAction(save_as_action)

        # Split menu - This demonstrates the core runtime splitting capability!
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

        # New document
        toolbar.addAction("📄 New", self.create_new_document)
        toolbar.addAction("📁 Open", self.open_file)
        toolbar.addAction("💾 Save", self.save_current)

        toolbar.addSeparator()

        # Split actions - Core feature!
        toolbar.addAction("⬌ Split →", lambda: self.split_current_pane(WherePosition.RIGHT))
        toolbar.addAction("⬍ Split ↓", lambda: self.split_current_pane(WherePosition.BOTTOM))
        toolbar.addAction("❌ Close", self.close_current_pane)

        toolbar.addSeparator()

        # Info
        toolbar.addAction("ℹ️ Focus Info", self.show_focus_info)

    def setup_statusbar(self):
        """Setup status bar."""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready - Create and split text editors as needed")

    def create_new_document(self):
        """Create new document in focused pane or first available."""
        focused_pane = self.multisplit.get_focused_pane()

        if not focused_pane:
            # No panes yet - initialize
            doc_id = self.provider.create_new_document()
            self.multisplit.initialize_empty(doc_id)
            self.statusbar.showMessage(f"Created first document: {doc_id}")
        else:
            # Create new document in current pane
            doc_id = self.provider.create_new_document()
            # Replace current pane content
            if self.multisplit.remove_pane(focused_pane):
                panes = self.multisplit.get_pane_ids()
                if panes:
                    # Split to add new document
                    self.multisplit.split_pane(panes[0], doc_id, WherePosition.RIGHT, 0.5)
                else:
                    # Initialize if no panes left
                    self.multisplit.initialize_empty(doc_id)
                self.statusbar.showMessage(f"Created new document: {doc_id}")

    def open_file(self):
        """Open file in new document."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "Text Files (*.txt);;Python Files (*.py);;All Files (*)"
        )

        if file_path:
            # Create widget ID for file
            widget_id = f"file:{file_path}"

            focused_pane = self.multisplit.get_focused_pane()
            if focused_pane:
                # Split current pane to add file
                success = self.multisplit.split_pane(
                    focused_pane, widget_id, WherePosition.RIGHT, 0.5
                )
                if success:
                    self.statusbar.showMessage(f"Opened: {Path(file_path).name}")
                else:
                    self.statusbar.showMessage("Failed to split pane")
            else:
                # Initialize with file
                self.multisplit.initialize_empty(widget_id)
                self.statusbar.showMessage(f"Opened: {Path(file_path).name}")

    def save_current(self):
        """Save currently focused document."""
        focused_pane = self.multisplit.get_focused_pane()
        if not focused_pane:
            self.statusbar.showMessage("No document focused")
            return

        # Find the widget ID for this pane
        # This is a limitation of current API - we need to track pane->widget mapping
        # For this demo, we'll show the concept
        self.statusbar.showMessage("Save functionality - would save focused document")

    def save_as_current(self):
        """Save as currently focused document."""
        self.statusbar.showMessage("Save As functionality - would save focused document as...")

    def split_current_pane(self, position: WherePosition):
        """Split the currently focused pane - CORE FEATURE!"""
        focused_pane = self.multisplit.get_focused_pane()

        if not focused_pane:
            self.statusbar.showMessage("No pane to split")
            return

        # Create new document for the split
        doc_id = self.provider.create_new_document()

        # Perform the split - this is the key capability!
        success = self.multisplit.split_pane(focused_pane, doc_id, position, 0.5)

        if success:
            direction = "horizontally" if position == WherePosition.RIGHT else "vertically"
            self.statusbar.showMessage(f"Split pane {direction} - added {doc_id}")
        else:
            self.statusbar.showMessage("Failed to split pane")

    def close_current_pane(self):
        """Close currently focused pane."""
        focused_pane = self.multisplit.get_focused_pane()

        if not focused_pane:
            self.statusbar.showMessage("No pane to close")
            return

        success = self.multisplit.remove_pane(focused_pane)
        if success:
            self.statusbar.showMessage(f"Closed pane: {focused_pane[:8]}...")
        else:
            self.statusbar.showMessage("Cannot close - last pane or error")

    def show_focus_info(self):
        """Show information about current focus and panes."""
        focused = self.multisplit.get_focused_pane()
        all_panes = self.multisplit.get_pane_ids()

        info = f"Focus: {focused[:8] if focused else 'None'} | Total panes: {len(all_panes)}"
        self.statusbar.showMessage(info)

        print("\n=== FOCUS INFO ===")
        print(f"Focused pane: {focused}")
        print(f"All panes: {all_panes}")
        print(f"Total editors: {len(self.provider.editors)}")
        print("==================\n")

    def on_pane_focused(self, pane_id: str):
        """Handle pane focus change."""
        self.statusbar.showMessage(
            f"Focus: {pane_id[:8]}... | Use Split menu to create more panes", 2000
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
        editor_count = len(self.provider.editors)

        # Only update if we have useful info to show
        if focused:
            msg = f"Focused: {focused[:8]}... | Panes: {pane_count} | Editors: {editor_count}"
            # Only update if different from current message
            if msg != self.statusbar.currentMessage():
                self.statusbar.showMessage(msg)


def main():
    """Run the text editor example."""
    app = QApplication(sys.argv)

    print("=" * 70)
    print("MULTISPLIT TEXT EDITOR - RUNTIME SPLITTING DEMO")
    print("=" * 70)
    print()
    print("This example demonstrates the core strength of MultiSplit widget:")
    print("• DYNAMIC PANE SPLITTING at runtime")
    print("• Multiple text editors in different panes")
    print("• Focus management between editors")
    print()
    print("Try this:")
    print("1. Start typing in the initial editor")
    print("2. Split > Split Horizontally (or Ctrl+Shift+H)")
    print("3. Type in the new editor pane")
    print("4. Split > Split Vertically (or Ctrl+Shift+V)")
    print("5. Open files: File > Open File")
    print("6. Click between editors to change focus")
    print("7. Close panes: Split > Close Pane (or Ctrl+W)")
    print()
    print("Key insight: You can split ANY pane at ANY time during runtime!")
    print("=" * 70)
    print()

    window = TextEditorWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
