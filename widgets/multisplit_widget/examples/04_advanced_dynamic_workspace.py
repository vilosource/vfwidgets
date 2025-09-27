#!/usr/bin/env python3
"""
Advanced Dynamic Workspace - MultiSplit Widget Example

This example demonstrates the full power of MultiSplit for building complex applications:
- Multiple widget types (editors, terminals, browsers, etc.)
- Dynamic pane type creation
- Session save/restore functionality
- Drag and drop between panes
- Advanced workspace management
- Plugin-like architecture
- Real-time updates and collaboration simulation

Key Learning Points:
1. Building complete applications with MultiSplit as foundation
2. Advanced WidgetProvider patterns for multiple widget types
3. Session management and persistence
4. Complex interaction patterns
5. Real-world application architecture

Usage:
- Workspace > New: Create different pane types
- File menu: Session save/restore
- Drag files between panes
- Right-click panes for context actions
- Dynamic splitting based on content type
"""

import random
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QStatusBar,
    QTextEdit,
    QToolBar,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)
from vfwidgets_multisplit import MultisplitWidget
from vfwidgets_multisplit.core.types import WherePosition
from vfwidgets_multisplit.view.container import WidgetProvider


class PaneType(Enum):
    TEXT_EDITOR = "text_editor"
    FILE_BROWSER = "file_browser"
    TERMINAL = "terminal"
    LOG_VIEWER = "log_viewer"
    TASK_LIST = "task_list"
    CHAT = "chat"
    DASHBOARD = "dashboard"
    WEB_VIEW = "web_view"
    IMAGE_VIEWER = "image_viewer"


@dataclass
class PaneConfig:
    pane_type: PaneType
    title: str
    config: dict[str, Any]


class WorkspaceSession:
    """Manages workspace sessions."""

    def __init__(self):
        self.sessions: dict[str, dict[str, Any]] = {}

    def save_session(
        self, name: str, layout_data: dict[str, Any], pane_configs: dict[str, PaneConfig]
    ):
        """Save workspace session."""
        self.sessions[name] = {
            "layout": layout_data,
            "panes": {
                pid: {
                    "type": config.pane_type.value,
                    "title": config.title,
                    "config": config.config,
                }
                for pid, config in pane_configs.items()
            },
        }

    def load_session(self, name: str) -> Optional[dict[str, Any]]:
        """Load workspace session."""
        return self.sessions.get(name)

    def list_sessions(self) -> list[str]:
        """List available sessions."""
        return list(self.sessions.keys())


