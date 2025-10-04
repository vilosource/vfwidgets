# Fixed Container Architecture - Implementation Task Guide

**Purpose**: Step-by-step implementation guide for the Fixed Container Architecture redesign
**Status**: Ready for execution
**Tracking**: Use todo list to mark tasks as in_progress → completed

---

## Phase 1: Prototype & Validation (Critical Path)

### Task 1: Create Prototype Directory Structure
**Status**: Pending
**Priority**: P0 (Blocker)
**Estimated Time**: 5 minutes

**Location**:
```
widgets/multisplit_widget/examples/prototype/
├── __init__.py
├── widget_pool.py
├── geometry_manager.py
└── visual_renderer.py
```

**Command**:
```bash
cd widgets/multisplit_widget/examples
mkdir -p prototype
touch prototype/__init__.py
touch prototype/widget_pool.py
touch prototype/geometry_manager.py
touch prototype/visual_renderer.py
```

**Acceptance Criteria**:
- ✅ Directory exists
- ✅ All files created
- ✅ Can import from prototype module

---

### Task 2: Implement WidgetPool Class
**Status**: Pending
**Priority**: P0 (Blocker)
**Estimated Time**: 30 minutes

**File**: `examples/prototype/widget_pool.py`

**Requirements**:
1. Fixed container using single QWidget parent
2. Dictionary storage: `{pane_id: widget}`
3. Methods: `add_widget()`, `remove_widget()`, `get_widget()`, `all_pane_ids()`

**Implementation Template**:
```python
"""Widget Pool - Fixed container for all pane widgets."""

from typing import Dict, Optional, Set
from PySide6.QtWidgets import QWidget

class WidgetPool:
    """
    Fixed container for all pane widgets.

    Widgets are added once and never reparented (except on destruction).
    This eliminates the GPU texture re-sync flash on QWebEngineView.
    """

    def __init__(self, parent: QWidget):
        """Initialize widget pool with fixed container."""
        self._container = parent  # Fixed parent for ALL widgets
        self._widgets: Dict[str, QWidget] = {}

    def add_widget(self, pane_id: str, widget: QWidget) -> None:
        """
        Add widget to pool - happens ONCE per widget.

        Args:
            pane_id: Unique pane identifier
            widget: Widget to add

        Raises:
            ValueError: If pane_id already exists
        """
        if pane_id in self._widgets:
            raise ValueError(f"Widget already exists for pane {pane_id}")

        # CRITICAL: Set parent ONCE - never changed after this
        widget.setParent(self._container)

        # Store reference
        self._widgets[pane_id] = widget

        # Initially hidden - renderer will show it
        widget.setVisible(False)

        print(f"✅ Added widget to pool: {pane_id} (parent set, hidden)")

    def remove_widget(self, pane_id: str) -> None:
        """
        Remove widget from pool - only when permanently closed.

        This is the ONLY time we reparent (to None for cleanup).
        """
        if pane_id not in self._widgets:
            return

        widget = self._widgets.pop(pane_id)
        widget.setParent(None)  # Reparent to None for cleanup

        print(f"❌ Removed widget from pool: {pane_id}")

    def get_widget(self, pane_id: str) -> Optional[QWidget]:
        """Get widget by pane ID."""
        return self._widgets.get(pane_id)

    def all_pane_ids(self) -> Set[str]:
        """Get all pane IDs currently in pool."""
        return set(self._widgets.keys())
```

**Testing**:
```python
# Test in Python REPL
from PySide6.QtWidgets import QApplication, QWidget, QTextEdit
app = QApplication([])
container = QWidget()
pool = WidgetPool(container)

widget = QTextEdit()
pool.add_widget("pane_1", widget)
assert widget.parent() == container  # ✅
assert not widget.isVisible()  # ✅
```

**Acceptance Criteria**:
- ✅ Can add widgets
- ✅ Widget parent is set to container
- ✅ Widgets are initially hidden
- ✅ Can retrieve widgets by pane_id
- ✅ ValueError on duplicate add

---

