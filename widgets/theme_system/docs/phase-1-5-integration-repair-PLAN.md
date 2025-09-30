# Phase 1.5: Integration Repair Tasks

## Critical Context
We discovered that Phase 0 and Phase 1 components work in isolation but fail integration. This interim phase fixes these issues BEFORE proceeding to Phase 2.

## Fundamental Rule
**Examples vs Tests**:
- **Tests** = Internal validation, can expose implementation details
- **Examples** = End-user documentation, ONLY show public API (ThemedWidget, ThemedApplication)

## Tasks

### Task 10: Fix Integration Issues
**Objective**: Make ThemeManager and ErrorRecoveryManager work with ThemedApplication

**Required Fixes**:
1. Add `get_instance()` method to ThemeManager for singleton access
2. Implement `handle_error()` method in ErrorRecoveryManager
3. Ensure ThemeManager singleton pattern is thread-safe
4. Validate all protocol contracts are enforced

**Validation**:
- ThemedApplication can get ThemeManager instance
- Error handling works end-to-end
- No AttributeError exceptions

### Task 11: Reorganize Tests vs Examples
**Objective**: Move internal architecture examples to tests directory

**Actions**:
1. Create `tests/integration/` directory structure
2. Move Phase 0 examples (protocols, errors, lifecycle, threading) to tests/
3. Move Phase 1 internal examples to tests/
4. Keep ONLY public API examples in examples/
5. Ensure all tests still pass after reorganization

**Result Structure**:
```
tests/
  integration/
    test_protocols.py      # Was 00_01_protocols.py
    test_errors.py         # Was 00_02_error_handling.py
    test_lifecycle.py      # Was 00_03_memory_management.py
    test_threading.py      # Was 00_04_thread_safety.py
    test_theme.py          # Was 00_05_theme_immutability.py
    test_manager.py        # Tests ThemeManager internals
    test_application.py    # Tests ThemedApplication internals
examples/
  01_basic_themed_widget.py  # Simple public API usage ONLY
```

### Task 12: Validate Public API
**Objective**: Ensure ThemedWidget and ThemedApplication work as advertised

**Tests Required**:
1. Create integration test that uses ONLY public API
2. Test theme switching through ThemedApplication
3. Test ThemedWidget property access
4. Test on_theme_changed callback
5. NO internal architecture exposed

**Success Criteria**:
```python
# This must work:
app = ThemedApplication(sys.argv)
widget = MyThemedWidget()
widget.theme.bg  # Works
app.set_theme('dark')  # Works
# Widget automatically updates
```

### Task 13: Create Real User Examples (Conditional)
**Objective**: Create simple, clear examples for end users

**ONLY IF Task 12 passes completely**:
1. `examples/01_simple_themed_button.py` - Basic button with theme
2. `examples/02_theme_switching.py` - Runtime theme switching
3. `examples/03_custom_theme_properties.py` - Using theme_config

**Requirements**:
- Maximum 100 lines per example
- Clear comments explaining WHAT, not HOW
- Zero implementation details exposed
- Must run successfully

## Validation Gate
Before marking Phase 1.5 complete:
- [ ] All integration tests pass
- [ ] Public API works without exposing internals
- [ ] Examples are simple and user-friendly
- [ ] No regression in previous work
- [ ] Living example updated and runs

## Why This Phase Exists
We learned that sequential task completion without integration validation creates technical debt. This phase pays that debt before proceeding, ensuring our foundation is solid.