# VFWidgets Theme System - API Refactoring Plan (Surgical Approach)

**Date:** 2025-10-01
**Status:** DRAFT - Awaiting Approval
**Goal:** Fix 5 critical API issues WITHOUT creating legacy baggage

---

## 🚨 Root Cause Analysis: Why We Have Duplicate APIs

### Historical Pattern Detection

**Evidence from codebase:**
- 40 files use `ThemedWidget, QWidget` (multiple inheritance)
- 23 files use `ThemedQWidget` (single inheritance)
- Both patterns exported in `__init__.py` with equal prominence
- Documentation shows both patterns as equivalent

**Why this happened:**
1. **No deprecation strategy** - Both APIs kept alive indefinitely
2. **No migration guide** - Users don't know which to use
3. **No forcing function** - No warnings, no errors, both work equally
4. **Examples show both** - Reinforces "both are fine" mentality

**Result:** **API fragmentation** - exactly what you're concerned about!

---

## 🎯 Anti-Fragmentation Strategy

### Core Principle: **One Clear Path Forward**

We will use a **3-phase surgical migration** instead of gradual deprecation:

```
Phase 1: Add New API (backward compatible)
    ↓
Phase 2: Automatic Migration (one-time, aggressive)
    ↓
Phase 3: Remove Old API (clean break)
```

**Key differences from previous refactors:**
1. ✅ **Aggressive timeline** - 3 phases in 4 weeks, not indefinite
2. ✅ **Forced migration** - Automated tooling, not manual rewrites
3. ✅ **Hard deadline** - Old API removed completely in 4 weeks
4. ✅ **Single source of truth** - One pattern in all docs/examples
5. ✅ **No "equivalent" messaging** - Clear primary/deprecated split

---

## 📊 Current State Analysis

### Issue 1: API Duplication

**Affected Files:**
- Source: 4 files (base.py, convenience.py, application.py, mixins.py)
- Examples: 40 files use old pattern, 23 use new pattern
- Tests: Unknown (need audit)

**Current exports:**
```python
# vfwidgets_theme/__init__.py
__all__ = [
    "ThemedWidget",      # ❌ OLD: Complex multiple inheritance
    "ThemedQWidget",     # ✅ NEW: Simple single inheritance
    "ThemedMainWindow",  # ✅ NEW
    "ThemedDialog",      # ✅ NEW
]
```

**Decision:** `ThemedQWidget`/`ThemedMainWindow`/`ThemedDialog` are PRIMARY

---

### Issue 2: Token Discovery

**Current State:**
- 179 tokens defined in `ColorTokenRegistry`
- All accessed as strings: `'window.background'`
- No IDE autocomplete
- 40 occurrences of `theme_config` dict in source

**Missing:**
- Token constants for IDE autocomplete
- Typed theme access

---

### Issue 3: Verbose Property Access

**Current Pattern (34 occurrences in examples):**
```python
bg = getattr(self.theme, 'bg', '#ffffff')  # Verbose!
```

**Missing:**
- Clean property access
- Smart defaults
- Type safety

---

### Issue 4: Role Markers (6 occurrences)

**Current:**
```python
button.setProperty("role", "danger")  # Magic string
```

**Missing:**
- Enum for type safety
- Helper functions

---

### Issue 5: Lifecycle Hooks

**Current:**
```python
def on_theme_changed(self):  # Only hook
    pass
```

**Missing:**
- `before_theme_change()`
- `after_theme_applied()`

---

## 🔧 Surgical Migration Plan

### Phase 1: Add New API (Week 1) - BACKWARD COMPATIBLE

**Goal:** Add new systems WITHOUT breaking anything

#### Task 1.1: Create Token Constants (Day 1-2)

**File:** `src/vfwidgets_theme/core/token_constants.py` (NEW)

```python
"""Token constants for IDE autocomplete."""

class Tokens:
    """All 179 theme tokens as constants."""

    # Base (11 tokens)
    COLORS_FOREGROUND = 'colors.foreground'
    COLORS_BACKGROUND = 'colors.background'
    COLORS_PRIMARY = 'colors.primary'
    # ... (generate all 179)

    @classmethod
    def all_tokens(cls) -> list[str]:
        """Get all token strings."""
        return [v for k, v in vars(cls).items() if not k.startswith('_')]
```

