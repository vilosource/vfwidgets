# Development Rules

## Overview

This document consolidates all critical development rules from the comprehensive MultiSplit documentation. These rules MUST be followed during implementation to ensure architectural integrity, maintainability, and extensibility. Violations will result in rejected code.

## What This Covers

- **Critical rules** that must never be violated
- **Architectural patterns** required for consistency
- **Layer separation** enforcement mechanisms
- **Validation code** for automated rule checking
- **Common anti-patterns** and how to avoid them

## What This Doesn't Cover

- Implementation details (covered in [mvp-plan.md](mvp-plan.md))
- Task creation workflow (covered in [development-protocol.md](development-protocol.md))
- Architecture rationale (covered in [02-architecture/](../02-architecture/))

---

## 🔴 CRITICAL RULES (Violations = Rejected Code)

### Rule 1: MVC Layer Separation
**Strictest architectural rule - NO exceptions allowed**

```python
# Model Layer
Model:      Pure Python only. NO Qt imports. NO widget references.
            NO controller imports. NO view imports.

# Controller Layer
Controller: Imports Model only. SOLE mutation point.
            ALL changes via Commands. NO view imports.

# View Layer
View:       Read Model. Call Controller. NEVER mutate Model directly.
            Qt imports allowed. Reconciliation required.
```

**Validation Code**:
```python
def validate_layer_separation(file_path: str, layer: str) -> bool:
    """Validate layer follows import rules."""
    with open(file_path) as f:
        content = f.read()

    if layer == "model":
        forbidden = [
            "PySide6", "PyQt", "QtWidgets", "QtCore", "QWidget", "QObject",
            "from view", "import view", "from controller", "import controller"
        ]
        for pattern in forbidden:
            if pattern in content:
                print(f"VIOLATION: Model layer imports {pattern}")
                return False

    elif layer == "controller":
        forbidden = [
            "from view", "import view", "QtWidgets", "QWidget"
        ]
        for pattern in forbidden:
            if pattern in content:
                print(f"VIOLATION: Controller layer imports {pattern}")
                return False

    return True

# Usage in CI/CD
assert validate_layer_separation("src/core/model.py", "model")
assert validate_layer_separation("src/controller/commands.py", "controller")
```

### Rule 2: Widget Provider Pattern
**MultiSplit NEVER creates widgets - Application ALWAYS provides them**

```python
# ✅ CORRECT - MultiSplit requests widgets
self.widget_needed.emit(widget_id, pane_id)

# ✅ CORRECT - Application provides widgets
def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
    return self.create_appropriate_widget(widget_id)

# ❌ FORBIDDEN - MultiSplit creates widgets
widget = QTextEdit()  # NEVER in MultiSplit code
pane.widget = SomeWidget()  # NEVER store widget instances

# ❌ FORBIDDEN - MultiSplit knows widget types
if isinstance(widget, QTextEdit):  # NEVER type-check widgets
```

**Validation Code**:
```python
def validate_no_widget_creation(file_path: str) -> bool:
    """Ensure no widget instantiation in MultiSplit code."""
    with open(file_path) as f:
        content = f.read()

    # Check for widget constructors
    widget_constructors = [
        "QWidget(", "QLabel(", "QTextEdit(", "QPushButton(",
        "QVBoxLayout(", "QHBoxLayout(", "QSplitter("
    ]

    for constructor in widget_constructors:
        if constructor in content:
            print(f"VIOLATION: Widget creation found: {constructor}")
            return False

    # Check for widget type checking
    type_checks = ["isinstance(", "type(", "__class__"]
    widget_types = ["QWidget", "QLabel", "QTextEdit"]

    for check in type_checks:
        if check in content:
            for widget_type in widget_types:
                if widget_type in content:
                    print(f"VIOLATION: Widget type checking found")
                    return False

    return True

# Usage
assert validate_no_widget_creation("src/core/model.py")
assert validate_no_widget_creation("src/controller/commands.py")
```

### Rule 3: No Direct Model Mutation
**ALL mutations must go through Commands - NO exceptions**

```python
# ❌ FORBIDDEN - Direct mutation
model.root.children.append(node)       # Bypasses command pattern
view.model.focused_pane_id = new_id    # View mutating model
widget.some_property = value           # Bypassing controller

# ✅ REQUIRED - Command pattern only
controller.execute(SplitCommand(pane_id, where, widget_id))
controller.execute(FocusCommand(pane_id))
controller.execute(CloseCommand(pane_id))
```

