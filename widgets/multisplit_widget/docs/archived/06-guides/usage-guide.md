# MultiSplit Widget Usage Guide

## Overview

This guide provides practical patterns, real-world examples, and production-ready code for building applications with MultiSplit. It focuses on common usage scenarios that developers encounter when creating split-pane interfaces.

## What This Covers

- **Real-world application patterns** - IDE, terminal multiplexer, dashboard
- **Widget provider implementations** - File-based, pooled, factory patterns
- **Layout management strategies** - Persistence, restoration, templating
- **User interaction patterns** - Keyboard shortcuts, drag-drop, context menus
- **Integration techniques** - Embedding in existing applications

## What This Doesn't Cover

- **Internal architecture details** - See [Architecture docs](../02-architecture/)
- **Custom renderer development** - See [Extension Guide](extension-guide.md)
- **Performance optimization** - See [Integration Guide](integration-guide.md)
- **Advanced tree operations** - See original [Advanced Operations Guide](../../advanced-operations-GUIDE.md)

---

## Common Application Patterns

### Pattern 1: Code Editor IDE

Complete IDE-style application with file tree, editors, and terminal:

```python
from PySide6.QtWidgets import *
from vfwidgets_multisplit import MultiSplitWidget, WherePosition

class CodeEditorIDE(QMainWindow):
    """Production-ready IDE with MultiSplit layout"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Code Editor IDE")
        self.resize(1200, 800)

        # Core data structures
        self.open_files = {}  # file_path -> editor instance
        self.terminals = {}   # session_id -> terminal instance
        self.recent_files = []

        # Create MultiSplit widget
        self.splitter = MultiSplitWidget()
        self.splitter.set_widget_provider(self)
        self.setCentralWidget(self.splitter)

        # Initialize with file tree
        self.file_tree = FileTreeWidget()
        self.file_tree.file_double_clicked.connect(self.open_file)
        self.splitter.set_root_widget(self.file_tree, "file_tree")

        # Setup keyboard shortcuts
        self.setup_shortcuts()

        # Connect layout signals
        self.splitter.pane_focused.connect(self.on_pane_focused)
        self.splitter.layout_changed.connect(self.save_workspace_state)

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Create or retrieve widgets based on ID"""

        if widget_id == "file_tree":
            return self.file_tree

        elif widget_id.startswith("editor:"):
            file_path = widget_id[7:]  # Remove "editor:" prefix

            if file_path not in self.open_files:
                editor = CodeEditor()
                try:
                    editor.load_file(file_path)
                    self.open_files[file_path] = editor
                    self.add_to_recent_files(file_path)
                except FileNotFoundError:
                    return self.create_error_widget(f"File not found: {file_path}")

            return self.open_files[file_path]

        elif widget_id.startswith("terminal:"):
            session_id = widget_id[9:]  # Remove "terminal:" prefix

            if session_id not in self.terminals:
                terminal = TerminalWidget()
                terminal.set_session_id(session_id)
                self.terminals[session_id] = terminal

            return self.terminals[session_id]

        else:
            return self.create_error_widget(f"Unknown widget: {widget_id}")

    def widget_closing(self, widget_id: str, widget: QWidget) -> None:
        """Handle widget cleanup"""

        if widget_id.startswith("editor:"):
            file_path = widget_id[7:]
            editor = self.open_files.get(file_path)

            if editor and editor.document().isModified():
                # Auto-save or prompt user
                if self.auto_save_enabled:
                    editor.save()
                else:
                    self.prompt_save_changes(editor, file_path)

            # Remove from tracking
            if file_path in self.open_files:
                del self.open_files[file_path]

        elif widget_id.startswith("terminal:"):
            session_id = widget_id[9:]
            if session_id in self.terminals:
                terminal = self.terminals[session_id]
                terminal.cleanup()
                del self.terminals[session_id]

    def open_file(self, file_path: str, split_position: str = None):
        """Open file in editor with optional split"""

        widget_id = f"editor:{file_path}"

        # Check if file is already open
        current_pane = self.find_widget_pane(widget_id)
        if current_pane:
            self.splitter.focus_pane(current_pane)
            return

        # Create editor widget
        editor = CodeEditor()
        editor.load_file(file_path)
        self.open_files[file_path] = editor

        # Determine where to place it
        target_pane = self.splitter.current_pane_id

        if split_position == "right":
            self.splitter.split_with_widget(
                target_pane, WherePosition.RIGHT, editor, widget_id
            )
        elif split_position == "bottom":
            self.splitter.split_with_widget(
                target_pane, WherePosition.BOTTOM, editor, widget_id
            )
        else:
            # Replace current pane
            self.splitter.replace_widget(target_pane, editor, widget_id)

    def new_terminal(self, split_position: str = "bottom"):
        """Create new terminal in split"""

        session_id = f"session_{len(self.terminals) + 1}"
        widget_id = f"terminal:{session_id}"

        terminal = TerminalWidget()
        terminal.set_session_id(session_id)
        self.terminals[session_id] = terminal

        current_pane = self.splitter.current_pane_id
        where = {
            "right": WherePosition.RIGHT,
            "left": WherePosition.LEFT,
            "top": WherePosition.TOP,
            "bottom": WherePosition.BOTTOM
        }.get(split_position, WherePosition.BOTTOM)

        self.splitter.split_with_widget(current_pane, where, terminal, widget_id)

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""

        # File operations
        QShortcut("Ctrl+O", self, self.open_file_dialog)
        QShortcut("Ctrl+S", self, self.save_current_file)
        QShortcut("Ctrl+W", self, self.close_current_pane)

        # Split operations
        QShortcut("Ctrl+\\", self, lambda: self.split_current_pane("right"))
        QShortcut("Ctrl+Shift+\\", self, lambda: self.split_current_pane("bottom"))

        # Terminal
        QShortcut("Ctrl+`", self, lambda: self.new_terminal("bottom"))

        # Pane navigation
        QShortcut("Ctrl+1", self, lambda: self.focus_pane_by_index(0))
        QShortcut("Ctrl+2", self, lambda: self.focus_pane_by_index(1))
        QShortcut("Ctrl+3", self, lambda: self.focus_pane_by_index(2))

        # Layout management
        QShortcut("Ctrl+Z", self, self.splitter.undo)
        QShortcut("Ctrl+Y", self, self.splitter.redo)
