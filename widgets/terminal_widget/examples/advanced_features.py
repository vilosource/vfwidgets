#!/usr/bin/env python3
"""Advanced terminal widget features example.

This example demonstrates advanced features of the TerminalWidget including:
- Multiple terminals in tabs
- Programmatic control (send commands, clear, reset)
- Output capture and processing
- Custom themes
- Signal handling
"""

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from vfwidgets_terminal import TerminalWidget


class AdvancedTerminalWindow(QMainWindow):
    """Advanced example window with multiple terminals and controls."""

    def __init__(self):
        """Initialize the advanced terminal window."""
        super().__init__()
        self.setWindowTitle("Terminal Widget - Advanced Features")
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create splitter for terminal and output
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Left side: Terminals
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Tab widget for multiple terminals
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        left_layout.addWidget(self.tab_widget)

        # Add initial terminals
        self.add_terminal("Bash", command="bash")
        self.add_terminal("Python", command="python", args=["-i"])

        splitter.addWidget(left_widget)

        # Right side: Output and controls
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Output capture display
        output_group = QGroupBox("Captured Output")
        output_layout = QVBoxLayout(output_group)
        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        self.output_display.setMaximumHeight(200)
        output_layout.addWidget(self.output_display)
        right_layout.addWidget(output_group)

        # Controls
        controls_group = QGroupBox("Terminal Controls")
        controls_layout = QVBoxLayout(controls_group)

        # Command input
        command_layout = QHBoxLayout()
        self.command_input = QTextEdit()
        self.command_input.setPlaceholderText("Enter command to send...")
        self.command_input.setMaximumHeight(60)
        command_layout.addWidget(self.command_input)

        send_btn = QPushButton("Send Command")
        send_btn.clicked.connect(self.send_command)
        command_layout.addWidget(send_btn)
        controls_layout.addLayout(command_layout)

        # Terminal actions
        actions_layout = QHBoxLayout()

        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_terminal)
        actions_layout.addWidget(clear_btn)

        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_terminal)
        actions_layout.addWidget(reset_btn)

        save_btn = QPushButton("Save Output")
        save_btn.clicked.connect(self.save_output)
        actions_layout.addWidget(save_btn)

        controls_layout.addLayout(actions_layout)

        # Options
        options_layout = QHBoxLayout()

        # Theme selector
        options_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        options_layout.addWidget(self.theme_combo)

        # Read-only mode
        self.readonly_check = QCheckBox("Read-only")
        self.readonly_check.toggled.connect(self.toggle_readonly)
        options_layout.addWidget(self.readonly_check)

        # Capture output
        self.capture_check = QCheckBox("Capture Output")
        self.capture_check.setChecked(True)
        options_layout.addWidget(self.capture_check)

        options_layout.addStretch()
        controls_layout.addLayout(options_layout)

        right_layout.addWidget(controls_group)

        # Status
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(status_group)
        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)
        right_layout.addWidget(status_group)

        right_layout.addStretch()
        splitter.addWidget(right_widget)

        # Set splitter sizes
        splitter.setSizes([800, 400])

        # Add terminal button
        add_terminal_layout = QHBoxLayout()
        add_bash_btn = QPushButton("+ New Bash Terminal")
        add_bash_btn.clicked.connect(lambda: self.add_terminal("Bash", "bash"))
        add_terminal_layout.addWidget(add_bash_btn)

        add_python_btn = QPushButton("+ New Python Terminal")
        add_python_btn.clicked.connect(lambda: self.add_terminal("Python", "python", ["-i"]))
        add_terminal_layout.addWidget(add_python_btn)

        add_terminal_layout.addStretch()
        layout.addLayout(add_terminal_layout)

    def add_terminal(self, name: str, command: str, args: list = None):
        """Add a new terminal tab."""
        # Create terminal with output capture
        terminal = TerminalWidget(
            command=command, args=args, capture_output=self.capture_check.isChecked(), debug=True
        )

        # Connect signals
        terminal.terminal_ready.connect(lambda: self.update_status(f"Terminal '{name}' ready"))
        terminal.output_received.connect(self.handle_output)
        terminal.terminal_closed.connect(
            lambda code: self.update_status(f"Terminal '{name}' closed with code {code}")
        )

        # Add to tabs
        index = self.tab_widget.addTab(terminal, name)
        self.tab_widget.setCurrentIndex(index)

    def close_tab(self, index: int):
        """Close a terminal tab."""
        if self.tab_widget.count() > 1:
            widget = self.tab_widget.widget(index)
            if isinstance(widget, TerminalWidget):
                widget.close_terminal()
            self.tab_widget.removeTab(index)

    def get_current_terminal(self) -> TerminalWidget:
        """Get the currently selected terminal."""
        widget = self.tab_widget.currentWidget()
        if isinstance(widget, TerminalWidget):
            return widget
        return None

    def send_command(self):
        """Send command to current terminal."""
        terminal = self.get_current_terminal()
        if terminal:
            command = self.command_input.toPlainText().strip()
            if command:
                terminal.send_command(command)
                self.command_input.clear()
                self.update_status(f"Sent: {command}")

    def clear_terminal(self):
        """Clear current terminal."""
        terminal = self.get_current_terminal()
        if terminal:
            terminal.clear()
            self.update_status("Terminal cleared")

    def reset_terminal(self):
        """Reset current terminal."""
        terminal = self.get_current_terminal()
        if terminal:
            terminal.reset()
            self.update_status("Terminal reset")

    def save_output(self):
        """Save terminal output to file."""
        terminal = self.get_current_terminal()
        if terminal and terminal.capture_output:
            from PySide6.QtWidgets import QFileDialog

            filename, _ = QFileDialog.getSaveFileName(self, "Save Output", "", "Text Files (*.txt)")
            if filename:
                terminal.save_output(filename)
                self.update_status(f"Output saved to {filename}")

    def change_theme(self, theme: str):
        """Change terminal theme."""
        # This would apply to new terminals
        # For existing terminals, we'd need to reload them
        self.update_status(f"Theme changed to {theme}")

    def toggle_readonly(self, checked: bool):
        """Toggle read-only mode."""
        terminal = self.get_current_terminal()
        if terminal:
            terminal.set_read_only(checked)
            self.update_status(f"Read-only: {checked}")

    def handle_output(self, data: str):
        """Handle output from terminal."""
        # Display in output window
        self.output_display.append(data.strip())

        # Scroll to bottom
        scrollbar = self.output_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def update_status(self, message: str):
        """Update status label."""
        self.status_label.setText(message)
        print(f"Status: {message}")


def main():
    """Run the advanced terminal example."""
    app = QApplication(sys.argv)
    app.setApplicationName("VFWidgets Terminal - Advanced Example")

    window = AdvancedTerminalWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
