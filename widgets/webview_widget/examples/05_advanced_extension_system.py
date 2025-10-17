"""05_advanced_extension_system.py

Complete example showing how to build an extension system on top of vfwidgets-webview.

This example demonstrates:
- Using run_javascript() for DOM manipulation
- Setting up QWebChannel for Python↔JavaScript bridge
- Using page() access for advanced configuration
- Using profile() for cache/cookie management
- Using settings() for feature configuration
- Building a real extension (ad blocker + page modifier)

This is a reference implementation for ViloWeb's extension system.

Phase 1 APIs Used:
    ✓ browser.run_javascript(script, callback)
    ✓ browser.page() - QWebEnginePage access
    ✓ browser.profile() - QWebEngineProfile access
    ✓ browser.settings() - QWebEngineSettings access
    ✓ browser.set_user_agent(ua)
"""

import sys
from typing import Optional

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Import our BrowserWidget
from vfwidgets_webview import BrowserWidget

# ===== Extension System: Python↔JavaScript Bridge =====


class ExtensionBridge(QObject):
    """Bridge object for Python↔JavaScript communication via QWebChannel.

    This demonstrates how ViloWeb extensions can communicate between
    Python and JavaScript using QWebChannel.

    Educational Note:
        QWebChannel allows JavaScript in the page to call Python methods
        and vice versa. This is the foundation for extension systems.
    """

    # Signals: Python → JavaScript
    theme_changed = Signal(str)  # Emit when theme changes
    setting_changed = Signal(str, object)  # Emit when setting changes

    # Signals: JavaScript → Python (for logging)
    log_received = Signal(str, str)  # level, message

    def __init__(self):
        super().__init__()
        self.blocked_elements = 0
        self.modified_elements = 0

    @Slot(str, str)
    def log_from_js(self, level: str, message: str):
        """Called by JavaScript to log messages to Python.

        Example JavaScript:
            qwebchannel.objects.extension.log_from_js('info', 'Hello from JS!');
        """
        self.log_received.emit(level, message)

    @Slot(str)
    def element_blocked(self, selector: str):
        """Called by JavaScript when an element is blocked.

        Example JavaScript:
            qwebchannel.objects.extension.element_blocked('.ad');
        """
        self.blocked_elements += 1
        self.log_received.emit("info", f"Blocked element: {selector}")

    @Slot(str)
    def element_modified(self, selector: str):
        """Called by JavaScript when an element is modified.

        Example JavaScript:
            qwebchannel.objects.extension.element_modified('h1');
        """
        self.modified_elements += 1
        self.log_received.emit("info", f"Modified element: {selector}")

    @Slot(str, result=str)
    def get_setting(self, key: str) -> str:
        """Called by JavaScript to get Python settings.

        Example JavaScript:
            const theme = await qwebchannel.objects.extension.get_setting('theme');
        """
        # In real app, would fetch from settings storage
        return "dark"

    @Slot(str, str)
    def notify_event(self, event_type: str, data: str):
        """Generic event notification from JavaScript.

        Example JavaScript:
            qwebchannel.objects.extension.notify_event('page_ready', 'loaded');
        """
        self.log_received.emit("event", f"{event_type}: {data}")


# ===== Extension Manager =====


