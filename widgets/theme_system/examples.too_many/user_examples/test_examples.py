#!/usr/bin/env python3
"""Test that all examples can be imported and initialized without errors."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def test_example(module_name):
    """Test that an example module can be imported."""
    print(f"\nTesting {module_name}...")
    try:
        # Import the module
        module = __import__(module_name.replace('.py', ''))
        print("  ✓ Module imported successfully")

        # Check for main function
        if hasattr(module, 'main'):
            print("  ✓ Has main() function")
        else:
            print("  ⚠ No main() function found")

        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    examples = [
        '01_minimal_hello_world.py',
        '02_theme_switching.py',
        '03_custom_themed_widgets.py',
        '04_multi_window_application.py',
        '05_complete_application.py'
    ]

    print("Testing VFWidgets Theme System Examples")
    print("=" * 40)

    results = []
    for example in examples:
        success = test_example(example)
        results.append((example, success))

    print("\n" + "=" * 40)
    print("Summary:")
    for example, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {status}: {example}")

    # Check overall success
    all_passed = all(success for _, success in results)
    if all_passed:
        print("\n✓ All examples imported successfully!")
        return 0
    else:
        print("\n✗ Some examples failed to import.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