class BasePane(QWidget):
    """Base class for all pane types."""

    content_changed = Signal(str)  # pane_id
    action_requested = Signal(str, str)  # action, data
    close_requested = Signal(str)  # pane_id

    def __init__(self, pane_id: str, pane_type: PaneType, title: str):
        super().__init__()
        self.pane_id = pane_id
        self.pane_type = pane_type
        self.title = title
        self.is_modified = False

        self.setup_ui()

    def setup_ui(self):
        """Setup base UI structure."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)

        # Header
        header = QFrame()
        header.setFrameStyle(QFrame.Shape.StyledPanel)
        header.setStyleSheet("""
            QFrame {
                background-color: #f8f8f8;
                border: 1px solid #ddd;
                padding: 2px;
            }
        """)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(4, 2, 4, 2)

        # Icon and title
        self.icon_label = QLabel(self.get_icon())
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("font-size: 11px; font-weight: bold;")

        header_layout.addWidget(self.icon_label)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()

        # Actions
        self.setup_header_actions(header_layout)

        # Content area
        self.content_widget = QWidget()
        self.setup_content()

        layout.addWidget(header)
        layout.addWidget(self.content_widget, 1)

    def get_icon(self) -> str:
        """Get icon for pane type."""
        icons = {
            PaneType.TEXT_EDITOR: "📝",
            PaneType.FILE_BROWSER: "📁",
            PaneType.TERMINAL: "💻",
            PaneType.LOG_VIEWER: "📋",
            PaneType.TASK_LIST: "✅",
            PaneType.CHAT: "💬",
            PaneType.DASHBOARD: "📊",
            PaneType.WEB_VIEW: "🌐",
            PaneType.IMAGE_VIEWER: "🖼️",
        }
        return icons.get(self.pane_type, "📄")

    def setup_header_actions(self, layout: QHBoxLayout):
        """Setup header action buttons."""
        pass  # Override in subclasses

    def setup_content(self):
        """Setup content area."""
        pass  # Override in subclasses

    def get_config(self) -> dict[str, Any]:
        """Get pane configuration."""
        return {}

    def set_config(self, config: dict[str, Any]):
        """Set pane configuration."""
        pass


class TextEditorPane(BasePane):
    """Text editor pane."""

    def __init__(self, pane_id: str, title: str = "Text Editor", file_path: str = ""):
        self.file_path = file_path
        super().__init__(pane_id, PaneType.TEXT_EDITOR, title)

    def setup_header_actions(self, layout: QHBoxLayout):
        save_btn = QPushButton("💾")
        save_btn.setMaximumSize(20, 20)
        save_btn.setToolTip("Save")
        save_btn.clicked.connect(self.save_file)
        layout.addWidget(save_btn)

    def setup_content(self):
        layout = QVBoxLayout(self.content_widget)
        layout.setContentsMargins(2, 2, 2, 2)

        self.editor = QPlainTextEdit()
        font = QFont("Consolas", 11)
        self.editor.setFont(font)

        if self.file_path:
            try:
                with open(self.file_path) as f:
                    self.editor.setPlainText(f.read())
            except Exception:
                self.editor.setPlainText(f"# Could not load: {self.file_path}\n")
        else:
            self.editor.setPlainText(f"# {self.title}\n\nStart editing...")

        self.editor.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.editor)

    def on_text_changed(self):
        if not self.is_modified:
            self.is_modified = True
            self.title_label.setText(f"{self.title} *")
            self.content_changed.emit(self.pane_id)

    def save_file(self):
        if not self.file_path:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save File")
            if file_path:
                self.file_path = file_path

        if self.file_path:
            try:
                with open(self.file_path, "w") as f:
                    f.write(self.editor.toPlainText())
                self.is_modified = False
                self.title_label.setText(self.title)
            except Exception as e:
                QMessageBox.warning(self, "Save Error", str(e))

    def get_config(self) -> dict[str, Any]:
        return {"file_path": self.file_path, "content": self.editor.toPlainText()}

    def set_config(self, config: dict[str, Any]):
        if "file_path" in config:
            self.file_path = config["file_path"]
        if "content" in config:
            self.editor.setPlainText(config["content"])


class FileBrowserPane(BasePane):
    """File browser pane."""

    def __init__(self, pane_id: str, title: str = "File Browser", root_path: str = "."):
        self.root_path = Path(root_path)
        super().__init__(pane_id, PaneType.FILE_BROWSER, title)

    def setup_header_actions(self, layout: QHBoxLayout):
        refresh_btn = QPushButton("🔄")
        refresh_btn.setMaximumSize(20, 20)
        refresh_btn.setToolTip("Refresh")
        refresh_btn.clicked.connect(self.refresh)
        layout.addWidget(refresh_btn)

    def setup_content(self):
        layout = QVBoxLayout(self.content_widget)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Files")
        self.tree.itemDoubleClicked.connect(self.open_file)
        layout.addWidget(self.tree)

        self.refresh()

    def refresh(self):
        self.tree.clear()
        root_item = QTreeWidgetItem(self.tree)
        root_item.setText(0, str(self.root_path))
        root_item.setData(0, Qt.ItemDataRole.UserRole, self.root_path)

        self.populate_tree(root_item, self.root_path)
        self.tree.expandItem(root_item)

    def populate_tree(self, parent_item: QTreeWidgetItem, path: Path):
        try:
            for item_path in sorted(path.iterdir()):
                if item_path.name.startswith("."):
                    continue

                item = QTreeWidgetItem(parent_item)
                if item_path.is_dir():
                    item.setText(0, f"📁 {item_path.name}")
                else:
                    item.setText(0, f"📄 {item_path.name}")
                item.setData(0, Qt.ItemDataRole.UserRole, item_path)

                if item_path.is_dir():
                    # Add placeholder for lazy loading
                    placeholder = QTreeWidgetItem(item)
                    placeholder.setText(0, "...")
        except PermissionError:
            pass

    def open_file(self, item: QTreeWidgetItem, column: int):
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if path and path.is_file():
            self.action_requested.emit("open_file", str(path))


class TerminalPane(BasePane):
    """Terminal/console pane."""

    def __init__(self, pane_id: str, title: str = "Terminal"):
        super().__init__(pane_id, PaneType.TERMINAL, title)
        self.command_history = []

    def setup_header_actions(self, layout: QHBoxLayout):
        clear_btn = QPushButton("🗑️")
        clear_btn.setMaximumSize(20, 20)
        clear_btn.setToolTip("Clear")
        clear_btn.clicked.connect(self.clear_output)
        layout.addWidget(clear_btn)

    def setup_content(self):
        layout = QVBoxLayout(self.content_widget)

        # Output area
        self.output = QTextEdit()
        self.output.setFont(QFont("Consolas", 10))
        self.output.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #333;
            }
        """)
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        # Command input
        cmd_layout = QHBoxLayout()
        cmd_layout.addWidget(QLabel("$ "))

        self.command_input = QLineEdit()
        self.command_input.setFont(QFont("Consolas", 10))
        self.command_input.returnPressed.connect(self.execute_command)
        cmd_layout.addWidget(self.command_input)

        layout.addLayout(cmd_layout)

        # Initial welcome
        self.output.append("Welcome to MultiSplit Terminal Simulator")
        self.output.append("Type 'help' for available commands")
        self.output.append("")

    def execute_command(self):
        command = self.command_input.text().strip()
        if not command:
            return

        self.command_history.append(command)
        self.output.append(f"$ {command}")

        # Simulate command execution
        if command == "help":
            self.output.append("Available commands:")
            self.output.append("  help    - Show this help")
            self.output.append("  clear   - Clear screen")
            self.output.append("  ls      - List files")
            self.output.append("  date    - Show current date")
            self.output.append("  echo    - Echo text")
        elif command == "clear":
            self.clear_output()
        elif command == "ls":
            self.output.append("file1.txt  file2.py  directory/")
        elif command == "date":
            from datetime import datetime

            self.output.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        elif command.startswith("echo "):
            self.output.append(command[5:])
        else:
            self.output.append(f"Command not found: {command}")

        self.output.append("")
        self.command_input.clear()

    def clear_output(self):
        self.output.clear()


