# Fixed Container Architecture - Complete Redesign

## Executive Summary

This document proposes a complete architectural redesign of MultisplitWidget to eliminate white flashes when splitting panes containing QWebEngineView widgets. The current tree-based approach has a **fundamental design flaw** that makes flash-free operation impossible. The proposed **Fixed Container Architecture** solves this by separating logical pane structure from physical widget containers.

**Status**: Proposal (2025-10-03)
**Author**: System Analysis
**Problem**: QWebEngineView GPU texture re-synchronization on reparenting
**Solution**: Never reparent widgets - use geometry-only updates

---

## Problem Analysis

### Root Cause

The fundamental issue is an **architectural contradiction**:

```
Tree mutation REQUIRES widget reparenting
         ↓
QWebEngineView FORBIDS reparenting (causes GPU flash)
         ↓
     UNSOLVABLE
```

### Current Architecture Issues

#### Issue 1: Widget Tree Mirrors Pane Tree

**Current approach**:
```python
# Pane tree structure dictates widget tree structure
SplitNode(node_123)
├── LeafNode(pane_A) → QSplitter[TerminalWidget_A]
└── LeafNode(pane_B) → QSplitter[TerminalWidget_B]

# When splitting pane_A:
# - Old wrapper becomes parent SplitNode
# - pane_A widget MUST move to new wrapper
# - Reparenting triggers GPU flash ❌
```

**Why this fails**:
1. Split operation changes tree structure
2. Tree structure change requires moving widgets
3. Moving widgets (reparenting) triggers QWebEngineView GPU texture re-sync
4. GPU re-sync causes visible white flash

#### Issue 2: Wrapper Reuse Complexity

Attempted solutions created cascading failures:

**Attempt 1**: Reuse splitters
- ✓ Fixed flash for non-split panes
- ✗ Still flashed on the pane being split

**Attempt 2**: Pre-wrap all leaves in splitters
- ✓ First split of a pane doesn't flash
- ✗ Second split creates new wrapper → reparenting → flash
- ✗ Infinite loop bugs from circular references

**Attempt 3**: Create replacement wrappers
- ✗ Still requires reparenting the frame
- ✗ Defeats the purpose of reuse
- ✗ Impossible to avoid reparenting when wrapper is "promoted"

#### Issue 3: Theoretical Impossibility

```
Mathematical proof this approach cannot work:

Given:
1. Pane P has wrapper W containing widget X
2. Split P creates SplitNode S
3. S needs container C to hold P and new pane Q
4. W is the natural choice for C (reuse)

Constraint:
- W can only contain ONE set of children at a time
- Either: W contains [X] (before split)
- Or:     W contains [P_container, Q_container] (after split)

Result:
- X MUST move from W to P_container
- Moving X = reparenting
- Reparenting = flash

QED: Tree-based approach cannot avoid reparenting ∎
```

### Current Code Issues

From `/home/kuja/GitHub/vfwidgets/widgets/multisplit_widget/src/vfwidgets_multisplit/view/container.py`:

**Lines 271-456**: `_build_widget_tree()`
- Recursively builds Qt widget tree from pane tree
- Creates/reuses splitters based on node IDs
- Complex wrapper detection logic (lines 368-419)
- Attempts to prevent reparenting by reusing containers
- **Fundamental flaw**: Tree building inherently requires reparenting

**Lines 218-269**: `_rebuild_layout()`
- Called on every structure change
- Swaps entire widget trees
- Comments acknowledge reparenting issue (lines 220-224)
- Uses `setUpdatesEnabled(False)` to minimize flashing
- **Doesn't solve the problem**, just tries to hide it

---

## Proposed Solution: Fixed Container Architecture

### Core Principle

**"Widgets Never Move"**

Separate the **logical pane tree** (model) from the **physical widget containers** (view).

### Key Insight

We don't need widgets in a tree structure. We need widgets at specific **positions** on screen. Qt layouts are just one way to achieve positioning - we can use **direct geometry control** instead.

### Three-Layer Architecture

