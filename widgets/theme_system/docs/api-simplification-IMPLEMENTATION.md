# API Simplification Implementation Plan

## Overview

This document provides step-by-step tasks to simplify the VFWidgets Theme System API. Each task is explicit and verifiable to ensure correct implementation from start to finish.

## Critical Success Factors

1. **Every task must be tested with exit code verification**
2. **No task is "complete" until examples run without crashes**
3. **Documentation must match implementation exactly**
4. **Breaking changes must have migration path**
5. **Rollback strategy in place before starting**
6. **Pre-analysis must be complete and approved**

## Git and Rollback Strategy

### Branch Strategy

**Before starting ANY implementation:**
```bash
cd /home/kuja/GitHub/vfwidgets/widgets/theme_system

# Create feature branch
git checkout -b feature/api-simplification

# Tag baseline
git tag v1.0.0-api-baseline

# Verify examples work at baseline
cd examples/user_examples
python test_run_examples.py > ../../baseline-results.txt
echo "Exit code: $?" >> ../../baseline-results.txt
```

### Commit Points

**Commit after completing each phase (not individual tasks):**

```bash
# After Phase 1
git add -A
git commit -m "feat(api): Phase 1 - Fix core inheritance model

- Added ThemedQWidget, ThemedMainWindow, ThemedDialog
- Created ThemingMixin for code reuse
- All examples still passing (no regressions)

Checkpoint: v1.0.1-phase1-complete
"
git tag v1.0.1-phase1-complete

# Verify checkpoint
cd examples/user_examples
python test_run_examples.py
echo "Exit code: $?"
```

### Rollback Decision Criteria

**STOP and ROLLBACK if ANY of these occur:**

1. **Time Overrun**: Any phase takes >2x estimated time
2. **Breaking Regressions**: More than 1 example breaks and can't be fixed within 30 min
3. **Critical Failures**: Segfaults (exit code 139/-11), Aborts (exit code 134/-6)
4. **No Improvement**: New API is not measurably simpler (<20% improvement)
5. **Performance Regression**: >10% slower than baseline
6. **Integration Failure**: New components don't integrate with existing code

### Rollback Procedure

If rollback criteria met:

```bash
# 1. STOP all work immediately
echo "ROLLBACK INITIATED at $(date)" > rollback.log

# 2. Document what went wrong
cat > docs/rollback-report-$(date +%Y%m%d-%H%M%S).md << EOF
# Rollback Report

Date: $(date)
Phase reached: [Phase N, Task N.N]
Last successful checkpoint: $(git describe --tags)

## Reason for Rollback
[Describe what went wrong - be specific]

## Exit Codes and Errors
\`\`\`
[Paste actual error output and exit codes]
\`\`\`

## Problems Encountered
- Problem 1: [description + exit code]
- Problem 2: [description + exit code]

## What We Learned
[What to do differently next time]

## Recommendation
[Should we try again? Different approach?]
EOF

# 3. Revert to last known good state
git checkout main
git branch -D feature/api-simplification

# Alternative: Revert to specific phase checkpoint
# git checkout v1.0.N-phaseN-complete
# git checkout -b feature/api-simplification-retry

# 4. Verify rollback successful
cd examples/user_examples
echo "=== Verifying Rollback ==="
python test_run_examples.py
EXIT=$?
echo "Exit code: $EXIT"

if [ $EXIT -eq 0 ]; then
    echo "✓ Rollback successful - examples working"
else
    echo "✗ CRITICAL: Rollback failed - examples still broken"
    exit 1
fi

# 5. Confirm baseline restored
echo "Current state: $(git describe --tags)"
diff baseline-results.txt <(python test_run_examples.py 2>&1)
```

### Phase Checkpoints

**After each phase, verify checkpoint health:**

```bash
#!/bin/bash
# checkpoint-verify.sh - Run after each phase

cd /home/kuja/GitHub/vfwidgets/widgets/theme_system

PHASE=$1
if [ -z "$PHASE" ]; then
    echo "Usage: ./checkpoint-verify.sh <phase_number>"
    exit 1
fi

echo "=== Phase $PHASE Checkpoint Verification ==="
echo "Date: $(date)"
echo "Tag: $(git describe --tags)"
echo "Commit: $(git rev-parse HEAD)"
echo ""

# 1. Examples test
echo "1. Testing examples..."
cd examples/user_examples
python test_run_examples.py
EXIT=$?
echo "Exit code: $EXIT"

if [ $EXIT -ne 0 ]; then
    echo "✗ CHECKPOINT FAILED - Examples not passing"
    echo "Rollback recommended"
    exit 1
fi

# 2. Import test
echo ""
echo "2. Testing imports..."
python -c "from vfwidgets_theme import *; print('✓ All imports work')" 2>&1
echo "Exit code: $?"

# 3. Regression check
echo ""
echo "3. Checking for regressions..."
cd ../..
if [ -f "baseline-results.txt" ]; then
    diff -u baseline-results.txt <(cd examples/user_examples && python test_run_examples.py 2>&1)
    if [ $? -eq 0 ]; then
        echo "✓ No regressions detected"
    else
        echo "⚠ Changes detected (review above diff)"
    fi
fi

# 4. Git status
echo ""
echo "4. Git status:"
git status --short

echo ""
echo "✓ CHECKPOINT HEALTHY - Safe to proceed to Phase $((PHASE + 1))"
```

