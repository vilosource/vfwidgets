# Model Design

## Overview

The MultiSplit model layer is a pure Python implementation that maintains the tree structure and state without any Qt dependencies. It provides the single source of truth for all pane arrangements, focus state, and constraints while ensuring data integrity through validation and immutable operations.

## What This Covers

- **Tree Data Structures**: Node types, hierarchy, and invariants
- **State Management**: Focus tracking, metadata, and session state
- **Visitor Pattern**: Tree traversal and transformation algorithms
- **Validation System**: Invariant checking and error detection
- **Serialization**: Save/restore mechanisms for persistence
- **Signal Architecture**: Abstract signals for framework integration

## What This Doesn't Cover

- Command execution (see [Controller Design](controller-design.md))
- Widget management (see [View Design](view-design.md))
- User interaction handling (handled by Controller and View)
- Qt-specific functionality (strictly forbidden in Model)

---

## Core Data Structures

### Node Hierarchy

```python
class PaneNode(ABC):
    """Abstract base for all tree nodes"""

    def __init__(self, node_id: NodeId):
        self.node_id = node_id
        self.metadata: dict[str, Any] = {}
        self.created_at: float = time.time()

    @abstractmethod
    def accept(self, visitor: NodeVisitor) -> Any:
        """Visitor pattern implementation"""

    @abstractmethod
    def calculate_size_requirements(self) -> SizeRequirements:
        """Calculate minimum/preferred sizes"""

    @abstractmethod
    def validate_constraints(self) -> ValidationResult:
        """Check node-specific invariants"""

class LeafNode(PaneNode):
    """Terminal node containing widget reference"""

    def __init__(self, node_id: NodeId, pane_id: PaneId, widget_id: WidgetId):
        super().__init__(node_id)
        self.pane_id = pane_id  # Stable pane identifier
        self.widget_id = widget_id  # Application widget identifier
        self.size_constraints = SizeConstraints()
        self.focus_order_hint: Optional[int] = None

    def accept(self, visitor: NodeVisitor) -> Any:
        return visitor.visit_leaf(self)

class SplitNode(PaneNode):
    """Internal node with child nodes and layout"""

    def __init__(self, node_id: NodeId, orientation: Orientation,
                 children: list[PaneNode], ratios: list[float]):
        super().__init__(node_id)
        self._children = children
        self._ratios = self._normalize_ratios(ratios)
        self.orientation = orientation
        self.divider_config = DividerConfig()

        # Validate structure immediately
        self._validate_structure()

    @property
    def children(self) -> list[PaneNode]:
        """Immutable children access"""
        return self._children.copy()

    @property
    def ratios(self) -> list[float]:
        """Immutable ratios access"""
        return self._ratios.copy()

    def accept(self, visitor: NodeVisitor) -> Any:
        return visitor.visit_split(self)

    def _validate_structure(self):
        """Ensure split invariants"""
        if len(self._children) < 2:
            raise InvalidStructureError("Split must have >= 2 children")
        if len(self._ratios) != len(self._children):
            raise InvalidStructureError("Ratios count must match children count")
        if abs(sum(self._ratios) - 1.0) > 0.001:
            raise InvalidStructureError(f"Ratios sum to {sum(self._ratios)}, not 1.0")
```

### Model State Container