**Validation Code**:
```python
def validate_no_direct_mutation(file_path: str, layer: str) -> bool:
    """Ensure no direct model mutation outside controller."""
    if layer == "view":
        with open(file_path) as f:
            content = f.read()

        # Check for direct model property assignment
        mutation_patterns = [
            "model.root =", "model.focused_pane_id =",
            "model.pane_registry[", "model.constraints[",
            ".children.append(", ".children.remove(",
            ".ratios[", ".ratios ="
        ]

        for pattern in mutation_patterns:
            if pattern in content:
                print(f"VIOLATION: Direct model mutation: {pattern}")
                return False

    return True

def validate_command_pattern_usage(file_path: str) -> bool:
    """Ensure commands are used for all mutations."""
    with open(file_path) as f:
        content = f.read()

    # Look for controller.execute calls
    if "controller.execute(" not in content and "self.execute(" not in content:
        if any(pattern in content for pattern in ["split", "close", "focus", "resize"]):
            print("VIOLATION: Operation found without command pattern")
            return False

    return True
```

### Rule 4: Import Hierarchy
**Strict dependency hierarchy - NO circular imports**

```python
# ✅ ALLOWED DEPENDENCIES (no cycles)
types.py        # No imports from other layers
exceptions.py   # No imports from other layers
nodes.py        # from types, exceptions only
model.py        # from types, exceptions, nodes only
commands.py     # from types, exceptions, nodes, model only
controller.py   # from model, commands only
view.py         # from model (read-only), controller only

# ❌ FORBIDDEN CYCLES
model.py:       from view import ...      # NEVER
controller.py:  from view import ...      # NEVER
commands.py:    from controller import... # NEVER
nodes.py:       from model import ...     # NEVER
```

**Validation Code**:
```python
import ast
import os
from typing import Dict, Set

def validate_import_hierarchy() -> bool:
    """Validate no circular imports in codebase."""

    # Define allowed dependencies
    dependencies = {
        "types": set(),
        "exceptions": set(),
        "utils": {"types", "exceptions"},
        "nodes": {"types", "exceptions", "utils"},
        "model": {"types", "exceptions", "utils", "nodes"},
        "commands": {"types", "exceptions", "utils", "nodes", "model"},
        "controller": {"types", "exceptions", "utils", "nodes", "model", "commands"},
        "view": {"types", "exceptions", "utils", "nodes", "model", "controller"}
    }

    def get_imports(file_path: str) -> Set[str]:
        """Extract module imports from Python file."""
        with open(file_path) as f:
            tree = ast.parse(f.read())

        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])

        return imports

    # Check each module's imports
    for module, allowed in dependencies.items():
        file_path = f"src/core/{module}.py"
        if os.path.exists(file_path):
            actual_imports = get_imports(file_path)

            # Filter to only our modules
            our_modules = actual_imports & set(dependencies.keys())

            if not our_modules.issubset(allowed):
                forbidden = our_modules - allowed
                print(f"VIOLATION: {module} imports forbidden modules: {forbidden}")
                return False

    return True

# Usage in CI/CD
assert validate_import_hierarchy()
```

---

## 📊 ARCHITECTURAL RULES

### Rule 5: Complete Skeleton First
**Define ALL interfaces upfront, implement incrementally**

```python
# ✅ REQUIRED - All methods declared from start
class Command(ABC):
    @abstractmethod
    def execute(self, model: PaneModel) -> CommandResult: pass

    @abstractmethod
    def undo(self, model: PaneModel) -> CommandResult: pass

    @abstractmethod
    def validate(self, model: PaneModel) -> bool: pass

    @abstractmethod
    def serialize(self) -> dict: pass

# ✅ ALLOWED - Incremental implementation
def complex_operation(self):
    raise NotImplementedError("Will implement in Phase 2")

# ❌ FORBIDDEN - Modifying interfaces later
# Adding methods to base classes after initial design
```

**Validation Code**:
```python
def validate_complete_interfaces() -> bool:
    """Ensure all abstract methods are declared."""

    from core.commands import Command
    from core.visitor import NodeVisitor

    # Check Command interface
    required_command_methods = ['execute', 'undo', 'validate', 'serialize']
    for method in required_command_methods:
        if not hasattr(Command, method):
            print(f"VIOLATION: Command missing method: {method}")
            return False

    # Check Visitor interface
    required_visitor_methods = ['visit_leaf', 'visit_split']
    for method in required_visitor_methods:
        if not hasattr(NodeVisitor, method):
            print(f"VIOLATION: NodeVisitor missing method: {method}")
            return False

    return True

def validate_no_interface_modification(git_diff: str) -> bool:
    """Ensure abstract base classes aren't modified after creation."""

    # Check if any ABC classes have new abstract methods
    modified_abcs = ["class Command(ABC)", "class NodeVisitor(Protocol)"]

    for abc_class in modified_abcs:
        if abc_class in git_diff and "@abstractmethod" in git_diff:
            print(f"VIOLATION: Abstract interface modified: {abc_class}")
            return False

    return True
```

