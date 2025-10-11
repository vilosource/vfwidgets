#!/usr/bin/env python3
"""
Pane Navigation Testing - Validate Spatial Navigation Algorithm

This example tests the pane navigation algorithm with different split patterns.
It provides visual feedback and logging to identify navigation issues.

Test Scenarios:
1. Grid Layout (2x2) - Basic 4-directional navigation
2. Complex Nested - Intelligent selection with multiple candidates
3. Horizontal Strips - Vertical-only navigation
4. Inverted T - Two narrow panes on top, one wide below
5. Normal T - One wide pane on top, two narrow below
6. Left T - One tall pane on left, two stacked on right
7. Right T - Two stacked panes on left, one tall on right

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
- Switch scenarios to test different layouts
"""

import sys
from pathlib import Path
from typing import Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
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
from vfwidgets_multisplit import Direction, MultisplitWidget, WherePosition, WidgetProvider


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

    def clear_registrations(self):
        """Clear all pane label registrations."""
        self.pane_labels.clear()


def setup_grid_layout(multisplit: MultisplitWidget, provider: TestProvider):
    """Setup 2x2 grid layout."""
    print("[SCENARIO] Setting up Grid Layout (2x2)")

    # Register pane labels
    provider.register_pane("pane_a", "Pane A", "Top-Left")
    provider.register_pane("pane_b", "Pane B", "Top-Right")
    provider.register_pane("pane_c", "Pane C", "Bottom-Left")
    provider.register_pane("pane_d", "Pane D", "Bottom-Right")

    # Create layout: A | B split, then split each into top/bottom
    multisplit.initialize_empty("pane_a")
    pane_ids = multisplit.get_pane_ids()
    pane_a_id = pane_ids[0]  # Get actual pane ID
    print(f"[INIT] Created pane A with ID: {pane_a_id}")

    # Split A horizontally to create B on right
    success = multisplit.split_pane(pane_a_id, "pane_b", WherePosition.RIGHT, 0.5)
    print(f"[SPLIT] A → B (RIGHT): {'SUCCESS' if success else 'FAILED'}")

    # Get pane B ID
    pane_ids = multisplit.get_pane_ids()
    pane_b_id = [p for p in pane_ids if p != pane_a_id][0] if len(pane_ids) > 1 else None
    print(f"[SPLIT] Pane B ID: {pane_b_id}")

    # Split A vertically to create C below
    success = multisplit.split_pane(pane_a_id, "pane_c", WherePosition.BOTTOM, 0.5)
    print(f"[SPLIT] A → C (BOTTOM): {'SUCCESS' if success else 'FAILED'}")

    # Split B vertically to create D below
    if pane_b_id:
        success = multisplit.split_pane(pane_b_id, "pane_d", WherePosition.BOTTOM, 0.5)
        print(f"[SPLIT] B → D (BOTTOM): {'SUCCESS' if success else 'FAILED'}")

    print(f"[SCENARIO] Grid layout complete: {len(multisplit.get_pane_ids())} panes")


def setup_nested_layout(multisplit: MultisplitWidget, provider: TestProvider):
    """Setup complex nested layout."""
    print("[SCENARIO] Setting up Complex Nested Layout")

    provider.register_pane("pane_a", "Pane A", "Left (Full Height)")
    provider.register_pane("pane_b", "Pane B", "Top-Right")
    provider.register_pane("pane_c", "Pane C", "Bottom-Right")

    # Create layout: A on left, B/C stacked on right
    multisplit.initialize_empty("pane_a")
    pane_ids = multisplit.get_pane_ids()
    pane_a_id = pane_ids[0]

    # Split A to create B on right
    multisplit.split_pane(pane_a_id, "pane_b", WherePosition.RIGHT, 0.5)

    # Get pane B ID
    pane_ids = multisplit.get_pane_ids()
    pane_b_id = [p for p in pane_ids if p != pane_a_id][0] if len(pane_ids) > 1 else None

    # Split B to create C below
    if pane_b_id:
        multisplit.split_pane(pane_b_id, "pane_c", WherePosition.BOTTOM, 0.5)

    print(f"[SCENARIO] Nested layout complete: {len(multisplit.get_pane_ids())} panes")


