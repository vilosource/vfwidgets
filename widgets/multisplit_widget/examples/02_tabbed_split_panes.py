#!/usr/bin/env python3
"""
Tabbed Split Panes - MultiSplit Widget Example

This example demonstrates advanced usage combining tabs with runtime splitting:
- Tab widgets within split panes
- Adding new tabs to focused pane
- Splitting panes that contain tabs
- Focus management between tabs and panes
- Moving tabs between panes

Key Learning Points:
1. Combining QTabWidget with MultiSplit panes
2. How splitting works with complex nested widgets
3. Managing focus between tabs and panes
4. Advanced WidgetProvider patterns for complex widgets

Usage:
- Tab > New Tab: Add tab to focused pane
- Split menu: Split current pane (tabs stay in original pane)
- Right-click tabs: Move tab to another pane
- Drag tabs: Reorder within pane
"""

import sys
from pathlib import Path
from typing import Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QStatusBar,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)
from vfwidgets_multisplit import MultisplitWidget
from vfwidgets_multisplit.core.types import WherePosition
from vfwidgets_multisplit.view.container import WidgetProvider


class CustomTab(QWidget):
    """Individual tab content - could be any widget."""

    content_changed = Signal(str)  # tab_id

    def __init__(self, tab_id: str, title: str, content_type: str = "text"):
        super().__init__()
        self.tab_id = tab_id
        self.title = title
        self.content_type = content_type
        self.is_modified = False

        self.setup_content()

    def setup_content(self):
        """Setup tab content based on type."""
        layout = QVBoxLayout(self)

        if self.content_type == "text":
            # Text editor tab
            self.editor = QPlainTextEdit()
            font = QFont("Consolas", 11)
            self.editor.setFont(font)
            self.editor.setPlainText(f"# {self.title}\n\nContent for {self.tab_id}")
            self.editor.textChanged.connect(self.on_content_changed)
            layout.addWidget(self.editor)

        elif self.content_type == "info":
            # Information display tab
            info_widget = QWidget()
            info_layout = QVBoxLayout(info_widget)

            title_label = QLabel(f"📋 {self.title}")
            title_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px;")

            content_label = QLabel(f"""
            <b>Tab ID:</b> {self.tab_id}<br>
            <b>Type:</b> {self.content_type}<br>
            <b>Features:</b>
            <ul>
                <li>This tab demonstrates complex widget content</li>
                <li>Multiple widgets within a single tab</li>
                <li>Interaction with the MultiSplit system</li>
                <li>Focus management</li>
            </ul>
            """)
            content_label.setWordWrap(True)
            content_label.setAlignment(Qt.AlignmentFlag.AlignTop)

            button = QPushButton("Click me!")
            button.clicked.connect(lambda: print(f"Button clicked in tab {self.tab_id}"))

            info_layout.addWidget(title_label)
            info_layout.addWidget(content_label, 1)
            info_layout.addWidget(button)

            layout.addWidget(info_widget)

        elif self.content_type == "demo":
            # Demo/testing tab
            demo_widget = QWidget()
            demo_layout = QVBoxLayout(demo_widget)

            demo_layout.addWidget(QLabel(f"🔧 Demo Tab: {self.title}"))

            # Some interactive elements
            button_layout = QHBoxLayout()
            for i in range(3):
                btn = QPushButton(f"Action {i + 1}")
                btn.clicked.connect(lambda checked, x=i: self.demo_action(x))
                button_layout.addWidget(btn)

            demo_layout.addLayout(button_layout)

            # Text area for output
            self.demo_output = QPlainTextEdit()
            self.demo_output.setMaximumHeight(100)
            self.demo_output.setPlainText("Demo output will appear here...")
            demo_layout.addWidget(self.demo_output)

            layout.addWidget(demo_widget)

    def on_content_changed(self):
        """Handle content changes."""
        if not self.is_modified:
            self.is_modified = True
            self.content_changed.emit(self.tab_id)

    def demo_action(self, action_id: int):
        """Handle demo actions."""
        self.demo_output.appendPlainText(f"Action {action_id + 1} executed in tab {self.tab_id}")

    def get_display_title(self) -> str:
        """Get display title for tab."""
        title = self.title
        if self.is_modified:
            title += " *"
        return title


