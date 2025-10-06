#!/usr/bin/env python3
"""
Benchmark Results Analysis and Visualization
"""

import sqlite3
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List


class BenchmarkResults:
    """Analyze and visualize benchmark results."""

    def __init__(self, results_db: Path):
        self.results_db = results_db

    def get_results_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get summary of results from the last N days."""
        cutoff_date = datetime.now() - timedelta(days=days)

        with sqlite3.connect(self.results_db) as conn:
            cursor = conn.execute(
                """
                SELECT name, COUNT(*) as count,
                       AVG(mean_time) as avg_time,
                       MIN(mean_time) as best_time,
                       MAX(mean_time) as worst_time,
                       AVG(memory_usage) as avg_memory
                FROM benchmark_results
                WHERE timestamp >= ?
                GROUP BY name
                ORDER BY name
            """,
                (cutoff_date.isoformat(),),
            )

            summary = {}
            for row in cursor:
                summary[row[0]] = {
                    "runs": row[1],
                    "avg_time_ms": row[2] * 1000,
                    "best_time_ms": row[3] * 1000,
                    "worst_time_ms": row[4] * 1000,
                    "avg_memory_mb": row[5],
                    "stability": (row[4] - row[3]) / row[2] if row[2] > 0 else 0,
                }

            return summary

    def get_trend_analysis(self, benchmark_name: str, days: int = 30) -> Dict[str, Any]:
        """Analyze trends for a specific benchmark."""
        cutoff_date = datetime.now() - timedelta(days=days)

        with sqlite3.connect(self.results_db) as conn:
            cursor = conn.execute(
                """
                SELECT timestamp, mean_time, memory_usage
                FROM benchmark_results
                WHERE name = ? AND timestamp >= ?
                ORDER BY timestamp
            """,
                (benchmark_name, cutoff_date.isoformat()),
            )

            data_points = []
            for row in cursor:
                data_points.append(
                    {
                        "timestamp": datetime.fromisoformat(row[0]),
                        "mean_time": row[1],
                        "memory_usage": row[2],
                    }
                )

        if len(data_points) < 2:
            return {"error": "Not enough data points for trend analysis"}

        # Calculate trends
        times = [dp["mean_time"] for dp in data_points]
        memory_usage = [dp["memory_usage"] for dp in data_points]

        # Simple linear trend (positive = getting slower, negative = getting faster)
        time_trend = self._calculate_trend([i for i in range(len(times))], times)
        memory_trend = self._calculate_trend([i for i in range(len(memory_usage))], memory_usage)

        # Performance stability (coefficient of variation)
        time_stability = statistics.stdev(times) / statistics.mean(times) if times else 0

        return {
            "data_points": len(data_points),
            "time_trend": time_trend,
            "memory_trend": memory_trend,
            "time_stability": time_stability,
            "avg_time": statistics.mean(times),
            "avg_memory": statistics.mean(memory_usage),
            "latest_time": times[-1],
            "latest_memory": memory_usage[-1],
            "improvement_factor": times[0] / times[-1] if times[-1] > 0 else 1.0,
        }

    def _calculate_trend(self, x: List[float], y: List[float]) -> float:
        """Calculate simple linear trend (slope)."""
        if len(x) != len(y) or len(x) < 2:
            return 0.0

        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] * x[i] for i in range(n))

        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            return 0.0

        slope = (n * sum_xy - sum_x * sum_y) / denominator
        return slope

    def detect_anomalies(self, benchmark_name: str, threshold: float = 2.0) -> List[Dict[str, Any]]:
        """Detect anomalous results using standard deviation."""
        with sqlite3.connect(self.results_db) as conn:
            cursor = conn.execute(
                """
                SELECT timestamp, mean_time, memory_usage
                FROM benchmark_results
                WHERE name = ?
                ORDER BY timestamp DESC
                LIMIT 100
            """,
                (benchmark_name,),
            )

            results = []
            for row in cursor:
                results.append(
                    {
                        "timestamp": datetime.fromisoformat(row[0]),
                        "mean_time": row[1],
                        "memory_usage": row[2],
                    }
                )

        if len(results) < 10:
            return []

        # Calculate statistics
        times = [r["mean_time"] for r in results]
        mean_time = statistics.mean(times)
        std_time = statistics.stdev(times)

        # Find anomalies (results beyond threshold standard deviations)
        anomalies = []
        for result in results:
            z_score = abs(result["mean_time"] - mean_time) / std_time if std_time > 0 else 0
            if z_score > threshold:
                anomalies.append(
                    {
                        "timestamp": result["timestamp"],
                        "mean_time": result["mean_time"],
                        "expected_time": mean_time,
                        "z_score": z_score,
                        "deviation": result["mean_time"] - mean_time,
                    }
                )

        return sorted(anomalies, key=lambda x: x["z_score"], reverse=True)

    def compare_benchmarks(self, benchmark_names: List[str], days: int = 30) -> Dict[str, Any]:
        """Compare performance of multiple benchmarks."""
        cutoff_date = datetime.now() - timedelta(days=days)
        comparison = {}

        for name in benchmark_names:
            with sqlite3.connect(self.results_db) as conn:
                cursor = conn.execute(
                    """
                    SELECT AVG(mean_time) as avg_time,
                           MIN(mean_time) as best_time,
                           MAX(mean_time) as worst_time,
                           COUNT(*) as runs,
                           AVG(memory_usage) as avg_memory
                    FROM benchmark_results
                    WHERE name = ? AND timestamp >= ?
                """,
                    (name, cutoff_date.isoformat()),
                )

                row = cursor.fetchone()
                if row and row[0] is not None:
                    comparison[name] = {
                        "avg_time_ms": row[0] * 1000,
                        "best_time_ms": row[1] * 1000,
                        "worst_time_ms": row[2] * 1000,
                        "runs": row[3],
                        "avg_memory_mb": row[4] or 0,
                    }

        # Find best and worst performers
        if comparison:
            best_performer = min(comparison.items(), key=lambda x: x[1]["avg_time_ms"])
            worst_performer = max(comparison.items(), key=lambda x: x[1]["avg_time_ms"])

            return {
                "comparison": comparison,
                "best_performer": {
                    "name": best_performer[0],
                    "avg_time_ms": best_performer[1]["avg_time_ms"],
                },
                "worst_performer": {
                    "name": worst_performer[0],
                    "avg_time_ms": worst_performer[1]["avg_time_ms"],
                },
                "performance_gap": worst_performer[1]["avg_time_ms"]
                / best_performer[1]["avg_time_ms"],
            }
        else:
            return {"comparison": comparison, "error": "No data available for comparison"}

    def generate_performance_dashboard(self) -> Dict[str, Any]:
        """Generate a comprehensive performance dashboard."""
        summary = self.get_results_summary(30)

        # Get all unique benchmark names
        with sqlite3.connect(self.results_db) as conn:
            cursor = conn.execute("SELECT DISTINCT name FROM benchmark_results")
            benchmark_names = [row[0] for row in cursor.fetchall()]

        # Analyze trends for each benchmark
        trends = {}
        anomalies = {}
        for name in benchmark_names:
            trends[name] = self.get_trend_analysis(name, 30)
            anomalies[name] = self.detect_anomalies(name, 2.0)

        # Overall health assessment
        health_score = self._calculate_health_score(summary, trends)

        return {
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
            "trends": trends,
            "anomalies": anomalies,
            "health_score": health_score,
            "benchmarks_count": len(benchmark_names),
            "recommendations": self._generate_recommendations(summary, trends, anomalies),
        }

    def _calculate_health_score(
        self, summary: Dict[str, Any], trends: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate overall performance health score (0-100)."""
        scores = []

        for benchmark_name, trend_data in trends.items():
            if "error" in trend_data:
                continue

            # Stability score (lower coefficient of variation is better)
            stability_score = max(0, 100 - trend_data["time_stability"] * 1000)

            # Trend score (negative trend is good, positive is bad)
            trend_score = max(0, 100 - abs(trend_data["time_trend"]) * 10000)

            # Data availability score
            data_score = min(100, trend_data["data_points"] * 10)

            benchmark_score = (stability_score + trend_score + data_score) / 3
            scores.append(benchmark_score)

        overall_score = statistics.mean(scores) if scores else 0

        return {
            "overall_score": overall_score,
            "rating": self._score_to_rating(overall_score),
            "individual_scores": {name: score for name, score in zip(trends.keys(), scores)},
        }

    def _score_to_rating(self, score: float) -> str:
        """Convert numeric score to rating."""
        if score >= 90:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 50:
            return "Fair"
        elif score >= 30:
            return "Poor"
        else:
            return "Critical"

    def _generate_recommendations(
        self, summary: Dict[str, Any], trends: Dict[str, Any], anomalies: Dict[str, Any]
    ) -> List[str]:
        """Generate performance improvement recommendations."""
        recommendations = []

        # Check for performance regressions
        for name, trend_data in trends.items():
            if "error" in trend_data:
                continue

            if trend_data["time_trend"] > 0.00001:  # Getting slower
                recommendations.append(
                    f"Performance regression detected in {name} - investigate recent changes"
                )

            if trend_data["time_stability"] > 0.2:  # Unstable performance
                recommendations.append(
                    f"Unstable performance in {name} - check for environmental factors"
                )

        # Check for anomalies
        for name, anomaly_list in anomalies.items():
            if len(anomaly_list) > 3:
                recommendations.append(f"Frequent anomalies in {name} - review test conditions")

        # Check memory usage
        for name, summary_data in summary.items():
            if summary_data["avg_memory_mb"] > 100:  # Arbitrary threshold
                recommendations.append(f"High memory usage in {name} - check for memory leaks")

        if not recommendations:
            recommendations.append("Performance looks healthy - continue monitoring")

        return recommendations

    def export_csv(self, benchmark_name: str, output_path: Path) -> bool:
        """Export benchmark results to CSV."""
        try:
            import csv

            with sqlite3.connect(self.results_db) as conn:
                cursor = conn.execute(
                    """
                    SELECT timestamp, duration, iterations, min_time, max_time,
                           mean_time, median_time, std_dev, memory_usage
                    FROM benchmark_results
                    WHERE name = ?
                    ORDER BY timestamp
                """,
                    (benchmark_name,),
                )

                with open(output_path, "w", newline="") as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(
                        [
                            "Timestamp",
                            "Duration",
                            "Iterations",
                            "Min Time",
                            "Max Time",
                            "Mean Time",
                            "Median Time",
                            "Std Dev",
                            "Memory Usage",
                        ]
                    )

                    for row in cursor:
                        writer.writerow(row)

            return True

        except Exception as e:
            print(f"Error exporting CSV: {e}")
            return False

    def cleanup_old_results(self, days: int = 90) -> int:
        """Clean up results older than specified days."""
        cutoff_date = datetime.now() - timedelta(days=days)

        with sqlite3.connect(self.results_db) as conn:
            cursor = conn.execute(
                """
                DELETE FROM benchmark_results
                WHERE timestamp < ?
            """,
                (cutoff_date.isoformat(),),
            )

            deleted_count = cursor.rowcount
            conn.commit()

        return deleted_count


if __name__ == "__main__":
    # Example usage
    results_db = Path("tests/benchmarks/results/results.db")
    if results_db.exists():
        analyzer = BenchmarkResults(results_db)

        # Generate dashboard
        dashboard = analyzer.generate_performance_dashboard()
        print(f"Performance Health: {dashboard['health_score']['rating']}")
        print(f"Overall Score: {dashboard['health_score']['overall_score']:.1f}/100")

        if dashboard["recommendations"]:
            print("\nRecommendations:")
            for rec in dashboard["recommendations"]:
                print(f"- {rec}")
    else:
        print("No benchmark results database found")