**Validation:**
```python
# Generate from ColorTokenRegistry.ALL_TOKENS
# Verify all 179 tokens present
# Add to __init__.py exports
```

**Test:**
```python
def test_token_constants_complete():
    registry_tokens = set(ColorTokenRegistry.get_all_token_names())
    constant_tokens = set(Tokens.all_tokens())
    assert registry_tokens == constant_tokens
```

---

#### Task 1.2: Create ThemeProperty Descriptor (Day 2-3)

**File:** `src/vfwidgets_theme/widgets/descriptors.py` (NEW)

```python
"""Property descriptors for clean theme access."""

from typing import Any, Optional

class ThemeProperty:
    """Descriptor for type-safe theme properties."""

    def __init__(self, token: str, default: Optional[str] = None):
        self.token = token
        self.default = default
        self._attr_name = None

    def __set_name__(self, owner, name):
        self._attr_name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self

        # Get from theme with smart default
        value = obj.theme.get(self.token, self.default)
        if value is None:
            # Fallback to ColorTokenRegistry default
            value = ColorTokenRegistry.get_default_value(
                self.token,
                obj.theme.type == 'dark'
            )
        return value

    def __set__(self, obj, value):
        raise AttributeError(f"Can't set theme property '{self._attr_name}'")
```

**Usage:**
```python
from vfwidgets_theme import ThemedQWidget, Tokens
from vfwidgets_theme.widgets.descriptors import ThemeProperty

class MyWidget(ThemedQWidget):
    # New way (clean!)
    bg = ThemeProperty(Tokens.WINDOW_BACKGROUND)
    fg = ThemeProperty(Tokens.WINDOW_FOREGROUND)

    # Old way still works (backward compat)
    theme_config = {'old_bg': 'window.background'}
```

**Test:**
```python
def test_theme_property_descriptor():
    widget = MyWidget()
    assert isinstance(widget.bg, str)
    assert widget.bg.startswith('#')  # Color value
```

---

#### Task 1.3: Create WidgetRole Enum (Day 3)

**File:** `src/vfwidgets_theme/widgets/roles.py` (NEW)

```python
"""Type-safe widget roles."""

from enum import Enum

class WidgetRole(Enum):
    """Semantic widget roles for styling."""

    DANGER = "danger"
    SUCCESS = "success"
    WARNING = "warning"
    SECONDARY = "secondary"
    EDITOR = "editor"
    PRIMARY = "primary"
    INFO = "info"

# Helper function for backward compat
def set_widget_role(widget, role: WidgetRole):
    """Set widget role (wraps setProperty)."""
    widget.setProperty("role", role.value)
```

**Validation:**
- All roles match existing stylesheet rules
- Backward compatible with string values

---

#### Task 1.4: Add Lifecycle Hooks (Day 4)

**File:** `src/vfwidgets_theme/widgets/base.py` (MODIFY)

```python
class ThemedWidget(metaclass=ThemedWidgetMeta):
    # ... existing code ...

    def before_theme_change(self, old_theme: Theme, new_theme: Theme) -> bool:
        """Called before theme switch. Return False to prevent."""
        return True

    def on_theme_changed(self):
        """Called during theme change."""
        # Auto-call update() now!
        if hasattr(self, 'update'):
            self.update()

    def after_theme_applied(self):
        """Called after theme fully applied."""
        pass

    def _on_global_theme_changed(self, theme: Theme):
        """Internal: orchestrates lifecycle."""
        old_theme = self._current_theme

        # Call before hook
        if not self.before_theme_change(old_theme, theme):
            return  # Cancelled

        # Apply theme
        self._current_theme = theme
        self._apply_theme_update()

        # Call during hook
        self.on_theme_changed()

        # Call after hook
        self.after_theme_applied()
```

---

#### Task 1.5: Export New APIs (Day 4)

**File:** `src/vfwidgets_theme/__init__.py` (MODIFY)

```python
# NEW: Token system
from .core.token_constants import Tokens

# NEW: Descriptors
from .widgets.descriptors import ThemeProperty, ColorProperty, FontProperty

# NEW: Roles
from .widgets.roles import WidgetRole, set_widget_role

__all__ = [
    # ... existing ...

    # NEW API
    "Tokens",           # Token constants
    "ThemeProperty",    # Property descriptor
    "WidgetRole",       # Role enum
    "set_widget_role",  # Role helper
]
```