```python
class PaneModel:
    """Central model managing complete state"""

    def __init__(self):
        # Tree structure
        self.root: Optional[PaneNode] = None
        self.pane_registry: dict[PaneId, LeafNode] = {}
        self.node_registry: dict[NodeId, PaneNode] = {}

        # Active state
        self.focused_pane_id: Optional[PaneId] = None
        self.selected_panes: set[PaneId] = set()
        self.locked_panes: set[PaneId] = set()

        # Constraints and configuration
        self.size_constraints: dict[PaneId, SizeConstraints] = {}
        self.global_constraints = GlobalConstraints()

        # Session metadata
        self.metadata: dict[str, Any] = {}
        self.modification_count: int = 0
        self.last_modified: float = time.time()

        # Abstract signals (no Qt dependency)
        self.signals = ModelSignals()

        # Validation
        self.validator = TreeValidator()
        self.validation_mode = ValidationMode.STRICT

    def generate_pane_id(self) -> PaneId:
        """Generate unique, stable pane identifier"""
        timestamp = int(time.time() * 1000000)  # microseconds
        random_part = random.randint(1000, 9999)
        return PaneId(f"pane-{timestamp}-{random_part}")

    def generate_node_id(self) -> NodeId:
        """Generate unique node identifier"""
        return NodeId(f"node-{uuid.uuid4().hex[:8]}")

    def validate_complete_state(self) -> ValidationResult:
        """Comprehensive state validation"""
        errors = []

        # Tree structure validation
        if self.root:
            tree_result = self.validator.validate_tree(self.root)
            errors.extend(tree_result.errors)

        # Registry consistency
        registry_result = self._validate_registries()
        errors.extend(registry_result.errors)

        # Focus state
        focus_result = self._validate_focus_state()
        errors.extend(focus_result.errors)

        return ValidationResult(len(errors) == 0, errors)
```

---

## Visitor Pattern Implementation

### Base Visitor Interface

```python
class NodeVisitor(ABC):
    """Abstract visitor for tree operations"""

    @abstractmethod
    def visit_leaf(self, node: LeafNode) -> Any:
        """Process leaf node"""

    @abstractmethod
    def visit_split(self, node: SplitNode) -> Any:
        """Process split node"""

    def visit_children(self, split: SplitNode) -> list[Any]:
        """Visit all children and collect results"""
        return [child.accept(self) for child in split.children]

class MutableVisitor(NodeVisitor):
    """Visitor that can modify tree structure"""

    def __init__(self, model: PaneModel):
        self.model = model
        self.changes_made = False

    def notify_change(self, node: PaneNode):
        """Record that a change was made"""
        self.changes_made = True
        self.model.modification_count += 1
        self.model.last_modified = time.time()
```

### Tree Traversal Visitors

```python
class DepthFirstVisitor(NodeVisitor):
    """Depth-first tree traversal"""

    def __init__(self, order: TraversalOrder = TraversalOrder.PRE_ORDER):
        self.order = order
        self.results: list[Any] = []

    def visit_leaf(self, node: LeafNode) -> Any:
        result = self.process_leaf(node)
        if self.order != TraversalOrder.POST_ORDER:
            self.results.append(result)
        return result

    def visit_split(self, node: SplitNode) -> Any:
        if self.order == TraversalOrder.PRE_ORDER:
            result = self.process_split(node)
            self.results.append(result)

        # Visit children
        child_results = self.visit_children(node)

        if self.order == TraversalOrder.POST_ORDER:
            result = self.process_split(node)
            self.results.append(result)

        return result

    @abstractmethod
    def process_leaf(self, node: LeafNode) -> Any:
        """Override to define leaf processing"""

    @abstractmethod
    def process_split(self, node: SplitNode) -> Any:
        """Override to define split processing"""

class PaneCollectorVisitor(DepthFirstVisitor):
    """Collect all pane IDs in traversal order"""

    def process_leaf(self, node: LeafNode) -> PaneId:
        return node.pane_id

    def process_split(self, node: SplitNode) -> None:
        return None  # Splits don't have pane IDs

class TreeStatisticsVisitor(NodeVisitor):
    """Calculate tree statistics"""

    def __init__(self):
        self.pane_count = 0
        self.split_count = 0
        self.max_depth = 0
        self.current_depth = 0

    def visit_leaf(self, node: LeafNode) -> dict:
        self.pane_count += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        return {
            'type': 'leaf',
            'pane_id': node.pane_id,
            'widget_id': node.widget_id,
            'depth': self.current_depth
        }

    def visit_split(self, node: SplitNode) -> dict:
        self.split_count += 1
        self.current_depth += 1

        children_stats = [child.accept(self) for child in node.children]

        self.current_depth -= 1

        return {
            'type': 'split',
            'orientation': node.orientation.value,
            'children_count': len(node.children),
            'depth': self.current_depth,
            'children': children_stats
        }
```

