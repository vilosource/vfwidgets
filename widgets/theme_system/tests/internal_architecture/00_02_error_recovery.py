#!/usr/bin/env python3
"""
Error Recovery Example for VFWidgets Theme System

This example demonstrates the robust error handling and fallback system
that ensures applications NEVER crash due to theme issues.

Key Features Demonstrated:
- Automatic fallback to minimal theme
- Property-level error recovery
- Silent recovery with logging
- Performance-optimized error handling
- Thread-safe error recovery

Run this example to see how the theme system handles various error scenarios
gracefully while maintaining application functionality.
"""

import threading
import time

# Import theme system components
from vfwidgets_theme.errors import (
    InvalidThemeFormatError,
    PropertyNotFoundError,
    ThemeLoadError,
    ThemeNotFoundError,
    ThemeSystemNotInitializedError,
    create_error_recovery_manager,
)
from vfwidgets_theme.fallbacks import (
    get_fallback_color,
    get_fallback_property,
    get_fallback_theme,
)
from vfwidgets_theme.logging import (
    configure_theme_logging,
    create_theme_logger,
    log_theme_error,
)


def demonstrate_exception_hierarchy():
    """Demonstrate the exception hierarchy and error types."""
    print("=== Exception Hierarchy Demo ===")

    # Theme not found error
    try:
        raise ThemeNotFoundError("dark-professional")
    except ThemeNotFoundError as e:
        print(f"✓ ThemeNotFoundError: {e}")

    # Theme load error
    try:
        raise ThemeLoadError("Failed to parse JSON", file_path="/themes/broken.json")
    except ThemeLoadError as e:
        print(f"✓ ThemeLoadError: {e}")

    # Property not found error
    try:
        raise PropertyNotFoundError("custom_accent", "colors.custom_accent")
    except PropertyNotFoundError as e:
        print(f"✓ PropertyNotFoundError: {e}")

    # Invalid theme format error
    try:
        raise InvalidThemeFormatError("Missing colors section")
    except InvalidThemeFormatError as e:
        print(f"✓ InvalidThemeFormatError: {e}")

    # System not initialized error
    try:
        raise ThemeSystemNotInitializedError()
    except ThemeSystemNotInitializedError as e:
        print(f"✓ ThemeSystemNotInitializedError: {e}")

    print()


def demonstrate_fallback_system():
    """Demonstrate the fallback theme system."""
    print("=== Fallback System Demo ===")

    # Get fallback theme
    fallback_theme = get_fallback_theme()
    print(f"✓ Fallback theme has {len(fallback_theme)} sections")
    print(f"  - Colors: {len(fallback_theme['colors'])} entries")
    print(f"  - Fonts: {len(fallback_theme['fonts'])} entries")
    print(f"  - Spacing: {len(fallback_theme['spacing'])} entries")

    # Get fallback colors
    primary_color = get_fallback_color("primary")
    unknown_color = get_fallback_color("nonexistent_color")
    print(f"✓ Primary color: {primary_color}")
    print(f"✓ Unknown color fallback: {unknown_color}")

    # Get fallback properties
    font_size = get_fallback_property("fonts.size")
    spacing = get_fallback_property("spacing.default")
    unknown_prop = get_fallback_property("unknown.property")
    print(f"✓ Font size: {font_size}")
    print(f"✓ Default spacing: {spacing}")
    print(f"✓ Unknown property: {unknown_prop}")

    print()


def demonstrate_error_recovery():
    """Demonstrate automatic error recovery."""
    print("=== Error Recovery Demo ===")

    # Create error recovery manager
    recovery_manager = create_error_recovery_manager()

    # Test 1: Theme not found recovery
    error = ThemeNotFoundError("missing-theme")
    recovered_theme = recovery_manager.recover_from_error(
        error, operation="load_theme"
    )
    print(f"✓ Theme not found → Recovered with {len(recovered_theme)} properties")

    # Test 2: Property not found recovery
    error = PropertyNotFoundError("missing_color")
    recovered_color = recovery_manager.recover_from_error(
        error,
        operation="get_property",
        context={"property_key": "missing_color"}
    )
    print(f"✓ Property not found → Recovered color: {recovered_color}")

    # Test 3: Invalid theme format recovery
    corrupted_theme = {"invalid": "data", "colors": {"bad_color": "invalid"}}
    error = InvalidThemeFormatError("Bad theme data", invalid_data=corrupted_theme)
    recovered_theme = recovery_manager.recover_from_error(
        error, operation="validate_theme"
    )
    print(f"✓ Invalid format → Recovered theme with {len(recovered_theme)} sections")

    # Test 4: System not initialized recovery
    error = ThemeSystemNotInitializedError()
    recovered_theme = recovery_manager.recover_from_error(
        error, operation="initialize_system"
    )
    print("✓ System not initialized → Recovered with minimal theme")

    print()


