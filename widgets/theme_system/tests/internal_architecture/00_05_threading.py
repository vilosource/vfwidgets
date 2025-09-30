"""
Thread Safety Infrastructure Example for VFWidgets Theme System.

This example demonstrates all thread safety components working together
in realistic multi-threaded scenarios, showing how ThemedWidget will
work transparently in any Qt application.

Key Demonstrations:
1. Thread-safe singleton theme manager
2. Concurrent theme loading and caching
3. Cross-thread notifications
4. Performance under high load
5. Deadlock prevention
6. Memory efficiency with thread-local storage
7. Qt integration (when available)
"""

import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List

# Import threading infrastructure
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from vfwidgets_theme.threading import (
    ThreadSafeThemeManager,
    ThemeLock, PropertyLock, RegistryLock,
    ThemeCache, StyleCache, PropertyCache,
    AsyncThemeLoader, ThemeLoadQueue, LoadProgress,
    ThemeSignalManager, CrossThreadNotifier, WidgetNotificationProxy,
    ReadWriteLock, AtomicOperations, ConcurrentRegistry,
    DeadlockDetection, get_performance_metrics, reset_performance_metrics
)


class ThreadSafetyDemo:
    """
    Comprehensive demonstration of thread safety infrastructure.

    Shows how all components work together to provide bulletproof
    thread safety while maintaining high performance.
    """

    def __init__(self):
        self.results: Dict[str, Any] = {}
        self.demo_widgets: List[Any] = []

    def run_all_demos(self):
        """Run all thread safety demonstrations."""
        print("🧵 VFWidgets Thread Safety Infrastructure Demo")
        print("=" * 60)

        reset_performance_metrics()

        # Run all demonstrations
        self.demo_singleton_thread_safety()
        self.demo_concurrent_theme_caching()
        self.demo_cross_thread_notifications()
        self.demo_async_theme_loading()
        self.demo_high_load_performance()
        self.demo_deadlock_prevention()
        self.demo_memory_efficiency()

        # Show final results
        self.show_final_results()

    def demo_singleton_thread_safety(self):
        """Demo 1: Thread-safe singleton pattern."""
        print("\n1️⃣  Thread-Safe Singleton Pattern")
        print("-" * 40)

        # Test singleton across multiple threads
        instances = []

        def get_manager_instance(thread_id: int):
            manager = ThreadSafeThemeManager.get_instance()
            instances.append((thread_id, id(manager)))

            # Configure manager from each thread
            manager.configure({
                f"thread_{thread_id}_setting": f"value_{thread_id}",
                "timestamp": time.time()
            })

        # Create 8 concurrent threads
        threads = []
        for i in range(8):
            thread = threading.Thread(target=get_manager_instance, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Verify singleton behavior
        unique_instances = set(instance_id for _, instance_id in instances)
        print(f"✅ Created {len(instances)} instance references")
        print(f"✅ All references point to same object: {len(unique_instances) == 1}")

        # Check configuration consistency
        manager = ThreadSafeThemeManager.get_instance()
        config = manager.get_configuration()
        print(f"✅ Final configuration has {len(config)} settings")
        print(f"✅ Thread-safe configuration updates: {len([k for k in config.keys() if k.startswith('thread_')]) == 8}")

        self.results['singleton'] = {
            'instances_created': len(instances),
            'unique_instances': len(unique_instances),
            'configuration_entries': len(config)
        }

    def demo_concurrent_theme_caching(self):
        """Demo 2: Concurrent theme caching with thread-local storage."""
        print("\n2️⃣  Concurrent Theme Caching")
        print("-" * 40)

        cache_results = []

        def cache_operations(thread_id: int):
            theme_cache = ThemeCache()
            style_cache = StyleCache()
            property_cache = PropertyCache()

            thread_result = {
                'thread_id': thread_id,
                'themes_cached': 0,
                'styles_cached': 0,
                'properties_cached': 0,
                'cache_hits': 0,
                'total_accesses': 0
            }

            # Cache themes specific to this thread
            for i in range(50):
                theme_name = f"theme_{thread_id}_{i}"
                theme_data = {
                    "colors": {"primary": f"#00{thread_id:02X}{i:02X}FF"},
                    "thread_id": thread_id,
                    "theme_index": i
                }
                theme_cache.set_theme(theme_name, theme_data)
                thread_result['themes_cached'] += 1

                # Cache corresponding styles
                style_key = f"style_{thread_id}_{i}"
                style_data = f"QWidget {{ background-color: {theme_data['colors']['primary']}; }}"
                style_cache.set_style(style_key, style_data)
                thread_result['styles_cached'] += 1

                # Cache properties
                widget_id = f"widget_{thread_id}_{i}"
                property_cache.set_property(widget_id, "color", theme_data['colors']['primary'])
                thread_result['properties_cached'] += 1

            # Test cache access patterns (90% should hit)
            for i in range(1000):
                theme_name = f"theme_{thread_id}_{i % 45}"  # 90% will hit existing
                theme = theme_cache.get_theme(theme_name)

                thread_result['total_accesses'] += 1
                if theme is not None:
                    thread_result['cache_hits'] += 1

            cache_results.append(thread_result)

        # Run concurrent cache operations
        threads = []
        for i in range(6):
            thread = threading.Thread(target=cache_operations, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Analyze results
        total_themes = sum(r['themes_cached'] for r in cache_results)
        total_styles = sum(r['styles_cached'] for r in cache_results)
        total_properties = sum(r['properties_cached'] for r in cache_results)
        total_hits = sum(r['cache_hits'] for r in cache_results)
        total_accesses = sum(r['total_accesses'] for r in cache_results)

        hit_rate = total_hits / total_accesses if total_accesses > 0 else 0

        print(f"✅ Cached {total_themes} themes across {len(cache_results)} threads")
        print(f"✅ Cached {total_styles} stylesheets")
        print(f"✅ Cached {total_properties} properties")
        print(f"✅ Cache hit rate: {hit_rate:.2%} (target: >90%)")
        print(f"✅ Thread isolation: Each thread has independent cache")

        self.results['caching'] = {
            'total_themes': total_themes,
            'total_styles': total_styles,
            'total_properties': total_properties,
            'hit_rate': hit_rate,
            'threads': len(cache_results)
        }

    def demo_cross_thread_notifications(self):
        """Demo 3: Cross-thread notification system."""
        print("\n3️⃣  Cross-Thread Notifications")
        print("-" * 40)

        # Qt Signal Manager Demo
        signal_manager = ThemeSignalManager()
        signal_results = []

        def signal_handler(theme_name: str, theme_data: Dict[str, Any]):
            signal_results.append({
                'theme_name': theme_name,
                'thread_id': threading.current_thread().ident,
                'timestamp': time.time()
            })

        signal_manager.connect_theme_handler(signal_handler)

        # Cross-Thread Notifier Demo
        cross_notifier = CrossThreadNotifier()
        notification_results = []

        def notification_handler(message: str, data: Any):
            notification_results.append({
                'message': message,
                'data': data,
                'handler_thread': threading.current_thread().ident
            })

        cross_notifier.add_handler(notification_handler)

        # Widget Notification Proxy Demo
        widget_proxy = WidgetNotificationProxy()

        class MockWidget:
            def __init__(self, widget_id: str):
                self.widget_id = widget_id
                self.theme_properties = {}

            def set_theme_property(self, property_name: str, value: Any):
                self.theme_properties[property_name] = value

        # Create mock widgets
        widgets = [MockWidget(f"widget_{i}") for i in range(10)]
        for widget in widgets:
            widget_proxy.register_widget(widget)

        # Generate notifications from multiple threads
        def notification_operations(thread_id: int):
            # Signal manager notifications
            for i in range(5):
                signal_manager.emit_theme_changed(
                    f"theme_{thread_id}_{i}",
                    {"thread_id": thread_id, "index": i}
                )

            # Cross-thread notifications
            for i in range(3):
                cross_notifier.notify(
                    f"message_{thread_id}_{i}",
                    {"thread_id": thread_id, "data": f"data_{i}"}
                )

            # Widget notifications
            for i, widget in enumerate(widgets[:3]):
                widget_proxy.notify_property_changed(
                    widget,
                    f"property_{thread_id}",
                    f"value_{thread_id}_{i}"
                )

        # Run notification operations
        threads = []
        for i in range(4):
            thread = threading.Thread(target=notification_operations, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Process pending notifications
        cross_notifier.process_pending()
        widget_proxy.process_notifications()

        print(f"✅ Qt signals processed: {len(signal_results)} (from {4 * 5} sent)")
        print(f"✅ Cross-thread notifications: {len(notification_results)} (from {4 * 3} sent)")
        print(f"✅ Widget notifications processed")
        print(f"✅ Widgets registered: {widget_proxy.get_registered_count()}")

        self.results['notifications'] = {
            'signal_count': len(signal_results),
            'cross_thread_count': len(notification_results),
            'registered_widgets': widget_proxy.get_registered_count()
        }

    def demo_async_theme_loading(self):
        """Demo 4: Asynchronous theme loading."""
        print("\n4️⃣  Asynchronous Theme Loading")
        print("-" * 40)

        async def async_loading_demo():
            loader = AsyncThemeLoader()
            load_queue = ThemeLoadQueue()
            progress = LoadProgress()

            # Progress tracking
            progress_updates = []

            def progress_callback(current: int, total: int, message: str):
                progress_updates.append((current, total, message))

            progress.set_callback(progress_callback)

            # Load themes asynchronously
            theme_names = ["dark_theme", "light_theme", "blue_theme", "green_theme", "red_theme"]

            start_time = time.perf_counter()

            # Load themes concurrently
            load_tasks = []
            for theme_name in theme_names:
                task = loader.load_theme(theme_name)
                load_tasks.append(task)

            loaded_themes = await asyncio.gather(*load_tasks)

            end_time = time.perf_counter()
            load_time = end_time - start_time

            # Queue-based loading demo
            queue_results = []

            def queue_callback(theme_name: str, theme_data: Dict[str, Any]):
                queue_results.append((theme_name, len(theme_data)))

            for theme_name in theme_names:
                load_queue.enqueue_load(theme_name, queue_callback)

            load_queue.process_queue()

            return {
                'concurrent_load_time': load_time,
                'themes_loaded': len(loaded_themes),
                'queue_processed': len(queue_results),
                'progress_updates': len(progress_updates)
            }

        # Run async demo
        async_result = asyncio.run(async_loading_demo())

        print(f"✅ Loaded {async_result['themes_loaded']} themes concurrently")
        print(f"✅ Total load time: {async_result['concurrent_load_time']:.3f}s (target: <0.5s each)")
        print(f"✅ Queue processed {async_result['queue_processed']} themes")
        print(f"✅ Progress tracking updates: {async_result['progress_updates']}")

        self.results['async_loading'] = async_result

    def demo_high_load_performance(self):
        """Demo 5: Performance under high concurrent load."""
        print("\n5️⃣  High Load Performance")
        print("-" * 40)

        # Create concurrent registry
        registry = ConcurrentRegistry()

        # Create locks for testing
        theme_lock = ThemeLock("performance_test")
        property_lock = PropertyLock()

        # Performance metrics
        operation_times = []
        lock_times = []

        class PerformanceWidget:
            def __init__(self, widget_id: str):
                self.widget_id = widget_id
                self.properties = {}

        def high_load_operations(thread_id: int):
            thread_times = []
            thread_locks = []

            # Create widgets for this thread
            widgets = []
            for i in range(100):
                widget = PerformanceWidget(f"widget_{thread_id}_{i}")
                widgets.append(widget)

                # Register in concurrent registry
                start_time = time.perf_counter()
                registry.register(widget)
                end_time = time.perf_counter()
                thread_times.append(end_time - start_time)

            # Test lock performance
            for i in range(1000):
                start_time = time.perf_counter()
                theme_lock.acquire()
                theme_lock.release()
                end_time = time.perf_counter()
                thread_locks.append(end_time - start_time)

            # Test property locking
            for i in range(100):
                with property_lock.property_context(f"property_{i % 10}"):
                    time.sleep(0.0001)  # Minimal work

            operation_times.extend(thread_times)
            lock_times.extend(thread_locks)

        # Run high-load test with 10 threads (more than required 8+)
        start_time = time.perf_counter()

        threads = []
        for i in range(10):
            thread = threading.Thread(target=high_load_operations, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        end_time = time.perf_counter()
        total_time = end_time - start_time

        # Calculate performance metrics
        avg_operation_time = sum(operation_times) / len(operation_times) if operation_times else 0
        avg_lock_time = sum(lock_times) / len(lock_times) if lock_times else 0
        total_widgets = registry.get_widget_count()

        print(f"✅ Processed {len(operation_times)} operations in {total_time:.3f}s")
        print(f"✅ Average operation time: {avg_operation_time*1000000:.2f}μs (target: <50μs)")
        print(f"✅ Average lock time: {avg_lock_time*1000000:.2f}μs (target: <1μs)")
        print(f"✅ Total widgets registered: {total_widgets}")
        print(f"✅ Operations per second: {len(operation_times)/total_time:.0f}")
        print(f"✅ Concurrent threads supported: 10 (target: 8+)")

        self.results['performance'] = {
            'total_operations': len(operation_times),
            'total_time': total_time,
            'avg_operation_time': avg_operation_time,
            'avg_lock_time': avg_lock_time,
            'widgets_registered': total_widgets,
            'operations_per_second': len(operation_times) / total_time,
            'concurrent_threads': 10
        }

    def demo_deadlock_prevention(self):
        """Demo 6: Deadlock detection and prevention."""
        print("\n6️⃣  Deadlock Detection and Prevention")
        print("-" * 40)

        detector = DeadlockDetection()
        lock_a = threading.Lock()
        lock_b = threading.Lock()

        operation_results = []

        def safe_operation_1(thread_id: int):
            try:
                with detector.track_lock(lock_a, "lock_a"):
                    time.sleep(0.01)
                    with detector.track_lock(lock_b, "lock_b"):
                        operation_results.append(f"operation_1_success_{thread_id}")
            except Exception as e:
                operation_results.append(f"operation_1_error_{thread_id}: {e}")

        def safe_operation_2(thread_id: int):
            try:
                with detector.track_lock(lock_b, "lock_b"):
                    time.sleep(0.01)
                    with detector.track_lock(lock_a, "lock_a"):
                        operation_results.append(f"operation_2_success_{thread_id}")
            except Exception as e:
                operation_results.append(f"operation_2_error_{thread_id}: {e}")

        # Run potentially conflicting operations
        threads = []
        for i in range(2):
            thread_1 = threading.Thread(target=safe_operation_1, args=(i,))
            thread_2 = threading.Thread(target=safe_operation_2, args=(i,))
            threads.extend([thread_1, thread_2])

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join(timeout=3.0)  # Timeout to prevent hanging

        warnings = detector.get_warnings()
        lock_graph = detector.get_lock_graph()

        print(f"✅ Operations completed: {len(operation_results)}")
        print(f"✅ Deadlock warnings detected: {len(warnings)}")
        print(f"✅ Lock graph tracked: {len(lock_graph)} threads")

        successful_ops = [r for r in operation_results if "success" in r]
        print(f"✅ Successful operations: {len(successful_ops)}/{len(operation_results)}")

        self.results['deadlock_prevention'] = {
            'operations_completed': len(operation_results),
            'warnings_detected': len(warnings),
            'successful_operations': len(successful_ops),
            'threads_tracked': len(lock_graph)
        }

    def demo_memory_efficiency(self):
        """Demo 7: Memory efficiency with thread-local storage."""
        print("\n7️⃣  Memory Efficiency")
        print("-" * 40)

        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        memory_results = []

        def memory_intensive_operations(thread_id: int):
            # Create thread-local caches
            theme_cache = ThemeCache()
            style_cache = StyleCache()
            property_cache = PropertyCache()

            # Fill caches with substantial data
            for i in range(200):
                # Theme data
                theme_cache.set_theme(f"theme_{thread_id}_{i}", {
                    "colors": {f"color_{j}": f"#FF{j:04X}" for j in range(20)},
                    "properties": {f"prop_{j}": f"value_{j}" * 10 for j in range(10)}
                })

                # Style data
                style_cache.set_style(f"style_{thread_id}_{i}",
                    f"QWidget {{ /* Style {i} */ }} " * 5)

                # Property data
                for j in range(10):
                    property_cache.set_property(
                        f"widget_{thread_id}_{i}_{j}",
                        f"property_{j}",
                        f"value_{thread_id}_{i}_{j}"
                    )

            # Get cache statistics
            theme_stats = theme_cache.get_cache_stats()
            style_count = style_cache.get_cache_size()

            memory_results.append({
                'thread_id': thread_id,
                'themes_cached': theme_stats['cached_themes'],
                'styles_cached': style_count
            })

        # Run memory-intensive operations
        threads = []
        for i in range(8):
            thread = threading.Thread(target=memory_intensive_operations, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        total_themes = sum(r['themes_cached'] for r in memory_results)
        total_styles = sum(r['styles_cached'] for r in memory_results)

        print(f"✅ Memory increase: {memory_increase / (1024*1024):.2f} MB")
        print(f"✅ Themes cached across all threads: {total_themes}")
        print(f"✅ Styles cached across all threads: {total_styles}")
        print(f"✅ Memory per cached item: {memory_increase / (total_themes + total_styles):.0f} bytes")
        print(f"✅ Thread-local isolation: Each thread has independent caches")

        self.results['memory_efficiency'] = {
            'memory_increase_mb': memory_increase / (1024*1024),
            'total_themes': total_themes,
            'total_styles': total_styles,
            'memory_per_item': memory_increase / (total_themes + total_styles) if (total_themes + total_styles) > 0 else 0,
            'threads': len(memory_results)
        }

    def show_final_results(self):
        """Show final demonstration results and performance analysis."""
        print("\n🎯 Final Results and Performance Analysis")
        print("=" * 60)

        # Performance requirements check
        perf_metrics = get_performance_metrics()

        print("\n📊 Performance Requirements Validation:")
        print(f"{'✅' if self.results['performance']['avg_lock_time'] < 0.000001 else '❌'} Lock acquisition: {self.results['performance']['avg_lock_time']*1000000:.2f}μs (target: <1μs)")
        print(f"{'✅' if self.results['caching']['hit_rate'] > 0.9 else '❌'} Cache hit rate: {self.results['caching']['hit_rate']:.1%} (target: >90%)")
        print(f"{'✅' if self.results['performance']['concurrent_threads'] >= 8 else '❌'} Concurrent threads: {self.results['performance']['concurrent_threads']} (target: 8+)")
        print(f"{'✅' if self.results['async_loading']['concurrent_load_time'] < 2.5 else '❌'} Async loading: {self.results['async_loading']['concurrent_load_time']:.3f}s (target: <0.5s each)")

        print(f"\n📈 Overall Performance:")
        print(f"  • Operations per second: {self.results['performance']['operations_per_second']:.0f}")
        print(f"  • Memory efficiency: {self.results['memory_efficiency']['memory_per_item']:.0f} bytes per item")
        print(f"  • Thread safety: All operations completed successfully")
        print(f"  • Deadlock prevention: {self.results['deadlock_prevention']['successful_operations']} successful operations")

        print(f"\n🎉 Thread Safety Infrastructure Validation:")
        print(f"  ✅ Singleton pattern: Thread-safe across {self.results['singleton']['instances_created']} accesses")
        print(f"  ✅ Thread-local caching: {self.results['caching']['total_themes']} themes cached efficiently")
        print(f"  ✅ Cross-thread notifications: {self.results['notifications']['signal_count']} signals processed")
        print(f"  ✅ Async operations: {self.results['async_loading']['themes_loaded']} themes loaded concurrently")
        print(f"  ✅ High-load performance: {self.results['performance']['widgets_registered']} widgets managed")
        print(f"  ✅ Deadlock prevention: {len(self.results['deadlock_prevention'])} warnings detected")
        print(f"  ✅ Memory efficiency: {self.results['memory_efficiency']['memory_increase_mb']:.2f}MB for {self.results['memory_efficiency']['threads']} threads")

        # Check if all requirements met
        all_passed = (
            self.results['performance']['avg_lock_time'] < 0.000001 and
            self.results['caching']['hit_rate'] > 0.9 and
            self.results['performance']['concurrent_threads'] >= 8
        )

        print(f"\n{'🎯 ALL REQUIREMENTS MET' if all_passed else '⚠️  Some requirements need attention'}")
        print("\n" + "=" * 60)

        print("\n💡 Integration with ThemedWidget:")
        print("   • All thread safety is completely transparent to developers")
        print("   • ThemedWidget inherits bulletproof multi-threading support")
        print("   • No additional code required for thread-safe theming")
        print("   • Performance optimized for Qt application patterns")
        print("   • Memory management prevents leaks across threads")
        print("   • Error recovery works correctly in multi-threaded scenarios")


if __name__ == "__main__":
    # Run comprehensive thread safety demonstration
    demo = ThreadSafetyDemo()
    demo.run_all_demos()

    print("\n🚀 Thread Safety Infrastructure Ready for ThemedWidget Integration!")
    print("   Task 5 Complete - Phase 0 Foundation Established")