### Search and Query Visitors

```python
class NodeSearchVisitor(NodeVisitor):
    """Search for specific nodes"""

    def __init__(self, predicate: Callable[[PaneNode], bool]):
        self.predicate = predicate
        self.matches: list[PaneNode] = []
        self.path_to_match: dict[PaneNode, list[PaneNode]] = {}
        self.current_path: list[PaneNode] = []

    def visit_leaf(self, node: LeafNode) -> bool:
        self.current_path.append(node)
        if self.predicate(node):
            self.matches.append(node)
            self.path_to_match[node] = self.current_path.copy()
            found = True
        else:
            found = False
        self.current_path.pop()
        return found

    def visit_split(self, node: SplitNode) -> bool:
        self.current_path.append(node)

        if self.predicate(node):
            self.matches.append(node)
            self.path_to_match[node] = self.current_path.copy()
            found = True
        else:
            found = False

        # Continue searching children
        for child in node.children:
            if child.accept(self):
                found = True

        self.current_path.pop()
        return found

class PanePathVisitor(NodeVisitor):
    """Find path from root to specific pane"""

    def __init__(self, target_pane_id: PaneId):
        self.target_pane_id = target_pane_id
        self.path: Optional[list[PaneNode]] = None
        self.current_path: list[PaneNode] = []

    def visit_leaf(self, node: LeafNode) -> bool:
        self.current_path.append(node)
        if node.pane_id == self.target_pane_id:
            self.path = self.current_path.copy()
            return True
        self.current_path.pop()
        return False

    def visit_split(self, node: SplitNode) -> bool:
        self.current_path.append(node)

        for child in node.children:
            if child.accept(self):
                return True  # Found in subtree

        self.current_path.pop()
        return False
```

---

## State Validation

### Comprehensive Validation System

```python
class TreeValidator:
    """Validates tree structure and state"""

    def __init__(self, mode: ValidationMode = ValidationMode.STRICT):
        self.mode = mode
        self.validators = [
            self._validate_tree_structure,
            self._validate_pane_uniqueness,
            self._validate_ratios,
            self._validate_orientation_consistency,
            self._validate_depth_limits
        ]

    def validate_tree(self, root: PaneNode) -> ValidationResult:
        """Run all tree validations"""
        errors = []

        for validator in self.validators:
            try:
                result = validator(root)
                if not result.is_valid:
                    errors.extend(result.errors)
            except Exception as e:
                errors.append(f"Validator {validator.__name__} failed: {e}")

        return ValidationResult(len(errors) == 0, errors)

    def _validate_tree_structure(self, root: PaneNode) -> ValidationResult:
        """Validate basic tree properties"""
        errors = []
        visited = set()

        def check_node(node: PaneNode, parent: Optional[SplitNode] = None) -> bool:
            # Check for cycles
            if id(node) in visited:
                errors.append(f"Cycle detected at node {node.node_id}")
                return False
            visited.add(id(node))

            # Validate node state
            try:
                node_result = node.validate_constraints()
                if not node_result.is_valid:
                    errors.extend([f"Node {node.node_id}: {e}"
                                 for e in node_result.errors])
            except Exception as e:
                errors.append(f"Node {node.node_id} validation failed: {e}")

            # Recurse for splits
            if isinstance(node, SplitNode):
                if len(node.children) < 2:
                    errors.append(f"Split {node.node_id} has < 2 children")

                for child in node.children:
                    if not check_node(child, node):
                        return False

            return True

        check_node(root)
        return ValidationResult(len(errors) == 0, errors)

    def _validate_pane_uniqueness(self, root: PaneNode) -> ValidationResult:
        """Ensure all pane IDs are unique"""
        errors = []
        pane_ids = set()

        def collect_panes(node: PaneNode):
            if isinstance(node, LeafNode):
                if node.pane_id in pane_ids:
                    errors.append(f"Duplicate pane ID: {node.pane_id}")
                pane_ids.add(node.pane_id)
            elif isinstance(node, SplitNode):
                for child in node.children:
                    collect_panes(child)

        collect_panes(root)
        return ValidationResult(len(errors) == 0, errors)

    def _validate_ratios(self, root: PaneNode) -> ValidationResult:
        """Validate split ratios"""
        errors = []

        def check_ratios(node: PaneNode):
            if isinstance(node, SplitNode):
                # Check ratio count
                if len(node.ratios) != len(node.children):
                    errors.append(f"Split {node.node_id}: ratio count mismatch")

                # Check ratio sum
                ratio_sum = sum(node.ratios)
                if abs(ratio_sum - 1.0) > 0.001:
                    errors.append(f"Split {node.node_id}: ratios sum to {ratio_sum}")

                # Check individual ratios
                for i, ratio in enumerate(node.ratios):
                    if ratio <= 0 or ratio >= 1:
                        errors.append(f"Split {node.node_id}: invalid ratio[{i}] = {ratio}")

                # Recurse
                for child in node.children:
                    check_ratios(child)

        check_ratios(root)
        return ValidationResult(len(errors) == 0, errors)

class StateValidator:
    """Validate complete model state"""

    def validate_model_consistency(self, model: PaneModel) -> ValidationResult:
        """Check model-level consistency"""
        errors = []

        # Registry consistency
        if model.root:
            tree_panes = self._collect_tree_panes(model.root)
            registry_panes = set(model.pane_registry.keys())

            if tree_panes != registry_panes:
                missing_in_tree = registry_panes - tree_panes
                missing_in_registry = tree_panes - registry_panes

                if missing_in_tree:
                    errors.append(f"Panes in registry but not tree: {missing_in_tree}")
                if missing_in_registry:
                    errors.append(f"Panes in tree but not registry: {missing_in_registry}")

        # Focus state validation
        if model.focused_pane_id:
            if model.focused_pane_id not in model.pane_registry:
                errors.append(f"Focused pane {model.focused_pane_id} not in registry")

        # Selection state validation
        invalid_selections = model.selected_panes - set(model.pane_registry.keys())
        if invalid_selections:
            errors.append(f"Invalid selected panes: {invalid_selections}")

        return ValidationResult(len(errors) == 0, errors)
```