### Rule 6: Visitor Pattern for Tree Operations
**New tree operations = new visitor, NOT modified nodes**

```python
# ✅ CORRECT - New operation as visitor
class BoundsCalculator(NodeVisitor):
    def visit_leaf(self, node: LeafNode) -> Bounds:
        return self.calculate_leaf_bounds(node)

    def visit_split(self, node: SplitNode) -> Bounds:
        return self.calculate_split_bounds(node)

# ✅ CORRECT - Using visitor
calculator = BoundsCalculator()
bounds = root_node.accept(calculator)

# ❌ FORBIDDEN - Modifying node classes
class LeafNode(PaneNode):
    def calculate_bounds(self):  # NEVER add operation methods
        pass
```

**Validation Code**:
```python
def validate_visitor_pattern_usage() -> bool:
    """Ensure tree operations use visitor pattern."""

    # Check that node classes don't have operation methods
    node_files = ["src/core/nodes.py"]
    forbidden_methods = [
        "calculate_", "find_", "collect_", "traverse_",
        "search_", "filter_", "transform_"
    ]

    for file_path in node_files:
        with open(file_path) as f:
            content = f.read()

        for method in forbidden_methods:
            if f"def {method}" in content:
                print(f"VIOLATION: Operation method in node class: {method}")
                return False

    return True

def validate_visitor_implementations(visitor_dir: str) -> bool:
    """Ensure all visitors implement required methods."""

    import importlib
    import pkgutil

    # Find all visitor classes
    for _, name, _ in pkgutil.iter_modules([visitor_dir]):
        module = importlib.import_module(f"{visitor_dir.replace('/', '.')}.{name}")

        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and
                hasattr(attr, 'visit_leaf') and
                hasattr(attr, 'visit_split')):

                # Validate visitor implementation
                if not callable(attr.visit_leaf) or not callable(attr.visit_split):
                    print(f"VIOLATION: Invalid visitor implementation: {attr_name}")
                    return False

    return True
```

### Rule 7: Command Pattern for All Mutations
**Every state change must be a Command with undo support**

```python
# ✅ REQUIRED - All mutations via commands
class SplitCommand(Command):
    def __init__(self, pane_id: PaneId, where: WherePosition, widget_id: WidgetId):
        self.pane_id = pane_id
        self.where = where
        self.widget_id = widget_id
        self.undo_data = None  # REQUIRED for undo

    def execute(self, model: PaneModel) -> CommandResult:
        # Store undo data BEFORE mutation
        self.undo_data = self._capture_state(model)

        # Perform mutation
        result = self._perform_split(model)

        return result

    def undo(self, model: PaneModel) -> CommandResult:
        # Restore from undo_data
        return self._restore_state(model, self.undo_data)

# ❌ FORBIDDEN - Direct mutation methods
class PaneModel:
    def split_pane(self, ...):  # NEVER - use SplitCommand
        pass

    def close_pane(self, ...):  # NEVER - use CloseCommand
        pass
```

**Validation Code**:
```python
def validate_command_pattern_complete() -> bool:
    """Ensure all commands implement required methods."""

    import inspect
    from controller.commands.base import Command

    # Find all command classes
    command_classes = []
    for name, obj in inspect.getmembers(sys.modules['controller.commands']):
        if (inspect.isclass(obj) and
            issubclass(obj, Command) and
            obj != Command):
            command_classes.append(obj)

    required_methods = ['execute', 'undo', 'validate', 'serialize']

    for cmd_class in command_classes:
        for method in required_methods:
            if not hasattr(cmd_class, method):
                print(f"VIOLATION: Command {cmd_class.__name__} missing {method}")
                return False

            # Check method isn't just raising NotImplementedError
            method_obj = getattr(cmd_class, method)
            if hasattr(method_obj, '__func__'):
                source = inspect.getsource(method_obj)
                if "NotImplementedError" in source and "TODO" not in source:
                    print(f"WARNING: {cmd_class.__name__}.{method} not implemented")

    return True

def validate_undo_data_storage() -> bool:
    """Ensure commands store undo data."""

    command_files = glob.glob("src/controller/commands/*.py")

    for file_path in command_files:
        with open(file_path) as f:
            content = f.read()

        if "class" in content and "Command" in content:
            if "self.undo_data" not in content:
                print(f"VIOLATION: Command missing undo_data: {file_path}")
                return False

    return True
```

### Rule 8: Signal Order Contract
**Signals must be emitted in exact order for every structural change**