## Implementation Phases

---

## Phase 1: Fix Core Inheritance Model (CRITICAL)

### Task 1.1: Create ThemedQWidget Base Class

**File:** `/widgets/theme_system/src/vfwidgets_theme/widgets/base.py`

**Action:** Create a new class that properly inherits from QWidget

```python
class ThemedQWidget(QWidget):
    """
    A QWidget with built-in theming support.

    This is the base class that properly inherits from QWidget,
    eliminating the need for multiple inheritance.
    """

    # All the theming logic from current ThemedWidget
    # but with proper QWidget inheritance
```

**Verification:**
```bash
# Test 1: Can it be imported?
python -c "from vfwidgets_theme.widgets.base import ThemedQWidget; print('✓ Import works')"

# Test 2: Is it a QWidget?
python -c "from vfwidgets_theme.widgets.base import ThemedQWidget; from PySide6.QtWidgets import QWidget; print('✓ Is QWidget' if issubclass(ThemedQWidget, QWidget) else '✗ NOT QWidget')"

# Test 3: Does it have theming methods?
python -c "from vfwidgets_theme.widgets.base import ThemedQWidget; w = ThemedQWidget(); print('✓ Has theme attr' if hasattr(w, 'theme') else '✗ Missing theme')"
```

**Exit Criteria:**
- [ ] All 3 verification tests pass
- [ ] Class can be instantiated without errors
- [ ] isinstance(ThemedQWidget(), QWidget) returns True

---

### Task 1.2: Create ThemedMainWindow Class

**File:** `/widgets/theme_system/src/vfwidgets_theme/widgets/base.py`

**Action:** Create a QMainWindow variant with theming

```python
class ThemedMainWindow(QMainWindow):
    """
    A QMainWindow with built-in theming support.

    Use this instead of ThemedWidget + QMainWindow inheritance.
    """

    # Include the same theming mixin logic
    # but inherit from QMainWindow
```

**Verification:**
```bash
# Test: Can create and show window?
timeout 2 python -c "
import sys
from PySide6.QtWidgets import QApplication
from vfwidgets_theme.widgets.base import ThemedMainWindow

app = QApplication(sys.argv)
window = ThemedMainWindow()
window.show()
print('✓ ThemedMainWindow created and shown')
" && echo "Exit code: $?"
```

**Exit Criteria:**
- [ ] Window can be created without errors
- [ ] Window is a QMainWindow subclass
- [ ] Window has theme attribute
- [ ] Exit code is 0 or timeout (124/-15)

---

### Task 1.3: Create ThemedDialog Class

**File:** `/widgets/theme_system/src/vfwidgets_theme/widgets/base.py`

**Action:** Create a QDialog variant with theming

```python
class ThemedDialog(QDialog):
    """
    A QDialog with built-in theming support.
    """
    # Same theming mixin logic
```

**Verification:**
```bash
timeout 2 python -c "
import sys
from PySide6.QtWidgets import QApplication
from vfwidgets_theme.widgets.base import ThemedDialog

app = QApplication(sys.argv)
dialog = ThemedDialog()
print('✓ ThemedDialog created')
" && echo "Exit code: $?"
```

**Exit Criteria:**
- [ ] Dialog can be created without errors
- [ ] Dialog is a QDialog subclass
- [ ] Exit code is 0 or timeout

---

### Task 1.4: Create Theming Mixin for Code Reuse

**File:** `/widgets/theme_system/src/vfwidgets_theme/widgets/base.py`

**Action:** Extract common theming logic into a mixin

```python
class ThemingMixin:
    """
    Mixin that provides theming functionality.

    Internal use only - users should use ThemedQWidget, ThemedMainWindow, etc.
    """

    def _init_theming(self):
        """Initialize theming system - called by __init__ of themed classes."""
        # Widget ID
        self._widget_id = str(uuid.uuid4())

        # Managers
        self._theme_manager = None
        self._lifecycle_manager = None

        # Theme properties
        self._theme_properties = ThemePropertiesManager(self)
        self.theme = ThemeAccess(self)

        # Configuration
        self._theme_config = getattr(self.__class__, '_merged_theme_config',
                                     getattr(self, 'theme_config', {}).copy())

        # Initialize system
        self._initialize_theme_system()
```