---

## Signal Architecture

### Abstract Signal System

```python
class AbstractSignal:
    """Pure Python signal implementation"""

    def __init__(self):
        self._callbacks: list[Callable] = []
        self._enabled = True

    def connect(self, callback: Callable):
        """Connect callback to signal"""
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def disconnect(self, callback: Callable = None):
        """Disconnect callback or all callbacks"""
        if callback is None:
            self._callbacks.clear()
        elif callback in self._callbacks:
            self._callbacks.remove(callback)

    def emit(self, *args, **kwargs):
        """Emit signal to all connected callbacks"""
        if not self._enabled:
            return

        for callback in self._callbacks.copy():  # Copy to allow modifications
            try:
                callback(*args, **kwargs)
            except Exception as e:
                # Log error but continue with other callbacks
                print(f"Signal callback error: {e}")

    def block(self):
        """Temporarily block signal emission"""
        self._enabled = False

    def unblock(self):
        """Re-enable signal emission"""
        self._enabled = True

class ModelSignals:
    """All model signals in one container"""

    def __init__(self):
        # Structural changes
        self.about_to_change = AbstractSignal()      # Before any mutation
        self.changed = AbstractSignal()              # After mutation complete
        self.structure_changed = AbstractSignal()    # Tree modified
        self.node_added = AbstractSignal()           # Node(s) added
        self.node_removed = AbstractSignal()         # Node(s) removed
        self.node_modified = AbstractSignal()        # Node properties changed

        # State changes
        self.focus_changed = AbstractSignal()        # Focus moved
        self.selection_changed = AbstractSignal()    # Selection updated
        self.constraint_changed = AbstractSignal()   # Size constraints changed

        # Error states
        self.validation_failed = AbstractSignal()    # Validation error
        self.corruption_detected = AbstractSignal()  # State corruption

        # Lifecycle
        self.model_reset = AbstractSignal()          # Complete reset
        self.loading_started = AbstractSignal()      # Restore in progress
        self.loading_complete = AbstractSignal()     # Restore finished

    def block_all(self):
        """Block all signals"""
        for signal in self.__dict__.values():
            if isinstance(signal, AbstractSignal):
                signal.block()

    def unblock_all(self):
        """Unblock all signals"""
        for signal in self.__dict__.values():
            if isinstance(signal, AbstractSignal):
                signal.unblock()
```

