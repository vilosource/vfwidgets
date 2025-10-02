# Execution Strategy - API Consolidation Plan

**Date:** 2025-10-01
**Status:** READY TO EXECUTE
**Agent:** `theme-system-consolidation`

---

## Quick Start

### Invoke the Agent

```bash
# In Claude Code, use the agent
> Use the theme-system-consolidation agent to implement Week 2 of the API consolidation plan
```

The agent will:
1. Read the plan and strategy docs
2. Create a phase-specific todo list
3. Work through tasks with TDD
4. Report progress at quality gates

---

## Overview

We have **Week 1 complete** (documentation aligned). Now we need to execute **Weeks 2-3** (examples + code).

### What's Done ✅

- API-STRATEGY.md - Philosophy documented
- API-CONSOLIDATION-PLAN.md - Detailed roadmap
- ROADMAP.md - Updated with rationale
- quick-start-GUIDE.md - Shows only simple API
- widget-development-GUIDE.md - Bridge document
- api-REFERENCE.md - Reorganized by skill level
- theme-customization-GUIDE.md - Updated

### What's Left 🔨

**Week 2: Examples Reorganization** (5 days)
- Reorganize examples/ directory structure
- Update examples 01-04 (simple API only)
- Create example 05 (bridge to ThemedWidget)
- Create examples/README.md

**Week 3: Code Implementation** (9 days)
- Tokens constants class
- ThemeProperty descriptors
- WidgetRole enum
- Inheritance order validation
- Testing & polish

---

## Execution Phases

### Phase 1: Examples Reorganization

**Duration:** 5 days
**Agent tasks:** 6 tasks

**Quality gate:**
```bash
cd examples && ./run_tests.sh
# All examples should run successfully
```

**Deliverables:**
- Reorganized examples/ directory
- examples/README.md explaining progression
- All examples running successfully
- Clear simple → advanced path

---

### Phase 2: Tokens Implementation

**Duration:** 2 days
**Agent tasks:** 7 tasks

**Quality gate:**
```bash
pytest tests/test_tokens.py -v --cov=vfwidgets_theme.core.token_constants
python -c "from vfwidgets_theme import Tokens; print(len(Tokens.all_tokens()))"
# Should print: 179
```

**Deliverables:**
- `src/vfwidgets_theme/core/token_constants.py` (NEW)
- All 179 tokens as constants
- Tests with 90%+ coverage
- Exported in `__init__.py`

---

### Phase 3: ThemeProperty Implementation

**Duration:** 1 day
**Agent tasks:** 7 tasks

**Quality gate:**
```bash
pytest tests/test_properties.py -v --cov=vfwidgets_theme.widgets.properties
python -c "from vfwidgets_theme.widgets.properties import ThemeProperty; print('OK')"
```

**Deliverables:**
- `src/vfwidgets_theme/widgets/properties.py` (NEW)
- ThemeProperty, ColorProperty, FontProperty
- Tests with 90%+ coverage
- Exported in `__init__.py`

---

### Phase 4: WidgetRole Implementation

**Duration:** 1 day
**Agent tasks:** 6 tasks

**Quality gate:**
```bash
pytest tests/test_roles.py -v --cov=vfwidgets_theme.widgets.roles
python -c "from vfwidgets_theme import WidgetRole; print(WidgetRole.DANGER)"
```

**Deliverables:**
- `src/vfwidgets_theme/widgets/roles.py` (NEW)
- WidgetRole enum with all roles
- set_widget_role and get_widget_role helpers
- Tests with 90%+ coverage

---

### Phase 5: Validation & Polish

**Duration:** 5 days
**Agent tasks:** 8+ tasks

**Quality gate:**
```bash
pytest tests/ -v --cov=vfwidgets_theme --cov-report=term-missing
cd examples && ./run_tests.sh
# Both should pass 100%
```

**Deliverables:**
- Inheritance order validation in ThemedWidget
- Helpful error messages
- Full test suite passing
- Version bumped to 2.0.0-rc4
- CHANGELOG.md updated

---

## Review & Checkpoint Strategy

### After Each Phase

**Review Questions:**
1. Did all tests pass?
2. Does the implementation match the spec?
3. Are docs updated?
4. Any regressions introduced?
5. Ready for next phase?

**Commands to run:**
```bash
# Full test suite
pytest tests/ -v --cov=vfwidgets_theme

# Examples
cd examples && ./run_tests.sh

# Import test
python -c "from vfwidgets_theme import *"

# Check coverage
pytest --cov-report=html
open htmlcov/index.html
```

### Every 5 Tasks

**Quick checkpoint:**
- [ ] Tests passing?
- [ ] Todo list updated?
- [ ] Any blockers?
- [ ] Agent on track?

### Quality Gates (MANDATORY)

**Cannot proceed to next phase without passing quality gate.**

Each quality gate has:
- Specific commands to run
- Expected output
- Pass/fail criteria

---

## Testing Protocol

### TDD Cycle (Agent MUST Follow)

```
For every task:

1. Write test FIRST (should fail)
2. Run test → verify fails correctly
3. Implement minimum code
4. Run test → verify passes
5. Run ALL tests → verify no regressions
6. Refactor if needed
7. Update docs
8. Mark task complete
```

### Test Coverage Requirements

**New code:** 90%+ coverage
**Modified code:** No coverage decrease
**Overall:** Maintain or improve

### Test Types Required

