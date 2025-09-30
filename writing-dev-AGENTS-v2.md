# Writing Development Agents - Lessons Learned (Version 2)

This document captures critical lessons learned when writing development agents that implement code through step-by-step task execution. **Version 2 incorporates lessons from the VFWidgets theme system failure.**

## 🚨 CRITICAL: The #1 Rule Above All Others

**SHOW THE ACTUAL OUTPUT OR IT DIDN'T HAPPEN**

```bash
# ❌ NEVER ACCEPT THIS:
"✅ Example executed successfully"

# ✅ ONLY ACCEPT THIS:
$ python example.py
Theme changed to: dark
Widget background: #2d2d2d
Exit code: 0
```

## Core Principles (UPDATED)

### 1. Proof-of-Execution Development
**Old Rule:** "Examples must be executed immediately"
**NEW Rule:** "Show the actual terminal output of execution, including error messages, or the task is incomplete"

**Implementation:**
```markdown
## Task Completion Evidence
```bash
$ python examples/01_basic_widget.py
Creating themed application...
Widget registered: TestWidget
Theme changed: dark
Background color: #2d2d2d
Exit code: 0
```
```

**Why:** Agents can claim execution without actually running code. Require proof.

### 2. Start-from-User Development
**Old Rule:** "Integration-first development"
**NEW Rule:** "Start from the simplest user code and work backwards"

**Implementation:**
```python
# BEFORE implementing ANYTHING, this must work:
def test_minimum_viable_feature():
    """This is what the user wants to do"""
    app = ThemedApplication()
    widget = ThemedWidget()
    app.set_theme('dark')
    assert widget.background == 'dark_color'  # Must actually work

# Only AFTER this works, add complexity
```

**Why:** We built 40 tasks before checking if the basic use case worked.

### 3. Reality-Check Driven Development
**NEW Rule:** "Every 3rd task must include a reality check: run the simplest possible user scenario"

**Reality Check Template:**
```python
# reality_check.py - Must run every 3 tasks
from your_package import MainClass

obj = MainClass()
result = obj.primary_method()
print(f"Reality check: {result}")
assert result is not None, "Basic functionality broken!"
```

## Task Execution Requirements (ENHANCED)

### Mandatory Execution Evidence
Each task MUST provide:

```markdown
## Task X: Implementation

### Code Written
[show the actual code]

### Execution Evidence
```bash
# Running unit tests
$ pytest tests/test_task_x.py -v
test_basic_functionality ... PASSED
test_error_handling ... PASSED

# Running integration test
$ python tests/integration/test_with_previous.py
Connecting to Task X-1 component... OK
Testing integration... OK

# Running example
$ python examples/task_x_example.py
[ACTUAL OUTPUT HERE - NOT SIMULATED]
Output line 1...
Output line 2...
Exit code: 0
```

### Living Example Output
```bash
$ python examples/living_example.py
Phase 1: ✓ Working
Phase 2: ✓ Working
Phase 3: ✓ Working
Current task: ✓ Integrated
```
```

### ❌ Automatic Task Failure Conditions
A task automatically FAILS if:
- No execution output is shown
- Output is described but not displayed
- Exit codes are not checked
- Errors are hidden or summarized
- "Successfully executed" without showing output

## API Reality Validation

### NEW: API Contract Lock
**Rule:** "Once an API is used in an example, it's locked. Any change is a breaking change."

```python
# api_contracts.py - Generated from first usage
class APIContract:
    """These methods MUST exist because examples use them"""

    # From example_01.py line 23
    ThemedApplication.set_theme: Callable[[str], None]

    # From example_02.py line 45
    ThemedWidget.theme: property

    # From example_03.py line 12
    ThemeManager.current_theme: property  # NOT get_current_theme()!
```

### NEW: Import Reality Check
**Rule:** "The agent must show successful imports before claiming completion"

```bash
$ python -c "from vfwidgets_theme import ThemedWidget, ThemedApplication; print('✓ Imports work')"
✓ Imports work
Exit code: 0
```

## Common Failure Patterns (FROM REAL FAILURES)

### 1. The PyQt/PySide Confusion
**What happened:**
```python
from PySide6.QtCore import pyqtSignal  # WRONG - doesn't exist
```

**Prevention:**
```python
# Framework check at task start
$ python -c "from PySide6.QtCore import Signal; print(f'Using PySide6, Signal={Signal}')"
```

### 2. The Missing Method Assumption
**What happened:**
```python
theme_manager.get_instance()  # Assumed singleton pattern
# Reality: No such method exists
```

**Prevention:**
```python
# API discovery before use
$ python -c "
from package import ThemeManager
print(dir(ThemeManager))  # Show ACTUAL methods
"
```

### 3. The Signal Connection Failure
**What happened:**
```python
manager.theme_changed.connect(...)  # Signal doesn't exist
# Silent failure, no theme updates
```

**Prevention:**
```python
# Verify signals exist and connect
signal = getattr(manager, 'theme_changed', None)
assert signal is not None, "Signal doesn't exist!"
signal.connect(callback)
print(f"✓ Signal connected: {signal}")
```

### 4. The Mapping Mismatch
**What happened:**
```python
theme_config = {'bg': 'window.background'}  # Maps to non-existent property
```

**Prevention:**
```python
# Validate mapping targets exist
for key, path in theme_config.items():
    value = resolve_path(theme, path)
    assert value is not None, f"Path {path} doesn't exist in theme!"
```

## Development Methodology Updates

### NEW: Execution-First Task Structure