---

## Serialization System

### Model Persistence

```python
class ModelSerializer:
    """Handle model save/restore operations"""

    CURRENT_VERSION = 1

    def save_model(self, model: PaneModel) -> dict:
        """Serialize complete model to dict"""
        return {
            'version': self.CURRENT_VERSION,
            'root': self._serialize_node(model.root) if model.root else None,
            'focused_pane_id': model.focused_pane_id,
            'selected_panes': list(model.selected_panes),
            'locked_panes': list(model.locked_panes),
            'size_constraints': self._serialize_constraints(model.size_constraints),
            'global_constraints': self._serialize_global_constraints(model.global_constraints),
            'metadata': model.metadata.copy(),
            'modification_count': model.modification_count,
            'last_modified': model.last_modified
        }

    def restore_model(self, model: PaneModel, data: dict) -> bool:
        """Restore model from serialized data"""
        try:
            # Validate format
            if 'version' not in data:
                raise ValueError("Missing version field")

            version = data['version']
            if version > self.CURRENT_VERSION:
                raise ValueError(f"Unsupported version: {version}")

            # Clear current state
            model.root = None
            model.pane_registry.clear()
            model.node_registry.clear()

            # Restore tree structure
            if data.get('root'):
                model.root = self._deserialize_node(data['root'])
                self._rebuild_registries(model)

            # Restore state
            model.focused_pane_id = data.get('focused_pane_id')
            model.selected_panes = set(data.get('selected_panes', []))
            model.locked_panes = set(data.get('locked_panes', []))
            model.metadata = data.get('metadata', {}).copy()
            model.modification_count = data.get('modification_count', 0)
            model.last_modified = data.get('last_modified', time.time())

            # Validate restored state
            validation = model.validate_complete_state()
            if not validation.is_valid:
                raise ValueError(f"Restored state is invalid: {validation.errors}")

            return True

        except Exception as e:
            # Reset to clean state on failure
            model.reset()
            raise ValueError(f"Model restore failed: {e}")

    def _serialize_node(self, node: PaneNode) -> dict:
        """Serialize a single node"""
        base_data = {
            'node_id': node.node_id,
            'metadata': node.metadata.copy(),
            'created_at': node.created_at
        }

        if isinstance(node, LeafNode):
            base_data.update({
                'type': 'leaf',
                'pane_id': node.pane_id,
                'widget_id': node.widget_id,
                'focus_order_hint': node.focus_order_hint
            })
        elif isinstance(node, SplitNode):
            base_data.update({
                'type': 'split',
                'orientation': node.orientation.value,
                'ratios': node.ratios,
                'children': [self._serialize_node(child) for child in node.children]
            })

        return base_data

    def _deserialize_node(self, data: dict) -> PaneNode:
        """Deserialize a single node"""
        node_type = data.get('type')

        if node_type == 'leaf':
            node = LeafNode(
                NodeId(data['node_id']),
                PaneId(data['pane_id']),
                WidgetId(data['widget_id'])
            )
            node.focus_order_hint = data.get('focus_order_hint')

        elif node_type == 'split':
            children = [self._deserialize_node(child) for child in data['children']]
            node = SplitNode(
                NodeId(data['node_id']),
                Orientation(data['orientation']),
                children,
                data['ratios']
            )
        else:
            raise ValueError(f"Unknown node type: {node_type}")

        # Restore base properties
        node.metadata = data.get('metadata', {}).copy()
        node.created_at = data.get('created_at', time.time())

        return node
```

---

## Thread Safety Design

### Threading Model