```

### Pattern 2: Data Analysis Dashboard

Dashboard with synchronized plots and data tables:

```python
class DataDashboard(QMainWindow):
    """Real-time data dashboard with MultiSplit"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Analysis Dashboard")

        # Data management
        self.datasets = {}  # name -> DataFrame
        self.plots = {}     # plot_id -> PlotWidget
        self.tables = {}    # table_id -> TableWidget

        # Create MultiSplit
        self.splitter = MultiSplitWidget()
        self.splitter.set_widget_provider(self)
        self.setCentralWidget(self.splitter)

        # Load initial dashboard layout
        self.create_default_dashboard()

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Create dashboard widgets"""

        widget_type, param = widget_id.split(":", 1)

        if widget_type == "plot":
            if param not in self.plots:
                plot = PlotWidget()
                plot.setup_realtime_updates()
                self.plots[param] = plot
            return self.plots[param]

        elif widget_type == "table":
            if param not in self.tables:
                table = DataTableWidget()
                table.setup_data_binding()
                self.tables[param] = table
            return self.tables[param]

        elif widget_type == "control":
            return ControlPanelWidget()

        elif widget_type == "summary":
            return SummaryStatsWidget()

        return QLabel(f"Unknown widget: {widget_id}")

    def create_default_dashboard(self):
        """Create 2x2 dashboard layout"""

        # Control panel (left side)
        control_panel = ControlPanelWidget()
        control_panel.dataset_changed.connect(self.update_all_widgets)
        self.splitter.set_root_widget(control_panel, "control:main")

        # Main content area (right side)
        plot_widget = PlotWidget()
        root_pane = self.splitter.current_pane_id
        self.splitter.split_with_widget(
            root_pane, WherePosition.RIGHT, plot_widget, "plot:main"
        )

        # Split right side vertically
        panes = list(self.splitter.all_pane_ids)
        right_pane = panes[1]  # Second pane (right side)

        table_widget = DataTableWidget()
        self.splitter.split_with_widget(
            right_pane, WherePosition.BOTTOM, table_widget, "table:main"
        )

        # Summary stats (bottom right)
        summary_widget = SummaryStatsWidget()
        panes = list(self.splitter.all_pane_ids)
        bottom_right_pane = panes[2]
        self.splitter.split_with_widget(
            bottom_right_pane, WherePosition.RIGHT, summary_widget, "summary:main"
        )

        # Set equal ratios for clean 2x2 grid
        self.splitter.set_equal_ratios()
