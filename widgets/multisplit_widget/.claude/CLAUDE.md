# MultiSplit Widget - Claude Code Development Instructions

## 🚨 CRITICAL: Development Protocol

This project follows a **strict three-phase development protocol**:

```
1. WRITE     → Documentation defines architecture
2. DOCUMENT  → Tasks specify implementation
3. EXECUTE   → Agent implements following rules
```

**DO NOT implement code without documented tasks.**
**DO NOT create tasks without documentation.**
**DO NOT violate layer separation rules.**

---

## Project Overview

MultiSplit is a PySide6 widget for recursive split-pane layouts following **strict MVC architecture** with a **widget provider pattern**. The widget manages layout but NEVER creates widgets.

### Key Documents (Read These First!)
1. `docs/mvc-rules.md` - **CRITICAL: Layer separation rules**
2. `docs/development-rules-GUIDE.md` - **Complete development rules**
3. `docs/development-protocol-GUIDE.md` - **How we work**
4. `docs/mvp-implementation-PLAN.md` - **What to build**

---

## 🔴 ABSOLUTE RULES (Violations = Rejected)

### Layer Separation
```
Model:      Pure Python. NO Qt. NO widgets.
Controller: Commands only. NO view imports.
View:       No model mutations. Reconcile only.
```

### File Organization
```
src/core/       → Model layer (NO Qt imports)
src/controller/ → Controller layer (NO view imports)
src/view/       → View layer (Qt allowed, read-only model)
```

### Import Verification
```python
# For ANY file in src/core/
if "PySide6" in file_content or "PyQt" in file_content:
    REJECT: "Model cannot import Qt"

# For ANY file in src/controller/
if "from view" in file_content:
    REJECT: "Controller cannot import view"
```

---

## Development Workflow

### When Asked to Implement Something

1. **CHECK for documentation**
   ```
   Does docs/ contain specifications for this feature?
   NO → Ask: "Please document this feature first"
   YES → Continue
   ```

2. **CHECK for task definition**
   ```
   Is there a detailed task with:
   - File paths?
   - Allowed imports?
   - Success criteria?
   NO → Ask: "Please create a detailed task"
   YES → Continue
   ```

3. **IMPLEMENT following rules**
   ```python
   # Before writing ANY import:
   Check: What layer is this file in?
   Check: Is this import allowed for this layer?

   # Before writing ANY model change:
   Check: Am I using a Command?
   Check: Does the Command have undo?
   ```

4. **VALIDATE before completing**
   ```python
   ✓ No forbidden imports
   ✓ All mutations via Commands
   ✓ Signals in correct order
   ✓ Tests included
   ✓ Documentation updated
   ```

---

## Quick Decision Tree

### "Add a new feature"
```
Modifies tree structure? → Create Command in src/controller/commands/
Traverses tree?         → Create Visitor in src/core/visitors/
Renders something?      → Create Renderer in src/view/renderers/
Handles user input?     → Create Handler in src/view/interaction/
```

### "Fix a bug"
```
In model layer?      → No Qt imports allowed, pure Python fix
In controller?       → Ensure Commands have proper undo
In view?            → Ensure reconciliation, not rebuild
```

### "Add a widget"
```
STOP: MultiSplit NEVER creates widgets
→ Widget creation is the application's responsibility
→ Use WidgetProvider protocol
```

---

## Command Template

When implementing any Command:

```python
from core.types import PaneId  # Allowed
from core.model import PaneModel  # Allowed
from controller.commands import Command, CommandResult  # Allowed
# from PySide6 import ...  # FORBIDDEN in commands

class YourCommand(Command):
    def __init__(self, pane_id: PaneId):
        # Store ALL data needed for undo
        self.pane_id = pane_id
        self.previous_state = None  # Set during execute

    def validate(self, model: PaneModel) -> ValidationResult:
        # Check preconditions
        if not model.find_node(self.pane_id):
            return ValidationResult(False, "Pane not found")
        return ValidationResult(True)

    def execute(self, model: PaneModel) -> CommandResult:
        # Signal order is CRITICAL
        model.signals.about_to_change.emit()

        # Store state for undo
        self.previous_state = self._capture_state(model)

        # Perform mutation
        # ...

        model.signals.changed.emit()
        return CommandResult(success=True)

    def undo(self, model: PaneModel) -> CommandResult:
        # MUST reverse execute() exactly
        model.signals.about_to_change.emit()
        self._restore_state(model, self.previous_state)
        model.signals.changed.emit()
        return CommandResult(success=True)
```

---

## Testing Requirements

### For Model Tests
```python
# Run without Qt
import sys
assert 'PySide6' not in sys.modules
from core.model import PaneModel  # Should work
```

### For Command Tests
```python
def test_command_undo():
    model = PaneModel()
    initial_state = model.save_state()

    cmd = YourCommand(...)
    cmd.execute(model)
    cmd.undo(model)

    assert model.save_state() == initial_state  # Perfect undo
```

---

## Common Mistakes to Avoid

### ❌ Creating widgets directly
```python
# WRONG
widget = QLabel("Hello")  # MultiSplit never creates widgets
```

### ❌ Importing Qt in model
```python
# WRONG - in src/core/model.py
from PySide6.QtCore import QObject  # Model is pure Python
```

### ❌ Mutating model directly
```python
# WRONG
model.root.children.append(node)  # Use Commands

# RIGHT
controller.execute(SplitCommand(...))
```

### ❌ Rebuilding on update
```python
# WRONG
self.clear_all_widgets()
self.rebuild_from_model()  # Causes flicker

# RIGHT
self.reconcile(old_tree, new_tree)  # Reuse widgets
```

---

## Validation Checklist

Before submitting code:

- [ ] File is in correct layer directory
- [ ] Imports match layer restrictions
- [ ] All mutations use Commands
- [ ] Commands have working undo
- [ ] No widgets created directly
- [ ] View uses reconciliation
- [ ] Signals emitted in order
- [ ] Tests can run without Qt (for model)
- [ ] Documentation updated

---

## Getting Help

1. **Architecture questions** → Read `docs/split-pane-architecture.md`
2. **Rule violations** → Check `docs/development-rules-GUIDE.md`
3. **Task structure** → See `docs/development-protocol-GUIDE.md`
4. **Widget patterns** → Read `docs/widget-provider-ARCHITECTURE.md`

---

## Special Agent Usage

When complex implementation is needed:

```
Use the multisplit-developer agent for implementation.
The agent knows all rules and will enforce them.
```

---

## Remember

**"Documentation → Tasks → Implementation"**

Never skip steps. The architecture depends on it.