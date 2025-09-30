# Phase 2: Property System with Safety - Implementation Tasks

## Overview
This phase enhances the property system with type safety, validation, and advanced features. All tasks must follow the integration-first development approach established in Phase 1.5.

## Critical Development Rules (from writing-dev-AGENTS.md)

1. **Integration-First Development**: You CANNOT proceed to the next task until the current task integrates with all previous work
2. **Examples Are Tests**: Every example created must be executed immediately to verify it works
3. **Living Example Pattern**: Maintain a `living_example.py` that grows with each task
4. **Examples vs Tests Distinction**:
   - Tests are for INTERNAL validation (can expose implementation)
   - Examples are for END USERS (only show ThemedWidget/ThemedApplication)
5. **Continuous Validation**: Previous work must keep working (zero regressions)
6. **Contract Enforcement**: Enforce protocol contracts with runtime validation

## Phase 2 Tasks

### Task 11: Robust Property Descriptors
**Objective**: Create type-safe property descriptors with validation and caching

**Requirements**:
1. Create `PropertyDescriptor` class in `src/vfwidgets_theme/properties/descriptors.py`
2. Implement type validation at runtime
3. Add property validation rules (min/max, regex, enum)
4. Support computed properties with caching
5. Build property inheritance chain
6. Create debugging tools for property access

**Implementation Details**:
```python
class PropertyDescriptor:
    """Type-safe property descriptor with validation."""
    def __init__(self, name: str, type_hint: Type, validator=None, default=None):
        self.name = name
        self.type_hint = type_hint
        self.validator = validator
        self.default = default

    def __get__(self, obj, owner):
        # Return typed, validated value
        pass

    def __set__(self, obj, value):
        # Validate and set with type checking
        pass
```

**Validation Criteria**:
- [ ] Type checking works at runtime
- [ ] Validators prevent invalid values
- [ ] Computed properties cache correctly
- [ ] Inheritance chain resolves properly
- [ ] Integration test with ThemedWidget passes
- [ ] Living example updated and runs

### Task 12: Event System with Qt Integration
**Objective**: Integrate Qt signals/slots for efficient theme change notifications

**Requirements**:
1. Create `EventSystem` class in `src/vfwidgets_theme/events/system.py`
2. Use Qt signals/slots for theme changes
3. Implement debouncing with QTimer
4. Add property-specific signals
5. Event filtering for performance
6. Event replay for testing

**Implementation Details**:
```python
class ThemeEventSystem:
    """Qt-integrated event system with debouncing."""
    # Signals
    theme_changing = Signal(str)  # Before change
    theme_changed = Signal(str)   # After change
    property_changed = Signal(str, object, object)  # property, old, new

    def __init__(self):
        self._debounce_timer = QTimer()
        self._debounce_timer.timeout.connect(self._flush_events)
        self._pending_events = []
```

**Validation Criteria**:
- [ ] Qt signals properly connected
- [ ] Debouncing prevents rapid updates
- [ ] Property-specific signals work
- [ ] Event filtering improves performance
- [ ] Integration with ThemedWidget/ThemedApplication
- [ ] Living example demonstrates events

### Task 13: Advanced Mapping with Validation
**Objective**: Create validated theme property mapping system

**Requirements**:
1. Create `ThemeMapping` class in `src/vfwidgets_theme/mapping/mapper.py`
2. CSS selector parser for widget targeting
3. Conflict resolution strategy
4. Mapping composition support
5. Visual debugging tools
6. Validation at mapping time

**Implementation Details**:
```python
class ThemeMapping:
    """Maps theme properties to widget properties with validation."""
    def __init__(self):
        self._mappings = {}
        self._selector_cache = {}

    def add_mapping(self, selector: str, property_map: Dict[str, str]):
        # Validate selector and properties
        # Cache parsed selector
        pass

    def resolve_conflicts(self, widget) -> Dict[str, Any]:
        # Resolve when multiple mappings apply
        pass
```

**Validation Criteria**:
- [ ] CSS selectors parse correctly
- [ ] Conflicts resolve predictably
- [ ] Mapping composition works
- [ ] Validation catches errors early
- [ ] Integration with existing theme system
- [ ] Living example shows mapping in action

### Task 14: Pattern Recognition with Caching
**Objective**: Implement efficient pattern matching for widget selection

