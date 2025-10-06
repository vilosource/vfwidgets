#!/usr/bin/env python3
"""Test that all examples can actually RUN without crashing.
This tests beyond just import - it actually runs each example.
"""

import subprocess
import sys


def test_example_runs(script_path):
    """Test that an example can actually run without crashing."""
    print(f"\nTesting {script_path}...")

    # Run with timeout and capture output
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=2,  # 2 second timeout for GUI apps
            check=False,  # Don't raise on non-zero exit
        )

        # Check exit code
        if (
            result.returncode == 0 or result.returncode == -15
        ):  # -15 is SIGTERM from timeout, which is OK for GUI apps
            print(f"  ✓ Ran successfully (exit code: {result.returncode})")
            return True
        else:
            print(f"  ✗ CRASHED with exit code: {result.returncode}")

            # Show error output
            if "Traceback" in result.stderr or "Error" in result.stderr:
                print("  Error output:")
                for line in result.stderr.split("\n"):
                    if line and not line.startswith("22:"):  # Skip debug lines
                        print(f"    {line}")

            return False

    except subprocess.TimeoutExpired:
        # Timeout is expected for GUI apps that run successfully
        print("  ✓ Running (timed out as expected for GUI)")
        return True
    except Exception as e:
        print(f"  ✗ Failed to run: {e}")
        return False


def main():
    examples = [
        "01_minimal_hello_world.py",
        "02_theme_switching.py",
        "03_custom_themed_widgets.py",
        "04_multi_window_application.py",
        "05_complete_application.py",
        "06_new_api_simple.py",
        "07_tabbed_text_editor.py",
        "08_vscode_theme_showcase.py",
    ]

    print("Testing VFWidgets Theme System Examples - ACTUAL RUNTIME")
    print("=" * 60)

    results = []
    for example in examples:
        success = test_example_runs(example)
        results.append((example, success))

    print("\n" + "=" * 60)
    print("Runtime Test Summary:")

    passed = 0
    failed = 0
    for example, success in results:
        if success:
            print(f"  ✓ PASS: {example}")
            passed += 1
        else:
            print(f"  ✗ FAIL: {example} - CRASHED AT RUNTIME")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")

    if failed > 0:
        print("\n✗ CRITICAL: Some examples are crashing at runtime!")
        print("The theme system has runtime errors that need to be fixed.")
        return 1
    else:
        print("\n✓ All examples run successfully!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