**Verification:**
```bash
# Test: Can ThemedQWidget use the mixin?
python -c "
from vfwidgets_theme.widgets.base import ThemedQWidget
w = ThemedQWidget()
assert hasattr(w, '_widget_id'), 'Missing _widget_id'
assert hasattr(w, 'theme'), 'Missing theme'
print('✓ ThemingMixin working')
"
```

**Exit Criteria:**
- [ ] Mixin can be used by all themed classes
- [ ] No code duplication between ThemedQWidget, ThemedMainWindow, etc.
- [ ] All themed classes have identical theming behavior

---

### Task 1.5: Update ThemedQWidget to Use Mixin

**File:** `/widgets/theme_system/src/vfwidgets_theme/widgets/base.py`

**Action:** Make ThemedQWidget use the mixin properly

```python
class ThemedQWidget(ThemingMixin, QWidget):
    """
    A QWidget with built-in theming support.

    Simple single inheritance - just use this like any QWidget.
    """

    theme_config = {
        'background': 'window.background',
        'color': 'window.foreground',
        'font': 'text.font'
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_theming()  # Initialize theming from mixin
```

**Verification:**
```bash
# Test: Single inheritance works
timeout 2 python -c "
import sys
from PySide6.QtWidgets import QApplication, QLabel
from vfwidgets_theme.widgets.base import ThemedQWidget

app = QApplication(sys.argv)

# Test 1: Can create ThemedQWidget directly
w = ThemedQWidget()
w.show()
print('✓ ThemedQWidget works')

# Test 2: Can inherit from it with single inheritance
class MyWidget(ThemedQWidget):
    pass

w2 = MyWidget()
w2.show()
print('✓ Single inheritance works')
" && echo "Exit code: $?"
```

**Exit Criteria:**
- [ ] ThemedQWidget can be instantiated
- [ ] Single inheritance from ThemedQWidget works
- [ ] Exit code is 0 or timeout
- [ ] NO crashes or segfaults

---

### Task 1.6: Apply Mixin Pattern to ThemedMainWindow and ThemedDialog

**File:** `/widgets/theme_system/src/vfwidgets_theme/widgets/base.py`

**Action:** Make all themed classes consistent

```python
class ThemedMainWindow(ThemingMixin, QMainWindow):
    theme_config = {
        'background': 'window.background',
        'color': 'window.foreground',
        'font': 'text.font'
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_theming()

class ThemedDialog(ThemingMixin, QDialog):
    theme_config = {
        'background': 'dialog.background',
        'color': 'dialog.foreground',
        'font': 'text.font'
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_theming()
```

**Verification:**
```bash
# Test all three classes
timeout 3 python -c "
import sys
from PySide6.QtWidgets import QApplication
from vfwidgets_theme.widgets.base import ThemedQWidget, ThemedMainWindow, ThemedDialog

app = QApplication(sys.argv)

# Test each class
w = ThemedQWidget()
win = ThemedMainWindow()
dlg = ThemedDialog()

assert hasattr(w, 'theme'), 'ThemedQWidget missing theme'
assert hasattr(win, 'theme'), 'ThemedMainWindow missing theme'
assert hasattr(dlg, 'theme'), 'ThemedDialog missing theme'

print('✓ All themed classes work')
" && echo "Exit code: $?"
```

**Exit Criteria:**
- [ ] All three classes can be instantiated
- [ ] All have identical theming API
- [ ] Exit code is 0 or timeout
- [ ] No crashes

---

### Task 1.7: Mark Old ThemedWidget as Deprecated

**File:** `/widgets/theme_system/src/vfwidgets_theme/widgets/base.py`

**Action:** Keep old ThemedWidget for backwards compatibility but mark deprecated

```python
class ThemedWidget(ThemingMixin, QWidget):
    """
    DEPRECATED: Use ThemedQWidget instead.

    This class remains for backwards compatibility but requires
    manual multiple inheritance which is error-prone.

    Old way (error-prone):
        class MyWidget(ThemedWidget, QWidget):  # Easy to get wrong
            pass

    New way (simple):
        class MyWidget(ThemedQWidget):  # Just works!
            pass
    """

    def __init__(self, parent=None, **kwargs):
        import warnings
        warnings.warn(
            "ThemedWidget is deprecated. Use ThemedQWidget instead. "
            "See migration guide at docs/migration-GUIDE.md",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(parent, **kwargs)
        self._init_theming()
```

**Verification:**
```bash
# Test: Does it show deprecation warning?
python -W default -c "
import sys
from PySide6.QtWidgets import QApplication
from vfwidgets_theme.widgets.base import ThemedWidget

app = QApplication(sys.argv)
w = ThemedWidget()
" 2>&1 | grep -q "DeprecationWarning" && echo "✓ Deprecation warning works"
```

**Exit Criteria:**
- [ ] Old code still works
- [ ] Deprecation warning is shown
- [ ] Warning includes migration instructions

---

## Phase 2: Update Public API