### Task 3: Implement GeometryManager Class
**Status**: Pending
**Priority**: P0 (Blocker)
**Estimated Time**: 45 minutes

**File**: `examples/prototype/geometry_manager.py`

**Requirements**:
1. Pure calculation - no Qt widget operations
2. Calculate rectangles from tree structure
3. Handle horizontal/vertical splits
4. Include handle spacing (6px gap)
5. Correct last-section width calculation

**Implementation Template**:
```python
"""Geometry Manager - Pure calculation layer for widget positioning."""

from typing import Dict, List
from PySide6.QtCore import QRect

class GeometryManager:
    """
    Calculates widget geometries from pane structure.

    Pure calculation layer - no Qt widget operations.
    Just math: rectangles → rectangles
    """

    HANDLE_WIDTH = 6  # Gap between panes for splitter handle

    def calculate_simple_split(
        self,
        viewport: QRect,
        orientation: str,  # "horizontal" or "vertical"
        ratio: float = 0.5
    ) -> Dict[str, QRect]:
        """
        Calculate geometry for simple 2-pane split.

        Args:
            viewport: Available screen space
            orientation: "horizontal" (left/right) or "vertical" (top/bottom)
            ratio: First pane ratio (0.0-1.0)

        Returns:
            {"left": QRect, "right": QRect} or {"top": QRect, "bottom": QRect}
        """
        if orientation == "horizontal":
            return self._split_horizontal(viewport, [ratio, 1.0 - ratio])
        else:
            return self._split_vertical(viewport, [ratio, 1.0 - ratio])

    def _split_horizontal(
        self,
        rect: QRect,
        ratios: List[float]
    ) -> Dict[str, QRect]:
        """
        Split rectangle horizontally (left/right).

        Returns dict with keys: "pane_0", "pane_1", etc.
        """
        results = {}
        current_x = rect.x()
        total_width = rect.width()

        for i, ratio in enumerate(ratios):
            # Calculate width for this section
            if i == len(ratios) - 1:
                # Last section: use remaining space (avoids rounding errors)
                width = (rect.x() + rect.width()) - current_x
            else:
                # Not last: calculate from ratio, minus handle space
                width = int(total_width * ratio) - self.HANDLE_WIDTH

            # Create rectangle for this section
            section_rect = QRect(
                current_x,
                rect.y(),
                width,
                rect.height()
            )

            results[f"pane_{i}"] = section_rect

            # Move to next section (includes handle gap)
            current_x += width + self.HANDLE_WIDTH

        return results

    def _split_vertical(
        self,
        rect: QRect,
        ratios: List[float]
    ) -> Dict[str, QRect]:
        """
        Split rectangle vertically (top/bottom).

        Returns dict with keys: "pane_0", "pane_1", etc.
        """
        results = {}
        current_y = rect.y()
        total_height = rect.height()

        for i, ratio in enumerate(ratios):
            # Calculate height for this section
            if i == len(ratios) - 1:
                # Last section: use remaining space
                height = (rect.y() + rect.height()) - current_y
            else:
                # Not last: calculate from ratio, minus handle space
                height = int(total_height * ratio) - self.HANDLE_WIDTH

            # Create rectangle for this section
            section_rect = QRect(
                rect.x(),
                current_y,
                rect.width(),
                height
            )

            results[f"pane_{i}"] = section_rect

            # Move to next section (includes handle gap)
            current_y += height + self.HANDLE_WIDTH

        return results
```

**Testing**:
```python
# Test calculations
from PySide6.QtCore import QRect
gm = GeometryManager()

viewport = QRect(0, 0, 800, 600)
result = gm.calculate_simple_split(viewport, "horizontal", 0.5)

# Verify left pane
assert result["pane_0"].x() == 0
assert result["pane_0"].width() == 400 - 6  # Minus handle

# Verify right pane
assert result["pane_1"].x() == 400  # After handle
assert result["pane_1"].width() == 400  # Gets remainder
```

**Acceptance Criteria**:
- ✅ Horizontal split works correctly
- ✅ Vertical split works correctly
- ✅ Handle spacing (6px) included
- ✅ Last section gets exact remainder
- ✅ No off-by-one errors