```

### Pattern 3: Terminal Multiplexer

Terminal multiplexer with session management:

```python
class TerminalMultiplexer(QWidget):
    """tmux-style terminal multiplexer"""

    def __init__(self):
        super().__init__()

        # Session management
        self.sessions = {}  # session_id -> TerminalSession
        self.session_counter = 0

        # Layout
        layout = QVBoxLayout(self)

        # Status bar
        self.status_bar = QLabel("Ready")
        layout.addWidget(self.status_bar)

        # MultiSplit for terminals
        self.splitter = MultiSplitWidget()
        self.splitter.set_widget_provider(self)
        layout.addWidget(self.splitter)

        # Connect signals
        self.splitter.pane_focused.connect(self.update_status_bar)

        # Create first terminal
        self.new_session()

        # Setup shortcuts
        self.setup_terminal_shortcuts()

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Provide terminal widgets"""

        if widget_id.startswith("terminal:"):
            session_id = widget_id[9:]

            if session_id not in self.sessions:
                # Create new terminal session
                terminal = TerminalWidget()
                session = TerminalSession(session_id, terminal)
                self.sessions[session_id] = session

            return self.sessions[session_id].terminal

        return QLabel(f"Unknown: {widget_id}")

    def new_session(self, split_direction: str = None):
        """Create new terminal session"""

        self.session_counter += 1
        session_id = f"session_{self.session_counter}"
        widget_id = f"terminal:{session_id}"

        # Create terminal
        terminal = TerminalWidget()
        terminal.start_shell()

        # Create session wrapper
        session = TerminalSession(session_id, terminal)
        self.sessions[session_id] = session

        # Add to layout
        if not self.splitter.current_pane_id:
            # First terminal
            self.splitter.set_root_widget(terminal, widget_id)
        else:
            # Split existing
            where = {
                "right": WherePosition.RIGHT,
                "left": WherePosition.LEFT,
                "up": WherePosition.TOP,
                "down": WherePosition.BOTTOM
            }.get(split_direction, WherePosition.RIGHT)

            self.splitter.split_with_widget(
                self.splitter.current_pane_id, where, terminal, widget_id
            )

        return session_id

    def setup_terminal_shortcuts(self):
        """Setup tmux-style shortcuts"""

        # Session management (Ctrl+B prefix like tmux)
        prefix_action = QAction(self)
        prefix_action.setShortcut("Ctrl+B")
        prefix_action.triggered.connect(self.enter_command_mode)
        self.addAction(prefix_action)

        # Quick splits (without prefix for convenience)
        QShortcut("Alt+Right", self, lambda: self.new_session("right"))
        QShortcut("Alt+Down", self, lambda: self.new_session("down"))
        QShortcut("Alt+Left", self, lambda: self.new_session("left"))
        QShortcut("Alt+Up", self, lambda: self.new_session("up"))

        # Pane navigation
        QShortcut("Alt+H", self, lambda: self.navigate_pane("left"))
        QShortcut("Alt+J", self, lambda: self.navigate_pane("down"))
        QShortcut("Alt+K", self, lambda: self.navigate_pane("up"))
        QShortcut("Alt+L", self, lambda: self.navigate_pane("right"))
```

---

## Widget Provider Patterns

### File-Based Provider

Provider that manages file-based widgets like editors:

```python
class FileBasedProvider:
    """Provider for file-based widgets with smart caching"""

    def __init__(self):
        self.file_cache = {}      # file_path -> editor instance
        self.watch_manager = FileWatchManager()
        self.auto_save_enabled = True
        self.max_cache_size = 50

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Provide file-based widgets with intelligent caching"""

        if widget_id.startswith("editor:"):
            return self._provide_editor(widget_id, pane_id)
        elif widget_id.startswith("image:"):
            return self._provide_image_viewer(widget_id, pane_id)
        elif widget_id.startswith("pdf:"):
            return self._provide_pdf_viewer(widget_id, pane_id)
        else:
            return self._create_unknown_widget(widget_id)

    def _provide_editor(self, widget_id: str, pane_id: str) -> QWidget:
        """Provide code editor with file watching"""

        file_path = widget_id[7:]  # Remove "editor:" prefix

        # Check cache first
        if file_path in self.file_cache:
            editor = self.file_cache[file_path]
            # Refresh if file changed externally
            if self.watch_manager.has_changed(file_path):
                self._refresh_editor(editor, file_path)
            return editor

        # Create new editor
        try:
            editor = CodeEditor()
            editor.load_file(file_path)

            # Setup file watching
            self.watch_manager.watch_file(file_path,
                                        lambda: self._on_file_changed(file_path))

            # Cache management
            self._manage_cache_size()
            self.file_cache[file_path] = editor

            return editor

        except Exception as e:
            return self._create_error_widget(f"Failed to load {file_path}: {e}")

    def _manage_cache_size(self):
        """Keep cache size under limit"""
        if len(self.file_cache) >= self.max_cache_size:
            # Remove least recently used
            oldest_file = min(self.file_cache.keys(),
                            key=lambda f: self.file_cache[f].last_access_time)
            del self.file_cache[oldest_file]

    def widget_closing(self, widget_id: str, widget: QWidget) -> None:
        """Handle file-based widget cleanup"""

        if widget_id.startswith("editor:"):
            file_path = widget_id[7:]

            # Auto-save if enabled
            if self.auto_save_enabled and hasattr(widget, 'document'):
                if widget.document().isModified():
                    widget.save()

            # Stop watching file
            self.watch_manager.unwatch_file(file_path)

            # Keep in cache for potential reuse
            if file_path in self.file_cache:
                self.file_cache[file_path].last_access_time = time.time()