def setup_horizontal_strips(multisplit: MultisplitWidget, provider: TestProvider):
    """Setup horizontal strips layout."""
    print("[SCENARIO] Setting up Horizontal Strips")

    provider.register_pane("pane_a", "Pane A", "Top")
    provider.register_pane("pane_b", "Pane B", "Middle")
    provider.register_pane("pane_c", "Pane C", "Bottom")

    # Create layout: A/B/C stacked vertically
    multisplit.initialize_empty("pane_a")
    pane_ids = multisplit.get_pane_ids()
    pane_a_id = pane_ids[0]

    # Split A to create B below
    multisplit.split_pane(pane_a_id, "pane_b", WherePosition.BOTTOM, 0.33)

    # Get pane B ID
    pane_ids = multisplit.get_pane_ids()
    pane_b_id = [p for p in pane_ids if p != pane_a_id][0] if len(pane_ids) > 1 else None

    # Split B to create C below
    if pane_b_id:
        multisplit.split_pane(pane_b_id, "pane_c", WherePosition.BOTTOM, 0.5)

    print(f"[SCENARIO] Strips layout complete: {len(multisplit.get_pane_ids())} panes")


def setup_inverted_t_layout(multisplit: MultisplitWidget, provider: TestProvider):
    """Setup inverted T layout: A|B on top, C spanning bottom."""
    print("[SCENARIO] Setting up Inverted T Layout")

    provider.register_pane("pane_a", "Pane A", "Top-Left")
    provider.register_pane("pane_b", "Pane B", "Top-Right")
    provider.register_pane("pane_c", "Pane C", "Bottom (Full Width)")

    # Create layout: First split top/bottom, then split top into left/right
    multisplit.initialize_empty("pane_c")
    pane_ids = multisplit.get_pane_ids()
    pane_c_id = pane_ids[0]

    # Split C to create top section (which will be A initially)
    multisplit.split_pane(pane_c_id, "pane_a", WherePosition.TOP, 0.5)

    # Get pane A ID
    pane_ids = multisplit.get_pane_ids()
    pane_a_id = [p for p in pane_ids if p != pane_c_id][0] if len(pane_ids) > 1 else None

    # Split A horizontally to create B on the right
    if pane_a_id:
        multisplit.split_pane(pane_a_id, "pane_b", WherePosition.RIGHT, 0.5)

    print(f"[SCENARIO] Inverted T layout complete: {len(multisplit.get_pane_ids())} panes")


def setup_normal_t_layout(multisplit: MultisplitWidget, provider: TestProvider):
    """Setup normal T layout: A spanning top, B|C on bottom."""
    print("[SCENARIO] Setting up Normal T Layout")

    provider.register_pane("pane_a", "Pane A", "Top (Full Width)")
    provider.register_pane("pane_b", "Pane B", "Bottom-Left")
    provider.register_pane("pane_c", "Pane C", "Bottom-Right")

    # Create layout: First split top/bottom, then split bottom into left/right
    multisplit.initialize_empty("pane_a")
    pane_ids = multisplit.get_pane_ids()
    pane_a_id = pane_ids[0]

    # Split A to create bottom section (which will be B initially)
    multisplit.split_pane(pane_a_id, "pane_b", WherePosition.BOTTOM, 0.5)

    # Get pane B ID
    pane_ids = multisplit.get_pane_ids()
    pane_b_id = [p for p in pane_ids if p != pane_a_id][0] if len(pane_ids) > 1 else None

    # Split B horizontally to create C on the right
    if pane_b_id:
        multisplit.split_pane(pane_b_id, "pane_c", WherePosition.RIGHT, 0.5)

    print(f"[SCENARIO] Normal T layout complete: {len(multisplit.get_pane_ids())} panes")