**Documentation:** Update quick-start-GUIDE.md to show NEW API first

---

### Phase 2: Aggressive Migration (Week 2) - ONE-TIME BREAK

**Goal:** Migrate ALL code to new API in one surgical operation

#### Task 2.1: Automated Code Migration (Day 5-6)

**File:** `scripts/migrate_to_new_api.py` (NEW)

```python
#!/usr/bin/env python3
"""
Automatic migration script for API v2.0.

Migrates:
1. ThemedWidget → ThemedQWidget/ThemedMainWindow/ThemedDialog
2. theme_config strings → Tokens constants
3. getattr(self.theme, ...) → ThemeProperty descriptors
4. setProperty("role", ...) → WidgetRole enum
"""

import ast
import re
from pathlib import Path
from typing import List, Tuple

class APIv2Migrator(ast.NodeTransformer):
    """AST transformer for automatic migration."""

    def __init__(self):
        self.changes = []
        self.tokens_import_needed = False
        self.role_import_needed = False

    def visit_ClassDef(self, node: ast.ClassDef):
        """Transform class definitions."""

        # Pattern: class X(ThemedWidget, QWidget)
        if self._is_themed_widget_multiple_inheritance(node):
            qt_base = self._get_qt_base_class(node)

            if qt_base == 'QWidget':
                node.bases = [ast.Name('ThemedQWidget', ast.Load())]
                self.changes.append(f"Line {node.lineno}: {node.name} → ThemedQWidget")

            elif qt_base == 'QMainWindow':
                node.bases = [ast.Name('ThemedMainWindow', ast.Load())]
                self.changes.append(f"Line {node.lineno}: {node.name} → ThemedMainWindow")

            elif qt_base == 'QDialog':
                node.bases = [ast.Name('ThemedDialog', ast.Load())]
                self.changes.append(f"Line {node.lineno}: {node.name} → ThemedDialog")

        # Transform theme_config strings to Tokens
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name) and target.id == 'theme_config':
                        self._transform_theme_config(item.value)

        return node

    def _transform_theme_config(self, node: ast.Dict):
        """Transform theme_config dict to use Tokens."""
        if not isinstance(node, ast.Dict):
            return

        for i, value in enumerate(node.values):
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                # Convert 'window.background' → Tokens.WINDOW_BACKGROUND
                token_name = self._string_to_token_constant(value.value)
                node.values[i] = ast.Attribute(
                    value=ast.Name('Tokens', ast.Load()),
                    attr=token_name,
                    ctx=ast.Load()
                )
                self.tokens_import_needed = True
                self.changes.append(f"theme_config: '{value.value}' → Tokens.{token_name}")

    def visit_Call(self, node: ast.Call):
        """Transform setProperty calls."""

        # Pattern: widget.setProperty("role", "danger")
        if (isinstance(node.func, ast.Attribute) and
            node.func.attr == 'setProperty' and
            len(node.args) >= 2):

            if (isinstance(node.args[0], ast.Constant) and
                node.args[0].value == "role"):

                role_value = node.args[1]
                if isinstance(role_value, ast.Constant):
                    # Transform to set_widget_role(widget, WidgetRole.DANGER)
                    role_enum = self._string_to_role_enum(role_value.value)
                    self.role_import_needed = True
                    self.changes.append(
                        f"Line {node.lineno}: setProperty('role', '{role_value.value}') "
                        f"→ set_widget_role(..., WidgetRole.{role_enum})"
                    )

        return node

    @staticmethod
    def _string_to_token_constant(token_str: str) -> str:
        """Convert 'window.background' → 'WINDOW_BACKGROUND'."""
        return token_str.replace('.', '_').upper()

    @staticmethod
    def _string_to_role_enum(role_str: str) -> str:
        """Convert 'danger' → 'DANGER'."""
        return role_str.upper()

    @staticmethod
    def _is_themed_widget_multiple_inheritance(node: ast.ClassDef) -> bool:
        """Check if class uses ThemedWidget with multiple inheritance."""
        if len(node.bases) < 2:
            return False

        base_names = [b.id for b in node.bases if isinstance(b, ast.Name)]
        return 'ThemedWidget' in base_names

    @staticmethod
    def _get_qt_base_class(node: ast.ClassDef) -> str:
        """Get Qt base class (QWidget, QMainWindow, etc)."""
        qt_bases = {'QWidget', 'QMainWindow', 'QDialog', 'QFrame'}
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id in qt_bases:
                return base.id
        return 'QWidget'  # Default

def migrate_file(file_path: Path, dry_run: bool = False) -> List[str]:
    """Migrate a single file."""
    with open(file_path) as f:
        source = f.read()

    try:
        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError as e:
        return [f"SKIP (syntax error): {e}"]

    migrator = APIv2Migrator()
    new_tree = migrator.visit(tree)

    if not migrator.changes:
        return ["No changes needed"]

    # Update imports
    if migrator.tokens_import_needed:
        # Add: from vfwidgets_theme import Tokens
        pass  # Implementation details...

    if not dry_run:
        new_source = ast.unparse(new_tree)
        with open(file_path, 'w') as f:
            f.write(new_source)

    return migrator.changes

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Migrate to API v2.0')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would change without modifying files')
    parser.add_argument('paths', nargs='+', type=Path,
                       help='Files or directories to migrate')
    args = parser.parse_args()

    files_to_migrate = []
    for path in args.paths:
        if path.is_dir():
            files_to_migrate.extend(path.rglob('*.py'))
        else:
            files_to_migrate.append(path)

    print(f"Migrating {len(files_to_migrate)} files...")
    print()

    for file_path in files_to_migrate:
        print(f"📄 {file_path}")
        changes = migrate_file(file_path, dry_run=args.dry_run)
        for change in changes:
            print(f"  {change}")
        print()

    if args.dry_run:
        print("🔍 DRY RUN - No files modified")
    else:
        print("✅ Migration complete!")

if __name__ == '__main__':
    main()
```

