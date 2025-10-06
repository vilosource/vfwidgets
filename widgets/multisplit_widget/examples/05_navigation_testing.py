#!/usr/bin/env python3
"""
Pane Navigation Testing - Validate Spatial Navigation Algorithm

This example creates multiple tabs with different split patterns to test
the pane navigation algorithm. It provides visual feedback and logging
to identify navigation issues.

Test Scenarios:
1. Grid Layout (2x2) - Basic 4-directional navigation
2. Complex Nested - Intelligent selection with multiple candidates
3. Horizontal Strips - Vertical-only navigation

Key Features:
- Visual focus indicators with colored borders
- Navigation test buttons for each direction
- Log panel showing navigation attempts
- Expected vs actual behavior comparison
- Keyboard shortcuts: Ctrl+Shift+Arrow keys

Usage:
- Use Ctrl+Shift+Arrow keys to navigate between panes
- Click directional buttons to test navigation
- Check log panel for expected vs actual behavior
- Switch tabs to test different layouts
"""

import sys
from pathlib import Path
from typing import Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QKeyEvent, QShowEvent
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from vfwidgets_multisplit import MultisplitWidget, WherePosition, WidgetProvider, Direction


class TestPaneWidget(QWidget):
    """Widget for a test pane with visual indicators."""

    def __init__(self, pane_id: str, label: str, position_info: str):
        super().__init__()
        self.pane_id = pane_id
        self.label = label
        self.position_info = position_info

        # Setup layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Header
        header = QLabel(f"<b>{label}</b>")
        header.setStyleSheet("font-size: 16px; color: #333;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Position info
        pos_label = QLabel(position_info)
        pos_label.setStyleSheet("font-size: 12px; color: #666;")
        pos_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(pos_label)

        # Pane ID
        id_label = QLabel(f"ID: {pane_id[:12]}...")
        id_label.setStyleSheet("font-size: 10px; color: #999;")
        id_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(id_label)

        # Text area
        self.text_area = QPlainTextEdit()
        self.text_area.setPlainText(
            f"This is {label}\n\n"
            f"Use Ctrl+Shift+Arrow keys to navigate between panes.\n\n"
            f"Focus this pane and try navigating in all directions to test "
            f"the spatial navigation algorithm."
        )
        font = QFont("Consolas", 11)
        self.text_area.setFont(font)
        layout.addWidget(self.text_area, 1)

        # Set unfocused style
        self.update_focus_style(False)

    def update_focus_style(self, focused: bool):
        """Update visual style based on focus state."""
        if focused:
            self.setStyleSheet("""
                QWidget {
                    background-color: #e3f2fd;
                    border: 4px solid #2196F3;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #fafafa;
                    border: 2px solid #e0e0e0;
                }
            """)


class TestProvider(WidgetProvider):
    """Provider for test pane widgets."""

    def __init__(self):
        self.panes: dict[str, TestPaneWidget] = {}
        self.pane_labels: dict[str, tuple[str, str]] = {}  # pane_id -> (label, position_info)

    def register_pane(self, pane_id: str, label: str, position_info: str):
        """Pre-register a pane with its label and position info."""
        self.pane_labels[pane_id] = (label, position_info)

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Create a test pane widget."""
        if pane_id in self.pane_labels:
            label, position_info = self.pane_labels[pane_id]
        else:
            label = widget_id
            position_info = "Unknown position"

        pane_widget = TestPaneWidget(pane_id, label, position_info)
        self.panes[pane_id] = pane_widget
        return pane_widget

    def get_pane_widget(self, pane_id: str) -> Optional[TestPaneWidget]:
        """Get pane widget by ID."""
        return self.panes.get(pane_id)

    def widget_closing(self, widget_id: str, pane_id: str, widget: QWidget) -> None:
        """Handle widget closing."""
        if pane_id in self.panes:
            del self.panes[pane_id]


class NavigationTestTab(QWidget):
    """A test tab with a specific layout and navigation test controls."""

    log_message = Signal(str)  # Signal for logging navigation attempts

    def __init__(self, tab_name: str, setup_func, expected_nav: dict):
        super().__init__()
        self.tab_name = tab_name
        self.expected_nav = expected_nav  # pane_label -> {direction: expected_target}

        # Create provider
        self.provider = TestProvider()

        # DON'T create multisplit yet - will be done on first show
        self.multisplit = None
        self.setup_func = setup_func
        self.setup_complete = False

        # Setup layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Placeholder - will be populated when tab is shown
        self.main_layout = main_layout

    def _create_control_panel(self) -> QWidget:
        """Create control panel with navigation buttons and expected behavior."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Title
        title = QLabel(f"<b>{self.tab_name}</b>")
        title.setStyleSheet("font-size: 14px;")
        layout.addWidget(title)

        # Navigation buttons
        nav_group = QWidget()
        nav_layout = QVBoxLayout(nav_group)
        nav_layout.setContentsMargins(0, 8, 0, 8)

        # Up button
        up_btn = QPushButton("↑ Navigate UP")
        up_btn.clicked.connect(lambda: self.test_navigation(Direction.UP))
        nav_layout.addWidget(up_btn)

        # Left and Right buttons
        h_layout = QHBoxLayout()
        left_btn = QPushButton("← LEFT")
        left_btn.clicked.connect(lambda: self.test_navigation(Direction.LEFT))
        h_layout.addWidget(left_btn)

        right_btn = QPushButton("RIGHT →")
        right_btn.clicked.connect(lambda: self.test_navigation(Direction.RIGHT))
        h_layout.addWidget(right_btn)
        nav_layout.addLayout(h_layout)

        # Down button
        down_btn = QPushButton("↓ Navigate DOWN")
        down_btn.clicked.connect(lambda: self.test_navigation(Direction.DOWN))
        nav_layout.addWidget(down_btn)

        layout.addWidget(nav_group)

        # Expected behavior display
        expected_label = QLabel("<b>Expected Navigation:</b>")
        layout.addWidget(expected_label)

        self.expected_text = QTextEdit()
        self.expected_text.setReadOnly(True)
        self.expected_text.setMaximumHeight(150)
        self.expected_text.setPlainText(self._format_expected_behavior())
        layout.addWidget(self.expected_text)

        layout.addStretch()

        return panel

    def _format_expected_behavior(self) -> str:
        """Format expected navigation behavior as text."""
        lines = []
        for pane_label, directions in sorted(self.expected_nav.items()):
            lines.append(f"{pane_label}:")
            for direction, target in sorted(directions.items()):
                lines.append(f"  {direction}: {target if target else 'none'}")
            lines.append("")
        return "\n".join(lines)

    def test_navigation(self, direction: Direction):
        """Test navigation in a direction and log results."""
        if not self.multisplit:
            self.log_message.emit("Tab not initialized yet")
            return

        current_pane_id = self.multisplit.get_focused_pane()
        if not current_pane_id:
            self.log_message.emit("No pane focused")
            return

        # Get current pane label
        current_widget = self.provider.get_pane_widget(current_pane_id)
        current_label = current_widget.label if current_widget else "Unknown"

        # Attempt navigation
        success = self.multisplit.navigate_focus(direction)

        # Get new pane label
        new_pane_id = self.multisplit.get_focused_pane()
        new_widget = self.provider.get_pane_widget(new_pane_id)
        new_label = new_widget.label if new_widget else "Unknown"

        # Check against expected
        expected_target = self.expected_nav.get(current_label, {}).get(direction.value, "none")

        if success:
            actual = new_label
        else:
            actual = current_label  # No change

        # Log result
        if expected_target == actual:
            status = "✅ PASS"
            color = "green"
        else:
            status = "❌ FAIL"
            color = "red"

        log_entry = (
            f"{status} {current_label} → {direction.value.upper()}: "
            f"Expected='{expected_target}', Actual='{actual}'"
        )
        self.log_message.emit(log_entry)

    def setup_layout_if_needed(self):
        """Setup layout if not already done."""
        if not self.setup_complete:
            print(f"[SETUP] Creating layout for {self.tab_name}")

            # Create multisplit widget
            self.multisplit = MultisplitWidget(provider=self.provider)
            self.multisplit.focus_changed.connect(self.on_focus_changed)

            # Left side: MultisplitWidget
            self.multisplit.setMinimumWidth(600)
            self.main_layout.addWidget(self.multisplit, 3)

            # Right side: Controls and log
            control_panel = self._create_control_panel()
            self.main_layout.addWidget(control_panel, 1)

            # Setup the specific split pattern for this tab
            self.setup_func(self.multisplit, self.provider)
            self.setup_complete = True
            print(f"[SETUP] Layout complete for {self.tab_name}")

    def on_focus_changed(self, old_pane_id: str, new_pane_id: str):
        """Handle focus change - update visual indicators."""
        # Update old pane style
        if old_pane_id:
            old_widget = self.provider.get_pane_widget(old_pane_id)
            if old_widget:
                old_widget.update_focus_style(False)

        # Update new pane style
        if new_pane_id:
            new_widget = self.provider.get_pane_widget(new_pane_id)
            if new_widget:
                new_widget.update_focus_style(True)


def setup_grid_layout(multisplit: MultisplitWidget, provider: TestProvider):
    """Setup 2x2 grid layout."""
    # Register pane labels
    provider.register_pane("pane_a", "Pane A", "Top-Left")
    provider.register_pane("pane_b", "Pane B", "Top-Right")
    provider.register_pane("pane_c", "Pane C", "Bottom-Left")
    provider.register_pane("pane_d", "Pane D", "Bottom-Right")

    # Create layout: A | B split, then split each into top/bottom
    multisplit.initialize_empty("pane_a")

    # Split A horizontally to create B on right
    multisplit.split_pane("pane_a", "pane_b", WherePosition.RIGHT, 0.5)

    # Split A vertically to create C below
    multisplit.split_pane("pane_a", "pane_c", WherePosition.BOTTOM, 0.5)

    # Split B vertically to create D below
    multisplit.split_pane("pane_b", "pane_d", WherePosition.BOTTOM, 0.5)


def setup_nested_layout(multisplit: MultisplitWidget, provider: TestProvider):
    """Setup complex nested layout."""
    provider.register_pane("pane_a", "Pane A", "Left (Full Height)")
    provider.register_pane("pane_b", "Pane B", "Top-Right")
    provider.register_pane("pane_c", "Pane C", "Bottom-Right")

    # Create layout: A on left, B/C stacked on right
    multisplit.initialize_empty("pane_a")

    # Split A to create B on right
    multisplit.split_pane("pane_a", "pane_b", WherePosition.RIGHT, 0.5)

    # Split B to create C below
    multisplit.split_pane("pane_b", "pane_c", WherePosition.BOTTOM, 0.5)


def setup_horizontal_strips(multisplit: MultisplitWidget, provider: TestProvider):
    """Setup horizontal strips layout."""
    provider.register_pane("pane_a", "Pane A", "Top")
    provider.register_pane("pane_b", "Pane B", "Middle")
    provider.register_pane("pane_c", "Pane C", "Bottom")

    # Create layout: A/B/C stacked vertically
    multisplit.initialize_empty("pane_a")

    # Split A to create B below
    multisplit.split_pane("pane_a", "pane_b", WherePosition.BOTTOM, 0.33)

    # Split B to create C below
    multisplit.split_pane("pane_b", "pane_c", WherePosition.BOTTOM, 0.5)


class NavigationTestWindow(QMainWindow):
    """Main window with navigation test tabs."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pane Navigation Testing - Spatial Algorithm Validation")
        self.setGeometry(100, 100, 1400, 800)

        # Create main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Instructions
        instructions = QLabel(
            "<b>Navigation Testing Instructions:</b> "
            "Use Ctrl+Shift+Arrow keys or buttons to navigate. "
            "Check log for expected vs actual behavior."
        )
        instructions.setStyleSheet("padding: 8px; background-color: #fff3cd; border: 1px solid #ffc107;")
        layout.addWidget(instructions)

        # Tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs, 3)

        # Log area
        log_label = QLabel("<b>Navigation Log:</b>")
        layout.addWidget(log_label)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMaximumHeight(150)
        self.log_area.setFont(QFont("Consolas", 10))
        layout.addWidget(self.log_area)

        # Create test tabs
        self.create_test_tabs()

        # Install event filter for keyboard shortcuts
        self.installEventFilter(self)

    def showEvent(self, event):
        """Setup first tab when window is shown."""
        super().showEvent(event)
        # Setup the first tab
        if self.tabs.count() > 0:
            first_tab = self.tabs.widget(0)
            if isinstance(first_tab, NavigationTestTab):
                first_tab.setup_layout_if_needed()

    def create_test_tabs(self):
        """Create all test tabs."""
        # Tab 1: Grid Layout
        grid_expected = {
            "Pane A": {"right": "Pane B", "down": "Pane C", "left": "none", "up": "none"},
            "Pane B": {"left": "Pane A", "down": "Pane D", "right": "none", "up": "none"},
            "Pane C": {"right": "Pane D", "up": "Pane A", "left": "none", "down": "none"},
            "Pane D": {"left": "Pane C", "up": "Pane B", "right": "none", "down": "none"},
        }
        grid_tab = NavigationTestTab("Grid Layout (2x2)", setup_grid_layout, grid_expected)
        grid_tab.log_message.connect(self.add_log_entry)
        self.tabs.addTab(grid_tab, "Tab 1: Grid 2x2")

        # Tab 2: Nested Layout
        nested_expected = {
            "Pane A": {"right": "Pane B or C", "left": "none", "up": "none", "down": "none"},
            "Pane B": {"left": "Pane A", "down": "Pane C", "right": "none", "up": "none"},
            "Pane C": {"left": "Pane A", "up": "Pane B", "right": "none", "down": "none"},
        }
        nested_tab = NavigationTestTab("Complex Nested", setup_nested_layout, nested_expected)
        nested_tab.log_message.connect(self.add_log_entry)
        self.tabs.addTab(nested_tab, "Tab 2: Nested")

        # Tab 3: Horizontal Strips
        strips_expected = {
            "Pane A": {"down": "Pane B", "up": "none", "left": "none", "right": "none"},
            "Pane B": {"up": "Pane A", "down": "Pane C", "left": "none", "right": "none"},
            "Pane C": {"up": "Pane B", "down": "none", "left": "none", "right": "none"},
        }
        strips_tab = NavigationTestTab("Horizontal Strips", setup_horizontal_strips, strips_expected)
        strips_tab.log_message.connect(self.add_log_entry)
        self.tabs.addTab(strips_tab, "Tab 3: Strips")

        # Connect tab change signal to setup layouts on demand
        self.tabs.currentChanged.connect(self.on_tab_changed)

    def on_tab_changed(self, index: int):
        """Setup layout for the newly selected tab."""
        tab = self.tabs.widget(index)
        if isinstance(tab, NavigationTestTab):
            tab.setup_layout_if_needed()

    def add_log_entry(self, message: str):
        """Add entry to log area."""
        self.log_area.append(message)

    def eventFilter(self, obj, event):
        """Handle global keyboard shortcuts."""
        if event.type() == event.Type.KeyPress:
            if event.modifiers() == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier):
                current_tab = self.tabs.currentWidget()
                if isinstance(current_tab, NavigationTestTab):
                    if event.key() == Qt.Key.Key_Left:
                        current_tab.test_navigation(Direction.LEFT)
                        return True
                    elif event.key() == Qt.Key.Key_Right:
                        current_tab.test_navigation(Direction.RIGHT)
                        return True
                    elif event.key() == Qt.Key.Key_Up:
                        current_tab.test_navigation(Direction.UP)
                        return True
                    elif event.key() == Qt.Key.Key_Down:
                        current_tab.test_navigation(Direction.DOWN)
                        return True

        return super().eventFilter(obj, event)


def main():
    """Run the navigation test example."""
    app = QApplication(sys.argv)

    print("=" * 70)
    print("PANE NAVIGATION TESTING - SPATIAL ALGORITHM VALIDATION")
    print("=" * 70)
    print()
    print("This example tests the pane navigation algorithm with 3 scenarios:")
    print()
    print("Tab 1: Grid Layout (2x2)")
    print("  - Tests basic 4-directional navigation")
    print("  - Each pane should navigate to its immediate neighbor")
    print()
    print("Tab 2: Complex Nested Layout")
    print("  - Left pane + right side split into top/bottom")
    print("  - Tests intelligent selection when multiple panes exist")
    print()
    print("Tab 3: Horizontal Strips")
    print("  - 3 panes stacked vertically")
    print("  - Tests up/down navigation, left/right should not navigate")
    print()
    print("Controls:")
    print("  - Ctrl+Shift+Arrow keys: Navigate in that direction")
    print("  - Buttons: Test specific navigation")
    print("  - Log: Shows expected vs actual behavior")
    print()
    print("Current Issue:")
    print("  Navigation uses simple tab order, not spatial awareness!")
    print("  You'll see FAIL messages for most tests.")
    print("=" * 70)
    print()

    window = NavigationTestWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
