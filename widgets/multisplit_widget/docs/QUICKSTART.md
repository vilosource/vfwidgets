# MultisplitWidget Quick Start

Get started with MultisplitWidget in 5 minutes. This guide shows you the essential pattern for building dynamic split-pane interfaces.

## Installation

```bash
pip install vfwidgets-multisplit
```

## The 3-Step Pattern

Every MultisplitWidget application follows this pattern:

1. **Create a WidgetProvider** - defines what widgets go in panes
2. **Create MultisplitWidget** - the layout container
3. **Split panes dynamically** - at runtime, based on user actions

## Minimal Example

```python
#!/usr/bin/env python3
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit
from vfwidgets_multisplit import MultisplitWidget, WherePosition, WidgetProvider

class MyProvider(WidgetProvider):
    """Step 1: Define what widgets to create"""

    def provide_widget(self, widget_id: str, pane_id: str):
        editor = QTextEdit()
        editor.setPlainText(f"Editor: {widget_id}")
        return editor

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Step 2: Create MultisplitWidget with provider
        self.multisplit = MultisplitWidget(provider=MyProvider())
        self.setCentralWidget(self.multisplit)

        # Initialize with first editor
        self.multisplit.initialize_empty("editor-1")

        # Step 3: Split panes dynamically
        focused = self.multisplit.get_focused_pane()
        self.multisplit.split_pane(focused, "editor-2", WherePosition.RIGHT, 0.5)

if __name__ == "__main__":
    app = QApplication([])
    window = MyApp()
    window.show()
    app.exec()
```

**Result**: A window with two text editors side-by-side.

## Understanding the Pattern

### WidgetProvider

The provider creates widgets on demand:

```python
class MyProvider(WidgetProvider):
    def provide_widget(self, widget_id: str, pane_id: str):
        """Called when a new pane is created"""
        # widget_id identifies WHAT to create (e.g., "editor-1", "file:/path")
        # pane_id identifies WHERE it goes (unique pane ID)
        return my_widget

    def widget_closing(self, widget_id: str, pane_id: str, widget):
        """Optional: called before widget removal"""
        # Clean up, save state, etc.
        pass
```

### Split Operations

```python
# Get focused pane
focused = multisplit.get_focused_pane()

# Split it horizontally (new pane on right)
multisplit.split_pane(focused, "new-widget-id", WherePosition.RIGHT, 0.5)

# Split vertically (new pane on bottom)
multisplit.split_pane(focused, "another-id", WherePosition.BOTTOM, 0.5)
```

### Focus Management

```python
# Track focus changes (v0.2.0+)
multisplit.focus_changed.connect(on_focus_changed)

def on_focus_changed(old_pane_id: str, new_pane_id: str):
    print(f"Focus: {old_pane_id} -> {new_pane_id}")
```

## Common Patterns

### Pattern 1: Different Widget Types

```python
class MultiTypeProvider(WidgetProvider):
    def provide_widget(self, widget_id: str, pane_id: str):
        # Parse widget_id to determine type
        if widget_id.startswith("editor:"):
            return QTextEdit()
        elif widget_id.startswith("terminal:"):
            return TerminalWidget()
        elif widget_id.startswith("browser:"):
            return WebView()
```

### Pattern 2: File-Based Widgets

```python
class FileProvider(WidgetProvider):
    def provide_widget(self, widget_id: str, pane_id: str):
        if widget_id.startswith("file:"):
            file_path = widget_id[5:]  # Remove "file:" prefix
            editor = QTextEdit()
            with open(file_path) as f:
                editor.setPlainText(f.read())
            return editor
```

### Pattern 3: Focus-Aware Actions

```python
def split_current():
    """Split the currently focused pane"""
    focused = multisplit.get_focused_pane()
    if focused:
        multisplit.split_pane(focused, "new-widget", WherePosition.RIGHT, 0.5)

def close_current():
    """Close the currently focused pane"""
    focused = multisplit.get_focused_pane()
    if focused:
        multisplit.remove_pane(focused)
```

## Widget Lookup (v0.2.0+)

Access widgets in panes:

```python
# Get widget in a specific pane
widget = multisplit.get_widget(pane_id)

# Get all widgets
all_widgets = multisplit.get_all_widgets()  # dict[pane_id, widget]

# Find pane containing a widget
pane_id = multisplit.find_pane_by_widget(my_widget)
```

## Next Steps

1. **Explore Examples** - See `examples/` for complete applications:
   - `01_basic_text_editor.py` - Multi-document text editor
   - `02_tabbed_split_panes.py` - Tabs + splitting
   - `03_keyboard_driven_splitting.py` - Vim-like controls

2. **Read the Guide** - See [GUIDE.md](GUIDE.md) for best practices and advanced patterns

3. **API Reference** - See [API.md](API.md) for complete API documentation

4. **Migration** - Upgrading from v0.1.x? See [MIGRATION.md](MIGRATION.md)

## Key Insights

- **You can split ANY pane at ANY time** - This is what makes MultisplitWidget powerful
- **MultisplitWidget handles layout** - You just provide widgets through the provider
- **Focus tracking is automatic** - Use signals to react to focus changes
- **Widget lookup is built-in** - No need to manually track widgets (v0.2.0+)

Ready to build? Start with the examples and customize from there!
