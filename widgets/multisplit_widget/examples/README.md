# MultiSplit Widget Examples

This directory contains comprehensive examples demonstrating the power and flexibility of the MultiSplit widget for building dynamic, runtime-splittable user interfaces.

## 🚀 Quick Start

Run the examples launcher for the best experience:

```bash
cd examples/
python run_examples.py
```

The launcher provides a guided tour through all examples with detailed descriptions and easy execution.

## 📚 Learning Progression

The examples are designed as a progressive learning path, with each building on concepts from previous ones:

### 1. Basic Text Editor (`01_basic_text_editor.py`)
**Difficulty:** Beginner
**Focus:** Core runtime splitting concepts

```bash
python 01_basic_text_editor.py
```

**What you'll learn:**
- Basic `WidgetProvider` implementation for text editors
- Runtime pane splitting with user interaction
- Multiple text editors in different panes
- Focus management between editors
- Keyboard shortcuts for splitting operations
- Basic file operations within split panes

**Key insight:** Understanding that you can split ANY pane at ANY time during runtime - this is the fundamental strength of MultiSplit.

---

### 2. Tabbed Split Panes (`02_tabbed_split_panes.py`)
**Difficulty:** Intermediate
**Focus:** Complex widget hierarchies

```bash
python 02_tabbed_split_panes.py
```

**What you'll learn:**
- Combining `QTabWidget` with MultiSplit panes
- Splitting panes that contain complex widgets (tabs)
- Adding new tabs to focused pane
- Focus management between tabs AND panes
- Context menus for advanced interactions
- Working with nested widget patterns

**Key insight:** MultiSplit works seamlessly with arbitrarily complex widget hierarchies - tabs, splitters, custom widgets, etc.

---

### 3. Keyboard-Driven Control (`03_keyboard_driven_splitting.py`)
**Difficulty:** Advanced
**Focus:** Power-user interaction patterns

```bash
python 03_keyboard_driven_splitting.py
```

**What you'll learn:**
- Vim-like keyboard navigation (`h/j/k/l` keys)
- Modal interaction patterns (NORMAL/COMMAND mode)
- Command palette for discoverable actions (`Ctrl+Space`)
- Global keyboard event handling
- Advanced focus navigation patterns
- Building keyboard-first workflows

**Key insight:** Complex layouts become manageable with proper keyboard control - no mouse required for sophisticated operations.

## 🎯 Core Concepts Demonstrated

### Runtime Pane Splitting
The fundamental feature that makes MultiSplit powerful:
- Split any pane at any time during runtime
- Horizontal and vertical splitting
- Keyboard shortcuts and programmatic control
- Focus-aware splitting (split the currently focused pane)

### Widget Provider Pattern
Flexible architecture for creating different content types:
```python
class MyWidgetProvider(WidgetProvider):
    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        # Create and return widget based on widget_id
        return my_custom_widget
```

### Focus Management
Sophisticated focus tracking:
- Click-to-focus on any widget within panes
- Tab navigation between panes
- Focus-aware operations (split focused pane)
- Visual focus indicators

### Session Persistence
Save and restore complex layouts:
- Layout structure preservation
- Widget state persistence
- Workspace management
- Multiple named sessions

## 🛠️ Technical Patterns

### Basic Usage Pattern
```python
from vfwidgets_multisplit import MultisplitWidget, WherePosition, WidgetProvider

# 1. Create a widget provider
class MyProvider(WidgetProvider):
    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        return MyCustomWidget(widget_id)

    def widget_closing(self, widget_id: str, pane_id: str, widget: QWidget) -> None:
        """Optional: cleanup before widget removal"""
        print(f"Widget {widget_id} closing in pane {pane_id}")

# 2. Create MultiSplit widget
provider = MyProvider()
multisplit = MultisplitWidget(provider=provider)

# 3. Initialize with content
multisplit.initialize_empty("my-widget-1")

# 4. Split panes dynamically
focused_pane = multisplit.get_focused_pane()
multisplit.split_pane(focused_pane, "my-widget-2", WherePosition.RIGHT, 0.5)
```

### Advanced Provider Pattern
```python
class AdvancedProvider(WidgetProvider):
    def __init__(self):
        self.widget_types = {
            "editor": self.create_editor,
            "terminal": self.create_terminal,
            "browser": self.create_browser,
        }

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        # Parse widget_id: "type:config"
        widget_type, config = widget_id.split(":", 1) if ":" in widget_id else (widget_id, "")

        creator = self.widget_types.get(widget_type, self.create_default)
        return creator(pane_id, config)
```

