# VFWidgets MultisplitWidget

A dynamic split-pane widget for PySide6 with vim-inspired keyboard navigation and flexible widget provider pattern.

## Installation

```bash
# Install from local path
pip install ./widgets/multisplit_widget

# Install in editable mode for development
pip install -e ./widgets/multisplit_widget

# Install with development dependencies
pip install -e "./widgets/multisplit_widget[dev]"
```

## Quick Start

### Basic Usage with WidgetProvider

```python
from PySide6.QtWidgets import QApplication, QTextEdit
from vfwidgets_multisplit import MultisplitWidget, WidgetProvider, WherePosition

class TextEditorProvider(WidgetProvider):
    """Provides QTextEdit widgets on demand."""

    def provide_widget(self, widget_id: str, pane_id: str):
        """Called when MultisplitWidget needs a widget for a pane."""
        return QTextEdit(f"Editor {widget_id}")

app = QApplication([])

# CRITICAL: Provider MUST be in constructor!
provider = TextEditorProvider()
widget = MultisplitWidget(provider=provider)
widget.show()

app.exec()
```

## Features

- **Dynamic splitting**: Split panes horizontally or vertically at runtime
- **Lazy widget creation**: Widgets created on-demand via WidgetProvider pattern
- **Keyboard navigation**: Vim-inspired focus movement between panes
- **Drag-to-resize**: Interactive pane resizing with live preview - grab dividers with mouse to adjust split ratios in real-time
- **Focus management**: Track and manage focus across multiple panes
- **Session persistence**: Save and restore pane layouts
- **Theme-aware dividers**: Dividers automatically use theme colors with hover effects (vfwidgets_theme integration)
- **Customizable styling**: Configure divider appearance with SplitterStyle (minimal/compact/comfortable presets)
- **QWebEngineView optimized**: Smart rendering prevents GPU compositor flash when resizing web-based widgets (terminals, browsers)

## Critical: WidgetProvider Pattern

### ❌ Wrong Approach

**Do NOT try to set provider after construction:**
```python
# ❌ WRONG - set_widget_provider() does NOT exist!
multisplit = MultisplitWidget()
multisplit.set_widget_provider(provider)  # ERROR: Method doesn't exist!
```

### ✅ Correct Approach

**Provider MUST be passed in constructor:**
```python
# ✅ CORRECT - Provider in constructor
provider = MyWidgetProvider()
multisplit = MultisplitWidget(provider=provider)
```

**Why this matters:**
- MultisplitWidget initializes the first pane during `__init__()`
- The provider is needed immediately to create the initial widget
- There is no setter method - provider must be in constructor
- Missing provider results in placeholder widgets with "No provider available" warning

See [examples/01_basic_text_editor.py](examples/01_basic_text_editor.py) for the complete pattern.

## API Reference

### Import Paths

**All public types available from main package** (v0.2.0+):

```python
from vfwidgets_multisplit import (
    MultisplitWidget,    # Main widget
    WidgetProvider,      # Provider base class
    WherePosition,       # Split positions (LEFT/RIGHT/TOP/BOTTOM)
    Direction,           # Navigation directions (UP/DOWN/LEFT/RIGHT)
    SplitterStyle,       # Divider styling configuration
)
```

**Legacy import paths** (deprecated but still supported):
```python
# Old way - still works but not recommended
from vfwidgets_multisplit.view.container import WidgetProvider
from vfwidgets_multisplit.core.types import WherePosition
```

### Split Operations

```python
from vfwidgets_multisplit import MultisplitWidget, WherePosition

# Split pane horizontally (vertical divider)
multisplit.split_pane(
    pane_id="pane_123",
    widget_id="editor-2",
    position=WherePosition.RIGHT,
    ratio=0.5
)

# Split pane vertically (horizontal divider)
multisplit.split_pane(
    pane_id="pane_123",
    widget_id="editor-3",
    position=WherePosition.BOTTOM,
    ratio=0.5
)

# Get currently focused pane
focused_pane = multisplit.get_focused_pane()

# Remove a pane
multisplit.remove_pane(pane_id)
```

### Drag-to-Resize

Drag-to-resize is **enabled by default** with live preview:

**How it works:**
1. Hover over any divider between panes - cursor changes to resize arrows
2. Click and drag the divider to adjust split ratios
3. Visual feedback updates in real-time as you drag
4. Release mouse to commit the new ratios (undo/redo supported)

**Behavior:**
- **Live preview**: Pane sizes update immediately during drag
- **Smooth interaction**: 60 FPS polling for responsive feel
- **Theme integration**: Dividers show hover effects (if vfwidgets_theme available)
- **Constraints**: Respects minimum pane sizes (default 50x50 pixels)

**No configuration needed** - just use the widget and drag dividers!

### Widget IDs

Widget IDs are **user-defined unique strings** passed to your `WidgetProvider`:

```python
class MyProvider(WidgetProvider):
    def provide_widget(self, widget_id: str, pane_id: str):
        # widget_id is what YOU provide when creating/splitting panes
        # pane_id is generated by MultisplitWidget

        if widget_id.startswith("file:"):
            filepath = widget_id[5:]
            return FileEditor(filepath)
        else:
            return NewEditor(widget_id)

# Simple IDs
multisplit.split_pane(pane_id, "editor-1", WherePosition.RIGHT)
multisplit.split_pane(pane_id, "editor-2", WherePosition.BOTTOM)

# Complex IDs
multisplit.split_pane(pane_id, "file:/path/to/file.txt", WherePosition.RIGHT)

# Default ID (used by auto-initialization)
# When MultisplitWidget is created, it auto-initializes with widget_id="default"
```

### Focus Management

MultisplitWidget provides signals for managing focus after pane operations:

```python
# Connect to pane_added signal for automatic focus
multisplit.pane_added.connect(lambda pane_id: multisplit.focus_pane(pane_id))

# Or with custom logic
def on_pane_added(pane_id: str):
    # Only focus if this was from a split operation
    if should_auto_focus:
        multisplit.focus_pane(pane_id)
        print(f"Focused new pane: {pane_id}")

multisplit.pane_added.connect(on_pane_added)

# Available signals
multisplit.pane_added      # Signal(str) - emitted when pane is created
multisplit.pane_focused    # Signal(str) - emitted when pane gains focus
multisplit.pane_removed    # Signal(str) - emitted when pane is removed
```

**Important for QWebEngineView-based widgets**: If your widgets use `QWebEngineView` (terminals, browsers, web views), you need to override `setFocus()` to properly handle programmatic focus. See the [Focus Management Guide](docs/focus-management-GUIDE.md) for details.

### Auto-Focus on Pane Closure

When removing panes (either manually or programmatically), you may want to automatically focus a sibling pane to maintain workflow continuity. This "undo split" pattern is especially useful for terminal emulators and editors.

**Pattern: Auto-focus sibling on close**

```python
def close_pane_with_auto_focus(multisplit, pane_id):
    """Close a pane and automatically focus its sibling (undo split pattern)."""
    # Get the pane's parent to find sibling
    from vfwidgets_multisplit.core.nodes import LeafNode
    from vfwidgets_multisplit.core.types import PaneId

    pane_node = multisplit._model.get_pane(PaneId(pane_id))

    # Find sibling pane before removal
    next_focus = None
    if pane_node and pane_node.parent:
        for child in pane_node.parent.children:
            if isinstance(child, LeafNode) and str(child.pane_id) != pane_id:
                next_focus = str(child.pane_id)
                break

    # Remove pane
    multisplit.remove_pane(pane_id)

    # Auto-focus sibling
    if next_focus:
        multisplit.focus_pane(next_focus)

# Usage example: Manual pane close (Ctrl+W)
def on_close_pane_shortcut():
    focused = multisplit.get_focused_pane()
    if focused:
        close_pane_with_auto_focus(multisplit, focused)

# Usage example: Programmatic close (e.g., terminal exit)
def on_terminal_exit(session_id):
    pane_id = get_pane_for_session(session_id)
    if pane_id:
        close_pane_with_auto_focus(multisplit, pane_id)
```

**Benefits:**
- Seamless UX - no manual clicking required after close
- Mimics "undo split" behavior - focus returns to sibling
- Works for both manual (keyboard shortcut) and programmatic (widget signal) closures

**Real-world example**: ViloxTerm uses this pattern for both Ctrl+W (manual close) and terminal exit (auto-close) to maintain focus continuity.

### Divider Styling

Customize divider appearance with `SplitterStyle`:

```python
from vfwidgets_multisplit import MultisplitWidget, SplitterStyle

# Minimal style (1px dividers - good for terminals)
style = SplitterStyle.minimal()
multisplit = MultisplitWidget(provider=provider, splitter_style=style)

# Compact style (3px dividers)
style = SplitterStyle.compact()
multisplit = MultisplitWidget(provider=provider, splitter_style=style)

# Comfortable style (6px dividers - DEFAULT)
style = SplitterStyle.comfortable()  # This is the default
multisplit = MultisplitWidget(provider=provider, splitter_style=style)

# Custom style with specific colors
style = SplitterStyle(
    handle_width=4,
    handle_bg="#1e1e1e",           # Normal background
    handle_hover_bg="#007acc",      # Hover background
    handle_hover_border="#0098ff",  # Hover border
    show_hover_effect=True,
    cursor_on_hover=True
)
multisplit = MultisplitWidget(provider=provider, splitter_style=style)
```

**Theme Integration:**
- If `vfwidgets_theme` is available, dividers automatically use theme colors
- Custom colors override theme defaults
- Colors support hex format (`#RRGGBB`) or named colors (`"blue"`)

**Available Presets:**
- `SplitterStyle.minimal()` - 1px handles, no margins (terminal emulators)
- `SplitterStyle.compact()` - 3px handles, 1px margins
- `SplitterStyle.comfortable()` - 6px handles, 2px margins (default)

## Development

```bash
# Run tests
cd widgets/multisplit_widget
pytest

# Format code
black src/

# Lint
ruff check src/

# Type check
mypy src/
```

## API Documentation

See [API documentation](docs/api.md) for detailed usage.

## Examples

Check the `examples/` directory for usage examples:
- `basic_usage.py` - Simple usage example
- `advanced_features.py` - Advanced features demonstration

## License

MIT License - See LICENSE file for details.
