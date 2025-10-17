# WebView-Based Widget Architecture Patterns - Research Findings

**Date**: 2025-10-16
**Purpose**: Research established patterns for webview-based widgets to inform markdown widget refactoring
**Status**: Complete

## Executive Summary

This research examines webview architecture patterns from VS Code, Jupyter QtConsole, Electron, and Qt/PySide6 best practices to inform the refactoring of VFWidgets' markdown widget. Key findings include:

1. **CSS Theme Injection**: Use JavaScript to create/modify `<style>` elements with CSS variables, injected via `QWebEngineScript` or `runJavaScript()`
2. **Testing Strategy**: Separate HTML/JS unit tests (Jest/Playwright) from Qt integration tests (pytest-qt)
3. **Communication Protocol**: QWebChannel for bidirectional messaging with strong typing via `@Slot` decorators
4. **Playwright Limitations**: Cannot directly test QWebEngineView; requires separate HTML testing approach

---

## 1. CSS Theme Injection Patterns

### 1.1 VS Code Webview API Pattern

**Source**: [VS Code Webview API Documentation](https://code.visualstudio.com/api/extension-guides/webview)

VS Code uses a well-established pattern for injecting themes into webviews:

#### Theme Variables
- VS Code groups themes into three categories: `vscode-light`, `vscode-dark`, `vscode-high-contrast`
- Adds special class to body element based on theme category
- Theme color variables are prefixed with `vscode` and dots are replaced with dashes
- **Example**: `editor.foreground` becomes `var(--vscode-editor-foreground)`

```css
/* VS Code pattern - theme variables in CSS */
body {
  color: var(--vscode-editor-foreground);
  background-color: var(--vscode-editor-background);
}
```

#### Resource Loading
- Uses `asWebviewUri()` to convert local file paths to webview-accessible URIs
- **Content Security Policy (CSP)** is required for all webviews
- CSP implicitly disables inline scripts and styles - must extract to external files

```html
<meta http-equiv="Content-Security-Policy"
      content="default-src 'none';
               img-src ${webview.cspSource} https:;
               script-src 'nonce-${nonce}';
               style-src ${webview.cspSource};">
```

#### Message Passing
- Extension → Webview: `webview.postMessage()`
- Webview → Extension: `acquireVsCodeApi()` function
- Messages only delivered if webview is live (visible or `retainContextWhenHidden`)

**Key Quote**: "Theme color variables are prefixed with vscode and dots are replaced with dashes, for example editor.foreground becomes var(--vscode-editor-foreground)."

**Recommendation**: This is the gold standard. Adopt CSS custom properties (variables) pattern for markdown widget theme injection.

---

### 1.2 Jupyter QtConsole Approach

**Source**: [Jupyter QtConsole GitHub](https://github.com/jupyter/qtconsole)

Jupyter QtConsole originally removed HTML support but has been discussing restoration:

#### Theme Implementation
- Syntax highlighting handled by **Pygments library**
- Theme exposed via `style` argument - any Pygments style can be used
- Custom themes via CSS files: `c.JupyterQtConsoleApp.stylesheet` points to custom CSS
- Color scheme: `c.JupygerWidget.syntax_style` sets the color scheme

#### HTML Rendering Patterns Discussed
1. **QDialog with QWebView**: Open HTML in separate dialog
2. **QStackedLayout**: Mix rich text and webengine widgets - switch between them based on content type
3. **Signal-based**: Emit HTML content in Qt signal, captured by embedding apps

**Key Quote**: "The Qt widget has full syntax highlighting handled by the pygments library, and the style argument exposes access to any style by name that can be found by pygments."

**Recommendation**: The Pygments pattern shows that server-side theme rendering is viable. Consider adding a Python-based renderer option alongside the current JavaScript renderer.

---

### 1.3 Qt WebEngine CSS Injection Pattern

**Source**: [Qt WebEngine StyleSheet Browser Example](https://doc.qt.io/qt-5/qtwebengine-webenginewidgets-stylesheetbrowser-example.html)

Qt's official example demonstrates CSS injection using `QWebEngineScript`:

#### Implementation Pattern
```python
# Create script that injects CSS
script = QWebEngineScript()
script.setName("stylesheet-injector")
script.setInjectionPoint(QWebEngineScript.DocumentReady)
script.setRunsOnSubFrames(True)
script.setWorldId(QWebEngineScript.ApplicationWorld)

# JavaScript to create and append CSS element
script.setSourceCode("""
    (function() {
        var style = document.createElement('style');
        style.type = 'text/css';
        style.id = 'injected-stylesheet';
        style.innerText = '..css content..';
        document.head.appendChild(style);
    })();
""")

page.scripts().insert(script)
```

#### Key Configuration
- **Injection Point**: `DocumentReady` ensures DOM is available
- **SubFrames**: `setRunsOnSubFrames(true)` applies to iframes
- **World ID**: `ApplicationWorld` isolates from page scripts

#### Alternative: runJavaScript()
- `QWebEnginePage.runJavaScript()` - immediate execution
- `QWebEngineScript` - persistent, runs automatically on page load

**Key Quote**: "The technique uses JavaScript to create and append CSS elements to the documents."

**Recommendation**: Current markdown widget uses `runJavaScript()` which is appropriate for dynamic theme changes. For persistent base styles, consider `QWebEngineScript`.

---

## 2. Architecture Patterns for Webview Widgets

### 2.1 Electron IPC Architecture

**Source**: [Electron IPC Documentation](https://www.electronjs.org/docs/latest/tutorial/ipc)

Electron's architecture provides insights into process separation:

#### Process Architecture
- **Main Process**: Node.js backend
- **Renderer Process**: Web content (one per window)
- **Webview**: Embedded browser within renderer (deprecated in favor of BrowserView)

#### Communication Pattern
```javascript
// Renderer → Main Process
ipcRenderer.send('channel-name', data);

// Main Process → Renderer
ipcMain.on('channel-name', (event, data) => {
  event.reply('reply-channel', response);
});

// Webview Communication
webview.send('channel', data);  // Window → Webview
webview.addEventListener('ipc-message', handler);  // Webview → Window
```

#### Important Warning
**Electron's webview tag is deprecated**: "Based on Chromium's webview, which is undergoing dramatic architectural changes. Electron recommends to not use the webview tag and to consider alternatives, like iframe, Electron's BrowserView, or an architecture that avoids embedded content altogether."

**Key Quote**: "ipcMain and ipcRenderer are the two main modules responsible for communicating in Electron. They are inherited from the NodeJS.EventEmitter module, which is based primarily on two methods: addListener(channel) and emit(channel)."

**Recommendation**: QWebChannel (Qt's approach) is more appropriate than mimicking Electron's IPC. QWebChannel provides type-safe, object-oriented communication vs. Electron's string-based channels.

---

### 2.2 WebView Architecture Components

**Source**: [Chromium WebView Architecture](https://chromium.googlesource.com/chromium/src/+/HEAD/android_webview/docs/architecture.md)

Understanding Chromium's architecture helps inform design decisions:

#### Separation of Concerns
1. **Browser Code**: Runs in host application process with same permissions
2. **Renderer Process**: Sandboxed with fewer permissions
3. **Web Content**: HTML/CSS/JavaScript served locally or remotely

#### Testing Considerations
- **Hybrid apps** (native + webview) have testing complexity
- Requires multiple tool types: native testing tools + web testing tools
- Dynamic webview content introduces testing challenges
- Modern tools (with AI) can validate dynamic content across approaches

**Key Quote**: "Testing mobile applications becomes complex when constructed with a mix of native, cross-platform, or webview components, leading to fragmentation with the tools, languages, and frameworks needed for high coverage."

**Recommendation**: Adopt clear separation: Native Qt tests (pytest-qt) for widget integration, separate HTML/JS tests (Playwright/Jest) for rendering logic.

---

### 2.3 Content Security Policy (CSP) Best Practices

**Source**: [OWASP Content Security Policy Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html)

Security considerations for webview-based widgets:

#### CSP Fundamentals
- Prevents/minimizes security threats by restricting what code can do
- Significantly reduces risk of XSS attacks
- Must specify which domains can execute scripts

#### Best Practices
1. **Default-src**: Set as restrictively as possible (ideally `'self'`)
2. **Avoid unsafe-inline and unsafe-eval**: Extract all inline scripts/styles
3. **Only allow needed hosts and protocols**: Whitelist approach
4. **Use nonces for inline content**: When absolutely necessary

#### Markdown Rendering Security
**Key Quote**: "Naive Markdown implementations can lead to security vulnerabilities like Cross-Site Scripting (XSS). When Markdown is converted to HTML, there's a risk of malicious code execution if the Markdown includes embedded HTML or JavaScript."

#### Recommended CSP for Markdown Widget
```html
<meta http-equiv="Content-Security-Policy"
      content="default-src 'self';
               script-src 'self' 'nonce-{random}';
               style-src 'self' 'unsafe-inline';
               img-src 'self' data: https:;
               font-src 'self' data:;">
```

**Recommendation**: Add CSP meta tag to viewer.html. Current implementation lacks explicit CSP, making it vulnerable to XSS if markdown contains malicious HTML.

---

## 3. Testing Strategies

### 3.1 Pytest-Qt for QWebEngineView

**Source**: [pytest-qt Documentation](https://pytest-qt.readthedocs.io/), [GitHub Issue #483](https://github.com/pytest-dev/pytest-qt/issues/483)

Testing Qt WebEngine widgets requires specific considerations:

#### QWebEngineView Testing Pattern
```python
import pytest
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

def test_webengine_basic(qtbot):
    """Test basic QWebEngineView functionality"""
    view = QWebEngineView()
    qtbot.addWidget(view)

    # Wait for page load
    with qtbot.waitSignal(view.loadFinished, timeout=10000):
        view.setHtml("<html><body><h1>Test</h1></body></html>")

    # Assert page loaded
    assert view.url().scheme() != ""
```

#### Key Fixture: qapp_args
**QWebEngineView requires QApplication arguments** to initialize properly:

```python
@pytest.fixture(scope="session")
def qapp_args():
    """Provide QApplication arguments for QtWebEngine."""
    return [sys.argv[0]]  # Program name required
```

**Key Quote**: "When testing QWebEngineView, you may need a fixture that provides QApplication arguments: `@pytest.fixture(scope='session') def qapp_args(): return [sys.argv[0]]`"

#### Best Practices
1. **Use qtbot.waitSignal**: Wait for `loadFinished` signal (asynchronous)
2. **Register widgets**: `qtbot.addWidget()` ensures proper cleanup
3. **Prefer widget methods over event simulation**: More reliable than simulating clicks
4. **Avoid GUI popups**: Set `QT_QPA_PLATFORM=offscreen` or use pytest-xvfb

**Recommendation**: Current markdown widget tests should follow this pattern. Add explicit `qapp_args` fixture and use `waitSignal` for async operations.

---

### 3.2 Playwright Integration Limitations

**Source**: [Playwright GitHub Issue #36961](https://github.com/microsoft/playwright/issues/36961)

Playwright cannot directly test QWebEngineView:

#### The Problem
- Playwright's `connect_over_cdp()` attempts to connect to QtWebEngine via Chrome DevTools Protocol
- **QtWebEngine's DevTools server doesn't implement all CDP methods**
- Specifically fails on `Browser.setDownloadBehavior` - not supported by Qt WebEngine

#### Connection Attempt
```python
# This FAILS with QWebEngineView
browser = await playwright.chromium.connect_over_cdp(
    "ws://127.0.0.1:9222/devtools/page/<id>"
)
# Error: Protocol error (Browser.setDownloadBehavior):
#        Browser context management is not supported
```

#### Workaround Options
1. **Extract HTML/JS to standalone files**: Test separately without Qt
2. **Use Jest for JavaScript unit tests**: Test rendering logic in Node.js
3. **Use Playwright on standalone HTML**: Test the HTML template independently
4. **Keep Qt integration tests separate**: Use pytest-qt for widget integration

**Key Quote**: "chromium.connect_over_cdp(wsUrl) immediately aborts with: Protocol error (Browser.setDownloadBehavior): Browser context management is not supported."

**Recommendation**: Adopt dual testing strategy:
- **HTML/JS Testing**: Extract rendering logic to testable modules (Jest or standalone Playwright)
- **Qt Integration Testing**: Use pytest-qt for widget functionality

---

### 3.3 Dual Testing Strategy

**Source**: [Pytest-Playwright Documentation](https://playwright.dev/python/docs/test-runners)

Combining Playwright and pytest for comprehensive coverage:

#### Tool Selection
- **Playwright**: End-to-end browser automation, NOT suitable for unit testing
- **Jest/Vitest/Mocha**: JavaScript unit testing frameworks
- **pytest**: Python testing framework, manages test execution and structure
- **pytest-qt**: Qt widget testing plugin for pytest

#### Recommended Structure
```
tests/
├── unit/                      # Python unit tests
│   ├── test_bridges.py       # Test QWebChannel bridge
│   └── test_theme_logic.py   # Test theme token resolution
├── integration/               # Qt integration tests
│   └── test_markdown_viewer.py  # Test full widget with pytest-qt
└── html/                      # HTML/JS testing
    ├── test_rendering.html    # Standalone HTML for Playwright
    ├── test_rendering.spec.py # Playwright tests
    └── viewer.test.js         # Jest unit tests (if extracted)
```

#### Example: Standalone HTML Testing
```python
# test_rendering.spec.py
import pytest
from playwright.sync_api import sync_playwright

def test_markdown_rendering():
    """Test markdown rendering in isolation."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Load standalone test HTML
        page.goto("file:///path/to/test_rendering.html")

        # Test rendering
        page.evaluate("window.MarkdownViewer.render('# Hello')")

        # Assert result
        assert page.query_selector("h1").inner_text() == "Hello"

        browser.close()
```

**Key Quote**: "For maximum effectiveness, use Playwright for browser automation and Pytest to manage the test execution, structure, and reporting."

**Recommendation**: Create `tests/html/` directory with standalone HTML files that can be tested with Playwright independently of Qt.

---

## 4. Python ↔ JavaScript Communication

### 4.1 QWebChannel Best Practices

**Source**: [Stack Overflow](https://stackoverflow.com/questions/75067758/), [Qt Forum](https://forum.qt.io/topic/143706/)

QWebChannel enables bidirectional communication between Python and JavaScript:

#### Critical: Keep Reference to Channel
**Most common mistake**: Not keeping a reference to the QWebChannel object leads to garbage collection.

```python
# ❌ WRONG - channel will be garbage collected
def setup_channel():
    channel = QWebChannel()
    self.page().setWebChannel(channel)

# ✅ CORRECT - store as instance attribute
def setup_channel(self):
    self.channel = QWebChannel()  # Keep reference!
    self.page().setWebChannel(self.channel)

# ✅ ALSO CORRECT - give it a parent
def setup_channel(self):
    channel = QWebChannel(self)  # Parent keeps it alive
    self.page().setWebChannel(channel)
```

**Key Quote**: "A critical issue is that you must keep a reference to the channel to prevent garbage collection. The web page doesn't take ownership of the channel, so you should either give it a parent or store it as an attribute."

#### Use @Slot Decorators
```python
class JavaScriptBridge(QObject):
    message_received = Signal(dict)

    @Slot(str)
    def receiveMessage(self, message_json: str) -> None:
        """Methods should use @Slot with type hints."""
        message = json.loads(message_json)
        self.message_received.emit(message)

    @Slot(str, result=str)
    def processData(self, data: str) -> str:
        """Use result= for return values."""
        return data.upper()
```

#### JavaScript Side
```javascript
// Load QWebChannel library
new QWebChannel(qt.webChannelTransport, function(channel) {
    // Access Python object
    var bridge = channel.objects.qtBridge;

    // Call Python method
    bridge.processData("hello", function(result) {
        console.log(result);  // "HELLO"
    });
});
```

#### Communication Methods
- **Python → JavaScript**: `page.runJavaScript("jsFunction(data);")`
- **JavaScript → Python**: Call methods on registered objects via QWebChannel

**Recommendation**: Current markdown widget implementation is correct - it keeps channel reference and uses @Slot decorators properly.

---

### 4.2 Message Protocol Design

Based on current markdown widget implementation and best practices:

#### Message Structure
```python
# Python → JavaScript
{
    "type": "command",
    "action": "render",
    "data": "# Markdown content"
}

# JavaScript → Python
{
    "type": "ready",
    "status": "initialized"
}

{
    "type": "toc_changed",
    "data": [
        {"level": 1, "text": "Heading", "id": "heading"}
    ]
}
```

#### Recommended Pattern
1. **Type field**: Identifies message category (command, event, query)
2. **Action field**: Specific action within type
3. **Data field**: Payload (can be any JSON-serializable data)
4. **Error handling**: Include error field for failures

**Recommendation**: Formalize message protocol with TypeScript definitions and Python dataclasses for type safety.

---

## 5. Recommendations for Markdown Widget Refactoring

### 5.1 Immediate Improvements (Phase 1)

#### 1. Add Content Security Policy
```html
<!-- viewer.html -->
<meta http-equiv="Content-Security-Policy"
      content="default-src 'self';
               script-src 'self' 'unsafe-inline';
               style-src 'self' 'unsafe-inline';
               img-src 'self' data: https: file:;
               font-src 'self' data:;">
```

#### 2. Extract Theme Bridge
```python
# bridges/theme_bridge.py
class ThemeBridge:
    """Manages theme communication between Python and JavaScript."""

    def __init__(self, page: QWebEnginePage):
        self.page = page

    def apply_theme(self, theme: Theme) -> None:
        """Apply theme to web content."""
        css_vars = self._build_css_variables(theme)
        self._inject_css(css_vars)

    def _build_css_variables(self, theme: Theme) -> dict:
        """Build CSS variables from theme tokens with fallbacks."""
        # Extract theme_config and _get_color_with_fallback logic
        pass
```

#### 3. Add Standalone HTML Test File
```html
<!-- tests/html/test_rendering.html -->
<!DOCTYPE html>
<html>
<head>
    <!-- Same resources as viewer.html but standalone -->
</head>
<body>
    <div id="test-container"></div>
    <script>
        // Test harness for Playwright
        window.testAPI = {
            render: (markdown) => window.MarkdownViewer.render(markdown),
            getRenderedHTML: () => document.getElementById('content').innerHTML,
            setTheme: (theme) => window.MarkdownViewer.setTheme(theme)
        };
    </script>
</body>
</html>
```

---

### 5.2 Architecture Refactoring (Phase 2)

#### Proposed Layer Structure
```
┌─────────────────────────────────────┐
│  MarkdownViewer (Qt Widget)         │
│  - Widget lifecycle                  │
│  - ThemedWidget integration          │
│  - User interaction                  │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│  WebViewHost (Abstraction)          │
│  - QWebEngineView wrapper            │
│  - Bridge management                 │
│  - Resource loading                  │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│  ThemeBridge (Communication)        │
│  - CSS variable injection            │
│  - Theme token resolution            │
└─────────────────────────────────────┘
                │
┌───────────────▼─────────────────────┐
│  RendererProtocol (Interface)       │
│  ├─ MarkdownItRenderer              │
│  └─ PythonMarkdownRenderer          │
└─────────────────────────────────────┘
```

#### Directory Structure
```
markdown_widget/
├── src/vfwidgets_markdown/
│   ├── widgets/
│   │   └── markdown_viewer.py       # Reduced to ~400 lines
│   ├── hosting/
│   │   ├── webview_host.py          # Reusable QWebEngineView wrapper
│   │   └── resource_loader.py       # Resource management
│   ├── bridges/
│   │   ├── theme_bridge.py          # Theme communication
│   │   └── message_bridge.py        # General messaging
│   ├── renderers/
│   │   ├── base.py                  # RendererProtocol (ABC)
│   │   └── markdown_it/
│   │       ├── renderer.py          # Python coordinator
│   │       ├── html/viewer.html
│   │       ├── js/viewer.js
│   │       └── css/viewer.css
│   └── tests/
│       ├── unit/                    # Python unit tests
│       ├── integration/             # pytest-qt tests
│       └── html/                    # Playwright tests
```

---

### 5.3 Testing Strategy

#### Unit Tests (pytest)
```python
# tests/unit/test_theme_bridge.py
def test_css_variable_generation():
    """Test CSS variable generation from theme tokens."""
    theme = create_mock_theme()
    bridge = ThemeBridge(mock_page)
    css_vars = bridge._build_css_variables(theme)

    assert "--md-bg" in css_vars
    assert "--md-fg" in css_vars
```

#### Integration Tests (pytest-qt)
```python
# tests/integration/test_markdown_viewer.py
def test_theme_application(qtbot, qapp_args):
    """Test theme application to viewer."""
    viewer = MarkdownViewer()
    qtbot.addWidget(viewer)

    with qtbot.waitSignal(viewer.viewer_ready, timeout=5000):
        pass  # Wait for initialization

    # Apply theme and verify CSS injection
    viewer.on_theme_changed(create_test_theme())

    # TODO: How to verify CSS was applied?
    # Need to extract rendered HTML and check styles
```

#### HTML/JS Tests (Playwright)
```python
# tests/html/test_rendering.py
def test_markdown_rendering(page):
    """Test markdown rendering in isolation."""
    page.goto("file:///path/to/test_rendering.html")

    # Test rendering
    page.evaluate("window.testAPI.render('# Hello')")

    # Verify result
    assert page.query_selector("h1").inner_text() == "Hello"

def test_theme_css_variables(page):
    """Test CSS variable application."""
    page.goto("file:///path/to/test_rendering.html")

    # Inject CSS variables (simulating Python injection)
    page.evaluate("""
        const style = document.createElement('style');
        style.id = 'theme-vars';
        style.textContent = ':root { --md-bg: #ff0000; }';
        document.head.appendChild(style);
    """)

    # Verify CSS variable is applied
    bg_color = page.evaluate("""
        getComputedStyle(document.documentElement)
            .getPropertyValue('--md-bg')
    """)
    assert bg_color.strip() == "#ff0000"
```

---

### 5.4 Specific Fixes for Current Issues

#### Issue: markdown.colors.code.background Not Applied

**Root Cause Analysis**:
1. CSS specificity conflict with Prism.js hardcoded backgrounds
2. Prism themes loaded after CSS variables injected
3. CSS variable may not exist (token resolution failure)

**Debugging Strategy** (using standalone HTML test):
```python
def test_code_background_theme(page):
    """Test that code background color is applied correctly."""
    page.goto("file:///path/to/test_rendering.html")

    # 1. Inject CSS variable
    page.evaluate("""
        document.documentElement.style.setProperty('--md-code-bg', '#123456');
    """)

    # 2. Render markdown with code block
    page.evaluate("""
        window.testAPI.render('```python\\nprint("test")\\n```');
    """)

    # 3. Wait for Prism highlighting
    page.wait_for_timeout(500)

    # 4. Check computed background color
    code_bg = page.evaluate("""
        const pre = document.querySelector('pre[class*="language-"]');
        return getComputedStyle(pre).backgroundColor;
    """)

    # 5. Verify it matches CSS variable (converted to rgb)
    assert code_bg == "rgb(18, 52, 86)"  # #123456 in RGB
```

**Recommended Fix**:
1. **Increase CSS specificity**: Use `body #content pre[class*="language-"]` (already done)
2. **Add !important**: Use `!important` on background (already done)
3. **Inject after Prism loads**: Delay CSS variable injection
4. **Verify token exists**: Add logging for token resolution

```python
# In on_theme_changed()
color = self._get_color_with_fallback(token_path, current_theme)
if color:
    logger.info(f"✓ Token {token_path} resolved to {color}")
else:
    logger.error(f"✗ Token {token_path} NOT FOUND - check theme definition")
```

---

## 6. Patterns for Future WebView Widgets

### 6.1 Reusable Components

Based on this research, these components should be extracted to `vfwidgets_common`:

#### 1. WebViewHost
```python
# vfwidgets_common/hosting/webview_host.py
class WebViewHost:
    """Reusable QWebEngineView host for any webview widget."""

    def __init__(self, parent=None):
        self.view = QWebEngineView(parent)
        self._setup_page()
        self._setup_security()

    def load_template(self, html_path: Path, base_url: QUrl) -> None:
        """Load HTML template with base URL for resources."""
        pass

    def inject_css(self, css: str, style_id: str = "injected") -> None:
        """Inject CSS into page."""
        pass

    def inject_script(self, js: str) -> None:
        """Inject JavaScript into page."""
        pass
```

#### 2. ThemeBridge
```python
# vfwidgets_common/bridges/theme_bridge.py
class ThemeBridge:
    """Standard theme communication for webview widgets."""

    def __init__(self, page: QWebEnginePage, theme_config: dict):
        self.page = page
        self.theme_config = theme_config

    def apply_theme(self, theme: Theme) -> None:
        """Apply theme using CSS custom properties."""
        css_vars = self.build_css_variables(theme)
        self.inject_css_variables(css_vars)
```

#### 3. MessageBridge
```python
# vfwidgets_common/bridges/message_bridge.py
class MessageBridge(QObject):
    """Standard message protocol for Python ↔ JavaScript."""

    message_received = Signal(dict)

    def __init__(self, page: QWebEnginePage):
        super().__init__()
        self.page = page
        self._setup_channel()

    def send_message(self, message_type: str, **kwargs) -> None:
        """Send typed message to JavaScript."""
        pass
```

---

### 6.2 Standard Testing Infrastructure

#### Fixture Library
```python
# tests/conftest.py (shared across widgets)
@pytest.fixture(scope="session")
def qapp_args():
    """QApplication arguments for QtWebEngine."""
    return [sys.argv[0]]

@pytest.fixture
def webview_host(qtbot):
    """Create WebViewHost for testing."""
    host = WebViewHost()
    qtbot.addWidget(host.view)
    yield host
    # Cleanup handled by qtbot

@pytest.fixture
def mock_theme():
    """Create mock theme for testing."""
    return create_mock_theme()
```

#### Playwright Test Template
```python
# tests/html/conftest.py (shared Playwright setup)
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser():
    """Launch browser for all tests."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        yield browser
        browser.close()

@pytest.fixture
def page(browser):
    """Create new page for each test."""
    page = browser.new_page()
    yield page
    page.close()
```

---

## 7. Security Considerations

### 7.1 Content Security Policy

**Recommended CSP for Markdown Widget**:
```html
<meta http-equiv="Content-Security-Policy"
      content="default-src 'self';
               script-src 'self' 'unsafe-inline';
               style-src 'self' 'unsafe-inline';
               img-src 'self' data: https: file:;
               font-src 'self' data:;
               connect-src 'none';">
```

Explanation:
- `default-src 'self'`: Only load resources from same origin
- `script-src 'self' 'unsafe-inline'`: Allow bundled scripts and inline (needed for injected theme JS)
- `style-src 'self' 'unsafe-inline'`: Allow bundled styles and inline (needed for CSS variables)
- `img-src 'self' data: https: file:`: Allow local images, data URLs, HTTPS, and file URLs
- `font-src 'self' data:`: Allow bundled fonts and data URLs
- `connect-src 'none'`: No XHR/fetch requests needed

### 7.2 Markdown Sanitization

**Current Risk**: markdown-it may allow raw HTML injection

**Recommendations**:
1. **Disable HTML in markdown**: Configure markdown-it with `html: false`
2. **Use DOMPurify**: Sanitize rendered HTML before display
3. **Validate image URLs**: Check URLs before loading images

```javascript
// In viewer.js
const md = markdownit({
    html: false,  // Disable raw HTML
    xhtmlOut: true,
    breaks: true,
    linkify: true,
});

// After rendering, sanitize
const rendered = md.render(content);
const clean = DOMPurify.sanitize(rendered);
```

---

## 8. Key Takeaways

### What Works Well
1. ✅ **CSS Custom Properties for Theming**: VS Code pattern is industry standard
2. ✅ **QWebChannel for Communication**: Type-safe, object-oriented approach
3. ✅ **Separate HTML/JS Testing**: Playwright for rendering, pytest-qt for integration
4. ✅ **QWebEngineScript for Persistent Styles**: Official Qt pattern for CSS injection

### What to Avoid
1. ❌ **Electron's IPC Pattern**: String-based channels less suitable than QWebChannel
2. ❌ **Playwright Direct CDP Connection**: Cannot test QWebEngineView directly
3. ❌ **Inline Scripts/Styles**: Violates CSP best practices
4. ❌ **Monolithic Widget Classes**: Separate concerns (hosting, theming, rendering)

### Prioritized Actions
1. **Phase 1 (Immediate)**:
   - Add Content Security Policy to viewer.html
   - Extract ThemeBridge class
   - Create standalone HTML test file
   - Add explicit token resolution logging

2. **Phase 2 (Short-term)**:
   - Refactor markdown_viewer.py using layer architecture
   - Implement RendererProtocol abstraction
   - Add Playwright test suite for HTML/JS
   - Enhance pytest-qt integration tests

3. **Phase 3 (Long-term)**:
   - Extract reusable components to vfwidgets_common
   - Create standard testing infrastructure
   - Document patterns for future webview widgets
   - Consider Python-based renderer option

---

## 9. References

### Documentation
- [VS Code Webview API](https://code.visualstudio.com/api/extension-guides/webview)
- [Qt WebEngine Overview](https://doc.qt.io/qt-6/qtwebengine-overview.html)
- [QWebEngineScript Example](https://doc.qt.io/qt-5/qtwebengine-webenginewidgets-stylesheetbrowser-example.html)
- [Electron IPC Tutorial](https://www.electronjs.org/docs/latest/tutorial/ipc)
- [pytest-qt Documentation](https://pytest-qt.readthedocs.io/)
- [Playwright Python Documentation](https://playwright.dev/python/docs/test-runners)

### Security
- [OWASP CSP Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html)
- [Content Security Policy Guide](https://web.dev/articles/csp)
- [Secure Markdown Rendering](https://www.pullrequest.com/blog/secure-markdown-rendering-in-react-balancing-flexibility-and-safety/)

### Community Resources
- [Jupyter QtConsole](https://github.com/jupyter/qtconsole)
- [Electron WebView IPC Demo](https://github.com/kw77/electron-webview-ipc-demo)
- [pytest-qt Issue #483](https://github.com/pytest-dev/pytest-qt/issues/483) - QWebEngine testing

---

**Next Steps**: See `ARCHITECTURE-REFACTORING-PLAN.md` for detailed implementation plan based on these research findings.
