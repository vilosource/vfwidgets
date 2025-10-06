# MultisplitWidget Architecture

Internal architecture documentation for developers contributing to or extending MultisplitWidget.

## Table of Contents

- [Overview](#overview)
- [Fixed Container Architecture](#fixed-container-architecture)
- [Component Layers](#component-layers)
- [Drag-to-Resize Implementation](#drag-to-resize-implementation)
- [Focus Management](#focus-management)
- [Extension Points](#extension-points)

---

## Overview

MultisplitWidget is a dynamic split-pane widget built on a **Fixed Container Architecture** that achieves high performance by eliminating widget reparenting and using pure geometry calculations.

**Core Philosophy:**
- **No widget tree manipulation** - widgets stay in fixed container
- **Geometry-based layout** - pure math converts tree → rectangles
- **Separation of concerns** - model/view/controller pattern
- **Command pattern** - all mutations through undo/redo commands

**Key Metrics:**
- **Zero reparenting** - widgets created once, positioned via `setGeometry()`
- **60 FPS** - real-time drag-to-resize with timer-based polling
- **Minimal dividers** - 6px gaps (configurable 1-10px)

---

## Fixed Container Architecture

The Fixed Container Architecture (v0.2.0) eliminates Qt widget tree manipulation for improved performance and stability.

### Three-Layer Design

```
┌─────────────────────────────────────────────┐
│  Layer 3: VisualRenderer                    │
│  - Applies geometries via setGeometry()     │
│  - NO reparenting, NO tree building         │
│  - Focus border overlay                     │
└─────────────────────────────────────────────┘
                    ↑
                    │ QRect geometries
                    │
┌─────────────────────────────────────────────┐
│  Layer 2: GeometryManager                   │
│  - Pure math: tree → rectangles             │
│  - Recursive geometry calculation           │
│  - Divider position calculation             │
│  - NO Qt dependencies                       │
└─────────────────────────────────────────────┘
                    ↑
                    │ PaneNode tree
                    │
┌─────────────────────────────────────────────┐
│  Layer 1: WidgetPool                        │
│  - Fixed QWidget container                  │
│  - All pane widgets are children            │
│  - Visibility tracking (visible/hidden)     │
│  - NEVER reparents widgets                  │
└─────────────────────────────────────────────┘
```

### Layer 1: WidgetPool

**Purpose:** Fixed container that owns all pane widgets.

**Key Responsibilities:**
- Create widgets via WidgetProvider
- Store widgets in single parent container
- Track visibility state
- Provide widget lookup by pane ID

**Critical Invariant:**
```python
# Widgets NEVER change parent - always children of pool container
assert widget.parent() == self._container  # Always true
```

**Files:**
- `src/vfwidgets_multisplit/view/widget_pool.py`

### Layer 2: GeometryManager

**Purpose:** Pure mathematical conversion from tree structure to widget geometries.

**Algorithm:**
```
Input:  PaneNode tree + QRect viewport
Output: dict[pane_id -> QRect geometry]

Recursion:
1. Base case (LeafNode): Return viewport rectangle
2. Recursive case (SplitNode):
   a. Split viewport by orientation and ratios
   b. Subtract HANDLE_WIDTH (6px) from all but last child
   c. Recurse to children with their sub-rectangles
   d. Collect all leaf geometries
```

**Divider Calculation:**
```
Input:  PaneNode tree + QRect viewport
Output: dict[node_id -> list[QRect divider_rects]]

For each SplitNode with N children:
  - Generate N-1 divider rectangles
  - Position dividers in 6px gaps between children
  - Orientation determines divider axis:
    * HORIZONTAL split → vertical divider lines
    * VERTICAL split → horizontal divider lines
```

**Files:**
- `src/vfwidgets_multisplit/view/geometry_manager.py`

**Key Constants:**
```python
HANDLE_WIDTH = 6  # Gap between panes for divider
```

### Layer 3: VisualRenderer

**Purpose:** Apply calculated geometries to actual widgets.

**Key Operations:**
```python
def render(geometries: dict[str, QRect]):
    # 1. Hide panes not in layout
    for pane_id in all_panes - visible_panes:
        widget.setVisible(False)

    # 2. Position and show visible panes
    for pane_id, geometry in geometries.items():
        was_hidden = not widget.isVisible()

        widget.setGeometry(geometry)  # ONLY geometry change
        widget.setVisible(True)
        widget.raise_()               # Z-order

        # Smart repaint strategy for QWebEngineView compatibility
        if was_hidden:
            widget.repaint()  # Immediate paint for newly visible widgets
        else:
            widget.update()   # Async paint for resized widgets (GPU compositor safe)
```

**Critical:**
- Uses `repaint()` for newly visible widgets (immediate display)
- Uses `update()` for already-visible widgets being resized (prevents QWebEngineView GPU flash)
- Never calls `setParent()` - geometry changes only
- Focus border is separate overlay widget

**Files:**
- `src/vfwidgets_multisplit/view/visual_renderer.py`

---

## Component Layers

### Model Layer

**Files:**
- `src/vfwidgets_multisplit/core/model.py` - PaneModel (tree + state)
- `src/vfwidgets_multisplit/core/nodes.py` - LeafNode, SplitNode
- `src/vfwidgets_multisplit/core/types.py` - Types and enums

**Tree Structure:**
```python
PaneNode (ABC)
├── LeafNode(pane_id, widget_id)
└── SplitNode(orientation, ratios, children: list[PaneNode])
```

**Signals:**
- `structure_changed` - Tree modified (split/remove)
- `pane_added(pane_id)` - New pane created
- `pane_removed(pane_id)` - Pane deleted
- `focus_changed(old, new)` - Focus transition

### Controller Layer

**Files:**
- `src/vfwidgets_multisplit/controller/controller.py` - PaneController
- `src/vfwidgets_multisplit/controller/commands.py` - Command implementations

**Command Pattern:**
```python
class Command(ABC):
    def execute(model: PaneModel) -> bool
    def undo(model: PaneModel) -> bool
    def redo(model: PaneModel) -> bool

Commands:
- SplitPaneCommand(pane_id, widget_id, position, ratio)
- RemovePaneCommand(pane_id)
- SetRatiosCommand(node_id, ratios)  # For drag-to-resize
```

**Undo/Redo:**
- All model mutations via commands
- Command history stack (undo/redo)
- Validation before execution

### View Layer

**Files:**
- `src/vfwidgets_multisplit/view/container.py` - PaneContainer (main view)
- `src/vfwidgets_multisplit/view/widget_pool.py` - WidgetPool
- `src/vfwidgets_multisplit/view/geometry_manager.py` - GeometryManager
- `src/vfwidgets_multisplit/view/visual_renderer.py` - VisualRenderer
- `src/vfwidgets_multisplit/view/divider_widget.py` - DividerWidget

---

## Drag-to-Resize Implementation

### Two-Phase Architecture

Drag-to-resize uses a two-phase approach to enable live preview without model pollution:

**Phase 1: Live Preview (During Drag)**
```python
def _on_divider_resize(node_id, divider_index, delta_pixels):
    # 1. Get SplitNode from tree
    split_node = find_split_by_id(model.root, node_id)

    # 2. Calculate new ratios from pixel delta
    new_ratios = calculate_new_ratios(split_node.ratios, delta_pixels)

    # 3. TEMPORARILY modify node (preview only)
    old_ratios = split_node.ratios
    split_node.ratios = new_ratios

    # 4. Recalculate geometries with preview ratios
    geometries = geometry_manager.calculate_layout(model.root, viewport)

    # 5. Restore original ratios (NO MODEL CHANGE)
    split_node.ratios = old_ratios

    # 6. Render preview geometries directly
    visual_renderer.render(geometries)
```

**Phase 2: Final Commit (On Mouse Release)**
```python
def _on_divider_commit(node_id, divider_index, delta_pixels):
    # Calculate final ratios
    new_ratios = calculate_new_ratios(...)

    # Update model via command (undo/redo support)
    command = SetRatiosCommand(model, node_id, new_ratios)
    controller.execute_command(command)
```

### DividerWidget

**Mouse Tracking:**
- Uses **timer-based polling** at 60 FPS (16ms intervals)
- Tracks global cursor position via `QCursor.pos()`
- Bypasses Qt mouse event system (more reliable cross-platform)

**Signals:**
```python
class DividerWidget(QWidget):
    # Live preview during drag (emits every frame)
    resize_requested = Signal(str, int, int)  # node_id, divider_index, delta_pixels

    # Final commit when drag completes
    resize_committed = Signal(str, int, int)  # node_id, divider_index, delta_pixels
```

**Event Flow:**
```
1. mousePressEvent
   └─> Start QTimer (16ms interval)

2. Timer callback (_update_drag_position)
   └─> QCursor.pos() - get global mouse position
   └─> Calculate delta from drag start
   └─> emit resize_requested(node_id, divider_index, delta)

3. mouseReleaseEvent
   └─> Stop timer
   └─> emit resize_committed(node_id, divider_index, final_delta)
```

**Why Timer Polling?**
- `grabMouse()` doesn't work on Linux for non-popup windows
- Mouse events can be lost when cursor moves fast
- Timer polling is reliable and smooth (60 FPS)

**Files:**
- `src/vfwidgets_multisplit/view/divider_widget.py`

---

## Focus Management

### Focus Flow

```
User clicks pane widget
    ↓
eventFilter intercepts MouseButtonPress
    ↓
Find pane_id from clicked widget
    ↓
Find focusable child widget (not container)
    ↓
Call setFocus() with MouseFocusReason
    ↓
Emit pane_focused signal
    ↓
model.set_focused_pane(pane_id)
    ↓
Emit focus_changed(old, new)
```

### Critical: Focus Child Widgets

**Problem:** Pane containers are often `QWidget` wrappers around actual focusable widgets.

**Solution:** `_find_focusable_widget()` helper:
```python
def _find_focusable_widget(widget: QWidget) -> Optional[QWidget]:
    """Find first focusable child in pane."""
    if widget.focusPolicy() not in (NoFocus, TabFocus):
        return widget

    for child in widget.findChildren(QWidget):
        if child.focusPolicy() not in (NoFocus, TabFocus):
            return child

    return None
```

**Example:**
```
QWidget (container, NoFocus)
  └─ DocumentEditor (focusable)  ← This gets setFocus()
```

### Divider Focus Policy

**Critical:** Dividers must NOT steal focus from panes:
```python
# In DividerWidget.__init__
self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
```

**Files:**
- `src/vfwidgets_multisplit/view/container.py` - Event filter
- `src/vfwidgets_multisplit/core/focus.py` - FocusManager

---

## Extension Points

### Custom Divider Styling

**Override DividerWidget styling:**
```python
class CustomDividerWidget(DividerWidget):
    def _update_style(self):
        # Custom styling logic
        self.setStyleSheet(...)
```

**Register custom divider class:**
```python
# In Container.__init__
self.divider_class = CustomDividerWidget
```

### Custom Geometry Calculation

**Extend GeometryManager:**
```python
class CustomGeometryManager(GeometryManager):
    HANDLE_WIDTH = 10  # Wider dividers

    def _split_horizontal(self, rect, ratios):
        # Custom split logic
        ...
```

### Custom Focus Logic

**Extend FocusManager:**
```python
class CustomFocusManager(FocusManager):
    def find_adjacent_pane(self, pane_id, direction):
        # Custom navigation logic
        ...
```

### Custom Commands

**Add new commands:**
```python
class SwapPanesCommand(Command):
    def execute(self, model: PaneModel) -> bool:
        # Swap two panes
        ...
```

---

## Performance Notes

### Geometry Calculation

- **O(n)** where n = number of panes
- Single tree traversal
- No widget operations during calculation

### Rendering

- **O(visible_panes)** to apply geometries
- Smart repaint strategy:
  - `repaint()` for newly visible widgets (synchronous, immediate display)
  - `update()` for already-visible widgets being resized (asynchronous, prevents QWebEngineView GPU flash)
- `raise_()` ensures correct z-order

### Drag Performance

- **60 FPS** timer polling
- Lightweight ratio calculation
- Direct geometry application (no model updates)

---

## Testing Strategy

### Unit Tests

- `tests/core/` - Model and tree operations
- `tests/controller/` - Command execution
- `tests/view/` - Geometry calculations

### Integration Tests

- `tests/integration/` - Full widget lifecycle
- Focus management
- Drag-to-resize flows

### Performance Tests

- Large tree layouts (100+ panes)
- Rapid split/remove operations
- Drag performance under load

---

## Migration Notes

### From v0.1.x to v0.2.0

**Major Change:** Switched from QSplitter hierarchy to Fixed Container Architecture

**Breaking Changes:**
- None (API unchanged)

**Internal Changes:**
- Removed QSplitter usage
- Added WidgetPool, GeometryManager, VisualRenderer
- Implemented drag-to-resize
- Added SplitterStyle configuration

---

## Implementation Guidelines

### Adding New Features

1. **Model Change?**
   - Add to `PaneModel` class
   - Create Command subclass
   - Update serialization (session management)

2. **Visual Change?**
   - Modify GeometryManager calculation
   - Update VisualRenderer rendering
   - Add SplitterStyle configuration if needed

3. **Interaction Change?**
   - Extend event filter in Container
   - Add signal/slot connections
   - Update FocusManager if focus-related

### Code Style

- Use **type hints** everywhere
- **Docstrings** for all public methods
- **Comments** for complex algorithms
- **Assertions** for invariants

### Documentation

- Update API.md for public API changes
- Update ARCHITECTURE.md for internal changes
- Add examples for new features
- Update migration guide for breaking changes

---

## References

- [drag-to-resize-IMPLEMENTATION.md](drag-to-resize-IMPLEMENTATION.md) - Drag implementation details
- [API.md](API.md) - Public API reference
- [GUIDE.md](GUIDE.md) - Developer usage guide
- [Fixed Container Architecture Summary](archived/fixed-container-architecture-SUMMARY.md)