**Usage:**
```bash
# Dry run first
python scripts/migrate_to_new_api.py --dry-run examples/ src/

# Real migration
python scripts/migrate_to_new_api.py examples/ src/

# Verify
pytest tests/
python examples/test_examples.py
```

---

#### Task 2.2: Migrate All Examples (Day 7)

```bash
# Automated migration
python scripts/migrate_to_new_api.py examples/

# Manual verification (spot-check 5 files)
# Fix any migration issues
# Run all examples to verify
./examples/run_tests.sh
```

**Checklist:**
- [ ] All 45 examples migrated
- [ ] All examples run without errors
- [ ] All examples show NEW API only
- [ ] No mixed patterns

---

#### Task 2.3: Migrate Source Code (Day 8)

```bash
# Automated migration
python scripts/migrate_to_new_api.py src/vfwidgets_theme/

# Manual review required for:
# - base.py (complex metaclass code)
# - testing/utils.py (test infrastructure)

# Run tests
pytest tests/ -v
```

---

#### Task 2.4: Update All Documentation (Day 8-9)

**Files to update:**
- `docs/quick-start-GUIDE.md` - Show NEW API only
- `docs/api-REFERENCE.md` - NEW API first, old API in "Legacy" section
- `docs/theme-customization-GUIDE.md` - Use Tokens constants
- `examples/README.md` - Update all code snippets
- `README.md` - Update quick start

**Pattern:**
```markdown
## Quick Start (NEW API)

```python
from vfwidgets_theme import ThemedQWidget, Tokens
from vfwidgets_theme.widgets.descriptors import ThemeProperty

class MyWidget(ThemedQWidget):  # ✅ Single inheritance
    bg = ThemeProperty(Tokens.WINDOW_BACKGROUND)  # ✅ Type-safe
```

## Legacy API (Deprecated)

```python
# ⚠️ DEPRECATED: Use ThemedQWidget instead
class MyWidget(ThemedWidget, QWidget):
    theme_config = {'bg': 'window.background'}
```
```

---

### Phase 3: Remove Old API (Week 3) - CLEAN BREAK

**Goal:** Completely remove old APIs and clean up codebase

#### Task 3.1: Mark APIs as Deprecated (Day 10)

**File:** `src/vfwidgets_theme/widgets/base.py`