```

### Factory Registry Provider

Extensible provider using factory pattern:

```python
class FactoryRegistryProvider:
    """Extensible provider using factory registration"""

    def __init__(self):
        self.factories = {}  # prefix -> factory function
        self.widget_cache = {}
        self.default_factory = None

        # Register built-in factories
        self.register_factory("editor", self._create_editor)
        self.register_factory("terminal", self._create_terminal)
        self.register_factory("browser", self._create_browser)
        self.register_factory("plot", self._create_plot_widget)

    def register_factory(self, prefix: str, factory_func: callable):
        """Register factory for widget type"""
        self.factories[prefix] = factory_func

    def set_default_factory(self, factory_func: callable):
        """Set fallback factory for unknown types"""
        self.default_factory = factory_func

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Create widget using registered factories"""

        # Check cache first
        if widget_id in self.widget_cache:
            return self.widget_cache[widget_id]

        # Parse widget type
        if ":" in widget_id:
            widget_type, param = widget_id.split(":", 1)
        else:
            widget_type, param = widget_id, ""

        # Find factory
        if widget_type in self.factories:
            factory = self.factories[widget_type]
            widget = factory(param, pane_id)
        elif self.default_factory:
            widget = self.default_factory(widget_id, pane_id)
        else:
            widget = QLabel(f"No factory for: {widget_type}")

        # Cache widget
        self.widget_cache[widget_id] = widget
        return widget

    def _create_editor(self, param: str, pane_id: str) -> QWidget:
        """Factory for code editors"""
        editor = CodeEditor()
        if param:  # param is file path
            editor.load_file(param)
        return editor

    def _create_terminal(self, param: str, pane_id: str) -> QWidget:
        """Factory for terminals"""
        terminal = TerminalWidget()
        if param:  # param is session id
            terminal.set_session_id(param)
        terminal.start_shell()
        return terminal

    def _create_browser(self, param: str, pane_id: str) -> QWidget:
        """Factory for web browsers"""
        browser = WebBrowserWidget()
        if param:  # param is URL
            browser.load(param)
        return browser

    def _create_plot_widget(self, param: str, pane_id: str) -> QWidget:
        """Factory for plot widgets"""
        plot = PlotWidget()
        if param:  # param is plot configuration
            plot.configure(param)
        return plot
```

---

## Layout Management Strategies

### Template-Based Layouts

Pre-defined layout templates for common scenarios:

```python
class LayoutTemplates:
    """Pre-defined layout templates"""

    @staticmethod
    def ide_layout() -> dict:
        """Standard IDE layout: file tree, editor, terminal"""
        return {
            "type": "split",
            "orientation": "horizontal",
            "ratios": [0.2, 0.8],
            "children": [
                {
                    "type": "leaf",
                    "pane_id": "file_tree_pane",
                    "widget_id": "file_tree"
                },
                {
                    "type": "split",
                    "orientation": "vertical",
                    "ratios": [0.7, 0.3],
                    "children": [
                        {
                            "type": "leaf",
                            "pane_id": "editor_pane",
                            "widget_id": "editor:untitled.txt"
                        },
                        {
                            "type": "leaf",
                            "pane_id": "terminal_pane",
                            "widget_id": "terminal:main"
                        }
                    ]
                }
            ]
        }

    @staticmethod
    def dashboard_2x2() -> dict:
        """2x2 grid dashboard layout"""
        return {
            "type": "split",
            "orientation": "horizontal",
            "ratios": [0.5, 0.5],
            "children": [
                {
                    "type": "split",
                    "orientation": "vertical",
                    "ratios": [0.5, 0.5],
                    "children": [
                        {"type": "leaf", "pane_id": "top_left", "widget_id": "plot:main"},
                        {"type": "leaf", "pane_id": "bottom_left", "widget_id": "table:data"}
                    ]
                },
                {
                    "type": "split",
                    "orientation": "vertical",
                    "ratios": [0.5, 0.5],
                    "children": [
                        {"type": "leaf", "pane_id": "top_right", "widget_id": "plot:secondary"},
                        {"type": "leaf", "pane_id": "bottom_right", "widget_id": "summary:stats"}
                    ]
                }
            ]
        }

    @staticmethod
    def terminal_grid(rows: int, cols: int) -> dict:
        """Grid of terminal sessions"""

        def create_terminal_leaf(row: int, col: int) -> dict:
            session_id = f"session_{row}_{col}"
            return {
                "type": "leaf",
                "pane_id": f"terminal_{row}_{col}",
                "widget_id": f"terminal:{session_id}"
            }

        # Build grid structure recursively
        def build_row(row: int) -> dict:
            if cols == 1:
                return create_terminal_leaf(row, 0)

            return {
                "type": "split",
                "orientation": "horizontal",
                "ratios": [1.0/cols] * cols,
                "children": [create_terminal_leaf(row, col) for col in range(cols)]
            }

        if rows == 1:
            return build_row(0)

        return {
            "type": "split",
            "orientation": "vertical",
            "ratios": [1.0/rows] * rows,
            "children": [build_row(row) for row in range(rows)]
        }

class LayoutManager:
    """Manage layout templates and persistence"""

    def __init__(self, splitter: MultiSplitWidget):
        self.splitter = splitter
        self.templates = LayoutTemplates()
        self.saved_layouts = {}

    def apply_template(self, template_name: str):
        """Apply a predefined template"""

        if template_name == "ide":
            layout = self.templates.ide_layout()
        elif template_name == "dashboard":
            layout = self.templates.dashboard_2x2()
        elif template_name.startswith("terminal_grid_"):
            # Parse "terminal_grid_2x3" format
            _, _, dimensions = template_name.split("_")
            rows, cols = map(int, dimensions.split("x"))
            layout = self.templates.terminal_grid(rows, cols)
        else:
            raise ValueError(f"Unknown template: {template_name}")

        self.splitter.restore_layout(layout)

    def save_custom_layout(self, name: str):
        """Save current layout as custom template"""
        layout = self.splitter.save_layout()
        self.saved_layouts[name] = layout

    def restore_custom_layout(self, name: str):
        """Restore a custom saved layout"""
        if name in self.saved_layouts:
            self.splitter.restore_layout(self.saved_layouts[name])
```

### Smart Persistence

Advanced persistence with incremental saves and recovery:

```python
class SmartPersistence:
    """Advanced layout persistence with recovery"""

    def __init__(self, splitter: MultiSplitWidget, app_name: str):
        self.splitter = splitter
        self.app_name = app_name
        self.auto_save_enabled = True
        self.save_interval = 30  # seconds

        # File paths
        self.workspace_dir = Path.home() / f".{app_name}"
        self.workspace_dir.mkdir(exist_ok=True)

        self.current_session_file = self.workspace_dir / "current_session.json"
        self.backup_session_file = self.workspace_dir / "backup_session.json"
        self.crash_recovery_file = self.workspace_dir / "crash_recovery.json"

        # Auto-save timer
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)
        if self.auto_save_enabled:
            self.auto_save_timer.start(self.save_interval * 1000)

        # Connect to layout changes
        self.splitter.layout_changed.connect(self.mark_dirty)
        self.dirty = False

    def save_session(self, session_data: dict = None) -> bool:
        """Save complete session with error handling"""

        try:
            # Prepare session data
            if session_data is None:
                session_data = self.collect_session_data()

            # Backup current session before overwriting
            if self.current_session_file.exists():
                shutil.copy2(self.current_session_file, self.backup_session_file)

            # Write new session
            with open(self.current_session_file, 'w') as f:
                json.dump(session_data, f, indent=2)

            # Clear crash recovery file on successful save
            if self.crash_recovery_file.exists():
                self.crash_recovery_file.unlink()

            self.dirty = False
            return True

        except Exception as e:
            print(f"Failed to save session: {e}")
            # Save to crash recovery file as fallback
            try:
                with open(self.crash_recovery_file, 'w') as f:
                    json.dump(session_data, f, indent=2)
            except:
                pass
            return False

    def restore_session(self) -> bool:
        """Restore session with crash recovery"""

        # Try crash recovery first
        if self.crash_recovery_file.exists():
            if self.show_crash_recovery_dialog():
                return self.restore_from_file(self.crash_recovery_file)

        # Try current session
        if self.current_session_file.exists():
            return self.restore_from_file(self.current_session_file)

        # Try backup
        if self.backup_session_file.exists():
            return self.restore_from_file(self.backup_session_file)

        return False

    def collect_session_data(self) -> dict:
        """Collect complete session state"""

        return {
            "version": "1.0",
            "timestamp": time.time(),
            "layout": self.splitter.save_layout(),
            "focus": self.splitter.current_pane_id,
            "undo_stack": self.collect_undo_state(),
            "app_metadata": self.collect_app_metadata()
        }

    def auto_save(self):
        """Periodic auto-save"""
        if self.dirty and self.auto_save_enabled:
            self.save_session()

    def mark_dirty(self):
        """Mark session as needing save"""
        self.dirty = True
```

---

## User Interaction Patterns

### Keyboard Navigation

Complete keyboard shortcuts and navigation:

```python
class KeyboardNavigationMixin:
    """Mixin to add comprehensive keyboard navigation"""

    def setup_keyboard_navigation(self):
        """Setup all keyboard shortcuts"""

        # Pane navigation
        self.nav_shortcuts = {
            "Ctrl+Right": lambda: self.navigate_spatially("right"),
            "Ctrl+Left": lambda: self.navigate_spatially("left"),
            "Ctrl+Up": lambda: self.navigate_spatially("up"),
            "Ctrl+Down": lambda: self.navigate_spatially("down"),

            # Tab-style navigation
            "Ctrl+Tab": self.splitter.focus_next_pane,
            "Ctrl+Shift+Tab": self.splitter.focus_previous_pane,

            # Numbered pane access
            "Alt+1": lambda: self.focus_pane_by_index(0),
            "Alt+2": lambda: self.focus_pane_by_index(1),
            "Alt+3": lambda: self.focus_pane_by_index(2),
            "Alt+4": lambda: self.focus_pane_by_index(3),

            # Split operations
            "Ctrl+\\": lambda: self.smart_split("vertical"),
            "Ctrl+Shift+\\": lambda: self.smart_split("horizontal"),

            # Resize operations
            "Ctrl+Shift+Right": lambda: self.resize_current_pane("right", 10),
            "Ctrl+Shift+Left": lambda: self.resize_current_pane("left", 10),
            "Ctrl+Shift+Up": lambda: self.resize_current_pane("up", 10),
            "Ctrl+Shift+Down": lambda: self.resize_current_pane("down", 10),

            # Layout operations
            "Ctrl+Shift+R": self.reset_layout_ratios,
            "Ctrl+Shift+M": self.maximize_current_pane,
            "Ctrl+Shift+E": self.equalize_all_panes,

            # Close operations
            "Ctrl+W": self.close_current_pane,
            "Ctrl+Shift+W": self.close_all_except_current,

            # Undo/Redo
            "Ctrl+Z": self.splitter.undo,
            "Ctrl+Y": self.splitter.redo,
            "Ctrl+Shift+Z": self.splitter.redo,
        }

        # Register all shortcuts
        for key_combo, action in self.nav_shortcuts.items():
            shortcut = QShortcut(key_combo, self)
            shortcut.activated.connect(action)

    def navigate_spatially(self, direction: str):
        """Navigate based on spatial position"""

        current_pane = self.splitter.current_pane_id
        if not current_pane:
            return

        # Get all pane geometries
        pane_rects = {}
        for pane_id in self.splitter.all_pane_ids:
            rect = self.splitter.get_pane_rect(pane_id)
            pane_rects[pane_id] = rect

        current_rect = pane_rects[current_pane]
        current_center = current_rect.center()

        # Find best pane in direction
        best_pane = None
        best_distance = float('inf')

        for pane_id, rect in pane_rects.items():
            if pane_id == current_pane:
                continue

            pane_center = rect.center()

            # Check if pane is in the right direction
            if direction == "right" and pane_center.x() <= current_center.x():
                continue
            elif direction == "left" and pane_center.x() >= current_center.x():
                continue
            elif direction == "up" and pane_center.y() >= current_center.y():
                continue
            elif direction == "down" and pane_center.y() <= current_center.y():
                continue

            # Calculate distance
            distance = (current_center - pane_center).manhattanLength()
            if distance < best_distance:
                best_distance = distance
                best_pane = pane_id

        if best_pane:
            self.splitter.focus_pane(best_pane)

    def smart_split(self, orientation: str):
        """Intelligent splitting based on current pane size"""

        current_pane = self.splitter.current_pane_id
        if not current_pane:
            return

        # Get current pane dimensions
        rect = self.splitter.get_pane_rect(current_pane)

        # Choose split direction based on aspect ratio
        if orientation == "auto":
            if rect.width() > rect.height():
                where = WherePosition.RIGHT
            else:
                where = WherePosition.BOTTOM
        elif orientation == "vertical":
            where = WherePosition.RIGHT
        else:
            where = WherePosition.BOTTOM

        # Create appropriate widget for split
        widget, widget_id = self.create_default_split_widget()
        self.splitter.split_with_widget(current_pane, where, widget, widget_id)
```

### Drag and Drop Support

Complete drag and drop implementation:

```python
class DragDropHandler:
    """Handle drag and drop operations for MultiSplit"""

    def __init__(self, splitter: MultiSplitWidget, provider):
        self.splitter = splitter
        self.provider = provider

        # Enable drag and drop
        self.splitter.setAcceptDrops(True)

        # Visual feedback
        self.drop_indicator = DropIndicator(self.splitter)
        self.drop_indicator.hide()

        # Connect events
        self.splitter.dragEnterEvent = self.drag_enter_event
        self.splitter.dragMoveEvent = self.drag_move_event
        self.splitter.dragLeaveEvent = self.drag_leave_event
        self.splitter.dropEvent = self.drop_event

    def drag_enter_event(self, event):
        """Handle drag enter"""

        if self.can_handle_mime_data(event.mimeData()):
            event.acceptProposedAction()
            self.drop_indicator.show()
        else:
            event.ignore()

    def drag_move_event(self, event):
        """Handle drag move with visual feedback"""

        pos = event.pos()

        # Find target pane
        target_pane = self.splitter.get_pane_at_position(pos)
        if not target_pane:
            self.drop_indicator.hide()
            return

        # Determine drop zone
        pane_rect = self.splitter.get_pane_rect(target_pane)
        drop_zone = self.calculate_drop_zone(pos, pane_rect)

        # Update visual indicator
        self.drop_indicator.update_position(pane_rect, drop_zone)
        event.acceptProposedAction()

    def drop_event(self, event):
        """Handle actual drop"""

        self.drop_indicator.hide()

        pos = event.pos()
        target_pane = self.splitter.get_pane_at_position(pos)

        if not target_pane:
            return

        # Calculate drop position
        pane_rect = self.splitter.get_pane_rect(target_pane)
        drop_zone = self.calculate_drop_zone(pos, pane_rect)

        # Handle different mime types
        mime_data = event.mimeData()

        if mime_data.hasUrls():
            # File drops
            for url in mime_data.urls():
                file_path = url.toLocalFile()
                self.handle_file_drop(file_path, target_pane, drop_zone)

        elif mime_data.hasText():
            # Text drops
            text = mime_data.text()
            self.handle_text_drop(text, target_pane, drop_zone)

        event.acceptProposedAction()

    def calculate_drop_zone(self, pos: QPoint, rect: QRect) -> str:
        """Calculate which zone of the pane was targeted"""

        # Calculate relative position
        rel_x = (pos.x() - rect.x()) / rect.width()
        rel_y = (pos.y() - rect.y()) / rect.height()

        # Define drop zones
        edge_threshold = 0.25

        if rel_x < edge_threshold:
            return "left"
        elif rel_x > (1 - edge_threshold):
            return "right"
        elif rel_y < edge_threshold:
            return "top"
        elif rel_y > (1 - edge_threshold):
            return "bottom"
        else:
            return "center"

    def handle_file_drop(self, file_path: str, target_pane: str, zone: str):
        """Handle dropped files"""

        # Determine widget type from file extension
        ext = Path(file_path).suffix.lower()

        if ext in ['.py', '.js', '.html', '.css', '.txt', '.md']:
            widget_id = f"editor:{file_path}"
            widget = self.provider.provide_widget(widget_id, target_pane)
        elif ext in ['.jpg', '.png', '.gif', '.bmp']:
            widget_id = f"image:{file_path}"
            widget = ImageViewer(file_path)
        else:
            # Generic file viewer
            widget_id = f"file:{file_path}"
            widget = FileViewer(file_path)

        # Place widget based on drop zone
        if zone == "center":
            self.splitter.replace_widget(target_pane, widget, widget_id)
        else:
            where = {
                "left": WherePosition.LEFT,
                "right": WherePosition.RIGHT,
                "top": WherePosition.TOP,
                "bottom": WherePosition.BOTTOM
            }[zone]

            self.splitter.split_with_widget(target_pane, where, widget, widget_id)

class DropIndicator(QWidget):
    """Visual feedback for drag and drop operations"""

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.current_zone = "center"
        self.pane_rect = QRect()

    def update_position(self, pane_rect: QRect, zone: str):
        """Update indicator position and style"""
        self.pane_rect = pane_rect
        self.current_zone = zone

        # Calculate indicator geometry
        if zone == "center":
            self.setGeometry(pane_rect)
        else:
            # Show split preview
            indicator_rect = self.calculate_split_indicator_rect(pane_rect, zone)
            self.setGeometry(indicator_rect)

        self.update()

    def paintEvent(self, event):
        """Paint the drop indicator"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.current_zone == "center":
            # Highlight entire pane
            color = QColor(0, 120, 215, 100)  # Semi-transparent blue
            painter.fillRect(self.rect(), color)

            # Border
            pen = QPen(QColor(0, 120, 215), 2)
            painter.setPen(pen)
            painter.drawRect(self.rect().adjusted(1, 1, -1, -1))
        else:
            # Show split preview
            color = QColor(0, 120, 215, 150)
            painter.fillRect(self.rect(), color)
