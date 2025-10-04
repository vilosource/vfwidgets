# MultisplitWidget Documentation

**Version**: 0.2.0
**Runtime-splittable pane widget for PySide6/PyQt6**

---

## Quick Navigation

| Document | Description |
|----------|-------------|
| **[QUICKSTART.md](QUICKSTART.md)** | Get started in 5 minutes |
| **[API.md](API.md)** | Complete API reference |
| **[GUIDE.md](GUIDE.md)** | Developer guide & best practices |
| **[MIGRATION.md](MIGRATION.md)** | Version migration & API stability |
| **[../examples/](../examples/)** | Working example applications |

---

## What is MultisplitWidget?

MultisplitWidget is a **pure layout container** that manages recursive split-pane interfaces. Think VS Code's editor layout, but as a reusable Qt widget.

### Key Features

- **Runtime Splitting** - Split any pane at any time during execution
- **Focus Management** - Automatic focus tracking with keyboard navigation
- **Session Persistence** - Save and restore complex layouts
- **Widget Provider Pattern** - You provide widgets, MultisplitWidget handles layout
- **MVC Architecture** - Clean separation of concerns

### What It Looks Like

```python
from vfwidgets_multisplit import MultisplitWidget, WherePosition

# Create with provider
multisplit = MultisplitWidget(provider=MyProvider())

# Initialize with first widget
multisplit.initialize_empty("editor-1")

# Split to add more widgets
focused = multisplit.get_focused_pane()
multisplit.split_pane(focused, "editor-2", WherePosition.RIGHT, 0.5)
```

**Result**: Two editors side-by-side, dynamically split at runtime.

---

## Documentation Overview

### [QUICKSTART.md](QUICKSTART.md)

**Get started in 5 minutes**

- Installation
- The 3-step pattern (Provider → MultisplitWidget → Split)
- Minimal working example
- Common patterns
- Links to examples

**Start here** if you're new to MultisplitWidget.

---

### [API.md](API.md)

**Complete API reference for v0.2.0**

- MultisplitWidget class
  - Pane management (split, remove, focus)
  - Widget lookup (get_widget, get_all_widgets, find_pane_by_widget)
  - Navigation (navigate_focus)
  - Session management (save_session, load_session)
  - Signals (pane_added, pane_removed, focus_changed, layout_changed)
- WidgetProvider protocol
  - provide_widget() - create widgets
  - widget_closing() - cleanup hook
- Enums (WherePosition, Direction, SplitterStyle)
- Type aliases and error handling

**Use this** as a reference while coding.

---

### [GUIDE.md](GUIDE.md)

**Developer guide with best practices**

- Core principles (public API only, clean imports)
- WidgetProvider patterns
  - Multi-type providers
  - File-based providers
  - Stateful providers
- Focus management
  - Using focus_changed signal
  - Focus-aware operations
  - Keyboard navigation
- Session persistence
  - Save/load patterns
  - Auto-save
  - Multiple named sessions
- Common patterns
  - IDE layouts
  - Dashboard layouts
  - Dynamic widget creation
  - Widget lookup for operations
- Best practices & troubleshooting
- Performance tips

**Read this** to build production-quality applications.

---

### [MIGRATION.md](MIGRATION.md)

**Version migration & API stability**

- Version strategy (0.x vs 1.0+)
- Migration guide: v0.1.x → v0.2.0
  - Breaking changes (focus_changed signal, private attributes, widget_closing signature)
  - New features (widget lifecycle, lookup APIs)
  - Step-by-step migration
- Common migration issues
- API stability levels
  - Stable APIs
  - Recently stabilized (v0.2.0)
  - Internal APIs to avoid
- Version history
- Future deprecation policy

**Check this** when upgrading between versions.

---

### [../examples/](../examples/)

**Working example applications**

Three progressive examples demonstrating MultisplitWidget capabilities:

1. **01_basic_text_editor.py** - Multi-document text editor
   - Basic WidgetProvider implementation
   - Runtime pane splitting
   - Focus management
   - Widget lookup APIs

2. **02_tabbed_split_panes.py** - Tabs + splitting
   - Complex widget hierarchies (QTabWidget + splitting)
   - Context menus
   - Advanced provider patterns

3. **03_keyboard_driven_splitting.py** - Vim-like controls
   - Keyboard navigation (h/j/k/l)
   - Modal interaction (NORMAL/COMMAND mode)
   - Command palette

**Run these** to see MultisplitWidget in action, then customize for your needs.

---

## Installation