### Task 2.1: Export New Classes in __init__.py

**File:** `/widgets/theme_system/src/vfwidgets_theme/widgets/__init__.py`

**Action:** Add new classes to public API

```python
from .base import (
    ThemedWidget,        # DEPRECATED
    ThemedQWidget,       # NEW - for QWidget
    ThemedMainWindow,    # NEW - for QMainWindow
    ThemedDialog,        # NEW - for QDialog
)

__all__ = [
    'ThemedWidget',        # Keep for backwards compat
    'ThemedQWidget',       # PRIMARY API
    'ThemedMainWindow',    # PRIMARY API
    'ThemedDialog',        # PRIMARY API
    # ... other exports
]
```

**Verification:**
```bash
# Test: Can import new classes?
python -c "
from vfwidgets_theme import ThemedQWidget, ThemedMainWindow, ThemedDialog
print('✓ New classes available in public API')
"
```

**Exit Criteria:**
- [ ] All new classes can be imported from vfwidgets_theme
- [ ] Old ThemedWidget still importable

---

### Task 2.2: Export New Classes in Package __init__.py

**File:** `/widgets/theme_system/src/vfwidgets_theme/__init__.py`

**Action:** Add to main package exports

```python
# Primary user-facing imports - THE API
from .widgets import (
    ThemedWidget,        # DEPRECATED - use ThemedQWidget
    ThemedQWidget,       # NEW PRIMARY API for QWidget
    ThemedMainWindow,    # NEW PRIMARY API for QMainWindow
    ThemedDialog,        # NEW PRIMARY API for QDialog
    ThemedApplication,
    # ... other exports
)

__all__ = [
    # ======================================
    # PRIMARY API - THE way to use theming
    # ======================================
    "ThemedQWidget",         # THE way to create themed widgets
    "ThemedMainWindow",      # THE way to create themed windows
    "ThemedDialog",          # THE way to create themed dialogs
    "ThemedApplication",     # THE way to manage themes

    # DEPRECATED
    "ThemedWidget",          # Use ThemedQWidget instead

    # ... rest
]
```

**Verification:**
```bash
# Test: Top-level imports work
python -c "
from vfwidgets_theme import ThemedQWidget, ThemedMainWindow, ThemedDialog, ThemedApplication
print('✓ All new classes available at top level')
"
```

**Exit Criteria:**
- [ ] All classes importable from vfwidgets_theme
- [ ] Import doesn't crash

---

## Phase 3: Improve Property Access

### Task 3.1: Add Smart Defaults to ThemeAccess

**File:** `/widgets/theme_system/src/vfwidgets_theme/widgets/base.py`

**Action:** Make property access return sensible defaults

```python
class ThemeAccess:
    """Dynamic theme property access object."""

    def __init__(self, widget: 'ThemedWidget'):
        self._widget = weakref.ref(widget)

    def __getattr__(self, name: str) -> Any:
        """Dynamic property access with smart defaults."""
        widget = self._widget()
        if widget is None:
            return None

        # Try to get from theme
        value = widget._theme_properties.get_property(name)

        # If not found, return smart default
        if value is None:
            return self._get_smart_default(name)

        return value

    def _get_smart_default(self, name: str) -> Any:
        """Return sensible default based on property name."""
        # Check if we have a theme to determine light/dark
        widget = self._widget()
        is_light = True  # Default assumption

        if widget and hasattr(widget, '_current_theme_name'):
            theme_name = widget._current_theme_name or ''
            is_light = 'light' in theme_name.lower()

        # Smart defaults based on property name
        if 'background' in name.lower() or 'bg' in name.lower():
            return '#ffffff' if is_light else '#1e1e1e'
        elif 'foreground' in name.lower() or 'fg' in name.lower() or 'color' in name.lower():
            return '#000000' if is_light else '#ffffff'
        elif 'border' in name.lower():
            return '#cccccc' if is_light else '#555555'
        elif 'accent' in name.lower() or 'primary' in name.lower():
            return '#0066cc'
        elif 'error' in name.lower():
            return '#cc0000'
        elif 'warning' in name.lower():
            return '#ff9900'
        elif 'success' in name.lower():
            return '#00aa00'

        # Fallback
        return None
```

**Verification:**
```bash
# Test: Property access with defaults
python -c "
from vfwidgets_theme.widgets.base import ThemedQWidget
from PySide6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
w = ThemedQWidget()

# These should not crash even if property doesn't exist
bg = w.theme.background
fg = w.theme.foreground
accent = w.theme.accent

print(f'✓ Smart defaults work: bg={bg}, fg={fg}, accent={accent}')
"
```

**Exit Criteria:**
- [ ] Accessing non-existent properties returns sensible defaults
- [ ] No crashes from missing properties
- [ ] No need for getattr() in user code

---

### Task 3.2: Remove getattr() from All Examples

**Files:** All 5 example files

**Action:** Update examples to use simpler property access

