"""Example 02: Custom Start Page

This example shows how to customize ViloWeb's start page and
demonstrate QWebChannel bridge functionality.

Educational Focus:
    - Custom application initialization
    - Creating tabs programmatically
    - QWebChannel bridge testing
    - JavaScript↔Python communication

Run:
    python examples/02_custom_start_page.py
"""

import sys
from pathlib import Path

# Add parent directory to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtCore import QTimer
from viloweb import ViloWebApplication


def create_demo_html() -> str:
    """Create HTML page demonstrating QWebChannel bridge.

    Educational Note:
        This demonstrates how JavaScript can interact with Python
        via the QWebChannel bridge. The page includes:
        - Buttons to call Python methods
        - Console showing Python responses
        - Examples of bi-directional communication
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ViloWeb QWebChannel Demo</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                max-width: 800px;
                margin: 40px auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 30px;
                backdrop-filter: blur(10px);
            }
            h1 {
                margin-top: 0;
                font-size: 2.5em;
            }
            button {
                background: white;
                color: #667eea;
                border: none;
                padding: 12px 24px;
                margin: 8px;
                border-radius: 6px;
                font-size: 16px;
                cursor: pointer;
                transition: transform 0.2s;
            }
            button:hover {
                transform: scale(1.05);
            }
            #console {
                background: rgba(0, 0, 0, 0.3);
                border-radius: 8px;
                padding: 15px;
                margin-top: 20px;
                font-family: 'Courier New', monospace;
                min-height: 200px;
                max-height: 400px;
                overflow-y: auto;
            }
            .log-entry {
                margin: 5px 0;
                padding: 5px;
                border-left: 3px solid #4CAF50;
                padding-left: 10px;
            }
            .section {
                margin: 30px 0;
            }
            .info-box {
                background: rgba(255, 255, 255, 0.15);
                border-radius: 8px;
                padding: 15px;
                margin: 15px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌐 ViloWeb QWebChannel Demo</h1>

            <div class="info-box">
                <p><strong>What is this?</strong></p>
                <p>This page demonstrates Python↔JavaScript communication via QWebChannel.
                Click the buttons below to call Python methods from JavaScript!</p>
            </div>

            <div class="section">
                <h2>🔗 Bridge Connection</h2>
                <button onclick="testConnection()">Test Bridge Connection</button>
                <button onclick="getBridgeVersion()">Get Bridge Version</button>
                <button onclick="getBrowserInfo()">Get Browser Info</button>
            </div>

            <div class="section">
                <h2>📚 Bookmarks</h2>
                <button onclick="bookmarkPage()">Bookmark This Page</button>
                <button onclick="testBookmarkCommand()">Test Bookmark Command</button>
            </div>

            <div class="section">
                <h2>📝 Logging</h2>
                <button onclick="logInfo()">Log Info Message</button>
                <button onclick="logWarning()">Log Warning Message</button>
                <button onclick="logError()">Log Error Message</button>
            </div>

            <div class="section">
                <h2>🖥️ Console Output</h2>
                <div id="console"></div>
                <button onclick="clearConsole()">Clear Console</button>
            </div>
        </div>

        <script>
            // Console logging
            function log(message, style = '') {
                const consoleDiv = document.getElementById('console');
                const entry = document.createElement('div');
                entry.className = 'log-entry';
                entry.style = style;
                entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
                consoleDiv.appendChild(entry);
                consoleDiv.scrollTop = consoleDiv.scrollHeight;
            }

            function clearConsole() {
                document.getElementById('console').innerHTML = '';
            }

            // Wait for QWebChannel bridge to be ready
            function waitForBridge(callback) {
                if (typeof window.viloWeb !== 'undefined') {
                    callback();
                } else {
                    setTimeout(() => waitForBridge(callback), 100);
                }
            }

            // Bridge tests
            function testConnection() {
                waitForBridge(() => {
                    log('✓ Bridge connected: window.viloWeb is available', 'border-color: #4CAF50');
                    log(`  Bridge has methods: ${Object.keys(window.viloWeb).filter(k => typeof window.viloWeb[k] === 'function').join(', ')}`);
                });
            }

            function getBridgeVersion() {
                waitForBridge(() => {
                    const version = window.viloWeb.get_bridge_version();
                    log(`Bridge version: ${version}`, 'border-color: #2196F3');
                });
            }

            function getBrowserInfo() {
                waitForBridge(() => {
                    const info = JSON.parse(window.viloWeb.get_browser_info());
                    log(`Browser: ${info.browser} v${info.version}`, 'border-color: #2196F3');
                    log(`Engine: ${info.engine}`, 'border-color: #2196F3');
                });
            }

            function bookmarkPage() {
                waitForBridge(() => {
                    window.viloWeb.bookmark_current_page();
                    log('✓ Bookmark requested via Python bridge', 'border-color: #FF9800');
                });
            }

            function testBookmarkCommand() {
                waitForBridge(() => {
                    const canExecute = window.viloWeb.can_execute_command('bookmark');
                    log(`Can execute 'bookmark' command: ${canExecute}`, 'border-color: #9C27B0');
                });
            }

            function logInfo() {
                waitForBridge(() => {
                    window.viloWeb.log_from_js('info', 'This is an info message from JavaScript');
                    log('✓ Sent info log to Python', 'border-color: #4CAF50');
                });
            }

            function logWarning() {
                waitForBridge(() => {
                    window.viloWeb.log_from_js('warning', 'This is a warning from JavaScript');
                    log('✓ Sent warning log to Python', 'border-color: #FF9800');
                });
            }

            function logError() {
                waitForBridge(() => {
                    window.viloWeb.log_from_js('error', 'This is an error from JavaScript');
                    log('✓ Sent error log to Python', 'border-color: #f44336');
                });
            }

            // Auto-test connection on load
            window.addEventListener('load', () => {
                log('Page loaded, waiting for QWebChannel bridge...', 'border-color: #2196F3');
                waitForBridge(() => {
                    log('✓ QWebChannel bridge ready!', 'border-color: #4CAF50');
                });
            });
        </script>
    </body>
    </html>
    """


def main():
    """Run custom start page demo."""
    print("=" * 60)
    print("ViloWeb Example 02: Custom Start Page")
    print("=" * 60)
    print()
    print("This example demonstrates:")
    print("  - Custom HTML start page")
    print("  - QWebChannel bridge (Python↔JavaScript)")
    print("  - Bridge method testing")
    print()
    print("The browser will open with a demo page showing all")
    print("available QWebChannel bridge methods.")
    print()
    print("=" * 60)

    # Create application
    app = ViloWebApplication()

    # After main window is shown, replace first tab with demo page
    def setup_demo_page():
        main_window = app.main_window
        if main_window:
            # Get first tab's widget
            first_tab_widget = main_window._tab_widget.widget(0)
            if first_tab_widget:
                # Load demo HTML
                html_content = create_demo_html()
                first_tab_widget.webview.setHtml(html_content)
                print("Demo page loaded in first tab")

    # Schedule demo page setup after event loop starts
    QTimer.singleShot(500, setup_demo_page)

    # Run application
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
