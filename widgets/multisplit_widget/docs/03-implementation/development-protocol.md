# Development Protocol

## Overview

This document defines the **Write → Document → Execute** development workflow for the MultiSplit widget. It provides concrete templates, validation procedures, and best practices for creating implementable tasks that maintain architectural integrity.

## What This Covers

- **Three-phase development workflow** with clear handoff points
- **Task creation templates** with validation requirements
- **Agent communication protocols** for implementation
- **Quality assurance procedures** at each phase
- **Common patterns and examples** for effective task creation

## What This Doesn't Cover

- Individual coding standards (covered in [development-rules.md](development-rules.md))
- Architecture decisions (covered in [02-architecture/](../02-architecture/))
- Specific implementation details (covered in [mvp-plan.md](mvp-plan.md))

---

## Core Development Workflow

### The Three-Phase Protocol

```
1. WRITE     → Create comprehensive documentation/specifications
2. DOCUMENT  → Break down into detailed, atomic tasks
3. EXECUTE   → Agent implements tasks following rules
```

Each phase has specific inputs, outputs, and validation criteria to ensure quality and consistency.

---

## Phase 1: WRITE - Documentation First

**Responsibility**: Human architects and designers
**Goal**: Define WHAT to build with complete clarity

### Inputs
- Requirements and user stories
- Architecture decisions
- Technical constraints
- Integration requirements

### Process
1. **Write architectural documents**
   - Design decisions with rationale
   - Component relationships and dependencies
   - Data flow diagrams and interaction patterns
   - Interface specifications and contracts

2. **Define all contracts**
   - Protocols and abstract interfaces
   - Type definitions and validation rules
   - Signal contracts and event flows
   - Command structures and patterns

3. **Document patterns**
   - Usage patterns and examples
   - Integration scenarios
   - Error handling strategies
   - Extension points and hooks

### Outputs
- Complete documentation set that defines scope
- Clear architectural boundaries
- All interfaces and contracts specified
- No ambiguity about what needs to be built

### Validation Criteria
- [ ] All components have clear responsibilities
- [ ] No circular dependencies in architecture
- [ ] All interfaces are complete and testable
- [ ] Extension points are identified
- [ ] Integration requirements are specified

---

## Phase 2: DOCUMENT - Task Breakdown

**Responsibility**: Human task creators and project managers
**Goal**: Convert documentation into implementable tasks

### Task Structure Template

```markdown
## Task: [Descriptive Name]

### Context
- **Component**: Which component/layer this affects
- **Dependencies**: Other tasks that must complete first
- **Documentation**: Related documentation sections

### Acceptance Criteria
- [ ] Specific measurable outcome 1
- [ ] Specific measurable outcome 2
- [ ] All tests pass
- [ ] No rule violations
- [ ] Documentation updated

### Implementation Details
- **File to create/modify**: `src/core/model.py`
- **Layer**: Model (no Qt imports allowed)
- **Allowed imports**: `types.py`, `exceptions.py`, `utils.py`
- **Forbidden imports**: Any Qt, view layer, controller layer
- **Required patterns**: Command pattern, visitor pattern

### Code Template
```python
# Provide specific template if complex
from core.types import PaneId
from core.exceptions import InvalidOperationError

class ExampleClass:
    def example_method(self, param: PaneId) -> bool:
        # Implementation here
        pass
```

### Validation Requirements
- [ ] Check no forbidden imports
- [ ] Verify required patterns used
- [ ] Ensure signals emitted in correct order
- [ ] Validate error handling

### Test Requirements
- [ ] Unit tests for all public methods
- [ ] Integration tests for key workflows
- [ ] Error case testing
- [ ] Performance requirements met

### Definition of Done
- [ ] Implementation complete
- [ ] All tests pass
- [ ] Code review approved
- [ ] Documentation updated
- [ ] No rule violations
```

### Task Granularity Rules

1. **One file per task** (preferably)
   - Makes tasks atomic and reviewable
   - Reduces merge conflicts
   - Clear ownership and scope

2. **One concept per task**
   - Example: "implement SplitCommand" not "implement commands"
   - Focused validation and testing
   - Clear success criteria

3. **Completable in one session**
   - Typically 2-4 hours of work
   - Agent can complete without context switching
   - Immediate feedback cycle

4. **Independently testable**
   - Task can be validated in isolation
   - Clear pass/fail criteria
   - Dependencies are explicit

5. **Clear success criteria**
   - Measurable outcomes
   - Specific acceptance criteria
   - No ambiguous requirements

### Task Documentation Requirements

Every task MUST include:

#### Layer Specification
```python
# ✅ REQUIRED
Layer: Model (src/core/)
Constraints: No Qt imports, pure Python only

# ✅ REQUIRED
Layer: Controller (src/controller/)
Constraints: Commands only, no view imports

# ✅ REQUIRED
Layer: View (src/view/)
Constraints: Read-only model access, reconciliation required
```

#### Import Rules
```python
# ✅ ALLOWED IMPORTS
from typing import Optional, List
from core.types import PaneId, WidgetId
from core.exceptions import InvalidOperationError

# ❌ FORBIDDEN IMPORTS
from PySide6.QtWidgets import QWidget  # No Qt in model
from view.container import PaneContainer  # No view in controller
from controller.commands import Command  # No controller in model
```

#### Required Patterns
```python
# ✅ COMMAND PATTERN REQUIRED
class SplitCommand(Command):
    def execute(self, model: PaneModel) -> CommandResult
    def undo(self, model: PaneModel) -> CommandResult

# ✅ VISITOR PATTERN REQUIRED
class TreeOperation:
    def visit_leaf(self, node: LeafNode) -> Any
    def visit_split(self, node: SplitNode) -> Any

# ✅ SIGNAL ORDER REQUIRED
model.signals.about_to_change.emit()
# ... perform mutation ...
model.signals.changed.emit()
```

#### Validation Code Templates

Provide specific validation snippets:
```python
# Validate layer separation
def validate_imports(file_path: str, layer: str) -> bool:
    """Check if file follows import rules for its layer."""
    with open(file_path) as f:
        content = f.read()

    if layer == "model":
        forbidden = ["PySide6", "PyQt", "view.", "controller."]
        for pattern in forbidden:
            if pattern in content:
                return False

    return True

# Validate command pattern
def validate_command_implementation(command_class) -> bool:
    """Check if command follows required pattern."""
    required_methods = ['execute', 'undo', 'validate']
    return all(hasattr(command_class, method) for method in required_methods)
```

---

## Phase 3: EXECUTE - Agent Implementation

**Responsibility**: Specialized implementation agents
**Goal**: Implement tasks following all rules and patterns

### Agent Communication Protocol

#### Task Assignment Template
```markdown
To: multisplit-developer agent

**Task**: [Task name from Phase 2]
**Rules**: Follow development-rules.md strictly
**Context**: [Specific context and background]

**Requirements**:
1. Layer restrictions: [specific layer rules]
2. Import rules: [allowed/forbidden imports]
3. Pattern requirements: [required patterns]
4. Test requirements: [test specifications]

**Validation**:
- Run provided validation code
- Check all acceptance criteria
- Ensure no rule violations

Please implement according to the task specification.
```

#### Agent Response Template
```markdown
**Task**: [Task name]
**Status**: Complete/Failed

**Implementation Summary**:
- Files created/modified: [list]
- Key components implemented: [list]
- Patterns used: [Command, Visitor, etc.]

**Validation Results**:
- [ ] Layer rules followed
- [ ] Import restrictions respected
- [ ] Required patterns implemented
- [ ] All tests pass
- [ ] Acceptance criteria met

**Notes**: [Any important implementation decisions or issues]
```

### Agent Validation Checklist

Before completing any task, agent must verify:

#### Layer-Specific Checks
```python
# Model layer validation
if implementing_in_model_layer:
    ✓ No Qt imports anywhere
    ✓ No controller imports
    ✓ No view imports
    ✓ Pure Python only
    ✓ Abstract signals only

# Controller layer validation
if implementing_in_controller_layer:
    ✓ All mutations via Commands
    ✓ No view imports
    ✓ Proper transaction handling
    ✓ Undo/redo support implemented
    ✓ Signal order correct

# View layer validation
if implementing_in_view_layer:
    ✓ No model mutations
    ✓ Reconciliation not rebuild
    ✓ Atomic updates only
    ✓ Widget reuse maximized
    ✓ Qt imports allowed
```

#### Pattern Validation
```python
# Command pattern validation
if implementing_command:
    ✓ Inherits from Command base class
    ✓ Implements execute() method
    ✓ Implements undo() method
    ✓ Implements validate() method
    ✓ Stores undo data properly

# Visitor pattern validation
if implementing_visitor:
    ✓ Implements visit_leaf() method
    ✓ Implements visit_split() method
    ✓ Used for tree operations
    ✓ No node modification

# Signal pattern validation
if emitting_signals:
    ✓ about_to_change emitted first
    ✓ changed emitted after mutation
    ✓ specific signals emitted last
    ✓ No signals during transactions
```

---

## Task Creation Guidelines

### For Human Task Creators

