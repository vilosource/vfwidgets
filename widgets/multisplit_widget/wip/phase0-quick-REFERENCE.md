# Phase 0 Quick Reference Card

## File Locations Map

```
Project Root: /home/kuja/GitHub/vfwidgets/widgets/multisplit_widget/

Source Code:
├── src/vfwidgets_multisplit/
│   ├── __init__.py
│   ├── multisplit.py (main widget - Phase 3)
│   ├── core/
│   │   ├── __init__.py (create this)
│   │   ├── types.py (exists - enhance)
│   │   ├── utils.py (create)
│   │   ├── nodes.py (create)
│   │   ├── visitor.py (create)
│   │   ├── tree_utils.py (create)
│   │   ├── signals.py (create)
│   │   ├── signal_bridge.py (create)
│   │   └── geometry.py (create)
│   ├── view/
│   │   ├── __init__.py (create this)
│   │   └── tree_reconciler.py (create)
│   └── controller/
│       ├── __init__.py (create this)
│       ├── transaction.py (create)
│       └── controller.py (create)

Tests:
├── tests/
│   ├── __init__.py (exists)
│   ├── test_multisplit.py (exists - Phase 3)
│   ├── test_id_generation.py (create)
│   ├── test_tree_utils.py (create)
│   ├── test_signals.py (create)
│   ├── test_geometry.py (create)
│   ├── test_reconciler.py (create)
│   └── test_transactions.py (create)

Documentation:
├── wip/
│   ├── phase0-tasks-IMPLEMENTATION.md (task specs)
│   ├── phase0-progress-TRACKER.md (progress tracking)
│   ├── phase0-validation-CHECKLIST.md (validation)
│   ├── phase0-common-ERRORS.md (troubleshooting)
│   └── phase0-quick-REFERENCE.md (this file)
```

## Import Patterns

### Within core/ directory
```python
# In core/utils.py importing from core/types.py
from .types import PaneId, NodeId, WidgetId
```

### From view/ to core/
```python
# In view/tree_reconciler.py importing from core
from ..core.types import PaneId
from ..core.nodes import PaneNode, LeafNode, SplitNode
```

### From tests/
```python
# In tests/test_id_generation.py
from vfwidgets_multisplit.core.types import PaneId
from vfwidgets_multisplit.core.utils import generate_pane_id
```

## Common Commands

### Create a new Python file with proper structure
```python
"""Module description.

Pure Python implementation with no Qt dependencies.
"""

from typing import Optional, List, Dict
# Imports here

# Implementation here
```

### Run specific test
```bash
python -m pytest tests/test_id_generation.py -v
```

### Run all Phase 0 tests
```bash
python -m pytest tests/test_id_generation.py tests/test_tree_utils.py tests/test_signals.py tests/test_geometry.py tests/test_reconciler.py tests/test_transactions.py -v
```

### Check if module is importable
```bash
python -c "from vfwidgets_multisplit.core.types import PaneId; print('Success')"
```

## Type Patterns

### NewType for type safety
```python
from typing import NewType

PaneId = NewType('PaneId', str)
NodeId = NewType('NodeId', str)
```

### Forward references
```python
from __future__ import annotations  # At top of file

class Node:
    def clone(self) -> 'Node':  # Can reference itself
        pass
```

### TYPE_CHECKING for circular imports
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .controller import Controller  # Only during type checking
```

## Test Patterns

### Basic test structure
```python
import unittest

class TestFeature(unittest.TestCase):
    def setUp(self):
        """Run before each test."""
        self.test_data = create_data()

    def test_specific_case(self):
        """Test description."""
        # Arrange
        input_val = "test"

        # Act
        result = function(input_val)

        # Assert
        self.assertEqual(result, expected)

    def tearDown(self):
        """Run after each test."""
        cleanup()
```

### Common assertions
```python
self.assertEqual(a, b)  # a == b
self.assertNotEqual(a, b)  # a != b
self.assertTrue(x)  # x is True
self.assertFalse(x)  # x is False
self.assertIn(item, container)  # item in container
self.assertIsNone(x)  # x is None
self.assertIsNotNone(x)  # x is not None
self.assertAlmostEqual(a, b, places=3)  # For floats
self.assertRaises(ValueError, func, arg)  # Expects exception
```

## Validation Patterns

### Ratio validation
```python
def validate_ratios(ratios: List[float]) -> bool:
    if not ratios:
        return False
    if any(r < 0 for r in ratios):
        return False
    total = sum(ratios)
    return abs(total - 1.0) <= 0.001  # Tolerance for floats
```

### ID format validation
```python
def validate_id_format(id_string: str, id_type: str) -> bool:
    if id_type == "widget":
        parts = id_string.split(":")
        return len(parts) == 2 and all(parts)
    elif id_type in ["pane", "node"]:
        parts = id_string.split("_")
        return len(parts) == 2 and len(parts[1]) == 8
    return False
```

## MVC Rules Quick Check

| Layer | Can Import | Cannot Import | Can Do | Cannot Do |
|-------|------------|---------------|--------|-----------|
| Model | Python stdlib, types | Qt, View, Controller | Define data, emit signals | Create widgets, handle events |
| View | Model, Controller, Qt | - | Read Model, call Controller | Mutate Model, business logic |
| Controller | Model | Qt, View | Mutate Model, validate | Create widgets, render |

## Common Gotchas

1. **Missing __init__.py**: Python won't recognize as package
2. **Wrong imports**: Use relative imports within package
3. **Mutable defaults**: Use `None` not `[]` or `{}`
4. **Float comparison**: Use tolerance not `==`
5. **Strong references**: Use `weakref` for callbacks
6. **No error handling**: Always try/except in signal emission
7. **Direct mutation**: Always use commands for changes
8. **Qt in Model**: Never import Qt in core/

## Task Dependencies Graph

```
P0.1.1 (Types) ─┬─> P0.1.2 (ID Gen) ─┬─> P0.1.3 (Validation)
                │                     └─> P0.1.4 (Tests)
                │
                ├─> P0.2.1 (Nodes) ──> P0.2.2 (Visitor) ──> P0.2.3 (Utils) ──> P0.2.4 (Tests)
                │                                             │
                ├─> P0.4.1 (Bounds) ──────────────────────> P0.4.2 (Geometry) ──> P0.4.3 (Tests)
                │                                             │
                └─> P0.5.1 (Reconciler) ─────────────────────┴──> P0.5.2 (Tests)

P0.3.1 (Signals) ──> P0.3.2 (Bridge) ──> P0.3.3 (Tests)

P0.6.1 (Transaction) ──> P0.6.2 (Controller) ──> P0.6.3 (Tests)
```

## Success Criteria Checklist

For EVERY task:
- [ ] Dependencies complete
- [ ] __init__.py files exist
- [ ] Tests written first
- [ ] Implementation matches spec
- [ ] Tests pass
- [ ] No Qt in core/
- [ ] Type hints complete
- [ ] Docstrings present
- [ ] No linting errors
- [ ] Integration verified