class LogViewerPane(BasePane):
    """Log viewer pane with real-time updates."""

    def __init__(self, pane_id: str, title: str = "Log Viewer"):
        super().__init__(pane_id, PaneType.LOG_VIEWER, title)
        self.log_entries = []
        self.auto_scroll = True

        # Timer for simulating log updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.add_simulated_log)
        self.update_timer.start(2000)  # Add log every 2 seconds

    def setup_header_actions(self, layout: QHBoxLayout):
        pause_btn = QPushButton("⏸️")
        pause_btn.setMaximumSize(20, 20)
        pause_btn.setToolTip("Pause updates")
        pause_btn.clicked.connect(self.toggle_updates)
        layout.addWidget(pause_btn)

    def setup_content(self):
        layout = QVBoxLayout(self.content_widget)

        # Controls
        controls = QHBoxLayout()
        controls.addWidget(QLabel("Level:"))

        self.level_filter = QComboBox()
        self.level_filter.addItems(["ALL", "DEBUG", "INFO", "WARN", "ERROR"])
        controls.addWidget(self.level_filter)

        controls.addStretch()

        auto_scroll_checkbox = QCheckBox("Auto-scroll")
        auto_scroll_checkbox.setChecked(True)
        auto_scroll_checkbox.toggled.connect(self.set_auto_scroll)
        controls.addWidget(auto_scroll_checkbox)

        layout.addLayout(controls)

        # Log display
        self.log_display = QTextEdit()
        self.log_display.setFont(QFont("Consolas", 9))
        self.log_display.setReadOnly(True)
        layout.addWidget(self.log_display)

    def add_simulated_log(self):
        """Add simulated log entry."""
        levels = ["DEBUG", "INFO", "WARN", "ERROR"]
        level = random.choice(levels)
        messages = [
            "Processing request",
            "Database connection established",
            "Cache miss for key",
            "User authentication successful",
            "File upload completed",
            "Background task started",
            "Memory usage: 45%",
        ]

        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")
        message = random.choice(messages)

        log_entry = f"[{timestamp}] {level:5s} - {message}"
        self.log_entries.append(log_entry)

        # Apply level filter
        selected_level = self.level_filter.currentText()
        if selected_level == "ALL" or level == selected_level:
            color = {"DEBUG": "#888", "INFO": "#333", "WARN": "#ff8800", "ERROR": "#ff0000"}.get(
                level, "#333"
            )

            self.log_display.append(f'<span style="color: {color}">{log_entry}</span>')

            if self.auto_scroll:
                scrollbar = self.log_display.verticalScrollBar()
                scrollbar.setValue(scrollbar.maximum())

    def toggle_updates(self):
        if self.update_timer.isActive():
            self.update_timer.stop()
        else:
            self.update_timer.start(2000)

    def set_auto_scroll(self, enabled: bool):
        self.auto_scroll = enabled


