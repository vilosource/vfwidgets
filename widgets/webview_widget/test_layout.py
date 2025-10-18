#!/usr/bin/env python3
"""Quick visual test to verify NavigationBar and WebView sizing.

This script creates a BrowserWidget and prints the actual sizes of components
to verify the layout is correct.
"""

import sys

from PySide6.QtWidgets import QApplication

from vfwidgets_webview import BrowserWidget


def main():
    app = QApplication(sys.argv)

    # Create browser
    browser = BrowserWidget()
    browser.resize(1200, 800)
    browser.show()

    # Force layout calculation
    app.processEvents()

    # Print sizes
    print("\n=== Component Sizes ===")
    print(f"BrowserWidget:  {browser.width()} x {browser.height()}")
    print(f"NavigationBar:  {browser.navbar.width()} x {browser.navbar.height()}")
    print(f"WebView:        {browser.webview.width()} x {browser.webview.height()}")

    print("\n=== Size Policies ===")
    print(f"NavigationBar horizontal: {browser.navbar.sizePolicy().horizontalPolicy()}")
    print(f"NavigationBar vertical:   {browser.navbar.sizePolicy().verticalPolicy()}")
    print(f"WebView horizontal:       {browser.webview.sizePolicy().horizontalPolicy()}")
    print(f"WebView vertical:         {browser.webview.sizePolicy().verticalPolicy()}")

    print("\n=== Layout Info ===")
    layout = browser.layout()
    print(f"Layout margins: {layout.contentsMargins()}")
    print(f"Layout spacing: {layout.spacing()}")

    print("\n=== Expected Behavior ===")
    print("✓ NavigationBar should be ~40-45px tall (buttons + margins)")
    print("✓ WebView should take remaining vertical space")
    print("✓ NavigationBar height should be << WebView height")

    navbar_height = browser.navbar.height()
    webview_height = browser.webview.height()
    total_height = browser.height()

    print("\n=== Actual Results ===")
    print(f"NavigationBar: {navbar_height}px ({navbar_height/total_height*100:.1f}%)")
    print(f"WebView:       {webview_height}px ({webview_height/total_height*100:.1f}%)")

    if navbar_height < 60 and webview_height > 700:
        print("\n✓ Layout looks CORRECT!")
    else:
        print("\n✗ Layout looks INCORRECT - NavigationBar too tall or WebView too short")

    print("\nClose the window to exit...")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
