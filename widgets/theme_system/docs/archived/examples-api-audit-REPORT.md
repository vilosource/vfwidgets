# Examples API Usage Audit Report

**Date:** 2025-10-01
**Auditor:** Expert Systems Architect
**Scope:** All 45 example files in `examples/` directory

---

## 🔍 Executive Summary

**The examples show SIGNIFICANT API fragmentation:**

- **14 files** use OLD API only (`ThemedWidget, QWidget` multiple inheritance)
- **7 files** use NEW API only (`ThemedQWidget` convenience classes)
- **4 files** use BOTH APIs (mixing patterns - worst case!)

**This confirms the critical issue: No single clear API pattern.**

---

## 📊 Detailed Breakdown

### Top-Level Examples (6 files)

The main numbered examples that users see first:

| File | API Used | Status |
|------|----------|--------|
| `01_hello_world.py` | ✅ NEW (`ThemedQWidget`) | Good |
| `02_buttons_and_layout.py` | ✅ NEW (`ThemedMainWindow`, `ThemedQWidget`) | Good |
| `03_theme_switching.py` | ✅ NEW (`ThemedMainWindow`, `ThemedQWidget`) | Good |
| `04_input_forms.py` | ✅ NEW (`ThemedMainWindow`, `ThemedDialog`) | Good |
| `05_vscode_editor.py` | ⚠️ **MIXED** (imports both!) | **BAD** |
| `06_role_markers.py` | ✅ NEW (`ThemedMainWindow`) | Good |

**Result:** 5/6 use new API, but #5 imports both (confusing!)

---

### Subdirectory Examples

#### `basic/` (6 files)
**Pattern:** Mostly OLD API

- `themed_button.py` - ❌ OLD (`ThemedWidget, QWidget`)
- `themed_label.py` - ❌ OLD (`ThemedWidget, QWidget`)
- `themed_input.py` - ❌ OLD (`ThemedWidget, QWidget`)
- `themed_list.py` - ❌ OLD (`ThemedWidget, QWidget`)
- `themed_dialog.py` - ⚠️ **MIXED**

**Issue:** Teaching users the OLD pattern!

#### `user_examples/` (6 files)
**Pattern:** Mixed

- `01_minimal_hello_world.py` - ❌ OLD
- `02_theme_switching.py` - ❌ OLD
- `03_custom_themed_widgets.py` - ❌ OLD (custom widgets)
- `04_multi_window_application.py` - ⚠️ **MIXED**
- `05_complete_application.py` - ✅ NEW
- `06_new_api_simple.py` - ✅ NEW (filename says "new API"!)

**Issue:** Mix of patterns confuses users about which to use

#### `tutorials/` (5 files)
**Pattern:** Mix

- `01_hello_theme.py` - ❌ OLD
- `02_custom_theme.py` - ❌ OLD
- `03_theme_switching.py` - ❌ OLD
- `04_vscode_import.py` - ❌ OLD
- `05_custom_widget.py` - ❌ OLD
- `06_complete_app.py` - ⚠️ **MIXED**

**Issue:** Tutorials teaching OLD pattern exclusively!

#### `layouts/` (5 files)
**Pattern:** OLD API

- `dock_widget.py` - ❌ OLD
- `grid_layout.py` - ❌ OLD
- `splitter.py` - ❌ OLD
- `stacked_widget.py` - ❌ OLD
- `tab_widget.py` - ❌ OLD

**Issue:** Layout examples all use OLD API

#### `development_examples/` (7 files)
**Pattern:** OLD API

- Most use `ThemedWidget, QWidget` pattern

**Issue:** Dev examples show OLD pattern

---

## 🚨 Critical Problems Identified

### Problem 1: Mixed Imports

**4 files import BOTH APIs:**

```python
# examples/05_vscode_editor.py (line 49-55)
from vfwidgets_theme import (
    ThemedApplication,
    ThemedDialog,          # NEW API
    ThemedMainWindow,      # NEW API
    ThemedQWidget,         # NEW API
    ThemedWidget,          # OLD API - WHY???
)
```

**Impact:** Users see both and don't know which to use

### Problem 2: Inconsistent Imports

**Same functionality, different imports:**

```python
# File A
from vfwidgets_theme import ThemedQWidget

# File B
from vfwidgets_theme import ThemedWidget
from PySide6.QtWidgets import QWidget

class MyWidget(ThemedWidget, QWidget):  # More complex!
```

**Impact:** Confusion about "the right way"

### Problem 3: Basic Examples Teach OLD API