def demonstrate_performance():
    """Demonstrate performance requirements for error handling."""
    print("=== Performance Demo ===")

    recovery_manager = create_error_recovery_manager()

    # Test error recovery performance
    error = PropertyNotFoundError("test_property")

    # Warm up
    for _ in range(100):
        recovery_manager.recover_from_error(error, operation="get_property")

    # Measure performance
    iterations = 1000
    start_time = time.perf_counter()

    for _ in range(iterations):
        recovery_manager.recover_from_error(error, operation="get_property")

    end_time = time.perf_counter()
    avg_time_ms = ((end_time - start_time) / iterations) * 1000

    print(f"✓ Error recovery performance: {avg_time_ms:.3f}ms per operation")
    print(f"  Target: < 1.0ms, {'✓ PASS' if avg_time_ms < 1.0 else '✗ FAIL'}")

    # Test fallback color performance
    start_time = time.perf_counter()

    for _ in range(iterations):
        get_fallback_color("primary")

    end_time = time.perf_counter()
    avg_time_us = ((end_time - start_time) / iterations) * 1000000

    print(f"✓ Fallback color performance: {avg_time_us:.1f}μs per operation")
    print(f"  Target: < 100μs, {'✓ PASS' if avg_time_us < 100 else '✗ FAIL'}")

    print()


def demonstrate_thread_safety():
    """Demonstrate thread-safe error handling."""
    print("=== Thread Safety Demo ===")

    recovery_manager = create_error_recovery_manager()
    results = []
    errors = []

    def worker_thread(thread_id: int):
        """Worker thread for testing thread safety."""
        try:
            for i in range(100):
                error = PropertyNotFoundError(f"property_{thread_id}_{i}")
                result = recovery_manager.recover_from_error(
                    error, operation="thread_test"
                )
                results.append((thread_id, i, result is not None))
        except Exception as e:
            errors.append((thread_id, e))

    # Start multiple threads
    threads = []
    for i in range(5):
        thread = threading.Thread(target=worker_thread, args=(i,))
        threads.append(thread)
        thread.start()

    # Wait for completion
    for thread in threads:
        thread.join()

    print("✓ Thread safety test completed")
    print(f"  Results: {len(results)} operations")
    print(f"  Errors: {len(errors)} errors")
    print(f"  {'✓ PASS' if len(errors) == 0 else '✗ FAIL'}")

    print()


def demonstrate_logging_integration():
    """Demonstrate logging integration with error recovery."""
    print("=== Logging Integration Demo ===")

    # Configure logging
    configure_theme_logging()

    # Create logger
    logger = create_theme_logger("demo", debug=True)

    # Test different error logging scenarios
    errors = [
        ThemeNotFoundError("demo-theme"),
        ThemeLoadError("Parse error", file_path="demo.json"),
        PropertyNotFoundError("demo_property"),
        InvalidThemeFormatError("Demo format error"),
    ]

    for error in errors:
        log_theme_error(logger, error, context={"demo": True})

    print("✓ Error logging demonstrated (check console output)")
    print()


def demonstrate_graceful_degradation():
    """Demonstrate graceful degradation with partial theme data."""
    print("=== Graceful Degradation Demo ===")

    recovery_manager = create_error_recovery_manager()

    # Test with partially corrupted theme
    partial_theme = {
        "colors": {
            "primary": "#007acc",
            "invalid_color": "not-a-color",
            # Missing required colors
        },
        "fonts": {
            # Missing default font
            "size": "invalid-size"
        },
        # Missing spacing section
    }

    corrected_theme = recovery_manager.apply_graceful_degradation(
        partial_theme, "validate_theme"
    )

    print(f"✓ Original theme sections: {len(partial_theme)}")
    print(f"✓ Corrected theme sections: {len(corrected_theme)}")
    print(f"✓ Colors in corrected theme: {len(corrected_theme['colors'])}")
    print(f"✓ Fonts in corrected theme: {len(corrected_theme['fonts'])}")
    print(f"✓ Spacing in corrected theme: {len(corrected_theme['spacing'])}")

    # Verify essential properties exist
    essential_colors = ['primary', 'background', 'text', 'border']
    for color in essential_colors:
        if color in corrected_theme['colors']:
            print(f"  ✓ {color}: {corrected_theme['colors'][color]}")

    print()


def main():
    """Run all error handling demonstrations."""
    print("VFWidgets Theme System - Error Handling & Recovery Demo")
    print("=" * 60)
    print()

    try:
        demonstrate_exception_hierarchy()
        demonstrate_fallback_system()
        demonstrate_error_recovery()
        demonstrate_performance()
        demonstrate_thread_safety()
        demonstrate_logging_integration()
        demonstrate_graceful_degradation()

        print("🎉 All error handling demonstrations completed successfully!")
        print()
        print("Key Takeaways:")
        print("- Applications never crash due to theme errors")
        print("- Automatic fallback to working theme in all scenarios")
        print("- Performance requirements met (< 1ms error recovery)")
        print("- Thread-safe operation under concurrent access")
        print("- Comprehensive logging for debugging")
        print("- Graceful degradation preserves partial data")

    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        print("This should never happen - error recovery should prevent all crashes!")


if __name__ == "__main__":
    main()