```python
import threading
from typing import Any, Callable
from contextlib import contextmanager

class ThreadSafeModel:
    """Thread-safe wrapper for PaneModel"""

    def __init__(self):
        self._model = PaneModel()
        self._lock = threading.RLock()  # Reentrant lock
        self._read_count = 0
        self._write_lock = threading.Lock()

    @contextmanager
    def read_lock(self):
        """Acquire read lock for concurrent reads"""
        with self._lock:
            self._read_count += 1
        try:
            yield self._model
        finally:
            with self._lock:
                self._read_count -= 1

    @contextmanager
    def write_lock(self):
        """Acquire exclusive write lock"""
        self._write_lock.acquire()
        # Wait for all readers to finish
        while True:
            with self._lock:
                if self._read_count == 0:
                    break
            time.sleep(0.001)
        try:
            yield self._model
        finally:
            self._write_lock.release()

    def execute_command(self, command: Command) -> CommandResult:
        """Thread-safe command execution"""
        with self.write_lock() as model:
            return command.execute(model)
```

### Concurrent Access Patterns

```python
class AsyncModelProxy:
    """Async-safe model access"""

    def __init__(self, model: ThreadSafeModel):
        self.model = model
        self._pending_commands = asyncio.Queue()
        self._executor = ThreadPoolExecutor(max_workers=1)

    async def read_tree(self) -> Optional[PaneNode]:
        """Async read operation"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self._read_tree_sync
        )

    def _read_tree_sync(self) -> Optional[PaneNode]:
        with self.model.read_lock() as m:
            return self._deep_copy_tree(m.root)

    async def queue_command(self, command: Command):
        """Queue command for sequential execution"""
        await self._pending_commands.put(command)

    async def process_commands(self):
        """Process command queue sequentially"""
        while True:
            command = await self._pending_commands.get()
            await self._execute_command_async(command)
```

---

## Serialization & Versioning

### Schema Versioning Strategy

```python
class ModelSerializer:
    """Enhanced serializer with versioning"""

    CURRENT_VERSION = "2.0.0"
    MIN_COMPATIBLE_VERSION = "1.0.0"

    def serialize(self, model: PaneModel) -> dict:
        """Serialize with version and metadata"""
        return {
            'version': self.CURRENT_VERSION,
            'created_at': time.time(),
            'metadata': {
                'pane_count': len(model.pane_registry),
                'tree_depth': self._calculate_depth(model.root),
                'application': 'MultiSplit'
            },
            'model': self._serialize_model_v2(model),
            'checksum': self._calculate_checksum(model)
        }

    def deserialize(self, data: dict) -> PaneModel:
        """Deserialize with migration support"""
        version = data.get('version', '1.0.0')

        if not self._is_compatible(version):
            raise IncompatibleVersionError(f"Version {version} not supported")

        # Migrate if needed
        if version < self.CURRENT_VERSION:
            data = self._migrate_data(data, version)

        # Verify checksum
        if 'checksum' in data:
            if not self._verify_checksum(data):
                raise CorruptedDataError("Checksum verification failed")

        return self._deserialize_model_v2(data['model'])

    def _migrate_data(self, data: dict, from_version: str) -> dict:
        """Migrate data from older versions"""
        migrations = {
            '1.0.0': self._migrate_v1_to_v2,
            '1.5.0': self._migrate_v15_to_v2,
        }

        current_version = from_version
        while current_version < self.CURRENT_VERSION:
            if current_version in migrations:
                data = migrations[current_version](data)
                current_version = data['version']
            else:
                break

        return data
```

### Widget State Persistence

```python
class WidgetStateManager:
    """Manages widget state serialization"""

    def save_widget_states(self, model: PaneModel,
                          provider: WidgetProvider) -> dict:
        """Save all widget states"""
        states = {}
        for pane_id, leaf in model.pane_registry.items():
            widget = provider.get_widget(leaf.widget_id)
            if widget and hasattr(widget, 'save_state'):
                states[pane_id] = {
                    'widget_id': leaf.widget_id,
                    'state': widget.save_state(),
                    'timestamp': time.time()
                }
        return states

    def restore_widget_states(self, model: PaneModel,
                            provider: WidgetProvider,
                            states: dict):
        """Restore widget states"""
        for pane_id, state_data in states.items():
            if pane_id in model.pane_registry:
                leaf = model.pane_registry[pane_id]
                widget = provider.get_widget(leaf.widget_id)
                if widget and hasattr(widget, 'restore_state'):
                    widget.restore_state(state_data['state'])
```