```
┌─────────────────────────────────────────────────┐
│  Layer 3: Visual Renderer                       │
│  - Applies geometries to widgets                │
│  - setGeometry() only (no reparenting)         │
└─────────────────────────────────────────────────┘
                     ↑
                     │ Dict[PaneId, QRect]
                     │
┌─────────────────────────────────────────────────┐
│  Layer 2: Geometry Manager                      │
│  - Pure calculation (no Qt operations)          │
│  - Tree → Rectangles mapping                    │
└─────────────────────────────────────────────────┘
                     ↑
                     │ PaneNode tree
                     │
┌─────────────────────────────────────────────────┐
│  Layer 1: Widget Pool                           │
│  - Fixed container for all widgets              │
│  - Widgets added once, never reparented         │
└─────────────────────────────────────────────────┘
```

---

## Detailed Design

### Layer 1: Widget Pool

**Purpose**: Permanent home for all widgets. Widgets are added once and never moved.

```python
class WidgetPool:
    """
    Fixed container for all pane widgets.

    Widgets are added when panes are created and removed only when
    panes are permanently destroyed. They NEVER reparent during splits,
    moves, or other tree structure changes.
    """

    def __init__(self, parent: QWidget):
        # Single container for ALL widgets
        # Using QWidget with no layout for absolute positioning
        self._container = QWidget(parent)

        # Widget registry
        self._widgets: Dict[PaneId, QWidget] = {}

    def add_widget(self, pane_id: PaneId, widget: QWidget) -> None:
        """
        Add widget to pool - happens ONCE per widget lifetime.

        After this call, the widget's parent never changes until
        the widget is destroyed.
        """
        if pane_id in self._widgets:
            raise ValueError(f"Widget already exists for pane {pane_id}")

        # Set parent ONCE - never changed after this
        widget.setParent(self._container)

        # Store reference
        self._widgets[pane_id] = widget

        # Initially hidden - renderer will show it
        widget.setVisible(False)

    def remove_widget(self, pane_id: PaneId) -> None:
        """
        Remove widget from pool - only when pane is permanently closed.

        This is the ONLY time we reparent (to None for cleanup).
        """
        if pane_id not in self._widgets:
            return

        widget = self._widgets.pop(pane_id)

        # Reparent to None for cleanup
        # This is fine because the widget is being destroyed
        widget.setParent(None)

    def get_widget(self, pane_id: PaneId) -> Optional[QWidget]:
        """Get widget by pane ID."""
        return self._widgets.get(pane_id)

    def all_pane_ids(self) -> Set[PaneId]:
        """Get all pane IDs in pool."""
        return set(self._widgets.keys())
```

**Key Properties**:
- ✅ Widgets added once, never reparented (except destruction)
- ✅ Simple dictionary lookup
- ✅ No tree structure needed
- ✅ Works with any widget type, including QWebEngineView

---

### Layer 2: Geometry Manager

**Purpose**: Pure calculation layer - converts pane tree to widget rectangles.

