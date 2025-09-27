#!/usr/bin/env python3
"""
MultiSplit Widget Examples Runner

This script provides a convenient way to run and explore all MultiSplit widget examples.
Each example demonstrates progressively more advanced concepts for runtime pane splitting.
"""

import sys
from pathlib import Path

from PySide6.QtCore import QProcess, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class ExampleInfo:
    """Information about an example."""

    def __init__(
        self, file_name: str, title: str, description: str, concepts: list[str], difficulty: str
    ):
        self.file_name = file_name
        self.title = title
        self.description = description
        self.concepts = concepts
        self.difficulty = difficulty

    @property
    def file_path(self) -> Path:
        return Path(__file__).parent / self.file_name


class ExampleRunner(QMainWindow):
    """Main window for running examples."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MultiSplit Widget Examples")
        self.setGeometry(100, 100, 1000, 700)

        # Running processes
        self.running_processes: list[QProcess] = []

        # Example definitions
        self.examples = [
            ExampleInfo(
                "01_basic_text_editor.py",
                "Basic Text Editor with Runtime Splitting",
                """
                This example demonstrates the core strength of MultiSplit widget - dynamic runtime
                pane splitting. Start with a simple text editor and split it into multiple editors
                on demand during runtime.

                Perfect for beginners to understand the fundamental concept of runtime splitting.
                """,
                [
                    "Basic WidgetProvider implementation",
                    "Runtime pane splitting with user interaction",
                    "Multiple text editors in different panes",
                    "Focus management between editors",
                    "Keyboard shortcuts for splitting",
                    "Basic file operations",
                ],
                "Beginner",
            ),
            ExampleInfo(
                "02_tabbed_split_panes.py",
                "Tabbed Split Panes",
                """
                This example shows how to combine tab widgets within split panes while maintaining
                the runtime splitting capability. Each pane contains a QTabWidget with multiple tabs,
                and you can split panes that contain tabs.

                Demonstrates working with complex widget hierarchies.
                """,
                [
                    "QTabWidget integration with MultiSplit",
                    "Splitting panes that contain tabs",
                    "Adding new tabs to focused pane",
                    "Focus management between tabs and panes",
                    "Context menus for advanced interactions",
                    "Complex nested widget patterns",
                ],
                "Intermediate",
            ),
            ExampleInfo(
                "03_keyboard_driven_splitting.py",
                "Keyboard-Driven Split Control",
                """
                This example demonstrates advanced keyboard control for power users. Features
                vim-like navigation, modal command interfaces, and a command palette for
                discoverable actions. No mouse required!

                Perfect for understanding how to create keyboard-driven workflows.
                """,
                [
                    "Vim-like keyboard navigation (h/j/k/l)",
                    "Modal interaction patterns (NORMAL/COMMAND mode)",
                    "Command palette for discoverable actions",
                    "Global keyboard event handling",
                    "Advanced focus navigation patterns",
                    "Power-user workflow optimization",
                ],
                "Advanced",
            ),
            ExampleInfo(
                "04_advanced_dynamic_workspace.py",
                "Advanced Dynamic Workspace",
                """
                This example demonstrates the full power of MultiSplit for building complete
                applications. Features multiple widget types, session management, real-time
                updates, and a plugin-like architecture for different pane types.

                Shows how MultiSplit can be the foundation for IDEs, dashboards, and complex tools.
                """,
                [
                    "Multiple widget types (editors, terminals, browsers, logs, etc.)",
                    "Dynamic pane creation at runtime",
                    "Session save/restore functionality",
                    "Plugin-like architecture for pane types",
                    "Real-time updates and data flow",
                    "Complete IDE-like application structure",
                    "Advanced workspace management patterns",
                ],
                "Expert",
            ),
        ]

        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout(central_widget)

        # Header
        header = self.create_header()
        layout.addWidget(header)

        # Main content
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - example list
        left_panel = self.create_example_list()
        splitter.addWidget(left_panel)

        # Right panel - example details
        right_panel = self.create_details_panel()
        splitter.addWidget(right_panel)

        splitter.setSizes([300, 700])
        layout.addWidget(splitter)

        # Footer
        footer = self.create_footer()
        layout.addWidget(footer)

        # Select first example by default
        if self.examples:
            self.example_list.setCurrentRow(0)
            self.show_example_details(self.examples[0])

    def create_header(self) -> QWidget:
        """Create header section."""
        header = QFrame()
        header.setFrameStyle(QFrame.Shape.StyledPanel)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a90e2, stop:1 #357abd);
                color: white;
                padding: 15px;
                border-radius: 5px;
            }
        """)

        layout = QVBoxLayout(header)

        title = QLabel("MultiSplit Widget Examples")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        layout.addWidget(title)

        subtitle = QLabel("Learn runtime pane splitting from basic to advanced concepts")
        subtitle.setStyleSheet("font-size: 14px; color: #e8f4f8;")
        layout.addWidget(subtitle)

        return header

    def create_example_list(self) -> QWidget:
        """Create example list panel."""
        panel = QGroupBox("Examples")
        layout = QVBoxLayout(panel)

        self.example_list = QListWidget()
        self.example_list.currentRowChanged.connect(self.on_example_selected)

        # Populate examples
        for i, example in enumerate(self.examples):
            item = QListWidgetItem()

            # Create custom widget for the item
            item_widget = QWidget()
            item_layout = QVBoxLayout(item_widget)
            item_layout.setContentsMargins(5, 5, 5, 5)

            # Title
            title = QLabel(f"{i + 1}. {example.title}")
            title.setStyleSheet("font-weight: bold; font-size: 12px;")
            item_layout.addWidget(title)

            # Difficulty badge
            difficulty_color = {
                "Beginner": "#4CAF50",
                "Intermediate": "#FF9800",
                "Advanced": "#F44336",
                "Expert": "#9C27B0",
            }.get(example.difficulty, "#666")

            difficulty = QLabel(example.difficulty)
            difficulty.setStyleSheet(f"""
                QLabel {{
                    background-color: {difficulty_color};
                    color: white;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-size: 10px;
                    font-weight: bold;
                }}
            """)
            difficulty.setMaximumWidth(80)
            item_layout.addWidget(difficulty)

            # Set item
            item.setSizeHint(item_widget.sizeHint())
            self.example_list.addItem(item)
            self.example_list.setItemWidget(item, item_widget)

        layout.addWidget(self.example_list)

        # Controls
        controls = QHBoxLayout()

        self.run_button = QPushButton("🚀 Run Example")
        self.run_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.run_button.clicked.connect(self.run_selected_example)
        controls.addWidget(self.run_button)

        self.view_code_button = QPushButton("📄 View Code")
        self.view_code_button.clicked.connect(self.view_example_code)
        controls.addWidget(self.view_code_button)

        layout.addLayout(controls)

        return panel

    def create_details_panel(self) -> QWidget:
        """Create details panel."""
        panel = QGroupBox("Example Details")
        layout = QVBoxLayout(panel)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.details_content = QWidget()
        self.details_layout = QVBoxLayout(self.details_content)

        scroll.setWidget(self.details_content)
        layout.addWidget(scroll)

        return panel

    def create_footer(self) -> QWidget:
        """Create footer section."""
        footer = QFrame()
        footer.setFrameStyle(QFrame.Shape.StyledPanel)
        footer.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                padding: 8px;
            }
        """)

        layout = QHBoxLayout(footer)

        info = QLabel(
            "💡 Tip: Start with Example 1 and progress through each example to build understanding"
        )
        info.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(info)

        layout.addStretch()

        # Running processes indicator
        self.process_label = QLabel("")
        layout.addWidget(self.process_label)

        self.kill_all_button = QPushButton("⏹️ Stop All")
        self.kill_all_button.clicked.connect(self.kill_all_processes)
        self.kill_all_button.setVisible(False)
        layout.addWidget(self.kill_all_button)

        return footer

    def on_example_selected(self, row: int):
        """Handle example selection."""
        if 0 <= row < len(self.examples):
            self.show_example_details(self.examples[row])

    def show_example_details(self, example: ExampleInfo):
        """Show details for selected example."""
        # Clear existing content
        for i in reversed(range(self.details_layout.count())):
            self.details_layout.itemAt(i).widget().setParent(None)

        # Title
        title = QLabel(example.title)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        self.details_layout.addWidget(title)

        # Difficulty and file info
        info_layout = QHBoxLayout()

        difficulty_color = {
            "Beginner": "#4CAF50",
            "Intermediate": "#FF9800",
            "Advanced": "#F44336",
            "Expert": "#9C27B0",
        }.get(example.difficulty, "#666")

        difficulty = QLabel(f"Difficulty: {example.difficulty}")
        difficulty.setStyleSheet(f"""
            QLabel {{
                background-color: {difficulty_color};
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: bold;
            }}
        """)
        info_layout.addWidget(difficulty)

        file_label = QLabel(f"File: {example.file_name}")
        file_label.setStyleSheet("color: #666; font-family: monospace;")
        info_layout.addWidget(file_label)

        info_layout.addStretch()
        self.details_layout.addLayout(info_layout)

        # Description
        desc_label = QLabel("Description:")
        desc_label.setStyleSheet("font-weight: bold; margin-top: 15px;")
        self.details_layout.addWidget(desc_label)

        description = QLabel(example.description.strip())
        description.setWordWrap(True)
        description.setStyleSheet("margin-left: 10px; line-height: 1.4;")
        self.details_layout.addWidget(description)

        # Concepts
        concepts_label = QLabel("Key Concepts:")
        concepts_label.setStyleSheet("font-weight: bold; margin-top: 15px;")
        self.details_layout.addWidget(concepts_label)

        for concept in example.concepts:
            concept_item = QLabel(f"• {concept}")
            concept_item.setStyleSheet("margin-left: 20px; margin-bottom: 5px;")
            concept_item.setWordWrap(True)
            self.details_layout.addWidget(concept_item)

        # Spacer
        self.details_layout.addStretch()

    def run_selected_example(self):
        """Run the selected example."""
        current_row = self.example_list.currentRow()
        if 0 <= current_row < len(self.examples):
            example = self.examples[current_row]
            self.run_example(example)

    def run_example(self, example: ExampleInfo):
        """Run an example."""
        if not example.file_path.exists():
            QMessageBox.warning(
                self, "File Not Found", f"Example file not found: {example.file_path}"
            )
            return

        # Create process
        process = QProcess(self)
        process.finished.connect(lambda: self.on_process_finished(process))

        # Start the example
        process.start(sys.executable, [str(example.file_path)])

        if process.waitForStarted():
            self.running_processes.append(process)
            self.update_process_indicator()

            QMessageBox.information(
                self,
                "Example Started",
                f"Started: {example.title}\n\nThe example is now running in a separate window.",
            )
        else:
            QMessageBox.warning(self, "Start Failed", f"Failed to start example: {example.title}")

    def view_example_code(self):
        """View the code for selected example."""
        current_row = self.example_list.currentRow()
        if 0 <= current_row < len(self.examples):
            example = self.examples[current_row]

            if not example.file_path.exists():
                QMessageBox.warning(self, "File Not Found", f"File not found: {example.file_path}")
                return

            # Create code viewer window
            code_window = CodeViewerWindow(example, self)
            code_window.show()

    def on_process_finished(self, process: QProcess):
        """Handle process completion."""
        if process in self.running_processes:
            self.running_processes.remove(process)
            self.update_process_indicator()

    def update_process_indicator(self):
        """Update process indicator."""
        count = len(self.running_processes)
        if count > 0:
            self.process_label.setText(f"Running: {count} example(s)")
            self.kill_all_button.setVisible(True)
        else:
            self.process_label.setText("")
            self.kill_all_button.setVisible(False)

    def kill_all_processes(self):
        """Kill all running processes."""
        for process in self.running_processes[:]:  # Copy list
            process.kill()
            process.waitForFinished(1000)

        self.running_processes.clear()
        self.update_process_indicator()

    def closeEvent(self, event):
        """Handle window close."""
        if self.running_processes:
            reply = QMessageBox.question(
                self,
                "Running Examples",
                f"There are {len(self.running_processes)} examples still running.\nKill them and exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.kill_all_processes()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


class CodeViewerWindow(QMainWindow):
    """Window for viewing example code."""

    def __init__(self, example: ExampleInfo, parent=None):
        super().__init__(parent)
        self.example = example

        self.setWindowTitle(f"Code: {example.title}")
        self.setGeometry(150, 150, 800, 600)

        # Setup UI
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Header
        header = QLabel(f"📄 {example.file_name}")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)

        # Code display
        code_edit = QTextEdit()
        code_edit.setFont(QFont("Consolas", 10))
        code_edit.setReadOnly(True)

        try:
            with open(example.file_path, encoding="utf-8") as f:
                code_edit.setPlainText(f.read())
        except Exception as e:
            code_edit.setPlainText(f"Error loading file: {e}")

        layout.addWidget(code_edit)

        # Footer
        footer = QHBoxLayout()

        run_button = QPushButton("🚀 Run This Example")
        run_button.clicked.connect(self.run_example)
        footer.addWidget(run_button)

        footer.addStretch()

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        footer.addWidget(close_button)

        layout.addLayout(footer)

    def run_example(self):
        """Run this example."""
        if hasattr(self.parent(), "run_example"):
            self.parent().run_example(self.example)


def main():
    """Run the examples runner."""
    app = QApplication(sys.argv)

    print("=" * 60)
    print("MULTISPLIT WIDGET EXAMPLES RUNNER")
    print("=" * 60)
    print()
    print("This runner helps you explore MultiSplit widget examples")
    print("in a progressive learning path:")
    print()
    print("1. 📝 Basic Text Editor - Learn core splitting concepts")
    print("2. 📂 Tabbed Split Panes - Complex widget hierarchies")
    print("3. ⌨️  Keyboard Control - Advanced interaction patterns")
    print("4. 🏗️  Dynamic Workspace - Complete application example")
    print()
    print("Each example builds on concepts from the previous ones.")
    print("=" * 60)
    print()

    runner = ExampleRunner()
    runner.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
