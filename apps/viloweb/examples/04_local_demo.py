"""Example 04: Local HTML Demo (Works Without External URLs)

This example demonstrates ViloWeb using only local HTML content,
bypassing the Qt WebEngine zygote/sandboxing issues that affect
some Linux configurations.

Educational Focus:
    - Using setHtml() instead of navigate()
    - QWebChannel bridge with local content
    - All browser features work (tabs, bookmarks concept, UI)
    - Perfect for learning browser architecture without network issues

Run:
    python examples/04_local_demo.py
"""

import sys
from pathlib import Path

# Add parent directory to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtCore import QTimer
from viloweb import ViloWebApplication


def create_demo_html() -> str:
    """Create comprehensive demo HTML page."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>ViloWeb Local Demo</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                min-height: 100vh;
            }
            .container {
                max-width: 1000px;
                margin: 0 auto;
            }
            header {
                text-align: center;
                padding: 40px 0;
            }
            h1 {
                font-size: 3em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            }
            .subtitle {
                font-size: 1.2em;
                opacity: 0.9;
            }
            .card {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 30px;
                margin: 20px 0;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            .card h2 {
                margin-bottom: 15px;
                font-size: 1.8em;
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
                transition: transform 0.2s, box-shadow 0.2s;
                font-weight: 600;
            }
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            }
            button:active {
                transform: translateY(0);
            }
            #console {
                background: rgba(0, 0, 0, 0.3);
                border-radius: 8px;
                padding: 20px;
                margin-top: 20px;
                font-family: 'Courier New', monospace;
                min-height: 200px;
                max-height: 400px;
                overflow-y: auto;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            .log-entry {
                margin: 5px 0;
                padding: 8px;
                border-left: 3px solid #4CAF50;
                padding-left: 12px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 4px;
            }
            .log-info { border-left-color: #2196F3; }
            .log-warning { border-left-color: #FF9800; }
            .log-error { border-left-color: #f44336; }
            .feature-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }
            .feature {
                background: rgba(255, 255, 255, 0.05);
                padding: 20px;
                border-radius: 8px;
                text-align: center;
            }
            .feature-icon {
                font-size: 2em;
                margin-bottom: 10px;
            }
            .info-box {
                background: rgba(76, 175, 80, 0.2);
                border-left: 4px solid #4CAF50;
                padding: 15px;
                margin: 15px 0;
                border-radius: 4px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🌐 ViloWeb</h1>
                <p class="subtitle">Educational Web Browser - Local Demo Mode</p>
            </header>

            <div class="info-box">
                <strong>✨ Demo Mode Active</strong><br>
                This page runs entirely locally, demonstrating all ViloWeb features
                without requiring external network access or dealing with Qt WebEngine
                sandboxing issues.
            </div>

            <div class="card">
                <h2>🎯 ViloWeb Features</h2>
                <div class="feature-grid">
                    <div class="feature">
                        <div class="feature-icon">📑</div>
                        <h3>Multi-Tab Browsing</h3>
                        <p>Open, close, and switch between tabs</p>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">⭐</div>
                        <h3>Bookmarks</h3>
                        <p>Save and manage your favorite pages</p>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">🔗</div>
                        <h3>QWebChannel Bridge</h3>
                        <p>Python ↔ JavaScript communication</p>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">🎨</div>
                        <h3>Theme Integration</h3>
                        <p>Automatic theme detection and application</p>
                    </div>
                </div>
            </div>

            <div class="card">
                <h2>🔗 QWebChannel Bridge Demo</h2>
                <p>Test Python↔JavaScript communication via the bridge:</p>
                <div style="margin: 20px 0;">
                    <button onclick="testConnection()">🔌 Test Connection</button>
                    <button onclick="getBridgeInfo()">ℹ️ Get Bridge Info</button>
                    <button onclick="testBookmark()">⭐ Test Bookmark</button>
                    <button onclick="logMessages()">📝 Log Messages</button>
                    <button onclick="clearConsole()">🗑️ Clear Console</button>
                </div>
                <div id="console"></div>
            </div>

            <div class="card">
                <h2>📚 Try These Actions</h2>
                <ul style="line-height: 1.8; margin-left: 20px;">
                    <li><strong>Ctrl+T</strong> - Open new tab</li>
                    <li><strong>Ctrl+W</strong> - Close current tab</li>
                    <li><strong>Ctrl+D</strong> - Bookmark this page</li>
                    <li><strong>Ctrl+B</strong> - View bookmarks</li>
                    <li><strong>File → New Tab</strong> - Create another tab</li>
                    <li><strong>Bookmarks → Add Bookmark</strong> - Save this page</li>
                </ul>
            </div>

            <div class="card">
                <h2>🎓 Educational Value</h2>
                <p>ViloWeb demonstrates modern browser architecture:</p>
                <ul style="line-height: 1.8; margin: 15px 0 0 20px;">
                    <li><strong>Tab Management</strong> - Each tab is independent</li>
                    <li><strong>Signal Forwarding</strong> - Clean event propagation</li>
                    <li><strong>Bookmark Persistence</strong> - JSON-based storage</li>
                    <li><strong>Bridge Pattern</strong> - Python↔JavaScript communication</li>
                    <li><strong>Theme System</strong> - Optional vfwidgets-theme integration</li>
                </ul>
            </div>
        </div>

        <script>
            // Console logging
            function log(message, type = 'info') {
                const consoleDiv = document.getElementById('console');
                const entry = document.createElement('div');
                entry.className = `log-entry log-${type}`;
                const time = new Date().toLocaleTimeString();
                entry.textContent = `[${time}] ${message}`;
                consoleDiv.appendChild(entry);
                consoleDiv.scrollTop = consoleDiv.scrollHeight;
            }

            function clearConsole() {
                document.getElementById('console').innerHTML = '';
                log('Console cleared', 'info');
            }

            // Wait for QWebChannel bridge
            function waitForBridge(callback) {
                if (typeof window.viloWeb !== 'undefined') {
                    callback();
                } else {
                    setTimeout(() => waitForBridge(callback), 100);
                }
            }

            // Bridge test functions
            function testConnection() {
                waitForBridge(() => {
                    log('✓ Bridge connected: window.viloWeb is available', 'info');
                    const methods = Object.keys(window.viloWeb).filter(k =>
                        typeof window.viloWeb[k] === 'function'
                    );
                    log(`Available methods: ${methods.join(', ')}`, 'info');
                });
            }

            function getBridgeInfo() {
                waitForBridge(() => {
                    const version = window.viloWeb.get_bridge_version();
                    const info = JSON.parse(window.viloWeb.get_browser_info());
                    log(`Bridge version: ${version}`, 'info');
                    log(`Browser: ${info.browser} v${info.version}`, 'info');
                    log(`Engine: ${info.engine}`, 'info');
                });
            }

            function testBookmark() {
                waitForBridge(() => {
                    window.viloWeb.bookmark_current_page();
                    log('✓ Bookmark request sent to Python', 'warning');
                    log('  (Check Python console for confirmation)', 'warning');
                });
            }

            function logMessages() {
                waitForBridge(() => {
                    window.viloWeb.log_from_js('info', 'Test info message from JavaScript');
                    window.viloWeb.log_from_js('warning', 'Test warning from JavaScript');
                    window.viloWeb.log_from_js('error', 'Test error from JavaScript');
                    log('✓ Sent test messages to Python logger', 'info');
                });
            }

            // Auto-init
            window.addEventListener('load', () => {
                log('ViloWeb Local Demo loaded successfully', 'info');
                log('Waiting for QWebChannel bridge...', 'info');

                waitForBridge(() => {
                    log('✓ QWebChannel bridge ready!', 'info');
                    log('Click buttons above to test features', 'info');
                });
            });
        </script>
    </body>
    </html>
    """