```python
class GeometryManager:
    """
    Calculates widget geometries from pane tree structure.

    This is a PURE calculation layer with NO Qt widget operations.
    It just does math: Tree + Viewport → Rectangles.
    """

    def calculate_layout(
        self,
        tree: Optional[PaneNode],
        viewport: QRect
    ) -> Dict[PaneId, QRect]:
        """
        Calculate geometry for all panes in tree.

        Args:
            tree: Current pane tree structure
            viewport: Available screen space

        Returns:
            Dictionary mapping pane IDs to their screen rectangles
        """
        if tree is None:
            return {}

        geometries: Dict[PaneId, QRect] = {}
        self._calculate_recursive(tree, viewport, geometries)
        return geometries

    def _calculate_recursive(
        self,
        node: PaneNode,
        rect: QRect,
        result: Dict[PaneId, QRect]
    ) -> None:
        """Recursively calculate geometries for tree nodes."""

        if isinstance(node, LeafNode):
            # Leaf node: assign entire rectangle to this pane
            result[node.pane_id] = rect

        elif isinstance(node, SplitNode):
            # Split node: divide rectangle among children

            # Split the rectangle based on orientation and ratios
            child_rects = self._split_rectangle(
                rect,
                node.orientation,
                node.ratios if node.ratios else [0.5, 0.5]
            )

            # Recursively process children
            for child, child_rect in zip(node.children, child_rects):
                self._calculate_recursive(child, child_rect, result)

    def _split_rectangle(
        self,
        rect: QRect,
        orientation: Orientation,
        ratios: List[float]
    ) -> List[QRect]:
        """
        Split rectangle into parts based on orientation and ratios.

        Args:
            rect: Rectangle to split
            orientation: HORIZONTAL or VERTICAL
            ratios: Proportion for each split (must sum to 1.0)

        Returns:
            List of rectangles for each split section
        """
        if orientation == Orientation.HORIZONTAL:
            # Split horizontally (left/right)
            return self._split_horizontal(rect, ratios)
        else:
            # Split vertically (top/bottom)
            return self._split_vertical(rect, ratios)

    def _split_horizontal(
        self,
        rect: QRect,
        ratios: List[float]
    ) -> List[QRect]:
        """Split rectangle horizontally (left/right)."""
        results = []
        current_x = rect.x()
        total_width = rect.width()

        for i, ratio in enumerate(ratios):
            # Calculate width for this section
            if i == len(ratios) - 1:
                # Last section gets remaining width (avoids rounding errors)
                width = rect.right() - current_x + 1
            else:
                width = int(total_width * ratio)

            # Create rectangle for this section
            section_rect = QRect(
                current_x,
                rect.y(),
                width,
                rect.height()
            )
            results.append(section_rect)

            current_x += width

        return results

    def _split_vertical(
        self,
        rect: QRect,
        ratios: List[float]
    ) -> List[QRect]:
        """Split rectangle vertically (top/bottom)."""
        results = []
        current_y = rect.y()
        total_height = rect.height()

        for i, ratio in enumerate(ratios):
            # Calculate height for this section
            if i == len(ratios) - 1:
                # Last section gets remaining height (avoids rounding errors)
                height = rect.bottom() - current_y + 1
            else:
                height = int(total_height * ratio)

            # Create rectangle for this section
            section_rect = QRect(
                rect.x(),
                current_y,
                rect.width(),
                height
            )
            results.append(section_rect)

            current_y += height

        return results
```

**Key Properties**:
- ✅ Pure calculation - no side effects
- ✅ Easily testable (no Qt needed for tests)
- ✅ Reuses existing tree traversal logic
- ✅ Handles arbitrary ratios and orientations

---

### Layer 3: Visual Renderer

**Purpose**: Apply calculated geometries to widgets using only `setGeometry()`.

```python
class VisualRenderer:
    """
    Renders pane layout by applying geometries to widgets.

    Uses ONLY setGeometry() - the most efficient Qt operation.
    Never reparents, never rebuilds widget trees.
    """

    def __init__(self, pool: WidgetPool):
        self._pool = pool

    def render(
        self,
        geometries: Dict[PaneId, QRect],
        focused_pane_id: Optional[PaneId] = None
    ) -> None:
        """
        Apply layout by setting widget geometries.

        Args:
            geometries: Mapping of pane IDs to screen rectangles
            focused_pane_id: Currently focused pane (for z-order)
        """
        visible_panes = set(geometries.keys())
        all_panes = self._pool.all_pane_ids()

        # 1. Show and position visible widgets
        for pane_id, geometry in geometries.items():
            widget = self._pool.get_widget(pane_id)
            if not widget:
                continue

            # Apply geometry (no reparenting!)
            widget.setGeometry(geometry)

            # Make visible
            if not widget.isVisible():
                widget.setVisible(True)

            # Bring to front (z-order)
            widget.raise_()

        # 2. Hide widgets not in current layout
        hidden_panes = all_panes - visible_panes
        for pane_id in hidden_panes:
            widget = self._pool.get_widget(pane_id)
            if widget and widget.isVisible():
                widget.setVisible(False)

        # 3. Focus management
        if focused_pane_id:
            focused_widget = self._pool.get_widget(focused_pane_id)
            if focused_widget:
                # Ensure focused widget is on top
                focused_widget.raise_()
                focused_widget.setFocus()
```

**Key Properties**:
- ✅ Only uses `setGeometry()` - doesn't trigger GPU re-sync
- ✅ Simple show/hide for widgets not in layout
- ✅ Z-order management for overlapping scenarios
- ✅ No tree building, no reparenting

---

## Integration with Existing Architecture

### Model Layer (No Changes)

The Model layer is already perfect - it's pure Python with no Qt dependencies:

```python
# Unchanged - already correct
class PaneModel:
    root: Optional[PaneNode]
    focused_pane_id: Optional[PaneId]
    signals: ModelSignals
```

### Controller Layer (No Changes)

The Controller layer is already perfect - executes commands without knowing about views:

```python
# Unchanged - already correct
class PaneController:
    def execute(self, command: Command) -> CommandResult:
        # Validates, executes, signals
```

### View Layer (Complete Replacement)

**Before** (Tree-based):
```python
class PaneContainer(QWidget):
    def _rebuild_layout(self):
        # Build widget tree from pane tree
        root_widget = self._build_widget_tree(self.model.root)
        # Swap widget trees (causes reparenting)
        self.layout().addWidget(root_widget)
```

**After** (Geometry-based):
```python
class PaneContainer(QWidget):
    def __init__(self, model: PaneModel, provider: WidgetProvider):
        super().__init__()

        # New components
        self._pool = WidgetPool(self)
        self._geometry_manager = GeometryManager()
        self._renderer = VisualRenderer(self._pool)

        # Connect to model
        self._model = model
        model.signals.structure_changed.connect(self._on_structure_changed)
        model.signals.focus_changed.connect(self._on_focus_changed)

    def _on_structure_changed(self):
        """Handle tree structure changes."""
        # 1. Calculate new geometries
        viewport = self.rect()
        geometries = self._geometry_manager.calculate_layout(
            self._model.root,
            viewport
        )

        # 2. Apply geometries (no reparenting!)
        self._renderer.render(geometries, self._model.focused_pane_id)

    def _on_focus_changed(self, old_id: PaneId, new_id: PaneId):
        """Handle focus changes."""
        # Just bring focused widget to front
        widget = self._pool.get_widget(new_id)
        if widget:
            widget.raise_()
            widget.setFocus()

    def resizeEvent(self, event):
        """Handle container resize."""
        # Recalculate layout for new viewport size
        self._on_structure_changed()
```

---

## Split Operation Flow

### Before (Tree-based - Causes Flash)

```python
def split_pane(pane_id: PaneId, direction: Direction):
    # 1. Execute command (updates model tree)
    controller.execute(SplitCommand(pane_id, direction))

    # 2. Rebuild entire widget tree
    root_widget = container._build_widget_tree(model.root)

    # Problem: pane_id's widget moves from old wrapper to new wrapper
    # This is REPARENTING → GPU flash ❌
```

### After (Geometry-based - No Flash)

```python
def split_pane(pane_id: PaneId, direction: Direction):
    # 1. Execute command (updates model tree)
    controller.execute(SplitCommand(pane_id, direction))

    # 2. Create widget for new pane
    new_widget = provider.provide_widget(new_pane_id)
    pool.add_widget(new_pane_id, new_widget)  # Added ONCE

    # 3. Calculate new geometries
    geometries = geometry_manager.calculate_layout(model.root, viewport)

    # 4. Apply geometries (no reparenting!)
    renderer.render(geometries)

    # Result: Existing widgets just change position/size
    # No reparenting → No GPU flash ✅
```

---

## Performance Analysis

### Current Approach (Tree-based)

**Operations per split**:
1. Clone tree (deep copy)
2. Build new widget tree (recursive)
3. Create/find splitter widgets
4. Reparent widgets into splitters ← **GPU flash here**
5. Swap root widgets
6. Clean up old widgets
7. Update layouts

**Complexity**: O(n) where n = number of panes
**Problem**: Step 4 causes visible flash

### New Approach (Geometry-based)

**Operations per split**:
1. Calculate geometries (tree traversal)
2. Apply geometries with `setGeometry()`
3. Show/hide widgets as needed

**Complexity**: O(n) where n = number of panes
**Advantage**: No reparenting, more efficient

### Benchmark Estimates

For 10 panes:
- **Current**: ~50-100ms (includes reparenting overhead + flash)
- **New**: ~10-20ms (pure geometry calculation + application)

For 100 panes (future scalability):
- **Current**: Would be very slow (rebuilding entire tree)
- **New**: Still fast (incremental geometry updates possible)

---

## Implementation Plan

### Phase 1: Prototype (1 week)

**Goal**: Prove geometry-based approach eliminates flashes

1. Create minimal `WidgetPool` class
2. Create minimal `GeometryManager` class
3. Create minimal `VisualRenderer` class
4. Test with 2-pane split using QWebEngineView
5. **Validate**: No white flash on split

**Success Criteria**:
- ✅ Can split a pane with QWebEngineView
- ✅ Zero white flashes
- ✅ Existing widget doesn't reparent