```

---

## Common Pitfalls

### Pitfall 1: Widget ID Instability

**Problem**: Changing widget ID format breaks persistence
```python
# ❌ BAD: Inconsistent ID format
def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
    if "_" in widget_id:  # Old format
        return self.handle_old_format(widget_id)
    else:  # New format
        return self.handle_new_format(widget_id)
```

**Solution**: Version your widget ID formats
```python
# ✅ GOOD: Versioned ID handling
def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
    if widget_id.startswith("v1:"):
        return self.handle_v1_format(widget_id[3:])
    elif widget_id.startswith("v2:"):
        return self.handle_v2_format(widget_id[3:])
    else:
        # Current format (no prefix)
        return self.handle_current_format(widget_id)
```

### Pitfall 2: Expensive Widget Creation

**Problem**: Creating heavy widgets blocks UI
```python
# ❌ BAD: Blocking widget creation
def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
    if widget_id.startswith("large_file:"):
        file_path = widget_id[11:]
        editor = CodeEditor()
        with open(file_path, 'r') as f:
            content = f.read()  # Could be huge file!
        editor.setPlainText(content)
        return editor
```

**Solution**: Use placeholders and async loading
```python
# ✅ GOOD: Async loading with placeholder
def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
    if widget_id.startswith("large_file:"):
        # Return placeholder immediately
        placeholder = LoadingWidget("Loading file...")

        # Load asynchronously
        file_path = widget_id[11:]
        self.load_file_async(file_path, placeholder, widget_id, pane_id)

        return placeholder