class TaskListPane(BasePane):
    """Task list pane."""

    def __init__(self, pane_id: str, title: str = "Tasks"):
        super().__init__(pane_id, PaneType.TASK_LIST, title)
        self.tasks = []

    def setup_header_actions(self, layout: QHBoxLayout):
        add_btn = QPushButton("➕")
        add_btn.setMaximumSize(20, 20)
        add_btn.setToolTip("Add task")
        add_btn.clicked.connect(self.add_task)
        layout.addWidget(add_btn)

    def setup_content(self):
        layout = QVBoxLayout(self.content_widget)

        self.task_list = QListWidget()
        self.task_list.itemChanged.connect(self.task_changed)
        layout.addWidget(self.task_list)

        # Add some initial tasks
        self.add_initial_tasks()

    def add_initial_tasks(self):
        initial_tasks = [
            "Review code changes",
            "Update documentation",
            "Fix bug in login system",
            "Implement new feature",
            "Run tests",
        ]

        for task in initial_tasks:
            self.add_task_item(task, False)

    def add_task(self):
        text, ok = QInputDialog.getText(self, "New Task", "Task description:")
        if ok and text:
            self.add_task_item(text, False)

    def add_task_item(self, text: str, completed: bool):
        item = QListWidgetItem(text)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(Qt.CheckState.Checked if completed else Qt.CheckState.Unchecked)
        self.task_list.addItem(item)

    def task_changed(self, item: QListWidgetItem):
        # Update task status
        pass


