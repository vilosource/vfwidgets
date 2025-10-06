# KeybindingManager Developer Experience Plan

**Document Type**: PLAN
**Status**: Draft
**Created**: 2025-10-03
**Purpose**: Define requirements for exceptional developer experience

---

## Table of Contents

1. [Philosophy](#philosophy)
2. [DX Requirements](#dx-requirements)
3. [Priority Classification](#priority-classification)
4. [Success Criteria](#success-criteria)
5. [Comparison with Other Libraries](#comparison-with-other-libraries)

---

## Philosophy

### Core Belief: Developer Experience IS Product Quality

A reusable library is only as good as its developer experience. The KeybindingManager should be:

- **Discoverable** - Easy to find what you need
- **Understandable** - Clear documentation and examples
- **Predictable** - Behaves as expected, no surprises
- **Debuggable** - Clear errors, helpful warnings
- **Extensible** - Easy to customize and adapt

### The 5-Minute Rule

**Goal**: A developer should be able to integrate KeybindingManager into their app in < 5 minutes with:
1. Copy-paste from Quick Start
2. See it working
3. Understand how to customize

If it takes longer, our DX has failed.

---

## DX Requirements

### 1. Progressive Examples ⭐ CRITICAL

**Problem**: Developers learn by example, not by reading architecture docs.

**Solution**: Provide 4 progressive examples:

#### Example 1: Minimal (10 lines)
```python
# examples/01_minimal_usage.py
from vfwidgets_keybinding import ActionRegistry, KeybindingManager
from PySide6.QtWidgets import QApplication, QMainWindow

app = QApplication([])
window = QMainWindow()

registry = ActionRegistry()
registry.register("quit", "Quit", app.quit, "Ctrl+Q")

manager = KeybindingManager(registry)
manager.apply_to_window(window)

window.show()
app.exec()
```

#### Example 2: Full Application (50 lines)
- Multiple categories
- Multiple actions
- Persistence enabled
- Basic error handling

#### Example 3: Custom Dialog (100 lines)
- Shows customization UI
- Save/load settings
- Reset to defaults

#### Example 4: Advanced Context-Aware (150 lines)
- Different shortcuts in different modes
- Dynamic action registration
- Conflict handling

**Acceptance Criteria**:
- Each example runs without modification
- Comments explain every line
- Progressive complexity (don't show everything at once)
- `examples/README.md` explains what each example teaches

---

### 2. Type Hints & IDE Support ⭐ CRITICAL

**Problem**: Without type hints, IDE can't help developers.

**Solution**:
- Every public method has full type hints
- Use `dataclasses` for structured data
- Provide `.pyi` stub files if needed

```python
from typing import Callable, Optional, Dict, List
from dataclasses import dataclass

@dataclass
class ActionDefinition:
    action_id: str
    name: str
    handler: Callable[[], None]
    default_shortcut: Optional[str]
    category: str
    description: str
    enabled: bool = True

class ActionRegistry:
    def register(
        self,
        action_id: str,
        name: str,
        handler: Callable[[], None],
        default_shortcut: Optional[str] = None,
        category: str = "General",
        description: str = ""
    ) -> None:
        """Register an action with the registry."""
```

**Acceptance Criteria**:
- VSCode IntelliSense shows parameter types
- PyCharm autocomplete works
- `mypy --strict` passes with no errors

---

### 3. Error Messages & Validation ⭐ CRITICAL

**Problem**: Cryptic errors waste developer time.

**Solution**: Every error should:
1. Say what went wrong
2. Say why it's wrong
3. Suggest how to fix it

```python
class ActionRegistry:
    def register(self, action_id: str, ...):
        # Duplicate ID
        if action_id in self.actions:
            raise ValueError(
                f"Action '{action_id}' is already registered.\n"
                f"Solution: Use a unique ID or call "
                f"registry.unregister('{action_id}') first."
            )

        # Invalid handler
        if not callable(handler):
            raise TypeError(
                f"Handler for action '{action_id}' must be callable.\n"
                f"Got: {type(handler).__name__}\n"
                f"Solution: Pass a function or method, e.g., self.on_save"
            )

        # Invalid shortcut format
        if default_shortcut and not QKeySequence(default_shortcut).count():
            raise ValueError(
                f"Invalid shortcut '{default_shortcut}' for action '{action_id}'.\n"
                f"Examples of valid shortcuts: 'Ctrl+S', 'Ctrl+Shift+K', 'F5'\n"
                f"See Qt QKeySequence documentation for format."
            )
```

**Acceptance Criteria**:
- Every exception has multi-line message
- Error messages tested in test suite
- Common mistakes have specific errors (not generic ValueError)

---

### 4. Quick Start Guide ⭐ HIGH PRIORITY

**File**: `docs/getting-started-GUIDE.md`

**Structure**:
```markdown
# 5-Minute Quick Start

## Prerequisites
- Python 3.8+
- PySide6 or PyQt6

## Step 1: Install (10 seconds)
```bash
pip install vfwidgets-keybinding
```

## Step 2: Copy This Code (1 minute)
[Complete minimal example that actually runs]

## Step 3: Run It (10 seconds)
```bash
python my_app.py
```

Press Ctrl+Q → App quits
Success! You've integrated KeybindingManager.

## Next Steps
- [Add more actions](examples/02_full_application.py)
- [Enable persistence](docs/persistence.md)
- [Customize UI](examples/03_custom_dialog.py)
```

**Acceptance Criteria**:
- Can be completed in 5 minutes
- Copy-paste works without modification
- Links to next learning resources

---

### 5. API Reference Documentation ⭐ HIGH PRIORITY

**File**: `docs/api-reference-GUIDE.md`

**Structure**: For each public class/method:
- **Signature** with types
- **Description** (what it does)
- **Parameters** (each one explained)
- **Returns** (what you get back)
- **Raises** (possible exceptions)
- **Example** (usage code)
- **See Also** (related methods)

**Example**:
```markdown
## ActionRegistry.register()

### Signature
```python
def register(
    self,
    action_id: str,
    name: str,
    handler: Callable[[], None],
    default_shortcut: Optional[str] = None,
    category: str = "General",
    description: str = ""
) -> None
```

### Description
Registers a new action that can be triggered by keyboard shortcuts.

### Parameters
- `action_id` (str): Unique identifier for this action. Used for keybinding lookups.
- `name` (str): Human-readable name displayed in UI (e.g., "Save File")
- `handler` (Callable): Function/method called when action is triggered
- `default_shortcut` (str, optional): Default key sequence (e.g., "Ctrl+S")
- `category` (str): Group name for UI organization (default: "General")
- `description` (str): Detailed explanation for tooltips/help

### Raises
- `ValueError`: If action_id already registered
- `TypeError`: If handler is not callable

### Example
```python
registry.register(
    action_id="save_file",
    name="Save File",
    handler=self.on_save,
    default_shortcut="Ctrl+S",
    category="File",
    description="Save the current document to disk"
)
```

### See Also
- `ActionRegistry.unregister()`
- `ActionRegistry.get_action()`
```

**Acceptance Criteria**:
- Every public API documented
- Examples for each method
- Links between related methods

---

### 6. Common Patterns Cookbook ⭐ SHOULD HAVE

**File**: `docs/patterns-GUIDE.md`

**Structure**:
```markdown
## Pattern: Migrating from Hardcoded QActions

**Scenario**: You have existing QActions hardcoded.

**Before**:
```python
save_action = QAction("Save", self)
save_action.setShortcut("Ctrl+S")
save_action.triggered.connect(self.save)
self.addAction(save_action)
```

**After**:
```python
registry.register("save", "Save", self.save, "Ctrl+S")
manager.apply_to_window(self)
```

**Benefits**:
- User can customize shortcut
- Automatic persistence
- No manual QAction management

---

## Pattern: Context-Aware Shortcuts

**Scenario**: Different shortcuts when in edit mode vs view mode.

[Solution code + explanation]

---

## Pattern: Dynamic Action Registration

**Scenario**: Register actions based on plugins or runtime config.

[Solution code + explanation]
```

**Acceptance Criteria**:
- Covers 10+ common use cases
- Real-world scenarios (not toy examples)
- Copy-paste solutions

---

### 7. Troubleshooting Guide ⭐ SHOULD HAVE

**File**: `docs/troubleshooting-GUIDE.md`

**Structure**:
```markdown
## Shortcut Not Working

### Symptoms
- Pressing key combination does nothing
- No error message appears

### Possible Causes

#### 1. Action Not Registered
**Check**:
```python
if manager.get_binding("my_action"):
    print("Registered")
```

**Solution**: Call `registry.register()` before `manager.apply_to_window()`

#### 2. Manager Not Applied to Window
**Check**:
```python
actions = window.actions()
print(f"Window has {len(actions)} actions")
```

**Solution**: Call `manager.apply_to_window(window)` after registration

#### 3. Shortcut Conflict
**Check**:
```python
conflicts = manager.detect_conflicts("Ctrl+S")
if conflicts:
    print(f"Conflicts: {conflicts}")
```

**Solution**: Use different shortcut or resolve conflict
```

**Acceptance Criteria**:
- Top 10 issues covered
- Diagnostic steps provided
- Clear solutions

---

### 8. Testing Utilities ⭐ SHOULD HAVE

**Problem**: Developers need to test their keybindings.

**Solution**: Provide test helpers:

```python
# vfwidgets_keybinding/testing.py
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt

class KeybindingTestCase:
    """Helper for testing keybindings."""

    @staticmethod
    def trigger_shortcut(widget, key_sequence: str):
        """Simulate pressing a keyboard shortcut."""
        # Parse key sequence
        # Generate key events
        # Send to widget
        pass

    @staticmethod
    def assert_action_called(manager, action_id):
        """Assert an action was triggered."""
        pass

# Usage in tests
def test_save_shortcut(qtbot):
    # Setup
    window = MyApp()
    qtbot.addWidget(window)

    # Trigger
    KeybindingTestCase.trigger_shortcut(window, "Ctrl+S")

    # Assert
    assert window.save_called
```

**Acceptance Criteria**:
- Testing utils in separate module
- Works with pytest-qt
- Examples in tests/ directory

---

### 9. Visual Debugging Tools ⭐ NICE TO HAVE

**Problem**: Hard to see what's registered and what conflicts exist.

**Solution**: Debug helpers:

```python
class KeybindingManager:
    def print_summary(self):
        """Print human-readable summary of all bindings."""
        print("=" * 60)
        print("KEYBINDING SUMMARY")
        print("=" * 60)

        for category in self.registry.get_categories():
            print(f"\n[{category}]")
            actions = self.registry.get_actions_by_category(category)
            for action in actions:
                binding = self.get_binding(action.action_id)
                print(f"  {action.name:30s} {binding or '(none)':15s}")

        # Show conflicts
        conflicts = self.find_all_conflicts()
        if conflicts:
            print("\n⚠️  CONFLICTS:")
            for key, action_ids in conflicts.items():
                print(f"  {key}: {', '.join(action_ids)}")

    def validate(self) -> List[str]:
        """Return list of issues/warnings."""
        issues = []

        # Check for conflicts
        conflicts = self.find_all_conflicts()
        for key, action_ids in conflicts.items():
            issues.append(f"Conflict: {key} used by {len(action_ids)} actions")

        # Check for actions without shortcuts
        for action in self.registry.get_all_actions():
            if not self.get_binding(action.action_id):
                issues.append(f"No shortcut: {action.name}")

        return issues
```

**Acceptance Criteria**:
- `print_summary()` shows table of all bindings
- `validate()` returns list of issues
- Can be called during development

---

### 10. Performance Documentation ⭐ NICE TO HAVE

**File**: `docs/performance-GUIDE.md`

**Content**:
```markdown
## Performance Characteristics

### Action Registration
- **O(1)** per action
- **Memory**: ~200 bytes per action
- **Limit**: Tested with 1000+ actions, no measurable impact

### QAction Creation
- **Cost**: ~1ms per action on modern hardware
- **When**: Only during `apply_to_window()`, not runtime
- **Recommendation**: Register all actions at startup

### Storage I/O
- **Save**: < 10ms for 100 actions (JSON serialization)
- **Load**: < 5ms for 100 actions (JSON parsing)
- **Recommendation**: Auto-save on change, not every keystroke

### Memory Usage
- **Baseline**: ~50KB for manager infrastructure
- **Per Action**: ~200 bytes (ActionDefinition + QAction)
- **Example**: 100 actions = 50KB + 20KB = 70KB total

## Benchmarks

Run benchmarks:
```bash
python benchmarks/benchmark_registration.py
```

Results on reference hardware:
- Register 1000 actions: 15ms
- Apply to window: 120ms
- Save to JSON: 8ms
- Load from JSON: 4ms
```

**Acceptance Criteria**:
- Real benchmark numbers
- Guidance on limits
- Runnable benchmark scripts

---

### 11. Migration Guides ⭐ SHOULD HAVE

**File**: `docs/migration-GUIDE.md`

**Structure**:
```markdown
## From Hardcoded QActions

### Step 1: Extract Actions
Identify all QAction creations in your code.

### Step 2: Create Registry
Create ActionRegistry and register each action.

### Step 3: Replace QAction Code
Remove manual QAction creation, use manager.

### Step 4: Add Customization UI (Optional)
Add KeybindingDialog to preferences.

### Complete Example
[Before/after comparison of real app]

---

## From Other Keybinding Libraries

### From QShortcut
[Comparison and migration]

### From Custom Solution
[Comparison and migration]
```

**Acceptance Criteria**:
- Step-by-step migration
- Real code examples
- Comparison tables

---

### 12. Keyboard Shortcut Conventions ⭐ SHOULD HAVE

**File**: `docs/shortcut-conventions-GUIDE.md`

**Content**:
```markdown
## Platform Conventions

### Cross-Platform Shortcuts
Qt automatically maps Ctrl ↔ Cmd on macOS:
- Use `Ctrl+S` in code
- Renders as `Cmd+S` on macOS
- Renders as `Ctrl+S` on Windows/Linux

### Standard Application Shortcuts

#### File Operations
- New: `Ctrl+N`
- Open: `Ctrl+O`
- Save: `Ctrl+S`
- Save As: `Ctrl+Shift+S`
- Close: `Ctrl+W`
- Quit: `Ctrl+Q`

#### Edit Operations
- Undo: `Ctrl+Z`
- Redo: `Ctrl+Shift+Z` or `Ctrl+Y`
- Cut: `Ctrl+X`
- Copy: `Ctrl+C`
- Paste: `Ctrl+V`

[etc...]

### Custom Shortcuts - Best Practices

1. **Avoid single keys** (except F1-F12)
   - ❌ `S` for save
   - ✅ `Ctrl+S` for save

2. **Use Shift for "stronger" variant**
   - `Ctrl+W`: Close pane
   - `Ctrl+Shift+W`: Close tab (more destructive)

3. **Avoid conflicts with common apps**
   - Don't override Ctrl+C, Ctrl+V, etc.

4. **Group related actions**
   - `Ctrl+1`, `Ctrl+2`: Switch tabs
   - `Ctrl+Plus`, `Ctrl+Minus`: Zoom
```

**Acceptance Criteria**:
- Platform differences explained
- Standard shortcuts listed
- Best practices with examples

---

### 13. Accessibility Considerations ⭐ SHOULD HAVE

**File**: `docs/accessibility-GUIDE.md`

**Content**:
```markdown
## Keyboard-Only Navigation

KeybindingManager supports keyboard-only users by:
- All actions accessible via keyboard
- Customizable shortcuts for any action
- Visual indicators in UI

## Screen Reader Support

### Action Names
Use clear, descriptive action names:
```python
# ❌ Bad (unclear)
registry.register("sp_v", "SP V", ...)

# ✅ Good (clear)
registry.register("split_vertical", "Split Vertical", ...)
```

### Descriptions
Provide descriptions for screen readers:
```python
registry.register(
    "split_vertical",
    "Split Vertical",
    handler,
    description="Split the current pane vertically, creating a new pane below"
)
```

## Alternative Input Methods

KeybindingManager works with:
- On-screen keyboards
- Voice input (Dragon NaturallySpeaking, etc.)
- Switch access
```

**Acceptance Criteria**:
- Accessibility best practices documented
- Screen reader support verified
- Alternative input methods tested

---

### 14. Integration Examples ⭐ SHOULD HAVE

**Examples**:
- `examples/integration_viloxterm.py` - How ViloxTerm uses it
- `examples/integration_simple_editor.py` - Simple text editor
- `examples/integration_with_menu.py` - Menu bar + toolbar + shortcuts

**Acceptance Criteria**:
- Shows real-world integration
- Demonstrates best practices
- Runnable examples

---

### 15. Changelog & Versioning ⭐ MUST HAVE

**File**: `CHANGELOG.md`

**Format**: Keep a Changelog format
```markdown
# Changelog

All notable changes to KeybindingManager will be documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/).
Versioning follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Initial implementation of ActionRegistry
- Basic KeybindingManager

## [0.1.0] - 2025-10-03

### Added
- Initial architecture design
- Developer experience plan
```

**Acceptance Criteria**:
- Every release documented
- Breaking changes clearly marked
- Migration guides for breaking changes

---

## Priority Classification

### 🔴 CRITICAL (Must Have Before Phase 1 Release)

**Rationale**: Without these, library is unusable/frustrating

1. **Progressive Examples** - Can't learn without examples
2. **Type Hints** - IDE support is non-negotiable
3. **Error Messages** - Debugging is impossible otherwise
4. **Quick Start Guide** - Lowers barrier to entry
5. **API Reference** - Must document public API
6. **Changelog** - Version management requirement

**Deliverables for Phase 1**:
- `examples/01_minimal_usage.py`
- `examples/02_full_application.py`
- `docs/getting-started-GUIDE.md`
- `docs/api-reference-GUIDE.md`
- Type hints on all public methods
- Helpful error messages implemented
- `CHANGELOG.md` started

---

### 🟡 SHOULD HAVE (Phase 2 - UI & Polish)

**Rationale**: Significantly improves DX, expected for production library

7. **Common Patterns** - Saves developers time
8. **Troubleshooting Guide** - Self-service support
9. **Testing Utilities** - Professional libraries are testable
10. **Migration Guides** - Eases adoption
11. **Shortcut Conventions** - Helps choose good defaults
12. **Accessibility** - Inclusive design

**Deliverables for Phase 2**:
- `docs/patterns-GUIDE.md`
- `docs/troubleshooting-GUIDE.md`
- `vfwidgets_keybinding/testing.py`
- `docs/migration-GUIDE.md`
- `docs/shortcut-conventions-GUIDE.md`
- `docs/accessibility-GUIDE.md`

---

### 🟢 NICE TO HAVE (Phase 3 - Advanced)

**Rationale**: Polish and advanced features

13. **Visual Debugging Tools** - Developer convenience
14. **Performance Docs** - Transparency and trust
15. **Integration Examples** - Real-world validation

**Deliverables for Phase 3**:
- `manager.print_summary()` and `validate()`
- `docs/performance-GUIDE.md`
- `benchmarks/` directory
- Advanced integration examples

---

## Success Criteria

### Quantitative Metrics

1. **Time to First Working Example**: < 5 minutes
2. **API Documentation Coverage**: 100% of public methods
3. **Example Coverage**: At least 4 progressive examples
4. **Test Coverage**: > 80% for core functionality
5. **Type Hint Coverage**: 100% of public API

### Qualitative Metrics

1. **Developer Feedback**: "Easy to integrate"
2. **Issue Tracker**: < 10% "how do I...?" questions
3. **StackOverflow**: Clear, correct answers to common questions
4. **Adoption**: Other VFWidgets apps use it

### Comparison Benchmarks

**Compared to "DIY QAction" approach:**
- Setup time: 5 min vs 30 min (6x faster)
- Lines of code: 10 vs 50 (5x less code)
- Features: Customizable, persistent (vs hardcoded)

**Compared to other keybinding libraries:**
- Better Qt integration than generic solutions
- Better docs than most Qt-specific solutions
- Better DX than rolling your own

---

## Comparison with Other Libraries

### Qt Built-in (QAction/QShortcut)

| Feature | Qt Built-in | KeybindingManager |
|---------|-------------|-------------------|
| Shortcuts work | ✅ | ✅ |
| User customizable | ❌ | ✅ |
| Persistence | ❌ | ✅ |
| Conflict detection | ❌ | ✅ |
| UI for editing | ❌ | ✅ |
| DX | ⚠️ Manual | ✅ Automated |

### Custom Solutions (DIY)

| Feature | DIY | KeybindingManager |
|---------|-----|-------------------|
| Full control | ✅ | ⚠️ Some abstraction |
| Maintenance | ❌ Your burden | ✅ We maintain |
| Documentation | ❌ None | ✅ Comprehensive |
| Testing | ❌ Your task | ✅ Provided |
| Time to implement | ❌ Hours/days | ✅ Minutes |

---

## References

- Qt Documentation: https://doc.qt.io/qt-6/qaction.html
- Keep a Changelog: https://keepachangelog.com/
- Semantic Versioning: https://semver.org/
- Type Hints (PEP 484): https://www.python.org/dev/peps/pep-0484/
- VS Code Keybindings (inspiration): https://code.visualstudio.com/docs/getstarted/keybindings

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2025-10-03 | Initial DX plan created |