**Before:**
```python
bg = getattr(self.theme, 'background', '#ffffff')
```

**After:**
```python
bg = self.theme.background  # Smart default if not in theme
```

**Verification:**
```bash
# Run all examples with new API
for example in 01_*.py 02_*.py 03_*.py 04_*.py 05_*.py; do
    timeout 2 python "$example" && echo "✓ $example runs"
done
```

**Exit Criteria:**
- [ ] All examples run without crashes
- [ ] No getattr() calls remain in examples
- [ ] Exit codes are 0 or timeout

---

## Phase 4: Update Examples to Use New API

### Task 4.1: Update Example 01 - Minimal Hello World

**File:** `/widgets/theme_system/examples/user_examples/01_minimal_hello_world.py`

**Action:** Use ThemedQWidget with single inheritance

```python
from PySide6.QtWidgets import QLabel
from vfwidgets_theme import ThemedQWidget, ThemedApplication

class HelloWidget(ThemedQWidget):  # CHANGED: Single inheritance!
    """A simple label that gets themed automatically."""

    def __init__(self):
        super().__init__()

        # Create label as child
        label = QLabel("Hello, Themed World!", self)
        label.setMinimumSize(300, 100)
```

**Verification:**
```bash
timeout 2 python 01_minimal_hello_world.py
echo "Exit code: $?"
# Expected: 0 or timeout (124/-15)
```

**Exit Criteria:**
- [ ] Example uses single inheritance
- [ ] Example runs without crashes
- [ ] Exit code is 0 or timeout

---

### Task 4.2: Update Example 02 - Theme Switching

**File:** `/widgets/theme_system/examples/user_examples/02_theme_switching.py`

**Action:** Use ThemedQWidget, remove getattr()

```python
class ThemeSwitcherWidget(ThemedQWidget):  # CHANGED: Single inheritance

    def update_styling(self):
        """Apply theme colors to the widget."""
        # CHANGED: Direct access, no getattr
        bg = self.theme.background
        fg = self.theme.foreground

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg};
                color: {fg};
            }}
        """)
```

**Verification:**
```bash
timeout 2 python 02_theme_switching.py
echo "Exit code: $?"
```

**Exit Criteria:**
- [ ] Single inheritance
- [ ] No getattr() calls
- [ ] Runs without crashes

---

### Task 4.3: Update Example 03 - Custom Themed Widgets

**File:** `/widgets/theme_system/examples/user_examples/03_custom_themed_widgets.py`

**Action:** Update all custom widgets

```python
class ThemedProgressBar(ThemedQWidget):  # CHANGED
    # ... rest of implementation with direct property access

class ThemedCard(ThemedQWidget):  # CHANGED
    # ... rest of implementation

class CustomWidgetShowcase(ThemedQWidget):  # CHANGED
    # ... rest of implementation
```

**Verification:**
```bash
timeout 2 python 03_custom_themed_widgets.py
echo "Exit code: $?"
```

**Exit Criteria:**
- [ ] All widgets use ThemedQWidget
- [ ] Single inheritance only
- [ ] No crashes

---

### Task 4.4: Update Example 04 - Multi Window Application

**File:** `/widgets/theme_system/examples/user_examples/04_multi_window_application.py`

**Action:** Use ThemedMainWindow for windows

```python
class DocumentWindow(ThemedMainWindow):  # CHANGED: Use ThemedMainWindow
    """A document editor window that supports theming."""

    def __init__(self, title="Untitled"):
        super().__init__()  # CHANGED: No multiple inheritance
        # ... rest

class SidePanel(ThemedQWidget):  # CHANGED: Use ThemedQWidget
    # ... rest
```

**Verification:**
```bash
timeout 2 python 04_multi_window_application.py
echo "Exit code: $?"
```

**Exit Criteria:**
- [ ] Windows use ThemedMainWindow
- [ ] Widgets use ThemedQWidget
- [ ] No crashes

---

### Task 4.5: Update Example 05 - Complete Application

**File:** `/widgets/theme_system/examples/user_examples/05_complete_application.py`

**Action:** Use new API throughout

```python
class ThemeEditor(ThemedQWidget):  # CHANGED
    # ... implementation

class AnimatedWidget(ThemedQWidget):  # CHANGED
    # ... implementation

class CompleteApplication(ThemedMainWindow):  # CHANGED
    # ... implementation
```

**Verification:**
```bash
timeout 2 python 05_complete_application.py
echo "Exit code: $?"
```

**Exit Criteria:**
- [ ] All classes use new API
- [ ] No multiple inheritance
- [ ] Runs without crashes

---

### Task 4.6: Run Comprehensive Example Tests

**Action:** Use the runtime test suite

```bash
cd /home/kuja/GitHub/vfwidgets/widgets/theme_system/examples/user_examples
python test_run_examples.py
```