---

### Task 4: Implement VisualRenderer Class
**Status**: Pending
**Priority**: P0 (Blocker)
**Estimated Time**: 30 minutes

**File**: `examples/prototype/visual_renderer.py`

**Requirements**:
1. Apply geometries using ONLY `setGeometry()`
2. Show/hide widgets based on presence in layout
3. Manage z-order with `raise_()`
4. Focus management

**Implementation Template**:
```python
"""Visual Renderer - Apply geometries to widgets without reparenting."""

from typing import Dict, Optional
from PySide6.QtCore import QRect
from .widget_pool import WidgetPool

class VisualRenderer:
    """
    Renders layout by applying geometries to widgets.

    Uses ONLY setGeometry() - never reparents widgets.
    """

    def __init__(self, pool: WidgetPool):
        """Initialize renderer with widget pool."""
        self._pool = pool

    def render(
        self,
        geometries: Dict[str, QRect],
        focused_pane_id: Optional[str] = None
    ) -> None:
        """
        Apply layout by setting widget geometries.

        Args:
            geometries: Mapping of pane IDs to screen rectangles
            focused_pane_id: Currently focused pane (for z-order)
        """
        visible_panes = set(geometries.keys())
        all_panes = self._pool.all_pane_ids()

        print(f"🎨 Rendering {len(visible_panes)} panes...")

        # 1. Show and position visible widgets
        for pane_id, geometry in geometries.items():
            widget = self._pool.get_widget(pane_id)
            if not widget:
                print(f"⚠️  No widget for {pane_id}")
                continue

            # CRITICAL: Apply geometry (NO REPARENTING!)
            old_geo = widget.geometry()
            widget.setGeometry(geometry)

            print(f"  📐 {pane_id}: {old_geo} → {geometry}")

            # Make visible if hidden
            if not widget.isVisible():
                widget.setVisible(True)
                print(f"  👁️  Showed {pane_id}")

            # Bring to front (z-order)
            widget.raise_()

        # 2. Hide widgets not in current layout
        hidden_panes = all_panes - visible_panes
        for pane_id in hidden_panes:
            widget = self._pool.get_widget(pane_id)
            if widget and widget.isVisible():
                widget.setVisible(False)
                print(f"  🙈 Hid {pane_id}")

        # 3. Focus management
        if focused_pane_id:
            focused_widget = self._pool.get_widget(focused_pane_id)
            if focused_widget:
                focused_widget.raise_()
                focused_widget.setFocus()
                print(f"  🎯 Focused {focused_pane_id}")
```

**Testing**:
```python
# Test rendering
from PySide6.QtCore import QRect
renderer = VisualRenderer(pool)

geometries = {
    "pane_1": QRect(0, 0, 400, 600)
}
renderer.render(geometries)

widget = pool.get_widget("pane_1")
assert widget.isVisible()  # ✅
assert widget.geometry() == QRect(0, 0, 400, 600)  # ✅
```

**Acceptance Criteria**:
- ✅ Can render geometries
- ✅ Widgets become visible
- ✅ Correct geometry applied
- ✅ Hidden widgets not in layout
- ✅ Focus management works

---

### Task 5: Create Phase 1 Test Example
**Status**: Pending
**Priority**: P0 (Blocker - CRITICAL TEST)
**Estimated Time**: 1 hour

**File**: `examples/03_geometry_prototype.py`

**Requirements**:
1. Test with QWebEngineView (the problematic widget)
2. Visual comparison: tree-based vs geometry-based
3. Clear instructions for user to observe flash
4. Split button to trigger test