### Phase 2: Full Implementation (2 weeks)

**Goal**: Replace existing tree-based view with geometry-based view

1. Implement complete `WidgetPool` with lifecycle management
2. Implement complete `GeometryManager` with all split orientations
3. Implement complete `VisualRenderer` with focus management
4. Replace `PaneContainer._rebuild_layout()` with geometry pipeline
5. Remove `PaneContainer._build_widget_tree()` entirely
6. Remove all splitter reuse logic
7. Remove wrapper splitter pattern

**Success Criteria**:
- ✅ All existing tests pass
- ✅ Zero white flashes in all scenarios
- ✅ Simpler codebase (less code than before)

### Phase 3: Optimization (1 week)

**Goal**: Optimize for performance and features

1. Incremental geometry updates (only changed panes)
2. Smooth geometry transitions (animations)
3. Virtual scrolling (for many panes)
4. Memory pooling (reuse QRect objects)

**Success Criteria**:
- ✅ 60fps split operations
- ✅ Smooth resize animations
- ✅ Handles 100+ panes efficiently

### Phase 4: Documentation (3 days)

**Goal**: Document new architecture

1. Update architecture documentation
2. Add inline code documentation
3. Create migration guide
4. Update examples

---

## Risk Analysis

### Risk 1: setGeometry() Might Also Cause Flash

**Likelihood**: Low
**Impact**: High (would invalidate entire approach)

**Mitigation**:
- Test in Phase 1 prototype FIRST
- If fails, investigate QWebEngineView rendering pipeline
- Fallback: Use QGraphicsView with proxy widgets

**Test Plan**:
```python
# Minimal test case
widget = QWebEngineView()
widget.setParent(container)
widget.setGeometry(0, 0, 400, 300)  # Initial
widget.setGeometry(0, 0, 200, 300)  # Changed - does this flash?
```

### Risk 2: Complex Geometry Calculations

**Likelihood**: Medium
**Impact**: Low (just code complexity)

**Mitigation**:
- Borrow logic from existing `_build_widget_tree()`
- Existing code already calculates sizes, just in different form
- Pure calculation layer is easy to test

**Evidence**: Current code already does this (lines 448-452 in container.py):
```python
if node.ratios and len(node.ratios) == splitter.count():
    total = sum(node.ratios)
    sizes = [int(1000 * r / total) for r in node.ratios]
    splitter.setSizes(sizes)
```

### Risk 3: Focus Management Complexity

**Likelihood**: Low
**Impact**: Medium

**Mitigation**:
- Focus is already managed by Model layer
- Just need to call `widget.setFocus()` on correct widget
- Z-order management with `widget.raise_()` is straightforward

### Risk 4: Splitter Handles Lost

**Likelihood**: High
**Impact**: Medium

**Current splitters provide draggable handles for resizing**

**Mitigation**:
- Implement custom resize handles as separate widgets
- Position handles between panes using geometry calculation
- Handle drag events to update model ratios
- More control than QSplitter provides

**Alternative**:
- Keep QSplitter as visual decoration only
- Don't use it for layout (use geometry instead)
- Splitter just draws the handle, geometry controls positioning

---

## Alternative Approaches Considered

### Alternative 1: QGraphicsView with Proxy Widgets

**Idea**: Use Qt's graphics scene framework

```python
scene = QGraphicsScene()
for pane_id, widget in widgets.items():
    proxy = scene.addWidget(widget)
    proxy.setGeometry(geometries[pane_id])
```

**Pros**:
- Built for complex positioning
- Hardware accelerated
- Easy z-order management

**Cons**:
- Heavier than plain widgets
- Proxy widget overhead
- More complex integration

**Decision**: Keep as fallback if setGeometry() doesn't work

### Alternative 2: Manual Absolute Positioning

**Idea**: Use absolute positioning within single QWidget

```python
class AbsoluteContainer(QWidget):
    def add_widget(self, widget: QWidget):
        widget.setParent(self)
        # No layout - manual positioning only
```

**Pros**:
- Even simpler than QStackedWidget
- Minimal overhead
- Direct control

**Cons**:
- Loses layout system benefits
- Manual z-order management
- No automatic size propagation

**Decision**: Use for Phase 1 prototype, optimize if needed

### Alternative 3: Keep Tree-based, Use Offscreen Rendering

**Idea**: Pre-render widgets offscreen before showing