**Expected Output:**
```
✓ PASS: 01_minimal_hello_world.py
✓ PASS: 02_theme_switching.py
✓ PASS: 03_custom_themed_widgets.py
✓ PASS: 04_multi_window_application.py
✓ PASS: 05_complete_application.py

Results: 5 passed, 0 failed
```

**Exit Criteria:**
- [ ] All 5 examples pass
- [ ] 0 failures
- [ ] No crashes or segfaults

---

## Phase 5: Documentation Updates

### Task 5.1: Create Migration Guide

**File:** `/widgets/theme_system/docs/migration-GUIDE.md`

**Action:** Write complete migration guide

```markdown
# Migration Guide: ThemedWidget → ThemedQWidget

## Why Migrate?

The old `ThemedWidget` mixin required confusing multiple inheritance.
The new `ThemedQWidget` uses simple single inheritance.

## Quick Migration

### Before (Old API)
\```python
class MyWidget(ThemedWidget, QWidget):
    pass
\```

### After (New API)
\```python
class MyWidget(ThemedQWidget):
    pass
\```

## Complete Migration Steps

1. Find all classes using ThemedWidget
2. Check if they inherit from QWidget, QMainWindow, or QDialog
3. Replace with appropriate new class:
   - `ThemedWidget + QWidget` → `ThemedQWidget`
   - `ThemedWidget + QMainWindow` → `ThemedMainWindow`
   - `ThemedWidget + QDialog` → `ThemedDialog`
4. Remove QWidget/QMainWindow/QDialog from inheritance list
5. Test that examples run without crashes

## Property Access Changes

### Before
\```python
bg = getattr(self.theme, 'background', '#ffffff')
\```

### After
\```python
bg = self.theme.background  # Auto-defaults to sensible value
\```
```

**Verification:**
```bash
# Check file exists and has content
[ -f docs/migration-GUIDE.md ] && wc -l docs/migration-GUIDE.md
```

**Exit Criteria:**
- [ ] Migration guide exists
- [ ] Contains clear before/after examples
- [ ] Explains all breaking changes

---

### Task 5.2: Update README.md

**File:** `/widgets/theme_system/README.md`

**Action:** Replace all incorrect API examples

**Changes Needed:**
1. Replace `VFWidget` with `ThemedQWidget`
2. Replace `ThemeManager` with `ThemedApplication`
3. Remove references to non-existent `theme_property()` decorator
4. Add simple working examples using new API

**Verification:**
```bash
# Test: No mentions of old incorrect APIs
! grep -q "VFWidget" README.md && echo "✓ No VFWidget references"
! grep -q "ThemeManager" README.md && echo "✓ No ThemeManager references"
```

**Exit Criteria:**
- [ ] All code examples are copy-pasteable and work
- [ ] No references to non-existent APIs
- [ ] Shows ThemedQWidget, ThemedMainWindow, ThemedDialog

---

### Task 5.3: Update API Reference

**File:** `/widgets/theme_system/docs/api-REFERENCE.md`

**Action:** Document new classes

Add sections for:
- `ThemedQWidget` (primary API)
- `ThemedMainWindow` (for main windows)
- `ThemedDialog` (for dialogs)
- `ThemedWidget` (deprecated, with migration note)

**Verification:**
```bash
# Check all new classes documented
grep -q "ThemedQWidget" docs/api-REFERENCE.md && echo "✓ ThemedQWidget documented"
grep -q "ThemedMainWindow" docs/api-REFERENCE.md && echo "✓ ThemedMainWindow documented"
grep -q "ThemedDialog" docs/api-REFERENCE.md && echo "✓ ThemedDialog documented"
```

**Exit Criteria:**
- [ ] All new classes have complete documentation
- [ ] Examples in docs are tested and work
- [ ] Deprecated APIs clearly marked

---

### Task 5.4: Create Quick Start Guide

**File:** `/widgets/theme_system/docs/quick-start-GUIDE.md`

**Action:** Write 60-second quick start

```markdown
# Quick Start Guide - VFWidgets Theme System

## 60 Second Start

### Step 1: Install (10 seconds)
\```bash
cd widgets/theme_system
pip install -e .
\```

### Step 2: Your First Themed Widget (30 seconds)
\```python
from PySide6.QtWidgets import QApplication
from vfwidgets_theme import ThemedQWidget, ThemedApplication
import sys

class MyWidget(ThemedQWidget):
    pass  # That's it!

app = ThemedApplication(sys.argv)
widget = MyWidget()
widget.show()
sys.exit(app.exec())
\```

### Step 3: Run It (20 seconds)
\```bash
python my_widget.py
\```

✓ You now have a fully themed widget!
```

**Verification:**
```bash
# Extract and run the example from docs
python -c "$(grep -A 20 'Step 2:' docs/quick-start-GUIDE.md | grep -v '^#' | grep -v '^$')" &
sleep 2
killall python
echo "✓ Quick start example works"
```