class DashboardPane(BasePane):
    """Dashboard with metrics and charts."""

    def __init__(self, pane_id: str, title: str = "Dashboard"):
        super().__init__(pane_id, PaneType.DASHBOARD, title)

    def setup_content(self):
        layout = QGridLayout(self.content_widget)

        # Metrics
        metrics = [
            ("CPU Usage", "45%", "#4CAF50"),
            ("Memory", "2.1GB", "#2196F3"),
            ("Disk I/O", "125 MB/s", "#FF9800"),
            ("Network", "1.2 Mbps", "#9C27B0"),
        ]

        for i, (name, value, color) in enumerate(metrics):
            metric_widget = self.create_metric_widget(name, value, color)
            layout.addWidget(metric_widget, 0, i)

        # Chart placeholder
        chart_widget = QWidget()
        chart_widget.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        chart_label = QLabel("📊 Chart Placeholder\n(Real charts would go here)")
        chart_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_layout = QVBoxLayout(chart_widget)
        chart_layout.addWidget(chart_label)

        layout.addWidget(chart_widget, 1, 0, 1, 4)

    def create_metric_widget(self, name: str, value: str, color: str) -> QWidget:
        widget = QFrame()
        widget.setFrameStyle(QFrame.Shape.StyledPanel)
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                color: white;
                border-radius: 4px;
                padding: 8px;
            }}
        """)

        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel(name))

        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(value_label)

        return widget


class DynamicWorkspaceProvider(WidgetProvider):
    """Advanced provider supporting multiple pane types."""

    def __init__(self):
        self.panes: dict[str, BasePane] = {}
        self.pane_configs: dict[str, PaneConfig] = {}
        self.counter = 0

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Create widget based on type specification."""
        # Parse widget_id format: "type:config"
        if ":" in widget_id:
            pane_type_str, config_str = widget_id.split(":", 1)
        else:
            pane_type_str = widget_id
            config_str = ""

        try:
            pane_type = PaneType(pane_type_str)
        except ValueError:
            pane_type = PaneType.TEXT_EDITOR

        # Create pane based on type
        if pane_type == PaneType.TEXT_EDITOR:
            if config_str:
                pane = TextEditorPane(pane_id, "Editor", config_str)
            else:
                self.counter += 1
                pane = TextEditorPane(pane_id, f"Editor {self.counter}")

        elif pane_type == PaneType.FILE_BROWSER:
            root_path = config_str if config_str else "."
            pane = FileBrowserPane(pane_id, "Files", root_path)

        elif pane_type == PaneType.TERMINAL:
            pane = TerminalPane(pane_id, "Terminal")

        elif pane_type == PaneType.LOG_VIEWER:
            pane = LogViewerPane(pane_id, "Logs")

        elif pane_type == PaneType.TASK_LIST:
            pane = TaskListPane(pane_id, "Tasks")

        elif pane_type == PaneType.DASHBOARD:
            pane = DashboardPane(pane_id, "Dashboard")

        else:
            # Default to text editor
            pane = TextEditorPane(pane_id, f"Unknown Type: {pane_type_str}")

        # Store references
        self.panes[pane_id] = pane
        self.pane_configs[pane_id] = PaneConfig(pane_type, pane.title, pane.get_config())

        # Connect signals
        pane.action_requested.connect(self.handle_pane_action)

        return pane

    def handle_pane_action(self, action: str, data: str):
        """Handle action requests from panes."""
        if action == "open_file":
            # Request to open file - emit signal for main window to handle
            self.file_open_requested.emit(data)

    file_open_requested = Signal(str)

    def get_pane_configs(self) -> dict[str, PaneConfig]:
        """Get all pane configurations."""
        return self.pane_configs.copy()

    def widget_closing(self, widget_id: str, widget: QWidget) -> None:
        """Handle widget closing."""
        # Find and remove pane
        pane_id = None
        for pid, pane in self.panes.items():
            if pane == widget:
                pane_id = pid
                break

        if pane_id:
            del self.panes[pane_id]
            if pane_id in self.pane_configs:
                del self.pane_configs[pane_id]


