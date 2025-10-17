"""Tests for Phase 1 API additions.

This module tests the new APIs added in Phase 1:
- run_javascript() - Execute JavaScript in page
- page() - Access to QWebEnginePage
- profile() - Access to QWebEngineProfile
- settings() - Access to QWebEngineSettings
- set_user_agent() - Convenience method for user agent
"""

import pytest
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings

from vfwidgets_webview import BrowserWidget, WebView
from vfwidgets_webview.webpage import WebPage


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


# ===== JavaScript Execution Tests =====


def test_webview_run_javascript_no_callback(webview):
    """Test JavaScript execution without callback."""
    # Should not crash
    webview.run_javascript("console.log('test')")


def test_webview_run_javascript_with_callback(webview, qtbot):
    """Test JavaScript execution with callback."""
    results = []

    def callback(result):
        results.append(result)

    # Execute simple JavaScript that returns a value
    webview.run_javascript("2 + 2", callback)

    # Wait a bit for callback
    qtbot.wait(100)

    # Result should be 4
    assert len(results) == 1
    assert results[0] == 4


def test_browser_run_javascript_delegates_to_webview(browser):
    """Test that BrowserWidget delegates JavaScript to WebView."""
    # Should not crash - verifies delegation works
    browser.run_javascript("console.log('test from browser')")


def test_browser_run_javascript_with_callback(browser, qtbot):
    """Test BrowserWidget JavaScript with callback."""
    results = []

    def callback(result):
        results.append(result)

    browser.run_javascript("10 * 5", callback)

    # Wait for callback
    qtbot.wait(100)

    # Result should be 50
    assert len(results) == 1
    assert results[0] == 50


# ===== Page Access Tests =====


def test_webview_page_access(webview):
    """Test that WebView exposes page."""
    page = webview.page()
    assert isinstance(page, WebPage)


def test_browser_page_access(browser):
    """Test that BrowserWidget exposes page."""
    page = browser.page()
    assert isinstance(page, WebPage)
    assert page == browser.webview.page()


def test_page_access_consistency(browser):
    """Test that page access is consistent."""
    # Should return same object
    page1 = browser.page()
    page2 = browser.page()
    assert page1 is page2


# ===== Profile Access Tests =====


def test_webview_profile_access(webview):
    """Test that WebView exposes profile."""
    profile = webview.profile()
    assert isinstance(profile, QWebEngineProfile)


def test_browser_profile_access(browser):
    """Test that BrowserWidget exposes profile."""
    profile = browser.profile()
    assert isinstance(profile, QWebEngineProfile)


def test_profile_access_consistency(browser):
    """Test that profile access is consistent."""
    # Should return same object
    profile1 = browser.profile()
    profile2 = browser.profile()
    assert profile1 is profile2


# ===== Settings Access Tests =====


def test_browser_settings_access(browser):
    """Test that BrowserWidget exposes settings."""
    settings = browser.settings()
    assert isinstance(settings, QWebEngineSettings)


def test_settings_access_consistency(browser):
    """Test that settings access is consistent."""
    # Should return same object
    settings1 = browser.settings()
    settings2 = browser.settings()
    assert settings1 is settings2


# ===== User Agent Tests =====


def test_browser_set_user_agent(browser):
    """Test setting custom user agent."""
    custom_ua = "TestBrowser/1.0 (Testing)"

    browser.set_user_agent(custom_ua)

    # Verify it was set
    assert browser.profile().httpUserAgent() == custom_ua


def test_user_agent_persists(browser):
    """Test that user agent persists."""
    custom_ua = "ViloWeb/1.0"

    browser.set_user_agent(custom_ua)

    # Should still be set after access
    assert browser.profile().httpUserAgent() == custom_ua


# ===== Integration Tests =====


def test_qwebchannel_can_be_setup(browser):
    """Test that QWebChannel can be setup (for ViloWeb extensions)."""
    from PySide6.QtCore import QObject, Slot
    from PySide6.QtWebChannel import QWebChannel

    # Create a simple bridge object
    class TestBridge(QObject):
        @Slot(str)
        def test_method(self, message):
            pass

    bridge = TestBridge()

    # This should work without errors
    channel = QWebChannel()
    channel.registerObject("testBridge", bridge)
    browser.page().setWebChannel(channel)

    # Verify channel was set
    assert browser.page().webChannel() == channel


def test_settings_can_be_configured(browser):
    """Test that settings can be configured."""
    settings = browser.settings()

    # Should be able to configure settings
    settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)

    # Verify it was set
    assert settings.testAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled)


def test_profile_cache_can_be_configured(browser):
    """Test that profile cache can be configured."""
    profile = browser.profile()

    # Should be able to configure cache
    profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.MemoryHttpCache)

    # Verify it was set
    assert profile.httpCacheType() == QWebEngineProfile.HttpCacheType.MemoryHttpCache


# ===== API Completeness Tests =====


def test_phase1_apis_exist_on_webview(webview):
    """Test that all Phase 1 APIs exist on WebView."""
    assert hasattr(webview, "run_javascript")
    assert hasattr(webview, "page")
    assert hasattr(webview, "profile")
    assert callable(webview.run_javascript)
    assert callable(webview.page)
    assert callable(webview.profile)


def test_phase1_apis_exist_on_browser(browser):
    """Test that all Phase 1 APIs exist on BrowserWidget."""
    assert hasattr(browser, "run_javascript")
    assert hasattr(browser, "page")
    assert hasattr(browser, "profile")
    assert hasattr(browser, "settings")
    assert hasattr(browser, "set_user_agent")
    assert callable(browser.run_javascript)
    assert callable(browser.page)
    assert callable(browser.profile)
    assert callable(browser.settings)
    assert callable(browser.set_user_agent)
