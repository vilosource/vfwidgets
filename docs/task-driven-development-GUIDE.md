# Task-Driven Development Guide - VFWidgets Methodology

**Status**: 📖 Methodology Guide
**Created**: 2025-10-11
**Author**: VFWidgets Team
**Purpose**: Document our task-driven development approach for replication across projects

---

## 🎯 What is Task-Driven Development?

Task-Driven Development (TDD) is our methodology for implementing complex, multi-week projects while preserving architectural context and preventing drift.

**Core Idea**: Break implementation into granular, self-contained tasks where each task includes:
- Complete architectural context
- Full implementation code (copy-paste ready)
- Complete tests
- Runnable examples
- Validation checklists

**Result**: Anyone (including your future self) can implement the project correctly without participating in design discussions.

---

## 🏗️ The Document Structure

### Required Documents (7 files minimum)

```
project/wip/
├── START-HERE.md                    # Navigation hub (entry point)
├── IMPLEMENTATION-RULES.md          # Core principles + patterns
├── {project}-architecture-DESIGN.md # Complete architecture spec
├── {project}-implementation-TASKS.md # Step-by-step task list
├── phase1-REFERENCE.md              # Quick reference for phase 1
├── phase2-REFERENCE.md              # Quick reference for phase 2
└── phase3-REFERENCE.md              # Quick reference for phase 3
```

### Document Purposes

| Document | Purpose | When to Read |
|----------|---------|-------------|
| START-HERE.md | Navigation hub, quick start guide | **First thing** - always |
| IMPLEMENTATION-RULES.md | Core principles, patterns, anti-patterns | Before any task |
| *-DESIGN.md | Complete architecture, design decisions | Reference during tasks |
| *-TASKS.md | Granular implementation tasks | Daily work |
| phase*-REFERENCE.md | Quick pattern lookup, phase overview | Start of each phase |

---

## 📋 Creating the Document Set

### Step 1: Design Phase - Create Architecture Document

**File**: `{project}-architecture-DESIGN.md`

**Contents**:
1. **Core Design Principles** (Why are we doing this?)
   - List 3-5 key architectural principles
   - Explain rationale for each
   - Provide examples

2. **Complete Architecture** (What are we building?)
   - Full component hierarchy
   - Layer definitions
   - Component responsibilities
   - Interaction patterns

3. **Public API Specifications** (How will it be used?)
   - API signatures for each component
   - Signal definitions
   - Usage examples (5-6 patterns from simple to complex)

4. **Key Design Decisions** (What did we decide and why?)
   - List major decisions
   - Explain alternatives considered
   - Justify chosen approach

**Example Structure**:
```markdown
# Project Architecture - Design Document

## Core Design Principles
### 1. [Principle Name]
**Rule**: [Clear statement]
**Why**: [Rationale]
**Example**: [Code example]

## Component Hierarchy
[ASCII diagram showing layers/components]

## Component Specifications
### Component Name
**Role**: [MODEL/VIEW/CONTROLLER/etc.]
**Responsibility**: [Single clear statement]
**Public API**:
```python
class Component:
    """Docstring"""

    # Signals
    signal_name = Signal()

    def public_method(self, arg: type) -> type:
        """Docstring"""
```

## Usage Patterns
### Pattern 1: Minimal
[3-5 line example]

### Pattern 2: Simple
[10-15 line example]

### Pattern 3: Advanced
[20-30 line example]

## Key Design Decisions
### Decision 1: [Name]
**Why**: [Rationale]
**Alternative**: [What we didn't choose]
**Choice**: [What we chose and why]
```

