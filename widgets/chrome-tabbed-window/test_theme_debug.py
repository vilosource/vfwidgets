#!/usr/bin/env python3
"""Debug script to test theme color retrieval."""

import sys
from pathlib import Path

# Add both chrome-tabbed-window and theme_system to path
base_dir = Path(__file__).parent
sys.path.insert(0, str(base_dir / "src"))

theme_system_path = base_dir.parent / "theme_system" / "src"
if theme_system_path.exists():
    sys.path.insert(0, str(theme_system_path))

from vfwidgets_theme import ThemedApplication
from chrome_tabbed_window import ChromeTabbedWindow

# Create themed application
app = ThemedApplication(sys.argv)
app.set_theme("dark")

# Create window
window = ChromeTabbedWindow()

# Get theme from window
theme = window.get_current_theme()
print(f"\n=== Theme Debug Info ===")
print(f"Theme object: {theme}")
print(f"Theme type: {type(theme)}")

if theme:
    print(f"Has colors attr: {hasattr(theme, 'colors')}")
    if hasattr(theme, 'colors'):
        print(f"\nTheme colors type: {type(theme.colors)}")
        print(f"\nAvailable theme colors:")
        for key in sorted(theme.colors.keys()):
            if 'tab' in key.lower() or 'editor' in key.lower():
                print(f"  {key}: {theme.colors[key]}")

    if hasattr(theme, 'name'):
        print(f"\nTheme name: {theme.name}")

# Now check what the renderer gets
from chrome_tabbed_window.components.chrome_tab_renderer import ChromeTabRenderer
colors = ChromeTabRenderer.get_tab_colors(theme)

print(f"\n=== Renderer Colors ===")
for key, color in colors.items():
    print(f"  {key}: {color.name()}")

print("\nDone!")
sys.exit(0)