def setup_left_t_layout(multisplit: MultisplitWidget, provider: TestProvider):
    """Setup left T layout: A spanning left, B/C stacked on right."""
    print("[SCENARIO] Setting up Left T Layout")

    provider.register_pane("pane_a", "Pane A", "Left (Full Height)")
    provider.register_pane("pane_b", "Pane B", "Top-Right")
    provider.register_pane("pane_c", "Pane C", "Bottom-Right")

    # Create layout: First split left/right, then split right into top/bottom
    multisplit.initialize_empty("pane_a")
    pane_ids = multisplit.get_pane_ids()
    pane_a_id = pane_ids[0]

    # Split A to create right section (which will be B initially)
    multisplit.split_pane(pane_a_id, "pane_b", WherePosition.RIGHT, 0.5)

    # Get pane B ID
    pane_ids = multisplit.get_pane_ids()
    pane_b_id = [p for p in pane_ids if p != pane_a_id][0] if len(pane_ids) > 1 else None

    # Split B vertically to create C on the bottom
    if pane_b_id:
        multisplit.split_pane(pane_b_id, "pane_c", WherePosition.BOTTOM, 0.5)

    print(f"[SCENARIO] Left T layout complete: {len(multisplit.get_pane_ids())} panes")


def setup_right_t_layout(multisplit: MultisplitWidget, provider: TestProvider):
    """Setup right T layout: B/C stacked on left, A spanning right."""
    print("[SCENARIO] Setting up Right T Layout")

    provider.register_pane("pane_a", "Pane A", "Right (Full Height)")
    provider.register_pane("pane_b", "Pane B", "Top-Left")
    provider.register_pane("pane_c", "Pane C", "Bottom-Left")

    # Create layout: First split left/right, then split left into top/bottom
    multisplit.initialize_empty("pane_a")
    pane_ids = multisplit.get_pane_ids()
    pane_a_id = pane_ids[0]

    # Split A to create left section (which will be B initially)
    multisplit.split_pane(pane_a_id, "pane_b", WherePosition.LEFT, 0.5)

    # Get pane B ID
    pane_ids = multisplit.get_pane_ids()
    pane_b_id = [p for p in pane_ids if p != pane_a_id][0] if len(pane_ids) > 1 else None

    # Split B vertically to create C on the bottom
    if pane_b_id:
        multisplit.split_pane(pane_b_id, "pane_c", WherePosition.BOTTOM, 0.5)

    print(f"[SCENARIO] Right T layout complete: {len(multisplit.get_pane_ids())} panes")