```bash
pip install vfwidgets-multisplit
```

---

## Quick Example

```python
#!/usr/bin/env python3
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit
from vfwidgets_multisplit import MultisplitWidget, WherePosition, WidgetProvider

class SimpleProvider(WidgetProvider):
    def provide_widget(self, widget_id: str, pane_id: str):
        editor = QTextEdit()
        editor.setPlainText(f"Editor: {widget_id}")
        return editor

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.multisplit = MultisplitWidget(provider=SimpleProvider())
        self.setCentralWidget(self.multisplit)

        # Initialize with first editor
        self.multisplit.initialize_empty("editor-1")

        # Split horizontally
        focused = self.multisplit.get_focused_pane()
        self.multisplit.split_pane(focused, "editor-2", WherePosition.RIGHT, 0.5)

if __name__ == "__main__":
    app = QApplication([])
    window = App()
    window.show()
    app.exec()
```

---

## Learning Path

1. **New to MultisplitWidget?**
   → Read [QUICKSTART.md](QUICKSTART.md)
   → Run [examples/01_basic_text_editor.py](../examples/01_basic_text_editor.py)

2. **Building an application?**
   → Read [GUIDE.md](GUIDE.md) for patterns and best practices
   → Keep [API.md](API.md) open as reference
   → Study [examples/](../examples/) for complete implementations

3. **Upgrading from v0.1.x?**
   → Read [MIGRATION.md](MIGRATION.md)
   → Update code following the checklist
   → Check examples for v0.2.0 API usage

4. **Need help?**
   → Check [Troubleshooting](GUIDE.md#troubleshooting) in GUIDE.md
   → Review [Common Issues](MIGRATION.md#common-issues) in MIGRATION.md
   → Open an issue on GitHub

---

## Key Concepts

### WidgetProvider Pattern

You implement a `WidgetProvider` to create widgets on demand:

```python
class MyProvider(WidgetProvider):
    def provide_widget(self, widget_id: str, pane_id: str):
        """Create widget based on widget_id"""
        return MyWidget(widget_id)

    def widget_closing(self, widget_id: str, pane_id: str, widget: QWidget):
        """Optional: cleanup before widget removal"""
        widget.save_state()
```

MultisplitWidget calls these methods automatically during pane lifecycle.

### Runtime Splitting

The core feature - split any pane at any time:

```python
# Get focused pane
focused = multisplit.get_focused_pane()

# Split it
multisplit.split_pane(
    focused,              # pane to split
    "new-widget-id",      # widget_id for new pane
    WherePosition.RIGHT,  # where to place new pane
    0.5                   # split ratio
)
```

No predefined layout - build complex structures dynamically based on user actions.

### Focus Management

Automatic focus tracking with signals:

```python
multisplit.focus_changed.connect(on_focus_changed)

def on_focus_changed(old_pane_id: str, new_pane_id: str):
    print(f"Focus: {old_pane_id} -> {new_pane_id}")
```

Focus-aware operations:

```python
# Split current pane
focused = multisplit.get_focused_pane()
multisplit.split_pane(focused, "widget-id", WherePosition.BOTTOM)

# Close current pane
multisplit.remove_pane(focused)

# Navigate with keyboard
multisplit.navigate_focus(Direction.RIGHT)
```

---

## Architecture

MultisplitWidget follows strict **MVC architecture**:

- **Model** - Tree structure of panes (pure Python, no Qt)
- **View** - Visual rendering with Qt widgets
- **Controller** - Mediates between Model and View

As a user, you interact with the **public API** only. Internal MVC details are hidden.

---

## Version Notes

**Current Version**: 0.2.0

**Major Changes in v0.2.0**:
- Widget lookup APIs (`get_widget`, `get_all_widgets`, `find_pane_by_widget`)
- Improved `focus_changed` signal (old + new pane IDs)
- `widget_closing()` lifecycle hook
- Clean package imports
- Private internal attributes

See [MIGRATION.md](MIGRATION.md) for upgrade guide.

---

## Historical Documentation

Older design documents, implementation plans, and architecture specs have been moved to [archived/](archived/) for reference. These documents capture the development history but are not needed for using MultisplitWidget.

---

## Contributing

Found an issue or have a suggestion?

1. Check the documentation thoroughly
2. Review examples to ensure it's not a usage issue
3. Open an issue on GitHub with:
   - Clear description
   - Minimal reproduction example
   - Expected vs actual behavior

---

## License

[Your license here]

---

**Happy splitting! 🎯**

For questions or support, please open an issue on GitHub.