```python
# ✅ REQUIRED order for structural changes
def execute(self, model: PaneModel) -> CommandResult:
    # 1. Signal about to change
    model.signals.about_to_change.emit()

    # 2. Perform mutation
    result = self._perform_mutation(model)

    # 3. Signal changed
    model.signals.changed.emit()

    # 4. Signal specific changes
    if result.structure_changed:
        model.signals.structure_changed.emit()

    if result.changed_panes:
        for pane_id in result.changed_panes:
            model.signals.node_changed.emit(pane_id)

    return result

# ❌ FORBIDDEN - Wrong order or missing signals
def bad_execute(self, model: PaneModel):
    self._perform_mutation(model)  # NEVER mutate before signal
    model.signals.changed.emit()   # NEVER skip about_to_change
```

**Validation Code**:
```python
def validate_signal_order() -> bool:
    """Ensure proper signal emission order in commands."""

    command_files = glob.glob("src/controller/commands/*.py")

    for file_path in command_files:
        with open(file_path) as f:
            content = f.read()

        if "def execute(" in content:
            lines = content.split('\n')
            execute_started = False
            found_about_to_change = False
            found_mutation = False
            found_changed = False

            for line in lines:
                line = line.strip()

                if "def execute(" in line:
                    execute_started = True
                    continue

                if execute_started and line.startswith("def "):
                    break  # End of execute method

                if execute_started:
                    if "about_to_change.emit()" in line:
                        if found_mutation:
                            print(f"VIOLATION: about_to_change after mutation in {file_path}")
                            return False
                        found_about_to_change = True

                    elif any(x in line for x in ["model.root =", "children.append", "_perform_"]):
                        if not found_about_to_change:
                            print(f"VIOLATION: mutation before about_to_change in {file_path}")
                            return False
                        found_mutation = True

                    elif "changed.emit()" in line:
                        if not found_mutation:
                            print(f"VIOLATION: changed without mutation in {file_path}")
                            return False
                        found_changed = True

    return True
```

---

## 🎨 VIEW LAYER RULES

### Rule 9: Reconciliation, Never Rebuild
**Always reuse existing widgets, never clear and rebuild**

```python
# ✅ CORRECT - Reconciliation preserves widgets
def on_structure_changed(self):
    old_tree = self.current_tree
    new_tree = self.model.root

    # Calculate minimal diff
    diff = self.reconciler.diff_trees(old_tree, new_tree)

    # Apply only necessary changes
    for pane_id in diff.removed:
        self._remove_widget(pane_id)  # Remove only deleted

    for pane_id in diff.added:
        self._add_widget(pane_id)     # Add only new

    for pane_id in diff.modified:
        self._update_widget(pane_id)  # Update only changed

# ❌ FORBIDDEN - Rebuild destroys all widgets
def bad_update(self):
    self.clear_all_widgets()      # NEVER clear everything
    self.build_from_tree()        # NEVER rebuild from scratch
```

**Validation Code**:
```python
def validate_no_rebuild_pattern() -> bool:
    """Ensure view uses reconciliation, not rebuild."""

    view_files = glob.glob("src/view/*.py")

    forbidden_patterns = [
        "clear_all", "removeWidget", "deleteLater",
        "build_from_tree", "rebuild", "recreate_all"
    ]

    for file_path in view_files:
        with open(file_path) as f:
            content = f.read()

        for pattern in forbidden_patterns:
            if pattern in content and "reconcil" not in content:
                print(f"VIOLATION: Rebuild pattern found: {pattern} in {file_path}")
                return False

    return True

def validate_reconciliation_usage() -> bool:
    """Ensure reconciliation is used for updates."""

    container_file = "src/view/container.py"
    if os.path.exists(container_file):
        with open(container_file) as f:
            content = f.read()

        required_patterns = [
            "reconciler.diff_trees", "diff.removed", "diff.added",
            "setUpdatesEnabled(False)", "setUpdatesEnabled(True)"
        ]

        for pattern in required_patterns:
            if pattern not in content:
                print(f"VIOLATION: Missing reconciliation pattern: {pattern}")
                return False

    return True
```

### Rule 10: Atomic View Updates
**All view updates must be atomic to prevent flicker**

```python
# ✅ REQUIRED - Atomic updates
def update_layout(self):
    self.setUpdatesEnabled(False)  # REQUIRED
    try:
        self._reconcile_changes()
        self._update_geometry()
        self._update_focus_indicators()
    finally:
        self.setUpdatesEnabled(True)  # REQUIRED in finally

# ❌ FORBIDDEN - Non-atomic updates
def bad_update(self):
    self._add_widget(pane_id)      # Immediate update
    self._remove_widget(other_id)  # Another immediate update
    self._update_geometry()        # Third immediate update
```

