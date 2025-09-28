# Chrome-Tabbed-Window-Developer Agent Usage Guide

## Agent Location
`/home/kuja/GitHub/vfwidgets/.claude/agents/chrome-tabbed-window-developer.md`

## How to Invoke the Agent

Use the Task tool or prefix your request with `>` to invoke the agent:

```
> Implement the TabModel class following the Phase 1 specifications
```

or

```
> Create QTabWidget compatibility tests for the addTab method
```

## Key Agent Capabilities

### 1. **Foundation Implementation**
- `> Set up the MVC architecture with proper file structure`
- `> Implement TabModel with QTabWidget data requirements`
- `> Create the ChromeTabbedWindow controller class with QTabWidget API`
- `> Implement Qt Property system for all properties`

### 2. **API Implementation**
- `> Implement addTab, insertTab, and removeTab methods with exact QTabWidget behavior`
- `> Add signal emission with proper timing for currentChanged`
- `> Implement tab property methods (setTabText, tabText, etc.)`
- `> Handle edge cases for empty widget and invalid indices`

### 3. **Testing**
- `> Create comparison tests between QTabWidget and ChromeTabbedWindow`
- `> Write signal spy tests to verify timing`
- `> Add edge case tests for 0 tabs, invalid index, null widgets`
- `> Create memory leak tests for tab operations`

### 4. **Chrome UI Implementation**
- `> Implement Chrome tab shape rendering in ChromeTabBar`
- `> Add hover and selection effects for tabs`
- `> Create tab close button with proper hit testing`
- `> Implement smooth 60 FPS animations`

### 5. **Platform Support**
- `> Create platform detection and capability system`
- `> Implement WindowsPlatformAdapter with frameless support`
- `> Add macOS-specific features like traffic lights`
- `> Handle Linux/Wayland restrictions gracefully`

## Agent Working Rules

The agent will ALWAYS:
✅ Maintain 100% QTabWidget API compatibility
✅ Follow strict MVC architecture
✅ Test against actual QTabWidget behavior
✅ Use Qt Property system for all properties
✅ Match signal timing exactly
✅ Handle edge cases identically
✅ Write comprehensive tests

The agent will NEVER:
❌ Add public methods beyond QTabWidget in v1.0
❌ Change signal emission order or timing
❌ Skip Qt property system
❌ Mix view and model code
❌ Hardcode platform behavior
❌ Forget parent/child ownership rules

## Example Workflow

### Day 1: Foundation Setup
```
> Create the complete file structure for ChromeTabbedWindow following MVC pattern
> Implement TabData dataclass with all QTabWidget fields
> Set up TabModel class with basic signal definitions
```

### Day 2: Core API
```
> Implement addTab and removeTab with proper parent/child handling
> Add currentIndex management with signal emission
> Create basic compatibility tests for these methods
```

### Day 3: Properties
```
> Implement all Qt properties using the Property system
> Add property change notifications
> Test property behavior against QTabWidget
```

### Day 4: Testing
```
> Create comprehensive comparison test suite
> Add signal spy tests for timing verification
> Write edge case tests for all methods
```

## Tracking Progress

The agent uses TodoWrite to track tasks:
```
> Update the todo list with completed Phase 1 foundation tasks
> Mark TabModel implementation as complete
```

## Daily Progress Updates

Ask the agent to update progress:
```
> Update daily-progress.md with today's completed tasks and any blockers
```

## Decision Documentation

For architectural decisions:
```
> Document the decision to use Strategy pattern for platform adapters in decision-log.md
```

## Quality Checks

Before moving to next phase:
```
> Run all compatibility tests and report results
> Verify signal timing matches QTabWidget exactly
> Check that all edge cases are handled
```

## Common Commands

### Implementation
- `> Implement [specific method] with QTabWidget-compatible behavior`
- `> Add Chrome visual rendering for [component]`
- `> Create platform adapter for [platform]`

### Testing
- `> Write comparison test for [feature]`
- `> Add edge case test for [scenario]`
- `> Create performance benchmark for [operation]`

### Documentation
- `> Update implementation checklist with completed tasks`
- `> Document architectural decision about [topic]`
- `> Add code examples for [feature]`

## Important Notes

1. The agent works in `/home/kuja/GitHub/vfwidgets/widgets/chrome-tabbed-window/`
2. It follows the phases defined in the wip/ directory
3. It prioritizes compatibility over features
4. It uses test-driven development
5. It documents all decisions

## Success Validation

The agent knows the implementation is successful when:
```python
# This code works with ZERO modifications:
from PySide6.QtWidgets import QTabWidget
widget = QTabWidget()  # Original

# Changes to:
from chrome_tabbed_window import ChromeTabbedWindow
widget = ChromeTabbedWindow()  # Drop-in replacement!
```

---

**Remember:** The agent is focused on creating a 100% QTabWidget-compatible widget with Chrome visuals. Use it for implementation, testing, and documentation of the ChromeTabbedWindow widget.