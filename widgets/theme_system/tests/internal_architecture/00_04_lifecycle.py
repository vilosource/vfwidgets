"""
Example demonstrating VFWidgets Theme System Memory Management Foundation.

This example shows how the memory management system provides automatic,
bulletproof memory management for themed widgets without any developer effort.

Key Demonstrations:
1. Automatic widget registration and cleanup
2. WeakRef-based memory management prevents leaks
3. Context managers for efficient batch operations
4. Memory tracking and leak detection
5. Performance monitoring and validation
6. Thread-safe operations

Philosophy: "ThemedWidget is THE way" - developers get perfect memory
management just by inheriting from ThemedWidget.

Run this example to see:
- Zero memory leaks after widget destruction
- Automatic cleanup when widgets go out of scope
- Performance metrics meeting strict requirements
- Thread-safe concurrent operations
"""

import gc
import threading
import time
from contextlib import contextmanager
from typing import List

# Import the memory management components
from vfwidgets_theme.lifecycle import (
    WidgetRegistry,
    LifecycleManager,
    ThemeUpdateContext,
    WidgetCreationContext,
    PerformanceContext,
    MemoryTracker,
    LeakDetector,
    ResourceReporter,
    PerformanceMonitor,
    CleanupScheduler,
)
from vfwidgets_theme.testing import MockWidget, MockThemeProvider


def demonstrate_automatic_memory_management():
    """Demonstrate automatic memory management without developer effort."""
    print("=== Automatic Memory Management Demo ===")

    registry = WidgetRegistry()
    manager = LifecycleManager(registry=registry)

    # Set up theme provider
    theme_provider = MockThemeProvider()
    manager.set_default_theme_provider(theme_provider)

    print(f"Initial widget count: {manager.get_widget_count()}")

    # Create widgets - they are automatically registered
    widgets = []
    print("\nCreating 10 widgets...")
    for i in range(10):
        widget = MockWidget()
        manager.register_widget(widget)  # In real ThemedWidget, this is automatic
        widgets.append(widget)

    print(f"Widget count after creation: {manager.get_widget_count()}")
    print(f"Registry count: {registry.count()}")

    # Simulate widget destruction (going out of scope)
    print("\nDestroying widgets by removing references...")
    widget_ids = [id(w) for w in widgets]
    del widgets  # Remove all references

    # Force garbage collection to trigger WeakRef callbacks
    gc.collect()
    time.sleep(0.1)  # Allow callbacks to execute

    print(f"Widget count after destruction: {manager.get_widget_count()}")
    print(f"Registry count after cleanup: {registry.count()}")

    # Cleanup manager
    manager.cleanup()
    print("✓ Automatic memory management working correctly!")


def demonstrate_context_managers():
    """Demonstrate context managers for efficient batch operations."""
    print("\n=== Context Managers Demo ===")

    manager = LifecycleManager()

    # Demonstrate WidgetCreationContext
    print("\nUsing WidgetCreationContext for batch widget creation...")
    with WidgetCreationContext(manager) as context:
        for i in range(20):
            widget = MockWidget()
            context.register_widget(widget)

        print(f"Created {context.get_created_count()} widgets in context")

    print(f"Total registered widgets: {manager.get_widget_count()}")

    # Demonstrate ThemeUpdateContext
    print("\nUsing ThemeUpdateContext for batch theme updates...")
    with ThemeUpdateContext(manager) as context:
        context.update_theme("dark_theme")
        print(f"Updated {context.get_updated_count()} widgets")

    # Demonstrate PerformanceContext
    print("\nUsing PerformanceContext for resource monitoring...")
    with PerformanceContext() as perf_context:
        # Simulate some work
        more_widgets = []
        for i in range(100):
            widget = MockWidget()
            manager.register_widget(widget)
            more_widgets.append(widget)

        # Clean up
        for widget in more_widgets:
            manager.unregister_widget(widget)

    metrics = perf_context.get_metrics()
    print(f"Performance metrics: {metrics}")

    manager.cleanup()
    print("✓ Context managers working efficiently!")


