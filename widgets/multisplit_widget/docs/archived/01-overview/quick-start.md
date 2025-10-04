# MultiSplit Quick Start Guide

## Overview

This guide gets you up and running with MultiSplit in minutes. We'll build a simple IDE-style interface step by step, showing the core patterns you'll use in any MultiSplit application.

---

## Minimal Example

### Step 1: Basic Setup

```python
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit, QLabel
from vfwidgets_multisplit import MultiSplitWidget, WherePosition

class SimpleIDE(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple IDE")
        self.setGeometry(100, 100, 1200, 800)

        # Create the MultiSplit widget
        self.splitter = MultiSplitWidget()
        self.splitter.set_widget_provider(self)  # Tell it we'll provide widgets
        self.setCentralWidget(self.splitter)

        # Start with a single editor
        editor = QTextEdit()
        editor.setPlainText("# Welcome to MultiSplit!\n# Try splitting this pane.")
        self.splitter.set_root_widget(editor, "editor:welcome.py")

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Called when MultiSplit needs a widget (during restoration)"""
        if widget_id.startswith("editor:"):
            filename = widget_id[7:]  # Remove "editor:" prefix
            editor = QTextEdit()
            editor.setPlainText(f"# Content for {filename}")
            return editor
        elif widget_id.startswith("terminal:"):
            terminal = QLabel("Terminal Placeholder")
            terminal.setStyleSheet("background: black; color: green; padding: 10px;")
            return terminal
        else:
            return QLabel(f"Unknown widget: {widget_id}")

    def widget_closing(self, widget_id: str, widget: QWidget):
        """Called before a widget is removed from layout"""
        print(f"Widget {widget_id} is being closed")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleIDE()
    window.show()
    sys.exit(app.exec())
```

**Run this and you'll see**: A single text editor in a window. Not very exciting yet, but it's the foundation.

### Step 2: Adding Splits

Now let's add some functionality to split panes:

```python
class SimpleIDE(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple IDE with Splits")
        self.setGeometry(100, 100, 1200, 800)

        # Create MultiSplit
        self.splitter = MultiSplitWidget()
        self.splitter.set_widget_provider(self)
        self.setCentralWidget(self.splitter)

        # Add menu for splitting
        self.setup_menus()

        # Start with welcome editor
        editor = QTextEdit()
        editor.setPlainText("# Welcome to MultiSplit!\n# Use menu to add splits.")
        self.splitter.set_root_widget(editor, "editor:welcome.py")

    def setup_menus(self):
        """Create menus for split operations"""
        menubar = self.menuBar()

        # Split menu
        split_menu = menubar.addMenu("Split")

        # Add split actions
        split_menu.addAction("Split Right", self.split_right)
        split_menu.addAction("Split Down", self.split_down)
        split_menu.addAction("Add Terminal", self.add_terminal)
        split_menu.addSeparator()
        split_menu.addAction("Close Current Pane", self.close_current)

        # View menu
        view_menu = menubar.addMenu("View")
        view_menu.addAction("Save Layout", self.save_layout)
        view_menu.addAction("Restore Layout", self.restore_layout)

    def split_right(self):
        """Add a new editor to the right of current pane"""
        current_pane = self.splitter.current_pane_id
        new_editor = QTextEdit()
        new_editor.setPlainText("# New editor split to the right")

        self.splitter.split_with_widget(
            current_pane,
            WherePosition.RIGHT,
            new_editor,
            f"editor:untitled-{len(self.splitter.all_pane_ids)}.py"
        )

    def split_down(self):
        """Add a new editor below current pane"""
        current_pane = self.splitter.current_pane_id
        new_editor = QTextEdit()
        new_editor.setPlainText("# New editor split below")

        self.splitter.split_with_widget(
            current_pane,
            WherePosition.BOTTOM,
            new_editor,
            f"editor:bottom-{len(self.splitter.all_pane_ids)}.py"
        )

    def add_terminal(self):
        """Add a terminal-like widget"""
        current_pane = self.splitter.current_pane_id
        terminal = QLabel("$ Terminal ready for commands")
        terminal.setStyleSheet("""
            background: #1e1e1e;
            color: #00ff00;
            padding: 10px;
            font-family: 'Courier New', monospace;
        """)

        self.splitter.split_with_widget(
            current_pane,
            WherePosition.BOTTOM,
            terminal,
            f"terminal:{len(self.splitter.all_pane_ids)}"
        )

    def close_current(self):
        """Close the currently focused pane"""
        current_pane = self.splitter.current_pane_id
        if current_pane:
            self.splitter.close_pane(current_pane)

    def save_layout(self):
        """Save current layout to file"""
        layout = self.splitter.save_layout()
        import json
        with open("layout.json", "w") as f:
            json.dump(layout, f, indent=2)
        print("Layout saved to layout.json")

    def restore_layout(self):
        """Restore layout from file"""
        try:
            import json
            with open("layout.json", "r") as f:
                layout = json.load(f)
            self.splitter.restore_layout(layout)
            print("Layout restored from layout.json")
        except FileNotFoundError:
            print("No saved layout found")

    # Widget provider methods (same as before)
    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        if widget_id.startswith("editor:"):
            filename = widget_id[7:]
            editor = QTextEdit()
            editor.setPlainText(f"# Content for {filename}")
            return editor
        elif widget_id.startswith("terminal:"):
            terminal = QLabel("$ Terminal ready for commands")
            terminal.setStyleSheet("""
                background: #1e1e1e; color: #00ff00; padding: 10px;
                font-family: 'Courier New', monospace;
            """)
            return terminal
        else:
            return QLabel(f"Unknown widget: {widget_id}")

    def widget_closing(self, widget_id: str, widget: QWidget):
        print(f"Widget {widget_id} is being closed")
```