```

### Pitfall 3: Memory Leaks in Provider

**Problem**: Not cleaning up cached widgets
```python
# ❌ BAD: Unbounded cache growth
class LeakyProvider:
    def __init__(self):
        self.widget_cache = {}  # Never cleared!

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        if widget_id not in self.widget_cache:
            self.widget_cache[widget_id] = self.create_widget(widget_id)
        return self.widget_cache[widget_id]
```

**Solution**: Implement cache management
```python
# ✅ GOOD: Managed cache with size limits
class ManagedProvider:
    def __init__(self):
        self.widget_cache = {}
        self.access_times = {}
        self.max_cache_size = 50

    def widget_closing(self, widget_id: str, widget: QWidget) -> None:
        # Clean up when widgets are closed
        if widget_id in self.widget_cache:
            del self.widget_cache[widget_id]
            del self.access_times[widget_id]
```

### Pitfall 4: Ignoring Widget Lifecycle

**Problem**: Not handling widget_closing notifications
```python
# ❌ BAD: Ignoring lifecycle
def widget_closing(self, widget_id: str, widget: QWidget) -> None:
    pass  # Not saving state or cleaning up!
```

**Solution**: Proper lifecycle management
```python
# ✅ GOOD: Complete lifecycle handling
def widget_closing(self, widget_id: str, widget: QWidget) -> None:
    # Save any pending changes
    if hasattr(widget, 'has_unsaved_changes') and widget.has_unsaved_changes():
        self.save_widget_state(widget_id, widget)

    # Clean up resources
    if hasattr(widget, 'cleanup'):
        widget.cleanup()

    # Remove from tracking
    self.remove_from_cache(widget_id)