def main():
    """Run ViloWeb with local HTML demo."""
    print("=" * 60)
    print("ViloWeb Example 04: Local HTML Demo")
    print("=" * 60)
    print()
    print("This example demonstrates ViloWeb using only local HTML.")
    print("Perfect for systems where Qt WebEngine sandboxing causes issues.")
    print()
    print("Features demonstrated:")
    print("  ✓ All ViloWeb UI features (tabs, menus, toolbar)")
    print("  ✓ QWebChannel bridge (Python↔JavaScript)")
    print("  ✓ Bookmark system (test by pressing Ctrl+D)")
    print("  ✓ Theme integration")
    print()
    print("=" * 60)
    print()

    # Create application
    app = ViloWebApplication()

    # Load demo HTML after window is shown
    def load_demo_html():
        window = app.main_window
        if window and window._tab_widget.count() > 0:
            # Get first tab's browser widget
            first_tab = window._tab_widget.widget(0)
            if first_tab:
                html = create_demo_html()
                first_tab.webview.setHtml(html, baseUrl="http://viloweb.local/demo")
                print("✓ Demo HTML loaded successfully")
                print("  Try the interactive buttons on the page!")

    # Schedule HTML loading after Qt event loop starts
    QTimer.singleShot(500, load_demo_html)

    # Run application
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