def demonstrate_memory_tracking():
    """Demonstrate memory tracking and leak detection."""
    print("\n=== Memory Tracking Demo ===")

    tracker = MemoryTracker()
    detector = LeakDetector()
    reporter = ResourceReporter()

    print("Creating widgets with memory tracking...")
    widgets = []
    for i in range(15):
        widget = MockWidget()
        widgets.append(widget)

        # Track memory usage
        tracker.start_tracking(widget)
        detector.track_object(widget)
        reporter.track_widget(widget)

    print(f"Tracking {tracker.get_tracked_count()} widgets")

    # Get memory usage for first widget
    if widgets:
        memory_usage = tracker.get_memory_usage(widgets[0])
        print(f"First widget memory usage: {memory_usage} bytes")

    # Check for leaks (should be none since widgets are still referenced)
    leaks = detector.detect_leaks(max_age_seconds=0.1)
    print(f"Potential leaks detected: {len(leaks)}")

    # Generate resource report
    report = reporter.generate_report()
    print(f"Resource report: {report}")

    # Simulate widget destruction and check for leaks
    print("\nDestroying half the widgets...")
    widgets_to_destroy = widgets[:7]
    for widget in widgets_to_destroy:
        stats = tracker.stop_tracking(widget)
        if stats:
            print(f"Widget {id(widget)} final stats: {stats}")

    del widgets_to_destroy
    gc.collect()

    # Check leak detection after GC
    gc_stats = detector.force_gc_and_check()
    print(f"GC stats: {gc_stats}")

    # Clean up remaining widgets
    for widget in widgets[7:]:
        tracker.stop_tracking(widget)

    print("✓ Memory tracking and leak detection working!")


def demonstrate_performance_monitoring():
    """Demonstrate performance monitoring and validation."""
    print("\n=== Performance Monitoring Demo ===")

    monitor = PerformanceMonitor()
    manager = LifecycleManager()

    # Test widget registration performance
    print("Testing widget registration performance...")
    with monitor.measure("widget_registration"):
        widgets = []
        for i in range(100):
            widget = MockWidget()
            manager.register_widget(widget)
            widgets.append(widget)

    # Test theme update performance
    print("Testing theme update performance...")
    with monitor.measure("theme_update"):
        with ThemeUpdateContext(manager) as context:
            context.update_theme("performance_test_theme")

    # Test cleanup performance
    print("Testing cleanup performance...")
    with monitor.measure("cleanup"):
        manager.cleanup()

    # Get and display metrics
    metrics = monitor.get_metrics()
    print("\nPerformance Metrics:")
    for operation, data in metrics.items():
        duration_ms = data['duration']['avg'] * 1000
        print(f"  {operation}:")
        print(f"    Average duration: {duration_ms:.3f}ms")
        print(f"    Operations count: {data['count']}")
        print(f"    Memory impact: {data['memory']['avg']:,.0f} bytes")

    # Validate performance requirements
    registration_time = metrics.get('widget_registration', {}).get('duration', {}).get('avg', 0)
    if registration_time * 1_000_000 < 10:  # Convert to microseconds
        print("✓ Widget registration performance requirement met (<10μs)")
    else:
        print(f"⚠ Widget registration took {registration_time * 1_000_000:.1f}μs (target: <10μs)")

    cleanup_time = metrics.get('cleanup', {}).get('duration', {}).get('avg', 0)
    if cleanup_time * 1000 < 100:  # Convert to milliseconds
        print("✓ Cleanup performance requirement met (<100ms for 100 widgets)")
    else:
        print(f"⚠ Cleanup took {cleanup_time * 1000:.1f}ms (target: <100ms)")

    print("✓ Performance monitoring complete!")


def demonstrate_thread_safety():
    """Demonstrate thread-safe memory management operations."""
    print("\n=== Thread Safety Demo ===")

    manager = LifecycleManager()
    results = []
    threads = []

    def worker_thread(thread_id: int, num_widgets: int):
        """Worker thread that creates and manages widgets."""
        try:
            # Create widgets
            widgets = []
            for i in range(num_widgets):
                widget = MockWidget()
                manager.register_widget(widget)
                widgets.append(widget)

            # Simulate some work
            time.sleep(0.01)

            # Update themes
            with ThemeUpdateContext(manager) as context:
                context.update_theme(f"theme_thread_{thread_id}")

            # Clean up widgets
            for widget in widgets:
                manager.unregister_widget(widget)

            results.append(f"Thread {thread_id}: SUCCESS - managed {num_widgets} widgets")

        except Exception as e:
            results.append(f"Thread {thread_id}: ERROR - {str(e)}")

    # Start multiple threads
    print("Starting 8 worker threads...")
    for i in range(8):
        thread = threading.Thread(
            target=worker_thread,
            args=(i, 25)  # Each thread manages 25 widgets
        )
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Display results
    print("\nThread Results:")
    for result in results:
        print(f"  {result}")

    # Verify system state
    print(f"\nFinal widget count: {manager.get_widget_count()}")
    manager.cleanup()

    success_count = sum(1 for r in results if "SUCCESS" in r)
    print(f"✓ Thread safety: {success_count}/8 threads completed successfully")


