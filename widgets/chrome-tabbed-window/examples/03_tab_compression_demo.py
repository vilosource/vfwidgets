#!/usr/bin/env python3
"""
Tab compression demonstration.

Shows how tabs dynamically compress as more are added, mimicking Chrome browser behavior.
"""

import sys
from pathlib import Path

# Add src to path so we can import ChromeTabbedWindow
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from chrome_tabbed_window import ChromeTabbedWindow


class TabCompressionDemo(QMainWindow):
    """Demo window showing tab compression behavior."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chrome Tab Compression Demo")
        self.setGeometry(100, 100, 1000, 600)

        # Create main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create ChromeTabbedWindow
        self.tabs = ChromeTabbedWindow(self)
        self.tabs.setTabsClosable(True)

        # Add initial tabs
        for i in range(3):
            label = QLabel(f"<h2>Tab {i + 1}</h2><p>This is content for tab {i + 1}</p>")
            label.setAlignment(Qt.AlignCenter)
            self.tabs.addTab(label, f"Tab {i + 1}")

        layout.addWidget(self.tabs)

        # Control panel
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)

        # Tab count label
        self.tab_count_label = QLabel(f"Tabs: {self.tabs.count()}")
        self.tab_count_label.setMinimumWidth(80)
        control_layout.addWidget(self.tab_count_label)

        # Tab width label
        self.tab_width_label = QLabel("Tab width: ---")
        self.tab_width_label.setMinimumWidth(120)
        control_layout.addWidget(self.tab_width_label)

        # Add tab button
        add_btn = QPushButton("Add Tab")
        add_btn.clicked.connect(self.add_tab)
        control_layout.addWidget(add_btn)

        # Add multiple tabs button
        add_5_btn = QPushButton("Add 5 Tabs")
        add_5_btn.clicked.connect(lambda: [self.add_tab() for _ in range(5)])
        control_layout.addWidget(add_5_btn)

        # Remove tab button
        remove_btn = QPushButton("Remove Tab")
        remove_btn.clicked.connect(self.remove_tab)
        control_layout.addWidget(remove_btn)

        # Clear all button
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.clear_all)
        control_layout.addWidget(clear_btn)

        control_layout.addStretch()

        # Info label
        info_label = QLabel("Chrome-style: 52px min, 240px max")
        info_label.setStyleSheet("color: #666; font-style: italic;")
        control_layout.addWidget(info_label)

        layout.addWidget(control_panel)

        # Update display
        self.update_display()

        # Connect signals
        self.tabs.tabCloseRequested.connect(self.on_tab_close)

    def add_tab(self):
        """Add a new tab."""
        count = self.tabs.count()
        label = QLabel(f"<h2>Tab {count + 1}</h2><p>This is content for tab {count + 1}</p>")
        label.setAlignment(Qt.AlignCenter)
        self.tabs.addTab(label, f"Tab {count + 1}")
        self.update_display()

    def remove_tab(self):
        """Remove the last tab."""
        if self.tabs.count() > 0:
            self.tabs.removeTab(self.tabs.count() - 1)
            self.update_display()

    def clear_all(self):
        """Remove all tabs."""
        while self.tabs.count() > 0:
            self.tabs.removeTab(0)
        self.update_display()

    def on_tab_close(self, index):
        """Handle tab close request."""
        self.tabs.removeTab(index)
        self.update_display()

    def update_display(self):
        """Update the display labels."""
        count = self.tabs.count()
        self.tab_count_label.setText(f"Tabs: {count}")

        # Get actual tab width from the tab bar
        if count > 0 and hasattr(self.tabs, '_tab_bar'):
            tab_bar = self.tabs._tab_bar
            # Get the size hint which shows our calculated width
            size_hint = tab_bar.tabSizeHint(0) if count > 0 else None
            if size_hint:
                width = size_hint.width()
                self.tab_width_label.setText(f"Tab width: {width}px")

                # Add color coding based on compression state
                if width == 240:  # Max width
                    self.tab_width_label.setStyleSheet("color: green; font-weight: bold;")
                elif width == 52:  # Min width
                    self.tab_width_label.setStyleSheet("color: red; font-weight: bold;")
                else:  # Compressed
                    self.tab_width_label.setStyleSheet("color: orange; font-weight: bold;")
            else:
                self.tab_width_label.setText("Tab width: ---")
        else:
            self.tab_width_label.setText("Tab width: ---")


def main():
    """Run the tab compression demo."""
    app = QApplication(sys.argv)

    print("="*60)
    print("CHROME TAB COMPRESSION DEMO")
    print("="*60)
    print("\nThis demo shows how tabs compress as more are added:")
    print("- Few tabs (1-4): Maximum width (240px)")
    print("- Medium tabs (5-15): Dynamic compression")
    print("- Many tabs (16+): Minimum width (52px)")
    print("\nKey differences from scroll-based approaches:")
    print("- ALL tabs are always visible")
    print("- No scroll buttons needed")
    print("- Exactly like Chrome browser behavior")
    print("="*60)

    window = TabCompressionDemo()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