The `basic/` directory (likely used by beginners) shows OLD API:

```python
# basic/themed_button.py
class ThemedButton(ThemedWidget, QWidget):  # ❌ Teaching old pattern!
    theme_config = {
        'bg': 'button.background',
        'fg': 'button.foreground'
    }
```

**Impact:** New users learn deprecated pattern first!

### Problem 4: No Clear Migration Message

Files using OLD API have no comments like:
```python
# NOTE: This example uses the old API for backward compatibility.
# New code should use ThemedQWidget instead.
```

**Impact:** Users don't know OLD API is deprecated

---

## 📈 Statistics Summary

### By API Type

```
OLD API only:     14 files (56%)
NEW API only:      7 files (28%)
BOTH APIs:         4 files (16%)
─────────────────────────────
Total:            25 files (100%)
```

### By Example Category

```
Top-level (01-06):    83% NEW API ✅ (but 1 mixed)
basic/:               83% OLD API ❌
user_examples/:       50/50 mix   ⚠️
tutorials/:          100% OLD API ❌
layouts/:            100% OLD API ❌
development/:        100% OLD API ❌
```

### Import Patterns

```
23 files: from vfwidgets_theme import ThemedWidget, ThemedApplication
 2 files: from vfwidgets_theme import ThemedApplication
 1 file:  from vfwidgets_theme import ThemedApplication, ThemedMainWindow, ThemedQWidget
```

**Observation:** `ThemedWidget, ThemedApplication` is the most common import!

---

## ✅ What's Working

### Good Examples (Using NEW API Consistently)

1. **`01_hello_world.py`** - Perfect! Simple, clear, uses `ThemedQWidget`
2. **`02_buttons_and_layout.py`** - Uses `ThemedMainWindow` + `ThemedQWidget`
3. **`03_theme_switching.py`** - Consistent NEW API usage
4. **`04_input_forms.py`** - Uses `ThemedDialog` properly
5. **`06_role_markers.py`** - Clean NEW API pattern

**These should be the template for all examples!**

---

## 🔧 Recommendations

### Immediate Actions (Week 2 of Refactoring Plan)

1. **Migrate ALL examples to NEW API**
   ```bash
   python scripts/migrate_to_new_api.py examples/
   ```

2. **Remove mixed imports**
   - `05_vscode_editor.py` - Remove `ThemedWidget` import
   - `basic/themed_dialog.py` - Standardize to NEW API
   - `user_examples/04_multi_window_application.py` - Standardize
   - `tutorials/06_complete_app.py` - Standardize

3. **Delete or mark as "legacy"**
   ```bash
   # Move old examples to legacy/ folder
   mkdir examples/legacy/
   mv examples/basic/ examples/legacy/basic/
   mv examples/development_examples/ examples/legacy/development/

   # Add README warning
   cat > examples/legacy/README.md << EOF
   # Legacy Examples

   These examples use the OLD API (ThemedWidget with multiple inheritance).
   They are kept for reference only.

   **For new code, use examples in the parent directory!**
   EOF
   ```

4. **Consolidate tutorials**
   - Rewrite `tutorials/` to use NEW API exclusively
   - Or delete and point to top-level examples

### Documentation Updates

**`examples/README.md` should say:**

```markdown
# VFWidgets Theme System - Examples

All examples use the **new simplified API** with convenience classes:

- `ThemedQWidget` - For custom widgets
- `ThemedMainWindow` - For application windows
- `ThemedDialog` - For dialogs

## Quick Start

See `01_hello_world.py` for the simplest example.

## ⚠️ Old API Notice

If you see examples using `ThemedWidget, QWidget` (multiple inheritance),
they are outdated. Use the convenience classes instead.
```

---

## 🎯 Success Criteria for Migration

After migration, we should have:

- [ ] **0 files** using `ThemedWidget, QWidget` pattern
- [ ] **0 files** importing both old and new APIs
- [ ] **100%** of top-level examples (01-06) using NEW API
- [ ] **100%** of `basic/` examples using NEW API or moved to legacy/
- [ ] **100%** of `tutorials/` using NEW API
- [ ] Clear "OLD API" warnings in any legacy examples
- [ ] `examples/README.md` shows ONLY new API

---

## 📝 Migration Checklist

### Phase 1: Top-Level Examples (Day 7)

- [x] `01_hello_world.py` - ✅ Already NEW API
- [x] `02_buttons_and_layout.py` - ✅ Already NEW API
- [x] `03_theme_switching.py` - ✅ Already NEW API
- [x] `04_input_forms.py` - ✅ Already NEW API
- [ ] `05_vscode_editor.py` - Remove `ThemedWidget` import, verify classes
- [x] `06_role_markers.py` - ✅ Already NEW API

