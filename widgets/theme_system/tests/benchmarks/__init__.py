"""
Performance Benchmarking Suite for VFWidgets Theme System

This module provides comprehensive performance benchmarking with:
- Micro-benchmarks for critical paths
- Macro-benchmarks for real scenarios
- Performance tracking over time
- Regression detection
- Report generation
"""

from .results import BenchmarkResults
from .runner import BenchmarkRunner
from .suite import BenchmarkSuite

__all__ = ["BenchmarkSuite", "BenchmarkRunner", "BenchmarkResults"]
