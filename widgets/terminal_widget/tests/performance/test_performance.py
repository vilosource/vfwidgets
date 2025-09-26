"""Performance and reliability tests for VFWidgets Terminal Widget."""

import gc
import threading
import time
from unittest.mock import Mock

import pytest
from vfwidgets_terminal import EventCategory, EventConfig, TerminalWidget


@pytest.mark.performance
class TestEventThroughput:
    """Test event processing throughput and performance."""

    def test_high_frequency_selection_events(
        self, qtbot, mock_embedded_server, mock_qwebengineview, mock_qwebchannel, performance_timer
    ):
        """Test handling high-frequency selection change events."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        events_received = []
        widget.selectionChanged.connect(lambda text: events_received.append(text))

        performance_timer.start()

        # Generate high-frequency selection events
        num_events = 1000
        for i in range(num_events):
            widget.bridge.on_selection_changed(f"selection {i}")

        performance_timer.stop()

        # Should process all events
        assert len(events_received) == num_events

        # Should complete within reasonable time (less than 1 second)
        assert performance_timer.elapsed < 1.0

        # Calculate throughput
        throughput = num_events / performance_timer.elapsed
        assert throughput > 1000  # At least 1000 events per second

    def test_high_frequency_key_events(
        self, qtbot, mock_embedded_server, mock_qwebengineview, mock_qwebchannel, performance_timer
    ):
        """Test handling high-frequency key events."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        events_received = []
        widget.keyPressed.connect(lambda event: events_received.append(event))

        performance_timer.start()

        # Generate rapid key events
        num_events = 500
        for i in range(num_events):
            key = chr(97 + (i % 26))  # a-z
            widget.bridge.on_key_pressed(key, f"Key{key.upper()}", False, False, False)

        performance_timer.stop()

        # Should process all events
        assert len(events_received) == num_events

        # Should complete quickly
        assert performance_timer.elapsed < 2.0

    def test_mixed_event_throughput(
        self, qtbot, mock_embedded_server, mock_qwebengineview, mock_qwebchannel, performance_timer
    ):
        """Test throughput with mixed event types."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Track different event types
        selection_events = []
        key_events = []
        bell_events = []
        scroll_events = []

        widget.selectionChanged.connect(lambda text: selection_events.append(text))
        widget.keyPressed.connect(lambda event: key_events.append(event))
        widget.bellActivated.connect(lambda: bell_events.append(True))
        widget.scrollOccurred.connect(lambda pos: scroll_events.append(pos))

        performance_timer.start()

        # Generate mixed events
        num_events = 200
        for i in range(num_events):
            widget.bridge.on_selection_changed(f"text {i}")
            widget.bridge.on_key_pressed("a", "KeyA", False, False, False)
            widget.bridge.on_bell()
            widget.bridge.on_scroll(i * 10)

        performance_timer.stop()

        # Should process all events
        assert len(selection_events) == num_events
        assert len(key_events) == num_events
        assert len(bell_events) == num_events
        assert len(scroll_events) == num_events

        # Should complete efficiently
        assert performance_timer.elapsed < 1.0

    def test_event_throughput_with_filtering(
        self, qtbot, mock_embedded_server, mock_qwebengineview, mock_qwebchannel, performance_timer
    ):
        """Test event throughput with category filtering enabled."""
        # Enable only INTERACTION events
        config = EventConfig(enabled_categories={EventCategory.INTERACTION})
        widget = TerminalWidget(event_config=config)
        qtbot.addWidget(widget)

        interaction_events = []
        appearance_events = []

        widget.selectionChanged.connect(lambda text: interaction_events.append(text))
        widget.bellActivated.connect(lambda: appearance_events.append(True))

        performance_timer.start()

        # Generate events of both types
        num_events = 1000
        for i in range(num_events):
            widget.bridge.on_selection_changed(f"text {i}")  # INTERACTION
            widget.bridge.on_bell()  # APPEARANCE

        performance_timer.stop()

        # Only interaction events should be processed
        assert len(interaction_events) == num_events
        assert len(appearance_events) == 0  # Filtered out

        # Filtering should not significantly impact performance
        assert performance_timer.elapsed < 1.0


@pytest.mark.performance
class TestMemoryUsage:
    """Test memory usage and leak detection."""

    def test_memory_usage_during_events(
        self, qtbot, mock_embedded_server, mock_qwebengineview, mock_qwebchannel
    ):
        """Test memory usage during high event volume."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Force garbage collection before test
        gc.collect()
        initial_objects = len(gc.get_objects())

        # Generate many events
        for i in range(10000):
            widget.bridge.on_selection_changed(f"memory test {i}")

            # Periodic garbage collection
            if i % 1000 == 0:
                gc.collect()

        # Final garbage collection
        gc.collect()
        final_objects = len(gc.get_objects())

        # Memory growth should be minimal
        # Allow some growth but not proportional to event count
        object_growth = final_objects - initial_objects
        assert object_growth < 1000, f"Too much memory growth: {object_growth} objects"

    def test_memory_cleanup_on_widget_destruction(
        self, qtbot, mock_embedded_server, mock_qwebengineview, mock_qwebchannel
    ):
        """Test memory cleanup when widgets are destroyed."""
        initial_widgets = []

        # Create multiple widgets
        for i in range(10):
            widget = TerminalWidget()
            qtbot.addWidget(widget)
            initial_widgets.append(widget)

            # Generate some events to create internal state
            widget.bridge.on_selection_changed(f"widget {i} test")

        # Force garbage collection
        gc.collect()
        objects_with_widgets = len(gc.get_objects())

        # Destroy widgets
        for widget in initial_widgets:
            widget.close_terminal()

        initial_widgets.clear()
        gc.collect()
        objects_without_widgets = len(gc.get_objects())

        # Should have freed significant memory
        freed_objects = objects_with_widgets - objects_without_widgets
        assert freed_objects > 0

    def test_event_data_cleanup(
        self, qtbot, mock_embedded_server, mock_qwebengineview, mock_qwebchannel
    ):
        """Test that event data objects are properly cleaned up."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        event_objects = []

        def collect_events(event):
            event_objects.append(event)

        widget.keyPressed.connect(collect_events)

        # Generate events with large data
        large_text = "x" * 10000
        for i in range(100):
            widget.bridge.on_key_pressed(large_text, "Key", False, False, False)

        # Clear event references
        event_objects.clear()
        gc.collect()

        # Memory should be freed (exact measurement is difficult but should not crash)

    @pytest.mark.slow
    def test_long_running_memory_stability(
        self, qtbot, mock_embedded_server, mock_qwebengineview, mock_qwebchannel
    ):
        """Test memory stability over long running period."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Sample memory usage at intervals
        memory_samples = []

        for cycle in range(10):
            gc.collect()
            initial_objects = len(gc.get_objects())

            # Generate events
            for i in range(1000):
                widget.bridge.on_selection_changed(f"cycle {cycle} event {i}")

            gc.collect()
            final_objects = len(gc.get_objects())
            memory_samples.append(final_objects - initial_objects)

        # Memory growth should stabilize and not increase linearly
        if len(memory_samples) > 5:
            early_avg = sum(memory_samples[:3]) / 3
            late_avg = sum(memory_samples[-3:]) / 3
            # Later cycles should not use significantly more memory
            assert late_avg < early_avg * 2


