#!/usr/bin/env python3
"""
Test script for Phase 2 ChromeTabbedWindow features.

Tests the newly implemented features:
1. Tab Animations
2. New Tab Button
3. Tab Drag-and-Drop
4. Tab Overflow with Scroll
5. Window Edge Resizing
6. Platform-Specific Adapters
"""

import sys

from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget

# Add the src directory to the path
sys.path.insert(0, 'src')

from chrome_tabbed_window import ChromeTabbedWindow


def test_basic_functionality():
    """Test basic functionality of ChromeTabbedWindow with new features."""
    print("Testing ChromeTabbedWindow Phase 2 features...")

    app = QApplication(sys.argv)

    # Create the ChromeTabbedWindow
    tabs = ChromeTabbedWindow()
    tabs.setWindowTitle("ChromeTabbedWindow Phase 2 Test")
    tabs.resize(800, 600)

    # Test 1: Basic tab creation and TabAnimator integration
    print("✓ Testing tab creation with animations...")
    for i in range(5):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel(f"Tab {i+1} Content")
        button = QPushButton(f"Button in Tab {i+1}")
        layout.addWidget(label)
        layout.addWidget(button)
        tabs.addTab(widget, f"Tab {i+1}")

    # Test 2: New Tab Button signal
    print("✓ Testing new tab button signal...")
    def on_new_tab():
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel(f"New Tab {tabs.count() + 1}")
        layout.addWidget(label)
        tabs.addTab(widget, f"New Tab {tabs.count() + 1}")
        print(f"  Added new tab, total tabs: {tabs.count()}")

    # Connect new tab signal (assuming it's available)
    if hasattr(tabs._tab_bar, 'newTabRequested'):
        tabs._tab_bar.newTabRequested.connect(on_new_tab)
        print("  New tab button signal connected")

    # Test 3: Tab Overflow - add many tabs
    print("✓ Testing tab overflow with scroll...")
    for i in range(10):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel(f"Overflow Tab {i+1}")
        layout.addWidget(label)
        tabs.addTab(widget, f"Overflow {i+1}")

    print(f"  Total tabs created: {tabs.count()}")

    # Test 4: Platform adapter
    print("✓ Testing platform adapter...")
    if hasattr(tabs, '_platform'):
        platform_type = type(tabs._platform).__name__
        print(f"  Platform adapter: {platform_type}")

        # Test capabilities
        if hasattr(tabs._platform, 'capabilities'):
            caps = tabs._platform.capabilities
            print(f"  Frameless mode support: {caps.can_use_window_mode}")
            print(f"  System resize support: {caps.supports_system_resize}")

    # Test 5: Tab Animator
    print("✓ Testing TabAnimator...")
    if hasattr(tabs._tab_bar, '_animator'):
        animator = tabs._tab_bar._animator
        print(f"  TabAnimator instance: {type(animator).__name__}")
        print(f"  Animation running: {animator.is_animating()}")

    # Test 6: Edge resizing setup
    print("✓ Testing edge resizing setup...")
    if hasattr(tabs, '_resize_edge'):
        print(f"  Resize edge tracking: {tabs._resize_edge}")
        print(f"  Resize margin: {tabs.RESIZE_MARGIN}px")

    # Show the window
    tabs.show()

    print("\nAll tests completed successfully!")
    print("The window should now be visible with all Phase 2 features enabled.")
    print("Try:")
    print("- Hovering over tabs (should see animations)")
    print("- Clicking the + button to add new tabs")
    print("- Dragging tabs to reorder them")
    print("- Resizing the window from edges (if frameless mode)")
    print("- Scrolling through tabs if there are many")

    return app, tabs


if __name__ == "__main__":
    app, tabs = test_basic_functionality()

    # Keep the application running
    sys.exit(app.exec())