**Try this**: Use the Split menu to create a complex layout, then save and restore it.

---

## Key Patterns

### Pattern 1: Widget Provider

The widget provider is your bridge between MultiSplit and your application:

```python
def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
    """
    This method is called when MultiSplit needs a widget.
    It happens during:
    - Layout restoration
    - Undo operations that re-create panes
    """

    # Parse your widget ID format
    widget_type, params = widget_id.split(":", 1)

    # Create appropriate widget
    if widget_type == "editor":
        return self.create_editor(params)
    elif widget_type == "terminal":
        return self.create_terminal(params)
    elif widget_type == "browser":
        return self.create_browser(params)
    else:
        # Always provide a fallback
        return QLabel(f"Unknown widget: {widget_id}")
```

### Pattern 2: Widget IDs

Choose a consistent format for widget IDs:

```python
# Option 1: Type:Parameter format
"editor:main.py"
"terminal:session-1"
"browser:https://example.com"

# Option 2: Hierarchical format
"project:myapp:editor:src/main.py"
"workspace:debug:terminal:gdb"

# Option 3: UUID format (when no natural ID)
"editor:550e8400-e29b-41d4-a716-446655440000"

# The key: Make them meaningful to YOUR application
```

### Pattern 3: Split Operations

All layout changes use the same patterns:

```python
# Split current pane
current_pane = self.splitter.current_pane_id
self.splitter.split_with_widget(
    current_pane,           # Which pane to split
    WherePosition.RIGHT,    # Where to add new pane
    widget,                 # Widget instance to display
    "editor:new_file.py"    # Widget ID for restoration
)

# Replace current widget
self.splitter.replace_widget(
    current_pane,
    new_widget,
    "terminal:session-2"
)

# Close pane
self.splitter.close_pane(current_pane)
```

### Pattern 4: Navigation

MultiSplit provides built-in navigation:

```python
# Focus specific pane
self.splitter.focus_pane("pane-123")

# Navigate between panes
self.splitter.focus_next_pane()
self.splitter.focus_previous_pane()

# Get current state
current = self.splitter.current_pane_id
all_panes = self.splitter.all_pane_ids
```

### Pattern 5: Persistence

Save and restore layouts easily:

```python
def save_workspace(self):
    """Save complete workspace state"""
    workspace = {
        # MultiSplit saves layout structure
        "layout": self.splitter.save_layout(),

        # Application saves widget-specific state
        "widget_states": self.save_all_widget_states(),

        # Application saves other state
        "window_geometry": self.saveGeometry().data(),
        "last_file": self.current_file_path,
    }

    with open("workspace.json", "w") as f:
        json.dump(workspace, f, indent=2)

def restore_workspace(self):
    """Restore complete workspace state"""
    with open("workspace.json", "r") as f:
        workspace = json.load(f)

    # Restore application state first
    self.restoreGeometry(workspace["window_geometry"])
    self.current_file_path = workspace.get("last_file")

    # Prepare widget states for provider
    self.widget_states = workspace["widget_states"]

    # Restore layout (this triggers provide_widget calls)
    self.splitter.restore_layout(workspace["layout"])
```

---

## Common Use Cases

### Use Case 1: Code Editor