**Implementation Template**:
```python
"""
Phase 1 Prototype Test - QWebEngineView Flash Detection

CRITICAL TEST: Does setGeometry() on QWebEngineView cause GPU flash?

Instructions:
1. Run: python examples/03_geometry_prototype.py
2. Click "Split Pane" button
3. OBSERVE: Does the LEFT pane flash white?
   - NO FLASH = Phase 1 SUCCESS ✅ → Proceed to Phase 2
   - FLASH = Phase 1 FAIL ❌ → Need QGraphicsView fallback
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
)
from PySide6.QtCore import QRect, Qt
from PySide6.QtWebEngineWidgets import QWebEngineView

from prototype.widget_pool import WidgetPool
from prototype.geometry_manager import GeometryManager
from prototype.visual_renderer import VisualRenderer


class GeometryPrototypeTest(QWidget):
    """Phase 1 Prototype: Geometry-Based Layout Test."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phase 1: Geometry Prototype - Flash Detection Test")
        self.resize(800, 650)

        # Create components
        self._pool = WidgetPool(self)
        self._geometry_manager = GeometryManager()
        self._renderer = VisualRenderer(self._pool)

        # State
        self._is_split = False

        # Setup UI
        self._setup_ui()

        # Create initial widget
        self._create_initial_widget()

    def _setup_ui(self):
        """Create control panel."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Control panel at top
        panel = QWidget()
        panel.setMaximumHeight(50)
        panel.setStyleSheet("background: #2d2d2d; color: white;")
        panel_layout = QVBoxLayout(panel)

        # Instructions
        instructions = QLabel(
            "🔬 CRITICAL TEST: Click 'Split' and observe if LEFT pane flashes white"
        )
        instructions.setStyleSheet("font-weight: bold; padding: 5px;")
        panel_layout.addWidget(instructions)

        # Split button
        self.split_btn = QPushButton("Split Pane (Geometry Mode)")
        self.split_btn.clicked.connect(self._test_split)
        self.split_btn.setStyleSheet("""
            QPushButton {
                background: #0078d4;
                color: white;
                border: none;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #106ebe;
            }
        """)
        panel_layout.addWidget(self.split_btn)

        layout.addWidget(panel)

        # Rest of window is for panes (managed by geometry)
        # Don't add anything else - pool manages widget positioning

    def _create_initial_widget(self):
        """Create initial QWebEngineView widget."""
        webview = QWebEngineView()
        webview.setUrl("https://example.com")

        # Add to pool
        self._pool.add_widget("pane_1", webview)

        # Render full viewport
        viewport = QRect(0, 50, 800, 600)  # Below control panel
        self._renderer.render({"pane_1": viewport})

        print("✅ Initial widget created and rendered")

    def _test_split(self):
        """CRITICAL TEST: Split using geometry mode."""
        if self._is_split:
            print("⚠️  Already split")
            return

        print("\n" + "="*60)
        print("🔬 PHASE 1 CRITICAL TEST: Splitting with geometry mode...")
        print("="*60)

        # Create second widget
        webview2 = QWebEngineView()
        webview2.setUrl("https://example.org")
        self._pool.add_widget("pane_2", webview2)

        # Calculate split geometries (50/50 horizontal)
        viewport = QRect(0, 50, 800, 600)
        geometries = self._geometry_manager.calculate_simple_split(
            viewport, "horizontal", 0.5
        )

        # Map to actual pane IDs
        actual_geometries = {
            "pane_1": geometries["pane_0"],  # Left (existing)
            "pane_2": geometries["pane_1"]   # Right (new)
        }

        print(f"📐 Calculated geometries:")
        for pane_id, geo in actual_geometries.items():
            print(f"  {pane_id}: {geo}")

        # CRITICAL: Apply geometries using only setGeometry()
        print("\n🎨 Applying geometries (using setGeometry() only)...")
        self._renderer.render(actual_geometries)

        self._is_split = True
        self.split_btn.setEnabled(False)

        print("\n" + "="*60)
        print("👁️  OBSERVE: Did 'pane_1' (left, example.com) flash WHITE?")
        print("   NO FLASH = ✅ Phase 1 SUCCESS")
        print("   FLASH = ❌ Phase 1 FAIL")
        print("="*60 + "\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GeometryPrototypeTest()
    window.show()
    sys.exit(app.exec())
```

