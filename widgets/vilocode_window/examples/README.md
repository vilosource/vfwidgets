# ViloCodeWindow Examples

This directory contains **5 progressive examples** that teach you how to use ViloCodeWindow, from minimal "Hello World" to production-ready IDE patterns.

## Learning Path

### 01_minimal.py - Hello World (★☆☆☆☆)
**What you'll learn:** The absolute basics
- Creating a ViloCodeWindow
- Setting main content
- Status messages
- ~30 lines of code

**Start here if:** You've never used ViloCodeWindow before

```bash
python examples/01_minimal.py
```

### 02_basic_layout.py - VS Code Layout Basics (★★☆☆☆)
**What you'll learn:** The 3-column layout pattern
- Activity bar with icons
- Sidebar with multiple panels
- Connecting components with signals
- File explorer implementation
- ~150 lines of code

**Start here if:** You understand the basics and want to build a simple IDE layout

```bash
python examples/02_basic_layout.py
```

### 03_full_layout.py - Complete IDE Layout (★★★☆☆)
**What you'll learn:** All four components together
- Activity bar + Sidebar + Main content + Auxiliary bar
- Multiple sidebar panels (Explorer, Search, Git)
- Auxiliary bar for secondary content (Outline)
- Full component integration
- ~250 lines of code

**Start here if:** You want to see the complete VS Code layout in action

```bash
python examples/03_full_layout.py
```

### 04_customization.py - Customization & Features (★★★★☆)
**What you'll learn:** Advanced customization
- Menu bar integration
- Keyboard shortcuts (default + custom)
- Theme system integration
- Frameless vs Embedded modes
- Status bar customization
- ~200 lines of code

**Start here if:** You need menus, shortcuts, or theme integration

```bash
python examples/04_customization.py
```

### 05_advanced_ide.py - Real-World IDE (★★★★★)
**What you'll learn:** Production-ready patterns
- Tab widget for multiple files
- Working file I/O operations
- Search functionality with results
- **Styling main pane widgets with theme system**
- Getting theme colors dynamically
- Extensible architecture
- Best practices for real IDEs
- ~400 lines of code

**Start here if:** You're building a real IDE and want to see best practices

```bash
python examples/05_advanced_ide.py
```

## Quick Reference

### Public API Demonstrated

| Feature | Example | Methods Used |
|---------|---------|--------------|
| Basic window | 01 | `ViloCodeWindow()`, `set_main_content()` |
| Activity bar | 02, 03 | `add_activity_item()`, `set_active_activity_item()` |
| Sidebar | 02, 03 | `add_sidebar_panel()`, `show_sidebar_panel()`, `toggle_sidebar()` |
| Auxiliary bar | 03 | `set_auxiliary_content()`, `toggle_auxiliary_bar()` |
| Menu bar | 04 | `set_menu_bar()` |
| Shortcuts | 04 | `register_custom_shortcut()`, `get_all_shortcuts()` |
| Status bar | All | `set_status_message()`, `get_status_bar()` |
| Themes | 04 | Automatic via ThemedApplication |
| File operations | 05 | N/A (custom implementation) |

### Signals Demonstrated

| Signal | Example | Description |
|--------|---------|-------------|
| `activity_item_clicked` | 02, 03, 05 | Emitted when activity bar item clicked |
| `sidebar_panel_changed` | 02, 03, 05 | Emitted when sidebar panel changes |
| `sidebar_visibility_changed` | N/A | Emitted when sidebar visibility toggles |
| `auxiliary_bar_visibility_changed` | N/A | Emitted when auxiliary bar visibility toggles |

## Design Principles

All examples follow these principles:

1. **Public API Only** - No access to internal widgets or private methods
2. **Progressive Complexity** - Each example builds on previous concepts
3. **Real Usage** - Examples show practical patterns, not toy demos
4. **Best Practices** - Production-ready code you can copy
5. **Self-Documenting** - Extensive comments explain the "why"

## Common Patterns

### Opening a File
```python
# Example 05 shows the complete pattern
def open_file(path: Path) -> None:
    with open(path, 'r') as f:
        content = f.read()

    editor = QTextEdit()
    editor.setPlainText(content)
    tab_widget.addTab(editor, path.name)
```

### Connecting Components
```python
# Activity bar → Sidebar (Examples 02, 03, 05)
def on_activity_clicked(item_id: str) -> None:
    window.show_sidebar_panel(item_id)

window.activity_item_clicked.connect(on_activity_clicked)

# Sidebar → Activity bar (bidirectional)
def on_panel_changed(panel_id: str) -> None:
    window.set_active_activity_item(panel_id)

window.sidebar_panel_changed.connect(on_panel_changed)
```

### Custom Shortcuts
```python
# Example 04 shows multiple patterns
window.register_custom_shortcut(
    "my_action",           # Unique ID
    "Ctrl+Shift+A",        # Key sequence
    my_callback,           # Callable
    "My Action"            # Description
)
```

### Theme Integration
```python
# Example 04 shows theme detection and switching
from vfwidgets_theme import ThemedApplication

app = ThemedApplication(sys.argv)  # Automatic theming
window = ViloCodeWindow()  # Will be themed automatically
```

### Styling Main Pane Widgets
```python
# Example 05 shows how to style widgets in the main pane using theme colors
from vfwidgets_theme import get_theme_manager

def get_editor_stylesheet() -> str:
    """Get editor stylesheet using theme colors."""
    try:
        theme_manager = get_theme_manager()
        theme = theme_manager.get_current_theme()

        # Get colors from theme
        bg = theme.get_color("editor.background") or "#1e1e1e"
        fg = theme.get_color("editor.foreground") or "#d4d4d4"

        return f"""
            QTextEdit {{
                background-color: {bg};
                color: {fg};
            }}
        """
    except ImportError:
        # Fallback if theme system not available
        return "QTextEdit { background-color: #1e1e1e; color: #d4d4d4; }"

# Apply to your widget
editor = QTextEdit()
editor.setStyleSheet(get_editor_stylesheet())
```

## Archive

The `archive/` directory contains the original 10 examples that were consolidated into these 5 examples. They're kept for reference but the new examples are recommended for learning.

## Dependencies

- **Required**: `vfwidgets-vilocode-window`, `PySide6`
- **Optional**: `vfwidgets-theme` (for theming in example 04)
- **Optional**: `chrome-tabbed-window` (for Chrome-style tabs in example 05)

## Need Help?

1. Start with `01_minimal.py` and work your way up
2. Each example is self-contained and runnable
3. Read the docstrings at the top of each file
4. Check the main README.md for API documentation
5. Look at the test files in `tests/` for more usage patterns

## Contributing

When adding new examples:
- Follow the progressive complexity pattern
- Use public API only (no `window._internal_widget`)
- Add extensive comments explaining the "why"
- Keep examples focused on one main concept
- Update this README with the new example