When creating tasks for the agent:

#### DO: ✅
- **Specify exact file paths** - `src/core/model.py` not "the model file"
- **List allowed/forbidden imports explicitly** - No guessing required
- **Provide code templates when helpful** - Especially for complex patterns
- **Reference specific rules that apply** - Section numbers from development-rules.md
- **Include test requirements** - What must be tested and how
- **Define clear success criteria** - Measurable, binary pass/fail

#### DON'T: ❌
- **Create vague tasks** - "implement the view" is too broad
- **Combine multiple concepts** - Each task should have one clear focus
- **Assume context** - Be explicit about requirements and constraints
- **Skip validation requirements** - Every task needs validation criteria
- **Leave dependencies unclear** - Specify what must be done first

### Task Template Examples

#### Example 1: Model Component
```markdown
## Task: Implement PaneModel Core Structure

### Context
- **Component**: Model layer core (src/core/model.py)
- **Dependencies**: types.py, exceptions.py, utils.py must exist
- **Documentation**: [mvc-architecture.md](../02-architecture/mvc-architecture.md)

### Acceptance Criteria
- [ ] PaneModel class created with all required attributes
- [ ] Tree structure management methods implemented
- [ ] Focus tracking implemented
- [ ] Registry management for fast lookup
- [ ] All signals defined using AbstractSignal
- [ ] No Qt imports anywhere in file

### Implementation Details
- **File to create**: `src/core/model.py`
- **Layer**: Model (NO Qt imports allowed)
- **Allowed imports**:
  ```python
  from typing import Optional, Dict, Set
  from core.types import PaneId, NodeId
  from core.nodes import PaneNode, LeafNode, SplitNode
  from core.signals import ModelSignals
  from core.exceptions import InvalidStructureError, PaneNotFoundError
  ```
- **Forbidden imports**: Any PySide6, PyQt, view, controller modules
- **Required patterns**: Abstract signals, registry pattern

### Code Template
```python
class PaneModel:
    """Core model - pure Python, no Qt dependencies."""

    def __init__(self):
        # Tree structure
        self.root: Optional[PaneNode] = None

        # Focus and selection
        self.focused_pane_id: Optional[PaneId] = None

        # Registries for fast lookup
        self.pane_registry: Dict[PaneId, PaneNode] = {}

        # Signals (abstract, not Qt)
        self.signals = ModelSignals()

    def find_node(self, pane_id: PaneId) -> Optional[PaneNode]:
        """Find node by pane ID."""
        # Implementation required

    def validate_tree(self) -> bool:
        """Validate tree structure."""
        # Implementation required
```

### Validation Requirements
```python
# Check no Qt imports
def validate_model_imports():
    with open('src/core/model.py') as f:
        content = f.read()
    forbidden = ['PySide6', 'PyQt', 'QWidget', 'QObject']
    return not any(pattern in content for pattern in forbidden)

# Check required methods exist
def validate_model_interface():
    from core.model import PaneModel
    required_methods = ['find_node', 'validate_tree', 'get_statistics']
    return all(hasattr(PaneModel, method) for method in required_methods)
```

### Test Requirements
- [ ] Unit tests for all public methods
- [ ] Test tree manipulation operations
- [ ] Test signal emission
- [ ] Test registry consistency
- [ ] Tests must run without Qt imports

### Definition of Done
- [ ] PaneModel class fully implemented
- [ ] All acceptance criteria met
- [ ] Import validation passes
- [ ] All tests pass
- [ ] No pylint/ruff errors
```

#### Example 2: Controller Component
```markdown
## Task: Implement SplitCommand

### Context
- **Component**: Controller layer (src/controller/commands/split_command.py)
- **Dependencies**: Command base class, model types, tree utilities
- **Documentation**: [mvp-plan.md](mvp-plan.md#split-command)

### Acceptance Criteria
- [ ] SplitCommand class inherits from Command
- [ ] Implements all required abstract methods
- [ ] Validates split operation preconditions
- [ ] Performs split with proper signal order
- [ ] Stores complete undo data
- [ ] Undo perfectly reverses execute

### Implementation Details
- **File to create**: `src/controller/commands/split_command.py`
- **Layer**: Controller (command pattern only)
- **Allowed imports**:
  ```python
  from core.types import PaneId, WidgetId, WherePosition, Orientation
  from core.model import PaneModel
  from core.nodes import LeafNode, SplitNode
  from core.utils import generate_pane_id, generate_node_id
  from controller.commands.base import Command, CommandResult
  ```
- **Forbidden imports**: No view imports, no Qt imports
- **Required patterns**: Command pattern with undo support

### Validation Requirements
```python
# Validate command interface
def validate_split_command():
    from controller.commands.split_command import SplitCommand
    cmd = SplitCommand(pane_id, where, widget_id)
    required = ['validate', 'execute', 'undo', 'redo']
    return all(hasattr(cmd, method) for method in required)

