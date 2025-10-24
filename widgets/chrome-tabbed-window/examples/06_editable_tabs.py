#!/usr/bin/env python3
"""
Example 06: Editable Tabs

Demonstrates the tab renaming feature introduced in v1.1.
Shows how to:
- Enable inline tab editing via double-click
- Validate tab names
- Handle rename events
- Prevent duplicate names
"""

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from chrome_tabbed_window import ChromeTabbedWindow


class EditableTabsDemo(ChromeTabbedWindow):
    """Demo showing editable tab functionality."""

    def __init__(self):
        super().__init__()

        # Window configuration
        self.setWindowTitle("Chrome Tabbed Window - Editable Tabs Demo")
        self.resize(900, 600)

        # Enable tab features
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setTabsEditable(True)  # New in v1.1!

        # Set validation callback
        self.setTabRenameValidator(self._validate_tab_name)

        # Connect to rename signals
        self.tabRenameStarted.connect(self._on_rename_started)
        self.tabRenameFinished.connect(self._on_rename_finished)
        self.tabRenameCancelled.connect(self._on_rename_cancelled)

        # Create some initial tabs
        self._create_initial_tabs()

        # Show instructions
        self._show_instructions()

    def _create_initial_tabs(self):
        """Create initial demo tabs."""
        # Tab 1: Instructions
        instructions = QTextEdit()
        instructions.setReadOnly(True)
        instructions.setHtml(
            """
            <h2>Editable Tabs Demo</h2>

            <h3>How to Use:</h3>
            <ol>
                <li><b>Double-click</b> a tab's title text to rename it</li>
                <li>Type the new name and press <b>Enter</b> to save</li>
                <li>Press <b>ESC</b> to cancel editing</li>
                <li>Try creating duplicate names (will be rejected)</li>
                <li>Try empty names (will be rejected)</li>
            </ol>

            <h3>Features Demonstrated:</h3>
            <ul>
                <li>Inline tab editing with QLineEdit overlay</li>
                <li>Validation to prevent duplicate/empty names</li>
                <li>Signals for rename events (started, finished, cancelled)</li>
                <li>Automatic text trimming</li>
                <li>Visual feedback during editing</li>
            </ul>

            <h3>Public API:</h3>
            <pre>
# Enable editing
window.setTabsEditable(True)

# Set validator
def validate(index, text):
    if not text.strip():
        return (False, "")  # Reject empty
    return (True, text.strip())
window.setTabRenameValidator(validate)

# Connect signals
window.tabRenameFinished.connect(handler)
            </pre>
            """
        )
        self.addTab(instructions, "Instructions")

        # Tab 2: Content example
        content1 = QLabel("This is Tab 1\n\nDouble-click the tab title to rename me!")
        content1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.addTab(content1, "Tab 1")

        # Tab 3: Another content example
        content2 = QTextEdit()
        content2.setPlainText(
            "This is Tab 2\n\n"
            "Try renaming this tab by double-clicking its title.\n\n"
            "Validation rules:\n"
            "- Cannot be empty\n"
            "- Cannot duplicate existing tab names\n"
            "- Automatically trimmed"
        )
        self.addTab(content2, "Tab 2")

        # Tab 4: Settings/controls
        controls = self._create_controls_widget()
        self.addTab(controls, "Settings")

    def _create_controls_widget(self) -> QWidget:
        """Create widget with controls for toggling features."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Instructions label
        info = QLabel("<h3>Feature Controls</h3><p>Toggle tab editing and other features:</p>")
        layout.addWidget(info)

        # Toggle editable button
        toggle_editable = QPushButton("Toggle Editable (Currently: ON)")
        toggle_editable.clicked.connect(lambda: self._toggle_editable(toggle_editable))
        layout.addWidget(toggle_editable)

        # Add tab button
        add_tab_btn = QPushButton("Add New Tab")
        add_tab_btn.clicked.connect(self._add_new_tab)
        layout.addWidget(add_tab_btn)

        # Event log
        self._event_log = QTextEdit()
        self._event_log.setReadOnly(True)
        self._event_log.setMaximumHeight(200)
        layout.addWidget(QLabel("<b>Event Log:</b>"))
        layout.addWidget(self._event_log)

        layout.addStretch()
        return widget

    def _toggle_editable(self, button: QPushButton):
        """Toggle tabs editable state."""
        new_state = not self.tabsEditable()
        self.setTabsEditable(new_state)
        button.setText(f"Toggle Editable (Currently: {'ON' if new_state else 'OFF'})")
        self._log_event(f"Tabs editable: {new_state}")

    def _add_new_tab(self):
        """Add a new tab."""
        count = self.count()
        label = QLabel(f"This is tab #{count}\n\nYou can rename me!")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.addTab(label, f"New Tab {count}")
        self._log_event(f"Added new tab: 'New Tab {count}'")

    def _validate_tab_name(self, index: int, proposed_text: str) -> tuple[bool, str]:
        """
        Validate proposed tab name.

        Args:
            index: Index of tab being renamed
            proposed_text: Proposed new name

        Returns:
            (is_valid, sanitized_text) tuple
        """
        # Trim whitespace
        sanitized = proposed_text.strip()

        # Reject empty names
        if not sanitized:
            self._log_event("❌ Validation failed: Empty name", error=True)
            QMessageBox.warning(
                self,
                "Invalid Name",
                "Tab name cannot be empty.",
            )
            return (False, "")

        # Check for duplicates (excluding the tab being renamed)
        for i in range(self.count()):
            if i != index and self.tabText(i) == sanitized:
                self._log_event(f"❌ Validation failed: Duplicate name '{sanitized}'", error=True)
                QMessageBox.warning(
                    self,
                    "Duplicate Name",
                    f"A tab named '{sanitized}' already exists.\nPlease choose a different name.",
                )
                return (False, "")

        # Valid!
        return (True, sanitized)

    def _on_rename_started(self, index: int):
        """Handle rename started."""
        old_name = self.tabText(index)
        self._log_event(f"📝 Editing started: Tab {index} ('{old_name}')")

    def _on_rename_finished(self, index: int, new_text: str):
        """Handle rename completed."""
        self._log_event(f"✅ Renamed: Tab {index} → '{new_text}'", success=True)

    def _on_rename_cancelled(self, index: int):
        """Handle rename cancelled."""
        old_name = self.tabText(index)
        self._log_event(f"🚫 Cancelled: Tab {index} ('{old_name}')")

    def _log_event(self, message: str, error: bool = False, success: bool = False):
        """Log an event to the event log."""
        if error:
            color = "red"
        elif success:
            color = "green"
        else:
            color = "blue"

        self._event_log.append(f'<span style="color: {color}">{message}</span>')

    def _show_instructions(self):
        """Show initial instructions dialog."""
        msg = QMessageBox(self)
        msg.setWindowTitle("Editable Tabs Demo")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(
            "<h3>Welcome to the Editable Tabs Demo!</h3>"
            "<p><b>Double-click</b> any tab title to rename it.</p>"
        )
        msg.setInformativeText(
            "• Press <b>Enter</b> to save\n"
            "• Press <b>ESC</b> to cancel\n"
            "• Empty names are rejected\n"
            "• Duplicate names are rejected\n\n"
            "Check the 'Settings' tab for more controls and event log."
        )
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()


def main():
    """Run the editable tabs demo."""
    app = QApplication(sys.argv)

    # Set application metadata
    app.setApplicationName("Editable Tabs Demo")
    app.setOrganizationName("VFWidgets")

    # Create and show demo window
    demo = EditableTabsDemo()
    demo.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