---

## Registry Management

### Efficient Registry Operations

```python
class RegistryManager:
    """Optimized registry management"""

    def __init__(self):
        self.pane_index: dict[PaneId, LeafNode] = {}
        self.node_index: dict[NodeId, PaneNode] = {}
        self.parent_index: dict[NodeId, NodeId] = {}
        self.depth_index: dict[NodeId, int] = {}

    def rebuild_indices(self, root: Optional[PaneNode]):
        """Rebuild all indices in single pass"""
        self.clear_indices()
        if root:
            self._index_tree(root, None, 0)

    def _index_tree(self, node: PaneNode,
                   parent_id: Optional[NodeId],
                   depth: int):
        """Recursively index tree"""
        self.node_index[node.node_id] = node
        self.depth_index[node.node_id] = depth

        if parent_id:
            self.parent_index[node.node_id] = parent_id

        if isinstance(node, LeafNode):
            self.pane_index[node.pane_id] = node
        elif isinstance(node, SplitNode):
            for child in node.children:
                self._index_tree(child, node.node_id, depth + 1)

    def find_ancestors(self, node_id: NodeId) -> list[NodeId]:
        """Find all ancestors efficiently"""
        ancestors = []
        current = self.parent_index.get(node_id)
        while current:
            ancestors.append(current)
            current = self.parent_index.get(current)
        return ancestors
```

### Cycle Detection Algorithm

```python
class CycleDetector:
    """Efficient cycle detection using DFS"""

    def has_cycle(self, root: PaneNode) -> bool:
        """Check for cycles in tree"""
        visited = set()
        rec_stack = set()

        return self._dfs_cycle_check(root, visited, rec_stack)

    def _dfs_cycle_check(self, node: PaneNode,
                        visited: set[NodeId],
                        rec_stack: set[NodeId]) -> bool:
        """DFS-based cycle detection"""
        if node.node_id in rec_stack:
            return True  # Cycle detected

        if node.node_id in visited:
            return False  # Already processed

        visited.add(node.node_id)
        rec_stack.add(node.node_id)

        if isinstance(node, SplitNode):
            for child in node.children:
                if self._dfs_cycle_check(child, visited, rec_stack):
                    return True

        rec_stack.remove(node.node_id)
        return False
```

---

## Performance Optimization

### Complexity Analysis

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| Find Pane | O(1) | O(n) |
| Add Pane | O(log n) | O(1) |
| Remove Pane | O(log n) | O(1) |
| Validate Tree | O(n) | O(h) |
| Serialize | O(n) | O(n) |
| Find Ancestors | O(h) | O(h) |
| Cycle Detection | O(n) | O(n) |
| Registry Rebuild | O(n) | O(n) |

Where: n = number of nodes, h = tree height

### Memory Management

```python
class MemoryEfficientModel:
    """Memory-optimized model implementation"""

    __slots__ = ['root', 'pane_registry', 'node_registry',
                 'focused_pane_id', '_weak_refs']

    def __init__(self):
        self.root = None
        self.pane_registry = {}
        self.node_registry = weakref.WeakValueDictionary()
        self.focused_pane_id = None
        self._weak_refs = []

    def compress_metadata(self):
        """Compress rarely-used metadata"""
        for node in self.node_registry.values():
            if hasattr(node, 'metadata') and node.metadata:
                # Only keep essential metadata
                essential = {k: v for k, v in node.metadata.items()
                           if k in ['created_at', 'locked', 'constraints']}
                node.metadata = essential
```

---

## Common Pitfalls

### ❌ Direct Tree Mutation
```python
# DON'T: Modify tree directly
model.root.children.append(new_node)
split.ratios[0] = 0.6
leaf.widget_id = "new-widget"

# DO: Use immutable operations
new_children = split.children + [new_node]
new_split = SplitNode(split.node_id, split.orientation, new_children, new_ratios)
```