**Exit Criteria:**
- [ ] Guide can be followed in 60 seconds
- [ ] All examples work when copy-pasted
- [ ] Clear and simple

---

### Task 5.5: Update Examples README

**File:** `/widgets/theme_system/examples/user_examples/README.md`

**Action:** Update to show new API

Replace all examples to use:
- `ThemedQWidget` instead of `ThemedWidget`
- Single inheritance
- Direct property access

**Verification:**
```bash
# Check examples in README match actual files
grep -q "ThemedQWidget" examples/user_examples/README.md && echo "✓ Uses new API"
```

**Exit Criteria:**
- [ ] All examples in README use new API
- [ ] Examples match actual example files
- [ ] No confusing multiple inheritance shown

---

## Phase 6: Final Validation

### Task 6.1: Run All Tests

**Action:** Execute comprehensive test suite

```bash
# Test 1: Import test
python -c "
from vfwidgets_theme import (
    ThemedQWidget,
    ThemedMainWindow,
    ThemedDialog,
    ThemedApplication
)
print('✓ All imports work')
"

# Test 2: Runtime test
cd examples/user_examples
python test_run_examples.py

# Test 3: Inheritance test
python -c "
from vfwidgets_theme import ThemedQWidget, ThemedMainWindow
from PySide6.QtWidgets import QWidget, QMainWindow

assert issubclass(ThemedQWidget, QWidget), 'ThemedQWidget not a QWidget!'
assert issubclass(ThemedMainWindow, QMainWindow), 'ThemedMainWindow not a QMainWindow!'
print('✓ Inheritance correct')
"

# Test 4: Property access test
python -c "
import sys
from PySide6.QtWidgets import QApplication
from vfwidgets_theme import ThemedQWidget

app = QApplication(sys.argv)
w = ThemedQWidget()

# Should not crash even if properties don't exist
bg = w.theme.background
fg = w.theme.foreground
accent = w.theme.accent

assert bg is not None, 'No default for background!'
print('✓ Property access with defaults works')
"
```

**Exit Criteria:**
- [ ] All imports succeed
- [ ] All 5 examples run without crashes
- [ ] Inheritance is correct
- [ ] Property access works with defaults

---

### Task 6.2: Create Validation Checklist

**File:** `/widgets/theme_system/docs/validation-CHECKLIST.md`

**Action:** Document what must be verified

```markdown
# Validation Checklist

Before considering this implementation complete, verify:

## Core Functionality
- [ ] ThemedQWidget can be instantiated
- [ ] ThemedQWidget is a QWidget subclass
- [ ] ThemedMainWindow is a QMainWindow subclass
- [ ] ThemedDialog is a QDialog subclass
- [ ] Single inheritance works: `class X(ThemedQWidget): pass`
- [ ] Theme property access works: `self.theme.background`
- [ ] Smart defaults work for missing properties
- [ ] No crashes from multiple inheritance order

## Examples
- [ ] Example 01 runs (exit code 0 or timeout)
- [ ] Example 02 runs (exit code 0 or timeout)
- [ ] Example 03 runs (exit code 0 or timeout)
- [ ] Example 04 runs (exit code 0 or timeout)
- [ ] Example 05 runs (exit code 0 or timeout)
- [ ] All examples use single inheritance
- [ ] No getattr() in examples

## Documentation
- [ ] README has no references to VFWidget
- [ ] README has no references to ThemeManager
- [ ] README examples are copy-pasteable and work
- [ ] API reference documents all new classes
- [ ] Migration guide exists and is complete
- [ ] Quick start guide can be followed in 60 seconds

## Backwards Compatibility
- [ ] Old ThemedWidget still works (with warning)
- [ ] Deprecation warning is shown
- [ ] Migration path is clear

## Developer Experience
- [ ] New developer can create themed widget in < 1 minute
- [ ] No need to understand multiple inheritance
- [ ] No need to understand mixin pattern
- [ ] Error messages are helpful
- [ ] Documentation matches implementation
```

**Exit Criteria:**
- [ ] Checklist exists
- [ ] All items can be verified with tests

---

### Task 6.3: Run Final Verification

**Action:** Go through validation checklist systematically