```markdown
## Task X: [Name]

### 1. Minimal Test Case (WRITE FIRST)
```python
def test_this_task_works():
    component = Component()
    result = component.do_thing()
    assert result == expected
```

### 2. Run Test (BEFORE IMPLEMENTATION)
```bash
$ python test_minimal.py
Error: Component doesn't exist yet
```

### 3. Implementation
[Now implement to make test pass]

### 4. Run Test Again (AFTER IMPLEMENTATION)
```bash
$ python test_minimal.py
✓ Test passes
```

### 5. Integration Check
```bash
$ python previous_examples.py
✓ Still working
```
```

### NEW: The Three-Layer Validation

1. **Unit Layer** - Component works alone
2. **Integration Layer** - Component works with others
3. **User Layer** - User can actually use it

```python
# ALL THREE must pass:
assert unit_tests_pass()         # Layer 1
assert integration_tests_pass()  # Layer 2
assert user_can_use_it()        # Layer 3 - MOST IMPORTANT
```

## Agent Instructions Template (UPDATED)

```markdown
## Critical Development Rules for Agents

### EXECUTION REQUIREMENTS
1. **SHOW OUTPUT OR IT DIDN'T HAPPEN** - Display actual terminal output, not descriptions
2. **EXIT CODES MATTER** - Show exit code after every execution
3. **ERRORS ARE GOLD** - Show full error messages, don't summarize
4. **IMPORTS FIRST** - Verify imports work before claiming completion

### INTEGRATION REQUIREMENTS
1. **User story first** - Start with simplest user code, work backwards
2. **Reality check every 3 tasks** - Run basic user scenario
3. **API contracts are sacred** - Once used in example, cannot change
4. **Previous examples must still run** - Zero regressions

### VALIDATION GATES
- Task incomplete until output is shown
- Integration checkpoint every 3 tasks
- Phase gate: ALL examples must run
- Final gate: New user can use the system

### FAILURE PROTOCOL
When something doesn't work:
1. SHOW THE ERROR (complete error, not summary)
2. DIAGNOSE (run diagnostic commands)
3. FIX (show the fix)
4. VERIFY (run again, show it working)
5. PREVENT (add test to prevent regression)

### Example of Acceptable Task Completion

✅ GOOD:
```bash
$ python example.py
Starting application...
Theme loaded: dark
Widget created with theme
Result: SUCCESS
Exit code: 0
```

❌ BAD:
"Executed example.py successfully"
```

## Validation Code for Agents

```python
def validate_task_with_evidence(task_num: int) -> bool:
    """Task validation with execution evidence."""

    print(f"\n=== Validating Task {task_num} ===")

    # 1. Show unit test execution
    print("\n1. Running unit tests:")
    result = subprocess.run(
        [sys.executable, f"tests/test_task_{task_num}.py"],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"❌ Unit tests failed:\n{result.stderr}")
        return False

    # 2. Show integration test execution
    print("\n2. Running integration test:")
    result = subprocess.run(
        [sys.executable, f"tests/integration/test_task_{task_num}.py"],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"❌ Integration failed:\n{result.stderr}")
        return False

    # 3. Show example execution
    print("\n3. Running example:")
    result = subprocess.run(
        [sys.executable, f"examples/task_{task_num}_example.py"],
        capture_output=True, text=True
    )
    print(result.stdout)
    print(f"Exit code: {result.returncode}")
    if result.returncode != 0:
        print(f"❌ Example failed:\n{result.stderr}")
        return False

    # 4. Reality check - basic user scenario
    print("\n4. Reality check:")
    result = subprocess.run(
        [sys.executable, "-c", """
from my_package import MainAPI
api = MainAPI()
print(f"Basic functionality: {api.basic_method()}")
"""],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"❌ Reality check failed:\n{result.stderr}")
        return False

    print(f"\n✅ Task {task_num} validated with evidence")
    return True
```

## The Ultimate Test

Before ANY agent claims phase/project completion:

```python
# ultimate_test.py - Must work for new users
"""
This is what a new user would write after reading the docs.
If this doesn't work, the project isn't done.
"""

from your_package import YourMainClass

# The most basic use case
thing = YourMainClass()
result = thing.do_the_main_thing()
print(f"Did it work? {result}")

# The second most common use case
thing.configure(some_option=True)
result2 = thing.do_another_thing()
print(f"Did that work? {result2}")

# Error handling
try:
    thing.do_invalid_thing()
except YourException as e:
    print(f"Error handling works: {e}")

print("✅ Package is actually usable!")
```

## Summary of Changes

### What's Different in V2

1. **Execution Evidence Required** - Output must be shown, not described
2. **User-First Development** - Start from user code, not architecture
3. **Reality Checks** - Regular validation that basics still work
4. **API Contract Locking** - Used APIs cannot change
5. **Import Verification** - Imports must be tested
6. **Error Visibility** - Full errors shown, not hidden
7. **Exit Code Tracking** - Every execution shows exit code

### The Core Lesson

**"Working software" means software that ACTUALLY RUNS when a user tries the examples.**

Not software that has tests, not software with documentation, not software with beautiful architecture - software that executes successfully when someone types `python example.py`.

### The New Mantra

> "Show the output or it didn't happen.
> Run the example or it's not done.
> Check the exit code or it's not real.
> Test the imports or it won't work."

## Final Note

The difference between development theater and real development is execution. Agents must be forced to show real execution output, not simulate it. This document exists because we learned this lesson the hard way.

Remember: **The computer doesn't lie. Either the code runs or it doesn't. Show us which.**