### ❌ Qt Dependencies in Model
```python
# DON'T: Import Qt in model
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QObject

# DO: Keep model pure Python
from typing import Protocol
from abc import ABC, abstractmethod
```

### ❌ Skipping Validation
```python
# DON'T: Assume state is valid
split.ratios = [0.3, 0.3]  # Invalid sum!
model.root = corrupted_tree

# DO: Validate before using
result = model.validate_complete_state()
if not result.is_valid:
    raise InvalidStateError(result.errors)
```

### ❌ Registry Inconsistency
```python
# DON'T: Update tree without registry
model.root = new_tree
# Registry now inconsistent!

# DO: Update both together
model.root = new_tree
model._rebuild_registries()
```

### ❌ Signal Ordering Violations
```python
# DON'T: Emit signals in wrong order
model.changed.emit()
# Mutation happens here
model.about_to_change.emit()  # Too late!

# DO: Follow strict signal order
model.about_to_change.emit()
# Mutation happens
model.changed.emit()
```

---

## Quick Reference

### Node Types
| Type | Purpose | Key Properties |
|------|---------|---------------|
| `LeafNode` | Widget container | `pane_id`, `widget_id` |
| `SplitNode` | Layout container | `orientation`, `children`, `ratios` |

### Visitor Patterns
| Visitor | Use Case | Returns |
|---------|----------|---------|
| `PaneCollectorVisitor` | Get all pane IDs | `list[PaneId]` |
| `TreeStatisticsVisitor` | Calculate tree stats | `dict` |
| `NodeSearchVisitor` | Find matching nodes | `list[PaneNode]` |
| `PanePathVisitor` | Path to specific pane | `list[PaneNode]` |

### Signal Categories
| Category | Signals | Purpose |
|----------|---------|---------|
| Structure | `structure_changed`, `node_added` | Tree modifications |
| State | `focus_changed`, `selection_changed` | Active state |
| Validation | `validation_failed`, `corruption_detected` | Error conditions |

### Validation Checks
| Check | Purpose | Failure Condition |
|-------|---------|-------------------|
| Tree Structure | Basic tree integrity | Cycles, invalid nodes |
| Pane Uniqueness | No duplicate IDs | Same pane ID in multiple leaves |
| Ratio Validation | Valid split ratios | Ratios don't sum to 1.0 |
| Registry Consistency | Tree matches registry | Missing or extra entries |

### State Properties
| Property | Type | Purpose |
|----------|------|---------|
| `focused_pane_id` | `Optional[PaneId]` | Currently focused pane |
| `selected_panes` | `set[PaneId]` | Multi-selection state |
| `locked_panes` | `set[PaneId]` | Panes locked from modification |
| `size_constraints` | `dict[PaneId, SizeConstraints]` | Per-pane size limits |

---

## Validation Checklist

- ✅ All tree mutations preserve invariants
- ✅ Registry stays synchronized with tree
- ✅ Ratios sum to 1.0 (±0.001 tolerance)
- ✅ No cycles in tree structure
- ✅ All pane IDs are unique
- ✅ Focused pane exists in tree
- ✅ Selected panes exist in tree
- ✅ Node validation passes for all nodes
- ✅ Signal order is maintained
- ✅ No Qt imports in model code

## Related Documents

- **[Controller Design](controller-design.md)** - Command execution and transactions
- **[View Design](view-design.md)** - Reconciliation and rendering
- **[Focus Management](focus-management.md)** - Focus tracking algorithms
- **[MVC Architecture](../02-architecture/mvc-architecture.md)** - Layer boundaries
- **[Tree Structure](../02-architecture/tree-structure.md)** - Tree fundamentals
- **[MVP Plan](../03-implementation/mvp-plan.md)** - Phase 0 foundations
- **[Widget Provider](../02-architecture/widget-provider.md)** - Provider protocol
- **[Development Rules](../03-implementation/development-rules.md)** - MVC validation

---

The model design provides a solid foundation for MultiSplit's data integrity and serves as the single source of truth for all tree state and operations.