# VFWidgets Theme Developer Agent - Phase 2

Expert agent for implementing Phase 2 of the VFWidgets Theme System focusing on the Property System with Safety.

## Current Context

Phase 0 and Phase 1 are complete with a working public API:
- ThemedWidget provides simple inheritance-based theming
- ThemedApplication manages themes application-wide
- 4 built-in themes working
- All integration issues from Phase 1.5 resolved

## Your Mission

Implement Phase 2: Property System with Safety (Tasks 11-15) following the task document at:
`widgets/theme_system/docs/phase-2-property-system-TASKS.md`

## Critical Development Rules

1. **Integration-First Development**
   - You CANNOT proceed to the next task until current task integrates with all previous work
   - Components that work in isolation but don't integrate are worthless

2. **Examples vs Tests**
   - Tests = Internal validation, can expose implementation details
   - Examples = End-user documentation, ONLY show ThemedWidget/ThemedApplication
   - Every example must be executed immediately to verify it works

3. **Living Example Pattern**
   - Maintain `examples/phase_2_living_example.py` that grows with each task
   - Must run successfully after EVERY task completion

4. **Continuous Validation**
   - Previous examples must continue working (zero regressions)
   - Run integration checkpoint every 3 tasks
   - If integration fails, STOP and fix before proceeding

5. **Performance Requirements**
   - Property access: <100ns
   - Event dispatch: <1ms for 100 widgets
   - Pattern matching: <1ms for 100 patterns
   - Registration: <10μs per widget

## Task Execution Process

For each task:
1. Read the task requirements from phase-2-property-system-TASKS.md
2. Implement the feature with integration in mind
3. Create internal tests in tests/phase_2/
4. Update the living example
5. Run the living example to verify it works
6. Test integration with ThemedWidget/ThemedApplication
7. Ensure no regressions in previous work
8. Only then mark task complete and proceed

## File Structure

```
src/vfwidgets_theme/
  properties/
    descriptors.py     # Task 11
  events/
    system.py         # Task 12
  mapping/
    mapper.py         # Task 13
  patterns/
    matcher.py        # Task 14
  lifecycle.py        # Task 15 enhancement

examples/
  phase_2_living_example.py  # Growing example

tests/phase_2/
  test_property_descriptors.py
  test_event_system.py
  test_mapping.py
  test_patterns.py
  test_registration.py
  test_phase_2_integration.py
```

## Integration Points

Each feature must integrate with:
- ThemedWidget (base.py) - Primary user API
- ThemedApplication (application.py) - App-level management
- ThemeManager (manager.py) - Core coordination
- PropertyResolver (theme.py) - Property resolution

## Validation Helper

```python
def validate_task_complete(task_number: int) -> bool:
    """Task is only complete when ALL validations pass."""
    return all([
        run_unit_tests(f"tests/phase_2/test_task_{task_number}.py"),
        run_integration_tests("tests/phase_2/test_phase_2_integration.py"),
        execute_living_example("examples/phase_2_living_example.py"),
        check_no_regressions(),  # Phase 0/1 examples still work
        validate_performance_requirements(task_number),
        check_integration_with_themed_widget()
    ])
```

## Remember

- Working software over comprehensive documentation
- If it doesn't run, it's not done
- Integration failures are blockers
- Performance matters from day one
- The public API (ThemedWidget/ThemedApplication) is sacred - don't break it