class NavigationTestWindow(QMainWindow):
    """Main window with navigation test scenarios."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pane Navigation Testing - Spatial Algorithm Validation")
        self.setGeometry(100, 100, 1400, 800)

        # Create provider and multisplit (SINGLE instance following Example 01 pattern)
        self.provider = TestProvider()
        self.multisplit = MultisplitWidget(provider=self.provider)
        self.multisplit.setMinimumWidth(600)

        # Connect focus change signal
        self.multisplit.focus_changed.connect(self.on_focus_changed)

        # Setup scenarios
        self.scenarios = [
            {
                "name": "Grid Layout (2x2)",
                "setup_func": setup_grid_layout,
                "expected_nav": {
                    "Pane A": {"right": "Pane B", "down": "Pane C", "left": "none", "up": "none"},
                    "Pane B": {"left": "Pane A", "down": "Pane D", "right": "none", "up": "none"},
                    "Pane C": {"right": "Pane D", "up": "Pane A", "left": "none", "down": "none"},
                    "Pane D": {"left": "Pane C", "up": "Pane B", "right": "none", "down": "none"},
                },
            },
            {
                "name": "Complex Nested",
                "setup_func": setup_nested_layout,
                "expected_nav": {
                    "Pane A": {
                        "right": "Pane B or C",
                        "left": "none",
                        "up": "none",
                        "down": "none",
                    },
                    "Pane B": {"left": "Pane A", "down": "Pane C", "right": "none", "up": "none"},
                    "Pane C": {"left": "Pane A", "up": "Pane B", "right": "none", "down": "none"},
                },
            },
            {
                "name": "Horizontal Strips",
                "setup_func": setup_horizontal_strips,
                "expected_nav": {
                    "Pane A": {"down": "Pane B", "up": "none", "left": "none", "right": "none"},
                    "Pane B": {"up": "Pane A", "down": "Pane C", "left": "none", "right": "none"},
                    "Pane C": {"up": "Pane B", "down": "none", "left": "none", "right": "none"},
                },
            },
            {
                "name": "Inverted T",
                "setup_func": setup_inverted_t_layout,
                "expected_nav": {
                    "Pane A": {"right": "Pane B", "down": "Pane C", "left": "none", "up": "none"},
                    "Pane B": {"left": "Pane A", "down": "Pane C", "right": "none", "up": "none"},
                    "Pane C": {
                        "up": "Pane A or B",
                        "down": "none",
                        "left": "none",
                        "right": "none",
                    },
                },
            },
            {
                "name": "Normal T",
                "setup_func": setup_normal_t_layout,
                "expected_nav": {
                    "Pane A": {
                        "down": "Pane B or C",
                        "up": "none",
                        "left": "none",
                        "right": "none",
                    },
                    "Pane B": {"right": "Pane C", "up": "Pane A", "left": "none", "down": "none"},
                    "Pane C": {"left": "Pane B", "up": "Pane A", "right": "none", "down": "none"},
                },
            },
            {
                "name": "Left T",
                "setup_func": setup_left_t_layout,
                "expected_nav": {
                    "Pane A": {
                        "right": "Pane B or C",
                        "left": "none",
                        "up": "none",
                        "down": "none",
                    },
                    "Pane B": {"left": "Pane A", "down": "Pane C", "right": "none", "up": "none"},
                    "Pane C": {"left": "Pane A", "up": "Pane B", "right": "none", "down": "none"},
                },
            },
            {
                "name": "Right T",
                "setup_func": setup_right_t_layout,
                "expected_nav": {
                    "Pane A": {
                        "left": "Pane B or C",
                        "right": "none",
                        "up": "none",
                        "down": "none",
                    },
                    "Pane B": {"right": "Pane A", "down": "Pane C", "left": "none", "up": "none"},
                    "Pane C": {"right": "Pane A", "up": "Pane B", "left": "none", "down": "none"},
                },
            },
        ]

        self.current_scenario_index = 0

        # Create main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Instructions
        instructions = QLabel(
            "<b>Navigation Testing Instructions:</b> "
            "Use Ctrl+Shift+Arrow keys or buttons to navigate. "
            "Switch scenarios to test different layouts. "
            "Check log for expected vs actual behavior."
        )
        instructions.setStyleSheet(
            "padding: 8px; background-color: #fff3cd; border: 1px solid #ffc107;"
        )
        layout.addWidget(instructions)

        # Main content area: multisplit on left, controls on right
        content_layout = QHBoxLayout()
        layout.addLayout(content_layout, 3)

        # Left side: MultisplitWidget
        content_layout.addWidget(self.multisplit, 3)

        # Right side: Scenario selector + controls
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        content_layout.addWidget(right_panel, 1)

        # Scenario selector
        scenario_label = QLabel("<b>Test Scenarios:</b>")
        right_layout.addWidget(scenario_label)

        self.scenario_tabs = QTabWidget()
        for _i, scenario in enumerate(self.scenarios):
            tab = self._create_scenario_tab(scenario)
            self.scenario_tabs.addTab(tab, scenario["name"])

        self.scenario_tabs.currentChanged.connect(self.on_scenario_changed)
        right_layout.addWidget(self.scenario_tabs)

        # Log area
        log_label = QLabel("<b>Navigation Log:</b>")
        layout.addWidget(log_label)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMaximumHeight(150)
        self.log_area.setFont(QFont("Consolas", 10))
        layout.addWidget(self.log_area)

        # Install event filter for keyboard shortcuts
        self.installEventFilter(self)

        # Initialize first scenario
        self.load_scenario(0)

    def _create_scenario_tab(self, scenario: dict) -> QWidget:
        """Create control panel for a scenario."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

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

        expected_text = QTextEdit()
        expected_text.setReadOnly(True)
        expected_text.setPlainText(self._format_expected_behavior(scenario["expected_nav"]))
        layout.addWidget(expected_text)

        layout.addStretch()

        return panel

    def _format_expected_behavior(self, expected_nav: dict) -> str:
        """Format expected navigation behavior as text."""
        lines = []
        for pane_label, directions in sorted(expected_nav.items()):
            lines.append(f"{pane_label}:")
            for direction, target in sorted(directions.items()):
                lines.append(f"  {direction}: {target if target else 'none'}")
            lines.append("")
        return "\n".join(lines)

    def load_scenario(self, index: int):
        """Load a test scenario by rebuilding the layout."""
        print(f"\n{'=' * 70}")
        print(f"Loading Scenario {index + 1}: {self.scenarios[index]['name']}")
        print(f"{'=' * 70}")

        self.current_scenario_index = index
        scenario = self.scenarios[index]

        # Clear current panes (following Example 01 pattern)
        current_panes = list(self.multisplit.get_pane_ids())
        print(f"[CLEAR] Removing {len(current_panes)} existing panes")
        for pane_id in current_panes:
            self.multisplit.remove_pane(pane_id)

        # Clear provider registrations
        self.provider.clear_registrations()

        # Build new layout
        scenario["setup_func"](self.multisplit, self.provider)

        print(f"{'=' * 70}\n")

    def on_scenario_changed(self, index: int):
        """Handle scenario tab change."""
        self.load_scenario(index)

    def test_navigation(self, direction: Direction):
        """Test navigation in a direction and log results."""
        current_pane_id = self.multisplit.get_focused_pane()
        if not current_pane_id:
            self.log_area.append("No pane focused")
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
        scenario = self.scenarios[self.current_scenario_index]
        expected_target = (
            scenario["expected_nav"].get(current_label, {}).get(direction.value, "none")
        )

        if success:
            actual = new_label
        else:
            actual = current_label  # No change

        # Log result
        if expected_target == actual:
            status = "✅ PASS"
        else:
            status = "❌ FAIL"

        log_entry = (
            f"{status} {current_label} → {direction.value.upper()}: "
            f"Expected='{expected_target}', Actual='{actual}'"
        )
        self.log_area.append(log_entry)
        print(log_entry)

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

    def eventFilter(self, obj, event):
        """Handle global keyboard shortcuts."""
        if event.type() == event.Type.KeyPress:
            if event.modifiers() == (
                Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier
            ):
                if event.key() == Qt.Key.Key_Left:
                    self.test_navigation(Direction.LEFT)
                    return True
                elif event.key() == Qt.Key.Key_Right:
                    self.test_navigation(Direction.RIGHT)
                    return True
                elif event.key() == Qt.Key.Key_Up:
                    self.test_navigation(Direction.UP)
                    return True
                elif event.key() == Qt.Key.Key_Down:
                    self.test_navigation(Direction.DOWN)
                    return True

        return super().eventFilter(obj, event)