class TabContainer(QTabWidget):
    """Enhanced tab widget with drag support and context menus."""

    tab_move_requested = Signal(str, str)  # tab_id, target_pane_id
    tab_focused = Signal(str)  # tab_id
    pane_split_requested = Signal(str, int)  # pane_id, position

    def __init__(self, pane_id: str):
        super().__init__()
        self.pane_id = pane_id
        self.tabs: dict[str, CustomTab] = {}

        # Setup tab widget
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)

        # Connect signals
        self.tabCloseRequested.connect(self.close_tab)
        self.currentChanged.connect(self.on_tab_changed)

        # Context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def add_tab(self, tab: CustomTab) -> int:
        """Add a tab to this container."""
        self.tabs[tab.tab_id] = tab

        # Add to tab widget
        index = self.addTab(tab, tab.get_display_title())

        # Update title when content changes
        tab.content_changed.connect(
            lambda: self.setTabText(self.indexOf(tab), tab.get_display_title())
        )

        # Focus the new tab
        self.setCurrentIndex(index)
        self.tab_focused.emit(tab.tab_id)

        return index

    def close_tab(self, index: int):
        """Close tab at index."""
        if self.count() <= 1:
            # Don't close last tab - instead ask to close pane
            reply = QMessageBox.question(
                self,
                "Close Pane",
                "This is the last tab. Close the entire pane?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                # Signal parent to close pane
                self.parent().close_pane_requested.emit(self.pane_id)
            return

        # Get tab widget and remove
        tab_widget = self.widget(index)
        if tab_widget and hasattr(tab_widget, "tab_id"):
            tab_id = tab_widget.tab_id
            if tab_id in self.tabs:
                del self.tabs[tab_id]

        self.removeTab(index)

    def on_tab_changed(self, index: int):
        """Handle tab change."""
        if index >= 0:
            tab_widget = self.widget(index)
            if tab_widget and hasattr(tab_widget, "tab_id"):
                self.tab_focused.emit(tab_widget.tab_id)

    def show_context_menu(self, position):
        """Show context menu for tabs."""
        tab_index = self.tabBar().tabAt(position)
        if tab_index < 0:
            return

        tab_widget = self.widget(tab_index)
        if not tab_widget:
            return

        menu = QMenu()

        # Split actions
        split_h = QAction("Split Pane Horizontally", self)
        split_h.triggered.connect(
            lambda: self.pane_split_requested.emit(self.pane_id, WherePosition.RIGHT)
        )
        menu.addAction(split_h)

        split_v = QAction("Split Pane Vertically", self)
        split_v.triggered.connect(
            lambda: self.pane_split_requested.emit(self.pane_id, WherePosition.BOTTOM)
        )
        menu.addAction(split_v)

        menu.addSeparator()

        # Tab actions
        new_tab = QAction("New Tab Here", self)
        new_tab.triggered.connect(self.request_new_tab)
        menu.addAction(new_tab)

        close_tab = QAction("Close Tab", self)
        close_tab.triggered.connect(lambda: self.close_tab(tab_index))
        menu.addAction(close_tab)

        menu.exec(self.mapToGlobal(position))

    def request_new_tab(self):
        """Request new tab in this pane."""
        self.parent().new_tab_requested.emit(self.pane_id)


class TabbedPaneWidget(QWidget):
    """Widget that combines tabs with pane information."""

    new_tab_requested = Signal(str)  # pane_id
    close_pane_requested = Signal(str)  # pane_id
    split_pane_requested = Signal(str, int)  # pane_id, position
    tab_focused = Signal(str, str)  # pane_id, tab_id

    def __init__(self, pane_id: str):
        super().__init__()
        self.pane_id = pane_id

        # Setup layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)

        # Pane header
        header = QFrame()
        header.setFrameStyle(QFrame.Shape.StyledPanel)
        header.setStyleSheet("""
            QFrame {
                background-color: #e8e8e8;
                border: 1px solid #ccc;
                padding: 2px;
            }
        """)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(4, 2, 4, 2)

        self.header_label = QLabel(f"📂 Pane: {pane_id[:8]}...")
        self.header_label.setStyleSheet("font-size: 10px; color: #666;")
        header_layout.addWidget(self.header_label)

        header_layout.addStretch()

        # Quick action buttons
        new_tab_btn = QPushButton("+")
        new_tab_btn.setMaximumSize(20, 20)
        new_tab_btn.setToolTip("New tab")
        new_tab_btn.clicked.connect(lambda: self.new_tab_requested.emit(self.pane_id))
        header_layout.addWidget(new_tab_btn)

        # Tab container
        self.tab_container = TabContainer(pane_id)

        # Connect signals
        self.tab_container.tab_focused.connect(
            lambda tab_id: self.tab_focused.emit(self.pane_id, tab_id)
        )
        self.tab_container.pane_split_requested.connect(self.split_pane_requested.emit)

        # Add to layout
        layout.addWidget(header)
        layout.addWidget(self.tab_container, 1)

    def add_tab(self, tab: CustomTab):
        """Add tab to this pane."""
        self.tab_container.add_tab(tab)
        self.update_header()

    def update_header(self):
        """Update header with current info."""
        tab_count = self.tab_container.count()
        current_tab = self.tab_container.currentWidget()
        current_title = current_tab.title if current_tab else "None"

        self.header_label.setText(
            f"📂 Pane: {self.pane_id[:8]}... | Tabs: {tab_count} | Current: {current_title}"
        )


class TabbedSplitProvider(WidgetProvider):
    """Provider for tabbed split panes."""

    def __init__(self):
        self.panes: dict[str, TabbedPaneWidget] = {}
        self.tab_counter = 0
        self.tab_types = ["text", "info", "demo"]

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Create a tabbed pane widget."""
        # Create tabbed pane
        pane_widget = TabbedPaneWidget(pane_id)
        self.panes[pane_id] = pane_widget

        # Parse widget_id to determine initial tabs
        if widget_id.startswith("tabs:"):
            # Format: "tabs:type1,type2,type3"
            tab_types = widget_id[5:].split(",") if len(widget_id) > 5 else ["text"]
        else:
            # Default single tab
            tab_types = ["text"]

        # Create initial tabs
        for tab_type in tab_types:
            self.create_tab_in_pane(pane_id, tab_type)

        return pane_widget

    def create_tab_in_pane(self, pane_id: str, tab_type: str = "text") -> str:
        """Create a new tab in the specified pane."""
        self.tab_counter += 1
        tab_id = f"tab-{self.tab_counter}"

        # Create tab
        title = f"{tab_type.title()} {self.tab_counter}"
        tab = CustomTab(tab_id, title, tab_type)

        # Add to pane
        if pane_id in self.panes:
            self.panes[pane_id].add_tab(tab)

        return tab_id

    def get_pane_widget(self, pane_id: str) -> Optional[TabbedPaneWidget]:
        """Get pane widget by ID."""
        return self.panes.get(pane_id)

    def widget_closing(self, widget_id: str, widget: QWidget) -> None:
        """Handle widget closing."""
        # Find pane by widget
        pane_id = None
        for pid, pane in self.panes.items():
            if pane == widget:
                pane_id = pid
                break

        if pane_id:
            del self.panes[pane_id]


class TabbedSplitWindow(QMainWindow):
    """Main window demonstrating tabbed split panes."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("MultiSplit Tabbed Panes - Advanced Runtime Splitting")
        self.setGeometry(100, 100, 1400, 900)

        # Create provider
        self.provider = TabbedSplitProvider()

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

        # Initialize with first tabbed pane
        self.multisplit.initialize_empty("tabs:text,info")

        # Connect pane-level signals
        self.connect_pane_signals()

    def connect_pane_signals(self):
        """Connect signals from existing panes."""
        for pane_widget in self.provider.panes.values():
            pane_widget.new_tab_requested.connect(self.add_tab_to_pane)
            pane_widget.close_pane_requested.connect(self.close_pane)
            pane_widget.split_pane_requested.connect(self.split_pane)
            pane_widget.tab_focused.connect(self.on_tab_focused)

    def setup_menus(self):
        """Setup application menus."""
        menubar = self.menuBar()

        # Tab menu
        tab_menu = menubar.addMenu("&Tab")

        new_text_tab = QAction("New &Text Tab", self)
        new_text_tab.setShortcut("Ctrl+T")
        new_text_tab.triggered.connect(lambda: self.add_tab_to_focused_pane("text"))
        tab_menu.addAction(new_text_tab)

        new_info_tab = QAction("New &Info Tab", self)
        new_info_tab.triggered.connect(lambda: self.add_tab_to_focused_pane("info"))
        tab_menu.addAction(new_info_tab)

        new_demo_tab = QAction("New &Demo Tab", self)
        new_demo_tab.triggered.connect(lambda: self.add_tab_to_focused_pane("demo"))
        tab_menu.addAction(new_demo_tab)

        # Split menu
        split_menu = menubar.addMenu("&Split")

        split_h = QAction("Split &Horizontally", self)
        split_h.setShortcut("Ctrl+Shift+H")
        split_h.triggered.connect(lambda: self.split_focused_pane(WherePosition.RIGHT))
        split_menu.addAction(split_h)

        split_v = QAction("Split &Vertically", self)
        split_v.setShortcut("Ctrl+Shift+V")
        split_v.triggered.connect(lambda: self.split_focused_pane(WherePosition.BOTTOM))
        split_menu.addAction(split_v)

        split_menu.addSeparator()

        close_pane = QAction("&Close Pane", self)
        close_pane.setShortcut("Ctrl+W")
        close_pane.triggered.connect(self.close_focused_pane)
        split_menu.addAction(close_pane)

    def setup_toolbar(self):
        """Setup toolbar."""
        toolbar = QToolBar("Main")
        self.addToolBar(toolbar)

        # Tab actions
        toolbar.addAction("📝 Text Tab", lambda: self.add_tab_to_focused_pane("text"))
        toolbar.addAction("📋 Info Tab", lambda: self.add_tab_to_focused_pane("info"))
        toolbar.addAction("🔧 Demo Tab", lambda: self.add_tab_to_focused_pane("demo"))

        toolbar.addSeparator()

        # Split actions
        toolbar.addAction("⬌ Split →", lambda: self.split_focused_pane(WherePosition.RIGHT))
        toolbar.addAction("⬍ Split ↓", lambda: self.split_focused_pane(WherePosition.BOTTOM))
        toolbar.addAction("❌ Close", self.close_focused_pane)

        toolbar.addSeparator()

        # Info
        toolbar.addAction("ℹ️ Info", self.show_info)

    def setup_statusbar(self):
        """Setup status bar."""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready - Add tabs and split panes as needed")

    def add_tab_to_focused_pane(self, tab_type: str = "text"):
        """Add tab to focused pane."""
        focused_pane = self.multisplit.get_focused_pane()
        if focused_pane:
            tab_id = self.provider.create_tab_in_pane(focused_pane, tab_type)
            self.statusbar.showMessage(f"Added {tab_type} tab: {tab_id}")
        else:
            self.statusbar.showMessage("No pane focused")

    def add_tab_to_pane(self, pane_id: str, tab_type: str = "text"):
        """Add tab to specific pane."""
        self.provider.create_tab_in_pane(pane_id, tab_type)
        self.statusbar.showMessage(f"Added {tab_type} tab to {pane_id[:8]}...")

    def split_focused_pane(self, position: WherePosition):
        """Split focused pane with new tabbed pane."""
        focused_pane = self.multisplit.get_focused_pane()
        if not focused_pane:
            self.statusbar.showMessage("No pane to split")
            return

        # Create new tabbed pane with initial tabs
        widget_id = "tabs:text,info"
        success = self.multisplit.split_pane(focused_pane, widget_id, position, 0.5)

        if success:
            direction = "horizontally" if position == WherePosition.RIGHT else "vertically"
            self.statusbar.showMessage(f"Split pane {direction} - created new tabbed pane")
            # Connect signals for new pane
            self.connect_pane_signals()
        else:
            self.statusbar.showMessage("Failed to split pane")

    def split_pane(self, pane_id: str, position: int):
        """Split specific pane."""
        widget_id = "tabs:text"
        success = self.multisplit.split_pane(pane_id, widget_id, WherePosition(position), 0.5)
        if success:
            self.connect_pane_signals()
            self.statusbar.showMessage(f"Split pane {pane_id[:8]}...")

    def close_focused_pane(self):
        """Close focused pane."""
        focused_pane = self.multisplit.get_focused_pane()
        if focused_pane:
            self.close_pane(focused_pane)

    def close_pane(self, pane_id: str):
        """Close specific pane."""
        success = self.multisplit.remove_pane(pane_id)
        if success:
            self.statusbar.showMessage(f"Closed pane: {pane_id[:8]}...")
        else:
            self.statusbar.showMessage("Cannot close - last pane or error")

    def show_info(self):
        """Show current state info."""
        focused = self.multisplit.get_focused_pane()
        all_panes = self.multisplit.get_pane_ids()
        total_tabs = sum(pane.tab_container.count() for pane in self.provider.panes.values())

        info = f"Focus: {focused[:8] if focused else 'None'} | Panes: {len(all_panes)} | Total tabs: {total_tabs}"
        self.statusbar.showMessage(info)

        print("\n=== TABBED SPLIT INFO ===")
        print(f"Focused pane: {focused}")
        print(f"Total panes: {len(all_panes)}")
        print(f"Total tabs: {total_tabs}")
        for pane_id, pane in self.provider.panes.items():
            print(f"  Pane {pane_id}: {pane.tab_container.count()} tabs")
        print("=========================\n")

    def on_pane_focused(self, pane_id: str):
        """Handle pane focus change."""
        pane_widget = self.provider.get_pane_widget(pane_id)
        if pane_widget:
            tab_count = pane_widget.tab_container.count()
            self.statusbar.showMessage(f"Focus: {pane_id[:8]}... ({tab_count} tabs)", 2000)

    def on_tab_focused(self, pane_id: str, tab_id: str):
        """Handle tab focus within pane."""
        print(f"Tab focused: {tab_id} in pane {pane_id}")

    def on_pane_added(self, pane_id: str):
        """Handle pane added."""
        print(f"Pane added: {pane_id}")

    def on_pane_removed(self, pane_id: str):
        """Handle pane removed."""
        print(f"Pane removed: {pane_id}")


def main():
    """Run the tabbed split panes example."""
    app = QApplication(sys.argv)

    print("=" * 70)
    print("MULTISPLIT TABBED PANES - ADVANCED RUNTIME SPLITTING")
    print("=" * 70)
    print()
    print("This example demonstrates combining tabs with runtime splitting:")
    print("• Tab widgets WITHIN split panes")
    print("• Split panes that contain multiple tabs")
    print("• Add new tabs to any focused pane")
    print("• Right-click tabs for split options")
    print()
    print("Try this:")
    print("1. Add tabs: Tab > New Text Tab (or Ctrl+T)")
    print("2. Split panes: Split > Split Horizontally")
    print("3. Add more tabs to the new pane")
    print("4. Right-click tabs for context menu options")
    print("5. Split panes with tabs - tabs stay in original pane")
    print("6. Focus different tabs and panes")
    print()
    print("Key insight: You can split complex widgets (like tab containers)")
    print("and the widget hierarchy is preserved!")
    print("=" * 70)
    print()

    window = TabbedSplitWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
