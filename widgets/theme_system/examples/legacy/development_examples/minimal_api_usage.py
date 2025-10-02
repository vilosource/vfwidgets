#!/usr/bin/env python3
"""
Minimal API Usage - The Simplest Way to Use the Theme System

This example shows the absolute minimum code needed to use the theme system.
Perfect for understanding the basic API without Qt dependencies.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from vfwidgets_theme import ThemedApplication


def main():
    """Minimal demo of theme system API."""
    print("\n" + "="*50)
    print("MINIMAL THEME SYSTEM API USAGE")
    print("="*50)

    # 1. Create ThemedApplication - that's it!
    app = ThemedApplication()
    print("\n✅ Created ThemedApplication")
    print(f"   Available themes: {app.available_themes}")

    # 2. Switch themes - super simple!
    print("\n📝 Switching themes:")
    for theme_name in ['dark', 'light', 'default']:
        app.set_theme(theme_name)
        print(f"   ✅ Set theme to '{theme_name}'")
        print(f"      Current: {theme_name}")
        print(f"      Type: {app.theme_type}")

    # 3. Get performance stats - automatic tracking!
    stats = app.get_performance_statistics()
    print("\n📊 Performance Statistics:")
    print(f"   Theme switches: {stats.get('theme_switch_count', 0)}")
    print(f"   Average time: {stats.get('average_theme_switch_time', 0):.4f}s")

    print("\n" + "="*50)
    print("THAT'S IT! Just 3 lines of code:")
    print("  1. app = ThemedApplication()")
    print("  2. app.set_theme('dark')")
    print("  3. Your widgets automatically update!")
    print("="*50)

    return 0


if __name__ == '__main__':
    sys.exit(main())