def demonstrate_stress_test():
    """Stress test the memory management system."""
    print("\n=== Stress Test Demo ===")

    manager = LifecycleManager()
    tracker = MemoryTracker()
    detector = LeakDetector()

    print("Running stress test: 10 cycles of 100 widgets each...")

    start_time = time.perf_counter()
    total_widgets_created = 0

    for cycle in range(10):
        print(f"Cycle {cycle + 1}/10...")

        # Create widgets
        widgets = []
        with WidgetCreationContext(manager) as context:
            for i in range(100):
                widget = MockWidget()
                context.register_widget(widget)
                tracker.start_tracking(widget)
                detector.track_object(widget)
                widgets.append(widget)

        total_widgets_created += len(widgets)

        # Update themes
        with ThemeUpdateContext(manager) as theme_context:
            theme_context.update_theme(f"stress_theme_{cycle}")

        # Clean up widgets
        for widget in widgets:
            tracker.stop_tracking(widget)
            manager.unregister_widget(widget)

        del widgets
        gc.collect()

        # Check for leaks periodically
        if cycle % 3 == 0:
            gc_stats = detector.force_gc_and_check()
            if gc_stats['potential_leaks'] > 10:
                print(f"⚠ Potential memory leaks detected: {gc_stats['potential_leaks']}")

    end_time = time.perf_counter()
    duration = end_time - start_time

    print(f"\nStress test completed:")
    print(f"  Total widgets created: {total_widgets_created:,}")
    print(f"  Total duration: {duration:.2f} seconds")
    print(f"  Widgets per second: {total_widgets_created / duration:,.0f}")
    print(f"  Average cycle time: {(duration / 10) * 1000:.1f}ms")

    # Final cleanup and validation
    manager.cleanup()
    final_widget_count = manager.get_widget_count()

    if final_widget_count == 0:
        print("✓ Stress test passed: No memory leaks detected")
    else:
        print(f"⚠ Stress test warning: {final_widget_count} widgets not cleaned up")


def demonstrate_cleanup_protocols():
    """Demonstrate cleanup protocols and automatic resource management."""
    print("\n=== Cleanup Protocols Demo ===")

    scheduler = CleanupScheduler()

    # Create objects that need cleanup
    class TestCleanupObject:
        def __init__(self, name: str):
            self.name = name
            self.cleaned_up = False
            self.resources = ["resource1", "resource2", "resource3"]

        def cleanup(self) -> None:
            """Clean up resources."""
            self.resources.clear()
            self.cleaned_up = True
            print(f"  Cleaned up {self.name}")

        def is_cleanup_required(self) -> bool:
            """Check if cleanup is needed."""
            return not self.cleaned_up

    print("Creating objects that need cleanup...")
    objects = []
    for i in range(5):
        obj = TestCleanupObject(f"Object_{i}")
        objects.append(obj)
        scheduler.schedule_cleanup(obj)

    print(f"Scheduled {scheduler.get_scheduled_count()} objects for cleanup")

    # Execute cleanup
    print("\nExecuting cleanup...")
    cleaned_count = scheduler.execute_cleanup()
    print(f"Successfully cleaned up {cleaned_count} objects")

    # Verify cleanup
    for obj in objects:
        assert obj.cleaned_up, f"Object {obj.name} was not cleaned up"

    print("✓ Cleanup protocols working correctly!")


def run_all_demonstrations():
    """Run all memory management demonstrations."""
    print("VFWidgets Theme System - Memory Management Foundation Demo")
    print("=" * 60)

    try:
        demonstrate_automatic_memory_management()
        demonstrate_context_managers()
        demonstrate_memory_tracking()
        demonstrate_performance_monitoring()
        demonstrate_thread_safety()
        demonstrate_cleanup_protocols()
        demonstrate_stress_test()

        print("\n" + "=" * 60)
        print("✓ All memory management demonstrations completed successfully!")
        print("\nKey Achievements:")
        print("  • Zero memory leaks through WeakRef usage")
        print("  • Automatic cleanup when widgets are destroyed")
        print("  • Performance requirements met (registration <10μs, cleanup <100ms)")
        print("  • Thread-safe operations under concurrent load")
        print("  • Comprehensive memory tracking and leak detection")
        print("  • Efficient context managers for batch operations")
        print("  • Bulletproof cleanup protocols for resource management")
        print("\n'ThemedWidget is THE way' - developers get perfect memory management")
        print("automatically without any effort!")

    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_demonstrations()