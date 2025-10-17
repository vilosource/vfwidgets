"""Basic tests for WebView and WebPage.

These tests verify that our wrapper works correctly.
"""

import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

# Test imports
try:
    from vfwidgets_webview.webpage import WebPage
    from vfwidgets_webview.webview import WebView

    print("✅ Imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)


def test_webpage_creation():
    """Test that we can create a WebPage."""
    print("\nTest: WebPage creation")
    page = WebPage()
    assert page is not None
    print("✅ WebPage created successfully")


def test_webview_creation():
    """Test that we can create a WebView."""
    print("\nTest: WebView creation")
    webview = WebView()
    assert webview is not None
    print("✅ WebView created successfully")


def test_webview_load():
    """Test that WebView can load a URL."""
    print("\nTest: WebView load URL")

    app = QApplication.instance() or QApplication(sys.argv)

    webview = WebView()

    # Track if load started
    load_started = []
    webview.load_started.connect(lambda: load_started.append(True))

    # Load a simple URL
    webview.load("https://example.com")

    # Process events briefly
    QTimer.singleShot(100, app.quit)
    app.exec()

    assert len(load_started) > 0, "Load should have started"
    print("✅ WebView loaded URL successfully")


def test_webview_api():
    """Test WebView API methods."""
    print("\nTest: WebView API")

    webview = WebView()

    # Test URL methods (URL won't be set until navigation starts)
    # Initially empty
    assert webview.url() == ""

    # Test navigation state
    assert not webview.can_go_back()  # No history yet
    assert not webview.can_go_forward()

    # Test zoom
    webview.set_zoom_factor(1.5)
    assert webview.zoom_factor() == 1.5

    print("✅ WebView API works correctly")


if __name__ == "__main__":
    print("Running vfwidgets-webview basic tests...\n")
    print("=" * 60)

    # Create QApplication for tests
    app = QApplication.instance() or QApplication(sys.argv)

    try:
        test_webpage_creation()
        test_webview_creation()
        test_webview_load()
        test_webview_api()

        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
