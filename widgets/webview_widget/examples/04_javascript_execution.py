"""04_javascript_execution.py

Demonstrate JavaScript execution and page manipulation.

This example shows:
- How to execute JavaScript in the page
- How to get results from JavaScript
- How to manipulate page content from Python
- Practical use cases for run_javascript()

New in Phase 1:
    - browser.run_javascript(script, callback)
    - browser.page() - for advanced configuration
    - browser.profile() - for browser settings
    - browser.set_user_agent() - convenience method
"""

import sys

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Import our BrowserWidget
from vfwidgets_webview import BrowserWidget


class JavaScriptDemo(QWidget):
    """Demo widget showing JavaScript execution capabilities."""

    def __init__(self):
        super().__init__()

        # Create browser
        self.browser = BrowserWidget()

        # Create control panel
        control_panel = self._create_control_panel()

        # Create output log
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(200)
        self.log.setPlaceholderText("JavaScript execution results will appear here...")

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        layout.addWidget(control_panel)
        layout.addWidget(self.browser)
        layout.addWidget(QLabel("Execution Log:"))
        layout.addWidget(self.log)

        # Set custom user agent (Phase 1 feature)
        self.browser.set_user_agent("vfwidgets-webview-demo/1.0 (JavaScript Example)")

        # Load example page
        self.browser.navigate("https://example.com")
        self.log_message("Loaded example.com - Try the buttons above!")

    def _create_control_panel(self) -> QWidget:
        """Create control buttons for JavaScript demos."""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)

        # Button: Get page title
        btn_title = QPushButton("Get Title")
        btn_title.setToolTip("Get page title using JavaScript")
        btn_title.clicked.connect(self.get_page_title)

        # Button: Get all links
        btn_links = QPushButton("Count Links")
        btn_links.setToolTip("Count links on page")
        btn_links.clicked.connect(self.count_links)

        # Button: Change colors
        btn_colors = QPushButton("Red Headings")
        btn_colors.setToolTip("Make all headings red")
        btn_colors.clicked.connect(self.make_headings_red)

        # Button: Inject banner
        btn_banner = QPushButton("Inject Banner")
        btn_banner.setToolTip("Inject custom banner at top of page")
        btn_banner.clicked.connect(self.inject_banner)

        # Button: Get metadata
        btn_meta = QPushButton("Get Metadata")
        btn_meta.setToolTip("Extract page metadata")
        btn_meta.clicked.connect(self.get_metadata)

        # Custom JavaScript input
        self.custom_js_input = QLineEdit()
        self.custom_js_input.setPlaceholderText("Enter custom JavaScript...")
        btn_execute = QPushButton("Execute")
        btn_execute.clicked.connect(self.execute_custom_js)

        layout.addWidget(btn_title)
        layout.addWidget(btn_links)
        layout.addWidget(btn_colors)
        layout.addWidget(btn_banner)
        layout.addWidget(btn_meta)
        layout.addStretch()
        layout.addWidget(QLabel("Custom:"))
        layout.addWidget(self.custom_js_input)
        layout.addWidget(btn_execute)

        return panel

    def log_message(self, message: str) -> None:
        """Add message to log."""
        self.log.append(f"• {message}")

    @Slot()
    def get_page_title(self):
        """Get page title using JavaScript."""
        self.log_message("Getting page title...")

        # Execute JavaScript and get result via callback
        def handle_title(title):
            self.log_message(f"✓ Page title: {title}")

        self.browser.run_javascript("document.title", handle_title)

    @Slot()
    def count_links(self):
        """Count links on the page."""
        self.log_message("Counting links...")

        # JavaScript to count all <a> elements
        script = "document.querySelectorAll('a').length"

        def handle_count(count):
            self.log_message(f"✓ Found {count} links on the page")

        self.browser.run_javascript(script, handle_count)

    @Slot()
    def make_headings_red(self):
        """Make all headings red using JavaScript."""
        self.log_message("Making all headings red...")

        # JavaScript to change all heading colors
        script = """
        document.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach(heading => {
            heading.style.color = 'red';
        });
        'Headings modified'
        """

        def handle_result(result):
            self.log_message(f"✓ {result}")

        self.browser.run_javascript(script, handle_result)

    @Slot()
    def inject_banner(self):
        """Inject a custom banner at the top of the page."""
        self.log_message("Injecting banner...")

        # JavaScript to create and inject a banner
        script = """
        (function() {
            // Remove existing banner if present
            const existing = document.getElementById('python-banner');
            if (existing) existing.remove();

            // Create banner
            const banner = document.createElement('div');
            banner.id = 'python-banner';
            banner.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px;
                text-align: center;
                font-size: 18px;
                font-family: Arial, sans-serif;
                box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                z-index: 10000;
            `;
            banner.innerHTML = '🐍 This page is controlled by Python! 🎉';

            // Inject at top of body
            document.body.insertBefore(banner, document.body.firstChild);

            // Adjust body padding to account for banner
            document.body.style.paddingTop = '60px';

            return 'Banner injected';
        })();
        """

        def handle_result(result):
            self.log_message(f"✓ {result}")

        self.browser.run_javascript(script, handle_result)

    @Slot()
    def get_metadata(self):
        """Extract page metadata."""
        self.log_message("Extracting metadata...")

        # JavaScript to extract metadata
        script = """
        ({
            title: document.title,
            url: window.location.href,
            links: document.querySelectorAll('a').length,
            paragraphs: document.querySelectorAll('p').length,
            images: document.querySelectorAll('img').length,
            headings: document.querySelectorAll('h1, h2, h3').length,
            description: document.querySelector('meta[name="description"]')?.content || 'N/A'
        })
        """

        def handle_metadata(data):
            self.log_message("✓ Page Metadata:")
            if isinstance(data, dict):
                for key, value in data.items():
                    self.log_message(f"  {key}: {value}")
            else:
                self.log_message(f"  {data}")

        self.browser.run_javascript(script, handle_metadata)

    @Slot()
    def execute_custom_js(self):
        """Execute custom JavaScript from input field."""
        script = self.custom_js_input.text().strip()

        if not script:
            self.log_message("⚠ No JavaScript entered")
            return

        self.log_message(f"Executing: {script[:50]}...")

        def handle_result(result):
            self.log_message(f"✓ Result: {result}")

        try:
            self.browser.run_javascript(script, handle_result)
        except Exception as e:
            self.log_message(f"✗ Error: {e}")


def main():
    """Create and show JavaScript execution demo."""
    # Create Qt application
    app = QApplication(sys.argv)

    # Create main window
    window = QMainWindow()
    window.setWindowTitle("JavaScript Execution Demo - vfwidgets-webview")

    # Create demo widget
    demo = JavaScriptDemo()

    # Set as central widget
    window.setCentralWidget(demo)

    # Show window
    window.resize(1200, 800)
    window.show()

    print("\n=== JavaScript Execution Demo ===")
    print("This example demonstrates the Phase 1 API additions:")
    print("  • browser.run_javascript(script, callback)")
    print("  • browser.page() - access to QWebEnginePage")
    print("  • browser.profile() - access to QWebEngineProfile")
    print("  • browser.set_user_agent(ua) - convenience method")
    print("\nUse the buttons to:")
    print("  • Extract data from the page (title, links, metadata)")
    print("  • Modify page content (colors, inject banners)")
    print("  • Execute custom JavaScript")
    print("\nThis is the foundation for ViloWeb's extension system!")

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