```python
import warnings

class ThemedWidget(metaclass=ThemedWidgetMeta):
    """DEPRECATED: Use ThemedQWidget, ThemedMainWindow, or ThemedDialog instead.

    This class will be removed in v3.0.0 (4 weeks).

    Migration:
        # Old
        class MyWidget(ThemedWidget, QWidget):
            pass

        # New
        class MyWidget(ThemedQWidget):
            pass
    """

    def __init__(self, *args, **kwargs):
        # Emit deprecation warning
        warnings.warn(
            "ThemedWidget with multiple inheritance is deprecated. "
            "Use ThemedQWidget, ThemedMainWindow, or ThemedDialog instead. "
            "See migration guide: https://docs.vfwidgets.com/migration",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(*args, **kwargs)
```

**Also deprecate:**
- `theme_config` dict access (warn if no ThemeProperty descriptors used)
- String-based role setting

---

#### Task 3.2: Create Migration Guide (Day 10-11)

**File:** `docs/MIGRATION-v2.0.md` (NEW)

```markdown
# Migration Guide: v1.x → v2.0

## Automatic Migration (Recommended)

```bash
# Install migration tool
pip install vfwidgets-theme[migration]

# Run migration
vfwidgets-migrate --dry-run .
vfwidgets-migrate .
```

## Manual Migration

### 1. Update Class Inheritance

**Before:**
```python
class MyWidget(ThemedWidget, QWidget):
    pass
```

**After:**
```python
class MyWidget(ThemedQWidget):  # Single inheritance
    pass
```

### 2. Replace theme_config with Tokens

**Before:**
```python
theme_config = {
    'bg': 'window.background',
    'fg': 'window.foreground'
}
```

**After:**
```python
from vfwidgets_theme import Tokens
from vfwidgets_theme.widgets.descriptors import ThemeProperty

bg = ThemeProperty(Tokens.WINDOW_BACKGROUND)
fg = ThemeProperty(Tokens.WINDOW_FOREGROUND)
```

### 3. Replace setProperty("role") with WidgetRole

**Before:**
```python
button.setProperty("role", "danger")
```

**After:**
```python
from vfwidgets_theme import WidgetRole, set_widget_role

set_widget_role(button, WidgetRole.DANGER)
```

## Breaking Changes

- `ThemedWidget` multiple inheritance: Deprecated, use `ThemedQWidget`
- `theme_config` dict: Deprecated, use `ThemeProperty` descriptors
- String-based roles: Deprecated, use `WidgetRole` enum

## Timeline

- **Week 1:** Deprecation warnings added
- **Week 2:** Old API marked for removal
- **Week 3:** Documentation updated to show new API only
- **Week 4:** Old API removed completely in v3.0.0
```

---

#### Task 3.3: Add Deprecation Tests (Day 11)

**File:** `tests/test_deprecations.py` (NEW)

```python
import pytest
import warnings

def test_themed_widget_multiple_inheritance_deprecated():
    """ThemedWidget with QWidget should emit deprecation warning."""
    with pytest.warns(DeprecationWarning, match="ThemedWidget.*deprecated"):
        class TestWidget(ThemedWidget, QWidget):
            pass

        widget = TestWidget()

def test_theme_config_dict_deprecated():
    """theme_config dict should emit warning if no descriptors."""
    with pytest.warns(DeprecationWarning, match="theme_config.*deprecated"):
        class TestWidget(ThemedQWidget):
            theme_config = {'bg': 'window.background'}

        widget = TestWidget()

def test_string_role_deprecated():
    """setProperty('role', str) should emit warning."""
    from PySide6.QtWidgets import QPushButton

    button = QPushButton()

    with pytest.warns(DeprecationWarning, match="setProperty.*role.*deprecated"):
        button.setProperty("role", "danger")
```

---

#### Task 3.4: Remove Old APIs (Day 12-14)

**Files to modify:**

1. **src/vfwidgets_theme/widgets/base.py**
   - Remove `ThemedWidget` class completely
   - Keep only `ThemedWidgetMeta` (used internally)

2. **src/vfwidgets_theme/widgets/__init__.py**
   - Remove `ThemedWidget` from `__all__`
   - Add comment: `# ThemedWidget removed in v3.0.0 - use ThemedQWidget`

3. **src/vfwidgets_theme/__init__.py**
   - Remove `ThemedWidget` from exports
   - Update docstring to remove references

