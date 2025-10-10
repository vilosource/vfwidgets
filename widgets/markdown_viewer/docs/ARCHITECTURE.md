# Markdown Viewer Widget - Architecture

## Overview

The MarkdownViewer widget is a PySide6-based markdown rendering widget that uses QWebEngineView to display markdown content rendered by JavaScript libraries. The architecture follows a layered approach with clear separation between Python (Qt) and JavaScript (rendering) layers.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│  (User's Qt Application - Editor, TOC Sidebar, etc.)       │
└────────────────────┬────────────────────────────────────────┘
                     │ Uses Public API
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                  MarkdownViewer Widget                       │
│                    (Python/PySide6)                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  QWebEngineView (Base Class)                          │  │
│  │  - Resource loading                                    │  │
│  │  - Qt ↔ JavaScript bridge (QWebChannel)               │  │
│  │  - Signal handling                                     │  │
│  │  - Theme integration (optional ThemedWidget)           │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │ QWebChannel Bridge
                     ↓
┌─────────────────────────────────────────────────────────────┐
│             JavaScript Rendering Layer                       │
│                  (viewer.html + viewer.js)                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  markdown-it (Core Parser)                            │  │
│  │  ├─ markdown-it-anchor (heading IDs)                  │  │
│  │  ├─ markdown-it-emoji (emoji support)                 │  │
│  │  ├─ markdown-it-footnote (footnotes)                  │  │
│  │  ├─ markdown-it-katex (math rendering)                │  │
│  │  └─ ... (10+ plugins)                                 │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │  Mermaid.js (Diagram Rendering)                       │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │  Prism.js (Syntax Highlighting)                       │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │  KaTeX (Math Rendering)                               │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Python Layer (Qt/PySide6)

#### MarkdownViewer Class

**Responsibilities:**
- Manage QWebEngineView lifecycle
- Load and inject HTML template
- Handle Qt ↔ JavaScript communication
- Emit signals for application integration
- Provide public API for content and navigation

**Key Components:**

```python
class MarkdownViewer(QWebEngineView):
    \"\"\"
    Main widget class.

    Hierarchy:
    - Optionally extends ThemedWidget (if vfwidgets-theme available)
    - Always extends QWebEngineView
    \"\"\"

    # Resource Management
    def _load_resources(self) -> None:
        \"\"\"Load HTML template and setup page.\"\"\"

    def _setup_webengine_page(self) -> None:
        \"\"\"Configure QWebEnginePage settings.\"\"\"

    # Qt ↔ JavaScript Bridge
    def _setup_bridge(self) -> None:
        \"\"\"Setup QWebChannel for bidirectional communication.\"\"\"

    # Content Management
    def set_markdown(self, content: str) -> None:
        \"\"\"Send markdown to JavaScript layer for rendering.\"\"\"

    # Signal Handling
    def _on_javascript_message(self, msg: dict) -> None:
        \"\"\"Handle messages from JavaScript layer.\"\"\"
```

#### Resource Loading Strategy

```python
# Resources bundled in package
resources/
├── viewer.html       # Template loaded once
├── js/*.js          # Loaded via <script> tags in HTML
└── css/*.css        # Loaded via <link> tags in HTML

# Loading process:
1. Read viewer.html from package resources
2. Replace placeholders if needed (theme, config)
3. Load into QWebEngineView
4. JavaScript libraries load automatically
5. Setup QWebChannel bridge
6. Ready to receive markdown content
```

### 2. JavaScript Layer (WebView)

#### viewer.js - Main Controller

**Responsibilities:**
- Initialize all rendering libraries
- Parse and render markdown
- Extract metadata (TOC, headings)
- Handle theme switching
- Communicate with Python layer

**Architecture:**

```javascript
// Singleton pattern
const MarkdownRenderer = {
    // Initialization
    md: null,              // markdown-it instance
    prismLoaded: false,
    mermaidReady: false,
    katexReady: false,

    // Setup
    init() {
        this.initMarkdownIt();
        this.initMermaid();
        this.initPrism();
        this.initKatex();
        this.setupBridge();
    },

    // Rendering
    render(markdown) {
        const html = this.md.render(markdown);
        document.getElementById('content').innerHTML = html;
        this.postProcess();  // Mermaid, Prism highlighting
        this.extractTOC();
        this.notifyPython({ type: 'content_loaded' });
    },

    // TOC extraction
    extractTOC() {
        const headings = document.querySelectorAll('h1,h2,h3,h4,h5,h6');
        const toc = Array.from(headings).map(h => ({
            level: parseInt(h.tagName[1]),
            text: h.textContent,
            id: h.id,
            line: h.dataset.line
        }));
        this.notifyPython({ type: 'toc_changed', data: toc });
    },

    // Theme handling
    setTheme(theme) {
        document.body.dataset.theme = theme;
        this.setSyntaxTheme(theme === 'dark' ? 'vscode-dark' : 'vscode-light');
    },

    // Python communication
    notifyPython(message) {
        if (window.qtBridge) {
            window.qtBridge.messageReceived(JSON.stringify(message));
        }
    }
};
```

#### markdown-it Configuration

```javascript
// Core markdown-it setup
const md = markdownit({
    html: true,           // Allow HTML tags
    linkify: true,        // Auto-convert URLs to links
    typographer: true,    // Smart quotes, dashes, ellipses
    breaks: false,        // No line breaks = <br>
    highlight: function(code, lang) {
        // Delegate to Prism.js
        return Prism.highlight(code, Prism.languages[lang] || Prism.languages.markup, lang);
    }
});

// Load plugins
md.use(markdownitAnchor, { /* options */ });
md.use(markdownitEmoji);
md.use(markdownitFootnote);
md.use(markdownitKatex);
md.use(markdownitCheckbox);
// ... 10+ more plugins
```

#### Mermaid Integration

```javascript
// Initialize Mermaid
mermaid.initialize({
    startOnLoad: false,  // Manual trigger
    theme: 'dark',       // Default theme
    securityLevel: 'loose'
});

// Post-process code blocks
function processMermaid() {
    document.querySelectorAll('code.language-mermaid').forEach((block, index) => {
        const code = block.textContent;
        const id = `mermaid-${index}`;
        mermaid.render(id, code).then(result => {
            const div = document.createElement('div');
            div.innerHTML = result.svg;
            block.parentElement.replaceWith(div);
        });
    });
}
```

### 3. Qt ↔ JavaScript Bridge

**QWebChannel Communication:**

```python
# Python setup
self.channel = QWebChannel()
self.bridge = JavaScriptBridge(self)
self.channel.registerObject("qtBridge", self.bridge)
page.setWebChannel(self.channel)

class JavaScriptBridge(QObject):
    \"\"\"Bridge object exposed to JavaScript.\"\"\"

    message_received = Signal(str)

    @Slot(str)
    def messageReceived(self, msg: str):
        \"\"\"Receive messages from JavaScript.\"\"\"
        data = json.loads(msg)
        if data['type'] == 'toc_changed':
            self.parent().toc_changed.emit(data['data'])
        elif data['type'] == 'heading_clicked':
            self.parent().heading_clicked.emit(data['id'])
        # ... handle other message types
```

```javascript
// JavaScript setup
new QWebChannel(qt.webChannelTransport, function(channel) {
    window.qtBridge = channel.objects.qtBridge;

    // Listen for Python commands
    // (sent via runJavaScript)

    // Send messages to Python
    window.qtBridge.messageReceived(JSON.stringify({
        type: 'content_loaded'
    }));
});
```

**Message Protocol:**

```javascript
// Python → JavaScript
page.runJavaScript("MarkdownRenderer.render(content)")
page.runJavaScript("MarkdownRenderer.setTheme('dark')")
page.runJavaScript("MarkdownRenderer.scrollToHeading('intro')")

// JavaScript → Python
{
    type: 'content_loaded' | 'toc_changed' | 'heading_clicked' | 'link_clicked',
    data: any  // Type-specific payload
}
```

## Data Flow

### Rendering Flow

```
1. Application calls viewer.set_markdown(content)
   ↓
2. Python escapes content for JavaScript
   ↓
3. Python calls page.runJavaScript("MarkdownRenderer.render(escapedContent)")
   ↓
4. JavaScript markdown-it parses markdown → HTML
   ↓
5. JavaScript inserts HTML into DOM
   ↓
6. JavaScript post-processes:
   - Mermaid renders diagrams
   - Prism highlights code
   - KaTeX renders math
   ↓
7. JavaScript extracts TOC from headings
   ↓
8. JavaScript sends message to Python: { type: 'content_loaded' }
   ↓
9. Python emits content_loaded signal
   ↓
10. JavaScript sends message to Python: { type: 'toc_changed', data: [...] }
    ↓
11. Python emits toc_changed signal with TOC data
    ↓
12. Application receives signals and updates UI
```

### Theme Switching Flow

```
1. Application calls viewer.set_theme('dark')
   ↓
2. Python stores theme preference
   ↓
3. Python calls page.runJavaScript("MarkdownRenderer.setTheme('dark')")
   ↓
4. JavaScript updates document.body.dataset.theme = 'dark'
   ↓
5. CSS responds to [data-theme="dark"] selector
   ↓
6. JavaScript calls setSyntaxTheme('vscode-dark')
   ↓
7. Prism CSS updates to dark theme
   ↓
8. Mermaid theme updates to 'dark'
   ↓
9. KaTeX inherits dark colors from CSS
```

### Image Resolution Flow

```
1. Markdown contains: ![Alt](./image.png)
   ↓
2. markdown-it generates: <img src="./image.png" alt="Alt">
   ↓
3. Browser requests: ./image.png
   ↓
4. QWebEngineUrlSchemeHandler intercepts request
   ↓
5. Python image resolver callback:
   - If base64: return data URL
   - If relative: resolve against base_path
   - If custom resolver: call user callback
   - If HTTP/HTTPS: allow through
   ↓
6. Image loaded and displayed
```

## Theme Integration Architecture

### Optional ThemedWidget Integration

```python
# Check if vfwidgets-theme is available
THEME_AVAILABLE = False
try:
    from vfwidgets_theme import ThemedWidget
    THEME_AVAILABLE = True
except ImportError:
    ThemedWidget = object  # Fallback

# Conditional inheritance
if THEME_AVAILABLE:
    _BaseClass = type("_Base", (ThemedWidget, QWebEngineView), {})
else:
    _BaseClass = QWebEngineView

class MarkdownViewer(_BaseClass):
    \"\"\"Widget with optional theme support.\"\"\"

    # Only used if ThemedWidget available
    theme_config = {
        "background": "editor.background",
        "foreground": "editor.foreground",
        "link": "textLink.foreground",
        "code_bg": "editor.selectionBackground",
    }

    def on_theme_changed(self):
        \"\"\"Called when theme changes (ThemedWidget callback).\"\"\"
        if THEME_AVAILABLE:
            theme = self.get_current_theme()
            is_dark = theme.get_token("editor.background").is_dark()
            self.set_theme("dark" if is_dark else "light")
```

### CSS Theme Variables

```css
/* viewer.css */
:root[data-theme="dark"] {
    --md-bg: #1e1e1e;
    --md-fg: #d4d4d4;
    --md-link: #3794ff;
    --md-code-bg: #2d2d2d;
    --md-border: #404040;
}

:root[data-theme="light"] {
    --md-bg: #ffffff;
    --md-fg: #333333;
    --md-link: #0066cc;
    --md-code-bg: #f5f5f5;
    --md-border: #dddddd;
}

/* Injected from Python when ThemedWidget active */
:root[data-theme="custom"] {
    --md-bg: {{ theme.editor.background }};
    --md-fg: {{ theme.editor.foreground }};
    /* ... */
}
```

## Performance Considerations

### Rendering Optimization

1. **Debouncing**: Live preview updates debounced (default 300ms)
2. **Incremental Rendering**: Future - only re-render changed sections
3. **Lazy Loading**: Mermaid/KaTeX only loaded when needed
4. **Caching**: Rendered HTML cached for repeat renders

### Memory Management

- JavaScript libraries loaded once, reused
- DOM cleared before each render
- No memory leaks in Qt ↔ JavaScript bridge
- Images handled by QWebEngine's cache

### Large Document Handling

- No size limits enforced
- QWebEngine handles large DOM trees
- Scroll performance handled by Chromium
- If too large (>10MB), let it crash (documented limitation)

## Security Considerations

### Content Sanitization

- markdown-it configured with `html: true` (allow HTML in markdown)
- XSS risk: User content is trusted (desktop app, not web app)
- No external content loading by default

### Resource Loading

- All JavaScript/CSS bundled locally
- No CDN requests
- Images: configurable resolver for security policies

### JavaScript Isolation

- QWebEngineView sandboxed
- JavaScript cannot access Python directly (only via QWebChannel)
- Limited API surface exposed to JavaScript

## Extension Points

### For Application Developers

1. **Custom TOC UI**: Use `get_toc()` data
2. **Custom Navigation**: Use scroll methods + signals
3. **Custom Image Resolution**: Use `set_image_resolver()`
4. **Custom Theme**: Use `inject_css()`
5. **Editor Coupling**: Use sync mode + signals

### For Future Development

1. **Custom markdown-it Plugins**: `register_plugin()` API
2. **Custom Mermaid Themes**: Additional theme files
3. **Custom Prism Languages**: Additional language grammars
4. **Custom Preprocessors**: Hook before markdown-it
5. **Custom Postprocessors**: Hook after rendering

## Testing Architecture

### Unit Tests (Python)

- Test resource loading
- Test QWebChannel setup
- Test signal emission
- Test public API methods
- Mock JavaScript layer

### Integration Tests (Python + JavaScript)

- Test actual markdown rendering
- Test theme switching
- Test image loading
- Test export functionality
- Full QWebEngineView testing with pytest-qt

### JavaScript Tests (Future)

- Test markdown-it configuration
- Test plugin integration
- Test TOC extraction
- Test theme switching logic
- Test Mermaid/Prism/KaTeX integration

## Directory Structure

```
src/vfwidgets_markdown/
├── __init__.py              # Public API exports
├── viewer.py                # MarkdownViewer class
├── constants.py             # Configuration constants
├── utils.py                 # Utility functions
├── py.typed                 # Type hint marker
└── resources/
    ├── viewer.html          # HTML template
    ├── js/
    │   ├── markdown-it.min.js              (~50KB)
    │   ├── markdown-it-plugins.min.js      (~20KB)
    │   ├── mermaid.min.js                  (~200KB)
    │   ├── prism.min.js                    (~15KB)
    │   ├── katex.min.js                    (~100KB)
    │   └── viewer.js                       (custom)
    └── css/
        ├── viewer.css                      (base styles)
        ├── github-markdown.css             (GitHub styling)
        ├── katex.min.css
        └── prism-themes/
            ├── prism-vscode-dark.css
            ├── prism-vscode-light.css
            └── prism-github.css

tests/
├── test_viewer.py           # MarkdownViewer tests
├── test_rendering.py        # Rendering tests
├── test_theme.py            # Theme integration tests
└── test_integration.py      # Integration tests

examples/
├── 01_basic_viewer.py
├── 02_live_preview.py
├── 03_toc_sidebar.py
├── 04_themed_viewer.py
├── 05_image_support.py
└── 06_export.py

docs/
├── ARCHITECTURE.md          # This file
├── API.md                   # API reference
└── QUICKSTART.md            # Quick start guide
```

## Future Architecture Considerations

### Potential Enhancements

1. **Virtual Scrolling**: For very large documents
2. **Web Workers**: Offload rendering to worker thread
3. **Incremental Updates**: Only re-render changed portions
4. **Plugin System**: Runtime plugin loading
5. **Multiple Renderers**: Support other markdown engines

### Backward Compatibility

- Public API remains stable
- Internal implementation can change
- JavaScript layer can be swapped
- Theme integration optional forever

## Summary

The MarkdownViewer architecture provides:

✅ Clean separation of concerns (Python ↔ JavaScript)
✅ Extensible design (plugins, themes, custom resolution)
✅ Performance optimized (debouncing, lazy loading)
✅ Security conscious (sandboxing, local resources)
✅ Well-tested (unit + integration tests)
✅ Developer-friendly (signals, data APIs, examples)

The architecture supports the widget's core goal: **Display markdown beautifully while providing hooks for rich applications.**