# Test undo/redo roundtrip
def test_split_undo_roundtrip():
    # Setup initial state
    # Execute split
    # Execute undo
    # Verify state is identical to initial
```

### Test Requirements
- [ ] Test split in all directions (left, right, top, bottom)
- [ ] Test validation rejects invalid operations
- [ ] Test undo restores exact previous state
- [ ] Test redo works after undo
- [ ] Test signal emission order

### Definition of Done
- [ ] SplitCommand fully implemented
- [ ] All command pattern methods working
- [ ] Undo/redo tested and working
- [ ] Validation comprehensive
- [ ] Integration with model tested
```

#### Example 3: View Component
```markdown
## Task: Implement Basic Reconciliation

### Context
- **Component**: View layer (src/view/container.py)
- **Dependencies**: TreeReconciler, GeometryCalculator, Qt widgets
- **Documentation**: [mvp-plan.md](mvp-plan.md#basic-container)

### Acceptance Criteria
- [ ] PaneContainer class created inheriting QWidget
- [ ] Reconciliation algorithm implemented
- [ ] No widget rebuild, only minimal changes
- [ ] Atomic updates with setUpdatesEnabled
- [ ] Widget provider integration working
- [ ] Geometry calculation and layout

### Implementation Details
- **File to create**: `src/view/container.py`
- **Layer**: View (Qt allowed, read-only model access)
- **Allowed imports**:
  ```python
  from PySide6.QtWidgets import QWidget, QVBoxLayout
  from PySide6.QtCore import Signal
  from core.model import PaneModel
  from controller.controller import PaneController
  from view.tree_reconciler import TreeReconciler
  from view.geometry import GeometryCalculator
  ```
- **Forbidden imports**: No controller mutations, no model mutations
- **Required patterns**: Reconciliation, atomic updates, provider pattern

### Validation Requirements
```python
# Validate no model mutation
def validate_view_readonly():
    # Check that view never calls model mutation methods
    # Only reads from model, calls controller for changes

# Validate reconciliation efficiency
def validate_reconciliation():
    # Test that minimal widgets are recreated
    # Measure widget reuse percentage
```

### Test Requirements
- [ ] Test reconciliation preserves existing widgets
- [ ] Test atomic updates prevent flicker
- [ ] Test widget provider integration
- [ ] Test geometry calculation accuracy
- [ ] Performance test for large trees

### Definition of Done
- [ ] Container handles all model changes via reconciliation
- [ ] No widgets unnecessarily recreated
- [ ] Updates are flicker-free
- [ ] Widget provider properly integrated
- [ ] All tests pass
```

---

## Validation Procedures

### Task Quality Checklist

Before assigning a task to an agent:

#### Requirements Clarity
- [ ] Task has single, clear focus
- [ ] Success criteria are measurable
- [ ] All dependencies are explicit
- [ ] Layer constraints are specified
- [ ] Import rules are complete

#### Implementation Guidance
- [ ] File paths are exact
- [ ] Code templates provided if needed
- [ ] Patterns and interfaces specified
- [ ] Error handling requirements clear
- [ ] Performance requirements stated

#### Validation Completeness
- [ ] Validation code provided
- [ ] Test requirements comprehensive
- [ ] Integration testing specified
- [ ] Rule compliance checked
- [ ] Definition of done is clear

### Agent Output Validation

After agent completes a task:

#### Code Quality Checks
```python
# Automated validation script
def validate_task_completion(task_spec, implementation):
    checks = []

    # Layer compliance
    checks.append(validate_layer_rules(implementation, task_spec.layer))

    # Import restrictions
    checks.append(validate_imports(implementation, task_spec.allowed_imports))

    # Pattern usage
    checks.append(validate_patterns(implementation, task_spec.required_patterns))

    # Test coverage
    checks.append(validate_test_coverage(implementation, task_spec.test_requirements))

    return all(checks)
```

#### Manual Review Points
- [ ] Architecture principles followed
- [ ] Code is maintainable and extensible
- [ ] Error handling is appropriate
- [ ] Documentation is updated
- [ ] Integration points work correctly

---

## Common Patterns and Templates