**Requirements**:
1. Create `PatternMatcher` in `src/vfwidgets_theme/patterns/matcher.py`
2. Efficient pattern matching algorithm
3. Result caching for performance
4. Pattern priority system
5. Testing utility for patterns
6. Plugin support for custom patterns

**Implementation Details**:
```python
class PatternMatcher:
    """High-performance pattern matching with caching."""
    def __init__(self):
        self._patterns = []
        self._cache = LRUCache(maxsize=1000)

    def add_pattern(self, pattern: str, priority: int = 0):
        # Compile and cache pattern
        pass

    def match(self, widget) -> List[str]:
        # Return matching patterns (cached)
        pass
```

**Validation Criteria**:
- [ ] Pattern matching is fast (<1ms for 100 patterns)
- [ ] Cache hit rate >90% in typical use
- [ ] Priority system works correctly
- [ ] Custom patterns via plugins work
- [ ] Integration with ThemeMapping
- [ ] Performance test passes benchmarks

### Task 15: Widget Registration Safety
**Objective**: Implement bulletproof widget registration/deregistration

**Requirements**:
1. Enhance `WidgetRegistry` in `src/vfwidgets_theme/lifecycle.py`
2. Safe registration/deregistration with guards
3. Widget lifecycle tracking
4. Registration decorators
5. Bulk registration optimization
6. Validation and error recovery

**Implementation Details**:
```python
class EnhancedWidgetRegistry(WidgetRegistry):
    """Safe widget registration with lifecycle tracking."""

    @contextmanager
    def bulk_register(self):
        # Batch registration for performance
        pass

    def safe_register(self, widget, retry=3):
        # Registration with retry and validation
        pass

    @property
    def health_check(self) -> Dict[str, Any]:
        # Registry health metrics
        pass
```

**Validation Criteria**:
- [ ] Registration never fails silently
- [ ] Deregistration cleans up properly
- [ ] Bulk operations are atomic
- [ ] Memory leaks prevented
- [ ] Integration with existing registry
- [ ] Stress test with 1000+ widgets passes

## Integration Checkpoint Requirements

After every 3 tasks (Task 13), perform full integration checkpoint:
1. Run all examples from Phase 2
2. Verify no regressions in Phase 0/1 work
3. Execute integration test suite
4. Update and run living example
5. Fix ANY issues before continuing

## Living Example for Phase 2

Create `examples/phase_2_living_example.py` that demonstrates:
```python
#!/usr/bin/env python3
"""
Phase 2 Living Example - Property System Features
This example grows with each task to demonstrate new capabilities.
"""

# Task 11: Property descriptors with validation
class ValidatedWidget(ThemedWidget):
    theme_config = {
        'bg': PropertyDescriptor('window.background', str, validator=is_color),
        'size': PropertyDescriptor('window.size', int, min=10, max=1000)
    }

# Task 12: Event system demonstration
widget.theme_changed.connect(on_theme_change)
widget.property_changed.connect(on_property_change)

# Task 13: Advanced mapping
mapper = ThemeMapping()
mapper.add_mapping("QButton", {"bg": "button.background"})
mapper.add_mapping("QButton:hover", {"bg": "button.hover"})

# Task 14: Pattern matching
matcher = PatternMatcher()
matcher.add_pattern("*Dialog", priority=10)
matcher.add_pattern("Custom*", priority=5)

# Task 15: Safe registration
with registry.bulk_register():
    for widget in create_widgets(100):
        registry.safe_register(widget)
```

## Test Organization

All internal tests go in `tests/phase_2/`:
- `test_property_descriptors.py` - Task 11 internals
- `test_event_system.py` - Task 12 internals
- `test_mapping.py` - Task 13 internals
- `test_patterns.py` - Task 14 internals
- `test_registration.py` - Task 15 internals
- `test_phase_2_integration.py` - Full integration test

## Success Criteria for Phase 2

Phase 2 is complete when:
1. ✅ All 5 tasks implemented and tested
2. ✅ Living example runs all features
3. ✅ Integration tests pass
4. ✅ No regressions in Phase 0/1
5. ✅ Performance benchmarks met:
   - Property access: <100ns
   - Event dispatch: <1ms for 100 widgets
   - Pattern matching: <1ms for 100 patterns
   - Registration: <10μs per widget
6. ✅ Documentation complete

## Notes for Agent

- Remember: Integration > Isolation
- Test every example immediately
- Update living example with each task
- Enforce contracts with runtime checks
- Previous examples must continue working
- If integration fails, STOP and fix before proceeding