**Verification:**
```bash
# Should fail
grep -r "ThemedWidget" src/ | grep -v "Meta" | grep -v "comment"

# Should pass
pytest tests/
python examples/run_tests.sh
```

---

### Phase 4: Validation & Polish (Week 4)

#### Task 4.1: Comprehensive Testing (Day 15-16)

```bash
# Run full test suite
pytest tests/ --cov=vfwidgets_theme --cov-report=html

# Run all examples
cd examples && ./run_tests.sh

# Check for any lingering old API usage
grep -r "ThemedWidget, Q" .
grep -r 'setProperty.*"role"' .
grep -r "theme_config = {" src/
```

**Acceptance Criteria:**
- [ ] 100% test pass rate
- [ ] All 45 examples run without errors
- [ ] Zero deprecation warnings in our code
- [ ] Zero occurrences of old patterns in src/

---

#### Task 4.2: Documentation Audit (Day 17)

**Checklist:**
- [ ] All docs show NEW API only
- [ ] Old API mentioned only in MIGRATION-v2.0.md
- [ ] Quick start is < 15 lines
- [ ] Examples are consistent (all use same pattern)
- [ ] API reference updated
- [ ] CHANGELOG.md updated

---

#### Task 4.3: Release Preparation (Day 18-20)

1. **Version Bump:** `1.0.0-dev` → `2.0.0-rc1`
2. **CHANGELOG.md:**

```markdown
# v2.0.0-rc1 (2025-10-XX)

## 🎉 Major API Improvements

### New Features

- ✅ **Token Constants**: `Tokens.WINDOW_BACKGROUND` for IDE autocomplete
- ✅ **ThemeProperty Descriptors**: Clean property access
- ✅ **WidgetRole Enum**: Type-safe roles
- ✅ **Lifecycle Hooks**: `before_theme_change()`, `after_theme_applied()`
- ✅ **Simplified API**: `ThemedQWidget` as primary API

### Breaking Changes

- ❌ **Removed `ThemedWidget` multiple inheritance**
  - Use `ThemedQWidget`, `ThemedMainWindow`, or `ThemedDialog` instead
  - See migration guide: docs/MIGRATION-v2.0.md

- ❌ **Deprecated `theme_config` dict**
  - Use `ThemeProperty` descriptors instead
  - Automatic migration tool available

- ❌ **Deprecated string-based roles**
  - Use `WidgetRole` enum instead

### Migration

Automatic migration available:
```bash
pip install vfwidgets-theme[migration]
vfwidgets-migrate .
```

Manual migration guide: docs/MIGRATION-v2.0.md
```

3. **Git Tag:** `v2.0.0-rc1`
4. **Announcement:** Prepare blog post/announcement

---

## 🛡️ Anti-Fragmentation Safeguards

### 1. Forcing Functions

**Compiler/Runtime Checks:**
```python
# In base.py
def _validate_api_usage(self):
    """Fail fast if using deprecated patterns."""
    if self.__class__.__bases__ == (ThemedWidget, QWidget):
        raise RuntimeError(
            f"{self.__class__.__name__} uses deprecated multiple inheritance. "
            "Use ThemedQWidget instead. See: docs/MIGRATION-v2.0.md"
        )
```

### 2. CI/CD Checks

**File:** `.github/workflows/api-lint.yml` (NEW)

```yaml
name: API Linting

on: [push, pull_request]

jobs:
  lint-api:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Check for deprecated patterns
        run: |
          # Fail if any source files use old patterns
          if grep -r "ThemedWidget, Q" src/; then
            echo "ERROR: Found deprecated multiple inheritance in src/"
            exit 1
          fi

          if grep -r 'setProperty.*"role"' src/; then
            echo "ERROR: Found deprecated string roles in src/"
            exit 1
          fi

          if grep -r "theme_config = {" src/ | grep -v "test" | grep -v "example"; then
            echo "ERROR: Found deprecated theme_config in src/"
            exit 1
          fi
```

### 3. Pre-commit Hook

**File:** `.pre-commit-config.yaml` (ADD)

```yaml
repos:
  - repo: local
    hooks:
      - id: check-deprecated-api
        name: Check for deprecated API usage
        entry: scripts/check_deprecated_api.sh
        language: script
        files: \\.py$
```

**File:** `scripts/check_deprecated_api.sh` (NEW)