1. **Unit tests** - Test the code in isolation
2. **Integration tests** - Test with existing system
3. **Example tests** - Examples run successfully
4. **Import tests** - Clean import works

---

## Progress Tracking

### Agent Uses TodoWrite

The agent creates phase-specific todo lists:

```markdown
Phase 1: Examples Reorganization
├─ [x] Task 1.1: Audit current examples
├─ [in_progress] Task 1.2: Create README
├─ [ ] Task 1.3: Update examples 01-04
├─ [ ] Task 1.4: Create example 05
├─ [ ] Task 1.5: Migrate to advanced/
└─ [ ] Task 1.6: Run all examples
```

### You Can Monitor

```bash
# Check what agent is working on
# (Look at conversation for current todo list)
```

---

## Rollback Strategy

### If Phase Fails Quality Gate

**Option 1: Fix Forward**
- Agent debugs the issue
- Fixes the problem
- Re-runs quality gate

**Option 2: Rollback Phase**
- Git revert to start of phase
- Review what went wrong
- Adjust approach
- Restart phase

**Option 3: Pause & Review**
- Stop agent
- Manual review of code
- Decide: fix, rollback, or adjust plan

### Git Commit Strategy

**Agent should commit:**
- After each completed task
- After passing quality gate
- With clear descriptive messages

**Commit message format:**
```
feat(tokens): implement Tokens constants class

- Add all 179 tokens from ColorTokenRegistry
- Implement all_tokens() and validate() methods
- Add comprehensive test coverage (95%)
- Export in __init__.py

Tests: pytest tests/test_tokens.py -v
```

---

## Communication Points

### Agent Reports At:

1. **Phase start** - "Starting Phase X: [description]"
2. **Quality gate** - "Phase X quality gate: [PASS/FAIL]"
3. **Blockers** - "Blocked on: [description], need guidance"
4. **Phase complete** - "Phase X complete, ready for review"

### You Review At:

1. After each quality gate
2. When agent reports blocker
3. After phase completion
4. Before proceeding to next phase

---

## Success Criteria

### Overall Success Means:

✅ **All phases complete**
✅ **All tests passing (100% suite)**
✅ **All examples running**
✅ **No regressions**
✅ **Documentation matches implementation**
✅ **Version bumped to 2.0.0-rc4**
✅ **Ready for release candidate testing**

### Acceptance Checklist:

- [ ] Phase 1: Examples reorganized, all running
- [ ] Phase 2: Tokens implemented with 90%+ coverage
- [ ] Phase 3: ThemeProperty implemented with 90%+ coverage
- [ ] Phase 4: WidgetRole implemented with 90%+ coverage
- [ ] Phase 5: Validation working, error messages helpful
- [ ] All quality gates passed
- [ ] Full test suite passing
- [ ] CHANGELOG.md updated
- [ ] Version bumped

---

## Troubleshooting

### If Agent Gets Stuck

**Symptoms:**
- Not making progress
- Failing same test repeatedly
- Unclear about next step

**Actions:**
1. Review current task specification
2. Check if agent has read all required docs
3. Provide specific guidance
4. Break down task into smaller steps

### If Tests Fail

**Actions:**
1. Read test output carefully
2. Check implementation vs spec
3. Verify test is correct (not the code)
4. Debug with print statements
5. Ask agent to explain failure

### If Quality Gate Fails

**Actions:**
1. Review quality gate criteria
2. Identify what's missing
3. Create specific tasks to address gaps
4. Re-run quality gate

---

## Post-Completion

### After All Phases Complete

1. **Full system test**
   ```bash
   pytest tests/ -v --cov=vfwidgets_theme
   cd examples && ./run_tests.sh
   ```

2. **Manual smoke test**
   - Install in fresh environment
   - Run a few examples
   - Test imports

3. **Documentation review**
   - Read updated docs
   - Verify code examples work
   - Check for broken links

4. **Version & release**
   - Bump to 2.0.0-rc4
   - Update CHANGELOG.md
   - Tag release
   - Announce to team

---

## Quick Reference

### Agent Invocation

```bash
# Start Week 2 (Examples)
> Use theme-system-consolidation agent to implement Phase 1 (examples reorganization)

# Start Week 3 (Code)
> Use theme-system-consolidation agent to implement Phase 2 (Tokens implementation)

# Continue where left off
> Continue with theme-system-consolidation agent on the next phase
```

### Key Documents

- **Plan:** `docs/API-CONSOLIDATION-PLAN.md`
- **Strategy:** `docs/API-STRATEGY.md`
- **Agent:** `.claude/agents/theme-system-consolidation.md`
- **This doc:** `docs/EXECUTION-STRATEGY.md`

### Test Commands

```bash
# Unit tests
pytest tests/ -v

# Coverage
pytest --cov=vfwidgets_theme --cov-report=term-missing

# Examples
cd examples && ./run_tests.sh

# Specific test
pytest tests/test_tokens.py -v

# Import check
python -c "from vfwidgets_theme import *"
```

---

## Summary

1. **Agent is ready:** `theme-system-consolidation`
2. **Work is scoped:** Weeks 2-3 of API Consolidation Plan
3. **Process is clear:** TDD with quality gates
4. **Progress is tracked:** TodoWrite + commits
5. **Reviews are scheduled:** After each quality gate
6. **Success is defined:** All tests pass, docs match, version bumped

**Ready to execute!** 🚀

Start with: `> Use theme-system-consolidation agent to implement Phase 1`
