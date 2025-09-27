# Phase 0 Common Errors and Solutions

## Purpose
Help the multisplit-developer agent avoid common pitfalls and resolve typical implementation issues.

## Import Errors

### Error: ModuleNotFoundError
**Problem**: `from core.types import PaneId`
**Solution**: Use relative imports
```python
# Wrong
from core.types import PaneId

# Correct
from .types import PaneId  # For same directory
from ..core.types import PaneId  # For parent directory
```

### Error: Circular Import
**Problem**: Two modules importing each other
**Solution**: Use TYPE_CHECKING for type hints only
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .nodes import PaneNode  # Only imported during type checking
```

## Type Errors

### Error: NewType not working
**Problem**: `PaneId = NewType('PaneId', str)` not recognized
**Solution**: Import from typing
```python
from typing import NewType

PaneId = NewType('PaneId', str)
```

### Error: Forward reference issues
**Problem**: Class referencing itself in type hints
**Solution**: Use string literals
```python
class PaneNode:
    def clone(self) -> 'PaneNode':  # String literal for forward reference
        pass
```

## Test Errors

### Error: Tests not found
**Problem**: `python -m pytest` doesn't find tests
**Solution**: Ensure proper test structure
```python
# File must start with test_
# tests/test_module.py

import unittest

class TestClassName(unittest.TestCase):  # Must inherit unittest.TestCase
    def test_something(self):  # Method must start with test_
        pass

if __name__ == '__main__':
    unittest.main()
```

### Error: Import error in tests
**Problem**: Can't import module being tested
**Solution**: Use proper package imports
```python
# In tests/test_id_generation.py
from vfwidgets_multisplit.core.types import PaneId
from vfwidgets_multisplit.core.utils import generate_pane_id
```

## Architecture Violations

### Error: Qt import in Model
**Problem**: Accidentally importing Qt in core layer
**Solution**: Remove all Qt imports from core/
```python
# NEVER in core/ files:
from PySide6.QtCore import Signal  # ❌

# Instead use:
from .signals import AbstractSignal  # ✅
```

### Error: Direct model mutation
**Problem**: View trying to change model directly
**Solution**: Always go through controller
```python
# Wrong in View:
self.model.focused_pane_id = pane_id  # ❌

# Correct in View:
self.controller.execute_command(FocusCommand(pane_id))  # ✅
```

## Common Python Issues

### Error: Mutable default arguments
**Problem**: Using `[]` or `{}` as default arguments
**Solution**: Use None and create inside function
```python
# Wrong
def __init__(self, children: List[Node] = []):  # ❌
    self.children = children

# Correct
def __init__(self, children: Optional[List[Node]] = None):  # ✅
    self.children = children or []
```

### Error: Float comparison
**Problem**: Direct equality check on floats
**Solution**: Use tolerance for comparison
```python
# Wrong
if sum(ratios) == 1.0:  # ❌

# Correct
if abs(sum(ratios) - 1.0) <= 0.001:  # ✅
```

## Geometry Calculation Issues

### Error: Integer division truncation
**Problem**: Lost pixels due to integer division
**Solution**: Give remaining pixels to last child
```python
for i, ratio in enumerate(ratios):
    if i == len(ratios) - 1:
        # Last child gets remaining space
        child_width = bounds.x + bounds.width - current_x
    else:
        child_width = int(available_width * ratio)
```

### Error: Negative dimensions
**Problem**: Bounds with negative width/height
**Solution**: Validate in __post_init__
```python
@dataclass(frozen=True)
class Bounds:
    width: int
    height: int

    def __post_init__(self):
        if self.width < 0 or self.height < 0:
            raise ValueError(f"Negative dimensions: {self.width}x{self.height}")
```

## Signal Issues

### Error: Memory leak from signal handlers
**Problem**: Strong references prevent garbage collection
**Solution**: Use weakref
```python
import weakref

class AbstractSignal:
    def __init__(self):
        self._handlers: List[weakref.ref] = []  # Weak references

    def connect(self, handler):
        self._handlers.append(weakref.ref(handler))
```

### Error: Handler exception breaks emission
**Problem**: One bad handler stops all handlers
**Solution**: Catch and continue
```python
def emit(self, *args):
    for ref in self._handlers:
        handler = ref()
        if handler:
            try:
                handler(*args)
            except Exception as e:
                print(f"Handler error: {e}")
                # Continue to next handler
```

## Tree Traversal Issues

### Error: Infinite recursion
**Problem**: Cycles in tree structure
**Solution**: Track visited nodes
```python
def traverse(node, visited=None):
    if visited is None:
        visited = set()

    if node.node_id in visited:
        return  # Prevent cycle

    visited.add(node.node_id)
    # Continue traversal
```

### Error: None node crashes visitor
**Problem**: Visitor doesn't handle None
**Solution**: Check before visiting
```python
def visit_children(self, node: SplitNode):
    for child in node.children:
        if child is not None:  # Check first
            child.accept(self)
```

## Transaction Issues

### Error: Nested transaction breaks
**Problem**: Inner transaction interferes with outer
**Solution**: Propagate to parent
```python
class NestedTransactionContext(TransactionContext):
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type or self.rolled_back:
            self.parent.rollback()  # Propagate rollback
```

### Error: Partial rollback
**Problem**: Some commands don't undo properly
**Solution**: Store undo data during execute
```python
def execute(self, model):
    # Store state for undo
    self.old_value = model.value
    # Make change
    model.value = self.new_value

def undo(self, model):
    # Restore old state
    model.value = self.old_value
```

## File Structure Issues

### Error: Package not found
**Problem**: Python doesn't recognize package
**Solution**: Ensure __init__.py exists
```bash
src/vfwidgets_multisplit/
├── __init__.py  # Required
├── core/
│   ├── __init__.py  # Required
│   └── types.py
└── view/
    ├── __init__.py  # Required
    └── reconciler.py
```

### Error: Relative import beyond top level
**Problem**: Too many `..` in relative import
**Solution**: Use absolute imports from package root
```python
# Instead of
from ....core.types import PaneId  # ❌

# Use
from vfwidgets_multisplit.core.types import PaneId  # ✅
```

## Debugging Tips

### Check Import Path
```python
import sys
print(sys.path)  # See where Python looks for modules
```

### Verify Module Structure
```python
import vfwidgets_multisplit
print(dir(vfwidgets_multisplit))  # See what's in the module
```

### Test Individual Functions
```python
# Run specific test
python -m pytest tests/test_id_generation.py::TestIDGeneration::test_pane_id_generation -v
```

### Check Type Hints
```python
# Use mypy for type checking
mypy src/vfwidgets_multisplit/core/types.py
```

## Prevention Checklist

Before implementing each task:
- [ ] Check all dependencies are complete
- [ ] Verify import paths are correct
- [ ] Ensure __init__.py files exist
- [ ] Use relative imports within package
- [ ] Add TYPE_CHECKING for circular imports
- [ ] Handle None and empty cases
- [ ] Use weakref for callbacks
- [ ] Validate all inputs
- [ ] Write tests first
- [ ] Run tests before committing