**Validation Code**:
```python
def validate_atomic_updates() -> bool:
    """Ensure all view updates are atomic."""

    view_files = glob.glob("src/view/*.py")

    for file_path in view_files:
        with open(file_path) as f:
            content = f.read()

        # Check for update methods
        update_methods = re.findall(r'def (\w*update\w*|reconcil\w*)\(', content)

        for method in update_methods:
            method_content = extract_method_content(content, method)

            if "setUpdatesEnabled(False)" not in method_content:
                print(f"VIOLATION: Non-atomic update in {method}")
                return False

            if "finally:" not in method_content or "setUpdatesEnabled(True)" not in method_content:
                print(f"VIOLATION: Missing atomic cleanup in {method}")
                return False

    return True

def extract_method_content(content: str, method_name: str) -> str:
    """Extract method content for analysis."""
    lines = content.split('\n')
    in_method = False
    method_lines = []
    indent_level = None

    for line in lines:
        if f"def {method_name}(" in line:
            in_method = True
            indent_level = len(line) - len(line.lstrip())
            method_lines.append(line)
        elif in_method:
            if line.strip() and (len(line) - len(line.lstrip())) <= indent_level:
                break  # End of method
            method_lines.append(line)

    return '\n'.join(method_lines)
```

### Rule 11: View Owns Styling
**Styling and appearance belong in view layer only**

```python
# ✅ CORRECT - Styling in view layer
class PaneContainer(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("QWidget { border: 1px solid gray; }")
        self.focus_border_color = QColor(0, 120, 212)

    def apply_theme(self, theme: Theme):
        self.setStyleSheet(theme.generate_stylesheet())

# ❌ FORBIDDEN - Styling in model
class PaneModel:
    def __init__(self):
        self.border_color = "gray"      # NEVER - model doesn't know colors
        self.font_size = 12             # NEVER - model doesn't know fonts

# ❌ FORBIDDEN - Styling in controller
class SplitCommand:
    def execute(self, model):
        widget.setStyleSheet("...")     # NEVER - controller doesn't style
```

**Validation Code**:
```python
def validate_styling_separation() -> bool:
    """Ensure styling only exists in view layer."""

    # Check model and controller layers have no styling
    non_view_files = glob.glob("src/core/*.py") + glob.glob("src/controller/*.py")

    styling_patterns = [
        "setStyleSheet", "QColor", "QFont", "QPalette",
        "color", "font", "border", "margin", "padding"
    ]

    for file_path in non_view_files:
        with open(file_path) as f:
            content = f.read()

        for pattern in styling_patterns:
            if pattern in content and "import" not in content:
                print(f"VIOLATION: Styling in non-view layer: {pattern} in {file_path}")
                return False

    return True
```

---

## 📦 DATA MANAGEMENT RULES

### Rule 12: PaneId Immutability
**PaneId must remain stable across all operations**

```python
# ✅ CORRECT - PaneId never changes
pane_id = generate_pane_id()  # Generated once
# ... pane_id used throughout lifetime ...
# ... split operations, moves, undo/redo ...
# ... pane_id NEVER changes ...

# ❌ FORBIDDEN - Changing PaneId
def split_pane(self, pane_id):
    new_id = generate_pane_id()
    old_node.pane_id = new_id    # NEVER change existing ID

# ❌ FORBIDDEN - PaneId based on content
def generate_content_based_id(widget_content):
    return f"pane_{hash(widget_content)}"  # NEVER - unstable
```

**Validation Code**:
```python
def validate_pane_id_immutability() -> bool:
    """Ensure PaneId is never modified after creation."""

    all_files = (glob.glob("src/**/*.py", recursive=True) +
                glob.glob("tests/**/*.py", recursive=True))

    for file_path in all_files:
        with open(file_path) as f:
            content = f.read()

        # Check for PaneId assignment after creation
        if ".pane_id =" in content and "def __init__" not in content:
            print(f"VIOLATION: PaneId modification in {file_path}")
            return False

        # Check for PaneId regeneration
        regeneration_patterns = [
            "pane_id = generate_pane_id",
            "node.pane_id = PaneId"
        ]

        for pattern in regeneration_patterns:
            if pattern in content and "__init__" not in content:
                print(f"VIOLATION: PaneId regeneration in {file_path}")
                return False

    return True

def test_pane_id_stability():
    """Test that PaneId remains stable across operations."""

    model = PaneModel()
    controller = PaneController(model)

    # Create initial pane
    root_id = generate_pane_id()
    model.set_root(LeafNode(root_id, "test:widget"))

    original_id = root_id

    # Perform various operations
    controller.execute(SplitCommand(root_id, WherePosition.RIGHT, "test:widget2"))
    assert root_id == original_id, "PaneId changed during split"

    controller.undo()
    assert root_id == original_id, "PaneId changed during undo"

    controller.redo()
    assert root_id == original_id, "PaneId changed during redo"
```

### Rule 13: Widget ID Opacity
**widget_id is opaque to MultiSplit - only store and return**