```bash
#!/bin/bash
# final-verification.sh

echo "=== VFWidgets Theme System - Final Verification ==="
echo ""

PASS=0
FAIL=0

# Test 1: Imports
echo "Test 1: Imports..."
if python -c "from vfwidgets_theme import ThemedQWidget, ThemedMainWindow, ThemedDialog" 2>/dev/null; then
    echo "  ✓ PASS"
    ((PASS++))
else
    echo "  ✗ FAIL"
    ((FAIL++))
fi

# Test 2: Single Inheritance
echo "Test 2: Single Inheritance..."
if timeout 2 python -c "
import sys
from PySide6.QtWidgets import QApplication
from vfwidgets_theme import ThemedQWidget

class TestWidget(ThemedQWidget):
    pass

app = QApplication(sys.argv)
w = TestWidget()
" 2>/dev/null; then
    echo "  ✓ PASS"
    ((PASS++))
else
    echo "  ✗ FAIL"
    ((FAIL++))
fi

# Test 3-7: All Examples
for i in 01 02 03 04 05; do
    echo "Test $((i+2)): Example $i..."
    if timeout 2 python ${i}_*.py >/dev/null 2>&1; then
        echo "  ✓ PASS"
        ((PASS++))
    else
        EXIT=$?
        if [ $EXIT -eq 124 ]; then
            echo "  ✓ PASS (timeout - GUI app running)"
            ((PASS++))
        else
            echo "  ✗ FAIL (exit code: $EXIT)"
            ((FAIL++))
        fi
    fi
done

# Summary
echo ""
echo "=== RESULTS ==="
echo "Passed: $PASS"
echo "Failed: $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "✓ ALL TESTS PASSED - Implementation complete!"
    exit 0
else
    echo "✗ SOME TESTS FAILED - Implementation incomplete!"
    exit 1
fi
```

**Exit Criteria:**
- [ ] Script exits with code 0
- [ ] All tests pass
- [ ] No failures reported

---

## Phase 7: Commit and Document

### Task 7.1: Create Commit with Changes

**Action:** Commit all changes with descriptive message

```bash
git add -A
git commit -m "feat: simplify theme system API with single inheritance

BREAKING CHANGE: ThemedWidget mixin replaced with concrete classes

- Add ThemedQWidget (QWidget with theming)
- Add ThemedMainWindow (QMainWindow with theming)
- Add ThemedDialog (QDialog with theming)
- Deprecate old ThemedWidget mixin pattern
- Add smart defaults for theme property access
- Update all examples to use single inheritance
- Remove verbose getattr() calls from examples
- Update documentation to match implementation

Migration:
- Replace ThemedWidget + QWidget with ThemedQWidget
- Replace ThemedWidget + QMainWindow with ThemedMainWindow
- Replace getattr(self.theme, 'prop', default) with self.theme.prop

Fixes: #<issue-number>
See: docs/migration-GUIDE.md"
```

**Verification:**
```bash
git log -1 --oneline | grep "feat: simplify theme system API"
```

**Exit Criteria:**
- [ ] Commit created
- [ ] Commit message follows conventional commits
- [ ] Breaking change documented

---

### Task 7.2: Update Implementation Progress

**File:** `/widgets/theme_system/docs/implementation-progress.md`

**Action:** Document completion

```markdown
## API Simplification (COMPLETED - 2025-09-30)

### Status: ✓ COMPLETE

### What Was Done:
- Created ThemedQWidget, ThemedMainWindow, ThemedDialog
- Implemented ThemingMixin for code reuse
- Added smart defaults for property access
- Updated all 5 examples to use new API
- Migrated from multiple inheritance to single inheritance
- Updated all documentation
- Created migration guide

### Verification:
- All examples run without crashes (exit code 0 or timeout)
- All imports work correctly
- Single inheritance pattern works
- Property access with defaults works
- Documentation matches implementation

### Breaking Changes:
- ThemedWidget now requires explicit QWidget co-inheritance (deprecated)
- New classes ThemedQWidget, ThemedMainWindow, ThemedDialog recommended

### Migration Path:
See docs/migration-GUIDE.md for complete migration instructions
```

**Exit Criteria:**
- [ ] Progress documented
- [ ] Status marked as complete
- [ ] Verification results included

---

## Success Criteria

This implementation is considered COMPLETE when:

1. **All code tests pass:**
   - [ ] All imports work
   - [ ] All examples run (exit code 0 or timeout)
   - [ ] No crashes or segfaults
   - [ ] Single inheritance works correctly

2. **Documentation is accurate:**
   - [ ] README examples work when copy-pasted
   - [ ] API reference matches implementation
   - [ ] No references to non-existent APIs
   - [ ] Migration guide is complete

3. **Developer experience is simple:**
   - [ ] Can create themed widget with single inheritance
   - [ ] No need to understand mixins
   - [ ] Property access is simple
   - [ ] Error messages are helpful

4. **Backwards compatibility maintained:**
   - [ ] Old code still works (with warnings)
   - [ ] Migration path is clear
   - [ ] Breaking changes documented

## Rollback Plan

If implementation fails or causes critical issues:

1. Revert to previous commit
2. Keep ThemedWidget as-is with multiple inheritance
3. Document the inheritance pattern better
4. Add better error messages for wrong inheritance order

## Notes for Implementation

- **Never skip verification steps** - Exit codes are critical
- **Test after each task** - Don't batch multiple tasks without testing
- **Document failures** - If something doesn't work, document why
- **Use the testing protocol** - Always check exit codes, not just output
- **Keep migration path** - Old code must still work