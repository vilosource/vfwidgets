# Pane Navigation Testing Plan

**Status**: Documented - Wrong Behavior Confirmed
**Created**: 2025-10-06
**Updated**: 2025-10-06
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

## Observed Wrong Behavior (2025-10-06)

Using `examples/05_navigation_testing.py` with Grid Layout (2x2):

### Tree Structure and Tab Order

The grid layout is created with these operations:
```python
initialize_empty("pane_a")              # Creates A
split_pane(A, "pane_b", RIGHT, 0.5)    # Creates B on right of A
split_pane(A, "pane_c", BOTTOM, 0.5)   # Creates C below A
split_pane(B, "pane_d", BOTTOM, 0.5)   # Creates D below B
```

This creates a tree structure:
```
         Root (Horizontal: A|B)
        /                      \
   Split (Vert: A/C)        Split (Vert: B/D)
    /        \               /           \
   A          C             B             D
```

**Resulting Tab Order (depth-first traversal)**: A → C → B → D

### Actual Navigation Failures

**Test Case: Starting at Pane D (bottom-right)**

1. **D → UP**
   - Expected: Pane B (directly above D)
   - Actual: Pane B ✓ (WORKS - by accident! Previous in tab order: D→B)

2. **B → LEFT** (now at Pane B, top-right)
   - Expected: Pane A (directly left of B)
   - **Actual: Pane C** ❌ WRONG
   - Reason: Tab order previous is B→C, not spatial left

**Root Cause**: Navigation uses `get_previous_pane()` and `get_next_pane()` which traverse the tree in tab order (A→C→B→D), completely ignoring spatial positioning.

### Complete Tab Order Navigation Matrix

Grid Layout (2x2):
```
┌─────────┬─────────┐
│ Pane A  │ Pane B  │  Tab order: A(1) → C(2) → B(3) → D(4)
├─────────┼─────────┤
│ Pane C  │ Pane D  │
└─────────┴─────────┘
```

**Current (Tab Order) Behavior**:
- A → LEFT/UP: wraps to D (last pane)
- A → RIGHT/DOWN: C (next in tab order) ❌ Should be B or C based on direction
- C → LEFT/UP: A (previous) ❌ Should be none (left) or A (up)
- C → RIGHT/DOWN: B ❌ Should be D (right) or none (down)
- B → LEFT/UP: C ❌ Should be A (left) or none (up)
- B → RIGHT/DOWN: D ✓ (accidentally correct)
- D → LEFT/UP: B ✓ (accidentally correct for UP, wrong for LEFT)
- D → RIGHT/DOWN: wraps to A ❌ Should be none for both

**Summary**: Only 2 out of ~16 possible navigation operations work correctly, and those are accidental due to tab order alignment with spatial layout.

### Complex Nested Layout Behavior

Using `examples/05_navigation_testing.py` with Complex Nested layout:

**Tree Structure**:
```python
initialize_empty("pane_a")              # Creates A (left side)
split_pane(A, "pane_b", RIGHT, 0.5)    # Creates B on right of A
split_pane(B, "pane_c", BOTTOM, 0.5)   # Creates C below B
```

Tree:
```
         Root (Horizontal: A | B/C)
        /                          \
       A                        Split (Vert: B/C)
                                 /          \
                                B            C
```

**Resulting Tab Order**: A → B → C

**Observed Navigation (from Pane C)**:

Layout visualization:
```
┌─────────┬─────────┐
│         │ Pane B  │
│ Pane A  │   (TR)  │
│  (L)    ├─────────┤
│         │ Pane C  │
│         │   (BR)  │
└─────────┴─────────┘
```

1. **C → UP** (from bottom-right)
   - Expected: Pane B (directly above C)
   - Actual: Pane B ✓ (WORKS - previous in tab order C→B)

2. **B → LEFT** (from top-right)
   - Expected: Pane A (to the left of B)
   - Actual: Pane A ✓ (WORKS - previous in tab order B→A)

3. **B → UP** (from top-right)
   - Expected: none (B is at the top)
   - **Actual: Pane A** ❌ WRONG
   - Reason: Tab order wraps or navigates to previous (B→A)

**Tab Order Analysis for Nested**:
- Tab order: A → B → C (linear, matches spatial left-to-right then top-to-bottom)
- Some navigation works correctly by accident because tab order partially aligns with spatial layout
- UP/DOWN navigation within right column works (B↔C)
- LEFT navigation from right column works (B→A, C→A via B)
- But UP from B incorrectly goes to A instead of none
- DOWN from C would incorrectly wrap or go nowhere

**Key Issue**: Even when tab order accidentally produces correct results for some directions, it fails for boundary cases (navigating UP when already at top, DOWN when at bottom, etc.).

### Horizontal Strips Layout Behavior

Using `examples/05_navigation_testing.py` with Horizontal Strips layout:

**Tree Structure**:
```python
initialize_empty("pane_a")              # Creates A (top)
split_pane(A, "pane_b", BOTTOM, 0.33)  # Creates B below A
split_pane(B, "pane_c", BOTTOM, 0.5)   # Creates C below B
```

Tree:
```
    Root (Vert: A/B/C)
     /      |       \
    A       B        C
```

**Resulting Tab Order**: A → B → C

**Layout visualization**:
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

