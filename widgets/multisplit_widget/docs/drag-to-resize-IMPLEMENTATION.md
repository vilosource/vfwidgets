# Drag-to-Resize Implementation Plan for MultisplitWidget

## Architecture Analysis Complete

**Current State:**
- MultisplitWidget v0.2.0 uses "Fixed Container Architecture"
- Panes positioned via `setGeometry()` - no QSplitter hierarchy
- GeometryManager calculates layouts with 6px gaps (HANDLE_WIDTH) between panes
- These gaps currently just show MultisplitWidget's background color
- SetRatiosCommand already exists and works with model's SplitNode ratios
- `splitter_moved` signal connected but never emitted (no dividers exist yet)

**Key Discovery:** Infrastructure is 80% ready! We just need to add interactive divider widgets in the gaps.

## Implementation Plan

### Phase 1: Create Interactive Divider Widget (NEW FILE)
**File:** `widgets/multisplit_widget/src/vfwidgets_multisplit/view/divider_widget.py`

Create `DividerWidget` class:
- Inherits from `QWidget` (or `ThemedWidget` if theme-aware)
- Properties: `orientation`, `split_node_id`, `divider_index`, `style: SplitterStyle`
- Mouse events: `mousePressEvent`, `mouseMoveEvent`, `mouseReleaseEvent`
- Visual states: normal, hover, dragging
- Emits signal: `resize_requested(node_id: str, divider_index: int, delta_pixels: int)`
- Applies SplitterStyle colors and hover effects
- Changes cursor to SizeHorCursor/SizeVerCursor on hover

### Phase 2: Add Divider Management to GeometryManager
**File:** `widgets/multisplit_widget/src/vfwidgets_multisplit/view/geometry_manager.py`

Add new method:
```python
def calculate_dividers(self, tree: PaneNode, viewport: QRect) -> dict[str, list[QRect]]:
    """Calculate divider rectangles for each SplitNode.

    Returns:
        Dict mapping node_id -> list of divider rectangles
        Each SplitNode with N children has N-1 dividers
    """
```

Logic:
- Traverse tree to find all SplitNodes
- For each SplitNode with children, calculate N-1 divider positions
- Dividers occupy the 6px gaps between child panes
- Return dict: `{node_id: [divider_rect1, divider_rect2, ...]}`

### Phase 3: Add Divider Pool to Container
**File:** `widgets/multisplit_widget/src/vfwidgets_multisplit/view/container.py`

Add to PaneContainer:
```python
class PaneContainer:
    def __init__(...):
        self._dividers: dict[str, list[DividerWidget]] = {}  # node_id -> dividers

    def _update_dividers(self, divider_geometries: dict[str, list[QRect]]):
        """Create/update/remove divider widgets to match tree structure."""

    def _on_divider_resize(self, node_id: str, divider_index: int, delta: int):
        """Handle divider drag - calculate new ratios and emit signal."""
```

Connect divider signal to `splitter_moved` emission (which already connects to MultisplitWidget).

### Phase 4: Wire Up Full Rendering Pipeline
**File:** `widgets/multisplit_widget/src/vfwidgets_multisplit/view/container.py`

Modify `_rebuild_layout()`:
```python
def _rebuild_layout(self):
    # Existing pane geometry calculation
    geometries = self._geometry_manager.calculate_layout(self.model.root, viewport)
    self._visual_renderer.render(geometries)

    # NEW: Calculate and render dividers
    divider_geometries = self._geometry_manager.calculate_dividers(self.model.root, viewport)
    self._update_dividers(divider_geometries)
```

### Phase 5: Implement Drag-to-Resize Logic

When divider dragged:
1. DividerWidget tracks mouse delta in pixels
2. On release, emits `resize_requested(node_id, index, delta_pixels)`
3. Container converts pixel delta to new ratios
4. Emits `splitter_moved(node_id, new_ratios)`
5. MultisplitWidget (already wired) calls SetRatiosCommand
6. Model updates, signals structure_changed
7. Layout rebuilds with new ratios

**Ratio Calculation:**
```python
def calculate_new_ratios(split_node: SplitNode, divider_index: int,
                        delta_pixels: int, total_size: int) -> list[float]:
    """Convert pixel delta to new ratio distribution."""
    # Divider between child[i] and child[i+1]
    # Increase child[i] size, decrease child[i+1] size
    # Keep other children unchanged
```

### Phase 6: Visual Feedback
- Hover state: lighter background color from SplitterStyle
- Dragging state: show ghosted/highlighted divider line
- Cursor changes: horizontal ↔ or vertical ↕ resize cursor
- Optional: live preview during drag (update ratios in real-time vs on release)

### Phase 7: Testing
- Test in all three examples (01, 02, 03)
- Test horizontal and vertical splits
- Test with nested splits (tree with multiple levels)
- Test in ViloxTerm with terminal widgets
- Ensure QWebEngineView widgets don't flash during resize