```

### Pitfall 5: Synchronous File Operations

**Problem**: Blocking UI with file I/O
```python
# ❌ BAD: Synchronous file operations
def save_workspace(self):
    layout = self.splitter.save_layout()
    with open("workspace.json", "w") as f:
        json.dump(layout, f, indent=2)  # Blocks UI!
```

**Solution**: Async file operations
```python
# ✅ GOOD: Async file operations
def save_workspace_async(self):
    layout = self.splitter.save_layout()

    def save_worker():
        with open("workspace.json", "w") as f:
            json.dump(layout, f, indent=2)

    QtConcurrent.run(save_worker)
```

---

## Quick Reference

### Essential Patterns Checklist

| Pattern | Purpose | Key Benefits |
|---------|---------|--------------|
| File-Based Provider | File editors, viewers | Smart caching, file watching |
| Factory Registry | Extensible widget types | Plugin architecture, modularity |
| Template Layouts | Predefined configurations | Consistent UX, quick setup |
| Smart Persistence | Robust save/restore | Crash recovery, incremental saves |
| Keyboard Navigation | Power user workflows | Efficiency, accessibility |

### Widget Provider Methods

| Method | When to Use | Critical for |
|--------|-------------|--------------|
| `provide_widget()` | Always required | Widget creation |
| `widget_closing()` | Always implement | Resource cleanup |
| `save_widget_state()` | With persistence | Session management |
| `can_close_widget()` | With unsaved data | Data protection |
| `get_widget_menu()` | Context menus | User interaction |

### Layout Template Formats

| Template Type | Use Case | Structure |
|---------------|----------|-----------|
| IDE Layout | Code editing | Tree + Editor + Terminal |
| Dashboard Grid | Data visualization | 2x2 or 3x3 grid |
| Terminal Grid | Command line work | NxM terminal grid |
| Document Viewer | Reading/reviewing | Single pane focus |
| Comparison View | Side-by-side analysis | 2-pane horizontal |

### Keyboard Shortcuts Standard

| Shortcut | Action | Alternative |
|----------|--------|-------------|
| `Ctrl+\` | Split vertical | `Ctrl+Shift+\` horizontal |
| `Ctrl+W` | Close pane | `Alt+F4` |
| `Ctrl+Tab` | Next pane | `Ctrl+Shift+Tab` previous |
| `Ctrl+1-9` | Pane by number | `Alt+1-9` |
| `Ctrl+Z/Y` | Undo/Redo | Standard editing |

### Performance Guidelines

| Operation | Target Time | Optimization |
|-----------|-------------|--------------|
| Widget creation | < 50ms | Use placeholders for slow widgets |
| Layout restoration | < 200ms | Cache widget instances |
| Save workspace | < 100ms | Async file operations |
| Pane switching | < 16ms | Avoid heavy focus handlers |
| Split operation | < 30ms | Pre-allocate common widgets |

## Validation Checklist

### Provider Implementation ✓

- [ ] `provide_widget()` handles all expected widget types
- [ ] `widget_closing()` performs proper cleanup
- [ ] Widget IDs are stable across application sessions
- [ ] Error handling for failed widget creation
- [ ] Cache management prevents memory leaks

### Layout Management ✓

- [ ] Workspace save/restore works correctly
- [ ] Template layouts apply without errors
- [ ] Undo/redo preserves widget instances
- [ ] Focus management works with keyboard navigation
- [ ] Layout changes persist across application restarts

### User Experience ✓

- [ ] Keyboard shortcuts are consistent and documented
- [ ] Drag and drop provides visual feedback
- [ ] Context menus appear in appropriate locations
- [ ] Error states show helpful information
- [ ] Performance remains responsive under load

### Integration Quality ✓

- [ ] No memory leaks during extended use
- [ ] File operations don't block the UI
- [ ] Widget states persist correctly
- [ ] Provider gracefully handles missing files/resources
- [ ] Application shutdown is clean and fast

### Production Readiness ✓

- [ ] Crash recovery restores unsaved work
- [ ] Auto-save prevents data loss
- [ ] Large files load without blocking UI
- [ ] Error messages guide user to resolution
- [ ] Accessibility features work correctly

## Related Documents

- **[Integration Guide](integration-guide.md)** - Performance optimization and caching strategies
- **[Extension Guide](extension-guide.md)** - Advanced customization and extension patterns
- **[Widget Provider Architecture](../02-architecture/widget-provider.md)** - Provider pattern design details
- **[Public API Reference](../05-api/public-api.md)** - Complete API documentation
- **[Core Concepts](../01-overview/core-concepts.md)** - Fundamental MultiSplit concepts

---

This usage guide provides the foundation for building production-quality applications with MultiSplit. Focus on implementing robust providers, managing widget lifecycles properly, and providing excellent user experience through keyboard navigation and smart defaults.