class ExtensionManager:
    """Manages browser extensions using Phase 1 APIs.

    This shows how to build an extension system on top of vfwidgets-webview.
    """

    def __init__(self, browser: BrowserWidget):
        self.browser = browser
        self.bridge = ExtensionBridge()
        self.channel: Optional[QWebChannel] = None

        # Extension state
        self.ad_blocker_enabled = False
        self.page_modifier_enabled = False

        # Setup QWebChannel bridge
        self._setup_bridge()

    def _setup_bridge(self):
        """Setup QWebChannel for Python↔JavaScript communication.

        Educational Note:
            This uses browser.page() to access QWebEnginePage,
            which is needed to set the web channel.
        """
        # Create channel
        self.channel = QWebChannel()

        # Register our bridge object
        # JavaScript can access as: qwebchannel.objects.extension
        self.channel.registerObject("extension", self.bridge)

        # Set channel on page (Phase 1 API: browser.page())
        self.browser.page().setWebChannel(self.channel)

        # Inject QWebChannel JavaScript library
        self._inject_qwebchannel_lib()

    def _inject_qwebchannel_lib(self):
        """Inject QWebChannel JavaScript library into page.

        Educational Note:
            This is needed once per page load to enable JavaScript
            access to the QWebChannel API.
        """
        # Load qwebchannel.js from Qt resources
        qwebchannel_js = """
        // QWebChannel initialization
        new QWebChannel(qt.webChannelTransport, function(channel) {
            window.extension = channel.objects.extension;
            console.log('Extension bridge ready!');
        });
        """

        # Inject on page load (Phase 1 API: browser.run_javascript())
        self.browser.load_finished.connect(
            lambda success: self.browser.run_javascript(qwebchannel_js) if success else None
        )

    def enable_ad_blocker(self):
        """Enable ad blocker extension.

        Educational Note:
            This uses run_javascript() to inject ad-blocking code
            into the page. Real ad blockers would be more sophisticated.
        """
        self.ad_blocker_enabled = True

        # JavaScript to block common ad elements
        ad_blocker_script = """
        (function() {
            // Common ad selectors
            const adSelectors = [
                '.ad', '.ads', '.advertisement',
                '[class*="ad-"]', '[id*="ad-"]',
                'iframe[src*="ads"]',
                'div[class*="sponsor"]'
            ];

            let blockedCount = 0;

            adSelectors.forEach(selector => {
                document.querySelectorAll(selector).forEach(el => {
                    el.remove();
                    blockedCount++;

                    // Notify Python via QWebChannel
                    if (window.extension) {
                        window.extension.element_blocked(selector);
                    }
                });
            });

            // Log to Python
            if (window.extension) {
                window.extension.log_from_js('info',
                    `Ad blocker: Blocked ${blockedCount} elements`);
            }

            return blockedCount;
        })();
        """

        # Execute on current page
        def log_result(count):
            print(f"Ad blocker: Blocked {count} elements")

        self.browser.run_javascript(ad_blocker_script, log_result)

    def disable_ad_blocker(self):
        """Disable ad blocker."""
        self.ad_blocker_enabled = False

    def enable_page_modifier(self):
        """Enable page modifier extension.

        Educational Note:
            This shows how to use run_javascript() to modify page
            appearance and behavior.
        """
        self.page_modifier_enabled = True

        # JavaScript to modify page styling
        page_modifier_script = """
        (function() {
            // Add custom styles
            const style = document.createElement('style');
            style.id = 'extension-styles';
            style.textContent = `
                /* Extension styles */
                body {
                    filter: brightness(0.95) contrast(1.05);
                }

                a {
                    color: #0066cc !important;
                    text-decoration: underline !important;
                }

                img {
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }
            `;

            // Remove existing if present
            const existing = document.getElementById('extension-styles');
            if (existing) existing.remove();

            document.head.appendChild(style);

            // Count modified elements
            const imageCount = document.querySelectorAll('img').length;
            const linkCount = document.querySelectorAll('a').length;

            // Notify Python
            if (window.extension) {
                window.extension.log_from_js('info',
                    `Page modifier: Styled ${imageCount} images, ${linkCount} links`);
            }

            return {images: imageCount, links: linkCount};
        })();
        """

        def log_result(result):
            if isinstance(result, dict):
                print(
                    f"Page modifier: Styled {result.get('images', 0)} images, "
                    f"{result.get('links', 0)} links"
                )

        self.browser.run_javascript(page_modifier_script, log_result)

    def disable_page_modifier(self):
        """Disable page modifier."""
        self.page_modifier_enabled = False

        # Remove custom styles
        remove_styles_script = """
        const style = document.getElementById('extension-styles');
        if (style) style.remove();
        """
        self.browser.run_javascript(remove_styles_script)


