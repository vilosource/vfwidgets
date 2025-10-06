# Pane Navigation Testing Plan

**Status**: Investigation Phase
**Created**: 2025-10-06
**Issue**: Spatial navigation not implemented - uses simple tab order

---

## Current Problem

The MultisplitWidget's `navigate_focus(direction)` method currently has a TODO comment indicating spatial navigation is not implemented:

**File**: `widgets/multisplit_widget/src/vfwidgets_multisplit/core/focus.py:111`

```python
def navigate(self, direction: Direction) -> Optional[PaneId]:
    """Navigate focus in a direction."""
    current = self.model.focused_pane_id
    if not current:
        return self.get_next_pane()

    # For now, use simple tab order for left/right
    # TODO: Implement spatial navigation
    if direction in (Direction.LEFT, Direction.UP):
        return self.get_previous_pane(current)
    else:
        return self.get_next_pane(current)
```

**Current Behavior**:
- LEFT/UP: cycles to previous pane in tab order
- RIGHT/DOWN: cycles to next pane in tab order

**Expected Behavior**:
- LEFT: moves focus to the pane directly to the left (based on geometry)
- RIGHT: moves focus to the pane directly to the right
- UP: moves focus to the pane directly above
- DOWN: moves focus to the pane directly below

---

## Test Scenarios

### Scenario 1: Grid Layout (2x2)

```
┌─────────┬─────────┐
│ Pane A  │ Pane B  │
│  (TL)   │  (TR)   │
├─────────┼─────────┤
│ Pane C  │ Pane D  │
│  (BL)   │  (BR)   │
└─────────┴─────────┘
```

**Expected Navigation**:
- From A: RIGHT→B, DOWN→C, LEFT→none, UP→none
- From B: LEFT→A, DOWN→D, RIGHT→none, UP→none
- From C: RIGHT→D, UP→A, LEFT→none, DOWN→none
- From D: LEFT→C, UP→B, RIGHT→none, DOWN→none

**Purpose**: Tests basic 4-directional navigation in a simple grid.

---

### Scenario 2: Complex Nested Layout

```
┌─────────┬─────────┐
│         │ Pane B  │
│ Pane A  │   (TR)  │
│  (L)    ├─────────┤
│         │ Pane C  │
│         │   (BR)  │
└─────────┴─────────┘
```

**Expected Navigation**:
- From A: RIGHT→B or C (needs intelligent selection based on center/proximity)
- From B: LEFT→A, DOWN→C
- From C: LEFT→A, UP→B

**Purpose**: Tests navigation when multiple panes exist in a direction - should choose based on spatial proximity/alignment.

---

### Scenario 3: Horizontal Strips

```
┌──────────────────┐
│     Pane A       │
│     (Top)        │
├──────────────────┤
│     Pane B       │
│    (Middle)      │
├──────────────────┤
│     Pane C       │
│    (Bottom)      │
└──────────────────┘
```

**Expected Navigation**:
- From A: DOWN→B, LEFT→none, RIGHT→none, UP→none
- From B: UP→A, DOWN→C, LEFT→none, RIGHT→none
- From C: UP→B, DOWN→none, LEFT→none, RIGHT→none

**Purpose**: Tests vertical-only navigation, ensures horizontal navigation doesn't incorrectly wrap.

---

## Spatial Navigation Algorithm Requirements

### 1. Geometry-Based Selection

For each direction, the algorithm should:

1. **Get candidate panes**: Find all panes in the target direction
2. **Filter by alignment**:
   - For LEFT/RIGHT: Filter panes that vertically overlap with current pane
   - For UP/DOWN: Filter panes that horizontally overlap with current pane
3. **Choose closest**: Select the pane with the closest edge distance
4. **Fallback**: If no aligned panes, choose the closest pane by center-to-center distance

### 2. Edge Cases

- **No panes in direction**: Return None (no navigation)
- **Multiple equally valid panes**: Choose based on:
  - Alignment with current pane center
  - Shortest edge-to-edge distance
- **Wrapping behavior**: Should NOT wrap (unlike tab order)

### 3. Data Needed for Algorithm

Each pane needs its bounding rectangle:
- `x, y, width, height` in container coordinates
- Can be obtained from `visual_renderer.get_pane_geometry(pane_id)`

---

## Testing Strategy

### Phase 1: Create Visual Test Example

Create `examples/05_navigation_testing.py` with:
- Pre-configured tab scenarios (Grid, Nested, Strips)
- Visual focus indicators (colored borders)
- Navigation test buttons
- Log panel showing expected vs actual navigation
- Keyboard shortcuts (Ctrl+Shift+Arrow keys)

### Phase 2: Document Failures

Run the test example and document:
- Which navigation directions work correctly
- Which fail and how (wrong pane selected, wraps incorrectly, etc.)
- Edge cases that break

### Phase 3: Implement Spatial Algorithm

Based on test results:
1. Implement geometry-based navigation in `focus.py`
2. Add helper methods for:
   - Getting pane geometries
   - Calculating overlap
   - Finding closest pane
3. Add unit tests for algorithm

### Phase 4: Validate with Tests

Re-run `05_navigation_testing.py` and verify:
- All scenarios pass expected behavior
- No regressions in existing functionality
- Performance is acceptable (< 10ms per navigation)

---

## Implementation Notes

### Geometry Source

Pane geometries can be obtained from `VisualRenderer`:

```python
# In FocusManager, need access to visual_renderer
geometry = visual_renderer.get_pane_geometry(pane_id)
# Returns QRect with x, y, width, height
```

**Challenge**: `FocusManager` currently doesn't have access to `VisualRenderer`. Need to either:
1. Pass geometry data through the model
2. Add visual_renderer reference to FocusManager
3. Move navigation logic to controller layer (has access to both)

### Preferred Approach

Move spatial navigation to **Controller layer**:
- Controller has access to both Model and View
- Can query geometries from VisualRenderer
- Can calculate spatial relationships
- Updates focus via Model

---

## Success Criteria

✅ All 3 test scenarios pass with correct spatial navigation
✅ No wrapping when no pane exists in direction
✅ Intelligent selection when multiple candidates exist
✅ Performance < 10ms per navigation call
✅ Works correctly with dynamic layout changes
✅ Unit tests cover edge cases

---

## References

- `src/vfwidgets_multisplit/core/focus.py` - Current navigation implementation
- `src/vfwidgets_multisplit/view/visual_renderer.py` - Geometry calculations
- `src/vfwidgets_multisplit/controller/controller.py` - May need refactoring
- `examples/03_keyboard_driven_splitting.py` - Existing navigation example (uses simplified version)