```python
# ✅ CORRECT - Opaque usage
class LeafNode:
    def __init__(self, pane_id: PaneId, widget_id: WidgetId):
        self.pane_id = pane_id
        self.widget_id = widget_id  # Store as-is, don't interpret

# ✅ CORRECT - Pass-through
def request_widget(self, widget_id: WidgetId, pane_id: PaneId):
    self.widget_needed.emit(widget_id, pane_id)  # Just pass along

# ❌ FORBIDDEN - Interpreting widget_id
def create_widget_from_id(self, widget_id: WidgetId):
    if widget_id.startswith("editor:"):     # NEVER parse widget_id
        return QTextEdit()
    elif widget_id.startswith("terminal:"):
        return QTerminal()

# ❌ FORBIDDEN - Widget_id validation
def validate_widget_id(self, widget_id: WidgetId) -> bool:
    return ":" in widget_id  # NEVER validate format
```

**Validation Code**:
```python
def validate_widget_id_opacity() -> bool:
    """Ensure widget_id is treated as opaque."""

    multisplit_files = glob.glob("src/**/*.py", recursive=True)

    # Remove provider and test files (they can interpret widget_id)
    multisplit_files = [f for f in multisplit_files
                       if "provider" not in f and "test" not in f]

    forbidden_operations = [
        ".startswith(", ".endswith(", ".split(':',
        ".replace(", ".strip(", "parse_", "validate_widget_id"
    ]

    for file_path in multisplit_files:
        with open(file_path) as f:
            content = f.read()

        if "widget_id" in content:
            for operation in forbidden_operations:
                if f"widget_id{operation}" in content:
                    print(f"VIOLATION: widget_id interpretation in {file_path}")
                    return False

    return True
```

---

## ⚡ PERFORMANCE RULES

### Rule 14: Widget Reuse Maximization
**Always reuse widgets during reconciliation**

```python
# ✅ CORRECT - Maximum reuse
def reconcile(self, diff: DiffResult):
    # Preserve widgets that haven't changed
    for pane_id in diff.modified:
        widget = self.widget_map[pane_id]
        # Update widget position, don't recreate
        self._update_widget_geometry(widget, new_bounds)

    # Only create new widgets for truly new panes
    for pane_id in diff.added:
        self._create_widget(pane_id)  # Last resort

# ❌ FORBIDDEN - Unnecessary recreation
def bad_reconcile(self, diff: DiffResult):
    # Clear everything
    for widget in self.widget_map.values():
        widget.deleteLater()  # NEVER - destroys reusable widgets

    # Recreate everything
    self._create_all_widgets()
```

**Validation Code**:
```python
def validate_widget_reuse() -> bool:
    """Ensure widgets are maximally reused."""

    container_file = "src/view/container.py"
    if os.path.exists(container_file):
        with open(container_file) as f:
            content = f.read()

        # Check for excessive widget destruction
        destruction_patterns = [
            "deleteLater()", "clear()", "removeWidget",
            "widget_map.clear()", "widget_map = {}"
        ]

        for pattern in destruction_patterns:
            if pattern in content and "diff.removed" not in content:
                print(f"VIOLATION: Excessive widget destruction: {pattern}")
                return False

    return True

def measure_widget_reuse_efficiency():
    """Measure widget reuse during reconciliation."""

    # This would be a performance test
    container = PaneContainer(model, controller)

    # Track widget creation
    widgets_created = 0
    original_create = container._create_widget

    def tracking_create(*args, **kwargs):
        nonlocal widgets_created
        widgets_created += 1
        return original_create(*args, **kwargs)

    container._create_widget = tracking_create

    # Perform operations that should reuse widgets
    # ... test operations ...

    # Measure efficiency
    efficiency = (total_operations - widgets_created) / total_operations
    assert efficiency > 0.8, f"Widget reuse efficiency too low: {efficiency}"
```

### Rule 15: Batch Operations
**Group related changes to minimize update cycles**

```python
# ✅ CORRECT - Batched operations
with controller.begin_transaction():
    controller.execute(SplitCommand(...))
    controller.execute(ResizeCommand(...))
    controller.execute(FocusCommand(...))
# Single update at end

# ✅ CORRECT - Atomic view updates
self.setUpdatesEnabled(False)
try:
    self._process_all_changes(diff)
finally:
    self.setUpdatesEnabled(True)

# ❌ FORBIDDEN - Individual updates
controller.execute(SplitCommand(...))    # Update
controller.execute(ResizeCommand(...))   # Update
controller.execute(FocusCommand(...))    # Update (3 total)
```

**Validation Code**:
```python
def validate_batched_operations() -> bool:
    """Ensure operations are properly batched."""

    test_files = glob.glob("tests/**/*.py", recursive=True)

    for file_path in test_files:
        with open(file_path) as f:
            content = f.read()

        # Look for multiple execute calls without transaction
        execute_calls = content.count("controller.execute(")
        transaction_calls = content.count("begin_transaction(")

        if execute_calls > 2 and transaction_calls == 0:
            print(f"WARNING: Multiple operations without transaction in {file_path}")

    return True
```

