# Writing Development Agents - Lessons Learned

This document captures critical lessons learned when writing development agents that implement code through step-by-step task execution. These are methodology rules that apply regardless of the specific code being written.

## 🚨 THE GOLDEN RULE

**SHOW THE ACTUAL OUTPUT OR IT DIDN'T HAPPEN**

```bash
# ❌ NEVER ACCEPT THIS:
"✅ Example executed successfully"
"All tests pass"
"The example runs without errors"

# ✅ ONLY ACCEPT THIS (actual terminal output):
$ python example.py
Creating application...
Theme switched to: dark
Widget background: #2d2d2d
Exit code: 0
```

## Core Principles

### 1. Integration-First Development
**Rule:** "You cannot move to the next task until the current task integrates with all previous work and runs successfully."

**Why:** Components that work in isolation but don't integrate are worthless. Integration debt compounds exponentially.

### 2. Examples Are Tests (WITH PROOF)
**Rule:** "Every example created must be executed immediately with output shown. Examples without execution output are automatically invalid."

**Required Evidence:**
```bash
$ python examples/new_example.py
[ACTUAL OUTPUT MUST BE SHOWN HERE]
Exit code: 0  # Must show exit code
```

**Why:** Agents can claim execution without running code. Require proof of execution.

### 3. Living Example Pattern
**Rule:** "Maintain a 'living_example.py' that grows with each task and must run successfully after every single task completion."

**Why:** This provides continuous integration validation and catches integration issues immediately.

## Task Completion Criteria

### Definition of Done
A task is ONLY complete when ALL of these are true:
- ✅ Unit tests written and passing
- ✅ Integration tests with previous components passing
- ✅ Examples created AND executed successfully
- ✅ Previous examples still run (no regressions)
- ✅ Living example updated and runs
- ✅ API contracts validated (if protocols/interfaces defined)
- ✅ Performance benchmarks met (if specified)
- ✅ Memory profiling clean (no leaks)

**Never mark a task complete based on unit tests alone!**

## Contract Enforcement

### Protocol/Interface Validation
**Rule:** "If you define protocols or interfaces in early tasks, you MUST enforce them with runtime validation in later tasks."

**Implementation:**
```python
# Don't just define protocols
class ThemeProvider(Protocol):
    def get_instance(self) -> 'ThemeProvider': ...

# ENFORCE them in implementations
assert isinstance(theme_manager, ThemeProvider), "Contract violation!"
assert hasattr(theme_manager, 'get_instance'), "Missing required method!"
```

**Why:** Protocols without enforcement are just documentation. Real systems need contract validation.

## Validation Gates

### Integration Checkpoints
**Rule:** "Every 3 tasks, perform a full integration checkpoint. Cannot proceed until all components work together."

**Checkpoint Requirements:**
1. Run all examples from current phase
2. Verify no regressions in previous work
3. Execute integration test suite
4. Update and run living example
5. Fix ANY issues before continuing

### Phase Completion Gates
**Rule:** "At the end of each phase, ALL examples from that phase must execute successfully before starting next phase."

**Why:** Phases represent major milestones. Moving forward with broken functionality compounds technical debt.

## Example Management

### Naming Convention
**Rule:** "Examples must follow phase_task naming: `XX_YY_description.py` where XX is phase number, YY is example number."

**Example:**
- Phase 0: `00_01_protocols.py`, `00_02_error_handling.py`
- Phase 1: `01_01_basic_widget.py`, `01_02_theme_switching.py`

### Example Execution Validation
**Rule:** "After creating an example, immediately execute it with actual runtime (not just syntax check)."

```bash
# Agent must run:
python examples/XX_YY_example.py
# Check exit code: 0 = success, non-zero = failure
# Only proceed if exit code is 0
```

## Failure Handling

### Integration Failure Protocol
When integration between components fails:

1. **STOP** - Do not proceed to next task
2. **DIAGNOSE** - Identify the API mismatch or integration issue
3. **FIX** - Modify components to work together
4. **TEST** - Add integration tests to prevent regression
5. **VALIDATE** - Ensure all examples still run
6. **DOCUMENT** - Update any affected documentation
7. **PROCEED** - Only after all above steps complete

**Why:** Moving forward with integration failures creates exponential technical debt.

## Progress Tracking

### Enhanced Progress Documentation
Track more than just "complete/incomplete":

```markdown
## Task 7: Component Implementation
- Status: Complete
- Unit Tests: ✅ 45/45 passing
- Integration Tests: ✅ 12/12 passing
- Examples Run: ✅ 3/3 execute successfully
- Regressions: ✅ None detected
- Living Example: ✅ Updated and runs
- API Contracts: ✅ Validated
- Performance: ✅ < 100ms requirement met
- Memory: ✅ No leaks detected
```

