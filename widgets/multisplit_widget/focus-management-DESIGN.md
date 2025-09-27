# Focus Management Design for MultiSplit Widget

## Problem Statement

The current focus management system in MultiSplit widget fails to properly track focus when users interact with complex widgets inside panes. While clicking on empty space or frames works, clicking on actual widgets (buttons, editors, web views, etc.) doesn't update the pane focus, causing split operations to target the wrong pane.

### Root Causes

1. **Event Consumption**: Complex widgets consume mouse events before they reach our event filter
2. **Single-Level Filtering**: We only install event filters on immediate children, missing nested widgets
3. **Rebuild Loss**: Event filters are lost when the widget tree is rebuilt
4. **Focus Chain Ignorance**: We're not leveraging Qt's built-in focus chain system

## Proposed Solution: Hybrid Focus-Tracking System

### Overview

Implement a three-pronged approach that combines:
1. Qt's FocusIn/FocusOut events (primary mechanism)
2. Recursive event filter installation (fallback for click detection)
3. Dynamic child widget monitoring (for runtime-added widgets)

### Architecture

```
┌─────────────────────────────────────────┐
│           MultiSplit Widget              │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────┐   │
│  │    Focus Tracking System         │   │
│  │                                  │   │
│  │  1. Qt Focus Events (Primary)    │   │
│  │     - FocusIn → Update pane      │   │
│  │     - Handles tab navigation     │   │
│  │                                  │   │
│  │  2. Recursive Filters (Fallback) │   │
│  │     - Install on all descendants │   │
│  │     - Catch remaining clicks     │   │
│  │                                  │   │
│  │  3. Child Monitoring (Dynamic)   │   │
│  │     - Watch for new widgets      │   │
│  │     - Auto-install filters       │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

## Implementation Details

### 1. Qt Focus Event Handling

**File**: `src/vfwidgets_multisplit/view/container.py`

```python
def eventFilter(self, obj, event):
    """Enhanced event filter for comprehensive focus tracking."""
    from PySide6.QtCore import QEvent, Qt

    # PRIMARY: Handle Qt focus events
    if event.type() == QEvent.Type.FocusIn:
        # Widget gained focus - find its pane
        pane_id = self._find_widget_pane(obj)
        if pane_id:
            logger.info(f"FocusIn event: widget in pane {pane_id} gained focus")
            self.pane_focused.emit(pane_id)
            return False

    # FALLBACK: Handle mouse clicks
    elif event.type() == QEvent.Type.MouseButtonPress:
        if event.button() == Qt.MouseButton.LeftButton:
            pane_id_str = obj.property("pane_id")
            if not pane_id_str:
                # Try to find pane by traversing parents
                pane_id_str = self._find_widget_pane(obj)

            if pane_id_str:
                logger.info(f"Mouse click detected in pane: {pane_id_str}")
                self.pane_focused.emit(pane_id_str)

    return False
```

### 2. Recursive Event Filter Installation

```python
def _install_recursive_filters(self, widget: QWidget, pane_id: PaneId, depth: int = 0):
    """Recursively install event filters on widget and all descendants."""
    if depth > 10:  # Prevent infinite recursion
        return

    # Install filter on this widget
    if not widget.property("event_filter_installed"):
        widget.installEventFilter(self)
        widget.setProperty("event_filter_installed", True)
        widget.setProperty("pane_id", str(pane_id))

        logger.debug(f"Installed filter on {widget.__class__.__name__} at depth {depth}")

    # Install on all children
    for child in widget.findChildren(QWidget):
        if child.parent() == widget:  # Direct children only
            self._install_recursive_filters(child, pane_id, depth + 1)
```

### 3. Find Widget's Pane

```python
def _find_widget_pane(self, widget: QWidget) -> Optional[str]:
    """Find which pane a widget belongs to by traversing parents."""
    current = widget
    max_depth = 20

    while current and max_depth > 0:
        # Check if widget has pane_id property
        pane_id = current.property("pane_id")
        if pane_id:
            return pane_id

        # Check if widget is in our tracking dict
        for pid, w in self._widgets.items():
            if w == current:
                return str(pid)

        # Check frame containers
        for pid, frame in self._focus_frames.items():
            if frame == current or frame.isAncestorOf(current):
                return str(pid)

        current = current.parent()
        max_depth -= 1

    return None