### Signal Implementation Pattern
```python
# Model signals (abstract)
class ModelSignals:
    def __init__(self):
        self.about_to_change = AbstractSignal()
        self.changed = AbstractSignal()
        self.structure_changed = AbstractSignal()

# Signal order in commands
def execute(self, model):
    model.signals.about_to_change.emit()
    # ... perform mutation ...
    model.signals.changed.emit()
    model.signals.structure_changed.emit()
```

### Command Implementation Pattern
```python
class ExampleCommand(Command):
    def __init__(self, ...):
        # Store parameters
        self.undo_data = None

    def validate(self, model: PaneModel) -> bool:
        # Check preconditions
        pass

    def execute(self, model: PaneModel) -> CommandResult:
        # Store undo data
        self.undo_data = self._capture_state(model)

        # Emit signals in order
        model.signals.about_to_change.emit()

        # Perform mutation
        result = self._perform_operation(model)

        # Emit completion signals
        model.signals.changed.emit()

        return result

    def undo(self, model: PaneModel) -> CommandResult:
        # Restore from undo_data
        pass
```

### Reconciliation Pattern
```python
def reconcile_changes(self):
    old_tree = self.current_tree
    new_tree = self.model.root

    # Calculate minimal diff
    diff = self.reconciler.diff_trees(old_tree, new_tree)

    # Apply changes atomically
    self.setUpdatesEnabled(False)
    try:
        for pane_id in diff.removed:
            self._remove_widget(pane_id)

        for pane_id in diff.added:
            self._add_widget(pane_id)

        for pane_id in diff.modified:
            self._update_widget(pane_id)

        self._update_geometry()
    finally:
        self.setUpdatesEnabled(True)
```

---

## Benefits of This Protocol

### 1. Separation of Concerns
- **Humans focus on**: Architecture, design, requirements
- **Agents focus on**: Implementation details, code generation
- **Clear handoff points**: Documentation → Tasks → Implementation

### 2. Quality Assurance
- **Rules enforced consistently** across all implementations
- **Every task has validation** built into the specification
- **Agents can't violate architecture** due to explicit constraints

### 3. Scalability
- **Multiple agents** can work on different tasks simultaneously
- **Tasks can be parallelized** when dependencies are clear
- **Consistent quality** regardless of which agent implements

### 4. Traceability
- **Every line of code** traces back to a specific task
- **Every task** traces back to documentation and requirements
- **Every decision** is documented and reviewable

---

## Common Pitfalls and Solutions

### Pitfall 1: Vague Task Specifications
**Problem**: Tasks like "implement the view" or "add focus handling"
**Solution**: Break into atomic tasks with single clear focus
**Example**: "Implement PaneContainer.reconcile() method with TreeReconciler"

### Pitfall 2: Missing Layer Specifications
**Problem**: Agent doesn't know which layer rules apply
**Solution**: Always specify layer and import rules explicitly
**Example**: "Layer: Model (NO Qt imports), Layer: View (Qt allowed)"

### Pitfall 3: Insufficient Validation
**Problem**: No way to verify implementation correctness
**Solution**: Provide validation code and comprehensive test requirements
**Example**: Include import checking, pattern validation, integration tests

### Pitfall 4: Unclear Dependencies
**Problem**: Agent can't complete task due to missing dependencies
**Solution**: Explicit dependency list and completion order
**Example**: "Dependencies: types.py, model.py must be complete first"

### Pitfall 5: Missing Success Criteria
**Problem**: No clear definition of when task is complete
**Solution**: Measurable acceptance criteria and definition of done
**Example**: "[ ] Can split pane horizontally [ ] Undo works [ ] Tests pass"

---

## Related Documents

- [Development Rules](development-rules.md) - Critical rules for implementation
- [MVP Plan](mvp-plan.md) - Complete implementation roadmap
- [MVC Architecture](../02-architecture/mvc-architecture.md) - Layer specifications
- [Widget Provider](../02-architecture/widget-provider.md) - Provider pattern details

---

## Quick Reference

### Task Creation Checklist
```
✅ Single clear focus
✅ Layer and import rules specified
✅ Patterns and interfaces defined
✅ Validation code provided
✅ Test requirements complete
✅ Success criteria measurable
✅ Dependencies explicit
```

### Agent Assignment Template
```
Task: [Name]
Layer: [Model/Controller/View + constraints]
Imports: [Allowed list] / [Forbidden list]
Patterns: [Required patterns]
Validation: [Specific checks]
Tests: [Requirements]
Success: [Measurable criteria]
```

### Validation Order
```
1. Layer rules compliance
2. Import restrictions followed
3. Required patterns implemented
4. Tests pass
5. Integration works
6. Documentation updated
```

This protocol ensures that our MultiSplit widget is built with consistent quality, architectural integrity, and maintainability from day one.