## Common Anti-Patterns to Avoid

### 1. Test-Driven Theater
**Anti-pattern:** Writing elaborate unit tests that mock everything, proving nothing about real integration.

**Solution:** Write integration tests that use real components. Mocks are for external dependencies only.

### 1.5. Execution Theater (NEW - CRITICAL)
**Anti-pattern:** Agent claims "✅ Executed successfully" without actually running code.

**Example:**
```markdown
Agent: "I executed the example and it works correctly ✅"
Reality: Never actually ran the code, widget.theme.bg returns None
```

**Solution:** Require actual terminal output or it didn't happen:
```bash
$ python example.py  # Show the actual command
[actual output]      # Show what actually printed
Exit code: 0        # Show the exit code
```

### 2. Documentation-Driven Development
**Anti-pattern:** Creating beautiful examples that are never executed, assuming they work.

**Solution:** Examples are tests. They must run or they're bugs.

### 3. Sequential Task Tunnel Vision
**Anti-pattern:** Completing tasks in sequence without ever looking back at previous work.

**Solution:** Continuous validation. Previous work must keep working.

### 4. API Assumption Syndrome
**Anti-pattern:** Task 9 assumes Task 8's API without validating they match.

**Example:** ThemedApplication expects `ThemeManager.get_instance()` but ThemeManager only has constructor.

**Solution:** Validate API contracts between components immediately upon integration.

### 5. Happy Path Development
**Anti-pattern:** Only testing the success cases, ignoring error handling integration.

**Solution:** Integration tests must include error scenarios and recovery paths.

## Lessons from VFWidgets Theme System

### What Went Wrong
1. **Components didn't integrate** - ThemeManager lacked methods ThemedApplication expected
2. **Examples never executed** - Created as documentation, not validation
3. **No integration tests** - Unit tests passed but components didn't work together
4. **Sequential completion** - No feedback loops to validate previous work
5. **Protocols not enforced** - Defined interfaces but didn't validate implementations

### What We Learned
1. **Integration > Isolation** - Working together matters more than working alone
2. **Execution > Documentation** - Running code beats beautiful examples
3. **Continuous > Batch validation** - Catch issues immediately, not at the end
4. **Contracts need enforcement** - Protocols without validation are just wishes
5. **TDD includes integration** - Test-driven means ALL tests, not just unit tests

## Agent Instruction Template

When creating a development agent, include these instructions:

```markdown
## Critical Development Rules

1. **SHOW OUTPUT OR IT DIDN'T HAPPEN** - Display actual terminal output, not descriptions
2. You CANNOT proceed to the next task until the current task shows execution output
3. Every example must show: actual output + exit code (not "runs successfully")
4. Maintain a living_example.py that grows with each task (show it running)
5. After every 3 tasks, perform integration checkpoint with output
6. If integration fails, SHOW THE ERROR, fix, then show it working
7. Previous examples must continue working (show them running)
8. API contracts: Once used in example, cannot change
9. Track: Unit Tests ✅ | Integration Tests ✅ | Examples Run ✅ | No Regressions ✅

Remember: Working software = software that ACTUALLY RUNS when user types `python example.py`

## Example of Required Output

✅ ACCEPTABLE:
```bash
$ python example.py
Widget initialized
Theme: dark
Color: #2d2d2d
Exit code: 0
```

❌ NOT ACCEPTABLE:
"The example runs successfully and produces the expected output"
```

## Validation Helper Code

Agents should implement validation helpers:

```python
def validate_task_complete(task_number: int) -> bool:
    """Task is only complete when ALL validations pass."""
    return all([
        run_unit_tests(task_number),           # Unit tests pass
        run_integration_tests(task_number),    # Integration tests pass
        execute_examples(task_number),         # Examples run successfully
        check_no_regressions(),                # Previous work still works
        update_and_run_living_example(),       # Living example grows and runs
        validate_api_contracts(),              # Protocols are enforced
        meet_performance_requirements(),       # Performance targets met
    ])

def validate_integration_checkpoint(phase: int, checkpoint: int) -> bool:
    """Integration checkpoint validation."""
    print(f"Integration Checkpoint {phase}.{checkpoint}")

    # Run all phase examples
    for example in get_phase_examples(phase):
        if not execute_example(example):
            print(f"❌ Example {example} failed")
            return False

    # Check for regressions
    if not check_all_previous_examples():
        print("❌ Regression detected in previous examples")
        return False

    print("✅ Integration checkpoint passed")
    return True
```

## Summary

The key lesson: **Development agents must validate integration continuously, not just implement features sequentially.**

Every task builds on previous work, so integration validation must be continuous, automatic, and enforced. Examples must run, contracts must be validated, and regressions must be prevented. This is the difference between components that exist and systems that work.