---

## 🧪 TESTING RULES

### Rule 16: Layer Testing Isolation
**Each layer must be testable in isolation**

```python
# ✅ CORRECT - Model tests without Qt
def test_model_split():
    model = PaneModel()  # No Qt imports needed
    command = SplitCommand(pane_id, where, widget_id)

    result = command.execute(model)
    assert result.success
    assert len(model.get_all_panes()) == 2

# ✅ CORRECT - Controller tests with mock model
def test_controller_undo():
    mock_model = Mock(spec=PaneModel)
    controller = PaneController(mock_model)

    command = Mock(spec=Command)
    controller.execute(command)

    assert command.execute.called
    assert command in controller.undo_stack

# ✅ CORRECT - View tests with mock controller
def test_view_reconciliation():
    mock_controller = Mock(spec=PaneController)
    mock_model = Mock(spec=PaneModel)

    container = PaneContainer(mock_model, mock_controller)
    # Test view behavior without real mutations
```

**Validation Code**:
```python
def validate_test_isolation() -> bool:
    """Ensure tests don't cross layer boundaries inappropriately."""

    model_test_files = glob.glob("tests/model/**/*.py", recursive=True)

    for file_path in model_test_files:
        with open(file_path) as f:
            content = f.read()

        # Model tests shouldn't import Qt
        if any(qt in content for qt in ["PySide6", "PyQt", "QWidget"]):
            print(f"VIOLATION: Model test imports Qt: {file_path}")
            return False

        # Model tests shouldn't import view/controller
        if any(layer in content for layer in ["from view", "from controller"]):
            print(f"VIOLATION: Model test imports other layers: {file_path}")
            return False

    return True

def validate_mock_usage() -> bool:
    """Ensure appropriate mocking in tests."""

    controller_test_files = glob.glob("tests/controller/**/*.py", recursive=True)

    for file_path in controller_test_files:
        with open(file_path) as f:
            content = f.read()

        # Controller tests should mock model and view
        if "PaneModel(" in content and "Mock" not in content:
            print(f"WARNING: Controller test using real model: {file_path}")

        if "PaneContainer(" in content:
            print(f"VIOLATION: Controller test creating real view: {file_path}")
            return False

    return True
```

---

## 🛡️ ERROR HANDLING RULES

### Rule 17: Specific Exception Types
**Use specific exceptions, never generic Exception**

```python
# ✅ CORRECT - Specific exceptions
def find_node(self, pane_id: PaneId) -> PaneNode:
    if pane_id not in self.pane_registry:
        raise PaneNotFoundError(f"Pane {pane_id} not found")
    return self.pane_registry[pane_id]

def validate_structure(self) -> bool:
    if not self.root:
        raise InvalidStructureError("Tree has no root")
    if not self.root.validate():
        raise InvalidStructureError("Root node validation failed")

# ❌ FORBIDDEN - Generic exceptions
def bad_find_node(self, pane_id: PaneId) -> PaneNode:
    try:
        return self.pane_registry[pane_id]
    except KeyError:
        raise Exception("Something went wrong")  # NEVER
```

**Validation Code**:
```python
def validate_specific_exceptions() -> bool:
    """Ensure only specific exceptions are raised."""

    all_files = glob.glob("src/**/*.py", recursive=True)

    for file_path in all_files:
        with open(file_path) as f:
            content = f.read()

        # Check for generic Exception usage
        if "raise Exception(" in content:
            print(f"VIOLATION: Generic Exception raised in {file_path}")
            return False

        # Check for bare except clauses
        if "except:" in content:
            print(f"VIOLATION: Bare except clause in {file_path}")
            return False

    return True

def validate_exception_hierarchy() -> bool:
    """Ensure all custom exceptions inherit from appropriate base."""

    from core.exceptions import PaneError

    exception_module = __import__('core.exceptions')

    for name in dir(exception_module):
        obj = getattr(exception_module, name)
        if (isinstance(obj, type) and
            issubclass(obj, Exception) and
            obj != PaneError and
            obj != Exception):

            if not issubclass(obj, PaneError):
                print(f"VIOLATION: Exception {name} doesn't inherit from PaneError")
                return False

    return True
```

---

## 🚫 ANTI-PATTERNS TO AVOID

### Anti-Pattern 1: Creating Widgets in Advance
```python
# ❌ BAD - Premature widget creation
class BadPaneManager:
    def __init__(self):
        self.widget_pool = [QTextEdit() for _ in range(10)]  # NEVER

# ✅ GOOD - On-demand via provider
class GoodPaneManager:
    def need_widget(self, widget_id: WidgetId, pane_id: PaneId):
        self.widget_needed.emit(widget_id, pane_id)  # Request from app
```