# ===== Main Demo Application =====


class ExtensionDemo(QWidget):
    """Demo application showing extension system built on Phase 1 APIs."""

    def __init__(self):
        super().__init__()

        # Create browser
        self.browser = BrowserWidget()

        # Configure browser using Phase 1 APIs
        self._configure_browser()

        # Create extension manager
        self.extension_manager = ExtensionManager(self.browser)

        # Create UI
        control_panel = self._create_control_panel()
        log_panel = self._create_log_panel()

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        layout.addWidget(control_panel)
        layout.addWidget(self.browser)
        layout.addWidget(log_panel)

        # Connect bridge logging
        self.extension_manager.bridge.log_received.connect(self.log_message)

        # Load example page
        self.browser.navigate("https://example.com")
        self.log_message("info", "Loaded example.com")

    def _configure_browser(self):
        """Configure browser using Phase 1 APIs.

        Educational Note:
            This demonstrates how to use profile(), settings(),
            and set_user_agent() for browser configuration.
        """
        # Set custom user agent (Phase 1 API)
        self.browser.set_user_agent("vfwidgets-webview-demo/1.0 (Extension System Example)")

        # Configure profile (Phase 1 API: browser.profile())
        profile = self.browser.profile()

        # Use memory cache (faster for demo)
        from PySide6.QtWebEngineCore import QWebEngineProfile

        profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.MemoryHttpCache)

        # Configure settings (Phase 1 API: browser.settings())
        settings = self.browser.settings()

        # Enable JavaScript (required for extensions)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)

        # Enable local storage (extensions might use it)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)

        print("✓ Browser configured:")
        print(f"  User agent: {profile.httpUserAgent()}")
        js_enabled = settings.testAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled)
        print(f"  JavaScript: {js_enabled}")
        print("  Cache: Memory")

    def _create_control_panel(self) -> QWidget:
        """Create control panel with extension toggles."""
        panel = QWidget()
        panel.setMaximumHeight(150)
        layout = QVBoxLayout(panel)

        # Title
        title = QLabel("<b>Extension System Demo</b>")
        layout.addWidget(title)

        # Extension controls
        extensions_group = QGroupBox("Extensions")
        ext_layout = QHBoxLayout(extensions_group)

        # Ad blocker toggle
        self.ad_blocker_checkbox = QCheckBox("Ad Blocker")
        self.ad_blocker_checkbox.stateChanged.connect(self.toggle_ad_blocker)

        # Page modifier toggle
        self.page_modifier_checkbox = QCheckBox("Page Modifier")
        self.page_modifier_checkbox.stateChanged.connect(self.toggle_page_modifier)

        ext_layout.addWidget(self.ad_blocker_checkbox)
        ext_layout.addWidget(self.page_modifier_checkbox)
        ext_layout.addStretch()

        layout.addWidget(extensions_group)

        # Actions
        actions_group = QGroupBox("Actions")
        actions_layout = QHBoxLayout(actions_group)

        # Reload page
        btn_reload = QPushButton("Reload Page")
        btn_reload.clicked.connect(self.reload_page)

        # Extract metadata
        btn_metadata = QPushButton("Extract Metadata")
        btn_metadata.clicked.connect(self.extract_metadata)

        # Test bridge
        btn_test_bridge = QPushButton("Test Bridge")
        btn_test_bridge.clicked.connect(self.test_bridge)

        actions_layout.addWidget(btn_reload)
        actions_layout.addWidget(btn_metadata)
        actions_layout.addWidget(btn_test_bridge)
        actions_layout.addStretch()

        layout.addWidget(actions_group)

        return panel

    def _create_log_panel(self) -> QWidget:
        """Create log panel."""
        panel = QWidget()
        panel.setMaximumHeight(150)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)

        layout.addWidget(QLabel("<b>Extension Log:</b>"))

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

        return panel

    def log_message(self, level: str, message: str):
        """Add message to log."""
        icon = {"info": "ℹ️", "event": "📢", "error": "❌", "success": "✅"}.get(level, "•")

        self.log.append(f"{icon} {message}")

    @Slot(int)
    def toggle_ad_blocker(self, state: int):
        """Toggle ad blocker extension."""
        if state:
            self.extension_manager.enable_ad_blocker()
            self.log_message("info", "Ad blocker enabled")
        else:
            self.extension_manager.disable_ad_blocker()
            self.log_message("info", "Ad blocker disabled")

    @Slot(int)
    def toggle_page_modifier(self, state: int):
        """Toggle page modifier extension."""
        if state:
            self.extension_manager.enable_page_modifier()
            self.log_message("info", "Page modifier enabled")
        else:
            self.extension_manager.disable_page_modifier()
            self.log_message("info", "Page modifier disabled")

    @Slot()
    def reload_page(self):
        """Reload page and re-apply extensions."""
        self.browser.reload()
        self.log_message("info", "Reloading page...")

    @Slot()
    def extract_metadata(self):
        """Extract page metadata using JavaScript."""
        self.log_message("info", "Extracting metadata...")

        # JavaScript to extract metadata
        script = """
        ({
            title: document.title,
            url: window.location.href,
            links: document.querySelectorAll('a').length,
            images: document.querySelectorAll('img').length,
            paragraphs: document.querySelectorAll('p').length,
            headings: document.querySelectorAll('h1, h2, h3').length,
        })
        """

        def handle_metadata(data):
            if isinstance(data, dict):
                self.log_message("success", "Metadata extracted:")
                for key, value in data.items():
                    self.log_message("info", f"  {key}: {value}")

        self.browser.run_javascript(script, handle_metadata)

    @Slot()
    def test_bridge(self):
        """Test QWebChannel bridge communication."""
        self.log_message("info", "Testing bridge...")

        # JavaScript to test bridge
        script = """
        (async function() {
            if (!window.extension) {
                return 'Bridge not ready';
            }

            // Test calling Python methods from JavaScript
            window.extension.log_from_js('event', 'Bridge test successful!');

            // Test getting settings
            const setting = await window.extension.get_setting('theme');
            window.extension.log_from_js('info', 'Got setting: ' + setting);

            return 'Bridge test complete';
        })();
        """

        def handle_result(result):
            self.log_message("success", f"{result}")

        self.browser.run_javascript(script, handle_result)


