"""Tests for user script injection APIs.

This module tests the CSP-safe script injection features added to support
QWebChannel and browser extensions.
"""

import pytest
from PySide6.QtWebEngineCore import QWebEngineScript

from vfwidgets_webview import BrowserWidget, WebChannelHelper, WebView


@pytest.fixture
def webview(qtbot):
    """Create a WebView for testing."""
    view = WebView()
    qtbot.addWidget(view)
    return view


@pytest.fixture
def browser(qtbot):
    """Create a BrowserWidget for testing."""
    widget = BrowserWidget()
    qtbot.addWidget(widget)
    return widget


# ===== User Script Injection Tests =====


def test_inject_user_script_basic(webview):
    """Test basic user script injection."""
    script_code = "console.log('test script');"

    # Should not crash
    webview.inject_user_script(script_code, name="test-script")


def test_inject_user_script_with_custom_params(webview):
    """Test user script injection with custom parameters."""
    script_code = "window.testValue = 42;"

    webview.inject_user_script(
        script_code,
        name="custom-script",
        injection_point=QWebEngineScript.InjectionPoint.DocumentReady,
        world_id=QWebEngineScript.ScriptWorldId.ApplicationWorld,
        runs_on_subframes=False,
    )

    # Verify script was inserted
    scripts = webview.page().scripts()
    found_scripts = scripts.find("custom-script")
    assert len(found_scripts) > 0


def test_remove_user_script(webview):
    """Test removing a user script."""
    webview.inject_user_script("test", name="removable")

    # Should return True (script exists)
    assert webview.remove_user_script("removable") is True

    # Should return False (already removed)
    assert webview.remove_user_script("removable") is False


def test_clear_user_scripts(webview):
    """Test clearing all user scripts."""
    webview.inject_user_script("script1", name="s1")
    webview.inject_user_script("script2", name="s2")
    webview.inject_user_script("script3", name="s3")

    # Clear all
    webview.clear_user_scripts()

    # All should be gone
    scripts = webview.page().scripts()
    assert len(scripts.find("s1")) == 0
    assert len(scripts.find("s2")) == 0
    assert len(scripts.find("s3")) == 0


def test_multiple_scripts_coexist(webview):
    """Test that multiple scripts can coexist."""
    webview.inject_user_script("console.log('script1');", name="script1")
    webview.inject_user_script("console.log('script2');", name="script2")

    scripts = webview.page().scripts()
    assert len(scripts.find("script1")) > 0
    assert len(scripts.find("script2")) > 0


# ===== BrowserWidget Delegation Tests =====


def test_browser_inject_user_script(browser):
    """Test that BrowserWidget delegates to WebView."""
    browser.inject_user_script("test", name="browser-script")

    # Should be in webview's scripts
    scripts = browser.webview.page().scripts()
    assert len(scripts.find("browser-script")) > 0


def test_browser_remove_user_script(browser):
    """Test BrowserWidget script removal."""
    browser.inject_user_script("test", name="browser-script")

    assert browser.remove_user_script("browser-script") is True
    assert browser.remove_user_script("browser-script") is False


def test_browser_clear_user_scripts(browser):
    """Test BrowserWidget clears scripts."""
    browser.inject_user_script("s1", name="s1")
    browser.inject_user_script("s2", name="s2")

    browser.clear_user_scripts()

    scripts = browser.webview.page().scripts()
    assert len(scripts.find("s1")) == 0
    assert len(scripts.find("s2")) == 0


# ===== WebChannelHelper Tests =====


def test_webchannel_helper_load_qt_resource():
    """Test loading Qt resource."""
    # This resource should exist in Qt
    content = WebChannelHelper.load_qt_resource(":/qtwebchannel/qwebchannel.js")

    # Should load successfully
    assert content is not None
    assert len(content) > 0
    assert "QWebChannel" in content  # Should contain QWebChannel class


def test_webchannel_helper_load_invalid_resource():
    """Test loading non-existent resource."""
    content = WebChannelHelper.load_qt_resource(":/nonexistent/file.js")

    # Should return None
    assert content is None


def test_webchannel_helper_setup_channel(browser, qtbot):
    """Test WebChannelHelper setup."""
    from PySide6.QtCore import QObject, Slot

    class TestBridge(QObject):
        @Slot(str)
        def test_method(self, msg: str):
            pass

    bridge = TestBridge()

    # Should not crash
    channel = WebChannelHelper.setup_channel(browser, bridge, "testBridge")

    # Channel should be set
    assert channel is not None
    assert browser.page().webChannel() == channel


def test_webchannel_helper_scripts_injected(browser, qtbot):
    """Test that WebChannelHelper injects scripts."""
    from PySide6.QtCore import QObject, Slot

    class TestBridge(QObject):
        @Slot(str)
        def test_method(self, msg: str):
            pass

    bridge = TestBridge()

    WebChannelHelper.setup_channel(browser, bridge, "testBridge")

    # Should have injected qwebchannel library
    scripts = browser.webview.page().scripts()
    assert len(scripts.find("qwebchannel-library")) > 0

    # Should have injected init script
    assert len(scripts.find("qwebchannel-init-testBridge")) > 0


# ===== Integration Tests =====


def test_user_script_persists_across_navigation(browser, qtbot):
    """Test that user scripts persist across page navigations."""
    # Inject script
    browser.inject_user_script("window.injectedValue = 'persistent';", name="persistent-script")

    # Navigate to example.com
    browser.navigate("https://example.com")

    # Wait for load
    qtbot.wait(100)

    # Script should still be there (it runs on every page load)
    scripts = browser.webview.page().scripts()
    assert len(scripts.find("persistent-script")) > 0


def test_api_completeness_webview(webview):
    """Test that all user script APIs exist on WebView."""
    assert hasattr(webview, "inject_user_script")
    assert hasattr(webview, "remove_user_script")
    assert hasattr(webview, "clear_user_scripts")
    assert callable(webview.inject_user_script)
    assert callable(webview.remove_user_script)
    assert callable(webview.clear_user_scripts)


def test_api_completeness_browser(browser):
    """Test that all user script APIs exist on BrowserWidget."""
    assert hasattr(browser, "inject_user_script")
    assert hasattr(browser, "remove_user_script")
    assert hasattr(browser, "clear_user_scripts")
    assert callable(browser.inject_user_script)
    assert callable(browser.remove_user_script)
    assert callable(browser.clear_user_scripts)
