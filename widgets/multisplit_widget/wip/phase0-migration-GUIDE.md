# Phase 0 Migration Guide

## Existing Code Analysis

### core/types.py
**Status**: EXISTS - Needs modification

**Keep in place**:
- PaneId type definition
- Orientation, WherePosition, Direction enums
- All exception classes
- Size, Position, Rect dataclasses

**Add**:
- NodeId = NewType('NodeId', str)
- WidgetId = NewType('WidgetId', str)
- Bounds dataclass (see P0.4.1)

**Move to core/utils.py** (P0.1.2):
- generate_pane_id() function
- Lines 96-99 in current file

**Move to core/tree_utils.py** (P0.2.3):
- normalize_ratios() function
- validate_ratio() function
- validate_ratios() function
- Lines 102-128 in current file

## Implementation Order

### Step 1: Enhance types.py (P0.1.1)
```python
# Add after line 15
NodeId = NewType('NodeId', str)
WidgetId = NewType('WidgetId', str)

# Add Bounds dataclass (P0.4.1) after Rect class
@dataclass(frozen=True)
class Bounds:
    x: int
    y: int
    width: int
    height: int
    # ... rest of implementation
```

### Step 2: Create utils.py (P0.1.2)
Move these functions from types.py:
- generate_pane_id() (lines 96-99)

Add new functions:
- generate_node_id()
- generate_widget_id()
- validate_id_format()
- parse_widget_id()

### Step 3: Continue with remaining tasks
Follow P0.2.1 onwards as documented in phase0-tasks-IMPLEMENTATION.md

## Testing Strategy

1. After each modification, run:
   ```bash
   python -c "from vfwidgets_multisplit.core.types import PaneId, NodeId, WidgetId"
   ```

2. Ensure backward compatibility:
   ```python
   # Old imports should still work
   from vfwidgets_multisplit.core.types import PaneId, Orientation
   ```

3. Run validation script:
   ```bash
   python wip/run_phase0_tests.py
   ```

## Notes

- The existing types.py has good foundation but mixes concerns
- Functions will be moved to appropriate modules for better organization
- All existing functionality will be preserved
- New functionality will be added incrementally