class WorkspaceDialog(QDialog):
    """Dialog for creating new panes."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Pane")
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)

        self.pane_type = QComboBox()
        for ptype in PaneType:
            self.pane_type.addItem(f"{ptype.value.replace('_', ' ').title()}", ptype)

        self.title = QLineEdit()
        self.config = QLineEdit()

        layout.addRow("Pane Type:", self.pane_type)
        layout.addRow("Title:", self.title)
        layout.addRow("Config:", self.config)

        buttons = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        buttons.addWidget(create_btn)
        buttons.addWidget(cancel_btn)
        layout.addRow(buttons)

    def get_pane_spec(self) -> str:
        """Get pane specification string."""
        ptype = self.pane_type.currentData()
        config = self.config.text().strip()

        if config:
            return f"{ptype.value}:{config}"
        return ptype.value


class AdvancedWorkspaceWindow(QMainWindow):
    """Advanced workspace demonstration."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("MultiSplit Advanced Dynamic Workspace")
        self.setGeometry(50, 50, 1600, 1000)

        # Session management
        self.session_manager = WorkspaceSession()

        # Create provider
        self.provider = DynamicWorkspaceProvider()
        self.provider.file_open_requested.connect(self.open_file_in_editor)

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

        # Initialize with dashboard
        self.create_initial_workspace()

    def setup_menus(self):
        """Setup application menus."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        new_workspace = QAction("&New Workspace", self)
        new_workspace.triggered.connect(self.new_workspace)
        file_menu.addAction(new_workspace)

        file_menu.addSeparator()

        save_session = QAction("&Save Session...", self)
        save_session.setShortcut("Ctrl+S")
        save_session.triggered.connect(self.save_session)
        file_menu.addAction(save_session)

        load_session = QAction("&Load Session...", self)
        load_session.setShortcut("Ctrl+O")
        load_session.triggered.connect(self.load_session)
        file_menu.addAction(load_session)

        # Workspace menu
        workspace_menu = menubar.addMenu("&Workspace")

        new_pane = QAction("&New Pane...", self)
        new_pane.setShortcut("Ctrl+N")
        new_pane.triggered.connect(self.create_new_pane)
        workspace_menu.addAction(new_pane)

        workspace_menu.addSeparator()

        # Quick pane types
        quick_editor = QAction("Quick &Editor", self)
        quick_editor.setShortcut("Ctrl+E")
        quick_editor.triggered.connect(lambda: self.create_quick_pane(PaneType.TEXT_EDITOR))
        workspace_menu.addAction(quick_editor)

        quick_terminal = QAction("Quick &Terminal", self)
        quick_terminal.setShortcut("Ctrl+T")
        quick_terminal.triggered.connect(lambda: self.create_quick_pane(PaneType.TERMINAL))
        workspace_menu.addAction(quick_terminal)

        quick_browser = QAction("Quick &Browser", self)
        quick_browser.setShortcut("Ctrl+B")
        quick_browser.triggered.connect(lambda: self.create_quick_pane(PaneType.FILE_BROWSER))
        workspace_menu.addAction(quick_browser)

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

    def setup_toolbar(self):
        """Setup toolbar."""
        toolbar = QToolBar("Main")
        self.addToolBar(toolbar)

        # Quick actions
        toolbar.addAction("🆕 New Pane", self.create_new_pane)
        toolbar.addSeparator()

        # Quick pane types
        toolbar.addAction("📝 Editor", lambda: self.create_quick_pane(PaneType.TEXT_EDITOR))
        toolbar.addAction("💻 Terminal", lambda: self.create_quick_pane(PaneType.TERMINAL))
        toolbar.addAction("📁 Browser", lambda: self.create_quick_pane(PaneType.FILE_BROWSER))
        toolbar.addAction("📋 Logs", lambda: self.create_quick_pane(PaneType.LOG_VIEWER))
        toolbar.addAction("✅ Tasks", lambda: self.create_quick_pane(PaneType.TASK_LIST))
        toolbar.addAction("📊 Dashboard", lambda: self.create_quick_pane(PaneType.DASHBOARD))

        toolbar.addSeparator()

        # Split actions
        toolbar.addAction("⬌ Split →", lambda: self.split_focused_pane(WherePosition.RIGHT))
        toolbar.addAction("⬍ Split ↓", lambda: self.split_focused_pane(WherePosition.BOTTOM))

        toolbar.addSeparator()

        # Session actions
        toolbar.addAction("💾 Save", self.save_session)
        toolbar.addAction("📁 Load", self.load_session)

    def setup_statusbar(self):
        """Setup status bar."""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Advanced workspace ready - Create and split any pane type")

    def create_initial_workspace(self):
        """Create initial workspace layout."""
        # Initialize with dashboard
        self.multisplit.initialize_empty("dashboard:")

        # Add some initial panes
        panes = self.multisplit.get_pane_ids()
        if panes:
            main_pane = panes[0]

            # Add file browser on left
            self.multisplit.split_pane(main_pane, "file_browser:.", WherePosition.LEFT, 0.25)

            # Add terminal on bottom
            self.multisplit.split_pane(main_pane, "terminal:", WherePosition.BOTTOM, 0.7)

            # Add task list on right
            self.multisplit.split_pane(main_pane, "task_list:", WherePosition.RIGHT, 0.75)

    def new_workspace(self):
        """Create new workspace."""
        # Clear current workspace
        panes = self.multisplit.get_pane_ids()
        for pane_id in panes[1:]:  # Keep first pane
            self.multisplit.remove_pane(pane_id)

        # Reset first pane to dashboard
        if panes:
            self.multisplit.remove_pane(panes[0])
        self.multisplit.initialize_empty("dashboard:")

    def create_new_pane(self):
        """Create new pane with dialog."""
        dialog = WorkspaceDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            pane_spec = dialog.get_pane_spec()
            self.add_pane_to_workspace(pane_spec)

    def create_quick_pane(self, pane_type: PaneType):
        """Create pane of specific type quickly."""
        pane_spec = pane_type.value + ":"
        self.add_pane_to_workspace(pane_spec)

    def add_pane_to_workspace(self, pane_spec: str):
        """Add pane to workspace."""
        focused = self.multisplit.get_focused_pane()

        if focused:
            # Split focused pane
            success = self.multisplit.split_pane(focused, pane_spec, WherePosition.RIGHT, 0.5)
            if success:
                self.statusbar.showMessage(f"Added pane: {pane_spec}")
        else:
            # Initialize empty workspace
            self.multisplit.initialize_empty(pane_spec)

    def split_focused_pane(self, position: WherePosition):
        """Split focused pane with new editor."""
        focused = self.multisplit.get_focused_pane()
        if focused:
            success = self.multisplit.split_pane(focused, "text_editor:", position, 0.5)
            if success:
                direction = "horizontally" if position == WherePosition.RIGHT else "vertically"
                self.statusbar.showMessage(f"Split {direction}")

    def open_file_in_editor(self, file_path: str):
        """Open file in new editor pane."""
        focused = self.multisplit.get_focused_pane()
        if focused:
            pane_spec = f"text_editor:{file_path}"
            success = self.multisplit.split_pane(focused, pane_spec, WherePosition.RIGHT, 0.6)
            if success:
                self.statusbar.showMessage(f"Opened: {Path(file_path).name}")

    def save_session(self):
        """Save current session."""
        name, ok = QInputDialog.getText(self, "Save Session", "Session name:")
        if ok and name:
            # Get layout data (simplified - real implementation would use session API)
            layout_data = {"panes": self.multisplit.get_pane_ids()}
            pane_configs = self.provider.get_pane_configs()

            self.session_manager.save_session(name, layout_data, pane_configs)
            self.statusbar.showMessage(f"Session saved: {name}")

    def load_session(self):
        """Load saved session."""
        sessions = self.session_manager.list_sessions()
        if not sessions:
            QMessageBox.information(self, "Load Session", "No saved sessions found.")
            return

        session_name, ok = QInputDialog.getItem(
            self, "Load Session", "Select session:", sessions, 0, False
        )

        if ok and session_name:
            session_data = self.session_manager.load_session(session_name)
            if session_data:
                # Clear current workspace
                self.new_workspace()

                # Load panes (simplified implementation)
                # Real implementation would restore exact layout
                for _pane_id, pane_data in session_data["panes"].items():
                    pane_spec = f"{pane_data['type']}:"
                    self.add_pane_to_workspace(pane_spec)

                self.statusbar.showMessage(f"Session loaded: {session_name}")

    def on_pane_focused(self, pane_id: str):
        """Handle pane focus change."""
        pane = self.provider.panes.get(pane_id)
        if pane:
            pane_type = pane.pane_type.value.replace("_", " ").title()
            self.statusbar.showMessage(f"Focus: {pane_type} | {pane.title}")

    def on_pane_added(self, pane_id: str):
        """Handle pane added."""
        total_panes = len(self.multisplit.get_pane_ids())
        print(f"Pane added: {pane_id} | Total: {total_panes}")

    def on_pane_removed(self, pane_id: str):
        """Handle pane removed."""
        total_panes = len(self.multisplit.get_pane_ids())
        print(f"Pane removed: {pane_id} | Total: {total_panes}")


def main():
    """Run the advanced workspace example."""
    app = QApplication(sys.argv)

    print("=" * 80)
    print("MULTISPLIT ADVANCED DYNAMIC WORKSPACE")
    print("=" * 80)
    print()
    print("This example demonstrates the full power of MultiSplit for building")
    print("complete applications:")
    print()
    print("🎯 FEATURES DEMONSTRATED:")
    print("• Multiple widget types (editors, terminals, browsers, logs, etc.)")
    print("• Dynamic pane creation at runtime")
    print("• Session save/restore functionality")
    print("• Advanced workspace management")
    print("• Plugin-like architecture for pane types")
    print("• Real-time updates and data flow")
    print("• Complete IDE-like application structure")
    print()
    print("🚀 TRY THIS WORKFLOW:")
    print("1. Explore the initial workspace layout")
    print("2. Use toolbar to quickly add different pane types")
    print("3. Split panes: Split menu or Ctrl+Shift+H/V")
    print("4. Double-click files in browser to open in editor")
    print("5. Watch real-time log updates")
    print("6. Save workspace: File > Save Session")
    print("7. Create custom layouts for different workflows")
    print()
    print("💡 KEY INSIGHT:")
    print("MultiSplit becomes the foundation for ANY complex application!")
    print("Think IDEs, monitoring dashboards, data analysis tools...")
    print("=" * 80)
    print()

    window = AdvancedWorkspaceWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
