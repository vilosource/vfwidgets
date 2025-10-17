"""Example 01: Basic Browser Usage

This example demonstrates the simplest way to start ViloWeb.

Educational Focus:
    - Application entry point
    - Default configuration
    - Basic browser window

Run:
    python examples/01_basic_browser.py
"""

import sys
from pathlib import Path

# Add parent directory to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from viloweb import main

if __name__ == "__main__":
    print("=" * 60)
    print("ViloWeb Example 01: Basic Browser")
    print("=" * 60)
    print()
    print("Starting ViloWeb with default configuration...")
    print()
    print("Features demonstrated:")
    print("  - Multi-tab browsing")
    print("  - Navigation (back/forward/reload)")
    print("  - Bookmarks")
    print("  - Theme integration (if vfwidgets-theme installed)")
    print()
    print("Try:")
    print("  - Press Ctrl+T for new tab")
    print("  - Press Ctrl+D to bookmark current page")
    print("  - Press Ctrl+B to view bookmarks")
    print()
    print("=" * 60)

    sys.exit(main())