**Observed Navigation**: ✅ **ALL TESTS PASS**

- A → DOWN → B ✓ (next in tab order)
- A → UP → none ✓ (no previous, already at start)
- A → LEFT/RIGHT → none ✓ (wraps but should be none - accidental pass or actual boundary?)
- B → UP → A ✓ (previous in tab order)
- B → DOWN → C ✓ (next in tab order)
- B → LEFT/RIGHT → none ✓
- C → UP → B ✓ (previous in tab order)
- C → DOWN → none ✓ (no next, already at end)
- C → LEFT/RIGHT → none ✓

**Why It Works**:
- Tab order A→B→C perfectly matches the vertical spatial arrangement top-to-bottom
- UP direction = previous pane in tab order
- DOWN direction = next pane in tab order
- LEFT/RIGHT have no valid targets (single column), and tab order doesn't provide any either
- Boundaries work correctly because start/end of tab order align with top/bottom of layout

**Important**: This is the ONLY scenario where tab-order navigation accidentally produces completely correct results because:
1. Linear vertical arrangement matches linear tab order
2. Only UP/DOWN navigation is valid (LEFT/RIGHT should always be none)
3. Tab order direction (forward/backward) maps perfectly to spatial direction (down/up)

This demonstrates that tab-order navigation can work correctly, but **only in the special case of single-column/row layouts**. Any 2D grid immediately breaks this alignment.

### Inverted T Layout Behavior

Using `examples/05_navigation_testing.py` with Inverted T layout:

**Tree Structure**:
```python
initialize_empty("pane_c")              # Creates C (bottom, full width)
split_pane(C, "pane_a", TOP, 0.5)      # Creates A on top of C
split_pane(A, "pane_b", RIGHT, 0.5)    # Creates B on right of A
```

Tree:
```
         Root (Vertical: Top/C)
        /                     \
   Split (Horiz: A|B)          C
    /          \
   A            B
```

**Resulting Tab Order**: A → B → C

**Layout visualization**:
```
┌─────────┬─────────┐
│ Pane A  │ Pane B  │
│  (TL)   │  (TR)   │
├─────────┴─────────┤
│     Pane C        │
│  (Bottom Full)    │
└───────────────────┘
```

**Observed Navigation** (2025-10-06):

**From Pane A (Top-Left)**:
1. **A → LEFT**
   - Expected: none (A is at left edge)
   - **Actual: Pane B** ❌ WRONG
   - Reason: Tab order wraps or navigates forward (A→B)

2. **A → DOWN**
   - Expected: Pane C (directly below A)
   - **Actual: Pane B** ❌ WRONG
   - Reason: Tab order next (A→B), ignores spatial positioning

**From Pane B (Top-Right)**:
3. **B → DOWN**
   - Expected: Pane C (directly below B)
   - Actual: Pane C ✓ (WORKS - next in tab order B→C)

**From Pane C (Bottom Full Width)**:
4. **C → UP**
   - Expected: Pane A or B (should intelligently choose based on C's center or last focused)
   - Actual: Pane B ✓ (WORKS - previous in tab order C→B, but wrong reasoning)

**Tab Order Analysis for Inverted T**:
- Tab order: A → B → C
- Tree structure creates left-to-right then top-to-bottom traversal
- Only 2 out of 4+ tested operations work, and both are accidental
- Critical failures:
  - A → DOWN goes to B instead of C (navigates in tab order, not spatial down)
  - A → LEFT goes to B instead of none (wraps/navigates in tab order)
- The algorithm completely ignores that:
  - A and B are on the same row (neither should navigate horizontally between them in opposite direction)
  - C spans the full width below both A and B
  - DOWN from A should look at vertical spatial relationships, not sibling order in tree

**Root Cause**: The tree structure `(A|B)/C` creates tab order A→B→C, but:
- A's RIGHT sibling in the tree is B (correct spatially)
- A's DOWN relationship should be to C (parent's sibling), but algorithm uses A→B (next in depth-first traversal)
- LEFT from A should be none (at edge), but algorithm wraps or uses previous/next

This scenario perfectly demonstrates why **spatial navigation requires geometry**, not tree traversal.

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

### Phase 1: Create Visual Test Example ✅ COMPLETED

Created `examples/05_navigation_testing.py` with:
- ✅ Pre-configured scenarios (Grid, Nested, Strips)
- ✅ Visual focus indicators (blue borders when focused)
- ✅ Navigation test buttons for each direction
- ✅ Log panel showing expected vs actual navigation with PASS/FAIL
- ✅ Keyboard shortcuts (Ctrl+Shift+Arrow keys)
- ✅ Single MultisplitWidget pattern (following Example 01)
- ✅ Dynamic scenario switching

**Implementation Details**:
- Uses single MultisplitWidget instance to avoid lifecycle issues
- Clears and rebuilds layout when switching scenarios
- Provider tracks pane labels for test validation
- Real-time logging of navigation attempts

### Phase 2: Document Failures ✅ COMPLETED

Documented actual wrong behavior:
- ✅ Tab order navigation confirmed (A→C→B→D for Grid layout)
- ✅ Specific failure case documented (B → LEFT goes to C instead of A)
- ✅ Complete navigation matrix analyzed
- ✅ Root cause identified: uses tree traversal instead of geometry

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