def main():
    """Create and show extension system demo."""
    # Create Qt application
    app = QApplication(sys.argv)

    # Create main window
    window = QMainWindow()
    window.setWindowTitle("Extension System Demo - vfwidgets-webview Phase 1")

    # Create demo widget
    demo = ExtensionDemo()

    # Set as central widget
    window.setCentralWidget(demo)

    # Show window
    window.resize(1400, 900)
    window.show()

    print("\n" + "=" * 70)
    print("Extension System Demo - Reference Implementation")
    print("=" * 70)
    print("\nThis example demonstrates:")
    print("  ✓ QWebChannel setup using browser.page()")
    print("  ✓ Python↔JavaScript bridge communication")
    print("  ✓ JavaScript execution using browser.run_javascript()")
    print("  ✓ Browser configuration using browser.profile() and browser.settings()")
    print("  ✓ Extension system architecture")
    print("\nPhase 1 APIs Used:")
    print("  • browser.run_javascript(script, callback)")
    print("  • browser.page() - Access to QWebEnginePage")
    print("  • browser.profile() - Access to QWebEngineProfile")
    print("  • browser.settings() - Access to QWebEngineSettings")
    print("  • browser.set_user_agent(ua)")
    print("\nTry:")
    print("  1. Enable Ad Blocker - removes ad elements from page")
    print("  2. Enable Page Modifier - applies custom styling")
    print("  3. Extract Metadata - gets page information via JavaScript")
    print("  4. Test Bridge - verifies Python↔JavaScript communication")
    print("\nThis is the foundation for ViloWeb's extension system!")
    print("=" * 70 + "\n")

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