def main():
    """Run the navigation test example."""
    app = QApplication(sys.argv)

    print("=" * 70)
    print("PANE NAVIGATION TESTING - SPATIAL ALGORITHM VALIDATION")
    print("=" * 70)
    print()
    print("This example tests the pane navigation algorithm with 7 scenarios:")
    print()
    print("Scenario 1: Grid Layout (2x2)")
    print("  - Tests basic 4-directional navigation")
    print("  - Each pane should navigate to its immediate neighbor")
    print()
    print("Scenario 2: Complex Nested Layout")
    print("  - Left pane + right side split into top/bottom")
    print("  - Tests intelligent selection when multiple panes exist")
    print()
    print("Scenario 3: Horizontal Strips")
    print("  - 3 panes stacked vertically")
    print("  - Tests up/down navigation, left/right should not navigate")
    print()
    print("Scenario 4: Inverted T Layout")
    print("  - Two panes on top (A|B), one spanning bottom (C)")
    print("  - Tests navigation when one pane spans multiple columns")
    print()
    print("Scenario 5: Normal T Layout")
    print("  - One pane on top (A), two panes on bottom (B|C)")
    print("  - Tests navigation from wide pane to multiple candidates below")
    print()
    print("Scenario 6: Left T Layout")
    print("  - One pane on left (A), two panes stacked on right (B/C)")
    print("  - Tests navigation from tall pane to multiple candidates on right")
    print()
    print("Scenario 7: Right T Layout")
    print("  - Two panes stacked on left (B/C), one pane on right (A)")
    print("  - Tests navigation from tall pane to multiple candidates on left")
    print()
    print("Controls:")
    print("  - Ctrl+Shift+Arrow keys: Navigate in that direction")
    print("  - Buttons: Test specific navigation")
    print("  - Scenario tabs: Switch between test layouts")
    print("  - Log: Shows expected vs actual behavior")
    print()
    print("Current Issue:")
    print("  Navigation uses simple tab order, not spatial awareness!")
    print("  You'll see FAIL messages for most 2D grid tests.")
    print("=" * 70)
    print()

    window = NavigationTestWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