## Files to Create/Modify

**New Files:**
1. `widgets/multisplit_widget/src/vfwidgets_multisplit/view/divider_widget.py` (~150 lines)

**Modified Files:**
1. `widgets/multisplit_widget/src/vfwidgets_multisplit/view/geometry_manager.py` (+80 lines)
2. `widgets/multisplit_widget/src/vfwidgets_multisplit/view/container.py` (+120 lines)
3. `widgets/multisplit_widget/README.md` (update line 50 - feature is now real)

**No Changes Needed:**
- `multisplit.py` - signal wiring already exists
- `commands.py` - SetRatiosCommand already works
- `core/` - model and tree structure perfect as-is

## Estimated Complexity
**Medium** - Most infrastructure exists, we're adding the missing interactive layer.

Total new code: ~350 lines
Time estimate: 2-3 hours implementation + 1 hour testing

## Architecture Notes

### Current Fixed Container Architecture
```
Layer 1: WidgetPool - Fixed container holding all pane widgets
Layer 2: GeometryManager - Pure math: tree → rectangles
Layer 3: VisualRenderer - Applies geometries via setGeometry()
```

### With Drag-to-Resize
```
Layer 1: WidgetPool - Fixed container (panes + dividers)
Layer 2: GeometryManager - Pure math: tree → pane rects + divider rects
Layer 3: VisualRenderer - Applies geometries to panes
Layer 3b: DividerManager - Applies geometries to dividers (NEW)
Layer 4: DividerWidget - Interactive mouse handling (NEW)
```

### Key Insight: Dividers Map to SplitNodes

For a tree structure:
```
SplitNode(HORIZONTAL, ratios=[0.5, 0.5])
  ├─ LeafNode(pane_1)
  └─ LeafNode(pane_2)
```

There is **1 divider** between the two children.

For a nested tree:
```
SplitNode(VERTICAL, ratios=[0.3, 0.7])  ← 1 horizontal divider here
  ├─ LeafNode(pane_1)
  └─ SplitNode(HORIZONTAL, ratios=[0.5, 0.5])  ← 1 vertical divider here
       ├─ LeafNode(pane_2)
       └─ LeafNode(pane_3)
```

Total: **2 dividers** (one per SplitNode)

### Divider Positioning Algorithm

Given `SplitNode` with orientation and N children:
- Calculate child pane rectangles (already done by GeometryManager)
- For each gap between consecutive children:
  - Gap is HANDLE_WIDTH (6px) wide/tall
  - Divider rect fills the gap
  - Store as `dividers[node_id][child_index]`

Example for HORIZONTAL split with 2 children:
```
Pane 1: x=0,   y=0, w=597, h=800
Divider: x=597, y=0, w=6,   h=800  ← Interactive widget here
Pane 2: x=603, y=0, w=597, h=800
```

### Mouse Drag to Ratio Conversion

When user drags divider by `delta_pixels`:
```python
# Example: horizontal divider between panes of total width 1200px
# Current ratios: [0.5, 0.5] = [600px, 600px]
# User drags +100px to the right

# Old widths: [600, 600]
# New widths: [700, 500]
# New ratios: [700/1200, 500/1200] = [0.583, 0.417]

def calculate_new_ratios(old_ratios, divider_index, delta_pixels, total_size):
    # Convert ratios to pixel sizes
    sizes = [ratio * total_size for ratio in old_ratios]

    # Apply delta to adjacent panes
    sizes[divider_index] += delta_pixels
    sizes[divider_index + 1] -= delta_pixels

    # Clamp to minimum sizes (e.g., 50px)
    sizes = [max(50, s) for s in sizes]

    # Convert back to ratios
    new_total = sum(sizes)
    new_ratios = [s / new_total for s in sizes]

    return new_ratios
```

## Theme Integration

DividerWidget should use theme-aware colors:
- Normal state: `editor.background` (darker than widget.background)
- Hover state: `list.hoverBackground` (slight highlight)
- Or use SplitterStyle custom colors if provided

This matches the existing MultisplitWidget background theming (already implemented in multisplit.py:169-190).

## Performance Considerations

1. **Widget Reuse**: Dividers should be reused like panes (divider pool pattern)
2. **Drag Performance**: Consider live updates (update on every mouseMoveEvent) vs deferred (update on mouseReleaseEvent only)
3. **QWebEngineView Compatibility**: Since we use setGeometry() (not reparenting), resize should be smooth

## Future Enhancements (Out of Scope)

- Double-click divider to reset to equal ratios
- Keyboard shortcuts to adjust ratios (Ctrl+Shift+Arrow keys)
- Visual snap guides when divider approaches certain positions
- Animated transitions when ratios change programmatically
