#!/usr/bin/env python3
"""
Phase 0 Test Runner and Validator

Run this script to validate Phase 0 implementation progress.
It checks for file existence, runs tests, and reports status.
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Define expected files
EXPECTED_FILES = {
    "Core Types": [
        "src/vfwidgets_multisplit/__init__.py",
        "src/vfwidgets_multisplit/core/__init__.py",
        "src/vfwidgets_multisplit/core/types.py",
        "src/vfwidgets_multisplit/core/utils.py",
        "src/vfwidgets_multisplit/core/nodes.py",
        "src/vfwidgets_multisplit/core/visitor.py",
        "src/vfwidgets_multisplit/core/tree_utils.py",
        "src/vfwidgets_multisplit/core/signals.py",
        "src/vfwidgets_multisplit/core/signal_bridge.py",
        "src/vfwidgets_multisplit/core/geometry.py",
    ],
    "View Layer": [
        "src/vfwidgets_multisplit/view/__init__.py",
        "src/vfwidgets_multisplit/view/tree_reconciler.py",
    ],
    "Controller Layer": [
        "src/vfwidgets_multisplit/controller/__init__.py",
        "src/vfwidgets_multisplit/controller/transaction.py",
        "src/vfwidgets_multisplit/controller/controller.py",
    ],
    "Tests": [
        "tests/__init__.py",
        "tests/test_id_generation.py",
        "tests/test_tree_utils.py",
        "tests/test_signals.py",
        "tests/test_geometry.py",
        "tests/test_reconciler.py",
        "tests/test_transactions.py",
    ]
}

PHASE0_TESTS = [
    "tests/test_id_generation.py",
    "tests/test_tree_utils.py",
    "tests/test_signals.py",
    "tests/test_geometry.py",
    "tests/test_reconciler.py",
    "tests/test_transactions.py",
]


def check_file_exists(filepath: str) -> Tuple[bool, str]:
    """Check if a file exists relative to project root."""
    full_path = PROJECT_ROOT / filepath
    exists = full_path.exists()
    status = "✅" if exists else "❌"
    return exists, status


def run_test(test_file: str) -> Tuple[bool, str, str]:
    """Run a specific test file and return results."""
    test_path = PROJECT_ROOT / test_file

    if not test_path.exists():
        return False, "NOT FOUND", ""

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_path), "-v", "--tb=short"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=30
        )

        # Parse output for pass/fail
        output = result.stdout + result.stderr

        if result.returncode == 0:
            # Extract test count from output
            if "passed" in output:
                # Find lines like "5 passed in 0.12s"
                for line in output.split('\n'):
                    if 'passed' in line and 'in' in line:
                        return True, "PASSED", line.strip()
            return True, "PASSED", "All tests passed"
        else:
            # Extract failure summary
            if "FAILED" in output:
                for line in output.split('\n'):
                    if 'failed' in line.lower() or 'error' in line.lower():
                        return False, "FAILED", line.strip()
            return False, "FAILED", "Tests failed"

    except subprocess.TimeoutExpired:
        return False, "TIMEOUT", "Test execution timed out"
    except FileNotFoundError:
        return False, "NOT FOUND", "Test file not found"
    except Exception as e:
        return False, "ERROR", str(e)


def check_imports() -> Tuple[bool, List[str]]:
    """Check if core modules can be imported."""
    errors = []
    modules_to_check = [
        "vfwidgets_multisplit.core.types",
        "vfwidgets_multisplit.core.utils",
        "vfwidgets_multisplit.core.nodes",
        "vfwidgets_multisplit.core.visitor",
        "vfwidgets_multisplit.core.tree_utils",
        "vfwidgets_multisplit.core.signals",
        "vfwidgets_multisplit.core.signal_bridge",
        "vfwidgets_multisplit.core.geometry",
        "vfwidgets_multisplit.view.tree_reconciler",
        "vfwidgets_multisplit.controller.transaction",
        "vfwidgets_multisplit.controller.controller",
    ]

    for module in modules_to_check:
        try:
            __import__(module)
        except ImportError as e:
            errors.append(f"{module}: {str(e)}")
        except Exception as e:
            errors.append(f"{module}: Unexpected error - {str(e)}")

    return len(errors) == 0, errors


def main():
    """Run Phase 0 validation."""
    print("=" * 70)
    print("PHASE 0 VALIDATION REPORT")
    print("=" * 70)
    print()

    # Check file existence
    print("📁 FILE EXISTENCE CHECK")
    print("-" * 40)

    all_files_exist = True
    for category, files in EXPECTED_FILES.items():
        print(f"\n{category}:")
        for filepath in files:
            exists, status = check_file_exists(filepath)
            all_files_exist = all_files_exist and exists
            print(f"  {status} {filepath}")

    # Check imports
    print("\n" + "=" * 70)
    print("📦 IMPORT CHECK")
    print("-" * 40)

    imports_ok, import_errors = check_imports()
    if imports_ok:
        print("✅ All core modules can be imported successfully")
    else:
        print("❌ Import errors found:")
        for error in import_errors:
            print(f"  - {error}")

    # Run tests
    print("\n" + "=" * 70)
    print("🧪 TEST EXECUTION")
    print("-" * 40)

    test_results = []
    all_tests_pass = True

    for test_file in PHASE0_TESTS:
        print(f"\nRunning {test_file}...")
        success, status, message = run_test(test_file)
        test_results.append((test_file, success, status, message))
        all_tests_pass = all_tests_pass and success

        status_icon = "✅" if success else "❌"
        print(f"  {status_icon} {status}: {message}")

    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("-" * 40)

    # Count statistics
    existing_files = sum(1 for cat in EXPECTED_FILES.values()
                        for f in cat if check_file_exists(f)[0])
    total_files = sum(len(files) for files in EXPECTED_FILES.values())

    passing_tests = sum(1 for _, success, _, _ in test_results if success)
    total_tests = len(test_results)

    print(f"\nFiles Created: {existing_files}/{total_files}")
    print(f"Tests Passing: {passing_tests}/{total_tests}")
    print(f"Imports Working: {'✅ Yes' if imports_ok else '❌ No'}")

    # Calculate completion percentage
    file_percent = (existing_files / total_files) * 100 if total_files > 0 else 0
    test_percent = (passing_tests / total_tests) * 100 if total_tests > 0 else 0

    print(f"\nFile Completion: {file_percent:.1f}%")
    print(f"Test Completion: {test_percent:.1f}%")

    # Overall status
    print("\n" + "=" * 70)
    if all_files_exist and all_tests_pass and imports_ok:
        print("🎉 PHASE 0 COMPLETE - All foundations are in place!")
        return 0
    else:
        print("🚧 PHASE 0 IN PROGRESS")
        if not all_files_exist:
            print("  - Some files still need to be created")
        if not imports_ok:
            print("  - Import errors need to be resolved")
        if not all_tests_pass:
            print("  - Some tests are failing or missing")
        print("\nNext steps:")
        print("  1. Create any missing files")
        print("  2. Fix import errors")
        print("  3. Implement failing tests")
        print("  4. Run this script again to validate")
        return 1


if __name__ == "__main__":
    sys.exit(main())
