#!/usr/bin/env python3
"""
Test Examples - Improved Testing Protocol
===========================================

Tests all example files with comprehensive error detection.

Key improvements based on lessons learned:
- Checks exit codes
- Checks for "Exception ignored" in stderr (critical!)
- Checks for error patterns even when exit code is OK
- Captures stderr throughout entire runtime (including after timeout)
- Tests widget lifecycle, not just startup
"""

import os
import subprocess
import sys
import tempfile


def test_example_runs(script_path):
    """
    Properly test if an example runs without errors.

    Returns:
        tuple: (success: bool, message: str)
    """
    print(f"\nTesting {script_path}...")

    # Create temp file for stderr to capture ALL output
    stderr_fd, stderr_path = tempfile.mkstemp(suffix=".log", prefix="test_")

    # Variable to track if we need to clean up
    cleanup_done = False

    try:
        with open(stderr_path, "w") as stderr_file:
            try:
                result = subprocess.run(
                    [sys.executable, script_path],
                    stdout=subprocess.DEVNULL,  # Discard stdout
                    stderr=stderr_file,  # Write stderr to file
                    timeout=2,
                    check=False,  # Don't raise, we check manually
                )
                # If we get here, no timeout occurred
                timeout_occurred = False
            except subprocess.TimeoutExpired:
                # Timeout is EXPECTED for GUI apps
                timeout_occurred = True
                result = None

        # Read stderr from file (captures ALL output, even during/after timeout)
        with open(stderr_path) as f:
            stderr_content = f.read()

        # Clean up temp file
        try:
            os.close(stderr_fd)
            os.unlink(stderr_path)
            cleanup_done = True
        except:
            pass

        # CHECK THE EXIT CODE (only if we have a result - no timeout)
        if not timeout_occurred and result.returncode not in [0, -15, 124]:
            msg = f"✗ CRASHED: exit code {result.returncode}"
            print(f"  {msg}")
            if "Traceback" in stderr_content:
                print("  Traceback found in stderr:")
                for line in stderr_content.split("\n")[:10]:  # First 10 lines
                    if line.strip():
                        print(f"    {line}")
            return False, msg

        # CRITICAL: Check for ignored exceptions (these don't fail exit codes!)
        if "Exception ignored" in stderr_content:
            msg = "✗ IGNORED EXCEPTION DETECTED"
            print(f"  {msg}")
            # Show the exception
            lines = stderr_content.split("\n")
            for i, line in enumerate(lines):
                if "Exception ignored" in line:
                    # Show context (5 lines)
                    start = max(0, i)
                    end = min(len(lines), i + 6)
                    print("  Exception context:")
                    for context_line in lines[start:end]:
                        if context_line.strip():
                            print(f"    {context_line}")
                    break
            return False, msg

        # NEW: Check for error patterns even if exit code OK
        # This is CRITICAL - catches errors logged during runtime that don't crash the app
        error_patterns = [
            ("[ERROR]", "ERROR log message found"),
            ("TypeError:", "TypeError found"),
            ("AttributeError:", "AttributeError found"),
            ("Error calling Python override", "Python override error"),
            ("KeyError:", "KeyError found"),
            ("ValueError:", "ValueError found"),
            ("RuntimeError:", "RuntimeError found"),
        ]

        for pattern, description in error_patterns:
            if pattern in stderr_content:
                msg = f"✗ ERROR PATTERN: {description}"
                print(f"  {msg}")
                # Show first occurrence with context
                lines = stderr_content.split("\n")
                for i, line in enumerate(lines):
                    if pattern in line:
                        start = max(0, i - 2)
                        end = min(len(lines), i + 3)
                        print("  Error context:")
                        for context_line in lines[start:end]:
                            if context_line.strip() and not context_line.startswith("[DEBUG]"):
                                print(f"    {context_line}")
                        break
                return False, msg

        # All checks passed!
        if timeout_occurred:
            print("  ✓ Running (timed out as expected for GUI)")
            return True, "GUI timeout (expected)"
        else:
            print("  ✓ Runs successfully")
            return True, "Success"

    except Exception as e:
        # Clean up if not already done
        if not cleanup_done:
            try:
                os.close(stderr_fd)
                os.unlink(stderr_path)
            except:
                pass

        msg = f"✗ Test error: {e}"
        print(f"  {msg}")
        return False, msg


def main():
    """Run all example tests."""
    examples = [
        "01_hello_world.py",
        "02_buttons_and_layout.py",
        "03_theme_switching.py",
        "04_input_forms.py",
        "05_vscode_editor.py",
        "06_role_markers.py",
    ]

    print("=" * 70)
    print("VFWidgets Theme System - Example Tests")
    print("Improved Protocol: Exit codes + stderr analysis")
    print("=" * 70)

    results = []
    for example in examples:
        success, message = test_example_runs(example)
        results.append((example, success, message))

    # Summary
    print("\n" + "=" * 70)
    print("Test Summary:")
    print("=" * 70)

    passed = 0
    failed = 0

    for example, success, message in results:
        if success:
            print(f"  ✓ PASS: {example}")
            passed += 1
        else:
            print(f"  ✗ FAIL: {example} - {message}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")

    if failed > 0:
        print("\n✗ CRITICAL: Some examples have errors!")
        print("Review the output above for details.")
        return 1
    else:
        print("\n✓ All examples run successfully!")
        print("No crashes, no ignored exceptions, no runtime errors.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