```

### 4. Dynamic Child Monitoring

```python
def _monitor_widget_children(self, widget: QWidget, pane_id: PaneId):
    """Monitor widget for dynamically added children."""
    from PySide6.QtCore import QTimer

    def check_new_children():
        # Find children without filters
        for child in widget.findChildren(QWidget):
            if not child.property("event_filter_installed"):
                logger.debug(f"Found new child widget: {child.__class__.__name__}")
                self._install_recursive_filters(child, pane_id, 0)

    # Check periodically for new children (for highly dynamic widgets)
    timer = QTimer()
    timer.timeout.connect(check_new_children)
    timer.start(1000)  # Check every second

    # Store timer to prevent garbage collection
    widget.setProperty("child_monitor_timer", timer)
```

### 5. Special Handling for Complex Widgets

```python
def _handle_complex_widget(self, widget: QWidget, pane_id: PaneId):
    """Special handling for complex widget types."""
    widget_type = widget.__class__.__name__

    if "WebView" in widget_type or "WebEngine" in widget_type:
        # Web views need special handling
        logger.info(f"Installing web view focus handler for pane {pane_id}")
        # Web views often have a focusProxy
        focus_proxy = widget.focusProxy()
        if focus_proxy:
            self._install_recursive_filters(focus_proxy, pane_id)

    elif "Editor" in widget_type or "TextEdit" in widget_type:
        # Text editors may have viewport widgets
        if hasattr(widget, 'viewport'):
            viewport = widget.viewport()
            if viewport:
                self._install_recursive_filters(viewport, pane_id)

    elif "TabWidget" in widget_type:
        # Tab widgets need monitoring for tab changes
        if hasattr(widget, 'currentChanged'):
            widget.currentChanged.connect(
                lambda: self.pane_focused.emit(str(pane_id))
            )
```

## Integration Points

### 1. Container Creation
Modify `_create_pane_container` to use the new comprehensive filter installation:

```python
def _create_pane_container(self, pane_id: PaneId, widget: QWidget) -> QWidget:
    """Create container with comprehensive focus tracking."""
    frame = QFrame()
    # ... existing frame setup ...

    # Install recursive filters
    self._install_recursive_filters(frame, pane_id)
    self._install_recursive_filters(widget, pane_id)

    # Handle complex widgets
    self._handle_complex_widget(widget, pane_id)

    # Monitor for dynamic children
    self._monitor_widget_children(widget, pane_id)

    return frame
```

### 2. Tree Rebuilding
Ensure filters are preserved/reinstalled during rebuilds:

```python
def _build_widget_tree(self, node: PaneNode) -> Optional[QWidget]:
    """Build widget tree with focus tracking preserved."""
    if isinstance(node, LeafNode):
        # ... existing code ...

        # CRITICAL: Always reinstall comprehensive filters
        if frame and widget:
            self._install_recursive_filters(frame, node.pane_id)
            self._install_recursive_filters(widget, node.pane_id)
            self._handle_complex_widget(widget, node.pane_id)
```

## Testing Strategy

### Test Cases

1. **Simple Widgets**: Buttons, labels
2. **Text Editors**: QTextEdit, QPlainTextEdit, custom editors
3. **Web Views**: QWebEngineView with complex DOM
4. **Tab Containers**: QTabWidget with multiple tabs
5. **Nested Containers**: Widgets with deep nesting
6. **Dynamic Content**: Widgets that add children at runtime

### Verification Methods

1. **Focus Logging**: Comprehensive logging of all focus changes
2. **Visual Indicators**: Clear border highlighting for focused panes
3. **Split Verification**: Ensure splits always target the correct pane
4. **Tab Navigation**: Verify tab key moves focus correctly

## Performance Considerations

1. **Filter Overhead**: Recursive filters add overhead - limit depth
2. **Timer Management**: Clean up timers when widgets are destroyed
3. **Memory Leaks**: Ensure proper cleanup of event filters
4. **Lazy Installation**: Install filters only when needed

## Migration Path

1. **Phase 1**: Implement Qt focus event handling
2. **Phase 2**: Add recursive filter installation
3. **Phase 3**: Add dynamic monitoring
4. **Phase 4**: Add complex widget handlers
5. **Phase 5**: Optimize and clean up

## Success Criteria

1. ✓ Clicking any widget updates pane focus
2. ✓ Tab navigation works correctly
3. ✓ Splits target the correct pane
4. ✓ Works with all widget types
5. ✓ No performance degradation
6. ✓ No memory leaks