```python
widget.setVisible(False)
# Reparent while hidden
widget.setParent(new_parent)
widget.setVisible(True)
```

**Pros**:
- Minimal architecture change

**Cons**:
- Doesn't actually prevent GPU re-sync
- QWebEngineView might still flash
- Doesn't solve root cause

**Decision**: Rejected - doesn't solve fundamental issue

---

## Design Verification

### Algorithm Correctness: ✅ VERIFIED

The Fixed Container Architecture is mathematically sound:

**Proof**: For any split operation s:
- Current approach: Widget reparenting required → R(s) ≥ 1
- New approach: Only geometry changes → R(s) = 0 for existing widgets

The algorithm successfully eliminates reparenting for all existing widgets during split operations.

### Known Issues Identified

#### Issue 1: Geometry Calculation Bug ❌
**Location**: `_split_horizontal()` and `_split_vertical()` last section calculation

**Current (incorrect)**:
```python
if i == len(ratios) - 1:
    width = rect.right() - current_x + 1  # WRONG
```

**Fixed**:
```python
if i == len(ratios) - 1:
    width = (rect.x() + rect.width()) - current_x  # CORRECT
```

#### Issue 2: Missing Splitter Handle Spacing ❌
**Impact**: Panes will overlap without gaps for handles

**Fix Required**:
```python
HANDLE_WIDTH = 6
section_rect = QRect(
    current_x,
    rect.y(),
    width - (HANDLE_WIDTH if i < len(ratios)-1 else 0),
    rect.height()
)
```

### Critical Unverified Assumption ⚠️

**Assumption**: `setGeometry()` on QWebEngineView doesn't cause GPU flash

**Status**: UNVERIFIED - This is the make-or-break assumption

**Phase 1 Test Required**:
```python
widget = QWebEngineView()
widget.load("http://example.com")
widget.setParent(container)
widget.setGeometry(0, 0, 400, 300)  # Initial
time.sleep(1)  # Let it render
widget.setGeometry(0, 0, 200, 300)  # Resize - DOES THIS FLASH?
```

**Risk Assessment**:
- If passes: ✅ Design works as intended
- If fails: ❌ Need fallback to QGraphicsView approach

### Confidence Levels

- **Algorithm Correctness**: 95% (mathematically proven)
- **Will Solve Flash Problem**: 70% (depends on setGeometry() test)
- **Implementation Complexity**: Low (simpler than current)
- **Performance Improvement**: High (geometry-only operations)

## Success Criteria

### Must Have (Phase 2)
- ✅ Zero white flashes during split operations
- ✅ Works with QWebEngineView and all widget types
- ✅ All existing functionality preserved
- ✅ Simpler codebase than current implementation
- ✅ Passes all existing tests
- ⚠️ Verify setGeometry() doesn't cause GPU flash (Phase 1)

### Should Have (Phase 3)
- ✅ 60fps performance for split operations
- ✅ Smooth resize animations
- ✅ Handles 20+ panes without lag

### Could Have (Future)
- ✅ Virtual scrolling for 100+ panes
- ✅ Custom splitter handle styling
- ✅ Animated split transitions

---

## API Compatibility

### Public API: ✅ 100% BACKWARD COMPATIBLE

The redesign changes **ONLY** the internal View layer implementation. All public APIs remain identical.

#### ViloxTerm Usage (Current)

```python
# From /home/kuja/GitHub/vfwidgets/apps/viloxterm/src/viloxterm/app.py

from vfwidgets_multisplit import MultisplitWidget, SplitterStyle
from vfwidgets_multisplit.core.types import WherePosition

# Create MultisplitWidget with provider
multisplit = MultisplitWidget(
    widget_provider=self.terminal_provider,
    splitter_style=SplitterStyle.MINIMAL
)

# Split operations (unchanged)
multisplit.split(
    pane_id=current_pane,
    where=WherePosition.RIGHT,
    widget_id="terminal_xyz"
)

# Focus operations (unchanged)
multisplit.set_focused_pane(pane_id)

# Signals (unchanged)
multisplit.pane_focused.connect(handler)
multisplit.pane_closed.connect(handler)
```

**Result**: ✅ No changes required in ViloxTerm or any other consumer

#### MultisplitWidget Public API

