#!/usr/bin/env python3
"""
Benchmark Runner with Advanced Features
"""

import threading
import time
from dataclasses import dataclass
from typing import Any, Callable, Optional

from .suite import BenchmarkResult, BenchmarkSuite


@dataclass
class BenchmarkConfig:
    """Configuration for benchmark execution."""

    iterations: int = 100
    warmup: int = 10
    timeout: float = 60.0  # seconds
    parallel: bool = False
    processes: int = 1
    threads: int = 1


class BenchmarkRunner:
    """Advanced benchmark runner with parallel execution support."""

    def __init__(self, suite: BenchmarkSuite):
        self.suite = suite
        self.configs: dict[str, BenchmarkConfig] = {}

    def configure_benchmark(self, name: str, config: BenchmarkConfig):
        """Configure a specific benchmark."""
        self.configs[name] = config

    def run_benchmark_with_config(
        self, benchmark_func: Callable, config: BenchmarkConfig
    ) -> BenchmarkResult:
        """Run a benchmark with specific configuration."""
        if config.parallel and config.processes > 1:
            return self._run_parallel_process(benchmark_func, config)
        elif config.parallel and config.threads > 1:
            return self._run_parallel_thread(benchmark_func, config)
        else:
            return self._run_sequential(benchmark_func, config)

    def _run_sequential(self, benchmark_func: Callable, config: BenchmarkConfig) -> BenchmarkResult:
        """Run benchmark sequentially."""
        # Create a temporary benchmark suite for this run
        temp_suite = BenchmarkSuite(self.suite.results_dir)

        @temp_suite.benchmark(iterations=config.iterations, warmup=config.warmup)
        def wrapped_benchmark():
            return benchmark_func()

        return wrapped_benchmark()

    def _run_parallel_thread(
        self, benchmark_func: Callable, config: BenchmarkConfig
    ) -> BenchmarkResult:
        """Run benchmark with multiple threads."""
        results = []
        exceptions = []

        def worker():
            try:
                start_time = time.perf_counter()
                benchmark_func()
                end_time = time.perf_counter()
                results.append(end_time - start_time)
            except Exception as e:
                exceptions.append(e)

        # Warmup
        for _ in range(config.warmup):
            worker()

        results.clear()
        exceptions.clear()

        # Actual benchmark with threading
        threads = []
        iterations_per_thread = max(1, config.iterations // config.threads)

        for thread_id in range(config.threads):
            thread_iterations = iterations_per_thread
            if thread_id == config.threads - 1:
                # Last thread gets any remaining iterations
                thread_iterations = config.iterations - (thread_id * iterations_per_thread)

            def thread_worker(iterations=thread_iterations):
                for _ in range(iterations):
                    worker()

            thread = threading.Thread(target=thread_worker)
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        if exceptions:
            raise exceptions[0]

        # Calculate statistics (simplified)
        if not results:
            raise RuntimeError("No successful benchmark iterations")

        import statistics

        return BenchmarkResult(
            name=f"{benchmark_func.__name__}_threaded",
            duration=sum(results),
            iterations=len(results),
            min_time=min(results),
            max_time=max(results),
            mean_time=statistics.mean(results),
            median_time=statistics.median(results),
            std_dev=statistics.stdev(results) if len(results) > 1 else 0.0,
            memory_usage=0.0,  # TODO: Implement memory tracking for threaded
            timestamp=time.time(),
            metadata={"threads": config.threads},
        )

    def _run_parallel_process(
        self, benchmark_func: Callable, config: BenchmarkConfig
    ) -> BenchmarkResult:
        """Run benchmark with multiple processes."""
        # Note: This is a simplified implementation
        # Process-based benchmarking is complex due to serialization requirements
        # For now, fall back to threading
        return self._run_parallel_thread(benchmark_func, config)

    def run_stress_test(
        self, benchmark_func: Callable, duration_seconds: float = 60.0
    ) -> dict[str, Any]:
        """Run stress test for a specified duration."""
        print(f"Running stress test for {duration_seconds} seconds...")

        start_time = time.time()
        end_time = start_time + duration_seconds

        iterations = 0
        times = []
        errors = 0

        while time.time() < end_time:
            try:
                iteration_start = time.perf_counter()
                benchmark_func()
                iteration_end = time.perf_counter()

                times.append(iteration_end - iteration_start)
                iterations += 1

                # Print progress every 100 iterations
                if iterations % 100 == 0:
                    elapsed = time.time() - start_time
                    remaining = duration_seconds - elapsed
                    print(
                        f"  Progress: {elapsed:.1f}s elapsed, {remaining:.1f}s remaining, "
                        f"{iterations} iterations"
                    )

            except Exception as e:
                errors += 1
                if errors > 10:  # Stop if too many errors
                    print(f"Stopping stress test due to excessive errors: {e}")
                    break

        total_time = time.time() - start_time

        if not times:
            return {
                "error": "No successful iterations",
                "total_time": total_time,
                "iterations": iterations,
                "errors": errors,
            }

        import statistics

        return {
            "total_time": total_time,
            "iterations": iterations,
            "errors": errors,
            "iterations_per_second": iterations / total_time,
            "mean_time": statistics.mean(times),
            "median_time": statistics.median(times),
            "min_time": min(times),
            "max_time": max(times),
            "std_dev": statistics.stdev(times) if len(times) > 1 else 0.0,
        }

    def run_load_test(
        self, benchmark_func: Callable, concurrent_users: int = 10, duration_seconds: float = 30.0
    ) -> dict[str, Any]:
        """Run load test with multiple concurrent 'users'."""
        print(
            f"Running load test with {concurrent_users} concurrent users for {duration_seconds} seconds..."
        )

        results = []
        exceptions = []

        def user_worker():
            """Simulate a user running the benchmark repeatedly."""
            user_start = time.time()
            user_end = user_start + duration_seconds
            user_iterations = 0
            user_times = []

            while time.time() < user_end:
                try:
                    iteration_start = time.perf_counter()
                    benchmark_func()
                    iteration_end = time.perf_counter()

                    user_times.append(iteration_end - iteration_start)
                    user_iterations += 1

                except Exception as e:
                    exceptions.append(e)
                    break

            results.append(
                {
                    "iterations": user_iterations,
                    "times": user_times,
                    "total_time": time.time() - user_start,
                }
            )

        # Run concurrent users
        threads = []
        for user_id in range(concurrent_users):
            thread = threading.Thread(target=user_worker, name=f"User-{user_id}")
            threads.append(thread)
            thread.start()

        # Wait for all users
        for thread in threads:
            thread.join()

        # Aggregate results
        total_iterations = sum(r["iterations"] for r in results)
        all_times = []
        for r in results:
            all_times.extend(r["times"])

        if not all_times:
            return {
                "error": "No successful iterations",
                "concurrent_users": concurrent_users,
                "exceptions": len(exceptions),
            }

        import statistics

        return {
            "concurrent_users": concurrent_users,
            "total_iterations": total_iterations,
            "total_exceptions": len(exceptions),
            "iterations_per_second": total_iterations / duration_seconds,
            "mean_time": statistics.mean(all_times),
            "median_time": statistics.median(all_times),
            "min_time": min(all_times),
            "max_time": max(all_times),
            "std_dev": statistics.stdev(all_times) if len(all_times) > 1 else 0.0,
            "per_user_results": results,
        }

    def profile_benchmark(
        self, benchmark_func: Callable, profiler: str = "cprofile"
    ) -> dict[str, Any]:
        """Profile a benchmark to identify bottlenecks."""
        if profiler == "cprofile":
            return self._profile_with_cprofile(benchmark_func)
        else:
            return {"error": f"Unsupported profiler: {profiler}"}

    def _profile_with_cprofile(self, benchmark_func: Callable) -> dict[str, Any]:
        """Profile using cProfile."""
        import cProfile
        import io
        import pstats

        profiler = cProfile.Profile()
        profiler.enable()

        try:
            # Run benchmark multiple times for better profiling data
            for _ in range(10):
                benchmark_func()
        except Exception as e:
            return {"error": f"Profiling failed: {e}"}
        finally:
            profiler.disable()

        # Analyze results
        stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stream)
        stats.sort_stats("cumulative")
        stats.print_stats(20)  # Top 20 functions

        profile_output = stream.getvalue()

        return {
            "profile_output": profile_output,
            "total_calls": stats.total_calls,
        }

    def compare_benchmarks(
        self, benchmark_funcs: list[Callable], names: Optional[list[str]] = None
    ) -> dict[str, Any]:
        """Compare multiple benchmark functions."""
        if names is None:
            names = [func.__name__ for func in benchmark_funcs]

        results = {}

        for func, name in zip(benchmark_funcs, names):
            print(f"Running comparison benchmark: {name}")
            try:
                # Run each benchmark with standard config
                config = BenchmarkConfig(iterations=50, warmup=5)
                result = self.run_benchmark_with_config(func, config)
                results[name] = result
            except Exception as e:
                results[name] = {"error": str(e)}

        # Find best and worst performers
        valid_results = {
            name: result for name, result in results.items() if isinstance(result, BenchmarkResult)
        }

        if valid_results:
            best = min(valid_results.items(), key=lambda x: x[1].mean_time)
            worst = max(valid_results.items(), key=lambda x: x[1].mean_time)

            return {
                "results": results,
                "best_performer": {"name": best[0], "time": best[1].mean_time},
                "worst_performer": {"name": worst[0], "time": worst[1].mean_time},
                "comparison_factor": (
                    worst[1].mean_time / best[1].mean_time
                    if best[1].mean_time > 0
                    else float("inf")
                ),
            }
        else:
            return {"results": results, "error": "No valid benchmark results"}


if __name__ == "__main__":
    # Example usage
    from vfwidgets_theme import ThemedWidget

    def sample_benchmark():
        """Sample benchmark function."""
        widget = ThemedWidget()
        widget.resize(100, 100)
        widget.deleteLater()
        time.sleep(0.001)  # Simulate some work

    suite = BenchmarkSuite()
    runner = BenchmarkRunner(suite)

    # Run stress test
    stress_results = runner.run_stress_test(sample_benchmark, duration_seconds=5.0)
    print(
        f"Stress test results: {stress_results['iterations']} iterations in {stress_results['total_time']:.2f}s"
    )