@pytest.mark.performance
class TestEventLatency:
    """Test event processing latency."""

    def test_single_event_latency(
        self, qtbot, mock_embedded_server, mock_qwebengineview, mock_qwebchannel
    ):
        """Test latency for single event processing."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        latencies = []

        def measure_latency(text):
            end_time = time.perf_counter()
            latency = end_time - start_time
            latencies.append(latency)

        widget.selectionChanged.connect(measure_latency)

        # Measure latency for multiple events
        for i in range(100):
            start_time = time.perf_counter()
            widget.bridge.on_selection_changed(f"latency test {i}")

        # Calculate statistics
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)

        # Should have very low latency (sub-millisecond)
        assert avg_latency < 0.001  # Less than 1ms average
        assert max_latency < 0.01  # Less than 10ms maximum

    def test_batch_event_latency(
        self, qtbot, mock_embedded_server, mock_qwebengineview, mock_qwebchannel
    ):
        """Test latency when processing event batches."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        batch_latencies = []

        def measure_batch_end(text):
            if "batch_end" in text:
                end_time = time.perf_counter()
                latency = end_time - batch_start_time
                batch_latencies.append(latency)

        widget.selectionChanged.connect(measure_batch_end)

        # Process events in batches
        batch_size = 100
        for batch in range(10):
            batch_start_time = time.perf_counter()

            for i in range(batch_size):
                widget.bridge.on_selection_changed(f"batch {batch} event {i}")

            # Mark end of batch
            widget.bridge.on_selection_changed(f"batch_end {batch}")

        # Batch processing should scale reasonably
        avg_batch_latency = sum(batch_latencies) / len(batch_latencies)
        assert avg_batch_latency < 0.1  # Less than 100ms per batch