**Time Investment**: 4-6 hours (critical - don't rush this)

---

### Step 2: Create Implementation Rules Document

**File**: `IMPLEMENTATION-RULES.md`

**Contents**:
1. **Core Principles** (expanded from architecture)
   - Each principle gets its own section
   - Include ✅ GOOD and ❌ BAD examples
   - Explain consequences of violations

2. **Code Patterns** (templates to copy)
   - Template for each component type
   - Signal patterns
   - Common compositions
   - Testing patterns

3. **Common Pitfalls** (what NOT to do)
   - List 5-10 common mistakes
   - Show anti-pattern code
   - Show correct pattern code
   - Explain why it matters

4. **Implementation Checklist** (validation)
   - Checklist for each component type
   - Specific items to verify
   - Testing requirements
   - Code quality checks

**Template Structure**:
```markdown
# Implementation Rules - [Project Name]

## ⚠️ READ THIS BEFORE IMPLEMENTING ANY TASK

## Core Principles

### 1. [Principle Name]
**Rule**: [Clear rule statement]

**Requirements**:
- ✅ [Requirement 1]
- ✅ [Requirement 2]

**Example**:
```python
# ✅ GOOD: [Description]
class GoodExample:
    pass

# ❌ BAD: [Description]
class BadExample:
    pass
```

## Code Patterns

### Pattern Name
```python
# Template code
```

## Common Pitfalls

### Pitfall 1: [Name]
**Problem**: [Description]

```python
# ❌ BAD
bad_code()

# ✅ GOOD
good_code()
```

## Implementation Checklists

### For [Component Type]:
- [ ] [Specific check]
- [ ] [Specific check]
```

**Time Investment**: 3-4 hours

---

### Step 3: Create Task List with Complete Implementations

**File**: `{project}-implementation-TASKS.md`

**Critical**: This is where most time is spent. Each task must be **completely self-contained**.

**Task Template**:
```markdown
### TASK-XXX: [Component Name]

**⚠️ Before Starting - Read These Documents**:
1. `IMPLEMENTATION-RULES.md` - Sections: [list specific sections]
2. `{project}-architecture-DESIGN.md` - Section: [specific section]
3. `phase*-REFERENCE.md` - [What to look for]

**Architecture Context**:
- **Layer**: [Which layer in architecture]
- **MVC Role**: [MODEL/VIEW/CONTROLLER/etc.]
- **Responsibility**: [Single sentence - what it does]
- **Key Principle**: [Which principle from rules applies]
- **Pattern**: [Which pattern to use]
- **Why [Type]**: [Why this architectural choice]

**Design Notes**:
- [Key constraint 1 - what NOT to do]
- [Key constraint 2]
- [Implementation approach]
- [Specific behavior notes]

**Description**: [One sentence summary]

**File to Create**: `path/to/file.py`

**Public API**:
```python
# Complete API specification with types and docstrings
class Component:
    """Full docstring."""

    signal_name = Signal(type)

    def method_name(self, arg: type) -> type:
        """Docstring with Args/Returns."""
```

**Implementation Details**:
```python
# COMPLETE WORKING IMPLEMENTATION
# This is copy-paste ready code
# Include ALL methods, ALL imports, ALL logic
# 50-150 lines typically

from module import Class

class Component:
    # Full implementation here
    pass
```

**Testing**:
```python
# File: tests/path/test_component.py
# COMPLETE TEST FILE
# 5-10 test functions covering public API

import pytest

def test_creation(qapp):
    """Test component can be created."""
    pass

def test_public_method(qapp):
    """Test public method works."""
    pass
```

**Example**:
```python
# File: examples/XX_component.py
# COMPLETE RUNNABLE EXAMPLE
# Shows real usage of the component

def main():
    app = QApplication(sys.argv)
    demo = DemoWidget()
    demo.show()
    sys.exit(app.exec())
```

**Dependencies**: [List task IDs that must complete first]

**Expected Output**:
- File created: `path/to/file.py`
- Import works: `from package import Component`
- Tests pass: `pytest tests/path/test_component.py -v`
- Example runs: `python examples/XX_component.py`

**✅ Completion Checklist ([Component Type])**:
- [ ] [Specific verification 1]
- [ ] [Specific verification 2]
- [ ] [Specific verification 3]
- [ ] Import verification passes
- [ ] All tests pass with -v flag
- [ ] Example runs without errors
- [ ] Code follows [pattern name] pattern
- [ ] [Component-specific check]

---
```

**Key Requirements for Tasks**:
1. **Complete code** - not pseudocode, actual working implementation
2. **Complete tests** - not test descriptions, actual test functions
3. **Complete examples** - not usage notes, runnable Python files
4. **Context headers** - every task reminds you of principles
5. **Checklists** - every task validates compliance

**Time Investment**: 8-12 hours (most important document)
- Budget 30-60 minutes per task
- 15-20 tasks typical
- DO NOT RUSH THIS - it saves weeks later

---

### Step 4: Create Phase Reference Cards

**Files**: `phase1-REFERENCE.md`, `phase2-REFERENCE.md`, `phase3-REFERENCE.md`

**Purpose**: Quick-lookup guides for each implementation phase (week).

**Contents per Phase**:
1. **Phase Overview** (5 lines)
   - What you're building this phase
   - Which layers/components
   - Time estimate

2. **Architecture Diagram** (ASCII art)
   - Show how components in this phase relate
   - Show dependencies on previous phases

3. **Tasks Summary Table**
   - Task ID | Component | Type | Lines | Complexity

4. **Code Pattern Templates** (copy-paste ready)
   - Template for this phase's component types
   - Signal patterns specific to this phase
   - Composition patterns if applicable

5. **Common Pitfalls for This Phase** (3-5)
   - Mistakes specific to this phase
   - ❌ BAD and ✅ GOOD examples

6. **Testing Strategy for This Phase**
   - What to test
   - What NOT to test
   - Example test patterns

7. **Success Criteria for This Phase**
   - Checklist of deliverables
   - How to know phase is complete

**Template Structure**:
```markdown
# Phase N Quick Reference - [Phase Name]

**Phase**: N of M
**Duration**: Week N
**Goal**: [One sentence]
**Layers**: [Which architectural layers]

## Phase N Goals
[Bullet list of components to build]

## Architecture Overview
```
[ASCII diagram]
```

## Tasks Summary
| Task ID | Component | Type | Lines | Complexity |
|---------|-----------|------|-------|------------|
| TASK-XXX | Name | Type | ~XX | Low/Med/High |

## [Component Type] Pattern
```python
# Template for this phase's components
```

## Common Phase N Pitfalls
### Pitfall 1: [Name]
```python
# ❌ BAD
# ✅ GOOD
```

## Testing Strategy
[What to focus on]

## Success Criteria
- [ ] [Deliverable 1]
- [ ] [Deliverable 2]
```

**Time Investment**: 2-3 hours (1 hour per phase)

---

### Step 5: Create START-HERE Navigation Hub

**File**: `START-HERE.md`

**Purpose**: The FIRST document anyone reads. Orients them completely.

**Contents**:
1. **What We're Building** (2 paragraphs)
   - Project summary
   - Architecture overview
   - Goal/outcome

2. **Document Roadmap** (numbered list)
   - Which document to read first (IMPLEMENTATION-RULES)
   - Which document to reference (architecture)
   - Which document for daily work (tasks)
   - Which documents for quick lookup (phase references)

3. **Quick Start Guide** (3 steps)
   - Step 1: Read rules (5 min)
   - Step 2: Read phase reference (5 min)
   - Step 3: Start first task (30-60 min)

4. **Implementation Checklist** (3 sections)
   - Before starting any task
   - During implementation
   - After implementation

5. **File Organization** (tree diagram)
   - Show wip/ directory structure
   - Show what will be created
   - Map tasks to files

6. **Learning Path** (timeline)
   - If you're new (day-by-day plan)
   - If you're returning (recovery steps)

7. **Common Questions** (FAQ)
   - "Where do I start?"
   - "I don't understand [concept]!"
   - "I'm stuck on a task!"
   - "Do I really need to read all docs?"

8. **Success Criteria** (checklists)
   - Phase 1 complete when...
   - Phase 2 complete when...
   - Project complete when...

9. **Next Steps** (action items)
   - Right now: [3 steps]
   - Remember: [5 reminders]

10. **Quick Reference Card** (lookup table)
    - Need to know X? → Read Y

**Template Structure**:
```markdown
# START HERE - [Project Name]

## 🎯 What We're Building
[2 paragraph summary]

## 📚 Document Roadmap

### 🚀 Start Implementation
1. **READ FIRST**: [`IMPLEMENTATION-RULES.md`](./IMPLEMENTATION-RULES.md)
   - [What's in it]
2. **Architecture Reference**: [`*-DESIGN.md`](./design.md)
   - [What's in it]
3. **Task List**: [`*-TASKS.md`](./tasks.md)
   - [What's in it]

### 📖 Phase-Specific Guides
4. **Phase 1 Guide**: [`phase1-REFERENCE.md`](./phase1.md)
5. **Phase 2 Guide**: [`phase2-REFERENCE.md`](./phase2.md)

## 🏃 Quick Start Guide

### Step 1: Read the Rules (5 minutes)
```bash
cat wip/IMPLEMENTATION-RULES.md
```
**Key Takeaways**: [3-4 bullet points]

### Step 2: Review Phase Reference (5 minutes)
```bash
cat wip/phase1-REFERENCE.md
```
**Key Takeaways**: [3-4 bullet points]

### Step 3: Start First Task (30-60 minutes)
```bash
cat wip/*-TASKS.md
# Find TASK-001
# Copy implementation code
# Run tests and example
```

## 📋 Implementation Checklist

### Before Starting ANY Task
- [ ] [Check 1]
- [ ] [Check 2]

### During Implementation
- [ ] [Check 1]
- [ ] [Check 2]

### After Implementation
- [ ] [Check 1]
- [ ] [Check 2]

## 🗂️ File Organization
```
wip/
├── START-HERE.md              # 👈 You are here
├── IMPLEMENTATION-RULES.md    # Core principles
├── *-DESIGN.md               # Architecture
├── *-TASKS.md                # Daily work
└── phase*-REFERENCE.md        # Quick lookup

To Be Created:
[List files that will be created]
```

## 🎓 Learning Path

### If You're New
Day 1: [What to do]
Day 2-7: [What to do]

### If You're Returning After a Break
1. Quick refresh: [Steps]
2. [Time estimate]

## 🚫 Common Questions

### "Where do I start?"
**Answer**: [Clear answer]

### "I'm stuck!"
**Answer**: [Clear answer]

## ✅ Success Criteria

### Phase 1 Complete When:
- [ ] [Criterion]

### Project Complete When:
- [ ] [Criterion]

## 🎯 Next Steps

**Right Now**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Remember**:
- 📖 [Reminder]
- 🎨 [Reminder]

## 📖 Quick Reference Card
```
NEED TO KNOW...          READ THIS...
─────────────────────────────────────
[Topic]                  [Document]
```
```

**Time Investment**: 2-3 hours

---

## 📊 Complete Timeline

### Planning Phase (1-2 days)
- **Architecture Design**: 4-6 hours
- **Implementation Rules**: 3-4 hours
- **Task List Creation**: 8-12 hours
- **Phase References**: 2-3 hours
- **START-HERE**: 2-3 hours

**Total Planning**: 19-28 hours (2-3.5 days)

### Implementation Phase (2-4 weeks)
- **With this system**: Smooth, consistent, on-track
- **Without this system**: Drift, rework, confusion

**Time Saved During Implementation**: 40-80 hours
- No architectural drift rework
- No "what was I doing?" time
- No "why did we decide this?" research
- No inconsistency debugging

**ROI**: 2-3 days planning saves 1-2 weeks of implementation problems

---

## ✅ Quality Checklist for Task-Driven Development

Before considering your documentation complete, verify:

### Architecture Document
- [ ] 3-5 core principles clearly stated
- [ ] Complete component hierarchy with ASCII diagram
- [ ] Every component has responsibility statement
- [ ] Every component has complete API specification
- [ ] 5+ usage patterns from simple to complex
- [ ] Key design decisions documented with rationale

### Implementation Rules
- [ ] Each principle has ✅ GOOD and ❌ BAD examples
- [ ] Code templates for each component type
- [ ] 5-10 common pitfalls documented
- [ ] Checklists for each component type
- [ ] Signal patterns clearly shown
- [ ] Testing strategy explained

### Task List
- [ ] Every task has context header
- [ ] Every task has complete implementation code
- [ ] Every task has complete test code
- [ ] Every task has runnable example
- [ ] Every task has completion checklist
- [ ] Tasks ordered by dependencies
- [ ] Each task is 30-90 minutes of work

### Phase References
- [ ] One reference per phase/week
- [ ] ASCII architecture diagram per phase
- [ ] Code templates specific to phase
- [ ] Common pitfalls specific to phase
- [ ] Success criteria clearly stated
- [ ] Testing strategy for phase

### START-HERE
- [ ] Clear "what we're building" summary
- [ ] Explicit reading order (numbered)
- [ ] Quick start guide (3 steps, <15 min)
- [ ] FAQ answers common questions
- [ ] Learning path for new developers
- [ ] Recovery path for returning developers
- [ ] Quick reference lookup table

---

## 🎯 When to Use This Methodology

**Good Fit**:
- ✅ Multi-week projects (2+ weeks)
- ✅ Complex architectures (3+ layers)
- ✅ Multiple components (10+ classes)
- ✅ Multiple phases (2+ distinct phases)
- ✅ Risk of context loss (long projects)
- ✅ Multiple developers (or solo across long time)
- ✅ Critical to maintain architecture consistency

**Poor Fit**:
- ❌ Single-file scripts
- ❌ 1-day projects
- ❌ Exploratory prototypes
- ❌ Throwaway code
- ❌ Projects with unclear requirements

**Rule of Thumb**: If implementation will take more than 1 week, use Task-Driven Development.

---

## 🔄 Adapting to Different Project Types

### For Widget Projects (like markdown-widget)
- Focus on MVC layers
- Emphasize composability
- Include usage patterns
- Show atomic → composite progression

### For Application Projects (like ViloxTerm)
- Focus on plugin architecture
- Emphasize extensibility points
- Include integration patterns
- Show core → plugins progression

### For Library Projects
- Focus on public API design
- Emphasize backward compatibility
- Include migration guides
- Show simple → advanced API usage

### For Refactoring Projects
- Document current state (as-is)
- Document target state (to-be)
- Include migration strategies
- Show step-by-step transformation

**Key**: Adapt the structure, not the methodology. Always include:
1. Architecture document (DESIGN)
2. Implementation rules (RULES)
3. Task list with complete code (TASKS)
4. Phase references (REFERENCE)
5. Navigation hub (START-HERE)

---

## 🎉 Success Stories

### Case Study: Markdown Widget (Oct 2025)

**Project**: Implement MVC markdown widget architecture
**Complexity**: 14+ components, 4 layers, 3 weeks
**Team**: 1 developer (with potential gaps)

**Approach**:
- Created 7 documentation files
- 28 hours planning
- Complete code in every task

**Results**:
- ✅ Could return after 2 weeks, back on track in 20 minutes
- ✅ Zero architectural drift
- ✅ Consistent code patterns throughout
- ✅ New developer could onboard in 1 hour
- ✅ Complete implementation possible without any design discussions

**Quote**: *"Even if we forget everything about our discussions, someone can pick this up and implement it correctly."*

---

## 📚 Additional Resources

### Templates
- See `widgets/markdown_widget/wip/` for complete example
- Copy structure for new projects
- Adapt to your specific needs

### Tools
- Markdown for all documentation
- ASCII art for diagrams (simple, version-control friendly)
- Code blocks with syntax highlighting
- Checklists for validation

### Best Practices
- **Be explicit**: Never assume knowledge
- **Be complete**: Include full working code
- **Be consistent**: Use same patterns throughout
- **Be validatable**: Include checklists
- **Be recoverable**: Support context loss

---

## 🚀 Getting Started with Your Next Project

### Step 1: Set Up Directory
```bash
mkdir -p project/wip
cd project/wip
```

### Step 2: Create Documents (in order)
1. Start with architecture design (4-6 hours)
2. Extract implementation rules (3-4 hours)
3. Create task list with code (8-12 hours)
4. Write phase references (2-3 hours)
5. Write START-HERE last (2-3 hours)

### Step 3: Validate
- [ ] Can someone with zero context understand what to build?
- [ ] Does each task have complete code?
- [ ] Are there templates for common patterns?
- [ ] Are anti-patterns documented?
- [ ] Is there a clear entry point?

### Step 4: Implement
- Follow your own task list
- Check completion checklists
- Update docs if you find gaps
- Celebrate small wins!

---

## 💡 Final Thoughts

**Task-Driven Development is an investment in:**
- Architectural consistency
- Developer productivity
- Context preservation
- Project maintainability
- Knowledge transfer

**The alternative cost:**
- Architectural drift
- Inconsistent implementations
- Lost time recovering context
- Debugging architectural violations
- Knowledge silos

**Choose wisely. Your future self will thank you.** 🎉

---

## 📖 Document Change Log

| Date | Version | Changes |
|------|---------|---------|
| 2025-10-11 | 1.0 | Initial methodology documentation based on markdown-widget success |

---

## 🤝 Contributing

This methodology is living documentation. If you:
- Find gaps in the process
- Discover better patterns
- Have success stories to share
- Find ways to improve efficiency

Please update this guide for future projects!