```bash
#!/bin/bash
set -e

echo "Checking for deprecated API usage..."

# Check staged files only
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$' || true)

if [ -z "$STAGED_FILES" ]; then
  exit 0
fi

# Check for deprecated patterns
if echo "$STAGED_FILES" | xargs grep -l "ThemedWidget, Q" 2>/dev/null; then
  echo "❌ ERROR: Deprecated multiple inheritance found"
  echo "   Use ThemedQWidget instead"
  exit 1
fi

if echo "$STAGED_FILES" | xargs grep -l 'setProperty.*"role"' 2>/dev/null; then
  echo "❌ ERROR: Deprecated string roles found"
  echo "   Use WidgetRole enum instead"
  exit 1
fi

echo "✅ No deprecated API usage found"
```

### 4. Documentation Lock

**Process:**
- All documentation PRs require approval
- Quick start guide is LOCKED (only shows new API)
- Old API mentioned ONLY in MIGRATION-v2.0.md
- Any PR adding old API examples is auto-rejected

### 5. Monitoring & Cleanup

**Week 1 Post-Release:**
```bash
# Search for any lingering old patterns
grep -r "ThemedWidget, Q" .
grep -r 'setProperty.*"role"' .
grep -r "theme_config = {" . | grep -v test

# Check GitHub issues for migration problems
# Gather feedback on new API
```

---

## 📈 Success Metrics

### Quantitative

- [ ] **0** files using `ThemedWidget, QWidget` pattern in src/
- [ ] **0** occurrences of `getattr(self.theme, ...)` in examples/
- [ ] **0** string-based role markers in examples/
- [ ] **100%** examples using new API
- [ ] **< 4 weeks** from start to old API removal

### Qualitative

- [ ] New developers can create themed widget in < 5 minutes
- [ ] IDE autocomplete works for all tokens
- [ ] Zero "which API should I use?" questions
- [ ] Documentation shows ONE clear path
- [ ] Widget library authors adopt quickly

---

## 🚀 Timeline Summary

| Week | Phase | Key Activities | Deliverable |
|------|-------|----------------|-------------|
| 1 | Add New API | Create Tokens, ThemeProperty, WidgetRole, lifecycle hooks | Backward-compatible v2.0.0-alpha |
| 2 | Migrate | Automated migration of all code, update docs | Migrated codebase |
| 3 | Remove | Delete old APIs, add forcing functions | Clean v2.0.0-beta |
| 4 | Polish | Testing, docs, release prep | v2.0.0-rc1 release |

**Hard Deadline:** 4 weeks from approval

---

## ✅ Approval Checklist

Before starting, confirm:

- [ ] **Strategy approved**: 3-phase surgical migration
- [ ] **Timeline approved**: 4 weeks hard deadline
- [ ] **Breaking changes approved**: Old API removed completely
- [ ] **Forcing functions approved**: Pre-commit hooks, CI checks
- [ ] **Migration tool approved**: Automated AST transformation
- [ ] **Documentation lock approved**: Only new API in docs
- [ ] **Success metrics approved**: Zero old API usage in src/

---

## 🆘 Rollback Plan

If critical issues arise:

**Phase 1 Rollback:**
- Revert new API additions
- No impact (backward compatible)

**Phase 2 Rollback:**
- Revert migrations
- Git history has all changes
- Takes 1 hour

**Phase 3 Rollback:**
- Restore old API from git
- Re-add to exports
- Takes 2 hours

**Point of No Return:** v2.0.0-rc1 release
- After release, no rollback
- Forward-only fixes

---

## 📝 Post-Completion Tasks

After v2.0.0 release:

1. **Monitor adoption** (2 weeks)
   - GitHub issues for migration problems
   - User feedback on new API
   - Performance metrics

2. **Create best practices guide** (Week 5)
   - Common patterns with new API
   - Anti-patterns to avoid
   - Widget library integration guide

3. **Blog post** (Week 6)
   - "Why we rewrote our API"
   - Before/after comparisons
   - Lessons learned

---

## 🎯 Key Principle

**"One clear path forward, executed surgically, with hard deadlines and forcing functions."**

No gradual deprecation. No "both work fine." No indefinite coexistence.

**Add → Migrate → Remove** in 4 weeks. Clean break. One API. Forever.
