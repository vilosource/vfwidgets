# Widget Provider Architecture

## Overview

The Widget Provider pattern is the core mechanism that enables MultiSplit to be a pure layout container without any knowledge of widget types. MultiSplit manages **where** widgets go (layout structure) while the application controls **what** widgets are (creation and lifecycle).

## Prerequisites

The widget provider pattern requires **Phase 0 foundations**:

- **ID Generation**: Unique widget and pane identifiers
- **Signal Bridge**: Connect provider requests to application responses
- **Tree Reconciler**: Determine when widgets are needed/removed
- **Geometry Calculator**: Calculate widget positions and sizes

See [MVP Implementation Plan](../../mvp-implementation-PLAN.md#phase-0-critical-foundations-must-have-first) for Phase 0 details.

---

## Core Principle

**"MultiSplit is a layout choreographer, not a widget factory."**

```python
# ✅ MultiSplit manages layout structure
tree = {
    "type": "split",
    "orientation": "horizontal",
    "children": [
        {"pane_id": "pane-1", "widget_id": "editor:main.py"},  # Where
        {"pane_id": "pane-2", "widget_id": "terminal:1"}       # Where
    ]
}

# ✅ Application manages widget creation
class MyProvider:
    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        if widget_id.startswith("editor:"):
            return CodeEditor(widget_id[7:])  # What
        elif widget_id.startswith("terminal:"):
            return Terminal(int(widget_id[9:]))  # What
```

MultiSplit never creates widgets - it only requests them when needed and provides positions where they should be placed.

---

## Provider Protocol

### Complete Interface

```python
from typing import Protocol, Optional
from PySide6.QtWidgets import QWidget, QMenu

class WidgetProvider(Protocol):
    """Complete widget provider interface for MultiSplit"""

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """
        Create or retrieve a widget for the given ID.

        Args:
            widget_id: Opaque identifier meaningful to application
            pane_id: Where the widget will be placed in layout

        Returns:
            QWidget instance to display in the pane

        Raises:
            WidgetProviderError: If widget cannot be created
        """

    def widget_closing(self, widget_id: str, widget: QWidget) -> None:
        """
        Notification that widget is being removed from layout.

        Args:
            widget_id: The widget's identifier
            widget: The actual widget instance being removed

        Note:
            Save any widget state before this call returns.
            Widget may be destroyed after this call.
        """

    def save_widget_state(self, widget_id: str, widget: QWidget) -> dict:
        """
        Save widget state for persistence.

        Args:
            widget_id: The widget's identifier
            widget: The widget instance

        Returns:
            JSON-serializable state dict
        """

    def restore_widget_state(self, widget_id: str, widget: QWidget,
                           state: dict) -> None:
        """
        Restore widget state from saved data.

        Args:
            widget_id: The widget's identifier
            widget: The widget instance
            state: Previously saved state dict
        """

    def can_close_widget(self, widget_id: str, widget: QWidget) -> bool:
        """
        Check if widget can be closed.

        Returns:
            True if widget can be closed, False to prevent closure
        """

    def get_widget_menu(self, widget_id: str, widget: QWidget) -> Optional[QMenu]:
        """
        Get context menu for widget.

        Returns:
            QMenu instance or None if no menu available
        """
```

### Minimal Interface

For basic usage, only two methods are required:

```python
class BasicProvider:
    """Minimal provider implementation"""

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Create widget - REQUIRED"""
        # Implementation required

    def widget_closing(self, widget_id: str, widget: QWidget) -> None:
        """Widget removal notification - REQUIRED"""
        # Clean up if needed
        pass
```

---

## Widget ID Design

### Opaque to MultiSplit

Widget IDs are **completely opaque** to MultiSplit - it only stores and returns them:

```python
# MultiSplit NEVER interprets these formats
widget_ids = [
    "editor:src/main.py",
    "terminal:session-42",
    "plot:dataset-analysis-1",
    "uuid:550e8400-e29b-41d4-a716-446655440000",
    "view://project/file?line=42",
    "my_app_widget_type_xyz_instance_123"
]

# MultiSplit only:
# 1. Stores them in tree nodes
# 2. Passes them to provider when widgets needed
# 3. Returns them unchanged during serialization
```

### Meaningful to Application

Applications should design widget IDs to be **self-describing**:

```python
# Recommended patterns

# Type:Parameter format
"editor:path/to/file.py"
"terminal:session_id"
"browser:https://example.com"
"plot:dataset_name"

# Hierarchical format
"workspace:project1:editor:main.py"
"view:sidebar:file_tree"
"tool:debugger:breakpoints"

# UUID format (when no natural ID)
"editor:550e8400-e29b-41d4-a716-446655440000"
```

### ID Requirements

1. **Unique within session** - No two active widgets share an ID
2. **Stable across saves** - Same ID produces same widget after save/restore
3. **Meaningful to application** - Application can recreate widget from ID alone
4. **JSON-safe** - No characters that break JSON serialization
5. **URL-safe** - Avoid problematic characters for persistence

---

## Provider Patterns

### Pattern 1: Direct Creation

```python
class DirectProvider:
    """Create fresh widgets on each request"""

    def __init__(self):
        self.widget_states = {}  # Save state between closures

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Create new widget each time"""
        widget_type, param = widget_id.split(":", 1)

        if widget_type == "editor":
            editor = CodeEditor()
            editor.load_file(param)

            # Restore saved state if available
            if widget_id in self.widget_states:
                editor.restore_state(self.widget_states[widget_id])

            return editor

        elif widget_type == "terminal":
            return Terminal(session_id=int(param))

        else:
            return QLabel(f"Unknown widget: {widget_id}")

    def widget_closing(self, widget_id: str, widget: QWidget) -> None:
        """Save state before widget is destroyed"""
        if hasattr(widget, 'save_state'):
            self.widget_states[widget_id] = widget.save_state()
```

### Pattern 2: Widget Pool

```python
class PoolProvider:
    """Reuse widgets when possible"""

    def __init__(self):
        self.widget_pool: dict[str, QWidget] = {}
        self.active_widgets: dict[str, QWidget] = {}

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Get from pool or create new"""

        # Check if we already have this widget active
        if widget_id in self.active_widgets:
            return self.active_widgets[widget_id]

        # Check pool for reusable widget
        if widget_id in self.widget_pool:
            widget = self.widget_pool.pop(widget_id)
            self.active_widgets[widget_id] = widget
            return widget

        # Create new widget
        widget = self._create_widget(widget_id)
        self.active_widgets[widget_id] = widget
        return widget

    def widget_closing(self, widget_id: str, widget: QWidget) -> None:
        """Return widget to pool"""
        if widget_id in self.active_widgets:
            del self.active_widgets[widget_id]

            # Return to pool for reuse
            self.widget_pool[widget_id] = widget

    def _create_widget(self, widget_id: str) -> QWidget:
        """Factory method for widget creation"""
        widget_type, param = widget_id.split(":", 1)

        if widget_type == "editor":
            editor = CodeEditor()
            editor.load_file(param)
            return editor

        # Add more widget types...
        return QLabel(f"Unknown: {widget_id}")
```

### Pattern 3: Factory Registry

```python
class FactoryProvider:
    """Use registered factories for different widget types"""

    def __init__(self):
        self.factories: dict[str, callable] = {}
        self.widget_cache: dict[str, QWidget] = {}

    def register_factory(self, prefix: str, factory: callable):
        """Register a factory for widget type prefix"""
        self.factories[prefix] = factory

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Create widget using registered factory"""

        # Check cache first
        if widget_id in self.widget_cache:
            return self.widget_cache[widget_id]

        # Find appropriate factory
        prefix = widget_id.split(":")[0]
        if prefix in self.factories:
            factory = self.factories[prefix]
            widget = factory(widget_id, pane_id)
            self.widget_cache[widget_id] = widget
            return widget

        # Fallback for unknown types
        return QLabel(f"No factory for: {widget_id}")

    def widget_closing(self, widget_id: str, widget: QWidget) -> None:
        """Clean up widget"""
        if widget_id in self.widget_cache:
            del self.widget_cache[widget_id]
            widget.deleteLater()

# Usage
provider = FactoryProvider()
provider.register_factory("editor", lambda wid, pid: CodeEditor(wid[7:]))
provider.register_factory("terminal", lambda wid, pid: Terminal(int(wid[9:])))
```

### Pattern 4: Async Provider

```python
class AsyncProvider:
    """Handle slow widget creation asynchronously"""

    def __init__(self):
        self.pending_widgets: dict[str, QFuture] = {}
        self.placeholder_widgets: dict[str, QWidget] = {}

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Return placeholder immediately, load real widget async"""

        # Check if real widget already exists
        if widget_id in self.widget_cache:
            return self.widget_cache[widget_id]

        # Create placeholder
        placeholder = QLabel("Loading...")
        placeholder.setAlignment(Qt.AlignCenter)
        self.placeholder_widgets[widget_id] = placeholder

        # Start async creation
        future = self._create_widget_async(widget_id, pane_id)
        future.finished.connect(
            lambda: self._on_widget_ready(widget_id, pane_id, future.result())
        )

        return placeholder

    def _create_widget_async(self, widget_id: str, pane_id: str) -> QFuture:
        """Create widget in background thread"""

        def create_widget():
            # Potentially slow operation
            widget_type, param = widget_id.split(":", 1)
            if widget_type == "editor":
                editor = CodeEditor()
                with open(param, 'r') as f:
                    editor.setPlainText(f.read())  # Slow file I/O
                return editor
            return QLabel(f"Unknown: {widget_id}")

        return QtConcurrent.run(create_widget)

    def _on_widget_ready(self, widget_id: str, pane_id: str, widget: QWidget):
        """Replace placeholder with real widget"""
        if widget_id in self.placeholder_widgets:
            # Signal MultiSplit to replace the placeholder
            self.widget_ready.emit(widget_id, pane_id, widget)
```

---

## Lifecycle Management

### Widget Request Flow

```python
# 1. MultiSplit determines widget is needed
def _reconcile_tree_changes(self, diff: DiffResult):
    for pane_id in diff.added:
        widget_id = self._get_widget_id_for_pane(pane_id)
        self._request_widget(widget_id, pane_id)

# 2. MultiSplit requests widget from provider
def _request_widget(self, widget_id: str, pane_id: str):
    if self.widget_provider:
        widget = self.widget_provider.provide_widget(widget_id, pane_id)
        self._place_widget(pane_id, widget)
    else:
        # Signal for external handling
        self.widget_needed.emit(widget_id, pane_id)

# 3. MultiSplit places widget in layout
def _place_widget(self, pane_id: str, widget: QWidget):
    # Add to widget map
    self.widget_map[pane_id] = widget

    # Update Qt layout structure
    self._update_layout_geometry()
```

### Widget Removal Flow

```python
# 1. MultiSplit determines widget should be removed
def _reconcile_tree_changes(self, diff: DiffResult):
    for pane_id in diff.removed:
        self._remove_widget(pane_id)

# 2. MultiSplit notifies provider before removal
def _remove_widget(self, pane_id: str):
    if pane_id in self.widget_map:
        widget = self.widget_map[pane_id]
        widget_id = self._get_widget_id_for_pane(pane_id)

        # Notify provider
        if self.widget_provider:
            self.widget_provider.widget_closing(widget_id, widget)

        # Signal for external handling
        self.widget_closing.emit(widget_id, widget)

        # Remove from layout
        widget.setParent(None)
        del self.widget_map[pane_id]
```

---

## State Management

### Cooperative Persistence

MultiSplit and the application work together for complete state persistence:

```python
class PersistentApplication:
    """Application with full state persistence"""

    def save_session(self) -> dict:
        """Save complete application session"""

        # MultiSplit saves layout structure
        layout = self.multisplit.save_layout()

        # Application saves widget states
        widget_states = {}
        for pane_id, widget in self.multisplit.get_widget_map().items():
            widget_id = layout['pane_widgets'][pane_id]
            widget_states[widget_id] = self.save_widget_state(widget_id, widget)

        return {
            "layout": layout,
            "widget_states": widget_states,
            "app_settings": self.get_app_settings()
        }

    def restore_session(self, session: dict):
        """Restore complete session"""

        # Prepare widget states for restoration
        self.saved_widget_states = session.get("widget_states", {})

        # Restore app settings
        self.restore_app_settings(session.get("app_settings", {}))

        # Restore layout (triggers widget_needed signals)
        self.multisplit.restore_layout(session["layout"])

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Create widget with restored state"""

        # Create widget
        widget = self.create_widget_from_id(widget_id)

        # Restore saved state if available
        if widget_id in self.saved_widget_states:
            state = self.saved_widget_states[widget_id]
            self.restore_widget_state(widget_id, widget, state)

        return widget
```

### State Synchronization

```python
class StatefulProvider:
    """Provider that maintains widget state"""

    def save_widget_state(self, widget_id: str, widget: QWidget) -> dict:
        """Extract widget state for persistence"""

        state = {"widget_type": type(widget).__name__}

        if isinstance(widget, QTextEdit):
            state.update({
                "text": widget.toPlainText(),
                "cursor_position": widget.textCursor().position(),
                "scroll_position": widget.verticalScrollBar().value()
            })

        elif isinstance(widget, QWebEngineView):
            state.update({
                "url": widget.url().toString(),
                "zoom_factor": widget.zoomFactor(),
                "scroll_position": widget.page().scrollPosition()
            })

        # Add more widget types...

        return state

    def restore_widget_state(self, widget_id: str, widget: QWidget,
                           state: dict) -> None:
        """Apply saved state to widget"""

        if isinstance(widget, QTextEdit):
            widget.setPlainText(state.get("text", ""))

            # Restore cursor position
            cursor = widget.textCursor()
            cursor.setPosition(state.get("cursor_position", 0))
            widget.setTextCursor(cursor)

            # Restore scroll position
            widget.verticalScrollBar().setValue(
                state.get("scroll_position", 0)
            )

        elif isinstance(widget, QWebEngineView):
            widget.load(QUrl(state.get("url", "about:blank")))
            widget.setZoomFactor(state.get("zoom_factor", 1.0))

            # Scroll position restored after load
            def restore_scroll():
                pos = state.get("scroll_position", QPointF(0, 0))
                widget.page().scrollToPosition(pos)

            widget.loadFinished.connect(restore_scroll)
```

---

## Integration Examples

### Complete Application Example

```python
class IDE(QMainWindow):
    """Complete IDE using MultiSplit with provider pattern"""

    def __init__(self):
        super().__init__()

        # Create MultiSplit widget
        self.multisplit = MultiSplitWidget()
        self.multisplit.set_widget_provider(self)
        self.setCentralWidget(self.multisplit)

        # Widget management
        self.editors: dict[str, CodeEditor] = {}
        self.terminals: dict[str, Terminal] = {}
        self.file_tree = FileTreeWidget()

        # Start with file tree
        self.multisplit.set_root_widget(self.file_tree, "file_tree")

        # Connect signals
        self.file_tree.file_opened.connect(self.open_file_in_split)

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Create widgets based on ID format"""

        widget_type, param = widget_id.split(":", 1)

        if widget_type == "editor":
            if widget_id not in self.editors:
                editor = CodeEditor()
                editor.load_file(param)
                self.editors[widget_id] = editor
            return self.editors[widget_id]

        elif widget_type == "terminal":
            if widget_id not in self.terminals:
                terminal = Terminal(session_id=int(param))
                self.terminals[widget_id] = terminal
            return self.terminals[widget_id]

        elif widget_type == "file_tree":
            return self.file_tree

        else:
            return QLabel(f"Unknown widget: {widget_id}")

    def widget_closing(self, widget_id: str, widget: QWidget) -> None:
        """Clean up when widget is removed"""

        # Save any unsaved changes
        if isinstance(widget, CodeEditor) and widget.document().isModified():
            # Prompt to save
            if self.prompt_save_changes(widget):
                widget.save()

        # Remove from tracking
        widget_type = widget_id.split(":")[0]
        if widget_type == "editor" and widget_id in self.editors:
            del self.editors[widget_id]
        elif widget_type == "terminal" and widget_id in self.terminals:
            del self.terminals[widget_id]

    def open_file_in_split(self, file_path: str):
        """Open file in new split pane"""

        widget_id = f"editor:{file_path}"

        # Split current pane
        current_pane = self.multisplit.current_pane_id
        if current_pane:
            # Create widget first
            editor = CodeEditor()
            editor.load_file(file_path)

            # Add to split
            self.multisplit.split_with_widget(
                current_pane,
                WherePosition.RIGHT,
                editor,
                widget_id
            )
```

---

## Error Handling

### Provider Error Recovery

```python
class RobustProvider:
    """Provider with comprehensive error handling"""

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Create widget with fallback on errors"""

        try:
            # Attempt normal widget creation
            widget = self._create_widget(widget_id)
            return widget

        except FileNotFoundError:
            # File-based widget but file missing
            return self._create_error_widget(
                f"File not found: {widget_id}",
                widget_id
            )

        except PermissionError:
            # Access denied
            return self._create_error_widget(
                f"Access denied: {widget_id}",
                widget_id
            )

        except Exception as e:
            # Generic fallback
            return self._create_error_widget(
                f"Error creating widget: {e}",
                widget_id
            )

    def _create_error_widget(self, message: str, widget_id: str) -> QWidget:
        """Create error placeholder widget"""

        error_widget = QWidget()
        layout = QVBoxLayout(error_widget)

        # Error message
        error_label = QLabel(message)
        error_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(error_label)

        # Widget ID for debugging
        id_label = QLabel(f"Widget ID: {widget_id}")
        id_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(id_label)

        # Retry button
        retry_button = QPushButton("Retry")
        retry_button.clicked.connect(
            lambda: self._retry_widget_creation(widget_id)
        )
        layout.addWidget(retry_button)

        return error_widget

    def can_close_widget(self, widget_id: str, widget: QWidget) -> bool:
        """Prevent closing widgets with unsaved changes"""

        if isinstance(widget, CodeEditor):
            if widget.document().isModified():
                # Prompt user
                reply = QMessageBox.question(
                    widget,
                    "Unsaved Changes",
                    f"Save changes to {widget_id}?",
                    QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
                )

                if reply == QMessageBox.Save:
                    return widget.save()  # True if save succeeded
                elif reply == QMessageBox.Discard:
                    return True  # Allow closing without saving
                else:
                    return False  # Cancel closing

        return True  # Allow closing by default
```

---

## Quick Reference

### Provider Interface Checklist

| Method | Required | Purpose |
|--------|----------|---------|
| `provide_widget()` | ✅ | Create/retrieve widget for ID |
| `widget_closing()` | ✅ | Cleanup before widget removal |
| `save_widget_state()` | ➖ | Persistence support |
| `restore_widget_state()` | ➖ | Persistence support |
| `can_close_widget()` | ➖ | Prevent unwanted closures |
| `get_widget_menu()` | ➖ | Context menu support |

### Widget ID Best Practices

- ✅ Use consistent format across application
- ✅ Include enough info to recreate widget
- ✅ Keep IDs stable across sessions
- ✅ Avoid special characters that break JSON
- ❌ Don't embed complex objects in IDs
- ❌ Don't change ID format between versions

### Provider Pattern Benefits

- **Clean Separation**: Layout logic separate from widget logic
- **Flexible Creation**: Application controls all widget creation
- **Easy Testing**: Mock providers for isolated testing
- **State Control**: Application manages widget persistence
- **Type Safety**: No widget type coupling in MultiSplit

## Related Documents

- **[Core Concepts](../01-overview/core-concepts.md)** - Provider pattern overview
- **[MVC Architecture](mvc-architecture.md)** - How provider fits in MVC
- **[Tree Structure](tree-structure.md)** - Where widget IDs are stored
- **[Usage Guide](../../usage.md)** - Provider implementation examples
- **[Widget Provider Architecture](../../widget-provider-ARCHITECTURE.md)** - Original design document

---

The Widget Provider pattern is the key to MultiSplit's flexibility and reusability - it enables any application to use MultiSplit without coupling to specific widget types or creation patterns.