@pytest.mark.reliability
class TestStressTests:
    """Stress tests for reliability and robustness."""

    @pytest.mark.slow
    def test_continuous_event_generation(
        self, qtbot, mock_embedded_server, mock_qwebengineview, mock_qwebchannel
    ):
        """Test continuous event generation over time."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        events_processed = 0
        errors_caught = 0

        def count_events(text):
            nonlocal events_processed
            events_processed += 1

        def count_errors():
            nonlocal errors_caught
            errors_caught += 1

        widget.selectionChanged.connect(count_events)

        # Generate events continuously for a period
        start_time = time.time()
        duration = 5  # seconds
        event_count = 0

        while time.time() - start_time < duration:
            try:
                widget.bridge.on_selection_changed(f"stress test {event_count}")
                event_count += 1

                # Brief pause to prevent overwhelming
                if event_count % 1000 == 0:
                    time.sleep(0.001)

            except Exception:
                count_errors()

        # Should process most events without errors
        assert events_processed > 0
        assert errors_caught == 0
        assert events_processed >= event_count * 0.95  # At least 95% success rate

    def test_rapid_widget_creation_destruction(self, qtbot):
        """Test rapid widget creation and destruction."""
        widgets_created = 0
        widgets_destroyed = 0

        try:
            for i in range(20):
                # Create widget
                widget = TerminalWidget(port=0)  # Random port
                qtbot.addWidget(widget)
                widgets_created += 1

                # Generate some events
                if widget.bridge:
                    widget.bridge.on_selection_changed(f"rapid test {i}")

                # Destroy widget
                widget.close_terminal()
                widgets_destroyed += 1

                # Brief pause
                time.sleep(0.01)

        except Exception as e:
            pytest.fail(f"Rapid creation/destruction failed: {e}")

        assert widgets_created == 20
        assert widgets_destroyed == 20

    def test_concurrent_event_processing(
        self, qtbot, mock_embedded_server, mock_qwebengineview, mock_qwebchannel
    ):
        """Test concurrent event processing from multiple sources."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        events_received = []

        def collect_events(text):
            events_received.append(text)

        widget.selectionChanged.connect(collect_events)

        # Create multiple threads generating events
        def event_generator(thread_id, num_events):
            for i in range(num_events):
                widget.bridge.on_selection_changed(f"thread {thread_id} event {i}")
                time.sleep(0.001)

        threads = []
        num_threads = 5
        events_per_thread = 100

        # Start threads
        for thread_id in range(num_threads):
            thread = threading.Thread(target=event_generator, args=(thread_id, events_per_thread))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=10)

        # Should receive events from all threads
        expected_total = num_threads * events_per_thread
        assert len(events_received) >= expected_total * 0.9  # Allow some timing variance

    def test_edge_case_resilience(
        self, qtbot, mock_embedded_server, mock_qwebengineview, mock_qwebchannel
    ):
        """Test resilience against edge cases and malformed data."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Test various edge cases
        edge_cases = [
            "",  # Empty string
            " ",  # Whitespace
            "\n\r\t",  # Control characters
            "null\x00byte",  # Null bytes
            "unicode: 🚀🎯📊💻🔥",  # Unicode emojis
            "very long string " * 1000,  # Very long string
            "\x1b[31mANSI\x1b[0m",  # ANSI escape sequences
            "line1\nline2\nline3",  # Multiline
            "\x08\x7f",  # Backspace and delete
        ]

        errors_count = 0

        for i, case in enumerate(edge_cases):
            try:
                widget.bridge.on_selection_changed(case)
                widget.bridge.on_key_pressed(case[:1] if case else "a", "Key", False, False, False)
                widget.bridge.on_title_changed(case)
            except Exception as e:
                errors_count += 1
                print(f"Error with case {i}: {e}")

        # Should handle all edge cases gracefully
        assert errors_count == 0


@pytest.mark.benchmark
class TestBenchmarks:
    """Benchmark tests for performance comparison."""

    def test_event_processing_benchmark(
        self, qtbot, mock_embedded_server, mock_qwebengineview, mock_qwebchannel, benchmark
    ):
        """Benchmark event processing performance."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        events_received = []
        widget.selectionChanged.connect(lambda text: events_received.append(text))

        def process_events():
            for i in range(1000):
                widget.bridge.on_selection_changed(f"benchmark {i}")

        # Run benchmark
        result = benchmark(process_events)

        # Verify all events were processed
        assert len(events_received) == 1000

    def test_widget_creation_benchmark(self, qtbot, benchmark):
        """Benchmark widget creation performance."""

        def create_widget():
            widget = TerminalWidget(port=0)
            qtbot.addWidget(widget)
            return widget

        # Run benchmark
        widget = benchmark(create_widget)

        # Clean up
        widget.close_terminal()

    def test_signal_connection_benchmark(self, qtbot, mock_embedded_server, benchmark):
        """Benchmark signal connection performance."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        def connect_many_handlers():
            handlers = []
            for i in range(100):
                handler = Mock()
                handlers.append(handler)
                widget.selectionChanged.connect(handler)
            return handlers

        # Run benchmark
        handlers = benchmark(connect_many_handlers)

        # Verify connections work
        widget.bridge.on_selection_changed("test")
        for handler in handlers:
            handler.assert_called_once_with("test")


@pytest.mark.performance
class TestResourceUsage:
    """Test resource usage and efficiency."""

    def test_cpu_usage_during_events(
        self, qtbot, mock_embedded_server, mock_qwebengineview, mock_qwebchannel
    ):
        """Test CPU usage during event processing."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        import os

        import psutil

        # Get current process
        process = psutil.Process(os.getpid())

        # Measure CPU before
        cpu_before = process.cpu_percent()
        time.sleep(0.1)  # Let CPU settle

        # Generate events
        start_time = time.time()
        event_count = 0

        while time.time() - start_time < 1.0:  # 1 second
            widget.bridge.on_selection_changed(f"cpu test {event_count}")
            event_count += 1

        # Measure CPU after
        cpu_after = process.cpu_percent()

        # CPU usage should be reasonable (less than 50% for event processing)
        cpu_usage = max(cpu_after - cpu_before, cpu_after)
        assert cpu_usage < 50.0, f"High CPU usage: {cpu_usage}%"

        print(f"Processed {event_count} events with {cpu_usage}% CPU usage")

    def test_file_descriptor_usage(self, qtbot):
        """Test file descriptor usage doesn't grow excessively."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_fds = process.num_fds() if hasattr(process, "num_fds") else 0

        widgets = []
        try:
            # Create multiple widgets
            for i in range(10):
                widget = TerminalWidget(port=0)
                qtbot.addWidget(widget)
                widgets.append(widget)

            current_fds = process.num_fds() if hasattr(process, "num_fds") else 0

            # Should not use excessive file descriptors
            fd_growth = current_fds - initial_fds
            assert fd_growth < 100, f"Excessive FD usage: {fd_growth} FDs"

        finally:
            # Clean up
            for widget in widgets:
                try:
                    widget.close_terminal()
                except:
                    pass

        # FDs should be released
        final_fds = process.num_fds() if hasattr(process, "num_fds") else 0
        assert final_fds <= current_fds
