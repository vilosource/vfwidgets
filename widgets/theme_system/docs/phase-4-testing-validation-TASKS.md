# Phase 4: Testing & Validation - Implementation Tasks

## Overview
This phase implements comprehensive testing, validation, and quality assurance for the theme system. All tasks must follow the integration-first development approach.

## Critical Development Rules (from writing-dev-AGENTS.md)

1. **Integration-First Development**: You CANNOT proceed to the next task until the current task integrates with all previous work
2. **Examples Are Tests**: Every example created must be executed immediately to verify it works
3. **Living Example Pattern**: Maintain a `living_example.py` that grows with each task
4. **Examples vs Tests Distinction**:
   - Tests are for INTERNAL validation (can expose implementation)
   - Examples are for END USERS (only show ThemedWidget/ThemedApplication)
5. **Continuous Validation**: Previous work must keep working (zero regressions)
6. **Contract Enforcement**: Enforce protocol contracts with runtime validation

## Phase 4 Tasks

### Task 21: Comprehensive Test Suite
**Objective**: Create exhaustive test coverage for all components

**Requirements**:
1. Create test framework in `tests/comprehensive/test_suite.py`
2. Property-based testing with Hypothesis
3. Fuzz testing for theme parsing
4. Performance regression tests
5. Memory leak detection
6. Thread safety verification

**Implementation Details**:
```python
class ComprehensiveTestSuite:
    """Complete test coverage with advanced testing techniques."""

    @given(st.dictionaries(st.text(), st.text()))
    def test_theme_properties_invariants(self, props):
        # Property-based testing for theme invariants
        pass

    def test_memory_leaks(self):
        # Track widget registration/deregistration
        pass

    def test_thread_safety(self):
        # Concurrent theme changes
        pass
```

**Validation Criteria**:
- [ ] >90% code coverage achieved
- [ ] Property tests find no invariant violations
- [ ] Fuzz testing handles malformed input
- [ ] No memory leaks detected
- [ ] Thread safety verified
- [ ] Performance within requirements

### Task 22: Visual Testing Framework
**Objective**: Implement screenshot-based visual regression testing

**Requirements**:
1. Create `VisualTestFramework` in `tests/visual/framework.py`
2. Screenshot capture for widgets
3. Image comparison with tolerance
4. Visual diff generation
5. Baseline management
6. CI/CD integration support

**Implementation Details**:
```python
class VisualTestFramework:
    """Visual regression testing for themed widgets."""

    def capture_widget(self, widget: ThemedWidget) -> QImage:
        # Capture widget rendering
        pass

    def compare_images(self, actual: QImage, expected: QImage, tolerance=0.01):
        # Compare with perceptual difference
        pass

    def generate_diff(self, actual: QImage, expected: QImage) -> QImage:
        # Create visual diff image
        pass
```

**Validation Criteria**:
- [ ] Screenshots capture accurately
- [ ] Comparison handles minor variations
- [ ] Diff images clearly show changes
- [ ] Baseline updates work correctly
- [ ] Integration with test suite
- [ ] CI/CD ready

### Task 23: Performance Benchmarking
**Objective**: Create comprehensive performance benchmarking system

**Requirements**:
1. Create `BenchmarkSuite` in `tests/benchmarks/suite.py`
2. Micro-benchmarks for critical paths
3. Macro-benchmarks for real scenarios
4. Performance tracking over time
5. Regression detection
6. Report generation

**Implementation Details**:
```python
class BenchmarkSuite:
    """Performance benchmarking with tracking."""

    def __init__(self):
        self.results_db = Path("benchmarks/results.db")

    @benchmark
    def bench_property_access(self):
        # Measure property descriptor performance
        pass

    @benchmark
    def bench_theme_switch(self):
        # Measure theme switching performance
        pass

    def generate_report(self) -> BenchmarkReport:
        # Create performance report with trends
        pass
```

**Validation Criteria**:
- [ ] All critical paths benchmarked
- [ ] Results tracked over time
- [ ] Regression detection works
- [ ] Reports clearly show trends
- [ ] Integration with CI/CD
- [ ] Performance requirements validated

### Task 24: Validation Framework
**Objective**: Runtime validation system for theme integrity

**Requirements**:
1. Create `ValidationFramework` in `src/vfwidgets_theme/validation/framework.py`
2. Schema validation for themes
3. Contract validation for protocols
4. Runtime assertion system
5. Validation decorators
6. Debug vs production modes