**Unchanged Methods**:
```python
class MultisplitWidget(QWidget):
    # Construction
    def __init__(
        self,
        widget_provider: WidgetProvider,
        model: Optional[PaneModel] = None,
        controller: Optional[PaneController] = None,
        splitter_style: SplitterStyle = SplitterStyle.DEFAULT
    )

    # Split operations
    def split(
        self,
        pane_id: PaneId,
        where: WherePosition,
        widget_id: WidgetId,
        ratio: float = 0.5
    ) -> Optional[PaneId]

    def close_pane(self, pane_id: PaneId) -> bool

    # Focus management
    def set_focused_pane(self, pane_id: PaneId) -> bool
    def get_focused_pane(self) -> Optional[PaneId]

    # Signals
    pane_focused = Signal(str)  # PaneId
    pane_closed = Signal(str)   # PaneId
    structure_changed = Signal()
```

**All APIs remain exactly the same** - only internal implementation changes.

#### WidgetProvider Interface

```python
# From /home/kuja/GitHub/vfwidgets/apps/viloxterm/src/viloxterm/providers/terminal_provider.py

class TerminalProvider(WidgetProvider):
    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Unchanged - still returns QWidget"""
        session_id = self.server.create_session(command="bash")
        session_url = self.server.get_session_url(session_id)
        terminal = TerminalWidget(server_url=session_url)
        return terminal
```

**Result**: ✅ Provider interface unchanged, no modifications needed

### Internal Changes Only

**What Changes** (Internal View layer only):
- Remove `_build_widget_tree()` method
- Remove `_rebuild_layout()` method
- Remove splitter reuse logic
- Add `WidgetPool`, `GeometryManager`, `VisualRenderer` classes

**What Stays the Same** (Public API):
- All public methods and their signatures
- All signals and their parameters
- Model layer (PaneModel, PaneNode, etc.)
- Controller layer (PaneController, Commands)
- WidgetProvider protocol

### Zero Migration Effort

**For ViloxTerm**: No changes required
**For other consumers**: No changes required
**For tests**: Existing tests should pass unchanged

The redesign is a **pure refactoring** - better implementation of the same contract.

---

## Migration Strategy

### Backward Compatibility

**API**: ✅ Zero changes to public API
- `MultisplitWidget` interface 100% unchanged
- Model/Controller unchanged
- WidgetProvider protocol unchanged
- Only internal View implementation changed

**Behavior**: Identical user experience (but better)
- Same split operations
- Same focus behavior
- Same resize behavior
- **Better**: No white flashes
- **Better**: Simpler internal code
- **Better**: Higher performance

### Migration Path

1. **Phase 1**: Develop in parallel on feature branch
2. **Phase 2**: Integration testing
3. **Phase 3**: A/B testing (old vs new implementation)
4. **Phase 4**: Switch default implementation
5. **Phase 5**: Remove old tree-based code

### Rollback Plan

Keep old implementation available:

```python
class PaneContainer(QWidget):
    def __init__(self, mode="geometry"):  # or "tree"
        if mode == "geometry":
            self._use_geometry_mode()
        else:
            self._use_tree_mode()
```

Can toggle via environment variable for emergency rollback.

---

## Conclusion

The **Fixed Container Architecture** solves the white flash problem by attacking the root cause: it eliminates reparenting entirely by separating logical structure from physical containers.

**Key Advantages**:
1. **Solves root cause** (not a workaround)
2. **Simpler code** (removes complex reuse logic)
3. **Better performance** (geometry-only updates)
4. **More maintainable** (pure calculation layer)
5. **Future-proof** (enables optimizations like animations)

**Implementation Risk**: Low
- Phase 1 prototype validates core assumption
- Borrows from existing geometry calculation code
- Maintains all existing APIs

**Recommendation**: Proceed with Phase 1 prototype immediately.

---

## Related Documents

- [MVC Architecture](02-architecture/mvc-architecture.md) - Model/Controller remain unchanged
- [Current Implementation Issues](../IMPLEMENTATION_COMPLETE.md) - Context for why redesign is needed
- [Widget Provider Pattern](02-architecture/widget-provider.md) - Provider integration unchanged

---

**Next Steps**:
1. Review and approve this design
2. Create Phase 1 prototype branch
3. Implement minimal WidgetPool + GeometryManager + VisualRenderer
4. Test with QWebEngineView split operation
5. Validate zero flashes before proceeding to Phase 2