**Testing Instructions**:
1. Run: `python examples/03_geometry_prototype.py`
2. Wait for page to load (example.com)
3. Click "Split Pane (Geometry Mode)" button
4. **OBSERVE CAREFULLY**: Does the left pane (example.com) flash white?

**Acceptance Criteria**:
- ✅ App launches successfully
- ✅ Initial QWebEngineView renders example.com
- ✅ Split button works
- ✅ Second pane appears on right
- ✅ **CRITICAL**: Left pane does NOT flash white

---

### Task 6: Run Phase 1 Flash Detection Test
**Status**: Pending
**Priority**: P0 (DECISION POINT)
**Estimated Time**: 15 minutes

**Commands**:
```bash
cd widgets/multisplit_widget
python examples/03_geometry_prototype.py
```

**Test Procedure**:
1. Launch app
2. Wait 2-3 seconds for example.com to fully load
3. Click "Split Pane" button ONCE
4. **Observe left pane carefully** - does it flash white?

**Decision Tree**:

**If NO FLASH** ✅:
- Phase 1 SUCCESS
- setGeometry() is safe to use
- Proceed to tasks 8-22 (full implementation)
- Expected confidence: 95%

**If FLASH** ❌:
- Phase 1 FAIL
- setGeometry() triggers GPU re-sync
- Proceed to tasks 23-24 (QGraphicsView fallback)
- Expected confidence: 70%

**Document Results**:
- Take screenshot showing split state
- Note exact behavior observed
- Record in `docs/phase1-results-REPORT.md`

**Acceptance Criteria**:
- ✅ Test completed
- ✅ Results documented
- ✅ Decision made: proceed or pivot

---

### Task 7: Document Phase 1 Results
**Status**: Pending
**Priority**: P0
**Estimated Time**: 20 minutes

**File**: `docs/phase1-results-REPORT.md`

**Template**:
```markdown
# Phase 1 Results Report

**Date**: [DATE]
**Tester**: [NAME]
**Test**: Geometry-based layout with QWebEngineView

## Test Setup

- **Widget Type**: QWebEngineView
- **Initial URL**: https://example.com
- **Split Config**: 50/50 horizontal
- **Operation**: setGeometry() to resize existing widget

## Results

### Visual Observation

[SCREENSHOT - Before split]

[SCREENSHOT - After split]

**Flash Detected**: [YES/NO]

**Description**: [Detailed description of what was observed]

## Analysis

[If NO FLASH]:
- ✅ setGeometry() does NOT trigger GPU texture re-sync
- ✅ Geometry-based approach is VALID
- ✅ Proceed to Phase 2 implementation

[If FLASH]:
- ❌ setGeometry() DOES trigger GPU texture re-sync
- ❌ Geometry-based approach FAILS assumption
- ❌ Pivot to QGraphicsView fallback approach

## Decision

**Path Forward**: [Proceed to Phase 2 / Pivot to Fallback]

**Confidence Level**: [Percentage]

**Next Steps**: [List of next tasks to execute]
```

**Acceptance Criteria**:
- ✅ Report created
- ✅ Screenshots included
- ✅ Decision documented
- ✅ Next steps clear

---

## Phase 2: Full Implementation (If Phase 1 Passes)

### Tasks 8-16: Production Implementation
[Detailed specifications for each production component]

### Tasks 17-18: Testing & Integration
[Test procedures and ViloxTerm integration steps]

### Tasks 19-22: Optimization & Documentation
[Performance optimization and doc updates]

---

## Fallback Path (If Phase 1 Fails)

### Tasks 23-24: QGraphicsView Implementation
[Alternative approach using QGraphicsProxyWidget]

---

## Summary

**Total Tasks**: 25
**Critical Path**: Tasks 1-7 (Phase 1)
**Decision Point**: Task 6 results
**Estimated Total Time**:
- Phase 1: 3-4 hours
- Phase 2 (if proceed): 2-3 days
- Fallback (if pivot): 2-3 days

**Success Metrics**:
- Phase 1: No white flash on setGeometry()
- Phase 2: All tests pass, ViloxTerm works, no flashes
- Final: 100% API compatibility, better performance
