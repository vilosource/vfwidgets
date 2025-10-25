---
name: testing-standards
description: Enforce evidence-based testing with actual terminal output, exit codes, and pytest-qt best practices. Use when running tests, verifying implementations, or validating changes.
allowed-tools:
  - Bash
  - Read
  - Grep
---

# Testing Standards Skill

When the user asks to run tests or verify implementation, follow these evidence-based testing standards. **Show actual output, not descriptions.**

## Core Principle: Evidence-Based Execution

**NEVER** say "tests passed" or "successfully executed" without showing actual proof.

❌ **WRONG**:
```
The tests ran successfully and all passed.
```

✅ **CORRECT**:
```
Running pytest...

============================= test session starts ==============================
platform linux -- Python 3.11.0, pytest-7.4.0
collected 15 items

tests/test_widget.py ...............                                     [100%]

============================== 15 passed in 0.45s ===============================

Exit code: 0 ✅
```

## 1. Always Show Exit Codes

Every command execution must show the exit code:

```bash
# Run command and show exit code
pytest tests/
echo "Exit code: $?"
```

**Exit code meanings**:
- `0` = Success ✅
- `1` = Tests failed ❌
- `2` = Test execution error (syntax error, import failure) ❌
- `5` = No tests collected ⚠️

## 2. Running Tests with pytest

### Basic Test Execution

```bash
# From widget directory - show full output
pytest tests/ -v

# Check exit code
echo "Exit code: $?"
```

### With Coverage Reporting

```bash
# Run with coverage
pytest tests/ --cov=vfwidgets_<name> --cov-report=term-missing

# Exit code indicates success/failure
echo "Exit code: $?"
```

### Running Specific Tests

```bash
# Single test file
pytest tests/test_widget.py -v

# Single test function
pytest tests/test_widget.py::test_widget_creation -v

# Tests matching pattern
pytest tests/ -k "theme" -v
```

## 3. Verify Import Works

Before running tests, verify the package can be imported:

```bash
# Test import - show actual output
python -c "from vfwidgets_<name> import <WidgetClass>; print('✅ Import successful')"

# Show exit code
echo "Exit code: $?"
```

**Expected output**:
```
✅ Import successful
Exit code: 0
```

If import fails, show the actual error:
```
Traceback (most recent call last):
  File "<string>", line 1, in <module>
ModuleNotFoundError: No module named 'vfwidgets_<name>'
Exit code: 1
```

## 4. Running Examples as Integration Tests

Examples must run successfully:

```bash
# Run example - show actual output and exit code
timeout 5s python examples/01_basic_usage.py &
EXAMPLE_PID=$!
sleep 2
kill $EXAMPLE_PID 2>/dev/null
echo "Example started successfully, Exit code: $?"
```

For headless testing (CI/CD):
```bash
# Use xvfb for headless execution
xvfb-run python examples/01_basic_usage.py
echo "Exit code: $?"
```

## 5. pytest-qt Testing Patterns

### Using qtbot Fixture

```python
def test_widget_interaction(qtbot):
    """Test widget interaction using qtbot."""
    widget = MyWidget()
    qtbot.addWidget(widget)  # Auto-cleanup after test

    # Simulate click
    qtbot.mouseClick(widget.button, Qt.LeftButton)

    # Wait for signal
    with qtbot.waitSignal(widget.value_changed, timeout=1000):
        widget.button.click()
```

### Testing Signals

```python
def test_signal_emission(qtbot):
    """Test signal is emitted correctly."""
    widget = MyWidget()

    # Capture signal emissions
    with qtbot.waitSignal(widget.value_changed) as blocker:
        widget.set_value(42)

    # Verify signal arguments
    assert blocker.args == [42]
```

### Testing Async Operations

```python
def test_async_operation(qtbot):
    """Test async operation completes."""
    widget = MyWidget()

    # Wait for callback
    with qtbot.waitCallback() as callback:
        widget.load_data(callback)

    # Verify result
    assert callback.args[0] == expected_data
```

## 6. Code Quality Checks

Always run code quality tools and show actual output:

### Black Formatting

```bash
# Check formatting - show actual output
black --check src/
echo "Exit code: $?"

# Auto-format if needed
black src/
echo "Exit code: $?"
```

### Ruff Linting

```bash
# Run linter - show actual violations
ruff check src/
echo "Exit code: $?"

# Show what will be fixed
ruff check src/ --fix --diff
```

### MyPy Type Checking

```bash
# Run type checker - show actual errors
mypy src/
echo "Exit code: $?"
```

## 7. Full Test Suite Execution

When running complete validation, execute all checks:

```bash
# 1. Format check
echo "=== Checking code formatting ==="
black --check src/
BLACK_EXIT=$?

# 2. Linting
echo "=== Running linter ==="
ruff check src/
RUFF_EXIT=$?

# 3. Type checking
echo "=== Type checking ==="
mypy src/
MYPY_EXIT=$?

# 4. Unit tests
echo "=== Running unit tests ==="
pytest tests/ -v --cov=vfwidgets_<name> --cov-report=term-missing
PYTEST_EXIT=$?

# 5. Example verification
echo "=== Verifying examples run ==="
python -c "from vfwidgets_<name> import <Widget>; print('✅ Import works')"
IMPORT_EXIT=$?

# Show summary
echo "=== Test Summary ==="
echo "Black: $BLACK_EXIT"
echo "Ruff: $RUFF_EXIT"
echo "MyPy: $MYPY_EXIT"
echo "Pytest: $PYTEST_EXIT"
echo "Import: $IMPORT_EXIT"

# Overall status
if [ $BLACK_EXIT -eq 0 ] && [ $RUFF_EXIT -eq 0 ] && [ $MYPY_EXIT -eq 0 ] && [ $PYTEST_EXIT -eq 0 ] && [ $IMPORT_EXIT -eq 0 ]; then
    echo "✅ All checks passed"
    exit 0
else
    echo "❌ Some checks failed"
    exit 1
fi
```

## 8. Test Output Interpretation

### Pytest Success Output

```
============================= test session starts ==============================
collected 15 items

tests/test_widget.py ...............                                     [100%]

============================== 15 passed in 0.45s ===============================
```

**Interpretation**: All 15 tests passed ✅

### Pytest Failure Output

```
============================= test session starts ==============================
collected 15 items

tests/test_widget.py ..F............                                     [100%]

=================================== FAILURES ===================================
_______________________________ test_widget_value ______________________________

    def test_widget_value():
>       assert widget.value == 42
E       assert 0 == 42

tests/test_widget.py:23: AssertionError
=========================== short test summary info ============================
FAILED tests/test_widget.py::test_widget_value - assert 0 == 42
========================= 1 failed, 14 passed in 0.52s =========================
```

**Interpretation**: 1 test failed, 14 passed ❌

### Coverage Report

```
---------- coverage: platform linux, python 3.11.0 -----------
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
src/vfwidgets_widget/widget.py      145      8    94%   23-24, 56-58, 102
src/vfwidgets_widget/__init__.py      3      0   100%
---------------------------------------------------------------
TOTAL                               148      8    94%
```

**Interpretation**: 94% coverage, missing lines identified

## 9. Common Testing Mistakes

### ❌ Mistake 1: Not Showing Actual Output

```
"I ran the tests and they all passed."
```

**Why wrong**: No proof of execution

**Correct approach**: Show actual pytest output with exit codes

### ❌ Mistake 2: Ignoring Non-Zero Exit Codes

```
pytest tests/
# (exits with code 1, but not acknowledged)
"Tests completed"
```

**Why wrong**: Exit code 1 means failure

**Correct approach**: Check and report exit code

### ❌ Mistake 3: Not Testing Examples

```
"Tests pass, implementation is complete"
```

**Why wrong**: Examples might not run even if unit tests pass

**Correct approach**: Verify examples run successfully

## 10. CI/CD Testing Pattern

For headless test execution (GitHub Actions, etc.):

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests with xvfb (headless X server)
xvfb-run pytest tests/ --cov=vfwidgets_<name> --cov-report=xml

# Check exit code
if [ $? -eq 0 ]; then
    echo "✅ Tests passed in CI"
else
    echo "❌ Tests failed in CI"
    exit 1
fi
```

## 11. Test File Organization

Organize tests by type:

```
tests/
├── unit/                    # Unit tests (isolated)
│   ├── test_widget.py
│   └── test_model.py
├── integration/             # Integration tests (multiple components)
│   ├── test_widget_integration.py
│   └── test_theme_integration.py
└── conftest.py             # Shared fixtures
```

### conftest.py Example

```python
"""Shared test fixtures."""

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    """Provide QApplication instance for all tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()
```

## 12. Benchmarking (Optional)

For performance-critical widgets:

```bash
# Run benchmark tests
pytest tests/benchmark/ --benchmark-only

# Show actual benchmark results
echo "Exit code: $?"
```

## Documentation Reference

For detailed testing guidance:
- **Task-driven development**: `docs/task-driven-development-GUIDE.md`
- **Widget development**: `docs/widget-development-GUIDE.md`

## Testing Checklist

Before marking testing as complete:

- [ ] All unit tests pass (exit code 0)
- [ ] Code coverage > 80%
- [ ] Examples run successfully
- [ ] Import verification successful
- [ ] Black formatting passes
- [ ] Ruff linting passes (or violations addressed)
- [ ] MyPy type checking passes (or errors justified)
- [ ] **All outputs shown with actual terminal output**
- [ ] **All exit codes verified and reported**
- [ ] No "successfully executed" without proof