```python
class CodeEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.splitter = MultiSplitWidget()
        self.splitter.set_widget_provider(self)
        self.setCentralWidget(self.splitter)

        # Track open files
        self.open_files = {}

    def open_file(self, file_path: str):
        """Open file in current pane or split"""
        # Create editor widget
        editor = QTextEdit()
        with open(file_path, 'r') as f:
            editor.setPlainText(f.read())

        # Track the file
        widget_id = f"editor:{file_path}"
        self.open_files[file_path] = editor

        # Add to layout
        if self.splitter.root_is_split:
            # Split current pane
            self.splitter.split_with_widget(
                self.splitter.current_pane_id,
                WherePosition.RIGHT,
                editor,
                widget_id
            )
        else:
            # Replace root widget
            self.splitter.set_root_widget(editor, widget_id)

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Recreate editor for file"""
        if widget_id.startswith("editor:"):
            file_path = widget_id[7:]
            try:
                editor = QTextEdit()
                with open(file_path, 'r') as f:
                    editor.setPlainText(f.read())
                return editor
            except FileNotFoundError:
                label = QLabel(f"File not found: {file_path}")
                label.setStyleSheet("color: red; padding: 20px;")
                return label
        return QLabel(f"Unknown: {widget_id}")
```

### Use Case 2: Terminal Multiplexer

```python
class TerminalMultiplexer(QWidget):
    def __init__(self):
        super().__init__()
        self.splitter = MultiSplitWidget()
        self.splitter.set_widget_provider(self)

        layout = QVBoxLayout()
        layout.addWidget(self.splitter)
        self.setLayout(layout)

        # Start with one terminal
        self.terminal_count = 0
        self.new_terminal()

    def new_terminal(self):
        """Create a new terminal"""
        self.terminal_count += 1
        terminal = self.create_terminal_widget()
        widget_id = f"terminal:{self.terminal_count}"

        if self.splitter.root_is_split:
            # Split existing layout
            self.splitter.split_with_widget(
                self.splitter.current_pane_id,
                WherePosition.BOTTOM,
                terminal,
                widget_id
            )
        else:
            # First terminal
            self.splitter.set_root_widget(terminal, widget_id)

    def create_terminal_widget(self):
        """Create terminal-like widget"""
        terminal = QTextEdit()
        terminal.setStyleSheet("""
            background: #000;
            color: #0f0;
            font-family: 'Courier New', monospace;
            font-size: 12pt;
        """)
        terminal.setPlainText(f"Terminal {self.terminal_count + 1}\n$ ")
        return terminal

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Recreate terminal"""
        if widget_id.startswith("terminal:"):
            return self.create_terminal_widget()
        return QLabel(f"Unknown: {widget_id}")
```

### Use Case 3: Data Dashboard

```python
class DataDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.splitter = MultiSplitWidget()
        self.splitter.set_widget_provider(self)
        self.setCentralWidget(self.splitter)

        self.create_initial_layout()

    def create_initial_layout(self):
        """Create 2x2 grid of plots"""
        # Start with top-left plot
        plot1 = self.create_plot("Dataset A")
        self.splitter.set_root_widget(plot1, "plot:dataset-a")

        # Split right for top-right
        plot2 = self.create_plot("Dataset B")
        self.splitter.split_with_widget(
            self.splitter.current_pane_id,
            WherePosition.RIGHT,
            plot2,
            "plot:dataset-b"
        )

        # Split both top panes down
        all_panes = self.splitter.all_pane_ids[:]  # Copy list
        for i, pane_id in enumerate(all_panes):
            plot = self.create_plot(f"Dataset {chr(67 + i)}")  # C, D, etc.
            self.splitter.split_with_widget(
                pane_id,
                WherePosition.BOTTOM,
                plot,
                f"plot:dataset-{chr(97 + i + 2)}"  # c, d, etc.
            )

    def create_plot(self, title: str):
        """Create a plot widget placeholder"""
        plot = QLabel(f"📊 {title}\n\n[Plot visualization would go here]")
        plot.setAlignment(Qt.AlignCenter)
        plot.setStyleSheet("""
            border: 2px solid #ccc;
            background: #f9f9f9;
            font-size: 14pt;
            padding: 20px;
        """)
        return plot

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Recreate plot widget"""
        if widget_id.startswith("plot:"):
            dataset_name = widget_id[5:].replace("-", " ").title()
            return self.create_plot(f"Dataset {dataset_name}")
        return QLabel(f"Unknown: {widget_id}")
```

---

## Keyboard Shortcuts

Add keyboard shortcuts for common operations:

```python
from PySide6.QtGui import QShortcut, QKeySequence

class IDEWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # ... setup code ...
        self.setup_shortcuts()

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Splitting
        QShortcut(QKeySequence("Ctrl+D"), self, self.split_right)
        QShortcut(QKeySequence("Ctrl+Shift+D"), self, self.split_down)

        # Navigation
        QShortcut(QKeySequence("Ctrl+Tab"), self, self.splitter.focus_next_pane)
        QShortcut(QKeySequence("Ctrl+Shift+Tab"), self, self.splitter.focus_previous_pane)

        # Layout
        QShortcut(QKeySequence("Ctrl+W"), self, self.close_current_pane)
        QShortcut(QKeySequence("Ctrl+Z"), self, self.splitter.undo)
        QShortcut(QKeySequence("Ctrl+Y"), self, self.splitter.redo)

    def split_right(self):
        """Split current pane to the right"""
        current = self.splitter.current_pane_id
        widget = self.create_new_widget()
        self.splitter.split_with_widget(current, WherePosition.RIGHT, widget, "new_widget")

    def close_current_pane(self):
        """Close current pane with confirmation"""
        if len(self.splitter.all_pane_ids) > 1:  # Don't close last pane
            self.splitter.close_pane(self.splitter.current_pane_id)
```

---

## Error Handling

Handle edge cases gracefully:

```python
def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
    """Robust widget provider with error handling"""
    try:
        # Parse widget ID
        if ":" not in widget_id:
            raise ValueError(f"Invalid widget ID format: {widget_id}")

        widget_type, params = widget_id.split(":", 1)

        # Create widget based on type
        if widget_type == "editor":
            return self.create_editor(params)
        elif widget_type == "terminal":
            return self.create_terminal(params)
        else:
            # Unknown type - return placeholder
            return self.create_error_widget(f"Unknown widget type: {widget_type}")

    except Exception as e:
        # Any error - return error widget
        return self.create_error_widget(f"Error creating widget: {e}")

def create_error_widget(self, message: str) -> QWidget:
    """Create widget to display errors"""
    error_widget = QLabel(f"⚠️ Error\n\n{message}")
    error_widget.setStyleSheet("""
        background: #ffeeee;
        border: 2px solid #cc0000;
        color: #cc0000;
        padding: 20px;
        font-size: 12pt;
    """)
    error_widget.setAlignment(Qt.AlignCenter)
    return error_widget

def widget_closing(self, widget_id: str, widget: QWidget):
    """Save state before widget closes"""
    try:
        # Save widget state if it supports it
        if hasattr(widget, 'save_state'):
            state = widget.save_state()
            self.widget_states[widget_id] = state

        # Clean up resources
        if hasattr(widget, 'cleanup'):
            widget.cleanup()

    except Exception as e:
        print(f"Error saving state for {widget_id}: {e}")
```

---

## Next Steps

Now that you have the basics working:

1. **Read the Architecture Docs** - [MVC Architecture](../02-architecture/mvc-architecture.md) and [Widget Provider](../02-architecture/widget-provider.md)

2. **Check the API Reference** - [Public API](../05-api/public-api.md) for all available methods

3. **See Usage Patterns** - [Usage Guide](../06-guides/usage-guide.md) for advanced patterns

4. **Integration Details** - [Integration Guide](../06-guides/integration-guide.md) for production use

## Quick Reference

### Essential Methods
```python
# Setup
splitter = MultiSplitWidget()
splitter.set_widget_provider(provider)

# Layout operations
splitter.set_root_widget(widget, widget_id)
splitter.split_with_widget(pane_id, where, widget, widget_id)
splitter.replace_widget(pane_id, widget, widget_id)
splitter.close_pane(pane_id)

# Navigation
splitter.focus_pane(pane_id)
splitter.focus_next_pane()
current = splitter.current_pane_id

# Persistence
layout = splitter.save_layout()
splitter.restore_layout(layout)

# Undo/Redo
splitter.undo()
splitter.redo()
can_undo = splitter.can_undo()
```

### Position Constants
```python
from vfwidgets_multisplit import WherePosition

WherePosition.LEFT    # Split to the left
WherePosition.RIGHT   # Split to the right
WherePosition.TOP     # Split above
WherePosition.BOTTOM  # Split below
```

### Widget Provider Template
```python
def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
    # Parse ID and create appropriate widget
    # Always return a QWidget (use error widget for failures)
    pass

def widget_closing(self, widget_id: str, widget: QWidget):
    # Save state, clean up resources
    pass
```

---

You're now ready to build sophisticated split-pane interfaces with MultiSplit!