**Implementation Details**:
```python
class ValidationFramework:
    """Runtime validation with configurable strictness."""

    def __init__(self, mode: ValidationMode):
        self.mode = mode  # DEBUG, PRODUCTION, STRICT

    @validate_theme
    def validate_theme_structure(self, theme: Theme):
        # Validate theme conforms to schema
        pass

    @validate_contract
    def validate_protocol_implementation(self, obj, protocol):
        # Verify protocol contract
        pass

    @validation_decorator
    def require_valid_color(self, func):
        # Decorator for color validation
        pass
```

**Validation Criteria**:
- [ ] Schema validation catches errors
- [ ] Contract validation enforced
- [ ] Runtime assertions work
- [ ] Decorators easy to use
- [ ] Mode switching works
- [ ] Performance overhead acceptable

### Task 25: Integration Test Scenarios
**Objective**: Real-world integration test scenarios

**Requirements**:
1. Create scenario tests in `tests/scenarios/`
2. Complex multi-widget applications
3. Theme switching under load
4. Error recovery scenarios
5. Migration scenarios
6. Plugin integration tests

**Implementation Details**:
```python
class IntegrationScenarios:
    """Real-world usage scenarios."""

    def test_complex_application(self):
        # 100+ widget application
        pass

    def test_rapid_theme_switching(self):
        # Switch themes rapidly
        pass

    def test_error_recovery(self):
        # Corrupt theme handling
        pass

    def test_migration_path(self):
        # Upgrade from old version
        pass
```

**Validation Criteria**:
- [ ] Complex apps work correctly
- [ ] Rapid switching handled
- [ ] Errors recovered gracefully
- [ ] Migration paths work
- [ ] Plugin integration works
- [ ] Real-world scenarios covered

## Integration Checkpoint Requirements

After Task 23 (mid-phase checkpoint):
1. Run all benchmarks and verify performance
2. Execute comprehensive test suite
3. Check visual regression tests
4. Verify no regressions in Phase 0/1/2/3
5. Update and run living example
6. Fix ANY issues before continuing

## Living Example for Phase 4

Create `examples/phase_4_living_example.py` that demonstrates:
```python
#!/usr/bin/env python3
"""
Phase 4 Living Example - Testing & Validation Features
This example grows with each task to demonstrate validation capabilities.
"""

from vfwidgets_theme import ThemedApplication, ThemedWidget
from vfwidgets_theme.validation import ValidationFramework, ValidationMode

# Task 21: Comprehensive testing (shown via test runner)
# Run: pytest tests/comprehensive/ -v --cov

# Task 22: Visual testing
from tests.visual import VisualTestFramework
visual = VisualTestFramework()
widget = ThemedWidget()
baseline = visual.capture_widget(widget)
# Theme change...
comparison = visual.compare_images(current, baseline)

# Task 23: Performance benchmarking
from tests.benchmarks import BenchmarkSuite
suite = BenchmarkSuite()
report = suite.run_all()
print(f"Performance: {report.summary()}")

# Task 24: Validation framework
validator = ValidationFramework(ValidationMode.STRICT)
validator.validate_theme_structure(app.current_theme)

# Task 25: Integration scenarios
# These run as part of test suite
# pytest tests/scenarios/ -v
```

## Test Organization

All tests organized by type:
- `tests/comprehensive/` - Task 21 comprehensive suite
- `tests/visual/` - Task 22 visual testing
- `tests/benchmarks/` - Task 23 performance
- `tests/validation/` - Task 24 validation tests
- `tests/scenarios/` - Task 25 integration scenarios
- `tests/phase_4_integration.py` - Full integration test

## Performance Requirements

- Test suite execution: <5 minutes for full suite
- Visual comparison: <100ms per widget
- Benchmark execution: <1 second per benchmark
- Validation overhead: <5% in production mode
- Scenario tests: <30 seconds each

## Success Criteria for Phase 4

Phase 4 is complete when:
1. ✅ All 5 tasks implemented and tested
2. ✅ >90% code coverage achieved
3. ✅ Visual regression testing operational
4. ✅ Performance benchmarks passing
5. ✅ Validation framework integrated
6. ✅ Real-world scenarios tested
7. ✅ No regressions in previous phases
8. ✅ Documentation complete

## Notes for Agent

- Testing must be comprehensive but fast
- Visual tests need baseline management
- Benchmarks must track history
- Validation must have minimal overhead
- Scenarios should reflect real usage
- If tests fail, fix the code not the tests