### Focus-Aware Operations
```python
# Split the currently focused pane
focused = multisplit.get_focused_pane()
if focused:
    multisplit.split_pane(focused, "new-widget", WherePosition.BOTTOM, 0.5)

# Handle focus changes (v0.2.0+)
multisplit.focus_changed.connect(self.on_focus_changed)

def on_focus_changed(self, old_pane_id: str, new_pane_id: str):
    print(f"Focus changed: {old_pane_id} -> {new_pane_id}")
    if new_pane_id:
        self.update_ui_for_focused_pane(new_pane_id)
```

## 🏗️ Building Your Own Application

Use these examples as templates for building your own applications:

### For Simple Multi-Document Apps
Start with **Example 1** (Basic Text Editor):
- Replace `DocumentEditor` with your document type
- Customize the `WidgetProvider` for your content
- Add file operations specific to your domain
- Use the widget lookup APIs for focus-aware operations

### For Complex Applications with Multiple Widget Types
Use **Example 2** (Tabbed Split Panes) as a foundation:
- Combine complex widgets (tabs, trees, etc.) with splitting
- Handle nested widget hierarchies
- Implement context menus for advanced interactions
- Add domain-specific toolbar and menu actions

### For Keyboard-Driven Tools
Combine patterns from **Example 3** (Keyboard Control):
- Implement modal interaction patterns
- Create custom keyboard shortcuts
- Build command palettes for discoverability
- Add vim-like navigation if appropriate

## 🎨 Customization Points

### Visual Styling
- Pane headers and borders
- Focus indicators
- Split handles and dividers
- Theme integration

### Interaction Patterns
- Keyboard shortcuts
- Context menus
- Drag and drop
- Tool palettes

### Content Types
- Custom editor widgets
- Data visualization panels
- Media viewers
- Communication tools

## 📖 API Reference

### MultisplitWidget
```python
class MultisplitWidget(QWidget):
    # Initialization
    def __init__(self, provider: WidgetProvider = None, parent: QWidget = None)
    def initialize_empty(self, widget_id: str = "default")

    # Pane Management
    def split_pane(self, pane_id: str, widget_id: str, position: WherePosition, ratio: float = 0.5) -> bool
    def remove_pane(self, pane_id: str) -> bool
    def get_pane_ids() -> List[str]
    def get_focused_pane() -> Optional[str]

    # Widget Lookup (v0.2.0+)
    def get_widget(self, pane_id: str) -> Optional[QWidget]
    def get_all_widgets() -> dict[str, QWidget]
    def find_pane_by_widget(self, widget: QWidget) -> Optional[str]

    # Session Management
    def save_session() -> str  # Returns JSON
    def load_session(json_str: str) -> bool

    # Signals
    pane_added = Signal(str)              # pane_id
    pane_removed = Signal(str)            # pane_id
    focus_changed = Signal(str, str)      # old_pane_id, new_pane_id (v0.2.0+)
    layout_changed = Signal()
```

### WidgetProvider Protocol
```python
class WidgetProvider(Protocol):
    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Create widget for the given IDs."""
        ...

    def widget_closing(self, widget_id: str, pane_id: str, widget: QWidget) -> None:
        """Handle widget cleanup before removal (optional, v0.2.0+)."""
        ...
```

### WherePosition Enum
```python
class WherePosition(Enum):
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"
```

## 🔍 Troubleshooting

### Common Issues

**Focus not updating when clicking widgets:**
- Ensure your widgets participate in Qt's focus chain
- Check that event filters are properly installed
- See focus management implementation in examples

**Pane splitting not working:**
- Verify `WidgetProvider.provide_widget()` returns valid widgets
- Check that pane IDs exist before splitting
- Ensure ratio values are between 0.0 and 1.0

**Session restore failing:**
- Confirm widget IDs are consistent between saves/loads
- Verify `WidgetProvider` can recreate widgets from saved IDs
- Check for missing widget configurations

### Performance Considerations

- **Large numbers of panes:** MultiSplit handles hundreds of panes efficiently
- **Complex widgets:** Use lazy loading in `provide_widget()` for expensive widgets
- **Real-time updates:** Throttle update frequencies for data-heavy panes
- **Memory management:** Implement proper cleanup in `widget_closing()`

## 💡 Best Practices

1. **Start Simple:** Begin with basic splitting, add complexity incrementally
2. **Design Widget IDs:** Use structured IDs that encode widget type and configuration
3. **Handle Focus:** Always consider which pane should be focused after operations
4. **Plan for Sessions:** Design your widget IDs to be serializable for session management
5. **Test Edge Cases:** Empty workspaces, single panes, complex nested layouts
6. **User Feedback:** Provide clear visual indicators for focus and available actions

## 🤝 Contributing

Found issues or have improvements? Please contribute back to the project:

1. Test examples with your specific use cases
2. Report bugs with minimal reproduction examples
3. Suggest new example scenarios
4. Contribute additional widget provider patterns

## 📄 License

These examples are provided under the same license as the MultiSplit widget project.

---

**Happy splitting!** 🎯

For questions or support, please refer to the main project documentation or create an issue in the project repository.