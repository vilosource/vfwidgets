#!/usr/bin/env python3
"""
Simple Visual Test to verify framework works
"""

import sys
import tempfile
from pathlib import Path

from PySide6.QtWidgets import QApplication, QLabel

# Ensure QApplication exists before importing our modules
if not QApplication.instance():
    app = QApplication(sys.argv)

from framework import VisualTestFramework


def test_simple_visual():
    """Simple visual test."""
    print("Testing Visual Framework...")

    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create framework
        framework = VisualTestFramework(
            baseline_dir=temp_path / "baselines",
            output_dir=temp_path / "output",
            tolerance=0.01
        )

        print("Framework initialized")

        # Create a simple widget
        widget = QLabel("Visual Test")
        widget.resize(150, 50)
        widget.setStyleSheet("QLabel { background-color: lightblue; color: black; font-size: 14px; }")

        print("Widget created")

        # Capture and test
        result = framework.run_visual_test(
            "simple_test",
            widget,
            update_baseline=True
        )

        print(f"Test result: {result.result.value}")
        print(f"Difference: {result.difference_percentage:.2%}")
        print(f"Baseline exists: {result.baseline_path.exists() if result.baseline_path else False}")
        print(f"Actual exists: {result.actual_path.exists() if result.actual_path else False}")

        # Test again (should be identical)
        result2 = framework.run_visual_test("simple_test", widget)

        print(f"Second test result: {result2.result.value}")
        print(f"Second difference: {result2.difference_percentage:.2%}")

        # Generate report
        report = framework.generate_test_report()
        print("\nTest Report:")
        print(f"Total tests: {report['total']}")
        print(f"Success rate: {report['success_rate']:.1%}")

        return True


if __name__ == "__main__":
    try:
        success = test_simple_visual()
        if success:
            print("\n✅ Visual framework test PASSED")
        else:
            print("\n❌ Visual framework test FAILED")
    except Exception as e:
        print(f"\n❌ Visual framework test ERROR: {e}")
        import traceback
        traceback.print_exc()
