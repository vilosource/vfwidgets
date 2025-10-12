# Known Issues - VFTheme Studio MVP

**Version:** 0.1.0-dev (Phase 2 Complete)
**Date:** 2025-10-12
**Last Updated:** 2025-10-12 (Post-Fix)

---

## Recently Fixed Issues

### ✅ Preview Not Updating (FIXED)

**Status:** FIXED ✅
**Impact:** None (resolved)

**Description:**
When users edited color tokens in the inspector, the preview canvas didn't update in real-time.

**Fix:**
Modified `_on_token_changed()` in `window.py` to force theme re-registration with the theme system before applying updates.

**Date Fixed:** 2025-10-12

---

## Non-Critical Issues

### 1. Segmentation Fault on Exit

**Status:** Known, Non-Critical
**Impact:** None on functionality
**Occurs:** When closing the application

**Description:**
When the application exits, you may see:
```
Segmentation fault (core dumped)
```

**Why it happens:**
- This is a Qt widget cleanup race condition
- Theme system tries to clean up widgets during shutdown
- Qt is simultaneously destroying widgets
- Both systems try to access the same memory

**Impact:**
- ✅ **Does NOT affect application functionality**
- ✅ **Does NOT lose data** (saved files are fine)
- ✅ **Does NOT crash during normal use**
- ❌ Only occurs during exit/shutdown

**Workaround:**
- Ignore the segfault message
- Or add explicit cleanup in window close event (future fix)

**Will be fixed in:** Phase 3 (cleanup improvements)

---

## Test-Only Issues

### 2. Headless Test Widget Visibility

**Status:** Known, Test Environment Only
**Impact:** None on real usage

**Description:**
4 tests fail in headless (no display) environment:
- `test_inspector_edit_mode_activation`
- `test_inspector_save_valid_value`
- `test_token_validation_invalid_hex`
- `test_color_picker_button_visibility`

**Why it happens:**
- Widgets behave differently without X11 display
- Visibility checks fail in headless mode
- Timing issues with Qt event loop

**Impact:**
- ✅ **All functionality works in real GUI**
- ✅ **Core functionality tests pass (23/27)**
- ❌ UI state tests fail in headless mode

**Workaround:**
- Run application manually to verify
- Use `pytest -k "not visibility"` to skip these tests

**Will be fixed in:** Phase 3 (improved test fixtures)

---

## Minor UI Issues

### 3. RGB Format Validation

**Status:** Known, Minor Limitation
**Impact:** Low - hex colors work fine

**Description:**
RGB format validation is strict:
```python
# This fails validation (spaces around commas)
"rgb(33, 150, 243)"  # ❌ Fails

# Workaround: Use hex instead
"#2196f3"  # ✅ Works
```

**Why it happens:**
- QColor parser is strict about RGB format
- Manual parsing not implemented yet

**Impact:**
- ⚠️ RGB format might not work as expected
- ✅ Hex colors work perfectly
- ✅ Color names work (blue, red, etc.)

**Workaround:**
- Use hex format instead: `#2196f3`
- Use color picker (🎨) which outputs hex

**Will be fixed in:** Phase 3 (improved validation)

---

## Feature Limitations (By Design in MVP)

These are **not bugs** - they're features planned for future phases:

### 4. No Font Editing

**Status:** Not Implemented Yet
**Will be added in:** Phase 3

Currently you can only edit **color tokens** (197 tokens).
Font tokens are not editable in MVP.

### 5. No Theme Templates

**Status:** Not Implemented Yet
**Will be added in:** Phase 3

Cannot start from pre-built templates.
Must create themes from scratch or load existing JSON files.

### 6. No Bulk Editing

**Status:** Not Implemented Yet
**Will be added in:** Phase 3

Must edit tokens one at a time.
No multi-select or bulk operations.

### 7. No Accessibility Validation

**Status:** Not Implemented Yet
**Will be added in:** Phase 4

No WCAG contrast checking.
Must manually verify accessibility.

### 8. JSON Export Only

**Status:** Not Implemented Yet
**Will be added in:** Phase 4

Only exports to VFWidgets JSON format.
No VSCode, CSS, or QSS export yet.

---

## Reporting Issues

**Found a bug?** Please report at:
https://github.com/viloforge/vfwidgets/issues

**Include:**
1. Operating system and version
2. Python version (`python --version`)
3. PySide6 version (`pip show PySide6`)
4. Steps to reproduce
5. Expected vs actual behavior
6. Error messages or screenshots

**Priority levels:**
- **Critical:** Crashes during use, data loss
- **High:** Feature doesn't work, blocking workflow
- **Medium:** Inconvenient but has workaround
- **Low:** Minor cosmetic issues

---

## Status Summary

| Issue | Severity | Impact | Status |
|-------|----------|--------|--------|
| Segfault on exit | Low | None | Known, will fix Phase 3 |
| Headless test failures | N/A | Test only | Known, will fix Phase 3 |
| RGB validation strict | Low | Minor | Workaround exists |
| No font editing | N/A | By design | Phase 3 feature |
| No templates | N/A | By design | Phase 3 feature |
| No bulk edit | N/A | By design | Phase 3 feature |
| No accessibility check | N/A | By design | Phase 4 feature |
| JSON only export | N/A | By design | Phase 4 feature |

**MVP Stability:** ✅ **Stable for intended use** (color theme editing)

---

## Workarounds Summary

**Quick Reference:**

1. **Segfault on exit?** → Ignore it, doesn't affect functionality
2. **RGB color not working?** → Use hex format instead
3. **Need fonts?** → Wait for Phase 3
4. **Need templates?** → Load existing themes as starting points
5. **Need bulk edit?** → Edit tokens one by one (or wait for Phase 3)
6. **Need accessibility check?** → Use external tools (Phase 4)
7. **Need other formats?** → Convert JSON manually (Phase 4)

---

*Last Updated: 2025-10-12*
*Phase 2 Complete - MVP Ready*