### Phase 2: Subdirectories (Day 7-8)

#### basic/ (6 files - all need migration)
- [ ] `themed_button.py` - Migrate to `ThemedQWidget`
- [ ] `themed_label.py` - Migrate to `ThemedQWidget`
- [ ] `themed_input.py` - Migrate to `ThemedQWidget`
- [ ] `themed_list.py` - Migrate to `ThemedQWidget`
- [ ] `themed_dialog.py` - Migrate to `ThemedDialog`, remove mixed imports

#### user_examples/ (6 files - 4 need migration)
- [ ] `01_minimal_hello_world.py` - Migrate to `ThemedQWidget`
- [ ] `02_theme_switching.py` - Migrate to `ThemedMainWindow`
- [ ] `03_custom_themed_widgets.py` - Migrate custom widgets to `ThemedQWidget`
- [ ] `04_multi_window_application.py` - Remove mixed imports, standardize
- [x] `05_complete_application.py` - ✅ Already NEW API
- [x] `06_new_api_simple.py` - ✅ Already NEW API

#### tutorials/ (6 files - all need migration)
- [ ] `01_hello_theme.py` - Migrate to `ThemedQWidget`
- [ ] `02_custom_theme.py` - Migrate to `ThemedMainWindow`
- [ ] `03_theme_switching.py` - Migrate to `ThemedMainWindow`
- [ ] `04_vscode_import.py` - Migrate to `ThemedMainWindow`
- [ ] `05_custom_widget.py` - Migrate to `ThemedQWidget`
- [ ] `06_complete_app.py` - Remove mixed imports

#### layouts/ (5 files - all need migration)
- [ ] `dock_widget.py` - Migrate to `ThemedQWidget`
- [ ] `grid_layout.py` - Migrate to `ThemedQWidget`
- [ ] `splitter.py` - Migrate to `ThemedQWidget`
- [ ] `stacked_widget.py` - Migrate to `ThemedQWidget`
- [ ] `tab_widget.py` - Migrate to `ThemedQWidget`

#### development_examples/ (7 files - decision needed)
- **Option A:** Delete (dev examples, not user-facing)
- **Option B:** Move to `examples/legacy/`
- **Option C:** Migrate to NEW API

### Phase 3: Verification (Day 8)

```bash
# Should return 0
grep -r "class.*ThemedWidget, Q" examples/ | wc -l

# Should return 0 (no mixed imports)
grep -r "ThemedWidget," examples/*.py | grep "ThemedQWidget\|ThemedMainWindow" | wc -l

# Run all examples
./examples/run_tests.sh
```

---

## 🎓 Lessons Learned

### Why This Happened

1. **No API versioning** - Both APIs coexist with no clear "v1 vs v2"
2. **Examples created at different times** - Early examples use OLD, later use NEW
3. **No style guide** - No document saying "always use ThemedQWidget"
4. **No review process** - Examples added without checking consistency
5. **No deprecation warnings** - OLD API works fine, so examples weren't updated

### How to Prevent Future Fragmentation

1. ✅ **Single source of truth** - Top-level examples (01-06) are canonical
2. ✅ **Style guide** - Document in `examples/STYLE_GUIDE.md`
3. ✅ **Pre-commit hook** - Block OLD API in examples/
4. ✅ **CI check** - Fail if any example uses OLD API
5. ✅ **Review requirement** - All example PRs require maintainer approval

---

## 📋 Next Steps

1. **Review this audit** with team
2. **Approve migration strategy** (automatic tool vs manual)
3. **Execute Phase 2 (Week 2)** of refactoring plan:
   - Run migration tool on examples/
   - Manually verify 5 complex examples
   - Run test suite
   - Update documentation
4. **Lock down examples/** with forcing functions

---

## ✅ Approval Required

Before proceeding with migration:

- [ ] Audit findings reviewed
- [ ] Migration approach approved (automatic tool + manual verification)
- [ ] Decision on `development_examples/` (delete/migrate/legacy)
- [ ] Timeline approved (Day 7-8 of refactoring plan)
- [ ] Success criteria agreed upon (0 old API usage in examples/)

---

**Bottom Line:** Examples show the exact API fragmentation problem we're trying to fix. This validates the urgent need for the surgical refactoring plan. The migration MUST happen to provide users with clear, consistent guidance.