### Anti-Pattern 2: Storing Widget References in Model
```python
# ❌ BAD - Widget in model
class BadLeafNode:
    def __init__(self, widget: QWidget):
        self.widget = widget  # NEVER store Qt objects in model

# ✅ GOOD - Widget ID only
class GoodLeafNode:
    def __init__(self, pane_id: PaneId, widget_id: WidgetId):
        self.pane_id = pane_id
        self.widget_id = widget_id  # Opaque string only
```

### Anti-Pattern 3: Mutating Model Directly
```python
# ❌ BAD - Direct mutation
def bad_split(self, model: PaneModel):
    model.root.children.append(new_node)  # NEVER

# ✅ GOOD - Command pattern
def good_split(self, controller: PaneController):
    controller.execute(SplitCommand(...))  # Always via commands
```

### Anti-Pattern 4: Rebuilding on Update
```python
# ❌ BAD - Clear and rebuild
def bad_update(self):
    for widget in self.widgets:
        widget.deleteLater()  # NEVER clear all
    self.build_everything()   # NEVER rebuild

# ✅ GOOD - Reconciliation
def good_update(self):
    diff = self.reconciler.diff_trees(old, new)
    self._apply_minimal_changes(diff)  # Only necessary changes
```

---

## ✅ ENFORCEMENT CHECKLIST

Before committing code, verify:

### Critical Rules (MUST PASS)
- [ ] No Qt imports in model layer
- [ ] All mutations go through commands
- [ ] Commands have proper undo support
- [ ] Reconciliation preserves widgets
- [ ] PaneIds remain stable across operations
- [ ] Signals emitted in correct order
- [ ] No circular imports in hierarchy

### Architecture Rules (MUST PASS)
- [ ] Visitor pattern used for tree operations
- [ ] Complete interfaces defined upfront
- [ ] Widget provider pattern followed
- [ ] Layer separation maintained
- [ ] Atomic view updates used

### Quality Rules (SHOULD PASS)
- [ ] Specific exceptions used
- [ ] Widget reuse maximized
- [ ] Operations batched appropriately
- [ ] Tests isolated by layer
- [ ] Documentation updated

### Automated Validation
```python
def run_all_validations() -> bool:
    """Run complete validation suite."""

    validations = [
        validate_layer_separation,
        validate_no_widget_creation,
        validate_no_direct_mutation,
        validate_import_hierarchy,
        validate_visitor_pattern_usage,
        validate_command_pattern_complete,
        validate_signal_order,
        validate_no_rebuild_pattern,
        validate_atomic_updates,
        validate_pane_id_immutability,
        validate_widget_id_opacity,
        validate_specific_exceptions
    ]

    results = []
    for validation in validations:
        try:
            result = validation()
            results.append(result)
            if not result:
                print(f"FAILED: {validation.__name__}")
        except Exception as e:
            print(f"ERROR in {validation.__name__}: {e}")
            results.append(False)

    passed = sum(results)
    total = len(results)

    print(f"Validation Results: {passed}/{total} passed")

    return all(results)

# Usage in CI/CD
if __name__ == "__main__":
    success = run_all_validations()
    sys.exit(0 if success else 1)
```

---

## Quick Reference

### Golden Rules
1. **Model knows nothing of Qt** - Pure Python only
2. **View never touches Model** - Read-only access, controller for changes
3. **Controller is the only writer** - All mutations via commands
4. **Commands for all mutations** - No direct model changes
5. **Reconcile, don't rebuild** - Preserve widgets whenever possible
6. **Provider creates widgets** - MultiSplit only arranges
7. **Extend, don't modify** - Complete skeleton first

### Import Hierarchy
```
types → exceptions → utils → nodes → model → commands → controller → view → widget
```

### Signal Order
```
about_to_change → mutate → changed → structure_changed → node_changed
```

### Layer Responsibilities
```
Model:      Structure + State (no Qt)
Controller: Mutations + Undo (commands only)
View:       Display + Interaction (reconciliation)
Provider:   Widget Creation (application)
```

### Validation Commands
```bash
# Run automated checks
python -m src.validation.validate_all

# Check specific layer
python -m src.validation.validate_layer model

# Check rule compliance
python -m src.validation.validate_rules
```

---

## Related Documents

- [MVP Plan](mvp-plan.md) - Implementation roadmap with algorithms
- [Development Protocol](development-protocol.md) - Task creation and execution workflow
- [MVC Architecture](../02-architecture/mvc-architecture.md) - Layer specifications
- [Widget Provider](../02-architecture/widget-provider.md) - Provider pattern details

---

This document consolidates all critical rules from our comprehensive documentation. Following these rules ensures architectural integrity, maintainability, and extensibility of the MultiSplit widget codebase.